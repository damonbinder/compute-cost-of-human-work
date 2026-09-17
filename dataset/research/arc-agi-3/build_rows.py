#!/usr/bin/env python3
"""Emit the nine ARC-AGI-3 candidate rows from the retained calculation file.

Reads research/arc-agi-3/calculations.json (written by compute_arc3.py) and
writes points.csv in the COLUMNS.md field order. Text fields are held inside the
folder's length norms; the script fails rather than truncating if one overruns.

Usage:
    python3 build_rows.py <calculations.json> <out-points.csv>

Dependencies: Python 3.9+ standard library only.
"""
import csv
import json
import sys

HEADER = ['point_id', 'task', 'task_category', 'task_description', 'model_id',
          'compute_scope', 'compute_flops', 'human_skill', 'human_time_scope',
          'human_time', 'performance_vs_human', 'comparison_issues',
          'compute_evidence', 'human_time_evidence', 'performance_evidence',
          'human_time_statistic', 'human_time_subset', 'human_attempts',
          'human_time_source', 'human_time_method', 'compute_method',
          'compute_statistic', 'compute_subset', 'ai_attempts', 'compute_source',
          'tokens', 'tokens_accounting', 'source_dataset', 'source_record',
          'notes', 'ai_cost_usd', 'ai_cost_basis', 'ai_cost_date',
          'human_cost_usd', 'human_cost_basis']

LIMITS = {'notes': 586, 'task_description': 560, 'performance_evidence': 337,
          'source_record': 455, 'compute_source': 220, 'human_time_source': 205}

HARNESS_NAME = {'standard': 'Standard', 'provider_adapter': 'Provider Adapter'}

CHANCE = ('A random policy solves a level under once in 10,000 tries, so the chance '
          'floor is ~0.')
UNCENSORED = 'UNCENSORED'

# point_id -> (harness, effort, performance label, closing sentence of
# performance_evidence). The six Provider Adapter rows are `above` on the
# coordinator's ruling of 2026-09-13: RHAE is censored at parity by
# construction, and the uncensored action counts put the agent at roughly twice
# the median completer's efficiency.
ROWS = [
    ('game-arcagi3-astra-pa-high', 'provider_adapter', 'high', 'above', UNCENSORED),
    ('game-arcagi3-astra-pa-max', 'provider_adapter', 'max', 'above', UNCENSORED),
    ('game-arcagi3-astra-pa-xhigh', 'provider_adapter', 'xhigh', 'above', UNCENSORED),
    ('game-arcagi3-astra-pa-medium', 'provider_adapter', 'medium', 'above', UNCENSORED),
    ('game-arcagi3-astra-pa-low', 'provider_adapter', 'low', 'above', UNCENSORED),
    ('game-arcagi3-astra-pa-none', 'provider_adapter', 'none', 'above', UNCENSORED),
    ('game-arcagi3-astra-std-max', 'standard', 'max', 'below', CHANCE),
    ('game-arcagi3-astra-std-xhigh', 'standard', 'xhigh', 'below', CHANCE),
    ('game-arcagi3-astra-std-high', 'standard', 'high', 'below', CHANCE),
]

# Measured on the 25 Public Demo runs of the same configuration: total actions
# against the environments' summed human baseline actions, and the share of the
# 183 baselined levels finished in strictly fewer actions than that level's
# baseline. The denominator is pooled over all baselined levels, matching the
# action ratio beside it; it differs from the completed-level count only for the
# none configuration, which left three levels of one environment unfinished.
UNCENSORED_STATS = {
    ('provider_adapter', 'max'): (37.8, 97.3),
    ('provider_adapter', 'xhigh'): (39.8, 98.4),
    ('provider_adapter', 'high'): (41.3, 95.6),
    ('provider_adapter', 'medium'): (41.0, 96.2),
    ('provider_adapter', 'low'): (44.3, 95.1),
    ('provider_adapter', 'none'): (47.8, 93.4),
}


def task_description(harness, effort):
    return (
        'One previously unseen ARC-AGI-3 semi-private environment played from the opening '
        'frame to the last of its six or more levels, on first exposure, with no '
        'instructions about goal or mechanics. Each turn the agent gets the 64x64 '
        'grid as rows of integers, up to seven animation frames and the available '
        'actions, and replies with one action; it is stopped at five times the median '
        f'human action count per level. GPT-6 Astra at {effort} reasoning effort under '
        f"ARC's {HARNESS_NAME[harness]} harness. Mean over the 55 environments. The "
        'human unit is one first-exposure attempt.')


def performance_evidence(score, tail, harness, effort):
    clause = ('so it censors at parity' if tail is UNCENSORED
              else 'so 100% is human parity')
    base = (
        "RHAE normalises a level's action count to the median human who completed it, "
        f'squared and capped at 1.15, {clause}. This run scored '
        f'{score * 100:.2f}% over the 55 semi-private environments, all solvable by '
        'humans on first exposure.')
    if tail is UNCENSORED:
        used, beaten = UNCENSORED_STATS[(harness, effort)]
        tail = (f'Uncensored on the public set it used {used}% of the baseline actions, '
                f'beating it on {beaten}% of levels.')
    return (base + ' ' + tail).strip() if tail else base


