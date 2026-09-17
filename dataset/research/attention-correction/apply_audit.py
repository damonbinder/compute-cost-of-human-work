#!/usr/bin/env python3
"""Apply the attention audit: per-family closed-model shapes and the context cap.

Two changes, both recomputed through the recipe of
research/attention-correction.md rather than applied as a multiplier.

1. The dense bracket for `attention_basis = estimated` models becomes a
   per-family full-attention layer count, `L = share * (N / 196608)^(1/3)` with
   the width unchanged. models.csv `attention_layers` moves for every closed
   model; the small dense research models keep the plain rule.
2. `attention_context` is held at 200,000 on the SWE-Marathon rows, whose
   measured gross-tokens-over-turns figure runs to 575,020 on harnesses the
   block's own note shows compacting.

Both move `attention_ratio` and `compute_flops` on every affected row. The row
is decomposed the way research/compute-range/compute_range.py decomposes it —
an attention term, a weight-matrix term, and on a few operation_count rows a
remainder that is neither — and rebuilt at the new shape and context.

Usage: python3 research/attention-correction/apply_audit.py [--dry-run]
Run from dataset/. Dependencies: Python 3.9+ standard library only.
"""

import argparse
import csv
import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from architectures import DISCLOSED, family_for, shape_from_active  # noqa: E402

DATASET = Path(__file__).resolve().parents[2]
REPO = DATASET.parent
OUT = REPO / "agent-work" / "derived" / "attention-correction"

CONTEXT_CAP = 200000
CAPPED_SOURCES = {"SWE-Marathon v1.1"}

# operation_count rows applying the shared 2 * N_active coefficient to a text
# backbone, as in research/compute-range/compute_range.py.
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

# operation_count training rows whose every counted position belongs to the
# row's own model at one context, so the whole figure scales like a
# params_tokens row. research/attention-correction.md#training-rows.
SINGLE_MODEL_OPERATION_ROWS = {
    "agen-codexfer-codex300m",
    "agen-codexfer-codex2p5b",
    "agen-codexfer-codex12b",
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


def sig(x, n=4):
    return float("%.*g" % (n, x))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    mfields, models = read_csv(DATASET / "models.csv")
    pfields, points = read_csv(DATASET / "points.csv")

    shape_change = {}
    for m in models:
        if m["attention_basis"] != "estimated" or m["model_id"] in DISCLOSED:
            continue
        active = num(m["active_parameters"])
        if active is None:
            continue
        fam = family_for(m["company"])
        layers, width = shape_from_active(active, fam)
        old_l, old_w = int(m["attention_layers"]), int(m["attention_width"])
        if (layers, width) != (old_l, old_w):
            shape_change[m["model_id"]] = (old_l, old_w, layers, width, fam)
            m["attention_layers"] = str(layers)
            m["attention_width"] = str(width)

    by_id = {m["model_id"]: m for m in models}
    records = []
    for r in points:
        ctx_old = num(r["attention_context"])
        if ctx_old is None:
            continue
        model = by_id.get(r["model_id"])
        if model is None:
            continue
        active = num(model["active_parameters"])
        old_l, old_w = None, None
        if r["model_id"] in shape_change:
            old_l, old_w = shape_change[r["model_id"]][0], shape_change[r["model_id"]][1]
        else:
            old_l, old_w = int(model["attention_layers"]), int(model["attention_width"])
        new_l, new_w = int(model["attention_layers"]), int(model["attention_width"])

        ctx_new = ctx_old
        if r["source_dataset"] in CAPPED_SOURCES and ctx_old > CONTEXT_CAP:
            ctx_new = float(CONTEXT_CAP)
        if (old_l, old_w) == (new_l, new_w) and ctx_new == ctx_old:
            continue

        flops = num(r["compute_flops"])
        r_old = 2.0 * old_l * old_w * ctx_old / active
        r_new = 2.0 * new_l * new_w * ctx_new / active

        if r["compute_method"] == "params_tokens" or \
                r["point_id"] in SINGLE_MODEL_OPERATION_ROWS:
            weights = flops / (1.0 + r_old)
            processed = weights / (2.0 * active)
            other = 0.0
        elif r["point_id"] in OPERATION_COUNT_TEXT_ROWS:
            processed = num(r["tokens"])
            attention = 4.0 * old_l * old_w * ctx_old * processed
            weights = min(2.0 * active * processed, flops - attention)
            other = flops - attention - weights
        else:
            raise SystemExit("unhandled row " + r["point_id"])

        new_flops = other + 2.0 * active * processed * (1.0 + r_new)
        records.append(dict(
            point_id=r["point_id"], source_dataset=r["source_dataset"],
            model_id=r["model_id"], family=family_for(model["company"]),
            layers_before=old_l, layers_after=new_l, attention_width=new_w,
            attention_context_before=ctx_old, attention_context_after=ctx_new,
            attention_ratio_before=r_old, attention_ratio_after=r_new,
            compute_flops_before=flops, compute_flops_after=new_flops,
            factor=new_flops / flops))
        if ctx_new != ctx_old:
            r["attention_context"] = repr(float(ctx_new))
        r["attention_ratio"] = repr(sig(r_new))
        r["compute_flops"] = repr(new_flops)

    if not args.dry_run:
        write_csv(DATASET / "models.csv", mfields, models)
        write_csv(DATASET / "points.csv", pfields, points)
        OUT.mkdir(parents=True, exist_ok=True)
        with (OUT / "audit-corrections.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(records[0]), lineterminator="\r\n")
            w.writeheader()
            w.writerows(records)
        json.dump({
            "models_reshaped": len(shape_change),
            "rows_changed": len(records),
            "context_cap": CONTEXT_CAP,
            "capped_sources": sorted(CAPPED_SOURCES),
            "by_family": Counter(v[4] for v in shape_change.values()),
            "factor_median": statistics.median(x["factor"] for x in records),
        }, (OUT / "audit-run.json").open("w"), indent=1)

    fams = Counter(v[4] for v in shape_change.values())
    print("models reshaped:", len(shape_change), dict(fams))
    print("rows changed:", len(records))
    by_src = defaultdict(list)
    for x in records:
        by_src[x["source_dataset"]].append(x["factor"])
    for s, fs in sorted(by_src.items(), key=lambda kv: -len(kv[1]))[:14]:
        print("  %-52s %4d  median x%.3f" % (s[:52], len(fs), statistics.median(fs)))
    print("overall median factor %.3f" % statistics.median(x["factor"] for x in records))


if __name__ == "__main__":
    main()
