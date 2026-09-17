# Kaggle Game Arena chess — evidence and calculation note

*Created 2026-09-13 09:10.*
*Last revised 2026-09-13 11:10, after independent review; see `candidates/game-arena/REVISION.md`.*

## TL;DR

Nine candidate rows across the two Kaggle Game Arena chess boards that publish an `Estimated Human Elo`
column: eight from **Chess Text version 1, evaluated 2025-08-21**, and one, GPT-5, from **Chess Openings
version 1**, which is the only board it appears on. The work unit is one move decision, following the
dataset's existing `game-chess-move-maia` and `game-chess-move-gpt35` rows. Compute per move runs 1.11e14
(GPT-4.1) to 5.35e15 (Grok 4) FLOPs, a 48-fold spread; human time is 7.1 seconds per move on every row. The
Estimated Human Elo blocker is resolved: the same unauthenticated Kaggle JSON API that returns only score,
tokens, and cost for the current 30-model board returns the human-Elo column when the request carries
`versionNumber: 1`, so no archive or rendered page was needed. Two assumptions dominate. First, on the
version 1 boards `Avg. Tokens/Turn` counts output tokens only and the prompt is added back from the boards'
own cost column; the cost column changes the FLOP total by 3% to 55% depending on the model. Second,
Kaggle's Estimated Human Elo is read as a Lichess blitz rating, which is what makes the Lichess move-time
evidence the right donor, and that reading rests on how the Stockfish anchors behind it were themselves
calibrated rather than on anything Kaggle says.

## The source

Board: `https://www.kaggle.com/benchmarks/kaggle/chess-text`. Kaggle's pages are client-rendered and the
host is blocked to the browser tool, so everything below comes from the unauthenticated JSON APIs, with the
retained responses under `agent-work/sources/game-arena/` and their exact call bodies in that folder's `PROVENANCE.md`.

Three boards matter. **Chess Text version 1** (benchmarkVersionId 129, evaluated 2025-08-21) carries ten
models plus a Kaggle-supplied "Grandmaster" reference row, with four columns: Score, `Estimated Human Elo*`,
`Avg. Tokens/Turn`, `Avg. Cost/Turn`. **Chess Openings version 1** (evaluated 2025-09-24, published
2025-10-21) carries ten models and the same four columns, over games that begin from an assigned opening
rather than the standard starting position.
**Chess Text version 2** (benchmarkVersionId 349, evaluated 2026-09-08) carries 30 models but only Score,
tokens, and cost; it contributes no row, and is used here only to fix what the token column counts.

### Resolving the Estimated Human Elo blocker

The scouting note recorded that the JSON API returns only score, tokens, and cost for the current board,
that the v1 REST path is permission-denied, and that the Internet Archive was down. None of that had to be
worked around. `GetBenchmarkLeaderboard` accepts a `VersionNumberSelector` inside its slug selector, and the
error text returned for a malformed identifier enumerates the accepted selectors:

    POST https://www.kaggle.com/api/i/benchmarks.BenchmarkService/GetBenchmarkLeaderboard
    {"versionIdentifier":{"benchmarkSlugSelector":{"ownerSlug":"kaggle","benchmarkSlug":"chess-text","versionNumber":1}}}

That returns the August 2025 board including child task 411, `Estimated Human Elo*`, with its bootstrap
interval per model. The same call with `benchmarkSlug: chess-text-openings, versionNumber: 1` returns the
openings board with the same column as child task 559.

The current 30-model board still has no human-Elo column exposed anywhere I could reach. Its version 2
record has exactly three child tasks. The Kaggle blog posts that might restate it are writeups reachable
through `discussions.WriteUpsService` with `{"slug": "<slug>", "forumName": "blog"}`; I read the Game Arena
posts that exist under guessable slugs — `chess-text-leaderboard` (2025-08-14), `game-arena-chess-openings`
(2025-10-21), and `game-arena-poker` and `game-arena-werewolf` (both 2026-02-02) — and none carries a
human-Elo figure for a board later than version 1. So the tokens-versus-human-Elo pairing is available only
for the version 1 model set.

### What Kaggle says it measures

The primary methodology statement is the Kaggle blog post of 2025-08-14, retained verbatim as
`agent-work/sources/game-arena/kaggle-blog-chess-text-leaderboard.md`. In its own words:

> The Chess Text leaderboard is the result of running all-play-all games across top AI models. The result is
> 20 games for white and black openings each for each model pair for a total of 40 per pair.

> The Game Arena Elo is computed using the standard Bradley-Terry algorithm taking outcomes from all-play-all
> matches between these models [...]. The human estimated Elos of these LLMs are estimated through playing
> matches between these models and Stockfish engines of different levels, and then linearly regressing using
> Stockfish's estimated human Elos. Confidence intervals are calculated by bootstrapping match results 500
> times and then calculating both the Game Arena Elo and the human Elos per bootstrap.

Kaggle does not publish which Stockfish levels it used, how many games it played against them, or the fitted
regression. So the Estimated Human Elo is a reported result that cannot be recomputed from public material;
what can be checked is its stability across boards and the scale its anchors sit on.

### The harness

The chess harness is open source at `google-deepmind/game_arena`. Its `NO_LEGAL_ACTIONS` prompt template is
retained as `agent-work/sources/game-arena/game-arena-chess-prompt-template.txt` and matches the rendered prompt in the
published replays character for character. Every chess episode in the replay archive records
`useOpenings=false`, `includeLegalActions=false`, `useImage=false`, `illegalMoveForfeit=true`, and
`actTimeout=3600`. So the model is given the position in FEN plus the move list as text, no legal-move list
and no board image, and must return one move in standard algebraic notation after step-by-step reasoning. An
illegal or unparseable answer is retried; exhausting the retries forfeits the game.

