#!/usr/bin/env python3
"""Derivations for the skill-games-2 rows: Space Fortress, Suphx, Cicero.

Every number quoted in skill-games-2.md comes from this script. It counts
network operations at two FLOPs per multiply-add, takes a backward pass as
twice the forward unless activation checkpointing is in force (then three
times), and adds a 3 per cent allowance for optimizer, normalization,
activation and bookkeeping arithmetic, matching the convention of
research/game-learning/game-learning.md.

It also runs the Tenhou promotion-ladder simulation that sets the Suphx human
time, and the measured hanchan-duration reduction over Tenhou's own published
score logs when those logs are supplied.

Usage:
    python3 skill_games_2_calc.py --output <path/to/out.json> \
        [--tenhou-logs <dir of Tenhou scb*.log files>] [--seed 20260914]

Dependencies: the Python standard library only.
"""

import argparse
import glob
import json
import os
import random
import statistics

FLOPS_PER_MAC = 2
OVERHEAD = 1.03          # optimizer, normalization, activation, bookkeeping


# --------------------------------------------------------------------------
# 1. Space Fortress: PPO with the SF-GRU policy network
# --------------------------------------------------------------------------

def conv_macs(out_h, out_w, out_c, k_h, k_w, in_c):
    return out_h * out_w * out_c * k_h * k_w * in_c


def sf_gru_forward_macs(n_actions, in_channels=4):
    """Agarwal et al. (2018) Section 4.1, SF-GRU.

    84x84 grayscale observation, a stack of the last four frames (Section
    3.4); two convolutions of 16 and 32 filters, sizes 8 and 4, strides 4 and
    2; a 256-unit linear layer; a 256-unit GRU; policy and value heads.
    """
    # conv1: (84-8)/4 + 1 = 20
    c1 = conv_macs(20, 20, 16, 8, 8, in_channels)
    # conv2: (20-4)/2 + 1 = 9
    c2 = conv_macs(9, 9, 32, 4, 4, 16)
    flat = 9 * 9 * 32                       # 2592
    fc = flat * 256
    gru = 3 * (256 * 256 + 256 * 256)       # update, reset, candidate
    heads = 256 * n_actions + 256 * 1
    total = c1 + c2 + fc + gru + heads
    return {"conv1": c1, "conv2": c2, "fc": fc, "gru": gru, "heads": heads,
            "total_macs": total, "forward_flops": total * FLOPS_PER_MAC}


def space_fortress(n_actions, steps=45_000_000, ppo_epochs=4, in_channels=4):
    """One 45M-step PPO run.

    Per environment step the actor runs one forward pass to choose an action.
    The step is then replayed in each of the four PPO epochs the paper
    specifies ("we updated the policy 4 times every epoch"), and each replay
    is a forward and a backward, charged at three forward costs. That is
    1 + 4 x 3 = 13 forward-equivalents per environment step.
    """
    f = sf_gru_forward_macs(n_actions, in_channels)
    per_step_equivalents = 1 + ppo_epochs * 3
    base = steps * per_step_equivalents * f["forward_flops"]
    # Evaluation allowance: the reported scores are means over three-minute
    # games at 30 decisions per second. Allow 100 evaluation games, which is
    # generous against the paper's reported means and bests.
    eval_decisions = 100 * 180 * 30
    evaluation = eval_decisions * f["forward_flops"]
    total = (base + evaluation) * OVERHEAD
    return {"network": f,
            "forward_equivalents_per_step": per_step_equivalents,
            "environment_steps": steps,
            "training_flops": base,
            "evaluation_flops": evaluation,
            "total_flops": total}


# --------------------------------------------------------------------------
# 2. Suphx
# --------------------------------------------------------------------------

def suphx_model_macs(in_channels, head):
    """Li et al. (2020) Figures 4 and 5 and Table 2.

    A Dx34x1 input, a 3x1 convolution to 256 channels, fifty further 3x1
    convolutions at 256 channels with residual connections, then the model's
    head. The discard model (D = 838) ends in a 1x1 convolution to one
    channel over the 34 tile columns. The Riichi, Chow, Pong and Kong models
    (D = 958) end in a 1x1 convolution to 32 channels, then two blocks of two
    fully connected layers of width 1024 and 256, then a two-way output.
    """
    pos = 34
    stem = pos * 256 * 3 * in_channels
    trunk = 50 * (pos * 256 * 3 * 256)
    if head == "discard":
        tail = pos * 1 * 1 * 256
    else:
        conv32 = pos * 32 * 1 * 256
        flat = pos * 32                     # 1088
        fcs = (flat * 1024 + 1024 * 256 + 256 * 1024 + 1024 * 256 + 256 * 2)
        tail = conv32 + fcs
    total = stem + trunk + tail
    return {"stem": stem, "trunk": trunk, "tail": tail,
            "total_macs": total, "forward_flops": total * FLOPS_PER_MAC}


