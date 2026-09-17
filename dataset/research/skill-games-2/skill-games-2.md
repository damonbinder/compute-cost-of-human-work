# Space Fortress, Suphx and Cicero: training compute against human learning time

*Created 2026-09-14 14:35.*

Three skill-acquisition rows. One pairs the PPO agent of
[Agarwal et al. (2018)](https://arxiv.org/abs/1809.02206) against the 52 subjects
who learned the Autoturn version of Space Fortress under a one-hour protocol; one
pairs
[Suphx](https://arxiv.org/abs/2003.13590) against the ranked Tenhou play a human
puts in to reach the 10-dan record rank Suphx reached; one pairs
[Cicero's](https://www.science.org/doi/10.1126/science.ade9097) training run
against the hours behind a top-decile finish in the webDiplomacy blitz league
Cicero entered.

| Row | Training FLOPs | Human time, h | Label |
|---|---:|---:|---|
| game-spacefortress-train-ppogru-autoturn | 4.0526e15 | 0.75 | above |
| game-mahjong-train-suphx | 5.6984e18 | 1370 | above |
| game-diplomacy-train-cicero | 1.0058e21 | 600 | match |

Every figure comes from `research/skill-games-2/skill_games_2_calc.py`, whose
retained output is
`agent-work/derived/skill-games-2/skill-games-2-calc.json`. The script counts
two FLOPs per multiply-add, charges a backward pass at twice the forward
(three times where activation checkpointing is in force), and adds 3% for
optimizer, normalization, activation and bookkeeping arithmetic, matching
`research/game-learning/game-learning.md`.

Retained sources are under `agent-work/sources/skill-games-2/`: the three arXiv
PDFs and their text extracts, the Cicero technical report PDF and extract, a
capture of Tenhou's promotion-point table, and five hours of Tenhou's published
score logs.

## Space Fortress

Space Fortress was built by [Mané and Donchin
(1989)](https://doi.org/10.1016/0001-6918(89)90003-6) as an instrument for
studying complex skill acquisition, so the human learning curve is the
published object rather than something inferred. Agarwal et al. ported it to
Gym and ran both legs on the same game.

The ship flies in a frictionless arena and destroys a central fortress. Missiles
must land more than 250 ms apart while the fortress's vulnerability builds to
10; once it reaches 10 the strategy reverses and a double shot inside 250 ms
destroys the fortress. A game lasts three minutes of real time, the game runs at
30 frames per second with no action repeat, and the score is +100 per fortress
destroyed, −100 per ship death and −2 per missile fired. Autoturn points the
ship at the fortress automatically and has three actions; Youturn is the
original game and has five.

### Space Fortress human learning

117 subjects were given the rules, including the change in required firing rate
at vulnerability 10, and then played 20 games — one hour of play. 52 played
Autoturn and 65 played Youturn. Table 1 reports, for each version, the mean over
all subjects of the last 5, last 10, last 15 and all 20 games, and the best
single game by any subject:

| Version | N | Best | Last 5 | Last 10 | Last 15 | All 20 |
|---|---:|---:|---:|---:|---:|---:|
| Autoturn | 52 | 3000 | 1989 | 1978 | 1940 | 1810 |
| Youturn | 65 | 2314 | 216 | 153 | 43 | −169 |

The row reads this as a learning budget with a measured endpoint: **15 games,
2,700 seconds, produces a player scoring 1,989 on Autoturn**, that being the mean
over the five games that follow. The duration is fixed by the protocol rather
than by any completion-time sample, so the evidence class is `defined_duration`,
and the 52 Autoturn subjects are the recorded attempts at that fixed duration.
The alternative reading — all 20 games, 3,600 seconds, at the all-games mean of
1,810 — mixes the learning phase into the endpoint and is not used.

Only the Autoturn leg becomes a row. The Youturn humans are still learning after
their hour, and the row built against them is withheld; the reason and the
derivation are in `agent-work/removed/skill-games-2/`.

Table 1's caption says "102 humans" while its own N column and the body text say
52 and 65. The N column is used.

The usual asymmetry runs one way and is not corrected for: the subjects arrive
with vision, motor control and a lifetime of world knowledge, and the network
starts from random weights.

### Space Fortress compute

Agarwal et al. give the SF-GRU policy network in Section 4.1: two convolutions
of 16 filters at size 8 stride 4 and 32 filters at size 4 stride 2 over the
84×84 observation, a 256-unit linear layer over the flattened 9×9×32 = 2,592
features, a 256-unit GRU, and linear policy and value heads. Section 3.4 states
that the agent is given a stack of the last four observations, so the input is
four channels.

| Component | Multiply-accumulates |
|---|---:|
| Convolution 1 | 1,638,400 |
| Convolution 2 | 663,552 |
| Linear 2592→256 | 663,552 |
| GRU, three gates | 393,216 |
| Policy and value heads, Autoturn | 1,024 |

That is 3,359,744 multiply-accumulates, **6,719,488 FLOPs per forward pass** on
Autoturn.

Every agent in the paper is trained for **45 million steps**. Per environment
step the actor runs one forward pass to choose an action, and the step is then
replayed in each of the four PPO epochs the paper specifies ("we updated the
policy 4 times every epoch"), each replay a forward and a backward at three
forward costs. That is 13 forward-equivalents per step, or 3.9309e15 FLOPs. An
evaluation allowance of 100 three-minute games at 30 decisions per second adds
3.6285e12, under 0.1%. With the 3% allowance the Autoturn run costs
**4.052565e15 FLOPs**.

Sixteen parallel worker processes change how the 45 million steps are
distributed, not how many there are. The released Gym environment
(`github.com/agakshat/spacefortress`) was not retrievable on 2026-09-14, so the
network shape rests on the paper's own description.

**The load-bearing assumption is the input channel count.** Section 3.4 says the
agent sees a stack of four observations; Section 4.1 writes the SF-GRU input as
"1x84x84". At one channel the first convolution falls from 1,638,400 to 409,600
multiply-accumulates and the run costs 2.570e15 FLOPs, 37% below the central.
Section 3.4 is the passage that describes the RL setup for all agents, and the
non-recurrent SF-FF variant needs the stack, so four channels is the central.

### game-spacefortress-train-ppogru-autoturn

The agent trained with the reward structure of Section 4.4, which rewards unit
increases in fortress vulnerability and adds a bonus for destruction, reaching
**average score 2,510, best 2,870, 43 fortress destructions per game** with
SF-GRU on Autoturn. The humans score 1,989. The agent is at 1.26× the human
mean, above the 1.15 top of the dataset's match band, so `above`; it is not
`far_above`, because the best human game of 3,000 exceeds the agent's best of
2,870 and the human mean is 79% of the agent's.

Both sides are scored on the game's own unclipped score over three-minute games
of the same version, so no translation is needed. The reward *shaping* differs
from what the humans were given: the agent receives a per-step signal marking
the two critical context switches, which the humans had to detect from the
screen, while the agent's 84×84 grayscale observation omits the time elapsed
since its last shot, which the paper says makes the task partially observed.
Both differences are conditions of the same task, flagged
`different_inputs_or_tools`.

### What is not built: the Youturn row and the 10-to-30-hour human curves

**Youturn.** The same recipe on the full five-action game was built as a row and
then withheld at merge. The agent averages 2,356 with 41 fortress destructions a
game against a human mean of 216 and 14.36 destructions, so the two sides are not
at the same proficiency, and no other Youturn human anchor exists at any
duration. The row, its model record and the derivation are in
`agent-work/removed/skill-games-2/`.

**The 10-to-30-hour human curves.** The classical Space Fortress literature
trains subjects for 10 to 30 hours, and the 10-hour Israeli Air Force protocol is
the best known learning curve in the field. No row is built from it, for two
independent reasons.

**The score scales do not meet.** The classical game reports a Total score built
from Points, Control, Velocity and Speed subscores, of which the modern Gym port
implements only the points component (+100 / −100 / −2). A 1980s Total of 2,500
and a 2018 score of 2,500 are different quantities, and the papers publish no
conversion.

**No agent checkpoint score is published.** Additional rungs would need the
agent's score at intermediate step counts. Agarwal et al. publish those only as
the curves of Figure 2, with no table, so there is no checkpoint figure to pair
with a 10-hour or 30-hour human endpoint. Figure 3's transfer curves are at
different critical time intervals and are not comparable to either human leg.

## Suphx

[Li et al. (2020)](https://arxiv.org/abs/2003.13590) built Suphx for four-player
Japanese Mahjong and put it on Tenhou.net, where it played 5,760 games in the
expert room. Its record rank reached **10 dan** and its stable rank **8.74**,
against **7.46** for the pooled expert-room play of the human 10-dan holders and
above 99.99% of ranked Tenhou players. The proficiency target is a Tenhou dan
rank, which is the same instrument on both sides, and that is what makes the
pairing worth building.

### Suphx compute

Five convolutional models share a structure (Figures 4 and 5, Table 2): a
D×34×1 input, a 3×1 convolution to 256 channels, fifty further 3×1 convolutions
at 256 channels with residual connections, then a head. The discard model takes
D = 838 and ends in a 1×1 convolution to one channel over the 34 tile columns,
giving 34 outputs. The Riichi, Chow, Pong and Kong models take D = 958 and end
in a 1×1 convolution to 32 channels, two blocks of two fully connected layers of
width 1024 and 256, and a two-way output. There is no pooling.

| Model | Stem | Fifty-block trunk | Head | Forward FLOPs |
|---|---:|---:|---:|---:|
| Discard | 21,881,856 | 334,233,600 | 8,704 | 712,248,320 |
| Riichi / Chow / Pong / Kong | 25,015,296 | 334,233,600 | 2,179,584 | 722,856,960 |

**Supervised learning.** Table 3 gives the training data: 15M discard, 5M
Riichi, 10M Chow, 10M Pong and 4M Kong state-action pairs, 44 million in total.
At three forward costs per sample and one pass over each set, supervised
training costs 9.494e16 FLOPs — under 2% of the run.

**Self-play reinforcement learning.** Footnote 8 states that Suphx is RL-2
trained with about **2.5 million games**. A hanchan runs about ten hands and a
hand consumes the 70-tile live wall, so the four seats make about 700 discard
decisions per game; the Chow, Pong, Kong and Riichi models are queried only
where the action is legal, taken here as 250 further calls per game. Only the
discard model is updated by RL (Section 4.2), and every collected discard
decision takes one gradient pass at three forward costs.

| Component | FLOPs |
|---|---:|
| Rollout, discard model | 1.2464e18 |
| Rollout, meld and Riichi models | 4.5179e17 |
| Learner, discard model | 3.7393e18 |
| Supervised learning | 9.494e16 |

With the 3% allowance the run costs **5.698437e18 FLOPs**.

**Hardware cross-check.** The paper reports that training one agent on 1.5
million games cost 44 GPUs — 4 Titan XP and 40 Tesla K80 — for two days. At
fp32 peak that fleet is 2.234e14 FLOP/s; scaled to 2.5 million games it runs
2.88e5 seconds, so 6.43e19 FLOPs at full utilization, 6.43e18 at 10% and 3.22e18
at 5%. The operation count implies 8.9% of peak, which is what a small
convolutional network stepping a CPU game simulator across a heterogeneous
fleet should look like. The cross-check is a reasonableness test on the
operation count, not the estimator.

Excluded from the work unit: the RL-basic, RL-1 and RL-2 ablation runs at 1.5
million games each; the offline evaluation of 1 million games on 20 K80 GPUs for
two days, which measures the ablations rather than producing Suphx; and run-time
policy adaptation, which footnote 8 says was not integrated into the agent that
played on Tenhou. The global reward predictor is a small recurrent network
trained on Tenhou logs and is not separately counted.

**Assumptions.** Decisions per game and the meld-call rate are estimated from
the structure of a hanchan, not reported; halving the meld rate moves the total
by 4%. The supervised pass count is taken as one epoch over the stated data
sizes; at five epochs the total rises to 6.09e18, 7% higher, because supervised
learning is a small share. The paper does not state the batch size, learning
rate schedule or number of gradient passes per collected sample for RL, so the
learner term is the single largest uncertainty.

### Tenhou human learning time

Tenhou publishes no hours-to-rank study. What it does publish is the exact
promotion-point table and, in its own score logs, the duration of every game.
Those two, with the placement distribution the Suphx paper measured for the
human 10-dan cohort, give a rank-versus-games derivation.

**The promotion rules.** From [Tenhou's manual](https://tenhou.net/man/), section
段級位制, four-player East-South (hanchan) play. Each rank has a starting point
total, a promotion total, and a fourth-place penalty that grows with rank; first
and second place pay by room. Points reset to the new rank's starting total on
promotion and on demotion, with the surplus discarded, and a dan rank demotes
when the total goes negative.

| Room | 1st | 2nd | 3rd | Open to |
|---|---:|---:|---:|---|
| 一般 ippan | +30 | +15 | 0 | everyone |
| 上級 joukyuu | +60 | +15 | 0 | 1 kyu and above |
| 特上 tokujou (expert) | +75 | +30 | 0 | 4 dan and above |
| 鳳凰 houou (phoenix) | +90 | +45 | 0 | 7 dan and above, humans only |

Fourth place costs 45, 60, 75, 90, 105, 120, 135, 150 and 165 points at 1 through
9 dan; promotion needs 400, 800, 1200, 1600, 2000, 2400, 2800, 3200 and 3600
against starting totals of 200, 400, 600, 800, 1000, 1200, 1400, 1600 and 1800.

**The placement distribution.** Suphx's Table 5 gives expert-room placement rates
for four players. The human 10-dan cohort finishes 28.0% / 26.8% / 24.7% / 20.5%.

**The game duration is measured.** Tenhou's score logs
(`tenhou.net/sc/raw/`) record the duration of every ranked game in minutes.
Five hours of logs from 2026-09-12 give, for four-player East-South games:

| Room | Games | Mean, min | Median, min | SD, min |
|---|---:|---:|---:|---:|
| 一般 ippan | 948 | 28.77 | 29 | 9.78 |
| 上級 joukyuu | 661 | 28.89 | 29 | 9.66 |
| 特上 tokujou | 547 | 27.91 | 27 | 8.04 |
| 鳳凰 houou | 121 | 28.14 | 28 | 9.35 |

**The ladder simulation.** A player with a fixed placement distribution enters at
新人 with zero points and plays the highest room open to the rank held, taking a
placement draw per game and moving by the official table, until promotion out of
9 dan. Over 20,000 trials at the measured 10-dan distribution the climb takes a
mean of **1,573 hanchan, 739 hours** (median 1,473 games, 10th to 90th percentile
993 to 2,285). Ignoring demotion entirely, a closed-form expectation gives 1,616
games and 759 hours: overshoot past each threshold roughly offsets the games lost
to demotion.

**That figure is a floor, because it assumes 10-dan strength from the first
ranked game.** A climber is weaker than that over the games in which the skill is
acquired. Rerunning the ladder at a distribution halfway between chance and the
mature one — 26.5% / 25.9% / 24.85% / 22.75% — gives a mean of 5,422 hanchan and
**2,542 hours**. The two readings are both defensible and neither is privileged,
so the row's human time is their geometric mean, **1,370 hours = 4,932,623
seconds**, following the dataset's rule for two defensible readings of one
evidence base.

**How sensitive this is.** Points per hanchan at 9 dan, the binding rank, for the
four measured expert-room distributions:

| Player | In 特上 tokujou | In 鳳凰 houou |
|---|---:|---:|
| Suphx | −0.63 | +7.89 |
| Human 10-dan cohort | −4.79 | +3.44 |
| Bakuuchi | −8.10 | +0.03 |
| NAGA | −7.46 | +0.47 |

Two things follow. **The expert room is not a route to 10 dan for anyone in this
table**, Suphx included: every measured distribution has negative point drift at
9 dan there, so Suphx's 10-dan record rank was an upswing across 5,760 games
against a negative drift, and its stable rank of 8.74 is the robust measure of
where it sits. And the model reproduces the outcomes it was not fitted to:
Bakuuchi and NAGA, at essentially zero drift in the phoenix room, stalled at
record ranks of 9 and 8 dan after 30,516 and 9,649 games, while the human cohort,
at +3.44, gets through.

**What the number is and is not.** It is ranked four-player hanchan played on
Tenhou, at the platform's own measured game durations, on the way to a first
10-dan record rank. It excludes study, offline and club play, replay review, and
three-player and East-only games, all of which push the true learning time up. It
also applies an expert-room placement distribution at phoenix-room payouts for
the 7-to-10-dan leg, because Tenhou publishes no phoenix-room distribution for
the 10-dan cohort; that is the model's weakest link and it flatters the human
side by understating how hard the last three ranks are.

### game-mahjong-train-suphx

Suphx against the human holders of the same 10-dan record rank. Both sides
reached 10 dan; Suphx's stable rank of 8.74 exceeds the cohort's 7.46 in the same
room, a modest edge on a scale where the humans plainly do the job, so `above`.
The performance comparator is a pool of 10-dan humans' expert-room games treated
as one macro player, because the paper could not compute a reliable stable rank
for any of them individually, while the timed population is a modelled climber;
the row flags `different_human_baseline` for that.

## Cicero

The [Cicero paper](https://www.science.org/doi/10.1126/science.ade9097) entered
the agent anonymously in 40 games of a webDiplomacy blitz league between 19
August and 13 October 2022, against 82 human opponents. Cicero more than doubled
the average human score and **ranked in the top 10% of participants who played
more than one game, and second of the 19 who played five or more**. Participants
played at most six games and were ranked on the mean of their best three.

This row is the training run. It is kept separate from the inference question,
which `agent-work/codex/reviews/cicero.md` closed as unresolvable and which
explicitly left the training lead open.

### Cicero compute

Four training components are published, in descending order of cost.

**The dialogue model.** The base is R2C2, a 2.7-billion-parameter Transformer
encoder-decoder pretrained on internet text with a BART denoising objective; it
was fine-tuned on text from 40,408 webDiplomacy games containing 12,901,662
dialogue messages, on **256 V100 GPUs for 100,000 training steps**. The released
training command in `parlai_diplomacy/README.md` of
`github.com/facebookresearch/diplomacy_cicero` gives the rest: embedding size
2048, 22 encoder and 22 decoder layers, feed-forward size 8192, 32 heads, GPT-2
dictionary plus 109 special tokens, input truncated to 2048 and targets to 512,
per-worker batch 2 with update frequency 1, dynamic batching off, and activation
checkpointing on.

Those shapes reproduce the stated size: 22 × (4d² + 2·d·ffn) = 1.107e9 encoder
parameters, 22 × (8d² + 2·d·ffn) = 1.476e9 decoder parameters and 1.03e8 tied
embeddings, 2.687e9 in total against the paper's 2.7 billion.

Per position and per layer the weight matrices cost 4d² in the encoder and 6d²
in the decoder — the decoder's extra 2d² being the cross-attention query and
output projections — plus 2·d·ffn for the feed-forward block; each decoder layer
also runs key and value projections over every encoder position, 2d² each. The
output head costs d × vocabulary per decoder position. Attention score and value
products cost 2·d·context per layer per position. At 1,400 encoder positions and
60 decoder positions one forward pass is **4.1533e12 FLOPs**, of which the
encoder weight matrices are 1.8086e12 and encoder attention 1.7662e11.

Batch 2 per worker over 256 workers is 512 examples per step, so 100,000 steps
process 51.2 million examples — about four passes over the 12.88 million training
messages. Activation checkpointing recomputes the forward pass inside the
backward, so one update costs four forward passes, not three. The fine-tune is
therefore **8.506e20 FLOPs**, 85% of the row.

**The dialogue-conditional action prediction model.** A BART-large model fine-tuned
in the same manner on the same corpus, on **128 V100 GPUs for 250,000 steps**,
same truncations. At d = 1024, feed-forward 4096 and 12 layers each side, one
forward pass at 1,400 encoder and 40 decoder positions is 6.106e11 FLOPs; at the
same per-worker batch of 2 that is 64 million examples and, at three forward
costs, **1.172e20 FLOPs**.

**The dialogue-free strategy models.** Table S10 gives ten transformer blocks and
a two-layer LSTM decoder, all at width 224, over the 81 board locations: batch
500, 400 epochs, 32 V100 GPUs. One forward pass is 6.178e8 FLOPs. Over 125,261
games at about 40 phases each, 400 epochs cost **3.714e18 FLOPs**.

**Self-play reinforcement learning.** RL-Cor-BR computes a joint policy with 100
samples for approximating p and a one-step rollout on every turn of every
generated game. No budget is published — not games, GPUs, or wall time. Charging
500 network calls per phase over 40 phases of 200,000 generated games, with an
equal learner term, gives **4.942e18 FLOPs**.

With the 3% allowance the training run costs **1.005776e21 FLOPs**.

**Hardware cross-check.** 256 V100s at fp16 tensor-core peak are 3.2e16 FLOP/s,
so the dialogue fine-tune is 2.66e4 seconds at full utilization and 24.6 hours at
30% — an ordinary duration for a 100,000-step run at this size.

**What the figure covers and what it assumes.** The scope is
`additional_training`: R2C2's and BART-large's internet pretraining is the
starting model and is excluded, which is also what keeps the general-language
attribution problem out of the row. The two assumed inputs are the per-GPU batch
of the order-prediction fine-tune, which the repository does not publish and
which is taken from the dialogue command, and the mean context length. At 900
encoder positions the total falls to 6.884e20 and at the full 2,048-token
truncation it rises to 1.445e21; the 1,400 central is the midpoint of a game in
which the model's context is a player's whole accumulated dialogue plus the board
state, truncated at 2048. The two small components together are 0.9% of the
total, so the unpublished self-play budget would have to be two orders of
magnitude larger than assumed to matter.

The `tokens` figure, 1.667e11, is the processed text positions of the two
language fine-tunes only; the strategy models are not token models and their
work is in the operation count.

### Cicero human learning time

**No measured learning-hours data exists for Diplomacy.** The number is the
dataset builder's estimate, and the reasoning is as follows.

The proficiency target is a top-decile finish in the league Cicero entered. Its
participants were webDiplomacy regulars who opted into a competitive blitz
league; finishing in the top tenth of that pool is an experienced player's
result, not a beginner's. Diplomacy is learned by playing whole games — there is
no drill, no puzzle set, and the skill being learned is negotiation across a
seven-player board, which only a full game exercises.

The league's own format fixes the active time of a blitz game: 5-minute turns and
game controls that, in the paper's words, "allowed games to be completed within 2
hours". Ordinary full-press webDiplomacy games run on longer turn clocks and
carry more press per game, so 3 hours of active attention per game is the rate
used. Reaching the top decile of a competitive league pool is put at roughly 200
full-press games. That gives **600 hours = 2,160,000 seconds**, with a range of
150 to 2,000 hours from 50 games at 3 hours to 500 games at 4.

Nothing in the paper constrains this. Table S13 lists the 82 opponents with their
scores and games played in the league, but participants were capped at six games,
so it carries no career counts. The WebDiplomacy dataset's player-rating feature
buckets Elo into five bins with no games-per-player figure attached.

### game-diplomacy-train-cicero

The human baseline is defined as a player who reached the same top-decile league
standing Cicero reached, so the two sides sit at the same proficiency by
construction and the label is `match`. Cicero's score was more than double the
league average, but the average player is not the comparator whose hours are
counted.

The row flags `different_inputs_or_tools`. Cicero ran on eight V100s with a
separate machine controlling the dialogue with each recipient, so its six
conversations proceeded wholly independently and in parallel; a human in a
five-minute blitz turn is one person handling six correspondents in series. The
task and the scoring are the league's own on both sides.

## Reproduction

```
python3 dataset/research/skill-games-2/skill_games_2_calc.py \
    --output agent-work/derived/skill-games-2/skill-games-2-calc.json \
    --tenhou-logs agent-work/sources/skill-games-2/tenhou-logs
```

The script needs only the standard library. Without `--tenhou-logs` it falls back
to the measured room durations recorded in its own `ROOM_MINUTES` table and
reproduces every other figure unchanged. The ladder simulation is seeded at
20260914; at 20,000 trials the mean game count moves by under 1% across seeds.
