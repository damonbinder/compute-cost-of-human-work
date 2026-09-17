#!/usr/bin/env python3
"""Build one candidate row per (Epoch SWE-bench Verified run, OpenAI difficulty bin) from
the retained per-instance joined table.

Dependencies: Python 3.9+ standard library only.  No network access.

Usage (all paths explicit; outputs are written fresh):

  python3 build_bin_rows.py \
      --perinstance  agent-work/sources/epoch-swebench-bins/epoch-swebench-perinstance.csv \
      --run-links    agent-work/sources/epoch-swebench-bins/epoch-swebench-run-links.csv \
      --models       "../AI Compute vs Human Time/dataset/models.csv" \
      --parent-points "../AI Compute vs Human Time/dataset/points.csv" \
      --out-points   candidates/epoch-swebench-bins/points.csv \
      --out-bins     agent-work/sources/epoch-swebench-bins/epoch-swebench-bin-summary.csv \
      --out-calc     research/epoch-swebench-bins/calculations.json

One run is excluded from the CSV and kept in the calculations file with its disposition: on
`epoch/qwen3.6-plus` the Inspect 2,000,000-token budget binds on 42% to 98% of the instances in
each bin, so the recorded values are the harness cap rather than the model's workload.

--models supplies flops_per_token and active_parameters_basis for the model IDs already in
the dataset; --parent-points supplies the benchmark-wide row a bin row refines, and is used
only to name that row and to check that the four bins re-aggregate to its values.  Runs with
no existing dataset row are built the same way, without that check and without the refinement
sentence in `notes`.
"""

import argparse
import collections
import csv
import json
import math
import os
import statistics
import sys

# Source difficulty label -> (point_id suffix, human seconds, short prose, human-time basis)
# Inspect's task_args set token_limit = 2,000,000, enforced against the same non-cache-read
# count these rows record.  An instance at or above this is treated as censored by the cap.
TOKEN_LIMIT = 2_000_000
CAP_THRESHOLD = 1_950_000
CAP_NOTE_THRESHOLD = 10.0          # percent of a bin's instances, above which notes say so

# Runs kept out of the CSV, with the disposition recorded in calculations.json.
EXCLUDED_RUNS = {
    "agen-epoch-swebench-qwen36plus":
        "The Inspect 2,000,000-token budget binds on 42.2%, 67.7%, 97.6% and 66.7% of the "
        "instances in the four bins, so the recorded per-instance totals are the harness cap, "
        "not the model's workload. The endpoint also reports no cache counters, so every "
        "re-read prefix is counted as newly processed; the two effects push in opposite "
        "directions and neither is recoverable from the retained members.",
}

# Cached-context attention omitted by the 2 * active_parameters convention, priced with the
# 4 * layers * d_model * context_positions recipe the dataset's RULER row uses.
ATTENTION_SHAPES = {"L=64, d=8192": (64, 8192), "L=96, d=12288": (96, 12288)}

BINS = [
    ("<15 min fix",     "lt15m", 7.5 * 60,   "under 15 minutes", "the bin interval's midpoint"),
    ("15 min - 1 hour", "15m1h", 37.5 * 60,  "15 min to 1 hour", "the bin interval's midpoint"),
    ("1-4 hours",       "1h4h",  150.0 * 60, "1 to 4 hours",     "the bin interval's midpoint"),
    (">4 hours",        "gt4h",  360.0 * 60, "over 4 hours",     "6 h assigned to this open upper bin"),
]

# CSV text-field length norms for this folder (DECISIONS.md).
LIMITS = {"notes": 586, "task_description": 560, "performance_evidence": 337,
          "source_record": 455, "compute_source": 220, "human_time_source": 205}

HEADER = ["point_id", "task", "task_category", "task_description", "model_id", "compute_scope",
          "compute_flops", "human_skill", "human_time_scope", "human_time", "performance_vs_human",
          "comparison_issues", "compute_evidence", "human_time_evidence", "performance_evidence",
          "human_time_statistic", "human_time_subset", "human_attempts", "human_time_source",
          "human_time_method", "compute_method", "compute_statistic", "compute_subset",
          "ai_attempts", "compute_source", "tokens", "tokens_accounting", "source_dataset",
          "source_record", "notes"]

