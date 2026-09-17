#!/usr/bin/env python3
"""Recompute compute_flops, attention_context, attention_ratio and the bar on
the 283 METR source_total rows from METR's own per-run billing.

The dataset measures compute as actually run. METR's `generation_cost` field,
divided by `tokens_count`, gives a billed price per counted token that the
vendor rate cards turn into a bound on the share of counted positions that took
a weights pass. On HCAST the billed price sits at or above the model's uncached
input price on every alias whose rate card is identified, which is what a run
that recomputes its prefix every call costs and what no cache-read share can
produce. So the processed fraction is 1: P = C, not the perfect-caching
P = sqrt(2 C n) the earlier rebuild assumed.

The trajectory length T = min(C, sqrt(2 C n)) at n = 2,800 survives, because n
is the scaffold's per-call cadence and not a caching assumption; with P = C it
no longer touches the weight-matrix term and enters only the attended context,
where it still sets the context band that compute_flops_low and
compute_flops_high carry alongside the parameter band.

Caching is a fact about the run and not an uncertainty. The determination is
committed to per alias and carries no band.

The derivation is research/metr/cache-accounting.md and the review report
agent-work/reviews/metr-billing-rebuild-2026-09-16.md.

Usage: python3 research/metr/metr_billing_rebuild.py [--dry-run]
Run from dataset/. Dependencies: Python 3.9+ standard library only.
"""

import argparse
import csv
import json
import math
import re
import statistics
import sys
from pathlib import Path

DATASET = Path(__file__).resolve().parents[2]
REPO = DATASET.parent
OUT = REPO / "agent-work" / "derived" / "metr-billing"

sys.path.insert(0, str(DATASET / "research" / "attention-correction"))
from architectures import family_for, shape_from_active  # noqa: E402

N_NEW = 2800.0          # trajectory-length constant, unchanged
BETA = 0.3191           # output share of new tokens, Terminal-Bench 2.1 median

# Per-alias processed fraction, as determined. Caching is a fact about the run,
# not an uncertainty: either the scaffold cached or it did not, and the billing
# says which. Damon ruled on 2026-09-16 that the determination is committed to
# and carries no band, so `f` is 1 everywhere and nothing here enters the range.
# `basis` records how each alias was settled.
#
# Only three aliases are billed on the runs the dataset uses. Every alias from
# Time Horizon 1.1's Inspect harness carries no cost record at all, so its
# determination is transferred: caching is requested by the harness, and the
# harness that was billed is Time Horizon 1.0's. The four Inspect aliases whose
# model was billed under 1.0 are transfers on the same footing as the four with
# no billing anywhere, and the notes say so rather than calling them measured.
ALIAS = {
    # alias                                    f    basis
    "GPT-4 0314":                             (1.0, "own billing; no cached tier ever existed for gpt-4-32k"),
    "DeepSeek-R1":                            (1.0, "own billing; inconsistent with any caching"),
    "gpt-oss-120b":                           (1.0, "scaffold transfer, flock-public; own card refuted by its own billing"),
    "GPT-4o (Inspect)":                       (1.0, "vendor transfer, OpenAI post-Oct-2024 aliases"),
    "o1 (Inspect)":                           (1.0, "vendor transfer, OpenAI post-Oct-2024 aliases"),
    "Claude 3.5 Sonnet (New) (Inspect)":      (1.0, "vendor transfer, nine Anthropic aliases"),
    "Claude 3.7 Sonnet (Inspect)":            (1.0, "vendor transfer, nine Anthropic aliases"),
    "GPT-5 (Inspect)":                        (1.0, "vendor transfer, OpenAI post-Oct-2024 aliases"),
    "GPT-5.3-Codex":                          (1.0, "vendor transfer, OpenAI post-Oct-2024 aliases"),
    "Claude Opus 4.6 (Inspect)":              (1.0, "vendor transfer, nine Anthropic aliases"),
    "Gemini 3 Pro":                           (1.0, "vendor transfer, Gemini 2.5 Pro Preview"),
}

# The 10th and 90th percentiles of the new-tokens-per-call constant, from the
# sixteen Terminal-Bench 2.1 submissions, as research/compute-range/compute_range.py
# computes them. With P = C the constant no longer touches the weight-matrix
# term; it still sets the trajectory length and so the attended context, which
# is the context band research/compute-range/compute-range.md defines.
N_NEW_LOW, N_NEW_HIGH = 1976.4, 19087.9

