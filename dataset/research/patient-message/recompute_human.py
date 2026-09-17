"""Ayers forum-reply duration: original portal-timing calibration and assumptions.

Python 3.9+ standard library only. No clinical advice or model execution.
python3 -B recompute_human.py --sources HUMAN_SOURCE_DIR --output NEW_JSON
Source directory contains the retained XMLs, manifest and assumptions.json.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET


def txt(node):
    return ''.join(node.itertext())


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sources', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    a = p.parse_args()
    source, output = a.sources.resolve(), a.output.resolve()
    if output.exists() or output == source or source in output.parents:
        p.error('Choose a new output outside the source directory.')
    verified = {}
    for entry in json.loads((source/'source-manifest.json').read_text()):
        f = (source/entry['file']).resolve()
        assert source in f.parents and f.stat().st_size == entry['bytes']
        digest = hashlib.sha256(f.read_bytes()).hexdigest()
        assert digest == entry['sha256'], entry['file']
        verified[entry['file']] = digest
    original = ET.parse(source/'tai-seale2024.xml').getroot()
    table = next(t for t in original.iter('table-wrap')
                 if 'Time Spent Answering Patient Messages' in txt(t))
    labels = ['immediate_before_activation', 'delayed_before_activation', 'no_activation_T0']
    cohorts = {k: {} for k in labels}
    metric = None
    for row in table.iter('tr'):
        cells = [txt(c).strip() for c in row]
        if cells[0] in ['Read time, s', 'Reply time, s', 'Reply length, characters']:
            metric = {'Read time, s': 'read_seconds', 'Reply time, s': 'reply_seconds',
                      'Reply length, characters': 'reply_characters'}[cells[0]]
        elif cells[0].startswith('Time 0'):
            assert metric and len(cells) == 7
            for i, label in enumerate(labels):
                count = int(cells[1+2*i])
                match = re.fullmatch(r'(\d+) \((\d+)-(\d+)\)', cells[2+2*i])
                assert match, cells[2+2*i]
                median, q1, q3 = map(int, match.groups())
                cohorts[label][metric] = {'n': count, 'median': median, 'iqr': [q1, q3]}
    for cohort in cohorts.values():
        assert len(cohort) == 3
        assert len({c['n'] for c in cohort.values()}) == 1
    contributing_n = sum(c['read_seconds']['n'] for c in cohorts.values())
    assert contributing_n == 3680
    ferguson = ET.parse(source/'ferguson2023.xml').getroot()
    context = next(txt(x) for x in ferguson.iter('p') if 'average of 3.83 minutes' in txt(x))
    assert '2061 portal messages' in context and '2 physicians' in context
    assumptions = json.loads((source/'assumptions.json').read_text())
    central = sum(assumptions['central_seconds'].values())
    scenarios = {k: sum(v.values()) for k, v in assumptions['scenario_seconds'].items()}
    result = {
        'human_time': central,
        'human_skill': 'expert',
        'human_time_scope': 'task_performance',
        'human_time_evidence': 'transferred_timings',
        'human_time_method': 'estimated',
        'human_time_statistic': 'point_estimate',
        'human_time_subset': 'all',
        'human_attempts': contributing_n,
        'target': assumptions['target'],
        'central_assumed_components_seconds': assumptions['central_seconds'],
        'sensitivity_seconds': scenarios,
        'calibration_cohorts': cohorts,
        'count_semantics': 'Unique T0 message replies contributing to the calibration; '
                           'the same messages have read, reply and character measurements. '
                           'Count once. These are not observed Reddit response times.',
        'statistic_semantics': 'Judged transfer; no pooled median or median total is inferred '
                               'from the published component medians.',
        'context_only': {'study': 'Ferguson2023', 'timed_messages': 2061, 'physicians': 2,
                         'reported_mean_minutes': 3.83, 'mean_seconds': 3.83*60,
                         'contributes_to_human_attempts': False,
                         'reason': 'Broader portal workflow; start/end timestamp boundaries unspecified.'},
        'source_sha256': verified,
    }
    with output.open('x') as f:
        json.dump(result, f, indent=2)
        f.write('\n')
    print(json.dumps({k: result[k] for k in ('human_time', 'human_attempts', 'sensitivity_seconds')}, indent=2))


if __name__ == '__main__':
    main()
