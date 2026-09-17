#!/usr/bin/env python3
"""Compute and human-time arithmetic for reas-flt-lean-anthropic-internal.

Reproduces every number in research/flt-anthropic.md and in
candidates/flt-anthropic/points.csv.

Dependencies: Python 3.8+ standard library only.

Usage (paths are explicit; run from anywhere):

    python3 compute_flt_anthropic.py \
        --artifact  agent-work/sources/flt-anthropic/artifact-measurements.json \
        --anchors   agent-work/sources/flt-anthropic/human-anchor-measurements.json \
        --out       research/flt-anthropic/calculations.json

The two input files are retained evidence and are read, never written. The script
writes only --out.
"""

import argparse
import json
from datetime import date


# ---------------------------------------------------------------- reported facts

# Anthropic, https://www.anthropic.com/research/formalizing-fermats-last-theorem :
# "consuming about six billion output tokens from a general-purpose internal
# research model roughly comparable to Claude Fable 5.1."
OUTPUT_TOKENS = 6.0e9

# Dataset-wide frontier closed-model prior: 100B active parameters, 2 FLOPs per
# parameter per token. Same coefficient as every Opus/Fable-class record.
ACTIVE_PARAMETERS = 1.0e11
FLOPS_PER_TOKEN = 2 * ACTIVE_PARAMETERS
ACTIVE_PARAMETERS_LOW = 3.0e10
ACTIVE_PARAMETERS_HIGH = 3.0e11

# Meta FAIR "Automatic Textbook Formalization" (arXiv:2604.03071), the calibration
# donor. Reported: 83B input tokens "with multiple counting in multi-turn dialogs"
# and 561M output tokens; $430K uncached; "approximate price of $100K overall,
# $14K out of which for output tokens in both cases".
META_INPUT_GROSS = 83.0e9          # C in the paper's Appendix A: double-counted prefix
META_OUTPUT = 561.0e6
META_TURNS = 54.8                  # T, "avg. T ~ 54.8", stated in Appendix A
META_AGENTS = 30_000.0             # N, "30K Claude 4.5 Opus agents"; cancels out of the ratio
META_COST_UNCACHED = 430_000.0
META_COST_CACHED = 100_000.0
META_COST_OUTPUT = 14_000.0
OPUS_45_INPUT_PRICE_PER_TOKEN = 5.0 / 1e6   # platform.claude.com pricing table
OPUS_45_OUTPUT_PRICE_PER_TOKEN = 25.0 / 1e6

# Appendix A's own price model: c_store = 2 c_in (1-hour cache), c_hit = c_in / 10.
C_STORE_MULT = 2.00
C_HIT_MULT = 0.10


# ---------------------------------------------------------------- compute