def notes(cached_rate_multiple, attention_low, attention_high, context_k):
    return (
        'No token counts are published for the semi-private runs. Compute inverts the '
        "published cost at Astra list prices under ARC's own cost model, which prices the "
        'gross input counter at the input rate and carries no cached rate in either of its '
        'benchmarking repositories. Output per gross input and the cached share are '
        'measured on the 25 public-demo runs of the same configuration, whose per-call '
        f'counters are published. Cache reads priced at $1/M instead: {cached_rate_multiple:.2f}x. '
        f'The ruled 100-600B size range gives 0.33-2.0x; attention over the {context_k}k '
        f'context, omitted by the convention, adds {attention_low:.1f}-{attention_high:.1f}x.')


def source_record(model_id, score, cost):
    return (
        f'arcprize.org leaderboard v3.json entry {model_id}, ARC-AGI-3 Semi-Private, 55 '
        f'environments, score {score:.5f}, cost {cost:.2f}, payload generated 2026-09-04. '
        'Donor mix from the 25 ARC-AGI-3 Public Demo runs of the same configuration, '
        'session GUIDs in research/arc-agi-3/astra-public-demo-runs.csv; performance: '
        'ARC-AGI-3 technical report sections 4.1 and 5, and https://arcprize.org/blog/astra')


def main(calc_path, out_path):
    calc = json.load(open(calc_path, encoding='utf-8'))
    out = []
    for pid, harness, effort, label, extra in ROWS:
        cfg = calc['configurations'][f'{harness}|{effort}']
        per = cfg['per_environment']
        att = cfg['omitted_attention']
        cached_mult = (cfg['scenarios']['arc_priced_cache_reads_at_cached_rate']['flops']
                       / cfg['scenarios']['central']['flops'])
        ctx_k = round(cfg['donor_public_demo']['mean_context_tokens_per_call'] / 1000)
        row = {
            'point_id': pid,
            'task': (f'Solve one unseen ARC-AGI-3 environment on first exposure '
                     f'({HARNESS_NAME[harness]} harness, {effort} reasoning)'),
            'task_category': 'games',
            'task_description': task_description(harness, effort),
            'model_id': 'gpt-6-astra',
            'compute_scope': 'inference',
            'compute_flops': repr(per['compute_flops']),
            'human_skill': 'typical',
            'human_time_scope': 'task_performance',
            'human_time': '486',
            'performance_vs_human': label,
            'comparison_issues': ('different_task; different_inputs_or_tools; '
                                  'different_attempt_selection'),
            'compute_evidence': 'derived_assumed_inputs',
            'human_time_evidence': 'task_timings',
            'performance_evidence': performance_evidence(
                cfg['leaderboard_score'], extra, harness, effort),
            'human_time_statistic': 'median',
            'human_time_subset': 'successful',
            'human_attempts': '',
            'human_time_source': ('https://arcprize.org/media/ARC_AGI_3_Technical_Report.pdf'
                                  ' section 5.3.1; research/arc-agi-3.md#human-baseline'),
            'human_time_method': 'other_calculation',
            'compute_method': 'params_tokens',
            'compute_statistic': 'mean',
            'compute_subset': 'all',
            'ai_attempts': '55',
            'compute_source': (f'research/arc-agi-3.md#{pid}; '
                               'research/arc-agi-3/calculations.json; '
                               'research/arc-agi-3/compute_arc3.py; '
                               'agent-work/sources/arc-agi-3/astra-public-demo-usage-2026-09-13.csv'),
            'tokens': repr(per['counted_tokens']),
            'tokens_accounting': 'input_cache_creation_output',
            'source_dataset': 'ARC-AGI-3 Semi-Private leaderboard, GPT-6 Astra, September 2026',
            'source_record': source_record(cfg['leaderboard_model_id'],
                                           cfg['leaderboard_score'],
                                           cfg['leaderboard_cost_usd']),
            'notes': notes(cached_mult, att[0]['ratio_to_recorded'],
                           att[2]['ratio_to_recorded'], ctx_k),
            'ai_cost_usd': f"{per['cost_usd']:.2f}",
            'ai_cost_basis': 'reported',
            'ai_cost_date': '2026-09-03',
            'human_cost_usd': '12.78',
            'human_cost_basis': 'reported_payment',
        }
        for field, cap in LIMITS.items():
            if len(row[field]) > cap:
                raise SystemExit(f'{pid}: {field} is {len(row[field])} > {cap}')
        out.append(row)
    with open(out_path, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=HEADER)
        w.writeheader()
        w.writerows(out)
    print(f'{len(out)} rows -> {out_path}')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    main(sys.argv[1], sys.argv[2])
