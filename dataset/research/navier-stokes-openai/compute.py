#!/usr/bin/env python3
"""Compute and human-time arithmetic for the OpenAI Navier-Stokes row.

Reproduces every number quoted in research/navier-stokes-openai.md and every
numeric field of candidates/navier-stokes-openai/points.csv.

Dependencies: Python 3.8+ standard library only.

Usage:
    python3 compute.py --sources <agent-work/sources/navier-stokes-openai> --output <new-calculations.json>

--sources must be the retained source directory for this study.  The script
reads three files from it to confirm the published quantities it is built on are
still the ones on disk; it does not parse them for values, because the values
are transcribed as literals below with their provenance.  It never writes into
--sources.  --output is a path for a fresh JSON file; the retained
calculations.json is not modified.
"""

import argparse
import json
import os
import sys

# ---------------------------------------------------------------------------
# Published quantities. Provenance for each is in the research note.
# ---------------------------------------------------------------------------

# OpenAI, "On the Navier-Stokes Millennium Prize Problem", 2026-09-08.
# "In the process of resolving the Navier-Stokes problem, the agents sent 2.7
#  million messages and used approximately 130 billion output tokens."
NS_OUTPUT_TOKENS = 1.30e11
NS_MESSAGES = 2.7e6
# "Across all attempted problems, the agents sent 4.9 million messages and used
#  about 300 billion output tokens."
ALL_OUTPUT_TOKENS = 3.00e11
ALL_MESSAGES = 4.9e6
# "about 88 hours after the first agents were launched" + "an additional 17
#  hours via GPT-6 Astra"
MATH_RUN_HOURS = 88.0
FORMALIZATION_HOURS = 17.0

# Shared model coefficient, identical to the gpt-6-astra record in
# candidates/portal-astra/models.csv: 2 * 100e9 active parameters.
FLOPS_PER_TOKEN = 2.0e11
ACTIVE_PARAMS = 1.0e11
ACTIVE_PARAMS_LOW = 3.0e10
ACTIVE_PARAMS_HIGH = 3.0e11

# ---------------------------------------------------------------------------
# Donor run for the input side: Meta FAIR, "Automatic Textbook Formalization"
# (arXiv:2604.03071), Claude Opus 4.5, RepoProver multi-agent scaffold.
#
# UNITS, following research/meta-textbook.md#transfer-anchor and DECISIONS.md:
#     r = APPENDED tokens per output token, INCLUDING the agent's own prior
#         output re-entering the next prompt (all but the final turn's)
#     k = 1 + r = total processed tokens per output token, adding the output
#         generation itself
# Re-entered assistant output is a cache-creation position that is processed
# again, not a cache read, and COLUMNS excludes only cache reads.  The accepted
# Portal row does this: tokens = 5,356,638 = 3,758,297 fresh input + 1,598,341
# output, where the fresh input includes up to 1,598,341 of re-entered output.
#
# Decomposition used here:
#     r = reentered_own_output_per_output + non_output_appended_per_output
# The first term is (T-1)/T, because the output of every turn but the last
# re-enters the prefix exactly once as a counted prefill (later re-reads are
# cache reads and are excluded).  The donor's own headline uses a flat 1.0,
# which agrees to 2% at its T = 54.76 and not at the turn counts inferred here.
#
# Settled anchor (research/meta-textbook.md#transfer-anchor, final):
#     non-output appended per output  3.2
#     r central 4.2, band 3.5 to 5.3  (5.3 is the upper bound, the single
#                                      aggregate application of Appendix A)
#     k central 5.2, band 4.5 to 6.3
# The central is Appendix A's model applied per role across Table 2's eight
# roles; the band runs from the front-loaded profile at the measured fixed tool
# prefix up to the aggregate application.
# ---------------------------------------------------------------------------

META_TURNS_PER_AGENT = 54.76   # Appendix A, T, unweighted

DONOR_R_CENTRAL = 4.2          # appended per output, incl. re-entered own output
DONOR_R_LOW = 3.5
DONOR_R_HIGH = 5.3             # upper bound
DONOR_NON_OUTPUT = 3.2         # non-output appended per output token

