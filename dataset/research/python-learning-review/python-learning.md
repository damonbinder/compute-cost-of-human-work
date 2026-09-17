# Learning to write short Python functions

**The human-learning estimate in this note is superseded.** On 2026-09-14 the
human side of every row it covers was re-estimated as the active hours to reach the
capability the run bought, read off a published hours-to-proficiency table, rather
than the hours to move a benchmark score. The current figures, the method and the
per-row arithmetic are in [skill-acquisition human learning time](../skill-acquisition-human-time.md).
Everything else here — the endpoints, the task inspection and the compute
reconstruction — still stands.

These are estimates of active learning time to five specified HumanEval endpoints. They are not observed learning curves. The central estimates are **35, 70 and 110 hours** from no programming experience, and **90 and 140 additional hours** from the two stated Python baselines. AI compute is outside this review.

## Quantity being estimated

The human is an ordinary adult with adequate English reading, ordinary numeracy and routine computer use. The three Codex comparisons start with no programming knowledge. The Code Llama comparisons start with existing Python function-writing ability at the specified initial score; they do not charge for acquiring that initial ability.

The target is the original 164-problem HumanEval distribution, with one first submitted function per unseen problem. The learner receives the original function signature, docstring, examples and any supplied helper code, then writes a solution without generative-AI assistance or executing it before submission. Success requires passing the original tests. A learner can inspect and revise their own draft before submitting. The target is an aggregate rate, not the same individual correct answers as the model, mastery of all problems, or general professional software competence.

During learning, the person can read instruction and ordinary Python documentation, trace worked examples, execute and debug practice programs, and receive human or deterministic feedback. Practice uses other problems and variations, not memorized HumanEval answers. Active reading, implementation, unsuccessful attempts and error review are included. Breaks, elapsed calendar time, earlier learning and a separate final assessment are excluded. These different learning inputs justify `different_inputs_or_tools` relative to next-token corpus training. The assumed endpoint uses the same assessment; the existence of other assessments in contextual studies does not by itself justify `different_assessment`.

## Verified model endpoints

| Point | Starting model result | Ending result | Original locator |
|---|---:|---:|---|
| Codex 300M | Near zero | 13.17% | Chen et al., Table 1 and §3.4 |
| Codex 2.5B | Near zero | 21.36% | Chen et al., Table 1 and §3.4 |
| Codex 12B | Near zero | 28.81% | Chen et al., Table 1 and §3.4 |
| Code Llama 7B | Llama 2 7B: 12.2% | 33.5% | Rozière et al., Table 2 |
| Code Llama 34B | Llama 2 34B: 22.6% | 48.8% | Rozière et al., Table 2 |

