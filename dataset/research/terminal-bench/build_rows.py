#!/usr/bin/env python3
"""Build the Terminal-Bench candidate rows from the retained source extracts.

Inputs (all read, never written):
  --sources   directory holding the retained extracts, normally
              agent-work/sources/terminal-bench/ of this folder. Required files:
                tb21-leaderboard-submissions.csv
                tb21-task-time-estimates.csv
                tbscience-leaderboard-v0-1-eval.csv
                tbscience-task-time-estimates.csv
                valsai-terminal-bench-science-board.csv
                aa-terminalbench-v2-1-token-counts.csv
Outputs (written fresh, nothing in --sources is modified):
  --out       directory receiving points.csv, models.csv, dispositions.csv
              and calculations.json.

Dependencies: Python 3.9+ standard library only.

Usage:
  python3 build_rows.py --sources agent-work/sources/terminal-bench \
                        --out candidates/terminal-bench
"""

import argparse
import csv
import json
import math
import os
import statistics

POINT_FIELDS = [
    "point_id", "task", "task_category", "task_description", "model_id", "compute_scope",
    "compute_flops", "human_skill", "human_time_scope", "human_time", "performance_vs_human",
    "comparison_issues", "compute_evidence", "human_time_evidence", "performance_evidence",
    "human_time_statistic", "human_time_subset", "human_attempts", "human_time_source",
    "human_time_method", "compute_method", "compute_statistic", "compute_subset", "ai_attempts",
    "compute_source", "tokens", "tokens_accounting", "source_dataset", "source_record", "notes",
    "ai_cost_usd", "ai_cost_basis", "ai_cost_date", "human_cost_usd", "human_cost_basis",
]

MODEL_FIELDS = [
    "model_id", "model", "company", "model_release_date", "model_release_source",
    "flops_per_token", "flops_per_token_method", "active_parameters", "active_parameters_basis",
    "encoder_parameters", "encoder_parameters_basis", "decoder_parameters",
    "decoder_parameters_basis", "parameter_source", "notes",
]

DISPOSITION_FIELDS = [
    "source", "record", "model", "agent", "n_trials", "accuracy_pct", "ratio_to_human",
    "standard_errors_below_guide", "outcome", "reason",
]

# --- shared FLOPs-per-token coefficients -------------------------------------
# Models already in a registry keep that registry's value; see research note.
FPT = {
    "claude-opus-4-7": 200e9,
    "claude-opus-4-8": 200e9,
    "claude-opus-5-max": 200e9,
    "gemini-3-pro": 200e9,
    "gemini-3.1-pro-preview": 200e9,
    "gpt-5-5": 346e9,
    "gpt-5-6-sol": 200e9,
    "gpt-5-6-terra": 40e9,
    "gpt-5-6-luna": 16e9,
    "gpt-6-astra": 600e9,
    # new in this batch
    "claude-fable-5": 300e9,
    "claude-fable-5-1": 300e9,
    "claude-sonnet-5": 200e9,
    "grok-4-5": 200e9,
    "glm-5.1": 80e9,
    # new with the 2026-09-13 Artificial Analysis reconciliation
    "grok-4-6": 200e9,
    "gemini-3-8-flash": 80e9,
    "gemini-3-5-flash-lite": 40e9,
    "kimi-k3": 208e9,
    "muse-spark-1-3": 200e9,
    "muse-glimmer": 60e9,
    "glm-5.3": 80e9,
    "glm-5.3-flash": 36e9,
    "qwen3.8-2.4t-a95b": 190e9,
    "qwen3.8-27b": 54e9,
    "deepseek-v4-pro-0813": 98e9,
    "k2-horizon-375b-a23b": 46e9,
    "minimax-m3": 46e9,
    "inkling": 82e9,
    "nvidia-nemotron-3-ultra-550b-a55b": 110e9,
    "mistral-medium-3-5": 256e9,
}

# submission file -> (point_id, model_id, agent label used in prose)
OFFICIAL = {
    "2026-05-01-anthropic-claude-opus-4-7-max-claude-code.json": ("agen-tbench21-opus47-claudecode", "claude-opus-4-7"),
    "2026-05-01-anthropic-claude-opus-4-7-max-terminus-2.json": ("agen-tbench21-opus47-terminus2", "claude-opus-4-7"),
    "2026-05-01-gemini-gemini-3-pro-preview-high-gemini-cli.json": ("agen-tbench21-gemini3pro-geminicli", "gemini-3-pro"),
    "2026-05-01-gemini-gemini-3-pro-preview-high-terminus-2.json": ("agen-tbench21-gemini3pro-terminus2", "gemini-3-pro"),
    "2026-05-01-glm-5-1-max-claude-code.json": ("agen-tbench21-glm51-claudecode", "glm-5.1"),
    "2026-05-01-openai-gpt-5-5-xhigh-codex.json": ("agen-tbench21-gpt55-codex", "gpt-5-5"),
    "2026-05-05-gemini-gemini-3-1-pro-preview-high-gemini-cli.json": ("agen-tbench21-gemini31pro-geminicli", "gemini-3.1-pro-preview"),
    "2026-05-05-gemini-gemini-3-1-pro-preview-high-terminus-2.json": ("agen-tbench21-gemini31pro-terminus2", "gemini-3.1-pro-preview"),
    "2026-06-05-anthropic-claude-fable-5-high-terminus-2.json": ("agen-tbench21-fable5-terminus2", "claude-fable-5"),
    "2026-06-07-anthropic-claude-fable-5-xhigh-claude-code.json": ("agen-tbench21-fable5-claudecode", "claude-fable-5"),
    "2026-07-09-anthropic-claude-opus-4-8-high-claude-code.json": ("agen-tbench21-opus48-claudecode", "claude-opus-4-8"),
    "2026-07-09-anthropic-claude-sonnet-5-high-claude-code.json": ("agen-tbench21-sonnet5-claudecode", "claude-sonnet-5"),
    "2026-07-09-cursor-grok-4-5-none-cursor-cli.json": ("agen-tbench21-grok45-cursorcli", "grok-4-5"),
    "2026-07-10-gpt-5-6-sol-max-codex.json": ("agen-tbench21-gpt56sol-codex", "gpt-5-6-sol"),
    "2026-07-11-openai-gpt-5-6-luna-max-codex.json": ("agen-tbench21-gpt56luna-codex", "gpt-5-6-luna"),
    "2026-07-11-openai-gpt-5-6-terra-max-codex.json": ("agen-tbench21-gpt56terra-codex", "gpt-5-6-terra"),
}

OFFICIAL_DROP = {
    "2026-05-01-openai-gpt-5-5-xhigh-terminus-2.json": (
        "dispositions",
        "The run reports cached_input_tokens = 0 while its reported $493.85 is far below the "
        "$730.39 that GPT-5.5 list prices give on 81,469,069 input and 10,768,129 output tokens; "
        "solving at those prices puts about 52.6M of the reported input on the cache-read rate, so "
        "uncached_input_tokens is a gross input count and the counted quantity cannot be measured "
        "from it"),
    "2026-07-09-openai-muse-spark-1-1-xhigh-mini-swe-agent.json": (
        "dispositions",
        "uncached_input_tokens is 60,996 over 445 trials, 137 tokens per trial, against 932,239,373 "
        "cached input; the mini-SWE-agent counter reports essentially all input as cached and the "
        "fresh-input count is not usable"),
    "2026-07-10-gpt-5-6-luna-max-codex.json": (
        "dispositions",
        "Superseded by the same model and agent resubmitted on 2026-07-11 (PR #112) on Codex 0.144.1 "
        "with 4 rather than 33 reward-hacking disqualifications; building both would count one model "
        "run twice"),
    "2026-07-10-gpt-5-6-terra-max-codex.json": (
        "dispositions",
        "Superseded by the same model and agent resubmitted on 2026-07-11 (PR #115) on Codex 0.144.1 "
        "with 1 rather than 32 reward-hacking disqualifications; building both would count one model "
        "run twice"),
}

