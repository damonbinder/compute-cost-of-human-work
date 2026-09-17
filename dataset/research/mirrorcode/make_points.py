#!/usr/bin/env python3
"""Emit candidates/mirrorcode/points.csv and models.csv with the root headers.

Dependencies: Python 3.9+ standard library only.

Inputs (explicit paths, no implied layout):
  --calculations  the JSON written by compute_rows.py
  --points-out    points.csv to write (created or overwritten)
  --models-out    models.csv to write; header only, because all four models already
                  exist in the dataset registry and are reused unchanged

Usage:
  python3 make_points.py \
    --calculations /abs/path/research/mirrorcode/calculations.json \
    --points-out   /abs/path/candidates/mirrorcode/points.csv \
    --models-out   /abs/path/candidates/mirrorcode/models.csv

Every text field is checked against the CSV length norms in DECISIONS.md before writing;
the script exits non-zero rather than emitting an over-long field.
"""
import argparse, csv, json, os, sys

LIMITS = {"notes": 586, "task_description": 560, "performance_evidence": 337,
          "source_record": 455, "compute_source": 220, "human_time_source": 205}

POINTS_HEADER = ["point_id", "task", "task_category", "task_description", "model_id",
"compute_scope", "compute_flops", "human_skill", "human_time_scope", "human_time",
"performance_vs_human", "comparison_issues", "compute_evidence", "human_time_evidence",
"performance_evidence", "human_time_statistic", "human_time_subset", "human_attempts",
"human_time_source", "human_time_method", "compute_method", "compute_statistic",
"compute_subset", "ai_attempts", "compute_source", "tokens", "tokens_accounting",
"source_dataset", "source_record", "notes"]

MODELS_HEADER = ["model_id", "model", "company", "model_release_date", "model_release_source",
"flops_per_token", "flops_per_token_method", "active_parameters", "active_parameters_basis",
"encoder_parameters", "encoder_parameters_basis", "decoder_parameters",
"decoder_parameters_basis", "parameter_source", "notes"]

REPO = "https://github.com/epoch-research/MirrorCode-data"
BLOG = "https://epoch.ai/blog/mirrorcode-preliminary-results"
PAPER = "https://arxiv.org/abs/2606.30182"
DATASET = "MirrorCode preliminary runs, Epoch AI, March 2026"

TASK_DESC = {
 ("gotree", "Python"): "One autonomous agent run reimplementing gotree, a 16,905-line Go phylogenetics toolkit, in Python from behavior alone. The agent has execute-only access to the reference binary, its documentation and 1,899 visible test cases, with no source access, internet or third-party libraries, and works until it calls submit under a one-billion-token budget. Completion is byte-identical stdout, stderr and exit code on all 2,001 cases, the 102 hidden ones graded where the agent cannot reach. The human unit is one engineer reimplementing gotree to that criterion.",
 ("pkl", "{L}"): "One autonomous agent run reimplementing a scoped subset of pkl eval, the evaluator of Apple's 61,461-line Java configuration language, in {L} from behavior alone. The agent has the reference binary execute-only, the documentation, 733 visible cases and the Pkl standard library source, but not the evaluator's own source, and no internet. Command-line flags, the binary module, Pkl projects and every URI scheme but file: are out of scope. Completion is byte-identical stdout, stderr and exit code on all 770 cases, the 37 hidden ones graded out of reach.",
 ("cal", "{L}"): "One autonomous agent run reimplementing cal, the 984-line util-linux calendar utility, in {L} from behavior alone. Byte-exact output is required for the default, --monday, --week, vertical multi-month and day-of-year layouts and for the 1752 Julian-to-Gregorian reform; other locales and coloring are out of scope. The agent has execute-only access to the reference binary, its manual and 764 visible cases, with no source access or internet, and works until it calls submit. Completion is matching stdout, stderr and exit code on all 1,365 cases.",
 ("choose", "{L}"): "One autonomous agent run reimplementing choose, a 931-line Rust field-selection tool in the style of cut and awk, in {L} from behavior alone. The agent has execute-only access to the reference binary, its documentation and 127 visible test cases, with no source access, internet or third-party libraries, and works until it calls submit under a one-billion-token budget. Completion is byte-identical stdout, stderr and exit code on every scored case, which for this run means the 127 visible cases.",
}

