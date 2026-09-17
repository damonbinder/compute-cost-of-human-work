#!/usr/bin/env python3
"""Write the five FrontierMath Erdos candidate rows from calculations.json.

Every numeric field comes out of the calculations file, so a row cannot drift
from the arithmetic. Text fields are held at or under the dataset maxima
DECISIONS.md records, and the script refuses to write if any exceeds them.

    python3 research/build_rows.py \
        --calculations research/calculations.json \
        --points-header ../../../dataset/points.csv \
        --out points.csv
"""

import argparse
import csv
import json

CAPS = {"notes": 586, "task_description": 560, "performance_evidence": 337,
        "source_record": 455, "compute_source": 220, "human_time_source": 205}

BENCH = "https://github.com/epoch-research/LeanOpenProblems"
PAPER = "https://epoch.ai/files/frontiermath-erdos.pdf"
POST = "https://epoch.ai/latest/announcing-frontiermath-erdos"

NOTE_PRE = "Compute uses the repository's published per-attempt token counters, not a cost inversion; priced at Astra's rates they reproduce the reported dollars. attention_context is this row's own cache-read multiple times 2,800. The Lean term is uncompressed, so an upper bound. "

SHARED = {
    "task_category": "mathematics_puzzles",
    "model_id": "gpt-6-astra",
    "compute_scope": "inference",
    "human_skill": "expert",
    "human_time_scope": "task_performance",
    "performance_vs_human": "match",
    "compute_evidence": "derived_assumed_inputs",
    "human_time_evidence": "llm_estimate_judgment",
    "human_time_statistic": "point_estimate",
    "human_time_subset": "successful",
    "human_attempts": "not_applicable",
    "compute_method": "params_tokens",
    "compute_statistic": "mean",
    "compute_subset": "successful",
    "tokens_accounting": "input_cache_creation_output",
    "source_dataset": "FrontierMath Erdos (FME)",
    "ai_cost_basis": "reported",
    "ai_cost_date": "2026-09-03",
    "human_cost_usd": "",
    "human_cost_basis": "not_available",
    "frontier": "",
}

