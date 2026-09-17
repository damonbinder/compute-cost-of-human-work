"""Recompute the matched ARC observation from retained original sources.

Usage: python3 -B recompute.py /path/to/sources [--output-dir /path/to/research]
Uses only the Python standard library; no network or production writes.
"""
import argparse
import ast
import collections
import csv
import json
from pathlib import Path
import re
import statistics

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('sources', type=Path)
parser.add_argument('--folder',required=True)
parser.add_argument('--model',required=True)
parser.add_argument('--output-dir', type=Path, required=True)
args = parser.parse_args()
s = args.sources
with (s / 'human-attempts.csv').open(newline='') as f:
    humans = list(csv.DictReader(f))
out = []
mismatches = []
coverage = collections.Counter()
for file in sorted((s / args.folder).glob('*.json')):
    if not re.fullmatch(r'[0-9a-f]{8}', file.stem):
        continue
    coverage['task_files'] += 1
    puzzle = json.loads((s / 'tasks' / file.name).read_text())
    pairs = collections.defaultdict(list)
    for array_index, row in enumerate(json.loads(file.read_text())):
        coverage['array_entries'] += 1
        for slot, response in row.items():
            assert slot in {'attempt_1', 'attempt_2'}
            if response is None:
                coverage['null_slots'] += 1
                continue
            coverage['retained_responses'] += 1
            meta = response['metadata']
            ix = int(meta['pair_index'])
            assert meta['task_id'] == file.stem
            assert meta['model'] == args.model
            if ix != array_index:
                mismatches.append([file.stem, array_index, slot, ix])
            assert len(meta['choices']) == 2
            assert meta['choices'][0]['message']['role'] == 'user'
            assert meta['choices'][1]['message']['role'] == 'assistant'
            prompt = meta['choices'][0]['message']['content']
            assert '--Test Input--' in prompt and '--End of Test Input--' in prompt
            tail = prompt.split('--Test Input--')[-1].split('--End of Test Input--')[0].strip()
            assert ast.literal_eval(tail) == puzzle['test'][ix]['input'], (file.name, ix)
            training = prompt.split('--Training Examples--')[1].split('--End of Training Examples--')[0]
            examples = re.findall(r'--Example \d+--\s*INPUT:\s*(.*?)\s*OUTPUT:\s*(.*?)(?=--Example|$)',training,re.S)
            assert len(examples) == len(puzzle['train'])
            for (inp,ans),expected in zip(examples,puzzle['train']):
                assert ast.literal_eval(inp.strip()) == expected['input']
                assert ast.literal_eval(ans.strip()) == expected['output']
            computed_correct = response['answer'] == puzzle['test'][ix]['output']
            if response['correct'] is None:
                coverage['unscored_native_responses'] += 1
            else:
                assert computed_correct == response['correct']
            response['recomputed_correct'] = computed_correct
            usage = meta['usage']
            reasoning = (usage.get('completion_tokens_details') or {}).get('reasoning_tokens',0) or 0
            assert reasoning >= 0
            if meta['provider'] == 'gemini':
                assert usage['total_tokens'] == usage['prompt_tokens'] + usage['completion_tokens'] + reasoning
            else:
                assert usage['total_tokens'] == usage['prompt_tokens'] + usage['completion_tokens']
                assert reasoning <= usage['completion_tokens']
            pairs[ix].append((slot, response))
    for ix, calls in pairs.items():
        assert len(calls) <= 2 and len(calls) == len({x[0] for x in calls})
        complete = len(calls) == 2 and {x[0] for x in calls} == {'attempt_1', 'attempt_2'}
        if complete:
            assert calls[0][1]['metadata']['choices'][0] == calls[1][1]['metadata']['choices'][0]
            assert calls[0][1]['metadata']['start_timestamp'] != calls[1][1]['metadata']['start_timestamp']
        all_h = [r for r in humans if r['task_set'] == 'Public Eval'
                 and r['task_ID'] == file.stem and int(r['test_index']) == ix]
        hs = [r for r in all_h if float(r['duration_seconds']) > 5]
        def usage_sum(field):
            return sum(a['metadata']['usage'][field] for _, a in calls)
        out.append({
            'task_id': file.stem, 'test_index': ix, 'calls': len(calls),
            'slots': [x[0] for x in calls], 'complete_two': complete,
            'tokens': usage_sum('total_tokens'), 'input_tokens': usage_sum('prompt_tokens'),
            'completion_tokens': usage_sum('completion_tokens'),
            'reported_reasoning_tokens': sum(((a['metadata']['usage'].get('completion_tokens_details') or {}).get('reasoning_tokens') or 0) for _, a in calls),
            'ai_correct': any(a['recomputed_correct'] for _, a in calls),
            'human_n': len(hs),
            'human_mean': statistics.mean(float(r['duration_seconds']) for r in hs) if hs else None,
            'human_success': statistics.mean(int(r['correct_submissions']) > 0 for r in hs) if hs else None,
            'human_seconds_sum': sum(float(r['duration_seconds']) for r in hs),
            'human_correct_n': sum(int(r['correct_submissions']) > 0 for r in hs),
            'excluded_human_views_at_most_5_seconds': len(all_h) - len(hs),
        })
selected = [r for r in out if r['complete_two'] and r['human_n']]
n = sum(r['human_n'] for r in selected)
assert n > 0
summary = {
    'human_minimum_duration_exclusive_seconds': 5,
    'selected_pairs': len(selected), 'human_attempts': n,
    'selected_retained_responses': sum(r['calls'] for r in selected),
    'tokens': sum(r['tokens'] * r['human_n'] for r in selected) / n,
    'input_tokens': sum(r['input_tokens'] * r['human_n'] for r in selected) / n,
    'completion_tokens': sum(r['completion_tokens'] * r['human_n'] for r in selected) / n,
    'reported_reasoning_tokens': sum(r['reported_reasoning_tokens'] * r['human_n'] for r in selected) / n,
    'human_time': sum(r['human_seconds_sum'] for r in selected) / n,
    'ai_success': sum(r['ai_correct'] * r['human_n'] for r in selected) / n,
    'human_success': sum(r['human_correct_n'] for r in selected) / n,
    'weighted_ai_correct_n': sum(r['ai_correct'] * r['human_n'] for r in selected),
    'human_correct_n': sum(r['human_correct_n'] for r in selected),
    'excluded_human_views_at_most_5_seconds': sum(r['excluded_human_views_at_most_5_seconds'] for r in selected),
    'index_mismatches': mismatches, 'source_correct_mismatches': [],
    'source_coverage': dict(coverage),
}
args.output_dir.mkdir(parents=True, exist_ok=True)
for name, value in [('verified-pairs.json', out), ('summary.json', summary)]:
    (args.output_dir / name).write_text(json.dumps(value, indent=2) + '\n')
print(json.dumps(summary, indent=2))
