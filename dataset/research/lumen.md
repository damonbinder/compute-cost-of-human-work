# LUMEN — automated systematic review and meta-analysis (arXiv 2606.28362)

*Created 2026-09-13 10:58.*
*Last revised 2026-09-13 11:52, after the independent review at `reviews/lumen-independent.md`
and the coordinator's recheck.*

## Summary

Five candidate rows, one per LUMEN domain review, at **8.62e17 to 1.17e18 FLOPs** against
**905 to 1,463 human active hours** (3.26e6 to 5.27e6 seconds), i.e. 1.7e11 to 3.2e11 FLOPs per
human-second. Compute comes from the paper's per-phase median token counts (Table S1)
distributed across the five reviews by their published per-phase dollars (Table 3), with each
phase's routed models supplying the FLOPs-per-token coefficient. Human time comes from the
Allen & Olkin (1999) regression of meta-analysis active hours on citations retrieved, applied to
each review's own search yield; person-years anywhere in this note convert at 2,000 active hours
per `DECISIONS.md`. Performance is **`below` for D1, D2 and D4, `match` for D3 and D5**,
following the paper's own grouping of the domains by divergence from the reference review.

Three things a reviewer should look at first:

1. **The paper's tokens and its dollars do not reconcile.** At March 2026 list prices the
   published token counts imply a $16.35 bill against a reported $23.51; the whole gap is in
   title–abstract screening, at 2.06×. Only one of the three candidate explanations survives
   contact with the paper's own numbers, and it would raise every row's compute by 1.1× to 1.9×.
2. **D3's screening cost is a sevenfold outlier** ($0.0013 per record against $0.0052 in the
   other four runs and $0.0096 in the repository's own pilot), which is what makes D3 the
   cheapest and lowest-compute row.
3. **The human baseline is a transfer from 37 commercial meta-analyses of the 1990s**, and D5's
   search yield sits close to the point where the fitted quadratic turns over.

Point IDs: `agen-lumen-d1-gemini31pro` through `agen-lumen-d5-gemini31pro`. One new model
record, `gemini-3.1-flash-lite-preview`, in `candidates/lumen/models.csv`.

---

## Source and what it actually publishes

Huang Y-H, Lin Y-S. *LUMEN: Cost-Transparent Multi-Agent Pipeline for Automated Systematic
Review and Meta-Analysis.* arXiv:2606.28362v1 [cs.IR], stamped 29 March 2026. Retained at
`agent-work/sources/lumen/lumen-arxiv-2606.28362v1-text.txt`; every value used is transcribed into
`agent-work/sources/lumen/lumen-source-values.json` with its table of origin. Provenance for all retained
files is `agent-work/sources/lumen/MANIFEST.md`.

Reported, and used here:

- **Table 2** — per review: search yield, records screened after deduplication and keyword
  pre-screen, studies included, and the published meta-analysis used as ground truth.
- **Table 3** — per review, per phase: US dollars. Five phase groups plus a total.
- **Table S1** — per phase: the **median** across the five runs of API calls, input tokens,
  output tokens and wall-clock minutes. Ranges are given for calls only.
- **Table S3** — per review, per screener: the five-point score distribution. This is the
  per-review workload evidence for the dominant phase; see below.
- **Table 1** — the 11-agent inventory with the model routed to each agent.
- **Table S2** — per review: dual-screener agreement, arbiter invocations, human-review queue.
- **Tables 5, S4, S5** — the extraction ablation, per-analysis results and the complete Phase 5
  meta-analysis output.

Not reported, and therefore derived or assumed here:

- **Per-review token counts.** Only the five-run medians exist. Per-review *call* counts for
  screening are recoverable from Table S3, and per-review dollars are published.
- **Per-model token splits within a phase.** Only the routing is stated.
- **The prices actually paid.** Section 2.1 gives three figures; two conflict with list prices.
- **Any human-time measurement.** The paper's only human anchor is Borah's 67-week calendar
  median, which is elapsed time, not active time.

**The public cost logs do not exist.** Section 2.2 and the abstract both state that all cost
logs are in the public repository. The complete tree of `YHHuan/LUMEN` on 2026-09-13
(`agent-work/sources/lumen/lumen-repo-tree-2026-09-13.txt`) holds `configs/`, `lumen/`, `prompts/`,
`tests/` and four top-level files. There is no data, projects or logs directory. Worse for
verification purposes, the repository is a **later and different system**: its README is headed
"LUMEN v3", it describes 9 agents rather than 11, binary screening with a 0–100 confidence
rather than a five-point scale, 4-round extraction rather than three-pass, and a model roster of
Gemini 2.5 Flash / Claude Sonnet 4.5 / Claude Opus 4.1 through OpenRouter rather than the
paper's Gemini 3.1 Pro / GPT-4.1 Mini / Claude Sonnet 4.6 / GPT-5.4. The rows below use the
paper's configuration throughout. The repository contributes two things: `lumen/core/cost.py`
shows each logged call carries `calls`, `input_tokens`, `output_tokens` and `cost` and nothing
else, which fixes the token accounting; and the README's `met_ovary` pilot table
(`agent-work/sources/lumen/lumen-repo-readme-v3.md`) is the only independent same-family token/call/dollar
triple in existence — 937 candidate studies, ~1,876 screening calls, ~3.7M screening tokens,
~$9.0, i.e. **2.00 calls and $0.0096 per record screened, and ~1,972 input tokens per screening
call**. It is used below as a cross-check on both the call-count derivation and the D3 outlier.

### Internal inconsistencies found in the paper

Recorded because they bear on how much weight the numbers carry.