# ---------------------------------------------------------------------------
# Bracketing decoder shapes for the omitted cached-context attention term.
# Same three shapes research/portal-astra.md uses, for cross-row consistency.
# ---------------------------------------------------------------------------

ATTENTION_SHAPES = [
    {"label": "L=64, d=8192", "layers": 64, "d_model": 8192},
    {"label": "L=80, d=10240", "layers": 80, "d_model": 10240},
    {"label": "L=96, d=12288", "layers": 96, "d_model": 12288},
]
# Average context a forwarded position sees is L/2 in a linearly growing dialog,
# with L the dialog length this row's own closure table infers (466k-633k).
CONTEXT_LOW = 2.33e5      # high scenario's 466,000-token dialog
CONTEXT_CENTRAL = 2.475e5 # central scenario's 495,000-token dialog
CONTEXT_HIGH = 3.165e5    # low scenario's 633,000-token dialog

# ---------------------------------------------------------------------------
# Human-time scenario components, in active hours. Bases are in the note.
#
# The Lean component is anchored on the batch's two retained formalization
# anchors rather than on a bare person-weeks-per-page judgment:
#   - Odd Order Theorem: ~160 lines of formal proof per page of source
#     mathematics (agent-work/sources/meta-textbook/human-formalization-anchors.md)
#   - Imperial FLT, Lean 4 era: 5.88 realized lines per active hour, band 4.90 to
#     7.35, that is 11,765 lines per all-in person-year over a 2,000-hour
#     person-year (research/flt-anthropic.md, its Revision 6)
# 166 pages x 160 lines / 5.88 lines per hour = 4,515 hours at the anchored
# rate, which is then multiplied by an explicit hard-analysis penalty.  The
# penalty is bracketed by 1x (the anchored rate holds) and the artifact's own
# 16.2x line ratio (429,279 lines / 166 pages against Odd Order's 160).
# ---------------------------------------------------------------------------

# DECISIONS.md, "Person-years and active hours" (Damon, 2026-09-13): one person-year
# is 2,000 active hours, and less-than-full-time engagement on the task is a stated
# on-task fraction, never a lower hours-per-year figure.
HOURS_PER_PERSON_YEAR = 2000.0
ON_TASK_FRACTION = 0.5              # share of a full-time year an expert puts on this problem
PAPER_PAGES = 166
LINES_PER_PAGE_ODD_ORDER = 160.0    # Odd Order Theorem anchor
# Imperial FLT realized rate, from research/flt-anthropic.md Revision 6:
# 11,765 lines per all-in person-year over a 2,000-hour person-year, after the
# staffing correction to 1.5-2 funded FTE that superseded the old 6,960 numerator.
# The 3.87 and 3.48 figures are both superseded; 3.48 in particular pairs the old
# numerator with the new denominator and must not be used.
LINES_PER_ACTIVE_HOUR = {"fast": 7.353375, "central": 5.8827, "slow": 4.90225}
WRITEUP_HOURS = 3000.0              # the 166-page paper, identical in every scenario

HUMAN_SCENARIOS = {
    "low": {
        "analytic_experts": 3, "analytic_years": 3,
        "hard_analysis_multiplier": 2.0, "lean_rate": "fast",
    },
    "central": {
        "analytic_experts": 5, "analytic_years": 13,
        "hard_analysis_multiplier": 5.0, "lean_rate": "central",
    },
    "high": {
        "analytic_experts": 20, "analytic_years": 20,
        "hard_analysis_multiplier": 10.0, "lean_rate": "slow",
    },
}


