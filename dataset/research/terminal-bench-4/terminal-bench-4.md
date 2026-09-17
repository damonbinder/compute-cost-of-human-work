# Terminal-Bench 4.0

*Created 2026-09-14 12:10.*
*Last revised 2026-09-14 12:40, attended context moved to the cells' own cache reads.*

## Summary

248 rows. **240 of them are per-task**: one row for each task-and-model pair where
the model resolved that task in at least three of its five repeats, across 54 of the
benchmark's 66 tasks and all 13 models on the official leaderboard. Each carries that
task's own author expert-time estimate as `human_time` — 0.75 h to 60 h, median 4 h —
and that task's own measured token counts as compute. The other 8 are Artificial
Analysis collection rows, one per model clearing the performance guide, positioned at
the 66-task mean of 23,552.73 s, because that board publishes only collection totals.

Terminal-Bench 4.0 is the first source in this folder where per-task compute and
per-task human time are both published, so it is the first agentic benchmark whose
rows are genuinely task-distinct rather than one collection average copied down a
column. The reason it is possible is that the leaderboard submissions in
`harbor-framework/terminal-bench` name a **Harbor Hub job** for every run, and the
job's results view serves per-trial records — task name, reward, gross input tokens,
cache reads, output tokens and dollars — 100 to a page, server-rendered. 4,290 such
records cover 13 runs × 66 tasks × 5 trials. Summed per run they reproduce the
submission file's own `metrics` block exactly on 11 of 13 runs and to within 2.7% on
the other two.

Ninety-three rows are `match` and 155 are `below`, on this folder's 0.85 to 1.15 band
against a human baseline of completion.

**One finding changes how a Terminal-Bench token counter must be read, and it applies
to 4.0 only.** The leaderboard's `uncached_input_tokens` is **gross** input on this
board, with `cached_input_tokens` a subset of it, not a disjoint fresh-input counter.
A per-trial least-squares solve of dollars on the three counters settles it: under the
disjoint reading the fitted cache-read price is negative on eleven of the twelve
runs that publish cost; under the subset reading the fit returns each provider's
published rates, exactly. Reading the counter the other way would overstate counted
tokens on Opus 5 by a factor of 25. Terminal-Bench 2.1's counters are **not** the
same and `research/terminal-bench.md` is right about them: there `cached_input_tokens`
exceeds `uncached_input_tokens` on 18 of 20 submissions, so the two cannot be nested,
and the eleven exact list-price reproductions that note records confirm the disjoint
reading. The counter changed meaning between repositories.

Everything below is reproduced by

```
python3 research/terminal-bench-4/build_rows.py \
    --sources agent-work/sources/terminal-bench-4 \
    --out agent-work/derived/terminal-bench-4
```

which reads only the retained extracts and writes `points.csv`, `dispositions.csv`
and `calculations.json`.

## The benchmark and the work unit

