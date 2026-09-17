#!/usr/bin/env python3
"""Build the METR RE-Bench candidate rows from the digitized figure data.

Input   the CSV written by digitize_figures.py
Output  points.csv (35 columns, COLUMNS.md order), a calculations JSON holding every
        intermediate, and a dispositions CSV for the cells that are not rows.

The arithmetic, in one place:

  per-run cost   Figure 11 plots each configuration's cost budget against its
                 score@k. Matching each marker's score to the score@k tables of
                 Figures 7 and 8 fixes its k, and cost/k is that configuration's
                 cost for one run at its own run limit. The four to five markers
                 per configuration agree to about 1%, which is the check that the
                 log cost axis has been read correctly; the human markers land on
                 the $1,855 per 8-hour attempt the paper states in words.

  budget cost    k * per-run cost, with k set by the allocation the paper says is
                 best for that scaffold at that total time budget (Section 4.2 and
                 the Figure 2 caption: 30-minute runs for Modular, 2-hour runs for
                 AIDE at budgets of 2 hours or more).

  tokens         Figure 12 gives, per configuration, the median completion tokens
                 per second during API time and the median share of run time spent
                 waiting on completion requests. Their product times the run limit
                 is output tokens per run. Subtracting the output cost from the run
                 cost and dividing by the input price gives input tokens per run, so
                 the input-to-output split is measured per configuration rather than
                 transferred. The paper's pooled 29M/499K = 58.12 is kept only as a
                 cross-check, and it is refuted per configuration: see
                 research/rebench.md. The band scales the measured output rate by
                 0.5 and 1.5, which is what the median-of-a-product assumption and
                 the violin spreads warrant.

  FLOPs          tokens * flops_per_token from the Codex model registry
                 (2e11 for both Claude 3.5 Sonnet revisions, 1e11 for o1-preview).

Dependencies: Python standard library only.

Usage:
    python3 make_rows.py <figure-data.csv> <out-points.csv> <out-calculations.json> <out-dispositions.csv>
"""
import csv
import json
import math
import sys

# ---------------------------------------------------------------- source facts
POOLED_INPUT = 29.0e6        # paper Section 6.2, per 8-hour run, pooled over agents
POOLED_OUTPUT = 0.499e6      # paper Section 6.2
POOLED_COST = 123.0          # paper Section 6.2
HUMAN_PAY_PER_ATTEMPT = 1855.0   # paper Section 6.2
HUMAN_MEAN_8H_TABLE5 = 0.64      # paper Table 5, 71 attempts by 61 experts

PRICES = {                   # research/cost/list-prices.csv, in force 2024-10/11
    "claude-3-5-sonnet-20241022": (3.0e-6, 15.0e-6),
    "claude-3-5-sonnet-20240620": (3.0e-6, 15.0e-6),
    "o1-preview-2024-09-12": (15.0e-6, 60.0e-6),
}
FLOPS_PER_TOKEN = {          # ../AI Compute vs Human Time/dataset/models.csv
    "claude-3-5-sonnet-20241022": 2.0e11,
    "claude-3-5-sonnet-20240620": 2.0e11,
    "o1-preview-2024-09-12": 1.0e11,
}

CONFIGS = {
    "claude-3-5-sonnet-20240620 / Modular": dict(
        model="claude-3-5-sonnet-20240620", scaffold="Modular", limit="30min",
        slug="sonnet35old-modular", runs_per_hour=2),
    "claude-3-5-sonnet-20241022 / Modular": dict(
        model="claude-3-5-sonnet-20241022", scaffold="Modular", limit="30min",
        slug="sonnet35new-modular", runs_per_hour=2),
    "claude-3-5-sonnet-20241022 / AIDE": dict(
        model="claude-3-5-sonnet-20241022", scaffold="AIDE", limit="2h",
        slug="sonnet35new-aide", runs_per_hour=0.5),
    "o1-preview / AIDE": dict(
        model="o1-preview-2024-09-12", scaffold="AIDE", limit="2h",
        slug="o1preview-aide", runs_per_hour=0.5),
}

