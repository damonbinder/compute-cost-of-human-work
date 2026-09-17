# BabyBERTa: acquiring child-vocabulary grammatical contrasts

**The human-learning estimate in this note is superseded.** On 2026-09-14 the
human side of every row it covers was re-estimated as the active hours to reach the
capability the run bought, read off a published hours-to-proficiency table, rather
than the hours to move a benchmark score. The current figures, the method and the
per-row arithmetic are in [skill-acquisition human learning time](../skill-acquisition-human-time.md).
Everything else here — the endpoints, the task inspection and the compute
reconstruction — still stands.

## lang-lacq-zorro-babyberta

Train three BabyBERTa initializations and select the best; each is trained from random initialization on AO-CHILDES to the paper's 260,000-update checkpoint. Target: approximately 80.5% agreement with the original Zorro labels on unseen English minimal pairs using 571 content words and 23 grammatical paradigms. Human comparator: an ordinary literate adult, already competent in another language and able to read alphabetic text, initially knowing no English, learning vocabulary and grammar to this recognition target. It is not a claim about an infant's development, native fluency, or 80.5% of English generally.

Central compute is **1.3134425203e16 FLOPs** for all three training trajectories including monitoring and selection; human learning is a coarse **40 active hours (144,000 seconds)**. Human target performance is matched by construction, not measured in a Zorro human cohort.

## Original endpoint and selection