def meta_calibration():
    """Effective (appended) token workload of the Meta FAIR donor run.

    Appendix A of arXiv:2604.03071 states the structure of the 83B figure outright.
    With N agents, T turns each, and m tokens added per turn, the gross input count is

        C = N m T(T+1)/2

    because every turn re-reads the whole prefix, while the dialogs contain only

        N L = N T m = 2C / (T + 1)

    distinct positions. N L is exactly what COLUMNS' params_tokens rule counts -- each
    position forwarded once, as fresh input or cache creation, with cache re-reads
    excluded -- and it already contains the run's output positions, since an assistant
    message becomes part of the prefix of the next turn.

    N cancels: the ratio depends only on T.
    """
    gross_ratio = META_INPUT_GROSS / META_OUTPUT
    appended = 2.0 * META_INPUT_GROSS / (META_TURNS + 1.0)
    m = 2.0 * META_INPUT_GROSS / (META_AGENTS * META_TURNS * (META_TURNS + 1.0))
    output_per_turn = META_OUTPUT / (META_AGENTS * META_TURNS)

    out = {
        "route": "Appendix A of arXiv:2604.03071; appended positions N L = 2C/(T+1)",
        "given": {"gross_input_tokens_C": META_INPUT_GROSS, "output_tokens": META_OUTPUT,
                  "avg_turns_T": META_TURNS, "agents_N": META_AGENTS},
        "gross_input_per_output_token": gross_ratio,
        "appended_over_gross": 2.0 / (META_TURNS + 1.0),
        "appended_tokens_N_L": appended,
        "appended_input_tokens_excluding_output": appended - META_OUTPUT,
        "counted_tokens_per_output_token": appended / META_OUTPUT,
        "appended_input_per_output_token": (appended - META_OUTPUT) / META_OUTPUT,
        "per_turn": {
            "tokens_added_per_turn_m": m,
            "output_tokens_per_turn": output_per_turn,
            "input_tokens_per_turn": m - output_per_turn,
            "check_m_over_output_per_turn": m / output_per_turn,
            "note": ("Second derivation of the same number from the same three inputs; it "
                     "agrees with N L / output by construction, so it is a transcription "
                     "check rather than independent evidence."),
        },
    }

    # Appendix A's own price formulas, evaluated, as the validation of the structure.
    p_nocache = OPUS_45_INPUT_PRICE_PER_TOKEN * META_INPUT_GROSS
    p_cache = (C_HIT_MULT * OPUS_45_INPUT_PRICE_PER_TOKEN * META_INPUT_GROSS
               + (1.0 + C_STORE_MULT) * OPUS_45_INPUT_PRICE_PER_TOKEN * appended)
    out_cost = OPUS_45_OUTPUT_PRICE_PER_TOKEN * META_OUTPUT
    out["price_reproduction"] = {
        "formula_nocache": "P_nocache = c_in * C",
        "formula_cache": "P_cache = c_hit * C + (c_in + c_store) * N L",
        "p_nocache_usd": p_nocache, "output_cost_usd": out_cost,
        "total_uncached_usd": p_nocache + out_cost, "paper_uncached_usd": META_COST_UNCACHED,
        "uncached_error": abs(p_nocache + out_cost - META_COST_UNCACHED) / META_COST_UNCACHED,
        "p_cache_usd": p_cache, "total_cached_usd": p_cache + out_cost,
        "paper_cached_usd": META_COST_CACHED,
        "cached_error": abs(p_cache + out_cost - META_COST_CACHED) / META_COST_CACHED,
        "conclusion": ("Appendix A's formulas reproduce both of the paper's cost figures to "
                       "under 0.25% at Claude Opus 4.5 list prices, which validates the "
                       "structure and fixes T. This is the derivation the row uses."),
    }

    # DONOR-SIDE ONLY. T enters the conversion of the donor's reported gross count C into
    # appended positions N L. It does not enter the transfer: r = N L / output = m / o, in
    # which T cancels. Do not read this table as a target-side sensitivity.
    out["sensitivity_to_T_donor_side_only"] = {
        str(t): {"appended_over_gross": 2.0 / (t + 1.0),
                 "counted_tokens_per_output_token": (2.0 * META_INPUT_GROSS / (t + 1.0)) / META_OUTPUT}
        for t in (30, 40, 54.8, 70, 90)
    }

    # Corrected cost route, kept as corroboration of the geometry route. Invert the
    # cached cost for the appended share f using Appendix A's OWN price model, in which
    # appended tokens cost c_in + c_store = 3 c_in. Two readings of the c_hit base.
    cached_input_cost = META_COST_CACHED - META_COST_OUTPUT
    uncached_input_cost = OPUS_45_INPUT_PRICE_PER_TOKEN * META_INPUT_GROSS
    target = cached_input_cost / uncached_input_cost
    cost_route = {}
    for label, hit_on_whole_C in (("c_hit charged on all of C", True),
                                  ("c_hit charged on C - N L", False)):
        if hit_on_whole_C:
            f = (target - C_HIT_MULT) / (1.0 + C_STORE_MULT)
        else:
            f = (target - C_HIT_MULT) / (1.0 + C_STORE_MULT - C_HIT_MULT)
        cost_route[label] = {
            "appended_share_f": f,
            "counted_tokens_per_output_token": f * META_INPUT_GROSS / META_OUTPUT,
        }
    out["cost_route_corroboration"] = {
        "price_model": "appended tokens at c_in + c_store = 3 c_in, the one-hour cache",
        "readings": cost_route,
        "geometry_route": out["counted_tokens_per_output_token"],
        "agreement": ("Both readings land within 3%% of the geometry route's %.2f, so the cost "
                      "statement and the dialog geometry corroborate each other."
                      % out["counted_tokens_per_output_token"]),
    }

    out["superseded_cost_inversion"] = {
        "result_discarded": "8.4 to 13.8 counted input tokens per output token",
        "what_it_did": ("Solved the cached-versus-uncached cost ratio for a fresh share f under "
                        "the assumption that appended tokens are billed at a write multiplier "
                        "INSTEAD OF the base input rate, substituting the 5-minute cache's 1.25x "
                        "write price into a dollar figure the paper computed at the one-hour "
                        "cache's cost."),
        "why_it_is_wrong": ("Appendix A sets c_store = 2 c_in, so appended tokens cost c_in + "
                            "c_store = 3x the base rate, not 1.25x or 2x. Substituting the wrong "
                            "multiplier into the paper's own dollar figure solves for the wrong "
                            "quantity. Redone at 3x, the same inversion returns 5.29 to 5.47 "
                            "depending on the c_hit base, which agrees with the geometry route; "
                            "see cost_route_corroboration. Retained so the 8.4-13.8 figure is "
                            "identifiable as an error if it surfaces in an earlier draft."),
    }
    return out