# Vendor rate cards used to read the billing, from research/cost/list-prices.csv
# except gpt-4-32k, which list-prices.csv carries at the 8K tier. Columns are
# USD per million tokens: uncached input, cache read, output.
RATE_CARDS = {
    "GPT-4 0314": (60.00, None, 120.00),   # the 32K tier, which the billing fits
    "GPT-4 Turbo": (10.00, None, 30.00),
    "gpt-3.5-turbo-instruct": (1.50, None, 2.00),
    "GPT-4o": (2.50, 1.25, 10.00),
    "o1": (15.00, 7.50, 60.00),
    "o1-preview": (15.00, 7.50, 60.00),
    "Claude 3 Opus": (15.00, 1.50, 75.00),
    "Claude 3.5 Sonnet (Old)": (3.00, 0.30, 15.00),
    "Claude 3.5 Sonnet (New)": (3.00, 0.30, 15.00),
    "Claude 3.7 Sonnet": (3.00, 0.30, 15.00),
    "Claude 4 Sonnet": (3.00, 0.30, 15.00),
    "Claude 4 Opus": (15.00, 1.50, 75.00),
    "Claude 4.1 Opus": (15.00, 1.50, 75.00),
    "Claude Sonnet 4.5": (3.00, 0.30, 15.00),
    "Claude Opus 4.5": (5.00, 0.50, 25.00),
    "DeepSeek-R1": (0.55, 0.14, 2.19),
    "Gemini 2.5 Pro Preview": (1.25, 0.31, 10.00),
    "Grok 4": (3.00, 0.75, 15.00),
    "Kimi K2 Thinking": (0.60, 0.15, 2.50),
    "gpt-oss-120b": (0.15, None, 0.60),
}
# Cards for the aliases that carry no cost record, used to convert a donor's
# observed price ratio into a processed fraction on the alias's own prices.
TRANSFER_CARDS = {
    "GPT-4o (Inspect)": (2.50, 1.25, 10.00),
    "o1 (Inspect)": (15.00, 7.50, 60.00),
    "Claude 3.5 Sonnet (New) (Inspect)": (3.00, 0.30, 15.00),
    "Claude 3.7 Sonnet (Inspect)": (3.00, 0.30, 15.00),
    "GPT-5 (Inspect)": (1.25, 0.125, 10.00),
    "GPT-5.3-Codex": (1.75, 0.175, 14.00),
    "Claude Opus 4.6 (Inspect)": (5.00, 0.50, 25.00),
    "Gemini 3 Pro": (2.00, 0.20, 12.00),
}


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        return r.fieldnames, list(r)


