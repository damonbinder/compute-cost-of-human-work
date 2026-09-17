#!/usr/bin/env python3
"""Invert the reported API cost of the GPT-6 Astra Factorio run into processed
token positions and FLOPs.

The run published no token counters. The only compute evidence is the operator's
statement that the logs imply roughly $4,500 of API spend. This script converts
that dollar figure into billed token units using OpenAI's list prices at the run
date and the structure of the one contemporaneous run of the same model that did
publish counters (the cozyblaze Portal run).

Two different quantities can be transferred from that donor, and they disagree by
a factor of about 2.2:

  cost branch     transfer the donor's cache-read amplification alpha, that is
                  its dollars per billed unit;
  cadence branch  transfer the donor's mean cached prefix and its seconds per
                  call, and let alpha fall out.

The central value is the geometric mean of the two, reported as the inversion at
the single alpha that reproduces it so that tokens, positions and FLOPs stay
internally consistent.

Following the accepted `game-portal-gpt6astra` row, the donor's image share of
billed units is transferred too: `tokens` is the text remainder and image patch
positions are charged in `compute_flops` at one position per patch.

Standard library only. Explicit input and output paths; nothing is modified in
place. Usage:

    python3 research/factorio-astra/compute_factorio_astra.py \
        --portal-summary      agent-work/sources/portal-astra/summary.json \
        --portal-calculations research/portal-astra/calculations.json \
        --prices              agent-work/sources/factorio-astra/openai-list-prices-2026-09-13.json \
        --hltb                agent-work/sources/factorio-astra/howlongtobeat-factorio-17455.json \
        --out                 research/factorio-astra/calculations.json
"""

import argparse
import json
import math


# ---------------------------------------------------------------------------
# Facts about the Factorio run, all from agent-work/sources/factorio-astra/run-facts.json.
# ---------------------------------------------------------------------------
FACTORIO_COST_USD = 4500.0          # operator statement, 2026-09-11
FACTORIO_GOAL_CLOCK_S = 4 * 86400 + 11 * 3600   # "4 days 11 hours"; a lower bound
FACTORIO_INGAME_S = 43 * 3600 + 40 * 60 + 46    # victory screen "43:40:46"
SCREENSHOT_W, SCREENSHOT_H = 1280, 800          # debug overlay in every screenshot

# Wall-clock scenarios. The operator's 4 d 11 h equals the interval between her
# own two posts (2026-09-06 21:34:31Z to 2026-09-11 09:32:03Z is 4 d 11 h 57 m
# 32 s) and the opening post's screenshots already show a mid-game base, so the
# run started earlier. Astra's 2026-09-03 release caps the elapsed time at about
# 725,000 s.
WALL_CLOCK_SCENARIOS_S = [385200.0, 430000.0, 470000.0, 518400.0]

# Shared dataset model coefficients (models.csv), 2 * active parameters.
# Astra moved from 100B to 300B active under the 2026-09-13 parameter-prior
# ruling in collection-work/DECISIONS.md; its sensitivity range is 100-600B.
# Luna is unchanged at the nano-tier 8B prior, range 3-24B.
ASTRA_ACTIVE_PARAMS = 300e9
LUNA_ACTIVE_PARAMS = 8e9
ASTRA_PARAM_SCENARIOS = [(100e9, "100B"), (600e9, "600B")]
LUNA_PARAM_SCENARIOS = [(3e9, "3B"), (24e9, "24B")]

# Judgment inputs, argued in research/factorio-astra.md.
LUNA_COST_SHARE_CENTRAL = 0.02
LUNA_COST_SHARE_RANGE = (0.0, 0.10)
ALPHA_SCENARIOS = [0.0, 13.64, 25.0, 100.0, 200.0]