def donor_anchor():
    """The settled Meta anchor, quoted rather than re-derived.

    research/meta-textbook.md#transfer-anchor owns this derivation; this row
    uses it only as a labelled reference scenario and builds its own r from run
    structure.  Recorded here so the note and the scenario table cannot drift
    from the donor note.
    """
    return {
        "source": "research/meta-textbook.md#transfer-anchor",
        "non_output_appended_per_output": DONOR_NON_OUTPUT,
        "r_appended_per_output": DONOR_R_CENTRAL,
        "r_band": [DONOR_R_LOW, DONOR_R_HIGH],
        "k_total_per_output": 1.0 + DONOR_R_CENTRAL,
        "k_band": [1.0 + DONOR_R_LOW, 1.0 + DONOR_R_HIGH],
        "turns_per_agent_T": META_TURNS_PER_AGENT,
        "basis": ("Appendix A's equal-chunk model applied per role over Table 2's eight "
                  "roles; band from the front-loaded profile at the measured tool prefix "
                  "up to the single aggregate application, which is the upper bound"),
        "note": ("r already includes re-entered own output, so total processed is 1 + r. "
                 "The donor's headline charges every output token one re-entry; the exact "
                 "(T-1)/T form agrees to 2% at its T = 54.76 and differs by 18% at this "
                 "row's inferred T = 5.4, which is why this row carries the exact form."),
    }


# ---------------------------------------------------------------------------
# Dialog length implied for the OpenAI run.
# ---------------------------------------------------------------------------

OUTPUT_PER_MESSAGE = NS_OUTPUT_TOKENS / NS_MESSAGES   # 48,148
CONCURRENT_AGENTS = 1.0e4          # "on the order of 10,000 concurrent agents"
CONTEXT_CAPS = [2.0e5, 1.0e6]      # RepoProver-like cap, and a generous 2026 cap


def dialog_length():
    """Turn count and agent-instance count the published figures force.

    A dialog appending m tokens per turn over T turns reaches L = T*m, where
    m = output per turn * (1 + r_external).  Note that the generation pass and
    the re-entry pass do not lengthen the dialog, so the closure check below
    uses (1 + r_external), not k.
    """
    out = {"output_per_message": OUTPUT_PER_MESSAGE, "meta_T": META_TURNS_PER_AGENT}
    t = NS_MESSAGES / CONCURRENT_AGENTS
    out["if_10k_were_the_population"] = {
        "turns_per_agent": t,
        "dialog_length_at_zero_input": t * OUTPUT_PER_MESSAGE,
        "verdict": "impossible; exceeds any deployed context window counting output alone",
    }
    rows = []
    for cap in CONTEXT_CAPS:
        for r_ext in (0.0, 0.9, DONOR_NON_OUTPUT):
            t_max = cap / (OUTPUT_PER_MESSAGE * (1.0 + r_ext))
            rows.append({
                "context_cap": cap,
                "r_external": r_ext,
                "max_turns_per_agent": t_max,
                "min_agent_instances": NS_MESSAGES / t_max,
                "instance_lifetime_hours_at_10k_concurrent":
                    CONCURRENT_AGENTS * MATH_RUN_HOURS / (NS_MESSAGES / t_max),
            })
    out["bounded_by_context"] = rows
    return out


# ---------------------------------------------------------------------------
# External input per output token, from named components.
# ---------------------------------------------------------------------------

R_COMPONENTS = {
    "low": {
        "instances": 2.6e5, "seed_tokens": 5.0e4,
        "message_body_tokens": 5.0e3, "fanout": 1.0,
        "tool_tokens_per_turn": 3.0e3,
    },
    "central": {
        "instances": 5.0e5, "seed_tokens": 1.0e5,
        "message_body_tokens": 5.0e3, "fanout": 3.0,
        "tool_tokens_per_turn": 1.0e4,
    },
    "high": {
        "instances": 1.3e6, "seed_tokens": 2.0e5,
        "message_body_tokens": 5.0e3, "fanout": 10.0,
        "tool_tokens_per_turn": 3.0e4,
    },
}


def r_build():
    """r = (T-1)/T re-entered own output + external input, per output token."""
    out = {}
    for name, c in R_COMPONENTS.items():
        seeding = c["instances"] * c["seed_tokens"]
        peers = NS_MESSAGES * c["message_body_tokens"] * c["fanout"]
        tools = NS_MESSAGES * c["tool_tokens_per_turn"]
        external = seeding + peers + tools
        r_external = external / NS_OUTPUT_TOKENS
        turns = NS_MESSAGES / c["instances"]
        reentered = (turns - 1.0) / turns
        r = reentered + r_external
        out[name] = {
            "instances": c["instances"],
            "seeding_tokens": seeding,
            "seeding_per_output": seeding / NS_OUTPUT_TOKENS,
            "peer_message_tokens": peers,
            "peer_per_output": peers / NS_OUTPUT_TOKENS,
            "tool_result_tokens": tools,
            "tool_per_output": tools / NS_OUTPUT_TOKENS,
            "external_input_tokens": external,
            "r_external": r_external,
            "implied_turns_per_agent": turns,
            "reentered_own_output_per_output": reentered,
            "r_appended_per_output": r,
            "k": 1.0 + r,
            "implied_dialog_length": turns * OUTPUT_PER_MESSAGE * (1.0 + r_external),
            "implied_instance_lifetime_hours":
                CONCURRENT_AGENTS * MATH_RUN_HOURS / c["instances"],
        }
    return out