TEXT = {
1: dict(
    point_id="reas-erdos1-astra",
    task="Disprove Erdos problem 1 on sum-distinct sets",
    task_id="disprove-erdos-problem-1-on-sum-distinct-sets",
    repo="https://github.com/tadamcz/erdos1",
    lean="apn/data/erdos/Isolated/Erdos1.erdos_1.lean",
    appendix="Appendix B.1",
    task_description=(
        "Resolve Erdos problem 1: if A is a subset of {1,...,N} of size n whose "
        "subset sums are all distinct, must N exceed a fixed constant times "
        "2^n? Erdos called it perhaps his first serious problem, dated it to "
        "1931 and offered $500; the only prior bounds were Erdos and Moser's "
        "lower 2^n/sqrt(n) and Bohman's upper 0.22002 times 2^n, and it was "
        "open in August 2026. The deliverable and completion criterion is a "
        "Lean 4 proof of the benchmark's trusted statement or of its negation "
        "that Comparator accepts on Lean's three standard axioms."),
    performance_evidence=(
        "AI produced a Lean 4 disproof that Comparator accepted on Lean's three "
        "standard axioms and that replays in the repository's CI: for every "
        "epsilon there are arbitrarily large sum-distinct sets of size n in "
        "{1,...,N} with N below epsilon 2^n. Resolved in 2 of 5 attempts. "
        "Assumed human baseline 194 active hours."),
    notes=NOTE_PRE + 'Human time: 4 x 7 d x 8 h/d x 0.35 = 78 h for the human resolution of Erdos 52, x 1.5 because this construction was not immediately legible, = 118 h, plus 2,427 measured lines / 31.7 per hour = 77 h; scenarios 92 to 395 h. Mean over the two resolutions, $405 and $1,384; the disproof is ineffective in epsilon.',
    issues="different_inputs_or_tools; different_assessment",
),
74: dict(
    point_id="reas-erdos74-astra",
    task="Disprove Erdos problem 74 on almost bipartite graphs",
    task_id="disprove-erdos-problem-74-on-almost-bipartite-graphs",
    repo="https://github.com/tadamcz/erdos74",
    lean="apn/data/erdos/Isolated/Erdos74.erdos_74.lean",
    appendix="Appendix B.2",
    task_description=(
        "Resolve Erdos problem 74: for every f(n) tending to infinity, however "
        "slowly, is there a graph of infinite chromatic number in which every "
        "finite subgraph on n vertices can be made bipartite by deleting at "
        "most f(n) edges? Erdos, Hajnal and Szemeredi posed it in 1982, Erdos "
        "restated it a dozen times to 1997 and offered $500, and it was open in "
        "August 2026. The deliverable and completion criterion is a Lean 4 "
        "proof of the benchmark's trusted statement or of its negation that "
        "Comparator accepts on Lean's three standard axioms."),
    performance_evidence=(
        "AI produced a Lean 4 disproof that Comparator accepted on Lean's three "
        "standard axioms: some f tending to infinity forces chromatic number at "
        "most 3. Resolved in 7 of 7 attempts, in three distinct ways on Bloom's "
        "initial reading. No named partial result existed. Assumed human "
        "baseline 158 active hours."),
    notes=NOTE_PRE + 'Human time: 4 x 7 d x 8 h/d x 0.35 = 78 h for the human resolution of Erdos 52, unscaled, plus 2,516 measured lines / 31.7 per hour = 79 h; scenarios 76 to 287 h. Mean over the six resolutions with counters, $47 to $271; the seventh, $222, postdates the snapshot; every attempt resolved it.',
    issues="different_inputs_or_tools; different_assessment",
),
126: dict(
    point_id="reas-erdos126-astra",
    task="Prove Erdos problem 126 on prime factors of pairwise sums",
    task_id="prove-erdos-problem-126-on-prime-factors-of-pairwise-sums",
    repo="https://github.com/tadamcz/erdos126",
    lean="apn/data/erdos/Isolated/Erdos126.erdos_126.lean",
    appendix="Appendix B.3",
    task_description=(
        "Resolve Erdos problem 126: with f(n) the least number of distinct "
        "primes dividing the pairwise sums a+b of an n-element set of naturals, "
        "does f(n)/log n tend to infinity? Erdos and Turan proved f(n) between "
        "of order log n and of order n/log n in their first joint paper in 1934, "
        "Erdos asked repeatedly for the improvement and offered $250, and it was "
        "open in August 2026. The deliverable and completion criterion is a Lean "
        "4 proof of the benchmark's trusted statement or of its negation that "
        "Comparator accepts on Lean's three standard axioms."),
    performance_evidence=(
        "AI produced a Lean 4 proof that Comparator accepted on Lean's three "
        "standard axioms, and the four published resolutions prove polynomial "
        "lower bounds f(n) of order n^c at c = 1/8, 1/3, 1/2 and 1/5, far "
        "stronger than the superlogarithmic statement asked for. Resolved in 5 "
        "of 5 attempts. Human baseline 175 active hours."),
    notes=NOTE_PRE + 'Human time: 4 x 7 d x 8 h/d x 0.35 = 78 h for the human resolution of Erdos 52, unscaled, plus 3,058 measured lines / 31.7 per hour = 96 h; scenarios 84 to 313 h. Mean over the four resolutions with counters, $154 to $249; the fifth, $172, postdates the snapshot; every attempt resolved it.',
    issues="different_inputs_or_tools; different_assessment",
),
548: dict(
    point_id="reas-erdos548-astra",
    task="Prove the Erdos-Sos conjecture",
    task_id="prove-the-erdos-sos-conjecture",
    repo="https://github.com/tadamcz/erdos548",
    lean="apn/data/erdos_autoformalized/Isolated/Erdos548.erdos_548.lean",
    appendix="Appendix B.4",
    task_description=(
        "Resolve Erdos problem 548, the Erdos-Sos conjecture: for n at least "
        "k+1, does every graph on n vertices with at least (k-1)n/2 + 1 edges "
        "contain every tree on k+1 vertices? Erdos and Sos posed it in 1962, a "
        "survey is devoted to the special cases proved since, Chung's "
        "collection calls it one of the most tantalizing problems in extremal "
        "graph theory, and it was open in August 2026. The deliverable and "
        "completion criterion is a Lean 4 proof of the benchmark's trusted "
        "statement or of its negation that Comparator accepts on Lean's three "
        "standard axioms."),
    performance_evidence=(
        "AI produced a Lean 4 proof of the full conjecture that Comparator "
        "accepted on Lean's three standard axioms, by a double count of "
        "vertex orderings paired with an initial-edge label. Resolved in 1 of 4 "
        "attempts. Riordan and Scott have since read, simplified and extended "
        "the argument. Assumed human baseline 101 active hours."),
    notes=NOTE_PRE + 'Human time: 2 x 8 d x 8 h/d x 0.4 = 51 h for Riordan and Scott digesting and extending this argument, x 1.2 for a cold start, = 61 h, plus 1,243 measured lines / 31.7 per hour = 39 h; scenarios 40 to 212 h. The one verified resolution, $363 over 20.5 working hours.',
    issues="different_inputs_or_tools; different_assessment",
),
571: dict(
    point_id="reas-erdos571-astra",
    task="Prove the Erdos-Simonovits rational exponents conjecture",
    task_id="prove-the-erdos-simonovits-rational-exponents-conjecture",
    repo="https://github.com/tadamcz/erdos571",
    lean="apn/data/erdos_autoformalized/Isolated/Erdos571.erdos_571.lean",
    appendix="Appendix B.5",
    task_description=(
        "Resolve Erdos problem 571, a problem of Erdos and Simonovits: for "
        "every rational alpha in [1,2) is there a bipartite graph G whose Turan "
        "number ex(n;G) grows as n^alpha? Erdos posed it from 1974, Bukh and "
        "Conlon proved it for finite families rather than a single graph and "
        "later work realized many individual exponents, Bloom lists it among "
        "his ten favourite Erdos problems, and it was open in August 2026. The "
        "completion criterion is a Lean 4 proof of the benchmark's trusted "
        "statement or of its negation that Comparator accepts."),
    performance_evidence=(
        "AI produced a Lean 4 proof of the full single-graph conjecture that "
        "Comparator accepted on Lean's three standard axioms, constructing "
        "balanced rooted models for every rational exponent. Resolved in 1 of 4 "
        "attempts. Bloom judges it the hardest of the five. Human baseline "
        "563 hours."),
    notes=NOTE_PRE + 'Human time: 4 x 7 d x 8 h/d x 0.35 = 78 h for Erdos 52, x 3 because this artifact is 10,390 lines against 1,243 to 3,058 and a structural theorem, = 235 h, the one figure above the anchors, plus 10,390 / 31.7 = 328 h; scenarios 253 to 1,164 h. The one resolution, $617 over 41.3 h.',
    issues="different_inputs_or_tools; different_assessment",
),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--calculations", required=True)
    ap.add_argument("--points-header", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    calc = json.load(open(args.calculations, encoding="utf-8"))
    with open(args.points_header, newline="", encoding="utf-8-sig") as fh:
        fields = next(csv.reader(fh))
    assert len(fields) == 40, len(fields)

    rows = []
    for problem in (1, 74, 126, 548, 571):
        e = calc["problems"][str(problem)]
        c, hum = e["compute"], e["human"]["central"]
        t = TEXT[problem]
        r = dict(SHARED)
        r.update({
            "point_id": t["point_id"],
            "task": t["task"],
            "task_description": t["task_description"],
            "compute_flops": repr(c["compute_flops"]),
            "compute_flops_low": repr(c["compute_flops_low"]),
            "compute_flops_high": repr(c["compute_flops_high"]),
            "human_time": repr(hum["seconds"]),
            "comparison_issues": t["issues"],
            "performance_evidence": t["performance_evidence"],
            "human_time_source": ("research/frontiermath-erdos/frontiermath-erdos.md#human-time-%d; "
                                  "research/frontiermath-erdos/"
                                  "frontiermath-erdos.md#human-time"
                                  % problem),
            "ai_attempts": str(len(c["resolutions"])),
            "compute_source": (
                "%s#readme token table; "
                "research/frontiermath-erdos/frontiermath-erdos.md#compute; "
                "research/frontiermath-erdos/compute_frontiermath_erdos.py; "
                "research/attention-correction.md" % t["repo"]),
            "tokens": repr(c["counted_tokens"]),
            "source_record": (
                "%s; paper %s Table 3, %s; proof and counters %s at the "
                "2026-09-06 commit; statement %s/blob/main/%s; "
                "erdosproblems.com/%d; performance: "
                "research/frontiermath-erdos/frontiermath-erdos.md#verification"
                % (POST, PAPER, t["appendix"], t["repo"], BENCH, t["lean"],
                   problem)),
            "notes": t["notes"],
            "ai_cost_usd": "%.2f" % c["mean_cost_usd"],
            "attention_context": repr(c["attention_context"]),
            "attention_ratio": repr(c["attention_ratio"]),
            "task_id": t["task_id"],
        })
        for k, cap in CAPS.items():
            if len(r[k]) > cap:
                raise SystemExit("%s: %s is %d chars, cap %d"
                                 % (r["point_id"], k, len(r[k]), cap))
        if set(r) != set(fields):
            raise SystemExit("field mismatch: %s"
                             % sorted(set(r) ^ set(fields)))
        rows.append(r)

    with open(args.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\r\n")
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        print("%-22s flops=%-24s human_s=%-12s $%s  n=%s"
              % (r["point_id"], r["compute_flops"], r["human_time"],
                 r["ai_cost_usd"], r["ai_attempts"]))
    print("field lengths (cap): " + ", ".join(
        "%s %d(%d)" % (k, max(len(r[k]) for r in rows), CAPS[k]) for k in CAPS))


if __name__ == "__main__":
    main()
