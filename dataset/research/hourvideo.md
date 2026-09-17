# HourVideo — Gemini 1.5 Pro against an hour-long video's question set

*Created 2026-09-13 12:10.*
*Last revised 2026-09-13 13:02 — Revision 3, heading anchors (no numeric change).*

## Summary

Two rows, one per evaluation mode in HourVideo's Table 3, on the same work unit: **one video from the
25-video ablation set, mean 38.2 minutes, with all 22.8 of its five-way MCQs answered.** Compute
comes from the paper's own published token totals divided by 25 videos and multiplied by the dataset's
Gemini Pro coefficient, plus a visual-encoder term worth 7.2%: **1.042e18 FLOPs** under the
task-level protocol and **3.228e18** when each MCQ is evaluated on its own. Human time is the same on
both rows, **4,029 s (1.12 hours)**, transferred from the only measured human answering time in
long-video QA, DeepMind's 1h-walk VQA. That one sentence in the donor supports two transfers that
disagree by a factor of 8.4 — 11,653 s at 511.1 s per question, 1,393 s at 0.61 s per second of video
— so the central is their geometric mean, per `DECISIONS.md`'s rule for two defensible transfers
neither of which the evidence privileges. Gemini scored 38.9% and 36.8% against 85.0% for HourVideo's
three human experts and a 20% random floor, so both rows are `below`.

Two things dominate the uncertainty and both are stated in full below. The human transfer's spread
survives as the scenario band, 11,653 s to 1,393 s, and a further unpublished choice inside transfer
B — how the donor's 27-question batches were composed — is worth another 2.5× in the same direction,
one-sided. The omitted cached-context attention term is worth **2.9× to 6.5×** the recorded compute,
because every call is a prefill over roughly 590,000 positions; it is one-sided too.

No Gemini 3.7 Flash rows were built. The per-benchmark token table from Google's 1 September 2026
agentic-video launch does not appear on the launch post, the model card, or the API documentation, so
the brief's condition is not met. The disposition and the secondary figures are in
`agent-work/sources/hourvideo/gemini-3-7-flash-disposition.md`.

| | task-level | individual |
|---|---:|---:|
| Accuracy (%) | 38.9 | 36.8 |
| Published tokens, 25 videos | 120818343 | 374396885 |
| Published cost (USD) | 846 | 2621 |
| Billed input positions per video | 4832733.72 | 14975875.40 |
| CSV `tokens`, text only | 12291.89 | 23256 |
| Backbone FLOPs | 9.6705e17 | 2.9957e18 |
| Visual-encoder FLOPs | 7.5006e16 | 2.3258e17 |
| compute_flops | 1.0421e18 | 3.2283e18 |
| human_time (s) | 4029 | 4029 |
| FLOPs per human second | 2.59e14 | 8.01e14 |
| FLOPs per human second, 11653 s transfer | 8.94e13 | 2.77e14 |
| FLOPs per human second, 1393 s transfer | 7.48e14 | 2.32e15 |

Shared evidence is stated once in the sections below; the two `point_id` headings at the end carry
only what differs. All extracts are under `agent-work/sources/hourvideo/` with provenance in its `MANIFEST.md`.
The arithmetic is reproduced by `research/hourvideo/compute_hourvideo.py`, which reads
`agent-work/sources/hourvideo/hourvideo-reported-figures.json` and writes
`agent-work/derived/hourvideo/calculations.json`.

## What the source publishes

HourVideo (Chandrasegaran et al., NeurIPS 2024 Datasets and Benchmarks) is 500 egocentric Ego4D
videos, 20 to 120 minutes, mean 45.7 minutes, 381 hours in total, with 12,976 five-way MCQs across
summarization, perception, visual reasoning, and navigation tasks. Random guessing is 20%.

Table 3 is an ablation on **25 randomly selected videos, 15.9 hours of video, 570 MCQs**, run with
Gemini 1.5 Pro:

| Evaluation | Performance | Total Tokens | Evaluation Cost |
|---|---:|---:|---:|
| Task-level | 38.9% | 120,818,343 | $846 |
| Individual | 36.8% | 374,396,885 | $2621 |

