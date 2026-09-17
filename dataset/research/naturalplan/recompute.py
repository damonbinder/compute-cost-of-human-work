#!/usr/bin/env python3
"""Natural Plan calendar replay. Python3 + sentencepiece. No model calls.
Usage: python recompute.py SOURCE_DIR NEW_OUTPUT_DIR [--assumptions FILE]
"""
import argparse
import ast
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
from calendar_constraints import answer, task_details


def main():
    p = argparse.ArgumentParser()
    p.add_argument('source_dir', type=Path)
    p.add_argument('output_dir', type=Path)
    p.add_argument('--assumptions', type=Path, default=Path(__file__).with_name('assumptions.json'))
    args = p.parse_args()
    src, out = args.source_dir.resolve(), args.output_dir.resolve()
    if out.exists() or out == src or src in out.parents:
        raise SystemExit('Output must be new and outside source directory')
    for row in json.loads((src / 'manifest.json').read_text()):
        assert hashlib.sha256((src / row['path']).read_bytes()).hexdigest() == row['sha256'], row['path']
    tree_source = json.loads((src / 'tree.json').read_text())
    assert tree_source['sha'] == 'ca76db336072ff8931db43bc1ca8d381038cf073'
    blobs = {r['path']: r['sha'] for r in tree_source['tree'] if r['type'] == 'blob'}
    for local, original in [('data__calendar_scheduling.json', 'data/calendar_scheduling.json'),
                            ('data__README.md', 'data/README.md'),
                            ('evaluate_calendar_scheduling.py', 'evaluate_calendar_scheduling.py')]:
        raw = (src / local).read_bytes()
        assert hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == blobs[original], local
    a = json.loads(args.assumptions.read_text())
    import sentencepiece as spm
    tok = spm.SentencePieceProcessor(model_file=str(src / 'gemma-tokenizer.model'))
    expected = '61a7b147390c64585d6c3543dd6fc636906c9af3865a5548f27f31aee1d4c8e2'
    assert hashlib.sha256((src / 'gemma-tokenizer.model').read_bytes()).hexdigest() == expected
    loader = (src / 'vertex-loader.py').read_text()
    assert expected in loader and 'gemini-1.5-pro' in loader
    data = json.loads((src / 'data__calendar_scheduling.json').read_text())
    assert len(data) == 1000
    # Execute only three isolated deterministic original evaluator functions;
    # do not import its flags, file loader or main routine.
    tree = ast.parse((src / 'evaluate_calendar_scheduling.py').read_text())
    pure = ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef)
                           and n.name in ('hour_to_num', '_parse_response', 'compute_solve_rate')], type_ignores=[])
    env = {'re': re}
    exec(compile(pure, 'original-evaluator-functions', 'exec'), env)

    def human(d, settings):
        B, P, D, F = len(d['schedule_blocks']), len(d['people']), len(d['days']), len(d['exclusions'])
        parts = {'orientation': settings['orientation'],
                 'read_and_mark_intervals': B * settings['per_interval_read_mark'],
                 'participant_day_context': P * D * settings['per_person_day_context'],
                 'interpret_preferences': F * settings['per_preference_interpret'],
                 'find_slot': settings['slot_scan_fixed'] + D * settings['slot_scan_per_day'],
                 'verify': settings['verify_fixed'] + P * settings['verify_per_person'] + F * settings['verify_per_preference'],
                 'write_answer': settings['write_answer']}
        return {'seconds': sum(parts.values()), 'components': parts}

    rows = []
    groups = defaultdict(list)
    prefixes = set()
    for key, r in data.items():
        assert r['prompt_5shot'].count('TASK: ') == 6 and r['prompt_5shot'].count('SOLUTION: ') == 6
        prefixes.add(r['prompt_5shot'].rsplit('TASK: ', 1)[0])
        d = task_details(r)
        gold, pred, tolerant = answer(r['golden_plan']), answer(r['pred_5shot_pro']), answer(r['pred_5shot_pro'], True)
        assert gold in d['valid'], key
        native_ok = env['_parse_response'](r['pred_5shot_pro']) == env['_parse_response'](r['golden_plan'])
        assert native_ok == (pred == gold), key
        it, ot = len(tok.encode(r['prompt_5shot'])), len(tok.encode(r['pred_5shot_pro']))
        assert it > 0 and ot > 0
        token_count = it + ot + a['message_and_stop_allowance_tokens']
        if tolerant in d['valid']:
            failure = None
        elif tolerant is None:
            failure = 'no_proposed_slot'
        elif tolerant[0] not in d['days']:
            failure = 'wrong_day'
        elif tolerant[2] - tolerant[1] != d['duration_slots']:
            failure = 'wrong_duration'
        elif tolerant[1] < 18 or tolerant[2] > 34:
            failure = 'outside_work_hours'
        elif tolerant in d['feasible']:
            failure = 'violates_earliest'
        else:
            failure = 'busy_or_excluded'
        row = {'id': key, 'people': len(d['people']), 'days': len(d['days']),
               'duration_hours': float(r['duration']), 'target_words': len(d['target'].split()),
               'busy_interval_count': len(d['schedule_blocks']), 'preference_fragment_count': len(d['exclusions']),
               'earliest_required': d['earliest'], 'gold': gold, 'prediction': pred, 'tolerant_prediction': tolerant,
               'feasible_slots': d['feasible'], 'accepted_slots': d['valid'],
               'native_exact': native_ok, 'constraint_valid': tolerant in d['valid'], 'failure_type': failure,
               'input_text_tokens': it, 'output_text_tokens': ot, 'total_text_tokens': token_count,
               'compute_flops': 2 * a['active_parameters'] * token_count,
               'human': {name: human(d, val) for name, val in a['human'].items()}}
        rows.append(row)
        groups[(row['people'], row['days'])].append(row)
    assert len(prefixes) == 10 and len(groups) == 10 and all(len(rs) == 100 for rs in groups.values())
    assert sum(r['native_exact'] for r in rows) == 489
    assert sum(r['constraint_valid'] for r in rows) == 534
    assert sum(len(r['accepted_slots']) > 1 for r in rows) == 166

    def summarize(rs):
        mean = lambda fn: sum(fn(r) for r in rs) / len(rs)
        return {'count': len(rs), 'native_exact_correct': sum(r['native_exact'] for r in rs),
                'constraint_valid_correct': sum(r['constraint_valid'] for r in rs),
                'multiple_valid_answers': sum(len(r['accepted_slots']) > 1 for r in rs),
                'input_text_tokens': mean(lambda r: r['input_text_tokens']),
                'output_text_tokens': mean(lambda r: r['output_text_tokens']),
                'text_tokens': mean(lambda r: r['total_text_tokens']),
                'compute_flops': mean(lambda r: r['compute_flops']),
                'busy_intervals': mean(lambda r: r['busy_interval_count']),
                'preference_fragments': mean(lambda r: r['preference_fragment_count']),
                'target_words': mean(lambda r: r['target_words']),
                'human_seconds': {name: mean(lambda r: r['human'][name]['seconds']) for name in a['human']}}
    summary = summarize(rows)
    summary['human_reported_seconds'] = a['human_reported_seconds']
    summary['human_central_components'] = {k: sum(r['human']['central']['components'][k] for r in rows) / len(rows)
                                           for k in rows[0]['human']['central']['components']}
    summary['failure_types'] = dict(Counter(r['failure_type'] or 'valid' for r in rows))
    summary['strict_unparsed'] = [r['id'] for r in rows if r['prediction'] is None]
    summary['tolerant_unparsed'] = [r['id'] for r in rows if r['tolerant_prediction'] is None]
    summary['active_parameter_scenarios'] = {str(n): summary['text_tokens'] * 2 * n for n in (30_000_000_000, 300_000_000_000)}
    summary['no_wrapper_allowance_flops'] = (summary['text_tokens'] - a['message_and_stop_allowance_tokens']) * 2 * a['active_parameters']
    result = {'point_id': 'reas-work-calendar-naturalplan-gemini15pro-5shot', 'assumptions': a,
              'summary': summary, 'groups': [{'people': key[0], 'days': key[1], **summarize(rs)} for key, rs in sorted(groups.items())]}
    out.mkdir(parents=True)
    (out / 'calculations.json').write_text(json.dumps(result, indent=2) + '\n')
    (out / 'attempts.json').write_text(json.dumps(rows, indent=2) + '\n')
    selection = json.loads(Path(__file__).with_name('inspection-selection.json').read_text())
    inspected = [{'id': key, 'target': task_details(data[key])['target'],
                  'gold': data[key]['golden_plan'], 'prediction': data[key]['pred_5shot_pro']}
                 for key in selection['ids']]
    (out / 'inspected-tasks.json').write_text(json.dumps(inspected, indent=2) + '\n')
    print(json.dumps(summary))


if __name__ == '__main__':
    main()
