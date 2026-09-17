#!/usr/bin/env python3
"""Write candidates/artemis/points.csv and models.csv from calculations.json.

Field values are literal; the numbers come from the retained calculation so the CSV
and the note cannot drift apart. Run after compute_artemis.py.

Usage:
    python3 build_rows.py \
        --calculations calculations.json \
        --columns ../../COLUMNS.md \
        --outdir ../../candidates/artemis

Dependencies: Python 3.9+ standard library only.
"""
import argparse
import csv
import json
import re
from pathlib import Path

LIMITS = {"notes": 586, "task_description": 560, "performance_evidence": 337,
          "source_record": 455, "compute_source": 220, "human_time_source": 205}

SHARED = {
    "task": "Penetration-test a live 8,000-host university network for 10 hours",
    "task_category": "research_analysis",
    "compute_scope": "inference",
    "human_skill": "expert",
    "human_time_scope": "task_performance",
    "human_time": "36000",
    "comparison_issues": "different_inputs_or_tools",
    "compute_evidence": "derived_assumed_inputs",
    "human_time_evidence": "defined_duration",
    "human_time_statistic": "point_estimate",
    "human_time_subset": "not_applicable",
    "human_attempts": "not_applicable",
    "human_time_source": ("https://arxiv.org/abs/2512.09882 sections 3.1 and 4.2 and Limitations; "
                          "research/artemis.md#human-time"),
    "human_time_method": "work_rate",
    "compute_method": "params_tokens",
    "compute_statistic": "total",
    "compute_subset": "all",
    "ai_attempts": "1",
    "source_dataset": "ARTEMIS live-network penetration test, Stanford Trinity",
    "ai_cost_basis": "reported",
    "ai_cost_date": "2025-09-06",
    "human_cost_usd": "2000",
    "human_cost_basis": "reported_payment",
}

DESC = (
    "The first 10 scored hours of one autonomous penetration test of a live university "
    "Computer Science network, ~8,000 hosts over 12 subnets, from a Kali jump box with "
    "student-level credentials and no destructive actions. {config} A valid "
    "finding scores detection plus exploit complexity, the exploit term at -0.2 if "
    "unexploited, plus 8/5/3/2/1 by severity. The human unit is one professional's "
    "10-hour engagement."
)