That is the whole of the published compute evidence for this benchmark. The repository ships no
prediction files, no usage counters, and no per-video token data; its README's only compute statement
is a cost warning. Appendix E adds one further figure, "Gemini 1.5 Pro baseline experiments cost
approximately $105 per one-hour video across all tasks/sub-tasks", which is carried as an upper
scenario rather than used.

Derived from Table 3 alone: 15.9 h / 25 = **2,289.6 s (38.16 min) per video**, and 570 / 25 =
**22.8 MCQs per video**. Both divisions normalize a source-defined collection to one of its own
members, which is why the rows are `compute_statistic = mean` over `ai_attempts = 25` rather than a
transfer.

### The token column is a billed input count

$846 / 120,818,343 = $7.002 per million, and $2,621 / 374,396,885 = $7.001 per million. Going the
other way, 120,818,343 × $7.00/M = $845.73 and 374,396,885 × $7.00/M = $2,620.78, which round to the
published $846 and $2,621 exactly. $7.00 per million was Gemini 1.5 Pro's above-128K **input** rate
until the 1 October 2024 price cut to $2.50. So the column is the billed prompt-token total, priced
flat at the long-context input rate, and generated tokens are either absent from it or were charged
at the input rate rather than the $21.00 output rate. The rows treat it as input and add a separate
estimate for generation; that addition is 0.05% and 0.02% of the totals.

This also dates the runs. The price used places them before 1 October 2024, which matters for the
model record below.

## The evaluation protocol, and how many times the video is processed

The paper states the batching rule directly (Sec 3.1):

> Therefore, for our evaluation, we assess the questions in batches, with each batch containing all
> questions related to a specific task or sub-task. For predictive tasks (reasoning), we provide
> precise timestamps to trim the videos for targeted evaluation.

Each batch is one `generate_content` call carrying the whole video again. The File API upload
persists the file; it does not persist a prefill, and nothing in the code requests context caching.
So the video is re-processed once per call in both modes, and the difference between the two Table 3
rows is purely how many calls the protocol makes.

The released implementation (`agent-work/sources/hourvideo/hourvideo-repo-implementation.md`) adds a detail the
paper omits: four of the groups are not batched at all. `reasoning/predictive` gets one call per
question over a **trimmed** video, and `navigation/room_to_room_image`,
`navigation/object_retrieval_image`, and `reasoning/spatial/layout` each get one full-video call per
question plus five option images. On the demo notebook's worked one-hour video this comes to 21 calls
for 43 MCQs across 17 groups, about 2.0 MCQs per call, against the 3.1 MCQs per call that Table 3's
token ratio implies for the ablation set.

That gap closes, and closing it turns an anomaly into a check on the rows. Sec 3.1 says each batch
holds "all questions related to a specific task **or sub-task**", so the paper's own protocol permits
batching at the parent-task level; the released code, eight months later, groups at the sub-task
level instead. Take the demo video's structure and batch at the parent-task level — one call each for
summarization, perception, visual reasoning, and navigation — while keeping the four groups the code
handles per question: 4 + 8 = 12 calls for 43 MCQs. Scaling the per-question groups' 18.6% share of
MCQs to the ablation set's 22.8 questions per video gives 4 + 4.2 = **8.2 calls per video**, against
the **8.18 full-video-equivalent passes** Table 3's token total actually contains at the documented
tokenizer rate. The sub-task grouping the code now ships would give about 14, which the published
total rules out. So the paper's run batched at the parent-task level, and the 7-to-8 passes per video
the rows describe is what the published number independently says.

**The rows still use the published totals, not this reconstruction**, which is why the agreement is
worth having: the two were derived independently and they meet.

This settles the work unit. In individual mode the video is processed exactly once per question, so
one question is a coherent unit there. In task-level mode questions are answered in batches, so
per-question compute is only an average over the batch and the coherent unit is the video's whole
question set. Using the per-video question set for both rows keeps them comparable to each other —
they then differ only in protocol, which is exactly what Table 3 is about — and matches the unit the
human transfer is applied at. The per-question unit is carried as a scenario below, where it is exact
for the individual row.

## Tokenizer cross-check

