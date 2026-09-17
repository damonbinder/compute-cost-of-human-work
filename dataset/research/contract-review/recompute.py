#!/usr/bin/env python3
"""Contract-review cost-bound estimate. Standard library only; no model call."""
import argparse
import hashlib
import json
from decimal import Decimal
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--sources', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
s, o = a.sources.resolve(), a.output.resolve()
if o.exists() or o == s or s in o.parents:
    raise SystemExit('Output must be new and outside sources')
for f in json.loads((s / 'manifest.json').read_text()):
    assert hashlib.sha256((s / f['path']).read_bytes()).hexdigest() == f['sha256'], f['path']

x = json.loads((s / 'reported-inputs.json').read_text())
pr = json.loads((s / 'pricing-and-limit.json').read_text())
diagnostic_prices = json.loads((s / 'review-pricing-evidence.json').read_text())
D = lambda value: Decimal(str(value))
c = D(x['mean_api_usd'])
pi = D(pr['pricing']['input_usd_per_token'])
po = D(pr['pricing']['output_usd_per_token'])
cap = D(pr['output_limit']['max_output_tokens'])
coef = D(550000000000)

# Assumed split informed by the whole-document/16K comparison setup and the
# explanatory checklist output. This is not native usage or a midpoint prior.
output = D(3500)
inp = (c - output * po) / pi
n = inp + output
assert (inp, output, n) == (D(14500), D(3500), D(18000))

scenarios = {}
for ot in (0, 1000, 2048, 3000, 3500, 4096):
    ot = D(ot)
    it = (c - ot * po) / pi
    scenarios[str(ot)] = dict(input_tokens=it, output_tokens=ot, tokens=it + ot, flops=(it + ot) * coef)

# Same assumed input scale, different inferred outputs: a plausibility check,
# not a claim that source prompts/tokenizers or native outputs were identical.
diagnostics = {}
for model, prices in diagnostic_prices['models'].items():
    ot = (D(prices['reported_mean_cost_usd']) - inp * D(prices['input_usd_per_token'])) / D(prices['output_usd_per_token'])
    diagnostics[model] = dict(assumed_input_tokens=inp, inferred_output_tokens=ot, total_tokens=inp + ot)

result = dict(
    tokens=n,
    compute_flops=n * coef,
    human_time=D(x['human_mean_minutes']) * 60,
    input_tokens=inp,
    assumed_output_tokens=output,
    coefficient=coef,
    conditional_single_response_scenarios=scenarios,
    original_midpoint_alternative=scenarios['2048'],
    cross_model_diagnostics=diagnostics,
    unconstrained_price_only_tokens=[c / po, c / pi],
    rounded_cost_token_bounds=[(D('.245') - cap * po) / pi + cap, D('.255') / pi],
    active_parameter_scenarios=[n * coef / 2, n * coef * 2],
    one_unreported_duplicate_request_flops=2 * n * coef,
)

def json_number(value):
    if isinstance(value, Decimal):
        return int(value) if value == value.to_integral_value() else float(value)
    raise TypeError(type(value).__name__)

text = json.dumps(result, indent=2, default=json_number) + '\n'
o.parent.mkdir(parents=True, exist_ok=True)
o.write_text(text)
print(text)