# Figure 11 marker -> (run limit, k), fixed by matching each marker's score to the
# score@k tables of Figures 7 and 8. Costs in USD as digitized.
F11_K = {
    ("claude-3-5-sonnet-20240620 / Modular", 30.69): ("30min", 4),
    ("claude-3-5-sonnet-20240620 / Modular", 121.87): ("30min", 16),
    ("claude-3-5-sonnet-20240620 / Modular", 244.19): ("30min", 32),
    ("claude-3-5-sonnet-20240620 / Modular", 488.93): ("30min", 64),
    ("claude-3-5-sonnet-20241022 / Modular", 6.65): ("30min", 1),
    ("claude-3-5-sonnet-20241022 / Modular", 26.13): ("30min", 4),
    ("claude-3-5-sonnet-20241022 / Modular", 106.08): ("30min", 16),
    ("claude-3-5-sonnet-20241022 / Modular", 211.74): ("30min", 32),
    ("claude-3-5-sonnet-20241022 / Modular", 842.52): ("30min", 128),
    ("claude-3-5-sonnet-20241022 / AIDE", 2.71): ("30min", 1),
    ("claude-3-5-sonnet-20241022 / AIDE", 10.88): ("2h", 1),
    ("claude-3-5-sonnet-20241022 / AIDE", 43.69): ("2h", 4),
    ("claude-3-5-sonnet-20241022 / AIDE", 86.66): ("2h", 8),
    ("claude-3-5-sonnet-20241022 / AIDE", 174.35): ("2h", 16),
    ("o1-preview / AIDE", 7.33): ("30min", 1),
    ("o1-preview / AIDE", 29.37): ("2h", 1),
    ("o1-preview / AIDE", 117.74): ("2h", 4),
    ("o1-preview / AIDE", 235.74): ("2h", 8),
    ("o1-preview / AIDE", 467.25): ("2h", 16),
    ("human", 467.82): ("8h", 0.25),
    ("human", 1856.42): ("8h", 1),
    ("human", 3720.65): ("8h", 2),
    ("human", 7442.92): ("8h", 4),
    ("human", 14896.09): ("8h", 8),
}

BUDGETS = {   # total agent hours -> human seconds, human attempts in the budget
    2: dict(human_seconds=7200, human_attempts_in_budget=0.25, label="2h"),
    8: dict(human_seconds=28800, human_attempts_in_budget=1, label="8h"),
    32: dict(human_seconds=115200, human_attempts_in_budget=4, label="32h"),
}


def read_figure_data(path):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def per_run_costs(rows):
    """Fit each configuration's cost for one run at its own run limit."""
    acc, out = {}, {}
    for r in rows:
        if r["figure"] != "figure11":
            continue
        key = (r["series"], float(r["cost_usd"]))
        limit, k = F11_K[key]
        acc.setdefault((r["series"], limit), []).append(float(r["cost_usd"]) / k)
    for key, vals in acc.items():
        mean = sum(vals) / len(vals)
        spread = (max(vals) - min(vals)) / mean
        assert spread < 0.05, (key, vals)
        out[key] = dict(cost=mean, samples=vals, spread=spread)
    return out


def score_table(rows):
    out = {}
    for r in rows:
        if r["figure"] in ("figure7", "figure8"):
            out[(r["series"], r["allocation"])] = float(r["score"])
        if r["figure"] == "figure6":
            out[("ci", r["series"], r["allocation"])] = (
                float(r["score"]), float(r["ci_low"]), float(r["ci_high"]))
        if r["figure"] == "figure11" and r["series"] == "human":
            _, k = F11_K[("human", float(r["cost_usd"]))]
            out[("human", k)] = float(r["score"])
    return out


