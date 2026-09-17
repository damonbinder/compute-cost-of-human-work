#!/usr/bin/env python3
"""Reconstruct the AI compute and human time for one LAIT evaluation-book run.

LAIT (arXiv 2606.26040) logged per-job token usage but withheld the run
workspaces that hold it, so this script rebuilds the workload from what the paper
and the public pipeline code do publish: the chunking rule, the eight-stage model
mapping, the prompt templates, and the corpus counts in Tables 1, 7, 8 and 9.

Everything the paper states is read from a source-values JSON; everything this
script adds is an explicit assumption declared in ASSUMPTIONS below, and every
assumption is swept over a low/central/high grid so the output carries a range,
not a point.

Dependencies: Python 3.9+, tiktoken (only for measuring the prompt templates; if
tiktoken is unavailable pass --skip-template-measurement and the transcribed
counts in the source-values JSON are used instead).

Usage:
  python3 compute_lait.py \
      --source-values agent-work/sources/lait/lait-source-values.json \
      --prompts-dir  agent-work/sources/lait/repo \
      --models-csv   "../../../AI Compute vs Human Time/dataset/models.csv" \
      --withheld-tsv agent-work/sources/lait/repo/docs-release-withheld-files.tsv \
      --out          lait-calculations.json

All paths are explicit; the script writes only --out and reads nothing else.
"""

import argparse
import csv
import itertools
import json
import math
import os
import re
import statistics

# ---------------------------------------------------------------------------
# Assumptions. Nothing below is published by LAIT.
# ---------------------------------------------------------------------------

ASSUMPTIONS = {
    "harness_overhead_tokens": {
        "what": "System prompt plus tool schemas prepended by the agent CLI to every job. "
                "Claude Code runs with --bare and --tools Read,Write; Codex runs `codex exec`.",
        "low": 1500, "central": 3500, "high": 8000,
    },
    "harness_cache_reuse": {
        "what": "Whether the identical harness prefix of repeated same-stage jobs is a "
                "provider-side cache read (excluded from the parameter-multiplication term) "
                "or is re-created per job. --no-session-persistence makes every job a fresh "
                "conversation, but the provider prefix cache can still hit across jobs.",
        "low": True, "central": False, "high": False,
    },
    "style_bible_tokens": {
        "what": "Size of outputs/style_bible.json: character voice profiles, prose-style "
                "profile, terminology and named entities for an ~8K-word excerpt.",
        "low": 800, "central": 1500, "high": 3000,
    },
    "reasoning_multiplier": {
        "what": "Scale on the per-stage reasoning-token estimates in STAGES. Claude Code ran at "
                "effort `max` and Codex at `xhigh`; neither publishes a reasoning-token count.",
        "low": 0.5, "central": 1.0, "high": 2.0,
    },
    "global_source_read_fraction": {
        "what": "Fraction of the run's source chunks that book_review and cross_chunk_audit "
                "actually read. Both prompts point the agent at inputs/source_chunk_####.txt "
                "for traceability but do not require reading all of them.",
        "low": 0.4, "central": 1.0, "high": 1.0,
    },
    "retry_uplift": {
        "what": "Extra token cost from jobs that were executed more than once. The corpus pins the "
                "count: 2,930 published job-metric records against 2,723 distinct job manifests in "
                "the same 31 runs, so 207 records (7.07% of records, 7.60% of distinct jobs) are "
                "second executions. They cannot be in-loop retries or quota pauses: _run_job in "
                "core/executor.py writes its manifest once before the retry loop and appends "
                "exactly one metric record at whichever terminal point it reaches, recording "
                "in-loop retries only as attempt_count and quota_pause_count on that single "
                "record. Each excess record is therefore a second full _run_job invocation under "
                "the same job_id, overwriting the same manifest - the ResumePoint restart path. "
                "Central charges each as a full job; low charges each as half a job, allowing for "
                "a restart that aborts early. There is no mechanism for more than 7.60%.",
        "low": 0.038, "central": 0.076, "high": 0.076,
    },
}