That configuration is observed on version 2 episodes only. The version 1 archive is gone — the current
`kaggle/chess-text-gameplay` archive holds only the current model set, and versioned dataset downloads
(`?datasetVersionNumber=1`) return 404 without credentials — so for version 1 it is a transfer. The part
that matters for `different_inputs_or_tools` is independently supported by the benchmark's own version 1
description, "Chess with the board represented in FEN/PGN formats".

## Work unit: one move

The dataset's two existing LLM and neural-network chess rows both use one move — `game-chess-move-maia` is
"one post-opening decision by released Maia-1500", and `game-chess-move-gpt35` is "one legal chess move,
averaging total generation work across 4823 accepted moves". One move is also the unit the boards themselves
normalize to: the compute column is `Avg. Tokens/Turn`, described by Kaggle as "Average number of tokens per
move". Taking one move keeps these rows directly comparable with the existing chess points and avoids
inventing a per-game move count that the version 1 boards do not publish.

## Compute side

### What `Avg. Tokens/Turn` counts: the cost column settles it, and the answer differs by board version

The column's description is "Average number of tokens per move", which does not say whether prompt tokens
are included. The answer is **not the same on both board versions**, which is the single most consequential
finding in this note and the one the first submission got wrong.

Write `T` for the published `Avg. Tokens/Turn`, `P` for mean prompt tokens per move, and `p_in`, `p_out` for
the model's list prices. Two readings predict different costs, and their difference has a sign that does not
require knowing `P`:

- **H1**, `T = P + output`: cost `= p_in·P + p_out·(T − P)`, which is **below** `p_out·T`, because
  `p_in < p_out`.
- **H2**, `T` is output only: cost `= p_in·P + p_out·T`, which is **above** `p_out·T`.

So comparing the implied price `cost/T` with the model's list output price decides between them, and the
decision holds at any non-negative prompt length. On the **Chess Openings version 1** board, whose cost
column carries two decimal places:

| Model | `Avg. Tokens/Turn` | List output price (USD/1M) | `p_out·T` (cents) | Published cost (cents) | Implied USD/1M | Prompt solved | ± |
|---|---|---|---|---|---|---|---|
| o3 | 9986 | 8.00 | 7.9888 | 8.06 | 8.071 | 356.0 | 25 |
| GPT-5 | 12129 | 10.00 | 12.1290 | 12.17 | 10.034 | 328.0 | 40 |
| Grok 4 | 24738 | 15.00 | 37.1070 | 37.41 | 15.122 | 1010.0 | 17 |
| Gemini 2.5 Pro | 4207 | 10.00 | 4.2070 | 4.25 | 10.102 | 344.0 | 40 |
| o4 mini | 9335 | 4.40 | 4.1074 | 4.15 | 4.446 | 387.3 | 45 |
| GPT-4.1 | 751 | 8.00 | 0.6008 | 0.68 | 9.055 | 396.0 | 25 |
| Claude Sonnet 4 | 10666 | 15.00 | 15.9990 | 16.15 | 15.142 | 503.3 | 17 |
| Claude Opus 4 | 2932 | 75.00 | 21.9900 | 22.77 | 77.660 | 520.0 | 3 |
| Gemini 2.5 Flash | 11195 | 2.50 | 2.7988 | 2.81 | 2.510 | 375.0 | 167 |

The published cost exceeds `p_out·T` for all nine, so H1 is impossible for every one of them. The same test
on the **Chess Text version 1** board gives the same verdict for every model that carries a price, the
implied prices being 8.078, 15.045, 10.063, 4.455, 8.358, 15.122, 77.105, and 2.556 USD per million against
list output prices of 8.00, 15.00, 10.00, 4.40, 8.00, 15.00, 75.00, and 2.50.

On **Chess Text version 2** the test flips. There the implied price falls *below* the list output price for
every model I have a price for — o3 7.887 against 8.00, Grok 4 14.383 against 15.00, GPT-5 mini 1.950
against 2.00, Claude Sonnet 4.5 14.143 against 15.00, Claude Opus 4.6 22.735 against 25.00 — so H2 is
impossible there and H1 holds. Solving the version 2 costs under H1 recovers prompt lengths of 355, 1050,
357, 427, and 421 tokens, against replay-measured means for those same five models of 365, 1018, 363, 501,
and 456. **The column changed meaning between board versions.**

Two independent lines therefore agree on version 2: its replay archive and its cost column. Only the cost
column is available for version 1, and it is unambiguous there.

The first submission established the identity on the version 2 replays and transferred it to version 1 on
the strength of the identical child-task description, while explicitly setting the cost column aside as
unable to discriminate. That was wrong on both counts. `Avg. Cost/Turn` is not a FLOP measurement and
COLUMNS.md is right that billing units are not one, but it is admissible evidence about *what the token
column counts*, and for version 1 it is the only evidence there is.

**The prices are not taken on trust.** They are inputs, but a wrong output price does not produce the table
above: it produces a negative solved prompt, or one in the tens of thousands of tokens. Every one of the
nine lands between 328 and 1010 tokens, which is what a FEN plus a growing move list plus a short fixed
instruction actually costs. The two models that appear on both a version 1 board and the version 2 replay
archive pin it further: the openings cost column implies 356 tokens for o3 against 365 measured, and 1010
for Grok 4 against 1017.9 measured — Grok 4's distinctive thousand-token prompt recovered to within eight
tokens from nothing but a published cost and a list price.