# Artificial Analysis rows. Rule after the 2026-09-13 review: every scored cell on that
# board becomes a row if it clears the exclusion guide and the model has a parameter prior,
# in either registry or derivable by the method of the relevant report in
# research/model-priors/. Effort variants are separate model IDs at the same weights, on the
# dataset's existing convention (gpt-5-high, claude-opus-5-max).
AA_BUILD = {
    # slug: (point_id, model_id, label, served reasoning effort as the board names it)
    "claude-fable-5-1": ("agen-tbench21-aa-fable51", "claude-fable-5-1", "Claude Fable 5.1", "max"),
    "claude-fable-5-1-xhigh": ("agen-tbench21-aa-fable51-xhigh", "claude-fable-5-1", "Claude Fable 5.1", "xhigh"),
    "claude-fable-5-1-high": ("agen-tbench21-aa-fable51-high", "claude-fable-5-1", "Claude Fable 5.1", "high"),
    "gpt-6-astra": ("agen-tbench21-aa-gpt6astra", "gpt-6-astra", "GPT-6 Astra", "max"),
    "gpt-6-astra-high": ("agen-tbench21-aa-gpt6astra-high", "gpt-6-astra", "GPT-6 Astra", "high"),
    "gpt-6-astra-medium": ("agen-tbench21-aa-gpt6astra-medium", "gpt-6-astra", "GPT-6 Astra", "medium"),
    "gpt-5-6-sol": ("agen-tbench21-aa-gpt56sol", "gpt-5-6-sol", "GPT-5.6 Sol", "max"),
    "gpt-5-6-sol-xhigh": ("agen-tbench21-aa-gpt56sol-xhigh", "gpt-5-6-sol", "GPT-5.6 Sol", "xhigh"),
    "gpt-5-6-terra": ("agen-tbench21-aa-gpt56terra", "gpt-5-6-terra", "GPT-5.6 Terra", "max"),
    "gpt-5-6-luna": ("agen-tbench21-aa-gpt56luna", "gpt-5-6-luna", "GPT-5.6 Luna", "max"),
    "claude-opus-5": ("agen-tbench21-aa-opus5", "claude-opus-5-max", "Claude Opus 5", "max"),
    "claude-fable-5": ("agen-tbench21-aa-fable5", "claude-fable-5", "Claude Fable 5", "max"),
    "grok-4-6": ("agen-tbench21-aa-grok46", "grok-4-6", "Grok 4.6", "high"),
    "gemini-3-8-flash": ("agen-tbench21-aa-gemini38flash", "gemini-3-8-flash", "Gemini 3.8 Flash", "high"),
    "gemini-3-5-flash-lite": ("agen-tbench21-aa-gemini35flashlite", "gemini-3-5-flash-lite", "Gemini 3.5 Flash-Lite", None),
    "kimi-k3": ("agen-tbench21-aa-kimik3", "kimi-k3", "Kimi K3", "max"),
    "muse-spark-1-3": ("agen-tbench21-aa-musespark13", "muse-spark-1-3", "Muse Spark 1.3", "max"),
    "muse-glimmer": ("agen-tbench21-aa-museglimmer", "muse-glimmer", "Muse Glimmer", "high"),
    "glm-5-3": ("agen-tbench21-aa-glm53", "glm-5.3", "GLM-5.3", "max"),
    "glm-5-3-flash": ("agen-tbench21-aa-glm53flash", "glm-5.3-flash", "GLM-5.3-Flash", None),
    "qwen3-8-2-4t-a95b": ("agen-tbench21-aa-qwen38max", "qwen3.8-2.4t-a95b", "Qwen3.8 2.4T A95B", None),
    "qwen3-8-27b": ("agen-tbench21-aa-qwen3827b", "qwen3.8-27b", "Qwen3.8 27B", "xhigh"),
    "deepseek-v4-pro": ("agen-tbench21-aa-dsv4pro0813", "deepseek-v4-pro-0813", "DeepSeek V4 Pro 0813", "max"),
    "k2-horizon-375b-a23b": ("agen-tbench21-aa-k2horizon", "k2-horizon-375b-a23b", "K2 Horizon 375B A23B", None),
    "minimax-m3": ("agen-tbench21-aa-minimaxm3", "minimax-m3", "MiniMax-M3", None),
    "inkling": ("agen-tbench21-aa-inkling", "inkling", "Inkling", "xhigh"),
    "nvidia-nemotron-3-ultra-550b-a55b": ("agen-tbench21-aa-nemotron3ultra", "nvidia-nemotron-3-ultra-550b-a55b", "Nemotron 3 Ultra 550B A55B", None),
    "mistral-medium-3-5": ("agen-tbench21-aa-mistralmedium35", "mistral-medium-3-5", "Mistral Medium 3.5", None),
}
AA_DROP_REASON = {
    "gpt-oss-120b": (
        "Resolution rate 26.22% is a ratio of 0.262 to the human baseline, 13.9 standard errors "
        "below the half-of-human guide, so the cell is excluded on performance under the "
        "2026-09-13 exclusion ruling"),
}

# Coordinator ruling 2026-09-13: this folder's match band is 0.85 to 1.15 of the human on
# the benchmark's own metric.
MATCH_LOW, MATCH_HIGH = 0.85, 1.15


def label(ratio):
    if ratio > MATCH_HIGH:
        return "above"
    return "match" if ratio >= MATCH_LOW else "below"


AGENT_URL = "https://github.com/harbor-framework/terminal-bench-2-1/tree/main/leaderboard/submissions"
TASK_URL = "https://github.com/harbor-framework/terminal-bench-2-1/tree/main/tasks"
PAPER = "https://arxiv.org/abs/2601.11868"
AA_URL = "https://artificialanalysis.ai/evaluations/terminalbench-v2-1"


def read_csv(path):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def human_time(sources):
    rows = read_csv(os.path.join(sources, "tb21-task-time-estimates.csv"))
    vals = [float(r["expert_time_estimate_min"]) for r in rows if r["expert_time_estimate_min"]]
    jvals = [float(r["junior_time_estimate_min"]) for r in rows if r["junior_time_estimate_min"]]
    return {
        "n_tasks": len(rows),
        "n_with_expert_estimate": len(vals),
        "expert_mean_min": sum(vals) / len(vals),
        "expert_median_min": statistics.median(vals),
        "expert_geomean_min": math.exp(sum(math.log(v) for v in vals) / len(vals)),
        "expert_min_min": min(vals),
        "expert_max_min": max(vals),
        "expert_sum_min": sum(vals),
        "expert_mean_sec": sum(vals) / len(vals) * 60.0,
        "junior_mean_min": sum(jvals) / len(jvals),
        "junior_mean_sec": sum(jvals) / len(jvals) * 60.0,
    }


TASK_DESCRIPTION = (
    "One agent attempt at one Terminal-Bench 2.1 task, averaged over the benchmark's 89 tasks with "
    "{trials} trials in the run. Each task supplies a natural-language instruction and a Docker "
    "container with internet access; the {agent} agent driving {model} works in the terminal until "
    "the task's agent timeout, and a separate verifier container runs the task's tests. Success is "
    "the task's own pass/fail test suite. The human unit is one domain expert completing the same "
    "task once.")

PERF = (
    "The run resolved {acc:.2f}% of its {trials} trials (standard error {se:.2f} pp). No human "
    "attempt at these tasks was timed or scored: the task authors' expert time estimates how long a "
    "focused domain expert needs to complete the task, so the human baseline they imply is "
    "completion and the resolution rate is read against 100%.")


def build_official(sources, ht, notes_extra):
    subs = {r["submission_file"]: r for r in read_csv(os.path.join(sources, "tb21-leaderboard-submissions.csv"))}
    points, calcs, disps = [], [], []
    for fname, (pid, model_id) in OFFICIAL.items():
        s = subs[fname]
        unc = int(s["uncached_input_tokens"])
        out = int(s["output_tokens"])
        cached = int(s["cached_input_tokens"])
        n = int(s["n_trials"])
        tokens = (unc + out) / n
        flops = tokens * FPT[model_id]
        acc = float(s["accuracy_pct"])
        se = float(s["accuracy_stderr_pct"])
        cost = float(s["total_cost_usd"]) / n
        dq = int(s["disqualified_trials"])
        agent = s["agent_label"]
        calcs.append({
            "point_id": pid, "source": "official leaderboard", "submission_file": fname,
            "pr": s["pr"], "model_id": model_id, "model_label": s["model_label"],
            "agent": agent, "agent_version": s["agent_version"], "reasoning_effort": s["reasoning_effort"],
            "date": s["date"], "n_trials": n, "accuracy_pct": acc, "accuracy_stderr_pct": se,
            "uncached_input_tokens": unc, "cached_input_tokens": cached, "output_tokens": out,
            "counted_tokens_total": unc + out, "counted_tokens_per_trial": tokens,
            "flops_per_token": FPT[model_id], "compute_flops": flops,
            "total_cost_usd": float(s["total_cost_usd"]), "cost_per_trial_usd": cost,
            "cached_to_uncached_ratio": cached / unc, "uncached_to_output_ratio": unc / out,
            "disqualified_trials": dq, "reward_hacks_pct": float(s["reward_hacks_pct"]),
            "avg_trial_duration_sec": float(s["avg_trial_duration_sec"]),
            "ratio_to_human": acc / 100.0, "label": label(acc / 100.0),
        })
        note = (
            "Cache reads of {cr:,} are excluded; the counted quantity is {unc:,} uncached input plus "
            "{out:,} output over {n} trials. Human time is the mean of the task authors' expert "
            "estimates for 88 of the 89 tasks (caffe-cifar-10 carries none); the median is 3,600 s. "
            "{extra}").format(cr=cached, unc=unc, out=out, n=n, extra=notes_extra.get(pid, "")).strip()
        points.append({
            "point_id": pid,
            "task": "Solve a Terminal-Bench 2.1 terminal task",
            "task_category": "coding",
            "task_description": TASK_DESCRIPTION.format(trials=n, agent=agent, model=s["model_label"]),
            "model_id": model_id,
            "compute_scope": "inference",
            "compute_flops": "%.1f" % flops,
            "human_skill": "expert",
            "human_time_scope": "task_performance",
            "human_time": "%.2f" % ht["expert_mean_sec"],
            "performance_vs_human": label(acc / 100.0),
            "comparison_issues": "different_attempt_selection",
            "compute_evidence": "derived_assumed_inputs",
            "human_time_evidence": "source_estimate",
            "performance_evidence": PERF.format(acc=acc, trials=n, se=se),
            "human_time_statistic": "mean",
            "human_time_subset": "not_applicable",
            "human_attempts": "not_applicable",
            "human_time_source": "%s; research/terminal-bench.md#human-time" % TASK_URL,
            "human_time_method": "estimated",
            "compute_method": "params_tokens",
            "compute_statistic": "mean",
            "compute_subset": "all",
            "ai_attempts": str(n),
            "compute_source": "%s; research/terminal-bench.md#%s" % (AGENT_URL, pid),
            "tokens": repr(tokens),
            "tokens_accounting": "input_cache_creation_output",
            "source_dataset": "Terminal-Bench 2.1 official leaderboard",
            "source_record": (
                "{url}/{f} (PR {pr}, repo at commit 7131e4375048a0e408a8fb404b5f499d726b695b); model "
                "{mn}, agent {ag} {av}, reasoning_effort {re}, run dated {dt}; performance: the same "
                "file's metrics.accuracy over {n} trials").format(
                    url=AGENT_URL, f=fname, pr=s["pr"], mn=s["model_name"], ag=s["agent"],
                    av=s["agent_version"], re=s["reasoning_effort"], dt=s["date"], n=n),
            "notes": note,
            "ai_cost_usd": "%.5f" % cost,
            "ai_cost_basis": "reported",
            "ai_cost_date": s["date"],
            "human_cost_usd": "",
            "human_cost_basis": "not_available",
        })
    for fname, (_outcome, reason) in OFFICIAL_DROP.items():
        s = subs[fname]
        disps.append({
            "source": "Terminal-Bench 2.1 official leaderboard",
            "record": fname,
            "model": s["model_label"],
            "agent": s["agent_label"],
            "n_trials": s["n_trials"],
            "accuracy_pct": s["accuracy_pct"],
            "ratio_to_human": "%.3f" % (float(s["accuracy_pct"]) / 100.0),
            "standard_errors_below_guide": "",
            "outcome": "not a row",
            "reason": reason,
        })
    return points, calcs, disps


