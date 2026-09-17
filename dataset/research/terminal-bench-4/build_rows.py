#!/usr/bin/env python3
"""Build the Terminal-Bench 4.0 candidate rows.

Reads only the retained extracts in agent-work/sources/terminal-bench-4/ and
writes candidate points, candidate models, the withheld-cell dispositions and a
calculations dump. Nothing here touches dataset/points.csv or dataset/models.csv.

    python3 dataset/research/terminal-bench-4/build_rows.py \
        --sources agent-work/sources/terminal-bench-4 \
        --out agent-work/derived/terminal-bench-4
"""

import argparse
import collections
import csv
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from task_descriptions import TASK_SUMMARY  # noqa: E402

POINT_HEADER = [
    "point_id", "task", "task_category", "task_description", "model_id",
    "compute_scope", "compute_flops", "human_skill", "human_time_scope",
    "human_time", "performance_vs_human", "comparison_issues",
    "compute_evidence", "human_time_evidence", "performance_evidence",
    "human_time_statistic", "human_time_subset", "human_attempts",
    "human_time_source", "compute_method", "compute_statistic",
    "compute_subset", "ai_attempts", "compute_source", "tokens",
    "tokens_accounting", "source_dataset", "source_record", "notes",
    "ai_cost_usd", "ai_cost_basis", "ai_cost_date", "human_cost_usd",
    "human_cost_basis", "attention_context", "attention_ratio"]

MODEL_HEADER = [
    "model_id", "model", "company", "model_release_date",
    "model_release_source", "flops_per_token", "flops_per_token_method",
    "active_parameters", "active_parameters_basis", "active_parameters_low",
    "active_parameters_high", "encoder_parameters", "encoder_parameters_basis",
    "decoder_parameters", "decoder_parameters_basis", "parameter_source",
    "notes", "attention_layers", "attention_width", "attention_basis"]

CAP = 200000.0
MATCH_LOW, MATCH_HIGH = 0.85, 1.15

# New tokens processed per call. The median over the sixteen Terminal-Bench 2.1
# official submissions, the constant research/attention-correction.md already
# adopts for the METR rebuild and terminal-bench-science uses for the same
# cache-implied context.
N_NEW_PER_CALL = 2800.0

# model_id -> (active_parameters, attention_layers, attention_width)
SHAPES = {
    "claude-opus-5-max": (1.0e11, 80, 10240),
    "claude-opus-4-8": (1.0e11, 80, 10240),
    "claude-fable-5": (1.5e11, 91, 11648),
    "claude-fable-5-1": (1.5e11, 91, 11648),
    "claude-sonnet-5": (1.0e11, 80, 10240),
    "glm-5.3": (4.0e10, 59, 7552),
    "gpt-5-6-sol": (1.5e11, 91, 11648),
    "gpt-5-6-terra": (2.0e10, 47, 6016),
    "gpt-5-6-luna": (8.0e9, 34, 4352),
    "grok-4-5": (1.0e11, 80, 10240),
    "grok-4-6": (1.0e11, 80, 10240),
    "gemini-3-8-flash": (4.0e10, 59, 7552),
    "gemini-3-7-flash": (4.0e10, 59, 7552),
    "gpt-6-astra": (3.0e11, 115, 14720),
    "claude-fable-5-1-aa": (1.5e11, 91, 11648),
}

