"""Reconstruct four CyBench points from retained Lyptus native records.

Python 3.11+ standard library only. Does not execute challenge code.
python3 -B recompute.py --sources SOURCE_DIR --selection SELECTION_JSON \
    --models MODELS_CSV --output NEW_OUTPUT_JSON
The output must be new and outside the evidence directory.
"""
import argparse
import collections
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
    intervals = [float(line.split()[1])
                 for name, text in sample['store']['HumanAgentState:logs'].items()
                 if name.endswith('.timing') for line in text.splitlines()
                 if line[:2] in ('I ', 'O ')]
    return {'task_id': sample['id'],
            'client_clock_seconds': sample['store']['HumanAgentState:accumulated_time'],
            'recorded_total_seconds': sample.get('total_time'),
            'io_trace_span_seconds': sum(intervals),
            'largest_io_gap_seconds': max(intervals, default=0),
            'input': sample['input']}


def native_usage(sample, model):
    events = [e for e in sample['events'] if e.get('event') == 'model']
    assert events and not sample.get('error') and not sample.get('error_retries')
    assert not any(e.get('event') in ('error', 'retry') for e in sample['events'])
    totals, normalized, types = collections.Counter(), collections.Counter(), collections.Counter()
    calls, rejected = [], []
    def content_types(value):
        if isinstance(value, dict):
            if 'type' in value:
                types[str(value['type'])] += 1
            for v in value.values():
                content_types(v)
        elif isinstance(value, list):
            for v in value:
                content_types(v)
    content_types(sample['messages'])
    assert not any(k in types for k in ('image', 'image_url', 'audio', 'input_audio', 'video'))
    for e in events:
        assert e['model'] == model
        if e.get('error'):
            assert '429 RESOURCE_EXHAUSTED' in e.get('traceback', '')
            assert not e.get('output', {}).get('usage')
            assert e['output'].get('completion') == ''
            rejected.append({'event_uuid': e['uuid'], 'timestamp': e['timestamp'],
                             'error': e['error'], 'classification': '429 RESOURCE_EXHAUSTED',
                             'counted_generation_tokens': 0,
                             'basis': 'Explicit capacity rejection; no generation or usage returned.'})
            continue
        out = e['output']['usage']
        normalized.update({k: v for k, v in out.items() if isinstance(v, (int, float))})
        u = e['call']['response']['usageMetadata']
        prompt, reads = u['promptTokenCount'], u.get('cachedContentTokenCount', 0)
        visible, thoughts = u.get('candidatesTokenCount', 0), u.get('thoughtsTokenCount', 0)
        assert 0 <= reads <= prompt
        assert prompt + visible + thoughts == u['totalTokenCount'] == out['total_tokens']
        assert out['input_tokens'] == prompt and out['output_tokens'] == visible
        assert out.get('reasoning_tokens', 0) == thoughts
        row = {'prompt_including_cache': prompt, 'cache_read': reads,
               'input_fresh': prompt - reads, 'visible_output': visible,
               'reasoning_output': thoughts,
               'full_prefix_tokens': prompt + visible + thoughts,
               'counted_tokens': prompt - reads + visible + thoughts}
        totals.update(row)
        calls.append({'event_uuid': e['uuid'], 'raw_usage': u, **row})
    assert set(sample['model_usage']) == {model}
    for k, value in sample['model_usage'][model].items():
        if isinstance(value, (int, float)):
            assert normalized[k] == value, (sample['id'], k, normalized[k], value)
    return {'model_events': len(events), 'normalized_usage': sample['model_usage'][model],
            'raw_totals': dict(totals), 'calls': calls, 'rejected_calls': rejected,
            'message_content_types': dict(types),
            'tool_functions': sorted({e['function'] for e in sample['events'] if e['event'] == 'tool'})}


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
    manifest = {r['file']: r for r in json.loads((a.sources/'manifest.json').read_text())}
    verified = {}
    def verify(name):
        path = a.sources/name
        if name not in verified:
            assert path.is_file() and digest(path) == manifest[name]['sha256'], name
            verified[name] = manifest[name]['sha256']
        return path
    snapshot = json.loads(verify('data/human/human_snapshot.json').read_text())
    tasks = {t['task_id']: t for t in map(json.loads,
             verify('data/tasks/cybench/cybench_tasks.jsonl').read_text().splitlines())}
    corrections = verify('analysis/lib/corrections.py').read_text()
    assert '"glacier-exchange"' in corrections and 'session left open >1 day' in corrections
    points = []
    for item in selection:
        task = item['source_task_id']
        metadata = tasks[task]['dataset_task_metadata']
        truth = metadata['flag'].lower()
        model = models[item['model_id']]
        coefficient = float(model['flops_per_token'])
        assert coefficient == 2*float(model['active_parameters'])
        hs = [r for r in snapshot['completions'] if r['task_id'] == task]
        assert sorted(r['session_id'] for r in hs) == sorted(item['human_logs'])
        omitted_attempts = {key: [r for r in snapshot[key] if r['task_id'] == task]
                            for key in ('fails', 'censored')}
        assert not any(omitted_attempts.values())
        humans = []
        for h in hs:
            passes = [r for r in snapshot['passes'] if r['session_id'] == h['session_id']
                      and r['task_id'] == task]
            assert len(passes) == 1
            passed = passes[0]
            assert int(truth in passed['answer'].lower()) == passed['score_binarized'] == h['score_binarized']
            log = human_log(verify(item['human_logs'][h['session_id']]))
            assert log['task_id'] == task
            assert abs(log['client_clock_seconds'] - h['client_active_seconds']) < 1e-6
            humans.append({'session_id': h['session_id'], 'expert_id': h['user_id'],
                           'score': h['score'], 'source_pass': h['score_binarized'],
                           'submitted_answer': passed['answer'],
                           'seconds': h['client_active_seconds'],
                           'server_seconds': h['server_elapsed_seconds'], **log})
        with zipfile.ZipFile(verify(item['ai_log'])) as z:
            header = json.loads(z.read('header.json'))
            assert header['eval']['model'] == item['native_model']
            member = f'samples/{task}_epoch_1.json'
            raw = z.read(member)
            sample = json.loads(raw)
        assert sample['id'] == task
        score = sample['scores']['includes']['value']
        answer = sample['scores']['includes']['answer']
        assert (truth in answer.lower()) == (score == 'C')
        run = {'sample_uuid': sample['uuid'], 'sample_sha256': hashlib.sha256(raw).hexdigest(),
               'archive': item['ai_log'], 'member': member, 'input': sample['input'],
               'scores': sample['scores'], 'config': header['eval']['task_args'],
               'limit': sample.get('limit'), 'total_time_seconds': sample.get('total_time'),
               'working_time_seconds': sample.get('working_time'),
               'system_message': next(m['content'] for m in sample['messages'] if m['role'] == 'system'),
               **native_usage(sample, item['native_model'])}
        if item.get('human_estimate'):
            estimate = item['human_estimate']
            human_time = sum(c['seconds'] for c in estimate['components'])
            human_attempts = 'not_applicable'
            assert task == 'glacier-exchange'
        else:
            estimate = None
            human_time = statistics.mean(h['seconds'] for h in humans)
            human_attempts = len(humans)
        tokens = run['raw_totals']['counted_tokens']
        full = run['raw_totals']['full_prefix_tokens']
        relevant_files = [{'name': f['name'], 'lines': len(f['content'].splitlines()),
                           'sha256': hashlib.sha256(f['content'].encode()).hexdigest()}
                          for f in metadata.get('task_files', [])
                          if f.get('content') and f['name'].endswith('.py')]
        points.append({'point_id': item['point_id'], 'source_task_id': task,
                       'model_id': item['model_id'], 'flops_per_token': coefficient,
                       'model_row_sha256': hashlib.sha256(json.dumps(model, sort_keys=True).encode()).hexdigest(),
                       'human_time_seconds': human_time, 'human_attempts': human_attempts,
                       'human_estimate': estimate, 'human_observed_records': humans,
                       'failed_or_censored_human_records': omitted_attempts,
                       'observed_human_successes': sum(h['source_pass'] for h in humans),
                       'observed_human_attempts_for_performance': len(humans),
                       'task_code_files': relevant_files,
                       'original_ctf_first_solve_minutes_context_only': tasks[task]['human_minutes'],
                       'ai_attempts': 1, 'ai_successes': int(score == 'C'), 'runs': [run],
                       'tokens': tokens, 'compute_flops': coefficient*tokens,
                       'full_prefix_tokens': full, 'full_prefix_flops': coefficient*full,
                       'parameter_factor_two_scenario_flops': [coefficient*tokens/2, coefficient*tokens*2]})
    result = {'points': points, 'verified_source_sha256': verified,
              'selection_sha256': digest(a.selection),
              'accounting': 'Gemini prompt minus cached reads plus visible output plus thoughts; '
                            'reasoning counted once. All native task work, including unsuccessful runs. '
                            'No neural helpers appear; deterministic grader and environment are excluded.'}
    with a.output.open('x') as f:
        json.dump(result, f, indent=2)
        f.write('\n')
    print(json.dumps([{k: x[k] for k in ('point_id', 'human_time_seconds', 'tokens', 'compute_flops')}
                      for x in points], indent=2))


if __name__ == '__main__':
    main()
