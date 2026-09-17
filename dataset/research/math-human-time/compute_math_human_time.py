#!/usr/bin/env python3
"""Derive the two calibration tables in research/math-human-time/math-human-time.md
and apply the method to the eight AI-solved rows named in the note.

Reads   research/math-human-time/solve-time.csv
        research/math-human-time/formalization.csv
Writes  agent-work/derived/math-human-time/calculations.json

Every hours figure is arithmetic on stated quantities:

  solve hours          = person_days x HOURS_PER_WORKING_DAY x on_task_fraction
  formalization hours  = author_days x HOURS_PER_ACTIVE_DAY x UNCOMMITTED_MULTIPLIER
                         (repository projects), or
                       = people x elapsed_days x HOURS_PER_WORKING_DAY x fraction
                         (projects whose commit history is a later import)

Nothing here uses years open, prize status, prize money, counts of failed prior
attempts, the field's cumulative effort, or grant totals.
"""

import csv, json, os, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(REPO, "agent-work", "derived", "math-human-time")

# DECISIONS.md: one person-year is 2,000 active hours over 250 working days.
HOURS_PER_WORKING_DAY = 8.0

# A day on which a volunteer formalizer pushes a commit is a working session, not
# a full day. 4 hours is my assumption; the band 2 to 8 is carried as a scenario.
HOURS_PER_ACTIVE_DAY = 4.0
HOURS_PER_ACTIVE_DAY_BAND = (2.0, 8.0)

# Commit-days undercount: blueprint writing, review and Zulip discussion leave no
# commit. 1.5 is my assumption; the band 1.2 to 2.5 is carried as a scenario.
UNCOMMITTED_MULTIPLIER = 1.5
UNCOMMITTED_MULTIPLIER_BAND = (1.2, 2.5)

# Carleson is the one project with both a measured blueprint .tex line count and a
# stated page count, so it fixes the conversion used for the other blueprints.
CARLESON_TEX_LINES, CARLESON_PAGES = 9778, 144
TEX_LINES_PER_PAGE = CARLESON_TEX_LINES / CARLESON_PAGES


def read(name):
    with open(os.path.join(HERE, name), newline="") as f:
        return list(csv.DictReader(f))


def num(s):
    s = (s or "").strip()
    return float(s) if s else None


# ---------------------------------------------------------------- table 1

solve = read("solve-time.csv")
for r in solve:
    r["person_days"] = num(r["person_days"])
    r["elapsed_days"] = num(r["elapsed_days"])
    r["people"] = num(r["people"])
    r["on_task_fraction"] = num(r["on_task_fraction"])
    r["pages"] = num(r["pages"])
    r["active_hours"] = r["person_days"] * HOURS_PER_WORKING_DAY * r["on_task_fraction"]
    # The elapsed bound: the same window at an on-task fraction of one.
    r["elapsed_bound_hours"] = r["person_days"] * HOURS_PER_WORKING_DAY
    r["hours_per_page"] = (r["active_hours"] / r["pages"]) if r["pages"] else None

fit = [r for r in solve if r["used_in_fit"] == "yes"]
by_class = {}
for cls in ("short", "medium", "large"):
    rows = [r for r in fit if r["size_class"] == cls]
    hpp = sorted(r["hours_per_page"] for r in rows if r["hours_per_page"])
    hrs = sorted(r["active_hours"] for r in rows)
    by_class[cls] = {
        "n_rows": len(rows),
        "n_with_pages": len(hpp),
        "hours_per_page_median": round(st.median(hpp), 1) if hpp else None,
        "hours_per_page_min": round(min(hpp), 1) if hpp else None,
        "hours_per_page_max": round(max(hpp), 1) if hpp else None,
        "hours_per_page_dispersion": round(max(hpp) / min(hpp), 1) if hpp else None,
        "total_hours_median": round(st.median(hrs)),
        "total_hours_min": round(min(hrs)),
        "total_hours_max": round(max(hrs)),
        "total_hours_dispersion": round(max(hrs) / min(hrs), 1),
    }

unassisted = [r for r in fit if r["assisted"] == "no"]
assisted = [r for r in fit if r["assisted"] == "ai"]
direct = [r for r in fit if r["record_type"] == "direct"]
timeline = [r for r in fit if r["record_type"] == "timeline"]

