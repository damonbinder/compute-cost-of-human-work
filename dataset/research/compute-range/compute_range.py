#!/usr/bin/env python3
"""Write compute_flops_low and compute_flops_high into points.csv.

The bar combines exactly two named uncertainties and nothing else: the model's
active-parameter range from models.csv, and the attended-context range that
follows from the new-tokens-per-call constant. Everything is recomputed through
the recipe of research/attention-correction.md rather than applied as a single
multiplier, because the attention shape of an `estimated` model is itself a
function of the active-parameter count.

    compute_flops = other + 2 * N_active * P  +  4 * L * d_attn * N_bar * P

    low  = other + 2 * N_low  * P  +  4 * L(N_low)  * d(N_low)  * N_bar_low  * P
    high = other + 2 * N_high * P  +  4 * L(N_high) * d(N_high) * N_bar_high * P

On the 283 METR source_total rows the constant also sets the processed-position
count, P = min(C, sqrt(2 * C * n)) with N_bar = P / 2, so each end reruns that
rebuild and the bounds are the extremes over the two ends.

The derivation, the percentiles of the constant and what the bar does not cover
are in research/compute-range/compute-range.md.

Usage: python3 research/compute-range/compute_range.py [--dry-run]
Run from dataset/. Dependencies: Python 3.9+ standard library only.
"""

import argparse
import csv
import json
import math
import statistics
import sys
from pathlib import Path

DATASET = Path(__file__).resolve().parents[2]
REPO = DATASET.parent
HERE = Path(__file__).resolve().parent
OUT = REPO / "agent-work" / "derived" / "compute-range"

sys.path.insert(0, str(DATASET / "research" / "attention-correction"))
from architectures import attention_shape, family_for, shape_from_active  # noqa: E402

NOTE = "research/compute-range/compute-range.md"

# Largest mean attended context any row may assume, as in
# research/attention-correction.md. The bar respects it on both sides.
CONTEXT_CAP = 200000

# The sixteen official Terminal-Bench 2.1 leaderboard submissions, the only
# agent runs in the collection publishing uncached_input_tokens,
# cached_input_tokens and output_tokens per trial. Inverting
#     n = P^2 / (2 * C_cache),  P = (uncached + output) / trials,
#     C_cache = cached / trials
# on each gives the spread of the new-tokens-per-call constant. C_cache is the
# cache reads alone, matching the definition of alpha = C_cache / P used
# everywhere else; an earlier build put P + cached/trials here, which is not the
# same quantity and understated every value by (alpha + 1) / alpha. The
# consistent median is 3,041 against 2,783, a 9.3% move, so the 2,800 central
# stands; the percentiles below are the consistent ones.
# Fields: label, uncached_input, cached_input, output, n_trials.
TB21_SUBMISSIONS = [
    ("anthropic/claude-opus-4-7 max, Claude Code", 31873388, 806584422, 14896548, 447),
    ("anthropic/claude-opus-4-7 max, Terminus 2", 16646631, 336161721, 12451178, 445),
    ("gemini/gemini-3-pro-preview high, Gemini CLI", 47653156, 329123284, 7219388, 445),
    ("gemini/gemini-3-pro-preview high, Terminus 2", 26094316, 89495525, 12862730, 445),
    ("glm-5.1 max, Claude Code", 13570352, 374577728, 10635681, 445),
    ("openai/gpt-5.5 xhigh, Codex", 336797311, 392433664, 5966373, 445),
    ("gemini/gemini-3.1-pro-preview high, Gemini CLI", 44843158, 366583353, 6123596, 445),
    ("gemini/gemini-3.1-pro-preview high, Terminus 2", 27525560, 96199940, 12935831, 445),
    ("anthropic/claude-fable-5 high, Terminus 2", 7874199, 56146091, 7412519, 445),
    ("anthropic/claude-fable-5 xhigh, Claude Code", 20480925, 174066133, 9954945, 445),
    ("anthropic/claude-opus-4-8 high, Claude Code", 12873472, 161931526, 8089069, 445),
    ("anthropic/claude-sonnet-5 high, Claude Code", 20137729, 527220403, 11216322, 445),
    ("cursor/grok-4.5, Cursor CLI", 12570445, 161079936, 4734062, 445),
    ("gpt-5.6-sol max, Codex", 25266704, 540552541, 5935747, 445),
    ("openai/gpt-5.6-luna max, Codex", 40023670, 1376567117, 10628905, 445),
    ("openai/gpt-5.6-terra max, Codex", 29803660, 864130644, 8707506, 445),
]

# The central the file already carries. research/attention-correction.md rounds
# the 2,783 median to 2,800 and the Vals KSP rows use the unrounded 2,783; the
# difference is 0.6% and both sit inside the bar.
N_NEW_CENTRAL = 2800.0

