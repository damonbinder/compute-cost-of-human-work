#!/usr/bin/env python3
"""Reproduce the compute figures for point game-portal-gpt6astra.

Inputs are the two retained evidence files; nothing is read from a temporary
directory or from the candidate folder layout.

Usage:
  python3 compute_portal_astra.py \
      --summary  agent-work/sources/portal-astra/summary.json \
      --scan     agent-work/sources/portal-astra/session-scan.json \
      --out      calculations.json

Dependencies: Python 3.9+ standard library.

Assumptions carried here are stated in research/portal-astra.md. The two that
set the central value: 300B active parameters (6e11 FLOPs per processed
position, ruled 2026-09-13; sensitivity 100-600B), and one backbone position per
32x32 image patch. A third, cached-
context attention, is omitted from the central value by dataset convention and
priced in the scenarios; for this row it is larger than the central value.
"""
import argparse
import json
import math

FLOPS_PER_POSITION = 6e11          # 2 * 300e9 active parameters
ACTIVE_PARAMETERS = 300e9
# Ruled 2026-09-13: research/model-priors/accepted-priors.csv, gpt-6-astra at 300B
# active, sensitivity 100-600B. Basis is inference economics plus a price ratio,
# both of which respond to FLOPs per emitted token, so any recurrent-depth loop
# multiplier is already inside the prior rather than additive on top of it.

# gpt-6-astra image accounting, OpenAI "Images and vision" guide.
PATCH = 32
ASTRA_BILLING_MULTIPLIER = 1.2
FULL_RES = (1280, 720)             # principal point (640, 360) in the agent's own helper
DEFAULT_RES = (640, 360)           # controller fit360p() of a 1280x720 backbuffer

# OpenAI list prices per million tokens for gpt-6-astra, used only as a cross-check.
PRICE_INPUT = 10.0
PRICE_CACHED_INPUT = 1.0
PRICE_OUTPUT = 50.0

# Cached-context attention, omitted from compute_flops by dataset convention.
# Recipe and the two-operations-per-multiply-add convention follow
# dataset/research/ruler/ruler.md: 4 * L * d_model * N_context per appended
# position, counting QK and attention-value multiplication.
CONTEXT_POSITIONS = 130_000        # overlay reads CONTEXT 130.0k / 258.4k
ATTENTION_SHAPES = [
    ("L=64, d=8192", 64, 8192),
    ("L=80, d=10240", 80, 10240),
    ("L=96, d=12288", 96, 12288),
]


def patches(width, height):
    return math.ceil(width / PATCH) * math.ceil(height / PATCH)


