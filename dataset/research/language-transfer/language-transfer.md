# Japanese and Arabic continual pretraining

**The human-learning estimate in this note is superseded.** On 2026-09-14 the
human side of every row it covers was re-estimated as the active hours to reach the
capability the run bought, read off a published hours-to-proficiency table, rather
than the hours to move a benchmark score. The current figures, the method and the
per-row arithmetic are in [skill-acquisition human learning time](../skill-acquisition-human-time.md).
Everything else here — the endpoints, the task inspection and the compute
reconstruction — still stands.

These reconstructions began with the original papers, model configurations and benchmark questions. No previous human-hour estimates were consulted. One Japanese candidate is submitted. The other three original leads remain pending for the reasons below.

## lang-xfer-ja-swallow7b

### Work and endpoint

The [original Swallow paper](https://arxiv.org/abs/2404.17790), Tables 1–4 and Section 4.3, describes Llama 2 7B continued for 100 billion tokens, with 90% Japanese and 10% English sampling. Vocabulary expands from 32,000 to 43,176. The selected endpoint is **JCommonsenseQA (JCQA), 38.5% → 48.1%**, evaluated on 1,119 questions with four demonstrations. Each question has five choices: random guessing is 20%, not 25%.

The human work is additional study by ordinary adult learners who already read kana, know some common kanji and basic grammar, and score approximately 38.5% on comparable unseen JCQA items. Their target is approximately 48.1% without a dictionary or AI during assessment. Prior acquisition of that starting ability is excluded. This is not a claim that 38.5% denotes A1, that 48.1% denotes A2, or that either score measures overall Japanese proficiency. The model’s other gains are not individually matched.

The historical [JGLUE v1.1 validation file](https://github.com/yahoojapan/JGLUE/blob/d176ea9f6bb1e4f3250c18aaa7720572d7548bcc/datasets/jcommonsenseqa-v1.1/valid-v1.1.json) was retained in full, not replaced by today's v1.3. Item inspection establishes a mixture of everyday vocabulary, short syntactic descriptions, written word distinctions and some cultural knowledge:

| Original ID | What must be understood | Why it matters |
|---|---|---|
| 8939 | Identify a motherboard as an electronic circuit board, among superficially similar choices | Technical noun recognition plus a short definition; ordinary computing knowledge helps. |
| 8940 | Name a landscape of rice fields | Everyday landscape vocabulary and a written compound. |
| 8941 | Distinguish an expression describing crouching/sitting from other actions | Exact lexical usage matters, not just recognizing a topic. |
| 8942 | Identify what is turned to release water | Basic description and household vocabulary. |
| 9039 | Identify a musical instrument among five nouns | A learner can succeed with partial vocabulary knowledge. |
| 9040 | Identify a traditional protective bow/charm | Japanese cultural vocabulary can remain difficult even with sound basic grammar. |

The target score leaves more than half the questions wrong. It does not require mastery of all rare cultural vocabulary. Conversely, knowing kana or using translated answer choices alone is not the target; questions and choices remain in their original Japanese.

### Human duration: 100 active hours, judgment scenario

The central estimate is **100 additional active study hours** (360,000 seconds), with a **30–300 hour sensitivity**, for a mix of written vocabulary/kanji practice, short reading, grammar consolidation and relevant everyday/cultural knowledge. This is a course-sized incremental learning block, not a proportional conversion of 9.6 score points into hours. The prerequisite is operationally defined by the starting test capability; no fixed previous number of study hours is imputed.

The primary anchor is the Japan Foundation's [Irodori FAQ, Q12–15](https://www.irodori.jpf.go.jp/en/faq.html). It estimates 80–100 hours per elementary block, explicitly including vocabulary/kanji/grammar practice rather than merely classroom activity time. Its [reading guidance](https://www.irodori.jpf.go.jp/assets/data/elementary01/pdf/Y_howto_en.pdf) includes understanding practical unannotated Japanese through partial comprehension; [Elementary 2 contents](https://www.irodori.jpf.go.jp/assets/data/elementary02/pdf/Z_contents_en.pdf) include simple articles, daily-life terms and cultural topics. These are relevant learning activities for the inspected JCQA demands. The source's hours are planned course effort, not observed JCQA acquisition times. Hence `assumed` and `estimated`, not `task_timings`, `transferred_timings` or `unit_conversion`.

Why 100 rather than a full beginner course or thousands of fluency hours: the learner already has appreciable task ability, the desired gain is modest, and the task consists of short recognition questions rather than sustained fluent composition. Why not just a few hours memorizing 107 answers: the target is generalization to comparable unseen items, not training on the validation answer key. The 100-hour scenario allows a substantive block of vocabulary and reading work. Its weakest link is that a course-sized block has not been calibrated to this particular score transition. More exposure may produce less progress when errors concern fine semantic or cultural distinctions; well-targeted instruction may produce more progress for learners whose main gap is a small set of everyday words. The sensitivity reflects those alternatives, not a statistical confidence interval.

A direct Japanese-learning study was also checked: [Senoo and Yonemoto (2014)](https://journals.lib.unb.ca/index.php/CJAL/article/view/22405), pp. 4–8 and results. It followed one already intermediate, multilingual learner over eight weeks, with one hour of guided reading weekly plus untimed independent reading. It is not a population learning curve or a total active-time observation. Its vocabulary tests and participant background do not calibrate JCQA; it is retained as a reason **not** to infer a universal vocabulary-points-per-hour rate. The central duration remains the explicit course-based judgment above.

Performance is `match` by the assumed human endpoint. This is not a measured human learning result. Humans receive structured exercises and instruction; the model learns next-token prediction from web/document text, so `different_inputs_or_tools` is flagged.

### Compute

The retained original model configuration gives 32 layers, hidden width 4,096, intermediate width 11,008, 32 attention heads/KV heads and vocabulary 43,176. Parameters are reconstructed from those dimensions. Input embeddings are lookups, so the linear-operation count uses attention/MLP matrices and the output head, rather than charging a dense input embedding multiplication.

For hidden width h, intermediate width i, layer count L and vocabulary V:

- Linear weights used in forward matrix products: `W = L × (4h² + 3hi) + Vh`.
- Parameter count: `W + Vh + (2L+1)h`, including input embeddings and RMSNorm weights.
- Linear training arithmetic: `6 × W × 100B` (forward plus both gradients).
- Causal attention training estimate: `7 × L × (4096+1) × h × 100B`. This accounts approximately for triangular QK/AV forward/backward products plus score recomputation in FlashAttention, which the paper reports using. The exact kernel packing is not measured.

Section 4.3 reports Japanese evaluations approximately every 20B tokens. The estimate includes six Japanese checkpoints, counting the diagnostic starting checkpoint, plus starting/final English evaluations. Japanese item counts come from Table 2. English multiple-choice alternatives are counted separately using Table 3 (four for OpenBookQA/HellaSwag, two for XWinograd). Each scored sequence is conservatively allotted 4,096 processed positions, including its prompt/output. These are assumed evaluation lengths, not source token counters.

Routine loss monitoring is not logged publicly. A separate **1% of training tokens in forward-only monitoring** allowance is assumed. Its 0–5% sensitivity is retained. There is no rollout or reward-model stage in this base checkpoint. Chat fine-tuning, separate hyperparameter/ablation runs and prior Llama training are excluded. Additional full-layer activation recomputation is not reported and is omitted centrally; the calculator gives an extra-forward scenario. Elementwise normalization/softmax and optimizer arithmetic are omitted; they are small relative to the matrix products.

`research/calculations.json` reports the training, benchmark-evaluation and monitoring components separately. `recompute.py` accepts explicit source/output paths, does not run training or model evaluation, and refuses to overwrite evidence. Its optional AceGPT audit requires sentencepiece; the Swallow arithmetic itself uses standard Python.

### Model identity and release

The [original project release](https://swallow-llm.github.io/swallow-llama.en.html) and [AIST announcement](https://www.aist.go.jp/aist_j/press_release/pr2023/pr20231219/pr20231219.html) establish 19 December 2023 availability. This is the base Swallow-7b-hf model, not later instruction-tuned or Llama 3-derived Swallow releases. Developer organizations: Tokyo Institute of Technology and AIST.

## lang-xfer-ja-swallow70b — pending

Table 4 reports JCQA 86.9% → 93.5%, alongside a mixed set of F1/BLEU/arithmetic changes. At this near-ceiling JCQA level, errors can concern narrow lexical/cultural distinctions rather than the elementary reading activities that anchor the 7B scenario. The inspected questions do not identify which errors distinguish the two 70B checkpoints. Reusing the 100-hour elementary block or a generic advanced-fluency course would be poorly supported. This lead needs individual error evidence or a separately justified advanced reading/knowledge-learning scenario. Its 100B-token compute is reconstructible, but no numeric human estimate is submitted merely to duplicate the 7B row.

## lang-xfer-ar-acegpt13b — pending

[Original AceGPT paper](https://arxiv.org/abs/2309.12053), Section 2.2.1 and Appendix E.1: base 13B continued on 10B tokens (6B Arabic, 4B English), context 2,048. The chat model adds SFT and RLAIF; those stages must not be mixed with the base benchmark. Original configuration and model commit history were retained. First generative weight upload is 22 September 2023; the earlier 15 September upload is explicitly a sequence-classification model and is not evidence for release of the causal language model. December weights were subsequently updated.

The paper Table 8 gives Arabic MMLU 33.76% for Llama 2 13B and 40.45% for AceGPT 13B, but nearby prose says 37.26%. All **57 released 13B subject files** were independently downloaded. They contain 14,042 questions; exact `response_answer == answer` gives **5,165 correct = 36.7825%**. The mean of 57 subject accuracies is **38.9369%**, so simple micro/macro weighting does not explain 40.45%. The retained source metrics are not a reconciliation of these published values. A historical checkpoint/evaluation-version difference remains possible. Do not silently assign the largest improvement to the current files.

The original MMLU questions were inspected, including elementary mathematics and management. Some require specialized concepts such as satisficing versus compromise, not just Arabic decoding. A human target therefore requires stated prior subject knowledge as well as Arabic literacy. The preliminary 180-hour thought experiment (a course block plus academic reading) is **not submitted as data**: its endpoint cannot currently be aligned to a consistent source result. The original [ANU Arabic course](https://programsandcourses.anu.edu.au/2019/course/arab6102/first%20semester/2143) requires six contact hours plus at least four preparation/study hours weekly for 12 weeks (120-hour minimum), but includes alphabet/pronunciation and introductory communication. It is not a calibration for a 33.76→40.45% academic multiple-choice gain.

The alternative EXAMs endpoint is also problematic. Retained test data have 537 questions: Social 272, Science 115, Islamic Studies 73, Physics 42 and Biology 35. They include regional historical/cultural curriculum, malformed text and apparent answer-key issues. It is not a clean language-only acquisition test for generic English-speaking learners. This does not prohibit eventual use, but selecting a human population and knowledge target is substantive work, not a generic Arabic-fluency conversion.

The optional calculator audit tokenizes retained MMLU prompt/response strings with the original tokenizer: 25,400,462 unpadded tokens including a one-token-per-item allowance. This is only an evaluation-work audit, not the full training cost or an inference candidate. Batched padding, other evaluations and hidden monitoring would still need accounting.

## lang-xfer-ar-acegpt7b — pending

The base 7B training is 30B tokens (19.2B Arabic, 10.8B English), rather than the 13B model's 10B. Table 8 Arabic MMLU moves 29.47→32.14%, a small near-chance gain, while EXAMs moves 23.48→31.96%. The benchmark-content concerns above apply. No generic study-hours value is assigned to this small mixed language/knowledge change. Native 7B result files are an available follow-up source, but reconciling them and defining the human prior knowledge should precede a point.
