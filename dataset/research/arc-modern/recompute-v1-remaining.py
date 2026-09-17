#!/usr/bin/env python3
"""Reconstruct new ARC1 first-test comparisons. Source parser adapted from the reviewed ARC1 expansion implementation; all numerical outputs recomputed. Python 3.10+, standard library only.

Read retained original human actions, task grids and AI response records. Do not
execute model output. Sources and selection are never modified; output is new.
"""
import argparse
import ast
import collections
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path
import re


def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for data in iter(lambda: f.read(1024*1024), b''):
            h.update(data)
    return h.hexdigest()


def grid(text):
    return [[int(c) for c in row] for row in text.strip('|').split('|')]


def load_tasks(sources):
    tasks = collections.defaultdict(lambda: {'train': [], 'test': []})
    with (agent-work/sources/'human-evaluation-tasks.csv').open() as f:
        for row in csv.DictReader(f):
            tasks[Path(row['task_name']).stem][row['example_type']].append(
                {'input': grid(row['input_grid']), 'output': grid(row['output_grid'])})
    assert len(tasks) == 400
    return tasks


def load_humans(sources, tasks):
    summaries = collections.defaultdict(dict)
    with (agent-work/sources/'human-summary_data.csv').open() as f:
        for row in csv.DictReader(f):
            if row['task_type'] != 'evaluation':
                continue
            key = row['joint_id_task']
            attempt = int(row['attempt_number'])
            assert attempt not in summaries[key]
            truth = tasks[Path(row['task_name']).stem]['test'][0]['output']
            row['rescored_correct'] = grid(row['test_output_grid']) == truth
            summaries[key][attempt] = row
    events = collections.defaultdict(list)
    action_counts = collections.Counter()
    with (agent-work/sources/'human-data.csv').open() as f:
        for row in csv.DictReader(f):
            if row['task_type'] != 'evaluation':
                continue
            action_counts[row['action']] += 1
            events[row['joint_id_task']].append(dict(time=dt.datetime.fromisoformat(row['time']) if row['time'] else None,
                action_id=int(row['action_id']), attempt=int(row['attempt_number']),
                action=row['action'], submit_grid=row['test_output_grid'] if row['action']=='submit' else None))
    assert set(events) == set(summaries)
    result = collections.defaultdict(list)
    untimed = []
    for key, actions in events.items():
        if any(x['time'] is None for x in actions):
            assert all(x['time'] is None for x in actions), key
            untimed.append(dict(session_id=key, submissions=len(summaries[key]),
                reason='Every action timestamp absent in original data'))
            continue
        actions.sort(key=lambda x: (x['time'], x['action_id']))
        summary = summaries[key]
        assert sorted(summary) == list(range(1, len(summary)+1))
        assert len(summary) == 3 or any(x['solved'] == 'true' for x in summary.values())
        start = actions[0]['time']
        assert actions[0]['action'] == 'reset_grid'
        submits = [x for x in actions if x['action'] == 'submit']
        assert len(submits) == len(summary)
        assert {x['attempt'] for x in submits} == set(summary)
        summary_grid_discrepancies = []
        task_id = Path(summary[1]['task_name']).stem
        truth = tasks[task_id]['test'][0]['output']
        for submit in submits:
            record = summary[submit['attempt']]
            actual_grid = grid(submit['submit_grid'])
            if actual_grid != grid(record['test_output_grid']):
                summary_grid_discrepancies.append(dict(attempt=submit['attempt'],
                    submit_grid=actual_grid, summary_grid=grid(record['test_output_grid']),
                    submit_correct=actual_grid==truth,
                    summary_correct=record['rescored_correct']))
            record['rescored_correct'] = actual_grid == truth
        end2 = max(x['time'] for x in submits if x['attempt'] <= 2)
        end3 = max(x['time'] for x in submits)
        duration2, duration3 = (end2-start).total_seconds(), (end3-start).total_seconds()
        assert 0 < duration2 <= duration3
        first = summary[1]
        # The first explanation is timestamped only when finished, together with
        # the first submit. Its preceding gap cannot safely be called writing.
        explanation = [x for x in actions if x['action'] == 'write_first_description']
        assert len(explanation) == 1
        before = [x for x in actions if x['action_id'] < explanation[0]['action_id']]
        explanation_gap = (explanation[0]['time']-max(x['time'] for x in before)).total_seconds()
        result[Path(first['task_name']).stem].append(dict(
            session_id=key, participant_id=first['hashed_id'],
            completed_study=first['complete'] == 'true',
            seconds_two_submissions=duration2, seconds_three_submissions=duration3,
            seconds_source_full_task=(actions[-1]['time']-start).total_seconds(),
            correct_two_submissions=any(x['rescored_correct'] for k,x in summary.items() if k<=2),
            correct_three_submissions=any(x['rescored_correct'] for x in summary.values()),
            source_correct_two_submissions=any(x['solved']=='true' for k,x in summary.items() if k<=2),
            source_correct_three_submissions=any(x['solved']=='true' for x in summary.values()),
            score_discrepancies=[dict(attempt=k,source_correct=x['solved']=='true',
                rescored_correct=x['rescored_correct']) for k,x in summary.items()
                if x['rescored_correct'] != (x['solved']=='true')],
            summary_grid_discrepancies=summary_grid_discrepancies,
            submissions=len(summary), first_explanation_preceding_gap_seconds=explanation_gap))
    return dict(result), dict(action_counts), untimed


