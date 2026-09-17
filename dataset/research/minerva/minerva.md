# Minerva on MATH

Two actual configurations of the original **62.50B-parameter Minerva** answer one representative question from the 5,000-problem MATH test set: greedy generation and majority vote over256 sampled solutions. No interpolated model is used. Prior PaLM pretraining and Minerva continued training are excluded because these points measure task execution.

## Original sources and workload

[Lewkowycz et al., arXiv2206.14858v2](https://arxiv.org/abs/2206.14858v2), retained `paper.pdf`/`paper.html`, Table2 gives62.50B parameters; Table3 gives27.6% greedy accuracy and43.4% majority256 accuracy. Section2.3 specifies left truncation to1024input tokens, generation up to512tokens, and temperature0.6/top-p0.95 when sampling repeatedly. AppendixD.2 Listing2 supplies the same four-shot worked-example prompt for MATH. AppendixD distinguishes the adopted normalized-answer metric from the original stricter scorer. A correct result means a correct final answer, not necessarily correct reasoning.

Original problem text comes from the seven standard [MATH test partitions](https://huggingface.co/datasets/EleutherAI/hendrycks_math). The retained Parquet hashes are checked against their source tree; all5,000questions enter the input average. The four-shot prompt is reconstructed from Listing2's numbered lines, preserving its blank lines and printed text. Native unseen-question wrapper is not released; appending `Problem:`/`Solution:` follows the printed template. PDF line breaks can differ slightly from the original prompt string.

The original [PaLM paper](https://arxiv.org/abs/2204.02311), §2, describes a256k SentencePiece vocabulary and splitting numbers into individual digits. Native PaLM tokenizer assets were not recovered. We therefore tokenize the actual inputs using cl100k ranks with its pretokenization digit groups changed to single digits. This is a **proxy**, not the PaLM tokenizer. The p50k ranks/pattern provide a second proxy. Both retained rank files can be read offline. Mean clipped input is **712.92positions**; the alternative tokenizer gives759.5062. The1024value is an actual truncation rule, not an assumed mean. It is applied per question after adding the examples.

### Output length: an estimated transfer, including unsuccessful responses

The original [sample explorer](https://minerva-demo.github.io/) has a public JavaScript source map in its [repository](https://github.com/minerva-demo/minerva-demo.github.io). The active literal array contains326entries, after excluding commented-out examples, including219MATH outputs. This is a curated gallery, not the complete evaluation record.

| Gallery model label | MATH outputs | Correct | Incorrect | False positive | Mean proxy output positions |
|---|---:|---:|---:|---:|---:|
| `64b` |14|2|0|12|145.79|
| `540b` |205|95|92|18|165.77|

The `64b` label maps to the paper's62B model: its first line-intercept example is the same output explicitly identified as Minerva62B in Figure1. No64B model appears in the original model table. We do not turn the gallery typo into a new model. The fourteen examples are overwhelmingly false-positive demonstrations, so their mean is not a representative native62B estimate.

For the 540B gallery, correct outputs average 153.36 proxy positions, incorrect outputs 173.76, and false positives 190.39. Removing two exact duplicate response records leaves **203 distinct outputs for 200 questions**. Average distinct output lengths within each question, then give each question equal weight: **166.13 positions**, rounded to **170** as the single-response estimate. This corrects the greedy estimate's selection weights too. Both greedy and sampling use this mixed-model length transfer; the gallery does not establish either configuration's native mean.

Two questions have multiple distinct outputs: lengths 294/170/128 and 183/83. These show that responses to the same question vary, but **do not calibrate the maximum of 256 samples**. The central longest-branch estimate is a judgment: for each question, double its mean observed length and cap at the source limit of 512, then average across the 200 questions. This yields **303.5933 decoder steps**. The factor of two allows materially longer branches without assuming that every question reaches the cap. It is uncertain: factors of one and three, and all branches running to 512, are retained alternatives. Sampling unrelated questions from the pooled gallery to estimate a within-question maximum would confuse differences between problem complexity and differences between solutions.

The gallery is curated, mostly from the 540B model, and includes false-positive demonstrations. It cannot establish the 62B length distribution or the temperature-dependent tail. Figure 13 is not used as native output-length evidence: its title says “Length of targets with high BLEU score,” although the caption calls them samples; the surrounding section compares ground-truth and generated text.

### Compute accounting: a transferred execution model

Use the reported 62.50B parameters and the approximation **125e9 FLOPs per processed decoder position**. Multiply-adds count as two operations. As with other `params_tokens` estimates, this omits context-attention arithmetic and small scalar operations; `compute_flops` adds the attention term back (`research/attention-correction.md`).

The contemporary [T5X source at commit 357ba009224caabd9694edb1bad233e75e1f0989](https://github.com/google-research/t5x/tree/357ba009224caabd9694edb1bad233e75e1f0989), dated July 1, 2022, gives a more coherent implementation estimate than independently charging 256 compact prefixes. Retained `t5x-minerva-era-models.py`, `DecoderOnlyModel.predict_batch_with_aux` and `_compute_kv_cache`, compute the prefix cache **before** `num_decodes` expansion. The cache forward receives the full padded input/target array. We assume the source 1024-input plus 512-output limits define a **1536-position prefill**, even where positions are zero. Retained `t5x-minerva-era-decoding.py`, `temperature_sample` and `_temperature_sample_single_trial`, then expand that cache across samples and run the entire batch until its longest branch finishes. Finished branches still undergo forwards; masking their output does not remove their matrix work.

**This is a source-framework transfer, not proof of Minerva's actual inference configuration.** The paper identifies T5X for training but does not release its inference wrapper, padding shape or `num_decodes` grouping. The central estimate assumes one question per group, with 256 samples sharing a prefill. Greedy uses one question and one response. Unknown batching across different questions could increase greedy's decoder work; the 512-step scenario covers that diagnostic. A custom compact prefill would reduce the input work; a separate call per sample would increase repeated prefill substantially.

T5X leaves the last input position to be forwarded by each decoding branch. The final generated token is not itself forwarded, so the approximation `padded prefill + branches × generated steps` already accounts for this offset; we do not add another 255 last-prefix forwards. Cache initialization's unused dummy outputs are assumed compiler-eliminated, rather than charged as a second full prefill.

- Greedy: 125e9 × (1536 + 170) = **2.1325e14 FLOPs**.
- Majority 256: 125e9 × (1536 + 256 × 303.5933333) = **9.9069867e15 FLOPs**.

`tokens_accounting=decoder_processed` records these estimated executed positions, including padding and finished-branch forwards. They are not ordinary semantic input/output token totals. `compute_method=params_tokens` still describes the 2P multiplication. Majority voting's string processing and symbolic final-answer grading add no LLM helper calls; prior model training remains excluded.

| Majority-256 execution scenario | FLOPs |
|---|---:|
| Central: one padded prefill, two-times response-length tail | 9.90699e15 |
| One-times length tail | 5.50805e15 |
| Three-times length tail | 1.24611e16 |
| Every branch to 512-step cap | 1.65760e16 |
| Four prefills, same assumed tail | 1.04830e16 |
| Sixteen prefills, same assumed tail | 1.27870e16 |
| 256 independent padded calls, 170 steps each | 5.45920e16 |
| Compact prefill once, central tail | 9.80410e15 |

The four/sixteen-group alternatives hold the tail fixed to isolate prefill grouping; they do not claim that smaller groups have the same empirically measured maximum. All are assumptions, not confidence bounds. The first submission's compact full-prefix calculation, 2.825344e16 FLOPs, remains archived for comparison; it is not the preferred execution model after this source review.

For greedy, a compact prefill gives 1.10365e14 FLOPs, while a 512-step padded execution gives 2.56e14. A ±25% response-length proxy change gives 2.079375e14–2.185625e14. For majority, applying that proxy change before the two-times tail and cap gives 7.97832e15–1.13661e16. The `longer_output_flops` diagnostic uses 320 steps for greedy and the three-times capped tail for majority. Native PaLM tokenization could differ from either retained proxy; its uncertainty affects response-length estimates even when prefill shape is fixed.

Both configurations use `compute_evidence=derived_assumed_inputs`: source-defined MATH tasks and sampling budgets are combined with assumed execution and response lengths. The majority estimate is dominated by a cross-model length estimate from the same task collection, consistent with the existing AlphaCode treatment of same-task response examples. This classification does not make those lengths native 62B counters; proxy tokenization and borrowing another model's outputs are separate assumptions.

## Human comparison

[Hendrycks et al., original MATH paper](https://arxiv.org/abs/2103.03874), §3.1 and AppendixA.6, selected20random test problems and gave six computer-science university students an allotted60minutes, without calculators. One participant, described in the main text as a CS PhD student who did not especially like mathematics, answered8/20correctly. Other participants scored13,14,15,18and18. We use the explicitly named8/20baseline, not their average or an elite contestant's result.

**180seconds per question** estimates active use of that one-hour, twenty-question session. It is not a recorded mean solution time: the source gives the allowed interval, not individual start/stop times or actual early completion. Given the challenging questions and12not-correct answers, near-full use is a reasonable central assumption. A90-second scenario allows only half the budget to have been active; there is no evidence supporting a precise pause deduction. The two rows therefore take `human_time_low` at90seconds and `human_time_high` at the180-second budget itself, which the session allocation caps. All question opportunities are included, not just the eight correct answers. Because this is a duration-budget assumption without a measured timing donor, fields are `assumed`/`estimated`/`point_estimate`, with attempts and subset `not_applicable`.

The human skill label is `expert` in the limited sense of a technically trained CS PhD baseline, not a mathematics competition specialist or world-class solver. The description states the actual source population so this cannot be mistaken for a generic professional mathematician. The person's attitude toward mathematics does not establish lack of prior training.

The human comparison uses a20-item subset while the AI score uses all5,000test questions: `different_assessment`. Both are scored on final answers and use no calculators/external numerical tools, but the model receives four worked demonstrations: `different_inputs_or_tools`. These are concrete conditions differences; an estimated duration alone is not a flag. The original human sample is too small to establish a precise population success probability, but it is usable evidence for a best-judgment comparison.

## reas-math-minerva62b-greedy

One greedy answer, estimated mean cost across the complete original MATH test question distribution. AI27.6% versus the source human8/20=40% is classified **below**. This is a directional estimate from a small human sample, not a population significance claim. It preserves the unsuccessful model answers in compute and performance.

## reas-math-minerva62b-majority256

One final answer selected by majority vote after all256model samples, with all sampling work counted. AI43.4% versus human40% is **match** as a broad source comparison. This is an actual62.50B setting near the observed human result, not an invented interpolated parity model.

## Model and reproduction

Minerva62B was described in the2022paper; the original weights/API were not publicly released. `model_release_date` remains blank. The paper's publication date is not substituted for a release. Company: Google Research. Parameters are reported, with the62500000000value taken from Table2 rather than treating the62B name as an exact count.

Install `tiktoken` and `pyarrow`, then run:

```
python3 research/minerva/recompute.py --sources agent-work/sources/minerva --output /path/to/new-calculations.json
```

This parses retained literal data, prompt lines and Parquets; it does not execute JavaScript, load model weights or run solutions. Tokenizer tables are local. Output must be new and outside sources. `source_hashes` in the result and `agent-work/sources/minerva/manifest.json` retain provenance. Derived gallery/question JSON files are convenience inspection extracts; the calculator returns to original source-map/Parquet inputs. Source PDFs are retained with text extracts for inspection.
