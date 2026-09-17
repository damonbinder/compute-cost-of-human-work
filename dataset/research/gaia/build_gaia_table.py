#!/usr/bin/env python3
"""Join HAL GAIA per-task token usage to the GAIA annotator times and levels.

For every HAL run summary produced by extract_hal_usage.py, and for each GAIA
difficulty level plus the whole validation split, this computes:
  - the number of questions, the agent's accuracy and its binomial standard error
    (accuracy counts every question; per-question compute averages only the
    questions that carry usage, since a task with no logged call is missing
    evidence rather than a task that cost nothing)
  - the mean human annotator solve time
  - mean per-question token counts, split by model, under three accountings
      counted  the dataset's rule: fresh input + cache creation + output,
               cache reads excluded, reasoning included in output
      gross    every prompt token charged again on every call (no cache credit)
      output   generated tokens only
  - mean per-question FLOPs from counted tokens and each model's coefficient
  - the mean prefix length per LLM call, for the cached-context attention scenario
  - mean counted tokens per question split by outcome, since the human timings are
    successful solves by construction while the AI mean averages failures too

Token conventions handled (see the research note):
  OpenAI/OpenRouter  prompt_tokens includes prompt_tokens_details.cached_tokens
                     -> counted input = prompt_tokens - cached_tokens
  Anthropic direct   prompt_tokens excludes cache_creation/cache_read, which are
                     additive -> counted input = prompt_tokens + cache_creation
  In every HAL GAIA run cache_creation and cache_read are zero: the harness sets
  no cache_control, so no Anthropic prompt caching occurred.

Dependencies: none beyond the standard library.

Usage:
    python3 build_gaia_table.py <run_summaries_dir> <annotator_times_csv> \
        <models_csv>[,<models_csv>...] <out_json> <out_csv>
"""
import csv
import json
import math
import os
import sys
from collections import defaultdict

# HAL usage model name -> dataset model_id. Names are the litellm/openrouter
# strings that appear in the traces.
MODEL_ID_MAP = {
    "o3-mini-2025-01-31": "o3-mini-2025-01-31",
    "o4-mini-2025-04-16": "o4-mini-2025-04-16",
    "o3-2025-04-16": "o3-2025-04-16",
    "gpt-4.1-2025-04-14": "gpt-4.1-2025-04-14",
    "gpt-5-2025-08-07": "gpt-5",
    "gpt-4o-2024-11-20": "gpt-4o-2024-11-20",
    "claude-3-7-sonnet-20250219": "claude-3-7-sonnet",
    "claude-opus-4-20250514": "claude-opus-4",
    "anthropic/claude-opus-4": "claude-opus-4",
    "anthropic/claude-opus-4.1": "claude-opus-4-1",
    "anthropic/claude-sonnet-4.5": "claude-sonnet-4-5",
    "claude-sonnet-4-5-20250929": "claude-sonnet-4-5",
    "anthropic/claude-haiku-4.5": "claude-haiku-4-5",
    "claude-haiku-4-5-20251001": "claude-haiku-4-5",
    "deepseek-ai/DeepSeek-R1": "deepseek-r1",
    "deepseek-ai/DeepSeek-V3": "deepseek-v3",
    "deepseek/deepseek-chat-v3-0324": "deepseek-v3-0324",
    "gemini-2.0-flash": "gemini-2.0-flash-001",
    "gemini/gemini-2.0-flash": "gemini-2.0-flash-001",
    "gemini-2.0-flash-001": "gemini-2.0-flash-001",
}


def load_coefficients(paths):
    coef = {}
    for path in paths:
        with open(path) as fh:
            for row in csv.DictReader(fh):
                try:
                    coef[row["model_id"]] = float(row["flops_per_token"])
                except (TypeError, ValueError):
                    pass
    return coef


def counted_tokens(u):
    """Dataset rule: fresh input + cache creation + output; cache reads excluded."""
    prompt = u.get("prompt_tokens", 0)
    cached = u.get("cached_tokens", 0)  # OpenAI-style subset of prompt_tokens
    creation = u.get("cache_creation_input_tokens", 0)  # Anthropic-style, additive
    return (prompt - cached) + creation + u.get("completion_tokens", 0)