def tokens_from_cost(cost, model, ratio):
    """Pooled-ratio inversion. Retained only for the refuted cross-check."""
    p_in, p_out = PRICES[model]
    return cost * (1.0 + ratio) / (ratio * p_in + p_out)


def figure12_medians(rows):
    out = {}
    for r in rows:
        if r["figure"] == "figure12":
            out[(r["series"], r["allocation"])] = (
                float(r["score"]), float(r["ci_low"]), float(r["ci_high"]))
    return out


def per_run_tokens(series, cost_per_run, f12, output_scale=1.0):
    """Output tokens per run from figure 12; input tokens from what is left of the
    run cost after paying for that output."""
    cfg = CONFIGS[series]
    p_in, p_out = PRICES[cfg["model"]]
    rate = f12[(series, "completion_tokens_per_second")][0]
    share = f12[(series, "api_time_share")][0]
    seconds = 1800 if cfg["limit"] == "30min" else 7200
    out_tokens = rate * share * seconds * output_scale
    in_tokens = (cost_per_run - out_tokens * p_out) / p_in
    assert in_tokens > 0, (series, output_scale)
    return in_tokens, out_tokens


def bands_from_figures(rows):
    out = {}
    for r in rows:
        if r["figure"].endswith("-band"):
            out[(r["series"], r["allocation"])] = (float(r["ci_low"]), float(r["ci_high"]))
    return out


# ------------------------------------------------------------------ row text
COLUMNS = ["point_id", "task", "task_category", "task_description", "model_id",
           "compute_scope", "compute_flops", "human_skill", "human_time_scope",
           "human_time", "performance_vs_human", "comparison_issues",
           "compute_evidence", "human_time_evidence", "performance_evidence",
           "human_time_statistic", "human_time_subset", "human_attempts",
           "human_time_source", "human_time_method", "compute_method",
           "compute_statistic", "compute_subset", "ai_attempts", "compute_source",
           "tokens", "tokens_accounting", "source_dataset", "source_record", "notes",
           "ai_cost_usd", "ai_cost_basis", "ai_cost_date", "human_cost_usd",
           "human_cost_basis"]

CAPS = dict(notes=586, task_description=560, performance_evidence=337,
            source_record=455, compute_source=220, human_time_source=205)

STEM = ("One of RE-Bench's seven open-ended ML research engineering environments, "
        "averaged over the seven, which run from writing a fast Triton kernel to "
        "scaffolding GPT-3.5 for Rust CodeContests. The agent gets a weak starting solution and 0-6 H100s, and "
        "may run the scoring function at will. Score is normalized to 0 at the "
        "starting solution and 1 at a strong reference. ")

SELECTION = (" The submission is the best-scoring run in six environments and a "
             "random one in Scaling Law Experiment, whose score is hidden.")
BUDGET_CLAUSE = {
    (2, "30min"): "Work unit is 2 hours on one environment, as four 30-minute runs." + SELECTION,
    (2, "2h"): "Work unit is 2 hours on one environment, as a single 2-hour run.",
    (8, "30min"): "Work unit is 8 hours on one environment, as sixteen 30-minute runs." + SELECTION,
    (8, "2h"): "Work unit is 8 hours on one environment, as four 2-hour runs." + SELECTION,
    (32, "30min"): "Work unit is 32 hours on one environment, as 64 30-minute runs." + SELECTION,
    (32, "2h"): "Work unit is 32 hours on one environment, as sixteen 2-hour runs." + SELECTION,
}

HUMAN_CLAUSE = {
    2: "against 0.077 for a human expert two hours into an 8-hour attempt",
    8: "against 0.657 for one 8-hour attempt by a human expert",
    32: "against 1.110 for the best of four 8-hour attempts by human experts",
}

HUMAN_TAIL = {
    8: ("The human side is 71 attempts by 61 ML experts under the same 8-hour cap, "
        "published mean 0.64."),
    32: ("The human side is the best-of-four statistic over those 71 recorded 8-hour "
         "attempts by 61 experts."),
}

