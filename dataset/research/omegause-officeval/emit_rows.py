#!/usr/bin/env python3
"""Write the OmegaUse-OfficeVal candidate points.csv and models.csv from the
inversion output.  Agents whose calculations.json entry has build_row false are
skipped; dispositions.csv is maintained by hand and is not written here.

Usage:
  python3 emit_rows.py \
      --calculations <path>/calculations.json \
      --attention    <path>/attention-scenarios.json \
      --table3       <path>/omegause-table3.csv \
      --outdir       <path>/candidates/omegause-officeval

Dependencies: Python 3.8+ standard library only.
"""
import argparse, csv, json, math, os

POINT_COLS = ["point_id","task","task_category","task_description","model_id","compute_scope",
 "compute_flops","human_skill","human_time_scope","human_time","performance_vs_human",
 "comparison_issues","compute_evidence","human_time_evidence","performance_evidence",
 "human_time_statistic","human_time_subset","human_attempts","human_time_source",
 "human_time_method","compute_method","compute_statistic","compute_subset","ai_attempts",
 "compute_source","tokens","tokens_accounting","source_dataset","source_record","notes",
 "ai_cost_usd","ai_cost_basis","ai_cost_date","human_cost_usd","human_cost_basis"]
MODEL_COLS = ["model_id","model","company","model_release_date","model_release_source",
 "flops_per_token","flops_per_token_method","active_parameters","active_parameters_basis",
 "encoder_parameters","encoder_parameters_basis","decoder_parameters","decoder_parameters_basis",
 "parameter_source","notes"]
CAPS = {"notes":586,"task_description":560,"performance_evidence":337,"source_record":455,
        "compute_source":220,"human_time_source":205}

AGENTS = {  # OmegaUse label -> (point_id suffix, model display name)
 "GLM-5.2":         ("glm52",       "GLM-5.2"),
 "Qwen3.7-Plus":    ("qwen37plus",  "Qwen3.7-Plus"),
 "Kimi K2.6":       ("kimik26",     "Kimi K2.6"),
 "DeepSeek-V4-Pro": ("dsv4pro",     "DeepSeek-V4-Pro"),
 "Minimax M3":      ("minimaxm3",   "MiniMax M3"),
}
# Agents whose calculations.json entry has build_row false are skipped; their
# cells go to dispositions.csv instead.
DONOR_PHRASE = {
 "GLM-5.2": "Epoch's SWE-bench run of the same endpoint and three Artificial Analysis agent benchmarks",
 "Qwen3.7-Plus": "Epoch's SWE-bench run of the sibling Qwen3.7-Max",
 "Kimi K2.6": "Epoch's SWE-bench run of the same endpoint",
 "DeepSeek-V4-Pro": "Epoch's SWE-bench run of the same endpoint and two Artificial Analysis agent benchmarks",
 "Minimax M3": "four Artificial Analysis agent benchmarks",
}
TASK_DESCRIPTION = (
 "One of the 100 OmegaUse-OfficeVal tasks: a Chinese-language office request plus its input "
 "files, delivered as a finished artifact in the original format. The set supplies 220 input "
 "files (63 docx, 31 pptx, 25 xlsx, 14 pdf, 77 images, 10 video or audio) and requires 115 "
 "output artifacts. A task-specific code verifier scores the artifact from 0 to 100: it must "
 "first pass every usability check, then earns weighted credit for met requirements minus "
 "penalties for damage. The work unit is one task and every value is a per-task mean over all "
 "100.")
HUMAN_TIME_SOURCE = ("https://huggingface.co/datasets/baidu-frontier-research/OmegaUse-OfficeVal "
 "human_labor_time; agent-work/sources/omegause-officeval/omegause-human-labor-time.csv; "
 "research/omegause-officeval.md#human-baseline")

MODELS = [
 dict(model_id="minimax-m3", model="MiniMax-M3", company="MiniMax",
      model_release_date="2026-06-01",
      model_release_source="https://www.minimax.io/blog/minimax-m3",
      flops_per_token=4.6e10, flops_per_token_method="two_active_parameters",
      active_parameters=2.3e10, active_parameters_basis="reported",
      encoder_parameters="not_applicable", encoder_parameters_basis="not_applicable",
      decoder_parameters="not_applicable", decoder_parameters_basis="not_applicable",
      parameter_source=("https://huggingface.co/MiniMaxAI/MiniMax-M3 model summary; "
        "agent-work/sources/omegause-officeval/minimax-m3-config.json; "
        "research/omegause-officeval.md#model-records"),
      notes=("Developer states about 428B total and about 23B activated. Counting the published "
        "config gives 23.3B excluding embeddings and the output head. Native multimodal; the "
        "coefficient covers text positions only. MiniMax Sparse Attention selects 16 blocks of "
        "128 keys on 57 of 60 layers, which bounds the attention term 2N omits.")),
]


def fmt(x):
    return repr(x) if isinstance(x, float) else x


