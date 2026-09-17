#!/usr/bin/env python3
"""FrontierMath Erdos: measured-token compute and anchored human time for the five
GPT-6 Astra resolutions.

Every number in research/frontiermath-erdos.md comes out of this script. It reads
nothing: every input is a named constant below with its source in the comment
above it. Standard library only, Python 3.9+.

Revision 7 (2026-09-16) replaces the human side with the research-mathematics
calibration of research/math-human-time/math-human-time.md, which Damon ruled
the standing method for these rows. The anchor-times-multiplier construction
and the 31.7 lines-per-hour formalization rate are withdrawn; the anchors
survive below as corroboration and as the direct record on #548.

Revision 4 (2026-09-16). Revision 2 changed the compute side, because the
per-problem submission repositories were found. Revision 3 made human_time the
active time the person who solved the problem spent, conditional on succeeding,
with no multiplier for other people's failed attempts. Revision 4 converts the
elapsed-time anchors to summed active hours honestly, places each problem within
or below the resulting band rather than at its top, and replaces the Imperial
FLT formalization rate with Li's, which is the matched case.

  * Compute is no longer a cost inversion. Each repository's README publishes
    per-attempt input / output / cache-read / cache-write token counts from the
    harness's own eval logs, so compute_flops is built from measured tokens. The
    dollar inversion survives only as a cross-check: pricing the counters at
    Astra's rates reproduces each reported dollar figure.
  * Human time is no longer programme-years keyed to how long the problem had
    been open. It is the size of the delivered artifact priced through two
    calibration tables: thirty-five resolved research problems giving hours per
    written page by size class, and twelve formalization projects giving formal
    lines per active hour. Years open is computed but never used.
"""

import argparse
import json

# ---------------------------------------------------------------- AI side

# OpenAI list prices for gpt-6-astra, USD per million text tokens, from
# dataset/research/cost/list-prices.csv and restated in each submission
# repository's README as the rates OpenAI provided on 2026-09-03.
P_INPUT = 10.00
P_OUTPUT = 50.00
P_CACHE_READ = 1.00
P_CACHE_WRITE = 12.50

# gpt-6-astra, copied from dataset/models.csv (not edited here).
ACTIVE = 3.0e11
ACTIVE_LOW = 1.0e11
ACTIVE_HIGH = 6.0e11
ATT_LAYERS = 75
ATT_WIDTH = 14720
OPENAI_LAYER_SHARE = 0.65  # research/attention-correction.md#model-architectures

# research/attention-correction.md#cache-implied-context and COLUMNS.md: the
# cache-implied mean attended context is alpha * n, with alpha the run's own
# cache-read multiple and n the new tokens per call. The percentiles are the
# 10th and 90th over the sixteen official Terminal-Bench 2.1 submissions.
N_NEW_CENTRAL = 2800.0
N_NEW_P10 = 1976.0
N_NEW_P90 = 19088.0
CONTEXT_CAP = 200000.0