def main(summary_dir, times_csv, models_csvs, out_json, out_csv):
    coef = load_coefficients(models_csvs.split(","))

    level = {}
    human_s = {}
    with open(times_csv) as fh:
        for row in csv.DictReader(fh):
            level[row["task_id"]] = int(row["level"])
            human_s[row["task_id"]] = float(row["seconds"])

    runs = []
    for name in sorted(os.listdir(summary_dir)):
        if not name.endswith(".json") or name.startswith("_"):
            continue
        with open(os.path.join(summary_dir, name)) as fh:
            s = json.load(fh)
        if not s.get("per_task_usage"):
            continue  # slim upload: run-level usage only
        scored = s.get("raw_eval_results") or {}
        cfg = s["config"]
        run = {
            "run_id": cfg["run_id"],
            "agent_name": cfg["agent_name"],
            "agent_dir": "open_deep_research"
            if "open_deep_research" in cfg.get("run_command", "")
            else "hal_generalist_agent",
            "date": cfg["date"],
            "agent_args": cfg.get("agent_args"),
            "git_info": s.get("git_info"),
            "run_accuracy": (s.get("results") or {}).get("accuracy"),
            "call_counts": s.get("call_counts"),
            "levels": {},
        }
        by_level = defaultdict(
            lambda: {
                "n": 0,
                "n_scored_true": 0,
                "n_missing_usage": 0,
                "usage": defaultdict(lambda: defaultdict(int)),
                "counted_solved": 0,
                "counted_failed": 0,
                "n_solved_with_usage": 0,
                "n_failed_with_usage": 0,
            }
        )
        for task_id, lv in level.items():
            usage = s["per_task_usage"].get(task_id)
            for key in (lv, "all"):
                b = by_level[key]
                b["n"] += 1
                sc = scored.get(task_id)
                if isinstance(sc, dict) and sc.get("score"):
                    b["n_scored_true"] += 1
                if not usage:
                    b["n_missing_usage"] += 1
                    continue
                task_counted = 0
                for m, u in usage.items():
                    for k, v in u.items():
                        b["usage"][m][k] += v
                    task_counted += counted_tokens(u)
                solved = isinstance(sc, dict) and bool(sc.get("score"))
                b["counted_solved" if solved else "counted_failed"] += task_counted
                b["n_solved_with_usage" if solved else "n_failed_with_usage"] += 1

        for key, b in by_level.items():
            sel = [t for t, lv in level.items() if key == "all" or lv == key]
            times = [human_s[t] for t in sel]
            acc = b["n_scored_true"] / b["n"]
            per_model = {}
            flops = 0.0
            tot_counted = tot_gross = tot_output = tot_prompt = 0
            calls = 0
            unknown = []
            for m, u in b["usage"].items():
                mid = MODEL_ID_MAP.get(m)
                c = counted_tokens(u)
                g = u.get("prompt_tokens", 0) + u.get(
                    "cache_creation_input_tokens", 0
                ) + u.get("cache_read_input_tokens", 0) + u.get("completion_tokens", 0)
                per_model[m] = {
                    "model_id": mid,
                    "flops_per_token": coef.get(mid),
                    "counted_tokens": c,
                    "gross_tokens": g,
                    "prompt_tokens": u.get("prompt_tokens", 0),
                    "cached_tokens": u.get("cached_tokens", 0),
                    "cache_creation_input_tokens": u.get(
                        "cache_creation_input_tokens", 0
                    ),
                    "cache_read_input_tokens": u.get("cache_read_input_tokens", 0),
                    "completion_tokens": u.get("completion_tokens", 0),
                    "reasoning_tokens": u.get("reasoning_tokens", 0),
                    "calls": u.get("calls", 0),
                }
                tot_counted += c
                tot_gross += g
                tot_output += u.get("completion_tokens", 0)
                tot_prompt += u.get("prompt_tokens", 0)
                calls += u.get("calls", 0)
                if mid is None or coef.get(mid) is None:
                    unknown.append(m)
                else:
                    flops += c * coef[mid]
            n_obs = b["n"] - b["n_missing_usage"]
            run["levels"][str(key)] = {
                "n_questions": b["n"],
                "n_missing_usage": b["n_missing_usage"],
                "n_with_usage": n_obs,
                "accuracy": acc,
                "accuracy_se": math.sqrt(acc * (1 - acc) / b["n"]),
                "human_mean_s": sum(times) / len(times),
                "human_median_s": sorted(times)[len(times) // 2],
                "counted_tokens_total": tot_counted,
                "counted_tokens_per_question": tot_counted / n_obs,
                "counted_tokens_per_question_all_denom": tot_counted / b["n"],
                "gross_tokens_per_question": tot_gross / n_obs,
                "output_tokens_per_question": tot_output / n_obs,
                "llm_calls_per_question": calls / n_obs,
                "mean_prefix_tokens_per_call": (tot_prompt / calls) if calls else 0,
                "flops_total": flops,
                "flops_per_question": flops / n_obs,
                "n_solved_with_usage": b["n_solved_with_usage"],
                "n_failed_with_usage": b["n_failed_with_usage"],
                "counted_tokens_per_solved_question": (
                    b["counted_solved"] / b["n_solved_with_usage"]
                    if b["n_solved_with_usage"] else None
                ),
                "counted_tokens_per_failed_question": (
                    b["counted_failed"] / b["n_failed_with_usage"]
                    if b["n_failed_with_usage"] else None
                ),
                "models_without_coefficient": sorted(set(unknown)),
                "per_model": per_model,
            }
        runs.append(run)

    with open(out_json, "w") as fh:
        json.dump({"runs": runs}, fh, indent=1)

    cols = [
        "run_id",
        "agent_dir",
        "date",
        "model_arg",
        "reasoning_effort",
        "level",
        "n_questions",
        "n_with_usage",
        "accuracy",
        "accuracy_se",
        "human_mean_s",
        "counted_tokens_per_question",
        "gross_tokens_per_question",
        "output_tokens_per_question",
        "llm_calls_per_question",
        "mean_prefix_tokens_per_call",
        "flops_per_question",
        "models_without_coefficient",
    ]
    with open(out_csv, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for run in runs:
            for key in ("1", "2", "3", "all"):
                d = run["levels"][key]
                w.writerow(
                    {
                        "run_id": run["run_id"],
                        "agent_dir": run["agent_dir"],
                        "date": run["date"],
                        "model_arg": (run["agent_args"] or {}).get("model_name"),
                        "reasoning_effort": (run["agent_args"] or {}).get(
                            "reasoning_effort", ""
                        ),
                        "level": key,
                        **{
                            c: d[c]
                            for c in cols
                            if c in d and c not in ("level",)
                        },
                        "models_without_coefficient": ";".join(
                            d["models_without_coefficient"]
                        ),
                    }
                )
    print(f"{len(runs)} runs -> {out_json}, {out_csv}")


if __name__ == "__main__":
    if len(sys.argv) != 6:
        raise SystemExit(__doc__)
    main(*sys.argv[1:])
