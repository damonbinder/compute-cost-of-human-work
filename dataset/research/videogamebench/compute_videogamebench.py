#!/usr/bin/env python3
"""Convert VideoGameBench per-run API cost into a token workload and a FLOP estimate.

The paper (arXiv:2505.18134) publishes a dollar figure for each model-game run and no
token counts.  The harness produced those dollars with ``litellm.completion_cost`` over
the provider's own usage counters, so cost is an exact linear function of the measured
input and output tokens at known prices:

    cost = input_tokens * price_in + output_tokens * price_out

This script inverts that relation.  It reconstructs what each VG-Agent request contained
from the released harness (fixed prompts, a 20-message rolling context that re-sends its
images, one screenshot per executed action at a known resolution), prices the requests in
order from the first call of the run, and stops when their cumulative cost reaches the
published run cost.  Early calls carry a shorter history than the steady state, which
matters for the two runs that lasted under ten calls.  FLOPs use the dataset's
2 * active_parameters convention over every processed position, text and image alike, plus
a separate visual-encoder term for GPT-4o, whose dataset model record declares one.

Only the ratio of output to input tokens materially affects the FLOP total: the image and
text split changes which positions are called text, not how many positions there are.

Dependencies: Python 3.8+ standard library only.

Usage:
    python3 compute_videogamebench.py \
        --inputs       research/videogamebench/inputs.json \
        --walkthroughs agent-work/sources/videogamebench/walkthrough-metadata.json \
        --out          research/videogamebench/calculations.json \
        --points-out   candidates/videogamebench/points.csv \
        --models-out   candidates/videogamebench/models.csv

All paths are explicit; the script only writes the files named by --out, --points-out and
--models-out and never modifies its inputs.
"""

import argparse
import csv
import json
import os

MODEL_ORDER = ["gpt4o", "sonnet37", "gemini25pro", "llama4mav", "gemini20flash"]
GAME_ORDER = ["civ1", "nfs", "tim", "doom2", "crystal", "kirby", "zelda"]

def point_id(game, model):
    return "game-vgb-%s-%s" % (game, model)


# --------------------------------------------------------------------------------------
# Context reconstruction
# --------------------------------------------------------------------------------------

def dos_history(call_index, frames_per_step):
    """Message roles of a DOS agent's history before call `call_index` (1-based).

    The evaluator stores one observation before the loop, then each step appends the
    assistant's JSON, an "Observation: ..." line and one "Frame:" message per captured
    frame.  `get_action` reads the history before appending its own assistant message, so
    the tail is always a frame message.  Pass call_index=None for the steady state.
    """
    if call_index is None:
        cycle = ["assistant", "obs"] + ["frame"] * frames_per_step
        return cycle * 24
    seq = ["frame"]
    for _ in range(call_index - 1):
        seq += ["assistant", "obs"] + ["frame"] * frames_per_step
    return seq


def gb_history(call_index, actions_per_call):
    """Message roles of a Game Boy agent's history before call `call_index` (1-based).

    One call returns a list of actions; each executed action appends its own image message
    and only one assistant message is appended per call, so images outnumber assistant
    messages by `actions_per_call` to one.  The wait loop between calls runs `no_op` without
    storing observations, so it adds nothing.  Pass call_index=None for the steady state.
    """
    if call_index is None:
        cycle = ["assistant"] + ["frame"] * actions_per_call
        return cycle * 24
    seq = ["frame"]
    for _ in range(call_index - 1):
        seq += ["assistant"] + ["frame"] * actions_per_call
    return seq


