"""Reconstruct the observed CUPS completion cohort without running Copilot.

Dependency: tiktoken. --sources holds retained original code and vocabularies;
--logs is the JSON from extract_logs.py; --models is the frozen model CSV;
--output must be new and outside the evidence directories. No network access.
"""
import argparse
import base64
from collections import Counter, defaultdict
import csv
from datetime import datetime
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re
from statistics import median, mean

import tiktoken


PATTERN = r"'s|'t|'re|'ve|'m|'ll|'d| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"
MODEL_ID = 'github-copilot-2022-08'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def encoding(src):
    vocab = json.loads((src / 'historical-client/copilot/dist/tokenizer.json').read_text())
    byte_values = list(range(33, 127)) + list(range(161, 173)) + list(range(174, 256))
    characters = byte_values[:]
    for n in range(256):
        if n not in byte_values:
            byte_values.append(n)
            characters.append(256 + len(characters) - 188)
    # Standard byte-to-Unicode map used in original client module 94.
    inverse = {chr(character): byte for byte, character in zip(byte_values, characters)}
    ranks = {bytes(inverse[c] for c in word): rank for word, rank in vocab.items()
             if word != '<|endoftext|>'}
    reference = {base64.b64decode(token): int(rank) for token, rank in
                 (line.split() for line in (src / 'p50k_base.tiktoken').read_bytes().splitlines())}
    assert ranks == reference, 'Historical tokenizer must equal retained p50k vocabulary.'
    return tiktoken.Encoding(name='copilot-aug2022-original', pat_str=PATTERN,
                             mergeable_ranks=ranks, special_tokens={'<|endoftext|>': 50256})


def decode(value):
    if value == '':
        return ''
    result = json.loads(value)
    assert isinstance(result, str)
    return result


