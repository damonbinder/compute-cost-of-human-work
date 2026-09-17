# Four missing GPQA source records

These four original Epoch table records were absent from production despite completion of the assigned Epoch-prefixed leads. Their identifiers are matched directly to retained scatter_data.csv; no legacy estimates are used.

## Human baseline

The baseline is the **second expert validator**: a contractor holding or pursuing a PhD in the question's own scientific domain, hired by the [original GPQA paper](https://arxiv.org/abs/2311.12022) (§2.1, §2.3, §3.1, Appendix A.5.2) to answer the revised question after the writer acted on the first expert's feedback. Experts may use Google provided they declare it, must write an explanation, and after seeing the correct answer must give feedback and suggest revisions; on Diamond they reported sufficient expertise on 97.0% of validations. The revised question is the text the AI is scored on, so this expert is doing the AI's task, plus the explanation and feedback work.

From the [retained Diamond CSV](https://openaipublic.blob.core.windows.net/simple-evals/gpqa_diamond.csv), `Validator Answered Correctly_EV_2` gives **161/198 = 81.3131%**, reproducing the paper's Table 2 Diamond figure of 81.3%, and `Self-reported time (minutes)_EV_2` over the same 198 attempts gives a mean of **1,560.909090909091 seconds** (26.02 minutes; median 1,200 seconds; range 2 to 360 minutes; 48 reports under 15 minutes, which are retained). No filter on correctness or speed. The times are self-reported and cover explanation and feedback as well as answering, so they bound time-to-answer from above. 32 distinct people supplied the 198 second validations, and the same 198 observations are reused across every model row rather than being independent human samples per row.

Diamond admits a question only when the first expert validator answered it correctly, so `Validator Answered Correctly_EV_1` is 1 on all 198 records and the pooled two-expert figure of 359/396 = 90.66% measures the selection rule. The second expert's 81.31% is the only expert number the selection does not force, and the paper (§3.2) places true expert accuracy on Diamond between the unselected extended-set 64.8% and this 81.3%.

This replaces the earlier non-expert-validator baseline of 131/594 = 22.05%, which sat below the 25% four-choice guessing rate: that human did not do the task, so labelling an AI above or far above them said nothing. Re-anchored 2026-09-14.

Labelling follows `../COLUMNS.md`. The expert is 56.31 points above the 25% chance floor, so half of that puts the `below` floor at **53.16%**; rows under it are withheld to `agent-work/removed/excluded.csv`. `far_above` would require the AI more than 112.6 points above chance and is unreachable on a four-choice benchmark. Within the retained range, a score within five percentage points of 81.31% is `match` (76.31-86.31%), below that band `below`, above it `above`.

## AI workload and model evidence

[Epoch's output-length table](https://epoch.ai/data-insights/output-length) gives mean output tokens and best accuracy across scorers. It lacks native input, cache and failed-call counters. Input reconstruction uses the [author evaluator](https://gist.github.com/tadamcz/a61515465e34a3c66f3a78673502bc3f), actual198question texts and fourchoices, plus12assumed chat positions. The fixed choice ordering is a counting assumption; original permutations are not known. All inputs are treated as fresh. No cache or unobserved retry work is claimed measured.

Retained DeepSeekV3-family tokenizer counts R1 and V3; this is a family-vocabulary assumption for the historical endpoints. The original distilled-Llama tokenizer counts the70B distilled model, and the retained Llama3.1 tokenizer counts405B. Output already contains reasoning; do not add it again. The recipe multiplies input+output by the shared2P coefficient and omits context-dependent attention, which `compute_flops` carries separately (`research/attention-correction.md`).

Original DeepSeek model cards independently confirm37B active for R1/V3 and the distilled70B model based on Llama3.3. [Meta's original release](https://ai.meta.com/blog/meta-llama-3-1/) identifies the dense405B model. Existing model rows remain identical; no new parameter assumptions are introduced. Current direct access to Meta's gated HuggingFace card was unavailable; the independent public Meta release supplies the supporting claim.

Against the 81.31% expert baseline, DeepSeek-R1 (71.72%), DeepSeek-V3 (56.53%) and R1-Distill-Llama-70B (55.74%) are `below`, and Llama-3.1-405B (50.92%) falls under the 53.16% floor and is withheld. The human source-selection and protocol qualifications remain explicit.

## Reproduction

Run `python research/recompute.py SOURCE_DIRECTORY --models MODELS_CSV --selection research/selection.json --output NEW_JSON` with tokenizers installed. Output must be outside sources and cannot overwrite an existing file. It checks raw human data and source-row joins and retains all198input counts for each model.

## reas-epoch-gpqa-r1

Source identifier: DeepSeek-R1. Input 256.52020202; output 7594.72727273; total 7851.24747475 tokens. Coefficient 74000000000 FLOPs/token; result 5.8099231e+14 FLOPs. A20-position wrapper change alters total by0.255%.

## reas-epoch-gpqa-v3

Source identifier: DeepSeek-V3. Input 256.52020202; output 610.99494949; total 867.51515152 tokens. Coefficient 74000000000 FLOPs/token; result 6.4196121e+13 FLOPs. A20-position wrapper change alters total by2.305%.

## reas-epoch-gpqa-r1distill70b

Source identifier: DeepSeek-R1-Distill-Llama-70B. Input 269.70707071; output 10937.88888889; total 11207.59595960 tokens. Coefficient 140000000000 FLOPs/token; result 1.5690634e+15 FLOPs. A20-position wrapper change alters total by0.178%.

## reas-epoch-gpqa-llama31-405b

Source identifier: Llama-3.1-405B-Instruct. Input 269.70707071; output 619.81313131; total 889.52020202 tokens. Coefficient 810000000000 FLOPs/token; result 7.2051136e+14 FLOPs. A20-position wrapper change alters total by2.248%.

## Retained reconstruction sources

The evaluator gist revision is `69ce610eab3ffc263ade42676e29c478087dd658` (metadata updated2026-08-26). It supplies a reconstruction template, not evidence of every historical prompt. The DeepSeek tokenizer is from https://huggingface.co/deepseek-ai/DeepSeek-V3-0324/resolve/main/tokenizer.json; the distilled model tokenizer is from https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Llama-70B/resolve/main/tokenizer.json. Llama3.1 uses the retained public NousResearch family-vocabulary copy from the earlier collection. Exact retained files are identified by the SHA256 hashes in calculations.json; the earlier mirror download URL was not retained locally. DeepSeek family transfer and the assumed chat wrapper remain qualifications.
