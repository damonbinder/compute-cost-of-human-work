# GDPval — the collection as one point per model

GDPval is OpenAI's set of real-world professional deliverables. The public gold
set is [220 tasks](https://huggingface.co/datasets/openai/gdpval) across 44
occupations and nine sectors: each task gives a written prompt and its reference
files, and asks for a finished artifact — a document, spreadsheet, slide deck,
diagram or media file — of the kind the occupation actually produces. Occupational
experts wrote the tasks, produced the reference deliverables, and graded the model
outputs blind against them.

Two rows stand on it, `work-gdpval-collection-gpt5` and
`work-gdpval-collection-opus5`. Each is the collection at its average: the mean
expert time the source publishes for the 220 tasks, against the mean per-task
compute for one model over the same 220 tasks. Eighteen further rows stand on
individual tasks, under GPT-5.4, because a third-party run published a per-task
token ledger and per-task grades for them; they are in
[exp035 per-task rows](#exp035-per-task-rows) and they do not disturb the two
collection rows.

**Why one row and not 220.** No per-task compute exists. OpenAI publishes a
collection mean, Artificial Analysis publishes collection totals, and nothing
else publishes GDPval usage at task resolution (surveyed in
`agent-work/scouting/gdpval-per-task-compute.md`). Giving each task the collection
average would put the same FLOP figure on 220 rows spanning two orders of
magnitude of real work — the one measured per-task ledger that exists, 34 of the
220 tasks under GPT-5.4, spans 27× in fresh input plus output tokens. A FLOP value
has to be an estimate for its own row's task; a collection average is an estimate
for the collection, so the collection gets the row. The 440 withdrawn task rows
and their notes are in `agent-work/removed/`. Where that ledger does give a
task its own compute, and a grade exists to go with it, the task gets a row on
its own terms; that is the 18 rows below, and it is the same rule, not an
exception to it.

## Human time

**34,164 s (9.49 h), the gold set's published mean expert completion time.**
Appendix Table 5 of the [GDPval paper](https://arxiv.org/html/2510.04374v1) gives
the full seven-number summary of the gold set's completion times: mean 9.49 h, sd
13.75, min 0.50, p25 2.38, median 5.00, p75 10.00, max 100.00. Experts
self-reported real-world time to complete at submission and occupational reviewers
independently validated and corrected those reports, so this is a source estimate
with a validation step rather than a timing measurement, and the paper flags that
self-reports may run high or low.

The paper publishes two incompatible means for this same quantity. Table 5 says
9.49 h with a mean task dollar value of $398.46; section A.2.1 says H_T = 404 min
(6.73 h) with a mean expert cost of $361. The pairs imply different mean wages,
$42.0 and $53.6 per hour, so this is two computations over the same 220 tasks
rather than a units slip, and the paper does not reconcile them. Table 5 is used
here because it is the descriptive summary of the released gold set, internally
consistent across all seven statistics, and presented as a property of the data;
the A.2.1 figure appears only inside the cost-advantage calculation, and the paper
never says how it was constructed. Taking A.2.1 instead would shorten human time
by 29%.

Per-task times are not published anywhere — not in the paper, not on Hugging Face,
not from any third party. The evidence behind that statement, and the
distributional comparison against the 220 bottom-up estimates this project made
before the rows were withdrawn, are in
`agent-work/scouting/gdpval-human-time.md`.

## GPT-5 compute

**1.4658721323206752e17 FLOPs per task.** Appendix A.2.1 and Table 2 report a mean
expert cost of $361 and a naive GPT-5 cost advantage of 474×, so the mean model
invoice is $361/474 = $0.7616 per task. This is a ratio of means, and OpenAI's
setup for it is GPT-5 high with web search and code interpreter, three completions
per prompt; it is not the later best-of-four-plus-judge scaffold.

Inverting the invoice needs an input/output split, which the paper does not give.
At [launch pricing](https://openai.com/gpt-5/) of $1.25/M input and $10/M output
and an assumed 4:1 input:output position ratio — plausible for a reasoning agent
repeatedly re-reading reference material and tool results — output is
0.7616/(10e-6 + 4×1.25e-6) = 50,773.6 positions and input 203,094.2, for 253,867.8
primary positions. A 2:1 ratio would give about 182,785 positions before the helper
allowance and 8:1 about 342,722, so the assumption moves the primary positions by −28% to +35%. Ten
search and extraction passes at 1,000 positions each add a 10,000-position helper
allowance at the primary coefficient; that is an allowance the named tools make
possible, not an observed count. Total 263,867.79 positions at 2e11 FLOPs per token
gives 5.2774e16 in the weight matrices, and the attention term at
`attention_ratio` 1.778 brings it to 1.4659e17.

The invoice does not separate fresh input, cached input, output or non-model
charges. Cache discounts increase the positions inferred from a given invoice while
cache reuse decreases the newly processed fraction, so the direction of the error
is not known. Because the FLOP figure is inverted from the dollar figure, this
row's `compute_flops` and `ai_cost_usd` are not independent.

## Opus-5 compute

**1.6148470105226074e17 FLOPs per task.** The [Artificial Analysis GDPval-AA
page](https://artificialanalysis.ai/evaluations/gdpval-aa), fetched 2026-09-12 and
retained as `agent-work/sources/gdpval/fetched/aa-gdpval.html`, carries a
server-rendered record for slug `claude-opus-5` at max effort. Its
`canonicalEvalTokenCounts.gdpval` gives collection totals: input 1,443,328,948,
answer 12,091,348, reasoning 9,300,465, cacheableInput 1,407,667,015. The record's
model-level `cacheHitRate` is 0.996663404781368, and [AA's
methodology](https://artificialanalysis.ai/methodology/intelligence-benchmarking)
states that evaluation token counts are combined with live measurements of typical
model cache hit rates rather than the rate realized in the run. So the four counts
are reported workload and the cache rate is a transferred parameter.

Treating `input` as inclusive of cacheable input, cache hits are
cacheableInput × cacheHitRate and cache creations the remainder. Cache reads carry
no weights pass, so fresh input + cache creation + answer + reasoning per task is
(1,443,328,948 − 1,407,667,015 × 0.996663 + 12,091,348 + 9,300,465)/220 =
280,684.37 positions, of which cache creation alone is 21,349.2. Normalization is
over the source's 220 tasks, not over its 60.47 mean turns. The same 10,000-position
helper allowance gives 290,684.37 positions, 5.8137e16 FLOPs in the weight matrices
and 1.6148e17 with attention.

Counting cache reads as processed positions instead would give 6,657,821.6 positions
per task, over 23× larger, which is not the matrix work a cached prefix costs;
ignoring cache-miss creation would drop 21,349 positions per task. Token categories
approximate multimodal document handling, and visual preprocessing is not separately
measured. The AA judge is not a helper delivering the task output.

## Performance

**GPT-5 high: `below`.** [Figure
5](https://arxiv.org/html/2510.04374v1/assets/gdpval_winrates.png) reports 38.8%
wins plus ties against the expert deliverables, with the strict-win segment at
roughly 35%; Table 2 separately reports 39.0% while defining its rate as rated
better, and that inconsistency is left standing. Grading was blinded pairwise
comparison by occupational experts, three model samples per prompt and three graders
per sample, with ties at half credit. Under this file's rule — half the better
side's score, judged as whether the job was done — a model preferred or tied in
about two comparisons in five is doing the job somewhat worse than the expert, which
is `below`. Neither figure is an all-criteria pass rate.

**Claude Opus 5 max: `above`, flagged `different_assessment`.** No expert grading of
Opus 5 on GDPval exists. AA's GDPval-AA v2 rates it at Elo 1735 against the expert
deliverables anchored at 1000, under anonymized pairwise comparison by an AI panel
with Bradley-Terry scoring and half-credit ties, and audio and video files judged by
a native multimodal judge. That supports `above`, but the comparison rests on a
grading protocol the human experts never ran, which is why the row carries
`different_assessment` rather than `none_identified`. The two rows' labels are
therefore not directly comparable with each other: one is expert-graded and one is
panel-graded.

## Model assumptions

GPT-5 uses the registry's 100B active estimate and 2e11 FLOPs-per-token coefficient,
based on [Epoch's GPT-5 compute
analysis](https://epochai.substack.com/p/notes-on-gpt-5-training-compute), with
release date 2025-08-07 from the [OpenAI system
card](https://openai.com/index/gpt-5-system-card/).

`claude-opus-5-max`: 100B active, 2e11 FLOPs per token. The [Anthropic
release](https://www.anthropic.com/news/claude-opus-5) establishes 2026-07-24 and a
max-effort-capable Opus 5 but discloses no parameters, and the [Epoch model
page](https://epoch.ai/models/claude-opus-5) lists them as unknown. The
contemporaneous [Kimi K3 technical report](https://arxiv.org/abs/2607.24653) reports
104B activated parameters in a 2.8T MoE frontier native-multimodal 1M-context agent;
rounding that reference class to 100B is the transfer used here. It is an
architecture-scale prior, not an inference from token price, latency or score, and
not a claim about Anthropic's architecture. A 50–200B range moves compute 0.5–2×.
Image preprocessing is folded into the overall approximation rather than given a
fabricated encoder.

Attention on both rows uses `attention_context` 108,500 and `attention_ratio` 1.778,
derived in [research/attention-correction.md](../attention-correction.md).

<a id="exp035-per-task-rows"></a>

## exp035 per-task rows

Eighteen GDPval tasks also carry a row of their own, because for those tasks a
per-task token ledger and a per-task grade both exist. They are the only GDPval
points in the file with task-specific compute, which is what a row requires. They
do not replace the two collection rows and are not a second reading of them: the
collection rows are GPT-5 high and Claude Opus 5 max over all 220 tasks, and these
are GPT-5.4 over 18. Twenty-two tasks were graded; four of the twenty-two produced
a deliverable that does not do the job and are withheld, which
[the critical-item decisions](#critical-item-decisions) sets out.

### Where the numbers come from

HyeonSang Jeon ran the whole 220-task gold set through Codex against a GPT-5.4
deployment on Azure AI Foundry on 2026-09-12, published the run as
[`HyeonSang/exp035_codex_foundry_full220`](https://huggingface.co/datasets/HyeonSang/exp035_codex_foundry_full220),
and graded its deliverables himself against the rubrics OpenAI open-sourced into
`openai/gdpval` on 2026-02-10. Cost instrumentation was live only for the last 34
tasks in run order, so `cost_ledger.jsonl` carries 85 records over 34 distinct
`task_id`s. Of those 34, 22 produced a deliverable and were graded; 12 errored with
`TaskExecutionError` and are withheld, as are four of the 22 whose deliverable
does not do the job (both below). The survey of the run, its integrity
checks, and the join of tokens to grades are in
`agent-work/scouting/gdpval-grader-submission.md` and its
`exp035_34tasks_tokens_and_scores.csv`. The 2.6 GB download sits in
`agent-work/sources/gdpval/hyeonsang/exp035/`.

This is the only run anywhere with both measured per-task compute and measured
per-task performance on GDPval. No other HyeonSang repo has a ledger and a grade
file together, OpenAI publishes a collection mean, and Artificial Analysis
publishes collection totals.

### How the ledger is read

A ledger record is one Codex turn. Every settled record carries
`missing_reasons: ["call_reachability_unknown"]` and the note "one Codex turn; the
model requests inside it are not individually reported", so the ledger is a lower
bound at turn granularity rather than an audit of API calls. Each row's
`compute_evidence` is `derived_assumed_inputs` and its notes say the count is a
lower bound.

Three ledger states matter. **Settled** records carry token counts and are summed.
**Reserved** records — 13 across the 34 tasks — have null in all four token fields;
they are attempts opened and never concluded, and the rows that have one take
`compute_subset = positive_tokens` rather than `all`. **Infrastructure retries**,
`retry_kind: infrastructure` on 51 of the 85 records, are re-attempts of the same
turn against the provider, and their tokens are real spend, so they stay in the
total. A task's compute is therefore the whole goal run including its retries,
which is why `compute_statistic` is `total` and `ai_attempts` is 1.

**Cache treatment follows the attention recipe.** `input_tokens` is gross and
contains `cached_input_tokens`; `total_billed_tokens` is `input_tokens +
output_tokens`; `reasoning_tokens` sit inside `output_tokens`. A cache read is a
key, not a query: it raises the context later positions attend over and takes no
pass through the weight matrices. So the counted positions are fresh input plus
output, `tokens_accounting` is `input_cache_creation_output`, and the cached
positions enter only through `attention_context`. Counting cache reads as processed
positions instead would multiply the block's counted positions by 8.3 and misprice a
cached prefix as a full forward pass.

**Attention context comes from the ledger's own turn structure.** All of a task's
distinct positions are either fresh input or output, because a cached position is a
repeat of one of those; the dialog inside one turn is append-only and each new
position attends over the prefix before it, so the length-weighted mean prefix is
half the turn's trajectory. With `k` settled records the trajectory is cut into `k`
separate attempts, giving

```
attention_context = (fresh input + output) / (2 · k)
```

That is the recipe's per-row precedence, set from the run's own records rather than
from the collection fallback, and it is the reason these rows carry contexts of
3,913 to 42,330 rather than the 108,500 the two collection rows take from
Artificial Analysis's turn count. `attention_ratio` is
`2 · 80 · 10240 · attention_context / 1e11` on the registry's GPT-5.4 shape, and
runs 0.064 to 0.694. No row is near the recipe's 200,000 cap.
`compute_flops = 2e11 · (fresh input + output) · (1 + attention_ratio)`.

**Dollars.** `model_cost_usd` is null on every exp035 record, so the figure is list
price on the run date, 2026-09-12, applied to the ledger's own three counters:
fresh input at $2.50/M, cached input at $0.25/M and output at $15.00/M. Reasoning
tokens are inside the output counter and bill at the output rate, and gpt-5.4
carries no cache-write surcharge — that starts at GPT-5.6
(`research/cost/openai-cache-write.md`). Microsoft publishes the same three rates
for GPT-5.4 in Azure AI Foundry as OpenAI does on its own sheet, so the provider
mismatch between the run and `research/cost/list-prices.csv` costs nothing here.
The 18 rows total $4.88, and the four withheld rows another $4.24. Two qualifications: Azure's >272K-input tier doubles input
and cached rates and raises output by half, and the ledger reports no per-call
prompt length, so a turn that crossed the boundary is underpriced; and the ledger's
own incompleteness applies to the dollar as much as to the FLOP.

### Performance is a rubric fraction, not a win rate

The grades come from `step8_grade.py` in `hyeonsangjeon/gdpval-realworks`: judge
`gpt-5.6-sol` at reasoning effort max, temperature 0, seed 42, against the
`openai/gdpval` rubrics pinned at commit `11e7900`, with a vision model for visual
rubric items and `gpt-audio-1.5` for audio ones. Run status `final`, graded
2026-09-12. Each task's score is the fraction of its own rubric's points awarded.

**This is not GDPval's headline metric.** GDPval's win rate is a blinded pairwise
preference of an occupational expert between the model's deliverable and the
expert's own. A rubric fraction is a different instrument on a different scale, and
84.8% of rubric points does not mean an 84.8% win rate.

**There is no published human anchor for it.** Neither the
[GDPval paper](https://arxiv.org/html/2510.04374v1), the
[Hugging Face dataset card](https://huggingface.co/datasets/openai/gdpval) that
ships `rubric_pretty` and `rubric_json`, nor
[OpenAI's GDPval page](https://openai.com/index/gdpval/) reports what fraction of
rubric points the gold expert deliverables themselves earn under a judge. The
paper's automated grader is pairwise, and it predates the rubric release. So there
is no anchor to place bands around, and no basis for calling a 96% row better than
the expert and a 55% row worse.

Damon's ruling of 2026-09-14 is that these grades count as comparable to the human.
The rows therefore take `comparison_issues = different_assessment`, and each row's
`performance_evidence` states the awarded and available rubric points, the judge
configuration, and that no rubric score for the expert's deliverable exists. The
label is set by whether the deliverable does the job, which the next section works
through task by task.

<a id="critical-item-decisions"></a>

### The critical-item decisions

**Nothing in the rubric is flagged critical by its author.** `critical_fail` in the
grade file is the harness's own convention, and its source says so: `required` is
`null` on all 10,453 rubric items across the 220 tasks, so
`batch-runner/core/grader.py` treats an item as critical when `abs(max_score) >= 4`
and sets `critical_fail` when any such item's `model_did_right` is false. So the
flag means "missed an item worth four points or more", not "missed something the
rubric's author called essential".

Twelve of the 22 carry the flag, at scores from 54.7% to 98.6%. Reading the graded
items behind each one separates three kinds of case, and Damon's rule — a row's
label says whether the AI did the job, and a defective value is re-estimated rather
than annotated — assigns each to a label.

| Task | Occupation | Rubric (%) | What the high-weight miss was | Decision |
|---|---|---:|---|---|
| `ee09d943` | Accountants and Auditors | 54.73 | Formatting 2.75/5, and underneath it the trial balance's net profit, total assets and total liabilities plus equity are all wrong, `#REF!` errors are visible, and eight schedules report the wrong balance | withheld |
| `ff85ee58` | Audio and Video Technicians | 61.48 | The −10 timing penalty fired: the sax "consistently start[s] about half a beat early" against the bed. Entrance timing failed outright and no spatial effect was applied. Five further audio items returned `judge_error` | withheld |
| `e6429658` | Nurse Practitioners | 67.05 | Formatting 4.0/5, but only one of the two required deliverables exists — the appeal letter, no patient-assistance application PDF — so every Application item fails, and the judge found invented patient identifiers | withheld |
| `e4f664ea` | Producers and Directors | 67.27 | The 20-point "plot follows the narrative treatment" and 16-point "characters do not contradict the story breakdown" both fail outright | withheld |
| `ec591973` | First-Line Supervisors of Non-Retail Sales Workers | 72.08 | Formatting 1.75/5 — subtitle over title, text spilling out of cards, clipped footer — plus 2,901 characters against a 110-word limit and no phased horizon, pilot scope or success threshold | below |
| `d025a41c` | Customer Service Representatives | 75.46 | Formatting 3.375/5; four required problematic statements unidentified, case content misattributed, one quotation absent from the reference file, and a Python script shipped rather than the single Word file | below |
| `ed2bc14c` | Property, Real Estate, and Community Association Managers | 85.80 | Formatting 4.08/5. The memo, three renewal drafts and event plan are all present; the substantive miss is an 8-of-20 rather than 9-of-20 tally on a departure reason the memo still identifies correctly | match |
| `fd6129bd` | Project Management Specialists | 88.93 | Formatting 3.67/5; every other shortfall is a partial on completeness detail such as a decision-rationale field | match |
| `f841ddcf` | Order Clerks | 89.49 | Formatting 3.25/5 for a clipped summary paragraph; the rest are AutoFilter formalities and an unrounded $5,210.60 against the rubric's $5,211 | match |
| `d7cfae6f` | Sales Representatives, Wholesale and Manufacturing, Except Technical and Scientific | 89.67 | Inventory coverage computed as supply minus expected over expected rather than supply over expected: Makeup reads −18% against 82%, Fragrance 502% against 602% | below |
| `e996036e` | First-Line Supervisors of Non-Retail Sales Workers | 89.74 | Formatting 1.75/5 with lines cut mid-word; Year-1 shipments total $255,000 against $225,000, and Net 30 and Net 60 receipts are both modelled a quarter early | below |
| `f9a1c16c` | Audio and Video Technicians | 98.61 | Formatting 3.9/5: one input label crosses a box border and some centre-stage labels overlap. The only unmet item in the task | match |

Four deliverables do not do the job and are withheld to
`agent-work/removed/excluded.csv`: a financial package whose trial balance does not
tie, a mix whose overdub is out of time, a two-part deliverable missing its second
part, and a screenplay that departs from the treatment it was asked to adapt.

Four do the job and are materially flawed, and take `below`: a broken-looking
strategy slide that still carries the strategy, a feedback document that misses
four of its required findings, a sales report whose headline coverage metric is
computed on the wrong definition, and a scenario model whose Year-1 total and cash
timing are both wrong.

Four keep `match`: in each, the only high-weight miss is a partial on the generic
"Overall formatting and style of the deliverable" item and the substance is
delivered. A partial on a presentation-polish criterion is a formality, not a
failure to do the job.

The ten rows the flag never touched keep `match` and their
`performance_evidence` now says what the flag means rather than calling the item
critical.

### What the block shows

Scores on the 22 graded tasks run 54.7% to 98.6% of rubric points, mean 84.8 and
median 89.6. On the 18 that became rows they run 72.1% to 98.6%, mean 89.7 and
median 90.3, because the four withheld deliverables are four of the five lowest.

**Compute spans 70× and says nothing about quality.** Billed tokens across the 34
ledger tasks run 37,776 to 2,655,572; counted positions on the 22 graded tasks run
7,825 to 210,644, a factor of 27. The Spearman rank correlation between billed
tokens and rubric percentage on the 22 is **−0.161**, and between counted positions
and rubric percentage −0.239. The cheapest of the 22 scored 91.2% and the dearest,
at 2.66M billed tokens over four attempts, scored 54.7% and is one of the four now
withheld. Spend tracks task difficulty and retry churn, not output quality.

**The per-task rows sit an order of magnitude below the collection row.** Their
compute runs 1.665e15 to 2.951e16 FLOPs against human times of 3,600 to 36,000 s,
giving 2.4e11 to 4.0e12 FLOPs per human-second with a median of 6.3e11. The GPT-5
collection row is at 4.3e12. The two are not the same measurement — the collection
figure is inverted from a dollar invoice for a three-completion best-of scaffold,
these are a lower-bound token ledger for one Codex run — and the gap is a
reasonable size for that difference.

| point_id | Occupation | Human time (s) | Turns | Fresh input (tokens) | Cached input (tokens) | Output (tokens) | Counted positions (tokens) | attention_context (tokens) | attention_ratio | compute_flops (FLOPs) | Rubric (%) | Cost (USD) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `work-gdpval-feb5eefc-gpt54` | Personal Financial Advisors | 36000 | 4 | 97991 | 445696 | 20720 | 118711 | 14838.9 | 0.2431 | 2.951e+16 | 96.2 | 0.6672 |
| `work-gdpval-d3d255b2-gpt54` | Real Estate Sales Agents | 7200 | 1 | 76635 | 461568 | 8025 | 84660 | 42330 | 0.6935 | 2.867e+16 | 98.19 | 0.42735 |
| `work-gdpval-f3351922-gpt54` | Customer Service Representatives | 10800 | 2 | 60366 | 59136 | 7240 | 67606 | 16901.5 | 0.2769 | 1.727e+16 | 79.18 | 0.2743 |
| `work-gdpval-f9a1c16c-gpt54` | Audio and Video Technicians | 7200 | 1 | 38102 | 467328 | 18276 | 56378 | 28189 | 0.4618 | 1.648e+16 | 98.61 | 0.48623 |
| `work-gdpval-f9f82549-gpt54` | Private Detectives and Investigators | 14400 | 1 | 29131 | 258048 | 11361 | 40492 | 20246 | 0.3317 | 1.078e+16 | 83.94 | 0.30775 |
| `work-gdpval-efca245f-gpt54` | First-Line Supervisors of Production and Operating Workers | 36000 | 1 | 16857 | 243584 | 19737 | 36594 | 18297 | 0.2998 | 9.513e+15 | 90.92 | 0.39909 |
| `work-gdpval-ffed32d8-gpt54` | Pharmacists | 10800 | 1 | 22914 | 234624 | 8919 | 31833 | 15916.5 | 0.2608 | 8.027e+15 | 95.92 | 0.24973 |
| `work-gdpval-fe0d3941-gpt54` | Sales Representatives, Wholesale and Manufacturing, Technical and Scientific Products | 14400 | 1 | 18390 | 146176 | 13057 | 31447 | 15723.5 | 0.2576 | 7.910e+15 | 95.83 | 0.27837 |
| `work-gdpval-d7cfae6f-gpt54` | Sales Representatives, Wholesale and Manufacturing, Except Technical and Scientific Products | 18000 | 1 | 13594 | 292224 | 12954 | 26548 | 13274 | 0.2175 | 6.464e+15 | 89.67 | 0.30135 |
| `work-gdpval-f841ddcf-gpt54` | Order Clerks | 7200 | 1 | 14052 | 345728 | 8994 | 23046 | 11523 | 0.1888 | 5.479e+15 | 89.49 | 0.25647 |
| `work-gdpval-d025a41c-gpt54` | Customer Service Representatives | 7200 | 1 | 15297 | 160256 | 7048 | 22345 | 11172.5 | 0.1831 | 5.287e+15 | 75.46 | 0.18403 |
| `work-gdpval-ec591973-gpt54` | First-Line Supervisors of Non-Retail Sales Workers | 7200 | 1 | 16327 | 87168 | 5467 | 21794 | 10897 | 0.1785 | 5.137e+15 | 72.08 | 0.14461 |
| `work-gdpval-fd3ad420-gpt54` | Real Estate Brokers | 14400 | 1 | 15343 | 86656 | 5807 | 21150 | 10575 | 0.1733 | 4.963e+15 | 94.65 | 0.14713 |
| `work-gdpval-fd6129bd-gpt54` | Project Management Specialists | 16200 | 1 | 7315 | 186624 | 9941 | 17256 | 8628 | 0.1414 | 3.939e+15 | 88.93 | 0.21406 |
| `work-gdpval-e996036e-gpt54` | First-Line Supervisors of Non-Retail Sales Workers | 14400 | 1 | 4626 | 136064 | 12052 | 16678 | 8339 | 0.1366 | 3.791e+15 | 89.74 | 0.22636 |
| `work-gdpval-ed2bc14c-gpt54` | Property, Real Estate, and Community Association Managers | 10800 | 1 | 8666 | 104320 | 6413 | 15079 | 7539.5 | 0.1235 | 3.388e+15 | 85.8 | 0.14394 |
| `work-gdpval-dfb4e0cd-gpt54` | Compliance Officers | 10800 | 1 | 7778 | 144000 | 4603 | 12381 | 6190.5 | 0.1014 | 2.727e+15 | 98.6 | 0.12449 |
| `work-gdpval-d4525420-gpt54` | First-Line Supervisors of Retail Sales Workers | 3600 | 1 | 6521 | 53632 | 1304 | 7825 | 3912.5 | 0.0641 | 1.665e+15 | 91.18 | 0.04927 |

### What is withheld and what is shaky

**The 12 errored tasks are withheld.** They burned 1,964,593 billed tokens against
zero output, the judge returned `no_deliverables` and 0 rubric points, and a row
substantially below the human baseline takes no label in this file. Their full rows,
with the same compute recipe applied, are in `agent-work/removed/excluded.csv`, and
the per-task figures are tabulated in
`agent-work/removed/gdpval/exp035-errored-tasks.md`.

**Four graded tasks are withheld too.** Their deliverables do not do the job, for
the reasons in [the critical-item decisions](#critical-item-decisions), and their
rows are in the same `excluded.csv` with the reasoning in each row's
`exclusion_reason`. Their compute is real and is recorded there.

**The 34 are a tail block, not a draw.** They are positions 186–219 of the 220 in
run order; `cost_summary` records `not_run_tasks: 186` and `partial_tasks: 34`. Run
order is by `task_id`, a random UUID, so the block is quasi-random with respect to
task content, and its completion rate, 22 of 34, matches the run as a whole, 150 of
220. Treat it as a sample of convenience.

**Human time is our own estimate, not a measurement.** Each row's `human_time` is
the bottom-up per-task estimate this project built from the inspected prompt and
reference files before the 440 task rows were withdrawn, carried over unchanged, so
`human_time_evidence` is `llm_estimate_judgment` and `human_time_statistic` is
`point_estimate`. OpenAI publishes the gold set's time distribution and no per-task
values, so there is nothing to check these against task by task. The 18 estimates
run 3,600 to 36,000 s with a median of 10,800; the gold set's published mean is
34,164. The reasoning behind each one is reproduced below.

**Other limits.** The 18 are one attempt each under one scaffold, and Codex's own
orchestration tokens are inside the ledger's counters only to the extent the turn
records reach them. The token counts carry no separate image or audio accounting,
so multimodal reference handling is folded into the text positions. Model size is
the registry's 100B active estimate for the GPT-5 family, and a 40–250B range moves
every row's compute by 0.4–2.5×.

## Per-task human time, exp035 rows

These are the estimates and the reasoning behind them, carried over from the
withdrawn per-task material in `agent-work/removed/gdpval/`. Each estimates active
professional effort on the task at expert skill, using ordinary office and research
tools without AI assistance. They were built from the prompt and reference files,
not from any timing observation, and the reference deliverables were used to
establish scope rather than treated as correct.

### The range on each of them

Added 2026-09-17. No single estimate below has an alternative of its own, but the
set does, and the bounds come from it. The 220 bottom-up estimates this project
built cover exactly the 220 gold tasks OpenAI published a time distribution for, so
the two are two descriptions of the same 220 numbers. Fitting a lognormal to each
interquartile range gives a log spread of **0.727** for the estimates against
**1.064** for Table 5, and the medians agree exactly at 5.00 h; the estimates are a
rank-preserving, compressed image of the published distribution, which is the
signature of judgment estimates regressing toward a central case. The derivation and
the distribution-to-distribution comparison are in
`agent-work/scouting/gdpval-human-time.md`.

Two numbers follow from those two spreads.

**Where the published distribution puts a task our budget calls h hours.** The
rank-preserving power map anchored on the common median,
`Q(h) = clip(5*(h/5)^1.464, 0.5, 100)` with the exponent 1.464 = 1.064/0.727,
reproduces every one of Table 5's seven statistics to within 7%. It is the source's
own answer for a task at our estimate's rank.

**How far the answer can sit from it.** Under the shrinkage geometry that produces
the compression, the residual spread of the published value around `Q(h)` is
`sqrt(1.064^2 - 0.727^2) = 0.777` in log, so one residual standard deviation is a
factor of `exp(0.777) = 2.175` either way.

Each row's bounds are `Q(h)/2.175` and `Q(h)*2.175`, in hours, converted to seconds.
The bounds are not a factor on the central, because `Q` is nonlinear: the low runs
0.23x the central on the shortest task and 0.63x on the longest. The central stays
where the bottom-up budget put it, and it sits inside the band on all seventeen.

Whether the central should move to `Q(h)` is open and is Damon's to rule. It is the
same question the collection rows already answered one way — they take Table 5's
34,164 s over section A.2.1's 404 min — and answering it the same way here would
move all seventeen and would put the evidence label in question, because the value
would then be our ranking scaled onto the source's own published distribution rather
than a judgment. The scouting note's recommendation to resolve the calibration target
before touching a central stands.

<a id="work-gdpval-d3d255b2-gpt54"></a>

### Advise a seller on a cash purchase offer

Task `d3d255b2-f5f2-4841-9f62-2083ec9ef3da`; Real Estate Sales Agents.

Provided three comps sold $505000, $510000, $495000; mean=$503333.33 and mean DOM 30. The source says list is 3.4% above comps, but(525000/503333.33−1)=4.3046%. The $500000 offer is 0.6623% below that mean and 4.7619% below list. Source price-per-area comparisons are rough and property dimensions are assumed, so do not claim a formal appraisal. As-is condition/no other contingencies/30 day close reduce execution friction, but cash does not establish guaranteed closing.

Human target uses the supplied market analysis and corrects its arithmetic; it does not collect new MLS comps or pretend an exact appraisal. A modest counter around $505000–510000 with seller-approved flexibility is supportable; the exact counter is professional judgment. No human output provided.

Human estimate 2 h: 30 min review/recalculate comps and terms, 30 min choose strategy/tradeoffs, 45 min client narrative and 15 min PDF check. No negotiation calls or transaction execution.

<a id="work-gdpval-d7cfae6f-gpt54"></a>

### Assess cosmetics-set inventory against seasonal sales

Task `d7cfae6f-4a82-4289-955e-c799dfe1e0f4`; Sales Representatives, Wholesale and Manufacturing, Except Technical and Scientific Products.

Nineteen brands span skincare, makeup and fragrance. The source has a sales tab, OH+OO tab and separate October/Q1 shipment tabs; joins need case/label normalization and should exclude repeated axis/grand totals. Negative sales such as returns are not discarded. Source blanks are treated as zero only for reproducing reported additive totals; a blank or negative prior-year denominator must not produce an unqualified ordinary growth percentage.

The decision date and shipment headings identify Q1 2024 as the intended future horizon, despite repeated Q1 2023 wording. The requested seasonal proxy is full Q3 2022 through Q1 2023, not an invented daily forecast for the remaining September days. Native sums: current YTD 10734.7, prior YTD 7760.7, historical three-quarter proxy 10734.5, OH+OO 7978.6, October shipments 2365, Q1 shipments 2121.6. Under the specified additive treatment of expected shipments, coverage exceeds proxy sales by 1730.7, or 16.1228%. This assumes future shipment lines are incremental to the OH+OO snapshot; the data cannot independently prove absence of order overlap. Use provided shipment-dollar summaries rather than multiplying inconsistent auxiliary product columns. The isolated #REF! cell does not remove the intact Q1 brand figures.

Five active hours estimates one auditing labels, totals and period logic, one and a half implementing brand joins and calculations, one creating axis/grand totals and requested layout, and one and a half reconciling arithmetic, exceptional percentages and the shipment assumption. Comments remain blank as explicitly requested.

<a id="work-gdpval-feb5eefc-gpt54"></a>

### Compare GRAT and CRAT options for a business-sale client

Task `feb5eefc-39f1-4451-9ef9-bffe011b71dd`; Personal Financial Advisors.

No client asset schedule, prior gifts, cash-flow needs, spouse age or funding month is supplied. This is a researched planning comparison with explicit scenarios, not execution of either trust. A simple $16m minus $10.86m exemption benchmark gives $5.14m exposed and $2.056m tax at 40%, but is not a personalized estate-tax assessment: availability of both exemptions, other assets and elections matter. The cash sale has already occurred, so a later charitable trust cannot retroactively avoid the sale's capital-gains event.

Original IRS explanations distinguish a GRAT's retained annuity and potential remainder for children from a CRAT's charitable remainder. The 2003 model guidance predates the 2015 task and specifies payout limits, at least 10% actuarial remainder and the exhaustion test: https://www.irs.gov/irb/2003-31_IRB . Do not import the 2016 sample early-termination relief into a 2015 analysis. The IRS historical 7520 table gives January 2015 2.2%, with rates varying across the year: https://www.irs.gov/businesses/small-businesses-self-employed/section-7520-interest-rates-for-prior-years . A January example must therefore be labeled illustrative rather than the client's known funding month.

As a numerical scope check, a $5m two-year level-annuity GRAT at 2.2% has approximately $2.583m annual retained payments; a stipulated 6% asset return leaves roughly $297k at term, whereas 2.2% leaves approximately zero. That is growth-dependent transfer, not removal of the whole $5m from the estate. A $5m twenty-year CRAT paying 5% annually has an approximately 19.8% discounted charitable remainder at 2.2% before applicable adjustments. The fixed term is a transparent illustration; a lifetime version at age 62 requires mortality/exhaustion testing and spouse information if joint. A CRAT's terminal assets benefit charity rather than the children, so it should not be recommended solely as an equivalent inheritance vehicle. These examples establish calculation complexity, not a recommendation to establish a trust.

Estimate: 10 hours = 2.5 historical tax/mechanics research + 2 scenario calculations/sensitivities + 3 clear comparative writing + 1.5 layout/figures + 1 numerical and objective-fit review. Drafting legal instruments, tax returns and implementing investments are excluded.

<a id="work-gdpval-ffed32d8-gpt54"></a>

### Compare ninety- and hundred-day pharmacy refill economics

Task `ffed32d8-d192-4e3f-8cd4-eda5a730aec3`; Pharmacists.

Both original price/reimbursement PDFs were read. Reimbursements are already for 300 patients per fill; multiplying them by 300 again is wrong. Drug cost uses the per-1,000-tablet price, days per fill, fills and 300 enrollments. Vial costs are $0.008/$0.12/$0.26/$0.73 for the specified sizes, including the unusually low eight-dram price as supplied rather than silently changing it.

The independent audit computes total net receipts after the two stated expenses: $72,766.88 for 90 days, $52,993.95 for 100 days, a difference of $19,772.93 (2.4716% of $800k). This exceeds $16k under the task's decision rule. The reference's $73,486/$53,009.40/$20,477.45 figures do not reconcile: for example, amlodipine 5mg's 90-day net is $7,084.80, not $7,384.80, and amlodipine 10mg reimbursement differs from its source. Decimal arithmetic from the native PDFs is retained in the portable audit.

The task calls reimbursement minus drug/vial expenses 'annual revenue'; identify that convention rather than confuse it with gross sales or full net profit after all operating costs. Three 100-day fills cover only 300 days (82.2% of 365), compared with 360 (98.6%); fill coverage is not measured adherence. The report can state the requested financial outcome while explaining the unequal-coverage assumption. Three hundred enrollments per medicine do not establish 3,000 distinct people, and no real patients or clinical outcomes are inferred.

Estimate: 3 hours = 0.5 source transcription/unit checks + 0.75 ten-drug calculations + 0.75 concise comparative table/summary + 1 arithmetic and coverage/threshold verification.

<a id="work-gdpval-e996036e-gpt54"></a>

### Compare three retail-account terms proposals

Task `e996036e-8287-4e7f-8d0a-90a57cb53c45`; First-Line Supervisors of Non-Retail Sales Workers.

The input has four sales values totaling $200,000 and four shipment values ($70k/$80k/$80k/$25k) totaling $255,000, conflicting with the prompt's $225,000. The reference simply uses the quarterly figures. A full answer should preserve the source schedule as one case and show the stated $225k annual case by explicit proportional scaling (15/17), rather than hide the disagreement. Three commercial structures can then be compared on either consistent volume basis.

Wholesale revenue is shipment MSRP value times (1-retailer margin); marketing allowance is up to 4% of shipment retail value, not wholesale revenue. No cost of goods, financing rate or bad-debt probability is given, so net wholesale receipts are not a quantified profit estimate. The reference has payment-term labels but no receipt-date schedule. A substantive answer needs a stated shipment/invoice timing convention (for example equal monthly shipments within each quarter) to display Net 30/60 cash timing and quarter-end allowance payments. These are assumptions, not native invoice dates. A visual can compare net receipts with payment flexibility and retailer activation benefits without pretending those qualitative benefits are measured ROI.

Estimate: 4 hours = 0.5 reconcile inputs + 1.5 formulas and receipt timing + 0.75 visual and structure choices + 0.5 recommendation + 0.75 checks. No actual negotiation or twenty-store rollout is included.

<a id="work-gdpval-f9f82549-gpt54"></a>

### Create employee-theft investigation guidance and case briefing

Task `f9f82549-fdde-4462-aff8-e70fba5b8c66`; Private Detectives and Investigators.

The prompt requests a flowchart plus incident details, but calls the companion both a PowerPoint and a PDF. A reasonable full deliverable is one editable deck with a section/slide per flowchart heading, plus its PDF export, not one unrelated investigation per heading. The source flowchart is image-only and was rendered and read. Its inconclusive-evidence branch points to suspension and recovery, which is not a sound general inference to copy automatically. The companion reference also invents specific five-to-seven-day delays, the management escalation path, photographs and police involvement not supplied in the prompt.

The estimate covers constructing an anonymized workflow and accurately mapping the stated event—temporary diversion of deposits for gambling followed by later deposit—onto it. Where the actual incident record supplies no step outcome, identify the procedure to follow rather than fabricate evidence or an interview. General documentation, evidence preservation, internal review and HR/legal escalation can be described without pretending a corporate disciplinary policy or jurisdiction-specific rule is supplied. This is an awareness/training artifact, not conducting a live investigation or making an employment decision.

Estimate: 4 hours = 1 workflow and fact/procedure separation + 1 flowchart construction + 1.5 companion briefing + 0.5 anonymization, consistency and exports.

<a id="work-gdpval-fe0d3941-gpt54"></a>

### Design workflows and a survey for hypothetical blood sensing

Task `fe0d3941-e32c-4bf1-a643-b566d2b4cb3c`; Sales Representatives, Wholesale and Manufacturing, Technical and Scientific Products.

The supplied workflow has nine current steps and four proposed steps. The schematic was visually inspected: a hypothetical watch shines a labeled wavelength toward skin and vessels; no validation, sensitivity, specificity or analyte calibration is provided. The requested product is a title/workflow/legend/benefits deck (roughly three to four slides) plus two survey pages. 'Over a hundred people' is an intended eventual audience, not a requirement to recruit respondents or collect their answers.

The reference survey contains six physician and four consumer questions. Its reliability question presupposes dependable results despite no evidence; a better yes/no instrument asks about acceptance conditional on demonstrated accuracy or the need for validation. Benefits should remain conditional on the technology working. Yes/no willingness-to-pay can test a clearly hypothetical price premium, but cannot estimate an actual market price or clinical performance from nonexistent responses. The time estimate includes survey wording and conditional claims, not engineering development or a systematic clinical feasibility review.

Estimate: 4 hours = 0.75 understand source steps and limitations + 1.25 workflow/legend/benefits design + 1 survey questions and separate-page PDF + 1 consistency, readability and export checks.

<a id="work-gdpval-ed2bc14c-gpt54"></a>

### Develop a tenant-retention memo from exit surveys

Task `ed2bc14c-99ac-4a2a-8467-482a1a5d67f3`; Property, Real Estate, and Community Association Managers.

All twenty native comments were read; the workbook has no header row. A five-way single-category coding gives rent/value 9 (45%), community 5 (25%), maintenance 3 (15%), job relocation 2 (10%) and homeownership 1 (5%). Comment 6 mentions a pool elsewhere but explicitly compares value at the new rent; coding it as rent/value is a documented judgment. The two leading categories are robust to moving that one comment. The current letter is sent sixty days before expiry and requires thirty-day notice to vacate; the reference memo's claim of a sixty-day notice deadline is not supported.

The goal 'increase retention by 10%' lacks a baseline and relative-versus-percentage-point convention. A professional proposal should define the metric and request the current baseline, not pretend a forecasted improvement has been demonstrated. Tiered offers can specify approval-dependent incentives without inventing affordable rent levels or legal lease changes. Two low-cost events use existing amenities; their proposed budget is a planning assumption rather than an observed vendor quote.

Estimate: 3 hours = 0.5 code/check comments + 1 offers and communication sequence + 0.75 concise drafting + 0.75 fit to two pages and check numbers/lease assumptions. Running events or waiting six months is not included.

<a id="work-gdpval-f9a1c16c-gpt54"></a>

### Draw a touring-band stage plot

Original task `f9a1c16c-53fd-4c8f-88cc-5c325ec2f0bb`; occupation: Audio and Video Technicians. Full prompt, rubric and URLs: `agent-work/sources/gdpval/fetched/f9a1c16c-53fd-4c8f-88cc-5c325ec2f0bb.json`. Inputs and reference outputs: `agent-work/sources/gdpval/fetched/f9a1c16c-53fd-4c8f-88cc-5c325ec2f0bb/`; text/worksheet/code extraction: `agent-work/sources/gdpval/fetched/tranche7-extracts.txt`.

Inspected the actual single-page reference visually: simple reusable icons, six input labels and seven outputs; some labels are truncated and the drummer is placed upstage despite prompt downstage wording. Target follows the prompt and readable layout rather than copying those defects. Four mics plus two DI inputs; five wedge outputs plus two IEM sends. Stage-right is performer-relative and wedge numbering/cross-referenced sends require checking. Estimate15min inventory,15min signal routing,60min icon/layout construction,30min orientation/send/label checks=2h;1–3h sensitivity. Static visual work permits Opus collection transfer despite the separate lack of audio-production evidence.

Selected human time: 7200seconds. This is a visual signal-routing document, not audio mixing, installing equipment or performing a show.

<a id="work-gdpval-f3351922-gpt54"></a>

### Explain TSP funds and military-to-civilian transition benefits

Task `f3351922-dbdd-45da-85c5-e7110696bbe5`; Customer Service Representatives.

The prompt provides no age, balances, military retirement system, tax-exempt balance or civilian appointment details. The work is a comprehensive explanatory email, not a personalized allocation or retirement calculation. It should distinguish G/F/C/S/I exposures and risk from lifecycle allocation funds; a dated I-Fund description matters because the benchmark changed, so old EAFE-only explanations should not be copied. The original November 2024 board minutes confirm the completed transition: https://www.frtib.gov/meeting_minutes/2024/2024Nov.pdf .

Original rule 5 CFR 1600.33, retained at https://www.law.cornell.edu/cfr/text/5/1600.33, conditions account combination on separation being reported and excludes tax-exempt contributions from transfer to a civilian account. OPM's FERS explanation, https://www.opm.gov/retirement-center/benefits-officers-center/fers-election-options/ , distinguishes automatic 1% and matching contributions, together reaching 5% when the employee contributes 5%. That benefit must be conditional on the applicable civilian retirement coverage, not represented as a blanket consequence of past military service. Current general guidance should be checked against the email's date; no numeric annual contribution limit is necessary to answer the task.

Estimate: 3 hours = 1.25 official fund/transition-rule research + 1 draft a clear organized email + 0.75 verify conditions, links and avoid unsupported personalized advice.

<a id="work-gdpval-d025a41c-gpt54"></a>

### Give feedback on three bank-support chats

Task `d025a41c-c439-4ee1-bc79-dd5c94b27a2d`; Customer Service Representatives.

All three original chats were read: gas-station authorization hold, stolen-card dispute and first direct deposit. Problems include an ambiguous merchant question, repeating text without explanation, abrupt refusal, mistaking frustration with thieves for abuse of staff, gender assumption, typos and disproportionate reassurance. The target preserves bank procedures while improving communication. Original reference sometimes changes quotations (for example, different wording/emoji) and drops the first-deposit exception; quoted statements should match originals and alternatives must retain up-to-five-day first-deposit detail.

The named guide https://www.tidio.com/blog/best-practices-for-live-chat-etiquette/ supports listening, clear questions and tone matching; it does not say every friendly greeting is unprofessional. Approximately 16 specific comment/rewrite items is a sensible scope, as illustrated by the reference, with three bold headings and 1.5 spacing.

Human estimate 2 h: 20 min read chats/guide, 60 min select/write precise feedback and alternatives, 25 min edit for policy fidelity/tone and 15 min Word layout. Not a live customer-service interaction or banking-policy review.

<a id="work-gdpval-efca245f-gpt54"></a>

### Model three running-board production recovery plans

Task `efca245f-c24f-4f75-a9d5-59201330ab7a`; First-Line Supervisors of Production and Operating Workers.

The input contains regular, supplemental and expected POs. Recomputed unshipped quantities including May are Crew 5,520 and Extended 4,035, total 9,555; through April they total 8,080. The displayed Open total formulas stop at row 12 and omit May, despite the task requiring May readiness. The February supplemental 900 of each product is due on the 15th and cannot be overlooked. Priority is Crew December–February, Extended November–February, then Crew March/April before Extended March/April.

The holiday calendar uses January 22 restart, February 5 capacity upgrade, February 19 Louis Riel Day and March 30 Good Friday. The contemporaneous Manitoba code is retained at https://web2.gov.mb.ca/laws/statutes/archive/e110(2018-06-03)e.php . Easter Monday is not automatically a general holiday for this private facility. Notice on January 2 permits a February 5–March 2 four-calendar-week extended period, containing nineteen working days. Staggered individual shifts and backfill, not paid overtime, allow the cell's ten hours. The reference uses 170 output on twenty-three days through March 9, exceeding the allowed four weeks.

Guard throughput is not supplied. Using one full cell-day each week for its 100 units, moving that work after February 1 in scenarios 2/3, and assuming negligible changeovers with unused day fractions reusable, the portable audit gives running-board capacity by April 13 / April 30: scenario 1 6,090/7,305; scenario 2 7,440/8,925; scenario 3 8,105/9,590. These are transparent capacity checks, not a completed daily allocation schedule. Scenario 3 has only 25/35 units of headroom, so rounding whole days per product or adding unstated shutdowns can change feasibility. The task merits a full calendar and cumulative-order audit, not a rough weekly table.

Estimate: 10 hours = 1.5 input/date reconciliation + 3.5 three daily schedules/formulas + 2 priority/deadline and assumption checks + 1.5 summaries/layout + 1.5 independent cross-checks. Actual production or supplier waiting is outside the work unit.

<a id="work-gdpval-fd6129bd-gpt54"></a>

### Prepare a change-control SOP and form

Task `fd6129bd-f095-429b-873c-dcc3137be2c3`; Project Management Specialists.

The 642-word source specifies thresholds: more than two business days of delay, over $5,000 budget change, contractual/CRO scope, or regulatory filing changes. It gives PM, QA, technical operations, finance and regulatory routing, low-risk processing, required form fields and a central tracker. The work is to resolve and document this existing workflow, not discover a new approval system. The prompt asks for a completed form without supplying a case; the target uses a labelled illustrative business change and flags different_task. The human reference invents a GMP antifoam/endotoxin change and approval; those are not observed facts and must not be used as evidence of a completed real review.

Estimate 4.5 hours: 1 hour mapping thresholds, conditional approvals and conflicting responsibility language; 1.5 hours drafting the SOP; 1 hour building the form, example and tracker; 1 hour checking field completeness and the low-risk exception. No actual clinical quality decision, client meeting or approval waiting time is included.

<a id="work-gdpval-ec591973-gpt54"></a>

### Present a differentiated retail-channel strategy

Task `ec591973-04d5-48c0-981c-1ab2fcec2dc1`; First-Line Supervisors of Non-Retail Sales Workers.

There are no numerical business inputs. The supplied reference is one slide with three channel columns and KPIs, confirming that the deliverable is a compact strategy argument rather than an implementation plan or financial model. The prompt's store closures, low-volume stockouts, staffing constraints and weak open-sell expertise should drive distinct choices. Generic full-assortment recommendations without door-level investment discipline would miss the task. No unsupported ROI or retention lift should be invented. Assortment, CRM/loyalty, service and activation choices must fit a readable single slide and five-minute verbal arc.

Estimate: 2 hours = 0.75 structure the channel choices + 0.75 design/edit the slide + 0.5 rehearse the logic and check readability. The five-minute pitch is the design target, not an additional observed human performance time.

<a id="work-gdpval-fd3ad420-gpt54"></a>

### Propose a multi-state qualifying-broker compensation model

Task `fd3ad420-6f7d-43b1-a990-c0c5c047d071`; Real Estate Brokers.

The source Word document provides headings and options, leaving all percentages and dollar amounts unspecified. Selecting coherent commercial terms is part of the work; the reference's 75/15/10, $1,000, $250 and 5% figures are not market evidence. It also changes Sample Realty to another company and presents qualifying-broker income as passive despite oversight obligations. A recommended structure should allocate the gross commission fully and explain who funds any self-sourced-lead uplift or flat-fee alternative, avoiding incompatible stacked splits.

Original regulatory checks matter even for a one-page proposal: North Carolina distinguishes QB from the BIC for each office, https://bulletins.ncrec.gov/do-i-need-a-firm-license/ ; Georgia Rule 520-1-.07 retains supervision/instruction responsibilities, https://grec.state.ga.us/wp-content/uploads/pdfs/About/520-1-%2007%20For%20the%20Website.pdf ; Florida's company-qualifying process is documented in https://www2.myfloridalicense.com/re/documents/DBPR_RE_13_Broker_Transactions.pdf . These do not set compensation percentages, but prevent the proposal from claiming that a license-only arrangement removes mandatory duties. Recruiting can be optional without implying oversight is optional. Equity requires separately documented eligibility and vesting; the task is not to draft grant instruments or obtain licenses.

Estimate: 4 hours = 1.5 scope/regulatory checks + 1 consistent commercial terms and examples + 1 draft/design one page + 0.5 totals and responsibility review.

<a id="work-gdpval-d4525420-gpt54"></a>

### Recommend an overnight grocery manager

Task `d4525420-a427-4ef2-b4e9-2dcc2d31b3b6`; First-Line Supervisors of Retail Sales Workers.

There are thirteen candidates and 52 weekly productivity observations each, plus attendance points, performance labels and short notes. The human-readable evaluation sheet contains shifted average formulas: for example, Mark's formula refers to Brian's source row. Recompute by name rather than trusting cached/formula-linked rankings. Brian averages 74.731 cases/hour with zero attendance points and helps outside his area; Sophia averages 93.962 with two points and is learning aspects of management. Monica's much higher 187.288 does not outweigh notes that she does not work well with others. These are task-provided job observations, not invented personality judgments.

The stated criterion permits a reasoned choice between demonstrated cross-team contribution and explicit management development; productivity is the lowest-priority factor and should not determine the result. One active hour estimates twenty minutes checking the evaluation/attendance source and productivity alignment, twenty comparing the leading candidates on the requested priorities, and twenty drafting and checking the short rationale. Conducting new interviews or making an actual personnel decision is not included.

<a id="work-gdpval-dfb4e0cd-gpt54"></a>

### Screen grant awards for spending-rate concerns

Task `dfb4e0cd-a0b7-454e-b943-0dd586c2764c`; Compliance Officers.

The source has 2,458 awards and 13 substantive columns. The prompt explicitly requires FFR Expenditure Amt divided by Total Awarded Amt, not either drawdown column. Using unrounded day fractions (as-of minus start)/(end minus start), strict spending inequalities and inclusive time thresholds gives 2 fast and 51 slow awards; fast IDs are 322 and 480. The reference rounds both ratios to two decimals before filtering and returns 76 awards, changing boundary classifications. The professional target uses unrounded calculations and display-only rounding. A spending flag is a contact priority, not a legal finding.

Estimate 3 hours: 45 minutes inspecting dates, numerator choice and thresholds; 60 minutes formulas, filters and the eight-column export; 45 minutes checking threshold cases and totals against original rows; 30 minutes formatting and documenting the as-of date. The volume is handled with formulas rather than manual per-award review. The original human reference's rounding mistake does not reduce the target to reproducing that mistake.

<a id="work-gdpval-f841ddcf-gpt54"></a>

### Summarize June shipments and delayed purchase orders

Task `f841ddcf-2a28-4f6d-bac3-61b607219d3e`; Order Clerks.

The source contains 66 populated POs, not the 113 rows suggested by worksheet dimensions. June is defined by actual shipment date, regardless of the original ship window. The independent audit finds 48 June shipments: ordered cost $145,218.80, shipped cost $140,008.204, short-shipped $5,210.596, overall fill 96.4119%. Display dollars to cents after aggregation; averaging individual fill percentages would not give the weighted total.

The requested delayed cohort requires both ship-start and cancel dates in June, then actual shipment in July: five POs across four accounts, ordered $13,300 and shipped $13,248. June-start windows ending in July are not automatically delayed under that explicit definition. Three source actual dates lie after the stated July 7 as-of date; these do not enter either selected cohort, but should not be represented as already observed on July 7. The existing reference's totals match the relevant native selection and are checked rather than treated as timing evidence.

Estimate: 2 hours = 0.5 verify date/amount fields and selection + 0.5 grouped tables and formulas + 0.5 filterable layout and recap + 0.5 reconcile boundary records and rounding. No order fulfillment or account communication is included.
