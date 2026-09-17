# AceGPT base: Arabic academic-question learning

**The human-learning estimate in this note is superseded.** On 2026-09-14 the
human side of every row it covers was re-estimated as the active hours to reach the
capability the run bought, read off a published hours-to-proficiency table, rather
than the hours to move a benchmark score. The current figures, the method and the
per-row arithmetic are in [skill-acquisition human learning time](../skill-acquisition-human-time.md).
Everything else here — the endpoints, the task inspection and the compute
reconstruction — still stands.

## lang-xfer-ar-acegpt7b-base

One complete 30B-token continued-pretraining run costs an estimated **1.28763e21 FLOPs**. Human time is an assumed **60 active hours** of targeted additional study for an already literate learner improving from approximately 29.47% to 32.14% on comparable unseen Arabic academic questions. This is not learning Arabic from scratch or acquiring all the professional subject knowledge in MMLU.

### Exact endpoint and source arithmetic

[The original paper](https://arxiv.org/abs/2309.12053), Table 8, reports Llama2-7B 29.47% and AceGPT-7B-base 32.14% on Arabic MMLU. The verified [author repository](https://github.com/FreedomIntelligence/AceGPT/tree/061a656497168edd8f01ce6c03d6a4c7fa1d42d5) supplies all 57 test subjects, 14,042 questions, five-shot demonstrations and matching model metrics. The endpoint is base continued pretraining, not chat SFT or RLAIF.

The paper score is an unusual nested average. The original `eval/summary.py` averages subject accuracies within each subdiscipline, subdiscipline means within each of four domains, then the four domain means equally. Replaying that exact rule gives 29.468659% before and 32.135273% after. Averaging all 57 subjects directly instead gives 29.476543% and 31.552483%; question-weighted results also differ. Those alternatives are not substituted into the published transition. A human target must use the same nested weighting.

The four retained metric files verify against the pinned Git tree. The 13B file reconstructs 40.454615%, matching Table 8's 40.45%, rather than the body paragraph's 37.26%. Thus the body is inconsistent with both its table and released metrics, not evidence of a recovered lower-scoring run. The 13B baseline is only available in the paper table in this retained repository. A second human-learning point is deferred rather than extrapolated from the 7B duration.

### What the questions require

I inspected original test questions and paired answers from six subjects: anatomy, business ethics, elementary mathematics, high-school biology, US government/politics and logical fallacies. The 1,279 paired records join on exact question and answer text. `calculations.json` retains 24 seeded changed-answer examples and all six subject transition counts. Examples include identifying protein-coated viruses, the function of fetal vessels, a circular trunk's circumference and a US congressional committee. These require knowledge as well as language; some translations are awkward. A biology distractor becomes “archaeological coins,” and literal translation of the Ways and Means Committee obscures a proper institutional name.

The change is not a uniform language improvement: elementary mathematics gains 83 formerly incorrect answers but loses 80 previously correct ones; biology gains 55 and loses 52. Anatomy has 40 gains versus 24 losses, and business ethics 24 versus 13. The 2.67-point aggregate gain is real under the stated scoring, but cannot isolate a causal amount of Arabic language knowledge. The human work unit therefore permits vocabulary clarification, reading practice and refreshing already familiar concepts. It does not claim to teach exactly the model's changed items or charge a separate degree in every subject.

ACVA was investigated as an alternative and rejected as a cleaner human target. The retained six-item exploratory sample includes a statement calling a tarboosh a traditional Iraqi shoe with a “yes” key. That is a concrete labeling problem, not merely a demand for perfect evidence. Broad cultural generalizations and binary F1 further complicate its learning endpoint. The selected MMLU task at least supplies inspectable subject questions and before/after model answers.

### Human estimate

The human is an ordinary university-educated adult learning Modern Standard Arabic as an additional language, already able to decode the script and some basic sentences, with a starting score around 29.47% under this benchmark's weighting. They have sufficient prior subject knowledge to exceed the final target when equivalent questions are presented in their fluent language. This prerequisite prevents interpreting the duration as learning medicine, law and science from scratch. Neither the model's starting score nor the target establishes a CEFR level.

The **60-hour** central route allocates 24 hours to vocabulary and sentence interpretation, 24 to guided reading of short academic questions, and 12 to mixed unseen practice with error review. This could be twelve five-hour study blocks spread over several weeks. Work targets transferable question forms, negation, technical terms and reactivating knowledge already available in the learner's fluent language. It aims for a small average improvement while allowing many questions to remain inaccessible. Sixty hours is not proportional conversion of 2.67 percentage points, nor a claim that only the originally corrected questions need to be memorized.

Two original provider descriptions check the scale and prerequisites. [Oxford Centre for Islamic Studies](https://www.oxcis.ac.uk/modern-standard-arabic) offers a 36-hour course directed toward academic-text comprehension for learners with specified prior Arabic study or placement-test readiness. [SOAS](https://www.soas.ac.uk/study/find-course/arabic-modern-standard-intermediate-course) describes 20-hour modules including 15 taught and at least five guided independent hours, with about 180 prior formal hours as an intermediate entry route. These are course prescriptions, not observed benchmark learning durations. They show that focused reading development can occupy modules of tens of hours after prerequisites; they do not show that this target equals completion of either course. Prior study is excluded because the comparison begins at the stated existing capability, just as the AI excludes Llama2 pretraining.

The central practice budget spans several such focused modules rather than an entire language qualification. A 15-hour scenario represents a few productive vocabulary and question-interpretation corrections for a learner near the target. A 200-hour scenario allows substantial vocabulary gaps and less efficient transfer of subject knowledge into Arabic. These are judgment scenarios, not confidence bounds. Human evidence is **assumed**, method **estimated**, with no timing donor observations or attempt count. Performance is **match** because the human study target is the same final score; it is not an observed human learning experiment.

Human instruction, dictionaries during study and feedback differ from AI next-token corpus training. At endpoint testing both receive the question and five worked examples without translation tools. Public benchmark contamination and translation artifacts limit interpreting the measured gain as generalization; no unsupported contamination correction is applied.

### Model and release identity

The base family is FreedomIntelligence AceGPT-7B, initialized from Llama2-7B. Initial HF commit `5ddd685e9876c69ddab78a3fe652f937e18ab59c` on **2023-09-14** contains a causal-LM config and a full 26,953,717,956-byte weight file. This supports first public base-family availability. September 22 and November 29 weight replacements exist; released evaluation records do not pin a HF weight hash. The date is not proof that those first weights are byte-identical to the reported final model. The current architecture and initial architecture agree on 32 layers, width 4096, FF 11008, 32 attention/KV heads and vocabulary 32000: **6,738,415,616 parameters**, including untied embeddings.

The initial 13B upload on September 15 is labeled SequenceClassification, unlike its later September 22 causal-LM upload. It must not automatically inherit the earlier date as a usable base generator. Small original tree/config/history files retain this finding without downloading weights.

### Compute recipe and assumptions

Paper §2.2.1 reports 30B training tokens for 7B: 19.2B Arabic and 10.8B English. Appendix E.1 gives 2048-token context, AdamW, total batch 3072, accumulation 128 and 24 A100 80GB GPUs. Full base continued training is counted; prior Llama2 training, chat SFT, reward training and synthetic chat-data generation are excluded. No portion of training is allocated away merely because MMLU is one endpoint.

The repository does not contain the advertised pretraining implementation. The central calculation therefore assumes ordinary dense attention and no activation recomputation; these are not claimed source-measured execution settings. One sequence per GPU per accumulation microstep is small, and parameter/optimizer sharding across the stated 24 GPUs can make training feasible without requiring a specific checkpoint policy. Full decoder-layer recomputation and triangular attention are explicit alternatives. The released HF config alone does not establish the training attention kernel.

For matrix parameters M=L(4d²+3df), a transformer block forward over S tokens uses 2SM+4LdS² FLOPs, plus output head 2SdV. Training counts three matrix-forward equivalents for forward and backward. Adam is approximated by ten scalar operations per parameter per update. There are approximately 4,769 updates, derived from the rounded reported token budget; this is not a recovered exact optimizer-step count. Norms, activations, softmax and embedding-index work are not exhaustively counted.

The monitoring schedule is unpublished. Central overhead assumes a check about every 100 updates plus endpoint, 48 checks of 1,024 sequences each; it adds about 0.112% to total compute. Zero monitoring and tenfold monitoring are alternatives. This input is estimated rather than a fabricated native count. One final MMLU evaluation is estimated using actual native prompt/visible-response token lengths from the 1,279 retained paired-record subset, scaled to all 14,042 questions. The six-subject length transfer and full untruncated prompts are assumptions; this component contributes only about 0.022%. Token strings are counted with the original tokenizer. No generation cap is substituted for mean output length.

Total: **1.28763159381427e21 FLOPs**. Full-layer checkpointing raises it to **1.70840417109427e21**; triangular attention gives **1.23933680469427e21**. Source-specific absence of a training implementation makes these material assumptions, even though the model dimensions and 30B-token budget are reported. Tokens field is the 30B weight-update positions only; monitoring/evaluation work is included separately in FLOPs. One whole run is `total`, `all`, one AI attempt.

### Reproduction and retained evidence

Run `python recompute.py --sources /path/to/sources/acegpt-learning --output /path/to/new-calculations.json` with sentencepiece installed. No model or original evaluator is executed. Outputs must be new and outside source evidence. The calculator records all source hashes, reproduces the original nested score aggregation, joins paired response records and retains formulas/scenarios. The Git tree contains the identities used to verify downloaded original files. Only benchmark data, small source code, metrics, selected paired answer records and model metadata were fetched; no full model or large whole repository was downloaded.


## Benchmark corruption

Original Arabic MMLU contains 1,489 repeated IP-spoofing-family items across 50 subjects (10.604% of questions; 9.50184% of the paper nested score weight), with inconsistent answer keys. This is source data corruption, not a response join failure. Among the 1,279 released paired answers retained here, 51 belong to this family: correctness 16→18, compared with 342→391 on the other 1,228. Most gain in this subset survives exclusion, but the subset covers only 9.375% of full benchmark weight. The human target is the noisy source score, not clean language proficiency or memorization of wrong keys. Assuming 25% expected correctness on this defective family only as a diagnostic, the implied remaining-task scores are 29.94→32.88%. That small change in target interpretation does not warrant changing the coarse 60-hour judgment or 15–200-hour scenarios. The family audit is in the companion AceGPT13B study; no full clean aggregate model score is claimed. See [the retained corruption audit](../acegpt13b-learning/corruption-review.md) and its reproducible calculation.
