# Epoch expansion: open models

These observations use the reviewed source-defined GPQA Diamond, MATH Level 5 and OTIS collections. Human evidence and limitations remain in [GPQA](gpqa.md), [MATH](mathl5.md), and [OTIS](otis.md). GPQA uses the arithmetic mean of 594 original human reports, including the 77 shorter than the instructed 15 minutes. MATH uses an assumed ten-minute average effort budget for an IMO-gold-level solver targeting approximately 90%, not an observed Level-5 human timing or score. OTIS assumes full use of the contest allowance and compares original score-frequency tables.

The Epoch output table records mean output tokens per question, including reasoning output. We add an input estimate, then multiply the sum by twice active parameters. No additional reasoning multiplier, benchmark-size multiplier, or training teacher/reward-model cost is applied. Per-benchmark means describe the same benchmark collection as the point. External scoring is excluded. Source table is freshly downloaded agent-work/sources/epoch/scatter_data.csv; exact row keys appear below.

GPQA input reconstruction uses the original Epoch researcher prompt, 198 original questions and all four choices plus 12 assumed wrapper positions. MATH uses all 1,324 Level-5 test statements, including any Asymptote code, plus 50 assumed instruction/wrapper positions. The historical provider wrapper is unavailable. OTIS uses the recovered 45 question texts with the retained tokenizer or explicit proxy, the recovered short instruction and 12 assumed chat positions; see [the input correction](epoch-otis-input-correction.md). Tokenizers are saved alongside original sources and the generator reproduces means. Llama-3 and Llama-3.1 vocabularies come from public NousResearch mirrors; other vocabularies come from original model repositories. DBRX uses cl100k_base, following the original Databricks blog identification of the GPT-4 tokenizer. Llama-2 uses the publicly mirrored original SentencePiece vocabulary; Llama-4 retains Llama-3.1 as an explicit proxy without claiming identical vocabulary. Proxy sensitivity is quantified per point below.

Performance match is a coarse comparison within five percentage points of the stated human target, not a statistical equivalence claim. The GPQA human baseline is the second expert validator, an in-domain PhD who answered the revised question and scored 81.31%; chance is 25% and the 53.16% floor applies. MATH human target remains an assumption.


## Model: llama-2-70b-chat

