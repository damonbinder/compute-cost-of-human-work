#!/usr/bin/env python3
"""Compute and human-time arithmetic for the Meta FAIR textbook formalization row.

Dependencies: Python 3.9+ standard library only.

Usage:
    python3 calculations.py <inputs.json> <output.json>

Example (paths relative to the repository root of this batch):
    python3 research/meta-textbook/calculations.py \
        agent-work/sources/meta-textbook/paper-token-tables.json \
        research/meta-textbook/calculations.json

The input file is the retained transcription of the paper's Tables 1-3. The script writes a new
output file and never modifies its input. Every judgement-based constant is defined once below,
under HUMAN_* or ATTENTION_*, and is argued for in research/meta-textbook.md.
"""

import json
import sys

M = 1e6

# --- Shared model coefficient (from ../AI Compute vs Human Time/dataset/models.csv, id
# claude-opus-4-5; read-only reference, not modified) ---
FLOPS_PER_TOKEN = 2e11
ACTIVE_PARAMETERS = 1e11

# --- Attention scenario: bracketing (n_layers, d_model) pairs at ~100B dense-equivalent active
# parameters, using params ~ 12 * n_layers * d_model^2. Attention FLOPs per processed position at
# context length c is 4 * n_layers * d_model * c, so a prefill of N positions costs about
# 2 * n_layers * d_model * N^2. See DECISIONS.md "Cached-context attention". ---
ATTENTION_ARCHS = {
    "wide_shallow_L48_d13312": (48, 13312),
    "central_L80_d10240": (80, 10240),
    "narrow_deep_L126_d8192": (126, 8192),
}

# --- Human baseline constants (argued in research/meta-textbook.md#human-baseline) ---
# Human-equivalent line count for the same 340 targets, discounting the agents' documented
# duplication, rabbit-hole content and superficial mathlib restatements against the 130,062
# measured lines.
HUMAN_EQUIV_LINES = {"low": 70000, "central": 90000, "high": 130000}
# Lines of Lean produced per expert person-year. Every anchor in
# agent-work/sources/meta-textbook/human-formalization-anchors.md sits at or below 15,000: seL4 gives 15,000
# project-specific and 10,000 all-in, and Imperial FLT gives 10,000-15,000 once its FTE assumption
# is stated. The central takes the top of that anchor band. The "low" rate is deliberately above
# every anchor and is a judgment, not an anchored value; see research/meta-textbook.md.
HUMAN_LINES_PER_PERSON_YEAR = {"low_above_anchor_judgment": 25000, "central": 15000, "high": 10000}
# DECISIONS.md, "Person-years and active hours" (Damon, 2026-09-13): human_time is literal active
# time, one person-year is 2,000 active hours, and less-than-full-time engagement on the task is a
# stated on-task fraction rather than a lower hours-per-year figure.
HOURS_PER_PERSON_YEAR = 2000
# The anchors report effort charged to the project, and for a formalization project the reading,
# proof writing and review that make up charged effort are the task itself, so no fraction below 1
# is applied. Argued in research/meta-textbook.md#human-baseline.
ON_TASK_FRACTION = 1.0
SECONDS_PER_HOUR = 3600
# Fully loaded annual cost of one expert formalizer, used only for the cost cross-check in the
# note. This is not used to set any time.
SALARY_PER_PERSON_YEAR_USD = 150000


