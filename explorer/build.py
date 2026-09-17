"""Build explorer/index.html from dataset/.

Reads dataset/points.csv and dataset/models.csv, writes one self-contained
static page with the whole dataset embedded. No network, no libraries, no deps.

    python3 explorer/build.py

Columns with few distinct values are dictionary-encoded so the page stays small;
free text is embedded as written. Every stored enum value gets a short label —
the page never shows a reader a column name or a raw token.
"""

import csv
import datetime
import json
import os
import re
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
DATASET = os.path.join(HERE, "..", "dataset")
BLOB = "https://github.com/damonbinder/ai-compute-vs-human-time/blob/main/dataset/"

# Colour slots before a dimension folds its smallest values into "Other".
# Eight is where hues stop being reliably separable on a scatter, so the long
# tails — developers, source collections — fold there. Task category is a
# closed set of ten that Damon wants shown whole, and takes two extra hues.
MAX_SLOTS = 8
CATEGORY_SLOTS = 10

LABELS = {
    "point_id": "ID",
    "task": "Task",
    "task_category": "Category",
    "task_description": "Description",
    "model_id": "Model",
    "compute_scope": "Compute scope",
    "compute_flops": "Compute (FLOP)",
    "human_skill": "Human skill",
    "human_time_scope": "Human time covers",
    "human_time": "Human time (s)",
    "performance_vs_human": "Performance vs human",
    "comparison_issues": "Comparison issues",
    "compute_evidence": "Compute evidence",
    "human_time_evidence": "Human-time evidence",
    "performance_evidence": "Performance evidence",
    "human_time_statistic": "Human-time statistic",
    "human_time_subset": "Human-time subset",
    "human_attempts": "Human attempts",
    "human_time_source": "Human-time source",
    "compute_method": "Compute method",
    "compute_statistic": "Compute statistic",
    "compute_subset": "Compute subset",
    "ai_attempts": "AI attempts",
    "compute_source": "Compute source",
    "tokens": "Tokens",
    "tokens_accounting": "Tokens counted",
    "source_dataset": "Source collection",
    "source_record": "Source record",
    "notes": "Notes",
    "compute_flops_low": "Compute, low",
    "compute_flops_high": "Compute, high",
    "human_time_low": "Human time, low",
    "human_time_high": "Human time, high",
    "task_id": "Task ID",
    "frontier": "Frontier",
    "attention_context": "Attended context",
    "attention_ratio": "Attention share",
    # Price, not cost: both bases are what a provider charges, margin included.
    "ai_cost_usd": "AI price (USD)",
    "ai_cost_basis": "Price basis",
    "ai_cost_date": "Price date",
    "human_cost_usd": "Human price (USD)",
    "human_cost_basis": "Human price basis",
}

