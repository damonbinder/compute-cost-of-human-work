# 2025 BEHAVIOR Challenge

*Created 2026-09-14 13:52.*

Five rows on one model: the policy that won the 2025 BEHAVIOR Challenge, on the
five household activities out of fifty where it fully completed the activity in
a majority of its evaluation episodes. The human side is unusually strong for a
robotics row — the mean of 200 measured teleoperation demonstrations per
activity, read off the released dataset — and the compute side is derived from
the entry's own published code, which fixes every shape and rate the recipe
needs. Both sides run inside a simulator, and the human drives the same
simulated robot through a teleoperation rig, so the comparison is a
simulated-robot comparison throughout.

| | |
|---|---|
| Benchmark | [2025 BEHAVIOR Challenge](https://behavior.stanford.edu/challenge/index.html) at NeurIPS 2025, 50 BEHAVIOR-1K household activities in OmniGibson on NVIDIA Isaac Sim |
| Robot | R1 Pro mobile bimanual, two 7-DOF arms with parallel-jaw grippers, 23-D action space |
| Human | JoyLo whole-body teleoperation, 10,000 demonstrations, 200 per activity, 1,103 hours |
| AI | Robot Learning Collective's PiBehavior, a π0.5 derivative, 1st place with a 0.2605 public and 0.2599 private q-score |
| Rows | 5 built, 45 activities withheld, and every other entry withheld |

Retained sources sit in `agent-work/sources/behavior/`: the two published entry
reports (arXiv 2512.06951 and 2512.10071), the winning entry's per-task score
figure, the released dataset's `meta/episodes.jsonl` and `meta/info.json`, and
`docs/challenge/task_data.json` from the BEHAVIOR-1K repository.

<a id="human-time"></a>

## The human leg is measured, and the measurement is exact

The challenge's demonstration corpus is a LeRobot dataset,
[behavior-1k/2025-challenge-demos](https://huggingface.co/datasets/behavior-1k/2025-challenge-demos),
whose `meta/episodes.jsonl` gives the frame count of every one of the 10,000
episodes and whose `meta/info.json` gives the 30 Hz frame rate. Grouping the
episodes by activity gives 200 per activity and a mean episode length per
activity in seconds. The corpus mean is 397.0 s, which reproduces the
challenge's published "6.6 minutes on average" exactly, and the longest
activity's mean is 869 s, which reproduces its "longest tasks averaging 14
minutes".

The same durations appear, rounded to the second, as the `duration` field of
`docs/challenge/task_data.json` in the
[BEHAVIOR-1K repository](https://github.com/StanfordVL/BEHAVIOR-1K), and the
winning entry's code uses them a third way: its per-activity stage count is
`clip(ceil(duration × 30 / 900), 5, 15)`, which reproduces its hard-coded
`TASK_NUM_STAGES` table for all fifty activities. Three independent uses of the
same number agree, so the human duration is measured rather than estimated.

### Per-activity durations for the five built rows

| Activity | Demonstrations | Mean s | Median s | Min s | Max s |
|---|---|---|---|---|---|
| turning_on_radio | 200 | 71.7 | 70.3 | 32.3 | 145.1 |
| make_microwave_popcorn | 200 | 107.9 | 106.7 | 52.8 | 161.8 |
| cook_bacon | 200 | 256.0 | 246.6 | 204.0 | 382.9 |
| cook_hot_dogs | 200 | 304.8 | 293.6 | 217.2 | 747.0 |
| moving_boxes_to_storage | 200 | 486.5 | 484.8 | 312.5 | 656.7 |

Every row records the mean. The medians sit below the means on all five, by 2%
to 4%, so the choice of statistic moves nothing material.

### What the teleoperator is, and what the duration excludes

The demonstrator is a trained operator piloting the same simulated R1 Pro the
policy controls, through the JoyLo whole-body interface — the `robo-cabinet-aloha`
convention, where the human works through the robot rather than with their own
hands. They are recorded as `expert`.

One feature of the collection procedure matters for the comparison and is
recorded as `different_attempt_selection`. The winning entry's failure analysis
states that activities were divided into steps during collection and "if the
operator failed at a given step, the simulation was rolled back to the start of
that substep". The stored episode is therefore a concatenation of successful
substeps, and its duration excludes the operator's own failed attempts. The
policy's episode duration, by contrast, includes everything it does inside one
evaluation episode, recoveries included. The human figure is the cleaner of the
two and the AI figure is the more inclusive, which biases the comparison against
the AI.

## Performance: five activities out of fifty were basically done

The challenge scores each activity over 10 held-out evaluation instances. The
ranking metric is the q-score, the mean fraction of BDDL goal conditions
satisfied at episode end; binary full success is reported alongside it. The
evaluation time limit per activity is twice that activity's mean demonstration
duration.

The winning entry published its full public-leaderboard result as a 50 × 10
heatmap of per-episode scores, activities ordered by mean demonstration
duration. Reading the cell colors back through the Greens colormap recovers the
matrix; the recovered matrix has mean 0.2605 and a fraction 0.1120 of cells at
1.0, which are exactly the entry's published public q-score and public binary
success rate. The row ordering matches the demonstration-duration ordering
exactly, which fixes each row's identity. The read-off is therefore exact, not
approximate.

<a id="per-activity-results"></a>

| Activity | Episodes fully completed of 10 | Task q-score | Built |
|---|---|---|---|
| make_microwave_popcorn | 9 | 0.897 | yes |
| cook_hot_dogs | 8 | 0.848 | yes |
| cook_bacon | 7 | 0.755 | yes |
| turning_on_radio | 6 | 0.598 | yes |
| moving_boxes_to_storage | 6 | 0.648 | yes |
| picking_up_trash | 4 | 0.665 | no |
| wash_a_baseball_cap | 3 | 0.449 | no |
| clean_boxing_gloves | 2 | 0.199 | no |
| spraying_fruit_trees | 2 | 0.299 | no |

Nine further activities completed exactly one episode of ten and thirty-two
completed none. The counts check against the entry's own published binary success
rate: 56 of the 500 cells sit at 1.0, which is the 11.20% it reports, and the
five built rows account for 36 of them. The line for building a row is a majority of the
ten evaluation episodes fully completed, because a teleoperator completes the
activity essentially always and an entry that fully finishes the job in fewer
than half its attempts has not basically done the job.

Against a human baseline that succeeds by construction, 9 of 10 is broadly
comparable and earns `match`; 6 to 8 of 10 is noticeably worse while still doing
the job, and earns `below`. The 85% threshold follows the existing
`robo-cabinet-aloha` row, which is labelled `match` on 17 of 20.

<a id="compute-recipe"></a>

## The compute recipe comes out of the entry's own code

The winning policy is π0.5 with the language path removed. Every shape and rate
below is read from the entry's
[released code](https://github.com/IliaLarchenko/behavior-1k-solution) and its
[report](https://arxiv.org/abs/2512.06951), not assumed.

- **Vision.** A frozen SigLIP So400m/14 tower over three 224×224 RGB cameras —
  head, left wrist, right wrist — giving 256 patches per image and 768 image
  tokens. 27 layers at width 1152, the same tower as the π0.6 recipe in
  `research/physical-intelligence/physical-intelligence.md`, 411,070,464
  non-embedding parameters.
- **Backbone.** openpi's `gemma_2b`: 18 layers, width 2048, MLP 16,384, 8 query
  heads of 256 and 1 key/value head, 1,981,808,640 non-embedding parameters.
  Text is gone — 50 trainable task embeddings replace the prompt — so the prefix
  carries 5 task-related tokens (one base embedding plus four stage-conditioned
  tokens) and 32 state tokens, the 23-D proprioception padded to the model's
  action dimension of 32 and discretized into per-dimension embeddings. The
  prefix is 768 + 5 + 32 = 805 positions.
- **Action expert.** openpi's `gemma_300m`: 18 layers, width 1024, MLP 4096,
  same 8 × 256 query shape, 311,427,072 parameters, which reproduces the report's
  "∼311M". It predicts a 30-step action chunk with **20 flow-matching denoising
  steps**, the default in the entry's own `serve_b1k.py`.
- **Execution rate.** The wrapper predicts 30 actions, executes 26 of them
  compressed by cubic spline into 20 steps at 30 Hz, and keeps 4 for inpainting.
  One inference cycle therefore covers 20/30 s of simulated robot time, so the
  policy runs **1.5 inference cycles per robot-second**.

Per inference cycle, counting two operations per multiply-add and pricing
attention at 4 × layers × query width × context per processed position — the
same convention as `research/attention-correction.md`, carried inside the
operation count rather than through the `attention_context` columns:

| Component | FLOPs per cycle |
|---|---|
| Vision encoder weights | 6.314e11 |
| Vision encoder attention | 2.446e10 |
| Backbone prefix weights | 3.191e12 |
| Backbone prefix attention | 9.556e10 |
| Action expert weights | 3.737e11 |
| Action expert attention | 7.388e10 |
| Subtotal | 4.390e12 |
| With 10% allowance | 4.829e12 |

The 10% allowance covers the learnable KV-cache transform across all 18 backbone
layers, the action and time projections, the stage classifier and the
task–stage fusion MLPs, matching the allowance the π0.6 rows carry. The FAST
auxiliary head is training-only and is excluded.

At 1.5 cycles per second that is **7.243e12 FLOPs per robot-second**. The entry
ran inference on a single RTX 4090, whose dense BF16 peak is roughly 1.7e14
FLOP/s, so the recipe implies about 4% of peak sustained and about 29 ms of
arithmetic per cycle inside a 667 ms budget. Small-batch flow-matching inference
is memory-bandwidth bound, so a few percent of peak is the right order and the
recipe and the hardware are consistent.

No text tokens enter the estimate, because the entry removed text processing
entirely. Both token columns are `not_applicable`; image patches, state
positions and action positions stay in the calculation above, as the column
definitions require.

The arithmetic is in `behavior_flops.py` in this folder; it writes
`agent-work/derived/behavior/behavior-flops.csv`.

<a id="episode-duration"></a>

## The policy's episode duration is an assumption, and the row states it

Neither entry publishes per-episode simulated time. The challenge tracks it as a
secondary efficiency metric, but no per-activity value is released, so the
number of inference cycles per episode has to be assumed. Three anchors bracket
it:

| Scenario | AI episode duration | Basis |
|---|---|---|
| Compressed | mean demonstration / 1.3 | The policy tracks the demonstrated trajectory and executes it at the 1.3× spline compression, with no recovery time |
| Central | mean demonstration | Compression is cancelled by recovery attempts and by the compression being disabled whenever the gripper state changes |
| Time limit | 2 × mean demonstration | The evaluation cap, a hard ceiling on any episode |

Every row records the central scenario: **the policy's episode runs for the same
simulated time as the mean teleoperation demonstration of that activity**. The
entry's report supports it in both directions. It is trained by behavior cloning
on those very demonstrations and follows their trajectories, which is why the
compression exists at all; but the compression is explicitly disabled around
gripper transitions, which are most of the manipulation, and the entry's
headline recovery mechanism re-opens the gripper and re-attempts failed grasps,
which adds cycles inside a successful episode.

The scenario moves compute by −23%/+100% and nothing else in the row. The
`compute_flops_low` and `compute_flops_high` columns cover a different and
specific pair of uncertainties, so they stay blank and the band lives here.

| Activity | Compressed FLOPs | Central FLOPs | Time-limit FLOPs |
|---|---|---|---|
| turning_on_radio | 3.995e14 | 5.193e14 | 1.039e15 |
| make_microwave_popcorn | 6.012e14 | 7.815e14 | 1.563e15 |
| cook_bacon | 1.426e15 | 1.854e15 | 3.708e15 |
| cook_hot_dogs | 1.698e15 | 2.208e15 | 4.415e15 |
| moving_boxes_to_storage | 2.711e15 | 3.524e15 | 7.047e15 |

## Simulation is the comparison's standing caveat

Both sides act in OmniGibson, and neither side is a person doing the activity
with their own hands. Two consequences are worth stating plainly.

Simulated household manipulation is harder than the real thing for the human and
probably easier for the policy. The winning entry's own analysis says operating
a humanoid-like robot in simulation "is challenging for human operators", which
inflates the human durations relative to a person cooking bacon in a kitchen; a
person cooks six rashers in far less than 256 s of hands-on time. The durations
here are teleoperation durations, not unaided-human durations, and the rows say
so. Against that, the policy faces no sensor noise, no calibration drift and no
contact-model error, which is the `phys-vima200m-visual-manipulation`
precedent.

The endpoint is well specified, which is the one thing simulation buys
unambiguously. Each activity's completion is a BDDL goal-condition set evaluated
by the simulator, identical for the demonstration and the policy, so the Roomba
failure mode — a nominally-shared task where the two sides stop at different
points — does not arise here.

## Rows withheld

| What | Reason |
|---|---|
| 45 of the 50 activities, winning entry | Fewer than half the evaluation episodes fully completed; 32 completed none. The nine with any full completion are in the results table above; all 45 are enumerated in `agent-work/removed/behavior/dispositions.csv` |
| Team Comet's competition entry, all activities | 2nd place at a 0.2514 test q-score, but the report publishes no per-activity result for the submitted system |
| Team Comet's post-challenge model, all activities | Its per-activity figure is the only per-activity data it gives, and the 25 accuracies shown average 26.8% against the 15% validation success rate stated in the same caption and table, so the two cannot both be right. It is also not the challenge entry, and the report does not say which inference configuration produced it |
| SimpleAI Robot, The North Star, Embodied Intelligence | Placed 3rd to 5th; no technical report, no architecture and no per-activity result published |
| Efficiency-metric rows | The challenge's simulated-time, distance-navigated and hand-displacement metrics are tracked but not released per activity |

<a id="model-record"></a>

## Model record

One new model.

| Field | Value |
|---|---|
| model_id | `pi-behavior-rlc-2025` |
| Release date | 2025-12-07, the report's date; weights are public on Hugging Face |
| Encoder parameters | 411,070,464 |
| Decoder parameters | 2,293,235,712 |

Decoder parameters combine the `gemma_2b` backbone's non-embedding weights,
1,981,808,640, with the `gemma_300m` action expert's 311,427,072. The embedding
table is excluded as a lookup, and the 50 task embeddings and 596 stage
embeddings with it. The three components process different position counts, so
no shared per-token coefficient applies and `flops_per_token` is
`not_applicable`.