### Reasoning tokens are inside the count

Three lines of evidence, two of them independent of each other:

- Across all 5,686 replay episodes, `reasoning_tokens > generation_tokens` never occurs on a single call, and
  for well-populated reasoning models the residual is a plausible final answer: Claude Opus 5 generation 5914
  against reasoning 5324, residual 590; GPT-5.6 Sol 5237 and 5164, residual 73; Grok 4.5 16072 and 15751,
  residual 321.
- In the retained episode excerpt a Gemini 3.7 Flash call reports prompt 134, generation 335, reasoning 179
  and total 469, and 134 + 335 = 469, so the 179 reasoning tokens sit inside the 335.
- On version 1 the cost column confirms it without touching the replays at all. The implied price per
  published token lands within 1% of each model's list *output* price for seven of nine (3.5% for Claude
  Opus 4, 13% for GPT-4.1, both of which carry the largest prompt fraction). If reasoning tokens were missing
  from the published count, the implied price would sit far above the output price rather than just above it.

### Adding the prompt back

For the eight Chess Text rows the output-token count comes from that board and the prompt from the Chess
Openings board's cost solve, which is the tightest version 1-era estimate available: same harness, same
prompt template, model-specific, and two decimal places of cost rather than one. The Chess Text board's own
cost column is published to one decimal, which bounds the prompt only to ±250 to ±1667 tokens and so does
not constrain it usefully. Using a prompt measured on one board with output tokens from another is a real
seam, and it matters most for GPT-4.1, where the prompt is 36% of the corrected total; for every other row
it is under 9%.

DeepSeek-R1-0528 is the one model with no published list price for its hosted endpoint, so its prompt
cannot be solved the way the other eight are. The obvious substitute does not work. Its two version 1 boards
share a prompt and a price, so the marginal cost per published token gives a central output price of
`(10.80 − 9.50) cents / (15240 − 13389.6) tokens` = 7.03 USD per million, which does match a known $3/$7 per
million host pair to within 0.4%. But **both** boards publish cost rounded, and propagating both roundings
leaves the output price only loosely bounded, at **6.49 to 7.57**, and the prompt not bounded at all: the
interval runs **−2268 to +2889 tokens**. A negative prompt is impossible, so the solve is uninformative
about prompt length, and it cannot be what supports the row.

What supports it instead is the prompt structure, which is the same text for every model on this harness —
a FEN, a growing move list, and a fixed instruction — so prompt length varies only by tokenizer and game
length. The eight prompts solved from published list prices span 328 to 1010 tokens, and 328 to 520 once
Grok 4's distinctive xAI tokenization is set aside. I use **310.4 tokens**, the two-board solve's central
figure, which sits just below that band. The row is insensitive to the choice: moving the prompt across the
whole 328 to 520 band changes compute by under 1.6%, and substituting DeepSeek V3.2's replay-measured 423.7
tokens, on the same tokenizer, changes it by 0.8%. This is the weakest of the nine prompt estimates, and it
is also the one that matters least.

The prompt estimate barely moves the rows. Substituting the replay-measured prompt for every model — the
same model where it exists, the nearest sibling on the same harness otherwise — changes compute by at most
2.1% (GPT-4.1) and by under 0.3% for six of the nine. Those alternatives are carried in
`agent-work/derived/game-arena/calculations.json` as `prompt_scenario_replay_measured`.

### Cache accounting

The harness records no cache fields at all: no cache-read, cache-creation, or cached-prompt counter exists
anywhere in `call_details` or `generate_returns`. The prompt is short and changes on every move, because it
carries the FEN and the growing move list, and the shared prefix is the roughly 100 tokens of fixed
instruction text. Nothing suggests a cache is in play, and a cache read of that prefix would be immaterial
against the thousands of generated tokens. These rows therefore count all prompt and generated tokens once,
with `tokens_accounting: input_output`, and claim no cache decomposition. That label is only correct once the
prompt is restored; with output tokens alone, no enum value in COLUMNS.md would describe the counted
quantity.

### Retries

Retried calls are included: on version 2 the per-move sums that reproduce the published averages include
every call, and calls per move run 1.00 to 1.27 across models. The retained excerpt shows one such move,
Claude Opus 4.6 playing `Qf5+` over two calls, 350 + 381 prompt tokens and 959 + 667 generated. The version 1
cost column likewise prices whatever the harness billed, retries included.

### The version 2 replay check, and what it does and does not show

`research/game-arena/aggregate_replays.py` parses all 5,686 episodes of `kaggle/chess-text-gameplay` and
aggregates per-call counters by model; the output is `agent-work/sources/game-arena/chess-replay-usage-by-model.json`.
Restricting to the 12 models whose counters are internally consistent, mean(prompt + generation) per move
over the published `Avg. Tokens/Turn` has median 1.013, with ten of the twelve between 0.987 and 1.021.

Two qualifications the first submission did not make. First, the published version 2 column actually tracks
the provider's `total_tokens` counter rather than `prompt_tokens + generation_tokens`; on the verification
subset the two are equal by construction, so that subset cannot tell them apart, and where they differ the
published value follows `total_tokens` — Grok 4 publishes 20397 against a replay `total_tokens` mean of 22964
and a prompt-plus-generation mean of 1189, Gemini 3 Flash Preview 8449 against 8334 and 4615, Grok 4.3 10238
against 10393 and 2833. The models where the prompt-plus-generation reading works are those where
`generation_tokens` is correctly populated; the ones where it fails are those where the provider reports only
the final answer there and the reasoning only in `total_tokens`. Second, the filter that builds the
verification subset is not neutral with respect to the result it tests: excluding a model for any
zero-valued `total_tokens` call drops Claude Opus 4.6 (ratio 1.158, one bad call in roughly 9,100), Claude
Sonnet 4.6 (1.166, one bad call) and DeepSeek V3.2 (1.319, 22 bad calls), all deviating in the same direction
as the two outliers the subset does contain.