# operation_count rows whose recipe applies the shared 2 * N_active coefficient
# to a text backbone, from research/attention-correction.md. On these the
# parameter-proportional part is 2 * N_active * tokens and whatever else the
# operation count carries (a vision or audio encoder) is held fixed.
OPERATION_COUNT_TEXT_ROWS = {
    "agen-village-web-opus41-first-deployment",
    "agen-village-web-sonnet45-first-deployment",
    "agen-village-gemini25-first-website",
    "agen-village-opus41-connections-prototype",
    "agen-village-opus41-benefits-screener",
    "agen-village-claude37-first-own-site",
    "agen-village-gpt5-first-site",
    "game-factorio-gpt6astra",
    "game-portal-gpt6astra",
    "agen-mlebench-operand-insults",
    "game-pokemon-crystal-gemini3pro-red",
    "perc-ocr-gpt4o-omnidocbench-en",
    "perc-geolocation-fairlocator-gpt4o",
    "perc-imagenet-gpt4o",
    "perc-asr-gpt4o",
    "code-copilot-cups-accepted-completion-2022",
}

NEW_COLUMNS = ["compute_flops_low", "compute_flops_high"]


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        return r.fieldnames, list(r)


def write_csv(path, fields, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\r\n")
        w.writeheader()
        w.writerows(rows)


def num(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def quantile(values, q):
    """Linear interpolation between order statistics, the numpy default."""
    xs = sorted(values)
    pos = q * (len(xs) - 1)
    lo = int(math.floor(pos))
    hi = min(lo + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (pos - lo)


def step_tokens():
    """n_new for each of the sixteen submissions, and its 10th/90th percentile."""
    ns = []
    for label, uncached, cached, output, trials in TB21_SUBMISSIONS:
        p = (uncached + output) / trials
        c_cache = cached / trials
        ns.append((p * p / (2.0 * c_cache), label))
    values = [n for n, _ in ns]
    return ns, quantile(values, 0.10), quantile(values, 0.90)


def fmt(x):
    return repr(float(x))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    per_submission, n_low, n_high = step_tokens()

    _, models = read_csv(DATASET / "models.csv")
    pfields, points = read_csv(DATASET / "points.csv")
    models_by_id = {m["model_id"]: m for m in models}

    alpha = {}
    with (HERE / "cache-alpha.csv").open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            alpha[row["point_id"]] = (float(row["cache_alpha"]), row["alpha_basis"])

    records, blanked = [], 0
    for r in points:
        # cleared, not defaulted: a rerun must not leave a stale bar behind on
        # a row this run decides gets none.
        r["compute_flops_low"] = ""
        r["compute_flops_high"] = ""
        pid = r["point_id"]
        flops = num(r["compute_flops"])
        model = models_by_id.get(r["model_id"])
        if flops is None or model is None:
            blanked += 1
            continue
        active = num(model["active_parameters"])
        n_lo = num(model["active_parameters_low"])
        n_hi = num(model["active_parameters_high"])
        ctx = num(r["attention_context"])
        tokens = num(r["tokens"])

        # --- the attended-context range -------------------------------------
        ctx_lo = ctx_hi = ctx
        ctx_basis = "none"
        if ctx is not None:
            if pid in alpha:
                a, ctx_basis = alpha[pid]
                bound = CONTEXT_CAP
                if tokens:
                    bound = min(bound, tokens / 2.0)
                ctx_lo = min(a * n_low, bound)
                ctx_hi = min(a * n_high, bound)
                # the central must stay inside its own bar
                ctx_lo = min(ctx_lo, ctx)
                ctx_hi = max(ctx_hi, ctx)
                if ctx_hi <= ctx_lo * 1.0001:
                    # both ends are held by the same bound, and what separates
                    # them is the six-significant-figure rounding of the
                    # recorded central. There is no context band here.
                    ctx_lo = ctx_hi = ctx
                    ctx_basis = "bound at both ends"

        # A METR source_total row rebuilt its processed positions from the same
        # constant, so on those the constant moves P as well as the context and
        # both ends are rebuilt rather than rescaled.
        # SWE-Marathon is source_total too and is not rebuilt this way: it
        # measures its turn count per rollout. Requiring both the context and
        # the processed count to reproduce separates the two blocks.
        metr_rebuild = False
        if ctx is not None and tokens and r["tokens_accounting"] == "source_total" \
                and r["compute_method"] == "params_tokens":
            expect = min(tokens, math.sqrt(2.0 * tokens * N_NEW_CENTRAL))
            shape_ratio = 2.0 * int(model["attention_layers"]) * \
                int(model["attention_width"]) * ctx / active
            implied = flops / (1.0 + shape_ratio) / (2.0 * active)
            if abs(ctx - expect / 2.0) <= 0.005 * ctx and \
                    abs(implied - expect) <= 0.005 * expect:
                metr_rebuild = True
                ctx_basis = "metr_rebuild"

        has_context_range = ctx_lo != ctx_hi or metr_rebuild
        has_parameter_range = n_lo is not None and n_hi is not None
        if not has_context_range and not has_parameter_range:
            blanked += 1
            continue

        # --- decompose the central ------------------------------------------
        if r["compute_method"] == "reported":
            blanked += 1
            continue
        if ctx is None:
            # No attention term. An operation_count row without one counts its
            # architecture's products directly and every term of that count is
            # proportional to the parameter count, so the whole figure scales.
            if not has_parameter_range or active is None:
                blanked += 1
                continue
            low = flops * n_lo / active
            high = flops * n_hi / active
            records.append({
                "point_id": pid, "source_dataset": r["source_dataset"],
                "model_id": r["model_id"], "compute_method": r["compute_method"],
                "shape_basis": model["attention_basis"], "ctx_basis": ctx_basis,
                "active_parameters": active, "active_low": n_lo, "active_high": n_hi,
                "attention_context": "", "context_low": "", "context_high": "",
                "processed_positions": "", "other_flops": 0.0,
                "compute_flops": flops, "compute_flops_low": low,
                "compute_flops_high": high, "ratio_high_low": high / low,
            })
            r["compute_flops_low"] = fmt(low)
            r["compute_flops_high"] = fmt(high)
            continue

        layers = int(model["attention_layers"])
        width = int(model["attention_width"])
        basis = model["attention_basis"]
        ratio = 2.0 * layers * width * ctx / active

        if r["compute_method"] == "params_tokens":
            # compute_flops = 2 * N * P * (1 + ratio); P is the effective
            # processed-position count, which equals tokens except on the few
            # rows whose counted total covers a helper model as well.
            weights = flops / (1.0 + ratio)
            processed = weights / (2.0 * active)
            other = 0.0
        elif pid in OPERATION_COUNT_TEXT_ROWS:
            processed = tokens
            attention = 4.0 * layers * width * ctx * processed
            weights = min(2.0 * active * processed, flops - attention)
            other = flops - attention - weights
        else:
            blanked += 1
            continue

        def endpoint(n_active, context, proc):
            if basis == "estimated":
                lay, wid = shape_from_active(n_active, family_for(model["company"]))
            else:
                lay, wid = layers, width
            return other + 2.0 * n_active * proc + \
                4.0 * lay * wid * context * proc

        a_lo = n_lo if has_parameter_range else active
        a_hi = n_hi if has_parameter_range else active
        if metr_rebuild:
            # Rerun the rebuild at each end of the constant. P and the context
            # it implies both move, so both terms are rebuilt; the ends of the
            # bar are the extremes over the two, not the two in order.
            ends = []
            for n in (n_low, n_high):
                pr = min(tokens, math.sqrt(2.0 * tokens * n))
                ends.append((pr / 2.0, pr))
            ctx_lo = min(c for c, _ in ends)
            ctx_hi = max(c for c, _ in ends)
            low = min(endpoint(a_lo, c, p) for c, p in ends)
            high = max(endpoint(a_hi, c, p) for c, p in ends)
        else:
            low = endpoint(a_lo, ctx_lo, processed)
            high = endpoint(a_hi, ctx_hi, processed)
        low = min(low, flops)
        high = max(high, flops)

        r["compute_flops_low"] = fmt(low)
        r["compute_flops_high"] = fmt(high)
        records.append({
            "point_id": pid, "source_dataset": r["source_dataset"],
            "model_id": r["model_id"], "compute_method": r["compute_method"],
            "shape_basis": basis, "ctx_basis": ctx_basis,
            "active_parameters": active, "active_low": a_lo, "active_high": a_hi,
            "attention_context": ctx, "context_low": ctx_lo, "context_high": ctx_hi,
            "processed_positions": processed, "other_flops": other,
            "compute_flops": flops, "compute_flops_low": low,
            "compute_flops_high": high, "ratio_high_low": high / low,
        })

    # The two columns sit immediately after compute_flops, matching COLUMNS.md.
    at = pfields.index("compute_flops") + 1
    for offset, c in enumerate(NEW_COLUMNS):
        if c not in pfields:
            pfields.insert(at + offset, c)

    if not args.dry_run:
        write_csv(DATASET / "points.csv", pfields, points)
        OUT.mkdir(parents=True, exist_ok=True)
        with (OUT / "ranges.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(records[0]), lineterminator="\r\n")
            w.writeheader()
            w.writerows(records)
        json.dump({
            "n_new_central": N_NEW_CENTRAL,
            "n_new_per_submission": {label: n for n, label in per_submission},
            "n_new_median": statistics.median([n for n, _ in per_submission]),
            "n_new_p10": n_low,
            "n_new_p90": n_high,
            "context_cap": CONTEXT_CAP,
            "rows_with_bar": len(records),
            "rows_blank": blanked,
        }, (OUT / "run.json").open("w"), indent=1)

    ratios = [x["ratio_high_low"] for x in records]
    print("n_new  p10 %.1f  median %.1f  p90 %.1f"
          % (n_low, statistics.median([n for n, _ in per_submission]), n_high))
    print("rows with a bar: %d   blank: %d" % (len(records), blanked))
    print("high/low  p10 %.2f  median %.2f  p90 %.2f  max %.2f"
          % (quantile(ratios, 0.10), statistics.median(ratios),
             quantile(ratios, 0.90), max(ratios)))


if __name__ == "__main__":
    main()
