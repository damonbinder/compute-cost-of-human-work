#!/usr/bin/env python3
"""Recover the bar geometry of three histograms in the Remote Labor Index paper.

The RLI paper (arXiv:2510.26787v1) publishes no table of per-deliverable API
costs and no table of per-project human completion times. The only record of
either is a rendered histogram. All three histograms are vector graphics, so the
bar rectangles and the axis tick marks survive in the PDF content stream and the
underlying counts can be read back exactly.

Panels recovered:

  fig12_costs        page 20, "Distribution of Model Running Costs" - the API
                     cost of one AI deliverable, pooled across agents
  fig4_cost          page 5 left, "Project Costs"
  fig4_time          page 5 right, "Project Completion Times"

Output is a JSON file of bar edges, bar tops, per-bar clip rectangles and axis
calibration points in the figures' own device space, which `price_to_flops.py`
then turns into counts and summary statistics without needing the PDF. This
script is the step that needs the PDF; it is retained so the extraction can be
repeated, not so it has to be.

The clip rectangles matter. A histogram bin of count zero is drawn as a
zero-height rectangle that carries no fill path, so it is invisible to a scan of
the drawn bars but still leaves a clip rectangle in `<defs>`. The completion-time
panel has three such bins; without them its bin grid looks shorter than it is.

Dependencies: Python 3 standard library, plus the `pdftocairo` binary from
Poppler (tested with Poppler 25.x). No Python packages.

Usage:

    python3 research/remote-labor-index/extract_figure_bars.py \\
        --pdf /path/to/2510.26787v1.pdf \\
        --out agent-work/sources/remote-labor-index/figure-bar-geometry.json
"""

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

# Matplotlib's default first colour, which every bar in these three panels uses.
BAR_FILL = "rgb(25.4"

PANELS = {
    "fig12_costs": {
        "page": 20,
        "description": 'Figure 12, "Distribution of Model Running Costs"',
        "x_range": (0.0, 1e9),
        "printed_stats": {"min": 0.03, "mean": 2.34, "median": 0.92, "max": 29.51},
        "x_axis": "log10 USD",
        "y_axis": "count of AI deliverables",
    },
    "fig4_cost": {
        "page": 5,
        "description": 'Figure 4 left, "Project Costs"',
        "x_range": (0.0, 600.0),
        "printed_stats": {"min": 9.0, "mean": 632.6, "median": 200.0, "max": 22500.0},
        "x_axis": "log10 USD",
        "y_axis": "count of projects",
    },
    "fig4_time": {
        "page": 5,
        "description": 'Figure 4 right, "Project Completion Times"',
        "x_range": (600.0, 1e9),
        "printed_stats": {"min": 0.2, "mean": 28.9, "median": 11.5, "max": 450.0},
        "x_axis": "log10 hours",
        "y_axis": "count of projects",
    },
}


def page_to_svg(pdf: Path, page: int) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "page.svg"
        subprocess.run(
            ["pdftocairo", "-svg", "-f", str(page), "-l", str(page), str(pdf), str(out)],
            check=True,
            capture_output=True,
        )
        return out.read_text()


def parse_clip_rectangles(svg: str, to_device):
    """Bar-width clip rectangles from `<defs>`, in device space.

    matplotlib emits one clip rectangle per bar, including bars of count zero
    that carry no fill path. Coordinates here are rounded to whole page units by
    the renderer, so they locate a bin but do not measure it precisely.
    """
    defs = svg.split("</defs>")[0]
    found = []
    for _cid, d in re.findall(r'<clipPath id="([^"]*)">\s*<path[^>]*d="([^"]*)"', defs, re.S):
        nums = [float(v) for v in re.findall(r"-?\d+\.?\d*", d)]
        if len(nums) < 6:
            continue
        xs, ys = nums[0::2][:4], nums[1::2][:4]
        x0, y0 = to_device(min(xs), max(ys))
        x1, y1 = to_device(max(xs), min(ys))
        found.append({"x0": x0, "x1": x1, "height": y1 - y0})
    return found


