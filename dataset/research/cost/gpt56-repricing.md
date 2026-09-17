# GPT-5.6 repricing — corrected price windows and the rows they touch

*Created 2026-09-13 18:07.*

## TL;DR

The GPT-5.6 family repriced twice in its first six weeks and `list-prices.csv` carried only the
final rate, undated. All three models launched 2026-07-09 at **$5.00/$0.50/$30.00 (Sol),
$2.50/$0.25/$15.00 (Terra), $1.00/$0.10/$6.00 (Luna)**; on **2026-07-30** OpenAI cut Terra 20% and
Luna 80% permanently; on **2026-08-21** it cut Sol to $4.00/$0.40/$20.00 under a promotion the
pricing page marks "available at least through November 21, 2026". Wayback captures of
`developers.openai.com/api/docs/pricing` bracket both changes to within a day. `list-prices.csv` now
carries six dated windows for the family instead of three open ones, and `build_list_prices.py`
regenerates it. **Sol is the only promotional rate anywhere in the table**; no other model in
`list-prices.csv` has a promotional rate recorded as if it were the only rate.

**Zero `list_price` rows have an `ai_cost_date` inside a window whose rate changed** — the literal
scan the brief asked for comes back empty across `points.csv`, `excluded.csv`, all 26
`candidates/*/points.csv`, `claude-rows-backfill.csv` and `codex-cost-backfill.csv` (1,025
`list_price` rows in total). But **three ALE-Bench candidate rows are wrong for a different reason**:
they are `list_price` at `ai_cost_date` 2026-09-08, and the dollars they carry were computed by the
ALE-Bench harness at the **launch** rates, which that date no longer selects. Their recomputed values
are in the table below. Two more rows (the apex-agents Terra and Luna rows, in `excluded.csv` and
`claude-rows-backfill.csv`) keep their dollar figures unchanged but name a window ID that no longer
exists and need a label edit only.

**Next action for the coordinator:** apply the three ALE-Bench recomputations, or relabel those rows
`reported` — the choice is argued under "Which repair" below. Then fix four `price_rows_used` strings.
`research/terminal-bench.md` and `research/ale-bench.md` both carry a paragraph saying
`list-prices.csv` is right and the harnesses are wrong; both now have it backwards and want an
amendment.

## What the primary sources say

### The pricing page, capture by capture

OpenAI's pricing page renders its tables client-side and the Wayback records are gzipped, so a plain
`curl` of an archived URL returns an SPA shell with no numbers in it. The captures below were taken
with `curl -sSL https://web.archive.org/web/<TS>id_/https://developers.openai.com/api/docs/pricing`
piped through `gunzip -c`; three are retained under `agent-work/sources/cost/wayback/` and listed in
`agent-work/sources/cost/PROVENANCE.md`.

Standard tier, USD per million tokens, as input / cached input / cache write / output.

| Capture (UTC) | Sol | Terra | Luna | Promo sentence |
|---|---|---|---|---|
| 2026-07-09 17:50 | 5.00 / 0.50 / 6.25 / 30.00 | 2.50 / 0.25 / 3.125 / 15.00 | 1.00 / 0.10 / 1.25 / 6.00 | absent |
| 2026-07-14 17:25 | 5.00 / 0.50 / 6.25 / 30.00 | 2.50 / 0.25 / 3.125 / 15.00 | 1.00 / 0.10 / 1.25 / 6.00 | absent |
| 2026-07-29 10:31 | 5.00 / 0.50 / 6.25 / 30.00 | 2.50 / 0.25 / 3.125 / 15.00 | 1.00 / 0.10 / 1.25 / 6.00 | absent |
| 2026-07-30 19:51 | 5.00 / 0.50 / 6.25 / 30.00 | 2.00 / 0.20 / 2.50 / 12.00 | 0.20 / 0.02 / 0.25 / 1.20 | absent |
| 2026-07-31 10:44 | 5.00 / 0.50 / 6.25 / 30.00 | 2.00 / 0.20 / 2.50 / 12.00 | 0.20 / 0.02 / 0.25 / 1.20 | absent |
| 2026-08-20 10:30 | 5.00 / 0.50 / 6.25 / 30.00 | 2.00 / 0.20 / 2.50 / 12.00 | 0.20 / 0.02 / 0.25 / 1.20 | absent |
| 2026-08-21 10:30 | 5.00 / 0.50 / 6.25 / 30.00 | 2.00 / 0.20 / 2.50 / 12.00 | 0.20 / 0.02 / 0.25 / 1.20 | absent |
| 2026-08-22 10:30 | 4.00 / 0.40 / 5.00 / 20.00 | 2.00 / 0.20 / 2.50 / 12.00 | 0.20 / 0.02 / 0.25 / 1.20 | present |
| 2026-08-24 09:39 | 4.00 / 0.40 / 5.00 / 20.00 | 2.00 / 0.20 / 2.50 / 12.00 | 0.20 / 0.02 / 0.25 / 1.20 | present |
| live 2026-09-13 | 4.00 / 0.40 / 5.00 / 20.00 | 2.00 / 0.20 / 2.50 / 12.00 | 0.20 / 0.02 / 0.25 / 1.20 | present |

