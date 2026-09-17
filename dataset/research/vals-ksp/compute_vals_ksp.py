#!/usr/bin/env python3
"""Vals Time Horizon Index: KSP -- human time per rung and cost-inverted compute.

Reads nothing: every input is a published figure transcribed below, each one
sourced in research/vals-ksp/vals-ksp.md. Writes its tables to
agent-work/derived/vals-ksp/.

Human time: Vals's own interpolation, transcribed from the board bundle
_astro/KSPTimeHorizonIndex.CNaTPLV4.js.

Compute: the board publishes a dollar per whole campaign and no tokens. The
campaign dollar is first prorated to the point at which the model completed its
last whole rung, using the board's own progress series (effective run-time
days), then inverted to counted tokens B = U + O (fresh input plus cache
creation plus output) by carrying a donor run's cache structure:

    alpha = C / B                 cache reads per counted token
    u, beta = U / B, O / B        shares of the counted total
    P_new = u*p_in + beta*p_out   price of a million counted tokens
    P_eff = alpha*p_cached + P_new
    B     = cost * f * 1e6 / P_eff      f = day(rung N) / effective_days

Mean attended context is the donor-implied N_bar = alpha * n_new at the
n_new = 2783 that research/attention-correction.md already uses, not the
200,000 fallthrough cap.
"""

import json
import math
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "..", "..", "agent-work", "derived", "vals-ksp")

# ---------------------------------------------------------------- human time
# Vals's rung table, minutes, from the board bundle. g = {Mun 120, Minmus 31,
# Duna 36, Ike 180}; "Duna landing" is g.Ike + g.Duna.
RUNGS = [("Mun landing", 120),
         ("Mun landing and return", 132),
         ("Minmus landing", 31),
         ("Minmus landing and return", 44),
         ("Duna landing", 180 + 36)]
PCT_PER_RUNG = 100 / 30


def vals_hours(score_pct):
    """Vals's F(): walk the rung table, prorating the last partial rung."""
    n, mins = max(0.0, score_pct) / PCT_PER_RUNG, 0.0
    for _, m in RUNGS:
        d = min(1.0, n)
        mins += m * d
        n -= d
        if n <= 1e-4:
            return mins / 60
    return None


def human_seconds(completed_rungs):
    return sum(m for _, m in RUNGS[:completed_rungs]) * 60


# ------------------------------------------------------------------ the board
# https://www.vals.ai/benchmarks/time_horizon_index, updated 2026-08-20.
BOARD = [
    # slug, model_id, accuracy %, cost_per_test USD, setting
    ("anthropic/claude-opus-5",  "claude-opus-5-max", 13.667, 1308.942459, "compute effort max"),
    ("openai/gpt-5.6-sol",       "gpt-5-6-sol",       13.000,  668.087725, "reasoning effort max"),
    ("anthropic/claude-opus-4-8", "claude-opus-4-8",  11.833, 1499.319504, "compute effort max"),
    ("openai/gpt-5.5",           "gpt-5-5",            8.333,  516.360641, "reasoning effort xhigh"),
    ("grok/grok-4.5",            "grok-4-5",           6.333,  344.035038, "reasoning effort high"),
    ("grok/grok-4.6",            "grok-4-6",           5.833,  225.116660, "reasoning effort high"),
    ("kimi/kimi-k3",             "kimi-k3",            5.167,        None, "no cost published"),
    ("meta/muse_spark_1_1",      None,                 1.667,  144.921195, "reasoning effort xhigh"),
]

# list prices in force on 2026-08-20, USD per million: input, cached, output.
PRICES = {
    "claude-opus-5-max": (5.00, 0.50, 25.00),
    "claude-opus-4-8":   (5.00, 0.50, 25.00),
    "gpt-5-6-sol":       (5.00, 0.50, 30.00),
    "gpt-5-5":           (5.00, 0.50, 30.00),
    "grok-4-5":          (2.00, 0.50,  6.00),
    "grok-4-6":          (2.00, 0.50,  6.00),
}

