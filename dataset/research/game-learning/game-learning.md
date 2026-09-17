# Game learning

*Created 2026-09-14 12:10.*

Five skill-acquisition rows pairing a single-purpose game agent's training
compute against the learning time of a human who reached the same proficiency
on the same game. Two come from the platform game of Dubey et al. (2018), and
three from the Atari-100k successors BBF, DreamerV3 and EfficientZero V2 on
Frostbite, which
reuse the Frostbite human anchors already established in
`research/games-memory/atari-learning.md`. Every FLOP figure is an operation
count for one configured training run of that row's game, at two operations per
multiply-add, with a 3% allowance for optimizer, normalization, activation and
bookkeeping arithmetic. The arithmetic is in `research/game-learning/calculations.py`,
with output in `agent-work/derived/game-learning/calculations.json`.

Rows that would have been built but are not asserted — every EMPA row, the
whole Sonic grid, the Dubey ablation conditions — are listed in the final
section with the reason, and in full in `agent-work/removed/game-learning/`.

## Sources and scope

[Dubey et al. (2018)](https://arxiv.org/abs/1802.10217), retained at
`agent-work/sources/game-learning/1802.10217.pdf`;
[Schwarzer et al. (2023)](https://arxiv.org/abs/2305.19452) for BBF, retained at
`agent-work/sources/game-learning/2305.19452.pdf`;
[Hafner et al. (2023)](https://arxiv.org/abs/2301.04104) for DreamerV3, retained at
`agent-work/sources/game-learning/2301.04104.pdf`;
[Wang et al. (2024)](https://arxiv.org/abs/2403.00564) for EfficientZero V2, retained at
`agent-work/sources/game-learning/2403.00564.pdf`;
[Tsividis et al. (2021)](https://arxiv.org/abs/2107.12544) for EMPA, retained at
`agent-work/sources/game-learning/2107.12544.pdf`. The Frostbite human evidence
is [Tsividis et al. (2017)](https://gershmanlab.com/pubs/Tsividis17.pdf) and
[Mnih et al. (2015)](https://www.nature.com/articles/nature14236), already
retained under `agent-work/sources/games-memory/`.

Each row's work unit is one configured training run on one game, from random
initialization to the published policy. Hyperparameter development, other
games, and other seeds are outside the unit. Where a paper reports a mean over
seeds, the compute describes one run and the performance describes the reported
aggregate; that mismatch is stated in the row's notes.

## Dubey human priors

Dubey et al. built a browser platform game to measure how much of human speed
at an unfamiliar video game comes from prior knowledge. Two experiments matter
here, and only one of them puts humans and the agent on the same game.

The **motivating example** (their Figure 1) is a small platformer with a robot
sprite and a princess. Forty subjects played the original rendering and forty
played a re-textured version that strips semantic and affordance cues. The
paper reports that the first group finished "just under 1 minute of game-play
or 3000 action inputs" and the second took "more than twice the time (2
minutes) and action inputs (6500)". The RL agent solved both, "taking about 4
million action inputs to solve each one". Same game, same terminal condition,
measured on both sides: these are the two rows.

The **ablation study** (their Figures 2 and 3) measures 120 subjects per
condition on a much larger game, with times from 1.8 minutes for the original
to 20 minutes with all object priors masked. No agent was run on that game —
the paper says it "is too large-scale to be solved by RL agents". The agent
step counts in Figure 8 belong to small-game versions on which no human times
were collected. The two halves of the ablation study therefore never meet on
one task, and no ablation row is built. This is the main reason the study
yields two rows rather than eleven.

Human time is read as 60 seconds and 120 seconds, rounding the paper's "just
under 1 minute" and "2 minutes". The time is a mean over the forty finishers in
each condition; participants who abandoned the game are not in it. Both sides
end at the same event, the terminal reward for reaching the door, so the
proficiency target needs no translation and the label is `match` by the task's
own success criterion rather than by construction.

The asymmetry is the usual one and runs one way: the subjects arrive with
vision, motor control and a lifetime of world knowledge, and the network starts
from random weights. The comparison is of game-specific learning.

## ICM A3C compute

The paper names its agent only as A3C augmented with the curiosity module of
Pathak et al. (2017), and publishes no architecture or step-count table, so the
network shape is taken from that method's published configuration: a 42x42x4
input, four 3x3 stride-2 convolutions of 32 channels, an LSTM of 256 units over
the resulting 3x3x32 = 288 features, and policy and value heads. Five actions
are assumed (four arrow keys and a no-op); the action count reaches only the
final 256-wide projection and moves the total by under 0.01%. The curiosity
module carries its own copy of the convolutional trunk, run on the current and
next observation, an inverse model over the concatenated 576 features through a
256-unit hidden layer, and a forward model over features plus a one-hot action.
This is the single largest assumption in the row and it is an assumption about
input resolution and channel width, not about the algorithm.

Per environment step, charge one actor forward, one curiosity forward to score
the intrinsic reward, and a forward-and-backward pass over both networks in the
learner at three forward costs each. That is 5,192,960 FLOPs for the policy
forward, 8,746,496 for the curiosity forward and 55,757,824 per step. Over the
4,000,000 action inputs the paper reports, with the 3% allowance, the run costs
**2.297222e14 FLOPs**. A3C's parallel workers change how the steps are
distributed, not how many there are.

The step count is the same for both renderings, because the paper reports the
same figure for both and separately shows the agent is insensitive to the
manipulation. The two rows therefore differ only on the human side, which is
the comparison the study exists to make.

### game-dubey-original-icma3c

Original rendering. Human 60 seconds, forty finishers; agent 4,000,000 action
inputs to the same terminal state. `match`.

### game-dubey-retextured-icma3c

Re-textured rendering with semantics and affordance cues removed. Human 120
seconds, forty finishers; the agent's requirement is unchanged. `match`.

## Atari 100k successors on Frostbite

BBF, DreamerV3 and EfficientZero V2 all train on Frostbite under the Atari-100k
protocol — 100,000 agent decisions, 400,000 emulator frames, about two hours of
real-time play — and all three end far above the roughly 300-point early-play
endpoint that `research/games-memory/atari-learning.md` uses for DQN and
EfficientZero. Rather than label all three `far_above` against a target none of
them is actually at, each row takes whichever published Frostbite human anchor
sits closest to that agent's score:

| Anchor | Human time, s | Frostbite score | Evidence |
|---|---:|---:|---|
| Early play | 120 | 300 | Tsividis first-episode mean 356, existing row anchor |
| Five-minute reading | 300 | 1000 | Tsividis states directly that about 1000 points corresponds to normal-condition play after about five minutes |
| Professional tester | 7200 | 4335 | Mnih Methods, the anchor of `game-atari-train-muzero` |

The middle anchor is new to the dataset and is taken verbatim from Tsividis
et al. (2017), whose Figure 4 discussion says the instruction and observation
conditions "allow humans to capture approximately 1000 points in their first
episode — this corresponds to human performance after about 5 minutes of play
under normal conditions". That sentence is the authors' own reading of their
own 71-participant normal-condition timing data, so the evidence class is
`task_timings` with those 71 sessions as the contributing sample, on the same
footing as the 120-second anchor's donor count. It is a reading of a learning
curve, not a recovered mean hitting time, and the row says so.

Assigning by proximity means BBF (2384.8) and DreamerV3 (3377) take the
professional-tester anchor and land `below` it, and EfficientZero V2 (1136.3)
takes the five-minute anchor and lands `match`. Under the 120-second anchor all
three would be `far_above`; that alternative is a uniform relabelling, not a
different compute estimate, and nothing else in the rows would change.

The starting-point asymmetry is inherited and unchanged: the tester brings
general video-game skill and the networks start from random weights. The
Atari-100k agents are evaluated on their own protocols rather than Mnih's
five-minute episode cap, so every row flags `different_assessment`.

DreamerV3's Frostbite score is 3377 in its own paper at the default 200M model
size. EfficientZero V2 quotes 909 for DreamerV3, which is the smaller S
configuration; the row uses the authors' own number for the size whose
hyperparameters are published in full.

## BBF compute

Schwarzer et al. use the 15-layer Impala-CNN ResNet with every layer's width
scaled 4x, so the base channel widths (16, 32, 32) become (64, 128, 128). Each
of the three stages is a 3x3 convolution, a 3x3 stride-2 max-pool and two
residual blocks of two 3x3 convolutions; on an 84x84x4 input the stage
resolutions after pooling are 42, 21 and 11, giving an 11x11x128 = 15,488
feature vector. The encoder costs 802,934,784 multiply-accumulates. The dueling
distributional head is assumed to be a 2048-unit hidden layer over those
features with 51 atoms and 18 actions; the head is 4% of the encoder, so the
width assumption is not load-bearing. The SPR self-prediction branch adds a
two-convolution latent transition model at 11x11x128, a 15,488 to 2048
projection and a 2048 to 2048 prediction head, applied at each prediction
depth. The update horizon anneals from 10 to 3 after each reset; a mean depth
of 5 is used.

Replay ratio 8 at 100,000 environment steps gives 800,000 gradient steps, and
the batch size is 32 — the paper states EfficientZero's batch is eight times
theirs, and EfficientZero's is 256. That is 25,600,000 replayed samples. Per
sample: three forward-equivalents over the online path (encoder, Q head and the
five-step SPR branch), one online and one target forward at the bootstrap
state, and five target-encoder passes over the future observations for the SPR
targets, which are stop-gradient and carry no backward. Those five encoder
passes are 43% of the sample cost, so the mean-depth assumption is the largest
single uncertainty in this row. The per-sample cost is 1.8543677e10 FLOPs.
Adding the 100,000 actor forwards and the 3% allowance gives
**4.891320e17 FLOPs**.

The paper's reported 10 hours on half an A100 is a reasonableness check rather
than an input: the estimate implies 1.36e13 FLOP/s, about 9% of a half-A100's
bf16 peak, which is unremarkable for small-batch RL stepping a CPU emulator.
Periodic network resets reinitialize weights; they do not change the number of
gradient steps.

## DreamerV3 compute

Hafner et al. publish the inputs directly. Atari100K uses 400,000 environment
steps at action repeat 4, replay ratio 128, batch shape 16 x 64, and the
default 200M-parameter model size. Dividing the replay ratio by the 1,024 time
steps in a minibatch and by the action repeat gives one gradient step per 32
environment steps, so 12,500 gradient steps over 12,800,000 replayed positions.
Each gradient step also imagines a 15-step rollout from every one of its 1,024
latent states, which is 192,000,000 imagined positions.

Charge 6ND on both: the replayed positions against the full 200M parameters,
and the imagined positions against the 90M that actually run in imagination —
the block-diagonal GRU, the dynamics predictor, the reward and continue heads,
the actor and the critic, with the convolutional encoder and decoder excluded
because imagination never touches pixels. The 90M split is derived from the
Table 3 shapes at model dimension 1024 and is an estimate, not a reported
figure; the imagination term is 85% of the total, so this split is the row's
main uncertainty. The actor's 100,000 decision forwards are negligible. With
the 3% allowance the run costs **1.226297e17 FLOPs**.

The reported 0.1 A100-days implies 1.4e13 FLOP/s, about 5% of the card's bf16
peak, which is what a sequentially-unrolled recurrent model at batch 16 should
look like.

## EfficientZero V2 compute

Wang et al. state that the image architecture follows EfficientZero's, so the
per-call costs are the ones already established in
`research/games-memory/atari-learning.md#efficientzero-compute`: representation
297,271,296 FLOPs, prediction 5,569,216, and dynamics-plus-reward-plus-prediction
18,174,720 per recurrent expansion. What changes is the search and the update
schedule. Their Table 3 gives batch size 256, unroll 5, TD steps 5,
update-to-data 1, and 16 simulations with 8 sampled actions on Atari 100k. One
root search therefore costs 302,840,512 + 16 x 18,174,720 = 593,636,032 FLOPs,
against EfficientZero's 1,211,576,512 at 50 simulations.

Update-to-data 1 over 100,000 collected decisions gives 100,000 learner
updates, against EfficientZero's 120,000. Reanalysis is assumed to run one
Gumbel search at each of the six states in a sample's unroll window, matching
EfficientZero's structure, which the paper says it follows; unlike
EfficientZero it is a single search per state rather than separate value and
policy searches, because the value target is the mixed search-or-TD target
rather than a dedicated root-value search. That gives 153,600,000 reanalysis
roots. The learner sample cost is EfficientZero's 2,905,060,096 FLOPs,
unchanged: same unroll depth, same consistency branch, same architecture.

| Component | FLOPs |
|---|---:|
| Reanalysis | 91,182,494,515,200,000 |
| Learner | 74,369,538,457,600,000 |
| Collection searches | 59,363,603,200,000 |
| Evaluation allowance | 1,253,759,299,584,000 |

The evaluation allowance transfers EfficientZero's schedule — thirteen
checkpoint assessments of 32 episodes at 3,000 decisions plus a final 32
episodes at the 27,000-decision cap — and contributes under 1%. With the 3%
allowance the total is **1.718711e17 FLOPs**. No GPU time is reported for this
run, so there is no hardware cross-check.

### game-atari-train-bbf

BBF Frostbite 2384.8 against the professional tester's 4334.7 after two hours of
practice. After the 65.2 random floor that is 54% of the tester, so `below`.

### game-atari-train-dreamerv3

DreamerV3 Frostbite 3377 against the same 4334.7, 78% after the floor. `below`.

### game-atari-train-efficientzerov2

EfficientZero V2 Frostbite 1136.3 against the roughly 1000 points Tsividis
reads off five minutes of normal play. `match`.

## Withheld rows

Nothing in this section is in `points.csv`. The corresponding entries are in
`agent-work/removed/`.

**Every EMPA row.** Tsividis et al. (2021) is the largest measured
human-learning corpus available for this comparison — 300 participants across
90 games, with DDQN and Rainbow baselines — and it yields nothing, for two
independent reasons. The human learning curves are published in agent steps,
and the paper states no conversion from steps to seconds; it says only that
humans learn "in a matter of minutes (corresponding to a few hundred steps)",
which does not support a per-game duration. And on every game for which the
paper prints numbers, the deep RL baselines fail to reach the human target
inside the 1,000,000-step budget: on Bait DDQN solves two of five levels and
fails the rest, on Zelda four of five, on Zelda 1 it never passes level three,
on Butterflies four of five. Those rows would be withheld for substantial
underperformance even if the human times existed. The per-game numbers that
would settle the remaining games live only in the Figure 3 scatter, not in a
table.

**Dubey ablation conditions.** Eleven measured human conditions on the large
game, no agent run on that game. See the Dubey section.

**The whole Sonic grid of Nichol et al. (2018).** Two Rainbow per-level rows
were built and then withheld at merge: the pair is the two best of eleven test
levels, selected by the performance floor itself, and each row charges the whole
two-hour practice budget to a single level when the practice transfers across
all eleven. PPO clears half the human on no level, the two joint variants are
withheld on attribution because their pretraining is shared across the eleven
test levels, Rainbow's other nine levels fall below half the human score, the
five aggregate rows all fall below half the human aggregate of 7438.2, and JERK
is a scripted non-neural algorithm with no FLOP recipe of the kind this dataset
uses. The rows, the model record, the compute recipe and the reasons are in
`agent-work/removed/game-learning/`.

**DreamerV3-S on Frostbite.** The 909 figure EfficientZero V2 quotes is the
smaller S configuration. The size whose hyperparameters are published in full is
the 200M default, which is the row built above.
