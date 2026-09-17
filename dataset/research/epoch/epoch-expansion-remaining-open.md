# Epoch Gemma, Tulu and Yi observations

Original Epoch output-table means and source accuracy are paired with reviewed GPQA/MATH/OTIS human recipes. These are inference observations, not training-compute estimates. GPQA/MATH inputs use full source questions plus assumed wrappers; OTIS uses the recovered 45 question texts with the retained tokenizer or explicit proxy, the recovered short instruction and 12 assumed chat positions; see [the input correction](epoch-otis-input-correction.md).

Gemma 2 Table 2 reports embedding/nonembedding counts: 9B = 917,962,752 + 8,324,201,984 = 9,242,164,736; 27B = 1,180,237,824 + 26,047,480,320 = 27,227,718,144. Gemma 3 Table 1 reports 1,416M + 25,600M = 27,016M language-model parameters; its separate 417M vision encoder is not used on these text-only questions. Counts include the embedding matrix consistently with the registry 2P convention. Original reports are linked per model.

The Tulu source Identifier explicitly names the 70B DPO checkpoint. Its model card distinguishes that stage from the final RLVR model; we preserve the exact checkpoint identity. The November 21 release announcement makes the training recipe and intermediate models public. Yi dates use the original repository news: May 13, 2024 for Yi-1.5 and November 23, 2023 for public chat models; earlier invited tests and base releases are not substituted.

