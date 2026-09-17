# Counting r in strawberry

Ten points describe the mean compute of answering one fixed question: **“How many times does the letter r appear in strawberry”**. Max Woolf made 100 fresh calls to each of ten OpenRouter endpoints on August 10, 2025. The required answer is **3**. This collection varies the model and its sampled response, not the word or question.

## Source and work unit

The [original dataset](https://huggingface.co/datasets/minimaxir/llm-strawberry/tree/a0319935ae3810b66a207266ec67f9f41afe6972) has exactly 1,000 rows, all with positive input/output token counts and nonempty responses. No `(model, created)` keys or complete records are duplicated. The [original notebook](https://github.com/minimaxir/llm-blueberry/blob/9038b39cdb58772e3be0a1327e1314c902a47620/llm_count_letters.ipynb), cells 3–7, defines the requested model IDs, 100 trials and a single user message. It passes no temperature, reasoning, output-length or provider-selection settings to the primary calls.

The notebook saves `response["usage"]["prompt_tokens"]` and `completion_tokens`, plus the returned text, optional reasoning text and extracted count. The Parquet export contains these flattened fields; it does not retain the complete API objects, provider routes, finish reasons or cache/reasoning-detail counters. We preserve its original counts rather than reconstructing prompts from the visible question. Input counts differ among providers/models, including within Kimi and gpt-oss; the actual wrapper responsible for each difference is not recoverable.

The separate Gemini 2.5 Flash call extracts a numerical answer for evaluation. It receives the primary response and is not used to solve or improve the answer, so its compute is outside the task. No primary-model retries or external tool calls are present in the notebook's request recipe. All 100 returned calls per model are included, including incorrect answers.

## Token accounting

For each model, sum exported prompt and completion tokens, divide by 100, then multiply by its shared `2 × active_parameters` coefficient. This is a mean over 100 actual one-question attempts: `compute_statistic=mean`, `compute_subset=all`, `ai_attempts=100`.

Reasoning belongs to completion tokens. OpenRouter's [April 18, 2025 usage example](https://openrouter.ai/blog/announcements/smarter-charts-inline-svgs-and-live-usage-accounting/) nests reasoning under completion and makes total tokens equal prompt plus completion. Its [usage documentation](https://openrouter.ai/docs/cookbook/administration/usage-accounting) identifies native tokenizer counts. The retained gpt-oss records independently support this accounting: native completion totals exceed retokenized final text plus reasoning by only 9–12 Harmony framing positions. We do **not** add the reasoning strings again. For proprietary models, those strings may summarize reasoning and cannot replace its native count.

Reasoning text is returned in 98/100 mini, 99/100 nano, and all Pro/gpt-oss calls. Other endpoints return none in that separate field. Kimi often writes a thought-process explanation directly in its normal response, which is already part of completion. We do not infer a routing decision or absence of internal work from a null reasoning string.

Cache decomposition was not exported, so the central estimate counts full prompts. `compute_evidence=derived_assumed_inputs` reflects this assumption and, for closed models, the parameter priors. A deliberately extreme all-prompt-cached scenario is retained in `calculations.json`; it removes the whole prompt term, without claiming that these short requests were cache eligible or actually cached. At fixed size, that changes compute by 3.1–36.0%, depending on the model. No unobserved cache reads are subtracted centrally. The 2P convention also omits context-dependent attention; `compute_flops` carries that term separately (`research/attention-correction.md`).

## Response checks and human comparison

The source's count extractor grades the final numerical answer, not every explanatory sentence. A local audit recovers explicit answer phrases from all 1,000 retained responses and agrees with all source labels. Gemini 2.5 Flash gives **3 in 90 calls, 4 in 8, and 2 in 2**. The other nine endpoints give the correct count in 100/100. All ten wrong answers are retained verbatim in the calculation audit. The repository's later false-negative repair notebook modifies the blueberry experiment, not this strawberry dataset.

### Human time

Use **4 active seconds** for a literate adult encountering this prompt afresh: roughly two seconds to understand the ten-word question, 1.5 seconds to inspect the ten-letter word, and half a second to report the count. This is a task-inspection estimate, not measured timing. **3–8 seconds** are the bounds. The floor is set by reading: at the 238 to 260 words a minute Brysbaert (2019) reports for adult silent reading, the question's own words take about two seconds, so three seconds is as fast as a fresh encounter goes once a chunked look at the word and a half-second response are added. The ceiling allows a deliberate letter-by-letter scan of the ten letters at the roughly 300 milliseconds an item that serial enumeration costs, plus one re-count. The human need only give the count; the AI's optional explanations do not enlarge the required deliverable.

The assumed human baseline can count the three visible occurrences reliably. The nine 100/100 results support `match`; Flash's one-in-ten errors support `below` against that baseline. These judgments concern this exact question. Human time is not a repeated-100-question practice time, and no human sample count is implied: `human_time_evidence=assumed`, `human_time_method=estimated`, `human_time_statistic=point_estimate`, and human subset/attempts `not_applicable`.

## Model assumptions

The five existing model records are copied unchanged after checking their original numerical anchors. New records are GPT-5 Chat, GPT-5 nano, gpt-oss 20b, Kimi K2 Instruct and Gemini 2.5 Flash. API aliases identify the endpoints sampled on August 10; returned provider-specific revisions were not preserved.

| Model | Active parameters | Basis | Public date |
|---|---:|---|---|
| Claude Opus 4.1 | 180B | Shared estimate from a model-specific throughput/bandwidth scenario | 2025-08-05 |
| Claude Sonnet 4 | 100B | Shared estimate | 2025-05-22 |
| GPT-5 Chat | 100B | Weak GPT-5 family transfer | 2025-08-07 |
| GPT-5 mini | 20B | Shared small-reasoning-model prior | 2025-08-07 |
| GPT-5 nano | 8B | Weak transfer of the GPT-4.1 nano small-model prior | 2025-08-07 |
| Gemini 2.5 Flash | 40B | Efficient-MoE peer estimate | 2025-06-17 |
| Gemini 2.5 Pro | 100B | Shared frontier-peer estimate | 2025-06-17 |
| Kimi K2 Instruct | 32B | Reported active count | 2025-07-11 |
| gpt-oss 120b | 5.1B | Rounded reported active count | 2025-08-05 |
| gpt-oss 20b | 3.6B | Rounded reported active count | 2025-08-05 |

**GPT-5 Chat.** The [OpenAI developer release](https://openai.com/index/introducing-gpt-5-for-developers/) announces the non-reasoning Chat model separately from the reasoning API model on August 7. The point uses `openai/gpt-5-chat`, not a claim about ChatGPT's consumer router. [Epoch's original analysis](https://epochai.substack.com/p/notes-on-gpt-5-training-compute), “Pre-training,” estimates about 100B active for GPT-5. We transfer that family scale to the separate Chat model with **30–300B** scenarios. The source does not disclose Chat's architecture or establish equal weights or sizes.

**GPT-5 nano.** OpenAI's same announcement introduces nano as the smallest API tier, without a count. We preserve the established GPT-4.1 nano 8B prior across this adjacent small-model tier. Its numerical anchor is the original [Ministral 8B release](https://mistral.ai/news/ministraux/); [Bowdon's original account](https://cbowdon.github.io/posts/gpt-params/index.html), final substantive paragraph, names it as a comparator for his GPT-4.1 nano NLP tests, but supplies no raw benchmark data. This is a two-step weak transfer. We do not use that page's regression, which assigns different sizes to different reasoning settings of the same model. The contemporaneous disclosed gpt-oss active sizes 3.6B and 5.1B show that small reasoning models can occupy this scale; they do not measure nano. Retain **1–20B** scenarios rather than infer size from this task's 100% accuracy or API prices.

**Gemini 2.5 Flash.** Google's [original report](https://storage.googleapis.com/deepmind-media/gemini/gemini_v2_5_report.pdf), §2.1, identifies sparse MoE architecture without an active count. The 40B prior uses the contemporaneous [DeepSeek-V3](https://huggingface.co/deepseek-ai/DeepSeek-V3) 37B and [Mixtral8×22B](https://mistral.ai/news/mixtral-8x22b/) 39B active disclosures, rounded to their common scale. It agrees with existing Flash priors and remains a weak peer transfer, with **10–150B** scenarios. The [June 17 announcement](https://developers.googleblog.com/en/gemini-2-5-thinking-model-updates/) dates the stable endpoint. The point's requested endpoint is the stable alias.

**Kimi and gpt-oss.** The [original Kimi model card](https://huggingface.co/moonshotai/Kimi-K2-Instruct#2-model-summary) reports 32B active and 1T total. [OpenRouter's original-0711 endpoint page](https://openrouter.ai/moonshotai/kimi-k2) dates availability to July 11, corroborated by the original HF repository's July 11 creation; this is not the September or thinking revision. The [OpenAI gpt-oss release](https://openai.com/index/introducing-gpt-oss/) dates both open models to August 5 and reports 5.1B/3.6B active. The detailed retained model card gives 5.13B/3.61B; the launch's rounded values keep both registry coefficients at the same precision. Quantization does not discount the arithmetic count.

**Other shared coefficients.** The [original Claude analysis](https://unexcitedneurons.substack.com/p/estimating-the-size-of-claude-opus) derives 167–188B for Opus 4.1 at 24 tokens/s under its 4–4.5 TB/s effective-bandwidth FP8 scenario, supporting the shared 180B central. Sonnet's 100B and Gemini Pro's 100B remain coarse shared estimates. Mini 20B transfers the original 10–30B o4-mini estimate identified in the linked registry research. Model-specific assumptions and all scenario endpoints are frozen in `model-inputs.csv` and `config.json`; scenario FLOPs are retained alongside the central values. They are sensitivities, not confidence intervals.

## Points

Input/output numbers below are native per-call means, including optional generated explanation and reasoning within output.

### reas-strawberry-opus41

18 input +138.28 output =156.28 tokens. At 180B active: **5.62608e13 FLOPs**. Correct 100/100; human 4 seconds.

### reas-strawberry-sonnet4

18 input +91.82 output =109.82 tokens. At 100B active: **2.1964e13 FLOPs**. Correct 100/100; human 4 seconds.

### reas-strawberry-gpt5-chat

17 input +37.95 output =54.95 tokens. At 100B active: **1.099e13 FLOPs**. Correct 100/100; human 4 seconds.

### reas-strawberry-gpt5-mini

16 input +157.21 output =173.21 tokens. At 20B active: **6.9284e12 FLOPs**. Correct 100/100; human 4 seconds.

### reas-strawberry-gpt5-nano

16 input +445.12 output =461.12 tokens. At 8B active: **7.37792e12 FLOPs**. Correct 100/100; human 4 seconds.

### reas-strawberry-gemini25-flash

10 input +17.79 output =27.79 tokens. At 40B active: **2.2232e12 FLOPs**. Correct 90/100; human 4 seconds. Both incorrect-count categories remain in the mean.

### reas-strawberry-gemini25-pro

10 input +308.97 output =318.97 tokens. At 100B active: **6.3794e13 FLOPs**. Correct 100/100; human 4 seconds.

### reas-strawberry-kimi-k2

28.34 input +357.73 output =386.07 tokens. At 32B active: **2.470848e13 FLOPs**. Correct 100/100; human 4 seconds.

### reas-strawberry-gpt-oss120b

78.68 input +147.82 output =226.5 tokens. At 5.1B active: **2.3103e12 FLOPs**. Correct 100/100; human 4 seconds.

### reas-strawberry-gpt-oss20b

77.58 input +188.45 output =266.03 tokens. At 3.6B active: **1.915416e12 FLOPs**. Correct 100/100; human 4 seconds.

## Reproduction

Original dataset revision: `a0319935ae3810b66a207266ec67f9f41afe6972`. Original code revision: `9038b39cdb58772e3be0a1327e1314c902a47620`. `agent-work/sources/strawberry/source-manifest.json` records source URLs and hashes, including the original Parquet LFS hash and notebook Git blobs.

Install `pyarrow` and `tiktoken`. The calculator reads the original Parquet, safely parses literal notebook settings, audits all response labels and recomputes the means. It does not execute the notebook or call any model. Use explicit paths and a new output outside the source directory:

```sh
python3 -B research/strawberry/recompute.py --sources agent-work/sources/strawberry --models research/strawberry/model-inputs.csv --config research/strawberry/config.json --output /path/to/new-calculations.json
```

The original question is a related source for the old GPT-4o letter-count lead. These points use different documented 2025 models and new IDs; they do not reconstruct the earlier screenshot's model or workload.
