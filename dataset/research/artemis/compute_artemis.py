#!/usr/bin/env python3
"""Invert the ARTEMIS API spend into counted tokens and FLOPs for the A1 and A2 rows.

The paper publishes dollars and no token counts, so compute is cost-inverted under
DECISIONS.md's cost-only-compute ruling. Two independent routes are computed:

  1. a donor transfer, using measured FLOPs-per-dollar from accepted rows of this
     folder whose model, provider path and caching regime match the ARTEMIS
     configuration (GAIA HAL and Open Deep Research runs); and
  2. an analytic price-structure model, where a call is R input tokens and one
     output token with a cached share h, priced at the provider's list rates.

Reads only retained evidence; writes a single JSON to --out.

Usage:
    python3 compute_artemis.py \
        --donors agent-work/sources/artemis/gaia-donor-rows.csv \
        --prices ../../research/cost/list-prices.csv \
        --out calculations.json

Dependencies: Python 3.9+ standard library only.
"""
import argparse
import csv
import json
import math
from pathlib import Path

# Active-parameter coefficients, 2 x active parameters, from the Codex registry
# ../AI Compute vs Human Time/dataset/models.csv unless noted.
FLOPS_PER_TOKEN = {
    "gpt-5": 2.0e11,              # 100B active
    "claude-sonnet-4": 2.0e11,    # 100B active
    "claude-sonnet-4-5": 2.0e11,  # 100B active, donor for claude-sonnet-4
    "claude-opus-4": 3.6e11,      # 180B active
    "o3-2025-04-16": 1.0e11,      # 50B active
    "o3-pro": 1.0e11,             # assumed equal to o3: same weights, longer thinking
    "gemini-2.5-pro": 2.0e11,     # 100B active
    "o4-mini-2025-04-16": 4.0e10,  # 20B active
    "claude-opus-4-1": 3.6e11,    # 180B active
}

# o3-pro is absent from research/cost/list-prices.csv. Rates read from
# https://developers.openai.com/api/docs/pricing on 2026-09-13: no cached-input
# tier is published, so every input token is billed and counted.
O3_PRO_PRICE = {"input": 20.00, "cached_input": None, "output": 80.00}

REPORTED = {
    "A1": {"total_usd": 291.47, "usd_per_hour": 18.21},
    "A2": {"total_usd": 944.07, "usd_per_hour": 59.00},
}
RUN_HOURS = 16.0
SCORED_HOURS = 10.0


def load_prices(path: Path):
    out = {}
    with path.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            out.setdefault(row["model_id"], []).append(row)
    return out


def price_at(prices, model_id, date):
    for row in prices.get(model_id, []):
        start = row["price_sheet_start"] or "0000-00-00"
        end = row["price_sheet_end"] or "9999-99-99"
        if start <= date <= end:
            return {
                "input": float(row["input_usd_per_m"]),
                "cached_input": float(row["cached_input_usd_per_m"]) if row["cached_input_usd_per_m"] else None,
                "output": float(row["output_usd_per_m"]),
                "source_url": row["source_url"],
            }
    raise KeyError(f"no price row for {model_id} at {date}")


def flops_per_dollar(price, fpt, R, h):
    """R input tokens and one output token per call; h of the input read from cache.

    Cache reads are excluded from the parameter-multiplication term, per COLUMNS.md.
    A model with no cached-input tier is priced and counted at h = 0.
    """
    if price["cached_input"] is None:
        h = 0.0
    fresh = R * (1.0 - h)
    cached = R * h
    counted = fresh + 1.0
    usd = (price["input"] * fresh + (price["cached_input"] or 0.0) * cached + price["output"]) / 1e6
    return fpt * counted / usd


def implied_R(measured_fpd, price, fpt):
    """Invert an uncached measurement for R, the input tokens per output token."""
    p_in, p_out = price["input"], price["output"]
    # measured = fpt (R+1) 1e6 / (p_in R + p_out)
    k = measured_fpd / (fpt * 1e6)
    return (1.0 - k * p_out) / (k * p_in - 1.0)


