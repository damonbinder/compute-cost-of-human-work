# Physical Intelligence π0.6, π*0.6 and π0.7

*Created 2026-09-14 12:14.*

Thirteen rows across three Physical Intelligence models on nine household,
laundry, cafe and factory manipulation tasks. The family is unusual in this
category because the compute leg and the AI's own duration are both published:
the [π0.6 model card](https://website.pi-asset.com/pi06star/PI06_model_card.pdf)
gives the whole architecture and the evaluations report **throughput in
successes per hour**, which converts directly into robot seconds per completed
task. The human leg is the weak half — nothing in the family publishes a timed
human on any of these tasks — so every human duration here is our estimate,
recorded as `llm_estimate_judgment`.

Retained sources sit in `agent-work/sources/physical-intelligence/`: the model
card PDF and its rendered pages, the π*0.6 paper (arXiv 2511.14759v1) and the
π0.7 paper PDF and blog post.

## What each source supplies

| Source | Date | Supplies |
|---|---|---|
| π0.6 model card | 2025-11-17 | Architecture, 63 ms per chunk on one H100, throughput and success rate on four static and four mobile tasks |
| π*0.6 paper (arXiv 2511.14759) | 2025-11-18 | Task success criteria with time limits, 50 Hz control, throughput and success rate for the RL specialists |
| π0.7 paper and blog | 2026-04-16 | 5 denoising steps, 50-step chunks, Ĥ ∈ {15, 25} executed, 38–127 ms inference, throughput normalized to the π*0.6 specialists, and the one human comparison in the family |

## The architecture gives per-chunk FLOPs

π0.6 is a vision-language backbone initialized from **Gemma 3 4B**, a **SigLIP
400M** vision encoder and an **860M action expert** with the same layer count as
the backbone. It takes up to four 448×448 images and produces a 50-step action
chunk with five flow-matching denoising steps; the card quotes **63 ms per chunk
on a single H100 with three cameras**, and π0.7 quotes 38 ms for its minimal
variant and 127 ms with the memory encoder and subgoal images enabled. Those
latencies are a cross-check, not the compute estimate: at batch one a 5B model is
memory-bandwidth bound, so wall-clock time understates how much arithmetic the
hardware could have done. The recipe below implies 139 TFLOP/s during the 63 ms,
about 14% of an H100's dense BF16 peak, which is the right order for small-batch
inference and so leaves the latency and the operation count consistent.

Shapes come from the published Gemma 3 4B configuration — 34 layers, width 2560,
MLP 10240, 8 query heads of 256 and 4 key/value heads, SigLIP tower of 27 layers
at width 1152 with patch 14 and 256 emitted tokens per image. The backbone's
non-embedding parameters are 3.209×10⁹ and the vision tower's 4.111×10⁸; the
action expert's width follows from spreading its reported 860M over the
backbone's 34 layers at Gemma's per-layer parameter-to-width ratio, giving about
1325.

### Compute recipe

Per action chunk, counting two operations per multiply-add, with three cameras at
448×448 (1024 encoded patches each, 256 tokens each into the backbone), 20 text
positions for the task prompt and conditioning metadata, 2 state positions, a
790-position prefix, 50 action tokens and 5 denoising steps:

| Component | FLOPs per chunk |
|---|---|
| Vision encoder weights | 2.526e12 |
| Vision encoder attention | 3.914e11 |
| Backbone prefix weights | 5.070e12 |
| Backbone prefix attention | 1.738e11 |
| Action expert weights | 4.300e11 |
| Action expert attention | 3.785e10 |
| Subtotal | 8.628e12 |

Attention is priced at 4 × layers × query width × context per processed position,
the same convention as `research/attention-correction.md`, and is carried inside
this operation count rather than through the `attention_context` columns, exactly
as the earlier `research/robotics-science/pi0-shirt.md` recipe does.

On top of the subtotal, **π0.6 and π*0.6 take a 10% allowance** and **π0.7 a 20%
allowance**. The 10% covers the backbone's low-frequency discrete outputs — the
FAST action tokens and the predicted subtask string, which the model card says run
below the action rate — plus projections and embeddings. π0.7's extra 10% covers
its MEM video-history encoder and the separate Gemma 3 4B high-level policy that
supplies subtask instructions. π0.7's world model, a 14B BAGEL variant that
generates subgoal images on four H100s, is **excluded**: it belongs to the
π0.7 (GC) configuration, and the out-of-the-box dexterity results used here are
plain π0.7.

Chunks per second come from the π0.7 paper's deployment statement: 50-step chunks
at 50 Hz with Ĥ ∈ {15, 25} steps executed before the next inference. Taking the
midpoint, Ĥ = 20, gives **2.5 chunks per second**. The extremes give 2.0 and 3.33,
so the whole compute column moves by −20%/+33% under that assumption alone.

Multiplying through:

| Model | FLOPs per chunk | FLOPs per robot-second |
|---|---|---|
| π0.6, π*0.6 | 9.491e12 | 2.373e13 |
| π0.7 | 1.035e13 | 2.588e13 |

π*0.6 shares π0.6's architecture; RL with Recap adds only an advantage-indicator
text token to the prompt, which is inside the 20-position text allowance.

The arithmetic is in `pi_chunk_flops.py` in this folder; it writes
`agent-work/derived/physical-intelligence/pi-flops.csv`.

### Throughput read-off

Throughput is published only as bar charts. Values were recovered by measuring
bar tops and gridline positions in pixels on 400 dpi renders of the source PDFs
and converting with the labelled axis ticks. Where a value can be checked against
prose it agrees: the card says π0.6 assembles the box "20% of the time" against a
measured bar of 15% with its error bar reaching 20%, and the π*0.6 text says box
assembly reaches "about 90%" success against measured subtask bars of 90–97%.

| Figure | Task | Model | Successes/hour | Success rate |
|---|---|---|---|---|
| Card Fig. 2 | Shirt folding (flat start) | π0.6 | 49.0 | 0.855 |
| Card Fig. 2 | Laundry, T-shirts and shorts | π0.6 | 18.8 | 0.625 |
| Card Fig. 2 | Box building | π0.6 | 4.55 | 0.15 |
| Card Fig. 2 | Table bussing | π0.6 | 43.8 | 0.99 |
| Card Fig. 3 | Laundry pickup into basket | π0.6 | 101.1 | — |
| Card Fig. 3 | Tidy bed | π0.6 | 24.6 | — |
| Card Fig. 3 | Dishes in sink | π0.6 | 43.3 | — |
| Card Fig. 3 | Items in drawer | π0.6 | 70.9 | — |
| π*0.6 Fig. 7, 8 | Laundry, T-shirts and shorts | π*0.6 | 59.9 | 0.96 |
| π*0.6 Fig. 7, 8 | Laundry, button-up shirt | π*0.6 | 8.31 | 0.74 |
| π*0.6 Fig. 7, 8 | Double espresso | π*0.6 | 28.7 | 0.92 |
| π*0.6 Fig. 7, 8 | Box assembly | π*0.6 | 13.22 | 0.90 |
| π0.7 Fig. 6 | Laundry, T-shirts and shorts | π0.7 | 58.6 | 0.97 |
| π0.7 Fig. 6 | Laundry, button-up shirt | π0.7 | 12.1 | 0.74 |
| π0.7 Fig. 6 | Double espresso | π0.7 | 27.6 | 0.97 |
| π0.7 Fig. 6 | Box building | π0.7 | 19.3 | 0.88 |

The mobile tasks report average task progress rather than a success rate. π0.7's
figure gives throughput normalized to the π*0.6 specialist, measured at 0.979,
1.457, 0.963 and 1.457 of the specialist's rate, so its absolute rates are the
π*0.6 rates scaled by those factors.

Throughput is defined as successfully completed tasks per hour over the whole
evaluation, so 3600 divided by it is **robot wall-clock seconds per completed
task including the time spent on failed attempts**. Every row therefore carries
`compute_statistic = total_per_completed_sample` and `compute_subset = all`.

## Task definitions and success criteria

The π*0.6 paper states the criteria and time limits, and the π0.5 paper supplies
the mobile-task rubrics.

- **Laundry (T-shirts and shorts).** Retrieve a T-shirt or shorts from a basket,
  flatten, fold, stack in the top right corner of the table, within 200 s.
- **Laundry (diverse, hardest item).** The same, for a button-up shirt, within
  500 s.
- **Shirt folding (flat start).** The π0 task: a T-shirt already flat on the
  table, folded and stacked. This is the same work unit as the existing
  `robo-shirt-pi0` row.
- **Make espresso.** Pick up the portafilter, grind into it, tamp, lock into the
  machine, bring the cup, extract a double shot, serve. All steps within 200 s
  without dropping the portafilter or spilling.
- **Box assembly.** From a flattened cardboard sheet to an assembled box with a
  label attached and the box stacked in a crate, within 600 s, in a factory
  deployment.
- **Table bussing.** The π0 task: clear a table, trash into the trash bin and
  dishes into the dish bin. The number of objects on the table is not published.
- **Laundry pickup.** Mobile bimanual: pick clothing off the floor and place it in
  the laundry basket. The π0.5 rubric scores this out of 3 for one clothing item.
- **Tidy bed.** Mobile bimanual: straighten the blanket over the sheets and place
  two pillows at the head of the bed. The π0.5 rubric scores this out of 5.

## Human time estimates

No publication in this family times a human doing any of these tasks with their
own hands, and Physical Intelligence has released no teleoperation data whose
episode durations could be read off. Every human duration below is therefore our
own judgment estimate, built by summing the steps a competent adult would take at
the same prepared workstation, and every row records
`human_time_evidence = llm_estimate_judgment` with
`human_time_statistic = point_estimate`.

| Task | Human seconds | Build-up |
|---|---|---|
| Fold an already-flat T-shirt | 15 | Adopted unchanged from `research/robotics-science/pi0-shirt.md` so the three models on this task share one baseline |
| Fold a T-shirt or shorts from a basket | 20 | 3 s retrieve, 6 s shake out and flatten, 9 s fold, 2 s stack |
| Fold a button-up shirt from a basket | 30 | 8 s retrieve and flatten, 20 s smooth, fold sleeves back, fold in thirds and halve, 2 s stack |
| Make a double espresso | 55 | 4 s portafilter, 8 s grind, 5 s tamp, 3 s lock in, 3 s cup, 27 s extraction, 5 s serve |
| Assemble and label a packaging box | 18 | 10 s fold and tuck flaps, 5 s peel and apply the label, 3 s place in the crate |
| Bus a table | 30 | Roughly six items carried to a dish bin and a trash bin at about 5 s each |
| Pick one clothing item off the floor into the basket | 8 | 4 s cross the room, 2 s stoop and grasp, 2 s place |
| Tidy a bed | 45 | 30 s straighten the blanket over the sheets from both sides, 15 s place two pillows neatly |

Two caveats belong with these numbers. The espresso figure is wall-clock for one
serially executed drink; about 27 s of it is extraction, during which a barista
would normally start the next drink, so the strictly active-time reading is closer
to 30 s. The two espresso rows take that reading as `human_time_low` and the
wall-clock 55 s as `human_time_high`, and the flat-shirt row takes the
ten-to-twenty-five-second range of `research/robotics-science/pi0-shirt.md` with the
central it already adopts from there. And the table-bussing figure assumes six objects, because the evaluation's
object count is not published — that row carries `different_task` for exactly this
reason, as do the two mobile rows whose rubric item counts are only partly
specified.

### Bounds on the eight budgets

Added 2026-09-17. Each budget above is a sum of named steps, and each bound below
re-runs that sum with one or more steps at its own end. Nothing is a factor on the
central.

The fold-from-basket rows take their bound from a sibling row rather than from a
re-run. Retrieving the garment is 3 s and the remaining 17 s — shake out, flatten,
fold, stack — is the same work as the `robo-shirt-pi0` task, whose own note argues
**10 to 25 seconds** for it on garment size and care. So 3 + 10 = **13 s** and
3 + 25 = **28 s**.

| Task | Low | Central | High | Steps at their ends |
|---|---:|---:|---:|---|
| Fold a T-shirt or shorts from a basket | 13 | 20 | 28 | 3 s retrieve, then `pi0-shirt.md`'s own 10-25 s for flatten, fold and stack |
| Fold a button-up shirt from a basket | 20 | 30 | 46 | retrieve and flatten 5-12, smooth and fold sleeves, thirds and halve 14-30, stack 1-4 |
| Assemble and label a packaging box | 12 | 18 | 29 | fold and tuck the flaps 7-16, peel and apply the label 3-8, place in the crate 2-5 |
| Bus a table | 20 | 30 | 45 | four to nine objects at the 5 s per-item transfer the central uses |
| Pick one clothing item off the floor | 5 | 8 | 14 | cross the room 2-8, stoop and grasp 1.5-3, place 1.5-3 |
| Tidy a bed | 28 | 45 | 70 | straighten the blanket over the sheets 20-50, place two pillows 8-20 |

Two of these deserve a word. The table-bussing bound moves the object count and
holds the per-item rate, because the count is the one thing the evaluation does not
publish and the row already carries `different_task` for it; four to nine objects is
what a table cleared into a dish bin and a trash bin holds, and 5 s an item is the
dataset's own figure for an arm's-reach transfer, `robo-binpick`. The laundry-pickup
bound is almost all in the crossing step, because the room and the distance from the
item to the basket are not published and a mobile base's traverse is the only part
of that eight seconds that can be several times what the central charges.

## The only human-performance statement in the family

π0.7 contains one direct human comparison, and it is worth stating precisely
because it is easy to over-read.

The claim covers **shirt folding on the bimanual UR5e platform, zero-shot**. No
laundry-folding data was collected on the UR5e; the operators had collected the
folding data on the smaller static bimanual robot but had never attempted the task
on the UR5e. Ten operators were recruited from the top 2% of Physical
Intelligence's operator fleet by experience, a mean of about 375 hours across all
platforms, and each performed three trials, 30 in total, with no practice period
and with the same initial shirt configuration, time limit and rubric as the policy
evaluation. **The operators achieved 90.9% task progress and an 80.6% success
rate; π0.7 (GC) achieved 85.6% task progress and an 80% success rate.**

So the claim is a *success-rate* match between a policy and expert teleoperators,
both operating the same unfamiliar robot, on one task. It is not a claim about the
model matching a person folding a shirt by hand, and it says nothing about speed:
neither the operators' nor the policy's episode durations are published, and this
task does not appear in any throughput figure. Both legs of a row are therefore
missing, and no row is built from it. It is the strongest human-comparison
evidence in the family and it applies to no other task in this note.

## Rows withheld

| Task and model | Reason |
|---|---|
| Box building, π0.6 out of the box | 15% success, 20% by the card's prose. A human succeeds essentially always, so the AI is substantially below the baseline rather than near it |
| Dishes in sink, items in drawer, π0.6 | The number of dishes or items in one evaluation episode is not published, so no human duration can be matched to the work unit |
| Shirt folding on the UR5e, π0.7 versus teleoperators | Neither the policy's nor the operators' episode durations are published; there is no time on either leg |
| All π0.5 comparison bars | Outside this collection's scope, and π0.5 scores zero on laundry folding and box assembly |
| Laundry targeted-failure-removal ablation, π*0.6 | An ablation configuration with an adversarial initial condition; its throughput is not reported on the same footing |

## Model records

Three new models. All three share the recipe above, so none carries a single
FLOPs-per-token coefficient: the vision encoder, backbone and action expert
process different position counts.

| Field | π0.6 | π*0.6 | π0.7 |
|---|---|---|---|
| Release date | 2025-11-17 | 2025-11-18 | 2026-04-16 |
| Basis | Model card publication | arXiv v1 submission | Blog and paper publication |
| Encoder parameters | 411,070,464 | 411,070,464 | 411,070,464 |
| Decoder parameters | 4,068,642,560 | 4,068,642,560 | 4,068,642,560 |

Encoder parameters are the SigLIP tower computed from the published Gemma 3
vision configuration. Decoder parameters combine the Gemma 3 4B text tower's
non-embedding weights, 3,208,642,560, with the reported 860M action expert; the
embedding table is excluded because it is a lookup, not a per-position matrix
multiply. None of the three has a public weight release, so the release dates are
publication dates for the results.
