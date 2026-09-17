# METR RE-Bench — evidence and calculations

*Created 2026-09-13 17:48.*
*Last revised 2026-09-13 19:05.*

## TL;DR

Eight rows from METR's RE-Bench (arXiv 2411.15114v2), covering four agent configurations
at total time budgets of 2, 8, and 32 hours per environment. The human side needs no
estimation: 71 attempts by 61 ML experts, every one capped at 8 hours, with score-over-time
curves that give the 2-hour and 32-hour points as well. The compute side is built from two
figures. Figure 11 publishes each configuration's dollar cost budget; Figure 12 publishes its
median completion-token rate and the median share of run time spent on API calls, whose
product times the run limit is output tokens per run. Input is then what the run cost buys,
so the input-to-output split is measured per configuration rather than transferred — it runs
from 3.8 for o1-preview in AIDE to 133 for Claude 3.5 Sonnet in Modular, and the paper's
pooled 58 describes none of them. Environment-level rows are not defensible on compute and
are recorded as dispositions. At 2 hours the agents beat the humans by 1.3 to 3.7 times; at
8 hours the best agent reaches 68% of the human score; at 32 hours 51 to 55%.

Revision 1 replaced the pooled-ratio inversion with the Figure 12 route on the independent
review's finding, relabeled the two `far_above` rows `above` on the coordinator's ruling,
and replaced four unmeasured claims with measurements. `candidates/rebench/REVISION.md`
lists the changes and the old and new `compute_flops`.

## Source

Hjalmar Wijk et al., *RE-Bench: Evaluating frontier AI R&D capabilities of language model
agents against human experts*, METR, arXiv 2411.15114, v1 submitted 2024-11-22, v2
2025-05-27. Retained at `agent-work/sources/rebench/rebench-2411.15114v2.pdf`; verbatim
passages behind every claim below are in `agent-work/sources/rebench/rebench-key-passages.md`.

Seven hand-built ML research engineering environments. Each gives the worker a weak
starting solution, a VM with 0 to 6 H100s, and a scoring function they may run at will.
The raw score is linearly rescaled so the starting solution is 0 and the task author's
strong reference solution is 1, with sub-starting scores floored at 0. Humans and agents
work under the same conditions on the same environments, scored by the same code.

Four agent configurations were evaluated: `claude-3-5-sonnet-20241022` and
`claude-3-5-sonnet-20240620` in METR's Modular scaffold, and `claude-3-5-sonnet-20241022`
and `o1-preview` in AIDE. All three model IDs already exist in the Codex registry at
`../AI Compute vs Human Time/dataset/models.csv` with 100B, 100B, and 50B active
parameters respectively; none is touched by the accepted-priors ruling in
`research/model-priors/accepted-priors.csv`, so this batch adds no model records and
`candidates/rebench/models.csv` carries only its header.

The paper's footnote gives the environments as `github.com/METR/ai-rd-tasks`; that
repository was renamed and now redirects to `github.com/METR/RE-Bench`, which is what the
rows cite. A reader following the paper lands in the same place.

## What the paper publishes, and what it does not

Published in words: the human baseline design and its 8-hour cap, Table 5's per-source
human means, and one pooled compute sentence — 29M input tokens, 499K output tokens, and
about $123 per 8-hour run, averaged over the agent runs, with no prompt caching used.

Published only as plots, but per configuration, which is what the rows need. Figures 6, 7,
and 8 carry score@k; Figure 2 and Figure 11 carry best observed score@k against the total
time budget and against the cost budget in USD; **Figure 12** carries the median completion
tokens per second during API time and the median share of run time spent waiting on
completion requests. Per-environment scores are published too, in Appendices G (per-task
score histograms), H (per-task score@k at both run limits), and I (per-task human score over
time).

Not published at all, two years after the paper said it was coming: the anonymized
per-attempt human data and the agent trajectories. Checked on 2026-09-13,
`github.com/METR/RE-Bench` holds only the environments, build steps, and password-protected
official solutions; `github.com/METR/eval-analysis-public` holds only the Time Horizon 1.0
and 1.1 reports; `transcripts.metr.org` serves a Vivaria front end whose API is not
reachable. There is no public per-run token counter, and per the no-outreach ruling in
`DECISIONS.md` none was sought.

## Grain: why these rows and not environment-level rows

Damon's question for this source was whether environment-level rows survive the
`transferred_workload` rules. They do not, and the reason is compute alone.

