# Epoch older Claude inference observations

Twenty original output-table observations and one native SimpleQA-Verified evaluation retain the reviewed benchmark work units and human recipes. Seven exact Claude model identities are added. All inputs here are text. No vision positions or encoder passes are mixed into the decoder counts.

## Parameter assumptions

Every coefficient is estimated. No cited Anthropic announcement discloses these parameter counts. The central choices are rounded architectural priors; they are not inferred from API prices, performance percentages or response length. Correlated uncertainty across model families remains substantial.

**Claude 2.0, Claude 2.1 and Claude 3 Sonnet: 100B active, 200B FLOPs/token.** We transfer the existing later-Sonnet 100B scale backward to these broad general-purpose Claude models. The original [Epoch Sonnet analysis](https://epoch.ai/gradient-updates/frontier-language-models-have-become-much-smaller) estimates 400B total for Sonnet 3.5. The explicitly transferred quarter-active convention from [Epoch's energy analysis](https://epoch.ai/gradient-updates/how-much-energy-does-chatgpt-use) gives 100B. The newer [model-specific bandwidth analysis](https://unexcitedneurons.substack.com/p/estimating-the-size-of-claude-opus) independently suggests approximately 100B active for Sonnet 4.5 under FP8 and calibrated serving-bandwidth assumptions. Neither establishes the older models' architecture, but together they make a transparent same-family 100B prior reasonable.

We investigated Alan Thompson's original [July 2023 note](https://lifearchitect.substack.com/p/the-memo-17jul2023), which estimates Claude 2 at 130B, and [March 2024 note](https://lifearchitect.substack.com/p/the-memo-special-edition-claude-3), which estimates Sonnet 3 at 70B. Neither provides a reproducible architectural or serving calculation. They are weak corroboration of the order of magnitude, not a reason to manufacture a precise 130B-to-70B change. Adopt 100B for both, with a wide 50–200B-active sensitivity. Anthropic's original [Claude 3 launch](https://www.anthropic.com/news/claude-3-family) says Sonnet is faster than Claude 2; without fixed serving hardware/batching, that supports caution about equality but not a numerical FLOP ratio. The equal central coefficients express unresolved differences, not asserted identical weights or architectures.

**Claude 3.5 Sonnet June: 100B active, 200B FLOPs/token.** This uses the same 400B-total/quarter-active derivation as the already reviewed October snapshot. No independent architecture change between those snapshots is assumed. The 50–200B sensitivity applies.

**Claude 3 Opus: 180B active, 360B FLOPs/token.** Prefer a transfer from the better-supported Opus 4/4.1 active estimate over the unexplained 2T-total guess in Thompson's March note. The [original bandwidth analysis](https://unexcitedneurons.substack.com/p/estimating-the-size-of-claude-opus) calibrates 4–4.5 TB/s on open models and divides by 23/24 tokens per second for Opus 4/4.1, yielding approximately 174–196B/167–188B under FP8. The rounded 180B is explicitly transferred to Opus 3. This is not a measured Opus 3 throughput or an assumption that versions share weights. Anthropic says Opus 3 has similar speed to Claude 2/2.1, offering no clear support for a several-fold active-size jump. We therefore reject 2T × one-quarter = 500B as the central estimate: both the starting size and the activation transfer would be weak. A wide 90–500B-active scenario covers materially different architectures, including that alternative; it is not a confidence interval or hard bound. The newer calibration can fail across hardware, precision, batching, attention and speculative decoding, so transfer uncertainty is genuine.

**Claude 3 and 3.5 Haiku: 20B active, 40B FLOPs/token.** The original Claude 3 model family places Haiku at the smallest end, and the [Haiku launch](https://www.anthropic.com/news/claude-3-haiku) emphasizes fast ingestion/generation. Thompson's March note proposes 20B without explaining a measurement. We retain 20B as a weak size prior, consistent with the separately reviewed small-model scale ([Epoch's o4-mini range is 10–30B](https://epoch.ai/data-insights/ai-capabilities-progress-has-sped-up); source table row `o4-mini-2025-04-16_medium`), rather than treat it as a disclosure or calculate size from latency. This cross-family check is only an order-of-magnitude plausibility check. Transfer to Haiku 3.5 is assumed; higher task accuracy does not establish a larger parameter count. A 10–40B scenario represents factor-two uncertainty. Dense execution is assumed at this scale; a different hosted sparse architecture could change the active count.

## Public availability and identity

Official launch pages establish July 11, 2023 for Claude 2, November 21 for 2.1, March 4, 2024 for Opus/Sonnet 3, March 13 for Haiku 3. The contemporaneous [AWS availability notice](https://aws.amazon.com/about-aws/whats-new/2024/06/anthropic-claude-3-5-sonnet-model-bedrock/) establishes June 20 for Sonnet 3.5; the Anthropic launch page currently displays June 21. The [AWS launch update](https://aws.amazon.com/blogs/aws/upgraded-claude-3-5-sonnet-from-anthropic-available-now-computer-use-public-beta-and-claude-3-5-haiku-coming-soon-in-amazon-bedrock/) explicitly corrects its October announcement: Haiku 3.5 became available November 4. Thus internal suffixes February 29, March 7 and October 22 are not substituted for public release dates. The original Epoch source Identifiers remain preserved.

## Text input reconstruction and native audit

The original Anthropic tokenizer [implementation](https://github.com/anthropics/anthropic-tokenizer-typescript/blob/4d75e64d32fe5cd2b5a24d954242f9fab12e8b4b/index.ts) applies NFKC normalization before tokenization with its published [token data](https://github.com/anthropics/anthropic-tokenizer-typescript/blob/4d75e64d32fe5cd2b5a24d954242f9fab12e8b4b/claude.json). The [provider's README](https://github.com/anthropics/anthropic-tokenizer-typescript/blob/4d75e64d32fe5cd2b5a24d954242f9fab12e8b4b/README.md) says it supports older Claude models but is only a rough approximation for Claude 3 onward. We therefore use it directly for Claude 2/2.1 and explicitly as a same-provider proxy for Claude 3/3.5. The historical wrappers remain assumptions: 12 positions after the full GPQA question/choices/instruction, and 50 after each full Level-5 MATH problem. Exact historical prompts are not claimed. The native SimpleQA row uses logged usage instead of proxy tokenization.

The retained `agent-work/sources/epoch/claude-legacy-input-counts.json` records counts using original NFKC normalization and the pinned tokenizer file; the historical tokenizer script is not a current CSV replay command. GPQA mean input is 270.025252525 tokens across 198 questions; MATH mean is 136.999244713 across 1,324 problems. OTIS uses the recovered 45 question texts with the retained tokenizer or explicit proxy, the recovered short instruction and 12 assumed chat positions; see [the input correction](epoch-otis-input-correction.md). The script-generated counts and original strings are retained in sources. A ±50% input scenario is reported per point, separately from the wider parameter uncertainty.

The full native Haiku 3.5 SimpleQA archive contains 1,000 primary model events, all successful. The audit checks unique event UUIDs, exact event-to-sample usage sums and header reconciliation; no failed or pending call was omitted. External Gemini answer grading is excluded from solving. The source scorer reports 67 correct of 1,000, compared with the unchanged assumed human fact-checker target. All other rows use the matching original output-table means and scores, with no added reasoning budget.

Human assumptions and measured observations remain distinguished in the linked benchmark studies. GPQA means retain other_calculation; MATH's 600-second effort and quality target, OTIS full-paper allocation and SimpleQA lookup estimate remain the accepted assumptions.


## Model: claude-2.0

Active parameters: 1e+11; coefficient 2P = 2e+11 FLOPs/token. [original source 1](https://epoch.ai/gradient-updates/frontier-language-models-have-become-much-smaller); [original source 2](https://epoch.ai/gradient-updates/how-much-energy-does-chatgpt-use); [parameter assumptions](#parameter-assumptions); release 2023-07-11 supported by [release source](https://www.anthropic.com/news/claude-2). Input estimate uses the original older-Claude tokenizer plus assumed wrappers.


## reas-epoch-gpqa-claude2

Work unit and human baseline: [gpqa](gpqa.md). Source row: Identifier `claude-2.0`, Benchmark `GPQA diamond` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.3465909091; classification above versus human target 0.2205387205. Mean output 199.863636364; input 270.025252525 (claude_legacy); total 469.888888889 tokens/question × 200000000000 FLOPs/token = 9.39777777778e+13 FLOPs/question. A ±50% input estimate changes total compute by ±28.7%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-mathl5-claude2

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `claude-2.0`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.1172583082; classification below versus human target 0.9. Mean output 258.773413897; input 136.999244713 (claude_legacy); total 395.77265861 tokens/question × 200000000000 FLOPs/token = 7.91545317221e+13 FLOPs/question. A ±50% input estimate changes total compute by ±17.3%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-otis-claude2

Original Epoch table: Identifier `claude-2.0`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 363.666666667. Input under `claude_legacy` = 189.088888889. Total = 552.755555556 text tokens × 200000000000 FLOPs/token = **1.10551111111e+14 FLOPs**.

Work unit and human baseline: [OTIS](otis.md). AI accuracy 2.5%. Original human contest score frequencies imply 51.5507% under equal weighting of the three papers. Current input reconstruction and tokenizer qualification: [OTIS correction](epoch-otis-input-correction.md#reas-epoch-otis-claude2).

## Model: claude-2.1

Active parameters: 1e+11; coefficient 2P = 2e+11 FLOPs/token. [original source 1](https://epoch.ai/gradient-updates/frontier-language-models-have-become-much-smaller); [original source 2](https://epoch.ai/gradient-updates/how-much-energy-does-chatgpt-use); [parameter assumptions](#parameter-assumptions); release 2023-11-21 supported by [release source](https://www.anthropic.com/news/claude-2-1). Input estimate uses the original older-Claude tokenizer plus assumed wrappers.


## reas-epoch-gpqa-claude21

Work unit and human baseline: [gpqa](gpqa.md). Source row: Identifier `claude-2.1`, Benchmark `GPQA diamond` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.3295454545; classification above versus human target 0.2205387205. Mean output 220.48989899; input 270.025252525 (claude_legacy); total 490.515151515 tokens/question × 200000000000 FLOPs/token = 9.8103030303e+13 FLOPs/question. A ±50% input estimate changes total compute by ±27.5%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-otis-claude21

Original Epoch table: Identifier `claude-2.1`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 366.266666667. Input under `claude_legacy` = 189.088888889. Total = 555.355555556 text tokens × 200000000000 FLOPs/token = **1.11071111111e+14 FLOPs**.

Work unit and human baseline: [OTIS](otis.md). AI accuracy 1.94444%. Original human contest score frequencies imply 51.5507% under equal weighting of the three papers. Current input reconstruction and tokenizer qualification: [OTIS correction](epoch-otis-input-correction.md#reas-epoch-otis-claude21).

## Model: claude-3-haiku-20240307

Active parameters: 2e+10; coefficient 2P = 4e+10 FLOPs/token. [original source 1](https://lifearchitect.substack.com/p/the-memo-special-edition-claude-3); [parameter assumptions](#parameter-assumptions); release 2024-03-13 supported by [release source](https://www.anthropic.com/news/claude-3-haiku). Input estimate uses Anthropic’s older tokenizer as an explicit rough proxy; Claude 3 tokenization differs.


## reas-epoch-gpqa-haiku3

Work unit and human baseline: [gpqa](gpqa.md). Source row: Identifier `claude-3-haiku-20240307`, Benchmark `GPQA diamond` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.3630050505; classification above versus human target 0.2205387205. Mean output 345.752525253; input 270.025252525 (claude_legacy); total 615.777777778 tokens/question × 40000000000 FLOPs/token = 2.46311111111e+13 FLOPs/question. A ±50% input estimate changes total compute by ±21.9%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-mathl5-haiku3

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `claude-3-haiku-20240307`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.1487915408; classification below versus human target 0.9. Mean output 401.019637462; input 136.999244713 (claude_legacy); total 538.018882175 tokens/question × 40000000000 FLOPs/token = 2.1520755287e+13 FLOPs/question. A ±50% input estimate changes total compute by ±12.7%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-otis-haiku3

Original Epoch table: Identifier `claude-3-haiku-20240307`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 566.711111111. Input under `claude_legacy` = 189.088888889. Total = 755.8 text tokens × 40000000000 FLOPs/token = **3.0232e+13 FLOPs**.

Work unit and human baseline: [OTIS](otis.md). AI accuracy 1.80556%. Original human contest score frequencies imply 51.5507% under equal weighting of the three papers. Current input reconstruction and tokenizer qualification: [OTIS correction](epoch-otis-input-correction.md#reas-epoch-otis-haiku3).

## Model: claude-3-5-haiku-20241022

Active parameters: 2e+10; coefficient 2P = 4e+10 FLOPs/token. [original source 1](https://lifearchitect.substack.com/p/the-memo-special-edition-claude-3); [parameter assumptions](#parameter-assumptions); release 2024-11-04 supported by [release source](https://aws.amazon.com/blogs/aws/upgraded-claude-3-5-sonnet-from-anthropic-available-now-computer-use-public-beta-and-claude-3-5-haiku-coming-soon-in-amazon-bedrock/). Input estimate uses Anthropic’s older tokenizer as an explicit rough proxy; Claude 3 tokenization differs.


## reas-epoch-gpqa-haiku35

Work unit and human baseline: [gpqa](gpqa.md). Source row: Identifier `claude-3-5-haiku-20241022`, Benchmark `GPQA diamond` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.3813131313; classification above versus human target 0.2205387205. Mean output 295.934343434; input 270.025252525 (claude_legacy); total 565.95959596 tokens/question × 40000000000 FLOPs/token = 2.26383838384e+13 FLOPs/question. A ±50% input estimate changes total compute by ±23.9%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-mathl5-haiku35

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `claude-3-5-haiku-20241022`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.4635574018; classification below versus human target 0.9. Mean output 427.484138973; input 136.999244713 (claude_legacy); total 564.483383686 tokens/question × 40000000000 FLOPs/token = 2.25793353474e+13 FLOPs/question. A ±50% input estimate changes total compute by ±12.1%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-otis-haiku35

Original Epoch table: Identifier `claude-3-5-haiku-20241022`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 561.044444444. Input under `claude_legacy` = 189.088888889. Total = 750.133333333 text tokens × 40000000000 FLOPs/token = **3.00053333333e+13 FLOPs**.

Work unit and human baseline: [OTIS](otis.md). AI accuracy 4.30556%. Original human contest score frequencies imply 51.5507% under equal weighting of the three papers. Current input reconstruction and tokenizer qualification: [OTIS correction](epoch-otis-input-correction.md#reas-epoch-otis-haiku35).

## Model: claude-3-opus-20240229

Active parameters: 1.8e+11; coefficient 2P = 3.6e+11 FLOPs/token. [original source 1](https://unexcitedneurons.substack.com/p/estimating-the-size-of-claude-opus); [parameter assumptions](#parameter-assumptions); release 2024-03-04 supported by [release source](https://www.anthropic.com/news/claude-3-family). Input estimate uses Anthropic’s older tokenizer as an explicit rough proxy; Claude 3 tokenization differs.


## reas-epoch-gpqa-opus3

Work unit and human baseline: [gpqa](gpqa.md). Source row: Identifier `claude-3-opus-20240229`, Benchmark `GPQA diamond` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.4715909091; classification above versus human target 0.2205387205. Mean output 432.050505051; input 270.025252525 (claude_legacy); total 702.075757576 tokens/question × 360000000000 FLOPs/token = 2.52747272727e+14 FLOPs/question. A ±50% input estimate changes total compute by ±19.2%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-mathl5-opus3

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `claude-3-opus-20240229`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.3748111782; classification below versus human target 0.9. Mean output 493.401057402; input 136.999244713 (claude_legacy); total 630.400302115 tokens/question × 360000000000 FLOPs/token = 2.26944108761e+14 FLOPs/question. A ±50% input estimate changes total compute by ±10.9%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-otis-opus3

Original Epoch table: Identifier `claude-3-opus-20240229`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 581.466666667. Input under `claude_legacy` = 189.088888889. Total = 770.555555556 text tokens × 360000000000 FLOPs/token = **2.774e+14 FLOPs**.

Work unit and human baseline: [OTIS](otis.md). AI accuracy 4.72222%. Original human contest score frequencies imply 51.5507% under equal weighting of the three papers. Current input reconstruction and tokenizer qualification: [OTIS correction](epoch-otis-input-correction.md#reas-epoch-otis-opus3).

## Model: claude-3-sonnet-20240229

Active parameters: 1e+11; coefficient 2P = 2e+11 FLOPs/token. [original source 1](https://epoch.ai/gradient-updates/frontier-language-models-have-become-much-smaller); [original source 2](https://epoch.ai/gradient-updates/how-much-energy-does-chatgpt-use); [parameter assumptions](#parameter-assumptions); release 2024-03-04 supported by [release source](https://www.anthropic.com/news/claude-3-family). Input estimate uses Anthropic’s older tokenizer as an explicit rough proxy; Claude 3 tokenization differs.


## reas-epoch-gpqa-sonnet3

Work unit and human baseline: [gpqa](gpqa.md). Source row: Identifier `claude-3-sonnet-20240229`, Benchmark `GPQA diamond` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.4059343434; classification above versus human target 0.2205387205. Mean output 467.964646465; input 270.025252525 (claude_legacy); total 737.98989899 tokens/question × 200000000000 FLOPs/token = 1.47597979798e+14 FLOPs/question. A ±50% input estimate changes total compute by ±18.3%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-mathl5-sonnet3

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `claude-3-sonnet-20240229`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.1817409366; classification below versus human target 0.9. Mean output 491.717522659; input 136.999244713 (claude_legacy); total 628.716767372 tokens/question × 200000000000 FLOPs/token = 1.25743353474e+14 FLOPs/question. A ±50% input estimate changes total compute by ±10.9%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-otis-sonnet3

Original Epoch table: Identifier `claude-3-sonnet-20240229`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 592.977777778. Input under `claude_legacy` = 189.088888889. Total = 782.066666667 text tokens × 200000000000 FLOPs/token = **1.56413333333e+14 FLOPs**.

Work unit and human baseline: [OTIS](otis.md). AI accuracy 2.5%. Original human contest score frequencies imply 51.5507% under equal weighting of the three papers. Current input reconstruction and tokenizer qualification: [OTIS correction](epoch-otis-input-correction.md#reas-epoch-otis-sonnet3).

## Model: claude-3-5-sonnet-20240620

Active parameters: 1e+11; coefficient 2P = 2e+11 FLOPs/token. [original source 1](https://epoch.ai/gradient-updates/frontier-language-models-have-become-much-smaller); [original source 2](https://epoch.ai/gradient-updates/how-much-energy-does-chatgpt-use); [parameter assumptions](#parameter-assumptions); release 2024-06-20 supported by [release source](https://aws.amazon.com/about-aws/whats-new/2024/06/anthropic-claude-3-5-sonnet-model-bedrock/). Input estimate uses Anthropic’s older tokenizer as an explicit rough proxy; Claude 3 tokenization differs.


## reas-epoch-gpqa-sonnet35-0620

Work unit and human baseline: [gpqa](gpqa.md). Source row: Identifier `claude-3-5-sonnet-20240620`, Benchmark `GPQA diamond` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.5404040404; classification above versus human target 0.2205387205. Mean output 420.545454545; input 270.025252525 (claude_legacy); total 690.570707071 tokens/question × 200000000000 FLOPs/token = 1.38114141414e+14 FLOPs/question. A ±50% input estimate changes total compute by ±19.6%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-mathl5-sonnet35-0620

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `claude-3-5-sonnet-20240620`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.516805136; classification below versus human target 0.9. Mean output 439.615558912; input 136.999244713 (claude_legacy); total 576.614803625 tokens/question × 200000000000 FLOPs/token = 1.15322960725e+14 FLOPs/question. A ±50% input estimate changes total compute by ±11.9%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-otis-sonnet35-0620

Original Epoch table: Identifier `claude-3-5-sonnet-20240620`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 555.555555556. Input under `claude_legacy` = 189.088888889. Total = 744.644444444 text tokens × 200000000000 FLOPs/token = **1.48928888889e+14 FLOPs**.

Work unit and human baseline: [OTIS](otis.md). AI accuracy 6.52778%. Original human contest score frequencies imply 51.5507% under equal weighting of the three papers. Current input reconstruction and tokenizer qualification: [OTIS correction](epoch-otis-input-correction.md#reas-epoch-otis-sonnet35-0620).

## lang-epoch-simpleqa-haiku35

[Original evaluation](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/Ttvi2yQBmZ6L7jV86d9dH6.eval). Full 1,000-sample event audit found exactly one successful primary call per sample, no error/pending calls, no cache traffic. Native input 32,285 + output 66,674 = 98,959; divide by 1,000 gives 98.959 tokens × 4e+10 = 3.95836e+12 FLOPs. Header and successful-event sums match sample totals. Accuracy 67/1,000; below assumed human 95% target. Human recipe: [SimpleQA](simpleqa.md). The complete audit result is retained at `agent-work/sources/epoch/lang-epoch-simpleqa-haiku35/full-event-audit.json`, alongside its original archive.