HUMAN_TIME_SOURCE = (
    "https://cdn.openai.com/introducing-swe-bench-verified/swe-b-annotation-instructions.pdf; "
    "research/epoch-swebench-bins.md#human-time-bins")

NOTE_REFINES = "Refines and supersedes {parent} at merge. "
NOTE_NEW = "No benchmark-wide row exists for this run. "
NOTE_BASE = ("Human time is {basis}, not a timing; it assumes codebase familiarity and "
             "clarified high-level requirements. Some native tests reject valid fixes, and "
             "models may have seen published solutions in training. Omitted cached-context "
             "attention adds at least {attn}x the recorded value.")


def call_count(group):
    """Model calls in a bin, from the transcript length: system plus (assistant, tool) pairs."""
    return sum(max(float(r["message_count"] or 0) / 2.0, 1.0) for r in group)


def attention_scenario(group, link, coefficient):
    """Omitted cached-context attention for one bin, as a ratio to the recorded compute.

    Appended positions are the counted workload.  The mean prefix each of them attends over is
    bounded below by the run's cache reads per call, which are prefix positions attended to but
    not re-processed, and above by all input-side positions per call, which additionally counts
    prefix that was re-processed rather than read from cache.  Both are per-call means from the
    transcript length, not per-call prefixes: the retained summaries do not carry those, so this
    is a bounded scenario rather than a derivation.
    """
    calls = call_count(group)
    appended = sum(float(r["counted_tokens"]) for r in group)
    cache_read = sum(float(r["cache_read_tokens"]) for r in group)
    fresh_in = sum(float(r["input_tokens"]) for r in group)
    cache_write = sum(float(r["cache_write_tokens"]) for r in group)
    inside = link["cache_reads_inside_input"] == "1"
    prefix_lo = cache_read / calls
    prefix_hi = (fresh_in / calls) if inside else ((cache_read + fresh_in + cache_write) / calls)
    out = {"model_calls": calls, "appended_positions": appended,
           "mean_prefix_lower": prefix_lo, "mean_prefix_upper": prefix_hi,
           "recipe": "4 * layers * d_model * context_positions per appended position",
           "recipe_source": "dataset/research/ruler/ruler.md",
           "basis": "prefix bounded below by cache reads per call and above by all input-side "
                    "positions per call; one-sided upward, excluded from compute_flops",
           "shapes": {}}
    for name, (layers, d_model) in ATTENTION_SHAPES.items():
        four_ld = 4 * layers * d_model
        out["shapes"][name] = {
            "layers": layers, "d_model": d_model, "four_L_d": four_ld,
            "attention_flops_lower": four_ld * prefix_lo * appended,
            "attention_flops_upper": four_ld * prefix_hi * appended,
            "ratio_to_compute_flops_lower": four_ld * prefix_lo / coefficient,
            "ratio_to_compute_flops_upper": four_ld * prefix_hi / coefficient,
        }
    return out