def per_request(inp, game_key, model_key, params, call_index=None):
    """Text tokens, image billing units and output tokens for one API request.

    `call_index` is the 1-based position of the call within the run, or None for the
    steady state in which the context window is always full.
    """
    P = inp["prompt_tokens"]
    game = inp["games"][game_key]
    model = inp["models"][model_key]
    C = model["context_messages"]
    A = params["response_action_tokens"]
    M = params["response_memory_tokens"]
    ovh = P["message_overhead"]

    priced_reasoning = 0
    unpriced_reasoning = 0
    if model_key == "gemini25pro":
        priced_reasoning = params["gemini25pro_reasoning_tokens_per_call"]
        unpriced_reasoning = params["gemini25pro_unpriced_reasoning_tokens_per_call"]

    if game["emulator"] == "dos":
        F = params["dos_frames_per_step"]
        size = params["dos_image_size"]
        roles = dos_history(call_index, F)[-C:]
        text = P["system_dos"] + 2 + game["task_prompt_tokens"]
        text += roles.count("obs") * P["dos_observation_line"]
        text += roles.count("frame") * P["dos_frame_label"]
        text += roles.count("assistant") * (A + P["dos_assistant_json_overhead"])
        text += P["reflection_prompt"] + M + P["dos_mouse_line"] + game["task_prompt_tokens"]
        text += ovh * (len(roles) + 2)
        n_images = roles.count("frame") + F
        base_out = A + M + P["dos_response_json_overhead"]
    else:
        K = params["gb_actions_per_call"]
        size = params["gb_image_size"]
        roles = gb_history(call_index, K)[-C:]
        text = P["system_gba_realtime"] + 2 + game["task_prompt_tokens"]
        text += roles.count("frame") * P["gb_frame_label"]
        text += roles.count("assistant") * (A + P["gb_assistant_prefix"])
        text += P["reflection_prompt"] + M
        text += P["gba_realtime_prompt"]
        text += ovh * (len(roles) + 3)
        n_images = roles.count("frame")
        base_out = A + M + P["gb_response_tag_overhead"]

    # Thinking tokens count against maxOutputTokens on these endpoints, so the cap applies
    # to the whole generated output.
    priced_out = min(base_out + priced_reasoning, model["max_output_tokens"])
    generated_out = min(base_out + priced_reasoning + unpriced_reasoning,
                        model["max_output_tokens"])

    image_units = n_images * model["image_tokens"][size]
    return {
        "text_tokens_per_request": text,
        "images_per_request": n_images,
        "image_size": size,
        "image_units_per_image": model["image_tokens"][size],
        "image_units_per_request": image_units,
        "priced_output_tokens_per_request": priced_out,
        "generated_output_tokens_per_request": generated_out,
        "priced_reasoning_tokens_per_request": priced_reasoning,
        "unpriced_reasoning_tokens_per_request": unpriced_reasoning,
    }


def evaluate(inp, game_key, model_key, params):
    model = inp["models"][model_key]

    p_in = model["price_in_per_token"]
    p_out = model["price_out_per_token"]
    if model_key == "llama4mav" and params["llama4_price_override"]:
        p_in, p_out = params["llama4_price_override"]

    def price(r):
        return ((r["text_tokens_per_request"] + r["image_units_per_request"]) * p_in
                + r["priced_output_tokens_per_request"] * p_out)

    budget = inp["run_cost_usd"][game_key][model_key]
    steady = per_request(inp, game_key, model_key, params, None)

    calls = 0.0
    text_tokens = 0.0
    image_positions_units = 0.0
    spent = 0.0
    if params["ramp_up_context"]:
        i = 1
        while True:
            r = per_request(inp, game_key, model_key, params, i)
            c = price(r)
            share = 1.0 if spent + c <= budget else (budget - spent) / c
            calls += share
            text_tokens += share * (r["text_tokens_per_request"]
                                    + r["generated_output_tokens_per_request"])
            image_positions_units += share * r["image_units_per_request"]
            spent += share * c
            if share < 1.0:
                break
            i += 1
            # Once the window is full every later call is identical to the steady state.
            if price(per_request(inp, game_key, model_key, params, i)) == price(steady):
                remaining = budget - spent
                extra = remaining / price(steady)
                calls += extra
                text_tokens += extra * (steady["text_tokens_per_request"]
                                        + steady["generated_output_tokens_per_request"])
                image_positions_units += extra * steady["image_units_per_request"]
                spent = budget
                break
    else:
        calls = budget / price(steady)
        text_tokens = calls * (steady["text_tokens_per_request"]
                               + steady["generated_output_tokens_per_request"])
        image_positions_units = calls * steady["image_units_per_request"]

    image_positions = image_positions_units if params["image_units_are_positions"] else 0.0
    positions = text_tokens + image_positions
    flops = 2.0 * model["active_parameters"] * positions

    encoder = model.get("encoder_parameters")
    encoder_flops = 0.0
    if encoder and params["gpt4o_encoder_parameters"] and params["image_units_are_positions"]:
        encoder_flops = 2.0 * encoder * image_positions
        flops += encoder_flops

    out = dict(steady)
    out.update({
        "price_in_per_token": p_in,
        "price_out_per_token": p_out,
        "run_cost_usd": budget,
        "steady_state_cost_per_request_usd": price(steady),
        "implied_requests": calls,
        "text_tokens_total": text_tokens,
        "image_positions_total": image_positions,
        "processed_positions_total": positions,
        "encoder_flops": encoder_flops,
        "compute_flops": flops,
    })
    if inp["games"][game_key]["emulator"] == "gb":
        out["implied_game_actions"] = calls * params["gb_actions_per_call"]
    else:
        out["implied_game_actions"] = calls
    return out


