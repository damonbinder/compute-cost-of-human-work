# Epoch: GPT-4.5 and Grok output-table observations

These twelve observations use [Epoch's original output-length table](https://epoch.ai/data-insights/output-length): GPT-4.5 preview, Grok-2 1212, Grok-3 beta and Grok-3 mini beta at high effort, each on GPQA Diamond, MATH Level 5 and OTIS. Exact identifiers, reported mean output lengths and scores come from that table. Active-size estimates and their sensitivity ranges are in [model assumptions](epoch-grok-gpt45-models.md).

The work unit is one answered benchmark question. Compute estimates one input and answer generation per question. The source marks only Grok-3 mini as reasoning; its output count already includes reasoning, which is counted once. There are no input, cache, retry or failed-call counters in this historical table. The reconstruction cannot audit that unreported work and does not establish that it was absent. Input is treated as newly processed text; cache reuse is unrecoverable. Benchmark grading is outside the human/AI answer-production task.

## Task inputs and tokenizer

GPQA counts all 198 original Diamond questions and four choices using the [Epoch researcher's instruction](https://gist.github.com/tadamcz/a61515465e34a3c66f3a78673502bc3f), with 12 assumed chat positions. Choice order is fixed for counting; the historical randomized order is not recovered. MATH counts all 1,324 original Level 5 test statements, including Asymptote code, with 50 assumed instruction/chat positions.

OTIS counts all 45 original question texts retained in a later [Epoch run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/bXgZZgzRE3wXoSRUgrbsVf.eval). `agent-work/sources/epoch/otis-original-question-text.json` records each exact question, target and archive-member locator. The questions cover the [2024](https://web.evanchen.cc/exams/OTIS-Mock-AIME-2024.pdf), [2025I](https://web.evanchen.cc/exams/OTIS-Mock-AIME-2025-I.pdf) and [2025II](https://web.evanchen.cc/exams/OTIS-Mock-AIME-2025-II.pdf) papers. We transfer that later run's short instruction to show work and return an integer answer, then add 12 assumed chat positions. The historical instruction is not recovered; outputs and accuracy remain the historical table values.

For GPT-4.5, [OpenAI's tiktoken 0.14.0 mapping](https://github.com/openai/tiktoken/blob/0.14.0/tiktoken/model.py) maps the `gpt-4.5-` prefix to `o200k_base`. The original vocabulary and encoding definition are retained and hash-checked under `agent-work/sources/epoch/small-models/`.

For Grok-2, we use [xAI's released tokenizer](https://huggingface.co/xai-org/grok-2/blob/daf4395a80ad177386cfe39641b64fc12b1d70ed/tokenizer.tok.json), with the exact V1 splitting expression and vocabulary-loading rules in the [implementation linked by the original release](https://github.com/sgl-project/sglang/blob/97a38ee85ba62e268bde6388f1bf8edfe2ca9d76/python/sglang/srt/tokenizer/tiktoken_tokenizer.py). This reconstructs plain-text tokens; the explicit assumed chat allowance is separate. The released weights/tokenizer are labelled Grok-2, without a confirmed 1212 API identity. For both Grok-3 endpoints this is an explicit earlier-family tokenizer proxy. No reported output count is retokenized or multiplied.

`recompute_grok_gpt45_table.py` takes the retained sources directory and reproduces per-question input counts, hashes and Grok-2 architecture arithmetic. It requires tiktoken and pyarrow. `calculations.json` in the review batch records every original source row, input/output sum, coefficient and FLOP product; the exact point-ID sections below make the CSV calculations inspectable.

## Human and performance comparison

The reviewed [GPQA baseline](gpqa.md) is the second expert validator: 198 recorded in-domain PhD validations of the revised question, mean active time 1,560.909090909091 seconds and 161/198 correct (81.31%), against 25% four-choice guessing. Diamond admits a question only when the first expert answered correctly, so 81.31% is biased upward; unselected expert accuracy on the extended set is 64.8%. The expert also writes an explanation and post-answer feedback, which the AI does not. The `below` floor is 53.16% and `far_above` is unreachable here. GPT-4.5 (68.69%), Grok 3 (75.76%) and Grok 3 mini (73.74%) are `below` the expert; Grok 2 (53.79%) clears the floor and is `below`.

The [MATH baseline](mathl5.md) assumes 600 seconds for an IMO-gold-level solver targeting 90% correct on Level 5; neither is a measured Level 5 human aggregate. GPT-4.5 at 78.63% and Grok-2 at 63.52% are below that target. Grok-3 at 88.75% and Grok-3 mini at 88.07% are broadly comparable to the approximate 90% target, hence match. Humans can see rendered diagrams while the model input contains diagram code.

The [OTIS baseline](otis.md) assumes the full three-hour allowance divided by 15, or 720 seconds per question. Original contest score frequencies give 51.5507246% accuracy under equal weighting of the three papers. GPT-4.5 at 37.78% and Grok-2 at 11.53% are below this baseline; Grok-3 at 55.56% is broadly comparable; Grok-3 mini at 77.78% is above it. Humans allocate effort over a paper while the model answers independently. These are aggregate comparisons, not a claim of identical success on individual questions.

The three match decisions use the substantive closeness of those scores to an approximate or aggregated human baseline. They do not impose a universal percentage cutoff or claim formal statistical equivalence. Per-point input and parameter sensitivities below are separate scenarios, not confidence bounds.


## Reconstructed input means

| Tokenizer | GPQA | MATH Level 5 | OTIS |
|---|---:|---:|---:|
| o200k | 265.626263 | 135.910121 | 186.6 |
| grok2 | 261.575758 | 134.575529 | 190.333333 |

## reas-epoch-gpqa-gpt45

[Epoch output table](https://epoch.ai/data-insights/output-length): Identifier `gpt-4.5-preview-2025-02-27`, Benchmark `GPQA diamond`. AI score 0.686868686869; human result/target 0.220538720539; comparison **above**. Human work and timing: [gpqa](gpqa.md).

Input 265.626262626 + reported mean output 919.353535354 = 1184.97979798 text tokens per question. At 1.2e+12 FLOPs/token, estimated compute is **1.42197575758e+15 FLOPs per question**.

Changing input alone by ±50% changes compute by ±11.2%. The model's 200–1200B active-parameter scenario gives 4.73992e+14–2.84395e+15 FLOPs at central tokens. These are sensitivity calculations, not confidence bounds.


## reas-epoch-mathl5-gpt45

[Epoch output table](https://epoch.ai/data-insights/output-length): Identifier `gpt-4.5-preview-2025-02-27`, Benchmark `MATH level 5`. AI score 0.786253776435; human result/target 0.9; comparison **below**. Human work and timing: [mathl5](mathl5.md).

Input 135.910120846 + reported mean output 850.354229607 = 986.264350453 text tokens per question. At 1.2e+12 FLOPs/token, estimated compute is **1.18351722054e+15 FLOPs per question**.

Changing input alone by ±50% changes compute by ±6.89%. The model's 200–1200B active-parameter scenario gives 3.94506e+14–2.36703e+15 FLOPs at central tokens. These are sensitivity calculations, not confidence bounds.


## reas-epoch-otis-gpt45

[Epoch output table](https://epoch.ai/data-insights/output-length): Identifier `gpt-4.5-preview-2025-02-27`, Benchmark `OTIS Mock AIME 2024-2025`. AI score 0.377777777778; human result/target 0.515507246377; comparison **below**. Human work and timing: [otis](otis.md).

Input 186.6 + reported mean output 1608.86666667 = 1795.46666667 text tokens per question. At 1.2e+12 FLOPs/token, estimated compute is **2.15456e+15 FLOPs per question**.

Changing input alone by ±50% changes compute by ±5.2%. The model's 200–1200B active-parameter scenario gives 7.18187e+14–4.30912e+15 FLOPs at central tokens. These are sensitivity calculations, not confidence bounds.


## reas-epoch-gpqa-grok2

[Epoch output table](https://epoch.ai/data-insights/output-length): Identifier `grok-2-1212`, Benchmark `GPQA diamond`. AI score 0.537878787879; human result/target 0.220538720539; comparison **above**. Human work and timing: [gpqa](gpqa.md).

Input 261.575757576 + reported mean output 639.787878788 = 901.363636364 text tokens per question. At 230000000000 FLOPs/token, estimated compute is **2.07313636364e+14 FLOPs per question**.

Changing input alone by ±50% changes compute by ±14.5%. The model's 80–150B active-parameter scenario gives 1.44218e+14–2.70409e+14 FLOPs at central tokens. These are sensitivity calculations, not confidence bounds.


## reas-epoch-mathl5-grok2

[Epoch output table](https://epoch.ai/data-insights/output-length): Identifier `grok-2-1212`, Benchmark `MATH level 5`. AI score 0.635196374622; human result/target 0.9; comparison **below**. Human work and timing: [mathl5](mathl5.md).

Input 134.575528701 + reported mean output 1048.2092145 = 1182.7847432 text tokens per question. At 230000000000 FLOPs/token, estimated compute is **2.72040490937e+14 FLOPs per question**.

Changing input alone by ±50% changes compute by ±5.69%. The model's 80–150B active-parameter scenario gives 1.89246e+14–3.54835e+14 FLOPs at central tokens. These are sensitivity calculations, not confidence bounds.


## reas-epoch-otis-grok2

[Epoch output table](https://epoch.ai/data-insights/output-length): Identifier `grok-2-1212`, Benchmark `OTIS Mock AIME 2024-2025`. AI score 0.115277777778; human result/target 0.515507246377; comparison **below**. Human work and timing: [otis](otis.md).

Input 190.333333333 + reported mean output 1631.33333333 = 1821.66666667 text tokens per question. At 230000000000 FLOPs/token, estimated compute is **4.18983333333e+14 FLOPs per question**.

Changing input alone by ±50% changes compute by ±5.22%. The model's 80–150B active-parameter scenario gives 2.91467e+14–5.465e+14 FLOPs at central tokens. These are sensitivity calculations, not confidence bounds.


## reas-epoch-gpqa-grok3

[Epoch output table](https://epoch.ai/data-insights/output-length): Identifier `grok-3-beta`, Benchmark `GPQA diamond`. AI score 0.757575757576; human result/target 0.220538720539; comparison **above**. Human work and timing: [gpqa](gpqa.md).

Input 261.575757576 + reported mean output 2524.33333333 = 2785.90909091 text tokens per question. At 230000000000 FLOPs/token, estimated compute is **6.40759090909e+14 FLOPs per question**.

Changing input alone by ±50% changes compute by ±4.69%. The model's 50–500B active-parameter scenario gives 2.78591e+14–2.78591e+15 FLOPs at central tokens. These are sensitivity calculations, not confidence bounds.


## reas-epoch-mathl5-grok3

[Epoch output table](https://epoch.ai/data-insights/output-length): Identifier `grok-3-beta`, Benchmark `MATH level 5`. AI score 0.88746223565; human result/target 0.9; comparison **match**. Human work and timing: [mathl5](mathl5.md).

Input 134.575528701 + reported mean output 2813.71601208 = 2948.29154079 text tokens per question. At 230000000000 FLOPs/token, estimated compute is **6.78107054381e+14 FLOPs per question**.

Changing input alone by ±50% changes compute by ±2.28%. The model's 50–500B active-parameter scenario gives 2.94829e+14–2.94829e+15 FLOPs at central tokens. These are sensitivity calculations, not confidence bounds.


## reas-epoch-otis-grok3

[Epoch output table](https://epoch.ai/data-insights/output-length): Identifier `grok-3-beta`, Benchmark `OTIS Mock AIME 2024-2025`. AI score 0.555555555556; human result/target 0.515507246377; comparison **match**. Human work and timing: [otis](otis.md).

Input 190.333333333 + reported mean output 5544.8 = 5735.13333333 text tokens per question. At 230000000000 FLOPs/token, estimated compute is **1.31908066667e+15 FLOPs per question**.

Changing input alone by ±50% changes compute by ±1.66%. The model's 50–500B active-parameter scenario gives 5.73513e+14–5.73513e+15 FLOPs at central tokens. These are sensitivity calculations, not confidence bounds.


## reas-epoch-gpqa-grok3mini

[Epoch output table](https://epoch.ai/data-insights/output-length): Identifier `grok-3-mini-beta_high`, Benchmark `GPQA diamond`. AI score 0.737373737374; human result/target 0.220538720539; comparison **above**. Human work and timing: [gpqa](gpqa.md).

Input 261.575757576 + reported mean output 7766.38383838 = 8027.95959596 text tokens per question. At 40000000000 FLOPs/token, estimated compute is **3.21118383838e+14 FLOPs per question**.

Changing input alone by ±50% changes compute by ±1.63%. The model's 5–60B active-parameter scenario gives 8.02796e+13–9.63355e+14 FLOPs at central tokens. These are sensitivity calculations, not confidence bounds.


## reas-epoch-mathl5-grok3mini

[Epoch output table](https://epoch.ai/data-insights/output-length): Identifier `grok-3-mini-beta_high`, Benchmark `MATH level 5`. AI score 0.880664652568; human result/target 0.9; comparison **match**. Human work and timing: [mathl5](mathl5.md).

Input 134.575528701 + reported mean output 6443.49924471 = 6578.07477341 text tokens per question. At 40000000000 FLOPs/token, estimated compute is **2.63122990937e+14 FLOPs per question**.

Changing input alone by ±50% changes compute by ±1.02%. The model's 5–60B active-parameter scenario gives 6.57807e+13–7.89369e+14 FLOPs at central tokens. These are sensitivity calculations, not confidence bounds.


## reas-epoch-otis-grok3mini

[Epoch output table](https://epoch.ai/data-insights/output-length): Identifier `grok-3-mini-beta_high`, Benchmark `OTIS Mock AIME 2024-2025`. AI score 0.777777777778; human result/target 0.515507246377; comparison **above**. Human work and timing: [otis](otis.md).

Input 190.333333333 + reported mean output 20232.4888889 = 20422.8222222 text tokens per question. At 40000000000 FLOPs/token, estimated compute is **8.16912888889e+14 FLOPs per question**.

Changing input alone by ±50% changes compute by ±0.466%. The model's 5–60B active-parameter scenario gives 2.04228e+14–2.45074e+15 FLOPs at central tokens. These are sensitivity calculations, not confidence bounds.