FLOPS_PER_TOKEN = {
    "claude-opus-5-max": 2.0e11,
    "claude-opus-4-8":   2.0e11,
    "gpt-5-6-sol":       3.0e11,
    "gpt-5-5":           3.46e11,
    "grok-4-5":          2.0e11,
    "grok-4-6":          2.0e11,
}

# attention shape (attention_layers, attention_width) from models.csv
SHAPE = {
    "claude-opus-5-max": (80, 10240, 1.0e11),
    "claude-opus-4-8":   (80, 10240, 1.0e11),
    "gpt-5-6-sol":       (91, 11648, 1.5e11),
    "gpt-5-5":           (96, 12288, 1.73e11),
    "grok-4-5":          (80, 10240, 1.0e11),
    "grok-4-6":          (80, 10240, 1.0e11),
}

# ---------------------------------------------------------------- the donors
# U = fresh input plus cache creation, C = cache reads, O = output.
# Every figure is from dataset/research/terminal-bench.md.
DONORS = {
    "claude-opus-5-max": [
        ("AA Terminus 2, claude-opus-5", 6258841, 126095036, 1333842 + 3102688),
    ],
    "claude-opus-4-8": [
        ("official Claude Code 2.1.205 high", 12873472, 161931526, 8089069),
    ],
    "gpt-5-6-sol": [
        ("AA Terminus 2, gpt-5-6-sol max", 1930620, 29223016, 589903 + 716956),
        ("official Codex 0.144.0 max", 25266704, 540552541, 5935747),
    ],
    "gpt-5-5": [
        ("official Codex 0.125.0 xhigh", 336797311, 392433664, 5966373),
    ],
    "grok-4-5": [
        ("official Cursor CLI high", 12570445, 161079936, 4734062),
    ],
    "grok-4-6": [
        ("AA Terminus 2, grok-4-6 high", 1622674, 73850969, 697912 + 992376),
    ],
}

# GPT-5.5 has one donor and it is the Codex 0.125.0 run whose own note records
# that its counted tokens are largely repeated re-prefill rather than a cached
# dialog (n_new inverts to 179,554 against a 2,783 median). The Sol Codex
# structure at GPT-5.5 prices is carried as its named alternative.
ALTERNATES = {
    "gpt-5-5": [("Sol Codex structure at GPT-5.5 prices",
                 25266704, 540552541, 5935747)],
}

CAP = 200000   # attention_context cap, research/attention-correction.md
N_NEW = 2783   # mean new tokens per call, research/attention-correction.md

# Progress series, from the board bundle _astro/series.BVd8p07A.js, retained as
# research/vals-ksp/ksp-series.json. day at which each model completed its last
# whole rung, and its effective run time, both in 24-hour units.
PRORATE = {
    "claude-opus-5-max": (1.0417, 5.0),
    "gpt-5-6-sol":       (0.7083, 5.0),
    "claude-opus-4-8":   (3.5545, 5.0),
    "gpt-5-5":           (1.8440, 5.0),
    "grok-4-5":          (0.0813, 5.0),
    "grok-4-6":          (1.3750, 5.0),
}

# alpha used for the attention context. Five models take their own donor's.
# GPT-5.5's own donor re-prefilled rather than cached, so its alpha of 1.145 is
# a harness artifact and returns a 3,187-token context for a 120-hour OpenCode
# session; the sibling GPT-5.6 Sol Codex alpha is used instead. Stated in the
# note and in the row.
CONTEXT_ALPHA = {"gpt-5-5": 17.3239}


def invert(cost, prices, U, C, O):
    B = U + O
    alpha, u, beta = C / B, U / B, O / B
    p_in, p_cached, p_out = prices
    P_new = u * p_in + beta * p_out
    P_eff = alpha * p_cached + P_new
    return {"alpha": alpha, "u": u, "beta": beta, "P_new": P_new,
            "P_eff": P_eff, "tokens": cost * 1e6 / P_eff}


