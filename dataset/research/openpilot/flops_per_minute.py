#!/usr/bin/env python3
"""Turn the per-inference ONNX counts into FLOPs per minute of driving.

modeld runs the deployed driving graph once per camera frame at
ModelConstants.MODEL_RUN_FREQ = 20 Hz (DT_MDL = 0.05 s), so one minute of
driving is 1,200 forward passes of every graph in the deployed set.

Reads the JSON written by count_onnx_flops.py; writes a table to stdout.
"""
import json
import sys

RATE_HZ = 20
SECONDS = 60
CALLS = RATE_HZ * SECONDS

# release -> (label, release date, [graph file names])
SETS = [
    ("v0.8", "2020-11-29", ["supercombo-v0.8.onnx"]),
    ("v0.8.5", "2021-06-12", ["supercombo-v0.8.5.onnx"]),
    ("v0.8.16", "2022-08-31", ["supercombo-v0.8.16.onnx"]),
    ("v0.9.4", "2023-07-27", ["supercombo-v0.9.4.onnx"]),
    ("v0.9.7", "2024-06-14", ["supercombo-v0.9.7.onnx"]),
    ("v0.9.9", "2025-06-19", ["driving_vision-v0.9.9.onnx", "driving_policy-v0.9.9.onnx"]),
    ("v0.11.1", "2026-06-05", ["driving_vision-v0.11.1.onnx", "driving_policy-v0.11.1.onnx"]),
    ("v0.11.1-big", "2026-06-05", ["big_driving_vision-v0.11.1.onnx", "big_driving_policy-v0.11.1.onnx"]),
    ("chestnut-cinque-v2", "2026-09-11", ["big_driving_supercombo-master.onnx"]),
]


def sig(x, n=4):
    from decimal import Decimal
    if x == 0:
        return 0
    import math
    e = math.floor(math.log10(abs(x)))
    return int(round(x, -(e - n + 1)))


def main(paths):
    counts = {}
    for p in paths:
        for r in json.load(open(p)):
            counts[r["model"]] = r
    print(f"{'release':<20} {'date':<11} {'params':>13} {'MACs/inf':>15} "
          f"{'FLOPs/inf':>16} {'FLOPs/min':>14} {'rounded':>12}")
    for label, date, files in SETS:
        if not all(f in counts for f in files):
            print(f"{label:<20} MISSING {[f for f in files if f not in counts]}")
            continue
        params = sum(counts[f]["parameters"] for f in files)
        macs = sum(counts[f]["macs_per_inference"] for f in files)
        flops = 2 * macs
        per_min = flops * CALLS
        print(f"{label:<20} {date:<11} {params:>13,} {macs:>15,} {flops:>16,} "
              f"{per_min:>14.6e} {sig(per_min):>12}")


if __name__ == "__main__":
    main(sys.argv[1:])
