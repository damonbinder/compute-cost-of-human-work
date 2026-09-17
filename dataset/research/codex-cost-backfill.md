# Codex-dataset cost backfill — merged from five block CSVs

*Created 2026-09-13 15:39.*

## TL;DR

`research/codex-cost-backfill.csv` merges the five block CSVs into **1,410 rows, one per Codex
`point_id`, sorted by `point_id`** — the full Codex `dataset/points.csv` set, no duplicates and no
unknown IDs. **924 rows carry an AI dollar figure (394 `reported`, 530 `list_price`) and 486 are
`not_available`; on the human side 111 rows are `reported_payment` and 1,299 are
`not_available`.** The five blocks arrived in near-identical shape: headers matched exactly, all
five used CRLF endings and pure ASCII, no whitespace padding, no empty evidence cells, and the
blank/empty-string and `YYYY-MM-DD` conventions already agreed. **One format fix was applied** — 12
`ai_cost_usd` values in the epoch block were in scientific notation and are now plain decimal at
identical precision.

**Two residuals, both recorded rather than silently resolved.** First, `robo-towel-pr2` appeared in
no block CSV; it is filled at merge as `not_available` / `not_available`, which its own price-table
row and the other-m-z convention both dictate, and its `evidence` cell says so explicitly. Second,
the epoch block rounds `ai_cost_usd` to six decimal places, which costs real precision on the
cheapest rows — `reas-strawberry-gpt-oss20b` recomputes to $0.000041569 and is stored as
$0.000042, a 1.0% error. Nothing else failed: all 15 spot-checks reproduced, and a wider automated
sweep reproduced 228 more.

Next action: apply `codex-cost-backfill.csv` to the Codex rows on `point_id`. The consolidated flag
list at the bottom holds the judgement calls the block agents asked to have revisited; none of them
blocks the merge.

## Counts

| `ai_cost_basis` | Rows | Sum of `ai_cost_usd`, USD |
|---|---:|---:|
| reported | 394 | 3322.02 |
| list_price | 530 | 1643.02 |
| not_available | 486 | — |
| **Total** | **1410** | **4965.04** |

| `human_cost_basis` | Rows | Sum of `human_cost_usd`, USD |
|---|---:|---:|
| reported_payment | 111 | 1666.62 |
| reported_price | 0 | — |
| not_available | 1299 | — |
| **Total** | **1410** | **1666.62** |

`ai_cost_usd` spans $0.0000292 to $682.37, median $0.762. `human_cost_usd` takes only three distinct
values — $16.6162 on 100 epoch GPQA rows, $0.10 on 10 Cost-of-Pass BBQ rows, and $4.00 on one
other-m-z row. `ai_cost_date` spans 2023-11-06 to 2026-09-12.

## Per-block provenance

Each block covers a disjoint slice and the slices tile the Codex set exactly once. Routing was
verified against each row's `source_dataset`: no row sits in a block its `source_dataset`
contradicts.

| Block | Slice | Rows | reported | list_price | not_available | reported_payment | Sum ai_cost_usd, USD |
|---|---|---:|---:|---:|---:|---:|---:|
| gdpval | `source_dataset` names GDPval | 440 | 220 | 220 | 0 | 0 | 1611.59 |
| metr | `source_dataset` names METR | 399 | 111 | 0 | 288 | 0 | 1004.40 |
| epoch-costofpass | Epoch AI (293) or Cost-of-Pass (30) | 323 | 30 | 274 | 19 | 110 | 35.98 |
| other-a-l | remainder, `point_id` a–l | 108 | 2 | 20 | 86 | 0 | 163.51 |
| other-m-z | remainder, `point_id` m–z and digits | 139 | 31 | 16 | 92 | 1 | 2149.56 |
| merge fill | `robo-towel-pr2` | 1 | 0 | 0 | 1 | 0 | 0.00 |
| **Total** | | **1410** | **394** | **530** | **486** | **111** | **4965.04** |

The two `16x-clean-markdown-*` rows start with a digit and sit in other-m-z, consistent with that
block's stated "m–z and digits" scope. Dollar totals are dominated by four Vending-Bench 2 runs in
other-m-z ($2,135.54 of its $2,149.56) and by GDPval's 440 whole-task rows; the 323 epoch rows total
$35.98 because most are single questions.

## Format check and what was changed

