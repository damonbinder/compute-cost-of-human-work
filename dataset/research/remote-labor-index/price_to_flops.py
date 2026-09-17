#!/usr/bin/env python3
"""Remote Labor Index: reconstruct the published histograms and invert the pooled
API cost per AI deliverable into a token workload and a FLOP estimate.

Three jobs, in this order.

1. Histogram reconstruction. The paper publishes no table of per-deliverable API
   costs and no table of per-project human completion times; it publishes three
   rendered histograms. Their bar geometry was recovered by
   `extract_figure_bars.py` into `figure-bar-geometry.json`, including the clip
   rectangles of bins drawn with zero height. This script converts that geometry
   into integer bar counts and summary statistics and checks them against the
   statistics printed inside each panel.

2. Cost inversion, net of cache reads. The only compute evidence in the source is
   the pooled mean API cost per AI deliverable, $2.34. Prompt caching is on by
   default at the OpenAI and Google endpoints and is applied to Anthropic models
   by OpenHands, and cache reads are on the invoice while contributing nothing to
   the parameter-multiplication term COLUMNS defines. So the invoice is split
   into cache reads, cache creation and fresh input plus output, at an assumed
   cache-hit share of input, and only the non-read positions are counted.

   The hit share is not reported anywhere, so it is set the way `DECISIONS.md`
   sets the Astra Factorio cache structure: two defensible branches, the central
   reported at the single hit share that reproduces their geometric mean, so that
   positions, tokens and FLOPs stay internally consistent.

     branch A   caching absent or wholly ineffective, hit share zero. The upper
                bound on counted positions.
     branch B   idealized full-prefix reuse. For a conversation that grows
                linearly over N model calls and is cached in full at every call,
                the cache-read share of input is 1 - 2/(N+1). The lower bound.

   Branch B's N is not free: it fixes the mean and maximum context per call and
   the per-call increment, and the script reports all three so the choice can be
   checked against each endpoint's context window and against what one agent step
   plausibly adds.

3. Attention. `DECISIONS.md` requires every long-context run to carry a
   quantified scenario for the attention term the 2 x active_parameters
   convention omits, using the RULER recipe 4 * L * d_model * N_context with
   bracketing architectures. It is computed here as a multiple of the recorded
   compute value and is not added to it.

The pooled cost distribution is not broken down by agent configuration anywhere
in the source, so every per-configuration row carries the same pooled figure and
differs only through its price sheet and its parameter coefficient. That is a
transfer, and the rows say so.

Standard library only. Explicit input and output paths; nothing is modified in
place. Usage:

    python3 research/remote-labor-index/price_to_flops.py \\
        --geometry agent-work/sources/remote-labor-index/figure-bar-geometry.json \\
        --prices   agent-work/sources/remote-labor-index/api-list-prices-2025.json \\
        --inputs   research/remote-labor-index/inputs.json \\
        --models   /path/to/dataset/models.csv \\
        --out      research/remote-labor-index/calculations.json
"""

import argparse
import csv
import json
import math
from pathlib import Path


# --------------------------------------------------------------------------
# 1. Histogram reconstruction