def donor_families(path: Path):
    fams = {}
    with path.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            fam = row["point_id"].rsplit("-l", 1)[0]
            n = float(row["ai_attempts"])
            d = fams.setdefault(fam, {"model_id": row["model_id"], "questions": 0.0,
                                      "flops": 0.0, "usd": 0.0, "rows": []})
            d["questions"] += n
            d["flops"] += n * float(row["compute_flops"])
            d["usd"] += n * float(row["ai_cost_usd"])
            d["rows"].append(row["point_id"])
    for d in fams.values():
        d["flops_per_usd"] = d["flops"] / d["usd"]
    return fams


def attention_multiple(L, d_model, n_context, fpt):
    """4 L d_model N per processed position, as a multiple of the recorded 2P per token."""
    return 4.0 * L * d_model * n_context / fpt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--donors", required=True, type=Path)
    ap.add_argument("--prices", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--table1", type=Path, default=None,
                    help="table1-scores.csv written by extract_paper_tables.py")
    ap.add_argument("--date", default="2025-09-06",
                    help="date whose price sheet applies; the study window")
    args = ap.parse_args()

    prices = load_prices(args.prices)
    px = {m: price_at(prices, m, args.date)
          for m in ["gpt-5", "claude-sonnet-4", "claude-opus-4", "claude-opus-4-1",
                    "o3-2025-04-16", "gemini-2.5-pro", "o4-mini-2025-04-16"]}
    px["o3-pro"] = dict(O3_PRO_PRICE, source_url="https://developers.openai.com/api/docs/pricing")
    px["claude-sonnet-4-5"] = price_at(prices, "claude-sonnet-4-5", "2025-10-01")

    fams = donor_families(args.donors)
    out = {"reported": REPORTED, "run_hours": RUN_HOURS, "scored_hours": SCORED_HOURS,
           "price_date": args.date,
           "prices": {k: v for k, v in px.items()},
           "donor_families": fams}

    # ---- call structure, calibrated on the uncached Anthropic donors -------------
    calib = {}
    for fam, target in [("agen-gaia-hal-sonnet45", "claude-sonnet-4-5"),
                        ("agen-gaia-hal-sonnet45high", "claude-sonnet-4-5"),
                        ("agen-gaia-hal-opus4high", "claude-opus-4"),
                        ("agen-gaia-odr-opus4", "claude-opus-4")]:
        if fam in fams:
            calib[fam] = {
                "model": target,
                "flops_per_usd": fams[fam]["flops_per_usd"],
                "implied_R": implied_R(fams[fam]["flops_per_usd"], px[target], FLOPS_PER_TOKEN[target]),
            }
    out["uncached_donor_calibration"] = calib
    R_band = (40.0, 120.0)
    R_mid = 60.0
    out["call_structure"] = {
        "R_input_per_output_band": R_band,
        "R_mid": R_mid,
        "basis": "solved from the uncached Anthropic donor runs; see uncached_donor_calibration",
    }

    # ---- A1: GPT-5 throughout, OpenAI path, automatic caching --------------------
    a1_donors = {k: fams[k]["flops_per_usd"] for k in ("agen-gaia-hal-gpt5", "agen-gaia-odr-gpt5")}
    a1_low, a1_high = min(a1_donors.values()), max(a1_donors.values())
    a1_central_fpd = math.sqrt(a1_low * a1_high)
    a1_structural = {
        f"R={R}_h={h}": flops_per_dollar(px["gpt-5"], FLOPS_PER_TOKEN["gpt-5"], R, h)
        for R in (40, 60, 120) for h in (0.0, 0.5, 0.8, 0.9, 0.95)
    }
    a1_usd = REPORTED["A1"]["total_usd"] * SCORED_HOURS / RUN_HOURS
    out["A1"] = {
        "model_mix": "GPT-5 supervisor, sub-agents, triage and prompt generation; "
                     "o4-mini summarization and routing as an unquantified minority share",
        "donor_flops_per_usd": a1_donors,
        "flops_per_usd_low": a1_low,
        "flops_per_usd_high": a1_high,
        "flops_per_usd_central": a1_central_fpd,
        "structural_cross_check": a1_structural,
        "usd_16h": REPORTED["A1"]["total_usd"],
        "usd_10h": a1_usd,
        "flops_central": a1_usd * a1_central_fpd,
        "flops_low": a1_usd * a1_low,
        "flops_high": a1_usd * a1_high,
        "tokens_central": a1_usd * a1_central_fpd / FLOPS_PER_TOKEN["gpt-5"],
        "flops_16h_central": REPORTED["A1"]["total_usd"] * a1_central_fpd,
        "o3_rotation_scenario": {
            # OPENAI_AVAILABLE_MODELS defaults to "o3,gpt-5", so on the OpenAI path a
            # continuation would move the supervisor to o3. The paper says A1 used GPT-5
            # for supervisor and sub-agents, which is the better authority on what ran;
            # this bounds the alternative.
            f"o3_share_{x}": (1 - x) * a1_central_fpd + x * flops_per_dollar(
                px["o3-2025-04-16"], FLOPS_PER_TOKEN["o3-2025-04-16"], 60, 0.8)
            for x in (0.10, 0.15, 0.20)
        },
        "o4mini_helper_sensitivity": {
            "share_0.05": 0.95 * a1_central_fpd + 0.05 * fams["agen-gaia-hal-o4minihigh"]["flops_per_usd"]
            if "agen-gaia-hal-o4minihigh" in fams else None,
        },
    }

    # ---- A2: Sonnet 4 sub-agents, rotating supervisor, pinned triager -----------
    pool = ["claude-sonnet-4", "o3-2025-04-16", "claude-opus-4", "gemini-2.5-pro", "o3-pro"]
    helpers = ["claude-opus-4-1", "o4-mini-2025-04-16"]
    # Per-model FLOPs per dollar at the mid structure. Anthropic and o3-pro have no
    # usable cache on this harness (no cache_control; no cached tier), so h = 0.
    h_by_model = {"claude-sonnet-4": 0.0, "claude-opus-4": 0.0, "o3-pro": 0.0,
                  "o3-2025-04-16": 0.8, "gemini-2.5-pro": 0.8,
                  "claude-opus-4-1": 0.0, "o4-mini-2025-04-16": 0.8}
    per_model = {}
    for m in pool + helpers:
        per_model[m] = {
            "mid": flops_per_dollar(px[m], FLOPS_PER_TOKEN[m], R_mid, h_by_model[m]),
            "R40": flops_per_dollar(px[m], FLOPS_PER_TOKEN[m], 40, h_by_model[m]),
            "R120": flops_per_dollar(px[m], FLOPS_PER_TOKEN[m], 120, h_by_model[m]),
            "no_cache": flops_per_dollar(px[m], FLOPS_PER_TOKEN[m], R_mid, 0.0),
            "h95": flops_per_dollar(px[m], FLOPS_PER_TOKEN[m], R_mid, 0.95),
            "flops_per_token": FLOPS_PER_TOKEN[m],
        }
    # Donor-measured values replace the analytic ones where a matching run exists.
    per_model["claude-sonnet-4"]["donor"] = (fams["agen-gaia-hal-sonnet45"]["flops_per_usd"]
                                             + fams["agen-gaia-hal-sonnet45high"]["flops_per_usd"]) / 2
    per_model["claude-opus-4"]["donor"] = (fams["agen-gaia-hal-opus4high"]["flops_per_usd"]
                                           + fams["agen-gaia-odr-opus4"]["flops_per_usd"]) / 2
    per_model["claude-opus-4-1"]["donor"] = fams["agen-gaia-odr-opus41"]["flops_per_usd"]
    per_model["o4-mini-2025-04-16"]["donor"] = fams["agen-gaia-hal-o4minihigh"]["flops_per_usd"]
    used = {m: per_model[m].get("donor", per_model[m]["mid"]) for m in pool + helpers}

    # The scaffold draws the next supervisor model uniformly at random from the pool,
    # so equal shares are defensible in two ways and neither is privileged: equal
    # dollars per pool member, or equal calls per pool member, which makes dollars
    # proportional to the per-call price. Both are computed and the central is their
    # geometric mean, following DECISIONS.md on two defensible transfers.
    usd_per_call = {}
    for m in pool:
        h = h_by_model[m] if px[m]["cached_input"] is not None else 0.0
        usd_per_call[m] = (px[m]["input"] * R_mid * (1 - h)
                           + (px[m]["cached_input"] or 0.0) * R_mid * h
                           + px[m]["output"]) / 1e6
    call_equal = {m: usd_per_call[m] / sum(usd_per_call.values()) for m in pool}
    out.setdefault("A2_allocation", {})["usd_per_call"] = usd_per_call
    out["A2_allocation"]["call_equal_dollar_shares"] = call_equal
    # TriageManager is constructed once with the supervisor model live at startup and
    # is never reassigned when _switch_to_random_model fires, so triage dollars sit on
    # one model. The scaffold's own documentation recommends starting on Sonnet 4 and
    # the paper lists it first, so that is the central; other pool members are scenarios.
    out["A2_allocation"]["helper_note"] = (
        "OpenRouter-path defaults put prompt and TODO generation on anthropic/claude-opus-4.1 "
        "and summarization and routing on openai/o4-mini; both sit near 2.1e16 FLOPs per "
        "dollar, so the split between them is immaterial")

    def a2_blend(sub, sup, tri, help_share, sup_shares, triage_model):
        shares = {m: sup * sup_shares.get(m, 0.0) for m in pool}
        shares["claude-sonnet-4"] += sub
        shares[triage_model] = shares.get(triage_model, 0.0) + tri
        for m in helpers:
            shares[m] = shares.get(m, 0.0) + help_share / len(helpers)
        assert abs(sum(shares.values()) - 1.0) < 1e-9, sum(shares.values())
        fpd = sum(shares[m] * used[m] for m in shares)
        tok = sum(shares[m] * used[m] / FLOPS_PER_TOKEN[m] for m in shares)
        usd10 = REPORTED["A2"]["total_usd"] * SCORED_HOURS / RUN_HOURS
        return {"dollar_shares": shares, "flops_per_usd": fpd, "tokens_per_usd": tok,
                "per_model_10h": {m: {"usd": shares[m] * usd10,
                                      "tokens": shares[m] * usd10 * used[m] / FLOPS_PER_TOKEN[m],
                                      "flops": shares[m] * usd10 * used[m]}
                                  for m in shares if shares[m] > 0}}

    # Shares respect the paper's stated ordering, sub-agents > supervisor > triage, with
    # the unnamed helpers below triage.
    equal_pool = {m: 0.2 for m in pool}
    gem_son = {"gemini-2.5-pro": 0.5, "claude-sonnet-4": 0.5}
    a2 = {
        "dollar_equal": a2_blend(0.55, 0.20, 0.15, 0.10, equal_pool, "claude-sonnet-4"),
        "call_equal": a2_blend(0.55, 0.20, 0.15, 0.10, call_equal, "claude-sonnet-4"),
        "low": a2_blend(0.40, 0.30, 0.20, 0.10, call_equal, "claude-opus-4"),
        "high": a2_blend(0.70, 0.15, 0.10, 0.05, gem_son, "claude-sonnet-4"),
        "triage_on_opus4": a2_blend(0.55, 0.20, 0.15, 0.10, call_equal, "claude-opus-4"),
        "triage_on_o3pro": a2_blend(0.55, 0.20, 0.15, 0.10, call_equal, "o3-pro"),
        "no_helpers_rotating_triage": a2_blend(0.55, 0.45, 0.0, 0.0, call_equal, "claude-sonnet-4"),
    }
    a2["central"] = {
        "flops_per_usd": math.sqrt(a2["dollar_equal"]["flops_per_usd"] * a2["call_equal"]["flops_per_usd"]),
        "tokens_per_usd": math.sqrt(a2["dollar_equal"]["tokens_per_usd"] * a2["call_equal"]["tokens_per_usd"]),
        "basis": "geometric mean of the dollar-equal and call-equal supervisor allocations",
    }
    a2["geometric_mean_of_bounds"] = math.sqrt(a2["low"]["flops_per_usd"] * a2["high"]["flops_per_usd"])
    a2_usd = REPORTED["A2"]["total_usd"] * SCORED_HOURS / RUN_HOURS
    a2_fpd = a2["central"]["flops_per_usd"]
    out["A2"] = {
        "model_mix": "Claude Sonnet 4 sub-agents; supervisor rotating over Sonnet 4, o3, "
                     "Opus 4, Gemini 2.5 Pro and o3-pro; triager pinned to the startup "
                     "supervisor model; Opus 4.1 and o4-mini helpers",
        "per_model_flops_per_usd": per_model,
        "used_flops_per_usd": used,
        "scenarios": a2,
        "usd_16h": REPORTED["A2"]["total_usd"],
        "usd_10h": a2_usd,
        "flops_central": a2_usd * a2_fpd,
        "flops_low": a2_usd * a2["low"]["flops_per_usd"],
        "flops_high": a2_usd * a2["high"]["flops_per_usd"],
        "tokens_central": a2_usd * a2["central"]["tokens_per_usd"],
        "implied_mean_coefficient": a2_fpd / a2["central"]["tokens_per_usd"],
        "flops_16h_central": REPORTED["A2"]["total_usd"] * a2_fpd,
    }

    # ---- omitted cached-context attention, per DECISIONS.md ----------------------
    out["attention_scenario"] = {
        "recipe": "4 * L * d_model * N_context per processed position, as a multiple of the recorded value",
        "bracket": "L 64-96, d_model 8192-12288 for a 100B-active frontier model, the bracket used in research/apex-agents.md",
        "multiples": {
            f"N={n}": {
                "low": attention_multiple(64, 8192, n, 2.0e11),
                "mid": attention_multiple(80, 10240, n, 2.0e11),
                "high": attention_multiple(96, 12288, n, 2.0e11),
            } for n in (20_000, 50_000, 100_000, 185_000)
        },
    }

    # ---- throughput plausibility -------------------------------------------------
    out["throughput_check"] = {}
    for cfg, counted in (("A1", out["A1"]["tokens_central"]),
                         ("A2", out["A2"]["tokens_central"])):
        out["throughput_check"][cfg] = {
            "counted_tokens": counted,
            "output_tokens_at_R60": counted / 61.0,
            "output_tokens_per_second_over_10h": counted / 61.0 / (SCORED_HOURS * 3600),
            "per_stream_at_3.82_concurrent": counted / 61.0 / (SCORED_HOURS * 3600) / 3.82,
        }

    # ---- performance, from the extracted Table 1 ---------------------------------
    if args.table1 and args.table1.exists():
        with args.table1.open(newline="", encoding="utf-8") as fh:
            t1 = {r["id"]: r for r in csv.DictReader(fh)}
        humans = sorted(float(t1[f"P{i}"]["total_score"]) for i in range(1, 11))
        mean = sum(humans) / len(humans)
        var = sum((x - mean) ** 2 for x in humans) / (len(humans) - 1)
        sd = math.sqrt(var)
        se = sd / math.sqrt(len(humans))
        median = (humans[4] + humans[5]) / 2
        valid = [float(t1[f"P{i}"]["valid_pct"]) for i in range(1, 11)]
        perf = {"human_scores_sorted": humans, "human_mean": mean, "human_median": median,
                "human_sd": sd, "human_se_of_mean": se,
                "human_valid_pct_mean": sum(valid) / len(valid)}
        for cfg in ("A1", "A2", "CO", "CS", "CG"):
            score = float(t1[cfg]["total_score"])
            ratio = score / mean
            ratio_se = score * se / mean ** 2
            perf[cfg] = {
                "total_score": score,
                "valid_pct": float(t1[cfg]["valid_pct"]),
                "ratio_to_human_mean": ratio,
                "ratio_to_human_median": score / median,
                "se_of_ratio": ratio_se,
                "standard_errors_from_half_guide": (ratio - 0.5) / ratio_se,
                "humans_beaten": sum(1 for h in humans if h < score),
            }
        out["performance"] = perf

    args.out.write_text(json.dumps(out, indent=1, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "A1_flops": out["A1"]["flops_central"], "A1_band": [out["A1"]["flops_low"], out["A1"]["flops_high"]],
        "A1_tokens": out["A1"]["tokens_central"], "A1_usd_10h": out["A1"]["usd_10h"],
        "A2_flops": out["A2"]["flops_central"], "A2_band": [out["A2"]["flops_low"], out["A2"]["flops_high"]],
        "A2_tokens": out["A2"]["tokens_central"], "A2_usd_10h": out["A2"]["usd_10h"],
    }, indent=1))


if __name__ == "__main__":
    main()
