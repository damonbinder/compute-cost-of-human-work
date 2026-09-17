#!/usr/bin/env python3
"""Recompute the Latxa human proposal from SOURCE_DIR into NEW_OUTPUT_DIR.

Python 3 standard library only. Keep assumptions.json and question-inspection.json
beside this script. Source inputs are read, never modified or executed.
"""
import argparse
import collections
import hashlib
import json
import random
from pathlib import Path


def read(path):
    return json.loads(path.read_text())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source_dir', type=Path)
    parser.add_argument('output_dir', type=Path)
    args = parser.parse_args()
    source, output = args.source_dir.resolve(), args.output_dir.resolve()
    if output.exists() or source == output or source in output.parents:
        raise SystemExit('Output must be a new directory outside retained sources.')
    here = Path(__file__).resolve().parent
    assumptions = read(here / 'assumptions.json')
    inspection = read(here / 'question-inspection.json')
    manifest = read(source / 'manifest.json')
    for entry in manifest['files']:
        assert hashlib.sha256((source / entry['path']).read_bytes()).hexdigest() == entry['sha256'], entry['path']
    questions = [json.loads(line) for line in (source / 'atarikoa.jsonl').read_text().splitlines()]
    assert len(questions) == assumptions['source_question_count'] == 5169
    assert all(len(q['candidates']) == 4 and q['answer'] in range(4) for q in questions)
    selected_ids = sorted(random.Random(20260913).sample(range(len(questions)), 60))
    assert [q['id'] for q in inspection['records']] == selected_ids
    for q in inspection['records']:
        assert {k: q[k] for k in questions[q['id']]} == questions[q['id']]
    category_counts = dict(collections.Counter(q['inspection_category'] for q in inspection['records']))
    assert category_counts == inspection['category_counts']
    targets = {}
    for size, target in assumptions['targets'].items():
        start = read(source / f'Llama-2-{size}-hf_eus_proficiency_5-shot.json')['results']['eus_proficiency']['acc,none']
        end = read(source / f'latxa-{size}-v1.1_eus_proficiency_5-shot.json')['results']['eus_proficiency']['acc,none']
        assert start == target['start_accuracy'] and end == target['end_accuracy']
        hours = sum(assumptions['components_hours'][k] for k in target['components'])
        assert hours == target['central_hours']
        targets[size] = {
            'start_accuracy': start,
            'end_accuracy': end,
            'human_hours': hours,
            'human_time': hours * 3600,
            'sensitivity_hours': target['sensitivity_hours'],
            'sensitivity_seconds': [h * 3600 for h in target['sensitivity_hours']],
            'known_answer_equivalent_fraction_for_scale_only': (end - 0.25) / 0.75,
        }
    cumulative, total = {}, 0
    for level, hours in assumptions['heoc_incremental_planning_hours'].items():
        total += hours
        cumulative[level] = total
    result = {
        'source_hashes_checked': len(manifest['files']),
        'question_count': len(questions),
        'question_sample_count': len(selected_ids),
        'sample_category_counts': category_counts,
        'answer_key_counts': dict(collections.Counter(q['answer'] for q in questions)),
        'heoc_cumulative_planning_hours': cumulative,
        'targets': targets,
        'interpretation': 'Hours are task-inspected learning-route assumptions. No formula fits hours to scores; the guessing diagnostic is not used in duration arithmetic.',
    }
    output.mkdir(parents=True)
    (output / 'human-calculations.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(targets, indent=2))


if __name__ == '__main__':
    main()
