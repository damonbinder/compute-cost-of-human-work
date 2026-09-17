#!/usr/bin/env python3
"""Derive the `frontier` tag of points.csv from `task_id`.

One task often appears as several rows, one per model or per model
configuration. `task_id` says which rows are the same task; this module picks
the one row per task that is the frontier, and `frontier` records the choice.

The rule, ruled by Damon on 2026-09-16:

  * The frontier row is the cheapest `match` row of the task. Match is the
    target, not the ceiling: a cheaper `below` row does not win, and an `above`
    row does not outrank a `match` row.
  * A task with no `match` row takes the cheapest `above` row.
  * A task whose rows are all `below` (or otherwise carry no `match` or `above`
    row) has no frontier row: every row is tagged `no`.
  * A task whose rows disagree on `human_time` is not eligible at all: every
    row is left blank, pending a separate ruling.

Ties on `compute_flops` within the winning label go to the lexicographically
smallest `point_id`, so the tag is a function of the data alone.

Usage:
  python3 research/frontier/frontier.py --check    report the derived tag against the file
  python3 research/frontier/frontier.py --write    write the derived tag into points.csv
  python3 research/frontier/frontier.py --seed-task-ids
                                                   fill blank task_id cells from the task name

Run from dataset/, or pass the dataset directory as the last argument. A run
summary is written to agent-work/derived/frontier/run.json.
"""

import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

WINNING_LABELS = ("match", "above")


def group_key(row):
    """Task identity. Rows sharing a `task_id` are the same task."""
    return row["task_id"]


def derive(rows):
    """Return {point_id: frontier value} plus a per-task record of the choice.

    The record is a dict of task_id -> {"rows", "winner", "label", "status"},
    where status is one of `frontier`, `no_frontier` or `human_time_varies`.
    """
    groups = defaultdict(list)
    for row in rows:
        groups[group_key(row)].append(row)

    tags, record = {}, {}
    for task_id, members in groups.items():
        times = {m["human_time"] for m in members}
        if len(times) > 1:
            record[task_id] = {"rows": len(members), "winner": None,
                               "label": None, "status": "human_time_varies",
                               "human_times": sorted(times)}
            for m in members:
                tags[m["point_id"]] = ""
            continue
        winner = None
        for label in WINNING_LABELS:
            candidates = [m for m in members
                          if m["performance_vs_human"] == label]
            if candidates:
                best = min(float(m["compute_flops"]) for m in candidates)
                winner = sorted((m for m in candidates
                                 if float(m["compute_flops"]) == best),
                                key=lambda m: m["point_id"])[0]
                break
        for m in members:
            tags[m["point_id"]] = "yes" if m is winner else "no"
        record[task_id] = {
            "rows": len(members),
            "winner": winner["point_id"] if winner else None,
            "label": winner["performance_vs_human"] if winner else None,
            "status": "frontier" if winner else "no_frontier",
        }
    return tags, record


def mismatches(rows):
    """Point IDs whose recorded `frontier` differs from the derived value."""
    tags, _ = derive(rows)
    return [(r["point_id"], r["frontier"], tags[r["point_id"]])
            for r in rows if r["frontier"] != tags[r["point_id"]]]


def slug(task):
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", task.lower())).strip("-")


def read_points(path):
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def write_points(path, heads, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, heads, lineterminator="\r\n")
        writer.writeheader()
        writer.writerows(rows)


def main(argv):
    mode = next((a for a in argv[1:] if a.startswith("--")), "--check")
    positional = [a for a in argv[1:] if not a.startswith("--")]
    base = Path(positional[0]) if positional else Path.cwd()
    if not (base / "points.csv").is_file():
        base = Path(__file__).resolve().parents[2]
    path = base / "points.csv"
    heads, rows = read_points(path)

    if mode == "--seed-task-ids":
        by_slug = {r["task_id"]: r["task"] for r in rows if r["task_id"]}
        filled = 0
        for r in rows:
            if not r["task_id"]:
                r["task_id"] = slug(r["task"])
                filled += 1
            by_slug.setdefault(r["task_id"], r["task"])
        write_points(path, heads, rows)
        print(json.dumps({"seeded": filled}, indent=2))
        return 0

    tags, record = derive(rows)
    if mode == "--write":
        for r in rows:
            r["frontier"] = tags[r["point_id"]]
        write_points(path, heads, rows)

    bad = mismatches(rows)
    summary = {
        "points": len(rows),
        "tasks": len(record),
        "tasks_with_frontier": sum(1 for v in record.values()
                                   if v["status"] == "frontier"),
        "tasks_no_frontier": sum(1 for v in record.values()
                                 if v["status"] == "no_frontier"),
        "tasks_human_time_varies": sum(1 for v in record.values()
                                       if v["status"] == "human_time_varies"),
        "rows_yes": sum(1 for v in tags.values() if v == "yes"),
        "rows_no": sum(1 for v in tags.values() if v == "no"),
        "rows_blank": sum(1 for v in tags.values() if v == ""),
        "frontier_by_label": {
            label: sum(1 for v in record.values() if v["label"] == label)
            for label in WINNING_LABELS},
        "mismatches": len(bad),
    }
    out = base.parent / "agent-work" / "derived" / "frontier"
    if out.parent.is_dir():
        out.mkdir(parents=True, exist_ok=True)
        (out / "run.json").write_text(
            json.dumps({"summary": summary, "tasks": record}, indent=2,
                       sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    for point_id, recorded, derived_value in bad[:20]:
        print("  %s: recorded %r, derived %r"
              % (point_id, recorded, derived_value))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
