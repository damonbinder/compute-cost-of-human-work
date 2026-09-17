#!/usr/bin/env python3
"""Operation count for the SRT-H autonomous cholecystectomy points.

Counts neural arithmetic for the two SRT-H policy levels from their published
architectures and control rates, then multiplies by each work unit's recorded
robot duration. Two FLOPs are charged per multiply-add regardless of execution
precision, following the dataset convention.

Dependencies: Python 3.9+ standard library only. No model weights, robot code
or network access. Two retained source files are read, both checked against
SHA-256 values in the recipe: the DistilBERT WordPiece vocabulary, used to
measure instruction length, and the authors' Zenodo figure archive, which
supplies the subtask durations and whose trajectory lengths are verified
against the values printed in Fig. 6C before any duration is used.

Usage (from the batch directory):

    python3 -B research/srt-h/operations.py \
        --sources agent-work/sources/srt-h \
        --recipe research/srt-h/recipe.json \
        --output /tmp/srt-h-recomputed.json

The output path must not already exist and must not sit inside the sources
directory; reproduction writes new output rather than modifying evidence.
"""

import argparse
import csv as csvmod
import hashlib
import io
import json
import math
import os
import sys
import zipfile


def read_deposit(sources, deposit, work_units):
    """Durations and trajectory lengths from the retained Zenodo archive.

    Each record is one party's kinematic trace for one subtask, sampled at the
    paper's 30 FPS with no time column, so elapsed time over n samples is
    (n-1)/30. Summing the per-sample Euclidean path of both arms reproduces the
    trajectory lengths printed in Fig. 6C, which is what ties each record to its
    panel; the check is enforced, not merely reported.
    """
    path = os.path.join(sources, deposit["archive"])
    with open(path, "rb") as handle:
        digest = hashlib.sha256(handle.read()).hexdigest()
    if digest != deposit["archive_sha256"]:
        sys.exit("Zenodo archive hash mismatch: %s" % digest)

    measured = {}
    with zipfile.ZipFile(path) as archive:
        for unit in work_units:
            if "ai_record" not in unit:
                continue
            entry = {}
            for party in ("ai", "human"):
                member = deposit["member_prefix"] + unit["%s_record" % party]
                with archive.open(member) as handle:
                    rows = list(csvmod.reader(io.TextIOWrapper(handle, "utf-8")))
                points = [[float(value) for value in row] for row in rows[1:] if row]
                length = 0.0
                for start, stop in deposit["position_columns"]:
                    for first, second in zip(points, points[1:]):
                        length += math.dist(first[start:stop], second[start:stop])
                length *= 1000.0
                published = unit["published_trajectory_length_mm"][party]
                if abs(length - published) > deposit["trajectory_length_tolerance_mm"]:
                    sys.exit("trajectory length %.4f mm does not match the published %.3f mm for %s"
                             % (length, published, member))
                entry[party] = {
                    "record": unit["%s_record" % party],
                    "samples": len(points),
                    "duration_s": (len(points) - 1) / deposit["sample_rate_hz"],
                    "duration_s_inclusive_rule": len(points) / deposit["sample_rate_hz"],
                    "trajectory_length_mm": length,
                    "published_trajectory_length_mm": published,
                }
            entry["deposit_task_index"] = unit["deposit_task_index"]
            entry["deposit_task_label"] = unit["deposit_task_label"]
            measured[unit["point_id"]] = entry
    return measured

# ----------------------------------------------------------------------------
# Counting helpers. "macs" are multiply-adds; "elem" are produced activation
# elements that attract the elementwise allowance; "soft" are attention score
# elements that attract one softmax operation each.
# ----------------------------------------------------------------------------


class Count:
    def __init__(self, macs=0, elem=0, soft=0):
        self.macs = macs
        self.elem = elem
        self.soft = soft

    def add(self, other):
        self.macs += other.macs
        self.elem += other.elem
        self.soft += other.soft
        return self

    def scaled(self, k):
        return Count(self.macs * k, self.elem * k, self.soft * k)

    def flops(self, mac_flops, elem_ops):
        return self.macs * mac_flops + self.elem * elem_ops + self.soft

    def as_dict(self, mac_flops, elem_ops):
        return {
            "multiply_adds": self.macs,
            "activation_elements": self.elem,
            "attention_score_elements": self.soft,
            "matrix_flops": self.macs * mac_flops,
            "flops": self.flops(mac_flops, elem_ops),
        }