def parse_page(svg: str):
    """Return (bars, ticks, clips, matrix) in the plotting group's own device space.

    pdftocairo emits most of a matplotlib axes inside a group carrying an affine
    `transform`, but flattens some paths into page coordinates. Both forms are
    normalised here onto the transformed frame, which is the frame the axis tick
    marks live in.
    """
    body = svg.split("</defs>")[-1]
    paths = re.findall(r"<path[^>]*?/>", body, re.S)

    matrices = re.findall(r'transform="matrix\(([^)]*)\)"', body)
    if not matrices:
        raise SystemExit("no affine transform found on this page")
    a, b, c, d, e, f = [float(v) for v in matrices[0].split(",")]
    if b or c:
        raise SystemExit("unexpected rotated/skewed transform")

    def to_device(x, y):
        return ((x - e) / a, (y - f) / d)

    bars, ticks = [], []
    for p in paths:
        dattr = re.search(r'\sd="([^"]*)"', p)
        if not dattr:
            continue
        nums = [float(v) for v in re.findall(r"-?\d+\.?\d*", dattr.group(1))]
        transformed = "transform=" in p
        fill = re.search(r'\sfill="([^"]*)"', p)
        fill = fill.group(1) if fill else None

        if fill and fill.startswith(BAR_FILL) and len(nums) >= 6:
            # "M x0 ybase L x1 ybase L x1 ytop L x0 ytop Z ..."
            x0, ybase, x1, ytop = nums[0], nums[1], nums[2], nums[5]
            if not transformed:
                x0, ybase = to_device(x0, ybase)
                x1, ytop = to_device(x1, ytop)
            bars.append({"x0": x0, "x1": x1, "y_base": ybase, "y_top": ytop})
        elif "stroke" in p and len(nums) == 4:
            x0, y0, x1, y1 = nums
            if not transformed:
                x0, y0 = to_device(x0, y0)
                x1, y1 = to_device(x1, y1)
            ticks.append({"x0": x0, "y0": y0, "x1": x1, "y1": y1})

    return bars, ticks, parse_clip_rectangles(svg, to_device), [a, b, c, d, e, f]


def axis_ticks(ticks, x_lo, x_hi):
    """Split tick segments into y-axis ticks and long x-axis (major) ticks."""
    ys, xs = [], []
    for t in ticks:
        horizontal = abs(t["y0"] - t["y1"]) < 0.02
        vertical = abs(t["x0"] - t["x1"]) < 0.02
        if horizontal and abs(t["x0"] - t["x1"]) < 12 and x_lo <= t["x0"] < x_hi:
            ys.append(round(t["y0"], 6))
        if vertical and 0 < abs(t["y0"] - t["y1"]) < 12 and x_lo <= t["x0"] < x_hi:
            xs.append((round(t["x0"], 6), round(abs(t["y0"] - t["y1"]), 3)))
    ys = sorted(set(ys))
    # Major x ticks are drawn longer than minor ones.
    if xs:
        longest = max(length for _, length in xs)
        majors = sorted({x for x, length in xs if abs(length - longest) < 0.01})
        minors = sorted({x for x, length in xs if abs(length - longest) >= 0.01})
    else:
        majors, minors = [], []
    return ys, majors, minors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()

    if not args.pdf.is_file():
        sys.exit(f"no such file: {args.pdf}")

    pages = {}
    result = {
        "generated_by": "research/remote-labor-index/extract_figure_bars.py",
        "source_pdf": "https://arxiv.org/pdf/2510.26787v1",
        "method": (
            "pdftocairo -svg per page; bar rectangles identified by matplotlib's "
            "default bar fill rgb(25.489807%, 41.175842%, 88.233948%); axis tick "
            "segments identified by stroke paths of four coordinates. Coordinates "
            "are in the plotting group's own device space after applying the "
            "page's affine transform."
        ),
        "panels": {},
    }

    for name, spec in PANELS.items():
        page = spec["page"]
        if page not in pages:
            pages[page] = parse_page(page_to_svg(args.pdf, page))
        bars, ticks, clips, matrix = pages[page]
        x_lo, x_hi = spec["x_range"]
        panel_bars = sorted(
            (b for b in bars if x_lo <= b["x0"] < x_hi), key=lambda b: b["x0"]
        )
        # Bar-width clips only, deduplicated: matplotlib emits a fill clip and an
        # edge clip per bar, at the same position and within a page unit of width.
        widths = [b["x1"] - b["x0"] for b in panel_bars]
        nominal = sorted(widths)[len(widths) // 2] if widths else 0.0
        panel_clips, seen = [], []
        for clip in sorted(
            (c for c in clips if x_lo <= c["x0"] < x_hi), key=lambda c: c["x0"]
        ):
            if abs((clip["x1"] - clip["x0"]) - nominal) > 0.5 * nominal:
                continue
            if any(abs(clip["x0"] - prior) < 0.5 * nominal for prior in seen):
                continue
            seen.append(clip["x0"])
            panel_clips.append(clip)
        y_ticks, x_majors, x_minors = axis_ticks(ticks, x_lo, x_hi)
        result["panels"][name] = {
            "page": page,
            "description": spec["description"],
            "x_axis": spec["x_axis"],
            "y_axis": spec["y_axis"],
            "printed_stats": spec["printed_stats"],
            "page_transform_matrix": matrix,
            "bars": [
                {k: round(v, 6) for k, v in b.items()} for b in panel_bars
            ],
            "bar_clip_rectangles": [
                {k: round(v, 6) for k, v in c.items()} for c in panel_clips
            ],
            "y_tick_positions": y_ticks,
            "x_major_tick_positions": x_majors,
            "x_minor_tick_positions": x_minors,
        }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=1) + "\n")
    for name, panel in result["panels"].items():
        print(f"{name}: {len(panel['bars'])} drawn bars, "
              f"{len(panel['bar_clip_rectangles'])} bins, "
              f"{len(panel['y_tick_positions'])} y ticks, "
              f"{len(panel['x_major_tick_positions'])} major x ticks")


if __name__ == "__main__":
    main()
