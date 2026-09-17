#!/usr/bin/env python3
"""Quantify the attention term the 2 x active-parameters convention omits.

Reads the calculations file this study's build script writes and prints, per row,
the omitted attention FLOPs as a multiple of the recorded compute_flops, under two
bracketing architectures.

Recipe (DECISIONS 2026-09-13, the dataset's RULER row): attention costs
4 * L * d_model * N_context FLOPs per processed token, against 2 * active_parameters
for the parameter term, so the ratio is 2 * L * d_model * N_context / active_parameters.

N_context is the mean prefix a processed token attends over. With prompt caching the
processed tokens per trial are exactly the counted quantity (uncached input plus output),
and an append-only agent dialog grows its prefix linearly to that same total, so the
length-weighted mean prefix is half the counted tokens per trial.

Dependencies: Python 3.9+ standard library only.

Usage:
  python3 attention_scenario.py --calculations candidates/terminal-bench/calculations.json
"""

import argparse
import json

# Bracketing shapes by active-parameter class, because a 96-layer 12288-wide bracket is
# not a plausible shape for an 8B-active model. (min active B, low arch, high arch).
ARCH_CLASSES = [
    (100.0, ((64, 8192), (96, 12288))),
    (30.0, ((48, 6144), (64, 8192))),
    (0.0, ((32, 4096), (48, 6144))),
]


def archs_for(active):
    for floor, pair in ARCH_CLASSES:
        if active / 1e9 >= floor:
            return pair
    return ARCH_CLASSES[-1][1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--calculations", required=True)
    args = ap.parse_args()
    data = json.load(open(args.calculations))
    points = list(data["points"])
    if "tbscience_astra" in data:
        a = data["tbscience_astra"]
        points.append({"point_id": a["point_id"],
                       "counted_tokens_per_trial": a["counted_tokens_per_task"],
                       "flops_per_token": a["flops_per_token"]})
    print("%-38s %10s %10s %10s %14s %6s %6s"
          % ("point_id", "active_B", "tokens/tr", "mean_ctx", "arch bracket", "low_x", "high_x"))
    lo_all, hi_all = [], []
    for p in sorted(points, key=lambda r: r["point_id"]):
        tok = p["counted_tokens_per_trial"]
        active = p["flops_per_token"] / 2.0
        ctx = tok / 2.0
        (l1, d1), (l2, d2) = archs_for(active)
        lo = 2.0 * l1 * d1 * ctx / active
        hi = 2.0 * l2 * d2 * ctx / active
        lo_all.append(lo)
        hi_all.append(hi)
        print("%-38s %10.0f %10.0f %10.0f %14s %6.2f %6.2f"
              % (p["point_id"], active / 1e9, tok, ctx,
                 "%d/%d-%d/%d" % (l1, d1, l2, d2), lo, hi))
    print()
    print("across rows: %.2f to %.2f x the recorded compute_flops, one-sided upward"
          % (min(lo_all), max(hi_all)))


if __name__ == "__main__":
    main()