def suphx(sl_epochs=1, games=2_500_000, decisions_per_game=700,
          meld_calls_per_game=250):
    discard = suphx_model_macs(838, "discard")
    meld = suphx_model_macs(958, "meld")

    sl_sizes = {"discard": 15_000_000, "riichi": 5_000_000,
                "chow": 10_000_000, "pong": 10_000_000, "kong": 4_000_000}
    sl = {}
    for name, n in sl_sizes.items():
        f = discard if name == "discard" else meld
        sl[name] = 3 * f["forward_flops"] * n * sl_epochs
    sl_total = sum(sl.values())

    # Self-play RL. Each hanchan runs about ten hands; a hand consumes the
    # 70-tile live wall, so the four seats make about 700 discard decisions
    # per game. Chow, Pong, Kong and Riichi models are queried only where the
    # action is legal; 250 such calls per game is the assumed rate.
    rollout_discard = games * decisions_per_game * discard["forward_flops"]
    rollout_meld = games * meld_calls_per_game * meld["forward_flops"]
    # Only the discard model is updated by RL (Section 4.2); every collected
    # discard decision takes one gradient pass at three forward costs.
    learner = games * decisions_per_game * 3 * discard["forward_flops"]
    rl_total = rollout_discard + rollout_meld + learner

    total = (sl_total + rl_total) * OVERHEAD
    return {"discard_model": discard, "meld_model": meld,
            "supervised": sl, "supervised_total": sl_total,
            "rl_rollout_discard": rollout_discard,
            "rl_rollout_meld": rollout_meld,
            "rl_learner": learner, "rl_total": rl_total,
            "total_flops": total,
            "supervised_samples": sum(sl_sizes.values())}


def suphx_hardware_check(games=2_500_000, reported_games=1_500_000):
    """44 GPUs for two days trained an agent on 1.5 million games."""
    titan_xp = 4 * 12.15e12        # fp32 peak, GP102
    k80 = 40 * 4.37e12             # fp32 peak per GK210 die
    peak = titan_xp + k80
    seconds = 2 * 24 * 3600 * (games / reported_games)
    return {"peak_flops_per_second": peak,
            "scaled_seconds": seconds,
            "at_100_percent": peak * seconds,
            "at_10_percent": peak * seconds * 0.10,
            "at_5_percent": peak * seconds * 0.05}


# --------------------------------------------------------------------------
# 3. Tenhou promotion ladder
# --------------------------------------------------------------------------

# tenhou.net/man/ #DAN, four-player East-South (hanchan) table.
# (rank name, promotion pt, starting pt, fourth-place penalty, room)
TENHOU_LADDER = [
    ("shinjin",    20,    0,    0,   "ippan"),
    ("9kyu",       20,    0,    0,   "ippan"),
    ("8kyu",       20,    0,    0,   "ippan"),
    ("7kyu",       20,    0,    0,   "ippan"),
    ("6kyu",       40,    0,    0,   "ippan"),
    ("5kyu",       60,    0,    0,   "ippan"),
    ("4kyu",       80,    0,    0,   "ippan"),
    ("3kyu",      100,    0,    0,   "ippan"),
    ("2kyu",      100,    0,   15,   "ippan"),
    ("1kyu",      100,    0,   30,   "joukyuu"),
    ("1dan",      400,  200,   45,   "joukyuu"),
    ("2dan",      800,  400,   60,   "joukyuu"),
    ("3dan",     1200,  600,   75,   "joukyuu"),
    ("4dan",     1600,  800,   90,   "tokujou"),
    ("5dan",     2000, 1000,  105,   "tokujou"),
    ("6dan",     2400, 1200,  120,   "tokujou"),
    ("7dan",     2800, 1400,  135,   "houou"),
    ("8dan",     3200, 1600,  150,   "houou"),
    ("9dan",     3600, 1800,  165,   "houou"),
]

ROOM_POINTS = {"ippan": (30, 15), "joukyuu": (60, 15),
               "tokujou": (75, 30), "houou": (90, 45)}

