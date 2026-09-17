#!/usr/bin/env python3
"""Operation count for the MonoRace onboard networks (arXiv:2601.15222v1).

Counts matrix and convolution arithmetic only, at two operations per
multiply-add, matching the dataset's convention and the recipe already used for
the Swift drone-racing row. Batch normalisation, ReLU, max-pooling, the EKF,
the PnP solve, the corner detector and the conventional image preprocessing are
outside the AI-model FLOP total.

Dependencies: Python 3.8+ standard library only.

Usage:
    python3 gatenet_flops.py --inputs <monorace-inputs.json> --out <calculations.json>

Both paths are explicit. The script only reads --inputs and only writes --out.
"""

import argparse
import json


def conv(h, w, c_in, c_out, k):
    """FLOPs for a same-padded conv over an h x w output grid, 2 ops per MAC."""
    return 2 * h * w * c_in * c_out * k * k


def gatenet_flops(g, input_channels=None, upsample_kernel=None, skip_mode=None):
    """FLOPs for one GateNet forward pass over one 384x384 crop.

    Encoder: inc, then down1..down4 (max-pool then a double 3x3 conv block).
    Decoder: up1..up4 (channel-preserving transposed conv, skip combination,
    then a double 3x3 conv block). Five 1x1 heads, one per scale.
    """
    f = g["channel_scale_f"]
    base = g["base_channels"]
    k = g["conv_kernel"]
    ch = {name: base[name] // f for name in base}
    c_in = g["input_channels"] if input_channels is None else input_channels
    ku = g["upsample_kernel"] if upsample_kernel is None else upsample_kernel
    mode = g["skip_mode"] if skip_mode is None else skip_mode

    size = g["input_height"]
    assert size == g["input_width"]

    parts = {}
    # --- encoder -------------------------------------------------------
    # inc at full resolution; its output is the first skip.
    parts["inc"] = conv(size, size, c_in, ch["inc"], k) + conv(size, size, ch["inc"], ch["inc"], k)
    skips = [(ch["inc"], size)]
    prev = ch["inc"]
    for name in ["down1", "down2", "down3", "down4"]:
        size //= 2
        out = ch[name]
        parts[name] = conv(size, size, prev, out, k) + conv(size, size, out, out, k)
        if name != "down4":
            skips.append((out, size))
        prev = out

    # --- decoder -------------------------------------------------------
    # skips are [inc, down1, down2, down3]; up1 consumes down3, up4 consumes inc.
    decoder_out_channels = {}
    for idx, name in enumerate(["up1", "up2", "up3", "up4"]):
        skip_c, skip_size = skips[-1 - idx]
        # Transposed convolution from size -> 2*size, counted at its input
        # positions, preserving the channel count so the skip can be added.
        up = conv(size, size, prev, prev, ku)
        size *= 2
        assert size == skip_size
        combined = prev if mode == "add" else prev + skip_c
        out = ch[name]
        block = conv(size, size, combined, out, k) + conv(size, size, out, out, k)
        parts[name] = up + block
        decoder_out_channels[name] = (out, size)
        prev = out

    # --- multi-scale 1x1 heads ----------------------------------------
    head_sources = {
        "outc0": (ch["down4"], g["input_height"] // 16),
        "outc1": decoder_out_channels["up1"],
        "outc2": decoder_out_channels["up2"],
        "outc3": decoder_out_channels["up3"],
        "outc4": decoder_out_channels["up4"],
    }
    heads = 0
    for spec in g["output_heads"]:
        c, s = head_sources[spec["name"]]
        heads += conv(s, s, c, 1, spec["kernel"])
    parts["output_heads"] = heads

    parts["total"] = sum(v for key, v in parts.items() if key != "total")
    return parts


def mlp_flops(widths):
    """FLOPs for one forward pass of a fully connected stack, 2 ops per MAC."""
    return sum(2 * widths[i] * widths[i + 1] for i in range(len(widths) - 1))


def mlp_params(widths):
    """Weight count of a fully connected stack; biases excluded."""
    return sum(widths[i] * widths[i + 1] for i in range(len(widths) - 1))


def gatenet_params(g):
    """GateNet weight count, from the same ladder as the FLOP count.

    Weights only: biases and the affine parameters of batch normalisation are
    excluded, as are the non-parametric max-pool, ReLU and sigmoid stages.
    """
    f = g["channel_scale_f"]
    base = g["base_channels"]
    k = g["conv_kernel"]
    ku = g["upsample_kernel"]
    ch = {name: base[name] // f for name in base}
    c_in = g["input_channels"]

    enc = c_in * ch["inc"] * k * k + ch["inc"] * ch["inc"] * k * k
    prev = ch["inc"]
    for name in ["down1", "down2", "down3", "down4"]:
        out = ch[name]
        enc += prev * out * k * k + out * out * k * k
        prev = out

    dec = 0
    for name in ["up1", "up2", "up3", "up4"]:
        out = ch[name]
        dec += prev * prev * ku * ku            # channel-preserving transposed conv
        dec += prev * out * k * k + out * out * k * k
        prev = out

    heads = ch["down4"] + ch["up1"] + ch["up2"] + ch["up3"] + ch["up4"]
    return {"encoder": enc, "decoder": dec, "output_heads": heads, "total": enc + dec + heads}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", required=True, help="path to monorace-inputs.json")
    ap.add_argument("--out", required=True, help="path to write calculations JSON")
    args = ap.parse_args()

    data = json.loads(open(args.inputs, encoding="utf-8").read())
    g = data["gatenet"]
    c = data["gcnet"]
    r = data["race"]
    sc = data["scenarios"]

    gate = gatenet_flops(g)
    gate_per_call = gate["total"]
    gc_per_call = mlp_flops(c["layer_widths"])
    per_second = gate_per_call * g["call_rate_hz"] + gc_per_call * c["call_rate_hz"]

    t_org = r["ai_completion_seconds_organizer"]
    t_onboard = r["ai_completion_seconds_onboard"]
    total = per_second * t_org

    best = r["human_best_completions_seconds"]
    human_mean_best = sum(best.values()) / len(best)
    allc = r["human_all_completions_seconds"]
    human_mean_all = sum(allc) / len(allc)

    # Bracketing scenarios for the two assumed architecture inputs.
    gray = gatenet_flops(g, input_channels=sc["input_channels_grayscale"])["total"]
    k4 = gatenet_flops(g, upsample_kernel=sc["upsample_kernel_large"])["total"]
    concat = gatenet_flops(g, skip_mode="concat")["total"]
    concat_k4 = gatenet_flops(g, skip_mode="concat", upsample_kernel=sc["upsample_kernel_large"])["total"]

    def race_total(gate_call):
        return (gate_call * g["call_rate_hz"] + gc_per_call * c["call_rate_hz"]) * t_org

    out = {
        "gatenet_breakdown_flops_per_call": gate,
        "gatenet_parameters": gatenet_params(g),
        "gcnet_parameters": mlp_params(c["layer_widths"]),
        "gatenet_flops_per_call": gate_per_call,
        "gcnet_flops_per_call": gc_per_call,
        "gatenet_flops_per_second": gate_per_call * g["call_rate_hz"],
        "gcnet_flops_per_second": gc_per_call * c["call_rate_hz"],
        "gcnet_share_of_total": gc_per_call * c["call_rate_hz"] / per_second,
        "system_flops_per_second": per_second,
        "ai_race_seconds_organizer": t_org,
        "ai_race_seconds_onboard": t_onboard,
        "compute_flops_per_race": total,
        "compute_flops_per_race_onboard_timing": per_second * t_onboard,
        "compute_flops_per_lap": total / r["laps_per_race"],
        "human_time_seconds_mean_of_pilot_bests": human_mean_best,
        "human_attempts_pilot_bests": len(best),
        "human_time_seconds_mean_of_all_completions": human_mean_all,
        "human_attempts_all_completions": len(allc),
        "human_time_seconds_per_lap": human_mean_best / r["laps_per_race"],
        "ai_speed_advantage_vs_mean_pilot_best": human_mean_best / t_org,
        "scenarios": {
            "grayscale_input_flops_per_call": gray,
            "grayscale_input_race_flops": race_total(gray),
            "upsample_kernel_4_flops_per_call": k4,
            "upsample_kernel_4_race_flops": race_total(k4),
            "concat_skips_flops_per_call": concat,
            "concat_skips_race_flops": race_total(concat),
            "concat_skips_and_kernel_4_flops_per_call": concat_k4,
            "concat_skips_and_kernel_4_race_flops": race_total(concat_k4),
        },
    }
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