Reported active parameters: 7e+10; coefficient 2P = 1.4e+11 FLOPs/token. [Architecture/model card](https://huggingface.co/meta-llama/Llama-2-70b-chat-hf); release 2023-07-18 supported by [release source](https://about.fb.com/news/2023/07/llama-2/). Input uses the public mirror of the original Llama 2 vocabulary; the historical serving wrapper remains assumed.


## reas-epoch-mathl5-llama2-70b

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `Llama-2-70b-chat-hf`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.03285498489; classification below versus human target 0.9. Mean output 433.097432024; input 143.668429003 (original Llama 2 mirror); total 576.765861027 tokens/question × 140000000000 FLOPs/token = 8.07472205438e+13 FLOPs/question. A ±50% input estimate changes total compute by ±12.5%; this is a sensitivity scenario. [Tokenizer provenance and calculation](../tokenizer-family-correction/tokenizer-family-correction.md#reas-epoch-mathl5-llama2-70b).


## Model: llama-3-8b-instruct

Reported active parameters: 8e+09; coefficient 2P = 1.6e+10 FLOPs/token. [Architecture/model card](https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct); release 2024-04-18 supported by [release source](https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct). 


## reas-epoch-mathl5-llama3-8b

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `Meta-Llama-3-8B-Instruct`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.06127265861; classification below versus human target 0.9. Mean output 417.630664653; input 135.979607251 (llama); total 553.610271903 tokens/question × 16000000000 FLOPs/token = 8.85776435045e+12 FLOPs/question. A ±50% input estimate changes total compute by ±12.3%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-otis-llama3-8b

Original Epoch table: Identifier `Meta-Llama-3-8B-Instruct`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 645.111111111. Input under `llama` = 187.155555556. Total = 832.266666667 text tokens × 16000000000 FLOPs/token = **1.33162666667e+13 FLOPs**.

Work unit and human baseline: [OTIS](otis.md). AI accuracy 0.833333%. Original human contest score frequencies imply 51.5507% under equal weighting of the three papers. Current input reconstruction and tokenizer qualification: [OTIS correction](epoch-otis-input-correction.md#reas-epoch-otis-llama3-8b).

## Model: llama-3.1-8b-instruct

Reported active parameters: 8e+09; coefficient 2P = 1.6e+10 FLOPs/token. [Architecture/model card](https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct); release 2024-07-23 supported by [release source](https://huggingface.co/meta-llama/Llama-3.1-405B-Instruct). 


## reas-epoch-mathl5-llama31-8b

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `Llama-3.1-8B-Instruct`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.2287575529; classification below versus human target 0.9. Mean output 1309.30740181; input 135.979607251 (llama31); total 1445.28700906 tokens/question × 16000000000 FLOPs/token = 2.3124592145e+13 FLOPs/question. A ±50% input estimate changes total compute by ±4.7%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## Model: llama-3.1-70b-instruct

Reported active parameters: 7e+10; coefficient 2P = 1.4e+11 FLOPs/token. [Architecture/model card](https://huggingface.co/meta-llama/Llama-3.1-70B-Instruct); release 2024-07-23 supported by [release source](https://huggingface.co/meta-llama/Llama-3.1-405B-Instruct). 


## reas-epoch-gpqa-llama31-70b

Work unit and human baseline: [gpqa](gpqa.md). Source row: Identifier `Llama-3.1-70B-Instruct`, Benchmark `GPQA diamond` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.4419191919; classification above versus human target 0.2205387205. Mean output 677.242424242; input 269.707070707 (llama31); total 946.949494949 tokens/question × 140000000000 FLOPs/token = 1.32572929293e+14 FLOPs/question. A ±50% input estimate changes total compute by ±14.2%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-mathl5-llama31-70b

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `Llama-3.1-70B-Instruct`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.3667862538; classification below versus human target 0.9. Mean output 730.790030211; input 135.979607251 (llama31); total 866.769637462 tokens/question × 140000000000 FLOPs/token = 1.21347749245e+14 FLOPs/question. A ±50% input estimate changes total compute by ±7.84%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## Model: llama-3.1-405b-instruct

Reported active parameters: 4.05e+11; coefficient 2P = 8.1e+11 FLOPs/token. [Architecture/model card](https://huggingface.co/meta-llama/Llama-3.1-405B-Instruct); release 2024-07-23 supported by [release source](https://huggingface.co/meta-llama/Llama-3.1-405B-Instruct). 


## reas-epoch-mathl5-llama31-405b

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `Llama-3.1-405B-Instruct`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.497734139; classification below versus human target 0.9. Mean output 897.789274924; input 135.979607251 (llama31); total 1033.76888218 tokens/question × 810000000000 FLOPs/token = 8.37352794562e+14 FLOPs/question. A ±50% input estimate changes total compute by ±6.58%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## Model: llama-3.3-70b-instruct

Reported active parameters: 7e+10; coefficient 2P = 1.4e+11 FLOPs/token. [Architecture/model card](https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct); release 2024-12-06 supported by [release source](https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct). Input estimate uses the same Llama-3.1 family vocabulary with the shared wrapper assumption.


## reas-epoch-gpqa-llama33-70b

Work unit and human baseline: [gpqa](gpqa.md). Source row: Identifier `Llama-3.3-70B-Instruct`, Benchmark `GPQA diamond` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.4744318182; classification above versus human target 0.2205387205. Mean output 806.833333333; input 269.707070707 (llama31); total 1076.54040404 tokens/question × 140000000000 FLOPs/token = 1.50715656566e+14 FLOPs/question. A ±50% input estimate changes total compute by ±12.5%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-mathl5-llama33-70b

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `Llama-3.3-70B-Instruct`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.4159743202; classification below versus human target 0.9. Mean output 946.560422961; input 135.979607251 (llama31); total 1082.54003021 tokens/question × 140000000000 FLOPs/token = 1.5155560423e+14 FLOPs/question. A ±50% input estimate changes total compute by ±6.28%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-otis-llama33-70b

Original Epoch table: Identifier `Llama-3.3-70B-Instruct`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 1157.04444444. Input under `llama31` = 187.155555556. Total = 1344.2 text tokens × 140000000000 FLOPs/token = **1.88188e+14 FLOPs**.

Work unit and human baseline: [OTIS](otis.md). AI accuracy 5.13889%. Original human contest score frequencies imply 51.5507% under equal weighting of the three papers. Current input reconstruction and tokenizer qualification: [OTIS correction](epoch-otis-input-correction.md#reas-epoch-otis-llama33-70b).

## Model: llama-4-scout

Reported active parameters: 1.7e+10; coefficient 2P = 3.4e+10 FLOPs/token. [Architecture/model card](https://huggingface.co/meta-llama/Llama-4-Scout-17B-16E-Instruct); release 2025-04-05 supported by [release source](https://huggingface.co/meta-llama/Llama-4-Scout-17B-16E-Instruct). Reported 17B active MoE count. Text-input token estimate uses Llama-3.1 tokenizer as a proxy for unavailable exact provider accounting; not a claim of identical vocabulary.


## reas-epoch-gpqa-llama4-scout

Work unit and human baseline: [gpqa](gpqa.md). Source row: Identifier `Llama-4-Scout-17B-16E-Instruct`, Benchmark `GPQA diamond` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.5183080808; classification above versus human target 0.2205387205. Mean output 927.348484848; input 269.707070707 (llama31); total 1197.05555556 tokens/question × 34000000000 FLOPs/token = 4.06998888889e+13 FLOPs/question. A ±50% input estimate changes total compute by ±11.3%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-mathl5-llama4-scout

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `Llama-4-Scout-17B-16E-Instruct`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.622734139; classification below versus human target 0.9. Mean output 1117.68504532; input 135.979607251 (llama31); total 1253.66465257 tokens/question × 34000000000 FLOPs/token = 4.26245981873e+13 FLOPs/question. A ±50% input estimate changes total compute by ±5.42%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-otis-llama4-scout

Original Epoch table: Identifier `Llama-4-Scout-17B-16E-Instruct`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 1435.46666667. Input under `llama31` = 187.155555556. Total = 1622.62222222 text tokens × 34000000000 FLOPs/token = **5.51691555556e+13 FLOPs**.

Work unit and human baseline: [OTIS](otis.md). AI accuracy 7.77778%. Original human contest score frequencies imply 51.5507% under equal weighting of the three papers. Current input reconstruction and tokenizer qualification: [OTIS correction](epoch-otis-input-correction.md#reas-epoch-otis-llama4-scout).

## Model: llama-4-maverick

Reported active parameters: 1.7e+10; coefficient 2P = 3.4e+10 FLOPs/token. [Architecture/model card](https://huggingface.co/meta-llama/Llama-4-Maverick-17B-128E-Instruct); release 2025-04-05 supported by [release source](https://huggingface.co/meta-llama/Llama-4-Maverick-17B-128E-Instruct). Reported 17B active MoE count. Text-input token estimate uses Llama-3.1 tokenizer as a proxy for unavailable exact provider accounting; not a claim of identical vocabulary.


## reas-epoch-gpqa-llama4-maverick

Work unit and human baseline: [gpqa](gpqa.md). Source row: Identifier `Llama-4-Maverick-17B-128E-Instruct-FP8`, Benchmark `GPQA diamond` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.6698232323; classification above versus human target 0.2205387205. Mean output 885.434343434; input 269.707070707 (llama31); total 1155.14141414 tokens/question × 34000000000 FLOPs/token = 3.92748080808e+13 FLOPs/question. A ±50% input estimate changes total compute by ±11.7%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-mathl5-llama4-maverick

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `Llama-4-Maverick-17B-128E-Instruct-FP8`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.730173716; classification below versus human target 0.9. Mean output 888.533232628; input 135.979607251 (llama31); total 1024.51283988 tokens/question × 34000000000 FLOPs/token = 3.48334365559e+13 FLOPs/question. A ±50% input estimate changes total compute by ±6.64%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-otis-llama4-maverick

Original Epoch table: Identifier `Llama-4-Maverick-17B-128E-Instruct-FP8`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 1312.66666667. Input under `llama31` = 187.155555556. Total = 1499.82222222 text tokens × 34000000000 FLOPs/token = **5.09939555556e+13 FLOPs**.

Work unit and human baseline: [OTIS](otis.md). AI accuracy 20.5556%. Original human contest score frequencies imply 51.5507% under equal weighting of the three papers. Current input reconstruction and tokenizer qualification: [OTIS correction](epoch-otis-input-correction.md#reas-epoch-otis-llama4-maverick).

## Model: qwen2-72b-instruct

Reported active parameters: 7.2e+10; coefficient 2P = 1.44e+11 FLOPs/token. [Architecture/model card](https://huggingface.co/Qwen/Qwen2-72B-Instruct); release 2024-06-06 supported by [release source](https://github.com/QwenLM/Qwen3#news). 


## reas-epoch-gpqa-qwen2-72b

Work unit and human baseline: [gpqa](gpqa.md). Source row: Identifier `qwen2-72b-instruct`, Benchmark `GPQA diamond` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.4078282828; classification above versus human target 0.2205387205. Mean output 335.070707071; input 273.808080808 (qwen); total 608.878787879 tokens/question × 144000000000 FLOPs/token = 8.76785454545e+13 FLOPs/question. A ±50% input estimate changes total compute by ±22.5%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-mathl5-qwen2-72b

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `qwen2-72b-instruct`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.3906722054; classification below versus human target 0.9. Mean output 536.614803625; input 138.580060423 (qwen); total 675.194864048 tokens/question × 144000000000 FLOPs/token = 9.7228060423e+13 FLOPs/question. A ±50% input estimate changes total compute by ±10.3%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## Model: qwen2.5-72b-instruct

Reported active parameters: 7.27e+10; coefficient 2P = 1.454e+11 FLOPs/token. [Architecture/model card](https://huggingface.co/Qwen/Qwen2.5-72B-Instruct); release 2024-09-19 supported by [release source](https://qwenlm.github.io/blog/qwen2.5/). 


## reas-epoch-gpqa-qwen25-72b

Work unit and human baseline: [gpqa](gpqa.md). Source row: Identifier `qwen2.5-72b-instruct`, Benchmark `GPQA diamond` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.4914772727; classification above versus human target 0.2205387205. Mean output 713.772727273; input 273.808080808 (qwen); total 987.580808081 tokens/question × 145400000000 FLOPs/token = 1.43594249495e+14 FLOPs/question. A ±50% input estimate changes total compute by ±13.9%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-mathl5-qwen25-72b

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `qwen2.5-72b-instruct`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.6317031722; classification below versus human target 0.9. Mean output 920.135951662; input 138.580060423 (qwen); total 1058.71601208 tokens/question × 145400000000 FLOPs/token = 1.53937308157e+14 FLOPs/question. A ±50% input estimate changes total compute by ±6.54%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-otis-qwen25-72b

Original Epoch table: Identifier `qwen2.5-72b-instruct`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 992.266666667. Input under `qwen` = 195.288888889. Total = 1187.55555556 text tokens × 145400000000 FLOPs/token = **1.72670577778e+14 FLOPs**.

Work unit and human baseline: [OTIS](otis.md). AI accuracy 8.05556%. Original human contest score frequencies imply 51.5507% under equal weighting of the three papers. Current input reconstruction and tokenizer qualification: [OTIS correction](epoch-otis-input-correction.md#reas-epoch-otis-qwen25-72b).

## Model: deepseek-llm-67b-chat

Reported active parameters: 6.7e+10; coefficient 2P = 1.34e+11 FLOPs/token. [Architecture/model card](https://huggingface.co/deepseek-ai/deepseek-llm-67b-chat); release 2023-11-29 supported by [release source](https://www.reddit.com/r/LocalLLaMA/comments/186o3sx/). November 29 public launch/use report corroborates availability; original model card supplies architecture.


## reas-epoch-mathl5-ds67b

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `deepseek-llm-67b-chat`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.06391616314; classification below versus human target 0.9. Mean output 444.975075529; input 140.250755287 (ds67); total 585.225830816 tokens/question × 134000000000 FLOPs/token = 7.84202613293e+13 FLOPs/question. A ±50% input estimate changes total compute by ±12%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## Model: deepseek-v3

Reported active parameters: 3.7e+10; coefficient 2P = 7.4e+10 FLOPs/token. [Architecture/model card](https://huggingface.co/deepseek-ai/DeepSeek-V3); release 2024-12-26 supported by [release source](https://api-docs.deepseek.com/news/news1226/). 


## reas-epoch-mathl5-v3

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `DeepSeek-V3`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.6485083082; classification below versus human target 0.9. Mean output 1047.41314199; input 134.336858006 (deepseek); total 1181.75 tokens/question × 74000000000 FLOPs/token = 8.74495e+13 FLOPs/question. A ±50% input estimate changes total compute by ±5.68%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-otis-v3

Original Epoch table: Identifier `DeepSeek-V3`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 1865.82222222. Input under `deepseek` = 184.311111111. Total = 2050.13333333 text tokens × 74000000000 FLOPs/token = **1.51709866667e+14 FLOPs**.

Work unit and human baseline: [OTIS](otis.md). AI accuracy 15.8333%. Original human contest score frequencies imply 51.5507% under equal weighting of the three papers. Current input reconstruction and tokenizer qualification: [OTIS correction](epoch-otis-input-correction.md#reas-epoch-otis-v3).

## Model: deepseek-r1

Reported active parameters: 3.7e+10; coefficient 2P = 7.4e+10 FLOPs/token. [Architecture/model card](https://huggingface.co/deepseek-ai/DeepSeek-R1); release 2025-01-20 supported by [release source](https://api-docs.deepseek.com/news/news250120/). 


## reas-epoch-mathl5-r1

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `DeepSeek-R1`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.9305135952; classification match versus human target 0.9. Mean output 4792.57401813; input 134.336858006 (deepseek); total 4926.91087613 tokens/question × 74000000000 FLOPs/token = 3.64591404834e+14 FLOPs/question. A ±50% input estimate changes total compute by ±1.36%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## Model: deepseek-r1-distill-llama-70b

Reported active parameters: 7e+10; coefficient 2P = 1.4e+11 FLOPs/token. [Architecture/model card](https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Llama-70B); release 2025-01-20 supported by [release source](https://api-docs.deepseek.com/news/news250120/). Llama 3.3 70B architecture; student inference only, excluding training teacher/reward models.


## reas-epoch-mathl5-r1distill70b

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `DeepSeek-R1-Distill-Llama-70B`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.8989803625; classification match versus human target 0.9. Mean output 4288.8081571; input 135.979607251 (r1distill); total 4424.78776435 tokens/question × 140000000000 FLOPs/token = 6.19470287009e+14 FLOPs/question. A ±50% input estimate changes total compute by ±1.54%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-otis-r1distill70b

Original Epoch table: Identifier `DeepSeek-R1-Distill-Llama-70B`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 16154.7333333. Input under `r1distill` = 187.155555556. Total = 16341.8888889 text tokens × 140000000000 FLOPs/token = **2.28786444444e+15 FLOPs**.

Work unit and human baseline: [OTIS](otis.md). AI accuracy 51.3889%. Original human contest score frequencies imply 51.5507% under equal weighting of the three papers. Current input reconstruction and tokenizer qualification: [OTIS correction](epoch-otis-input-correction.md#reas-epoch-otis-r1distill70b).

## Model: eurus-2-7b-prime

Reported active parameters: 7e+09; coefficient 2P = 1.4e+10 FLOPs/token. [Architecture/model card](https://huggingface.co/PRIME-RL/Eurus-2-7B-PRIME); release 2025-01-02 supported by [release source](https://github.com/PRIME-RL/PRIME#-news). Fine-tuned Qwen2.5-Math-7B policy. Training-time process reward model is not a fixed-policy inference helper.


## reas-epoch-gpqa-eurus7b

Work unit and human baseline: [gpqa](gpqa.md). Source row: Identifier `Eurus-2-7B-PRIME`, Benchmark `GPQA diamond` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.3390151515; classification above versus human target 0.2205387205. Mean output 1002.71212121; input 273.808080808 (eurus); total 1276.52020202 tokens/question × 14000000000 FLOPs/token = 1.78712828283e+13 FLOPs/question. A ±50% input estimate changes total compute by ±10.7%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## Model: phi-3-medium-128k-instruct

Reported active parameters: 1.4e+10; coefficient 2P = 2.8e+10 FLOPs/token. [Architecture/model card](https://huggingface.co/microsoft/Phi-3-medium-128k-instruct); release 2024-05-21 supported by [release source](https://huggingface.co/microsoft/Phi-3-medium-128k-instruct). 


## reas-epoch-mathl5-phi3-medium

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `Phi-3-medium-128k-instruct`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.1756042296; classification below versus human target 0.9. Mean output 520.403323263; input 143.668429003 (phi3); total 664.071752266 tokens/question × 28000000000 FLOPs/token = 1.85940090634e+13 FLOPs/question. A ±50% input estimate changes total compute by ±10.8%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## Model: phi-4

Reported active parameters: 1.4e+10; coefficient 2P = 2.8e+10 FLOPs/token. [Architecture/model card](https://huggingface.co/microsoft/phi-4); release 2024-12-12 supported by [release source](https://huggingface.co/microsoft/phi-4). 


## reas-epoch-gpqa-phi4

Work unit and human baseline: [gpqa](gpqa.md). Source row: Identifier `phi-4`, Benchmark `GPQA diamond` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.5606060606; classification above versus human target 0.2205387205. Mean output 668.53030303; input 269.813131313 (phi4); total 938.343434343 tokens/question × 28000000000 FLOPs/token = 2.62736161616e+13 FLOPs/question. A ±50% input estimate changes total compute by ±14.4%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-mathl5-phi4

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `phi-4`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.649358006; classification below versus human target 0.9. Mean output 866.203172205; input 135.99244713 (phi4); total 1002.19561934 tokens/question × 28000000000 FLOPs/token = 2.80614773414e+13 FLOPs/question. A ±50% input estimate changes total compute by ±6.78%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-otis-phi4

Original Epoch table: Identifier `phi-4`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 1243.97777778. Input under `phi4` = 187.2. Total = 1431.17777778 text tokens × 28000000000 FLOPs/token = **4.00729777778e+13 FLOPs**.

Work unit and human baseline: [OTIS](otis.md). AI accuracy 13.75%. Original human contest score frequencies imply 51.5507% under equal weighting of the three papers. Current input reconstruction and tokenizer qualification: [OTIS correction](epoch-otis-input-correction.md#reas-epoch-otis-phi4).

## Model: dbrx-instruct

Reported active parameters: 3.6e+10; coefficient 2P = 7.2e+10 FLOPs/token. [Architecture/model card](https://www.databricks.com/blog/introducing-dbrx-new-state-art-open-llm); release 2024-03-27 supported by [release source](https://www.databricks.com/blog/introducing-dbrx-new-state-art-open-llm). 36B active of 132B total MoE parameters. Original Databricks blog identifies the GPT-4 tokenizer; input reconstruction uses cl100k_base.


## reas-epoch-gpqa-dbrx

Work unit and human baseline: [gpqa](gpqa.md). Source row: Identifier `dbrx-instruct`, Benchmark `GPQA diamond` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.3289141414; classification above versus human target 0.2205387205. Mean output 378.767676768; input 269.813131313 (cl100k); total 648.580808081 tokens/question × 72000000000 FLOPs/token = 4.66978181818e+13 FLOPs/question. A ±50% input estimate changes total compute by ±20.8%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-mathl5-dbrx

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `dbrx-instruct`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.1165030211; classification below versus human target 0.9. Mean output 639.170694864; input 135.99244713 (cl100k); total 775.163141994 tokens/question × 72000000000 FLOPs/token = 5.58117462236e+13 FLOPs/question. A ±50% input estimate changes total compute by ±8.77%; no claim this is a confidence interval. The model coefficient and its sources appear above.
