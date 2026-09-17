# AceGPT 13B: additional Arabic academic study

**The human-learning estimate in this note is superseded.** On 2026-09-14 the
human side of every row it covers was re-estimated as the active hours to reach the
capability the run bought, read off a published hours-to-proficiency table, rather
than the hours to move a benchmark score. The current figures, the method and the
per-row arithmetic are in [skill-acquisition human learning time](../skill-acquisition-human-time.md).
Everything else here — the endpoints, the task inspection and the compute
reconstruction — still stands.

## lang-xfer-ar-acegpt13b-base

One 10B-token continued-pretraining run costs an estimated **8.22890e20 FLOPs**. The human estimate is **100 active hours** of additional study to improve the source-weighted Arabic MMLU score from approximately **33.76% to 40.45%**, starting with basic Arabic reading and relevant prior subject knowledge. This is an explicitly noisy benchmark endpoint, not a claim of general Arabic fluency.

## Endpoint and source identity

The original [AceGPT paper](https://arxiv.org/abs/2309.12053), Table 8, identifies Llama2-13B and AceGPT-13B-base. The verified author repository's 13B few-shot metrics reproduce **40.454615%** with the original nested averaging code. The body paragraph's 37.26% is inconsistent with both that table and the released metrics. The [shared 7B study](../acegpt-learning/acegpt-learning.md) explains the common benchmark construction and aggregation; this point uses its own model workload and human route.

The baseline is less securely reconstructed. No Llama2-13B metrics or answer archive exists in the pinned repository tree. Table 8 directly reports 33.76%, but averaging its displayed domain numbers gives 33.9825%. Retain the explicitly reported overall baseline and show 33.98% as a sensitivity, rather than silently claim exact reproduction. A 0.22-point ambiguity does not determine the coarse human study budget. The final raw score is directly reconstructed.

The first September 15 HF upload was a sequence classifier: its original index contains `score.weight` and no `lm_head.weight`. The September 22 causal upload contains the full language-model head and all six weight shards, with index total 52,063,457,280 bytes. Therefore **2023-09-22** is the supported first public causal-model family date. December replacement weights exist, and evaluation records do not pin a particular HF revision. The date is not an assertion of byte-identical weights throughout this history. Retained configs/indexes establish the distinction without downloading model weights.

The architecture is 40 layers, width 5120, FF width 13824, 40 query/KV heads and a 32000-entry vocabulary, with untied embeddings. It has **13,015,864,320 parameters**; four bytes per parameter exactly reproduces the original causal index's total size. The model is the base, not the chat/RLAIF system.

## Actual task and defective questions

I inspected 24 seeded native final-model questions across six subjects, retained in the calculation. They require mathematics, biology, anatomy, reasoning and institutional knowledge, not just translation. Examples include PAC fundraising, federal versus state authority, subtracting business losses from profits, and relations between blood flow and anatomy. The model both succeeds and fails on elementary items; an English-readable equation is not a reliable proxy for Arabic academic comprehension.

The inspection also exposed major original data corruption. The separate [audit](corruption-review.md) identifies **1,489 repeated IP-spoofing-family questions** across 50 subjects, occupying **9.50184% of the source's nested score weight**. Options are effectively repeated but keys differ. The model records exactly match the original CSVs, so this is not a join error. A biology question about nineteenth-century “Soviet” Lysenko and malformed mathematical items illustrate other translation/content defects; the duplicate audit is not exhaustive.

The human target is to improve the aggregate score through meaningful questions while retaining the benchmark's defective scoring component. It is not to memorize wrong keys. If the defective family yields an illustrative 25% expected score, the reported transition corresponds to about **34.68% to 42.08%** on the remaining weighted material. This is only a composition sensitivity, not a regraded model result. The baseline alternative of 33.98% changes this interpretation slightly, without establishing a different course or skill level.

## Independent human route

The selected person is an ordinary university-educated adult learning Modern Standard Arabic as an additional language, able to decode script and basic sentences, already scoring near the stated baseline. Their relevant subject knowledge in a fluent language is sufficient to exceed the final target. Prior Arabic and subject study is outside this additional-learning unit, just as the model excludes Llama2 pretraining. These prerequisites are important: the point does not say a beginner can acquire professional knowledge across all MMLU disciplines in 100 hours.

The central route is **30 hours** of academic vocabulary and sentence relations, **40 hours** of guided reading across familiar subject areas, and **30 hours** of mixed unseen question practice and review. Compared with merely recognizing isolated terminology, getting around two-fifths of this difficult mixed material right calls for parsing relations, distractors, negation and short explanations while refreshing familiar concepts. It still permits most questions to remain wrong. Study is not limited to the released questions and does not require mastery of all professional topics.

The **100 hours** is a fresh practice-budget judgment. It was not obtained by scaling the accepted 7B duration or multiplying score gain by a fixed learning rate. For example, twenty study blocks of five active hours can combine explanations, new reading, vocabulary review and later testing on different material. The source target begins with a stronger but incompletely observed baseline; a larger final gain does not imply a universal number of hours per percentage point.

Original provider descriptions offer a scale check, not timing donors. [Oxford Centre for Islamic Studies](https://www.oxcis.ac.uk/modern-standard-arabic) describes a 36-hour academic-reading-oriented course for learners with prior study or placement readiness. [SOAS](https://www.soas.ac.uk/study/find-course/arabic-modern-standard-intermediate-course) describes 20-hour modules containing taught and guided independent work. A sustained targeted program on the order of a few such modules, with substantial review, is plausible for improving access to already known concepts. These descriptions do not establish either benchmark level, and their full prerequisite courses are not charged again.

**30–300 hours** are retained as scenarios. The shorter route covers a learner close to the required receptive vocabulary; the longer route allows weak technical reading and substantial review. Defective items, baseline ambiguity and unknown prior human language history make a narrow uncertainty range inappropriate. Evidence is `assumed`, method `estimated`, with no empirical timing donor or human attempt count. `match` states the constructed final-score target, not observed human parity. Human instruction and feedback differ from corpus-only training; no clean language-acquisition interpretation is asserted.

## Full compute reconstruction

Paper §2.2.1 specifies **10B continued-training tokens** for 13B, comprising 6B Arabic and 4B English. Appendix E.1 supplies sequence length 2048, global batch 3072 and AdamW on 24 A100 80GB GPUs. Prior Llama2 training, SFT and RLAIF are not included. No fraction of base training is allocated away because the chosen endpoint is only MMLU.

For M=L(4d²+3df), the dominant forward costs are 2SM+4LdS² for transformer matrices and dense attention, plus 2SdV for the output head. Forward and backward use three equivalents. The central dense/no-checkpoint choice is an explicit assumption because original training code is not released; it is not inferred from the evaluation config. Small per-device microbatches and sharded optimizer state can make this feasible. Full-layer recomputation is a material alternative, increasing total to **1.09342e21**; triangular attention gives **7.97737e20**. Adam bookkeeping uses ten scalar operations per parameter per estimated update. Elementwise functions and memory operations are not exhaustively counted.

The approximately 1,590 optimizer steps come from the rounded token budget, not native logs. Monitoring assumes a check about every 100 updates plus endpoint: 16 checks, each 1024 sequences of length 2048. Its **9.18752e17 FLOPs** are about 0.112% of total; zero and tenfold alternatives are retained. This unknown schedule is not presented as reported.

One final evaluation is estimated from actual native prompt and visible-response lengths for 1,279 questions in six subjects, scaled to the source's 14,042 total. The final-model subset is independently downloaded and Git-verified. The native lengths are scored with the original unchanged Llama tokenizer; no output cap is treated as actual usage. Full untruncated prompt counting and six-subject workload transfer are explicit assumptions. Evaluation contributes **5.43192e17 FLOPs**, about 0.066% of total. This small uncertainty does not dominate the training estimate.

The point counts one complete run: `total`, `all`, one AI attempt. Its token field holds only the 10B weight-update positions; monitoring and evaluation FLOPs are added separately.

## Reproduction

Run `recompute.py --sources /path/to/sources/acegpt13b-learning --output /path/to/new-calculations.json` with sentencepiece installed. Inputs must be the retained original sources and output a new file outside them. No model or original evaluator is executed. The corruption audit has a separate explicit `--shared-sources` argument pointing to the accepted 7B source package; it does not modify shared evidence. Do not copy or mutate the earlier accepted candidate when publishing this separate point.
