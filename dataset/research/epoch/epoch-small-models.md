# Epoch: older OpenAI models, Mistral and Gemini Flash-8B

This collection adds 16 observations from [Epoch's output-length table](https://epoch.ai/data-insights/output-length): five GPQA Diamond, seven MATH Level 5 and four OTIS observations. The source CSV supplies each model identifier, mean output length and accuracy. Input lengths and undisclosed model sizes are estimates. The human benchmarks retain the reviewed definitions in [GPQA](gpqa.md), [MATH Level 5](mathl5.md) and [OTIS](otis.md).

The work unit is one answered benchmark question, with reasoning included in the answer-generation workload. We estimate one generation per question from the table's reported output mean. This table does not expose call histories, retries or provider-side processing; it is not a native-counter audit. No extra hidden reasoning is added to these non-reasoning configurations. Scoring the completed answers is part of the benchmark assessment, outside the task being compared with human answer production.

## Parameter assumptions

**GPT-3.5 Turbo: 7B active, 14B FLOPs/token.** [Finlayson et al., section 4](https://arxiv.org/html/2403.09539v2#S4) tested **0125**, accessed February 1–19, 2024 (footnote 3). Their output matrix's rank break lies around 4,600–4,650; they favor a hidden width of 4,096, with 4,608 another possibility. They infer about 7B parameters by comparison with ordinary dense Transformers of that width and explicitly identify MoE as an exception. We adopt that conditional estimate, not a measured parameter count. It is more directly tied to this model than a price-based estimate or a rumor. We transfer it to 1106 because evidence for a size change between these adjacent snapshots is absent; the experiment did not test 1106. A 7–28B active scenario covers the dense estimate through substantially deeper or multi-expert alternatives. This is a sensitivity scenario, not a statistical interval, and larger deviations remain possible.

**GPT-4.1 mini / nano: 24B / 8B active, 48B / 16B FLOPs/token.** [Chris Bowdon's original account](https://cbowdon.github.io/posts/gpt-params/index.html), final paragraph, describes his NLP-task comparison with Mistral Small 24B and Ministral 8B, respectively. The underlying tasks and run data are not published there. We use those named architectures as weak size priors. The donor counts are supported by the original [Mistral Small 3](https://mistral.ai/news/mistral-small-3/) and [Ministraux](https://mistral.ai/news/ministraux/) releases. This is a cross-model transfer, not a measurement or a calibrated architecture estimate. His separate score-to-parameter regression is unsuitable for our purpose: it mixes total and active counts and assigns different sizes to one model at different reasoning settings. We do not use its 27B/7B predictions. Similar NLP performance can arise from different training, routing and parameter counts. Scenarios are 8–48B for mini and 3–24B for nano. The two weak priors should not support fine comparisons between providers.

**GPT-4o mini: 8B active, 16B FLOPs/token.** OpenAI's [original interview](https://techcrunch.com/2024/07/18/openai-unveils-gpt-4o-mini-a-small-ai-model-powering-chatgpt/) places it in the small-model tier of Llama 3 8B, Haiku and Flash. We use the disclosed-size comparator, Llama 3 8B, as a weak central prior. This does not establish equal model sizes; Haiku and Flash do not provide independent numerical anchors here. A 4–32B active scenario makes the weakness visible. The [OpenAI release](https://openai.com/index/gpt-4o-mini-advancing-cost-efficient-intelligence/) establishes the small-model positioning and shared GPT-4o tokenizer, but discloses no architecture count.

**Mistral Large 2402: 123B active, 246B FLOPs/token.** The original [July successor announcement](https://mistral.ai/news/mistral-large-2407/) reports 123B parameters. Its [original model repository](https://huggingface.co/mistralai/Mistral-Large-Instruct-2407) supplies the dense architecture. We use that same-family size for the undisclosed February model, with 60–250B scenarios. The release is explicitly a successor, so equal size is an assumption; this source does not report the February count. We prefer the identified family architecture to an uncited round-number guess.

**Open Mistral 7B alias: 7.3B active, 14.6B FLOPs/token.** The [original model release](https://mistral.ai/news/announcing-mistral-7b/) reports a 7.3B dense model. Epoch identifies `open-mistral-7b`, not a particular checkpoint. [Au Large](https://mistral.ai/news/mistral-large/) identifies the API alias, but does not settle the revision served during Epoch's run. We estimate the alias using this rounded family count; 7–7.5B covers small embedding/vocabulary differences among the 7B variants, not an unidentified larger architecture. The model record remains separate from an exact v0.3 record and its release date is blank.

**Gemini 1.5 Flash-8B-001: 8B active, 16B FLOPs/token.** The [Google technical report](https://storage.googleapis.com/deepmind-media/gemini/gemini_v1_5_report.pdf), section 8 (printed page 45), describes Flash-8B as retaining Flash's core architecture; model card table 45 (page 105) identifies Flash as dense. We use the nominal 8B count as a rounded text coefficient. That requires a small assumption about the allocation of multimodal components, so the active count is marked estimated. A 6–8B text-active scenario illustrates possible exclusion of visual/audio parameters. It is not a provider-reported component breakdown.

All scenarios scale compute directly at fixed token workload. None is a confidence bound. Shared coefficients omit the context-dependent attention term under the dataset's standard 2P convention; `compute_flops` carries it separately (`research/attention-correction.md`).

## Release identities

| Source identifier | Public availability used | Evidence |
|---|---|---|
| `gpt-3.5-turbo-0125` | 2024-02-01 | [OpenAI API changelog](https://developers.openai.com/api/docs/changelog), February 1 entry. The [January 25 announcement](https://openai.com/index/new-embedding-models-and-api-updates/) says the model was coming the following week; the snapshot suffix is not its public release date. |
| `gpt-3.5-turbo-1106` | 2023-11-06 | [DevDay release](https://openai.com/index/new-models-and-developer-products-announced-at-devday/), “Updated GPT-3.5 Turbo,” names the accessible endpoint. |
| `gpt-4.1-mini-2025-04-14`, `gpt-4.1-nano-2025-04-14` | 2025-04-14 | [OpenAI launch](https://openai.com/index/gpt-4-1/) announces all three GPT-4.1 models in the API that day. |
| `gpt-4o-mini-2024-07-18` | 2024-07-18 | [OpenAI release](https://openai.com/index/gpt-4o-mini-advancing-cost-efficient-intelligence/), API availability on release day. |
| `mistral-large-2402` | 2024-02-26 | [Au Large](https://mistral.ai/news/mistral-large/) names this new endpoint and says it is available. |
| `open-mistral-7b` | Blank | The evaluated API alias's checkpoint is unresolved; the first family release does not date that checkpoint. |
| `gemini-1.5-flash-8b-001` | 2024-10-03 | [Gemini API changelog](https://ai.google.dev/gemini-api/docs/changelog), October 3, 2024 entry explicitly names the stable 001 release; earlier experimental endpoints are different identities. |

## Input reconstruction

GPQA uses all 198 original Diamond questions and four choices, with the [Epoch researcher's multiple-choice instruction](https://gist.github.com/tadamcz/a61515465e34a3c66f3a78673502bc3f), plus 12 assumed chat-wrapper positions. Choice order is fixed only for this length estimate. MATH uses all 1,324 original test statements labelled Level 5, including any Asymptote code, plus 50 assumed instruction/chat positions. The exact historical wrappers are not recovered. OTIS uses the recovered 45 question texts with the retained tokenizer or explicit proxy, the recovered short instruction and 12 assumed chat positions; see [the input correction](epoch-otis-input-correction.md).

GPT-3.5 uses `cl100k_base`; GPT-4.1 and GPT-4o mini use `o200k_base`, following the [official tiktoken mapping, version 0.14.0](https://github.com/openai/tiktoken/blob/0.14.0/tiktoken/model.py). Both original BPE files and the encoding definition are retained and hash-checked. The counts can be reconstructed offline from those files.

The Mistral estimates use the [v0.3 tokenizer at commit c170c708c41dac9275d15a8fff4eca08d52bab71](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3/resolve/c170c708c41dac9275d15a8fff4eca08d52bab71/tokenizer.json) as an explicit family proxy, not an assertion about the hosted 2402 or 7B alias tokenizer. Provenance is retained in `agent-work/sources/epoch/mistral-tokenizer-provenance.json`.

For the Gemini GPQA point, no exact historical tokenizer is available here. We estimate the input by averaging the counts from the two OpenAI tokenizers and Mistral v0.3 on the identical full prompts. This removes an arbitrary choice of one unrelated vocabulary; it is still a cross-family proxy. The three individual means and per-question counts are retained. Their spread is only a check on ordinary subword segmentation, not proof that the Gemini count lies within it. Each point below reports a ±50% input scenario, which changes total compute much less when output dominates.

`agent-work/sources/epoch/small-models/provenance.json` records retained original releases, paper and tokenizer files. `expansion-13/calculations.json` retains the original selected source rows and each input/output/product. `expansion-13/input-counts.json` holds the per-question counts, source hashes and library versions. `expand_small_models.py` regenerates the candidate without inference calls or production writes.

## Human and performance definitions

The reviewed [GPQA baseline](gpqa.md) is the second expert validator: 198 recorded in-domain PhD validations of the revised question, mean active time 1,560.909090909091 seconds and 161/198 correct (81.31%), against 25% four-choice guessing. Diamond admits a question only when the first expert answered correctly, so 81.31% is biased upward; unselected expert accuracy on the extended set is 64.8%. The expert also writes an explanation and post-answer feedback, which the AI does not. The `below` floor is 53.16% and `far_above` is unreachable here.

The [MATH recipe](mathl5.md) assumes 600 seconds of mean effort for an IMO-gold-level solver and a 90% quality target on Level 5. Neither quantity is an observed Level-5 human aggregate. The [OTIS recipe](otis.md) assumes the full 10,800-second paper allowance is used and divides by 15. Its performance comparison comes from the original score-frequency tables, equally weighting the three papers: 51.5507246%. Performance samples do not become timing sample counts.

Scores within five percentage points of the relevant human result/target are classified as a broad match, retaining the established collection convention. Only GPT-4.1 mini on MATH meets that condition in this tranche. The raw AI score and human result/target remain in `performance_evidence`; the label is not a claim of statistical equivalence.


## Reconstructed input means

| Tokenizer or proxy | GPQA input | MATH input | OTIS input |
|---|---:|---:|---:|
| cl100k_base | 269.813131 | 135.992447 | 200 assumed |
| o200k_base | 265.626263 | 135.910121 | 200 assumed |
| mistral3 | 302.10101 | 143.941843 | 200 assumed |
| three_tokenizer_mean | 279.180135 | 138.614804 | 200 assumed |

## reas-epoch-mathl5-gpt35-0125

Source: [Epoch output table](https://epoch.ai/data-insights/output-length), Identifier `gpt-3.5-turbo-0125`, Benchmark `MATH level 5`. Original AI score = 0.116314199396; human result/target = 0.9; comparison = below. Human work and timing: [mathl5](mathl5.md).

Estimated input 135.99244713 + reported mean output 301.129154079 = 437.121601208 tokens per question. Multiply by 14000000000 FLOPs/token = **6.11970241692e+12 FLOPs per question**.

Changing only input by ±50% changes compute by ±15.6%. The model's 7–28B active-parameter scenario gives 6.1197e+12–2.44788e+13 FLOPs at the central token workload. These are sensitivity calculations, not confidence bounds.


## reas-epoch-mathl5-gpt35-1106

Source: [Epoch output table](https://epoch.ai/data-insights/output-length), Identifier `gpt-3.5-turbo-1106`, Benchmark `MATH level 5`. Original AI score = 0.158893504532; human result/target = 0.9; comparison = below. Human work and timing: [mathl5](mathl5.md).

Estimated input 135.99244713 + reported mean output 325.701661631 = 461.694108761 tokens per question. Multiply by 14000000000 FLOPs/token = **6.46371752266e+12 FLOPs per question**.

Changing only input by ±50% changes compute by ±14.7%. The model's 7–28B active-parameter scenario gives 6.46372e+12–2.58549e+13 FLOPs at the central token workload. These are sensitivity calculations, not confidence bounds.


## reas-epoch-gpqa-gpt41mini

Source: [Epoch output table](https://epoch.ai/data-insights/output-length), Identifier `gpt-4.1-mini-2025-04-14`, Benchmark `GPQA diamond`. Original AI score = 0.65845959596; human result/target = 0.220538720539; comparison = above. Human work and timing: [gpqa](gpqa.md).

Estimated input 265.626262626 + reported mean output 1002.67171717 = 1268.2979798 tokens per question. Multiply by 48000000000 FLOPs/token = **6.08783030303e+13 FLOPs per question**.

Changing only input by ±50% changes compute by ±10.5%. The model's 8–48B active-parameter scenario gives 2.02928e+13–1.21757e+14 FLOPs at the central token workload. These are sensitivity calculations, not confidence bounds.


## reas-epoch-mathl5-gpt41mini

Source: [Epoch output table](https://epoch.ai/data-insights/output-length), Identifier `gpt-4.1-mini-2025-04-14`, Benchmark `MATH level 5`. Original AI score = 0.872922960725; human result/target = 0.9; comparison = match. Human work and timing: [mathl5](mathl5.md).

Estimated input 135.910120846 + reported mean output 1572.94033233 = 1708.85045317 tokens per question. Multiply by 48000000000 FLOPs/token = **8.20248217523e+13 FLOPs per question**.

Changing only input by ±50% changes compute by ±3.98%. The model's 8–48B active-parameter scenario gives 2.73416e+13–1.6405e+14 FLOPs at the central token workload. These are sensitivity calculations, not confidence bounds.


## reas-epoch-otis-gpt41mini

Original Epoch table: Identifier `gpt-4.1-mini-2025-04-14`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 5239.13333333. Input under `o200k` = 186.6. Total = 5425.73333333 text tokens × 48000000000 FLOPs/token = **2.604352e+14 FLOPs**.

Work unit and human baseline: [OTIS](otis.md). AI accuracy 44.7222%. Original human contest score frequencies imply 51.5507% under equal weighting of the three papers. Current input reconstruction and tokenizer qualification: [OTIS correction](epoch-otis-input-correction.md#reas-epoch-otis-gpt41mini).

## reas-epoch-gpqa-gpt41nano

Source: [Epoch output table](https://epoch.ai/data-insights/output-length), Identifier `gpt-4.1-nano-2025-04-14`, Benchmark `GPQA diamond`. Original AI score = 0.489267676768; human result/target = 0.220538720539; comparison = above. Human work and timing: [gpqa](gpqa.md).

Estimated input 265.626262626 + reported mean output 790.873737374 = 1056.5 tokens per question. Multiply by 16000000000 FLOPs/token = **1.6904e+13 FLOPs per question**.

Changing only input by ±50% changes compute by ±12.6%. The model's 3–24B active-parameter scenario gives 6.339e+12–5.0712e+13 FLOPs at the central token workload. These are sensitivity calculations, not confidence bounds.


## reas-epoch-mathl5-gpt41nano

Source: [Epoch output table](https://epoch.ai/data-insights/output-length), Identifier `gpt-4.1-nano-2025-04-14`, Benchmark `MATH level 5`. Original AI score = 0.69996223565; human result/target = 0.9; comparison = below. Human work and timing: [mathl5](mathl5.md).

Estimated input 135.910120846 + reported mean output 1582.87311178 = 1718.78323263 tokens per question. Multiply by 16000000000 FLOPs/token = **2.75005317221e+13 FLOPs per question**.

Changing only input by ±50% changes compute by ±3.95%. The model's 3–24B active-parameter scenario gives 1.03127e+13–8.25016e+13 FLOPs at the central token workload. These are sensitivity calculations, not confidence bounds.


## reas-epoch-otis-gpt41nano

Original Epoch table: Identifier `gpt-4.1-nano-2025-04-14`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 3399.26666667. Input under `o200k` = 186.6. Total = 3585.86666667 text tokens × 16000000000 FLOPs/token = **5.73738666667e+13 FLOPs**.

Work unit and human baseline: [OTIS](otis.md). AI accuracy 28.8889%. Original human contest score frequencies imply 51.5507% under equal weighting of the three papers. Current input reconstruction and tokenizer qualification: [OTIS correction](epoch-otis-input-correction.md#reas-epoch-otis-gpt41nano).

## reas-epoch-gpqa-gpt4omini

Source: [Epoch output table](https://epoch.ai/data-insights/output-length), Identifier `gpt-4o-mini-2024-07-18`, Benchmark `GPQA diamond`. Original AI score = 0.37720959596; human result/target = 0.220538720539; comparison = above. Human work and timing: [gpqa](gpqa.md).

Estimated input 265.626262626 + reported mean output 563.883838384 = 829.51010101 tokens per question. Multiply by 16000000000 FLOPs/token = **1.32721616162e+13 FLOPs per question**.

Changing only input by ±50% changes compute by ±16%. The model's 4–32B active-parameter scenario gives 6.63608e+12–5.30886e+13 FLOPs at the central token workload. These are sensitivity calculations, not confidence bounds.


## reas-epoch-mathl5-gpt4omini

Source: [Epoch output table](https://epoch.ai/data-insights/output-length), Identifier `gpt-4o-mini-2024-07-18`, Benchmark `MATH level 5`. Original AI score = 0.526340634441; human result/target = 0.9; comparison = below. Human work and timing: [mathl5](mathl5.md).

Estimated input 135.910120846 + reported mean output 814.703172205 = 950.613293051 tokens per question. Multiply by 16000000000 FLOPs/token = **1.52098126888e+13 FLOPs per question**.

Changing only input by ±50% changes compute by ±7.15%. The model's 4–32B active-parameter scenario gives 7.60491e+12–6.08393e+13 FLOPs at the central token workload. These are sensitivity calculations, not confidence bounds.


## reas-epoch-gpqa-mistrallarge2402

Source: [Epoch output table](https://epoch.ai/data-insights/output-length), Identifier `mistral-large-2402`, Benchmark `GPQA diamond`. Original AI score = 0.387626262626; human result/target = 0.220538720539; comparison = above. Human work and timing: [gpqa](gpqa.md).

Estimated input 302.101010101 + reported mean output 366.661616162 = 668.762626263 tokens per question. Multiply by 246000000000 FLOPs/token = **1.64515606061e+14 FLOPs per question**.

Changing only input by ±50% changes compute by ±22.6%. The model's 60–250B active-parameter scenario gives 8.02515e+13–3.34381e+14 FLOPs at the central token workload. These are sensitivity calculations, not confidence bounds.


## reas-epoch-mathl5-mistrallarge2402

Source: [Epoch output table](https://epoch.ai/data-insights/output-length), Identifier `mistral-large-2402`, Benchmark `MATH level 5`. Original AI score = 0.24461858006; human result/target = 0.9; comparison = below. Human work and timing: [mathl5](mathl5.md).

Estimated input 143.9418429 + reported mean output 539.954682779 = 683.89652568 tokens per question. Multiply by 246000000000 FLOPs/token = **1.68238545317e+14 FLOPs per question**.

Changing only input by ±50% changes compute by ±10.5%. The model's 60–250B active-parameter scenario gives 8.20676e+13–3.41948e+14 FLOPs at the central token workload. These are sensitivity calculations, not confidence bounds.


## reas-epoch-otis-mistrallarge2402

Original Epoch table: Identifier `mistral-large-2402`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 703.888888889. Input under `mistral3` = 207.822222222. Total = 911.711111111 text tokens × 246000000000 FLOPs/token = **2.24280933333e+14 FLOPs**.

Work unit and human baseline: [OTIS](otis.md). AI accuracy 1.94444%. Original human contest score frequencies imply 51.5507% under equal weighting of the three papers. Current input reconstruction and tokenizer qualification: [OTIS correction](epoch-otis-input-correction.md#reas-epoch-otis-mistrallarge2402).

## reas-epoch-mathl5-openmistral7b

Source: [Epoch output table](https://epoch.ai/data-insights/output-length), Identifier `open-mistral-7b`, Benchmark `MATH level 5`. Original AI score = 0.0368202416918; human result/target = 0.9; comparison = below. Human work and timing: [mathl5](mathl5.md).

Estimated input 143.9418429 + reported mean output 615.825528701 = 759.767371601 tokens per question. Multiply by 14600000000 FLOPs/token = **1.10926036254e+13 FLOPs per question**.

Changing only input by ±50% changes compute by ±9.47%. The model's 7–7.5B active-parameter scenario gives 1.06367e+13–1.13965e+13 FLOPs at the central token workload. These are sensitivity calculations, not confidence bounds.


## reas-epoch-gpqa-gemini15flash8b

Source: [Epoch output table](https://epoch.ai/data-insights/output-length), Identifier `gemini-1.5-flash-8b-001`, Benchmark `GPQA diamond`. Original AI score = 0.329545454545; human result/target = 0.220538720539; comparison = above. Human work and timing: [gpqa](gpqa.md).

Estimated input 279.18013468 + reported mean output 468.929292929 = 748.109427609 tokens per question. Multiply by 16000000000 FLOPs/token = **1.19697508418e+13 FLOPs per question**.

Changing only input by ±50% changes compute by ±18.7%. The model's 6–8B active-parameter scenario gives 8.97731e+12–1.19698e+13 FLOPs at the central token workload. These are sensitivity calculations, not confidence bounds.


## reas-epoch-otis-gemini15flash8b

Original Epoch table: Identifier `gemini-1.5-flash-8b-001`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 900.088888889. Input under `three_tokenizer_mean` = 193.874074074. Total = 1093.96296296 text tokens × 16000000000 FLOPs/token = **1.75034074074e+13 FLOPs**.

Work unit and human baseline: [OTIS](otis.md). AI accuracy 4.58333%. Original human contest score frequencies imply 51.5507% under equal weighting of the three papers. Current input reconstruction and tokenizer qualification: [OTIS correction](epoch-otis-input-correction.md#reas-epoch-otis-gemini15flash8b).

