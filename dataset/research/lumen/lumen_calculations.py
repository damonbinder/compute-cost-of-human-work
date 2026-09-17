#!/usr/bin/env python3
"""Compute the AI-compute and human-time values for the five LUMEN domain reviews.

Reads the transcribed paper values and the two model tables, writes one JSON file
holding every intermediate quantity used in research/lumen.md and in
candidates/lumen/points.csv.

Dependencies: Python 3.9+ standard library only (csv, json, argparse, statistics).

Usage (paths are explicit; nothing is resolved relative to this file):

    python3 lumen_calculations.py \
        --source   .../sources/lumen/lumen-source-values.json \
        --dataset-models .../AI Compute vs Human Time/dataset/models.csv \
        --local-models   .../AI Compute vs Human Time claude-rows/models.csv \
        --candidate-models .../AI Compute vs Human Time claude-rows/candidates/lumen/models.csv \
        --output   .../research/lumen/calculations.json

--local-models and --candidate-models are both optional; coefficients are looked
up in the dataset table first, then the local table, then the candidate table.
The script only reads the model tables; it writes nothing but --output.
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
from pathlib import Path


def load_coefficients(paths):
    """model_id -> flops_per_token, from the first table that defines it."""
    coeffs = {}
    for path in paths:
        if path is None:
            continue
        p = Path(path)
        if not p.exists():
            continue
        with open(p, newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                mid = row["model_id"]
                val = row.get("flops_per_token", "")
                if mid in coeffs or not val or val in ("not_applicable", ""):
                    continue
                coeffs[mid] = float(val)
    return coeffs


def allen_olkin_hours(citations):
    """Allen IE, Olkin I. JAMA 1999;282(7):634-5. Total hours from citations retrieved."""
    return 721.0 + 0.243 * citations - 0.0000123 * citations ** 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True)
    ap.add_argument("--dataset-models", required=True)
    ap.add_argument("--local-models")
    ap.add_argument("--candidate-models")
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    src = json.load(open(args.source, encoding="utf-8"))
    coeffs = load_coefficients(
        [args.dataset_models, args.local_models, args.candidate_models]
    )

    reviews = ["D1", "D2", "D3", "D4", "D5"]
    phases = src["per_phase_medians_tableS1"]
    routing = src["model_routing_table1"]
    costs = src["cost_by_phase_usd_table3"]
    prices = src["list_prices_usd_per_million_march_2026"]

    out = {
        "provenance": src["_provenance"],
        "coefficients_used": {},
        "phase_effective_coefficients": {},
        "median_review": {},
        "per_review": {},
        "dollar_cross_check": {},
        "human_time": {},
        "scenarios": {},
    }

    # ---- effective FLOPs-per-token coefficient for each phase ------------------
    for phase, share in routing.items():
        eff = 0.0
        for model_id, frac in share.items():
            if model_id not in coeffs:
                raise SystemExit(
                    f"model_id {model_id!r} has no flops_per_token in the supplied "
                    f"model tables"
                )
            out["coefficients_used"][model_id] = coeffs[model_id]
            eff += frac * coeffs[model_id]
        out["phase_effective_coefficients"][phase] = eff

    # ---- the published median run ---------------------------------------------
    med_in = sum(p["input_tokens"] for p in phases.values())
    med_out = sum(p["output_tokens"] for p in phases.values())
    med_flops = 0.0
    med_phase_rows = {}
    derived_screen = src["derived_screening_calls"]
    for phase, p in phases.items():
        toks = p["input_tokens"] + p["output_tokens"]
        f = toks * out["phase_effective_coefficients"][phase]
        med_flops += f
        # Table S1's P3.1 call count is refuted by Table S3 (both screeners scored every
        # screened record); the derived median is used and the reported one is retained
        # beside it so the discrepancy is visible rather than silently carried.
        refuted = phase == "P3.1_screen"
        calls = derived_screen["median"] if refuted else p["calls"]
        med_phase_rows[phase] = {
            "input_tokens": p["input_tokens"],
            "output_tokens": p["output_tokens"],
            "tokens": toks,
            "calls": calls,
            "mean_input_tokens_per_call": p["input_tokens"] / calls,
            "effective_flops_per_token": out["phase_effective_coefficients"][phase],
            "flops": f,
        }
        if refuted:
            med_phase_rows[phase]["calls_basis"] = (
                "derived as 2 x screened + arbiter from Tables S2 and S3"
            )
            med_phase_rows[phase]["calls_reported_tableS1"] = p["calls"]
            med_phase_rows[phase]["calls_reported_tableS1_status"] = (
                "refuted by Table S3 and by Table S1's own range maximum of 7,520; not used"
            )
    out["median_review"] = {
        "description": (
            "Sum of the Table S1 per-phase medians. This is a composite of five runs, "
            "not the median total of any single run."
        ),
        "input_tokens": med_in,
        "output_tokens": med_out,
        "tokens": med_in + med_out,
        "wallclock_min": sum(p["wallclock_min"] for p in phases.values()),
        "compute_flops": med_flops,
        "by_phase": med_phase_rows,
    }

    # ---- per-review allocation -------------------------------------------------
    # Within a Table 3 phase group, dollars are a linear function of tokens (fixed
    # per-model prices), so token counts are allocated across reviews in proportion
    # to that group's published dollars, anchored on the Table S1 median tokens.
    group_median_cost = {
        g: statistics.median([costs[g][r] for r in reviews]) for g in costs
    }
    out["group_median_cost_usd"] = group_median_cost

    group_median_tokens = {}
    for phase, p in phases.items():
        g = p["table3_group"]
        acc = group_median_tokens.setdefault(g, {"input": 0, "output": 0})
        acc["input"] += p["input_tokens"]
        acc["output"] += p["output_tokens"]
    out["group_median_tokens"] = group_median_tokens

    for r in reviews:
        per_phase = {}
        total_in = total_out = total_flops = 0.0
        for phase, p in phases.items():
            g = p["table3_group"]
            scale = costs[g][r] / group_median_cost[g]
            # within a group, sub-phases keep their median token shares
            share_in = (
                p["input_tokens"] / group_median_tokens[g]["input"]
                if group_median_tokens[g]["input"]
                else 0.0
            )
            share_out = (
                p["output_tokens"] / group_median_tokens[g]["output"]
                if group_median_tokens[g]["output"]
                else 0.0
            )
            tin = group_median_tokens[g]["input"] * scale * share_in
            tout = group_median_tokens[g]["output"] * scale * share_out
            eff = out["phase_effective_coefficients"][phase]
            f = (tin + tout) * eff
            per_phase[phase] = {
                "group": g,
                "group_cost_usd": costs[g][r],
                "scale_vs_group_median_cost": scale,
                "input_tokens": tin,
                "output_tokens": tout,
                "tokens": tin + tout,
                "flops": f,
            }
            total_in += tin
            total_out += tout
            total_flops += f
        out["per_review"][r] = {
            **src["datasets_table2"][r],
            "reported_total_cost_usd": src["cost_total_usd_table3"][r],
            "input_tokens": total_in,
            "output_tokens": total_out,
            "tokens": total_in + total_out,
            "compute_flops": total_flops,
            "by_phase": per_phase,
        }

    # ---- dollar cross-check ----------------------------------------------------
    # Predict the bill from the allocated tokens at March 2026 list prices and the
    # routing shares, and compare with the reported Table 3 dollars.
    def predict_cost(phase, tin, tout):
        c = 0.0
        for model_id, frac in routing[phase].items():
            pr = prices[model_id]
            c += (tin * frac / 1e6) * pr["input"] + (tout * frac / 1e6) * pr["output"]
        return c

    med_pred_by_group = {}
    for phase, p in phases.items():
        g = p["table3_group"]
        med_pred_by_group[g] = med_pred_by_group.get(g, 0.0) + predict_cost(
            phase, p["input_tokens"], p["output_tokens"]
        )
    out["dollar_cross_check"]["median_review_by_group"] = {
        g: {
            "predicted_usd": med_pred_by_group[g],
            "reported_median_usd": group_median_cost[g],
            "reported_over_predicted": group_median_cost[g] / med_pred_by_group[g],
        }
        for g in group_median_cost
    }
    tot_pred = sum(med_pred_by_group.values())
    tot_rep = sum(group_median_cost.values())
    out["dollar_cross_check"]["median_review_total"] = {
        "predicted_usd": tot_pred,
        "reported_sum_of_group_medians_usd": tot_rep,
        "reported_median_total_usd": statistics.median(
            [src["cost_total_usd_table3"][r] for r in reviews]
        ),
        "reported_over_predicted": tot_rep / tot_pred,
    }

    # ---- scenarios -------------------------------------------------------------
    # (a) dollar-reconciled tokens: scale each group's tokens so the predicted bill
    #     equals the reported bill at list prices.
    recon = {}
    for r in reviews:
        tokens = 0.0
        flops = 0.0
        for phase, p in phases.items():
            g = p["table3_group"]
            k = out["dollar_cross_check"]["median_review_by_group"][g][
                "reported_over_predicted"
            ]
            pp = out["per_review"][r]["by_phase"][phase]
            tokens += pp["tokens"] * k
            flops += pp["flops"] * k
        recon[r] = {"tokens": tokens, "compute_flops": flops}
    out["scenarios"]["dollar_reconciled"] = {
        "description": (
            "Each Table 3 group's tokens multiplied by the factor that makes the "
            "token-implied bill at March 2026 list prices equal the reported bill."
        ),
        "per_review": recon,
    }

    # (b) omitted cached-context attention term, 4 * layers * d_model * n_context
    #     per processed token, applied at each phase's mean input length per call.
    #     P3.1 uses the call count derived from Table S3 (both screeners scored every
    #     screened record), not Table S1's P3.1 median, which Table S3 refutes.
    derived_calls = src["derived_screening_calls"]

    def phase_calls(phase, p):
        return derived_calls["median"] if phase == "P3.1_screen" else p["calls"]

    att = {}
    for arch in src["attention_architectures"]:
        per_review_att = {}
        for r in reviews:
            extra = 0.0
            for phase, p in phases.items():
                n_ctx = p["input_tokens"] / phase_calls(phase, p)
                per_tok = 4 * arch["layers"] * arch["d_model"] * n_ctx
                extra += out["per_review"][r]["by_phase"][phase]["tokens"] * per_tok
            base = out["per_review"][r]["compute_flops"]
            per_review_att[r] = {
                "attention_flops": extra,
                "fraction_of_recorded": extra / base,
                "total_with_attention": base + extra,
            }
        att[arch["label"]] = {
            "layers": arch["layers"],
            "d_model": arch["d_model"],
            "per_review": per_review_att,
        }
    out["scenarios"]["cached_context_attention"] = {
        "description": (
            "Attention term omitted by the 2 x active_parameters convention, using "
            "4 * layers * d_model * n_context per processed token at each phase's "
            "mean input length per call. One-sided; the recorded compute_flops "
            "excludes it. P3.1's context length uses the Table S3-derived median of "
            f"{derived_calls['median']} screening calls, giving "
            f"{phases['P3.1_screen']['input_tokens'] / derived_calls['median']:.0f} "
            "input tokens per call, or twice that if Table S1's P3.1 row is "
            "per-screener."
        ),
        "mean_input_tokens_per_call": {
            phase: p["input_tokens"] / phase_calls(phase, p)
            for phase, p in phases.items()
        },
        "architectures": att,
    }

    # (c) screening allocated by the Table S3-derived call count instead of by
    #     dollars. This is a derived per-review quantity, not a hypothesis, and it
    #     applies to all five rows.
    p31 = phases["P3.1_screen"]
    med_screen_tokens = p31["input_tokens"] + p31["output_tokens"]
    eff31 = out["phase_effective_coefficients"]["P3.1_screen"]
    calls_alloc = {}
    for r in reviews:
        toks = med_screen_tokens * derived_calls[r] / derived_calls["median"]
        base = out["per_review"][r]
        new_flops = base["compute_flops"] - base["by_phase"]["P3.1_screen"]["flops"] + toks * eff31
        calls_alloc[r] = {
            "derived_screening_calls": derived_calls[r],
            "screening_tokens": toks,
            "screening_tokens_dollar_allocated": base["by_phase"]["P3.1_screen"]["tokens"],
            "tokens": base["tokens"] - base["by_phase"]["P3.1_screen"]["tokens"] + toks,
            "compute_flops": new_flops,
            "ratio_to_recorded": new_flops / base["compute_flops"],
        }
    out["scenarios"]["screening_allocated_by_derived_calls"] = {
        "description": (
            "Screening tokens allocated across reviews by the Table S3-derived call "
            "count rather than by Table 3 dollars. Not adopted as central: it forces "
            "identical tokens per screened record across domains by construction, "
            "which the dollars say is false."
        ),
        "per_review": calls_alloc,
    }

    # tokens per screened record under each allocation, the check that discriminates them
    out["screening_tokens_per_record"] = {
        r: {
            "dollar_allocated": out["per_review"][r]["by_phase"]["P3.1_screen"]["tokens"]
            / src["datasets_table2"][r]["screened"],
            "usd_per_record": costs["P3.1_TA_screening"][r]
            / src["datasets_table2"][r]["screened"],
            "met_ovary_pilot_usd_per_record": src["met_ovary_pilot_repo_readme"]["derived"][
                "usd_per_record_screened"
            ],
        }
        for r in reviews
    }

    # ---- human time ------------------------------------------------------------
    ao = src["allen_olkin_1999"]
    admin_share = ao["components_mean_sd_hours"]["other_administrative"][0] / ao["mean_hours"]
    mr = src["michelson_reuter_2019"]
    mr_hours = mr["scientist_years_per_review"] * mr["hours_per_scientist_year"]
    ao_turning_point = 0.243 / (2 * 0.0000123)
    for r in reviews:
        d = src["datasets_table2"][r]
        h_yield = allen_olkin_hours(d["yield"])
        h_screened = allen_olkin_hours(d["screened"])
        midpoint = (d["yield"] + d["screened"]) / 2
        h_central = allen_olkin_hours(midpoint) * (1 - admin_share)  # 2026-09-16 central
        out["human_time"][r] = {
            "citations_midpoint": midpoint,
            "hours_central_midpoint_excluding_administrative": h_central,
            "seconds_central_rounded": round(h_central * 3600),
            "citations_retrieved_yield": d["yield"],
            "citations_after_dedup_prescreen": d["screened"],
            "hours_from_yield": h_yield,
            "seconds_from_yield": h_yield * 3600,
            "seconds_from_yield_rounded": round(h_yield * 3600),
            "hours_from_screened_alternative": h_screened,
            "hours_excluding_administrative": h_yield * (1 - admin_share),
            "michelson_reuter_hours": mr_hours,
            "ratio_michelson_reuter_to_central": mr_hours / h_yield,
            "flops_per_human_second": out["per_review"][r]["compute_flops"]
            / (h_central * 3600),
        }
    out["human_time"]["_model"] = {
        "equation": ao["equation"],
        "n_meta_analyses": ao["n_meta_analyses"],
        "sample_mean_hours": ao["mean_hours"],
        "sample_median_hours": ao["median_hours"],
        "sample_range_hours": ao["range_hours"],
        "administrative_share_of_mean": admin_share,
        "quadratic_turning_point_citations": ao_turning_point,
        "citations_implying_sample_mean": None,
    }
    # citation count at which the model reproduces the sample mean, by bisection
    lo, hi = 0.0, ao_turning_point
    for _ in range(200):
        mid = (lo + hi) / 2
        if allen_olkin_hours(mid) < ao["mean_hours"]:
            lo = mid
        else:
            hi = mid
    out["human_time"]["_model"]["citations_implying_sample_mean"] = (lo + hi) / 2

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2)
    print(f"wrote {args.output}")

    # short console summary
    print("\nreview  tokens(M)  FLOPs        human_h   FLOPs/human-s")
    for r in reviews:
        pr = out["per_review"][r]
        ht = out["human_time"][r]
        print(
            f"{r}      {pr['tokens']/1e6:7.3f}  {pr['compute_flops']:.3e}  "
            f"{ht['hours_from_yield']:7.0f}   {ht['flops_per_human_second']:.3e}"
        )
    m = out["median_review"]
    print(f"\nmedian composite: {m['tokens']/1e6:.3f}M tokens, {m['compute_flops']:.3e} FLOPs")
    cc = out["dollar_cross_check"]["median_review_total"]
    print(
        f"dollar cross-check: predicted ${cc['predicted_usd']:.2f} vs reported "
        f"${cc['reported_sum_of_group_medians_usd']:.2f} "
        f"({cc['reported_over_predicted']:.2f}x)"
    )
    for g, v in out["dollar_cross_check"]["median_review_by_group"].items():
        print(f"  {g:20s} predicted ${v['predicted_usd']:6.2f}  reported ${v['reported_median_usd']:6.2f}  x{v['reported_over_predicted']:.2f}")


if __name__ == "__main__":
    main()
