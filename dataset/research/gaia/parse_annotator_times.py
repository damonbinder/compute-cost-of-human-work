#!/usr/bin/env python3
"""Parse the GAIA validation annotators' self-reported solve times into seconds.

Input: the GAIA 2023 validation metadata parquet (columns task_id, Level,
Annotator Metadata), whose 'How long did this take?' field is free text.
Output: a CSV with one row per validation question (task_id, level, raw string,
seconds, parse rule) and a JSON with per-level and overall statistics.

All 165 strings are covered by six rules; every judgment call is recorded in the
``rule`` column so a reviewer can re-decide any of them:
  plain      "5 minutes", "20 Minutes", "30 minutes." -> the stated number
  seconds    "30 seconds"                             -> the stated number
  range      "5-10 minutes"                           -> midpoint of the range
  bare       "6", "10"                                -> read as minutes
  under      "<1 minute"                              -> 30 s, midpoint of 0-60
  few        "a few minutes at most"                  -> 180 s, "a few" = 3

Dependencies: pandas, pyarrow.

Usage:
    python3 parse_annotator_times.py <metadata.parquet> <out.csv> <out_stats.json>
"""
import csv
import json
import re
import statistics
import sys

import pandas as pd


def parse(raw):
    s = (raw or "").strip().rstrip(".").lower()
    m = re.fullmatch(r"(\d+)\s*-\s*(\d+)\s*minutes?", s)
    if m:
        return (int(m.group(1)) + int(m.group(2))) / 2 * 60, "range"
    m = re.fullmatch(r"(\d+)\s*minutes?", s)
    if m:
        return int(m.group(1)) * 60, "plain"
    m = re.fullmatch(r"(\d+)\s*seconds?", s)
    if m:
        return float(m.group(1)), "seconds"
    m = re.fullmatch(r"(\d+)", s)
    if m:
        return int(m.group(1)) * 60, "bare"
    if s == "<1 minute":
        return 30.0, "under"
    if s == "a few minutes at most":
        return 180.0, "few"
    raise ValueError(f"unparsed: {raw!r}")


def main(parquet_path, out_csv, out_stats):
    df = pd.read_parquet(parquet_path)
    rows = []
    for _, r in df.iterrows():
        am = r["Annotator Metadata"] or {}
        raw = am.get("How long did this take?")
        secs, rule = parse(raw)
        rows.append(
            {
                "task_id": r["task_id"],
                "level": int(r["Level"]),
                "raw": raw,
                "seconds": secs,
                "rule": rule,
                "steps": am.get("Number of steps"),
                "n_tools": am.get("Number of tools"),
                "has_file": bool(r["file_name"]),
            }
        )
    with open(out_csv, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    stats = {"n": len(rows)}
    for level in (1, 2, 3, "all"):
        sel = rows if level == "all" else [r for r in rows if r["level"] == level]
        vals = sorted(r["seconds"] for r in sel)
        stats[str(level)] = {
            "n": len(sel),
            "mean_s": statistics.fmean(vals),
            "median_s": statistics.median(vals),
            "min_s": vals[0],
            "max_s": vals[-1],
            "total_s": sum(vals),
            "n_with_file": sum(1 for r in sel if r["has_file"]),
            "rules": {
                k: sum(1 for r in sel if r["rule"] == k)
                for k in sorted({r["rule"] for r in sel})
            },
        }
    with open(out_stats, "w") as fh:
        json.dump(stats, fh, indent=1)
    print(json.dumps(stats, indent=1))


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    main(sys.argv[1], sys.argv[2], sys.argv[3])