None of this changes a number, because the version 1 rows now rest on the cost column rather than on the
replays.

### Arithmetic

`compute_flops = (published output tokens + estimated prompt tokens) × flops_per_token`, with
`flops_per_token = 2 × active_parameters` from the model record. Eight of the nine models already have
records in the main dataset's `models.csv` and are reused unchanged, including their active-parameter
assumptions; only DeepSeek-R1-0528 is new. `compute_flops` additionally carries the cached-context
attention term of `research/attention-correction.md`; the FLOPs/move column below is the parameter
term alone.

| Model | Board | Output tokens | Prompt | Total | FLOPs/token | FLOPs/move |
|---|---|---|---|---|---|---|
| o3 | Chess Text v1 | 9532.6 | 356.0 | 9888.6 | 1.0e11 | 9.8886e14 |
| GPT-5 | Chess Openings v1 | 12129 | 328.0 | 12457 | 2.0e11 | 2.4914e15 |
| Grok 4 | Chess Text v1 | 22267.11661 | 1010.0 | 23277.11661 | 2.3e11 | 5.3537368203e15 |
| Gemini 2.5 Pro | Chess Text v1 | 4074.4 | 344.0 | 4418.4 | 2.0e11 | 8.8368e14 |
| o4 mini | Chess Text v1 | 8977.8 | 387.3 | 9365.1 | 4.0e10 | 3.746040e14 |
| GPT-4.1 | Chess Text v1 | 717.9 | 396.0 | 1113.9 | 1.0e11 | 1.11390e14 |
| Claude Sonnet 4 | Chess Text v1 | 10316 | 503.3 | 10819.3 | 2.0e11 | 2.163860e15 |
| Claude Opus 4 | Chess Text v1 | 3177.5 | 520.0 | 3697.5 | 3.6e11 | 1.33110e15 |
| DeepSeek-R1-0528 | Chess Text v1 | 13389.6 | 310.4 | 13700 | 7.4e10 | 1.01380e15 |

The statistic is each board's own mean over every move the model played, so `compute_statistic: mean` and
`compute_subset: all`. `ai_attempts` is `not_applicable`: the published figure is a board aggregate
normalized per turn, and COLUMNS.md excludes turns used to normalize a benchmark aggregate from that count.

`compute_evidence: derived_assumed_inputs` on all nine. The reason is the prompt component, which is solved
from a billing column at assumed list prices rather than measured for these runs, and — for eight of the
nine — the active-parameter count, which is an estimate for every closed model here. DeepSeek-R1-0528's
active count is `reported`, not estimated, so that second reason does not apply to it; its label rests on
the prompt term alone.

## Human side

### Population and its strength

The human baseline is an online blitz player whose rating equals the model's Estimated Human Elo. That is the
same construction the dataset already uses for `game-chess-move-maia`, which compares Maia-1500's single-node
move with "an ordinary approximately 1500-rated Lichess blitz player".

Which pool the rating belongs to is the load-bearing question, because a 1686 FIDE player and a 1686 Lichess
blitz player are not the same person. Kaggle does not say. The chain that does say something runs through the
anchors: Kaggle regresses onto "Stockfish's estimated human Elos", citing `official-stockfish/Stockfish`
issue 3635. In that thread, vondele describes a calibrated `UCI_Elo` scheme as "calibrated at 1500 Elo
against the maia engine at lichess", and lucasart states that "in this context we are referring to 1500 elo
for the lichess blitz rating scale". So the Stockfish scale is nominally a Lichess blitz scale, and the
Estimated Human Elo inherits that.

The chain is looser than those two quotes make it look. vondele's remark is about his experimental
`vondele/Stockfish:rep` branch with `RandomEvalPerturb`, which was never merged, while the 1347–2886 Skill
Level numbers Kaggle would have used come from dav1312's unsourced table for released Stockfish. Both sit in
the same thread and the whole thread is Lichess-facing, so the Lichess blitz reading remains the most
defensible one available, but it is an inference about a family of calibrations rather than a single
documented one.

The thread also records the calibration's known bias, and its direction matters. vondele writes that at 1500
Elo the engine "matches maia5 in a direct match quite well, however, for humans it seems clearly stronger".
Suppose an anchor set to nominal `N` really plays at human-scale `N + Δ` with `Δ > 0`, and let the model's
true human-equivalent rating be `R`. The observed score follows the true strengths, `S = f(R − N − Δ)`, while
Kaggle's regression reads it as `S = f(R_est − N)`, so `R_est = R − Δ`. **The published Estimated Human Elo is
therefore lower than the model's true human-equivalent strength: Kaggle's column is conservative, not
optimistic.** I have not adjusted for this, because the thread gives a direction and not a magnitude.

This changes no number, and `performance_vs_human: match` remains correct either way, because the human
population is selected *at* the published rating by construction and because the timing donor varies by only
10% across the whole rating range. It matters because a reader will use the direction.

### Move times

