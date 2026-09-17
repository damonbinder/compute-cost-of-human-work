# DivEMT English translation

Six points compare raw mBART-50 one-to-many translations with professional translation from scratch, one target language per point. Both coordinates are arithmetic means over the same 413 English sentences. Post-editing time and post-edited output are never used as the AI workload or human translation-time baseline.

## Sources and work unit

Original paper: https://aclanthology.org/2022.emnlp-main.532/ (Sarti et al., EMNLP 2022); original repository: https://github.com/gsarti/divemt; processed data: https://huggingface.co/datasets/GroNLP/divemt. Retained originals are `agent-work/sources/divemt/paper.pdf`, `paper.txt`, `main.tsv`, `parse_utils.py` and the repository tree. `agent-work/sources/divemt/paired-calculations.csv` retains every paired item, human and machine unit identifiers, timing, token lengths and operation components; `agent-work/sources/divemt/calculation-summary.json` contains summaries and the exact exclusion list. `agent-work/sources/divemt/recompute.py` reproduces the numerical calculation with SentencePiece.

The main TSV has 7740 records: 430 items × six languages × three modes. For each language and item, select the HT row's `src_text` and `time_s`; pair it with the PE2 row's `mt_text`. PE2 `tgt_text` is human-edited and is not the machine output. All paired source strings were checked equal, and all pairs exist exactly once. Three professional translators per language split the task modalities across documents; there are 413 timed HT sentence attempts per point, not 1239. The task is sentence translation, not a full document job. The source sentences come from Wikinews, Wikibooks and Wikivoyage.

Paper section 3 and Appendix C establish professional experience, publishable-quality instructions, self-review, source article access and permitted internet terminology research without machine translation. Human timer records the sentence's editing-mode interval; translators were told to leave editing mode for unrelated activities. This includes relevant thinking and reference lookup, not only keystrokes. Human source/article access differs from sentence-only MT and is flagged. No claim is made that all final professional text received an independent quality audit.

## Timing and filter

Use the source's derived `time_s`, exactly `event_time / 1000` in `parse_utils.py` line 337. This reconstructs active annotation sessions from events. It differs from PET's separate `edit_time` field in 54 of 7740 rows; silently substituting that column changes the means. Human time is the arithmetic mean of HT `time_s`, hence task_timings / other_calculation / mean. All retained attempts are used, without selecting success. The raw timing filter is independent of outcome.

Following Appendix D's rule, exclude any item whose `time_s` is at least 2700 seconds in any mode or language, then exclude that item everywhere. This gives 17 items and 413 remaining. The paper prints only 16 item identifiers despite saying 17; the raw-derived extra is document 13 sentence 2, `flores101-main-132`. We apply the stated rule to the raw data, not the incomplete printed list. Exact excluded item IDs:

- `flores101-main-1001`
- `flores101-main-1003`
- `flores101-main-1021`
- `flores101-main-1061`
- `flores101-main-1072`
- `flores101-main-1074`
- `flores101-main-132`
- `flores101-main-243`
- `flores101-main-284`
- `flores101-main-31`
- `flores101-main-32`
- `flores101-main-331`
- `flores101-main-332`
- `flores101-main-403`
- `flores101-main-412`
- `flores101-main-503`
- `flores101-main-541`

## Model

The paper section 3.4 identifies mBART-50 one-to-many; Appendix F says Hugging Face Transformers default decoding was used for the model evaluation. This is evidence for the default recipe, not a retained execution trace. The original release config and current retained config both specify 12 encoder layers, 12 decoder layers, dimension 1024, FF dimension 4096, 16 heads, vocabulary 250054, beam count 5, early stopping, max length 200 and use_cache=true. None of the retokenized outputs approaches 200 steps. No task-specific generation script or beam trace was found in the source repository.