def merged(central, override):
    p = dict(central)
    p.update(override)
    return p


# --------------------------------------------------------------------------------------
# CSV generation
# --------------------------------------------------------------------------------------

POINTS_HEADER = ["point_id", "task", "task_category", "task_description", "model_id",
                 "compute_scope", "compute_flops", "human_skill", "human_time_scope",
                 "human_time", "performance_vs_human", "comparison_issues",
                 "compute_evidence", "human_time_evidence", "performance_evidence",
                 "human_time_statistic", "human_time_subset", "human_attempts",
                 "human_time_source", "human_time_method", "compute_method",
                 "compute_statistic", "compute_subset", "ai_attempts", "compute_source",
                 "tokens", "tokens_accounting", "source_dataset", "source_record", "notes"]

MODELS_HEADER = ["model_id", "model", "company", "model_release_date", "model_release_source",
                 "flops_per_token", "flops_per_token_method", "active_parameters",
                 "active_parameters_basis", "encoder_parameters", "encoder_parameters_basis",
                 "decoder_parameters", "decoder_parameters_basis", "parameter_source", "notes"]

# The shared Gemini 2.5 Pro 03-25 record, copied byte-identically from
# candidates/balrog/models.csv so the two batches merge to one record.  Any edit here must
# be made in both batches, or incorporate.py will see a conflict.
BALROG_MODELS_CSV = "candidates/balrog/models.csv"
SHARED_MODEL_IDS = ["gemini-2.5-pro-03-25"]


def load_shared_model_rows(path):
    with open(path, newline="") as f:
        rows = {r["model_id"]: r for r in csv.DictReader(f)}
    missing = [m for m in SHARED_MODEL_IDS if m not in rows]
    if missing:
        raise SystemExit("shared model record(s) %s not found in %s" % (missing, path))
    return [rows[m] for m in SHARED_MODEL_IDS]

DOS_GAMES = {"civ1", "nfs", "tim", "doom2"}

TASK_NAME = {
    "civ1": "Complete Civilization I from raw frames",
    "nfs": "Complete The Need for Speed from raw frames",
    "tim": "Complete The Incredible Machine from raw frames",
    "doom2": "Complete Doom II from raw frames",
    "crystal": "Complete Pokemon Crystal from raw frames",
    "kirby": "Complete Kirby's Dream Land from raw frames",
    "zelda": "Complete Link's Awakening DX from raw frames",
}

COMPLETION = {
    "civ1": "win on Chieftain, seven civilizations",
    "nfs": "first on all nine tracks",
    "tim": "solve all 87 levels",
    "doom2": "beat all 30 stages",
    "crystal": "all sixteen badges, then Red",
    "kirby": "clear all five stages",
    "zelda": "all eight instruments, then the Owl",
}

PLATFORM = {
    "dos": "640x400 MS-DOS frames; mouse and keyboard actions",
    "gb": "160x144 Game Boy frames; button actions, several per response",
}

# Gemini 2.5 Pro is the only model with repeat runs, on three games (appendix D.3).
VARIANCE_NOTE = {
    ("kirby", "gemini25pro"): " Five repeat runs reached the first checkpoint in four, "
                              "sample variance 0.2.",
    ("doom2", "gemini25pro"): " Five repeat runs all scored zero checkpoints.",
    ("tim", "gemini25pro"): " Five repeat runs all scored zero checkpoints.",
}

# CSV free-text fields are held at or under the reference dataset's own maxima: notes 586,
# task_description 560, performance_evidence 337, source_record 455.  Everything that does not
# fit those limits lives in research/videogamebench.md, which compute_source and
# human_time_source point at.
FIELD_LIMITS = {"notes": 586, "task_description": 560, "performance_evidence": 337,
                "source_record": 455, "compute_source": 220, "human_time_source": 205}


def format_number(x):
    """Exact value of the documented calculation, as the dataset records derived values."""
    return repr(float(x))


