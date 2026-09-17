#!/usr/bin/env python3
"""Digitize the result figures of RE-Bench (METR, arXiv 2411.15114v2).

The paper reports its agent scores and its per-agent dollar costs only as plots, so
this script reads them off the figure bitmaps embedded in the PDF and writes one CSV:

  figure6   score@k for each agent configuration under three ways of allocating
            8 total hours, with the plotted 95% confidence whiskers
  figure7   score@k with a 30-minute run limit, k = 1..128
  figure8   score@k with a 2-hour run limit, k = 1..16
  figure11  best observed score@k against the cost budget in USD, per configuration
            and for the human experts

Axis calibration is hard-coded to the gridline pixel rows of the retained bitmaps and
verified at run time: every calibration row must still be mostly gridline grey, and the
value-versus-pixel fit must be linear to better than 1.5 px.

Dependencies: pypdf, pillow, numpy, scipy.

Usage:
    python3 digitize_figures.py agent-work/sources/rebench/rebench-2411.15114v2.pdf \
        research/rebench/figure-data.csv
"""
import sys
import numpy as np
from pypdf import PdfReader
from PIL import Image
from scipy import ndimage

GRID = (241, 241, 241)

SERIES = {
    "claude-3-5-sonnet-20240620 / Modular": (182, 31, 67),
    "claude-3-5-sonnet-20241022 / Modular": (206, 106, 56),
    "claude-3-5-sonnet-20241022 / AIDE": (5, 172, 111),
    "o1-preview / AIDE": (12, 87, 137),
}

# page index, bitmap size, and which embedded image on that page
FIGURES = {
    "figure5": (13, (1200, 750), 0),
    "figure6": (13, (1038, 737), 1),
    "figure7": (14, (1200, 750), 0),
    "figure8": (14, (1200, 750), 1),
    "figure2": (2, (1200, 750), 0),
    "figure11": (19, (1200, 750), 0),
    "figure12": (26, (973, 1382), 0),
}

# gridline pixel -> axis value, read off the retained bitmaps and asserted below
CAL_Y = {
    "figure6": [(283.5, 0.8), (376.5, 0.6), (469.5, 0.4), (561.5, 0.2)],
    "figure7": [(103.5, 1.2), (197.0, 1.0), (288.5, 0.8), (381.5, 0.6),
                (474.5, 0.4), (567.5, 0.2)],
    # figure 8's 0.2 gridline is covered by the plotted bands, so it is not used
    "figure8": [(103.5, 1.2), (197.0, 1.0), (288.5, 0.8), (381.5, 0.6), (474.5, 0.4)],
    "figure11": [(66.0, 1.4), (150.5, 1.2), (235.5, 1.0), (320.5, 0.8),
                 (405.5, 0.6), (490.5, 0.4), (575.5, 0.2)],
}
CAL_Y["figure2"] = [(66.0, 1.4), (150.5, 1.2), (234.5, 1.0), (319.5, 0.8),
                    (404.5, 0.6), (488.5, 0.4)]
# figure 2 x axis: total time budget in hours, doubling every 143.3 px
CAL_X_LOG_F2 = [(152.5, 0.5), (295.5, 1.0), (438.5, 2.0), (581.5, 4.0),
                (725.5, 8.0), (868.5, 16.0), (1011.5, 32.0), (1155.5, 64.0)]

CAL_X_LOG = {  # x gridline pixel -> dollars, log10 axis
    "figure11": [(162.5, 3.0), (299.5, 10.0), (424.5, 30.0), (561.5, 100.0),
                 (686.5, 300.0), (823.5, 1000.0), (948.5, 3000.0), (1085.5, 10000.0)],
}

# Figure 6 bar x-spans, in plot order
F6_BARS = {
    "30min@16": [272, 326, 380, 433],
    "2h@4": [527, 581, 635, 689],
    "8h@1": [783, 837, 890, 944],
}
F6_BAR_WIDTH = 52

# marker x-positions on the log2 sample axis of figures 7 and 8
F7_X0, F7_DX, F7_KS = 289.0, 124.28, [1, 2, 4, 8, 16, 32, 64, 128]
F8_X0, F8_DX, F8_KS = 295.1, 213.72, [1, 2, 4, 8, 16]


def load(pdf_path, name):
    page_index, size, which = FIGURES[name]
    imgs = [im.image for im in PdfReader(pdf_path).pages[page_index].images
            if im.image.size == size]
    return np.array(imgs[which % len(imgs)].convert("RGB")).astype(int)


def _check_grid(img, index, axis):
    line = img[int(round(index))] if axis == 0 else img[:, int(round(index))]
    frac = (np.abs(line - np.array(GRID)).sum(axis=1) < 25).mean()
    assert frac > 0.30, f"axis {axis} index {index} is only {frac:.2f} gridline grey"