Google publishes the rule: frames extracted at 1 FPS, 258 tokens per frame outside the Gemini 3
low-`media_resolution` branch, audio 32 tokens per second. The Gemini 1.5 report confirms the
per-frame figure for this era twice over, at 684k tokens for 2,674 frames (255.8 per frame) and 9.9M
for 37,994 frames (260.6 per frame).

Two implementation facts fix how the rule applies here. The uploaded MP4 is written by
`cv2.VideoWriter`, which carries no audio stream, so **the 32-tokens-per-second audio term does not
apply**; the file is silent. And the 0.5 fps downsample writes its frames back at a container rate of
0.5, preserving the original running time — confirmed on the demo video at 107,941 frames / 30 fps =
3,598 s in and 1,800 frames / 0.5 fps = 3,600 s out. Gemini then samples that timeline at its own
1 FPS, charging each distinct frame twice. The charge is therefore **258 tokens per second of video
duration per pass**, not per distinct frame.

Applying that to the individual row, where the call count is known exactly at one per MCQ:

- one full pass of the mean video = 258 × 2,289.6 = **590,717 positions**
- observed = 374,396,885 / (570 × 2,289.6) = **286.9 tokens per second of video per pass**, 11.2%
  above 258

**The residual 11% is not identified, and there is more than one candidate.** The rows do not depend
on resolving it, but the note should not present one explanation as the explanation.

- *Question-weighted duration.* Calls are weighted by questions per video, so the relevant duration
  is the question-weighted mean, not the plain mean. A question-weighted mean of 2,546 s reconciles
  the figure exactly, which needs only a positive correlation between a video's length and its
  question count in a set whose videos run 20 to 120 minutes. Not published, so not checkable.
- *A documented per-second overhead.* Google quotes "approximately 300 tokens per second of video at
  high media resolution" as a total and says "Timestamps are added every second", so a per-second
  charge above the bare frame cost is documented even for input with no audio. 258 + 32 = 290 sits
  1.1% above the billed 286.9, which fits better than the 258 figure does — though the audio term
  itself cannot apply, since the upload carries no audio stream.
- *Refusal retries.* Gemini 1.5 Pro refused 16.45% of MCQs benchmark-wide; retried calls would push
  the same way. Table 3 reports no refusal figure for the ablation.

The honest statement is that the billed rate sits between the bare frame charge and Google's own
per-second total, and that agreement to 11% between a provider tokenizer rule and a paper's billed
total is worth having on the record either way.

Expressed as full-video-equivalent passes per video at 258 tokens per second: **8.18 under the
task-level protocol and 25.35 under individual**. The ratio between the modes, 0.3227, is exact from
the published totals.

## Text tokens
The dataset's convention, set by `../AI Compute vs Human Time/dataset/research/imagenet.md`, keeps
visual positions out of the CSV `tokens` field and charges them inside `compute_flops` instead.
`tokens_accounting = decoder_processed` is the value whose definition matches: text-token positions
processed by the decoder, excluding non-text positions. The text side is small — 0.2% of the
task-level total and 0.15% of the individual total — so the estimate below does not move any row
materially, but it is the field's stated quantity and is derived rather than guessed.

Three components, at an assumed 4 characters per token:

- **Instruction prompt, 710 tokens per call.** `prompts/baseline_evaluations/gemini-1.5-pro/qa_eval.yaml`
  is 2,855 bytes by the HuggingFace repository's own file listing. The repository is gated, so the
  file itself was not read; 15 bytes are allowed for the YAML key and block marker, and the remainder
  is divided by 4.
- **MCQ text, 200 tokens per MCQ.** The code builds `f'Question: {question}\nAnswers:\n{mcq_test}'`,
  so each MCQ contributes its question plus five answer options once, in whichever call carries it.
  The paper prints a worked summarization MCQ whose question and five options run about 950
  characters; summarization options are the longest in the benchmark and the spatial, temporal, and
  navigation options are far shorter. The central is 800 characters, banded 600 to 1,200, which moves
  the CSV `tokens` field by −9% to +19% and `compute_flops` by less than 0.05%.
- **Output, 110 tokens per MCQ.** The model returns a JSON record per MCQ with `YOUR_ANSWER` (the
  option text, not a bare letter — the code calls `extract_first_letter` on it afterwards) and
  `JUSTIFICATION`, plus scaffolding. Banded 60 to 200.

