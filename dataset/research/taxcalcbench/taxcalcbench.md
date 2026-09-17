# TaxCalcBench: two concrete 2024 returns

These four points compare two nonthinking models on two synthetic returns from the original July 2025 release. Each point averages the four saved attempts, including all incorrect answers. The human estimates cover calculation and checking from the supplied facts, with a blank form, calculator and IRS instructions. Document gathering, input preparation, filing and state returns are outside this work unit.

Original sources: [paper v1](https://arxiv.org/html/2507.16126v1) and [repository commit 8922f1af](https://github.com/column-tax/tax-calc-bench/tree/8922f1af853a32652b1c1dcbc5121dcbbd50761e). The selected originals retain their repository paths under `agent-work/sources/taxcalcbench/selected-original/`; its manifest verifies all 48 files against the original Git blobs. This is a selected two-case collection, not an estimate of the 51-case benchmark average.

## Compute

`tax_return_generator.py` formats the literal in `tax_return_generation_prompt.py` with `tax_year="2024"` and Python's default `json.dumps(input_data)`. It sends one user message to LiteLLM and saves only `response.choices[0].message.content`. We reconstruct that serialization, including escaped Unicode, and count every character of each retained answer. Provider usage, cache counters and call timestamps were not retained. Dates inside the synthetic taxpayer facts are not call timestamps.

The native configurations are `gemini/gemini-2.5-flash-preview-05-20` and `anthropic/claude-sonnet-4-20250514`, each with source setting `lobotomized`. Gemini receives an enabled thinking object with budget zero; the pinned [LiteLLM 1.72.1 package](https://pypi.org/project/litellm/1.72.1/) maps this to `thinkingBudget: 0` (`vertex_and_google_ai_studio_gemini.py`, `_map_thinking_param`). Claude receives no thinking argument. Thus there is no inferred hidden-reasoning budget to add. No worker tools or helper models are invoked. The expected XML and deterministic 19-line evaluator are evaluation machinery, not part of the model doing the return.

The closed model tokenizers are unavailable here. Counts use the retained [cl100k vocabulary](https://openaipublic.blob.core.windows.net/encodings/cl100k_base.tiktoken) as an English/JSON tokenizer proxy, with 32 additional input positions for service framing and one output termination position per call. The answer count includes the full form, blank lines and printed calculation explanations. A ±25% text-length scenario tests the proxy; the framing allowance remains fixed. These are estimated processed tokens, not provider measurements.

### Repeated-input cache estimate

`TaxCalculationTestRunner.run_all_tests` traverses model, then case. `_run_single_test` synchronously executes runs 1–4 for that case, with no intentional wait or concurrent interleaving. The README specifies four repeats. This ordering supports closely spaced identical requests, although the actual launch command and timestamps do not survive. [Google's May 8 announcement](https://developers.googleblog.com/gemini-2-5-models-now-support-implicit-caching/) says implicit caching is automatic, favors similar requests close together, and requires at least 1,024 Flash input tokens. Both prompts exceed that threshold.

Central Gemini accounting assumes the first prompt is fresh and **50% expected reuse of the exact prompt on each of runs 2–4**. Average fresh prompt work is `(1 + 3 × 0.5) / 4 = 0.625` of its token count. The 32 framing tokens remain fresh. This partial-reuse assumption is not an observed cache hit rate and does not use Google's billing discount as a FLOP factor. Sensitivities count only the first prompt fresh (0.25), or every prompt fresh (1.0). Reuse of the common instruction prefix from earlier cases could reduce work further; that is not assumed in these bounded four-run calculations. Cached-context attention is omitted by the 2P approximation and added back in `compute_flops` (`research/attention-correction.md`).

Claude's plain string message contains no `cache_control` markers. We count its full prompt on every call. No additional unseen failed calls are invented: the scope is the four persisted results per configuration. Service errors before a saved result are not recoverable from this release.

| Case / model | Prompt proxy tokens | Mean answer proxy tokens | Mean counted tokens, including allowances | Mean FLOPs |
|---|---:|---:|---:|---:|
| Single W-2 / Flash | 4,271 | 1,785.5 | 4,487.875 | 3.5903e14 |
| Single W-2 / Sonnet 4 | 4,271 | 1,564.5 | 5,868.5 | 1.1737e15 |
| HOH / Flash | 4,844 | 1,805.5 | 4,866 | 3.8928e14 |
| HOH / Sonnet 4 | 4,844 | 1,562.25 | 6,439.25 | 1.28785e15 |

Flash's first-only/all-fresh alternatives are 2.309e14/4.8716e14 FLOPs for the single return and 2.4396e14/5.346e14 for HOH. `calculations.json` retains each response, its estimated cache component, all scored amounts and separate tokenizer and parameter sensitivities. These scenarios are not confidence intervals. Compute uses each model's shared `2 × active_parameters` coefficient; context-dependent attention is not separately reconstructed.

## Human time

The baseline is an experienced US individual-tax preparer familiar with Form 1040, working without generative AI or a tax engine. The preparer may consult 2024 IRS instructions and use a calculator or ordinary spreadsheet. The target is a checked set of correct form values, with the supplied filing status and claims accepted as facts. No human timing or accuracy experiment accompanies these model outputs. The durations below are task-inspection judgments, with no contributing timed sample.

For the single return, **10 active minutes** allows reading the labeled facts and ruling out the mostly empty sections, selecting the standard deduction and tax worksheet, entering the repeated totals into a preformatted form, and checking the balance. The actual numerical work is short: one wages/withholding pair, one deduction, one tax-worksheet expression and one subtraction. The estimate includes checking the year and brackets, the step all eight model answers get wrong; it is not a whole-filing survey average. The bounds follow the same two mechanisms the HOH row names. With the year's bracket table already open and the form preformatted, the four entries and their checks plus two minutes on the labeled facts come to six minutes, 360 seconds. Looking the brackets up and re-entering and checking the empty fields adds ten minutes, 960 seconds.

For HOH, **18 active minutes**, with an 8–30-minute scenario, allows the same form work plus reviewing two W-2s, resolving five Box 12 codes in the instructions, completing the additional-tax calculation, and checking the no-dependent-claim input. The extra effort is lookup and correct routing of uncommon payroll-tax codes, not difficult arithmetic. A preparer who remembers the codes and has tables open could approach the lower scenario; unfamiliarity with the codes or manual entry/checking of all zero fields motivates the upper one. These are broad practical estimates, not stopwatch subtotals.

The human may use reference documents and a calculator; the model receives neither tool. This concrete difference is flagged. Estimated human timing alone does not create a separate assessment or population flag. “Below” is a judgment that repeated material calculation failures fall below this competent, checked-return target; no 100% observed human success rate is claimed. The paper's deterministic tax-engine baseline is not substituted for human performance.

## admin-taxcalc2024-single-w2-flash

Native case: `single-w2-balance-due-no-state-income-tax`; Flash saved runs 1–4. The age-51 single filer has wages $145,000 and withholding $12,000, with no other income or dependent claims. The [2024 IRS instructions](https://www.irs.gov/pub/irs-prior/i1040gi--2024.pdf), pages 6 and 76, give the $14,600 deduction and worksheet: taxable income $130,400; tax `130,400 × .24 − 6,957.50 = 24,338.50`, rounded to $24,339; balance $12,339. These independently calculated values match the expected XML.

Flash reports income tax $22,443, $24,041, $23,971 and $22,442. All four fail the complete-return criterion, including the $5-tolerance version. Each gets 16/19 scored lines correct (84.21%).

## admin-taxcalc2024-single-w2-sonnet4

Same case and human baseline. Sonnet reports income tax $24,274, $23,712, $24,298 and $25,456. All four complete returns fail, including the $5-tolerance version; each has 16/19 scored lines correct. These are arithmetic/lookup failures, not merely a strict-parser rejection.

## admin-taxcalc2024-hoh-box12-flash

Native case: `hoh-multiple-w2-box12-codes`; Flash runs 1–4. Two W-2s give wages `32,456 + 15,444 = 47,900` and withholding `4,444 + 1,223 = 5,667`. The input explicitly sets `hoh_planning_to_claim_child_or_dependent_credit=false`. The qualifying person's name supports the supplied HOH status; it is not an instruction to claim a dependent credit.

The $21,900 deduction leaves $26,000 taxable income. The original IRS tax table, page 67, gives **$2,792** for HOH in the $26,000–26,050 row. Box 12 codes A/B/M/N add `150 + 200 + 455 + 145 = 950` on [2024 Schedule 2](https://www.irs.gov/pub/irs-prior/f1040s2--2024.pdf), line 13 (instructions page 99). Code L's $10,000 substantiated reimbursement does not add taxable wages; see the [2024 W-2 instructions](https://www.irs.gov/pub/irs-prior/iw2w3--2024.pdf), pages 21–22. Total tax is $3,742 and refund $1,925, matching the source fixture. This calculation follows the benchmark's stated claims, rather than adding eligibility facts absent from its inputs.

Flash omits the $950 and adds a $2,000 child credit in every run. Its income-tax values are $2,770, $2,771, $2,580 and $2,750; refunds $4,897, $4,896, $5,087 and $4,917. All 4/4 returns fail, with mean line accuracy 71.05%.

## admin-taxcalc2024-hoh-box12-sonnet4

Same case and human baseline. Sonnet's income-tax values are $2,792, $2,690, $2,760 and $2,760; refunds $2,875, $2,977, $2,907 and $2,907. All omit the $950, although none claims the child credit. All 4/4 returns fail, with mean line accuracy 80.26%.

The calculator separately joins each numbered output line and reproduces the source's description-based parser. All 16 result files and their 304 scored line values agree. Whole-return failure is distinct from percentage of lines correct; many correct lines are zero.

## Model assumptions

[Google's May 20 release](https://developers.googleblog.com/gemini-api-io-updates/) identifies the exact `gemini-2.5-flash-preview-05-20` endpoint. The [June 17 announcement](https://developers.googleblog.com/en/gemini-2-5-thinking-model-updates/) says stable Flash has no model changes from that preview. The preview therefore receives its own May 20 registry date but the same shared coefficient as stable Flash.

The [Gemini 2.5 report](https://storage.googleapis.com/deepmind-media/gemini/gemini_v2_5_report.pdf) describes sparse MoE without disclosing an active count. The retained [DeepSeek-V3 model card](https://huggingface.co/deepseek-ai/DeepSeek-V3) reports 37B active; the original [Mixtral 8x22B announcement](https://mistral.ai/news/mixtral-8x22b/) reports 39B. Rounding this efficient-MoE peer scale to 40B supplies the existing Flash prior, not a discovered Gemini dimension. The broad parameter scenario is 10B–150B.

[Anthropic released Sonnet 4 on May 22](https://www.anthropic.com/news/claude-4); the `20250514` API snapshot suffix is not its public-release date. Its unchanged shared 100B estimate transfers an original [Sonnet 4.5 throughput analysis](https://unexcitedneurons.substack.com/p/estimating-the-size-of-claude-opus), whose FP8 estimate is 97.6B–109.8B, to Sonnet 4. That later-family estimate is conditional on serving assumptions and does not disclose Sonnet 4's architecture. Retain the shared 50B–200B scenario.

## Reproduction

Python 3.10+ and `tiktoken` are required. All vocabulary ranks and study inputs are local; the command makes no API calls and does not import the original benchmark or LiteLLM. From any directory, supply explicit paths:

```sh
python3 -B /path/to/research/taxcalcbench/recompute.py \
  --sources /path/to/sources/taxcalcbench \
  --models /path/to/research/taxcalcbench/model-inputs.csv \
  --assumptions /path/to/research/taxcalcbench/assumptions.json \
  --output /path/to/new-taxcalc-replay.json
```

The frozen model input file preserves the reviewed calculation independently of future registry revisions. The output must be new and outside the source directory. Source hashes and original Git blobs are checked before arithmetic; the script then reconstructs prompts, retokenizes all answers, recomputes source scores and checks the two tax calculations against the original XML.
