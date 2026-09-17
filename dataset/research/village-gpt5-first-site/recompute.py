#!/usr/bin/env python3
"""Reconstruct the selected original GPT-5 website episode; requires tiktoken.

Read-only sources. Explicit paths; the output directory must not exist.
No API calls, remote tokenizer downloads, or model inference.
"""
import argparse
import base64
import copy
import hashlib
import json
import math
import statistics
from collections import Counter
from datetime import datetime
from pathlib import Path

import tiktoken


def load_encoding(source):
    definition = json.loads((source / "tokenizer/definition.json").read_text())
    ranks = {}
    for line in (source / "tokenizer/o200k_base.tiktoken").read_bytes().splitlines():
        token, rank = line.split()
        ranks[base64.b64decode(token)] = int(rank)
    return tiktoken.Encoding(name="retained_o200k", pat_str=definition["pat_str"],
                             mergeable_ranks=ranks,
                             special_tokens=definition["special_tokens"])


def visible_counts(turn, tok, overhead):
    visible, summary, reasoning = 0, 0, False
    for item in turn["agentMessage"]:
        if item["type"] == "function_call":
            visible += tok(item["name"]) + tok(item["arguments"]) + overhead
        elif item["type"] == "message":
            visible += sum(tok(c.get("text", "")) for c in item["content"]) + overhead / 2
        elif item["type"] == "reasoning":
            reasoning = True
            summary += sum(tok(c["text"]) for c in item["summary"])
        else:
            raise AssertionError(item["type"])
    return visible, summary, reasoning


def gui(turn):
    return any(i.get("name") == "use_computer" for i in turn["agentMessage"])


