# Epoch additional GPT, o3, Hermes and WizardLM observations

Ten output-table observations retain the reviewed GPQA Diamond, MATH Level 5 and OTIS work units, human estimates and performance comparisons. GPT-4.1 and public o3 retain the reviewed coefficients and identities. Hermes and WizardLM add two model records. Training/merging is not charged to these inference observations.

## Parameter assumptions

GPT-4.1 and public o3 each use the reviewed 50B-active assumption, or 100B FLOPs/token. The original [Epoch energy analysis](https://epoch.ai/gradient-updates/how-much-energy-does-chatgpt-use) supplies a central 200B-total GPT-4o estimate with one-quarter activation. Its transfer to GPT-4.1 and o3 is assumed, not a provider disclosure. [Native-family model research](epoch-native-families.md#model-assumptions) records the shared provenance. A 25–100B-active scenario scales their FLOPs by one half to twice; these are sensitivity cases rather than confidence bounds. The o3 source identifiers explicitly specify high reasoning effort. Reported output includes reasoning and is used instead of a token budget.

Hermes 2 Theta is a dense 70B parameter merge of Hermes 2 Pro and Llama-3 Instruct, as described by the [original Nous model card](https://huggingface.co/NousResearch/Hermes-2-Theta-Llama-3-70B). Merging produces one model; it is not a two-model inference ensemble. The original config has 80 layers, hidden size 8192, 64 attention heads, 8 KV heads and 28672 intermediate size, consistent with the reported 70B scale. The original files are pinned below. June 20 public announcement is supported by a contemporaneous [ThursdAI release account](https://sub.thursdai.news/p/thursdai-june-20th-claude-sonnet): the author describes Teknium announcing the release while that day's episode was being prepared, and availability within the preceding hour. [The same-day announcement-channel digest](https://buttondown.com/ainews/archive/ainews-shazeer-et-al-2024/) corroborates it. The HF repository creation date is June 14; that preparatory timestamp does not establish when the model was public. Date provenance is a contemporary first-hand release account rather than a dated Nous press release.

WizardLM's [original launch page](https://wizardlm.github.io/WizardLM2/) dates its release April 15, 2024. The withdrawn original checkpoint is preserved by the public alpindale mirror, whose model card identifies the original Mixtral-8x22B base. Its retained configuration reports MixtralForCausalLM, 56 layers, hidden size 6144, intermediate size 16384, 48 attention heads, 8 KV heads, eight experts and two experts per token. These match the Mixtral architecture. [Mistral's original release](https://mistral.ai/news/mixtral-8x22b/) reports 39B active of 141B total. We use that rounded active-backbone count, coefficient 78B FLOPs/token, rather than multiplying 8×22B or charging all experts. Post-training changes weights rather than this executed configuration. Mirror provenance is explicitly retained; the accessible original launch supports identity/date but does not independently host the withdrawn weights.

## Input reconstruction

GPQA uses full original questions and answer options with the reviewed instruction prefix plus 12 assumed wrapper positions. MATH uses each of the 1,324 Level-5 problem statements plus 50 assumed wrapper tokens. OTIS uses the recovered 45 question texts with the retained tokenizer or explicit proxy, the recovered short instruction and 12 assumed chat positions; see [the input correction](epoch-otis-input-correction.md). Output lengths and scores are the matching original scatter_data.csv means, not a transfer between benchmarks. The full source Identifier is recorded per point. Input uncertainty is shown as ±50% per point; exact historical wrapper equality is not claimed.

OpenAI inputs use o200k_base under the [official tiktoken model mapping](https://github.com/openai/tiktoken/blob/main/tiktoken/model.py). Hermes uses its original JSON tokenizer; WizardLM uses the preserved original SentencePiece model directly through sentencepiece. No proxy tokenizer is needed for these two open models. Immutable source files:

- hermes70 config.json: [pinned file](https://huggingface.co/NousResearch/Hermes-2-Theta-Llama-3-70B/resolve/8948247fa83f3f970ad24b3394d5656507642922/config.json).
- hermes70 tokenizer.json: [pinned file](https://huggingface.co/NousResearch/Hermes-2-Theta-Llama-3-70B/resolve/8948247fa83f3f970ad24b3394d5656507642922/tokenizer.json).
- wizard2 config.json: [pinned file](https://huggingface.co/alpindale/WizardLM-2-8x22B/resolve/661fa9dcdb48da87a59da37a97df289ee6f5dd50/config.json).
- wizard2 tokenizer.model: [pinned file](https://huggingface.co/alpindale/WizardLM-2-8x22B/resolve/661fa9dcdb48da87a59da37a97df289ee6f5dd50/tokenizer.model).

All human timing and quality assumptions retain the accepted benchmark recipes linked below. No new human sample or performance measurement is introduced.


## Model: gpt-4.1-2025-04-14

Active parameters: 5e+10; coefficient 2P = 1e+11 FLOPs/token. [original source 1](https://epoch.ai/gradient-updates/how-much-energy-does-chatgpt-use); [parameter assumptions](#parameter-assumptions); release 2025-04-14 supported by [release source](https://openai.com/index/gpt-4-1/). Input estimate uses the official o200k_base tokenizer mapping plus an assumed wrapper.


## reas-epoch-gpqa-gpt41

Work unit and human baseline: [gpqa](gpqa.md). Source row: Identifier `gpt-4.1-2025-04-14`, Benchmark `GPQA diamond` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.6691919192; classification above versus human target 0.2205387205. Mean output 797.348484848; input 265.626262626 (o200k); total 1062.97474747 tokens/question × 100000000000 FLOPs/token = 1.06297474747e+14 FLOPs/question. A ±50% input estimate changes total compute by ±12.5%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-mathl5-gpt41

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `gpt-4.1-2025-04-14`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.830060423; classification below versus human target 0.9. Mean output 1299.5641994; input 135.910120846 (o200k); total 1435.47432024 tokens/question × 100000000000 FLOPs/token = 1.43547432024e+14 FLOPs/question. A ±50% input estimate changes total compute by ±4.73%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-otis-gpt41

Original Epoch table: Identifier `gpt-4.1-2025-04-14`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 3812.11111111. Input under `o200k` = 186.6. Total = 3998.71111111 text tokens × 100000000000 FLOPs/token = **3.99871111111e+14 FLOPs**.

Work unit and human baseline: [OTIS](otis.md). AI accuracy 38.3333%. Original human contest score frequencies imply 51.5507% under equal weighting of the three papers. Current input reconstruction and tokenizer qualification: [OTIS correction](epoch-otis-input-correction.md#reas-epoch-otis-gpt41).

## Model: o3-2025-04-16

Active parameters: 5e+10; coefficient 2P = 1e+11 FLOPs/token. [original source 1](https://epoch.ai/gradient-updates/how-much-energy-does-chatgpt-use); [parameter assumptions](#parameter-assumptions); [parameter assumptions](#parameter-assumptions); release 2025-04-16 supported by [release source](https://openai.com/index/introducing-o3-and-o4-mini/). Input estimate uses the official o200k_base tokenizer mapping plus an assumed wrapper.


## reas-epoch-gpqa-o3high

Work unit and human baseline: [gpqa](gpqa.md). Source row: Identifier `o3-2025-04-16_high`, Benchmark `GPQA diamond` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.8181818182; classification above versus human target 0.2205387205. Mean output 7606.86363636; input 265.626262626 (o200k); total 7872.48989899 tokens/question × 100000000000 FLOPs/token = 7.87248989899e+14 FLOPs/question. A ±50% input estimate changes total compute by ±1.69%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-mathl5-o3high

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `o3-2025-04-16_high`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.9777190332; classification above versus human target 0.9. Mean output 3218.75151057; input 135.910120846 (o200k); total 3354.66163142 tokens/question × 100000000000 FLOPs/token = 3.35466163142e+14 FLOPs/question. A ±50% input estimate changes total compute by ±2.03%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## Model: hermes-2-theta-llama-3-70b

Active parameters: 7e+10; coefficient 2P = 1.4e+11 FLOPs/token. [original source 1](https://huggingface.co/NousResearch/Hermes-2-Theta-Llama-3-70B); release 2024-06-20 supported by [release source](https://sub.thursdai.news/p/thursdai-june-20th-claude-sonnet). Dense 70B merge of Hermes 2 Pro and Llama-3 Instruct; no inference ensemble.


## reas-epoch-gpqa-hermes70b

Work unit and human baseline: [gpqa](gpqa.md). Source row: Identifier `Hermes-2-Theta-Llama-3-70B`, Benchmark `GPQA diamond` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.3746843434; classification above versus human target 0.2205387205. Mean output 286.570707071; input 269.707070707 (hermes70); total 556.277777778 tokens/question × 140000000000 FLOPs/token = 7.78788888889e+13 FLOPs/question. A ±50% input estimate changes total compute by ±24.2%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-mathl5-hermes70b

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `Hermes-2-Theta-Llama-3-70B`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.2268693353; classification below versus human target 0.9. Mean output 343.752265861; input 135.979607251 (hermes70); total 479.731873112 tokens/question × 140000000000 FLOPs/token = 6.71624622356e+13 FLOPs/question. A ±50% input estimate changes total compute by ±14.2%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-otis-hermes70b

Original Epoch table: Identifier `Hermes-2-Theta-Llama-3-70B`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 700.777777778. Input under `hermes70` = 187.155555556. Total = 887.933333333 text tokens × 140000000000 FLOPs/token = **1.24310666667e+14 FLOPs**.

Work unit and human baseline: [OTIS](otis.md). AI accuracy 2.5%. Original human contest score frequencies imply 51.5507% under equal weighting of the three papers. Current input reconstruction and tokenizer qualification: [OTIS correction](epoch-otis-input-correction.md#reas-epoch-otis-hermes70b).

## Model: wizardlm-2-8x22b

Active parameters: 3.9e+10; coefficient 2P = 7.8e+10 FLOPs/token. [original source 1](https://huggingface.co/alpindale/WizardLM-2-8x22B/resolve/661fa9dcdb48da87a59da37a97df289ee6f5dd50/config.json); [original source 2](https://mistral.ai/news/mixtral-8x22b/); release 2024-04-15 supported by [release source](https://wizardlm.github.io/WizardLM2/). Mixtral backbone with two of eight experts active per token; 39B active of 141B total. Original configuration preserved in a public mirror.


## reas-epoch-gpqa-wizardlm2

Work unit and human baseline: [gpqa](gpqa.md). Source row: Identifier `WizardLM-2-8x22B`, Benchmark `GPQA diamond` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.4343434343; classification above versus human target 0.2205387205. Mean output 1025.64141414; input 302.101010101 (wizard2); total 1327.74242424 tokens/question × 78000000000 FLOPs/token = 1.03563909091e+14 FLOPs/question. A ±50% input estimate changes total compute by ±11.4%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-mathl5-wizardlm2

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `WizardLM-2-8x22B`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.2573640483; classification below versus human target 0.9. Mean output 1017.79154079; input 143.9418429 (wizard2); total 1161.73338369 tokens/question × 78000000000 FLOPs/token = 9.06152039275e+13 FLOPs/question. A ±50% input estimate changes total compute by ±6.2%; no claim this is a confidence interval. The model coefficient and its sources appear above.
