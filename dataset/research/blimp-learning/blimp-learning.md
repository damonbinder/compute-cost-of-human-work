# Learning the contrasts in filtered BLiMP

**Both rows this note derived are withheld.** `lang-lacq-blimp-roberta` and
`lang-lacq-blimp-llama70b` were removed from `points.csv` on 2026-09-14: a general
language model's training run buys all of its capabilities, and no principled share
of it can be attributed to the one grammar test the rows measured. The rows and the
ruling are in `agent-work/removed/blimp-skyline/`. The note stays inside the dataset
because the `llama-2-70b` model record still cites its architecture and
operation-count derivation; its human-learning estimate supports no asserted row.

Two observations reconstruct the full pretraining of the BabyLM 2023 skyline models, RoBERTa-base and Llama 2 70B. The assessment is the released vocabulary-filtered BLiMP set, not the complete original benchmark and not the models trained on BabyLM's small corpus.

## Source-defined endpoint

The [BabyLM findings](https://arxiv.org/abs/2504.08165), §5.4, explicitly identify the fully pretrained RoBERTa-base and Llama 2 70B. Table 2 rounds their BLiMP scores to 87% and 84%. The [original released results](https://github.com/babylm/submissions2023/tree/1c01b60e2c66afccda03482cc4dc77385cf69434) preserve RoBERTa skyline record 1583 and final corrected Llama 2 record 1623. Averaging their twelve native category scores gives **86.744913%** and **83.519626%**. The broader `blimp` field in model_summary.csv is not this twelve-category mean; using it would mix a different aggregate into the endpoint. Earlier Llama records differ and are not substituted for the corrected result.

The [pinned evaluation pipeline](https://github.com/babylm/evaluation-pipeline-2023/tree/17b3806376fa90c24653efe0c6c571adfb6a72c7) supplies the actual filtered archive. It has **57,812 pairs, 62 surviving paradigms, twelve categories**. A pair survives only if its words occur at least twice in the 10-million-word training corpus. Our mechanical count finds 2,405 lowercased whitespace word forms after terminal punctuation removal, including names, inflections, contractions and malformed variants; this is not a count of independent words a human must memorize. The calculator retains the vocabulary and three seeded examples per category.

The task is choosing the more acceptable sentence in a pair, with the twelve categories equally weighted. It is not writing grammatical prose, free conversation, translation or a general English-proficiency percentage. Model likelihood scoring differs operationally from a human choice but targets the same contrast. Random choice scores 50%; no original random-initialization benchmark score is asserted.

Original [BLiMP](https://aclanthology.org/2020.tacl-1.25/) human validation used native-English-speaking US respondents. Its **88.6% individual** label agreement differs from **96.4% twenty-rater majority** agreement. Those judgments cover a small sample of the original paradigms, not a measured learner curve on this filtered set. Neither number is used as a learner duration or pooled-human target here.

## Human learning estimate

The proposed human is an ordinary alphabetically literate adult competent in another language, initially without English, receiving targeted instruction and practice in the relevant written contrasts. The target is roughly 84–87% on unseen examples from this task distribution. It does not require reproducing the model's error pattern or acquiring the rest of its multilingual, factual or coding knowledge. Both rows use the same coarse **150 active hours**; the evidence does not justify resolving a 3.2-percentage-point endpoint difference into a precise extra number of hours. **50 and 400 hours** are faster and slower scenarios, not confidence limits.

This estimate was reconstructed from the task and timed learning evidence, not inherited from an earlier language row or mapped from a CEFR syllabus.

### What has to be learned

Agreement and ordinary word-order contrasts often have conspicuous local cues. However, the assessment also distinguishes permissible verb arguments and semantic classes (a person versus an inanimate picture doing the respecting), control versus raising verbs, anaphor binding through clauses, missing arguments, filler–gap dependencies, extraction islands, negative-polarity licensing, ellipsis and quantifier restrictions. For example, knowing that “declared there to be” is possible while “obliged there to be” is not requires a verb-construction distinction, not just knowing the words' translations. Some minimal pairs contain deliberately unnatural or debatable sentences; the endpoint is agreement with the released labels.

There are many shared rules across the 62 paradigms, so 62 independent language courses would overcount. Conversely, learning number agreement in a tiny language does not establish mastery of twelve equally weighted categories. At an 85% overall target, being at chance on three categories would require about 96.7% on the other nine; a learner cannot ignore all the less familiar categories and still meet the target.

### Original timed evidence and its limits

[Batterink and Neville (2013)](https://www.batterinklab.com/_files/ugd/a9b75d_3ec8e5991750412a930c984766f82aac.pdf) included 23 explicit-instruction participants among 67 adults (44 in implicit conditions), screened for no French/Romance exposure. In the explicit group, about one hour of sentence exposure plus under five minutes of instruction supported about 89% grammaticality judgments. New nouns and verbs occurred at test. This is direct evidence that some grammatical generalization can be acquired in hours rather than hundreds of hours. Its grammar was restricted to number agreement and simple word-category/order patterns; it does not directly calibrate BLiMP's semantics, binding, islands or full lexical range.

[Karpicke and Roediger (2008), original supporting methods](https://learninglab.psych.purdue.edu/downloads/2008/2008_Karpicke_Roediger_ScienceSupportingMaterial.pdf), studied forty people across four conditions, not forty full-ST learners. In the full repeated study/test condition, forty Swahili–English pairs received four cycles of five-second study and eight-second retrieval trials: **2,080 seconds of relevant learning**. Four thirty-second arithmetic distractors bring the experimental interval to 2,200 seconds, but are not vocabulary practice. The [original paper](https://learninglab.psych.purdue.edu/downloads/2008/2008_Karpicke_Roediger_Science.pdf) reports roughly 80% recall after a week for repeated-retrieval conditions. This gives a useful lexical scale check; initial translation-pair recall is neither grammatical competence nor complete contextual word knowledge. It would be inappropriate to divide 2,405 surface forms by the experimental learning rate and declare that to be English learning time.

### Why 150 hours

A targeted route combines explicit rule explanations, sentence interpretation, repeated contrast judgments with feedback, and vocabulary/verb-construction practice. The timed studies support learning local rules quickly and acquiring a limited recognition vocabulary in tens of active hours. They do not support a near-zero allowance for consolidating the harder interacting constructions.

As an effort check, several thousand varied feedback-bearing contrast exercises spread across the twelve categories would occupy tens of hours: 6,000 exercises at an assumed thirty seconds including feedback take fifty hours. This is a proposed practice budget, not an observed learning curve or a claim that six thousand trials guarantee the endpoint. Add explanation/reading and contextual lexical practice of comparable scale; repeated review and integration make an overall order of one to two hundred active hours plausible. The central 150 is a rounded judgment within that scale. It is not a sum of independently measured subcomponents, and neither the trial count nor the feedback duration is presented as sourced.

The 50-hour scenario assumes efficient targeted instruction, favorable first-language transfer and rapid recognition learning, with limited repetition. The 400-hour scenario allows slower lexical acquisition, less favorable transfer and repeated consolidation of difficult categories. The task is narrow enough that full conversational proficiency should not be charged by default, but substantially broader than the miniature-French experiment. An actual timed BLiMP learner study could materially change the central estimate.

`human_time_evidence=assumed`, `human_time_method=estimated` and `point_estimate` describe the selected practice budget. The French and vocabulary studies support its plausibility but do not determine its numerical duration. `human_attempts` and `human_time_subset` are `not_applicable`. Performance is match by the specified time-to-target construction. Prior language/literacy and teaching versus random model weights and text-only pretraining are recorded as different_inputs_or_tools.

## lang-lacq-blimp-roberta

Train the original RoBERTa-base from random weights through its full 500,000-update pretraining and assess the filtered BLiMP target. The [RoBERTa paper](https://arxiv.org/abs/1907.11692), Table 9, reports twelve layers, width 768, FFN 3072 and an 8K sequence batch. Training uses full-length 512-position examples. Interpret 8K as 8,192 centrally; a literal 8,000 scenario changes the total by about 2.3%. Total central training positions: **2,097,152,000,000**.

The release-era fairseq model has 124,696,665 unique parameters; the converted HF model adds one 768-element token-type embedding, giving **124,697,433**. This does not change the operation recipe's projection shapes. The [first public README commit](https://github.com/facebookresearch/fairseq/commit/17fcc72a641e6994bea0b14356a611a0dd6cd1a1), timestamped July 27, 2019 UTC, includes the downloadable base weights. Use that directly evidenced date rather than assuming the paper date is the model release.

For sequence length S, encoder forward FLOPs are L(8Sd² + 4SdF + 4S²d). The MLM transform and vocabulary projection add m(2Sd² + 2SdV). Original fairseq selects masked positions before the head; m=0.15 during training. Three forward-equivalents approximate forward/backward matrix operations, and an explicit 14P/update covers a small optimizer/scalar allowance. It would be wrong to use BabyBERTa's full-position MLM-head recipe for this implementation.

The later BabyLM evaluation uses HF masked pseudo-likelihood: one masked forward pass for each non-special token, returning full-sequence logits before extracting the relevant prediction. Tokenize the actual 115,624 sentences with the retained RoBERTa tokenizer, including BOS/EOS; default batch size is one, so no between-sentence padding is needed for this reconstruction. All masked passes are charged. This final assessment is about 3.55e15 FLOPs, tiny next to training.

## lang-lacq-blimp-llama70b

Train the **base Llama 2 70B**, not Chat, from random initialization through the [original report's](https://arxiv.org/abs/2307.09288) two trillion pretraining tokens. The source skyline is the fully pretrained model; no SFT/RLHF or MSGS fine-tuning is necessary for its zero-shot BLiMP score and none is silently included. [Meta's July 18, 2023 announcement](https://about.fb.com/news/2023/07/llama-2/) establishes family availability.

Dimensions are 80 layers, width 8,192, SwiGLU inner width 28,672, 64 query heads and eight KV heads of width 128, vocabulary 32,000 and untied input/output embeddings. Unique parameters: **68,976,648,192**. The retained [public NousResearch HF conversion configuration](https://huggingface.co/NousResearch/Llama-2-70b-hf/blob/main/config.json) supplies the exact dimensions; the original Meta code implements that architecture and the paper reports its rounded 70B size. Meta’s gated configuration was not publicly readable during this check, and the paper does not enumerate every hidden dimension. This is a published-configuration calculation, not an independent measurement of the weights.

For sequence length S, training forward operations are L(4Sd² + 4Sd·dKV + 6SdF + 2S(S+1)d) + 2SdV. The original [Llama 1 report](https://arxiv.org/abs/2302.13971), §2.4, explicitly skips masked causal QK scores, uses FlashAttention backward, and saves expensive linear outputs for selective recomputation. Llama 2 §2.2 adopts most Llama 1 pretraining settings. Transfer this implementation as the central estimate: S=4,096, three forward-equivalents plus one additional triangular QK recomputation per backward (L·S(S+1)d per sequence), and the small optimizer allowance. This is a source-informed implementation transfer, not a measured Llama 2 kernel counter. Monitoring uses the same triangular forward; final Hugging Face BLiMP scoring retains dense attention. Dense training attention and one full-extra-forward are explicit scenarios; the central recipe does not assume every linear layer is recomputed.

Causal final scoring uses one teacher-forced pass per sentence. Empty context gets a start token and prediction of the final continuation position leaves the processed length equal to the encoded sentence length. Actual filtered strings are tokenized using the retained Llama 2 SentencePiece model. No helper model is needed to score these contrasts.

## Monitoring, scope and replay

Neither original training report exports its periodic held-out validation counter. To avoid silently setting that work to zero, the central recipe includes an **explicit accounting allowance of one billion validation token positions**: five hundred checks of two million positions. This schedule is assumed, not attributed to either paper. It represents a modest periodic language-model check on a multi-trillion-position training run. One hundred times that allowance and zero periodic validation are retained scenarios. Central monitoring adds under 0.02% to either total, so this unknown does not drive the comparison. This is a weak assumption for associated work, not a claim to have recovered complete training telemetry.

Reported full training counts dominate. Broader architecture search and training other model sizes are outside the two specified single-checkpoint work units; unrelated downstream fine-tuning evaluations are also outside the target learning process. Scalar operations and the actual distributed kernel schedule are not individually profiled. These are analytic dominant-operation estimates, hence derived_assumed_inputs/operation_count, not measured FLOPs. Training tokens contain repeated processed padded positions; separate monitoring/final-assessment positions are not mislabeled as training tokens. Analytic AI attempt/subset fields are not_applicable; human attempt and subset fields are not_applicable for the assumed learning budget.

`recompute.py --sources SOURCE_DIR --output NEW_JSON` needs Python, tokenizers and sentencepiece and makes no model calls. It reads the retained archives, computes category means, inspects native sentences, tokenizes them and calculates the formulas. Output must be new and outside sources. It retains source hashes, selected examples, lexical forms, token lengths, component arithmetic and scenarios.

## Original GPT-2 lead disposition

`lang-lacq-blimp-gpt2large` remains a researched workload gap rather than a fabricated full-training point. Its model is identifiable and its corrected native score is 83.0239%, retained separately. The BLiMP repository explicitly records August 2021 errata: some journal Table 3/4 values are wrong; corrected native results govern. The original GPT-2 technical report gives batch 512 and context 1,024 but does not disclose the number of training updates for the released large model. Forty GB of WebText is corpus size, not processed training positions. The released small checkpoint metadata/index and hparams do not expose a training-step counter. Applying an arbitrary number of dataset passes would dominate the estimate. The two independently grounded full-training skyline points above advance the original leads while this specific missing workload remains explicit.