def compute_scenarios(rb):
    """Total processed tokens and FLOPs. k = 1 + r throughout."""
    rows = [
        ("floor_generation_only", 0.0,
         "DECISIONS.md-mandated floor: the published output count alone, r = 0."),
        ("server_side_kv_retention", rb["central"]["r_external"],
         "Own output never re-prefilled because the harness keeps KV state across turns; "
         "external input only. The value this row carried at revision 1."),
        ("low", rb["low"]["r_appended_per_output"],
         "Light seeding, no fan-out, small tool results, longest dialogs."),
        ("central", rb["central"]["r_appended_per_output"],
         "Seeding, peer messages at fan-out 3, tool results, plus (T-1)/T re-entered output."),
        ("high", rb["high"]["r_appended_per_output"],
         "Heavy seeding, fan-out 10, large tool results, shortest dialogs."),
        ("donor_transfer_unchanged", DONOR_R_CENTRAL,
         "Meta's settled anchor transferred with no adjustment for turn shape."),
    ]
    out = []
    for name, r, basis in rows:
        k = 1.0 + r
        tokens = NS_OUTPUT_TOKENS * k
        out.append({
            "scenario": name, "r_appended_per_output": r, "k": k, "tokens": tokens,
            "flops": tokens * FLOPS_PER_TOKEN, "basis": basis,
        })
    return out


def no_cache_scenario(rb):
    """What a harness with no prompt caching would have processed.

    Every turn re-prefills the whole prefix, so input positions are
    m*T(T+1)/2 per agent with m = output_per_turn * (1 + r_external), and
    generation is charged once more on top.
    """
    c = rb["central"]
    rows = []
    for t in (3.0, c["implied_turns_per_agent"], 10.0, 30.0):
        k = (1.0 + c["r_external"]) * (t + 1.0) / 2.0 + 1.0
        tokens = NS_OUTPUT_TOKENS * k
        rows.append({
            "turns_per_agent": t,
            "k": k,
            "tokens": tokens,
            "flops": tokens * FLOPS_PER_TOKEN,
        })
    return rows


def attention_scenarios(central_tokens, central_flops):
    """Cached-context attention omitted by the 2*active_parameters convention.

    Per appended position attending over N context positions, the QK and
    attention-value products cost 4 * layers * d_model * N, counting a multiply
    and an add as two operations.  This is the recipe
    dataset/research/ruler/ruler.md uses and research/portal-astra.md reuses.
    """
    rows = []
    for shape in ATTENTION_SHAPES:
        four_ld = 4.0 * shape["layers"] * shape["d_model"]
        for label, ctx in (("low", CONTEXT_LOW), ("central", CONTEXT_CENTRAL),
                           ("high", CONTEXT_HIGH)):
            per_position = four_ld * ctx
            total = per_position * central_tokens
            rows.append({
                "shape": shape["label"],
                "context_scenario": label,
                "context_positions": ctx,
                "four_L_d": four_ld,
                "flops_per_position": per_position,
                "attention_flops": total,
                "ratio_to_central_compute": total / central_flops,
            })
    return rows