# Per-stage model, prompt template, what enters the context, and what is generated.
# `reason` is an assumed reasoning-token volume at the stage's effort setting;
# `writes` is the content the agent writes into its output file.
STAGES = {
    "style_analysis": {
        "provider": "claude", "model_key": "claude",
        "turns": 3,
        "reason": 6000,
        "notes": "Runs once per run. Reads inputs/full_source.txt, writes outputs/style_bible.json.",
    },
    "translate": {
        "provider": "codex", "model_key": "gpt",
        "turns": 3,
        "reason": 2500,
        "notes": "One per chunk in local cycle 1. Reads the style bible; source chunk and both "
                 "boundary contexts are inline in the prompt.",
    },
    "litrans_review": {
        "provider": "codex", "model_key": "gpt",
        "turns": 2,
        "reason": 3000,
        "notes": "One per chunk per local cycle. 25 yes/no/maybe questions; everything inline, "
                 "no file read.",
    },
    "chunk_literary_review": {
        "provider": "claude", "model_key": "claude",
        "turns": 3,
        "reason": 3000,
        "notes": "One per chunk per local cycle. Reads the style bible.",
    },
    "revise": {
        "provider": "codex", "model_key": "gpt",
        "turns": 3,
        "reason": 2500,
        "notes": "One per failing chunk in local cycles 2+. Carries both review payloads inline.",
    },
    "book_review": {
        "provider": "codex", "model_key": "gpt",
        "turns": 8,
        "reason": 6000,
        "notes": "One per global cycle. Reads the reconstructed draft, the style bible and the "
                 "source chunks.",
    },
    "cross_chunk_audit": {
        "provider": "codex", "model_key": "gpt",
        "turns": 8,
        "reason": 5000,
        "notes": "One per global cycle, in parallel with book_review; same read set.",
    },
    "final_revise": {
        "provider": "claude", "model_key": "claude",
        "turns": 5,
        "reason": 3000,
        "notes": "One per affected chunk between global cycles. Reads the full source, the full "
                 "draft and the style bible.",
    },
}

TOOL_RESULT_OVERHEAD = 60   # wrapper tokens per tool call/result pair
FINAL_MESSAGE_TOKENS = 60   # the agent's closing text message

# Bracketing architectures for the omitted cached-context attention term, at the
# dataset's shared 100B-active assumption. 4 * layers * d_model.
ATTENTION_SHAPES = [
    {"label": "L=64, d_model=8192", "layers": 64, "d_model": 8192},
    {"label": "L=80, d_model=10240", "layers": 80, "d_model": 10240},
    {"label": "L=96, d_model=12288", "layers": 96, "d_model": 12288},
]

# List prices, USD per million tokens, from agent-work/sources/lait/model-list-prices-2026-09-13.md.
# Used only for the independent cost cross-check; no compute value depends on them.
LIST_PRICES = {
    "claude": {"model": "Claude Opus 4.6", "input": 5.00, "output": 25.00},
    "gpt": {"model": "GPT-5.4", "input": 2.50, "output": 15.00},
}


# ---------------------------------------------------------------------------
# Prompt template measurement
# ---------------------------------------------------------------------------

PROMPT_FILES = {
    "style_analysis": "prompt-style_analysis.txt",
    "translate": "prompt-translate.txt",
    "litrans_review": "prompt-litrans_review.txt",
    "chunk_literary_review": "prompt-chunk_literary_review.txt",
    "revise": "prompt-revise.txt",
    "book_review": "prompt-book_review.txt",
    "cross_chunk_audit": "prompt-cross_chunk_audit.txt",
    "final_revise": "prompt-final_revise.txt",
}


def measure_templates(prompts_dir):
    """Token count of each prompt template with its {placeholders} removed."""
    import tiktoken
    enc = tiktoken.get_encoding("o200k_base")
    out = {}
    for stage, fname in PROMPT_FILES.items():
        path = os.path.join(prompts_dir, fname)
        text = open(path, encoding="utf-8").read()
        stripped = re.sub(r"\{[a-z_]+(?::[^}]*)?\}", "", text)
        out[stage] = len(enc.encode(stripped))
    return out


# ---------------------------------------------------------------------------
# Pipeline structure solved from the published corpus counts
# ---------------------------------------------------------------------------

STAGE_PREFIXES = sorted(STAGES, key=len, reverse=True)


