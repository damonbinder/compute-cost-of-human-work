#!/usr/bin/env python3
"""Recount fixed Epoch prompts with original/proxy vocabularies.

Requires tokenizers, sentencepiece and pyarrow. All paths are explicit; no network.
Original sources and existing outputs are never overwritten.
"""
import argparse
import ast
import csv
import hashlib
import json
import math
import statistics
from pathlib import Path

import pyarrow
import pyarrow.parquet as pq
import sentencepiece
import tokenizers


def csv_rows(path):
    with path.open(newline='') as f:
        return list(csv.DictReader(f))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--sources', type=Path, required=True)
    ap.add_argument('--points', type=Path, required=True)
    ap.add_argument('--models', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args()
    s, o = a.sources.resolve(), a.output.resolve()
    if o.exists() or o.is_relative_to(s) or o in [a.points.resolve(), a.models.resolve()]:
        ap.error('Output must be new and outside the sources directory.')
    hashes = {}
    for item in json.loads((s/'source-manifest.json').read_text())['files']:
        p = (s/item['path']).resolve()
        if not p.is_relative_to(s):
            raise ValueError('Source path escape')
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        assert h == item['sha256'], item['path']
        hashes[item['path']] = h

    gpqa = csv_rows(s/'gpqa_diamond.csv')
    code = json.loads((s/'gpqa-gist.json').read_text())['files']['gpqa.py']['content']
    tree = ast.parse(code)
    assignment = next(x for x in tree.body if isinstance(x, ast.Assign) and any(
        isinstance(y, ast.Name) and y.id == 'SIMPLE_COT_TEMPLATE' for y in x.targets))
    template = ast.literal_eval(assignment.value.func.value).strip()
    answer_fields = ['Correct Answer', 'Incorrect Answer 1', 'Incorrect Answer 2', 'Incorrect Answer 3']
    gp = [template.format(letters='A,B,C,D', question=q['Question'], choices='\n'.join(
        f'{chr(65+i)}) {q[k]}' for i, k in enumerate(answer_fields))) for q in gpqa]
    math_questions = [q for f in sorted(s.glob('math-test-*.parquet'))
                      for q in pq.read_table(f).to_pylist() if q['level'] == 'Level 5']
    otis = json.loads((s/'otis-original-question-text.json').read_text())['questions']
    prompts = {'gpqa': gp, 'mathl5': [q['problem'] for q in math_questions],
               'otis': [q['observed_instruction_before']+q['question']+q['observed_instruction_after'] for q in otis]}
    assert {k: len(v) for k, v in prompts.items()} == {'gpqa': 198, 'mathl5': 1324, 'otis': 45}
    wrappers = {'gpqa': 12, 'mathl5': 50, 'otis': 12}
    files = {'gemma2': 'gemma-tokenizer.model', 'llama2': 'llama2-tokenizer.model',
             'mixtral8x7': 'mistralai--Mixtral-8x7B-Instruct-v0.1--tokenizer.json',
             'mixtral8x22': 'mixtral8x22-tokenizer.json', 'nemo': 'nemo-tokenizer.json',
             'phi3': 'phi3-tokenizer.json', 'mistral3': 'mistral3-tokenizer.json'}
    counts = {}
    for key, file in files.items():
        if file.endswith('.model'):
            enc = sentencepiece.SentencePieceProcessor(model_file=str(s/file))
            length = lambda text: len(enc.encode(text, out_type=int))
        else:
            enc = tokenizers.Tokenizer.from_file(str(s/file))
            length = lambda text: len(enc.encode(text, add_special_tokens=False).ids)
        counts[key] = {b: [length(q)+wrappers[b] for q in qs] for b, qs in prompts.items()}

    specs = [
        ('reas-epoch-mathl5-gemma2-9b', 'gemma-2-9b-it', 'mathl5', 'nemo', 'gemma2'),
        ('reas-epoch-otis-gemma2-9b', 'gemma-2-9b-it', 'otis', 'nemo', 'gemma2'),
        ('reas-epoch-gpqa-gemma2-27b', 'gemma-2-27b-it', 'gpqa', 'nemo', 'gemma2'),
        ('reas-epoch-mathl5-gemma2-27b', 'gemma-2-27b-it', 'mathl5', 'nemo', 'gemma2'),
        ('reas-epoch-otis-gemma2-27b', 'gemma-2-27b-it', 'otis', 'nemo', 'gemma2'),
        ('reas-epoch-mathl5-llama2-70b', 'Llama-2-70b-chat-hf', 'mathl5', 'phi3', 'llama2'),
        ('reas-epoch-mathl5-mixtral8x7b', 'Mixtral-8x7B-Instruct-v0.1', 'mathl5', 'mistral3', 'mixtral8x7'),
        ('reas-epoch-gpqa-mixtral8x22b', 'open-mixtral-8x22b', 'gpqa', 'mistral3', 'mixtral8x22'),
        ('reas-epoch-mathl5-mixtral8x22b', 'open-mixtral-8x22b', 'mathl5', 'mistral3', 'mixtral8x22')]
    benchmarks = {'gpqa': 'GPQA diamond', 'mathl5': 'MATH level 5', 'otis': 'OTIS Mock AIME 2024-2025'}
    table = csv_rows(s/'scatter_data.csv')
    points = {r['point_id']: r for r in csv_rows(a.points)}
    models = {r['model_id']: r for r in csv_rows(a.models)}
    results = {}
    for pid, identity, bench, old, new in specs:
        found = [r for r in table if r['Identifier'] == identity and r['Benchmark'] == benchmarks[bench]]
        assert len(found) == 1, pid
        source = found[0]
        out = float(source['Output tokens per question'])
        row = points[pid]
        coef = float(models[row['model_id']]['flops_per_token'])
        old_input = statistics.mean(counts[old][bench])
        new_input = statistics.mean(counts[new][bench])
        # Permit the archived or corrected CSV, so the published calculator does
        # not depend on a private audit directory. Neither supplies token inputs.
        assert any(math.isclose(inp+out, float(row['tokens']), rel_tol=1e-12) and
                   math.isclose((inp+out)*coef, float(row['compute_flops']), rel_tol=1e-12)
                   for inp in [old_input, new_input]), pid
        results[pid] = {'identifier': identity, 'benchmark': bench, 'old_tokenizer': old,
                        'new_tokenizer': new, 'old_input': old_input, 'new_input': new_input,
                        'output': out, 'coefficient': coef, 'tokens': new_input+out,
                        'compute_flops': (new_input+out)*coef,
                        'token_delta': new_input-old_input,
                        'compute_fraction_delta': (new_input-old_input)/(old_input+out),
                        'different_question_counts': sum(x != y for x, y in zip(counts[old][bench], counts[new][bench])),
                        'source_row': source}
    result = {'points': results, 'counts': counts, 'source_sha256': hashes,
              'prompt_sha256': {k: hashlib.sha256(json.dumps(v, ensure_ascii=False).encode()).hexdigest()
                                for k, v in prompts.items()},
              'wrapper_positions': wrappers,
              'versions': {'tokenizers': tokenizers.__version__, 'sentencepiece': sentencepiece.__version__,
                           'pyarrow': pyarrow.__version__}}
    o.parent.mkdir(parents=True, exist_ok=True)
    with o.open('x') as f:
        json.dump(result, f, indent=2, sort_keys=True)
        f.write('\n')
    print(json.dumps({k: {f: r[f] for f in ['old_input', 'new_input', 'token_delta', 'compute_fraction_delta']}
                      for k, r in results.items()}, indent=2))


if __name__ == '__main__':
    main()