Headers are byte-identical across all five blocks:
`point_id,ai_cost_usd,ai_cost_basis,ai_cost_date,human_cost_usd,human_cost_basis,evidence`.

Checked and already consistent, so nothing was changed:

| Property | Result |
|---|---|
| Line endings | CRLF in all five, no lone CR or LF; merged file written CRLF to match |
| Encoding | Pure ASCII, no BOM, in all five |
| Whitespace padding on any field | None in any block |
| Empty or missing `evidence` | None in any block |
| Embedded newlines in `evidence` | None in any block |
| Blank vs empty string | All blocks use empty string; no sentinel strings, no `NA`, no `null` |
| `ai_cost_date` format | `YYYY-MM-DD` on every non-blank value in all five |
| Field count per row | 7 on every row in all five |

**The one change applied.** Twelve `ai_cost_usd` values in `epoch-costofpass.csv` were written in
scientific notation while the other four blocks used plain decimal throughout. Each was converted to
plain decimal with the value asserted equal as an exact `Decimal` before and after, so no precision
was gained or lost:

| point_id | Before | After |
|---|---|---|
| extr-2digitadd-gpt4omini | 5.43639e-05 | 0.0000543639 |
| extr-2digitadd-llama31-8b | 4.1782e-05 | 0.000041782 |
| lang-bbq-llama31-8b | 5.23206e-05 | 0.0000523206 |
| reas-epoch-gpqa-gemini15flash8b | 8.08086e-05 | 0.0000808086 |
| reas-epoch-gpqa-ministral3b | 2.91972e-05 | 0.0000291972 |
| reas-epoch-gpqa-ministral8b | 7.7501e-05 | 0.000077501 |
| reas-epoch-gpqa-nemo | 9.91265e-05 | 0.0000991265 |
| reas-epoch-mathl5-llama3-8b | 9.96498e-05 | 0.0000996498 |
| reas-epoch-mathl5-ministral3b | 3.16851e-05 | 0.0000316851 |
| reas-epoch-mathl5-ministral8b | 7.55076e-05 | 0.0000755076 |
| reas-epoch-mathl5-mistralnemo | 9.88448e-05 | 0.0000988448 |
| reas-gsm8k-cop-llama31-8b | 7.40964e-05 | 0.0000740964 |

No other value in any column was altered. `evidence` cells are carried through verbatim.

## Coverage check against the Codex points.csv

| Check | Result |
|---|---|
| Codex `point_id` count | 1410 |
| Merged file rows | 1410 |
| Distinct `point_id` in merged file | 1410 |
| IDs in Codex but not in the merged file | 0 |
| IDs in the merged file but not in Codex | 0 |
| IDs appearing in more than one block | 0 |
| Sorted ascending by `point_id` | yes |

**One ID was missing from the block CSVs and is filled at merge.** The five blocks supplied 1,409
rows between them. `robo-towel-pr2` fell through the gap: its `source_dataset` is "PR2 geometric
towel folding ICRA 2010", so it belonged to the other-m-z slice, and neither "other" block picked it
up. It is filled `not_available` on both sides, which is the only defensible reading and matches the
other-m-z convention for never-API-served models verbatim:

- **AI side.** `model_id` is `pr2-geometric-towel-2010`, a 2010 Berkeley PR2 geometric folding
  policy. `research/cost/list-prices.csv` already carries it as provider `not_api_served` with the
  reason "task-specific or research model, never sold through a per-token API". The Codex row has
  `tokens = not_applicable` and `compute_evidence = derived_assumed_inputs`, so there is neither a
  dollar figure nor a token count to price.
- **Human side.** `human_time_evidence` is `assumed` and `human_time_method` is `estimated` — the
  20-minute figure is not from a human study, so no payment or price is reported anywhere.

The row's `evidence` cell opens "NOT COVERED BY ANY BLOCK CSV; filled at merge 2026-09-13" so the
fill is visible to anyone reading the CSV alone rather than only here.

## Value checks

Every check below runs over all 1,410 merged rows and passes with no exceptions.