The timing donor is Russek (2025), DOI 10.1111/cogs.70119, whose published aggregates give count-weighted
mean own-clock seconds per move by time control and Lichess rating bin. The aggregates and the code that
builds them are at `https://github.com/evanrussek/Thinking_Time_VOC_Chess`, retained revision
`0f21b31c05bec0494bc3c5da2e14c0be55fa345e`; the rows' `human_time_source` cites the DOI and the retained
output, and this is the repository locator behind them. This is the same donor and the same
recomputation script the main dataset already uses for its Maia and GPT-3.5 chess rows; I reran it rather
than copying its outputs, and it reproduces the numbers those rows quote (7.090 seconds for the (1250,1525]
bin at 5+0, and 4.310 seconds for the (1800,3000] bin at 3+0). Output retained as
`agent-work/sources/game-arena/russek-move-times-by-elo-bin.json`, with the verified input Git blob hashes.

Five-minute games without increment (300+0) are the primary time control, matching `game-chess-move-maia`.
At that control:

| Lichess blitz rating bin | Mean own-clock seconds per move | Move observations |
|---|---|---|
| (0,1250] | 7.568 | 25908504 |
| (1250,1525] | 7.090 | 27844861 |
| (1525,1800] | 6.935 | 24559078 |
| (1800,3000] | 6.909 | 18043931 |

Own-clock move time in a fixed-budget game is set mostly by the clock, not by the player's strength: the
four bins span 6.909 to 7.568 seconds, under 10%, while the compute across these nine rows spans a factor
of 48. All nine rows therefore record the count-weighted mean over the whole rating range at 300+0 rather
than the bin matching each model's Estimated Human Elo,

    (25908504 x 7.568 + 27844861 x 7.090 + 24559078 x 6.935 + 18043931 x 6.909) / 96356374 = 7.145 s,

recorded as **7.1 seconds** on the file's one-decimal precedent, with `human_attempts` the pooled
96,356,374 move observations. Damon ruled on 2026-09-16 that one task carries one human time, and the
rating-invariance above is what makes the pooled figure the right transfer for every row: the per-bin
figures were varying with the model's strength, not with the work. The human axis being close to a constant
here is a property of the comparison, not a failure of it. The dataset's question is what compute buys at a
given human-equivalent performance, and at blitz the human's time per move is roughly fixed by the format.

These are own-clock intervals, the difference between consecutive clock readings for the same player plus the
increment, restricted by the source's preprocessing to plies 15 to 75. They exclude thinking during the
opponent's turn and include move entry. No successful-outcome selection applies, so `human_time_subset: all`.
`human_attempts` is the bin's move-observation count; raw participants cannot be deduplicated from published
aggregates.

`human_time_statistic: mean` on all nine rows, because the recorded value is literally the count-weighted
arithmetic mean of the donor's move times. The existing `game-chess-move-maia` row is a different task
under `task_id` and keeps its own (1250,1525] bin figure of 7.090 seconds as a `point_estimate`; on
COLUMNS.md's definitions `mean` is the accurate label there too, so that discrepancy is the precedent's and
is not touched here.

### What the models actually took

The comparison's clock asymmetry is not hypothetical. `actTimeout=3600` is a configured ceiling, but
`call_details[].duration_secs` records what the models really spent, and summing it per move across the
330,939 version 2 moves that carry the field gives per-model means from 5.1 seconds (Gemini 3.7 Flash) to
275.4 seconds (Grok 4.6), with a median across models of 50.2 seconds. o3, the one model on both the version
1 and version 2 chess boards, averages 203.1 seconds per move with a median of 176.0. The human baseline is
7 seconds per move inside a five-minute budget for the whole game. That is what `different_assessment`
carries. Retained as `agent-work/sources/game-arena/chess-replay-durations-and-call-details-coverage.json`.

### Alternative time controls as scenarios

The choice of 5+0 is a convention, not a measurement of this task. The same bins at other controls, for the
(1525,1800] bin holding o3 and GPT-5:

| Time control | Mean own-clock seconds per move |
|---|---|
| 180+0 | 4.356 |
| 180+2 | 6.912 |
| 300+0 | 6.935 |
| 300+3 | 10.892 |

So the human axis moves by a factor of 2.5 across the plausible blitz range, and by much more if a classical
control were chosen instead; Russek's published aggregates do not cover controls slower than 300+3 in the
files the recomputation script reads. Anyone rescaling these rows to a different control should move all nine
together.

## Performance comparison

`performance_vs_human: match` on all nine rows. The human population is selected at the model's Estimated
Human Elo, so strength is matched by that selection. It is not an observed result against humans: no model on
either board played a human, and the estimate is a regression through engine play.

`comparison_issues: different_inputs_or_tools; different_assessment` on all nine. The inputs differ because
the model reads a FEN string and a text move list while the human reads a board, which is the same flag the
existing `game-chess-move-gpt35` row carries for the same reason. The assessment differs because the model's
strength comes from engine matches regressed onto a Stockfish scale while the human's comes from a Lichess
rating, and because of the clock asymmetry quantified above.

### Cross-check on the Elo estimate

Eight of the nine models carry an Estimated Human Elo on both version 1 boards, which are two independent
all-play-all runs on a task differing only in the forced opening:

| Model | Chess Text v1 | Chess Openings v1 | Difference |
|---|---|---|---|
| o3 | 1686 | 1688 | 2 |
| Grok 4 | 1395 | 1397 | 2 |
| Gemini 2.5 Pro | 1343 | 1352 | 9 |
| o4 mini | 1109 | 1061 | -48 |
| GPT-4.1 | 759 | 708 | -51 |
| Claude Sonnet 4 | 703 | 678 | -25 |
| Claude Opus 4 | 667 | 671 | 4 |
| DeepSeek-R1 | 664 | 707 | 43 |

