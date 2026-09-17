#!/usr/bin/env python3
"""Write the candidate CSV rows for game-factorio-gpt6astra and gpt-5-6-luna.

Numeric fields come from the retained calculations file, so the CSV cannot drift
from the arithmetic. Text fields are held here and are length-capped to the
maxima already present in the production dataset, checked at write time:

    notes 586, task_description 560, performance_evidence 337,
    source_record 455, compute_source 220, human_time_source 205,
    models.csv notes 365.

The shared `gpt-6-astra` model row is copied byte-for-byte from this folder's
accepted `models.csv` rather than restated, so it cannot drift from the registry.
Its coefficient is checked against the active-parameter count the calculations
file actually used, so a prior change cannot land in one file and not the other.

Standard library only. Explicit input and output paths; nothing is modified in
place. Run `compute_factorio_astra.py` first. Usage:

    python3 research/factorio-astra/build_rows.py \
        --calculations    research/factorio-astra/calculations.json \
        --points-header   points.csv \
        --models-header   models.csv \
        --astra-model-row models.csv \
        --out-points      candidates/factorio-astra/points.csv \
        --out-models      candidates/factorio-astra/models.csv
"""

import argparse
import csv
import json


# Longest value present in the production dataset for each field, which new rows
# are kept at or under.
CAPS = {
    "notes": 586,
    "task_description": 560,
    "performance_evidence": 337,
    "source_record": 455,
    "compute_source": 220,
    "human_time_source": 205,
}
MODEL_NOTES_CAP = 365

TASK_DESCRIPTION = (
    "One GPT-6 Astra run through Codex /goal played the Factorio base game with enemies "
    "enabled, from a fresh map on a seed of its own choosing to the rocket launch, the game's "
    "win condition. Astra planned and a GPT-5.6 Luna worker at medium reasoning effort "
    "executed as a subagent: the loop pauses the game, forks the save to test designs in Lua, "
    "scripts the inputs, and screenshots to check placement. Includes all intermediate design "
    "work, failures and retries. The human unit is one player finishing Factorio's main story "
    "unaided, the same rocket launch."
)

PERFORMANCE_EVIDENCE = (
    "The GPT-6 Astra run reached Factorio's victory screen, showing Time played 43:40:46 and "
    "the dialog announcing the rocket launch. The human baseline is 279 polled "
    "HowLongToBeat main-story completions at a mean of 201,181 seconds; the base game's only "
    "win condition is that same launch, though each submitter's criterion is unrecorded."
)

COMPUTE_SOURCE = (
    "research/factorio-astra.md#compute; research/factorio-astra/calculations.json; "
    "research/factorio-astra/compute_factorio_astra.py; "
    "agent-work/sources/factorio-astra/openai-list-prices-2026-09-13.json"
)

HUMAN_TIME_SOURCE = (
    "https://howlongtobeat.com/game/17455; research/factorio-astra.md#human-baseline"
)

SOURCE_RECORD = (
    "https://x.com/_Mira___Mira_/status/2098343807410712814 completion and cost; "
    "https://x.com/_Mira___Mira_/status/2096713682818630027 goal prompt and harness; "
    "gpt-6-astra through Codex /goal with gpt-5.6-luna at medium reasoning effort as the "
    "worker, Astra's effort not stated; retained extracts in "
    "agent-work/sources/factorio-astra/MANIFEST.md and agent-work/sources/factorio-astra/run-facts.json; "
    "performance: https://pbs.twimg.com/media/HR7K72GakAAOA2t.jpg"
)

NOTES = (
    "No token counters were published; compute inverts the operator's about-$4,500 API cost at "
    "list prices on the Portal run's measured mix. Its two transferable quantities disagree: "
    "dollars per billed unit give 3.73e19 FLOPs, cached prefix with cadence 8.16e19, and the "
    "recorded value is their geometric mean; the 100-600B size range gives 1.9e19-1.1e20 "
    "and omitted cached-context attention would add 4.6e19-2.0e20. The donor's 36.19% share is "
    "transferred, so tokens is text only. Luna is assumed 2% of spend, the 4 d 11 h clock a "
    "lower bound, and the agent plays paused, scripting inputs."
)

