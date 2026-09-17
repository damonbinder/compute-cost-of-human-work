# Cost-column backfill for the Claude-authored rows

*Created 2026-09-13 14:30.*

## TL;DR

All 239 rows of `points.csv` (144) and `excluded.csv` (95) now carry the five cost columns. **163 are `list_price`, 58 are `reported`, and 18 are `not_available`.** Observed AI cost runs from $0.006 for one GPT-4.1 chess move to $429,910 for the Meta textbook formalization. **The human side is almost empty: only the five Remote Labor Index rows carry a human cost**, $632.60, the paper's printed mean freelance project price; every other source reports a human duration and no payment or price at all. The machine-readable copy is `claude-rows-backfill.csv` in this directory, one row per point with the price-table row and derivation used.

Three things worth knowing before using the column.

1. **Two rows have a cost column that is not independent of their compute column.** The Factorio row's compute is inverted from the operator's "$4500", and the five Remote Labor Index rows' compute is inverted from the $2.34 mean. A cost-per-FLOP statistic built on those rows measures the price sheet, nothing else.
2. **The nine APEX-Agents rows are upper bounds.** Artificial Analysis publishes no cache split for this benchmark, so the whole input counter is priced at the gross input rate even though seven of the nine providers cache by default. Pricing the unobserved cached share would have meant estimating it.
3. **The seven VideoGameBench Llama 4 Maverick figures came out of a lookup bug** in the harness, at $0.10/$0.20 per million against Together's $0.27/$0.85. They are the operator's published accounting, so they stay `reported`, but they are about a third of what the endpoint would have charged.

## Counts by basis

| Basis | points.csv | excluded.csv | Total |
|---|---|---|---|
| `reported` | 16 | 42 | 58 |
| `list_price` | 118 | 45 | 163 |
| `not_available` | 10 | 8 | 18 |
| **Total** | **144** | **95** | **239** |

| Human basis | points.csv | excluded.csv | Total |
|---|---|---|---|
| `reported_payment` | 0 | 0 | 0 |
| `reported_price` | 0 | 5 | 5 |
| `not_available` | 144 | 90 | 234 |
| **Total** | **144** | **95** | **239** |

## By study

| Study | Rows | `reported` | `list_price` | `not_available` | Lowest AI cost, USD | Highest AI cost, USD | Research note |
|---|---|---|---|---|---|---|---|
| Epoch AI SWE-bench Verified bins | 124 | 0 | 124 | 0 | 0.0776673 | 5.3586 | `research/epoch-swebench-bins.md` |
| BALROG Crafter | 26 | 0 | 16 | 10 | 0.0956637 | 4.32295 | `research/balrog.md` |
| Kaggle Game Arena chess | 9 | 9 | 0 | 0 | 0.006 | 0.335 | `research/game-arena.md` |
| MirrorCode | 13 | 0 | 13 | 0 | 11.1908 | 576.663 | `research/mirrorcode.md` |
| LUMEN | 5 | 5 | 0 | 0 | 19.51 | 29.04 | `research/lumen.md` |
| APEX-Agents | 9 | 0 | 9 | 0 | 0.19678 | 4.25599 | `research/apex-agents.md` |
| VideoGameBench | 35 | 35 | 0 | 0 | 0.01 | 30 | `research/videogamebench.md` |
| Remote Labor Index | 5 | 5 | 0 | 0 | 2.34 | 2.34 | `research/remote-labor-index.md` |
| HourVideo | 2 | 2 | 0 | 0 | 33.84 | 104.84 | `research/hourvideo.md` |
| Portal (GPT-6 Astra) | 1 | 1 | 0 | 0 | 571.33 | 571.33 | `research/portal-astra.md` |
| Factorio (GPT-6 Astra) | 1 | 1 | 0 | 0 | 4500 | 4500 | `research/factorio-astra.md` |
| Meta textbook formalization | 1 | 0 | 1 | 0 | 429910 | 429910 | `research/meta-textbook.md` |
| SRT-H | 4 | 0 | 0 | 4 | — | — | `research/srt-h.md` |
| LAIT | 1 | 0 | 0 | 1 | — | — | `research/lait.md` |
| OpenAI Navier-Stokes | 1 | 0 | 0 | 1 | — | — | `research/navier-stokes-openai.md` |
| Anthropic FLT | 1 | 0 | 0 | 1 | — | — | `research/flt-anthropic.md` |
| MonoRace | 1 | 0 | 0 | 1 | — | — | `research/monorace.md` |

## Method, per study

### Epoch AI SWE-bench Verified bins (124 rows)

`list_price`. Every instance's `model_usage` counters are in `agent-work/sources/epoch-swebench-bins/epoch-swebench-perinstance.csv`. For each of the 124 bins I sum `input_tokens`, `output_tokens`, `cache_read_tokens`, `cache_write_tokens` and `reasoning_tokens` over the bin's instances, decompose them into billed categories with the same endpoint-family rule table `research/epoch-swebench-bins.md` uses for the counted workload, price each category at the list rate in force on the run's `Started at` date, and divide by the bin's completed evaluations, matching `compute_statistic = total_per_completed_sample`. Where the source total is `I + O` or `I + O + R` the input counter is gross and the cache read is subtracted out of it before pricing; where the total is additive the input counter is already fresh. Cache reads, which the FLOP term excludes, are priced here at the cached-input rate. Cache writes are zero everywhere except the Anthropic endpoints and `epoch/qwen3.7-max`, both of which have a published write rate. *Correction (coordinator, 2026-09-13): OpenAI bills cache writes at 1.25× input on GPT-5.6 and later (from 2026-07-09); no harness behind these rows records written tokens, so the two APEX GPT-5.6 rows in this file are lower bounds with a ceiling of 25% of their input-rate term; see research/cost/openai-cache-write.md.*

### BALROG Crafter (26 rows)

`list_price` on the sixteen API-served runs, `not_available` on the ten open-weight runs. `agent-work/derived/balrog/balrog-crafter-calculations.json` gives each submission's ten-episode `input_tokens` and `output_tokens` totals and its submission date; the cost is those totals at list divided by ten episodes, matching `compute_flops`. `research/balrog.md` establishes that no caching occurred on any Claude, Gemini or OpenAI run (no `cache_control`, `agent.cache_icl` false, and a 424-token shared prefix below both automatic-cache thresholds), so the input counter is gross and is priced gross. The image tokens on the two vision runs are inside the provider's own input counter and are therefore already billed.

### Kaggle Game Arena chess (9 rows)

`reported`. The board publishes `Avg. Cost/Turn` in cents beside `Avg. Tokens/Turn`, at the same unit and statistic as the row (the mean over every move the model played in its all-play-all). `research/game-arena.md` already used that column to solve the prompt length, so it is the most load-bearing number in the study and is carried directly. Rebuilding o3 and GPT-5 from tokens, solved prompt and list prices returns 7.70 and 12.17 cents against the published 7.7 and 12.17.

### MirrorCode (13 rows)

`list_price`. `agent-work/sources/mirrorcode/mirrorcode-run-records.csv` carries `input_tokens`, `cache_write`, `cache_read` and `output_tokens` per episode, transcribed from the retained `info.json` files, whose `total_cost` field is null. Each category is priced at the Anthropic rate for that model and the episodes are averaged, matching each row's `compute_statistic`. The cache-write rate used is the 5-minute TTL (1.25x base input) the price table carries; a 1-hour TTL would raise the write term by 60%, and nothing in the records says which was used.

### LUMEN (5 rows)

`reported`. Table 3 publishes a per-review dollar total over all six phases, which is the row's own work unit. The paper's tokens and dollars do not reconcile (`research/lumen.md`: $16.35 predicted against $23.51 reported), and the dollars are the side the paper measured, so the reported total is carried unchanged. The date is the paper's dateline for its stated March 2026 pricing window.

### APEX-Agents (9 rows)