def prompt_data(metadata):
    prompts = [x['message']['content'] for x in metadata['choices']
               if x['message']['role'] == 'user']
    assert len(prompts) == 1
    prompt = prompts[0]
    def parse_grid(text):
        try:
            value = ast.literal_eval(text.strip())
            return [value] if value and isinstance(value[0], int) else value
        except SyntaxError:
            return [ast.literal_eval(line.strip()) for line in text.strip().splitlines() if line.strip()]
    test = parse_grid(prompt.split('--Test Input--',1)[1].split('--End of Test Input--',1)[0])
    examples = []
    for match in re.finditer(r'--Example \d+--\s*INPUT:\s*(.*?)\s*OUTPUT:\s*(.*?)(?=--Example|--End of Training)', prompt, re.S):
        examples.append({'input': parse_grid(match[1]), 'output': parse_grid(match[2])})
    assert examples
    return prompt, test, examples


def usage(metadata):
    u = metadata['usage']
    p, c, total = (u[k] for k in ['prompt_tokens', 'completion_tokens', 'total_tokens'])
    assert all(isinstance(x, int) and x >= 0 for x in [p,c,total])
    reasoning = (u.get('completion_tokens_details') or {}).get('reasoning_tokens') or 0
    if total == p+c:
        counted_output = c
        reasoning_relationship = 'included_in_completion'
    else:
        assert total == p+c+reasoning
        counted_output = c+reasoning
        reasoning_relationship = 'additional_to_completion'
    cached = (u.get('prompt_tokens_details') or {}).get('cached_tokens')
    assert cached is None or 0 <= cached <= p
    return dict(prompt_tokens=p, completion_tokens=c, native_total=total,
                explicit_reasoning_tokens=reasoning, output_including_reasoning=counted_output,
                reasoning_relationship=reasoning_relationship, known_cached_tokens=cached,
                counted_tokens=total-(cached or 0))