def human_time():
    base = {k: PAPER_PAGES * LINES_PER_PAGE_ODD_ORDER / v
            for k, v in LINES_PER_ACTIVE_HOUR.items()}
    out = {"_hours_per_person_year": HOURS_PER_PERSON_YEAR,
           "_on_task_fraction": ON_TASK_FRACTION,
           "_lines_per_active_hour": LINES_PER_ACTIVE_HOUR,
           "_anchored_lean_hours_before_multiplier": base,
           "_lean_rate_note": ("the Lean component is literal active hours: a lines-per-active-hour "
                               "rate is a per-hour rate, so no on-task fraction applies to it. "
                               "CURRENT: 5.88 lines per active hour, band 4.90 to 7.35, the "
                               "Imperial FLT realized rate of 11,765 lines per all-in person-year "
                               "over a 2,000-hour person-year, after that row's staffing "
                               "correction to 1.5-2 funded FTE (research/flt-anthropic.md "
                               "Revision 6). DEAD, do not reuse: 3.87, which carried the old "
                               "6,960-lines numerator on an 1,800-hour person-year; and 3.48, "
                               "which paired that superseded numerator with the 2,000-hour "
                               "denominator. This row used each in turn before adopting 5.88."),
           "_artifact_lines_per_page": 429279.0 / PAPER_PAGES,
           "_artifact_ratio_to_odd_order": (429279.0 / PAPER_PAGES) / LINES_PER_PAGE_ODD_ORDER}
    for name, sc in HUMAN_SCENARIOS.items():
        discovery = (sc["analytic_experts"] * sc["analytic_years"]
                     * HOURS_PER_PERSON_YEAR * ON_TASK_FRACTION)
        analytic = discovery + WRITEUP_HOURS
        lean = base[sc["lean_rate"]] * sc["hard_analysis_multiplier"]
        total_hours = analytic + lean
        out[name] = {
            "headcount": sc["analytic_experts"],
            "years": sc["analytic_years"],
            "on_task_fraction": ON_TASK_FRACTION,
            "discovery_hours": discovery,
            "writeup_hours": WRITEUP_HOURS,
            "analytic_hours": analytic,
            "lean_rate_name": sc["lean_rate"],
            "lines_per_active_hour": LINES_PER_ACTIVE_HOUR[sc["lean_rate"]],
            "anchored_lean_hours": base[sc["lean_rate"]],
            "hard_analysis_multiplier": sc["hard_analysis_multiplier"],
            "lean_formalization_hours": lean,
            "total_hours": total_hours,
            "total_seconds": total_hours * 3600.0,
            "person_years_at_2000h": total_hours / HOURS_PER_PERSON_YEAR,
        }
    return out


def codex_helper_bound():
    """Bounding estimate for the Codex consolidation passes.

    COLUMNS requires missing helper contributions to be estimated from available
    evidence.  Codex consolidated insights across agent groups between rounds.
    Neither the round count nor the digest size is published, so this is a
    structural estimate with a stated conservative variant, not a measurement.
    Coefficient: the primary model's, as COLUMNS permits.
    """
    rounds = 10.0             # "after some time we cross-pollinated"; 88-hour effort
    groups = 10.0             # A/B/C/D variants, groups of varying size
    digest_tokens = 5.0e5     # one agent-dialog-sized digest per group, from this row's geometry
    out_per_consolidation = 1.0e4
    central_in = rounds * groups * digest_tokens
    central_out = rounds * groups * out_per_consolidation
    central = central_in + central_out
    conservative = 10.0 * 100.0 * digest_tokens      # 10 rounds x 100 groups
    # What Codex would have to process to matter at the 10% level:
    threshold = 0.10 * NS_OUTPUT_TOKENS * 2.7187
    return {
        "rounds_assumed": rounds,
        "groups_assumed": groups,
        "digest_tokens_per_group": digest_tokens,
        "central_tokens": central,
        "central_flops": central * FLOPS_PER_TOKEN,
        "conservative_tokens": conservative,
        "conservative_flops": conservative * FLOPS_PER_TOKEN,
        "tokens_needed_to_reach_10pct_of_row": threshold,
        "group_round_consolidations_needed_for_that": threshold / digest_tokens,
    }