AA_TASK_DESCRIPTION = (
    "One agent attempt at one Terminal-Bench 2.1 task, averaged over the benchmark's 89 tasks with "
    "267 trials in the run. Each task supplies a natural-language instruction and a Docker container "
    "with internet access; the Terminus 2 agent driving {model} works in the terminal in an e2b "
    "sandbox until the task's agent timeout{effort}, and a separate verifier runs the task's tests. "
    "Success is the task's own pass/fail test suite. The human unit is one domain expert completing "
    "the same task once.")


def build_aa(sources, ht, notes_extra):
    aa = {r["aa_slug"]: r for r in read_csv(os.path.join(sources, "aa-terminalbench-v2-1-token-counts.csv"))}
    points, calcs, disps = [], [], []
    for slug, row in sorted(aa.items(), key=lambda kv: -float(kv[1]["score"])):
        n = int(row["trials"])
        gross_in = int(row["input_tokens"])
        cacheable = int(row["cacheable_input_tokens"])
        answer = int(row["answer_tokens"])
        reasoning = int(row["reasoning_tokens"])
        unc = gross_in - cacheable
        out = answer + reasoning
        acc = float(row["score"]) * 100.0
        se = math.sqrt(acc / 100.0 * (1 - acc / 100.0) / n) * 100.0
        if slug not in AA_BUILD:
            disps.append({
                "source": "Artificial Analysis Terminal-Bench v2.1 board",
                "record": "%s (%s)" % (slug, row["aa_name"]),
                "model": row["aa_name"], "agent": "Terminus 2",
                "n_trials": n, "accuracy_pct": "%.2f" % acc,
                "ratio_to_human": "%.3f" % (acc / 100.0),
                "standard_errors_below_guide": "%.1f" % ((0.5 - acc / 100.0) / (se / 100.0)),
                "outcome": "not a row",
                "reason": AA_DROP_REASON[slug],
            })
            continue
        pid, model_id, lbl, effort = AA_BUILD[slug]
        tokens = (unc + out) / n
        flops = tokens * FPT[model_id]
        hit = float(row["cache_hit_rate"]) if row["cache_hit_rate"] != "" else None
        priced = row["price_1m_input_usd"] != ""
        cost = ((unc * float(row["price_1m_input_usd"])
                 + cacheable * float(row["price_1m_cache_hit_usd"])
                 + out * float(row["price_1m_output_usd"])) / 1e6 / n) if priced else None
        calcs.append({
            "point_id": pid, "source": "Artificial Analysis", "aa_slug": slug,
            "aa_name": row["aa_name"], "creator": row["creator"],
            "model_id": model_id, "reasoning_effort": effort, "trials": n, "accuracy_pct": acc, "binomial_stderr_pct": se,
            "passes": round(acc / 100.0 * n),
            "input_tokens": gross_in, "cacheable_input_tokens": cacheable,
            "uncached_input_tokens": unc, "answer_tokens": answer, "reasoning_tokens": reasoning,
            "counted_tokens_total": unc + out, "counted_tokens_per_trial": tokens,
            "flops_per_token": FPT[model_id], "compute_flops": flops,
            "cache_hit_rate": hit,
            "cost_per_trial_usd": cost,
            "counted_tokens_per_trial_at_hit_rate": (
                (gross_in - cacheable * hit + out) / n if hit is not None else None),
            "ratio_to_human": acc / 100.0, "label": label(acc / 100.0),
        })
        hit_clause = ("At the published {h:.4f} cache hit rate, counting the missed share as "
                      "fresh gives {t:,.0f} tokens per trial.").format(
                          h=hit, t=(gross_in - cacheable * hit + out) / n) if hit is not None \
            else "The board publishes no cache hit rate for this model."
        note = (
            "Cacheable input of {c:,} is excluded as cache reads; the counted quantity is {u:,} "
            "uncached input plus {a:,} answer and {r:,} reasoning tokens over {n} trials. {hc} "
            "Human time is the mean author expert estimate over 88 tasks; median 3,600 s. "
            "{extra}").format(
                c=cacheable, u=unc, a=answer, r=reasoning, n=n, hc=hit_clause,
                extra=notes_extra.get(pid, "")).strip()
        points.append({
            "point_id": pid,
            "task": "Solve a Terminal-Bench 2.1 terminal task",
            "task_category": "coding",
            "task_description": AA_TASK_DESCRIPTION.format(
                model=lbl,
                effort=(", served at %s reasoning effort" % effort) if effort else ""),
            "model_id": model_id,
            "compute_scope": "inference",
            "compute_flops": "%.1f" % flops,
            "human_skill": "expert",
            "human_time_scope": "task_performance",
            "human_time": "%.2f" % ht["expert_mean_sec"],
            "performance_vs_human": label(acc / 100.0),
            "comparison_issues": "different_attempt_selection",
            "compute_evidence": "derived_assumed_inputs",
            "human_time_evidence": "source_estimate",
            "performance_evidence": PERF.format(acc=acc, trials=n, se=se),
            "human_time_statistic": "mean",
            "human_time_subset": "not_applicable",
            "human_attempts": "not_applicable",
            "human_time_source": "%s; research/terminal-bench.md#human-time" % TASK_URL,
            "human_time_method": "estimated",
            "compute_method": "params_tokens",
            "compute_statistic": "mean",
            "compute_subset": "all",
            "ai_attempts": str(n),
            "compute_source": "%s; research/terminal-bench.md#%s" % (AA_URL, pid),
            "tokens": repr(tokens),
            "tokens_accounting": "input_cache_creation_output",
            "source_dataset": "Artificial Analysis Terminal-Bench v2.1 board",
            "source_record": (
                "{url}, model slug {slug} ({name}), canonicalEvalTokenCounts.terminalbenchV21 and "
                "terminalbenchV21 score in the page payload retrieved 2026-09-13; Terminus 2 harness "
                "in an e2b sandbox, pass@1 over 3 repeats of each of the 89 tasks; performance: the "
                "same payload field").format(url=AA_URL, slug=slug, name=row["aa_name"]),
            "notes": note,
            "ai_cost_usd": ("%.5f" % cost) if priced else "",
            "ai_cost_basis": "list_price" if priced else "not_available",
            "ai_cost_date": "2026-09-13" if priced else "",
            "human_cost_usd": "",
            "human_cost_basis": "not_available",
        })
    return points, calcs, disps


TBSCI_REASON = (
    "Terminal-Bench-Science 0.1, 70 tasks, mean author expert estimate 22.19 h. Resolution rate "
    "{acc:.2f}% against the completion the authors' expert estimates imply is a ratio of {ratio:.3f} "
    "to the human baseline, {se:.1f} standard errors below the half-of-human guide, so the cell is "
    "excluded on performance under the 2026-09-13 exclusion ruling. Compute would in any case need "
    "reconstruction: the board publishes one undecomposed total_tokens that includes cache reads "
    "(98-99% of it on the price identity), not the dataset's counted quantity.")

VALS_REASON = (
    "Vals AI Terminal-Bench-Science 0.1 board, Terminus 2, one trial per task over 70 tasks. "
    "{extra} The board publishes cost per task but null avg_input_tokens and avg_output_tokens, so "
    "the only compute route is a dollar inversion needing both a cache structure and an "
    "uncached-to-output ratio transferred from a benchmark whose tasks are about thirty times "
    "shorter.")