def measure_structure(withheld_tsv, sv):
    """Count chunks and agent jobs per evaluation run from the withheld-file manifest.

    `docs/release/withheld-files.tsv` lists every path removed from the public branch,
    which includes the whole of each run workspace. Two path families are countable:

      runs/<run>/inputs/source_chunk_NNNN.txt
          one per source chunk entering the pipeline

      runs/<run>/manifests/<stage>_<book>[_chunk_NNNN]_cycle_NN.json
          one per agent job, written by _write_manifest in core/executor.py

    So the workload structure is measured, not inferred. The Table 9 corpus totals are
    recomputed here as a cross-check.
    """
    inv = sv["run_inventory"]
    eval_runs = set(inv["evaluation_run_directories"])
    multi_runs = set(inv["multilingual_run_directories"])

    chunks = {}
    jobs = {}
    metrics = set()
    manifests_all = 0
    with open(withheld_tsv, newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh, delimiter="\t")
        next(reader)
        for row in reader:
            path = row[0]
            if not path.startswith("runs/"):
                continue
            parts = path.split("/")
            run = parts[1]
            rest = "/".join(parts[2:])
            if rest.startswith("inputs/source_chunk_"):
                chunks[run] = chunks.get(run, 0) + 1
            elif rest == "metrics/run_summary.json":
                metrics.add(run)
            elif rest.startswith("manifests/"):
                manifests_all += 1
                name = rest[len("manifests/"):-len(".json")]
                stage = next((st for st in STAGE_PREFIXES
                              if name == st or name.startswith(st + "_")), None)
                if stage is None:
                    raise SystemExit("unrecognised manifest stage: %s" % name)
                jobs.setdefault(run, {})
                jobs[run][stage] = jobs[run].get(stage, 0) + 1

    missing = eval_runs - set(chunks)
    if missing:
        raise SystemExit("evaluation runs absent from the manifest: %s" % missing)

    n_eval = len(eval_runs)
    eval_chunks = sum(chunks[r] for r in eval_runs)
    eval_jobs = {st: sum(jobs[r].get(st, 0) for r in eval_runs) for st in STAGES}
    per_run = {r: {"source_chunks": chunks[r],
                   "agent_jobs": sum(jobs[r].values()),
                   "jobs_per_chunk": sum(jobs[r].values()) / chunks[r],
                   "final_revise_jobs": jobs[r].get("final_revise", 0)}
               for r in sorted(eval_runs, key=lambda x: -sum(jobs[x].values()))}

    dev_runs = set(chunks) - eval_runs - multi_runs
    manifests_logged = sum(sum(jobs[r].values()) for r in jobs if r in metrics)

    t9 = sv["table9_artifacts"]
    checks = {
        "runs_in_manifest": len(chunks),
        "runs_published": t9["completed_pipeline_runs"],
        "chunks_in_manifest": sum(chunks.values()),
        "chunks_published": t9["source_chunks_processed"],
        "runs_with_metrics_in_manifest": len(metrics),
        "runs_with_metrics_published": t9["runs_with_job_metric_logs"],
        "distinct_jobs_in_logged_runs": manifests_logged,
        "job_metric_records_published": t9["logged_agent_jobs"],
        "attempts_per_distinct_job": t9["logged_agent_jobs"] / manifests_logged,
        "translate_plus_revise_all_runs": sum(
            jobs[r].get("translate", 0) + jobs[r].get("revise", 0) for r in jobs),
        "final_revise_all_runs": sum(jobs[r].get("final_revise", 0) for r in jobs),
        "chunk_cycle_artifacts_published": t9["chunk_cycle_translation_or_revision_artifacts"],
        "development_runs_identified": len(dev_runs),
        "development_chunks": sum(chunks[r] for r in dev_runs),
    }

    job_totals = [v["agent_jobs"] for v in per_run.values()]
    return {
        "evaluation_runs": n_eval,
        "per_evaluation_run": per_run,
        "agent_jobs_per_run_min": min(job_totals),
        "agent_jobs_per_run_max": max(job_totals),
        "agent_jobs_per_run_spread": max(job_totals) / min(job_totals),
        "evaluation_chunks_total": eval_chunks,
        "chunks_per_evaluation_book": eval_chunks / n_eval,
        "chunks_per_evaluation_book_min": min(chunks[r] for r in eval_runs),
        "chunks_per_evaluation_book_max": max(chunks[r] for r in eval_runs),
        "jobs_total_evaluation_runs": eval_jobs,
        "jobs_per_evaluation_book": {st: eval_jobs[st] / n_eval for st in STAGES},
        "jobs_per_evaluation_book_total": sum(eval_jobs.values()) / n_eval,
        "local_cycles_per_chunk": (eval_jobs["translate"] + eval_jobs["revise"]) / eval_chunks,
        "final_revise_per_chunk": eval_jobs["final_revise"] / eval_chunks,
        "global_cycles_per_run": eval_jobs["book_review"] / n_eval,
        "cross_checks": checks,
    }