Release date is 2021-02-12: commit `76c3ed36313be529dfd8899d31ab35a5f40d4feb` added the configuration, tokenizer and 2.44 GB PyTorch weights. Retained `model-commits.json`, `release-tree.json` and `release-config.json` establish this; it is not inferred from a paper date. URLs: https://huggingface.co/facebook/mbart-large-50-one-to-many-mmt/commit/76c3ed36313be529dfd8899d31ab35a5f40d4feb and https://huggingface.co/facebook/mbart-large-50-one-to-many-mmt/blob/76c3ed36313be529dfd8899d31ab35a5f40d4feb/config.json.

Parameter bookkeeping is derived from configuration and original Transformers MBart implementation: https://github.com/huggingface/transformers/blob/v4.11.3/src/transformers/models/mbart/modeling_mbart.py (retained locally). Shared vocabulary embeddings contain 250054×1024 = 256055296 weights and also provide the output head. Assign shared embeddings to the encoder once. Each stack has 1026×1024 positional weights, embedding layer norm and final layer norm. Encoder layers contain four attention matrices, two FF matrices, their biases and two layer norms; decoder layers add cross-attention and a third layer norm. This gives encoder 408264704 and decoder-exclusive 202614784, total 610879488. Counts are marked reported: COLUMNS.md includes calculation from published architecture without assumed dimensions; a checkpoint tensor audit is not required. The output-head arithmetic is still counted even though its weights are tied.

## Operation count

The source tokenizer's `_tokenize` uses SentencePiece, with English language prefix and EOS suffix (`tokenization_mbart50.py`, lines 215 and 287–305): https://github.com/huggingface/transformers/blob/v4.11.3/src/transformers/models/mbart50/tokenization_mbart50.py. Encode the actual HT source and raw PE2 machine string with the retained model tokenizer. Let S = source SentencePiece length + 2 and T = raw machine SentencePiece length + 2. T includes the initial decoder EOS step predicting the target language and the final step predicting EOS. Five beam hypotheses each process T positions, so the CSV's decoder_processed tokens are mean(5T); encoder positions remain in this calculation rather than mixed into that field.

For d=1024, f=4096, L=12, B=5 and V=250054, count multiply-add as two operations:

- Encoder, once per source: L × (8 S d² + 4 S d f + 4 S² d).
- Cross-attention key/value projections, once per beam and encoder sequence: L × B × 4 S d².
- Cached decoder: L × B × [12 T d² + 4 T d f + 2 d T(T+1) + 4 T S d]. This includes self Q/K/V/output, cross Q/output, feedforward, growing self-attention and cross-attention score/value products.
- Full vocabulary head each decoder step: 2 B T d V.

Compute each sentence separately and then average; nonlinear attention terms do not use only mean length. Learned embedding lookup is not a dense matrix multiply. Small bias, normalization, ReLU, softmax and beam bookkeeping operations are omitted. No GPU peak-rate proxy is used.

The substantial assumption is that all five beams continue for the retokenized winning output length. Actual alternative beam lengths and batching/padding are unavailable; detokenization/retokenization can also alter the exact original token sequence. The default five-beam cached recipe is therefore derived_assumed_inputs, not measured operations or a single-parameter coefficient. AI attempts is not_applicable because this is a normalized analytic per-sentence workload, not a measured run sample.

## Performance interpretation

The professional post-editors' changes to raw MT inform the below classification. HTER is the word-normalized edit count between raw MT and their final output; it is not a success probability and includes stylistic edits. The low number accepted unchanged and substantial median edit burden support a broad below-professional judgment, not a claim that every edit repairs a factual error. We inspected source/MT/edited examples for each language. For example, an Italian output renders people being passed by commuters as being watched; a Ukrainian output contains mixed-language text. Some Dutch changes are predominantly stylistic. These examples illustrate why an edit rate is evidence for broad quality rather than an exact error count. The final human post-edit is an assessment artifact, not part of AI-only completion.

## divemt-mbart50-en-ara