def load_model(sources, config, tasks):
    included, omitted, other_pairs, mismatches = {}, [], [], []
    diagnostics = dict(empty_response_slots=[], cache_fields=[], helper_fields=[],
                       error_status_finish_fields=[], zero_total_responses=[])
    def error_fields(value, prefix=''):
        if isinstance(value, dict):
            for key, child in value.items():
                if child and ('error' in key.lower() or key.lower() in ['status','finish_reason']):
                    yield prefix+'/'+key, child
                yield from error_fields(child, prefix+'/'+key)
        elif isinstance(value, list):
            for i, child in enumerate(value):
                yield from error_fields(child, prefix+'/'+str(i))
    def cache_fields(value, prefix=''):
        if isinstance(value, dict):
            for key, child in value.items():
                if 'cache' in key.lower():
                    yield prefix+'/'+key, child
                yield from cache_fields(child, prefix+'/'+key)
        elif isinstance(value, list):
            for i, child in enumerate(value):
                yield from cache_fields(child, prefix+'/'+str(i))
    found_tasks = set()
    for path in sorted((agent-work/sources/'runs'/config['source_directory']).glob('*.json')):
        if not re.fullmatch('[0-9a-f]{8}', path.stem):
            continue
        found_tasks.add(path.stem)
        task = tasks[path.stem]
        first_responses = []
        incomplete = []
        payload = json.loads(path.read_text())
        for field, value in error_fields(payload):
            diagnostics['error_status_finish_fields'].append(dict(task_id=path.stem,
                field=field,value=value))
        for array_index, pair in enumerate(payload):
            actual_indexes = set()
            responses = []
            for slot in ['attempt_1','attempt_2']:
                answer = pair.get(slot)
                if not answer or not answer.get('metadata'):
                    incomplete.append({'array_index':array_index, 'slot':slot})
                    diagnostics['empty_response_slots'].append(dict(task_id=path.stem,
                        array_index=array_index, slot=slot))
                    continue
                m = answer['metadata']
                if not m['usage']['total_tokens']:
                    diagnostics['zero_total_responses'].append(dict(task_id=path.stem,
                        array_index=array_index,slot=slot))
                for field, value in cache_fields(m):
                    diagnostics['cache_fields'].append(dict(task_id=path.stem,slot=slot,
                        field=field,value=value))
                if m.get('tool_calls') or m.get('num_turns'):
                    diagnostics['helper_fields'].append(dict(task_id=path.stem,slot=slot,
                        tool_calls=m.get('tool_calls'),num_turns=m.get('num_turns')))
                assert m['task_id'] == path.stem
                assert m['model'] == config['endpoint'], (path,m['model'])
                prompt, test, train = prompt_data(m)
                assert train == task['train'], path
                matches = [i for i,t in enumerate(task['test']) if t['input'] == test]
                assert len(matches) == 1, (path,matches)
                index = matches[0]
                actual_indexes.add(index)
                if m.get('pair_index',index) != index or array_index != index:
                    mismatches.append(dict(task_id=path.stem, array_index=array_index,
                        metadata_index=m.get('pair_index'), actual_index=index, slot=slot))
                correct = answer['answer'] == task['test'][index]['output']
                if isinstance(answer.get('correct'), bool):
                    assert answer['correct'] == correct, (path,slot,'source score differs')
                responses.append(dict(slot=slot, array_index=array_index, actual_index=index,
                    correct=correct, usage=usage(m), kwargs=m['kwargs'],
                    start=m['start_timestamp'], end=m['end_timestamp'],
                    prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(),
                    response_chars=sum(len(x['message']['content'] or '') for x in m['choices']
                                       if x['message']['role']=='assistant'),
                    reasoning_summary_chars=len(m.get('reasoning_summary') or ''),
                    answer=answer['answer']))
            assert len(actual_indexes) <= 1, (path,actual_indexes)
            if actual_indexes == {0}:
                first_responses.extend(responses)
            else:
                other_pairs.extend(dict(task_id=path.stem, **r) for r in responses)
        if len(first_responses) == 2:
            assert {r['slot'] for r in first_responses} == {'attempt_1','attempt_2'}
            assert len({r['prompt_sha256'] for r in first_responses}) == 1
            included[path.stem] = dict(responses=first_responses,
                tokens=sum(r['usage']['counted_tokens'] for r in first_responses),
                correct=any(r['correct'] for r in first_responses))
        else:
            omitted.append(dict(task_id=path.stem, first_test_responses=first_responses,
                empty_slots=incomplete, reason='Fewer than two recoverable first-test responses'))
    for task_id in sorted(set(tasks)-found_tasks):
        omitted.append(dict(task_id=task_id, first_test_responses=[], empty_slots=[],
            reason='No task file in the original released configuration'))
    return included, omitted, other_pairs, mismatches, diagnostics


