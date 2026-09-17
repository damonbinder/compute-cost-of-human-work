# Epoch o-series and hosted QwQ-Plus reasoning observations

Fifteen observations use the original Epoch output-table means and reviewed GPQA Diamond, MATH Level 5 and OTIS human recipes. Six model identities are represented. Inference effort configurations are retained at point level; the two o1 configurations share one December 17 API model record. No model parameter count in this tranche is provider-disclosed.

## Parameter assumptions

**o4-mini: 20B active, 40B FLOPs/token.** [Epoch's original capability-progress analysis](https://epoch.ai/data-insights/ai-capabilities-progress-has-sped-up), data table row `o4-mini-2025-04-16_medium`, states an estimated active size of 10–30B. The midpoint is 20B. That analysis does not supply a direct parameter measurement, and its training-compute ceiling discussion is not independently inverted here. We adopt its explicitly stated size estimate. Reasoning effort changes generated tokens, not the model coefficient, so the estimate applies to the high-effort observations. A 10–30B sensitivity scales these FLOPs by 0.5–1.5.

**o1-mini and o3-mini: 20B active each, 40B FLOPs/token.** The numerical anchor is the o4-mini estimate above, explicitly transferred to the earlier small-reasoning family. [OpenAI's o1-mini launch](https://openai.com/index/openai-o1-mini-advancing-cost-efficient-reasoning/) describes a smaller, STEM-focused model rather than a full broad-knowledge model; [the o3-mini launch](https://openai.com/index/openai-o3-mini/) describes the next small reasoning model in this lineage. These facts support the family comparison, but do not demonstrate equal sizes. With no model-specific count established after searching original technical/release material and external analyses, a shared 20B prior is more defensible than manufacturing architecture changes from price ratios. A wider 10–40B scenario reflects the transfer uncertainty. This is a modeling judgment, not a measured interval or a claim that reasoning performance determines parameter count.

**o1 December 17 API and o1-preview: 50B active each, 100B FLOPs/token.** Retain the reviewed o1-family scale while distinguishing the exact API snapshot from the `o1-metr` source alias. The original numerical anchor is [Epoch's GPT-4o energy analysis](https://epoch.ai/gradient-updates/how-much-energy-does-chatgpt-use): central 200B total times assumed quarter activation gives 50B. Its transfer to the o1 lineage is explicit, without assuming that OpenAI disclosed matching architectures. The public [December API announcement](https://openai.com/index/o1-and-new-tools-for-developers/) identifies `o1-2024-12-17` as newly post-trained relative to the earlier ChatGPT release; the date therefore is December 17, not December 5. [September's preview release](https://openai.com/index/introducing-openai-o1-preview/) supports September 12 for o1-preview. Sensitivity 25–100B directly scales compute by one half to twice.

**Hosted QwQ-Plus: assumed 32B active, 64B FLOPs/token.** The task lead's wording is misleading: the original output table identifies `qwq-plus`, not the open `qwq-32b` endpoint. [Current original Alibaba documentation](https://www.alibabacloud.com/help/en/model-studio/qwq-plus) calls Plus an enhanced QwQ model based on Qwen2.5, without disclosing size. [Qwen's original open-model announcement](https://qwenlm.github.io/blog/qwq-32b/) reports 32B parameters and shows a distinct `qwq-32b` API name. Crucially, [Alibaba Lingma's March 6 release account](https://www.cnblogs.com/tongyilingma/p/18755931) introduces the 32B reasoning release and explicitly tells users to select QwQ-plus in Lingma. This supports a close model-family connection, but not exact equivalence of the hosted enhanced weights. We therefore use 32B as an **estimated family transfer**, with a 16–72B-active sensitivity (0.5–2.25 times compute), rather than incorrectly marking it reported. The scenario is not a hard bound; the hosted architecture may differ.

The March 6 QwQ-Plus date records its documented public availability in Lingma. Epoch's April 8 output-table date is not independently established as a new public model release. The non-versioned hosted alias does not identify which later checkpoint generated the evaluation. We preserve the actual source Identifier and disclose that limitation; we do not relabel this observation as open QwQ-32B.

## Workload, configuration and tokenization

[Epoch's original output-length methodology](https://epoch.ai/data-insights/output-length) includes thinking tokens in output. The reported output means are used once, with no extra reasoning budget. Full source Identifiers preserve high/medium settings. For o1-mini, `_high` is retained as the source's configuration label rather than evidence that its public API exposed a user-adjustable effort control. o1-preview has no such suffix. All official release sources establish public availability rather than inferring it from snapshot names.

GPQA input uses the original 198 question/choice strings and instruction prefix plus 12 assumed wrapper positions. MATH uses all 1,324 original Level-5 problem strings plus 50 assumed wrapper positions. OTIS uses the recovered 45 question texts with the retained tokenizer or explicit proxy, the recovered short instruction and 12 assumed chat positions; see [the input correction](epoch-otis-input-correction.md). OpenAI uses the [official tiktoken o200k_base mapping](https://github.com/openai/tiktoken/blob/main/tiktoken/model.py). QwQ-Plus uses the open QwQ-32B tokenizer as an explicit same-family proxy, not a reported hosted tokenizer identity. Its immutable original file is [here](https://huggingface.co/Qwen/QwQ-32B/resolve/976055f8c83f394f35dbd3ab09a285a984907bd0/tokenizer.json). Each row's ±50% input scenario is reported separately from parameter uncertainty. The hosted QwQ coefficient and input-proxy uncertainties are distinct assumptions.

Human timings, populations, task differences and performance targets retain the independently reviewed benchmark recipes. Direction labels describe the reported model performance relative to those targets; no parity-compute claim is introduced. The MATH human 90% target and OTIS fixed effort allocation remain assumptions, while GPQA human timings are averaged original observations.


## Model: o1-2024-12-17

Active parameters: 5e+10; coefficient 2P = 1e+11 FLOPs/token. [original source 1](https://epoch.ai/gradient-updates/how-much-energy-does-chatgpt-use); [parameter assumptions](#parameter-assumptions); release 2024-12-17 supported by [release source](https://openai.com/index/o1-and-new-tools-for-developers/). Input estimate uses the official o200k_base tokenizer mapping plus assumed wrappers.


## reas-epoch-mathl5-o1high

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `o1-2024-12-17_high`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.9471299094; classification match versus human target 0.9. Mean output 4133.01283988; input 135.910120846 (o200k); total 4268.92296073 tokens/question × 100000000000 FLOPs/token = 4.26892296073e+14 FLOPs/question. A ±50% input estimate changes total compute by ±1.59%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## Model: o1-2024-12-17

Active parameters: 5e+10; coefficient 2P = 1e+11 FLOPs/token. [original source 1](https://epoch.ai/gradient-updates/how-much-energy-does-chatgpt-use); [parameter assumptions](#parameter-assumptions); release 2024-12-17 supported by [release source](https://openai.com/index/o1-and-new-tools-for-developers/). Input estimate uses the official o200k_base tokenizer mapping plus assumed wrappers.


## reas-epoch-otis-o1med

Original Epoch table: Identifier `o1-2024-12-17_medium`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 10844.8666667. Input under `o200k` = 186.6. Total = 11031.4666667 text tokens × 100000000000 FLOPs/token = **1.10314666667e+15 FLOPs**.

Work unit and human baseline: [OTIS](otis.md). AI accuracy 73.3333%. Original human contest score frequencies imply 51.5507% under equal weighting of the three papers. Current input reconstruction and tokenizer qualification: [OTIS correction](epoch-otis-input-correction.md#reas-epoch-otis-o1med).

## Model: o1-preview-2024-09-12

Active parameters: 5e+10; coefficient 2P = 1e+11 FLOPs/token. [original source 1](https://epoch.ai/gradient-updates/how-much-energy-does-chatgpt-use); [parameter assumptions](#parameter-assumptions); release 2024-09-12 supported by [release source](https://openai.com/index/introducing-openai-o1-preview/). Input estimate uses the official o200k_base tokenizer mapping plus assumed wrappers.


## reas-epoch-gpqa-o1prev

Work unit and human baseline: [gpqa](gpqa.md). Source row: Identifier `o1-preview-2024-09-12`, Benchmark `GPQA diamond` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.5031565657; classification above versus human target 0.2205387205. Mean output 2990.07070707; input 265.626262626 (o200k); total 3255.6969697 tokens/question × 100000000000 FLOPs/token = 3.2556969697e+14 FLOPs/question. A ±50% input estimate changes total compute by ±4.08%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-mathl5-o1prev

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `o1-preview-2024-09-12`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.8164652568; classification below versus human target 0.9. Mean output 3639.79380665; input 135.910120846 (o200k); total 3775.70392749 tokens/question × 100000000000 FLOPs/token = 3.77570392749e+14 FLOPs/question. A ±50% input estimate changes total compute by ±1.8%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-otis-o1prev

Original Epoch table: Identifier `o1-preview-2024-09-12`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 8307.64444444. Input under `o200k` = 186.6. Total = 8494.24444444 text tokens × 100000000000 FLOPs/token = **8.49424444444e+14 FLOPs**.

Work unit and human baseline: [OTIS](otis.md). AI accuracy 31.1111%. Original human contest score frequencies imply 51.5507% under equal weighting of the three papers. Current input reconstruction and tokenizer qualification: [OTIS correction](epoch-otis-input-correction.md#reas-epoch-otis-o1prev).

## Model: o1-mini-2024-09-12

Active parameters: 2e+10; coefficient 2P = 4e+10 FLOPs/token. [original source 1](https://epoch.ai/data-insights/ai-capabilities-progress-has-sped-up); [parameter assumptions](#parameter-assumptions); release 2024-09-12 supported by [release source](https://openai.com/index/openai-o1-mini-advancing-cost-efficient-reasoning/). Input estimate uses the official o200k_base tokenizer mapping plus assumed wrappers.


## reas-epoch-gpqa-o1mini

Work unit and human baseline: [gpqa](gpqa.md). Source row: Identifier `o1-mini-2024-09-12_high`, Benchmark `GPQA diamond` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.6237373737; classification above versus human target 0.2205387205. Mean output 1856.86868687; input 265.626262626 (o200k); total 2122.49494949 tokens/question × 40000000000 FLOPs/token = 8.48997979798e+13 FLOPs/question. A ±50% input estimate changes total compute by ±6.26%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-mathl5-o1mini

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `o1-mini-2024-09-12_high`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.891805136; classification match versus human target 0.9. Mean output 1851.54003021; input 135.910120846 (o200k); total 1987.45015106 tokens/question × 40000000000 FLOPs/token = 7.94980060423e+13 FLOPs/question. A ±50% input estimate changes total compute by ±3.42%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-otis-o1mini

Original Epoch table: Identifier `o1-mini-2024-09-12_high`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 8013.35555556. Input under `o200k` = 186.6. Total = 8199.95555556 text tokens × 40000000000 FLOPs/token = **3.27998222222e+14 FLOPs**.

Work unit and human baseline: [OTIS](otis.md). AI accuracy 46.9444%. Original human contest score frequencies imply 51.5507% under equal weighting of the three papers. Current input reconstruction and tokenizer qualification: [OTIS correction](epoch-otis-input-correction.md#reas-epoch-otis-o1mini).

## Model: o3-mini-2025-01-31

Active parameters: 2e+10; coefficient 2P = 4e+10 FLOPs/token. [original source 1](https://epoch.ai/data-insights/ai-capabilities-progress-has-sped-up); [parameter assumptions](#parameter-assumptions); release 2025-01-31 supported by [release source](https://openai.com/index/openai-o3-mini/). Input estimate uses the official o200k_base tokenizer mapping plus assumed wrappers.


## reas-epoch-gpqa-o3mini

Work unit and human baseline: [gpqa](gpqa.md). Source row: Identifier `o3-mini-2025-01-31_high`, Benchmark `GPQA diamond` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.7702020202; classification above versus human target 0.2205387205. Mean output 7717.71717172; input 265.626262626 (o200k); total 7983.34343434 tokens/question × 40000000000 FLOPs/token = 3.19333737374e+14 FLOPs/question. A ±50% input estimate changes total compute by ±1.66%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-mathl5-o3mini

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `o3-mini-2025-01-31_high`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.9648791541; classification above versus human target 0.9. Mean output 2955.49848943; input 135.910120846 (o200k); total 3091.40861027 tokens/question × 40000000000 FLOPs/token = 1.23656344411e+14 FLOPs/question. A ±50% input estimate changes total compute by ±2.2%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-otis-o3mini

Original Epoch table: Identifier `o3-mini-2025-01-31_high`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 12818.8. Input under `o200k` = 186.6. Total = 13005.4 text tokens × 40000000000 FLOPs/token = **5.20216e+14 FLOPs**.

Work unit and human baseline: [OTIS](otis.md). AI accuracy 76.9444%. Original human contest score frequencies imply 51.5507% under equal weighting of the three papers. Current input reconstruction and tokenizer qualification: [OTIS correction](epoch-otis-input-correction.md#reas-epoch-otis-o3mini).

## Model: o4-mini-2025-04-16

Active parameters: 2e+10; coefficient 2P = 4e+10 FLOPs/token. [original source 1](https://epoch.ai/data-insights/ai-capabilities-progress-has-sped-up); [parameter assumptions](#parameter-assumptions); release 2025-04-16 supported by [release source](https://openai.com/index/introducing-o3-and-o4-mini/). Input estimate uses the official o200k_base tokenizer mapping plus assumed wrappers.


## reas-epoch-gpqa-o4mini

Work unit and human baseline: [gpqa](gpqa.md). Source row: Identifier `o4-mini-2025-04-16_high`, Benchmark `GPQA diamond` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.7960858586; classification above versus human target 0.2205387205. Mean output 7855.01010101; input 265.626262626 (o200k); total 8120.63636364 tokens/question × 40000000000 FLOPs/token = 3.24825454545e+14 FLOPs/question. A ±50% input estimate changes total compute by ±1.64%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-mathl5-o4mini

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `o4-mini-2025-04-16_high`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.9782854985; classification above versus human target 0.9. Mean output 3281.36933535; input 135.910120846 (o200k); total 3417.27945619 tokens/question × 40000000000 FLOPs/token = 1.36691178248e+14 FLOPs/question. A ±50% input estimate changes total compute by ±1.99%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-otis-o4mini

Original Epoch table: Identifier `o4-mini-2025-04-16_high`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 14084.2. Input under `o200k` = 186.6. Total = 14270.8 text tokens × 40000000000 FLOPs/token = **5.70832e+14 FLOPs**.

Work unit and human baseline: [OTIS](otis.md). AI accuracy 81.6667%. Original human contest score frequencies imply 51.5507% under equal weighting of the three papers. Current input reconstruction and tokenizer qualification: [OTIS correction](epoch-otis-input-correction.md#reas-epoch-otis-o4mini).

## Model: qwq-plus

Active parameters: 3.2e+10; coefficient 2P = 6.4e+10 FLOPs/token. [original source 1](https://qwenlm.github.io/blog/qwq-32b/); [original source 2](https://www.alibabacloud.com/help/en/model-studio/qwq-plus); [parameter assumptions](#parameter-assumptions); release 2025-03-06 supported by [release source](https://www.cnblogs.com/tongyilingma/p/18755931). Hosted QwQ-Plus uses an assumed 32B family coefficient and QwQ-32B tokenizer proxy; exact architecture and historical alias revision are undisclosed.


## reas-epoch-gpqa-qwq32b

Work unit and human baseline: [gpqa](gpqa.md). Source row: Identifier `qwq-plus`, Benchmark `GPQA diamond` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.654040404; classification above versus human target 0.2205387205. Mean output 8802.37373737; input 273.808080808 (qwq32); total 9076.18181818 tokens/question × 64000000000 FLOPs/token = 5.80875636364e+14 FLOPs/question. A ±50% input estimate changes total compute by ±1.51%; no claim this is a confidence interval. The model coefficient and its sources appear above.