# Every resolution whose token counts are published, from the README table of
# github.com/tadamcz/erdos{1,74,126,548,571} at the 2026-09-06 commits. Tokens
# are in millions as the READMEs give them: input / output / cache read / cache
# write. cost_usd and working_h are the READMEs' own figures, which match the
# paper's Table 3 to the dollar and to rounding in hours.
# (label, cost_usd, working_h, input_M, output_M, cache_read_M, cache_write_M)
RESOLUTIONS = {
    1: [
        ("default configuration, 28 Aug 2026", 405, 27.1, 0.05, 3.3, 74, 13.4),
        ("ReAct agent, larger budget, 26 Aug 2026 re-run", 1384, 84.0, 0.41, 8.6, 410, 43.4),
    ],
    74: [
        ("default configuration, 28 Aug 2026", 218, 14.5, 0.04, 1.7, 44, 7.2),
        ("ReAct agent, larger budget, 26 Aug 2026", 47, 5.0, 0.02, 0.3, 16, 1.1),
        ("ReAct agent, larger budget, 26 Aug 2026 re-run", 84, 5.8, 0.04, 0.7, 18, 2.4),
        ("default configuration, 2 Sep 2026", 150, 8.2, 0.06, 1.1, 30, 5.2),
        ("default configuration, 31 Aug 2026", 183, 11.5, 0.03, 1.5, 34, 6.1),
        ("default configuration, 28 Aug 2026 re-run", 271, 18.5, 0.05, 2.0, 65, 8.5),
    ],
    126: [
        ("default configuration, 28 Aug 2026", 247, 15.8, 0.06, 1.8, 53, 8.3),
        ("default configuration, 31 Aug 2026", 154, 8.4, 0.02, 0.9, 38, 5.5),
        ("default configuration, 2 Sep 2026", 194, 9.5, 0.03, 1.3, 40, 7.0),
        ("ReAct agent, larger budget, 26 Aug 2026", 249, 17.0, 0.02, 1.7, 77, 7.1),
    ],
    548: [
        ("ReAct agent, larger budget, 26 Aug 2026", 363, 20.5, 0.19, 2.1, 113, 11.5),
    ],
    571: [
        ("ReAct agent, larger budget, 26 Aug 2026 re-run", 617, 41.3, 0.35, 3.3, 222, 18.1),
    ],
}

# Resolutions the paper's Table 3 lists for which no token counts are published,
# because they postdate the 2026-09-06 repository snapshot.
# problem -> [(cost_usd, working_h), ...]
RESOLUTIONS_WITHOUT_TOKENS = {74: [(222, 10)], 126: [(172, 10)]}

# ---------------------------------------------------------------- human side

HOURS_PER_PERSON_YEAR = 2000.0       # DECISIONS.md, Damon 2026-09-13
# A standard working day, from the same ruling: 2,000 hours over 250 working
# days. Every anchor below converts elapsed calendar days through this figure.
HOURS_PER_WORKING_DAY = 8.0

# ---- Anchors -------------------------------------------------------------
#
# Revision 5, on Damon's rulings of 2026-09-16: every hours figure must be
# arithmetic on stated quantities, each factor either pointed at something in
# the record or labelled as an assumption with its reason. The form is
#
#     summed active hours = people x elapsed_days x 8 h/day x on_task_fraction
#
# elapsed_days are calendar days, so the fraction absorbs both weekends and the
# teaching, supervision, refereeing and other projects a working mathematician
# carries. The result bounds the work done inside the window from above: nothing
# in the record says the window was the whole job.
#
# Fields: key, people, elapsed_days, fraction (low, central, high), what the
# anchor measures, where each factor comes from.
ANCHORS = {
    "A1_erdos1026": dict(
        people=6, elapsed_days=2.0, fraction=(0.125, 0.25, 0.375),
        measures="a small, obscure problem closed under directed attention",
        people_basis="Tao's blog post of 2025-12-08 names about six "
                     "contributors making identifiable inputs",
        days_basis="Tao: all key inputs were 'assembled within 48 hours'",
        fraction_basis="pointed, not assumed: the same post times the "
                       "individual contributions at 'within hours', 'less than "
                       "an hour after that' and 'approximately an hour of run "
                       "time', which is one to three hours each over the "
                       "window, so 1/8 to 3/8 of one working day"),
    "A2_riordan_scott_548": dict(
        people=2, elapsed_days=8.0, fraction=(0.20, 0.40, 0.60),
        measures="digesting, simplifying and extending a short argument already "
                 "in hand, on this study's own problem #548",
        people_basis="two authors on arXiv:2609.15893",
        days_basis="2026-09-06, when the submission repositories were pushed, "
                   "to their 2026-09-14 submission",
        fraction_basis="assumption. Both are Oxford professors with teaching "
                       "and administration, but 14 September is before "
                       "Michaelmas term starts, so the fraction is set above a "
                       "term-time one; 0.40 is 3.2 hours a day each for eight "
                       "straight days including a weekend"),
    "A3_erdos52": dict(
        people=4, elapsed_days=7.0, fraction=(0.20, 0.35, 0.50),
        measures="resolving a Bloom top-ten Erdos problem and writing 25 pages",
        people_basis="four authors on arXiv:2605.28781",
        days_basis="2026-05-20, the AI disproof of #90 that the erdosproblems "
                   "wiki records as having inspired it, to their 2026-05-27 "
                   "submission",
        fraction_basis="assumption. Four working mathematicians in late May, "
                       "out of term in both the UK and the US, collaborating "
                       "intensively; 0.35 is 2.8 hours a day each. Four people "
                       "full time for a week would be 224 hours and they were "
                       "not full time"),
    "A4_sothanaphan_728": dict(
        people=1, elapsed_days=28.0, fraction=(0.15, 0.30, 0.50),
        measures="writing a 20-page paper from a finished AI Lean proof",
        people_basis="sole author of arXiv:2601.07421",
        days_basis="about four weeks spanning v1 to v5, the last dated "
                   "2026-01-27, against an AI resolution earlier that January",
        fraction_basis="assumption. One author over a month rather than a "
                       "burst, so a lower fraction than the two collaborative "
                       "anchors above"),
}
# Noga Alon's "a few dozen Erdos problems over his career" (Quanta, Aug 2026)
# is about 36 problems over a career from 1979, one per 1.3 years. It does not
# convert to hours without his time allocation, so it is used only as a
# direction check and is not an anchor.

