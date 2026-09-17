# OTIS: replacing the fixed input estimate

This correction replaces the 200-token input assumption in 45 previously incorporated output-table points with counts of the original 45 question texts. Reported output, model coefficients, human time, performance, configuration and native-counter points are unchanged. Full source extraction and Google tokenizer evidence are described in [the Gemini table reconstruction](epoch-gemini-table.md#input-reconstruction).

Each input is the original question plus the short instruction to work step by step and end with an integer answer, recovered from a later original Epoch run, plus 12 assumed chat positions. The historical runs may have used a different wrapper. This is a reconstruction of the same task content, not a claim of recovered historical usage. Every question contributes once to an equal-question mean.

To isolate this correction, the tokenizer or explicit proxy already selected for each model’s GPQA/MATH reconstruction is reused: OpenAI cl100k/o200k, retained model tokenizers, and existing Mistral/Claude/Gemini proxies. Anthropic’s legacy tokenizer uses its original NFKC normalization. The choice of proxy is not new evidence of the hosted model’s vocabulary. These counts can later be refined independently of recovering the question content.

Formula: new tokens = source mean output + reconstructed input mean; new FLOPs = new tokens × the existing shared coefficient. Source outputs are rechecked against exact identifier/benchmark pairs in the original scatter_data.csv. Every old row is checked against source output + 200. The resulting FLOP changes range from −1.936% to +0.865%.

`agent-work/sources/epoch/otis-input-correction/deltas.csv` and `deltas.json` provide all IDs, old/new inputs, tokens, FLOPs and changes. `input-counts.json` stores all 45 counts per tokenizer plus hashes. `field-changes.json` limits a proposed patch to tokens, compute_flops, compute_source and notes and carries old-value guards; it does not apply the patch. The first production values are retained in original-points.csv.

Gemma 2 now uses the original shared Google vocabulary: mean input 194.6 tokens. The archived correction files below retain their original NeMo-proxy calculation; [the current tokenizer reconstruction](../tokenizer-family-correction/tokenizer-family-correction.md) supplies the Gemma 2 refinement. Other entries in this note retain their stated tokenizers.

## Input means

| Tokenizer or proxy | Reconstructed input mean |
|---|---:|
| cl100k | 187.2 |
| deepseek | 184.311111111 |
| hermes70 | 187.155555556 |
| llama | 187.155555556 |
| llama31 | 187.155555556 |
| mistral3 | 207.822222222 |
| nemo | 194.533333333 |
| o200k | 186.6 |
| phi4 | 187.2 |
| qwen | 195.288888889 |
| r1distill | 187.155555556 |
| tulu3 | 187.155555556 |
| three_tokenizer_mean | 193.874074074 |
| claude_legacy | 189.088888889 |

## reas-epoch-otis-llama3-70b

Original Epoch table: Identifier `Meta-Llama-3-70B-Instruct`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 705.266666667. Input under `llama` = 187.155555556. Total = 892.422222222 text tokens × 140000000000 FLOPs/token = **1.24939111111e+14 FLOPs**. The prior value was 1.26737333333e+14; change -1.419%.


## reas-epoch-otis-qwen25-32b

Original Epoch table: Identifier `qwen2.5-32b-instruct`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 841.755555556. Input under `qwen` = 195.288888889. Total = 1037.04444444 text tokens × 65000000000 FLOPs/token = **6.74078888889e+13 FLOPs**. The prior value was 6.77141111111e+13; change -0.4522%.


## reas-epoch-otis-v3-0324

Original Epoch table: Identifier `DeepSeek-V3-0324`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 3179. Input under `deepseek` = 184.311111111. Total = 3363.31111111 text tokens × 74000000000 FLOPs/token = **2.48885022222e+14 FLOPs**. The prior value was 2.50046e+14; change -0.4643%.


## reas-epoch-otis-llama3-8b

Original Epoch table: Identifier `Meta-Llama-3-8B-Instruct`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 645.111111111. Input under `llama` = 187.155555556. Total = 832.266666667 text tokens × 16000000000 FLOPs/token = **1.33162666667e+13 FLOPs**. The prior value was 1.35217777778e+13; change -1.52%.


## reas-epoch-otis-llama33-70b

Original Epoch table: Identifier `Llama-3.3-70B-Instruct`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 1157.04444444. Input under `llama31` = 187.155555556. Total = 1344.2 text tokens × 140000000000 FLOPs/token = **1.88188e+14 FLOPs**. The prior value was 1.89986222222e+14; change -0.9465%.


## reas-epoch-otis-llama4-scout

Original Epoch table: Identifier `Llama-4-Scout-17B-16E-Instruct`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 1435.46666667. Input under `llama31` = 187.155555556. Total = 1622.62222222 text tokens × 34000000000 FLOPs/token = **5.51691555556e+13 FLOPs**. The prior value was 5.56058666667e+13; change -0.7854%.


## reas-epoch-otis-llama4-maverick

Original Epoch table: Identifier `Llama-4-Maverick-17B-128E-Instruct-FP8`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 1312.66666667. Input under `llama31` = 187.155555556. Total = 1499.82222222 text tokens × 34000000000 FLOPs/token = **5.09939555556e+13 FLOPs**. The prior value was 5.14306666667e+13; change -0.8491%.


## reas-epoch-otis-qwen25-72b

Original Epoch table: Identifier `qwen2.5-72b-instruct`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 992.266666667. Input under `qwen` = 195.288888889. Total = 1187.55555556 text tokens × 145400000000 FLOPs/token = **1.72670577778e+14 FLOPs**. The prior value was 1.73355573333e+14; change -0.3951%.


## reas-epoch-otis-v3

Original Epoch table: Identifier `DeepSeek-V3`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 1865.82222222. Input under `deepseek` = 184.311111111. Total = 2050.13333333 text tokens × 74000000000 FLOPs/token = **1.51709866667e+14 FLOPs**. The prior value was 1.52870844444e+14; change -0.7595%.


## reas-epoch-otis-r1distill70b

Original Epoch table: Identifier `DeepSeek-R1-Distill-Llama-70B`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 16154.7333333. Input under `r1distill` = 187.155555556. Total = 16341.8888889 text tokens × 140000000000 FLOPs/token = **2.28786444444e+15 FLOPs**. The prior value was 2.28966266667e+15; change -0.07854%.


## reas-epoch-otis-phi4

Original Epoch table: Identifier `phi-4`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 1243.97777778. Input under `phi4` = 187.2. Total = 1431.17777778 text tokens × 28000000000 FLOPs/token = **4.00729777778e+13 FLOPs**. The prior value was 4.04313777778e+13; change -0.8864%.


## reas-epoch-otis-gpt4o-0806

Original Epoch table: Identifier `gpt-4o-2024-08-06`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 835.666666667. Input under `o200k` = 186.6. Total = 1022.26666667 text tokens × 100000000000 FLOPs/token = **1.02226666667e+14 FLOPs**. The prior value was 1.03566666667e+14; change -1.294%.


## reas-epoch-otis-sonnet35-1022

Original Epoch table: Identifier `claude-3-5-sonnet-20241022`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 593.111111111. Input under `cl100k` = 187.2. Total = 780.311111111 text tokens × 200000000000 FLOPs/token = **1.56062222222e+14 FLOPs**. The prior value was 1.58622222222e+14; change -1.614%.


## reas-epoch-otis-sonnet37

Original Epoch table: Identifier `claude-3-7-sonnet-20250219`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 1435.64444444. Input under `cl100k` = 187.2. Total = 1622.84444444 text tokens × 200000000000 FLOPs/token = **3.24568888889e+14 FLOPs**. The prior value was 3.27128888889e+14; change -0.7826%.


## reas-epoch-otis-sonnet37-64k

Original Epoch table: Identifier `claude-3-7-sonnet-20250219_64K`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 26990.1333333. Input under `cl100k` = 187.2. Total = 27177.3333333 text tokens × 200000000000 FLOPs/token = **5.43546666667e+15 FLOPs**. The prior value was 5.43802666667e+15; change -0.04708%.


## reas-epoch-otis-mistrallarge2407

Original Epoch table: Identifier `mistral-large-2407`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 894.555555556. Input under `mistral3` = 207.822222222. Total = 1102.37777778 text tokens × 246000000000 FLOPs/token = **2.71184933333e+14 FLOPs**. The prior value was 2.69260666667e+14; change 0.7146%.


## reas-epoch-otis-mistrallarge2411

Original Epoch table: Identifier `mistral-large-2411`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 938.044444444. Input under `mistral3` = 207.822222222. Total = 1145.86666667 text tokens × 246000000000 FLOPs/token = **2.818832e+14 FLOPs**. The prior value was 2.79958933333e+14; change 0.6873%.


## reas-epoch-otis-mistralsmall2501

Original Epoch table: Identifier `mistral-small-2501`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 883.177777778. Input under `nemo` = 194.533333333. Total = 1077.71111111 text tokens × 48000000000 FLOPs/token = **5.17301333333e+13 FLOPs**. The prior value was 5.19925333333e+13; change -0.5047%.


## reas-epoch-otis-mistralsmall2503

Original Epoch table: Identifier `mistral-small-2503`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 854.488888889. Input under `nemo` = 194.533333333. Total = 1049.02222222 text tokens × 48000000000 FLOPs/token = **5.03530666667e+13 FLOPs**. The prior value was 5.06154666667e+13; change -0.5184%.


## reas-epoch-otis-gemma2-9b

Original Epoch table: Identifier `gemma-2-9b-it`, Benchmark `OTIS Mock AIME 2024-2025`. Retained output 567.6 + input 194.6 using the original shared Gemma vocabulary = 762.2 text tokens. At 18484329472 FLOPs/token: **1.40887559236e+13 FLOPs**. [Tokenizer provenance and calculation](../tokenizer-family-correction/tokenizer-family-correction.md#reas-epoch-otis-gemma2-9b).


## reas-epoch-otis-gemma2-27b

Original Epoch table: Identifier `gemma-2-27b-it`, Benchmark `OTIS Mock AIME 2024-2025`. Retained output 707.377777778 + input 194.6 using the original shared Gemma vocabulary = 901.977777778 text tokens. At 54455436288 FLOPs/token: **4.9117593411e+13 FLOPs**. [Tokenizer provenance and calculation](../tokenizer-family-correction/tokenizer-family-correction.md#reas-epoch-otis-gemma2-27b).


## reas-epoch-otis-gemma3-27b

Original Epoch table: Identifier `gemma-3-27b-it`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 3147.28888889. Input under `nemo` = 194.533333333. Total = 3341.82222222 text tokens × 54032000000 FLOPs/token = **1.80565338311e+14 FLOPs**. The prior value was 1.80860713244e+14; change -0.1633%.


## reas-epoch-otis-tulu3-70b

Original Epoch table: Identifier `Llama-3.1-Tulu-3-70B-DPO`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 970.866666667. Input under `tulu3` = 187.155555556. Total = 1158.02222222 text tokens × 140000000000 FLOPs/token = **1.62123111111e+14 FLOPs**. The prior value was 1.63921333333e+14; change -1.097%.


## reas-epoch-otis-gpt4turbo

Original Epoch table: Identifier `gpt-4-turbo-2024-04-09`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 751.777777778. Input under `cl100k` = 187.2. Total = 938.977777778 text tokens × 550000000000 FLOPs/token = **5.16437777778e+14 FLOPs**. The prior value was 5.23477777778e+14; change -1.345%.


## reas-epoch-otis-gpt4o-0513

Original Epoch table: Identifier `gpt-4o-2024-05-13`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 735.666666667. Input under `o200k` = 186.6. Total = 922.266666667 text tokens × 100000000000 FLOPs/token = **9.22266666667e+13 FLOPs**. The prior value was 9.35666666667e+13; change -1.432%.


## reas-epoch-otis-gpt4o-1120

Original Epoch table: Identifier `gpt-4o-2024-11-20`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 990.822222222. Input under `o200k` = 186.6. Total = 1177.42222222 text tokens × 100000000000 FLOPs/token = **1.17742222222e+14 FLOPs**. The prior value was 1.19082222222e+14; change -1.125%.


## reas-epoch-otis-llama32-90b

Original Epoch table: Identifier `Llama-3.2-90B-Vision-Instruct`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 1155.2. Input under `tulu3` = 187.155555556. Total = 1342.35555556 text tokens × 140000000000 FLOPs/token = **1.87929777778e+14 FLOPs**. The prior value was 1.89728e+14; change -0.9478%.


## reas-epoch-otis-gpt41

Original Epoch table: Identifier `gpt-4.1-2025-04-14`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 3812.11111111. Input under `o200k` = 186.6. Total = 3998.71111111 text tokens × 100000000000 FLOPs/token = **3.99871111111e+14 FLOPs**. The prior value was 4.01211111111e+14; change -0.334%.


## reas-epoch-otis-hermes70b

Original Epoch table: Identifier `Hermes-2-Theta-Llama-3-70B`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 700.777777778. Input under `hermes70` = 187.155555556. Total = 887.933333333 text tokens × 140000000000 FLOPs/token = **1.24310666667e+14 FLOPs**. The prior value was 1.26108888889e+14; change -1.426%.


## reas-epoch-otis-o1med

Original Epoch table: Identifier `o1-2024-12-17_medium`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 10844.8666667. Input under `o200k` = 186.6. Total = 11031.4666667 text tokens × 100000000000 FLOPs/token = **1.10314666667e+15 FLOPs**. The prior value was 1.10448666667e+15; change -0.1213%.


## reas-epoch-otis-o1prev

Original Epoch table: Identifier `o1-preview-2024-09-12`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 8307.64444444. Input under `o200k` = 186.6. Total = 8494.24444444 text tokens × 100000000000 FLOPs/token = **8.49424444444e+14 FLOPs**. The prior value was 8.50764444444e+14; change -0.1575%.


## reas-epoch-otis-o1mini

Original Epoch table: Identifier `o1-mini-2024-09-12_high`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 8013.35555556. Input under `o200k` = 186.6. Total = 8199.95555556 text tokens × 40000000000 FLOPs/token = **3.27998222222e+14 FLOPs**. The prior value was 3.28534222222e+14; change -0.1631%.


## reas-epoch-otis-o3mini

Original Epoch table: Identifier `o3-mini-2025-01-31_high`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 12818.8. Input under `o200k` = 186.6. Total = 13005.4 text tokens × 40000000000 FLOPs/token = **5.20216e+14 FLOPs**. The prior value was 5.20752e+14; change -0.1029%.


## reas-epoch-otis-o4mini

Original Epoch table: Identifier `o4-mini-2025-04-16_high`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 14084.2. Input under `o200k` = 186.6. Total = 14270.8 text tokens × 40000000000 FLOPs/token = **5.70832e+14 FLOPs**. The prior value was 5.71368e+14; change -0.09381%.


## reas-epoch-otis-claude2

Original Epoch table: Identifier `claude-2.0`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 363.666666667. Input under `claude_legacy` = 189.088888889. Total = 552.755555556 text tokens × 200000000000 FLOPs/token = **1.10551111111e+14 FLOPs**. The prior value was 1.12733333333e+14; change -1.936%.


## reas-epoch-otis-claude21

Original Epoch table: Identifier `claude-2.1`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 366.266666667. Input under `claude_legacy` = 189.088888889. Total = 555.355555556 text tokens × 200000000000 FLOPs/token = **1.11071111111e+14 FLOPs**. The prior value was 1.13253333333e+14; change -1.927%.


## reas-epoch-otis-haiku3

Original Epoch table: Identifier `claude-3-haiku-20240307`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 566.711111111. Input under `claude_legacy` = 189.088888889. Total = 755.8 text tokens × 40000000000 FLOPs/token = **3.0232e+13 FLOPs**. The prior value was 3.06684444444e+13; change -1.423%.


## reas-epoch-otis-haiku35

Original Epoch table: Identifier `claude-3-5-haiku-20241022`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 561.044444444. Input under `claude_legacy` = 189.088888889. Total = 750.133333333 text tokens × 40000000000 FLOPs/token = **3.00053333333e+13 FLOPs**. The prior value was 3.04417777778e+13; change -1.434%.


## reas-epoch-otis-opus3

Original Epoch table: Identifier `claude-3-opus-20240229`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 581.466666667. Input under `claude_legacy` = 189.088888889. Total = 770.555555556 text tokens × 360000000000 FLOPs/token = **2.774e+14 FLOPs**. The prior value was 2.81328e+14; change -1.396%.


## reas-epoch-otis-sonnet3

Original Epoch table: Identifier `claude-3-sonnet-20240229`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 592.977777778. Input under `claude_legacy` = 189.088888889. Total = 782.066666667 text tokens × 200000000000 FLOPs/token = **1.56413333333e+14 FLOPs**. The prior value was 1.58595555556e+14; change -1.376%.


## reas-epoch-otis-sonnet35-0620

Original Epoch table: Identifier `claude-3-5-sonnet-20240620`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 555.555555556. Input under `claude_legacy` = 189.088888889. Total = 744.644444444 text tokens × 200000000000 FLOPs/token = **1.48928888889e+14 FLOPs**. The prior value was 1.51111111111e+14; change -1.444%.


## reas-epoch-otis-gpt41mini

Original Epoch table: Identifier `gpt-4.1-mini-2025-04-14`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 5239.13333333. Input under `o200k` = 186.6. Total = 5425.73333333 text tokens × 48000000000 FLOPs/token = **2.604352e+14 FLOPs**. The prior value was 2.610784e+14; change -0.2464%.


## reas-epoch-otis-gpt41nano

Original Epoch table: Identifier `gpt-4.1-nano-2025-04-14`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 3399.26666667. Input under `o200k` = 186.6. Total = 3585.86666667 text tokens × 16000000000 FLOPs/token = **5.73738666667e+13 FLOPs**. The prior value was 5.75882666667e+13; change -0.3723%.


## reas-epoch-otis-mistrallarge2402

Original Epoch table: Identifier `mistral-large-2402`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 703.888888889. Input under `mistral3` = 207.822222222. Total = 911.711111111 text tokens × 246000000000 FLOPs/token = **2.24280933333e+14 FLOPs**. The prior value was 2.22356666667e+14; change 0.8654%.


## reas-epoch-otis-gemini15flash8b

Original Epoch table: Identifier `gemini-1.5-flash-8b-001`, Benchmark `OTIS Mock AIME 2024-2025`. Retained original output = 900.088888889. Input under `three_tokenizer_mean` = 193.874074074. Total = 1093.96296296 text tokens × 16000000000 FLOPs/token = **1.75034074074e+13 FLOPs**. The prior value was 1.76014222222e+13; change -0.5569%.

Reproduce the input counts with `python recompute_otis_inputs.py SOURCE_DIR OUTPUT_DIR`. Dependencies are Python tokenizers and tiktoken, plus Node tiktoken. No historical run calls or paid model requests are needed.