def billable(width, height):
    return math.ceil(patches(width, height) * ASTRA_BILLING_MULTIPLIER)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", required=True)
    ap.add_argument("--scan", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    summary = json.load(open(args.summary, encoding="utf-8"))
    scan = json.load(open(args.scan, encoding="utf-8"))

    usage = summary["last_reported_thread_token_usage"]
    reported_input = usage["input_tokens"]
    cached_input = usage["cached_input_tokens"]
    cache_write = usage["cache_write_input_tokens"]
    output = usage["output_tokens"]
    reasoning = usage["reasoning_output_tokens"]

    # evidence/README.md: "Cached input is included in input-token counts;
    # reasoning output is included in output-token counts." OpenAI's prompt-
    # caching guide partitions input_tokens into ordinary, cached and
    # cache-write tokens, all one forward pass each, so subtracting the cache
    # reads already leaves every newly processed input token. cache_write is
    # reported for completeness and deliberately NOT added: doing so would
    # double-count a non-zero counter.
    fresh_input = reported_input - cached_input
    charged_units = fresh_input + output

    n_full = scan["images_by_resolution_request"]["full_res"]
    n_default = scan["images_by_resolution_request"]["default_360p"]

    image_billing = n_full * billable(*FULL_RES) + n_default * billable(*DEFAULT_RES)
    image_positions = n_full * patches(*FULL_RES) + n_default * patches(*DEFAULT_RES)

    text_tokens = charged_units - image_billing
    backbone_positions = text_tokens + image_positions
    flops = FLOPS_PER_POSITION * backbone_positions

    cost = (fresh_input * PRICE_INPUT + cached_input * PRICE_CACHED_INPUT
            + output * PRICE_OUTPUT) / 1e6

    # Corroborating decomposition of the non-image share of fresh input.
    tok = scan.get("o200k_base_tokens") or {}
    measured_text_in_log = tok.get("tool_result_text")
    fresh_text = text_tokens - output
    residual = None
    if measured_text_in_log is not None:
        residual = fresh_text - measured_text_in_log

    attention = {}
    for label, layers, d_model in ATTENTION_SHAPES:
        per_position = 4 * layers * d_model * CONTEXT_POSITIONS
        total = per_position * backbone_positions
        attention[label] = {
            "layers": layers,
            "d_model": d_model,
            "four_L_d": 4 * layers * d_model,
            "flops_per_appended_position": per_position,
            "attention_flops": total,
            "ratio_to_compute_flops": total / flops,
            "operation_count_including_attention": flops + total,
        }

    scenarios = {
        "active_parameters_100B": 2 * 100e9 * backbone_positions,
        "active_parameters_600B": 2 * 600e9 * backbone_positions,
        "billing_units_charged_as_positions": FLOPS_PER_POSITION * charged_units,
        "image_tokens_additional_to_reported_input": FLOPS_PER_POSITION * (
            charged_units + image_positions),
        "full_prefix_no_cache_exclusion": FLOPS_PER_POSITION * (
            reported_input + output - image_billing + image_positions),
        # Not additive on top of the central value: the serving-economics prior
        # behind 300B active already absorbs a loop multiplier. Retained to show
        # what an explicit pass count would do to a parameter-only coefficient.
        "recurrent_depth_two_passes": 2 * flops,
        "recurrent_depth_four_passes": 4 * flops,
        "plus_cached_context_attention_L64_d8192":
            attention["L=64, d=8192"]["operation_count_including_attention"],
        "plus_cached_context_attention_L96_d12288":
            attention["L=96, d=12288"]["operation_count_including_attention"],
    }

    result = {
        "point_id": "game-portal-gpt6astra",
        "reported_counters": {
            "input_tokens_including_cache_reads": reported_input,
            "cached_input_tokens": cached_input,
            "cache_write_input_tokens": cache_write,
            "output_tokens_including_reasoning": output,
            "reasoning_output_tokens": reasoning,
            "total_tokens": usage["total_tokens"],
            "elapsed_to_completion_seconds": summary["elapsed_to_completion_seconds"],
            "model": summary["models"][0],
        },
        "derived": {
            "fresh_input_tokens": fresh_input,
            "charged_units": charged_units,
            "tokens_accounting_category": "input_cache_creation_output",
            "charged_units_formula": "(input_tokens - cached_input_tokens) + output_tokens",
            "cache_write_treatment": (
                "reported zero; under OpenAI's partition cache-write tokens sit inside "
                "input_tokens and are one forward pass, so they are already inside fresh "
                "input and are not added again"),
            "images_full_res_1280x720": n_full,
            "images_default_640x360": n_default,
            "image_text_echoes_excluded": scan.get("image_text_echoes"),
            "deferred_results_attributed_to_originating_cell": len(
                scan.get("deferred_results_resolved") or []),
            "billable_tokens_per_full_res_image": billable(*FULL_RES),
            "billable_tokens_per_default_image": billable(*DEFAULT_RES),
            "patches_per_full_res_image": patches(*FULL_RES),
            "patches_per_default_image": patches(*DEFAULT_RES),
            "image_billing_units": image_billing,
            "image_backbone_positions": image_positions,
            "text_tokens": text_tokens,
            "fresh_input_text_tokens": fresh_text,
            "backbone_positions": backbone_positions,
        },
        "compute_flops": flops,
        "flops_per_position": FLOPS_PER_POSITION,
        "active_parameters": ACTIVE_PARAMETERS,
        "omitted_cached_context_attention": {
            "note": (
                "Not included in compute_flops. The 2 * active_parameters coefficient is a "
                "dataset-wide convention that omits attention; for this row the omitted term "
                "is larger than the recorded value, and the omission is one-sided."),
            "recipe": "4 * layers * d_model * context_positions per appended position",
            "recipe_source": "dataset/research/ruler/ruler.md",
            "context_positions": CONTEXT_POSITIONS,
            "appended_positions": backbone_positions,
            "shapes": attention,
        },
        "cross_checks": {
            "list_price_cost_usd": round(cost, 2),
            "overlay_reported_cost_usd": 571.33,
            "session_log_image_blocks": scan["images_total"],
            "session_log_image_blocks_plus_text_echoes": scan.get("images_plus_echoes"),
            "summary_removed_images": summary["removed_images"],
            "tool_result_text_tokens_o200k": measured_text_in_log,
            "fresh_input_text_not_from_tool_results": residual,
            "in_game_ticks_visible_in_log": scan["tick_sum"],
            "in_game_seconds_visible_in_log": round(scan["tick_sum"] / 67, 1),
            "overlay_in_game_timer_seconds": 6817.42,
        },
        "scenarios": scenarios,
    }

    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=1)
        handle.write("\n")
    print(json.dumps(result, indent=1))


if __name__ == "__main__":
    main()
