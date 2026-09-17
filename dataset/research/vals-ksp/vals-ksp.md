# Vals Time Horizon Index: KSP

*Created 2026-09-14 12:10.*
*Last revised 2026-09-14 13:20.*

Six rows from Vals AI's Time Horizon Index: KSP board, one per model that
completed at least one mission of the ladder. The work unit is **the first N
missions of the ladder**, not the campaign: each row's N is the number of rungs
the model actually finished, and its human time is the sum of Vals's own
per-rung minutes for exactly those rungs. Compute is the board's campaign dollar
**prorated to the point at which the model completed that last rung**, then
inverted to tokens; charging the whole five-day clock to the first N missions
would charge the unit for the work the agent then spent failing at mission
N+1.

## Summary

| point_id | Model | Rungs | Rung day / 5 | Prorated $ | Human time (s) | Tokens | compute_flops |
|---|---|---:|---:|---:|---:|---:|---:|
| game-ksp-ladder4-opus5max | Claude Opus 5 (max) | 4 | 1.0417 | 272.71 | 19620 | 14,210,043 | 4.370e18 |
| game-ksp-ladder3-gpt56sol | GPT-5.6 Sol (max) | 3 | 0.7083 | 94.64 | 16980 | 4,980,571 | 2.229e18 |
| game-ksp-ladder3-opus48 | Claude Opus 4.8 (max) | 3 | 3.5545 | 1065.87 | 16980 | 64,286,093 | 1.739e19 |
| game-ksp-ladder2-gpt55 | GPT-5.5 (xhigh) | 2 | 1.8440 | 190.43 | 15120 | 31,698,701 | 1.818e19 |
| game-ksp-ladder1-grok45 | Grok 4.5 (high) | 1 | 0.0813 | 5.59 | 7200 | 721,941 | 2.057e17 |
| game-ksp-ladder1-grok46 | Grok 4.6 (high) | 1 | 1.3750 | 61.91 | 7200 | 4,076,434 | 1.644e18 |

All six are `match` on completion. Proration and the donor-implied attention
context together move compute down by 6x (Opus 4.8) to 185x (Grok 4.5) against
the first build, which charged the whole campaign and took the 200,000-token
attention cap.

Two board cells produce no row. Kimi K3 finished one rung but Vals publishes a
null cost for it, so there is no compute evidence. Meta's Muse Spark 1.1 scored
1.667%, exactly half of one rung, and completed no mission at any grain, so the
AI did not do the job the row would assert.

The arithmetic is in `research/vals-ksp/compute_vals_ksp.py`; its output is
`agent-work/derived/vals-ksp/vals-ksp-calculations.txt` and
`vals-ksp-rows.json`. Board extracts are retained on disk in
`agent-work/sources/vals-ksp/`.

<a id="the-benchmark-and-the-work-unit"></a>

## The benchmark and the work unit

An agent gets a five-day clock and attempts a fixed 30-mission ladder in
Kerbal Space Program, in order. Rung 1 is a Mun landing; rung 2 starts from
scratch and asks for another landing followed by the safe return of the same
Kerbal; the same pair repeats for Minmus, Duna, Ike, Gilly, Dres, Eeloo, Moho,
Vall, Bop, Pol, Laythe, Tylo, and Eve, which takes the ladder to rung 28.
Asteroid capture is rung 29 and a single-Kerbal grand tour is rung 30. One
completed rung is 3.33%, and while a mission is in progress the referee can
award partial credit for reaching the target's sphere of influence, entering
orbit, landing, taking off, or surviving reentry at Kerbin.

The agent does not play the game through the vehicle editor. It gets a parts
catalog and reference craft, writes a raw `.craft` file, and writes a Python
flight program that sends permitted commands — throttle, attitude, staging,
maneuver nodes, time warp, docking, fuel transfer — through the benchmark's
control API. A trusted referee process passes those to KSP, reads vessel state,
records a signed telemetry trace and scores it; the model cannot edit the trace.
The agent may screenshot the game when it chooses. KSP restarts from a clean
save before every scored rung and parked vessels do not carry over, while craft
files, flight code, logs and notes do, and one OpenCode session and workspace
persist across rungs.