def reconstruct_panel(panel, y_tick_step, x_major_values):
    """Turn bar geometry into integer counts and summary statistics."""
    y_ticks = panel["y_tick_positions"]
    if len(y_ticks) < 2:
        raise ValueError("need at least two y ticks to set the count scale")
    spacings = [y_ticks[i + 1] - y_ticks[i] for i in range(len(y_ticks) - 1)]
    units_per_count = (sum(spacings) / len(spacings)) / y_tick_step

    x_majors = panel["x_major_tick_positions"]
    if len(x_majors) != len(x_major_values):
        raise ValueError("major tick count does not match the supplied labels")
    decades = [
        (x_majors[i + 1] - x_majors[i])
        / (math.log10(x_major_values[i + 1]) - math.log10(x_major_values[i]))
        for i in range(len(x_majors) - 1)
    ]
    units_per_decade = sum(decades) / len(decades)
    x0_dev, x0_val = x_majors[0], x_major_values[0]

    def to_value(x_dev):
        return 10 ** (math.log10(x0_val) + (x_dev - x0_dev) / units_per_decade)

    bins = []
    max_rounding_error = 0.0
    for bar in panel["bars"]:
        raw = (bar["y_top"] - bar["y_base"]) / units_per_count
        count = round(raw)
        max_rounding_error = max(max_rounding_error, abs(raw - count))
        bins.append(
            {
                "lower": to_value(bar["x0"]),
                "upper": to_value(bar["x1"]),
                "count_raw": raw,
                "count": count,
            }
        )

    # Bins drawn with zero height carry a clip rectangle but no fill path. Locate
    # them by extrapolating the drawn bins' own width along the grid; the clip
    # coordinates are rounded to whole page units and only place a bin, so they
    # are never used to measure one.
    width = bins[0]["upper"] / bins[0]["lower"]
    drawn_lower, drawn_upper = bins[0]["lower"], bins[-1]["upper"]
    empty_below = empty_above = 0
    for clip in panel.get("bar_clip_rectangles", []):
        if clip["height"] >= 0.5 * units_per_count:
            continue
        # Which bin of the drawn grid does this clip's left edge fall on?
        index = round(math.log(to_value(clip["x0"]) / drawn_lower) / math.log(width))
        if index < 0:
            empty_below += 1
        elif index >= len(bins):
            empty_above += 1
    grid_lower = drawn_lower / width**empty_below
    grid_upper = drawn_upper * width**empty_above

    n = sum(b["count"] for b in bins)
    geo_centre_mean = (
        sum(b["count"] * math.sqrt(b["lower"] * b["upper"]) for b in bins) / n
    )
    arith_centre_mean = (
        sum(b["count"] * 0.5 * (b["lower"] + b["upper"]) for b in bins) / n
    )

    cumulative, median = 0, None
    for b in bins:
        prior, cumulative = cumulative, cumulative + b["count"]
        if median is None and cumulative >= n / 2 and b["count"]:
            frac = (n / 2 - prior) / b["count"]
            median = b["lower"] * (b["upper"] / b["lower"]) ** frac
    return {
        "description": panel["description"],
        "page": panel["page"],
        "printed_stats": panel["printed_stats"],
        "units_per_count": units_per_count,
        "units_per_decade": units_per_decade,
        "max_count_rounding_error": max_rounding_error,
        "bins": bins,
        "bins_drawn": len(bins),
        "bins_total": len(bins) + empty_below + empty_above,
        "empty_bins_below": empty_below,
        "empty_bins_above": empty_above,
        "drawn_range_lower": drawn_lower,
        "drawn_range_upper": drawn_upper,
        "grid_lower": grid_lower,
        "grid_upper": grid_upper,
        "n": n,
        "reconstructed_mean_geometric_bin_centres": geo_centre_mean,
        "reconstructed_mean_arithmetic_bin_centres": arith_centre_mean,
        "reconstructed_median": median,
    }


# --------------------------------------------------------------------------
# 2. Cost inversion, net of cache reads


def invert(cost_usd, price, input_share, hit_share, flops_per_token):
    """Positions and FLOPs implied by `cost_usd` under one cache structure.

    `input_share` is the share of billed positions that are input rather than
    output. `hit_share` is the share of those input positions served from cache.
    Cache reads are paid for and excluded from the count; cache creation is
    counted, and on Anthropic endpoints it is also charged a write premium.
    """
    write_multiplier = price["cache_write_multiplier"] if hit_share > 0 else 1.0
    per_input = (1.0 - hit_share) * write_multiplier * price["input"]
    per_input += hit_share * price["cached_input"]
    usd_per_position = (input_share * per_input + (1.0 - input_share) * price["output"]) / 1e6
    total = cost_usd / usd_per_position
    counted = total * (input_share * (1.0 - hit_share) + (1.0 - input_share))
    return {
        "hit_share": hit_share,
        "input_share": input_share,
        "usd_per_mtok": usd_per_position * 1e6,
        "billed_positions": total,
        "cache_read_positions": total * input_share * hit_share,
        "tokens": counted,
        "flops": counted * flops_per_token,
    }