def fmt_pct(x):
    return ("%.4f" % (100.0 * x)).rstrip("0").rstrip(".")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--perinstance", required=True)
    ap.add_argument("--run-links", required=True)
    ap.add_argument("--models", required=True)
    ap.add_argument("--parent-points", required=True)
    ap.add_argument("--out-points", required=True)
    ap.add_argument("--out-bins", required=True)
    ap.add_argument("--out-calc", required=True)
    args = ap.parse_args(argv)

    for out in (args.out_points, args.out_bins, args.out_calc):
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)

    with open(args.perinstance) as fh:
        records = list(csv.DictReader(fh))
    with open(args.run_links) as fh:
        links = {r["run"]: r for r in csv.DictReader(fh)}
    with open(args.models) as fh:
        models = {r["model_id"]: r for r in csv.DictReader(fh)}
    with open(args.parent_points) as fh:
        parents = {r["point_id"]: r for r in csv.DictReader(fh)
                   if r["point_id"].startswith("agen-epoch-swebench-")}

    grouped = collections.defaultdict(list)
    for rec in records:
        grouped[(rec["run"], rec["difficulty"])].append(rec)

    rows, bin_rows, excluded_bin_rows, calc = [], [], [], {}
    for run in sorted({r["run"] for r in records}):
        link = links[run]
        model_id = link["model_id"]
        coefficient = float(models[model_id]["flops_per_token"])
        basis = models[model_id]["active_parameters_basis"]
        parent = parents.get(run)
        run_recs = [r for r in records if r["run"] == run]
        run_scored = sum(int(r["scored"]) for r in run_recs)
        run_resolved = sum(int(r["resolved"]) for r in run_recs)
        run_tokens = sum(float(r["counted_tokens"]) for r in run_recs)
        run_allow = sum(float(r["allowance_tokens"]) for r in run_recs)
        # Evidence class: a reported active-parameter count and no assumed missing-work
        # allowance mean no substantial assumed input entered the calculation.
        evidence = ("derived_supported_inputs" if basis == "reported" and run_allow == 0
                    else "derived_assumed_inputs")
        accounting = ("input_output" if link["cache_counters_reported"] == "0"
                      else "input_cache_creation_output")
        effort = link["reasoning_effort"]

        calc[run] = {
            "model_id": model_id, "endpoint": link["endpoint"], "log_url": link["log_url"],
            "flops_per_token": coefficient, "active_parameters_basis": basis,
            "compute_evidence": evidence, "tokens_accounting": accounting,
            "reasoning_effort": effort,
            "inspect_task": link["inspect_task"], "harness": link["harness"],
            "excluded_from_csv": EXCLUDED_RUNS.get(run),
            "run_total": {
                "instances": len(run_recs), "completed_evaluations": run_scored,
                "resolved": run_resolved,
                "recorded_counted_tokens": run_tokens,
                "missing_work_allowance_tokens": run_allow,
                "tokens_per_completed_evaluation": (run_tokens + run_allow) / run_scored,
                "parent_point_id": run if parent else None,
                "parent_tokens": float(parent["tokens"]) if parent else None,
                "parent_compute_flops": float(parent["compute_flops"]) if parent else None,
                "parent_human_time_s": float(parent["human_time"]) if parent else None,
            },
            "bins": {},
        }
        # The four bin rows must re-aggregate to the row they refine.
        if parent:
            assert abs(calc[run]["run_total"]["tokens_per_completed_evaluation"]
                       - float(parent["tokens"])) < 1e-6 * float(parent["tokens"]), run

        for label, key, human_s, prose, hbasis in BINS:
            group = grouped[(run, label)]
            n = len(group)
            scored = sum(int(r["scored"]) for r in group)
            resolved = sum(int(r["resolved"]) for r in group)
            counted = sum(float(r["counted_tokens"]) for r in group)
            allow = sum(float(r["allowance_tokens"]) for r in group)
            per_instance = [float(r["counted_tokens"]) + float(r["allowance_tokens"]) for r in group]
            tokens = (counted + allow) / scored
            flops = tokens * coefficient
            sd = statistics.stdev(per_instance) if n > 1 else 0.0
            se = sd / math.sqrt(n) if n > 1 else 0.0
            work = [float(r["working_time_s"]) for r in group if r["working_time_s"]]
            capped = sum(1 for r in group if float(r["counted_tokens"]) >= CAP_THRESHOLD)
            cap_pct = 100.0 * capped / n
            attention = attention_scenario(group, link, coefficient)
            attn_lo = attention["shapes"]["L=64, d=8192"]["ratio_to_compute_flops_lower"]

            point_id = "%s-%s" % (run, key)
            task = "Resolve a SWE-bench Verified issue (%s bin)" % label
            task_description = (
                "One issue-equivalent from the %d issues in Epoch's 484-issue SWE-bench Verified "
                "set carrying the original difficulty label '%s' (%s of estimated work): inspect "
                "the supplied issue and repository and implement a patch using %s. Success is "
                "assessed with fail-to-pass and regression tests. AI compute is the bin's total "
                "submitted workload amortized per completed evaluation in the bin, including "
                "incorrect answers." % (n, label, prose, link["harness"]))
            performance_evidence = (
                "AI passes native tests on %d/%d completed evaluations in this bin (%s%%), "
                "against %d of the run's %d completed evaluations (%s%%). Human target: a "
                "complete correct patch, conditional on solving; no observed human solve rate."
                % (resolved, scored, fmt_pct(resolved / scored), run_resolved, run_scored,
                   fmt_pct(run_resolved / run_scored)))
            source_record = (
                "%s; primary=%s; reasoning_effort=%s; Inspect task %s; difficulty label '%s', "
                "%d of 484 issues; performance: per-sample swe_bench_scorer in the same log; "
                "difficulty labels: https://huggingface.co/datasets/princeton-nlp/SWE-bench_Verified"
                % (link["log_url"], link["endpoint"], effort, link["inspect_task"], label, n))
            # reasoning_effort and the harness are carried in source_record, not repeated here.
            note = (NOTE_REFINES.format(parent=run) if parent else NOTE_NEW) + \
                NOTE_BASE.format(basis=hbasis, attn="%.2f" % attn_lo)
            if allow:
                note += (" A lost-response allowance adds %s%% of this bin's tokens."
                         % ("%.2g" % (100.0 * allow / counted)))
            if cap_pct >= CAP_NOTE_THRESHOLD:
                note += (" The 2M-token harness cap binds on %.1f%% of instances here, so the "
                         "mean is partly a floor." % cap_pct)
            if n <= 3:
                note += (" Only %d instances carry this label, standard error %s%% of the mean; "
                         "the bin mean is %.2fx the 1-4 hour bin's."
                         % (n, "%.0f" % (100.0 * se / (sum(per_instance) / n)),
                            tokens / calc[run]["bins"]["1-4 hours"]["tokens_per_completed_evaluation"]))

            row = {
                "point_id": point_id, "task": task, "task_category": "coding",
                "task_description": task_description, "model_id": model_id,
                "compute_scope": "inference", "compute_flops": repr(flops),
                "human_skill": "expert", "human_time_scope": "task_performance",
                "human_time": repr(human_s), "performance_vs_human": "below",
                "comparison_issues": "different_assessment; different_attempt_selection",
                "compute_evidence": evidence, "human_time_evidence": "assumed",
                "performance_evidence": performance_evidence,
                "human_time_statistic": "point_estimate", "human_time_subset": "not_applicable",
                "human_attempts": "not_applicable",
                "human_time_source": HUMAN_TIME_SOURCE,
                "human_time_method": "estimated", "compute_method": "params_tokens",
                "compute_statistic": "total_per_completed_sample", "compute_subset": "all",
                "ai_attempts": "not_applicable",
                "compute_source": "research/epoch-swebench-bins.md#%s" % point_id,
                "tokens": repr(tokens), "tokens_accounting": accounting,
                "source_dataset": "Epoch AI benchmarks", "source_record": source_record,
                "notes": note,
            }
            for field, limit in LIMITS.items():
                if len(row[field]) > limit:
                    raise SystemExit("%s: %s is %d characters, over the %d-character norm"
                                     % (point_id, field, len(row[field]), limit))
            if run not in EXCLUDED_RUNS:
                rows.append(row)

            calc[run]["bins"][label] = {
                "point_id": point_id, "instances": n, "completed_evaluations": scored,
                "resolved": resolved, "resolved_rate": resolved / scored,
                "recorded_counted_tokens": counted, "missing_work_allowance_tokens": allow,
                "tokens_per_completed_evaluation": tokens,
                "tokens_per_completed_evaluation_recorded_only": counted / scored,
                "compute_flops": flops,
                "instances_at_token_cap": capped, "percent_at_token_cap": cap_pct,
                "omitted_cached_context_attention": attention,
                "per_instance_sd": sd, "per_instance_se_of_mean": se,
                "se_over_mean": se / (sum(per_instance) / n) if n else None,
                "human_time_s": human_s, "human_time_basis": hbasis,
                "mean_input_tokens": sum(float(r["input_tokens"]) for r in group) / n,
                "mean_output_tokens": sum(float(r["output_tokens"]) for r in group) / n,
                "mean_cache_read_tokens": sum(float(r["cache_read_tokens"]) for r in group) / n,
                "mean_cache_write_tokens": sum(float(r["cache_write_tokens"]) for r in group) / n,
                "mean_reasoning_tokens": sum(float(r["reasoning_tokens"]) for r in group) / n,
                "mean_working_time_s": (sum(work) / len(work)) if work else None,
            }
            (bin_rows if run not in EXCLUDED_RUNS else excluded_bin_rows).append({
                "point_id": point_id, "run": run, "model_id": model_id,
                "endpoint": link["endpoint"], "inspect_task": link["inspect_task"],
                "difficulty": label, "instances": n,
                "completed_evaluations": scored, "resolved": resolved,
                "resolved_rate": "%.6f" % (resolved / scored),
                "tokens_per_completed_evaluation": "%.6f" % tokens,
                "tokens_recorded_only": "%.6f" % (counted / scored),
                "missing_work_allowance_tokens": "%.6f" % allow,
                "per_instance_se_of_mean": "%.3f" % se,
                "percent_at_token_cap": "%.1f" % cap_pct,
                "attention_ratio_L64_d8192_lower": "%.3f" % attn_lo,
                "flops_per_token": repr(coefficient), "compute_flops": repr(flops),
                "human_time_s": repr(human_s),
                "mean_working_time_s": ("%.3f" % (sum(work) / len(work))) if work else "",
            })

        # Alternative the coordinator may prefer: fold the three >4 h instances into the
        # 1-4 h bin.  Recorded here so the swap needs no re-derivation, not used by the rows.
        a, b = calc[run]["bins"]["1-4 hours"], calc[run]["bins"][">4 hours"]
        n_ab = a["instances"] + b["instances"]
        sc_ab = a["completed_evaluations"] + b["completed_evaluations"]
        tok_ab = (a["recorded_counted_tokens"] + a["missing_work_allowance_tokens"]
                  + b["recorded_counted_tokens"] + b["missing_work_allowance_tokens"]) / sc_ab
        calc[run]["folded_over_1_hour_bin"] = {
            "instances": n_ab, "completed_evaluations": sc_ab,
            "resolved": a["resolved"] + b["resolved"],
            "resolved_rate": (a["resolved"] + b["resolved"]) / sc_ab,
            "tokens_per_completed_evaluation": tok_ab,
            "compute_flops": tok_ab * coefficient,
            "human_time_s": (a["instances"] * a["human_time_s"]
                             + b["instances"] * b["human_time_s"]) / n_ab,
        }

        # Human-time consistency: the bin-weighted mean must equal the parent row's value.
        weighted = sum(calc[run]["bins"][b]["instances"] * calc[run]["bins"][b]["human_time_s"]
                       for b, *_ in [(x[0],) for x in BINS])
        weighted /= sum(calc[run]["bins"][b[0]]["instances"] for b in BINS)
        calc[run]["run_total"]["bin_weighted_human_time_s"] = weighted
        if parent:
            assert abs(weighted - float(parent["human_time"])) < 1e-9, run

    with open(args.out_points, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=HEADER)
        writer.writeheader()
        writer.writerows(rows)
    with open(args.out_bins, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(bin_rows[0].keys()))
        writer.writeheader()
        writer.writerows(bin_rows)
    with open(args.out_calc, "w") as fh:
        json.dump(calc, fh, indent=1, sort_keys=True)
        fh.write("\n")

    print("rows=%d -> %s" % (len(rows), args.out_points))
    return 0


if __name__ == "__main__":
    sys.exit(main())
