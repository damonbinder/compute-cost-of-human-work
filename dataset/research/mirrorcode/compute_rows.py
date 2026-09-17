#!/usr/bin/env python3
"""Compute the MirrorCode candidate rows' FLOPs, token totals and scenarios.

Dependencies: Python 3.9+ standard library only.

Inputs (explicit paths, no implied layout):
  --run-records   CSV of the 19 public MirrorCode run records, one row per run,
                  as retained at agent-work/sources/mirrorcode/mirrorcode-run-records.csv
  --models        models.csv supplying flops_per_token per model_id; the dataset
                  registry at ../AI Compute vs Human Time/dataset/models.csv is
                  read-only and is only read here
  --out           JSON file to write (created or overwritten; no input is modified)

Usage:
  python3 compute_rows.py \
    --run-records /abs/path/sources/mirrorcode/mirrorcode-run-records.csv \
    --models      /abs/path/dataset/models.csv \
    --out         /abs/path/research/mirrorcode/calculations.json

Method:
  compute_flops = (input_tokens + cache_write + output_tokens) * flops_per_token,
  i.e. the dataset's cache rule: fresh input plus cache creation plus output,
  cache reads excluded. Anthropic's Inspect counters are additive, verified here
  by checking input + cache_write + cache_read + output == total_tokens for every
  record. reasoning_tokens are a subset of output_tokens under the Anthropic
  convention and are not added again.

  Cached-context attention is omitted by the 2*active_parameters convention and is
  priced separately as a one-sided scenario, using 4*layers*d_model*context per
  processed position at the mean per-call prefix
  (input + cache_write + cache_read) / assistant_messages.
"""
import argparse, csv, json, statistics

# Reference lines of code of the target program, from MirrorCode's own tables.
# Blog (April 2026) "Description of MirrorCode target programs"; paper Table 3 rounds these.
TARGET_LOC = {"gotree": 16905, "pkl": 61461, "cal": 984, "choose": 931}

# End-to-end test cases scored in these runs, from the same blog table, and confirmed by the
# row counts of each run's cases.jsonl. The second work quantity MirrorCode publishes, carried
# as a named sensitivity on the human-time transfer; lines of code stay the central proxy.
TARGET_TESTS = {"gotree": 2001, "pkl": 770, "cal": 1365, "choose": 127}

# Four MirrorCode contributors' estimates for a skilled engineer to reimplement
# gotree without AI assistance, passing all test cases, given only the information
# MirrorCode provides. Epoch blog footnote 20 / paper section 4. Weeks, low-high.
GOTREE_ESTIMATE_WEEKS = [(1.5, 2.5), (13.0, 17.0), (3.0, 3.0), (13.0, 13.0)]
HOURS_PER_FULLTIME_WEEK = 40.0   # 2,000 active hours per person-year over 50 weeks

# Bracketing decoder shapes for the omitted cached-context attention term, matching
# the brackets used by the accepted Portal row in this folder.
ATTENTION_SHAPES = [("L=64, d=8192", 64, 8192), ("L=80, d=10240", 80, 10240), ("L=96, d=12288", 96, 12288)]

# Effort-versus-size scenarios for the transfer off gotree. The central transfer is
# linear in reference LoC, which is the rule Epoch itself applies in blog footnote 21.
SIZE_EXPONENTS = [0.8, 1.0, 1.2]

# Epoch's own soft lower bound, blog footnote 21: one human SWE did not complete a
# simpler 2,000-LoC MirrorCode task in 20 hours, passing 42% of test cases; Epoch
# extrapolates that rate linearly by LoC and calls the result a soft lower bound.
BASELINE_HOURS, BASELINE_LOC, BASELINE_PASS_RATE = 20.0, 2000, 0.42