def job_counts_per_evaluation_book(struct):
    """Jobs of each stage for one evaluation-book run, measured."""
    return dict(struct["jobs_per_evaluation_book"])


# ---------------------------------------------------------------------------
# Per-job token model
# ---------------------------------------------------------------------------

def per_job_tokens(stage, sv, templates, geom, knobs):
    """Distinct input tokens, generated tokens and tool-call count for one job."""
    t1 = sv["table1_evaluation_books"]
    src_book = t1["src_tokens_mean"]
    mt_book = t1["mt_tokens_mean"]
    n = geom["chunks_per_evaluation_book"]
    src_chunk = src_book / n
    mt_chunk = mt_book / n
    bib = knobs["style_bible_tokens"]
    bound = sv["pipeline_implementation"]["boundary_context_tokens_per_side"] * 1.1  # paragraph-rounded
    tmpl = templates[stage]
    rm = knobs["reasoning_multiplier"]
    frac = knobs["global_source_read_fraction"]

    inline = 0.0
    reads = 0.0
    n_reads = 0
    writes = 0.0

    if stage == "style_analysis":
        reads, n_reads = src_book, 1
        writes = bib
    elif stage == "translate":
        inline = src_chunk + 2 * bound
        reads, n_reads = bib, 1
        writes = mt_chunk
    elif stage == "litrans_review":
        inline = src_chunk + mt_chunk + 4 * bound
        writes = 25 * 28                      # 25 judgments with a short issue string each
    elif stage == "chunk_literary_review":
        inline = src_chunk + mt_chunk + 4 * bound
        reads, n_reads = bib, 1
        writes = 600                          # four lens verdicts plus findings
    elif stage == "revise":
        inline = src_chunk + mt_chunk + 4 * bound + 350 + 400   # failed questions, literary findings
        reads, n_reads = bib, 1
        writes = mt_chunk
    elif stage in ("book_review", "cross_chunk_audit"):
        reads = mt_book + bib + frac * src_book
        n_reads = 2 + max(1, round(frac * n))
        writes = 900 if stage == "book_review" else 700
    elif stage == "final_revise":
        inline = src_chunk + mt_chunk + 500
        reads, n_reads = src_book + mt_book + bib, 3
        writes = mt_chunk + 90                # revised chunk plus the revision report
    else:
        raise KeyError(stage)

    harness = 0.0 if knobs["_harness_free"] else knobs["harness_overhead_tokens"]
    distinct_input = harness + tmpl + inline + reads + n_reads * TOOL_RESULT_OVERHEAD
    generated = STAGES[stage]["reason"] * rm + writes + FINAL_MESSAGE_TOKENS
    return {"distinct_input": distinct_input, "generated": generated,
            "turns": STAGES[stage]["turns"], "reads": reads, "inline": inline,
            "template": tmpl, "harness": harness, "writes": writes}