def fit_axis(img, pairs, axis, log=False):
    for px, _ in pairs:
        _check_grid(img, px, axis)
    x = np.array([p for p, _ in pairs], float)
    v = np.array([np.log10(u) if log else u for _, u in pairs], float)
    b, a = np.polyfit(x, v, 1)
    assert np.abs((a + b * x - v) / b).max() < 1.5, "axis fit is not linear to 1.5 px"
    if log:
        return lambda p: 10 ** (a + b * np.asarray(p, float))
    return lambda p: a + b * np.asarray(p, float)


def markers(img, color, tol=90, erosion=5, blank=None, min_px=6):
    """Marker centroids. Eroding the color mask drops the thin connecting line."""
    mask = np.abs(img - np.array(color)).sum(axis=2) < tol
    if blank is not None:
        (y0, y1), (x0, x1) = blank
        mask[y0:y1, x0:x1] = False
    lbl, n = ndimage.label(ndimage.binary_erosion(mask, np.ones((erosion, erosion), bool)))
    pts = []
    for i in range(1, n + 1):
        ys, xs = np.where(lbl == i)
        if len(ys) >= min_px:
            pts.append((xs.mean(), ys.mean()))
    return sorted(pts)


def figure6(pdf, rows):
    img = load(pdf, "figure6")
    vy = fit_axis(img, CAL_Y["figure6"], 0)
    dark = img.sum(axis=2) < 200
    for alloc, xs in F6_BARS.items():
        for (name, color), x0 in zip(SERIES.items(), xs):
            x1 = x0 + F6_BAR_WIDTH
            # the legend box overlaps two bar columns above y=250, so search below it
            sub = np.abs(img[250:648, x0 + 3:x1 - 2] - np.array(color)).sum(axis=2) < 30
            top = np.where(sub.any(axis=1))[0].min() + 250
            mid = (x0 + x1) // 2
            wh = np.where(dark[250:648, mid - 2:mid + 3].any(axis=1))[0] + 250
            rows.append(["figure6", name, alloc, "", round(float(vy(top)), 4),
                         round(float(vy(wh.max())), 4), round(float(vy(wh.min())), 4)])


def score_at_k(pdf, fig, limit, x0, dx, ks, rows):
    img = load(pdf, fig)
    vy = fit_axis(img, CAL_Y[fig], 0)
    for name, color in SERIES.items():
        for x, y in markers(img, color, blank=((0, 340), (600, img.shape[1]))):
            i = int(round((x - x0) / dx))
            assert abs(x - (x0 + i * dx)) < 6, (fig, name, x)
            rows.append([fig, name, f"{limit}@{ks[i]}", "",
                         round(float(vy(y)), 4), "", ""])


def figure11(pdf, rows):
    img = load(pdf, "figure11")
    vy = fit_axis(img, CAL_Y["figure11"], 0)
    vx = fit_axis(img, CAL_X_LOG["figure11"], 1, log=True)
    for name, color in list(SERIES.items()) + [("human", (72, 72, 72))]:
        for x, y in markers(img, color, blank=((0, 250), (0, 620))):
            rows.append(["figure11", name, "", round(float(vx(x)), 2),
                         round(float(vy(y)), 4), "", ""])



# ---------------------------------------------------------------- figure 12
# Appendix A.2.2. Two stacked violin panels, four violins each in series order,
# every violin carrying a median tick between two whisker caps. Bitmap 973x1382.
F12_PANELS = {
    "completion_tokens_per_second": dict(
        cal=[(24.0, 0.0), (153.5, 20.0), (283.5, 40.0), (413.5, 60.0),
             (543.5, 80.0), (673.5, 100.0), (803.5, 120.0), (934.5, 140.0)],
        bands=[(165, 210), (261, 306), (357, 402), (453, 498)]),
    "api_time_share": dict(
        cal=[(32.5, 0.0), (396.5, 0.4), (579.5, 0.6), (761.5, 0.8), (943.5, 1.0)],
        bands=[(719, 765), (815, 860), (911, 957), (1007, 1053)]),
}
# run limit each configuration was evaluated at in figure 12, in seconds
F12_RUN_SECONDS = {
    "claude-3-5-sonnet-20240620 / Modular": 1800,
    "claude-3-5-sonnet-20241022 / Modular": 1800,
    "claude-3-5-sonnet-20241022 / AIDE": 7200,
    "o1-preview / AIDE": 7200,
}

# confidence bands read off figures 7 and 8 at the 32-hour allocations, where
# figure 6 has no bar. Marker columns come from the score@k axis.
F78_BANDS = [
    ("figure7", "claude-3-5-sonnet-20240620 / Modular", "30min@64", 1035),
    ("figure7", "claude-3-5-sonnet-20241022 / Modular", "30min@64", 1035),
    ("figure8", "claude-3-5-sonnet-20241022 / AIDE", "2h@16", 1150),
    ("figure8", "o1-preview / AIDE", "2h@16", 1150),
]


