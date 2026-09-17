#!/usr/bin/env python3
"""Build the ARC-AGI-3 disposition table.

One row per source record: the 39 ARC-AGI-3 Semi-Private leaderboard entries, and
the 12 GPT-6 Astra ARC-AGI-3 Public Demo configurations the results page reports.

RHAE is normalised so that 100% is the median human who completed the level, so
the ratio to the human baseline is the score itself, and the chance floor is
about zero (an environment is only accepted if a random policy solves a level
less than once in 10,000 tries). The exclusion guide therefore sits at RHAE 0.5.

Standard errors of a mean over 55 environments: for the twelve GPT-6 Astra
configurations, the per-environment standard deviation measured on the same
configuration's 25 public-demo cells; for every other entry, the largest value a
[0, 1]-bounded mean can take, 0.5 / sqrt(55), which is an upper bound and
therefore the most generous test the close-call rule can be given.

Usage:
    python3 build_dispositions.py <leaderboard.json> <public-demo-cells.csv> <out.csv>

Dependencies: Python 3.9+ standard library only.
"""
import csv
import json
import math
import statistics
import sys

N_SEMI = 55
N_PUBLIC = 25
GUIDE = 0.5
ROW_IDS = {
    'openai-gpt-6-astra-high-provider-adapter': 'game-arcagi3-astra-pa-high',
    'openai-gpt-6-astra-max-provider-adapter': 'game-arcagi3-astra-pa-max',
    'openai-gpt-6-astra-xhigh-provider-adapter': 'game-arcagi3-astra-pa-xhigh',
    'openai-gpt-6-astra-medium-provider-adapter': 'game-arcagi3-astra-pa-medium',
    'openai-gpt-6-astra-low-provider-adapter': 'game-arcagi3-astra-pa-low',
    'openai-gpt-6-astra-none-provider-adapter': 'game-arcagi3-astra-pa-none',
    'openai-gpt-6-astra-max': 'game-arcagi3-astra-std-max',
    'openai-gpt-6-astra-xhigh': 'game-arcagi3-astra-std-xhigh',
    'openai-gpt-6-astra-high': 'game-arcagi3-astra-std-high',
}
PUBLIC_REASON = (
    'ARC never reports public-set scores on the official leaderboard, states the public '
    'set is materially easier than the private set and that evaluating on it is not a '
    'valid measure of progress, and no dollar cost is published for these runs; the 25 '
    'environments have been public since 2025. The measured per-call token counters of '
    'these runs are used instead as the donor mix for the semi-private inversion'
)
FIELDS = ['record', 'dataset', 'model_display', 'harness', 'effort', 'n_environments',
          'rhae', 'human_baseline', 'ratio_to_human', 'se_of_ratio', 'se_basis',
          'se_of_ratio_note', 'standard_errors_below_guide', 'cost_usd', 'point_id',
          'outcome', 'reason']


def main(lb_path, cells_path, out_path):
    evals = json.load(open(lb_path, encoding='utf-8'))['evaluations']
    cells = list(csv.DictReader(open(cells_path, newline='', encoding='utf-8')))

    by_config = {}
    for c in cells:
        suffix = '-provider-adapter' if c['harness'] == 'provider_adapter' else ''
        key = f"openai-gpt-6-astra-{c['effort']}{suffix}"
        by_config.setdefault(key, []).append(float(c['rhae_pct']) / 100)

    bound_se = GUIDE / math.sqrt(N_SEMI)
    rows = []
    for e in sorted(evals, key=lambda x: -x['score']):
        mid = e['modelId']
        scores = by_config.get(mid)
        if scores:
            se = statistics.stdev(scores) / math.sqrt(N_SEMI)
            se_basis = 'public_demo_per_environment_sd'
        else:
            se = bound_se
            se_basis = 'upper_bound_for_unit_interval_mean'
        ratio = e['score']
        sebelow = (GUIDE - ratio) / se if se > 0 else float('inf')
        harness = 'provider_adapter' if mid.endswith('-provider-adapter') else 'standard'
        effort = ''
        if mid.startswith('openai-gpt-6-astra-'):
            effort = mid[len('openai-gpt-6-astra-'):].replace('-provider-adapter', '')
        if ratio >= GUIDE:
            outcome, pid = 'row', ROW_IDS[mid]
            reason = (f'RHAE {ratio:.4f} against a human baseline of 1.0 on the '
                      f'benchmark\'s own metric, above the half-of-human guide; built '
                      f'as {pid}')
        else:
            outcome, pid = 'not a row', ''
            reason = (f'RHAE {ratio:.4f} is {ratio:.2f} of the human baseline, '
                      f'{sebelow:.2f} standard errors below the half-of-human guide')
            if abs(e['cost'] - 10000) < 1e-9:
                reason += ('; the run also stopped at ARC\'s published $10,000 per-run '
                           'cost cap, so the score is censored')
        rows.append({
            'record': mid, 'dataset': 'ARC-AGI-3 Semi-Private',
            'model_display': e['modelDisplayName'],
            'harness': harness if mid.startswith('openai-gpt-6-astra-') else '',
            'effort': effort, 'n_environments': N_SEMI,
            'rhae': round(ratio, 6), 'human_baseline': 1.0,
            'ratio_to_human': round(ratio, 4), 'se_of_ratio': round(se, 4),
            'se_basis': se_basis if ratio < GUIDE else '',
            'se_of_ratio_note': '' if ratio < GUIDE else 'not applied; entry is a row',
            'standard_errors_below_guide': round(sebelow, 2) if ratio < GUIDE else '',
            'cost_usd': round(e['cost'], 2), 'point_id': pid,
            'outcome': outcome, 'reason': reason,
        })

    for key, scores in sorted(by_config.items(), key=lambda kv: -statistics.mean(kv[1])):
        harness = 'provider_adapter' if key.endswith('-provider-adapter') else 'standard'
        effort = key[len('openai-gpt-6-astra-'):].replace('-provider-adapter', '')
        mean = statistics.mean(scores)
        rows.append({
            'record': key + ' (public demo)', 'dataset': 'ARC-AGI-3 Public Demo',
            'model_display': 'GPT-6 Astra', 'harness': harness, 'effort': effort,
            'n_environments': N_PUBLIC, 'rhae': round(mean, 6), 'human_baseline': 1.0,
            'ratio_to_human': round(mean, 4),
            'se_of_ratio': round(statistics.stdev(scores) / math.sqrt(N_PUBLIC), 4),
            'se_basis': '', 'se_of_ratio_note': 'not applied; disposition is not on score',
            'standard_errors_below_guide': '', 'cost_usd': '', 'point_id': '',
            'outcome': 'not a row', 'reason': PUBLIC_REASON,
        })

    with open(out_path, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    n_rows = sum(1 for r in rows if r['outcome'] == 'row')
    print(f'{len(rows)} records, {n_rows} rows -> {out_path}')


if __name__ == '__main__':
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    main(*sys.argv[1:])