# Measured mean game time in minutes from Tenhou's own score logs; overridden
# by --tenhou-logs when the logs are supplied.
ROOM_MINUTES = {"ippan": 28.77, "joukyuu": 28.89,
                "tokujou": 27.91, "houou": 28.14}


def tenhou_drift(placement, room, penalty):
    """Points per hanchan at one rank and room, for a placement distribution."""
    first, second = ROOM_POINTS[room]
    p1, p2, _p3, p4 = placement
    return first * p1 + second * p2 - penalty * p4


def tenhou_ladder(placement, trials=20000, seed=20260914, room_minutes=None,
                  cap=2_000_000):
    """Expected ranked hanchan and hours to first reach 10 dan.

    A player with a fixed placement distribution enters at shinjin with zero
    points and plays the highest room open to the rank held. Points move by
    the official table; reaching the promotion figure advances the rank and
    resets the total to the new rank's starting points; a negative total at a
    dan rank demotes and resets likewise. The walk stops on promotion out of
    9 dan.
    """
    rng = random.Random(seed)
    minutes = dict(room_minutes or ROOM_MINUTES)
    p1, p2, p3, p4 = placement
    cum = [p1, p1 + p2, p1 + p2 + p3]
    games_out, minutes_out = [], []
    for _ in range(trials):
        i, pts, games, mins = 0, 0, 0, 0.0
        while i < len(TENHOU_LADDER):
            name, promote, start, penalty, room = TENHOU_LADDER[i]
            first, second = ROOM_POINTS[room]
            u = rng.random()
            if u < cum[0]:
                pts += first
            elif u < cum[1]:
                pts += second
            elif u < cum[2]:
                pass
            else:
                pts -= penalty
            games += 1
            mins += minutes[room]
            if pts >= promote:
                i += 1
                if i < len(TENHOU_LADDER):
                    pts = TENHOU_LADDER[i][2]
            elif pts < 0:
                # Only dan ranks demote; kyu ranks floor at zero.
                if start == 0:
                    pts = 0
                else:
                    i -= 1
                    pts = TENHOU_LADDER[i][2]
            if games > cap:
                break
        games_out.append(games)
        minutes_out.append(mins)
    games_out.sort()
    minutes_out.sort()

    def pct(xs, q):
        return xs[min(len(xs) - 1, int(q * len(xs)))]

    return {"trials": trials,
            "placement": list(placement),
            "room_minutes": minutes,
            "mean_games": statistics.mean(games_out),
            "median_games": statistics.median(games_out),
            "p10_games": pct(games_out, 0.10),
            "p90_games": pct(games_out, 0.90),
            "mean_hours": statistics.mean(minutes_out) / 60.0,
            "median_hours": statistics.median(minutes_out) / 60.0,
            "p10_hours": pct(minutes_out, 0.10) / 60.0,
            "p90_hours": pct(minutes_out, 0.90) / 60.0}


def tenhou_ladder_no_demotion(placement, room_minutes=None):
    """Closed-form expectation ignoring demotion, as a lower bound."""
    minutes = dict(room_minutes or ROOM_MINUTES)
    p1, p2, _p3, p4 = placement
    games = 0.0
    hours = 0.0
    per_rank = []
    for name, promote, start, penalty, room in TENHOU_LADDER:
        first, second = ROOM_POINTS[room]
        drift = first * p1 + second * p2 - penalty * p4
        need = promote - start
        g = need / drift
        games += g
        hours += g * minutes[room] / 60.0
        per_rank.append({"rank": name, "room": room, "points_needed": need,
                         "points_per_game": drift, "games": g})
    return {"games": games, "hours": hours, "per_rank": per_rank}


def measure_hanchan_minutes(log_dir):
    """Mean game time from Tenhou's published score logs.

    Column 1 of an scb log is the start time, column 2 the game time in
    minutes and column 3 the table code: the first character is the number of
    seats, the second the room and the third the length.
    """
    codes = {"tokujou": "四特南", "houou": "四鳳南",
             "joukyuu": "四上南", "ippan": "四般南"}
    buckets = {k: [] for k in codes}
    files = sorted(glob.glob(os.path.join(log_dir, "scb*.log")))
    for path in files:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                parts = line.split("|")
                if len(parts) < 4:
                    continue
                table = parts[2].strip()[:3]
                for key, code in codes.items():
                    if table == code:
                        buckets[key].append(int(parts[1].strip()))
    out = {"files": [os.path.basename(f) for f in files]}
    minutes = {}
    for key, vals in buckets.items():
        if not vals:
            continue
        minutes[key] = statistics.mean(vals)
        out[key] = {"games": len(vals), "mean_minutes": statistics.mean(vals),
                    "median_minutes": statistics.median(vals),
                    "sd_minutes": statistics.stdev(vals) if len(vals) > 1 else 0.0}
    out["room_minutes"] = minutes
    return out