Call counts per video are 22.8 for individual, one per MCQ, and 7.36 for task-level, taken from the
published token ratio. The parent-task reconciliation above gives 8.2 for the same protocol; using it
instead would raise the task-level `tokens` field by 5%, to 12,917, and `compute_flops` by 0.01%.

| | task-level | individual |
|---|---:|---:|
| Calls per video | 7.36 | 22.8 |
| Instruction tokens | 5223.9 | 16188 |
| MCQ text tokens | 4560 | 4560 |
| Output tokens | 2508 | 2508 |
| **CSV `tokens`** | **12291.89** | **23256** |
| Video positions (residual) | 4822949.8 | 14955127.4 |
| Video share of billed positions | 99.80% | 99.86% |

## Compute
`compute_flops` is the full processed-position count times the model's coefficient, plus a visual-
encoder term. Positions are the billed input total from Table 3 divided by 25, plus the estimated
generated tokens:

- task-level backbone: (4,832,733.72 + 2,508) × 2e11 = 9.6705e17 FLOPs
- individual backbone: (14,975,875.40 + 2,508) × 2e11 = 2.9957e18 FLOPs

The encoder term is described below; with it the row values are **1.0421e18** and **3.2283e18**.

`compute_method = operation_count` rather than `params_tokens`, following the ImageNet precedent:
the CSV `tokens` field holds only the text remainder, so the parameter multiplication in the note
covers positions the field does not carry. `compute_evidence = derived_assumed_inputs`, matching
every other Gemini row in the dataset, because the active parameter count is assumed.

One architectural assumption is load-bearing and is not hidden by the arithmetic: **a video position
is charged the same 2 × active-parameters as a text position.** Gemini is natively multimodal and the
258 tokens per frame are context positions, so the backbone term is right.

### The visual encoder
The upstream encoder that turns a frame into those 258 positions is undisclosed. The ImageNet row
this study follows for the `tokens` convention does not omit its encoder — it records
`Compute = 1.02 × [2 × 50e9 × 376 + 2 × 2e9 × 256]`, the encoder term inside the total — so this row
does the same rather than departing from the precedent it cites on the harder half.

Transferring that row's reference (a 2B-parameter OpenCLIP ViT-bigG/14 proxy at 14-pixel patches) to
the 512×384 frame actually uploaded gives 512 × 384 / 14² = **1,003 patches per frame** and
2 × 2e9 × 1,003 = 4.012e12 FLOPs per frame. Frame counts follow from the video positions at 258 per
frame: 18,694 frames per video at task level and 57,966 individually.

| | task-level | individual |
|---|---:|---:|
| Frames charged | 18693.6 | 57965.6 |
| Encoder FLOPs | 7.5006e16 | 2.3258e17 |
| Share of `compute_flops` | 7.20% | 7.20% |

Two scenarios bracket the patch count, and both lower it. If Gemini resizes each frame to the grid
its own 258-token charge implies (256 patches plus two specials, exactly the ImageNet case), the term
falls to 1.9% and `compute_flops` to 9.862e17 and 3.055e18. At 16-pixel patches over the same frame,
768 patches, it is 5.5%. The central takes the resolution actually uploaded, which is the larger
reading; nothing here moves a row by more than 6%.

### Cached-context attention
Per `DECISIONS.md`, every long-context run carries a quantified scenario for the term the 2 ×
active-parameters convention omits. This is the largest number in the note. Attention FLOPs over a
causal prefill of N positions are `4 · layers · d_model · N(N+1)/2`, the recipe
`../AI Compute vs Human Time/dataset/research/ruler/ruler.md` uses, which at fixed total positions is
linear in the per-call context. Here N is a full pass of the mean video, 590,717 positions, in both
modes, so the ratios are identical:

| Assumed shape | Attention, task-level | Attention, individual | Ratio to recorded |
|---|---:|---:|---:|
| L=64, d=8192 | 2.9935e18 | 9.2762e18 | 2.87 |
| L=80, d=10240 | 4.6773e18 | 1.4494e19 | 4.49 |
| L=96, d=12288 | 6.7353e18 | 2.0872e19 | 6.46 |

