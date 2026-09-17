#!/usr/bin/env python3
"""Operation counts for the game-learning skill-acquisition rows.

Covers the curiosity-driven A3C agent of Dubey et al. (2018), Rainbow on the
Sonic benchmark of Nichol et al. (2018), and the Atari-100k successors BBF,
DreamerV3 and EfficientZero V2 on Frostbite.

Two operations per multiply-add throughout. Output goes to
agent-work/derived/game-learning/calculations.json; nothing is written inside
dataset/.
"""

import json
from pathlib import Path

OUT = (Path(__file__).resolve().parents[3]
       / "agent-work" / "derived" / "game-learning" / "calculations.json")
OVERHEAD = 1.03  # optimizer, normalization, activations, bookkeeping
res = {}


def conv(h_out, w_out, c_out, k, c_in):
    """Multiply-accumulates for one convolution producing h_out x w_out x c_out."""
    return h_out * w_out * c_out * k * k * c_in


def dense(n_in, n_out):
    return n_in * n_out


# ---------------------------------------------------------------------------
# 1. Dubey et al. (2018): curiosity-driven A3C (Pathak et al. 2017 shapes)
# ---------------------------------------------------------------------------
# 42x42x4 input, four 3x3 stride-2 convolutions of 32 channels, LSTM(256) over
# the 3x3x32 = 288 flattened features, policy over five actions plus a value.
A = 5  # four arrow keys plus a no-op

trunk = (conv(21, 21, 32, 3, 4) + conv(11, 11, 32, 3, 32)
         + conv(6, 6, 32, 3, 32) + conv(3, 3, 32, 3, 32))
lstm = 4 * (dense(288, 256) + dense(256, 256))
heads = dense(256, A) + dense(256, 1)
policy_fwd = 2 * (trunk + lstm + heads)

# Intrinsic curiosity module: its own copy of the convolutional trunk, run on
# s_t and s_{t+1}; an inverse model over the concatenated features; and a
# forward model over features plus a one-hot action.
icm_fwd = 2 * (2 * trunk
               + dense(2 * 288, 256) + dense(256, A)
               + dense(288 + A, 256) + dense(256, 288))

# Per environment step: one actor forward, one ICM forward to score the
# intrinsic reward, and a forward-plus-backward pass over both networks in the
# learner, charged as three forwards each.
dubey_step = policy_fwd + icm_fwd + 3 * policy_fwd + 3 * icm_fwd
DUBEY_STEPS = 4_000_000
dubey_total = dubey_step * DUBEY_STEPS * OVERHEAD
res["dubey"] = {"policy_forward_flops": policy_fwd,
                "icm_forward_flops": icm_fwd,
                "per_step_flops": dubey_step,
                "action_inputs": DUBEY_STEPS,
                "total_flops": dubey_total}

# ---------------------------------------------------------------------------
# 2. Rainbow on one Sonic test level (Nichol et al. 2018)
# ---------------------------------------------------------------------------
# Hessel et al. architecture on 84x84x4: three convolutions, then a dueling
# pair of 512-unit streams over the 7x7x64 = 3136 features, each emitting 51
# atoms (the advantage stream once per action).
SONIC_ACTIONS = 7
ATOMS = 51
rb_conv = (conv(20, 20, 32, 8, 4) + conv(9, 9, 64, 4, 32) + conv(7, 7, 64, 3, 64))
rb_value = dense(3136, 512) + dense(512, ATOMS)
rb_adv = dense(3136, 512) + dense(512, ATOMS * SONIC_ACTIONS)
rainbow_fwd = 2 * (rb_conv + rb_value + rb_adv)

SONIC_STEPS = 1_000_000          # the benchmark's fixed per-level budget
RB_WARMUP = 20_000               # 80K frames of replay history at frame skip 4
RB_PERIOD = 4                    # one update every four agent steps
RB_BATCH = 32
rb_updates = (SONIC_STEPS - RB_WARMUP) // RB_PERIOD
rb_samples = rb_updates * RB_BATCH
# Five forward-equivalents per replayed sample: three for the online
# forward-and-backward at s_t, one online forward at s_{t+n} for the double-Q
# action selection, one target-network forward at s_{t+n}.
rainbow_total = (rainbow_fwd * (SONIC_STEPS + 5 * rb_samples)) * OVERHEAD
res["rainbow_sonic"] = {"forward_flops": rainbow_fwd,
                        "updates": rb_updates,
                        "replay_samples": rb_samples,
                        "total_flops": rainbow_total}

# ---------------------------------------------------------------------------
# 3. BBF on one Atari-100k game (Schwarzer et al. 2023)
# ---------------------------------------------------------------------------
# 15-layer Impala-CNN ResNet at width scale 4: base channels (16, 32, 32)
# become (64, 128, 128). Each stage is a 3x3 convolution, a 3x3 stride-2
# max-pool, and two residual blocks of two 3x3 convolutions. 84x84x4 input.
s1 = conv(84, 84, 64, 3, 4) + 4 * conv(42, 42, 64, 3, 64)
s2 = conv(42, 42, 128, 3, 64) + 4 * conv(21, 21, 128, 3, 128)
s3 = conv(21, 21, 128, 3, 128) + 4 * conv(11, 11, 128, 3, 128)
bbf_enc = s1 + s2 + s3                      # multiply-accumulates
BBF_FEAT = 11 * 11 * 128
BBF_HIDDEN = 2048
BBF_ACTIONS = 18
bbf_q = (dense(BBF_FEAT, BBF_HIDDEN) + dense(BBF_HIDDEN, ATOMS)
         + dense(BBF_HIDDEN, ATOMS * BBF_ACTIONS))