LUNA_NOTES = (
    "8B active is the dataset's nano-tier prior, carried across because OpenAI's model "
    "page positions Luna as roughly corresponding to the nano tier of earlier GPT-5 families. "
    "That establishes the tier, not the size, and the prior is anchored on 2024 models; 3-24B "
    "is the scenario range. Price is not used as size evidence, and reasoning effort is a task "
    "configuration."
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--calculations", required=True)
    ap.add_argument("--points-header", required=True)
    ap.add_argument("--models-header", required=True)
    ap.add_argument("--astra-model-row", required=True)
    ap.add_argument("--out-points", required=True)
    ap.add_argument("--out-models", required=True)
    args = ap.parse_args()

    calc = json.load(open(args.calculations))
    c = calc["central"]

    point = {
        "point_id": "game-factorio-gpt6astra",
        "task": "Complete the Factorio base game by launching a rocket",
        "task_category": "games",
        "task_description": TASK_DESCRIPTION,
        "model_id": "gpt-6-astra",
        "compute_scope": "inference",
        "compute_flops": repr(c["flops"]),
        "human_skill": "typical",
        "human_time_scope": "task_performance",
        "human_time": repr(calc["csv_values"]["human_time"]),
        "performance_vs_human": "match",
        "comparison_issues": "different_inputs_or_tools; different_attempt_selection",
        "compute_evidence": "derived_assumed_inputs",
        "human_time_evidence": "task_timings",
        "performance_evidence": PERFORMANCE_EVIDENCE,
        "human_time_statistic": "mean",
        "human_time_subset": "successful",
        "human_attempts": repr(calc["csv_values"]["human_attempts"]),
        "human_time_source": HUMAN_TIME_SOURCE,
        "human_time_method": "other_calculation",
        "compute_method": "operation_count",
        "compute_statistic": "total",
        "compute_subset": "all",
        "ai_attempts": "1",
        "compute_source": COMPUTE_SOURCE,
        "tokens": repr(c["text_tokens"]),
        "tokens_accounting": "input_cache_creation_output",
        "source_dataset": "Mira Factorio base-game run, GPT-6 Astra, September 2026",
        "source_record": SOURCE_RECORD,
        "notes": NOTES,
    }

    luna = {
        "model_id": "gpt-5-6-luna",
        "model": "GPT-5.6 Luna",
        "company": "OpenAI",
        "model_release_date": "2026-07-09",
        "model_release_source":
            "https://developers.openai.com/api/docs/changelog; https://openai.com/index/gpt-5-6/",
        "flops_per_token": "16000000000",
        "flops_per_token_method": "two_active_parameters",
        "active_parameters": "8000000000",
        "active_parameters_basis": "estimated",
        "encoder_parameters": "not_applicable",
        "encoder_parameters_basis": "not_applicable",
        "decoder_parameters": "not_applicable",
        "decoder_parameters_basis": "not_applicable",
        "parameter_source":
            "https://developers.openai.com/api/docs/models/gpt-5.6-luna; "
            "https://cbowdon.github.io/posts/gpt-params/index.html; "
            "https://mistral.ai/news/ministraux/; research/factorio-astra.md#model-records",
        "notes": LUNA_NOTES,
    }

    # Checks that must hold before anything is written.
    for field, cap in CAPS.items():
        n = len(point[field])
        if n > cap:
            raise SystemExit("%s is %d characters, over the dataset maximum of %d"
                             % (field, n, cap))
    if len(luna["notes"]) > MODEL_NOTES_CAP:
        raise SystemExit("gpt-5-6-luna notes is %d characters, over %d"
                         % (len(luna["notes"]), MODEL_NOTES_CAP))
    # validate.py captures a cited path up to whitespace, ';', ',' or a bracket,
    # so a path must not be followed directly by any other punctuation.
    import re
    for field in ("compute_source", "human_time_source", "source_record"):
        for m in re.finditer(r'(?:research|sources)/[^\s;,()]*[.,:!?](?=\s|$)', point[field]):
            raise SystemExit("%s: cited path ends in punctuation: %r" % (field, m.group(0)))

    points_header = open(args.points_header).readline().rstrip("\r\n").split(",")
    models_header = open(args.models_header).readline().rstrip("\r\n").split(",")
    if set(point) != set(points_header):
        raise SystemExit("points fields differ from the header")
    if set(luna) != set(models_header):
        raise SystemExit("models fields differ from the header")

    astra = [r for r in csv.DictReader(open(args.astra_model_row))
             if r["model_id"] == "gpt-6-astra"]
    if len(astra) != 1:
        raise SystemExit("expected exactly one gpt-6-astra row in " + args.astra_model_row)
    used = calc["inputs"]["astra_active_parameters"]
    if float(astra[0]["active_parameters"]) != used:
        raise SystemExit(
            "gpt-6-astra is %s active in %s but the calculations used %s; rerun "
            "compute_factorio_astra.py against the ruled prior"
            % (astra[0]["active_parameters"], args.astra_model_row, used))
    if float(astra[0]["flops_per_token"]) != 2 * used:
        raise SystemExit("gpt-6-astra flops_per_token is not 2 * active_parameters")
    if float(luna["active_parameters"]) != calc["inputs"]["luna_active_parameters"]:
        raise SystemExit("gpt-5-6-luna active_parameters disagrees with the calculations")

    with open(args.out_points, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=points_header)
        w.writeheader(); w.writerow(point)
    with open(args.out_models, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=models_header)
        w.writeheader(); w.writerow(astra[0]); w.writerow(luna)

    print("wrote", args.out_points, "and", args.out_models)
    for field, cap in CAPS.items():
        print("  %-22s %4d / %d" % (field, len(point[field]), cap))
    print("  %-22s %4d / %d" % ("models notes (luna)", len(luna["notes"]), MODEL_NOTES_CAP))
    print("  compute_flops", point["compute_flops"], " tokens", point["tokens"])


if __name__ == "__main__":
    main()
