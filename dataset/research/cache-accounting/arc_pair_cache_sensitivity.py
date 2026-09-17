"""Audit identical ARC prompts and a stated second-prompt cache scenario.
Usage: python arc_pair_cache_sensitivity.py DATASET OUTPUT_JSON
Uses only Python's standard library; refuses to overwrite output.
"""
import argparse
import datetime
import json
import statistics
from pathlib import Path

cli = argparse.ArgumentParser()
cli.add_argument('dataset', type=Path)
cli.add_argument('output', type=Path)
args = cli.parse_args()
if args.output.exists():
    raise SystemExit('Output already exists')

def timestamp(s):
    return datetime.datetime.fromisoformat(s.replace('Z', '+00:00'))

def inputs(metadata):
    return [x for x in metadata['choices'] if x['message']['role'] in ['system', 'user']]

result = {}
for folder in ['kimi-k2.5', 'deepseek-v3.2', 'glm-5']:
    records = []
    for source in sorted((args.dataset / 'agent-work/sources/arc-expansion' / folder).glob('*.json')):
        for pair in json.loads(source.read_text()):
            attempts = [v for k, v in pair.items() if k.startswith('attempt_') and v]
            if len(attempts) != 2:
                continue
            first, second = [a['metadata'] for a in attempts]
            records.append({
                'file': str(source.relative_to(args.dataset)),
                'pair_index': first['pair_index'],
                'identical_input': inputs(first) == inputs(second),
                'second_start_minus_first_end_seconds': (timestamp(second['start_timestamp']) - timestamp(first['end_timestamp'])).total_seconds(),
                'prompt_tokens_first': first['usage']['prompt_tokens'],
                'prompt_tokens_second': second['usage']['prompt_tokens'],
            })
    summary = json.loads((args.dataset / 'research/arc-expansion' / folder / 'summary.json').read_text())
    total, prompt = summary['tokens'], summary['input_tokens']
    # Both prompts have equal native lengths in these pairs. Weighted means are
    # from the existing selected human-matched case set, not all scanned pairs.
    assert all(r['prompt_tokens_first'] == r['prompt_tokens_second'] for r in records)
    result[folder] = {
        'pairs': records,
        'pair_count': len(records),
        'all_inputs_identical': all(r['identical_input'] for r in records),
        'all_second_calls_start_after_first_ends': all(r['second_start_minus_first_end_seconds'] >= 0 for r in records),
        'median_gap_seconds': statistics.median(r['second_start_minus_first_end_seconds'] for r in records),
        'weighted_total_tokens': total,
        'weighted_input_tokens': prompt,
        'hypothetical_one_of_two_prompts_fully_cached_tokens': total - prompt / 2,
        'hypothetical_relative_reduction': prompt / (2 * total),
        'full_input_share': prompt / total,
    }
args.output.write_text(json.dumps(result, indent=2) + '\n')
