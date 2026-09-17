# Llammas: Estonian reading acquisition

**The human-learning estimate in this note is superseded.** On 2026-09-14 the
human side of every row it covers was re-estimated as the active hours to reach the
capability the run bought, read off a published hours-to-proficiency table, rather
than the hours to move a benchmark score. The current figures, the method and the
per-row arithmetic are in [skill-acquisition human learning time](../skill-acquisition-human-time.md).
Everything else here — the endpoints, the task inspection and the compute
reconstruction — still stands.

## lang-xfer-et-llammas-base

One continued-pretraining run from Llama 2-7B to Llammas-base costs an estimated **2.74022797806535e20 FLOPs**. The human estimate is **150 active hours**, learning to improve from roughly chance to 39.34% correct on comparable unseen four-option Estonian passage questions. This is partial reading comprehension, not general Estonian fluency.

### Endpoint and model identity

[The original 2025 evaluation](https://aclanthology.org/2025.nodalida-1.37/), Table 6, directly compares Llama 2-7B with Llammas-base: zero-shot Belebele 22.95%→39.34%. The retained author repository pin 1f1f501389b8c4159ee4e1af854e281be0e7bf26 contains 122 questions over 64 passages, consistent with 28→48 correct. Table 3 is the different five-shot 28.69%→36.89% setting. These are not mixed. The earlier 2024 paper's instruction-tuned evaluations are not the base model's endpoint.

Belebele is chosen because the task supplies all factual information in an inspectable passage and permits the same human reading/answering activity. Translation requires a separate output-quality scale, while XCOPA mixes language with commonsense reasoning. This choice does not allocate only a fraction of training to reading: all 5B-token continued training is counted. The target is performance on unseen questions of this kind, not memorizing the 122 released answers.

The original[training paper](https://arxiv.org/abs/2404.04042) and HF README identify Llammas-base as Llama 2-7B after 5B tokens,75% Estonian/25% English documents. No SFT or synthetic instruction creation is included. The initial public[model commit](https://huggingface.co/tartuNLP/Llammas-base/tree/90245dff3f07c09bd2e18bf0cbe26b6995964bee) on 2024-02-16 contains both full weight shards, not merely a README. Its architecture is 32 layers,d 4096,FF 11008,32 query/KV heads,vocabulary 32000 and untied embeddings. Exact architectural parameter count is 6,738,415,616. The operation calculation separates lookup embeddings, transformer matrices and output head, rather than using all parameters uniformly.

### Human learning estimate

The human is an ordinary literate adult with English reading ability and normal general knowledge, initially without useful Estonian or closely related Finnish knowledge. The English task instructions are therefore understood. The starting 22.95% is a small-sample near-chance result, not an assertion that this adult knows exactly 22.95% of Estonian. The goal is partial comprehension sufficient to reach about 39% on new questions without translation tools. Study can use dictionaries, instruction, worked examples and feedback; those learning conditions differ from corpus next-token training.

`calculations.json` retains 16 seeded source items. They include literal quantity discrimination (more than 1000 stamps versus exactly 1000), tracking who failed to hear speech, identifying a corpse's location among competing place names, causal explanations, event order and questions with negation. The passages average 59.48 words but use inflected forms and news vocabulary. For example, the stamp question still requires recognizing the question word for quantity and the difference between “over” and “nearly”; shared numerals alone do not settle it. The satellite question asks what remains uncertain despite numerical facts. These observations argue against both a few memorized phrases and a full general-language qualification as the target.

The[Integration Foundation course FAQ](https://www.integratsioon.ee/en/let-us-answer-some-questions-about-estonian-language-courses) gives A1 as 100 academic contact hours plus at least 50 independent academic hours, and A2 as 150 plus 50. Its[good-practice definition](https://www.integratsioon.ee/en/good-practice-language-learning) explicitly defines an academic hour as 45 minutes. Thus the complete multi-skill A1 package is 112.5 active hours, and the combined A1+A2 packages 262.5 hours. These are prescribed study loads, not observed times to this benchmark; they provide scale checks only. Official[reading descriptors](https://www.integratsioon.ee/en/keeleoskustase) distinguish familiar words/simple sentences from finding information in short texts. Neither descriptor is assigned from 39% accuracy.

My central targeted route is 90 hours building receptive prerequisites and 60 hours applying them to short factual texts. The 90-hour component concentrates on high-frequency vocabulary, question words, negation, pronouns, common case endings and verb forms, rather than oral interaction or polished writing. It is smaller than the full A1 package but retains repeated practice and review; reading connected news sentences requires more than an isolated word list. The 60-hour component allows roughly 30 guided sessions of two hours combining unfamiliar passage work, explanation of incorrect options, vocabulary review and a later attempt on different material. This is a practice budget, not an assumed two-hour duration for one benchmark passage. It aims to make a limited subset of questions genuinely interpretable while leaving many errors; it does not require reliable comprehension of every passage.

**150 hours is an analyst judgment, not a measured learning curve or a linear conversion of accuracy gain.** A 50-hour scenario represents efficient focused recognition training where simpler questions provide much of the gain. A 400-hour scenario allows slow vocabulary acquisition, difficult morphology and needing wider reading experience before partial news comprehension improves. These scenarios express route uncertainty, not statistical bounds. No empirical timing donor is used: human evidence is `assumed`, method `estimated`, attempts/subset `not_applicable`. Course enrollments are not counted as timing observations. The human endpoint is constructed to match the AI's final question accuracy, so performance is `match` by definition of this learning target, not measured human parity.

The public benchmark and its underlying news may overlap web pretraining. No released row-level contamination audit establishes otherwise. This limits how confidently the AI gain represents generalization to genuinely new text and is retained as a concrete research limitation; no arbitrary decontamination penalty is applied.

### Training and evaluation arithmetic

The pinned[training repository](https://github.com/TartuNLP/llammas/tree/3e94fe3c6db99a297014bca31cd1d8beab3bf20d) sets 19080 updates,8 processes,16 examples per device,2 accumulation steps and 1024-position packed sequences: **5,001,707,520 training positions**. The 75/25 mix is over documents, not an exact token-language fraction. Prior Llama 2 training and unrelated ablations are excluded.

The requirements point to taidopurason/transformers@LUMI. Its retained 33f3d7d5db6994bac3ae320ecf937d8aef4e1c95 commit predates training. The released loading call does not request FlashAttention, and its LlamaDecoderLayer uses dense LlamaAttention unless the Flash flag is set. QK and AV compute full square attention followed by masking. The trainer enables configured gradient checkpointing; modeling code checkpoints each entire decoder layer. Thus dense attention with full layer recomputation is the source-backed central choice, not an inference from generic Llama defaults.

Let M=L(4d²+3df). A length-S transformer forward uses 2SM+4LdS² matrix operations. Training counts four times this block forward (forward, two backward-equivalent matrix passes, one checkpoint recomputation), plus three output-head forwards 2SdV. The head lies outside the checkpointed layer. Adam bookkeeping is estimated 10 operations per parameter per update, a tiny addition. Embedding lookup, norms, activations, softmax and memory traffic are not exhaustively counted; this is dominant matrix-operation accounting, with optimizer work explicitly added, not hardware runtime conversion.

The source evaluates every 1272 steps, giving 15 checks including the final step. `valid_data.json` is not released. Central monitoring assumes 1024 sequences of 1024 positions per check. This is a disclosed missing-size estimate, not recovered validation data. Monitoring contributes 2.16285e17 FLOPs,0.079% of total;0 and 16384 sequences/check scenarios quantify its modest effect. No native validation-length claim is made. The retained final Belebele prompts are tokenized with the released model tokenizer; four independent one-letter likelihood scores and a full output head are conservatively counted. Their 1.9609e15 FLOPs are negligible. The later evaluation is used only to identify the capability endpoint; no other subsequent benchmark campaign is charged.

Main total 2.74023e20; no-checkpoint alternative 2.06555e20; triangular-attention alternative 2.68657e20; very large validation alternative 2.77267e20. The no-checkpoint alternative is diagnostic, contradicted by the released configuration. Token field includes training positions only, as defined by `training`; monitoring and endpoint evaluation are separately included in FLOPs. One complete run is the unit: compute statistic `total`, subset `all`, attempts 1.

### Reproduction

Run `python recompute.py --sources /path/to/sources/llammas-estonian --output /path/to/new-calculations.json` with sentencepiece installed. The calculator requires a new output outside source evidence, performs no model execution and records source hashes, exact inspected examples, formulas and scenario values. Use the retained pinned sources, not later versions of their upstream repositories.
