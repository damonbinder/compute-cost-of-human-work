# Epoch expansion: previously reviewed model assumptions

New source workload observations for three existing canonical model records. Parameter assumptions and identities are copied unchanged from the authorized current registry: GPT-4o August 2024 uses 50B active, Claude 3.5/3.7 Sonnet use 100B active. These are assumptions, not reported architecture facts. Parameter-source strings are retained without treating older research as new evidence.

Original Epoch output means and scores are matched to the exact source identifiers below. Both ordinary and 64K-thinking Claude 3.7 use one model identity; the source suffix records the generation configuration, not a distinct trained model. Thinking is already included in output. A 64K budget is not 64K actual usage, and no budget multiplier is applied.

GPQA and MATH inputs use the reviewed full-question reconstruction with 12/50 assumed wrapper positions. GPT-4o uses the public o200k_base tokenizer; Claude uses cl100k_base as an explicit input-count proxy. OTIS uses the recovered 45 question texts with the retained tokenizer or explicit proxy, the recovered short instruction and 12 assumed chat positions; see [the input correction](epoch-otis-input-correction.md). Each point records input sensitivity. Human recipes, scope differences and performance targets are unchanged from GPQA/MATH/OTIS notes.

Official release cross-checks: [Claude 3.5 October](https://www.anthropic.com/news/3-5-models-and-computer-use) confirms October 22, 2024 availability; [Claude 3.7](https://www.anthropic.com/news/claude-3-7-sonnet) confirms February 24, 2025 and that standard/extended thinking use the same model. The 20250219 API identifier is not treated as its public release day.


## Model: gpt-4o-2024-08-06

Previously reviewed assumed active parameters: 5e+10; coefficient 2P = 1e+11 FLOPs/token. Shared parameter-source locator: `https://epoch.ai/gradient-updates/how-much-energy-does-chatgpt-use; research/fresh-five-models.md; research/imagenet.md#perc-imagenet-gpt4o; https://github.com/mlfoundations/open_clip/blob/main/src/open_clip/model_configs/ViT-bigG-14.json`; release 2024-08-06 supported by [release source](https://openai.com/index/introducing-structured-outputs-in-the-api/). Input tokenizer is the public GPT-4o o200k_base vocabulary, with assumed historical wrapper positions.


## reas-epoch-gpqa-gpt4o-0806

Work unit and human baseline: [gpqa](gpqa.md). Source row: Identifier `gpt-4o-2024-08-06`, Benchmark `GPQA diamond` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.4921085859; classification above versus human target 0.2205387205. Mean output 588.97979798; input 265.626262626 (o200k); total 854.606060606 tokens/question × 100000000000 FLOPs/token = 8.54606060606e+13 FLOPs/question. A ±50% input estimate changes total compute by ±15.5%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-mathl5-gpt4o-0806

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `gpt-4o-2024-08-06`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.532760574; classification below versus human target 0.9. Mean output 701.834592145; input 135.910120846 (o200k); total 837.744712991 tokens/question × 100000000000 FLOPs/token = 8.37744712991e+13 FLOPs/question. A ±50% input estimate changes total compute by ±8.11%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-otis-gpt4o-0806

Original Epoch table: Identifier `gpt-4o-2024-08-06`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 835.666666667. Input under `o200k` = 186.6. Total = 1022.26666667 text tokens × 100000000000 FLOPs/token = **1.02226666667e+14 FLOPs**.

Work unit and human baseline: [OTIS](otis.md). AI accuracy 6.38889%. Original human contest score frequencies imply 51.5507% under equal weighting of the three papers. Current input reconstruction and tokenizer qualification: [OTIS correction](epoch-otis-input-correction.md#reas-epoch-otis-gpt4o-0806).

## Model: claude-3-5-sonnet-20241022

Previously reviewed assumed active parameters: 1e+11; coefficient 2P = 2e+11 FLOPs/token. Shared parameter-source locator: `research/metr/metr-expanded-models.md#claude-3-5-sonnet-20241022`; release 2024-10-22 supported by [release source](https://github.com/METR/eval-analysis-public/blob/52cb829c7a2efb2d659285c4b1768d191d97f8d2/data/external/release_dates.yaml). Input tokenizer is cl100k_base as an explicit proxy, not an assertion about the proprietary Claude vocabulary.


## reas-epoch-gpqa-sonnet35-1022

Work unit and human baseline: [gpqa](gpqa.md). Source row: Identifier `claude-3-5-sonnet-20241022`, Benchmark `GPQA diamond` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.553030303; classification above versus human target 0.2205387205. Mean output 353.904040404; input 269.813131313 (cl100k); total 623.717171717 tokens/question × 200000000000 FLOPs/token = 1.24743434343e+14 FLOPs/question. A ±50% input estimate changes total compute by ±21.6%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-mathl5-sonnet35-1022

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `claude-3-5-sonnet-20241022`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.5694864048; classification below versus human target 0.9. Mean output 450.567220544; input 135.99244713 (cl100k); total 586.559667674 tokens/question × 200000000000 FLOPs/token = 1.17311933535e+14 FLOPs/question. A ±50% input estimate changes total compute by ±11.6%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-otis-sonnet35-1022

Original Epoch table: Identifier `claude-3-5-sonnet-20241022`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 593.111111111. Input under `cl100k` = 187.2. Total = 780.311111111 text tokens × 200000000000 FLOPs/token = **1.56062222222e+14 FLOPs**.

Work unit and human baseline: [OTIS](otis.md). AI accuracy 8.47222%. Original human contest score frequencies imply 51.5507% under equal weighting of the three papers. Current input reconstruction and tokenizer qualification: [OTIS correction](epoch-otis-input-correction.md#reas-epoch-otis-sonnet35-1022).

## Model: claude-3-7-sonnet

Previously reviewed assumed active parameters: 1e+11; coefficient 2P = 2e+11 FLOPs/token. Shared parameter-source locator: `research/metr/metr-expanded-models.md#claude-3-7-sonnet`; release 2025-02-24 supported by [release source](https://github.com/METR/eval-analysis-public/blob/52cb829c7a2efb2d659285c4b1768d191d97f8d2/data/external/release_dates.yaml). Input tokenizer is cl100k_base as an explicit proxy, not an assertion about the proprietary Claude vocabulary.


## reas-epoch-gpqa-sonnet37

Work unit and human baseline: [gpqa](gpqa.md). Source row: Identifier `claude-3-7-sonnet-20250219`, Benchmark `GPQA diamond` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.6603535354; classification above versus human target 0.2205387205. Mean output 591.48989899; input 269.813131313 (cl100k); total 861.303030303 tokens/question × 200000000000 FLOPs/token = 1.72260606061e+14 FLOPs/question. A ±50% input estimate changes total compute by ±15.7%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-mathl5-sonnet37

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `claude-3-7-sonnet-20250219`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.6818353474; classification below versus human target 0.9. Mean output 823.406344411; input 135.99244713 (cl100k); total 959.398791541 tokens/question × 200000000000 FLOPs/token = 1.91879758308e+14 FLOPs/question. A ±50% input estimate changes total compute by ±7.09%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-otis-sonnet37

Original Epoch table: Identifier `claude-3-7-sonnet-20250219`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 1435.64444444. Input under `cl100k` = 187.2. Total = 1622.84444444 text tokens × 200000000000 FLOPs/token = **3.24568888889e+14 FLOPs**.

Work unit and human baseline: [OTIS](otis.md). AI accuracy 21.9444%. Original human contest score frequencies imply 51.5507% under equal weighting of the three papers. Current input reconstruction and tokenizer qualification: [OTIS correction](epoch-otis-input-correction.md#reas-epoch-otis-sonnet37).

## Model: claude-3-7-sonnet

Previously reviewed assumed active parameters: 1e+11; coefficient 2P = 2e+11 FLOPs/token. Shared parameter-source locator: `research/metr/metr-expanded-models.md#claude-3-7-sonnet`; release 2025-02-24 supported by [release source](https://github.com/METR/eval-analysis-public/blob/52cb829c7a2efb2d659285c4b1768d191d97f8d2/data/external/release_dates.yaml). Input tokenizer is cl100k_base as an explicit proxy, not an assertion about the proprietary Claude vocabulary.


## reas-epoch-gpqa-sonnet37-64k

Work unit and human baseline: [gpqa](gpqa.md). Source row: Identifier `claude-3-7-sonnet-20250219_64K`, Benchmark `GPQA diamond` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.7727272727; classification above versus human target 0.2205387205. Mean output 13013.4949495; input 269.813131313 (cl100k); total 13283.3080808 tokens/question × 200000000000 FLOPs/token = 2.65666161616e+15 FLOPs/question. A ±50% input estimate changes total compute by ±1.02%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-mathl5-sonnet37-64k

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `claude-3-7-sonnet-20250219_64K`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.9116314199; classification match versus human target 0.9. Mean output 13666.9070997; input 135.99244713 (cl100k); total 13802.8995468 tokens/question × 200000000000 FLOPs/token = 2.76057990937e+15 FLOPs/question. A ±50% input estimate changes total compute by ±0.493%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-otis-sonnet37-64k

Original Epoch table: Identifier `claude-3-7-sonnet-20250219_64K`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 26990.1333333. Input under `cl100k` = 187.2. Total = 27177.3333333 text tokens × 200000000000 FLOPs/token = **5.43546666667e+15 FLOPs**.

Work unit and human baseline: [OTIS](otis.md). AI accuracy 57.7778%. Original human contest score frequencies imply 51.5507% under equal weighting of the three papers. Current input reconstruction and tokenizer qualification: [OTIS correction](epoch-otis-input-correction.md#reas-epoch-otis-sonnet37-64k).

