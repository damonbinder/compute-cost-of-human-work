# OpenAI's cache-write charge — when it started, who it touches, and what it is worth

*Created 2026-09-13 18:58.*

## TL;DR

**OpenAI charges 1.25x the uncached input rate for a cache write on GPT-5.6 and later, and on
nothing else.** The Cache writes column reached `developers.openai.com/api/docs/pricing` on
**2026-07-09**, GPT-5.6 launch day: the 2026-07-07 capture has no such column anywhere on the
page, and the 07-09 capture carries it in every tier table with a rate on the three GPT-5.6 rows
and `-` on gpt-5.5, gpt-5.5-pro, the whole 5.4 line and every older model. The prompt-caching
guide states the same split as a rule — "For GPT-5.6 and later, cache writes cost 1.25x the
standard, uncached input-token rate" against "No additional cache-write charge" for GPT-5.5 and
for "Other earlier models". **The independent reviewer's finding was right about the rate and the
column, and wrong about the scope: this is not a charge that applies to every model and tier.**
GPT-4o, o1, o3, GPT-4.1 and the whole GPT-5 through GPT-5.5 ladder never carried it.

**Writes are reported.** On GPT-5.6 and later there is a counter,
`usage.input_tokens_details.cache_write_tokens`, and `input_tokens` partitions into three
disjoint buckets — ordinary, cached-read and written — each billed at its own rate. The charge is
not additive. **But no harness or leaderboard behind any row in this folder records that
counter**, so in practice writes sit invisibly inside each row's uncached-input residual and
**no row can be repriced exactly; every one can only be bounded.**

**Thirteen distinct rows are exposed, and the bound is 25% of each row's input-rate term.**
`research/cost/list-prices.csv` gains a `cache_write_usd_per_m` on seven rows (the six GPT-5.6
windows and GPT-6 Astra) and stays blank on the other 53 OpenAI rows, where blank means the page
prints `-`. Of the 268 OpenAI-priced `list_price` rows across the five sources the brief names,
19 row-instances — 13 distinct `point_id`s, several appearing in both a candidate file and the
promoted file — are on a GPT-5.6 or GPT-6 endpoint dated after the charge began. **Median bound 3.2% of `ai_cost_usd`,
maximum 22.96%**; in dollars, median $0.021 and maximum $0.48. The whole exposure across
`points.csv` and `excluded.csv` together is **$0.66**, and `research/codex-cost-backfill.csv` is
untouched — its newest OpenAI-priced row is dated 2026-03-27.

**Next action for the coordinator:** the price table is corrected and regenerates. The thirteen
rows need a ruling, not a recomputation — either leave `ai_cost_usd` as the lower bound it now
provably is and record the ceiling, or widen the two APEX-Agents rows, which are the only ones
where the bound is material.

## What OpenAI charges, and since when

| Window | Cache writes column on the pricing page | Models carrying a rate | Multiple | Evidence |
|---|---|---|---|---|
| to 2026-07-07 | absent | — | — | `agent-work/sources/cost/wayback/openai-pricing-2026-07-07.txt` |
| 2026-07-09 onward | present in Standard, Batch, Flex and Fast mode | GPT-5.6 Sol, Terra, Luna | 1.25 | `agent-work/sources/cost/wayback/openai-pricing-2026-07-09.txt` |
| 2026-08-07 onward | same | + GPT-5.6 Cyber | 1.25 | `agent-work/sources/cost/wayback/openai-pricing-2026-08-22.txt`, Cyber table: $12.50 / $1.25 / $15.625 / $75.00 |
| 2026-09-03 onward | same | + GPT-6 Astra | 1.25 | live page and `agent-work/sources/factorio-astra/openai-list-prices-2026-09-13.json` |

Six captures of the same URL fix the boundary and the scope:

- **2026-06-05** and **2026-07-07**: the Flagship table is Model / Input / Cached input / Output.
  There is no Cache writes column anywhere on the page, in any tier tab.
