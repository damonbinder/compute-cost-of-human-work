# Freelance-writer news summaries

## writing-news-summary-textdavinci002

One supplied news article summarized into a short newsletter paragraph. The retained set has 76 distinct article/model-output pairs, averaging 730 article words and 46 summary words by whitespace splitting.

## Original evidence

[Zhang et al. (2023)](https://arxiv.org/abs/2301.13848) compared InstructGPT summaries with work by experienced freelance writers. Section 4 requests roughly 50-word human summaries; the model receives a 25-word instruction to obtain similar output lengths. Temperature is 0.3. The authors estimate 12–15 minutes per summary from a pilot.

The [released repository](https://github.com/Tiiiger/benchmark_llm_summarization/tree/4e87890ed070c7db3dd5c1125adb5bde0ccd2eb1) supplies articles, summaries and ratings. We use `pairwise_evaluation_results.json`, not the earlier Likert experiment with different prompts. Its 599 ratings concern 112 distinct writer/article pairs and 76 distinct model outputs. Each article ID has exactly one article string and one model summary. Counting every rating as another generation would duplicate compute. There are no duplicate evaluator/article/writer-summary triples. We retain the actual released records rather than forcing the paper's rounded study counts.

Overall preferences: 239 judgments favor the model, 243 favor the writer and 117 are ties. These support **match**. Informativeness preferences are 250/217/132 respectively. These are ratings, not independent human timing observations. The comparison uses the actual paired outputs, rather than the original benchmark's incidental reference summaries.

## Human time

Use **810 seconds**, the midpoint of the authors' 12–15-minute estimate. Inspecting five articles across the length distribution confirmed ordinary news summarization, with selection and rewriting of relevant facts. The source's estimate is adequate for this task; no additional generic writing-rate model is needed.

The paper does not release pilot durations or identify a timing sample. Therefore this is `assumed`, `estimated`, `point_estimate`, with human attempts and subset `not_applicable`. Neither the six evaluators nor the 112 rated writer summaries supplies a timing count. The reported 720–900-second range is an estimate range, not a confidence interval. Article difficulty and individual pace vary beyond it.

## Model

The endpoint is **text-davinci-002**, released on **2022-03-15** in the [official announcement](https://community.openai.com/t/introducing-insert-and-edits-capabilities/15993/1). It is distinct from the later `davinci-002`. The study assigns 175 billion parameters, explicitly inferred from the API naming scheme. We retain this estimate, giving 350 billion FLOPs per token; it is not a disclosed architecture.

## Compute

The retained texts are retokenized with the official `p50k_base` vocabulary. We reconstruct the paper's template as:

```text
Article: {article}
Summarize the article in 25 words.
Summary:
```

Exact whitespace and native usage counters are unavailable. Add two assumed output positions for an omitted initial newline and stop token. Count each article's full input and one retained output, then average the 76 costs. Mean input is 1,001.0921 tokens; visible output is 56.5; total is **1,059.5921 tokens**. At the shared coefficient, compute is **370,857,236,842,105.25 FLOPs**. The maximum reconstructed input is 2,343 tokens, so the stated inputs do not force context truncation.

This is `params_tokens`, `derived_assumed_inputs`, `mean`, `all`, with 76 AI attempts. It describes the retained generations, not all requests made during the study. Source records do not retain retry histories. Independent full-prefix processing is assumed; the coefficient omits attention, which `compute_flops` carries separately (`research/attention-correction.md`). Removing the two overhead positions gives 3.70157e14 FLOPs; adding 32 further prompt positions gives 3.82057e14. The inferred model size is the larger uncertainty: a different active-parameter estimate rescales compute proportionally.

## Reproduction

Python 3 and `tiktoken` are required. No model inference or network access occurs. The script verifies joins, retokenizes the texts and recalculates costs and preferences. Use a new output path:

```bash
python3 research/freelance-news-summaries/recompute.py \
  --sources agent-work/sources/freelance-news-summaries \
  --models models.csv --output /tmp/freelance-summary-replay.json
```

`agent-work/sources/freelance-news-summaries/manifest.json` records source URLs and hashes. `calculations.json` retains per-article inputs and results. Original strings are used without escape or whitespace normalization.
