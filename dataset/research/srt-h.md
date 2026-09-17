# SRT-H autonomous cholecystectomy on ex vivo porcine gallbladders

*Created 2026-09-13 12:20.*
*Last revised 2026-09-13 12:50 (Revision 1, on the independent review).*

## Summary

Four candidate rows from [Kim et al. (2025)](https://www.science.org/doi/10.1126/scirobotics.adt5254), the SRT-H hierarchical surgical policy: one complete clipping-and-cutting phase of a cholecystectomy, and the three artery subtasks on which an expert surgeon repeated the robot's work on the same gallbladder through the same da Vinci Research Kit console.

| point_id | Work unit | AI seconds | Human seconds | compute_flops |
|---|---|---|---|---|
| `robo-cholecystectomy-srth` | Complete 17-task clipping-and-cutting phase | 317 | 222.56 | 1.79e13 |
| `robo-clip-artery-first-srth` | Apply the first clip to the cystic artery (deposit task 10) | 18.10 | 12.10 | 1.03e12 |
| `robo-clip-artery-third-srth` | Apply the third clip to the cystic artery (deposit task 14) | 25.00 | 18.50 | 1.43e12 |
| `robo-cut-artery-srth` | Go to the cutting position on the cystic artery (deposit task 16) | 19.00 | 13.00 | 1.09e12 |

Compute is an operation count over each unit's own recorded robot duration, from the published Swin-T and EfficientNet-B3 architectures at the published control rates. The human's time and the robot's time differ on every row and compute is charged over the robot's, which is the longer of the two here: the surgeon was faster on all three subtasks. Three rows carry a measured human duration; the procedure row transfers the surgeon-to-robot ratio from those three, which is why it is the weakest of the four.

All six subtask durations are derived from the authors' own kinematic records in the Zenodo deposit rather than read off Fig. 6C, and the script verifies each record against the trajectory length printed in the figure before it uses the duration.

The dominant assumption is the number of Swin-T forward passes in one high-level inference. The paper's preprocessing text implies ten (a global view and a fixed center crop for each of five frames); Fig. 2B's `History len = 4` label would imply fewer. Ten is central; five drops the procedure figure by 27%. The full scenario band on the procedure is 1.0e13 to 2.0e13.

## Source and what it measures

[arXiv:2505.10251v2](https://arxiv.org/abs/2505.10251) is the version used throughout; the published version is [Science Robotics 10.1126/scirobotics.adt5254](https://www.science.org/doi/10.1126/scirobotics.adt5254), volume 10, issue 104, article eadt5254, dated 2025-07-09 by [Crossref](https://api.crossref.org/works/10.1126/scirobotics.adt5254). Retained evidence and its provenance are in `agent-work/sources/srt-h/MANIFEST.md`; line numbers below refer to `agent-work/sources/srt-h/srt-h-2505.10251v2-text.txt`.

The task is the clipping-and-cutting phase of a cholecystectomy on ex vivo porcine gallbladder tissue, begun from the critical view of safety, which a demonstrator establishes by blunt dissection before the phase starts (lines 971–974). The phase is 17 tasks: grabbing the gallbladder (1), applying six clips (2 × 6 = 12) and cutting twice (2 × 2 = 4), where each clip and each cut counts as the motion plus a retraction (lines 987–990). Table 1 reports 100% success on all eight unseen gallbladders with no human intervention, durations of 290, 315, 304, 300, 396, 318, 274 and 337 s, mean 317 s, and a mean of six self-corrections per procedure. That duration "excludes the time of reloading the clips and making tool changes performed by the operator" (lines 284–286); a state machine subscribing to the high-level policy's task instructions pauses both policies during those transitions (lines 1232–1238). So the recorded 317 s is policy-active time, which is what the compute recipe charges.

Two items in the paper are not part of these runs and are excluded from compute. GPT-4o appears only as an alternative high-level planner explored in the Supplementary Methods and rejected (lines 1684–1700); it was given the first few frames of one sequence, not used in the eight procedures. The voice-override and drop-down intervention path exists (lines 1146–1149) but the eight runs were "fully autonomously without human intervention".

### Expert-surgeon comparison

Lines 785–795 describe it: "Given the same gallbladder, both performed several tasks including adding the first and third clip to the artery and cutting it. Each round, SRT-H was deployed first and the surgeon was asked to repeat the same task." The surgeon had experience with robotic and manual cholecystectomy, had no prior dVRK experience but "was given sufficient time to become familiar with using the system", and contributed no training data.

Figure 6C prints the comparison. Reading the three panels left to right, in the caption's order of first clip, third clip, cut:

| Subtask | SRT-H duration (s) | Surgeon duration (s) | SRT-H trajectory length (mm) | Surgeon trajectory length (mm) | SRT-H mean jerk | Surgeon mean jerk |
|---|---|---|---|---|---|---|
| First clip on the artery | 18 | 12 | 31.387 | 54.005 | 2.544 | 3.058 |
| Third clip on the artery | 25 | 19 | 43.450 | 63.072 | 2.675 | 3.050 |
| Cut the artery | 19 | 13 | 44.384 | 47.348 | 2.665 | 2.987 |

Mean jerk is in units of 10⁻² mm/s³. The values are legible as text in the PDF and were also read off the rendered figure, retained as `agent-work/sources/srt-h/srt-h-fig6c-durations.png`.

The paper's own reading: "the surgeon completes all tasks faster than SRT-H. However, we observed that SRT-H navigated with shorter trajectory length and less mean jerk compared to the surgeon" (lines 802–805), and in the introduction, "Compared to an expert surgeon, our framework shows comparable performance, although with longer execution time" (lines 151–152).

### The Zenodo deposit, and why the rows use it instead of the figure

The figure's durations are integers. The paper's own data deposit ([record 15637074](https://zenodo.org/records/15637074), CC-BY-4.0, issued 2025-06-11) holds the records behind them. Zenodo was unreachable when this note was first written — the record page, the API, the DOI redirect and the site root all returned HTTP 504 — and came back during the independent review; both attempts are in `agent-work/sources/srt-h/zenodo-15637074-retrieval-log.txt`. The archive, `science_robotics_figure_files.zip`, 802,142 bytes, SHA-256 `9570e9df75cc4d6b9ee2a6df4e00033e73ba39fc4a7bf71daf194beb9cf654ae`, is retained in `agent-work/sources/srt-h/`.

Under `fig6_trajectoryplots/script_and_data/` it holds six kinematics CSVs, one per party per subtask, each fourteen columns of PSM1 and PSM2 position and orientation with no time column, plus `plot_sr.py`, the script that renders Fig. 6A and 6B from exactly those six files and names them in the panel order first clip, third clip, cut.

**The records are the figure's own data, and that is checkable rather than asserted.** Summing the per-sample Euclidean path of both arms, in millimetres, gives 31.387, 54.005, 43.450, 63.072, 44.384 and 47.348 — the six published trajectory lengths, to all three decimals, in that panel order. `operations.py` recomputes this and exits if any record misses its published value by more than 0.001 mm, so no duration can be used from a record that is not tied to its panel.

Both streams are sampled at 30 FPS (line 969) and the records carry no time column, so elapsed time over *n* samples is (*n*−1)/30:

| Subtask | Deposit task index | SRT-H samples | SRT-H s | Surgeon samples | Surgeon s | Fig. 6C integers |
|---|---|---|---|---|---|---|
| Clipping first clip right tube | 10 | 544 | 18.10 | 364 | 12.10 | 18 / 12 |
| Clipping third clip right tube | 14 | 751 | 25.00 | 556 | 18.50 | 25 / 19 |
| Go to the cutting position right tube | 16 | 571 | 19.00 | 391 | 13.00 | 19 / 13 |

Four of the six land on exact tenths or halves, which is itself a check on the reading. Using *n*/30 instead adds 0.033 s everywhere and moves no row by more than 0.2%. The figure's integers are these values rounded, and the surgeon's third-clip time is 18.50 s, not 19.

Three further things the deposit settles.

- **One record per party per subtask.** `human_attempts = 1` is now an observation rather than an inference from the paper's wording.
- **The third subtask is the same unit for both parties.** Both files are named `..._16_go_to_the_cutting_position_right_tube_recovery-{SRT,Jeff}.csv`: the authors' own label, task 16, *go to the cutting position on the right tube*, one of the six task instructions quoted verbatim in the paper. The measured segment is the approach to the cutting position, ending at the same point for both, not a cut one party completed and the other did not. That closes the question of whether the halted gripper closure applied asymmetrically; it did not, because closure is outside the measured segment on both sides.
- **None of the three donors is a retraction.** Indices 10, 14 and 16 fall where the paper's arithmetic puts them under the ordering of one grasp followed, per tube, by three clip motions and a cut approach each trailed by a retraction. All three donors are motion tasks, which is the premise the procedure row's transfer rests on.

The surgeon's files are labelled `Jeff`, and the author list includes Jeffrey Jopling of the Johns Hopkins Department of Surgery. The paper describes the surgeon only by experience; the deposit identifies an attending co-author, which supports `human_skill = expert`.

## Compute recipe

Full arithmetic is in `agent-work/derived/srt-h/calculations.json`; inputs and assumption labels are in `research/srt-h/recipe.json`; the script is `research/srt-h/operations.py`. Two FLOPs per multiply-add, per the dataset convention. An elementwise allowance of three operations per produced activation element covers a normalization affine transform and a nonlinearity, with one operation per attention score for the softmax; per-channel rescaling in squeeze-and-excitation and in FiLM is charged as one multiply-add per element. Dropping the whole elementwise allowance moves the procedure figure by 0.6%, so nothing turns on it.

SRT-H is two policies running at different fixed rates, and the compute per second of robot operation is therefore constant. Each row is that rate times its own recorded duration.

### High-level policy, one inference every 3 s

The high-level policy "predicts a new task instruction every 3 s" along with a correction flag and a corrective instruction (line 1128). Its reported size is "approximately 45 million parameters, with 29 million allocated to the encoder and the remaining 16 million shared between the Transformer and MLP heads" (lines 1663–1664).

The encoder is Swin-Transformer tiny pretrained on ImageNet, chosen for "its ability to produce a compact output token size of 768" (lines 1086–1089). Counting its published configuration — patch 4, embedding width 96, depths 2/2/6/2, heads 3/6/12/24, window 7, MLP ratio 4 — at 224 × 224 gives **4,489,798,656 multiply-adds and 28,286,818 parameters**, against the 4.5 GFLOPs and 28M the Swin paper reports and the 29M the SRT-H supplement reports. That agreement is the check that the encoder term is right. One pass is 9.025e9 FLOPs once the elementwise allowance is added. The final stage emits 7 × 7 = 49 tokens of width 768, passed to the decoder "without pooling to preserve spatial information".

The number of passes is the recipe's weakest input. The paper says "Each image undergoes preprocessing... The image is resized to 224 × 224... Alongside this global view, a centered crop that captures the most task-critical region is extracted and resized to 224 × 224" (lines 1078–1083), and separately "we include a history of 𝑘 = 4 past image frames, each spaced 1 s apart, along with the current frame as input to the HL policy" (lines 1091–1093). Read together that is five frames, each in two views, so **ten encoder passes and 490 memory tokens** per inference. Against that, Fig. 2B labels the image stack `History len = 4` and draws four token groups, and the ablation table has a separate "No Center Crop" variant. The center crop is a fixed 432 × 480 region of the 960 × 540 endoscope image (lines 611–614) and goes through the same single encoder, which is consistent with the reported 29M: two encoders would be about 57M. Ten is central; five, six and eight are carried as scenarios.

The decoder is six layers, eight heads, with three learnable query embeddings for the three outputs. Its width is not published. Inverting the reported 16M pins it: a six-layer decoder costs 8d² + 2·d·ffn parameters per layer, which is 14.2M at d = 384 with ffn 1536 and 25.2M at d = 512 with ffn 2048, so d ≈ 384 under either feed-forward convention. Reconstructing the decoder at d = 384 with the input projection and the three heads gives 14.9M parameters, against the reported 16M, and **2.120e9 FLOPs** per inference — 2.3% of the call. Charging the full 16M against every one of the 493 positions instead, which assumes no architecture at all, gives 1.578e10 and raises the procedure total by 8%.

One high-level inference is **9.237e10 FLOPs**, and the policy runs at 1/3 Hz.

### Low-level policy, one inference every 20 or 30 action steps

The low-level policy takes the endoscope left image and both wrist images, encodes them with a FiLM-conditioned EfficientNet-B3 at 224 × 224, fuses a DistilBERT embedding of the current instruction, and emits a 60 × 20 action chunk covering a 2 s horizon at 30 Hz (lines 1172–1189, 1194–1195). It "contains approximately 72M parameters" (lines 1213–1214).

**The 30 Hz is the action rate, not the inference rate.** Only part of each chunk is executed before the policy runs again: "for the 'grabbing gallbladder' phase... Setting the horizon to 30 timesteps... In contrast, for the other phases, we set a shorter execution horizon of 20 timesteps" (lines 1220–1228). So the network is queried **1.5 times per second in the clipping and cutting phases and once per second while grasping**, not thirty times per second. Charging the chunk rate would overstate this policy's compute by a factor of twenty.

Counting EfficientNet-B3 from its published scaling rule — width 1.2, depth 1.4, divisor 8, squeeze ratio 0.25 — reproduces **1,834,593,536 multiply-adds and 12,233,232 parameters at the reference 300 × 300**, against the 1.8B and 12M the EfficientNet paper reports and an exact match to the reference implementation's parameter count. At 224 × 224 the same count gives 966,055,776 multiply-adds per image, 1.971e9 FLOPs with the elementwise allowance, and a 7 × 7 × 1536 feature map, so 49 tokens per camera and 147 in total.

The three widths the SRT-H paper does not publish — the action transformer's depth, width and feed-forward size — come from the same first author's dVRK predecessor, whose Table 3 gives 4 encoder layers, 7 decoder layers, feed-forward 3200, hidden 512 and 8 heads for ACT on this robot (`agent-work/sources/srt-h/srt-2407.12998v1-act-hyperparameters.txt`), and from Yell-At-Your-Robot, whose low-level policy is the identical construction of ACT plus an EfficientNet-B3 backbone plus RT-1-style FiLM plus DistilBERT (`agent-work/sources/srt-h/yay-2403.12910v1-policy-architecture.txt`). The reconstruction is then checked against the one number SRT-H does publish:

| Component | Parameters |
|---|---|
| EfficientNet-B3 feature extractor, shared across the three cameras | 10,696,232 |
| FiLM scale-and-shift generators from the 768-wide language embedding, one per MBConv block output | 5,549,104 |
| ACT transformer, 4 encoder and 7 decoder layers at width 512, feed-forward 3200, with the input projection, 60 query embeddings and the action head | 55,746,560 |
| **Total** | **71,991,896** |
| Reported | approximately 72,000,000 |

That is the strongest single piece of evidence for the low-level reconstruction, and it also settles a choice the paper leaves open: one EfficientNet-B3 shared across the three cameras rather than three separate backbones, which would add 21M and break the total. The frozen DistilBERT sits outside the 72M, consistent with the paper describing it as pretrained and frozen and with 66M not fitting inside 72M alongside anything else.

Instruction length is measured rather than assumed. `operations.py` runs a WordPiece tokenizer over the retained `distilbert-base-uncased` vocabulary against the instruction strings the paper quotes verbatim — six task instructions from the main text and Fig. 2B, and all eighteen corrective instructions from the Supplementary Methods. The six task instructions come to 4, 6, 8, 8, 10 and 11 positions including the two special tokens, **mean 7.833**, which is the central value. The longest published instruction, 11 positions, raises the procedure total by 0.7%. DistilBERT is charged on every low-level call; charging it once per high-level step instead, which is what caching the unchanged instruction would give, lowers the procedure total by 1.3%.

One low-level inference is **1.756e10 FLOPs**: 5.955e9 for the three FiLM-conditioned backbone passes, 6.675e8 for DistilBERT, and 1.094e10 for the action transformer over 149 encoder tokens and 60 decoder queries.

### Rate and totals

Both reported inference latencies are consistent with the counts on the stated hardware — 9.237e10 FLOPs in about 25 ms and 1.756e10 in about 20 ms on a single RTX 4090 imply roughly 4 and 1 TFLOP/s, a few percent of the card, which is what unbatched small-model inference in Python looks like. The latencies are not used as evidence of FLOPs; they just fail to contradict the count.

Per second of policy-active operation, in the clipping and cutting phases: 9.237e10 / 3 + 1.5 × 1.756e10 = **5.71e10 FLOPs per second**. In the grasping phase the low-level term drops to one call per second, giving 4.83e10.

### Scenarios

All on `robo-cholecystectomy-srth`, whose central value is 1.795e13.

| Scenario | Procedure FLOPs | Change |
|---|---|---|
| Central | 1.795e13 | — |
| 5 high-level encoder passes (global view only, or four frames in two views less the crop) | 1.307e13 | −27% |
| 6 high-level encoder passes (center crop on the current frame only) | 1.405e13 | −22% |
| 8 high-level encoder passes (four frames in two views) | 1.600e13 | −11% |
| High-level frame cache: six encoder passes, full 490-token memory | 1.413e13 | −21% |
| High-level decoder charged as 2 × 16M × positions | 1.939e13 | +8% |
| Action transformer at width 384, the low end of the 72M budget | 1.514e13 | −16% |
| Grasping phase given no share of the duration | 1.811e13 | +0.9% |
| Grasping phase given 2/17 of the duration | 1.778e13 | −0.9% |
| Instruction encoded once per high-level step | 1.771e13 | −1.3% |
| Longest published instruction on every call | 1.807e13 | +0.7% |
| Matrix operations only, no elementwise allowance | 1.783e13 | −0.6% |
| Every lever low at once | 1.004e13 | −44% |
| Every lever high at once | 1.968e13 | +10% |

The frame-cache line is a different mechanism from the pass-count lines above it. Those vary how many views the model looks at; this one varies how often it re-encodes the same view. Consecutive high-level calls are 3 s apart over frames spaced 1 s apart, so two of the five are shared with the previous call, and an implementation that keeps their embeddings re-encodes six views while the decoder still attends to all 490 memory tokens. It is one-sided downward and sits inside the band, so the central does not move.

The band is **1.0e13 to 2.0e13**, and the encoder-pass count is most of it. The three subtask rows are the same per-second rate times a shorter duration, so every percentage above carries over to them except the two grasping-phase lines, which are zero for a clip or a cut.

## Human time

Three rows take the surgeon's duration from his own kinematic record in the deposit: **12.10, 18.50 and 13.00 s**, each a sample count divided by the paper's stated 30 FPS. That is a recorded timing for the stated task and population changed only in units, so `human_time_evidence = task_timings` with `human_time_method = unit_conversion` — not `reported`, because the seconds are not printed anywhere as seconds, and not `estimated`, because nothing is transferred or judged. The deposit holds exactly one record per party per subtask, so `human_attempts = 1` is observed, and the statistic is a `point_estimate` rather than a mean.

### The procedure row's transfer

No surgeon performed the whole 17-task phase. The procedure row transfers the ratio measured on the three subtasks: the surgeon took 43.60 s where SRT-H took 62.10 s, a ratio of **0.70209**, applied to the 317 s robot mean to give **222.56 s**. The three per-subtask ratios are 0.6685, 0.7400 and 0.6842, which bracket the transferred value at 211.9 to 234.6 s.

Two things about that transfer belong in a reviewer's hands. It is a short-range transfer — same surgeon, same gallbladder, same console, same instruments, three of the seventeen tasks — which is about as favorable as this kind of transfer gets. But it is one-sided in a knowable direction, and the deposit now demonstrates the premise rather than leaving it as an inference from the paper's task list: indices 10, 14 and 16 are all motion tasks, none of them a retraction, while the fourteen tasks outside the donor set are dominated by retractions and transitions, which is where a surgeon's speed advantage over a policy that replans every 0.67 s is likely to be largest. 222.56 s is therefore more likely to be an overestimate of the surgeon's whole-phase time than an underestimate. The row is `transferred_timings` with `human_time_method = estimated` and `different_task` in `comparison_issues`, and it is the one of the four I would drop first if a reviewer objects.

A second transfer is available and is deliberately not averaged in. The three donors are 3 of 17 tasks, so a per-task rate gives 43.60 / 3 × 17 = **247.07 s**, and the geometric mean with the ratio transfer would be 234.50 s. DECISIONS' rule that two defensible transfers be centred on their geometric mean does not bind here, because these two are not equally defensible: the robot spent 62.10 s of 317 s, 19.6% of the phase, on 17.6% of the tasks, so the ratio transfer already carries the task-length information that a per-task rate throws away. Both transfers are biased the same way as well, so averaging them cancels nothing. 247.07 s is recorded in `calculations.json` as a named scenario.

**Range: 211.92 to 247.07 s**, added 2026-09-17. The high is that second transfer, the per-task rate. The low is the spread of the transfer ratio itself across the three donor records, which is measured: the surgeon-to-robot ratios are 12.10/18.10 = 0.66851, 18.50/25.00 = 0.74000 and 13.00/19.00 = 0.68421, against the pooled 43.60/62.10 = 0.70209 the central uses. The lowest of the three over the 317 s phase gives 0.66851 x 317 = **211.92 s**; the highest gives 234.58 s, which sits between the central and the per-task-rate transfer and so needs no bound of its own. This is the dispersion of the evidence the transfer rests on, not a factor on the central.

There is no external anchor worth using. Published operative times for laparoscopic or robotic cholecystectomy are whole-operation, in vivo, human-anatomy figures on different instruments, and substituting one for a dVRK phase on ex vivo porcine tissue would be a worse transfer than the within-experiment one.

## Performance and comparison flags

`performance_vs_human = match` on all four rows. Both parties completed the same subtasks on the same tissue; SRT-H was slower on all three and better on both published motion-quality measures on all three; and the paper states the comparison itself as "comparable performance, although with longer execution time". The procedure row transfers that same judgment, since the surgeon has no whole-phase record, and adds the eight-for-eight autonomous completion on unseen gallbladders. Speed is not double-counted into the performance label: it is the row's y-value.

`different_inputs_or_tools` on all four. The console, the instruments, the tissue and the port geometry are shared, which is the strongest tool symmetry available anywhere in this category, but the supplied information is not identical. SRT-H reads the endoscope's left image plus two wrist cameras mounted near the instrument tips; the surgeon works from the console's stereo endoscope view and has no wrist-camera feed. The flag records that concrete difference, not the embodiment.

`different_task` additionally on the procedure row, because the human duration covers three subtasks and the AI's covers seventeen.

Two further differences are recorded here rather than flagged, because each is a limitation of the evidence rather than a difference in what was compared. The surgeon is n = 1 on one gallbladder, which the paper itself calls a preliminary comparison. And SRT-H was deployed first and the surgeon then repeated the task, so the surgeon had just watched the same motion performed, which if anything favors the human side of the timing.

The clips used by both parties had their latching mechanism disabled, so the clip subtasks are the clipping motion rather than a clip that locks. That applies symmetrically and is stated in each row's task description. The third subtask is no longer a worry at all: the deposit's shared task label shows both parties were recorded over *go to the cutting position on the right tube*, so the halted gripper closure falls outside the measured segment on both sides.

## Point entries

### robo-cholecystectomy-srth

Compute **1.794807e13 FLOPs**, human time **222.56 s**, transferred as set out under [Human time](#human-time) from three donor surgeon records, `human_attempts = 3`. 105.667 high-level inferences and 466.176 low-level inferences over 317 s, with 1/17 of the duration at the grasping phase's slower low-level rate. That 1/17 is an equal-share allocation across the 17 tasks; the paper does not publish the grasping phase's duration, and the two alternatives in the scenario table move the total by under 1% either way.

`compute_statistic = mean` with `ai_attempts = 8`: compute is exactly linear in duration at fixed rates, so the rate times the mean of the eight recorded durations is the mean compute over the eight runs. The one approximation is treating the grasping share as identical across runs.

`tokens = 3651.72` text positions, the 466.176 low-level calls at 7.833 DistilBERT positions each, with `tokens_accounting = encoder_processed`. Image patches and the 60 action positions stay in the calculation file rather than being added to the text count, per the column definition.

### robo-clip-artery-first-srth

Compute **1.034146e12 FLOPs** over the robot's 18.10 s; human time **12.10 s**, from the surgeon's 364-sample record of deposit task 10 at 30 FPS, `human_time_evidence = task_timings`, `human_time_method = unit_conversion`, `human_attempts = 1`. 6.033 high-level and 27.15 low-level inferences. `tokens = 212.675`.

### robo-clip-artery-third-srth

Compute **1.428378e12 FLOPs** over the robot's 25.00 s; human time **18.50 s**, from the surgeon's 556-sample record of deposit task 14 at 30 FPS, on the same evidence terms as the row above. This is the row the deposit changed most: Fig. 6C rounds 18.50 to 19, a 2.6% move. 8.333 high-level and 37.5 low-level inferences. `tokens = 293.75`. The fractional call counts are what a fixed rate over a 25 s window gives; they are not rounded up, because rounding would imply a phase boundary the source does not record.

### robo-cut-artery-srth

Compute **1.085567e12 FLOPs** over the robot's 19.00 s; human time **13.00 s**, from the surgeon's 391-sample record of deposit task 16 at 30 FPS, on the same evidence terms as the two rows above. 6.333 high-level and 28.5 low-level inferences. `tokens = 223.25`.

The unit is the authors' own task 16, *go to the cutting position on the right tube*, so the row's `task` and `task_description` name the approach rather than a completed cut. The paper's halted gripper closure sits outside the measured segment, for both parties. The point ID keeps the word cut because it was assigned before the deposit was in hand and is now cited in the review record.

## Considered and not drafted

- **The second clip on the artery, and every duct subtask.** Fig. 6C covers three subtasks only. There is no surgeon duration for the other fourteen tasks, so there is no human side.
- **A row on the n = 3 ablation set (Fig. 4).** The variant comparison uses three different gallbladders, a 90 s per-task cap, and no surgeon. It is a model-versus-model result, and the stacked bar segments in Fig. 4C do not resolve unambiguously in the text layer.
- **A training row.** The training workload is partly published — 16,000 trajectories over about 17 hours of data from 34 gallbladders, the high-level policy 500 epochs at 4,000 iterations in about 20 hours on one RTX 4090, the low-level policy 1,500 epochs in about 100 h on the same card — but the DAgger correction dataset's size is not given, the base-versus-fine-tune split is not separable, and the natural human side would be the surgical training that produces a cholecystectomy-capable surgeon, which is a different and much larger research question than this note. Worth a separate look; not drafted here.
- **A GPT-4o high-level-planner row.** The supplement gives no token counts, no run length and no success criterion beyond "would not be able to guide the LL policy through a full cholecystectomy". There is nothing to count.

## Open questions for the reviewer

1. **~~The Zenodo deposit~~ — answered.** Retrieved during the independent review and retained. The Fig. 6C durations are rounded; the finer values are in the table above, and the surgeon's third-clip time is 18.50 s rather than 19. There is exactly one record per party per subtask, so `human_attempts = 1` stands as an observation.
2. **Ten Swin-T passes or fewer.** Still open, and still the single largest lever in the compute estimate. The reviewer reads Fig. 2B's `History len = 4` as the paper's own variable for the history, k = 4 past frames, rather than as a count of total inputs, which makes ten the reading of the text and leaves the five- and six-pass lines as alternatives about the crop. No code release settles it.
3. **The procedure row's human time.** A ratio transferred from three of seventeen tasks, one-sided upward, and now collinear with the three subtask rows by construction: its human time is 0.70209 times its own robot duration and its compute is the same per-second rate times that duration, so it extends the scale by 17× rather than adding an independent human observation. Reasonable people could want this row dropped or its flag strengthened.
4. **~~Whether the halted cut applies to both parties~~ — answered in the rows' favor.** The deposit's two task-16 files carry the same authors' label for both parties, so the measured segment is the approach to the cutting position on both sides and the gripper closure is outside it.
5. **Nesting is undeclared.** The three subtask rows are tasks 10, 14 and 16 of the procedure row's 17, and their compute and duration sit inside its totals. DECISIONS' finer-grain convention was written for rows refining an existing Codex row, so this is a specification gap to raise at merge rather than a violation.

## Reproduction

`operations.py` needs Python 3.9 or later and the standard library only. It reads two source files — the DistilBERT vocabulary and the Zenodo figure archive — checks both SHA-256 values against the recipe, verifies each kinematic record against its published trajectory length before using its duration, and refuses to overwrite an existing output or to write inside the sources directory. No model weights, robot code, GPU or network access are involved.

```sh
python3 -B research/srt-h/operations.py \
    --sources agent-work/sources/srt-h \
    --recipe research/srt-h/recipe.json \
    --output /tmp/srt-h-recomputed.json
```

The retained `calculations.json` was produced by that command with `--output agent-work/derived/srt-h/calculations.json`, and records the SHA-256 of the recipe and of every retained source file alongside the component totals, the parameter reconciliations, the per-unit results, the human-time transfer and every scenario in the table above.