| Check | Result |
|---|---|
| `ai_cost_basis` is one of `reported` / `list_price` / `not_available` | 1410/1410 |
| `human_cost_basis` is one of `reported_payment` / `reported_price` / `not_available` | 1410/1410 |
| `ai_cost_usd` present iff `ai_cost_basis` is not `not_available` | 924 present, 486 blank, 0 violations both directions |
| `ai_cost_date` present when `ai_cost_basis` is `list_price` | 530/530 |
| `ai_cost_date` blank when `ai_cost_basis` is `not_available` | 486/486 |
| `human_cost_usd` present iff `human_cost_basis` is not `not_available` | 111 present, 1299 blank, 0 violations |
| `ai_cost_date` parses as `YYYY-MM-DD` | 924/924 non-blank values |
| No negative or zero cost | 0 negatives, 0 zeros, in both cost columns |
| Nothing above $10,000 per row | 0 rows; the largest is `vending-bench-2-opus46` at $682.37 |
| `evidence` non-empty | 1410/1410 |

The four largest AI figures are the Vending-Bench 2 runs ($682.37, $558.60, $555.00, $339.57), all
`reported` from Andon Labs's own `mean_cost` over 5–6 multi-day runs, then
`agen-village-opus41-benefits-screener` at $107.43. All are plausible for their work units; none
needed a second look.

`ai_cost_date` was also checked against `research/cost/list-prices.csv` for every one of the 530
`list_price` rows: each date falls inside a price window whose rates are non-blank. Nine rows match
more than one window, all DeepSeek — the price table carries both a first-party and a Together row
for `deepseek-r1`, `deepseek-v3`, and `deepseek-v3-0324`, with overlapping validity. That is the
price table's provider dimension, not an error, and the epoch block resolved it to first-party rates
consistently (verified by recomputation: `reas-epoch-gpqa-r1` prices at DeepSeek's $0.55/$2.19 and
`reas-epoch-gpqa-v3` at the $0.14/$0.28 launch discount in force on 2025-01-27). The choice is
flagged below because the block itself raised it.

## Spot-check: 15 list_price rows recomputed

Each row was recomputed from the token counts in its `evidence` cell at the rates in
`research/cost/list-prices.csv` for its `ai_cost_date`, independently of the block's own arithmetic.
**All 15 reproduce the stored figure.**

| point_id | Block | Recomputed, USD | Stored, USD | Rel. diff |
|---|---|---:|---:|---:|
| work-gdpval-1b1ade2d-opus5 | gdpval | 6.5633872 | 6.5634 | -2.0e-06 |
| work-gdpval-a1963a68-opus5 | gdpval | 6.5633872 | 6.5634 | -2.0e-06 |
| reas-epoch-gpqa-nemo | epoch-costofpass | 0.000099126525 | 0.0000991265 | 2.5e-07 |
| reas-epoch-gpqa-sonnet35-1022 | epoch-costofpass | 0.0061179993 | 0.006118 | -1.1e-07 |
| reas-epoch-mathl5-qwen25-72b | epoch-costofpass | 0.00127045932 | 0.00127046 | -5.4e-07 |
| reas-epoch-mathl5-qwenplus25 | epoch-costofpass | 0.00114771032 | 0.00114771 | 2.8e-07 |
| reas-epoch-otis-gemini15pro2 | epoch-costofpass | 0.0043765835 | 0.00437658 | 8.0e-07 |
| reas-epoch-mathl5-mistral7b | epoch-costofpass | 0.000198590625 | 0.000198591 | -1.9e-06 |
| lang-epoch-simpleqa-gemini31pro | epoch-costofpass | 0.024086842 | 0.0240868 | 1.7e-06 |
| agen-village-web-sonnet45-first-deployment | other-a-l | 3.77819905 | 3.778199 | 1.3e-08 |
| cyber-lyptus-locktalk-gemini25pro | other-a-l | 0.16942225 | 0.169422 | 1.5e-06 |
| cyber-lyptus-back-to-past-gemini25pro | other-a-l | 0.294486 | 0.294486 | 0 |
| reas-strawberry-gpt5-chat | other-m-z | 0.00040075 | 0.000401 | -6.2e-04 |
| reas-strawberry-gpt-oss20b | other-m-z | 0.000041569 | 0.000042 | -1.0e-02 |
| reas-strawberry-opus41 | other-m-z | 0.010641 | 0.010641 | 0 |

All diffs except the last two are pure display rounding in the stored figure. The two exceptions are
six-decimal-place rounding biting values below $0.0005, discussed under residuals.

Three of the fifteen are worth spelling out because they exercise the harder rate rules.

