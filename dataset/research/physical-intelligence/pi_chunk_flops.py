#!/usr/bin/env python3
"""Per-action-chunk and per-task FLOPs for the Physical Intelligence pi0.6 family.

Architecture inputs are the published Gemma 3 4B and SigLIP So400m shapes plus
the pi0.6 model card's 860M action expert, four-camera 448x448 input, five
denoising steps and 50-step action chunk. Throughput values are read off the
published bar charts; the read-off procedure is in physical-intelligence.md.

Writes agent-work/derived/physical-intelligence/pi-flops.csv.
"""
import csv
from pathlib import Path

# --- Gemma 3 4B text backbone (google/gemma-3-4b-pt config.json) ---
L_B, D_B, FF_B = 34, 2560, 10240
HEADS, HEAD_DIM, KV_HEADS = 8, 256, 4
DQ = HEADS * HEAD_DIM                      # 2048 query/output width
attn_params = D_B * DQ + 2 * D_B * KV_HEADS * HEAD_DIM + DQ * D_B
mlp_params = 3 * D_B * FF_B
backbone_params = L_B * (attn_params + mlp_params)     # non-embedding

# --- SigLIP So400m vision encoder (Gemma 3 vision_config) ---
L_V, D_V, FF_V, PATCH = 27, 1152, 4304, 14
vision_params = L_V * (4 * D_V * D_V + 2 * D_V * FF_V)

# --- action expert: 860M over the backbone's layer count ---
AE_PARAMS = 860e6
# Gemma-shaped layer costs 14.4 d^2 params; invert for the expert width.
D_AE = (AE_PARAMS / L_B / 14.4) ** 0.5

# --- workload per action chunk ---
CAMERAS = 3                 # the 63 ms figure is quoted for three cameras
IMG = 448
PATCHES = (IMG // PATCH) ** 2          # 1024 encoded patches per image
TOK_PER_IMG = 256                      # Gemma 3 mm_tokens_per_image
TEXT_TOK = 20                          # task prompt, metadata, state text
STATE_TOK = 2
PREFIX = CAMERAS * TOK_PER_IMG + TEXT_TOK + STATE_TOK
CHUNK = 50                             # action tokens per chunk
STEPS = 5                              # denoising steps
EXEC_STEPS = 20                        # H-hat, midpoint of {15, 25}
CONTROL_HZ = 50
CHUNKS_PER_S = CONTROL_HZ / EXEC_STEPS

vis_w = CAMERAS * PATCHES * 2 * vision_params
vis_a = CAMERAS * PATCHES * L_V * 4 * D_V * PATCHES
pre_w = PREFIX * 2 * backbone_params
pre_a = PREFIX * L_B * 4 * DQ * PREFIX
act_w = CHUNK * STEPS * 2 * AE_PARAMS
act_a = CHUNK * STEPS * L_B * 4 * D_AE * (PREFIX + CHUNK)
per_chunk = vis_w + vis_a + pre_w + pre_a + act_w + act_a

ALLOWANCE = {"pi06": 1.10, "pi07": 1.20}
COEF = {k: per_chunk * v * CHUNKS_PER_S for k, v in ALLOWANCE.items()}

# task, model key, successes per hour
TASKS = [
    ("pi-shirt-flat-pi06",        "pi06", 49.0),
    ("pi-laundry-fold-pi06",      "pi06", 18.8),
    ("pi-table-bus-pi06",         "pi06", 43.8),
    ("pi-laundry-pickup-pi06",    "pi06", 101.1),
    ("pi-make-bed-pi06",          "pi06", 24.6),
    ("pi-laundry-fold-pistar06",  "pi06", 59.9),
    ("pi-laundry-diverse-pistar06", "pi06", 8.31),
    ("pi-espresso-pistar06",      "pi06", 28.7),
    ("pi-box-assembly-pistar06",  "pi06", 13.22),
    ("pi-laundry-fold-pi07",      "pi07", 0.979 * 59.9),
    ("pi-laundry-diverse-pi07",   "pi07", 1.457 * 8.31),
    ("pi-espresso-pi07",          "pi07", 0.963 * 28.7),
    ("pi-box-build-pi07",         "pi07", 1.457 * 13.22),
]

out = Path(__file__).resolve().parents[3] / "agent-work/derived/physical-intelligence"
out.mkdir(parents=True, exist_ok=True)
rows = []
for pid, key, tph in TASKS:
    seconds = 3600.0 / tph
    chunks = seconds * CHUNKS_PER_S
    rows.append({
        "point_id": pid, "model": key,
        "successes_per_hour": round(tph, 3),
        "seconds_per_success": round(seconds, 1),
        "chunks_per_success": round(chunks, 1),
        "text_tokens": round(chunks * TEXT_TOK),
        "compute_flops": f"{COEF[key] * seconds:.4g}",
    })
with (out / "pi-flops.csv").open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)

if __name__ == "__main__":
    print(f"backbone non-embedding params : {backbone_params:,.0f}")
    print(f"vision encoder params         : {vision_params:,.0f}")
    print(f"action expert width           : {D_AE:.0f}")
    print(f"prefix positions              : {PREFIX}")
    print("per-chunk FLOPs")
    for n, v in [("vision weights", vis_w), ("vision attention", vis_a),
                 ("prefix weights", pre_w), ("prefix attention", pre_a),
                 ("action expert weights", act_w),
                 ("action expert attention", act_a)]:
        print(f"  {n:<24}{v:.4g}")
    print(f"  {'subtotal':<24}{per_chunk:.4g}")
    for k in COEF:
        print(f"{k}: per-chunk {per_chunk*ALLOWANCE[k]:.4g}  "
              f"per robot-second {COEF[k]:.4g}")
    for r in rows:
        print(r)
