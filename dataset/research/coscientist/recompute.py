"""Rebuild retained Coscientist GPT-4 group estimates; Python 3 + tiktoken 0.14.0.

Usage: python recompute.py --input-dir PATH --output-json NEW_PATH
Inputs are immutable source CSVs, model-inputs.csv and inputs.json. No API calls.
cl100k_base data may download on first use; tiktoken verifies the encoding hash.
The output is a new JSON containing per-run/per-call audit data and group means.
"""
import argparse
import collections
import csv
import hashlib
import json
from pathlib import Path
import re
import statistics

import tiktoken


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input-dir', required=True, type=Path)
    ap.add_argument('--output-json', required=True, type=Path)
    args = ap.parse_args()
    if args.output_json.exists():
        raise FileExistsError('Choose a new output path; retained evidence is not overwritten.')
    config = json.loads((args.input_dir / 'inputs.json').read_text())
    with (args.input_dir / 'model-inputs.csv').open() as handle:
        model = next(csv.DictReader(handle))
    encoder = tiktoken.get_encoding(config['tokenizer'])
    count = lambda text: len(encoder.encode(text, disallowed_special=()))
    results = []
    for group in config['groups']:
        path = args.input_dir / group['file']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == group['sha256']
        with path.open() as handle:
            rows = list(csv.DictReader(handle))
        runs = collections.defaultdict(list)
        for row in rows:
            if row['model'] == 'gpt-4':
                runs[row['run_id']].append(row)
        audits = []
        for run_id, messages in runs.items():
            messages.sort(key=lambda x: int(x['message_id']))
            assert len(messages) == 42
            assert [int(x['message_id']) for x in messages] == list(range(42))
            assert [x['role'] for x in messages] == ['system', 'user'] + ['assistant', 'user'] * 20
            history_tokens = 0
            calls = []
            yields = []
            choices = []
            for index, message in enumerate(messages):
                content_tokens = count(message['message'])
                if message['role'] == 'assistant':
                    prompt = history_tokens + config['chat_reply_priming']
                    output = content_tokens + config['output_end_token']
                    processed = prompt + output
                    calls.append({'message_id': index, 'input_tokens': prompt,
                                  'output_tokens': output, 'processed': processed,
                                  'attention_position_pairs': processed * (processed + 1) / 2})
                    try:
                        choice = json.loads(message['message'])
                        choices.append(tuple(sorted((k, str(v)) for k, v in choice.items()
                                                    if k != 'your observation')))
                    except json.JSONDecodeError:
                        choices.append(('unparsed', message['message']))
                found = re.search(r'yield of this reaction is ([-\d.]+)%', message['message'])
                if message['role'] == 'user' and found:
                    yields.append(float(found.group(1)))
                history_tokens += content_tokens + count(message['role']) + config['chat_tokens_per_message']
            assert len(calls) == 20 and yields
            audits.append({'run_id': run_id, 'task': messages[1]['message'],
                           'calls': calls, 'valid_yield_responses': len(yields),
                           'yield_percentages': yields, 'best_yield_percent': max(yields),
                           'unique_choices': len(set(choices)),
                           'tokens': sum(c['processed'] for c in calls),
                           'attention_position_pairs': sum(c['attention_position_pairs'] for c in calls)})
        mean_tokens = statistics.mean(a['tokens'] for a in audits)
        mean_pairs = statistics.mean(a['attention_position_pairs'] for a in audits)
        context = mean_pairs / mean_tokens
        n = float(model['active_parameters'])
        layers, width = int(model['attention_layers']), float(model['attention_width'])
        flops = 2*n*mean_tokens + 4*layers*width*mean_pairs
        bounds = []
        for key in ('active_parameters_low', 'active_parameters_high'):
            bound = float(model[key])
            dense = max(8, round((bound / 196608)**(1/3)))
            bounds.append(2*bound*mean_tokens + 4*round(.65*dense)*(128*dense)*mean_pairs)
        results.append({'point_id': group['point_id'], 'source_file': group['file'],
                        'all_source_runs': len(set(r['run_id'] for r in rows)),
                        'included_gpt4_runs': len(audits), 'tokens': mean_tokens,
                        'compute_flops': flops, 'compute_flops_low': min(bounds),
                        'compute_flops_high': max(bounds), 'attention_context': context,
                        'attention_ratio': 2*layers*width*context/n,
                        'mean_best_yield_percent': statistics.mean(a['best_yield_percent'] for a in audits),
                        'mean_unique_choices': statistics.mean(a['unique_choices'] for a in audits),
                        'invalid_responses': sum(20-a['valid_yield_responses'] for a in audits),
                        'human_time': group['human_time_seconds'], 'runs': audits})
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(results, indent=2) + '\n')
    for row in results:
        print(json.dumps({k:v for k,v in row.items() if k != 'runs'}))


if __name__ == '__main__':
    main()