**GDPval Opus 5** is the only four-rate row checked. Artificial Analysis reports input
1,443,328,948, cacheableInput 1,407,667,015, answer 12,091,348, reasoning 9,300,465, cacheHitRate
0.996663404781368, over 220 tasks. Splitting that gives 35,661,933 fresh input, 1,402,970,205 cache
reads, 4,696,810 cache writes, and 21,391,813 output. At `claude-opus-5-max` rates of
$5.00 / $0.50 / $6.25 / $25.00 per Mtok that is $1,443.95 total, $6.5634 per task. The cache-write
rate at 1.25x base input and the cache read priced on its own counter are both applied correctly.

**AI Village Sonnet 4.5** is the only row combining a main model, a controller, and a helper on a
different price sheet. Main ($3.20042 from 467,118 input, 303,687 cache creation, 1,479,446 cache
read, 14,427 output) plus controller ($0.51270 from 154,970 in / 3,186 out with no cache fields)
plus helper ($0.06508 from 52,064 blended GPT-5-Codex tokens at the GPT-5 input rate) sums to
$3.778199 exactly.

**Both Lyptus rows** reproduce to the cent and their token reconstructions match the Codex `tokens`
field exactly (70,335 and 147,460).

### Token reconciliation against the Codex rows

For 13 of the 15 the token decomposition in `evidence` sums to the Codex row's `tokens` field
exactly under that row's `tokens_accounting`. The two that do not are both explained, documented,
and correct:

| point_id | Evidence tokens | Codex `tokens` | Gap | Why |
|---|---:|---:|---:|---|
| work-gdpval-*-opus5 | 280684.368 | 290684.368 | 10000 | The Codex row's note says "Includes assumed 10 k helper positions". The allowance is an estimate with no dollar counterpart, and `COLUMNS.md` says `ai_cost_usd` is never estimated, so the cost excludes it. gdpval.md states it reproduces 280684.3683257959 deliberately. |
| agen-village-web-sonnet45-first-deployment | 785232 | 795787 | 10555 | The evidence cell names it: "estimated consolidation call and Sonnet's 10,000-token helper timeout allowance excluded". |

This is the general convention all five blocks adopted — price observed counters only, leave
reconstructed components out of the dollar figure, and name them in `evidence`. It means a handful
of rows have a cost that is a small understatement of the row's own compute basis rather than an
estimate. Sixteen epoch rows are affected more seriously; see flag 4.

### Wider automated sweep

Beyond the 15, two evidence formats are regular enough to parse and recompute in bulk:

| Pattern | Rows | Reproduce |
|---|---:|---|
| `Priced in X@a +out Y@b per M` (epoch output-length and Inspect-log rows) | 216 | 216/216 |
| `Priced A in + B out tokens at X/Y USD per Mtok` (other-m-z rows) | 12 | 12/12 |

So 243 of the 530 `list_price` rows have had their arithmetic reproduced from the stated tokens and
rates, with no failures.

## Residuals from the merge

1. **`robo-towel-pr2` was filled at merge, not by a block agent.** The values are forced by the
   price table and the Codex row, and the evidence cell is explicit about the provenance, but it is
   the one row in the file no block agent reviewed.
2. **The epoch block rounds `ai_cost_usd` to six decimal places, which is lossy below $0.0005.**
   `reas-strawberry-gpt-oss20b` recomputes to $0.000041569 and is stored as $0.000042 (1.0% high);
   `reas-strawberry-gpt5-chat` recomputes to $0.00040075 and is stored as $0.000401 (0.06% high).
   The other blocks store six significant figures instead and do not have this problem — the twelve
   scientific-notation values were the epoch block's cheapest rows carrying full precision, so the
   rounding is inconsistent within that block too. Nothing was changed: restoring precision means
   recomputing figures rather than reformatting them, which is a block edit, not a merge fix. The
   rows affected are the cheapest in the file and the absolute error is under $0.0000005 each.
3. **`cyber-lyptus-back-to-past-gemini25pro` has 429,721 cumulative prompt tokens** (139,023 fresh
   plus 290,698 cache reads) against Google's 200k long-context boundary for `gemini-2.5-pro`. That
   is a cumulative total across an agentic run's many turns, not a single prompt, so the standard
   tier the block used is almost certainly right; it would only be wrong if an individual call's
   prompt crossed 200k, which the released log would have to be re-read to rule out. The sibling
   Lyptus row is under the boundary even cumulatively. other-a-l.md asserts no call in any priced
   row exceeded a 200k prompt, so the block did check this — the note is here so the assertion is
   not lost.

