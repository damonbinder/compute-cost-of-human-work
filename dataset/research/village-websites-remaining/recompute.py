#!/usr/bin/env python3
"""Reconstruct one original Village website episode. Requires tiktoken.

Inputs are read-only; --output-dir must not exist. Native usage and inferred
image/consolidation/helper components remain separate in the resulting JSON.
"""
import argparse
import copy
import hashlib
import json
import math
import re
import statistics
from collections import Counter
from datetime import datetime
from pathlib import Path

import tiktoken


def timestamp(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def full_input(usage):
    return sum(usage.get(k, 0) for k in
               ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))


def gui(turn):
    names = [c.get("name") for c in turn["agentMessage"].get("content", [])]
    return "computer" in names


def git_blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def calculate(source, cfg):
    enc = tiktoken.get_encoding(cfg["summary_tokenizer"])
    tok = lambda text: len(enc.encode(text or "", disallowed_special=()))
    raw = json.loads((source / "village/claude37-selected-sessions.json").read_text())
    sessions = {s["id"]: s for s in raw["sessions"]}
    events = json.loads((source / "village/events-2025-10-13.json").read_text())["events"]
    event_by_id = {e["id"]: e for e in events}
    selected_events = [event_by_id[i] for i in cfg["event_ids"]]
    image_units = cfg.get("image_units", cfg["screenshot_width"] * cfg["screenshot_height"] / cfg["image_area_per_unit"])
    tail = cfg["image_tail_tokens"]
    summary_scale = cfg.get("summary_input_scale", 1)
    calls, per_session, summaries, increments, known_ids, all_turns = [], [], [], [], set(), {}
    synthetic = 0
    for sid in cfg["session_ids"]:
        s = sessions[sid]
        turns, prior_C, intervals = [], 0, []
        all_turns.update({t["id"]: t for t in s["turns"]})
        for t in s["turns"]:
            m = t["agentMessage"]
            u = m["usage"]
            if m["id"] == "msg_00000000000000000000000000000000":
                assert full_input(u) + u["output_tokens"] == 0
                synthetic += 1
                continue
            assert m["model"] == cfg["native_model"]
            assert m["id"] not in known_ids
            known_ids.add(m["id"])
            C, R = full_input(u), u.get("cache_read_input_tokens", 0)
            assert C >= prior_C, (sid, t["id"], C, prior_C)
            # Initial screen and GUI results enter the next model request.
            inserted = not turns or gui(turns[-1])
            if inserted:
                # Exact historical serialization is absent. Put the image at
                # the end of the added suffix before a small text reminder.
                end = C - tail
                start = max(prior_C, end - image_units)
                assert 0 <= start < end <= C
                intervals.append((start, end))
                if turns:
                    increments.append(C - prior_C - turns[-1]["agentMessage"]["usage"]["output_tokens"])
            image_fresh = sum(max(0, end - max(start, R)) for start, end in intervals)
            fresh_input = u["input_tokens"] + u.get("cache_creation_input_tokens", 0)
            assert 0 <= image_fresh <= fresh_input
            calls.append({"session_id": sid, "turn_id": t["id"], "message_id": m["id"],
                          "created_at": t["createdAt"], "full_input": C,
                          "input": u["input_tokens"], "cache_creation": u.get("cache_creation_input_tokens", 0),
                          "cache_read": R, "output_including_thinking": u["output_tokens"],
                          "inserted_screenshot": inserted, "fresh_image_units_estimate": image_fresh,
                          "fresh_text_input_estimate": fresh_input - image_fresh})
            prior_C = C
            turns.append(t)
        native = Counter()
        for c in calls:
            if c["session_id"] == sid:
                for k in ("input", "cache_creation", "cache_read", "output_including_thinking", "fresh_image_units_estimate"):
                    native[k] += c[k]
        stop = min((e for e in selected_events if e["data"].get("actionType") == "STOP_USING_COMPUTER"
                    and e["createdAt"] > turns[-1]["createdAt"]), key=lambda e: e["createdAt"])
        last = turns[-1]
        # A summary is separately visible but its usage is not. Approximate
        # its input by the final retained context plus last response/result.
        extra_result = image_units if gui(last) else tok((last.get("output") or "") + (last.get("error") or ""))
        summary_input = prior_C + last["agentMessage"]["usage"]["output_tokens"] + extra_result + cfg["summary_tool_wrapper_tokens"]
        summary_images = sum(end - start for start, end in intervals) + (image_units if gui(last) else 0)
        summary = {"session_id": sid, "stop_event_id": stop["id"],
                   "input_combined_estimate": summary_input * summary_scale,
                   "image_units_estimate": summary_images * summary_scale,
                   "output_text_tokens_proxy": tok(stop["data"]["summary"]),
                   "input_before_scale": summary_input}
        summaries.append(summary)
        per_session.append({"session_id": sid, "native_calls": len(turns), "native": dict(native),
                            "estimated_inserted_images": len(intervals), "summary": summary})

    # One computer chat response also appears in the event stream. A controller
    # response can create START/WAIT and TALK records with the same usage.
    # Match exact usage, timing and action type instead of deduplicating text.
    native_chat = [t for t in all_turns.values() if t["agentAction"].get("action") == "send_message_back_to_chat"]
    controllers, dedup = [], []
    for e in sorted(selected_events, key=lambda e: e["eventIndex"]):
        d, mirror = e["data"], None
        assert d.get("agentId", d.get("speakerId")) == cfg["agent_id"]
        if d["actionType"] == "AGENT_TALK":
            for t in native_chat:
                u = t["agentMessage"]["usage"]
                if (u["input_tokens"], u["output_tokens"]) == (d["inputTokens"], d["outputTokens"]) and abs(timestamp(t["createdAt"]) - timestamp(e["createdAt"])) < 2:
                    assert t["agentAction"]["content"] == d["content"]
                    mirror = t["id"]
            for prior in controllers:
                if prior["action_type"] in ("START_USING_COMPUTER", "WAIT") and (prior["input"], prior["output"]) == (d["inputTokens"], d["outputTokens"]) and abs(timestamp(prior["created_at"]) - timestamp(e["createdAt"])) < 1.1:
                    mirror = prior["event_id"]
        if mirror:
            dedup.append({"event_id": e["id"], "event_index": e["eventIndex"], "same_response_as": mirror})
        else:
            controllers.append({"event_id": e["id"], "event_index": e["eventIndex"],
                                "created_at": e["createdAt"], "action_type": d["actionType"],
                                "input": d["inputTokens"], "output": d["outputTokens"]})

    helper_observed = []
    for p in sorted((source / "helpers").glob("*.stderr.txt")):
        text = p.read_text()
        assert "gpt-5-codex" in text and "0.46.0" in text
        counts = re.findall(r"tokens used\s*\n([\d,]+)", text)
        assert len(counts) == 1
        turn_id = p.name.split(".")[0]
        assert text == all_turns[turn_id]["error"]
        helper_observed.append({"turn_id": turn_id, "file": str(p.relative_to(source)), "tokens": int(counts[0].replace(",", "")), "basis": "native stderr blended_total"})
    for c in cfg["helper_screenshot_counters"]:
        assert c["turn_id"] in all_turns and (source / c["path"]).exists()
        helper_observed.append({**c, "basis": "native terminal counter, manually read screenshot"})
    helper_observed_total = sum(c["tokens"] for c in helper_observed)
    helper_missing = sum(c[cfg.get("missing_helper_case", "tokens")] for c in cfg["missing_helpers"])
    assert "previous bash command timed out" in all_turns["01367a61-49d0-4e6d-94cd-555e42a59c58"]["error"]

    vc = json.loads((source / "models/clip-vit-large-patch14-336.json").read_text())["vision_config"]
    h, m, layers, patch, size = (vc[k] for k in ("hidden_size", "intermediate_size", "num_hidden_layers", "patch_size", "image_size"))
    patches = (size // patch) ** 2
    S = patches + 1
    clip_flops = 2 * patches * patch ** 2 * vc["num_channels"] * h + layers * (8 * S * h ** 2 + 4 * S * h * m + 4 * S ** 2 * h) + 2 * h * vc["projection_dim"]
    native_combined = sum(c["input"] + c["cache_creation"] + c["output_including_thinking"] for c in calls)
    native_read = sum(c["cache_read"] for c in calls)
    controller_input = sum(e["input"] for e in controllers)
    controller_total = controller_input * cfg.get("controller_input_scale", 1) + sum(e["output"] for e in controllers)
    summary_total = sum(s["input_combined_estimate"] + s["output_text_tokens_proxy"] for s in summaries)
    fresh_images = sum(c["fresh_image_units_estimate"] for c in calls) + sum(s["image_units_estimate"] for s in summaries)
    primary_combined = native_combined + controller_total + summary_total
    helper_total = helper_observed_total + helper_missing
    text_total = primary_combined - fresh_images + helper_total
    visual_multiplier = cfg.get("visual_backbone_multiplier", 1)
    size_scale = cfg.get("model_size_scale", 1)
    primary_flops = 2 * cfg["primary_active_parameters"] * size_scale * (primary_combined + (visual_multiplier - 1) * fresh_images)
    helper_flops = 2 * cfg["helper_active_parameters"] * size_scale * helper_total
    frontend_flops = fresh_images / image_units * cfg["vision_crops"] * clip_flops
    # Audit artifact version against original native git-diff end hashes.
    expected = {"deployed-index.html": "e4483256a8c8d732bdfe0ea58b058c4a0cac4be5", "deployed-styles.css": "c08b6716324292487e76d20dd10108e5359ed030", "original-created-projects.html": "bcee2f99b5cbcf9f8575119a71db188e2efbba6a"}
    artifact_check = {}
    for filename, sha in expected.items():
        data = (source / "artifacts" / filename).read_bytes()
        assert git_blob(data) == sha
        assert any(sha in p.read_text() for p in (source / "helpers").glob("*.stderr.txt"))
        artifact_check[filename] = {"bytes": len(data), "git_blob_sha1": sha}
    total_flops = primary_flops + helper_flops + frontend_flops
    return {"point_id": cfg["point_id"], "compute_flops": total_flops, "tokens": text_total,
            "human_time_seconds": 60 * sum(x["minutes"] for x in cfg["human_minutes"]),
            "native_combined_fresh_positions": native_combined, "native_cache_read_positions_excluded": native_read,
            "controller_input_native": controller_input, "controller_total_assuming_no_unreported_cache_creation": controller_total,
            "consolidation_combined_estimate": summary_total, "helper_observed_fresh_tokens": helper_observed_total,
            "helper_missing_estimate": helper_missing, "helper_total": helper_total,
            "primary_combined_positions": primary_combined, "fresh_image_units_estimate": fresh_images,
            "fresh_primary_text_tokens_estimate": primary_combined - fresh_images,
            "primary_flops": primary_flops, "helper_flops": helper_flops, "vision_frontend_flops": frontend_flops,
            "clip_flops_per_336px_crop": clip_flops, "image_units_per_screenshot_estimate": image_units,
            "full_native_prefix_alternative_flops": total_flops + 2 * cfg["primary_active_parameters"] * size_scale * native_read,
            "native_calls": len(calls), "synthetic_turns_excluded": synthetic,
            "controller_response_count": len(controllers), "mirrored_events_excluded": dedup,
            "gui_context_growth_minus_previous_output": {"n": len(increments), "min": min(increments), "median": statistics.median(increments), "max": max(increments)},
            "sessions": per_session, "calls": calls, "controllers": controllers,
            "helpers_observed": helper_observed, "artifacts": artifact_check}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source-dir", required=True, type=Path)
    p.add_argument("--selection", required=True, type=Path)
    p.add_argument("--output-dir", required=True, type=Path)
    args = p.parse_args()
    if args.output_dir.exists():
        p.error("output directory already exists; choose a new directory")
    cfg = json.loads(args.selection.read_text())
    result = calculate(args.source_dir, cfg)
    cases = {
        "missing_helpers_low": {"missing_helper_case": "low"},
        "missing_helpers_high": {"missing_helper_case": "high"},
        "no_additional_consolidation_input": {"summary_input_scale": 0},
        "double_consolidation_input": {"summary_input_scale": 2},
        "controller_input_half": {"controller_input_scale": .5},
        "controller_input_double": {"controller_input_scale": 2},
        "image_750_units": {"image_units": 750},
        "image_1250_units": {"image_units": 1250},
        "later_28px_rule_sensitivity_only": {"image_units": math.ceil(1024 / 28) * math.ceil(768 / 28)},
        "image_tail_zero": {"image_tail_tokens": 0},
        "image_tail_256": {"image_tail_tokens": 256},
        "one_encoder_crop": {"vision_crops": 1},
        "twenty_four_encoder_crops": {"vision_crops": 24},
        "visual_backbone_half": {"visual_backbone_multiplier": .5},
        "visual_backbone_double": {"visual_backbone_multiplier": 2},
        "model_size_half": {"model_size_scale": .5},
        "model_size_double": {"model_size_scale": 2},
    }
    result["sensitivity"] = {}
    for name, override in cases.items():
        c = copy.deepcopy(cfg)
        c.update(override)
        alt = calculate(args.source_dir, c)
        result["sensitivity"][name] = {k: alt[k] for k in ("compute_flops", "tokens", "fresh_image_units_estimate", "helper_missing_estimate", "consolidation_combined_estimate")}
    result["human_sensitivity_seconds"] = [60 * cfg["human_minutes_low"], 60 * cfg["human_minutes_high"]]
    args.output_dir.mkdir(parents=True, exist_ok=False)
    (args.output_dir / "calculations.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in ("point_id", "compute_flops", "tokens", "human_time_seconds", "native_calls", "controller_response_count", "helper_total")}))


if __name__ == "__main__":
    main()