def build_dispositions(sources):
    disps = []
    for r in read_csv(os.path.join(sources, "tbscience-leaderboard-v0-1-eval.csv")):
        acc = float(r["accuracy_pct"])
        se = float(r["accuracy_stderr_pct"])
        ratio = acc / 100.0
        ses_below = (0.5 - ratio) / (se / 100.0)
        disps.append({
            "source": "Terminal-Bench-Science 0.1 official leaderboard (tbench.ai)",
            "record": "leaderboard v0-1-eval rank %s" % r["rank"],
            "model": r["model_label"], "agent": r["agent_label"],
            "n_trials": r["trials"], "accuracy_pct": "%.2f" % acc,
            "ratio_to_human": "%.3f" % ratio,
            "standard_errors_below_guide": "%.1f" % ses_below,
            "outcome": "not a row",
            "reason": TBSCI_REASON.format(acc=acc, ratio=ratio, se=ses_below),
        })
    for r in read_csv(os.path.join(sources, "valsai-terminal-bench-science-board.csv")):
        if r["model"] == ASTRA_VALS_MODEL:
            continue  # built as a row, see build_astra
        acc = float(r["accuracy_pct"])
        ratio = acc / 100.0
        n = 70
        se = math.sqrt(ratio * (1 - ratio) / n)
        ses_below = ((0.5 - ratio) / se) if se > 0 else None
        if ratio >= 0.5:
            extra = ("Resolution rate {acc:.2f}% clears the half-of-human guide against the "
                     "completion the authors' expert estimates imply; this cell is held on compute "
                     "alone and is the one Terminal-Bench-Science cell that could become a row if a "
                     "token decomposition appears.").format(acc=acc)
        elif ses_below is None:
            extra = ("The run resolved no task, so the cell is excluded on performance.")
        else:
            extra = ("Resolution rate {acc:.2f}% is a ratio of {ratio:.3f} to the human baseline, "
                     "{se:.1f} standard errors below the half-of-human guide, so the cell is "
                     "excluded on performance.").format(acc=acc, ratio=ratio, se=ses_below)
        disps.append({
            "source": "Vals AI Terminal-Bench-Science 0.1 board",
            "record": r["model"], "model": r["model"], "agent": "Terminus 2",
            "n_trials": n, "accuracy_pct": "%.2f" % acc,
            "ratio_to_human": "%.3f" % ratio,
            "standard_errors_below_guide": ("%.1f" % ses_below) if ses_below is not None else "",
            "outcome": "not a row",
            "reason": VALS_REASON.format(extra=extra),
        })
    return disps


