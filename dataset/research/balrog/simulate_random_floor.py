#!/usr/bin/env python3
"""Measure what a uniform-random policy scores on BALROG's Crafter metric.

Runs a uniform-random policy over Crafter's 17 actions under the environment settings
BALROG uses (`envs.crafter_kwargs`: area 64x64, view 9x9, size 256x256, reward True,
max_episode_steps 2000), including the single noop step BALROG's `CrafterLanguageWrapper`
consumes on reset, and scores each episode by BALROG's own metric: the number of the 22
achievements unlocked at least once, divided by 22.

Output : JSON with, for each replication, the mean, standard deviation, standard error,
         mean episode length and per-achievement unlock rates, plus the pooled figures.

Crafter's simulation is NOT bit-reproducible across processes even with every seed this
script controls fixed, so re-running will not reproduce the published numbers exactly.
That is why the script runs several independent replications and records each: the
spread across them is the honest uncertainty on the floor. The published floor used in
the research note is the Crafter paper's own random column (Table B.1, 227.6 / 22 =
10.345%), which this simulation corroborates rather than replaces.

Dependencies: python3, numpy, crafter (`pip install crafter`). Tested with crafter 1.8.3.

Usage:
    python3 simulate_random_floor.py --episodes 200 --seed 20260913 \
        --out /path/to/research/balrog/crafter-random-floor.json
"""
import argparse
import collections
import json
import os
import statistics

import numpy as np

N_ACTIONS = 17
N_ACHIEVEMENTS = 22
MAX_EPISODE_STEPS = 2000


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=int, default=200, help="episodes per replication")
    ap.add_argument("--replications", type=int, default=5)
    ap.add_argument("--seed", type=int, default=20260913)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    import crafter

    def replication(seed):
        rng = np.random.default_rng(seed)
        fractions, lengths = [], []
        unlocks = collections.Counter()
        for _ in range(args.episodes):
            env = crafter.Env(area=(64, 64), view=(9, 9), size=(256, 256), reward=True,
                              length=MAX_EPISODE_STEPS, seed=int(rng.integers(1 << 31)))
            env.reset()
            # BALROG's CrafterLanguageWrapper.reset() steps the environment once with action 0.
            _, _, done, info = env.step(0)
            steps = 1
            while not done and steps < MAX_EPISODE_STEPS:
                _, _, done, info = env.step(int(rng.integers(N_ACTIONS)))
                steps += 1
            achieved = {k for k, v in info["achievements"].items() if v > 0}
            fractions.append(100.0 * len(achieved) / N_ACHIEVEMENTS)
            lengths.append(steps)
            unlocks.update(achieved)
        sd = statistics.stdev(fractions)
        return {"seed": seed, "episodes": args.episodes,
                "mean_progression_percent": statistics.mean(fractions),
                "sd_progression_percent": sd,
                "sem_progression_percent": sd / args.episodes ** 0.5,
                "mean_steps": statistics.mean(lengths),
                "per_achievement_unlock_percent": {k: 100.0 * v / args.episodes
                                                   for k, v in sorted(unlocks.items())}}

    reps = [replication(args.seed + i) for i in range(args.replications)]
    means = [r["mean_progression_percent"] for r in reps]
    result = {
        "replications": reps,
        "pooled_mean_progression_percent": statistics.mean(means),
        "replication_mean_min": min(means), "replication_mean_max": max(means),
        "mean_within_replication_sem": statistics.mean(r["sem_progression_percent"] for r in reps),
        "crafter_paper_random_column_percent": 227.6 / 22,
        "reproducibility": ("crafter is not bit-reproducible across processes: repeated runs of this "
                            "script with identical arguments give different replication means. The "
                            "spread between replication_mean_min and replication_mean_max is the "
                            "operative uncertainty."),
        "env_settings": {"area": [64, 64], "view": [9, 9], "size": [256, 256], "reward": True,
                         "max_episode_steps": MAX_EPISODE_STEPS, "reset_noop_step": True},
    }
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w") as fh:
        json.dump(result, fh, indent=1)
    print(f"replications={args.replications} x {args.episodes} episodes: pooled mean "
          f"{result['pooled_mean_progression_percent']:.3f}% "
          f"(range {result['replication_mean_min']:.3f}-{result['replication_mean_max']:.3f}), "
          f"within-replication sem ~{result['mean_within_replication_sem']:.3f}, "
          f"paper random column {result['crafter_paper_random_column_percent']:.3f}%")


if __name__ == "__main__":
    main()
