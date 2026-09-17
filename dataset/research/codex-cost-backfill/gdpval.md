# GDPval cost backfill for the Codex dataset

*Created 2026-09-13 14:14.*

## TL;DR

All 440 GDPval rows in the Codex `points.csv` are backfilled in `gdpval.csv`: 220 `gpt-5-high` rows at
**$0.762 per task, basis `reported`**, recovered from the GDPval paper's own stated mean expert cost
($361) and stated naive cost improvement (474x); 220 `claude-opus-5-max` rows at **$6.5634 per task,
basis `list_price`**, from Artificial Analysis's GDPval-AA v2 token counts priced at Anthropic's
published rates. **`human_cost_usd` is blank and `human_cost_basis` is `not_available` on every
row**: the paper's $361 is explicitly hours multiplied by a BLS median wage, which the column
definition bars ("Never derived from time and a wage"), and no expert payment is reported. Two things
to flag at merge: the GPT-5 cost is **not independent of `compute_flops`** (the Codex note inverts the
FLOP figure from this same dollar amount), and the two models' costs differ by 8.6x while their
compute proxies differ by only 1.10x.

## Counts by basis

| Basis | Rows | Model | ai_cost_usd | ai_cost_date |
|---|---|---|---|---|
| reported | 220 | gpt-5-high | 0.762 | 2025-09-25 |
| list_price | 220 | claude-opus-5-max | 6.5634 | 2026-09-12 |
| not_available | 0 | — | — | — |

Human side: 440 rows `not_available`, 0 `reported_payment`, 0 `reported_price`.

Row set: every row in `dataset/points.csv` whose `source_dataset` names GDPval — 218 `GDPval`
(gpt-5-high), 218 `GDPval / GDPval-AA v2` (claude-opus-5-max), and 4 `GDPval gold subset` (2 of each
model). 220 distinct task hashes x 2 models = 440 point_ids, all unique, `-gpt5` / `-opus5` suffix
agreeing with `model_id` on every row. The Codex `dataset/` has no `excluded.csv`, so nothing else is
in scope.

## GPT-5 high: $0.762 per task, `reported`

The paper states both halves of the quotient and states that the model figure is an invoice.

- Appendix A.2.4: "On average, on our 220 gold subset HT = 404 minutes and HC = $361."
- Table 2, gpt-5 row: naive cost improvement **474x** (win rate 39.0%, naive speed improvement 90x).
- Footnote 8: "For each task, we collected three API completions per model and averaged the observed
  response times recorded in the API metadata. We also recorded the average invoiced cost per task."

So MC = HC / 474 = 361/474 = **0.7616033755274262**, written as 0.762 at the three significant
figures both inputs carry. The speed ratio cross-checks the unit: 404 min / 90 = 4.49 min = 269 s per
completion, so Table 2's ratios are per single completion against the gold-subset means, matching the
row's per-task unit. The paper does not print a dollar model cost anywhere; the quotient is the only
route, and it is exact given the two stated numbers, so this is an observed invoice published in
ratio form rather than an estimate.

`ai_cost_date` = 2025-09-25, the GDPval publication date, as the latest bound on the run. The exact
run date is not published; the runs fall between GPT-5's 2025-08-07 release and publication. Nothing
hinges on the choice — the basis is an invoice, not a price sheet, and OpenAI's GPT-5 sheet
($1.25/$10.00 per M) has been unchanged since 2025-08-07 (`research/cost/list-prices.csv`).

**Circularity flag.** `research/gdpval/gdpval.md#gpt-5-compute` builds the row's `compute_flops`
*from* this dollar figure: 0.7616033755 inverted at $1.25/M input and $10/M output under an assumed
4:1 input:output position ratio, giving 253,867.79 primary positions, plus a 10,000-position helper
allowance, times 2e11 FLOP/token = 5.277355836849508e16. For these 220 rows `ai_cost_usd` and
`compute_flops` are one observation, not two. Any later FLOP-per-dollar conversion applied to them
recovers the assumed 4:1 mix and the 100B parameter assumption, not evidence.

## Claude Opus 5 max: $6.5634 per task, `list_price`

AA publishes no dollar figure for this model on the GDPval-AA v2 page — the page's cost-per-task
chart carries only the twenty cheapest models, and Opus 5 is not among them — but it publishes the
token counts, which is what `list_price` requires.

From the retained record `dataset/sources/gdpval/fetched/aa-opus5-record.json` (AA page fetched
2026-09-12), `canonicalEvalTokenCounts.gdpval`: input 1,443,328,948; cacheableInput 1,407,667,015;
answer 12,091,348; reasoning 9,300,465. Model-level `cacheHitRate` 0.996663404781368. Normalized over
the evaluation's 220 tasks, on the Codex note's accounting (`input` inclusive of cacheable input;
hits = cacheableInput x rate; creations = cacheableInput x (1 - rate)):

| Counter | Tokens per task | Rate USD/M | USD per task |
|---|---|---|---|
| Cache read | 6377137.3 | 0.50 | 3.188569 |
| Cache write | 21349.2 | 6.25 | 0.133432 |
| Fresh input | 162099.7 | 5.00 | 0.810498 |
| Output (answer + reasoning) | 97235.5 | 25.00 | 2.430888 |
| Total | — | — | 6.563387 |

