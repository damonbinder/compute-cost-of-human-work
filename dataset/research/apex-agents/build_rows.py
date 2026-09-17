#!/usr/bin/env python3
"""APEX-Agents-AA: derive per-task token workloads, cache branches, FLOPs and human time.

Dependencies: Python 3.9+ standard library only.

Usage:
  python3 build_rows.py \
      --aa-models  <agent-work/sources/apex-agents/aa-apex-agents-model-records.json> \
      --cacheable  <agent-work/sources/apex-agents/aa-cacheable-input-shares.csv> \
      --out        <research/apex-agents/calculations.json>

Every path is explicit; the script reads only the two retained source extracts and
writes one new JSON file. It does not modify the evidence it reads.
"""
import argparse, csv, json, math, statistics

# ---------------------------------------------------------------- constants
TASKS = 452                    # AA's APEX-Agents subset (480 less two IB worlds)
REPEATS = 3                    # AA methodology, Additional Evaluations table
# Criteria per task. Law and consulting are the card's 160-task means; IB is the mean
# over the 132 tasks AA retains, computed from the export, not the card's 160-task 2.93.
CRITERIA_IB, CRITERIA_LAW, CRITERIA_MC = 3.038, 4.57, 4.68
TASKS_IB, TASKS_LAW, TASKS_MC = 132, 160, 160
EST_H_IB, EST_H_LAW, EST_H_MC = 1.36, 2.40, 1.69     # dataset card domain means
BASELINE_EST_H, BASELINE_TRUE_H = 1.70, 1.37         # paper Section 3.5, n=96
BASELINE_BENCHMARK_EST_H = 1.82                      # v3 headline comparator
BASELINE_HEADLINE_DIFF_H = 0.45                      # v3 headline over-estimate

# Long-horizon donor evaluations, used for the scenario column only.
LONG_HORIZON = ['harveyLab', 'briefcase', 'gdpval', 'analystAgent']

# How the central is built, per row, from the provider caching evidence in
# research/apex-agents.md#the-caching-construction.
#   provider_default  - the endpoint caches without harness action, so the no-reuse
#                       branch is not live; bracket the achieved hit share instead.
#   uncached_harness  - the published harness sets no cache breakpoints and the
#                       provider caches nothing without them; gross is the central.
#   undetermined      - provider default not established; keep the two-branch bracket.
CENTRAL_RULE = {
    'gemini-3-5-flash':         'provider_default',
    'kimi-k3':                  'provider_default',
    'gpt-5-6-terra':            'provider_default',
    'gpt-5-5':                  'provider_default',
    'gpt-5-6-luna':             'provider_default',
    'glm-5-2':                  'provider_default',
    'gpt-5-4':                  'provider_default',
    'claude-opus-4-6-adaptive': 'uncached_harness',
    'gpt-oss-120b':             'undetermined',
}

# Fraction of the eligible prefix actually served from cache. Floor inverted from
# Lumer et al. (2601.06007) Table 2; ceiling is complete reuse of the eligible prefix.
HIT_SHARE_FLOOR = 0.60

# Lowest step-implied eligibility across Mercor's Table 4 (19 steps -> 1 - 2/20).
MERCOR_MIN_ELIGIBILITY = 0.90

# Active parameters per token. Values and bases come from the registries; see
# research/apex-agents.md#model-records. Kept here so the arithmetic is reproducible.
ACTIVE_PARAMS = {
    'gemini-3-5-flash':          ('gemini-3.5-flash',        40e9),
    'kimi-k3':                   ('kimi-k3',                104e9),
    'gpt-5-6-terra':             ('gpt-5-6-terra',           20e9),
    'gpt-5-5':                   ('gpt-5-5',                173e9),
    'gpt-5-6-luna':              ('gpt-5-6-luna',             8e9),
    'glm-5-2':                   ('glm-5.2',                 40e9),
    'gpt-5-4':                   ('gpt-5.4-2026-03-05',     100e9),
    'claude-opus-4-6-adaptive':  ('claude-opus-4-6',        100e9),
    'gpt-oss-120b':              ('gpt-oss-120b',           5.1e9),
}

# Mercor Table 4: mean steps per run on the Archipelago harness, same benchmark.
MERCOR_STEPS = {'Claude Opus 4.5': 19, 'Gemini 3 Flash': 54, 'Gemini 3 Pro': 24,
                'GPT-5': 34, 'GPT-5.2': 35, 'GPT-OSS-120B': 43, 'Grok 4': 31,
                'Kimi K2 Thinking': 92}

