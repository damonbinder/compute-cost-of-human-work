#!/usr/bin/env python3
"""Emit the per-point_id sections of research/terminal-bench.md.

Reads the calculations file the study's build script writes and prints one Markdown
section per row, with the retained inputs and the arithmetic. Output goes to stdout;
append it to the research note rather than letting the script edit the note in place.

Dependencies: Python 3.9+ standard library only.

Usage:
  python3 emit_point_sections.py --calculations candidates/terminal-bench/calculations.json
"""

import argparse
import json

# Attention-scenario brackets, kept identical to attention_scenario.py.
ARCH_CLASSES = [
    (100.0, ((64, 8192), (96, 12288))),
    (30.0, ((48, 6144), (64, 8192))),
    (0.0, ((32, 4096), (48, 6144))),
]


def archs_for(active):
    for floor, pair in ARCH_CLASSES:
        if active / 1e9 >= floor:
            return pair
    return ARCH_CLASSES[-1][1]


def attention(tok, fpt):
    active = fpt / 2.0
    ctx = tok / 2.0
    (l1, d1), (l2, d2) = archs_for(active)
    return 2.0 * l1 * d1 * ctx / active, 2.0 * l2 * d2 * ctx / active


def official(p, ht):
    lo, hi = attention(p["counted_tokens_per_trial"], p["flops_per_token"])
    lines = []
    lines.append("### %s" % p["point_id"])
    lines.append("")
    lines.append("%s under %s %s at reasoning effort %s, submitted %s in PR %s "
                 "(`%s`)."
                 % (p["model_label"], p["agent"], p["agent_version"], p["reasoning_effort"],
                    p["date"], p["pr"], p["submission_file"]))
    lines.append("")
    lines.append("| Input | Value |")
    lines.append("|---|---|")
    lines.append("| trials | %d |" % p["n_trials"])
    lines.append("| uncached input tokens | %d |" % p["uncached_input_tokens"])
    lines.append("| cached input tokens (excluded) | %d |" % p["cached_input_tokens"])
    lines.append("| output tokens | %d |" % p["output_tokens"])
    lines.append("| reported total cost (USD) | %.2f |" % p["total_cost_usd"])
    lines.append("| resolution rate (%%) | %.2f |" % p["accuracy_pct"])
    lines.append("| standard error (pp) | %.2f |" % p["accuracy_stderr_pct"])
    lines.append("| disqualified trials | %d |" % p["disqualified_trials"])
    lines.append("| mean trial duration (s) | %.1f |" % p["avg_trial_duration_sec"])
    lines.append("")
    lines.append("counted tokens = %d + %d = %d; per trial %d / %d = **%.4f**."
                 % (p["uncached_input_tokens"], p["output_tokens"], p["counted_tokens_total"],
                    p["counted_tokens_total"], p["n_trials"], p["counted_tokens_per_trial"]))
    lines.append("")
    lines.append("compute_flops = %.4f x %.4g = **%.6g**."
                 % (p["counted_tokens_per_trial"], p["flops_per_token"], p["compute_flops"]))
    lines.append("")
    lines.append("ai_cost_usd = %.2f / %d = **%.5f**, `reported`, dated %s."
                 % (p["total_cost_usd"], p["n_trials"], p["cost_per_trial_usd"], p["date"]))
    lines.append("")
    lines.append("Cache structure: cached input is %.2f times uncached input, and uncached "
                 "input is %.2f times output. Ratio to the human baseline %.3f, so `%s` on the "
                 "0.85 to 1.15 match band. Omitted attention term %.2f-%.2fx the recorded value."
                 % (p["cached_to_uncached_ratio"], p["uncached_to_output_ratio"],
                    p["ratio_to_human"], p["label"], lo, hi))
    lines.append("")
    return "\n".join(lines)


