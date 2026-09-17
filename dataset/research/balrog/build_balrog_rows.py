#!/usr/bin/env python3
"""Build the BALROG Crafter candidate points and the calculation record.

Inputs (all read-only):
  --sources           directory holding the retained BALROG/Crafter evidence:
                        balrog-crafter-env-summaries.json
                        balrog-crafter-episodes.csv
                        balrog-harness-commits.json
                        crafter-human-episodes.csv
  --dataset-models    the existing dataset's models.csv (for reused model_ids)
  --candidate-models  this batch's models.csv (for newly added model_ids)

Outputs (both written fresh; neither path need be the published one):
  --points-out   candidate rows in the dataset point schema
  --calc-out     JSON record of every input, intermediate and result

Dependencies: python3 standard library only.

Usage:
    python3 build_balrog_rows.py \
        --sources   agent-work/sources/balrog \
        --dataset-models "../../../AI Compute vs Human Time/dataset/models.csv" \
        --candidate-models ../../candidates/balrog/models.csv \
        --points-out /tmp/balrog-rebuild/points.csv \
        --calc-out   /tmp/balrog-rebuild/balrog-crafter-calculations.json

The published outputs were produced with --points-out candidates/balrog/points.csv and
--calc-out research/balrog/balrog-crafter-calculations.json.
"""
import argparse
import csv
import json
import math
import os
import statistics

REPO = "https://github.com/balrog-ai/experiments"
COMMIT = "32574bb7d41256e2726899586ca1468a91cfc49f"
HARNESS = "https://github.com/balrog-ai/BALROG"
HARNESS_INSPECTED = "b7afe79e3e4265811cfa985ed7c95c4d1a11e3f5"

POINT_FIELDS = [
    "point_id", "task", "task_category", "task_description", "model_id", "compute_scope",
    "compute_flops", "human_skill", "human_time_scope", "human_time", "performance_vs_human",
    "comparison_issues", "compute_evidence", "human_time_evidence", "performance_evidence",
    "human_time_statistic", "human_time_subset", "human_attempts", "human_time_source",
    "human_time_method", "compute_method", "compute_statistic", "compute_subset", "ai_attempts",
    "compute_source", "tokens", "tokens_accounting", "source_dataset", "source_record", "notes",
]

# Human interface rate: crafter/run_gui.py advances one environment step per rendered frame
# and caps the frame rate at --fps, default 5. See agent-work/sources/balrog/balrog-code-and-config-extracts.md.
HUMAN_STEPS_PER_SECOND = 5.0

# Billed image positions per Crafter frame (256x256, set by envs.crafter_kwargs.size).
# Anthropic: tokens ~= (width * height) / 750. Google: 258 tokens for images whose
# dimensions are both <= 384 px.
IMAGE_TOKENS = {"anthropic": 256 * 256 / 750.0, "google": 258.0}

# Uniform-random floor on BALROG's Crafter metric. Primary value is the Crafter paper's own
# random column (arXiv:2109.06780v2 Table B.1, "Crafter without rewards"): the 22 success
# rates sum to 227.6, so the mean achievement count is 2.276 and the metric is 227.6 / 22.
# research/balrog/simulate_random_floor.py corroborates it under BALROG's exact settings; its
# within-replication standard error supplies the uncertainty.
RANDOM_FLOOR_RATES = [0.0, 0.0, 9.3, 0.0, 50.2, 0.0, 24.4, 0.0, 0.1, 0.4, 0.0,
                      0.0, 0.0, 0.0, 0.0, 0.3, 0.3, 0.0, 44.6, 0.0, 4.4, 93.6]
RANDOM_FLOOR = sum(RANDOM_FLOOR_RATES) / 22.0
RANDOM_FLOOR_SE = 0.40  # mean within-replication SEM of research/balrog/crafter-random-floor.json
FLOOR_FLAG_Z = 2.5

# Whether provider-side prompt caching could have reduced actual processing below the counted
# prompt positions, keyed by the harness client name recorded in each submission.
_NO_CACHE_OPT_IN = (
    " Caching on this endpoint is opt-in per request and the harness sends no cache block, so the "
    "counters are the full processed prompt.")
