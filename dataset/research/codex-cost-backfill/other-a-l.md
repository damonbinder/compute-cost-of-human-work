# Codex-row cost backfill: non-GDPval/METR/Epoch/Cost-of-Pass rows, point_id a-l

*Created 2026-09-13 14:27.*

## TL;DR

108 Codex rows are in scope (every `points.csv` row whose `source_dataset` is not GDPval, METR,
Epoch AI or Cost-of-Pass and whose `point_id` starts with a-l). **22 carry an observed AI cost: 2
`reported` and 20 `list_price`. The other 86 are `not_available`**, and the reason is structural
rather than a research gap — 71 of them run a model that was never sold per token or that the source
self-hosted, and 15 run an API model whose token counts the source never published, so the row's
`tokens` value is a reconstruction rather than a usage counter. **No row in scope has a human cost**:
only Better Call GPT publishes a dollar figure for the human ($74.26 per contract for a junior
lawyer) and its own Section 4.2.3 says that figure was computed from average time and an hourly
rate, which `COLUMNS.md` excludes. The whole priced set totals $163.51, and 87% of that is four AI
Village website builds; the twelve Lyptus cyber tasks together cost $2.01.

`other-a-l.csv` carries point_id, ai_cost_usd, ai_cost_basis, ai_cost_date, human_cost_usd,
human_cost_basis, evidence. **Next action: merge the CSV into the root `points.csv` cost columns by
point_id.** Nothing in the Codex dataset was written.

## Counts by basis

| ai_cost_basis | Rows |
|---|---:|
| reported | 2 |
| list_price | 20 |
| not_available | 86 |
| **Total** | **108** |

| human_cost_basis | Rows |
|---|---:|
| not_available | 108 |

## The 22 priced rows

| point_id | ai_cost_usd | basis | date | Model |
|---|---:|---|---|---|
| agen-village-opus41-benefits-screener | 107.431237 | list_price | 2025-10-22 | claude-opus-4-1 |
| agen-village-opus41-connections-prototype | 19.133966 | list_price | 2025-11-03 | claude-opus-4-1 |
| agen-village-web-opus41-first-deployment | 16.585767 | list_price | 2025-10-13 | claude-opus-4-1 |
| agen-village-claude37-first-own-site | 11.672873 | list_price | 2025-10-13 | claude-3-7-sonnet |
| agen-village-web-sonnet45-first-deployment | 3.778199 | list_price | 2025-10-13 | claude-sonnet-4-5 |
| agen-village-gemini25-first-website | 1.185962 | list_price | 2025-10-13 | gemini-2.5-pro-preview-06-05 |
| agen-work-agentcompany | 0.678847 | list_price | 2025-05-09 | claude-3-7-sonnet |
| cyber-lyptus-glacier-exchange-gemini25pro | 0.660746 | list_price | 2026-03-17 | gemini-2.5-pro |
| agen-osworld | 0.660435 | list_price | 2025-10-30 | claude-sonnet-4-5 |
| cyber-lyptus-flatbuffers-opus46 | 0.578707 | list_price | 2026-03-13 | claude-opus-4-6 |
| cyber-lyptus-back-to-past-gemini25pro | 0.294486 | list_price | 2026-03-17 | gemini-2.5-pro |
| lang-work-contract-review-gpt4-1106 | 0.25 | reported | 2023-11-06 | gpt-4-1106-preview |
| cyber-lyptus-locktalk-gemini25pro | 0.169422 | list_price | 2026-03-17 | gemini-2.5-pro |
| cyber-lyptus-kill-pcap-gpt4o | 0.167 | list_price | 2026-03-27 | gpt-4o-2024-08-06 |
| agen-work-tau2-telecom | 0.109957 | reported | 2025-06-04 | gpt-4.1-2025-04-14 |
| cyber-lyptus-keygenme-gpt4o | 0.05306 | list_price | 2026-03-27 | gpt-4o-2024-08-06 |
| cyber-lyptus-stock-management-sonnet46 | 0.029472 | list_price | 2026-03-20 | claude-sonnet-4-6 |
| cyber-lyptus-flag-command-gemini25pro | 0.027416 | list_price | 2026-03-17 | gemini-2.5-pro |
| cyber-lyptus-packedaway-gemini25pro | 0.017634 | list_price | 2026-03-17 | gemini-2.5-pro |
| cyber-lyptus-lootstash-gemini25pro | 0.008188 | list_price | 2026-03-17 | gemini-2.5-pro |
| cyber-lyptus-cal-latex-opus3 | 0.00783 | list_price | 2026-03-16 | claude-3-opus-20240229 |
| cyber-lyptus-password-strings-opus3 | 0.006525 | list_price | 2026-03-15 | claude-3-opus-20240229 |

