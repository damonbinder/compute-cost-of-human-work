#!/usr/bin/env python3
"""Build the per-task Terminal-Bench-Science 0.1 candidate rows.

Reads only the retained extracts in agent-work/sources/terminal-bench-science/
and dataset/models.csv, and writes the candidate points CSV, a per-row
calculation dump and the withheld-cell dispositions. Nothing here modifies
dataset/points.csv or dataset/models.csv.

Usage:
  python3 dataset/research/terminal-bench-science/build_rows.py \
      --sources agent-work/sources/terminal-bench-science \
      --models dataset/models.csv \
      --out agent-work/candidates \
      --derived agent-work/derived/terminal-bench-science
"""

import argparse
import collections
import csv
import json
import statistics
from pathlib import Path

# Per-call new tokens assumed when turning a trial's cache-read total into a
# mean attended context. 2,800 is the median over the sixteen Terminal-Bench
# 2.1 official leaderboard submissions, the constant
# research/attention-correction.md#metr-cache-reads already adopts.
N_NEW_PER_CALL = 2800.0
CONTEXT_CAP = 200000.0

# Leaderboard entry label -> (model_id, short id fragment, cost usable).
# Cost is usable where the hub's own per-trial cost_usd sums to the
# leaderboard's published total for the entry. It does not for Kimi K3 and
# GLM 5.3, whose Anthropic-compatible endpoints the hub priced at Anthropic
# rates; those rows carry no cost.
ENTRIES = {
    "Opus 5":        ("claude-opus-5-max", "opus5",      True),
    "GPT-5.6 Sol":   ("gpt-5-6-sol",       "gpt56sol",   True),
    "Fable 5":       ("claude-fable-5",    "fable5",     True),
    "Opus 4.8":      ("claude-opus-4-8",   "opus48",     True),
    "GPT-5.6 Terra": ("gpt-5-6-terra",     "gpt56terra", True),
    "GLM 5.3":       ("glm-5.3",           "glm53",      False),
    "Kimi K3":       ("kimi-k3",           "kimik3",     False),
    "Grok 4.6":      ("grok-4-6",          "grok46",     True),
    "GPT-5.6 Luna":  ("gpt-5-6-luna",      "gpt56luna",  True),
}

COMMIT = "ff55a1b0810a5cc2ebac3ebb007cbe6a26aa2e3b"
TASKS_URL = ("https://github.com/harbor-framework/terminal-bench-science/tree/"
             + COMMIT + "/tasks")
BOARD_URL = "https://www.terminal-bench-science.ai/"
NOTE = "research/terminal-bench-science/terminal-bench-science.md"

HEADER = ["point_id", "task", "task_category", "task_description", "model_id",
          "compute_scope", "compute_flops", "human_skill", "human_time_scope",
          "human_time", "performance_vs_human", "comparison_issues",
          "compute_evidence", "human_time_evidence", "performance_evidence",
          "human_time_statistic", "human_time_subset", "human_attempts",
          "human_time_source", "compute_method", "compute_statistic",
          "compute_subset", "ai_attempts", "compute_source", "tokens",
          "tokens_accounting", "source_dataset", "source_record", "notes",
          "ai_cost_usd", "ai_cost_basis", "ai_cost_date", "human_cost_usd",
          "human_cost_basis", "attention_context", "attention_ratio"]


