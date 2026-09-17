# Epoch: Gemini 1.5 and 2.0 output-table observations

These 16 observations use [Epoch's original output-length table](https://epoch.ai/data-insights/output-length): six GPQA Diamond, five MATH Level 5 and five OTIS rows. The exact model IDs, mean output tokens and accuracy are copied from the original table; inputs are reconstructed. All six configurations are marked non-reasoning in that source. Google supplies no active-parameter count for them; the explicit shared estimates and scenarios are in [model assumptions](epoch-gemini-table-models.md).

The work unit is one answered benchmark question. Compute estimates one input and answer generation per question from the reported mean output. The table includes reasoning in output tokens; we do not add another reasoning count. It has no input, cache or call-event counters. Consequently this is not an audit of retries or unsuccessful requests, and it does not establish that such work was absent. Input is counted as newly processed text; any cache reuse cannot be recovered from this source. Benchmark grading is outside the answer-production task compared with humans.

## Input reconstruction

GPQA uses all 198 original Diamond questions with four choices and the [Epoch researcher's instruction](https://gist.github.com/tadamcz/a61515465e34a3c66f3a78673502bc3f). Choice order is fixed for this length calculation; the historical random ordering is not recovered. We add 12 assumed chat positions. MATH uses all 1,324 original Level 5 test statements, including Asymptote code, and adds 50 assumed instruction/chat positions. Those are the previously reviewed task-input recipes, recounted using Google's appropriate tokenizer files.

For OTIS, the later original [Epoch Gemini 3.1 Pro run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/bXgZZgzRE3wXoSRUgrbsVf.eval) retains all 45 original question strings. `agent-work/sources/epoch/otis-original-question-text.json` preserves each text, target and original `.eval` URL/member locator. It extracts task inputs, not model answers. The questions cover the same three 15-problem papers as the historical table. We count each question with the later run's instruction to show working and end with an integer answer, then add 12 assumed chat positions. Transferring that short instruction to the historical runs is explicit; their exact wrapper is not recovered. This replaces the earlier 200-token OTIS input assumption with a count of the actual task content. Outputs and performance still come from the historical table.

The original contest papers remain available at [2024](https://web.evanchen.cc/exams/OTIS-Mock-AIME-2024.pdf), [2025I](https://web.evanchen.cc/exams/OTIS-Mock-AIME-2025-I.pdf) and [2025II](https://web.evanchen.cc/exams/OTIS-Mock-AIME-2025-II.pdf). This change to input accounting does not change their human baseline.

## Tokenizer identity

Google's [Vertex SDK loader at commit 44766a0](https://github.com/googleapis/python-aiplatform/blob/44766a094f50d03093197027327d0ac2ec641829/vertexai/tokenization/_tokenizer_loading.py), committed September 25, 2024, explicitly maps all four 1.5 stable 001/002 identifiers to the original Gemma SentencePiece tokenizer. The file pins both its [original model bytes](https://raw.githubusercontent.com/google/gemma_pytorch/33b652c465537c6158f9a472ea5700e5e770ad3f/tokenizer/tokenizer.model) and SHA256 `61a7b147390c64585d6c3543dd6fc636906c9af3865a5548f27f31aee1d4c8e2`. We reproduce the SDK's direct SentencePiece encoding, without automatic BOS/EOS addition; the assumed wrappers are separate.

Google's [GenAI SDK loader at commit 6a4c0b0](https://github.com/googleapis/python-genai/blob/6a4c0b0a1748bf42ecd78bae9d401592be32eaca/google/genai/_local_tokenizer_loader.py) explicitly maps `gemini-2.0-flash-001` to Gemma 3's tokenizer. Its [original model bytes](https://raw.githubusercontent.com/google/gemma_pytorch/014acb7ac4563a5f77c76d7ff98f31b568c16508/tokenizer/gemma3_cleaned_262144_v2.spiece.model) have SHA256 `1299c11d7cf632ef3b4e11937501358ada021bbdf7c47638d13c0ee982f2e79c`. The [Gemma 3 report](https://storage.googleapis.com/deepmind-media/gemma/Gemma3Report.pdf), §2.1 “Tokenizer,” states that it uses the same tokenizer as Gemini 2.0. This supports using it for the Pro 2.0 experimental endpoint, which is not individually listed in the SDK loader. That Pro mapping is family-level evidence, not a recovered provider token counter.

The two original tokenizer files are retained and hash-checked. There are no live inference or tokenizer API calls. `recompute_gemini_table.py` accepts the retained sources directory and reproduces all per-question input counts. `expansion-15/input-counts.json` records these counts, hashes, wrapper assumptions and the SentencePiece version; `calculations.json` retains every original source row and product. `expand_gemini_table.py` generates the candidate CSVs and this note without writing production.

## Human and performance definitions

The reviewed [GPQA baseline](gpqa.md) is the second expert validator: 198 recorded in-domain PhD validations of the revised question, mean active time 1,560.909090909091 seconds and 161/198 correct (81.31%), against 25% four-choice guessing. Diamond admits a question only when the first expert answered correctly, so 81.31% is biased upward; unselected expert accuracy on the extended set is 64.8%. The expert also writes an explanation and post-answer feedback, which the AI does not. The `below` floor is 53.16% and `far_above` is unreachable here. Of the six Gemini results here, Gemini 1.5 Pro (57.23%), 2.0 Flash (64.14%) and 2.0 Pro (65.66%) are `below` the expert; the three 1.5 Flash and 1.0 Pro results fall under the 53.16% floor and are withheld.

The [MATH recipe](mathl5.md) assumes 600 seconds of mean effort for an IMO-gold-level solver targeting 90% correct on Level 5. Neither is an observed Level 5 human aggregate. All five AI scores here are below 83%, so they are below that assumed target. Humans can view rendered diagrams; the source model input includes diagram code.

The [OTIS recipe](otis.md) assumes the full 10,800-second paper allowance is used and divides it by 15, giving 720 seconds per question. It is not a timing sample. Human performance is calculated from original contest score frequencies, equally weighting the three papers: 51.5507246%. AI scores range from 3.89% to 31.11%, below that trained-contestant baseline. Humans allocate effort across an entire paper; AI answers independently.

The classifications do not require a universal numerical threshold or formal equivalence test. No near-boundary match decision is needed in these sixteen entries. Per-point sensitivity below varies the input count and model parameter estimate separately; neither is a statistical confidence interval.


## Reconstructed input means

| Google tokenizer | GPQA | MATH Level5 | OTIS |
|---|---:|---:|---:|
| gemma | 266.535354 | 138.867825 | 194.6 |
| gemma3 | 265.156566 | 138.892749 | 195.066667 |

## reas-epoch-gpqa-gemini15flash1

[Epoch output table](https://epoch.ai/data-insights/output-length): Identifier `gemini-1.5-flash-001`, Benchmark `GPQA diamond`. AI score 0.403724747475; human result/target 0.220538720539; comparison **above**. Human work and timing: [gpqa](gpqa.md).

Input 266.535353535 + reported mean output 355.585858586 = 622.121212121 text tokens per question. At 54000000000 FLOPs/token, estimated compute is **3.35945454545e+13 FLOPs per question**.

Changing input alone by ±50% changes compute by ±21.4%. The model's 8–100B active-parameter scenario gives 9.95394e+12–1.24424e+14 FLOPs at central tokens. These are sensitivity calculations, not confidence bounds.


## reas-epoch-mathl5-gemini15flash1

[Epoch output table](https://epoch.ai/data-insights/output-length): Identifier `gemini-1.5-flash-001`, Benchmark `MATH level 5`. AI score 0.25122734139; human result/target 0.9; comparison **below**. Human work and timing: [mathl5](mathl5.md).

Input 138.867824773 + reported mean output 445.245468278 = 584.113293051 text tokens per question. At 54000000000 FLOPs/token, estimated compute is **3.15421178248e+13 FLOPs per question**.

Changing input alone by ±50% changes compute by ±11.9%. The model's 8–100B active-parameter scenario gives 9.34581e+12–1.16823e+14 FLOPs at central tokens. These are sensitivity calculations, not confidence bounds.


## reas-epoch-otis-gemini15flash1

[Epoch output table](https://epoch.ai/data-insights/output-length): Identifier `gemini-1.5-flash-001`, Benchmark `OTIS Mock AIME 2024-2025`. AI score 0.0388888888889; human result/target 0.515507246377; comparison **below**. Human work and timing: [otis](otis.md).

Input 194.6 + reported mean output 1005.71111111 = 1200.31111111 text tokens per question. At 54000000000 FLOPs/token, estimated compute is **6.48168e+13 FLOPs per question**.

Changing input alone by ±50% changes compute by ±8.11%. The model's 8–100B active-parameter scenario gives 1.9205e+13–2.40062e+14 FLOPs at central tokens. These are sensitivity calculations, not confidence bounds.


## reas-epoch-gpqa-gemini15flash2

[Epoch output table](https://epoch.ai/data-insights/output-length): Identifier `gemini-1.5-flash-002`, Benchmark `GPQA diamond`. AI score 0.473169191919; human result/target 0.220538720539; comparison **above**. Human work and timing: [gpqa](gpqa.md).

Input 266.535353535 + reported mean output 427.641414141 = 694.176767677 text tokens per question. At 54000000000 FLOPs/token, estimated compute is **3.74855454545e+13 FLOPs per question**.

Changing input alone by ±50% changes compute by ±19.2%. The model's 8–100B active-parameter scenario gives 1.11068e+13–1.38835e+14 FLOPs at central tokens. These are sensitivity calculations, not confidence bounds.


## reas-epoch-mathl5-gemini15flash2

[Epoch output table](https://epoch.ai/data-insights/output-length): Identifier `gemini-1.5-flash-002`, Benchmark `MATH level 5`. AI score 0.618674471299; human result/target 0.9; comparison **below**. Human work and timing: [mathl5](mathl5.md).

Input 138.867824773 + reported mean output 581.860271903 = 720.728096677 text tokens per question. At 54000000000 FLOPs/token, estimated compute is **3.89193172205e+13 FLOPs per question**.

Changing input alone by ±50% changes compute by ±9.63%. The model's 8–100B active-parameter scenario gives 1.15316e+13–1.44146e+14 FLOPs at central tokens. These are sensitivity calculations, not confidence bounds.


## reas-epoch-otis-gemini15flash2

[Epoch output table](https://epoch.ai/data-insights/output-length): Identifier `gemini-1.5-flash-002`, Benchmark `OTIS Mock AIME 2024-2025`. AI score 0.1625; human result/target 0.515507246377; comparison **below**. Human work and timing: [otis](otis.md).

Input 194.6 + reported mean output 907.444444444 = 1102.04444444 text tokens per question. At 54000000000 FLOPs/token, estimated compute is **5.95104e+13 FLOPs per question**.

Changing input alone by ±50% changes compute by ±8.83%. The model's 8–100B active-parameter scenario gives 1.76327e+13–2.20409e+14 FLOPs at central tokens. These are sensitivity calculations, not confidence bounds.


## reas-epoch-gpqa-gemini15pro1

[Epoch output table](https://epoch.ai/data-insights/output-length): Identifier `gemini-1.5-pro-001`, Benchmark `GPQA diamond`. AI score 0.458648989899; human result/target 0.220538720539; comparison **above**. Human work and timing: [gpqa](gpqa.md).

Input 266.535353535 + reported mean output 357.444444444 = 623.97979798 text tokens per question. At 200000000000 FLOPs/token, estimated compute is **1.24795959596e+14 FLOPs per question**.

Changing input alone by ±50% changes compute by ±21.4%. The model's 30–300B active-parameter scenario gives 3.74388e+13–3.74388e+14 FLOPs at central tokens. These are sensitivity calculations, not confidence bounds.


## reas-epoch-mathl5-gemini15pro1

[Epoch output table](https://epoch.ai/data-insights/output-length): Identifier `gemini-1.5-pro-001`, Benchmark `MATH level 5`. AI score 0.40747734139; human result/target 0.9; comparison **below**. Human work and timing: [mathl5](mathl5.md).

Input 138.867824773 + reported mean output 445.266616314 = 584.134441088 text tokens per question. At 200000000000 FLOPs/token, estimated compute is **1.16826888218e+14 FLOPs per question**.

Changing input alone by ±50% changes compute by ±11.9%. The model's 30–300B active-parameter scenario gives 3.50481e+13–3.50481e+14 FLOPs at central tokens. These are sensitivity calculations, not confidence bounds.


## reas-epoch-otis-gemini15pro1

[Epoch output table](https://epoch.ai/data-insights/output-length): Identifier `gemini-1.5-pro-001`, Benchmark `OTIS Mock AIME 2024-2025`. AI score 0.0680555555556; human result/target 0.515507246377; comparison **below**. Human work and timing: [otis](otis.md).

Input 194.6 + reported mean output 811.088888889 = 1005.68888889 text tokens per question. At 200000000000 FLOPs/token, estimated compute is **2.01137777778e+14 FLOPs per question**.

Changing input alone by ±50% changes compute by ±9.67%. The model's 30–300B active-parameter scenario gives 6.03413e+13–6.03413e+14 FLOPs at central tokens. These are sensitivity calculations, not confidence bounds.


## reas-epoch-gpqa-gemini15pro2

[Epoch output table](https://epoch.ai/data-insights/output-length): Identifier `gemini-1.5-pro-002`, Benchmark `GPQA diamond`. AI score 0.572285353535; human result/target 0.220538720539; comparison **above**. Human work and timing: [gpqa](gpqa.md).

Input 266.535353535 + reported mean output 441.292929293 = 707.828282828 text tokens per question. At 200000000000 FLOPs/token, estimated compute is **1.41565656566e+14 FLOPs per question**.

Changing input alone by ±50% changes compute by ±18.8%. The model's 30–300B active-parameter scenario gives 4.24697e+13–4.24697e+14 FLOPs at central tokens. These are sensitivity calculations, not confidence bounds.


## reas-epoch-mathl5-gemini15pro2

[Epoch output table](https://epoch.ai/data-insights/output-length): Identifier `gemini-1.5-pro-002`, Benchmark `MATH level 5`. AI score 0.703927492447; human result/target 0.9; comparison **below**. Human work and timing: [mathl5](mathl5.md).

Input 138.867824773 + reported mean output 571.367824773 = 710.235649547 text tokens per question. At 200000000000 FLOPs/token, estimated compute is **1.42047129909e+14 FLOPs per question**.

Changing input alone by ±50% changes compute by ±9.78%. The model's 30–300B active-parameter scenario gives 4.26141e+13–4.26141e+14 FLOPs at central tokens. These are sensitivity calculations, not confidence bounds.


## reas-epoch-otis-gemini15pro2

[Epoch output table](https://epoch.ai/data-insights/output-length): Identifier `gemini-1.5-pro-002`, Benchmark `OTIS Mock AIME 2024-2025`. AI score 0.230555555556; human result/target 0.515507246377; comparison **below**. Human work and timing: [otis](otis.md).

Input 194.6 + reported mean output 826.666666667 = 1021.26666667 text tokens per question. At 200000000000 FLOPs/token, estimated compute is **2.04253333333e+14 FLOPs per question**.

Changing input alone by ±50% changes compute by ±9.53%. The model's 30–300B active-parameter scenario gives 6.1276e+13–6.1276e+14 FLOPs at central tokens. These are sensitivity calculations, not confidence bounds.


## reas-epoch-gpqa-gemini20flash

[Epoch output table](https://epoch.ai/data-insights/output-length): Identifier `gemini-2.0-flash-001`, Benchmark `GPQA diamond`. AI score 0.641414141414; human result/target 0.220538720539; comparison **above**. Human work and timing: [gpqa](gpqa.md).

Input 265.156565657 + reported mean output 605.833333333 = 870.98989899 text tokens per question. At 80000000000 FLOPs/token, estimated compute is **6.96791919192e+13 FLOPs per question**.

Changing input alone by ±50% changes compute by ±15.2%. The model's 10–150B active-parameter scenario gives 1.74198e+13–2.61297e+14 FLOPs at central tokens. These are sensitivity calculations, not confidence bounds.


## reas-epoch-mathl5-gemini20flash

[Epoch output table](https://epoch.ai/data-insights/output-length): Identifier `gemini-2.0-flash-001`, Benchmark `MATH level 5`. AI score 0.821657854985; human result/target 0.9; comparison **below**. Human work and timing: [mathl5](mathl5.md).

Input 138.892749245 + reported mean output 908.879909366 = 1047.77265861 text tokens per question. At 80000000000 FLOPs/token, estimated compute is **8.38218126888e+13 FLOPs per question**.

Changing input alone by ±50% changes compute by ±6.63%. The model's 10–150B active-parameter scenario gives 2.09555e+13–3.14332e+14 FLOPs at central tokens. These are sensitivity calculations, not confidence bounds.


## reas-epoch-otis-gemini20flash

[Epoch output table](https://epoch.ai/data-insights/output-length): Identifier `gemini-2.0-flash-001`, Benchmark `OTIS Mock AIME 2024-2025`. AI score 0.311111111111; human result/target 0.515507246377; comparison **below**. Human work and timing: [otis](otis.md).

Input 195.066666667 + reported mean output 1566 = 1761.06666667 text tokens per question. At 80000000000 FLOPs/token, estimated compute is **1.40885333333e+14 FLOPs per question**.

Changing input alone by ±50% changes compute by ±5.54%. The model's 10–150B active-parameter scenario gives 3.52213e+13–5.2832e+14 FLOPs at central tokens. These are sensitivity calculations, not confidence bounds.


## reas-epoch-gpqa-gemini20pro

[Epoch output table](https://epoch.ai/data-insights/output-length): Identifier `gemini-2.0-pro-exp-02-05`, Benchmark `GPQA diamond`. AI score 0.656565656566; human result/target 0.220538720539; comparison **above**. Human work and timing: [gpqa](gpqa.md).

Input 265.156565657 + reported mean output 625.050505051 = 890.207070707 text tokens per question. At 200000000000 FLOPs/token, estimated compute is **1.78041414141e+14 FLOPs per question**.

Changing input alone by ±50% changes compute by ±14.9%. The model's 30–300B active-parameter scenario gives 5.34124e+13–5.34124e+14 FLOPs at central tokens. These are sensitivity calculations, not confidence bounds.
