# Terminal-Bench 2.1 and Terminal-Bench-Science 0.1

*Created 2026-09-13 17:35.*
*Last revised 2026-09-13 20:05 (Revision 2, on the recheck): MiniMax-M3 moved to the root
registry's canonical 23B record, the five reasoning-effort model IDs collapsed onto their
base IDs, and four wording and provenance fixes. Revision 1 is preserved under
`candidates/terminal-bench/revision-1/` and the first submission of nineteen rows under
`candidates/terminal-bench/first-submission/`; the twenty-row state the independent review
checked is recorded row by row in `reviews/terminal-bench-independent.md`.*

## Summary

Forty-five rows: forty-four on Terminal-Bench 2.1 and one on Terminal-Bench-Science 0.1.
Thirteen are `match` and thirty-two are `below`, on the coordinator's 0.85 to 1.15 match
band.

Sixteen of the Terminal-Bench 2.1 rows come from the benchmark operator's own leaderboard
submissions in `harbor-framework/terminal-bench-2-1`, which publish
`uncached_input_tokens`, `cached_input_tokens` and `output_tokens` per run — the dataset's
counted quantity measured directly, with cache reads already separated. The other
twenty-eight come from Artificial Analysis's independent Terminus 2 run of the same 89
tasks, which publishes `input`, `cacheableInput`, `answer` and `reasoning` per model. That
board carries 29 scored cells and every one of them is now a row or a disposition. Human
time on all forty-four is 12,402.27 s, the mean of the task authors' own expert-time
estimates over 88 of the 89 tasks, recorded as `source_estimate`.

The forty-fifth row is **GPT-6 Astra on Terminal-Bench-Science 0.1**: 1.297e17 FLOPs
against 79,873.71 s of expert time, 46 of 70 tasks resolved, `below`. Its human side is the
best in this batch — 70 tasks authored by practising scientists, mean expert estimate
22.19 h, up to 600 h — and it is the only Terminal-Bench-Science cell on either board that
clears the half-of-human guide. Compute is a dollar inversion, because neither board
publishes a usable token count, and it rests on two irreconcilable donor readings of the
cache structure whose geometric mean is the central. The other 42 cells are recorded in
`candidates/terminal-bench/dispositions.csv`.

Nineteen new model records. Everything here is reproduced by
`python3 research/terminal-bench/build_rows.py --sources agent-work/sources/terminal-bench --out <dir>`,
which reads only the retained extracts in `agent-work/sources/terminal-bench/` and writes
`points.csv`, `models.csv`, `dispositions.csv` and `calculations.json`. That is the
reproduction path for every number below.

## The benchmark and the work unit

Terminal-Bench 2.0 is 89 terminal tasks, each an instruction plus a Docker container plus
a test suite plus an oracle solution, selected from 229 crowd-sourced contributions by 93
contributors ([Terminal-Bench 2.0, arXiv 2601.11868](https://arxiv.org/abs/2601.11868),
submitted 2026-01-17). Terminal-Bench 2.1 is the verified refresh — its README records that
"26 tasks were modified to fix bugs, modify timeouts or resources, or improve robustness to
reward hacking" — and the `harbor-framework/terminal-bench-2-1` repository carries the same
89 task directories as `harbor-framework/terminal-bench-2` with every `task.toml`'s
`expert_time_estimate_min` and `junior_time_estimate_min` byte-identical between the two.
Rows are built against 2.1 because that is the dataset both boards evaluated.

The work unit is **one agent attempt at one task, averaged over the suite**. Compute is
published only as a run total, so the grain is fixed by the source: total counted tokens
divided by the run's trial count. The trial counts are 445 on the official board (89 tasks
at 5 trials; one run logs 447) and 267 on Artificial Analysis (3 repeats). Because every
task receives the same number of trials, the arithmetic mean of the per-task author
estimates is the matching human quantity for a mean over trials, so the two sides are at
the same grain even though the compute is an aggregate.

Tasks run with internet access (`network_mode = "public"` / `allow_internet = true`) and
per-task agent timeouts from 600 s to 12,000 s, median 900 s.

## Human time

`human_time = 12402.27 s` on the forty-four Terminal-Bench 2.1 rows. The
Terminal-Bench-Science row's 79,873.71 s is derived under its own point_id below, from the
same kind of field.

The Terminal-Bench paper states the collection method verbatim: "Task authors were asked
to report how long they thought a junior software engineer with little familiarity with
the topic would take to complete their task (a 'junior time estimate') and how long a
domain expert would require ('expert time estimate')." The sibling benchmark's contributing
guide, `terminal-bench-science/CONTRIBUTING.md`, glosses the same field as "best-case hours
for a focused domain expert"; Terminal-Bench 2.1 itself ships no contributing guide, so
that gloss is the sibling's and the paper's sentence carries the claim on its own. These
are **estimates made by the people who wrote the tasks**, not timings, which is what
`human_time_evidence = source_estimate` records, with `human_time_method = estimated`,
`human_time_subset = not_applicable` and `human_attempts = not_applicable`. No human has
attempted a Terminal-Bench 2 task under measurement; the paper reports none, and the
"human-written solution" it mentions is the oracle, written by the task author with no
time attached.

From `agent-work/sources/terminal-bench/tb21-task-time-estimates.csv`, 88 of the 89 tasks carry
an expert estimate (`caffe-cifar-10` carries none):

| Statistic | Expert (min) | Junior (min) |
|---|---|---|
| n | 88 | 88 |
| mean | 206.70 | 1425.40 |
| median | 60 | 240 |
| geometric mean | 71.02 | — |
| minimum | 5 | 10 |
| maximum | 2400 | 19200 |
| sum | 18190 | 125435 |

206.70454545 min x 60 = **12,402.2727 s**. The arithmetic mean is used because
`COLUMNS.md` prefers it and because the compute figure is itself a mean over the same
tasks. The distribution is right-skewed: the median is 3,600 s and the geometric mean
4,261 s, and both are recorded here as scenarios. The mean is 3.4 times the median. Four
tasks carry expert estimates of a day or more (`gpt2-codegolf` 2,400 min; `fix-ocaml-gc`,
`regex-chess` and `write-compressor` 1,440 min each); dropping those four takes the mean
from 206.70 min to 136.5 min, so they account for a factor of 1.5 and the rest of the skew
is the shape of the remaining 84.

`human_skill = expert` follows the field's own definition. The junior estimates would
support a parallel `typical`-skill set of rows at 85,524 s; they are not built, because
the junior estimate is a second estimate of the same task by the same author and would
duplicate every row.

Two limitations, both stated in the rows' notes or here rather than in the CSV. First, one
task of 89 has no estimate, so the mean is over 88 while the compute mean is over all 89 —
a coverage gap of about 1%, direction unknown. Second, the paper's own Table 1 bins the
expert estimates as 36 under 1 h, 35 from 1 h to a day, 3 from a day to a week, summing to
74 rather than 89; the repository at the leaderboard's commit gives 40/44/4 over 88. The
paper's table therefore describes a smaller snapshot than what ships in 2.1. The
repository values are used because they are the dataset the runs were scored on.

## Compute: what the sources publish

### Official leaderboard submissions

Each file in `terminal-bench-2-1/leaderboard/submissions/` carries a `metrics` block with
`uncached_input_tokens`, `cached_input_tokens`, `output_tokens`, `total_cost_usd`,
`accuracy`, `accuracy_stderr` and `n_trials`, plus `metadata` naming the model, agent,
agent version, reasoning effort, date and merge PR. The counted quantity is

```
tokens_per_trial = (uncached_input_tokens + output_tokens) / n_trials
compute_flops    = tokens_per_trial * flops_per_token
```

`cached_input_tokens` is excluded, as `COLUMNS.md` requires for cache reads. That leaves
fresh input plus cache creation plus output, which is `input_cache_creation_output`.

**What the price check does and does not establish** (corrected in Revision 1). Pricing the
three counters at published list rates reproduces `total_cost_usd` exactly, to the cent, on
eleven of the sixteen official runs: both Gemini CLI runs (Gemini 3 Pro,
2 x 47.653156 + 0.2 x 329.123284 + 12 x 7.219388 = 247.76 against 247.76; Gemini 3.1 Pro
236.49 against 236.49), both Gemini Terminus 2 runs, GPT-5.5 under Codex at 5.00/0.50/30.00,
all four GPT-5.6 Codex runs at their launch rates, Grok 4.5 under Cursor CLI at
2.00/0.50/6.00, and the Muse Spark run that is dispositioned on other grounds. On those
eleven the counter definitions are confirmed: `uncached_input_tokens` is what is billed at
the input rate and `cached_input_tokens` is what is billed at the cache-read rate.

Five runs do not reproduce at any documented price vector, and their counter definitions
are therefore **assumed rather than confirmed**. Every Claude Code run's counters at list
price come to more than its reported figure — Opus 4.7 1.56x, Fable 5 1.59x, Sonnet 5 1.34x
at 3.00/0.30/15.00, Opus 4.8 1.21x — while Anthropic's own Terminus 2 runs roughly do
reproduce (Opus 4.7 to 0.97x at 5.00/0.50/25.00 and 1.00x with uncached at the 6.25
cache-write rate, Fable 5 to 1.15x). The gap is Claude Code specific, not Anthropic
specific. An earlier version of this note argued the mapping from a pooled solve over Opus
4.7 and Opus 4.8 under Claude Code that returned $6.04/M against a $6.25/M cache-write rate;
that argument does not survive, because solving within a single model returns a negative
cache-read price (Opus 4.7's two runs give p_C = -1.79, Fable 5's give -4.35), so no single
price vector fits an Anthropic model's two runs and the $6.04 was a coincidence of pooling.

The fifth is `agen-tbench21-glm51-claudecode`, which runs the other way: its reported
$277.14 is **2.26x** the $122.52 its own counters give at the GLM-5 list rates, and still
1.70x the $163 they give at GLM-5.3's. That is the largest unreproduced gap among built
rows and it is stated in that row's notes.

None of this changes a token value. It changes what the evidence supports: eleven rows have
confirmed counter definitions and five have assumed ones, and no row's dollars depend on the
check, since all sixteen official rows take `ai_cost_basis = reported`.

**A price-table finding, since amended.** The board's costs for GPT-5.6 Sol, Terra and Luna
reproduce at 5.00/0.50/30.00, 2.50/0.25/15.00 and 1.00/0.10/6.00 per million, which
`research/cost/list-prices.csv` did not carry when these rows were first built. The table
now carries six dated windows for the family and `research/cost/gpt56-repricing.md` records
the history: all three launched 2026-07-09 at those rates; on 2026-07-30 Terra and Luna were
cut 20% and 80% permanently; on 2026-08-21 Sol was cut to 4.00/0.40/20.00 under the one
promotional rate in the table. Only Sol's cut is promotional, and the earlier framing of the
whole family as one promotion was wrong. No Terminal-Bench row's dollars depend on the
table: the sixteen official rows and the Astra science row are `ai_cost_basis = reported`,
and the Artificial Analysis rows price at that board's own published rates.

### Artificial Analysis

Artificial Analysis runs Terminal-Bench v2.1 itself: "We run Terminal-Bench v2.1 with the
Terminus 2 agent harness in an e2b sandbox and report pass@1 averaged over 3 repeats per
task", on "the same 89 curated tasks". Its page also describes what v2.1 is — "v2.1
incorporates environment and instruction fixes — patched Dockerfiles ... and corrected
instruction-test mismatches across roughly a dozen tasks" — which an earlier version of this
note misread as something Artificial Analysis did on top of the benchmark. It is not: it is
the same refresh the Terminal-Bench 2.1 README describes from the other side, and both
boards run that dataset. `different_assessment` was dropped from these rows in Revision 1
accordingly; no row carries it, and the sixteen official rows span six harnesses without any
of them carrying one either.