ALLOC_WORDS = {"30min@4": "four 30-minute runs", "2h@1": "one 2-hour run",
               "30min@16": "sixteen 30-minute runs", "2h@4": "four 2-hour runs",
               "30min@64": "64 30-minute runs", "2h@16": "sixteen 2-hour runs"}

# label, and whether the cell becomes a row in points.csv
DECISIONS = {
    "agen-rebench-2h-sonnet35old-modular": ("above", True),
    "agen-rebench-2h-sonnet35new-modular": ("above", True),
    "agen-rebench-2h-sonnet35new-aide": ("above", True),
    "agen-rebench-2h-o1preview-aide": ("above", True),
    "agen-rebench-8h-sonnet35old-modular": (None, False),
    "agen-rebench-8h-sonnet35new-modular": ("below", True),
    "agen-rebench-8h-sonnet35new-aide": (None, False),
    "agen-rebench-8h-o1preview-aide": ("below", True),
    "agen-rebench-32h-sonnet35old-modular": (None, False),
    "agen-rebench-32h-sonnet35new-modular": ("below", True),
    "agen-rebench-32h-sonnet35new-aide": (None, False),
    "agen-rebench-32h-o1preview-aide": ("below", True),
}

SCAFFOLD_NAME = {"Modular": "METR's Modular scaffold", "AIDE": "the AIDE scaffold"}

DISPOSITION_REASON = {
    "agen-rebench-8h-sonnet35old-modular":
        "Score 0.265 is 40% of the 0.657 human 8-hour score, 2.22 standard errors "
        "below the half-of-human guide, so it is excluded rather than labeled below",
    "agen-rebench-8h-sonnet35new-aide":
        "Score 0.224 is 34% of the 0.657 human 8-hour score, 1.81 standard errors "
        "below the half-of-human guide, so it is excluded rather than labeled below",
    "agen-rebench-32h-sonnet35old-modular":
        "Score 0.341 is 31% of the 1.110 human 32-hour score, 8.17 standard errors "
        "below the half-of-human guide on the Figure 7 band 0.289 to 0.364",
    "agen-rebench-32h-sonnet35new-aide":
        "Score 0.437 is 39% of the 1.110 human 32-hour score, 1.44 standard errors "
        "below the half-of-human guide on the Figure 8 band 0.146 to 0.453, so the "
        "one-standard-error close-call rule does not restore it",
}

GRAIN_DISPOSITIONS = [
    ("environment-level rows, 7 environments x 4 configurations x 3 budgets", "", "",
     "not a row",
     "Rests on compute alone. No per-environment token or cost figure exists "
     "anywhere in the paper, and the suite figures cannot be pushed onto one "
     "environment: tokens per wall-clock-bounded run track the environment's "
     "feedback-loop length (Table 3: 40 seconds to 2.5 hours to score a solution), "
     "and Figure 12's API-time-share violins span almost the whole 0-to-1 range "
     "within a single configuration. Per-environment scores are published, in "
     "Appendices G, H and I, so the performance side would be buildable"),
    ("suite-level row pooling all four agent configurations, 8h@1", "8h@1", "",
     "not a row",
     "The paper's one direct token statement (29M input, 499K output, $123 per 8-hour "
     "run) pools three models with two different FLOPs-per-token coefficients and "
     "undisclosed run weights, so neither a single model_id nor a pooled agent score "
     "can be fixed; the four configurations' 8h@1 scores span 0.096 to 0.368"),
    ("8h@1 rows, one per configuration", "8h@1", "",
     "not a row",
     "Matches the human work unit exactly but has no per-configuration input-token "
     "route. Figure 12 gives output tokens for an 8-hour run, but Figure 11 plots "
     "cost only at each configuration's best allocation, so input cannot be backed "
     "out; the pooled 29M/499K would have to be transferred across scaffolds whose "
     "measured input-to-output ratios run from 3.8 to 134. Scores are 0.096, 0.139, "
     "0.167 and 0.368"),
    ("16-hour and 64-hour budget rows", "", "",
     "not a row",
     "Figure 11 also plots human budgets of 16 and 64 hours and the matching agent "
     "score@k, so these are buildable; only the 2, 8 and 32-hour budgets the abstract "
     "names are built, to avoid multiplying rows off one resampled run pool"),
]


