#!/usr/bin/env python3
"""Invert OmegaUse-OfficeVal's published cost per task into processed token
positions and FLOPs for each of the five evaluated agents.

OmegaUse-OfficeVal (arXiv:2607.27155v2, Table 3) publishes dollars per task and
wall-clock hours per task and no token counts, so the compute has to be inverted
from the bill.  The inversion needs a cache structure, transferred from agentic
runs of the same model endpoint that do publish one (build_donor_structures.py).
Two parameters are transferred:

  h   = served cache reads / gross prompt positions
  rho = output tokens / freshly processed input positions

With F freshly processed input positions, served cache S = F*h/(1-h) and output
O = rho*F, the bill per task is

  cost = [ F*P_in + S*P_cached + O*P_out ] / 1e6

so F = cost*1e6 / ( P_in + (h/(1-h))*P_cached + rho*P_out ), and the dataset's
counted positions (fresh input + cache creation + output, cache reads excluded)
are B = F*(1+rho).  FLOPs = 2*active_parameters*B.

Each branch structure gives one B.  The central is the geometric mean of the
lowest and the highest branch, following the folder's rule for two defensible
transfers that disagree; a single-branch agent takes that branch and carries the
h sensitivity instead.  The geometric mean of every branch is reported alongside,
since the folder's rule names two transfers and up to four are available here.
Scenarios recompute B under the stated alternatives.  An independent cross-check
rescales the Epoch donor's billed positions per second of agent working time by
OmegaUse's wall clock per task.

Qwen3.7-Plus is computed but not emitted as a row (build_row False): Alibaba
prices it in a thinking and a non-thinking mode whose input rates differ
four-fold, and the paper does not say which ran.  Its numbers are kept here so
the disposition is reproducible.

Usage:
  python3 compute_omegause.py \
      --donors <path>/donor-structures.csv \
      --prices <path>/omegause-prices-run-window.csv \
      --table3 <path>/omegause-table3.csv \
      --tasks  <path>/omegause-human-labor-time.csv \
      --out    <path>/calculations.json

Dependencies: Python 3.8+ standard library only.
"""
import argparse, csv, json, math

AGENTS = {
    "GLM-5.2": dict(
        model_id="glm-5.2", active=40e9, donor_models=["glm-5.2"],
        extra_branches=[], xcheck="glm-5.2", build_row=True),
    "Qwen3.7-Plus": dict(
        # No same-model donor exists: Qwen3.7 was never released open-weight and
        # neither Epoch nor Artificial Analysis ran the Plus alias.  Branch 1 is
        # the same provider's sibling as Epoch measured it; branch 2 raises h to
        # the level the other four providers' automatic caches reach in the same
        # donor family, which is what Alibaba's default implicit cache should do.
        model_id="qwen3.7-plus", active=17e9, donor_models=["qwen3.7-max"],
        extra_branches=[("assumed-implicit-reuse-h095", 0.95, "qwen3.7-max")],
        xcheck="qwen3.7-max", build_row=False),
    "Kimi K2.6": dict(
        model_id="kimi-k2.6", active=32e9, donor_models=["kimi-k2.6"],
        extra_branches=[], xcheck="kimi-k2.6", build_row=True),
    "DeepSeek-V4-Pro": dict(
        model_id="deepseek-v4-pro-preview", active=49e9,
        donor_models=["deepseek-v4-pro-preview", "deepseek-v4-pro-0813"],
        extra_branches=[], xcheck="deepseek-v4-pro-preview", build_row=True),
    "Minimax M3": dict(
        model_id="minimax-m3", active=23e9, donor_models=["minimax-m3"],
        extra_branches=[], xcheck=None, build_row=True),
}
# Artificial Analysis reports eligible, not served, cache tokens.  Branches use
# complete reuse of the eligible prefix, which is what Epoch measures directly on
# three of these five providers (h = 0.89-0.98 of gross prompt positions); the
# 0.60 achieved share that agent-work/sources/apex-agents/harness-and-provider-caching.md
# inverts out of Lumer et al.'s Gemini 2.5 Pro and GPT-5.2 measurements is
# carried as a scenario instead.
AA_BRANCH_SHARE = 1.0
AA_SCENARIO_SHARE = 0.6
H_SENSITIVITY = (0.85, 0.99)
# Alternative price sheets, applied as scenarios.  Each entry is
# (label, {input/cached/output overrides}).
PRICE_SCENARIOS = {
    "qwen3.7-plus": [
        ("thinking-mode-rate-implicit-cache", dict(input=1.60, cached=0.32, output=1.60)),
        ("thinking-mode-rate-cache-held", dict(input=1.60, cached=0.08, output=1.60)),
        ("non-thinking-explicit-cache-rate", dict(cached=0.04)),
    ],
    "deepseek-v4-pro-preview": [
        ("off-peak-half-rate", dict(input=0.66, cached=0.022, output=1.98)),
    ],
    "minimax-m3": [
        ("undiscounted-sheet", dict(input=0.60, cached=0.12, output=2.40)),
    ],
}
# Providers that double the rate above a prompt-length threshold.  Under the
# linear-growth context model used by attention_scenarios.py, a run whose final
# context is N_final bills the fraction (N_final - T)/N_final of its calls, and
# 1 - (T/N_final)^2 of its served-cache volume, at the upper tier.
LONG_CONTEXT_TIER = {"minimax-m3": dict(threshold=512000, multiplier=2.0)}