# Does people count, or pages, predict hours better? Report both correlations on
# logs, which is the scale the figures span.
import math
def logcorr(xs, ys):
    xs = [math.log(x) for x in xs]; ys = [math.log(y) for y in ys]
    mx, my = st.mean(xs), st.mean(ys)
    num_ = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    den = math.sqrt(sum((a - mx) ** 2 for a in xs) * sum((b - my) ** 2 for b in ys))
    return round(num_ / den, 2)

with_pages = [r for r in fit if r["pages"]]
predictors = {
    "log pages vs log hours": logcorr([r["pages"] for r in with_pages],
                                      [r["active_hours"] for r in with_pages]),
    "log people vs log hours": logcorr([r["people"] for r in fit],
                                       [r["active_hours"] for r in fit]),
    "log elapsed days vs log hours": logcorr([r["elapsed_days"] for r in fit],
                                             [r["active_hours"] for r in fit]),
}

table1 = {
    "n_rows_total": len(solve),
    "n_in_fit": len(fit),
    "n_reported_not_used": len(solve) - len(fit),
    "n_direct_records": len(direct),
    "n_timeline_only": len(timeline),
    "n_unassisted": len(unassisted),
    "n_ai_assisted": len(assisted),
    "hours_min": round(min(r["active_hours"] for r in fit)),
    "hours_max": round(max(r["active_hours"] for r in fit)),
    "median_unassisted_hours": round(st.median([r["active_hours"] for r in unassisted])),
    "median_ai_assisted_hours": round(st.median([r["active_hours"] for r in assisted])),
    "by_class": by_class,
    "predictors_log_correlation": predictors,
    "rows": [
        {k: r[k] for k in ("key", "problem", "area", "character", "size_class",
                           "people", "elapsed_days", "person_days",
                           "on_task_fraction", "fraction_basis", "pages",
                           "record_type", "assisted", "used_in_fit")}
        | {"active_hours": round(r["active_hours"]),
           "elapsed_bound_hours": round(r["elapsed_bound_hours"]),
           "hours_per_page": round(r["hours_per_page"], 1) if r["hours_per_page"] else None}
        for r in solve
    ],
}

# ---------------------------------------------------------------- table 2

form = read("formalization.csv")
for r in form:
    for k in ("paper_pages", "blueprint_pages", "formal_lines", "formal_lines_for_rate", "author_days",
              "elapsed_days", "people_for_fraction", "on_task_fraction", "contributors"):
        r[k] = num(r[k])
    if r["hours_method"] == "author_days":
        r["active_hours"] = r["author_days"] * HOURS_PER_ACTIVE_DAY * UNCOMMITTED_MULTIPLIER
        r["active_hours_low"] = r["author_days"] * HOURS_PER_ACTIVE_DAY_BAND[0] * UNCOMMITTED_MULTIPLIER_BAND[0]
        r["active_hours_high"] = r["author_days"] * HOURS_PER_ACTIVE_DAY_BAND[1] * UNCOMMITTED_MULTIPLIER_BAND[1]
    elif r["hours_method"] == "fraction":
        r["active_hours"] = (r["people_for_fraction"] * r["elapsed_days"]
                             * HOURS_PER_WORKING_DAY * r["on_task_fraction"])
        r["active_hours_low"] = r["active_hours"] / 2
        r["active_hours_high"] = r["active_hours"] * 2
    else:
        r["active_hours"] = None
        r["active_hours_low"] = r["active_hours_high"] = None
    r["lines_per_active_hour"] = (r["formal_lines_for_rate"] / r["active_hours"]
                                  if r["formal_lines_for_rate"] and r["active_hours"] else None)
    r["lines_per_paper_page"] = (r["formal_lines"] / r["paper_pages"]
                                 if r["formal_lines"] and r["paper_pages"] else None)
    r["lines_per_blueprint_page"] = (r["formal_lines"] / r["blueprint_pages"]
                                     if r["formal_lines"] and r["blueprint_pages"] else None)
    r["hours_per_paper_page"] = (r["active_hours"] / r["paper_pages"]
                                 if r["active_hours"] and r["paper_pages"] else None)
    r["hours_per_blueprint_page"] = (r["active_hours"] / r["blueprint_pages"]
                                     if r["active_hours"] and r["blueprint_pages"] else None)