def run_scenario(sv, templates, struct, knobs):
    jobs = job_counts_per_evaluation_book(struct)

    per_stage = {}
    totals = {"claude": {"counted": 0.0, "input": 0.0, "output": 0.0},
              "gpt": {"counted": 0.0, "input": 0.0, "output": 0.0}}
    attention_sum = {s["label"]: 0.0 for s in ATTENTION_SHAPES}
    conv_lengths = []

    # If harness prefixes are cache reads across same-stage jobs, only the first job
    # of each stage in a run pays for them.
    reuse = knobs["harness_cache_reuse"]

    for stage, njobs in jobs.items():
        if njobs <= 0:
            continue
        paid = per_job_tokens(stage, sv, templates, struct, dict(knobs, _harness_free=False))
        free = per_job_tokens(stage, sv, templates, struct, dict(knobs, _harness_free=True))
        if reuse:
            inp = paid["distinct_input"] + (njobs - 1) * free["distinct_input"]
        else:
            inp = njobs * paid["distinct_input"]
        out = njobs * paid["generated"]
        # Dataset convention: re-entered assistant output counts as fresh input or
        # cache creation, and generation counts separately.
        counted = inp + out + out
        key = STAGES[stage]["model_key"]
        totals[key]["input"] += inp
        totals[key]["output"] += out
        totals[key]["counted"] += counted

        conv = paid["distinct_input"] + paid["generated"]
        conv_lengths.append((njobs, conv))
        for shape in ATTENTION_SHAPES:
            four_ld = 4 * shape["layers"] * shape["d_model"]
            attention_sum[shape["label"]] += njobs * (four_ld * conv * (conv + 1) / 2.0)

        per_stage[stage] = {
            "jobs": njobs, "model_key": key,
            "distinct_input_per_job": paid["distinct_input"],
            "generated_per_job": paid["generated"],
            "conversation_tokens_per_job": conv,
            "counted_tokens_total": counted,
        }

    uplift = 1.0 + knobs["retry_uplift"]
    for k in totals:
        for f in totals[k]:
            totals[k][f] *= uplift
    for lab in attention_sum:
        attention_sum[lab] *= uplift

    tokens_total = totals["claude"]["counted"] + totals["gpt"]["counted"]
    weighted_conv = sum(j * c * c for j, c in conv_lengths) / sum(j * c for j, c in conv_lengths)

    # No-cache upper scenario: without prefix caching each turn re-processes the
    # growing prefix. Content arriving roughly evenly across T assistant turns makes
    # the processed input about (T+1)/2 times the distinct content.
    no_cache_counted = 0.0
    for stage, njobs in jobs.items():
        if njobs <= 0:
            continue
        p = per_job_tokens(stage, sv, templates, struct, dict(knobs, _harness_free=False))
        T = p["turns"]
        no_cache_counted += njobs * (p["distinct_input"] * (T + 1) / 2.0 + 2 * p["generated"])
    no_cache_counted *= uplift

    return {"jobs": jobs, "per_stage": per_stage,
            "model_totals": totals, "tokens_total": tokens_total,
            "attention_flops": attention_sum,
            "token_weighted_mean_context": weighted_conv,
            "no_cache_counted_tokens": no_cache_counted}


# ---------------------------------------------------------------------------