def check_caps(row):
    for k, cap in CAPS.items():
        assert len(row[k]) <= cap, (row["point_id"], k, len(row[k]))


def band_text(cell):
    lo = min(cell["flops_band"].values()) / cell["flops"]
    hi = max(cell["flops_band"].values()) / cell["flops"]
    return "to %.2fx and %.2fx" % (hi, lo)


def row_fields(cell):
    hours = cell["hours"]
    limit = cell["allocation"].split("@")[0]
    cfg = CONFIGS[cell["series"]]
    label = DECISIONS[cell["point_id"]][0]
    budget = BUDGETS[hours]
    issues = ["different_inputs_or_tools"]
    if hours == 2:
        issues.append("different_assessment")
    if cell["k"] > 1:
        issues.append("different_attempt_selection")
    human_cost = {2: "", 8: "1855", 32: "7420"}[hours]
    if hours == 2:
        perf = ("Mean normalized score over the seven environments, %s: %.3f, %s. The "
                "AI is %.1f times the human score on a metric whose floor is the "
                "starting solution. The human side is 71 attempts by 61 ML experts, "
                "read off their score logs at the 2-hour mark." % (
                    ("best of " if cell["k"] > 1 else "") + ALLOC_WORDS[cell["allocation"]],
                    cell["score"], HUMAN_CLAUSE[hours], cell["ratio_ai_over_human"]))
    else:
        perf = ("Mean normalized score over the seven environments, %s: %.3f, %s. That "
                "is %d%% of the human score on a metric whose floor is the starting "
                "solution. %s" % (
                    ("best of " if cell["k"] > 1 else "") + ALLOC_WORDS[cell["allocation"]],
                    cell["score"], HUMAN_CLAUSE[hours],
                    round(100 * cell["ratio_ai_over_human"]), HUMAN_TAIL[hours]))
    notes = ("Output tokens per run are Figure 12's medians for this configuration, "
             "completion tokens per second during API time times the API-time share "
             "times the run limit; input is what the run cost buys at Oct 2024 "
             "list prices, an input-to-output ratio of %.3g against "
             "the paper's pooled 58. Scaling the measured output rate by 0.5 and 1.5 "
             "moves the FLOP total %s. No prompt caching was used, so input is gross "
             "re-processing. The k runs are resampled with replacement from METR's pool. "
             "The environment's GPU work, a mean 2.3 H100s, is "
             "excluded and was identical on the human side."
             % (cell["input_output_ratio"], band_text(cell)))
    src = ("METR RE-Bench, arXiv 2411.15114v2: %s in %s, %s run limit, score@%d; agent "
           "score %s, cost budget Figure 11, allocation rule Section 4.2 and the "
           "Figure 2 caption; environments github.com/METR/RE-Bench; performance: "
           "human score Figure 11 and Table 5; "
           "agent-work/sources/rebench/rebench-2411.15114v2.pdf" % (
               cfg["model"], SCAFFOLD_NAME[cfg["scaffold"]],
               "30-minute" if limit == "30min" else "2-hour", cell["k"],
               "Figure 7" if limit == "30min" else "Figure 8"))
    row = {
        "point_id": cell["point_id"],
        "task": "RE-Bench ML research engineering environment, %d-hour budget" % hours,
        "task_category": "coding",
        "task_description": STEM + BUDGET_CLAUSE[(hours, limit)],
        "model_id": cfg["model"],
        "compute_scope": "inference",
        "compute_flops": repr(cell["flops"]),
        "human_skill": "expert",
        "human_time_scope": "task_performance",
        "human_time": str(budget["human_seconds"]),
        "performance_vs_human": label or "",
        "comparison_issues": "; ".join(issues),
        "compute_evidence": "derived_assumed_inputs",
        "human_time_evidence": "defined_duration",
        "performance_evidence": perf,
        "human_time_statistic": "point_estimate",
        "human_time_subset": "not_applicable",
        "human_attempts": "not_applicable",
        "human_time_source": ("arXiv 2411.15114v2 Section 3.4 and Appendix A.1: all 71 "
                              "expert attempts capped at 8 hours, breaks excluded; "
                              "research/rebench.md#human-time"),
        "human_time_method": "work_rate",
        "compute_method": "params_tokens",
        "compute_statistic": "total",
        "compute_subset": "all",
        "ai_attempts": str(cell["k"]),
        "compute_source": ("research/rebench.md#%s; research/rebench/figure-data.csv; "
                           "research/rebench/make_rows.py" % cell["point_id"]),
        "tokens": repr(cell["tokens"]),
        "tokens_accounting": "input_output",
        "source_dataset": "METR RE-Bench (arXiv 2411.15114v2)",
        "source_record": src,
        "notes": notes,
        "ai_cost_usd": "%.2f" % cell["cost_usd"],
        "ai_cost_basis": "reported",
        "ai_cost_date": "2024-11-22",
        "human_cost_usd": human_cost,
        "human_cost_basis": "reported_payment" if human_cost else "not_available",
    }
    check_caps(row)
    return row