# Cached-context attention, 4*L_full*d_model*N_context per processed position
# (DECISIONS.md, RULER recipe). L_full counts layers carrying quadratic attention.
# Two models disclose their architecture; the rest are bracketed by tier, anchored
# on those two. See research/apex-agents.md#cached-context-attention.
ATTN_SHAPES = {
    'kimi-k3':                  {'disclosed': (24, 7168)},
    'gpt-oss-120b':             {'disclosed': (18, 2880)},
    'gpt-5-5':                  {'low': (64, 8192), 'mid': (80, 10240), 'high': (96, 12288)},
    'gpt-5-4':                  {'low': (64, 8192), 'mid': (80, 10240), 'high': (96, 12288)},
    'claude-opus-4-6-adaptive': {'low': (64, 8192), 'mid': (80, 10240), 'high': (96, 12288)},
    'gemini-3-5-flash':         {'low': (48, 5120), 'mid': (60, 6144), 'high': (72, 7168)},
    'glm-5-2':                  {'low': (48, 5120), 'mid': (60, 6144), 'high': (72, 7168)},
    'gpt-5-6-terra':            {'low': (36, 3584), 'mid': (46, 4352), 'high': (56, 5120)},
    'gpt-5-6-luna':             {'low': (28, 2880), 'mid': (34, 3488), 'high': (40, 4096)},
}


def human_time_seconds():
    """Task-weighted expert estimate over the 452-task subset, and its calibration."""
    est_h = (TASKS_IB * EST_H_IB + TASKS_LAW * EST_H_LAW + TASKS_MC * EST_H_MC) / TASKS
    ratio = BASELINE_TRUE_H / BASELINE_EST_H
    return {
        'subset_weighted_estimate_hours': est_h,
        'subset_weighted_estimate_seconds': est_h * 3600,
        'baselining_ratio': ratio,
        'calibrated_hours': est_h * ratio,
        'calibrated_seconds': est_h * ratio * 3600,
        'additive_alternative_hours': est_h - (BASELINE_EST_H - BASELINE_TRUE_H),
        'full_480_estimate_hours': (EST_H_IB + EST_H_LAW + EST_H_MC) / 3,
        # The paper's own v3 headline compares the sampled true time with the
        # benchmark-wide estimate rather than with the sampled estimate.
        'headline_ratio_hours': est_h * (BASELINE_TRUE_H / BASELINE_BENCHMARK_EST_H),
        'headline_ratio_seconds': est_h * (BASELINE_TRUE_H / BASELINE_BENCHMARK_EST_H) * 3600,
        'headline_additive_hours': est_h - BASELINE_HEADLINE_DIFF_H,
        'headline_additive_seconds': (est_h - BASELINE_HEADLINE_DIFF_H) * 3600,
        'subset_weighted_criteria_per_task':
            (TASKS_IB * CRITERIA_IB + TASKS_LAW * CRITERIA_LAW + TASKS_MC * CRITERIA_MC) / TASKS,
    }


def donor_shares(rows):
    """model_slug -> {benchmark: cacheable share} from the retained AA table."""
    out = {}
    for r in rows:
        out.setdefault(r['model_slug'], {})[r['benchmark']] = float(r['cacheable_share'])
    return out


def pick_donor(slug, company, shares):
    """Median cacheable share for a model: own donors, else same-company donors."""
    own = shares.get(slug, {})
    if own:
        return statistics.median(own.values()), 'own_model', sorted(own), None
    peers = {s: v for s, v in shares.items() if v and COMPANY_OF.get(s) == company}
    if peers:
        med = {s: statistics.median(v.values()) for s, v in peers.items()}
        return statistics.median(med.values()), 'same_company', sorted(peers), med
    allmed = [statistics.median(v.values()) for v in shares.values() if v]
    return statistics.median(allmed), 'all_models', [], None


