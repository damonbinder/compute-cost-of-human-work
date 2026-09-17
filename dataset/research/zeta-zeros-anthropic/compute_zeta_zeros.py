#!/usr/bin/env python3
"""Arithmetic for reas-zeta-zeros-anthropic-internal.

Compute: Anthropic published output tokens only (3.1e7). Total processed
positions are (1 + r) x output at the Fermat row's r = 4.21 appended tokens per
output token, then priced at 2 x active_parameters plus the attention term
4 x L x d_attn x context per processed position, per
research/attention-correction.md.

Human: the standing method in research/math-human-time/math-human-time.md --
pages x the size class's hours-per-page rate, with the class's own dispersion as
the range. No formalization term: the Lean artifact is outside the work unit,
because the published token figure does not cover it.

Dependencies: Python 3.9+ standard library only.
"""

import json

# ---------------------------------------------------------------- compute

OUTPUT_TOKENS = 3.1e7          # Anthropic blog, "a total of 31 million output tokens"
R_APPENDED = 4.21              # research/flt-anthropic.md#compute, Meta textbook donor
K = 1.0 + R_APPENDED
TOKENS = K * OUTPUT_TOKENS

ACTIVE = 1.5e11                # research/model-priors/anthropic.md, internal research Claude
ACTIVE_LOW = 5.5e10
ACTIVE_HIGH = 4.0e11
CONTEXT = 1.0e5                # Claude Code agent session, the Fermat row's central
ANTHROPIC_LAYER_SHARE = 0.70   # research/attention-correction.md#model-architectures


def shape_from_active(active, share=ANTHROPIC_LAYER_SHARE):
    """L_dense = (N / 196608)^(1/3); d_attn = 128 * L_dense; L = share * L_dense."""
    dense = max(8, int(round((active / 196608.0) ** (1.0 / 3.0))))
    return max(1, int(round(dense * share))), 128 * dense


def flops(active, tokens, context):
    layers, width = shape_from_active(active)
    params_term = 2.0 * active * tokens
    attn_term = 4.0 * layers * width * context * tokens
    return {
        "active_parameters": active,
        "attention_layers": layers,
        "attention_width": width,
        "params_term": params_term,
        "attention_term": attn_term,
        "total": params_term + attn_term,
        "attention_ratio": 2.0 * layers * width * context / active,
    }


central = flops(ACTIVE, TOKENS, CONTEXT)
low = flops(ACTIVE_LOW, TOKENS, CONTEXT)
high = flops(ACTIVE_HIGH, TOKENS, CONTEXT)

# Scenarios on the input-side reconstruction, at the central parameter count.
scenarios = {}
for name, k in [
    ("output_only_floor", 1.0),
    ("transfer_band_low", 3.0),
    ("donor_append_profile_low", 4.5),
    ("central", K),
    ("donor_append_profile_high", 6.3),
    ("transfer_band_high", 10.0),
]:
    scenarios[name] = {"k": k, "tokens": k * OUTPUT_TOKENS,
                       "compute_flops": flops(ACTIVE, k * OUTPUT_TOKENS, CONTEXT)["total"]}

# ------------------------------------------------------------------ human

PAGES = 21                      # arXiv:2608.13637, Comments field
RATE_MEDIUM = 8.3               # research/math-human-time/math-human-time.md#table1
RATE_MEDIUM_LOW = 1.1
RATE_MEDIUM_HIGH = 20.0

human_hours = PAGES * RATE_MEDIUM
human_hours_low = PAGES * RATE_MEDIUM_LOW
human_hours_high = PAGES * RATE_MEDIUM_HIGH

# What the excluded Lean term would add, reported and not recorded.
LEAN_MACHINE_LINES = 103032     # measured, anthropics/formal-math zeta23/, 16 Sep 2026
LINES_PER_PAPER_PAGE = 417
LINES_PER_HOUR = 12.6
lean_hours_from_pages = PAGES * LINES_PER_PAPER_PAGE / LINES_PER_HOUR
lean_hours_from_machine_lines = LEAN_MACHINE_LINES / LINES_PER_HOUR

out = {
    "compute": {
        "output_tokens": OUTPUT_TOKENS,
        "r_appended": R_APPENDED,
        "k": K,
        "tokens": TOKENS,
        "context": CONTEXT,
        "central": central,
        "low": low,
        "high": high,
        "scenarios": scenarios,
    },
    "human": {
        "pages": PAGES,
        "class": "medium (13-60 pages)",
        "hours": human_hours,
        "hours_low": human_hours_low,
        "hours_high": human_hours_high,
        "seconds": human_hours * 3600,
        "seconds_low": human_hours_low * 3600,
        "seconds_high": human_hours_high * 3600,
        "excluded_lean_hours_from_pages": lean_hours_from_pages,
        "excluded_lean_hours_from_machine_lines": lean_hours_from_machine_lines,
    },
    "ratio_flops_per_human_second": central["total"] / (human_hours * 3600),
}

print(json.dumps(out, indent=2))