def grouped_choices(events, tolerance=10):
    by_signature = defaultdict(list)
    for r in events:
        m = r['Measurements']
        key = (r['session_index'], r['CurrentPrompt'], r['CurrentSuggestion'],
               m['numTokens'], m.get('meanLogProb'), m.get('meanAlternativeLogProb'))
        by_signature[key].append(r)
    groups = []
    for rows in by_signature.values():
        clusters = []
        for row in sorted(rows, key=lambda r: r['issued_ms']):
            if not clusters or row['issued_ms'] - clusters[-1][0]['issued_ms'] > tolerance:
                clusters.append([row])
            else:
                clusters[-1].append(row)
        groups.extend(clusters)
    result = []
    for group in groups:
        rows = sorted(group, key=lambda r: r['event_index'])
        first = rows[0]
        prompt_char_counts = {r['Measurements']['promptCharLen'] for r in rows}
        assert len(prompt_char_counts) == 1
        result.append({'session': first['session_index'], 'first_event': first['event_index'],
                       'first_state': first['StateName'], 'issued_ms': median(r['issued_ms'] for r in rows),
                       'issued_jitter_ms': max(r['issued_ms'] for r in rows) - min(r['issued_ms'] for r in rows),
                       'event_indices': [r['event_index'] for r in rows],
                       'prompt': first['prompt'], 'suggestion': first['suggestion'],
                       'prompt_chars_native': first['Measurements']['promptCharLen'],
                       'output_tokens_native': first['Measurements']['numTokens'],
                       'input_tokens_text': first['input_tokens_text'],
                       'output_tokens_text': first['output_tokens_text'],
                       'reported_lines': max(r['Measurements']['numLines'] for r in rows),
                       'accepted_events': sum(r['StateName'] == 'Accepted' for r in rows),
                       'accepted_event_indices': [r['event_index'] for r in rows if r['StateName'] == 'Accepted'],
                       'rejected_events': sum(r['StateName'] == 'Rejected' for r in rows),
                       'task': first['Task']})
    return sorted(result, key=lambda g: (g['session'], g['issued_ms'], g['first_event']))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['sources', 'logs', 'models', 'output']:
        p.add_argument('--' + name, required=True, type=Path)
    args = p.parse_args()
    src, logs_path, models_path, out = [getattr(args, n).resolve() for n in ['sources', 'logs', 'models', 'output']]
    if out.exists() or src in out.parents or out == src or out in [logs_path, models_path]:
        p.error('output must be new and outside source evidence and input files')
    logs = json.loads(logs_path.read_text())
    assert logs['original_pickle_sha256'] == sha(src / 'data_labeled_study.pkl')
    enc = encoding(src)
    events = []
    for si, session in enumerate(logs['sessions']):
        for ei, original in enumerate(session):
            assert original['session_index'] == si and original['event_index'] == ei
            r = dict(original)
            r['prompt'], r['suggestion'] = decode(r['CurrentPrompt']), decode(r['CurrentSuggestion'])
            r['input_tokens_text'] = len(enc.encode(r['prompt']))
            r['output_tokens_text'] = len(enc.encode(r['suggestion']))
            timestamp = datetime.fromisoformat(r['TimeGenerated'].replace('Z', '+00:00'))
            r['issued_ms'] = round(timestamp.timestamp() * 1000 - r['Measurements']['timeSinceIssuedMs'])
            events.append(r)
    assert len(logs['sessions']) == 21 and len(events) == 3490
    choices = grouped_choices(events)
    assert len(choices) == 1023
    # Identical native issuance clock and prompt length identify same-request alternatives.
    requests = []
    for choice in choices:
        if (requests and choice['session'] == requests[-1]['session'] and
                abs(choice['issued_ms'] - requests[-1]['issued_ms']) <= 10 and
                choice['prompt_chars_native'] == requests[-1]['prompt_chars_native']):
            requests[-1]['choices'].append(choice)
        else:
            requests.append({'session': choice['session'], 'issued_ms': choice['issued_ms'],
                             'prompt_chars_native': choice['prompt_chars_native'], 'choices': [choice]})

    for choice in choices:
        if choice['prompt']:
            choice['input_tokens_estimated'] = choice['input_tokens_text'] * choice['prompt_chars_native'] / len(choice['prompt'])
            choice['input_method'] = 'native_characters_times_own_retained_prompt_density'
            choice['density_donor'] = [choice['session'], choice['first_event']]
        else:
            donors = [g for g in choices if g['session'] == choice['session'] and g['prompt']]
            donor = min(donors, key=lambda g: abs(g['issued_ms'] - choice['issued_ms']))
            choice['input_tokens_estimated'] = donor['input_tokens_text'] / len(donor['prompt']) * choice['prompt_chars_native']
            choice['input_method'] = 'native_characters_times_nearest_same_session_prompt_density'
            choice['density_donor'] = [donor['session'], donor['first_event']]
        choice['output_tokens_estimated'] = (choice['output_tokens_native'] if choice['output_tokens_native'] > 0
                                              else max(1, choice['output_tokens_text']))
        choice['output_method'] = 'native_logprob_count' if choice['output_tokens_native'] > 0 else 'visible_text_tokenization'

    for request in requests:
        observed = request['choices']
        # The original archive maps session 16 to code_20.cpp and 17 to code_21.js;
        # all other sessions use Python. C++ is not in the client's parsing list.
        language = 'cpp' if request['session'] == 16 else 'javascript' if request['session'] == 17 else 'python'
        block_start = any(re.search(r'[:{]\s*$', c['prompt']) for c in observed)
        multiline = any(c['reported_lines'] > 1 for c in observed) or block_start
        expected_n = 1 if language == 'cpp' else 3 if multiline else 1
        expected_n = max(expected_n, len(observed))
        input_per = mean(c['input_tokens_estimated'] for c in observed)
        output_per = mean(c['output_tokens_estimated'] for c in observed)
        raw_input_per = mean(c['input_tokens_text'] if c['prompt'] else c['input_tokens_estimated'] for c in observed)
        request.update(language=language, multiline_inferred=multiline, generated_candidates_estimated=expected_n,
                       observed_choices=len(observed), hidden_candidates_estimated=expected_n-len(observed),
                       input_tokens_estimated=expected_n * input_per,
                       output_tokens_estimated=expected_n * (output_per + 1),
                       input_tokens_raw_text_scenario=expected_n * raw_input_per,
                       input_tokens_shared_prefix_scenario=input_per,
                       observed_choices_only_tokens=len(observed) * (input_per + output_per + 1),
                       three_candidates_every_request_tokens=max(3, len(observed)) * (input_per + output_per + 1))

    model_rows = list(csv.DictReader(models_path.open(newline='')))
    model = next(r for r in model_rows if r['model_id'] == MODEL_ID)
    coefficient = Decimal(model['flops_per_token'])
    assert coefficient == 2 * Decimal(model['active_parameters'])
    acceptance_events = [r for r in events if r['StateName'] == 'Accepted']
    event_by_key = {(r['session_index'], r['event_index']): r for r in events}
    accepted = [event_by_key[(c['session'], c['accepted_event_indices'][0])]
                for c in choices if c['accepted_event_indices']]
    denominator = len(accepted)
    assert len(acceptance_events) == 386 and denominator == 382
    input_total = sum(Decimal(str(r['input_tokens_estimated'])) for r in requests)
    output_total = sum(Decimal(str(r['output_tokens_estimated'])) for r in requests)
    token_total = input_total + output_total
    # The historical telemetry confidence/quantile functions evaluate a small
    # linear score twice per display. A conservative 100 scalar operations per
    # visible display contributes <10^-9 of the dominant model work.
    displays = sum(r['StateName'] in ['Shown', 'Replay', 'Browsing'] for r in events)
    helper_operations = 100 * displays
    total_flops = coefficient * token_total + helper_operations
    def scenario(tokens):
        return str((coefficient * Decimal(str(tokens)) + helper_operations) / denominator)
    summary = {
        'point_id': 'code-copilot-cups-accepted-completion-2022',
        'session_count': 21, 'event_count': len(events), 'native_states': dict(Counter(r['StateName'] for r in events)),
        'choice_count': len(choices), 'request_count': len(requests),
        'dedup_choice_counts_by_clock_tolerance_ms': {str(t): len(grouped_choices(events, t)) for t in [1, 2, 5, 10, 25]},
        'max_clock_jitter_ms': max(c['issued_jitter_ms'] for c in choices),
        'first_observed_choice_states': dict(Counter(c['first_state'] for c in choices)),
        'missing_prompt_choices': sum(not c['prompt'] for c in choices),
        'zero_native_token_choices': sum(c['output_tokens_native'] == 0 for c in choices),
        'prompt_text_native_char_mismatch_choices': sum(c['prompt'] != '' and len(c['prompt']) != c['prompt_chars_native'] for c in choices),
        'generated_candidates_estimated': sum(r['generated_candidates_estimated'] for r in requests),
        'hidden_candidates_estimated': sum(r['hidden_candidates_estimated'] for r in requests),
        'multiline_requests_inferred': sum(r['multiline_inferred'] for r in requests),
        'accepted_events': len(acceptance_events),
        'normalization': 'distinct generated choices accepted at least once',
        'accepted_distinct_choices': sum(c['accepted_events'] > 0 for c in choices),
        'accepted_mean_characters': mean(len(r['suggestion']) for r in accepted),
        'accepted_mean_reported_lines': mean(r['Measurements']['numLines'] for r in accepted),
        'accepted_at_most_20_characters': sum(len(r['suggestion']) <= 20 for r in accepted),
        'accepted_multiline_texts': sum('\n' in r['suggestion'] for r in accepted),
        'task_accept_counts': dict(Counter(r['Task'] for r in accepted)),
        'input_tokens_total_estimated': str(input_total), 'output_tokens_total_estimated': str(output_total),
        'tokens_per_accepted_estimated': str(token_total / denominator),
        'helper_operations_estimated': helper_operations,
        'total_flops_estimated': str(total_flops), 'flops_per_accepted_estimated': str(total_flops / denominator),
        'human_seconds_estimated': 20, 'human_seconds_scenarios': [8, 60],
        'scenarios_flops_per_accepted': {
            'per_acceptance_event_instead_of_distinct_choice': str(total_flops / len(acceptance_events)),
            'observed_choices_only': scenario(sum(r['observed_choices_only_tokens'] for r in requests)),
            'shared_prompt_across_same_request_candidates': scenario(sum(r['input_tokens_shared_prefix_scenario'] + r['output_tokens_estimated'] for r in requests)),
            'raw_logged_prompt_text_without_native_length_alignment': scenario(sum(r['input_tokens_raw_text_scenario'] + r['output_tokens_estimated'] for r in requests)),
            'three_candidates_every_request': scenario(sum(r['three_candidates_every_request_tokens'] for r in requests)),
            'active_parameters_4B': str(((Decimal(8000000000) * token_total) + helper_operations) / denominator),
            'active_parameters_24B': str(((Decimal(48000000000) * token_total) + helper_operations) / denominator),
        },
    }
    result = {'source_sha256': {'pickle': sha(src / 'data_labeled_study.pkl'), 'extracted_logs': sha(logs_path),
                               'historical_agent': sha(src / 'copilot-agent-aug2022.js'),
                               'historical_tokenizer': sha(src / 'historical-client/copilot/dist/tokenizer.json'),
                               'models': sha(models_path)},
              'summary': summary, 'requests': requests,
              'accepted_output_records': [{'session': r['session_index'], 'event': r['event_index'],
                                           'prompt': r['prompt'], 'suggestion': r['suggestion'], 'task': r['Task']}
                                          for r in accepted],
              'native_acceptance_event_records': [{'session': r['session_index'], 'event': r['event_index'],
                                                   'suggestion': r['suggestion']}
                                                  for r in acceptance_events]}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