def pick_long_horizon(slug, company, shares):
    own = {b: v for b, v in shares.get(slug, {}).items() if b in LONG_HORIZON}
    if own:
        return statistics.median(own.values())
    peers = []
    for s, v in shares.items():
        sub = [x for b, x in v.items() if b in LONG_HORIZON]
        if sub and COMPANY_OF.get(s) == company:
            peers.append(statistics.median(sub))
    if peers:
        return statistics.median(peers)
    allm = []
    for v in shares.values():
        sub = [x for b, x in v.items() if b in LONG_HORIZON]
        if sub:
            allm.append(statistics.median(sub))
    return statistics.median(allm)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--aa-models', required=True)
    ap.add_argument('--cacheable', required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()

    aa = json.load(open(a.aa_models))
    rows = list(csv.DictReader(open(a.cacheable)))

    global COMPANY_OF
    COMPANY_OF = {r['model_slug']: r['company'] for r in rows}
    for slug, rec in aa.items():
        COMPANY_OF.setdefault(slug, rec['creator'])

    shares = donor_shares(rows)
    ht = human_time_seconds()

    models = {}
    for slug, rec in aa.items():
        tk = rec['canonicalEvalTokenCounts_apexAgents']
        assert tk['cacheableInput'] is None, slug     # the gap this whole branch exists for
        I = tk['input'] / TASKS
        O = (tk['answer'] + tk['reasoning']) / TASKS

        s, basis, donors, peer_meds = pick_donor(slug, rec['creator'], shares)
        s_lh = pick_long_horizon(slug, rec['creator'], shares)
        h = rec['cacheHitRate']

        rule = CENTRAL_RULE[slug]
        T_gross = I + O                               # no reuse at all
        T_full = I * (1 - s) + O                      # every eligible token served
        T_floor = I * (1 - HIT_SHARE_FLOOR * s) + O   # eligible prefix served at the floor rate
        if rule == 'provider_default':
            hi, lo = T_floor, T_full
            T = math.sqrt(hi * lo)
        elif rule == 'uncached_harness':
            hi = lo = T = T_gross
        else:
            hi, lo = T_gross, T_full
            T = math.sqrt(hi * lo)
        implied_share = (T_gross - T) / I             # cache-read share reproducing the central

        mid, P = ACTIVE_PARAMS[slug]
        fpt = 2 * P
        scen = {
            'no_reuse': T_gross,
            'full_eligible_reuse': T_full,
            'hit_share_floor': T_floor,
            'aa_live_cache_hit_rate_direct': I * (1 - h) + O,
            'long_horizon_donor_share': I * (1 - s_lh) + O,
            'mercor_step_eligibility_floor': I * (1 - MERCOR_MIN_ELIGIBILITY) + O,
        }
        models[slug] = {
            'model_name': rec['name'], 'company': rec['creator'],
            'central_rule': rule,
            'aa_rate_exceeds_eligibility': h is not None and h > s,
            'central_branch_high': hi, 'central_branch_low': lo,
            'model_id': mid, 'release_date': rec['releaseDate'],
            'pass_at_1': rec['apexAgentsPassAt1'],
            'input_tokens_per_task': I,
            'answer_tokens_per_task': tk['answer'] / TASKS,
            'reasoning_tokens_per_task': tk['reasoning'] / TASKS,
            'output_tokens_per_task': O,
            'gross_tokens_per_task': T_gross,
            'cacheable_share_donor': s,
            'cacheable_share_donor_basis': basis,
            'cacheable_share_donor_benchmarks': donors,
            'cacheable_share_donor_peer_medians': peer_meds,
            'cacheable_share_long_horizon': s_lh,
            'aa_live_cache_hit_rate': h,
            'counted_tokens_per_task': T,
            'implied_cache_read_share_of_input': implied_share,
            'active_parameters': P,
            'flops_per_token': fpt,
            'compute_flops': T * fpt,
            'scenario_counted_tokens': scen,
            'scenario_flops_multiple_of_central': {k: v / T for k, v in scen.items()},
            'mean_context_if_N_calls': {N: I / N for N in (20, 40, 60, 80)},
        }

    # Corroboration: Mercor's own step counts imply a cacheable share under the
    # linear-prefix-growth recipe 1 - 2/(N+1) used by the dataset's RLI rows.
    corr = {m: {'steps': n, 'implied_cacheable_share_lower_bound': 1 - 2 / (n + 1)}
            for m, n in MERCOR_STEPS.items()}

    # Cached-context attention, omitted from compute_flops by the 2*P convention.
    attn = {}
    for slug, m in models.items():
        per = {}
        for name, (Lf, dm) in ATTN_SHAPES[slug].items():
            coef = 4 * Lf * dm
            per['%s L_full=%d d=%d' % (name, Lf, dm)] = {
                str(ctx): coef * ctx * m['counted_tokens_per_task'] / m['compute_flops']
                for ctx in (10000, 20000, 50000, 100000)}
        attn[slug] = per

    out = {
        'description': 'APEX-Agents-AA per-task token workload, cache branches, FLOPs and human time',
        'inputs': {'aa_models': a.aa_models, 'cacheable_shares': a.cacheable},
        'constants': {'tasks': TASKS, 'repeats': REPEATS,
                      'task_runs': TASKS * REPEATS,
                      'hit_share_floor': HIT_SHARE_FLOOR,
                      'mercor_min_eligibility': MERCOR_MIN_ELIGIBILITY,
                      'tasks_ib': TASKS_IB, 'tasks_law': TASKS_LAW,
                      'tasks_mc': TASKS_MC, 'est_hours_ib': EST_H_IB,
                      'est_hours_law': EST_H_LAW, 'est_hours_mc': EST_H_MC,
                      'baselining_estimated_hours': BASELINE_EST_H,
                      'baselining_true_hours': BASELINE_TRUE_H,
                      'baselining_n': 96},
        'human_time': ht,
        'models': models,
        'mercor_step_corroboration': corr,
        'cached_context_attention_multiple_of_recorded': attn,
    }
    with open(a.out, 'w') as f:
        json.dump(out, f, indent=1, sort_keys=True)
    print('wrote', a.out)
    print('human_time central %.1f s (uncalibrated %.1f s; v3 headline %.1f / %.1f s)' %
          (ht['calibrated_seconds'], ht['subset_weighted_estimate_seconds'],
           ht['headline_ratio_seconds'], ht['headline_additive_seconds']))
    for slug, m in sorted(models.items(), key=lambda kv: -kv[1]['compute_flops']):
        print('%-26s %-17s tokens %10.0f  cache-read %.3f  FLOPs %.3e' %
              (slug, m['central_rule'], m['counted_tokens_per_task'],
               m['implied_cache_read_share_of_input'], m['compute_flops']))


if __name__ == '__main__':
    main()
