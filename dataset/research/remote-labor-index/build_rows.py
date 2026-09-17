#!/usr/bin/env python3
"""Assemble the five Remote Labor Index candidate rows from the calculation output.

Every numeric field comes from `calculations.json`, so the CSV cannot drift from
the arithmetic in `price_to_flops.py`. The prose fields live here, and the script
enforces the dataset's text-length norms on each of them rather than leaving that
to a later check.

Standard library only. Explicit input and output paths; nothing is modified in
place. Usage:

    python3 research/remote-labor-index/build_rows.py \\
        --calculations research/remote-labor-index/calculations.json \\
        --points-header points.csv \\
        --models-header models.csv \\
        --out-points /path/to/new-points.csv \\
        --out-models /path/to/new-models.csv

`--points-header` and `--models-header` are read for their header rows only; no
row of either file is read or written. `--out-models` is written with a header
and no rows: this collection adds no model, reusing `gpt-5`, `claude-sonnet-4-5`,
`grok-4` and `gemini-2.5-pro-preview-06-05` from the registry unchanged.
"""

import argparse
import csv
import json
from pathlib import Path

# Dataset text-length norms, in characters.
LIMITS = {
    "notes": 586,
    "task_description": 560,
    "performance_evidence": 337,
    "source_record": 455,
    "compute_source": 220,
    "human_time_source": 205,
}

ORDER = ["work-rli-gpt5-cli", "work-rli-gpt5-cua", "work-rli-sonnet45",
         "work-rli-grok4", "work-rli-gemini25pro"]

TASKNAME = "RLI: remote freelance project"

DESC_HEAD = (
    "Complete one end-to-end remote freelance project, as the collection average over the "
    "Remote Labor Index: 240 commissioned projects across 23 Upwork subcategories, the largest "
    "video, CAD, design, audio and game dev. Input: a brief plus client files. Output: the "
    "requested deliverables in one directory. No questions, no client contact. Done when "
    "evaluators judge it at least as good as the paid human deliverable. Mean human time "
    "28.9 h. Run in "
)

# Appendix B.6 scopes the multimedia tools to the OpenHands environment; the
# computer-use agent gets computer-use, file-editor and bash tools and nothing
# else. The leaderboard page's summary says all agents had them, and that
# conflict is recorded in the research note rather than split across the rows.
SCAFFOLD = {
    "work-rli-gpt5-cli": (
        "OpenHands CLI scaffold",
        "the OpenHands CLI environment with image, speech and video tools and a $30 budget.",
    ),
    "work-rli-gpt5-cua": (
        "Scale AI computer-use scaffold",
        "Scale AI's computer-use Ubuntu VM with screenshot, file-editor and bash tools, a "
        "one-hour timeout and a $30 budget.",
    ),
    "work-rli-sonnet45": (
        "Scale AI computer-use scaffold",
        "Scale AI's computer-use Ubuntu VM with screenshot, file-editor and bash tools, a "
        "one-hour timeout and a $30 budget.",
    ),
    "work-rli-grok4": (
        "OpenHands CLI scaffold",
        "the OpenHands CLI environment with image, speech and video tools and a $30 budget.",
    ),
    "work-rli-gemini25pro": (
        "OpenHands CLI scaffold",
        "the OpenHands CLI environment with image, speech and video tools and a $30 budget.",
    ),
}

LEADERBOARD = {
    "work-rli-gpt5-cli": "leaderboard gpt-5-2025-08-07 in agent-work/sources/remote-labor-index/scale-leaderboard-rli-2026-09-13.json",
    "work-rli-gpt5-cua": "not listed separately on the Scale leaderboard",
    "work-rli-sonnet45": "leaderboard claude-4-5-Sonnet in agent-work/sources/remote-labor-index/scale-leaderboard-rli-2026-09-13.json",
    "work-rli-grok4": "not listed on the Scale leaderboard",
    "work-rli-gemini25pro": "leaderboard gemini-2.5-pro-preview-06-05 in agent-work/sources/remote-labor-index/scale-leaderboard-rli-2026-09-13.json",
}

EXTRA = {
    "work-rli-gpt5-cli": "",
    "work-rli-gpt5-cua": (
        " Billed input includes screenshots; the text-image split is undetermined."
    ),
    "work-rli-sonnet45": (
        " Billed input includes screenshots; the text-image split is undetermined."
    ),
    "work-rli-grok4": " Grok 4 list prices double above 128k prompt tokens.",
    "work-rli-gemini25pro": " Model revision resolved from this run's leaderboard entry.",
}


