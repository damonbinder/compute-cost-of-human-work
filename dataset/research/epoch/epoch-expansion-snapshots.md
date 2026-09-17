# Epoch GPT snapshots and text-only Llama3.2

Original Epoch output-table means and exact source accuracy are paired with reviewed GPQA/MATH/OTIS human recipes. No human timing or performance target changes. Every source Identifier is preserved; configurations are distinct model snapshots. GPQA/MATH use full-question tokenization plus assumed wrappers; OTIS uses the recovered 45 question texts with the retained tokenizer or explicit proxy, the recovered short instruction and 12 assumed chat positions; see [the input correction](epoch-otis-input-correction.md).

## Parameter assumptions

Numerical provenance: [Epoch’s original MoE inference analysis](https://epoch.ai/gradient-updates/moe-vs-dense-models-inference), section “Estimating the MoE inference edge,” estimates GPT-4 arithmetic as equivalent to a dense 275B-parameter model, giving 2 × 275B = 550B FLOPs/token. [Epoch’s energy analysis](https://epoch.ai/gradient-updates/how-much-energy-does-chatgpt-use), “Estimating the energy cost of a query,” gives a central GPT-4o total size estimate of 200B and assumes one quarter active. We adopt 200B ÷ 4 = 50B active, or 100B FLOPs/token; the article instead uses its pessimistic 400B endpoint for its own energy calculation. Both are external architectural estimates, not OpenAI disclosures.

The official OpenAI releases do not disclose active parameter counts. GPT-4 June and the three Turbo snapshots use the existing registry GPT-4-family assumption of 275B active parameters (550B FLOPs/token); GPT-4o May/November use the existing 50B active assumption (100B FLOPs/token). These are model-family transfers, not reported sizes or values derived from API prices. Retaining the same count within each family avoids inventing unsupported architecture differences between snapshots. Turbo may in fact differ from the original GPT-4; a half-to-double coefficient sensitivity is 137.5–550B active for GPT-4/Turbo and 25–100B for GPT-4o, scaling resulting FLOPs directly. These intervals are scenarios, not confidence bounds. Parameter evidence is estimated for all six OpenAI records. Official sources establish identity/date, not the numerical assumption.

Llama3.2 90B adds vision encoding and adapter cross-attention to the Llama3.1 70B language backbone. Meta states the language-model parameters remain unchanged; original code skips cross-attention blocks when text_only_inference=True. These benchmark inputs contain text only, so we use the reported 70B language backbone, 140B FLOPs/token, with visual components not used. Source code: https://github.com/meta-llama/llama-models/blob/88e9f6aadc0067cb7a4724cc5e46eca384c11a91/models/llama3/multimodal/model.py#L1188 ; retained as agent-work/sources/epoch/llama32-multimodal-model.py. This is an execution-path coefficient for text-only use, not the model total. Extra image-token embeddings and setup overhead are negligible within reported rounded70B.

Dates are public availability: June13 GPT-4 function-calling update, Nov6 GPT-4 Turbo launch, Jan25 updated Turbo preview, Apr9 Turbo general availability, May13 GPT-4o launch, Nov20 GPT-4o update, Sep25 Llama3.2 launch. Official announcement/changelog sources appear per model; snapshot suffixes alone were not used as evidence.

Tokenizer sources: [official tiktoken model mapping](https://github.com/openai/tiktoken/blob/main/tiktoken/model.py) maps GPT-4 to cl100k_base and GPT-4o to o200k_base. Local tiktoken files reproduce counts. Llama3.2 uses the explicitly disclosed original Tulu Llama3.1 family proxy, [immutable tokenizer](https://huggingface.co/allenai/Llama-3.1-Tulu-3-70B-DPO/resolve/2dab5183da9252bedf6039a0b09c86b9ca4d0ba9/tokenizer.json), since the gated original checkpoint was not accessible. This is not a claim of exact historical wrapper/tokenizer identity.


## Model: gpt-4-0613

Active parameters: 2.75e+11; coefficient 2P = 5.5e+11 FLOPs/token. [original source 1](https://epoch.ai/gradient-updates/moe-vs-dense-models-inference); [parameter assumptions](#parameter-assumptions); release 2023-06-13 supported by [release source](https://openai.com/index/function-calling-and-other-api-updates/). Input estimate uses the provider tiktoken cl100k_base mapping plus assumed wrapper.


## reas-epoch-mathl5-gpt4-0613

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `gpt-4-0613`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.2297016616; classification below versus human target 0.9. Mean output 348.885951662; input 135.99244713 (cl100k); total 484.878398792 tokens/question × 550000000000 FLOPs/token = 2.66683119335e+14 FLOPs/question. A ±50% input estimate changes total compute by ±14%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## Model: gpt-4-1106-preview

Active parameters: 2.75e+11; coefficient 2P = 5.5e+11 FLOPs/token. [original source 1](https://epoch.ai/gradient-updates/moe-vs-dense-models-inference); [parameter assumptions](#parameter-assumptions); release 2023-11-06 supported by [release source](https://openai.com/index/new-models-and-developer-products-announced-at-devday/). Input estimate uses the provider tiktoken cl100k_base mapping plus assumed wrapper.


## reas-epoch-gpqa-gpt4-1106

Work unit and human baseline: [gpqa](gpqa.md). Source row: Identifier `gpt-4-1106-preview`, Benchmark `GPQA diamond` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.4236111111; classification above versus human target 0.2205387205. Mean output 531.767676768; input 269.813131313 (cl100k); total 801.580808081 tokens/question × 550000000000 FLOPs/token = 4.40869444444e+14 FLOPs/question. A ±50% input estimate changes total compute by ±16.8%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-mathl5-gpt4-1106

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `gpt-4-1106-preview`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.4002077039; classification below versus human target 0.9. Mean output 764.996978852; input 135.99244713 (cl100k); total 900.989425982 tokens/question × 550000000000 FLOPs/token = 4.9554418429e+14 FLOPs/question. A ±50% input estimate changes total compute by ±7.55%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## Model: gpt-4-0125-preview

Active parameters: 2.75e+11; coefficient 2P = 5.5e+11 FLOPs/token. [original source 1](https://epoch.ai/gradient-updates/moe-vs-dense-models-inference); [parameter assumptions](#parameter-assumptions); release 2024-01-25 supported by [release source](https://openai.com/index/new-embedding-models-and-api-updates/). Input estimate uses the provider tiktoken cl100k_base mapping plus assumed wrapper.


## reas-epoch-gpqa-gpt4-0125

Work unit and human baseline: [gpqa](gpqa.md). Source row: Identifier `gpt-4-0125-preview`, Benchmark `GPQA diamond` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.4226641414; classification above versus human target 0.2205387205. Mean output 582.909090909; input 269.813131313 (cl100k); total 852.722222222 tokens/question × 550000000000 FLOPs/token = 4.68997222222e+14 FLOPs/question. A ±50% input estimate changes total compute by ±15.8%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-mathl5-gpt4-0125

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `gpt-4-0125-preview`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.3541351964; classification below versus human target 0.9. Mean output 832.093655589; input 135.99244713 (cl100k); total 968.086102719 tokens/question × 550000000000 FLOPs/token = 5.32447356495e+14 FLOPs/question. A ±50% input estimate changes total compute by ±7.02%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## Model: gpt-4-turbo-2024-04-09

Active parameters: 2.75e+11; coefficient 2P = 5.5e+11 FLOPs/token. [original source 1](https://epoch.ai/gradient-updates/moe-vs-dense-models-inference); [parameter assumptions](#parameter-assumptions); release 2024-04-09 supported by [release source](https://developers.openai.com/api/docs/changelog). Input estimate uses the provider tiktoken cl100k_base mapping plus assumed wrapper.


## reas-epoch-gpqa-gpt4turbo

Work unit and human baseline: [gpqa](gpqa.md). Source row: Identifier `gpt-4-turbo-2024-04-09`, Benchmark `GPQA diamond` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.4659090909; classification above versus human target 0.2205387205. Mean output 565.015151515; input 269.813131313 (cl100k); total 834.828282828 tokens/question × 550000000000 FLOPs/token = 4.59155555556e+14 FLOPs/question. A ±50% input estimate changes total compute by ±16.2%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-mathl5-gpt4turbo

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `gpt-4-turbo-2024-04-09`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.4673338369; classification below versus human target 0.9. Mean output 614.728096677; input 135.99244713 (cl100k); total 750.720543807 tokens/question × 550000000000 FLOPs/token = 4.12896299094e+14 FLOPs/question. A ±50% input estimate changes total compute by ±9.06%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-otis-gpt4turbo

Original Epoch table: Identifier `gpt-4-turbo-2024-04-09`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 751.777777778. Input under `cl100k` = 187.2. Total = 938.977777778 text tokens × 550000000000 FLOPs/token = **5.16437777778e+14 FLOPs**.

Work unit and human baseline: [OTIS](otis.md). AI accuracy 6.66667%. Original human contest score frequencies imply 51.5507% under equal weighting of the three papers. Current input reconstruction and tokenizer qualification: [OTIS correction](epoch-otis-input-correction.md#reas-epoch-otis-gpt4turbo).

## Model: gpt-4o-2024-05-13

Active parameters: 5e+10; coefficient 2P = 1e+11 FLOPs/token. [original source 1](https://epoch.ai/gradient-updates/how-much-energy-does-chatgpt-use); [parameter assumptions](#parameter-assumptions); release 2024-05-13 supported by [release source](https://openai.com/index/hello-gpt-4o/). Input estimate uses the provider tiktoken o200k_base mapping plus assumed wrapper.


## reas-epoch-gpqa-gpt4o-0513

Work unit and human baseline: [gpqa](gpqa.md). Source row: Identifier `gpt-4o-2024-05-13`, Benchmark `GPQA diamond` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.4889520202; classification above versus human target 0.2205387205. Mean output 588.373737374; input 265.626262626 (o200k); total 854 tokens/question × 100000000000 FLOPs/token = 8.54e+13 FLOPs/question. A ±50% input estimate changes total compute by ±15.6%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-mathl5-gpt4o-0513

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `gpt-4o-2024-05-13`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.5104796073; classification below versus human target 0.9. Mean output 671.021903323; input 135.910120846 (o200k); total 806.932024169 tokens/question × 100000000000 FLOPs/token = 8.06932024169e+13 FLOPs/question. A ±50% input estimate changes total compute by ±8.42%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-otis-gpt4o-0513

Original Epoch table: Identifier `gpt-4o-2024-05-13`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 735.666666667. Input under `o200k` = 186.6. Total = 922.266666667 text tokens × 100000000000 FLOPs/token = **9.22266666667e+13 FLOPs**.

Work unit and human baseline: [OTIS](otis.md). AI accuracy 6.25%. Original human contest score frequencies imply 51.5507% under equal weighting of the three papers. Current input reconstruction and tokenizer qualification: [OTIS correction](epoch-otis-input-correction.md#reas-epoch-otis-gpt4o-0513).

## Model: gpt-4o-2024-11-20

Active parameters: 5e+10; coefficient 2P = 1e+11 FLOPs/token. [original source 1](https://epoch.ai/gradient-updates/how-much-energy-does-chatgpt-use); [parameter assumptions](#parameter-assumptions); release 2024-11-20 supported by [release source](https://developers.openai.com/api/docs/changelog). Input estimate uses the provider tiktoken o200k_base mapping plus assumed wrapper.


## reas-epoch-gpqa-gpt4o-1120

Work unit and human baseline: [gpqa](gpqa.md). Source row: Identifier `gpt-4o-2024-11-20`, Benchmark `GPQA diamond` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.4788510101; classification above versus human target 0.2205387205. Mean output 725.626262626; input 265.626262626 (o200k); total 991.252525253 tokens/question × 100000000000 FLOPs/token = 9.91252525253e+13 FLOPs/question. A ±50% input estimate changes total compute by ±13.4%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-mathl5-gpt4o-1120

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `gpt-4o-2024-11-20`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.497734139; classification below versus human target 0.9. Mean output 791.101963746; input 135.910120846 (o200k); total 927.012084592 tokens/question × 100000000000 FLOPs/token = 9.27012084592e+13 FLOPs/question. A ±50% input estimate changes total compute by ±7.33%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-otis-gpt4o-1120

Original Epoch table: Identifier `gpt-4o-2024-11-20`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 990.822222222. Input under `o200k` = 186.6. Total = 1177.42222222 text tokens × 100000000000 FLOPs/token = **1.17742222222e+14 FLOPs**.

Work unit and human baseline: [OTIS](otis.md). AI accuracy 6.25%. Original human contest score frequencies imply 51.5507% under equal weighting of the three papers. Current input reconstruction and tokenizer qualification: [OTIS correction](epoch-otis-input-correction.md#reas-epoch-otis-gpt4o-1120).

## Model: llama-3.2-90b-vision-instruct

Active parameters: 7e+10; coefficient 2P = 1.4e+11 FLOPs/token. [original source 1](https://ai.meta.com/blog/llama-3-2-connect-2024-vision-edge-mobile-devices/); [original source 2](https://github.com/meta-llama/llama-models/blob/88e9f6aadc0067cb7a4724cc5e46eca384c11a91/models/llama3/multimodal/model.py#L1188); release 2024-09-25 supported by [release source](https://ai.meta.com/blog/llama-3-2-connect-2024-vision-edge-mobile-devices/). Input estimate uses the original Tulu Llama3.1 tokenizer as a family proxy plus assumed wrapper.


## reas-epoch-gpqa-llama32-90b

Work unit and human baseline: [gpqa](gpqa.md). Source row: Identifier `Llama-3.2-90B-Vision-Instruct`, Benchmark `GPQA diamond` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.4103535354; classification above versus human target 0.2205387205. Mean output 648.116161616; input 269.707070707 (tulu3); total 917.823232323 tokens/question × 140000000000 FLOPs/token = 1.28495252525e+14 FLOPs/question. A ±50% input estimate changes total compute by ±14.7%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-mathl5-llama32-90b

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `Llama-3.2-90B-Vision-Instruct`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.3943542296; classification below versus human target 0.9. Mean output 824.576283988; input 135.979607251 (tulu3); total 960.555891239 tokens/question × 140000000000 FLOPs/token = 1.34477824773e+14 FLOPs/question. A ±50% input estimate changes total compute by ±7.08%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-otis-llama32-90b

Original Epoch table: Identifier `Llama-3.2-90B-Vision-Instruct`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 1155.2. Input under `tulu3` = 187.155555556. Total = 1342.35555556 text tokens × 140000000000 FLOPs/token = **1.87929777778e+14 FLOPs**.

Work unit and human baseline: [OTIS](otis.md). AI accuracy 2.63889%. Original human contest score frequencies imply 51.5507% under equal weighting of the three papers. Current input reconstruction and tokenizer qualification: [OTIS correction](epoch-otis-input-correction.md#reas-epoch-otis-llama32-90b).