def build_points_rows(inp, results, walk):
    rows = []
    for g in GAME_ORDER:
        wt = walk["games"][inp["games"][g]["walkthrough_key"]]
        for m in MODEL_ORDER:
            r = results[g][m]["central"]
            mod = inp["models"][m]
            gm = inp["games"][g]
            prog = inp["exact_progress_pct"][g][m]
            chk = inp["checkpoint_score_pct"][g][m]
            endpoint = prog / 100.0 * wt["length_seconds"]
            emu = gm["emulator"]

            desc = (
                "One VG-Agent run of %s in real time, to completion (%s). Input is the raw frame "
                "plus a text statement of objective and controls; output is one action per step, in "
                "a ReAct loop with a rolling %d-message context of recent frames and a written "
                "memory. %s. The emulator runs on while the model thinks; game-state reads, overlays "
                "and guides are barred. The run stopped early unfinished; human time is one recorded "
                "expert longplay to the same criterion."
            ) % (gm["name"], COMPLETION[g], mod["context_messages"], PLATFORM[emu])

            perf = (
                "Criterion is completing the game. The run reached %.2f%% of the walkthrough and "
                "scored %s%% on the benchmark's checkpoint scale; it did not finish, while the "
                "human recording does. One run per model per game was funded.%s"
            ) % (prog, ("%.2f" % chk).rstrip("0").rstrip("."),
                 VARIANCE_NOTE.get((g, m), ""))

            low_mult = inp["parameter_sensitivity"]["low_multiplier"]
            high_mult = inp["parameter_sensitivity"]["high_multiplier"]
            estimated = m in inp["parameter_sensitivity"]["estimated_models"]
            notes = (
                "Workload inverted from this run's $%.2f at %.2f/%.2f USD per million input/output "
                "tokens, the rate the harness applied: %.0f calls, %.3g processed positions; "
                "scenarios %.3g-%.3g FLOPs%s. Image billing units count as positions, not tokens. %s"
            ) % (
                r["run_cost_usd"], r["price_in_per_token"] * 1e6, r["price_out_per_token"] * 1e6,
                r["implied_requests"], r["processed_positions_total"],
                results[g][m]["_flops_min"], results[g][m]["_flops_max"],
                (", 30-300B prior %.3g-%.3g"
                 % (results[g][m]["_flops_min"] * low_mult,
                    results[g][m]["_flops_max"] * high_mult)) if estimated else "",
                ("Furthest state %.0f s into the %d s longplay."
                 % (endpoint, wt["length_seconds"])) if prog > 0 else
                ("Progress is 0.00%% of the %d s longplay; the paper states a zero score does not "
                 "mean no progress." % wt["length_seconds"]),
            )
            extra = []
            if m == "llama4mav":
                extra.append("The cost is the harness's own accounting at a fallback rate reached "
                             "through a lookup bug, not an invoice; the two rates that could have "
                             "applied instead give about a third of this.")
            if m == "gemini25pro":
                extra.append("Central charges 700 thinking tokens per call, always generated and "
                             "inside the priced counter. Google repointed preview-03-25 to the 05-06 "
                             "checkpoint mid-window, so which checkpoint ran is unresolved.")
            if r["run_cost_usd"] < 0.10:
                extra.append("The published cost carries one significant figure.")
            if g == "civ1":
                extra.append("The paper calls this game's progress estimate very noisy.")
            if extra:
                notes = notes + " " + " ".join(extra)

            rows.append({
                "point_id": point_id(g, m),
                "task": TASK_NAME[g],
                "task_category": "games",
                "task_description": desc,
                "model_id": mod["model_id"],
                "compute_scope": "inference",
                "compute_flops": format_number(r["compute_flops"]),
                "human_skill": "expert",
                "human_time_scope": "task_performance",
                "human_time": "%d" % wt["length_seconds"],
                "performance_vs_human": "below",
                "comparison_issues": "different_inputs_or_tools; different_attempt_selection",
                "compute_evidence": "derived_assumed_inputs",
                "human_time_evidence": "task_timings",
                "performance_evidence": perf,
                "human_time_statistic": "point_estimate",
                "human_time_subset": "successful",
                "human_attempts": "1",
                "human_time_source": "%s; research/videogamebench.md#human-baseline" % wt["url"],
                "human_time_method": "reported",
                "compute_method": "operation_count",
                "compute_statistic": "total",
                "compute_subset": "all",
                "ai_attempts": "1",
                "compute_source": "research/videogamebench.md#compute",
                "tokens": format_number(r["text_tokens_total"]),
                "tokens_accounting": "input_output",
                "source_dataset": "VideoGameBench (Zhang et al., 2025)",
                "source_record": (
                    "arXiv:2505.18134v3 Table 8 (cost) and Table 7 (walkthrough); model %s; "
                    "harness github.com/alexzhang13/videogamebench commit "
                    "faab53179cb4babdd102f35cb83c24a5f2c29d05, all_experiments.sh; walkthrough %s; "
                    "performance: arXiv:2505.18134v3 Tables 2 and 10."
                ) % (mod["paper_revision"], wt["url"]),
                "notes": notes,
            })
    over = [(r["point_id"], k, len(r[k])) for r in rows for k, lim in FIELD_LIMITS.items()
            if len(r[k]) > lim]
    if over:
        raise SystemExit("free-text fields over the dataset's maxima: %s" % over[:5])
    return rows