The [Codex paper](https://arxiv.org/abs/2107.03374v2) reports single-sample pass@1; its selected temperature is 0.2. The near-zero starting result is the paper's GPT baseline characterization, not an invented exact zero at each size. The [original Code Llama paper](https://arxiv.org/abs/2308.12950v1) uses greedy decoding for Table 2 pass@1; its p. 6 table agrees with the retained later HTML. The latter rows concern base Code Llama after code and long-context training, not Code Llama–Python or Instruct. These model scores define assumed human targets; they are not observations of humans after the proposed hours.

## What the tasks require

The complete prompt inventory was inspected, followed by the full prompt, canonical solution and tests of 29 tasks retained in `inspected-tasks.json`. Selection combines a spread through the numbered set with examples of particular prerequisite skills; it is not a randomly weighted estimate of task difficulty or human accuracy.

| Examples | Learning requirement relevant to the budget |
|---|---|
| 2, 35, 52 | Arithmetic or a basic built-in; translating strict versus non-strict conditions. |
| 8, 14, 24 | Accumulators, list construction, slices and loop boundaries. Empty input and equality cases matter. |
| 0, 20, 43 | Pair search and distinguishing two positions; a nested-loop solution is sufficient. |
| 72, 104, 112, 128, 136, 144 | Composing familiar operations while preserving all conditions, return types, signs and empty cases. |
| 1, 10, 63, 80, 96 | State tracking, repeated search, recurrence, windows and elementary number operations. |
| 32, 129 | More substantial algorithm selection. The lower targets do not require this entire tail. |

Short reference code is not a reliable measure of learning difficulty: task 115 compresses a word problem into a short expression, while task 120 contains an important zero-length exception. Task 79 benefits from knowing a built-in conversion. The relevant learning work is recognizing operations, translating specifications and checking boundaries, not reproducing the reference program's syntax. Original tests remain the endpoint; no stronger production-quality test suite is substituted.

## Learning evidence and its limits

**Beginner instruction can produce some independent code within a few hours.** [Prat et al. (2020)](https://www.nature.com/articles/s41598-020-60661-8), Methods and Results, studied 36 analyzed adults without programming experience after ten 45-minute Python sessions. The later Rock–Paper–Scissors task was partially decomposed, permitted execution, and received stepwise credit out of 51. Mean credit was 57%, with large individual variation. This supports a short initial foundation, but 57% is not a HumanEval pass rate. The assessment followed instruction; its time is not included in the learning exposure. The source does not establish which HumanEval endpoint is reached in 7.5 hours.

**Writing practice is a substantial component of an introductory course.** [Python Grids (2018)](https://link.springer.com/article/10.1186/s41039-018-0085-9), “Course context” and “Collected data,” reports a 46.6-hour sum of per-exercise median self-reported effort for students with no previous programming. The course covered procedural Python, lists, files and elementary objects, with mostly 1–100-line exercises across nine rounds. This is neither a median student's complete course time nor a recorded HumanEval learning duration. It checks the scale of practice allowances; lectures, reading and voluntary activities are not all included in that number.

**The available HumanEval student experiment does not supply a fresh-learning curve.** [Gardella et al. (2026)](https://juholeinonen.com/assets/pdf/gardella2026fast.pdf), §§3.1–3.3, recruited mostly students beyond CS1. Initial tasks used either a partner or AI; the later solo assessment repeated the same eight selected tasks. Its prior-study estimate of roughly 25 solo minutes for four selected tasks is task-performance context, not training time. The cited 2024 study's full text was not available through the original accessible route, so no unseen results or corrigendum were used.

**The larger unaided control group is mainly experienced.** The original [RealHumanEval data](https://github.com/clinicalml/realhumaneval) at commit `29de154c63003532bc8c26437b509b7b3e481790` contains 243 participants, including 39 `nomodel` controls. Of those controls, 3 described themselves as beginning Python users, 22 intermediate and 14 advanced. Its 17 selected tasks mix HumanEval-related functions with editing and data manipulation. The [paper](https://arxiv.org/html/2404.02806v2) permits testing during the session and provides no accumulated learning hours. It cannot identify the five transitions here. The README's older participant count is not used. [StudentEval](https://arxiv.org/abs/2306.04556) assesses students prompting a model, not unaided code writing.

## How the budgets were chosen

The three components below are judgments about work, not measured subtotals. Instruction includes tracing and short guided drills. Writing practice includes attempts that fail, debugging and immediate feedback. The final component includes delayed reimplementation, mixed problem sets and reviewing first-submission mistakes after committing an answer; it is distinct from debugging the initial practice task.

The lowest route emphasizes a restricted repertoire of useful operations. The middle beginner route adds collection fluency and substantial independent practice; its 40-hour writing component is comparable in scale to the Python Grids exercise evidence. The highest beginner route adds composition and elementary algorithmic work, then more mixed practice without immediate hints. The two additional-learning routes omit the initial setup and syntax foundation but invest more heavily in independent transfer and handling unfamiliar specifications.

For scale, 18 hours of practice allows roughly fifty short attempt-and-feedback cycles averaging about twenty minutes. A 40–86-hour component permits more variations, harder attempts and rework. Those counts and rates are illustrations of the assumed budget, not an observed exercise schedule or a formula converting benchmark questions to hours. Actual learning should stop at the capability endpoint, not after a required number of exercises.

No reported study establishes the link from these activities to the exact aggregate scores. The numerical endpoints do not uniquely identify a person's knowledge: two people with the same score may have different conceptual gaps. The descriptions below choose ordinary, broad elementary repertoires rather than memorization or an unusually specialized set of strengths. That mapping is the main uncertainty, and it would require fresh unaided pre/post assessments to test it. The duration classification is therefore `assumed` / `estimated`, with `point_estimate`, `human_attempts=not_applicable` and `human_time_subset=not_applicable`. None of the contextual study samples is counted as a contributing timing sample.

| Route | Instruction/tracing | Writing/debugging | Delayed practice/review | Total | Efficient / slower scenarios |
|---|---:|---:|---:|---:|---:|
| Codex 300M | 12 h | 18 h | 5 h | 35 h | 12 / 100 h |
| Codex 2.5B | 20 h | 40 h | 10 h | 70 h | 25 / 200 h |
| Codex 12B | 26 h | 66 h | 18 h | 110 h | 40 / 350 h |
| Code Llama 7B | 14 h | 56 h | 20 h | 90 h additional | 30 / 300 h |
| Code Llama 34B | 24 h | 86 h | 30 h | 140 h additional | 50 / 450 h |

Efficient scenarios assume strong transfer from ordinary mathematical and verbal reasoning, well-chosen exercises and prompt feedback. Slower scenarios allow repeated misconceptions, less effective materials and more practice before independent transfer. They concern the same starting/ending targets; they are not confidence intervals, measured quantiles or physical bounds. No generic course duration or score-percentage slope determines the central values.

## agen-codexfer-codex300m

**35 hours = 126,000 seconds.** Start without programming. Build basic expressions, function returns, conditionals, a few list/string operations and simple loops. The assumed endpoint is 13.17% first-submission accuracy over the full benchmark. This route leaves most unfamiliar or composed problems unsolved. The 12–100-hour scenarios primarily vary initial concept acquisition and the amount of practice needed to write elementary functions independently.

## agen-codexfer-codex2p5b

**70 hours = 252,000 seconds.** Start without programming. Broaden basic function writing to strings, lists, conversions, accumulators, filtering and common edge cases. The assumed endpoint is 21.36%. This is a separate full route from the same starting cohort; it includes its foundation once. The 25–200-hour scenarios vary fluency and generalization from worked exercises to new specifications.

## agen-codexfer-codex12b

**110 hours = 396,000 seconds.** Start without programming. Add functions combining several operations, nested iteration, simple counting/search and parsing. The assumed endpoint is 28.81%. This does not require complete algorithmic competence. The 40–350-hour scenarios allow large variation in independent problem decomposition and first-submission reliability.

## agen-codexfer-codellama7b

**90 additional hours = 324,000 seconds.** Start able to write elementary Python functions using scalar operations, branches and simple loops, with an assumed 12.2% aggregate first-submission rate. Acquire broader collection operations, composition, basic search/counting and more reliable boundary handling to target 33.5%. The learner's earlier effort is excluded. The 30–300-hour scenarios reflect differences in which skills underlie the same starting score and how quickly they transfer.

## agen-codexfer-codellama34b

**140 additional hours = 504,000 seconds.** Start with functions, loops and common list/string operations, at an assumed 22.6% aggregate rate, but with gaps in composition and unfamiliar specifications. Improve multi-step translation, nested data, state tracking, algorithm selection and mixed first-submission practice to target 48.8%. This narrower capability does not require professional software-engineering experience. The 50–450-hour scenarios vary the initial repertoire and time needed for robust transfer.

## Reproduction

`assumptions.json` contains the selected budgets and scenarios. `recompute.py` requires only Python's standard library. It checks the original 164-task file and the unaided-control count, extracts the inspected tasks, sums the component hours and writes the proposed field values. It does not execute source programs, estimate AI compute or modify evidence. Use an output directory that does not exist:

```sh
python3 research/python-learning-review/recompute.py --source-dir agent-work/sources/python-learning-review --config research/python-learning-review/assumptions.json --output-dir /absolute/path/to/new-output
```

The source and configuration paths may be absolute when running elsewhere. `human-fields.json` records the human-side estimates and their assumed learning budgets. AI compute is documented separately in the linked model-training notes. `performance_vs_human=match` is justified by the explicitly matched human learning target, not empirical human timing evidence.
