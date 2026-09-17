# SimpleQA-Verified: original logged executions

The initial leads called this SimpleQA, but each downloaded header identifies **SimpleQA-Verified**, `codelion/SimpleQA-Verified`, 1,000 questions. The first source questions agree with [Google's original verified set](https://huggingface.co/datasets/google/simpleqa-verified). The work is answering one short factual question without tools, not writing a researched report. Human baseline is an experienced fact checker allowed web research without AI.

## Human duration and quality

The three-minute estimate is an assumption informed by inspecting the first 20 original questions and their supporting-source types, not a measured annotation average. Examples include finding a former Icelandic prime minister's airline career, an Australian museum's rebranding year, the court-ordered amount following Stella Obasanjo's death, and a historical Q-ship's false-stern disguise. Most can be answered by locating a named entity, reading a short biography/news item/table, and checking that the date or requested relation is the right one. Some require disambiguation: “MOBA” in the Scott Wilson question means Museum of Bad Art rather than a videogame genre. The naval-history question may require searching a long historical text. Three minutes allows a short query, source inspection and a second check for the ordinary items while averaging some longer searches. The bounds come from the composition of the set rather than a factor on the mean. A plain item—one named-entity lookup, one source read, one confirmation—runs about 90 seconds, and a disambiguation or long-text item like the Q-ship question runs about ten minutes, so a three-minute mean implies roughly one item in six is the long kind. At one in twenty the mean is 115 seconds; at one in three it is 260 seconds. Those are the bounds. It does not include composing the models' often extraneous paragraphs, because only the requested short fact is scored.

[Original SimpleQA paper](https://cdn.openai.com/papers/simpleqa.pdf) and [release's quality verification](https://openai.com/index/introducing-simpleqa/) report 94.4% agreement by a third rater on a 1,000-question sample. This is a different dataset sample and experienced-rater comparison, not observed 95% on Verified. We use approximately 95% as an **assumed fact-checker target**, supported by the availability of verified answer sources. The AI rates (13.9–50.1%) are materially below this target. This is not a matched-quality duration estimated to reproduce hallucinations; both tool and assessment differences are explicit.

## Logged workload

`agent-work/sources/epoch/<point_id>/header.json`, `summaries.json` and other small ZIP members were extracted from the source `.eval` archives using HTTP byte ranges. `agent-work/sources/epoch/legacy-accounting/selection.json` contains the exact public URLs. The historical network extractor is not needed to inspect the retained source members. Each plan is `generate` followed by a SimpleQA grader, with no solving tools or helper. Gemini 2.0 Flash is an **external outcome evaluator** receiving the reference answer after the response; it does not assist task execution and is excluded. The primary-model `model_usage` sums provide the numerator, including all recorded usage.

For DeepSeek and Qwen, `total_tokens == input_tokens + output_tokens`; the reported `reasoning_tokens` are therefore already a subset of output. Adding them again would double-count. GPT-oss supplies input and output only; its plan explicitly requests high reasoning effort. Every primary cache-read count is absent/zero in these three runs. The counts do not include costs of earlier pretraining.

DeepSeek: input 26,664 + output 375,939 = 402,603; reasoning subset 228,233; 1,000 scored completions; 275 correct. GPT-oss: 89,472 + 10,195,706 = 10,285,178; 1,000 completions; 139 correct. Qwen: 31,834 + 1,066,330 = 1,098,164; reasoning subset 651,065; **998 scored completions**, 500 correct. Two Qwen provider-filtered records have no usage/scoring; header `results.completed_samples=998` governs the denominator despite a per-summary completion flag. The input-filtered request is assigned zero; the output-filtered response receives a same-run mean workload estimate. Final compute includes that adjustment, as detailed in the linked failure audit.

Model identities, independent parameter and release sources are in `models.md`. The December 16 DeepSeek API name is resolved to V3.2 from the dated December 1 official API change log, not from the current meaning of that mutable API alias. Replay the current counter arithmetic, including subsequent missing-work corrections, with [the read-only accounting check](reproduction.md).

<!-- generated-point-appendix -->

## lang-epoch-simpleqa-dsv32

Model: DeepSeek-V3.2. Source: https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/MB78rXsEm7srHraZ94mfP8.eval.

Inputs/accounting: `{"correct": 275, "denominator": 1000, "primary": "deepseek/deepseek-reasoner", "usage": {"input_tokens": 26664, "input_tokens_cache_read": 0, "output_tokens": 375939, "reasoning_tokens": 228233, "total_tokens": 402603}}`.

Counted tokens per work unit = 402.603; coefficient = 7.4e+10 FLOPs/token; product = **2.9792622e+13 FLOPs**. Human = 180 seconds. AI correct on 275/1000 scored questions. Human accurate factual lookup target is approximately 95% correct (assumed experienced-rater baseline; original SimpleQA third-rater agreement was 94.4% on a different sample).

## lang-epoch-simpleqa-gptoss120b

Model: gpt-oss-120b. Source: https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/MAVCYoXJFEuBWUsJpSgnLL.eval.

Inputs/accounting: `{"correct": 139, "denominator": 1000, "primary": "together/openai/gpt-oss-120b", "usage": {"input_tokens": 89472, "output_tokens": 10195706, "total_tokens": 10285178}}`.

Counted tokens per work unit = 10285.178; coefficient = 1.02e+10 FLOPs/token; product = **1.049088156e+14 FLOPs**. Human = 180 seconds. AI correct on 139/1000 scored questions. Human accurate factual lookup target is approximately 95% correct (assumed experienced-rater baseline; original SimpleQA third-rater agreement was 94.4% on a different sample).

## lang-epoch-simpleqa-qwen3thinking

Model: Qwen3-235B-A22B-Thinking-2507. Source: https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/S9wG8ps9RJGx49yx4G4ucG.eval.

Inputs/accounting: `{"correct": 500, "denominator": 998, "primary": "alibaba/qwen3-235b-a22b-thinking-2507", "usage": {"input_tokens": 31834, "output_tokens": 1066330, "reasoning_tokens": 651065, "total_tokens": 1098164}}`.

Including recovered or estimated missing work, tokens per completed evaluation = 1101.46729933; × 44000000000 FLOPs/token = **4.84645611704e+13 FLOPs**. [Failure accounting](epoch-native-usage-audit.md#lang-epoch-simpleqa-qwen3thinking). Human = 180 seconds. AI correct on 500/998 scored questions. Human accurate factual lookup target is approximately 95% correct (assumed experienced-rater baseline; original SimpleQA third-rater agreement was 94.4% on a different sample).
