# Epoch Mistral-family observations

Original source output-table means and exact source accuracy are paired with the reviewed GPQA/MATH/OTIS human recipes. Full-question GPQA/MATH input reconstruction uses original Mistral v0.3 and NeMo tokenizer files where exact, and expressly disclosed family proxies for other models; historical wrappers add the reviewed 12 or 50 positions. OTIS uses the recovered 45 question texts with the retained tokenizer or explicit proxy, the recovered short instruction and 12 assumed chat positions; see [the input correction](epoch-otis-input-correction.md). Input sensitivity appears per point. No prior estimates are used for new model parameters or dates.

All new model counts are provider-reported rounded values. Mistral Large 2407/2411 are dense 123B models. Small 2501/2503 use reported 24B; these are text-input workloads and no separate image-processing work is added. Ministral uses reported 3B/8B, NeMo 12B, Mistral v0.3 7B. Mixtral uses **active** parameters, 12.9B for 8x7B (more precise original launch announcement; paper abstract rounds to 13B) and 39B for 8x22B (official model table), rather than all experts.

Release dates describe instructed/API availability: Mixtral 8x7B December 11, 2023 and 8x22B April 17, 2024. Earlier base-weight releases are not used for the instructed benchmark configuration. Mistral v0.3 official lifecycle page gives May 22, 2024; the original weight upload and public Hugging Face staff discussion corroborate same-day availability. Mistral Large 2411 uses the dated November 18 official API changelog. Other dates use original announcements.