def main():
    rows, lines = [], []
    lines.append("score -> Vals expert-human hours (F), and completed rungs\n")
    for slug, mid, acc, cost, setting in BOARD:
        n = acc / PCT_PER_RUNG
        done = int(math.floor(n + 1e-6))
        lines.append("%-24s %6.3f%%  rungs %.4f  completed %d  "
                     "F=%.4f h  unit=%d s"
                     % (slug, acc, n, done, vals_hours(acc),
                        human_seconds(done)))
    lines.append("")

    for slug, mid, acc, cost, setting in BOARD:
        if mid is None or cost is None:
            continue
        done = int(math.floor(acc / PCT_PER_RUNG + 1e-6))
        if done < 1:
            continue
        day, eff = PRORATE[mid]
        f = day / eff
        readings = []
        for label, U, C, O in DONORS[mid] + ALTERNATES.get(mid, []):
            r = invert(cost * f, PRICES[mid], U, C, O)
            r["label"] = label
            r["primary"] = label not in [a[0] for a in ALTERNATES.get(mid, [])]
            readings.append(r)
        prim = [r for r in readings if r["primary"]]
        lo = min(x["tokens"] for x in prim)
        hi = max(x["tokens"] for x in prim)
        tokens = math.sqrt(lo * hi)          # geometric mean of the extremes
        L, d, Nact = SHAPE[mid]
        alphas = [x["alpha"] for x in prim]
        alpha_c = CONTEXT_ALPHA.get(mid, math.exp(sum(map(math.log, alphas))
                                                  / len(alphas)))
        ctx = min(CAP, tokens / 2, alpha_c * N_NEW)
        ratio = 2 * L * d * ctx / Nact
        flops = tokens * FLOPS_PER_TOKEN[mid] * (1 + ratio)
        rows.append({"model_id": mid, "slug": slug, "setting": setting,
                     "accuracy_pct": acc, "cost_usd": cost,
                     "rung_day": day, "effective_days": eff, "prorate": f,
                     "cost_prorated": cost * f, "context_alpha": alpha_c,
                     "completed_rungs": done,
                     "human_seconds": human_seconds(done),
                     "vals_hours_at_score": vals_hours(acc),
                     "tokens": tokens, "tokens_low": lo, "tokens_high": hi,
                     "attention_context": ctx, "attention_ratio": ratio,
                     "compute_flops": flops,
                     "flops_param_only": tokens * FLOPS_PER_TOKEN[mid],
                     "readings": [{k: v for k, v in r.items()} for r in readings]})

    lines.append("cost inversion\n")
    for r in rows:
        lines.append("%s  campaign cost $%.2f; rung %d at day %.4f of %.3f -> "
                     "f=%.5f, prorated $%.2f"
                     % (r["model_id"], r["cost_usd"], r["completed_rungs"],
                        r["rung_day"], r["effective_days"], r["prorate"],
                        r["cost_prorated"]))
        for x in r["readings"]:
            lines.append("    %-42s alpha=%8.3f  u=%.4f beta=%.4f  "
                         "P_new=%7.3f P_eff=%8.3f  tokens=%,.0f".replace(",", "")
                         % (x["label"], x["alpha"], x["u"], x["beta"],
                            x["P_new"], x["P_eff"], x["tokens"])
                         + ("" if x["primary"] else "   [alternative]"))
        lines.append("    central tokens %.0f  (band %.0f - %.0f)"
                     % (r["tokens"], r["tokens_low"], r["tokens_high"]))
        lines.append("    N_ctx %.0f (alpha %.3f x %d)  r %.4f  param-only %.4e  "
                     "compute_flops %.6e"
                     % (r["attention_context"], r["context_alpha"], N_NEW,
                        r["attention_ratio"],
                        r["flops_param_only"], r["compute_flops"]))
        lines.append("    human %d s over %d rungs; FLOPs per human second %.3e"
                     % (r["human_seconds"], r["completed_rungs"],
                        r["compute_flops"] / r["human_seconds"]))
        lines.append("")

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "vals-ksp-calculations.txt"), "w") as f:
        f.write("\n".join(lines))
    with open(os.path.join(OUT, "vals-ksp-rows.json"), "w") as f:
        json.dump(rows, f, indent=1)
    print("\n".join(lines))


if __name__ == "__main__":
    main()