def num(x):
    return float(x) if x not in ("", None) else None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--sources", required=True)
    p.add_argument("--models", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--derived", required=True)
    a = p.parse_args()
    src, out, derived = Path(a.sources), Path(a.out), Path(a.derived)
    out.mkdir(parents=True, exist_ok=True)
    derived.mkdir(parents=True, exist_ok=True)

    trials = list(csv.DictReader((src / "tbscience-hub-trials.csv")
                                 .open(newline="", encoding="utf-8")))
    meta = {r["task"]: r for r in csv.DictReader(
        (src / "tbscience-task-metadata.csv").open(newline="", encoding="utf-8"))}
    models = {r["model_id"]: r for r in csv.DictReader(
        Path(a.models).open(newline="", encoding="utf-8"))}
    board = json.loads((src / "tbscience-leaderboard-api.json")
                       .read_text(encoding="utf-8"))
    entry_metrics = {r["metadata"]["model_display"]["label"]: r
                     for r in board["rows"]}

    by_pair = collections.defaultdict(list)
    for t in trials:
        by_pair[(t["entry_model"], t["task"])].append(t)

    rows, calcs, dispositions = [], [], []
    for (label, task), ts in sorted(by_pair.items()):
        model_id, short, cost_ok = ENTRIES[label]
        m = models[model_id]
        md = meta[task]
        hours = float(md["expert_time_estimate_hours"])
        good = [t for t in ts if t["reward"] == "1"]
        if not good:
            dispositions.append(dict(
                entry=label, model_id=model_id, task=task,
                expert_hours=hours, solved=0, trials=len(ts),
                reason="no trial resolved the task; the row would be "
                       "substantially below the completion the expert "
                       "estimate implies"))
            continue
        # Counted quantity: fresh input plus cache creation, plus output.
        # input_tokens is gross and includes cache_tokens (cache reads).
        proc = [int(t["input_tokens"]) - int(t["cache_tokens"])
                + int(t["output_tokens"]) for t in good]
        cache = [int(t["cache_tokens"]) for t in good]
        P = statistics.fmean(proc)
        C = statistics.fmean(cache)
        # Mean attended context from the trajectory's own turn structure:
        # cache reads are the sum of per-call prefixes, so with n_new tokens
        # processed per call the call count is P / n_new and the mean prefix
        # is C / (P / n_new) = (C / P) * n_new.
        ctx = min((C / P) * N_NEW_PER_CALL, P / 2.0, CONTEXT_CAP)
        L = float(m["attention_layers"])
        W = float(m["attention_width"])
        nact = float(m["active_parameters"])
        ratio = 2.0 * L * W * ctx / nact
        fpt = float(m["flops_per_token"])
        flops = fpt * P * (1.0 + ratio)

        costs = [num(t["cost_usd"]) for t in good]
        have_cost = cost_ok and all(c is not None for c in costs)
        cost = statistics.fmean(costs) if have_cost else None
        date = min(t["started_at"][:10] for t in good)
        agent = good[0]["agent_name"]
        agent_ver = good[0]["agent_version"]
        effort = good[0]["reasoning_effort"]
        served = good[0]["model_name"]
        entry_acc = entry_metrics[label]["metrics"]["accuracy"]

        pid = "agen-tbsci-%s-%s" % (task, short)
        desc = md["description"].rstrip()
        if not desc.endswith("."):
            desc += "."
        task_desc = (
            "One successful agent attempt at the Terminal-Bench-Science 0.1 "
            "task %s, in the %s domain (%s). %s The agent is handed the "
            "instruction and a Docker container with internet access, four "
            "CPUs, %s MB of memory and no GPU, and works in the terminal for "
            "up to an eight-hour agent phase; a separate verifier container "
            "then runs the task's tests, scored strict pass/fail. The %s "
            "agent %s drives %s at %s reasoning effort. The human unit is one "
            "domain expert completing the same task once."
            % (task, md["domain"].replace("-", " "),
               md["field"].replace("-", " "), desc, md["memory_mb"],
               agent, agent_ver, served, effort))

        perf = (
            "The model resolved this task in %d of its %d graded trials, so "
            "the task was completed. No human attempt was scored or timed: "
            "the task author's expert time estimate is how long a focused "
            "domain expert needs to finish this task, so the human baseline "
            "it implies is completion, which a resolved trial meets. The same "
            "run resolved %.2f%% of the benchmark's 210 trials overall."
            % (len(good), len(ts), entry_acc))

        note_bits = [
            "Compute is the mean over the %d resolved trial%s; cache reads of "
            "%s per resolved trial are excluded from the counted tokens and "
            "enter only the attended context."
            % (len(good), "" if len(good) == 1 else "s",
               format(round(C), ",")),
            "attention_context is (cache reads / counted tokens) x 2,800 "
            "assumed new tokens per call, the cadence constant in "
            "research/attention-correction.md; the sixteen Terminal-Bench 2.1 "
            "submissions span 1,651 to 13,460 there, which moves this row's "
            "attention term by about a factor of five either way.",
        ]
        if len(ts) - len(good):
            note_bits.append(
                "%d of the %d trials failed; their compute is not counted, so "
                "the figure is the cost of one success and not the expected "
                "cost of reaching one." % (len(ts) - len(good), len(ts)))
        if not cost_ok:
            note_bits.append(
                "No cost is recorded: Harbor Hub priced this "
                "Anthropic-compatible endpoint at Anthropic's 5.00/0.50/25.00 "
                "per million, so its per-trial cost_usd sums to 1.67x (Kimi "
                "K3) and 2.49x (GLM 5.3) the leaderboard's own published total "
                "for the run, which the provider's rates reproduce.")
        if model_id == "claude-fable-5":
            note_bits.append(
                "Anthropic serves Fable 5 with an Opus 4.8 fallback, so a "
                "share of the turns may have run on a different model.")

        rows.append(dict(
            point_id=pid,
            task="Complete the Terminal-Bench-Science task " + task,
            task_category="research_analysis",
            task_description=task_desc,
            model_id=model_id,
            compute_scope="inference",
            compute_flops=repr(flops),
            human_skill="expert",
            human_time_scope="task_performance",
            human_time=repr(hours * 3600.0),
            performance_vs_human="match",
            comparison_issues="none_identified",
            compute_evidence="derived_assumed_inputs",
            human_time_evidence="source_estimate",
            performance_evidence=perf,
            human_time_statistic="point_estimate",
            human_time_subset="not_applicable",
            human_attempts="not_applicable",
            human_time_source="%s/%s/%s/%s/task.toml; %s#human-time"
                              % (TASKS_URL, md["domain"], md["field"], task,
                                 NOTE),
            compute_method="params_tokens",
            compute_statistic="mean",
            compute_subset="successful",
            ai_attempts=str(len(good)),
            compute_source="%s; %s#compute; research/attention-correction.md"
                           % ("; ".join(
                               "https://hub.harborframework.com/jobs/%s?tab=trials" % j
                               for j in sorted({t["job_id"] for t in good})), NOTE),
            tokens=repr(P),
            tokens_accounting="input_cache_creation_output",
            source_dataset="Terminal-Bench-Science 0.1 official leaderboard",
            source_record=(
                "%s, leaderboard v0-1-eval entry %s + %s (%s, reasoning effort "
                "%s), 3 trials of each of the 70 tasks; resolved trials "
                "%s on Harbor Hub jobs %s; task definition and expert time "
                "estimate from the repository at commit %s; performance: the "
                "same leaderboard's per-task trial matrix"
                % (BOARD_URL, label, good[0]["entry_agent"], served, effort,
                   ", ".join(t["trial_id"] for t in good),
                   ", ".join(sorted({t["job_id"] for t in good})), COMMIT)),
            notes=" ".join(note_bits),
            ai_cost_usd=("%.5f" % cost) if cost is not None else "",
            ai_cost_basis="reported" if cost is not None else "not_available",
            ai_cost_date=date if cost is not None else "",
            human_cost_usd="",
            human_cost_basis="not_available",
            attention_context=repr(round(ctx, 1)),
            attention_ratio=repr(round(ratio, 4)),
        ))
        calcs.append(dict(
            point_id=pid, entry=label, model_id=model_id, task=task,
            domain=md["domain"], expert_hours=hours,
            trials=len(ts), resolved=len(good),
            mean_counted_tokens=P, mean_cache_reads=C, cache_over_counted=C / P,
            attention_context=ctx, attention_ratio=ratio,
            flops_per_token=fpt, compute_flops=flops,
            flops_per_human_second=flops / (hours * 3600.0),
            mean_cost_usd=cost if cost is not None else "",
            job_ids=" ".join(sorted({t["job_id"] for t in good}))))

    rows.sort(key=lambda r: r["point_id"])
    with (out / "terminal-bench-science.csv").open(
            "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=HEADER, lineterminator="\r\n")
        w.writeheader()
        w.writerows(rows)
    with (derived / "calculations.csv").open(
            "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(calcs[0]))
        w.writeheader()
        w.writerows(sorted(calcs, key=lambda r: r["point_id"]))
    with (out / "terminal-bench-science-dispositions.csv").open(
            "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(dispositions[0]))
        w.writeheader()
        w.writerows(sorted(dispositions, key=lambda r: (r["entry"], r["task"])))
    print(json.dumps({"rows": len(rows), "dispositions": len(dispositions),
                      "models_used": sorted({r["model_id"] for r in rows})},
                     indent=2))


if __name__ == "__main__":
    main()
