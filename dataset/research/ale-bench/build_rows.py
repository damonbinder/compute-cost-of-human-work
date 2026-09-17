#!/usr/bin/env python3
"""Build the ALE-Bench and AHC058 candidate rows from the retained extracts.

Reads only files under a sources directory and the two model registries, and
writes points.csv, models.csv, dispositions.csv and calculations.json into the
output directory named on the command line. It never modifies its inputs.

Usage:
    python3 build_rows.py \
        --sources agent-work/sources/ale-bench \
        --map research/ale-bench/model-map.csv \
        --codex-models "../AI Compute vs Human Time/dataset/models.csv" \
        --local-models models.csv \
        --out candidates/ale-bench

Dependencies: Python 3.10+ standard library only.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from pathlib import Path

# --- fixed judgments, documented in research/ale-bench.md --------------------
N_SAMPLES = 15          # repeated-sampling fan-out per problem, leaderboard protocol
LEADERBOARD_VERSION = "2026-09-08"
# performance_vs_human thresholds on the floor-adjusted ratio to the human mean
T_EXCLUDE, T_MATCH_LO, T_MATCH_HI, T_FAR_ABOVE = 0.50, 0.85, 1.15, 2.00
# Revision 1: where the billed cost shows a prompt-cache discount was taken, the cache reads it
# implies are removed from the parameter-multiplication term and the gross count becomes the
# scenario. This is the default-on caching ruling in DECISIONS.md, applied on the coordinator's
# 2026-09-13 instruction after the independent review.
CACHE_DEDUCTED_BASIS = "inverted_from_billed_cost"
# research/cost/list-prices.csv carries no row for the preview endpoint. Both the AHC058
# calculation and these two rows price it at the gemini-3-pro window, the same family, tier and
# dates; without it the two rows fall through to no_retained_price and take no deduction.
PRICE_OVERRIDES = {
    "gemini-3-pro-preview": [
        {
            "price_sheet_start": "2025-11-18", "price_sheet_end": "",
            "input_usd_per_m": "2.00", "cached_input_usd_per_m": "0.20", "output_usd_per_m": "12.00",
        }
    ]
}
# Revision 1, second pass. The GPT-5.6 family repriced twice in its first six weeks and the
# ALE-Bench harness's fallback table carries the launch rates, so the cost the leaderboard publishes
# for these three was computed at rates the rows' 2026-09-08 date no longer selects. The cache
# inversion therefore has to run at the rates the harness actually billed, while ai_cost_usd is
# repriced at the window the date does select. Windows and captures are in
# research/cost/gpt56-repricing.md; the same inversion is negative, and so uninvertible, at the
# later rates, which is what put the billed_above_sheet_rate flag on these rows in the first
# submission.
HARNESS_BILLING_DATE = {
    "gpt-5-6-sol": "2026-07-09",
    "gpt-5-6-terra": "2026-07-09",
    "gpt-5-6-luna": "2026-07-09",
}
# Blocked-configuration triage, Revision 1. Model strings come from the retained
# alebench-llm-configs.csv. ACTIVE_COUNT_IN_NAME lists the ones whose parameter count is in the
# name itself, so they want a reported count rather than a prior; OPEN_WEIGHT_VENDORS lists the
# vendors that publish weights for at least some models in the family, which says where to look
# first, not that this particular endpoint's weights are public.
ACTIVE_COUNT_IN_NAME = {
    "gemma-4-26b-a4b-it": "26B total, 4B active",
    "gemma-4-31B-it": "31B dense",
    "qwen3.5-35b-a3b": "35B total, 3B active",
    "qwen3.5-397b-a17b": "397B total, 17B active",
    "qwen3.5-27b": "27B dense",
    "nemotron-3-super-120b-a12b": "120B total, 12B active",
}
OPEN_WEIGHT_VENDORS = (
    "qwen/", "z-ai/", "deepseek/", "moonshotai/", "minimax/", "mistralai/", "xiaomi/",
    "google/gemma", "nvidia/", "stepfun/", "inclusionai/", "tencent/", "meta/",
)
# Why a model's billed cost sits above the dataset's gross list price, where it does.
CACHE_BASIS_CAUSE = {
    "grok-4.20-beta-0309b-reasoning": "billed at an OpenRouter reseller rate the sheet does not carry",
    "deepseek-r1-0528": "billed at the OpenRouter parasail/fp8 rate, which the sheet does not carry",
}

POINTS_FIELDS = [
    "point_id", "task", "task_category", "task_description", "model_id", "compute_scope",
    "compute_flops", "human_skill", "human_time_scope", "human_time", "performance_vs_human",
    "comparison_issues", "compute_evidence", "human_time_evidence", "performance_evidence",
    "human_time_statistic", "human_time_subset", "human_attempts", "human_time_source",
    "human_time_method", "compute_method", "compute_statistic", "compute_subset", "ai_attempts",
    "compute_source", "tokens", "tokens_accounting", "source_dataset", "source_record", "notes",
    "ai_cost_usd", "ai_cost_basis", "ai_cost_date", "human_cost_usd", "human_cost_basis",
]
MODELS_FIELDS = [
    "model_id", "model", "company", "model_release_date", "model_release_source",
    "flops_per_token", "flops_per_token_method", "active_parameters", "active_parameters_basis",
    "encoder_parameters", "encoder_parameters_basis", "decoder_parameters",
    "decoder_parameters_basis", "parameter_source", "notes",
]

NEW_MODELS = [
    {
        "model_id": "gemini-3-pro-preview",
        "model": "Gemini 3 Pro preview (gemini-3-pro-preview endpoint, November 2025 weights)",
        "company": "Google DeepMind",
        "model_release_date": "2025-11-18",
        "model_release_source": "https://ai.google.dev/gemini-api/docs/changelog 2025-11-18 entry launching gemini-3-pro-preview",
        "flops_per_token": "200000000000",
        "flops_per_token_method": "two_active_parameters",
        "active_parameters": "100000000000",
        "active_parameters_basis": "estimated",
        "encoder_parameters": "not_applicable",
        "encoder_parameters_basis": "not_applicable",
        "decoder_parameters": "not_applicable",
        "decoder_parameters_basis": "not_applicable",
        "parameter_source": "research/ale-bench.md#gemini-3-pro-preview",
        "notes": "100B active is the Gemini 3 family prior held for the whole family by the 2026-09-13 coordinator ruling, not a Google disclosure; grade C, 30-300B, moving dependent FLOPs 0.3x to 3x. Separate from gemini-3-pro because the preview endpoint is the revision these runs called; Google redirected it to gemini-3.1-pro-preview on 2026-03-09, after both runs.",
    }
]


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="") as fh:
        return list(csv.DictReader(fh))


def fmt(x: float, digits: int = 4) -> str:
    return f"{round(x, digits):g}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", required=True, type=Path)
    ap.add_argument("--map", required=True, type=Path)
    ap.add_argument("--codex-models", required=True, type=Path)
    ap.add_argument("--local-models", required=True, type=Path)
    ap.add_argument("--prices", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--note-head", type=Path, help="markdown prose prepended to the generated note")
    ap.add_argument("--note-out", type=Path, help="where to write the assembled research note")
    args = ap.parse_args()
    src, out = args.sources, args.out
    out.mkdir(parents=True, exist_ok=True)

    prices: dict[str, list[dict]] = {}
    for row in read_csv(args.prices):
        if row["input_usd_per_m"]:
            prices.setdefault(row["model_id"], []).append(row)
    prices.update(PRICE_OVERRIDES)

    coefficients: dict[str, float] = {}
    for path in (args.codex_models, args.local_models):
        for row in read_csv(path):
            if row["flops_per_token"] not in ("", "not_applicable"):
                coefficients[row["model_id"]] = float(row["flops_per_token"])
    for row in NEW_MODELS:
        coefficients[row["model_id"]] = float(row["flops_per_token"])

    # --- human side ----------------------------------------------------------
    human = [r for r in read_csv(src / "alebench-human-performance-per-problem.csv") if r["format"] == "short"]
    human_mean = statistics.mean(float(r["mean_performance"]) for r in human)
    human_floor = statistics.mean(float(r["min_performance"]) for r in human)
    window_s = statistics.mean(float(r["window_hours"]) for r in human) * 3600.0
    n_entries = sum(int(r["n_participants"]) for r in human)
    span = human_mean - human_floor

    # --- AI side -------------------------------------------------------------
    agg = {
        (r["model_name"], int(r["num_self_refine"])): r
        for r in read_csv(src / "alebench-leaderboard-aggregates.csv")
    }
    entrants = {r["problem_id"]: int(r["n_participants"]) for r in human}
    ranks: dict[str, list[tuple[int, int]]] = {}
    for r in read_csv(src / "alebench-leaderboard-selfrefine1-short.csv"):
        ranks.setdefault(r["model_name"], []).append((int(r["rank"]), entrants[r["problem_id"]]))

    mapping = read_csv(args.map)
    mapped_configs = {r["leaderboard_config"] for r in mapping}

    points, calcs, dispositions = [], [], []
    for m in mapping:
        cfg, model_id = m["leaderboard_config"], m["model_id"]
        a = agg[(cfg, 1)]
        inp, outp = float(a["input_tokens_short"]), float(a["output_tokens_short"])
        perf, sd = float(a["performance_short"]), float(a["performance_short_stdev"])
        cost = float(a["cost_short"])
        coeff = coefficients[model_id]
        billing_date = HARNESS_BILLING_DATE.get(model_id, LEADERBOARD_VERSION)
        billed_at, window_covers = price_at(prices.get(model_id), billing_date)
        charged_at, _ = price_at(prices.get(model_id), LEADERBOARD_VERSION)
        if model_id in CACHE_BASIS_CAUSE:
            # The rate the harness billed at is not in the sheet, so nothing can be inverted.
            cache_reads, cache_basis = 0.0, "billed_at_rate_not_in_sheet"
        else:
            cache_reads, cache_basis = implied_cache_reads(billed_at, inp, outp, cost)
        if model_id in HARNESS_BILLING_DATE and charged_at is not None:
            ai_cost = N_SAMPLES * priced(charged_at, inp - cache_reads, cache_reads, outp)
            repriced = True
        else:
            ai_cost = N_SAMPLES * cost
            repriced = False
        gross_tokens = N_SAMPLES * (inp + outp)
        net_tokens = N_SAMPLES * (inp - cache_reads + outp)
        deducted = cache_basis == CACHE_DEDUCTED_BASIS
        tokens = net_tokens if deducted else gross_tokens
        flops = tokens * coeff
        mean_rank = statistics.mean(rk for rk, _ in ranks[cfg])
        share_above = 100 * statistics.mean((rk - 1) / n for rk, n in ranks[cfg])
        firsts = sum(1 for rk, _ in ranks[cfg] if rk == 1)
        ratio = (perf - human_floor) / span
        se_ratio = (sd / math.sqrt(len(human))) / span
        if ratio >= T_FAR_ABOVE:
            label = "far_above"
        elif ratio >= T_MATCH_HI:
            label = "above"
        elif ratio >= T_MATCH_LO:
            label = "match"
        elif ratio >= T_EXCLUDE:
            label = "below"
        elif ratio + se_ratio >= T_EXCLUDE:
            label = "below"          # close call, kept under the one-standard-error rule
        else:
            label = None             # excluded: recorded in dispositions, not built
        close_call = label == "below" and ratio < T_EXCLUDE
        record = {
            "point_id": f"agen-alebench-short-{m['slug']}",
            "leaderboard_config": cfg,
            "model_id": model_id,
            "input_tokens_short_mean": inp,
            "output_tokens_short_mean": outp,
            "n_samples": N_SAMPLES,
            "tokens": tokens,
            "flops_per_token": coeff,
            "compute_flops": flops,
            "cost_short_mean_selected_sample": cost,
            "ai_cost_usd": ai_cost,
            "ai_cost_repriced_from_harness_window": repriced,
            "harness_billing_window_start": billing_date if repriced else "",
            "performance_short_mean": perf,
            "performance_short_stdev": sd,
            "human_mean_performance": human_mean,
            "human_floor_performance": human_floor,
            "ratio_to_human": ratio,
            "se_of_ratio": se_ratio,
            "label": label or "excluded",
            "close_call": close_call,
            "input_share_of_tokens": (inp - cache_reads) / (inp - cache_reads + outp),
            "gross_input_share_of_tokens": inp / (inp + outp),
            "implied_cache_reads_per_call": cache_reads,
            "cache_inference_basis": cache_basis,
            "cache_basis_cause": CACHE_BASIS_CAUSE.get(model_id, ""),
            # Two different windows, deliberately: the cache inversion has to run at the rates the
            # harness actually billed, while the dollars are priced at the rates in force on the
            # row's cost date. They coincide everywhere except the three GPT-5.6 rows.
            "billing_window": (
                f"{billed_at['price_sheet_start']} to {billed_at['price_sheet_end'] or 'open'}"
                if billed_at else "none in sheet"
            ),
            "billing_window_date": billing_date,
            "billing_window_covers_its_date": window_covers,
            "pricing_window": (
                f"{charged_at['price_sheet_start']} to {charged_at['price_sheet_end'] or 'open'}"
                if repriced and charged_at
                else "not repriced: ai_cost_usd is 15x the leaderboard's own billed cost"
            ),
            "pricing_window_date": LEADERBOARD_VERSION if repriced else "",
            "cache_reads_deducted": deducted,
            "gross_tokens": gross_tokens,
            "gross_compute_flops": gross_tokens * coeff,
            "scenario_multiplier_gross_over_central": gross_tokens / tokens,
            "mean_rank_over_23_contests": mean_rank,
            "mean_share_of_field_above_pct": share_above,
            "contests_ranked_first": firsts,
            "mean_entrants_per_contest": statistics.mean(n for _, n in ranks[cfg]),
        }
        calcs.append(record)
        if label is None:
            dispositions.append(
                {
                    "cell": f"{cfg} / self-refine x1 / short",
                    "kind": "excluded cell",
                    "n": len(human),
                    "ai_performance": fmt(perf, 1),
                    "human_performance": fmt(human_mean, 1),
                    "ratio_to_human": fmt(ratio, 3),
                    "se_of_ratio": fmt(se_ratio, 3),
                    "reason": (
                        f"Mean AtCoder performance {perf:.0f} over the 23 short-format problems is "
                        f"{ratio:.2f} of the {human_mean:.0f} mean entrant after subtracting the "
                        f"{human_floor:.0f} last-place floor, "
                        f"{(T_EXCLUDE - ratio) / se_ratio:.2f} standard errors below the "
                        "half-of-human guide, so it is not comparable to the human baseline and is "
                        "recorded here rather than built"
                        + (
                            "; this is the closest call in the set and the first cell that would "
                            "move under any loosening of the close-call rule"
                            if (T_EXCLUDE - ratio) / se_ratio < 1.2
                            else ""
                        )
                    ),
                }
            )
            continue
        points.append(build_point(m, record, window_s, human_mean, human_floor, n_entries, len(human)))

    # every leaderboard configuration that is not a row gets a disposition line, split by what
    # unblocks it: a transcribed architecture for models whose weights are published, or a new
    # grade-C prior for models whose lab publishes nothing. Revision 1, on the review's finding.
    api_model = {r["config"]: r["model_name"] for r in read_csv(src / "alebench-llm-configs.csv")}
    for row in read_csv(src / "alebench-leaderboard-aggregates.csv"):
        if int(row["num_self_refine"]) != 1 or row["model_name"] in mapped_configs:
            continue
        cfg = row["model_name"]
        api = api_model[cfg]
        perf = float(row["performance_short"])
        sd = float(row["performance_short_stdev"])
        ratio = (perf - human_floor) / span
        se = (sd / math.sqrt(len(human))) / span
        clears = ratio >= T_EXCLUDE or ratio + se >= T_EXCLUDE
        named = next((c for c in ACTIVE_COUNT_IN_NAME if c in api), None)
        vendor = next((v for v in OPEN_WEIGHT_VENDORS if api.startswith(v)), None)
        if named:
            reason = (
                f"The model name carries its own parameter count ({ACTIVE_COUNT_IN_NAME[named]}), so "
                "this wants a reported count transcribed from the released model card rather than a "
                "prior; the cheapest of the 74 to unblock"
            )
        elif vendor:
            reason = (
                f"{vendor.rstrip('/')} publishes weights for at least some models in this family, so "
                "the released configuration is worth checking for a reported active count before "
                "anything is assumed; the endpoint's own weights are not verified here"
            )
        else:
            reason = (
                "No published architecture and no active-parameter prior in either registry, so a "
                "new grade-C closed-model prior of the kind research/model-priors/ produces is "
                "needed before FLOPs can be estimated"
            )
        dispositions.append(
            {
                "cell": f"{cfg} / self-refine x1 / short",
                "kind": "not a row",
                "n": len(human),
                "ai_performance": fmt(perf, 1),
                "human_performance": fmt(human_mean, 1),
                "ratio_to_human": fmt(ratio, 3),
                "se_of_ratio": "",
                "reason": reason + ("; would clear the exclusion cut" if clears else "; would be excluded on its score"),
                "would_be_a_row": int(clears),
            }
        )
    share = {2: "27", 4: "44", 8: "67", 16: "84"}
    for sr in (2, 4, 8, 16):
        dispositions.append(
            {
                "cell": f"all 128 configurations / self-refine x{sr} / short",
                "kind": "not a row",
                "n": len(human),
                "ai_performance": "",
                "human_performance": fmt(human_mean, 1),
                "ratio_to_human": "",
                "se_of_ratio": "",
                "reason": (
                    "Self-refine resends the whole conversation each turn, so published input "
                    f"tokens are a median {share[sr]}% of the total at x{sr} and are gross of prompt-cache "
                    "reads that the published cost shows are being taken; the full-prefix "
                    "assumption would overstate the parameter term, and no cache split is published"
                ),
            }
        )
    dispositions.extend(PAPER_DISPOSITIONS)

    # --- AHC058 --------------------------------------------------------------
    ahc, ahc_calc = build_ahc058(src, agg, coefficients)
    points.append(ahc)
    calcs.append(ahc_calc)

    write_csv(out / "points.csv", POINTS_FIELDS, points)
    write_csv(out / "models.csv", MODELS_FIELDS, NEW_MODELS)
    write_csv(
        out / "dispositions.csv",
        [
            "cell", "kind", "n", "ai_performance", "human_performance", "ratio_to_human",
            "se_of_ratio", "would_be_a_row", "reason",
        ],
        dispositions,
    )
    (out / "calculations.json").write_text(
        json.dumps(
            {
                "human_mean_performance_short": human_mean,
                "human_floor_performance_short": human_floor,
                "human_window_seconds_short": window_s,
                "human_participant_entries_short": n_entries,
                "n_short_problems": len(human),
                "n_samples_per_problem": N_SAMPLES,
                "thresholds": {
                    "exclude": T_EXCLUDE, "match_low": T_MATCH_LO,
                    "match_high": T_MATCH_HI, "far_above": T_FAR_ABOVE,
                },
                "rows": calcs,
            },
            indent=1,
        )
        + "\n"
    )
    if args.note_head and args.note_out:
        args.note_out.write_text(args.note_head.read_text() + rows_section(calcs, mapping))
    print(json.dumps({"points": len(points), "models": len(NEW_MODELS), "dispositions": len(dispositions)}))


def rows_section(calcs: list[dict], mapping: list[dict]) -> str:
    effort = {m["leaderboard_config"]: m for m in mapping}
    out = ["\n## Rows\n"]
    out.append(
        "One heading per `point_id`. Every leaderboard row reads the same way: the short-subset means "
        "are the arithmetic means over the 23 short-format problems, `tokens` is 15 x (input - cache "
        "reads + output) where the billed cost shows a cache discount was taken and 15 x (input + "
        "output) otherwise, `compute_flops` is `tokens` x the model's `flops_per_token`, `ai_cost_usd` "
        "is 15 x the leaderboard's cost for the submitted sample, and the ratio is "
        "(AI performance - 55.3) / (1414.5 - 55.3). The gross scenario is the upward alternative on "
        "the cache-deducted rows. Six sections describe cells that are dispositions rather than rows; "
        "their label reads excluded and they are not in points.csv.\n"
    )
    for r in calcs:
        if r["point_id"] == "agen-ahc058-ale-agent":
            continue
        m = effort[r["leaderboard_config"]]
        out.append(f"### {r['point_id']}\n")
        out.append(
            f"`{r['model_id']}` as leaderboard configuration `{r['leaderboard_config']}` "
            f"({m['effort_note']}), self-refine x1.\n\n"
            f"- Short-subset means: input {r['input_tokens_short_mean']:,.0f} tokens, output "
            f"{r['output_tokens_short_mean']:,.0f}, cost ${r['cost_short_mean_selected_sample']:.4f}, "
            f"AtCoder performance {r['performance_short_mean']:.1f} (standard deviation across problems "
            f"{r['performance_short_stdev']:.0f}).\n"
            + (
                f"- Cache reads per call implied by the billed cost: "
                f"{r['implied_cache_reads_per_call']:,.0f} of {r['input_tokens_short_mean']:,.0f} input "
                f"tokens, removed from the parameter term.\n"
                f"- tokens = 15 x ({r['input_tokens_short_mean']:,.0f} - "
                f"{r['implied_cache_reads_per_call']:,.0f} + {r['output_tokens_short_mean']:,.0f}) "
                if r["cache_reads_deducted"]
                else f"- Cache basis: {r['cache_inference_basis']}"
                + (f" ({r['cache_basis_cause']})" if r["cache_basis_cause"] else "")
                + ", so input is counted gross.\n"
                f"- tokens = 15 x ({r['input_tokens_short_mean']:,.0f} + "
                f"{r['output_tokens_short_mean']:,.0f}) "
            )
            + f"= {r['tokens']:,.0f}; compute = {r['tokens']:,.0f} x {r['flops_per_token']:.3g} = "
            f"{r['compute_flops']:.3g} FLOPs; cost = 15 x ${r['cost_short_mean_selected_sample']:.4f} = "
            f"${r['ai_cost_usd']:.2f}.\n"
            f"- Mean rank {r['mean_rank_over_23_contests']:.1f} of a mean "
            f"{r['mean_entrants_per_contest']:.0f} entrants; {r['mean_share_of_field_above_pct']:.2f}% "
            "of the field finished above it"
            + (
                f", and it took 1st place outright on {r['contests_ranked_first']} of 23 contests.\n"
                if r["contests_ranked_first"]
                else ", and it never took 1st place.\n"
            )
            + f"- Ratio to the mean entrant: ({r['performance_short_mean']:.1f} - 55.3) / (1414.5 - 55.3) = "
            f"{r['ratio_to_human']:.3f}, standard error {r['se_of_ratio']:.3f}. Label **{r['label']}**"
            + (" (close call, kept under the one-standard-error rule)." if r["close_call"] else ".")
            + "\n"
            + (
                f"- Gross scenario, counting the cached prefix at full prefill: "
                f"{r['gross_tokens']:,.0f} tokens and {r['gross_compute_flops']:.3g} FLOPs, "
                f"{r['scenario_multiplier_gross_over_central']:.3f}x the central.\n"
                if r["cache_reads_deducted"]
                else ""
            )
        )
    a = next(r for r in calcs if r["point_id"] == "agen-ahc058-ale-agent")
    out.append("### agen-ahc058-ale-agent\n")
    lines = []
    for mid, v in a["per_model"].items():
        lines.append(
            f"- `{mid}`: {v['calls']:,} calls x ({v['input_per_call']:,.0f} input + "
            f"{v['output_per_call']:,.0f} output) per call, transferred from the leaderboard's "
            f"`{AHC058_DONOR[mid]}` short-subset means, priced at "
            f"${AHC058_PRICES[mid][0]:.2f}/M input and ${AHC058_PRICES[mid][1]:.2f}/M output "
            f"= ${v['cadence_cost']:.0f} unscaled.\n"
        )
    out.append("".join(lines))
    out.append(
        f"\nUnscaled the two models price to ${a['cadence_matched_cost_usd']:.0f}. Sakana reports about "
        f"${a['reported_api_cost_usd']:.0f} in API fees, so the transferred cadence is scaled by "
        f"k = {a['scale_factor_k']:.3f}, giving {a['tokens']:,.0f} counted tokens and "
        f"{a['compute_flops']:.3g} FLOPs at the two models' 100B-active priors. Taking k = 1 instead "
        f"(the unscaled cadence, which prices to the $1,300 all-in figure) gives "
        f"{a['compute_flops'] / a['scale_factor_k']:.3g} FLOPs, 1.30x the central.\n"
    )
    return "\n".join(out)


def price_at(windows: list[dict] | None, date: str) -> tuple[dict | None, bool]:
    """The price window covering `date`, and whether it covers it.

    Windows are [start, end] inclusive with an optional open end. Where none covers the date the
    latest window starting before it is returned with False: kimi-k2.5 is the case here, retired
    from the Moonshot API on 2026-08-31 and so unpriced on the leaderboard's own version date, which
    is itself evidence that the run predates the retirement. Nothing is returned for a model the
    sheet does not carry at all.
    """
    if not windows:
        return None, False
    for w in windows:
        start, end = w.get("price_sheet_start", ""), w.get("price_sheet_end", "")
        if start and date < start:
            continue
        if end and date > end:
            continue
        return w, True
    earlier = [w for w in windows if not w.get("price_sheet_start") or w["price_sheet_start"] <= date]
    if not earlier:
        return None, False
    return max(earlier, key=lambda w: w.get("price_sheet_start", "")), False


def priced(window: dict, fresh_input: float, cache_reads: float, output: float) -> float:
    """Cost of one call at a price window, in USD, with cache reads at the cached-input rate."""
    p_in, p_out = float(window["input_usd_per_m"]), float(window["output_usd_per_m"])
    p_cache = float(window["cached_input_usd_per_m"]) if window["cached_input_usd_per_m"] else 0.0
    return (p_in * fresh_input + p_cache * cache_reads + p_out * output) / 1e6


def implied_cache_reads(price: dict | None, inp: float, outp: float, cost: float) -> tuple[float, str]:
    """Cache reads per call implied by the gap between the gross list price and the billed cost.

    Returns (tokens, basis). Revision 1 separates the two readings the first submission collapsed:
    a gap of less than half a token is the billed cost landing on the gross list price, which says
    no cache discount was taken, while a gap more than half a token negative is the billed rate
    sitting above the sheet, which says nothing about caching either way. The first submission
    reported the former as the latter on four rows, which read as a claim that the price sheet was
    wrong for Claude Sonnet 4 and three others when it is exact for them.
    """
    if price is None:
        return 0.0, "no_retained_price"
    p_in, p_out = float(price["input_usd_per_m"]), float(price["output_usd_per_m"])
    p_cache = float(price["cached_input_usd_per_m"]) if price["cached_input_usd_per_m"] else 0.0
    gap = (p_in * inp + p_out * outp) / 1e6 - cost
    if p_in <= p_cache:
        return 0.0, "no_cache_rate"
    reads = gap / ((p_in - p_cache) / 1e6)
    if abs(reads) <= 0.5:                       # sub-token gap: billed at the gross list price
        return 0.0, "no_cache_discount_billed"
    if reads < 0:
        return 0.0, "billed_above_sheet_rate"
    if reads > inp:
        return inp, "capped_at_input"
    return reads, "inverted_from_billed_cost"


def build_point(m, r, window_s, human_mean, human_floor, n_entries, n_problems) -> dict:
    cfg = m["leaderboard_config"]
    if r["cache_reads_deducted"]:
        cache_clause = (
            "Cache reads implied by the billed cost are removed; the gross count is "
            f"{r['scenario_multiplier_gross_over_central']:.2f}x this. "
        )
    elif r["cache_inference_basis"] == "no_cache_discount_billed":
        cache_clause = "Billed cost lands on the gross list price, so no cache discount was taken. "
    elif r["cache_basis_cause"]:
        cache_clause = f"No cache split inverts: {r['cache_basis_cause']}, so input is gross. "
    else:
        cache_clause = "No cache split inverts from the billed cost, so input is gross. "
    if r["cache_reads_deducted"] and not r["billing_window_covers_its_date"]:
        cache_clause += "The model was retired before the cost date, so its last price window prices it. "
    if r.get("ai_cost_repriced_from_harness_window"):
        cache_clause += "Cost is repriced at the rates the cost date selects, not the launch rates billed. "
    note = (
        f"Human time is the contest window ({window_s / 3600:.2f} h mean), not measured effort; AHC "
        "publishes none. Published tokens cover the submitted sample only, so compute scales them by "
        f"the harness's {r['n_samples']} samples, taking the discarded ones to match it. "
        f"{cache_clause}Input is {100 * r['input_share_of_tokens']:.0f}% of tokens. The agent sees the "
        "scorer source and 50 local cases but no live leaderboard, and is re-scored on 150 private seeds."
    )
    if r["close_call"]:
        note += f" Kept at {r['ratio_to_human']:.2f} by the one-standard-error close-call rule."
    if m["model_id"] == "gpt-5-6-sol":
        note += " The ruled 150B prior raises this 1.5x at merge."
    if m["model_id"] == "gemini-2.5-flash":
        note += " The ruled 25B prior lowers this 0.625x at merge."
    if m["model_id"] == "grok-4.20-beta-0309b-reasoning":
        note += " The registry ID names a 0309b endpoint; this run used the OpenRouter alias."
    return {
        "point_id": r["point_id"],
        "task": "Solve one short-format AtCoder Heuristic Contest problem",
        "task_category": "coding",
        "task_description": (
            f"One of ALE-Bench's {n_problems} short-format AtCoder Heuristic Contest problems (windows 3.5 to "
            "6 hours, 21 of them 4 hours): an NP-hard optimisation task in routing, packing, scheduling, "
            "covering, planning or inference with no known optimum. The deliverable is one C++20 program "
            "inside the contest's limits, scored by the contest's own scorer over 150 "
            "private cases, ranked against that contest's entrants and converted to an AtCoder "
            "performance. The harness samples 15 solutions and submits the one scoring median on 50 "
            "local cases."
        ),
        "model_id": m["model_id"],
        "compute_scope": "inference",
        "compute_flops": repr(r["compute_flops"]),
        "human_skill": "expert",
        "human_time_scope": "task_performance",
        "human_time": fmt(window_s, 1),
        "performance_vs_human": r["label"],
        "comparison_issues": "different_inputs_or_tools; different_assessment",
        "compute_evidence": "derived_assumed_inputs",
        "human_time_evidence": "defined_duration",
        "performance_evidence": (
            f"AtCoder performance, the contests' own Elo-like transform of final rank, averaged over the "
            f"{n_problems} short-format problems: {r['performance_short_mean']:.0f} against "
            f"{human_mean:.1f}, the unweighted mean of those {n_problems} contests' own entrant means. "
            f"Ratio {r['ratio_to_human']:.2f} once the {human_floor:.1f} last-place floor is subtracted. "
            f"Mean rank {r['mean_rank_over_23_contests']:.0f} of {r['mean_entrants_per_contest']:.0f} "
            f"entrants, {r['mean_share_of_field_above_pct']:.1f}% of the field above it"
            + (f", 1st on {r['contests_ranked_first']} of {n_problems}." if r["contests_ranked_first"] else ".")
        ),
        "human_time_statistic": "point_estimate",
        "human_time_subset": "not_applicable",
        "human_attempts": "not_applicable",
        "human_time_source": (
            "agent-work/sources/ale-bench/alebench-human-performance-per-problem.csv; research/ale-bench.md#human-time"
        ),
        "human_time_method": "work_rate",
        "compute_method": "params_tokens",
        "compute_statistic": "mean",
        "compute_subset": "all",
        "ai_attempts": str(n_problems),
        "compute_source": (
            f"research/ale-bench.md#{r['point_id']}; research/ale-bench/build_rows.py; "
            "agent-work/sources/ale-bench/alebench-leaderboard-aggregates.csv"
        ),
        "tokens": repr(r["tokens"]),
        "tokens_accounting": "input_cache_creation_output" if r["cache_reads_deducted"] else "input_output",
        "source_dataset": "ALE-Bench leaderboard (AtCoder Heuristic Contests)",
        "source_record": (
            f"ALE-Bench leaderboard version {LEADERBOARD_VERSION}, configuration {cfg} ({m['effort_note']}), "
            f"model {m['config_model_name']}, self-refine x1, C++20, judge 202301, the 23 short-format "
            "problems of 40; per-problem records in "
            "agent-work/sources/ale-bench/alebench-leaderboard-selfrefine1-short.csv; performance: the same "
            "records against each contest's own entrant field"
        ),
        "notes": note,
        "ai_cost_usd": repr(r["ai_cost_usd"]),
        "ai_cost_basis": "list_price",
        "ai_cost_date": LEADERBOARD_VERSION,
        "human_cost_usd": "",
        "human_cost_basis": "not_available",
    }


# --- AHC058 ------------------------------------------------------------------
AHC058_API_USD = 1000.0          # Sakana: "about $1,000 in API fees"
AHC058_CALLS = {"gpt-5.2-2025-12-11": 2654, "gemini-3-pro-preview": 2119}
AHC058_DONOR = {"gpt-5.2-2025-12-11": "gpt-5.2-high", "gemini-3-pro-preview": "gemini-3-pro-preview-high"}
AHC058_PRICES = {  # USD per million tokens, list prices in force on 2025-12-14
    "gpt-5.2-2025-12-11": (1.75, 14.00),
    "gemini-3-pro-preview": (2.00, 12.00),
}


def build_ahc058(src: Path, agg: dict, coefficients: dict) -> tuple[dict, dict]:
    per_model, gross_cost = {}, 0.0
    for model_id, calls in AHC058_CALLS.items():
        a = agg[(AHC058_DONOR[model_id], 1)]
        inp, outp = float(a["input_tokens_short"]), float(a["output_tokens_short"])
        p_in, p_out = AHC058_PRICES[model_id]
        cost = calls * (inp * p_in + outp * p_out) / 1e6
        gross_cost += cost
        per_model[model_id] = {"calls": calls, "input_per_call": inp, "output_per_call": outp, "cadence_cost": cost}
    k = AHC058_API_USD / gross_cost
    tokens = sum(v["calls"] * (v["input_per_call"] + v["output_per_call"]) for v in per_model.values()) * k
    flops = sum(
        v["calls"] * (v["input_per_call"] + v["output_per_call"]) * k * coefficients[mid]
        for mid, v in per_model.items()
    )
    calc = {
        "point_id": "agen-ahc058-ale-agent",
        "per_model": per_model,
        "cadence_matched_cost_usd": gross_cost,
        "reported_api_cost_usd": AHC058_API_USD,
        "scale_factor_k": k,
        "tokens": tokens,
        "compute_flops": flops,
        "human_mean_performance": 1384.3,
        "label": "far_above",
    }
    point = {
        "point_id": "agen-ahc058-ale-agent",
        "task": "Win AtCoder Heuristic Contest 058 live",
        "task_category": "coding",
        "task_description": (
            "AtCoder Heuristic Contest 058, run live on 2025-12-14 over a 240-minute window: a "
            "hierarchical production-planning problem in which machines build other machines "
            "and a 500-step investment order must be chosen. The deliverable is one program submitted to "
            "AtCoder's judge inside the window and ranked by the contest's own score. Sakana AI's "
            "ALE-Agent entered as the account fishylene against the contest's human field, generating "
            "candidate solutions in parallel with two frontier models, evaluating them locally and "
            "refining them without human intervention."
        ),
        "model_id": "gpt-5.2-2025-12-11",
        "compute_scope": "inference",
        "compute_flops": repr(flops),
        "human_skill": "expert",
        "human_time_scope": "task_performance",
        "human_time": "14400",
        "performance_vs_human": "far_above",
        "comparison_issues": "none_identified",
        "compute_evidence": "derived_assumed_inputs",
        "human_time_evidence": "defined_duration",
        "performance_evidence": (
            "ALE-Agent placed 1st on the contest's own standings, ahead of all 804 rated human "
            "entrants; 1,317 entries are listed and 804 is the rated field Sakana calls the "
            "participants. The top rated human's official performance is 3535 and the 804 average "
            "1384, so the mean entrant reaches 39% of the standing the agent surpassed."
        ),
        "human_time_statistic": "point_estimate",
        "human_time_subset": "not_applicable",
        "human_attempts": "not_applicable",
        "human_time_source": "agent-work/sources/ale-bench/ahc058-sakana-report.txt; research/ale-bench.md#human-time",
        "human_time_method": "work_rate",
        "compute_method": "params_tokens",
        "compute_statistic": "total",
        "compute_subset": "all",
        "ai_attempts": "1",
        "compute_source": (
            "research/ale-bench.md#agen-ahc058-ale-agent; research/ale-bench/build_rows.py; "
            "agent-work/sources/ale-bench/ahc058-sakana-report.txt"
        ),
        "tokens": repr(tokens),
        "tokens_accounting": "input_output",
        "source_dataset": "Sakana AI ALE-Agent, AtCoder Heuristic Contest 058",
        "source_record": (
            "Sakana AI report of 2026-01-05 on the AHC058 run of 2025-12-14: 2,654 GPT-5.2 high-reasoning "
            "calls, 2,119 Gemini 3 Pro Preview high-thinking calls, about $1,000 in API fees within a "
            "$1,300 total; AtCoder contest ahc058, account fishylene, place 1; official results in "
            "agent-work/sources/ale-bench/ahc058-atcoder-results.csv; performance: the same standings"
        ),
        "notes": (
            "Compute inverts the reported API spend: per-call input and output come from the ALE-Bench "
            "leaderboard's measured one-shot calls by these same two configurations, scaled by 0.771 so "
            "the call counts price to $1,000 at December 2025 list rates. The unscaled cadence gives "
            "1.30x, which prices to the $1,300 all-in figure. Gemini 3 Pro contributes 45% of the "
            "tokens; model_id wrote the winning submission. compute_flops and ai_cost_usd are one "
            "observation, not two, since the FLOPs invert the spend. Human time is the contest "
            "window, which bounds entrants' effort but does not measure it."
        ),
        "ai_cost_usd": "1000",
        "ai_cost_basis": "reported",
        "ai_cost_date": "2025-12-14",
        "human_cost_usd": "",
        "human_cost_basis": "not_available",
    }
    return point, calc


PAPER_DISPOSITIONS = [
    {
        "cell": "ALE-Bench paper one-shot setting, 22 models x 3 languages (Tables 1, 2, A3)",
        "kind": "not a row",
        "n": 23,
        "ai_performance": "",
        "human_performance": "1414.5",
        "ratio_to_human": "",
        "se_of_ratio": "",
        "reason": (
            "The paper publishes no token counts; its cost per problem is pooled over all 40 problems "
            "and rounded to three decimals, so for most models it carries one or two significant figures "
            "and cannot be split onto the 23 short-format problems that carry the defensible human "
            "duration. The 2026-09-08 leaderboard supersedes it with measured token counts for the "
            "models it covers"
        ),
    },
    {
        "cell": "ALE-Bench paper iterative-refinement setting, 4 models (Table 3)",
        "kind": "not a row",
        "n": 23,
        "ai_performance": "",
        "human_performance": "1414.5",
        "ratio_to_human": "",
        "se_of_ratio": "",
        "reason": (
            "Same cost-only evidence as the one-shot setting, and the four-hour refinement chain resends "
            "its context each turn, so an inverted token total could not be split between fresh input and "
            "cache reads. o4-mini-high, Gemini 2.5 Pro and DeepSeek-R1 are all on the leaderboard"
        ),
    },
    {
        "cell": "ALE-Bench paper scaffolding setting, OpenHands and ALE-Agent variants (Tables 4, A5, A6)",
        "kind": "not a row",
        "n": 5,
        "ai_performance": "2284.8",
        "human_performance": "1520.0",
        "ratio_to_human": "1.50",
        "se_of_ratio": "",
        "reason": (
            "ALE-Agent with both methods averages 2285 performance on the five short-format lite problems "
            "against 1520 for their mean entrant, which would be an above row, but its $100.33 per problem "
            "is pooled over five short and five long problems and no token counts are published, so the "
            "compute cannot be put on the short subset. The AHC058 row carries the same system on stronger "
            "evidence"
        ),
    },
    {
        "cell": "ALE-Bench long-format problems, all settings",
        "kind": "not a row",
        "n": 17,
        "ai_performance": "",
        "human_performance": "1422.8",
        "ratio_to_human": "",
        "se_of_ratio": "",
        "reason": (
            "Contest windows run 199 to 367 hours of calendar time over 8 to 15 days, so the window is not "
            "a bound on effort and no active-time measurement exists; a human duration here would be a "
            "guess rather than a defined duration"
        ),
    },
]


def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