**No per-environment token or cost figure exists anywhere in the paper**, and the suite
figures cannot be pushed onto one environment. Runs are bounded by wall clock, not tokens,
so tokens per run are set by how much of the budget the agent spends generating rather than
waiting. Figure 12's API-time-share violins span almost the whole 0-to-1 range *within a
single configuration*, which is direct evidence of that spread; Appendix A.2.2 names the
cause, stating that agents spend most of a run waiting for VM commands and that the time
spent waiting on API calls "differs greatly across different environments"; and Table 3
gives the mechanism, with the time to train and score a reference solution running from 40
seconds in Optimize a Kernel to 2.5 hours in Fix Embedding. A suite average pushed onto one
environment would be wrong by a large factor, in a direction correlated with the
feedback-loop length the row is partly measuring.

Two secondary points. Per-environment run counts differ — 3 to 5 8-hour attempts per
environment per agent for the score-over-time analysis, unstated counts for the shorter runs
— so the suite average is not an equal-weight average across the seven and cannot be undone
into one. And the performance side of an environment-level row *would* be buildable from
Appendices G, H, and I; it is the compute side that stops it. (Revision 1: the first
submission said per-environment scores exist only as Figure 9. That was wrong, and it was the
weaker of the two reasons.)

What survives is the suite grain, which is what Figures 2, 6, 7, 8, 11, and 12 all report:
the mean normalized score across the seven environments, for one agent configuration, at one
total time budget. The work unit is "one RE-Bench environment worked for N hours", and the
score is the mean over which environment it is. That is a source-defined collection and its
average is not a transfer under COLUMNS.md.

The remaining choice was between the 8h@1 grain, where the pooled token sentence sits, and
the total-time-budget grain, where the paper's headline comparisons and all the
per-configuration evidence sit. The rows use the second. Figure 12 does give output tokens
for an 8-hour run, but Figure 11 plots cost only at each configuration's *best* allocation,
so an 8h@1 row has no route to input tokens and would have to transfer the pooled 29M/499K
across scaffolds whose measured ratios run from 3.8 to 133. The 8h@1 cells are recorded in
`candidates/rebench/dispositions.csv` with their scores (0.096, 0.139, 0.167, and 0.368).

The three budgets built are the three the abstract names. Figure 11 also plots 16-hour and
64-hour human budgets with matching agent points; those are buildable and are listed as
dispositions rather than built, because the marginal information is small and they compound
the non-independence noted below.

## Human time

Every human attempt was capped at 8 hours: "For practical reasons, we limited all expert
baselines to 8 hours" (Section 3.4), repeated in Appendix A.1. Breaks were excluded —
"Participants were allowed to take breaks by reporting their start and stop times" — so the
8 hours is active time, which is what `human_time` means. The paper adds that it "did not
carefully monitor whether people spent exactly 8 hours in all cases", checking commit logs
instead; no per-attempt duration is published.

The work unit therefore fixes the duration rather than sampling it, which is
`human_time_evidence = defined_duration` under the 2026-09-13 revision of COLUMNS.md, with
`human_time_subset` and `human_attempts` both `not_applicable`. The 71 attempts are the
performance sample, not a timing sample, and are stated in `performance_evidence` instead.
This matches the treatment `DECISIONS.md` gives the ALE-Bench contest window and the Codex
OTIS rows. `human_time_method = work_rate` follows this folder's two ARTEMIS
defined-duration rows, which use the same field combination; the column is due to be dropped
at the unified build.

The three budgets:

| Budget | Human work unit | human_time (s) |
|---|---|---|
| 2 hours | one expert, first 2 hours of an 8-hour attempt | 7200 |
| 8 hours | one expert, one full 8-hour attempt | 28800 |
| 32 hours | four experts, four full 8-hour attempts, best score taken | 115200 |

The 32-hour figure sums four people's active time, as COLUMNS.md requires for a baseline
combining several people. The 2-hour figure is a truncation of an 8-hour attempt rather than
a separately run 2-hour attempt; that is a real difference in the assessment protocol and
every 2-hour row carries `different_assessment` and says so in `notes`. It cuts both ways.
The experts were told to be "greedy," optimizing their score within the first 2 hours, which
makes the checkpoint close to what a 2-hour-budgeted expert would produce; but they knew
they had 8 hours, which an agent given 2 did not.

## Human performance

Table 5 gives the published means over the 71 attempts: 0.64 overall, 0.48 for the 45 runs
by applicants to METR's ML research scientist or engineer hiring process, 0.98 for the 17
from METR staff professional networks, and 0.83 for the 9 from graduate student outreach.
82% of attempts scored above zero and 24% matched or beat the reference solution.

Figure 11's human curve gives the same quantity at each budget, from the bootstrap that
generated the figure, and Figure 2 is a second reading of it on a time axis:

| Budget | Figure 11 | Figure 2 | 95% CI (Figure 11) | Implied SE |
|---|---|---|---|---|
| 2 hours | 0.077 | 0.073 | — | — |
| 8 hours | 0.657 | 0.657 | 0.533 to 0.781 | 0.063 |
| 32 hours | 1.110 | 1.139 | 0.967 to 1.193 | 0.058 |

The 8-hour value and Table 5's 0.64 are the same quantity estimated two ways and differ by
3%, which changes no label. The rows use the Figure 11 values for the ratio arithmetic,
because they sit on the same axis and the same bootstrap as the agent values, and quote 0.64
in `performance_evidence` as the paper's published figure.

Two spreads belong on the record rather than in a cell. At 32 hours Figure 2 reads 1.139
against Figure 11's 1.110; on Figure 2's value `agen-rebench-32h-sonnet35new-modular` sits at
0.502 rather than 0.515, still `below` and still inside the close-call band, but on the line
under a defensible alternative read. At 2 hours the three published readings span 0.073
(Figure 2), 0.077 (Figure 11), and about 0.095 (Figure 5, the reviewer's read, which I have
not re-digitized): Figure 5 is built from log-linear interpolations between score-log entries
(Section 4.1), which anticipate later gains and read high at intermediate times, so Figure 11
is the right source for a budget-axis value. Across that whole span the four 2-hour rows stay
`above`, with ratios from 1.06 to 3.9.

Human skill is `expert`: METR's professional-network baseliners have more than five years
of relevant experience or recent positions at Google DeepMind, Google, Anthropic, OpenAI,
FAR Labs, or Redwood Research; the hiring applicants passed a CV and CodeSignal screen, an
interview, and a task; the students are in ML PhD programs at Berkeley, CMU, Stanford, or
MIT.

## Compute

### Digitizing the figures

`research/rebench/digitize_figures.py` reads the PDF, pulls the figure bitmaps out at native
resolution, and writes `agent-work/derived/rebench/figure-data.csv`: 115 points covering Figure 2's
markers, Figure 6's twelve bars with their whiskers, Figure 7's and Figure 8's score@k
markers, Figure 11's cost-versus-score markers, Figure 12's eight violin medians with their
whiskers, and the Figure 7 and 8 confidence bands at the four 32-hour allocations. Axis
calibration is pinned to the gridline pixel rows of the retained bitmaps and is verified at
run time — each calibration row must still be mostly gridline grey, and the value-versus-pixel
fit must be linear to better than 1.5 px. Markers are found by eroding the series color mask
so the thin connecting line drops out; violin medians and whisker caps by their vertical
extent above the whisker line; confidence bands by walking out from the series line until the
column turns white or enters another series' own band.

The digitization is checkable four ways and passes all four.

- **Figures 6, 7, and 8 agree.** At 8 total hours Figure 6's bars and the corresponding
  score@k markers differ by at most 0.005 on a 0-to-1.4 axis, for all twelve cells.
- **Figure 11's human curve reproduces a number stated in words.** Its five human markers
  sit at $468, $1,856, $3,721, $7,443, and $14,896, which is 0.25, 1, 2, 4, and 8 times
  $1,862. The paper states it paid human experts "approximately $1,855" per attempt on
  average. The log cost axis is therefore read to 0.4%.
- **Figure 2 reproduces Figure 11 on a different axis.** Every human and agent point the rows
  use agrees within 0.005 except the two noted above: the 32-hour human value and the
  o1-preview 2h@16 score.
- **Figure 11's agent scores reproduce Figures 7 and 8.** Nineteen of the twenty agent
  markers match a score@k value to within 0.007. The twentieth, o1-preview at 2h@16, reads
  0.580 on Figure 11 and 0.586 on Figure 2 against 0.606 on Figure 8. Figures 2 and 11 are
  one plot on two axes and so are one reading, not two; the rows take Figure 8, the dedicated
  score@k figure, for consistency with every other score, and the alternative moves that row's
  ratio from 0.546 to 0.528, changing nothing.

### Per-run costs

Matching each Figure 11 marker's score to the score@k tables of Figures 7 and 8 fixes its
k. Cost divided by k is that configuration's cost for one run at its own run limit, and
the four or five markers per configuration agree closely, which is the check that the k
assignment is right:

| Configuration | Run limit | Cost per run (USD) | Markers | Spread |
|---|---|---|---|---|
| claude-3-5-sonnet-20240620 / Modular | 30 min | 7.64 | 4 | 0.7% |
| claude-3-5-sonnet-20241022 / Modular | 30 min | 6.60 | 5 | 1.8% |
| claude-3-5-sonnet-20241022 / AIDE | 2 h | 10.88 | 4 | 0.8% |
| o1-preview / AIDE | 2 h | 29.37 | 4 | 0.9% |
| human expert | 8 h | 1862 | 5 | 0.8% |

The budget cost is k times the per-run cost, with k set by the allocation the paper says is
best for that scaffold: 30-minute runs for Modular, 2-hour runs for AIDE at budgets of 2
hours or more (Section 4.2 and the Figure 2 caption). The full k table is in
`research/rebench/make_rows.py`.

One structural fact falls out and corroborates the scaffold descriptions. A 2-hour AIDE run
costs almost exactly four times a 30-minute AIDE run ($10.88 against $2.71 for Sonnet,
$29.37 against $7.33 for o1-preview), which is what a scaffold that does tree search over
whole solutions without accumulating context should do. Modular, which does accumulate, has
no 2-hour cost marker on Figure 11, because 30-minute runs score better for it and the figure
plots only each configuration's best allocation.

### Splitting cost into tokens: Figure 12

Figure 12 is two stacked violin panels in Appendix A.2.2, four violins each in series order,
every violin carrying a median tick between two whisker caps. The top panel is completion
tokens per second during time waiting for completion requests; the bottom is the proportion
of run time spent waiting for completion requests. Their product is output tokens per second
of run wall clock; times the run limit it is output tokens per run. My digitized medians:

| Configuration | Completion tok/s | API-time share | Run limit | Output tok/run |
|---|---|---|---|---|
| claude-3-5-sonnet-20240620 / Modular | 36.75 | 0.306 | 1800 s | 20262 |
| claude-3-5-sonnet-20241022 / Modular | 38.29 | 0.231 | 1800 s | 15893 |
| claude-3-5-sonnet-20241022 / AIDE | 54.28 | 0.520 | 7200 s | 203356 |
| o1-preview / AIDE | 107.04 | 0.326 | 7200 s | 251235 |

Input tokens are then what is left of the run cost after paying for that output, at the
October 2024 list prices in `research/cost/list-prices.csv` — $3 and $15 per million for
both Claude 3.5 Sonnet revisions, $15 and $60 for o1-preview with reasoning billed as
output. Caching is not in play: the paper states no prompt caching was used, so the input
side is gross re-processing and the uncached-harness ruling in `DECISIONS.md` applies.

| Configuration | Cost per run | Input tok/run | Total tok/run | Measured r = in/out |
|---|---|---|---|---|
| claude-3-5-sonnet-20240620 / Modular | 7.64 | 2445342 | 2465604 | 120.7 |
| claude-3-5-sonnet-20241022 / Modular | 6.60 | 2121306 | 2137199 | 133.5 |
| claude-3-5-sonnet-20241022 / AIDE | 10.88 | 2610875 | 2814231 | 12.8 |
| o1-preview / AIDE | 29.37 | 952986 | 1204221 | 3.8 |

A row's tokens are k times its configuration's total per run, and FLOPs are tokens times
`flops_per_token` from the Codex registry: 2e11 for both Claude 3.5 Sonnet revisions, 1e11
for o1-preview.

**This refutes the pooled ratio the first submission used.** Transferring the paper's pooled
r = 58 to each configuration implies completion rates of 73 and 84 tokens per second for the
two Modular configurations and 15 and 13 for the two AIDE ones; the Figure 12 whiskers for
those configurations are 9 to 67, 13 to 84, 37 to 59, and 3 to 130. The Modular pair sit above
their own violins and the AIDE pair below. That is the expected shape — Modular accumulates
context while AIDE does tree search over whole solutions, and o1-preview bills reasoning as
output — and it is why a pooled ratio cannot describe both. The correction is small for the
Modular rows (+3.7%) and large for the AIDE ones (−17% for Sonnet, −35% for o1-preview).

**The band.** Three assumptions sit behind the output figure: the product of two medians is
not the median of the product; the violins do not say which run lengths they pool, while the
rows apply each median to that configuration's own run limit; and the medians are read off a
plot. The band scales the measured output rate by 0.5 and 1.5 and lets input absorb the
residual of the fixed cost. Because output is 3 to 4% of the Modular bill, 28% of the
Sonnet/AIDE bill and 51% of the o1-preview bill, that band is 0.99x to 1.01x on the Modular rows, 0.86x to 1.14x on the
Sonnet/AIDE rows, and 0.69x to 1.31x on the o1-preview rows. Each row states its own in
`notes`. `compute_evidence` stays `derived_assumed_inputs`.