# The 13 candidate rows: point_id -> (target, language, model_id, [run_path substrings])
ROW_GROUPS = [
    ("agen-mirrorcode-gotree-py-opus4",    "gotree", "Python", "claude-opus-4",   "mZ5ASFjJSMr7JZ4p9vUK83"),
    ("agen-mirrorcode-gotree-py-opus41",   "gotree", "Python", "claude-opus-4-1", "MQs95W4LcHNevN9cr7Ygfy"),
    ("agen-mirrorcode-gotree-py-opus45",   "gotree", "Python", "claude-opus-4-5", "6H9RmCuEeK8khuibQggYCD"),
    ("agen-mirrorcode-gotree-py-opus46",   "gotree", "Python", "claude-opus-4-6", "2Eq9UuTDq9T6rmYyGKyADg"),
    ("agen-mirrorcode-pkl-c-opus46",       "pkl",    "C",      "claude-opus-4-6", "pkl_c"),
    ("agen-mirrorcode-pkl-py-opus46",      "pkl",    "Python", "claude-opus-4-6", "pkl_python"),
    ("agen-mirrorcode-pkl-rust-opus46",    "pkl",    "Rust",   "claude-opus-4-6", "pkl_rust"),
    ("agen-mirrorcode-cal-c-opus46",       "cal",    "C",      "claude-opus-4-6", "cal_c"),
    ("agen-mirrorcode-cal-py-opus46",      "cal",    "Python", "claude-opus-4-6", "cal_python"),
    ("agen-mirrorcode-cal-rust-opus46",    "cal",    "Rust",   "claude-opus-4-6", "cal_rust"),
    ("agen-mirrorcode-choose-c-opus46",    "choose", "C",      "claude-opus-4-6", "choose_c"),
    ("agen-mirrorcode-choose-py-opus46",   "choose", "Python", "claude-opus-4-6", "choose_python"),
    ("agen-mirrorcode-choose-rust-opus46", "choose", "Rust",   "claude-opus-4-6", "choose_rust"),
]


def load_records(path):
    out = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            for k in ("input_tokens", "cache_write", "cache_read", "output_tokens",
                      "total_tokens", "uncached_in_cw_out", "assistant_messages",
                      "tests_passed", "tests_total", "visible_passed", "visible_total",
                      "hidden_passed", "hidden_total", "compactions"):
                r[k] = int(r[k]) if r[k] not in ("", None) else None
            out.append(r)
    return out


def load_coefficients(path):
    coef = {}
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            try:
                coef[r["model_id"]] = float(r["flops_per_token"])
            except (TypeError, ValueError):
                pass
    return coef


