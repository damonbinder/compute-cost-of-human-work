# Cost backfill: Epoch AI and Cost-of-Pass blocks of the Codex dataset

*Created 2026-09-13 14:37.*

## TL;DR

All 323 rows in the Codex `points.csv` whose `source_dataset` names Epoch AI (293) or Cost-of-Pass
(30) are keyed in `epoch-costofpass.csv`: **30 `reported`, 274 `list_price`, 19 `not_available`** for
`ai_cost_usd`, and **110 `reported_payment`, 213 `not_available`** for `human_cost_usd`. **Epoch's
benchmarking hub publishes no dollar cost for any of the five benchmarks in scope**, contrary to the
brief's premise: the `benchmark_data.zip` download carries a cost column on many *external*
leaderboards but the five internal-run files (GPQA Diamond, MATH level 5, OTIS Mock AIME,
SWE-bench Verified, SimpleQA Verified) have thirteen columns and none of them is cost, and the
retained Inspect `.eval` headers carry no cost field either — so every Epoch row is priced at list.
Cost-of-Pass is the opposite case and better than expected: the retained per-record parquet files
carry `cost_per_prompt_token` and `cost_per_completion_token` alongside the token counts, so the
reported dollar figure is recoverable at full precision rather than at Table 6's one or two
significant figures. **That gave a clean 30-row test of `list-prices.csv`, which it passed 24/30
exactly and failed twice for reasons that are findings about the price table, not about the
backfill** (see "Cross-check" below). The one judgment call worth a second opinion is treating the
235 Epoch output-length rows as `list_price` when Epoch reports only the output token count and the
input is a reconstruction: the reconstructed input is a median 8% of each row's cost, so the call
barely moves the numbers, but it is a call.

Nothing outside this folder was written. The Codex dataset was read only.

## Counts by basis

| Task | Rows | reported | list_price | not_available |
|---|---|---|---|---|
| GPQA Diamond question | 100 | 0 | 91 | 9 |
| MATH Level 5 problem | 84 | 0 | 78 | 6 |
| OTIS Mock AIME problem | 71 | 0 | 67 | 4 |
| Resolve a SWE-bench Verified issue | 25 | 0 | 25 | 0 |
| SimpleQA-Verified factual lookup | 13 | 0 | 13 | 0 |
| Add two integers below 100 | 10 | 10 | 0 | 0 |
| Solve a grade-school arithmetic word problem | 10 | 10 | 0 | 0 |
| Answer a short social-context question | 10 | 10 | 0 | 0 |
| **Total** | **323** | **30** | **274** | **19** |

Human cost:

| Task | Rows | reported_payment | not_available |
|---|---|---|---|
| GPQA Diamond question | 100 | 100 | 0 |
| Answer a short social-context question | 10 | 10 | 0 |
| MATH Level 5 problem | 84 | 0 | 84 |
| OTIS Mock AIME problem | 71 | 0 | 71 |
| Resolve a SWE-bench Verified issue | 25 | 0 | 25 |
| SimpleQA-Verified factual lookup | 13 | 0 | 13 |
| Solve a grade-school arithmetic word problem | 10 | 0 | 10 |
| Add two integers below 100 | 10 | 0 | 10 |
| **Total** | **323** | **110** | **213** |

Resulting cost per work unit, in USD:

| Task | Rows priced | Minimum | Median | Maximum |
|---|---|---|---|---|
| Resolve a SWE-bench Verified issue | 25 | 0.0996 | 0.777 | 3.71 |
| OTIS Mock AIME problem | 67 | 0.000142 | 0.0089 | 0.653 |
| SimpleQA-Verified factual lookup | 13 | 0.000165 | 0.00607 | 0.0943 |
| Answer a short social-context question | 10 | 0.0000523 | 0.00264 | 0.0411 |
| GPQA Diamond question | 91 | 0.0000292 | 0.00254 | 0.385 |
| Solve a grade-school arithmetic word problem | 10 | 0.0000741 | 0.00292 | 0.0335 |
| Add two integers below 100 | 10 | 0.0000418 | 0.00145 | 0.019 |
| MATH Level 5 problem | 78 | 0.0000317 | 0.00133 | 0.25 |