`list_price`. Artificial Analysis publishes `canonicalEvalTokenCounts.apexAgents` as `input`, `answer` and `reasoning`, per-repeat normalized, so dividing by 452 tasks gives the per-task-run figure the row records. `cacheableInput` is null for this benchmark, so no cache split is observed: the whole input counter is priced at the gross input rate and answer plus reasoning at the output rate. **This is an upper bound on seven of the nine rows**, where `research/apex-agents.md` establishes that the provider caches by default; the compute column brackets the same unknown and takes a geometric-mean central, which the cost column cannot do without estimating. Run dates are not published, so the price-sheet date is the retrieval date of `list-prices.csv`.

### VideoGameBench (35 rows)

`reported`. Table 8 publishes the API cost of each of the 35 runs, and each row's `compute_evidence` already quotes its own figure, which is what I read rather than re-transcribing the table. The harness computed these itself with `litellm.completion_cost` over the providers' usage counters. **The seven Llama 4 Maverick figures are the harness's accounting at a lookup-bug fallback rate of $0.10/$0.20 per million, not Together's $0.27/$0.85**, so they are roughly a third of what the endpoint would have charged; that is a property of the published number, and the number is still what the operator states. Run dates are unpublished beyond "before 2025-05-23", so the date is the litellm price-table commit the study uses.

### Remote Labor Index (5 rows)

`reported` on both sides, and the one row set where the human side exists. Figure 12's printed mean model running cost is $2.34 per deliverable and the printed mean project cost is $632.60. **The $2.34 is pooled over 1,038 deliverables across five API-served configurations and is not broken down per configuration**, so all five rows carry the same figure, exactly as their compute does. The human figure is what the client paid for the freelance project through Upwork, which is a price rather than the worker's take, hence `reported_price`.

### HourVideo (2 rows)

`reported`. Table 3's Evaluation Cost column, $846 and $2,621, divided by the 25 videos in the ablation to match `compute_statistic = mean` over 25. `research/hourvideo.md` shows the column is the billed prompt-token total at $7.00 per million, which was Gemini 1.5 Pro's above-128K input rate until the 1 October 2024 cut, so the date is the last day of that price sheet.

### Portal (GPT-6 Astra) (1 row)

`reported`. The livestream overlay displayed `EST. API COST $571.33` at completion. The final counters price to $574.29 at OpenAI list rates, which my price module reproduces to the cent, so the overlay was read about 0.5% short of the run's final total; the operator's figure is the one carried.

### Factorio (GPT-6 Astra) (1 row)

`reported`. The operator's completion post of 11 September 2026: "At API pricing, logs indicate it would've cost about $4500". It covers the whole run including the Luna worker, which is the row's work unit. It is stated to one significant figure, and the row's compute is inverted from it, so the cost column and the compute column are not independent here.

### Meta textbook formalization (1 row)

`list_price`. Table 2's totals, 83,176M input and 561.2M output tokens, at Claude Opus 4.5 list rates give $429,910. The paper's own sentence is conditional, "Without token caching, this would correspond to a total cost of $430K", and its $100K alternative is explicitly back-of-the-envelope, so neither is a statement of the bill; pricing the published counters is the observed route. `research/meta-textbook.md` establishes that the OpenAI-compatibility endpoint the harness used cannot cache, so the gross input counter is the billed input.

### SRT-H (4 rows)

`not_available`. A self-hosted surgical policy, never API-served, and the paper reports no dollar cost.

### LAIT (1 row)

`not_available`. The paper reports no token, call or cost figure for any run. Footnote 8 gives a $400 monthly subscription "for the entire experiment", which is neither token-metered nor isolable to one evaluation book. The measurement exists and is withheld: `agents_pipeline/core/executor.py` writes `total_cost_usd` per job into 31 `run_summary.json` files that `docs/release/withheld-files.tsv` lists as withheld.

### OpenAI Navier-Stokes (1 row)

`not_available`. Internal OpenAI model, never sold per token; the note records that OpenAI published no dollar figure.

### Anthropic FLT (1 row)

`not_available`. Internal Anthropic research model, never sold per token; the published record is output tokens and nothing else.

### MonoRace (1 row)

`not_available`. Onboard racing system, never sold through a per-token or per-run API, and no operator cost figure.

## Conventions applied everywhere