def time_seconds(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


def interpolate(anchors, increments):
    """Apportion observed context growth using retained intervening work."""
    out = dict(anchors)
    positions = sorted(anchors)
    for lo, hi in zip(positions, positions[1:]):
        growth = anchors[hi] - anchors[lo]
        assert growth >= 0, (lo, hi, growth)
        weight = sum(increments[lo:hi])
        assert weight > 0
        cum = 0
        for j in range(lo + 1, hi):
            cum += increments[j - 1]
            out[j] = anchors[lo] + growth * cum / weight
    return out


def calculate(source, cfg):
    enc = load_encoding(source)
    tok = lambda s: len(enc.encode(s or "", disallowed_special=()))
    raw = json.loads((source / "sessions.json").read_text())
    sessions = raw["sessions"]
    assert [s["id"] for s in sessions] == cfg["session_ids"]
    events = sorted(json.loads((source / "events.json").read_text())["events"],
                    key=lambda e: e["eventIndex"])
    assert len(events) == 72
    assert {e["data"].get("agentId", e["data"].get("speakerId")) for e in events} == {cfg["agent_id"]}
    turns = [t for s in sessions for t in s["turns"]]
    assert len(turns) == len({t["id"] for t in turns}) == 186
    assert len({json.dumps(t["agentMessage"], sort_keys=True) for t in turns}) == 186
    assert all(s["agent"]["modelString"] == cfg["native_model"] for s in sessions)
    chat_events, anchored, counts, ratios, empty_residual = {}, {}, {}, [], []
    for t in turns:
        counts[t["id"]] = visible_counts(t, tok, cfg["function_framing_tokens"])
        action = t["agentAction"] or {}
        if action.get("action") == "send_message_back_to_chat":
            matches = [e for e in events if e["data"].get("content") == action["content"]]
            assert len(matches) == 1
            event = matches[0]
            chat_events[event["id"]] = t["id"]
            anchored[t["id"]] = event
            visible, summary, reasoning = counts[t["id"]]
            assert reasoning
            residual = event["data"]["outputTokens"] - visible
            assert residual > 0
            (ratios if summary else empty_residual).append((residual, summary))
    assert len(anchored) == 57
    ratio = sum(x[0] for x in ratios) / sum(x[1] for x in ratios)
    empty_mean = statistics.mean(x[0] for x in empty_residual)
    ratio *= cfg.get("reasoning_scale", 1)
    empty_mean *= cfg.get("reasoning_scale", 1)
    output = {}
    for t in turns:
        visible, summary, reasoning = counts[t["id"]]
        output[t["id"]] = (anchored[t["id"]]["data"]["outputTokens"] if t["id"] in anchored else
                           visible + (ratio * summary if summary else empty_mean if reasoning else 0))

    starts = [e for e in events if e["data"]["actionType"] == "START_USING_COMPUTER"]
    stops = [e for e in events if e["data"]["actionType"] == "STOP_USING_COMPUTER"]
    recaps = [e for e in events if e["data"]["actionType"] == "AGENT_TALK" and e["id"] not in chat_events]
    assert len(starts) == len(stops) == len(recaps) == 5
    assert all(e["data"]["summary"] == "No summary provided" for e in stops)
    first_inputs = [anchored[s["turns"][0]["id"]]["data"]["inputTokens"] for s in sessions
                    if s["turns"][0]["id"] in anchored]
    initial_estimate = statistics.mean(first_inputs) * cfg.get("unanchored_initial_scale", 1)
    image_units = cfg["image_base_tokens"] + cfg["image_tile_tokens"] * 4
    calls, per_session, validations, inserted_total, used_events = [], [], [], 0, set()
    controllers, memory = [], []
    for sn, s in enumerate(sessions):
        ts, stop = s["turns"], stops[sn]
        assert starts[sn]["createdAt"] <= ts[0]["createdAt"] < ts[-1]["createdAt"] <= stop["createdAt"] < recaps[sn]["createdAt"]
        known = {i: anchored[t["id"]]["data"]["inputTokens"] for i, t in enumerate(ts) if t["id"] in anchored}
        if 0 not in known:
            known[0] = initial_estimate
        known[len(ts)] = stop["data"]["inputTokens"]
        increments = [output[t["id"]] + tok(t.get("output")) + tok(t.get("error"))
                      + cfg["result_framing_tokens"] + (image_units if gui(t) else 0) for t in ts]
        if cfg.get("input_interpolation") == "equal_steps":
            increments = [1] * len(ts)
        C = interpolate(known, increments)
        # Leave-one-out checks use only observed interior native counters.
        for i in sorted(known):
            if i in (0, len(ts)):
                continue
            trial = dict(known)
            trial.pop(i)
            predicted = interpolate(trial, increments)[i]
            validations.append({"session_id": s["id"], "turn_id": ts[i]["id"],
                                "observed": known[i], "predicted": predicted,
                                "absolute_relative_error": abs(predicted / known[i] - 1)})
        image_intervals, session_calls = [], []
        for i in range(len(ts) + 1):
            # One initial screen and each prior GUI result. Repeated screenshot
            # presence and full history retention are explicit reconstruction assumptions.
            inserted = i == 0 or gui(ts[i - 1])
            if inserted:
                end = C[i] - cfg["image_tail_tokens"]
                image_intervals.append((end - image_units, end))
                inserted_total += 1
            cache = 0
            current_time = ts[i]["createdAt"] if i < len(ts) else stop["createdAt"]
            gap = time_seconds(current_time) - time_seconds(ts[i - 1]["createdAt"]) if i else None
            eligible = i > 0 and gap <= cfg["cache_max_gap_seconds"]
            if cfg.get("cache_case") == "static_prefix" and eligible:
                cache = min(cfg["static_prefix_tokens"], 128 * math.floor(C[i - 1] / 128))
            elif cfg.get("cache_case") == "initial_prefix" and eligible:
                cache = 128 * math.floor(C[0] / 128)
            elif cfg.get("cache_case") == "append_only" and eligible:
                cache = 128 * math.floor(C[i - 1] / 128)
            assert 0 <= cache <= C[i]
            visual = sum(max(0, b - max(a, cache)) for a, b in image_intervals)
            # Native positions constrain the total; billing visual positions
            # are a proxy for modality separation, not measured architecture.
            fresh = C[i] - cache
            assert 0 <= visual <= fresh
            t = ts[i] if i < len(ts) else None
            out = output[t["id"]] if t else stop["data"]["outputTokens"]
            call = {"session_id": s["id"], "turn_id": t["id"] if t else None,
                    "stop_event_id": None if t else stop["id"],
                    "input_combined": C[i], "input_basis": "native" if i in known and (i != 0 or t["id"] in anchored) else "estimated",
                    "output": out, "output_basis": "native" if not t or t["id"] in anchored else "estimated",
                    "cache_read_estimate": cache, "text_input_estimate": fresh - visual,
                    "image_positions_estimate": visual, "inserted_screenshot": inserted,
                    "recorded_gap_seconds": gap, "cache_timing_eligible": eligible}
            session_calls.append(call)
            if t:
                calls.append(call)
            else:
                controllers.append({**call, "event_id": stop["id"], "action_type": "STOP_USING_COMPUTER"})
                used_events.add(stop["id"])
        per_session.append({"session_id": s["id"], "calls": len(ts),
                            "native_anchors": sum(t["id"] in anchored for t in ts),
                            "full_input_sum": sum(c["input_combined"] for c in session_calls[:-1]),
                            "output_sum": sum(c["output"] for c in session_calls[:-1]),
                            "gui_actions": sum(gui(t) for t in ts), "stop_input": C[len(ts)]})
        # Reset-related memory writer: source documents consolidation, but no
        # native writer response survives here. One per reset is an assumption.
        count = cfg.get("memory_calls_per_reset", 1)
        writer_input = C[len(ts)] + stop["data"]["outputTokens"] + cfg["memory_wrapper_tokens"]
        writer_output = statistics.mean(e["data"]["outputTokens"] for e in recaps)
        cache = 0
        if cfg.get("cache_case") == "static_prefix":
            cache = cfg["static_prefix_tokens"]
        elif cfg.get("cache_case") == "initial_prefix":
            cache = 128 * math.floor(C[0] / 128)
        elif cfg.get("cache_case") == "append_only":
            cache = 128 * math.floor(C[len(ts)] / 128)
        visual = sum(max(0, b - max(a, cache)) for a, b in image_intervals)
        memory.append({"session_id": s["id"], "estimated_calls": count,
                       "input_combined": count * writer_input, "output": count * writer_output,
                       "cache_read_estimate": count * cache,
                       "image_positions_estimate": count * visual,
                       "text_input_estimate": count * (writer_input - cache - visual)})
    # START and outer recap are additional native calls. In-session chats
    # already counted above must not be added from the event stream again.
    for e in starts + recaps:
        d = e["data"]
        controllers.append({"event_id": e["id"], "action_type": d["actionType"],
                            "input_combined": d["inputTokens"], "output": d["outputTokens"],
                            "cache_read_estimate": 0, "image_positions_estimate": 0,
                            "text_input_estimate": d["inputTokens"],
                            "input_basis": "native", "output_basis": "native"})
        used_events.add(e["id"])
    assert len(used_events | set(chat_events)) == len(events)
    assert not used_events & set(chat_events)
    primary = calls + controllers + memory

    helpers = []
    by_id = {t["id"]: t for t in turns}
    for entry in cfg["helper_attempts"]:
        turn = by_id[entry["turn_id"]]
        command = turn["agentAction"]["command"]
        assert command.startswith("codex exec") and entry["error_contains"] in turn["error"]
        # The intended prompt/body is retained. Malformed shell expansion means
        # it is an explicit proxy, not a recovered native helper prompt.
        payload = tok(command)
        repeats = cfg.get("helper_forward_multiplier", 1) if entry["eligible_for_processing"] else 0
        estimate = repeats * (cfg["helper_wrapper_tokens"] + 2 * payload + cfg["helper_reasoning_tokens"])
        helpers.append({"turn_id": turn["id"], "intended_command_tokens": payload,
                        "forward_multiplier": repeats, "tokens_estimate": estimate,
                        "eligible_for_processing": entry["eligible_for_processing"]})
    helper_tokens = sum(c["tokens_estimate"] for c in helpers)
    vc = json.loads((source / "models/clip-vit-large-patch14-336.json").read_text())["vision_config"]
    h, m, layers, patch, size = (vc[k] for k in ("hidden_size", "intermediate_size", "num_hidden_layers", "patch_size", "image_size"))
    patches, n = (size // patch) ** 2, (size // patch) ** 2 + 1
    clip = (2 * patches * patch ** 2 * vc["num_channels"] * h
            + layers * (8 * n * h ** 2 + 4 * n * h * m + 4 * n ** 2 * h)
            + 2 * h * vc["projection_dim"])
    visual = sum(c["image_positions_estimate"] for c in primary)
    text_primary = sum(c["text_input_estimate"] + c["output"] for c in primary)
    size_scale = cfg.get("size_scale", 1)
    primary_flops = 2 * cfg["active_parameters"] * size_scale * (text_primary + visual * cfg.get("visual_position_multiplier", 1))
    helper_flops = 2 * cfg["helper_active_parameters"] * size_scale * helper_tokens
    frontend = visual / image_units * cfg["vision_crops"] * clip * cfg.get("frontend_scale", 1)
    native_input = sum(e["data"]["inputTokens"] for e in events)
    native_output = sum(e["data"]["outputTokens"] for e in events)
    return {"point_id": cfg["point_id"], "compute_flops": primary_flops + helper_flops + frontend,
            "tokens": text_primary + helper_tokens,
            "human_time_seconds": 60 * sum(x["minutes"] for x in cfg["human_minutes"]),
            "native_counter_calls": len(events), "native_input_sum": native_input,
            "native_output_sum": native_output, "computer_calls": len(calls),
            "computer_native_anchor_calls": len(anchored), "controller_calls": len(controllers),
            "estimated_memory_calls": sum(c["estimated_calls"] for c in memory),
            "hidden_reasoning_ratio": ratio, "empty_reasoning_residual_mean": empty_mean,
            "reasoning_calibration_nonempty_n": len(ratios), "reasoning_calibration_empty_n": len(empty_residual),
            "unanchored_session_initial_input_estimate": initial_estimate,
            "input_leave_one_out_mean_absolute_relative_error": statistics.mean(x["absolute_relative_error"] for x in validations),
            "input_leave_one_out_max_absolute_relative_error": max(x["absolute_relative_error"] for x in validations),
            "native_source_combined_positions": native_input + native_output,
            "primary_text_tokens_estimate": text_primary, "image_positions_estimate": visual,
            "estimated_inserted_screenshots": inserted_total, "image_units_per_screenshot": image_units,
            "cache_read_positions_estimate": sum(c["cache_read_estimate"] for c in primary),
            "helper_tokens_estimate": helper_tokens,
            "memory_combined_estimate": sum(c["input_combined"] - c["cache_read_estimate"] + c["output"] for c in memory),
            "primary_flops": primary_flops, "helper_flops": helper_flops,
            "vision_frontend_flops": frontend, "clip_flops_per_336px_crop": clip,
            "per_session": per_session, "computer_calls_detail": calls, "controllers": controllers,
            "memory_writes": memory, "helpers": helpers, "input_leave_one_out": validations}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-dir", required=True, type=Path)
    ap.add_argument("--config", required=True, type=Path)
    ap.add_argument("--output-dir", required=True, type=Path)
    args = ap.parse_args()
    if args.output_dir.exists():
        raise SystemExit("Output directory already exists; choose a new path.")
    cfg = json.loads(args.config.read_text())
    central = calculate(args.source_dir, cfg)
    cases = []
    for scenario in cfg["scenarios"]:
        alt = copy.deepcopy(cfg)
        alt.update(scenario["changes"])
        r = calculate(args.source_dir, alt)
        cases.append({"name": scenario["name"], "changes": scenario["changes"],
                      **{k: r[k] for k in ("compute_flops", "tokens", "image_positions_estimate", "cache_read_positions_estimate")}})
    artifact_hashes = {str(p.relative_to(args.source_dir)): hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in sorted((args.source_dir / "artifacts").glob("*.png"))}
    result = {"central": central, "scenarios": cases, "source_artifact_sha256": artifact_hashes}
    args.output_dir.mkdir(parents=True, exist_ok=False)
    (args.output_dir / "calculations.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({k: central[k] for k in ("compute_flops", "tokens", "human_time_seconds")}, indent=2))


if __name__ == "__main__":
    main()