def fresh_positions(cost_usd, h, rho, p_in, p_cached, p_out):
    """Freshly processed input positions implied by the bill, and the unit price."""
    amp = h / (1.0 - h)
    unit = p_in + amp * p_cached + rho * p_out
    return cost_usd * 1e6 / unit, unit


def gross_priced_positions(cost_usd, h, rho, p_in, p_out):
    """Same structure if the source priced gross prompt tokens at the full input
    rate, i.e. applied no cache discount at all."""
    unit = p_in / (1.0 - h) + rho * p_out
    return cost_usd * 1e6 / unit


def main():
    ap = argparse.ArgumentParser()
    for f in ("donors", "prices", "table3", "tasks", "out"):
        ap.add_argument("--" + f, required=True)
    a = ap.parse_args()

    donors = list(csv.DictReader(open(a.donors, newline="", encoding="utf-8-sig")))
    prices = {r["model_id"]: r for r in
              csv.DictReader(open(a.prices, newline="", encoding="utf-8-sig"))}
    table3 = {r["agent"]: r for r in
              csv.DictReader(open(a.table3, newline="", encoding="utf-8-sig"))}
    tasks = list(csv.DictReader(open(a.tasks, newline="", encoding="utf-8-sig")))

    times = sorted(int(t["human_labor_time_min"]) for t in tasks)
    n = len(times)
    human = {
        "n_tasks": n,
        "mean_minutes": sum(times) / n,
        "median_minutes": (times[n // 2 - 1] + times[n // 2]) / 2 if n % 2 == 0 else times[n // 2],
        "min_minutes": times[0], "max_minutes": times[-1],
        "mean_seconds": sum(times) / n * 60.0,
        "contributing_attempts": 2 * n,   # H_t averages the two shortest valid times
    }
    human_score = float(table3["Human"]["score"])
    out = {"human_baseline": human, "human_score": human_score,
           "aa_branch_share": AA_BRANCH_SHARE, "agents": {}}

    for agent, cfg in AGENTS.items():
        row = table3[agent]
        cost, hours, score = (float(row["cost_per_task_usd"]),
                              float(row["time_per_task_hours"]),
                              float(row["score"]))
        pr = prices[cfg["model_id"]]
        p_in, p_cached, p_out = (float(pr["input_usd_per_m"]),
                                 float(pr["cached_input_usd_per_m"]),
                                 float(pr["output_usd_per_m"]))
        active = cfg["active"]

        structures = []
        for d in donors:
            if d["model_id"] not in cfg["donor_models"]:
                continue
            share = d["served_share_of_eligible"]
            if share != "measured" and abs(float(share) - AA_BRANCH_SHARE) > 1e-9:
                continue
            structures.append((f'{d["donor"]}:{d["donor_detail"]}', float(d["h"]),
                               float(d["rho"]), share))
        for label, h, rho_from in cfg["extra_branches"]:
            rho = next(float(d["rho"]) for d in donors
                       if d["model_id"] == rho_from and d["donor"] == "epoch-swebench-verified")
            structures.append((label, h, rho, "constructed"))

        branches = []
        for label, h, rho, share in structures:
            F, unit = fresh_positions(cost, h, rho, p_in, p_cached, p_out)
            branches.append(dict(structure=label, served_share_of_eligible=share,
                                 h=h, rho=rho, usd_per_million_fresh=unit,
                                 fresh_input_tokens=F, output_tokens=rho * F,
                                 served_cache_tokens=F * h / (1 - h),
                                 billed_tokens=F * (1 + rho),
                                 flops=2 * active * F * (1 + rho)))
        lo = min(b["billed_tokens"] for b in branches)
        hi = max(b["billed_tokens"] for b in branches)
        central_B = math.sqrt(lo * hi)
        all_branch_gm = math.exp(sum(math.log(b["billed_tokens"]) for b in branches)
                                 / len(branches))

        # structure implied at the central, holding rho at the branch mean
        rho_bar = sum(b["rho"] for b in branches) / len(branches)
        F_c = central_B / (1 + rho_bar)
        unit_c = cost * 1e6 / F_c
        amp_c = (unit_c - p_in - rho_bar * p_out) / p_cached
        h_c = amp_c / (1 + amp_c) if amp_c > 0 else 0.0

        ref = min(branches, key=lambda b: abs(b["h"] - 0.95))
        scen = {}
        for hs in H_SENSITIVITY:
            F, _ = fresh_positions(cost, hs, ref["rho"], p_in, p_cached, p_out)
            scen[f"h_{hs}"] = dict(h=hs, billed_tokens=F * (1 + ref["rho"]),
                                   flops=2 * active * F * (1 + ref["rho"]))
        aa_lo = [d for d in donors if d["model_id"] in cfg["donor_models"]
                 and d["served_share_of_eligible"] != "measured"
                 and abs(float(d["served_share_of_eligible"]) - AA_SCENARIO_SHARE) < 1e-9]
        if aa_lo:
            vals = []
            for d in aa_lo:
                F, _ = fresh_positions(cost, float(d["h"]), float(d["rho"]), p_in, p_cached, p_out)
                vals.append(F * (1 + float(d["rho"])))
            scen["aa_served_share_0.6"] = dict(
                billed_tokens_low=min(vals), billed_tokens_high=max(vals),
                flops_low=2 * active * min(vals), flops_high=2 * active * max(vals))
        Fg = gross_priced_positions(cost, ref["h"], ref["rho"], p_in, p_out)
        scen["no_cache_discount_in_reported_cost"] = dict(
            h=ref["h"], rho=ref["rho"], billed_tokens=Fg * (1 + ref["rho"]),
            flops=2 * active * Fg * (1 + ref["rho"]))
        for name, over in PRICE_SCENARIOS.get(cfg["model_id"], []):
            q_in, q_cached, q_out = (over.get("input", p_in), over.get("cached", p_cached),
                                     over.get("output", p_out))
            vals = []
            for label, h, rho, _s in structures:
                F, _ = fresh_positions(cost, h, rho, q_in, q_cached, q_out)
                vals.append(F * (1 + rho))
            scen[name] = dict(prices=dict(input=q_in, cached_input=q_cached, output=q_out),
                              billed_tokens_low=min(vals), billed_tokens_high=max(vals),
                              billed_tokens_central=math.sqrt(min(vals) * max(vals)),
                              flops_central=2 * active * math.sqrt(min(vals) * max(vals)))
        if cfg["model_id"] in LONG_CONTEXT_TIER:
            t = LONG_CONTEXT_TIER[cfg["model_id"]]
            n_final = F_c                      # fresh input equals the final context
            if n_final > t["threshold"]:
                call_share = (n_final - t["threshold"]) / n_final
                vol_share = 1.0 - (t["threshold"] / n_final) ** 2
                k = t["multiplier"] - 1.0
                unit_tier = (p_in * (1 + k * call_share)
                             + amp_c * p_cached * (1 + k * vol_share)
                             + rho_bar * p_out * (1 + k * call_share))
                B_tier = cost * 1e6 / unit_tier * (1 + rho_bar)
                scen["long_context_tier"] = dict(
                    threshold=t["threshold"], final_context_tokens=n_final,
                    share_of_calls_above=call_share, share_of_cache_volume_above=vol_share,
                    billed_tokens=B_tier, flops=2 * active * B_tier,
                    ratio_to_central=B_tier / central_B)

        cross = None
        if cfg["xcheck"]:
            d = next(x for x in donors if x["model_id"] == cfg["xcheck"]
                     and x["donor"] == "epoch-swebench-verified")
            rate = float(d["billed_per_working_second"])
            cross = dict(donor=d["donor_detail"], donor_billed_per_working_second=rate,
                         omegause_wall_clock_s_per_task=hours * 3600.0,
                         implied_billed_tokens=rate * hours * 3600.0)
            cross["ratio_to_central"] = cross["implied_billed_tokens"] / central_B
            cross["ratio_to_gross_priced"] = (cross["implied_billed_tokens"]
                / scen["no_cache_discount_in_reported_cost"]["billed_tokens"])

        out["agents"][agent] = dict(
            model_id=cfg["model_id"], build_row=cfg["build_row"],
            active_parameters=active, flops_per_token=2 * active,
            cost_usd_per_task=cost, wall_clock_s_per_task=hours * 3600.0,
            score=score, score_ratio_to_human=score / human_score,
            prices_usd_per_m=dict(input=p_in, cached_input=p_cached, output=p_out),
            branches=branches, billed_tokens_low=lo, billed_tokens_high=hi,
            billed_tokens_central=central_B,
            billed_tokens_all_branch_geometric_mean=all_branch_gm,
            flops_low=2 * active * lo, flops_high=2 * active * hi,
            flops_central=2 * active * central_B,
            implied_central_structure=dict(rho=rho_bar, h=h_c,
                                           usd_per_million_fresh=unit_c,
                                           fresh_input_tokens=F_c,
                                           output_tokens=rho_bar * F_c,
                                           served_cache_tokens=F_c * h_c / (1 - h_c)),
            scenarios=scen, throughput_cross_check=cross)

    json.dump(out, open(a.out, "w"), indent=1)
    print("wrote", a.out)
    print(f'{"agent":16s} {"row":>4s} {"B/task":>11s} {"low":>11s} {"high":>11s} {"FLOPs":>10s} '
          f'{"h*":>5s} {"rho*":>5s} {"xchk":>9s} {"/cen":>5s} {"/gross":>6s}')
    for k, v in out["agents"].items():
        c = v["throughput_cross_check"]
        nan = float("nan")
        print(f'{k:16s} {str(v["build_row"]):>4s} {v["billed_tokens_central"]:11,.0f} '
              f'{v["billed_tokens_low"]:11,.0f} {v["billed_tokens_high"]:11,.0f} '
              f'{v["flops_central"]:10.4g} {v["implied_central_structure"]["h"]:5.3f} '
              f'{v["implied_central_structure"]["rho"]:5.3f} '
              f'{(c["implied_billed_tokens"] if c else nan):9,.0f} '
              f'{(c["ratio_to_central"] if c else nan):5.2f} '
              f'{(c["ratio_to_gross_priced"] if c else nan):6.2f}')


if __name__ == "__main__":
    main()