The promo sentence, verbatim from the 2026-08-22 capture and unchanged on the live page:

> GPT-5.6 Sol's promotional pricing is available at least through November 21, 2026.

It sits under the Sol row and is attached to Sol alone. Scanning the whole 2026-08-24 capture for
"promotional", "promotion", "limited time", "introductory", "temporary", "free until" and "free
through" returns that one sentence plus a navigation item and an unrelated fine-tuning note.

### Dating the two changes

**Terra and Luna, 2026-07-30.** The page still shows the launch rates at 10:31 UTC on 2026-07-29 and
shows the cut rates at 19:51 UTC on 2026-07-30, so the change lands on 2026-07-30. The trade press
dates the announcement to that day and gives the same numbers: Terra to $2/$12, Luna to 20 cents/$1.20,
"reducing the price of Terra by 20% and the cost of Luna by 80%", with Sol unchanged
([CNBC, 2026-07-30](https://www.cnbc.com/2026/07/30/open-ai-price-cut-gpt.html);
[Axios, 2026-07-30](https://www.axios.com/2026/07/30/openai-cuts-prices-gpt-terra-luna5)). Nothing in
the page or the coverage conditions these cuts on a date, so they are recorded as permanent.

**Sol, 2026-08-21.** The page still shows $5/$30 at 10:30 UTC on 2026-08-21 and shows $4/$20 with the
promo sentence at 10:30 UTC on 2026-08-22, so the change lands on one of those two days. The date is
taken as **2026-08-21** on two grounds: the coverage puts the announcement there
([Enterprise DNA](https://enterprisedna.co/resources/news/openai-gpt-56-sol-price-cut-20-percent-frontier-model-august-2026/),
[Startup Fortune](https://startupfortune.com/openai-cuts-gpt-56-sol-api-prices-after-holding-the-line-for-months/)),
and "at least through November 21, 2026" is exactly three months from 2026-08-21, which fixes the
promotion's start as surely as its end.

**The one soft edge.** The 2026-08-21 10:30 UTC capture is 03:30 Pacific, before OpenAI's business
day, so it does not contradict a same-day announcement — but it does mean a workload run early on
2026-08-21 may have billed at $5.00/$0.50/$30.00 rather than the promotional rate the window assigns
it. No row in either batch carries `ai_cost_date` 2026-08-21, so nothing turns on this today.

### The two harness price tables

Both harnesses that ship their own price table bill the whole family at the **launch** rates, which
is the independent confirmation that those rates were real.

- **ALE-Bench**, `src/ale_bench_eval/calc_cost.py` in `SakanaAI/ALE-Bench`: Sol 5 / 0.5 / 6.25 / 30,
  Terra 2.5 / 0.25 / 3.125 / 15, Luna 1 / 0.1 / 1.25 / 6, each with a 272k long-context tier at 2x
  (Sol output 45, Terra 22.5, Luna 9). These match the 2026-07-09 capture exactly, including the
  cache-write column.
- **Andon Labs Vending-Bench 2**, as recorded in `research/codex-cost-backfill.csv`: "Andon priced
  GPT-5.6 Sol at 5/30 per Mtok, above the 4/20 list sheet."
- **Terminal-Bench 2.1**'s official leaderboard submissions reproduce to the cent at 5.00/0.50/30.00,
  2.50/0.25/15.00 and 1.00/0.10/6.00, per `research/terminal-bench.md`. Those runs are dated
  2026-07-10 and 2026-07-11, inside the launch window, so the board and the corrected sheet now agree.

ALE-Bench's table is not a snapshot of any one day, though: it prices Gemini 3.8 / 3.7 / 3.6 Flash at
$1.50/$7.50, which is the **post-promotional** rate those models do not reach until 2027-01-01. Treat
it as a hand-maintained table, not as evidence of what was in force on a run date.

## The corrected windows

Six rows in `list-prices.csv` where there were three. `price_sheet_end` is the last day the sheet
applied, inclusive, per the file's own convention.

| model_id | start | end | input | cached | output | source |
|---|---|---|---|---|---|---|
| gpt-5-6-sol | 2026-07-09 | 2026-08-20 | 5.00 | 0.50 | 30.00 | wayback 20260821103049 |
| gpt-5-6-sol | 2026-08-21 | — | 4.00 | 0.40 | 20.00 | live page |
| gpt-5-6-terra | 2026-07-09 | 2026-07-29 | 2.50 | 0.25 | 15.00 | wayback 20260729103109 |
| gpt-5-6-terra | 2026-07-30 | — | 2.00 | 0.20 | 12.00 | live page |
| gpt-5-6-luna | 2026-07-09 | 2026-07-29 | 1.00 | 0.10 | 6.00 | wayback 20260729103109 |
| gpt-5-6-luna | 2026-07-30 | — | 0.20 | 0.02 | 1.20 | live page |

Ratios a backfill needs: pricing a launch-window workload off the current sheet is **1.25x low on
Sol input, 1.5x low on Sol output, 1.25x low on Terra across the board, and 5x low on Luna across the
board**. Only Terra (0.8x) and Luna (0.2x) scale uniformly; a Sol cost cannot be rescaled without the
token split.

`cache_write_usd_per_m` stays blank on all six, as on every other OpenAI row, even though the page
publishes a cache-write rate of 1.25x base input for this family. No row in either registry separates
cache creation from fresh input on an OpenAI model, so filling the column would change nothing and
would break the column's meaning elsewhere in the table. It is flagged in `list-prices.md` instead.

## Other models with the same problem

**None.** Three checks:

1. **OpenAI's current page carries exactly one promotional rate**, Sol's, established by the
   full-text scan above.
2. **No other OpenAI model in the table repriced during 2026.** Captures at 2026-03-23, 2026-05-05,
   2026-06-19, 2026-07-09 and 2026-08-24 show GPT-5.5 flat at 5.00/0.50/30.00, GPT-5.4 at
   2.50/0.25/15.00, GPT-5.4-mini at 0.75/0.075/4.50, GPT-5.4-nano at 0.20/0.02/1.25 and GPT-5.3-Codex
   at 1.75/0.175/14.00, each matching its single window in `list-prices.csv`. GPT-6 Astra first
   appears at 10.00/1.00/50.00 and has not moved since.
3. **The one other promotional rate found anywhere in the retained price sheets is Google's**, on
   Gemini 3.8 / 3.7 / 3.6 Flash: $0.75/$3.75 promotional through 2026-12-31, doubling to $1.50/$7.50
   on 2027-01-01 (`agent-work/sources/cost/live/google-gemini-pricing-2026-09-13.md`). **None of the three is in
   `list-prices.csv`**, because none appears in either registry — so no row can be priced off them.
   If one is ever added, note that the promotion runs from launch, so its single window would be
   correct for every past date and would only need splitting once 2027-01-01 arrives. The direction is
   the opposite of Sol's: the current rate is the low one and the future rate is the high one.

Anthropic's Sonnet 5 looks superficially similar — "the $2/$10 launch price is now the standard
price. The previously scheduled increase to $3/$15 will not occur" — but that is a scheduled increase
cancelled, so one window is right. Sonnet 5 has no row in `list-prices.csv` either.

## Affected rows

### Category 1 — `list_price` rows whose `ai_cost_date` falls in a changed window

**None.** Every `list_price` row in `points.csv` (175), `excluded.csv` (45), the 26
`candidates/*/points.csv` (112), `research/cost/claude-rows-backfill.csv` (163) and
`research/codex-cost-backfill.csv` (530) was resolved against the corrected window table; 1,025 rows
in total, every one landing inside exactly one window, and none of the GPT-5.6 ones landing in a
window that changed. `points.csv` contains no GPT-5.6 row at all.

### Category 2 — `list_price` rows priced at rates their own date does not select

Three rows, all in `candidates/ale-bench/points.csv`. Their cost is `15 x` the ALE-Bench
leaderboard's published dollar figure, which the harness computed at the launch rates; their
`ai_cost_date` is 2026-09-08, the leaderboard version date, at which the corrected sheet gives the
cut rates. The recomputation below holds the token counts and the implied cache split fixed and
reprices at the 2026-09-08 sheet.

| point_id | model | short-subset input / output | implied cache reads | old `ai_cost_usd` | new `ai_cost_usd` | ratio |
|---|---|---|---|---|---|---|
| agen-alebench-short-sol56max | gpt-5-6-sol | 6978 / 49052 | 2011 | 22.4610097826087 | 15.025688 | 0.668968 |
| agen-alebench-short-terra56max | gpt-5-6-terra | 2403 / 80168 | 1898 | 18.06386804347826 | 14.451094 | 0.800000 |
| agen-alebench-short-luna56max | gpt-5-6-luna | 31544 / 52714 | 1255 | 5.200478282608696 | 1.040096 | 0.200000 |

Cache reads are inverted from the gap between the gross-input price and the published cost, the same
inversion `research/ale-bench.md` describes. At the launch rates it yields 28.8%, 79.0% and 4.0% of
gross input respectively — all positive and all plausible. At the rates `list-prices.csv` used to
carry, the same inversion returns a **negative** count, which is what put
`price_sheet_below_billed_rate` on these three rows and forced their cache-read scenario to zero
reads. Correcting the sheet dissolves that flag: the scenario for these three can now be computed the
ordinary way, and `research/ale-bench.md`'s open question 6 ("a price-sheet discrepancy worth checking
independently") is answered — the harness was right and the sheet was wrong.

### Category 3 — rows whose dollars are unchanged but whose window label is stale

Two rows, each appearing in two files, so four `price_rows_used` strings.

| point_id | model | files | `price_rows_used` now says | should say |
|---|---|---|---|---|
| work-apex-agents-gpt56terra | gpt-5-6-terra | `excluded.csv`, `research/cost/claude-rows-backfill.csv` | `gpt-5-6-terra / openai / 2026-07-09..open` | `gpt-5-6-terra / openai / 2026-07-30..open` |
| work-apex-agents-gpt56luna | gpt-5-6-luna | `excluded.csv`, `research/cost/claude-rows-backfill.csv` | `gpt-5-6-luna / openai / 2026-07-09..open` | `gpt-5-6-luna / openai / 2026-07-30..open` |

Both are dated 2026-09-13 and were priced at the current rates, which the corrected table still gives
for that date. `$2.12637` and `$0.242495` both reproduce exactly. Only the window ID moves.

Worth recording against them, though: their derivation says "Run date not published; priced at the
retrieval-date sheet", which `COLUMNS.md` permits. That choice now carries more weight than it did.
Artificial Analysis published apex-agents results for models that launched 2026-07-09, so the runs
could sit anywhere in 2026-07-09 to 2026-09-13. If they predate 2026-07-30, Terra's cost is 1.25x
higher and Luna's is 5x higher than what the rows carry. This is a sensitivity, not a correction —
the rows follow the spec — but it is the single largest unpriced uncertainty the repricing creates.

### Rows checked and unaffected

- `candidates/terminal-bench/points.csv`, three rows (`agen-tbench21-gpt56sol-codex`,
  `-terra-codex`, `-luna-codex`), `ai_cost_basis = reported`, dates 2026-07-10 and 2026-07-11. The
  dollars come from the leaderboard, not the sheet. They were already right and the corrected sheet
  now agrees with them.
- `research/codex-cost-backfill.csv`, `vending-bench-2-gpt56sol`, `reported`, 2026-09-12. Andon's own
  figure; not sheet-derived.
- `candidates/apex-agents/points.csv`, two GPT-5.6 rows with blank cost columns; the costed versions
  are the Category 3 rows above.
- `candidates/ale-bench/points.csv`, `agen-alebench-short-dsr10528` and `-o3high`, and every other
  `list_price` row on a multi-window model across all files. All resolve to the window their cost was
  computed at.

## Which repair for the ALE-Bench three

Two internally consistent options, and the choice is the coordinator's.

**Reprice at 2026-09-08 (the numbers above).** Keeps `ai_cost_basis = list_price` and `ai_cost_date`
as the leaderboard version date, which is what `COLUMNS.md` prescribes when the run date is unknown,
and makes the row mean what the column says it means: these token counts at the rates in force on
that date. The cost then stops matching the leaderboard's own published dollar figure, which is a
cost worth naming in the row's notes.

**Relabel `reported`.** The figure is, literally, the leaderboard's published cost scaled by the
documented 15x protocol factor — the same status the Terminal-Bench rows have. This keeps the dollars
and drops the date problem, but `reported` in `COLUMNS.md` means "the operator or paper states the
dollar amount spent", and Sakana's leaderboard states a computed list-price figure rather than a bill,
so the label would be a stretch.

I lean to repricing. It is the option the column definitions actually support, the three ratios are
exact for Terra and Luna, and the Sol figure rests on a cache inversion that the corrected rates have
now made well-behaved. The stronger argument for the alternative is that moving `ai_cost_date` back
into the launch window — where the harness's rates were correct — would also fix the rows, but the
ALE-Bench runs have no published date and the harness's Gemini rows show its table is not
contemporaneous, so there is nothing to anchor such a date on.

## Notes elsewhere that now want an amendment

I did not edit these; they belong to other constructors.

- `research/terminal-bench.md`, the paragraph beginning "A price discrepancy worth recording", says
  "That table is right against OpenAI's page today". The observation was correct and the inference
  from it was the right one — the July runs do predate the Sol promotion — but the conclusion that
  `list-prices.csv` was right is now the wrong way round for Terra and Luna, whose 2026-07-30 cut is
  not a promotion at all.
- `research/ale-bench.md`, the cache-reads paragraph and open question 6, which describe
  `list-prices.csv` as disagreeing with the harness "for five configurations, where it implies a
  negative cache count". Three of those five are the GPT-5.6 rows and are now resolved in the
  harness's favour. The other two flagged configurations are Anthropic-path rows where the gap is
  exactly zero, a different phenomenon that this correction does not touch.
- `agent-work/sources/cost/live/openai-pricing-2026-09-13.md` omitted the promotional sentence at first
  retrieval. I added it, with a dated marginal note, since the file is a verbatim-extract record.

## Reproducing

```
python3 research/cost/build_list_prices.py \
    "../AI Compute vs Human Time/dataset/models.csv" \
    models.csv \
    research/cost/list-prices.csv
```

`build_list_prices.py` now regenerates `list-prices.csv` byte for byte, which it did not before this
pass: two earlier hand-edits to the CSV had never been folded back into the script, so any
regeneration would have silently reverted them. Both are now in the script — `deepseek-r1` on Together
splitting at 2025-03-26 rather than 2025-06-01 (documented in `list-prices.md`, and correct: R1-0528
did not exist before 2025-05-28, so only the `deepseek-r1` rows move), and `claude-opus-4-1` starting
2025-08-05 at its own release date rather than sharing Opus 4's 2025-05-22. Neither changes a price.