_NO_CACHE_THRESHOLD = (
    " Automatic caching on this endpoint needs a shared prefix of at least 1,024 tokens and the only "
    "prefix shared across calls is the ~425-token instruction block, so the counters are the full "
    "processed prompt.")
_CACHE_UNKNOWN = (
    " Provider-side prefix reuse is undocumented for this endpoint; full-prefix processing assumed.")
CACHE_NOTE = {
    "claude": _NO_CACHE_OPT_IN, "aws-bedrock": _NO_CACHE_OPT_IN,
    "openai": _NO_CACHE_THRESHOLD, "gemini": _NO_CACHE_THRESHOLD,
    "vllm": _CACHE_UNKNOWN, "nvidia": _CACHE_UNKNOWN, "xai": _CACHE_UNKNOWN,
}

MATCH_Z = 2.0  # match when the shortfall from the human mean is under two combined standard errors
HIGH_INVALID_RATE = 0.10  # disclose the harness default-action share above this

# run directory (under submissions/) -> row construction inputs.
#   model_id           : canonical model record used for flops_per_token
#   slug               : point_id suffix
#   modality           : "llm" (text only) or "vlm" (text + one image per step)
#   image_vendor       : image-token convention for vlm runs, else None
#   config             : short configuration description for task_description
#   reasoning_counted  : whether the recorded output counter includes hidden reasoning
RUNS = [
    ("LLM/20240410_robust_cot_DeepSeek-R1", "deepseek-r1", "deepseekr1", "llm", None,
     "robust_cot agent, NVIDIA NIM endpoint, max_tokens 8192", True),
    ("LLM/20241030_naive-Llama-3.2-1B-Instruct", "llama-3.2-1b-instruct", "llama32-1b", "llm", None,
     "naive agent, self-hosted vLLM, temperature 0, max_tokens 1024", True),
    ("LLM/20241030_naive-Llama-3.2-3B-Instruct", "llama-3.2-3b-instruct", "llama32-3b", "llm", None,
     "naive agent, self-hosted vLLM, temperature 0, max_tokens 1024", True),
    ("LLM/20241101_naive-Llama-3.1-8B-Instruct", "llama-3.1-8b-instruct", "llama31-8b", "llm", None,
     "naive agent, self-hosted vLLM, temperature 0, max_tokens 1024", True),
    ("LLM/20241103_Claude-3.5-Sonnet", "claude-3-5-sonnet-20240620", "claude35sonnet", "llm", None,
     "naive agent, Anthropic Messages API, temperature 0, max_tokens 1024", True),
    ("LLM/20241115_naive-Qwen2.5-7B-it", "qwen2.5-7b-instruct", "qwen25-7b", "llm", None,
     "naive agent, self-hosted vLLM, temperature 0, max_tokens 1024", True),
    ("LLM/20241209_naive-claude-3-5-haiku", "claude-3-5-haiku-20241022", "claude35haiku", "llm", None,
     "naive agent, Anthropic Messages API, temperature 0, max_tokens 1024", True),
    ("LLM/20241209_naive-mistral-nemo-instruct", "mistral-nemo-2407", "mistralnemo", "llm", None,
     "naive agent, self-hosted vLLM, temperature 0, max_tokens 1024", True),
    ("LLM/20241209_naive_Llama-3.3-70B-Instruct", "llama-3.3-70b-instruct", "llama33-70b", "llm", None,
     "naive agent, self-hosted vLLM, temperature 0, max_tokens 1024", True),
    ("LLM/20250113_robust_naive_microsoft_phi-4", "phi-4", "phi4", "llm", None,
     "robust_naive agent, self-hosted vLLM, temperature 0, max_tokens 1024", True),
    ("LLM/20250126_robust_cot_deepseek_R1_distill_qwen32B", "deepseek-r1-distill-qwen-32b",
     "r1distillqwen32b", "llm", None,
     "robust_cot agent, self-hosted vLLM, temperature 0, max_tokens 4096", True),
    ("LLM/20250313_robust_cot_Reka-Flash-3", "reka-flash-3", "rekaflash3", "llm", None,
     "robust_cot agent, self-hosted vLLM, temperature 1, max_tokens 4096", True),
    ("LLM/20250425_naive_Gemini-2.5-Pro-Exp-03-25", "gemini-2.5-pro-03-25", "gemini25pro", "llm", None,
     "naive agent, Gemini API, temperature 1, max_tokens 4096", False),
    ("LLM/20250425_naive_grok-3", "grok-3-beta", "grok3", "llm", None,
     "naive agent, xAI API, temperature 1, max_tokens 4096", True),
    ("LLM/20250713_naive_grok-4", "grok-4", "grok4", "llm", None,
     "naive agent, xAI API, temperature 1, max_tokens 4096", False),
    ("LLM/20250719-naive_gemini-2.5-flash", "gemini-2.5-flash", "gemini25flash", "llm", None,
     "naive agent, Gemini API, temperature 1, max_tokens 4096", False),
    ("LLM/20250808_naive_gpt-5-minimal", "gpt-5", "gpt5minimal", "llm", None,
     "naive agent, OpenAI chat completions, max_tokens 1024", True),
    ("LLM/20260203_naive_gemini-3-pro", "gemini-3-pro", "gemini3pro", "llm", None,
     "naive agent, Gemini API, default thinking, max_tokens 8192", False),
    ("LLM/20260213_naive_gemini-3-flash", "gemini-3-flash-preview", "gemini3flash", "llm", None,
     "naive agent, Gemini API, default thinking, max_tokens 8192", False),
    ("LLM/20260221_naive_gemini-3.1-pro", "gemini-3.1-pro-preview", "gemini31pro", "llm", None,
     "naive agent, Gemini API, default thinking, max_tokens 8192", False),
    ("LLM/20260223_naive_claude-haiku-4.5", "claude-haiku-4-5", "claudehaiku45", "llm", None,
     "naive agent, AWS Bedrock Converse, no extended thinking, max_tokens 8192", True),
    ("LLM/20260224_naive_claude-opus-4.5", "claude-opus-4-5", "claudeopus45", "llm", None,
     "naive agent, AWS Bedrock Converse, no extended thinking, max_tokens 8192", True),
    ("LLM/20260224_naive_claude-opus-4.5-thinking", "claude-opus-4-5", "claudeopus45thinking", "llm", None,
     "naive agent, AWS Bedrock Converse, extended thinking budget 1024, max_tokens 8192", True),
    ("LLM/20260225_naive_gemini-3.1-pro-thinking", "gemini-3.1-pro-preview", "gemini31prothinking", "llm", None,
     "naive agent, Gemini API, thinking budget 1024, max_tokens 8192", False),
    ("VLM/20241103_Claude-3.5-Sonnet", "claude-3-5-sonnet-20240620", "vlm-claude35sonnet", "vlm", "anthropic",
     "naive agent, one 256x256 frame per step, Anthropic Messages API, temperature 0", True),
    ("VLM/20250425_naive_Gemini-2.5-Pro-Exp-03-25", "gemini-2.5-pro-03-25", "vlm-gemini25pro", "vlm", "google",
     "naive agent, one 256x256 frame per step, Gemini API, temperature 1", True),
]

