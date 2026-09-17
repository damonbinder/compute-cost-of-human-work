# Microsoft Combo-6 Chinese–English translation

## Work unit and output evidence

Translate one independent Chinese news sentence into English, using the 1,000 originally Chinese sentences in WMT newstest2017 as the workload distribution. The original SGM identifies 123 native-Chinese articles; the other 1,001 sentences were translated into Chinese from English and are excluded. This is sentence translation, not production of a coherent complete document.

The [Microsoft paper](https://www.microsoft.com/en-us/research/wp-content/uploads/2018/03/final-achieving-human.pdf), Table3, defines Combo-6 as SV1/SV2/SV4, ARJT2/ARJT3/ARJT4 and DLDN2/DLDN3/DLDN4. The [released outputs](https://github.com/MicrosoftTranslator/Translator-HumanParityData/tree/52e67aefc6a703d589cbe468f4935ac350d264fa) contain all2,001 final translations and Reference-HT human translations from scratch. Line numbers join the original [WMT test SGM](https://data.statmt.org/wmt17/translation-task/test.tgz). The released human evaluation start/end times measure rating, not translation, and do not enter human_time.

The source description of DLDN variants matters: DLDN2 has a two-pass deliberation decoder; DLDN3 replaces deliberation with a conventional model trained with R2L-sampled data; DLDN4 instead adds bidirectional generation. They are not three identical two-pass deliberation models.

Inspected native-Chinese examples include a5,000RMB grant mistranslated as dollars, a registered poor household rendered as a girl who “built stalls,” and awkward administrative phrasing. These errors agree with the later professional evaluation rather than a blanket claim of perfect translation. The calculation retains every selected source sentence, actual final output and human reference, permitting inspection beyond these examples.

## Performance

The original paper's source-based sentence adequacy assessment placed Combo-6 close to Reference-HT. [Läubli et al.(2018)](https://aclanthology.org/D18-1512/), §2.3 and Figure1, explicitly reassessed Combo-6/Reference-HT on originally Chinese text. For isolated sentences, adequacy preferences were MT50%, human41%, tie9%; English-fluency preferences were MT32%, human51%, tie17%. The latter favors human translation. Document judgments also favor humans, but are not imported as this sentence task's endpoint. [Toral et al.(2018)](https://aclanthology.org/W18-6312/) independently found expert raters and originally Chinese material expose more differences than the original evaluation.

Use **below** professional human quality overall: preserving meaning and producing natural English are both part of translation. This is a collection-level judgment informed by professional ratings, not a success probability or a claim that every individual sentence is worse. The human duration targets a professional Chinese–English translator with native-level English writing, not imitation of the machine's exact mistakes. This does not claim that the Reference-HT vendors had that exact language background.

## Model identity

`microsoft-combo6-2018` identifies the named composite system. The released final text does not identify which constituent supplied the winning hypothesis. Assigning SV1 or another member as the sole producing model would invent that identity. No single per-token coefficient or parameter count describes this system; the operation recipe below includes its constituents and scoring models. The model has no verified public weight release, so its release date is blank. March2018 is the paper/output release, not evidence of public access to the model.

## Compute inputs

Paper§4.2 gives six encoder and decoder layers, width1,024,16heads, FFN4,096 for the ARJT/DLDN family and8,192 for SV. Source/target vocabularies are approximately44K/33K. All systems use beam8. Section4.2 explicitly combines eight hypotheses from each of nine systems:72 candidates. Section3.6 and the final feature list include R2L rescoring, an independently generated R2L best translation, round-trip backtranslation of every candidate, and sentence-vector similarity. Counting only the nine initial outputs would miss most work.

Original BPE merge codes, candidate lists and decoder traces are not released. We apply Jieba0.42.1 to the actual Chinese and Moses tokenization to the final English, then assume1.1 BPE positions per token plus EOS. This gives mean29.379 source and36.756 target positions. The factor is a modest vocabulary-splitting estimate for32K BPE merges on news; it is not a measured Microsoft segmentation rate. A±25% position sensitivity is retained. The central count retains all72 source-defined candidate slots for scoring. The source does not document deduplicating identical hypotheses across systems; scoring only36 unique candidates is an explicit alternative, not a claim of observed duplicate prevalence. Actual final output lengths proxy the unobserved candidate and draft lengths. Alternate translations may be longer or shorter; no success-only output selection is performed within the1,000-sentence workload.

The source names [Tensor2Tensor1.3.0](https://github.com/tensorflow/tensor2tensor/tree/v1.3.0) settings, but Microsoft's exact inference modifications are unavailable. In the retained original `_fast_decode`, self-attention K/V is cached. Encoder-attention K/V is projected inside each decoder call, with no explicit cross-attention cache. Returning more than one beam passes `stop_early=False`; the loop then executes input length plus `extra_length`, whose original default is50. We use that explicit processing regime for the eight-hypothesis generation stages, one source sentence per independent decoding group. It is an implementation transfer, not a recovered Microsoft runtime parameter. Extra lengths25/100 are alternatives.

Top-one stages can stop early. Their central processing length is1.25 times the corresponding final-language length, rounded up, with1.0/1.75 alternatives. The25% extension is a judgment allowing continued beam exploration after the eventual winning sequence; no source claims that exact stopping distribution. Backtranslation beam8 transfers the paper's global inference setting; greedy backtranslation is separately quantified. Cross-K/V hoisting is a major alternative because the actual Microsoft implementation is unavailable.

The arithmetic counts:

- Three SV encoders and eight-way n-best decoders, with FFN8,192.
- Three ARJT encoders/decoders, FFN4,096.
- DLDN2 encoder, first-pass draft generation and second-pass n-best generation, including its additional attention to the draft states.
- DLDN3 conventional encoder/decoder. Its reverse sampling was training data construction, not an extra inference helper.
- DLDN4 encoder and two decoder-direction searches. Bidirectional search details are missing; a one-direction alternative changes the total by less than2%.
- One R2L source encoding,72 teacher-forced target scores, and a beam search for the R2L-best sentence.
- E2Zscore:72 teacher-forced scores of the original Chinese source conditioned on each English candidate, distinct from the generated backtranslations used by E2ZSV. Each candidate English encoding is reused between these two operations; the reverse decoder adds6.3350199661e11 FLOPs and2,115.288 processed positions per sentence.
- Seventy-two English encodings and Chinese backtranslation beam searches.
- The shared sentence-vector encoder on the original Chinese,72 English candidates, R2L best output and72 backtranslations. Section3.5 specifies a four-layer RNN with first layer bidirectional and final width1,024. The central LSTM interpretation uses1,024 hidden units per first-layer direction, a2,048→1,024 second layer and two1,024-wide upper layers:88d² operations per token. These unspecified cell/directional details are assumptions; this component is only about1.2% of the total.
- Small sentence-vector dot products/norms, language-model score accumulation and reranker feature products. Non-neural dictionary lookups and sorting have no invented FLOP equivalent.

For width d, source length S and decoder steps T, each ordinary encoder costs6[2S(4d²+2dF)+4dS²]. Each beam decoder costs6[2T(6d²+2dF)+4dT(T+1)/2+4dTS+4d²ST]+2dVT. The final term in brackets is repeated encoder K/V projection; its hoisted alternative replaces ST with S. Teacher-forced scoring uses full dense causal-masked T² attention and one cross-K/V projection per candidate. DLDN2 adds its second memory attention. The calculator separately implements these components; no full-vocabulary head is charged to an encoder.

Central estimate: **3.683500397055174e13 FLOPs per sentence**. Backtranslations contribute2.70528561886e13, roughly73%. Cross-K/V hoisting gives1.0519876921e13; greedy backtranslation gives1.3515668220e13. Top-one length factors1.0/1.75 give3.1139e13/4.7694e13. BPE-position±25% gives2.4067e13/5.3889e13. These alternatives are processing assumptions, not statistical uncertainty intervals.

The token field is **33,226.536 decoder processed positions**, including all beams, teacher-forced scores and fixed-loop padding. Encoder and recurrent-encoder positions are counted in the operation recipe, not added to that token field. This is `derived_assumed_inputs`, `operation_count`, `point_estimate`, with AI subset/attempts not_applicable: the72-candidate processing recipe is estimated across a source-defined text distribution, not a measured set of complete execution traces.

## Human duration

[Weng and Morett(2026)](https://doi.org/10.1371/journal.pone.0352322), Methods3.1–3.4, studied30 experienced professional translators and35 postgraduate novices. The professionals had3–23years' experience. Importantly, they translated **English into Chinese**, their native language, not the reverse. Each completed three news excerpts averaging201 English words under counterbalanced timing conditions. We use only the30 professional Free-condition sessions from the [original workbook](https://zenodo.org/records/20415080), not the imposed16m15s/20m25s caps or novice observations.

Mean TotalDur_Ms/1,000 is1,357.610039 seconds. It covers reading, drafting and revision. Participants could not consult outside resources during the task but received a seven-term glossary and could look those terms up before starting. Chinese target-word/typing-unit counts are not treated as English words.

To transfer this professional news-writing workload, normalize by the201 English source words in the donor, and multiply by the29.363 English words in the actual Reference-HT translations of the selected Chinese sentences. English represents the translated information amount on opposite sides of the two tasks; this is a language-direction transfer, not a direct matched rate. The result198.326seconds is rounded to **200seconds**. The target is a professional with native-level English writing, not the same Chinese-native donor forced to produce their weaker language. Thus the central transfer retains strong target-language production on both sides. Chinese comprehension, English versus Chinese typing, named entities and institutional phrasing can still differ; equal task speed is not established by word normalization. The source gives time for careful reading, drafting and revision, rather than a bare typing rate. We retain that scale because the inspected target sentences also need lexical choice and polished reformulation. Isolated sentences lose helpful article context but need less document-level consistency checking; there is no evidence for a directional net adjustment of a particular size. This is why200seconds remains the central estimate with100–300seconds as a meaningful alternative range, rather than an exact conversion. It should not be transferred to novice Chinese-native writers working into weaker English.

The retained CET6 Chinese→English student sessions provide a same-direction check but are not the professional timing donor. Their outputs include conspicuous grammatical errors (for example “Dong Ting Lake locates in the eastnorth”), so treating those durations as professional-quality timings without adjustment would be misleading. They are not pooled with the30 professional Free sessions, and no extra donor attempts are claimed. A further [large professional productivity study](https://arxiv.org/abs/2312.12660) covers11 European language pairs, not Chinese, and explicitly excludes briefing and research time from its work-platform clocks (§5.1). It does not provide a clean replacement or a justified language-direction multiplier. Interpreting speech-rate studies likewise cannot calibrate this written task.

Human fields are `transferred_timings`, `estimated`, `point_estimate`, subset`all`, attempts30. This preserves the actual contributing donor cohort while clearly distinguishing it from the target1,000 sentences. The timing is not an inference from the original human quality-rater timestamps.

## lang-translate-zhen-microsoft-combo6

One independent originally Chinese news sentence translated into English: **3.683500397055174e13 FLOPs /200 human seconds**, with professional-quality comparison **below** based on the later sentence-fluency assessment. All source sentences enter the length distribution, including erroneous translations.

## Reproduction

Python3 with jieba0.42.1, sacremoses0.2.0 and openpyxl3.1.5:

```sh
python /path/to/research/microsoft-translation/recompute.py \
  --sources /path/to/sources/microsoft-translation \
  --assumptions /path/to/research/microsoft-translation/assumptions.json \
  --output /path/to/new-calculations.json
```

The output must be new and outside sources. The script reads the original SGM, released translations and donor workbook, retains their hashes and selected records, and computes all scenarios. It makes no model or API calls.
