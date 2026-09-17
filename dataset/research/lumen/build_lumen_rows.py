#!/usr/bin/env python3
"""Assemble candidates/lumen/points.csv from research/lumen/calculations.json.

Every numeric field is taken from the calculations file; only the text fields are
written here. Text fields are asserted against the dataset's own field-length
norms. Dependencies: Python 3.9+ standard library only.

    python3 build_lumen_rows.py \
        --calculations .../research/lumen/calculations.json \
        --header       .../points.csv \
        --output       .../candidates/lumen/points.csv

--header supplies the column order; the file is read only for its first line.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

# Dataset maxima for the fields the independent review flagged as over-long.
LIMITS = {
    "task": 82,
    "task_description": 560,
    "performance_evidence": 337,
    "source_record": 455,
    "compute_source": 220,
    "human_time_source": 205,
    "notes": 586,
}

TOPIC = {
    "D1": "antidepressants for depression in dementia",
    "D2": "CBT for insomnia in major depression",
    "D3": "laparoscopic versus open cholecystectomy",
    "D4": "pneumococcal vaccines in adults",
    "D5": "SGLT2 inhibitors in heart failure",
}
SHORT = {
    "D1": "antidepressants in dementia",
    "D2": "CBT-I in depression",
    "D3": "laparoscopic vs open cholecystectomy",
    "D4": "pneumococcal vaccines",
    "D5": "SGLT2i in heart failure",
}
KAPPA = {"D1": "0.74", "D2": "0.76", "D3": "0.73", "D4": "0.62", "D5": "0.21"}
PABAK = {"D1": "0.99", "D2": "0.99", "D3": "0.95", "D4": "0.94", "D5": "0.93"}
ARBITER = {"D1": 8, "D2": 5, "D3": 70, "D4": 26, "D5": 54}

# Label rule (research/lumen.md, "Labels, and the rule behind them"): where the source
# itself groups the domains by divergence from the reference review, the label follows
# that grouping, and the number of comparable outcomes is not a label input. Sections 3.1
# and 4.3 group D1, D2 and D4 as the heterogeneous domains whose I-squared diverges
# most from the reference, and D3 and D5 as the homogeneous ones where it does not.
PERF = {"D1": "below", "D2": "below", "D3": "match", "D4": "below", "D5": "match"}

GT_CITATION = {
    "D1": "Lenouvel E et al., Psychiatry Research 2024, PMID 39163819",
    "D2": "Furukawa Y et al., J Affective Disorders 2024, PMID 39242039",
    "D3": "Avicenna J Medicine 2024, PMC11057899, doi:10.1055/s-0043-1777710",
    "D4": "Farrar JL et al., Pathogens 2023;12(5):732, PMID 37242402",
    "D5": "Vaduganathan M et al., Lancet 2022;400:757-767",
}

PERF_EVIDENCE = {
    "D1": "Pooled estimates compared with a published meta-analysis. One comparable outcome, "
          "agreeing in direction; 5 poolable analyses with I-squared 50.8 to 90.8 per cent. The "
          "source groups this domain with D2 and D4 as the heterogeneous ones whose I-squared "
          "diverges most from the reference. No magnitude or extraction accuracy is reported.",
    "D2": "Pooled estimates compared with a published meta-analysis. One comparable outcome, "
          "agreeing in direction; 4 poolable analyses with I-squared 52.9 to 78.2 per cent. The "
          "reference recoded continuous sleep-quality scores into binary response categories to "
          "cut heterogeneity, a clinical judgment the pipeline cannot replicate.",
    "D3": "Pooled estimates compared with a published meta-analysis. Four comparable outcomes, "
          "all agreeing in direction; 6 poolable analyses with I-squared 0 to 29.4 per cent. Nine "
          "of the reference's fifteen studies were unavailable as PDFs, so at most six of fifteen "
          "could overlap, against 46 studies included here.",
    "D4": "Pooled estimates compared with a published meta-analysis. Three comparable outcomes, "
          "all agreeing in direction; 5 poolable analyses with I-squared 2.8 to 80.3 per cent and "
          "pooled vaccine effectiveness 38 to 54 per cent. The source groups this domain with D1 "
          "and D2 as the heterogeneous ones whose I-squared diverges most.",
    "D5": "Pooled estimates compared with a published meta-analysis. All four comparable outcomes "
          "reproduced the published hazard ratios within 1 per cent (0.777 vs 0.77 through 0.921 "
          "vs 0.92), I-squared 0 to 0.7 per cent; 7 poolable analyses. The included-study list is "
          "unpublished, so re-extraction of the reference's estimates is not excluded.",
}

SPECIFIC_NOTES = {
    "D1": "The label follows the source's grouping of D1, D2 and D4 as the heterogeneous "
          "domains whose I-squared diverges most from the reference; the number of comparable "
          "outcomes measures evidence quantity, not performance.",
    "D2": "The reference recoded continuous sleep-quality scores into binary categories, so the "
          "pipeline's four analyses are not the reference's; that and the source's heterogeneous "
          "grouping set the label.",
    "D3": "Screening cost $0.0013 per record against $0.0052 in the other four runs and $0.0096 "
          "in the repository's pilot, a sevenfold outlier, so this row is least secure on the low "
          "side; allocating screening by derived calls gives 1.418e+18.",
    "D4": "Table S2 records 45 studies passing screening against Table 2's 49 finally included, "
          "which cannot both be right. At 2,010 citations the active-hours regression sits mid "
          "fitted range, most secure of the five.",
    "D5": "Full-text screening cost $0.04, about one call for 11 included studies, either a "
          "near-absent phase or a source defect. At 8,062 citations the active-hours regression "
          "is 82 per cent to its quadratic's turn, least secure of the five.",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--calculations", required=True)
    ap.add_argument("--header", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    calc = json.load(open(args.calculations, encoding="utf-8"))
    with open(args.header, newline="", encoding="utf-8") as fh:
        header = next(csv.reader(fh))

    att = calc["scenarios"]["cached_context_attention"]["architectures"]
    recon = calc["scenarios"]["dollar_reconciled"]["per_review"]
    poolable = {"D1": 5, "D2": 4, "D3": 6, "D4": 5, "D5": 7}

    rows = []
    for d in ["D1", "D2", "D3", "D4", "D5"]:
        pr = calc["per_review"][d]
        ht = calc["human_time"][d]
        att_lo = att["low"]["per_review"][d]["fraction_of_recorded"] * 100
        att_hi = att["high"]["per_review"][d]["fraction_of_recorded"] * 100

        shared = (
            "Tokens allocate the five-run per-phase medians by published per-phase dollars; the "
            f"dollars instead imply {recon[d]['compute_flops']:.3e}, the surviving explanation "
            f"being a per-screener token row. Omitted attention adds {att_lo:.1f}-{att_hi:.1f}%, "
            "one-sided. Flags: own protocol, no PICO design or peer review; PDF-limited full "
            "text; concordance on 1-4 outcomes; 1990s donor timings."
        )

        task_description = (
            f"One run of an 11-agent pipeline on a PICO question about {TOPIC[d]}. Phases: "
            f"search strategy; four-database search returning {pr['yield']:,} records, "
            f"{pr['screened']:,} after deduplication and pre-screen; dual-model title-abstract "
            "screening of all of them with arbitration; full-text PICO check; three-pass "
            f"extraction from {pr['included']} included studies; REML meta-analysis in R metafor; "
            f"automated RoB-2 and GRADE; manuscript draft. Completion is that draft with its "
            f"{poolable[d]} pooled analyses. PICO definition, outcome recoding and peer review "
            "are outside the run."
        )

        rows.append({
            "point_id": f"agen-lumen-{d.lower()}-gemini31pro",
            "task": f"Automated systematic review/meta-analysis: {SHORT[d]}",
            "task_category": "research_analysis",
            "task_description": task_description,
            "model_id": "gemini-3.1-pro-preview",
            "compute_scope": "inference",
            "compute_flops": repr(pr["compute_flops"]),
            "human_skill": "expert",
            "human_time_scope": "task_performance",
            "human_time": str(ht["seconds_central_rounded"]),
            "performance_vs_human": PERF[d],
            "comparison_issues": "different_task; different_inputs_or_tools; "
                                 "different_assessment; different_human_baseline",
            "compute_evidence": "derived_assumed_inputs",
            "human_time_evidence": "transferred_timings",
            "performance_evidence": PERF_EVIDENCE[d],
            "human_time_statistic": "point_estimate",
            "human_time_subset": "all",
            "human_attempts": "37",
            "human_time_source": "Allen IE, Olkin I. JAMA 1999;282(7):634-635, PMID 10517715, "
                                 "active hours summed across the project team; "
                                 "agent-work/sources/lumen/allen-olkin-1999-extract.md; "
                                 "research/lumen.md#human-time",
            "human_time_method": "estimated",
            "compute_method": "params_tokens",
            "compute_statistic": "total",
            "compute_subset": "all",
            "ai_attempts": "1",
            "compute_source": "https://arxiv.org/abs/2606.28362 Tables 1, 3, S1, S3; "
                              "agent-work/sources/lumen/lumen-source-values.json; "
                              "research/lumen.md#compute-derivation; "
                              "research/lumen/calculations.json",
            "tokens": str(int(round(pr["tokens"]))),
            "tokens_accounting": "input_output",
            "source_dataset": "LUMEN (arXiv 2606.28362)",
            "source_record": (
                f"arXiv:2606.28362v1, domain review {d} ({pr['domain']}): Table 2 yield "
                f"{pr['yield']}, screened {pr['screened']}, included {pr['included']}; Table 3 "
                f"total ${pr['reported_total_cost_usd']:.2f}; Table S1 per-phase medians; Table "
                f"S2 kappa {KAPPA[d]}, PABAK {PABAK[d]}, {ARBITER[d]} arbiter calls; Table S3 "
                f"score distributions; Tables S4-S5 Arm A analyses; Table 1 routing. "
                f"performance: {GT_CITATION[d]}."
            ),
            "notes": shared + " " + SPECIFIC_NOTES[d],
        })

    over = [
        (r["point_id"], f, len(r[f]), lim)
        for r in rows for f, lim in LIMITS.items() if len(r[f]) > lim
    ]
    if over:
        for o in over:
            print(f"OVER LIMIT: {o[0]} {o[1]} {o[2]} > {o[3]}")
        raise SystemExit("field-length limits exceeded")

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=header)
        w.writeheader()
        for r in rows:
            if set(r) != set(header):
                raise SystemExit(
                    f"column mismatch: missing {sorted(set(header) - set(r))}, "
                    f"unknown {sorted(set(r) - set(header))}"
                )
            w.writerow(r)
    print(f"wrote {args.output} ({len(rows)} rows)")
    for f, lim in LIMITS.items():
        print(f"  {f:20s} max {max(len(r[f]) for r in rows):4d} / {lim}")


if __name__ == "__main__":
    main()
