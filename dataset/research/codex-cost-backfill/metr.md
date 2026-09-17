# METR cost backfill for the Codex dataset

*Created 2026-09-13 14:21.*

## TL;DR

All 399 METR rows in the Codex `points.csv` are keyed in `metr.csv`. **111 get `reported`**: METR's
release carries a per-run `generation_cost` for the four models it ran through Vivaria natively
(davinci-002, GPT-4 0314, DeepSeek-R1, gpt-oss-120b), and the mean over each point's exact run set
is the same unit and statistic as its `compute_flops`. **288 get `not_available`**: every Time
Horizon 1.1 run was imported from Inspect, and the importer leaves `generation_cost` at 0.0, so the
only observed quantity is `tokens_count` — an undecomposed `source_total` that per METR's own
Vivaria code includes cache reads and writes. No input/output split is published, so a list price
cannot be applied without assuming one. **The four cost-bearing models show why that assumption
would not be safe**: their observed blended rates run from 0.49x to 2.96x what the in-force list
input rate implies, and for gpt-oss-120b the reported cost is 2.96x *below* the cheapest published
rate, which means the token counter is not the billed quantity. **`human_cost_usd` is blank on all
399 rows**: the release does report a `human_cost`, but it is exactly `human_minutes` x 143.61
USD/h on all 65,637 runs in both exports — a wage derivation, which `COLUMNS.md` bars.

Next action for the merge: apply `metr.csv` keyed on `point_id`. If Damon wants the 288 Inspect rows
priced anyway, the decision to make is which single rate to apply to an undecomposed total; nothing
further can be recovered from the public release.

## Counts

| Basis | Rows | Models | Sum of ai_cost_usd, USD |
|---|---:|---|---:|
| reported | 111 | 4 | 1004.40 |
| not_available | 288 | 8 | — |
| list_price | 0 | — | — |

| human_cost_basis | Rows |
|---|---:|
| not_available | 399 |
| reported_payment | 0 |
| reported_price | 0 |

Scope check: the Codex expansion note assigns 402 IDs a disposition — 399 rows in `points.csv` plus
three nominal duration-bin IDs (`agen-metr2-30min-opus45`, `agen-metr2-2h-opus45`,
`agen-metr2-8h-opus45`) retained as `unresolved_work_unit` and never written as rows. This file
covers the 399 that exist.

## Per-model figures on the reported rows

Cost per run, averaged over all recorded runs of that task/model, matching `compute_statistic: mean`
and `compute_subset: all`.

| Model ID | Rows | Run date | Sum, USD | Median row, USD | Max row, USD | Blended rate, USD per M tokens |
|---|---:|---|---:|---:|---:|---:|
| davinci-002-metr | 24 | 2024-12 to 2025-01 | 18.78 | 0.7086 | 1.4889 | 2.0000 |
| gpt-4-0314 | 29 | 2024-12, 2025-06 | 898.83 | 35.9749 | 99.8975 | 60.7079 |
| deepseek-r1 | 29 | 2025-06-18 | 83.53 | 1.1491 | 9.9257 | 1.2185 |
| gpt-oss-120b | 29 | 2025-09-29 to 2025-09-30 | 3.26 | 0.0441 | 0.3875 | 0.0592 |

Blended rate is the median across the model's points of (mean cost) / (mean native tokens).

## Method

**Run sets.** Each point's exact runs come from the Codex notes, not re-derived: the 369 expanded
points from `agent-work/derived/metr/metr-expanded-records.jsonl`, the 30 initial points from the run IDs in
`research/metr/point-sections.md`, resolved against the retained release
(`agent-work/sources/metr/eval-analysis-public/reports/time-horizon-1-{0,1}/data/raw/runs.jsonl` @ 52cb829).
Every run ID resolved uniquely and the mean `tokens_count` reproduced each row's `tokens` field
exactly on all 399 rows, which confirms the cost mean is taken over the same runs as the compute
mean. METR's own `wrangle/cost.py` aggregates `generation_cost` with `mean` grouped by
(alias, task_id), the same unit this dataset uses.

**`ai_cost_date`** is the median run start date in UTC across the point's runs. 99 of the 111
reported points span at most 5 days; the 12 that span 25 to 35 days are all davinci-002 or GPT-4
runs inside the 2024-12 to 2025-01 window, and neither model repriced in it, so the convention
changes nothing.