## Consolidated flags from the block .md files

Everything the five block agents asked to have revisited, in one list. None of these blocks the
merge; each is a one-cell or one-rule change if Damon decides differently.

**Judgement calls a block agent explicitly asked to have a second opinion on**

1. **The 235 epoch output-length rows are `list_price` on a half-observed token count.** Epoch
   reports output tokens only; the input entering these costs is the Codex row's reconstruction of
   the question text plus an assumed wrapper, and the dataset's own evidence label for those rows is
   `derived_assumed_inputs`. Priced, the reconstructed input is a median 8.0% of the row's cost
   (quartiles 4.1% and 17.4%), so the call barely moves the numbers — but eleven rows sit above 40%,
   topping out at `reas-epoch-gpqa-gpt35-1106` at 57.9%. Flipping the rule leaves 39 `list_price`
   rows plus the 30 `reported` ones in that block. *(epoch-costofpass.md)*
2. **The two GPT-5.4 ARC rows ran six days before GPT-5.4's public price sheet**, so no rate was in
   force on the run date and they are `not_available`. The figures under the 2026-03-05 sheet are in
   each row's `evidence` cell — $0.249653 for `reas-arcagi-v1-gpt54-high` and $0.768960 for
   `reas-arcagi-v2-gpt54-high` — so flipping them to `list_price` at `ai_cost_date` 2026-03-05 is a
   one-cell edit if a post-hoc price beats a blank. *(other-m-z.md)*
3. **The 288 METR Inspect rows could be priced if a single rate were chosen for an undecomposed
   token total.** `generation_cost` is 0.0 on every Inspect-imported run — an importer gap, not a
   claim the runs were free — leaving only `tokens_count`, which Vivaria defines to include cache
   reads and writes. The four cost-bearing models show the assumption would not be harmless: their
   observed blended rates run 0.49x to 2.96x what the list input rate implies, and gpt-oss-120b's
   reported cost is 2.96x *below* the cheapest published rate for the model, so METR's counted
   tokens and METR's billed tokens are demonstrably different quantities. *(metr.md)*
4. **Sixteen epoch rows price observed counters while their compute includes an estimated
   missing-work allowance**, so cost and FLOPs are not on the same basis. Eleven are under 5%, but
   `reas-epoch-otis-gpt54xhigh` (563% allowance, cost covers 15% of the compute basis) and
   `reas-epoch-gpqa-gpt54xhigh` (220%, 31%) understate their own row's compute basis by 6.6x and
   3.2x. Their compute is dominated by a half-a-call allowance for sends that failed while reading
   response headers. The block left them filled and flagged rather than discarding a real observed
   figure. *(epoch-costofpass.md)*
5. **Three `not_available` other-m-z rows have a computed figure sitting unused in `evidence`** —
   Natural Plan $0.008371, the GPT-4 book name cloze $0.006279, the freelance news summaries
   $0.021192. All three release prompts and responses but no usage counters, so they are tokenizer
   reconstructions rather than observed counts, which the convention excludes. Three one-cell edits
   if the merge wants them. *(other-m-z.md)*

**Findings about `research/cost/list-prices.csv` that should be fixed at the source**

6. **The o1-mini corroboration in `list-prices.md` is not real.** That file cites Cost-of-Pass
   Table 4 as corroborating the inferred 2025-01-31 reprice to $1.10/$4.40, but the experiment's own
   retained records price o1-mini at $3.00/$12.00 while pricing o3-mini at $1.10/$4.40 in the same
   March 2025 runs. The likeliest reading is a stale hardcoded rate in their config, but either way
   the corroboration should come out of `list-prices.md`. Changes no row here: the Cost-of-Pass rows
   are `reported`, and the three Epoch o1-mini rows ran after the reprice. *(epoch-costofpass.md)*
7. **Together's DeepSeek-R1 split rate was in force by 2025-03-26, not 2025-06-01.**
   `list-prices.md` places the move from $7.00 flat to $3.00/$7.00 "between the 2025-02 and 2025-06
   captures" and dates the row 2025-06-01; the Cost-of-Pass records narrow it to on or before
   2025-03-26, so that row's `price_sheet_start` should move. *(epoch-costofpass.md)*