def main():
    ap = argparse.ArgumentParser()
    for f in ("calculations", "attention", "table3", "outdir"):
        ap.add_argument("--" + f, required=True)
    a = ap.parse_args()
    calc = json.load(open(a.calculations))
    att = json.load(open(a.attention))
    human_t = calc["human_baseline"]["mean_seconds"]
    human_score = calc["human_score"]
    os.makedirs(a.outdir, exist_ok=True)

    points = []
    for agent, (suffix, display) in AGENTS.items():
        v = calc["agents"][agent]
        if not v["build_row"]:
            continue
        pid = "agen-omegause-officeval-" + suffix
        ratio = v["score_ratio_to_human"]
        lo, hi = v["flops_low"], v["flops_high"]
        if len(v["branches"]) == 1:
            spread = ("a single donor, so the central is that branch and the note "
                      "carries an h sensitivity of 0.85 to 0.99 instead")
        else:
            spread = f"branch range {lo:.2g} to {hi:.2g} FLOPs, central their geometric mean"
        notes = (
          f"compute_flops is inverted from the reported ${v['cost_usd_per_task']:.4f} per task at "
          f"the provider's list prices with a cache structure from {DONOR_PHRASE[agent]}; "
          f"{spread}, so it is not independent of ai_cost_usd. The human score takes the best of "
          "the two or three annotator submissions, human_time the mean of the two shortest valid "
          "ones, so the sides select differently. The agent had shell and file tools and no GUI; "
          "annotators used office applications.")
        if agent == "Minimax M3":
            notes += " Mean runtime 2.28 h against a 4 h cap truncated some tasks."
        perf = (
          f"Task-specific code verifiers score each delivered artifact from 0 to 100 after a "
          f"usability gate; the figure is the mean over the 100 tasks. {display} scores "
          f"{v['score']:.2f} against {human_score:.2f} for the best of the at least two human "
          f"annotator submissions on the same tasks under the same verifiers, {ratio:.2f} of the "
          f"human score above a zero floor.")
        src = (
          f"arXiv:2607.27155v2 Table 3 (score, cost per task, hours per task) and Appendix E "
          f"(scaffold, 14400 s per-task timeout); model alias {display}; Hugging Face dataset "
          f"baidu-frontier-research/OmegaUse-OfficeVal, 100 tasks with human_labor_time; "
          f"agent-work/sources/omegause-officeval/omegause-table3.csv; donor structures in "
          f"agent-work/sources/omegause-officeval/donor-structures.csv; performance: the same "
          f"Table 3, human and model scored by the same verifiers")
        points.append({
          "point_id": pid,
          "task": "OmegaUse-OfficeVal office deliverable",
          "task_category": "administrative_operational",
          "task_description": TASK_DESCRIPTION,
          "model_id": v["model_id"],
          "compute_scope": "inference",
          "compute_flops": repr(v["flops_central"]),
          "human_skill": "typical",
          "human_time_scope": "task_performance",
          "human_time": repr(round(human_t, 4)),
          "performance_vs_human": "below",
          "comparison_issues": "different_attempt_selection; different_inputs_or_tools",
          "compute_evidence": "derived_assumed_inputs",
          "human_time_evidence": "task_timings",
          "performance_evidence": perf,
          "human_time_statistic": "mean",
          "human_time_subset": "successful",
          "human_attempts": str(calc["human_baseline"]["contributing_attempts"]),
          "human_time_source": HUMAN_TIME_SOURCE,
          "human_time_method": "other_calculation",
          "compute_method": "params_tokens",
          "compute_statistic": "mean",
          "compute_subset": "all",
          "ai_attempts": "100",
          "compute_source": (f"research/omegause-officeval.md#{pid}; "
              "research/omegause-officeval/calculations.json; "
              "research/omegause-officeval/compute_omegause.py"),
          "tokens": repr(v["billed_tokens_central"]),
          "tokens_accounting": "input_cache_creation_output",
          "source_dataset": "OmegaUse-OfficeVal",
          "source_record": src,
          "notes": notes,
          "ai_cost_usd": repr(v["cost_usd_per_task"]),
          "ai_cost_basis": "reported",
          "ai_cost_date": "2026-07-29",
          "human_cost_usd": "",
          "human_cost_basis": "not_available",
        })

    for p in points:
        for k, cap in CAPS.items():
            if len(p[k]) > cap:
                raise SystemExit(f'{p["point_id"]}: {k} is {len(p[k])} chars, cap {cap}')

    with open(os.path.join(a.outdir, "points.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=POINT_COLS, lineterminator="\n")
        w.writeheader()
        for p in points:
            w.writerow(p)
    with open(os.path.join(a.outdir, "models.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=MODEL_COLS, lineterminator="\n")
        w.writeheader()
        for m in MODELS:
            if len(m["notes"]) > 365:
                raise SystemExit(f'{m["model_id"]}: models notes {len(m["notes"])} chars, cap 365')
            w.writerow({k: fmt(v) for k, v in m.items()})
    print("wrote", len(points), "points and", len(MODELS), "models to", a.outdir)
    for p in points:
        print(f'  {p["point_id"]:36s} flops={float(p["compute_flops"]):.4g} '
              f'tokens={float(p["tokens"]):,.0f}')


if __name__ == "__main__":
    main()