**`human_cost_usd`.** The release's `human_cost` divided by `human_minutes` is 143.61 USD/h on every
one of the 41,629 TH1.0 and 24,008 TH1.1 runs, with no second value anywhere. That is a flat wage
applied to time, which `COLUMNS.md` excludes by name, and the release states no payment per task and
no per-baseliner rate. All 399 rows are therefore blank with `not_available`. If METR's papers turn
out to state 143.61 USD/h as an actual baseliner pay rate, the column still cannot take it, because
the per-task figure would remain a time-and-wage derivation.

## Why the 288 Inspect rows are not priced

`generation_cost` is 0.0 on all 1,391 Claude Opus 4.6 runs, all 1,602 GPT-5.3-Codex runs, and every
other TH1.1 Inspect-imported alias — a structural gap in the Vivaria Inspect importer, not a claim
that the runs were free. What survives is `tokens_count`, which
`research/metr/cache-accounting.md` establishes is a `source_total`: Vivaria's `shared/src/types.ts`
defines prompt totals to include cache reads and writes, and the August 2025 runs-view migration
adds prompt, output and caller-supplied serial-action tokens without subtracting cache reads. There
is no published rate for such an aggregate. Choosing the input rate, the output rate, or a blend is
an assumption about a split the source does not state, and `DECISIONS.md` makes the cost columns
observed-only.

The four cost-bearing models are the test of whether that assumption would be harmless, and it would
not be. Pricing their native-token totals at the list rate in force on the run date, against what
METR actually reports:

| Model ID | Rows | Native tokens, M | Reported, USD | At list input rate, USD | At list output rate, USD | Input/reported | Output/reported |
|---|---:|---:|---:|---:|---:|---:|---:|
| davinci-002-metr | 24 | 9.388 | 18.78 | 18.78 | 18.78 | 1.00 | 1.00 |
| gpt-4-0314 | 29 | 14.821 | 898.83 | 444.64 | 889.28 | 0.49 | 0.99 |
| deepseek-r1 | 29 | 78.498 | 83.53 | 43.17 | 171.91 | 0.52 | 2.06 |
| gpt-oss-120b | 29 | 64.228 | 3.26 | 9.63 | 38.54 | 2.96 | 11.83 |

Rates from `research/cost/list-prices.csv`: davinci-002 flat 2.00 from 2023-08-22; gpt-4 8k
30.00/60.00; deepseek-reasoner 0.55/2.19 for the 2025-01-20 sheet; gpt-oss-120b Together serverless
0.15/0.60 from 2025-08-05.

Three things fall out of that table. **gpt-oss-120b's reported cost is below the cheapest published
rate for the model** — 0.0592 USD/M against a 0.15 USD/M input rate, and no gpt-oss run anywhere in
the release exceeds 0.1422 USD/M — so METR's counted tokens and METR's billed tokens are
demonstrably different quantities, and list pricing would overstate by about 3x. **GPT-4 0314's
observed blended rate, 60.24 to 67.04 USD/M across the 174 selected runs, exceeds the 8k tier's
60.00 output rate**, which the 8k sheet cannot produce at any input/output mix; the 32k tier
(60.00/120.00) fits it at a 0.7% to 7.4% output share. The registry's gpt-4-0314 sheet also ends
2024-06-06, and these runs are from 2024-12 and 2025-06, so no list price was in force on the run
date at all. **DeepSeek-R1 sits at 2.2x its input rate**, a much larger output share than the
prompt-dominated agentic pattern would suggest. Only davinci-002, whose sheet is a single flat rate
with no split to guess, reconstructs exactly.

## Worked example

`agen-metr3-atariepochs-gpt3dv` — davinci-002 on `local_research/atari_epochs`, 8 runs, all included
per `compute_subset: all`.

Mean native tokens across the 8 runs is 256,498.75, which is the row's `tokens` field. The mean of
the 8 released `generation_cost` values is 0.512998 USD, and that is what goes in `ai_cost_usd` with
basis `reported`. `ai_cost_date` is 2024-12-24, the median run start.

The list-price reconstruction: davinci-002 is 2.00 USD per million tokens on both input and output
from 2023-08-22, with no cached rate and no split to assume, so 256,498.75 / 1e6 x 2.00 = 0.512998
USD. It agrees to every digit, and the per-run ratio is exactly 2.000000 USD/M on all 955 TH1.0
davinci-002 runs that carry both a cost and a token count, with no second value. This is the one model where `reported` and `list_price` would give the same
number.

The same task with gpt-oss-120b (`agen-metr3-atariepochs-oss120b`) is the counterexample: 6 runs,
mean 792,593.33 native tokens, reported mean cost 0.047666 USD. Together's 0.15 USD/M input rate on
those tokens would be 0.118889 USD, 2.49x the figure METR reports for the same runs.
