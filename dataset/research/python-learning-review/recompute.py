#!/usr/bin/env python3
"""Reproduce the proposed human fields and source-scope checks; standard library only."""
import argparse
import csv
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', required=True, type=Path)
    parser.add_argument('--config', required=True, type=Path)
    parser.add_argument('--output-dir', required=True, type=Path)
    args = parser.parse_args()
    if args.output_dir.exists():
        parser.error('output directory already exists; use a new directory')
    if not args.source_dir.is_dir():
        parser.error('source directory does not exist')
    config = json.loads(args.config.read_text())
    with gzip.open(args.source_dir / 'HumanEval.jsonl.gz', 'rt') as f:
        tasks = [json.loads(line) for line in f]
    assert len(tasks) == 164
    assert [r['task_id'] for r in tasks] == [f'HumanEval/{i}' for i in range(164)]
    required = {'task_id', 'prompt', 'canonical_solution', 'test', 'entry_point'}
    assert all(required <= set(r) for r in tasks)
    assert len(config['routes']) == 5
    csv.field_size_limit(100_000_000)
    with open(args.source_dir / 'realhumaneval-study-data.csv', newline='') as f:
        participants = list(csv.DictReader(f))
    controls = [r for r in participants if r['model'] == 'nomodel']
    scope_checks = {
        'humaneval_tasks': len(tasks),
        'full_prompt_solution_test_inspection_count': len(config['inspection_ids']),
        'realhumaneval_participants': len(participants),
        'realhumaneval_no_llm_controls': len(controls),
        'realhumaneval_control_python_experience': dict(sorted(Counter(r['python_experience'] for r in controls).items())),
        'realhumaneval_control_programming_experience': dict(sorted(Counter(r['prog_experience'] for r in controls).items())),
        'source_sha256': {
            name: hashlib.sha256((args.source_dir / name).read_bytes()).hexdigest()
            for name in ['HumanEval.jsonl.gz', 'realhumaneval-study-data.csv']
        },
    }
    assert len(participants) == 243 and len(controls) == 39
    proposed = []
    for route in config['routes']:
        hours = sum(route['components_hours'].values())
        assert hours == route['scenario_hours']['central']
        assert 0 < route['scenario_hours']['efficient_targeted_learning'] < hours < route['scenario_hours']['slow_or_less_well_matched_learning']
        pid = route['point_id']
        start = route['start_pass1_percent']
        endpoint = route['target_pass1_percent']
        if isinstance(start, str):
            transition = f"An ordinary adult learns Python from no programming to {endpoint}% HumanEval pass@1, without generative-AI assistance."
        else:
            starting_repertoire = route['starting_repertoire_short']
            transition = f"An ordinary Python learner improves from {starting_repertoire} ({start}% HumanEval pass@1) to {endpoint}%, without generative-AI assistance."
        description = (
            f"{transition} "
            "Assessment: one first submitted function per unseen problem in the original 164-problem set, "
            "using its signature, docstring and examples, with no code execution before submission. "
            "Active learning includes instruction, practice with execution and feedback, and error review; "
            "excludes earlier learning and a separate final assessment."
        )
        if isinstance(start, str):
            perf = f"{route['model']} reaches {endpoint}% pass@1 from a near-zero GPT baseline. The assumed human learning target is the same aggregate first-submission accuracy."
        else:
            perf = f"Llama 2 to {route['model']} improves HumanEval pass@1 from {start}% to {endpoint}%. The assumed human learning target is the same aggregate transition."
        proposed.append({
            'point_id': pid,
            'proposed_fields': {
                'human_skill': 'typical',
                'human_time_scope': 'skill_acquisition',
                'human_time': hours * 3600,
                'human_time_evidence': 'assumed',
                'human_time_method': 'estimated',
                'human_time_statistic': 'point_estimate',
                'human_time_subset': 'not_applicable',
                'human_attempts': 'not_applicable',
                'task_description': description,
                'performance_vs_human': 'match',
                'performance_evidence': perf,
                'comparison_issues': 'different_inputs_or_tools',
                'human_time_source': f'research/python-learning-review/python-learning.md#{pid}',
            },
            'notes_human_clause': 'No measured HumanEval learning curve links these practice hours to the target score.',
            'research_only': {
                'central_hours': hours,
                'components_hours': route['components_hours'],
                'scenario_hours': route['scenario_hours'],
                'scenario_seconds': {k: v * 3600 for k, v in route['scenario_hours'].items()},
            },
        })
    args.output_dir.mkdir(parents=True)
    for name, value in [
        ('human-fields.json', proposed),
        ('source-scope-checks.json', scope_checks),
        ('inspected-tasks.json', [tasks[n] for n in config['inspection_ids']]),
    ]:
        (args.output_dir / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({r['point_id']: r['proposed_fields']['human_time'] for r in proposed}, indent=2))


if __name__ == '__main__':
    main()