# leaderboard run file stem -> row-building metadata
RUNS = {
    "2026-08-26-anthropic-claude-opus-5-max-claude-code": dict(
        model_id="claude-opus-5-max", short="opus5", label="Opus 5",
        agent="Claude Code", effort="max"),
    "2026-08-26-anthropic-claude-opus-4-8-max-claude-code": dict(
        model_id="claude-opus-4-8", short="opus48", label="Opus 4.8",
        agent="Claude Code", effort="max"),
    "2026-08-26-anthropic-claude-fable-5-max-claude-code": dict(
        model_id="claude-fable-5", short="fable5", label="Claude Fable 5",
        agent="Claude Code", effort="max"),
    "2026-09-02-anthropic-claude-fable-5-1-max-claude-code": dict(
        model_id="claude-fable-5-1", short="fable51", label="Claude Fable 5.1",
        agent="Claude Code", effort="max"),
    "2026-08-26-anthropic-claude-sonnet-5-max-claude-code": dict(
        model_id="claude-sonnet-5", short="sonnet5", label="Claude Sonnet 5",
        agent="Claude Code", effort="max"),
    "2026-08-26-anthropic-glm-5-3-max-claude-code": dict(
        model_id="glm-5.3", short="glm53", label="GLM-5.3",
        agent="Claude Code", effort="max"),
    "2026-08-26-openai-gpt-5-6-sol-max-codex": dict(
        model_id="gpt-5-6-sol", short="gpt56sol", label="GPT-5.6 Sol",
        agent="Codex", effort="max"),
    "2026-08-26-openai-gpt-5-6-terra-max-codex": dict(
        model_id="gpt-5-6-terra", short="gpt56terra", label="GPT-5.6 Terra",
        agent="Codex", effort="max"),
    "2026-08-26-openai-gpt-5-6-luna-max-codex": dict(
        model_id="gpt-5-6-luna", short="gpt56luna", label="GPT-5.6 Luna",
        agent="Codex", effort="max"),
    "2026-08-26-xai-grok-4-5-none-grok-build": dict(
        model_id="grok-4-5", short="grok45", label="Grok 4.5",
        agent="Grok Build", effort=None),
    "2026-08-26-xai-grok-4-6-none-grok-build": dict(
        model_id="grok-4-6", short="grok46", label="Grok 4.6",
        agent="Grok Build", effort=None),
    "2026-09-01-gemini-gemini-3-8-flash-high-mini-swe-agent": dict(
        model_id="gemini-3-8-flash", short="gemini38flash",
        label="Gemini 3.8 Flash", agent="mini-swe-agent", effort="high"),
    "2026-09-02-gemini-gemini-3-7-flash-high-mini-swe-agent": dict(
        model_id="gemini-3-7-flash", short="gemini37flash",
        label="Gemini 3.7 Flash", agent="mini-swe-agent", effort="high"),
}

# Artificial Analysis slug -> (model_id, point suffix, served effort)
AA_ROWS = {
    "gpt-6-astra-xhigh": ("gpt-6-astra", "gpt6astra-xhigh", "xhigh"),
    "gpt-6-astra": ("gpt-6-astra", "gpt6astra", "max"),
    "gpt-6-astra-high": ("gpt-6-astra", "gpt6astra-high", "high"),
    "gpt-6-astra-medium": ("gpt-6-astra", "gpt6astra-medium", "medium"),
    "claude-fable-5-1-xhigh": ("claude-fable-5-1", "fable51-xhigh", "xhigh"),
    "claude-fable-5-1": ("claude-fable-5-1", "fable51", "max"),
    "claude-fable-5-1-high": ("claude-fable-5-1", "fable51-high", "high"),
    "claude-opus-5": ("claude-opus-5-max", "opus5", "max"),
}

LEAN_TASKS = {"takens-embedding-lean", "coq-block-bound"}

NOTE_REF = "research/terminal-bench-4/terminal-bench-4.md"


def sig(x, n):
    if x == 0:
        return 0.0
    return round(x, -int(math.floor(math.log10(abs(x)))) + (n - 1))


def attention(tokens, cache_reads, model_id):
    """Mean attended context from the run's own cache reads.

    Cache reads are the sum of the per-call prefixes: on call i the harness
    re-reads prefix_i tokens and processes n new ones, so C = sum(prefix_i) and
    P = sum(n_i). At a roughly constant n the call count is P / n and the mean
    prefix is C / (P / n) = (C / P) * n. The append-only bound P / 2 and the
    file's 200,000 cap stay as ceilings.
    """
    active, layers, width = SHAPES[model_id]
    ctx = min((cache_reads / tokens) * N_NEW_PER_CALL, tokens / 2.0, CAP)
    ratio = 2.0 * layers * width * ctx / active
    return ctx, ratio


