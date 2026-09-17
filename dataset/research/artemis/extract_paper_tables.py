#!/usr/bin/env python3
"""Extract the ARTEMIS paper's plain text, Table 1 and Appendix B from the retained arXiv HTML.

Reads only the retained HTML; writes new files into --outdir. Nothing in agent-work/sources/ is modified.

Usage:
    python3 extract_paper_tables.py \
        --html agent-work/sources/artemis/artemis-2512.09882v2.html \
        --outdir /tmp/artemis-extract

Dependencies: Python 3.9+ standard library only.

Outputs
    paper-text.txt            one stripped line per HTML text node
    table1-scores.csv         Table 1, one row per participant or agent configuration
    appendix-b-findings.csv   Appendix B, one row per submitted finding
    reconstruction.json       per-ID aggregates rebuilt from Appendix B, against Table 1
"""
import argparse
import csv
import html
import json
import re
from collections import OrderedDict
from pathlib import Path

SEVERITY_WEIGHT = {"C": 8, "H": 5, "M": 3, "L": 2, "I": 1}

# Table 1 column order, read left to right off the rendered table.
TABLE1_IDS = ["P1", "A2", "P2", "P4", "P5", "P3", "A1", "P8", "P9", "P10",
              "CO", "P6", "P7", "CS", "CG"]
TABLE1_ROWS = ["Total Findings", "Valid %", "Severity Score", "Complexity Score", "Total Score"]


def html_to_lines(path: Path):
    raw = path.read_text(encoding="utf-8", errors="replace")
    raw = re.sub(r"(?s)<(script|style).*?</\1>", " ", raw)
    raw = re.sub(r"(?s)<!--.*?-->", " ", raw)
    raw = re.sub(r"(?s)<[^>]+>", "\n", raw)
    raw = html.unescape(raw)
    return [ln.strip() for ln in raw.split("\n") if ln.strip()]


def extract_table1(lines):
    """Table 1 is rendered as a flat run: the 15 column labels, then each statistic row."""
    start = next(i for i, ln in enumerate(lines) if ln == "Participant")
    window = lines[start + 1:start + 400]
    values = OrderedDict()
    for label in TABLE1_ROWS:
        j = window.index(label)
        cells = []
        k = j + 1
        while len(cells) < len(TABLE1_IDS):
            cell = window[k]
            if re.fullmatch(r"-?[\d.]+%?", cell):
                cells.append(cell)
            k += 1
        values[label] = cells
    out = []
    for n, ident in enumerate(TABLE1_IDS):
        row = {"id": ident}
        for label in TABLE1_ROWS:
            key = label.lower().replace(" ", "_").replace("%", "pct")
            row[key] = values[label][n].rstrip("%")
        out.append(row)
    return out


def extract_appendix_b(lines):
    start = lines.index("Appendix B")
    end = next(i for i, ln in enumerate(lines)
               if i > start and "Participant Instructions and Scope" in ln)
    block = lines[start:end]
    i = block.index("Title") + 1
    fields = ["id", "valid", "severity", "orig_severity", "dc", "ec", "pc", "title"]
    recs = []
    while i + 8 <= len(block):
        recs.append(dict(zip(fields, block[i:i + 8])))
        i += 8
    return recs


def reconstruct(findings, table1):
    agg = {}
    for rec in findings:
        a = agg.setdefault(rec["id"], {"submitted": 0, "valid": 0, "severity_score": 0,
                                       "dc_plus_ec": 0.0})
        a["submitted"] += 1
        if rec["valid"] == "V":
            a["valid"] += 1
            a["severity_score"] += SEVERITY_WEIGHT.get(rec["severity"], 0)
            try:
                a["dc_plus_ec"] += float(rec["dc"]) + float(rec["ec"])
            except ValueError:
                pass
    # Appendix B labels the Codex baseline A0; Table 1 calls it CO.
    alias = {"A0": "CO", "1": "P1", "2": "P2", "3": "P3", "4": "P4", "5": "P5",
             "6": "P6", "7": "P7", "8": "P8", "9": "P9", "10": "P10"}
    agg = {alias.get(k, k): v for k, v in agg.items()}
    t1 = {r["id"]: r for r in table1}
    out = {}
    for ident, a in agg.items():
        published = t1[ident]
        out[ident] = {
            "appendix_b": a,
            "table1_severity_score": float(published["severity_score"]),
            "severity_matches": float(published["severity_score"]) == a["severity_score"],
            "table1_complexity_score": float(published["complexity_score"]),
            "dc_plus_ec_minus_complexity": round(a["dc_plus_ec"] - float(published["complexity_score"]), 4),
            "implied_verification_only_ec": round(
                (a["dc_plus_ec"] - float(published["complexity_score"])) / 1.2, 4),
        }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", required=True, type=Path)
    ap.add_argument("--outdir", required=True, type=Path)
    args = ap.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)

    lines = html_to_lines(args.html)
    (args.outdir / "paper-text.txt").write_text("\n".join(lines), encoding="utf-8")

    table1 = extract_table1(lines)
    with (args.outdir / "table1-scores.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(table1[0]))
        w.writeheader()
        w.writerows(table1)

    findings = extract_appendix_b(lines)
    with (args.outdir / "appendix-b-findings.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(findings[0]))
        w.writeheader()
        w.writerows(findings)

    (args.outdir / "reconstruction.json").write_text(
        json.dumps(reconstruct(findings, table1), indent=1, sort_keys=True), encoding="utf-8")

    print(f"lines={len(lines)} table1_rows={len(table1)} findings={len(findings)}")


if __name__ == "__main__":
    main()
