# Epoch: final thirteen output-table observations

These observations finish the remaining identities in [Epoch's original output-length table](https://epoch.ai/data-insights/output-length): Gemini 1.0 Pro 001, Qwen2.5-Max 0125, Qwen-Plus 0125 and Qwen-Turbo 1101 on three benchmarks, plus Gemini 2.0 Pro experimental on MATH Level 5. Exact snapshot identifiers, scores and mean output tokens come from the original table. The four new model estimates and the unchanged shared Gemini 2.0 Pro record are explained in [model assumptions](epoch-final-table-models.md).

The work unit is one answered benchmark question. The reconstruction uses one input plus the reported mean output for that question. The source marks all five configurations as non-reasoning. Its output counts already include reasoning where applicable; no second reasoning count or multiplier is added. The historical table has no input, cache, retry or failed-call counters. This reconstruction cannot audit that unreported work and does not establish that it was absent. Inputs are treated as newly processed text; cache reuse is unrecoverable. Benchmark grading is outside the answer-production task compared with humans.

## Input reconstruction

GPQA counts all 198 original Diamond questions and their four answer choices, using the [Epoch researcher's instruction](https://gist.github.com/tadamcz/a61515465e34a3c66f3a78673502bc3f). Choice order is fixed for length reconstruction, rather than claiming to recover the historical randomized ordering. Twelve assumed chat positions are added. MATH counts all 1,324 original Level 5 test problems, including Asymptote code, plus 50 assumed instruction/chat positions.

OTIS counts the exact 45 question strings retained in the later original [Epoch Gemini 3.1 Pro run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/bXgZZgzRE3wXoSRUgrbsVf.eval). `agent-work/sources/epoch/otis-original-question-text.json` includes each question, target, source archive URL and member locator. The questions cover the original [2024](https://web.evanchen.cc/exams/OTIS-Mock-AIME-2024.pdf), [2025I](https://web.evanchen.cc/exams/OTIS-Mock-AIME-2025-I.pdf) and [2025II](https://web.evanchen.cc/exams/OTIS-Mock-AIME-2025-II.pdf) papers. Its short instruction to show work and return an integer answer is transferred to the historical table runs; 12 assumed chat positions are added. The historical wrapper is not recovered. AI output counts and performance remain the original historical observations.

## Tokenizer identity

Google's [Vertex SDK loader](https://github.com/googleapis/python-aiplatform/blob/44766a094f50d03093197027327d0ac2ec641829/vertexai/tokenization/_tokenizer_loading.py) explicitly maps `gemini-1.0-pro-001` to the original Gemma tokenizer. We use its pinned vocabulary hash, `61a7b147390c64585d6c3543dd6fc636906c9af3865a5548f27f31aee1d4c8e2`, with direct SentencePiece encoding and no automatic BOS/EOS addition.

Gemini 2.0 Pro uses the previously reviewed Gemma 3 tokenizer, whose [original report](https://storage.googleapis.com/deepmind-media/gemma/Gemma3Report.pdf), §2.1, states that it shares a tokenizer with Gemini 2.0. The [Google GenAI loader](https://github.com/googleapis/python-genai/blob/6a4c0b0a1748bf42ecd78bae9d401592be32eaca/google/genai/_local_tokenizer_loader.py) pins the same file and maps the 2.0 Flash endpoint. Its Pro mapping is family-level evidence, not a recovered historical provider count.

The [Qwen2.5 report](https://arxiv.org/html/2412.15115v2), §2, specifies one byte-level BPE vocabulary for the family: 151,643 regular and 22 control tokens, including the hosted MoEs. We use the released [Qwen2.5 tokenizer](https://huggingface.co/Qwen/Qwen2.5-72B-Instruct/blob/495f39366efef23836d0cfae4fbe635880d2be31/tokenizer.json), SHA256 `c0382117ea329cdf097041132f6d735924b697924d6f6fc3945713e96ce87539`. It has exactly those counts. The report explicitly identifies Turbo 1101. The later Plus0125 and Max0125 mappings extend that documented family tokenizer to later revisions; they are not verified API token-counter matches. No output count is retokenized.

`recompute_final_table.py` accepts the retained sources directory and reproduces every per-question input count and file hash offline, using sentencepiece, tokenizers and pyarrow. Supply `--models /path/to/models.csv` to also reproduce all thirteen input/output sums and FLOP products from the original table and current shared coefficients. `--output /path/to/new-results.json` writes a new file outside the retained sources; it refuses to overwrite an existing file. The review batch's `input-counts.json` records both Google tokenizers and Qwen; `calculations.json` records every original table row, input/output sum and FLOP product. The exact point-ID sections below provide the CSV calculation locators.

## Human and performance meanings

The reviewed [GPQA baseline](gpqa.md) is the second expert validator: 198 recorded in-domain PhD validations of the revised question, mean active time 1,560.909090909091 seconds and 161/198 correct (81.31%), against 25% four-choice guessing. Diamond admits a question only when the first expert answered correctly, so 81.31% is biased upward; unselected expert accuracy on the extended set is 64.8%. The expert also writes an explanation and post-answer feedback, which the AI does not. The `below` floor is 53.16% and `far_above` is unreachable here. Of the four scores here, only Qwen-Max 2.5 (56.12%) clears the 53.16% floor, as `below`; the other three are withheld.

The [MATH baseline](mathl5.md) assumes an IMO-gold-level solver spends 600 seconds per Level 5 problem and targets 90% accuracy. Neither is a measured Level 5 human aggregate. The five AI scores range from 11.24% to 83.46%, below that assumed target. Humans can view rendered diagrams, while model inputs include diagram code.

The [OTIS baseline](otis.md) assumes use of the full three-hour paper allowance divided by 15, giving 720 seconds per question. Original contest score frequencies give 51.5507246% human accuracy under equal weighting of the three papers. All four AI scores are below 18%, so they are below that contestant baseline. Humans allocate their effort across the paper; AI answers independently.

This tranche contains four above and nine below classifications. There are no borderline match judgments. Input and model-size sensitivities below vary separately and are not confidence intervals.


## Reconstructed input means

| Tokenizer | GPQA | MATH Level 5 | OTIS |
|---|---:|---:|---:|
| gemma | 266.535354 | 138.867825 | 194.6 |
| gemma3 | 265.156566 | 138.892749 | 195.066667 |
| qwen25 | 273.808081 | 138.58006 | 195.288889 |

## reas-epoch-gpqa-gemini10pro

[Epoch output table](https://epoch.ai/data-insights/output-length): Identifier `gemini-1.0-pro-001`, Benchmark `GPQA diamond`. AI score 0.339646464646; human result/target 0.220538720539; comparison **above**. Human work and timing: [gpqa](gpqa.md).

Input 266.535353535 + reported mean output 211.207070707 = 477.742424242 text tokens per question. At 140000000000 FLOPs/token, estimated compute is **6.68839393939e+13 FLOPs per question**.

Changing input alone by ±50% changes compute by ±27.9%. The model's 20–200B active-parameter scenario gives 1.91097e+13–1.91097e+14 FLOPs at central tokens. These are sensitivity calculations, not confidence bounds.


## reas-epoch-mathl5-gemini10pro

[Epoch output table](https://epoch.ai/data-insights/output-length): Identifier `gemini-1.0-pro-001`, Benchmark `MATH level 5`. AI score 0.112443353474; human result/target 0.9; comparison **below**. Human work and timing: [mathl5](mathl5.md).

Input 138.867824773 + reported mean output 310.839123867 = 449.70694864 text tokens per question. At 140000000000 FLOPs/token, estimated compute is **6.29589728097e+13 FLOPs per question**.

Changing input alone by ±50% changes compute by ±15.4%. The model's 20–200B active-parameter scenario gives 1.79883e+13–1.79883e+14 FLOPs at central tokens. These are sensitivity calculations, not confidence bounds.


## reas-epoch-otis-gemini10pro

[Epoch output table](https://epoch.ai/data-insights/output-length): Identifier `gemini-1.0-pro-001`, Benchmark `OTIS Mock AIME 2024-2025`. AI score 0.0111111111111; human result/target 0.515507246377; comparison **below**. Human work and timing: [otis](otis.md).

Input 194.6 + reported mean output 545.466666667 = 740.066666667 text tokens per question. At 140000000000 FLOPs/token, estimated compute is **1.03609333333e+14 FLOPs per question**.

Changing input alone by ±50% changes compute by ±13.1%. The model's 20–200B active-parameter scenario gives 2.96027e+13–2.96027e+14 FLOPs at central tokens. These are sensitivity calculations, not confidence bounds.


## reas-epoch-gpqa-qwenmax25

[Epoch output table](https://epoch.ai/data-insights/output-length): Identifier `qwen-max-2025-01-25`, Benchmark `GPQA diamond`. AI score 0.561237373737; human result/target 0.220538720539; comparison **above**. Human work and timing: [gpqa](gpqa.md).

Input 273.808080808 + reported mean output 612.646464646 = 886.454545455 text tokens per question. At 74000000000 FLOPs/token, estimated compute is **6.55976363636e+13 FLOPs per question**.

Changing input alone by ±50% changes compute by ±15.4%. The model's 15–150B active-parameter scenario gives 2.65936e+13–2.65936e+14 FLOPs at central tokens. These are sensitivity calculations, not confidence bounds.


## reas-epoch-mathl5-qwenmax25

[Epoch output table](https://epoch.ai/data-insights/output-length): Identifier `qwen-max-2025-01-25`, Benchmark `MATH level 5`. AI score 0.671827794562; human result/target 0.9; comparison **below**. Human work and timing: [mathl5](mathl5.md).

Input 138.580060423 + reported mean output 957.589879154 = 1096.16993958 text tokens per question. At 74000000000 FLOPs/token, estimated compute is **8.11165755287e+13 FLOPs per question**.

Changing input alone by ±50% changes compute by ±6.32%. The model's 15–150B active-parameter scenario gives 3.28851e+13–3.28851e+14 FLOPs at central tokens. These are sensitivity calculations, not confidence bounds.


## reas-epoch-otis-qwenmax25

[Epoch output table](https://epoch.ai/data-insights/output-length): Identifier `qwen-max-2025-01-25`, Benchmark `OTIS Mock AIME 2024-2025`. AI score 0.161111111111; human result/target 0.515507246377; comparison **below**. Human work and timing: [otis](otis.md).

Input 195.288888889 + reported mean output 1332.06666667 = 1527.35555556 text tokens per question. At 74000000000 FLOPs/token, estimated compute is **1.13024311111e+14 FLOPs per question**.

Changing input alone by ±50% changes compute by ±6.39%. The model's 15–150B active-parameter scenario gives 4.58207e+13–4.58207e+14 FLOPs at central tokens. These are sensitivity calculations, not confidence bounds.


## reas-epoch-gpqa-qwenplus25

[Epoch output table](https://epoch.ai/data-insights/output-length): Identifier `qwen-plus-2025-01-25`, Benchmark `GPQA diamond`. AI score 0.481060606061; human result/target 0.220538720539; comparison **above**. Human work and timing: [gpqa](gpqa.md).

Input 273.808080808 + reported mean output 343.883838384 = 617.691919192 text tokens per question. At 42000000000 FLOPs/token, estimated compute is **2.59430606061e+13 FLOPs per question**.

Changing input alone by ±50% changes compute by ±22.2%. The model's 8–80B active-parameter scenario gives 9.88307e+12–9.88307e+13 FLOPs at central tokens. These are sensitivity calculations, not confidence bounds.


## reas-epoch-mathl5-qwenplus25

[Epoch output table](https://epoch.ai/data-insights/output-length): Identifier `qwen-plus-2025-01-25`, Benchmark `MATH level 5`. AI score 0.652756797583; human result/target 0.9; comparison **below**. Human work and timing: [mathl5](mathl5.md).

Input 138.580060423 + reported mean output 910.231873112 = 1048.81193353 text tokens per question. At 42000000000 FLOPs/token, estimated compute is **4.40501012085e+13 FLOPs per question**.

Changing input alone by ±50% changes compute by ±6.61%. The model's 8–80B active-parameter scenario gives 1.6781e+13–1.6781e+14 FLOPs at central tokens. These are sensitivity calculations, not confidence bounds.


## reas-epoch-otis-qwenplus25

[Epoch output table](https://epoch.ai/data-insights/output-length): Identifier `qwen-plus-2025-01-25`, Benchmark `OTIS Mock AIME 2024-2025`. AI score 0.177777777778; human result/target 0.515507246377; comparison **below**. Human work and timing: [otis](otis.md).

Input 195.288888889 + reported mean output 1259.71111111 = 1455 text tokens per question. At 42000000000 FLOPs/token, estimated compute is **6.111e+13 FLOPs per question**.

Changing input alone by ±50% changes compute by ±6.71%. The model's 8–80B active-parameter scenario gives 2.328e+13–2.328e+14 FLOPs at central tokens. These are sensitivity calculations, not confidence bounds.


## reas-epoch-gpqa-qwenturbo24

[Epoch output table](https://epoch.ai/data-insights/output-length): Identifier `qwen-turbo-2024-11-01`, Benchmark `GPQA diamond`. AI score 0.417929292929; human result/target 0.220538720539; comparison **above**. Human work and timing: [gpqa](gpqa.md).

Input 273.808080808 + reported mean output 616.626262626 = 890.434343434 text tokens per question. At 28000000000 FLOPs/token, estimated compute is **2.49321616162e+13 FLOPs per question**.

Changing input alone by ±50% changes compute by ±15.4%. The model's 4–40B active-parameter scenario gives 7.12347e+12–7.12347e+13 FLOPs at central tokens. These are sensitivity calculations, not confidence bounds.


## reas-epoch-mathl5-qwenturbo24

[Epoch output table](https://epoch.ai/data-insights/output-length): Identifier `qwen-turbo-2024-11-01`, Benchmark `MATH level 5`. AI score 0.562311178248; human result/target 0.9; comparison **below**. Human work and timing: [mathl5](mathl5.md).

Input 138.580060423 + reported mean output 714.744712991 = 853.324773414 text tokens per question. At 28000000000 FLOPs/token, estimated compute is **2.38930936556e+13 FLOPs per question**.

Changing input alone by ±50% changes compute by ±8.12%. The model's 4–40B active-parameter scenario gives 6.8266e+12–6.8266e+13 FLOPs at central tokens. These are sensitivity calculations, not confidence bounds.


## reas-epoch-otis-qwenturbo24

[Epoch output table](https://epoch.ai/data-insights/output-length): Identifier `qwen-turbo-2024-11-01`, Benchmark `OTIS Mock AIME 2024-2025`. AI score 0.0611111111111; human result/target 0.515507246377; comparison **below**. Human work and timing: [otis](otis.md).

Input 195.288888889 + reported mean output 1044.33333333 = 1239.62222222 text tokens per question. At 28000000000 FLOPs/token, estimated compute is **3.47094222222e+13 FLOPs per question**.

Changing input alone by ±50% changes compute by ±7.88%. The model's 4–40B active-parameter scenario gives 9.91698e+12–9.91698e+13 FLOPs at central tokens. These are sensitivity calculations, not confidence bounds.


## reas-epoch-mathl5-gemini20pro

[Epoch output table](https://epoch.ai/data-insights/output-length): Identifier `gemini-2.0-pro-exp-02-05`, Benchmark `MATH level 5`. AI score 0.834592145015; human result/target 0.9; comparison **below**. Human work and timing: [mathl5](mathl5.md).

Input 138.892749245 + reported mean output 964.439577039 = 1103.33232628 text tokens per question. At 200000000000 FLOPs/token, estimated compute is **2.20666465257e+14 FLOPs per question**.

Changing input alone by ±50% changes compute by ±6.29%. The model's 30–300B active-parameter scenario gives 6.61999e+13–6.61999e+14 FLOPs at central tokens. These are sensitivity calculations, not confidence bounds.