NEW_MODELS = [
    {
        "model_id": 'grok-4-6', "model": 'Grok 4.6', "company": 'xAI',
        "model_release_date": '2026-08-12',
        "model_release_source": 'https://artificialanalysis.ai/evaluations/terminalbench-v2-1 (model record grok-4-6, releaseDate 2026-08-12)',
        "flops_per_token": '200000000000', "flops_per_token_method": "two_active_parameters",
        "active_parameters": '100000000000', "active_parameters_basis": 'estimated',
        "encoder_parameters": "not_applicable", "encoder_parameters_basis": "not_applicable",
        "decoder_parameters": "not_applicable", "decoder_parameters_basis": "not_applicable",
        "parameter_source": 'research/model-priors/google-xai-others.md; research/model-priors/pricing-crosscheck.md',
        "notes": "100B active transfers the Grok 4.5 derivation, the ruled Grok 4 sparsity of 15x applied to the 1.5T V9 foundation the prior report records. The report's price ladder corroborates: Grok 4 prices 1.71x Grok 4.6 on the geometric mean of input and output, which on a 200B Grok 4 gives 117B. Sensitivity 45-210B, grade C.",
    },
    {
        "model_id": 'gemini-3-8-flash', "model": 'Gemini 3.8 Flash', "company": 'Google DeepMind',
        "model_release_date": '2026-09-02',
        "model_release_source": 'https://artificialanalysis.ai/evaluations/terminalbench-v2-1 (model record gemini-3-8-flash, releaseDate 2026-09-02)',
        "flops_per_token": '80000000000', "flops_per_token_method": "two_active_parameters",
        "active_parameters": '40000000000', "active_parameters_basis": 'estimated',
        "encoder_parameters": "not_applicable", "encoder_parameters_basis": "not_applicable",
        "decoder_parameters": "not_applicable", "decoder_parameters_basis": "not_applicable",
        "parameter_source": 'research/model-priors/google-xai-others.md',
        "notes": "40B active is the Gemini 3-generation Flash prior the report holds for gemini-3-flash-preview and gemini-3.5-flash, range 15-90B, grade C. Google discloses no Gemini expert sizes or routing. The report's own warning applies: Flash prices are not comparable across generations, so the tier rather than the price fixes this.",
    },
    {
        "model_id": 'gemini-3-5-flash-lite', "model": 'Gemini 3.5 Flash-Lite', "company": 'Google DeepMind',
        "model_release_date": '2026-07-21',
        "model_release_source": 'https://artificialanalysis.ai/evaluations/terminalbench-v2-1 (model record gemini-3-5-flash-lite, releaseDate 2026-07-21)',
        "flops_per_token": '40000000000', "flops_per_token_method": "two_active_parameters",
        "active_parameters": '20000000000', "active_parameters_basis": 'estimated',
        "encoder_parameters": "not_applicable", "encoder_parameters_basis": "not_applicable",
        "decoder_parameters": "not_applicable", "decoder_parameters_basis": "not_applicable",
        "parameter_source": 'research/model-priors/google-xai-others.md',
        "notes": '20B active is the Flash-Lite prior the report holds for gemini-3.1-flash-lite-preview, range 6-45B, grade C. Anchoring the 3.x price ladder on a 130B Pro gives Flash-Lite 16B, which is inside that range.',
    },
    {
        "model_id": 'muse-spark-1-3', "model": 'Muse Spark 1.3', "company": 'Meta',
        "model_release_date": '2026-09-02',
        "model_release_source": 'https://artificialanalysis.ai/evaluations/terminalbench-v2-1 (model record muse-spark-1-3, releaseDate 2026-09-02)',
        "flops_per_token": '200000000000', "flops_per_token_method": "two_active_parameters",
        "active_parameters": '100000000000', "active_parameters_basis": 'estimated',
        "encoder_parameters": "not_applicable", "encoder_parameters_basis": "not_applicable",
        "decoder_parameters": "not_applicable", "decoder_parameters_basis": "not_applicable",
        "parameter_source": 'research/model-priors/pricing-crosscheck.md',
        "notes": "Meta discloses nothing and no prior report covers the Muse line. 100B active is a within-lab price-ratio transfer from Muse Glimmer three weeks earlier: 1.25/4.25 against 0.35/1.50 is 3.18x on the geometric mean, giving 95B on a 30B Glimmer under the cross-check's bracket. Range 50-170B, grade C; the anchor rests only on Artificial Analysis.",
    },
    {
        "model_id": 'muse-glimmer', "model": 'Muse Glimmer', "company": 'Meta',
        "model_release_date": '2026-08-10',
        "model_release_source": 'https://artificialanalysis.ai/evaluations/terminalbench-v2-1 (model record muse-glimmer, releaseDate 2026-08-10)',
        "flops_per_token": '60000000000', "flops_per_token_method": "two_active_parameters",
        "active_parameters": '30000000000', "active_parameters_basis": 'estimated',
        "encoder_parameters": "not_applicable", "encoder_parameters_basis": "not_applicable",
        "decoder_parameters": "not_applicable", "decoder_parameters_basis": "not_applicable",
        "parameter_source": 'https://artificialanalysis.ai/evaluations/terminalbench-v2-1',
        "notes": "30B active is the figure Artificial Analysis publishes for this open-weight release. No prior report covers the Muse line and Meta publishes no architecture note the board's figure can be checked against, so the basis is estimated, as on Inkling, whose provenance is the same. Range 15-60B, grade C.",
    },
    {
        "model_id": 'glm-5.3', "model": 'GLM-5.3', "company": 'Z.ai',
        "model_release_date": '2026-08-18',
        "model_release_source": 'https://artificialanalysis.ai/evaluations/terminalbench-v2-1 (model record glm-5.3, releaseDate 2026-08-18)',
        "flops_per_token": '80000000000', "flops_per_token_method": "two_active_parameters",
        "active_parameters": '40000000000', "active_parameters_basis": 'reported',
        "encoder_parameters": "not_applicable", "encoder_parameters_basis": "not_applicable",
        "decoder_parameters": "not_applicable", "decoder_parameters_basis": "not_applicable",
        "parameter_source": 'research/model-priors/google-xai-others.md',
        "notes": "40B active on two independent lines: Epoch's GLM-5.3 entry states it shares GLM-5.2's base, which is 744B total over 40B active at Confident, and Artificial Analysis publishes 40B in its own model record. Range 35-45B.",
    },
    {
        "model_id": 'glm-5.3-flash', "model": 'GLM-5.3-Flash', "company": 'Z.ai',
        "model_release_date": '2026-08-26',
        "model_release_source": 'https://artificialanalysis.ai/evaluations/terminalbench-v2-1 (model record glm-5.3-flash, releaseDate 2026-08-26)',
        "flops_per_token": '36000000000', "flops_per_token_method": "two_active_parameters",
        "active_parameters": '18000000000', "active_parameters_basis": 'estimated',
        "encoder_parameters": "not_applicable", "encoder_parameters_basis": "not_applicable",
        "decoder_parameters": "not_applicable", "decoder_parameters_basis": "not_applicable",
        "parameter_source": 'research/model-priors/google-xai-others.md',
        "notes": "18B active from the prior report's efficient-MoE table, where Epoch records GLM-5.3-Flash at 320B total over 18B active at Likely confidence; Artificial Analysis publishes the same 18B. Likely rather than Confident is why the basis stays estimated. Range 12-25B.",
    },
    {
        "model_id": 'qwen3.8-2.4t-a95b', "model": 'Qwen3.8-2.4T-A95B', "company": 'Alibaba',
        "model_release_date": '2026-08-12',
        "model_release_source": 'https://artificialanalysis.ai/evaluations/terminalbench-v2-1 (model record qwen3.8-2.4t-a95b, releaseDate 2026-08-12)',
        "flops_per_token": '190000000000', "flops_per_token_method": "two_active_parameters",
        "active_parameters": '95000000000', "active_parameters_basis": 'reported',
        "encoder_parameters": "not_applicable", "encoder_parameters_basis": "not_applicable",
        "decoder_parameters": "not_applicable", "decoder_parameters_basis": "not_applicable",
        "parameter_source": 'research/model-priors/google-xai-others.md',
        "notes": "95B active is stated in the model's own name and matches the prior report's table for the Qwen3.8 generation, 2.4T total over 95B active at Epoch Confident. Open weights, so the count is computable from the published config.",
    },
    {
        "model_id": 'qwen3.8-27b', "model": 'Qwen3.8-27B', "company": 'Alibaba',
        "model_release_date": '2026-08-14',
        "model_release_source": 'https://artificialanalysis.ai/evaluations/terminalbench-v2-1 (model record qwen3.8-27b, releaseDate 2026-08-14)',
        "flops_per_token": '54000000000', "flops_per_token_method": "two_active_parameters",
        "active_parameters": '27000000000', "active_parameters_basis": 'reported',
        "encoder_parameters": "not_applicable", "encoder_parameters_basis": "not_applicable",
        "decoder_parameters": "not_applicable", "decoder_parameters_basis": "not_applicable",
        "parameter_source": 'https://artificialanalysis.ai/evaluations/terminalbench-v2-1',
        "notes": "27B is the dense parameter count in the model's own name, so every parameter is active; Artificial Analysis publishes the same 27B. Open weights.",
    },
    {
        "model_id": 'deepseek-v4-pro-0813', "model": 'DeepSeek V4 Pro 0813', "company": 'DeepSeek',
        "model_release_date": '2026-08-13',
        "model_release_source": 'https://artificialanalysis.ai/evaluations/terminalbench-v2-1 (model record deepseek-v4-pro, name DeepSeek V4 Pro 0813, releaseDate 2026-08-13)',
        "flops_per_token": '98000000000', "flops_per_token_method": "two_active_parameters",
        "active_parameters": '49000000000', "active_parameters_basis": 'reported',
        "encoder_parameters": "not_applicable", "encoder_parameters_basis": "not_applicable",
        "decoder_parameters": "not_applicable", "decoder_parameters_basis": "not_applicable",
        "parameter_source": 'https://deepseek.com/en/news/v4-preview/; research/model-priors/google-xai-others.md',
        "notes": "49B active is DeepSeek's own figure on its V4 release page, the citation the registry's deepseek-v4-pro-preview record already carries; the report's table and Artificial Analysis give the same 49B. Kept separate from that record, whose note says its run \"used the April preview, before the August general release\"; this is that general release.",
    },
    {
        "model_id": 'k2-horizon-375b-a23b', "model": 'K2 Horizon 375B-A23B', "company": 'MBZUAI Institute of Foundation Models',
        "model_release_date": '2026-09-03',
        "model_release_source": 'https://artificialanalysis.ai/evaluations/terminalbench-v2-1 (model record k2-horizon-375b-a23b, releaseDate 2026-09-03)',
        "flops_per_token": '46000000000', "flops_per_token_method": "two_active_parameters",
        "active_parameters": '23000000000', "active_parameters_basis": 'reported',
        "encoder_parameters": "not_applicable", "encoder_parameters_basis": "not_applicable",
        "decoder_parameters": "not_applicable", "decoder_parameters_basis": "not_applicable",
        "parameter_source": 'https://artificialanalysis.ai/evaluations/terminalbench-v2-1',
        "notes": "23B active is stated in the model's own name and republished in the Artificial Analysis model record. Open weights. The board carries no price fields for this model, so rows built from it leave the cost columns empty.",
    },
    {
        "model_id": 'inkling', "model": 'Inkling', "company": 'Thinking Machines',
        "model_release_date": '2026-07-15',
        "model_release_source": 'https://artificialanalysis.ai/evaluations/terminalbench-v2-1 (model record inkling, releaseDate 2026-07-15)',
        "flops_per_token": '82000000000', "flops_per_token_method": "two_active_parameters",
        "active_parameters": '41000000000', "active_parameters_basis": 'estimated',
        "encoder_parameters": "not_applicable", "encoder_parameters_basis": "not_applicable",
        "decoder_parameters": "not_applicable", "decoder_parameters_basis": "not_applicable",
        "parameter_source": 'https://artificialanalysis.ai/evaluations/terminalbench-v2-1',
        "notes": "41B active is the figure Artificial Analysis publishes for this open-weight release. No prior report covers Thinking Machines and the lab publishes no architecture note that the board's figure can be checked against, so the basis is estimated. Range 20-80B, grade C.",
    },
    {
        "model_id": 'nvidia-nemotron-3-ultra-550b-a55b', "model": 'Nemotron 3 Ultra 550B-A55B', "company": 'NVIDIA',
        "model_release_date": '2026-06-04',
        "model_release_source": 'https://artificialanalysis.ai/evaluations/terminalbench-v2-1 (model record nvidia-nemotron-3-ultra-550b-a55b, releaseDate 2026-06-04)',
        "flops_per_token": '110000000000', "flops_per_token_method": "two_active_parameters",
        "active_parameters": '55000000000', "active_parameters_basis": 'reported',
        "encoder_parameters": "not_applicable", "encoder_parameters_basis": "not_applicable",
        "decoder_parameters": "not_applicable", "decoder_parameters_basis": "not_applicable",
        "parameter_source": 'https://artificialanalysis.ai/evaluations/terminalbench-v2-1',
        "notes": "55B active is stated in the model's own name and republished in the Artificial Analysis model record. Open weights, so the count is computable from the published config.",
    },
    {
        "model_id": 'mistral-medium-3-5', "model": 'Mistral Medium 3.5', "company": 'Mistral AI',
        "model_release_date": '2026-04-29',
        "model_release_source": 'https://artificialanalysis.ai/evaluations/terminalbench-v2-1 (model record mistral-medium-3-5, releaseDate 2026-04-29)',
        "flops_per_token": '256000000000', "flops_per_token_method": "two_active_parameters",
        "active_parameters": '128000000000', "active_parameters_basis": 'estimated',
        "encoder_parameters": "not_applicable", "encoder_parameters_basis": "not_applicable",
        "decoder_parameters": "not_applicable", "decoder_parameters_basis": "not_applicable",
        "parameter_source": 'https://artificialanalysis.ai/evaluations/terminalbench-v2-1',
        "notes": "128B active is the figure Artificial Analysis publishes for this release and is the weakest new prior in this batch: no report covers Mistral Medium, Mistral has disclosed no Medium 3.x architecture, and 128B sits above the registry's 41B for the larger Mistral Large 3. An order-of-magnitude placeholder. Range 40-200B, grade C.",
    },
    {
        "model_id": "claude-fable-5", "model": "Claude Fable 5", "company": "Anthropic",
        "model_release_date": "2026-06-09",
        "model_release_source": "https://artificialanalysis.ai/evaluations/terminalbench-v2-1 (model record claude-fable-5, releaseDate 2026-06-09); corroborated by the Terminal-Bench-Science 0.1 leaderboard metadata model_release_date for Fable 5",
        "flops_per_token": "300000000000", "flops_per_token_method": "two_active_parameters",
        "active_parameters": "150000000000", "active_parameters_basis": "estimated",
        "encoder_parameters": "not_applicable", "encoder_parameters_basis": "not_applicable",
        "decoder_parameters": "not_applicable", "decoder_parameters_basis": "not_applicable",
        "parameter_source": "research/model-priors/anthropic.md",
        "notes": "150B active is the Anthropic prior report's own recommendation for the Fable class, grade C; Anthropic discloses nothing. Throughput inversion reads Fable 5 at 61-68B, which the report rejects because it would put Fable below Opus 5. Sensitivity 60-400B, 0.4x to 2.7x. Anthropic serves Fable 5 with an Opus 4.8 fallback, so some turns may run on a smaller model.",
    },
    {
        "model_id": "claude-fable-5-1", "model": "Claude Fable 5.1", "company": "Anthropic",
        "model_release_date": "2026-09-01",
        "model_release_source": "https://artificialanalysis.ai/evaluations/terminalbench-v2-1 (model record claude-fable-5-1, releaseDate 2026-09-01); corroborated by the Terminal-Bench-Science 0.1 leaderboard metadata model_release_date for Fable 5.1",
        "flops_per_token": "300000000000", "flops_per_token_method": "two_active_parameters",
        "active_parameters": "150000000000", "active_parameters_basis": "estimated",
        "encoder_parameters": "not_applicable", "encoder_parameters_basis": "not_applicable",
        "decoder_parameters": "not_applicable", "decoder_parameters_basis": "not_applicable",
        "parameter_source": "research/model-priors/anthropic.md",
        "notes": "150B active is the Anthropic prior report's own recommendation for Fable 5.1, the same number it gives Fable 5 because Anthropic describes 5.1 as about a one-and-a-half-fold step rather than a new scale, range 60-400B, grade C. The same 150B prices the batch's anthropic-internal-research-flt-2026-08 record, whose stated anchor is Fable 5.1.",
    },
    {
        "model_id": "claude-sonnet-5", "model": "Claude Sonnet 5", "company": "Anthropic",
        "model_release_date": "2026-06-30",
        "model_release_source": "https://artificialanalysis.ai/evaluations/terminalbench-v2-1 (model record claude-sonnet-5, releaseDate 2026-06-30)",
        "flops_per_token": "200000000000", "flops_per_token_method": "two_active_parameters",
        "active_parameters": "100000000000", "active_parameters_basis": "estimated",
        "encoder_parameters": "not_applicable", "encoder_parameters_basis": "not_applicable",
        "decoder_parameters": "not_applicable", "decoder_parameters_basis": "not_applicable",
        "parameter_source": "research/model-priors/anthropic.md",
        "notes": "100B active transfers the Sonnet-tier prior the ruling held unchanged for Sonnet 4.5 and 4.6; Anthropic discloses nothing for Sonnet 5. The prior report's throughput route reads Sonnet 4.5 at 85-110B and Sonnet 4.6 at 78-98B and is not usable for ranking contemporaneous models. Sensitivity 50-200B, grade C.",
    },
    {
        "model_id": "grok-4-5", "model": "Grok 4.5", "company": "xAI",
        "model_release_date": "2026-07-08",
        "model_release_source": "https://artificialanalysis.ai/evaluations/terminalbench-v2-1 (model record grok-4-5, releaseDate 2026-07-08, creator SpaceXAI)",
        "flops_per_token": "200000000000", "flops_per_token_method": "two_active_parameters",
        "active_parameters": "100000000000", "active_parameters_basis": "estimated",
        "encoder_parameters": "not_applicable", "encoder_parameters_basis": "not_applicable",
        "decoder_parameters": "not_applicable", "decoder_parameters_basis": "not_applicable",
        "parameter_source": "research/model-priors/google-xai-others.md",
        "notes": "100B active applies the ruled Grok 4 sparsity, 3e12 total over 200B active, to the 1.5T V9 foundation the prior report records for Grok 4.5. Bracketing: 2026 open-MoE sparsity of 19-33x gives 45-79B; scaling the report's 70B Grok 4.20 by its 3x foundation step gives 210B. Sensitivity 45-210B, grade C. The company field keeps xAI, as the submission does.",
    },
    {
        "model_id": "glm-5.1", "model": "GLM-5.1", "company": "Z.ai",
        "model_release_date": "2026-04-07",
        "model_release_source": "https://artificialanalysis.ai/evaluations/terminalbench-v2-1 (model record glm-5-1, releaseDate 2026-04-07, creator Z AI)",
        "flops_per_token": "80000000000", "flops_per_token_method": "two_active_parameters",
        "active_parameters": "40000000000", "active_parameters_basis": "estimated",
        "encoder_parameters": "not_applicable", "encoder_parameters_basis": "not_applicable",
        "decoder_parameters": "not_applicable", "decoder_parameters_basis": "not_applicable",
        "parameter_source": "research/model-priors/google-xai-others.md",
        "notes": "40B active is bracketed on both sides: GLM-5 (2026-02) and GLM-5.2 (2026-06) are both 744B total over 40B active, the first from published config files and the second corroborated by Epoch at Confident. Z.ai publishes no config for the April 5.1 point release, so the count is estimated rather than reported. Sensitivity 30-50B.",
    },
]


