"""Recompute the eight Lyptus cyber points from retained original logs.

Python 3 standard library only. No challenge code is executed.
Usage: python3 -B recompute.py --sources SOURCE_DIR --selection SELECTION_JSON
       --models MODELS_CSV --output NEW_OUTPUT_JSON
"""
import argparse
import collections
import copy
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path
import statistics
import zipfile


def digest(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def human_log(path):
    with zipfile.ZipFile(io.BytesIO(gzip.decompress(path.read_bytes()))) as z:
        names = [n for n in z.namelist() if n.startswith('samples/')]
        assert len(names) == 1
        sample = json.loads(z.read(names[0]))
    intervals = []
    for name, text in sample['store'].get('HumanAgentState:logs', {}).items():
        if name.endswith('.timing'):
            intervals.extend(float(line.split()[1]) for line in text.splitlines()
                             if line[:2] in ('I ', 'O '))
    return {'task_id': sample['id'],
            'client_clock_seconds': sample['store']['HumanAgentState:accumulated_time'],
            'recorded_total_seconds': sample.get('total_time'),
            'io_trace_span_seconds': sum(intervals),
            'largest_io_gap_seconds': max(intervals, default=0),
            'input': sample['input']}


def sample_identity_hash(sample):
    """Retry archives may omit the initial journal's temporary sandbox path."""
    value = copy.deepcopy(sample)
    for event in value.get('events', []):
        if isinstance(event.get('sample'), dict):
            event['sample'].pop('sandbox', None)
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def native_usage(sample, model):
    events = [e for e in sample['events'] if e.get('event') == 'model']
    assert events and not sample.get('error') and not sample.get('error_retries')
    assert not any(e.get('event') in ('error', 'retry') for e in sample['events'])
    totals = collections.Counter()
    normalized = collections.Counter()
    calls = []
    rejected_calls = []
    for e in events:
        assert e['model'] == model
        if e.get('error'):
            # This tranche has one explicit Vertex capacity rejection, with no
            # generated content or usage. Do not invent a completed generation.
            assert '429 RESOURCE_EXHAUSTED' in e.get('traceback', '')
            assert not e.get('output', {}).get('usage')
            assert e['output'].get('completion') == ''
            rejected_calls.append({'event_uuid': e['uuid'], 'error': e['error'],
                                   'classification': '429 RESOURCE_EXHAUSTED',
                                   'counted_generation_tokens': 0,
                                   'basis': 'Explicit capacity rejection; no returned generation or usage.'})
            continue
        out = e['output']['usage']
        normalized.update({k: v for k, v in out.items() if isinstance(v, (int, float))})
        response = e['call']['response']
        if model.startswith('anthropic/'):
            u = response['usage']
            fresh = u['input_tokens']
            creation = u.get('cache_creation_input_tokens', 0)
            reads = u.get('cache_read_input_tokens', 0)
            output = u['output_tokens']  # includes thinking tokens
            prompt = fresh + creation + reads
            reasoning = out.get('reasoning_tokens', 0)
            assert out['input_tokens'] == fresh and out['output_tokens'] == output
        elif model.startswith('openai/'):
            u = response['usage']
            prompt = u['prompt_tokens']
            reads = u.get('prompt_tokens_details', {}).get('cached_tokens', 0)
            fresh = prompt - reads
            creation = 0  # not separately reported; newly processed prompt is included
            output = u['completion_tokens']  # includes reasoning tokens
            reasoning = u.get('completion_tokens_details', {}).get('reasoning_tokens', 0)
            assert out['input_tokens'] == prompt and out['output_tokens'] == output
        elif model.startswith('google/'):
            u = response['usageMetadata']
            prompt = u['promptTokenCount']
            reads = u.get('cachedContentTokenCount', 0)
            fresh = prompt - reads
            creation = 0  # implicit cache creation is part of the noncached prompt
            reasoning = u.get('thoughtsTokenCount', 0)
            output = u.get('candidatesTokenCount', 0) + reasoning
            assert prompt + output == u['totalTokenCount']
            assert out['input_tokens'] == prompt
            assert out['output_tokens'] + out.get('reasoning_tokens', 0) == output
        else:
            raise ValueError('Unsupported provider: ' + model)
        assert fresh >= 0 and prompt + output == out['total_tokens']
        row = {'input_fresh': fresh, 'cache_creation': creation, 'cache_read': reads,
               'output_including_reasoning': output, 'reasoning_subset': reasoning,
               'full_prefix_tokens': prompt + output,
               'counted_tokens': fresh + creation + output}
        totals.update(row)
        calls.append({'event_uuid': e['uuid'], 'raw_usage': u, **row})
    assert set(sample['model_usage']) == {model}
    for k, value in sample['model_usage'][model].items():
        if isinstance(value, (int, float)):
            assert normalized[k] == value, (sample['id'], k, normalized[k], value)
    return {'model_events': len(events), 'normalized_usage': sample['model_usage'][model],
            'raw_totals': dict(totals), 'calls': calls,
            'rejected_calls': rejected_calls,
            'api_errors_or_retries': len(rejected_calls)}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for flag in ('sources', 'selection', 'models', 'output'):
        p.add_argument('--' + flag, type=Path, required=True)
    a = p.parse_args()
    a.sources, a.output = a.sources.resolve(), a.output.resolve()
    if a.output.exists() or a.output == a.sources or a.sources in a.output.parents:
        p.error('Choose a new output file outside the evidence directory.')
    selection = json.loads(a.selection.read_text())
    models = {r['model_id']: r for r in csv.DictReader(a.models.open(newline=''))}
    manifest = {r['file']: r for r in json.loads((a.sources/'manifest.json').read_text())
                if 'sha256' in r}
    verified = {}
    def verify(name):
        if name not in verified:
            path = a.sources/name
            assert path.is_file() and digest(path) == manifest[name]['sha256'], name
            verified[name] = manifest[name]['sha256']
        return a.sources/name
    snapshot = json.loads(verify('data/human/human_snapshot.json').read_text())
    points = []
    for item in selection:
        model = models[item['model_id']]
        coefficient = float(model['flops_per_token'])
        assert coefficient == 2*float(model['active_parameters'])
        hs = [r for r in snapshot['completions'] if r['task_id'] == item['source_task_id']]
        assert sorted(r['session_id'] for r in hs) == sorted(item['human_sessions'])
        assert not any(r['task_id'] == item['source_task_id'] for r in snapshot['censored'])
        humans = []
        for h in hs:
            record = {'session_id': h['session_id'], 'expert_id': h['user_id'],
                      'score': h['score'], 'source_pass': h['score_binarized'],
                      'seconds': h['client_active_seconds'],
                      'server_seconds': h['server_elapsed_seconds']}
            if h['session_id'] in item['human_logs']:
                name = item['human_logs'][h['session_id']]
                log = human_log(verify(name))
                assert log['task_id'] == item['source_task_id']
                assert abs(log['client_clock_seconds'] - record['seconds']) < 1e-6
                record.update({'source': name, **log})
            humans.append(record)
        unique = {}
        for name in item['ai_logs']:
            with zipfile.ZipFile(verify(name)) as z:
                header = json.loads(z.read('header.json'))
                assert header['eval']['model'] == item['native_model']
                member = 'samples/' + item['native_task_id'] + '_epoch_1.json'
                raw = z.read(member)
                sample = json.loads(raw)
                uid = sample['uuid']
                sample_hash = hashlib.sha256(raw).hexdigest()
                identity_hash = sample_identity_hash(sample)
                if uid in unique:
                    assert unique[uid]['identity_sha256'] == identity_hash
                    unique[uid]['archive_copies'].append(name)
                    unique[uid]['archive_sample_sha256'].append(sample_hash)
                    continue
                unique[uid] = {'sample_uuid': uid, 'sample_sha256': sample_hash,
                               'identity_sha256': identity_hash,
                               'archive_sample_sha256': [sample_hash],
                               'archive_copies': [name], 'member': member,
                               'input': sample['input'], 'scores': sample['scores'],
                               'config': header['eval']['task_args'],
                               'packages': header['eval'].get('packages'),
                               'total_time_seconds': sample.get('total_time'),
                               'working_time_seconds': sample.get('working_time'),
                               **native_usage(sample, item['native_model'])}
        runs = list(unique.values())
        assert len(runs) == 1, 'Initial tranche specifies one unique source run per point.'
        tokens = statistics.mean(r['raw_totals']['counted_tokens'] for r in runs)
        full = statistics.mean(r['raw_totals']['full_prefix_tokens'] for r in runs)
        points.append({'point_id': item['point_id'], 'source_task_id': item['source_task_id'],
                       'model_id': item['model_id'], 'flops_per_token': coefficient,
                       'human_time_seconds': statistics.mean(r['seconds'] for r in humans),
                       'human_attempts': len(humans), 'humans': humans,
                       'ai_attempts': len(runs), 'runs': runs, 'tokens': tokens,
                       'compute_flops': coefficient*tokens,
                       'full_prefix_tokens': full, 'full_prefix_flops': coefficient*full,
                       'parameter_factor_two_scenario_flops': [coefficient*tokens/2,
                                                               coefficient*tokens*2]})
    result = {'points': points, 'verified_source_sha256': verified,
              'selection_sha256': digest(a.selection), 'models_sha256': digest(a.models),
              'accounting': 'New input + cache creation + output; cached reads excluded. '
                            'Reasoning is included exactly once. Evaluation graders excluded.'}
    with a.output.open('x') as f:
        json.dump(result, f, indent=2)
        f.write('\n')
    print(json.dumps([{k: x[k] for k in ['point_id', 'human_time_seconds', 'tokens',
                                       'compute_flops', 'full_prefix_tokens']}
                      for x in points], indent=2))


if __name__ == '__main__':
    main()