def compute_scenarios(calib):
    """FLOP scenarios for the FLT run.

    What is transferred is a PER-TURN COMPOSITION RATIO, not anything about dialog length:

        r = N L / output = (N T m) / (N T o) = m / o

    so T cancels, and

        k = 1 + r = 2 + (tool-result tokens per turn) / (output tokens per turn)

    which returns 2 + 1468.3/341.2 = 6.30 on the donor at a single mean T. T mattered only
    on the donor side, to recover m from a reported gross count. An FLT agent whose dialogs
    run twice as long as Meta's, at the same tool-result and output volume per turn, has the
    same r and the same k. Earlier revisions of this row expressed the central, the band and
    both direction arguments in target dialog length, which was dimensionally wrong.

    Convention k = 1 + r is DECISIONS.md's: N L is the input side, and the re-entered output
    positions count as fresh input or cache creation when they re-enter while the output is
    counted again at generation, two separate forward passes.
    """
    gross_r = calib["gross_input_per_output_token"]
    ipt = calib["per_turn"]["input_tokens_per_turn"]     # tool-result tokens per turn
    opt = calib["per_turn"]["output_tokens_per_turn"]

    # Settled donor anchor, relayed 2026-09-13 from research/meta-textbook.md#transfer-anchor,
    # not re-derived here. Its band is an APPEND-PROFILE band at the donor's fixed T = 54.8,
    # running from a front-loaded opening block to linearly growing appends. It is a band on
    # the donor's own r, not on the transfer.
    DONOR_R = 4.21
    DONOR_R_LOW = 3.5
    DONOR_R_HIGH = 5.3

    # Transfer band: whether the FLT harness's tool-result-to-output composition resembles
    # Meta's at all. Tool result per output token from about 1 to about 8 gives k = 3 to 10.
    TRANSFER_K_LOW = 3.0
    TRANSFER_K_HIGH = 10.0

    # Short-output scenario: Meta's per-turn tool-result volume, twice its output per turn.
    R_OUTPUT_LENGTH = (ipt + 2.0 * opt) / (2.0 * opt)

    def row(r, label, note):
        k = 1.0 + r
        tokens = OUTPUT_TOKENS * k
        return {
            "label": label,
            "appended_input_per_output_token_r": r,
            "counted_multiplier_k": k,
            "tool_result_per_output_token": max(r - 1.0, 0.0),
            "counted_input_tokens": OUTPUT_TOKENS * r,
            "tokens_input_cache_creation_output": tokens,
            "compute_flops": tokens * FLOPS_PER_TOKEN,
            "note": note,
        }

    scenarios = {
        "output_only_floor": row(
            0.0, "Output tokens only",
            "The whole of the published compute record. A strict floor: it counts no prompt, "
            "no tool result, no Lean error text and no cache creation."),
        "output_length_low": row(
            R_OUTPUT_LENGTH, "Low, output-length argument",
            "Meta's per-turn tool-result volume of %.0f tokens against twice its %.0f output "
            "tokens per turn. Meta's agents were short-output and file-read-heavy; a proving "
            "run emitting whole Lean proof bodies per turn divides a similar tool-result "
            "volume into more output, which lowers r." % (ipt, opt)),
        "donor_low": row(
            DONOR_R_LOW, "Donor append-profile band, low",
            "Appendix A's equal-chunk-per-turn assumption relaxed toward a front-loaded "
            "opening block, at the donor's fixed T. A band on the donor's own r."),
        "central": row(
            DONOR_R, "Central, recorded",
            "The settled donor value. The transfer assumption is that the FLT harness appends "
            "about %.2f tokens of tool result, card text and system prompt per token the model "
            "emits, which is what Meta's agents did." % (DONOR_R - 1.0)),
        "donor_high": row(
            DONOR_R_HIGH, "Donor append-profile band, high",
            "Appendix A relaxed toward linearly growing appends, at the donor's fixed T. Also "
            "the value a single-mean-T reading returns, which is what this row carried as its "
            "central before the role-by-role derivation."),
        "transfer_low": row(
            TRANSFER_K_LOW - 1.0, "Transfer band, low",
            "About 1 tool-result token per output token: an output-dense proving harness whose "
            "reads are mostly Prove2Me card summaries rather than file bodies."),
        "transfer_high": row(
            TRANSFER_K_HIGH - 1.0, "Transfer band, high",
            "About 8 tool-result tokens per output token: frequent session restarts and "
            "compaction re-paying the system prompt and tool definitions, on top of Prove2Me's "
            "shared DAG context and long Lean error output."),
        "gross_if_no_caching": row(
            gross_r, "Gross basis, caching premise failed",
            "Every context position forwarded because nothing was cached. Conditional on the "
            "caching premise being wrong, not on a reading of the params_tokens rule."),
    }

    scenarios["caching_premise"] = {
        "premise": ("The appended basis is selected over the gross basis because the harness "
                    "cached. Anthropic describes it as a Claude Code-based multi-agent harness; "
                    "Claude Code runs against the Anthropic API, where automatic prompt caching "
                    "moves the cache point forward as a conversation grows, rather than through "
                    "an OpenAI-compatibility layer, which is what prevented caching in the Meta "
                    "donor run and is why DECISIONS.md records that row on the gross basis."),
        "evidence": ("platform.claude.com/docs/en/build-with-claude/prompt-caching: 'With "
                     "automatic caching, the cache point moves forward automatically as "
                     "conversations grow. Each new request caches everything up to the last "
                     "cacheable block, and previous content is read from cache.'"),
        "leverage_factor": (1.0 + gross_r) / (1.0 + DONOR_R),
        "status": ("Not directly evidenced for this run: Anthropic published no cache counters. "
                   "It is the largest single lever in the row."),
    }

    run_seconds = 11 * 24 * 3600.0
    scenarios["published_structure"] = {
        "output_tokens": OUTPUT_TOKENS,
        "run_days": 11,
        "aggregate_output_tokens_per_second": OUTPUT_TOKENS / run_seconds,
        "agents_reported": "dozens (blog); a team of Claude agents working in parallel (report)",
        "sustained_output_tokens_per_second_per_agent": {
            str(n): OUTPUT_TOKENS / run_seconds / n for n in (24, 48, 96)},
        "reading": ("The low end of dozens is not achievable by a single sequential stream, so "
                    "either concurrency ran well above the named agent count or each named agent "
                    "drove many parallel sessions. Either reading implies sessions more numerous "
                    "than the donor's, which bears on composition; it does not fix r. Earlier "
                    "revisions of this row wrongly said no agent count was published."),
    }

    scenarios["direction_arguments"] = {
        "downward": ["More output per turn than Meta's short-output, file-read-heavy agents; "
                     "this is the output_length_low scenario."],
        "upward": ["Session restarts and compaction rebuild the prefix as new appended "
                   "positions, re-paying the system prompt, tool definitions and re-read files "
                   "each time. The blog's account of the earlier failed campaign, that agents "
                   "quickly lost track of the project's state, is what restarts look like from "
                   "outside.",
                   "Prove2Me's shared DAG of theorem statements with natural-language "
                   "descriptions is tool-result volume per turn that Meta's agents did not carry "
                   "on top of their own file reads."],
        "void": ["Dialog length. Under r = m/o it does not enter the transfer at all."],
    }

    central = scenarios["central"]
    scenarios["model_size_sensitivity_on_central"] = {
        "active_parameters_low": ACTIVE_PARAMETERS_LOW,
        "active_parameters_high": ACTIVE_PARAMETERS_HIGH,
        "compute_flops_low": central["tokens_input_cache_creation_output"] * 2 * ACTIVE_PARAMETERS_LOW,
        "compute_flops_high": central["tokens_input_cache_creation_output"] * 2 * ACTIVE_PARAMETERS_HIGH,
    }
    return scenarios