def figure2(pdf, rows):
    """Figure 11 with total time budget on the x axis instead of dollars. Used only
    as a second reading of every score the rows use."""
    img = load(pdf, "figure2")
    vy = fit_axis(img, CAL_Y["figure2"], 0)
    vx = fit_axis(img, CAL_X_LOG_F2, 1, log=True)
    for name, color in list(SERIES.items()) + [("human", (72, 72, 72))]:
        for x, y in markers(img, color, blank=((0, 250), (0, 620))):
            rows.append(["figure2", name, "%.3gh" % float(vx(x)), "",
                         round(float(vy(y)), 4), "", ""])


def figure12(pdf, rows):
    img = load(pdf, "figure12")
    dark = img.sum(axis=2) < 250
    for panel, spec in F12_PANELS.items():
        vx = fit_axis_free(spec["cal"])
        for (name, _color), (lo, hi) in zip(SERIES.items(), spec["bands"]):
            counts = dark[lo - 14:hi + 14, :].sum(axis=0)
            xs = np.where(counts > 10)[0]
            groups, run = [], [xs[0]]
            for x in xs[1:]:
                if x - run[-1] > 3:
                    groups.append(run)
                    run = []
                run.append(x)
            groups.append(run)
            assert len(groups) == 3, (panel, name, len(groups))
            low, med, high = [float(vx(sum(g) / len(g))) for g in groups]
            rows.append(["figure12", name, panel, "", round(med, 4),
                         round(low, 4), round(high, 4)])


def fit_axis_free(pairs):
    """Linear fit with no gridline-grey check, for the figure 12 panels."""
    x = np.array([p for p, _ in pairs], float)
    v = np.array([u for _, u in pairs], float)
    b, a = np.polyfit(x, v, 1)
    assert np.abs((a + b * x - v) / b).max() < 2.0, "figure 12 axis fit"
    return lambda p: a + b * np.asarray(p, float)


def _on_ray(pixel, color, tol=14):
    """True if pixel is `color` alpha-blended over white."""
    alphas = []
    for p, c in zip(pixel, color):
        if 255 - c < 8:
            continue
        alphas.append((255 - p) / (255 - c))
    if not alphas or max(alphas) <= 0.02:
        return False
    spread = max(alphas) - min(alphas)
    return spread < tol / 255.0 * 4 and 0.02 < max(alphas) <= 1.08


def band_extent(img, color, x, others, vy):
    """Confidence-band extent at column x: walk out from the series line until the
    column turns white or enters another series' own band."""
    colmn = img[:, x, :]
    line = np.where(np.abs(colmn - np.array(color)).sum(axis=1) < 40)[0]
    line = line[(line > 80) & (line < 660)]
    assert len(line), (color, x)
    centre = int(line.mean())
    edges = []
    for step in (-1, 1):
        y = centre
        while True:
            n = y + step
            if n < 80 or n > 660:
                break
            p = tuple(colmn[n])
            if sum(p) >= 762:
                break
            if any(_on_ray(p, o) for o in others) and not _on_ray(p, color):
                break
            y = n
        edges.append(y)
    lo, hi = float(vy(max(edges))), float(vy(min(edges)))
    return lo, hi


def figure78_bands(pdf, rows):
    for fig, name, alloc, x in F78_BANDS:
        img = load(pdf, fig)
        vy = fit_axis(img, CAL_Y[fig], 0)
        color = SERIES[name]
        others = [c for n, c in SERIES.items() if n != name]
        lo, hi = band_extent(img, color, x, others, vy)
        rows.append([fig + "-band", name, alloc, "", round((lo + hi) / 2, 4),
                     round(lo, 4), round(hi, 4)])


def main(pdf, out):
    rows = []
    figure6(pdf, rows)
    score_at_k(pdf, "figure7", "30min", F7_X0, F7_DX, F7_KS, rows)
    score_at_k(pdf, "figure8", "2h", F8_X0, F8_DX, F8_KS, rows)
    figure11(pdf, rows)
    figure2(pdf, rows)
    figure12(pdf, rows)
    figure78_bands(pdf, rows)
    with open(out, "w", newline="") as fh:
        fh.write("figure,series,allocation,cost_usd,score,ci_low,ci_high\n")
        for r in rows:
            fh.write(",".join(f'"{c}"' if isinstance(c, str) and "," in c else str(c)
                              for c in r) + "\n")
    print(f"wrote {len(rows)} digitized points to {out}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    main(sys.argv[1], sys.argv[2])
