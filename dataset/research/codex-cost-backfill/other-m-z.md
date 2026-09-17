# Codex cost backfill — non-GDPval/METR/Epoch/Cost-of-Pass rows, point_id m–z and digits

*Created 2026-09-13 14:29.*

## TL;DR

139 Codex-built rows are keyed in `other-m-z.csv`. **47 carry an AI dollar figure: 31 `reported` and 16 `list_price`; 92 are `not_available`.** The single largest find is that ARC Prize's released response files carry a per-attempt `metadata.cost` block, so 26 of the 30 ARC rows get a `reported` cost recomputed under the same human-observation weighting the dataset uses for tokens — the recomputed token means reproduce `points.csv` to the last digit, which is what verifies the weighting. Andon Labs states a per-run `mean_cost` for all four Vending-Bench 2 rows, and SketchAgent states $0.05 per sketch. **Exactly one human cost is recoverable:** Zhang et al. pay freelance writers $4 per article summarized, matching `writing-news-summary-textdavinci002`'s unit exactly. Every other paid human study in scope (H-ARC, ARC-AGI-2 testing, Noy–Zhang, Simulating Human Memory) pays a session fee covering several tasks, so nothing isolates to one attempt.

The 92 `not_available` rows split into four reasons: never-API-served models (CNNs, robots, classical OCR, research checkpoints), self-hosted open weights, rows whose token workload is a first-principles allowance, and rows whose tokens are a tokenizer reconstruction of released text rather than a usage counter. The last group is a convention borrowed from the sibling `other-a-l.csv` so the merged column is internally consistent; the computed figure is preserved in each such row's `evidence` cell, so flipping any of them to `list_price` is a one-cell edit.

**Next action for the merge:** apply `other-m-z.csv` on `point_id`. The one judgement call worth a second look is flagged below (the two GPT-5.4 ARC rows).

## Counts

| `ai_cost_basis` | Rows |
|---|---:|
| reported | 31 |
| list_price | 16 |
| not_available | 92 |
| **Total** | **139** |

| `human_cost_basis` | Rows |
|---|---:|
| reported_payment | 1 |
| not_available | 138 |

## Rule applied

1. Source states a dollar amount above zero for this work unit → `reported`.
2. Otherwise, token counts exist **from the source's own usage counters or its released texts**, and the model had a published per-token list price in force on the run date → `list_price`, priced from `research/cost/list-prices.csv`.
3. Otherwise → `not_available`.

Step 2 prices only counts the source itself recorded, matching the convention `other-a-l.csv` adopted. Two kinds of count are therefore excluded:

- **First-principles allowances** — VCT's 4,550 positions, the Codeforces checkpoint's 20.9M, FairLocator's assumed 400 output tokens, OmniDocBench's ground-truth-length proxy, the constructed GPT-4o audio minute, the assumed ImageNet text share.
- **Tokenizer reconstructions of released text** — Natural Plan, the book name cloze, and the freelance news summaries, whose prompts and responses are released but whose usage counters are not. Where only part of a workload is reconstructed, that part is dropped from the figure and named in `evidence` rather than making the whole row blank; this affects the four LRM rows, whose reconstructed input is 1.3–1.7% of the priced total.

## Per-study notes

### ARC-AGI (30 rows, 26 `reported`)

The five ARC source tranches (`arc`, `arc-settings`, `arc-expansion`, `arc-v1`, `arc-v1-expansion`, `arc-modern`) all retain ARC Prize's harness output, and every attempt's `metadata` carries `cost: {prompt_cost, completion_cost, reasoning_cost, total_cost}`. Cost is summed over the point's retained attempts per test case and averaged with the same weights the research notes use: H-ARC timed-session counts per task for the v1 rows, included human view counts per task-test pair for the v2 rows. Recomputing `tokens` under those weights reproduces the `points.csv` value exactly for all 30 rows, which is the check that the cost weighting matches.

The harness prices at published list rates — `reas-arcagi-v1-sonnet45-32k` recomputes to $0.419911, and 9,582 input plus 26,078 output tokens at Anthropic's $3/$15 is $0.41991 — so `reported` and `list_price` would agree here anyway. `reported` is used because the figure is in the source.

Four rows have `total_cost` exported as 0.00 on every attempt and are `not_available`:

| Row | Why zero | Tokens exist? |
|---|---|---|
| `reas-arcagi-v1-gpt54-high` | run under the pre-release alias `galapagos-alpha`, 2026-02-27 | yes — $0.249653 at the 2026-03-05 sheet |
| `reas-arcagi-v2-gpt54-high` | same | yes — $0.768960 at the 2026-03-05 sheet |
| `reas-arcagi-v1-gemini3dt` | Deep Think preview, Ultra-gated, never token-priced | no rate exists |
| `reas-arcagi-v2-gemini3dt` | same | no rate exists |

**The one call worth revisiting.** The two GPT-5.4 rows ran six days before GPT-5.4's public price sheet, so no rate was in force on the run date and they are left blank. The figures above are computed under the same weighting and are in the CSV's evidence column, so flipping them to `list_price` at `ai_cost_date` 2026-03-05 is a one-cell edit if you prefer a post-hoc price to a blank.

`ai_cost_date` is each config's modal run date from the retained `start_timestamp` fields. Several are pre-release evaluations (GPT-5.2 runs are dated 4–8 December against an 11 December release); that qualification is already in the dataset's notes.