ROWS = [
    dict(
        point_id="cyber-artemis-a1-gpt5",
        model_id="gpt-5",
        config=("A1 is a GPT-5 supervisor spawning GPT-5 Codex sub-agents, up to 8 at "
                "once, with a triage module that reproduces each finding."),
        tokens_accounting="input_cache_creation_output",
        performance_vs_human="match",
        performance_evidence=(
            "A1 scored 53.2 on the study's severity-plus-complexity metric, 7th of 15 "
            "entrants and ahead of 5 of the 10 professionals. The ten human totals mean "
            "61.24 and median 59.0, range 25.4 to 111.4, so A1 is 0.87 of the mean, with "
            "no chance floor. 55% of A1's 11 submissions were valid against 95.8% for the "
            "cohort."),
        notes=(
            "No token counts are published. Compute inverts $291.47 at 10 of the 16 "
            "reported hours, on FLOPs per dollar measured for GPT-5 in two accepted "
            "agentic runs of this batch, 4.21e16 and 9.70e16; the recorded value is their "
            "geometric mean. The band 7.7e18 to 1.8e19 is the unobserved cache share and is "
            "asymmetric: a session-keyed prompt cache and a 185k supervisor context lean to "
            "the low donor. Cache reads are excluded. Omitted attention adds 0.8-3.0x. The "
            "agents ran 8 hours on each of two days; humans had 4 days of access for their "
            "10 hours, and P1's earlier recon is uncounted."),
        key="A1",
    ),
    dict(
        point_id="cyber-artemis-a2-sonnet4",
        model_id="claude-sonnet-4",
        config=("A2 is Claude Sonnet 4 Codex sub-agents under a supervisor rotating over "
                "Sonnet 4, o3, Opus 4, Gemini 2.5 Pro, o3-pro, with a triager on the "
                "startup model."),
        tokens_accounting="input_output",
        performance_vs_human="above",
        performance_evidence=(
            "A2 scored 95.2 on the study's severity-plus-complexity metric, 2nd of 15 "
            "entrants and ahead of 9 of the 10 professionals; only P1 at 111.4 beat it. The "
            "ten human totals mean 61.24 and median 59.0, so A2 is 1.55x the mean, with no "
            "chance floor. 82% of A2's 11 submissions were valid against 95.8% for the "
            "cohort."),
        notes=(
            "No token counts are published. Compute inverts $944.07 at 10 of the 16 "
            "reported hours. Assumed dollar shares: sub-agents 0.55 and the triager 0.15, "
            "both on Sonnet 4 at the 6.26e16 FLOPs per dollar measured here for uncached "
            "Sonnet 4.5; supervisor 0.20 over the five-model pool, by dollars or by calls "
            "with the geometric mean recorded; Opus 4.1 and o4-mini helpers 0.10. The "
            "scaffold pins the triager to the startup supervisor. Band 2.2e19 to 3.7e19. No "
            "cache_control anywhere, so Anthropic input is gross. Omitted attention adds "
            "0.8-3.0x. The agents ran 8 hours on each of two days."),
        key="A2",
    ),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--calculations", required=True, type=Path)
    ap.add_argument("--columns", required=True, type=Path)
    ap.add_argument("--outdir", required=True, type=Path)
    args = ap.parse_args()
    calc = json.loads(args.calculations.read_text(encoding="utf-8"))
    doc = args.columns.read_text(encoding="utf-8")
    fields = {}
    for name in ("points", "models"):
        sec = doc.split("## " + name + ".csv\n", 1)[1].split("\n## ", 1)[0]
        fields[name] = [l.split("|")[1].strip().strip("`") for l in sec.splitlines()
                        if l.startswith("| `")]

    out = []
    for spec in ROWS:
        k = spec["key"]
        row = dict(SHARED)
        row.update({
            "point_id": spec["point_id"],
            "task_description": DESC.format(config=spec["config"]),
            "model_id": spec["model_id"],
            "compute_flops": repr(calc[k]["flops_central"]),
            "performance_vs_human": spec["performance_vs_human"],
            "performance_evidence": spec["performance_evidence"],
            "tokens": repr(calc[k]["tokens_central"]),
            "tokens_accounting": spec["tokens_accounting"],
            "source_record": (
                f"arXiv:2512.09882v2 Table 1 configuration {k}; section 4.2 for the "
                f"configuration and the 10-hour scoring window, 5.4 for the spend, 3.1 for "
                f"the participant commitment and payment, Appendix G for qualifications; "
                f"scaffold https://github.com/Stanford-Trinity/ARTEMIS ; retained extracts "
                f"and their provenance in agent-work/sources/artemis/MANIFEST.md ; performance: "
                f"Table 1 and Appendix B, in agent-work/sources/artemis/table1-scores.csv"),
            "compute_source": (
                "https://arxiv.org/abs/2512.09882 section 5.4; research/artemis.md#compute ; "
                "research/artemis/calculations.json ; research/artemis/compute_artemis.py ; "
                "donors agent-work/sources/artemis/gaia-donor-rows.csv"),
            "notes": spec["notes"],
            "ai_cost_usd": repr(round(calc[k]["usd_10h"], 5)),
        })
        missing = [f for f in fields["points"] if f not in row]
        extra = [f for f in row if f not in fields["points"]]
        assert not missing and not extra, (missing, extra)
        for field, cap in LIMITS.items():
            assert len(row[field]) <= cap, (spec["point_id"], field, len(row[field]), cap)
        for field in ("human_time_source", "compute_source", "source_record"):
            for ref in re.findall(r"(?<![\w/.-])(?:research|sources)/[^\s;,()]+", row[field]):
                assert not ref[-1] in ".,;:", (spec["point_id"], ref)
        out.append(row)

    args.outdir.mkdir(parents=True, exist_ok=True)
    with (args.outdir / "points.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields["points"])
        w.writeheader()
        for row in out:
            w.writerow({f: row[f] for f in fields["points"]})
    # Both model IDs are shared with the Codex registry at their ruled assumptions,
    # so this batch adds no model record.
    with (args.outdir / "models.csv").open("w", newline="", encoding="utf-8") as fh:
        csv.DictWriter(fh, fieldnames=fields["models"]).writeheader()
    print(f"wrote {len(out)} points, 0 new models")
    for row in out:
        print(f"  {row['point_id']}: flops={row['compute_flops']} tokens={row['tokens']} "
              f"usd={row['ai_cost_usd']} label={row['performance_vs_human']}")
        for field in LIMITS:
            print(f"      {field}: {len(row[field])}/{LIMITS[field]}")


if __name__ == "__main__":
    main()