### Cross-checks on the token route

The pooled sentence validates the route rather than the split. Applying each configuration's
wall-clock output rate to an 8-hour run predicts 324K, 254K, 813K, and 1,005K output tokens,
an unweighted mean of 599K against the paper's ~499K for a run mix whose weights are
undisclosed — 20% high, which is the right order for four configurations averaged without
their weights. And r = 58 pooled is what a mix of Modular near 130 and AIDE near 4 to 13
produces, so the pooled sentence is consistent with the per-configuration reads rather than
in tension with them.

The pooled sentence also bounds the model mix behind it. At Sonnet list prices 29M input and
499K output cost $94.5, against the $123 stated. Solving 348a + 22.455b = 28.515, where a and
b are o1-preview's shares of pooled input and output, gives a between 1.7% and 8.2%: the
pooled compute is 92 to 98% Claude 3.5 Sonnet and its blended coefficient is 1.92e11 to
1.97e11 rather than 2e11. That is why no single-model row can carry it.

One comparison the first submission overstated: it called the agreement between the 8-hour
Modular row's token count and the paper's pooled 29.5M "the strongest evidence available that
the inversion is not badly wrong". Under the old method both sides were computed from the same
ratio and the same price pair, so the agreement was close to an identity and tested only the
cost reading, which the $1,862-versus-$1,855 anchor tests far more tightly. Under the Figure
12 method the two sides are independent, and the 8-hour Modular row's 34.2M tokens at $105.6
against the paper's 29.5M at $123 is a real, if loose, check.

### Compute deliberately excluded, and how much it is

Two workloads are inside `task_description` on a strict reading of COLUMNS.md and are not in
`compute_flops`.

**The environment's own GPUs.** Environments allocate 0 to 6 H100s, a mean of 2.29 across
the seven (4, 1, 1, 6, 2, 2, and 0 per Appendix C), and the agent uses them to train and
evaluate the models it is building. Eight hours at 2.29 H100s and 989 TFLOP/s BF16 is
6.5e19 FLOPs fully utilized, roughly 2e19 at a realistic 30% — ten times the agent's own
token compute on the 8-hour rows. The coordinator has ruled it stays excluded, and the
reasons are that no utilization figure is published and the agent chooses what to run, so the
number would be invented; and that the allocation is a fixed grant that does not vary with the
agent, so adding 2e19 to 2.3e19 at the 8-hour budget would put all four configurations within
a few percent of each other and the row would measure the GPU grant instead of the agent. The
contrast between 1.2e17 for o1-preview at 2 hours and 2.7e19 for Modular at 32 hours is the
information content of this block, and the GPU term would erase it. METR's own Figure 11
excludes H100 cost on the same axis.

**This conflicts with a Codex row and the conflict is logged for Damon.** The Codex dataset's
`agen-mlebench-operand-insults` includes the agent-trained classifier's compute explicitly,
its note calling "subordinate classifier training is included task work"; that row's fit is
2.06e10 FLOPs against 2.87e16 of LLM work, seven orders down, so the precedent has never been
tested where it bites. The two treatments cannot both be right, and the coordinator has logged
the question for Damon as a cross-batch specification item, since it governs every future
agentic-ML row.

**GPT-3.5 inside Scaffolding for Rust CodeContests.** In one of the seven environments the
agent's deliverable is a scaffold around `gpt-3.5-turbo-0125`, and the environment supplies
a $500 OpenAI credit. Usage is not published. The ceiling, if a run exhausted the whole
credit, is 2.3e19 FLOPs at the 12B-active prior; but one full evaluation pass over the 175
held-out problems at the reference solution's n = 8 is of order 2e16 FLOPs, so tens of
passes in a run is of order 1e18, which spread over the seven environments adds of order
1e17 to a per-run average. That is about 2% of the 8-hour Modular row and roughly a quarter
of `agen-rebench-2h-o1preview-aide` at 1.2e17, which is where this exclusion is weakest and
where COLUMNS' requirement to include helper calls bites hardest. The human baseliners had
the same credit.

Excluded correctly rather than as a judgment: the Llama-3 8B judge that scores Finetune
GPT-2 for QA is an evaluation environment outside the work unit.

## Labels

The metric is the normalized score, whose floor is 0 by construction: an agent that changes
nothing scores the starting solution, which is 0. So the above-chance ratio is just the
score ratio.

