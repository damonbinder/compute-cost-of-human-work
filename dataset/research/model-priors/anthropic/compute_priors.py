"""Reproduces every number in research/model-priors/anthropic.md that is arithmetic.

Two routes.

Route T (throughput / effective memory bandwidth): in memory-bound batched decode, one decoding
step reads the active weights once and emits one token for every sequence in the batch, so
per-user tokens/sec ~= effective_bandwidth / (bytes_per_active_param * active_params).
Inverting, active_params = effective_bandwidth / (bytes_per_param * tokens_per_sec).

Route C (training compute): C = 6 * N_active * D. Writing D = R * N_active gives
N_active = sqrt(C / (6R)). R is the tokens-per-active-parameter ratio and is the whole ballgame.

No network access. Run: python3 compute_priors.py
"""
import json, math

BW_LO, BW_HI = 4.0e12, 4.5e12          # bytes/s, unexcitedneurons Vertex calibration
FP8, HYB_LO, HYB_HI = 1.0, 0.68, 0.73  # bytes per active parameter

def route_T(tps, lo_bytes=FP8, hi_bytes=FP8):
    """(low, high) active params. Low uses low bandwidth with the high bytes/param."""
    return BW_LO / (hi_bytes * tps), BW_HI / (lo_bytes * tps)

def route_C(C, R):
    return math.sqrt(C / (6.0 * R))

# ---- Route T inputs ------------------------------------------------------------------
# Series V: OpenRouter / Google Vertex, as reported by unexcitedneurons 2026-03-12.
series_V = {"Opus 4": 23, "Opus 4.1": 24, "Opus 4.5": 40, "Opus 4.6": 43,
            "Sonnet 4.5": 41, "Sonnet 4.6": 51}
# Series A: Artificial Analysis P50, retrieved 2026-09-13, max-effort config where offered.
series_A = {"Opus 4.5": 44.5, "Opus 4.6": 44.3, "Opus 4.7": 44.0, "Opus 4.8": 58.0,
            "Opus 5": 51.0, "Fable 5": 66.0, "Fable 5.1": 67.0,
            "Sonnet 4.5": 47.3, "Sonnet 4.6": 45.9, "Sonnet 5": 74.0,
            "Haiku 4.5": 85.0, "Haiku 4.5 non-reasoning": 78.0}

out = {"route_T_fp8": {}, "route_T_hybrid_fp8_fp4": {}, "series_cross_check": {}}
for label, series in (("V", series_V), ("A", series_A)):
    for m, tps in series.items():
        lo, hi = route_T(tps)
        out["route_T_fp8"][f"{label}:{m}"] = [round(lo/1e9, 1), round(hi/1e9, 1)]
        lo2, hi2 = route_T(tps, HYB_LO, HYB_HI)
        out["route_T_hybrid_fp8_fp4"][f"{label}:{m}"] = [round(lo2/1e9, 1), round(hi2/1e9, 1)]

# Where the two measurement series overlap, how far apart are they?
for m in set(series_V) & set(series_A):
    out["series_cross_check"][m] = {"vertex_tps": series_V[m], "aa_tps": series_A[m],
                                    "ratio_aa_over_vertex": round(series_A[m]/series_V[m], 3)}

# Serving-policy variance that the method cannot see.
out["serving_policy_spread"] = {
    "opus_4_8_fast_mode_speed_multiple": 2.5,
    "sonnet_4_5_provider_spread_bedrock_over_azure": round(48.7/38.5, 3),
    "opus_4_5_provider_spread_amazon_over_azure": round(46.2/43.1, 3),
    "opus_4_1_to_opus_4_5_vertex_throughput_ratio": round(40/24, 3),
}

# ---- Route C inputs -----------------------------------------------------------------
# Epoch training-compute estimates, all flagged Speculative except 3.7 Sonnet (Likely).
C_epoch = {"Claude 2": 3.866e24, "Claude 3 Opus": 1.64e25,
           "Claude 3.5 Sonnet": 2.7e25, "Claude 3.7 Sonnet": 3.35e25}
# R = training tokens per active parameter. Anchors: Chinchilla 20; GPT-4 as leaked
# (1.8T total, ~280B active, ~13T tokens) gives 46; DeepSeek-V3 (37B active, 14.8T tokens) gives 400.
R_grid = [20, 46, 100, 200, 400]
out["route_C"] = {m: {f"R={R}": round(route_C(C, R)/1e9, 1) for R in R_grid}
                  for m, C in C_epoch.items()}
# Sanity check that the formula reproduces the two models where N and D are both known.
out["route_C_validation"] = {
    "GPT-4 at C=2.1e25, R=46": round(route_C(2.1e25, 46)/1e9, 1),   # target ~280B active
    "DeepSeek-V3 at C=3.4e24, R=400": round(route_C(3.4e24, 400)/1e9, 1),  # target 37B active
}

# ---- MoE sparsity route for the Fable/Mythos class ----------------------------------
# FT industry estimate: Fable 5 ~5e12 total. Contemporaneous sparsity references.
out["route_S_fable_active_from_5T_total"] = {
    "Kimi K3-like 27x (2.8T total / 104B active)": round(5e12/(2.8e12/104e9)/1e9, 1),
    "DeepSeek-like 32x": round(5e12/32/1e9, 1),
    "Kimi K2-like 48x": round(5e12/48/1e9, 1),
}

# ---- Price ratios, recorded so the note does not have to assert them ----------------
out["list_price_output_per_mtok"] = {"Haiku 4.5": 5, "Sonnet 4.5/4.6": 15, "Opus 3": 75,
                                     "Opus 4/4.1": 75, "Opus 4.5-5": 25, "Fable 5/5.1": 50,
                                     "Opus 4.8 fast": 50, "Opus 4.7 fast": 150}
out["open_model_output_price_per_mtok_reference"] = {
    "DeepSeek V3.1 (37B active)": 1.68, "Kimi K2 (32B active)": 2.50, "GLM-4.6 (32B active)": 2.20}

print(json.dumps(out, indent=2))
