#!/usr/bin/env python3
"""Performance labels for the OmegaUse-OfficeVal cells, and the standard errors
the close-call rule needs.

The benchmark score is the sum over 100 tasks of a per-task score in [0, 1], so
it reads as a percentage.  The chance floor is zero: an unmodified input file
triggers no positive rubric item, and any negative item it does trigger is
clipped away, so the delivered-artifact score of a do-nothing policy is 0.

Per-task scores are not released, so the per-task standard deviation is bounded
rather than measured: for a variable on [0, 1] with mean mu the largest possible
variance is mu*(1-mu), attained by a two-point distribution on {0, 1}.  That
gives the widest standard error, which is the conservative direction for a rule
that keeps rows within one standard error of the guide.  The human score is
treated as fixed; because both sides are scored on the same 100 tasks, the
paired standard error of the ratio would be smaller still.

Usage:
  python3 performance_labels.py --table3 <path>/omegause-table3.csv \
      --out <path>/performance-labels.csv

Dependencies: Python 3.8+ standard library only.
"""
import argparse, csv, math

N_TASKS = 100
GUIDE = 0.5


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--table3", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rows = list(csv.DictReader(open(a.table3, newline="", encoding="utf-8-sig")))
    human = next(r for r in rows if r["agent"] == "Human")
    hs = float(human["score"])
    out = []
    for r in rows:
        if r["agent"] == "Human":
            continue
        s = float(r["score"])
        mu = s / N_TASKS
        sd_max = math.sqrt(mu * (1 - mu))
        se_score = sd_max / math.sqrt(N_TASKS) * N_TASKS      # on the 0-100 scale
        ratio = s / hs
        se_ratio = se_score / hs
        sefg = (ratio - GUIDE) / se_ratio
        out.append(dict(agent=r["agent"], score=s, human_score=hs,
                        ratio_to_human=round(ratio, 4),
                        se_of_ratio_upper_bound=round(se_ratio, 4),
                        standard_errors_from_guide=round(sefg, 3),
                        label="below"))
    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]), lineterminator="\n")
        w.writeheader()
        for o in out:
            w.writerow(o)
    print("wrote", a.out)
    for o in out:
        print(f'{o["agent"]:16s} score {o["score"]:6.2f} ratio {o["ratio_to_human"]:.4f} '
              f'SE {o["se_of_ratio_upper_bound"]:.4f} -> {o["standard_errors_from_guide"]:+.3f} SE '
              f'from the 0.5 guide')


if __name__ == "__main__":
    main()
