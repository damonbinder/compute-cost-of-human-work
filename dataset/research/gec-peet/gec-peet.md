# Grammar correction with professional-editor timings

## Sources and human observations

[Vadehra et al.](https://arxiv.org/html/2510.04394v1), Sections 3.1–3.4, collected timed corrections by eight professional editors. The three conditions were source-only editing and post-editing GECToR/GEC-PD output. Editors made minimal corrections. The study excludes durations above 250 seconds and merges duplicate corrections for its timing-prediction training data. Table 3 places GECToR and human post-edited outputs at similar F0.5 scores, with humans making more edits and achieving higher recall. Exact backbone, ensemble size and GECToR checkpoint are not specified in the paper or repository README inspected.

[Original data, pinned revision](https://github.com/ankitvad/PEET_Scorer/tree/7d2330909212f0bdc0d29b2a1ccc4d120a6d7a21). `extract_timings.py` extracts the retained pickle using an allowlist of data constructors. `agent-work/sources/gec-peet/timing-records.csv` preserves the selected columns. Use each `_S` record's original `Time`, not the duplicate-averaged time, which can pool distinct editing conditions. We independently aggregate these records; their means do not exactly reproduce the paper's headline table.

## writing-gec-peet-conll14

Select CoNLL14 source sentences containing 3–50 whitespace-delimited tokens and `use250=1`. The length restriction avoids charging full human correction against the historical model's truncated 50-word input. There are 1,219 observed human corrections: median 27.486 seconds, mean 45.57585 seconds. Average source length is 21.9549 words. These are recorded survey times, including reading and entering the answer. The upper-tail cutoff follows the source; it does not establish that every remaining second was active editing. No editor metadata supports subtracting individual pauses. Median limits their influence without inventing a correction.

## writing-gec-peet-bea19

The corresponding BEA19 selection contains 4,209 human corrections: median 15.52 seconds, mean 27.05345 seconds, average 18.6788 words. The same selection is used for the AI workload calculation. Human quality observations are available at benchmark level, not separately for this length/timing subset.

## Compute reconstruction

This is an explicit architecture proxy for the study's GECToR system, not a measured run. [Original GECToR implementation](https://github.com/grammarly/gector/tree/fea1532608) maps its BERT, RoBERTa and XLNet choices to base encoders; the default is RoBERTa. The correction and error-detection heads act on word representations. The original prediction CLI defaults to one RoBERTa model and five iterations; its loop removes unchanged sentences. The released vocabulary contains 5,002 edit labels. Current released weights differ from the original paper; we do not assign their scores to this study.

Use one RoBERTa-base encoder with 12 layers, width 768, feedforward width 3,072 and 12 attention heads. `calculate_proxy.py` reproduces the retained custom wordwise byte BPE. In inference the per-word piece cap is disabled. It processes $START as three pieces ($, ST, ART), with no CLS/SEP wrappers under special_tokens_fix=1, and truncates every pass to 50 words. This reproduces the chosen historical indexer, not the unspecified PEET execution. Count unpadded per-sentence work; undisclosed batch padding could add operations. Matrix FLOPs per pass are `12*(24*n*768^2 + 4*n^2*768)`. Add the edit and binary detection heads and small scalar-operation terms. No vocabulary-generation head is executed.

Iteration estimate: charge one pass on every selected source, then one checking pass for each changed final output. Final outputs differ from source for 823/1,219 CoNLL and 2,301/4,209 BEA observations. This is a proxy for first-pass changes; final outputs do not reveal intermediate changes or reversals. Add `(147+22+2)/1312` source-pass equivalents using later correction counts in [the original paper's Table 4](https://arxiv.org/html/2005.12592v1). Interpret the allowance as approximately 147 third-pass, 22 fourth-pass and two fifth-pass equivalents per 1,312 sentences under the five-iteration cap; no sixth check is charged. The one-correction-per-later-changed-sentence convention and transfer from another GECToR configuration are assumptions. A changed last allowed iteration need not receive another checking pass. These limitations matter more than the small scalar terms.

The mean proxy workloads are 9.523013502 GFLOPs (CoNLL) and 7.893942541 GFLOPs (BEA). A single-pass version is 5.1588/4.5236 GFLOPs; three fully executed passes are 15.4764/13.5707 GFLOPs. A three-model ensemble would roughly triple any of these. These are concrete alternative configurations, not statistical uncertainty bounds. The source does not establish ensemble size; choosing one base model is a central configuration assumption supported by the original CLI default. The corresponding all-pass mean text positions are 53.6183978521 and 44.4938022979, recorded with encoder_processed. Predicted edit labels are not added as decoder tokens.

## Performance judgment

Use broadly comparable performance as the best estimate, based on the study's GECToR-versus-professional-correction comparison: CoNLL F0.5 45.82 versus 44.15; BEA 45.03 versus 45.94 under a common independently edited reference. Those professional comparison outputs were produced by post-editing, while our timings are unassisted source editing. The source-only quality is the reference for that comparison, so this is not a direct paired quality test of the timed condition. Human recall is higher, and the metric favors conservative correction. Mark `different_assessment`; do not call this exact parity or interpret the score as a percent of sentences corrected perfectly.

No human post-editing time or AI-assisted time savings enter `human_time`. The 50-word/timing-filter selection should be reviewed alongside the benchmark-level quality transfer. The main unresolved issue is the AI configuration, not the availability of human timings.
