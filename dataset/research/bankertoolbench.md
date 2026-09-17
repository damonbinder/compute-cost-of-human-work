# BankerToolBench — end-to-end investment banking deliverables

*Created 2026-09-13 17:15.*
*Last revised 2026-09-13 18:02, applying Revision 1: the four required fixes and all six optional suggestions from `reviews/bankertoolbench-independent.md`. No number changed; change log in `candidates/bankertoolbench/REVISION.md`.*

## Summary

Four candidate rows, one per published (model, agent-harness) cell of BankerToolBench's harness
comparison. The human side is the strongest in the legal-and-finance domain: **every one of the
100 tasks was completed by the investment banker who wrote it, at a published mean of 5 hours
and a maximum of 21 hours**, and that completion is the benchmark's reference deliverable. The AI
side is **cost-only** — the paper publishes no token counters for any model, and the only compute
figures anywhere in it are four per-run dollar amounts in Section B.2 — so the rows are built
under the `DECISIONS.md` cost-inversion ruling.

| point_id | Model | Harness | Score | Cost/run | Billed units | compute_flops | Label |
|---|---|---|---:|---:|---:|---:|---|
| work-btb-opus46-opencode | Claude Opus 4.6 | OpenCode | 53.2 | $2.00 | 121,479 | 2.430e16 | below |
| work-btb-opus46-openhands | Claude Opus 4.6 | OpenHands | 53.0 | $2.60 | 176,138 | 3.523e16 | below |
| work-btb-gpt52-opencode | GPT-5.2 | OpenCode | 56.1 | $1.10 | 295,879 | 5.918e16 | below |
| work-btb-gpt52-openhands | GPT-5.2 | OpenHands | 54.5 | $2.32 | 630,998 | 1.262e17 | below |

All four carry `human_time = 18000` seconds, the longest measured human anchor in this domain.