# --------------------------------------------------------------------------
# 4. Cicero training
# --------------------------------------------------------------------------

def encdec_forward_macs(d, ffn, enc_layers, dec_layers, vocab,
                        enc_positions, dec_positions):
    """Transformer encoder-decoder forward pass, in multiply-accumulates.

    Per encoder position: four d x d attention projections and two d x ffn
    feed-forward matrices in every encoder layer, plus the key and value
    projections each decoder layer applies to the encoder output. Per decoder
    position: four d x d self-attention projections, the cross-attention
    query and output projections, the feed-forward matrices and the output
    head over the vocabulary. Attention score and value products are counted
    at 2 x d x context per layer.
    """
    enc_layer = 4 * d * d + 2 * d * ffn
    cross_kv = 2 * d * d
    dec_layer = 4 * d * d + 2 * d * d + 2 * d * ffn
    enc_weights = enc_positions * (enc_layers * enc_layer +
                                   dec_layers * cross_kv)
    dec_weights = dec_positions * (dec_layers * dec_layer + d * vocab)
    enc_attn = enc_positions * enc_layers * 2 * d * enc_positions
    dec_self_attn = dec_positions * dec_layers * 2 * d * (dec_positions / 2.0)
    dec_cross_attn = dec_positions * dec_layers * 2 * d * enc_positions
    total = (enc_weights + dec_weights + enc_attn + dec_self_attn +
             dec_cross_attn)
    return {"encoder_weights": enc_weights, "decoder_weights": dec_weights,
            "encoder_attention": enc_attn,
            "decoder_self_attention": dec_self_attn,
            "decoder_cross_attention": dec_cross_attn,
            "total_macs": total, "forward_flops": total * FLOPS_PER_MAC}


def encdec_parameters(d, ffn, enc_layers, dec_layers, vocab):
    enc = enc_layers * (4 * d * d + 2 * d * ffn)
    dec = dec_layers * (4 * d * d + 4 * d * d + 2 * d * ffn)
    emb = vocab * d
    return {"encoder": enc, "decoder": dec, "embeddings": emb,
            "total": enc + dec + emb}


def cicero(enc_positions=1400, dec_positions=60,
           order_enc_positions=1400, order_dec_positions=40):
    vocab = 50265 + 109

    dialogue_shape = encdec_parameters(2048, 8192, 22, 22, vocab)
    dialogue_fwd = encdec_forward_macs(2048, 8192, 22, 22, vocab,
                                       enc_positions, dec_positions)
    # --checkpoint-activations True: the backward pass recomputes the forward,
    # so one update is four forward costs, not three.
    dialogue_examples = 100_000 * 256 * 2      # steps x GPUs x per-GPU batch
    dialogue = 4 * dialogue_fwd["forward_flops"] * dialogue_examples

    order_shape = encdec_parameters(1024, 4096, 12, 12, vocab)
    order_fwd = encdec_forward_macs(1024, 4096, 12, 12, vocab,
                                    order_enc_positions, order_dec_positions)
    order_examples = 250_000 * 128 * 2
    order = 3 * order_fwd["forward_flops"] * order_examples

    # Dialogue-free strategy models: ten transformer blocks and a two-layer
    # LSTM decoder, all at width 224, over the 81 board locations.
    d = 224
    block = 4 * d * d + 2 * d * d
    strategy_macs = 81 * 10 * block + 81 * 2 * (8 * d * d)
    strategy_fwd = strategy_macs * FLOPS_PER_MAC
    bc_states = 125_261 * 40
    bc = 3 * strategy_fwd * bc_states * 400        # 400 epochs, batch 500
    # Self-play RL: no budget is published. Charge 500 network calls per phase
    # over 40 phases of 200,000 generated games, plus an equal learner term.
    rl_games = 200_000
    rl = 2 * rl_games * 40 * 500 * strategy_fwd

    total = (dialogue + order + bc + rl) * OVERHEAD
    return {"dialogue_model_parameters": dialogue_shape,
            "dialogue_forward": dialogue_fwd,
            "dialogue_examples": dialogue_examples,
            "dialogue_flops": dialogue,
            "order_model_parameters": order_shape,
            "order_forward": order_fwd,
            "order_examples": order_examples,
            "order_flops": order,
            "strategy_forward_flops": strategy_fwd,
            "behaviour_cloning_flops": bc,
            "self_play_flops": rl,
            "total_flops": total}