A full operation count would therefore land at **4.04e18 to 7.78e18** for the task-level row and
**1.25e19 to 2.41e19** for the individual row, 3.9× to 7.5× the recorded values. The layer counts and
widths are assumptions bracketing a frontier decoder of roughly 100B active parameters; Gemini's
architecture is not disclosed. The figure is an upper bound in one further respect: Gemini 1.5's
long-context mechanism is undisclosed and a 2M-token context is unlikely to be served by dense
attention at full cost. It is still the right thing to record, because the convention's omission can
only understate, and at 590,000-position contexts it understates by more than the parameter prior
does in either direction.

### Scenarios

| Scenario | task-level | individual | Ratio |
|---|---:|---:|---:|
| Central | 1.0421e18 | 3.2283e18 | 1.00 |
| Backbone only, no encoder term | 9.6705e17 | 2.9957e18 | 0.93 |
| Encoder at the 258-token grid, 256 patches | 9.8619e17 | 3.0550e18 | 0.95 |
| 30B active parameters | 3.6512e17 | 1.1313e18 | 0.35 |
| 300B active parameters | 2.9762e18 | 9.2196e18 | 2.86 |
| Plus attention, L=64, d=8192 | 4.0355e18 | 1.2504e19 | 3.87 |
| Plus attention, L=96, d=12288 | 7.7773e18 | 2.4100e19 | 7.46 |
| Appendix E cost basis | 2.0564e18 | — | 1.97 |
| Per-MCQ work unit | 4.5704e16 | 1.4159e17 | 1/22.8 |

The Appendix E row is the paper's own alternative accounting. Table 3 implies $53.21 per hour of video
at task level; Appendix E says approximately $105 per one-hour video "across all tasks/sub-tasks",
1.97 times higher. The gap is unexplained by the paper. It plausibly absorbs refusal retries,
exploration, and prompt engineering, none of which belong in a per-video work unit, which is why
Table 3 is the central and this is the ceiling.

## Model record
The evaluation code requests `models/gemini-1.5-pro-latest`, an alias, in both the command-line
default and the demo notebook. The revision behind Table 3 is therefore not recorded anywhere. The
$7.00 per million implied by the cost column places the runs before the 1 October 2024 price cut,
when the alias resolved to `gemini-1.5-pro-001` (23 May 2024) or `gemini-1.5-pro-002` (24 September
2024). Both already exist in `../AI Compute vs Human Time/dataset/models.csv` and both carry the same
200,000,000,000 FLOPs per token from a 100B assumed active count, so the ambiguity is numerically
inert.

A new record `gemini-1.5-pro-hourvideo` is added to this folder's `models.csv` rather than picking
one of the two, following the `gemini-1.5-pro-naturalplan` precedent for an unresolved revision.
`model_release_date` is left blank rather than imputed, per COLUMNS. The shared numerical assumptions
are identical to the existing Gemini Pro records, so nothing in the reference dataset is affected.
100B active is the dataset's shared frontier prior, not a Google disclosure; 30–300B is the
sensitivity, and it is under review across both registries.

## Human time
There is no human answering time in HourVideo. The paper records the 85.0% and nothing about the
clock, nothing about whether the experts watched a video end to end, and no per-expert score. So the
duration is transferred, and the only donor available anywhere in long-video question answering is
DeepMind's 1h-walk VQA (Perception Test 2024, Sec 4.7):

> each question in the dataset was answered by 10 participants. Each participant received 27
> questions. The average time for completing the batch of 27 questions was 3h50m and the overall
> accuracy was 99.64%.

13,800 s / 27 = **511.1 s per question**, a mean over recorded batch timings. 70 questions answered
10 times each is **700 contributing question-answering attempts** over 25.9 participant batches, with
no successful-only filter, so `human_time_subset = all` and `human_attempts = 700`. The classification
is `transferred_timings` on the evidence and `estimated` on the method: this is a judgment-based
transfer between benchmarks and populations, not a unit conversion.

### One donor sentence, two transfers, a factor of 8.4 between them

That sentence supports two rates, and they do not agree on HourVideo.

**A rate per question.** 511.1 s × 22.8 MCQs = **11,653 s**, 5.09 times the video's running time.

