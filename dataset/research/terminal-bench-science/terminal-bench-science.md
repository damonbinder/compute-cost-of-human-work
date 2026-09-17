# Terminal-Bench-Science 0.1, per task

*Created 2026-09-14 12:02.*

## Summary

157 rows, one per task-and-model pair that the model resolved, built on **measured
per-trial token counts** published by Harbor Hub. The public job pages behind nine of the
fourteen official leaderboard entries carry `input_tokens`, `cache_tokens`, `output_tokens`
and `cost_usd` for each of the 70 tasks in each of the 3 trials — 1,890 trial records whose
pass counts and token totals reproduce the leaderboard's published per-entry figures
exactly. So the per-task route the scouting note wanted is open, and no suite-mean
cost-inverted row is needed.

Every row is `match`: the task author's expert time estimate is the time to **complete** the
task, and a resolved trial completes it. Human time is that estimate, `source_estimate`, and
it runs from 2 h to 600 h with a median of 12 h. Two rows sit at 600 h
(`onsager-ising-lean`, resolved by Fable 5 and by GPT-5.6 Sol) and one at 80 h, which are
the longest human times on any inference row in the collection.

Median compute is 2.9e17 FLOPs against a median 12 h of expert time, 8.1e12 FLOPs per
human-second; 68 of the 157 rows sit above the 1e13 brain anchor. 473 task-and-model cells
where no trial resolved the task are withheld, listed in
`agent-work/candidates/terminal-bench-science-dispositions.csv`.

Reproduced by

```
python3 research/terminal-bench-science/build_rows.py \
    --sources agent-work/sources/terminal-bench-science \
    --models dataset/models.csv \
    --out agent-work/candidates \
    --derived agent-work/derived/terminal-bench-science
```

which reads only the retained extracts in `agent-work/sources/terminal-bench-science/`.

<a id="what-the-sources-publish"></a>

## What the sources publish

Three public surfaces carry Terminal-Bench-Science 0.1 results, and they nest.

**The leaderboard API.** `https://www.terminal-bench-science.ai/api/leaderboard?package=terminal-bench-science%2Fterminal-bench-science&name=v0-1-eval`
is the JSON the site's own client calls, and it returns more than the page shows: 14 entries
with `metrics.accuracy`, `passes`, `total_tokens`, `total_cost_usd`, a `domain_metrics` block
repeating all of those for each of the five scientific domains, and a `task_matrix` giving,
for every entry and every one of the 70 tasks, the three trials' solved flag together with
each trial's UUID and the UUID of the Harbor Hub **job** it ran in. The token figure at every
one of those levels is a single undecomposed total that includes cache reads, which is why
the earlier pass built no row from this board.

**Harbor Hub job pages.** `https://hub.harborframework.com/jobs/<job_id>` is the run behind a
leaderboard entry: one job is one pass over all 70 tasks, so an entry's three trials are
three jobs. A public job's page server-renders `input_tokens`, `output_tokens`,
`cache_tokens` and `cost_usd` for the job, and its `?tab=trials` view server-renders the same
four fields **per trial**, alongside `task_name`, `reward`, `status`, `error_type`, `attempt`
and the start and finish timestamps, plus the job's `config` block naming the agent, its
version, the served model string and the reasoning effort. That per-trial view is the
measurement this note rests on.

**The repository.** `harbor-framework/terminal-bench-science` at commit
`ff55a1b0810a5cc2ebac3ebb007cbe6a26aa2e3b` carries the 70 `task.toml` files with
`expert_time_estimate_hours`, a one-sentence task description, the domain and field, the
8-hour `[agent] timeout_sec`, and the container's CPU, memory and GPU allocation. All 70
tasks allocate four CPUs, 16 GB and no GPU, and all 70 run the agent for up to 28,800 s.

