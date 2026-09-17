#!/usr/bin/env python3
"""Fold the attention term into compute_flops, and fix the METR cache over-charge.

Writes dataset/points.csv and dataset/models.csv in place and a run summary to
agent-work/derived/attention-correction/. The recipe, the per-source mean-context
table and the METR treatment are documented in research/attention-correction.md.

Recipe. A processed position costs 2 * active_parameters in the weight matrices
and 4 * L * d_attn * N_ctx in the attention products (PaLM's 12*L*H*Q*T forward
and backward, of which the forward third is 4*L*H*Q*T). With P processed
positions at a mean attended context N_bar,

    attention_flops = 4 * L * d_attn * N_bar * P
    attention_ratio = 2 * L * d_attn * N_bar / active_parameters

Cache reads are keys, not queries: they raise the context every later position
attends over and never take a weights pass. For params_tokens rows the counted
tokens are the processed positions, so the new value is the old one times
(1 + attention_ratio). For the METR source_total rows the counted total includes
cache reads at the full 2N rate, so the parameter term is rebuilt on the implied
processed count instead.

Usage: python3 research/attention-correction/apply_attention.py [--dry-run]
Run from dataset/. Dependencies: Python 3.9+ standard library only.
"""

import argparse
import csv
import json
import math
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from architectures import attention_shape  # noqa: E402

DATASET = Path(__file__).resolve().parents[2]
REPO = DATASET.parent
OUT = REPO / "agent-work" / "derived" / "attention-correction"

NOTE = "research/attention-correction.md"

# Largest mean attended context any row is allowed to assume. The longest
# measured per-call prefixes in the collection are ARC-AGI-3's 125k-146k and the
# ~130,000 of the two Astra game runs; harnesses compact rather than grow past
# that. Rows whose counted tokens would imply more are held here.
CONTEXT_CAP = 200000

# Mean new tokens per model call, used only to split a cache-read-inclusive
# counter into processed positions and cache reads. Median of the sixteen
# official Terminal-Bench 2.1 leaderboard submissions, whose metrics blocks
# carry uncached_input_tokens, cached_input_tokens and output_tokens per trial:
# n_new = P^2 / (2C) with P = uncached + output and C = P + cached.
STEP_TOKENS = 2800

# Mean attended context per processed position, where the source supports a
# figure other than half the counted tokens. Keys are source_dataset values.
SOURCE_CONTEXT = {
    # 1.443e9 gross input over 220 tasks at Artificial Analysis's 60.47 mean
    # turns. Transferred to the original GDPval rows, which are invoice-derived.
    "GDPval": 108500,
    "GDPval / GDPval-AA v2": 108500,
    "GDPval gold subset": 108500,
    # research/gaia.md: measured per-call prefixes of 3.6k-29.7k.
    "GAIA, HAL agent traces": 12000,
    # research/ale-bench.md: 2,727 input plus about 12k output, one-shot.
    "ALE-Bench leaderboard (AtCoder Heuristic Contests)": 9000,
    # research/balrog.md: bounded history window on a 424-token shared prefix.
    "BALROG": 3000,
    # research/arc-agi-3.md: 300 session records, 125k-146k per call.
    "ARC-AGI-3 Semi-Private leaderboard, GPT-6 Astra, September 2026": 135000,
    # research/apex-agents.md: input tokens per run over 40 calls.
    "APEX-Agents, Artificial Analysis implementation": 90731,
    # research/bankertoolbench.md: measured 39.5k and 14.2k prefixes, donor cadence.
    "BankerToolBench, Handshake AI": 118004,
    # research/textquests.md: the prefix re-read on each of ~12,500 calls averages
    # 40,000-51,000 tokens across the four runs.
    "TextQuests": 45000,
    # research/artemis.md brackets the mean prefix at 20k-100k.
    "ARTEMIS live-network penetration test, Stanford Trinity": 50000,
}

# Per-point mean attended context, where the row's own note or work-unit
# structure fixes one that half the counted tokens does not.
POINT_CONTEXT = {
    # Measured ~130,000-token prefix in both Astra game runs.
    "game-factorio-gpt6astra": 130000,
    "game-portal-gpt6astra": 130000,
    # research/meta-textbook.md: 1,645,274 full-prefix calls, mean prompt 50,554
    # and RMS 58,113, so the position-weighted mean context is RMS^2 / (2 * mean).
    "reas-lean-textbook-algcomb-opus45": 33410,
    # research/navier-stokes-openai.md derives a 247,500-token average context
    # from the row's own dialog geometry; above the cap and evidenced, so kept.
    "reas-navier-stokes-openai": 247500,
    # research/flt-anthropic.md: 30k-200k brackets a Claude Code agent session,
    # 100k central.
    "reas-flt-lean-anthropic-internal": 100000,
    # research/lumen.md sets each phase's mean input length per call; these
    # reproduce that note's central per-review attention shares.
    "agen-lumen-d1-gemini31pro": 2747,
    "agen-lumen-d2-gemini31pro": 3357,
    "agen-lumen-d3-gemini31pro": 6943,
    "agen-lumen-d4-gemini31pro": 6790,
    "agen-lumen-d5-gemini31pro": 1984,
    # Work units that are k independent sub-runs, so the counted tokens are k
    # trajectories rather than one: half the per-sub-run share is the context.
    "reas-cf-o3": 9000,                             # 1,162 generated candidates
    "lang-lait-novel-opening-gpt54": 9000,          # 1,449 agent jobs over 15 runs
    "lang-book-coherence-gpt4-inc": 1382,           # 98 annotation records
    "lang-book-coherence-gpt4-hier": 982,           # 98 annotation records
    "agen-ahc058-ale-agent": 9000,                  # ALE-Bench per-call cadence
    "reas-lean-minif2f-deepseekprov2-cot32": 3495,  # 32 proof samples
    "reas-math-minerva62b-majority256": 155,        # 256 sampled solutions
}