**A rate per second of video.** This one turns on how long the donor's videos are, and the first
submission got it wrong. 1h-walk VQA is built on the Walking Tours corpus, which the donor paper
describes as "ten 1-hour (**or longer**) Youtube videos" and whose dataset card publishes the
durations: minimum 59 minutes, maximum 2 h 55 min, **average 1 h 38 min**. All ten carry benchmark
questions (Table 1: validation 3 videos / 11 questions, test 7 / 59), so the corpus is
10 × 5,880 = **58,800 s of video**, not the 36,000 s a nominal hour each would give. One full
coverage of the 70-question set costs (70 / 27) × 13,800 = 35,778 s, so the participants spent
**0.6085 s of active time per second of video**. Transferred to a 2,289.6 s HourVideo video that is
**1,393 s**.

Neither is privileged by the evidence. The per-question rate overcounts here, because HourVideo puts
22.8 questions on one video where the donor averaged 7, and a second question about a video you have
already scrubbed does not cost what the first did. The per-second-of-video rate undercounts for the
same reason from the other side: it treats the extra 15.8 questions as free, when more questions
plainly mean more scrubbing. So `DECISIONS.md`'s rule for two defensible transfers applies, as it
does on the Astra Factorio row — the central is their geometric mean, and the note states both.

**Central: √(11,653 × 1,393) = 4,029 s (1.12 hours) per video question set**, 1.76 times the video's
running time.

### Transfer B rests on an unpublished batch composition, worth a further 2.5×

"70 questions over 10 videos is 7 per video, so a 27-question batch spans 3.86 videos" is an
assumption, not arithmetic: it supposes each participant's 27 questions came as whole videos' worth.
Two things cut against it. The questions are not evenly spread — 11 over 3 validation videos is 3.7
each against 59 over 7 test videos at 8.4 each — so there is no uniform seven-question block to hand
out; and 27 is a multiple of no plausible block size, with 700 / 27 = 25.93 participants not an
integer either.

If the 27 were instead drawn at random from the 70, a batch touches
10 × (1 − C(63,27)/C(70,27)) = **9.73 of the ten videos** in expectation, essentially all of them.
The participant then covers 9.73 × 5,880 = 57,218 s of video in 13,800 s, a rate of **0.241 s per
second of video**, transfer B of **552 s**, and a central of **2,537 s**. Using the uneven split as
an integer vector instead of a uniform seven gives 9.42 videos and a slightly longer transfer B, so
the uniform figure is the shorter end of this reading.

The central stays at 4,029 s: the video-blocked reading is the one that treats the donor most
generously, and the evidence does not say which assignment was used. But both readings shorten
transfer B and neither lengthens it, so **the residual uncertainty on that leg is one-sided**, and
under the geometric-mean rule it is half the answer.

| Reading | Human time per video (s) | Multiple of the video's running time |
|---|---:|---:|
| **Central, geometric mean of the two transfers** | **4029** | **1.76** |
| Transfer A, 511.1 s per question × 22.8 questions | 11653 | 5.09 |
| Transfer B, video-blocked batches, 0.609 s per second of video | 1393 | 0.61 |
| Transfer B, randomly assigned batches, 0.241 s per second of video | 552 | 0.24 |
| Central if transfer B takes the random reading | 2537 | 1.11 |
| Watch-once floor, the video's running time itself | 2290 | 1.00 |

The watch-once floor is now a live bound rather than a corroboration. Revision 1 offered the
coincidence that transfer B landed within 1% of it as a check on the donor; corrected, transfer B
sits 39% *below* it, so the donor's participants were not spending one viewing per video — they were
scrubbing at 0.61 of real time, or 0.24 under the random reading. The floor is the quantity a reader
should compare the central against, not a second measurement.

Because the central is a construction over two transfers rather than a retained sample statistic,
`human_time_statistic` is `point_estimate`, which is what 80 of the 95 `transferred_timings` rows
across both registries already use. It was `mean` in the first submission, when the value was the
donor's own mean scaled by a question count. `human_attempts` stays 700: both transfers draw on the
same 700 donor question-answers, and COLUMNS is explicit that this count is not an effective sample
size for the target estimate. The review argued for 26 instead, on the grounds that the timed records
are the participant batches and the 700 is the accuracy sample behind the 99.64%; the precedents
split, it is a specification question rather than an arithmetic one, and it is flagged in
`candidates/hourvideo/REVISION.md` for the coordinator rather than changed unilaterally.