8. **Confirmed rather than contradicted, in the same pass:** GPT-4o at $5.00/$15.00 for the
   `gpt-4o-2024-05-13` snapshot, independently confirming `list-prices.md`'s "a dated snapshot is
   not the alias" warning against Cost-of-Pass Table 4's $2.50/$10.00; and o3's 2025-06-10 cut, so
   the three Epoch o3 rows starting 2025-04-16 take $10.00/$40.00 rather than the current
   $2.00/$8.00 — five times what the live sheet implies. *(epoch-costofpass.md)*

**Provider and rate choices made without a source naming the host**

9. **Nine DeepSeek output-length rows priced first-party with no surviving log.** Epoch's retained
   Inspect logs use first-party endpoints for DeepSeek, Z.ai, Moonshot, and Alibaba and reach for
   Together or Fireworks only for `gpt-oss-120b` and `kimi-k2p5`, so first-party was inferred.
   Together instead would raise `deepseek-r1` rows 3.2x, `deepseek-v3` rows 1.2–5.2x, and
   `deepseek-v3-0324` rows 1.2–1.3x. *(epoch-costofpass.md)*
10. **Sixty epoch rows priced at a Together or Fireworks rate no source names as the host** — open
    weights run through an unnamed endpoint. `list-prices.md` calls these rates "a convenience, not
    evidence about what any run cost". Two invert the usual direction:
    `lang-epoch-simpleqa-kimik25` ran on `fireworks/kimi-k2p5` per its log but is priced at
    Moonshot's first-party sheet, and the three `qwen3-235b-a22b-thinking-2507` rows ran on
    Alibaba's first-party endpoint but are priced at Fireworks — in both cases because that is the
    only priced row available. *(epoch-costofpass.md)*
11. **The ten Max Woolf strawberry rows are priced at first-party sheets although the runs went
    through OpenRouter**, whose routed upstream provider is not retained. The two gpt-oss rows use
    the Together serverless rate because no first-party gpt-oss sheet exists. *(other-m-z.md)*
12. **Andon Labs priced Vending-Bench 2's GPT-5.6 Sol at $5/$30 per Mtok, above the $4/$20 list
    sheet.** The reported figure is kept as stated, since `reported` means what the operator says it
    spent. `ai_cost_date` for all four Vending-Bench rows is the 2026-09-12 report snapshot because
    Andon gives no run dates. *(other-m-z.md)*

**Scope conventions that shape the column and could be read differently**

13. **Graders are excluded from cost on 23 epoch rows, and on two they cost more than the answer.**
    Epoch's SimpleQA and OTIS runs call a separate model to grade. Grading is a median 1.0% of the
    primary model's cost, but on `lang-epoch-simpleqa-dsv32` it is 115% and on
    `lang-epoch-simpleqa-haiku35` 61%, because the grading prompt is roughly 1,800 tokens against a
    33-token question. Adding graders is a one-line change if "helpers" in `COLUMNS.md` should
    include them. *(epoch-costofpass.md)*
14. **The AI Village Codex CLI helper reports a blended counter that cannot be decomposed**, priced
    at the GPT-5 input rate, which is a lower bound. Each affected `evidence` cell states the
    output-rate upper bound; the largest gap is $0.90 on an $11.67 row. *(other-a-l.md)*
15. **Standard tier throughout the epoch block** — no batch discount, no long-context surcharge, no
    off-peak discount. DeepSeek's 2025-02-26 to 2025-08-20 off-peak window would have cut two of the
    nine DeepSeek rows by 50% or 75% had the runs fallen in it; the peak rate is used, as
    `list-prices.md` specifies. *(epoch-costofpass.md)*
16. **Cache reads are priced everywhere even though the dataset's FLOP term drops them.** On the
    cache-heavy agent rows the reads are the largest single line — 7.1M read positions on the
    benefits screener, 6.6M on the Claude 3.7 site build. This is the intended asymmetry, recorded
    so the FLOP/cost divergence on those rows is not mistaken for an error. *(other-a-l.md)*
17. **Three epoch models have no cached-input rate on their third-party rows**, so cache reads are
    priced at the full input rate. The only affected row is `lang-epoch-simpleqa-kimik25` with
    23,169 cache reads out of 1.16M tokens — negligible. *(epoch-costofpass.md)*