def shared_notes(row):
    return (
        "Compute inverts the pooled $2.34 mean API cost per deliverable; that distribution "
        "pools configurations, so all five RLI rows carry one observation. Positions exclude "
        "cache reads at an assumed "
        f"{100 * row['central_cache_hit_share']:.0f}% input hit rate, the geometric mean of no "
        "caching and full prefix reuse; envelope "
        f"{row['flops_low_over_central']:.2f}x-{row['flops_high_over_central']:.2f}x. Omitted, "
        "upward: cached-context attention 0.1x-2.4x, and multimedia helper FLOPs in the pooled "
        "OpenHands runs. writing_media is the plurality of 23 subcategories; a quarter (CAD, "
        "architecture, product design) fits none."
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--calculations", required=True, type=Path)
    ap.add_argument("--points-header", required=True, type=Path)
    ap.add_argument("--models-header", required=True, type=Path)
    ap.add_argument("--out-points", required=True, type=Path)
    ap.add_argument("--out-models", required=True, type=Path)
    args = ap.parse_args()

    calc = json.loads(args.calculations.read_text())
    with args.points_header.open(newline="") as fh:
        header = next(csv.reader(fh))
    with args.models_header.open(newline="") as fh:
        models_header = next(csv.reader(fh))

    rows = []
    for pid in ORDER:
        r = calc["rows"][pid]
        label, scaffold_desc = SCAFFOLD[pid]
        pct = f"{100.0 * r['automation_successes'] / 240:.2f}".rstrip("0").rstrip(".")
        perf = (
            f"Automation rate {r['automation_successes']} of 240 ({pct}%): trained evaluators "
            "judged the AI deliverable to satisfy the brief at least as well as the paid "
            "deliverable; majority of three, 94.4% agreement, false negatives under 5.8% at 95% "
            f"confidence. Elo {r['elo']} against a human baseline normalized to 1000. All 240 "
            "human deliverables met that bar by construction."
        )
        src = (
            "https://arxiv.org/abs/2510.26787 v1; "
            f"{r['agent_configuration']}, {label}; Tables 3-4, Figure 12, Appendices B.2 B.6 "
            "C.5; agent-work/sources/remote-labor-index/rli-paper-extracts.md; "
            "agent-work/sources/remote-labor-index/figure-bar-geometry.json; "
            "agent-work/sources/remote-labor-index/scale-leaderboard-methodology.md; "
            f"{LEADERBOARD[pid]}; performance: Table 3, Section 5, Appendix B.2"
        )
        row = {
            "point_id": pid,
            "task": TASKNAME,
            "task_category": "writing_media",
            "task_description": DESC_HEAD + scaffold_desc,
            "model_id": r["model_id"],
            "compute_scope": "inference",
            "compute_flops": repr(r["compute_flops_central"]),
            "human_skill": "expert",
            "human_time_scope": "task_performance",
            "human_time": repr(int(calc["human_time"]["mean_seconds"])),
            "performance_vs_human": "below",
            "comparison_issues": "different_attempt_selection; different_inputs_or_tools",
            "compute_evidence": "transferred_workload",
            "human_time_evidence": "task_timings",
            "performance_evidence": perf,
            "human_time_statistic": "mean",
            "human_time_subset": "successful",
            "human_attempts": repr(calc["human_time"]["attempts_used"]),
            "human_time_source": "research/remote-labor-index.md#human-time",
            "human_time_method": "other_calculation",
            "compute_method": "params_tokens",
            "compute_statistic": "mean",
            "compute_subset": "all",
            "ai_attempts": repr(calc["histogram_reconstruction"]["fig12_costs"]["n"]),
            "compute_source": (
                "research/remote-labor-index.md#compute; "
                "research/remote-labor-index/calculations.json"
            ),
            "tokens": repr(r["tokens_central"]),
            "tokens_accounting": "input_cache_creation_output",
            "source_dataset": "Remote Labor Index",
            "source_record": src,
            "notes": shared_notes(r) + EXTRA[pid],
        }
        mismatch = set(header) ^ set(row)
        if mismatch:
            raise SystemExit(f"field mismatch against the supplied header: {sorted(mismatch)}")
        for field, limit in LIMITS.items():
            if len(row[field]) > limit:
                raise SystemExit(
                    f"{pid}: {field} is {len(row[field])} characters, limit {limit}"
                )
        rows.append(row)

    args.out_points.parent.mkdir(parents=True, exist_ok=True)
    with args.out_points.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)
    args.out_models.parent.mkdir(parents=True, exist_ok=True)
    with args.out_models.open("w", newline="") as fh:
        csv.writer(fh).writerow(models_header)

    print(f"wrote {len(rows)} rows to {args.out_points}")
    print(f"wrote header-only models file to {args.out_models}")
    print("field lengths, longest row of each:")
    for field, limit in LIMITS.items():
        worst = max(len(r[field]) for r in rows)
        print(f"  {field:22s} {worst:4d} / {limit}")


if __name__ == "__main__":
    main()