def cicero_hardware_check(dialogue_flops):
    """256 V100 for the dialogue fine-tune, at fp16 tensor-core peak."""
    peak = 256 * 125e12
    return {"peak_flops_per_second": peak,
            "seconds_at_100_percent": dialogue_flops / peak,
            "hours_at_30_percent": dialogue_flops / (peak * 0.30) / 3600.0}


# --------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True)
    ap.add_argument("--tenhou-logs", default=None)
    ap.add_argument("--seed", type=int, default=20260914)
    ap.add_argument("--trials", type=int, default=20000)
    args = ap.parse_args()

    out = {}
    out["space_fortress_autoturn"] = space_fortress(3)
    out["space_fortress_youturn"] = space_fortress(5)
    out["space_fortress_single_frame_autoturn"] = space_fortress(
        3, in_channels=1)

    out["suphx"] = suphx()
    out["suphx_hardware_check"] = suphx_hardware_check()
    out["suphx_supervised_five_epochs"] = suphx(sl_epochs=5)["total_flops"]

    measured = None
    if args.tenhou_logs:
        measured = measure_hanchan_minutes(args.tenhou_logs)
        out["tenhou_game_times"] = measured
    room_minutes = measured["room_minutes"] if measured else None

    placement = (0.280, 0.268, 0.247, 0.205)     # Suphx Table 5, top human
    out["tenhou_ladder"] = tenhou_ladder(placement, trials=args.trials,
                                         seed=args.seed,
                                         room_minutes=room_minutes)
    out["tenhou_ladder_no_demotion"] = tenhou_ladder_no_demotion(
        placement, room_minutes=room_minutes)
    # The improving player: halfway between chance and the mature 10-dan
    # placement distribution, which is what the climber looks like over the
    # games in which the skill itself is being acquired.
    improving = tuple(round((x + 0.25) / 2, 5) for x in placement)
    out["tenhou_ladder_improving"] = tenhou_ladder(
        improving, trials=args.trials, seed=args.seed,
        room_minutes=room_minutes)
    out["tenhou_ladder_central_hours"] = (
        out["tenhou_ladder"]["mean_hours"]
        * out["tenhou_ladder_improving"]["mean_hours"]) ** 0.5
    # Measured expert-room placement distributions (Suphx Table 5) and the
    # points per hanchan each implies at 9 dan, where the 165-point
    # fourth-place penalty bites hardest.
    measured_players = {"suphx": (0.293, 0.275, 0.244, 0.187),
                        "top_human": placement,
                        "bakuuchi": (0.280, 0.262, 0.232, 0.224),
                        "naga": (0.256, 0.272, 0.259, 0.211)}
    out["tenhou_drift_9dan"] = {
        name: {"tokujou": tenhou_drift(pl, "tokujou", 165),
               "houou": tenhou_drift(pl, "houou", 165)}
        for name, pl in measured_players.items()}

    c = cicero()
    out["cicero"] = c
    out["cicero_hardware_check"] = cicero_hardware_check(c["dialogue_flops"])
    out["cicero_short_context"] = cicero(enc_positions=900)["total_flops"]
    out["cicero_long_context"] = cicero(enc_positions=2048)["total_flops"]

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, sort_keys=True)
    print(json.dumps({
        "space_fortress_autoturn": out["space_fortress_autoturn"]["total_flops"],
        "space_fortress_youturn": out["space_fortress_youturn"]["total_flops"],
        "suphx": out["suphx"]["total_flops"],
        "cicero": out["cicero"]["total_flops"],
        "tenhou_mean_games": out["tenhou_ladder"]["mean_games"],
        "tenhou_median_hours": out["tenhou_ladder"]["median_hours"],
        "tenhou_mean_hours": out["tenhou_ladder"]["mean_hours"],
        "tenhou_improving_hours": out["tenhou_ladder_improving"]["mean_hours"],
        "tenhou_central_hours": out["tenhou_ladder_central_hours"],
    }, indent=2))


if __name__ == "__main__":
    main()