def load_coefficients(models_csv):
    want = {"claude": "claude-opus-4-6", "gpt": "gpt-5.4-2026-03-05"}
    found = {}
    with open(models_csv, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            for key, mid in want.items():
                if row["model_id"] == mid:
                    found[key] = {"model_id": mid, "model": row["model"],
                                  "flops_per_token": float(row["flops_per_token"]),
                                  "active_parameters": float(row["active_parameters"]),
                                  "active_parameters_basis": row["active_parameters_basis"]}
    missing = set(want) - set(found)
    if missing:
        raise SystemExit("model records not found in %s: %s" % (models_csv, missing))
    return found


def flops(scen, coef):
    f = {k: scen["model_totals"][k]["counted"] * coef[k]["flops_per_token"] for k in coef}
    f["total"] = sum(f.values())
    return f


def price_cross_check(sv, scen, struct):
    """What the reconstructed workload would have cost at list prices.

    Independent of the $400 subscription: nothing in the token model uses it. Billed
    input is the distinct input plus the re-entered assistant output, priced at the
    base input rate (cache writes are within 25% of it for Opus and unpriced for
    GPT-5.4, and cache hits would make this smaller).
    """
    per_model, total = {}, 0.0
    for key, price in LIST_PRICES.items():
        t = scen["model_totals"][key]
        usd = (t["input"] + t["output"]) / 1e6 * price["input"] + t["output"] / 1e6 * price["output"]
        per_model[key] = {"model": price["model"], "usd_per_evaluation_book": usd}
        total += usd
    t8 = sv["table8_runs"]
    t9 = sv["table9_artifacts"]
    # Corpus size in evaluation-book equivalents, by source chunks.
    eq = t9["source_chunks_processed"] / struct["chunks_per_evaluation_book"]
    return {
        "per_model": per_model,
        "usd_per_evaluation_book": total,
        "evaluation_book_equivalents_in_corpus": eq,
        "usd_for_all_35_runs": total * eq,
        "usd_for_15_evaluation_runs": total * t8["runs_evaluation_books"],
        "reported_subscription_usd": sv["cost_statements"]["subscription_usd_total_experiment"],
        "note": "A flat subscription bounds spend rather than measuring it, so agreement "
                "here shows only that the token model is not off by an order of magnitude.",
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source-values", required=True)
    ap.add_argument("--prompts-dir", required=True)
    ap.add_argument("--models-csv", required=True)
    ap.add_argument("--withheld-tsv", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--skip-template-measurement", action="store_true")
    args = ap.parse_args()

    sv = json.load(open(args.source_values, encoding="utf-8"))
    transcribed = sv["pipeline_implementation"]["prompt_template_tokens_o200k_base_placeholders_removed"]
    if args.skip_template_measurement:
        templates, template_basis = transcribed, "transcribed from the source-values JSON"
    else:
        templates = measure_templates(args.prompts_dir)
        template_basis = "measured from the retained prompt files with tiktoken o200k_base"
        for k, v in templates.items():
            if v != transcribed[k]:
                raise SystemExit("template token mismatch for %s: measured %d, JSON %d"
                                 % (k, v, transcribed[k]))
    coef = load_coefficients(args.models_csv)
    struct = measure_structure(args.withheld_tsv, sv)

    central = {k: ASSUMPTIONS[k]["central"] for k in ASSUMPTIONS}
    central_scen = run_scenario(sv, templates, struct, central)
    central_flops = flops(central_scen, coef)

    # Full grid over the declared assumption levels.
    keys = list(ASSUMPTIONS)
    grid = []
    for combo in itertools.product(*[["low", "central", "high"] for _ in keys]):
        knobs = {k: ASSUMPTIONS[k][lvl] for k, lvl in zip(keys, combo)}
        s = run_scenario(sv, templates, struct, knobs)
        grid.append({"levels": dict(zip(keys, combo)),
                     "tokens_total": s["tokens_total"],
                     "flops_total": flops(s, coef)["total"]})
    tot = sorted(g["flops_total"] for g in grid)
    lo_scen = min(grid, key=lambda g: g["flops_total"])
    hi_scen = max(grid, key=lambda g: g["flops_total"])

    # One-at-a-time sensitivity around the central point.
    sens = {}
    for k in keys:
        row = {}
        for lvl in ("low", "central", "high"):
            knobs = dict(central); knobs[k] = ASSUMPTIONS[k][lvl]
            s = run_scenario(sv, templates, struct, knobs)
            row[lvl] = {"tokens_total": s["tokens_total"], "flops_total": flops(s, coef)["total"]}
        row["ratio_high_over_low"] = row["high"]["flops_total"] / row["low"]["flops_total"]
        sens[k] = row

    # Human side.
    tor = sv["toral_2018"]
    words = sv["table1_evaluation_books"]["ht_words_mean"]
    rate = tor["words_per_hour_from_scratch"]
    hours = words / rate
    human = {
        "words_per_excerpt": words,
        "donor_rate_words_per_hour": rate,
        "hours": hours,
        "seconds": hours * 3600.0,
        "scenarios": {},
    }
    for label, r, mult, why in [
        ("slowest donor translator, from scratch (T3)", 402, 1.0,
         "The slowest of the six translators in the from-scratch condition."),
        ("donor mean rate, from scratch", rate, 1.0,
         "Central: the reported 503 words/hour for condition HT."),
        ("plus one self-revision pass at 3x drafting speed", rate, 1 + 1 / 3.0,
         "A published literary translation is revised; the donor measured first-pass "
         "production only."),
        ("plus revision and editorial response at 2x drafting speed", rate, 1.5,
         "Heavier revision, including responding to a copy-editor."),
        ("trade guidance for creative work, 250 words/hour", 250, 1.0,
         "Low end of published agency guidance for creative text."),
        ("trade guidance for creative work, 125 words/hour", 125, 1.0,
         "Lowest published agency guidance for creative text."),
    ]:
        h = words / r * mult
        human["scenarios"][label] = {"rate_words_per_hour": r, "multiplier": mult,
                                     "hours": h, "seconds": h * 3600.0, "basis": why}

    out = {
        "_about": "Derived values for research/lait.md. Regenerate with compute_lait.py.",
        "template_token_basis": template_basis,
        "prompt_template_tokens": templates,
        "assumptions": ASSUMPTIONS,
        "model_coefficients": coef,
        "structure": struct,
        "central": {
            "per_stage": central_scen["per_stage"],
            "model_totals": central_scen["model_totals"],
            "tokens_total": central_scen["tokens_total"],
            "flops": central_flops,
            "flops_per_human_second": central_flops["total"] / human["seconds"],
            "token_weighted_mean_context": central_scen["token_weighted_mean_context"],
        },
        "range": {
            "grid_points": len(grid),
            "flops_min": tot[0], "flops_max": tot[-1],
            "flops_p10": tot[int(0.10 * (len(tot) - 1))],
            "flops_p90": tot[int(0.90 * (len(tot) - 1))],
            "flops_median": statistics.median(tot),
            "min_levels": lo_scen["levels"], "max_levels": hi_scen["levels"],
            "tokens_min": min(g["tokens_total"] for g in grid),
            "tokens_max": max(g["tokens_total"] for g in grid),
        },
        "sensitivity_one_at_a_time": sens,
        "scenarios": {
            "no_prefix_caching": {
                "what": "Every turn re-processes the growing prefix; no cache reads to exclude.",
                "tokens_total": central_scen["no_cache_counted_tokens"],
                "flops_total": None,
                "ratio_to_central_tokens": central_scen["no_cache_counted_tokens"] / central_scen["tokens_total"],
            },
            "cached_context_attention": {
                "what": "FLOPs the 2 x active_parameters convention omits: attention over the "
                        "context, at 4 * layers * d_model * context_positions per position, "
                        "summed as a causal triangle over each job's conversation.",
                "by_shape": {lab: {"flops": v, "ratio_to_central_compute": v / central_flops["total"]}
                             for lab, v in central_scen["attention_flops"].items()},
            },
            "active_parameter_prior": {
                "what": "Both models carry the dataset's shared 100B-active prior. 30B-300B.",
                "flops_at_30B": central_flops["total"] * 0.3,
                "flops_at_300B": central_flops["total"] * 3.0,
            },
            "output_only_floor": {
                "what": "Generated tokens alone, ignoring every input and re-entry token.",
                "tokens": central_scen["model_totals"]["claude"]["output"] + central_scen["model_totals"]["gpt"]["output"],
                "flops": (central_scen["model_totals"]["claude"]["output"] * coef["claude"]["flops_per_token"]
                          + central_scen["model_totals"]["gpt"]["output"] * coef["gpt"]["flops_per_token"]),
            },
        },
        "price_cross_check": price_cross_check(sv, central_scen, struct),
        "human_time": human,
        "aggregate_15_books": {
            "flops_total": central_flops["total"] * 15,
            "tokens_total": central_scen["tokens_total"] * 15,
            "human_seconds_total": human["seconds"] * 15,
        },
    }
    ncs = out["scenarios"]["no_prefix_caching"]
    ncs["flops_total"] = central_flops["total"] * ncs["ratio_to_central_tokens"]

    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    c = out["central"]
    st = out["structure"]
    print("chunks per evaluation book      %.2f (%d to %d)" % (st["chunks_per_evaluation_book"],
          st["chunks_per_evaluation_book_min"], st["chunks_per_evaluation_book_max"]))
    print("local cycles per chunk          %.3f" % st["local_cycles_per_chunk"])
    print("final_revise per chunk          %.3f" % st["final_revise_per_chunk"])
    print("global cycles per run           %.3f" % st["global_cycles_per_run"])
    for k, v in st["cross_checks"].items():
        print("  check %-38s %s" % (k, round(v, 4) if isinstance(v, float) else v))
    print("agent jobs per evaluation book  %.1f (%d to %d, %.2fx)"
          % (st["jobs_per_evaluation_book_total"], st["agent_jobs_per_run_min"],
             st["agent_jobs_per_run_max"], st["agent_jobs_per_run_spread"]))
    print("counted tokens per book         %.3e" % c["tokens_total"])
    print("  Claude Opus 4.6               %.3e" % c["model_totals"]["claude"]["counted"])
    print("  GPT-5.4                       %.3e" % c["model_totals"]["gpt"]["counted"])
    print("FLOPs per book (central)        %.4e" % c["flops"]["total"])
    print("FLOPs range over %d grid points %.3e to %.3e"
          % (out["range"]["grid_points"], out["range"]["flops_min"], out["range"]["flops_max"]))
    print("human seconds per book          %.0f (%.2f h)" % (human["seconds"], human["hours"]))
    print("FLOPs per human second          %.3e" % c["flops_per_human_second"])
    p = out["price_cross_check"]
    print("list-price cross-check          $%.2f per book, $%.0f for the corpus (subscription $%d)"
          % (p["usd_per_evaluation_book"], p["usd_for_all_35_runs"], p["reported_subscription_usd"]))


if __name__ == "__main__":
    main()
