# OmegaUse-OfficeVal: LLM agents against junior office workers on 100 timed office deliverables

*Created 2026-09-13 17:29.*
*Last revised 2026-09-13 18:07, Revision 1 after `reviews/omegause-officeval-independent.md` and the coordinator's rulings on it. Change log in `candidates/omegause-officeval/REVISION.md`.*

## Summary

Baidu's Agent Frontier Team published **OmegaUse-OfficeVal** (arXiv:2607.27155,
v1 2026-07-29, v2 2026-08-18): 100 real office-suite tasks, each a request plus
its input files, each delivered as a finished docx, pptx, xlsx or pdf, each
scored by a task-specific code verifier built from expert-revised rubrics. Both
sides of the comparison are measured on the same 100 tasks with the same
verifiers.

**The human side is the strongest in the fresh sweep.** Twenty screened
annotators worked the tasks without LLM assistance under a quality-gated
incentive scheme; each task went to at least two of them, and to a third when
their times diverged by more than 30%. The per-task figure is the mean of the two
shortest valid completion times, and all 100 are shipped in the public Hugging
Face parquet. Mean **139.42 minutes = 8,365.2 seconds**, median 122, range 5 to
501. The benchmark score of the best human submission per task is **27.79**.

**The compute side has to be inverted from dollars.** The paper publishes cost
per task and wall-clock hours per task and no token counts. The inversion prices
the bill at each provider's list rates and transfers a cache structure from
agentic runs of the same model endpoint that do publish one — Epoch AI's
SWE-bench Verified per-instance logs and Artificial Analysis's long-horizon agent
benchmarks. Damon has ruled cost-only compute rows acceptable where the
conversion is explicit; this one is, and it comes with an independent check the
Factorio row could not run.

**That check is the main reason to believe the numbers.** Two logically separate
quantities agree. Inverting the dollars at the donor's cache structure, and
separately rescaling the donor's *billed positions per second of agent working
time* by OmegaUse's own wall clock, land within a factor of 1.06 of each other
for Kimi K2.6, 1.2 for GLM-5.2 and 1.6 for DeepSeek-V4-Pro. If the paper's cost
had instead been computed on gross prompt tokens with no cache discount, the same
check would be off by 2.2 to 8.8 times, and by 4.7 and 6.1 times on the two rows
where the comparison is sharpest. That is what rules the no-cache-discount
reading out as the central, and it is stated as a scenario instead.

| point_id | model | FLOPs | branch range | tokens | human time | score | ratio | label |
|---|---|---:|---|---:|---:|---:|---:|---|
| agen-omegause-officeval-glm52 | GLM-5.2 | 1.71e16 | 1.20e16-2.44e16 | 213,988 | 8,365.2 | 17.91 | 0.64 | below |
| agen-omegause-officeval-kimik26 | Kimi K2.6 | 9.14e15 | single donor, see the h band | 142,822 | 8,365.2 | 17.00 | 0.61 | below |
| agen-omegause-officeval-dsv4pro | DeepSeek-V4-Pro | 2.44e16 | 1.88e16-3.17e16 | 249,179 | 8,365.2 | 14.48 | 0.52 | below |
| agen-omegause-officeval-minimaxm3 | MiniMax M3 | 3.61e16 | 2.67e16-4.88e16 | 783,920 | 8,365.2 | 13.82 | 0.50 | below, close call |