ffit = [r for r in form if r["used_in_fit"] == "yes"]
pfit = [r for r in form if r["used_in_page_fit"] == "yes"]
def spread(vals):
    vals = sorted(v for v in vals if v)
    if not vals:
        return None
    return {"n": len(vals), "min": round(min(vals), 1), "median": round(st.median(vals), 1),
            "max": round(max(vals), 1), "dispersion": round(max(vals) / min(vals), 1)}

table2 = {
    "n_projects": len(form),
    "n_in_fit": len(ffit),
    "tex_lines_per_page": round(TEX_LINES_PER_PAGE, 1),
    "lines_per_active_hour": spread([r["lines_per_active_hour"] for r in ffit]),
    "lines_per_paper_page": spread([r["lines_per_paper_page"] for r in pfit]),
    "lines_per_blueprint_page": spread([r["lines_per_blueprint_page"] for r in pfit]),
    "hours_per_paper_page": spread([r["hours_per_paper_page"] for r in pfit]),
    "hours_per_blueprint_page": spread([r["hours_per_blueprint_page"] for r in pfit]),
    "rows": [
        {k: r[k] for k in ("key", "project", "system", "paper_pages", "blueprint_pages",
                           "formal_lines", "formal_lines_for_rate", "contributors",
                           "author_days", "elapsed_days", "hours_method", "used_in_fit",
                           "used_in_page_fit")}
        | {"active_hours": round(r["active_hours"]) if r["active_hours"] else None,
           "active_hours_low": round(r["active_hours_low"]) if r["active_hours_low"] else None,
           "active_hours_high": round(r["active_hours_high"]) if r["active_hours_high"] else None,
           "lines_per_active_hour": round(r["lines_per_active_hour"], 1) if r["lines_per_active_hour"] else None,
           "lines_per_paper_page": round(r["lines_per_paper_page"]) if r["lines_per_paper_page"] else None,
           "lines_per_blueprint_page": round(r["lines_per_blueprint_page"]) if r["lines_per_blueprint_page"] else None,
           "hours_per_paper_page": round(r["hours_per_paper_page"]) if r["hours_per_paper_page"] else None,
           "hours_per_blueprint_page": round(r["hours_per_blueprint_page"]) if r["hours_per_blueprint_page"] else None}
        for r in form
    ],
}

# The Imperial FLT head-count-versus-grant comparison, which the note reports on
# its own because it is the one place a funded FTE and an observed work record
# can be put side by side.
FLT = next(r for r in form if r["key"] == "flt-imperial")
GRANT_TOTAL_GBP, GRANT_YEARS = 934043.0, 5.0
GRANT_FEC_PER_FTE = (93000.0, 125000.0)   # UK full economic cost per FTE, my band
funded_fte = (GRANT_TOTAL_GBP / GRANT_YEARS / GRANT_FEC_PER_FTE[1],
              GRANT_TOTAL_GBP / GRANT_YEARS / GRANT_FEC_PER_FTE[0])
funded_years_elapsed = (2026 + 259 / 365) - (2024 + 244 / 365)   # Sep 2024 to 16 Sep 2026
flt_check = {
    "author_days": FLT["author_days"],
    "buzzard_author_days": 302,
    "non_bot_commits": 1571,
    "bot_commits": 133,
    "non_bot_authors": 73,
    "observed_active_hours": round(FLT["active_hours"]),
    "observed_person_years_at_2000h": round(FLT["active_hours"] / 2000, 2),
    "grant_gbp_per_year": round(GRANT_TOTAL_GBP / GRANT_YEARS),
    "funded_fte_band": [round(funded_fte[0], 2), round(funded_fte[1], 2)],
    "funded_years_elapsed": round(funded_years_elapsed, 2),
    "funded_person_years_band": [round(funded_fte[0] * funded_years_elapsed, 1),
                                 round(funded_fte[1] * funded_years_elapsed, 1)],
    "funded_hours_band": [round(funded_fte[0] * funded_years_elapsed * 2000),
                          round(funded_fte[1] * funded_years_elapsed * 2000)],
}
flt_check["grant_overstates_by"] = [
    round(flt_check["funded_hours_band"][0] / flt_check["observed_active_hours"], 2),
    round(flt_check["funded_hours_band"][1] / flt_check["observed_active_hours"], 2)]
