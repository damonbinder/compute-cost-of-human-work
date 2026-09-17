#!/usr/bin/env python3
"""Reconstruct exam workload estimates from retained original sources.

Python 3; dependencies: tiktoken, tokenizers, numpy, pyarrow; Poppler pdftotext on PATH.
Usage: python3 -B recompute_exams.py --sources /path/to/sources --output /new/audit.json
Optional --models /path/to/models.csv adds the corresponding FLOP products.
Never invokes an API, downloads data, or changes the evidence directory.
"""
import argparse
import ast
import base64
import csv
import io
import json
import math
import pickle
import re
import statistics
import subprocess
import tarfile
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq
import tiktoken
from tokenizers import Tokenizer


def avg(values):
    return statistics.mean(values)


class HumanDataUnpickler(pickle.Unpickler):
    """Only the two numerical constructors present in Google's source pickle."""
    def find_class(self, module, name):
        if (module, name) == ("numpy.core.multiarray", "scalar"):
            return np._core.multiarray.scalar
        if (module, name) == ("numpy", "dtype"):
            return np.dtype
        raise ValueError(f"Unexpected object in human baseline: {module}.{name}")


def norm(text):
    return re.sub(r"\s+", " ", text).strip()


def pdf(source, *options):
    return subprocess.check_output(["pdftotext", *map(str, options), str(source), "-"], text=True)


def clean_gre(text):
    lines = []
    for line in text.replace("\f", "\n").splitlines():
        line = line.strip()
        if not line or re.fullmatch(r"-\d+-", line):
            continue
        if any(s in line for s in ["Unauthorized copying", "any part of this page", "GO ON TO THE NEXT PAGE", "NO TEST MATERIAL"]):
            continue
        lines.append(line)
    return "\n".join(lines)


def gre_questions(source):
    text = clean_gre(pdf(source, "-layout"))
    questions = []
    for section, count in [(2, 15), (3, 20)]:
        start = re.search(rf"Section {section}\nVerbal Reasoning\n\d+ questions", text).end()
        part = text[start:text.index(f"This is the end of Section {section}", start)]
        boundaries = list(re.finditer(r"(?m)^(\d+)\.\s", part))
        assert [int(m[1]) for m in boundaries] == list(range(1, count + 1))
        passages = []
        for m in re.finditer(r"Questions (\d+) (?:to|and) (\d+) are based on the following", part):
            q = next(q for q in boundaries if int(q[1]) == int(m[1]))
            passages.append((int(m[1]), int(m[2]), m.start(), norm(part[m.start():q.start()])))
        for index, match in enumerate(boundaries):
            end = boundaries[index + 1].start() if index + 1 < len(boundaries) else len(part)
            for _, _, pos, _ in passages:
                if match.start() < pos < end:
                    end = pos
            directions = re.search(r"Directions for questions", part[match.end():end])
            if directions:
                end = match.end() + directions.start()
            body = norm(part[match.end():end])
            context = " ".join(p[3] for p in passages if p[0] <= int(match[1]) <= p[1])
            questions.append({"section": section, "question": int(match[1]), "text": (context + " " + body).strip()})
    return questions


def mbe_questions(source):
    chunks = []
    for page in range(1, 6):
        for x in [0, 306]:
            chunk = pdf(source, "-layout", "-f", page, "-l", page, "-x", x, "-y", 140 if page == 1 else 20, "-W", 306, "-H", 640 if page == 1 else 750)
            chunks.append(chunk)
    text = "\n".join(chunks)
    text = re.sub(r"Copyright ©.*?reserved\.", "", text)
    text = re.sub(r"MBE Sample Test Questions\s*\|\s*\d+", "", text)
    matches = list(re.finditer(r"(?m)^\s*(\d+)\.\s+", text))
    assert [int(m[1]) for m in matches] == list(range(1, 22)), [m[1] for m in matches]
    return [norm(text[m.end():matches[i + 1].start() if i + 1 < len(matches) else len(text)]) for i, m in enumerate(matches)]