- **2026-07-09**, the day the GPT-5.6 family was released: Model / Input / Cached input / **Cache
  writes** / Output, in the Standard, Batch, Flex and Priority tabs alike. `gpt-5.6-sol` $5.00 /
  $0.50 / **$6.25** / $30.00, `gpt-5.6-terra` $2.50 / $0.25 / **$3.125** / $15.00, `gpt-5.6-luna`
  $1.00 / $0.10 / **$1.25** / $6.00. On the same table, `gpt-5.5`, `gpt-5.5-pro`, `gpt-5.4`,
  `gpt-5.4-mini`, `gpt-5.4-nano` and `gpt-5.4-pro` print `-` in that column.
- **2026-07-29**, **2026-08-21**, **2026-08-22**: the column persists and tracks the two GPT-5.6
  repricings at 1.25x throughout — Terra $3.125 to $2.50, Luna $1.25 to $0.25, Sol $6.25 to $5.00
  when the promotion landed. Long context is 2x on writes as on input; Batch and Flex are half,
  Fast mode double.
- **2026-09-13 live**: the full All-models table carries the column for every model on the page
  and a rate for exactly five — `gpt-6-astra`, the three `gpt-5.6` models and `gpt-5.6-cyber`.
  `gpt-5.5-cyber`, `gpt-5.2`, `gpt-5.1`, `gpt-5`, `gpt-5-mini`, `gpt-5-nano`, `gpt-4.1` and its
  mini and nano, `gpt-4o`, `gpt-4o-2024-05-13`, `gpt-4o-mini`, `o1`, `o1-pro`, `o3`, `o3-pro`,
  `o4-mini`, `o3-mini`, `gpt-4-turbo`, `gpt-4-0613`, the 3.5-turbo line, `davinci-002` and
  `babbage-002` all print `-`. The Multimodal, Image, Specialized and Finetuning tables have no
  such column at all.

The prompt-caching guide, retained at
`agent-work/sources/cost/live/openai-prompt-caching-2026-09-13.md`, states it as a model-generation rule
rather than a per-model fact, which is what makes the 2024-2025 models safe to leave blank
without a capture of every historical sheet: its model-comparison table gives "Cache write
charge — 1.25x the uncached input-token rate" for "GPT-5.6 and later" against "No additional
cache-write charge" for both "GPT-5.5 and GPT-5.5 Pro" and "Other earlier models".

**Artificial Analysis corroborates the scope independently.** Its model records carry a
`cacheWritePrice` field, and both AA extracts this folder already retains carry it.
`agent-work/sources/terminal-bench/aa-terminalbench-v2-1-token-counts.csv` gives $12.50 for
`gpt-6-astra` and its high and medium variants, $5.00 for `gpt-5-6-sol` and `gpt-5-6-sol-xhigh`,
$2.50 for `gpt-5-6-terra` and $0.25 for `gpt-5-6-luna` — 1.25x each model's input rate.
`agent-work/sources/apex-agents/aa-apex-agents-model-records.json` gives the same $2.50 and $0.25 for Terra
and Luna and **null for `gpt-5-5` and `gpt-5-4`**. That is a second party reading the same sheet
the same way, boundary included.

## How a written token is reported

The guide's own cost snippet is the specification:

```
input_tokens        = usage.input_tokens
cached_tokens       = usage.input_tokens_details.cached_tokens
cache_write_tokens  = usage.input_tokens_details.cache_write_tokens
ordinary_input      = input_tokens - cached_tokens - cache_write_tokens
```

Three consequences matter for pricing a row.

1. **A counter exists.** `cache_write_tokens` is a real field on GPT-5.6 and later, so a harness
   that wanted to price exactly could.
2. **The buckets are disjoint and the charge is not additive** — "input tokens use the
   uncached-input, cached-input, or cache-write rate". A written token is billed once, at 1.25x,
   instead of once at 1.0x. The delta a naive pricing misses is therefore **0.25x the input rate
   on the written tokens only**, never 1.25x.
3. **A harness that records only `input_tokens` and `cached_tokens` hides its writes inside its
   uncached residual.** That is the situation for every row in this folder. Artificial Analysis
   publishes `input`, `cacheableInput`, `answer` and `reasoning` and no write counter; the
   ALE-Bench leaderboard publishes input, output and a billed cost and no cache counters at all;
   the ARC-AGI-3 recordings carry `cached_tokens` in a reporting-only field with no write
   counter. **So no exact repricing is available for any row, only the bound.**

