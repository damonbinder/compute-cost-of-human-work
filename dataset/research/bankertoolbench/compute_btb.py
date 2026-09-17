#!/usr/bin/env python3
"""Invert BankerToolBench per-run dollar costs into billed token units and FLOPs.

Dependencies: Python 3.9+ standard library only.

Usage (paths are explicit; run from anywhere):

  python3 compute_btb.py \
      --cells       agent-work/sources/bankertoolbench/btb-table4-harness.csv \
      --prices      research/cost/list-prices.csv \
      --donors      agent-work/sources/epoch-swebench-bins/epoch-swebench-perinstance.csv \
      --out         research/bankertoolbench/calculations.json

Method, in full, is documented in research/bankertoolbench.md. In brief:

  A BankerToolBench cell publishes a mean dollar cost per task run and a mean
  wall-clock runtime per task run, and nothing else about the workload. The row
  needs `billed units` B = fresh input + cache creation + output, the quantity
  COLUMNS.md's params_tokens rule multiplies by the model coefficient.

  Cost is linear in four token counts, so B cannot be recovered from one dollar
  figure without a structure. The structure is transferred from a measured run
  of the same model in an agentic tool-calling harness that sets the same kind
  of cache breakpoints: Epoch AI's SWE-bench Verified logs, whose per-instance
  counters are already retained in this folder.

  Two transfers of one donor are defensible and the central is their geometric
  mean, following the DECISIONS.md ruling used for the Astra Factorio row:

    Transfer A (cost)    carry the donor's dollars per billed unit, equivalently
                         its cache-read amplification alpha = cache reads / B.
    Transfer B (cadence) carry the donor's seconds per call and its cached
                         prefix per call; the cell's own runtime then fixes the
                         call count, and alpha falls out.

  The reported central is the single alpha that reproduces the geometric-mean B,
  so tokens, cache reads and FLOPs stay mutually consistent.
"""

import argparse
import csv
import json
import math
from datetime import date

# --- model records -------------------------------------------------------
# flops_per_token is 2 * active_parameters, from the Codex registry at
# ../AI Compute vs Human Time/dataset/models.csv (both IDs are shared records;
# neither is changed by research/model-priors/accepted-priors.csv).
FLOPS_PER_TOKEN = {
    "claude-opus-4-6": 2.0e11,
    "gpt-5.2-2025-12-11": 2.0e11,
}

# Provider counter convention. "anthropic": input / cache_creation / cache_read
# are additive and disjoint. "openai": the input counter already contains the
# cached portion.
COUNTER_FAMILY = {
    "claude-opus-4-6": "anthropic",
    "gpt-5.2-2025-12-11": "openai",
}

# Donor run in agent-work/sources/epoch-swebench-bins/epoch-swebench-perinstance.csv used
# for each model's cache structure, plus the alternates carried as scenarios.
DONOR = {
    "claude-opus-4-6": "agen-epoch-swebench-opus46cc",
    "gpt-5.2-2025-12-11": "agen-epoch-swebench-gpt52high",
}
ALT_DONOR = {
    "claude-opus-4-6": "agen-epoch-swebench-opus46",
    "gpt-5.2-2025-12-11": "agen-epoch-swebench-gpt54high",
}

# The price sheet in force on this date is the one applied. The paper does not
# state its run dates; 2026-04-13 is its arXiv submission date, and neither
# price sheet changes anywhere between the models' releases and that date.
PRICE_DATE = date(2026, 4, 13)

# Epoch's Inspect budget for these runs. Instances whose gross token total sits
# at the budget are truncated measurements; the uncensored-only donor structure
# is reported as a scenario.
TOKEN_BUDGET = 2_000_000
CENSOR_FRACTION = 0.99

# Bracketing architectures for the omitted cached-context attention term,
# following the recipe DECISIONS.md requires (4 * L * d_model * N_context per
# appended position) and the pair used by research/epoch-swebench-bins.md.
ATTENTION_ARCH = [("L=64, d_model=8192", 64, 8192), ("L=96, d_model=12288", 96, 12288)]


