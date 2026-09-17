#!/usr/bin/env python3
"""Compute the TextQuests rows: FLOPs, tokens, dollar cost and the human suite duration.

Inputs are the retained extracts under agent-work/sources/textquests/ and the shared price table
under research/cost/list-prices.csv. Nothing is read from a candidate folder, a scratch
directory or the sibling Codex project.

Usage:
  python3 research/textquests/compute_textquests.py \
      --sources agent-work/sources/textquests \
      --prices research/cost/list-prices.csv \
      --out research/textquests/calculations.json

Dependencies: Python 3.9+ standard library only.
"""
import argparse, csv, json, os, statistics

MODES = ["no_clues", "with_clues"]
# Table 5 column labels -> model_id in the Codex registry.
MODEL_ID = {
    "o3": "o3-2025-04-16",
    "gemini-2.5-pro": "gemini-2.5-pro",
    "claude-opus-4.0": "claude-opus-4",
    "claude-sonnet-4.0": "claude-sonnet-4",
    "gpt-4.1": "gpt-4.1-2025-04-14",
    "gpt-4.1-mini": "gpt-4.1-mini-2025-04-14",
}
PROVIDER = {
    "o3": "openai", "gpt-4.1": "openai", "gpt-4.1-mini": "openai",
    "gemini-2.5-pro": "google",
    "claude-opus-4.0": "anthropic", "claude-sonnet-4.0": "anthropic",
}
# Table 5 label -> leaderboard "model" field, for progress and completions.
BOARD_NAME = {
    "o3": "o3", "gemini-2.5-pro": "Gemini 2.5 Pro", "claude-opus-4.0": "Claude Opus 4",
    "claude-sonnet-4.0": "Claude Sonnet 4", "gpt-4.1": "GPT-4.1", "gpt-4.1-mini": "GPT-4.1-mini",
}
GAMES = 25
MAX_STEPS = 500
# Attention bracket, the shapes the accepted Portal row uses: 4 * layers * d_model.
ATTENTION_SHAPES = [("L=64, d=8192", 64, 8192), ("L=80, d=10240", 80, 10240), ("L=96, d=12288", 96, 12288)]
PRICE_DATE = "2025-07-31"   # arXiv v1 submission; the runs are complete by then, exact dates unpublished
PAPER_HOURS_PER_GAME = 30.0  # the paper's own anchor, carried as a scenario


def parse_count(text):
    """'531M' -> 531e6, '6.8K' -> 6800, '239' -> 239."""
    t = text.strip()
    mult = {"M": 1e6, "K": 1e3}.get(t[-1], 1.0)
    return float(t[:-1] if mult != 1.0 else t) * mult


def human_suite(ifdb):
    """Suite duration: per-game arithmetic mean of the IFDB votes, games without a vote at the
    mean of the games that have one."""
    per_game, votes, noted = {}, 0, 0
    for game, rec in ifdb["games"].items():
        if rec["votes"]:
            per_game[game] = statistics.fmean(v["seconds"] for v in rec["votes"])
            votes += len(rec["votes"])
            noted += sum(1 for v in rec["votes"] if v["note"])
    timed_mean = statistics.fmean(per_game.values())
    total = sum(per_game.values()) + (GAMES - len(per_game)) * timed_mean
    # How much the seven imputed games can move the suite: place them anywhere from the 10th to
    # the 90th percentile of the eighteen that are timed.
    ordered = sorted(per_game.values())
    def pct(q):
        i = q * (len(ordered) - 1)
        lo = int(i)
        return ordered[lo] + (i - lo) * (ordered[min(lo + 1, len(ordered) - 1)] - ordered[lo])
    imputation = {f"{int(q*100)}th percentile of the timed games":
                  sum(per_game.values()) + (GAMES - len(per_game)) * pct(q)
                  for q in (0.10, 0.25, 0.50, 0.75, 0.90)}
    return {
        "imputation_sensitivity_seconds": imputation,
        "per_game_mean_seconds": per_game,
        "games_with_votes": len(per_game),
        "games_imputed": GAMES - len(per_game),
        "votes": votes,
        "votes_with_hint_note": noted,
        "timed_game_mean_seconds": timed_mean,
        "suite_seconds": total,
        "suite_hours": total / 3600.0,
        "median_of_game_means_seconds": statistics.median(per_game.values()),
        "suite_seconds_from_medians": (
            sum(ifdb["games"][g]["displayed_estimated_play_time_seconds"] for g in per_game)
            + (GAMES - len(per_game)) * statistics.fmean(
                ifdb["games"][g]["displayed_estimated_play_time_seconds"] for g in per_game)),
        "paper_anchor_suite_seconds": PAPER_HOURS_PER_GAME * 3600.0 * GAMES,
    }