Every difference sits inside the reported bootstrap interval, and Kaggle says the same thing in its own
write-up of the openings board: "Among overlapping models, Estimated Human Elo values on the Openings
leaderboard are roughly unchanged from their scores on the original Text leaderboard, typically within the
stated uncertainty ranges." That does not validate the scale, which is the real uncertainty, but it does show
the estimate is stable across two runs. GPT-5 appears on the openings board only, so its rating carries no
such check.

The same post warns against the comparison these rows are built on: "Because Elo ratings are
leaderboard-relative, we focus on within-board comparisons and rank order rather than absolute scores across
leaderboards." That caution applies squarely to the Game Arena Elo, which is a Bradley-Terry fit to one
board's results and has no meaning off it. The Estimated Human Elo is the column built precisely to escape
that, since it is anchored to engines outside the board rather than to the field — but it is a regression
through those anchors, so Kaggle's warning is a reason to treat these rows as one internally consistent set
rather than as nine independently placed points on a human rating scale.

### The low-Elo rows

The published Stockfish skill-level Elo mapping in issue 3635 runs from 1347 at level 0 to 2886 at level 19.
Six of these nine models are placed below 1347 and four below 800. Kaggle does not publish its anchor set, so
I cannot tell whether those placements are interpolation or extrapolation below the lowest anchor. Treat the
four sub-800 values as the weakest part of the collection; their bootstrap intervals are correspondingly
wide, ±120 to ±167 against ±41 to ±53 for the top three. Because the timing donor's lowest bin covers
everything up to 1250 at 7.568 seconds, even a large Elo error there changes no recorded number.

### The novice/typical cut

`typical` above 1250 and `novice` below. The reason is not that the timing bin happens to break there. On
COLUMNS.md's definitions, `typical` is "ordinary people without selection for specialist or elite skill" and
`novice` is "people with little or no task-specific training or experience". A Lichess blitz player rated
664 to 759 is a beginner who has not internalized basic tactics; one rated 1343 to 1686 plays recognizable
club chess, and the dataset already labels an approximately 1500-rated player `typical` in
`game-chess-move-maia`. The only row where the cut is arguable is
`game-chess-move-arena-o4mini` at 1109, and nothing numeric turns on it, since that rating sits in the same
timing bin either way.

## Points

Shared across all nine: `task_category: games`, `compute_scope: inference`, `human_time_scope:
task_performance`, `compute_method: params_tokens`, `compute_statistic: mean`, `compute_subset: all`,
`ai_attempts: not_applicable`, `compute_evidence: derived_assumed_inputs`, `tokens_accounting: input_output`,
`human_time_evidence: transferred_timings`, `human_time_method: estimated`, `human_time_statistic: mean`,
`human_time_subset: all`, `performance_vs_human: match`, and
`comparison_issues: different_inputs_or_tools; different_assessment`.

### game-chess-move-arena-o3

o3, board slug `openai/o3-2025-04-16`, model record `o3-2025-04-16` reused unchanged (50B active, 1.0e11
FLOPs per token). Chess Text v1: Game Arena Elo 1397 (+99/-73); Estimated Human Elo 1686 (±53);
`Avg. Tokens/Turn` 9532.6 output tokens; `Avg. Cost/Turn` 7.7 cents. Prompt 356.0 tokens from the openings
cost solve, within 9 tokens of o3's own replay-measured 365.0. Compute (9532.6 + 356.0) × 1.0e11 =
**9.8886e14 FLOPs** per move. Human Elo 1686 falls in the (1525,1800] bin, whose own mean is 6.909 seconds;
the row records the rating-pooled **7.1 seconds** over 96,356,374 move observations.
`human_skill: typical`.

### game-chess-move-arena-gpt5

GPT-5, board slug `openai/gpt-5-2025-08-07`, model record `gpt-5` reused unchanged (100B active, 2.0e11 FLOPs
per token). **This row comes from the Chess Openings version 1 board, evaluated 2025-09-24**, where games
begin from an assigned opening; GPT-5 appears on no other Game Arena chess board in any version, so it is
not a duplicate of any Chess Text row and has no cross-board Elo check. Every other row is evaluated
2025-08-21 on the Chess Text board. Game Arena Elo 1275 (+91/-81); Estimated Human Elo 1641
(+42/-41); `Avg. Tokens/Turn` 12129 output tokens; `Avg. Cost/Turn` 12.17 cents. Prompt 328.0 tokens.
Compute (12129 + 328.0) × 2.0e11 = **2.4914e15 FLOPs** per move. Human Elo 1641 falls in the (1525,1800]
bin, whose own mean is 6.909 seconds; the row records the rating-pooled **7.1 seconds** over
96,356,374 move observations. `human_skill: typical`. Kaggle's own write-up of that
board calls GPT-5 out: "the arrival of GPT-5 introduces a new high-skill contender".

### game-chess-move-arena-grok4

Grok 4, board slug `xai/grok-4-0709`, model record `grok-4` reused unchanged (115B active, 2.3e11 FLOPs per
token). Chess Text v1: Game Arena Elo 1112 (+90/-71); Estimated Human Elo 1395 (+46/-52);
`Avg. Tokens/Turn` 22267.11661 output tokens; `Avg. Cost/Turn` 33.5 cents. Prompt 1010.0 tokens, recovered
from the openings cost column to within 8 tokens of Grok 4's own replay-measured 1017.9 — the tightest
confirmation available that the cost solve works. Compute (22267.11661 + 1010.0) × 2.3e11 =
**5.3537368203e15 FLOPs** per move, the largest of the nine and 48 times GPT-4.1's. Human Elo 1395 falls in
the (1250,1525] bin, whose own mean is 7.090 seconds; the row records the rating-pooled
**7.1 seconds** over 96,356,374 move observations. `human_skill: typical`.