def write_points(cells, path):
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, COLUMNS, lineterminator="\r\n")
        w.writeheader()
        for cell in cells:
            if DECISIONS[cell["point_id"]][1]:
                w.writerow(row_fields(cell))


def write_dispositions(cells, path):
    head = ["cell_id", "budget_hours", "configuration", "allocation", "ai_score",
            "human_score", "ratio_to_human", "agent_se", "standard_errors_below_guide",
            "outcome", "reason"]
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\r\n")
        w.writerow(head)
        for cell in cells:
            label, is_row = DECISIONS[cell["point_id"]]
            if is_row:
                continue
            w.writerow([cell["point_id"], cell["hours"], cell["series"],
                        cell["allocation"], cell["score"], cell["human_score"],
                        cell["ratio_ai_over_human"],
                        "" if cell["agent_se"] is None else round(cell["agent_se"], 4),
                        "" if cell["se_below_guide"] is None
                        else round(cell["se_below_guide"], 2),
                        "excluded", DISPOSITION_REASON[cell["point_id"]]])
        for cell_id, alloc, _score, outcome, reason in GRAIN_DISPOSITIONS:
            w.writerow([cell_id, "", "", alloc, "", "", "", "", "", outcome, reason])


def main(fig_csv, points_csv, calc_json, disp_csv):

    rows = read_figure_data(fig_csv)
    runs = per_run_costs(rows)
    scores = score_table(rows)
    f12 = figure12_medians(rows)
    f78 = bands_from_figures(rows)
    ratio = POOLED_INPUT / POOLED_OUTPUT

    human = {2: scores[("human", 0.25)], 8: scores[("human", 1)], 32: scores[("human", 4)]}
    # bootstrap standard error of the human mean at 8 and 32 hours, from the
    # Figure 11 confidence band (half-width / 1.96); see research/rebench.md
    human_se = {8: 0.063, 32: 0.058, 2: 0.015}

    cells, calcs = [], dict(
        pooled=dict(input_tokens=POOLED_INPUT, output_tokens=POOLED_OUTPUT,
                    cost_usd=POOLED_COST, input_output_ratio=ratio,
                    implied_all_sonnet_cost=round(
                        POOLED_INPUT * 3e-6 + POOLED_OUTPUT * 15e-6, 2)),
        per_run_cost_usd={f"{k[0]} @ {k[1]}": round(v["cost"], 4)
                          for k, v in runs.items()},
        per_run_cost_spread={f"{k[0]} @ {k[1]}": round(v["spread"], 4)
                             for k, v in runs.items()},
        figure12_medians={f"{k[0]} | {k[1]}": v[0] for k, v in f12.items()},
        figure12_whiskers={f"{k[0]} | {k[1]}": (v[1], v[2]) for k, v in f12.items()},
        figure78_bands={f"{k[0]} | {k[1]}": v for k, v in f78.items()},
        human_score=human, human_se=human_se,
        human_mean_8h_paper_table5=HUMAN_MEAN_8H_TABLE5,
        human_pay_per_attempt_usd=HUMAN_PAY_PER_ATTEMPT,
        cells={})

    for hours, budget in BUDGETS.items():
        for series, cfg in CONFIGS.items():
            limit = "30min" if cfg["scaffold"] == "Modular" else "2h"
            k = int(hours * (2 if limit == "30min" else 0.5))
            alloc = f"{limit}@{k}"
            score = scores[(series, alloc)]
            cost_per_run = runs[(series, limit)]["cost"]
            cost = cost_per_run * k
            model = cfg["model"]
            f_in, f_out = per_run_tokens(series, cost_per_run, f12)
            toks = k * (f_in + f_out)
            flops = toks * FLOPS_PER_TOKEN[model]
            band = {}
            for sc in (0.5, 1.5):
                b_in, b_out = per_run_tokens(series, cost_per_run, f12, sc)
                band[f"output_rate_x{sc}"] = round(
                    k * (b_in + b_out) * FLOPS_PER_TOKEN[model], 6)
            pooled = tokens_from_cost(cost, model, ratio) * FLOPS_PER_TOKEN[model]
            h = human[hours]
            rel = score / h
            se_a, se_source = None, ""
            ci = scores.get(("ci", series, alloc))
            if ci:
                se_a, se_source = (ci[2] - ci[1]) / 2 / 1.96, "figure6 whiskers"
            elif (series, alloc) in f78:
                lo, hi = f78[(series, alloc)]
                se_a, se_source = (hi - lo) / 2 / 1.96, "figure7/8 band"
            se_rel = (rel * math.sqrt((se_a / score) ** 2 + (human_se[hours] / h) ** 2)
                      if se_a else None)
            cell = dict(point_id=f"agen-rebench-{budget['label']}-{cfg['slug']}",
                        series=series, hours=hours, allocation=alloc, k=k,
                        model=model, score=round(score, 4), human_score=round(h, 4),
                        ratio_ai_over_human=round(rel, 4),
                        ratio_human_over_ai=round(h / score, 4),
                        cost_usd=round(cost, 2), tokens=toks, flops=flops,
                        input_tokens_per_run=round(f_in, 1),
                        output_tokens_per_run=round(f_out, 1),
                        input_output_ratio=round(f_in / f_out, 3),
                        flops_band=band,
                        flops_under_pooled_ratio=pooled,
                        flops_vs_pooled_ratio=round(flops / pooled, 4),
                        agent_se=se_a, agent_se_source=se_source,
                        ratio_se=se_rel,
                        se_below_guide=((0.5 - rel) / se_rel) if se_rel else None)
            cells.append(cell)
            calcs["cells"][cell["point_id"]] = cell

    write_points(cells, points_csv)
    write_dispositions(cells, disp_csv)
    with open(calc_json, "w") as fh:
        json.dump(calcs, fh, indent=1, sort_keys=True)
    print(json.dumps({c["point_id"]: dict(score=c["score"], human=c["human_score"],
                                          ratio=c["ratio_ai_over_human"],
                                          cost=c["cost_usd"],
                                          flops="%.3e" % c["flops"],
                                          se_below=c["se_below_guide"])
                      for c in cells}, indent=1))
    return cells


if __name__ == "__main__":
    if len(sys.argv) != 5:
        raise SystemExit(__doc__)
    main(*sys.argv[1:])