def main(inp_path: str, out_path: str) -> None:
    with open(inp_path) as fh:
        src = json.load(fh)

    t2 = src["table2_by_agent_type"]
    t3 = src["table3_by_outcome"]
    price = src["anthropic_opus_4_5_list_price_usd_per_million"]
    ratios = src["appendix_a_price_ratios"]

    n_agents, in_M, out_M, total_M, _, _, turns, avg_turns = t2["Total"]
    input_tokens = in_M * M
    output_tokens = out_M * M
    total_tokens = input_tokens + output_tokens

    out = {}

    # --- 0. Internal consistency of the retained tables ---
    col_sum_in = sum(v[1] for k, v in t2.items() if not k.startswith("_") and k != "Total")
    col_sum_out = sum(v[2] for k, v in t2.items() if not k.startswith("_") and k != "Total")
    col_sum_n = sum(v[0] for k, v in t2.items() if not k.startswith("_") and k != "Total")
    col_sum_turns = sum(v[6] for k, v in t2.items() if not k.startswith("_") and k != "Total")
    out["table2_column_checks"] = {
        "sum_of_rows_in_M": col_sum_in,
        "printed_total_in_M": in_M,
        "sum_of_rows_out_M": round(col_sum_out, 4),
        "printed_total_out_M": out_M,
        "sum_of_rows_count": col_sum_n,
        "printed_total_count": n_agents,
        "sum_of_rows_turns": col_sum_turns,
        "printed_total_turns": turns,
        "avg_turns_recomputed": turns / n_agents,
        "printed_avg_turns": avg_turns,
    }
    t3n, t3in, t3out = t3["Total"][0], t3["Total"][1], t3["Total"][2]
    out["table2_vs_table3"] = {
        "agents_table2": n_agents,
        "agents_table3": t3n,
        "agent_shortfall": n_agents - t3n,
        "input_M_table2": in_M,
        "input_M_table3": t3in,
        "input_M_shortfall": round(in_M - t3in, 4),
        "output_M_shortfall": round(out_M - t3out, 4),
        "note": "Table 3 is the smaller set; the paper's prose quotes the Table 2 totals, which "
                "this row uses.",
        "aborted_share_of_table3_input": t3["Aborted"][1] / t3in,
    }

    # --- 1. Price cross-check: does the transcription reproduce the paper's own $430K/$14K? ---
    cost_in = input_tokens / M * price["input"]
    cost_out = output_tokens / M * price["output"]
    out["price_crosscheck"] = {
        "uncached_input_usd": cost_in,
        "output_usd": cost_out,
        "uncached_total_usd": cost_in + cost_out,
        "paper_uncached_total_usd": src["paper_cost_claims_usd"]["uncached_total"],
        "paper_output_usd": src["paper_cost_claims_usd"]["output_component_both_cases"],
    }

    # --- 2. Appendix A dialog-geometry model ---
    T = turns / n_agents
    m_per_turn = 2 * input_tokens / (n_agents * T * (T + 1))
    L_dialog = T * m_per_turn
    distinct_input_tokens = n_agents * L_dialog  # = 2C/(T+1)
    p_cache_over_p_nocache = ratios["c_hit_over_c_in"] + (
        1 + ratios["c_store_over_c_in"]
    ) * distinct_input_tokens / input_tokens
    out["appendix_a_model"] = {
        "agents_N": n_agents,
        "avg_turns_T": T,
        "input_positions_C": input_tokens,
        "avg_tokens_added_per_turn_m": m_per_turn,
        "avg_final_dialog_length_L": L_dialog,
        "distinct_input_tokens_N_times_L": distinct_input_tokens,
        "reread_multiple_C_over_NL": input_tokens / distinct_input_tokens,
        "mean_prompt_length_per_call": input_tokens / turns,
        "cached_over_uncached_input_price_ratio": p_cache_over_p_nocache,
        "implied_cached_total_usd": p_cache_over_p_nocache * cost_in + cost_out,
        "paper_cached_total_usd": src["paper_cost_claims_usd"]["cached_estimate_total"],
    }

    # --- 3. compute_flops ---
    # Central accounting: prompt caching is unavailable on the OpenAI-compatibility endpoint the
    # released code calls, so every one of the C input positions is a real forward pass.
    flops_no_cache = total_tokens * FLOPS_PER_TOKEN
    # Alternative if an undisclosed gateway did cache: only newly added positions are processed.
    tokens_if_cached = distinct_input_tokens + output_tokens
    flops_if_cached = tokens_if_cached * FLOPS_PER_TOKEN
    out["compute"] = {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "tokens_central": total_tokens,
        "flops_per_token": FLOPS_PER_TOKEN,
        "active_parameters": ACTIVE_PARAMETERS,
        "compute_flops_central_no_cache": flops_no_cache,
        "tokens_if_caching_had_applied": tokens_if_cached,
        "compute_flops_if_caching_had_applied": flops_if_cached,
        "ratio_central_to_cached": flops_no_cache / flops_if_cached,
    }
    # Sensitivity on the assumed active parameter count (30B-300B, the dataset's Opus-family band).
    out["compute"]["active_parameter_sensitivity"] = {
        f"{p/1e9:.0f}B": total_tokens * 2 * p for p in (3e10, 1e11, 3e11)
    }

    # --- 4. Omitted attention term ---
    # Under the Appendix A geometry, agent a's turn i carries a prompt of i*m positions, so the
    # sum of squared prompt lengths over the whole run is N * m^2 * T(T+1)(2T+1)/6.
    sum_sq_prompt = n_agents * m_per_turn ** 2 * T * (T + 1) * (2 * T + 1) / 6
    mean_ctx = input_tokens / turns
    att = {}
    for name, (n_layers, d_model) in ATTENTION_ARCHS.items():
        coeff = 2 * n_layers * d_model           # prefill: 2*L*d*N^2
        prefill = coeff * sum_sq_prompt
        decode = 2 * coeff * mean_ctx * output_tokens   # 4*L*d*c per generated token
        att[name] = {
            "n_layers": n_layers,
            "d_model": d_model,
            "implied_dense_params_12Ld2": 12 * n_layers * d_model ** 2,
            "prefill_attention_flops": prefill,
            "decode_attention_flops": decode,
            "total_attention_flops": prefill + decode,
            "as_fraction_of_recorded": (prefill + decode) / flops_no_cache,
        }
    out["omitted_attention"] = {
        "sum_of_squared_prompt_lengths": sum_sq_prompt,
        "rms_prompt_length": (sum_sq_prompt / turns) ** 0.5,
        "mean_prompt_length": mean_ctx,
        "scenarios": att,
    }

    # --- 5. Human baseline ---
    human = {}
    for label, lines, rate in (
        ("low", HUMAN_EQUIV_LINES["low"], HUMAN_LINES_PER_PERSON_YEAR["low_above_anchor_judgment"]),
        ("central", HUMAN_EQUIV_LINES["central"], HUMAN_LINES_PER_PERSON_YEAR["central"]),
        ("high", HUMAN_EQUIV_LINES["high"], HUMAN_LINES_PER_PERSON_YEAR["high"]),
    ):
        py = lines / rate
        hours = py * HOURS_PER_PERSON_YEAR * ON_TASK_FRACTION
        human[label] = {
            "human_equivalent_lines": lines,
            "lines_per_person_year": rate,
            "person_years": py,
            "hours_per_person_year": HOURS_PER_PERSON_YEAR,
            "on_task_fraction": ON_TASK_FRACTION,
            "hours": hours,
            "seconds": hours * SECONDS_PER_HOUR,
            "hours_per_designated_target": hours / src["table1"]["target_theorems_and_defs"],
            "salary_equivalent_usd": py * SALARY_PER_PERSON_YEAR_USD,
        }
    out["human"] = human
    out["human"]["_scenario_construction"] = (
        "low pairs the smallest human-equivalent line count with a rate above every anchor; high "
        "pairs the largest line count with the slowest anchor; central pairs the central line "
        "count with the top of the anchor band."
    )
    out["human"]["_anchor_rates_lines_per_person_year"] = {
        "sel4_project_specific_165000_over_11py": 165000 / 11,
        "sel4_all_in_200000_over_20py": 200000 / 20,
        "imperial_flt_58062_over_4py_funded_plus_volunteers": 58062 / 4,
        "imperial_flt_58062_over_6py_with_volunteers": 58062 / 6,
    }

    # --- 6. Cost comparison, stated as cost and never converted into a human time ---
    out["cost_comparison"] = {
        "paper_cached_price_usd": src["paper_cost_claims_usd"]["cached_estimate_total"],
        "uncached_price_usd": cost_in + cost_out,
        "central_human_salary_equivalent_usd": human["central"]["salary_equivalent_usd"],
        "salary_per_person_year_usd": SALARY_PER_PERSON_YEAR_USD,
        "note": "A salary comparison. It is not evidence about duration and sets no field.",
    }


    # --- 7. Transfer anchor: appended input per output token, applied role by role ---
    # appended_a = m_a * T_a = 2*C_a/(T_a+1) is exact for one agent. 2/(T+1) is convex in T, so
    # applying it once at the unweighted mean T overstates for a heterogeneous population in which
    # high-C agents also have high T. Apply it to each published partition instead.
    def partition_appended(table):
        rows, total = {}, 0.0
        for role, v in table.items():
            if role.startswith("_") or role == "Total":
                continue
            n, c_m, turns_r = v[0], v[1] * M, v[6]
            t_r = turns_r / n
            appended_r = 2 * c_m / (t_r + 1)
            total += appended_r
            rows[role] = {
                "N": n, "C_tokens": c_m, "turns": turns_r, "T": t_r,
                "appended_tokens": appended_r, "appended_over_C": appended_r / c_m,
                "mean_prompt_length": c_m / turns_r,
            }
        return rows, total

    role_rows, appended_roles = partition_appended(t2)
    outcome_rows, appended_outcomes = partition_appended(t3)
    appended_aggregate = 2 * input_tokens / (T + 1)

    # Front-loaded profile at an opening block the harness's measured fixed prefix supports:
    # ~7,936 tokens of tool schemas plus a 347-2,144 token mode prompt. Applied per role, skipping
    # any role whose mean prompt length is below B (the profile is infeasible there).
    B = 10000.0
    appended_front, front_detail = 0.0, {}
    for role, r_ in role_rows.items():
        t_r, c_a = r_["T"], r_["C_tokens"] / r_["N"]
        if r_["mean_prompt_length"] <= B or t_r <= 1:
            appended_front += r_["appended_tokens"]
            front_detail[role] = {"feasible_at_B": False, "used": "equal_chunk"}
            continue
        b = (c_a - t_r * B) / (t_r * (t_r - 1) / 2)
        appended_front += r_["N"] * (B + (t_r - 1) * b)
        front_detail[role] = {"feasible_at_B": True, "per_turn_increment_b": b}

    # Output generated on an agent's last turn is never re-appended.
    output_per_turn = output_tokens / turns
    output_never_reappended = n_agents * output_per_turn

    def three_quantities(appended, out_tokens=None, n=None):
        out_tokens = output_tokens if out_tokens is None else out_tokens
        n = n_agents if n is None else n
        non_output = appended - (out_tokens - n * (out_tokens / turns))
        return {
            "appended_input_tokens": appended,
            "appended_over_gross": appended / input_tokens,
            "non_output_appended_per_output_token": non_output / out_tokens,
            "r_total_appended_per_output_token": appended / out_tokens,
            "k_total_processed_per_output_token": 1 + appended / out_tokens,
            "implied_appended_per_agent": appended / n,
        }

    out["transfer_anchor"] = {
        "_definitions": {
            "non_output_appended_per_output_token":
                "Tool results, user turns and system prompt appended to dialogs, per output token. "
                "Excludes the model's own output.",
            "r_total_appended_per_output_token":
                "All distinct input positions ever appended, per output token. Includes the "
                "model's own output re-entering the next prompt, except the final turn's.",
            "k_total_processed_per_output_token":
                "1 + r. Total positions a caching harness would process per output token: every "
                "appended input position plus the output generation itself. This is the quantity "
                "COLUMNS' params_tokens counts, since re-entered output is cache creation, not a "
                "cache read. Do not relabel r as k.",
        },
        "central_role_level_table2": three_quantities(appended_roles),
        "alternative_outcome_level_table3": three_quantities(
            appended_outcomes, out_tokens=t3["Total"][2] * M, n=t3["Total"][0]),
        "alternative_outcome_level_table3_on_table2_output": three_quantities(appended_outcomes),
        "upper_bound_aggregate_single_application": three_quantities(appended_aggregate),
        "lower_front_loaded_per_role_B10000": three_quantities(appended_front),
        "role_detail": role_rows,
        "outcome_detail": outcome_rows,
        "front_loaded_detail": front_detail,
        "sanity_checks": {
            "output_tokens_per_turn": output_per_turn,
            "role_level_appended_per_turn": appended_roles / turns,
            "aggregate_appended_per_turn": appended_aggregate / turns,
            "measured_tool_schema_tokens": 7936,
            "mode_system_prompt_tokens_range": [347, 2144],
            "fixed_prefix_every_request_tokens_range": [8283, 10080],
            "sketcher_row_mean_prompt_length": role_rows["Sketcher"]["mean_prompt_length"],
            "sketcher_row_anomalous_below_tool_schema":
                bool(role_rows["Sketcher"]["mean_prompt_length"] < 7936),
        },
        "recommendation": {
            "r_central": appended_roles / output_tokens,
            "r_low": appended_front / output_tokens,
            "r_high": appended_aggregate / output_tokens,
            "k_central": 1 + appended_roles / output_tokens,
            "k_low": 1 + appended_front / output_tokens,
            "k_high": 1 + appended_aggregate / output_tokens,
            "basis": "Central is Appendix A's model applied to Table 2's eight roles. The band "
                     "runs from a front-loaded profile at the harness's measured fixed prefix to "
                     "the single aggregate application, which is an upper bound because 2/(T+1) "
                     "is convex in T. Between-agent heterogeneity is the dominant source of "
                     "spread and within-role heterogeneity pushes further down. Transfer T with "
                     "the ratio; it is a strong function of turn count.",
        },
    }

    # Per-role sum of squared prompt lengths, for the attention term.
    sum_sq_roles = sum(
        r_["N"] * (2 * r_["C_tokens"] / (r_["N"] * r_["T"] * (r_["T"] + 1))) ** 2
        * r_["T"] * (r_["T"] + 1) * (2 * r_["T"] + 1) / 6
        for r_ in role_rows.values()
    )
    out["omitted_attention"]["sum_of_squared_prompt_lengths_per_role"] = sum_sq_roles
    out["omitted_attention"]["per_role_scenarios"] = {
        name: {
            "total_attention_flops": 2 * nl * dm * sum_sq_roles
            + 2 * (2 * nl * dm) * mean_ctx * output_tokens,
            "as_fraction_of_recorded": (
                2 * nl * dm * sum_sq_roles + 2 * (2 * nl * dm) * mean_ctx * output_tokens
            ) / flops_no_cache,
        }
        for name, (nl, dm) in ATTENTION_ARCHS.items()
    }

    with open(out_path, "w") as fh:
        json.dump(out, fh, indent=2, sort_keys=False)
        fh.write("\n")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        raise SystemExit(2)
    main(sys.argv[1], sys.argv[2])