### game-chess-move-arena-gemini25pro

Gemini 2.5 Pro, board slug `google/gemini-2.5-pro`, model record `gemini-2.5-pro` reused unchanged (100B
active, 2.0e11 FLOPs per token). Chess Text v1: Game Arena Elo 1061 (+87/-67); Estimated Human Elo 1343
(+49/-57); `Avg. Tokens/Turn` 4074.4 output tokens; `Avg. Cost/Turn` 4.1 cents. Prompt 344.0 tokens. Compute
(4074.4 + 344.0) × 2.0e11 = **8.8368e14 FLOPs** per move. Human Elo 1343 falls in the (1250,1525] bin, whose own
mean is 7.090 seconds; the row records the rating-pooled **7.1 seconds** over 96,356,374 move
observations. `human_skill: typical`.

### game-chess-move-arena-o4mini

o4-mini, board slug `openai/o4-mini-2025-04-16`, model record `o4-mini-2025-04-16` reused unchanged (20B
active, 4.0e10 FLOPs per token). Chess Text v1: Game Arena Elo 831 (+78/-63); Estimated Human Elo 1109
(+71/-84); `Avg. Tokens/Turn` 8977.8 output tokens; `Avg. Cost/Turn` 4.0 cents. Prompt 387.3 tokens. Compute
(8977.8 + 387.3) × 4.0e10 = **3.746040e14 FLOPs** per move. Human Elo 1109 falls in the (0,1250] bin, whose own mean
is 7.568 seconds; the row records the rating-pooled **7.1 seconds** over 96,356,374 move
observations. `human_skill: novice`, the one row where that call is arguable.

### game-chess-move-arena-gpt41

GPT-4.1, board slug `openai/gpt-4.1-2025-04-14`, model record `gpt-4.1-2025-04-14` reused unchanged (50B
active, 1.0e11 FLOPs per token). Chess Text v1: Game Arena Elo 488 (+73/-63); Estimated Human Elo 759
(+121/-146); `Avg. Tokens/Turn` 717.9 output tokens, the smallest of the nine by an order of magnitude, since
GPT-4.1 is the only non-reasoning OpenAI model here; `Avg. Cost/Turn` 0.6 cents. Prompt 396.0 tokens. Compute
(717.9 + 396.0) × 1.0e11 = **1.11390e14 FLOPs** per move. This is the row the prompt correction changes most,
by 55%, and the only one where the prompt is a large share of the total — 36% — so the cross-board seam in
the prompt estimate matters here more than anywhere else. Human Elo 759 falls in the (0,1250] bin, whose own mean is
7.568 seconds; the row records the rating-pooled **7.1 seconds** over 96,356,374 move
observations. `human_skill: novice`.

### game-chess-move-arena-sonnet4

Claude Sonnet 4, board slug `anthropic/claude-sonnet-4@20250514`, model record `claude-sonnet-4` reused
unchanged (100B active, 2.0e11 FLOPs per token). Chess Text v1: Game Arena Elo 433 (+64/-57); Estimated Human
Elo 703 (+124/-160); `Avg. Tokens/Turn` 10316 output tokens; `Avg. Cost/Turn` 15.6 cents. Prompt 503.3
tokens. Compute (10316 + 503.3) × 2.0e11 = **2.163860e15 FLOPs** per move. Human Elo 703 falls in the
(0,1250] bin, whose own mean is 7.568 seconds; the row records the rating-pooled **7.1 seconds**
over 96,356,374 move observations. `human_skill: novice`. This row and
`game-chess-move-arena-grok4` show the pattern the board exposes most sharply: Sonnet 4 spends 2.2 times o3's
compute per move for an estimated human Elo nearly a thousand points lower.

### game-chess-move-arena-opus4

Claude Opus 4, board slug `anthropic/claude-opus-4@20250514`, model record `claude-opus-4` reused unchanged
(180B active, 3.6e11 FLOPs per token; this is the larger Opus 4 estimate the dataset carries, not the 100B
shared frontier prior used for later Opus versions). Chess Text v1: Game Arena Elo 398 (+73/-55); Estimated
Human Elo 667 (+133/-160); `Avg. Tokens/Turn` 3177.5 output tokens; `Avg. Cost/Turn` 24.5 cents. Prompt 520.0
tokens, the tightest solve of the nine at ±3 tokens, because Opus 4's $15 per million input price makes the
cost column most sensitive to prompt length. Compute (3177.5 + 520.0) × 3.6e11 = **1.33110e15 FLOPs** per
move. Human Elo 667 falls in the (0,1250] bin, whose own mean is 7.568 seconds; the row records the
rating-pooled **7.1 seconds** over 96,356,374 move observations. `human_skill: novice`.

### game-chess-move-arena-r1

