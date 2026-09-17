#!/usr/bin/env python3
"""Emit the HourVideo candidate rows, taking the column order from the registry CSVs.

The field text lives here so the two rows can be regenerated and re-checked against the
DECISIONS.md length norms without hand-editing a CSV. The numbers it writes are the ones
research/hourvideo/compute_hourvideo.py derives; this script does no arithmetic.

Dependencies: Python 3.8+ standard library only.

Usage:
    python3 emit_rows.py \
        --points-header ../../points.csv \
        --models-header ../../models.csv \
        --out-dir ../../candidates/hourvideo

Exits non-zero if any text field exceeds its norm or a cited path ends in punctuation.
"""
import argparse, csv, os, sys

_ap = argparse.ArgumentParser(description=__doc__)
_ap.add_argument("--points-header", required=True, help="CSV whose header row fixes the points column order")
_ap.add_argument("--models-header", required=True, help="CSV whose header row fixes the models column order")
_ap.add_argument("--out-dir", required=True, help="directory to write points.csv and models.csv into")
_args = _ap.parse_args()
OUT = _args.out_dir

with open(_args.points_header) as fh:
    POINT_HEADER = next(csv.reader(fh))
with open(_args.models_header) as fh:
    MODEL_HEADER = next(csv.reader(fh))

SHARED = dict(
    task="Answer an hour-long video's whole question set",
    task_category="perception",
    model_id="gemini-1.5-pro-hourvideo",
    compute_scope="inference",
    human_skill="expert",
    human_time_scope="task_performance",
    human_time="4029",
    performance_vs_human="below",
    comparison_issues="different_task; different_inputs_or_tools; different_assessment; different_human_baseline",
    compute_evidence="derived_assumed_inputs",
    human_time_evidence="transferred_timings",
    human_time_statistic="point_estimate",
    human_time_subset="all",
    human_attempts="700",
    human_time_source="https://arxiv.org/pdf/2411.19941 section 4.7; research/hourvideo.md#human-time",
    human_time_method="estimated",
    compute_method="operation_count",
    compute_statistic="mean",
    compute_subset="all",
    ai_attempts="25",
    tokens_accounting="decoder_processed",
    source_dataset="HourVideo (Chandrasegaran et al., NeurIPS 2024 Datasets and Benchmarks Track)",
)

rows = []

rows.append(dict(SHARED,
    point_id="perc-hourvideo-gemini15pro-tasklevel",
    task_description=(
        "One video from HourVideo's 25-video ablation set, mean 38.2 minutes of egocentric Ego4D "
        "footage, with all 22.8 of its five-way MCQs answered across summarization, perception, "
        "visual reasoning and navigation. Gemini 1.5 Pro receives the whole video, re-encoded to "
        "0.5 fps at 512x384 with no audio track, once per task or sub-task batch under HourVideo's "
        "task-level protocol, about 7 to 8 passes per video. Completion is an answer for every MCQ. "
        "The human unit is one person answering the same question set for the same video."),
    compute_flops="1.0420547132928709e+18",
    performance_evidence=(
        "Gemini 1.5 Pro scored 38.9% on the 570-MCQ ablation, refusal handling unreported; random "
        "guessing is 20%. Three human experts scored 85.0% on a separate 213-MCQ, 14-video sample "
        "of the same benchmark. The timing donor's participants scored 99.64% on their own "
        "70-question set. Benchmark-wide the model scored 37.3% over 445 videos."),
    compute_source=(
        "HourVideo NeurIPS 2024 Table 3 task-level row; research/hourvideo.md#compute; "
        "research/hourvideo/calculations.json"),
    tokens="12291.89",
    source_record=(
        "NeurIPS 2024 proceedings paper 5f2809607f692d79a01c05c43d702883: Table 3 task-level row "
        "(38.9%, 120,818,343 tokens, $846) over 25 videos, 15.9 h and 570 MCQs; Sec 3.1 batching "
        "protocol; Sec 3.2 configuration and human experts; Table 4; Table D.2 refusals. Model "
        "models/gemini-1.5-pro-latest per github.com/keshik6/HourVideo commit 1ac83c26. Extracts "
        "in agent-work/sources/hourvideo/MANIFEST.md, performance: same Table 3 and Sec 3.2"),
    notes=(
        "Table 3's token column is billed input: 120,818,343 x $7.00/M reproduces $846, the "
        "pre-October-2024 above-128K rate. tokens is the text remainder; 4,822,950 video positions "
        "per video are charged in compute_flops, with a 7.2% visual-encoder term. The coefficient "
        "omits attention over 590,000-position contexts, adding 2.9x to 6.5x. Human time is the "
        "geometric mean of two transfers out of one 1h-walk VQA sentence: 11,653 s at 511 s per "
        "question, 1,393 s at 0.61 s per second of video over a donor corpus averaging 98 min. The "
        "three experts came from the benchmark's own annotator pool."),
))

