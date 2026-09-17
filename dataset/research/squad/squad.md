# SQuAD: fixed-weight BERT question answering

## Sources and work unit

One answer span for a question and its supplied Wikipedia paragraph, averaged across the 10,570 questions of SQuAD v1.1 development data. This is reading comprehension, not open-web retrieval, explanation writing or training. The human uses the paragraph and selects an answer without AI. Ordinary English-literate crowdworkers are the typical baseline.

Original sources retained in `agent-work/sources/`:

- BERT paper Table 2 and Section 4.2: https://arxiv.org/abs/1810.04805 . `bert-paper.pdf` is v2, which distinguishes plain SQuAD from TriviaQA-augmented models.
- Original implementation and README: https://github.com/google-research/bert . `run_squad.py`, `tokenization.py`, `modeling.py`, `bert-readme.md`.
- Development questions: https://rajpurkar.github.io/SQuAD-explorer/dataset/dev-v1.1.json . Retained with the standard 30,522-entry uncased WordPiece vocabulary and large configuration.
- Human protocol: Rajpurkar et al., Section 3 and 6.2, https://aclanthology.org/D16-1264/ (`squad-paper.pdf`). This paper's numerical performance table is v1.0; do not assign those values to v1.1.
- Recorded answer timing: Ye et al., Section 5.1 pp.1604–1605 and Appendix E, https://aclanthology.org/2020.findings-emnlp.145/ (`ye2020.pdf`, `ye2020.txt`).

## Human time

Ye et al. report an average of 43 seconds for an answer and 151 seconds for an answer plus explanation. Their study includes SQuAD and Natural Questions reduced to supplied long-answer text with a single short answer. They do not provide task-separated timing counts or an exact sampling breakdown for the 43-second figure. Appendix E describes an explanation interface and payment but does not turn 43 seconds into a timing for all 10,570 BERT dev questions.

Use **43 seconds as a transferred estimate** for a typical reader to read the question/context and select the short answer. Keep the central value because this is closely related span answering, with no basis for a precise adjustment; method estimated, evidence transferred_timings, statistic point_estimate. Human_attempts is blank because the contributing answer-timing sample size is unreported. Use subset all; the source does not identify a successful-answer-only time filter. Do not substitute the model dev-set size or the explanation-annotation counts for the missing timing denominator. It excludes writing or verifying a compositional explanation.

The original SQuAD instructions recommended five answers per two minutes (24 seconds each). That is a recommended pace, not measured completion time, and article-level batching can permit context reuse. It supports a faster scenario but does not displace the recorded 43-second anchor. A reasonable duration sensitivity is 24–60 seconds for faster batched versus more deliberate reading; this is not a confidence interval. No historical salary or prior agent duration was used.

## Human performance

The original protocol treats the second annotation as one human prediction and all remaining annotations as references. It does not pool multiple humans into a superhuman consensus predictor. `recompute.py` applies that protocol to actual dev-v1.1 answers, using the official normalization (lowercase, punctuation/articles removal, whitespace) and maximum token F1 against the remaining references.

There are 10,567 questions with at least two annotations; three cannot support this leave-one-out calculation. The reconstructed human score is **91.044493% F1 and 81.527397% exact match** on those 10,567 questions. Models use all references, whereas this human calculation withholds its predicted answer. Flag different_assessment for this reference-set difference and the three-question coverage difference. The published leaderboard test human score 91.221% F1 is a separate test-set result, not the dev value used here.

The timing workers and performance annotators are not the same observed people. Both concern ordinary span-answering crowdworkers; no material skill-group difference is established, so different_human_baseline is not asserted just because identities are unlinked.

## Inference operation count

Run `python research/recompute.py SOURCE_DIR OUTPUT_DIR`. The calculator takes explicit paths, retains per-question counts, and needs only standard Python plus `six`. It imports the retained original tokenizer, replacing TensorFlow's file-opening wrapper with Python `open`; tokenization logic is unchanged. Context word splitting reproduces `read_squad_examples`, including U+202F. Question tokens truncate at 64. Document capacity is 384 minus question length minus three special positions. Windows advance by min(window length,128), and every window pads to 384.