Terminal-Bench 4.0 is 66 terminal tasks across software (18), science (14), machine
learning (11), operations (9), hardware (5), security (5) and media (4), tagged
`v4.0.0` in
[harbor-framework/terminal-bench](https://github.com/harbor-framework/terminal-bench/tree/v4.0.0)
and published on the
[Harbor Hub](https://hub.harborframework.com/datasets/terminal-bench/terminal-bench/latest).
Artificial Analysis describes the release as recalibrating "compute and time
allowances", improving "the fairness of instructions, environments, and verifiers",
and removing "eight tasks that were saturated, refusal-prone, publicly solved, or
affected by unresolved quality issues". Every task is an instruction, a Docker
environment, an oracle solution and a test suite; every one of the 66 carries
`[agent] timeout_sec = 28800`, an eight-hour agent clock, against Terminal-Bench 2.1's
600 s to 12,000 s.

**The work unit for a per-task row is one agent attempt at that one task**, with
compute the mean over the run's five trials of that task and performance the share of
those five that the verifier passed. This is the grain the source publishes, and it is
the grain the human side is published at too, so the two match without a transfer.

`task_category` is `coding` on 227 rows and `mathematics_puzzles` on the 13 rows for
`takens-embedding-lean` and `coq-block-bound`, which are Lean 4 and Coq proof
obligations; the folder already classifies formal proof that way
(`reas-lean-minif2f-deepseekprov2-cot32` and its siblings). The remaining Science, ML
and Hardware tasks are domain-flavoured software delivery verified by tests, which is
`coding` under the "classify the whole task, not its subject" rule.

<a id="human-time"></a>

## Human time

Every one of the 66 `task.toml` files carries `expert_time_estimate_hours`, the field
the Terminal-Bench paper describes as the task author's answer to how long "a domain
expert would require" to complete the task. These are estimates by the people who
wrote the tasks, never timings, which is what `human_time_evidence = source_estimate`
records. No human has attempted a Terminal-Bench 4.0 task under measurement.

| Statistic | Expert (h) |
|---|---|
| n | 66 |
| mean | 6.5424 |
| median | 4 |
| geometric mean | 4.303 |
| minimum | 0.75 |
| maximum | 60 |
| sum | 431.8 |

The distribution is much less skewed than 2.1's: the mean is 1.6 times the median here
against 3.4 times there, 61 of 66 tasks sit between one hour and one day, two are under
an hour and three are a day or more. Every task carries an estimate, so there is no
coverage gap of the kind 2.1's `caffe-cifar-10` creates.

A per-task row takes **that task's own estimate**, so `human_time_statistic` is
`point_estimate` rather than `mean`. The eight collection rows take the arithmetic mean
23,552.73 s, with `human_time_statistic = mean`, because the compute behind them is
itself an average over the same 66 tasks. There is no junior estimate in 4.0; the field
2.1 carried is gone.

`human_skill = expert` follows the field's own definition.

<a id="compute"></a>

## Compute

### What the sources publish

**The official leaderboard** is 13 submission files in
`leaderboard/submissions/` of `harbor-framework/terminal-bench`, each with a `metrics`
block (`uncached_input_tokens`, `cached_input_tokens`, `output_tokens`, `total_tokens`,
`total_cost_usd`, `accuracy`, `successes`, `n_trials` = 330), a `metadata` block naming
model, agent, agent version, reasoning effort and date, and a `source_jobs` entry
naming a Harbor Hub job.

**The Harbor Hub job page** is where the per-task data lives. Requesting
`https://hub.harborframework.com/jobs/<id>?tab=results&page=<n>` returns the trials
table server-rendered in the page payload, 100 rows a page, four pages per job. Each
record carries `task_name`, `reward`, `input_tokens`, `output_tokens`, `cache_tokens`,
`cost_usd`, `status`, `error_type`, start and finish times. All 4,290 are in
`agent-work/sources/terminal-bench-4/tb40-hub-trials.csv`. Every trial is `completed`
and `is_scored`; 144 carry an `error_type`, led by `OutputTokenExceededError` (52) and
`AgentTimeoutError` (32), and those are kept in the compute mean because the row's
compute is over all attempts.

Reconciling the Hub records against the submission metrics: 11 of 13 runs agree to
1.0000 on all four of gross input, cache tokens, output and dollars, and on the success
count. Opus 5 and GPT-5.6 Sol run 1.0% and 2.7% high on the Hub, with 173 against 171
and 123 against 123 successes — the job has moved slightly since the submission file
was written. The Hub is taken as the authority, since it is the only per-task source.

**Artificial Analysis** publishes
[a Terminal-Bench v4.0 board](https://artificialanalysis.ai/evaluations/terminalbench-v4-0)
carrying 30 scored models, with `canonicalEvalTokenCounts.terminalbenchV40` giving
`input`, `cacheableInput`, `answer` and `reasoning` per model. It publishes **no
per-task data**. Its "Cost per Task" and "Output Tokens per Task" charts are labelled
by the page's own strings as "Average cost per task (USD)" and "Output tokens used to
run one task", computed client-side from those four collection totals — the same
construction `scouting/gdpval-per-task-compute.md` found on the GDPval board. The
scouting note that proposed this source read those chart titles as per-task records;
they are not. Trials are 198, not published as a field but fixed by the page's stated
protocol ("We run all 66 Terminal-Bench v4.0 tasks and report pass@1 averaged over
three repeats per task") and confirmed because all 30 scores times 198 are integers.

### The counter semantics, and how they were established

Writing `I`, `C` and `O` for the Hub's `input_tokens`, `cache_tokens` and
`output_tokens`, the two candidate readings are

```
A (disjoint, as on Terminal-Bench 2.1):  billable = p_U·I + p_C·C + p_O·O
B (nested, C ⊂ I):                       billable = p_U·(I − C) + p_C·C + p_O·O
```

Each run gives 330 independent trials with a published `cost_usd`, so the price vector
can be fitted rather than assumed. `dataset/research/terminal-bench-4/price_solve.py`
runs the least squares. Reading A returns a **negative** cache-read price on every run
but one — Opus 5 −$5.75/M, GLM-5.3 −$1.14/M, Sol −$4.38/M — which is not a price.
Reading B returns the published rates:

| Run | p_U | p_C | p_O | relative residual |
|---|---|---|---|---|
| Opus 5 / Claude Code | 6.25 | 0.50 | 25.01 | 0.0004 |
| Opus 4.8 / Claude Code | 6.25 | 0.50 | 25.04 | 0.0014 |
| GLM-5.3 / Claude Code | 1.40 | 0.26 | 4.40 | 0.0000 |
| Gemini 3.7 Flash / mini-swe-agent | 0.75 | 0.07 | 3.75 | 0.0000 |
| GPT-5.6 Luna / Codex | 0.24 | 0.02 | 1.22 | 0.0022 |
| GPT-5.6 Terra / Codex | 2.47 | 0.20 | 12.04 | 0.0017 |
| GPT-5.6 Sol / Codex | 4.78 | 0.40 | 20.43 | 0.0027 |
| Sonnet 5 / Claude Code | 3.53 | 0.30 | 15.33 | 0.0385 |
| Fable 5.1 / Claude Code | 12.15 | 0.16 | 51.48 | 0.0914 |
| Fable 5 / Claude Code | 8.69 | 0.76 | 53.76 | 0.2622 |
| Grok 4.5 / Grok Build | 2.84 | 0.61 | −0.25 | 0.0587 |
| Grok 4.6 / Grok Build | 0.30 | 1.05 | −12.81 | 0.0454 |

Anthropic's `p_U` of 6.25 against `p_C` of 0.50 is the cache-**write** rate of a
$5.00/M input model at the standard 1.25× write and 0.1× read multipliers, which is what
`I − C` is: fresh input plus cache creation, the dataset's counted quantity exactly.
The two Grok runs and the two Fable runs fit worse, so their price vectors are not
established; their **token** counts are unaffected, since the counter definition is
established by the runs that do fit and the field is the same field in every file.

This also resolves an anomaly `research/terminal-bench.md` left open. That note records
that every Claude Code run on the 2.1 board prices 1.21× to 1.59× above its reported
cost under reading A, and that no single price vector fits an Anthropic model's two
runs. On 2.1 the fix cannot be reading B, because `cached_input_tokens` there exceeds
`uncached_input_tokens` on 18 of 20 submissions and `I − C` would be negative; 2.1's
counters really are disjoint and eleven of its runs reproduce to the cent. The
discrepancy on 2.1's Claude Code runs remains unexplained. What is settled is that the
4.0 repository's field of the same name means something different, and the 4.0 rows are
built accordingly.

### The recipe

Per task-and-model cell, over the `n = 5` trials with token records,

```
counted tokens per trial  = mean over trials of (I − C + O)
cache reads per trial     = mean over trials of C
N̄                         = min((cache reads / counted) · 2800, counted / 2, 200000)
r                         = 2 · attention_layers · attention_width · N̄ / active_parameters
compute_flops             = counted · 2 · active_parameters · (1 + r)
```

`tokens_accounting = input_cache_creation_output`, `compute_method = params_tokens`,
`compute_statistic = mean`, `compute_subset = all`, `ai_attempts = 5`. The attention
term follows `research/attention-correction.md` with the per-model shapes already in
`models.csv`.

### The attended context comes from the cell's own cache reads

The Hub publishes no turn or call count, but it publishes cache reads per trial, and
those are the sum of the per-call prefixes: on call `i` the harness re-reads `prefix_i`
tokens and processes `n_i` new ones, so `C = Σ prefix_i` against a counted total
`P = Σ n_i`. With the new tokens per call roughly constant at `n` the call count is
`P / n` and the mean prefix is `(C / P) · n`. At the `n = 2,800` that
`research/attention-correction.md#cache-implied-context` adopts — the median over the
sixteen Terminal-Bench 2.1 official submissions — `C / P` runs from 0.7 to 178 across
the 240 rows and `N̄` from 1,884 to the cap, with a median of 62,130. The four
Artificial Analysis collection rows take the same form on the board's own
`cacheableInput`, giving 15,621 to 32,960.

This replaces the half-the-counted-tokens fallback the first build used, under the
fallback order the same note now states: a context implied by the run's own cache
structure outranks both that fallback and the cap it ran into. The effect on the block
is large and one-directional — `compute_flops` falls on 222 of the 244 rows, by a
median factor of 0.55 and up to 0.25 — because the fallback was reading a compacting
eight-hour agent's whole token budget as one context.

**Ten of the 240 per-task rows still sit at the 200,000 cap**, down from 145. On those
the cell's own cache reads imply a prefix past 200,000 and the cap holds it there, so
the attention term is an upper bound; they are the four Sonnet 5 rows, two GLM-5.3 rows,
and the `wdm-design` and `coq-block-bound` cells for the three Codex-driven GPT-5.6
models. The sensitive assumption is now `n` rather than the fallback: inverting the
relation on the sixteen 2.1 submissions gives `n` from 1,651 to 13,460, which moves a
row's attention term by about a factor of five in either direction, and every row's
`notes` says so.

### Per-task compute is not the collection average

The single quantitative argument for this batch. Within one model and one harness,
counted tokens per trial across the 66 tasks span:

| Run | min | median | max | max/min |
|---|---:|---:|---:|---:|
| Fable 5.1 / Claude Code | 144,644 | 494,376 | 6,902,384 | 47.7 |
| Opus 5 / Claude Code | 88,979 | 469,782 | 5,087,922 | 57.2 |
| Fable 5 / Claude Code | 47,806 | 402,912 | 5,496,226 | 115.0 |
| GLM-5.3 / Claude Code | 90,888 | 522,428 | 2,975,404 | 32.7 |
| GPT-5.6 Sol / Codex | 38,482 | 187,379 | 1,792,897 | 46.6 |
| GPT-5.6 Luna / Codex | 35,507 | 336,806 | 6,000,149 | 169.0 |
| Grok 4.5 / Grok Build | 30,499 | 221,059 | 4,396,270 | 144.1 |
| Gemini 3.8 Flash / mini-swe-agent | 390,478 | 1,139,723 | 5,998,276 | 15.4 |

Fifteen to a hundred and seventy times, inside one run. A collection average asserted
task by task would be wrong by that much, in both directions, which is the reason the
rule exists.

## Performance and the band

There is no scored human attempt, so the label rests on what the author's estimate
implies. The field is the time for a focused domain expert to **complete** the task, so
the implied human baseline is completion: 100% on the benchmark's own pass/fail metric,
chance floor zero. The ratio to the human is therefore the resolution rate itself.

A cell enters the dataset only if the model resolved the task in a **majority of its
five repeats**, so every per-task row sits at 0.6, 0.8 or 1.0. On this folder's 0.85 to
1.15 band that makes 5-of-5 a `match` (93 rows) and 3-of-5 and 4-of-5 `below` (147
rows). Nothing reaches `above`, and nothing could: the implied baseline is a ceiling. A
real expert given these 66 tasks under an eight-hour clock would not finish all of them,
so the recorded ratios are conservative.

The eight Artificial Analysis rows are labelled on the collection resolution rate,
0.4899 to 0.5960, all `below`.

`comparison_issues = different_attempt_selection` on every row: the compute and cost
figures average over all five trials including failures and timeouts, while the human
time is the time to complete.

## Models

Twelve model IDs are reused unchanged: `claude-opus-5-max`, `claude-opus-4-8`,
`claude-fable-5`, `claude-fable-5-1`, `claude-sonnet-5`, `glm-5.3`, `gpt-5-6-sol`,
`gpt-5-6-terra`, `gpt-5-6-luna`, `grok-4-5`, `grok-4-6`, `gemini-3-8-flash`, plus
`gpt-6-astra` on the Artificial Analysis rows. `claude-opus-5-max` is used for the
max-effort Opus 5 run, matching `agen-tbench21-aa-opus5`; the three Fable 5.1 and four
GPT-6 Astra reasoning efforts on the Artificial Analysis board share one model ID each,
with the served effort recorded in `task_description`, following that batch's Revision 2.

`gpt-5-6-sol` carries the same caveat it carries on the 2.1 rows: DECISIONS ruled 150B
active and this note's arithmetic uses 150B, so if the merged registry still carries
100B for the shared ID those 27 rows move by 1.5× when `tools/apply_priors.py` runs.

**One new record**, in `candidates/terminal-bench-4-models.csv`:

| model_id | active (B) | basis | route |
|---|---|---|---|
| gemini-3-7-flash | 40 | estimated | the Gemini 3-generation Flash prior in `research/model-priors/google-xai-others.md`, 15-90B, grade C — the same value and range the registry already carries for `gemini-3-8-flash` |

Release date 2026-08-13, from the Artificial Analysis model record on the v4.0 page.
Attention shape 59 layers at 7,552 wide, from the dense-transformer rule in
`research/attention-correction.md#model-architectures` on a 40B active count, again
identical to `gemini-3-8-flash`.

## Dispositions

`agent-work/derived/terminal-bench-4/dispositions.csv` records 640 cells that are not
rows.

| Source | Cells | Why not rows |
|---|---|---|
| Official leaderboard, task-and-model cells | 441 | No trial resolved the task |
| Official leaderboard, task-and-model cells | 177 | Resolved in a minority of repeats: 107 at 1 of 5 and 70 at 2 of 5 |
| Artificial Analysis v4.0 board | 22 | Collection resolution rate 2.2 to 98.3 standard errors below the half-of-human guide |

The 2-of-5 cells are the closest call. At 0.4 they are below the half-of-human guide on
the point estimate, and the majority rule the coordinator set excludes them explicitly,
so they are not built even where the binomial standard error on five trials would admit
them. That standard error is 0.22 on five trials, which is why the rule is a majority
rule rather than a significance test at this grain.

The 22 Artificial Analysis dispositions include `claude-fable-5` at 42.4% and `glm-5-3`
at 41.9%, both 2.2 to 2.3 standard errors below the guide. `gpt-6-astra-medium` at
49.5% and `claude-opus-5` at 48.99% are **built**, at 0.14 and 0.28 standard errors
below the guide, under the one-standard-error close-call rule.

## What Terminal-Bench 2.1 cannot do retroactively

The same move was attempted on 2.1 and does not work. The 20 submission files in
`harbor-framework/terminal-bench-2-1` do carry a `source_jobs` UUID each, in the same
place and the same shape as 4.0's. **Those jobs are not published on the Harbor Hub**:
`https://hub.harborframework.com/jobs/<id>` returns 404 for every one tried
(`10e2e56b-…` for Opus 4.7 under Claude Code, `4860a28f-…` for GPT-5.6 Luna,
`f9d0318d-…` for Fable 5, `36288ba6-…` for Sonnet 5), while all 13 of the 4.0 jobs
return 200. The 2.1 files' own `trials` arrays hold UUIDs and nothing else, and
`https://hub.harborframework.com/trials/<id>` is not a route. So 2.1's per-trial
records exist — the leaderboard tooling computed the aggregates from them — but are not
public.

The other 2.1 donor is worse: Artificial Analysis's v2.1 board publishes the same four
collection totals and no per-task field, exactly as its v4.0 board does. Nothing on the
2.1 side has changed, and `agent-work/candidates/terminal-bench-2-1-per-task.csv` is
therefore written empty, with its header only. The existing 44 suite-level 2.1 rows
stand and nothing supersedes them.

What would unblock it is Terminal-Bench publishing the 2.1 jobs on the Hub, which costs
them a visibility flag. Worth re-checking rather than re-researching.

## Limitations

**The human number is an author's estimate, on every row.** That is the whole human side
of this source. A per-task row makes the estimate load-bearing in a way a 66-task mean
did not: the mean averaged 66 independent guesses, and each row now rests on one.
`takens-embedding-lean` at 60 h carries three rows and its estimate is a single
author's; so is `photonic-waveguide-routing` at 0.75 h.

**Ten of 240 rows have their attention term capped**, so their `compute_flops` is an
upper bound by an unquantified amount. The other 230 rest on the transferred 2,800 new
tokens per call, which the sixteen Terminal-Bench 2.1 submissions bracket at 1,651 to
13,460.

**Two runs' price vectors do not fit**, so the counter semantics on Grok Build and on
the Fable runs rest on the eleven runs that do. The token values do not depend on the
fit, only the confidence in what the field means.

**Five repeats is a coarse performance measurement.** The binomial standard error on the
resolution rate of one cell is 0.22, so the difference between a `match` row at 5-of-5
and a `below` row at 4-of-5 is well inside noise. The labels are honest about the
observed outcome and should not be read as separating the two cells' true rates.