DeepSeek-R1-0528, board slug `deepseek-ai/deepseek-r1-0528`, **new model record** `deepseek-r1-0528` in this
folder's `models.csv`. The dataset's existing `deepseek-r1` record is explicitly the January 2025 R1 and its
note says it is "not R1-0528", so a new record is required rather than a reuse. The R1-0528 `config.json` on
Hugging Face is identical to R1's and to DeepSeek-V3's on every dimension that determines the active count
(`hidden_size` 7168, `moe_intermediate_size` 2048, `n_routed_experts` 256, `n_shared_experts` 1,
`num_experts_per_tok` 8, `num_hidden_layers` 61, `first_k_dense_replace` 3, `intermediate_size` 18432,
`vocab_size` 129280), so the 37B active count carried by the dataset's `deepseek-r1`, `deepseek-v3`, and
`deepseek-v3.2` records applies unchanged: 3.7e10 active, 7.4e10 FLOPs per token, basis `reported`. Release
date 2025-05-28, from DeepSeek's own API news index, which lists "DeepSeek-R1-0528 Release 2025/05/28".
Chess Text v1: Game Arena Elo 394 (+74/-62); Estimated Human Elo 664 (+138/-167); `Avg. Tokens/Turn` 13389.6
output tokens; `Avg. Cost/Turn` 9.5 cents. Prompt 310.4 tokens — the one row whose prompt comes from
neither a published list price nor a measurement, resting instead on the cross-model prompt-length pattern
described above, since the two-board cost solve does not constrain it. Compute (13389.6 + 310.4) ×
7.4e10 = **1.01380e15 FLOPs** per move. Human Elo 664 falls in the (0,1250] bin, whose own mean is 7.568 seconds;
the row records the rating-pooled **7.1 seconds** over 96,356,374 move observations.
`human_skill: novice`.

## Dispositions: what is on these boards and not in the CSV

The two version 1 boards carry eleven rows each. Nine distinct models become points. The rest:

- **Grandmaster**, Estimated Human Elo 2500 on both boards. A Kaggle-supplied reference marker, not a model;
  it carries no token or cost figure and no Game Arena Elo.
- **Gemini 2.5 Flash**, Estimated Human Elo 314 on Chess Text and 282 on Chess Openings. Excluded. Lichess
  ratings floor at 400 and the timing donor's lowest bin is (0,1250], whose mass sits nowhere near 314. There
  is no human population at that rating whose move time could be taken, so the row would have compute on one
  axis and nothing defensible on the other. Reconsider if a lower-rated timing donor is ever added.
- **Kimi K2 Instruct**, Estimated Human Elo 262, Chess Text board only. Excluded for the same reason. Its
  Game Arena Elo is 0, the bottom anchor of the board; Kaggle's API is proto3 JSON, which omits zero-valued
  numbers, so that field is absent rather than blank in the retained response.
- **Every other model that appears on both version 1 boards** contributes one row, built on the Chess Text
  board, with its openings entry used as the Elo cross-check above rather than as a second row. Building both
  would put two near-identical points on the same model, the same human baseline, and a task differing only
  in the forced opening.

Also considered and not used:

- **The current 30-model board (version 2).** Exact per-call token counts are available for all 30 models
  from the replay archive, which is better compute evidence than either version 1 board offers, but no
  Estimated Human Elo is published or recoverable for it. Those 30 rows become available the moment Kaggle
  publishes or exposes a human-Elo column for version 2.
- **Heads-up poker.** No human anchor exists. The board's metric is Mean BB/100, retained as
  `agent-work/sources/game-arena/kaggle-poker-heads-up-v1-leaderboard.json`, and a win rate in big blinds per 100 hands
  is defined against the opponents faced. Kaggle's own description of the benchmark, retained as
  `agent-work/sources/game-arena/kaggle-blog-game-arena-poker.md`, states the field and the format: ten models, "900,000
  total hands, organized in a 'duplicate poker' format to reduce elements of luck. Each model played every
  other model for 20,000 hands". So GPT-5.6 Sol's +34.9 BB/100 on the current board is against the other
  models, not against humans, and it cannot be set beside published human heads-up win-rate norms, which are
  measured against human opposition. Kaggle publishes no Estimated Human Elo or equivalent for poker, and
  there is no analogue of the Lichess move-time corpus for heads-up no-limit, so the human-time axis would
  have to be invented as well. Excluded until a human-versus-model poker result exists.

## Reproduction

All three scripts take explicit paths, require only the Python standard library, and refuse to write into the
retained sources.

    python3 research/game-arena/calc.py \
        --sources /abs/path/to/sources/game-arena \
        --output /abs/path/to/new-calculations.json \
        --points-csv /abs/path/to/candidates/game-arena/points.csv \
        --models-csv /abs/path/to/candidates/game-arena/models.csv \
        --header-source /abs/path/to/this-folder

    python3 research/game-arena/aggregate_replays.py \
        --archive /abs/path/to/chess-text-gameplay.zip \
        --leaderboard /abs/path/to/sources/game-arena/kaggle-chess-text-v2-leaderboard.json \
        --output /abs/path/to/new-usage.json

    python3 research/game-arena/replay_durations.py \
        --archive /abs/path/to/chess-text-gameplay.zip \
        --output /abs/path/to/new-durations.json \
        --sources /abs/path/to/sources/game-arena

`calc.py` regenerates `agent-work/derived/game-arena/calculations.json`, which holds the token-column cost test on all
three boards, the DeepSeek price recovery, every row's inputs and arithmetic, the prompt and time-control
scenarios, the cross-board Elo check, and the excluded board rows with their reasons. With the three CSV
arguments it also emits `candidates/game-arena/points.csv` and `models.csv` from the same numbers, so the
candidate rows are reproducible rather than hand-written; it asserts on the way out that every CSV text field
stays inside the maxima the existing dataset's own rows observe. Those fields therefore carry only the
qualifications COLUMNS.md asks them to carry, and everything else about these points is in this note. The replay archive is
not retained; it is reproducible from the unauthenticated URL in `agent-work/sources/game-arena/PROVENANCE.md`.