Rates are the `claude-opus-5-max` row of `research/cost/list-prices.csv` (Anthropic sheet from
2026-07-24, no end date, retrieved 2026-09-13), applied per `list-prices.md` rules 4 and 5: cache
reads on their own counter at 0.1x base input, gross non-cacheable input at base input, and the
Anthropic 5-minute cache write at 1.25x base input. AA's record carries the identical price fields
(`price1mInputTokens` 5, `price1mOutputTokens` 25, `cacheHitPrice` 0.5, `cacheWritePrice` 6.25), so
sheet and record agree with no reconciliation needed. `ai_cost_date` = 2026-09-12, the page fetch
date, since AA does not publish the GDPval-AA v2 run date; the sheet has been in force since
2026-07-24, so any date in that window gives the same number.

The compute-counted positions implied by the same decomposition — fresh input + cache creations +
output = 280,684.368325795 per task — reproduce the Codex note's 280684.3683257959 exactly, so the
cost is at the same unit and statistic as `compute_flops`. Per the column definition, cache reads are
included in the cost even though they are excluded from the FLOP term; they are 49% of the dollar
total and 96% of the billed tokens.

### Cross-check against AA's own cost formula

AA's cost-per-task chart is reproducible from these records. Fitting it on the twenty models it does
list, every component matches exactly at N=220 under: cache hits = cacheableInput x cacheHitRate at
`cacheHitPrice`; **everything else of `input`** at `cacheWritePrice` (falling back to the input price
where the provider has none); answer and reasoning at the output price. Applying that formula to Opus
5 gives **$6.766012** per task, 3.0% above the figure used here. The whole difference is the 162,100
non-cacheable input tokens per task, which AA bills at the $6.25 write rate and this backfill bills at
the $5.00 input rate. The house convention is the one that matches Anthropic's actual sheet, so
$6.5634 stands; AA's own number is recorded here in case a later reader wants the site's figure.

### Sensitivity to the transferred cache-hit rate

AA's methodology states that evaluation token counts are combined with live measurements of typical
model cache hit rates rather than the rate realized in the run, so the read/write split is a transfer,
not an observation — the same transfer the compute figure rests on. It dominates the cost:

| Assumption | USD per task |
|---|---|
| Cache hit rate 0.996663 (as stated) | 6.5634 |
| Cache hit rate 1 | 6.4406 |
| Cache feature unused, all input at 5.00 | 35.2338 |
| Cacheable input all billed as fresh writes at 6.25 | 43.2319 |
| As stated, at the 50% batch discount | 3.2817 |

The floor is firm: output alone is $2.4309 per task and does not depend on the cache assumption.

## Human cost: `not_available` on all 440 rows

The brief anticipated `reported_payment` from the paper's $361. That does not survive the column
definition. `human_cost_usd` says "Never derived from time and a wage", and Appendix A.2.4 says HC was
built exactly that way: "we multiplied the reported task completion hours per occupation by the median
hourly wage for each occupation from the U.S. Bureau of Labor Statistics (2025b)". The paper's own
footnote adds that these wage estimates "likely underestimate their true market cost" for experts
recruited on experience. $361 is a wage-model output, not a payment and not a price.

Two further reasons it would not apply even if the basis were allowed. The rows' `human_time` values
are the Codex agent's own per-task professional estimates (1,500 s to 576,000 s across the 440 rows),
not the gold-subset 404-minute mean, so a single collection-mean dollar figure is not at the row's
unit. And the paper reports no payment figure anywhere — experts "were well compensated for their time
and experience", with no amount.

## What was checked and rejected

- No per-task cost or token ledger exists for either system. Confirmed against the HF gold-subset
  release (12 columns, all task-spec side), the paper, the AA page payload, the AA Data API schema,
  and `research/external/gdpval/aa_per_task_check.md`, which verified the same thing independently on
  2026-08-26. The finest public grain is per-model over all 220 tasks, which is what both figures use.
- The paper reports no invoiced cost for Claude, Gemini, or Grok ("We were not able to obtain cost
  estimates for Claude, Gemini, and Grok"), so the Opus rows cannot take a `reported` basis from it
  and the AA route is the only one.
- The 2026-08-26 AA capture (`research/external/gdpval/aa_gdpval_models.csv`) carries the same four
  GDPval token counts and the same $5/$25 prices as the 2026-09-12 capture used here. Only the Elo
  moved (1831.05 to 1735.09). The token and price inputs are stable across the two retrievals.
- The 10,000-position helper allowance in both compute figures has no dollar counterpart and none was
  invented. For GPT-5 any helper calls are already inside the invoice; for Opus, AA's counters are the
  eval's own billed tokens.

## Reproducing

The CSV is generated by keying on `model_id` over the GDPval rows of the Codex `points.csv`; the
arithmetic above is the whole derivation. Nothing in the Codex `dataset/` tree was created or
modified.
