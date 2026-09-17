# Pokémon Crystal through defeating Red

## game-pokemon-crystal-gemini3pro-red

One Gemini 3 Pro Preview run from a new game through defeating Red on Mt. Silver, including the Elite Four and all 16 badges. The human target is the same completion milestone for an experienced Pokémon player, using the game without AI, external walkthroughs or a speedrun route. Neither side must complete the Pokédex or Battle Tower. The estimate is **3.7563 × 10²⁰ FLOPs and 12 hours of human active play**. Match means comparable completion, not equal efficiency or identical battle losses.

## Original run and endpoint

[Joel Zhang's original report](https://blog.jcz.dev/gemini-3-pro-vs-25-pro-in-pokemon-crystal), “Milestone Comparison,” reports **24,178 turns and 1.88 billion tokens** through defeating Red. These are author-reported totals; they are not our assumed turn count or a conversion from API cost. The report describes structured RAM observations, screenshots, a map of observed tiles, notes, self-written tools and temporary agents. It documents a mid-run clarification of the map tool's semantics. It also says the system had no web access. Human inputs differ: the human uses the ordinary game interface and remembered gameplay knowledge, while the agent receives RAM-derived information and is instructed to ground its discoveries in observations.

The [original tracking repository](https://github.com/waylaidwanderer/gemini-plays-pokemon-public) provides additional task evidence. The race starts at commit `003af6fa14f06cd7c6b2cdeca276eaed83189c1c`, labelled Turn 0, on 19 November 2025. Its notepad says to start the game and lists no team; its tools and agents are empty. The reported finish turn is commit [`f80ac9b2fac095ce81eb3797e46c257090b06861`](https://github.com/waylaidwanderer/gemini-plays-pokemon-public/commit/f80ac9b2fac095ce81eb3797e46c257090b06861), timestamped **8 December 2025, 02:32 UTC**. The notes still describe the final Red battle, illustrating that memory text is not itself an exact event scorer. Completion is reported by the author and his milestone figure; it is not independently replayed from the game state here.

The finish tools are `escape_collision`, `find_path`, `force_press_button`, `press_sequence` and `select_move`. They expose actual gameplay demands: navigation, obstacle recovery, repeated menu choices and battles. The notes document all eight Kanto badges, the Power Plant and radio quests, and exploration of Mt. Silver. The much later branch head describes Battle Tower attempt 83. That later work is excluded. The later coauthored paper [Continual Harness](https://arxiv.org/html/2605.09998v1) says November completion; the December checkpoint and contemporaneous report are the more specific evidence for this race.

The public replay service now lists three later Flash runs and returns 404 for this historical race. Its absence does not establish missing work in the author's total, but native request messages and per-request usage were not recoverable from it. The Git repository retains state and tools, not native billing counters.

## Compute

The shared `gemini-3-pro` model uses **100B active parameters and 200B FLOPs per processed position**. Google's [18 November launch](https://blog.google/products-and-platforms/products/gemini/gemini-3/) establishes preview availability. The [model card](https://deepmind.google/models/model-cards/gemini-3-pro/) does not disclose the dimensions needed for an operation count. The size is a shared assumed prior, based on a contemporary frontier-model scale: [Epoch's original GPT-5 estimate](https://epochai.substack.com/p/notes-on-gpt-5-training-compute), “Pre-training,” estimates roughly 100B active. Transferring that scale to Gemini remains weak evidence; 30–300B is a parameter sensitivity, not a confidence interval. No exact hidden API revision is invented.

The central accounting assumptions are:

- The author's 1.88B total includes input, generated reasoning/output and helper calls. There is no separate reasoning multiplier. This interpretation of the reported total is not independently verified against its original counter implementation.
- All reported input is charged as fresh processing. Cache decomposition is absent. Gemini supports implicit caching, so this is a **full-prefix workload approximation**, not a measurement of newly processed tokens. We remove no *known* cache reads because none are supplied; that is not an observed zero. The high repeated-prefix workload makes this a material limitation.
- One current screenshot is presented per primary turn. This yields **24,178 estimated image presentations**, not an observed screenshot count. Original prompts and image history are unavailable.
- For the text/vision split, assume the high image setting's **1,120 accounting units per image**, documented in the [Gemini 3 guide](https://ai.google.dev/gemini-api/docs/generate-content/gemini-3). Subtract 27,079,360 such units from the reported combined total, leaving **1,852,920,640 estimated text tokens**. The input-output category describes the assumed counted quantity, including generated reasoning; this estimated text remainder is not an API-observed text counter. The original aggregate does not disclose that decomposition.
- Visual accounting units are not assumed to be physical positions. Use **1,024 physical visual positions per screenshot** as a separate proxy, and four 224-pixel CLIP ViT-bigG/14 frontend passes. Four passes here are a compute proxy, not a claim that Gemini actually makes four crops. The original [CLIP configuration](https://huggingface.co/laion/CLIP-ViT-bigG-14-laion2B-39B-b160k/blob/4054289/config.json) supplies 48 layers, width 1,664, feedforward width 8,192 and 256 patches plus a class position. This is not Gemini's disclosed image encoder.

The frontend count includes patch projection, attention projection matrices, feedforward matrices and attention matrix products at two FLOPs per multiply-add. It is 967,491,772,416 FLOPs per proxy pass. It excludes normalization, nonlinearities and any unknown Gemini resampling/projector. The backbone approximation excludes context-dependent attention, including attention over cached keys; `compute_flops` adds that term separately (`research/attention-correction.md`), and this row is the weakest application of it in the file. Emulator execution, deterministic pathfinding and other non-neural game code are outside this neural FLOP estimate.

```
text = 1,880,000,000 − 24,178 × 1,120 = 1,852,920,640
visual positions = 24,178 × 1,024 = 24,758,272
frontend = 24,178 × 4 × 967,491,772,416
FLOPs = 200,000,000,000 × (text + visual positions) + frontend
      = 375,629,350,464,293,896,192
```

The arithmetic retains digits for reproducibility; the source's rounded token total and assumed architecture do not support that physical precision. Image processing contributes little relative to the uncertain backbone total. If the 1.88B figure already excludes images, the subtraction would undercount by about 1.4%.

### Helpers and retries

All **64 agent-configuration changes** from Turn 0 to the finish are retained. They show **28 creation episodes** and **11,340 primary-turn intervals with a helper available**, including battle strategists, navigation advisers, clue analysts and switch-puzzle solvers. Availability is not an invocation count. The finish has no custom agent, but that does not mean the run had none. The author's earlier Blue recipe of a fixed critic every 25 turns is not silently transferred to this different harness.

The central estimate treats helper usage as included in the reported total. If the total omitted it, a stress scenario adds one 12,000-token helper call per turn in which a helper definition exists: **136.08M extra text tokens**, increasing compute to 4.0285 × 10²⁰ FLOPs. The scenario's call rate is assumed; its 12K allowance permits a task state and notes of several thousand tokens, a short specialist prompt and generated reasoning. It is not an empirical bound.

The author reports substantial API downtime, but downtime is not equivalent to successful generation. The central estimate assumes completed responses and visible retries are represented in the author's total. No native errors establish lost completed responses, and we do not multiply outage hours by a token cap. A separate stress calculation adds 2% completed-call-equivalent work; it is not an observed retry rate. Model calls used by the developer to build the harness before this run are outside task execution.

### Sensitivities

`calculations.json` retains one-at-a-time alternatives. Charging 30B or 300B active gives approximately 1.13 × 10²⁰ or 1.13 × 10²¹ FLOPs. If 50% or 90% of the author's aggregate were cache reads, the corresponding results would be 1.88 × 10²⁰ or 3.72 × 10¹⁹ FLOPs. These fractions merely expose sensitivity; they are not fitted cache estimates or limits. Recovering native cache counters would materially improve this entry. Low-media and repeated-image-history alternatives are also retained; the repeated-history calculation holds frontend reuse fixed and is not a reconstruction of historical serving behavior.

## Human active play

Two original human recordings give task-specific timing anchors:

| Recording | Player and endpoint | Recorded timing used |
|---|---|---:|
| [LongplayArchive](https://www.youtube.com/watch?v=mYaoA_EGFjs) | Terua; chapters explicitly identify Red and the second credits | Second credits start at 8:50:47; later legendary encounters excluded |
| [World of Longplays](https://www.youtube.com/watch?v=eeFFCjdfjYY) | Spazbo4; description says played in one sitting and ends after Red | Full video length 10:29:24 |

The first recording's chapters put Lance at 6:42, first credits at 6:52, Kanto gym leaders from 7:11 to 8:23, and Red at 8:40. This supports a substantial Johto campaign followed by a shorter Kanto/Red segment, rather than treating an Elite Four finish as the full Crystal task. The second recorder's single-sitting statement supports elapsed playback as a useful active-play anchor, but does not establish no breaks, editing or assistance. World of Longplays warns that most of its videos use savestates. These are efficient illustrative completions, not measured ordinary-player averages or speedrun records. The first includes optional Suicune and Lugia encounters before Red; chapter starts do not isolate their durations, so no exact deduction is made.

For the first recording, subtract the 200 seconds between the first-credits chapter at 6:52:13 and Fast Ship at 6:55:33. For the second, subtract assumed allowances of 200 seconds for first credits and 180 seconds for closing credits. This gives 31,647 and 37,384 seconds and an anchor mean of **9.59 hours**. Battle animations and dialogue still require ongoing attention and repeated decisions, so they are included; unattended pauses and passive credits are not intended as human active work. The available recordings do not permit an exact idle-time subtraction, which is one reason the row is a transfer estimate.

Allow **1.5 additional hours** for less practiced navigation, checking routes and solving puzzles, plus **1 hour** for team preparation and training. These are judgments about an experienced but unoptimized player, informed by the run's actual lighthouse pit, radio, switch-room and Mt. Silver obstacles, and its overleveled starter strategy. They also allow for the efficient recordings' potential savestate advantage. The result is 12.09 hours, rounded to **12 hours / 43,200 seconds**. A 9–18-hour sensitivity covers efficient repeat play through slower revisiting and preparation; it is not a population interval. No assumption requires the human to reproduce the agent's detours or its zero-loss record.

`human_attempts=2` counts the contributing donor recordings, not a two-person measurement of the target population. Their successful selection does not establish a 100% human success rate. Performance is match by construction because the human estimate targets reaching the same Red-defeated endpoint, with retries allowed on both sides.

## Reproduction

With Python 3 (standard library only), run:

```
python research/recompute.py /path/to/sources /path/to/new-output
```

Keep `assumptions.json` beside the script, or pass `--assumptions`. The script checks 81 source hashes, verifies the reported quantities and exact finish commit, reconstructs helper availability from all in-race configuration changes, reads the two original video descriptions and lengths, and writes new calculation files. It does not run a model, an emulator or downloaded code.