# Terse. A reader gets a label, not a sentence.
ENUMS = {
    "task_category": {
        "research_analysis": "Research and analysis", "coding": "Software",
        "mathematics_puzzles": "Maths and puzzles",
        "administrative_operational": "Administrative",
        "writing_media": "Writing and media", "games": "Games",
        "skill_acquisition": "Learning a skill", "perception": "Perception",
        "physical_tasks": "Physical tasks", "memory_recall": "Memory and recall",
    },
    # Three labels since 2026-09-15: far_above and unknown are retired.
    "performance_vs_human": {
        "below": "Worse", "match": "Comparable", "above": "Better",
    },
    "compute_scope": {
        "inference": "Inference", "additional_training": "Further training",
        "full_training": "Training from scratch",
    },
    "human_skill": {
        "novice": "Novices", "typical": "Ordinary people", "expert": "Experts",
        "world_class": "World-class",
    },
    "human_time_scope": {
        "task_performance": "Doing the task", "skill_acquisition": "Learning the task",
    },
    "compute_evidence": {
        "measured_operations": "Operations measured",
        "derived_supported_inputs": "From reported inputs",
        "derived_assumed_inputs": "From an assumed input",
        "transferred_workload": "Workload borrowed", "unknown": "Not established",
    },
    "human_time_evidence": {
        "task_timings": "People timed",
        "defined_duration": "Fixed by the work unit",
        "source_estimate": "Source estimate",
        "llm_estimate_from_data": "Our estimate, from timings",
        "llm_estimate_judgment": "Our estimate, by judgment",
    },
    "human_time_statistic": {
        "mean": "Mean", "median": "Median", "geometric_mean": "Geometric mean",
        "median_of_task_medians": "Median of task medians",
        "point_estimate": "Point estimate",
    },
    "compute_statistic": {
        "mean": "Mean", "median": "Median", "total": "Total for the work unit",
        "total_per_completed_sample": "Total per completed sample",
        "point_estimate": "Point estimate",
    },
    "human_time_subset": {
        "all": "All attempts", "successful": "Successful only",
        "not_applicable": "No selection",
    },
    "compute_subset": {
        "all": "All attempts", "successful": "Successful only",
        "positive_tokens": "Positive token counts", "not_applicable": "No selection",
    },
    "compute_method": {
        "reported": "Reported", "params_tokens": "Tokens times FLOP per token",
        "operation_count": "Operation count", "hardware_time": "Hardware time",
    },
    "tokens_accounting": {
        "training": "Training tokens", "source_total": "Source total",
        "input_output": "Input and output",
        "input_cache_creation_output": "Input, cache creation, output",
        "encoder_processed": "Encoder positions",
        "decoder_processed": "Decoder positions", "not_applicable": "None",
    },
    "comparison_issues": {
        "none_identified": "None identified", "different_task": "Different task",
        "different_inputs_or_tools": "Different inputs or tools",
        "different_assessment": "Different assessment",
        "different_human_baseline": "Different human baseline",
        "different_attempt_selection": "Different attempt selection",
    },
    "ai_cost_basis": {
        "reported": "Reported", "list_price": "List price",
        "not_available": "Not available",
    },
    # Columns that hold a count or a token, so the token needs a label too.
    "human_attempts": {"not_applicable": "Not applicable"},
    "ai_attempts": {"not_applicable": "Not applicable"},
    "tokens": {"not_applicable": "Not applicable"},
    "human_cost_basis": {
        "reported_payment": "Worker payment", "reported_price": "Client price",
        "not_available": "Not available",
    },
}

MODEL_COLS = ["model", "company", "model_release_date", "flops_per_token",
              "active_parameters", "active_parameters_basis", "parameter_source",
              "notes"]
MODEL_LABELS = ["Model", "Developer", "Released", "FLOP per token",
                "Active parameters", "Parameter basis", "Parameter source",
                "Model notes"]

# Long free text: shown full width in the record, not in the field grid.
WIDE = ["task_description", "performance_evidence", "notes", "human_time_source",
        "compute_source", "source_record"]


