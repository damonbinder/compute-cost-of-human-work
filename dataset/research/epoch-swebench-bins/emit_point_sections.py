#!/usr/bin/env python3
"""Emit the per-point sections of research/epoch-swebench-bins.md from calculations.json.

Dependencies: Python 3.9+ standard library only.  No network access.  Writes a fresh file;
the sections after the '<!-- GENERATED POINTS -->' marker in the note are its contents, so
re-running it and diffing checks that the note still matches the calculations.

  python3 emit_point_sections.py \
      --calc      research/epoch-swebench-bins/calculations.json \
      --run-links agent-work/sources/epoch-swebench-bins/epoch-swebench-run-links.csv \
      --out       /tmp/epoch-swebench-bin-sections.md
"""

import argparse
import csv
import json
import sys

BINS = ["<15 min fix", "15 min - 1 hour", "1-4 hours", ">4 hours"]
HUMAN_BASIS = {"<15 min fix": "bin interval midpoint", "15 min - 1 hour": "bin interval midpoint",
               "1-4 hours": "bin interval midpoint", ">4 hours": "6 h for the open upper bin"}


def g(x):
    return "{:,}".format(round(x)) if abs(x) >= 1 else "%.4g" % x


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--calc", required=True)
    ap.add_argument("--run-links", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    with open(args.calc) as fh:
        calc = json.load(fh)
    with open(args.run_links) as fh:
        links = {r["run"]: r for r in csv.DictReader(fh)}

    out = []
    for run in sorted(calc):
        rec, link = calc[run], links[run]
        if rec.get("excluded_from_csv"):
            continue
        for label in BINS:
            b = rec["bins"][label]
            counted = b["recorded_counted_tokens"]
            allow = b["missing_work_allowance_tokens"]
            out.append("## %s\n" % b["point_id"])
            out.append(
                "[Original run](%s); primary `%s`; reasoning_effort=%s; Inspect task `%s` "
                "(%s), 2,000,000-token limit. Difficulty label `%s`: %d instances, %d completed "
                "evaluations, %d resolved (%.4f%%)."
                % (link["log_url"], link["endpoint"], link["reasoning_effort"],
                   link["inspect_task"], link["harness"], label,
                   b["instances"], b["completed_evaluations"], b["resolved"],
                   100 * b["resolved_rate"]))
            out.append(
                "Mean per-instance native counters: input %s, cache write %s, cache read %s, "
                "output %s, reasoning %s."
                % (g(b["mean_input_tokens"]), g(b["mean_cache_write_tokens"]),
                   g(b["mean_cache_read_tokens"]), g(b["mean_output_tokens"]),
                   g(b["mean_reasoning_tokens"])))
            out.append(
                "Counted workload %s + missing-work allowance %s = %.6f tokens / %d completed "
                "evaluations = **%.6f tokens** x %s FLOPs/token = **%.6e FLOPs**."
                % (g(counted), ("%.6f" % allow) if allow else "0",
                   counted + allow, b["completed_evaluations"],
                   b["tokens_per_completed_evaluation"], g(rec["flops_per_token"]),
                   b["compute_flops"]))
            extra = ("Recorded counters alone give %.6f tokens per completed evaluation."
                     % b["tokens_per_completed_evaluation_recorded_only"]) if allow else ""
            out.append(
                "Human time %d s (%s). Per-instance counted-token standard deviation %s, "
                "standard error of the mean %s (%.1f%% of the mean). Mean AI working time %s s. "
                "At the 2,000,000-token harness cap: %d of %d instances (%.1f%%). %s"
                % (round(b["human_time_s"]), HUMAN_BASIS[label], g(b["per_instance_sd"]),
                   g(b["per_instance_se_of_mean"]), 100 * b["se_over_mean"],
                   ("%.1f" % b["mean_working_time_s"]) if b["mean_working_time_s"] else "not recorded",
                   b["instances_at_token_cap"], b["instances"], b["percent_at_token_cap"],
                   extra))
            at = b["omitted_cached_context_attention"]
            out.append(
                "Omitted cached-context attention, excluded from compute_flops and one-sided "
                "upward: %.0f model calls, mean prefix %s to %s positions, %s appended "
                "positions. At L=64, d_model=8192 that is %.3e to %.3e FLOPs, %.2fx to %.2fx the "
                "recorded value; at L=96, d_model=12288, 2.25 times those."
                % (at["model_calls"], g(at["mean_prefix_lower"]), g(at["mean_prefix_upper"]),
                   g(at["appended_positions"]),
                   at["shapes"]["L=64, d=8192"]["attention_flops_lower"],
                   at["shapes"]["L=64, d=8192"]["attention_flops_upper"],
                   at["shapes"]["L=64, d=8192"]["ratio_to_compute_flops_lower"],
                   at["shapes"]["L=64, d=8192"]["ratio_to_compute_flops_upper"]))
            out.append("")
    with open(args.out, "w") as fh:
        fh.write("\n".join(out).rstrip() + "\n")
    print("sections=%d -> %s"
          % (sum(len(calc[r]["bins"]) for r in calc if not calc[r].get("excluded_from_csv")),
             args.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