PERF = {
"agen-mirrorcode-gotree-py-opus4": "All three recorded episodes fell far short of the 2,001-case criterion, passing 24, 307 and 196 cases, that is 1.2%, 15.3% and 9.8%, with 0, 263 and 153 of 1,899 visible cases. The human baseline is an assumed complete pass by a skilled engineer, not an observed human result.",
"agen-mirrorcode-gotree-py-opus41": "The three episodes passed 317, 471 and 152 of 2,001 cases, that is 15.8%, 23.5% and 7.6%, with 286, 441 and 133 of 1,899 visible cases. None approached the completion criterion. The human baseline is an assumed complete pass by a skilled engineer, not an observed human result.",
"agen-mirrorcode-gotree-py-opus45": "The three episodes passed 946, 75 and 1,265 of 2,001 cases, that is 47.3%, 3.7% and 63.2%. The best wrote code for almost every subcommand but failed 723 visible cases; the worst passed no visible case at all. The human baseline is an assumed complete pass by a skilled engineer, not an observed human result.",
"agen-mirrorcode-gotree-py-opus46": "The single run passed 2,000 of 2,001 cases: all 1,899 visible and 101 of 102 hidden, failing one hidden gotree cut date edge case where the date boundary falls on a node. Epoch calls the target effectively solved. The human baseline is an assumed complete pass by a skilled engineer.",
"agen-mirrorcode-pkl-c-opus46": "The run passed 321 of 770 cases, 41.7%, being 307 of 733 visible and 14 of 37 hidden, after spending 90% of the one-billion-token budget. Epoch reports pkl unsolved under that budget. The human baseline is an assumed complete pass by a skilled engineer, not an observed human result.",
"agen-mirrorcode-pkl-py-opus46": "The scoring pass for this run crashed and no score exists for it. The label is transferred from the same model, target and budget in C and Rust, which passed 41.7% and 35.5%, and from Epoch's statement that pkl went unsolved under that budget. The human baseline is an assumed complete pass by a skilled engineer.",
"agen-mirrorcode-pkl-rust-opus46": "The run passed 273 of 770 cases, 35.5%, being 256 of 733 visible and 17 of 37 hidden, after spending 90% of the one-billion-token budget. Its solution evaluated eagerly throughout a lazily evaluated language. The human baseline is an assumed complete pass by a skilled engineer.",
"agen-mirrorcode-cal-c-opus46": "The run passed 1,365 of 1,365 cases, all 764 visible and all 601 hidden, meeting the benchmark's 100% completion criterion with the held-out suite exercised. The human baseline is an assumed complete pass by a skilled engineer, not an observed human result.",
"agen-mirrorcode-cal-py-opus46": "The run passed 1,363 of 1,365 cases, 99.85%, being all 764 visible and 599 of 601 hidden: two short of the 100% criterion and inside the benchmark's 99% substantial-reimplementation band. The human baseline is an assumed complete pass by a skilled engineer.",
"agen-mirrorcode-cal-rust-opus46": "The run passed 1,365 of 1,365 cases, all 764 visible and all 601 hidden, meeting the benchmark's 100% completion criterion with the held-out suite exercised. The human baseline is an assumed complete pass by a skilled engineer, not an observed human result.",
"agen-mirrorcode-choose-c-opus46": "The run passed all 127 cases scored, every one of them visible. The eval set held no hidden cases, so the 122 hidden duals the benchmark later added were not applied. The human baseline is an assumed complete pass by a skilled engineer, not an observed human result.",
"agen-mirrorcode-choose-py-opus46": "The run passed all 127 cases scored, every one of them visible. The eval set held no hidden cases, so the 122 hidden duals the benchmark later added were not applied. The human baseline is an assumed complete pass by a skilled engineer, not an observed human result.",
"agen-mirrorcode-choose-rust-opus46": "The run passed all 127 cases scored, every one of them visible. The eval set held no hidden cases, so the 122 hidden duals the benchmark later added were not applied. The human baseline is an assumed complete pass by a skilled engineer, not an observed human result.",
}