def aa(p, ht):
    lo, hi = attention(p["counted_tokens_per_trial"], p["flops_per_token"])
    lines = []
    lines.append("### %s" % p["point_id"])
    lines.append("")
    lines.append("Artificial Analysis model slug `%s` (%s, %s), Terminus 2 in an e2b sandbox, "
                 "3 repeats of each of the 89 tasks." % (p["aa_slug"], p["aa_name"], p["creator"]))
    lines.append("")
    lines.append("| Input | Value |")
    lines.append("|---|---|")
    lines.append("| trials | %d |" % p["trials"])
    lines.append("| input tokens (gross) | %d |" % p["input_tokens"])
    lines.append("| cacheable input tokens (excluded) | %d |" % p["cacheable_input_tokens"])
    lines.append("| answer tokens | %d |" % p["answer_tokens"])
    lines.append("| reasoning tokens | %d |" % p["reasoning_tokens"])
    lines.append("| published cache hit rate | %s |"
                 % ("%.6f" % p["cache_hit_rate"] if p["cache_hit_rate"] is not None else "not published"))
    lines.append("| resolution rate (%%) | %.2f |" % p["accuracy_pct"])
    lines.append("| binomial standard error (pp) | %.2f |" % p["binomial_stderr_pct"])
    lines.append("")
    lines.append("uncached input = %d - %d = %d; counted tokens = %d + %d + %d = %d; per "
                 "trial %d / %d = **%.4f**."
                 % (p["input_tokens"], p["cacheable_input_tokens"], p["uncached_input_tokens"],
                    p["uncached_input_tokens"], p["answer_tokens"], p["reasoning_tokens"],
                    p["counted_tokens_total"], p["counted_tokens_total"], p["trials"],
                    p["counted_tokens_per_trial"]))
    lines.append("")
    lines.append("compute_flops = %.4f x %.4g = **%.6g**."
                 % (p["counted_tokens_per_trial"], p["flops_per_token"], p["compute_flops"]))
    lines.append("")
    if p["counted_tokens_per_trial_at_hit_rate"] is not None:
        lines.append("Treating the share the published hit rate says missed cache as fresh gives "
                     "%.4f tokens per trial instead, %.1f%% higher; the row takes the "
                     "straightforward figure and states this in notes."
                     % (p["counted_tokens_per_trial_at_hit_rate"],
                        100.0 * (p["counted_tokens_per_trial_at_hit_rate"] / p["counted_tokens_per_trial"] - 1)))
        lines.append("")
    cost_clause = ("ai_cost_usd = **%.5f** per trial, `list_price` at the rates Artificial "
                   "Analysis publishes for this model, dated 2026-09-13 because the board gives "
                   "no run date." % p["cost_per_trial_usd"]) if p["cost_per_trial_usd"] is not None \
        else ("The board publishes no price fields for this model, so the cost columns are "
              "empty and `ai_cost_basis` is `not_available`.")
    lines.append("%s Ratio to the human baseline %.3f, so `%s`. Omitted attention term "
                 "%.2f-%.2fx the recorded value."
                 % (cost_clause, p["ratio_to_human"], p["label"], lo, hi))
    lines.append("")
    return "\n".join(lines)