| Inconsistency | Detail |
|---|---|
| **Screening call count** | Table S1's P3.1 median of 2,352 calls is refuted by Table S3 (next section) and by its own reported range maximum of 7,520. The derived median is 7,520. |
| **Poolable analyses** | Table 5 gives 6 / 4 / 11 / 6 / 7 Arm A analyses, 34 in total. The per-analysis listings in Tables S4 and S5 give 5 / 4 / 6 / 5 / 7, 27 in total. D3 is off by five. The rows use the supplement's counts, since those are the analyses actually enumerated. |
| Total API calls | Table S1's caption gives ~27,430 calls across the five runs. The derived screening counts alone sum to 35,143. The call total is not used in any row. |
| Wall-clock range | Results says 5.1–10.8 h; Discussion 4.1 says 3.5–10.8 h. Summing the Table S1 per-phase medians gives 339 min = 5.65 h. |
| D5 screening included | Table S2's "Included" column is blank for D5 alone. |
| D4 screening included | Table S2 gives 45 studies passing title–abstract screening for D4, but Table 2 gives 49 finally included. Full-text screening cannot add studies. |
| Table 3 "Other" vs Table 1 | "Other" is defined as Strategy + Pre-screen + Planning + Quality, but the 11-agent inventory contains no quality-assessment agent, so no model is named for the RoB-2/GRADE work. |
| Stated prices | Section 2.1's "$0.40–$1.25/M input" for the high-volume models and "$2.00/M" for GPT-5.4 do not match list prices for Gemini 3.1 Pro ($2.00) or GPT-5.4 ($2.50). See `agent-work/sources/lumen/model-pricing-2026-03.md`. |

One further oddity, not an inconsistency in the numbers: 2606.28362 is a June 2026 arXiv
identifier while the paper stamps itself 29 March 2026. Nothing here depends on it — the run
window is independently fixed by the paper's own "March 2026 model versions/pricing" — but both
are cited without remark in the paper itself.

---

## The screening call count, and what it fixes

Table S3 publishes, per domain and per screener, how many records received each of the five
relevance scores. **Both screeners' columns sum to exactly the Table 2 screened count in all
five domains**:

| Domain | Screener 1 sum | Screener 2 sum | Table 2 screened | Arbiter (Table S2) | Derived calls |
|---|---|---|---|---|---|
| D1 | 3,756 | 3,756 | 3,756 | 8 | 7,520 |
| D2 | 3,172 | 3,172 | 3,172 | 5 | 6,349 |
| D3 | 4,334 | 4,334 | 4,334 | 70 | 8,738 |
| D4 | 1,389 | 1,389 | 1,389 | 26 | 2,804 |
| D5 | 4,839 | 4,839 | 4,839 | 54 | 9,732 |

So each screener made one call per screened record and the median run made
2 × 3,756 + 8 = **7,520** screening calls, which is exactly the maximum of Table S1's own
reported P3.1 range. The `met_ovary` pilot confirms the design independently at 2.00 calls per
candidate. Table S1's P3.1 median of 2,352 cannot be right and is not used.

Two consequences:

- **Mean input tokens per screening call is 5,160,000 ÷ 7,520 = 686**, or **1,372** if Table
  S1's P3.1 row is per-screener rather than per-phase. It is not 2,194, which an earlier draft
  of this note carried in one place and contradicted in another.
- The cached-context attention scenario, which scales with context length, drops accordingly
  (below).

`compute_flops` itself does not move: the call count never entered the token allocation.
`calculations.json` uses the derived count wherever a call count is consumed, and retains Table
S1's reported 2,352 beside it under `calls_reported_tableS1` with its status, so the discrepancy
stays visible rather than being silently dropped.

## Work unit

One row is **one complete LUMEN run on one clinical question**: the six phases the paper
automates end to end — Phase 1 search-strategy generation from a PICO question, Phase 2 search
of PubMed, Scopus, OpenAlex and Europe PMC with deduplication and a keyword pre-screen rescue
pass, Phase 3.1 dual-model five-point title–abstract screening with arbitration, Phase 3.3
full-text PICO verification against retrieved PDFs, Phase 4 three-pass structured extraction
with evidence spans and tiebreaking, Phase 4.5 analysis planning, Phase 5 REML random-effects
meta-analysis with Knapp–Hartung adjustment executed deterministically in R `metafor`,
automated RoB-2/ROBINS-I and GRADE assessment, and Phase 6 a citation-grounded manuscript
draft. Completion is the produced draft with its pooled estimates. Zero retries and zero
failures are reported for all five runs.

**The human equivalent deliverable is a published systematic review and meta-analysis on the
same clinical question** — the kind of document each of the five comparison references is. That
is a wider unit than the AI run in two directions and narrower in none:

- LUMEN does not define or refine the PICO question (limitation 4: "PICO specification resists
  full automation"), does not recode or subgroup outcomes, does not interpret heterogeneity, and
  its draft is not peer-reviewed. The authors' own verdict, section 4.7: what $20 buys "is not a
  finished meta-analysis but a structured, auditable starting point".
- The human-hours model used below covers a complete meta-analysis project including project
  administration, which has no counterpart in the run.

Both directions are recorded as `different_task`. Phase 5 is deterministic R code rather than a
model call; its compute is not a token workload and is excluded, consistent with the paper
reporting no tokens for it. Table 3's P4 extraction cost is taken to be the production Arm A
only, not the Arm C and Arm D ablations that ran over the same corpora; the per-included-study
costs support that ($0.207 to $0.369, consistent with three passes rather than one plus two
ablations), but the paper does not say so.

## Model records

Four of the five routed models already exist in
`../AI Compute vs Human Time/dataset/models.csv` and are reused unchanged:

| Model | `model_id` | FLOPs/token |
|---|---|---|
| Claude Sonnet 4.6 | `claude-sonnet-4-6` | 2.0e11 |
| Gemini 3.1 Pro | `gemini-3.1-pro-preview` | 2.0e11 |
| GPT-4.1 Mini | `gpt-4.1-mini-2025-04-14` | 4.8e10 |
| GPT-5.4 | `gpt-5.4-2026-03-05` | 2.0e11 |

The paper gives no API version strings. `gemini-3.1-pro-preview` (released 2026-02-19) and
`gpt-5.4-2026-03-05` were the only releases of those names available in the stated March 2026
window; the `gemini-3.1-pro-preview-customtools` endpoint is not used because the paper
describes no custom tools.

The fifth, "Gemini Flash Lite", is new to the dataset and is added to
`candidates/lumen/models.csv` as `gemini-3.1-flash-lite-preview`, released 2026-03-03 per the
Gemini API changelog, at 20B active parameters (4.0e10 FLOPs/token). That is the dataset's own
shared small-tier assumption, carried by `o1-mini-2024-09-12`, `o3-mini-2025-01-31`,
`o4-mini-2025-04-16`, `claude-3-5-haiku-20241022`, `gpt-5-mini-2025-08-07` and
`grok-3-mini-beta`. It matters very little either way: the phase it serves carries 1.4% of
tokens, so even a factor-of-two error moves any row's `compute_flops` by under 0.5%.

`model_id` on every row is **`gemini-3.1-pro-preview`**, which carries the largest token
workload (about half of screening plus most of extraction, ~48% of the median run's tokens) and
the two phases the paper identifies as dominant. Claude Sonnet 4.6 carries more agents but ~9%
of tokens.

## Compute derivation

### Method

`compute_method = params_tokens`. For each phase, tokens × the token-weighted mean of the
routed models' `flops_per_token`:

| Phase | Routing (Table 1) | Token split | Effective FLOPs/token |
|---|---|---|---|
| P1 Strategy | Claude Sonnet 4.6 | 1.0 | 2.0e11 |
| P2.5 Pre-screen | Gemini Flash Lite | 1.0 | 4.0e10 |
| P3.1 T/A screening | Gemini 3.1 Pro, GPT-4.1 Mini, Sonnet 4.6 arbiter | 0.5 / 0.5 | 1.24e11 |
| P3.3 Full-text | Claude Sonnet 4.6 | 1.0 | 2.0e11 |
| P4 Extraction | Gemini 3.1 Pro, GPT-5.4 tiebreaker | 0.85 / 0.15 | 2.0e11 |
| P4.5 Planning | Claude Sonnet 4.6 | 1.0 | 2.0e11 |
| P6 Manuscript | Claude Sonnet 4.6 writer, GPT-5.4 guardian | 0.7 / 0.3 | 2.0e11 |
| Quality | assumed Claude Sonnet 4.6 | 1.0 | 2.0e11 |

Only P3.1 and P2.5 are sensitive to the split. In P4 and P6 both routed models carry 2.0e11, so
the assumed shares change nothing; they are recorded only for the dollar cross-check. The
Quality phase's model is unnamed in the paper; every plausible candidate on the high-judgment
tier carries 2.0e11.

**The P3.1 equal split is the design, not a guess**, and Table S3 now confirms it directly: both
screeners scored every record in every domain, so their input streams are the same text and
their token counts differ only by tokenizer. Arbitration ran on 5 to 70 records per run against
thousands screened, and Claude Sonnet 4.6 carries the same coefficient as Gemini 3.1 Pro, so
folding arbitration into the Gemini half is exact except for the small GPT-4.1 Mini share it
displaces. Moving the phase coefficient to its extremes (1.0e11 if the Mini screener's tokenizer
is materially more verbose, 1.32e11 if arbitration is 5% of phase tokens) moves a
screening-dominated row by roughly ±6%.

### Token accounting

`tokens_accounting = input_output`. The repository's `cost.py` records exactly `calls`,
`input_tokens`, `output_tokens` and `cost` per call, and section 2.2 describes the same
counters. No cache creation or cache read is logged, and cost is computed post hoc by
multiplying the two token counters by a flat per-model price, so no cache discount was applied.
There is no evidence that prompt caching was enabled. The recorded figure is therefore taken as
the full processed prefix on every call — the full-prefix assumption — with two known one-sided
risks: if Anthropic-side caching was on, `input_tokens` excludes cache reads and creation and
the true processed count is higher; if Google- or OpenAI-side caching was on, their counters
include cached reads that COLUMNS would remove from the parameter term and the count is an
overstatement. Neither is quantifiable from what is published.

### Distributing the published tokens across the five reviews

Table S1's token figures are **medians across the five runs**, not per-review values. Within a
Table 3 phase group the bill is a linear function of tokens at fixed per-model prices, so each
group's tokens are allocated across reviews in proportion to that group's published dollars,
anchored on the Table S1 median:

    tokens[group][review] = tokens_median[group] × cost[group][review] / median(cost[group][·])

and within a group, sub-phases keep their median token shares. Full arithmetic in
`research/lumen/lumen_calculations.py` → `agent-work/derived/lumen/calculations.json`. `tokens` in the CSV
is rounded to whole tokens and `human_time` to whole seconds; `compute_flops` is written at full
precision from the unrounded per-phase allocation, so `tokens` and `compute_flops` are not
exactly proportional.

**The allocation validates well on its own terms.** Screening tokens per record screened:

| Review | Screening tokens | Records screened | Tokens per record | USD per record |
|---|---|---|---|---|
| D1 | 6,605,700 | 3,756 | 1,759 | 0.0054 |
| D2 | 5,448,000 | 3,172 | 1,718 | 0.0053 |
| D3 | 1,845,204 | 4,334 | 426 | 0.0013 |
| D4 | 2,367,283 | 1,389 | 1,704 | 0.0053 |
| D5 | 8,107,143 | 4,839 | 1,675 | 0.0052 |

Four of five land within 5% of each other at about 1,700 tokens per record, or roughly 850 per
screener call — the right size for a prompt carrying full eligibility criteria plus a title and
abstract, and in the same range as the `met_ovary` pilot's ~1,972 per call. Nothing forced that
agreement: it falls out of dividing independently published dollars by independently published
record counts. Extraction behaves the same way, at 24,000 to 43,000 input tokens per included
study across three passes, against the v3 repository's 12,000-token PDF cap per pass.

### The alternative allocation, and why the dollars win

Table S3 supports a second, independent allocation: distribute screening tokens by the derived
call count rather than by dollars. This is a derived per-review quantity, not a hypothesis, and
it applies to all five rows:

| Review | Derived calls | Screening tokens by calls | By dollars | Row total vs recorded |
|---|---|---|---|---|
| D1 | 7,520 | 5,448,000 | 6,605,700 | 0.87× |
| D2 | 6,349 | 4,599,648 | 5,448,000 | 0.89× |
| D3 | 8,738 | 6,330,402 | 1,845,204 | 1.65× |
| D4 | 2,804 | 2,031,409 | 2,367,283 | 0.96× |
| D5 | 9,732 | 7,050,523 | 8,107,143 | 0.89× |

**The dollar allocation is kept as central**, for a reason that is about what each allocation can
see. Allocating by calls forces identical tokens per screened record across all five domains by
construction, so it cannot represent variation in record length — and record length plainly does
vary, since D3's corpus is pre-2000 surgical literature where many records carry no abstract at
all, which is the same property that cost D3 nine of fifteen ground-truth studies to PDF
unavailability. The dollars are review-specific, respond to content rather than to count, and
are internally consistent with Table 3's published per-review totals. Against that, the calls
allocation is exact about the one quantity it measures and the dollars are not measured tokens
at all. The honest statement is that the two agree within 11 to 13% on four of five rows and
disagree by 1.65× on D3, which is the same disagreement as the D3 cost outlier seen from the
other side.

**D3 is the largest per-review uncertainty in this set.** Its screening cost is $5.69 for 4,334
records, $0.0013 per record against $0.0052 in the other four runs and $0.0096 in the
repository's own pilot — a sevenfold outlier against the only independent observation — and the
paper's own sentence "screening cost scales linearly with deduplicated study count" does not
hold for it. Under the calls allocation D3's total rises from 8.62e17 to 1.418e18 FLOPs.

### The dollar cross-check fails in screening, and only one explanation survives

Predicting the bill from the published tokens, the published routing and March 2026 list prices
(`agent-work/sources/lumen/model-pricing-2026-03.md`):

| Phase group | Predicted USD | Reported median USD | Reported / predicted |
|---|---|---|---|
| P3.1 T/A screening | 8.15 | 16.80 | 2.06 |
| P4 Extraction | 5.11 | 3.72 | 0.73 |
| P3.3 Full-text | 1.52 | 1.19 | 0.78 |
| P6 Manuscript | 0.83 | 0.72 | 0.87 |
| Other | 0.74 | 1.08 | 1.46 |
| Total | 16.35 | 23.51 | 1.44 |

Every phase but screening agrees within 50%. Screening is out by a factor of two and is 71% of
the median bill, so it drives the 1.44× total. Three explanations are available and two are
decidable against the paper's own numbers:

1. **Table S1's P3.1 row is per-screener rather than per-phase.** Doubling it puts predicted
   screening at $16.30 against a reported $16.80 — a 3% fit — and the whole bill at $24.50
   against $23.51, a 4% fit. It also makes 1,372 rather than 686 input tokens per screening call,
   which is the more natural length for the described static-plus-dynamic prompt and is closer to
   the `met_ovary` pilot's ~1,972. **This is the surviving explanation.**
2. **The two tables' medians come from different runs.** This widens the gap rather than
   narrowing it. D1 (3,756 records) is the likely median-token run and D2 ($16.80) the
   median-cost run; pricing the Table S1 screening tokens against D1's own reported $20.37 gives
   **2.50×**, not 2.06×. Ruled out as an explanation.
3. **The prices are not the list prices.** A single wrong price table cannot make screening 2.06×
   low and extraction 1.37× high. For extraction the median-token and median-cost runs are the
   same run — Table S1's P4 median of 48 calls is exactly 3 × 16 included studies, which is D1,
   and D1's $3.72 is the median extraction cost — so there the list-price prediction *overshoots*.
   The paper's own stated prices push the wrong way too: its $1.25/M for Gemini would lower the
   prediction and widen the screening gap. Ruled out.

**`compute_flops` still uses the published tokens**, because they are a direct measurement, the
dollar route depends on prices the paper misstates for two of five models, and the dataset's
convention is to count processed tokens. But the evidence favours explanation 1, which means the
recorded values may be low by up to 1.9×, and every row's `notes` says so:

| Review | Recorded | Dollar-reconciled | Ratio |
|---|---|---|---|
| D1 | 1.067e18 | 1.883e18 | 1.76 |
| D2 | 9.460e17 | 1.602e18 | 1.69 |
| D3 | 8.619e17 | 9.622e17 | 1.12 |
| D4 | 9.996e17 | 1.151e18 | 1.15 |
| D5 | 1.173e18 | 2.212e18 | 1.88 |

### Cached-context attention

Per `DECISIONS.md`, `compute_flops` stays on the 2 × active_parameters convention and the omitted
attention term is quantified separately, at 4 · layers · d_model · n_context per processed token,
with n_context set to each phase's mean input length per call — using the **derived** screening
call count for P3.1. Those lengths are short: 686 tokens in screening, 11,146 in full-text
screening, 9,042 in extraction, 394 in manuscript writing. Across bracketing architectures
(64 layers × 8,192; 80 × 8,192; 96 × 12,288) the omitted term is:

| Review | Low | Central | High |
|---|---|---|---|
| D1 | 2.9% | 3.6% | 6.5% |
| D2 | 3.6% | 4.4% | 8.0% |
| D3 | 7.3% | 9.1% | 16.5% |
| D4 | 7.1% | 8.9% | 16.0% |
| D5 | 2.1% | 2.6% | 4.7% |

It is one-sided. This is a far smaller correction than the Portal row's 1.4–3.1× because nothing
in this pipeline re-reads a long context: the dominant phase sends one abstract at a time.

### Per-review results

| Review | Domain | Input tokens | Output tokens | Total tokens | compute_flops | Reported USD |
|---|---|---|---|---|---|---|
| D1 | Antidepressants in elderly | 7,134,379 | 752,210 | 7,886,588 | 1.067e18 | 26.10 |
| D2 | CBT-I for insomnia + depression | 6,161,417 | 669,179 | 6,830,596 | 9.460e17 | 22.51 |
| D3 | Laparoscopic vs open cholecystectomy | 4,034,348 | 1,062,313 | 5,096,661 | 8.619e17 | 19.51 |
| D4 | Pneumococcal vaccines | 4,785,694 | 1,201,573 | 5,987,267 | 9.996e17 | 22.65 |
| D5 | SGLT2i in heart failure | 8,258,766 | 767,043 | 9,025,809 | 1.173e18 | 29.04 |

For reference, the Table S1 median composite is 6.291M input + 713.2K output = 7.004M tokens and
9.712e17 FLOPs. No row is built on it: it is a sum of per-phase medians from five different runs,
not any run, and building a sixth row on it would double-count the same five runs.

## Human time

### What is available, and what is not

There is no measured person-time for producing any specific published systematic review, in the
Cochrane record or anywhere in this literature. Four bodies of evidence exist:

1. **Allen IE, Olkin I. JAMA 1999;282(7):634–635.** 37 meta-analyses conducted at MetaWorks, a
   commercial meta-analysis unit. Mean 1,139 total **active hours** summed across the project
   team — the quantity `human_time` wants — median 1,110, range 216 to 2,518.
   Crucially it publishes a regression of total hours on citations retrieved:
   **total hours = 721 + 0.243x − 0.0000123x²**, intercept 95% CI 478–964. Task categories:
   pre-analysis search, retrieval and database development 588 h (SD 337); statistical analysis
   144 h (SD 106); report and manuscript writing 206 h (SD 125); administrative 201 h (SD 193).
   Extract and checks in `agent-work/sources/lumen/allen-olkin-1999-extract.md`.
2. **Michelson M, Reuter K. Contemp Clin Trials Commun 2019;16:100443.** A labour model, not an
   observation: 1.72 scientist-years per review, built from five co-authors at 15 h/week for
   11 months. Under `DECISIONS.md`'s convention of 2,000 active hours to the person-year, that is
   **3,440 active hours**. The source's own 15 h/week is a less-than-full-time engagement, which
   the convention expresses as an on-task fraction rather than as a lower hours-per-year figure;
   converting at the source's implied 2,080 would give 3,578 instead.
3. **Borah R et al. BMJ Open 2017;7(2):e012545.** 67.3 weeks median from registration to
   publication across 195 reviews. This is the figure LUMEN's own abstract opens with, and it is
   elapsed calendar time across a team, not summed active time. It is **not** used, and no
   conversion from it is attempted.
4. **Bullers K et al. J Med Libr Assoc 2018;106(2):198–207.** Librarian time only: mean 30.7 h,
   median 22 h, n=105. A component, not a review.

### Choice

Allen & Olkin is used, through the regression rather than the flat mean, because its predictor —
citations retrieved before exclusion criteria — is the one review-specific quantity LUMEN
publishes for all five. JAMA's own wording is "the number of citations before exclusion criteria
are applied". Deduplication is not an exclusion criterion, but LUMEN's keyword pre-screen is, so
the matching count sits between Table 2 "Yield" (raw multi-database retrieval) and Table 2
"Screened" (after deduplication and pre-screen); the regression is evaluated at the midpoint of
that bracket. The regression then covers a whole MetaWorks project including 201 hours of
administration out of the 1,139-hour mean; the LUMEN run has no administrative counterpart, so
that share (17.6%) is removed. Both steps follow Damon's 2026-09-16 ruling that a known
over-attribution is corrected in the estimate rather than left as a flag; the earlier central
evaluated the regression at the raw yield with administration included.

| Review | Yield | Screened | Midpoint (x) | Regression hours | Excluding administration | Seconds (CSV) |
|---|---|---|---|---|---|---|
| D1 | 5,168 | 3,756 | 4,462.0 | 1,560 | 1,285 | 4,626,067 |
| D2 | 5,535 | 3,172 | 4,353.5 | 1,546 | 1,273 | 4,582,780 |
| D3 | 6,233 | 4,334 | 5,283.5 | 1,662 | 1,368 | 4,925,952 |
| D4 | 2,010 | 1,389 | 1,699.5 | 1,098 | 905 | 3,256,588 |
| D5 | 8,062 | 4,839 | 6,450.5 | 1,777 | 1,463 | 5,267,338 |

### Population, statistic and reasoning

The population is a qualified systematic-review team — `human_skill = expert`. The hours are
summed across the team for one project, which is what COLUMNS requires. `human_time_scope` is
`task_performance`.

`human_time_evidence = transferred_timings`: the durations are recorded timings, but for a
different set of tasks and a different population (37 MetaWorks meta-analyses of the 1990s, not
2020s reviews on these five clinical questions). `human_attempts = 37` counts the contributing
donor projects. `human_time_subset = all`: MetaWorks' 37 completed projects with no selection
among attempts. `human_time_method = estimated`, following the AGENTS.md rule that transfers to
a different population are estimated regardless of how mechanical the final arithmetic is.
`human_time_statistic = point_estimate`: the value is a regression prediction at one x, not the
average of a set of timings. This combination is the dataset's dominant pattern for transferred
timings — 69 of 81 existing rows use exactly `transferred_timings` / `estimated` /
`point_estimate` / `all`.

### Range and what would move it

| Variant, active hours | D1 | D2 | D3 | D4 | D5 | Basis |
|---|---|---|---|---|---|---|
| Central (midpoint, admin excluded) | 1,285 | 1,273 | 1,368 | 905 | 1,463 | Regression at the Yield–Screened midpoint, ×0.824 |
| Regression at Yield, admin included (former central) | 1,648 | 1,689 | 1,758 | 1,160 | 1,881 | Regression at Table 2 Yield |
| Deduplicated set instead | 1,460 | 1,368 | 1,543 | 1,035 | 1,609 | Regression at Table 2 Screened |
| Deduplicated set, admin excluded (the low) | 1,203 | 1,127 | 1,272 | 853 | 1,326 | Regression at Screened, ×0.824 |
| Regression at Yield, admin excluded | 1,357 | 1,391 | 1,448 | 955 | 1,549 | ×0.824, admin's 201/1,139 share |
| Michelson & Reuter model | 3,440 | 3,440 | 3,440 | 3,440 | 3,440 | 1.72 person-years × 2,000 active hours |

The central is not a floor. Deduplication is not an exclusion criterion, which is why the
central evaluates the regression at the Yield–Screened midpoint, but the reading in which
LUMEN's keyword pre-screen and its deduplication both count as exclusions is defensible and
it puts the human below the central. That reading is the low: the regression at the Screened
count with administration removed, 1,203, 1,127, 1,272, 853 and 1,326 active hours for D1 to
D5, 4,329,020, 4,055,832, 4,574,910, 3,067,867 and 4,769,800 seconds. `human_time_high`
stays at the Michelson & Reuter labour model, 3,440 hours, 12,384,000 seconds. Allen and
Olkin's intercept carries a 95% confidence interval of 478 to 964 against the fitted 721,
which would widen the low further; it is not carried.

Three cautions on the transfer:

- **Extrapolation.** The fitted quadratic turns over at x = 9,878 citations and must not be
  evaluated beyond it. D5 at 8,062 is 82% of the way there, and the range of x in the MetaWorks
  sample is not reported in the retrieved text. D5's hours are the least secure of the five;
  D4's, at x = 2,010 against a sample mean implying x ≈ 1,904, are the most secure.
- **Era.** MetaWorks worked before electronic full-text delivery, so retrieval was slower;
  against that, the modern expectation of dual independent screening of every record, formal
  risk-of-bias instruments and PRISMA reporting did not yet apply in full. The two effects push
  in opposite directions and neither is quantified here.
- **Scope.** The model covers a whole meta-analysis project, including protocol work that has
  no counterpart in the LUMEN run. Administration is removed from the central; protocol design
  and manuscript revision after review are not quantified and remain flagged as `different_task`.

## Performance

### What was assessed

Not a reproduction. LUMEN conducted its own review from a PICO question on each topic and then
compared its pooled estimates with a published meta-analysis on the same question
(`agent-work/sources/lumen/ground-truth-references.md` confirms all five references are genuine published
systematic reviews and meta-analyses on the stated topics). The assessment is therefore
directional and magnitude concordance of pooled effect estimates on the outcomes that happened
to be comparable — 13 across the five reviews, distributed 1 / 1 / 4 / 3 / 4 (Table 5, column
"GT (A)"). All 13 agreed directionally.

Study-set concordance is reported for one domain only: D3 lost 9 of 15 ground-truth studies to
PDF unavailability before 2000 (limitation 1). That **bounds** the overlap at six of fifteen; it
does not establish that the remaining six were included. No per-field extraction accuracy is
reported; limitation 6 says extraction was validated on poolability rather than per-field
accuracy, "precluding direct comparison with otto-SR's 93.1%". No conclusion-level agreement is
reported at all.

Poolable analysis counts use the supplement (Tables S4 and S5), which enumerate 5 / 4 / 6 / 5 / 7
= 27, not Table 5's headline 6 / 4 / 11 / 6 / 7 = 34. The I² ranges quoted in each row come from
the same enumerated analyses: D1 50.8–90.8%, D2 52.9–78.2%, D3 0–29.4%, D4 2.8–80.3%, D5
0–99.9% across all seven analyses but 0–0.7% across the four ground-truth-comparable ones.

### D5 verified independently

D5 is the only domain with published magnitudes, and they check out against the Lancet record
rather than only against the paper:

| Outcome | Vaduganathan 2022 | LUMEN (Table S5) | LUMEN k |
|---|---|---|---|
| CV death or HF hospitalization | 0.77 (0.72–0.82) | 0.777 | 6 |
| First HF hospitalization | 0.72 (0.67–0.78) | 0.724 | 7 |
| Cardiovascular death | 0.87 (0.79–0.95) | 0.877 | 5 |
| All-cause mortality | 0.92 (0.86–0.99) | 0.921 | 6 |

**A contamination caveat belongs with this result.** LUMEN pooled 5 to 7 studies per outcome
against the published review's 5 trials, and still reproduced all four point estimates to three
significant figures. The reference meta-analysis is itself an obvious hit for an
SGLT2i-in-heart-failure search, the pipeline's 11-study included list is not published, and
nothing in the paper excludes the reference or its derivatives from that list. Re-extraction of
the reference's own pooled estimates therefore cannot be ruled out. This is stated in D5's
`performance_evidence`.

### Labels, and the rule behind them

**Rule: where the paper itself groups the domains by divergence from the reference review, the
label follows the paper's grouping.** Section 3.1: "In heterogeneous domains (D1, D2, D4),
effect sizes agreed directionally but I² was higher". Section 4.3: "I² diverged most from ground
truth in heterogeneous outcome domains (D1, D2, D4) and least in homogeneous designs (D3, D5)."
That is a task-specific quality claim about these five runs, from the people who ran them, and
it is the best evidence available on the dimension that separates a usable synthesis from a
directionally-correct one.

| Review | Label | Basis |
|---|---|---|
| D1 | `below` | Paper's heterogeneous group; I² 50.8–90.8% against the reference |
| D2 | `below` | Paper's heterogeneous group; the reference's recoding of continuous sleep-quality scores into binary response categories is a judgment the pipeline cannot replicate, so its four analyses are not the reference's analyses |
| D3 | `match` | Paper's homogeneous group; 4/4 outcome directions, I² 0–29.4%, 6 poolable analyses |
| D4 | `below` | Paper's heterogeneous group; I² to 80.3%, higher than any of D1's |
| D5 | `match` | Paper's homogeneous group; 4/4 hazard ratios within 1%, I² 0–0.7% |

**The number of ground-truth-comparable outcomes is not used as a label input.** It measures how
much evidence exists, not how well the pipeline performed, and a thin but positive comparison is
weak evidence of `match`, not evidence of `below`. An earlier draft of these rows split D1
(`below`, 1 comparable outcome) from D4 (`match`, 3 comparable outcomes) on exactly that basis;
that was wrong, since D4's I² runs higher than any of D1's and the paper groups the two together.

`unknown` was considered for D1 and D2 and rejected: a comparison exists, and COLUMNS discourages
`unknown` where a usable comparison exists. No row is labelled `above`: speed is not in scope for
this field, and no quality dimension is reported on which LUMEN exceeded its reference.

### Comparison issues, on all five rows

Ordered task, inputs_or_tools, assessment, human_baseline, matching the order used by 1,401 of
the 1,410 existing dataset rows.

- `different_task` — LUMEN conducts its own review rather than reproducing the reference review's
  protocol, so the two include different study sets; and the run excludes PICO definition,
  outcome recoding, interpretation and peer review, while the human-hours model includes project
  administration.
- `different_inputs_or_tools` — LUMEN's full-text stage is limited to PDFs it can retrieve
  through automated acquisition, where a human team uses interlibrary loan and author contact.
  Documented magnitude exists for D3 only.
- `different_assessment` — concordance of pooled estimates on 1 to 4 outcomes per domain, against
  a published meta-analysis, with no per-field extraction accuracy, no conclusion-level agreement
  and no peer review.
- `different_human_baseline` — the timings come from 37 commercial meta-analysis projects of the
  1990s, a different population and era from the teams that wrote the five references.

---

## agen-lumen-d1-gemini31pro

Antidepressants for depression in older adults with dementia (Table 2 D1; ground truth Lenouvel
2024, PMID 39163819). Yield 5,168 → 3,756 screened → 16 included. Dual-screener κ = 0.74, PABAK
0.99, 8 arbiter invocations, 49 records queued for human review; 7,520 derived screening calls.
Five poolable analyses (Tables S4/S5) with I² 50.8–90.8%; one ground-truth-comparable outcome,
directionally in agreement. Total $26.10, the second most expensive run. Label `below` on the
paper's heterogeneous grouping.

Compute: screening 6.61M tokens (8.191e17 FLOPs), extraction 0.772M (1.544e17), full-text 0.259M
(5.177e16), manuscript 0.162M (3.239e16), other phases 0.088M (9.53e15). Total 7,886,588 tokens →
**1.067e18 FLOPs**. Dollar-reconciled scenario 1.883e18 (1.76×); calls-allocated 0.87×; omitted
attention 2.9–6.5%.

Human: regression at the Yield–Screened midpoint x = 4,462.0 gives 1,560.4 h; excluding the 17.6% administrative share, **1,285.0 h = 4,626,067 s** (formerly 1,648.3 h = 5,933,926 s, at the raw yield with administration included).

## agen-lumen-d2-gemini31pro

Cognitive behavioural therapy for insomnia in major depressive disorder with comorbid insomnia
(Table 2 D2; ground truth Furukawa 2024, PMID 39242039). Yield 5,535 → 3,172 screened → 10
included. κ = 0.76, PABAK 0.99, 5 arbiter invocations, 55 queued; 6,349 derived screening calls.
Four poolable analyses with I² 52.9–78.2%, one ground-truth-comparable outcome. Total $22.51.
This is the domain where the paper identifies the specific human judgment LUMEN could not
reproduce — the reference review's recoding of continuous sleep-quality scores into binary
>50%-improvement response categories. Label `below`.

Compute: screening 5.45M tokens (6.756e17), extraction 0.766M (1.532e17), full-text 0.467M
(9.334e16), manuscript 0.084M (1.681e16), other 0.066M (7.15e15). Total 6,830,596 tokens →
**9.460e17 FLOPs**. Dollar-reconciled 1.602e18 (1.69×); calls-allocated 0.89×; attention 3.6–8.0%.

Human: regression at the Yield–Screened midpoint x = 4,353.5 gives 1,545.8 h; excluding the 17.6% administrative share, **1,273.0 h = 4,582,780 s** (formerly 1,689.2 h = 6,081,046 s, at the raw yield with administration included).

## agen-lumen-d3-gemini31pro

Laparoscopic versus open cholecystectomy (Table 2 D3; ground truth Roy 2024, PMC11057899). Yield
6,233 → 4,334 screened → 46 included, the largest included set. κ = 0.73, PABAK 0.95, 70 arbiter
invocations, 296 queued; 8,738 derived screening calls. Six poolable analyses with I² 0–29.4%,
four ground-truth-comparable outcomes all matching in direction. Cheapest run at $19.51 despite
the most included studies, which is the paper's headline example of cost not predicting quality.
Label `match` on the paper's homogeneous grouping.

Two review-specific cautions. The screening cost is the sevenfold outlier discussed above, so
this row's compute is the least secure of the five on the low side; under the calls allocation it
would be 1.418e18 rather than 8.619e17. And nine of the reference review's fifteen studies were
unavailable as PDFs before 2000, so **at most** six of fifteen could overlap while LUMEN's own
set runs to 46 — directional agreement here is agreement between two substantially different
bodies of evidence.

Compute: screening 1.85M tokens (2.288e17), extraction 1.97M (3.943e17), full-text 0.945M
(1.890e17), manuscript 0.148M (2.952e16), other 0.187M (2.03e16). Total 5,096,661 tokens →
**8.619e17 FLOPs**. Dollar-reconciled 9.622e17 (1.12×); calls-allocated 1.65×; attention
7.3–16.5%.

Human: regression at the Yield–Screened midpoint x = 5,283.5 gives 1,661.5 h; excluding the 17.6% administrative share, **1,368.3 h = 4,925,952 s** (formerly 1,757.8 h = 6,327,938 s, at the raw yield with administration included).

## agen-lumen-d4-gemini31pro

Pneumococcal vaccine efficacy and effectiveness in adults (Table 2 D4; ground truth Farrar 2023,
PMID 37242402). Yield 2,010 → 1,389 screened → 49 included, the smallest corpus and the largest
included set. κ = 0.62, the lowest of the five, PABAK 0.94, 26 arbiter invocations, 51 queued;
2,804 derived screening calls. Five poolable analyses with I² 2.8–80.3% and pooled vaccine
effectiveness 38–54%, three ground-truth-comparable outcomes all agreeing in direction. Total
$22.65, exactly the reported median. Table S2 records 45 studies passing title–abstract screening
against Table 2's 49 finally included, which cannot both be right. Label `below` on the paper's
heterogeneous grouping — its I² runs higher than any of D1's, so it cannot sit on the other side
of the line from D1.

Compute: screening 2.37M tokens (2.935e17), extraction 2.21M (4.429e17), full-text 1.06M
(2.118e17), manuscript 0.152M (3.034e16), other 0.195M (2.11e16). Total 5,987,267 tokens →
**9.996e17 FLOPs**. Dollar-reconciled 1.151e18 (1.15×); calls-allocated 0.96×; attention
7.1–16.0%.

Human: regression at the Yield–Screened midpoint x = 1,699.5 gives 1,098.5 h; excluding the 17.6% administrative share, **904.6 h = 3,256,588 s** (formerly 1,159.7 h = 4,175,052 s, at the raw yield with administration included). The smallest corpus gives the smallest
human estimate, and at x = 2,010 the regression is being used near the centre of its plausible
fitted range, so this is the most secure of the five human values.

## agen-lumen-d5-gemini31pro

SGLT2 inhibitors in heart failure (Table 2 D5; ground truth Vaduganathan 2022, Lancet
400:757–767). Yield 8,062 → 4,839 screened → 11 included. Largest corpus, most expensive run at
$29.04, and the best result: all four published hazard ratios reproduced within 1% with I² of
0–0.7%, verified above against the Lancet record independently of the paper, subject to the
contamination caveat. Cohen's κ = 0.21 reflects a kappa paradox at ~97% exclusion; PABAK is 0.93.
9,732 derived screening calls. Seven poolable analyses. Table S2's "Included" cell is blank for
D5 alone. Label `match`.

The full-text screening phase cost $0.04 — 0.1% of the run, against $0.66 to $2.70 elsewhere —
which on the allocation gives 15,700 tokens for 11 included studies, about one call. Either
almost no full-text verification happened for D5 or the figure is wrong. It changes the total by
well under 1% either way, but it is a defect in the source.

Compute: screening 8.11M tokens (1.005e18), extraction 0.606M (1.212e17), full-text 0.016M
(3.14e15), manuscript 0.127M (2.542e16), other 0.170M (1.84e16). Total 9,025,809 tokens →
**1.173e18 FLOPs**, the largest of the five. Dollar-reconciled 2.212e18 (1.88×); calls-allocated
0.89×; attention 2.1–4.7%.

Human: regression at the Yield–Screened midpoint x = 6,450.5 gives 1,776.7 h; excluding the 17.6% administrative share, **1,463.1 h = 5,267,338 s** (formerly 1,880.6 h = 6,770,222 s, at the raw yield with administration included). At x = 8,062 this is the closest of
the five to the quadratic's turning point at 9,878 and is the least secure human value in the set.

---

## Considered and not built

| Candidate row | Why not |
|---|---|
| A sixth row on the Table S1 median composite | It is a sum of per-phase medians drawn from five different runs and corresponds to no run. Building it would also double-count the same five runs already represented. |
| The two SYNERGY screening benchmarks (S1 Bos_2018, S2 van_de_Schoot_2018) | Screening only, so the work unit is a stage rather than a review, and the dataset has no established stage-level unit for this. The published per-arm costs are also internally strange: per-record cost differs eight-fold between the two datasets for Gemini and GPT but not for Claude. Worth revisiting if stage-level rows are wanted; the arm costs do confirm the dual screener is Gemini + GPT + a small arbiter, since $17.53 + $2.40 = $19.93 against a reported dual cost of $20.02. |
| The repository's `met_ovary` pilot | A LUMEN v3 run on a different model roster, not one of the paper's five, and with no ground-truth comparison. Used here only as a cross-check on calls per record and dollars per record. |
| Separate rows for extraction Arms C and D | Ablation arms on already-extracted corpora, not complete runs, and no separate token or cost totals are published for them — only cost *ratios* of 2.6–3.9×. |
| A row using the paper's wall-clock as human-comparable elapsed time | `human_time` is summed active time. The 5.1–10.8 h figure is machine elapsed time and the paper's own human anchor (67 weeks) is calendar time. Neither converts. |
| otto-SR, MedSR-Copilot, meta-pipe, Elicit | Covered in `research/scouting/systematic-reviews.md`. None publishes token counts or dollars; otto-SR's compute would have to be built from prompt-length and reasoning-token assumptions from scratch. Out of scope for this note. |

## Specification gap to raise at merge

`compute_evidence = derived_assumed_inputs` is the best available fit and is what these rows
carry: the dollars that set each review's relative scale belong to that review. But the token
*magnitude* is a five-run collection median, which gives `transferred_workload` a real claim
too, and COLUMNS offers no combination of the two. Worth raising alongside the
`tokens_accounting` cache-counter gap already recorded in `DECISIONS.md`.

## Reproduction

```
python3 research/lumen/lumen_calculations.py \
  --source           agent-work/sources/lumen/lumen-source-values.json \
  --dataset-models   "../AI Compute vs Human Time/dataset/models.csv" \
  --local-models     models.csv \
  --candidate-models candidates/lumen/models.csv \
  --output           agent-work/derived/lumen/calculations.json
```

then

```
python3 research/lumen/build_lumen_rows.py \
  --calculations agent-work/derived/lumen/calculations.json \
  --header       points.csv \
  --output       candidates/lumen/points.csv
```

Python 3.9+, standard library only. Paths are explicit. `lumen_calculations.py` writes only
`--output` and reads the model tables without modifying them; `build_lumen_rows.py` reads
`--header` only for its column order, asserts every text field against the dataset's field-length
norms, and writes only `--output`. Nothing in `../AI Compute vs Human Time/` is written.
