#!/usr/bin/env python3
"""Recompute Five training and its human experience baseline; standard library only.

Required: --sources DIR --recipe FILE --output NEW_FILE. Inputs are read-only.
"""
import argparse
import csv
import hashlib
import itertools
import json
import math
from pathlib import Path
import statistics
import xml.etree.ElementTree as ET
import zipfile

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def xlsx_rows(path):
    with zipfile.ZipFile(path) as z:
        strings = []
        if "xl/sharedStrings.xml" in z.namelist():
            strings = ["".join(n.itertext()) for n in
                       ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", NS)]
        tree = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
        result = []
        for row in tree.findall("m:sheetData/m:row", NS):
            cells = {}
            for cell in row.findall("m:c", NS):
                column = "".join(c for c in cell.attrib["r"] if c.isalpha())
                value = cell.find("m:v", NS)
                raw = value.text if value is not None else None
                if cell.attrib.get("t") == "s":
                    raw = strings[int(raw)]
                elif cell.attrib.get("t") == "inlineStr":
                    raw = "".join(cell.find("m:is", NS).itertext())
                elif raw is not None:
                    raw = float(raw)
                cells[column] = raw
            result.append(cells)
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sources", type=Path, required=True)
    ap.add_argument("--recipe", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    sources, recipe_path, output = (p.resolve() for p in
                                    (args.sources, args.recipe, args.output))
    if output.exists() or sources == output or sources in output.parents or output == recipe_path:
        ap.error("Output must be a new file outside the source directory.")
    source_hashes = {}
    for entry in json.loads((sources / "five-source-manifest.json").read_text())["files"]:
        path = (sources / entry["path"]).resolve()
        if sources not in path.parents:
            raise ValueError("Source path escapes source directory")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != entry["sha256"]:
            raise ValueError(f"Source hash mismatch: {entry['path']}")
        source_hashes[entry["path"]] = digest
    p = json.loads(recipe_path.read_text())
    rows = xlsx_rows(sources / "dota-human-data.xlsx")
    assert [rows[0][c] for c in "ABCD"] == ["Age", "Education", "TimeOnTask", "MMR"]
    humans = [{"xlsx_row": i, "games": r["C"], "mmr": r["D"]}
              for i, r in enumerate(rows[1:], start=2)]
    assert len(humans) == 304
    selected = [r for r in humans if r["mmr"] >= p["human_mmr_minimum"]]
    mean_games = statistics.mean(r["games"] for r in selected)
    rohlcke_seconds = mean_games * p["human_minutes_per_game"] * 60  # one player
    career_years = p["human_career_years_per_player"]
    assert len(career_years) == p["human_players_required"]
    weeks = p["human_weeks_per_year"]
    rate = p["human_practice_hours_per_week"]
    # One policy plays all five heroes; the human counterpart is ONE player learning
    # the game, so the mean career, not the team sum (Damon, 2026-09-15).
    mean_career = statistics.mean(career_years)
    human_seconds = mean_career * weeks * rate * 3600
    human_scenarios = [mean_career * weeks * r * 3600
                       for r in (rate - p["human_practice_hours_per_week_sd"],
                                 p["human_practice_hours_per_week_upper_scenario"])]
    trained_fraction = (p["self_play_game_fraction"] * p["current_teams_in_self_play"] +
                        p["past_opponent_game_fraction"] * p["current_teams_in_past_opponent_game"]) / p["all_teams_per_game"]
    optimization = p["optimization_petaflop_days"] * 1e15 * 86400
    rollout = optimization / (p["training_to_forward_ratio"] *
                              p["effective_sample_reuse"] * trained_fraction)
    eval_games = (p["evaluation_active_training_days"] * 24 /
                  p["evaluation_update_hours"] * p["evaluation_games_per_update"])
    eval_forward = 2 * p["final_parameters"] * p["evaluation_forward_multiplier"]
    evaluation = (eval_games * p["evaluation_game_minutes"] * 60 *
                  p["policy_steps_per_game_second"] * p["heroes_per_game"] * eval_forward)
    # Original blog totals provide an independent approximation, not an extra term.
    history_rollout = (365.25 * 86400 * p["policy_steps_per_game_second"] *
                       p["heroes_per_game"] * 2 *
                       (p["blog_early_simulated_years"] * p["early_parameters"] +
                        (p["blog_total_simulated_years"] - p["blog_early_simulated_years"]) *
                        p["final_parameters"]))
    scenarios = []
    for opt, ratio, reuse, fraction in itertools.product(
            p["optimization_sensitivity_petaflop_days"],
            p["training_to_forward_ratio_sensitivity"],
            p["sample_reuse_sensitivity"], [0.5, 0.9, 1.0]):
        base = opt * 1e15 * 86400
        scenarios.append(base + base / (ratio * reuse * fraction) + evaluation)
    result = {
        "point_id": "game-dota2-train-openaifive",
        "source_hashes": source_hashes,
        "recipe_sha256": hashlib.sha256(recipe_path.read_bytes()).hexdigest(),
        "human_source_rows": selected,
        "human_source_population_count": len(humans),
        "human_selected_count": len(selected),
        "human_mean_games": mean_games,
        "human_median_games": statistics.median(r["games"] for r in selected),
        "human_mean_mmr": statistics.mean(r["mmr"] for r in selected),
        "human_mmr_range": [min(r["mmr"] for r in selected), max(r["mmr"] for r in selected)],
        "human_career_years_per_player": career_years,
        "human_practice_hours_per_week": rate,
        "human_time": human_seconds,
        "human_practice_rate_sensitivity_seconds": human_scenarios,
        "rohlcke_cross_check_seconds": rohlcke_seconds,
        "rohlcke_game_duration_sensitivity_seconds": [mean_games * m * 60
                                                      for m in p["human_minutes_per_game_sensitivity"]],
        "rohlcke_extra_study_sensitivity_seconds": [rohlcke_seconds * (1 + x)
                                                    for x in p["human_offline_study_extra_fraction_sensitivity"]],
        "optimization_flops": optimization,
        "assumed_training_eligible_hero_fraction": trained_fraction,
        "rollout_flops": rollout,
        "evaluation_game_count_estimate": eval_games,
        "evaluation_flops": evaluation,
        "compute_flops": optimization + rollout + evaluation,
        "all_input_sensitivity_flops": [min(scenarios), max(scenarios)],
        "historical_blog_rollout_cross_check_flops": history_rollout,
        "historical_blog_implied_sample_reuse": optimization / (3 * trained_fraction * history_rollout),
        "historical_blog_total_cross_check_flops": optimization + history_rollout + evaluation,
        "evaluation_fraction_of_total": evaluation / (optimization + rollout + evaluation),
        "omit_past_opponents_counterfactual_flops": optimization + rollout * trained_fraction + evaluation,
        "one_team_trajectories_per_game_sensitivity_flops": optimization + optimization / (3 * 0.5) + evaluation,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