Arabic: 413 paired sentences. Mean HT active time 121.675852300 seconds (median 76.189; not the chosen statistic). Using the distinct edit_time column instead would give 120.990276029 seconds.

Mean encoder positions 31.484261501; decoder steps per beam 34.832929782; total decoder positions 174.164648910. Mean components: encoder 9561495120.581, cross K/V 7923273837.094, decoder 61829377859.564, vocabulary head 89191561458.983 FLOPs. Total 168505708276.223 FLOPs per sentence.

Median raw-MT-to-post-edit HTER 35.714%; 11/413 unchanged outputs. Label: below professional publishable-quality translation.

## divemt-mbart50-en-ita

Italian: 413 paired sentences. Mean HT active time 166.440295400 seconds (median 115.153; not the chosen statistic). Using the distinct edit_time column instead would give 163.784537530 seconds.

Mean encoder positions 31.484261501; decoder steps per beam 35.239709443; total decoder positions 176.198547215. Mean components: encoder 9561495120.581, cross K/V 7923273837.094, decoder 62551899168.232, vocabulary head 90233142324.068 FLOPs. Total 170269810449.976 FLOPs per sentence.

Median raw-MT-to-post-edit HTER 25.806%; 35/413 unchanged outputs. Label: below professional publishable-quality translation.

## divemt-mbart50-en-nld

Dutch: 413 paired sentences. Mean HT active time 106.095719128 seconds (median 74.231; not the chosen statistic). Using the distinct edit_time column instead would give 105.891830508 seconds.

Mean encoder positions 31.484261501; decoder steps per beam 34.438256659; total decoder positions 172.191283293. Mean components: encoder 9561495120.581, cross K/V 7923273837.094, decoder 61125763409.201, vocabulary head 88180980024.407 FLOPs. Total 166791512391.283 FLOPs per sentence.

Median raw-MT-to-post-edit HTER 26.316%; 30/413 unchanged outputs. Label: below professional publishable-quality translation.

## divemt-mbart50-en-tur

Turkish: 413 paired sentences. Mean HT active time 86.449215496 seconds (median 59.907; not the chosen statistic). Using the distinct edit_time column instead would give 86.158733656 seconds.

Mean encoder positions 31.484261501; decoder steps per beam 31.518159806; total decoder positions 157.590799031. Mean components: encoder 9561495120.581, cross K/V 7923273837.094, decoder 55929922150.896, vocabulary head 80703917385.763 FLOPs. Total 154118608494.334 FLOPs per sentence.

Median raw-MT-to-post-edit HTER 36.842%; 23/413 unchanged outputs. Label: below professional publishable-quality translation.

## divemt-mbart50-en-ukr

Ukrainian: 413 paired sentences. Mean HT active time 182.144644068 seconds (median 138.486; not the chosen statistic). Using the distinct edit_time column instead would give 178.719651332 seconds.

Mean encoder positions 31.484261501; decoder steps per beam 36.687651332; total decoder positions 183.438256659. Mean components: encoder 9561495120.581, cross K/V 7923273837.094, decoder 65130522579.370, vocabulary head 93940674212.881 FLOPs. Total 176555965749.927 FLOPs per sentence.

Median raw-MT-to-post-edit HTER 57.692%; 2/413 unchanged outputs. Label: below professional publishable-quality translation.

## divemt-mbart50-en-vie

Vietnamese: 413 paired sentences. Mean HT active time 167.806658596 seconds (median 108.021; not the chosen statistic). Using the distinct edit_time column instead would give 162.405699758 seconds.

Mean encoder positions 31.484261501; decoder steps per beam 36.561743341; total decoder positions 182.808716707. Mean components: encoder 9561495120.581, cross K/V 7923273837.094, decoder 64902995829.153, vocabulary head 93618280135.593 FLOPs. Total 176006044922.421 FLOPs per sentence.

Median raw-MT-to-post-edit HTER 44.444%; 3/413 unchanged outputs. Label: below professional publishable-quality translation.