def usmle_questions(source):
    text = pdf(source)
    start = text.index("USMLE STEP 1 SAMPLE TEST QUESTIONS\nBLOCK 1")
    text = text[start:]
    text = text[:text.index("ANSWER FORM")]
    text = re.sub(r"(?m)^BLOCK \d+, ITEMS [^\n]*", "", text)
    text = re.sub(r"(?m)^\d+\s*$", "", text)
    text = text.replace("\f", "\n")
    matches = list(re.finditer(r"(?m)^\s*(\d+)\.\s+", text))
    assert [int(m[1]) for m in matches] == list(range(1, 120)), [m[1] for m in matches]
    return [norm(text[m.end():matches[i + 1].start() if i + 1 < len(matches) else len(text)]) for i, m in enumerate(matches)]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sources", required=True, type=Path)
    ap.add_argument("--models", type=Path)
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()
    src, out = args.sources.resolve(), args.output.resolve()
    if out.exists() or out == src or src in out.parents:
        ap.error("Output must be a new file outside the source evidence directory")

    # Take only the tokenizer pattern literal from the retained official source.
    definitions = ast.parse((src / "openai_public.py").read_text())
    pats = {}
    for func in definitions.body:
        if isinstance(func, ast.FunctionDef) and func.name in ["cl100k_base", "r50k_base"]:
            for node in ast.walk(func):
                if isinstance(node, ast.Dict):
                    for key, value in zip(node.keys, node.values):
                        if isinstance(key, ast.Constant) and key.value == "pat_str":
                            if isinstance(value, ast.Constant):
                                pats[func.name] = value.value
    pats["r50k_base"] = r"'s|'t|'re|'ve|'m|'ll|'d| ?\p{L}++| ?\p{N}++| ?[^\s\p{L}\p{N}]++|\s++$|\s+(?!\S)|\s"
    enc = {}
    for name in ["cl100k_base", "r50k_base"]:
        ranks = {base64.b64decode(line.split()[0]): int(line.split()[1]) for line in (src / (name + ".tiktoken")).read_bytes().splitlines()}
        enc[name] = tiktoken.Encoding(name=name, pat_str=pats[name], mergeable_ranks=ranks, special_tokens={})
    cl = lambda s: len(enc["cl100k_base"].encode(s, disallowed_special=()))
    old = lambda s: len(enc["r50k_base"].encode(s, disallowed_special=()))
    ll = Tokenizer.from_file(str(src / "llama-family-tokenizer-proxy.json"))
    ll.no_padding()
    ll.no_truncation()
    llama = lambda s: len(ll.encode(s, add_special_tokens=False).ids)
    audit = {"method": "Original-input reconstruction and explicitly stated workload assumptions", "points": {}}

    # Original MMLU data and original GPT-3 prompt, including its 2048-token crop.
    data = {}
    with tarfile.open(src / "mmlu-data.tar") as archive:
        for member in archive.getmembers():
            if member.isfile() and member.name.endswith(".csv") and member.name.startswith(("data/dev/", "data/test/")):
                data[member.name] = list(csv.reader(io.StringIO(archive.extractfile(member).read().decode())))
    subjects = sorted(k.removeprefix("data/test/").removesuffix("_test.csv") for k in data if k.startswith("data/test/"))
    def example(row, answer=True):
        return row[0] + "".join(f"\n{letter}. {choice}" for letter, choice in zip("ABCD", row[1:5])) + "\nAnswer:" + (" " + row[5] + "\n\n" if answer else "")
    mmlu = {"gpt3": [], "gpt4": [], "llama": []}
    word_counts = []
    for subject in subjects:
        dev, test = data[f"data/dev/{subject}_dev.csv"], data[f"data/test/{subject}_test.csv"]
        counts = {k: [] for k in mmlu}
        shots = []
        for row in test:
            prefix = "The following are multiple choice questions (with answers) about  " + subject.replace("_", " ") + ".\n\n"
            prompt = prefix + "".join(example(x) for x in dev[:5]) + example(row, False)
            counts["gpt4"].append(cl(prompt) + 1)
            # Meta's exact chat wrapper and outputs are not public without gated access.
            # Original 5-shot prompt + 12 chat positions + full documented 10-token cap.
            counts["llama"].append(llama(prompt) + 12 + 10)
            k = 5
            while old(prompt) > 2048:
                k -= 1
                prompt = prefix + "".join(example(x) for x in dev[:k]) + example(row, False)
            shots.append(k)
            counts["gpt3"].append(old(prompt) + 1)
            word_counts.append(len(example(row, False).split()))
        for key in mmlu:
            mmlu[key].append({"subject": subject, "n": len(test), "mean_tokens": avg(counts[key]), "token_sum": sum(counts[key])})
    audit["mmlu"] = {"subjects": len(subjects), "questions": len(word_counts), "mean_question_words": avg(word_counts), "by_model": mmlu}
    for point, model, key, macro in [
        ("lang-exam-mmlu-gpt4", "gpt-4-base-2023-report", "gpt4", False),
        ("lang-mmlu-parity-typical", "gpt-3-davinci-175b", "gpt3", False),
        ("lang-mmlu-parity-expert", "llama-3.1-405b-instruct", "llama", True),
    ]:
        tokens = avg(r["mean_tokens"] for r in mmlu[key]) if macro else sum(r["token_sum"] for r in mmlu[key]) / len(word_counts)
        audit["points"][point] = {"model_id": model, "tokens": tokens, "weighting": "equal subject then equal question" if macro else "equal question"}

    # GRE: question text from all 35 questions of the current official accessible
    # practice test, with every common reading passage repeated for each question.
    gre = gre_questions(src / "gre-verbal-accessible.pdf")
    qmean = avg(cl(x["text"]) for x in gre)
    report = pdf(src / "gpt4-report.pdf", "-layout")
    section = report[report.index("Example prompt for a multiple choice exam (AP Art History") :]
    demos = section[section.index("ANSWER KEY"):section.index("Problem 6.")]
    demos = re.sub(r"\n\s*\d+\s*\n\f", "\n", demos)
    explanation_samples = re.findall(r"Explanation for Problem \d+: (.*?)The answer is therefore", demos, flags=re.S)
    assert len(explanation_samples) == 5
    # Task-specific GRE demonstration questions, but explanation length transferred
    # from the five fully printed exam demonstration explanations (not a claimed log).
    explanation = avg(cl(norm(x)) for x in explanation_samples)
    input_tokens = 5 * (qmean + explanation + 15) + qmean + 25
    # Report: sample explanation, then send the existing explanation to sample letters.
    # Central counts the full input again in the answer-extraction call. The record
    # does not establish persistent KV reuse between these two sampling requests.
    shared_prefix = input_tokens + explanation + 8 + 2
    full_reprefill = 2 * input_tokens + 2 * explanation + 8 + 2
    audit["gre"] = {"sample_questions": len(gre), "question_tokens_mean": qmean, "demonstration_explanation_tokens_mean": explanation, "assumed_input_tokens": input_tokens, "tokens_if_prefix_KV_reused": shared_prefix, "questions": gre}
    audit["points"]["lang-exam-gre-verbal-gpt4"] = {"model_id": "gpt-4-2023-03-01-internal", "tokens": full_reprefill}

    # MBE: preserve the exact average over released configurations, but borrow input
    # length from all 21 original NCBE sample questions; the 200 paid items are absent.
    mbe = mbe_questions(src / "ncbe-sample.pdf")
    mbe_mean = avg(cl(q) for q in mbe)
    records = [r for r in csv.DictReader((src / "bar-mbe-results.csv").open()) if r["model"] == "openai:hidden-gpt-4-model-name"]
    configs = {}
    for r in records:
        key = (r["prompt"], r["temperature"], r["best_of"], r["max_tokens"])
        configs.setdefault("|".join(key), []).append(r)
    # Exact printed templates, stripped of their variable question/choice positions.
    common = "\n-----\nQuestion: \n(A) \n(B) \n(C) \n(D) \n-----\n\nAnswer: "
    p6 = "Act as if you are taking the Bar Exam.\nPlease answer the following question in this rank order format: \nFirst Choice: <LETTER>\nSecond Choice: <LETTER>\nThird Choice: <LETTER>\nExplanation of Choices: <EXPLANATION>\nAuthority or Citation for Explanation: " + common
    p7 = "Answer the following Bar Exam question in the following rank order format: \nFirst Choice: <LETTER>\nSecond Choice: <LETTER>\nThird Choice: <LETTER>\n" + common
    short_answer = "First Choice: A\nSecond Choice: B\nThird Choice: C"
    # p6 requests a rationale after ranked choices; use its actual 64-token cap.
    # p7 requests only three ranked letters; count that literal response template.
    output = (64 + cl(short_answer)) / 2
    formatted_inputs = []
    for question in mbe:
        parts = re.split(r"\([ABCD]\)", question)
        assert len(parts) == 5
        for template in [p6, p7]:
            filled = template.replace("Question: \n", "Question: " + parts[0].strip() + "\n")
            for letter, choice in zip("ABCD", parts[1:]):
                filled = filled.replace(f"({letter}) \n", f"({letter}) {choice.strip()}\n")
            formatted_inputs.append(cl(filled))
    mbe_tokens = avg(formatted_inputs) + output
    audit["mbe"] = {"sample_questions": len(mbe), "mean_question_tokens": mbe_mean, "formatted_input_tokens_mean": avg(formatted_inputs), "response_tokens_assumed_mean": output, "records": len(records), "correct": sum(r["is_correct"] == "True" for r in records), "accuracy": avg(r["is_correct"] == "True" for r in records), "configs": {k: {"records": len(v), "accuracy": avg(r["is_correct"] == "True" for r in v)} for k, v in configs.items()}, "sample_question_text": mbe}
    audit["points"]["lang-exam-mbe-gpt4"] = {"model_id": "gpt-4-bar-exam-preview", "tokens": mbe_tokens}

    usmle = usmle_questions(src / "step1-items.pdf")
    intro = "The following are multiple choice questions (with answers) about medical knowledge.\n**Question:** "
    values = [cl(intro + q + "\n**Answer:**(") + 12 + 1 for q in usmle]
    audit["usmle"] = {"proxy_edition": "April 2026", "proxy_questions": len(usmle), "question_tokens_mean": avg(cl(q) for q in usmle), "prompt_tokens_mean": avg(values) - 1, "output_tokens": 1, "question_text": usmle}
    audit["points"]["lang-exam-usmle-gpt4"] = {"model_id": "gpt-4-original-unspecified", "tokens": avg(values)}

    # PaLM: original 46-item JSON task and default prompt builder; expected length
    # across uniform five-shot choices avoids pretending the historical seed is known.
    bb = json.loads((src / "bigbench-known-unknowns.json").read_text())["examples"]
    inputs, targets, gold = [], [], []
    for item in bb:
        choices = list(item["target_scores"])
        inputs.append("\nQ: " + item["input"] + "\n  choice: " + "\n  choice: ".join(choices) + "\nA: ")
        targets.append(choices)
        gold.append(next(k for k, v in item["target_scores"].items() if v == 1))
    demo_lengths = [cl(x + y + "\n") for x, y in zip(inputs, gold)]
    prefills = [cl(x) + 5 * (sum(demo_lengths) - demo_lengths[i]) / (len(bb) - 1) for i, x in enumerate(inputs)]
    continuations = [sum(cl(t) for t in ts) for ts in targets]
    # Conditional likelihoods require both answer strings. Central uses independent
    # full prefills; also retain the efficient shared-prefix alternative.
    bb_tokens = avg(2*x + y for x, y in zip(prefills, continuations))
    human = HumanDataUnpickler(io.BytesIO((src / "bigbench-human.pkl").read_bytes())).load()["average"]["known_unknowns"]["multiple_choice_grade"]
    scores = json.loads((src / "bigbench-palm-example.json").read_text())["scores"]
    ai_score = next(r["score_dict"]["multiple_choice_grade"] for r in scores if r["number_of_shots"] == 5)
    audit["bigbench"] = {"questions": len(bb), "tokenizer": "cl100k proxy for unpublished PaLM tokenizer", "mean_prefill_tokens": avg(prefills), "mean_two_target_tokens": avg(continuations), "tokens_if_prefix_KV_shared": avg(x+y for x,y in zip(prefills, continuations)), "ai_accuracy": ai_score, "human_accuracy_percent": human}
    audit["points"]["lang-bigbench-parity-palm"] = {"model_id": "palm-540b-original", "tokens": bb_tokens}

    # Original Wiki QA records, mirrored without documents. Count all validation
    # questions and expected five demonstrations drawn uniformly from training.
    # Exact Meta demonstration IDs and wrapper remain unknown; no native usage claim.
    trivia = {}
    for split, expected_n in [("train", 61888), ("validation", 7993)]:
        rows = pq.read_table(src / f"triviaqa-wiki-{split}-00000-of-00001.parquet",
                             columns=["question", "question_id", "answer"]).to_pylist()
        assert len(rows) == expected_n == len({r["question_id"] for r in rows})
        counts = []
        for row in rows:
            q, a = row["question"], row["answer"]["value"]
            counts.append({"question_id": row["question_id"],
                           "question_words": len(q.split()),
                           "question_tokens": llama(q), "answer_tokens": llama(a),
                           "demonstration_tokens": llama(f"Question: {q}\nAnswer: {a}\n\n"),
                           "query_tokens": llama(f"Question: {q}\nAnswer:")})
        trivia[split] = {"questions": len(rows),
                         "means": {k: avg(r[k] for r in counts) for k in counts[0] if k != "question_id"},
                         "token_counts": counts}
    training, validation = trivia["train"]["means"], trivia["validation"]["means"]
    prompt_tokens = 5 * training["demonstration_tokens"] + validation["query_tokens"] + 1
    ttokens = prompt_tokens + 8
    trivia.update({"demonstration_rule": "Expected five uniform draws from the training split",
                   "demonstration_answer": "Original canonical answer.value, not all aliases",
                   "wrapper": "Question: {question}\\nAnswer: {answer}\\n\\n",
                   "query_wrapper": "Question: {question}\\nAnswer:",
                   "assumed_bos_tokens": 1, "assumed_output_tokens": 8,
                   "source_max_output_tokens": 24, "input_tokens": prompt_tokens,
                   "tokens_if_gold_length_plus_one_stop": prompt_tokens + validation["answer_tokens"] + 1,
                   "tokens_if_24_output": prompt_tokens + 24,
                   "tokens_if_validation_demos": 5 * validation["demonstration_tokens"] + validation["query_tokens"] + 1 + 8})
    audit["trivia"] = trivia
    audit["points"]["lang-trivia-question-llm"] = {"model_id": "llama-3.1-405b-base", "tokens": ttokens}

    if args.models:
        models = {r["model_id"]: r for r in csv.DictReader(args.models.open())}
        for value in audit["points"].values():
            value["flops_per_token"] = float(models[value["model_id"]]["flops_per_token"])
            value["compute_flops"] = value["tokens"] * value["flops_per_token"]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({k: v for k, v in audit["points"].items()}, indent=2))


if __name__ == "__main__":
    main()