**Human-cost exclusions worth knowing about, since 1,299 rows are `not_available`**

18. **Three large wage-derived figures were rejected by rule, not for lack of a source.** GDPval's
    $361 per task is explicitly hours times a BLS median wage; METR's `human_cost` is exactly
    `human_minutes` x 143.61 USD/h on all 65,637 runs in both exports; Better Call GPT's $74.26 per
    contract is stated in its own Section 4.2.3 as average time times an hourly rate. `COLUMNS.md`
    bars all three by name ("Never derived from time and a wage"). Together these account for most
    of the empty human column. *(gdpval.md, metr.md, other-a-l.md)*
19. **Eight paid human studies report a real payment that does not isolate to one task**, so they
    stay `not_available` with the figures recorded in `evidence`: Noy–Zhang ($10 base + up to $4
    bonus, two writing tasks per participant), H-ARC ($10 + $1 bonus over ~4.3 tasks), ARC-AGI-2
    human testing ($115–150 per 90-minute session + $5 per correct task), Simulating Human Memory
    ($20 for a one-hour session covering ten tasks), VCT ($5 per question + $25 bonus, but paid to
    the non-expert vetting cohort rather than the expert baseliners), GSM-Identity (£9/hour, an
    hourly wage the spec bars), SketchAgent ($0.50 per MTurk session, paid to the 2AFC judges rather
    than the QuickDraw drawers), and DeepSeek-Prover ($240 for ~12 hours, study-level). *(other-m-z.md)*
20. **The 111 `reported_payment` rows carry only three distinct values.** 100 epoch GPQA rows are
    at $16.6162, which is $10 base plus a $30 x 131/594 correct-rate bonus from the GPQA paper's
    non-expert validation, over the same 594 attempts whose mean duration is `human_time`.
    Superseded 2026-09-14: those rows now use the second expert validator, so `human_cost_usd` is
    $25.1313, the expert schedule's $10 base plus $10 x 161/198 plus the $7 flat post-revision
    bonus. See `epoch/gpqa.md`. The figures below record the backfill as it was submitted. Ten
    Cost-of-Pass BBQ rows are at $0.10, from the BBQ paper's $0.50 per five-example task. The single
    row outside the epoch block is `writing-news-summary-textdavinci002` at $4.00, from Zhang et al.
    §4.1's "we pay our writers $4 for every article they summarize".
    *(epoch-costofpass.md, other-m-z.md)*

**Structural notes on the 486 `not_available` AI rows**

21. **The bulk are structural, not research gaps.** Models never sold per token (CNNs, robots,
    classical OCR, research checkpoints), open weights the source self-hosted, rows whose token
    workload is a first-principles allowance rather than a counter, and rows whose tokens are a
    tokenizer reconstruction of released text. The METR Inspect importer gap (flag 3) is the largest
    single block at 288 rows. *(metr.md, other-a-l.md, other-m-z.md)*
22. **No per-task cost or token ledger exists for GDPval at any finer grain than per-model over all
    220 tasks**, confirmed against the HF gold-subset release, the paper, the AA page payload, and
    the AA Data API schema. The paper states outright that cost estimates could not be obtained for
    Claude, Gemini, or Grok, which is why the Opus rows take the AA route. Separately, the GDPval
    GPT-5 cost is **not independent of `compute_flops`** — the Codex note inverts the FLOP figure
    from this same dollar amount — and the two models' costs differ by 8.6x while their compute
    proxies differ by only 1.10x. *(gdpval.md)*

## Reproducing

The merge keys on `point_id` over the five block CSVs, applies the twelve scientific-notation
conversions listed above, adds the `robo-towel-pr2` fill, sorts ascending by `point_id`, and writes
CRLF. Every check in this file runs against `research/codex-cost-backfill.csv` as written, the Codex
`dataset/points.csv`, and `research/cost/list-prices.csv`.

Nothing under `../AI Compute vs Human Time/` or the snapshots folder was read for anything but
input, and nothing there was written. `DECISIONS.md`, `points.csv`, `excluded.csv`, and `COLUMNS.md`
in this folder were not touched. The five block CSVs and their `.md` notes are unmodified; the merge
writes only `research/codex-cost-backfill.csv` and this file.