Its page payload carries, per model, `terminalbenchV21` (the score) and
`canonicalEvalTokenCounts.terminalbenchV21` with `input`, `cacheableInput`, `answer` and
`reasoning`. `cacheableInput` is a subset of `input` on every model (ratios 0.88-0.98), so

```
tokens_per_trial = (input - cacheableInput + answer + reasoning) / 267
```

267 is confirmed arithmetically: every one of the 29 scored models' score times 267 is an
integer, and 267 = 89 x 3.

`cacheableInput` is what *could* be served from cache; Artificial Analysis separately
publishes a model-level `cacheHitRate` of 0.9934-0.9967 on every model but one. Treating the
missed share as fresh raises counted tokens by 2-6%; the rows take the straightforward
`input - cacheableInput` and state the adjusted figure in notes.

**Reconciliation, the main change in Revision 1.** The board carries 29 scored cells,
ranging 26.2% to 91.4%. The rule applied is: every scored cell is a row if it clears the
half-of-human guide and its model has a parameter prior, in either registry or derivable by
the method of the relevant report in `research/model-priors/`. Twenty-eight qualify;
`gpt-oss-120b` at 26.2% does not clear the guide and is the one disposition. Where the board
runs one model at more than one reasoning effort — GPT-6 Astra at max, high and medium,
Claude Fable 5.1 at max, xhigh and high, GPT-5.6 Sol at max and xhigh — each is its own row
on **one shared model ID**, with the served effort recorded in `task_description` and
`notes`. Revision 1 gave the five variants their own model IDs; Revision 2 collapsed them,
following ALE-Bench and this batch's own sixteen official rows, which carry
`reasoning_effort` the same way. The weights do not differ, so a second record would have
carried a second copy of the same prior.

The first submission built three of these on the stated ground that they were "the three
frontier models the official board does not carry", which was not a rule that selects three:
seventeen distinct models on this board are absent from the official one. It also
dispositioned the Artificial Analysis cells for GPT-5.6 Sol, Terra and Luna as duplicates of
official submissions, which was wrong — those official submissions are **Codex** runs, and
the scores differ accordingly (Sol 88.0% here against 76.2% official). Under this batch's
own practice a second harness is a second row, which is why Opus 4.7, Gemini 3 Pro,
Gemini 3.1 Pro and Fable 5 each get two. All four are now rows.

Artificial Analysis's scores on the same 89 tasks run above the official board's at the top
end (its Fable 5 Terminus 2 run scores 84.6% where the official Terminus 2 run scores 80.5%)
and the two boards are not score-comparable in detail, which the label section returns to.

## Performance and the match band

There is no scored human attempt, so the label rests on what the authors' estimate implies.
The field is the time for a focused domain expert to **complete** the task, so the human
baseline it implies is completion — 100% on the benchmark's own pass/fail metric, with a
chance floor of zero because the tasks are open-ended and verified by programmatic tests.
The ratio to the human baseline is therefore the resolution rate itself.

The coordinator ruled on 2026-09-13 that this folder's match band is **0.85 to 1.15** of the
human on the benchmark's own metric, the band recorded for ALE-Bench. Applied here, thirteen
rows at 0.850 to 0.914 are `match` and thirty-two at 0.506 to 0.846 are `below`. Nothing
reaches `above`, which would need 1.15, and nothing could: the implied human baseline is a
ceiling. The first submission labelled every row `below` on the reasoning that none was
"broadly comparable to an expert who finishes"; that reasoning is superseded, and the
reviewer's point that the 100% baseline is itself an unmeasured ceiling cuts in the same
direction — a real expert given these 89 tasks under the same timeouts would not resolve all
of them, so the true ratios are higher than the recorded ones, not lower.

One caveat the band cannot resolve: the two boards are not score-comparable, and all
thirteen `match` rows are Artificial Analysis rows, whose scores run above the official
board's at the top end. A single ratio boundary applied
across both boards mixes two measurement regimes. It is applied anyway, because the
alternative is a per-board boundary with no stated basis.