| point_id | Budget | Configuration | AI score | Human score | AI / human | Label |
|---|---|---|---|---|---|---|
| agen-rebench-2h-sonnet35old-modular | 2 h | Sonnet 0620 / Modular | 0.175 | 0.077 | 2.28 | above |
| agen-rebench-2h-sonnet35new-modular | 2 h | Sonnet 1022 / Modular | 0.278 | 0.077 | 3.63 | above |
| agen-rebench-2h-sonnet35new-aide | 2 h | Sonnet 1022 / AIDE | 0.101 | 0.077 | 1.31 | above |
| agen-rebench-2h-o1preview-aide | 2 h | o1-preview / AIDE | 0.282 | 0.077 | 3.68 | above |
| agen-rebench-8h-sonnet35new-modular | 8 h | Sonnet 1022 / Modular | 0.444 | 0.657 | 0.68 | below |
| agen-rebench-8h-o1preview-aide | 8 h | o1-preview / AIDE | 0.429 | 0.657 | 0.65 | below |
| agen-rebench-32h-sonnet35new-modular | 32 h | Sonnet 1022 / Modular | 0.572 | 1.110 | 0.51 | below |
| agen-rebench-32h-o1preview-aide | 32 h | o1-preview / AIDE | 0.606 | 1.110 | 0.55 | below |

**No row is `far_above`, by the coordinator's ruling.** The first submission labeled two of
the 2-hour rows `far_above` on the numerical guide, where the human scores 27% of the AI. The
ruling is that neither side has done the job at a 2-hour budget — the best agent reaches 0.28
on a scale whose 1.0 is a strong reference solution — so the label reports a 3.6-times edge on
partial progress rather than a job the human cannot do. This follows the ARTEMIS A2 row,
accepted four hours earlier at 1.55 times the human mean as `above` "not `far_above` because
one professional scored higher", and the reading of the label in
`research/codex-performance-relabel.md`: `far_above` is for a human side that is not doing the
job while the AI is. A second limb points the same way. The human figure is a mean, the
8-hour distribution has a long right tail with 24% of attempts at or above the reference, and
nothing published rules out individual 2-hour checkpoints above 0.28; and the 2-hour human
value is the least stable number in the set, spanning 0.073 to 0.095 across three figures.

The four 8-hour and 32-hour cells that fall under the exclusion line are in
`candidates/rebench/dispositions.csv` rather than built as rows, following the GAIA
precedent that sets built after the exclusion ruling record excluded cells in a dispositions
file. All four were tested against the close-call rule on measured bands, using Figure 6's
whiskers where a bar exists and the Figure 7 or Figure 8 confidence band otherwise:

| Cell | Agent score | Band | Agent SE | Ratio | Ratio SE | SE below the 0.5 guide |
|---|---|---|---|---|---|---|
| agen-rebench-8h-sonnet35old-modular | 0.265 | Figure 6 whiskers | 0.0132 | 0.403 | 0.0435 | 2.22 |
| agen-rebench-8h-sonnet35new-aide | 0.224 | Figure 6 whiskers | 0.0539 | 0.340 | 0.0883 | 1.81 |
| agen-rebench-32h-sonnet35old-modular | 0.341 | 0.289 to 0.364 | 0.0193 | 0.307 | 0.0236 | 8.17 |
| agen-rebench-32h-sonnet35new-aide | 0.437 | 0.146 to 0.453 | 0.0782 | 0.394 | 0.0736 | 1.44 |

All four are more than one standard error under the guide, so none is restored. (Revision 1:
the first submission said the 32-hour bands could not be read. They can — the series that
overlap them have ended by k = 16 and k = 64 — and reading them resolves the one genuine
close call against restoration at 1.44 standard errors.) The kept 32-hour Modular row is 0.45
standard errors *above* the guide, so it is inside the close-call band in the other direction
and protected either way.

Every row carries `different_inputs_or_tools`, because the human baseliners could browse the
web and use LLMs while agents reached the internet only through bash and were not observed
using it. Rows whose agent side is a best-of-k selection also carry
`different_attempt_selection`; the two 2-hour AIDE rows are single runs and do not. The
2-hour rows carry `different_assessment` for the truncated-attempt point above.

Three facts about the selection that the rows now state rather than gloss. The k results are
sampled **with replacement** from METR's recorded pool, whose size the paper does not give, so
`ai_attempts` = k is the run count of the work unit `task_description` defines rather than a
count of distinct recorded runs. The selection is by best score in six of the seven
environments and **random in Scaling Law Experiment**, where the agent cannot see its score.
And the human side is best-of-1 at 8 hours against the agent's best-of-16, which is the
asymmetry the paper defends in Section 4.2 on the ground that an agent could reset its own
environment and implement the same procedure.