**The work unit is the first N missions, and the AI did that job.** Every
published score decomposes as `3.333 * (completed rungs) + (partial credit
inside the current rung)`, because the ladder is strictly sequential and passing
a rung is what sends the next mission to the session. Taking N as the integer
part gives a task each row's model unambiguously finished, verified by signed
telemetry, with a human time Vals's own table supplies for exactly those rungs.
The campaign as a whole is not a defensible unit: no model has finished it, and
a fractional "13.67% of a space program" has no human counterpart.

**The cost is the whole campaign's, and it is prorated.** The board's own
Progress Over Time series gives each model's score against effective run time,
so the moment at which a model completed its last whole rung is recoverable, and
the campaign dollar is cut to that fraction of the clock. The proration rule and
its basis are in the compute section. What remains inside the prorated window is
all the work up to that completion, failures and retries included, against a
human leg that records a successful run; every row carries
`different_attempt_selection` for that.

<a id="human-time"></a>

## Human time

Vals does not publish per-mission human times as a table, but its board bundle
computes them, and the function is transcribable. From
`_astro/KSPTimeHorizonIndex.CNaTPLV4.js`, with minutes taken from the marathon's
timestamped legs:

| Rung | Mission | Minutes | Cumulative (s) |
|---:|---|---:|---:|
| 1 | Mun landing | 120 | 7200 |
| 2 | Mun landing and return | 132 | 15120 |
| 3 | Minmus landing | 31 | 16980 |
| 4 | Minmus landing and return | 44 | 19620 |
| 5 | Duna landing | 216 | 32580 |

The conversion `F` walks this table, giving whole rungs their full minutes and
prorating the rung in progress by its partial credit. It reproduces the board's
own statement that 10% progress is 4 h 43 min: three rungs, 120 + 132 + 31 =
283 minutes. Rung 5's 216 minutes is the marathon's Ike leg (180) plus its Duna
leg (36) — the marathon visited both on one trip — and enters no row here, since
no model completed rung 5.

Each row takes the cumulative figure at its own N. That is Vals's interpolation
applied at the only points where it does no interpolating at all: a completed
rung gets its whole recorded leg, and no row's human time contains a prorated
fraction of a leg.