RUNPATH = {
"agen-mirrorcode-gotree-py-opus4": "eval_sets/gotree-oldopus-v01-ns5k39b82nbd4vre/2026-03-30T12-14-54+00-00_MirrorCode_mZ5ASFjJSMr7JZ4p9vUK83.fast_plaintext/gotree_python_ep001 to ep003",
"agen-mirrorcode-gotree-py-opus41": "eval_sets/gotree-oldopus-v01-ns5k39b82nbd4vre/2026-03-30T12-14-54+00-00_MirrorCode_MQs95W4LcHNevN9cr7Ygfy.fast_plaintext/gotree_python_ep001 to ep003",
"agen-mirrorcode-gotree-py-opus45": "eval_sets/gotree-oldopus-v01-ns5k39b82nbd4vre/2026-03-30T12-14-54+00-00_MirrorCode_6H9RmCuEeK8khuibQggYCD.fast_plaintext/gotree_python_ep001 to ep003",
"agen-mirrorcode-gotree-py-opus46": "eval_sets/gotree-v03-w0yrevhbo2ep6388/2026-03-29T20-02-04+00-00_MirrorCode_2Eq9UuTDq9T6rmYyGKyADg.fast_plaintext/gotree_python",
"agen-mirrorcode-pkl-c-opus46": "eval_sets/ben-202603-mc-sc-opus-4-6-1b-v1-p1/pkl_c",
"agen-mirrorcode-pkl-py-opus46": "eval_sets/ben-202603-mc-sc-opus-4-6-1b-v1-p1/pkl_python",
"agen-mirrorcode-pkl-rust-opus46": "eval_sets/ben-202603-mc-sc-opus-4-6-1b-v1-p1/pkl_rust",
"agen-mirrorcode-cal-c-opus46": "eval_sets/compaction-sc-secure-opus-4-6-v1-p1/cal_c",
"agen-mirrorcode-cal-py-opus46": "eval_sets/compaction-sc-secure-opus-4-6-v1-p1/cal_python",
"agen-mirrorcode-cal-rust-opus46": "eval_sets/compaction-sc-secure-opus-4-6-v1-p1/cal_rust",
"agen-mirrorcode-choose-c-opus46": "eval_sets/compaction-sc-secure-opus-4-6-v1-p1/choose_c",
"agen-mirrorcode-choose-py-opus46": "eval_sets/compaction-sc-secure-opus-4-6-v1-p1/choose_python",
"agen-mirrorcode-choose-rust-opus46": "eval_sets/compaction-sc-secure-opus-4-6-v1-p1/choose_rust",
}

ALIAS = {"claude-opus-4": "anthropic/claude-opus-4-20250514",
         "claude-opus-4-1": "anthropic/claude-opus-4-1-20250805",
         "claude-opus-4-5": "anthropic/claude-opus-4-5-20251101",
         "claude-opus-4-6": "anthropic/claude-opus-4-6"}

PERF_LABEL = {"agen-mirrorcode-gotree-py-opus4": "below", "agen-mirrorcode-gotree-py-opus41": "below",
"agen-mirrorcode-gotree-py-opus45": "below", "agen-mirrorcode-gotree-py-opus46": "match",
"agen-mirrorcode-pkl-c-opus46": "below", "agen-mirrorcode-pkl-py-opus46": "below",
"agen-mirrorcode-pkl-rust-opus46": "below", "agen-mirrorcode-cal-c-opus46": "match",
"agen-mirrorcode-cal-py-opus46": "match", "agen-mirrorcode-cal-rust-opus46": "match",
"agen-mirrorcode-choose-c-opus46": "match", "agen-mirrorcode-choose-py-opus46": "match",
"agen-mirrorcode-choose-rust-opus46": "match"}

EXTRA_NOTE = {
"agen-mirrorcode-gotree-py-opus4": "Episode 1 passed hidden cases only, so its submission did not run against the visible suite.",
"agen-mirrorcode-gotree-py-opus41": "",
"agen-mirrorcode-gotree-py-opus45": "Episode tokens were 1.16M, 13.78M and 1.64M; the mean is 3.4 times the median, episode 2 having thrashed the cache.",
"agen-mirrorcode-gotree-py-opus46": "Only one episode was run for this model.",
"agen-mirrorcode-pkl-c-opus46": "",
"agen-mirrorcode-pkl-py-opus46": "Its scoring step crashed; the agent's work completed and its counters are intact.",
"agen-mirrorcode-pkl-rust-opus46": "",
"agen-mirrorcode-cal-c-opus46": "", "agen-mirrorcode-cal-py-opus46": "",
"agen-mirrorcode-cal-rust-opus46": "", "agen-mirrorcode-choose-c-opus46": "",
"agen-mirrorcode-choose-py-opus46": "", "agen-mirrorcode-choose-rust-opus46": "",
}

TASKNAME = {"gotree": "Reimplement gotree from its behavior alone",
            "pkl": "Reimplement pkl eval from its behavior alone",
            "cal": "Reimplement cal from its behavior alone",
            "choose": "Reimplement choose from its behavior alone"}