- Every price comes from `research/cost/list-prices.csv`, selected by `price_sheet_start <= ai_cost_date` and a blank or later `price_sheet_end`. The lookup refuses an ambiguous or missing period rather than guessing, and no row needed a manual override.
- `ai_cost_usd` is at the same unit and statistic as `compute_flops` on the same row: per completed evaluation for the Epoch bins, per episode for BALROG, per turn for Game Arena, per task run for APEX-Agents, per video for HourVideo, per project for the Remote Labor Index, and the run total elsewhere.
- Cache reads are priced. The FLOP term excludes them and the dollar term must not, so a row whose counted tokens are a small share of its billed traffic (the MirrorCode rows run 97% to 99% cache reads) has a cost far above what its `tokens` column suggests.
- The standard tier is used throughout. Long-context surcharges (Google and xAI above 200k prompt, OpenAI's 2026 long-context variant) are per request and cannot be resolved from aggregate counters; where they applied, the figure is low.
- No batch discount is applied anywhere. No source in this batch states that it used a batch API.
- Nothing is grossed up for unrecorded work. The Epoch rows' `compute_flops` includes a lost-response allowance worth 0% to 1.16% of a bin's tokens; the cost prices recorded counters only, so it is low by that much on those rows.

## Judgment calls

| Call | What was decided | Why it could go the other way |
|---|---|---|
| Remote Labor Index AI cost | `reported` at the pooled $2.34 on all five rows | The spec makes a payment that "cannot be isolated to this workload" `not_available`, and $2.34 spans five configurations while each row is one. Carried as reported because it is a stated dollar figure at the row's own unit and statistic, and because the row's compute is derived from it. |
| Remote Labor Index human cost | `reported_price` at $632.60 | On Upwork the freelancer is the seller, so the figure is close to a payment; it is called a price in the paper and the platform takes a fee out of it, which is why the price label is used. |
| BALROG open-weight runs | `not_available` on all ten | `list-prices.csv` does carry a Together, Mistral or DeepSeek rate for four of the ten. `research/balrog.md` puts all ten on self-hosted vLLM or NVIDIA NIM ("the twelve vLLM, NVIDIA NIM and xAI rows", which is the ten plus the two Grok runs), so nothing was charged per token. |
| Meta textbook | `list_price` at $429,910 rather than `reported` at $430K | The paper's $430K is conditional ("Without token caching, this would correspond to") and its $100K is back-of-the-envelope. Pricing the published counters gives the same number to four significant figures and is the observed route. |
| Portal | `reported` at $571.33 rather than the $574.29 the final counters price to | The overlay is the operator's statement, read about 0.5% short of the run's end. The list-price figure is the better estimate of the full run; the reported one is the observation. |
| APEX-Agents | Gross input at the input rate | The cache-read share is unobserved for this benchmark. Any split would be an estimate, which the column forbids. |

## Cross-checks run

| Check | Result |
|---|---|
| Portal's final counters at OpenAI list ($10 / $1 / $50 per million) | $574.29, reproducing `research/portal-astra.md` to the cent |
| Game Arena o3, 9,532.6 output and 356 solved prompt tokens at the 2025-08-21 sheet | 7.70 cents against a published 7.7 |
| Game Arena GPT-5, 12,129 output and 328 prompt at the 2025-09-24 sheet | 12.17 cents against a published 12.17 |
| Meta textbook, Table 2 totals at Opus 4.5 list | $429,910 against the paper's stated $430K |
| Epoch bin instance counts and counted-token totals against `calculations.json` | Exact on all 128 bins, asserted in the build |
| Epoch gross-input families: is the cache read inside the input counter? | `cache_read / input` runs 0.506 to 0.965 on every OpenAI, Google, Zhipu and Moonshot endpoint, never above 1 |
| Validator on a staged copy, `points.csv` | 0 errors, 144 points |
| Validator on a staged copy, `excluded.csv` with `exclusion_reason` dropped | 0 errors, 95 points |
| Field diff of the other 30 (points) and 31 (excluded) columns against the pre-edit files | 0 differences |

The validator is the project's own `../AI Compute vs Human Time/collection-work/tools/validate.py`. It cannot be pointed at this folder directly, as the README says: it needs a `models.csv` covering every referenced model and a `research/`, `agent-work/sources/` tree covering the parent registry's citations. The staged copy merges this folder's `models.csv` over the parent dataset's (285 records) and overlays both research and sources trees, this folder winning. Nothing in the project folder was written.

## Per-row values

`ai_cost_usd` is USD at the row's own unit and statistic, given to six significant figures where it was computed and as stated where it was reported. The price row is the `list-prices.csv` line the lookup selected, identified by model, provider and price period.

### Epoch AI SWE-bench Verified bins

Evidence for every row in this section is `research/epoch-swebench-bins.md`, at the heading named by the point ID.

| point_id | `ai_cost_usd` | Basis | Date | Price row used | `human_cost_usd` | Human basis |
|---|---|---|---|---|---|---|
| `agen-epoch-swebench-dsv4promax-lt15m` | 0.237902 | `list_price` | 2026-06-18 | `deepseek-v4-pro-preview` / deepseek / 2026-04-24..open | — | `not_available` |
| `agen-epoch-swebench-dsv4promax-15m1h` | 0.453457 | `list_price` | 2026-06-18 | `deepseek-v4-pro-preview` / deepseek / 2026-04-24..open | — | `not_available` |
| `agen-epoch-swebench-gemini25pro-lt15m` | 0.477357 | `list_price` | 2026-02-13 | `gemini-2.5-pro` / google / 2025-04-04..open | — | `not_available` |
| `agen-epoch-swebench-gemini25pro-15m1h` | 1.14387 | `list_price` | 2026-02-13 | `gemini-2.5-pro` / google / 2025-04-04..open | — | `not_available` |
| `agen-epoch-swebench-gemini31pro-ct-lt15m` | 1.26484 | `list_price` | 2026-02-24 | `gemini-3.1-pro-preview-customtools` / google / 2026-02-19..open | — | `not_available` |
| `agen-epoch-swebench-gemini31pro-ct-15m1h` | 2.18952 | `list_price` | 2026-02-24 | `gemini-3.1-pro-preview-customtools` / google / 2026-02-19..open | — | `not_available` |
| `agen-epoch-swebench-gemini35flash-lt15m` | 0.57047 | `list_price` | 2026-06-01 | `gemini-3.5-flash` / google / 2026-05-19..open | — | `not_available` |
| `agen-epoch-swebench-gemini35flash-15m1h` | 0.731001 | `list_price` | 2026-06-01 | `gemini-3.5-flash` / google / 2026-05-19..open | — | `not_available` |
| `agen-epoch-swebench-gemini3flash-lt15m` | 0.196955 | `list_price` | 2026-02-18 | `gemini-3-flash-preview` / google / 2025-12-17..open | — | `not_available` |
| `agen-epoch-swebench-gemini3flash-15m1h` | 0.301403 | `list_price` | 2026-02-18 | `gemini-3-flash-preview` / google / 2025-12-17..open | — | `not_available` |
| `agen-epoch-swebench-gemini3pro-lt15m` | 0.925251 | `list_price` | 2026-02-13 | `gemini-3-pro` / google / 2025-11-18..open | — | `not_available` |
| `agen-epoch-swebench-gemini3pro-15m1h` | 1.45004 | `list_price` | 2026-02-13 | `gemini-3-pro` / google / 2025-11-18..open | — | `not_available` |
| `agen-epoch-swebench-glm5-lt15m` | 0.492068 | `list_price` | 2026-02-15 | `glm-5` / zai / 2026-02-11..open | — | `not_available` |
| `agen-epoch-swebench-glm5-15m1h` | 0.746566 | `list_price` | 2026-02-15 | `glm-5` / zai / 2026-02-11..open | — | `not_available` |
| `agen-epoch-swebench-glm52max-lt15m` | 0.460462 | `list_price` | 2026-06-25 | `glm-5.2` / zai / 2026-06-16..open | — | `not_available` |
| `agen-epoch-swebench-glm52max-15m1h` | 0.955129 | `list_price` | 2026-06-25 | `glm-5.2` / zai / 2026-06-16..open | — | `not_available` |
| `agen-epoch-swebench-gpt41-lt15m` | 0.302103 | `list_price` | 2026-02-08 | `gpt-4.1-2025-04-14` / openai / 2025-04-14..open | — | `not_available` |
| `agen-epoch-swebench-gpt51codex-lt15m` | 0.285952 | `list_price` | 2026-02-17 | `gpt-5.1-2025-11-13` / openai / 2025-11-13..open | — | `not_available` |
| `agen-epoch-swebench-gpt51codex-15m1h` | 0.438097 | `list_price` | 2026-02-17 | `gpt-5.1-2025-11-13` / openai / 2025-11-13..open | — | `not_available` |
| `agen-epoch-swebench-gpt51high-lt15m` | 0.909101 | `list_price` | 2026-02-18 | `gpt-5.1-2025-11-13` / openai / 2025-11-13..open | — | `not_available` |
| `agen-epoch-swebench-gpt51high-15m1h` | 1.36182 | `list_price` | 2026-02-18 | `gpt-5.1-2025-11-13` / openai / 2025-11-13..open | — | `not_available` |
| `agen-epoch-swebench-gpt52high-lt15m` | 0.914089 | `list_price` | 2026-02-12 | `gpt-5.2-2025-12-11` / openai / 2025-12-11..open | — | `not_available` |
| `agen-epoch-swebench-gpt52high-15m1h` | 1.48835 | `list_price` | 2026-02-12 | `gpt-5.2-2025-12-11` / openai / 2025-12-11..open | — | `not_available` |
| `agen-epoch-swebench-gpt53codex-lt15m` | 0.386755 | `list_price` | 2026-02-25 | `gpt-5-3-codex` / openai / 2026-02-05..open | — | `not_available` |
| `agen-epoch-swebench-gpt53codex-15m1h` | 0.62672 | `list_price` | 2026-02-25 | `gpt-5-3-codex` / openai / 2026-02-05..open | — | `not_available` |
| `agen-epoch-swebench-gpt54high-lt15m` | 0.450485 | `list_price` | 2026-03-06 | `gpt-5.4-2026-03-05` / openai / 2026-03-05..open | — | `not_available` |
| `agen-epoch-swebench-gpt54high-15m1h` | 0.844715 | `list_price` | 2026-03-06 | `gpt-5.4-2026-03-05` / openai / 2026-03-05..open | — | `not_available` |
| `agen-epoch-swebench-gpt54high-1h4h` | 1.81131 | `list_price` | 2026-03-06 | `gpt-5.4-2026-03-05` / openai / 2026-03-05..open | — | `not_available` |
| `agen-epoch-swebench-gpt5high-lt15m` | 0.775185 | `list_price` | 2026-02-06 | `gpt-5` / openai / 2025-08-07..open | — | `not_available` |
| `agen-epoch-swebench-gpt5high-15m1h` | 1.06062 | `list_price` | 2026-02-06 | `gpt-5` / openai / 2025-08-07..open | — | `not_available` |
| `agen-epoch-swebench-gpt5med-lt15m` | 0.445932 | `list_price` | 2026-02-05 | `gpt-5` / openai / 2025-08-07..open | — | `not_available` |
| `agen-epoch-swebench-gpt5med-15m1h` | 0.63218 | `list_price` | 2026-02-05 | `gpt-5` / openai / 2025-08-07..open | — | `not_available` |
| `agen-epoch-swebench-gpt5mini-lt15m` | 0.0776673 | `list_price` | 2026-02-01 | `gpt-5-mini-2025-08-07` / openai / 2025-08-07..open | — | `not_available` |
| `agen-epoch-swebench-gpt5mini-15m1h` | 0.107942 | `list_price` | 2026-02-01 | `gpt-5-mini-2025-08-07` / openai / 2025-08-07..open | — | `not_available` |
| `agen-epoch-swebench-kimik25-lt15m` | 0.094073 | `list_price` | 2026-02-17 | `kimi-k2.5` / moonshot / 2026-01-27..2026-08-31 | — | `not_available` |
| `agen-epoch-swebench-kimik25-15m1h` | 0.181473 | `list_price` | 2026-02-17 | `kimi-k2.5` / moonshot / 2026-01-27..2026-08-31 | — | `not_available` |
| `agen-epoch-swebench-kimik26-lt15m` | 0.164953 | `list_price` | 2026-05-08 | `kimi-k2.6` / moonshot / 2026-04-20..open | — | `not_available` |
| `agen-epoch-swebench-kimik26-15m1h` | 0.360744 | `list_price` | 2026-05-08 | `kimi-k2.6` / moonshot / 2026-04-20..open | — | `not_available` |
| `agen-epoch-swebench-o3med-lt15m` | 2.40777 | `list_price` | 2026-02-12 | `o3-2025-04-16` / openai / 2025-06-10..open | — | `not_available` |
| `agen-epoch-swebench-o3med-15m1h` | 2.75664 | `list_price` | 2026-02-12 | `o3-2025-04-16` / openai / 2025-06-10..open | — | `not_available` |
| `agen-epoch-swebench-opus4-lt15m` | 2.32225 | `list_price` | 2026-02-06 | `claude-opus-4` / anthropic / 2025-05-22..open | — | `not_available` |
| `agen-epoch-swebench-opus4-15m1h` | 3.24596 | `list_price` | 2026-02-06 | `claude-opus-4` / anthropic / 2025-05-22..open | — | `not_available` |
| `agen-epoch-swebench-opus41-lt15m` | 2.91288 | `list_price` | 2026-02-11 | `claude-opus-4-1` / anthropic / 2025-05-22..open | — | `not_available` |
| `agen-epoch-swebench-opus41-15m1h` | 4.03172 | `list_price` | 2026-02-11 | `claude-opus-4-1` / anthropic / 2025-05-22..open | — | `not_available` |
| `agen-epoch-swebench-opus45-lt15m` | 0.289163 | `list_price` | 2026-02-05 | `claude-opus-4-5` / anthropic / 2025-11-24..open | — | `not_available` |
| `agen-epoch-swebench-opus45-15m1h` | 0.531719 | `list_price` | 2026-02-05 | `claude-opus-4-5` / anthropic / 2025-11-24..open | — | `not_available` |
| `agen-epoch-swebench-opus46-lt15m` | 0.196758 | `list_price` | 2026-02-10 | `claude-opus-4-6` / anthropic / 2026-02-05..open | — | `not_available` |
| `agen-epoch-swebench-opus46-15m1h` | 0.371295 | `list_price` | 2026-02-10 | `claude-opus-4-6` / anthropic / 2026-02-05..open | — | `not_available` |
| `agen-epoch-swebench-opus46cc-lt15m` | 0.819578 | `list_price` | 2026-02-18 | `claude-opus-4-6` / anthropic / 2026-02-05..open | — | `not_available` |
| `agen-epoch-swebench-opus46cc-15m1h` | 1.46305 | `list_price` | 2026-02-18 | `claude-opus-4-6` / anthropic / 2026-02-05..open | — | `not_available` |
| `agen-epoch-swebench-opus46cc-1h4h` | 2.87694 | `list_price` | 2026-02-18 | `claude-opus-4-6` / anthropic / 2026-02-05..open | — | `not_available` |
| `agen-epoch-swebench-opus47max-lt15m` | 1.09329 | `list_price` | 2026-04-20 | `claude-opus-4-7` / anthropic / 2026-04-16..open | — | `not_available` |
| `agen-epoch-swebench-opus47max-15m1h` | 2.49318 | `list_price` | 2026-04-20 | `claude-opus-4-7` / anthropic / 2026-04-16..open | — | `not_available` |
| `agen-epoch-swebench-opus47max-1h4h` | 5.3586 | `list_price` | 2026-04-20 | `claude-opus-4-7` / anthropic / 2026-04-16..open | — | `not_available` |
| `agen-epoch-swebench-opus47max-gt4h` | 2.64555 | `list_price` | 2026-04-20 | `claude-opus-4-7` / anthropic / 2026-04-16..open | — | `not_available` |
| `agen-epoch-swebench-qwen37max-lt15m` | 0.380102 | `list_price` | 2026-06-18 | `qwen3.7-max` / alibaba / 2026-05-21..open | — | `not_available` |
| `agen-epoch-swebench-qwen37max-15m1h` | 0.8494 | `list_price` | 2026-06-18 | `qwen3.7-max` / alibaba / 2026-05-21..open | — | `not_available` |
| `agen-epoch-swebench-sonnet37-lt15m` | 0.323321 | `list_price` | 2026-02-04 | `claude-3-7-sonnet` / anthropic / 2025-02-24..open | — | `not_available` |
| `agen-epoch-swebench-sonnet37-15m1h` | 0.453295 | `list_price` | 2026-02-04 | `claude-3-7-sonnet` / anthropic / 2025-02-24..open | — | `not_available` |
| `agen-epoch-swebench-sonnet45-lt15m` | 1.02192 | `list_price` | 2026-02-05 | `claude-sonnet-4-5` / anthropic / 2025-09-29..open | — | `not_available` |
| `agen-epoch-swebench-sonnet45-15m1h` | 1.32119 | `list_price` | 2026-02-05 | `claude-sonnet-4-5` / anthropic / 2025-09-29..open | — | `not_available` |
| `agen-epoch-swebench-sonnet46-lt15m` | 0.194709 | `list_price` | 2026-02-21 | `claude-sonnet-4-6` / anthropic / 2026-02-17..open | — | `not_available` |
| `agen-epoch-swebench-sonnet46-15m1h` | 0.423969 | `list_price` | 2026-02-21 | `claude-sonnet-4-6` / anthropic / 2026-02-17..open | — | `not_available` |
| `agen-epoch-swebench-gemini31pro-ct-gt4h` | 3.8072 | `list_price` | 2026-02-24 | `gemini-3.1-pro-preview-customtools` / google / 2026-02-19..open | — | `not_available` |
| `agen-epoch-swebench-gemini35flash-1h4h` | 1.08986 | `list_price` | 2026-06-01 | `gemini-3.5-flash` / google / 2026-05-19..open | — | `not_available` |
| `agen-epoch-swebench-gemini35flash-gt4h` | 1.13412 | `list_price` | 2026-06-01 | `gemini-3.5-flash` / google / 2026-05-19..open | — | `not_available` |
| `agen-epoch-swebench-gemini3flash-gt4h` | 0.399873 | `list_price` | 2026-02-18 | `gemini-3-flash-preview` / google / 2025-12-17..open | — | `not_available` |
| `agen-epoch-swebench-gemini3pro-gt4h` | 1.76757 | `list_price` | 2026-02-13 | `gemini-3-pro` / google / 2025-11-18..open | — | `not_available` |
| `agen-epoch-swebench-glm5-gt4h` | 0.595387 | `list_price` | 2026-02-15 | `glm-5` / zai / 2026-02-11..open | — | `not_available` |
| `agen-epoch-swebench-glm52max-1h4h` | 2.3075 | `list_price` | 2026-06-25 | `glm-5.2` / zai / 2026-06-16..open | — | `not_available` |
| `agen-epoch-swebench-glm52max-gt4h` | 1.51796 | `list_price` | 2026-06-25 | `glm-5.2` / zai / 2026-06-16..open | — | `not_available` |
| `agen-epoch-swebench-gpt4o1120-lt15m` | 0.729105 | `list_price` | 2026-02-11 | `gpt-4o-2024-11-20` / openai / 2024-10-01..open | — | `not_available` |
| `agen-epoch-swebench-gpt51codex-gt4h` | 0.838256 | `list_price` | 2026-02-17 | `gpt-5.1-2025-11-13` / openai / 2025-11-13..open | — | `not_available` |
| `agen-epoch-swebench-gpt52high-gt4h` | 2.85163 | `list_price` | 2026-02-12 | `gpt-5.2-2025-12-11` / openai / 2025-12-11..open | — | `not_available` |
| `agen-epoch-swebench-gpt53codex-1h4h` | 1.26776 | `list_price` | 2026-02-25 | `gpt-5-3-codex` / openai / 2026-02-05..open | — | `not_available` |
| `agen-epoch-swebench-gpt53codex-gt4h` | 1.1977 | `list_price` | 2026-02-25 | `gpt-5-3-codex` / openai / 2026-02-05..open | — | `not_available` |
| `agen-epoch-swebench-gpt54high-gt4h` | 2.30525 | `list_price` | 2026-03-06 | `gpt-5.4-2026-03-05` / openai / 2026-03-05..open | — | `not_available` |
| `agen-epoch-swebench-gpt5high-gt4h` | 0.672982 | `list_price` | 2026-02-06 | `gpt-5` / openai / 2025-08-07..open | — | `not_available` |
| `agen-epoch-swebench-kimik25-gt4h` | 0.213231 | `list_price` | 2026-02-17 | `kimi-k2.5` / moonshot / 2026-01-27..2026-08-31 | — | `not_available` |
| `agen-epoch-swebench-kimik26-1h4h` | 0.742176 | `list_price` | 2026-05-08 | `kimi-k2.6` / moonshot / 2026-04-20..open | — | `not_available` |
| `agen-epoch-swebench-opus4-gt4h` | 3.60442 | `list_price` | 2026-02-06 | `claude-opus-4` / anthropic / 2025-05-22..open | — | `not_available` |
| `agen-epoch-swebench-opus41-1h4h` | 5.19061 | `list_price` | 2026-02-11 | `claude-opus-4-1` / anthropic / 2025-05-22..open | — | `not_available` |
| `agen-epoch-swebench-opus41-gt4h` | 5.07252 | `list_price` | 2026-02-11 | `claude-opus-4-1` / anthropic / 2025-05-22..open | — | `not_available` |
| `agen-epoch-swebench-opus45-1h4h` | 1.20273 | `list_price` | 2026-02-05 | `claude-opus-4-5` / anthropic / 2025-11-24..open | — | `not_available` |
| `agen-epoch-swebench-opus45-gt4h` | 0.86413 | `list_price` | 2026-02-05 | `claude-opus-4-5` / anthropic / 2025-11-24..open | — | `not_available` |
| `agen-epoch-swebench-opus46-1h4h` | 0.720665 | `list_price` | 2026-02-10 | `claude-opus-4-6` / anthropic / 2026-02-05..open | — | `not_available` |
| `agen-epoch-swebench-opus46-gt4h` | 0.529065 | `list_price` | 2026-02-10 | `claude-opus-4-6` / anthropic / 2026-02-05..open | — | `not_available` |
| `agen-epoch-swebench-opus46cc-gt4h` | 1.77839 | `list_price` | 2026-02-18 | `claude-opus-4-6` / anthropic / 2026-02-05..open | — | `not_available` |
| `agen-epoch-swebench-qwen37max-gt4h` | 0.777379 | `list_price` | 2026-06-18 | `qwen3.7-max` / alibaba / 2026-05-21..open | — | `not_available` |
| `agen-epoch-swebench-sonnet37-gt4h` | 0.625514 | `list_price` | 2026-02-04 | `claude-3-7-sonnet` / anthropic / 2025-02-24..open | — | `not_available` |
| `agen-epoch-swebench-sonnet46-1h4h` | 1.28236 | `list_price` | 2026-02-21 | `claude-sonnet-4-6` / anthropic / 2026-02-17..open | — | `not_available` |
| `agen-epoch-swebench-sonnet46-gt4h` | 0.596806 | `list_price` | 2026-02-21 | `claude-sonnet-4-6` / anthropic / 2026-02-17..open | — | `not_available` |
| `agen-epoch-swebench-dsv4promax-1h4h` | 0.836507 | `list_price` | 2026-06-18 | `deepseek-v4-pro-preview` / deepseek / 2026-04-24..open | — | `not_available` |
| `agen-epoch-swebench-dsv4promax-gt4h` | 0.37058 | `list_price` | 2026-06-18 | `deepseek-v4-pro-preview` / deepseek / 2026-04-24..open | — | `not_available` |
| `agen-epoch-swebench-gemini25pro-1h4h` | 1.7205 | `list_price` | 2026-02-13 | `gemini-2.5-pro` / google / 2025-04-04..open | — | `not_available` |
| `agen-epoch-swebench-gemini25pro-gt4h` | 1.39903 | `list_price` | 2026-02-13 | `gemini-2.5-pro` / google / 2025-04-04..open | — | `not_available` |
| `agen-epoch-swebench-gemini31pro-ct-1h4h` | 3.4709 | `list_price` | 2026-02-24 | `gemini-3.1-pro-preview-customtools` / google / 2026-02-19..open | — | `not_available` |
| `agen-epoch-swebench-gemini3flash-1h4h` | 0.496438 | `list_price` | 2026-02-18 | `gemini-3-flash-preview` / google / 2025-12-17..open | — | `not_available` |
| `agen-epoch-swebench-gemini3pro-1h4h` | 2.65845 | `list_price` | 2026-02-13 | `gemini-3-pro` / google / 2025-11-18..open | — | `not_available` |
| `agen-epoch-swebench-glm5-1h4h` | 1.34599 | `list_price` | 2026-02-15 | `glm-5` / zai / 2026-02-11..open | — | `not_available` |
| `agen-epoch-swebench-gpt41-15m1h` | 0.624059 | `list_price` | 2026-02-08 | `gpt-4.1-2025-04-14` / openai / 2025-04-14..open | — | `not_available` |
| `agen-epoch-swebench-gpt41-1h4h` | 0.550543 | `list_price` | 2026-02-08 | `gpt-4.1-2025-04-14` / openai / 2025-04-14..open | — | `not_available` |
| `agen-epoch-swebench-gpt41-gt4h` | 0.638007 | `list_price` | 2026-02-08 | `gpt-4.1-2025-04-14` / openai / 2025-04-14..open | — | `not_available` |
| `agen-epoch-swebench-gpt4o1120-15m1h` | 1.37698 | `list_price` | 2026-02-11 | `gpt-4o-2024-11-20` / openai / 2024-10-01..open | — | `not_available` |
| `agen-epoch-swebench-gpt4o1120-1h4h` | 0.87542 | `list_price` | 2026-02-11 | `gpt-4o-2024-11-20` / openai / 2024-10-01..open | — | `not_available` |
| `agen-epoch-swebench-gpt4o1120-gt4h` | 0.240179 | `list_price` | 2026-02-11 | `gpt-4o-2024-11-20` / openai / 2024-10-01..open | — | `not_available` |
| `agen-epoch-swebench-gpt51codex-1h4h` | 0.801396 | `list_price` | 2026-02-17 | `gpt-5.1-2025-11-13` / openai / 2025-11-13..open | — | `not_available` |
| `agen-epoch-swebench-gpt51high-1h4h` | 2.01521 | `list_price` | 2026-02-18 | `gpt-5.1-2025-11-13` / openai / 2025-11-13..open | — | `not_available` |
| `agen-epoch-swebench-gpt51high-gt4h` | 1.33933 | `list_price` | 2026-02-18 | `gpt-5.1-2025-11-13` / openai / 2025-11-13..open | — | `not_available` |
| `agen-epoch-swebench-gpt52high-1h4h` | 3.46755 | `list_price` | 2026-02-12 | `gpt-5.2-2025-12-11` / openai / 2025-12-11..open | — | `not_available` |
| `agen-epoch-swebench-gpt5high-1h4h` | 1.82874 | `list_price` | 2026-02-06 | `gpt-5` / openai / 2025-08-07..open | — | `not_available` |
| `agen-epoch-swebench-gpt5med-1h4h` | 0.934846 | `list_price` | 2026-02-05 | `gpt-5` / openai / 2025-08-07..open | — | `not_available` |
| `agen-epoch-swebench-gpt5med-gt4h` | 0.726611 | `list_price` | 2026-02-05 | `gpt-5` / openai / 2025-08-07..open | — | `not_available` |
| `agen-epoch-swebench-gpt5mini-1h4h` | 0.143034 | `list_price` | 2026-02-01 | `gpt-5-mini-2025-08-07` / openai / 2025-08-07..open | — | `not_available` |
| `agen-epoch-swebench-gpt5mini-gt4h` | 0.145162 | `list_price` | 2026-02-01 | `gpt-5-mini-2025-08-07` / openai / 2025-08-07..open | — | `not_available` |
| `agen-epoch-swebench-kimik25-1h4h` | 0.300777 | `list_price` | 2026-02-17 | `kimi-k2.5` / moonshot / 2026-01-27..2026-08-31 | — | `not_available` |
| `agen-epoch-swebench-kimik26-gt4h` | 0.861975 | `list_price` | 2026-05-08 | `kimi-k2.6` / moonshot / 2026-04-20..open | — | `not_available` |
| `agen-epoch-swebench-o3med-1h4h` | 4.6092 | `list_price` | 2026-02-12 | `o3-2025-04-16` / openai / 2025-06-10..open | — | `not_available` |
| `agen-epoch-swebench-o3med-gt4h` | 1.21343 | `list_price` | 2026-02-12 | `o3-2025-04-16` / openai / 2025-06-10..open | — | `not_available` |
| `agen-epoch-swebench-opus4-1h4h` | 4.91378 | `list_price` | 2026-02-06 | `claude-opus-4` / anthropic / 2025-05-22..open | — | `not_available` |
| `agen-epoch-swebench-qwen37max-1h4h` | 2.08557 | `list_price` | 2026-06-18 | `qwen3.7-max` / alibaba / 2026-05-21..open | — | `not_available` |
| `agen-epoch-swebench-sonnet37-1h4h` | 0.670525 | `list_price` | 2026-02-04 | `claude-3-7-sonnet` / anthropic / 2025-02-24..open | — | `not_available` |
| `agen-epoch-swebench-sonnet45-1h4h` | 1.6559 | `list_price` | 2026-02-05 | `claude-sonnet-4-5` / anthropic / 2025-09-29..open | — | `not_available` |
| `agen-epoch-swebench-sonnet45-gt4h` | 1.39198 | `list_price` | 2026-02-05 | `claude-sonnet-4-5` / anthropic / 2025-09-29..open | — | `not_available` |

### BALROG Crafter

Evidence for every row in this section is `research/balrog.md`, at the heading named by the point ID.

| point_id | `ai_cost_usd` | Basis | Date | Price row used | `human_cost_usd` | Human basis |
|---|---|---|---|---|---|---|
| `game-balrog-crafter-gemini25pro` | 0.66591 | `list_price` | 2025-04-25 | `gemini-2.5-pro-03-25` / google / 2025-04-04..open | — | `not_available` |
| `game-balrog-crafter-grok4` | 1.39487 | `list_price` | 2025-07-23 | `grok-4` / xai / 2025-07-09..open | — | `not_available` |
| `game-balrog-crafter-gemini25flash` | 0.0956637 | `list_price` | 2025-07-22 | `gemini-2.5-flash` / google / 2025-06-17..open | — | `not_available` |
| `game-balrog-crafter-gpt5minimal` | 0.563244 | `list_price` | 2025-08-19 | `gpt-5` / openai / 2025-08-07..open | — | `not_available` |
| `game-balrog-crafter-gemini3pro` | 0.817278 | `list_price` | 2026-02-03 | `gemini-3-pro` / google / 2025-11-18..open | — | `not_available` |
| `game-balrog-crafter-gemini3flash` | 0.200094 | `list_price` | 2026-02-13 | `gemini-3-flash-preview` / google / 2025-12-17..open | — | `not_available` |
| `game-balrog-crafter-gemini31pro` | 0.761643 | `list_price` | 2026-02-21 | `gemini-3.1-pro-preview` / google / 2026-02-19..open | — | `not_available` |
| `game-balrog-crafter-claudeopus45` | 2.11779 | `list_price` | 2026-02-24 | `claude-opus-4-5` / anthropic / 2025-11-24..open | — | `not_available` |
| `game-balrog-crafter-claudeopus45thinking` | 4.32295 | `list_price` | 2026-02-24 | `claude-opus-4-5` / anthropic / 2025-11-24..open | — | `not_available` |
| `game-balrog-crafter-gemini31prothinking` | 1.08306 | `list_price` | 2026-02-25 | `gemini-3.1-pro-preview` / google / 2026-02-19..open | — | `not_available` |
| `game-balrog-crafter-vlm-claude35sonnet` | 1.1986 | `list_price` | 2024-11-11 | `claude-3-5-sonnet-20240620` / anthropic / 2024-06-20..open | — | `not_available` |
| `game-balrog-crafter-vlm-gemini25pro` | 2.16594 | `list_price` | 2025-04-25 | `gemini-2.5-pro-03-25` / google / 2025-04-04..open | — | `not_available` |
| `game-balrog-crafter-deepseekr1` | — | `not_available` | — | — | — | `not_available` |
| `game-balrog-crafter-rekaflash3` | — | `not_available` | — | — | — | `not_available` |
| `game-balrog-crafter-llama32-1b` | — | `not_available` | — | — | — | `not_available` |
| `game-balrog-crafter-llama32-3b` | — | `not_available` | — | — | — | `not_available` |
| `game-balrog-crafter-llama31-8b` | — | `not_available` | — | — | — | `not_available` |
| `game-balrog-crafter-claude35sonnet` | 0.953585 | `list_price` | 2024-11-11 | `claude-3-5-sonnet-20240620` / anthropic / 2024-06-20..open | — | `not_available` |
| `game-balrog-crafter-qwen25-7b` | — | `not_available` | — | — | — | `not_available` |
| `game-balrog-crafter-claude35haiku` | 0.260942 | `list_price` | 2024-12-11 | `claude-3-5-haiku-20241022` / anthropic / 2024-11-20..open | — | `not_available` |
| `game-balrog-crafter-mistralnemo` | — | `not_available` | — | — | — | `not_available` |
| `game-balrog-crafter-llama33-70b` | — | `not_available` | — | — | — | `not_available` |
| `game-balrog-crafter-phi4` | — | `not_available` | — | — | — | `not_available` |
| `game-balrog-crafter-r1distillqwen32b` | — | `not_available` | — | — | — | `not_available` |
| `game-balrog-crafter-grok3` | 0.891722 | `list_price` | 2025-04-25 | `grok-3-beta` / xai / 2025-04-09..open | — | `not_available` |
| `game-balrog-crafter-claudehaiku45` | 0.442795 | `list_price` | 2026-02-24 | `claude-haiku-4-5` / anthropic / 2025-10-15..open | — | `not_available` |

### Kaggle Game Arena chess

Evidence for every row in this section is `research/game-arena.md`, at the heading named by the point ID.

| point_id | `ai_cost_usd` | Basis | Date | Price row used | `human_cost_usd` | Human basis |
|---|---|---|---|---|---|---|
| `game-chess-move-arena-o3` | 0.077 | `reported` | 2025-08-21 | — | — | `not_available` |
| `game-chess-move-arena-gpt5` | 0.1217 | `reported` | 2025-09-24 | — | — | `not_available` |
| `game-chess-move-arena-grok4` | 0.335 | `reported` | 2025-08-21 | — | — | `not_available` |
| `game-chess-move-arena-gemini25pro` | 0.041 | `reported` | 2025-08-21 | — | — | `not_available` |
| `game-chess-move-arena-o4mini` | 0.04 | `reported` | 2025-08-21 | — | — | `not_available` |
| `game-chess-move-arena-gpt41` | 0.006 | `reported` | 2025-08-21 | — | — | `not_available` |
| `game-chess-move-arena-sonnet4` | 0.156 | `reported` | 2025-08-21 | — | — | `not_available` |
| `game-chess-move-arena-opus4` | 0.245 | `reported` | 2025-08-21 | — | — | `not_available` |
| `game-chess-move-arena-r1` | 0.095 | `reported` | 2025-08-21 | — | — | `not_available` |

### MirrorCode

Evidence for every row in this section is `research/mirrorcode.md`, at the heading named by the point ID.

| point_id | `ai_cost_usd` | Basis | Date | Price row used | `human_cost_usd` | Human basis |
|---|---|---|---|---|---|---|
| `agen-mirrorcode-gotree-py-opus46` | 194.13 | `list_price` | 2026-03-29 | `claude-opus-4-6` / anthropic / 2026-02-05..open | — | `not_available` |
| `agen-mirrorcode-cal-c-opus46` | 31.4201 | `list_price` | 2026-03-31 | `claude-opus-4-6` / anthropic / 2026-02-05..open | — | `not_available` |
| `agen-mirrorcode-cal-py-opus46` | 32.0128 | `list_price` | 2026-03-31 | `claude-opus-4-6` / anthropic / 2026-02-05..open | — | `not_available` |
| `agen-mirrorcode-cal-rust-opus46` | 32.8602 | `list_price` | 2026-03-31 | `claude-opus-4-6` / anthropic / 2026-02-05..open | — | `not_available` |
| `agen-mirrorcode-choose-c-opus46` | 14.7646 | `list_price` | 2026-03-31 | `claude-opus-4-6` / anthropic / 2026-02-05..open | — | `not_available` |
| `agen-mirrorcode-choose-py-opus46` | 20.939 | `list_price` | 2026-03-31 | `claude-opus-4-6` / anthropic / 2026-02-05..open | — | `not_available` |
| `agen-mirrorcode-choose-rust-opus46` | 11.1908 | `list_price` | 2026-03-31 | `claude-opus-4-6` / anthropic / 2026-02-05..open | — | `not_available` |
| `agen-mirrorcode-gotree-py-opus45` | 75.189 | `list_price` | 2026-03-30 | `claude-opus-4-5` / anthropic / 2025-11-24..open | — | `not_available` |
| `agen-mirrorcode-gotree-py-opus4` | 19.843 | `list_price` | 2026-03-30 | `claude-opus-4` / anthropic / 2025-05-22..open | — | `not_available` |
| `agen-mirrorcode-gotree-py-opus41` | 16.721 | `list_price` | 2026-03-30 | `claude-opus-4-1` / anthropic / 2025-05-22..open | — | `not_available` |
| `agen-mirrorcode-pkl-c-opus46` | 576.663 | `list_price` | 2026-03-31 | `claude-opus-4-6` / anthropic / 2026-02-05..open | — | `not_available` |
| `agen-mirrorcode-pkl-py-opus46` | 378.239 | `list_price` | 2026-03-31 | `claude-opus-4-6` / anthropic / 2026-02-05..open | — | `not_available` |
| `agen-mirrorcode-pkl-rust-opus46` | 557.296 | `list_price` | 2026-03-31 | `claude-opus-4-6` / anthropic / 2026-02-05..open | — | `not_available` |

### LUMEN

Evidence for every row in this section is `research/lumen.md`, at the heading named by the point ID.

| point_id | `ai_cost_usd` | Basis | Date | Price row used | `human_cost_usd` | Human basis |
|---|---|---|---|---|---|---|
| `agen-lumen-d1-gemini31pro` | 26.1 | `reported` | 2026-03-29 | — | — | `not_available` |
| `agen-lumen-d2-gemini31pro` | 22.51 | `reported` | 2026-03-29 | — | — | `not_available` |
| `agen-lumen-d3-gemini31pro` | 19.51 | `reported` | 2026-03-29 | — | — | `not_available` |
| `agen-lumen-d4-gemini31pro` | 22.65 | `reported` | 2026-03-29 | — | — | `not_available` |
| `agen-lumen-d5-gemini31pro` | 29.04 | `reported` | 2026-03-29 | — | — | `not_available` |

### APEX-Agents

Evidence for every row in this section is `research/apex-agents.md`, at the heading named by the point ID.

| point_id | `ai_cost_usd` | Basis | Date | Price row used | `human_cost_usd` | Human basis |
|---|---|---|---|---|---|---|
| `work-apex-agents-kimik3` | 2.14946 | `list_price` | 2026-09-13 | `kimi-k3` / moonshot / 2026-07-16..open | — | `not_available` |
| `work-apex-agents-gpt55` | 3.11135 | `list_price` | 2026-09-13 | `gpt-5-5` / openai / 2026-04-23..open | — | `not_available` |
| `work-apex-agents-glm52` | 1.58731 | `list_price` | 2026-09-13 | `glm-5.2` / zai / 2026-06-16..open | — | `not_available` |
| `work-apex-agents-gpt54` | 2.45485 | `list_price` | 2026-09-13 | `gpt-5.4-2026-03-05` / openai / 2026-03-05..open | — | `not_available` |
| `work-apex-agents-opus46` | 3.32139 | `list_price` | 2026-09-13 | `claude-opus-4-6` / anthropic / 2026-02-05..open | — | `not_available` |
| `work-apex-agents-gemini35flash` | 4.25599 | `list_price` | 2026-09-13 | `gemini-3.5-flash` / google / 2026-05-19..open | — | `not_available` |
| `work-apex-agents-gpt56terra` | 2.12637 | `list_price` | 2026-09-13 | `gpt-5-6-terra` / openai / 2026-07-09..open | — | `not_available` |
| `work-apex-agents-gpt56luna` | 0.242495 | `list_price` | 2026-09-13 | `gpt-5-6-luna` / openai / 2026-07-09..open | — | `not_available` |
| `work-apex-agents-gptoss120b` | 0.19678 | `list_price` | 2026-09-13 | `gpt-oss-120b` / together / 2025-08-05..open | — | `not_available` |

### VideoGameBench

Evidence for every row in this section is `research/videogamebench.md`, at the heading named by the point ID.

| point_id | `ai_cost_usd` | Basis | Date | Price row used | `human_cost_usd` | Human basis |
|---|---|---|---|---|---|---|
| `game-vgb-civ1-gpt4o` | 14.46 | `reported` | 2025-05-22 | — | — | `not_available` |
| `game-vgb-civ1-sonnet37` | 30 | `reported` | 2025-05-22 | — | — | `not_available` |
| `game-vgb-civ1-gemini25pro` | 5.29 | `reported` | 2025-05-22 | — | — | `not_available` |
| `game-vgb-civ1-llama4mav` | 0.42 | `reported` | 2025-05-22 | — | — | `not_available` |
| `game-vgb-civ1-gemini20flash` | 10.05 | `reported` | 2025-05-22 | — | — | `not_available` |
| `game-vgb-nfs-gpt4o` | 0.5 | `reported` | 2025-05-22 | — | — | `not_available` |
| `game-vgb-nfs-sonnet37` | 0.62 | `reported` | 2025-05-22 | — | — | `not_available` |
| `game-vgb-nfs-gemini25pro` | 0.38 | `reported` | 2025-05-22 | — | — | `not_available` |
| `game-vgb-nfs-llama4mav` | 0.04 | `reported` | 2025-05-22 | — | — | `not_available` |
| `game-vgb-nfs-gemini20flash` | 0.08 | `reported` | 2025-05-22 | — | — | `not_available` |
| `game-vgb-tim-gpt4o` | 1.36 | `reported` | 2025-05-22 | — | — | `not_available` |
| `game-vgb-tim-sonnet37` | 5.26 | `reported` | 2025-05-22 | — | — | `not_available` |
| `game-vgb-tim-gemini25pro` | 1.31 | `reported` | 2025-05-22 | — | — | `not_available` |
| `game-vgb-tim-llama4mav` | 0.11 | `reported` | 2025-05-22 | — | — | `not_available` |
| `game-vgb-tim-gemini20flash` | 0.18 | `reported` | 2025-05-22 | — | — | `not_available` |
| `game-vgb-doom2-gpt4o` | 0.17 | `reported` | 2025-05-22 | — | — | `not_available` |
| `game-vgb-doom2-sonnet37` | 0.4 | `reported` | 2025-05-22 | — | — | `not_available` |
| `game-vgb-doom2-gemini25pro` | 3.79 | `reported` | 2025-05-22 | — | — | `not_available` |
| `game-vgb-doom2-llama4mav` | 0.03 | `reported` | 2025-05-22 | — | — | `not_available` |
| `game-vgb-doom2-gemini20flash` | 0.01 | `reported` | 2025-05-22 | — | — | `not_available` |
| `game-vgb-crystal-gpt4o` | 15.04 | `reported` | 2025-05-22 | — | — | `not_available` |
| `game-vgb-crystal-sonnet37` | 29.64 | `reported` | 2025-05-22 | — | — | `not_available` |
| `game-vgb-crystal-gemini25pro` | 4.78 | `reported` | 2025-05-22 | — | — | `not_available` |
| `game-vgb-crystal-llama4mav` | 0.14 | `reported` | 2025-05-22 | — | — | `not_available` |
| `game-vgb-crystal-gemini20flash` | 3.88 | `reported` | 2025-05-22 | — | — | `not_available` |
| `game-vgb-kirby-gpt4o` | 8.91 | `reported` | 2025-05-22 | — | — | `not_available` |
| `game-vgb-kirby-sonnet37` | 2.98 | `reported` | 2025-05-22 | — | — | `not_available` |
| `game-vgb-kirby-gemini25pro` | 3.89 | `reported` | 2025-05-22 | — | — | `not_available` |
| `game-vgb-kirby-llama4mav` | 0.09 | `reported` | 2025-05-22 | — | — | `not_available` |
| `game-vgb-kirby-gemini20flash` | 0.16 | `reported` | 2025-05-22 | — | — | `not_available` |
| `game-vgb-zelda-gpt4o` | 7.86 | `reported` | 2025-05-22 | — | — | `not_available` |
| `game-vgb-zelda-sonnet37` | 20 | `reported` | 2025-05-22 | — | — | `not_available` |
| `game-vgb-zelda-gemini25pro` | 18.51 | `reported` | 2025-05-22 | — | — | `not_available` |
| `game-vgb-zelda-llama4mav` | 0.09 | `reported` | 2025-05-22 | — | — | `not_available` |
| `game-vgb-zelda-gemini20flash` | 0.18 | `reported` | 2025-05-22 | — | — | `not_available` |

### Remote Labor Index

Evidence for every row in this section is `research/remote-labor-index.md`, at the heading named by the point ID.

| point_id | `ai_cost_usd` | Basis | Date | Price row used | `human_cost_usd` | Human basis |
|---|---|---|---|---|---|---|
| `work-rli-gpt5-cli` | 2.34 | `reported` | 2025-10-27 | — | 632.6 | `reported_price` |
| `work-rli-gpt5-cua` | 2.34 | `reported` | 2025-10-27 | — | 632.6 | `reported_price` |
| `work-rli-sonnet45` | 2.34 | `reported` | 2025-10-27 | — | 632.6 | `reported_price` |
| `work-rli-grok4` | 2.34 | `reported` | 2025-10-27 | — | 632.6 | `reported_price` |
| `work-rli-gemini25pro` | 2.34 | `reported` | 2025-10-27 | — | 632.6 | `reported_price` |

### HourVideo

Evidence for every row in this section is `research/hourvideo.md`, at the heading named by the point ID.

| point_id | `ai_cost_usd` | Basis | Date | Price row used | `human_cost_usd` | Human basis |
|---|---|---|---|---|---|---|
| `perc-hourvideo-gemini15pro-tasklevel` | 33.84 | `reported` | 2024-09-30 | — | — | `not_available` |
| `perc-hourvideo-gemini15pro-individual` | 104.84 | `reported` | 2024-09-30 | — | — | `not_available` |

### Portal (GPT-6 Astra)

Evidence for every row in this section is `research/portal-astra.md`, at the heading named by the point ID.

| point_id | `ai_cost_usd` | Basis | Date | Price row used | `human_cost_usd` | Human basis |
|---|---|---|---|---|---|---|
| `game-portal-gpt6astra` | 571.33 | `reported` | 2026-09-05 | — | — | `not_available` |

### Factorio (GPT-6 Astra)

Evidence for every row in this section is `research/factorio-astra.md`, at the heading named by the point ID.

| point_id | `ai_cost_usd` | Basis | Date | Price row used | `human_cost_usd` | Human basis |
|---|---|---|---|---|---|---|
| `game-factorio-gpt6astra` | 4500 | `reported` | 2026-09-11 | — | — | `not_available` |

### Meta textbook formalization

Evidence for every row in this section is `research/meta-textbook.md`, at the heading named by the point ID.

| point_id | `ai_cost_usd` | Basis | Date | Price row used | `human_cost_usd` | Human basis |
|---|---|---|---|---|---|---|
| `reas-lean-textbook-algcomb-opus45` | 429910 | `list_price` | 2026-04-01 | `claude-opus-4-5` / anthropic / 2025-11-24..open | — | `not_available` |

### SRT-H

Evidence for every row in this section is `research/srt-h.md`, at the heading named by the point ID.

| point_id | `ai_cost_usd` | Basis | Date | Price row used | `human_cost_usd` | Human basis |
|---|---|---|---|---|---|---|
| `robo-cholecystectomy-srth` | — | `not_available` | — | — | — | `not_available` |
| `robo-clip-artery-first-srth` | — | `not_available` | — | — | — | `not_available` |
| `robo-clip-artery-third-srth` | — | `not_available` | — | — | — | `not_available` |
| `robo-cut-artery-srth` | — | `not_available` | — | — | — | `not_available` |

### LAIT

Evidence for every row in this section is `research/lait.md`, at the heading named by the point ID (LAIT has no per-point heading; see its Result section).

| point_id | `ai_cost_usd` | Basis | Date | Price row used | `human_cost_usd` | Human basis |
|---|---|---|---|---|---|---|
| `lang-lait-novel-opening-gpt54` | — | `not_available` | — | — | — | `not_available` |

### OpenAI Navier-Stokes

Evidence for every row in this section is `research/navier-stokes-openai.md`, at the heading named by the point ID.

| point_id | `ai_cost_usd` | Basis | Date | Price row used | `human_cost_usd` | Human basis |
|---|---|---|---|---|---|---|
| `reas-navier-stokes-openai` | — | `not_available` | — | — | — | `not_available` |

### Anthropic FLT

Evidence for every row in this section is `research/flt-anthropic.md`, at the heading named by the point ID.

| point_id | `ai_cost_usd` | Basis | Date | Price row used | `human_cost_usd` | Human basis |
|---|---|---|---|---|---|---|
| `reas-flt-lean-anthropic-internal` | — | `not_available` | — | — | — | `not_available` |

### MonoRace

Evidence for every row in this section is `research/monorace.md`, at the heading named by the point ID.

| point_id | `ai_cost_usd` | Basis | Date | Price row used | `human_cost_usd` | Human basis |
|---|---|---|---|---|---|---|
| `robo-drone-monorace` | — | `not_available` | — | — | — | `not_available` |

## Reproducing

The per-row derivation for every point, including the token decomposition that went into each `list_price` figure, is the `derivation` column of `claude-rows-backfill.csv`. Re-applying the backfill is a join on `point_id` into the five columns; no other column is touched.