# --- Terminal-Bench-Science: the GPT-6 Astra row ------------------------------
# Coordinator ruling 2026-09-13: build this cell. The Vals AI board publishes a dollar
# figure per task and no tokens, so compute is a cost inversion under the DECISIONS
# two-transfer rule, central at the geometric mean of the two transfers.

ASTRA_VALS_MODEL = "openai/gpt-6-astra"
ASTRA_POINT_ID = "agen-tbsci-gpt6astra-valsai"
ASTRA_MODEL_ID = "gpt-6-astra"
ASTRA_PRICES = (10.00, 1.00, 50.00)  # input, cached input, output, USD per million
ASTRA_VALS_TB21_MODEL = "openai/gpt-6-astra"  # the same operator's Terminal-Bench 2.1 cell
ASTRA_DONOR_SLUG = "gpt-6-astra"     # Artificial Analysis Terminal-Bench v2.1 record
ASTRA_TRIALS = 70
TBSCI_TRIALS = 210
TBSCI_URL = "https://www.vals.ai/benchmarks/terminal-bench-science"
TBSCI_TASK_URL = "https://github.com/harbor-framework/terminal-bench-science/tree/main/tasks"
# Models on both the Terminal-Bench 2.1 and Terminal-Bench-Science boards, used to measure
# how the cache-read share grows with task length. (label, prices, tb21 submission file)
# One model run under both Terminus 2 and its own lab's CLI on the official board, used to
# scale the Codex-run GPT-5.6 Sol cross-check into a Terminus 2 reading.
TERMINUS_PAIRS = [
    ("2026-05-01-anthropic-claude-opus-4-7-max-claude-code.json",
     "2026-05-01-anthropic-claude-opus-4-7-max-terminus-2.json", "Opus 4.7"),
    ("2026-06-07-anthropic-claude-fable-5-xhigh-claude-code.json",
     "2026-06-05-anthropic-claude-fable-5-high-terminus-2.json", "Fable 5"),
    ("2026-05-01-gemini-gemini-3-pro-preview-high-gemini-cli.json",
     "2026-05-01-gemini-gemini-3-pro-preview-high-terminus-2.json", "Gemini 3 Pro"),
    ("2026-05-05-gemini-gemini-3-1-pro-preview-high-gemini-cli.json",
     "2026-05-05-gemini-gemini-3-1-pro-preview-high-terminus-2.json", "Gemini 3.1 Pro"),
]
LENGTH_PAIRS = [
    ("GPT-5.6 Sol", (4.00, 0.40, 20.00), "2026-07-10-gpt-5-6-sol-max-codex.json"),
    ("GPT-5.6 Terra", (2.00, 0.20, 12.00), "2026-07-11-openai-gpt-5-6-terra-max-codex.json"),
    ("GPT-5.6 Luna", (0.20, 0.02, 1.20), "2026-07-11-openai-gpt-5-6-luna-max-codex.json"),
]


def invert(cost_usd, prices, k, m):
    """Counted tokens from a dollar figure, given U/O = k and cache_reads/(U+O) = m."""
    p_u, p_c, p_o = prices
    o = cost_usd * 1e6 / (p_u * k + p_c * m * (k + 1) + p_o)
    return {"output": o, "uncached": k * o, "cache_reads": m * (k + 1) * o,
            "counted": (k + 1) * o}


def tbsci_human_time(sources):
    rows = read_csv(os.path.join(sources, "tbscience-task-time-estimates.csv"))
    vals = [float(r["expert_time_estimate_hours"]) for r in rows if r["expert_time_estimate_hours"]]
    return {
        "n_tasks": len(rows), "n_with_expert_estimate": len(vals),
        "expert_mean_hours": sum(vals) / len(vals),
        "expert_median_hours": statistics.median(vals),
        "expert_geomean_hours": math.exp(sum(math.log(v) for v in vals) / len(vals)),
        "expert_min_hours": min(vals), "expert_max_hours": max(vals),
        "expert_sum_hours": sum(vals),
        "expert_mean_sec": sum(vals) / len(vals) * 3600.0,
    }