def read_csv(name):
    # The dataset files are CRLF; newline='' hands the parser the endings intact.
    with open(os.path.join(DATASET, name), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


points = read_csv("points.csv")
models_raw = read_csv("models.csv")
COLS = list(points[0].keys())

missing = sorted({r["model_id"] for r in points} - {m["model_id"] for m in models_raw})
if missing:
    print("  WARNING: model_id(s) not in the registry: %s" % missing[:5])

# Dictionary-encode any column repetitive enough to pay for the indirection.
enc, index = {}, {}
for c in COLS:
    counts = Counter(r[c] for r in points)
    if len(counts) <= len(points) / 4:
        vals = [v for v, _ in counts.most_common()]
        enc[c] = vals
        index[c] = {v: i for i, v in enumerate(vals)}

rows = [[index[c][r[c]] if c in index else r[c] for c in COLS] for r in points]


def year_bucket(date):
    """Release year, everything to 2020 in one step: 42 points across eight
    years, against 482 in 2026 alone."""
    y = (date or "").strip()[:4]
    if not y.isdigit():
        return "Unknown"
    return "2020 or earlier" if int(y) <= 2020 else y


def issue_count(cell):
    """How many comparison differences the row declares. none_identified means
    the comparison was reviewed and nothing material found, which is zero."""
    cell = (cell or "").strip()
    if not cell:
        return "Not assessed"
    if cell == "none_identified":
        return "None identified"
    n = len([x for x in cell.split(";") if x.strip()])
    return "One issue" if n == 1 else "%d issues" % n


def dimension(name, values, order=None, ramp=False, slots=MAX_SLOTS):
    """One colour-and-filter dimension: its value labels and a per-row index."""
    counts = Counter(values)
    if order:
        keep = [v for v in order if v in counts][:slots]
    else:
        keep = [v for v, _ in counts.most_common(slots)]
    rest = set(counts) - set(keep)
    labels = keep + (["Other"] if rest else [])
    idx = {v: (len(keep) if v in rest else keep.index(v)) for v in counts}
    out = {"name": name, "values": labels, "idx": [idx[v] for v in values]}
    if rest:
        out["other"] = len(keep)
    if ramp:
        out["ramp"] = True
    return out


def labelled(col):
    return [ENUMS[col][r[col]] for r in points]


def ordered(col):
    return list(ENUMS[col].values())


models = {m["model_id"]: m for m in models_raw}
companies = [models.get(r["model_id"], {}).get("company") or "Unknown" for r in points]

dims = [
    dimension("Task category", labelled("task_category"), ordered("task_category"),
              slots=CATEGORY_SLOTS),
    dimension("Performance vs human", labelled("performance_vs_human"),
              ordered("performance_vs_human")),
    dimension("Compute scope", labelled("compute_scope"),
              ordered("compute_scope")),
    dimension("Human skill", labelled("human_skill"), ordered("human_skill")),
    dimension("Compute evidence", labelled("compute_evidence"),
              ordered("compute_evidence")),
    dimension("Human-time evidence", labelled("human_time_evidence"),
              ordered("human_time_evidence")),
    dimension("Model release year",
              [year_bucket(models.get(r["model_id"], {}).get("model_release_date"))
               for r in points],
              ["2020 or earlier", "2021", "2022", "2023", "2024", "2025", "2026",
               "Unknown"], ramp=True),
    dimension("Comparison issues",
              [issue_count(r["comparison_issues"]) for r in points],
              ["None identified", "One issue", "2 issues", "3 issues",
               "4 issues", "5 issues", "Not assessed"],
              ramp=True),
    dimension("Developer", companies),
    dimension("Source collection", [r["source_dataset"] for r in points]),
]


def asserted_range(row, central, low, high):
    """The row's own bounds on a value, as factors either side of the central.

    Both ranges are asserted per row, not scaled from a default: the compute
    bounds are recomputed through the row's own recipe, the human bounds
    transcribed from the alternatives its research note argues. Factors are
    what the page draws with, since every axis derived from a value scales the
    same way.
    """
    def f(key):
        try:
            return float((row.get(key) or "").strip())
        except ValueError:
            return None
    c, lo, hi = f(central), f(low), f(high)
    if not c or not lo or not hi:
        return None
    return [round(lo / c, 4), round(hi / c, 4)]


def epoch(text):
    text = (text or "").strip()
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", text):
        return None
    y, m, d = (int(x) for x in text.split("-"))
    return (datetime.date(y, m, d) - datetime.date(1970, 1, 1)).days


def label_of(col):
    """A column added to the spec since this file was last touched still gets a
    readable label rather than failing the build."""
    if col in LABELS:
        return LABELS[col]
    print("  note: no label for %r, using a derived one" % col)
    return col.replace("_", " ").capitalize()


payload = {
    "cols": COLS,
    "enc": enc,
    "rows": rows,
    "labels": [label_of(c) for c in COLS],
    "enums": {c: ENUMS[c] for c in ENUMS},
    "wide": WIDE,
    "dims": dims,
    "models": {m["model_id"]: [m.get(k, "") for k in MODEL_COLS] for m in models_raw},
    "modelLabels": MODEL_LABELS,
    "release": [epoch(models.get(r["model_id"], {}).get("model_release_date"))
                for r in points],
    "range": [asserted_range(r, "compute_flops", "compute_flops_low",
                              "compute_flops_high") for r in points],
    "timeRange": [asserted_range(r, "human_time", "human_time_low",
                                 "human_time_high") for r in points],
    "blob": BLOB,
}

with open(os.path.join(HERE, "template.html"), encoding="utf-8") as f:
    html = f.read()
html = html.replace("__DATA__", json.dumps(payload, separators=(",", ":")))
html = html.replace("__NPOINTS__", "{:,}".format(len(points)))

out = os.path.join(HERE, "index.html")
with open(out, "w", encoding="utf-8") as f:
    f.write(html)
print("wrote %s (%.0f KB, %d points, %d encoded columns)"
      % (out, len(html) / 1024, len(points), len(enc)))