def build(calc):
    rows = []
    for r in calc["rows"]:
        pid, tgt, lang = r["point_id"], r["target"], r["language"]
        attn = [v["ratio_to_central"] for v in r["cached_context_attention_scenarios"].values()]
        crshare = 100.0 * sum(r["cache_read_per_run"]) / sum(r["billed_total_tokens_per_run"])
        shared = (f"Cache reads, {crshare:.0f}% of billed tokens, are excluded; tokens are fresh input, cache "
                  f"creation and output, with reasoning already inside output. The coefficient omits attention "
                  f"over a mean prefix of {r['mean_prefix_tokens_per_call']:,.0f} tokens, adding {attn[0]:.2f} "
                  f"to {attn[-1]:.2f} times the value. ")
        if tgt == "gotree":
            human = ("Human time is the mean of four contributors' estimates for gotree, 1.5-2.5, 13-17, 3 and 13 "
                     "weeks at 40 active hours a week; the span is 60 to 680 hours. ")
            stat, method = "point_estimate", "estimated"
            hsrc = f"{BLOG} footnote 20; {PAPER} section 4; research/mirrorcode.md#human-baseline"
        else:
            t = calc["human_time_derivation"]["targets"][tgt]
            tail = {
              "pkl": "that count is the whole codebase, so 1,200 hours is an upper anchor for the scoped task",
              "cal": ("lines of code is the weakest proxy for cal and one-sided downward there, the same donor "
                      "transferred by test count giving 225 hours"),
              "choose": "transferring the same donor by test count instead gives 20.9 hours",
            }[tgt]
            human = (f"Human time is {t['reference_loc']:,} reference lines of code at 19.5 active hours per 1,000, "
                     f"the rate the four gotree contributor estimates imply; {tail}. ")
            stat, method = "point_estimate", "estimated"
            hsrc = f"research/mirrorcode.md#human-baseline; {BLOG} footnotes 20 and 21; {PAPER} section 4"
        rows.append({
            "point_id": pid, "task": TASKNAME[tgt], "task_category": "coding",
            "task_description": (TASK_DESC.get((tgt, lang)) or TASK_DESC[(tgt, "{L}")].replace("{L}", lang)),
            "model_id": r["model_id"], "compute_scope": "inference",
            "compute_flops": repr(float(r["compute_flops"])), "human_skill": "expert",
            "human_time_scope": "task_performance", "human_time": r["human_time_seconds"],
            "performance_vs_human": PERF_LABEL[pid],
            "comparison_issues": ("different_assessment" if tgt == "choose" else "none_identified"),
            "compute_evidence": "derived_assumed_inputs", "human_time_evidence": "assumed",
            "performance_evidence": PERF[pid], "human_time_statistic": stat,
            "human_time_subset": "not_applicable", "human_attempts": "not_applicable",
            "human_time_source": hsrc, "human_time_method": method, "compute_method": "params_tokens",
            "compute_statistic": r["compute_statistic"], "compute_subset": "all",
            "ai_attempts": r["ai_attempts"],
            "compute_source": (f"research/mirrorcode.md#{pid}; research/mirrorcode/calculations.json; "
                               f"agent-work/sources/mirrorcode/mirrorcode-run-records.csv"),
            "tokens": (repr(r["tokens"]) if r["ai_attempts"] > 1 else f"{r['tokens']:.0f}"),
            "tokens_accounting": "input_cache_creation_output", "source_dataset": DATASET,
            "source_record": (f"{REPO} at branch main: {RUNPATH[pid]}, files info.json and scores.txt, model "
                              f"{ALIAS[r['model_id']]}. Extracts in agent-work/sources/mirrorcode/MANIFEST.md, performance: "
                              f"the same scores.txt and {BLOG}"),
            "notes": (shared + human + "Parameter size is assumed. " + EXTRA_NOTE[pid]).strip()})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--calculations", required=True)
    ap.add_argument("--points-out", required=True)
    ap.add_argument("--models-out", required=True)
    a = ap.parse_args()
    rows = build(json.load(open(a.calculations)))

    bad = [(row["point_id"], f, len(row[f]), lim)
           for row in rows for f, lim in LIMITS.items() if len(row[f]) > lim]
    if bad:
        for b in bad:
            print("TOO LONG:", b, file=sys.stderr)
        sys.exit(1)

    for path in (a.points_out, a.models_out):
        os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(a.points_out, "w", newline="") as f:
        w = csv.DictWriter(f, POINTS_HEADER); w.writeheader(); w.writerows(rows)
    with open(a.models_out, "w", newline="") as f:
        csv.DictWriter(f, MODELS_HEADER).writeheader()
    print(f"wrote {len(rows)} rows to {a.points_out}")
    print(f"wrote header-only models.csv to {a.models_out}")
    for row in rows:
        print(f"  {row['point_id']:<38} {float(row['compute_flops']):.4e} {row['human_time']:>9} "
              f"{row['performance_vs_human']:<6} {row['comparison_issues']}")


if __name__ == "__main__":
    main()
