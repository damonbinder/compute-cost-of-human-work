#!/usr/bin/env python3
"""Establish what the Terminal-Bench 4.0 token counters mean, from dollars.

Each Harbor Hub trial record carries input_tokens, cache_tokens, output_tokens
and cost_usd, so the per-million price vector can be fitted rather than assumed.
Two readings are tested per run:

    A  disjoint (as on Terminal-Bench 2.1):  cost = pU*I + pC*C + pO*O
    B  nested, C is a subset of I:           cost = pU*(I-C) + pC*C + pO*O

Reading A returns a negative cache-read price on nearly every run; reading B
returns each provider's published rates. See terminal-bench-4.md#compute.

    python3 dataset/research/terminal-bench-4/price_solve.py \
        --sources agent-work/sources/terminal-bench-4
"""

import argparse
import collections
import csv
from pathlib import Path


def lstsq(A, b):
    n = len(A[0])
    M = [[sum(A[k][i] * A[k][j] for k in range(len(A))) for j in range(n)]
         for i in range(n)]
    v = [sum(A[k][i] * b[k] for k in range(len(A))) for i in range(n)]
    for i in range(n):
        p = max(range(i, n), key=lambda r: abs(M[r][i]))
        M[i], M[p] = M[p], M[i]
        v[i], v[p] = v[p], v[i]
        for r in range(i + 1, n):
            f = M[r][i] / M[i][i]
            for c in range(i, n):
                M[r][c] -= f * M[i][c]
            v[r] -= f * v[i]
    x = [0.0] * n
    for i in reversed(range(n)):
        x[i] = (v[i] - sum(M[i][j] * x[j] for j in range(i + 1, n))) / M[i][i]
    return x


def fit(X, b):
    x = lstsq(X, b)
    res = sum((sum(X[k][i] * x[i] for i in range(3)) - b[k]) ** 2
              for k in range(len(b)))
    tot = sum(y * y for y in b)
    return x, (res / tot) ** 0.5


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", required=True)
    a = ap.parse_args()
    rows = list(csv.DictReader(
        open(Path(a.sources) / "tb40-hub-trials.csv", newline="")))
    by = collections.defaultdict(list)
    for r in rows:
        by[r["run"]].append(r)
    for run, rs in sorted(by.items()):
        rs = [r for r in rs if r["cost_usd"] not in ("", "None")
              and float(r["cost_usd"]) > 0 and r["input_tokens"] not in ("", "None")]
        if not rs:
            print("%-52s no published cost" % run[:52])
            continue
        I = [int(r["input_tokens"]) / 1e6 for r in rs]
        C = [int(r["cache_tokens"]) / 1e6 for r in rs]
        O = [int(r["output_tokens"]) / 1e6 for r in rs]
        b = [float(r["cost_usd"]) for r in rs]
        xa, ra = fit([[I[k], C[k], O[k]] for k in range(len(rs))], b)
        xb, rb = fit([[I[k] - C[k], C[k], O[k]] for k in range(len(rs))], b)
        print("%-52s A pU=%7.2f pC=%7.2f pO=%7.2f rrms=%.4f | "
              "B pU=%7.2f pC=%6.2f pO=%7.2f rrms=%.4f"
              % (run[:52], xa[0], xa[1], xa[2], ra, xb[0], xb[1], xb[2], rb))


if __name__ == "__main__":
    main()