def build_astra(sources):
    subs = {r["submission_file"]: r for r in read_csv(os.path.join(sources, "tb21-leaderboard-submissions.csv"))}
    board = {r["model_label"]: r for r in read_csv(os.path.join(sources, "tbscience-leaderboard-v0-1-eval.csv"))}
    vals = {r["model"]: r for r in read_csv(os.path.join(sources, "valsai-terminal-bench-science-board.csv"))}
    aa = {r["aa_slug"]: r for r in read_csv(os.path.join(sources, "aa-terminalbench-v2-1-token-counts.csv"))}
    ht = tbsci_human_time(sources)

    # Donor: the same model under the same harness on Terminal-Bench 2.1.
    d = aa[ASTRA_DONOR_SLUG]
    d_unc = int(d["input_tokens"]) - int(d["cacheable_input_tokens"])
    d_cache = int(d["cacheable_input_tokens"])
    d_out = int(d["answer_tokens"]) + int(d["reasoning_tokens"])
    k = d_unc / d_out
    m_donor = d_cache / (d_unc + d_out)

    # Length effect: growth in cache reads per counted token from Terminal-Bench 2.1 to
    # Terminal-Bench-Science, measured on the three models that appear on both boards.
    growth = []
    for pair_model, prices, fname in LENGTH_PAIRS:
        sub = subs[fname]
        u, c, o = (int(sub["uncached_input_tokens"]), int(sub["cached_input_tokens"]),
                   int(sub["output_tokens"]))
        m21 = c / (u + o)
        b = board[pair_model]
        total = int(b["total_tokens"])
        sci = invert_from_total(total, float(b["total_cost_usd"]), prices, u / o)
        m_sci = (total - sci) / sci
        growth.append({"model": pair_model, "m_tb21": m21, "m_tbscience": m_sci,
                       "growth": m_sci / m21, "tbscience_counted_per_trial": sci / TBSCI_TRIALS})
    g = math.exp(sum(math.log(x["growth"]) for x in growth) / len(growth))

    row = vals[ASTRA_VALS_MODEL]
    cost = float(row["cost_per_test_usd"])
    acc = float(row["accuracy_pct"])

    # Donor reading A: the same model's measured token mix, from Artificial Analysis.
    # Donor reading B: the same operator's own Terminal-Bench 2.1 cell. Vals bills
    # $1.339493 per task on the 89 tasks where Artificial Analysis measures a gross volume
    # worth $0.374 at these rates, so one reading is that Vals simply processes more tokens
    # at the donor's mix (A) and the other is that Vals' cache-read multiple is far higher
    # (B). The published fields do not choose; DECISIONS takes the geometric mean.
    tb21 = {r["model"]: r for r in read_csv(os.path.join(sources, "valsai-terminal-bench-2-1-board.csv"))}
    vals_tb21_cost = float(tb21[ASTRA_VALS_TB21_MODEL]["cost_per_test_usd"])
    d_unc_pt, d_out_pt = d_unc / 267.0, d_out / 267.0
    p_u, p_c, p_o = ASTRA_PRICES
    aa_cost_pt = (p_u * d_unc_pt + p_c * (d_cache / 267.0) + p_o * d_out_pt) / 1e6
    # The same volume priced gross: every input token at the input rate, no cache discount.
    aa_gross_pt = (p_u * (d_unc_pt + d_cache / 267.0) + p_o * d_out_pt) / 1e6
    m_vals = ((vals_tb21_cost * 1e6 - p_u * d_unc_pt - p_o * d_out_pt)
              / (p_c * (d_unc_pt + d_out_pt)))

    readings = {}
    for name, m_base in (("A_artificial_analysis_mix", m_donor), ("B_vals_own_tb21_cell", m_vals)):
        t1 = invert(cost, ASTRA_PRICES, k, m_base)
        t2 = invert(cost, ASTRA_PRICES, k, m_base * g)
        readings[name] = {
            "m_at_tb21_length": m_base, "m_at_science_length": m_base * g,
            "transfer_1_no_length_correction": t1, "transfer_2_length_corrected": t2,
            "counted_tokens_per_task": math.sqrt(t1["counted"] * t2["counted"]),
        }
    tokens = math.sqrt(readings["A_artificial_analysis_mix"]["counted_tokens_per_task"]
                       * readings["B_vals_own_tb21_cell"]["counted_tokens_per_task"])
    flops = tokens * FPT[ASTRA_MODEL_ID]
    se = math.sqrt(acc / 100.0 * (1 - acc / 100.0) / ASTRA_TRIALS) * 100.0
    lo_tokens = readings["B_vals_own_tb21_cell"]["transfer_2_length_corrected"]["counted"]
    hi_tokens = readings["A_artificial_analysis_mix"]["transfer_1_no_length_correction"]["counted"]

    # Insensitivity of reading A to the growth factor, the reviewer's point.
    growth_sensitivity = []
    for gg in (1.0, g, 6.0):
        t1 = invert(cost, ASTRA_PRICES, k, m_donor)
        t2 = invert(cost, ASTRA_PRICES, k, m_donor * gg)
        c = math.sqrt(t1["counted"] * t2["counted"])
        growth_sensitivity.append({"g": gg, "counted": c, "flops": c * FPT[ASTRA_MODEL_ID]})

    # Cross-check: Artificial Analysis measures Astra and GPT-5.6 Sol within 6% of each
    # other in counted tokens per trial on Terminal-Bench 2.1, so Sol's independently
    # inverted Terminal-Bench-Science figure scaled by that ratio is a separate reading.
    sol = aa["gpt-5-6-sol"]
    sol_counted = (int(sol["input_tokens"]) - int(sol["cacheable_input_tokens"])
                   + int(sol["answer_tokens"]) + int(sol["reasoning_tokens"]))
    astra_to_sol = (d_unc + d_out) / sol_counted
    sol_tbsci = [x for x in growth if x["model"] == "GPT-5.6 Sol"][0]["tbscience_counted_per_trial"]
    crosscheck = sol_tbsci * astra_to_sol
    # Sol ran under Codex; the four official pairs that run one model under both Terminus 2
    # and the lab's own CLI put a Terminus 2 run at this fraction of the CLI run's counted
    # tokens, which is the band the Sol reading has to be scaled through.
    t2_vs_cli = []
    for cli_file, t2_file, name in TERMINUS_PAIRS:
        a, b = subs[cli_file], subs[t2_file]
        ac = (int(a["uncached_input_tokens"]) + int(a["output_tokens"])) / int(a["n_trials"])
        bc = (int(b["uncached_input_tokens"]) + int(b["output_tokens"])) / int(b["n_trials"])
        t2_vs_cli.append({"model": name, "cli_per_trial": ac, "terminus2_per_trial": bc,
                          "ratio": bc / ac})
    cc_lo = crosscheck * min(x["ratio"] for x in t2_vs_cli)
    cc_hi = crosscheck * max(x["ratio"] for x in t2_vs_cli)

    calc = {
        "point_id": ASTRA_POINT_ID, "source": "Vals AI board, cost inversion",
        "model_id": ASTRA_MODEL_ID, "trials": ASTRA_TRIALS,
        "accuracy_pct": acc, "binomial_stderr_pct": se, "passes": round(acc / 100.0 * ASTRA_TRIALS),
        "cost_per_task_usd": cost, "mean_latency_sec": float(row["latency_sec"]),
        "prices_usd_per_m": list(ASTRA_PRICES),
        "donor_uncached": d_unc, "donor_cache_reads": d_cache, "donor_output": d_out,
        "k_uncached_over_output": k, "m_donor_cache_reads_over_counted": m_donor,
        "length_growth_factor": g, "length_growth_detail": growth,
        "vals_tb21_cost_per_task_usd": vals_tb21_cost,
        "aa_tb21_gross_cost_per_trial_usd": aa_cost_pt,
        "aa_tb21_undiscounted_cost_per_trial_usd": aa_gross_pt,
        "vals_over_aa_tb21_cost_ratio": vals_tb21_cost / aa_cost_pt,
        "vals_over_aa_tb21_undiscounted_ratio": vals_tb21_cost / aa_gross_pt,
        "m_implied_by_vals_tb21_cell": m_vals,
        "readings": readings, "growth_sensitivity": growth_sensitivity,
        "counted_tokens_per_task": tokens, "compute_flops": flops,
        "flops_per_token": FPT[ASTRA_MODEL_ID],
        "band_flops": [lo_tokens * FPT[ASTRA_MODEL_ID], hi_tokens * FPT[ASTRA_MODEL_ID]],
        "crosscheck_astra_to_sol_ratio_tb21": astra_to_sol,
        "crosscheck_counted_per_task": crosscheck,
        "terminus2_vs_cli_pairs": t2_vs_cli,
        "crosscheck_band_counted_per_task": [cc_lo, cc_hi],
        "implied_output_tokens_per_sec": [
            readings["B_vals_own_tb21_cell"]["transfer_2_length_corrected"]["output"] / float(row["latency_sec"]),
            readings["A_artificial_analysis_mix"]["transfer_1_no_length_correction"]["output"] / float(row["latency_sec"])],
        "human_time": ht, "ratio_to_human": acc / 100.0,
    }

    point = {
        "point_id": ASTRA_POINT_ID,
        "task": "Complete a Terminal-Bench-Science research workflow task",
        "task_category": "research_analysis",
        "task_description": (
            "One agent attempt at one Terminal-Bench-Science 0.1 task, averaged over the "
            "benchmark's 70 tasks at one trial each. Each task is a research workflow written "
            "and reviewed by practising scientists across five scientific domains, supplying an "
            "instruction and a Docker container with internet access; the Terminus 2 agent "
            "driving GPT-6 Astra works in the terminal for up to an eight-hour agent phase, "
            "then a verifier runs the task's tests. "
            "Scoring is strict pass/fail. The human unit is one domain expert completing the "
            "same task once."),
        "model_id": ASTRA_MODEL_ID,
        "compute_scope": "inference",
        "compute_flops": "%.1f" % flops,
        "human_skill": "expert",
        "human_time_scope": "task_performance",
        "human_time": "%.2f" % ht["expert_mean_sec"],
        "performance_vs_human": label(acc / 100.0),
        "comparison_issues": "different_attempt_selection",
        "compute_evidence": "derived_assumed_inputs",
        "human_time_evidence": "source_estimate",
        "performance_evidence": (
            "The run resolved %d of 70 tasks, %.2f%%, one graded run each (binomial standard "
            "error %.2f pp); tasks ending in an infrastructure error were re-attempted and a "
            "handful solved that way. No human attempt was scored: the authors' expert time "
            "estimates how long a domain expert needs to finish a task, so the implied baseline "
            "is completion."
            % (round(acc / 100.0 * ASTRA_TRIALS), acc, se)),
        "human_time_statistic": "mean",
        "human_time_subset": "not_applicable",
        "human_attempts": "not_applicable",
        "human_time_source": "%s; research/terminal-bench.md#%s" % (TBSCI_TASK_URL, ASTRA_POINT_ID),
        "human_time_method": "estimated",
        "compute_method": "params_tokens",
        "compute_statistic": "mean",
        "compute_subset": "all",
        "ai_attempts": str(ASTRA_TRIALS),
        "compute_source": "%s; research/terminal-bench.md#%s" % (TBSCI_URL, ASTRA_POINT_ID),
        "tokens": repr(tokens),
        "tokens_accounting": "input_cache_creation_output",
        "source_dataset": "Vals AI Terminal-Bench-Science 0.1 board",
        "source_record": (
            "%s, model openai/gpt-6-astra, Terminus 2 in a fixed configuration, pass@1 from a "
            "single run over the 70 tasks of Terminal-Bench-Science 0.1, board updated "
            "2026-09-11; task times from %s at commit "
            "ff55a1b0810a5cc2ebac3ebb007cbe6a26aa2e3b; performance: the same board's accuracy "
            "field" % (TBSCI_URL, TBSCI_TASK_URL)),
        "notes": (
            "Tokens are inverted from the board's $%.2f per task at Astra's 10.00/1.00/50.00 "
            "rates; no board publishes token counts for this run. Central is the geometric mean "
            "of two donor readings of the cache structure: Artificial Analysis's measured "
            "Terminal-Bench 2.1 mix for this model gives %.0f counted tokens, and reconciling "
            "this operator's own Terminal-Bench 2.1 cell, $%.4f a task against $%.4f of that "
            "volume priced gross, gives %.0f. Band %.2fe16 to %.2fe17. Cost and compute are not independent "
            "and error re-attempts sit inside the dollar. 100-600B active moves it 0.33-2.0x." % (
                cost, readings["A_artificial_analysis_mix"]["counted_tokens_per_task"],
                vals_tb21_cost, aa_gross_pt,
                readings["B_vals_own_tb21_cell"]["counted_tokens_per_task"],
                lo_tokens * FPT[ASTRA_MODEL_ID] / 1e16,
                hi_tokens * FPT[ASTRA_MODEL_ID] / 1e17)),
        "ai_cost_usd": "%.5f" % cost,
        "ai_cost_basis": "reported",
        "ai_cost_date": "2026-09-11",
        "human_cost_usd": "",
        "human_cost_basis": "not_available",
    }
    return point, calc