Result: **10,833 windows**, mean **1.024881741 windows/question**. Mean processed encoder positions including padding, special positions and repeated contexts are **393.5545885**; unpadded positions average **182.9351939**. Padding still enters dense attention and projections in the original implementation. It is included in tokens/encoder_processed. Answer labels are not output language tokens.

For sequence length S=384, hidden width d, L layers, and FF width 4d, dominant FLOPs per window are:

`L * (24*S*d^2 + 4*S^2*d) + 4*S*d`.

The first term covers Q/K/V/output projections and two feed-forward maps; the second covers attention score and value products; the last is the two-logit start/end head. A multiply-add counts as two FLOPs. There is **no vocabulary-sized MLM output head** in answer extraction. Layer normalization, GELU, softmax, biases, embedding additions and CPU span ranking are omitted small terms; this is a dominant-operation estimate, not a measured hardware instruction count. The unused pooler is not on the fetched QA output path.

- Base: 12 layers, d=768: 70,666,813,440 FLOPs/window; mean **72,425,126,773.46452 FLOPs/question**.
- Large: 24 layers, d=1024: 246,425,321,472/window; mean **252,556,812,441.45468/question**.
- Seven Large models: seven full passes; mean **1,767,897,687,090.1829/question**, and 2,754.882119 processed positions/question. Combination/ranking overhead is negligible relative to seven encoders.

Single-model architecture and workload inputs are directly supported by code and dev data (derived_supported_inputs). For the published ensemble, using this identical uncased 384-window recipe for each member is an explicit assumption (derived_assumed_inputs): Table 2 specifies seven systems with different pretraining checkpoints and fine-tuning seeds but does not release their exact checkpoint/recipe set. No training or prior fine-tuning cost is included in any row.

## Models and release

Both uncased Base and Large weights are linked in the **October 31, 2018** initial release commit: https://github.com/google-research/bert/commit/fe354751d7de010f60d362ae8d9343849ec39456 . `bert-initial-commits.json` supplies its 15:19:12Z timestamp; `bert-initial-readme.md` links both model archives. The earlier October 25 commit is a placeholder; October 18 in archive names is not the public release date. The November 2 Google blog is a later announcement.

Models.csv uses separate encoder counts from the architecture: `(30522+516)*d + L*(12*d^2+13*d)` = **108,891,648 Base / 334,092,288 Large**, including embeddings, encoder biases and normalization, excluding pooler and task head. These reconstructed counts are descriptive; FLOPs use the explicit layer recipe. No single shared FLOPs/token coefficient is assigned because attention depends on sequence length. The primary model for the ensemble is the same Large architecture, with seven-member cost in the point.

## lang-rc-squad-bert-base

Plain SQuAD Base, dev 88.5 F1 /80.8 EM in BERT Table 2. Estimated **below** the human 91.04 F1 baseline: a modest but meaningful span-overlap deficit. EM is nearly matched. README's reproducible run reports 88.4125 F1, supporting this configuration without invoking a hidden augmented checkpoint.

## lang-rc-squad-bert-large-single

Plain SQuAD Large, dev 90.9 F1 /84.1 EM. **Match** to human 91.04 F1, with higher EM. README reports 90.8708 F1 for an example run and about 90.5–91.0 across runs. These are fine-tuned model results, not zero-shot pretrained BERT performance.

## lang-rc-squad-bert

Seven-model plain SQuAD Large ensemble, dev 91.8 F1 /85.8 EM. **Match** overall: slightly better F1 and stronger EM, without claiming a decisive general comprehension advantage from a 0.76-point F1 difference and unequal reference protocols. Original legacy identity is preserved here.

The separate TriviaQA-augmented ensemble obtains dev 92.2 and test 93.2 F1; neither is used for these plain-SQuAD rows. README's released example recipes differ from the paper and do not fully specify all members of the best ensemble. Thus the ensemble point has a supported seven-member architecture but an assumed common workload recipe. It is not represented as bit-for-bit reproduction of an unavailable checkpoint.
