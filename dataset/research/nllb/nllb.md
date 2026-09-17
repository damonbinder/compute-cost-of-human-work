# NLLB-200-3.3B: English-to-Dutch chat translation

## lang-translate-chat-nllb33b-en-nl

One English chat turn translated into Dutch, averaged over the 389 English-source turns with a released NLLB baseline human rating in WMT2024's 27 rated English–Dutch conversations. Mean source length is 12.5964 whitespace-separated words. This replaces the unsupported legacy 500-word document unit with an observed source-defined collection; it is related coverage of lang-translate-doc-nllb, not a recovered document run.

Estimated compute: **4.3910125548e11 FLOPs per turn**. Estimated professional from-scratch human translation effort: **60 seconds per turn**. The quality judgment is **below** a competent professional translation, not equivalent by construction.

## Source records and quality

The [WMT2024 findings, §3.1.1](https://aclanthology.org/2024.wmt-1.59/) identifies the unmodified NLLB-3.3B baseline, sentence-level with no added context and beam size four. Source and exact baseline outputs are in the original [results repository](https://github.com/WMT-Chat-task/chat-task-2024-results/tree/394632f24291d1edcad035636b922c3e3d4dfb01), all_submissions/en-nl.csv. The exact source rows are retained in calculations.json, including references, model output, document/turn IDs and ratings.

Follow the source generate_human_ranks.ipynb: retain the last row for each model_app annotation identity; number turns in original row order within each document; join document + turn + model to the released submissions. **The annotation CSV's src_lang/tgt_lang metadata is constant for the pair and cannot select translation direction.** Filter the joined source_language=en and target_language=nl instead. This gives 389 turns and reproduces Table11's English→Dutch **82.6607/100** direct assessment. There are 263 ratings of100 and16 of0. Ratings come from professional linguists instructed to consider accuracy, grammar and conversation consistency; the clocks t1/t2 concern rating, not translation, and are not used as human translation time.

Inspecting the actual low-rated outputs supports the below judgment. For example, the account-investigation message ending in “148002 coins” is copied in English; a short greeting to NAME-F is also copied; a book-resynchronization response repeats the English source three times; one username/platform message is only partly translated. These are substantive translation failures, not just harmless paraphrases against a single reference. The mean82.66 is a quality rating, not82.66% success, and the professional comparator is not asserted to have measured score100. Most outputs are good, but the observed error burden supports below professional quality overall.

The original reference writers could see conversation context and the human evaluators assessed it; the sentence-level model did not. The proposed human is a professional translator working through the chat, with prior turns available. Therefore different_inputs_or_tools is concrete. No extra different_task flag is added merely because timing is transferred. The study limits the evaluated conversations by turn count; this point intentionally uses that same observed subset, not all2015 bilingual test turns.

## Human estimate from original timing observations

The original [DivEMT release](https://huggingface.co/datasets/GroNLP/divemt) contains raw from-scratch human translation clocks in main.tsv. This research reads those source rows afresh. Select task_type=ht and lang_id=nld. Apply the original study's >=45-minute item exclusion across all modes/languages: raw time_s identifies17 item IDs and leaves413 Dutch from-scratch observations from three professionals. The exact IDs and source hash are retained; this does not borrow any previous model's duration. time_s is the event-clock quantity, not a post-edit duration or an annotation clock.

The donor observations average21.2881 source words and106.0957 seconds. An intercept-plus-word-count least-squares description of those recorded timings is **6.3471 + 4.68564 × source words**, predicting65.3694 seconds at the target's12.5964-word mean. A simple total-time/total-word transfer predicts62.7779 seconds. Fifteen donor sentences of6–10 words average38.266 seconds, and78 of11–15 words average58.0736 seconds. For example, the sentence about rumors being “political chatter and silliness” takes22.330s; the explosion sentence takes64.706s; the sentence about running back from an accident takes22.594s. This observed variability matters more than decimal precision in the fit.

Choose **60 seconds** as a rounded mean-effort estimate for the target, slightly below the65s linear transfer: many chat turns are reusable greetings, requests and confirmation phrases rather than news/encyclopedic sentences. Other turns contain awkward English, masked entities, technical support instructions and repetition; they prevent assuming every short chat message takes only a few typing seconds. The baseline includes understanding, translating, typing and checking one turn in an ongoing chat-translation job; no customer waiting or document-management time. It does not reproduce NLLB's bad outputs. Scenarios30–90s cover a faster fluent chat translator and a slower careful professional, not formal confidence limits. The central estimate is strongly anchored in recorded same-direction professional translation work but not a measured time for these chat turns. human_time_evidence=transferred_timings, method=estimated, statistic=point_estimate; human_attempts=413 identifies the actual contributing donor timings, not the number of quality ratings.

## Model

The original [July6,2022 fairseq release commit](https://github.com/facebookresearch/fairseq/commit/26d62ae8fbf3deccf01a138d704be1e5c346ca9a) introduces examples/nllb/modeling/README.md with the **dense3.3B checkpoint link**. This supplies first public availability, earlier than the July8 Hugging Face weight upload. Model ID nllb-200-3.3b represents facebook/nllb-200-3.3B, not the54B MoE model or a distilled version. The WMT paper explicitly says it uses this model without fine-tuning.

Original HF config, unchanged architecture from the first weight upload, gives24 encoder and24 decoder layers, width2048, FFN8192,16 attention heads, vocabulary256206, ReLU, cached decoding. HF transformers4.21.0 M2M100 source supplies the attention and shared-embedding implementation. Parameter reconstruction gives encoder1,733,312,512 including the shared524,709,888 embedding weights; decoder1,611,550,720 excluding those shared weights. Total unique count3,344,863,232 is consistent with the rounded3.3B name. Decoder attention has **eight** d×d matrices per layer across self/cross attention; cross K/V are paid once per beam in inference, not omitted from stored parameters. The [original checkpoint index](https://huggingface.co/facebook/nllb-200-3.3B/blob/1a07f7d195896b2114afcb79b7b57ab512e7b43e/pytorch_model.bin.index.json) totals19,675,971,584 bytes, exactly matching four-byte weights for the reconstructed unique count plus three524,709,888-parameter embedding aliases. It includes aliases for shared/encoder/decoder embeddings and the tied output head; do not sum their storage aliases as unique parameters. Both model token coefficient and active_parameters are not_applicable because the operation recipe treats the two stacks separately.

## Inference arithmetic

Tokenize every original source and baseline output with the released SentencePiece model. Encoder length S is source pieces plus language tag and EOS, mean18.2879. Decoder work T is output pieces plus two: the decoder-start position predicts the forced target language, then target pieces and terminating EOS. Mean T=23.5578; maximum165. Tokenizer revisions move the source language tag before or after text without changing this count. Original model generation code is not released by the WMT organizers, so the HF cached implementation and token boundary recipe are disclosed reconstruction assumptions.

For d=2048, f=8192, L=24, vocabulary V=256206 and beam B=4, count multiplication and addition separately:

- Encoder: L(8Sd² + 4Sdf + 4S²d), once per input.
- Decoder cross-attention K/V: LB4Sd², once per beam, retained by use_cache.
- Per-step decoder projections/FFN: LBT(12d² + 4df). This includes self Q/K/V/output and cross Q/output; cross K/V are above.
- Self-attention score/value operations: LB4d·T(T+1)/2.
- Cross-attention score/value operations: LBT4Sd.
- Full-vocabulary output projection: BT2dV. It is tied to embeddings but still performs a matrix multiplication each decoder step.

Mean components are44.276B encoder,29.455B cross K/V,265.598B decoder linear,0.381B decoder self-attention,0.504B decoder cross-attention and98.888B output projection FLOPs. Total439.101B. No training, reference scoring or neural metric evaluator is part of producing the translation. No helper model is used in the reported baseline. Scalar normalization, activations, softmax and beam bookkeeping are omitted from this dominant-matrix operation estimate; they are small beside the dense projections, not measured zeros.

The four live beams' complete token traces and stopping lengths are unavailable. Central estimate assumes each beam processes the winning output length, a reasonable sequence-length proxy for alternatives translating the same short sentence; it is not a native beam counter and can underestimate later-finishing alternatives. A25% longer beam trajectory gives536.342B FLOPs;50% longer gives625.895B. The HF config max_length200 permits199 processed decoder steps after the initial start token, giving3.171e12 if every example ran to that limit, but the WMT paper does not establish that limit was used or that all beams ran to it. This is a stress scenario, not a reported workload. Using source-padding to the longest selected input instead of individual input lengths gives706.039B; actual inference batch/padding is unreported. The code allows both caches; cached K/V are not recomputed per step.

`tokens=94.23136` is four beams times mean decoder positions, under decoder_processed. Encoder positions remain in the operation calculation, not added to that field. compute_statistic=mean over the389 source outputs, compute_subset=all (including bad translations), ai_attempts=not_applicable for the benchmark-normalized analytic estimate. Winning text length, individual encoder lengths and architecture are retained; missing beam traces/padding make compute_evidence=derived_assumed_inputs.

## Replay

Python3 plus sentencepiece; no model weights or generation. The script accepts explicit source and shared DivEMT paths, verifies hashes and refuses to overwrite a result or place outputs under evidence directories.

```sh
python research/recompute.py --sources SOURCE_DIR --divemt-sources DIVEMT_SOURCE_DIR --output NEW_CALCULATIONS_JSON
```

After publication use dataset/sources/nllb and dataset/sources/divemt for the two source paths. The shared85MB DivEMT original is identified in divemt-manifest.json instead of duplicated. The initial parameter-count scratch result is preserved in the collection audit, not a competing published calculation.