## Conventions applied

- **Only counters the source itself records are priced.** Where a row's `compute_flops` includes a
  reconstructed component — an inferred consolidation call, a timeout allowance for a missing helper
  invocation, a tokenizer-proxy reconstruction of a prompt — that component is left out of the
  dollar figure and the CSV's `evidence` cell names it. This is what keeps the column observed-only,
  and it means a few AI Village figures are a small understatement rather than an estimate.
- **Cache reads are priced, not excluded.** The dataset's FLOP term drops cache reads; cost must not,
  and on the cache-heavy agent rows the reads are the largest single line (7.1M read positions on the
  benefits screener, 6.6M on the Claude 3.7 site build). Anthropic's cache write is charged at 1.25x
  base input; Google's and OpenAI's writes are free.
- **Reasoning tokens sit inside the output counter** on every model priced here and bill at the
  output rate. No row in scope uses Gemini 2.5 Flash Preview or a Qwen line, the two places where
  that would be wrong.
- **No call in any priced row exceeded a 200k prompt**, so no Google or Anthropic long-context tier
  applies; every figure is the standard tier, not batch.
- **The Codex CLI helper reports a blended counter** (non-cached input plus output) that cannot be
  decomposed. Those tokens are priced at the GPT-5 input rate, which is the lower bound; each
  affected `evidence` cell states what the output-rate upper bound would add. The largest such gap
  is $0.90 on an $11.67 row.

## Per-study notes

**AI Village website builds (6 rows, 5 priced, $159.79 combined).** The public replay export carries
native Anthropic and Gemini per-call usage — ordinary input, cache creation, cache read and output —
so these price cleanly despite the rows' heavy image-position estimation, because images bill as
input tokens and the native counters already contain them. Opus 4.1's rates dominate: the benefits
screener alone is $107 on 3.3M fresh input, 1.5M cache creation and 7.1M cache reads. The estimated
per-session consolidation/summary call and the reconstructed Codex helper inputs (marked `assumed` in
`village-expansion/calculations.json`) are excluded. `agen-village-gpt5-first-site` is the one
exception in this group: only 72 of its 201 calls have native OpenAI counters, none carries a cache
decomposition, and the other 129 responses are interpolated, so there is no observed total to price.

**Lyptus offensive cyber (12 rows, all priced, $2.01 combined).** `calculations.json` retains every
provider usage field per call, including `inference_geo` and `service_tier` (both standard/global),
so these are the cleanest list-price rows in the set. Run dates come from the eval-log filenames;
FlatBuffers alone has an undated `full.eval`, and its header's `created` field gives 2026-03-13. The
study reports no per-task dollar cost and pays its expert pool partly in volunteer time, so neither
side has a reported figure.

**tau2-bench telecom (reported).** The release file stores `agent_cost` per simulation. Summing the
456 worker runs gives $50.140428, so the mean is $0.1099571 — the same unit and statistic as
`compute_flops`, and the same figure the research note inverts to recover the cached-token counter.
The user-simulator cost ($0.0864364 mean) is environment, not worker, and is excluded exactly as its
compute is.

**tau-bench retail (not_available).** The released Sonnet trajectories carry a `user_cost` for the
simulator but no agent cost and no usage counters at all; the 78,464-token mean is a cl100k
reconstruction, so there is nothing observed to price.

**Better Call GPT contract review (reported, $0.25).** Table 5's mean API cost per contract is the
row's primary observation — its 18,000-token count is inverted from this dollar figure, not the other
way round. The date is the 2023-11-06 gpt-4-1106-preview launch sheet whose $10/$30 rates the
authors used; the run date is unpublished. **Flag for Damon:** the same table gives $74.26 per
document for a junior lawyer, the exact population and unit of this row's `human_time`. I left
`human_cost_usd` blank because Section 4.2.3 says the figure was computed from average time and an
hourly rate from a compensation survey, and `COLUMNS.md` says human cost is never derived from time
and a wage. If that clause is meant to bind only our own derivations, this row should read 74.26 /
`reported_payment`.