def price_lookup(prices, model_id, date):
    best = None
    for r in prices:
        if r["model_id"] != model_id:
            continue
        if r["price_sheet_start"] and r["price_sheet_start"] > date:
            continue
        if r["price_sheet_end"] and r["price_sheet_end"] < date:
            continue
        best = r
    if best is None:
        raise KeyError(f"no price window for {model_id} on {date}")
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", required=True)
    ap.add_argument("--prices", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    tbl = json.load(open(os.path.join(a.sources, "textquests-token-table-2026-09-13.json")))
    board = json.load(open(os.path.join(a.sources, "textquests-leaderboard-2026-09-13.json")))
    ifdb = json.load(open(os.path.join(a.sources, "ifdb-playtimes-2026-09-13.json")))
    coeff = json.load(open(os.path.join(a.sources, "model-coefficients-2026-09-13.json")))["models"]
    ctx = json.load(open(os.path.join(a.sources, "game-context-sizes-2026-09-13.json")))
    with open(a.prices, newline="") as f:
        prices = list(csv.DictReader(f))

    by_name = {e["model"]: e for e in board}
    human = human_suite(ifdb)
    cells = []
    for mode in MODES:
        for label, row in tbl["rows"][mode].items():
            total_in = parse_count(row["total_input"])
            cache = parse_count(row["cache"])
            out_tok = parse_count(row["total_output"])
            processed_in = total_in - cache
            counted = processed_in + out_tok
            fpt = float(coeff[MODEL_ID[label]]["flops_per_token"])
            flops = counted * fpt

            # Table 5 prints three significant figures in millions, so the difference of two
            # such numbers carries up to 1e6 of rounding error in the worst case.
            band = [(processed_in - 1e6) + out_tok, (processed_in + 1e6) + out_tok]

            e = by_name[BOARD_NAME[label]]
            side = e["noClues"] if mode == "no_clues" else e["withClues"]
            progress = side["progress"]
            completed = 0 if mode == "no_clues" else side["completed"]

            # Exclusion rule: ratio to the human's 100 per cent on the benchmark's own metric.
            # The per-game progress values are unpublished, so the standard error of the
            # 25-game mean is bounded by its largest possible value for a variable on [0, 100]:
            # sd <= sqrt(p * (100 - p)).
            max_sd = (progress * (100.0 - progress)) ** 0.5
            max_se_ratio = max_sd / (GAMES ** 0.5) / 100.0
            ratio = progress / 100.0
            se_below = (0.5 - ratio) / max_se_ratio if max_se_ratio else None

            # Nominal call count. It is two-sided, not a bound: finishing a game early removes
            # steps, while a parse failure retries the same history and adds a call whose tokens
            # are already inside the published totals.
            turns = GAMES * MAX_STEPS
            mean_context = cache / turns
            attention = {}
            for name, L, d in ATTENTION_SHAPES:
                attention[name] = counted * (4 * L * d) * mean_context

            p = price_lookup(prices, MODEL_ID[label], PRICE_DATE)
            if PROVIDER[label] == "anthropic":
                # processed_in is uncached input plus cache writes and the split is not
                # published; the harness marks a breakpoint every call, so almost all of it is
                # a cache write. Priced at the write rate, with the all-uncached floor kept.
                cost = (processed_in * float(p["cache_write_usd_per_m"])
                        + cache * float(p["cached_input_usd_per_m"])
                        + out_tok * float(p["output_usd_per_m"])) / 1e6
                cost_floor = (processed_in * float(p["input_usd_per_m"])
                              + cache * float(p["cached_input_usd_per_m"])
                              + out_tok * float(p["output_usd_per_m"])) / 1e6
            else:
                cost = (processed_in * float(p["input_usd_per_m"])
                        + cache * float(p["cached_input_usd_per_m"])
                        + out_tok * float(p["output_usd_per_m"])) / 1e6
                cost_floor = cost

            # Reasoning tokens that a provider may report outside completion_tokens.
            # Google's OpenAI-compatibility layer is the live case: Gemini 2.5 Pro cannot
            # disable thinking, yet its largest single response in the whole suite is 700
            # (No Clues) or 1.4K (With Clues) tokens and its mean is under 220.
            hidden = {f"{n} hidden reasoning tokens per call":
                      (counted + turns * n) * fpt for n in (500, 1000, 2000)}

            cells.append({
                "model_label": label, "mode": mode, "model_id": MODEL_ID[label],
                "provider": PROVIDER[label],
                "total_input_tokens": total_in, "cache_tokens": cache, "output_tokens": out_tok,
                "processed_input_tokens": processed_in, "counted_tokens": counted,
                "counted_tokens_rounding_band": band,
                "flops_per_token": fpt, "compute_flops": flops,
                "compute_flops_rounding_band": [band[0] * fpt, band[1] * fpt],
                "cache_hit_share": cache / total_in,
                "mean_context_tokens_at_500_steps": mean_context,
                "attention_flops_omitted": attention,
                "attention_ratio_to_central": {k: v / flops for k, v in attention.items()},
                "no_cache_exclusion_flops": (total_in + out_tok) * fpt,
                "hidden_reasoning_scenarios": hidden,
                "progress_pct": progress, "completed_games": completed,
                "ratio_to_human_progress": ratio,
                "max_se_of_ratio": max_se_ratio,
                "standard_errors_below_half_guide": se_below,
                "outcome": "row" if ratio >= 0.5 else "not a row",
                "ai_cost_usd": cost, "ai_cost_usd_all_uncached_floor": cost_floor,
                "ai_cost_date": PRICE_DATE,
                "flops_per_human_second": flops / human["suite_seconds"],
            })

    result = {
        "generated_from": {
            "token_table": "agent-work/sources/textquests/textquests-token-table-2026-09-13.json",
            "leaderboard": "agent-work/sources/textquests/textquests-leaderboard-2026-09-13.json",
            "ifdb": "agent-work/sources/textquests/ifdb-playtimes-2026-09-13.json",
            "model_coefficients": "agent-work/sources/textquests/model-coefficients-2026-09-13.json",
            "prices": "research/cost/list-prices.csv",
        },
        "conventions": {
            "counted_tokens": "total input minus cache tokens, plus output; cache reads excluded",
            "attention": "4 * layers * d_model * mean_context per counted token, omitted from compute_flops",
            "price_date": PRICE_DATE,
        },
        "human_scenarios": {
            "central, per-game mean of IFDB votes, 7 games imputed": human["suite_seconds"],
            "IFDB medians instead of means": human["suite_seconds_from_medians"],
            "the paper's own 30 hours a game anchor": human["paper_anchor_suite_seconds"],
            "timed 18 games only, no imputation": sum(human["per_game_mean_seconds"].values()),
        },
        "human": human,
        "repo_context_sizes": {
            "feelies_tokens_total": sum(g["feelies_tokens"] for g in ctx),
            "invisiclues_tokens_total": sum(g["invisiclues_tokens"] for g in ctx),
            "walkthrough_commands_total": sum(g["walkthrough_commands"] for g in ctx),
            "walkthrough_commands_min": min(g["walkthrough_commands"] for g in ctx),
            "walkthrough_commands_max": max(g["walkthrough_commands"] for g in ctx),
        },
        # A player who already knows every solution retypes the optimal walkthroughs. This is a
        # floor on the suite, and the ratio of a candidate human figure to it is a consistency
        # check on whether that figure could be walkthrough-following rather than play.
        "walkthrough_floor": {
            f"{rate} s a command": sum(g["walkthrough_commands"] for g in ctx) * rate
            for rate in (10, 15, 20)},
        "cells": cells,
    }
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(result, open(a.out, "w"), indent=1)
    print(f"human suite: {human['suite_hours']:.3f} h from {human['votes']} votes over "
          f"{human['games_with_votes']} games, {human['games_imputed']} imputed")
    for c in cells:
        print(f"{c['mode']:10} {c['model_label']:18} counted {c['counted_tokens']/1e6:6.1f}M "
              f"flops {c['compute_flops']:.4g} progress {c['progress_pct']:5.1f} "
              f"ratio {c['ratio_to_human_progress']:.3f} se_below {c['standard_errors_below_half_guide']:6.2f} "
              f"{c['outcome']:9} cost ${c['ai_cost_usd']:.0f}")


if __name__ == "__main__":
    main()