The nineteen `not_available` rows are nine models with no published per-token price anywhere:
`gemma-2-9b-it`, `gemma-2-27b-it`, `gemma-3-27b-it` (three rows each), `phi-4` (three),
`gemini-2.0-pro-exp-02-05` (two), `phi-3-medium-128k-instruct` (two), `eurus-2-7b-prime`,
`qwen1.5-32b-chat`, and `qwen1.5-72b-chat` (one each). `list-prices.md` deliberately declines to
promote a third-party size-bucket rate into the price columns for these, and I did not promote one
either.

## Cross-check: reported cost against list-price reconstruction

Epoch publishes no cost, so the only reported dollar figures anywhere in scope are Cost-of-Pass's.
I ran the check on all 30 rather than a sample. Each row's reported figure is the mean over 1,024
attempts of the retained record's own `num_prompt_tokens x cost_per_prompt_token +
num_completion_tokens x cost_per_completion_token`; the reconstruction reprices the same mean token
counts at `list-prices.csv` rates for the run date (2025-03-24 to 2025-03-28).

Twenty-four of thirty agree to machine precision. The six that do not fall into exactly two groups.

| Group | Rows | reported / list-price | Cause |
|---|---|---|---|
| o1-mini | 3 | 2.727 | The harness recorded $3.00/$12.00; `list-prices.csv` has $1.10/$4.40 from 2025-01-31 |
| DeepSeek-R1 on Together | 3 | 0.831, 0.893, 0.899 | The harness recorded $3.00/$7.00; `list-prices.csv` has $7.00/$7.00 flat until 2025-05-31 |

Both are findings about `list-prices.csv`, and both contradict a specific claim in `list-prices.md`:

- **The o1-mini corroboration in `list-prices.md` is not real.** That file's "What is weakest here"
  section says the inferred 2025-01-31 reprice date is "corroborated by Cost-of-Pass Table 4 using
  $1.10/$4.40 for both". Table 4 does say that, but the experiment's own retained records price
  o1-mini at $3.00/$12.00 while pricing o3-mini at $1.10/$4.40 in the same March 2025 runs, and
  Table 6 is built from those records. So Cost-of-Pass supports the o3-mini tier and not the
  o1-mini alignment. The most likely reading is a stale hardcoded o1-mini rate in their config
  rather than evidence that o1-mini was still $3/$12 in March 2025, but either way the
  corroboration should come out of `list-prices.md`. This does not change any row here: the
  Cost-of-Pass rows are `reported`, and the three Epoch o1-mini rows ran 2025-02-13 and 2025-03-06,
  after the reprice, so they take $1.10/$4.40 whichever way the question is settled.
- **Together's DeepSeek-R1 split rate was already in force by 2025-03-26.** `list-prices.md` places
  the move from $7.00 flat to $3.00/$7.00 "between the 2025-02 and 2025-06 captures" and dates the
  row 2025-06-01. The Cost-of-Pass records narrow that to on or before 2025-03-26. This is a
  refinement of an acknowledged gap, not a contradiction, but the `price_sheet_start` on that row
  should move.

Two further checks in the same pass, both confirming `list-prices.csv` against the experiment's own
recorded rates:

- **GPT-4o at $5.00/$15.00.** Cost-of-Pass Table 4 lists GPT-4o at $2.50/$10.00, but the endpoint is
  the `gpt-4o-2024-05-13` snapshot and the records price it at $5.00/$15.00. `list-prices.md`'s
  warning that "a dated snapshot is not the alias" is confirmed by an independent run.
- **o3's 2025-06-10 cut.** The three Epoch o3 rows started 2025-04-16, so they take $10.00/$40.00
  rather than the current $2.00/$8.00 — five times the cost the live sheet implies. Handled.

## Method

### Epoch, Inspect-log rows (58)

SWE-bench Verified (25), SimpleQA-Verified (13), and the GPQA and OTIS runs Epoch published as
`.eval` logs (10 each). Per-sample usage was summed from the retained `summaries.json` under
`dataset/sources/epoch/<point_id>/`, not from `header.json`: for several SWE-bench runs the header
covers only the final execution segment (for `agen-epoch-swebench-gemini3pro`, 203 of 484 issues),
which the Codex `swebench.md` note also establishes. My summed counters reproduce the "Native
counters" and "Counters" lines in `research/epoch/swebench.md` and
`research/epoch/epoch-native-final.md` exactly wherever those notes state them.

Whether the `input_tokens` counter is gross (cache reads included) or net, and whether
`reasoning_tokens` is additional to `output_tokens` or already inside it, was determined per run from
the counter identity against `total_tokens` rather than assumed by provider. The four resolved
patterns match the table in `epoch-native-final.md`: `google/*` is `I + O + R`; `epoch/gemini-3.5-flash`
is `I + CR + O + R`; `openai/*` is `I + O`; other `epoch/*` and Anthropic are `I + CR + CW + O`.

Billing then follows the counters rather than the FLOP convention, since the cost column includes
cache reads where the FLOP term excludes them: uncached input at the input rate, cache reads at the
cached-input rate, Anthropic cache writes at the 5-minute write rate (1.25x base input, which is
Inspect's default TTL), and output plus any additional reasoning at the output rate. The per-run
total is divided by `results.completed_samples` from the header, which is the denominator every row's
own `tokens` value uses.

### Epoch, output-length rows (235)

GPQA Diamond, MATH level 5, and OTIS Mock AIME rows sourced from
`https://epoch.ai/data-insights/output-length`. Epoch reports "Output tokens per question" and
nothing about input. The row's own `tokens` value minus that reported output gives the input the
Codex row counted, which the notes describe as the benchmark question texts tokenized with the
model's own tokenizer plus an assumed chat wrapper of 12 positions (GPQA, OTIS) or 50 (MATH). All
235 rows join to the retained `agent-work/sources/epoch/scatter_data.csv` on `Identifier` and `Benchmark` with
no misses. Input is priced at the input rate and output at the output rate; Epoch's output figure
already includes reasoning, and every model in this block bills reasoning at the ordinary output
rate (the two `separate_thinking_rate` models in scope, `qwen-plus-2025-01-25` and
`qwen-turbo-2024-11-01`, are flagged `Reasoning model? = N` in the scatter file, so the non-thinking
rate applies).

Run dates come from the current Epoch benchmarking hub, which publishes `Started at` for every
internal run. All 235 rows join, and 229 of them match the scatter file's `Best score (across
scorers)` to full precision, which identifies the hub row as the same run. The six that do not
(`reas-epoch-otis-llama3-8b`, `reas-epoch-gpqa-sonnet37-64k`, `reas-epoch-gpqa-gemma3-27b`,
`reas-epoch-otis-gemma3-27b`, `reas-epoch-gpqa-grok3mini`, `reas-epoch-gpqa-llama31-8b`) have been
re-run on the hub since, so their original run date is unknown and `ai_cost_date` carries the
applicable price-sheet date instead; two of the six are `gemma-3-27b-it` and are `not_available`
anyway. Three further models (`gpt-4-0613`, `mistral-large-2402`) were run after the last retained
sheet that lists them, so those five rows also carry the price-sheet date.

### Cost-of-Pass (30)

Two-digit addition, GSM8K, and BBQ, ten models each. The brief says the Codex compute was inverted
from the paper's cost; **it was not**. `research/cost-of-pass/cost-of-pass.md` establishes compute
from `response.usage.prompt_tokens` and `completion_tokens` in the retained HuggingFace
`full_records` parquet, and none of the thirty rows' `notes` mentions a cost inversion. The cost is
still `reported`, for a better reason: those same parquet files carry `cost_per_prompt_token` and
`cost_per_completion_token` per record, so the paper's own cost function can be evaluated at full
precision instead of read off Table 6 at one or two significant figures. Every value here reproduces
its Table 6 entry within that table's rounding, including o1's coarse 0.02/0.03/0.04.

`ai_cost_date` is the record timestamp: 2025-03-24 to 2025-03-28, which also settles that the
o1-mini rate above was stale at the time of the run rather than current.

### Human cost

Filled only where the source states a payment for the row's own unit, and never derived from a
duration and a wage.

- **GPQA Diamond, 100 rows, $16.6162, `reported_payment`.** The GPQA paper's Appendix A.4 states the
  non-expert validation schedule: $10 base payment per question validated plus a $30 bonus for each
  question answered correctly. The retained `agent-work/sources/epoch/gpqa_diamond.csv` gives 131 of 594
  non-expert attempts correct on the Diamond set, and those are the same 594 attempts whose mean
  self-reported duration is the rows' `human_time` of 2,105.05 seconds, which I recomputed from the
  same file. Mean payment per attempt is therefore 10 + 30 x 131/594 = 16.6162. The paper's $95 per
  hour figure is a pipeline-wide average and is not used.
- **BBQ, 10 rows, $0.10, `reported_payment`.** Parrish et al. (2022), Section 4: "We pay annotators
  $0.50 per task, and each task includes 5 examples presented as multiple choice problems". The
  rows' human accuracy and timing are already transferred from that same validation population on a
  different 300-item BBQ sample, so the payment transfer rides on an assumption the rows already
  make.
- **GSM8K, `not_available`.** GSM-Identity pays £9 per hour. A per-question figure would be a
  duration times a wage.
- **Two-digit addition, `not_available`.** Ashkenazi and Najjar (2018) compensated participants with
  course credit or 30 NIS for the whole session, not per problem, and participants could take the
  credit instead.
- **MATH Level 5, OTIS, SWE-bench Verified, SimpleQA-Verified, `not_available`.** These baselines are
  assumed solvers, unpaid contest participation, or difficulty-bin estimates. OpenAI paid the
  SWE-bench Verified annotators, but for labelling, not for resolving an issue.

## What the numbers rest on, in order of how much it matters

1. **The reconstructed input on the 235 output-length rows.** Epoch reports output tokens only. The
   input entering these costs is the Codex row's reconstruction of the actual question texts plus an
   assumed wrapper, and the dataset's own evidence label for those rows is
   `derived_assumed_inputs`. Priced, the input is a median **8.0%** of the row's cost (quartiles 4.1%
   and 17.4%), because output dominates in both quantity and price. Eleven rows sit above 40%, all
   of them GPQA rows on early non-reasoning models with short answers — the extreme is
   `reas-epoch-gpqa-gpt35-1106` at 57.9%, then `hermes70b` 48.5%, `yi34b` 47.0%, `llama3-70b` 46.8%,
   `gpt35-0125` 45.3%, `qwen2-72b` 45.0%, `ds67b` 43.3%, `dbrx` 41.6%, `llama3-8b` 41.6%,
   `llama2-70b` 40.6%, `nemo` 40.6%. If you would rather these 235 rows read `not_available`
   because the source states only half the token count, that is one rule change and it leaves 39
   `list_price` rows plus the 30 `reported` ones.
2. **Sixteen rows where the row's compute includes an estimated missing-work allowance that the cost
   excludes.** `ai_cost_usd` prices observed counters only. For most of the sixteen the gap is under
   5%, but five are large enough that cost and FLOPs are no longer on the same basis:

   | point_id | Allowance, % of compute basis | Share of compute the cost covers, % |
   |---|---|---|
   | reas-epoch-otis-gpt54xhigh | 563 | 15 |
   | reas-epoch-gpqa-gpt54xhigh | 220 | 31 |
   | reas-epoch-otis-glm5 | 40 | 72 |
   | lang-epoch-simpleqa-gpt54xhigh | 28 | 78 |
   | lang-epoch-simpleqa-glm47 | 21 | 83 |
   | reas-epoch-otis-glm47 | 20 | 84 |
   | reas-epoch-gpqa-glm5 | 13 | 89 |
   | reas-epoch-gpqa-gemini31pro | 4.9 | 95 |
   | reas-epoch-otis-gemini31pro | 4.4 | 96 |
   | reas-epoch-gpqa-glm47 | 2.4 | 98 |
   | reas-epoch-otis-sonnet46-32k | 1.4 | 99 |
   | reas-epoch-otis-dsv32 | 0.84 | 99 |
   | reas-epoch-gpqa-dsv32 | 0.38 | 100 |
   | agen-epoch-swebench-dsv4promax | 0.31 | 100 |
   | lang-epoch-simpleqa-opus46-max | 0.10 | 100 |
   | lang-epoch-simpleqa-qwen3thinking | 0.10 | 100 |

   Each affected row's `evidence` states its allowance. The two GPT-5.4 rows are the ones to watch:
   their compute is dominated by a half-a-call allowance for sends that failed while reading
   response headers, so their cost understates the row's own compute basis by 3.2x and 6.6x. The
   alternative would be to mark those two `not_available`, which discards a real observed figure; I
   have left them filled and flagged.
3. **Provider for the nine DeepSeek output-length rows.** No log survives for them. Epoch's own
   retained Inspect logs use first-party endpoints for DeepSeek, Z.ai, Moonshot, and Alibaba
   (`deepseek/deepseek-reasoner`, `zhipu/glm-5`, `moonshot/kimi-k2.5`,
   `alibaba/qwen3-235b-a22b-thinking-2507`) and reach for `together/` or `fireworks/` only for
   `gpt-oss-120b` and `kimi-k2p5`, so I priced these first-party. Together instead would raise
   `deepseek-r1` rows 3.2x, `deepseek-v3` rows 1.2–5.2x, and `deepseek-v3-0324` rows 1.2–1.3x.
4. **Sixty rows priced at a Together or Fireworks rate that no source names as the host.** These are
   open-weight models Epoch ran through an unnamed endpoint. `list-prices.md` calls these rates "a
   convenience, not evidence about what any run cost", and the same caveat carries through here.
   Two of them invert the usual direction: `lang-epoch-simpleqa-kimik25` ran on
   `fireworks/kimi-k2p5` per its log but is priced at Moonshot's first-party sheet because that is
   the only priced row, and the three `qwen3-235b-a22b-thinking-2507` rows ran on Alibaba's
   first-party endpoint but are priced at Fireworks for the same reason.
5. **Graders are excluded, and on two rows they cost more than the answer.** Epoch's SimpleQA and
   OTIS runs call `google/gemini-2.0-flash-001` or `openai/gpt-5-nano-2025-08-07` to grade the
   answer. The Codex rows exclude those from compute as outcome evaluation outside the work unit,
   and `ai_cost_usd` excludes them too. Grading costs a median 1.0% of the primary model's cost
   across the 23 affected rows, but on `lang-epoch-simpleqa-dsv32` it is 115% of the answer's cost
   and on `lang-epoch-simpleqa-haiku35` 61%, because the grading prompt is roughly 1,800 tokens
   against a 33-token question. Adding graders is a one-line change if the reading of "helpers" in
   `COLUMNS.md` should include them.
6. **Standard tier throughout: no batch discount, no long-context surcharge, no off-peak
   discount.** Epoch's Inspect logs are ordinary synchronous calls, so batch does not apply. Google
   and xAI tier at a 200k prompt, which only the SWE-bench agent rows could reach; the largest
   per-call mean prompt across the four heaviest runs is 94k tokens
   (`agen-epoch-swebench-gemini31pro-ct`), so a handful of late calls on the biggest issues might
   cross the boundary and nothing systematic does. DeepSeek's 2025-02-26 to 2025-08-20 off-peak
   window would have cut two of the nine DeepSeek rows by 50% or 75% had the runs fallen in it; the
   peak rate is used, as `list-prices.md` specifies.
7. **`gpt-oss-120b` and `qwen3-235b-a22b-thinking-2507` have no cached-input rate on their
   third-party rows, and neither does `fireworks/kimi-k2p5`.** Where a run records cache reads and
   the sheet publishes no cached rate, those reads are priced at the full input rate. The only
   affected row is `lang-epoch-simpleqa-kimik25` with 23,169 cache reads out of 1.16M tokens, so the
   effect is negligible.

## Reproducing

Everything is derived from files retained in the two folders, with one live download.

- Codex rows and token counts: `../AI Compute vs Human Time/dataset/points.csv`.
- Epoch per-run usage: `dataset/sources/epoch/<point_id>/summaries.json` and `header.json`.
- Epoch output-length figures: `dataset/sources/epoch/scatter_data.csv`, joined on `Identifier` and
  `Benchmark`.
- Epoch run dates: `https://epoch.ai/data/benchmark_data.zip`, files `gpqa_diamond.csv`,
  `math_level_5.csv`, `otis_mock_aime_2024_2025.csv`, `swe_bench_verified.csv`,
  `simpleqa_verified.csv`, column `Started at`; retrieved 2026-09-13. These are also the files that
  establish the hub publishes no cost for the internal runs.
- Cost-of-Pass costs and dates: `dataset/sources/cost-of-pass/runs/<task>/<endpoint>/full_records/dataset.parquet`,
  columns `num_prompt_tokens`, `num_completion_tokens`, `cost_per_prompt_token`,
  `cost_per_completion_token`, `timestamp`. Table 6 for the cross-check is in
  `dataset/sources/cost-of-pass/paper.txt`.
- Human payments: `dataset/sources/epoch/gpqa-paper.html` Appendix A.4 and
  `dataset/sources/epoch/gpqa_diamond.csv`; `dataset/sources/cost-of-pass/bbq-original.txt`
  Section 4; `dataset/sources/cost-of-pass/gsm-identity.txt` Section 6;
  `dataset/sources/cost-of-pass/addition-original-extract.txt`.
- Prices: `research/cost/list-prices.csv`, selected by `price_sheet_start <= ai_cost_date <=
  price_sheet_end`.

The brief restricted writing to this folder, so the build script is not retained. Every quantity
above is reproducible from the locators in each row's `evidence` field plus the rules in the Method
section.