def formalization_share():
    """Is the 17-hour GPT-6 Astra Lean run separable, and does it matter?

    Upper bound on its output: the retained NS Lean text, inflated by an
    attempt-to-accepted ratio, at roughly 3.5 characters per token.
    """
    ns_lean_bytes = 22829692  # agent-work/sources/navier-stokes-openai/lean-repo-measurements.txt
    chars_per_token = 3.5
    retained_tokens = ns_lean_bytes / chars_per_token
    out = {"retained_ns_lean_tokens": retained_tokens}
    for ratio in (10, 100):
        tok = retained_tokens * ratio
        out["attempts_x%d" % ratio] = {
            "output_tokens": tok,
            "share_of_published_130e9": tok / NS_OUTPUT_TOKENS,
        }
    return out


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--sources", required=True,
                   help="retained source directory, agent-work/sources/navier-stokes-openai")
    p.add_argument("--output", required=True, help="path for a fresh JSON file")
    args = p.parse_args(argv)

    required = ["openai-post.txt", "lean-repo-measurements.txt",
                "meta-textbook-caching-appendix.txt"]
    missing = [f for f in required
               if not os.path.isfile(os.path.join(args.sources, f))]
    if missing:
        sys.stderr.write("missing retained sources in %s: %s\n"
                         % (args.sources, ", ".join(missing)))
        return 2

    donor = donor_anchor()
    rb = r_build()
    scen = compute_scenarios(rb)
    central = [x for x in scen if x["scenario"] == "central"][0]
    per_human_second = central["flops"] / human_time()["central"]["total_seconds"]

    result = {
        "point_id": "reas-navier-stokes-openai",
        "units": {
            "r": "appended input tokens per output token",
            "k": "1 + r; total processed token positions per output token",
            "note": "params_tokens counts fresh input, cache creation and output; cache reads excluded",
        },
        "published_quantities": {
            "ns_output_tokens": NS_OUTPUT_TOKENS,
            "ns_messages": NS_MESSAGES,
            "all_problems_output_tokens": ALL_OUTPUT_TOKENS,
            "all_problems_messages": ALL_MESSAGES,
            "math_run_hours": MATH_RUN_HOURS,
            "formalization_hours": FORMALIZATION_HOURS,
            "total_wall_clock_hours": MATH_RUN_HOURS + FORMALIZATION_HOURS,
            "output_tokens_per_message": OUTPUT_PER_MESSAGE,
            "ns_share_of_all_problem_output": NS_OUTPUT_TOKENS / ALL_OUTPUT_TOKENS,
        },
        "model_coefficient": {
            "flops_per_token": FLOPS_PER_TOKEN,
            "active_parameters": ACTIVE_PARAMS,
            "basis": "identical to the gpt-6-astra record in the folder root models.csv",
        },
        "donor_anchor": donor,
        "dialog_length_inference": dialog_length(),
        "r_components": rb,
        "input_side_scenarios": scen,
        "no_cache_gross_scenarios": no_cache_scenario(rb),
        "parameter_sensitivity": {
            "active_30e9": central["tokens"] * 2.0 * ACTIVE_PARAMS_LOW,
            "active_100e9_central": central["flops"],
            "active_300e9": central["tokens"] * 2.0 * ACTIVE_PARAMS_HIGH,
        },
        "recurrent_depth_sensitivity": {
            "two_passes": central["flops"] * 2.0,
            "four_passes": central["flops"] * 4.0,
        },
        "cached_context_attention": attention_scenarios(central["tokens"],
                                                        central["flops"]),
        "compute_per_human_second": per_human_second,
        "formalization_share": formalization_share(),
        "codex_helper_bound": codex_helper_bound(),
        "human_time_scenarios": human_time(),
        "csv_values": {
            "compute_flops": central["flops"],
            "tokens": central["tokens"],
            "human_time_seconds": human_time()["central"]["total_seconds"],
            "ai_attempts": 1,
        },
    }

    with open(args.output, "w") as fh:
        json.dump(result, fh, indent=2, sort_keys=False)
        fh.write("\n")
    print("wrote %s" % args.output)
    print("  r central     = %.4f  (k = %.4f)" % (central["r_appended_per_output"], central["k"]))
    print("  compute_flops = %.4e" % result["csv_values"]["compute_flops"])
    print("  tokens        = %.4e" % result["csv_values"]["tokens"])
    print("  human_time    = %.4e s" % result["csv_values"]["human_time_seconds"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
