#!/usr/bin/env python3
"""Terminal-Bench-Science compute: the reconstruction that was considered and not used.

One Terminal-Bench-Science row is built, agen-tbsci-gpt6astra-valsai, and build_rows.py is
its reproduction path: this script does not compute any value that row carries. What it does
compute is the arithmetic behind two claims in research/terminal-bench.md — that the official
tbench.ai board's total_tokens is 98-99% cache reads and cannot support a row of its own, and
that the launch price vector is arithmetically excluded. Probe 1's per-model growth in
cache-read share is the same quantity build_rows.py recomputes for the row's growth factor,
from the same inputs.

Probe 2 is superseded. It inverts the Astra cell from a Gemini 3 Pro Terminus 2 donor under a
single transfer, which was the first submission's method; the built row uses the model's own
Artificial Analysis record and this operator's own Terminal-Bench 2.1 cell as two donors,
with a geometric mean. It is kept because the note cites its figure as the first reading that
was considered.

Two probes:

1. The official tbench.ai board publishes one gross `total_tokens` per model, cache reads
   included. With a price vector and an uncached-to-output ratio transferred from the same
   model's Terminal-Bench 2.1 Codex run, the two equations

       U + C + O = total_tokens
       p_U*U + p_C*C + p_O*O = total_cost_usd

   solve for the counted quantity U + O. Run for the three OpenAI models whose prices are
   documented, at both the current sheet and the July 2026 vector that this board's
   Terminal-Bench 2.1 sibling used, to show that the July vector is arithmetically
   excluded and the current one is internally consistent.

2. (Superseded, see above.) The Vals AI board publishes cost per task and no tokens at all,
   so its GPT-6 Astra cell needs a cache structure as well as an uncached-to-output ratio.
   This probe transfers both from one Terminal-Bench 2.1 Terminus 2 donor under a single
   transfer; the built row does not.

Dependencies: Python 3.9+ standard library only.

Usage:
  python3 tbscience_compute_probe.py --sources agent-work/sources/terminal-bench
"""

import argparse
import csv
import os

# model label on the tbench board -> (tb21 submission model_label, price vectors)
# price vector: (input, cached, output) USD per million.
CURRENT_SHEET = {
    "GPT-5.6 Sol": (4.00, 0.40, 20.00),
    "GPT-5.6 Terra": (2.00, 0.20, 12.00),
    "GPT-5.6 Luna": (0.20, 0.02, 1.20),
}
JULY_VECTOR = {  # reproduces the Terminal-Bench 2.1 board's own reported costs to the cent
    "GPT-5.6 Sol": (5.00, 0.50, 30.00),
    "GPT-5.6 Terra": (2.50, 0.25, 15.00),
    "GPT-5.6 Luna": (1.00, 0.10, 6.00),
}
TB21_DONOR = {  # tb21 submission file supplying the uncached-to-output ratio
    "GPT-5.6 Sol": "2026-07-10-gpt-5-6-sol-max-codex.json",
    "GPT-5.6 Terra": "2026-07-11-openai-gpt-5-6-terra-max-codex.json",
    "GPT-5.6 Luna": "2026-07-11-openai-gpt-5-6-luna-max-codex.json",
}
ASTRA_PRICE = (10.00, 1.00, 50.00)
ASTRA_DONOR = "2026-05-01-gemini-gemini-3-pro-preview-high-terminus-2.json"
ASTRA_COST_PER_TASK = 15.795618
ASTRA_FLOPS_PER_TOKEN = 600e9
TBSCI_TRIALS = 210
TBSCI_TASKS = 70


def read_csv(path):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def solve(total_tokens, cost_usd, prices, k):
    """Return (U, C, O) given U/O = k, or None where the residual is negative."""
    p_u, p_c, p_o = prices
    residual = cost_usd * 1e6 - p_c * total_tokens
    den = p_u * k - p_c * (k + 1) + p_o
    if den <= 0:
        return None
    o = residual / den
    if o <= 0:
        return None
    u = k * o
    return u, total_tokens - u - o, o


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", required=True)
    args = ap.parse_args()
    subs = {r["submission_file"]: r for r in read_csv(os.path.join(args.sources, "tb21-leaderboard-submissions.csv"))}
    board = {r["model_label"]: r for r in read_csv(os.path.join(args.sources, "tbscience-leaderboard-v0-1-eval.csv"))}

    print("Probe 1: tbench.ai board, OpenAI models under Codex")
    print("%-14s %-8s %8s %12s %12s %10s %10s" % ("model", "sheet", "k=U/O", "U+O total", "per trial", "share", "tb21/trial"))
    for label, sheet_name, sheet in [(m, "current", CURRENT_SHEET[m]) for m in CURRENT_SHEET] + \
                                     [(m, "july", JULY_VECTOR[m]) for m in JULY_VECTOR]:
        row = board[label]
        donor = subs[TB21_DONOR[label]]
        k = int(donor["uncached_input_tokens"]) / int(donor["output_tokens"])
        tb21_per_trial = (int(donor["uncached_input_tokens"]) + int(donor["output_tokens"])) / int(donor["n_trials"])
        total = int(row["total_tokens"])
        res = solve(total, float(row["total_cost_usd"]), sheet, k)
        if res is None:
            print("%-14s %-8s %8.3f %12s %12s %10s %10.0f" % (label, sheet_name, k, "negative", "-", "-", tb21_per_trial))
            continue
        u, c, o = res
        print("%-14s %-8s %8.3f %12.0f %12.0f %9.3f%% %10.0f"
              % (label, sheet_name, k, u + o, (u + o) / TBSCI_TRIALS, 100.0 * (u + o) / total, tb21_per_trial))

    print()
    print("Probe 2 (SUPERSEDED by build_rows.py): Vals AI board, GPT-6 Astra, single transfer")
    d = subs[ASTRA_DONOR]
    unc, cac, out = int(d["uncached_input_tokens"]), int(d["cached_input_tokens"]), int(d["output_tokens"])
    k = unc / out
    c_over_u = cac / unc
    p_u, p_c, p_o = ASTRA_PRICE
    # cost per task = (p_u*k*O + p_c*c_over_u*k*O + p_o*O) / 1e6
    o = ASTRA_COST_PER_TASK * 1e6 / (p_u * k + p_c * c_over_u * k + p_o)
    u = k * o
    print("donor %s: cached/uncached %.3f, uncached/output %.3f" % (ASTRA_DONOR, c_over_u, k))
    print("output %.0f, uncached %.0f, cache reads %.0f per task" % (o, u, c_over_u * u))
    print("counted tokens %.0f per task, compute %.3e FLOPs at %.1e per token"
          % (u + o, (u + o) * ASTRA_FLOPS_PER_TOKEN, ASTRA_FLOPS_PER_TOKEN))


if __name__ == "__main__":
    main()