def calculate(sources, human_sources, selection, models):
    tasks = load_tasks(human_sources)
    humans, action_counts, untimed = load_humans(human_sources,tasks)
    output = {'human_action_counts':action_counts, 'human_sessions':humans,
              'human_untimed_sessions':untimed, 'points':[]}
    for config in selection['configurations']:
        included, omitted, others, mismatches, diagnostics = load_model(sources,config,tasks)
        assert included
        all_h = [h for t in included for h in humans[t]]
        n = len(all_h)
        def hmean(field):
            return sum(h[field] for h in all_h)/n
        def weighted(fn):
            return sum(fn(v)*len(humans[t]) for t,v in included.items())/n
        tokens = weighted(lambda x:x['tokens'])
        model = models[config['model_id']]
        coefficient = float(model['flops_per_token'])
        assert coefficient == 2*float(model['active_parameters'])
        prompt_mean = weighted(lambda x:sum(r['usage']['prompt_tokens'] for r in x['responses']))
        second_prompt = weighted(lambda x:next(r['usage']['prompt_tokens'] for r in x['responses'] if r['slot']=='attempt_2'))
        output_mean = weighted(lambda x:sum(r['usage']['output_including_reasoning'] for r in x['responses']))
        retained = [r for value in included.values() for r in value['responses']]
        retained += [r for value in omitted for r in value['first_test_responses']]
        retained += others
        def retained_total(field):
            return sum(r['usage'][field] for r in retained)
        output['points'].append(dict(point_id=config['point_id'], model_id=config['model_id'],
            source_directory=config['source_directory'], included_tasks=len(included), human_attempts=n,
            human_time=hmean('seconds_two_submissions'), human_score=hmean('correct_two_submissions'),
            human_three_submission_time=hmean('seconds_three_submissions'),
            human_source_full_task_time=hmean('seconds_source_full_task'),
            human_three_submission_score=hmean('correct_three_submissions'),
            human_source_labels_two_submission_score=hmean('source_correct_two_submissions'),
            human_source_labels_three_submission_score=hmean('source_correct_three_submissions'),
            human_first_description_preceding_gap=hmean('first_explanation_preceding_gap_seconds'),
            ai_score=weighted(lambda x:x['correct']), tokens=tokens, flops_per_token=coefficient,
            compute_flops=tokens*coefficient, prompt_tokens=prompt_mean,
            output_including_reasoning=output_mean,
            source_metadata_diagnostics=diagnostics,
            retained_response_audit=dict(responses=len(retained),
                prompt_tokens=retained_total('prompt_tokens'),
                completion_tokens=retained_total('completion_tokens'),
                explicit_reasoning_tokens=retained_total('explicit_reasoning_tokens'),
                native_total=retained_total('native_total'),
                omitted_first_test_recoverable_tokens=sum(r['usage']['counted_tokens']
                    for value in omitted for r in value['first_test_responses']),
                other_test_tokens=sum(r['usage']['counted_tokens'] for r in others),
                cache_count_present=sum(r['usage']['known_cached_tokens'] is not None for r in retained),
                first_start=min(r['start'] for r in retained), last_start=max(r['start'] for r in retained)),
            cache_sensitivity=dict(second_identical_prompt_all_cached_tokens=tokens-second_prompt,
                second_identical_prompt_all_cached_flops=(tokens-second_prompt)*coefficient,
                all_prompt_cached_tokens=output_mean, all_prompt_cached_flops=output_mean*coefficient),
            included=included, omitted_first_tests=omitted, other_test_responses=others,
            array_or_metadata_index_mismatches=mismatches))
    return output


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['sources','human-sources','selection','models','manifest','output']:
        p.add_argument('--'+name,type=Path,required=True)
    a = p.parse_args()
    sources, selection, models, output = [getattr(a,k).resolve() for k in ['sources','selection','models','output']]
    human_sources = a.human_sources.resolve()
    if output.exists() or output.is_relative_to(sources) or output.is_relative_to(human_sources) or output in [selection,models]:
        p.error('output must be new and outside the retained source directory')
    manifest = json.loads(a.manifest.read_text())
    for entry in manifest:
        path = (agent-work/sources/entry['file']).resolve()
        if not path.is_relative_to(sources) or sha256(path) != entry['sha256']:
            p.error('source hash or path failed: '+entry['file'])
    human_manifest = json.loads((agent-work/sources/'shared-human-manifest.json').read_text())
    for entry in human_manifest:
        path = (human_sources/entry['file']).resolve()
        if not path.is_relative_to(human_sources) or sha256(path) != entry['sha256']:
            p.error('shared human source hash or path failed: '+entry['file'])
    with models.open() as f:
        model_rows = {r['model_id']:r for r in csv.DictReader(f)}
    result = calculate(sources,human_sources,json.loads(selection.read_text()),model_rows)
    result['source_manifest_sha256'] = sha256(a.manifest)
    result['selection_sha256'] = sha256(selection)
    result['models_sha256'] = sha256(models)
    result['shared_human_manifest_sha256'] = sha256(agent-work/sources/'shared-human-manifest.json')
    with output.open('x') as f:
        json.dump(result,f,indent=2)
        f.write('\n')
    print(json.dumps([{k:r[k] for k in ['point_id','included_tasks','human_attempts','human_time',
        'human_score','ai_score','tokens','compute_flops']} for r in result['points']],indent=2))


if __name__ == '__main__':
    main()