**The central judgment is which metric the rows are labelled on**, and it is stated at
[The performance reading](#the-performance-reading). The AI is read against the banker deliverable
on BTB's own weighted rubric `Score`, where the gold is 100 by construction, a do-nothing agent
is 0, and the four cells sit at 0.530 to 0.561 of the human. That clears the half-of-human
exclusion guide, by 1.2 to 3.0 standard errors on a task-sampling basis. On the paper's headline
`Pass Rate` the best model reaches 16% and bankers rate
0% of AI deliverables sendable as-is, which would send every row to dispositions instead. The
`Score` reading is taken, following the APEX-Agents ruling in `DECISIONS.md` that a
criterion-level score is preferred to a whole-task pass rate where both exist. A reviewer who
disagrees should start here; nothing else in the entry changes.

**The second judgment is the cost-to-token inversion**, at [Compute](#compute). It follows the
Factorio recipe: two defensible transfers of one measured donor, centred on their geometric mean.
Here the donors are much closer to the target than Factorio's were — Epoch AI's SWE-bench
Verified logs for the *same two models* in agentic tool-calling harnesses under the same caching
regime on each provider's side — and the two transfers land within 8% of each other on three of
the four cells. The residual compute uncertainty from the inversion is a factor of 1.33 upward on the
Opus rows and 0.80x to 1.16x on the GPT-5.2 rows, against the 100B active-parameter prior's
grade-C factor of roughly three, which dominates both.

Nothing else in the source supports a row. Nine models are scored but only two have a published
cost; the post-training experiment publishes real training FLOPs but reaches 11-14% of the
rubric. All of that is in `candidates/bankertoolbench/dispositions.csv`.

## What the source publishes

BankerToolBench (BTB) is Handshake AI's benchmark of junior investment-banking workflows,
arXiv:2604.11304v1, submitted 13 April 2026. Extracts are retained at
`agent-work/sources/bankertoolbench/btb-paper-extracts.md` with provenance beside them.

- **100 tasks.** Each is a senior banker's request, a data room of preloaded Excel, PDF,
  PowerPoint and image files, three MCP tools (a market-data API, an SEC EDGAR API, a company
  profile API) frozen to the task's historical date with the internet closed, and a sandbox with
  LibreOffice, Python and the file-manipulation libraries. The deliverable is typically multiple
  files: an Excel valuation, merger or LBO model, plus a pitch deck, tracker or memo. Product mix
  is 62% M&A, 19% leveraged finance, 10% ECM, 6% DCM and 3% both M&A and leveraged finance.
- **Rubrics.** Each task carries a banker-written rubric, average 150 binary criteria, weighted
  1 / 3 / 5 / 10 for nice-to-have / minor / major / critical. `Score` is the weighted percentage
  of criteria passed, times 100, averaged over tasks. An LLM verifier applies it.
- **Nine models, three runs each, one baseline harness.** OpenCode is the primary harness. A
  separate comparison runs Claude Opus 4.6 and GPT-5.2 through OpenCode, OpenHands and Goose.
- **No token counters anywhere.** Confirmed against the paper, the GitHub repository
  (`Handshake-AI-Research/bankertoolbench`, tree listed 2026-09-13: Harbor adapter, MCP tool
  servers, system prompt, verifier runner, no run logs) and the Hugging Face dataset (task
  inputs, shared tools, golden outputs for 10 of the 100 tasks). Artificial Analysis publishes no BTB evaluation.

## Human time

**The value: 18,000 seconds, mean, over 100 recorded completions.**

Section 3.1: "Each task was completed by human bankers, taking them an average of 5 hours and up
to 21 hours". Table 1's note defines the quantity: "Task completion time indicates the average
time required by a human expert to attempt one task from the benchmark", listed as 5 hours for
BTB against 7 for GDPval, 1.4 for APEX-Agents and 16 minutes for Finance Agent. So the statistic
is a mean over the 100 tasks, one banker completion each, and the conversion is 5 x 3600 = 18,000.

**`human_time_method` is `other_calculation`, not `reported`**, under the `DECISIONS.md` ruling
that a source-published mean is a statistic over recorded timings. `human_time_evidence` is
`task_timings`: these are recorded completions of the stated task by the stated population, not
estimates. `human_time_statistic` is `mean`; `human_attempts` is 100.

**Why not `source_estimate`, and how close the call is.** Damon's 2026-09-13 ruling adds
`source_estimate` for a duration the source estimated rather than observed. This is roughly a
60/40 call for `task_timings`, and `source_estimate` is the conservative alternative.

For `task_timings`: Section 3.1 asserts what the work took the people who did it — "Each task *was
completed* by human bankers, taking them an average of 5 hours and up to 21 hours" — rather than
what it ought to take, and a reported mean with an unround 21-hour maximum reads as a summary of
observations rather than a forecast.

Against it: **the paper describes no time-capture mechanism anywhere**. The only duration
instrument it documents is the Job Task Analysis survey's 11-point self-report scale, which is per
workflow, not per task. Section 4.2's "cumulatively working for over 5,700 hours" is a project
total and says nothing about how per-task time was recorded. Table 1's gloss is "the average time
required by a human expert to *attempt* one task", harmonised across a row that includes GDPval's
7 hours, which the Codex dataset carries as an estimate. And 5 hours is round where 21 is not.

Nothing else in the row turns on it: `source_estimate` with `human_time_method = estimated`
validates, and the 18,000 seconds does not move either way.

**`human_time_subset` is `successful`, and this is a judgment.** Section 4.4's pipeline requires
at least four bankers per task; final reviewers "assess the *expected deliverable* created by the
task author, ensuring it meets the standards for the actual work produced by top bankers", and
either of two final reviewers can reject the task, after which "BTB did not end up including many
draft tasks that bankers produced". The 100 retained timings are therefore attempts whose
deliverable met the standard. That is an outcome filter, not merely a skill-group selection, so
`successful` is the right value and `different_attempt_selection` is flagged, because the AI side
averages all 300 task runs including failures. It is the conservative reading rather than a clean
one: a rejected task is "sent back to Step 2" for revision rather than discarded outright, and
rejections "often indicate problems with the rubric, prompt, or task feasibility", so the filter
operates mostly at the task level. `all` is about equally defensible and would drop the
`different_attempt_selection` flag with no other change.

**What the 5 hours does and does not include.** It is the author's time completing the task and
producing the expected deliverable. It is not the benchmark-construction effort: 172 bankers
worked "cumulatively over 5,700 hours" across the project, which is about 57 hours per task
including prompt design, data-room assembly, rubric writing and four-stage review. The
5-hours-per-task figure is an order of magnitude below that and is the only figure the paper
attaches to task completion, so the two are clearly different quantities. The ratio is a useful
consistency check on the reading.

**The population.** Expert. 172 contributing bankers, mean 3.4 years of investment-banking
experience (median 2.8, two-year minimum), 47% analysts, 38% associates, 12% director or VP, at
bulge-bracket and elite-boutique banks. Section 4.3 adds that "Each task closely mirrors a real
job that the contributor previously completed at their bank", so the author had done the
underlying work before — an advantage over the agent that is stated here rather than adjusted for.

**What is not recoverable.** Only the mean and the 21-hour maximum are published. The released
`tasks.jsonl` carries `task_id`, `final_prompt`, `prompt_context`, `formatting_context`,
`product`, `workflow_cat`, `workflow_subcat`, `aggregated_rubric_json` and `canary`, and no time
field. The Job Task Analysis survey (n=193) rates workflow duration on an 11-point scale from
under 15 minutes to over a year, but per workflow category rather than per task, so it cannot
supply a distribution either. `DECISIONS.md` forbids contacting the authors. The 5 hours is a
rounded published figure and is used as it stands.

## The performance reading

BTB's human baseline is the gold deliverable **by construction**. The task author produced it,
wrote the rubric against their own process and against a baseline AI output, and reviewers
confirmed it meets top-banker standards. The verifier was never run on it and no independent
human attempt was scored. So the human's position on the benchmark's own metric is an assumed
100, and `performance_evidence` says so rather than presenting it as an observed result.

The chance floor is zero and the paper says so directly: "Agents which do nothing will trivially
receive a `Score` of 0 in BTB, since they will not have generated deliverable files."

**Ruling: the rows are labelled on `Score`.** The above-chance ratios are then

| Cell | Score | Ratio to human | Replicate SD over 3 runs | Replicate SE of the mean | Replicate SE margins above the 0.5 guide | Task-sampling SE margins |
|---|---:|---:|---:|---:|---:|---:|
| Claude Opus 4.6, OpenHands | 53.0 | 0.530 | 0.4 | 0.23 | 13.0 | 1.2 to 2.0 |
| Claude Opus 4.6, OpenCode | 53.2 | 0.532 | 0.5 | 0.29 | 11.1 | 1.3 to 2.1 |
| GPT-5.2, OpenHands | 54.5 | 0.545 | 1.5 | 0.87 | 5.2 | 1.8 to 3.0 |
| GPT-5.2, OpenCode | 56.1 | 0.561 | 0.2 | 0.12 | 52.8 | 2.4 to 4.1 |

**The two SE columns measure different things and the second is the relevant one.** Table 4's
standard deviations are run-to-run reproducibility of a 100-task mean, not sampling error over
tasks, so the "13.0 / 11.1 / 5.2 / 52.8" figures overstate the margin badly. **The per-task `Score`
standard deviation is not published.** Table 3's between-subcategory standard deviation is 5.23
points over 11 subcategories, and a per-task spread of 15 to 25 points is the plausible
consequence, giving a sampling SE over 100 tasks of 1.5 to 2.5 points. On that basis the four
rows sit 1.2 to 3.0 standard errors above the guide, which is the last column.

All four are `below` on either reading: the agent produced the deliverable set and satisfied a
little over half of the banker's criteria, which is Damon's "basically does the job, somewhat
worse than the human". The close-call rule in `DECISIONS.md` bites only below the guide, so it
does not apply to any of them, and no label turns on which standard error is used.

**Three reasons for taking `Score` rather than `Pass Rate`.**

1. The paper recommends it: "In the remainder of our results, BTB performance is measured using
   the aforementioned `Score`, which we recommend for fine-grained model comparison", and it is
   the metric with "high construct validity". `Pass Rate` is a transform of `Score` thresholded
   at T = 0.8 to predict banker acceptability.
2. `DECISIONS.md` has already ruled this way once. The APEX-Agents acceptance judged models on
   Mercor's criterion-level mean pass rate where it existed and fell back to pass@1 only where it
   did not, because pass@1 fails a task on any single missed criterion and understates work done.
   BTB's `Score` is exactly the criterion-level quantity; its `Pass Rate` is the whole-task one.
3. The exclusion rule's purpose is to drop rows where the AI basically did not do the job. `Pass
   Rate` answers "would a banker ship this", which is a different question from "how much of this
   job did it do".

**The reading that would exclude every row, stated plainly.** On `Pass Rate` the best model,
GPT-5.4, passes 16% of tasks against a human 100% by construction, a ratio of 0.16. On the
critical-weight criteria the figure is 1-2%. On the bankers' own readiness question, "0% of AI
deliverables are rated Sendable as-is", and Section 6.3 records that Claude Opus 4.6's
spreadsheets have "most of the key values hard-coded rather than formula-backed, which is
absolutely unacceptable in IB". Any of these would exclude all four rows. This is the same metric
asymmetry `DECISIONS.md` already records for APEX-Agents, and it is recorded in
`candidates/bankertoolbench/dispositions.csv` so the coordinator can flip the block in one place.

**Verifier error, and why it does not move the label.** Appendix D grades the verifier against a
two-banker consensus over 1,356 criteria: accuracy 88.22%, recall 0.933, false-positive rate
18.61%, kappa 0.756 against human inter-rater kappa 0.69-0.82. Two corrections follow and they
push opposite ways.

- *Same instrument on both sides.* If the gold truly satisfies every criterion, the verifier
  would score it at the recall, 93.3 rather than 100. Ratios rise to 0.568, 0.570, 0.584, 0.601.
  Further above the guide.
- *Both sides de-biased to truth.* A measured score is `p * recall + (1 - p) * FPR`, so a
  measured 0.532 implies a true criterion pass rate of `(0.532 - 0.1861) / (0.933 - 0.1861)` =
  0.463. The four cells de-bias to 0.460, 0.463, 0.481 and 0.502. Three of four fall just under
  the guide.

The central takes neither: the recorded metric is the verifier `Score` as published, which is
what every model in the benchmark is ranked on and the only measurement the human side has any
claim on at all. The de-biased reading assumes the verifier's error rates on AI deliverables
transfer to a gold deliverable that is well-formed by construction, which is unlikely and
unmeasured. It is recorded here because three of the four rows sit close enough to the line that
a coordinator should see it. Note also that the de-biased reading moves GPT-5.4, which is not a
row, to 0.529, so it does not change which models would survive by much.

## Compute

All arithmetic is in `research/bankertoolbench/compute_btb.py`, whose output is retained at
`agent-work/derived/bankertoolbench/calculations.json`. The reproduction command is at
[Reproduction](#reproduction).

### What the source gives, and what the row needs

Section B.2, the only place in the paper where a dollar figure appears: "OpenHands is 110% more
expensive than OpenCode when running GPT-5.2 (averaging $2.32 vs. $1.10 per run) and 30% more
expensive when running Claude Opus 4.6 ($2.60 vs. $2.00) ... Goose does not expose cost data".
Table 4 gives the matching runtimes: 1771.4, 977.3, 703.8 and 701.6 seconds, means over three
runs. Section 3.1 adds that agents "require up to 539 LLM calls to complete each task, where 97%
of their steps involve tool calls or code generation/execution".

The row needs `B` = fresh input + cache creation + output, the quantity COLUMNS.md's
`params_tokens` rule multiplies by the model coefficient with cache reads removed. Cost is a
linear function of four token counts, so one dollar figure cannot recover `B` without a
structure.

**The verifier's cost is excluded.** Table A7 reports a mean verifier cost of $0.495 per task,
separately from these figures. Two things confirm the Section B.2 numbers are agent cost, not
agent plus verifier: the paper's own "110% more expensive" is 2.32/1.10 exactly, which fails if a
common $0.495 sits inside both; and Section 6.5 attributes the cost gap to the harness making
more LLM calls. COLUMNS.md excludes an evaluation model outside the stated work unit in any case.

### Prices

From `research/cost/list-prices.csv`, USD per million tokens, at the price sheets in force on
2026-04-13. The paper does not state its run dates; that is its arXiv submission date, and
neither sheet changes between the models' releases and it.

| Model | Window opens | Input | Cached read | Cache write | Output |
|---|---|---:|---:|---:|---:|
| claude-opus-4-6 | 2026-02-05 | 5.00 | 0.50 | 6.25 | 25.00 |
| gpt-5.2-2025-12-11 | 2025-12-11 | 1.75 | 0.175 | — | 14.00 |

Reasoning tokens bill as output on both. The Anthropic sheet's `inference_geo=us` 1.1x multiplier
is not applied: the paper does not say where it ran, and the effect is at most 10% downward on
`B`. Batch discounts do not apply to an interactive agent loop.

### What the harness code establishes, and for which provider

This is the assumption that would silently corrupt every number if wrong, and it is the one the
APEX-Agents row turned on in the opposite direction (Stirrup sets no `cache_control` anywhere, so
its Anthropic input was gross). **It resolves differently for the two models, and the section must
say so: the breakpoint evidence covers Claude Opus 4.6 only.**

**Anthropic side — both harnesses set breakpoints, and both list this model.**

- **OpenCode**, `packages/opencode/src/provider/transform.ts`, function `applyCaching`: it takes
  the first two system messages and the last two non-system messages and attaches
  `anthropic: { cacheControl: { type: "ephemeral" } }` to each. Retained at HEAD
  (`opencode-applycaching.ts.txt`, commit 631f67a9f330e2e0b1c064db358e67133a053655) and at the
  run-era commit 63035f977ff3 of 2026-04-11, two days before the paper's submission
  (`opencode-applycaching-runera.ts.txt`). The two differ only by a later `alibaba` entry.
- **OpenHands**, `openhands-sdk/openhands/sdk/llm/llm.py`, method `_apply_prompt_caching`: it
  marks the static system block and "the last user/tool message so the cached prefix extends every
  turn". Retained at HEAD (`openhands-applypromptcaching.py.txt`, commit
  15a9b8609c12635abacefa1f91beacedd7798296). The pass runs only when `is_caching_prompt_active()`,
  which is a match against `PROMPT_CACHE_MODELS`; `claude-opus-4-6` is in that list at the run-era
  commit 5f106d052b40 of 2026-03-23, retained at
  `agent-work/sources/bankertoolbench/openhands-promptcachemodels-runera.py.txt`.

Both are the sliding-breakpoint pattern that produces near-full prefix reuse across turns, the
same pattern the Anthropic donor below runs.

**OpenAI side — no harness sets a breakpoint, and none is needed.** `PROMPT_CACHE_MODELS` is
Anthropic-only; a GPT-5 model matches `PROMPT_CACHE_RETENTION_MODELS` instead, which is a
retention parameter on OpenAI's own automatic cache rather than a breakpoint mechanism. OpenCode's
`applyCaching` provider options carry `anthropic`, `openrouter`, `bedrock`, `openaiCompatible` and
`copilot` and no native `openai` key. So the claim for the two GPT-5.2 rows is the weaker and
correct one: **OpenAI caches automatically at 1,024+ tokens and neither harness disables it**,
which is exactly `DECISIONS.md`'s default-on caching case, and OpenHands additionally extends the
retention of that automatic cache. The GPT-5.2 rows do not lean on this much in any event: their
alpha comes from measured OpenAI cache-read counters in the donor, and their no-cache-read ceiling
is only 1.15 to 1.16 times the central.

### The donors

The structure is transferred from measured runs of **the same two models** in agentic
tool-calling harnesses, taken from evidence already retained in this folder,
`agent-work/sources/epoch-swebench-bins/epoch-swebench-perinstance.csv`. A call is half the transcript
length, the convention `research/epoch-swebench-bins.md` uses for the same logs.

| Donor run | Harness | Model | B per instance | alpha | fresh / cache-write / output share | Calls | Cached prefix per call | Seconds per call |
|---|---|---|---:|---:|---|---:|---:|---:|
| agen-epoch-swebench-opus46cc | Claude Code CLI | claude-opus-4-6 | 84,293 | 15.370 | 0.4375 / 0.4275 / 0.1349 | 32.87 | 39,412 | 13.383 |
| agen-epoch-swebench-gpt52high | Inspect basic agent | gpt-5.2-2025-12-11 | 389,439 | 2.957 | 0.8814 / 0 / 0.1186 | 81.14 | 14,194 | 16.033 |

`alpha` is cache-read tokens per billed unit. Two notes on the choice.

- **Why the Claude Code run rather than the plain Inspect one for Opus 4.6.** The paper describes
  its own primary harness as "a popular open-source alternative to Claude Code that provides
  modern agentic capabilities like code generation/execution, MCP tool calling, and context
  compaction". `agen-epoch-swebench-opus46cc` is literally the Claude Code CLI agent on the same
  model. The plain Inspect run, `agen-epoch-swebench-opus46` at alpha 8.766, is carried as the
  `alternate_donor` scenario, and it raises the result by 1.25x to 1.33x.
- **Why the plain Inspect run for GPT-5.2.** No Claude-Code-equivalent GPT-5.2 run exists in
  either dataset. The nearest corroboration is `agen-epoch-swebench-gpt54high`, the next OpenAI
  model in the same harness, at alpha 3.336 against 2.957, which is the `alternate_donor`
  scenario for these rows and moves them 0.80x.

**Truncation in the donors.** Epoch's Inspect runs carry a 2,000,000-token budget. It binds on
72 of 484 instances (14.9%) in the Opus donor and 103 of 484 (21.3%) in the GPT-5.2 donor, which
is minority censoring and is kept under the `DECISIONS.md` harness-cap ruling. Restricting each
donor to its uncensored instances lowers alpha (to 11.21 and 1.39, because the truncated runs are
the long-prefix ones) and therefore raises `B` by 1.13x to 1.25x. That is the
`uncensored_only_donor` scenario. The all-instance structure is central because BTB runs are long
and have no equivalent cap.

### Two transfers, and the geometric mean

Following the `DECISIONS.md` ruling used for the Astra Factorio row. Write `P_new` for the dollar
price of a million billed units excluding the cache-read term, `P_new = u*P_in + w*P_cw +
beta*P_out` at the donor's shares: **$8.2326 per million for Opus 4.6** and **$3.2033 for
GPT-5.2**.

- **Transfer A, cost.** Carry the donor's dollars per billed unit, equivalently its alpha:
  `P_eff = alpha*P_cached + P_new`, so $15.9175 per million for Opus 4.6 and $3.7209 for GPT-5.2,
  and `B = cost / P_eff`.
- **Transfer B, cadence.** Carry the donor's seconds per call and its cached prefix per call. The
  cell's own measured runtime fixes the call count; the cost per call less the cached prefix's
  cost buys new content at `P_new`; alpha falls out.

Neither is privileged by the evidence, so the central is their geometric mean, reported at the
single alpha that reproduces it so tokens, cache reads and FLOPs stay consistent.

| Cell | Transfer A | Transfer B | Central B | Central alpha | Calls | compute_flops |
|---|---:|---:|---:|---:|---:|---:|
| Opus 4.6, OpenCode | 125,648 | 117,448 | 121,479 | 16.46 | 51 | 2.4296e16 |
| Opus 4.6, OpenHands | 163,342 | 189,936 | 176,138 | 13.06 | 58 | 3.5228e16 |
| GPT-5.2, OpenCode | 295,631 | 296,127 | 295,879 | 2.94 | 61 | 5.9176e16 |
| GPT-5.2, OpenHands | 623,512 | 638,575 | 630,998 | 2.71 | 120 | 1.2620e17 |

`compute_flops` is `B * 2e11`, the shared coefficient for both models at the registry's 100B
active parameters.

**The two transfers agree far better here than at Factorio, and the reason is checkable.** They
coincide exactly when the target's dollars per second of runtime equals the donor's. The Opus
donor spends $0.00305 per second and the GPT-5.2 donor $0.00111; the four cells spend $0.00285,
$0.00369, $0.00113 and $0.00131. The GPT-5.2 OpenCode cell matches its donor to 1.05%, which is
independent corroboration that the donor's structure is the right one to carry. The largest gap,
Opus on OpenHands at 1.21x the donor's rate, is the 16% spread between its two transfers.

**The call count is a sanity check that passes.** Section 3.1's "up to 539 LLM calls" is a
maximum over tasks and agents. The central call counts are means of 51 to 120, comfortably under
it, and the implied new content per call is 2,240 to 5,780 billed units, which sits beside the
donors' own 2,564 and 4,799.

### Compute scenarios

Ratios to each row's central. `DECISIONS.md` requires the cached-context attention scenario for
any run re-reading more than about 10,000 tokens per call; the mean prefixes here are 39,500
(Opus) and 14,200 (GPT-5.2) tokens, so both qualify.

| Scenario | Opus 4.6 OpenCode | Opus 4.6 OpenHands | GPT-5.2 OpenCode | GPT-5.2 OpenHands |
|---|---:|---:|---:|---:|
| Alternate donor run | 1.33x | 1.25x | 0.80x | 0.81x |
| Uncensored donor instances only | 1.25x | 1.20x | 1.14x | 1.13x |
| Cadence on the donor's total rather than working time | 1.01x | 1.01x | 1.01x | 1.01x |
| BTB cadence half the donor's (twice as many calls) | infeasible | 0.58x | 0.92x | 0.93x |
| BTB cadence twice the donor's (half as many calls) | 1.24x | 1.15x | 1.04x | 1.03x |
| No cache reads at all (arithmetic ceiling, not live) | 2.00x | 1.79x | 1.16x | 1.15x |
| Active parameters at the prior's grade-C range | \~0.3x to \~3x | \~0.3x to \~3x | \~0.3x to \~3x | \~0.3x to \~3x |

The cache assumption barely matters for the GPT-5.2 rows: even if every input token were fresh,
they would rise only 15-16%, because a low alpha means cache reads are a small part of the bill.
For the Opus rows the ceiling is a factor of two, and the harness code above is what rules it out.

**Seconds per call is the cadence transfer's weakest input**, and the two cadence rows bound it.
BTB spends 97% of its steps on tool calls and sandbox code execution — LibreOffice, `pdfplumber`,
`openpyxl` — so a slower per-call wall clock than the donor's is the more likely direction, and it
pushes `B` up: fewer calls means less cached-prefix spend out of a fixed budget and more of it
buying new content. At twice the donor's seconds per call the Opus OpenCode row rises 1.24x,
inside its 2.00x no-cache ceiling. The downward branch is bounded more sharply than by arithmetic
alone: at half the donor's seconds per call that row becomes **infeasible**, because the cached
prefix over the implied 105 calls would cost more than the $2.00 the run actually spent. The run's
cadence therefore cannot have been much faster than the donor's, which is a constraint the cost
figure imposes on the transfer rather than an assumption added to it.

Cached-context attention, since folded into `compute_flops` (`research/attention-correction.md`)
and one-sided upward, at
`4 * L * d_model * N_context` per appended position:

| Cell | Mean prefix | L=64, d=8192 | L=96, d=12288 |
|---|---:|---|---|
| Opus 4.6, OpenCode | 39,457 | 1.005e16 (0.41x) | 2.262e16 (0.93x) |
| Opus 4.6, OpenHands | 39,735 | 1.468e16 (0.42x) | 3.302e16 (0.94x) |
| GPT-5.2, OpenCode | 14,194 | 8.808e15 (0.15x) | 1.982e16 (0.33x) |
| GPT-5.2, OpenHands | 14,247 | 1.885e16 (0.15x) | 4.242e16 (0.34x) |

### Field choices

- `compute_method` is `params_tokens`: one model, one coefficient, and `B` is constructed to
  exactly the fresh-input-plus-cache-creation-plus-output definition the rule uses.
- `tokens_accounting` is `input_cache_creation_output`. For GPT-5.2 the cache-creation term is
  structurally zero: OpenAI's counters partition input into ordinary and cached with no separate
  cache-write charge, the counter form `DECISIONS.md` records as distinct from Anthropic's
  additive one.
- `tokens` is treated as text only. Five of the 100 tasks carry an image or PNG input file
  (Table A3), and the agents read the data room through `pdfplumber`, `openpyxl` and `pillow` in
  the sandbox rather than through a vision channel, so no image-billing split is separated out.
- `compute_evidence` is `derived_assumed_inputs`, matching the Factorio row: the workload's
  magnitude is set by this cell's own measured spend, and only the mix converting it is assumed.
  It is not `transferred_workload`, which COLUMNS.md reserves for a workload borrowed from
  another task; the dollars belong to this work unit.
- `ai_cost_date` is 2026-04-13, the paper's arXiv submission date, used as a proxy because the
  paper gives no run dates. Precedent `reported` rows in this folder use the run date. It is
  harmless here: both price windows open before every candidate run date and neither has closed,
  so any date between the models' releases and the submission gives the same prices.
- `compute_statistic` is `mean` and `ai_attempts` is 300. Table 4's Score and runtime are
  explicitly means over three runs of the 100 tasks. The cost sentence in Section B.2 describes
  the same cells but does not restate the averaging basis, so 300 rather than 100 is a reading of
  it; if the costs came from a single replicate the count would be 100 and no other field moves.

## Model records

Both model IDs already exist in the Codex registry at
`../AI Compute vs Human Time/dataset/models.csv` and are reused unchanged, so
`candidates/bankertoolbench/models.csv` carries only its header.

| model_id | flops_per_token | active_parameters | Basis |
|---|---:|---:|---|
| claude-opus-4-6 | 2.0e11 | 1.0e11 | estimated; shared record |
| gpt-5.2-2025-12-11 | 2.0e11 | 1.0e11 | estimated; shared record |

Neither appears in `research/model-priors/accepted-priors.csv`, so Damon's 2026-09-13 priors
ruling leaves both at 100B active. Both are grade C with roughly threefold ranges, which is the
largest single source of uncertainty in these rows and larger than the whole cost-inversion band.

## Comparison issues

`different_inputs_or_tools; different_assessment; different_attempt_selection`.

- **different_inputs_or_tools.** This is the row's strongest concrete comparison issue, and it is
  about supplied information, not only execution. **Every published BTB score is the
  maximum-context arm.** The released `tasks.jsonl` carries `prompt_context` and
  `formatting_context` as fields separate from `final_prompt`, and the repository's Harbor adapter
  defaults to `include_prompt_context=True, include_formatting_context=True`, so the agent's
  prompt carries an extra context section that Section 4.3 says gives "slightly more detail than a
  junior banker would typically receive". Section 6.4's ablation shows both layers "significantly
  improve performance" when added, so the scored arm is the assisted one. Execution differs too:
  the agent is barred from the internet and must build its Excel and PowerPoint deliverables
  through `openpyxl`, `python-pptx` and LibreOffice inside a Harbor sandbox, with a harness system
  prompt wrapped around the request. Cutting the other way, the data room and the MCP tools are
  shared — Section 4.3 has the task author "complete the task using the tools and data available
  in the environment" — and the banker had previously performed the underlying job at their bank.
- **different_assessment.** Only the AI was verifier-scored. The human's position on the metric is
  the gold deliverable passing by construction, not a measurement. See
  [The performance reading](#the-performance-reading).
- **different_attempt_selection.** The 100 human timings are completions whose deliverable passed
  a four-banker review; the AI compute is a mean over 300 task runs regardless of outcome.

## Reproduction

From this folder:

```
python3 research/bankertoolbench/compute_btb.py \
    --cells  agent-work/sources/bankertoolbench/btb-table4-harness.csv \
    --prices research/cost/list-prices.csv \
    --donors agent-work/sources/epoch-swebench-bins/epoch-swebench-perinstance.csv \
    --out    agent-work/derived/bankertoolbench/calculations.json

python3 research/bankertoolbench/build_rows.py \
    --calculations agent-work/derived/bankertoolbench/calculations.json \
    --columns      COLUMNS.md \
    --out          candidates/bankertoolbench/points.csv
```

Both need only the Python standard library. `build_rows.py` reads the column order out of
COLUMNS.md, asserts the CSV text-length norms from `DECISIONS.md`, and checks that no cited path
ends in punctuation. Writing to a different `--out` reproduces without touching retained evidence.

## work-btb-opus46-opencode

Claude Opus 4.6 in the OpenCode harness, the paper's primary configuration for this model.
`Score` 53.2 (SD 0.5 over three runs), runtime 701.6 s, cost $2.00 per run.

```
P_new  = 0.43755*5 + 0.42755*6.25 + 0.13491*25   = 8.2326 USD per million billed units
A: P_eff = 15.3699*0.50 + 8.2326 = 15.9175   B = 2.00 / 15.9175 * 1e6 = 125,648
B: calls = 701.6 / 13.3826 = 52.43
   USD per call      = 2.00 / 52.43            = 0.038149
   cached prefix cost= 39,411.8 * 0.50 / 1e6   = 0.019706
   new content       = 0.018443 / 8.2326 * 1e6 = 2,240.2 billed units per call
   B = 52.43 * 2,240.2 = 117,448     alpha = 39,411.8 / 2,240.2 = 17.59
central B = sqrt(125,648 * 117,448) = 121,478.5   alpha = 16.4625   calls ~ 51
compute_flops = 121,478.5 * 2e11 = 2.4295709e16
```

Ratio to the human baseline 0.532: 11.1 replicate standard errors above the exclusion guide on Table 4's run-to-run SD, or 1.3 to 2.1 on a task-sampling basis at a plausible per-task Score SD of 15 to 25 points. See [The performance reading](#the-performance-reading) for which is which; the label is the same on both.

## work-btb-opus46-openhands

Claude Opus 4.6 in the OpenHands harness. `Score` 53.0 (SD 0.4), runtime 703.8 s, cost $2.60.

```
A: B = 2.60 / 15.9175 * 1e6 = 163,342
B: calls = 703.8 / 13.3826 = 52.59 ; USD per call 0.049439 ; cached prefix 0.019706
   new content 0.029733 / 8.2326 * 1e6 = 3,611.6 per call ; B = 189,936 ; alpha = 10.91
central B = sqrt(163,342 * 189,936) = 176,137.6   alpha = 13.0572   calls ~ 58
compute_flops = 176,137.6 * 2e11 = 3.5227518e16
```

This cell is the widest of the four, a 16% spread between the transfers, because it spends 21%
more per second of runtime than its donor. Ratio to the human baseline 0.530. The paper notes
that OpenHands' extra spend buys no quality here: 53.0 against OpenCode's 53.2.

## work-btb-gpt52-opencode

GPT-5.2 at high reasoning effort in the OpenCode harness, the paper's primary configuration for
this model. `Score` 56.1 (SD 0.2), runtime 977.3 s, cost $1.10.

```
P_new  = 0.88136*1.75 + 0.11864*14.00          = 3.2033 USD per million billed units
A: P_eff = 2.9573*0.175 + 3.2033 = 3.7209   B = 1.10 / 3.7209 * 1e6 = 295,631
B: calls = 977.3 / 16.0333 = 60.95 ; USD per call 0.018046 ; cached prefix 14,194.1*0.175/1e6 = 0.002484
   new content 0.015562 / 3.2033 * 1e6 = 4,858.2 per call ; B = 296,127 ; alpha = 2.92
central B = sqrt(295,631 * 296,127) = 295,878.6   alpha = 2.9395   calls ~ 61
compute_flops = 295,878.6 * 2e11 = 5.9175727e16
```

The two transfers agree to 0.2%, because this cell's $0.00112555 per second of runtime is within
1.05% of the donor's $0.00111387. Ratio to the human baseline 0.561, the highest of the four rows.

## work-btb-gpt52-openhands

GPT-5.2 at high reasoning effort in the OpenHands harness. `Score` 54.5 (SD 1.5), runtime
1771.4 s, cost $2.32.

```
A: B = 2.32 / 3.7209 * 1e6 = 623,512
B: calls = 1771.4 / 16.0333 = 110.48 ; USD per call 0.020999 ; cached prefix 0.002484
   new content 0.018515 / 3.2033 * 1e6 = 5,779.9 per call ; B = 638,575 ; alpha = 2.46
central B = sqrt(623,512 * 638,575) = 630,998.4   alpha = 2.7050   calls ~ 120
compute_flops = 630,998.4 * 2e11 = 1.2619969e17
```

The highest-compute row in the set, and the clearest illustration of the harness effect: 1.8
times the runtime and 2.1 times the cost of the same model on OpenCode, for 1.6 fewer `Score`
points. Section B.2 attributes it to OpenHands generating "large monolithic scripts and then
spend[ing] the bulk of its runtime in a code-execute-debug loop". Ratio to the human baseline
0.545.

## Dispositions

`candidates/bankertoolbench/dispositions.csv` holds 20 records. In summary:

- **Two Goose cells** (Opus 4.6 at `Score` 52.9, GPT-5.2 at 56.7). Both would clear the exclusion
  line; the paper states Goose does not expose cost data, so they have no compute evidence at all.
- **Seven models from the primary nine-model evaluation** — Opus 4.5 (52.3), Gemini 3.1 Pro
  Preview (53.6), GPT-5.4 (58.1), GLM 5 (46.8), Qwen 3.5 397B (42.6), Grok 4 (31.4), Gemini 2.5
  Pro (29.4). No cost and no tokens are published outside the two-model harness comparison. Three
  of the seven would also fall under the exclusion guide on `Score`. The loss of GPT-5.4, the
  benchmark's best model, is the most annoying of these.
- **Six post-training records** (Qwen 3 4B and 32B, base plus Dr. GRPO plus DPO). These are the
  only genuinely reported compute figures in the paper: 13.0 and 143.6 EFLOPs for the 20 offline
  passes, plus roughly 35 and 177 hours of 8xH100 rollout generation for the frozen 1,600-rollout
  pools. They are excluded on performance, not compute: the post-trained models reach 0.11 to
  0.14 of the rubric against the banker deliverable, so the AI performance is not comparable to
  the human's under the exclusion ruling. Their holdout is also 20 of the 100 tasks, whose own
  human-time mean is not published.
- **The `Pass Rate` block judgment**, recorded so it can be flipped in one place.
- **Two human-time dead ends**: the Job Task Analysis survey's per-workflow duration scale, and
  the absence of any per-task timing in the released artifacts.
- **Two sub-analyses of the same runs**: Figure 9's reduced-context arms and Table A6's banker
  preference ranking. Neither publishes a separate cost, so neither could ever be built. They are
  listed so the source's record identities reconcile against rows and dispositions without a gap.