def load_prices(path, model_id, on_date):
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row["model_id"] != model_id:
                continue
            start = row["price_sheet_start"]
            end = row["price_sheet_end"]
            if start and date.fromisoformat(start) > on_date:
                continue
            if end and date.fromisoformat(end) < on_date:
                continue
            return {
                "input": float(row["input_usd_per_m"]),
                "cached": float(row["cached_input_usd_per_m"]),
                "cache_write": float(row["cache_write_usd_per_m"] or 0.0),
                "output": float(row["output_usd_per_m"]),
                "source_url": row["source_url"],
                "window_start": start,
            }
    raise SystemExit("no price sheet for %s on %s" % (model_id, on_date))


def donor_structure(path, run, family, uncensored_only=False):
    """Aggregate one Epoch run into the shares the transfer needs.

    Returns per-run totals and the derived structure. A call is half the
    transcript length, the convention research/epoch-swebench-bins.md uses for
    the same logs (system message plus assistant-and-tool pairs).
    """
    tot = dict.fromkeys(
        ["input", "output", "cache_read", "cache_write", "reasoning",
         "total", "messages", "working_s", "total_s"], 0.0)
    n = 0
    censored = 0
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row["run"] != run:
                continue
            gross = float(row["total_tokens"] or 0)
            at_budget = gross >= CENSOR_FRACTION * TOKEN_BUDGET
            if at_budget:
                censored += 1
            if uncensored_only and at_budget:
                continue
            n += 1
            for key, col in [("input", "input_tokens"), ("output", "output_tokens"),
                             ("cache_read", "cache_read_tokens"),
                             ("cache_write", "cache_write_tokens"),
                             ("reasoning", "reasoning_tokens"),
                             ("total", "total_tokens"),
                             ("messages", "message_count"),
                             ("working_s", "working_time_s"),
                             ("total_s", "total_time_s")]:
                v = row[col]
                tot[key] += float(v) if v not in ("", "None") else 0.0
    if n == 0:
        raise SystemExit("donor run %s not found in %s" % (run, path))

    if family == "anthropic":
        fresh = tot["input"]
        cache_write = tot["cache_write"]
    else:
        # OpenAI's input counter contains the cached portion; there is no
        # separate cache-write charge on automatic caching.
        fresh = tot["input"] - tot["cache_read"]
        cache_write = 0.0
    billed = fresh + cache_write + tot["output"]
    calls = tot["messages"] / 2.0
    return {
        "run": run,
        "instances": n,
        "instances_at_token_budget": censored,
        "uncensored_only": uncensored_only,
        "billed_units_per_instance": billed / n,
        "share_fresh_input": fresh / billed,
        "share_cache_write": cache_write / billed,
        "share_output": tot["output"] / billed,
        "alpha_cache_reads_per_billed_unit": tot["cache_read"] / billed,
        "calls_per_instance": calls / n,
        "cached_prefix_per_call": tot["cache_read"] / calls,
        "seconds_per_call_working": tot["working_s"] / calls,
        "seconds_per_call_total": tot["total_s"] / calls,
    }


def price_new_content(struct, prices):
    """USD per million billed units, excluding the cache-read term."""
    return (struct["share_fresh_input"] * prices["input"]
            + struct["share_cache_write"] * prices["cache_write"]
            + struct["share_output"] * prices["output"])


def transfer_cost(cost_usd, struct, prices):
    per_m = struct["alpha_cache_reads_per_billed_unit"] * prices["cached"] + price_new_content(struct, prices)
    return {
        "usd_per_million_billed_units": per_m,
        "alpha": struct["alpha_cache_reads_per_billed_unit"],
        "billed_units": cost_usd / per_m * 1e6,
    }


