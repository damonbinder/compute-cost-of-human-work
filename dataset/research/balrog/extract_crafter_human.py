#!/usr/bin/env python3
"""Extract per-episode statistics from the Crafter Human Expert Dataset.

Input  : the unzipped Crafter human dataset directory (100 `*.npz` episode files).
         Source archive: https://archive.org/details/crafter_human_dataset
         `dataset.zip`, md5 0276dc7b875cd5aea22852a2b9f71a20, 131,969,180 bytes.
         Unzipping it yields `dataset/` holding the 100 `.npz` files.
Output : a CSV with one row per episode carrying
           - environment steps,
           - the 22 achievement-unlocked flags and the BALROG-equivalent progression
             fraction (achievements unlocked / 22),
           - the step at which each achievement was first unlocked, -1 if never, which
             supports scoring a human episode at a truncated step budget,
           - the noop and sleeping-frame counts that identify the recording mode.

Conventions verified against crafter/recorder.py (EpisodeRecorder): the first array entry
is the reset observation with zero-filled action/reward fields, so the number of
environment steps is len(action) - 1 and array index k is environment step k.

A sleeping frame is one on which inventory_energy rises, which happens only while the
player sleeps. Under `run_gui.py --wait True` every frame of a sleeping bout would be
recorded as a noop and no other noop could occur, so the count of noops taken on
non-sleeping frames discriminates the two recording modes.

Dependencies: python3, numpy.

Usage:
    python3 extract_crafter_human.py \
        --dataset /path/to/unzipped/crafter_human_dataset/dataset \
        --out /path/to/sources/balrog/crafter-human-episodes.csv
"""
import argparse
import csv
import glob
import os

import numpy as np

NOOP_ACTION = 0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True, help="directory holding the 100 *.npz episode files")
    ap.add_argument("--out", required=True, help="output CSV path")
    args = ap.parse_args()

    files = sorted(glob.glob(os.path.join(args.dataset, "*.npz")))
    if not files:
        raise SystemExit(f"no .npz episodes found under {args.dataset}")

    rows = []
    ach_names = None
    for path in files:
        with np.load(path) as data:
            if ach_names is None:
                # The dataset spells the prefix "achivement_" (sic).
                ach_names = sorted(k for k in data.files if k.startswith("achivement_"))
            steps = int(data["action"].shape[0]) - 1
            flags, first = {}, {}
            for key in ach_names:
                series = data[key]
                short = key[len("achivement_"):]
                unlocked = bool(series.max() > 0)
                flags[short] = int(unlocked)
                # Array index k is environment step k, so argmax over (series > 0) is the
                # step on which the achievement was first recorded.
                first[short] = int(np.argmax(series > 0)) if unlocked else -1
            actions = data["action"][1:]
            energy = data["inventory_energy"]
            # Energy rises only while sleeping; index k of the diff is step k+1.
            sleeping = np.diff(energy.astype(int)) > 0

        unlocked_count = sum(flags.values())
        noop = int((actions == NOOP_ACTION).sum())
        noop_sleeping = int(((actions == NOOP_ACTION) & sleeping).sum())
        row = {"episode": os.path.basename(path), "steps": steps,
               "achievements_unlocked": unlocked_count, "progression": unlocked_count / len(ach_names),
               "noop_steps": noop, "sleeping_frames": int(sleeping.sum()),
               "noop_steps_not_sleeping": noop - noop_sleeping}
        row.update(flags)
        row.update({"first_unlock_step_" + k: v for k, v in first.items()})
        rows.append(row)

    if len(ach_names) != 22:
        raise SystemExit(f"expected 22 achievements, found {len(ach_names)}")

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    total = sum(r["steps"] for r in rows)
    print(f"episodes={len(rows)} mean_steps={total / len(rows):.2f} "
          f"mean_progression={100 * sum(r['progression'] for r in rows) / len(rows):.4f}% "
          f"total_steps={total} sleeping_frames={sum(r['sleeping_frames'] for r in rows)} "
          f"noop={sum(r['noop_steps'] for r in rows)} "
          f"noop_not_sleeping={sum(r['noop_steps_not_sleeping'] for r in rows)}")


if __name__ == "__main__":
    main()