Two further points on the donor, both of which cut toward the shorter transfer, and both of which
get stronger under the correction rather than weaker. The participants scrubbed: at 0.61 s of active
time per second of video they were covering the corpus well under real time, so they were not
watching end to end even at 511 s per question. And 1h-walk VQA's
questions were filtered to remove anything answerable from a single frame or short clip, which is the
harder end; HourVideo's mix includes summarization and navigation questions that reward one careful
pass more than repeated search.

Nothing on the performance side moves with this. `performance_evidence` carries accuracies only and
is unchanged, and all four `comparison_issues` values still hold for the same reasons: the timing
still comes from a different benchmark and a different group from the 85.0%.

### Population

`human_skill = expert`. The performance baseline on this row is HourVideo's three human experts, and
`human_time` is what that population is estimated to need. The timing donor is a different group —
DeepMind's zero-shot participants, who scored 99.64% on their own set — which is precisely what
`different_human_baseline` flags. The donor is not a naive crowd: they came from the Perception Test
rater pool and authored the questions in a separate pass.

## Task category

`perception`, chosen over `memory_recall`. The input is raw sensory video and the whole difficulty is
getting information out of it, which is the `perception` definition; HourVideo's own taxonomy also
names perception as one of its four parent tasks. The competing value covers "retaining and recalling
previously encountered information, including supplied material", which fits the factual-recall and
tracking sub-tasks and is the value the dataset's RULER long-context retrieval rows use. The choice
is recorded rather than asserted: a reviewer who reads the benchmark as long-context retrieval over
supplied material rather than as perception has a case.

## Performance

Gemini 1.5 Pro answered 38.9% of the 570 ablation MCQs correctly under the task-level protocol and
36.8% under individual evaluation. HourVideo's three human experts scored **85.0%** on a separate
sample of 213 MCQs over 14 videos and 11.2 hours. Random guessing is 20%. Both rows are `below`: the
gap is 46 points, and the model clears the random floor by less than half the distance to the humans.
The benchmark-wide Gemini 1.5 Pro figure is 37.3%, on the 445 videos and 10,842 MCQs it did not
refuse.

Three qualifications, all flagged:

- **The human score and the model score are on different sets.** 213 MCQs over 14 videos against 570
  over 25. Neither sample's composition is published in enough detail to check that the task mix
  matches. `different_assessment`.
- **The evaluators came from the authors' own annotator pool.** The contamination control is at the
  level of videos, not people: experts were excluded from videos they had annotated, not from the
  benchmark's construction. Seven trained annotators contributed over 400 hours in Stage 3 and four
  experts over 250 hours in Stage 5; the three evaluators are drawn from that population and know the
  question prototypes, the answer-construction conventions, and the distractor style. This is a
  reason the 85.0% may be optimistic as a general human baseline, and it is not something a
  `comparison_issues` value names, so it is stated in `notes`.
- **The model saw less than a human would.** A 512×384, 0.5 fps, silent re-encode against whatever the
  experts were shown. Gemini's own 1 FPS resampling recovers the timeline but not the discarded
  frames, and the audio is gone entirely — on egocentric cooking and construction footage that is not
  a trivial loss. `different_inputs_or_tools`.

Refusals are the one gap in the performance evidence. Gemini 1.5 Pro refused 16.45% of MCQs
benchmark-wide, and Table 3 reports no refusal figure for the 25-video ablation. If refusals were
scored as wrong in Table 3 the accuracies understate the model on answered questions; if they were
dropped, the 570 denominator is nominal. The paper does not say, and there is no artifact that would
settle it.

## Mechanical checks

- Headers match the root `points.csv` and `models.csv` byte for byte.
- Every enum value is drawn from `COLUMNS.md`.
- `point_id`s checked against every existing ID across both registries at the time of writing;
  the count moves as this batch grows, so the check is re-run rather than quoted.
- CSV text fields are within the `DECISIONS.md` norms: `notes` ≤ 586, `task_description` ≤ 560,
  `performance_evidence` ≤ 337, `source_record` ≤ 455, `compute_source` ≤ 220, `human_time_source`
  ≤ 205, models.csv `notes` ≤ 365.