# ---- The method, from research/math-human-time/math-human-time.md ---------
#
# Damon's ruling of 2026-09-16 makes the research-mathematics calibration the
# standing method for these rows, and it supersedes the anchor-times-multiplier
# construction revisions 4 to 6 used. The calibration's own tables supply every
# rate below; nothing here is a judgment multiplier.
#
#   pages  = measured Lean lines / lines per research-paper page
#   solve  = pages x the size class's hours per page
#   lean   = measured Lean lines / formal lines per active hour
#
# Step 4 of the method prefers a direct record on the problem at hand to the
# class rate, and #548 is the one row that has one: Riordan and Scott worked
# that exact argument in a dated eight-day window, anchor A2 below.

# Measured size of the delivered artifact: lines in the primary resolution
# module of each submission repository, wc -l at the 2026-09-06 commits.
LEAN_LINES = {1: 2427, 74: 2516, 126: 3058, 548: 1243, 571: 10390}
# No machine-idiom to human-idiom compression is applied, so the Lean term is an
# upper bound: a human writing Mathlib-idiom Lean would produce fewer lines than
# the machine did, and any compression only lowers the figure.

# Table 2 of the calibration: eight completed formalization projects, measured
# on both ends. Median 12.6 formal lines per active hour, band 5.4 to 15.0,
# which is a dispersion of 2.8 and the tightest number in that note. It
# supersedes both the 31.7 taken from Li's unpublished line count and the 5.88
# taken from the Imperial FLT project's funded head-count.
LINES_PER_ACTIVE_HOUR = (15.0, 12.6, 5.4)      # fast, central, slow
# Table 2's four projects with both a line count and a paper page count.
LINES_PER_PAPER_PAGE = 417.2
# Table 1 of the calibration: hours per written page by size class, over thirty
# resolved problems, with the class minimum and maximum as the dispersion.
# short <= 12 pages, medium 13-60, large > 60.
HOURS_PER_PAGE = {"short": (4.1, 8.0, 42.0),
                  "medium": (1.1, 8.3, 20.0),
                  "large": (18.8, 56.6, 196.5)}
# The one direct record in this batch: A2 times the cold-start multiplier the
# note argues, held at a point because a direct record carries no class
# dispersion.
DIRECT_SOLVE_HOURS = {548: 61.0}