Ministral date conflict: the [contemporaneous announcement](https://mistral.ai/news/ministraux/) is dated October 16, 2024 and states both models become available that day, whereas the [official changelog](https://docs.mistral.ai/resources/changelogs) places them under October 9. October 16 is retained as the clearer contemporaneous public-availability evidence.

Tokenizer provenance: `agent-work/sources/epoch/mistral3-tokenizer.json` is byte-identical to the [original immutable repository file](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3/resolve/c170c708c41dac9275d15a8fff4eca08d52bab71/tokenizer.json); revision `c170c708c41dac9275d15a8fff4eca08d52bab71`, SHA-256 `e553af6fff7d7ad76e830608b218c5c0b0822998d5a1a96099a74cd3c1cb1a49`. These revisions identify the verified files, not a claim that every historical hosted model used this tokenizer.

Tokenizer provenance: `agent-work/sources/epoch/nemo-tokenizer.json` is byte-identical to the [original immutable repository file](https://huggingface.co/mistralai/Mistral-Nemo-Instruct-2407/resolve/04d8a90549d23fc6bd7f642064003592df51e9b3/tokenizer.json); revision `04d8a90549d23fc6bd7f642064003592df51e9b3`, SHA-256 `e11c71726323d33da7b8d6f6f269f1988931c0a52b7122bcdd8c05042974e0db`. These revisions identify the verified files, not a claim that every historical hosted model used this tokenizer.


## Model: mistral-large-2407

Reported active parameters: 1.23e+11; coefficient 2P = 2.46e+11 FLOPs/token. [Architecture/model card](https://huggingface.co/mistralai/Mistral-Large-Instruct-2407); release 2024-07-24 supported by [release source](https://mistral.ai/news/mistral-large-2407/). Input tokenizer is the original Mistral 7B v0.3 vocabulary used as an explicit family proxy; historical provider vocabulary/wrapper accounting is not claimed identical.


## reas-epoch-gpqa-mistrallarge2407

Work unit and human baseline: [gpqa](gpqa.md). Source row: Identifier `mistral-large-2407`, Benchmark `GPQA diamond` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.4902146465; classification above versus human target 0.2205387205. Mean output 475.46969697; input 302.101010101 (mistral3); total 777.570707071 tokens/question × 246000000000 FLOPs/token = 1.91282393939e+14 FLOPs/question. A ±50% input estimate changes total compute by ±19.4%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-mathl5-mistrallarge2407

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `mistral-large-2407`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.448168429; classification below versus human target 0.9. Mean output 567.497734139; input 143.9418429 (mistral3); total 711.439577039 tokens/question × 246000000000 FLOPs/token = 1.75014135952e+14 FLOPs/question. A ±50% input estimate changes total compute by ±10.1%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-otis-mistrallarge2407

Original Epoch table: Identifier `mistral-large-2407`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 894.555555556. Input under `mistral3` = 207.822222222. Total = 1102.37777778 text tokens × 246000000000 FLOPs/token = **2.71184933333e+14 FLOPs**.

Work unit and human baseline: [OTIS](otis.md). AI accuracy 8.47222%. Original human contest score frequencies imply 51.5507% under equal weighting of the three papers. Current input reconstruction and tokenizer qualification: [OTIS correction](epoch-otis-input-correction.md#reas-epoch-otis-mistrallarge2407).

## Model: mistral-large-2411

Reported active parameters: 1.23e+11; coefficient 2P = 2.46e+11 FLOPs/token. [Architecture/model card](https://huggingface.co/mistralai/Mistral-Large-Instruct-2411); release 2024-11-18 supported by [release source](https://docs.mistral.ai/resources/changelogs). Input tokenizer is the original Mistral 7B v0.3 vocabulary used as an explicit family proxy; historical provider vocabulary/wrapper accounting is not claimed identical.


## reas-epoch-gpqa-mistrallarge2411

Work unit and human baseline: [gpqa](gpqa.md). Source row: Identifier `mistral-large-2411`, Benchmark `GPQA diamond` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.5132575758; classification above versus human target 0.2205387205. Mean output 582.106060606; input 302.101010101 (mistral3); total 884.207070707 tokens/question × 246000000000 FLOPs/token = 2.17514939394e+14 FLOPs/question. A ±50% input estimate changes total compute by ±17.1%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-mathl5-mistrallarge2411

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `mistral-large-2411`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.5028323263; classification below versus human target 0.9. Mean output 651.968277946; input 143.9418429 (mistral3); total 795.910120846 tokens/question × 246000000000 FLOPs/token = 1.95793889728e+14 FLOPs/question. A ±50% input estimate changes total compute by ±9.04%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-otis-mistrallarge2411

Original Epoch table: Identifier `mistral-large-2411`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 938.044444444. Input under `mistral3` = 207.822222222. Total = 1145.86666667 text tokens × 246000000000 FLOPs/token = **2.818832e+14 FLOPs**.

Work unit and human baseline: [OTIS](otis.md). AI accuracy 7.77778%. Original human contest score frequencies imply 51.5507% under equal weighting of the three papers. Current input reconstruction and tokenizer qualification: [OTIS correction](epoch-otis-input-correction.md#reas-epoch-otis-mistrallarge2411).

## Model: mistral-small-2501

Reported active parameters: 2.4e+10; coefficient 2P = 4.8e+10 FLOPs/token. [Architecture/model card](https://mistral.ai/news/mistral-small-3/); release 2025-01-30 supported by [release source](https://mistral.ai/news/mistral-small-3/). Input tokenizer is the original Mistral NeMo vocabulary used as an explicit family proxy; historical provider vocabulary/wrapper accounting is not claimed identical.


## reas-epoch-gpqa-mistralsmall2501

Work unit and human baseline: [gpqa](gpqa.md). Source row: Identifier `mistral-small-2501`, Benchmark `GPQA diamond` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.4529671717; classification above versus human target 0.2205387205. Mean output 532.439393939; input 268.247474747 (nemo); total 800.686868687 tokens/question × 48000000000 FLOPs/token = 3.8432969697e+13 FLOPs/question. A ±50% input estimate changes total compute by ±16.8%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-mathl5-mistralsmall2501

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `mistral-small-2501`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.448168429; classification below versus human target 0.9. Mean output 619.927492447; input 136.972054381 (nemo); total 756.899546828 tokens/question × 48000000000 FLOPs/token = 3.63311782477e+13 FLOPs/question. A ±50% input estimate changes total compute by ±9.05%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-otis-mistralsmall2501

Original Epoch table: Identifier `mistral-small-2501`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 883.177777778. Input under `nemo` = 194.533333333. Total = 1077.71111111 text tokens × 48000000000 FLOPs/token = **5.17301333333e+13 FLOPs**.

Work unit and human baseline: [OTIS](otis.md). AI accuracy 5.27778%. Original human contest score frequencies imply 51.5507% under equal weighting of the three papers. Current input reconstruction and tokenizer qualification: [OTIS correction](epoch-otis-input-correction.md#reas-epoch-otis-mistralsmall2501).

## Model: mistral-small-2503

Reported active parameters: 2.4e+10; coefficient 2P = 4.8e+10 FLOPs/token. [Architecture/model card](https://huggingface.co/mistralai/Mistral-Small-3.1-24B-Instruct-2503); release 2025-03-17 supported by [release source](https://mistral.ai/news/mistral-small-3-1/). Input tokenizer is the original Mistral NeMo vocabulary used as an explicit family proxy; historical provider vocabulary/wrapper accounting is not claimed identical.


## reas-epoch-gpqa-mistralsmall2503

Work unit and human baseline: [gpqa](gpqa.md). Source row: Identifier `mistral-small-2503`, Benchmark `GPQA diamond` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.4747474747; classification above versus human target 0.2205387205. Mean output 495.424242424; input 268.247474747 (nemo); total 763.671717172 tokens/question × 48000000000 FLOPs/token = 3.66562424242e+13 FLOPs/question. A ±50% input estimate changes total compute by ±17.6%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-mathl5-mistralsmall2503

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `mistral-small-2503`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.4677114804; classification below versus human target 0.9. Mean output 659.287009063; input 136.972054381 (nemo); total 796.259063444 tokens/question × 48000000000 FLOPs/token = 3.82204350453e+13 FLOPs/question. A ±50% input estimate changes total compute by ±8.6%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## reas-epoch-otis-mistralsmall2503

Original Epoch table: Identifier `mistral-small-2503`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 854.488888889. Input under `nemo` = 194.533333333. Total = 1049.02222222 text tokens × 48000000000 FLOPs/token = **5.03530666667e+13 FLOPs**.

Work unit and human baseline: [OTIS](otis.md). AI accuracy 5.83333%. Original human contest score frequencies imply 51.5507% under equal weighting of the three papers. Current input reconstruction and tokenizer qualification: [OTIS correction](epoch-otis-input-correction.md#reas-epoch-otis-mistralsmall2503).

## Model: ministral-3b-2410

Reported active parameters: 3e+09; coefficient 2P = 6e+09 FLOPs/token. [Architecture/model card](https://mistral.ai/news/ministraux/); release 2024-10-16 supported by [release source](https://mistral.ai/news/ministraux/). Input tokenizer is the original Mistral NeMo vocabulary used as an explicit family proxy; historical provider vocabulary/wrapper accounting is not claimed identical.


## reas-epoch-mathl5-ministral3b

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `ministral-3b-2410`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.1444486405; classification below versus human target 0.9. Mean output 655.156344411; input 136.972054381 (nemo); total 792.128398792 tokens/question × 6000000000 FLOPs/token = 4.75277039275e+12 FLOPs/question. A ±50% input estimate changes total compute by ±8.65%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## Model: ministral-8b-2410

Reported active parameters: 8e+09; coefficient 2P = 1.6e+10 FLOPs/token. [Architecture/model card](https://mistral.ai/news/ministraux/); release 2024-10-16 supported by [release source](https://mistral.ai/news/ministraux/). Input tokenizer is the original Mistral NeMo vocabulary used as an explicit family proxy; historical provider vocabulary/wrapper accounting is not claimed identical.


## reas-epoch-mathl5-ministral8b

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `ministral-8b-2410`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.149358006; classification below versus human target 0.9. Mean output 618.10347432; input 136.972054381 (nemo); total 755.075528701 tokens/question × 16000000000 FLOPs/token = 1.20812084592e+13 FLOPs/question. A ±50% input estimate changes total compute by ±9.07%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## Model: mistral-nemo-2407

Reported active parameters: 1.2e+10; coefficient 2P = 2.4e+10 FLOPs/token. [Architecture/model card](https://mistral.ai/news/mistral-nemo/); release 2024-07-18 supported by [release source](https://mistral.ai/news/mistral-nemo/). Input tokenizer is the original Mistral NeMo vocabulary; historical provider wrapper positions remain assumed.


## reas-epoch-mathl5-mistralnemo

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `open-mistral-nemo-2407`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.1082892749; classification below versus human target 0.9. Mean output 521.993202417; input 136.972054381 (nemo); total 658.965256798 tokens/question × 24000000000 FLOPs/token = 1.58151661631e+13 FLOPs/question. A ±50% input estimate changes total compute by ±10.4%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## Model: mistral-7b-instruct-v0.3

Reported active parameters: 7e+09; coefficient 2P = 1.4e+10 FLOPs/token. [Architecture/model card](https://docs.mistral.ai/models/mistral-7b-0-3); release 2024-05-22 supported by [release source](https://docs.mistral.ai/models/mistral-7b-0-3). Input tokenizer is the original Mistral 7B v0.3 vocabulary; historical provider wrapper positions remain assumed.


## reas-epoch-mathl5-mistral7b

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `Mistral-7B-Instruct-v0.3`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.03597054381; classification below versus human target 0.9. Mean output 650.420694864; input 143.9418429 (mistral3); total 794.362537764 tokens/question × 14000000000 FLOPs/token = 1.11210755287e+13 FLOPs/question. A ±50% input estimate changes total compute by ±9.06%; no claim this is a confidence interval. The model coefficient and its sources appear above.


## Model: mixtral-8x7b-instruct-v0.1

Reported active parameters: 1.29e+10; coefficient 2P = 2.58e+10 FLOPs/token. [Architecture/model card](https://mistral.ai/news/mixtral-of-experts/); release 2023-12-11 supported by [release source](https://mistral.ai/news/mixtral-of-experts/). Input uses the named Mixtral v0.1 repository vocabulary; the historical serving wrapper remains assumed.


## reas-epoch-mathl5-mixtral8x7b

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `Mixtral-8x7B-Instruct-v0.1`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.09290030211; classification below versus human target 0.9. Mean output 512.561178248; input 143.9418429 (original Mixtral 8x7B); total 656.503021148 tokens/question × 25800000000 FLOPs/token = 1.69377779456e+13 FLOPs/question. A ±50% input estimate changes total compute by ±11%; this is a sensitivity scenario. [Tokenizer provenance and calculation](../tokenizer-family-correction/tokenizer-family-correction.md#reas-epoch-mathl5-mixtral8x7b).


## Model: mixtral-8x22b-instruct-v0.1

Reported active parameters: 3.9e+10; coefficient 2P = 7.8e+10 FLOPs/token. [Architecture/model card](https://docs.mistral.ai/models/mixtral-8x22b-0-1-0-3); release 2024-04-17 supported by [release source](https://docs.mistral.ai/models/mixtral-8x22b-0-1-0-3). Input uses the named Mixtral v0.1 repository vocabulary; the historical serving wrapper remains assumed.


## reas-epoch-gpqa-mixtral8x22b

Work unit and human baseline: [gpqa](gpqa.md). Source row: Identifier `open-mixtral-8x22b`, Benchmark `GPQA diamond` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.3405934343; classification above versus human target 0.2205387205. Mean output 544.065656566; input 302.101010101 (original Mixtral 8x22B); total 846.166666667 tokens/question × 78000000000 FLOPs/token = 6.6001e+13 FLOPs/question. A ±50% input estimate changes total compute by ±17.9%; this is a sensitivity scenario. [Tokenizer provenance and calculation](../tokenizer-family-correction/tokenizer-family-correction.md#reas-epoch-gpqa-mixtral8x22b).


## reas-epoch-mathl5-mixtral8x22b

Work unit and human baseline: [mathl5](mathl5.md). Source row: Identifier `open-mixtral-8x22b`, Benchmark `MATH level 5` in [Epoch source](https://epoch.ai/data-insights/output-length). AI accuracy 0.2424471299; classification below versus human target 0.9. Mean output 689.314199396; input 143.9418429 (original Mixtral 8x22B); total 833.256042296 tokens/question × 78000000000 FLOPs/token = 6.49939712991e+13 FLOPs/question. A ±50% input estimate changes total compute by ±8.64%; this is a sensitivity scenario. [Tokenizer provenance and calculation](../tokenizer-family-correction/tokenizer-family-correction.md#reas-epoch-mathl5-mixtral8x22b).
