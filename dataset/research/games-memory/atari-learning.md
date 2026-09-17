# Atari learning

## Sources and human transition

Original sources: [Tsividis et al. 2017](https://gershmanlab.com/pubs/Tsividis17.pdf), retained at `agent-work/sources/games-memory/tsividis2017.pdf`; [Mnih et al. 2015](https://www.nature.com/articles/nature14236), author-paper [mirror](https://web.stanford.edu/class/psych209/Readings/MnihEtAlHassibis15NatureControlDeepRL.pdf), retained at `agent-work/sources/games-memory/mnih2015.pdf`; [EfficientZero paper v2](https://arxiv.org/html/2111.00210), Table 1 and Appendix A; [original implementation](https://github.com/YeWR/EfficientZero), retained main-branch archive under `agent-work/sources/games-memory/EfficientZero-main/` on 2026-09-12. The code snapshot, not a claim about an exact historical training trace, establishes the operation recipe.

Tsividis Figure 1 (PDF page 2, visually inspected) plots each participant's highest score so far against cumulative gameplay. The Frostbite group has 71 game-naive participants. Its central curve passes a few hundred points within the first few minutes; Part II reports first-episode mean 356 (interval 167–545). Ordinary adults already bring vision, motor control and world knowledge. AI starts with random network weights and learns visual representations too. This is a comparison of game-specific learning, not lifetime acquisition of all prerequisite skills.

**Judgment:** use 120 seconds of active, unaided exploration for estimated early-play performance around 300 Frostbite points, anchored primarily by the normal-condition first-episode mean of 356. The best-so-far curve supplies only a rough time scale, not an estimate of a future-episode mean. A reasonable reading/transfer range is 60–180 seconds. This is not a recovered mean hitting time. The CSV counts the 71 contributing learning sessions as timing donors, not as 71 measured times to the target score. All sessions contribute; each within-session best-so-far point is not a new attempt. Initial play is itself learning; no separately timed subsequent test is added. The target requires discovering elementary jumping/ice-floe controls, not reliably completing the igloo or attaining professional-tester skill. The first-episode result makes a multi-hour estimate for this target implausible. The central curve supports minutes rather than a subsecond guess.

The human endpoint is anchored to the normal-condition first-episode mean, while the best-so-far curve is used only to estimate the time scale. The comparison therefore flags different_assessment for human early learning play versus evaluation of a frozen AI policy. It does not flag different_attempt_selection: the human point is an analytic estimate, not a selected best-episode timing statistic. The approximate match is a broad estimated early-play endpoint comparison, not an assertion of equal mean future performance. Neither row uses the much higher original professional-tester benchmark (4335 Frostbite points). Mnih's own evaluation procedure caps AI episodes at five minutes; the Tsividis footnote describing the earlier human tester's episodes as lasting over five minutes should not override the original procedure.

## game-atari-dqn

One configured full DQN training run on Frostbite, starting randomly and producing the Table 2 policy: mean score 328.3, SD 250.5, across 30 evaluation episodes; random score 65.2. The learning work unit ends at that policy rather than adding a separate minute of gameplay.

### DQN compute

Methods and Extended Data Table 1 specify 84×84×4 input; convolutions 32×8×8 stride 4, 64×4×4 stride 2, 64×3×3 stride 1; 512-unit dense hidden layer. Use 18 output actions; changing to any smaller Atari action set has under 0.1% effect. Each multiply plus add counts as two FLOPs. Forward costs are 6,553,600 + 5,308,416 + 3,612,672 + 3,211,264 + 18,432 = **18,704,384**.

The paper's 50 million training “frames” and approximately 38 days refer to action observations with four-frame repeat: 200 million emulator frames / 60 Hz = 38.6 days. The later EfficientZero paper independently describes DQN's budget as 200 million frames. Batch 32, update every four decisions and replay warmup 50,000 give (50,000,000−50,000)/4 = 12,487,500 updates, or 399,600,000 replay samples. Per sample count online forward/backward as 3 forward costs and target-network next-state forward as one. This conventional backprop approximation slightly overcounts gradients into the first-layer input and includes terminal next-state forwards conservatively.

Add 50 million actor forwards (counting epsilon-random actions conservatively); 27 million validation forwards, obtained by transferring the paper's ablation schedule of every 250,000 training observations for 135,000 validation observations to this full run; and up to 135,000 final-evaluation forwards (30×300 seconds×15 decisions/s). The validation schedule is an allowance, not a documented trace of the main experiment. The base is 31,339,850,045,440,000 FLOPs. Multiply by 1.03 for optimizer, normalization/activation and small bookkeeping arithmetic: **3.22800455468032e16 FLOPs**. Validation contributes about 1.6%; the main uncertainty is conventional backward accounting, not simulated experience. Exclude hyperparameter-development experiments and other games because the work unit is one run with the published algorithm settings.

## game-atari-train-efficientzero

One configured full Frostbite run under the published Atari-100k recipe, random initialization to the policy represented by the reported 296.3 mean score. The study aggregates three seeds and 32 evaluation episodes per seed. The compute recipe describes one run, not all seeds used to estimate performance. The same modest human endpoint and 120-second transfer apply; similar final scores justify the same estimate despite very different training procedures.

### EfficientZero compute

Paper settings and retained code: 100,000 collected decisions; 120,000 learner updates including 20,000 final updates; batch 256; unroll five plus initial state; 50 MCTS simulations. Reanalyse policy fraction 0.99 and value fraction 1.0. Use MCTS root-value targets, corresponding to the full paper algorithm (`--use_root_value`), not the cheaper default command without this option. Code's `int(256*.99)` selects 253 policy trajectories. `core/reanalyze_worker.py` builds separate value and policy searches for six states each; it still evaluates padded observations before masking. Hence **120,000×6×(256+253) = 366,480,000 roots**, each with one initial inference and 50 recurrent expansions: **18,324,000,000 expansions**. Search trees cache latent states; do not multiply inference by the whole traversal depth.

Architecture comes from `config/atari/model.py`, `config/atari/__init__.py`, `core/model.py`. Four RGB observations give 12×96×96 input, 64 latent channels at 6×6. Representation: 32-channel stride-two stem, one 32-channel residual block; stride-two 32→64 residual block and its 3×3 skip; 64-channel residual blocks at 24×24, 12×12 and 6×6. Dynamics: action-concatenated 65→64 convolution and one residual block. Reward: 64→16 pointwise convolution, LSTM input 576/hidden 512, dense 512→32→601. Prediction: one 64-channel residual block; separate 16-channel value/policy heads, dense 576→32→601 or 18. Unused declared modules are excluded. Projection is 2304→1024→1024→1024, predictor 1024→512→1024; this uses current original-code dimensions where the paper prose differs.

All formulas and components are in `research/calculations.py`, with output in `research/calculations.json`. Two operations per multiply-add. Representation H=297,271,296; prediction P=5,569,216; dynamics+reward+prediction I=18,174,720; initial H+P=302,840,512. One root search costs H+P+50I=1,211,576,512 FLOPs.

Learner sample: 3×[initial + 5×(I+projection+predictor)] + 5×(initial+projection) = 2,905,060,096 FLOPs. The last term is the stop-gradient observation branch; `core/train.py` calls full initial inference even though its prediction output is discarded. No backward is charged through this detached branch. This is conventional forward/backward accounting, not a hardware measurement.

| Component | FLOPs |
|---|---:|
| Separate value and policy reanalysis | 444,018,560,117,760,000 |
| Learner, including consistency target forwards | 89,243,446,149,120,000 |
| Collection searches | 121,157,651,200,000 |
| Evaluation allowance | 2,558,849,593,344,000 |

Evaluation allows 13×32 episodes at 3,000 decisions plus final 32×27,000 decisions, each with search. These are conservative episode limits, not observed Frostbite durations; they contribute under 0.5%. Add 3% for non-MAC network operations, optimizer, tree arithmetic and small asynchronous queue excess. Total **5.520202739167667e17 FLOPs**. Integer emulator execution is not reinterpreted as FLOPs. The reported four GPUs for seven hours is a reasonableness lead, not the estimator: GPU type/utilization is not supplied. Two hours of environment exposure excludes replay/search and is not human training time.

## game-atari-train-muzero

**Human interval and endpoint:** Mnih Methods (retained `agent-work/sources/games-memory/mnih2015-layout.txt`, human-evaluation paragraph) directly reports approximately two hours of practice per game by its professional tester. Subsequent assessment averaged around 20 episodes capped at five minutes. Use 7200 seconds of game-specific practice, starting with professional general game-playing experience and ending at the reported Frostbite score about 4335. This is one tester's practice interval, not the duration of the later evaluation episodes or an estimate that ordinary people require two hours.

[MuZero v2](https://arxiv.org/html/1911.08265), Table S1, reports Frostbite 631378.53 versus human 4334.67. The original standard agent uses 20 billion environment frames, one million learner updates of batch 1024, five hypothetical unroll steps and 50 simulations per action. Appendix I describes 1000-episode assessments capped at 30 minutes, with no-op and human starts. Human and AI assessment caps differ materially; nevertheless the very large score gap supports above as a broad best estimate, not equal-capacity learning or a parity-compute observation. Human prior general skills and AI random initialization also differ. The source human learning interval is retained even though MuZero's endpoint is much stronger.

### MuZero compute

One full standard run; not the separately named Reanalyze variant. The published architecture (Appendices E–G) establishes the convolution recipe in `calculations-tranche-2.py`. Initial 128-plane 96×96 history is downsampled through 128-channel 48×48 and 256-channel 24×24/12×12 stages; use the specified 16 residual blocks at 6×6 after downsampling. Dynamics concatenates 18 action planes to 256 latent planes, followed by the stem and 16 residual blocks. This interpretation of the downsampling prefix is explicit; there is no additional full-resolution residual tower.

Two operations per multiply-add give representation trunk H=10192158720 and recurrent dynamics trunk G=1404407808. For each, allocate 2% for the small value/reward/policy heads, normalization, activation, pooling and tree scalar arithmetic. This is proportionate to heads which reduce channels before predicting 601 value/reward categories or 18 actions. It is an explicit approximation rather than a claim to know every head width. Initial I=10396001894.4, recurrent R=1432495964.16; one root search I+50R=82020800102.4 FLOPs. Latent states are cached, so charge a single dynamics/prediction call per expansion, not its whole traversal path.

Actor: (20 billion raw frames / four-frame repeat) × search = 4.10104000512e20 FLOPs. Learner: 1 million ×1024×3×(I+5R) = 5.39396558290944e19. The three-forward multiplier approximates forward/backward updates. Standard MuZero reuses the actor's stored search values/policies; it does not add the later Reanalyze algorithm's fresh searches. Prioritized replay changes sampling, not the total prescribed learner updates.

**Evaluation judgment:** a training curve and final assessments require additional searches, but their checkpoint count and actual episode lengths are not reported. Allocate 20 checkpoint assessments, including final no-op assessment, plus one final human-start assessment, each with 1000 episodes at the full 27000-decision cap. Twenty checkpoints correspond to a 5%-of-training cadence; this is a nominal allowance, not recovered observations. Full-length episodes conservatively offset shorter early episodes. The allocation is 567 million roots, 4.65057936580608e19 FLOPs. With 5–50 checkpoints the result varies by about -6.5% to +13% relative to this estimate. No later independently requested gameplay is added.

Total **5.105494499991552e20 FLOPs**. `calculations-tranche-2.json` preserves the breakdown. Main numerical limitations are the interpreted architecture and evaluation allowance; neither the published wall-clock duration nor simulated game hours is converted directly into FLOPs. Development/ablation runs and other games are outside the one-configured-run work unit.

## MuZero endpoint locator

The original [MuZero v2 PDF, page17, TableS1](https://arxiv.org/pdf/1911.08265v2#page=17) gives Frostbite631,378.53 for MuZero and4,334.67 for the human baseline. The HTML omits this supplementary table. The independent reviewer inspected this PDF page directly.