**Nine of fourteen entries have public jobs.** All three jobs are public, or none are. The
five that are not — Fable 5.1, DeepSeek V4.1 Flash, Gemini 3.8 Flash, Gemini 3.7 Flash and
DeepSeek V4 Pro — return 404 without a session, including their best entry, Fable 5.1 at
40.0%. Those five therefore have no per-task compute and are not built. Nothing was
requested from anyone; the 27 public job pages and one repository tarball are the whole
retrieval.

<a id="compute"></a>

## Compute

`input_tokens` on a trial is **gross** and contains `cache_tokens`: on the Opus 5 job the
displayed "95% cache hit" is exactly `cache_tokens / input_tokens`, and the displayed total
is `input_tokens + output_tokens`. The dataset's counted quantity is fresh input plus cache
creation plus output, so

```
P = input_tokens - cache_tokens + output_tokens
```

per trial, and `tokens_accounting = input_cache_creation_output`.

**The decomposition is confirmed by price.** Pricing each entry's summed `P` components at
published list rates reproduces the operator's own summed `cost_usd` to within a few per
cent on seven of the nine entries:

| Entry | Rates (input / cached / output, USD per million) | Priced / reported |
|---|---|---:|
| Grok 4.6 | 3.00 / 0.75 / 15.00 | 1.007 |
| GPT-5.6 Terra | 2.00 / 0.20 / 12.00 | 0.983 |
| GPT-5.6 Sol | 4.00 / 0.40 / 20.00 | 0.982 |
| GPT-5.6 Luna | 0.20 / 0.02 / 1.20 | 0.979 |
| Opus 4.8 | 5.00 / 0.50 / 25.00 | 0.969 |
| Opus 5 | 5.00 / 0.50 / 25.00 | 0.938 |
| Fable 5 | 10.00 / 1.00 / 50.00 | 0.950 |

The three OpenAI vectors are the post-cut rates in `research/cost/list-prices.csv`, which
dates these runs to after 2026-08-21 and agrees with the trials' own August timestamps. The
Anthropic residual of 3-6% is what a cache-creation share of `P` billed at the 6.25 rate
rather than 5.00 would add, so the shortfall runs the right way. On all seven the summed
per-trial `cost_usd` equals the leaderboard's published total for the entry to the cent, so
those rows take `ai_cost_basis = reported` with the trial's own start date.

**Kimi K3 and GLM 5.3 carry no cost, and the reason is instructive.** Both were served to
Claude Code through Anthropic-compatible endpoints at `api.kimi.ai` and `api.z.ai`, and
Harbor Hub priced both at **Anthropic's 5.00 / 0.50 / 25.00**: that vector reproduces the
hub's own per-trial totals to 0.987 and 0.988, and those totals come to 1.667x and 2.489x
the leaderboard's published cost for the same runs. The leaderboard is the one that is
right — Moonshot's 3.00 / 0.30 / 15.00 reproduces its Kimi figure to 0.987 and Z.ai's
GLM-5.2 rates of 1.40 / 0.26 / 4.40 reproduce its GLM figure to 0.989. The hub figure is
therefore not what the run cost and the board figure is a suite total with no per-task
split, so the 24 rows on those two models take `ai_cost_basis = not_available` rather than a
number. This does not touch their tokens, which reconcile exactly.

**The whole extract reconciles.** Summed over each entry's three jobs, the trial records
reproduce the leaderboard's `passes` and `total_tokens` exactly on all nine entries: 63/63
and 7,266,668,313 for Opus 5, 47/47 and 8,406,870,193 for GPT-5.6 Sol, and so on down the
nine. 36 of the 1,890 trials carry blank token or cost fields, every one of them a
`reward = 0` trial that hit `AgentTimeoutError` or `NonZeroAgentExitCodeError`, so no built
row loses a component.

**FLOPs.** `compute_flops = flops_per_token · P · (1 + attention_ratio)` on the row's model
record, the standard `params_tokens` recipe with the attention term from
`research/attention-correction.md`. `compute_evidence = derived_assumed_inputs` on every
row: the token count is measured, but every one of the nine models carries either an
estimated active-parameter count or an estimated attention shape.

