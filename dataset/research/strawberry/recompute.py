"""Recompute the original 1000-call strawberry experiment without making API calls.

Dependencies: pyarrow, tiktoken. Source notebooks are parsed as text, never executed.
python3 -B recompute.py --sources /path/to/sources --models /path/to/models.csv \
  --config /path/to/config.json --output /path/to/new.json
"""
import argparse
import ast
from collections import Counter
import csv
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import importlib.metadata
import json
from pathlib import Path
import re

import pyarrow.parquet as pq
import tiktoken


def count_answer(response):
    """Audit this fixed source's explicit final counts, not general response grading."""
    s = re.sub(r'[*_`{}\\]', '', response.lower())
    s = s.translate(str.maketrans({'“': '"', '”': '"', '‘': "'", '’': "'"}))
    patterns = [
        ('final_answer', r'final answer\s*[:—-]\s*(three|two|four|3|2|4)\b'),
        ('leading_answer', r'^\s*(three|two|four|3|2|4)\b'),
        ('explicit_total', r'(?:total(?:ing|ling)?(?: of)?|count is)\s*[:=]?\s*(three|two|four|3|2|4)\b'),
        ('total_appearances', r'total appearances of [\"\']r[\"\']\s*:\s*(three|two|four|3|2|4)\b'),
        ('count_phrase', r'\b(three|two|four|3|2|4)\s+(?:times?\b|occurrences?\b|instances?\b|letters?\s+[\"\']?r\b|[\"\']?r(?:[\"\']?s)?\b)'),
    ]
    for rule, pattern in patterns:
        found = re.findall(pattern, s)
        if found:
            v = found[-1]
            return (int(v) if v.isdigit() else {'two': 2, 'three': 3, 'four': 4}[v]), rule
    if re.search(r'\b(?:appears?|occurs?)\s+twice\b', s):
        return 2, 'twice'
    raise ValueError('No explicit count recovered from response: ' + repr(response))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sources', required=True, type=Path)
    p.add_argument('--models', required=True, type=Path)
    p.add_argument('--config', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    a = p.parse_args()
    src, out = a.sources.resolve(), a.output.resolve()
    if out.exists() or out == src or src in out.parents or out in [a.models.resolve(), a.config.resolve()]:
        p.error('output must be new and outside source evidence and input files')
    config = json.loads(a.config.read_text())
    models = {r['model_id']: r for r in csv.DictReader(a.models.open(newline=''))}
    notebook = json.loads((src / 'letter-count.ipynb').read_text())
    endpoint_map = None
    trials = None
    for cell in notebook['cells']:
        if cell['cell_type'] != 'code':
            continue
        text = ''.join(cell['source'])
        # Only parse two safe literal assignments; never import or run notebook code.
        if 'model_list = [' in text:
            node = next(x for x in ast.parse(text).body if isinstance(x, ast.Assign))
            endpoint_map = {k: v for item in ast.literal_eval(node.value) for k, v in item.items()}
        if 'num_trials = ' in text:
            for node in ast.parse(text).body:
                if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'num_trials' for t in node.targets):
                    trials = ast.literal_eval(node.value)
    assert trials == 100 and endpoint_map and len(endpoint_map) == 10
    rows = pq.read_table(src / 'strawberry.parquet').to_pylist()
    assert len(rows) == 1000 and set(r['model'] for r in rows) == set(endpoint_map)
    assert set(config['models']) == set(endpoint_map)
    assert len({(r['model'], r['created']) for r in rows}) == len(rows)
    assert len({json.dumps(r, sort_keys=True) for r in rows}) == len(rows)
    enc = tiktoken.get_encoding('o200k_harmony')
    audits = []
    for i, r in enumerate(rows):
        assert isinstance(r['prompt_tokens'], int) and r['prompt_tokens'] > 0
        assert isinstance(r['completion_tokens'], int) and r['completion_tokens'] > 0
        assert isinstance(r['response'], str) and r['response']
        count, rule = count_answer(r['response'])
        assert count == r['count_letters'] and (count == 3) == r['correct'], (i, r['model'])
        item = {'source_row': i, 'model': r['model'], 'created': r['created'],
                'response_sha256': hashlib.sha256(r['response'].encode()).hexdigest(),
                'prompt_tokens': r['prompt_tokens'], 'completion_tokens': r['completion_tokens'],
                'answer': count, 'audit_rule': rule, 'correct': count == 3}
        if r['model'].startswith('gpt-oss'):
            item['harmony_retokenized_visible_content'] = len(enc.encode(r['response']))
            item['harmony_retokenized_reasoning'] = len(enc.encode(r['reasoning'] or ''))
            item['native_completion_minus_retokenized_text'] = (r['completion_tokens']
                - item['harmony_retokenized_visible_content'] - item['harmony_retokenized_reasoning'])
        if count != 3:
            item['incorrect_response'] = r['response']
        audits.append(item)
    summaries = []
    for label in sorted(endpoint_map):
        group = [r for r in rows if r['model'] == label]
        assert len(group) == trials
        model_config = config['models'][label]
        model = models[model_config['model_id']]
        P = Decimal(model['active_parameters'])
        coeff = Decimal(model['flops_per_token'])
        assert coeff == 2 * P
        n = Decimal(len(group))
        prompt = sum(r['prompt_tokens'] for r in group)
        completion = sum(r['completion_tokens'] for r in group)
        mean_tokens = Decimal(prompt + completion) / n
        mean_flops = coeff * mean_tokens
        counts = Counter(r['prompt_tokens'] for r in group)
        summary = {
            'point_id': model_config['point_id'], 'model_id': model_config['model_id'],
            'source_model': label, 'requested_endpoint': endpoint_map[label],
            'calls': len(group), 'correct': sum(r['correct'] for r in group),
            'answer_counts': dict(sorted(Counter(r['count_letters'] for r in group).items())),
            'prompt_token_counts': dict(sorted(counts.items())),
            'total_prompt_tokens': prompt, 'total_completion_tokens': completion,
            'mean_prompt_tokens': str(Decimal(prompt) / n),
            'mean_completion_tokens': str(Decimal(completion) / n),
            'tokens': str(mean_tokens), 'compute_flops': str(mean_flops),
            'returned_reasoning_calls': sum(bool(r['reasoning']) for r in group),
            'first_call_utc': datetime.fromtimestamp(min(r['created'] for r in group), timezone.utc).isoformat(),
            'last_call_utc': datetime.fromtimestamp(max(r['created'] for r in group), timezone.utc).isoformat(),
            'human_seconds': config['human_seconds'], 'human_scenario_seconds': config['human_scenario_seconds'],
            'all_prompt_cache_reads_sensitivity_flops': str(coeff * Decimal(completion) / n),
            'parameter_scenario_flops': {str(v): str(2 * Decimal(str(v)) * mean_tokens)
                                         for v in model_config['parameter_scenario_active']},
        }
        if label.startswith('gpt-oss'):
            summary['harmony_framing_difference_counts'] = dict(sorted(Counter(
                r['native_completion_minus_retokenized_text'] for r in audits if r['model'] == label).items()))
        summaries.append(summary)
    result = {
        'question': 'How many times does the letter r appear in strawberry',
        'correct_count': 'strawberry'.count('r'),
        'source_sha256': {name: sha(src / name) for name in ['strawberry.parquet', 'letter-count.ipynb', 'fix-false-negatives.ipynb']},
        'model_inputs_sha256': sha(a.models), 'config_sha256': sha(a.config),
        'dependencies': {name: importlib.metadata.version(name) for name in ['pyarrow', 'tiktoken']},
        'native_rows': len(rows), 'duplicate_keys': 0, 'grade_disagreements': 0,
        'models': summaries, 'row_audit': audits,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(summaries, indent=2))


if __name__ == '__main__':
    main()