def astra(a):
    lo, hi = attention(a["counted_tokens_per_task"], a["flops_per_token"])
    A = a["readings"]["A_artificial_analysis_mix"]
    B = a["readings"]["B_vals_own_tb21_cell"]
    ht = a["human_time"]
    L = []
    L.append("### %s" % a["point_id"])
    L.append("")
    L.append("GPT-6 Astra under Terminus 2 in a fixed configuration on the Vals AI "
             "Terminal-Bench-Science 0.1 board, one graded run on each of the 70 tasks, board "
             "updated 2026-09-11. Built on the coordinator's 2026-09-13 ruling; reworked in "
             "Revision 1 to carry two donor readings of the cache structure. This is the only "
             "cell on either Terminal-Bench-Science board that clears the half-of-human guide.")
    L.append("")
    L.append("| Input | Value | Source |")
    L.append("|---|---|---|")
    L.append("| tasks resolved | %d of %d | Vals AI science board `accuracy` %.3f%% |"
             % (a["passes"], a["trials"], a["accuracy_pct"]))
    L.append("| cost per task (USD) | %.6f | Vals AI science board `cost_per_test` |" % a["cost_per_task_usd"])
    L.append("| mean latency (s) | %.1f | Vals AI science board `latency` |" % a["mean_latency_sec"])
    L.append("| list prices (USD per million) | %.2f input, %.2f cached, %.2f output | `research/cost/list-prices.csv`, window opening 2026-09-03 |"
             % tuple(a["prices_usd_per_m"]))
    L.append("| donor uncached input | %d | Artificial Analysis Terminal-Bench v2.1, slug gpt-6-astra |" % a["donor_uncached"])
    L.append("| donor cache reads | %d | the same record's `cacheableInput` |" % a["donor_cache_reads"])
    L.append("| donor output | %d | the same record's `answer` plus `reasoning` |" % a["donor_output"])
    L.append("| same operator, Terminal-Bench 2.1 | $%.6f per task | Vals AI Terminal-Bench 2.1 board, updated 2026-09-10 |" % a["vals_tb21_cost_per_task_usd"])
    L.append("| mean author expert estimate | %.6f h | 70 of 70 `expert_time_estimate_hours` |" % ht["expert_mean_hours"])
    L.append("")
    L.append("**Human time.** All 70 tasks carry an author estimate. Mean %.4f h, median %.1f h, "
             "geometric mean %.3f h, range %.1f to %.1f h, total %.1f h. %.6f h x 3600 = "
             "**%.2f s**. The field is defined as it is in Terminal-Bench 2.1, and the sibling "
             "benchmark's contributing guide glosses it as \"best-case hours for a focused domain "
             "expert\", so `source_estimate` and `human_skill = expert`."
             % (ht["expert_mean_hours"], ht["expert_median_hours"], ht["expert_geomean_hours"],
                ht["expert_min_hours"], ht["expert_max_hours"], ht["expert_sum_hours"],
                ht["expert_mean_hours"], ht["expert_mean_sec"]))
    L.append("")
    L.append("**Compute.** The board publishes a dollar figure and no tokens, so")
    L.append("")
    L.append("```")
    L.append("cost_per_task = (p_in*U + p_cached*C + p_out*O) / 1e6")
    L.append("```")
    L.append("")
    L.append("has three unknowns and needs two ratios: k = U/O and m = C/(U+O). k comes from the "
             "same model's Artificial Analysis Terminal-Bench 2.1 record, GPT-6 Astra under the "
             "same Terminus 2 harness: %d / %d = **%.4f**. m is the contested one, and two donors "
             "give irreconcilable answers."
             % (a["donor_uncached"], a["donor_output"], a["k_uncached_over_output"]))
    L.append("")
    L.append("*Reading A, the Artificial Analysis mix.* That record's own m is %d / %d = "
             "**%.4f**." % (a["donor_cache_reads"], a["donor_uncached"] + a["donor_output"],
                            A["m_at_tb21_length"]))
    L.append("")
    L.append("*Reading B, this operator's own Terminal-Bench 2.1 cell.* Vals runs the same 89 "
             "tasks and bills **$%.6f** per task. Artificial Analysis's measured volume for the "
             "same model on the same tasks costs **$%.4f** per trial at these rates with the "
             "cache discount its own split implies, and **$%.5f** priced gross with no discount "
             "at all. Vals therefore bills **%.2fx** the discounted figure and **%.2fx** the "
             "gross one — it is charging more than every token that volume contains would cost "
             "at the undiscounted input rate. Requiring Vals' dollars to cover Artificial "
             "Analysis's counted tokens puts the missing money on cache reads: m = **%.3f**, "
             "sixteen times Reading A's."
             % (a["vals_tb21_cost_per_task_usd"], a["aa_tb21_gross_cost_per_trial_usd"],
                a["aa_tb21_undiscounted_cost_per_trial_usd"],
                a["vals_over_aa_tb21_cost_ratio"], a["vals_over_aa_tb21_undiscounted_ratio"],
                a["m_implied_by_vals_tb21_cell"]))
    L.append("")
    L.append("The published fields do not choose between them. Reading A says Vals simply "
             "processes about 3.6x the tokens at the donor's mix, which its own error re-attempts "
             "and a longer agent budget would produce; Reading B says Vals' deployment caches far "
             "more aggressively or is billed on a different basis. Neither is privileged, so the "
             "central is their geometric mean, as DECISIONS requires for cost-inverted compute "
             "with a transferred cache structure.")
    L.append("")
    L.append("Each reading is itself bracketed on the benchmark-length growth in m. Three models "
             "appear on both Terminal-Bench boards, so that growth is measurable:")
    L.append("")
    L.append("| Model | m on Terminal-Bench 2.1 | m on Terminal-Bench-Science | growth |")
    L.append("|---|---|---|---|")
    for gr in a["length_growth_detail"]:
        L.append("| %s | %.2f | %.2f | %.3f |" % (gr["model"], gr["m_tb21"], gr["m_tbscience"], gr["growth"]))
    L.append("")
    L.append("Geometric mean growth **%.4f** (range %.2f to %.2f). Each reading is evaluated at "
             "its own m and at m times that factor:"
             % (a["length_growth_factor"],
                min(gr["growth"] for gr in a["length_growth_detail"]),
                max(gr["growth"] for gr in a["length_growth_detail"])))
    L.append("")
    L.append("| Reading | m | m x g | counted at m | counted at m x g | geometric mean |")
    L.append("|---|---|---|---|---|---|")
    for nm, R in (("A, Artificial Analysis mix", A), ("B, Vals' own 2.1 cell", B)):
        L.append("| %s | %.3f | %.3f | %.0f | %.0f | **%.0f** |"
                 % (nm, R["m_at_tb21_length"], R["m_at_science_length"],
                    R["transfer_1_no_length_correction"]["counted"],
                    R["transfer_2_length_corrected"]["counted"],
                    R["counted_tokens_per_task"]))
    L.append("")
    L.append("Central: sqrt(%.0f x %.0f) = **%.2f** counted tokens per task. compute_flops = "
             "%.2f x %.4g = **%.6g**, band %.3e to %.3e across all four cells."
             % (A["counted_tokens_per_task"], B["counted_tokens_per_task"],
                a["counted_tokens_per_task"], a["counted_tokens_per_task"],
                a["flops_per_token"], a["compute_flops"],
                a["band_flops"][0], a["band_flops"][1]))
    L.append("")
    L.append("**The growth factor is not the sensitive parameter; m is.** Holding Reading A and "
             "varying g over a sixfold range moves the result 1.4x: %s. A ten per cent error in "
             "the cached rate moves it about five per cent. The two m readings, by contrast, are "
             "4.8x apart in the result. The alarm in the probe section below about a 45x "
             "collapse is a property of the probe's single-transfer inversion of the official "
             "science board, not of this row."
             % ", ".join("g = %.2f gives %.3g" % (x["g"], x["flops"]) for x in a["growth_sensitivity"]))
    L.append("")
    L.append("**Cross-checks.** Artificial Analysis measures GPT-6 Astra and GPT-5.6 Sol within "
             "6%% of each other in counted tokens per trial on Terminal-Bench 2.1 (ratio %.3f). "
             "Scaling Sol's independently inverted Terminal-Bench-Science figure by that ratio "
             "gives %.0f counted tokens per task, but Sol ran under Codex; the four official "
             "pairs that run one model under both Terminus 2 and its own lab's CLI put a "
             "Terminus 2 run at %s of the CLI run, so the reading becomes %.0f to %.0f. The "
             "central of %.0f sits below that band, which is what Reading B pulls it to. The "
             "implied output rate is %.1f to %.1f tokens per second against the board's %.0f s "
             "mean latency; the low end is Reading B's length-corrected cell and is slow for "
             "this model, which is the clearest single argument against that corner."
             % (a["crosscheck_astra_to_sol_ratio_tb21"], a["crosscheck_counted_per_task"],
                ", ".join("%.3f (%s)" % (x["ratio"], x["model"]) for x in a["terminus2_vs_cli_pairs"]),
                a["crosscheck_band_counted_per_task"][0], a["crosscheck_band_counted_per_task"][1],
                a["counted_tokens_per_task"], a["implied_output_tokens_per_sec"][0],
                a["implied_output_tokens_per_sec"][1], a["mean_latency_sec"]))
    L.append("")
    L.append("**Judgments.** `task_category = research_analysis` rather than `coding`: the "
             "deliverable is often code, but `COLUMNS.md` asks for the whole task, and the whole "
             "task is scientific research work whose binding skill is domain expertise, which is "
             "why the benchmark files tasks under astronomy, ocean sciences and neuroscience. "
             "Ratio to the human baseline %.3f, below the 0.85 match band, so `below`. "
             "`ai_cost_basis = reported`, the board's own figure, but cost and compute are not "
             "independent on this row because the compute was inverted from the cost, flagged as "
             "the GDPval and Remote Labor Index rows are. Vals re-attempts tasks that end in an "
             "infrastructure error and never re-runs a graded result, so the resolution rate is "
             "one-sidedly inflated and the runs behind the per-task dollar exceed 70; "
             "`ai_attempts` counts the 70 tasks. Omitted attention term %.2f-%.2fx the recorded "
             "value." % (a["ratio_to_human"], lo, hi))
    L.append("")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--calculations", required=True)
    args = ap.parse_args()
    data = json.load(open(args.calculations))
    ht = data["human_time"]
    out = []
    for p in sorted(data["points"], key=lambda r: r["point_id"]):
        out.append(official(p, ht) if p["source"] == "official leaderboard" else aa(p, ht))
    if "tbscience_astra" in data:
        out.append(astra(data["tbscience_astra"]))
    print("\n".join(out))


if __name__ == "__main__":
    main()