<a id="attention"></a>

## The attended context, from the trial's own cache reads

These runs are the first in the collection to publish cache reads per work unit, which pins
the attended context better than the file's fallback does.

Cache reads are the sum of the per-call prefixes: on call `i` the harness re-reads
`prefix_i` tokens from cache and processes `n_i` new ones, so `C = Σ prefix_i` and
`P = Σ n_i`. With the new tokens per call roughly constant at `n`, the call count is `P / n`
and the mean attended context is

```
N̄ = C / (P / n) = (C / P) · n
```

`n = 2,800` is the constant `research/attention-correction.md#metr-cache-reads` already
adopts, the median over the sixteen Terminal-Bench 2.1 official submissions, the only agent
runs in the collection that publish their three token counters separately. `C / P` runs from
2.25 to 417 across the 157 rows with a median of 31, so `N̄` runs from 6,306 to the file's
200,000 cap with a median of 84,800. The cap binds on 21 rows and the append-only bound
`P / 2` binds on 13 more.

This is the sensitive assumption on these rows and each row's `notes` says so. Inverting the
same relation on the sixteen Terminal-Bench 2.1 submissions gives `n` from 1,651 to 13,460,
which moves a row's attention term by about a factor of five in either direction; the
attention term itself is a median 1.28 times the parameter term here, so the whole FLOP
figure moves by roughly 0.55× to 2.6× over that span. The fallback the rest of the file uses
— half the counted tokens — would put almost every one of these rows at the 200,000 cap
instead, since the median row counts 560,000 tokens, so the cache-read route is both better
founded and the more conservative of the two.

Median `attention_ratio` by entry, which is a property of the model shape and the context
rather than of the token count:

| Entry | Rows | Median counted tokens | Median N̄ | Median ratio | Median FLOPs |
|---|---:|---:|---:|---:|---:|
| Opus 5 | 35 | 941395 | 66657 | 1.09 | 5.96e17 |
| GPT-5.6 Sol | 32 | 288958 | 126963 | 1.79 | 2.63e17 |
| Fable 5 | 24 | 1225312 | 41977 | 0.59 | 6.75e17 |
| Opus 4.8 | 14 | 567364 | 135025 | 2.21 | 3.85e17 |
| GLM 5.3 | 13 | 817153 | 139165 | 3.10 | 2.99e17 |
| GPT-5.6 Terra | 12 | 299320 | 109778 | 3.10 | 4.66e16 |
| Grok 4.6 | 11 | 322950 | 34029 | 0.56 | 1.01e17 |
| Kimi K3 | 11 | 467650 | 55978 | 0.19 | 1.11e17 |
| GPT-5.6 Luna | 5 | 864321 | 151212 | 5.59 | 5.79e16 |

<a id="human-time"></a>

## Human time

Every row's `human_time` is that task's own `expert_time_estimate_hours` times 3,600. All 70
tasks carry one. The field is the same one Terminal-Bench 2.1 uses, glossed in
`terminal-bench-science/CONTRIBUTING.md` as "best-case hours for a focused domain expert",
and the Terminal-Bench paper states the collection method: task authors were asked to report
how long they thought a domain expert would require. These are **estimates by the people who
wrote the tasks**, not timings, which `human_time_evidence = source_estimate` records, with
`human_time_statistic = point_estimate`, `human_time_subset = not_applicable` and
`human_attempts = not_applicable`. No human has attempted a Terminal-Bench-Science task
under measurement.

Over the 70 tasks: mean 22.19 h, median 12.0 h, geometric mean 10.32 h, range 1.6 h
(`supraglacial-lake-classification`) to 600 h (`onsager-ising-lean`), total 1,553.1 h. Over
the 157 built rows the median is 12 h and the range is 2 h to 600 h. `human_skill = expert`
follows the field's own definition, and each task's `relevant_experience` field corroborates
it — `onsager-ising-lean` asks for a PhD in mathematics.