**TheAgentCompany and OSWorld.** Both retain native provider usage in the released trajectory
(LiteLLM records for OpenHands, Bedrock runtime records for OSWorld), so both price directly. The
OpenHands run is almost entirely cache reads — 1,159,432 of 1,159,590 prompt positions — which is why
$0.68 buys 1.2M positions. OSWorld's Bedrock run has zero cache counters; it is priced at Anthropic
first-party standard rates, and a Bedrock regional endpoint would add about 10%.

**Pokémon Crystal (not_available).** Joel Zhang reports 24,178 turns and 1.88 billion tokens but as a
single combined figure, with no input/output split, no cache decomposition and no dollar amount. On
the Gemini 3 Pro sheet the same 1.88B prices anywhere between roughly $3,800 (all input) and $22,600
(all output), so no defensible figure exists.

**Reconstructed-token API rows (12 of the 15, all not_available).** SpreadsheetBench, TravelPlanner/SCOPE,
BooookScore, Karvonen's GPT-3.5 chess, MLE-bench/Operand, the four TaxCalcBench rows, the GPT-4 USMLE
row and the GPT-3 davinci MMLU row all run a model that had a list price, but none of their releases
retains a usage counter. Each row's `tokens` value is a tokenizer-proxy reconstruction plus an
assumed completion length, so pricing it would price an estimate. TaxCalcBench is the sharpest case:
its runner saves only `response.choices[0].message.content` and discards usage, cache counters and
timestamps.

**Never-API-served and self-hosted rows (71, all not_available).** Two groups. The RL and
task-specific models — DQN, MuZero, EfficientZero, AlphaZero, AlphaGo Zero, AlphaStar, OpenAI Five,
GT Sophy, ACT ALOHA, Maia, Stockfish, the searchless chess transformer, the FAIR negotiator, the
Berkeley crossword solver, the binary64 converter, BERT on SQuAD, R2BERT, PEGASUS, mBART-50 on
DivEMT, Microsoft's 2018 WMT system and PaLM 540B — were never sold through a per-token API. The
open-weight checkpoints — Latxa, Swallow, AceGPT, Llammas, Code Llama, Kexer, MultiPL-T StarCoder,
RoBERTa, Llama 2 70B, NLLB, Llama 3.1 8B/405B, the BabyLM entrants and the 2021 Codex research models
— were run by the source on its own hardware, and most of those rows are training runs, which no
provider sells per token at all. Three GRE, MBE and MMLU rows use pre-release GPT-4 snapshots that were never sold on the API, so the
public `gpt-4` rate is not theirs. Two products are in neither group but still unpriceable: the free
December 2022 ChatGPT web preview was not token-metered, and GitHub Copilot in 2022 was a seat
subscription with no per-completion charge.

## Sources read

- Spec: `claude-rows/COLUMNS.md` cost rows, `claude-rows/DECISIONS.md` "Cost columns".
- Rates: `claude-rows/research/cost/list-prices.csv` and `list-prices.md`.
- Codex evidence (read-only): `dataset/points.csv`, and under `dataset/research/` the notes and
  `calculations.json` files for agent-operations, village-expansion, village-websites-remaining,
  village-gpt5-first-site, cyber-timings, cybench-expansion, workplace-agents, agent-benchmarks,
  spreadsheetbench, contract-review, pokemon-agents, gpt35-chess, mlebench, taxcalcbench,
  exams-knowledge, book-coherence, executive-memory, blimp-learning, divemt, squad, negotiation.
- Codex sources (read-only): `dataset/sources/workplace-agents/tau2-telecom.json` and
  `tau-sonnet-retail.json`, `dataset/sources/contract-review/paper.pdf`,
  `dataset/sources/cyber-timings/article.html` and `.../eval-set-9garycpkytw2ae95/full.eval`,
  `dataset/sources/pokemon-agents/gemini-crystal.html`.
