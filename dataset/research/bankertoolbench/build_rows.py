#!/usr/bin/env python3
"""Emit the BankerToolBench candidate points.csv from calculations.json.

Dependencies: Python 3.9+ standard library only.

Usage:

  python3 build_rows.py \
      --calculations research/bankertoolbench/calculations.json \
      --columns      COLUMNS.md \
      --out          candidates/bankertoolbench/points.csv

The column order is read from COLUMNS.md so the file cannot drift from the spec.
Numeric fields come from calculations.json; every text field is written here.
"""

import argparse
import csv
import json
import re

POINT_ID = {
    ("claude-opus-4-6", "OpenCode"): "work-btb-opus46-opencode",
    ("claude-opus-4-6", "OpenHands"): "work-btb-opus46-openhands",
    ("gpt-5.2-2025-12-11", "OpenCode"): "work-btb-gpt52-opencode",
    ("gpt-5.2-2025-12-11", "OpenHands"): "work-btb-gpt52-openhands",
}

MODEL_LABEL = {"claude-opus-4-6": "Claude Opus 4.6", "gpt-5.2-2025-12-11": "GPT-5.2"}

# What the harness code actually establishes, which differs by provider. Both
# harnesses set Anthropic cache_control breakpoints and both list claude-opus-4-6
# among the models they set them for. Neither sets any breakpoint for an OpenAI
# model: OpenHands gates its breakpoint pass on an Anthropic-only model list and
# OpenCode's provider options carry no native openai key. OpenAI's cache is
# automatic instead, which is the DECISIONS.md default-on caching case.
CACHE_CLAIM = {
    "claude-opus-4-6": "both harnesses set Anthropic cache breakpoints",
    "gpt-5.2-2025-12-11": "OpenAI caches automatically and neither harness disables it",
}

DONOR_LABEL = {
    "agen-epoch-swebench-opus46cc": "the Epoch SWE-bench Claude Code run of this model's",
    "agen-epoch-swebench-gpt52high": "the Epoch SWE-bench run of this model's",
}

TASK_DESCRIPTION = (
    "Complete one BankerToolBench task, as the mean over its 100 junior-banker workflows: a "
    "senior banker's request, a data room of Excel, PDF and PowerPoint files, SEC "
    "filings and market-data tools frozen to its historical date, no internet, and LibreOffice "
    "and Python in a sandbox. Output is the multi-file deliverable asked for, typically an Excel "
    "valuation, merger or LBO model plus a pitch deck or memo. Mix 62% M&A, 19% leveraged "
    "finance, 16% capital markets. Done when it satisfies the task's banker-written rubric, 150 "
    "weighted binary criteria on average."
)

HUMAN_TIME_SOURCE = (
    "https://arxiv.org/abs/2604.11304 v1 Section 3.1, Table 1 note and Sections 4.2 to 4.4; "
    "research/bankertoolbench.md#human-time"
)


def performance_evidence(score, sd):
    return (
        "Weighted rubric Score {score} of 100 over the 100 tasks, mean of 3 runs, SD {sd}. "
        "The human baseline is the banker's own expected deliverable, the benchmark's reference, "
        "reviewed to top-banker standard and taken as 100 by construction; it was never "
        "verifier-scored. A no-file agent scores 0. The thresholded Pass Rate tops out at 16%."
    ).format(score=("%.1f" % score), sd=("%.1f" % sd))


def notes(r, pid):
    donor = DONOR_LABEL[r["donor"]["run"]]
    scen = r["scenarios"]
    lo = min(1.0, scen["alternate_donor"]["ratio_to_central"], scen["uncensored_only_donor"]["ratio_to_central"])
    hi = max(scen["alternate_donor"]["ratio_to_central"], scen["uncensored_only_donor"]["ratio_to_central"])
    att = sorted(v / r["compute_flops"] for v in r["attention_omitted"]["by_architecture"].values())
    return (
        "Compute inverts the paper's only compute figure, the mean ${cost:.2f} per run, at list "
        "prices from {start}. Billed units are the geometric mean of two transfers of {donor} cache "
        "structure: its dollars per billed unit ({a:,.0f}) and its per-call prefix and cadence at "
        "this cell's {rt:.0f} s runtime ({b:,.0f}); alpha {al:.1f} over {calls:.0f} calls. Donor "
        "variants move it {lo:.2f}x to {hi:.2f}x, the no-cache-read ceiling {ceil:.2f}x; {cache}. "
        "The verifier's $0.495 per task is excluded as evaluation. Omitted attention adds "
        "{att0:.1f}x to {att1:.1f}x."
    ).format(
        cost=r["cost_per_run_usd"], start=r["price_sheet_start"], donor=donor,
        a=r["transfer_cost"]["billed_units"], rt=r["runtime_s"],
        b=r["transfer_cadence"]["billed_units"], al=r["central_alpha"],
        calls=r["central_calls_per_run"], lo=lo, hi=hi,
        ceil=scen["no_cache_reads_upper_bound"]["ratio_to_central"],
        cache=CACHE_CLAIM[r["model_id"]], att0=att[0], att1=att[-1],
    )