def invert_from_total(total_tokens, cost_usd, prices, k):
    """Counted tokens where a gross billed total is published as well as the cost."""
    p_u, p_c, p_o = prices
    o = (cost_usd * 1e6 - p_c * total_tokens) / (p_u * k - p_c * (k + 1) + p_o)
    return (k + 1) * o



def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    ht = human_time(args.sources)

    notes_extra = {
        "agen-tbench21-grok45-cursorcli": "40 of the 445 trials were disqualified for reward hacking; the token and cost totals include them.",
        "agen-tbench21-gpt56sol-codex": "32 of the 445 trials were disqualified for reward hacking; the token and cost totals include them. The reported cost reproduces at the family's launch rates, 5.00/0.50/30.00 per million, which OpenAI cut on 2026-08-21.",
        "agen-tbench21-gpt56luna-codex": "The reported cost reproduces at the launch rate 1.00/0.10/6.00 per million, which OpenAI cut 80% on 2026-07-30.",
        "agen-tbench21-gpt56terra-codex": "The reported cost reproduces at the launch rate 2.50/0.25/15.00 per million, which OpenAI cut 20% on 2026-07-30.",
        "agen-tbench21-glm51-claudecode": "The reported $277.14 is 2.26x the $122.52 these counters give at the GLM-5 list rates and 1.70x the $163 at GLM-5.3's, so this run's counter definitions are assumed rather than confirmed by a price check.",
        "agen-tbench21-fable5-claudecode": "Anthropic serves Fable 5 with an Opus 4.8 fallback, so some turns may have run on a smaller model. These counters at list price 1.59x the reported cost, as on every Claude Code run on this board.",
        "agen-tbench21-fable5-terminus2": "Anthropic serves Fable 5 with an Opus 4.8 fallback, so some turns may have run on a smaller model.",
        "agen-tbench21-opus47-claudecode": "The run logs 447 trials rather than the 445 that 89 tasks at 5 trials give. These counters at list price 1.56x the reported cost, as on every Claude Code run on this board.",
        "agen-tbench21-opus48-claudecode": "These counters at list price 1.21x the reported cost, as on every Claude Code run on this board.",
        "agen-tbench21-sonnet5-claudecode": "These counters at 3.00/0.30/15.00 price 1.34x the reported cost, as on every Claude Code run; the retained table carries no separate Sonnet 5 rate.",
        "agen-tbench21-aa-fable51": "The 150B prior is the Anthropic report's recommendation, not a disclosure; 60-400B moves the value 0.4-2.7x.",
        "agen-tbench21-aa-fable51-xhigh": "The same model ID as the max-effort row, served at xhigh; only the effort differs. The 150B prior is the Anthropic report's recommendation, not a disclosure.",
        "agen-tbench21-aa-fable51-high": "The same model ID as the max-effort row, served at high; only the effort differs. The 150B prior is the Anthropic report's recommendation, not a disclosure.",
        "agen-tbench21-aa-gpt6astra": "The 300B prior is ruled, not disclosed; 100-600B moves the value 0.33-2.0x.",
        "agen-tbench21-aa-gpt6astra-high": "The same model ID as the max-effort row, served at high; only the effort differs. The 300B prior is ruled, not disclosed.",
        "agen-tbench21-aa-gpt6astra-medium": "The same model ID as the max-effort row, served at medium; only the effort differs. The 300B prior is ruled, not disclosed.",
        "agen-tbench21-aa-gpt56sol": "A second harness, not a duplicate: the official Sol submission runs on Codex. The shared gpt-5-6-sol ID still carries 100B against the ruled 150B, so this value is 1.5x low until merge.",
        "agen-tbench21-aa-gpt56sol-xhigh": "The same model ID as the max-effort row, served at xhigh; only the effort differs. Like that row it carries the shared registry's 100B against the ruled 150B, so it is 1.5x low until merge.",
        "agen-tbench21-aa-gpt56terra": "Runs on Terminus 2, where the official board's Terra submission runs on Codex, so this is a second harness rather than a duplicate.",
        "agen-tbench21-aa-gpt56luna": "Runs on Terminus 2, where the official board's Luna submission runs on Codex, so this is a second harness rather than a duplicate.",
        "agen-tbench21-aa-fable5": "Runs at max effort, where the official board's Fable 5 Terminus 2 submission runs at high; Anthropic serves Fable 5 with an Opus 4.8 fallback.",
        "agen-tbench21-aa-opus5": "Cost is priced at the rates this board publishes for the model; Anthropic bills cache creation at 1.25x input, which this does not separate.",
        "agen-tbench21-aa-k2horizon": "The board publishes no price fields for this model, so the token counts cannot be priced and the cost columns stay empty.",
        "agen-tbench21-aa-musespark13": "The 100B prior is a within-lab price-ratio transfer from Muse Glimmer, whose own 30B rests only on this board; 50-170B moves the value 0.5-1.7x.",
        "agen-tbench21-aa-mistralmedium35": "Resolution 50.56% sits 0.1 standard errors above the half-of-human guide, so the row is a close call under the exclusion ruling.",
        "agen-tbench21-aa-minimaxm3": "The coefficient is the root registry's canonical MiniMax-M3 record, 23B active from the developer summary and the published config.",
    }

    p1, c1, d1 = build_official(args.sources, ht, notes_extra)
    p2, c2, d2 = build_aa(args.sources, ht, notes_extra)
    d3 = build_dispositions(args.sources)
    p3, c3 = build_astra(args.sources)

    points = sorted(p1 + p2 + [p3], key=lambda r: r["point_id"])
    with open(os.path.join(args.out, "points.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=POINT_FIELDS)
        w.writeheader()
        w.writerows(points)

    with open(os.path.join(args.out, "models.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=MODEL_FIELDS)
        w.writeheader()
        w.writerows(sorted(NEW_MODELS, key=lambda r: r["model_id"]))

    with open(os.path.join(args.out, "dispositions.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=DISPOSITION_FIELDS)
        w.writeheader()
        w.writerows(d1 + d2 + d3)

    with open(os.path.join(args.out, "calculations.json"), "w") as fh:
        json.dump({"human_time": ht, "points": c1 + c2, "tbscience_astra": c3},
                  fh, indent=1, sort_keys=True)

    print("points %d  models %d  dispositions %d" % (len(points), len(NEW_MODELS), len(d1 + d2 + d3)))
    print("human_time_sec %.4f (mean of %d author expert estimates over %d tasks)"
          % (ht["expert_mean_sec"], ht["n_with_expert_estimate"], ht["n_tasks"]))


if __name__ == "__main__":
    main()
