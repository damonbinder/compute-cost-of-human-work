#!/usr/bin/env python3
"""Invert the published ARC-AGI-3 Semi-Private dollar costs into token counts and FLOPs.

The ARC Prize leaderboard publishes, for each GPT-6 Astra configuration, a total
dollar cost for one run over the 55 semi-private environments and no token
counts. ARC's own cost model, implemented identically in both of its
benchmarking repositories, is

    cost = gross_input_tokens * input_price + output_tokens * output_price

with the gross input counter (cached tokens included) priced at the full input
rate; there is no cached-input rate anywhere in either repository. Inverting one
published dollar figure therefore needs one ratio, output tokens per gross input
token, and recovering the dataset's counted-token quantity needs a second, the
cached share of gross input.

Both ratios are measured, not assumed, from the companion ARC-AGI-3 Public Demo
runs of the *same* model, harness, reasoning effort and harness code, whose
per-call provider usage counters are published through the replay recordings
(see fetch_usage.py). Only the environment set differs.

Counted tokens follow COLUMNS.md `params_tokens`: fresh input plus cache
creation plus output, with cache reads removed. Cache creation is zero as
measured: every usage block in the 300 recordings carries `input_tokens_details`
with `cached_tokens` and nothing else, so no cache-write counter was reported for
these runs, and write-side tokens sit inside the gross input counter and are
already counted as fresh input. This is not a claim that writes are free -- the
retained Astra price sheet prints a $12.50 cache-write rate -- only that no
separate write counter exists in what the provider returned here.

Usage:
    python3 compute_arc3.py <leaderboard.json> <usage.csv> <runs.csv> \
        <out-calculations.json> <out-rows.csv>

Dependencies: Python 3.9+ standard library only.
"""
import csv
import json
import math
import sys

# --- Constants, with their sources -----------------------------------------

# GPT-6 Astra text-token list prices, USD per million, from the OpenAI model
# page transcribed in agent-work/sources/factorio-astra/openai-list-prices-2026-09-13.json
# and carried in research/cost/list-prices.csv (price sheet from 2026-09-03).
P_INPUT = 10.00
P_CACHED = 1.00
P_OUTPUT = 50.00
# Long-context surcharge starts above 272,000 input tokens; the harness caps the
# context far below that, so it never applies.
LONG_CONTEXT_THRESHOLD = 272_000

# models.csv: gpt-6-astra, 300B active parameters, 2 * active_parameters.
FLOPS_PER_TOKEN = 6.0e11
ACTIVE_PARAMS_LOW = 100e9
ACTIVE_PARAMS_CENTRAL = 300e9
ACTIVE_PARAMS_HIGH = 600e9

N_SEMI_PRIVATE = 55      # technical report Table 1
N_PUBLIC_DEMO = 25       # technical report Table 1

EFFORTS = ['max', 'xhigh', 'high', 'medium', 'low', 'none']

# Attention shapes bracketing 300B dense-equivalent active parameters, on the
# 12 * layers * d_model^2 standard-block count, following the convention in
# research/factorio-astra.md#cached-context-attention.
ATTENTION_SHAPES = [
    ('L=80, d=12288', 80, 12288),
    ('L=96, d=16384', 96, 16384),
    ('L=120, d=18432', 120, 18432),
]


def lb_model_id(harness: str, effort: str) -> str:
    suffix = '-provider-adapter' if harness == 'provider_adapter' else ''
    return f'openai-gpt-6-astra-{effort}{suffix}'


def invert(cost: float, kappa: float, rho: float, discounted: bool = False) -> dict:
    """Recover gross input, output and counted tokens from a published cost."""
    if discounted:
        price_per_gross_input = (1 - kappa) * P_INPUT + kappa * P_CACHED + rho * P_OUTPUT
    else:
        price_per_gross_input = P_INPUT + rho * P_OUTPUT
    gross_input = cost * 1e6 / price_per_gross_input
    output = rho * gross_input
    cached = kappa * gross_input
    counted = gross_input - cached + output
    return {
        'price_usd_per_million_gross_input': price_per_gross_input,
        'gross_input_tokens': gross_input,
        'cached_tokens': cached,
        'fresh_input_tokens': gross_input - cached,
        'output_tokens': output,
        'counted_tokens': counted,
        'flops': counted * FLOPS_PER_TOKEN,
    }