def attention_scenario(tokens_forwarded):
    """Cached-context attention omitted by the 2 * active_parameters convention.

    Recipe and bracketing shapes follow DECISIONS.md and the dataset's RULER row:
    4 * layers * d_model * context_positions FLOPs per appended position.
    """
    shapes = {"L=64, d=8192": (64, 8192),
              "L=80, d=10240": (80, 10240),
              "L=96, d=12288": (96, 12288)}
    contexts = {"30k": 30_000, "100k": 100_000, "200k": 200_000}
    out = {
        "note": ("Not included in compute_flops. The dataset's 2 * active_parameters coefficient "
                 "omits attention; the omission is one-sided, and at this run's context lengths "
                 "it is of the same order as the recorded value."),
        "recipe": "4 * layers * d_model * context_positions per appended position",
        "recipe_source": "DECISIONS.md, cached-context attention; dataset/research/ruler/ruler.md",
        "appended_positions": tokens_forwarded,
        "mean_context_positions_assumed": "30k to 200k, central 100k; not published for this run",
        "shapes": {},
    }
    for sname, (layers, d_model) in shapes.items():
        four_l_d = 4 * layers * d_model
        out["shapes"][sname] = {"layers": layers, "d_model": d_model, "four_L_d": four_l_d}
        for cname, ctx in contexts.items():
            out["shapes"][sname][f"attention_flops_at_{cname}_context"] = (
                four_l_d * ctx * tokens_forwarded)
    return out