def solve_hit_share(target, cost_usd, price, input_share, flops_per_token):
    """The single hit share whose counted positions equal `target`."""
    lo, hi = 0.0, 0.999999
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if invert(cost_usd, price, input_share, mid, flops_per_token)["tokens"] > target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def linear_growth_hit_share(calls):
    """Cache-read share of input for a context that grows linearly over `calls`
    model calls and is cached in full at every call: sum(S_k-1) / sum(S_k)."""
    return 1.0 - 2.0 / (calls + 1.0)


def load_model_coefficients(models_csv, wanted):
    coefficients = {}
    with open(models_csv, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["model_id"] in wanted:
                coefficients[row["model_id"]] = {
                    "model": row["model"],
                    "flops_per_token": float(row["flops_per_token"]),
                    "active_parameters": float(row["active_parameters"]),
                    "active_parameters_basis": row["active_parameters_basis"],
                }
    missing = sorted(set(wanted) - set(coefficients))
    if missing:
        raise SystemExit(f"model ids absent from {models_csv}: {', '.join(missing)}")
    return coefficients


def price_sheet(entry, tier):
    """Base or long-context list prices, with the cache-write multiplier."""
    if tier == "base":
        return {
            "input": entry["input"],
            "cached_input": entry["cached_input"],
            "output": entry["output"],
            "cache_write_multiplier": entry.get("cache_write_multiplier", 1.0),
        }
    premium = entry.get("long_context_premium")
    if not premium:
        return None
    scale = premium["input"] / entry["input"]
    return {
        "input": premium["input"],
        "cached_input": premium.get("cached_input", entry["cached_input"] * scale),
        "output": premium["output"],
        "cache_write_multiplier": entry.get("cache_write_multiplier", 1.0),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--geometry", required=True, type=Path)
    ap.add_argument("--prices", required=True, type=Path)
    ap.add_argument("--inputs", required=True, type=Path)
    ap.add_argument("--models", required=True, type=Path,
                    help="models.csv of the dataset registry; supplies flops_per_token")
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()

    geometry = json.loads(args.geometry.read_text())
    prices = json.loads(args.prices.read_text())
    cfg = json.loads(args.inputs.read_text())

    # --- histograms -------------------------------------------------------
    panels = {}
    for name, axes in cfg["histogram_axis_labels"].items():
        if name.startswith("_"):
            continue
        panels[name] = reconstruct_panel(
            geometry["panels"][name], axes["y_tick_step"], axes["x_major_values"]
        )

    cost_panel = panels["fig12_costs"]
    time_panel = panels["fig4_time"]
    project_cost_panel = panels["fig4_cost"]
    projects = cfg["projects_in_benchmark"]

    printed_time = time_panel["printed_stats"]
    checks = {
        "fig4_cost_n_over_projects": project_cost_panel["n"] / projects,
        "fig4_cost_paper_share_with_cost": cfg["paper_share_with_cost"],
        "fig4_cost_n_from_total_value_over_mean": (
            cfg["total_project_value_usd"] / project_cost_panel["printed_stats"]["mean"]
        ),
        "fig4_time_drawn_n_over_projects": time_panel["n"] / projects,
        "fig4_time_paper_share_with_time": cfg["paper_share_with_time"],
        "fig12_n_over_five_api_configurations": cost_panel["n"] / (projects * 5),
        "fig12_n_over_seven_configurations": cost_panel["n"] / (projects * 7),
    }
    for label, key in (
        ("geometric", "reconstructed_mean_geometric_bin_centres"),
        ("arithmetic", "reconstructed_mean_arithmetic_bin_centres"),
    ):
        total = time_panel[key] * time_panel["n"] + printed_time["min"] + printed_time["max"]
        checks[f"fig4_time_mean_with_both_extremes_{label}_centres"] = total / (
            time_panel["n"] + 2
        )
    checks["fig4_time_n_with_both_extremes"] = time_panel["n"] + 2
    checks["fig4_time_share_with_both_extremes"] = (time_panel["n"] + 2) / projects

    human = {
        "mean_hours": cfg["human_mean_hours"],
        "mean_seconds": cfg["human_mean_hours"] * 3600.0,
        "median_hours": cfg["human_median_hours"],
        "attempts_used": time_panel["n"] + 2,
        "attempts_basis": (
            "84% of 240 admits only 201 or 202; the bin-centre reconstruction over "
            "the 199 drawn observations plus the two printed extremes reproduces the "
            "printed mean, and a 202nd observation is excluded by it"
        ),
    }

    # --- cost inversion ---------------------------------------------------
    cost_usd = cfg["pooled_mean_cost_usd"]
    f_central = cfg["input_share_scenarios"][cfg["central_input_share"]]
    calls = cfg["branch_b_model_calls"]
    hit_b = linear_growth_hit_share(calls)
    coefficients = load_model_coefficients(
        args.models, {c["model_id"] for c in cfg["agent_configurations"]}
    )

    rows = {}
    for conf in cfg["agent_configurations"]:
        entry = prices["models"][conf["price_key"]]
        base = price_sheet(entry, "base")
        coef = coefficients[conf["model_id"]]
        fpt = coef["flops_per_token"]

        branch_a = invert(cost_usd, base, f_central, 0.0, fpt)
        branch_b = invert(cost_usd, base, f_central, hit_b, fpt)
        target = math.sqrt(branch_a["tokens"] * branch_b["tokens"])
        hit_central = solve_hit_share(target, cost_usd, base, f_central, fpt)
        central = invert(cost_usd, base, f_central, hit_central, fpt)

        # Branch B is a coupled model: its call count fixes the context profile.
        input_positions = branch_b["billed_positions"] * f_central
        mean_context = input_positions / calls
        branch_b_geometry = {
            "model_calls": calls,
            "hit_share": hit_b,
            "input_positions": input_positions,
            "mean_context_tokens": mean_context,
            "final_context_tokens": 2.0 * mean_context,
            "context_added_per_call": 2.0 * mean_context / calls,
            "context_window_tokens": conf["context_window_tokens"],
            "final_context_fits_window": 2.0 * mean_context <= conf["context_window_tokens"],
        }

        scenarios = {}
        for hit in cfg["cache_hit_scenarios"]:
            scenarios[f"cache_hit_{hit:.2f}_at_central_mix"] = invert(
                cost_usd, base, f_central, hit, fpt
            )
        for label, share in cfg["input_share_scenarios"].items():
            if label.startswith("_"):
                continue
            scenarios[f"{label}_at_central_cache"] = invert(
                cost_usd, base, share, hit_central, fpt
            )
        long_context = price_sheet(entry, "long_context")
        if long_context:
            scenarios["long_context_tier_at_central_mix_and_cache"] = invert(
                cost_usd, long_context, f_central, hit_central, fpt
            )

        low = min(scenarios.values(), key=lambda s: s["flops"])
        high = max(scenarios.values(), key=lambda s: s["flops"])

        # Cached-context attention, the term the 2N convention omits. RULER
        # recipe: 4 * L * d_model FLOPs per processed position per context token.
        attention = {}
        for shape in cfg["attention_architectures"]:
            coefficient = 4.0 * shape["layers"] * shape["d_model"]
            attention[shape["label"]] = {
                "four_l_d": coefficient,
                "multiple_of_compute_flops": {
                    f"context_{n}": coefficient * n / fpt
                    for n in cfg["attention_context_tokens"]
                },
                "multiple_at_branch_b_mean_context": coefficient * mean_context / fpt,
            }

        rows[conf["point_id"]] = {
            "agent_configuration": conf["label"],
            "scaffold": conf["scaffold"],
            "model_id": conf["model_id"],
            "model": coef["model"],
            "flops_per_token": fpt,
            "active_parameters": coef["active_parameters"],
            "active_parameters_basis": coef["active_parameters_basis"],
            "list_prices_usd_per_mtok": base,
            "pooled_mean_cost_usd": cost_usd,
            "central_input_share": f_central,
            "central_cache_hit_share": hit_central,
            "branch_a_no_cache": branch_a,
            "branch_b_full_prefix_reuse": branch_b,
            "branch_b_geometry": branch_b_geometry,
            "tokens_central": central["tokens"],
            "billed_positions_central": central["billed_positions"],
            "cache_read_positions_central": central["cache_read_positions"],
            "compute_flops_central": central["flops"],
            "flops_low": low["flops"],
            "flops_high": high["flops"],
            "flops_low_over_central": low["flops"] / central["flops"],
            "flops_high_over_central": high["flops"] / central["flops"],
            "flops_central_over_no_cache_recorded": central["flops"] / branch_a["flops"],
            "scenarios": scenarios,
            "omitted_attention_term": attention,
            "automation_successes": conf["automation_successes"],
            "automation_rate": conf["automation_successes"] / projects,
            "automation_rate_printed": conf["automation_rate_printed"],
            "elo": conf["elo"],
            "dollars_earned_usd": conf["dollars_earned_usd"],
            "human_time_seconds": human["mean_seconds"],
            "flops_per_human_second": central["flops"] / human["mean_seconds"],
        }

    result = {
        "generated_by": "research/remote-labor-index/price_to_flops.py",
        "inputs": {
            "geometry": str(args.geometry),
            "prices": str(args.prices),
            "inputs": str(args.inputs),
            "models": str(args.models),
        },
        "histogram_reconstruction": panels,
        "reconstruction_checks": checks,
        "human_time": human,
        "compute_conventions": {
            "central_input_share": f_central,
            "branch_b_model_calls": calls,
            "branch_b_hit_share": hit_b,
            "central_rule": (
                "geometric mean of branch A (no caching) and branch B (idealized "
                "full-prefix reuse), reported at the single cache-hit share that "
                "reproduces it"
            ),
            "counted_positions": (
                "fresh input plus cache creation plus output; cache reads excluded "
                "per COLUMNS, so tokens_accounting is input_cache_creation_output"
            ),
            "one_sided_terms": {
                "cache_reads": "downward, and now inside the central",
                "cached_context_attention": "upward, quantified in omitted_attention_term, not added",
                "multimedia_helper_model_flops": (
                    "upward, not quantified: gpt-image-1, openai/tts-1 and "
                    "veo-3.0-generate-preview calls in the OpenHands runs are inside "
                    "the same budget and their FLOPs are absent from compute_flops"
                ),
            },
        },
        "rows": rows,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=1) + "\n")

    print("histogram reconstruction")
    for name, panel in panels.items():
        print(
            f"  {name:12s} n={panel['n']:5d} bins={panel['bins_drawn']}/{panel['bins_total']} "
            f"grid {panel['grid_lower']:.4g}-{panel['grid_upper']:.6g} "
            f"mean(geo)={panel['reconstructed_mean_geometric_bin_centres']:9.3f} "
            f"printed={panel['printed_stats']['mean']:9.3f}"
        )
    print(f"\nbranch B: {calls} model calls, cache-read share {hit_b:.4f}")
    print("rows")
    for pid, row in rows.items():
        g = row["branch_b_geometry"]
        print(
            f"  {pid:22s} hit={row['central_cache_hit_share']:.4f} "
            f"tok={row['tokens_central']:11,.0f} flops={row['compute_flops_central']:.4e} "
            f"[{row['flops_low']:.2e}, {row['flops_high']:.2e}] "
            f"vs no-cache {row['flops_central_over_no_cache_recorded']:.3f}x  "
            f"ctx {g['mean_context_tokens']:7,.0f} (max {g['final_context_tokens']:8,.0f}, "
            f"+{g['context_added_per_call']:5,.0f}/call, fits={g['final_context_fits_window']})"
        )


if __name__ == "__main__":
    main()