def human_time_seconds():
    mids = [(lo + hi) / 2.0 for lo, hi in GOTREE_ESTIMATE_WEEKS]
    mean_weeks = statistics.fmean(mids)
    gotree_hours = mean_weeks * HOURS_PER_FULLTIME_WEEK
    rate = gotree_hours / TARGET_LOC["gotree"]          # active hours per reference LoC
    test_rate = gotree_hours / TARGET_TESTS["gotree"]   # active hours per end-to-end test case
    lo_weeks = min(lo for lo, _ in GOTREE_ESTIMATE_WEEKS)
    hi_weeks = max(hi for _, hi in GOTREE_ESTIMATE_WEEKS)
    per_target = {}
    for t, loc in TARGET_LOC.items():
        if t == "gotree":
            hours, basis = gotree_hours, "four contributor estimates, arithmetic mean of midpoints"
        else:
            hours, basis = loc * rate, "reference LoC times the gotree-calibrated rate"
        per_target[t] = {
            "reference_loc": loc,
            "active_hours": round(hours, 2),
            "seconds": int(round(hours * 3600)),
            "estimator_spread_low_hours": round(hours * (lo_weeks / mean_weeks), 2),
            "estimator_spread_high_hours": round(hours * (hi_weeks / mean_weeks), 2),
            "size_exponent_hours": {
                str(e): round(gotree_hours * (loc / TARGET_LOC["gotree"]) ** e, 2) for e in SIZE_EXPONENTS
            },
            "epoch_soft_lower_bound_hours": round(loc * BASELINE_HOURS / BASELINE_LOC, 2),
            "end_to_end_tests": TARGET_TESTS[t],
            "test_count_transfer_hours": round(TARGET_TESTS[t] * test_rate, 2),
            "basis": basis,
        }
    return {
        "gotree_estimates_weeks": GOTREE_ESTIMATE_WEEKS,
        "midpoints_weeks": mids,
        "mean_weeks": mean_weeks,
        "hours_per_fulltime_week": HOURS_PER_FULLTIME_WEEK,
        "rate_active_hours_per_1000_loc": round(rate * 1000, 4),
        "rate_active_hours_per_test_case": round(test_rate, 6),
        "test_count_transfer_note": (
            "Second work-quantity transfer off the same donor, kept as a sensitivity only. It agrees "
            "with the lines-of-code transfer for choose and disagrees by about an order of magnitude "
            "in opposite directions for cal and pkl. Lines of code stays central because the "
            "test-count proxy makes pkl 1.2 times gotree, against a source that expects months for "
            "pkl; a proxy that fails that check is not a co-equal transfer, so the geometric-mean "
            "rule for two defensible transfers does not apply."),
        "median_weeks": statistics.median(mids),
        "scenario_span_weeks": [lo_weeks, hi_weeks],
        "epoch_soft_lower_bound": {
            "source": "Epoch blog footnote 21",
            "baseline_hours": BASELINE_HOURS, "baseline_loc": BASELINE_LOC,
            "baseline_pass_rate": BASELINE_PASS_RATE,
            "note": "one human SWE, incomplete at 20 hours; linear LoC extrapolation, a soft lower bound only",
        },
        "targets": per_target,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-records", required=True)
    ap.add_argument("--models", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    recs = load_records(a.run_records)
    coef = load_coefficients(a.models)

    counter_check = []
    for r in recs:
        s = r["input_tokens"] + r["cache_write"] + r["cache_read"] + r["output_tokens"]
        counter_check.append({"run_path": r["run_path"], "sum_equals_total": s == r["total_tokens"]})
    assert all(c["sum_equals_total"] for c in counter_check), "Anthropic counters are not additive"

    human = human_time_seconds()
    rows = []
    for pid, target, lang, model_id, key in ROW_GROUPS:
        sel = [r for r in recs if r["target"] == target and r["language"] == lang and key in r["run_path"]]
        assert sel, pid
        unc = [r["uncached_in_cw_out"] for r in sel]
        tokens = statistics.fmean(unc)
        fpt = coef[model_id]
        flops = tokens * fpt
        prefix = [(r["input_tokens"] + r["cache_write"] + r["cache_read"]) / r["assistant_messages"]
                  for r in sel if r["assistant_messages"]]
        mean_ctx = statistics.fmean(prefix) if prefix else None
        attn = {}
        if mean_ctx:
            for label, L, d in ATTENTION_SHAPES:
                attn[label] = {
                    "flops": tokens * 4 * L * d * mean_ctx,
                    "ratio_to_central": (tokens * 4 * L * d * mean_ctx) / flops,
                }
        rows.append({
            "point_id": pid, "target": target, "language": lang, "model_id": model_id,
            "ai_attempts": len(sel),
            "compute_statistic": "mean" if len(sel) > 1 else "total",
            "runs": [r["run_path"] for r in sel],
            "uncached_tokens_per_run": unc,
            "tokens": tokens,
            "flops_per_token": fpt,
            "compute_flops": flops,
            "billed_total_tokens_per_run": [r["total_tokens"] for r in sel],
            "cache_read_per_run": [r["cache_read"] for r in sel],
            "output_tokens_per_run": [r["output_tokens"] for r in sel],
            "assistant_messages_per_run": [r["assistant_messages"] for r in sel],
            "mean_prefix_tokens_per_call": mean_ctx,
            "tests_passed_per_run": [r["tests_passed"] for r in sel],
            "tests_total_per_run": [r["tests_total"] for r in sel],
            "visible_per_run": [(r["visible_passed"], r["visible_total"]) for r in sel],
            "hidden_per_run": [(r["hidden_passed"], r["hidden_total"]) for r in sel],
            "human_time_seconds": human["targets"][target]["seconds"],
            "human_time_hours": human["targets"][target]["active_hours"],
            "cached_context_attention_scenarios": attn,
            "full_prefix_scenario_flops": statistics.fmean([r["total_tokens"] for r in sel]) * fpt,
        })

    out = {
        "method": {
            "compute": "params_tokens on input + cache_write + output; cache reads excluded",
            "reasoning_tokens": "subset of output_tokens under the Anthropic convention; not added again",
            "attention_scenario": "4 * layers * d_model * mean_prefix per processed position",
            "human_time": "2,000 active hours per person-year; a full-time week is 40 active hours",
        },
        "counter_additivity_check": counter_check,
        "human_time_derivation": human,
        "rows": rows,
    }
    with open(a.out, "w") as f:
        json.dump(out, f, indent=1)
    for r in rows:
        print(f"{r['point_id']:<38} n={r['ai_attempts']} tokens={r['tokens']:>12,.0f} "
              f"flops={r['compute_flops']:.4e} human_s={r['human_time_seconds']:>9} "
              f"ctx={r['mean_prefix_tokens_per_call']:>9,.0f}")


if __name__ == "__main__":
    main()