The [original paper](https://aclanthology.org/2021.conll-1.49/), Table1/§3.1, reports80.5 at260k updates. Footnote5 explicitly says the authors selected the top-scoring model from three random initializations. This is separate from the later domain-comparison averages over10 replications. The [original CONLL2021 benchmark tag](https://github.com/phueb/Zorro/tree/b2af8d51052fa9710f778040dde985d64791010d) retains three complete endpoint result sets under runs/huggingface_BabyBERTa_5M: 0_excluded scores78.3391%,1_excluded78.5783%, and2 scores80.5196%. The calculator checks each scored sentence against the original corresponding test string and reconstructs all23 paradigm results. Thus run2 is supported by both the selection statement and the original files, not inferred just because a score rounds to80.5.

The central work unit is the experiment that trained three candidates and selected the reported model. It counts all three rather than charge only the winning trajectory. The single-lineage alternative is 4.3781417343e15 FLOPs; it is retained to distinguish the cost of this particular final model’s updates from the cost of acquiring it through the reported selection process. Broader model/hyperparameter development is not included. No other run is called zero-cost or silently incorporated into the endpoint's denominator.

Use the paper's original tagged sentences/8192 files. The author's October 2021 update changes proper-name casing and content-word pairings; an initial download of that update is kept in scratch-audit, not used in the final calculation. There are 23 files, 4,000 sentences per file, or 46,000 pairs. The paper explicitly did not collect human agreement judgments for this test suite. Its comparison with BLiMP human agreement is a conjecture, not an observed Zorro human baseline.

## What the human has to learn

The paper's Table 5 and the retained original pairs show several distinct demands:

- Six determiner/subject–verb agreement paradigms require regular number marking, auxiliaries and resisting an intervening adjective, prepositional phrase or relative clause. For example, the head noun rather than an intervening noun controls singular/plural agreement.
- Anaphors, case, ordinary word order, irregular verbs and the local-attractor question require pronoun forms and common inflection/verb-pattern knowledge. The content vocabulary is small; unfamiliar adult encyclopedic vocabulary is not the main obstacle.
- Argument structure, binding and filler-gap contrasts require interpreting clauses and distinguishing permissible complements, not merely memorizing an -s suffix.
- N-bar ellipsis, two island paradigms, two negative-polarity paradigms and quantifier restrictions are less directly covered by elementary language lessons. Some constructed contrasts are semantically odd or disputable outside the test's intended interpretation. We target agreement with released labels, not a supposed universal grammatical gold standard.

A learner need not master every paradigm to average 80.5%. The focused-learning estimate below targets 18 of the 23 paradigms, allowing chance performance on five harder groups. The model's actual per-paradigm accuracies are retained; the human and AI need not have the same error distribution.

## Human learning estimate

Estimate **40 active hours (144,000 seconds)** for a typical alphabetically literate adult who already knows another language but no English. The learner receives focused instruction and feedback on the tested grammatical phenomena, using new examples rather than held-out answers. The target is about 80.5% label agreement on unseen Zorro minimal pairs, with side order randomized. It is not general English proficiency.

Relevant learning evidence comes from [Batterink and Neville (2013)](https://www.batterinklab.com/_files/ugd/a9b75d_3ec8e5991750412a930c984766f82aac.pdf), *Journal of Cognitive Neuroscience* 25(6), 936–951, DOI 10.1162/jocn_a_00354. Their 23 explicitly instructed adults had no French or substantial Romance-language exposure. After approximately one hour of exposure and less than five minutes of instruction, they averaged 89% grammaticality accuracy. The miniature-French exposure used 154 content words and three agreement/word-order rules. Its test used new nouns and verbs, so the score did not require learning every tested word's meaning. The subsequent assessment and EEG preparation are excluded from the learning duration.

Zorro adds more patterns and harder interference. Its six number-agreement paradigms include prepositional-phrase and relative-clause distractors. Pronouns, irregular forms, complement frames, relative clauses and licensing conditions also need instruction. Inspection of the original generators nevertheless shows a narrow recognition task: the “binding” paradigm contrasts finite forms with an “-ing” form in fixed “think about himself/herself” frames; the two filler-gap generators use a small range of relative-clause patterns; the irregular-verb generator starts from 32 past/participle pairs before filtering. The 571 content words do not imply that every meaning must be mastered to select the well-formed member of these pairs.

A feasibility scenario reaches 80.52% overall with 89% on 18 paradigms and chance on five less secure ones: transitive-verb classification, N-bar ellipsis, two island paradigms and superlative quantifiers. This is an assumed coverage target, not observed human Zorro performance. It motivates extra practice on the 18 included contrasts while allowing errors on the hardest cases. It does not linearly convert accuracy into learning hours.

The 40-hour estimate is a coarse allowance for that focused program. One budget consistent with it is six hours of basic forms and lexical orientation, nine hours of worked rule instruction, and 3,600 new feedback pairs at an assumed 25 seconds per pair including response and correction, or 25 hours. That gives about 200 pairs per targeted paradigm, with more exposure and slower feedback than the miniature-French experiment. These components are assumed checks on the total, not independently measured durations or a tested course. The longer and less natural Zorro sentences, weaker first-language transfer for some adults, and unfamiliar label conventions justify the additional allowance.

Use **10 hours** for rapid targeted learning and helpful prior-language transfer, and **120 hours** for slow lexical/form acquisition and repeated mixed practice. These are sensitivity scenarios, not confidence bounds. The evidence establishes the approximate scale more strongly than exactly 40 hours. The estimate excludes a separate final assessment and does not assume months of retention, speaking ability or complete comprehension of every sentence.

`human_time_evidence=assumed` and `human_time_method=estimated`: the 40-hour program is an assumed budget informed by the inspected task and learning studies. The French study supports rapid acquisition of some contrasts but does not determine this duration. `human_attempts` and `human_time_subset` are `not_applicable`. Human performance is matched by the estimated target; no human Zorro score was observed. Prior first-language knowledge and explicit instruction differ from the randomly initialized model’s child-directed text input. Repeated AI benchmark monitoring and model selection differ from the proposed unseen human assessment; the comparison flags record those differences.

## Training workload

Source code is pinned at [050688b914afd998d44e5101dbecf9e2d0ff7acc](https://github.com/phueb/BabyBERTa/tree/050688b914afd998d44e5101dbecf9e2d0ff7acc). The actual model config is8 layers, width256, FFN1024,8 heads, vocabulary8192,130 position embeddings and2 token types. The rounded5M parameters in paper Table1 do not override Table3/config. Counting embeddings, attention/FFN projections and biases, norms and tied MLM head yields **8,524,032 unique parameters**. This architecture-derived count is reported under COLUMNS. The original checkpoint path first appeared in the [June9,2021 commit](https://github.com/phueb/BabyBERTa/commit/a968fa965ee04bec14c9d7b74067422e2615ea7b); that is public family availability. The point targets the reported260k checkpoint, not a claim that the separately released final weight file necessarily stops there.

Load the original 21MB AO-CHILDES corpus. Apply io.py's exact filter (at least two spaces, its implementation of three words). Disable tokenizer truncation before measuring sequence lengths; otherwise an overlong sequence would look acceptable. Exclude n>126 raw subtokens, then include BOS/EOS. Here 893,989 raw sentences become 723,524 eligible sentences and no remaining sentence exceeds 126 subtokens. The dataset generator creates min(combinations(n, 2), 10) pattern examples per sentence even under probabilistic 15% masking; short sentences therefore have fewer than 10 examples. Total expanded examples: 6,378,072.

The source shuffles those examples and uses batches of 16 padded to their longest member. The exact historical shuffle is not released. For each length, compute the finite-population probability that the maximum of 16 draws without replacement is at most that length: product over i=0…15 of (cumulative_count−i)/(N−i). Its differences give E[max]=19.287829 and E[max²]=409.153307. The mean unpadded example is 9.854649 positions. A prefix of 260k randomly shuffled batches has these same expected moments. Training therefore processes 80,237,369.74 padded token positions; it does not read the full expanded dataset to its end. configs.py explicitly says full jobs could continue beyond the paper's fixed reported checkpoint. The first batch is skipped for the initial evaluation; the counter then counts 260k actual updates.

For sequence length S, dominant forward operations per example are:

F(S)=8(8S·256² + 4S·256·1024 + 4S²·256) + 2S·256² + 2S·256·8192.

The last two terms are the MLM transform and full-vocabulary projection. utils.forward_mlm calls the full model and selects loss positions **after** logits are produced; mask fraction does not remove other positions' matrix work. Use 3F for forward plus backward matrix work. Expected training is 4.111859931e15 FLOPs. Add an explicit 14P/update optimizer-and-gradient-processing approximation, 3.102747648e13 FLOPs (under 1% of total); scalar activation/normalization costs are not separately enumerated. The original Roberta 4.3.3 code is retained. No gradient checkpointing is enabled.

## Associated monitoring

At 0, 20k,…260k the source probes every paradigm: 14 checks including the untrained baseline and endpoint. Each check runs 92,000 unmasked sentences, batches 32 with original file order and batch-longest padding, full encoder and MLM head. Holistic scoring uses one forward pass per sentence, not one pass per token. Exact original-tag padding yields 1.680388050e13 FLOPs/check, 2.352543270e14 total. No dev-split perplexity run applies because train_prob=1.0. Monitoring positions are 13,839,168 and are separate from the training-token field. The corpus/tokenizer preparation has no additional neural model calls.

One trajectory = training forward/backward + optimizer + monitoring =4.3781417343e15 FLOPs. Three trajectories to produce and select the reported best model total 1.3134425203e16 FLOPs and 240,712,109.22 training positions. All other component counts in calculations.json are per trajectory; its named total fields include selection. The random batching and 3× backward approximations make compute_evidence=derived_assumed_inputs despite reported architecture. Completely unpadded training would cost 2.091e15 and all 128-position padding 2.869e16 before optimizer/monitoring; those are architectural sensitivities, not equally plausible shuffles. The analytic selection-experiment estimate uses compute_subset=not_applicable and ai_attempts=not_applicable. The single-run alternative remains available separately; central includes both losing replicas.

## Replay

Python 3 and tokenizers. No model training, benchmark solution or checkpoint execution. Source hashes, length histograms, monitoring counts, all three endpoint scores and the formula are retained in calculations.json. To reproduce after publication:

```sh
python research/recompute.py --sources SOURCE_DIR --output NEW_JSON
```

SOURCE_DIR is the published babyberta source directory. Output must be new and outside sources. The raw original source files remain unchanged. human-source-facts.json labels web-readable originals whose direct downloads failed; it is not represented as a native downloaded PDF. The actual Cambridge grammar handbook is retained.

The additional human-learning PDFs and original Zorro generators are retained under `human-learning/` within the published source directory. `audit_pairs.py --pairs ORIGINAL_ZORRO_DIRECTORY --output NEW_JSON` reproduces the inspected-paradigm sample and duration-budget arithmetic in `pair-audit.json`; Python standard library only.