# --------------------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--inputs", required=True)
    ap.add_argument("--walkthroughs", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--points-out")
    ap.add_argument("--models-out")
    ap.add_argument("--shared-models", default=BALROG_MODELS_CSV,
                    help="CSV holding the shared model records this batch reuses verbatim")
    args = ap.parse_args()

    shared_model_rows = load_shared_model_rows(args.shared_models)

    with open(args.inputs) as f:
        inp = json.load(f)
    with open(args.walkthroughs) as f:
        walk = json.load(f)

    central = inp["central"]
    results = {}
    for g in GAME_ORDER:
        results[g] = {}
        for m in MODEL_ORDER:
            per_scen = {"central": evaluate(inp, g, m, central)}
            for name, override in inp["scenarios"].items():
                per_scen[name] = evaluate(inp, g, m, merged(central, override))
            # The headline range covers workload uncertainty only. "images_not_positions"
            # is a stated accounting convention rather than an uncertainty, so it is kept
            # out of the min/max and reported separately.
            flops = [v["compute_flops"] for k, v in per_scen.items()
                     if k != "images_not_positions"]
            per_scen["_flops_min"] = min(flops)
            per_scen["_flops_max"] = max(flops)
            results[g][m] = per_scen

    walk_table = {}
    for g in GAME_ORDER:
        w = walk["games"][inp["games"][g]["walkthrough_key"]]
        walk_table[g] = {
            "walkthrough_seconds": w["length_seconds"],
            "video": w["url"],
            "channel": w["channel"],
            "endpoint_seconds_by_model": {
                m: round(inp["exact_progress_pct"][g][m] / 100.0 * w["length_seconds"], 2)
                for m in MODEL_ORDER
            },
        }

    out = {
        "_about": "Generated by research/videogamebench/compute_videogamebench.py. "
                  "compute_flops uses the central scenario; every scenario is retained per row.",
        "central_parameters": central,
        "scenario_definitions": inp["scenarios"],
        "human_baseline": walk_table,
        "rows": {},
    }
    for g in GAME_ORDER:
        for m in MODEL_ORDER:
            pid = point_id(g, m)
            r = results[g][m]
            out["rows"][pid] = {
                "game": g, "model": m, "model_id": inp["models"][m]["model_id"],
                "central": r["central"],
                "flops_min_over_scenarios": r["_flops_min"],
                "flops_max_over_scenarios": r["_flops_max"],
                "flops_by_scenario": {k: v["compute_flops"] for k, v in r.items()
                                      if not k.startswith("_")},
                "requests_by_scenario": {k: v["implied_requests"] for k, v in r.items()
                                         if not k.startswith("_")},
                "human_time_seconds": walk_table[g]["walkthrough_seconds"],
                "exact_progress_pct": inp["exact_progress_pct"][g][m],
                "endpoint_seconds_in_walkthrough": walk_table[g]["endpoint_seconds_by_model"][m],
                "flops_text_positions_only": r["images_not_positions"]["compute_flops"],
                "flops_per_human_second": r["central"]["compute_flops"] / walk_table[g]["walkthrough_seconds"],
            }

    with open(args.out, "w") as f:
        json.dump(out, f, indent=2, sort_keys=False)
        f.write("\n")

    if args.points_out:
        rows = build_points_rows(inp, results, walk)
        d = os.path.dirname(args.points_out)
        if d:
            os.makedirs(d, exist_ok=True)
        with open(args.points_out, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=POINTS_HEADER)
            w.writeheader()
            for row in rows:
                w.writerow(row)

    if args.models_out:
        d = os.path.dirname(args.models_out)
        if d:
            os.makedirs(d, exist_ok=True)
        with open(args.models_out, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=MODELS_HEADER)
            w.writeheader()
            for row in shared_model_rows:
                w.writerow(row)

    print("wrote %s" % args.out)
    if args.points_out:
        print("wrote %s (%d rows)" % (args.points_out, len(GAME_ORDER) * len(MODEL_ORDER)))
    if args.models_out:
        print("wrote %s (%d rows)" % (args.models_out, len(shared_model_rows)))


if __name__ == "__main__":
    main()