# operation_count rows whose recipe applies the shared 2 * active_parameters
# coefficient to a text backbone and says the attention term is left out. Every
# other operation_count row either counts its attention products from the
# architecture already (the encoder and encoder-decoder recipes, RULER, the
# 405B needle row) or uses no language backbone at all.
OPERATION_COUNT_ROWS = {
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

NEW_POINT_COLUMNS = ["attention_context", "attention_ratio"]
NEW_MODEL_COLUMNS = ["attention_layers", "attention_width", "attention_basis"]


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


def fmt(x):
    return repr(float(x))


def sig(x, n=4):
    if x == 0:
        return 0.0
    return round(x, -int(math.floor(math.log10(abs(x)))) + (n - 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    mfields, models = read_csv(DATASET / "models.csv")
    pfields, points = read_csv(DATASET / "points.csv")

    # --- models.csv: attention shape -------------------------------------
    shapes = {}
    for m in models:
        active = num(m["active_parameters"])
        shape = attention_shape(m["model_id"], active)
        if shape is None:
            m["attention_layers"] = "not_applicable"
            m["attention_width"] = "not_applicable"
            m["attention_basis"] = "not_applicable"
            continue
        layers, width, basis = shape
        m["attention_layers"] = str(layers)
        m["attention_width"] = str(width)
        m["attention_basis"] = basis
        shapes[m["model_id"]] = (layers, width, active, basis)
        if NOTE not in m["parameter_source"]:
            m["parameter_source"] = m["parameter_source"].rstrip("; ") + "; " + \
                NOTE + "#model-architectures"
    for c in NEW_MODEL_COLUMNS:
        if c not in mfields:
            mfields.append(c)

    # --- points.csv: fold the attention term in ---------------------------
    changed, skipped, records = [], [], []
    for r in points:
        r.setdefault("attention_context", "")
        r.setdefault("attention_ratio", "")
        pid = r["point_id"]
        method = r["compute_method"]
        eligible = method == "params_tokens" or pid in OPERATION_COUNT_ROWS
        if not eligible:
            continue
        tokens = num(r["tokens"])
        shape = shapes.get(r["model_id"])
        old = num(r["compute_flops"])
        if tokens is None or tokens <= 0 or shape is None or old is None:
            skipped.append((pid, "no token count or no attention shape"))
            continue
        layers, width, active, basis = shape

        # processed positions and the context they attend over
        capped = False
        if r["tokens_accounting"] == "source_total":
            processed = min(tokens, math.sqrt(2.0 * tokens * STEP_TOKENS))
            context = processed / 2.0
        else:
            processed = tokens
            context = POINT_CONTEXT.get(pid, SOURCE_CONTEXT.get(r["source_dataset"]))
            if context is None:
                # the default: an append-only dialog processed once, whose
                # length-weighted mean prefix is half the counted tokens. The
                # cap holds rows whose counted tokens are many trajectories.
                context = tokens / 2.0
                capped = context > CONTEXT_CAP
                context = min(context, CONTEXT_CAP)

        ratio = 2.0 * layers * width * context / active
        attention = 4.0 * layers * width * context * processed
        if r["tokens_accounting"] == "source_total":
            new = 2.0 * active * processed + attention
        else:
            new = old + attention

        r["attention_context"] = fmt(sig(context, 6))
        r["attention_ratio"] = fmt(sig(ratio, 4))
        r["compute_flops"] = fmt(new)
        if NOTE not in r["compute_source"]:
            r["compute_source"] = r["compute_source"].rstrip("; ") + "; " + NOTE
        changed.append(pid)
        records.append({
            "point_id": pid, "source_dataset": r["source_dataset"],
            "model_id": r["model_id"], "compute_method": method,
            "tokens_accounting": r["tokens_accounting"],
            "tokens": tokens, "processed_positions": processed,
            "attention_context": context, "context_capped": capped,
            "attention_layers": layers, "attention_width": width,
            "attention_basis": basis, "active_parameters": active,
            "attention_ratio": ratio, "compute_flops_before": old,
            "compute_flops_after": new, "factor": new / old,
        })
    for c in NEW_POINT_COLUMNS:
        if c not in pfields:
            pfields.append(c)

    if not args.dry_run:
        write_csv(DATASET / "models.csv", mfields, models)
        write_csv(DATASET / "points.csv", pfields, points)
        OUT.mkdir(parents=True, exist_ok=True)
        with (OUT / "corrections.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(records[0]), lineterminator="\r\n")
            w.writeheader()
            w.writerows(records)
        json.dump({"step_tokens": STEP_TOKENS, "context_cap": CONTEXT_CAP,
                   "rows_changed": len(changed), "rows_skipped": skipped},
                  (OUT / "run.json").open("w"), indent=1)

    factors = [x["factor"] for x in records]
    ratios = [x["attention_ratio"] for x in records]
    print("rows changed: %d   skipped: %d" % (len(changed), len(skipped)))
    print("attention_ratio  median %.3f  p25 %.3f  p75 %.3f"
          % (statistics.median(ratios),
             statistics.quantiles(ratios, n=4)[0],
             statistics.quantiles(ratios, n=4)[2]))
    print("factor           median %.3f  min %.3f  max %.3f"
          % (statistics.median(factors), min(factors), max(factors)))
    for pid, why in skipped:
        print("  skipped %s: %s" % (pid, why))


if __name__ == "__main__":
    main()