table2["flt_headcount_vs_grant"] = flt_check

# ---------------------------------------------------------------- the method applied

RATE = {c: by_class[c]["hours_per_page_median"] for c in by_class}
LINES_PER_HOUR = table2["lines_per_active_hour"]["median"]
LINES_PER_PAPER_PAGE = table2["lines_per_paper_page"]["median"]
LINES_PER_BLUEPRINT_PAGE = table2["lines_per_blueprint_page"]["median"]


def size_class(pages):
    return "short" if pages <= 12 else ("medium" if pages <= 60 else "large")


def apply_method(key, current, *, pages=None, lines=None, source_pages=None,
                 source_kind="paper", direct_solve_hours=None, formalization_only=False,
                 note=""):
    """pages: written mathematics the human must produce, in research-paper pages.
    If only a Lean artifact exists, pages is estimated from its line count at the
    table-2 research-paper ratio. lines: human-idiom Lean lines to be written."""
    est_from_lines = None
    if pages is None and lines is not None:
        pages = lines / LINES_PER_PAPER_PAGE
        est_from_lines = True
    cls = size_class(pages)
    if formalization_only:
        solve_h = 0.0
    elif direct_solve_hours is not None:
        solve_h = direct_solve_hours
    else:
        solve_h = RATE[cls] * pages
    if lines is None and source_pages is not None:
        per = LINES_PER_PAPER_PAGE if source_kind == "paper" else LINES_PER_BLUEPRINT_PAGE
        lines = source_pages * per
    lean_h = (lines / LINES_PER_HOUR) if lines else 0.0
    total = solve_h + lean_h
    return {
        "key": key,
        "pages": round(pages, 1),
        "pages_estimated_from_lines": bool(est_from_lines),
        "size_class": cls,
        "class_rate_hours_per_page": RATE[cls],
        "solve_hours": round(solve_h),
        "solve_basis": ("no solve term: the mathematics already exists" if formalization_only
                        else ("direct record" if direct_solve_hours is not None
                              else f"{RATE[cls]} h/page x {round(pages,1)} pages")),
        "human_idiom_lean_lines": round(lines) if lines else 0,
        "lean_hours": round(lean_h),
        "lean_basis": f"{round(lines) if lines else 0} lines / {LINES_PER_HOUR} lines per active hour",
        "method_hours": round(total),
        "current_row_hours": current,
        "ratio_to_current": round(total / current, 2),
        "note": note,
    }


worked = [
    apply_method("reas-erdos1-astra", 194, lines=2427,
                 note="No paper exists; pages estimated from the measured 2,427-line Lean artifact."),
    apply_method("reas-erdos74-astra", 158, lines=2516,
                 note="Six independent resolutions exist; the primary module is 2,516 lines."),
    apply_method("reas-erdos126-astra", 175, lines=3058,
                 note="Four independent resolutions; the primary module is 3,058 lines."),
    apply_method("reas-erdos548-astra", 101, lines=1243, direct_solve_hours=61,
                 note="Riordan and Scott's eight-day window on this exact argument is a direct "
                      "record and supersedes the class rate; the FrontierMath note's 51 h anchor "
                      "times its 1.2 multiplier is kept."),
    apply_method("reas-erdos571-astra", 563, lines=10390,
                 note="10,390 lines, four times any other of the five; Bloom judges it the hardest."),
    apply_method("reas-navier-stokes-openai", 13825, pages=166, source_pages=166,
                 source_kind="paper",
                 note="166-page analytic proof plus a Lean formalization. The formalization term "
                      "is sized from the paper rather than from the delivered 429,279-line "
                      "machine subtree."),
    apply_method("reas-lean-textbook-algcomb-opus45", 12000, pages=500,
                 source_pages=500, source_kind="blueprint", formalization_only=True,
                 note="Grinberg's textbook is 703 pages, of which about 500 are main text. A "
                      "textbook is blueprint-grade prose, so the blueprint line ratio applies."),
]