`comparison_issues = different_attempt_selection` on every row: the compute and cost figures
average over all trials including failures and, where applicable, trials later disqualified
for reward hacking, while the human time is the time to complete. The absent human score is
not itself listed, following `COLUMNS.md` ("Missing documentation or an estimated human
baseline alone is not a known difference").

## Terminal-Bench-Science 0.1

[Terminal-Bench-Science 0.1](https://www.tbench.ai/news/terminal-bench-science-0-1) is 70
tasks authored and reviewed by domain experts across the life, physical, Earth,
mathematical and engineering sciences, from 920 proposals and 386 pull requests by 376
contributors. Every task's `task.toml` carries `expert_time_estimate_hours`, glossed in
the contributing guide as "best-case hours for a focused domain expert". All 70 carry one.
Mean 22.19 h, median 12 h, geometric mean 10.32 h, range 1.6 h
(`supraglacial-lake-classification`) to 600 h (`onsager-ising-lean`), total 1,553.1 h. In
seconds the mean is 79,873 s — six and a half times the Terminal-Bench 2.1 figure and the
strongest author-estimated human time in this batch.

It produces exactly one row, and 37 cells that are not rows.

**Performance removes most of them.** The official board's fourteen entries run 3.33% to
40.0% resolution over 210 trials each (70 tasks x 3). Against the completion the authors'
estimates imply, the best is a ratio of 0.400, 3.0 standard errors below the half-of-human
guide; the rest are 6 to 38 standard errors below. Under the 2026-09-13 exclusion ruling and
the one-standard-error close-call rule, none is a row. The Vals AI board's 24 entries, one
graded run per task with Terminus 2, run 0% to 65.71%, and only **GPT-6 Astra at 65.71%**
clears the bar — 2.8 standard errors above it. That cell is the row; its derivation is under
its point_id below.

**The compute problem.** The official board publishes a single `total_tokens` per model with
no cache split, and it is a gross figure including cache reads: GPT-5.6 Luna's 14.247e9
tokens cost $383.20, or $0.0269 per million, below any input rate and just above its
$0.02/M cache-read rate. Recovering the counted quantity means solving

```
U + C + O = total_tokens
p_U*U + p_C*C + p_O*O = total_cost_usd
```

with an assumed U/O ratio. `python3 research/terminal-bench/tbscience_compute_probe.py
--sources agent-work/sources/terminal-bench` runs it. At OpenAI's current sheet, with U/O
transferred from each model's own Terminal-Bench 2.1 Codex run, the three OpenAI entries
agree closely on the counted share of the gross total — Sol 1.538%, Terra 1.487%, Luna
1.769% — implying 615,776, 539,575 and 1,200,265 counted tokens per trial, 6 to 11 times the
same models' Terminal-Bench 2.1 figures for a task budget roughly thirty times longer
(28,800 s against a 900 s median). The launch price vector is arithmetically excluded by
that solve: it gives shares of 0.024% and 0.205% for Sol and Terra and a negative residual
for Luna. **The dating argument points the same way and is stronger than the arithmetic
one**: the board carries DeepSeek V4.1 Flash at `model_release_date` 2026-09-10, so its runs
postdate both the 2026-07-30 Terra and Luna cuts and the 2026-08-21 Sol cut, and the current
vector is the right one on dates as well.

That solve is nonetheless a 1.5% residual of a difference between two large numbers — moving
the cached rate from $0.40 to $0.50 per million collapses Sol's counted tokens by a factor of
45 — and the Claude Code entries are worse, since the price check above shows Anthropic's
Claude Code runs are not list-reproducible at all. So no row is built from this board, and
the probe's output is kept as the input to the science row's growth factor rather than as a
compute estimate in its own right. **That fragility is a property of the probe, not of the
row**: the row's own arithmetic is a geometric mean of a fixed transfer and a
growth-dependent one, which is almost flat in the growth factor.

Why the official board is not the source for the built row even though it decomposes
further: its GPT-6 Astra cell does not exist. Astra is absent from the tbench.ai board
entirely, and of the fourteen models it does carry, none clears the performance bar.

## Models

Eleven model IDs are reused. `claude-opus-4-7`, `claude-opus-4-8`, `claude-opus-5-max`,
`gemini-3-pro`, `gemini-3.1-pro-preview` and `gpt-5-6-sol` come from the Codex registry at
`../AI Compute vs Human Time/dataset/models.csv` with its assumptions; `gpt-5-5`,
`gpt-5-6-terra`, `gpt-5-6-luna`, `gpt-6-astra`, `kimi-k3` and `minimax-m3` from this folder's
`models.csv`.

`minimax-m3` takes the root registry's canonical record, 23B active at 4.6e10 per token, on
MiniMax's own developer summary of about 428B total and about 23B activated and on a count
of the published config giving 23.3B excluding embeddings and the output head. Revision 1
had minted a 22B record here from the priors report's efficient-MoE table; the root record
is better sourced and is the one used.

`gpt-5-6-sol` is the one case where the ruled prior has not yet been applied: DECISIONS
ruled 150B active for it, but the ID is shared with the Codex registry, which still carries
100B, and shared IDs are updated once at merge. All three Sol rows —
`agen-tbench21-gpt56sol-codex`, `agen-tbench21-aa-gpt56sol` and
`agen-tbench21-aa-gpt56sol-xhigh` — are therefore 1.5x low until `tools/apply_priors.py`
runs, on the pattern of GAIA's `agen-gaia-hal-gemini20flash-l1`, and each says so in its
`notes`. Revision 1 had given the xhigh row a batch-only record carrying the ruled 150B,
which split one set of weights across two coefficients; collapsing the ID removed that.

`gemini-3-pro` is matched to the submissions' `gemini/gemini-3-pro-preview` endpoint; the
Codex registry's record for that model is named without the `-preview` suffix while its
sibling `gemini-3.1-pro-preview` keeps it.

Nineteen records are new, all grade C unless the basis says `reported`, each carrying its
range in its own `notes` field. Five came with the first submission:

| model_id | active (B) | flops_per_token | route |
|---|---|---|---|
| claude-fable-5 | 150 | 3.0e11 | the Anthropic report's own recommendation for the Fable class, 60-400B |
| claude-fable-5-1 | 150 | 3.0e11 | the same recommendation, 60-400B |
| claude-sonnet-5 | 100 | 2.0e11 | Sonnet-tier transfer from the Sonnet 4.5 and 4.6 priors the ruling held, 50-200B |
| grok-4-5 | 100 | 2.0e11 | ruled Grok 4 sparsity of 15x on the 1.5T V9 foundation, 45-210B |
| glm-5.1 | 40 | 8.0e10 | bracketed by GLM-5 and GLM-5.2, both 744B total over 40B active, 30-50B |

Fourteen are new in Revision 1, as amended:

| model_id | active (B) | basis | route |
|---|---|---|---|
| grok-4-6 | 100 | estimated | the Grok 4.5 derivation, corroborated by the report's 1.71x Grok 4 to Grok 4.6 price ladder, which gives 117B |
| gemini-3-8-flash | 40 | estimated | the Gemini 3-generation Flash prior the report holds, 15-90B |
| gemini-3-5-flash-lite | 20 | estimated | the Flash-Lite prior the report holds, 6-45B |
| muse-spark-1-3 | 100 | estimated | within-lab price ratio to Muse Glimmer, 3.18x on a 30B anchor, 50-170B |
| muse-glimmer | 30 | estimated | Artificial Analysis's own figure, no report coverage and no lab architecture note, 15-60B |
| glm-5.3 | 40 | reported | Epoch's "same base model as GLM-5.2", 744B over 40B, and Artificial Analysis agreeing |
| glm-5.3-flash | 18 | estimated | Epoch at Likely, 320B over 18B, Artificial Analysis agreeing |
| qwen3.8-2.4t-a95b | 95 | reported | stated in the model's name and in the report's table |
| qwen3.8-27b | 27 | reported | dense count in the model's name |
| deepseek-v4-pro-0813 | 49 | reported | DeepSeek's own V4 release page, the citation the registry's preview record already carries |
| k2-horizon-375b-a23b | 23 | reported | stated in the model's name |
| inkling | 41 | estimated | Artificial Analysis's own figure, no report coverage, 20-80B |
| nvidia-nemotron-3-ultra-550b-a55b | 55 | reported | stated in the model's name |
| mistral-medium-3-5 | 128 | estimated | Artificial Analysis's own figure, no report coverage, 40-200B |

Three of these deserve flagging rather than burying in a table. **`mistral-medium-3-5` at
128B is the weakest new prior in the batch**: no report covers Mistral Medium, Mistral has
disclosed no Medium 3.x architecture, and 128B sits above the registry's 41B for the larger
Mistral Large 3. It is an order-of-magnitude placeholder and its row should be read that way.
**`muse-glimmer` and `inkling` share one provenance** — a figure Artificial Analysis
publishes with nothing to check it against — so both are `estimated`; Revision 1 had
Glimmer as `reported` on the reasoning that the board's field reproduces the registries
elsewhere, which is an argument about the field in general rather than about this model.
**`deepseek-v4-pro-0813` is kept separate from `deepseek-v4-pro-preview`** not because their
dates differ but because that record's own note says its run "used the April preview, before
the August general release"; this is that general release, and both carry DeepSeek's own 49B.

Artificial Analysis's `activeParams` field is used as a source where it exists, because it
reproduces the registries' own counts wherever both exist — gpt-oss-120b 5.1B, Kimi K3 104B,
DeepSeek V4-Pro 49B, GLM-5.3 40B, GLM-5.3-Flash 18B all match, and its 23B for MiniMax-M3
matches the root record this batch now uses. It is null on every closed frontier model,
which is consistent with the priors reports' finding that no lab discloses.

Release dates come from the Artificial Analysis model records retrieved 2026-09-13, which
for Fable 5 and Fable 5.1 agree with the Terminal-Bench-Science leaderboard's own
`model_release_date` metadata. Claude Fable 5's submissions are dated 2026-06-05 and
2026-06-07, before its 2026-06-09 release — a pre-release partner evaluation. `grok-4-5` and
`grok-4-6` take `company = xAI` rather than the "SpaceXAI" label Artificial Analysis uses,
so the merged registry does not carry one lab under two names; the official submission's own
`metadata.model_org` says xAI.

Anthropic serves Fable 5 with an Opus 4.8 fallback, so a share of the Fable 5 rows' turns
may have run on a different model; that is stated in the model record and in those rows'
notes.

## Cached-context attention

Under the DECISIONS ruling, every run whose contexts exceed roughly 10k tokens re-read per
call carries a quantified scenario for the attention term the 2 x active-parameters
convention omits. `python3 research/terminal-bench/attention_scenario.py --calculations
candidates/terminal-bench/calculations.json` prints it per row.

The recipe is the dataset's RULER one: attention costs 4 x L x d_model x N_context per
processed token against 2 x active_parameters for the parameter term, so the ratio is
2 x L x d_model x N_context / active_parameters. With prompt caching the processed tokens
per trial are exactly the counted quantity, and an append-only agent dialog grows its prefix
linearly to that same total, so the length-weighted mean prefix is half the counted tokens
per trial. Architectures bracket by size class, because a 96-layer 12,288-wide shape is not
plausible for an 8B-active model: 64/8192 to 96/12288 above 100B active, 48/6144 to 64/8192
from 30B to 100B, 32/4096 to 48/6144 below 30B.

The term runs **0.01x to 5.25x** the parameter-only value across the forty-five rows, and
thirty-one of them sit between 0.12x and 1.35x. The extremes are informative rather than
typical: the lean-in-tokens, large-in-parameters Artificial Analysis rows sit at 0.01-0.05x,
and GPT-5.5 under the early Codex build is the reverse at 2.33-5.25x. The term is one-sided: including it raises every row. It is now included — `research/attention-correction.md`
folds it into `compute_flops` across the file, on a per-model attention shape rather than the
size-class bracket used here.

One limit of the recipe on these runs, which the reviewer is right about. The "mean prefix" it derives is a context length only where the
counted tokens really are one growing dialog. On GPT-5.5 under Codex 0.125.0 the 770,255
counted tokens per trial are largely repeated prefix re-processing, not a 385,128-token
context that harness ever held, so its 2.33-5.25x is an overestimate; on the heavily cached
Codex 0.144 runs the real per-call prefix exceeds half the counted tokens, so those are
underestimates. The scenario is an order-of-magnitude bracket, not a per-row measurement.

## Dispositions

`candidates/terminal-bench/dispositions.csv` records 42 cells that are not rows, with the
resolution rate, its ratio to the human baseline, how many standard errors that ratio sits
below the half-of-human guide, and the reason.

| Source | Cells | Why not rows |
|---|---|---|
| Terminal-Bench 2.1 official leaderboard | 4 | Two token counters that are demonstrably not the counted quantity (GPT-5.5 under Terminus 2, Muse Spark 1.1 under mini-SWE-agent) and the two 2026-07-10 Codex 0.144.0 runs of GPT-5.6 Luna and Terra |
| Artificial Analysis Terminal-Bench v2.1 | 1 | `gpt-oss-120b` at 26.2%, 13.9 standard errors below the half-of-human guide |
| Terminal-Bench-Science 0.1 official board | 14 | All 3.0 to 37.7 standard errors below the guide, and the published token total is gross |
| Vals AI Terminal-Bench-Science 0.1 board | 23 | All below the guide by 2.8 to 34.2 standard errors, or scoring zero. The board's 24th model, GPT-6 Astra, clears it and is built |

On the two superseded official runs: they are two distinct runs rather than resubmissions —
Codex 0.144.0 on 2026-07-10 against 0.144.1 on 2026-07-11, with different scores and
different disqualification counts — and excluding them creates a visible asymmetry. Sol's
kept row is its 32-disqualification 0.144.0 run, because Sol has no rerun, while Terra's and
Luna's kept rows are their clean 0.144.1 runs. The dispositions say so.

## Per-point arithmetic

Every row's inputs, arithmetic and per-row judgments follow. They are generated from
`candidates/terminal-bench/calculations.json` by
`python3 research/terminal-bench/emit_point_sections.py --calculations <file>`.

### agen-tbench21-aa-dsv4pro0813

Artificial Analysis model slug `deepseek-v4-pro` (DeepSeek V4 Pro 0813 (Reasoning, Max Effort), DeepSeek), Terminus 2 in an e2b sandbox, 3 repeats of each of the 89 tasks.

| Input | Value |
|---|---|
| trials | 267 |
| input tokens (gross) | 125630545 |
| cacheable input tokens (excluded) | 122337659 |
| answer tokens | 1098260 |
| reasoning tokens | 5351381 |
| published cache hit rate | 0.990800 |
| resolution rate (%) | 78.65 |
| binomial standard error (pp) | 2.51 |

uncached input = 125630545 - 122337659 = 3292886; counted tokens = 3292886 + 1098260 + 5351381 = 9742527; per trial 9742527 / 267 = **36488.8652**.

compute_flops = 36488.8652 x 9.8e+10 = **3.57591e+15**.

Treating the share the published hit rate says missed cache as fresh gives 40704.1441 tokens per trial instead, 11.6% higher; the row takes the straightforward figure and states this in notes.

ai_cost_usd = **0.13210** per trial, `list_price` at the rates Artificial Analysis publishes for this model, dated 2026-09-13 because the board gives no run date. Ratio to the human baseline 0.787, so `below`. Attention term 0.22-0.39x the parameter-only value, since folded into `compute_flops`.

### agen-tbench21-aa-dsv4pro0813

Artificial Analysis model slug `deepseek-v4-pro` (DeepSeek V4 Pro 0813 (Reasoning, Max Effort), DeepSeek), Terminus 2 in an e2b sandbox, 3 repeats of each of the 89 tasks.

| Input | Value |
|---|---|
| trials | 267 |
| input tokens (gross) | 125630545 |
| cacheable input tokens (excluded) | 122337659 |
| answer tokens | 1098260 |
| reasoning tokens | 5351381 |
| published cache hit rate | 0.990800 |
| resolution rate (%) | 78.65 |
| binomial standard error (pp) | 2.51 |

uncached input = 125630545 - 122337659 = 3292886; counted tokens = 3292886 + 1098260 + 5351381 = 9742527; per trial 9742527 / 267 = **36488.8652**.

compute_flops = 36488.8652 x 9.8e+10 = **3.57591e+15**.

Treating the share the published hit rate says missed cache as fresh gives 40704.1441 tokens per trial instead, 11.6% higher; the row takes the straightforward figure and states this in notes.

ai_cost_usd = **0.13210** per trial, `list_price` at the rates Artificial Analysis publishes for this model, dated 2026-09-13 because the board gives no run date. Ratio to the human baseline 0.787, so `below`. Attention term 0.22-0.39x the parameter-only value, since folded into `compute_flops`.

### agen-tbench21-aa-fable5

Artificial Analysis model slug `claude-fable-5` (Claude Fable 5 (Adaptive Reasoning, Max Effort, Opus 4.8 Fallback), Anthropic), Terminus 2 in an e2b sandbox, 3 repeats of each of the 89 tasks.

| Input | Value |
|---|---|
| trials | 267 |
| input tokens (gross) | 76661563 |
| cacheable input tokens (excluded) | 70817594 |
| answer tokens | 895326 |
| reasoning tokens | 3704940 |
| published cache hit rate | 0.994525 |
| resolution rate (%) | 84.64 |
| binomial standard error (pp) | 2.21 |

uncached input = 76661563 - 70817594 = 5843969; counted tokens = 5843969 + 895326 + 3704940 = 10444235; per trial 10444235 / 267 = **39116.9850**.

compute_flops = 39116.9850 x 3e+11 = **1.17351e+16**.

Treating the share the published hit rate says missed cache as fresh gives 40569.1499 tokens per trial instead, 3.7% higher; the row takes the straightforward figure and states this in notes.

ai_cost_usd = **1.34558** per trial, `list_price` at the rates Artificial Analysis publishes for this model, dated 2026-09-13 because the board gives no run date. Ratio to the human baseline 0.846, so `below`. Attention term 0.14-0.31x the parameter-only value, since folded into `compute_flops`.

### agen-tbench21-aa-fable51

Artificial Analysis model slug `claude-fable-5-1` (Claude Fable 5.1 (Adaptive Reasoning, Max Effort, Default Fallback), Anthropic), Terminus 2 in an e2b sandbox, 3 repeats of each of the 89 tasks.

| Input | Value |
|---|---|
| trials | 267 |
| input tokens (gross) | 149743249 |
| cacheable input tokens (excluded) | 142508037 |
| answer tokens | 1331788 |
| reasoning tokens | 4019111 |
| published cache hit rate | 0.994525 |
| resolution rate (%) | 91.39 |
| binomial standard error (pp) | 1.72 |

uncached input = 149743249 - 142508037 = 7235212; counted tokens = 7235212 + 1331788 + 4019111 = 12586111; per trial 12586111 / 267 = **47138.9925**.

compute_flops = 47138.9925 x 3e+11 = **1.41417e+16**.

Treating the share the published hit rate says missed cache as fresh gives 50061.2207 tokens per trial instead, 6.2% higher; the row takes the straightforward figure and states this in notes.

ai_cost_usd = **1.40646** per trial, `list_price` at the rates Artificial Analysis publishes for this model, dated 2026-09-13 because the board gives no run date. Ratio to the human baseline 0.914, so `match`. Attention term 0.16-0.37x the parameter-only value, since folded into `compute_flops`.

### agen-tbench21-aa-fable51-high

Artificial Analysis model slug `claude-fable-5-1-high` (Claude Fable 5.1 (Adaptive Reasoning, High Effort, Default Fallback), Anthropic), Terminus 2 in an e2b sandbox, 3 repeats of each of the 89 tasks.

| Input | Value |
|---|---|
| trials | 267 |
| input tokens (gross) | 54862921 |
| cacheable input tokens (excluded) | 52508525 |
| answer tokens | 577678 |
| reasoning tokens | 771669 |
| published cache hit rate | 0.994525 |
| resolution rate (%) | 89.89 |
| binomial standard error (pp) | 1.85 |

uncached input = 54862921 - 52508525 = 2354396; counted tokens = 2354396 + 577678 + 771669 = 3703743; per trial 3703743 / 267 = **13871.6966**.

compute_flops = 13871.6966 x 3e+11 = **4.16151e+15**.

Treating the share the published hit rate says missed cache as fresh gives 14948.4211 tokens per trial instead, 7.8% higher; the row takes the straightforward figure and states this in notes.

ai_cost_usd = **0.39003** per trial, `list_price` at the rates Artificial Analysis publishes for this model, dated 2026-09-13 because the board gives no run date. Ratio to the human baseline 0.899, so `match`. Attention term 0.05-0.11x the parameter-only value, since folded into `compute_flops`.

### agen-tbench21-aa-fable51-xhigh

Artificial Analysis model slug `claude-fable-5-1-xhigh` (Claude Fable 5.1 (Adaptive Reasoning, Xhigh Effort, Default Fallback), Anthropic), Terminus 2 in an e2b sandbox, 3 repeats of each of the 89 tasks.

| Input | Value |
|---|---|
| trials | 267 |
| input tokens (gross) | 94035465 |
| cacheable input tokens (excluded) | 89530769 |
| answer tokens | 952661 |
| reasoning tokens | 2121965 |
| published cache hit rate | 0.994525 |
| resolution rate (%) | 91.01 |
| binomial standard error (pp) | 1.75 |

uncached input = 94035465 - 89530769 = 4504696; counted tokens = 4504696 + 952661 + 2121965 = 7579322; per trial 7579322 / 267 = **28386.9738**.

compute_flops = 28386.9738 x 3e+11 = **8.51609e+15**.

Treating the share the published hit rate says missed cache as fresh gives 30222.8656 tokens per trial instead, 6.5% higher; the row takes the straightforward figure and states this in notes.

ai_cost_usd = **0.82832** per trial, `list_price` at the rates Artificial Analysis publishes for this model, dated 2026-09-13 because the board gives no run date. Ratio to the human baseline 0.910, so `match`. Attention term 0.10-0.22x the parameter-only value, since folded into `compute_flops`.

### agen-tbench21-aa-gemini35flashlite

Artificial Analysis model slug `gemini-3-5-flash-lite` (Gemini 3.5 Flash-Lite, Google), Terminus 2 in an e2b sandbox, 3 repeats of each of the 89 tasks.

| Input | Value |
|---|---|
| trials | 267 |
| input tokens (gross) | 211811347 |
| cacheable input tokens (excluded) | 207455987 |
| answer tokens | 966564 |
| reasoning tokens | 1114706 |
| published cache hit rate | 0.818852 |
| resolution rate (%) | 53.56 |
| binomial standard error (pp) | 3.05 |

uncached input = 211811347 - 207455987 = 4355360; counted tokens = 4355360 + 966564 + 1114706 = 6436630; per trial 6436630 / 267 = **24107.2285**.

compute_flops = 24107.2285 x 4e+10 = **9.64289e+14**.

Treating the share the published hit rate says missed cache as fresh gives 164857.1716 tokens per trial instead, 583.8% higher; the row takes the straightforward figure and states this in notes.

ai_cost_usd = **0.04769** per trial, `list_price` at the rates Artificial Analysis publishes for this model, dated 2026-09-13 because the board gives no run date. Ratio to the human baseline 0.536, so `below`. Attention term 0.16-0.36x the parameter-only value, since folded into `compute_flops`.

### agen-tbench21-aa-gemini38flash

Artificial Analysis model slug `gemini-3-8-flash` (Gemini 3.8 Flash (high), Google), Terminus 2 in an e2b sandbox, 3 repeats of each of the 89 tasks.

| Input | Value |
|---|---|
| trials | 267 |
| input tokens (gross) | 283570242 |
| cacheable input tokens (excluded) | 276083298 |
| answer tokens | 1697849 |
| reasoning tokens | 2956103 |
| published cache hit rate | 0.892090 |
| resolution rate (%) | 87.64 |
| binomial standard error (pp) | 2.01 |

uncached input = 283570242 - 276083298 = 7486944; counted tokens = 7486944 + 1697849 + 2956103 = 12140896; per trial 12140896 / 267 = **45471.5206**.

compute_flops = 45471.5206 x 8e+10 = **3.63772e+15**.

Treating the share the published hit rate says missed cache as fresh gives 157052.8327 tokens per trial instead, 245.4% higher; the row takes the straightforward figure and states this in notes.

ai_cost_usd = **0.16395** per trial, `list_price` at the rates Artificial Analysis publishes for this model, dated 2026-09-13 because the board gives no run date. Ratio to the human baseline 0.876, so `match`. Attention term 0.34-0.60x the parameter-only value, since folded into `compute_flops`.

### agen-tbench21-aa-glm53

Artificial Analysis model slug `glm-5-3` (GLM-5.3 (max), Z AI), Terminus 2 in an e2b sandbox, 3 repeats of each of the 89 tasks.

| Input | Value |
|---|---|
| trials | 267 |
| input tokens (gross) | 136692446 |
| cacheable input tokens (excluded) | 130793242 |
| answer tokens | 853063 |
| reasoning tokens | 2698125 |
| published cache hit rate | 0.995300 |
| resolution rate (%) | 83.90 |
| binomial standard error (pp) | 2.25 |

uncached input = 136692446 - 130793242 = 5899204; counted tokens = 5899204 + 853063 + 2698125 = 9450392; per trial 9450392 / 267 = **35394.7266**.

compute_flops = 35394.7266 x 8e+10 = **2.83158e+15**.

Treating the share the published hit rate says missed cache as fresh gives 37697.0795 tokens per trial instead, 6.5% higher; the row takes the straightforward figure and states this in notes.

ai_cost_usd = **0.21682** per trial, `list_price` at the rates Artificial Analysis publishes for this model, dated 2026-09-13 because the board gives no run date. Ratio to the human baseline 0.839, so `below`. Attention term 0.26-0.46x the parameter-only value, since folded into `compute_flops`.

### agen-tbench21-aa-glm53flash

Artificial Analysis model slug `glm-5-3-flash` (GLM-5.3-Flash, Z AI), Terminus 2 in an e2b sandbox, 3 repeats of each of the 89 tasks.

| Input | Value |
|---|---|
| trials | 267 |
| input tokens (gross) | 157758836 |
| cacheable input tokens (excluded) | 151446258 |
| answer tokens | 889979 |
| reasoning tokens | 2731018 |
| published cache hit rate | 0.995300 |
| resolution rate (%) | 84.27 |
| binomial standard error (pp) | 2.23 |

uncached input = 157758836 - 151446258 = 6312578; counted tokens = 6312578 + 889979 + 2731018 = 9933575; per trial 9933575 / 267 = **37204.4007**.

compute_flops = 37204.4007 x 3.6e+10 = **1.33936e+15**.

Treating the share the published hit rate says missed cache as fresh gives 39870.3087 tokens per trial instead, 7.2% higher; the row takes the straightforward figure and states this in notes.

ai_cost_usd = **0.02507** per trial, `list_price` at the rates Artificial Analysis publishes for this model, dated 2026-09-13 because the board gives no run date. Ratio to the human baseline 0.843, so `below`. Attention term 0.27-0.61x the parameter-only value, since folded into `compute_flops`.

### agen-tbench21-aa-gpt56luna

Artificial Analysis model slug `gpt-5-6-luna` (GPT-5.6 Luna (max), OpenAI), Terminus 2 in an e2b sandbox, 3 repeats of each of the 89 tasks.

| Input | Value |
|---|---|
| trials | 267 |
| input tokens (gross) | 82569478 |
| cacheable input tokens (excluded) | 81004211 |
| answer tokens | 887304 |
| reasoning tokens | 1259382 |
| published cache hit rate | 0.993391 |
| resolution rate (%) | 80.90 |
| binomial standard error (pp) | 2.41 |

uncached input = 82569478 - 81004211 = 1565267; counted tokens = 1565267 + 887304 + 1259382 = 3711953; per trial 3711953 / 267 = **13902.4457**.

compute_flops = 13902.4457 x 1.6e+10 = **2.22439e+14**.

Treating the share the published hit rate says missed cache as fresh gives 15907.6253 tokens per trial instead, 14.4% higher; the row takes the straightforward figure and states this in notes.

ai_cost_usd = **0.01689** per trial, `list_price` at the rates Artificial Analysis publishes for this model, dated 2026-09-13 because the board gives no run date. Ratio to the human baseline 0.809, so `below`. Attention term 0.23-0.51x the parameter-only value, since folded into `compute_flops`.

### agen-tbench21-aa-gpt56sol

Artificial Analysis model slug `gpt-5-6-sol` (GPT-5.6 Sol (max), OpenAI), Terminus 2 in an e2b sandbox, 3 repeats of each of the 89 tasks.

| Input | Value |
|---|---|
| trials | 267 |
| input tokens (gross) | 31153636 |
| cacheable input tokens (excluded) | 29223016 |
| answer tokens | 589903 |
| reasoning tokens | 716956 |
| published cache hit rate | 0.993391 |
| resolution rate (%) | 88.01 |
| binomial standard error (pp) | 1.99 |

uncached input = 31153636 - 29223016 = 1930620; counted tokens = 1930620 + 589903 + 716956 = 3237479; per trial 3237479 / 267 = **12125.3895**.

compute_flops = 12125.3895 x 2e+11 = **2.42508e+15**.

Treating the share the published hit rate says missed cache as fresh gives 12848.7766 tokens per trial instead, 6.0% higher; the row takes the straightforward figure and states this in notes.

ai_cost_usd = **0.17060** per trial, `list_price` at the rates Artificial Analysis publishes for this model, dated 2026-09-13 because the board gives no run date. Ratio to the human baseline 0.880, so `match`. Attention term 0.06-0.14x the parameter-only value, since folded into `compute_flops`.

### agen-tbench21-aa-gpt56sol-xhigh

Artificial Analysis model slug `gpt-5-6-sol-xhigh` (GPT-5.6 Sol (xhigh), OpenAI), Terminus 2 in an e2b sandbox, 3 repeats of each of the 89 tasks.

| Input | Value |
|---|---|
| trials | 267 |
| input tokens (gross) | 18963277 |
| cacheable input tokens (excluded) | 17507646 |
| answer tokens | 516757 |
| reasoning tokens | 442910 |
| published cache hit rate | 0.993391 |
| resolution rate (%) | 89.51 |
| binomial standard error (pp) | 1.88 |

uncached input = 18963277 - 17507646 = 1455631; counted tokens = 1455631 + 516757 + 442910 = 2415298; per trial 2415298 / 267 = **9046.0599**.

compute_flops = 9046.0599 x 2e+11 = **1.80921e+15**.

Treating the share the published hit rate says missed cache as fresh gives 9479.4445 tokens per trial instead, 4.8% higher; the row takes the straightforward figure and states this in notes.

ai_cost_usd = **0.11992** per trial, `list_price` at the rates Artificial Analysis publishes for this model, dated 2026-09-13 because the board gives no run date. Ratio to the human baseline 0.895, so `match`. Attention term 0.05-0.11x the parameter-only value, since folded into `compute_flops`.

### agen-tbench21-aa-gpt56terra

Artificial Analysis model slug `gpt-5-6-terra` (GPT-5.6 Terra (max), OpenAI), Terminus 2 in an e2b sandbox, 3 repeats of each of the 89 tasks.

| Input | Value |
|---|---|
| trials | 267 |
| input tokens (gross) | 74758292 |
| cacheable input tokens (excluded) | 71665427 |
| answer tokens | 799505 |
| reasoning tokens | 1522272 |
| published cache hit rate | 0.993391 |
| resolution rate (%) | 88.01 |
| binomial standard error (pp) | 1.99 |

uncached input = 74758292 - 71665427 = 3092865; counted tokens = 3092865 + 799505 + 1522272 = 5414642; per trial 5414642 / 267 = **20279.5581**.

compute_flops = 20279.5581 x 4e+10 = **8.11182e+14**.

Treating the share the published hit rate says missed cache as fresh gives 22053.5653 tokens per trial instead, 8.7% higher; the row takes the straightforward figure and states this in notes.

ai_cost_usd = **0.18120** per trial, `list_price` at the rates Artificial Analysis publishes for this model, dated 2026-09-13 because the board gives no run date. Ratio to the human baseline 0.880, so `match`. Attention term 0.13-0.30x the parameter-only value, since folded into `compute_flops`.

### agen-tbench21-aa-gpt6astra

Artificial Analysis model slug `gpt-6-astra` (GPT-6 Astra (max), OpenAI), Terminus 2 in an e2b sandbox, 3 repeats of each of the 89 tasks.

| Input | Value |
|---|---|
| trials | 267 |
| input tokens (gross) | 19314093 |
| cacheable input tokens (excluded) | 17081564 |
| answer tokens | 454593 |
| reasoning tokens | 755224 |
| published cache hit rate | 0.993391 |
| resolution rate (%) | 88.39 |
| binomial standard error (pp) | 1.96 |

uncached input = 19314093 - 17081564 = 2232529; counted tokens = 2232529 + 454593 + 755224 = 3442346; per trial 3442346 / 267 = **12892.6816**.

compute_flops = 12892.6816 x 6e+11 = **7.73561e+15**.

Treating the share the published hit rate says missed cache as fresh gives 13315.5190 tokens per trial instead, 3.3% higher; the row takes the straightforward figure and states this in notes.

ai_cost_usd = **0.37415** per trial, `list_price` at the rates Artificial Analysis publishes for this model, dated 2026-09-13 because the board gives no run date. Ratio to the human baseline 0.884, so `match`. Attention term 0.02-0.05x the parameter-only value, since folded into `compute_flops`.

### agen-tbench21-aa-gpt6astra-high

Artificial Analysis model slug `gpt-6-astra-high` (GPT-6 Astra (high), OpenAI), Terminus 2 in an e2b sandbox, 3 repeats of each of the 89 tasks.

| Input | Value |
|---|---|
| trials | 267 |
| input tokens (gross) | 13715507 |
| cacheable input tokens (excluded) | 12237045 |
| answer tokens | 362929 |
| reasoning tokens | 152128 |
| published cache hit rate | 0.993391 |
| resolution rate (%) | 89.89 |
| binomial standard error (pp) | 1.85 |

uncached input = 13715507 - 12237045 = 1478462; counted tokens = 1478462 + 362929 + 152128 = 1993519; per trial 1993519 / 267 = **7466.3633**.

compute_flops = 7466.3633 x 6e+11 = **4.47982e+15**.

Treating the share the published hit rate says missed cache as fresh gives 7769.2793 tokens per trial instead, 4.1% higher; the row takes the straightforward figure and states this in notes.

ai_cost_usd = **0.19766** per trial, `list_price` at the rates Artificial Analysis publishes for this model, dated 2026-09-13 because the board gives no run date. Ratio to the human baseline 0.899, so `match`. Attention term 0.01-0.03x the parameter-only value, since folded into `compute_flops`.

### agen-tbench21-aa-gpt6astra-medium

Artificial Analysis model slug `gpt-6-astra-medium` (GPT-6 Astra (medium), OpenAI), Terminus 2 in an e2b sandbox, 3 repeats of each of the 89 tasks.

| Input | Value |
|---|---|
| trials | 267 |
| input tokens (gross) | 10383185 |
| cacheable input tokens (excluded) | 9259654 |
| answer tokens | 266121 |
| reasoning tokens | 55816 |
| published cache hit rate | 0.993391 |
| resolution rate (%) | 89.51 |
| binomial standard error (pp) | 1.88 |

uncached input = 10383185 - 9259654 = 1123531; counted tokens = 1123531 + 266121 + 55816 = 1445468; per trial 1445468 / 267 = **5413.7378**.

compute_flops = 5413.7378 x 6e+11 = **3.24824e+15**.

Treating the share the published hit rate says missed cache as fresh gives 5642.9515 tokens per trial instead, 4.2% higher; the row takes the straightforward figure and states this in notes.

ai_cost_usd = **0.13705** per trial, `list_price` at the rates Artificial Analysis publishes for this model, dated 2026-09-13 because the board gives no run date. Ratio to the human baseline 0.895, so `match`. Attention term 0.01-0.02x the parameter-only value, since folded into `compute_flops`.

### agen-tbench21-aa-grok46

Artificial Analysis model slug `grok-4-6` (Grok 4.6 (high), SpaceXAI), Terminus 2 in an e2b sandbox, 3 repeats of each of the 89 tasks.

| Input | Value |
|---|---|
| trials | 267 |
| input tokens (gross) | 75473643 |
| cacheable input tokens (excluded) | 73850969 |
| answer tokens | 697912 |
| reasoning tokens | 992376 |
| published cache hit rate | 0.803561 |
| resolution rate (%) | 88.39 |
| binomial standard error (pp) | 1.96 |

uncached input = 75473643 - 73850969 = 1622674; counted tokens = 1622674 + 697912 + 992376 = 3312962; per trial 3312962 / 267 = **12408.0974**.

compute_flops = 12408.0974 x 2e+11 = **2.48162e+15**.

Treating the share the published hit rate says missed cache as fresh gives 66742.2574 tokens per trial instead, 437.9% higher; the row takes the straightforward figure and states this in notes.

ai_cost_usd = **0.18844** per trial, `list_price` at the rates Artificial Analysis publishes for this model, dated 2026-09-13 because the board gives no run date. Ratio to the human baseline 0.884, so `match`. Attention term 0.07-0.15x the parameter-only value, since folded into `compute_flops`.

### agen-tbench21-aa-inkling

Artificial Analysis model slug `inkling` (Inkling (xhigh), Thinking Machines), Terminus 2 in an e2b sandbox, 3 repeats of each of the 89 tasks.

| Input | Value |
|---|---|
| trials | 267 |
| input tokens (gross) | 293498254 |
| cacheable input tokens (excluded) | 287208629 |
| answer tokens | 975098 |
| reasoning tokens | 3036939 |
| published cache hit rate | 0.980942 |
| resolution rate (%) | 55.06 |
| binomial standard error (pp) | 3.04 |

uncached input = 293498254 - 287208629 = 6289625; counted tokens = 6289625 + 975098 + 3036939 = 10301662; per trial 10301662 / 267 = **38583.0037**.

compute_flops = 38583.0037 x 8.2e+10 = **3.16381e+15**.

Treating the share the published hit rate says missed cache as fresh gives 59083.9145 tokens per trial instead, 53.1% higher; the row takes the straightforward figure and states this in notes.

ai_cost_usd = **0.26728** per trial, `list_price` at the rates Artificial Analysis publishes for this model, dated 2026-09-13 because the board gives no run date. Ratio to the human baseline 0.551, so `below`. Attention term 0.28-0.49x the parameter-only value, since folded into `compute_flops`.

### agen-tbench21-aa-k2horizon

Artificial Analysis model slug `k2-horizon-375b-a23b` (K2 Horizon 375B A23B, MBZUAI Institute of Foundation Models), Terminus 2 in an e2b sandbox, 3 repeats of each of the 89 tasks.

| Input | Value |
|---|---|
| trials | 267 |
| input tokens (gross) | 117207453 |
| cacheable input tokens (excluded) | 112772864 |
| answer tokens | 662052 |
| reasoning tokens | 2645343 |
| published cache hit rate | not published |
| resolution rate (%) | 71.91 |
| binomial standard error (pp) | 2.75 |

uncached input = 117207453 - 112772864 = 4434589; counted tokens = 4434589 + 662052 + 2645343 = 7741984; per trial 7741984 / 267 = **28996.1948**.

compute_flops = 28996.1948 x 4.6e+10 = **1.33382e+15**.

The board publishes no price fields for this model, so the cost columns are empty and `ai_cost_basis` is `not_available`. Ratio to the human baseline 0.719, so `below`. Attention term 0.17-0.37x the parameter-only value, since folded into `compute_flops`.

### agen-tbench21-aa-kimik3

Artificial Analysis model slug `kimi-k3` (Kimi K3 (max), Kimi), Terminus 2 in an e2b sandbox, 3 repeats of each of the 89 tasks.

| Input | Value |
|---|---|
| trials | 267 |
| input tokens (gross) | 52251794 |
| cacheable input tokens (excluded) | 49461474 |
| answer tokens | 525087 |
| reasoning tokens | 1420531 |
| published cache hit rate | 0.974396 |
| resolution rate (%) | 85.02 |
| binomial standard error (pp) | 2.18 |

uncached input = 52251794 - 49461474 = 2790320; counted tokens = 2790320 + 525087 + 1420531 = 4735938; per trial 4735938 / 267 = **17737.5955**.

compute_flops = 17737.5955 x 2.08e+11 = **3.68942e+15**.

Treating the share the published hit rate says missed cache as fresh gives 22480.6900 tokens per trial instead, 26.7% higher; the row takes the straightforward figure and states this in notes.

ai_cost_usd = **0.19623** per trial, `list_price` at the rates Artificial Analysis publishes for this model, dated 2026-09-13 because the board gives no run date. Ratio to the human baseline 0.850, so `match`. Attention term 0.09-0.20x the parameter-only value, since folded into `compute_flops`.

### agen-tbench21-aa-minimaxm3

Artificial Analysis model slug `minimax-m3` (MiniMax-M3, MiniMax), Terminus 2 in an e2b sandbox, 3 repeats of each of the 89 tasks.

| Input | Value |
|---|---|
| trials | 267 |
| input tokens (gross) | 281325850 |
| cacheable input tokens (excluded) | 276103980 |
| answer tokens | 3066162 |
| reasoning tokens | 399338 |
| published cache hit rate | 0.972845 |
| resolution rate (%) | 65.17 |
| binomial standard error (pp) | 2.92 |

uncached input = 281325850 - 276103980 = 5221870; counted tokens = 5221870 + 3066162 + 399338 = 8687370; per trial 8687370 / 267 = **32536.9663**.

compute_flops = 32536.9663 x 4.6e+10 = **1.4967e+15**.

Treating the share the published hit rate says missed cache as fresh gives 60618.1701 tokens per trial instead, 86.3% higher; the row takes the straightforward figure and states this in notes.

ai_cost_usd = **0.08349** per trial, `list_price` at the rates Artificial Analysis publishes for this model, dated 2026-09-13 because the board gives no run date. Ratio to the human baseline 0.652, so `below`. Attention term 0.19-0.42x the parameter-only value, since folded into `compute_flops`.

### agen-tbench21-aa-mistralmedium35

Artificial Analysis model slug `mistral-medium-3-5` (Mistral Medium 3.5, Mistral), Terminus 2 in an e2b sandbox, 3 repeats of each of the 89 tasks.

| Input | Value |
|---|---|
| trials | 267 |
| input tokens (gross) | 229329980 |
| cacheable input tokens (excluded) | 219906575 |
| answer tokens | 1986783 |
| reasoning tokens | 4295853 |
| published cache hit rate | 0.956079 |
| resolution rate (%) | 50.56 |
| binomial standard error (pp) | 3.06 |

uncached input = 229329980 - 219906575 = 9423405; counted tokens = 9423405 + 1986783 + 4295853 = 15706041; per trial 15706041 / 267 = **58824.1236**.

compute_flops = 58824.1236 x 2.56e+11 = **1.5059e+16**.

Treating the share the published hit rate says missed cache as fresh gives 94998.6400 tokens per trial instead, 61.5% higher; the row takes the straightforward figure and states this in notes.

ai_cost_usd = **0.35296** per trial, `list_price` at the rates Artificial Analysis publishes for this model, dated 2026-09-13 because the board gives no run date. Ratio to the human baseline 0.506, so `below`. Attention term 0.24-0.54x the parameter-only value, since folded into `compute_flops`.

### agen-tbench21-aa-museglimmer

Artificial Analysis model slug `muse-glimmer` (Muse Glimmer (high), Meta), Terminus 2 in an e2b sandbox, 3 repeats of each of the 89 tasks.

| Input | Value |
|---|---|
| trials | 267 |
| input tokens (gross) | 192462978 |
| cacheable input tokens (excluded) | 191108562 |
| answer tokens | 807120 |
| reasoning tokens | 1506118 |
| published cache hit rate | 1.000000 |
| resolution rate (%) | 51.69 |
| binomial standard error (pp) | 3.06 |

uncached input = 192462978 - 191108562 = 1354416; counted tokens = 1354416 + 807120 + 1506118 = 3667654; per trial 3667654 / 267 = **13736.5318**.

compute_flops = 13736.5318 x 6e+10 = **8.24192e+14**.

Treating the share the published hit rate says missed cache as fresh gives 13736.5318 tokens per trial instead, 0.0% higher; the row takes the straightforward figure and states this in notes.

ai_cost_usd = **0.04340** per trial, `list_price` at the rates Artificial Analysis publishes for this model, dated 2026-09-13 because the board gives no run date. Ratio to the human baseline 0.517, so `below`. Attention term 0.14-0.24x the parameter-only value, since folded into `compute_flops`.

### agen-tbench21-aa-musespark13

Artificial Analysis model slug `muse-spark-1-3` (Muse Spark 1.3 (max), Meta), Terminus 2 in an e2b sandbox, 3 repeats of each of the 89 tasks.

| Input | Value |
|---|---|
| trials | 267 |
| input tokens (gross) | 278381178 |
| cacheable input tokens (excluded) | 271190060 |
| answer tokens | 1206180 |
| reasoning tokens | 3042293 |
| published cache hit rate | 0.950000 |
| resolution rate (%) | 84.27 |
| binomial standard error (pp) | 2.23 |

uncached input = 278381178 - 271190060 = 7191118; counted tokens = 7191118 + 1206180 + 3042293 = 11439591; per trial 11439591 / 267 = **42844.9101**.

compute_flops = 42844.9101 x 2e+11 = **8.56898e+15**.

Treating the share the published hit rate says missed cache as fresh gives 93629.5655 tokens per trial instead, 118.5% higher; the row takes the straightforward figure and states this in notes.

ai_cost_usd = **0.25365** per trial, `list_price` at the rates Artificial Analysis publishes for this model, dated 2026-09-13 because the board gives no run date. Ratio to the human baseline 0.843, so `below`. Attention term 0.22-0.51x the parameter-only value, since folded into `compute_flops`.

### agen-tbench21-aa-nemotron3ultra

Artificial Analysis model slug `nvidia-nemotron-3-ultra-550b-a55b` (Nemotron 3 Ultra 550B A55B (Reasoning), NVIDIA), Terminus 2 in an e2b sandbox, 3 repeats of each of the 89 tasks.

| Input | Value |
|---|---|
| trials | 267 |
| input tokens (gross) | 152970037 |
| cacheable input tokens (excluded) | 149511031 |
| answer tokens | 1578501 |
| reasoning tokens | 1693522 |
| published cache hit rate | 0.328126 |
| resolution rate (%) | 53.93 |
| binomial standard error (pp) | 3.05 |

uncached input = 152970037 - 149511031 = 3459006; counted tokens = 3459006 + 1578501 + 1693522 = 6731029; per trial 6731029 / 267 = **25209.8464**.

compute_flops = 25209.8464 x 1.1e+11 = **2.77308e+15**.

Treating the share the published hit rate says missed cache as fresh gives 401436.5761 tokens per trial instead, 1492.4% higher; the row takes the straightforward figure and states this in notes.

ai_cost_usd = **0.15163** per trial, `list_price` at the rates Artificial Analysis publishes for this model, dated 2026-09-13 because the board gives no run date. Ratio to the human baseline 0.539, so `below`. Attention term 0.14-0.24x the parameter-only value, since folded into `compute_flops`.

### agen-tbench21-aa-opus5

Artificial Analysis model slug `claude-opus-5` (Claude Opus 5 (Adaptive Reasoning, Max Effort), Anthropic), Terminus 2 in an e2b sandbox, 3 repeats of each of the 89 tasks.

| Input | Value |
|---|---|
| trials | 267 |
| input tokens (gross) | 132353877 |
| cacheable input tokens (excluded) | 126095036 |
| answer tokens | 1333842 |
| reasoning tokens | 3102688 |
| published cache hit rate | 0.996663 |
| resolution rate (%) | 89.14 |
| binomial standard error (pp) | 1.90 |

uncached input = 132353877 - 126095036 = 6258841; counted tokens = 6258841 + 1333842 + 3102688 = 10695371; per trial 10695371 / 267 = **40057.5693**.

compute_flops = 40057.5693 x 2e+11 = **8.01151e+15**.

Treating the share the published hit rate says missed cache as fresh gives 41633.3299 tokens per trial instead, 3.9% higher; the row takes the straightforward figure and states this in notes.

ai_cost_usd = **0.76875** per trial, `list_price` at the rates Artificial Analysis publishes for this model, dated 2026-09-13 because the board gives no run date. Ratio to the human baseline 0.891, so `match`. Attention term 0.21-0.47x the parameter-only value, since folded into `compute_flops`.

### agen-tbench21-aa-qwen3827b

Artificial Analysis model slug `qwen3-8-27b` (Qwen3.8 27B (xhigh), Alibaba), Terminus 2 in an e2b sandbox, 3 repeats of each of the 89 tasks.

| Input | Value |
|---|---|
| trials | 267 |
| input tokens (gross) | 244264574 |
| cacheable input tokens (excluded) | 233189640 |
| answer tokens | 1357477 |
| reasoning tokens | 4654402 |
| published cache hit rate | 0.830000 |
| resolution rate (%) | 79.78 |
| binomial standard error (pp) | 2.46 |

uncached input = 244264574 - 233189640 = 11074934; counted tokens = 11074934 + 1357477 + 4654402 = 17086813; per trial 17086813 / 267 = **63995.5543**.

compute_flops = 63995.5543 x 5.4e+10 = **3.45576e+15**.

Treating the share the published hit rate says missed cache as fresh gives 212468.3588 tokens per trial instead, 232.0% higher; the row takes the straightforward figure and states this in notes.

ai_cost_usd = **0.13196** per trial, `list_price` at the rates Artificial Analysis publishes for this model, dated 2026-09-13 because the board gives no run date. Ratio to the human baseline 0.798, so `below`. Attention term 0.31-0.70x the parameter-only value, since folded into `compute_flops`.

### agen-tbench21-aa-qwen38max

Artificial Analysis model slug `qwen3-8-2-4t-a95b` (Qwen3.8 2.4T A95B, Alibaba), Terminus 2 in an e2b sandbox, 3 repeats of each of the 89 tasks.

| Input | Value |
|---|---|
| trials | 267 |
| input tokens (gross) | 109664633 |
| cacheable input tokens (excluded) | 104828681 |
| answer tokens | 889247 |
| reasoning tokens | 2441444 |
| published cache hit rate | 0.967788 |
| resolution rate (%) | 82.02 |
| binomial standard error (pp) | 2.35 |

uncached input = 109664633 - 104828681 = 4835952; counted tokens = 4835952 + 889247 + 2441444 = 8166643; per trial 8166643 / 267 = **30586.6779**.

compute_flops = 30586.6779 x 1.9e+11 = **5.81147e+15**.

Treating the share the published hit rate says missed cache as fresh gives 43233.7807 tokens per trial instead, 41.3% higher; the row takes the straightforward figure and states this in notes.

ai_cost_usd = **0.20923** per trial, `list_price` at the rates Artificial Analysis publishes for this model, dated 2026-09-13 because the board gives no run date. Ratio to the human baseline 0.820, so `below`. Attention term 0.09-0.17x the parameter-only value, since folded into `compute_flops`.

### agen-tbench21-fable5-claudecode

Fable 5 under Claude Code 2.1.167 at reasoning effort xhigh, submitted 2026-06-07 in PR #75 (`2026-06-07-anthropic-claude-fable-5-xhigh-claude-code.json`).

| Input | Value |
|---|---|
| trials | 445 |
| uncached input tokens | 20480925 |
| cached input tokens (excluded) | 174066133 |
| output tokens | 9954945 |
| reported total cost (USD) | 552.67 |
| resolution rate (%) | 83.82 |
| standard error (pp) | 1.16 |
| disqualified trials | 1 |
| mean trial duration (s) | 579.7 |

counted tokens = 20480925 + 9954945 = 30435870; per trial 30435870 / 445 = **68395.2135**.

compute_flops = 68395.2135 x 3e+11 = **2.05186e+16**.

ai_cost_usd = 552.67 / 445 = **1.24196**, `reported`, dated 2026-06-07.

Cache structure: cached input is 8.50 times uncached input, and uncached input is 2.06 times output. Ratio to the human baseline 0.838, so `below` on the 0.85 to 1.15 match band. Attention term 0.24-0.54x the parameter-only value, since folded into `compute_flops`.

### agen-tbench21-fable5-terminus2

Fable 5 under Terminus 2 2.0.0 at reasoning effort high, submitted 2026-06-05 in PR #78 (`2026-06-05-anthropic-claude-fable-5-high-terminus-2.json`).

| Input | Value |
|---|---|
| trials | 445 |
| uncached input tokens | 7874199 |
| cached input tokens (excluded) | 56146091 |
| output tokens | 7412519 |
| reported total cost (USD) | 438.64 |
| resolution rate (%) | 80.45 |
| standard error (pp) | 1.16 |
| disqualified trials | 0 |
| mean trial duration (s) | 697.1 |

counted tokens = 7874199 + 7412519 = 15286718; per trial 15286718 / 445 = **34352.1753**.

compute_flops = 34352.1753 x 3e+11 = **1.03057e+16**.

ai_cost_usd = 438.64 / 445 = **0.98571**, `reported`, dated 2026-06-05.

Cache structure: cached input is 7.13 times uncached input, and uncached input is 1.06 times output. Ratio to the human baseline 0.804, so `below` on the 0.85 to 1.15 match band. Attention term 0.12-0.27x the parameter-only value, since folded into `compute_flops`.

### agen-tbench21-gemini31pro-geminicli

Gemini 3.1 Pro under Gemini CLI 0.40.0 at reasoning effort high, submitted 2026-05-05 in PR #68 (`2026-05-05-gemini-gemini-3-1-pro-preview-high-gemini-cli.json`).

| Input | Value |
|---|---|
| trials | 445 |
| uncached input tokens | 44843158 |
| cached input tokens (excluded) | 366583353 |
| output tokens | 6123596 |
| reported total cost (USD) | 236.49 |
| resolution rate (%) | 65.84 |
| standard error (pp) | 1.67 |
| disqualified trials | 1 |
| mean trial duration (s) | 652.9 |

counted tokens = 44843158 + 6123596 = 50966754; per trial 50966754 / 445 = **114532.0315**.

compute_flops = 114532.0315 x 2e+11 = **2.29064e+16**.

ai_cost_usd = 236.49 / 445 = **0.53144**, `reported`, dated 2026-05-05.

Cache structure: cached input is 8.17 times uncached input, and uncached input is 7.32 times output. Ratio to the human baseline 0.658, so `below` on the 0.85 to 1.15 match band. Attention term 0.60-1.35x the parameter-only value, since folded into `compute_flops`.

### agen-tbench21-gemini31pro-terminus2

Gemini 3.1 Pro under Terminus 2 2.0.0 at reasoning effort high, submitted 2026-05-05 in PR #69 (`2026-05-05-gemini-gemini-3-1-pro-preview-high-terminus-2.json`).

| Input | Value |
|---|---|
| trials | 445 |
| uncached input tokens | 27525560 |
| cached input tokens (excluded) | 96199940 |
| output tokens | 12935831 |
| reported total cost (USD) | 229.99 |
| resolution rate (%) | 65.62 |
| standard error (pp) | 1.65 |
| disqualified trials | 2 |
| mean trial duration (s) | 672.8 |

counted tokens = 27525560 + 12935831 = 40461391; per trial 40461391 / 445 = **90924.4742**.

compute_flops = 90924.4742 x 2e+11 = **1.81849e+16**.

ai_cost_usd = 229.99 / 445 = **0.51683**, `reported`, dated 2026-05-05.

Cache structure: cached input is 3.49 times uncached input, and uncached input is 2.13 times output. Ratio to the human baseline 0.656, so `below` on the 0.85 to 1.15 match band. Attention term 0.48-1.07x the parameter-only value, since folded into `compute_flops`.

### agen-tbench21-gemini3pro-geminicli

Gemini 3 Pro under Gemini CLI 0.40.0 at reasoning effort high, submitted 2026-05-01 in PR #66 (`2026-05-01-gemini-gemini-3-pro-preview-high-gemini-cli.json`).

| Input | Value |
|---|---|
| trials | 445 |
| uncached input tokens | 47653156 |
| cached input tokens (excluded) | 329123284 |
| output tokens | 7219388 |
| reported total cost (USD) | 247.76 |
| resolution rate (%) | 65.84 |
| standard error (pp) | 1.38 |
| disqualified trials | 2 |
| mean trial duration (s) | 436.6 |

counted tokens = 47653156 + 7219388 = 54872544; per trial 54872544 / 445 = **123309.0876**.

compute_flops = 123309.0876 x 2e+11 = **2.46618e+16**.

ai_cost_usd = 247.76 / 445 = **0.55676**, `reported`, dated 2026-05-01.

Cache structure: cached input is 6.91 times uncached input, and uncached input is 6.60 times output. Ratio to the human baseline 0.658, so `below` on the 0.85 to 1.15 match band. Attention term 0.65-1.45x the parameter-only value, since folded into `compute_flops`.

### agen-tbench21-gemini3pro-terminus2

Gemini 3 Pro under Terminus 2 2.0.0 at reasoning effort high, submitted 2026-05-01 in PR #48 (`2026-05-01-gemini-gemini-3-pro-preview-high-terminus-2.json`).

| Input | Value |
|---|---|
| trials | 445 |
| uncached input tokens | 26094316 |
| cached input tokens (excluded) | 89495525 |
| output tokens | 12862730 |
| reported total cost (USD) | 224.44 |
| resolution rate (%) | 73.93 |
| standard error (pp) | 1.29 |
| disqualified trials | 2 |
| mean trial duration (s) | 547.8 |

counted tokens = 26094316 + 12862730 = 38957046; per trial 38957046 / 445 = **87543.9236**.

compute_flops = 87543.9236 x 2e+11 = **1.75088e+16**.

ai_cost_usd = 224.44 / 445 = **0.50436**, `reported`, dated 2026-05-01.

Cache structure: cached input is 3.43 times uncached input, and uncached input is 2.03 times output. Ratio to the human baseline 0.739, so `below` on the 0.85 to 1.15 match band. Attention term 0.46-1.03x the parameter-only value, since folded into `compute_flops`.

### agen-tbench21-glm51-claudecode

GLM-5.1 under Claude Code 2.1.123 at reasoning effort max, submitted 2026-05-01 in PR #67 (`2026-05-01-glm-5-1-max-claude-code.json`).

| Input | Value |
|---|---|
| trials | 445 |
| uncached input tokens | 13570352 |
| cached input tokens (excluded) | 374577728 |
| output tokens | 10635681 |
| reported total cost (USD) | 277.14 |
| resolution rate (%) | 58.65 |
| standard error (pp) | 1.24 |
| disqualified trials | 0 |
| mean trial duration (s) | 944.6 |

counted tokens = 13570352 + 10635681 = 24206033; per trial 24206033 / 445 = **54395.5798**.

compute_flops = 54395.5798 x 8e+10 = **4.35165e+15**.

ai_cost_usd = 277.14 / 445 = **0.62279**, `reported`, dated 2026-05-01.

Cache structure: cached input is 27.60 times uncached input, and uncached input is 1.28 times output. Ratio to the human baseline 0.587, so `below` on the 0.85 to 1.15 match band. Attention term 0.40-0.71x the parameter-only value, since folded into `compute_flops`.

### agen-tbench21-gpt55-codex

GPT-5.5 under Codex 0.125.0 at reasoning effort xhigh, submitted 2026-05-01 in PR #45 (`2026-05-01-openai-gpt-5-5-xhigh-codex.json`).

| Input | Value |
|---|---|
| trials | 445 |
| uncached input tokens | 336797311 |
| cached input tokens (excluded) | 392433664 |
| output tokens | 5966373 |
| reported total cost (USD) | 2059.19 |
| resolution rate (%) | 83.15 |
| standard error (pp) | 1.13 |
| disqualified trials | 1 |
| mean trial duration (s) | 482.6 |

counted tokens = 336797311 + 5966373 = 342763684; per trial 342763684 / 445 = **770255.4697**.

compute_flops = 770255.4697 x 3.46e+11 = **2.66508e+17**.

ai_cost_usd = 2059.19 / 445 = **4.62739**, `reported`, dated 2026-05-01.

Cache structure: cached input is 1.17 times uncached input, and uncached input is 56.45 times output. Ratio to the human baseline 0.832, so `below` on the 0.85 to 1.15 match band. Attention term 2.33-5.25x the parameter-only value, since folded into `compute_flops`.

### agen-tbench21-gpt56luna-codex

GPT-5.6 Luna under Codex 0.144.1 at reasoning effort max, submitted 2026-07-11 in PR #112 (`2026-07-11-openai-gpt-5-6-luna-max-codex.json`).

| Input | Value |
|---|---|
| trials | 445 |
| uncached input tokens | 40023670 |
| cached input tokens (excluded) | 1376567117 |
| output tokens | 10628905 |
| reported total cost (USD) | 241.45 |
| resolution rate (%) | 75.73 |
| standard error (pp) | 1.32 |
| disqualified trials | 4 |
| mean trial duration (s) | 457.3 |

counted tokens = 40023670 + 10628905 = 50652575; per trial 50652575 / 445 = **113826.0112**.

compute_flops = 113826.0112 x 1.6e+10 = **1.82122e+15**.

ai_cost_usd = 241.45 / 445 = **0.54258**, `reported`, dated 2026-07-11.

Cache structure: cached input is 34.39 times uncached input, and uncached input is 3.77 times output. Ratio to the human baseline 0.757, so `below` on the 0.85 to 1.15 match band. Attention term 1.86-4.20x the parameter-only value, since folded into `compute_flops`.

### agen-tbench21-gpt56sol-codex

GPT-5.6 Sol under Codex 0.144.0 at reasoning effort max, submitted 2026-07-10 in PR #102 (`2026-07-10-gpt-5-6-sol-max-codex.json`).

| Input | Value |
|---|---|
| trials | 445 |
| uncached input tokens | 25266704 |
| cached input tokens (excluded) | 540552541 |
| output tokens | 5935747 |
| reported total cost (USD) | 574.68 |
| resolution rate (%) | 76.18 |
| standard error (pp) | 1.28 |
| disqualified trials | 32 |
| mean trial duration (s) | 431.0 |

counted tokens = 25266704 + 5935747 = 31202451; per trial 31202451 / 445 = **70117.8674**.

compute_flops = 70117.8674 x 2e+11 = **1.40236e+16**.

ai_cost_usd = 574.68 / 445 = **1.29142**, `reported`, dated 2026-07-10.

Cache structure: cached input is 21.39 times uncached input, and uncached input is 4.26 times output. Ratio to the human baseline 0.762, so `below` on the 0.85 to 1.15 match band. Attention term 0.37-0.83x the parameter-only value, since folded into `compute_flops`.

### agen-tbench21-gpt56terra-codex

GPT-5.6 Terra under Codex 0.144.1 at reasoning effort max, submitted 2026-07-11 in PR #115 (`2026-07-11-openai-gpt-5-6-terra-max-codex.json`).

| Input | Value |
|---|---|
| trials | 445 |
| uncached input tokens | 29803660 |
| cached input tokens (excluded) | 864130644 |
| output tokens | 8707506 |
| reported total cost (USD) | 421.15 |
| resolution rate (%) | 78.43 |
| standard error (pp) | 1.25 |
| disqualified trials | 1 |
| mean trial duration (s) | 432.8 |

counted tokens = 29803660 + 8707506 = 38511166; per trial 38511166 / 445 = **86541.9461**.

compute_flops = 86541.9461 x 4e+10 = **3.46168e+15**.

ai_cost_usd = 421.15 / 445 = **0.94640**, `reported`, dated 2026-07-11.

Cache structure: cached input is 28.99 times uncached input, and uncached input is 3.42 times output. Ratio to the human baseline 0.784, so `below` on the 0.85 to 1.15 match band. Attention term 0.57-1.28x the parameter-only value, since folded into `compute_flops`.

### agen-tbench21-grok45-cursorcli

Grok 4.5 under Cursor CLI 2026.07.08-0c04a8a at reasoning effort high, submitted 2026-07-09 in PR #86 (`2026-07-09-cursor-grok-4-5-none-cursor-cli.json`).

| Input | Value |
|---|---|
| trials | 445 |
| uncached input tokens | 12570445 |
| cached input tokens (excluded) | 161079936 |
| output tokens | 4734062 |
| reported total cost (USD) | 134.09 |
| resolution rate (%) | 79.33 |
| standard error (pp) | 1.46 |
| disqualified trials | 40 |
| mean trial duration (s) | 443.0 |

counted tokens = 12570445 + 4734062 = 17304507; per trial 17304507 / 445 = **38886.5326**.

compute_flops = 38886.5326 x 2e+11 = **7.77731e+15**.

ai_cost_usd = 134.09 / 445 = **0.30133**, `reported`, dated 2026-07-09.

Cache structure: cached input is 12.81 times uncached input, and uncached input is 2.66 times output. Ratio to the human baseline 0.793, so `below` on the 0.85 to 1.15 match band. Attention term 0.20-0.46x the parameter-only value, since folded into `compute_flops`.

### agen-tbench21-opus47-claudecode

Opus 4.7 under Claude Code 2.1.123 at reasoning effort max, submitted 2026-05-01 in PR #44 (`2026-05-01-anthropic-claude-opus-4-7-max-claude-code.json`).

| Input | Value |
|---|---|
| trials | 447 |
| uncached input tokens | 31873388 |
| cached input tokens (excluded) | 806584422 |
| output tokens | 14896548 |
| reported total cost (USD) | 599.52 |
| resolution rate (%) | 68.90 |
| standard error (pp) | 1.41 |
| disqualified trials | 2 |
| mean trial duration (s) | 799.6 |

counted tokens = 31873388 + 14896548 = 46769936; per trial 46769936 / 447 = **104630.7293**.

compute_flops = 104630.7293 x 2e+11 = **2.09261e+16**.

ai_cost_usd = 599.52 / 447 = **1.34121**, `reported`, dated 2026-05-01.

Cache structure: cached input is 25.31 times uncached input, and uncached input is 2.14 times output. Ratio to the human baseline 0.689, so `below` on the 0.85 to 1.15 match band. Attention term 0.55-1.23x the parameter-only value, since folded into `compute_flops`.

### agen-tbench21-opus47-terminus2

Opus 4.7 under Terminus 2 2.0.0 at reasoning effort max, submitted 2026-05-01 in PR #46 (`2026-05-01-anthropic-claude-opus-4-7-max-terminus-2.json`).

| Input | Value |
|---|---|
| trials | 445 |
| uncached input tokens | 16646631 |
| cached input tokens (excluded) | 336161721 |
| output tokens | 12451178 |
| reported total cost (USD) | 582.26 |
| resolution rate (%) | 66.07 |
| standard error (pp) | 1.37 |
| disqualified trials | 0 |
| mean trial duration (s) | 1042.7 |

counted tokens = 16646631 + 12451178 = 29097809; per trial 29097809 / 445 = **65388.3348**.

compute_flops = 65388.3348 x 2e+11 = **1.30777e+16**.

ai_cost_usd = 582.26 / 445 = **1.30845**, `reported`, dated 2026-05-01.

Cache structure: cached input is 20.19 times uncached input, and uncached input is 1.34 times output. Ratio to the human baseline 0.661, so `below` on the 0.85 to 1.15 match band. Attention term 0.34-0.77x the parameter-only value, since folded into `compute_flops`.

### agen-tbench21-opus48-claudecode

Opus 4.8 under Claude Code 2.1.205 at reasoning effort high, submitted 2026-07-09 in PR #92 (`2026-07-09-anthropic-claude-opus-4-8-high-claude-code.json`).

| Input | Value |
|---|---|
| trials | 445 |
| uncached input tokens | 12873472 |
| cached input tokens (excluded) | 161931526 |
| output tokens | 8089069 |
| reported total cost (USD) | 286.94 |
| resolution rate (%) | 78.88 |
| standard error (pp) | 1.31 |
| disqualified trials | 0 |
| mean trial duration (s) | 551.4 |

counted tokens = 12873472 + 8089069 = 20962541; per trial 20962541 / 445 = **47106.8337**.

compute_flops = 47106.8337 x 2e+11 = **9.42137e+15**.

ai_cost_usd = 286.94 / 445 = **0.64481**, `reported`, dated 2026-07-09.

Cache structure: cached input is 12.58 times uncached input, and uncached input is 1.59 times output. Ratio to the human baseline 0.789, so `below` on the 0.85 to 1.15 match band. Attention term 0.25-0.56x the parameter-only value, since folded into `compute_flops`.

### agen-tbench21-sonnet5-claudecode

Sonnet 5 under Claude Code 2.1.205 at reasoning effort high, submitted 2026-07-09 in PR #98 (`2026-07-09-anthropic-claude-sonnet-5-high-claude-code.json`).

| Input | Value |
|---|---|
| trials | 445 |
| uncached input tokens | 20137729 |
| cached input tokens (excluded) | 527220403 |
| output tokens | 11216322 |
| reported total cost (USD) | 288.18 |
| resolution rate (%) | 74.61 |
| standard error (pp) | 1.64 |
| disqualified trials | 3 |
| mean trial duration (s) | 629.6 |

counted tokens = 20137729 + 11216322 = 31354051; per trial 31354051 / 445 = **70458.5416**.

compute_flops = 70458.5416 x 2e+11 = **1.40917e+16**.

ai_cost_usd = 288.18 / 445 = **0.64760**, `reported`, dated 2026-07-09.

Cache structure: cached input is 26.18 times uncached input, and uncached input is 1.80 times output. Ratio to the human baseline 0.746, so `below` on the 0.85 to 1.15 match band. Attention term 0.37-0.83x the parameter-only value, since folded into `compute_flops`.

### agen-tbsci-gpt6astra-valsai

GPT-6 Astra under Terminus 2 in a fixed configuration on the Vals AI Terminal-Bench-Science 0.1 board, one graded run on each of the 70 tasks, board updated 2026-09-11. Built on the coordinator's 2026-09-13 ruling; reworked in Revision 1 to carry two donor readings of the cache structure. This is the only cell on either Terminal-Bench-Science board that clears the half-of-human guide.

| Input | Value | Source |
|---|---|---|
| tasks resolved | 46 of 70 | Vals AI science board `accuracy` 65.714% |
| cost per task (USD) | 15.795618 | Vals AI science board `cost_per_test` |
| mean latency (s) | 5426.7 | Vals AI science board `latency` |
| list prices (USD per million) | 10.00 input, 1.00 cached, 50.00 output | `research/cost/list-prices.csv`, window opening 2026-09-03 |
| donor uncached input | 2232529 | Artificial Analysis Terminal-Bench v2.1, slug gpt-6-astra |
| donor cache reads | 17081564 | the same record's `cacheableInput` |
| donor output | 1209817 | the same record's `answer` plus `reasoning` |
| same operator, Terminal-Bench 2.1 | $1.339493 per task | Vals AI Terminal-Bench 2.1 board, updated 2026-09-10 |
| mean author expert estimate | 22.187143 h | 70 of 70 `expert_time_estimate_hours` |

**Human time.** All 70 tasks carry an author estimate. Mean 22.1871 h, median 12.0 h, geometric mean 10.318 h, range 1.6 to 600.0 h, total 1553.1 h. 22.187143 h x 3600 = **79873.71 s**. The field is defined as it is in Terminal-Bench 2.1, and the sibling benchmark's contributing guide glosses it as "best-case hours for a focused domain expert", so `source_estimate` and `human_skill = expert`.

**Compute.** The board publishes a dollar figure and no tokens, so

```
cost_per_task = (p_in*U + p_cached*C + p_out*O) / 1e6
```

has three unknowns and needs two ratios: k = U/O and m = C/(U+O). k comes from the same model's Artificial Analysis Terminal-Bench 2.1 record, GPT-6 Astra under the same Terminus 2 harness: 2232529 / 1209817 = **1.8453**. m is the contested one, and two donors give irreconcilable answers.

*Reading A, the Artificial Analysis mix.* That record's own m is 17081564 / 3442346 = **4.9622**.

*Reading B, this operator's own Terminal-Bench 2.1 cell.* Vals runs the same 89 tasks and bills **$1.339493** per task. Artificial Analysis's measured volume for the same model on the same tasks costs **$0.3741** per trial at these rates with the cache discount its own split implies, and **$0.94993** priced gross with no discount at all. Vals therefore bills **3.58x** the discounted figure and **1.41x** the gross one — it is charging more than every token that volume contains would cost at the undiscounted input rate. Requiring Vals' dollars to cover Artificial Analysis's counted tokens puts the missing money on cache reads: m = **79.838**, sixteen times Reading A's.

The published fields do not choose between them. Reading A says Vals simply processes about 3.6x the tokens at the donor's mix, which its own error re-attempts and a longer agent budget would produce; Reading B says Vals' deployment caches far more aggressively or is billed on a different basis. Neither is privileged, so the central is their geometric mean, as DECISIONS requires for cost-inverted compute with a transferred cache structure.

Each reading is itself bracketed on the benchmark-length growth in m. Three models appear on both Terminal-Bench boards, so that growth is measurable:

| Model | m on Terminal-Bench 2.1 | m on Terminal-Bench-Science | growth |
|---|---|---|---|
| GPT-5.6 Sol | 17.32 | 64.01 | 3.695 |
| GPT-5.6 Terra | 22.44 | 66.24 | 2.952 |
| GPT-5.6 Luna | 27.18 | 55.52 | 2.043 |

Geometric mean growth **2.8141** (range 2.04 to 3.69). Each reading is evaluated at its own m and at m times that factor:

| Reading | m | m x g | counted at m | counted at m x g | geometric mean |
|---|---|---|---|---|---|
| A, Artificial Analysis mix | 4.962 | 13.964 | 544297 | 415434 | **475520** |
| B, Vals' own 2.1 cell | 79.838 | 224.668 | 152034 | 63506 | **98260** |

Central: sqrt(475520 x 98260) = **216158.83** counted tokens per task. compute_flops = 216158.83 x 6e+11 = **1.29695e+17**, band 3.810e+16 to 3.266e+17 across all four cells.

**The growth factor is not the sensitive parameter; m is.** Holding Reading A and varying g over a sixfold range moves the result 1.4x: g = 1.00 gives 3.27e+17, g = 2.81 gives 2.85e+17, g = 6.00 gives 2.4e+17. A ten per cent error in the cached rate moves it about five per cent. The two m readings, by contrast, are 4.8x apart in the result. The alarm in the probe section below about a 45x collapse is a property of the probe's single-transfer inversion of the official science board, not of this row.

**Cross-checks.** Artificial Analysis measures GPT-6 Astra and GPT-5.6 Sol within 6% of each other in counted tokens per trial on Terminal-Bench 2.1 (ratio 1.063). Scaling Sol's independently inverted Terminal-Bench-Science figure by that ratio gives 654742 counted tokens per task, but Sol ran under Codex; the four official pairs that run one model under both Terminus 2 and its own lab's CLI put a Terminus 2 run at 0.625 (Opus 4.7), 0.502 (Fable 5), 0.710 (Gemini 3 Pro), 0.794 (Gemini 3.1 Pro) of the CLI run, so the reading becomes 328851 to 519785. The central of 216159 sits below that band, which is what Reading B pulls it to. The implied output rate is 4.1 to 35.3 tokens per second against the board's 5427 s mean latency; the low end is Reading B's length-corrected cell and is slow for this model, which is the clearest single argument against that corner.

**Judgments.** `task_category = research_analysis` rather than `coding`: the deliverable is often code, but `COLUMNS.md` asks for the whole task, and the whole task is scientific research work whose binding skill is domain expertise, which is why the benchmark files tasks under astronomy, ocean sciences and neuroscience. Ratio to the human baseline 0.657, below the 0.85 match band, so `below`. `ai_cost_basis = reported`, the board's own figure, but cost and compute are not independent on this row because the compute was inverted from the cost, flagged as the GDPval and Remote Labor Index rows are. Vals re-attempts tasks that end in an infrastructure error and never re-runs a graded result, so the resolution rate is one-sidedly inflated and the runs behind the per-task dollar exceed 70; `ai_attempts` counts the 70 tasks. Attention term 0.38-0.85x the parameter-only value, since folded into `compute_flops`.