**The three budgets are not independent.** All three rows for a configuration are resamples of
one pool of recorded runs, and the human 8-hour and 32-hour values come from one sample of 71
attempts. A later analysis weighting rows equally is treating three observations where there
is one experiment.

## Points

Shared across all eight rows: `compute_scope = inference`, `compute_method = params_tokens`,
`compute_evidence = derived_assumed_inputs`, `compute_statistic = total`,
`compute_subset = all`, `tokens_accounting = input_output`, `task_category = coding`,
`human_skill = expert`, `human_time_evidence = defined_duration`,
`human_time_method = work_rate`, `human_time_statistic = point_estimate`.
`ai_cost_basis = reported` on every row, with `ai_cost_date = 2024-11-22`: the runs fall
between the 2024-10-22 release of `claude-3-5-sonnet-20241022` and the v1 submission, and both
price sheets held across that window, so the arXiv date stands in as the price-sheet date.
`human_cost_basis` is `reported_payment` at $1,855 on the 8-hour rows and 4 × $1,855 = $7,420
on the 32-hour rows. The 2-hour rows are `not_available`. METR does plot a human cost at the
2-hour budget, $468 on Figure 11's x axis, and the rows decline it while taking the AI number
off the same axis: $468 is a pro-ration of the $1,855 average, which is time times a wage and
is what the column forbids, whereas the AI budget is k times the cost of a run that was
actually made.

`task_category = coding` rather than `research_analysis`: six of the seven environments
deliver optimized ML code judged by running it, and the seventh, Scaling Law Experiment,
delivers a prediction from experiments the worker codes and runs. The whole task is ML
engineering.

### agen-rebench-2h-sonnet35old-modular

`claude-3-5-sonnet-20240620` in Modular, 2 total hours as four 30-minute runs. Cost
4 × $7.64 = $30.56. Tokens 4 × 2,465,604 = 9.86M at a measured r of 121. FLOPs 1.97e18; band
1.94e18 to 2.01e18. Score 0.175 (Figure 7, 30min@4; Figure 2 reads 0.177) against 0.077 for
the human at 2 hours. Ratio 2.28, `above`.

### agen-rebench-2h-sonnet35new-modular

`claude-3-5-sonnet-20241022` in Modular, 2 total hours as four 30-minute runs. Cost
4 × $6.60 = $26.41. Tokens 8.55M at r = 133. FLOPs 1.71e18; band 1.68e18 to 1.74e18. Score
0.278 (Figure 7, 30min@4; Figure 11 reads 0.285) against 0.077. Ratio 3.63, `above` on the
coordinator's ruling; the numerical guide alone would give `far_above`.

### agen-rebench-2h-sonnet35new-aide

`claude-3-5-sonnet-20241022` in AIDE, 2 total hours as one 2-hour run. Cost $10.88, read
directly off Figure 11 rather than multiplied. Tokens 2.81M at r = 12.8. FLOPs 5.63e17; band
4.82e17 to 6.44e17. Score 0.101 (Figure 8, 2h@1; Figure 2 reads 0.101) against 0.077. Ratio
1.31, `above`. This row and the next are the only two with no best-of-k selection on either
side.

### agen-rebench-2h-o1preview-aide

`o1-preview` in AIDE, 2 total hours as one 2-hour run. Cost $29.37. Tokens 1.20M at r = 3.8,
the lowest ratio in the set because o1-preview bills reasoning as output and AIDE does not
accumulate context. FLOPs 1.20e17; band 8.27e16 to 1.58e17. Score 0.282 (Figure 8, 2h@1;
Figure 2 reads 0.281) against 0.077. Ratio 3.68, `above` on the coordinator's ruling. It is
the cheapest row in the set, at a fifth the FLOPs of the next cheapest, and it beats the
human at 2 hours by 3.7 times, which is the paper's point. It is also the row where the
excluded GPT-3.5 helper would matter most, at roughly a quarter of the recorded total.

### agen-rebench-8h-sonnet35new-modular

`claude-3-5-sonnet-20241022` in Modular, 8 total hours as sixteen 30-minute runs — the
paper's best allocation for this configuration, and the one it reports as matching the 37th
percentile of human experts. Cost 16 × $6.60 = $105.64. Tokens 34.2M. FLOPs 6.84e18; band
6.74e18 to 6.94e18. Score 0.444 (Figure 7, 30min@16; Figure 6's bar 0.441, Figure 11's marker
0.445) against 0.657. Ratio 0.68, `below`.

### agen-rebench-8h-o1preview-aide