rows.append(dict(SHARED,
    point_id="perc-hourvideo-gemini15pro-individual",
    task_description=(
        "One video from HourVideo's 25-video ablation set, mean 38.2 minutes of egocentric Ego4D "
        "footage, with all 22.8 of its five-way MCQs answered across summarization, perception, "
        "visual reasoning and navigation. Gemini 1.5 Pro receives the whole video, re-encoded to "
        "0.5 fps at 512x384 with no audio track, once per MCQ under the paper's individual-"
        "evaluation ablation, so 22.8 passes per video. Completion is an answer for every MCQ. "
        "The human unit is one person answering the same question set for the same video."),
    compute_flops="3.2282583670636923e+18",
    performance_evidence=(
        "Gemini 1.5 Pro scored 36.8% on the 570-MCQ ablation, 2.1 points below the same model under "
        "task-level batching; refusal handling unreported, random guessing 20%. Three human experts "
        "scored 85.0% on a separate 213-MCQ, 14-video sample of the same benchmark. The timing "
        "donor's participants scored 99.64% on their own 70-question set."),
    compute_source=(
        "HourVideo NeurIPS 2024 Table 3 individual row; research/hourvideo.md#compute; "
        "research/hourvideo/calculations.json"),
    tokens="23256",
    source_record=(
        "NeurIPS 2024 proceedings paper 5f2809607f692d79a01c05c43d702883: Table 3 individual row "
        "(36.8%, 374,396,885 tokens, $2621) over 25 videos, 15.9 h and 570 MCQs; Sec 3.3 ablation "
        "description; Sec 3.2 configuration and human experts; Table 4. Model "
        "models/gemini-1.5-pro-latest per github.com/keshik6/HourVideo commit 1ac83c26. Extracts "
        "in agent-work/sources/hourvideo/MANIFEST.md, performance: same Table 3 and Sec 3.2"),
    notes=(
        "Table 3's token column is billed input: 374,396,885 x $7.00/M reproduces $2621, the "
        "pre-October-2024 above-128K rate. tokens is the text remainder; 14,955,127 video positions "
        "per video are charged in compute_flops, with a 7.2% visual-encoder term. One MCQ is exactly "
        "one video pass here, so a per-question unit is exact on this row at 1.42e17 FLOPs. The "
        "coefficient omits attention over 590,000-position contexts, adding 2.9x to 6.5x. Human "
        "time is the geometric mean of two transfers out of one 1h-walk VQA sentence, 11,653 s per "
        "question-rate and 1,393 s per second-of-video rate."),
))

models = [dict(
    model_id="gemini-1.5-pro-hourvideo",
    model="Gemini 1.5 Pro (HourVideo; models/gemini-1.5-pro-latest, unresolved revision)",
    company="Google DeepMind",
    model_release_date="",
    model_release_source="https://ai.google.dev/gemini-api/docs/changelog; research/hourvideo.md#model-record",
    flops_per_token="200000000000",
    flops_per_token_method="two_active_parameters",
    active_parameters="100000000000",
    active_parameters_basis="estimated",
    encoder_parameters="not_applicable",
    encoder_parameters_basis="not_applicable",
    decoder_parameters="not_applicable",
    decoder_parameters_basis="not_applicable",
    parameter_source=(
        "https://epochai.substack.com/p/notes-on-gpt-5-training-compute; "
        "research/hourvideo.md#model-record; "
        "../AI Compute vs Human Time/dataset/models.csv gemini-1.5-pro-001, gemini-1.5-pro-002"),
    notes=(
        "The evaluation code requests the models/gemini-1.5-pro-latest alias, so the revision is "
        "unpinned; Table 3's implied $7.00/M is the pre-2024-10-01 above-128K input rate, so the "
        "alias resolved to -001 or -002, which share this coefficient. Release date is blank rather "
        "than imputed. 100B active is the shared frontier prior, not a disclosure; 30-300B is its "
        "range."),
)]

LIMITS = dict(notes=586, task_description=560, performance_evidence=337, source_record=455,
              compute_source=220, human_time_source=205)
ok = True
for r in rows:
    assert set(r) == set(POINT_HEADER), set(POINT_HEADER) ^ set(r)
    for f, lim in LIMITS.items():
        n = len(r[f])
        flag = "OK " if n <= lim else "OVER"
        if n > lim:
            ok = False
        print(f"{flag} {r['point_id']:42s} {f:20s} {n:4d}/{lim}")
    for f in ("human_time_source", "compute_source", "source_record"):
        if r[f].rstrip()[-1] in ".,;:":
            print("TRAILING PUNCTUATION", r["point_id"], f)
            ok = False
for m in models:
    assert set(m) == set(MODEL_HEADER), set(MODEL_HEADER) ^ set(m)
    n = len(m["notes"])
    print(f"{'OK ' if n <= 365 else 'OVER'} {m['model_id']:42s} notes                {n:4d}/365")
    if n > 365:
        ok = False

os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "points.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=POINT_HEADER)
    w.writeheader()
    for r in rows:
        w.writerow(r)
with open(os.path.join(OUT, "models.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=MODEL_HEADER)
    w.writeheader()
    for m in models:
        w.writerow(m)
print("wrote", OUT, "ok" if ok else "WITH PROBLEMS")
sys.exit(0 if ok else 1)