def linear(count_in, dim_in, dim_out):
    """count_in positions through a dim_in -> dim_out projection."""
    return Count(macs=count_in * dim_in * dim_out, elem=count_in * dim_out)


# ----------------------------------------------------------------------------
# Swin-Transformer tiny
# ----------------------------------------------------------------------------


def swin_transformer(cfg, image_size):
    patch = cfg["patch_size"]
    dim = cfg["embed_dim"]
    depths = cfg["depths"]
    heads = cfg["num_heads"]
    window = cfg["window_size"]
    mlp_ratio = cfg["mlp_ratio"]

    res = image_size // patch
    total = Count()
    params = 0
    stages = []

    # Patch embedding: a patch x patch stride-patch convolution over 3 channels.
    tokens = res * res
    total.add(Count(macs=tokens * dim * (3 * patch * patch), elem=tokens * dim))
    params += 3 * patch * patch * dim + dim + 2 * dim

    channels = dim
    for stage_index, depth in enumerate(depths):
        tokens = res * res
        window_tokens = min(window * window, tokens)
        stage = Count()
        for _ in range(depth):
            block = Count()
            # qkv projection, attention output projection.
            block.add(linear(tokens, channels, 3 * channels))
            block.add(linear(tokens, channels, channels))
            # Windowed attention: query-key and attention-value products.
            block.add(Count(macs=tokens * window_tokens * channels,
                            soft=tokens * window_tokens))
            block.add(Count(macs=tokens * window_tokens * channels,
                            elem=tokens * channels))
            # Two-layer MLP with the stated expansion ratio.
            block.add(linear(tokens, channels, mlp_ratio * channels))
            block.add(linear(tokens, mlp_ratio * channels, channels))
            stage.add(block)
            params += (3 * channels * channels + 3 * channels
                       + channels * channels + channels
                       + 2 * mlp_ratio * channels * channels
                       + mlp_ratio * channels + channels
                       + 4 * channels
                       + (2 * window - 1) ** 2 * heads[stage_index])
        total.add(stage)
        stages.append({
            "stage": stage_index + 1,
            "tokens": tokens,
            "channels": channels,
            "blocks": depth,
            "multiply_adds": stage.macs,
        })
        if stage_index < len(depths) - 1:
            res //= 2
            merged_tokens = res * res
            total.add(linear(merged_tokens, 4 * channels, 2 * channels))
            params += 4 * channels * 2 * channels + 2 * (4 * channels)
            channels *= 2

    out_tokens = res * res
    params_with_head = params + channels * cfg["classifier_classes"] + cfg["classifier_classes"]
    return total, {
        "parameters_without_classifier": params,
        "parameters_with_classifier": params_with_head,
        "output_tokens": out_tokens,
        "output_width": channels,
        "stages": stages,
    }


# ----------------------------------------------------------------------------
# EfficientNet-B3
# ----------------------------------------------------------------------------