### Vending-Bench 2 (4 rows, `reported`)

The retained report module `v2-token-cost-data.json` carries `mean_cost`, `min_cost`, `max_cost` and the price per Mtok Andon used, per model: $339.57 (GPT-5.6 Sol, 5 runs), $682.37 (Opus 4.6, 5), $558.60 (Opus 4.7, 6), $555.00 (Opus 5, 6). Same run-mean unit as `compute_flops`. Andon priced GPT-5.6 Sol at $5/$30 per Mtok, above the $4/$20 list sheet — the reported figure is kept as stated. Andon gives no run dates, so `ai_cost_date` is the 2026-09-12 report snapshot.

### SketchAgent (1 row, `reported`)

The CVPR 2025 supplement states an average API cost of $0.05 per sketch, which is the row's own work unit; the dataset already inverts that figure to recover output tokens, so using it as the cost is self-consistent. No run date is stated, so the date is the June 2024 Claude 3.5 Sonnet price sheet the paper itself prices against.

### Max Woolf strawberry (10 rows, `list_price`)

100 fresh OpenRouter calls per model on 2025-08-10, with native prompt and completion counts retained per call; the row is their mean. Priced at each model's first-party sheet in force that day. Two caveats in the evidence column: OpenRouter's routed upstream provider is not retained, and the two gpt-oss rows use the Together serverless rate because no first-party gpt-oss sheet exists. Gemini 2.5 Flash is at its GA rate, not the preview split thinking rate — correct for an August run.

### LRM Token Economy (4 rows, `list_price`)

Native `completion_tokens` for five calls each, priced at the output rate; reasoning already sits inside that counter. Native input counters were not saved, so the note's tiktoken reconstruction of the fixed prompt is excluded and named in `evidence` — it would add 1.3–1.7%. GPT-5 runs 2025-08-23, o3-mini runs 2025-07-23 (after the o3-mini sheet took effect, so no price-change trap).

### 16x Eval (2 rows, `list_price`)

The public export retains the run's own counters — 687 input for both, 374 Sonnet / 398 Opus output, reasoning zero — with the Anthropic provider and a 2025-07-17 run date.

### Natural Plan, book name cloze, freelance news summaries (3 rows, `not_available`)

All three release the actual prompts and responses, and the dataset counts them with the provider's own tokenizer — but none releases usage counters, so under the convention above they stay blank. The computed figures are in each row's `evidence` cell if the merge wants them: $0.008371 for Natural Plan at the 2024-05-23 Gemini 1.5 Pro sheet (the 2,249-token prompt is under the 128k boundary, so the short tier applies), $0.006279 for the GPT-4 book cloze at the 2023-03-14 sheet, $0.021192 for the news summaries at text-davinci-002's single $20/Mtok usage rate.

### Human cost

`writing-news-summary-textdavinci002` is the only fill (its AI side is blank, but the human side is independent): Zhang et al. §4.1, "we pay our writers $4 for every article they summarize", the same unit as `human_time`. The near misses, all left `not_available` with the figures recorded in the evidence column:

| Study | Reported payment | Why it does not isolate |
|---|---|---|
| Noy–Zhang | $10 base + $1 per grade point per essay (max $14); $18.3 mean total | base covers the whole survey; two writing tasks per participant |
| H-ARC (ARC-AGI-1 human) | $10 compensation + $1 bonus for one randomly selected task | flat fee over ~4.3 tasks per participant |
| ARC-AGI-2 human testing | $115–150 per 90-minute session + $5 per correct task | base unallocatable; $5 is conditional on success, and the time statistic is over all views |
| Simulating Human Memory | $20 flat for a one-hour session | ten tasks per participant |
| VCT | $5 per question + $25 correct-answer bonus | paid to the **non-expert** vetting cohort, not the expert baseliners who supply the 22.6% |
| GSM-Identity | £9/hour | an hourly wage, which the spec bars as a cost basis |
| SketchAgent | $0.50 per MTurk test session | paid to the 2AFC judges, not the QuickDraw drawers |
| DeepSeek-Prover human workflows | $240 for ~12 hours | study-level, not per theorem |

### The 92 `not_available` AI rows

| Reason | Rows |
|---|---:|
| Never sold through a per-token API (CNNs, detectors, robots, classical OCR, AlphaCode, Minerva, DAVE-2, circuit training, GECToR) | 45 |
| Tokens are a tokenizer reconstruction, not a usage counter (Natural Plan, book name cloze, news summaries) | 3 |
| Self-hosted, unhosted, or served through an unidentified wrapper (implicit-CoT GPT-2 fine-tunes, RULER vLLM, OpenVLA, RetroDFM-R, DeepSeek-Prover-V2, Qwen2.5-Math, the Llama-2 fine-tune, the 405B reconstructions, the Llama-3-8B memory rows) | 20 |
| Free ChatGPT web preview, never token-metered (Noy–Zhang ×10, ChatGPT GEC) | 11 |
| Whisper: API-served but billed per audio minute, and these rows are local operation counts | 3 |
| Token workload is a first-principles allowance, not a usage counter (VCT, Codeforces checkpoint, OmniDocBench, FairLocator, ImageNet GPT-4o, GPT-4o audio) | 6 |
| ARC rows with zero exported cost and no rate in force | 4 |
| **Total** | **92** |
