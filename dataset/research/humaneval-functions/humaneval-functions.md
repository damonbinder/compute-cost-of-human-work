# Standalone Python functions: original Qwen and GPT-4o artifacts

Four proposed observations cover three different functions and two actual model configurations. Two additional Qwen attempts are withheld because they do not do the specified job; they are in `agent-work/removed/excluded.csv`, with the ruling in `agent-work/removed/humaneval-functions/`. The task IDs 26, 59 and 119 were fixed for duplicate filtering, integer factorization and parenthesis parsing before inspecting their retained Qwen outcomes. This is a deliberately small task sample, not a representative HumanEval average or a model ranking.

## Sources and selection

**Qwen:** the original [PartialOrderEval paper](https://aclanthology.org/2025.ijcnlp-long.128.pdf), its [author repository](https://github.com/nuprl/partialordereval/tree/b11c1837cc33846355a02d38dc07a62202f7a780), and [released generations](https://huggingface.co/datasets/nuprl-staging/partialordereval-generations/tree/eeb3b01269d0ca09c9bdafa3921520a8aaf8328a) provide the exact Qwen2.5-Coder-7B-Instruct identity, original null-variation prompts, one completion per task, and corresponding test programs, status and stderr. All 164 records are retained in `qwen-null-generations.json` and `qwen-null-results.json`. The solution_desc and canonical solutions in those records are benchmark metadata, **not model inputs**: generate_python.py reads only prompt. The shell command specifies temperature 0, one sample and maximum 8192 output tokens; the vLLM implementation uses chat, greedy sampling and no neural helpers or feedback loop. The token cap is only a diagnostic alternative, not the observed response length. The repository was published after the July 2025 result timestamps; the retained code is the author’s reconstruction of that run, not an independently timestamped runtime log.

**GPT-4o:** the [original EvalPerf brief artifact](https://github.com/evalplus/evalplus.github.io/blob/87418456d3a8c2bc6265f24ff91d2dd0e7993f4b/results/evalperf/gpt-4o-2024-08-06_openai_temp_1.0_evalperf_results.brief.json) identifies GPT-4o-2024-08-06, temperature 1, 100 samples/task, minimum 10 correct before profiling, and at most 20 profiled correct solutions. Each row uses profiled[0], not the shortest output or a weighted average. Correctness rates over all 100 samples are 100%, 86% and 94% for tasks 26, 59 and 119. Those rates give selection context; the numerator here is the estimated work of **one retained passing solution**, not the total search required to obtain success. No 100-sample total is inferred from the 20 profiles.

The October 19, 2024 [source-era EvalPlus code](https://github.com/evalplus/evalplus/tree/886a88f43988e3ff3546b2361e67f938e1add769) saves raw responses separately, but those raw files were not found in the public leaderboard/release artifacts. The brief filename has no perf-instruct/perf-CoT suffix: the historical filename builder would add one for those variants. We therefore reconstruct the default self-contained-script prompt, not a step-by-step or explicit efficiency prompt. Inspecting the retained code still matters: the prime-factor implementation uses a square-root bound, while duplicate filtering and parenthesis checking are linear-time implementations. The human targets include that ordinary algorithmic quality. No target is an industrial package with documentation, deployment, integration or exhaustive formal verification.

Historical HumanEval+ v0.1.10 prompts match the three original HumanEval prompts byte for byte. `recompute.py` checks this directly against the retained gzipped release. Tests were inspected as text; this reconstruction does not execute generated code. Parenthesis and factorization cases are detailed below.

## Compute

No native usage counters are retained in either source. These are source-specific input/output reconstructions, with `derived_assumed_inputs`, not measured FLOPs.

Qwen’s source system message calls it a programming expert. The user wrapper requests **only the function body**, in a Python fence, with no other text. We reconstruct the exact non-tool Qwen chat template around that source prompt, using the original model tokenizer without truncation or padding. The stored completion has already passed through `postprocessing.py`, which keeps the first Python fence, removes an optional function header, and discards surrounding text. Thus counting only the stored body would undercount. Central output is the retained body in its requested fence, one end token, and **25 additional tokens** for an optional header or brief omitted prose. This is a modest instruction-following assumption, not a recovered counter. Zero additional text and 100 additional tokens are retained scenarios. The duplicated docstring/indentation in task 59 makes extraction uncertainty particularly relevant.

GPT-4o input uses the original system message, the default self-contained-script instruction, the source task prompt in a fence, and 12 assumed chat-format tokens. Output includes the complete retained script in a fence, one end token, and **40 omitted-text tokens**. The source prompt permits a script and does not explicitly forbid a short introduction or explanation; 40 allows roughly one short paragraph. The retained artifact cannot determine that amount. Alternatives use zero and 160 additional tokens. Code comments and docstrings already present are counted, not added a second time. There is no evidence of a separate hidden reasoning stream for this non-reasoning model configuration.

The GPT-4o central recipe allocates **one prompt prefill across 32 API choices**. Historical run_codegen defaults to min(n_samples,32); OpenAIChatDecoder submits those choices as one API request, then repeats until 100 are collected. Correctness and profiling preserve sample order and select the first passing records. Since these tasks have no more than 14 failures among all 100, their first retained passing profile is within the first 32 under that default. Shared KV prefill is the best estimate for that batched execution, although the run’s CLI overrides and server internals are not retained. The alternatives allocate four prefills over all 100 outputs or charge a full prompt to the selected response. This is an inferred source execution, not a native cache counter. Ordinary input/output counts record the allocated fresh input plus the response; no padded-finished-branch workload is assumed for the opaque API. Unobserved retries are not assigned a multiplier; the artifacts provide no retry history. The external test runner is the evaluator, not a neural helper writing the function.

The weight-matrix term is 2P per processed token. Attention is counted separately using the current registry shape. Let I be full input tokens, O reconstructed output tokens, and b the number of API choices sharing prefill (32 for GPT-4o, 1 for Qwen):

```
processed = I/b + O
context_sum = I*(I+1)/(2*b) + I*O + O*(O+1)/2
attention_context = context_sum / processed
compute = 2*active_parameters*processed + 4*attention_layers*attention_width*context_sum
```

Sharing prefill does not shorten the prefix attended by each generated token. The causal sums include the current position; output counts include the reconstructed framing and omitted-text allowance. This is a source-specific single-call reconstruction, not the fallback cache-implied constant. The 200,000 context cap does not bind.

| Proposed point | FLOPs | Mean attended context | Parameter-only sensitivity range |
|---|---:|---:|---:|
| code-function-duplicate-filter-gpt4o | 2.08387279246e+13 | 220.542788389 | 1.04266020584e+13–4.16538528518e+13 |
| code-function-prime-factor-gpt4o | 2.65929220563e+13 | 229.366572372 | 1.33060662176e+13–5.31545221658e+13 |
| code-function-parentheses-qwen25coder7b | 5.89385133568e+12 | 193 | Not asserted: reported parameters |
| code-function-parentheses-gpt4o | 3.49003095817e+13 | 368.065412993 | 1.74703463824e+13–6.97347755942e+13 |

GPT-4o bounds use its current 25–100B parameter band and the current OpenAI shape rule, dense=round((N/196608)^(1/3)), L=round(0.65*dense), width=128*dense. These follow the current implementation; the prose formula omits the integer rounding. The central uses the frozen registry's rounded 41 layers and width 8064. Qwen's 28 layers and width 3584 are reported, so neither of the two uncertainties covered by the current range applies. The bars exclude omitted response text, prompt-sharing assumptions and human-time uncertainty. Those remain explicit scenarios in calculations.json.

A retained attempt is a real source record: compute_statistic=total, ai_attempts=1. GPT-4o subset=successful; Qwen's retained parentheses attempt is the sole source attempt, subset=all. The arithmetic is estimated but the attempt identities are known. Human durations are llm_estimate_judgment, not recorded timing transfers. No dollar costs are supplied: source artifacts contain postprocessed text rather than source-stated token counters or a workload-isolated bill, so reconstructing tokens does not qualify for list_price under the current specification. Human costs are also unavailable.

## Models

[Qwen’s September 19, 2024 announcement](https://qwenlm.github.io/blog/qwen2.5-coder/) explicitly releases the 7B Instruct model. Earlier September 17 repository upload is retained but does not alone establish public availability. The original model [config and tensor metadata](https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct/tree/c03e6d358207e414f1eca0bb1891e29f1db0e242) give 28 layers, width 3584, FF width 18944, 28 attention heads, 4 KV heads, vocabulary 152064, and untied embeddings. Counting embeddings, output head, attention/FF matrices, biases and norms yields **7,615,616,512**, exactly agreeing with the source safetensors metadata. This is the Coder model, not Qwen2.5-7B-Instruct. The model’s token coefficient is consequently 15,231,233,024 FLOPs/token; basis reported means calculated from a fully specified published architecture.

GPT-4o reuses the existing August 6 model identity and coefficient after checking its source basis. Its architecture is undisclosed. [Epoch’s original analysis](https://epoch.ai/gradient-updates/how-much-energy-does-chatgpt-use) judges roughly 200B total parameters with a quarter active, yielding the shared **50B active** central; this is an estimate, not an OpenAI measurement. We retain 25B and 100B active alternatives. No image is supplied, so its separately registered vision encoder is not invoked. The model’s original August 6 public API announcement supports its release date. The existing registry record is frozen in model-inputs.csv for calculation; it is not resubmitted in models.csv.

## Human estimates and task-specific inspection

These are **judgment estimates for an expert**, not timing transfers. No task-matched human stopwatch observations were found in these evaluation artifacts. The baseline is an experienced Python programmer already familiar with dictionaries, loops, integer division and balance counters; it excludes learning Python. Time includes reading, designing, entering code, and checking examples and basic boundary cases with normal non-AI tools. It excludes authoring the benchmark’s large hidden test suite. The estimates are not obtained by multiplying generated characters by typing speed.

### code-function-duplicate-filter-qwen25coder7b
### code-function-duplicate-filter-gpt4o

**180 seconds**, bounds 90 and 280 seconds. The subtle requirement is to remove **every occurrence** of any repeated value, not retain one copy. A familiar programmer needs roughly 45 seconds to read and distinguish that requirement, 35 seconds to choose a frequency map plus an order-preserving second pass, 45 seconds to write the small function, and 55 seconds to check an empty list, all-unique list, repeated middle values and an all-repeated list. These are judgment components of a three-minute total, not four observed timings. The low runs the same four at a fluent pace with only the two obvious checks, 90 seconds. The high is the central plus one rewrite-and-retest cycle, 100 seconds, which is what catching the every-occurrence requirement on a failing test actually costs: 280 seconds.

The Qwen attempt uses a seen set and appends the first occurrence. It fails the retained test `[1,2,3,2,4,3,5] -> [1,4,5]`. The human target is a working function, so this attempt is **withheld** under the current failure policy; a partial success score is not supplied by this task. GPT-4o’s first retained profile counts all occurrences, then filters values with count one while preserving order. It passes the source tests and matches the constructed expert target.

### code-function-prime-factor-qwen25coder7b
### code-function-prime-factor-gpt4o

**420 seconds**, plausible scenario 210–900 seconds. Composite integer input is guaranteed; no primality API, factorization library or research is needed. Around one minute is for the input assumptions, 100 seconds to reason through repeated factors and the remaining prime after trial division, two minutes to write/check the loop and updates, and about 140 seconds to test powers of two, odd prime powers, a product of two primes, and 13195. The working target uses standard square-root trial division, not an unbounded scan to n. This is more involved than filtering duplicates, particularly the leftover-prime condition and updating n inside the loop.

The GPT-4o profile handles powers of two, increments odd trial factors, refreshes the square-root bound after division, and returns a remaining n>1 as the largest factor. The retained Qwen result duplicates the docstring and indents its body by eight spaces after the supplied four-space docstring. The original evaluator records **IndentationError** before any functional test. Its mathematical factor loop is also less efficient, scanning factors until n becomes one. Because only postprocessed output is available, we cannot tell whether the raw function was valid with a different indentation/header layout. This attempt is withheld because the evaluated output cannot run. This does not establish that the raw model response was invalid; no silent syntax repair is applied.

### code-function-parentheses-qwen25coder7b
### code-function-parentheses-gpt4o

**300 seconds**, bounds 165 and 480 seconds. Roughly one minute is for reading the two-order requirement and exact Yes/No output, one minute to distinguish a nonnegative prefix balance from merely equal total counts, 90 seconds to implement the helper and two calls, and 90 seconds to check both successful orders, a negative prefix, a nonzero final balance and an impossible pair. The human is not asked to implement a general parser or find permutations of more than two strings. The low halves the reading and design components and trims the checks, 165 seconds. The high adds one implement-and-check cycle of 180 seconds to the central, which is the cost of learning from a failing test that the nonnegative-prefix condition was missed: 480 seconds.

Both retained solutions track balance, reject a negative prefix, require final zero, and test both concatenation orders. Qwen passes its retained original tests, including `[')', '('] -> Yes` and `[')(', ')('] -> No`. GPT-4o’s selected profile passes the expanded source tests. Match refers to producing this working algorithm at the stated scope, not an empirically measured human success probability.

## Reproduction

Install `tokenizers` and `tiktoken` in a normal Python environment. Run from any directory with explicit paths:

```sh
python recompute.py --source-dir /path/to/sources/humaneval-functions --output /path/to/new-calculations.json
```

The calculator never imports or executes source-generated programs. It reads source JSON, tokenizer data, a literal-only extraction of prompt constants, and published architecture dimensions. It checks equal prompt identities, exact parameter metadata, one Qwen completion/result per selected task and records input hashes. It refuses existing outputs and outputs inside source evidence. `calculations.json` retains the central values and alternatives. `model-inputs.csv` freezes the submitted model records for inspection; the calculation independently reconstructs Qwen P and reads the current model coefficients and attention shapes from that frozen snapshot.