def attention_scenarios(counted: float, fresh: float, output: float,
                        mean_context: float, kappa: float) -> list:
    """FLOPs omitted by the 2 * active_parameters convention.

    Attention costs 4 * layers * d_model * context_depth per processed position.
    A call whose cached share is f re-prefills the last (1 - f) of its context,
    so its fresh positions sit at depths from f * N to N and average
    N * (1 + f) / 2; generated positions sit at depth N.
    """
    fresh_depth = mean_context * (1 + kappa) / 2
    rows = []
    for label, layers, d_model in ATTENTION_SHAPES:
        coeff = 4 * layers * d_model
        flops = coeff * (fresh * fresh_depth + output * mean_context)
        rows.append({
            'shape': label,
            'layers': layers,
            'd_model': d_model,
            'dense_equivalent_parameters': 12 * layers * d_model ** 2,
            'four_l_d': coeff,
            'mean_fresh_depth': fresh_depth,
            'attention_flops': flops,
            'ratio_to_recorded': flops / (counted * FLOPS_PER_TOKEN),
        })
    return rows


def main(lb_path, usage_path, runs_path, out_json, out_csv):
    evals = {e['modelId']: e for e in json.load(open(lb_path, encoding='utf-8'))['evaluations']}
    usage = list(csv.DictReader(open(usage_path, newline='', encoding='utf-8')))
    runs = {r['session_guid']: r for r in
            csv.DictReader(open(runs_path, newline='', encoding='utf-8'))}

    out = {'constants': {
        'input_usd_per_m': P_INPUT, 'cached_input_usd_per_m': P_CACHED,
        'output_usd_per_m': P_OUTPUT, 'flops_per_token': FLOPS_PER_TOKEN,
        'n_semi_private': N_SEMI_PRIVATE, 'n_public_demo': N_PUBLIC_DEMO,
        'long_context_threshold_tokens': LONG_CONTEXT_THRESHOLD,
    }, 'configurations': {}}
    rows = []

    for harness in ('standard', 'provider_adapter'):
        for effort in EFFORTS:
            sel = [r for r in usage
                   if r['harness'] == harness and r['effort'] == effort]
            if len(sel) != N_PUBLIC_DEMO:
                raise SystemExit(f'{harness}/{effort}: {len(sel)} donor runs, expected {N_PUBLIC_DEMO}')
            I = sum(int(r['input_tokens']) for r in sel)
            K = sum(int(r['cached_tokens']) for r in sel)
            O = sum(int(r['output_tokens']) for r in sel)
            R = sum(int(r['reasoning_tokens']) for r in sel)
            calls = sum(int(r['usage_calls']) for r in sel)
            actions = sum(int(r['actions']) for r in sel)
            kappa, rho = K / I, O / I
            mean_context = I / calls

            wins = [r for r in sel if runs[r['session_guid']]['state'] == 'WIN']
            losses = [r for r in sel if runs[r['session_guid']]['state'] != 'WIN']

            def split(rs):
                if not rs:
                    return None
                i = sum(int(r['input_tokens']) for r in rs)
                k = sum(int(r['cached_tokens']) for r in rs)
                o = sum(int(r['output_tokens']) for r in rs)
                return {'kappa': k / i, 'rho': o / i, 'n': len(rs)}

            ev = evals[lb_model_id(harness, effort)]
            cost = ev['cost']
            central = invert(cost, kappa, rho)

            per_env_counted = central['counted_tokens'] / N_SEMI_PRIVATE
            per_env_flops = central['flops'] / N_SEMI_PRIVATE

            scen = {}
            scen['central'] = central
            scen['arc_priced_cache_reads_at_cached_rate'] = invert(cost, kappa, rho, discounted=True)
            for name, sp in (('kappa_from_won_donor_runs', split(wins)),
                             ('kappa_from_unsolved_donor_runs', split(losses))):
                if sp:
                    scen[name] = invert(cost, sp['kappa'], sp['rho'])
                    scen[name]['donor_runs'] = sp['n']
            for name, params in (('active_parameters_100B', ACTIVE_PARAMS_LOW),
                                 ('active_parameters_600B', ACTIVE_PARAMS_HIGH)):
                scen[name] = dict(central)
                scen[name]['flops'] = central['counted_tokens'] * 2 * params

            # Direct measurement on the donor set, as a cross-check only.
            donor_counted = I - K + O
            out['configurations'][f'{harness}|{effort}'] = {
                'leaderboard_model_id': lb_model_id(harness, effort),
                'leaderboard_score': ev['score'],
                'leaderboard_cost_usd': cost,
                'cost_usd_per_environment': cost / N_SEMI_PRIVATE,
                'donor_public_demo': {
                    'runs': len(sel), 'model_calls': calls, 'actions': actions,
                    'gross_input_tokens': I, 'cached_tokens': K,
                    'output_tokens': O, 'reasoning_tokens': R,
                    'counted_tokens': donor_counted,
                    'counted_tokens_per_environment': donor_counted / N_PUBLIC_DEMO,
                    'kappa_cached_share_of_gross_input': kappa,
                    'rho_output_per_gross_input': rho,
                    'mean_context_tokens_per_call': mean_context,
                    'won': len(wins), 'lost': len(losses),
                    'arc_cost_model_usd': (I * P_INPUT + O * P_OUTPUT) / 1e6,
                    'arc_cost_model_usd_per_environment': (I * P_INPUT + O * P_OUTPUT) / 1e6 / N_PUBLIC_DEMO,
                },
                'semi_private_work_ratio_per_environment': (
                    (cost / N_SEMI_PRIVATE) / ((I * P_INPUT + O * P_OUTPUT) / 1e6 / N_PUBLIC_DEMO)),
                'scenarios': scen,
                'per_environment': {
                    'counted_tokens': per_env_counted,
                    'compute_flops': per_env_flops,
                    'cost_usd': cost / N_SEMI_PRIVATE,
                    'gross_input_tokens': central['gross_input_tokens'] / N_SEMI_PRIVATE,
                    'cached_tokens': central['cached_tokens'] / N_SEMI_PRIVATE,
                    'output_tokens': central['output_tokens'] / N_SEMI_PRIVATE,
                },
                'omitted_attention': attention_scenarios(
                    central['counted_tokens'], central['fresh_input_tokens'],
                    central['output_tokens'], mean_context, kappa),
            }
            rows.append({
                'harness': harness, 'effort': effort,
                'leaderboard_model_id': lb_model_id(harness, effort),
                'rhae': ev['score'], 'cost_usd_total': cost,
                'cost_usd_per_environment': round(cost / N_SEMI_PRIVATE, 4),
                'kappa': round(kappa, 6), 'rho': round(rho, 8),
                'gross_input_tokens_total': round(central['gross_input_tokens']),
                'counted_tokens_total': round(central['counted_tokens']),
                'counted_tokens_per_environment': round(per_env_counted),
                'flops_per_environment': per_env_flops,
                'flops_per_env_cached_rate_scenario':
                    scen['arc_priced_cache_reads_at_cached_rate']['flops'] / N_SEMI_PRIVATE,
                'attention_ratio_mid': round(
                    out['configurations'][f'{harness}|{effort}']['omitted_attention'][1]['ratio_to_recorded'], 4),
            })

    with open(out_json, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1)
    with open(out_csv, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f'{len(rows)} configurations -> {out_json}, {out_csv}')


if __name__ == '__main__':
    if len(sys.argv) != 6:
        raise SystemExit(__doc__)
    main(*sys.argv[1:])
