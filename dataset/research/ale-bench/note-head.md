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