Moving from the suite mean to the task's own estimate is the substantive gain over
`agen-tbsci-gpt6astra-valsai`, which sits at the 79,874 s suite mean. The estimates are
right-skewed by a factor of 1.85 from mean to median, so a suite-mean row prices every task
at nearly twice the typical one.

<a id="performance"></a>

## Performance, and what is withheld

The human baseline the estimate implies is completion, and a resolved trial completes the
task on the benchmark's own strict pass/fail metric. Every built row is therefore `match`
by construction, with `comparison_issues = none_identified`: compute is the mean over the
resolved trials and human time is the time to complete, so both sides select the same
outcome.

What the row does not carry is reliability. 89 of the 157 rows rest on 1 resolved trial of
3, 44 on 2 and 24 on 3, and each row's `notes` states the split. A row is the compute of one
success, not the expected compute of reaching one; on a task resolved 1 in 3, the expected
figure is about three times the row's.

**473 cells are withheld**, every task-and-model pair among the nine entries where no trial
resolved the task, listed with its expert estimate and its 0-of-3 record in
`agent-work/candidates/terminal-bench-science-dispositions.csv`. These are the
substantially-below cases the product excludes: the AI did not do the job at all, so the row
would assert nothing about how hard the task is. 14 of the 70 tasks were resolved by none of
the nine entries and so appear in no row.

**The five entries without public jobs are not built at all**, and neither is a suite-mean
row for them. Their only compute evidence is the board's gross `total_tokens` and
`total_cost_usd`, and a suite-mean row would in any case fail the performance guide: the
best of the fourteen entries is Fable 5.1 at 40.0% ± 3.4, which is 2.96 standard errors
below the half-of-human bar that a 100% completion baseline implies. That is the same
disposition the earlier pass reached for all fourteen, and it is unchanged. The per-task
route escapes it because a resolved task is a completed task, not 40% of one.

<a id="judgments"></a>

## Judgments

**`task_category = research_analysis` on every row**, following
`agen-tbsci-gpt6astra-valsai`. Many deliverables are code and some are Lean proofs, but
`COLUMNS.md` asks for the whole task, and the whole task is scientific research work whose
binding skill is domain expertise — which is what the benchmark's own domain and
`relevant_experience` fields record. Classifying per task would mean 56 separate judgments
against a one-sentence description, and the category would track the output format rather
than the work.

**Model records are reused unchanged; no new model is needed.** `claude-opus-5-max`,
`claude-opus-4-8`, `claude-fable-5`, `gpt-5-6-sol`, `gpt-5-6-terra`, `gpt-5-6-luna`,
`kimi-k3`, `glm-5.3` and `grok-4-6` all exist in `models.csv` with the priors the
Terminal-Bench 2.1 batch established. Opus 5 takes `claude-opus-5-max` rather than
`claude-opus-5` because these runs are served at max reasoning effort, matching
`agen-tbench21-aa-opus5`; the two records carry the same weights, so nothing numerical turns
on it.

**One work unit per task-and-model pair, not per trial.** Three trials of one task under one
model are three attempts at the same work, so they make one row at the mean of the resolved
ones, with `compute_statistic = mean`, `compute_subset = successful` and `ai_attempts` the
resolved count. Building three rows would triple-weight a task that happens to have been run
three times.

**Fable 5's fallback.** Anthropic serves Fable 5 with an Opus 4.8 fallback, so a share of the
turns on those 24 rows may have run on a different model; the model record says so and the
rows' notes repeat it.

**Relation to `agen-tbsci-gpt6astra-valsai`.** That row stays. It is the Vals AI board — a
different operator, a different harness, one graded run per task rather than three, and a
much higher resolution rate — and the two boards are not mixed in any row here. It is the
only Terminal-Bench-Science row whose compute is inverted from a dollar figure; these 157
are measured.