Two structural facts cut the other way and are worth recording, because they mean the bound is
loose rather than a likely value. Writes are capped at **four per request**, and a reused prefix
refreshes its lifetime **without another write charge** — so in a long agent rollout with a
stable prefix, the written fraction of uncached input falls as the rollout goes on. A cache hit
rate of 0.993, which is what AA reports for the GPT-5.6 and Astra runs here, is exactly the
regime where writes are a small and shrinking share.

## Method for the bound

For each affected row: **bound = 0.25 x (the row's input-rate term)**, where the input-rate term
is the part of `ai_cost_usd` that prices tokens at the gross input rate. Every row's stored
`ai_cost_usd` was first reproduced from its retained token counters and the rates in
`list-prices.csv` for the window its `ai_cost_date` selects; all thirteen reproduce to
floating-point exactness, so the term being scaled is the term actually inside the row.

The three families of row differ only in how the uncached-input count is recovered:

- **ALE-Bench (4 rows).** Per-sample input from the leaderboard, minus the cache reads
  `candidates/ale-bench/calculations.json` inverts from the gap between gross list price and
  billed cost, times the 15 samples that make the row's work unit.
- **Terminal-Bench (7 rows).** AA's `input_tokens` minus `cacheable_input_tokens`, divided by 267
  trials.
- **APEX-Agents (2 rows).** AA's gross `input`, divided by 452 tasks. `cacheableInput` is null for
  this benchmark, so no cache split is observed at all and the whole input counter is the
  uncached term — which is why these two carry by far the largest bound.

Rows on OpenAI endpoints that predate 2026-07-09, or whose model is GPT-5.5 or older, have a
bound of exactly zero, and `research/cost/openai-cache-write.csv` carries them with that zero and
the reason rather than omitting them, so the file joins cleanly against any of the five sources.

## The exposed rows

Every figure is USD for the row's own work unit. The max understatement is the ceiling if every
uncached input token had been a cache write; an em dash under exact repricing means the row's
evidence carries no `cache_write_tokens` counter, which is every row.

| File | point_id | model | ai_cost (USD) | input-rate term (USD) | max understatement (USD) | share of cost (%) | exact repricing (USD) |
|---|---|---|---|---|---|---|---|
| points.csv | agen-alebench-short-luna56max | gpt-5-6-luna | 1.04010 | 0.090866 | 0.022716 | 2.18 | — |
| points.csv | agen-alebench-short-sol56max | gpt-5-6-sol | 15.02566 | 0.297830 | 0.074458 | 0.50 | — |
| points.csv | agen-alebench-short-terra56max | gpt-5-6-terra | 14.45109 | 0.015110 | 0.003777 | 0.03 | — |
| points.csv | agen-alebench-short-astra6max | gpt-6-astra | 42.25162 | 0.085108 | 0.021277 | 0.05 | — |
| excluded.csv | work-apex-agents-gpt56terra | gpt-5-6-terra | 2.12637 | 1.918778 | 0.479695 | 22.56 | — |
| excluded.csv | work-apex-agents-gpt56luna | gpt-5-6-luna | 0.24249 | 0.222668 | 0.055667 | 22.96 | — |
| candidates/ale-bench/points.csv | agen-alebench-short-luna56max | gpt-5-6-luna | 1.04010 | 0.090866 | 0.022716 | 2.18 | — |
| candidates/ale-bench/points.csv | agen-alebench-short-sol56max | gpt-5-6-sol | 15.02566 | 0.297830 | 0.074458 | 0.50 | — |
| candidates/ale-bench/points.csv | agen-alebench-short-terra56max | gpt-5-6-terra | 14.45109 | 0.015110 | 0.003777 | 0.03 | — |
| candidates/ale-bench/points.csv | agen-alebench-short-astra6max | gpt-6-astra | 42.25162 | 0.085108 | 0.021277 | 0.05 | — |
| candidates/terminal-bench/points.csv | agen-tbench21-aa-gpt56luna | gpt-5-6-luna | 0.01689 | 0.001172 | 0.000293 | 1.74 | — |
| candidates/terminal-bench/points.csv | agen-tbench21-aa-gpt56sol | gpt-5-6-sol | 0.17060 | 0.028923 | 0.007231 | 4.24 | — |
| candidates/terminal-bench/points.csv | agen-tbench21-aa-gpt56sol-xhigh | gpt-5-6-sol-xhigh | 0.11992 | 0.021807 | 0.005452 | 4.55 | — |
| candidates/terminal-bench/points.csv | agen-tbench21-aa-gpt56terra | gpt-5-6-terra | 0.18120 | 0.023168 | 0.005792 | 3.20 | — |
| candidates/terminal-bench/points.csv | agen-tbench21-aa-gpt6astra | gpt-6-astra | 0.37415 | 0.083615 | 0.020904 | 5.59 | — |
| candidates/terminal-bench/points.csv | agen-tbench21-aa-gpt6astra-high | gpt-6-astra-high | 0.19766 | 0.055373 | 0.013843 | 7.00 | — |
| candidates/terminal-bench/points.csv | agen-tbench21-aa-gpt6astra-medium | gpt-6-astra-medium | 0.13705 | 0.042080 | 0.010520 | 7.68 | — |
| research/cost/claude-rows-backfill.csv | work-apex-agents-gpt56terra | gpt-5-6-terra | 2.12637 | 1.918778 | 0.479695 | 22.56 | — |
| research/cost/claude-rows-backfill.csv | work-apex-agents-gpt56luna | gpt-5-6-luna | 0.24249 | 0.222668 | 0.055667 | 22.96 | — |

Per file, over the OpenAI-priced `list_price` rows each contains:

| File | OpenAI list_price rows | exposed | median bound (USD) | max bound (USD) | median bound (%) | max bound (%) |
|---|---|---|---|---|---|---|
| points.csv | 75 | 4 | 0.02200 | 0.07446 | 0.27 | 2.18 |
| excluded.csv | 19 | 2 | 0.26768 | 0.47969 | 22.76 | 22.96 |
| candidates/ale-bench/points.csv | 19 | 4 | 0.02200 | 0.07446 | 0.27 | 2.18 |
| candidates/gaia/points.csv | 25 | 0 | — | — | — | — |
| candidates/terminal-bench/points.csv | 7 | 7 | 0.00723 | 0.02090 | 4.55 | 7.68 |
| candidates/textquests/points.csv | 1 | 0 | — | — | — | — |
| research/cost/claude-rows-backfill.csv | 49 | 2 | 0.26768 | 0.47969 | 22.76 | 22.96 |
| research/codex-cost-backfill.csv | 73 | 0 | — | — | — | — |
| **All** | **268** | **19** | **0.02128** | **0.47969** | **3.20** | **22.96** |

The four ALE-Bench rows and the two APEX-Agents rows each appear twice, once in a candidate or
backfill file and once in the promoted `points.csv` or `excluded.csv`; the distinct count is 13.
No candidate folder other than ALE-Bench and Terminal-Bench holds an exposed row, and the 17
`candidates/*/points.csv` files without cost columns hold none by construction.

**Why the two APEX-Agents rows are the outliers.** They are the only exposed rows whose source
publishes no cache split at all, so their cost prices 959,389 and 1,113,342 input tokens per task
at the full gross rate. Their cost is already an acknowledged upper bound on the input side —
`research/cost/claude-rows-backfill.csv` says so in the derivation — and the cache-write bound
sits on top of it in the same direction. The honest reading is that these two rows have a wide
cost interval on the input term, not that they are 23% too low.

## What this does not cover

**Twenty-four `reported` rows are on GPT-5.6 or GPT-6 endpoints and are outside the brief, but
the same arithmetic reaches some of them.** Eleven are in `points.csv` (nine ARC-AGI-3 Astra
rows, Portal and Factorio), nine in `candidates/arc-agi-3/points.csv` and four in
`candidates/terminal-bench/points.csv`. A `reported` figure that an operator read off an invoice
is unaffected by definition. A `reported` figure that a harness computed from its own token
counters and its own price table is a list-price reconstruction wearing a different label, and it
understates by the same 25%-of-the-input-term ceiling if that price table has no write key.
`reviews/arc-agi-3-independent.md` establishes that ARC's cost model has exactly three keys —
`date`, `input`, `output` — so the nine ARC rows are in the second category. Their exposure is
small for the same reason the ALE-Bench Astra row's is: their input share is a few percent of a
reasoning-dominated bill. It is a coordinator call whether to bound them too.

**`research/cost/claude-rows-backfill.md` still carries the superseded rule** — "Cache writes are
zero everywhere except the Anthropic endpoints and `epoch/qwen3.7-max`" — in its prose. It is not
corrected here, because the backfill CSV and its note belong to another pass and this one was
told not to edit them. The rule is wrong for the two APEX-Agents rows in that same file and
correct for every other row in it.

## Two adjacent errors, flagged and not fixed

Both sit in files this pass edited, both are outside the cache-write brief, and neither is
touched.

1. **`list-prices.csv`, `gpt-6-astra`, `long_context_rule`** says "long context input 20.00 /
   output 100.00 above the short-context window". The live page's long-context Astra output is
   **$75.00**, not $100.00 — 1.5x, not 2x. The retained
   `agent-work/sources/factorio-astra/openai-list-prices-2026-09-13.json` says the same thing in words:
   "2x input and cache rates and 1.5x output". Nothing in this folder prices an Astra
   long-context request, so no row moves.
2. **`agent-work/sources/cost/live/openai-pricing-2026-09-13.md`** says "models with a long-context variant
   show 2x standard input and output". Input, cached input and cache writes are 2x; output is
   1.5x on every model that has a long-context tier (Sol $20.00 to $30.00, Terra $12.00 to
   $18.00, Luna $1.20 to $1.80, Astra $50.00 to $75.00).

## What changed in the shared price table

- **`research/cost/list-prices.csv`**: `cache_write_usd_per_m` filled on seven rows —
  `gpt-5-6-sol` 6.25 then 5.00, `gpt-5-6-terra` 3.125 then 2.50, `gpt-5-6-luna` 1.25 then 0.25,
  `gpt-6-astra` 12.50 — each transcribed from a capture that also carries that row's input rate,
  not derived. The six GPT-5.6 rows' `long_context_rule` now says the 2x long-context tier covers
  cache writes as well as input; the Astra row's note is left exactly as it was, for the reason
  in the section above. The other 53 OpenAI rows keep a blank cell, which under the file's own
  convention means the provider published no rate: here the page prints `-`.
- **`research/cost/build_list_prices.py`**: the same seven values inline, plus a comment on the
  OpenAI block recording the 2026-07-09 boundary.
- **`research/cost/list-prices.md`**: rule 5 rewritten (three providers charge for the write, not
  one), the OpenAI section's "There is no cache-write charge" removed and replaced with the dated
  boundary and the usage-object consequence, and the Anthropic section's "the only provider in the
  table that charges for the cache write" corrected.
- **`agent-work/sources/cost/live/openai-pricing-2026-09-13.md`**: the dropped Cache writes column restored
  across the whole table, plus GPT-5.6 Cyber and GPT-5.5 Cyber, and a tier-structure bullet
  saying which tables carry the column.
- **New retained evidence**: `agent-work/sources/cost/wayback/openai-pricing-2026-06-05.txt`,
  `agent-work/sources/cost/wayback/openai-pricing-2026-07-07.txt`,
  `agent-work/sources/cost/wayback/openai-pricing-2026-07-09.txt` and
  `agent-work/sources/cost/live/openai-prompt-caching-2026-09-13.md`, all four listed in
  `agent-work/sources/cost/PROVENANCE.md`.

## Reproducing

```
python3 research/cost/build_list_prices.py \
    "../AI Compute vs Human Time/dataset/models.csv" \
    models.csv \
    research/cost/list-prices.csv
```

**One caveat, and it is not about cache writes.** As of 2026-09-13 18:32 the claude-rows
`models.csv` carries two models that were not in it when `list-prices.csv` was last generated —
`minimax-m3` and `gemini-3-pro-preview` — so a regeneration today writes **315** rows, not the
313 the file and `list-prices.md`'s coverage table carry, the two extras being blank-price
fall-through rows. That drift predates this pass. Against the registry state `list-prices.csv`
was built from, the corrected script reproduces the corrected file **byte-for-byte**, verified
with `cmp`. Whoever next regenerates should decide whether to admit the two models and update the
coverage counts in `list-prices.md` at the same time.

`research/cost/openai-cache-write.csv` is the per-row table above plus the 249 zero-bound rows,
one line per (file, point_id).