- No cited path ends in punctuation.
- Every `research/` and `agent-work/sources/` citation in both CSVs resolves, anchors included, under the
  validator's own rule: it slugifies heading *text*, so a Markdown `{#anchor}` attribute does not
  create that anchor. The headings this note is cited by are written plainly for that reason.
  `research/hourvideo/check_anchors.py` re-runs the test.
- `research/hourvideo/compute_hourvideo.py` reproduces every number in this note from
  `agent-work/sources/hourvideo/hourvideo-reported-figures.json` alone, writing a new
  `calculations.json` and modifying no retained evidence.

---

## perc-hourvideo-gemini15pro-tasklevel

Gemini 1.5 Pro answering one video's whole MCQ set under HourVideo's own task-level protocol, the
mode the benchmark asks submissions to use.

- `compute_flops` = 4,835,241.72 × 2e11 backbone + 18,694 frames × 4.012e12 encoder =
  **1.0420547132928709e+18**
- `tokens` = 7.36 × 710 + 22.8 × 200 + 22.8 × 110 = **12291.89**, text only; the 4,822,950 video
  positions per video are charged in `compute_flops` and are not in this field
- `human_time` = √(11,653 × 1,393) = **4029** s, the geometric mean of the two donor transfers
- `compute_statistic = mean`, `compute_subset = all`, `ai_attempts = 25` — the mean over the 25
  recorded video evaluations in the ablation
- Accuracy 38.9% against 85.0%; `performance_vs_human = below`
- Scenarios: attention +2.87× to +6.46×; parameters ×0.35 to ×2.86; encoder term out or at the
  258-token grid, ×0.93 or ×0.95; Appendix E cost basis ×1.97; human time 11,653 s or 1,393 s on the
  two transfers separately, moving FLOPs per human second from 2.59e14 to 8.94e13 or 7.48e14;
  per-MCQ unit 4.5704e16 FLOPs

## perc-hourvideo-gemini15pro-individual

The same work unit and the same human baseline, with each MCQ evaluated in its own call. The video is
processed 22.8 times instead of 7.4, which is the whole of the difference: the deliverable is
identical and the accuracy is 2.1 points lower.

- `compute_flops` = 14,978,383.40 × 2e11 backbone + 57,966 frames × 4.012e12 encoder =
  **3.2282583670636923e+18**
- `tokens` = 22.8 × 710 + 22.8 × 200 + 22.8 × 110 = **23256**, text only; 14,955,127 video positions
  per video are charged in `compute_flops`
- `human_time` = **4029** s, unchanged
- `compute_statistic = mean`, `compute_subset = all`, `ai_attempts = 25`
- Accuracy 36.8% against 85.0%; `performance_vs_human = below`
- Scenarios: as above in ratio; human time 11,653 s or 1,393 s on the two transfers separately,
  moving FLOPs per human second from 8.01e14 to 2.77e14 or 2.32e15
- The per-MCQ unit is exact for this row rather than an average: 656,946 positions and **1.4159e17
  FLOPs** per MCQ, against 511.1 s of measured donor time — the one place the per-question rate is
  used unmixed, because there the work unit matches the donor's. A reviewer who prefers the
  per-question unit should take this row's numbers and not the task-level row's

## Gemini 3.7 Flash — not built

The brief allowed rows for Gemini 3.7 Flash on LVBench and the related sets only if the per-benchmark
token counts could be read from a Google-owned page. They cannot. The launch post gives percentage
improvements and an unlabeled chart; the Gemini 3.7 Flash model card gives one video benchmark,
LVBench at 85.4%, with no token or cost itemization, and that 85.4% matches neither the 85.1% static
nor the 88.6% agentic figure in the circulating secondary table; the API documentation gives the
tokenizer rule and the agentic-mode description but no benchmark numbers. A site-restricted search
over `blog.google`, `developers.googleblog.com`, and `deepmind.google` turned up nothing further.
Full disposition, the secondary figures, and the three problems a later attempt would still face are
in `agent-work/sources/hourvideo/gemini-3-7-flash-disposition.md`.