def dec(value):
    """Plain decimal text for a float, no exponent, trailing zeros trimmed."""
    text = f"{value:.6f}".rstrip("0").rstrip(".")
    return text or "0"


def load_models(paths):
    table = {}
    for path in paths:
        if not path or not os.path.exists(path):
            continue
        with open(path) as fh:
            for row in csv.DictReader(fh):
                table[row["model_id"]] = row
    return table


def run_date(metadata_yaml):
    for line in metadata_yaml.splitlines():
        if line.strip().startswith("date:"):
            return line.split(":", 1)[1].strip().strip('"')
    raise ValueError("no date in metadata.yaml")


def harness_at(commits, date):
    """Newest harness commit dated at or before the submission date, or None if the
    submission predates the repository's first public commit."""
    eligible = [c for c in commits if c["date"] <= date]
    return eligible[-1] if eligible else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", required=True)
    ap.add_argument("--dataset-models", required=True)
    ap.add_argument("--candidate-models", required=True)
    ap.add_argument("--points-out", required=True)
    ap.add_argument("--calc-out", required=True)
    args = ap.parse_args()

    summaries = json.load(open(os.path.join(args.sources, "balrog-crafter-env-summaries.json")))["runs"]
    commits = json.load(open(os.path.join(args.sources, "balrog-harness-commits.json")))["commits"]
    with open(os.path.join(args.sources, "balrog-crafter-episodes.csv")) as fh:
        episodes = list(csv.DictReader(fh))
    with open(os.path.join(args.sources, "crafter-human-episodes.csv")) as fh:
        human = list(csv.DictReader(fh))
    models = load_models([args.dataset_models, args.candidate_models])

    # ---- human baseline -------------------------------------------------
    ach = [k[len("first_unlock_step_"):] for k in human[0] if k.startswith("first_unlock_step_")]
    h_steps = [int(r["steps"]) for r in human]
    h_prog = [100.0 * float(r["progression"]) for r in human]
    n_h = len(human)
    human_mean_steps = statistics.mean(h_steps)
    human_time = human_mean_steps / HUMAN_STEPS_PER_SECOND
    human_prog_mean = statistics.mean(h_prog)
    human_prog_sem = statistics.stdev(h_prog) / math.sqrt(n_h)

    def human_at(budget):
        """Mean human score counting only achievements first unlocked within `budget` steps.

        An episode shorter than the budget contributes every achievement it unlocked, which
        falls out of the rule because all of its first-unlock steps are below its length."""
        scores = [100.0 * sum(1 for a in ach if 0 <= int(r["first_unlock_step_" + a]) <= budget) / len(ach)
                  for r in human]
        return statistics.mean(scores), statistics.stdev(scores) / math.sqrt(n_h)

    ai_steps_all = [int(r["num_steps"]) for r in episodes]
    human_block = {
        "episodes": n_h,
        "mean_steps_per_episode": human_mean_steps,
        "median_steps_per_episode": statistics.median(h_steps),
        "total_steps": sum(h_steps),
        "steps_per_second": HUMAN_STEPS_PER_SECOND,
        "mean_seconds_per_episode": human_time,
        "median_seconds_per_episode": statistics.median(h_steps) / HUMAN_STEPS_PER_SECOND,
        "mean_progression_percent": human_prog_mean,
        "sample_sd_progression_percent": statistics.stdev(h_prog),
        "sem_progression_percent": human_prog_sem,
        "episodes_unlocking_all_22": sum(1 for r in human if int(r["achievements_unlocked"]) == 22),
        "noop_steps": sum(int(r["noop_steps"]) for r in human),
        "sleeping_frames": sum(int(r["sleeping_frames"]) for r in human),
        "noop_steps_not_sleeping": sum(int(r["noop_steps_not_sleeping"]) for r in human),
        "ai_episodes_all_runs": len(episodes),
        "ai_mean_steps_all_runs": statistics.mean(ai_steps_all),
        "ai_min_steps": min(ai_steps_all), "ai_max_steps": max(ai_steps_all),
        "ai_episodes_reaching_cap": sum(1 for s in ai_steps_all if s >= 2000),
        "ai_episodes_ended_by_death": sum(1 for r in episodes if r["done"] == "True"),
        "human_to_ai_step_ratio": human_mean_steps / statistics.mean(ai_steps_all),
    }

    calc = {"human_baseline": human_block, "runs": {}, "constants": {
        "image_tokens_per_crafter_frame": IMAGE_TOKENS,
        "match_threshold_combined_se": MATCH_Z,
        "random_floor_percent": RANDOM_FLOOR, "random_floor_se": RANDOM_FLOOR_SE,
        "random_floor_flag_threshold_se": FLOOR_FLAG_Z,
        "high_invalid_action_rate": HIGH_INVALID_RATE,
        "experiments_commit": COMMIT, "harness_commit_inspected": HARNESS_INSPECTED}}
    rows = []

    for run, model_id, slug, modality, vendor, config, reasoning_counted in RUNS:
        summary = summaries[run]["crafter_summary"]
        eps = [e for e in episodes if e["run"] == run]
        n_ep = len(eps)
        total_in = sum(int(e["input_tokens"]) for e in eps)
        total_out = sum(int(e["output_tokens"]) for e in eps)
        total_steps = sum(int(e["num_steps"]) for e in eps)
        invalid = sum(int(e["invalid_actions"]) for e in eps)
        assert total_in == summary["input_tokens"], run
        assert total_out == summary["output_tokens"], run
        assert n_ep == summary["episodes_played"], run
        assert abs(total_steps / n_ep - summary["average_steps"]) < 1e-9, run

        endpoints = [k for k in summaries[run]["episode_client_model_ids"] if k != "(absent)"]
        endpoint = endpoints[0] if endpoints else summaries[run]["run_summary_client"]["model_id"]
        endpoint_from = ("recorded in all ten per-episode records" if endpoints else
                         "recorded in the run summary.json; the episode records omit it")
        date = run_date(summaries[run]["metadata_yaml"])
        harness = harness_at(commits, date)

        img_per_frame = IMAGE_TOKENS[vendor] if modality == "vlm" else 0.0
        image_positions = img_per_frame * total_steps
        text_positions = total_in + total_out - image_positions

        fpt = float(models[model_id]["flops_per_token"])
        param_basis = models[model_id]["active_parameters_basis"]
        processed_per_episode = (total_in + total_out) / n_ep
        compute_flops = fpt * processed_per_episode
        tokens_per_episode = text_positions / n_ep

        prog = summary["progression_percentage"]
        se = summary["standard_error"]
        z = (human_prog_mean - prog) / math.sqrt(se ** 2 + human_prog_sem ** 2)
        performance = "match" if z < MATCH_Z else "below"
        mean_steps = total_steps / n_ep
        matched_mean, matched_sem = human_at(mean_steps)
        z_floor = (prog - RANDOM_FLOOR) / math.sqrt(se ** 2 + RANDOM_FLOOR_SE ** 2)
        near_floor = z_floor < FLOOR_FLAG_Z
        invalid_rate = invalid / total_steps

        calc["runs"][run] = {
            "point_id": f"game-balrog-crafter-{slug}", "model_id": model_id,
            "endpoint_called": endpoint, "endpoint_evidence": endpoint_from,
            "submission_date": date, "harness_newest_commit_at_submission": harness,
            "flops_per_token": fpt, "active_parameters_basis": param_basis,
            "episodes": n_ep, "model_calls": total_steps, "mean_steps_per_episode": mean_steps,
            "total_input_tokens": total_in, "total_output_tokens": total_out,
            "image_tokens_per_frame": img_per_frame, "image_positions_total": image_positions,
            "text_positions_total": text_positions,
            "processed_positions_per_episode": processed_per_episode,
            "text_tokens_per_episode": tokens_per_episode,
            "compute_flops_per_episode": compute_flops,
            "mean_output_tokens_per_call": total_out / total_steps,
            "invalid_actions": invalid, "invalid_action_rate": invalid_rate,
            "progression_percent": prog, "progression_standard_error": se,
            "combined_se_z_vs_human": z, "performance_vs_human": performance,
            "human_score_at_ai_mean_steps_percent": matched_mean,
            "human_score_at_ai_mean_steps_sem": matched_sem,
            "z_vs_random_floor": z_floor, "near_random_floor": near_floor,
            "hidden_reasoning_counted": reasoning_counted,
        }

        # ---- notes: only qualifications needed to read this row -----------
        # Cache treatment, parameter-basis, harness-revision, default-action and
        # human_time-floor discussion lives in research/balrog.md, cited from compute_source.
        parts = [f"Mean over {n_ep} episodes; {total_steps} model calls, one per environment step. "
                 f"Episodes averaged {mean_steps:.1f} steps, all ending in death, against the human "
                 f"{human_mean_steps:.2f}, so human_time covers {human_mean_steps / mean_steps:.1f} "
                 f"times more play than compute_flops."]
        if not reasoning_counted:
            parts.append("The recorded output counter excludes hidden reasoning, so compute_flops is "
                         "a lower bound.")
        if modality == "vlm":
            parts.append(f"tokens excludes {img_per_frame:.6g} billed image positions per frame, which "
                         f"compute_flops retains.")
        if near_floor:
            floor_note = (f"The score is {z_floor:.2f} combined standard errors above the "
                          f"{RANDOM_FLOOR:.2f}% uniform-random floor, but the achievement composition "
                          f"is not random.")
            if invalid_rate > HIGH_INVALID_RATE:
                floor_note += (f" {100 * invalid_rate:.1f}% of calls produced no parseable action and "
                               f"were defaulted to Noop.")
            parts.append(floor_note)
        notes = " ".join(parts)

        perf = (f"BALROG Crafter progression {prog:.2f}% +/- {se:.2f} over {n_ep} episodes. The same "
                f"metric computed on the 100 recorded human expert episodes is {human_prog_mean:.2f}% "
                f"+/- {human_prog_sem:.2f}; the shortfall is {z:.2f} combined standard errors.")
        if performance == "match":
            perf += (f" Restricting the human episodes to this run's mean episode length of "
                     f"{mean_steps:.1f} steps, the human score is {matched_mean:.2f}% +/- "
                     f"{matched_sem:.2f}, which this run exceeds.")

        rows.append({
            "point_id": f"game-balrog-crafter-{slug}",
            "task": "Play one episode of Crafter",
            "task_category": "games",
            "task_description": (
                "One episode of Crafter from a fresh procedurally generated world, ending when the player "
                "dies or at a 2,000-step cap, scored by how many of the 22 achievements are unlocked at "
                "least once. The model acts once per environment step from a natural-language description "
                f"of the local view plus a 16-observation history ({config}). The human baseline is one "
                "episode played through the Crafter keyboard interface by the recorded expert players."),
            "model_id": model_id,
            "compute_scope": "inference",
            "compute_flops": dec(compute_flops),
            "human_skill": "expert",
            "human_time_scope": "task_performance",
            "human_time": dec(human_time),
            "performance_vs_human": performance,
            "comparison_issues": "different_inputs_or_tools",
            "compute_evidence": "derived_assumed_inputs",
            "human_time_evidence": "assumed",
            "performance_evidence": perf,
            "human_time_statistic": "mean",
            "human_time_subset": "all",
            "human_attempts": str(n_h),
            "human_time_source": (
                "https://archive.org/details/crafter_human_dataset; research/balrog.md#human-baseline"),
            "human_time_method": "work_rate",
            "compute_method": "params_tokens",
            "compute_statistic": "mean",
            "compute_subset": "all",
            "ai_attempts": str(n_ep),
            "compute_source": (
                f"{REPO} submissions/{run}/crafter/crafter_summary.json at commit {COMMIT}; "
                "research/balrog.md#compute"),
            "tokens": dec(round(tokens_per_episode, 1)),
            "tokens_accounting": "input_output" if modality == "llm" else "decoder_processed",
            "source_dataset": "BALROG",
            "source_record": (
                f"submissions/{run} crafter default, 10 episodes, commit {COMMIT}; endpoint {endpoint}; "
                f"dated {date}, harness " + (f"{harness['sha'][:7]} ({harness['date']})" if harness
                                             else "pre-release, before the repository opened")
                + "; performance: crafter_summary.json progression_percentage; human: "
                "crafter_human_dataset 100 episodes"),
            "notes": notes,
        })

    for path in (args.points_out, args.calc_out):
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(args.points_out, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=POINT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    with open(args.calc_out, "w") as fh:
        json.dump(calc, fh, indent=1)

    print(f"rows={len(rows)} human_time_s={human_time:.4f} human_progression={human_prog_mean:.4f}% "
          f"ai_mean_steps={human_block['ai_mean_steps_all_runs']:.2f} floor={RANDOM_FLOOR:.3f}%")
    for r in rows:
        v = next(x for x in calc["runs"].values() if x["point_id"] == r["point_id"])
        flag = " near-floor" if v["near_random_floor"] else ""
        print(f"  {r['point_id']:44s} {float(r['compute_flops']):.4e} {r['performance_vs_human']:5s}"
              f" human@{v['mean_steps_per_episode']:.0f}={v['human_score_at_ai_mean_steps_percent']:.2f}%{flag}")


if __name__ == "__main__":
    main()