# SPR branch: a two-convolution latent transition model at 11x11x128, a
# projection to 2048 and a prediction head, repeated over the update horizon.
bbf_trans = 2 * conv(11, 11, 128, 3, 128)
bbf_proj = dense(BBF_FEAT, BBF_HIDDEN)
bbf_pred = dense(BBF_HIDDEN, BBF_HIDDEN)
K = 5  # mean SPR prediction depth; the horizon anneals from 10 to 3

bbf_online_fwd = bbf_enc + bbf_q + K * (bbf_trans + bbf_proj + bbf_pred)
bbf_sample = (3 * bbf_online_fwd                 # online forward and backward
              + (bbf_enc + bbf_q)                # online forward at s_{t+n}
              + (bbf_enc + bbf_q)                # target forward at s_{t+n}
              + K * bbf_enc)                     # SPR target encodings
bbf_sample_flops = 2 * bbf_sample

BBF_STEPS = 100_000
BBF_RR = 8
BBF_BATCH = 32
bbf_samples = BBF_STEPS * BBF_RR * BBF_BATCH
bbf_actor = 2 * (bbf_enc + bbf_q) * BBF_STEPS
bbf_total = (bbf_sample_flops * bbf_samples + bbf_actor) * OVERHEAD
res["bbf"] = {"encoder_macs": bbf_enc,
              "sample_flops": bbf_sample_flops,
              "replay_samples": bbf_samples,
              "actor_flops": bbf_actor,
              "total_flops": bbf_total}

# ---------------------------------------------------------------------------
# 4. DreamerV3 on one Atari-100k game (Hafner et al., 200M default size)
# ---------------------------------------------------------------------------
DV3_PARAMS = 200e6
DV3_IMAGINED_PARAMS = 90e6   # sequence model, dynamics, heads, actor, critic
DV3_ENV_STEPS = 400_000
DV3_REPEAT = 4
DV3_BATCH, DV3_LENGTH = 16, 64
DV3_REPLAY_RATIO = 128
DV3_HORIZON = 15
dv3_grad_steps = int(DV3_ENV_STEPS
                     * DV3_REPLAY_RATIO / (DV3_BATCH * DV3_LENGTH) / DV3_REPEAT)
dv3_replayed = dv3_grad_steps * DV3_BATCH * DV3_LENGTH
dv3_imagined = dv3_grad_steps * DV3_BATCH * DV3_LENGTH * DV3_HORIZON
dv3_wm = 6 * DV3_PARAMS * dv3_replayed
dv3_im = 6 * DV3_IMAGINED_PARAMS * dv3_imagined
dv3_actor = 2 * DV3_IMAGINED_PARAMS * (DV3_ENV_STEPS / DV3_REPEAT)
dv3_total = (dv3_wm + dv3_im + dv3_actor) * OVERHEAD
res["dreamerv3"] = {"gradient_steps": dv3_grad_steps,
                    "replayed_positions": dv3_replayed,
                    "imagined_positions": dv3_imagined,
                    "world_model_flops": dv3_wm,
                    "imagination_flops": dv3_im,
                    "actor_flops": dv3_actor,
                    "total_flops": dv3_total}

# ---------------------------------------------------------------------------
# 5. EfficientZero V2 on one Atari-100k game (Wang et al. 2024)
# ---------------------------------------------------------------------------
# The image architecture is EfficientZero's, so the per-call costs are the ones
# already established in research/games-memory/atari-learning.md#efficientzero-compute.
EZ_H = 297_271_296          # representation
EZ_P = 5_569_216            # prediction
EZ_I = 18_174_720           # dynamics + reward + prediction
EZ_INITIAL = EZ_H + EZ_P
EZ_LEARNER_SAMPLE = 2_905_060_096

EZ2_SIMS = 16
EZ2_BATCH = 256
EZ2_STEPS = 100_000         # collected decisions, UTD 1 -> one update each
EZ2_UPDATES = 100_000
EZ2_REANALYSED_STATES = 6   # the unroll window, as in EfficientZero
ez2_root = EZ_INITIAL + EZ2_SIMS * EZ_I
ez2_roots = EZ2_UPDATES * EZ2_BATCH * EZ2_REANALYSED_STATES
ez2_reanalysis = ez2_roots * ez2_root
ez2_learner = EZ2_UPDATES * EZ2_BATCH * EZ_LEARNER_SAMPLE
ez2_collect = EZ2_STEPS * ez2_root
ez2_eval_decisions = 13 * 32 * 3000 + 32 * 27000
ez2_eval = ez2_eval_decisions * ez2_root
ez2_total = (ez2_reanalysis + ez2_learner + ez2_collect + ez2_eval) * OVERHEAD
res["efficientzero_v2"] = {"root_search_flops": ez2_root,
                           "reanalysis_roots": ez2_roots,
                           "reanalysis_flops": ez2_reanalysis,
                           "learner_flops": ez2_learner,
                           "collection_flops": ez2_collect,
                           "evaluation_flops": ez2_eval,
                           "total_flops": ez2_total}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(res, indent=2, sort_keys=True) + "\n", encoding="utf-8")
for k, v in res.items():
    print("%-18s %.6e" % (k, v["total_flops"]))
