# ALE-Bench short-format contests and ALE-Agent's AHC058 win

*Created 2026-09-13 17:36.*
*Revision 1, 2026-09-13 18:15, on the independent review at `reviews/ale-bench-independent.md`
and the coordinator's rulings of the same day; changes logged in
`candidates/ale-bench/REVISION.md`.*

*Label note, 2026-09-15: `far_above` was merged into `above` across the dataset (Damon's ruling that day), so rows this note calls `far_above` carry `above` in `points.csv`. The reasoning below is unchanged.*

## Summary

Forty-nine candidate rows put AI systems against the field of an AtCoder
Heuristic Contest. Forty-eight are one short-format ALE-Bench problem solved by
one model configuration on Sakana AI's public ALE-Bench leaderboard; the
forty-ninth is Sakana's ALE-Agent taking **first place among the 804 rated human
entrants of the live AHC058 contest on 14 December 2025**. Compute runs **4.3e15
to 5.1e17 FLOPs per problem** across 39 model identities on the leaderboard, and
**1.7e19 FLOPs** for the AHC058 run. Human time on every row is the contest
window: **14,635 s** (4.07 h, the mean over the 23 short-format problems) for the
leaderboard rows and **14,400 s** for AHC058.

The human side is a contest window, not a measured effort, and that is the single
judgment a reviewer should test first. AtCoder publishes no active-time
measurement for heuristic contests, and none exists anywhere I could find. The
2026-09-13 revision of `COLUMNS.md` names "a four-hour contest window" as the
example of `defined_duration`, so the rows take the window at face value and say
in `notes` that it bounds effort rather than measuring it. The coordinator ruled
on 2026-09-13 to keep it. Long-format ALE-Bench problems, whose windows run 199
to 367 hours of calendar time over 8 to 15 days, are not built for exactly this
reason and are recorded in `candidates/ale-bench/dispositions.csv`.

The compute side is measured rather than inverted for the 48 leaderboard rows.
The leaderboard publishes per-problem input tokens, output tokens and cost for
every model and every self-refine setting, and its published short-subset means
reproduce exactly from its own per-problem records. What the leaderboard does
*not* publish is the 14 discarded samples: its harness generates 15 independent
solutions per problem and records tokens only for the one it submits, so each
row multiplies the published counts by 15.

Labels: **2 far_above, 10 above, 11 match, 26 below**. Six leaderboard cells fall
below half the mean entrant's score and are recorded in the dispositions file
rather than built; three more are kept as `below` under the one-standard-error
close-call rule. The interesting shape is that the frontier reached the mean AHC
entrant with GPT-5.1 and Gemini 3 Pro in late 2025, and GPT-6 Astra
at 3,274 mean performance now sits 2.4 times the mean entrant on the contest's
own metric, taking first place outright on 14 of the 23 contests.

**A reviewer should look first at**: the contest window as human time; the
15-sample reconstruction, which is 93% of the counted compute and rests on the
discarded samples matching the submitted one; the choice of the mean contest
entrant (1414.5) over the benchmark's own published Human Average (1252) as the
baseline; and the cache-read deduction, which Revision 1 made the central on 31
rows.

## What the sources publish

Four primary sources, all read directly rather than through the scouting note.

**The ALE-Bench paper** (arXiv 2506.09050v2, Sakana AI and AtCoder, NeurIPS 2025
Datasets and Benchmarks) defines the benchmark: 40 AtCoder Heuristic Contest
problems, 23 short-format and 17 long-format, each shipped with its scorer,
visualiser, contest leaderboard and a rank-to-performance table. It reports
one-shot, iterative-refinement and scaffolding experiments in dollars per problem
with no token counts. None of its own experiment tables are built as rows; the
reasons are in the dispositions file.

**The Hugging Face dataset `SakanaAI/ALE-Bench`** ships, per problem, a
`performance.csv` giving every original contest entrant's rank and AtCoder
performance, a `standings_scores.csv`, and a `schedule.csv` with each contest's
exact start and end time. It also ships `ranking.csv`, the 6,139 active AtCoder
heuristic users with their ratings, average performances and participation
counts. Both human numbers this note uses come from these files.

**The ALE-Bench leaderboard** (`sakanaai.github.io/ALE-Bench-Leaderboard`,
version 2026-09-08) is a later and much richer evaluation than the paper: 128
model configurations, each run on all 40 problems at five self-refine settings,
with input tokens, output tokens, total tokens, cost, rank and performance
published per problem. Its stated protocol is "Self-refine x1 involved 15
sampling iterations, from which the response getting the median score across 50
local cases was selected", matching `scripts/run_eval.sh` in the ALE-Bench
repository (`--n_repeated_sampling 15 --n_self_refine 16 --n_public_cases 50
--selection_method median`, judge 202301, C++20). The repository's
`llm_configs/*.json` name the exact API model string and settings behind each of
the 128 configurations; Revision 1 retains all of them at a pinned commit as
`agent-work/sources/ale-bench/alebench-llm-configs.csv`, which is what
`research/ale-bench/model-map.csv` is built against.

**Sakana's AHC058 report** (`sakana.ai/ahc058/`, 5 January 2026) and AtCoder's own
contest pages carry the live-contest row.

## Human time

The work unit is one contest problem, and the duration the work unit fixes is the
contest window.

`agent-work/sources/ale-bench/alebench-human-performance-per-problem.csv` carries each
problem's window computed from the dataset's own `schedule.csv`. The 23
short-format problems run 4.0 hours each except `ahc004` at 6.0 and
`toyota2023summer-final` at 3.5, a mean of **4.0652 h = 14,634.8 s**. The 17
long-format problems average 244.7 h. AHC058's window is 240 minutes exactly,
from AtCoder's contest page.

Nothing measures how much of the window an entrant actually worked. AtCoder
records submission times but publishes no effort figure, the ALE-Bench paper
reports none, and the benchmark's regulations bear on the agent's conduct rather
than the humans'. A four-hour contest is a contiguous sitting, so the window is a
usable bound on effort; the same is not true of a ten-day window, which is why
long-format problems are not rows.

The direction of the error runs in the AI's favour, and Revision 1 corrects the
first submission, which said the opposite. The mean over entrants includes people
who registered, submitted once and stopped, so 14,635 s is an upper bound on the
mean entrant's effort. Overstating the human side understates FLOPs per
human-second, so these rows plausibly overstate how much human work a given FLOP
count substitutes for. Nothing here is conservative against the AI.

`human_time_method` is `work_rate`: one problem times a 4.0652 h per problem
window. That matches the only precedent for `defined_duration` in either batch,
the seven one-minute-of-play rows in the Codex dataset.

## Human baseline performance

AtCoder performance is an Elo-like transform of a contestant's rank within one
contest, typically 0 to 3500. ALE-Bench scores an AI by running its submitted
program on 150 private cases, ranking the result among that contest's original
entrants, and reading the performance off that contest's own rank-to-performance
table. The AI and the humans are therefore on one scale by construction.

The baseline these rows use is **1414.46, the unweighted mean of the 23
short-format contests' own entrant means**, computed from the 23 shipped
`performance.csv` files. Which mean it is matters, and the first submission's
`performance_evidence` was ambiguous about it: the mean over all 16,275
entrant-contest records is 1393.19, not 1414.46, because contests differ in size.
The unweighted mean of contest means is the right statistic because the AI's own
figure is also an unweighted mean over the same 23 contests, so both sides weight
each contest equally.

The corresponding floor is **55.26**, the mean of the 23 contests' last-place
performances. It is not a zero point: the per-contest minima run from +483 down
to −200, and 55.26 is their mean. A program that fails to compile or emits
invalid output scores zero on the contest's own scale, lands last, and therefore
lands near this value. Every ratio in this note subtracts it; at 4% of the scale
it moves ratios by about two points in the third decimal.

The paper prints a different figure, "Human Average" 1252 short / 1257 long /
1260 overall with a rating of 1414. Two clarifications. First, that 1414 is a
*rating*, a different quantity that happens to be numerically close to the 1414.46
*performance* mean above; the coincidence is not a corroboration. Second, the
reproduction is partial: restricting `ranking.csv` to the 2,220 users with at
least five heuristic-contest participations gives mean `avg_perf` 1260.03 and
mean `rating` 1414.27, matching the paper's overall and rating columns, and twelve
of the rank percentiles the paper prints reproduce against that same pool to
within a tenth of a point. The short column, 1252, cannot be computed from
`ranking.csv` alone, since that file carries no short-versus-long split; the paper
took it from internal AtCoder data. So the paper's baseline is *the average
regular AHC participant across all the contests they entered*, while 1414.46 is
*the average entry in these 23 contests*.

The coordinator ruled on 2026-09-13 to keep 1414.46 and to carry 1252 as a named
scenario. The scenario: at 1252 every ratio rises by a factor 1.113, which moves
eleven rows up a label and restores three of the six excluded cells. The per-row
ratios needed to redo that pass are in
`candidates/ale-bench/calculations.json`. The choice is also robust to the
statistic — the unweighted mean of the 23 contest *medians* is 1363.5, only 3.6%
below the mean of means — and 1414.46 is the higher bar of the two, so it is the
conservative side of the switch.

## Compute

`compute_method` is `params_tokens` throughout. For the leaderboard rows the
token counts are measured by the harness's own usage counters; the reconstruction
of the discarded samples is the assumed input, so `compute_evidence` is
`derived_assumed_inputs`.

**The 15-sample fan-out.** `src/ale_bench_eval/analyze_results.py` computes the
published totals with `estimate_total_cost(repeated_sampling_results.json,
selected_index)` for the sampling stage and
`estimate_total_cost(self_refine_results.json, n_max_refine=i)` for the refine
stage, and `self_refine_results[0]` is the selected sample. So at self-refine x1
the published input, output and cost are one generation: the sample the harness
chose. The other 14 were generated and paid for. Each row therefore counts 15
samples, taking the 14 discarded ones to match the submitted one. The assumption
is that selection by *median score over 50 local cases* is uncorrelated with
response length; selecting the median rather than the best is what makes that
plausible, and it is the largest single assumption in these rows. No sample-level
data is published, so it cannot be tested; the repository's `results/` ships
empty.

**Cache reads are deducted where the billed cost shows a discount was taken.**
This is the `DECISIONS.md` default-on caching ruling, applied in Revision 1 on
the coordinator's instruction; the first submission took the gross count as the
central everywhere. No cache counters are published, but they can be inverted
from the gap between the gross list price and the billed cost, and where that gap
is positive the reads it implies are removed from the parameter-multiplication
term, leaving `tokens = 15 x (input - cache reads + output)` and
`tokens_accounting = input_cache_creation_output`. Thirty-one retained rows are
deducted this way. The effect is small: the gross scenario is 1.035x the central
at the median deducted row, and only six rows move more than a tenth, led by
gpt-5.5 at reasoning effort none (1.288x) and gpt-5.4 at none (1.206x), where
short outputs leave input at half the total.

Two windows are in play and they are not the same window. The inversion has to
run at the rates the harness actually billed, which for the GPT-5.6 family are the
launch rates; `ai_cost_usd` is priced at the rates in force on the row's cost
date. `calculations.json` records them separately as `billing_window` and
`pricing_window`, and they coincide on every row except those three.

Cases that do not take the deduction fall into three kinds, each for a stated
reason. On every Anthropic-path row the gap is *exactly* zero — the billed cost
lands on the gross list price to sub-token precision — so no cache discount was
taken and the uncached-harness ruling applies; the first submission reported four
of these as price-sheet disagreements, which they are not.

Five further rows show a zero gap on providers that cache by default, and they
are a different finding, not an application of that ruling: `gemini-3.1-pro-preview`
at both thinking levels, `gemini-3.1-flash-lite-preview` and the two Qwen rows.
Google and Alibaba cache without being asked, so a zero implied read here says the
run took no cache hits rather than that caching was unavailable. The other Google
rows in the same build invert to positive counts — 146, 444, 972 and 354 reads per
call on Gemini 2.5 Flash, 2.5 Pro, 3 Flash and 3.5 Flash — which is what makes the
zero a measurement rather than an artefact of the method.

On `grok-4.20-beta` and
`deepseek-r1-0528` the harness billed at an OpenRouter reseller rate (for
DeepSeek, pinned to `parasail/fp8` with fallbacks disabled) that
`research/cost/list-prices.csv` does not carry, so nothing can be inverted and
input stays gross; the row's `notes` says so. One further caveat is recorded
rather than corrected: the inversion deducts the same implied read count from all
fifteen samples, whereas the true structure across fifteen identical prompts is
one cache-miss call and fourteen hits, so the deduction is at most one fifteenth
of the input term too large.

**Why only self-refine x1.** At x2 and beyond the harness resends the whole
conversation on every turn, so published input tokens rise from a median 14% of
the total at x1 to 27% at x2, 44% at x4, 67% at x8 and 84% at x16 over the 54
mapped configurations (11%, 30%, 50%, 69%, 84% over all 128), and those input
counts are gross of cache reads. Counting them at full prefill would overstate
the parameter term severalfold, and the billed-cost inversion that works at x1
becomes unreliable once the prefix is mostly cached. The four larger settings are
recorded in the dispositions file.

**Prices, and what the ALE-Bench harness billed at.** The first submission
concluded that `research/cost/list-prices.csv` disagreed with the harness's own
`calc_cost.py` fallback table for five configurations and flagged it for
checking. That conclusion was wrong in both directions and Revision 1 replaces
it. The GPT-5.6 family repriced twice in its first six weeks — Terra and Luna
were cut permanently on 2026-07-30, Sol promotionally on 2026-08-21 — and the
harness's fallback table carries the **launch** rates, which were correct for
runs in July 2026 and stale afterwards. The sheet carried only the final rate,
undated, until `research/cost/gpt56-repricing.md` added the six dated windows on
2026-09-13. Neither table was simply right: the harness's rates were correct when
billed, and the sheet's were correct for the date the rows carry. The consequence
for these rows is that the cache inversion has to run at the rates the harness
actually billed, where it returns 28.9%, 79.0% and 4.0% of gross input for Sol,
Terra and Luna, all positive and all plausible, while `ai_cost_usd` is repriced at
the window the row's `ai_cost_date` selects. The two remaining flagged
configurations were never sheet errors at all, being reseller rates.

**Cost columns.** `ai_cost_usd` is 15 times the leaderboard's published cost for
the submitted sample, on `list_price` basis at the leaderboard's version date,
because the leaderboard computes that cost from its own token counts at published
list rates and the 15-fold scaling is the same documented protocol fact the token
count uses. The three GPT-5.6 rows are the exception: their dollars are
recomputed from the same token and cache split at the rates in force on
2026-09-08, giving $15.03, $14.45 and $1.04 against the $22.46, $18.06 and $5.20
the harness's launch-rate table produced. AHC058 is `reported`: Sakana states
about $1,000 in API fees inside a $1,300 total that also covers AWS, and that
figure is not independent of the row's FLOPs, which invert it.

## Performance labels

The ratio is (AI performance - 55.26) / (1414.46 - 55.26). Thresholds: below 0.50
the cell is excluded, 0.50 to 0.85 is `below`, 0.85 to 1.15 is `match`, 1.15 to
2.00 is `above`, and 2.00 or more is `far_above`. The 0.50 and 2.00 cuts are the
dataset's half-of-the-better-side guide. The 0.85/1.15 band for `match` is my
reading of "broadly comparable" and had no ruling behind it; the coordinator
adopted it on 2026-09-13, so it is now a coordinator call rather than a
constructor's choice. The close-call rule applies at the 0.50 cut, using the
standard error of the AI's own mean across the 23 problems.

The band's fragility is worth stating rather than fixing. The per-row standard
error runs 0.029 to 0.149, and twelve rows sit within one standard error of a
label edge, among them opus48high at 1.172 ± 0.093, gpt54med at 1.173 ± 0.071,
gpt5high at 0.903 ± 0.056 and gemini31pro-high at 0.901 ± 0.121. The
one-standard-error close-call rule is deliberately **not** extended to the
interior edges: at the 0.50 cut it is one-sided because the alternative is
deletion, whereas at an interior boundary it would pull rows both ways at once
and produce an incoherent assignment. Boundary rows read as boundary rows.

`far_above` lands on two rows and the coordinator confirmed both. AHC058 is the
clear case: the agent finished ahead of all 804 rated human entrants. For GPT-6
Astra the ratio limb (2.368, seven standard errors clear of 2.00) is the weaker
argument, because the mean AHC entrant does write a working program. The stronger
one is rank, which Revision 1 adds to `performance_evidence` on every row: Astra's
mean rank across the 23 contests is 3.4 of a mean 708 entrants, 0.38% of the
field finished above it, and it took first place outright on 14 of the 23. That
is the first limb of the `far_above` definition — a step no human in the sample
matched — met directly rather than through the numerical guide.

## Model identities and priors

Every leaderboard configuration is mapped to a model identity in
`research/ale-bench/model-map.csv`, checked against the retained
`alebench-llm-configs.csv`, which names the exact API model string and settings.
Cells are considered only for the 54 configurations whose model already has a
vetted active-parameter record in the Codex registry or in this folder's
`models.csv`, and 48 of those 54 become rows; the other 74 configurations are
recorded in the dispositions file.

Shared IDs keep the Codex registry's current coefficient rather than the value
`research/model-priors/accepted-priors.csv` rules, following the ruling that
shared IDs are updated once at merge by `tools/apply_priors.py`; pre-applying
here would double-apply. The coordinator confirmed this on 2026-09-13. Two rows
are affected and say so in `notes`: `gpt-5.6-sol-max` rises 1.5x when the ruled
150B prior lands, and `gemini-2.5-flash-thinking` falls to 0.625x under the ruled
25B.

Three configurations carry an identity caveat. `grok-4.20-beta` calls the
OpenRouter alias `x-ai/grok-4.20-beta`, while the registry ID
`grok-4.20-beta-0309b-reasoning` names a particular evaluation endpoint; the
parameter prior is a coarse Grok-family figure either way, so the number does not
move, but the endpoint is not the same string and the row says so. `kimi-k2.5` was
retired from the Moonshot API on 2026-08-31, so no price window covers the rows'
2026-09-08 cost date and its last window is used, which is itself evidence that
the run predates the retirement. And `deepseek-v4-pro-high` and
`deepseek-v4-pro-no-thinking`, both in the dispositions rather than rows, call
`deepseek/deepseek-v4-pro` while the Codex registry carries
`deepseek-v4-pro-preview`; I have not established whether the preview record is
the same weights, so neither is mapped, and a later pass should settle it the way
`gemini-3-pro-preview` and `grok-4.20-beta` were settled here.

### gemini-3-pro-preview

One new model record. The AHC058 run and two leaderboard configurations call
Google's `gemini-3-pro-preview` endpoint, which is a different revision from the
registry's `gemini-3-pro`. Google's Gemini API changelog records the endpoint
launching on 2025-11-18 with the first Gemini 3 series model, and redirecting to
`gemini-3.1-pro-preview` on 2026-03-09. Both runs used here predate the redirect:
AHC058 ran on 2025-12-14, and the leaderboard's `gemini-3-pro-preview-high` and
`gemini-3.1-pro-preview-high` entries have visibly different output lengths
(20,623 against 31,168 tokens per call) and performances, so the alias was still
serving the November weights when they were run.

Active parameters are 100B, `estimated`, transferred under the 2026-09-13
coordinator ruling that holds the whole Gemini 3 family at 100B; Google discloses
no size. Grade C, 30-300B, moving dependent FLOPs 0.3x to 3x. The price sheet
carries no row for the preview endpoint, so both its rows and the AHC058
calculation price it at the `gemini-3-pro` window, the same family and tier over
the same dates; the override is explicit in `research/ale-bench/build_rows.py`.

## AHC058

AtCoder's own records carry the result. `https://atcoder.jp/contests/ahc058` gives
the window, 2025-12-14 15:00 to 19:00 JST, 240 minutes. The contest's results
file lists 1,317 entries, of which **804 are rated**; `fishylene`, affiliation
"Sakana AI (Unrated)", is **place 1**, and AtCoder's own user history for that
account confirms place 1 at AHC058 and no other first place in nine prior
heuristic contests. The top rated human, `yosupo`, has an official performance of
3,535 and the 804 rated entrants average 1,384.3, so the field mean is 39% of the
standing the agent beat. The agent's own performance is not published because the
account is unrated. The row says "ahead of all 804 rated human entrants" rather
than "1st of 805": 804 is Sakana's own framing of the field, and the standings
list 1,317 entries in all.

Sakana's report gives the compute evidence: 2,654 GPT-5.2 calls at high reasoning
effort, 2,119 Gemini 3 Pro Preview calls at high thinking level, and about $1,000
in API fees inside an approximately $1,300 total including AWS. No token counts
exist. Sakana's own submission log
(`sakanaai.github.io/fishylene-ahc058/data/submissions.json`) shows eight
submissions rising from rank 208 to rank 1, the last of them written by GPT-5.2,
which is why that is the row's `model_id`.

The inversion is in the row's section below. Its one structural assumption is
that ALE-Agent's per-call input and output resemble the same two model
configurations' measured one-shot calls on ALE-Bench. The check that makes this
more than a guess is the per-call cost: $1,000 over 4,773 calls is $0.21 per call,
against $0.28 and $0.25 per call measured for the same two configurations on the
leaderboard, so the run's calls were slightly cheaper than one-shot ALE-Bench
calls rather than an order of magnitude different.

`comparison_issues` is `none_identified`: the agent entered the live contest under
the same problem statement, the same judge, the same window and the same scoring
as the human field. AtCoder's generative-AI rules bar human entrants from the
assistance the agent is made of, but that is the comparison being drawn rather
than a confound in it.

## Dispositions

`candidates/ale-bench/dispositions.csv` records every cell of both sources that
is not a row, on the pattern of `candidates/gaia/dispositions.csv`: 6 excluded
leaderboard cells with their ratios and their distance from the cut in standard
errors, 74 leaderboard configurations that have no usable parameter count, the
four larger self-refine settings, the three paper experiment settings, and the
long-format problems.

Revision 1 splits the 74 by what unblocks each, because the first submission's
blanket "needs a closed-model prior" was wrong for more than half of them, and
adds a `would_be_a_row` column so a later pass can size the work. **Thirty-nine
of the 74 would clear the exclusion cut.** Six carry their own parameter count in
the model name and want a `reported` count transcribed from a model card rather
than a prior: `gemma-4-26b-a4b-it`, `gemma-4-31B-it`, `qwen3.5-35b-a3b`,
`qwen3.5-397b-a17b`, `qwen3.5-27b` and `nemotron-3-super-120b-a12b`. Forty-one
sit with vendors that publish weights for at least some models in the family —
Qwen, Z.ai, DeepSeek, Moonshot, MiniMax, Mistral, Xiaomi, Gemma, NVIDIA, StepFun,
InclusionAI, Tencent and Meta — where the released configuration is worth
checking before anything is assumed; the disposition says where to look, not that
the endpoint's own weights are public, since several named endpoints inside those
families are API-only. The remaining 27 have no published architecture and do
need a grade-C prior, and they hold the highest-scoring blocked cells:
`claude-fable-5.1-high` at ratio 1.645, `claude-fable-5-high` at 1.536,
`gpt-5.3-codex-xhigh` at 1.272 and `claude-sonnet-5-high` at 1.157. Of the 39
that would clear the cut, 20 are in that closed group and 19 are not, so the two
routes are worth about the same number of rows but not the same rows.

## Reproduction

`research/ale-bench/fetch_sources.py --hf-dir <hf> --out agent-work/sources/ale-bench`
rebuilds every retained extract from the public endpoints and a local copy of the
Hugging Face dataset. `research/ale-bench/build_rows.py` then rebuilds
`points.csv`, `models.csv`, `dispositions.csv`, `calculations.json` and this
note's row sections from those extracts, the model map, the two model registries
and the price sheet:

```
python3 research/ale-bench/build_rows.py \
  --sources agent-work/sources/ale-bench \
  --map research/ale-bench/model-map.csv \
  --codex-models "../AI Compute vs Human Time/dataset/models.csv" \
  --local-models models.csv \
  --prices research/cost/list-prices.csv \
  --note-head research/ale-bench/note-head.md \
  --note-out research/ale-bench.md \
  --out candidates/ale-bench
```

Both scripts take explicit input and output paths, write nothing into
`agent-work/sources/`, and need no candidate-folder layout.

## Open questions for the coordinator

The seven the first submission raised are all ruled on: the contest window stays,
1414.46 stays with 1252 as a named scenario, the match band is adopted as a
coordinator call, `far_above` stays on GPT-6 Astra with the rank evidence added,
shared-ID priors wait for the merge, the price-sheet question is answered by
`research/cost/gpt56-repricing.md`, and the larger self-refine settings wait for a
cache-structure inversion. Four things remain open.

1. **The deduction count is 31, not the 30 the review counted.** The extra row is
   `kimi-k2.5`, whose only price window ends 2026-08-31 when the model was
   retired; the build falls back to that last window rather than declining to
   invert. If the coordinator would rather the fallback not exist, that row goes
   back to gross and its compute rises 1.113x.
2. **The Sol reprice differs from the price agent's figure by 3e-5.** I get
   $15.025659 against $15.025688, from inverting the cache split at full
   precision rather than from a rounded intermediate; Terra and Luna match to the
   last digit. Nothing turns on it, but the two notes should not disagree.
3. **`human_time_statistic` is `point_estimate`** where the value is the
   arithmetic mean of 23 contest windows. The review suggested `mean`. I have kept
   `point_estimate` because the statistic is over work-unit durations, not over
   human times, and the sample columns are `not_applicable` accordingly; AHC058's
   single window is a point estimate on any reading.
4. **Twenty-seven blocked configurations need closed-model priors**, and they hold
   the four highest-scoring blocked cells. Nineteen more are unblocked by
   transcription rather than judgment and need no ruling, so that group is worth
   taking first.

## Rows

One heading per `point_id`. Every leaderboard row reads the same way: the short-subset means are the arithmetic means over the 23 short-format problems, `tokens` is 15 x (input - cache reads + output) where the billed cost shows a cache discount was taken and 15 x (input + output) otherwise, `compute_flops` is `tokens` x the model's `flops_per_token` plus the cached-context attention term of `research/attention-correction.md`, `ai_cost_usd` is 15 x the leaderboard's cost for the submitted sample, and the ratio is (AI performance - 55.3) / (1414.5 - 55.3). The gross scenario is the upward alternative on the cache-deducted rows. Six sections describe cells that are dispositions rather than rows; their label reads excluded and they are not in points.csv.

### agen-alebench-short-sonnet4

`claude-sonnet-4` as leaderboard configuration `claude-4-sonnet` (extended thinking on; 32000-token budget), self-refine x1.

- Short-subset means: input 2,727 tokens, output 12,375, cost $0.1938, AtCoder performance 693.9 (standard deviation across problems 444).
- Cache basis: no_cache_discount_billed, so input is counted gross.
- tokens = 15 x (2,727 + 12,375) = 226,533; compute = 226,533 x 2e+11 = 4.53e+16 FLOPs; cost = 15 x $0.1938 = $2.91.
- Mean rank 642.9 of a mean 708 entrants; 92.18% of the field finished above it, and it never took 1st place.
- Ratio to the mean entrant: (693.9 - 55.3) / (1414.5 - 55.3) = 0.470, standard error 0.068. Label **below** (close call, kept under the one-standard-error rule).

### agen-alebench-short-opus41

`claude-opus-4-1` as leaderboard configuration `claude-4.1-opus` (extended thinking on; 16000-token budget), self-refine x1.

- Short-subset means: input 2,727 tokens, output 5,004, cost $0.4162, AtCoder performance 713.3 (standard deviation across problems 409).
- Cache basis: no_cache_discount_billed, so input is counted gross.
- tokens = 15 x (2,727 + 5,004) = 115,967; compute = 115,967 x 3.6e+11 = 4.17e+16 FLOPs; cost = 15 x $0.4162 = $6.24.
- Mean rank 632.6 of a mean 708 entrants; 91.85% of the field finished above it, and it never took 1st place.
- Ratio to the mean entrant: (713.3 - 55.3) / (1414.5 - 55.3) = 0.484, standard error 0.063. Label **below** (close call, kept under the one-standard-error rule).

### agen-alebench-short-haiku45

`claude-haiku-4-5` as leaderboard configuration `claude-4.5-haiku` (extended thinking on; 16000-token budget), self-refine x1.

- Short-subset means: input 2,727 tokens, output 14,158, cost $0.0735, AtCoder performance 644.2 (standard deviation across problems 407).
- Cache basis: no_cache_discount_billed, so input is counted gross.
- tokens = 15 x (2,727 + 14,158) = 253,285; compute = 253,285 x 8e+10 = 2.03e+16 FLOPs; cost = 15 x $0.0735 = $1.10.
- Mean rank 668.3 of a mean 708 entrants; 95.61% of the field finished above it, and it never took 1st place.
- Ratio to the mean entrant: (644.2 - 55.3) / (1414.5 - 55.3) = 0.433, standard error 0.063. Label **excluded**.

### agen-alebench-short-opus45

`claude-opus-4-5` as leaderboard configuration `claude-4.5-opus` (extended thinking on; 16000-token budget), self-refine x1.

- Short-subset means: input 2,728 tokens, output 11,554, cost $0.3025, AtCoder performance 1046.4 (standard deviation across problems 376).
- Cache basis: no_cache_discount_billed, so input is counted gross.
- tokens = 15 x (2,728 + 11,554) = 214,237; compute = 214,237 x 2e+11 = 4.28e+16 FLOPs; cost = 15 x $0.3025 = $4.54.
- Mean rank 500.4 of a mean 708 entrants; 74.18% of the field finished above it, and it never took 1st place.
- Ratio to the mean entrant: (1046.4 - 55.3) / (1414.5 - 55.3) = 0.729, standard error 0.058. Label **below**.

### agen-alebench-short-sonnet45

`claude-sonnet-4-5` as leaderboard configuration `claude-4.5-sonnet` (extended thinking on; 32000-token budget), self-refine x1.

- Short-subset means: input 2,727 tokens, output 10,644, cost $0.1678, AtCoder performance 840.4 (standard deviation across problems 419).
- Cache basis: no_cache_discount_billed, so input is counted gross.
- tokens = 15 x (2,727 + 10,644) = 200,570; compute = 200,570 x 2e+11 = 4.01e+16 FLOPs; cost = 15 x $0.1678 = $2.52.
- Mean rank 583.3 of a mean 708 entrants; 85.06% of the field finished above it, and it never took 1st place.
- Ratio to the mean entrant: (840.4 - 55.3) / (1414.5 - 55.3) = 0.578, standard error 0.064. Label **below**.

### agen-alebench-short-opus46nothink

`claude-opus-4-6` as leaderboard configuration `claude-4.6-opus-no-thinking` (thinking disabled), self-refine x1.

- Short-subset means: input 2,699 tokens, output 1,659, cost $0.0550, AtCoder performance 1002.4 (standard deviation across problems 390).
- Cache basis: no_cache_discount_billed, so input is counted gross.
- tokens = 15 x (2,699 + 1,659) = 65,377; compute = 65,377 x 2e+11 = 1.31e+16 FLOPs; cost = 15 x $0.0550 = $0.82.
- Mean rank 523.5 of a mean 708 entrants; 76.18% of the field finished above it, and it never took 1st place.
- Ratio to the mean entrant: (1002.4 - 55.3) / (1414.5 - 55.3) = 0.697, standard error 0.060. Label **below**.

### agen-alebench-short-sonnet46med

`claude-sonnet-4-6` as leaderboard configuration `claude-4.6-sonnet-medium` (reasoning on; medium verbosity), self-refine x1.

- Short-subset means: input 47,435 tokens, output 93,595, cost $1.5462, AtCoder performance 1480.7 (standard deviation across problems 401).
- Cache basis: no_cache_discount_billed, so input is counted gross.
- tokens = 15 x (47,435 + 93,595) = 2,115,444; compute = 2,115,444 x 2e+11 = 4.23e+17 FLOPs; cost = 15 x $1.5462 = $23.19.
- Mean rank 329.0 of a mean 708 entrants; 46.88% of the field finished above it, and it never took 1st place.
- Ratio to the mean entrant: (1480.7 - 55.3) / (1414.5 - 55.3) = 1.049, standard error 0.062. Label **match**.

### agen-alebench-short-opus47nothink

`claude-opus-4-7` as leaderboard configuration `claude-4.7-opus-no-thinking` (thinking disabled), self-refine x1.

- Short-subset means: input 3,363 tokens, output 7,527, cost $0.2050, AtCoder performance 1358.2 (standard deviation across problems 562).
- Cache basis: no_cache_discount_billed, so input is counted gross.
- tokens = 15 x (3,363 + 7,527) = 163,338; compute = 163,338 x 2e+11 = 3.27e+16 FLOPs; cost = 15 x $0.2050 = $3.07.
- Mean rank 352.8 of a mean 708 entrants; 52.70% of the field finished above it, and it never took 1st place.
- Ratio to the mean entrant: (1358.2 - 55.3) / (1414.5 - 55.3) = 0.959, standard error 0.086. Label **match**.

### agen-alebench-short-opus48high

`claude-opus-4-8` as leaderboard configuration `claude-4.8-opus-high` (adaptive thinking; high effort), self-refine x1.

- Short-subset means: input 3,358 tokens, output 31,603, cost $0.8069, AtCoder performance 1648.9 (standard deviation across problems 603).
- Cache basis: no_cache_discount_billed, so input is counted gross.
- tokens = 15 x (3,358 + 31,603) = 524,409; compute = 524,409 x 2e+11 = 1.05e+17 FLOPs; cost = 15 x $0.8069 = $12.10.
- Mean rank 257.6 of a mean 708 entrants; 37.15% of the field finished above it, and it never took 1st place.
- Ratio to the mean entrant: (1648.9 - 55.3) / (1414.5 - 55.3) = 1.172, standard error 0.093. Label **above**.

### agen-alebench-short-opus48nothink

`claude-opus-4-8` as leaderboard configuration `claude-4.8-opus-no-thinking` (thinking disabled), self-refine x1.

- Short-subset means: input 3,358 tokens, output 14,221, cost $0.3723, AtCoder performance 1470.3 (standard deviation across problems 657).
- Cache basis: no_cache_discount_billed, so input is counted gross.
- tokens = 15 x (3,358 + 14,221) = 263,681; compute = 263,681 x 2e+11 = 5.27e+16 FLOPs; cost = 15 x $0.3723 = $5.58.
- Mean rank 323.6 of a mean 708 entrants; 45.84% of the field finished above it, and it never took 1st place.
- Ratio to the mean entrant: (1470.3 - 55.3) / (1414.5 - 55.3) = 1.041, standard error 0.101. Label **match**.

### agen-alebench-short-opus5high

`claude-opus-5` as leaderboard configuration `claude-opus-5-high` (adaptive thinking; high effort), self-refine x1.

- Short-subset means: input 3,358 tokens, output 67,188, cost $1.6965, AtCoder performance 2360.6 (standard deviation across problems 557).
- Cache basis: no_cache_discount_billed, so input is counted gross.
- tokens = 15 x (3,358 + 67,188) = 1,058,184; compute = 1,058,184 x 2e+11 = 2.12e+17 FLOPs; cost = 15 x $1.6965 = $25.45.
- Mean rank 85.1 of a mean 708 entrants; 11.47% of the field finished above it, and it took 1st place outright on 1 of 23 contests.
- Ratio to the mean entrant: (2360.6 - 55.3) / (1414.5 - 55.3) = 1.696, standard error 0.085. Label **above**.

### agen-alebench-short-dsr10528

`deepseek-r1-0528` as leaderboard configuration `deepseek-r1-0528` (reasoning on), self-refine x1.

- Short-subset means: input 2,386 tokens, output 19,742, cost $0.0400, AtCoder performance 781.6 (standard deviation across problems 454).
- Cache basis: billed_at_rate_not_in_sheet (billed at the OpenRouter parasail/fp8 rate, which the sheet does not carry), so input is counted gross.
- tokens = 15 x (2,386 + 19,742) = 331,926; compute = 331,926 x 7.4e+10 = 2.46e+16 FLOPs; cost = 15 x $0.0400 = $0.60.
- Mean rank 603.6 of a mean 708 entrants; 87.77% of the field finished above it, and it never took 1st place.
- Ratio to the mean entrant: (781.6 - 55.3) / (1414.5 - 55.3) = 0.534, standard error 0.070. Label **below**.

### agen-alebench-short-gemini25flash

`gemini-2.5-flash` as leaderboard configuration `gemini-2.5-flash-thinking` (thinking budget 24576), self-refine x1.

- Short-subset means: input 2,669 tokens, output 24,680, cost $0.0625, AtCoder performance 720.2 (standard deviation across problems 443).
- Cache reads per call implied by the billed cost: 146 of 2,669 input tokens, removed from the parameter term.
- tokens = 15 x (2,669 - 146 + 24,680) = 408,054; compute = 408,054 x 8e+10 = 3.26e+16 FLOPs; cost = 15 x $0.0625 = $0.94.
- Mean rank 618.4 of a mean 708 entrants; 91.02% of the field finished above it, and it never took 1st place.
- Ratio to the mean entrant: (720.2 - 55.3) / (1414.5 - 55.3) = 0.489, standard error 0.068. Label **below** (close call, kept under the one-standard-error rule).
- Gross scenario, counting the cached prefix at full prefill: 410,237 tokens and 3.28e+16 FLOPs, 1.005x the central.

### agen-alebench-short-gemini25pro

`gemini-2.5-pro` as leaderboard configuration `gemini-2.5-pro-thinking` (thinking budget 32768), self-refine x1.

- Short-subset means: input 2,669 tokens, output 25,702, cost $0.2599, AtCoder performance 917.5 (standard deviation across problems 554).
- Cache reads per call implied by the billed cost: 444 of 2,669 input tokens, removed from the parameter term.
- tokens = 15 x (2,669 - 444 + 25,702) = 418,897; compute = 418,897 x 2e+11 = 8.38e+16 FLOPs; cost = 15 x $0.2599 = $3.90.
- Mean rank 531.4 of a mean 708 entrants; 78.34% of the field finished above it, and it never took 1st place.
- Ratio to the mean entrant: (917.5 - 55.3) / (1414.5 - 55.3) = 0.634, standard error 0.085. Label **below**.
- Gross scenario, counting the cached prefix at full prefill: 425,562 tokens and 8.51e+16 FLOPs, 1.016x the central.

### agen-alebench-short-gemini3flash

`gemini-3-flash-preview` as leaderboard configuration `gemini-3-flash-preview-high` (thinking level high), self-refine x1.

- Short-subset means: input 2,669 tokens, output 29,323, cost $0.0889, AtCoder performance 1477.3 (standard deviation across problems 515).
- Cache reads per call implied by the billed cost: 972 of 2,669 input tokens, removed from the parameter term.
- tokens = 15 x (2,669 - 972 + 29,323) = 465,295; compute = 465,295 x 8e+10 = 3.72e+16 FLOPs; cost = 15 x $0.0889 = $1.33.
- Mean rank 305.4 of a mean 708 entrants; 45.52% of the field finished above it, and it never took 1st place.
- Ratio to the mean entrant: (1477.3 - 55.3) / (1414.5 - 55.3) = 1.046, standard error 0.079. Label **match**.
- Gross scenario, counting the cached prefix at full prefill: 479,872 tokens and 3.84e+16 FLOPs, 1.031x the central.

### agen-alebench-short-gemini3pro-high

`gemini-3-pro-preview` as leaderboard configuration `gemini-3-pro-preview-high` (thinking level high), self-refine x1.

- Short-subset means: input 2,669 tokens, output 20,623, cost $0.2507, AtCoder performance 1339.3 (standard deviation across problems 625).
- Cache reads per call implied by the billed cost: 1,150 of 2,669 input tokens, removed from the parameter term.
- tokens = 15 x (2,669 - 1,150 + 20,623) = 332,120; compute = 332,120 x 2e+11 = 6.64e+16 FLOPs; cost = 15 x $0.2507 = $3.76.
- Mean rank 350.7 of a mean 708 entrants; 53.70% of the field finished above it, and it never took 1st place.
- Ratio to the mean entrant: (1339.3 - 55.3) / (1414.5 - 55.3) = 0.945, standard error 0.096. Label **match**.
- Gross scenario, counting the cached prefix at full prefill: 349,374 tokens and 6.99e+16 FLOPs, 1.052x the central.

### agen-alebench-short-gemini3pro-low

`gemini-3-pro-preview` as leaderboard configuration `gemini-3-pro-preview-low` (thinking level low), self-refine x1.

- Short-subset means: input 2,669 tokens, output 7,691, cost $0.0954, AtCoder performance 1035.1 (standard deviation across problems 602).
- Cache reads per call implied by the billed cost: 1,236 of 2,669 input tokens, removed from the parameter term.
- tokens = 15 x (2,669 - 1,236 + 7,691) = 136,857; compute = 136,857 x 2e+11 = 2.74e+16 FLOPs; cost = 15 x $0.0954 = $1.43.
- Mean rank 471.0 of a mean 708 entrants; 70.99% of the field finished above it, and it never took 1st place.
- Ratio to the mean entrant: (1035.1 - 55.3) / (1414.5 - 55.3) = 0.721, standard error 0.092. Label **below**.
- Gross scenario, counting the cached prefix at full prefill: 155,401 tokens and 3.11e+16 FLOPs, 1.135x the central.

### agen-alebench-short-gemini31flashlite

`gemini-3.1-flash-lite-preview` as leaderboard configuration `gemini-3.1-flash-lite-preview-high` (thinking level high), self-refine x1.

- Short-subset means: input 2,669 tokens, output 16,171, cost $0.0249, AtCoder performance 761.2 (standard deviation across problems 617).
- Cache basis: no_cache_discount_billed, so input is counted gross.
- tokens = 15 x (2,669 + 16,171) = 282,594; compute = 282,594 x 4e+10 = 1.13e+16 FLOPs; cost = 15 x $0.0249 = $0.37.
- Mean rank 577.9 of a mean 708 entrants; 83.78% of the field finished above it, and it never took 1st place.
- Ratio to the mean entrant: (761.2 - 55.3) / (1414.5 - 55.3) = 0.519, standard error 0.095. Label **below**.

### agen-alebench-short-gemini31pro-high

`gemini-3.1-pro-preview` as leaderboard configuration `gemini-3.1-pro-preview-high` (thinking level high), self-refine x1.

- Short-subset means: input 2,669 tokens, output 31,168, cost $0.3794, AtCoder performance 1280.4 (standard deviation across problems 787).
- Cache basis: no_cache_discount_billed, so input is counted gross.
- tokens = 15 x (2,669 + 31,168) = 507,556; compute = 507,556 x 2e+11 = 1.02e+17 FLOPs; cost = 15 x $0.3794 = $5.69.
- Mean rank 382.7 of a mean 708 entrants; 58.58% of the field finished above it, and it never took 1st place.
- Ratio to the mean entrant: (1280.4 - 55.3) / (1414.5 - 55.3) = 0.901, standard error 0.121. Label **match**.

### agen-alebench-short-gemini31pro-low

`gemini-3.1-pro-preview` as leaderboard configuration `gemini-3.1-pro-preview-low` (thinking level low), self-refine x1.

- Short-subset means: input 2,669 tokens, output 3,382, cost $0.0459, AtCoder performance 1146.2 (standard deviation across problems 492).
- Cache basis: no_cache_discount_billed, so input is counted gross.
- tokens = 15 x (2,669 + 3,382) = 90,757; compute = 90,757 x 2e+11 = 1.82e+16 FLOPs; cost = 15 x $0.0459 = $0.69.
- Mean rank 436.7 of a mean 708 entrants; 63.19% of the field finished above it, and it never took 1st place.
- Ratio to the mean entrant: (1146.2 - 55.3) / (1414.5 - 55.3) = 0.803, standard error 0.075. Label **below**.

### agen-alebench-short-gemini35flash

`gemini-3.5-flash` as leaderboard configuration `gemini-3.5-flash-high` (thinking level high), self-refine x1.

- Short-subset means: input 2,669 tokens, output 47,318, cost $0.4294, AtCoder performance 1015.8 (standard deviation across problems 974).
- Cache reads per call implied by the billed cost: 354 of 2,669 input tokens, removed from the parameter term.
- tokens = 15 x (2,669 - 354 + 47,318) = 744,501; compute = 744,501 x 8e+10 = 5.96e+16 FLOPs; cost = 15 x $0.4294 = $6.44.
- Mean rank 467.6 of a mean 708 entrants; 68.81% of the field finished above it, and it never took 1st place.
- Ratio to the mean entrant: (1015.8 - 55.3) / (1414.5 - 55.3) = 0.707, standard error 0.149. Label **below**.
- Gross scenario, counting the cached prefix at full prefill: 749,809 tokens and 6e+16 FLOPs, 1.007x the central.

### agen-alebench-short-glm47

`glm-4.7` as leaderboard configuration `glm-4.7` (reasoning on), self-refine x1.

- Short-subset means: input 2,507 tokens, output 19,371, cost $0.0437, AtCoder performance 374.2 (standard deviation across problems 402).
- Cache reads per call implied by the billed cost: 886 of 2,507 input tokens, removed from the parameter term.
- tokens = 15 x (2,507 - 886 + 19,371) = 314,885; compute = 314,885 x 6.4e+10 = 2.02e+16 FLOPs; cost = 15 x $0.0437 = $0.66.
- Mean rank 717.0 of a mean 708 entrants; 103.09% of the field finished above it, and it never took 1st place.
- Ratio to the mean entrant: (374.2 - 55.3) / (1414.5 - 55.3) = 0.235, standard error 0.062. Label **excluded**.
- Gross scenario, counting the cached prefix at full prefill: 328,176 tokens and 2.1e+16 FLOPs, 1.042x the central.

### agen-alebench-short-glm5

`glm-5` as leaderboard configuration `glm-5` (reasoning on), self-refine x1.

- Short-subset means: input 2,422 tokens, output 22,350, cost $0.0735, AtCoder performance 751.8 (standard deviation across problems 535).
- Cache reads per call implied by the billed cost: 554 of 2,422 input tokens, removed from the parameter term.
- tokens = 15 x (2,422 - 554 + 22,350) = 363,280; compute = 363,280 x 8e+10 = 2.91e+16 FLOPs; cost = 15 x $0.0735 = $1.10.
- Mean rank 587.9 of a mean 708 entrants; 84.35% of the field finished above it, and it never took 1st place.
- Ratio to the mean entrant: (751.8 - 55.3) / (1414.5 - 55.3) = 0.512, standard error 0.082. Label **below**.
- Gross scenario, counting the cached prefix at full prefill: 371,587 tokens and 2.97e+16 FLOPs, 1.023x the central.

### agen-alebench-short-glm52high

`glm-5.2` as leaderboard configuration `glm-5.2-high` (reasoning effort high), self-refine x1.

- Short-subset means: input 2,529 tokens, output 33,289, cost $0.1496, AtCoder performance 1108.5 (standard deviation across problems 587).
- Cache reads per call implied by the billed cost: 359 of 2,529 input tokens, removed from the parameter term.
- tokens = 15 x (2,529 - 359 + 33,289) = 531,892; compute = 531,892 x 8e+10 = 4.26e+16 FLOPs; cost = 15 x $0.1496 = $2.24.
- Mean rank 441.8 of a mean 708 entrants; 64.75% of the field finished above it, and it never took 1st place.
- Ratio to the mean entrant: (1108.5 - 55.3) / (1414.5 - 55.3) = 0.775, standard error 0.090. Label **below**.
- Gross scenario, counting the cached prefix at full prefill: 537,277 tokens and 4.3e+16 FLOPs, 1.010x the central.

### agen-alebench-short-glm52max

`glm-5.2` as leaderboard configuration `glm-5.2-max` (reasoning effort xhigh), self-refine x1.

- Short-subset means: input 2,437 tokens, output 33,358, cost $0.1490, AtCoder performance 995.3 (standard deviation across problems 583).
- Cache reads per call implied by the billed cost: 1,032 of 2,437 input tokens, removed from the parameter term.
- tokens = 15 x (2,437 - 1,032 + 33,358) = 521,438; compute = 521,438 x 8e+10 = 4.17e+16 FLOPs; cost = 15 x $0.1490 = $2.24.
- Mean rank 484.4 of a mean 708 entrants; 71.74% of the field finished above it, and it never took 1st place.
- Ratio to the mean entrant: (995.3 - 55.3) / (1414.5 - 55.3) = 0.692, standard error 0.089. Label **below**.
- Gross scenario, counting the cached prefix at full prefill: 536,923 tokens and 4.3e+16 FLOPs, 1.030x the central.

### agen-alebench-short-gpt41

`gpt-4.1-2025-04-14` as leaderboard configuration `gpt-4.1` (no reasoning), self-refine x1.

- Short-subset means: input 2,404 tokens, output 2,403, cost $0.0235, AtCoder performance 584.1 (standard deviation across problems 437).
- Cache reads per call implied by the billed cost: 345 of 2,404 input tokens, removed from the parameter term.
- tokens = 15 x (2,404 - 345 + 2,403) = 66,934; compute = 66,934 x 1e+11 = 6.69e+15 FLOPs; cost = 15 x $0.0235 = $0.35.
- Mean rank 680.3 of a mean 708 entrants; 96.94% of the field finished above it, and it never took 1st place.
- Ratio to the mean entrant: (584.1 - 55.3) / (1414.5 - 55.3) = 0.389, standard error 0.067. Label **excluded**.
- Gross scenario, counting the cached prefix at full prefill: 72,110 tokens and 7.21e+15 FLOPs, 1.077x the central.

### agen-alebench-short-gpt5minimal

`gpt-5` as leaderboard configuration `gpt-5` (reasoning effort minimal), self-refine x1.

- Short-subset means: input 2,403 tokens, output 3,816, cost $0.0407, AtCoder performance 790.0 (standard deviation across problems 421).
- Cache reads per call implied by the billed cost: 390 of 2,403 input tokens, removed from the parameter term.
- tokens = 15 x (2,403 - 390 + 3,816) = 87,436; compute = 87,436 x 2e+11 = 1.75e+16 FLOPs; cost = 15 x $0.0407 = $0.61.
- Mean rank 613.8 of a mean 708 entrants; 88.29% of the field finished above it, and it never took 1st place.
- Ratio to the mean entrant: (790.0 - 55.3) / (1414.5 - 55.3) = 0.541, standard error 0.065. Label **below**.
- Gross scenario, counting the cached prefix at full prefill: 93,280 tokens and 1.87e+16 FLOPs, 1.067x the central.

### agen-alebench-short-gpt5mini

`gpt-5-mini-2025-08-07` as leaderboard configuration `gpt-5-mini-thinking` (reasoning effort high), self-refine x1.

- Short-subset means: input 2,403 tokens, output 8,786, cost $0.0181, AtCoder performance 860.7 (standard deviation across problems 337).
- Cache reads per call implied by the billed cost: 545 of 2,403 input tokens, removed from the parameter term.
- tokens = 15 x (2,403 - 545 + 8,786) = 159,658; compute = 159,658 x 4e+10 = 6.39e+15 FLOPs; cost = 15 x $0.0181 = $0.27.
- Mean rank 601.3 of a mean 708 entrants; 86.53% of the field finished above it, and it never took 1st place.
- Ratio to the mean entrant: (860.7 - 55.3) / (1414.5 - 55.3) = 0.593, standard error 0.052. Label **below**.
- Gross scenario, counting the cached prefix at full prefill: 167,839 tokens and 6.71e+15 FLOPs, 1.051x the central.

### agen-alebench-short-gpt5nano

`gpt-5-nano` as leaderboard configuration `gpt-5-nano-thinking` (reasoning effort high), self-refine x1.

- Short-subset means: input 2,403 tokens, output 16,255, cost $0.0066, AtCoder performance 820.7 (standard deviation across problems 351).
- Cache reads per call implied by the billed cost: 657 of 2,403 input tokens, removed from the parameter term.
- tokens = 15 x (2,403 - 657 + 16,255) = 270,023; compute = 270,023 x 1.6e+10 = 4.32e+15 FLOPs; cost = 15 x $0.0066 = $0.10.
- Mean rank 612.7 of a mean 708 entrants; 88.31% of the field finished above it, and it never took 1st place.
- Ratio to the mean entrant: (820.7 - 55.3) / (1414.5 - 55.3) = 0.563, standard error 0.054. Label **below**.
- Gross scenario, counting the cached prefix at full prefill: 279,874 tokens and 4.48e+15 FLOPs, 1.036x the central.

### agen-alebench-short-gpt5high

`gpt-5-high` as leaderboard configuration `gpt-5-thinking` (reasoning effort high), self-refine x1.

- Short-subset means: input 2,403 tokens, output 23,285, cost $0.2356, AtCoder performance 1283.1 (standard deviation across problems 365).
- Cache reads per call implied by the billed cost: 211 of 2,403 input tokens, removed from the parameter term.
- tokens = 15 x (2,403 - 211 + 23,285) = 382,148; compute = 382,148 x 2e+11 = 7.64e+16 FLOPs; cost = 15 x $0.2356 = $3.53.
- Mean rank 420.6 of a mean 708 entrants; 59.70% of the field finished above it, and it never took 1st place.
- Ratio to the mean entrant: (1283.1 - 55.3) / (1414.5 - 55.3) = 0.903, standard error 0.056. Label **match**.
- Gross scenario, counting the cached prefix at full prefill: 385,321 tokens and 7.71e+16 FLOPs, 1.008x the central.

### agen-alebench-short-gpt51high

`gpt-5.1-2025-11-13` as leaderboard configuration `gpt-5.1-thinking` (reasoning effort high), self-refine x1.

- Short-subset means: input 2,403 tokens, output 32,815, cost $0.3299, AtCoder performance 1326.1 (standard deviation across problems 331).
- Cache reads per call implied by the billed cost: 1,130 of 2,403 input tokens, removed from the parameter term.
- tokens = 15 x (2,403 - 1,130 + 32,815) = 511,317; compute = 511,317 x 2e+11 = 1.02e+17 FLOPs; cost = 15 x $0.3299 = $4.95.
- Mean rank 397.1 of a mean 708 entrants; 56.18% of the field finished above it, and it never took 1st place.
- Ratio to the mean entrant: (1326.1 - 55.3) / (1414.5 - 55.3) = 0.935, standard error 0.051. Label **match**.
- Gross scenario, counting the cached prefix at full prefill: 528,263 tokens and 1.06e+17 FLOPs, 1.033x the central.

### agen-alebench-short-gpt52high

`gpt-5.2-2025-12-11` as leaderboard configuration `gpt-5.2-high` (reasoning effort high), self-refine x1.

- Short-subset means: input 2,403 tokens, output 20,212, cost $0.2846, AtCoder performance 1393.3 (standard deviation across problems 269).
- Cache reads per call implied by the billed cost: 1,647 of 2,403 input tokens, removed from the parameter term.
- tokens = 15 x (2,403 - 1,647 + 20,212) = 314,515; compute = 314,515 x 2e+11 = 6.29e+16 FLOPs; cost = 15 x $0.2846 = $4.27.
- Mean rank 348.2 of a mean 708 entrants; 50.51% of the field finished above it, and it never took 1st place.
- Ratio to the mean entrant: (1393.3 - 55.3) / (1414.5 - 55.3) = 0.984, standard error 0.041. Label **match**.
- Gross scenario, counting the cached prefix at full prefill: 339,225 tokens and 6.78e+16 FLOPs, 1.079x the central.

### agen-alebench-short-gpt52med

`gpt-5.2-2025-12-11` as leaderboard configuration `gpt-5.2-medium` (reasoning effort medium), self-refine x1.

- Short-subset means: input 2,403 tokens, output 9,329, cost $0.1323, AtCoder performance 1347.7 (standard deviation across problems 285).
- Cache reads per call implied by the billed cost: 1,586 of 2,403 input tokens, removed from the parameter term.
- tokens = 15 x (2,403 - 1,586 + 9,329) = 152,185; compute = 152,185 x 2e+11 = 3.04e+16 FLOPs; cost = 15 x $0.1323 = $1.98.
- Mean rank 363.2 of a mean 708 entrants; 53.12% of the field finished above it, and it never took 1st place.
- Ratio to the mean entrant: (1347.7 - 55.3) / (1414.5 - 55.3) = 0.951, standard error 0.044. Label **match**.
- Gross scenario, counting the cached prefix at full prefill: 175,976 tokens and 3.52e+16 FLOPs, 1.156x the central.

### agen-alebench-short-gpt54high

`gpt-5.4-2026-03-05` as leaderboard configuration `gpt-5.4-high` (reasoning effort high), self-refine x1.

- Short-subset means: input 4,308 tokens, output 39,182, cost $0.5949, AtCoder performance 1752.8 (standard deviation across problems 483).
- Cache reads per call implied by the billed cost: 1,603 of 4,308 input tokens, removed from the parameter term.
- tokens = 15 x (4,308 - 1,603 + 39,182) = 628,300; compute = 628,300 x 2e+11 = 1.26e+17 FLOPs; cost = 15 x $0.5949 = $8.92.
- Mean rank 231.7 of a mean 708 entrants; 33.66% of the field finished above it, and it never took 1st place.
- Ratio to the mean entrant: (1752.8 - 55.3) / (1414.5 - 55.3) = 1.249, standard error 0.074. Label **above**.
- Gross scenario, counting the cached prefix at full prefill: 652,342 tokens and 1.3e+17 FLOPs, 1.038x the central.

### agen-alebench-short-gpt54med

`gpt-5.4-2026-03-05` as leaderboard configuration `gpt-5.4-medium` (reasoning effort medium), self-refine x1.

- Short-subset means: input 6,581 tokens, output 14,890, cost $0.2354, AtCoder performance 1649.3 (standard deviation across problems 463).
- Cache reads per call implied by the billed cost: 1,942 of 6,581 input tokens, removed from the parameter term.
- tokens = 15 x (6,581 - 1,942 + 14,890) = 292,927; compute = 292,927 x 2e+11 = 5.86e+16 FLOPs; cost = 15 x $0.2354 = $3.53.
- Mean rank 257.0 of a mean 708 entrants; 38.45% of the field finished above it, and it never took 1st place.
- Ratio to the mean entrant: (1649.3 - 55.3) / (1414.5 - 55.3) = 1.173, standard error 0.071. Label **above**.
- Gross scenario, counting the cached prefix at full prefill: 322,060 tokens and 6.44e+16 FLOPs, 1.099x the central.

### agen-alebench-short-gpt54none

`gpt-5.4-2026-03-05` as leaderboard configuration `gpt-5.4-none` (reasoning effort none), self-refine x1.

- Short-subset means: input 2,403 tokens, output 3,195, cost $0.0518, AtCoder performance 1099.9 (standard deviation across problems 492).
- Cache reads per call implied by the billed cost: 957 of 2,403 input tokens, removed from the parameter term.
- tokens = 15 x (2,403 - 957 + 3,195) = 69,614; compute = 69,614 x 2e+11 = 1.39e+16 FLOPs; cost = 15 x $0.0518 = $0.78.
- Mean rank 488.6 of a mean 708 entrants; 70.58% of the field finished above it, and it never took 1st place.
- Ratio to the mean entrant: (1099.9 - 55.3) / (1414.5 - 55.3) = 0.769, standard error 0.075. Label **below**.
- Gross scenario, counting the cached prefix at full prefill: 83,972 tokens and 1.68e+16 FLOPs, 1.206x the central.

### agen-alebench-short-gpt55med

`gpt-5-5` as leaderboard configuration `gpt-5.5-medium` (reasoning effort medium), self-refine x1.

- Short-subset means: input 2,403 tokens, output 10,623, cost $0.3248, AtCoder performance 1705.3 (standard deviation across problems 606).
- Cache reads per call implied by the billed cost: 1,313 of 2,403 input tokens, removed from the parameter term.
- tokens = 15 x (2,403 - 1,313 + 10,623) = 175,692; compute = 175,692 x 3.46e+11 = 6.08e+16 FLOPs; cost = 15 x $0.3248 = $4.87.
- Mean rank 228.3 of a mean 708 entrants; 34.08% of the field finished above it, and it never took 1st place.
- Ratio to the mean entrant: (1705.3 - 55.3) / (1414.5 - 55.3) = 1.214, standard error 0.093. Label **above**.
- Gross scenario, counting the cached prefix at full prefill: 195,393 tokens and 6.76e+16 FLOPs, 1.112x the central.

### agen-alebench-short-gpt55none

`gpt-5-5` as leaderboard configuration `gpt-5.5-none` (reasoning effort none), self-refine x1.

- Short-subset means: input 2,403 tokens, output 2,274, cost $0.0755, AtCoder performance 1132.2 (standard deviation across problems 502).
- Cache reads per call implied by the billed cost: 1,046 of 2,403 input tokens, removed from the parameter term.
- tokens = 15 x (2,403 - 1,046 + 2,274) = 54,459; compute = 54,459 x 3.46e+11 = 1.88e+16 FLOPs; cost = 15 x $0.0755 = $1.13.
- Mean rank 452.5 of a mean 708 entrants; 65.66% of the field finished above it, and it never took 1st place.
- Ratio to the mean entrant: (1132.2 - 55.3) / (1414.5 - 55.3) = 0.792, standard error 0.077. Label **below**.
- Gross scenario, counting the cached prefix at full prefill: 70,153 tokens and 2.43e+16 FLOPs, 1.288x the central.

### agen-alebench-short-gpt55xhigh

`gpt-5-5` as leaderboard configuration `gpt-5.5-xhigh` (reasoning effort xhigh), self-refine x1.

- Short-subset means: input 2,403 tokens, output 50,295, cost $1.5158, AtCoder performance 2172.2 (standard deviation across problems 604).
- Cache reads per call implied by the billed cost: 1,124 of 2,403 input tokens, removed from the parameter term.
- tokens = 15 x (2,403 - 1,124 + 50,295) = 773,609; compute = 773,609 x 3.46e+11 = 2.68e+17 FLOPs; cost = 15 x $1.5158 = $22.74.
- Mean rank 117.2 of a mean 708 entrants; 16.96% of the field finished above it, and it took 1st place outright on 2 of 23 contests.
- Ratio to the mean entrant: (2172.2 - 55.3) / (1414.5 - 55.3) = 1.557, standard error 0.093. Label **above**.
- Gross scenario, counting the cached prefix at full prefill: 790,472 tokens and 2.74e+17 FLOPs, 1.022x the central.

### agen-alebench-short-luna56max

`gpt-5-6-luna` as leaderboard configuration `gpt-5.6-luna-max` (reasoning effort max), self-refine x1.

- Short-subset means: input 31,544 tokens, output 52,714, cost $0.3467, AtCoder performance 1877.3 (standard deviation across problems 412).
- Cache reads per call implied by the billed cost: 1,255 of 31,544 input tokens, removed from the parameter term.
- tokens = 15 x (31,544 - 1,255 + 52,714) = 1,245,039; compute = 1,245,039 x 1.6e+10 = 1.99e+16 FLOPs; cost = 15 x $0.3467 = $1.04.
- Mean rank 175.5 of a mean 708 entrants; 25.37% of the field finished above it, and it never took 1st place.
- Ratio to the mean entrant: (1877.3 - 55.3) / (1414.5 - 55.3) = 1.341, standard error 0.063. Label **above**.
- Gross scenario, counting the cached prefix at full prefill: 1,263,866 tokens and 2.02e+16 FLOPs, 1.015x the central.

### agen-alebench-short-sol56max

`gpt-5-6-sol` as leaderboard configuration `gpt-5.6-sol-max` (reasoning effort max), self-refine x1.

- Short-subset means: input 6,978 tokens, output 49,052, cost $1.4974, AtCoder performance 2375.0 (standard deviation across problems 548).
- Cache reads per call implied by the billed cost: 2,014 of 6,978 input tokens, removed from the parameter term.
- tokens = 15 x (6,978 - 2,014 + 49,052) = 810,245; compute = 810,245 x 2e+11 = 1.62e+17 FLOPs; cost = 15 x $1.4974 = $15.03.
- Mean rank 73.7 of a mean 708 entrants; 11.05% of the field finished above it, and it took 1st place outright on 1 of 23 contests.
- Ratio to the mean entrant: (2375.0 - 55.3) / (1414.5 - 55.3) = 1.707, standard error 0.084. Label **above**.
- Gross scenario, counting the cached prefix at full prefill: 840,458 tokens and 1.68e+17 FLOPs, 1.037x the central.

### agen-alebench-short-terra56max

`gpt-5-6-terra` as leaderboard configuration `gpt-5.6-terra-max` (reasoning effort max), self-refine x1.

- Short-subset means: input 2,403 tokens, output 80,168, cost $1.2043, AtCoder performance 2141.0 (standard deviation across problems 501).
- Cache reads per call implied by the billed cost: 1,899 of 2,403 input tokens, removed from the parameter term.
- tokens = 15 x (2,403 - 1,899 + 80,168) = 1,210,079; compute = 1,210,079 x 4e+10 = 4.84e+16 FLOPs; cost = 15 x $1.2043 = $14.45.
- Mean rank 106.7 of a mean 708 entrants; 15.99% of the field finished above it, and it took 1st place outright on 1 of 23 contests.
- Ratio to the mean entrant: (2141.0 - 55.3) / (1414.5 - 55.3) = 1.535, standard error 0.077. Label **above**.
- Gross scenario, counting the cached prefix at full prefill: 1,238,566 tokens and 4.95e+16 FLOPs, 1.024x the central.

### agen-alebench-short-astra6max

`gpt-6-astra` as leaderboard configuration `gpt-6-astra-max` (reasoning effort max), self-refine x1.

- Short-subset means: input 2,403 tokens, output 56,185, cost $2.8168, AtCoder performance 3273.7 (standard deviation across problems 327).
- Cache reads per call implied by the billed cost: 1,835 of 2,403 input tokens, removed from the parameter term.
- tokens = 15 x (2,403 - 1,835 + 56,185) = 851,290; compute = 851,290 x 6e+11 = 5.11e+17 FLOPs; cost = 15 x $2.8168 = $42.25.
- Mean rank 3.4 of a mean 708 entrants; 0.38% of the field finished above it, and it took 1st place outright on 14 of 23 contests.
- Ratio to the mean entrant: (3273.7 - 55.3) / (1414.5 - 55.3) = 2.368, standard error 0.050. Label **far_above**.
- Gross scenario, counting the cached prefix at full prefill: 878,822 tokens and 5.27e+17 FLOPs, 1.032x the central.

### agen-alebench-short-gptoss120b

`gpt-oss-120b` as leaderboard configuration `gpt-oss-120b` (reasoning effort high), self-refine x1.

- Short-subset means: input 2,467 tokens, output 2,129, cost $0.0013, AtCoder performance 523.5 (standard deviation across problems 151).
- Cache reads per call implied by the billed cost: 2,241 of 2,467 input tokens, removed from the parameter term.
- tokens = 15 x (2,467 - 2,241 + 2,129) = 35,312; compute = 35,312 x 1.02e+10 = 3.6e+14 FLOPs; cost = 15 x $0.0013 = $0.02.
- Mean rank 733.3 of a mean 708 entrants; 104.28% of the field finished above it, and it never took 1st place.
- Ratio to the mean entrant: (523.5 - 55.3) / (1414.5 - 55.3) = 0.345, standard error 0.023. Label **excluded**.
- Gross scenario, counting the cached prefix at full prefill: 68,933 tokens and 7.03e+14 FLOPs, 1.952x the central.

### agen-alebench-short-gptoss20b

`gpt-oss-20b` as leaderboard configuration `gpt-oss-20b` (reasoning effort high), self-refine x1.

- Short-subset means: input 2,468 tokens, output 3,346, cost $0.0008, AtCoder performance 510.2 (standard deviation across problems 325).
- Cache reads per call implied by the billed cost: 398 of 2,468 input tokens, removed from the parameter term.
- tokens = 15 x (2,468 - 398 + 3,346) = 81,233; compute = 81,233 x 7.2e+09 = 5.85e+14 FLOPs; cost = 15 x $0.0008 = $0.01.
- Mean rank 709.8 of a mean 708 entrants; 101.70% of the field finished above it, and it never took 1st place.
- Ratio to the mean entrant: (510.2 - 55.3) / (1414.5 - 55.3) = 0.335, standard error 0.050. Label **excluded**.
- Gross scenario, counting the cached prefix at full prefill: 87,202 tokens and 6.28e+14 FLOPs, 1.073x the central.

### agen-alebench-short-grok420

`grok-4.20-beta-0309b-reasoning` as leaderboard configuration `grok-4.20-beta` (reasoning on), self-refine x1.

- Short-subset means: input 2,453 tokens, output 21,425, cost $0.1308, AtCoder performance 1171.7 (standard deviation across problems 437).
- Cache basis: billed_at_rate_not_in_sheet (billed at an OpenRouter reseller rate the sheet does not carry), so input is counted gross.
- tokens = 15 x (2,453 + 21,425) = 358,169; compute = 358,169 x 2.3e+11 = 8.24e+16 FLOPs; cost = 15 x $0.1308 = $1.96.
- Mean rank 446.5 of a mean 708 entrants; 63.92% of the field finished above it, and it never took 1st place.
- Ratio to the mean entrant: (1171.7 - 55.3) / (1414.5 - 55.3) = 0.821, standard error 0.067. Label **below**.

### agen-alebench-short-kimik25

`kimi-k2.5` as leaderboard configuration `kimi-k2.5` (reasoning on), self-refine x1.

- Short-subset means: input 2,539 tokens, output 15,340, cost $0.0466, AtCoder performance 858.8 (standard deviation across problems 565).
- Cache reads per call implied by the billed cost: 1,811 of 2,539 input tokens, removed from the parameter term.
- tokens = 15 x (2,539 - 1,811 + 15,340) = 241,028; compute = 241,028 x 6.4e+10 = 1.54e+16 FLOPs; cost = 15 x $0.0466 = $0.70.
- Mean rank 549.1 of a mean 708 entrants; 79.63% of the field finished above it, and it never took 1st place.
- Ratio to the mean entrant: (858.8 - 55.3) / (1414.5 - 55.3) = 0.591, standard error 0.087. Label **below**.
- Gross scenario, counting the cached prefix at full prefill: 268,188 tokens and 1.72e+16 FLOPs, 1.113x the central.

### agen-alebench-short-kimik26

`kimi-k2.6` as leaderboard configuration `kimi-k2.6` (reasoning on), self-refine x1.

- Short-subset means: input 2,362 tokens, output 47,616, cost $0.1914, AtCoder performance 1034.5 (standard deviation across problems 530).
- Cache reads per call implied by the billed cost: 1,710 of 2,362 input tokens, removed from the parameter term.
- tokens = 15 x (2,362 - 1,710 + 47,616) = 724,001; compute = 724,001 x 6.4e+10 = 4.63e+16 FLOPs; cost = 15 x $0.1914 = $2.87.
- Mean rank 458.3 of a mean 708 entrants; 67.86% of the field finished above it, and it never took 1st place.
- Ratio to the mean entrant: (1034.5 - 55.3) / (1414.5 - 55.3) = 0.720, standard error 0.081. Label **below**.
- Gross scenario, counting the cached prefix at full prefill: 749,658 tokens and 4.8e+16 FLOPs, 1.035x the central.

### agen-alebench-short-kimik3max

`kimi-k3` as leaderboard configuration `kimi-k3-max` (reasoning effort max), self-refine x1.

- Short-subset means: input 3,160 tokens, output 73,905, cost $1.1160, AtCoder performance 1714.3 (standard deviation across problems 430).
- Cache reads per call implied by the billed cost: 757 of 3,160 input tokens, removed from the parameter term.
- tokens = 15 x (3,160 - 757 + 73,905) = 1,144,619; compute = 1,144,619 x 2.08e+11 = 2.38e+17 FLOPs; cost = 15 x $1.1160 = $16.74.
- Mean rank 227.1 of a mean 708 entrants; 33.57% of the field finished above it, and it never took 1st place.
- Ratio to the mean entrant: (1714.3 - 55.3) / (1414.5 - 55.3) = 1.221, standard error 0.066. Label **above**.
- Gross scenario, counting the cached prefix at full prefill: 1,155,972 tokens and 2.4e+17 FLOPs, 1.010x the central.

### agen-alebench-short-llama4maverick

`llama-4-maverick` as leaderboard configuration `llama-4-maverick` (no reasoning), self-refine x1.

- Short-subset means: input 2,356 tokens, output 1,420, cost $0.0013, AtCoder performance 173.3 (standard deviation across problems 267).
- Cache reads per call implied by the billed cost: 2,100 of 2,356 input tokens, removed from the parameter term.
- tokens = 15 x (2,356 - 2,100 + 1,420) = 25,134; compute = 25,134 x 3.4e+10 = 8.55e+14 FLOPs; cost = 15 x $0.0013 = $0.02.
- Mean rank 778.3 of a mean 708 entrants; 110.65% of the field finished above it, and it never took 1st place.
- Ratio to the mean entrant: (173.3 - 55.3) / (1414.5 - 55.3) = 0.087, standard error 0.041. Label **excluded**.
- Gross scenario, counting the cached prefix at full prefill: 56,633 tokens and 1.93e+15 FLOPs, 2.253x the central.

### agen-alebench-short-o3high

`o3-2025-04-16` as leaderboard configuration `o3-high` (reasoning effort high), self-refine x1.

- Short-subset means: input 2,403 tokens, output 12,635, cost $0.1053, AtCoder performance 935.1 (standard deviation across problems 437).
- Cache reads per call implied by the billed cost: 417 of 2,403 input tokens, removed from the parameter term.
- tokens = 15 x (2,403 - 417 + 12,635) = 219,311; compute = 219,311 x 1e+11 = 2.19e+16 FLOPs; cost = 15 x $0.1053 = $1.58.
- Mean rank 528.4 of a mean 708 entrants; 76.68% of the field finished above it, and it never took 1st place.
- Ratio to the mean entrant: (935.1 - 55.3) / (1414.5 - 55.3) = 0.647, standard error 0.067. Label **below**.
- Gross scenario, counting the cached prefix at full prefill: 225,572 tokens and 2.26e+16 FLOPs, 1.029x the central.

### agen-alebench-short-o4minihigh

`o4-mini-2025-04-16` as leaderboard configuration `o4-mini-high` (reasoning effort high), self-refine x1.

- Short-subset means: input 2,403 tokens, output 11,224, cost $0.0515, AtCoder performance 835.7 (standard deviation across problems 192).
- Cache reads per call implied by the billed cost: 601 of 2,403 input tokens, removed from the parameter term.
- tokens = 15 x (2,403 - 601 + 11,224) = 195,387; compute = 195,387 x 4e+10 = 7.82e+15 FLOPs; cost = 15 x $0.0515 = $0.77.
- Mean rank 628.0 of a mean 708 entrants; 90.35% of the field finished above it, and it never took 1st place.
- Ratio to the mean entrant: (835.7 - 55.3) / (1414.5 - 55.3) = 0.574, standard error 0.029. Label **below**.
- Gross scenario, counting the cached prefix at full prefill: 204,402 tokens and 8.18e+15 FLOPs, 1.046x the central.

### agen-alebench-short-qwen36plus

`qwen3.6-plus` as leaderboard configuration `qwen3.6-plus` (reasoning on), self-refine x1.

- Short-subset means: input 2,662 tokens, output 19,559, cost $0.0600, AtCoder performance 805.1 (standard deviation across problems 442).
- Cache basis: no_cache_discount_billed, so input is counted gross.
- tokens = 15 x (2,662 + 19,559) = 333,314; compute = 333,314 x 3.4e+10 = 1.13e+16 FLOPs; cost = 15 x $0.0600 = $0.90.
- Mean rank 578.6 of a mean 708 entrants; 83.71% of the field finished above it, and it never took 1st place.
- Ratio to the mean entrant: (805.1 - 55.3) / (1414.5 - 55.3) = 0.552, standard error 0.068. Label **below**.

### agen-alebench-short-qwen37max

`qwen3.7-max` as leaderboard configuration `qwen3.7-max` (reasoning on), self-refine x1.

- Short-subset means: input 2,662 tokens, output 51,166, cost $0.3904, AtCoder performance 1265.4 (standard deviation across problems 634).
- Cache basis: no_cache_discount_billed, so input is counted gross.
- tokens = 15 x (2,662 + 51,166) = 807,422; compute = 807,422 x 2e+11 = 1.61e+17 FLOPs; cost = 15 x $0.3904 = $5.86.
- Mean rank 390.4 of a mean 708 entrants; 57.98% of the field finished above it, and it never took 1st place.
- Ratio to the mean entrant: (1265.4 - 55.3) / (1414.5 - 55.3) = 0.890, standard error 0.097. Label **match**.

### agen-ahc058-ale-agent

- `gpt-5.2-2025-12-11`: 2,654 calls x (2,403 input + 20,212 output) per call, transferred from the leaderboard's `gpt-5.2-high` short-subset means, priced at $1.75/M input and $14.00/M output = $762 unscaled.
- `gemini-3-pro-preview`: 2,119 calls x (2,669 input + 20,623 output) per call, transferred from the leaderboard's `gemini-3-pro-preview-high` short-subset means, priced at $2.00/M input and $12.00/M output = $536 unscaled.


Unscaled the two models price to $1298. Sakana reports about $1000 in API fees, so the transferred cadence is scaled by k = 0.770, giving 84,272,848 counted tokens and 1.69e+19 FLOPs at the two models' 100B-active priors. Taking k = 1 instead (the unscaled cadence, which prices to the $1,300 all-in figure) gives 2.19e+19 FLOPs, 1.30x the central.
