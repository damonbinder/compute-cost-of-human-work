#!/usr/bin/env python3
"""Write the candidate points.csv and models.csv for reas-flt-lean-anthropic-internal.

Field values are held here so the row is regenerated rather than hand-edited, and so the
recorded numbers come from research/flt-anthropic/calculations.json rather than being
retyped. Headers are copied from the batch root CSVs, so a header change there propagates.

Dependencies: Python 3.8+ standard library only.

Usage (paths are explicit):

    python3 build_flt_rows.py --base . --out candidates/flt-anthropic

--base is the batch root, the directory holding points.csv, models.csv and research/.
--out is the directory to write points.csv and models.csv into; it is created if needed.
The script reads --base/points.csv, --base/models.csv and
--base/research/flt-anthropic/calculations.json, and writes only the two files in --out.
"""
import argparse, csv, json, os

_ap = argparse.ArgumentParser(description=__doc__,
                              formatter_class=argparse.RawDescriptionHelpFormatter)
_ap.add_argument("--base", required=True, help="batch root holding points.csv and research/")
_ap.add_argument("--out", required=True, help="directory to write points.csv and models.csv into")
_args = _ap.parse_args()
BASE = _args.base
OUT = _args.out
os.makedirs(OUT, exist_ok=True)

calc = json.load(open(os.path.join(BASE, "research", "flt-anthropic", "calculations.json")))
rec = calc["recorded_values"]

points_header = next(csv.reader(open(os.path.join(BASE, "points.csv"))))
models_header = next(csv.reader(open(os.path.join(BASE, "models.csv"))))

MODEL_ID = "anthropic-internal-research-flt-2026-08"

task_description = (
    "Produce a machine-checked Lean 4 proof of Fermat's Last Theorem from the one-line goal "
    "statement, on Mathlib v4.33.0 plus the Imperial College FLT project and flt-regular. Complete "
    "means the build asserts exactly Lean's three standard axioms, no sorry, and comparator matches "
    "a Mathlib-only statement. One such proof: 29,511 theorems, the classical steps in the "
    "restricted forms the argument needs. AI side: one 11-day run from 7 August 2026, dozens of "
    "agents on a Claude Code harness over Prove2Me. Human side: same theorem, same standard, "
    "Mathlib idiom."
)

performance_evidence = (
    "The build compiled all 60,475 modules and asserts fermat_last_theorem rests on exactly "
    "Lean's three standard axioms; comparator v4.33.0 matched a Mathlib-only statement; nanoda "
    "checked 1,052,234 declarations; Buzzard reran comparator. No observed human result; the "
    "assumed matched-quality target is 84,000 active hours, 42 py at 2,000 h."
)

human_time_source = (
    "research/flt-anthropic.md#human-baseline; "
    "agent-work/sources/flt-anthropic/human-anchor-measurements.json; "
    "https://gtr.ukri.org/projects?ref=EP%2FY022904%2F1"
)

compute_source = (
    "research/flt-anthropic.md#compute; research/flt-anthropic/calculations.json; "
    "research/flt-anthropic/compute_flt_anthropic.py; "
    "https://www.anthropic.com/research/formalizing-fermats-last-theorem"
)

source_record = (
    "https://www.anthropic.com/research/formalizing-fermats-last-theorem; "
    "https://www-cdn.anthropic.com/9e431dff043da6538d99d6c2d231b670aa3da263.pdf; "
    "https://github.com/anthropics/fermats-last-theorem files README.md, PROOF-PATH.md, "
    "ATTRIBUTION.md, FinalCheck.lean, Theorems/Thm_fermat_last_theorem.lean; "
    "agent-work/sources/flt-anthropic/MANIFEST.md lists retained extracts; "
    "performance: https://xenaproject.wordpress.com/2026/09/04/flt-anthropic-has-beaten-me-to-it/"
)

notes = (
    "Anthropic published output tokens only, about six billion: a floor of 1.2e21 FLOPs. Counted "
    "tokens are (1+r) x output at r = 4.21 appended tokens per output token, a per-turn "
    "composition ratio from the Meta donor; donor band 3.5-5.3 and transfer band 3 to 10 give "
    "3.6e21 to 1.2e22. The appended basis holds only if the Claude Code harness cached, inferred "
    "not observed; uncached the gross count gives 1.8e23. nanoda ran on a build Anthropic "
    "patched. Human time is an expert estimate, no timing sample: 84,000 active hours, 42 "
    "person-years at 2,000 hours, range 24,000-300,000 h."
)

model_notes = (
    "Identity unresolved: an internal Anthropic research model, never released or named, described "
    "only as roughly comparable to Claude Fable 5.1, the comparability anchor rather than the "
    "model. Both release fields are blank: it was never public. 100B active is the dataset's shared "
    "frontier prior; 30B-300B moves dependent FLOPs 0.3x to 3x. Claude 4.7 tokenizer era."
)

point = {
    "point_id": "reas-flt-lean-anthropic-internal",
    "task": "Formalize Fermat's Last Theorem end to end in Lean 4",
    "task_category": "mathematics_puzzles",
    "task_description": task_description,
    "model_id": MODEL_ID,
    "compute_scope": "inference",
    "compute_flops": repr(rec["compute_flops"]),
    "human_skill": "expert",
    "human_time_scope": "task_performance",
    "human_time": repr(rec["human_time_seconds"]),
    "performance_vs_human": "match",
    "comparison_issues": "different_task",
    "compute_evidence": "derived_assumed_inputs",
    "human_time_evidence": "assumed",
    "performance_evidence": performance_evidence,
    "human_time_statistic": "point_estimate",
    "human_time_subset": "not_applicable",
    "human_attempts": "not_applicable",
    "human_time_source": human_time_source,
    "human_time_method": "estimated",
    "compute_method": "params_tokens",
    "compute_statistic": "total",
    "compute_subset": "all",
    "ai_attempts": "1",
    "compute_source": compute_source,
    "tokens": repr(rec["tokens"]),
    "tokens_accounting": "input_cache_creation_output",
    "source_dataset": "Anthropic Fermat's Last Theorem Lean formalization, August 2026",
    "source_record": source_record,
    "notes": notes,
}

model = {
    "model_id": MODEL_ID,
    "model": ("Anthropic internal research model, August 2026 FLT run (unnamed; described as roughly "
              "comparable to Claude Fable 5.1)"),
    "company": "Anthropic",
    "model_release_date": "",
    "model_release_source": "",
    "flops_per_token": "200000000000",
    "flops_per_token_method": "two_active_parameters",
    "active_parameters": "100000000000",
    "active_parameters_basis": "estimated",
    "encoder_parameters": "not_applicable",
    "encoder_parameters_basis": "not_applicable",
    "decoder_parameters": "not_applicable",
    "decoder_parameters_basis": "not_applicable",
    "parameter_source": ("research/flt-anthropic.md#model-identity; transfer of the shared frontier "
                         "closed-model prior carried by claude-opus-4-5, claude-opus-4-8 and "
                         "claude-opus-5 in ../AI Compute vs Human Time/dataset/models.csv and by "
                         "gpt-6-astra in models.csv"),
    "notes": model_notes,
}

for path, header, row in ((os.path.join(OUT, "points.csv"), points_header, point),
                          (os.path.join(OUT, "models.csv"), models_header, model)):
    assert set(row) == set(header), (set(header) ^ set(row))
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=header)
        w.writeheader()
        w.writerow(row)
    print("wrote", path)
