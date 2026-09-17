#!/usr/bin/env python3
"""Inspect original Zorro pairs without running a model. Python3 standard library.

--pairs names the original23-file Zorro directory. --output must be a new file
outside that directory. This is a task-inspection audit, not a human-score model.
"""
import argparse
import difflib
import hashlib
import json
from pathlib import Path


RESIDUAL = {
    "argument_structure-transitive",
    "ellipsis-n_bar",
    "island-effects-adjunct_island",
    "island-effects-coordinate_structure_constraint",
    "quantifiers-superlative",
}


def audit(pairs):
    results = []
    for path in sorted(pairs.glob("*.txt")):
        lines = path.read_text().splitlines()
        assert len(lines) == 4000, path
        examples = []
        for index in [0, 333, 999, 1777]:
            bad, good = lines[index * 2:index * 2 + 2]
            bt, gt = bad.split(), good.split()
            changes = []
            for tag, i, j, k, l in difflib.SequenceMatcher(a=bt, b=gt).get_opcodes():
                if tag != "equal":
                    changes.append({"bad": bt[i:j], "good": gt[k:l]})
            examples.append({"pair_index_zero_based": index, "bad": bad, "good": good, "changes": changes})
        results.append({
            "paradigm": path.stem,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "pair_count": len(lines) // 2,
            "mean_whitespace_positions_per_sentence": sum(len(s.split()) for s in lines) / len(lines),
            "targeted_in_18_paradigm_feasibility_scenario": path.stem not in RESIDUAL,
            "examples": examples,
        })
    assert len(results) == 23
    count = sum(r["targeted_in_18_paradigm_feasibility_scenario"] for r in results)
    assert count == 18
    return {
        "paradigms": results,
        "total_pairs": sum(r["pair_count"] for r in results),
        "feasibility_scenario": {
            "interpretation": "Assumed target coverage; not measured human performance or a guaranteed learning curve",
            "trained_paradigms": count,
            "assumed_accuracy_on_trained": 0.89,
            "residual_paradigms": len(RESIDUAL),
            "assumed_accuracy_on_residual": 0.5,
            "overall_assumed_accuracy": (count * 0.89 + len(RESIDUAL) * 0.5) / len(results),
        },
        "human_duration_proposal": {
            "closed_class_forms_and_lexical_orientation_hours_assumed": 6,
            "worked_rule_instruction_hours_assumed": 9,
            "feedback_pairs_assumed": 3600,
            "seconds_per_feedback_pair_assumed": 25,
            "feedback_hours_assumed": 3600 * 25 / 3600,
            "central_hours_estimated": 40,
            "central_seconds_estimated": 40 * 3600,
            "sensitivity_hours_assumed": [10, 120],
            "contextual_learning_study": "Batterink and Neville2013 explicit group:23 adults, approximately1h exposure plus<5min rules;89% mean on3 grammatical constructions",
            "contextual_study_participants": 23,
        },
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--pairs", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    pairs, output = args.pairs.resolve(), args.output.resolve()
    if output == pairs or pairs in output.parents:
        raise ValueError("Output must be outside the source-pair directory")
    if output.exists():
        raise FileExistsError(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(audit(pairs), indent=2) + "\n")


if __name__ == "__main__":
    main()
