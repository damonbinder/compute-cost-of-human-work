#!/usr/bin/env python3
"""Emit the derived tables research/gaia.md quotes, so they are not typed by hand.

Prints, in order:
  RESULTS      one line per configuration that contributed at least one row,
               over all 165 validation questions, sorted by accuracy
  ATTENTION    the omitted cached-context attention multiple, by primary model
  SELECTION    the kept/dropped split by level, and the correlation between
               accuracy and log10 FLOPs per question across the cells that have
               a coefficient
  CLOSE        the cells kept under the close-calls ruling
  DEDUP        per run, the op-name split and how many usage-bearing parent
               spans were dropped as duplicates

Dependencies: none beyond the standard library.

Usage:
    python3 note_tables.py <build_gaia_table_calc.json> <make_rows_calculations.json> \
        <points.csv> <dispositions.csv> <run_summaries_dir>
"""
import csv
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_rows import AGENT_LABEL, EFFORT, RUN_CODE, RUN_EXCLUSIONS  # noqa: E402

MODEL_NAME = {
    "sonnet37": "Claude 3.7 Sonnet", "sonnet37high": "Claude 3.7 Sonnet",
    "haiku45": "Claude Haiku 4.5", "opus41high": "Claude Opus 4.1",
    "opus41": "Claude Opus 4.1", "opus41think": "Claude Opus 4.1",
    "opus4": "Claude Opus 4", "opus4high": "Claude Opus 4",
    "sonnet45high": "Claude Sonnet 4.5", "sonnet45": "Claude Sonnet 4.5",
    "sonnet45v2": "Claude Sonnet 4.5", "dsr1": "DeepSeek-R1",
    "dsv3": "DeepSeek-V3", "dsv30324v2": "DeepSeek-V3-0324",
    "gemini20flash": "Gemini 2.0 Flash", "gpt41": "GPT-4.1", "gpt5": "GPT-5",
    "o3": "o3", "o3minilow": "o3-mini", "o3minihigh": "o3-mini",
    "o4minihigh": "o4-mini", "o4minilow": "o4-mini",
}


def main(table_calc, row_calc, points_csv, disp_csv, summary_dir):
    runs = {r["run_id"]: r for r in json.load(open(table_calc))["runs"]}
    pts = json.load(open(row_calc))["points"]
    points = list(csv.DictReader(open(points_csv)))
    disp = list(csv.DictReader(open(disp_csv)))
    kept_cfgs = {p["point_id"].rsplit("-", 1)[0] for p in points}

    print("RESULTS")
    print("| Agent | Model | Effort | Accuracy | FLOPs per question | Tokens per question |")
    print("|---|---|---|---:|---:|---:|")
    rows = []
    for rid, run in runs.items():
        if rid in RUN_EXCLUSIONS:
            continue
        ac, mc = RUN_CODE[rid]
        if f"agen-gaia-{ac}-{mc}" not in kept_cfgs:
            continue
        a = run["levels"]["all"]
        rows.append((a["accuracy"], "HAL" if ac == "hal" else "ODR", MODEL_NAME[mc],
                     EFFORT.get(rid, "default").replace(" reasoning effort", ""),
                     a["flops_per_question"], a["counted_tokens_per_question"]))
    for acc, ag, nm, ef, fl, tk in sorted(rows, key=lambda x: -x[0]):
        print(f"| {ag} | {nm} | {ef} | {acc:.3f} | {fl:.2e} | {tk:,.0f} |")

    print()
    print("ATTENTION")
    by_model = {}
    for p in pts:
        m = p["primary_model_id"]
        lo, hi = by_model.get(m, (9e9, 0.0))
        by_model[m] = (min(lo, p["scenario_attention_multiple_low"]),
                       max(hi, p["scenario_attention_multiple_high"]))
    for m, (lo, hi) in sorted(by_model.items()):
        span = f"{lo:.2f}" if abs(hi - lo) < 5e-3 else f"{lo:.2f}–{hi:.2f}"
        print(f"| {m} | {span} |")

    print()
    print("SELECTION")
    kept = {lv: sum(1 for p in points if p["point_id"].endswith(f"-l{lv}"))
            for lv in "123"}
    dropped = {lv: sum(1 for d in disp
                       if d["level"] == lv and d["outcome"] == "not a row")
               for lv in "123"}
    for lv in "123":
        print(f"| Level {lv} | kept {kept[lv]} | dropped {dropped[lv]} | "
              f"of {kept[lv] + dropped[lv]} |")
    xs, ys, lvl = [], [], []
    for rid, run in runs.items():
        if rid in RUN_EXCLUSIONS:
            continue
        for lv in "123":
            d = run["levels"][lv]
            if d["flops_per_question"] > 0:
                xs.append(d["accuracy"])
                ys.append(math.log10(d["flops_per_question"]))
                lvl.append(lv)
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    cov = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    r = cov / math.sqrt(sum((a - mx) ** 2 for a in xs)
                        * sum((b - my) ** 2 for b in ys))
    print(f"| cells with a coefficient | {n} | r(accuracy, log10 FLOPs/question) | {r:+.2f} |")
    keptset = {(p["run_id"], p["level"]) for p in pts}
    for lv in "123":
        gk = [10 ** y for y, l, x in zip(ys, lvl, xs) if l == lv]
        k = [math.log10(p["flops_per_question"]) for p in pts if p["level"] == lv]
        dset = [math.log10(run["levels"][lv]["flops_per_question"])
                for rid, run in runs.items()
                if rid not in RUN_EXCLUSIONS and (rid, lv) not in keptset
                and run["levels"][lv]["flops_per_question"] > 0]
        gm = lambda v: 10 ** (sum(v) / len(v)) if v else float("nan")  # noqa: E731
        print(f"| Level {lv} | kept geometric mean {gm(k):.2e} | "
              f"dropped geometric mean {gm(dset):.2e} | n {len(gk)} |")

    print()
    print("CLOSE")
    print("| ratio | SE of ratio | SEs under the guide | level | accuracy | n | run |")
    print("|---:|---:|---:|:--|---:|---:|---|")
    close = [d for d in disp if d["outcome"] == "row, close call"]
    for d in sorted(close, key=lambda x: -float(x["ratio_to_human"])):
        print(f"| {d['ratio_to_human']} | {d['se_of_ratio']} | "
              f"{d['standard_errors_below_guide']} | {d['level']} | "
              f"{d['accuracy']} | {d['n_questions']} | `{d['run_id']}` |")

    print()
    print("DEDUP")
    print("| Run | usage spans | counted | dropped as parent | op names |")
    print("|---|---:|---:|---:|---|")
    for name in sorted(os.listdir(summary_dir)):
        if not name.endswith(".json") or name.startswith("_"):
            continue
        s = json.load(open(os.path.join(summary_dir, name)))
        cc = s.get("call_counts") or {}
        ops = (s.get("span_breakdown") or {}).get("by_op_name") or {}
        with_usage = sum(v.get("with_usage", 0) for v in ops.values())
        names = "; ".join(
            f"{k} {v.get('counted', 0)} counted, {v.get('dropped_as_parent', 0)} dropped"
            for k, v in ops.items() if v.get("with_usage"))
        print(f"| `{s['config']['run_id']}` | {with_usage} | "
              f"{cc.get('usage_spans_counted', 0)} | "
              f"{cc.get('usage_spans_dropped_as_parent', 0)} | {names} |")


if __name__ == "__main__":
    if len(sys.argv) != 6:
        raise SystemExit(__doc__)
    main(*sys.argv[1:])