# FLT cannot be priced from a page count: no informal paper exists and the Imperial
# blueprint covers only the reduction. It is priced by scaling the one project
# aimed at the same deliverable, which is table 2's own flt-imperial row.
IMPERIAL_FRACTION_DONE = 0.55       # my assumption: 70 sorries open against 2,014 declarations,
                                    # and PROOF-PATH.md's restricted forms; the reduction is
                                    # roughly half delivered at 2.83 years of a 5-year plan
REMAINDER_MULTIPLIER = 2.5          # unchanged from research/flt-anthropic.md
flt_plan_hours = FLT["active_hours"] / IMPERIAL_FRACTION_DONE
flt_total = flt_plan_hours * (1 + REMAINDER_MULTIPLIER)
worked.insert(6, {
    "key": "reas-flt-lean-anthropic-internal",
    "pages": None, "pages_estimated_from_lines": False, "size_class": "large",
    "class_rate_hours_per_page": None,
    "solve_hours": round(flt_plan_hours),
    "solve_basis": f"{round(FLT['active_hours'])} observed active hours / {IMPERIAL_FRACTION_DONE} "
                   f"fraction of the reduction delivered = the whole reduction",
    "human_idiom_lean_lines": None,
    "lean_hours": round(flt_total - flt_plan_hours),
    "lean_basis": f"remainder multiplier {REMAINDER_MULTIPLIER} on the reduction, per research/flt-anthropic.md",
    "method_hours": round(flt_total),
    "current_row_hours": 84000,
    "ratio_to_current": round(flt_total / 84000, 2),
    "note": "Priced by scaling the Imperial project's observed work record rather than its "
            "funded head-count. The whole change from the current 84,000 is that the "
            "observed record is smaller than the grant implies.",
})

result = {
    "constants": {
        "hours_per_working_day": HOURS_PER_WORKING_DAY,
        "hours_per_active_day": HOURS_PER_ACTIVE_DAY,
        "hours_per_active_day_band": list(HOURS_PER_ACTIVE_DAY_BAND),
        "uncommitted_multiplier": UNCOMMITTED_MULTIPLIER,
        "uncommitted_multiplier_band": list(UNCOMMITTED_MULTIPLIER_BAND),
        "tex_lines_per_page": round(TEX_LINES_PER_PAGE, 1),
    },
    "table1_solve_time": table1,
    "table2_formalization": table2,
    "method_rates": {
        "hours_per_page_by_class": RATE,
        "formal_lines_per_active_hour": LINES_PER_HOUR,
        "formal_lines_per_paper_page": LINES_PER_PAPER_PAGE,
        "formal_lines_per_blueprint_page": LINES_PER_BLUEPRINT_PAGE,
    },
    "worked_rows": worked,
}

os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "calculations.json"), "w") as f:
    json.dump(result, f, indent=2, sort_keys=False)

# console summary
print(f"table 1: {table1['n_rows_total']} rows, {table1['n_in_fit']} in fit, "
      f"{table1['n_direct_records']} direct records")
for c, v in by_class.items():
    print(f"  {c:7s} n={v['n_rows']:2d}  h/page median {v['hours_per_page_median']}"
          f"  ({v['hours_per_page_min']} to {v['hours_per_page_max']}, x{v['hours_per_page_dispersion']})"
          f"  total hours median {v['total_hours_median']}"
          f" ({v['total_hours_min']} to {v['total_hours_max']}, x{v['total_hours_dispersion']})")
print("  predictors:", predictors)
print(f"table 2: {table2['n_projects']} projects, {table2['n_in_fit']} in fit")
for k in ("lines_per_active_hour", "lines_per_paper_page", "lines_per_blueprint_page",
          "hours_per_paper_page", "hours_per_blueprint_page"):
    print(f"  {k:26s} {table2[k]}")
print("  FLT:", json.dumps(flt_check))
print("worked rows:")
for w in worked:
    print(f"  {w['key']:38s} method {w['method_hours']:7d}  current {w['current_row_hours']:7d}"
          f"  x{w['ratio_to_current']}")
print("wrote", os.path.join(OUT, "calculations.json"))