# Years the problem had been open at resolution. Computed as a sanity check and
# never used in any human-time figure; see the note and Tao's wiki disclaimer 5.
YEAR_POSED = {1: 1931, 74: 1982, 126: 1934, 548: 1962, 571: 1974}
YEAR_RESOLVED = 2026


def anchor_hours(key):
    """people x elapsed_days x 8 h/day x on_task_fraction, at each end."""
    a = ANCHORS[key]
    base = a["people"] * a["elapsed_days"] * HOURS_PER_WORKING_DAY
    lo, c, hi = a["fraction"]
    return {"key": key, "people": a["people"],
            "elapsed_days": a["elapsed_days"], "fraction": a["fraction"],
            "person_days_x_8h": base,
            "hours_low": base * lo, "hours": base * c, "hours_high": base * hi,
            "arithmetic": "%d x %g d x %g h/d x %g = %.0f h"
                          % (a["people"], a["elapsed_days"],
                             HOURS_PER_WORKING_DAY, c, base * c),
            "measures": a["measures"], "people_basis": a["people_basis"],
            "days_basis": a["days_basis"],
            "fraction_basis": a["fraction_basis"]}


def shape_from_active(active):
    """research/attention-correction/architectures.py, OpenAI family."""
    dense = max(8, int(round((active / 196608.0) ** (1.0 / 3.0))))
    layers = max(1, int(round(dense * OPENAI_LAYER_SHARE)))
    return layers, 128 * dense


def attempt(row):
    """Counted positions and cache reads for one resolution."""
    label, cost, hours, inp, out, cread, cwrite = row
    counted = (inp + out + cwrite) * 1e6
    reads = cread * 1e6
    priced = (inp * P_INPUT + out * P_OUTPUT + cread * P_CACHE_READ
              + cwrite * P_CACHE_WRITE)
    return {"label": label, "cost_usd": cost, "working_hours": hours,
            "input": inp * 1e6, "output": out * 1e6, "cache_read": reads,
            "cache_write": cwrite * 1e6, "counted_tokens": counted,
            "priced_usd": priced, "priced_over_reported": priced / cost,
            "alpha": reads / counted}


def compute(problem):
    rows = [attempt(r) for r in RESOLUTIONS[problem]]
    counted = sum(r["counted_tokens"] for r in rows) / len(rows)
    # The row's own cache-read multiple, pooled over its resolutions.
    alpha = (sum(r["cache_read"] for r in rows)
             / sum(r["counted_tokens"] for r in rows))

    def endpoint(active, n_new):
        layers, width = shape_from_active(active)
        ctx = min(alpha * n_new, counted / 2.0, CONTEXT_CAP)
        return (2.0 * active * counted
                + 4.0 * layers * width * ctx * counted), ctx

    ctx = min(alpha * N_NEW_CENTRAL, counted / 2.0, CONTEXT_CAP)
    ratio = 2.0 * ATT_LAYERS * ATT_WIDTH * ctx / ACTIVE
    flops = 2.0 * ACTIVE * counted * (1.0 + ratio)
    low, ctx_low = endpoint(ACTIVE_LOW, N_NEW_P10)
    high, ctx_high = endpoint(ACTIVE_HIGH, N_NEW_P90)
    return {"resolutions": rows,
            "resolutions_without_tokens":
                RESOLUTIONS_WITHOUT_TOKENS.get(problem, []),
            "mean_cost_usd": sum(r["cost_usd"] for r in rows) / len(rows),
            "mean_working_hours":
                sum(r["working_hours"] for r in rows) / len(rows),
            "counted_tokens": counted, "alpha": alpha,
            "attention_context": ctx, "attention_ratio": ratio,
            "compute_flops": flops,
            "compute_flops_low": low, "compute_flops_high": high,
            "context_low": ctx_low, "context_high": ctx_high,
            "range_span": high / low}


def size_class(pages):
    return "short" if pages <= 12 else ("medium" if pages <= 60 else "large")