Original tokenizer: [allenai/Llama-3.1-Tulu-3-70B-DPO](https://huggingface.co/allenai/Llama-3.1-Tulu-3-70B-DPO/resolve/2dab5183da9252bedf6039a0b09c86b9ca4d0ba9/tokenizer.json), immutable revision `2dab5183da9252bedf6039a0b09c86b9ca4d0ba9`; retained under agent-work/sources/model-cards.

Original tokenizer: [01-ai/Yi-1.5-34B-Chat](https://huggingface.co/01-ai/Yi-1.5-34B-Chat/resolve/fa4ffba162f20948bf77c2a30eca952bf0812b7f/tokenizer.json), immutable revision `fa4ffba162f20948bf77c2a30eca952bf0812b7f`; retained under agent-work/sources/model-cards.

Original tokenizer: [01-ai/Yi-34B-Chat](https://huggingface.co/01-ai/Yi-34B-Chat/resolve/cf02cb50f2a03dead2fe205766a1c5598a90bf80/tokenizer.json), immutable revision `cf02cb50f2a03dead2fe205766a1c5598a90bf80`; retained under agent-work/sources/model-cards.

Gemma 2 inputs use the original Google vocabulary, shared with Gemma 1 by the Gemma 2 paper. Gemma 3 retains the disclosed NeMo proxy; this correction does not establish its vocabulary. Current Gemma 2 counts and provenance are in [the tokenizer reconstruction](../tokenizer-family-correction/tokenizer-family-correction.md).


## Model: gemma-2-9b-it

Reported active parameters: 9.24216e+09; coefficient 2P = 1.84843e+10 FLOPs/token. [Architecture/model card](https://arxiv.org/html/2408.00118v1#S2); release 2024-06-27 supported by [release source](https://blog.google/innovation-and-ai/technology/developers-tools/google-gemma-2/). Input uses the original shared Gemma 1/2 vocabulary; historical chat wrappers remain assumed.


## reas-epoch-mathl5-gemma2-9b

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `gemma-2-9b-it`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.2100641994; classification below versus human target 0.9. Mean output 434.913897281; input 138.867824773 (original Gemma); total 573.781722054 tokens/question × 18484329472 FLOPs/token = 1.06059703955e+13 FLOPs/question. A ±50% input estimate changes total compute by ±12.1%; this is a sensitivity scenario. [Tokenizer provenance and calculation](../tokenizer-family-correction/tokenizer-family-correction.md#reas-epoch-mathl5-gemma2-9b).


## reas-epoch-otis-gemma2-9b

Original Epoch table: Identifier `gemma-2-9b-it`, Benchmark `OTIS Mock AIME 2024-2025`. Retained output 567.6 + input 194.6 using the original shared Gemma vocabulary = 762.2 text tokens. At 18484329472 FLOPs/token: **1.40887559236e+13 FLOPs**. [Tokenizer provenance and calculation](../tokenizer-family-correction/tokenizer-family-correction.md#reas-epoch-otis-gemma2-9b).

Work unit and human baseline: [OTIS](otis.md). AI accuracy 0.555556%. Original human contest score frequencies imply 51.5507% under equal weighting of the three papers. Current input reconstruction and tokenizer qualification: [OTIS correction](epoch-otis-input-correction.md#reas-epoch-otis-gemma2-9b).

## Model: gemma-2-27b-it

Reported active parameters: 2.72277e+10; coefficient 2P = 5.44554e+10 FLOPs/token. [Architecture/model card](https://arxiv.org/html/2408.00118v1#S2); release 2024-06-27 supported by [release source](https://blog.google/innovation-and-ai/technology/developers-tools/google-gemma-2/). Input uses the original shared Gemma 1/2 vocabulary; historical chat wrappers remain assumed.


## reas-epoch-gpqa-gemma2-27b

Work unit and human baseline: [gpqa](gpqa.md). Source row: Identifier `gemma-2-27b-it`, Benchmark `GPQA diamond` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.3648989899; classification above versus human target 0.2205387205. Mean output 330.404040404; input 266.535353535 (original Gemma); total 596.939393939 tokens/question × 54455436288 FLOPs/token = 3.25065951345e+13 FLOPs/question. A ±50% input estimate changes total compute by ±22.3%; this is a sensitivity scenario. [Tokenizer provenance and calculation](../tokenizer-family-correction/tokenizer-family-correction.md#reas-epoch-gpqa-gemma2-27b).


## reas-epoch-mathl5-gemma2-27b

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `gemma-2-27b-it`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.2788897281; classification below versus human target 0.9. Mean output 468.844410876; input 138.867824773 (original Gemma); total 607.71223565 tokens/question × 54455436288 FLOPs/token = 3.30932349299e+13 FLOPs/question. A ±50% input estimate changes total compute by ±11.4%; this is a sensitivity scenario. [Tokenizer provenance and calculation](../tokenizer-family-correction/tokenizer-family-correction.md#reas-epoch-mathl5-gemma2-27b).


## reas-epoch-otis-gemma2-27b

Original Epoch table: Identifier `gemma-2-27b-it`, Benchmark `OTIS Mock AIME 2024-2025`. Retained output 707.377777778 + input 194.6 using the original shared Gemma vocabulary = 901.977777778 text tokens. At 54455436288 FLOPs/token: **4.9117593411e+13 FLOPs**. [Tokenizer provenance and calculation](../tokenizer-family-correction/tokenizer-family-correction.md#reas-epoch-otis-gemma2-27b).

Work unit and human baseline: [OTIS](otis.md). AI accuracy 1.38889%. Original human contest score frequencies imply 51.5507% under equal weighting of the three papers. Current input reconstruction and tokenizer qualification: [OTIS correction](epoch-otis-input-correction.md#reas-epoch-otis-gemma2-27b).

## Model: gemma-3-27b-it

Reported active parameters: 2.7016e+10; coefficient 2P = 5.4032e+10 FLOPs/token. [Architecture/model card](https://arxiv.org/html/2503.19786v1#S2); release 2025-03-12 supported by [release source](https://blog.google/innovation-and-ai/technology/developers-tools/gemma-3/). Input estimate uses the NeMo tokenizer as an explicit cross-family proxy because original Gemma tokenizer files require authentication; this is not a claim of identical tokenization.


## reas-epoch-gpqa-gemma3-27b

Work unit and human baseline: [gpqa](gpqa.md). Source row: Identifier `gemma-3-27b-it`, Benchmark `GPQA diamond` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.4886363636; classification above versus human target 0.2205387205. Mean output 830.121212121; input 268.247474747 (nemo); total 1098.36868687 tokens/question × 54032000000 FLOPs/token = 5.93470568889e+13 FLOPs/question. A ±50% input estimate changes total compute by ±12.2%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-mathl5-gemma3-27b

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `gemma-3-27b-it`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.7403700906; classification below versus human target 0.9. Mean output 1226.90861027; input 136.972054381 (nemo); total 1363.88066465 tokens/question × 54032000000 FLOPs/token = 7.36932000725e+13 FLOPs/question. A ±50% input estimate changes total compute by ±5.02%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-otis-gemma3-27b

Original Epoch table: Identifier `gemma-3-27b-it`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 3147.28888889. Input under `nemo` = 194.533333333. Total = 3341.82222222 text tokens × 54032000000 FLOPs/token = **1.80565338311e+14 FLOPs**.

Work unit and human baseline: [OTIS](otis.md). AI accuracy 19.7222%. Original human contest score frequencies imply 51.5507% under equal weighting of the three papers. Current input reconstruction and tokenizer qualification: [OTIS correction](epoch-otis-input-correction.md#reas-epoch-otis-gemma3-27b).

## Model: llama-3.1-tulu-3-70b-dpo

Reported active parameters: 7e+10; coefficient 2P = 1.4e+11 FLOPs/token. [Architecture/model card](https://huggingface.co/allenai/Llama-3.1-Tulu-3-70B-DPO); release 2024-11-21 supported by [release source](https://allenai.org/blog/tulu-3-technical). Input estimate uses the original checkpoint tokenizer plus the stated wrapper allowance.


## reas-epoch-gpqa-tulu3-70b

Work unit and human baseline: [gpqa](gpqa.md). Source row: Identifier `Llama-3.1-Tulu-3-70B-DPO`, Benchmark `GPQA diamond` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.4627525253; classification above versus human target 0.2205387205. Mean output 619.015151515; input 269.707070707 (tulu3); total 888.722222222 tokens/question × 140000000000 FLOPs/token = 1.24421111111e+14 FLOPs/question. A ±50% input estimate changes total compute by ±15.2%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-mathl5-tulu3-70b

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `Llama-3.1-Tulu-3-70B-DPO`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.4266427492; classification below versus human target 0.9. Mean output 753.571752266; input 135.979607251 (tulu3); total 889.551359517 tokens/question × 140000000000 FLOPs/token = 1.24537190332e+14 FLOPs/question. A ±50% input estimate changes total compute by ±7.64%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-otis-tulu3-70b

Original Epoch table: Identifier `Llama-3.1-Tulu-3-70B-DPO`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 970.866666667. Input under `tulu3` = 187.155555556. Total = 1158.02222222 text tokens × 140000000000 FLOPs/token = **1.62123111111e+14 FLOPs**.

Work unit and human baseline: [OTIS](otis.md). AI accuracy 4.44444%. Original human contest score frequencies imply 51.5507% under equal weighting of the three papers. Current input reconstruction and tokenizer qualification: [OTIS correction](epoch-otis-input-correction.md#reas-epoch-otis-tulu3-70b).

## Model: yi-1.5-34b-chat

Reported active parameters: 3.4e+10; coefficient 2P = 6.8e+10 FLOPs/token. [Architecture/model card](https://huggingface.co/01-ai/Yi-1.5-34B-Chat); release 2024-05-13 supported by [release source](https://github.com/01-ai/Yi#news). Input estimate uses the original checkpoint tokenizer plus the stated wrapper allowance.


## reas-epoch-mathl5-yi15-34b

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `Yi-1.5-34B-Chat`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.2548149547; classification below versus human target 0.9. Mean output 656.888217523; input 145.816465257 (yi15); total 802.704682779 tokens/question × 68000000000 FLOPs/token = 5.4583918429e+13 FLOPs/question. A ±50% input estimate changes total compute by ±9.08%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## Model: yi-34b-chat

Reported active parameters: 3.4e+10; coefficient 2P = 6.8e+10 FLOPs/token. [Architecture/model card](https://huggingface.co/01-ai/Yi-34B-Chat); release 2023-11-23 supported by [release source](https://github.com/01-ai/Yi#news). Input estimate uses the original checkpoint tokenizer plus the stated wrapper allowance.


## reas-epoch-mathl5-yi34b

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `Yi-34B-Chat`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.05145392749; classification below versus human target 0.9. Mean output 695.794561934; input 145.816465257 (yi); total 841.61102719 tokens/question × 68000000000 FLOPs/token = 5.72295498489e+13 FLOPs/question. A ±50% input estimate changes total compute by ±8.66%; no claim this is a confidence interval. The model coefficient and its sources appear above.
