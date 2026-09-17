#!/usr/bin/env python3
"""Per-inference-cycle and per-activity FLOPs for the 2025 BEHAVIOR Challenge
winning policy (Robot Learning Collective, PiBehavior).

Architecture inputs are the openpi gemma_2b and gemma_300m configurations the
entry's own code selects, the SigLIP So400m/14 tower at 224x224, three cameras,
a 30-step action horizon and 20 flow-matching denoising steps. Execution is 20
steps at 30 Hz per inference cycle. Human activity durations are the mean over
200 released JoyLo teleoperation demonstrations per activity.

Writes agent-work/derived/behavior/behavior-flops.csv.
"""
import csv
from pathlib import Path

# --- SigLIP So400m/14 vision encoder, same tower as the pi0.6 recipe ---
L_V, D_V, FF_V, PATCH = 27, 1152, 4304, 14
vision_params = L_V * (4 * D_V * D_V + 2 * D_V * FF_V)

# --- VLM backbone: openpi gemma_2b (PaliGemma text tower) ---
L_B, D_B, FF_B = 18, 2048, 16_384
HEADS, HEAD_DIM, KV_HEADS = 8, 256, 1
DQ = HEADS * HEAD_DIM                                   # 2048
vlm_attn = D_B * DQ + 2 * D_B * KV_HEADS * HEAD_DIM + DQ * D_B
vlm_mlp = 3 * D_B * FF_B                                # GeGLU: 2 up, 1 down
vlm_params = L_B * (vlm_attn + vlm_mlp)                 # non-embedding

# --- action expert: openpi gemma_300m ---
L_A, D_A, FF_A = 18, 1024, 4096
ae_attn = D_A * DQ + 2 * D_A * KV_HEADS * HEAD_DIM + DQ * D_A
ae_mlp = 3 * D_A * FF_A
ae_params = L_A * (ae_attn + ae_mlp)                    # ~311M, as reported

# --- workload per inference cycle ---
CAMERAS = 3                       # head, left wrist, right wrist
IMG = 224
PATCHES = (IMG // PATCH) ** 2     # 256 patches per image, no pooling
TASK_TOK = 5                      # base task embedding + 4 stage-fused tokens
STATE_TOK = 32                    # 23-D proprioception padded to action_dim 32
PREFIX = CAMERAS * PATCHES + TASK_TOK + STATE_TOK
CHUNK = 30                        # action horizon
STEPS = 20                        # flow-matching denoising steps
EXEC_STEPS = 20                   # 26 predicted actions executed in 20 steps
CONTROL_HZ = 30
CYCLES_PER_S = CONTROL_HZ / EXEC_STEPS            # 1.5 inference cycles per robot-second

vis_w = CAMERAS * PATCHES * 2 * vision_params
vis_a = CAMERAS * PATCHES * L_V * 4 * D_V * PATCHES
pre_w = PREFIX * 2 * vlm_params
pre_a = PREFIX * L_B * 4 * DQ * PREFIX
act_w = CHUNK * STEPS * 2 * ae_params
act_a = CHUNK * STEPS * L_A * 4 * DQ * (PREFIX + CHUNK)
per_cycle = vis_w + vis_a + pre_w + pre_a + act_w + act_a

ALLOWANCE = 1.10          # KV-cache transform, projections, embeddings, stage head
COEF = per_cycle * ALLOWANCE * CYCLES_PER_S       # FLOPs per robot-second

# activity, point_id, mean teleoperation seconds (n=200), episodes fully completed of 10
TASKS = [
    ("make_microwave_popcorn",  "robo-popcorn-behavior-rlc",       107.9, 9),
    ("cook_hot_dogs",           "robo-hotdogs-behavior-rlc",       304.8, 8),
    ("cook_bacon",              "robo-bacon-behavior-rlc",         256.0, 7),
    ("turning_on_radio",        "robo-radio-behavior-rlc",          71.7, 6),
    ("moving_boxes_to_storage", "robo-boxes-storage-behavior-rlc",  486.5, 6),
]

# episode-duration scenarios, as multiples of the mean teleoperation duration
SCENARIOS = {"compressed": 1 / 1.3, "central": 1.0, "time_limit": 2.0}

out = Path(__file__).resolve().parents[3] / "agent-work/derived/behavior"
out.mkdir(parents=True, exist_ok=True)
rows = []
for activity, pid, secs, succ in TASKS:
    row = {"activity": activity, "point_id": pid,
           "human_mean_s": secs, "episodes_completed_of_10": succ}
    for name, mult in SCENARIOS.items():
        ai_secs = secs * mult
        row[name + "_ai_seconds"] = round(ai_secs, 1)
        row[name + "_cycles"] = round(ai_secs * CYCLES_PER_S, 1)
        row[name + "_flops"] = f"{COEF * ai_secs:.4g}"
    rows.append(row)
with (out / "behavior-flops.csv").open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)

if __name__ == "__main__":
    print(f"vision encoder params : {vision_params:,.0f}")
    print(f"VLM backbone params   : {vlm_params:,.0f}")
    print(f"action expert params  : {ae_params:,.0f}")
    print(f"prefix positions      : {PREFIX}")
    print("per-cycle FLOPs")
    for n, v in [("vision weights", vis_w), ("vision attention", vis_a),
                 ("prefix weights", pre_w), ("prefix attention", pre_a),
                 ("action expert weights", act_w),
                 ("action expert attention", act_a)]:
        print(f"  {n:<26}{v:.4g}")
    print(f"  {'subtotal':<26}{per_cycle:.4g}")
    print(f"  {'with 10% allowance':<26}{per_cycle * ALLOWANCE:.4g}")
    print(f"FLOPs per robot-second : {COEF:.4g}")
    for r in rows:
        print(r)