def source_record(r, pid):
    return (
        "https://arxiv.org/abs/2604.11304 v1 Table 4 and Section B.2, {model} in the {harness} "
        "harness under Harbor, 100 tasks x 3 runs; "
        "https://github.com/Handshake-AI-Research/bankertoolbench; "
        "https://huggingface.co/datasets/handshake-ai-research/bankertoolbench; "
        "agent-work/sources/bankertoolbench/btb-table4-harness.csv; performance: Table 4 Score, "
        "Table A3 Excel row, banker readiness ratings in Section A.4"
    ).format(model=MODEL_LABEL[r["model_id"]], harness=r["harness"])


def build(calc):
    rows = []
    for r in calc["results"]:
        if not r["built"]:
            continue
        pid = POINT_ID[(r["model_id"], r["harness"])]
        rows.append({
            "point_id": pid,
            "task": "BankerToolBench investment banking deliverable",
            "task_category": "research_analysis",
            "task_description": TASK_DESCRIPTION,
            "model_id": r["model_id"],
            "compute_scope": "inference",
            "compute_flops": repr(r["compute_flops"]),
            "human_skill": "expert",
            "human_time_scope": "task_performance",
            "human_time": str(calc["human_time_seconds"]),
            "performance_vs_human": "below",
            "comparison_issues": "different_inputs_or_tools; different_assessment; different_attempt_selection",
            "compute_evidence": "derived_assumed_inputs",
            "human_time_evidence": "task_timings",
            "performance_evidence": performance_evidence(r["score"], r["score_sd_over_3_runs"]),
            "human_time_statistic": "mean",
            "human_time_subset": "successful",
            "human_attempts": "100",
            "human_time_source": HUMAN_TIME_SOURCE,
            "human_time_method": "other_calculation",
            "compute_method": "params_tokens",
            "compute_statistic": "mean",
            "compute_subset": "all",
            "ai_attempts": "300",
            "compute_source": ("research/bankertoolbench.md#compute; "
                               "research/bankertoolbench/calculations.json; "
                               "agent-work/sources/epoch-swebench-bins/epoch-swebench-perinstance.csv"),
            "tokens": repr(r["central_billed_units"]),
            "tokens_accounting": "input_cache_creation_output",
            "source_dataset": "BankerToolBench, Handshake AI",
            "source_record": source_record(r, pid),
            "notes": notes(r, pid),
            "ai_cost_usd": ("%.2f" % r["cost_per_run_usd"]),
            "ai_cost_basis": "reported",
            "ai_cost_date": "2026-04-13",
            "human_cost_usd": "",
            "human_cost_basis": "not_available",
        })
    rows.sort(key=lambda x: x["point_id"])
    return rows


def columns_from_spec(path):
    doc = open(path, encoding="utf-8").read()
    sec = doc.split("## points.csv\n", 1)[1].split("\n## ", 1)[0]
    return [l.split("|")[1].strip().strip("`") for l in sec.splitlines() if l.startswith("| `")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--calculations", required=True)
    ap.add_argument("--columns", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    calc = json.load(open(args.calculations, encoding="utf-8"))
    cols = columns_from_spec(args.columns)
    rows = build(calc)
    for row in rows:
        assert set(row) == set(cols), sorted(set(row) ^ set(cols))
    with open(args.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\r\n")
        w.writeheader()
        w.writerows(rows)
    caps = {"notes": 586, "task_description": 560, "performance_evidence": 337,
            "source_record": 455, "compute_source": 220, "human_time_source": 205}
    for row in rows:
        for field, cap in caps.items():
            n = len(row[field])
            flag = "OVER" if n > cap else "ok"
            print("%-28s %-20s %4d / %4d  %s" % (row["point_id"], field, n, cap, flag))
        for field in ("human_time_source", "compute_source", "source_record"):
            for ref in re.findall(r"(?<![\w/.-])(?:research|sources)/[^\s;,()]+", row[field]):
                assert not ref[-1] in ".,;:", (row["point_id"], ref)
    print("wrote %d rows to %s" % (len(rows), args.out))


if __name__ == "__main__":
    main()