`o1-preview` in AIDE, 8 total hours as four 2-hour runs — the paper's best allocation for
this configuration, reported as matching the 36th percentile of human experts. Cost
4 × $29.37 = $117.48. Tokens 4.82M. FLOPs 4.82e17; band 3.31e17 to 6.32e17. Score 0.429
(Figure 8, 2h@4; Figure 6's bar 0.426) against 0.657. Ratio 0.65, `below`. Reaching two
thirds of an 8-hour expert's score for $117 of tokens against $1,855 of pay is the comparison
METR built the benchmark to make.

### agen-rebench-32h-sonnet35new-modular

`claude-3-5-sonnet-20241022` in Modular, 32 total hours as 64 30-minute runs. Cost
64 × $6.60 = $422.55. Tokens 137M. FLOPs 2.74e19; band 2.70e19 to 2.78e19. Score 0.572
(Figure 7, 30min@64) against 1.110 for the best of four 8-hour human attempts. Ratio 0.515,
`below`, 0.45 standard errors above the exclusion line and so inside the close-call band; on
Figure 2's human 32-hour value of 1.139 it would be 0.502. Both sides are best-of-k here,
which makes the attempt structure more symmetric than at 8 hours, though k and the
per-attempt length still differ and the flag stays.

### agen-rebench-32h-o1preview-aide

`o1-preview` in AIDE, 32 total hours as sixteen 2-hour runs. Cost 16 × $29.37 = $469.90.
Tokens 19.3M. FLOPs 1.93e18; band 1.32e18 to 2.53e18. Score 0.606 (Figure 8, 2h@16) against
1.110. Ratio 0.546, `below`. Figures 11 and 2 read this cell at 0.580 and 0.586 rather than
0.606, the one disagreement among the paper's figures; at 0.580 the ratio is 0.522 and the
label is unchanged.

## Dispositions

`candidates/rebench/dispositions.csv` records eight cells: the four budget-and-configuration
cells that fall under the exclusion line, and four grain decisions.

| Cell | Outcome | Short reason |
|---|---|---|
| agen-rebench-8h-sonnet35old-modular | excluded | 0.265 against 0.657, ratio 0.40, 2.22 SE below the guide |
| agen-rebench-8h-sonnet35new-aide | excluded | 0.224 against 0.657, ratio 0.34, 1.81 SE below the guide |
| agen-rebench-32h-sonnet35old-modular | excluded | 0.341 against 1.110, ratio 0.31, 8.17 SE below the guide on the Figure 7 band |
| agen-rebench-32h-sonnet35new-aide | excluded | 0.437 against 1.110, ratio 0.39, 1.44 SE below the guide on the Figure 8 band |
| environment-level rows | not a row | No per-environment token or cost figure exists; per-environment scores do exist, in Appendices G, H and I |
| pooled suite-level row at 8h@1 | not a row | Three models, two coefficients, undisclosed run weights, and no published pooled score |
| 8h@1 rows per configuration | not a row | Figure 12 gives output tokens at 8 hours but Figure 11 gives cost only at each configuration's best allocation, so input cannot be backed out |
| 16-hour and 64-hour budget rows | not a row | Buildable from Figure 11; not built, to avoid multiplying rows off one resampled run pool |

## Coordinator rulings applied in revision 1

1. **The environment GPU compute stays excluded**, with the quantified scenario kept in the
   note and in every row's `notes`. The conflict with the Codex MLE-bench row is recorded
   above and logged for Damon as a cross-batch specification item.
2. **The two `far_above` rows become `above`.** All four 2-hour rows are now `above`, on the
   ARTEMIS A2 precedent and the batch's own reading of the label.
3. **The 32-hour exclusions stand** on the measured bands, with the one genuine close call at
   1.44 standard errors under the guide.
4. **All three budgets are kept**, with their non-independence recorded.
5. **`different_attempt_selection` is kept**, and the rows now state that the k runs are
   sampled with replacement and that selection is random in one of the seven environments.

## Open items

- **Placement of the retained extracts.** The rows cite `agent-work/sources/rebench/` in
  `source_record`, which the 2026-09-13 ruling moves to `agent-work/sources/rebench/` at acceptance.
  Eight `source_record` strings and two paths in this note and in `PROVENANCE.md` need
  rewriting then; `source_record` has 102 characters of headroom.
- **Which score to take for `agen-rebench-32h-o1preview-aide`.** Figure 8 gives 0.606, and
  Figures 11 and 2 give 0.580 and 0.586. The rows take Figure 8. The label is `below` either
  way.
- **The human 32-hour value.** Figure 11 gives 1.110 and Figure 2 gives 1.139. The rows take
  Figure 11. On Figure 2 the kept 32-hour Modular row sits at 0.502 rather than 0.515.