def transfer_cadence(cost_usd, runtime_s, struct, prices, seconds_key="seconds_per_call_working"):
    spc = struct[seconds_key]
    calls = runtime_s / spc
    usd_per_call = cost_usd / calls
    cache_cost_per_call = struct["cached_prefix_per_call"] * prices["cached"] / 1e6
    remainder = usd_per_call - cache_cost_per_call
    if remainder <= 0:
        return {"feasible": False, "calls": calls, "usd_per_call": usd_per_call,
                "cache_cost_per_call": cache_cost_per_call}
    per_m_new = price_new_content(struct, prices)
    billed_per_call = remainder / per_m_new * 1e6
    return {
        "feasible": True,
        "calls": calls,
        "seconds_per_call": spc,
        "usd_per_call": usd_per_call,
        "cache_cost_per_call": cache_cost_per_call,
        "billed_units_per_call": billed_per_call,
        "billed_units": calls * billed_per_call,
        "alpha": struct["cached_prefix_per_call"] / billed_per_call,
    }


def implied_alpha(cost_usd, billed_units, struct, prices):
    per_m = cost_usd / billed_units * 1e6
    return (per_m - price_new_content(struct, prices)) / prices["cached"]


def attention_scenarios(billed_units, calls, alpha):
    """Cached-context attention omitted by the 2 * active_parameters convention.

    4 * L * d_model * N_context FLOPs for each appended position, with
    N_context the mean cached prefix a call attends over and the appended
    positions the counted workload.
    """
    prefix = alpha * billed_units / calls
    out = {"mean_prefix_tokens": prefix, "appended_positions": billed_units, "by_architecture": {}}
    for label, layers, d_model in ATTENTION_ARCH:
        out["by_architecture"][label] = 4.0 * layers * d_model * prefix * billed_units
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cells", required=True, help="BTB Table 4 / Section B.2 extract")
    ap.add_argument("--prices", required=True, help="research/cost/list-prices.csv")
    ap.add_argument("--donors", required=True, help="Epoch SWE-bench per-instance counters")
    ap.add_argument("--out", required=True, help="JSON output path")
    args = ap.parse_args()

    with open(args.cells, newline="", encoding="utf-8") as fh:
        cells = list(csv.DictReader(fh))

    structs, prices_by_model = {}, {}
    for model_id, run in DONOR.items():
        fam = COUNTER_FAMILY[model_id]
        structs[model_id] = {
            "central": donor_structure(args.donors, run, fam, False),
            "uncensored_only": donor_structure(args.donors, run, fam, True),
            "alternate_donor": donor_structure(args.donors, ALT_DONOR[model_id], fam, False),
        }
        prices_by_model[model_id] = load_prices(args.prices, model_id, PRICE_DATE)

    results = []
    for cell in cells:
        if not cell["cost_per_run_usd"]:
            results.append({
                "model_id": cell["model_id"], "harness": cell["harness"],
                "score": float(cell["score"]), "runtime_s": float(cell["runtime_s"]),
                "built": False,
                "reason": "the paper publishes no cost for this harness, so there is no compute evidence",
            })
            continue

        model_id = cell["model_id"]
        prices = prices_by_model[model_id]
        donor = structs[model_id]["central"]
        cost = float(cell["cost_per_run_usd"])
        runtime = float(cell["runtime_s"])

        a = transfer_cost(cost, donor, prices)
        b = transfer_cadence(cost, runtime, donor, prices)
        central_b = math.sqrt(a["billed_units"] * b["billed_units"])
        central_alpha = implied_alpha(cost, central_b, donor, prices)
        # Call count at the central: the two transfers' call counts bracket it.
        calls_a = a["billed_units"] / donor["billed_units_per_instance"] * donor["calls_per_instance"]
        calls_central = math.sqrt(calls_a * b["calls"])

        flops = central_b * FLOPS_PER_TOKEN[model_id]

        scen = {}
        for name, st in [("uncensored_only_donor", structs[model_id]["uncensored_only"]),
                         ("alternate_donor", structs[model_id]["alternate_donor"])]:
            sa = transfer_cost(cost, st, prices)
            sb = transfer_cadence(cost, runtime, st, prices)
            sb_units = sb["billed_units"] if sb["feasible"] else float("nan")
            sc = math.sqrt(sa["billed_units"] * sb_units) if sb["feasible"] else float("nan")
            scen[name] = {"donor_run": st["run"], "alpha": st["alpha_cache_reads_per_billed_unit"],
                          "transfer_cost_billed_units": sa["billed_units"],
                          "transfer_cadence_billed_units": sb_units,
                          "billed_units": sc, "flops": sc * FLOPS_PER_TOKEN[model_id],
                          "ratio_to_central": sc / central_b}
        # Structural bound: the most tokens this spend can buy is the no-cache-read limit.
        no_cache = cost / price_new_content(donor, prices) * 1e6
        scen["no_cache_reads_upper_bound"] = {
            "billed_units": no_cache, "flops": no_cache * FLOPS_PER_TOKEN[model_id],
            "ratio_to_central": no_cache / central_b,
            "note": "arithmetic ceiling, not a live scenario: both harnesses set cache breakpoints",
        }
        sb_total = transfer_cadence(cost, runtime, donor, prices, "seconds_per_call_total")
        if sb_total["feasible"]:
            sc = math.sqrt(a["billed_units"] * sb_total["billed_units"])
            scen["cadence_on_donor_total_time"] = {
                "billed_units": sc, "flops": sc * FLOPS_PER_TOKEN[model_id],
                "ratio_to_central": sc / central_b}
        # Seconds per call is the cadence transfer's weakest input: BTB spends 97%
        # of its steps in sandbox tool calls and code execution, so its per-call
        # wall clock may be longer than the donor's. A slower cadence means fewer
        # calls, less cached-prefix spend per run, and a larger B.
        for mult in (0.5, 2.0):
            slowed = dict(donor)
            slowed["seconds_per_call_scaled"] = donor["seconds_per_call_working"] * mult
            sbm = transfer_cadence(cost, runtime, slowed, prices, "seconds_per_call_scaled")
            if not sbm["feasible"]:
                scen["cadence_%gx" % mult] = {"feasible": False}
                continue
            sc = math.sqrt(a["billed_units"] * sbm["billed_units"])
            scen["cadence_%gx" % mult] = {
                "seconds_per_call": slowed["seconds_per_call_scaled"],
                "billed_units": sc, "flops": sc * FLOPS_PER_TOKEN[model_id],
                "ratio_to_central": sc / central_b}

        results.append({
            "model_id": model_id, "harness": cell["harness"], "built": True,
            "score": float(cell["score"]), "score_sd_over_3_runs": float(cell["score_sd"]),
            "runtime_s": runtime, "cost_per_run_usd": cost,
            "prices_usd_per_million": {k: prices[k] for k in ("input", "cached", "cache_write", "output")},
            "price_sheet_start": prices["window_start"], "price_date": PRICE_DATE.isoformat(),
            "donor": donor,
            "usd_per_million_new_content": price_new_content(donor, prices),
            "transfer_cost": a,
            "transfer_cadence": b,
            "central_billed_units": central_b,
            "central_alpha": central_alpha,
            "central_calls_per_run": calls_central,
            "calls_from_cost_transfer": calls_a,
            "compute_flops": flops,
            "flops_per_token": FLOPS_PER_TOKEN[model_id],
            "attention_omitted": attention_scenarios(central_b, calls_central, central_alpha),
            "scenarios": scen,
        })

    out = {
        "generated_by": "research/bankertoolbench/compute_btb.py",
        "inputs": {"cells": args.cells, "prices": args.prices, "donors": args.donors},
        "price_date": PRICE_DATE.isoformat(),
        "human_time_seconds": 5 * 3600,
        "results": results,
    }
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2)
        fh.write("\n")

    for r in results:
        if not r["built"]:
            print("%-20s %-10s  not built: %s" % (r["model_id"], r["harness"], r["reason"]))
            continue
        print("%-20s %-10s  cost $%.2f  runtime %7.1fs  B_cost=%9.0f  B_cadence=%9.0f  "
              "B=%9.0f  alpha=%6.2f  calls=%6.1f  FLOPs=%.4e"
              % (r["model_id"], r["harness"], r["cost_per_run_usd"], r["runtime_s"],
                 r["transfer_cost"]["billed_units"], r["transfer_cadence"]["billed_units"],
                 r["central_billed_units"], r["central_alpha"], r["central_calls_per_run"],
                 r["compute_flops"]))


if __name__ == "__main__":
    main()
