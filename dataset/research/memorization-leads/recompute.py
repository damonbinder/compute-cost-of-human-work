#!/usr/bin/env python3
"""Recompute the one-string memorization estimate; Python 3.9+ standard library.

Usage: python3 -B recompute.py --sources /path/to/sources --output /tmp/result.json
Reads retained evidence and source-inputs.json. Never executes the training code,
downloads a model, or writes into the evidence directory.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path


def calculate(sources):
    manifest = json.loads((sources / "source-manifest.json").read_text())
    for item in manifest:
        actual = hashlib.sha256((sources / item["file"]).read_bytes()).hexdigest()
        if actual != item["sha256"]:
            raise ValueError("Source hash mismatch: " + item["file"])
    inputs = json.loads((sources / "source-inputs.json").read_text())
    code = sources / "code/src"
    train = (code / "lib_llm/lib_llm/training/train.py").read_text()
    random = (code / "data/synthetic_strings/random.py").read_text()
    train_config = (code / "utils/memorization/memorization.py").read_text()
    assert 'evaluation_strategy="epoch"' in train_config
    assert "run_callbacks_initially: bool = True" in train
    assert '"llama2-13b": ("Llama-2-13b-hf"' in (code / "defs.py").read_text()
    padding = int(re.search(r"pad_to_multiple_of=(\d+)", train).group(1))
    held_out = int(re.search(r"default_num_test_strings: ClassVar\[int\] = (\d+)", random).group(1))
    n = inputs["string_symbols"]
    epochs = inputs["epochs"]
    parameters = inputs["parameters"]
    unpadded = n + inputs["bos_positions"]
    padded = ((unpadded + padding - 1) // padding) * padding
    training_positions = epochs * padded
    training_flops = 6 * parameters * training_positions
    callback_epochs = epochs + 1
    callback_positions_single = callback_epochs * (1 + held_out) * n
    callback_positions = inputs["callback_forward_passes"] * callback_positions_single
    trainer_validation_positions = epochs * held_out * padded
    eval_positions = callback_positions + trainer_validation_positions
    monitoring_flops = 2 * parameters * eval_positions
    total = training_flops + monitoring_flops

    # The donor values are read again from the original result-table extraction.
    table = (sources / "binary2019.txt").read_text()
    scores = []
    for donor in inputs["human_donors"]:
        pattern = re.escape(str(donor["id"])) + r"\s+(\d+)\s+"
        score = int(re.search(pattern, table).group(1))
        assert score == donor["credited_digits"]
        scores.append(score)
    scaled_seconds = [inputs["encoding_phase_seconds"] * n / s for s in scores]
    human_central = inputs["human_central_seconds"]
    minimal_callback_positions = callback_epochs * n
    return {
        "point_id": inputs["point_id"],
        "source_files_verified": len(manifest),
        "source_inputs_sha256": hashlib.sha256((sources / "source-inputs.json").read_bytes()).hexdigest(),
        "paper_version": inputs["paper_version"],
        "code_revision": inputs["code_revision"],
        "code_public_release_date": inputs["code_public_release_date"],
        "parameters": parameters,
        "string_symbols": n,
        "epochs": epochs,
        "training_input_positions_per_epoch": padded,
        "training_tokens": training_positions,
        "training_flops": training_flops,
        "callback_evaluations_per_split": callback_epochs,
        "held_out_strings": held_out,
        "callback_forward_passes_per_sequence": inputs["callback_forward_passes"],
        "callback_forward_positions": callback_positions,
        "trainer_validation_forward_positions": trainer_validation_positions,
        "monitoring_forward_positions": eval_positions,
        "monitoring_flops": monitoring_flops,
        "compute_flops": total,
        "monitoring_share": monitoring_flops / total,
        "compute_scenarios_flops": {
            "released_code_two_callback_forwards_central": total,
            "one_callback_forward_same_held_out_and_trainer_evaluations": training_flops + 2 * parameters * (callback_positions_single + trainer_validation_positions),
            "one_train_string_forward_per_epoch_no_held_out_or_trainer_evaluation": training_flops + 2 * parameters * minimal_callback_positions,
            "training_only_reference_excludes_required_monitoring": training_flops,
            "released_code_plus_5_percent_arithmetic_overhead": total * 1.05,
        },
        "donor_credited_digits": scores,
        "donor_encoding_phase_seconds": inputs["encoding_phase_seconds"],
        "donor_linear_1024_digit_seconds": scaled_seconds,
        "mean_donor_linear_seconds": sum(scaled_seconds) / len(scaled_seconds),
        "human_time": human_central,
        "human_transfer_sensitivity_seconds": [human_central * factor for factor in inputs["human_sensitivity_factors"]],
        "human_attempts": len(scores),
        "performance_read_from_figure_percent_approximate": inputs["ai_accuracy_percent_approximate"],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    sources, output = args.sources.resolve(), args.output.resolve()
    if output == sources or sources in output.parents:
        raise ValueError("Output must be outside the retained sources directory")
    if output.exists():
        raise FileExistsError("Use a new output file: " + str(output))
    result = calculate(sources)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