def label(ratio):
    if ratio >= MATCH_HIGH:
        return "above"
    if ratio >= MATCH_LOW:
        return "match"
    return "below"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    src, out = Path(a.sources), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    tasks = {r["slug"]: r for r in
             csv.DictReader(open(src / "tb40-task-time-estimates.csv", newline=""))}
    subs = {r["submission_file"].replace(".json", ""): r for r in
            csv.DictReader(open(src / "tb40-leaderboard-submissions.csv", newline=""))}
    trials = list(csv.DictReader(open(src / "tb40-hub-trials.csv", newline="")))

    cells = collections.defaultdict(list)
    for t in trials:
        cells[(t["run"], t["task"].split("/")[-1])].append(t)

    points, disp, calc = [], [], {}
    for (run, slug), rs in sorted(cells.items()):
        meta, sub, tm = RUNS[run], subs[run], tasks[slug]
        k = sum(1 for r in rs if r["reward"] == "1")
        n = len(rs)
        ratio = k / n
        tok_rs = [r for r in rs if r["input_tokens"] not in ("", "None")]
        counted = [int(r["input_tokens"]) - int(r["cache_tokens"]) + int(r["output_tokens"])
                   for r in tok_rs]
        tokens = sum(counted) / len(counted) if counted else 0.0
        cost_rs = [float(r["cost_usd"]) for r in rs if r["cost_usd"] not in ("", "None")]
        cost = sum(cost_rs) / len(cost_rs) if cost_rs else None
        human = float(tm["expert_time_estimate_hours"]) * 3600.0
        if k < 3:
            disp.append(dict(
                run=run, task=slug, model_id=meta["model_id"], trials=n,
                resolved=k, resolution_rate=round(ratio, 4),
                expert_time_hours=tm["expert_time_estimate_hours"],
                counted_tokens_per_trial=round(tokens, 2),
                reason=("no trial resolved the task" if k == 0 else
                        "resolved in a minority of repeats (%d of %d)" % (k, n))))
            continue
        cache_mean = (sum(int(r["cache_tokens"]) for r in tok_rs) / len(tok_rs)
                      if tok_rs else 0.0)
        ctx, r_att = attention(tokens, cache_mean, meta["model_id"])
        fpt = 2.0 * SHAPES[meta["model_id"]][0]
        flops = tokens * fpt * (1.0 + r_att)
        pid = "agen-tb40-%s-%s" % (slug, meta["short"])
        effort = (" at %s reasoning effort" % meta["effort"]) if meta["effort"] else ""
        desc = ("%s. One agent attempt at the Terminal-Bench 4.0 task `%s`, "
                "averaged over the %d trials of this run. The %s agent driving %s%s "
                "works in the task's Docker container with internet access under an "
                "8-hour agent timeout, and a separate verifier container runs the "
                "task's tests. Success is that pass/fail suite. The human unit is one "
                "domain expert completing the same task once."
                % (TASK_SUMMARY[slug], slug, n, meta["agent"], meta["label"], effort))
        perf = ("The model resolved %d of its %d repeats of this task (%.1f%%). No "
                "human attempt at the task was timed or scored: the task author's "
                "expert time estimates how long a focused domain expert needs to "
                "complete it, so the human baseline it implies is completion and the "
                "resolution rate is read against 100%%." % (k, n, 100 * ratio))
        notes = ("Counted tokens are the run's own per-trial records: %s gross input "
                 "less %s cache reads plus %s output, summed over the %d trials and "
                 "divided by %d. The task author's expert estimate is %s h. Cache reads "
                 "are excluded; the Harbor Hub field named uncached_input_tokens in the "
                 "leaderboard submission is gross input, established by the per-trial "
                 "price solve in the research note. attention_context is the same "
                 "records' cache reads over counted tokens times 2,800 new tokens per "
                 "call, not the half-counted-tokens fallback; the sixteen Terminal-Bench "
                 "2.1 submissions bracket that constant at 1,651 to 13,460, which moves "
                 "the attention term by about a factor of five either way."
                 % (f"{sum(int(r['input_tokens']) for r in tok_rs):,}",
                    f"{sum(int(r['cache_tokens']) for r in tok_rs):,}",
                    f"{sum(int(r['output_tokens']) for r in tok_rs):,}",
                    len(tok_rs), len(tok_rs), tm["expert_time_estimate_hours"]))
        row = {
            "point_id": pid,
            "task": "Terminal-Bench 4.0: %s" % slug,
            "task_category": ("mathematics_puzzles" if slug in LEAN_TASKS else "coding"),
            "task_description": desc,
            "model_id": meta["model_id"],
            "compute_scope": "inference",
            "compute_flops": flops,
            "human_skill": "expert",
            "human_time_scope": "task_performance",
            "human_time": human,
            "performance_vs_human": label(ratio),
            "comparison_issues": "different_attempt_selection",
            "compute_evidence": "derived_assumed_inputs",
            "human_time_evidence": "source_estimate",
            "performance_evidence": perf,
            "human_time_statistic": "point_estimate",
            "human_time_subset": "not_applicable",
            "human_attempts": "not_applicable",
            "human_time_source": ("https://github.com/harbor-framework/terminal-bench/blob/"
                                  "v4.0.0/tasks/%s/task.toml; %s#human-time" % (slug, NOTE_REF)),
            "compute_method": "params_tokens",
            "compute_statistic": "mean",
            "compute_subset": "all",
            "ai_attempts": n,
            "compute_source": ("https://hub.harborframework.com/jobs/%s; %s#compute; "
                               "research/attention-correction.md"
                               % (sub["job_id"], NOTE_REF)),
            "tokens": tokens,
            "tokens_accounting": "input_cache_creation_output",
            "source_dataset": "Terminal-Bench 4.0 official leaderboard",
            "source_record": (
                "https://github.com/harbor-framework/terminal-bench/blob/main/leaderboard/"
                "submissions/%s.json; per-trial records for task %s from the run's Harbor "
                "Hub job https://hub.harborframework.com/jobs/%s retrieved 2026-09-14; "
                "model %s, agent %s %s, reasoning_effort %s, run dated %s; performance: "
                "the reward field of the same per-trial records"
                % (run, slug, sub["job_id"], sub["model_name"], sub["agent"],
                   sub["agent_version"], sub["reasoning_effort"] or "none", sub["date"])),
            "notes": notes,
            "ai_cost_usd": ("" if cost is None else round(cost, 5)),
            "ai_cost_basis": ("not_available" if cost is None else "reported"),
            "ai_cost_date": ("" if cost is None else sub["date"]),
            "human_cost_usd": "",
            "human_cost_basis": "not_available",
            "attention_context": sig(ctx, 6),
            "attention_ratio": sig(r_att, 4),
        }
        points.append(row)
        calc[pid] = dict(run=run, task=slug, trials=n, resolved=k,
                         gross_input=sum(int(r["input_tokens"]) for r in tok_rs),
                         cache_reads=sum(int(r["cache_tokens"]) for r in tok_rs),
                         output=sum(int(r["output_tokens"]) for r in tok_rs),
                         counted_tokens_per_trial=tokens,
                         flops_per_token=fpt, attention_context=ctx,
                         attention_ratio=r_att, compute_flops=flops,
                         human_time=human, cost_per_trial=cost)

    # Artificial Analysis collection rows
    aa = {r["aa_slug"]: r for r in
          csv.DictReader(open(src / "aa-terminalbench-v4-0-token-counts.csv", newline=""))}
    aa_human = sum(float(t["expert_time_estimate_hours"]) for t in tasks.values()) / len(tasks) * 3600
    for slug, (model_id, suffix, effort) in AA_ROWS.items():
        r = aa[slug]
        gross, cacheable = int(r["input_tokens"]), int(r["cacheable_input_tokens"])
        ans, rea = int(r["answer_tokens"]), int(r["reasoning_tokens"])
        tokens = (gross - cacheable + ans + rea) / 198.0
        score = float(r["score"])
        ctx, r_att = attention(tokens, cacheable / 198.0, model_id)
        fpt = 2.0 * SHAPES[model_id][0]
        flops = tokens * fpt * (1.0 + r_att)
        se = math.sqrt(score * (1 - score) / 198.0)
        pid = "agen-tb40-aa-%s" % suffix
        pu, pch, pcw, po = (float(r["price_1m_input_usd"]), float(r["price_1m_cache_hit_usd"]),
                            float(r["price_1m_cache_write_usd"] or r["price_1m_input_usd"]),
                            float(r["price_1m_output_usd"]))
        cost = ((gross - cacheable) * pu + cacheable * pch + (ans + rea) * po) / 1e6 / 198.0
        points.append({
            "point_id": pid,
            "task": "Solve a Terminal-Bench 4.0 terminal task",
            "task_category": "coding",
            "task_description": (
                "One agent attempt at one Terminal-Bench 4.0 task, averaged over the "
                "benchmark's 66 tasks with 198 trials in the run. Each task supplies a "
                "natural-language instruction and a Docker container; the agent works in "
                "the terminal under an 8-hour agent timeout, with %s served at %s "
                "reasoning effort, and a separate verifier runs the task's tests. Success "
                "is the task's own pass/fail test suite. The human unit is one domain "
                "expert completing the same task once." % (r["aa_name"], effort)),
            "model_id": model_id,
            "compute_scope": "inference",
            "compute_flops": flops,
            "human_skill": "expert",
            "human_time_scope": "task_performance",
            "human_time": round(aa_human, 2),
            "performance_vs_human": label(score),
            "comparison_issues": "different_attempt_selection",
            "compute_evidence": "derived_assumed_inputs",
            "human_time_evidence": "source_estimate",
            "performance_evidence": (
                "The run resolved %.2f%% of its 198 trials (standard error %.2f pp). No "
                "human attempt at these tasks was timed or scored: the task authors' "
                "expert time estimates how long a focused domain expert needs to complete "
                "the task, so the human baseline they imply is completion and the "
                "resolution rate is read against 100%%." % (100 * score, 100 * se)),
            "human_time_statistic": "mean",
            "human_time_subset": "not_applicable",
            "human_attempts": "not_applicable",
            "human_time_source": ("https://github.com/harbor-framework/terminal-bench/tree/"
                                  "v4.0.0/tasks; %s#human-time" % NOTE_REF),
            "compute_method": "params_tokens",
            "compute_statistic": "mean",
            "compute_subset": "all",
            "ai_attempts": 198,
            "compute_source": ("https://artificialanalysis.ai/evaluations/terminalbench-v4-0; "
                               "%s#compute; research/attention-correction.md" % NOTE_REF),
            "tokens": tokens,
            "tokens_accounting": "input_cache_creation_output",
            "source_dataset": "Artificial Analysis Terminal-Bench v4.0 board",
            "source_record": (
                "https://artificialanalysis.ai/evaluations/terminalbench-v4-0, model slug "
                "%s (%s), canonicalEvalTokenCounts.terminalbenchV40 and terminalbenchV40 "
                "score in the page payload retrieved 2026-09-14; pass@1 over 3 repeats of "
                "each of the 66 tasks; performance: the same payload field"
                % (slug, r["aa_name"])),
            "notes": (
                "Cacheable input of %s is excluded as cache reads; the counted quantity is "
                "%s uncached input plus %s answer and %s reasoning tokens over 198 trials. "
                "This board publishes only collection totals, so the row is the collection, "
                "positioned at the mean of the 66 task authors' expert estimates; the "
                "per-task rows in this batch come from the official leaderboard's Harbor Hub "
                "records instead. attention_context is cacheable input over counted tokens "
                "times 2,800 new tokens per call, the board's own cache structure rather "
                "than the half-counted-tokens fallback. Median expert estimate is 14,400 s."
                % (f"{cacheable:,}", f"{gross - cacheable:,}", f"{ans:,}", f"{rea:,}")),
            "ai_cost_usd": round(cost, 5),
            "ai_cost_basis": "list_price",
            "ai_cost_date": "2026-09-14",
            "human_cost_usd": "",
            "human_cost_basis": "not_available",
            "attention_context": sig(ctx, 6),
            "attention_ratio": sig(r_att, 4),
        })
        calc[pid] = dict(source="artificial-analysis", slug=slug, score=score,
                         counted_tokens_per_trial=tokens, flops_per_token=fpt,
                         attention_context=ctx, attention_ratio=r_att,
                         compute_flops=flops, cost_per_trial=cost)

    for slug, r in aa.items():
        if slug in AA_ROWS:
            continue
        score = float(r["score"])
        se = math.sqrt(score * (1 - score) / 198.0) or 1e-9
        disp.append(dict(run="artificial-analysis", task="collection", model_id=slug,
                         trials=198, resolved=round(score * 198),
                         resolution_rate=round(score, 4), expert_time_hours="",
                         counted_tokens_per_trial="",
                         reason=("%.1f%% resolution, %.1f standard errors below the "
                                 "half-of-human guide" % (100 * score, (0.5 - score) / se))))

    with (out / "points.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=POINT_HEADER)
        w.writeheader()
        w.writerows(points)
    with (out / "dispositions.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(disp[0].keys()))
        w.writeheader()
        w.writerows(disp)
    (out / "calculations.json").write_text(json.dumps(calc, indent=1, sort_keys=True))

    per_task = [p for p in points if p["point_id"].startswith("agen-tb40-") and
                not p["point_id"].startswith("agen-tb40-aa-")]
    print(json.dumps(dict(points=len(points), per_task=len(per_task),
                          aa_collection=len(points) - len(per_task),
                          dispositions=len(disp),
                          distinct_tasks=len({p["task"] for p in per_task}),
                          match=sum(1 for p in points if p["performance_vs_human"] == "match"),
                          below=sum(1 for p in points if p["performance_vs_human"] == "below"),
                          human_time_min=min(p["human_time"] for p in per_task),
                          human_time_max=max(p["human_time"] for p in per_task)), indent=1))


if __name__ == "__main__":
    main()