def billed_unit_price(alpha, beta, p_cached, p_input, p_output):
    """USD per million billed units (fresh input + cache creation + output).

    alpha = cache-read tokens per billed unit; beta = output share of billed
    units. Cache-creation tokens are zero in the calibration run and are held at
    zero here; the alternative is priced as a separate scenario.
    """
    return alpha * p_cached + (1.0 - beta) * p_input + beta * p_output


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--portal-summary", required=True)
    ap.add_argument("--portal-calculations", required=True)
    ap.add_argument("--prices", required=True)
    ap.add_argument("--hltb", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    portal = json.load(open(args.portal_summary))
    portal_calc = json.load(open(args.portal_calculations))
    prices = json.load(open(args.prices))
    hltb = json.load(open(args.hltb))

    astra_p = prices["models"]["gpt-6-astra"]
    luna_p = prices["models"]["gpt-5.6-luna"]

    # -- 1. Calibration on the Portal run ---------------------------------
    u = portal["last_reported_thread_token_usage"]
    inp, cached = u["input_tokens"], u["cached_input_tokens"]
    cwrite, out = u["cache_write_input_tokens"], u["output_tokens"]
    fresh = inp - cached
    billed = fresh + cwrite + out            # dataset params_tokens convention
    alpha = cached / billed                  # cache reads per billed unit
    beta = out / billed                      # output share of billed units
    calls = 3337                             # overlay TOOL CALLS at completion
    donor_seconds_per_call = portal["elapsed_to_completion_seconds"] / calls
    donor_cached_prefix_per_call = cached / calls
    donor_billed_per_call = billed / calls

    modelled_cost = (
        cached * astra_p["cached_input"]
        + fresh * astra_p["input"]
        + cwrite * astra_p["cache_write"]
        + out * astra_p["output"]
    ) / 1e6
    overlay_cost = 571.33                    # livestream overlay, EST. API COST

    # Image share of the donor's billed units, from the accepted Portal row.
    d = portal_calc["derived"]
    image_share = d["image_billing_units"] / d["charged_units"]
    patches_per_billable_unit = d["image_backbone_positions"] / d["image_billing_units"]
    # Backbone positions per billed unit once the image share is separated.
    position_factor = (1.0 - image_share) + image_share * patches_per_billable_unit

    calibration = {
        "donor_run": "cozyblaze Portal agent, gpt-6-astra at reasoning_effort max, 2026-09-04/05",
        "input_tokens": inp,
        "cached_input_tokens": cached,
        "cache_write_input_tokens": cwrite,
        "output_tokens": out,
        "fresh_input_tokens": fresh,
        "billed_units": billed,
        "alpha_cache_reads_per_billed_unit": alpha,
        "beta_output_share_of_billed_units": beta,
        "modelled_cost_usd": modelled_cost,
        "overlay_reported_cost_usd": overlay_cost,
        "cost_agreement_ratio": modelled_cost / overlay_cost,
        "elapsed_seconds": portal["elapsed_to_completion_seconds"],
        "tool_calls_from_summary": sum(portal["tool_methods_in_exec"].values()),
        "tool_calls_from_overlay": calls,
        "billed_units_per_call": donor_billed_per_call,
        "cached_prefix_per_call": donor_cached_prefix_per_call,
        "mean_prefix_tokens_per_call": inp / calls,
        "seconds_per_call": donor_seconds_per_call,
        "image_billing_units": d["image_billing_units"],
        "image_backbone_positions": d["image_backbone_positions"],
        "image_share_of_billed_units": image_share,
        "patch_positions_per_billable_image_unit": patches_per_billable_unit,
        "backbone_positions_per_billed_unit": position_factor,
        "implied_compaction_floor_tokens": 2 * (inp / calls) - 258400.0,
    }

    # -- 2. The two structural transfers ----------------------------------
    def invert_at_alpha(alpha_a, luna_share=LUNA_COST_SHARE_CENTRAL,
                        alpha_l=None, pa=None, pl=None):
        """Billed units for each model at a given cache-read amplification."""
        pa = pa or astra_p
        pl = pl or luna_p
        a_price = billed_unit_price(alpha_a, beta, pa["cached_input"],
                                    pa["input"], pa["output"])
        l_price = billed_unit_price(alpha_l if alpha_l is not None else alpha_a,
                                    beta, pl["cached_input"], pl["input"],
                                    pl["output"])
        a_u = FACTORIO_COST_USD * (1 - luna_share) / a_price * 1e6
        l_u = FACTORIO_COST_USD * luna_share / l_price * 1e6
        return a_u, l_u, a_price, l_price

    def bundle(a_u, l_u, astra_params=ASTRA_ACTIVE_PARAMS,
               luna_params=LUNA_ACTIVE_PARAMS, passes=1, pos_factor=None):
        """Text tokens, patch positions and FLOPs from billed units."""
        pf = position_factor if pos_factor is None else pos_factor
        total_u = a_u + l_u
        text = (1.0 - image_share) * total_u
        patches = image_share * patches_per_billable_unit * total_u
        a_pos, l_pos = pf * a_u, pf * l_u
        flops = a_pos * 2 * astra_params * passes + l_pos * 2 * luna_params
        return {
            "astra_billed_units": a_u,
            "luna_billed_units": l_u,
            "total_billed_units": total_u,
            "text_tokens": text,
            "image_patch_positions": patches,
            "astra_backbone_positions": a_pos,
            "luna_backbone_positions": l_pos,
            "flops": flops,
        }

    def seconds_per_call_at_pinned_prefix(alpha_a, astra_units):
        """Wall seconds per Astra call implied by an alpha, holding the donor's
        mean cached prefix. The turn size is prefix / alpha, so the call count is
        the billed-unit total divided by it. The wall clock is a lower bound, so
        this figure is a lower bound too."""
        u_call = donor_cached_prefix_per_call / alpha_a
        return FACTORIO_GOAL_CLOCK_S / (astra_units / u_call)

    # Cost branch: carry the donor's dollars per billed unit.
    a_u, l_u, a_price, l_price = invert_at_alpha(alpha)
    cost_branch = bundle(a_u, l_u)
    cost_branch.update({
        "transfer": "donor alpha (dollars per billed unit)",
        "alpha": alpha,
        "astra_usd_per_million_billed_units": a_price,
        "luna_usd_per_million_billed_units": l_price,
        "implied_astra_calls_at_donor_turn_size": a_u / donor_billed_per_call,
        "implied_seconds_per_astra_call_at_donor_turn_size":
            FACTORIO_GOAL_CLOCK_S / (a_u / donor_billed_per_call),
        "implied_seconds_per_call_at_pinned_prefix":
            seconds_per_call_at_pinned_prefix(alpha, a_u),
    })

    def cadence_branch(wall_clock_s, seconds_per_call=None,
                       luna_share=LUNA_COST_SHARE_CENTRAL):
        """Carry the donor's mean cached prefix and seconds per call instead.

        At a pinned cached prefix P the cost of one call is
        (P + (1-beta)*u*P_in + beta*u*P_out) / 1e6 with cache reads at P_cached,
        so the turn size u follows from the budget and the call count.
        """
        spc = seconds_per_call or donor_seconds_per_call
        n = wall_clock_s / spc
        astra_cost = FACTORIO_COST_USD * (1 - luna_share)
        cost_per_call_micro = astra_cost / n * 1e6
        per_unit = ((1.0 - beta) * astra_p["input"] + beta * astra_p["output"])
        prefix_cost = donor_cached_prefix_per_call * astra_p["cached_input"]
        u_call = (cost_per_call_micro - prefix_cost) / per_unit
        a_alpha = donor_cached_prefix_per_call / u_call
        a_units = n * u_call
        _, l_units, _, l_price = invert_at_alpha(a_alpha, luna_share)
        b = bundle(a_units, l_units)
        b.update({
            "transfer": "donor cached prefix and seconds per call",
            "wall_clock_seconds": wall_clock_s,
            "seconds_per_call": spc,
            "astra_calls": n,
            "billed_units_per_call": u_call,
            "alpha": a_alpha,
            "luna_usd_per_million_billed_units": l_price,
        })
        return b

    cadence_branches = [cadence_branch(w) for w in WALL_CLOCK_SCENARIOS_S]
    cadence_branches.append(cadence_branch(FACTORIO_GOAL_CLOCK_S, seconds_per_call=20.0))
    cadence_primary = cadence_branches[0]

    # -- 3. Central: geometric mean of the two transfers ------------------
    target = math.sqrt(cost_branch["flops"] * cadence_primary["flops"])

    lo, hi = cadence_primary["alpha"], cost_branch["alpha"]
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        au, lu, _, _ = invert_at_alpha(mid)
        f = bundle(au, lu)["flops"]
        if f > target:
            lo = mid
        else:
            hi = mid
    alpha_central = 0.5 * (lo + hi)
    au, lu, a_price_c, l_price_c = invert_at_alpha(alpha_central)
    central = bundle(au, lu)
    central.update({
        "basis": "geometric mean of the cost-transfer and cadence-transfer totals, "
                 "reported as the inversion at the alpha that reproduces it",
        "alpha": alpha_central,
        "geometric_mean_target_flops": target,
        "cost_branch_flops": cost_branch["flops"],
        "cadence_branch_flops": cadence_primary["flops"],
        "luna_cost_share": LUNA_COST_SHARE_CENTRAL,
        "astra_cost_usd": FACTORIO_COST_USD * (1 - LUNA_COST_SHARE_CENTRAL),
        "luna_cost_usd": FACTORIO_COST_USD * LUNA_COST_SHARE_CENTRAL,
        "astra_usd_per_million_billed_units": a_price_c,
        "luna_usd_per_million_billed_units": l_price_c,
        "astra_flops": position_factor * au * 2 * ASTRA_ACTIVE_PARAMS,
        "luna_flops": position_factor * lu * 2 * LUNA_ACTIVE_PARAMS,
        "luna_share_of_flops": (position_factor * lu * 2 * LUNA_ACTIVE_PARAMS)
        / bundle(au, lu)["flops"],
        "implied_billed_units_per_call_at_pinned_prefix":
            donor_cached_prefix_per_call / alpha_central,
        "implied_astra_calls_at_pinned_prefix":
            au / (donor_cached_prefix_per_call / alpha_central),
        "implied_seconds_per_call_at_pinned_prefix":
            seconds_per_call_at_pinned_prefix(alpha_central, au),
    })
    total_flops = central["flops"]

    # -- 4. Scenarios ------------------------------------------------------
    scenarios = []

    def add(name, b, comment):
        scenarios.append({
            "scenario": name,
            "astra_billed_units": b["astra_billed_units"],
            "luna_billed_units": b["luna_billed_units"],
            "total_billed_units": b["total_billed_units"],
            "text_tokens": b["text_tokens"],
            "flops": b["flops"],
            "ratio_to_central": b["flops"] / total_flops,
            "comment": comment,
        })

    add("Central", central,
        "Geometric mean of the two structural transfers; alpha = %.2f." % alpha_central)
    add("Cost transfer, alpha = %.2f" % alpha, cost_branch,
        "Carries the donor's dollars per billed unit. Implies %.1f s per Astra call "
        "at the donor's turn size, against the donor's %.1f."
        % (cost_branch["implied_seconds_per_astra_call_at_donor_turn_size"],
           donor_seconds_per_call))
    add("Cadence transfer, %.0f s wall clock" % FACTORIO_GOAL_CLOCK_S, cadence_primary,
        "Carries the donor's cached prefix and seconds per call; alpha falls out at "
        "%.2f." % cadence_primary["alpha"])
    for b in cadence_branches[1:4]:
        add("Cadence transfer, %.0f s wall clock" % b["wall_clock_seconds"], b,
            "A longer elapsed time than the operator's stated lower bound; alpha "
            "%.2f." % b["alpha"])
    add("Cadence transfer, 20 s per call", cadence_branches[4],
        "A faster loop than the donor's, as lower reasoning effort would give.")

    for a in ALPHA_SCENARIOS:
        au_, lu_, _, _ = invert_at_alpha(a)
        add("Cache-read amplification alpha = %g" % a, bundle(au_, lu_),
            "No prompt caching at all: every prefix token charged fresh." if a == 0
            else "Direct alpha sweep around the two transferred values, %.2f and "
                 "%.2f." % (cadence_primary["alpha"], alpha))

    for ls in LUNA_COST_SHARE_RANGE:
        au_, lu_, _, _ = invert_at_alpha(alpha_central, ls)
        add("Luna cost share = %.0f%%" % (100 * ls), bundle(au_, lu_),
            "Worker model's share of the $4,500.")

    au_, lu_, _, _ = invert_at_alpha(alpha_central, alpha_l=10.0)
    add("Luna worker threads short (alpha_Luna = 10)", bundle(au_, lu_),
        "A subagent with a short context buys more tokens per dollar.")

    for p, label in ASTRA_PARAM_SCENARIOS:
        au_, lu_, _, _ = invert_at_alpha(alpha_central)
        add("Astra active parameters = %s" % label,
            bundle(au_, lu_, astra_params=p),
            "The ruled sensitivity range around the 300B prior.")
    for p, label in LUNA_PARAM_SCENARIOS:
        au_, lu_, _, _ = invert_at_alpha(alpha_central)
        add("Luna active parameters = %s" % label,
            bundle(au_, lu_, luna_params=p),
            "The dataset's nano-tier scenario range.")

    lc_a = {**astra_p, "cached_input": astra_p["cached_input"] * 2,
            "input": astra_p["input"] * 2, "output": astra_p["output"] * 1.5}
    lc_l = {**luna_p, "cached_input": luna_p["cached_input"] * 2,
            "input": luna_p["input"] * 2, "output": luna_p["output"] * 1.5}
    au_, lu_, _, _ = invert_at_alpha(alpha_central, pa=lc_a, pl=lc_l)
    add("Long-context tier on every request", bundle(au_, lu_),
        "Every request above 272K input tokens: 2x input and cache rates, 1.5x output.")

    fm_a = {**astra_p, "cached_input": astra_p["cached_input"] * 2,
            "input": astra_p["input"] * 2, "output": astra_p["output"] * 2}
    fm_l = {**luna_p, "cached_input": luna_p["cached_input"] * 2,
            "input": luna_p["input"] * 2, "output": luna_p["output"] * 2}
    au_, lu_, _, _ = invert_at_alpha(alpha_central, pa=fm_a, pl=fm_l)
    add("Fast mode throughout", bundle(au_, lu_),
        "Both model pages price Fast mode at 2x the applicable rates; the donor "
        "session is recorded switching into it partway.")

    au_, lu_, _, _ = invert_at_alpha(alpha_central)
    for mult in (2, 4):
        add("Recurrent depth, %d passes per token" % mult,
            bundle(au_, lu_, passes=mult),
            "Astra is reported to reuse its layer stack; the pass count is not "
            "disclosed.")

    # Naive pricing: the operator's "$4,500 at API pricing" charging cache reads
    # at the full input rate. Rejected by the cadence cross-check.
    naive_a = {**astra_p, "cached_input": astra_p["input"]}
    naive_l = {**luna_p, "cached_input": luna_p["input"]}
    au_, lu_, ap_, _ = invert_at_alpha(alpha, pa=naive_a, pl=naive_l)
    naive = bundle(au_, lu_)
    add("Operator priced cache reads at the full input rate", naive,
        "Gives %.1f s per Astra call at the donor's turn size, against the donor's "
        "%.1f, which is why it is rejected."
        % (FACTORIO_GOAL_CLOCK_S / (au_ / donor_billed_per_call), donor_seconds_per_call))

    # Arithmetic ceiling: every dollar buys fresh input at list price.
    ceiling_units = FACTORIO_COST_USD / astra_p["input"] * 1e6
    add("Arithmetic ceiling, all spend on fresh input",
        bundle(ceiling_units, 0.0),
        "No cache reads and no output tokens. Not physical; it bounds the billed-unit "
        "total from above at standard-tier prices.")

    # No image separation, the first-submission treatment.
    au_, lu_, _, _ = invert_at_alpha(alpha_central)
    add("No image share separated", bundle(au_, lu_, pos_factor=1.0),
        "Every billed unit charged as one backbone position, as the first submission did. "
        "This is also the upper bound on the image correction: a lower image share than "
        "the donor's moves the row this way and no further.")

    # Image share on Astra's units only, the reviewer's illustrative treatment.
    au_, lu_, _, _ = invert_at_alpha(alpha_central)
    astra_only = {
        "astra_billed_units": au_,
        "luna_billed_units": lu_,
        "total_billed_units": au_ + lu_,
        "text_tokens": (1.0 - image_share) * au_ + lu_,
        "image_patch_positions": image_share * patches_per_billable_unit * au_,
        "flops": position_factor * au_ * 2 * ASTRA_ACTIVE_PARAMS
        + lu_ * 2 * LUNA_ACTIVE_PARAMS,
    }
    add("Image share on Astra's billed units only", astra_only,
        "The worker's units carried as text in full. Reproduces the review's "
        "illustrative figures at the cost-transfer alpha.")

    # -- 5. Turn-structure grid, restricted to feasible mean prefixes ------
    turn_structures = []
    for L in (calibration["mean_prefix_tokens_per_call"], 200000.0):
        for u_call in (donor_billed_per_call, 5000.0, 9367.6):
            fresh_call = (1.0 - beta) * u_call
            out_call = beta * u_call
            cached_call = L - fresh_call
            cost_call = (cached_call * astra_p["cached_input"]
                         + fresh_call * astra_p["input"]
                         + out_call * astra_p["output"]) / 1e6
            n_calls = central["astra_cost_usd"] / cost_call
            turn_structures.append({
                "mean_prefix_tokens": L,
                "billed_units_per_call": u_call,
                "implied_alpha": cached_call / u_call,
                "implied_compaction_floor_tokens": 2 * L - 258400.0,
                "cost_per_call_usd": cost_call,
                "implied_astra_calls": n_calls,
                "astra_billed_units": n_calls * u_call,
                "implied_seconds_per_call": FACTORIO_GOAL_CLOCK_S / n_calls,
            })

    # -- 6. Cached-context attention, omitted from compute_flops ----------
    # Shapes are chosen so their dense-equivalent parameter count, 12 * L * d^2
    # for a standard block, brackets the ruled 300B active prior rather than
    # being picked freely. Astra's architecture is not disclosed.
    attention = []
    astra_positions = central["astra_backbone_positions"]
    for layers, d_model in ((80, 12288), (96, 16384), (120, 18432)):
        for ctx_label, ctx in (("130k prefix (donor-measured)", 130000.0),
                               ("258k prefix (Codex window cap)", 258400.0)):
            per_pos = 4.0 * layers * d_model * ctx
            attention.append({
                "assumed_shape": "L=%d, d=%d" % (layers, d_model),
                "dense_equivalent_parameters": 12.0 * layers * d_model ** 2,
                "context_positions": ctx,
                "context_label": ctx_label,
                "four_L_d": 4.0 * layers * d_model,
                "flops_per_appended_position": per_pos,
                "attention_flops_over_astra_positions": per_pos * astra_positions,
                "ratio_to_central_total": per_pos * astra_positions / total_flops,
            })

    # -- 7. Image workload --------------------------------------------------
    patches = math.ceil(SCREENSHOT_W / 32) * math.ceil(SCREENSHOT_H / 32)
    billable = math.ceil(patches * prices["image_tokens"]["multiplier"]["gpt-6-astra"])
    images = {
        "screenshot_resolution": "%dx%d" % (SCREENSHOT_W, SCREENSHOT_H),
        "patches_per_screenshot": patches,
        "billable_units_per_screenshot": billable,
        "positions_per_screenshot": patches,
        "donor_image_share_of_billed_units": image_share,
        "transferred": True,
        "implied_screenshots_at_central": image_share * central["total_billed_units"] / billable,
        "note": "The donor's image share of billed units is transferred alongside its "
                "cache structure, following the accepted Portal row. Screenshots are "
                "1280x800 here against the donor's mostly 1280x720, so the implied "
                "screenshot count uses this run's own 1200 billable units per image.",
    }

    # -- 8. Human baseline -------------------------------------------------
    v = hltb["values"]
    human = {
        "source_url": hltb["source_url"],
        "main_story_mean_seconds": v["comp_main_avg"],
        "main_story_median_seconds": v["comp_main_med"],
        "main_story_headline_seconds": v["comp_main"],
        "main_story_rushed_seconds": v["comp_main_l"],
        "main_story_leisure_seconds": v["comp_main_h"],
        "main_story_polled": v["comp_main_count"],
        "value_used_seconds": v["comp_main_avg"],
        "ai_ingame_seconds": FACTORIO_INGAME_S,
        "ai_goal_clock_seconds_lower_bound": FACTORIO_GOAL_CLOCK_S,
        "flops_per_human_second": total_flops / v["comp_main_avg"],
        "flops_per_human_second_cost_branch": cost_branch["flops"] / v["comp_main_avg"],
        "flops_per_human_second_cadence_branch": cadence_primary["flops"] / v["comp_main_avg"],
    }

    out_obj = {
        "generated_by": "research/factorio-astra/compute_factorio_astra.py",
        "inputs": {
            "portal_summary": args.portal_summary,
            "portal_calculations": args.portal_calculations,
            "prices": args.prices,
            "hltb": args.hltb,
            "factorio_cost_usd": FACTORIO_COST_USD,
            "factorio_goal_clock_seconds_lower_bound": FACTORIO_GOAL_CLOCK_S,
            "factorio_ingame_seconds": FACTORIO_INGAME_S,
            "astra_active_parameters": ASTRA_ACTIVE_PARAMS,
            "luna_active_parameters": LUNA_ACTIVE_PARAMS,
            "luna_cost_share": LUNA_COST_SHARE_CENTRAL,
        },
        "calibration": calibration,
        "cost_branch": cost_branch,
        "cadence_branches": cadence_branches,
        "central": central,
        "scenarios": scenarios,
        "turn_structure_grid": turn_structures,
        "cached_context_attention": attention,
        "images": images,
        "human_baseline": human,
        "csv_values": {
            "compute_flops": total_flops,
            "tokens": central["text_tokens"],
            "human_time": v["comp_main_avg"],
            "human_attempts": v["comp_main_count"],
        },
    }

    with open(args.out, "w") as fh:
        json.dump(out_obj, fh, indent=1)
    print("wrote", args.out)
    print("donor alpha = %.4f  beta = %.6f  image share = %.5f  position factor = %.5f"
          % (alpha, beta, image_share, position_factor))
    print("cost branch    : alpha %6.2f  flops %.6g  (%.1f s/call implied)"
          % (cost_branch["alpha"], cost_branch["flops"],
             cost_branch["implied_seconds_per_astra_call_at_donor_turn_size"]))
    print("cadence branch : alpha %6.2f  flops %.6g  (%.0f calls, %.0f units/call)"
          % (cadence_primary["alpha"], cadence_primary["flops"],
             cadence_primary["astra_calls"], cadence_primary["billed_units_per_call"]))
    print("CENTRAL        : alpha %6.2f  flops %.6g  text tokens %.6g"
          % (alpha_central, total_flops, central["text_tokens"]))
    print("  billed units: Astra %.6g  Luna %.6g  total %.6g"
          % (central["astra_billed_units"], central["luna_billed_units"],
             central["total_billed_units"]))
    print("  patch positions %.6g   Luna share of FLOPs %.3f"
          % (central["image_patch_positions"], central["luna_share_of_flops"]))


if __name__ == "__main__":
    main()