def human(problem):
    """The research-mathematics calibration, applied to one row."""
    lines = LEAN_LINES[problem]
    pages = lines / LINES_PER_PAPER_PAGE
    cls = size_class(pages)
    rates = HOURS_PER_PAGE[cls]
    direct = DIRECT_SOLVE_HOURS.get(problem)
    out = {"lean_lines_measured": lines,
           "pages_from_lines": pages,
           "lines_per_paper_page": LINES_PER_PAPER_PAGE,
           "size_class": cls,
           "hours_per_page": {"low": rates[0], "central": rates[1],
                              "high": rates[2]},
           "lines_per_active_hour": {"fast": LINES_PER_ACTIVE_HOUR[0],
                                     "central": LINES_PER_ACTIVE_HOUR[1],
                                     "slow": LINES_PER_ACTIVE_HOUR[2]},
           "direct_solve_hours": direct,
           "solve_basis": ("direct record: Riordan and Scott's eight-day "
                           "window on this exact argument, anchor A2 x 1.2"
                           if direct else
                           "%g h/page x %.1f pages" % (rates[1], pages))}
    for tag, hpp, rate in (("low", rates[0], LINES_PER_ACTIVE_HOUR[0]),
                           ("central", rates[1], LINES_PER_ACTIVE_HOUR[1]),
                           ("high", rates[2], LINES_PER_ACTIVE_HOUR[2])):
        solve = direct if direct else hpp * pages
        lean = lines / rate
        total = solve + lean
        out[tag] = {"solve_hours": solve, "hours_per_page": hpp,
                    "lean_lines_per_hour": rate, "lean_hours": lean,
                    "total_hours": total, "seconds": total * 3600.0,
                    "total_excluding_lean_hours": solve,
                    "seconds_excluding_lean": solve * 3600.0,
                    "person_years_2000h": total / HOURS_PER_PERSON_YEAR}
    solve_line = ("%s = %.0f h solve" % (out["solve_basis"], out["central"]["solve_hours"])
                  if direct else
                  "%d lines / %.1f = %.1f pages, %s, x %g h/page = %.0f h solve"
                  % (lines, LINES_PER_PAPER_PAGE, pages, cls, rates[1],
                     out["central"]["solve_hours"]))
    out["arithmetic"] = (
        "%s; %d lines / %.1f lines/h = %.0f h Lean; total %.0f h"
        % (solve_line, lines, LINES_PER_ACTIVE_HOUR[1],
           out["central"]["lean_hours"], out["central"]["total_hours"]))
    out["years_open_sanity_check"] = YEAR_RESOLVED - YEAR_POSED[problem]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    args = ap.parse_args()

    result = {"anchors": {k: anchor_hours(k) for k in ANCHORS},
              "prices": {"input": P_INPUT, "output": P_OUTPUT,
                         "cache_read": P_CACHE_READ,
                         "cache_write": P_CACHE_WRITE},
              "problems": {}}
    for problem in (1, 74, 126, 548, 571):
        c = compute(problem)
        h = human(problem)
        c["scenarios"] = {
            "cheapest_resolution": min(
                2.0 * ACTIVE * r["counted_tokens"] * (1.0 + c["attention_ratio"])
                for r in c["resolutions"]),
            "dearest_resolution": max(
                2.0 * ACTIVE * r["counted_tokens"] * (1.0 + c["attention_ratio"])
                for r in c["resolutions"]),
            "parameter_only_no_attention": 2.0 * ACTIVE * c["counted_tokens"],
            "cache_reads_charged_a_weights_pass":
                2.0 * ACTIVE * (c["counted_tokens"] * (1.0 + c["alpha"]))
                * (1.0 + c["attention_ratio"]),
        }
        result["problems"][str(problem)] = {
            "compute": c, "human": h,
            "flops_per_human_second":
                c["compute_flops"] / h["central"]["seconds"]}

    text = json.dumps(result, indent=1, sort_keys=True)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