**The interpolation is defensible per unit, and the headline is not what the
rows use.** Vals's 90–120 hour figure is for all 28 rungs and is built the
other way round, from two whole-run proxies rather than from legs. The
50:18:58 [KSP Planet Landing Marathon](https://www.youtube.com/playlist?list=PLB3Ia8aQsDKjm9QdqGKH8VW8kDBDQXYx4)
(Mike Aben, 21 videos) already lands once at each destination and flies home;
the ladder additionally asks for a separate landing first, so Vals adds the
run's timestamped landing legs, 40 h 23 min, giving 90 h 42 min. For a slower
reading it takes the
[TrueAchievements completion survey](https://www.trueachievements.com/game/Kerbal-Space-Program-Enhanced-Edition/completiontime)
(31 responses), whose nearest-rank 75th percentile falls in the 60–80 hour
bucket, uses the bucket's 80-hour ceiling, and adds the same 40 h 23 min, giving
120 h 23 min. Vals states plainly that these are two proxies, "not lower and
upper bounds, a confidence interval, or a measured human distribution", and that
nobody has run the 28-rung sequence.

Neither headline enters a row. The per-rung minutes come only from the marathon,
so what the rows carry is one recorded expert run's legs.

**The two proxies are not the same skill level, and the per-rung table is the
faster one.** The marathon is a skilled player's continuous recorded run; the
TrueAchievements figure is a 75th-percentile completionist, a typical player,
and it is a completion-survey bucket for the console edition rather than a
timing of this ladder. Mixing them and then reading the per-rung times off the
faster one means every row's human time is at the fast tail of the human
distribution, which biases the rows toward the AI. The only available scale
factor is the ratio of the two headlines, 120:23 / 90:42 = 1.327; applying it
uniformly gives human times of 9,556 s, 20,068 s, 22,537 s and 26,041 s at
N = 1, 2, 3 and 4. That is a scenario, not the recorded value, because the
slower proxy has no per-leg decomposition and half of it is the same marathon's
landing pass.

**Three further caveats on the number.** The marathon leg is part of a
continuous run with carry-over vehicles and accumulated craft designs, while a
ladder rung starts from a clean save and, for the return missions, from scratch;
a standalone mission needs its own launch and so is longer than the leg. The
videos are an edited episode series, so the recorded leg is play time rather
than wall-clock time at the keyboard, and whether it includes vehicle design is
not established. And it is one run by one player: `human_attempts` is 1, which
is the honest sample size. All three point the same way, toward the recorded
minutes being shorter than a from-scratch attempt at the same mission.

`human_time_evidence` is `source_estimate` rather than `task_timings`. The
seconds are read off a human's recorded play, but the number the row uses is
Vals's estimate of a rung's human cost, and the judgment step that sets it —
which legs of a marathon correspond to a from-scratch mission, and that their
sum is the mission's duration — is Vals's, published by Vals. Under the
`DECISIONS.md` hybrid rule the party that made that step takes the field.

<a id="compute"></a>

## Compute

The board publishes `cost_per_test`, a dollar figure for the whole campaign, and
no tokens, no latency and no call counts. Cost-only compute is a sanctioned
basis (`agent-work/DECISIONS.md`, 2026-09-13). The dollar is first prorated to
the row's work unit, then inverted to counted tokens.

### Prorating the campaign dollar

The board's Progress Over Time chart is what makes the proration possible. Its
bundle, `_astro/series.BVd8p07A.js`, carries per model a `series` of
`{day, score}` points in effective run-time days together with an
`effective_days` total, retained as `research/vals-ksp/ksp-series.json`. The
first day at which a model's score reaches `3.333 x N` is the moment it
completed rung N.

| Model | Rung N | Completed at (days) | Hours | Effective days | f | Series |
|---|---:|---:|---:|---:|---:|---|
| Claude Opus 5 | 4 | 1.0417 | 25.0 | 5 | 0.20834 | hourly |
| GPT-5.6 Sol | 3 | 0.7083 | 17.0 | 5 | 0.14166 | hourly |
| Claude Opus 4.8 | 3 | 3.5545 | 85.3 | 5 | 0.71090 | event |
| GPT-5.5 | 2 | 1.8440 | 44.3 | 5 | 0.36880 | event |
| Grok 4.5 | 1 | 0.0813 | 1.95 | 5 | 0.01626 | event |
| Grok 4.6 | 1 | 1.3750 | 33.0 | 5 | 0.27500 | hourly |

**The rule is `cost_N = cost x day(rung N) / effective_days`, a constant spend
rate over effective run time.** Three things support it. The harness runs one
continuous agent loop with no idle phase, so agent time is the resource being
consumed. Vals's own progress-efficiency metric is area under the progress curve
divided by effective agent time, which budgets the run the same way. And nothing
else splits the dollar: there is no per-rung cost, and prorating by score share
would assume spend tracks progress, which these curves contradict outright —
Grok 4.5 took 1.6% of its clock to reach 53% of its final score, and Opus 4.8
took 71% of its clock to reach a rung Opus 5 reached in 21%.

The qualification is that spend within a session is back-loaded, since a growing
prefix makes each call dearer. Under a rising rate the first `f` of the clock
costs less than `f` of the money, so uniform proration **overstates** every row,
and most where `f` is smallest. The rows are upper bounds in that direction.

Four models carry a series sampled every 0.0417 days, 121 points over 5 days, so
their completion day is the first hourly sample at or after the event and is
high by up to one hour — 4% of Opus 5's figure and 6% of Sol's, inside the
proration's own error. Opus 4.8, GPT-5.5 and Grok 4.5 carry event-timed series
with four-decimal days.

### Inverting the prorated dollar

Counted tokens come from carrying a donor run's cache structure, the method
`research/bankertoolbench.md` sets out. Write `U` for fresh input plus cache
creation, `O` for output including reasoning, `C` for cache reads, and
`B = U + O` for the counted total the dataset's `input_cache_creation_output`
rule wants. With the donor's `alpha = C/B` and shares `u = U/B`, `beta = O/B`,

```
P_new = u*p_in + beta*p_out
P_eff = alpha*p_cached + P_new
B     = cost * f * 1e6 / P_eff
```

Every donor is a run of **the same model** in an agentic terminal harness with
measured `uncached_input_tokens`, `cached_input_tokens` and `output_tokens`,
taken from `research/terminal-bench.md`. Where a model has two such runs the
central is their geometric mean, per the `DECISIONS.md` two-transfer rule; where
it has one, that reading is the central and the alternatives are scenarios,
following the ARC-AGI-3 single-transfer clarification.

| Model | Donor | alpha | u | beta | P_eff ($/M) | Prorated $ | Counted tokens |
|---|---|---:|---:|---:|---:|---:|---:|
| Claude Opus 5 (max) | AA Terminus 2, `claude-opus-5` | 11.790 | 0.5852 | 0.4148 | 19.191 | 272.71 | 14,210,043 |
| GPT-5.6 Sol (max) | AA Terminus 2, `gpt-5-6-sol` | 9.026 | 0.5963 | 0.4037 | 19.605 | 94.64 | 4,827,437 |
| GPT-5.6 Sol (max) | official Codex 0.144.0 max | 17.324 | 0.8098 | 0.1902 | 18.418 | 94.64 | 5,138,563 |
| Claude Opus 4.8 (max) | official Claude Code 2.1.205 high | 7.725 | 0.6141 | 0.3859 | 16.580 | 1065.87 | 64,286,093 |
| GPT-5.5 (xhigh) | official Codex 0.125.0 xhigh | 1.145 | 0.9826 | 0.0174 | 6.008 | 190.43 | 31,698,701 |
| Grok 4.5 (high) | official Cursor CLI high | 9.309 | 0.7264 | 0.2736 | 7.749 | 5.59 | 721,941 |
| Grok 4.6 (high) | AA Terminus 2, `grok-4-6` | 22.292 | 0.4898 | 0.5102 | 15.187 | 61.91 | 4,076,434 |

**The two Sol readings agree to 6%**, 4.83M against 5.14M, which is the only
internal check available on the method here and it passes. Their geometric mean,
4,980,571, is the Sol row's central.

**`ai_cost_usd` is blank on all six, with basis `not_available`.** `COLUMNS.md`
requires the cost column to be the dollar for the same unit and statistic as
`compute_flops`, and never estimated. The observed dollar is the campaign's, a
different unit from the row's; the prorated figure is the row's unit but is
derived. Neither qualifies, so the column is empty and each row's `notes` gives
the campaign dollar instead. The first build of these rows carried the campaign
dollar as `reported`, which was wrong on the unit.


### Prices

Rates in force on 2026-08-20, the board's update date, USD per million input /
cached / output: Claude Opus 5 and Opus 4.8 5.00 / 0.50 / 25.00; GPT-5.6 Sol
5.00 / 0.50 / 30.00, its launch rates, since the promotional cut to
4.00 / 0.40 / 20.00 lands on 2026-08-21, the day after; GPT-5.5
5.00 / 0.50 / 30.00. All four are in `research/cost/list-prices.csv`.

**Grok 4.5 and 4.6 are not in that table**, and both are 2.00 / 0.50 / 6.00.
Two independent boards' reported dollars reproduce exactly at those rates:
Grok 4.5's official Terminal-Bench 2.1 submission, 12.570445 x 2 + 161.079936 x
0.5 + 4.734062 x 6 = $134.085 against a reported $134.09, and Artificial
Analysis's Grok 4.6 cell, 1.622674 x 2 + 73.850969 x 0.5 + 1.690288 x 6 =
$50.311 against the $50.311 its published per-trial figure implies. The table
should gain the two windows at merge.

Anthropic bills cache writes at 1.25x input, and the donor counters lump fresh
input with cache creation. Charging all of `U` at the 6.25 write rate instead of
5.00 lowers the two Opus rows' counted tokens by 3.7% and 4.4%; the rows take
the input rate, as the donor rows do.

### Attention

`attention_context` is the donor-implied mean prefix, not the 200,000
fallthrough cap. In an append-only dialog whose prefix is re-read from cache, a
run over `k` calls has `P = k * n_new` processed positions and
`C = k * N̄` cache reads, so

```
N̄ = alpha * n_new
```

At `n_new = 2,783`, the median `research/attention-correction.md` already uses
for the METR rebuild, the donor alphas give:

| Model | alpha | N̄ | attention_ratio | Attention share of compute_flops |
|---|---:|---:|---:|---:|
| Claude Opus 5 | 11.790 | 32,811 | 0.5376 | 35% |
| GPT-5.6 Sol | 12.505 | 34,801 | 0.4918 | 33% |
| Claude Opus 4.8 | 7.725 | 21,498 | 0.3522 | 26% |
| GPT-5.5 | 17.324 | 48,212 | 0.6575 | 40% |
| Grok 4.5 | 9.309 | 25,906 | 0.4244 | 30% |
| Grok 4.6 | 22.292 | 62,037 | 1.0164 | 50% |

Sol takes the geometric mean of its two donors' alphas. **GPT-5.5 takes the
GPT-5.6 Sol Codex alpha rather than its own donor's**, because its own donor is
the Codex 0.125.0 run that re-prefilled rather than cached: an alpha of 1.145
returns a 3,187-token mean prefix, which is not a context for a 120-hour
OpenCode session, and `DECISIONS.md`'s default-on caching ruling says the
no-reuse branch is not live where the provider caches by default and the harness
does not disable it, which `research/bankertoolbench.md` establishes OpenCode
does not. The same argument would move that row's token inversion too; it is
left on the same-model donor and the alternative is stated in its section.

This replaces the first build's 200,000 cap, which made the attention term three
quarters of `compute_flops` on every row. The rule in
`research/attention-correction.md` reserves its first tier for a context resting
on the run's own records and this one rests on a transferred alpha and a
transferred `n_new`, so the substitution is a judgment that a transferred
estimate beats a cap that is explicitly an upper bound. The cap readings are
2.1x to 3.2x higher and are the named alternative.


### Model sizes

Every coefficient is the registry's, at the ruled grade-C priors: 100B active
for Opus 5, Opus 4.8, Grok 4.5 and Grok 4.6, 150B for GPT-5.6 Sol, 173B for
GPT-5.5. The argued ranges move each row's parameter term in proportion, roughly
0.45x to 2.6x on the Opus and Grok rows.

## Performance

Each row's AI completed exactly the missions the row asserts, scored by the
referee from signed telemetry, so `performance_vs_human = match` on a completion
criterion, the same construction the Portal and Factorio rows use. No row claims
the AI matched the ladder; the rows are the prefix of the ladder each model
finished.

Three flags apply to every row.

- `different_attempt_selection`: the prorated window still contains every failure
  and retry the agent made on the way to rung N, while the human minutes are legs
  of a run that succeeded.
- `different_inputs_or_tools`: the agent writes craft files and Python and flies
  through a control API with a referee reading state for it, while the human
  plays the game interactively through the editor and the flight UI; the agent
  can also iterate against `bench validate-craft`, `verify-craft` and
  `fly-craft` before a scored attempt.
- `different_task`: the human minutes are legs of a continuous marathon with
  carried-over vehicles, not N missions each begun from a clean save.

## Dispositions

| Cell | Score | Why no row |
|---|---:|---|
| Kimi K3 | 5.167% | Finished rung 1, but Vals publishes a null cost: an infrastructure failure on the last day of cost collection left $345.10 confirmed against roughly $450 estimated. A cost inversion on a figure the operator declines to publish is not a compute estimate for the row's task. |
| Meta Muse Spark 1.1 | 1.667% | Exactly half of rung 1 and no completed mission, so no work unit exists at which the AI did the job. No model record is needed. |

## Limitations Vals states

Grok ran on Modal because xAI requires its GPU sandbox in specific locations,
and Claude Opus 5 ran on Modal for this campaign as well; Modal sessions last 24
hours, so those runs stopped and resumed from the same persistent workspace once
a day. Some early runs were scored under an earlier rubric and every signed
telemetry trace was rescored under the final one before publication. Vals also
publishes a progress-efficiency metric, area under the progress curve over
effective agent time; no row uses it.

<a id="game-ksp-ladder4-opus5max"></a>

## game-ksp-ladder4-opus5max

Claude Opus 5 at compute effort max, temperature 1, 128,000 max output tokens,
under OpenCode on Modal. Score 13.667%: rungs 1 to 4 complete — Mun landing, Mun
landing and return, Minmus landing, Minmus landing and return — plus partial
credit for a transfer trajectory toward Duna. Human time 19,620 s.

Rung 4 completed at day 1.0417 of 5, so `f` = 0.20834 and the $1,308.94 campaign
dollar prorates to $272.71. At the Artificial Analysis Terminus 2 donor's
structure that buys 14,210,043 counted tokens; parameter term 2.842e18;
`attention_context` 32,811, `attention_ratio` 0.5376; `compute_flops`
**4.370e18**. At the 200,000 cap it would be 1.216e19.

<a id="game-ksp-ladder3-gpt56sol"></a>

## game-ksp-ladder3-gpt56sol

GPT-5.6 Sol at reasoning effort max, 128,000 max output tokens, under OpenCode.
Score 13.000%: rungs 1 to 3 complete, plus 0.9 of rung 4 — it survived Kerbin
reentry on the Minmus return but did not complete the final landing. Human time
16,980 s.

Rung 3 completed at day 0.7083 of 5, so `f` = 0.14166 and the $668.09 campaign
dollar prorates to $94.64. Counted tokens 4,980,571, the geometric mean of the
Artificial Analysis Terminus 2 reading (4,827,437) and the official Codex
0.144.0 reading (5,138,563); parameter term 1.494e18; `attention_context`
34,801, `attention_ratio` 0.4918; `compute_flops` **2.229e18**. Priced at Sol's
launch rates, in force through 2026-08-20; the cut lands the next day. This is
the lowest-compute row on the set and the second-highest score on the board.

<a id="game-ksp-ladder3-opus48"></a>

## game-ksp-ladder3-opus48

Claude Opus 4.8 at compute effort max, temperature 1, 128,000 max output tokens,
under OpenCode. Score 11.833%: rungs 1 to 3 complete, plus 0.55 of rung 4 — it
took off again during the Minmus return. Human time 16,980 s.

Rung 3 completed at day 3.5545 of 5, so `f` = 0.71090 and the $1,499.32 campaign
dollar prorates to $1,065.87 — by far the largest prorated figure on the set,
because this run used 71% of its clock to reach the rung Opus 5 reached in 21%.
Counted tokens 64,286,093 from the official Claude Code 2.1.205 donor; parameter
term 1.286e19; `attention_context` 21,498, `attention_ratio` 0.3522;
`compute_flops` **1.739e19**. Against `game-ksp-ladder3-gpt56sol`, the same
three missions, this is 7.8 times the compute.

<a id="game-ksp-ladder2-gpt55"></a>

## game-ksp-ladder2-gpt55

GPT-5.5 at reasoning effort xhigh, 128,000 max output tokens, under OpenCode.
Score 8.333%: rungs 1 and 2 complete, plus half of rung 3. Human time 15,120 s.

Rung 2 completed at day 1.8440 of 5, so `f` = 0.36880 and the $516.36 campaign
dollar prorates to $190.43. Counted tokens 31,698,701 from the official Codex
0.125.0 xhigh donor; parameter term 1.097e19; `attention_context` 48,212,
`attention_ratio` 0.6575; `compute_flops` **1.818e19**.

**This row's donor is the weakest of the six.** The Codex 0.125.0 run's counted
tokens are largely repeated re-prefill rather than a cached dialog, which is why
its alpha is 1.145 where every other donor's is 7.7 to 22.3, and why 98.3% of
its counted total is input. Carrying that structure charges almost all of the
prorated dollar at the fresh-input rate and so returns a large token count. Its
attention context already comes from the GPT-5.6 Sol Codex alpha for that
reason; carrying the whole Sol Codex structure instead gives 10,339,630 counted
tokens and 5.93e18 FLOPs, 3.1 times lower. The same-model donor is the rule
these rows follow, so it stays the central, but this is the one row where the
rule and the caching evidence point different ways.

<a id="game-ksp-ladder1-grok45"></a>

## game-ksp-ladder1-grok45

Grok 4.5 at reasoning effort high, temperature 0.7, top_p 0.95, under OpenCode
on Modal. Score 6.333%: rung 1 complete, plus 0.9 of rung 2. Human time 7,200 s.

Rung 1 completed at day 0.0813 of 5 — 1.95 hours in — so `f` = 0.01626 and the
$344.04 campaign dollar prorates to $5.59. Counted tokens 721,941 from the
official Cursor CLI donor at 2.00 / 0.50 / 6.00; parameter term 1.444e17;
`attention_context` 25,906, `attention_ratio` 0.4244; `compute_flops`
**2.057e17**. Proration moves this row further than any other, by 61x, and it is
the row where the constant-rate assumption does the most work: it rests on a
figure taken from the first 1.6% of the clock. It is also the cheapest point on
the set by an order of magnitude, at 2.9e13 FLOPs per human second.

<a id="game-ksp-ladder1-grok46"></a>

## game-ksp-ladder1-grok46

Grok 4.6 at reasoning effort high, temperature 0.7, top_p 0.95, under OpenCode
on Modal. Score 5.833%: rung 1 complete, plus 0.75 of rung 2. Human time
7,200 s.

Rung 1 completed at day 1.3750 of 5, so `f` = 0.27500 and the $225.12 campaign
dollar prorates to $61.91. Counted tokens 4,076,434 from the Artificial Analysis
Terminus 2 donor; parameter term 8.153e17; `attention_context` 62,037, the
largest on the set, `attention_ratio` 1.0164; `compute_flops` **1.644e18**. Its
donor's published cache hit rate is 0.804, far below every other donor's 0.99,
and the Terminal-Bench row built from it records that treating the missed share
as fresh would raise its counted tokens 4.4-fold. Grok 4.6 scored below Grok 4.5
on this board and took 17 times as long to land on the Mun.


## Original evidence

Board: `https://www.vals.ai/benchmarks/time_horizon_index`, "Time Horizon Index:
KSP", version 1, `benchmark_id` `ksp_bench`, updated 2026-08-20, 8 models,
`use_cost_per_test` true, `runner` external, `mode` agentic, `dataset_type`
private. Per-model `accuracy` and `cost_per_test` are in the page's
`BenchmarkView` island props, retained at
`agent-work/sources/vals-ksp/thi_clean.json`; `latency` and `stderr` are zero on
every cell. The rung table and the conversion function are in
`agent-work/sources/vals-ksp/KSPTimeHorizonIndex.js`, and the progress series in
`agent-work/sources/vals-ksp/series.js`, cleaned to
`research/vals-ksp/ksp-series.json`. The narrative — ladder
structure, partial-credit rules, harness, referee, human reference, limitations
— is the board page itself, retained at `agent-work/sources/vals-ksp/thi.html`.