All four are `below`: each does a substantial part of the job at clearly lower
quality than a junior office worker. MiniMax M3 at 0.4973 of the human score sits
0.02 standard errors under the half-of-human guide and is kept by the close-calls
ruling. Nothing is excluded. **A fifth cell, Qwen3.7-Plus, is not built**; the
reason is in [The Qwen3.7-Plus cell](#the-qwen37-plus-cell).

Four things move the compute, in descending order.

1. **Which donor's cache structure is transferred.** The branch spread is 1.7x to
   2.0x per row and the central is the geometric mean of its ends, not a point
   estimate with error bars.
2. **Whether the paper's cost applied the providers' cache-hit rates.** The paper
   never says. The throughput check answers it, and the alternative is quantified
   per row.
3. **Two prices that are not simply listed.** DeepSeek's off-peak rate is half
   the listed one and would double that row; MiniMax's live rate carries a
   "Permanent 50% off" whose start date is not published, and the undiscounted
   rate would halve that row. Both are resolved by one principle, stated below.
4. **Cached-context attention is one-sided upward**, and `research/attention-correction.md`
   has since folded it into `compute_flops`. It
   is far smaller here than in earlier rows because two of the four models select
   a bounded number of key positions per query.

## Shared evidence

Everything below is in `agent-work/sources/omegause-officeval/`, whose `MANIFEST.md`
lists each file and where it came from.

### The benchmark and the work unit

From §3 and §4 of the paper. 1,715 practitioner-proposed tasks were filtered to
595 by expert screening, to 282 by three senior experts agreeing each task was
non-trivial, long-horizon and feasible, and curated down to 100. Instructions
were rewritten to remove identifying information, and input files were
reconstructed with LLM assistance and then manually revised. Three senior experts
had to agree on final acceptance.

**The benchmark is Chinese, and the retained parquet is not.** The Hugging Face
repository ships the tasks twice: the Chinese source in `tasks/` and `rubrics/`,
and an English translation in `task-en/`, `rubrics-en/` and the merged
`tasks_and_rubrics_en.json`. The default Data Studio parquet — the file retained
here, and the one the human times come from — is the **English merge**.
`research/omegause-officeval/language_check.py` counts the difference and writes
`agent-work/sources/omegause-officeval/language-check.csv`: **0 CJK characters across
the parquet's 100 instructions, 8,823 across the same 100 instructions in the
repository's `tasks/` directory**, which is retained as
`omegause-instructions-zh.json`. The input-file names are the same in both and
**131 of the 220 are Chinese**. So `task_description` is right to call these
Chinese-language office requests, and the locator for that claim is `tasks/`, not
the parquet. Task 1 in the original, for instance, asks for five specific
deletions and renumberings across a set of lesson-plan documents and then for the
result to be condensed onto two pages by changing only font size, line spacing
and image spacing.

Table 1 of the paper: 220 input files (63 docx, 31 pptx, 25 xlsx, 14 pdf, 77
images, 10 video or audio) and 115 required output artifacts (48 docx, 40 pptx,
24 xlsx, 3 pdf). The parquet reproduces the 220: summing `origin_files` over the
100 rows gives 2.2 files per task on average.

Scoring, from §4.3.3. Each task carries a usability rubric (219 items over the
set, 2.19 per task) and a task-completion rubric (2,009 items, 20.09 per task).
The artifact must satisfy **every** usability item or the task scores zero.
Otherwise the score is the weighted sum of triggered completion items, where
positive weights reward met requirements and negative weights penalise
unintended damage, clipped at zero and normalised by the maximum attainable
positive weight. The reported benchmark score is the sum of the 100 per-task
scores, so it reads as a percentage.

**The chance floor is zero.** Reading the retained rubrics, positive items are
specific edits the instruction asks for, so an unmodified input file triggers
none of them; whatever negative items it does trigger are clipped away. A
do-nothing policy scores 0, and the half-of-human guide therefore applies to the
raw ratio with no floor subtraction.

The AI harness, from Appendix E. One in-house scaffold for all five agents, with
programmatic tool use, shell execution and file operations, LibreOffice 24.2
available through managed `libreoffice` and `soffice` commands, and **no
GUI-level computer use**. Ubuntu 24.04.1 containers, CPU-only, inference through
remote APIs, 10 task environments in parallel with at most two concurrent
inference threads per model, and a **14,400-second wall-clock timeout per task**.
The paper warns that its reported runtimes are reference measurements affected by
scaffold, load and API latency.

### The run window

No run date is published. The five models bound it: GLM-5.2 was released
2026-06-16 and is the latest of them, and arXiv v1 went up 2026-07-29. So the
runs sit in **2026-06-16 to 2026-07-29**, and every price used below was in force
across the whole of it. `ai_cost_date` is 2026-07-29, the price-sheet date, since
the run date is unknown.

## Human baseline

From §4.2.1 and Appendix C. Twenty annotators were recruited, each interviewed
and given sample tasks to verify basic office-suite skills. The tasks are
described throughout as work "typically assigned to a junior worker, assistant,
or intern", which is why `human_skill` is `typical` rather than `expert`.

The measurement procedure, from Algorithm 1:

1. Each task goes to two randomly assigned annotators and each completion time is
   recorded separately.
2. A senior expert checks the submitted artifact. If it fails, the annotator
   revises it and **the revision time is added to that annotator's total**, until
   it passes. The submission is then valid for timing, but scores the annotator
   zero for bonus purposes.
3. If the slower valid time exceeds 1.3 times the faster, a third annotator does
   the same task under the same procedure.
4. `human_labor_time` is the **mean of the two shortest valid completion times**.

Bonuses were paid daily: the top 25% of quality-valid annotators earned 1.5x base
daily salary and the next 25% earned 1.25x. So the incentive pushes toward speed
subject to a quality gate, and the two-shortest rule pushes the recorded figure
further down. The published number is best read as a fast-but-acceptable junior
worker, not an average one.

The 100 values reproduce the paper exactly:

| statistic | parquet | paper |
|---|---:|---:|
| mean, minutes | 139.42 | 139.44 (2.324 h) |
| median, minutes | 122 | 121.8 (2.03 h) |
| max, minutes | 501 | 501 (8.35 h) |
| min, minutes | 5 | 5 |

`human_time` is the mean, **8,365.2 seconds**. `human_time_statistic` is `mean`,
`human_time_method` is `other_calculation` (a statistic over recorded timings,
following the folder's ruling on source-published means), and
`human_time_evidence` is `task_timings` under the enum as revised on 2026-09-13:
these are recorded timings of these exact tasks by people of the stated skill
level, aggregated.

`human_attempts` is **200**: exactly two annotator timings enter each task's
figure, over 100 tasks. Third-annotator timings were recorded on an unreported
number of tasks and enter only when they are among the two shortest, in which
case they displace one of the first two rather than adding to the count. So the
literal number of quality-passing attempts is 200 plus an unreported remainder;
200 is what enters the statistic, which is the folder's rule for donor and
contributing counts.

`human_time_subset` is `successful`, on the coordinator's ruling, with the
fastest-two rule stated in each row's `notes`. Every included timing is a
submission that passed the expert quality gate. The enum has no value for "the
fastest two of the recorded attempts". The reviewer's framing is the better one
for the merge list: the rule is part of the *statistic* — a trimmed mean over two
or three valid timings — so what the spec lacks is a trimmed or order-statistic
value in `human_time_statistic`, not a value in `human_time_subset`.

**The price proxy is not usable as `human_cost_usd`.** Each task carries one, at
a mean of 46.93 CNY = $6.8560 at the paper's 1 CNY = 0.14609 USD rate, which
reproduces Table 3's human Cost/Task to four decimals and is one of the joins
tying the parquet and the paper to the same data. But `price_source` in the
parquet is `explicit_price` on only 20 of the 100 tasks and `estimated_price` on
the other 80, where three experts estimated the value and a consistency rule
combined them. Under Damon's cost-column ruling the figure is observed only and
never estimated, so `human_cost_basis` is `not_available` on all four rows. The
annotators were paid a daily salary plus bonuses, so no per-task payment exists
either.

## Performance

From §5.1.1 and Table 3. The human baseline is the **highest-scoring of the at
least two annotator submissions** for each task, run through the same code
verifiers as the models. So the comparison is like for like on scoring, and
asymmetric on attempt selection: the human score takes the best submission while
the human time takes the mean of the two shortest. That is the concrete
difference behind `different_attempt_selection`.

The second flag, `different_inputs_or_tools`, is the harness. Both sides get the
same instruction and the same input files, but the agent was confined to shell,
Python and file APIs with GUI computer use disabled, while the annotators used
office applications. That plain difference is what the flag records. The paper's
§5.4 does not show that the restriction hurt the agents — on a Kimi K2.6 backbone
CoAct-Coding-Only scores 14.41, CoAct-Hybrid 13.77 and CoAct-CUA-Only 0.78, so
adding GUI actions alongside coding *lowered* the score by 4% and the coding-only
route the benchmark used is the best of the three available. What §5.4 does show
is that the harness route moves agent scores across an 18x range, which is why
the difference is worth flagging at all.

| agent | score | ratio to human | SE of ratio, upper bound | SEs from the 0.5 guide | label |
|---|---:|---:|---:|---:|---|
| GLM-5.2 | 17.91 | 0.6445 | 0.1380 | +1.047 | below |
| Qwen3.7-Plus | 17.51 | 0.6301 | 0.1368 | +0.951 | cell not built |
| Kimi K2.6 | 17.00 | 0.6117 | 0.1352 | +0.827 | below |
| DeepSeek-V4-Pro | 14.48 | 0.5211 | 0.1266 | +0.166 | below |
| MiniMax M3 | 13.82 | 0.4973 | 0.1242 | -0.022 | below, close call |

Per-task scores are not released, so the per-task standard deviation is bounded
rather than measured: for a score on [0, 1] with mean mu the largest possible
variance is mu(1-mu). That is the widest standard error available, which is the
conservative direction for a rule that keeps rows within one standard error of
the guide. `research/omegause-officeval/performance_labels.py` computes the
table. MiniMax M3 misses the guide by 0.075 points of score out of 100 and is
kept as `below`; the exclusion rule asks whether the AI basically did the job,
and a model that half-completes half the tasks plainly did part of it.

Two corroborating facts from §5.3, which the score alone does not show. Humans
score above 50 on 21% of tasks and zero on 29%; the best model, GLM-5.2, scores
above 50 on 14%, and DeepSeek-V4-Pro and MiniMax M3 score zero on 50% and 51%.
And from Figure 8, score falls with human labor time for both sides, more
steeply for the models.

## Compute

The arithmetic is reproduced by
`research/omegause-officeval/compute_omegause.py`, whose output is retained at
`agent-work/derived/omegause-officeval/calculations.json`. The donor table it reads is
built by `research/omegause-officeval/build_donor_structures.py`.

### Prices in the run window

USD per million tokens, all in force across 2026-06-16 to 2026-07-29.

| model | input | cache read | output | in the shared table |
|---|---:|---:|---:|---|
| glm-5.2 | 1.40 | 0.26 | 4.40 | yes |
| kimi-k2.6 | 0.95 | 0.16 | 4.00 | yes |
| deepseek-v4-pro-preview | 1.32 | 0.044 | 3.96 | yes |
| minimax-m3 | 0.30 | 0.06 | 1.20 | no |

The first three match `research/cost/list-prices.csv` exactly, and Artificial
Analysis's payload independently corroborates the GLM, DeepSeek and MiniMax
triples. `minimax-m3` is not in that table; its row, and a row for `qwen3.7-plus`
for the record, go to the coordinator as a proposed addition rather than as an
edit from here.

**The rule for choosing between two published rates: the rate the provider's own
page headlines.** Two rows would otherwise look inconsistent. MiniMax's page
*displays* $0.30 / $0.06 / $1.20, with the "Permanent 50% off" applied before the
number a reader sees, so a paper quoting the token pricing quotes $0.30 and the
undiscounted $0.60 / $0.12 / $2.40 sheet is the scenario. DeepSeek's page
displays peak and off-peak as two labelled columns, so a paper quoting the token
pricing quotes the standard column at $1.32 / $0.044 / $3.96 and off-peak is the
scenario. One rule produces both answers. On DeepSeek the throughput evidence
points the same way and is stated as evidence in that row's section, not as a
preference.

All providers involved cache by default, so there is no live no-cache branch:
Z.ai's implicit caching "intelligently identifies repeated context content
without manual configuration"; Moonshot's is "automatically enabled for all model
requests"; MiniMax's automatic caching applies at 512 or more input tokens with
no cache-write fee (Artificial Analysis's payload lists a
`price_cache_write_per_mtok` of 0.375 for MiniMax M3, which MiniMax's own page
contradicts; AA is the outlier here); DeepSeek's disk cache is automatic. The
Z.ai and Moonshot statements are already retained in
`agent-work/sources/apex-agents/harness-and-provider-caching.md`; the MiniMax one came from
the page named in the manifest.

### Why the cost has to be inverted, and how

Billing units and FLOPs are different quantities, and the dataset says so. Here
the conversion is exact in one direction — the reported dollars are a linear
function of three token counts — and the problem is that three unknowns cannot be
recovered from one number without structure.

Write **F** for freshly processed input positions, **S** for positions served
from cache, **O** for output, and parameterise by

- **h** = S / (F + S), the served share of gross prompt positions;
- **rho** = O / F, output per freshly processed input position.

Then S = F·h/(1-h), O = rho·F, and

```
cost = [ F·P_in + F·(h/(1-h))·P_cached + rho·F·P_out ] / 1e6
F    = cost·1e6 / ( P_in + (h/(1-h))·P_cached + rho·P_out )
```

Under COLUMNS `params_tokens` the counted positions are fresh input plus cache
creation plus output, with cache reads removed, so **B = F·(1 + rho)** and
FLOPs = 2·active_parameters·B. `tokens_accounting` is
`input_cache_creation_output`. Cache creation is not separately counted by any of
these providers' counters — only Anthropic charges for it — so it sits inside F.

**`compute_flops` is therefore not independent of `ai_cost_usd` on any of these
rows**, the same dependency `DECISIONS.md` already flags for the Codex GDPval and
RLI rows. Each row's `notes` says so.

**Text only, as a stated assumption rather than a dismissal.** `tokens` is
defined as a text-token count, so an image share would have to come out of it.
The paper says task-critical detail is often carried by images and video rather
than by the instruction, and 87 of the 220 input files are images or video, and
MiniMax M3 is natively multimodal. But Appendix E's scaffold description and the
prompt template in E.4 describe no vision path at all: the agent manipulates
files through shell commands, Python libraries and LibreOffice, so images inside
a docx arrive as bytes it does not paste into a prompt. The central image share
is **zero**. If some share did enter, `tokens` would be overstated by that share
— a 10% image share would take GLM-5.2's `tokens` from 213,988 to 192,589 — while
`compute_flops` would be unchanged, since image positions cost the same
2·active_parameters and these providers bill them at the text rate that the
inversion already applied.

### Donor cache structures

h and rho are transferred from agentic tool-use runs of the same model endpoint
that publish a token decomposition. Two families, both already retained in this
folder for other studies.

**Epoch AI's SWE-bench Verified per-instance logs** give measured cache reads,
measured cache writes and measured agent working time, 484 instances per run, all
run between 2026-05-08 and 2026-06-25 — within weeks of the OmegaUse runs.

| donor run | reasoning effort | h | rho | billed per instance | working s per instance | billed per working second |
|---|---|---:|---:|---:|---:|---:|
| glm-5.2 | max | 0.9779 | 0.5470 | 89,586 | 937.6 | 95.5 |
| kimi-k2.6 | provider default | 0.9685 | 0.3340 | 59,600 | 549.3 | 108.5 |
| deepseek-v4-pro-preview | max | 0.8924 | 0.1001 | 212,505 | 924.5 | 229.9 |
| qwen3.7-max | provider default | 0.6671 | 0.1289 | 218,506 | 580.9 | 376.1 |
| qwen3.6-plus | provider default | 0.0000 | 0.0156 | 1,535,362 | 648.8 | 2,366.3 |

Three checks on these donors, all from `epoch-swebench-run-links.csv`. Epoch's
2,000,000-token harness limit binds on 0% of glm-5.2 instances, 0% of kimi-k2.6
and 1% of deepseek-v4-pro, so the folder's harness-cap ruling touches no donor
used here. `cache_reads_inside_input` and `reasoning_additional_to_output` are 0
on every run, which confirms the additive treatment directly rather than by
arithmetic. And **`cache_counters_reported` is 0 for `qwen3.6-plus` alone**, so
that run's h = 0 is a missing counter, not measured zero reuse — which is the
fact, rather than an inference, that disqualifies it as a donor.

Two of the four donors ran at `reasoning_effort = max` and two at provider
default, so the transferred rho for GLM-5.2 and DeepSeek-V4-Pro is an
upper-effort figure. That biases rho up and therefore the unit price up and B
down, which is the conservative direction.

**Artificial Analysis's long-horizon agent benchmarks** (gdpval, briefcase,
harveyLab, analystAgent) give gross prompt tokens and a `cacheableInput` figure
for glm-5.2, deepseek-v4-pro (the 0813 checkpoint) and minimax-m3. As
`agent-work/sources/apex-agents/harness-and-provider-caching.md` establishes, `cacheableInput`
is AA's own eligibility computation over the trajectory prefix, not a served
count, so it is an upper bound on h.

**Branches use complete reuse of the eligible prefix.** That is not an
assumption of convenience: Epoch *measures* the served share on three of these
providers at 0.89 to 0.98 of gross prompt positions, and AA's eligible share on
comparable workloads is 0.94 to 0.99, so achieved over eligible sits near one for
exactly this provider set. The 0.60 achieved-share floor in the APEX evidence
file is an inversion of Lumer et al.'s Table 2 on **Gemini 2.5 Pro and GPT-5.2**
and is carried here as a scenario, not a branch. It raises every affected row by
1.6x to 5.6x (GLM-5.2 3.46-3.70x, DeepSeek-V4-Pro 1.62-1.68x, MiniMax M3
5.47-5.60x), read out of `calculations.json`.

The central for each row is the **geometric mean of the lowest and highest
branch**, following the folder's rule for two defensible transfers that disagree,
with both ends reported. Kimi K2.6 has one donor and therefore no branch spread;
it carries an h sensitivity instead.

**One extension of that rule is worth settling for the folder.** `DECISIONS.md`
names two transfers, and three of these rows have three or four branches. Taking
the geometric mean of *all* branches instead of the two ends gives GLM-5.2
235,799 counted positions (+10%), DeepSeek-V4-Pro 230,492 (-7.5%) and MiniMax M3
786,516 (+0.3%). Every effect is well inside the branch spread, so the choice
does not matter numerically here, but it should be settled once rather than per
study. These rows use the two-ends reading because it is what the ruling says and
because it does not let the number of donor benchmarks a vendor happens to
publish move the central.

### Which billing model the reported cost uses

Appendix E says only that "the token cost is calculated according to the token
pricing of the corresponding LLM". The word "cache" does not appear anywhere in
the paper. Two readings are possible: the bill as the provider actually charges
it, with cache reads at the cache-hit rate, or gross prompt tokens priced at the
full input rate.

The throughput cross-check separates them. Rescale the Epoch donor's **billed
positions per second of agent working time** by OmegaUse's own wall clock per
task, and compare with the cost inversion. The two use different published
quantities — dollars on one side, hours on the other — and a different donor
statistic on each. Both columns below come out of `calculations.json`.

| agent | cost inversion, B | donor rate x OmegaUse wall clock | ratio | same check under gross pricing |
|---|---:|---:|---:|---:|
| GLM-5.2 | 213,988 | 179,210 | 0.84 | 2.20x off |
| Kimi K2.6 | 142,822 | 151,941 | 1.06 | 4.65x off |
| DeepSeek-V4-Pro | 249,179 | 152,262 | 0.61 | 6.11x off |
| Qwen3.7-Plus (cell not built) | 190,287 | 261,337 | 1.37 | 8.83x off |

Under the cache-discounted reading every ratio is inside a factor of 1.7. Under
the gross-token reading the same comparison is off by **2.2x to 8.8x**, with the
implied billed positions falling far below what the donor's own measured
throughput can produce in the reported wall clock. GLM-5.2 at 2.2x is the weakest
of the four and should not be presented as one of the strong ones; Kimi at 4.7x
and DeepSeek at 6.1x carry the conclusion. The cache-discounted reading is
central and the other is a scenario, quantified per row below.

Two limits on the check, both pointing the same way.

- **The wall clock is a soft quantity.** With 10 task environments sharing at
  most two inference threads per model, queueing inflates it, so the donor-rate
  column should read high if anything. Two of the three ratios sit at or below
  one, which is the direction that would follow if the cost inversion were
  slightly generous — another reason not to push the central higher.
- **The check is structure-dependent.** The donor rate embeds the donor's own h:
  95.5 positions per second for glm-5.2 at h = 0.978 against 376.1 for
  qwen3.7-max at h = 0.667. So the ratio tests the inversion most directly when
  the transferred structure is the donor's own, and is a calibration check on a
  mixed central rather than a clean test of a single branch where it is not.
  Against the Epoch branch alone, GLM-5.2 reads 1.20 and DeepSeek-V4-Pro 0.47.

A second, independent sanity check: the implied output tokens divided by the
reported wall clock give decode rates of 42 (GLM-5.2), 26 (Kimi K2.6), 109
(DeepSeek-V4-Pro) and 29 (MiniMax M3) tokens per second. All four are physically
plausible for an agent loop that spends much of its wall clock on prefill and
tool execution, and MiniMax M3's 29 against its median decode speed of 90.85
tokens per second — `medianCanonicalAnswerOutputSpeed` for `minimax-m3` in
`agent-work/sources/scouting/legal-finance/artificialanalysis-models-merged.json` — is a 32%
duty cycle.

### Compute scenarios

Every row's parameter term omits cached-context attention, as the dataset's 2N
convention does; `research/attention-correction.md` carries the term in
`compute_flops`. `research/omegause-officeval/attention_scenarios.py`
quantifies it with the 4·L·d_model·N_context recipe, reconstructing
context from the inverted structure: with a prefix growing linearly to its final
length, gross prompt positions G = n·N_final/2 and F = N_final, so the implied
call count is n = 2/(1-h) and the call-averaged context is N_final/2.

**The term is much smaller here than in earlier rows, because two of the four
models bound the number of key positions per query.** GLM-5.2's config sets
`index_topk` to 2,048, with `index_skip_topk_offset` 3, read here as the first
three of its 78 layers attending densely; MiniMax M3's MSA selects 16 blocks of
128 on 57 of its 60 layers; Kimi K2.6 has no sparse-attention block and runs full
MLA attention.

| agent | L | d_model | implied calls | mean context | full attention, x recorded | selective attention, x recorded |
|---|---:|---:|---:|---:|---:|---:|
| GLM-5.2 | 78 | 6,144 | 56.0 | 67,316 | 1.61 | 0.109 |
| Kimi K2.6 | 61 | 7,168 | 63.5 | 53,533 | 1.46 | — |
| DeepSeek-V4-Pro | 61 | 7,168 | 25.6 | 88,603 | 1.58 | 0.037 |
| MiniMax M3 | 60 | 6,144 | 81.7 | 273,611 | 8.77 | 0.501 |

GLM-5.2's and MiniMax M3's rows sit on their measured configs, so 0.109x and
0.50x are the applicable figures for them; Kimi K2.6's 1.46x is applicable as
full attention. DeepSeek-V4-Pro publishes no config and gets both limbs on a
bracketing architecture. The recipe also ignores that three of the four use
multi-head latent attention, whose cached state is a 512-dimensional latent
rather than d_model, so even the full-attention limb overstates.

## Model records

Three model IDs already exist in the Codex registry at
`../AI Compute vs Human Time/dataset/models.csv` and are reused unchanged, with
their assumptions: `glm-5.2` (40B active, 8.0e10 per token), `kimi-k2.6` (32B,
6.4e10) and `deepseek-v4-pro-preview` (49B, 9.8e10). Damon's priors ruling flips
`glm-5.2`'s basis from `estimated` to `reported` without changing the value, and
that is applied to the unified registry at merge.

On DeepSeek's identity: the Codex record is the April 2026 preview, and the
August 2026 general release post-dates the OmegaUse run window, so the preview is
the endpoint that existed when the runs happened. Artificial Analysis lists the
August 0813 checkpoint at the same 49B active count, so the coefficient does not
turn on the choice.

**minimax-m3** is the one new ID. MiniMax released M3 on 2026-06-01 and its model
card states "~428B parameters and ~23B activated parameters", so 23B is
`reported`. Counting the published config independently: 60 layers at hidden size
6,144, 64 query heads of head dimension 128 with 4 key-value heads, three dense
layers at intermediate size 12,288 and 57 MoE layers activating 4 of 128 routed
experts plus one shared expert at intermediate size 3,072. Attention projections
are 1.070e8 per layer (6.417e9 over 60 layers), dense FFN 2.265e8 per layer
(6.795e8 over three), MoE FFN 2.839e8 per layer including the router (1.618e10
over 57). That is **23.28e9** excluding the embedding table and the output head,
or 24.51e9 with the output head — either way the developer's ~23B stands, and the
registry value is 23e9 with `flops_per_token` 4.6e10. Artificial Analysis's
payload also lists 23. **One folder document disagrees**: the reference table in
`research/model-priors/google-xai-others.md` lists MiniMax-M3 at 22B active,
"disclosed". The 4.5% difference changes nothing here, but the two should be
reconciled and the row's 23B is the better-sourced of the two; that report is
another study's file and is not edited from here.

**qwen3.7-plus is not minted.** The cell it would have served is not built, and
no other row needs the ID. For the record, had it been minted the prior would
have been 17B active, grade C, range 10 to 30B, carrying the Plus-tier count from
Qwen3.5-397B-A17B — the open pair behind the Codex registry's 17B for
`qwen3.6-plus` — and corroborated by the 6.25x price step below qwen3.7-max at
100B. Alibaba skipped the Qwen3.7 generation in its open-weight line and
discloses no size.

## The Qwen3.7-Plus cell

Qwen3.7-Plus scored 17.51, 0.63 of the human baseline, on $0.2152 and 0.193 hours
per task, and it is the best-value agent on the board by both weighted metrics.
Its performance evidence is exactly as good as the four rows'. **It is not built
as a row** (coordinator ruling, 2026-09-13), because three compute levers compound
and nothing in the source pins any of them. Its arithmetic is kept in
`calculations.json` so the disposition is reproducible.

**The price mode, 2.0x to 3.4x.** Alibaba's Model Studio sheet prices this alias
in two modes, and the premium sits on the input side: non-thinking 0-256K at
$0.40 in and $1.60 out, thinking 0-256K at **$1.60 in** and $1.60 out. Because
the output price is identical, the whole effect lands on the input and cached
terms, which is where this cell's unit price is concentrated.

| reading | central B | FLOPs |
|---|---:|---:|
| non-thinking, implicit cache $0.08 | 190,287 | 6.47e15 |
| thinking, implicit cache at 20% of $1.60 = $0.32 | 55,296 | 1.88e15 |
| thinking, cache rate held at $0.08 | 94,988 | 3.23e15 |
| non-thinking, explicit cache $0.04 | 250,863 | 8.53e15 |

The evidence does not settle it. Epoch ran the sibling qwen3.7-max at provider
default and got 9.48M reasoning tokens out of 12.08M output, so Alibaba's default
on that line is a thinking default — and this cell's rho is transferred from
precisely that thinking run, which makes a thinking structure priced at a
non-thinking rate internally inconsistent. Against that, $0.2152 per task is 7x
below GLM-5.2's on a wall clock only 2.7x shorter, which sits more comfortably
with the $0.40 rate.

**The cache branch.** No same-model donor exists — Qwen3.7 was never released
open-weight and neither Epoch nor Artificial Analysis ran the Plus alias — so one
of the two branches (h = 0.95) is constructed rather than donated. Epoch's other
Alibaba run, qwen3.6-plus, cannot supply one either: its `cache_counters_reported`
is 0.

**The parameter prior**, 17B with a 10-30B range, moves dependent FLOPs 0.59x to
1.76x.

**And the throughput cross-check cannot arbitrate**, because it is
structure-dependent in the way set out above and this cell's central is a
geometric mean of the donor's structure and a constructed one. Its 1.37 ratio is
not a test of that central.

Had the cell been kept, the minimum would have been the geometric mean of the two
price readings, 3.49e15, a stated band of roughly 1.1e15 to 1.9e16 across the
three levers, and no throughput ratio in its evidence.

One further unresolved point, recorded because it would matter if the cell is
ever revisited: the price sheet used is Alibaba's **Singapore** region, and a
Baidu team would plausibly have billed through the China-region Bailian console,
whose Plus-tier rates differ.

## agen-omegause-officeval-glm52

GLM-5.2 through the Z.ai API. Reported $1.4823 and 0.521 hours per task, score
17.91.

Four branch structures, all of the same endpoint:

| structure | h | rho | $/M fresh | B | FLOPs |
|---|---:|---:|---:|---:|---:|
| Epoch SWE-bench Verified, measured | 0.9779 | 0.5470 | 15.30 | 149,892 | 1.199e16 |
| AA harveyLab, complete reuse | 0.9532 | 0.4480 | 8.66 | 247,776 | 1.982e16 |
| AA briefcase, complete reuse | 0.9472 | 0.6015 | 8.62 | 272,477 | 2.181e16 |
| AA gdpval, complete reuse | 0.9359 | 0.7613 | 8.55 | 305,491 | 2.444e16 |

Central: geometric mean of 149,892 and 305,491 = **213,988 counted positions**,
FLOPs = 8.0e10 x 213,988 = **1.7119e16**. At the branch-mean rho of 0.5894 the
central corresponds to h = 0.964, $11.0100 per million fresh positions, 134,632
fresh input positions, 79,355 output and 3.63e6 cache reads, from about 56 calls
at a mean context of 67,316.

Scenarios: h = 0.85 gives 3.44e16 and h = 0.99 gives 6.38e15; the 0.60
achieved-share floor on the AA branches gives 5.93e16 to 6.34e16; the paper
pricing gross prompt tokens with no cache discount gives 6.51e15; the all-branch
geometric mean gives 1.89e16. Cached-context attention adds 0.109x on the model's
own sparse configuration.

Throughput cross-check: 95.5 billed positions per second of Epoch working time x
1,876 seconds = 179,210, which is 0.84 of the central and 1.20 of the Epoch
branch it is drawn from.

## agen-omegause-officeval-kimik26

Kimi K2.6 through the Moonshot API. Reported $0.7719 and 0.389 hours per task,
score 17.00.

One donor structure, Epoch's SWE-bench Verified run of the same endpoint, with
measured cache reads: h = 0.9685, rho = 0.3340. At $0.95 input, $0.16 cache read
and $4.00 output, the unit price is **$7.2096** per million fresh positions,
giving 107,066 fresh, 35,757 output, 3.29e6 cache reads and **142,822 counted
positions**. FLOPs = 6.4e10 x 142,822 = **9.1406e15**.

With a single donor there is no branch spread, so this row carries an h
sensitivity instead: h = 0.85 gives 2.06e16 and h = 0.99 gives 3.64e15. Pricing
without a cache discount gives 2.09e15. Kimi K2.6's config has no
sparse-attention block, so its cached-context attention term is the
full-attention 1.46x.

Throughput cross-check: 108.5 positions per second x 1,400 seconds = 151,941,
which is 1.06 of the central. This is the closest agreement of the three and,
because the central here *is* the donor's own structure, it is also the cleanest
test of the inversion anywhere in this note.

## agen-omegause-officeval-dsv4pro

DeepSeek-V4-Pro through the DeepSeek API. Reported $0.6111 and 0.184 hours per
task, score 14.48.

Three branch structures. The Epoch donor is the April preview endpoint the run
window used; the two AA donors are the August 0813 checkpoint at the same active
count.

| structure | h | rho | $/M fresh | B | FLOPs |
|---|---:|---:|---:|---:|---:|
| AA briefcase, complete reuse | 0.9714 | 0.4692 | 3.113 | 192,236 | 1.884e16 |
| AA gdpval, complete reuse | 0.9652 | 0.6492 | 4.126 | 197,217 | 1.933e16 |
| Epoch SWE-bench Verified, measured | 0.8924 | 0.1001 | 2.081 | 322,990 | 3.165e16 |

Central: geometric mean of 192,236 and 322,990 = **249,179 counted positions**,
FLOPs = 9.8e10 x 249,179 = **2.4420e16**, at $3.4485 per million fresh positions.

The price scenario is the largest here. DeepSeek's **off-peak rate is half the
listed one** (0.66 / 0.022 / 1.98), and peak is only 01:00-04:00 and 06:00-10:00
UTC on weekdays, so about 79% of wall-clock hours are off-peak and a figure taken
from a billing console would be dominated by it. The listed rate is central
anyway, for two reasons. The headline-rate principle above picks the standard
column, which is what a paper quoting "the token pricing of the corresponding
LLM" would quote. And the throughput evidence points the same way: this row
already reads 0.61 against its donor rate, the most generous of the three, and
off-peak would take it to 0.31 — a 3.3x disagreement, worse than anything else in
this note. Off-peak gives 4.88e16 and is the scenario.

Other scenarios: h = 0.85 gives 2.39e16 and h = 0.99 gives 1.20e16; the 0.60
achieved-share floor gives 3.96e16 to 4.10e16; no cache discount gives 2.44e15;
the all-branch geometric mean gives 2.26e16.

## agen-omegause-officeval-minimaxm3

MiniMax M3 through the MiniMax API. Reported $1.7572 and 2.275 hours per task,
score 13.82. The slowest and most expensive agent on the board, and the only one
whose mean runtime is a large fraction of the harness's 14,400-second cap.

Four branch structures, all Artificial Analysis, all of the same model, all at
complete reuse of the eligible prefix. No Epoch run of any MiniMax model exists,
so this row has no throughput cross-check.

| structure | h | rho | $/M fresh | B | FLOPs |
|---|---:|---:|---:|---:|---:|
| AA briefcase, complete reuse | 0.9832 | 0.4275 | 4.325 | 579,588 | 2.666e16 |
| AA gdpval, complete reuse | 0.9771 | 0.4799 | 3.424 | 756,204 | 3.479e16 |
| AA harveyLab, complete reuse | 0.9738 | 0.4211 | 2.740 | 823,470 | 3.788e16 |
| AA analystAgent, complete reuse | 0.9625 | 0.4017 | 2.322 | 1,060,288 | 4.877e16 |

Central: geometric mean of 579,588 and 1,060,288 = **783,920 counted positions**,
FLOPs = 4.6e10 x 783,920 = **3.6060e16**, at $3.2111 per million fresh positions.
At the branch-mean rho of 0.4325 that is h = 0.9755, 547,222 fresh positions,
236,698 output and 2.18e7 cache reads from about 82 calls at a mean context of
273,611 — long, but M3 is a million-token-context model and the row's 2.275-hour
runtime is consistent with it.

Scenarios: h = 0.85 gives 1.01e17 and h = 0.99 gives 1.69e16; the 0.60
achieved-share floor gives 1.97e17 to 2.02e17; no cache discount gives 1.34e16;
the all-branch geometric mean gives 3.62e16.

Two price-sheet scenarios are specific to this row. MiniMax's live page reaches
$0.30 / $0.06 / $1.20 by applying a "Permanent 50% off" to a $0.60 / $0.12 /
$2.40 sheet and publishes no start date for the discount; if the undiscounted
sheet was in force the central halves to 1.80e16. And **the same page doubles
every rate above 512,000 input tokens**, a threshold this row's own implied final
context of 547,222 crosses. Under the linear-growth context model that puts 6.4%
of calls and 12.5% of served-cache volume in the upper tier, lifting the unit
price about 11% and taking the central to 3.25e16, or 0.90x. It is a scenario
rather than the central because the context reconstruction is itself a model.

The 14,400-second cap is a real limitation on this row and on no other: a mean of
8,190 seconds against a 14,400-second cap, on a task-time distribution the paper
shows to be right-skewed, means an unreported share of tasks was cut off. The row
measures what M3 produced under that cap, and the score it is compared on is the
score of the truncated output, so the two sides of the row remain consistent. It
stays in `notes` rather than in `comparison_issues`, on the coordinator's ruling
and the reviewer's reasoning: `different_assessment` would tell a reader the
scoring differed, which it did not, and the cap applied equally to all five
agents with only its bindingness differing.

## Dispositions

`candidates/omegause-officeval/dispositions.csv` records all fourteen source
cells: the four rows above and **ten that are not rows**. The Qwen3.7-Plus cell
has its own section in this note. The other nine are the three CoAct variants
with a Kimi K2.6 backbone (§5.4 publishes scores with no cost, token count or
runtime, so there is no compute evidence of any kind), the same three variants'
OSWorld results in Figure 9b (a different benchmark with no human baseline here,
recorded so that every AI result the paper publishes is accounted for), the human
labor-time bucket splits in Figure 8 and the domain, file-type and
operation-intent splits in Figures 10 to 12 (all released only as heat maps), the
time-weighted and price-weighted scores (reweightings of the same 100 tasks, not
separate comparisons), the human baseline itself, and the task price proxy as a
human cost.

**The bucket splits are the most valuable thing missing.** Figure 8 shows score
falling with human labor time for every agent, and this dataset's whole point is
the relation between human time and AI compute. Four rows split into four
human-time buckets would be sixteen rows spanning an order of magnitude of human
time on one harness and one scoring rule. It needs per-task scores, which Baidu
has not released; the GitHub repository ships the verifiers and the evaluation
harness but no model outputs or result files.

## Reproducing

From the folder root, in order. Each script takes explicit input and output paths
and needs nothing beyond the Python standard library, except the first and the
last, which need `pyarrow`. Every step writes into `/tmp` and each later step
reads the step before it, so the chain runs end to end without touching the
retained evidence; the committed copies of the two intermediate files are
byte-identical to what it produces.

```
python3 -c "
import pyarrow.parquet as pq, csv
df = pq.read_table('agent-work/sources/omegause-officeval/omegause-officeval-tasks.parquet').to_pandas()
w = csv.writer(open('/tmp/omegause-human-labor-time.csv','w',newline=''))
w.writerow(['id','domain','operation_intent','human_labor_time_min','task_price_proxy_cny','price_source','n_origin_files'])
[w.writerow([r['id'],r['domain'],r['operation_intent'],int(r['human_labor_time']),int(r['task_price_proxy']),r['price_source'],len(r['origin_files'])]) for _,r in df.iterrows()]
"

python3 research/omegause-officeval/build_donor_structures.py \
  --epoch agent-work/sources/epoch-swebench-bins/epoch-swebench-perinstance.csv \
  --aa agent-work/sources/scouting/legal-finance/artificialanalysis-per-task-tokens.csv \
  --out /tmp/donor-structures.csv

python3 research/omegause-officeval/compute_omegause.py \
  --donors /tmp/donor-structures.csv \
  --prices agent-work/sources/omegause-officeval/omegause-prices-run-window.csv \
  --table3 agent-work/sources/omegause-officeval/omegause-table3.csv \
  --tasks /tmp/omegause-human-labor-time.csv \
  --out /tmp/calculations.json

python3 research/omegause-officeval/attention_scenarios.py \
  --calculations /tmp/calculations.json \
  --architectures agent-work/sources/omegause-officeval/architectures.csv \
  --out /tmp/attention-scenarios.json

python3 research/omegause-officeval/performance_labels.py \
  --table3 agent-work/sources/omegause-officeval/omegause-table3.csv \
  --out /tmp/performance-labels.csv

python3 research/omegause-officeval/emit_rows.py \
  --calculations /tmp/calculations.json \
  --attention /tmp/attention-scenarios.json \
  --table3 agent-work/sources/omegause-officeval/omegause-table3.csv \
  --outdir /tmp/omegause-rows

python3 research/omegause-officeval/language_check.py \
  --parquet agent-work/sources/omegause-officeval/omegause-officeval-tasks.parquet \
  --zh agent-work/sources/omegause-officeval/omegause-instructions-zh.json \
  --out /tmp/language-check.csv
```

## Open questions for the coordinator

1. **List-price rows for the two models not in the shared table**, proposed
   rather than written from here. `minimax-m3`: provider `minimax`, start
   2026-06-01, 0.30 / 0.06 / blank / 1.20, with a `long_context_rule` naming the
   above-512K tier at double and the "Permanent 50% off" the headline rate
   already includes. `qwen3.7-plus` for the record: 0.40 / 0.08 / 0.50 / 1.60,
   `reasoning_billed_as` filled — that field is what would have caught the
   two-mode pricing in the first place — and a `long_context_rule` naming both
   cached rates (implicit 0.2x with no creation charge, explicit 0.1x with
   creation at 1.25x) and the 256K tier. Alibaba's page says implicit caching
   "requires no extra configuration and cannot be disabled", which is stronger
   than the default-on ruling needs; the shared table should carry both Qwen
   cached rates rather than only the explicit one, and it is worth checking at
   merge whether any existing Qwen row was priced at the explicit rate on a
   harness that could not have set `cache_control`.
2. **`human_time_statistic` has no value for a trimmed or order-statistic mean.**
   These rows use `mean` plus `human_time_subset = successful`, which is the
   closest the frozen enum gets to "the mean of the two shortest of two or three
   valid timings", with the rule stated in `notes`. Raise as a statistic gap, not
   a subset gap.
3. **`comparison_issues` has no value for a run-time or budget cap**, which is
   why the MiniMax M3 row's 14,400-second timeout sits in `notes`. Worth adding
   to the same merge list.
4. **MiniMax M3 at 22B versus 23B.** This folder's priors report lists 22B
   "disclosed"; the model card, the config count and Artificial Analysis all give
   23B. The row uses 23B. The report is another study's file and was not edited
   from here.
5. **The geometric-mean rule at more than two branches.** Settled here as the
   geometric mean of the two ends, for the reasons in the donor section, but the
   ruling names two transfers and this is an extension. Worth one line in
   `DECISIONS.md` either way.