# ---------------------------------------------------------------- human time

# DECISIONS.md convention (Damon, 2026-09-13): human_time is literal active hours and one
# person-year is 2,000 active hours. Less-than-full-time engagement is expressed as a stated
# on-task fraction, never as a lower hours-per-year figure.
#
# Both routes below produce FTE-YEARS, not hours: Route 1's totals are all-in FTE times five
# years times one plus the remainder multiplier, derived from the fellowship award and elapsed
# calendar time; Route 2's rate is the same project's lines divided by those same FTE-years.
# Neither anchor carries an hours-per-year figure of its own, so the conversion is this one.
# No on-task fraction is applied. The 4-6 all-in person-years are funded headcount plus a
# judgment about the volunteer tail, not effective effort by construction, and the funded staff
# are not on this project every working hour. Declining the fraction is the conservative end:
# any fraction below 1 cuts the active hours and lowers human_time (0.7 would give 58,800 h).
ACTIVE_HOURS_PER_PERSON_YEAR = 2000.0
SECONDS_PER_HOUR = 3600.0


def human_estimate(anchors, artifact):
    """Active human time to produce the same verified deliverable, unaided.

    Revised 2026-09-13 on the Meta reviewer's finding that the Imperial College FLT
    project's funded staffing is about 1.5-2 FTE, not the 3 FTE this row first assumed,
    and that the funded clock starts with the fellowship in September 2024 rather than
    with the first commit in November 2023. The same measured output therefore represents
    fewer person-years and a faster realized rate.
    """
    icl = anchors["icl_flt_project"]
    mathlib = anchors["mathlib_v4_33_0"]
    rep = artifact["reported_by_source_not_measured_here"]

    grant_start = date(2024, 9, 1)          # EPSRC EP/Y022904/1 start
    asof = date(2026, 9, 13)
    funded_years = (asof - grant_start).days / 365.25

    # --- Route 1: scale up from the Imperial College project
    funded_fte = {"low": 1.5, "central": 1.75, "high": 2.0}   # GBP 186,809/yr awarded
    funded_py = {k: v * funded_years for k, v in funded_fte.items()}
    all_in_py = {"low": 4.0, "central": 5.0, "high": 6.0}     # funded plus the volunteer tail
    route1 = {
        "funded_years_to_date": funded_years,
        "funded_fte": funded_fte,
        "funded_person_years": funded_py,
        "all_in_person_years": all_in_py,
        "icl_output": {
            "lean_lines": icl["lean_lines"],
            "theorem_or_lemma_declarations": icl["theorem_or_lemma_declarations_at_line_start"],
            "sorry_remaining": icl["sorry_occurrences"],
        },
    }
    route1["realized_rate_lines_per_person_year"] = {
        "fast": icl["lean_lines"] / all_in_py["low"],
        "central": icl["lean_lines"] / all_in_py["central"],
        "slow": icl["lean_lines"] / all_in_py["high"],
    }
    route1["realized_rate_lines_per_active_hour"] = {
        k: v / ACTIVE_HOURS_PER_PERSON_YEAR
        for k, v in route1["realized_rate_lines_per_person_year"].items()}
    route1["realized_rate_note_for_borrowing_rows"] = (
        "Central 11,765 lines per all-in person-year, 5.88 per active hour at 2,000 hours. This "
        "SUPERSEDES the 6,960 lines per person-year and 3.87 per active hour carried by Revisions 1 "
        "and 2, which assumed 3 FTE over 2.82 calendar years (8.45 person-years). Revision 3 "
        "corrected the staffing to 1.5-2 funded FTE with the funded clock starting at the September "
        "2024 fellowship, i.e. 4-6 person-years all in. Restating the old 6,960 at 2,000 hours gives "
        "3.48; that pairs a superseded numerator with the new denominator and should not be used. "
        "Nothing in this row consumes a lines-per-hour figure: both routes run on person-years, and "
        "this rate is derived for display and for transfer.")

    # All-in FTE implied by the same figures, used to cost the grant's own five-year plan.
    all_in_fte = {k: v / funded_years for k, v in all_in_py.items()}
    reduction_py = {k: v * 5.0 for k, v in all_in_fte.items()}
    # PROOF-PATH.md gives the exact strength of each named step: Langlands-Tunnell in the
    # octahedral case only, Mazur as irreducibility of E_P[p] for Frey curves only, Ribet for
    # the Frey representation at squarefree conductor-supported levels only, R = T level-
    # conditioned for semistable W at p = 3 and p in {3, 5}, Wiles for semistable curves only.
    # The earlier 2-6 was judged against the full classical theorems and was biased high.
    remainder_multiplier = {"low": 1.5, "central": 2.5, "high": 5.0}
    route1["all_in_fte"] = all_in_fte
    route1["reduction_to_1980s_person_years"] = reduction_py
    route1["remainder_multiplier_on_reduction"] = remainder_multiplier
    route1["total_person_years"] = {
        "low": reduction_py["low"] * (1 + remainder_multiplier["low"]),
        "central": reduction_py["central"] * (1 + remainder_multiplier["central"]),
        "high": reduction_py["high"] * (1 + remainder_multiplier["high"]),
    }

    # --- Route 2: size the human-idiom deliverable, apply the rate
    nonboiler = rep["lines_of_lean_excluding_generated_boilerplate"]
    compression = {"low": 70.0, "central": 21.0, "high": 7.0}
    human_lines = {k: nonboiler / v for k, v in compression.items()}
    # Anchored at or below 15,000 lines per person-year, per the Meta review.
    rate_lines_per_py = {"low": 15000.0, "central": 12500.0, "high": 10000.0}
    route2 = {
        "artifact_non_boilerplate_lines": nonboiler,
        "artifact_declarations_total": (rep["theorems_in_final_tree"]
                                        + rep["local_supporting_lemmas"]),
        "mathlib_lines": mathlib["lean_lines_under_Mathlib"],
        "mathlib_theorem_or_lemma_declarations": mathlib["theorem_or_lemma_declarations_at_line_start"],
        "artifact_over_mathlib_lines": nonboiler / mathlib["lean_lines_under_Mathlib"],
        "artifact_over_mathlib_declarations": (
            (rep["theorems_in_final_tree"] + rep["local_supporting_lemmas"])
            / mathlib["theorem_or_lemma_declarations_at_line_start"]),
        "machine_to_human_idiom_compression": compression,
        "human_idiom_lines": human_lines,
        "lines_per_person_year": rate_lines_per_py,
        "person_years": {k: human_lines[k] / rate_lines_per_py[k] for k in compression},
    }
    route2["active_hours"] = {k: v * ACTIVE_HOURS_PER_PERSON_YEAR
                              for k, v in route2["person_years"].items()}

    chosen = {"low": 12.0, "central": 42.0, "high": 150.0}
    human = {
        "route1_scale_from_icl_project": route1,
        "route2_size_and_rate": route2,
        "not_independent": (
            "The two routes are NOT independent and their agreement is not evidence that the "
            "level is right. Route 1's total is linear in the assumed FTE; Route 2's rate is "
            "the same project's realized lines per person-year, which is inversely proportional "
            "to that FTE, so Route 2's person-years are linear in it too, in the same direction. "
            "They agree at every FTE. What the comparison does test is the non-FTE half: whether "
            "a remainder multiplier on a five-year plan lands where an idiom compression at the "
            "observed rate does."),
        "route1_scope_caveat": (
            "Route 1 costs the Imperial plan and multiplies it, which transfers a rate "
            "established on the modern route to the 1995 Darmon-Diamond-Taylor route in the "
            "special cases the argument needs. The two are different bodies of work."),
        "reconciliation": (
            "Route 1 gives %.0f-%.0f person-years, central %.0f. Route 2 gives %.0f-%.0f, "
            "central %.0f. The recorded range is 12-150 person-years, central 42, which both "
            "routes support; Route 2's corners combine the most and least favourable "
            "assumptions at once and are not treated as bounds."
            % (route1["total_person_years"]["low"], route1["total_person_years"]["high"],
               route1["total_person_years"]["central"], route2["person_years"]["low"],
               route2["person_years"]["high"], route2["person_years"]["central"])),
        "what_changed": (
            "Previously 60 person-years central on a 3 FTE assumption and a clock running from "
            "the first commit. Two corrections. Funded staffing is 1.5-2 FTE on GBP 186,809 a "
            "year and the funded clock starts with the fellowship in September 2024, so the "
            "same 58,827 lines represent 4-6 person-years rather than 8.5 and the realized rate "
            "rises from about 7,000 to 10,000-15,000 lines per person-year. And PROOF-PATH.md "
            "shows the classical theorems are proved only in restricted forms, so the remainder "
            "multiplier drops from 2-6 to 1.5-5. Together these take the central from 60 to 42."),
        "active_hours_per_person_year": ACTIVE_HOURS_PER_PERSON_YEAR,
        "person_years": chosen,
        "active_hours": {k: v * ACTIVE_HOURS_PER_PERSON_YEAR for k, v in chosen.items()},
        "human_time_seconds": {k: v * ACTIVE_HOURS_PER_PERSON_YEAR * SECONDS_PER_HOUR
                               for k, v in chosen.items()},
    }
    return human


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--artifact", required=True,
                    help="path to agent-work/sources/flt-anthropic/artifact-measurements.json")
    ap.add_argument("--anchors", required=True,
                    help="path to agent-work/sources/flt-anthropic/human-anchor-measurements.json")
    ap.add_argument("--out", required=True,
                    help="path to write research/flt-anthropic/calculations.json")
    args = ap.parse_args()

    artifact = json.load(open(args.artifact))
    anchors = json.load(open(args.anchors))

    calib = meta_calibration()
    comp = compute_scenarios(calib)
    human = human_estimate(anchors, artifact)

    central_flops = comp["central"]["compute_flops"]
    central_tokens = comp["central"]["tokens_input_cache_creation_output"]
    central_seconds = human["human_time_seconds"]["central"]

    result = {
        "point_id": "reas-flt-lean-anthropic-internal",
        "generated_by": "research/flt-anthropic/compute_flt_anthropic.py",
        "inputs": {"artifact": args.artifact, "anchors": args.anchors},
        "reported_by_anthropic": {
            "output_tokens": OUTPUT_TOKENS,
            "days": 11,
            "run_start": "2026-08-07",
            "root_theorem_proved": "2026-08-18T02:00:57Z",
            "published": "2026-09-04",
            "model": "unnamed internal research model, 'roughly comparable to Claude Fable 5.1'",
        },
        "model_coefficient": {
            "active_parameters": ACTIVE_PARAMETERS,
            "flops_per_token": FLOPS_PER_TOKEN,
            "basis": "dataset-wide frontier closed-model prior, not an Anthropic disclosure",
        },
        "meta_donor_calibration": calib,
        "compute_scenarios": comp,
        "omitted_cached_context_attention": attention_scenario(central_tokens),
        "human_time": human,
        "recorded_values": {
            "compute_flops": central_flops,
            "tokens": central_tokens,
            "tokens_accounting": "input_cache_creation_output",
            "human_time_seconds": central_seconds,
            "flops_per_human_second": central_flops / central_seconds,
        },
    }

    with open(args.out, "w") as fh:
        json.dump(result, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    r = result["recorded_values"]
    print("compute_flops      %.4g" % r["compute_flops"])
    print("tokens             %.6g" % r["tokens"])
    print("human_time (s)     %.6g" % r["human_time_seconds"])
    print("FLOPs / human-s    %.3g" % r["flops_per_human_second"])
    print("wrote", args.out)


if __name__ == "__main__":
    main()
