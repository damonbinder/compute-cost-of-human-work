# ARC-AGI-1: six additional configurations

The work unit is the first test grid of an ARC-AGI-1 public evaluation task, with two independent AI responses and up to two observed human submissions. These six configurations add coverage distinct from the earlier five ARC1 configurations and all ARC2 points. They do not use published headline accuracy or inherited workload estimates.

## Sources and common human reference

All **2,402 original run files**, 83,238,105 bytes, are retained from [ARC Prize's release at commit 3e9c9d1](https://huggingface.co/datasets/arcprize/arc_agi_v1_public_eval/tree/3e9c9d1a8402aff82356815c106cecaea65cb7d9). The source manifest has 2,418 original files with URL, SHA256 and, for run files, original Git blob identity. Native model endpoints and generation settings are checked in every available response. All prompts' examples and test inputs exactly match the original H-ARC task grids; available Boolean AI correctness labels agree with exact-grid rescoring. No array-index repair is needed.

The [H-ARC paper](https://www.nature.com/articles/s41597-025-05687-1), “User Interface” and “Procedure,” and its [original OSF data](https://osf.io/bh8yq/) define the human work. Reuse the same original action CSV, attempt-summary CSV and task-grid CSV as the reviewed ARC1 tranche. Their hashes are recorded in `shared-human-manifest.json`; the calculator accepts their directory explicitly. The 475 MB action file is not copied into this tranche.

There are 4,101 recorded human participant–task sessions. Ten have no action timestamps and are excluded from both sides' common reference. Include every timed session on the selected tasks, with either success or failure, including completed tasks from participants who later withdrew from the study. The source's whole-study `complete` field does not define task success. No duration is imputed for an unobserved assigned task.

For each session, duration is first automatic `reset_grid` to the last observed `submit` with attempt number at most two. Score the grid on the **actual submit event**, not the attempt-summary grid. Independent review of the first tranche found four summary-grid mismatches, including two summaries storing a later reset after a correct submission. Those fixes are included here. There remain 24 genuine native-label/grid disagreements among the original 7,820 submissions; both outcomes are retained in the audit.

The recorded clock is a proxy for active effort; thinking and editing remain included, and pauses cannot be identified reliably. The first written explanation has no separate start timestamp, so its inseparable interval remains. The separately timestamped final explanation after grid submissions is excluded. Human colored-grid tools and correctness feedback differ from AI text grids and independent guesses. These support the same three concrete flags: `different_task`, `different_inputs_or_tools`, `different_assessment`.

Let `n[t]` be the number of included timed human sessions for task `t`. Weight the AI's two-response token total and success by `n[t]`; divide by the total included human sessions. Human time and success use those same sessions. This gives both axes and both scores a common task distribution. The weights do not represent extra independent AI runs; `ai_attempts=not_applicable` describes a benchmark aggregate. Recorded human-session counts are retained in `human_attempts`.

## Native workload and missing responses

All six releases obey `total_tokens = prompt_tokens + completion_tokens`. Completion already contains reasoning work: do not add GPT-5.4's reasoning subcount again, or retokenize Claude's separately retained reasoning text and add it. Kimi's normalized separate reasoning counter is zero, but its full native completion count is retained; a zero auxiliary field does not establish zero thinking. The two non-thinking configurations are identified by explicit GPT-5.2 effort `none` and Qwen's Instruct model identity, not by inference from this field.

The complete metadata traversal finds no cache-named field and no nonempty `tool_calls` or `num_turns` field. Two independent response records are the observed work per included task. Prior model training and the external exact-grid checker are outside this inference work unit.

GPT-4o lacks attempt 2 for `5a5a2103`; its available attempt has 7,171 tokens. Kimi has missing first-test responses for `1990f7a8`, `212895b5`, `896d5239`, `e2092e0c` and `e9bb6954`; the five available partner responses total 244,851 tokens. Require a complete pair for the point and restrict the human reference to exactly those tasks. These available counters stay in the audit, outside the defined point subset. No error evidence establishes whether an absent response was dispatched or processed, so absent responses are not mechanically assigned zero work or a full generation. Kimi has two additional absent responses on second test inputs, which are outside the H-ARC first-test work unit regardless of completion.

## Cache assumption

With no retained cache counters, central compute charges each native input once plus native output. This is a **full-input-processing assumption**, not a physical cache-adjusted measurement. [Fireworks documents default prompt caching](https://docs.fireworks.ai/guides/prompt-caching), matching prefixes and replica-local caches. Kimi and Qwen's two prompts are identical within each pair; cache reuse could therefore matter, but there is no observed hit rate or replica routing. OpenAI's missing cache decomposition also matters for its short-output runs. All points use `derived_assumed_inputs`.

Two cache sensitivities retain all output: (1) only the second prompt is completely cached; (2) every prompt is completely cached. The latter is an output-only limiting scenario, not an estimated serving configuration. These vary the parameter-multiplication term; context-dependent and cached-context attention remain outside `2P`. Estimated model size varies independently.

## Models

Four existing shared model rows remain unchanged. Two new rows preserve distinctions in the actual source: unsuffixed GPT-4o is not assigned a guessed dated snapshot, and Qwen Instruct-2507 is distinct from Thinking-2507.

| Model | Public date | Active parameters | FLOPs/token | Original evidence and interpretation |
|---|---|---:|---:|---|
| GPT-4o API alias | 2024-05-13 | 50B estimated | 100B | [Original public release](https://openai.com/index/hello-gpt-4o/) dates the alias; the March 2026 run does not reveal its served checkpoint. [Epoch's original energy analysis](https://epoch.ai/gradient-updates/how-much-energy-does-chatgpt-use) supplies 200B central total and a quarter-active assumption. Use 200B × 0.25 = 50B, with 25–100B sensitivity. |
| GPT-5.2 | 2025-12-11 | 100B estimated | 200B | [Public release](https://openai.com/index/introducing-gpt-5-2/). Explicit family transfer from [Epoch's approximately 100B-active GPT-5 estimate](https://epochai.substack.com/p/notes-on-gpt-5-training-compute), not a GPT-5.2 disclosure; 50–200B sensitivity. |
| GPT-5.4-labelled prerelease run | 2026-03-05 | 100B estimated | 200B | [Public release](https://openai.com/index/introducing-gpt-5-4/); source folder identifies GPT-5.4 but native endpoint is `galapagos-alpha`, evaluated February 27. Preserve this qualification; the public date is not an asserted release of that private checkpoint. Same explicit GPT-5-family size prior, 50–200B. |
| Kimi K2.5 | 2026-01-27 | 32B reported | 64B | [Original model summary](https://github.com/MoonshotAI/Kimi-K2.5#2-model-summary) reports 32B activated and 1T total; [Moonshot's release history](https://www.kimi.com/en/help/agent/agent-overview) dates availability. Text grid inputs do not invoke the separately listed vision encoder. |
| Claude Opus 4.6 | 2026-02-05 | 100B estimated | 200B | [Anthropic release](https://www.anthropic.com/news/claude-opus-4-6). The [original serving analysis](https://unexcitedneurons.substack.com/p/estimating-the-size-of-claude-opus), “Active Parameter Count,” calibrates 4–4.5 TB/s from open models, then divides by 43 tokens/s, yielding 93–105B at assumed FP8. Rounded 100B, 50–200B sensitivity; precision and equal serving bandwidth remain assumptions. |
| Qwen3-235B-A22B-Instruct-2507 | 2025-07-21 | 22B reported | 44B | [Original model card](https://huggingface.co/Qwen/Qwen3-235B-A22B-Instruct-2507#model-overview) reports 235B total, 22B active, 94 layers and 8 selected experts of 128. [Qwen's dated News entry](https://github.com/QwenLM/Qwen3#news) explicitly dates this non-thinking release July 21; Thinking-2507 followed July 25. |

All size sensitivities scale FLOPs directly; they are not confidence intervals. Parameter assumptions are shared between points using the same model, not independently fitted to human time or ARC score.

## Reproduction

Python 3.10+ and standard library only. The calculator checks both the new source manifest and the three shared human-file hashes, then reads the original CSV/JSON without executing generated content. Provide explicit source, shared-human, selection, model and **new** output paths:

```sh
python3 -B /path/to/research/arc-v1-expansion/recompute.py \
  --sources /path/to/sources/arc-v1-expansion \
  --human-sources /path/to/sources/arc-v1 \
  --selection /path/to/research/arc-v1-expansion/selection.json \
  --models /path/to/models.csv \
  --output /path/to/new-reconstruction.json
```

In the collection workspace, shared human originals are currently in `collection-work/batches/arc-v1/sources`; after incorporation they are in `dataset/sources/arc-v1`. Neither directory is written by the calculator. [calculations.json](agent-work/derived/arc-v1-expansion/calculations.json) retains every included session, individual response usage and answer, source settings/timestamps, all omitted response slots, three-submission human sensitivity and source-label outcomes.

## Calculated operating points

All values use common human-session weights. AI success counts below are the actual unweighted task-pair counts; the percentages use the stated weights. The CSV and reconstruction retain more precision.

| Configuration | Tasks | Human sessions | Human seconds | AI success | Human success | Tokens | FLOPs |
|---|---:|---:|---:|---:|---:|---:|---:|
| GPT-4o API alias | 399 | 4086 | 350.187714 | 11.3803% | 60.8664% | 11532.576848 | 1.153257685e+15 |
| GPT-5.2 none | 400 | 4091 | 350.347103 | 16.3774% | 60.9142% | 10858.516011 | 2.171703202e+15 |
| GPT-5.4-labelled high | 400 | 4091 | 350.347103 | 96.0401% | 60.9142% | 24668.264483 | 4.933652897e+15 |
| Kimi K2.5 | 395 | 4041 | 350.408562 | 75.3031% | 60.9503% | 51135.654541 | 3.272681891e+15 |
| Opus 4.6 max, 120k thinking | 400 | 4091 | 350.347103 | 97.0178% | 60.9142% | 56151.939868 | 1.123038797e+16 |
| Qwen3 Instruct-2507 | 400 | 4091 | 350.347103 | 17.7463% | 60.9142% | 10864.519433 | 4.78038855e+14 |

| Configuration | Full-input FLOPs | Second prompt fully cached | All prompt cached | Human three-submission seconds / success |
|---|---:|---:|---:|---|
| GPT-4o API alias | 1.153258e+15 | 6.793486e+14 | 2.05299e+14 | 376.162996 / 64.9290% |
| GPT-5.2 none | 2.171703e+15 | 1.225001e+15 | 2.782991e+14 | 376.290638 / 64.9719% |
| GPT-5.4-labelled high | 4.933653e+15 | 3.977509e+15 | 3.00771e+15 | 376.290638 / 64.9719% |
| Kimi K2.5 | 3.272682e+15 | 2.970383e+15 | 2.668083e+15 | 376.382084 / 65.0087% |
| Opus 4.6 max, 120k thinking | 1.123039e+16 | 1.027198e+16 | 9.313566e+15 | 376.290638 / 64.9719% |
| Qwen3 Instruct-2507 | 4.780389e+14 | 2.696764e+14 | 6.131396e+13 | 376.290638 / 64.9719% |

The three-submission human sensitivity leaves the six above/below classifications unchanged. The full-source task-clock means, including final explanations, are also retained in the reconstruction.

## reas-arcagi-v1-gpt4o

Endpoint `gpt-4o`; native settings `{"stream":true,"max_output_tokens":8000}`. Recorded starts range from `2026-03-17T15:53:43.881343+00:00` to `2026-03-17T16:15:08.692778+00:00`. Native gpt-4o alias does not reveal the dated checkpoint. One task lacks a second response; its available usage is outside this defined subset.

Mean input 9479.586637298 + output including reasoning 2052.990210475 = **11532.576847773 tokens**; multiply by 100000000000 FLOPs/token = **1.15325768478e+15 FLOPs**. Exact first-grid successes: 46/399 complete pairs before weighting. The weighted outcome is below the stated human baseline.

Omitted first-test IDs: `5a5a2103`.

All absent source slots, including any non-first tests, are recorded under `source_metadata_diagnostics.empty_response_slots`. Available partner responses remain separately auditable.

## reas-arcagi-v1-gpt52-none

Endpoint `gpt-5.2-2025-12-11`; native settings `{"background":true,"reasoning":{"effort":"none"},"max_output_tokens":196608}`. Recorded starts range from `2025-12-06T22:43:37.192460+00:00` to `2025-12-06T23:06:39.488566+00:00`. Native endpoint was evaluated December 6, before its December 11 public release.

Mean input 9467.020288438 + output including reasoning 1391.495722317 = **10858.516010755 tokens**; multiply by 200000000000 FLOPs/token = **2.17170320215e+15 FLOPs**. Exact first-grid successes: 66/400 complete pairs before weighting. The weighted outcome is below the stated human baseline.

## reas-arcagi-v1-gpt54-high

Endpoint `galapagos-alpha`; native settings `{"background":true,"reasoning":{"effort":"high"},"max_output_tokens":128000}`. Recorded starts range from `2026-02-27T05:39:23.783595+00:00` to `2026-02-27T14:50:35.558214+00:00`. ARC Prize labels the run GPT-5.4; native endpoint is galapagos-alpha, evaluated February 27 before public release.

Mean input 9629.713761916 + output including reasoning 15038.550721095 = **24668.264483011 tokens**; multiply by 200000000000 FLOPs/token = **4.9336528966e+15 FLOPs**. Exact first-grid successes: 383/400 complete pairs before weighting. The weighted outcome is above the stated human baseline.

## reas-arcagi-v1-kimi-k25

Endpoint `accounts/fireworks/models/kimi-k2p5`; native settings `{"max_tokens":100000}`. Recorded starts range from `2026-02-12T16:12:34.499045+00:00` to `2026-02-12T18:01:06.078585+00:00`. Five first tests lack one response; their available usage is outside this defined subset. This is a single-model run, not Kimi Agent Swarm.

Mean input 9446.852264291 + output including reasoning 41688.802276664 = **51135.654540955 tokens**; multiply by 64000000000 FLOPs/token = **3.27268189062e+15 FLOPs**. Exact first-grid successes: 292/395 complete pairs before weighting. The weighted outcome is above the stated human baseline.

Omitted first-test IDs: `1990f7a8`, `212895b5`, `896d5239`, `e2092e0c`, `e9bb6954`.

All absent source slots, including any non-first tests, are recorded under `source_metadata_diagnostics.empty_response_slots`. Available partner responses remain separately auditable.

## reas-arcagi-v1-opus46-max

Endpoint `claude-opus-4-6`; native settings `{"max_tokens":128000,"betas":["effort-2025-11-24","max-effort-2026-01-24"],"stream":true,"thinking":{"type":"enabled","budget_tokens":120000},"output_config":{"effort":"max"}}`. Recorded starts range from `2026-02-03T23:44:41.657522+00:00` to `2026-02-04T04:51:44.548524+00:00`. Native endpoint was evaluated February 3–4, before its February 5 public release.

Mean input 9584.109508678 + output including reasoning 46567.830359325 = **56151.939868003 tokens**; multiply by 200000000000 FLOPs/token = **1.12303879736e+16 FLOPs**. Exact first-grid successes: 387/400 complete pairs before weighting. The weighted outcome is above the stated human baseline.

## reas-arcagi-v1-qwen3-235b

Endpoint `accounts/fireworks/models/qwen3-235b-a22b-instruct-2507`; native settings `{"max_tokens":100000}`. Recorded starts range from `2025-07-22T21:58:26.964153+00:00` to `2025-07-22T23:42:25.619318+00:00`. Native endpoint is the non-thinking Instruct-2507 revision, not Thinking-2507.

Mean input 9471.020288438 + output including reasoning 1393.499144463 = **10864.519432901 tokens**; multiply by 44000000000 FLOPs/token = **4.78038855048e+14 FLOPs**. Exact first-grid successes: 70/400 complete pairs before weighting. The weighted outcome is below the stated human baseline.

