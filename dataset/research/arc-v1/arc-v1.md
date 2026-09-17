# ARC-AGI-1: first test grid, two submissions

Each point compares producing the output grid for the **first test input** of an ARC-AGI-1 public evaluation task. AI compute includes both independent responses, including wrong answers. Human time ends at the second grid submission, or the first when the interface stopped after reporting success. This is a comparison of a defined subset and endpoint, not a reproduction of a published ARC leaderboard score.

## Original records and selection

[ARC Prize's original response collection](https://huggingface.co/datasets/arcprize/arc_agi_v1_public_eval/tree/3e9c9d1a8402aff82356815c106cecaea65cb7d9) supplies prompts, answers, endpoint names, generation settings and native usage. All 2,001 files in the five selected configuration directories are retained and checked against the repository's Git blob hashes. Configuration names and exact endpoints are in [selection.json](selection.json).

[H-ARC](https://www.nature.com/articles/s41597-025-05687-1), particularly “Task interface” and “Procedure,” supplies timed human grid editing. Its [original data](https://osf.io/bh8yq/) and [author repository](https://github.com/Le-Gris/h-arc/tree/463f88cd6522b73197b010bfd7e2373f6bc25bc5) are retained. The action CSV and attempt-summary CSV match OSF's published SHA256 hashes. H-ARC presents only the first test input. Of the 400 evaluation tasks, 19 have another test input; those additional AI responses are retained in the audit but excluded from these points.

The calculator checks every AI prompt's examples and test input against the author's original task grids. It resolves the actual test index from those grids, not array position alone. All available prompts match, and none of these five configurations needs an index correction. Every available Boolean AI correctness label also agrees with exact-grid rescoring.

Require two recoverable responses for the first test. This retains 400 tasks for QwQ, Sonnet and GPT-5.2; 374 for DeepSeek; and 399 for Gemini. DeepSeek has 26 first tests with only one response. Their 669,773 available tokens are preserved outside the point calculation; absent responses have no retained errors establishing whether processing occurred. They are not assigned zero cost or an invented full-response cost. Gemini's release has no file for task `15663ba9`. Every incorrect answer within the included subset remains counted. These selection limits prevent interpreting either incomplete release as a full-400-task run.

## Human duration and outcome

The original evaluation data contain 4,101 participant–task sessions. Ten have no timestamps on any action; exclude those ten from both sides' common reference weights. The remaining 4,091 sessions involve 944 participants and cover all 400 tasks. This includes completed task sessions from people who did not finish the entire study. The source's `complete` field concerns whole-study completion, not task success. Include both successful and failed task sessions.

For each timed session, subtract the first automatic `reset_grid` timestamp from the last `submit` timestamp with attempt number at most two. Each source session ends with reported success or three submissions; the two-submission truncation never invents an unobserved second attempt. Average these elapsed task clocks. This is a recorded interactive-session proxy for active effort: thinking and editing are included, but continuous attention was not measured, and no arbitrary inactivity cutoff is imposed. The full-set median is 260 seconds and the maximum is 4,234 seconds.

Participants also wrote an explanation after their first grid, before feedback. Its completion event shares a timestamp with the first submit; there is no separate writing-start timestamp. The preceding interval averages 66.95 seconds but contains inseparable reasoning and writing. **Do not subtract it as if it were measured writing time.** A separately timestamped explanation after the last submitted grid is excluded. The extra first explanation is a concrete `different_task` qualification.

Humans used colored-grid editing and received correctness feedback between submissions. Models received textual digit grids and generated two independent responses. These support `different_inputs_or_tools` and `different_assessment`. The human population is ordinary study participants after an interface tutorial, without selection for ARC expertise: `typical`.

Human success is recomputed from the grid on the original **submit event**, compared with the author's target grid. Four attempt-summary grids differ from those raw events: two first-attempt summaries contain a later reset instead of the correctly submitted answer, and two third-attempt differences remain wrong either way. The calculation retains all four raw-versus-summary grids. Actual submitted-grid equality differs from the source's `solved` label on **24 of 7,820 submissions**, across `b4a43f3b`, `58e15b12`, `423a55dc` and `310f3251`. All are single-test tasks; this is not a first-versus-second-test join error. The retained task CSV has no later task-specific revision in its published history. The calculation preserves both scores and every discrepancy. Timing follows observed source behavior, including any stopping or feedback based on those labels. On the full set, rescoring moves two-submission success from 60.792% to 60.914%; classifications are unchanged.

## Common weights and arithmetic

For included task `t`, let `n[t]` be its number of timed H-ARC sessions, `c[t]` the total counted tokens in its two AI responses, and `a[t]` indicate whether either response exactly solves the first grid. With `N = sum(n[t])`:

```
tokens = sum(n[t] * c[t]) / N
AI success = sum(n[t] * a[t]) / N
human time = sum(included session seconds) / N
human success = sum(included session successes) / N
FLOPs = tokens * model FLOPs/token
```

The weights give both axes and both performance scores the same task distribution. They do not create extra independent AI observations. `ai_attempts=not_applicable` identifies a benchmark aggregate normalized per question; the actual task and response counts remain explicit here. `human_attempts` counts contributing timed sessions. `human_time_method=other_calculation` reflects arithmetic on original timestamps, and both outcome subsets are `all` within the stated selection.

| Configuration | Tasks | Human sessions | Human seconds | AI success | Human success | Counted tokens | FLOPs |
|---|---:|---:|---:|---:|---:|---:|---:|
| QwQ-32B | 400 | 4,091 | 350.347103 | 10.9753% | 60.9142% | 37,975.924224 | 2.46843507455e15 |
| DeepSeek-V3.2 | 374 | 3,826 | 352.471772 | 64.8458% | 61.1343% | 47,353.349190 | 3.50414784004e15 |
| Sonnet 4.5, 32k thinking | 400 | 4,091 | 350.347103 | 75.3605% | 60.9142% | 35,659.776827 | 7.13195536544e15 |
| GPT-5.2 high | 400 | 4,091 | 350.347103 | 91.2735% | 60.9142% | 34,891.522366 | 6.97830447323e15 |
| Gemini 3 Pro | 399 | 4,082 | 350.412298 | 87.8491% | 60.9015% | 37,362.322636 | 7.47246452719e15 |

The outcomes support `below` for QwQ, `match` for DeepSeek, and `above` for the other three. DeepSeek's approximately four-percentage-point difference is a broad comparison on this sample and protocol; it is not a universal numerical threshold for parity.

The source's original three-submission endpoint is retained as a sensitivity:

| Included set | Three-grid seconds | Three-grid success | Full source task seconds including final explanation |
|---|---:|---:|---:|
| All 400 tasks | 376.290638 | 64.9719% | 399.484234 |
| DeepSeek's 374 | 378.390748 | 65.3424% | 401.666231 |
| Gemini's 399 | 376.400539 | 64.9682% | 399.613180 |

The main labels remain the same under the three-submission human comparison. [calculations.json](agent-work/derived/arc-v1/calculations.json) also retains native-label outcomes for both endpoints, all included session IDs, per-response usage, omitted records and the source configuration settings.

## Tokens and caching

QwQ, DeepSeek, Sonnet and GPT-5.2 obey native `total = prompt + completion`. Completion already includes thinking. QwQ and DeepSeek visibly retain reasoning in assistant content even though the normalized separate reasoning field is zero; zero there is not an absence of thinking. GPT-5.2's explicit reasoning is a subset of completion. Sonnet output likewise already includes thinking. Gemini instead obeys `total = prompt + completion + reasoning`; add its separate thoughts once.

No response in these five releases retains a cache-read count. Count the source input once for every call and all output, including reasoning. **The central values therefore assume the retained input requires full processing.** The [original harness](https://github.com/arcprize/arc-agi-benchmarking/tree/28e67d54b05df5be10281892243c509a42a874f1) explains the normalized counter fields but is a later snapshot, not proof of every historical request option. Its adapters omit cached-token details. No explicit Anthropic cache-creation setting is present in the retained run configuration. The sources cannot establish exact physical cache-adjusted work.

[Fireworks says prompt caching is enabled by default](https://docs.fireworks.ai/guides/prompt-caching), exact prefixes may be reused, and caches are replica-local. Both guesses have identical prompts, so this can materially affect QwQ and DeepSeek. Timing proximity does not establish that a request hit the same replica. Model prices and the harness's calculated costs do not recover native cache hits. The following scenarios vary only cached input, with model size fixed:

| Model | Central, all input charged | Second prompt fully cached | Every prompt fully cached |
|---|---:|---:|---:|
| QwQ-32B | 2.4684e15 | 2.1606e15 | 1.8527e15 |
| DeepSeek-V3.2 | 3.5041e15 | 3.1517e15 | 2.7993e15 |
| Sonnet 4.5 | 7.1320e15 | 6.1737e15 | 5.2155e15 |
| GPT-5.2 | 6.9783e15 | 6.0316e15 | 5.0849e15 |
| Gemini 3 Pro | 7.4725e15 | 6.5219e15 | 5.5507e15 |

For Fireworks the paired-prefix scenario reduces compute by 12.47% for QwQ and 10.06% for DeepSeek. These are sensitivities, not measured hit rates. Context-dependent attention, including attention over cached context, remains outside the `2P` approximation and is added back in `compute_flops` (`research/attention-correction.md`). All five points use `derived_assumed_inputs`, because unknown cache processing is consequential; three additionally use estimated model sizes.

## Models

The exact endpoints come from retained responses, not directory names alone. Dates below concern public release, not the date of a private evaluation.

| Model | Public date | Active parameters | FLOPs/token | Source and interpretation |
|---|---|---:|---:|---|
| QwQ-32B | 2025-03-06 | 32.5B | 65B | [Qwen release](https://qwenlm.github.io/blog/qwq-32b/) and [original model card](https://huggingface.co/Qwen/QwQ-32B/blob/main/README.md): dense, 32.5B total, 31.0B excluding embeddings. Use reported total consistently with the shared coefficient method. The date follows Qwen's displayed publication date. |
| DeepSeek-V3.2 | 2025-12-01 | 37B | 74B | [Original model card](https://fe-static.deepseek.com/chat/transparency/deepseek-v3.2-model-card-0414-EN.pdf) reports 671B total and 37B active, with December 1 release. This endpoint is not V3.2-Speciale. |
| Sonnet 4.5 | 2025-09-29 | 100B estimated | 200B | [Anthropic release](https://www.anthropic.com/news/claude-sonnet-4-5); assumed shared coefficient, supported in scale by the model-specific estimate below. |
| GPT-5.2 | 2025-12-11 | 100B estimated | 200B | [OpenAI release](https://openai.com/index/introducing-gpt-5-2/); transfer of [Epoch's original approximately 100B-active GPT-5 estimate](https://epochai.substack.com/p/notes-on-gpt-5-training-compute), “Pre-training.” No architecture equality is asserted. |
| Gemini 3 Pro | 2025-11-18 | 100B estimated | 200B | [Google release](https://blog.google/products-and-platforms/products/gemini/gemini-3/); weak contemporary frontier-peer assumption, anchored to the original GPT-5 estimate. Google does not disclose this size. |

The four existing model records are shared unchanged. Sonnet's 100B coefficient was originally transferred from a 400B-total Sonnet 3.5 estimate and a quarter-active MoE assumption; neither is a vendor disclosure. A separate [original serving analysis](https://unexcitedneurons.substack.com/p/estimating-the-size-of-claude-opus), “Active Parameter Count,” calibrates 4–4.5 TB/s effective weight bandwidth against three open models. At Sonnet 4.5's 41 tokens/s, assumed FP8 gives 97.6–109.8B active. It supports the rounded scale, while different precision, batching, speculative decoding or serving infrastructure can change the inference. Use 50–200B for Sonnet and GPT-5.2 sensitivity; use the shared wider 30–300B range for Gemini. These multiply each model's FLOPs directly and are not confidence intervals.

## reas-arcagi-v1-qwq32b

Endpoint `accounts/fireworks/models/qwq-32b`; `max_tokens=32768`; recorded March 6, 2025. Its 400 first-test pairs include 44 exact successes before human weighting. Mean prompt 9,473.020288 plus output 28,502.903935 = 37,975.924224 tokens. This dense model is distinct from the hosted QwQ-Plus entry elsewhere in the dataset.

## reas-arcagi-v1-dsv32

Endpoint `accounts/fireworks/models/deepseek-v3p2`; high reasoning, `max_tokens=100000`, streaming; recorded February 21–23, 2026. Its 374 complete first-test pairs include 237 exact successes. Mean prompt 9,525.052797 plus output 37,828.296393 = 47,353.349190 tokens. The 26 omitted first tests and their available responses are individually listed in the calculation. This is the cost of a complete pair on that subset, not campaign cost amortized over surviving questions.

## reas-arcagi-v1-sonnet45-32k

Endpoint `claude-sonnet-4-5-20250929`; thinking enabled with 32,000-token budget and `max_tokens=64000`; recorded September 30, 2025. Its 400 first-test pairs include 295 exact successes. Mean prompt 9,582.109509 plus output 26,077.667319 = 35,659.776827 tokens. The thinking budget is a limit, not a count of tokens generated.

## reas-arcagi-v1-gpt52-high

Endpoint `gpt-5.2-2025-12-11`; high reasoning, background mode, `max_output_tokens=196608`. The original timestamps are December 8, before public release; preserve that prerelease-evaluation qualification. Its 400 first-test pairs include 362 exact successes. Mean prompt 9,467.020288 plus output including reasoning 25,424.502078 = 34,891.522366 tokens. Do not add the separate reasoning subcount again.

## reas-arcagi-v1-gemini3pro

Endpoint `gemini-3-pro-preview`; `max_output_tokens=65536`, automatic function calling disabled. No explicit reasoning-level argument is retained. Most requests stream; four first-test responses omit the streaming flag. Original timestamps are November 14–15, before public release. Its 399 first-test pairs include 346 exact successes. Mean prompt 9,608.933366 plus output and separate thoughts 27,753.389270 = 37,362.322636 tokens. No run file for `15663ba9` was released in this snapshot.

## Reproduction

Python 3.10+ and the standard library suffice. The script reads JSON and CSV; it never runs model-generated content. Give explicit paths to the retained source directory, this selection file, a model registry containing these five IDs, and a **new** output file outside the source directory:

```sh
python3 -B /path/to/research/arc-v1/recompute.py \
  --sources /path/to/sources/arc-v1 \
  --selection /path/to/research/arc-v1/selection.json \
  --models /path/to/models.csv \
  --output /path/to/new-reconstruction.json
```

[calculations.json](agent-work/derived/arc-v1/calculations.json) contains the retained reconstruction. Sources are identified by URL, local path and SHA256 in `agent-work/sources/arc-v1/source-manifest.json` after incorporation; in this candidate the source directory is `../sources`. Every listed source hash is checked before calculation. Passing a larger registry changes its whole-file hash but not these five points. The raw timestamps, native totals and assumption scenarios remain separate from the two plotted values.
