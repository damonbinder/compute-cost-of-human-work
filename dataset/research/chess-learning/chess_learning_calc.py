"""Training FLOPs and human hours-to-rating for the chess skill-acquisition rows.

Reads nothing; writes a JSON summary. Usage:
    python3 chess_learning_calc.py --output <path>/chess-learning-calc.json
"""
import argparse, json, math

# ---------------------------------------------------------------- AI compute

def searchless_forward(d_model, layers, seq=79, out_bins=128):
    """FLOPs for one forward pass of a Ruoss et al. action-value transformer.

    Per position per layer: QKVO projections 4*d^2 MACs and a SwiGLU block of
    three d x 4d matrices, 12*d^2 MACs -> 16*d^2 MACs -> 32*d^2 FLOPs.
    Attention matrices: QK^T and AV, each d*seq MACs -> 4*d*seq FLOPs.
    Output head: 2*d*out_bins FLOPs at every position (all 79 run before the
    final bin distribution is read off).
    """
    per_pos_layer = 32 * d_model ** 2 + 4 * d_model * seq
    per_pos = layers * per_pos_layer + 2 * d_model * out_bins
    return per_pos * seq

def maia_forward_train():
    """Maia move-prediction net: the inference figure already established in
    research/games-memory/chess.md#maia-compute, plus the training graph's
    dense 5120 x 1858 one-hot legal-move mapping, which the inference row
    excludes because lc0 does it as an index selection."""
    inference = 77829166.08          # convolutions + dense + SE + 2% allowance
    policy_map = 2 * 5120 * 1858     # 8x8x80 logits -> 1858 move classes
    return inference, policy_map, inference + policy_map

BACKWARD_MULTIPLE = 3.0  # forward + backward = 3x forward

results = {"ai": {}, "human": {}}

sc_steps, sc_batch = 10_000_000, 4096
sc_seqs = sc_steps * sc_batch
for name, (d, L) in {"9m": (256, 8), "136m": (1024, 8), "270m": (1024, 16)}.items():
    fwd = searchless_forward(d, L)
    results["ai"][f"searchless-{name}"] = {
        "forward_flops_per_sequence": fwd,
        "sequences": sc_seqs,
        "positions": sc_seqs * 79,
        "training_flops": BACKWARD_MULTIPLE * fwd * sc_seqs,
    }

maia_steps, maia_batch = 400_000, 1024
maia_positions = maia_steps * maia_batch
inf, pmap, fwd = maia_forward_train()
results["ai"]["maia"] = {
    "inference_forward_flops": inf,
    "policy_mapping_flops": pmap,
    "training_forward_flops": fwd,
    "positions": maia_positions,
    "training_flops": BACKWARD_MULTIPLE * fwd * maia_positions,
}

# ------------------------------------------------- Lichess blitz -> FIDE Elo
# Least-absolute-deviation fit over ~28,000 Lichess accounts that list a FIDE
# rating (Lebowitz rating converter, blitz-only model "b").
LICHESS_TO_FIDE = (78.6426799, 0.8039702)

def to_fide(blitz):
    a, b = LICHESS_TO_FIDE
    return a + b * blitz

# ------------------------------------------------------------ human learning
# Curve A, Charness et al. (2005) combined sample. Geometric-mean cumulative
# hours at the sample mean rating, and the conditional-mean slope of log hours
# on rating implied by r, SD(rating) and SD(log hours) in Tables 1 and 2.
CH = {
    "s1": {"n": 200, "rating": 2032, "sd_rating": 278,
           "study_log": 3.4, "sd_study_log": 0.5, "r_study": 0.54,
           "play_log": 3.5, "sd_play_log": 0.4, "r_play": 0.41},
    "s2": {"n": 164, "rating": 2008, "sd_rating": 253,
           "study_log": 3.5, "sd_study_log": 0.4, "r_study": 0.48,
           "play_log": 3.5, "sd_play_log": 0.5, "r_play": 0.26},
}
slopes = [s["r_study"] * s["sd_study_log"] / s["sd_rating"] for s in CH.values()]
CH_SLOPE = sum(slopes) / len(slopes)                      # log10 hours per Elo point
CH_RATING = sum(s["rating"] for s in CH.values()) / 2     # 2020
CH_HOURS = sum(10 ** s["study_log"] + 10 ** s["play_log"] for s in CH.values()) / 2

def hours_charness(fide):
    return CH_HOURS * 10 ** (CH_SLOPE * (fide - CH_RATING))

# Curve B, Gobet and Campitelli (2007). Mean cumulative total practice at the
# moment 34 players crossed Elo 2200; slope from Table 1's group means.
GC_HOURS, GC_RATING, GC_N = 11053.0, 2200.0, 34
GC_TABLE1 = [(1780, 8303), (2030, 11715), (2165, 19618), (2300, 27929)]
_lo, _hi = GC_TABLE1[0], GC_TABLE1[-1]
GC_SLOPE = (math.log10(_hi[1]) - math.log10(_lo[1])) / (_hi[0] - _lo[0])

def hours_gobet(fide):
    return GC_HOURS * 10 ** (GC_SLOPE * (fide - GC_RATING))

def hours_central(fide):
    return math.sqrt(hours_charness(fide) * hours_gobet(fide))

results["human"]["charness"] = {"slope_log10_per_elo": CH_SLOPE, "elo_per_decade": 1 / CH_SLOPE,
                                "anchor_rating": CH_RATING, "anchor_hours": CH_HOURS,
                                "per_sample_slopes": slopes}
results["human"]["gobet"] = {"slope_log10_per_elo": GC_SLOPE, "elo_per_decade": 1 / GC_SLOPE,
                             "anchor_rating": GC_RATING, "anchor_hours": GC_HOURS, "n": GC_N}

TARGETS = {
    "searchless-270m": 2895,   # Lichess blitz vs humans, Ruoss et al. Table 1
    "maia-1100": 1417,         # lichess.org/@/maia1 blitz, retrieved 2026-09-14
    "maia-1500": 1489,         # lichess.org/@/maia5
    "maia-1900": 1621,         # lichess.org/@/maia9
    "searchless-9m": 2054,     # vs bots only; not built
    "searchless-136m": 2156,   # vs bots only; not built
}
for name, blitz in TARGETS.items():
    f = to_fide(blitz)
    row = {"lichess_blitz": blitz, "fide_equivalent": f,
           "hours_charness": hours_charness(f), "hours_gobet": hours_gobet(f),
           "hours_central": hours_central(f),
           "seconds_central": hours_central(f) * 3600}
    # bridge sensitivity: a flat 100-point discount instead of the fitted model
    alt = blitz - 100
    row["fide_flat100"] = alt
    row["hours_flat100"] = hours_central(alt)
    results["human"][name] = row

# ---------------------------------------------------------------- the rows
ROWS = {
    "game-chess-train-searchless270m": ("searchless-270m", "searchless-270m"),
    "game-chess-train-maia1100": ("maia", "maia-1100"),
    "game-chess-train-maia1500": ("maia", "maia-1500"),
    "game-chess-train-maia1900": ("maia", "maia-1900"),
}
results["rows"] = {}
for pid, (ai_key, human_key) in ROWS.items():
    flops = results["ai"][ai_key]["training_flops"]
    secs = results["human"][human_key]["seconds_central"]
    results["rows"][pid] = {"compute_flops": flops, "human_time_seconds": secs,
                            "flops_per_human_second": flops / secs}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--output", required=True)
    a = p.parse_args()
    with open(a.output, "w") as fh:
        json.dump(results, fh, indent=2)
    print(json.dumps(results, indent=2))