def write_csv(path, fields, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\r\n")
        w.writeheader()
        w.writerows(rows)


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def f_from_ratio(rho, card, beta=BETA):
    """Smallest processed fraction a billed price of rho * p_in tolerates.

    A counted token is fresh input, a cache read or output, in shares u, c and
    o of the counted total C, with u + c + o = 1 and the processed fraction
    f = u + o. The billed price per counted token is

        q = u * p_in + c * p_cache + o * p_out

    Holding the output share of the *new* tokens at the donor beta gives
    o = beta * f, and solving for f gives the expression below. Lower f needs
    higher o, so beta = 1 is the loosest floor and beta = 0 the tightest
    ceiling; the donor median sits between them.
    """
    p_in, p_cache, p_out = card
    if p_cache is None:
        return 1.0      # no cached tier: a re-read prefix costs the input price
    q = rho * p_in
    return min(1.0, (q - p_cache) / (p_in - p_cache + beta * (p_out - p_in)))


def load_runs():
    runs = []
    base = REPO / "agent-work" / "sources" / "metr" / "eval-analysis-public" / "reports"
    for rep in ("time-horizon-1-0", "time-horizon-1-1"):
        p = base / rep / "data" / "raw" / "runs.jsonl"
        if not p.exists():
            return None
        with p.open() as f:
            for line in f:
                runs.append(json.loads(line))
    return runs


def audit():
    """Print the per-alias billing arithmetic the table above rests on."""
    runs = load_runs()
    if runs is None:
        print("exports not on disk; agent-work/sources is gitignored")
        return
    print(f"{'alias':26s} {'runs':>5s} {'q':>9s} {'q/p_in':>7s} {'<p_in':>7s} {'o_nc':>7s} {'f_beta':>7s}")
    stats = {}
    for a, card in RATE_CARDS.items():
        qs = [r["generation_cost"] / r["tokens_count"] * 1e6 for r in runs
              if r.get("alias") == a and r.get("tokens_count") and r.get("generation_cost")
              and r.get("task_source") == "HCAST"]
        if not qs:
            continue
        p_in, p_cache, p_out = card
        q = statistics.median(qs)
        rho = q / p_in
        below = sum(1 for x in qs if x < p_in) / len(qs)
        o_nc = (q - p_in) / (p_out - p_in)
        fl = f_from_ratio(rho, card)
        stats[a] = (rho, fl)
        print(f"{a:26s} {len(qs):5d} {q:9.3f} {rho:7.3f} {below*100:6.1f}% {o_nc:7.4f} {fl:6.3f}")
    anth = [v[0] for k, v in stats.items() if k.startswith("Claude")]
    oai = [stats[k][0] for k in ("GPT-4o", "o1", "o1-preview") if k in stats]
    print("\ndonor price ratios: Anthropic median %.3f over %d aliases; "
          "OpenAI post-Oct-2024 median %.3f over %d; Gemini 2.5 Pro %.3f; Grok 4 %.3f"
          % (statistics.median(anth), len(anth), statistics.median(oai), len(oai),
             stats["Gemini 2.5 Pro Preview"][0], stats["Grok 4"][0]))
    for a, card in TRANSFER_CARDS.items():
        rho = (statistics.median(anth) if "Claude" in a
               else stats["Gemini 2.5 Pro Preview"][0] if "Gemini" in a
               else statistics.median(oai))
        # An Inspect alias takes its vendor's donor ratio even where the same
        # model was billed under Time Horizon 1.0: that is a different harness.
        print(f"transfer {a:34s} rho {rho:.3f} -> f at the donor output share "
              f"{f_from_ratio(rho, card):.3f}, determined 1.000")
    # gpt-oss-120b bills below the only card we have for it, which refutes the
    # card rather than measuring a cache share. Its low end reads that same
    # billing at the Together rate with cache reads taken as free, the most
    # caching any reading of it can support; it lands on Grok 4's figure, the
    # one flock-public alias whose billing does show a discount.
    q = statistics.median([r["generation_cost"] / r["tokens_count"] * 1e6 for r in runs
                           if r.get("alias") == "gpt-oss-120b" and r.get("tokens_count")
                           and r.get("generation_cost") and r.get("task_source") == "HCAST"])
    p_in, _, p_out = RATE_CARDS["gpt-oss-120b"]
    print("gpt-oss-120b at the Together card with cache reads free would give "
          "f %.3f, and Grok 4's own billing gives %.3f. Neither is adopted: the "
          "sub-reference price is better explained by a cheaper provider for an "
          "open-weight model many providers serve than by this one alias caching "
          "under a scaffold that cached nowhere else."
          % (q / (p_in + BETA * (p_out - p_in)), stats["Grok 4"][1]))


def mean_context(C, T, P):
    """Mean attended context over P processed positions of a linear-prefix run.

    Calls k, final length T, prefix T*s at fraction s of the run. Each call
    processes its n new tokens and a share of its prefix; the counted total
    charges the whole prefix. Writing A = P - T for the re-processed prefix
    positions, integrating the per-position context over the run gives

        N_bar = T * (A / 3 + T / 2) / P

    which is T / 2 for a perfectly cached run (A = 0) and T / 3 for one that
    recomputes everything on a run long enough that C >> T.
    """
    A = max(0.0, P - T)
    return T * (A / 3.0 + T / 2.0) / P


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--audit", action="store_true")
    args = ap.parse_args()
    if args.audit:
        audit()
        return

    _, models = read_csv(DATASET / "models.csv")
    pfields, points = read_csv(DATASET / "points.csv")
    by_id = {m["model_id"]: m for m in models}

    records, factors = [], []
    for r in points:
        if r["tokens_accounting"] != "source_total" or \
                "METR/eval-analysis-public" not in r["compute_source"]:
            continue
        m = re.search(r"alias=([^;]+)", r["source_record"])
        alias = m.group(1).strip()
        f_cen, basis = ALIAS[alias]
        model = by_id[r["model_id"]]
        N = float(model["active_parameters"])
        N_lo = num(model["active_parameters_low"])
        N_hi = num(model["active_parameters_high"])
        L = int(model["attention_layers"])
        d = int(model["attention_width"])
        est = model["attention_basis"] == "estimated"
        fam = family_for(model["company"])
        C = float(r["tokens"])
        old_flops = float(r["compute_flops"])
        old_ctx = float(r["attention_context"])

        # Guard: the row must reproduce the rebuild this script replaces.
        T = min(C, math.sqrt(2.0 * C * N_NEW))
        assert abs(old_ctx - T / 2.0) <= 0.005 * old_ctx, r["point_id"]
        implied = old_flops / (1.0 + 2.0 * L * d * old_ctx / N) / (2.0 * N)
        assert abs(implied - T) <= 0.005 * T, r["point_id"]

        def term(n_active, context, proc):
            lay, wid = shape_from_active(n_active, fam) if est else (L, d)
            return 2.0 * n_active * proc + 4.0 * lay * wid * context * proc

        P = max(f_cen * C, T)            # never below the trajectory itself
        ctx = mean_context(C, T, P)
        new_flops = term(N, ctx, P)
        ratio = 2.0 * L * d * ctx / N
        # The bar carries the two uncertainties COLUMNS.md names and nothing
        # else: the parameter band, and the attended-context band the
        # new-tokens-per-call constant sets through the trajectory length. The
        # processed fraction is determined, not banded, so P = C at both ends.
        ends = []
        for n_end in (N_NEW_LOW, N_NEW_HIGH):
            t = min(C, math.sqrt(2.0 * C * n_end))
            ends.append((mean_context(C, t, max(f_cen * C, t)), max(f_cen * C, t)))
        ctx_lo = min(c for c, _ in ends)
        ctx_hi = max(c for c, _ in ends)
        has_param = N_lo is not None and N_hi is not None
        has_context = ctx_hi > ctx_lo * (1.0 + 1e-9)
        if not has_param and not has_context:
            lo = hi = None               # neither uncertainty applies
        else:
            lo = min(term(N_lo if has_param else N, ctx_lo, min(p for _, p in ends)),
                     new_flops)
            hi = max(term(N_hi if has_param else N, ctx_hi, max(p for _, p in ends)),
                     new_flops)

        # A single-call row has P = C at both ends already, so the rebuild is
        # a no-op on it and the cell is left exactly as it stands rather than
        # rewritten at float noise.
        if abs(new_flops / old_flops - 1.0) > 1e-6:
            r["compute_flops"] = repr(new_flops)
            r["attention_context"] = f"{ctx:.6g}"
            r["attention_ratio"] = f"{ratio:.4f}"
            r["compute_flops_low"] = "" if lo is None else repr(lo)
            r["compute_flops_high"] = "" if hi is None else repr(hi)
        factors.append(new_flops / old_flops)
        records.append({
            "point_id": r["point_id"], "alias": alias, "model_id": r["model_id"],
            "source_dataset": r["source_dataset"], "counted_tokens": C,
            "trajectory_length": T, "processed_fraction": f_cen,
            "fraction_basis": basis, "context_low": ctx_lo, "context_high": ctx_hi,
            "processed_positions": P, "attention_context": ctx,
            "attention_ratio": ratio, "compute_flops_before": old_flops,
            "compute_flops": new_flops, "factor": new_flops / old_flops,
            "compute_flops_low": "" if lo is None else lo,
            "compute_flops_high": "" if hi is None else hi,
        })

    if not args.dry_run:
        write_csv(DATASET / "points.csv", pfields, points)
        OUT.mkdir(parents=True, exist_ok=True)
        with (OUT / "rows.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(records[0]), lineterminator="\r\n")
            w.writeheader()
            w.writerows(records)

    moved = [x for x in factors if abs(x - 1.0) > 1e-9]
    print("METR rows: %d   moved: %d   unchanged: %d"
          % (len(records), len(moved), len(factors) - len(moved)))
    print("factor on compute_flops  median %.2f  max %.2f  min %.2f"
          % (statistics.median(moved), max(factors), min(factors)))


if __name__ == "__main__":
    main()
