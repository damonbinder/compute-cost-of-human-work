"""Reconstruct released summary workloads. Requires tiktoken; no network or API calls.

Supply --sources, --models (CSV), and a new --output JSON path.
"""
import argparse
import csv
import hashlib
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

import tiktoken
from tiktoken.load import load_tiktoken_bpe
from tiktoken_ext.openai_public import r50k_pat_str


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sources', type=Path, required=True)
    p.add_argument('--models', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    src, out = a.sources.resolve(), a.output.resolve()
    if out.exists() or src == out or src in out.parents or out == a.models.resolve():
        p.error('output must be new and outside the source evidence')
    ranks = src / 'p50k_base.tiktoken'
    assert sha(ranks) == '94b5ca7dff4d00767bc256fdd1b27e5b17361d7b8a5f968547f9f23eb70d2069'
    enc = tiktoken.Encoding(name='p50k_retained', pat_str=r50k_pat_str,
                           mergeable_ranks=load_tiktoken_bpe(str(ranks)),
                           special_tokens={'<|endoftext|>': 50256})
    rows = json.loads((src / 'pairwise_evaluation_results.json').read_text())
    unique = {}
    for r in rows:
        ident = r['article_id']
        pair = (r['article_text'], r['text-davinci-002_summary'])
        if ident in unique:
            assert unique[ident] == pair, 'article ID has conflicting input or model output'
        unique[ident] = pair
    models = {r['model_id']: r for r in csv.DictReader(a.models.open(newline=''))}
    coefficient = Fraction(models['text-davinci-002']['flops_per_token'])
    details = []
    for ident, (article, summary) in sorted(unique.items()):
        # Source gives the template and a changed 25-word instruction; whitespace is reconstructed.
        prompt = f'Article: {article}\nSummarize the article in 25 words.\nSummary:'
        ni = len(enc.encode(prompt))
        no = len(enc.encode(summary))
        # One omitted leading newline and one stop position are explicit assumptions.
        positions = ni + no + 2
        details.append(dict(article_id=ident, input_tokens=ni, visible_output_tokens=no,
                            assumed_output_overhead=2, tokens=positions,
                            compute_flops=int(coefficient * positions),
                            article_words=len(article.split()), summary_words=len(summary.split())))
    n = len(details)
    avg = lambda field: float(Fraction(sum(r[field] for r in details), n))
    counts = {field: dict(Counter(str(r[field]) for r in rows))
              for field in ['overall_writer_better', 'informative_writer_better']}
    assert n == 76 and len(rows) == 599
    assert len({(r['article_id'], r['writer_summary'], r['evaluator_id']) for r in rows}) == 599
    result = dict(
        point_id='writing-news-summary-textdavinci002',
        source_sha256={name: sha(src / name) for name in
                       ['pairwise_evaluation_results.json', 'p50k_base.tiktoken']},
        model_coefficient=float(coefficient), attempts=n, rating_count=len(rows),
        distinct_human_summary_pairs=len({(r['article_id'], r['writer_summary']) for r in rows}),
        evaluator_count=len({r['evaluator_id'] for r in rows}), performance_counts=counts,
        mean_input_tokens=avg('input_tokens'), mean_visible_output_tokens=avg('visible_output_tokens'),
        mean_tokens=avg('tokens'), mean_compute_flops=avg('compute_flops'),
        mean_article_words=avg('article_words'), mean_summary_words=avg('summary_words'),
        max_input_tokens=max(r['input_tokens'] for r in details),
        human_time_seconds=13.5 * 60, source_human_estimate_seconds=[12 * 60, 15 * 60],
        prompt_and_output_overhead_scenario_flops=[avg('compute_flops') - float(coefficient) * 2,
                                                 avg('compute_flops') + float(coefficient) * 32],
        details=details)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'details'}, indent=2))


if __name__ == '__main__':
    main()