def round_filters(filters, width, divisor):
    filters *= width
    new = max(divisor, int(filters + divisor / 2) // divisor * divisor)
    if new < 0.9 * filters:
        new += divisor
    return int(new)


def round_repeats(repeats, depth):
    return int(math.ceil(depth * repeats))


def efficientnet(cfg, image_size, film_width=None):
    width = cfg["width_coefficient"]
    depth = cfg["depth_coefficient"]
    divisor = cfg["depth_divisor"]
    se_ratio = cfg["se_ratio"]

    total = Count()
    film = Count()
    params = 0
    film_params = 0

    res = math.ceil(image_size / 2)
    stem = round_filters(cfg["stem_filters"], width, divisor)
    total.add(Count(macs=res * res * stem * 3 * 3 * 3, elem=res * res * stem))
    params += 3 * 3 * 3 * stem + 2 * stem

    channels = stem
    block_records = []
    for spec in cfg["blocks"]:
        block_in = round_filters(spec["in"], width, divisor)
        block_out = round_filters(spec["out"], width, divisor)
        repeats = round_repeats(spec["repeats"], depth)
        for repeat_index in range(repeats):
            stride = spec["stride"] if repeat_index == 0 else 1
            cin = channels if repeat_index == 0 else block_out
            # Squeeze width follows the block's own input width, which the
            # reference implementation resets to the output width on repeats.
            squeeze = max(1, int((block_in if repeat_index == 0 else block_out) * se_ratio))
            res_in = res
            res_out = math.ceil(res_in / stride)
            expanded = cin * spec["expand"]
            block = Count()
            if spec["expand"] != 1:
                block.add(Count(macs=res_in * res_in * cin * expanded,
                                elem=res_in * res_in * expanded))
                params += cin * expanded + 2 * expanded
            kernel = spec["kernel"]
            block.add(Count(macs=res_out * res_out * expanded * kernel * kernel,
                            elem=res_out * res_out * expanded))
            params += expanded * kernel * kernel + 2 * expanded
            # Squeeze-and-excitation: pool to one position, two 1x1 layers,
            # then rescale the feature map.
            block.add(Count(macs=expanded * squeeze, elem=squeeze))
            block.add(Count(macs=squeeze * expanded, elem=expanded))
            block.add(Count(macs=res_out * res_out * expanded))
            params += expanded * squeeze + squeeze + squeeze * expanded + expanded
            block.add(Count(macs=res_out * res_out * expanded * block_out,
                            elem=res_out * res_out * block_out))
            params += expanded * block_out + 2 * block_out
            total.add(block)
            if film_width is not None:
                film.add(Count(macs=film_width * 2 * block_out, elem=2 * block_out))
                film.add(Count(macs=res_out * res_out * block_out))
                film_params += film_width * 2 * block_out + 2 * block_out
            block_records.append({
                "kernel": kernel,
                "stride": stride,
                "in_channels": cin,
                "expanded_channels": expanded,
                "out_channels": block_out,
                "resolution_out": res_out,
                "multiply_adds": block.macs,
            })
            res = res_out
            channels = block_out

    head = round_filters(cfg["head_filters"], width, divisor)
    total.add(Count(macs=res * res * channels * head, elem=res * res * head))
    params += channels * head + 2 * head
    params_with_classifier = params + head * cfg["classifier_classes"] + cfg["classifier_classes"]

    return total, film, {
        "parameters_without_classifier": params,
        "parameters_with_classifier": params_with_classifier,
        "film_parameters": film_params,
        "output_resolution": res,
        "output_channels": head,
        "output_tokens": res * res,
        "blocks": block_records,
    }


# ----------------------------------------------------------------------------
# WordPiece tokenizer (greedy longest-match-first, lowercased, no accents in
# the instruction strings so no normalization beyond casefolding is required).
# ----------------------------------------------------------------------------


def load_vocab(path):
    with open(path, "r", encoding="utf-8") as handle:
        return {line.rstrip("\n"): index for index, line in enumerate(handle)}


def wordpiece(text, vocab, unk="[UNK]", max_chars=100):
    pieces = []
    for word in text.lower().split():
        if len(word) > max_chars:
            pieces.append(unk)
            continue
        start = 0
        sub = []
        ok = True
        while start < len(word):
            end = len(word)
            found = None
            while start < end:
                candidate = word[start:end]
                if start > 0:
                    candidate = "##" + candidate
                if candidate in vocab:
                    found = candidate
                    break
                end -= 1
            if found is None:
                ok = False
                break
            sub.append(found)
            start = end
        pieces.extend(sub if ok else [unk])
    return pieces


def transformer_encoder_stack(tokens, layers, d_model, ffn_dim):
    total = Count()
    for _ in range(layers):
        total.add(linear(tokens, d_model, 3 * d_model))
        total.add(Count(macs=tokens * tokens * d_model, soft=tokens * tokens))
        total.add(Count(macs=tokens * tokens * d_model, elem=tokens * d_model))
        total.add(linear(tokens, d_model, d_model))
        total.add(linear(tokens, d_model, ffn_dim))
        total.add(linear(tokens, ffn_dim, d_model))
    return total


def cross_attention_decoder(queries, memory, layers, d_model, ffn_dim):
    total = Count()
    for _ in range(layers):
        # Self-attention over the query tokens.
        total.add(linear(queries, d_model, 3 * d_model))
        total.add(Count(macs=queries * queries * d_model, soft=queries * queries))
        total.add(Count(macs=queries * queries * d_model, elem=queries * d_model))
        total.add(linear(queries, d_model, d_model))
        # Cross-attention: queries from the query tokens, keys and values from
        # the encoder memory, which is what makes the memory length matter.
        total.add(linear(queries, d_model, d_model))
        total.add(linear(memory, d_model, 2 * d_model))
        total.add(Count(macs=queries * memory * d_model, soft=queries * memory))
        total.add(Count(macs=queries * memory * d_model, elem=queries * d_model))
        total.add(linear(queries, d_model, d_model))
        # Feed-forward on the query tokens only.
        total.add(linear(queries, d_model, ffn_dim))
        total.add(linear(queries, ffn_dim, d_model))
    return total


def decoder_parameters(layers, d_model, ffn_dim, self_attention=True):
    per_layer = (8 if self_attention else 4) * d_model * d_model + 2 * d_model * ffn_dim
    return layers * per_layer


# ----------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", required=True, help="retained evidence directory")
    parser.add_argument("--recipe", required=True, help="recipe.json path")
    parser.add_argument("--output", required=True, help="new JSON file to write")
    args = parser.parse_args()

    sources = os.path.abspath(args.sources)
    output = os.path.abspath(args.output)
    if os.path.exists(output):
        sys.exit("refusing to overwrite an existing output file: %s" % output)
    if output.startswith(sources + os.sep):
        sys.exit("the output must not be written inside the sources directory")

    with open(args.recipe, "r", encoding="utf-8") as handle:
        recipe = json.load(handle)

    mac_flops = recipe["convention"]["flops_per_multiply_add"]
    elem_ops = recipe["convention"]["elementwise_ops_per_activation_element"]

    hl = recipe["high_level_policy"]
    ll = recipe["low_level_policy"]

    measured = read_deposit(sources, recipe["deposit"], recipe["work_units"])
    ai_duration = {}
    human_duration = {}
    for unit in recipe["work_units"]:
        pid = unit["point_id"]
        if pid in measured:
            ai_duration[pid] = measured[pid]["ai"]["duration_s"]
            human_duration[pid] = measured[pid]["human"]["duration_s"]
        else:
            ai_duration[pid] = unit["ai_duration_s"]
    procedure_seconds = ai_duration[recipe["work_units"][0]["point_id"]]

    # --- language encoder input -------------------------------------------
    language = ll["language_encoder"]
    vocab_path = os.path.join(sources, language["vocab_file"])
    with open(vocab_path, "rb") as handle:
        digest = hashlib.sha256(handle.read()).hexdigest()
    if digest != language["vocab_sha256"]:
        sys.exit("DistilBERT vocabulary hash mismatch: %s" % digest)
    vocab = load_vocab(vocab_path)

    instructions = recipe["instructions"]
    task_positions = {}
    for text in instructions["task_instructions_verbatim"]:
        task_positions[text] = len(wordpiece(text, vocab)) + language["special_tokens_per_sequence"]
    corrective_positions = {}
    for text in instructions["corrective_instructions_verbatim"]:
        corrective_positions[text] = len(wordpiece(text, vocab)) + language["special_tokens_per_sequence"]

    task_values = sorted(task_positions.values())
    mean_task_positions = sum(task_values) / len(task_values)
    corrective_values = sorted(corrective_positions.values())

    def distilbert(tokens):
        stack = transformer_encoder_stack(
            tokens, language["layers"], language["d_model"], language["ffn_dim"])
        return stack

    language_count = distilbert(mean_task_positions)

    # --- high-level policy per inference -----------------------------------
    swin_count, swin_info = swin_transformer(hl["encoder"], hl["image_size"])
    encoder_passes = (hl["history_past_frames"] + hl["current_frame"]) * hl["views_per_frame"]
    hl_encoder = swin_count.scaled(encoder_passes)

    memory_tokens = encoder_passes * swin_info["output_tokens"]
    dec = hl["decoder"]
    hl_decoder = linear(memory_tokens, dec["input_width"], dec["d_model"])
    hl_decoder.add(cross_attention_decoder(
        dec["queries"], memory_tokens, dec["layers"], dec["d_model"], dec["ffn_dim"]))
    for classes in dec["head_classes"]:
        hl_decoder.add(linear(1, dec["d_model"], dec["d_model"]))
        hl_decoder.add(linear(1, dec["d_model"], classes))

    hl_call = Count().add(hl_encoder).add(hl_decoder)
    hl_call_flops = hl_call.flops(mac_flops, elem_ops)
    hl_rate = 1.0 / hl["inference_period_s"]

    # --- low-level policy per inference ------------------------------------
    backbone = ll["vision_backbone"]
    effnet_count, film_count, effnet_info = efficientnet(
        backbone, ll["image_size"], film_width=ll["film"]["conditioning_width"])
    effnet_ref, _, effnet_ref_info = efficientnet(backbone, backbone["reference_resolution"])

    visual = Count().add(effnet_count).add(film_count).scaled(ll["images_per_call"])
    visual_tokens = ll["images_per_call"] * effnet_info["output_tokens"]

    act = ll["action_transformer"]
    encoder_tokens = visual_tokens + act["extra_encoder_tokens"]
    act_count = linear(visual_tokens, effnet_info["output_channels"], act["d_model"])
    act_count.add(transformer_encoder_stack(
        encoder_tokens, act["encoder_layers"], act["d_model"], act["ffn_dim"]))
    act_count.add(cross_attention_decoder(
        ll["chunk_size"], encoder_tokens, act["decoder_layers"], act["d_model"], act["ffn_dim"]))
    act_count.add(linear(ll["chunk_size"], act["d_model"], ll["action_dimension"]))

    ll_call = Count().add(visual).add(language_count).add(act_count)
    ll_call_flops = ll_call.flops(mac_flops, elem_ops)
    rate_default = ll["action_hz"] / ll["execution_horizon_default_steps"]
    rate_grasp = ll["action_hz"] / ll["execution_horizon_grasp_steps"]

    # --- parameter reconciliation ------------------------------------------
    act_parameters = (
        decoder_parameters(act["encoder_layers"], act["d_model"], act["ffn_dim"], self_attention=False)
        + decoder_parameters(act["decoder_layers"], act["d_model"], act["ffn_dim"], self_attention=True)
        + effnet_info["output_channels"] * act["d_model"]
        + ll["chunk_size"] * act["d_model"]
        + act["d_model"] * ll["action_dimension"]
    )
    low_level_parameters = (
        effnet_info["parameters_without_classifier"]
        + effnet_info["film_parameters"]
        + act_parameters
    )
    hl_decoder_parameters = (
        decoder_parameters(dec["layers"], dec["d_model"], dec["ffn_dim"])
        + dec["input_width"] * dec["d_model"]
        + sum(dec["d_model"] * dec["d_model"] + dec["d_model"] * c for c in dec["head_classes"])
    )

    # --- per work unit ------------------------------------------------------
    def unit_flops(duration, grasp_fraction, hl_flops, ll_flops,
                   hl_rate_value, rate_default_value, rate_grasp_value,
                   language_flops_per_call=None, language_per_high_level=False):
        grasp_seconds = duration * grasp_fraction
        other_seconds = duration - grasp_seconds
        hl_calls = duration * hl_rate_value
        ll_calls = grasp_seconds * rate_grasp_value + other_seconds * rate_default_value
        total = hl_calls * hl_flops + ll_calls * ll_flops
        if language_per_high_level:
            total -= ll_calls * language_flops_per_call
            total += hl_calls * language_flops_per_call
        return total, hl_calls, ll_calls

    language_flops = language_count.flops(mac_flops, elem_ops)

    results = {}
    for unit in recipe["work_units"]:
        duration = ai_duration[unit["point_id"]]
        total, hl_calls, ll_calls = unit_flops(
            duration, unit["grasp_phase_fraction"],
            hl_call_flops, ll_call_flops, hl_rate, rate_default, rate_grasp)
        results[unit["point_id"]] = {
            "label": unit["label"],
            "ai_duration_s": duration,
            "high_level_calls": hl_calls,
            "low_level_calls": ll_calls,
            "high_level_flops": hl_calls * hl_call_flops,
            "low_level_flops": ll_calls * ll_call_flops,
            "compute_flops": total,
            "language_positions_per_low_level_call": mean_task_positions,
            "language_text_positions": ll_calls * mean_task_positions,
            "human_time_s": human_duration.get(unit["point_id"]),
            "deposit": measured.get(unit["point_id"]),
        }

    # --- human-time transfer for the whole-procedure unit -------------------
    order = [u["point_id"] for u in recipe["work_units"]]
    paired = sorted(human_duration, key=order.index)
    surgeon_total = sum(human_duration[p] for p in paired)
    robot_total = sum(ai_duration[p] for p in paired)
    ratio = surgeon_total / robot_total
    per_subtask_ratios = {p: human_duration[p] / ai_duration[p] for p in paired}
    procedure = recipe["work_units"][0]
    tasks = recipe["scenarios"]["human_per_task_rate_transfer_tasks"]
    per_task_rate = surgeon_total / len(paired) * tasks
    central = procedure_seconds * ratio
    human_transfer = {
        "paired_subtasks": paired,
        "surgeon_seconds_total": surgeon_total,
        "srt_h_seconds_total": robot_total,
        "surgeon_to_srt_h_ratio": ratio,
        "per_subtask_ratios": per_subtask_ratios,
        "procedure_srt_h_seconds": procedure_seconds,
        "procedure_surgeon_seconds_transferred": central,
        "procedure_surgeon_seconds_range": [
            procedure_seconds * min(per_subtask_ratios.values()),
            procedure_seconds * max(per_subtask_ratios.values()),
        ],
        "alternative_per_task_rate_transfer": {
            "seconds": per_task_rate,
            "donor_tasks": len(paired),
            "procedure_tasks": tasks,
            "geometric_mean_with_central": math.sqrt(central * per_task_rate),
            "adopted": False,
            "reason": ("Not averaged into the central. The two transfers are not equally "
                       "defensible: the ratio transfer already carries the task-length "
                       "information that a per-task rate discards, and both are biased the "
                       "same way, so averaging cancels nothing."),
        },
    }
    results[procedure["point_id"]]["human_time_s"] = central

    # --- scenarios ----------------------------------------------------------
    scen = recipe["scenarios"]
    scenarios = {}

    for passes in scen["hl_encoder_passes"]:
        memory = passes * swin_info["output_tokens"]
        decoder = linear(memory, dec["input_width"], dec["d_model"])
        decoder.add(cross_attention_decoder(
            dec["queries"], memory, dec["layers"], dec["d_model"], dec["ffn_dim"]))
        call = Count().add(swin_count.scaled(passes)).add(decoder)
        scenarios["high_level_%d_encoder_passes" % passes] = {
            "flops_per_call": call.flops(mac_flops, elem_ops),
            "procedure_flops": unit_flops(
                procedure_seconds, recipe["work_units"][0]["grasp_phase_fraction"],
                call.flops(mac_flops, elem_ops), ll_call_flops,
                hl_rate, rate_default, rate_grasp)[0],
        }

    # Frame caching: consecutive high-level calls share two of the five frames,
    # so an implementation that keeps their embeddings re-encodes six views
    # while the decoder still attends to all ten frames' tokens.
    cached_passes = scen["hl_frame_cache_encoder_passes"]
    cached_call = Count().add(swin_count.scaled(cached_passes)).add(hl_decoder)
    scenarios["high_level_frame_cache_%d_encoder_passes" % cached_passes] = {
        "description": scen["hl_frame_cache_note"],
        "flops_per_call": cached_call.flops(mac_flops, elem_ops),
        "procedure_flops": unit_flops(
            procedure_seconds, recipe["work_units"][0]["grasp_phase_fraction"],
            cached_call.flops(mac_flops, elem_ops), ll_call_flops,
            hl_rate, rate_default, rate_grasp)[0],
    }

    upper = scen["hl_decoder_parameter_multiplication_upper_bound_parameters"]
    upper_call = hl_encoder.flops(mac_flops, elem_ops) + 2 * upper * (memory_tokens + dec["queries"])
    scenarios["high_level_decoder_parameter_multiplication"] = {
        "flops_per_call": upper_call,
        "procedure_flops": unit_flops(
            procedure_seconds, recipe["work_units"][0]["grasp_phase_fraction"],
            upper_call, ll_call_flops, hl_rate, rate_default, rate_grasp)[0],
    }

    low = scen["ll_action_transformer_low"]
    low_act = linear(visual_tokens, effnet_info["output_channels"], low["d_model"])
    low_act.add(transformer_encoder_stack(
        encoder_tokens, low["encoder_layers"], low["d_model"], low["ffn_dim"]))
    low_act.add(cross_attention_decoder(
        ll["chunk_size"], encoder_tokens, low["decoder_layers"], low["d_model"], low["ffn_dim"]))
    low_call = Count().add(visual).add(language_count).add(low_act)
    scenarios["low_level_action_transformer_d%d" % low["d_model"]] = {
        "flops_per_call": low_call.flops(mac_flops, elem_ops),
        "action_transformer_parameters": (
            decoder_parameters(low["encoder_layers"], low["d_model"], low["ffn_dim"], self_attention=False)
            + decoder_parameters(low["decoder_layers"], low["d_model"], low["ffn_dim"])),
        "procedure_flops": unit_flops(
            procedure_seconds, recipe["work_units"][0]["grasp_phase_fraction"],
            hl_call_flops, low_call.flops(mac_flops, elem_ops),
            hl_rate, rate_default, rate_grasp)[0],
    }

    for fraction in scen["grasp_phase_fraction_alternatives"]:
        scenarios["procedure_grasp_fraction_%.4f" % fraction] = {
            "procedure_flops": unit_flops(
                procedure_seconds, fraction, hl_call_flops, ll_call_flops,
                hl_rate, rate_default, rate_grasp)[0],
        }

    if scen["language_cached_per_high_level_step"]:
        scenarios["language_encoded_once_per_high_level_step"] = {
            "procedure_flops": unit_flops(
                procedure_seconds, recipe["work_units"][0]["grasp_phase_fraction"],
                hl_call_flops, ll_call_flops, hl_rate, rate_default, rate_grasp,
                language_flops_per_call=language_flops, language_per_high_level=True)[0],
        }

    matrix_only_hl = hl_call.macs * mac_flops
    matrix_only_ll = ll_call.macs * mac_flops
    scenarios["matrix_operations_only"] = {
        "high_level_flops_per_call": matrix_only_hl,
        "low_level_flops_per_call": matrix_only_ll,
        "procedure_flops": unit_flops(
            procedure_seconds, recipe["work_units"][0]["grasp_phase_fraction"],
            matrix_only_hl, matrix_only_ll, hl_rate, rate_default, rate_grasp)[0],
    }

    # Combined extremes: every lever pushed the same way at once.
    low_passes = min(scen["hl_encoder_passes"])
    low_memory = low_passes * swin_info["output_tokens"]
    low_hl = Count().add(swin_count.scaled(low_passes))
    low_hl.add(linear(low_memory, dec["input_width"], dec["d_model"]))
    low_hl.add(cross_attention_decoder(
        dec["queries"], low_memory, dec["layers"], dec["d_model"], dec["ffn_dim"]))
    scenarios["combined_low"] = {
        "description": "%d high-level encoder passes, d=%d action transformer, language "
                       "encoded once per high-level step, no grasp-phase allowance, "
                       "matrix operations only" % (low_passes, low["d_model"]),
        "procedure_flops": unit_flops(
            procedure_seconds, 0.0, low_hl.macs * mac_flops, low_call.macs * mac_flops,
            hl_rate, rate_default, rate_grasp,
            language_flops_per_call=language_count.macs * mac_flops,
            language_per_high_level=True)[0],
    }
    scenarios["combined_high"] = {
        "description": "central encoder passes, high-level decoder charged by parameter "
                       "multiplication, longest published instruction, no grasp-phase allowance",
        "procedure_flops": None,
    }

    longest = max(corrective_values + task_values)
    long_language = distilbert(longest)
    long_call = Count().add(visual).add(long_language).add(act_count)
    scenarios["longest_published_instruction_%d_positions" % longest] = {
        "low_level_flops_per_call": long_call.flops(mac_flops, elem_ops),
        "procedure_flops": unit_flops(
            procedure_seconds, recipe["work_units"][0]["grasp_phase_fraction"],
            hl_call_flops, long_call.flops(mac_flops, elem_ops),
            hl_rate, rate_default, rate_grasp)[0],
    }
    scenarios["combined_high"]["procedure_flops"] = unit_flops(
        procedure_seconds, 0.0, upper_call, long_call.flops(mac_flops, elem_ops),
        hl_rate, rate_default, rate_grasp)[0]

    payload = {
        "recipe_sha256": hashlib.sha256(
            open(args.recipe, "rb").read()).hexdigest(),
        "source_hashes": {
            name: hashlib.sha256(open(os.path.join(sources, name), "rb").read()).hexdigest()
            for name in sorted(os.listdir(sources))
            if os.path.isfile(os.path.join(sources, name))
        },
        "convention": recipe["convention"],
        "high_level_policy": {
            "encoder": swin_info,
            "encoder_flops_per_pass": swin_count.flops(mac_flops, elem_ops),
            "encoder_passes_per_call": encoder_passes,
            "memory_tokens": memory_tokens,
            "decoder_parameters_reconstructed": hl_decoder_parameters,
            "decoder_flops_per_call": hl_decoder.flops(mac_flops, elem_ops),
            "flops_per_call": hl_call_flops,
            "components": {
                "encoder": hl_encoder.as_dict(mac_flops, elem_ops),
                "decoder": hl_decoder.as_dict(mac_flops, elem_ops),
            },
            "calls_per_second": hl_rate,
            "reported_parameters": {"total": 45000000, "encoder": 29000000,
                                    "transformer_and_heads": 16000000},
        },
        "low_level_policy": {
            "vision_backbone": effnet_info,
            "vision_backbone_flops_per_image": effnet_count.flops(mac_flops, elem_ops),
            "vision_backbone_multiply_adds_at_reference_resolution": effnet_ref.macs,
            "vision_backbone_parameters_with_classifier_check": effnet_ref_info["parameters_with_classifier"],
            "film_flops_per_image": film_count.flops(mac_flops, elem_ops),
            "language_positions_mean_task_instruction": mean_task_positions,
            "language_flops_per_call": language_flops,
            "visual_tokens": visual_tokens,
            "action_transformer_tokens": encoder_tokens,
            "action_transformer_queries": ll["chunk_size"],
            "action_transformer_parameters_reconstructed": act_parameters,
            "flops_per_call": ll_call_flops,
            "components": {
                "vision_and_film": visual.as_dict(mac_flops, elem_ops),
                "language": language_count.as_dict(mac_flops, elem_ops),
                "action_transformer": act_count.as_dict(mac_flops, elem_ops),
            },
            "calls_per_second_default_phases": rate_default,
            "calls_per_second_grasp_phase": rate_grasp,
            "parameter_reconciliation": {
                "efficientnet_b3_features": effnet_info["parameters_without_classifier"],
                "film_generators": effnet_info["film_parameters"],
                "action_transformer": act_parameters,
                "total": low_level_parameters,
                "reported_total": 72000000,
            },
        },
        "instruction_positions": {
            "task": task_positions,
            "corrective": corrective_positions,
            "mean_task_positions": mean_task_positions,
        },
        "human_time_transfer": human_transfer,
        "work_units": results,
        "scenarios": scenarios,
    }

    with open(output, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=False)
        handle.write("\n")
    print("wrote %s" % output)
    for point_id, value in results.items():
        print("  %-32s %.4e FLOPs over %.0f s" % (
            point_id, value["compute_flops"], value["ai_duration_s"]))


if __name__ == "__main__":
    main()
