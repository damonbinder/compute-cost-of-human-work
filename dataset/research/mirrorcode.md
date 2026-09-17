# MirrorCode — reimplementing whole programs from behavior alone

*Created 2026-09-13 12:04.*
*Last revised 2026-09-13 12:41, applying the independent review in `reviews/mirrorcode-independent.md`.*

## TL;DR

Thirteen candidate rows from the 19 public MirrorCode run records, covering four target
programs (gotree, pkl, cal, choose) and four Claude Opus generations, at **5.5e16 to 2.9e18
FLOPs** against human estimates of **18 hours to 1,200 hours** of active engineering time.
Compute is measured: every run publishes a complete, additive Anthropic usage block, so the
dataset's cache rule applies directly and `tokens` is exactly input + cache creation +
output. The human side rests on one published quantity — four MirrorCode contributors'
estimates that a skilled engineer would need 1.5–2.5, 13–17, 3 and 13 weeks to reimplement
gotree — and every non-gotree row transfers that estimate by reference lines of code. Seven
rows land at `match` (gotree and cal solved by Opus 4.6, choose solved in all three
languages); six at `below`.

**Scrutinize first:** the LoC transfer that sets human time for pkl, cal and choose (a
single rate, 19.5 active hours per 1,000 reference LoC, calibrated on one target). The same
donor transferred by end-to-end test count instead moves cal to 225 hours and pkl to 127, so
the proxy choice is worth an order of magnitude on two of the four targets. Then the `choose`
rows, whose runs were scored over 127 visible cases with no hidden duals, so the benchmark's
anti-hardcoding check never ran.

**What this data is not.** The public repository holds the raw data for Epoch's *April 2026
preliminary report*, which used a prototype scaffold on four targets with Opus 4, 4.1, 4.5
and 4.6. It is not the paper's main evaluation (Opus 4.7, GPT-5.5, Gemini 3.1 Pro Preview
over 25 targets), for which no per-run token counters are published. The paper's headline
"Opus 4.7 solved it in 14 hours, passing 2,000/2,001 tests, at a cost of $251" describes a
different run from the 2,000/2,001 Opus 4.6 run in this data, and no row here uses it.

## Shared evidence

### Sources

| What | Where |
|---|---|
| Run records | `https://github.com/epoch-research/MirrorCode-data` at branch `main`, 19 directories under `eval_sets/`, fetched 2026-09-13 |
| Paper | Adamczewski et al., *MirrorCode: AI can rebuild entire programs from behavior alone*, `https://arxiv.org/abs/2606.30182`, v2 of 2026-07-17 |
| Preliminary report | `https://epoch.ai/blog/mirrorcode-preliminary-results`, April 2026, reference [5] of the paper |
| Retained extracts | `agent-work/sources/mirrorcode/MANIFEST.md` |
| Arithmetic | `research/mirrorcode/compute_rows.py`, output `agent-work/derived/mirrorcode/calculations.json` |
| Row assembly | `research/mirrorcode/make_points.py`, output `candidates/mirrorcode/points.csv` and `models.csv` |

Both scripts take explicit input and output paths, depend on the standard library only, and
write new files rather than touching the retained evidence. `compute_rows.py` reads the
dataset registry at `../AI Compute vs Human Time/dataset/models.csv` read-only, for the
FLOPs-per-token coefficients, and nothing in that project folder is modified.

The blog's "Data" section names the repository as the raw data for that post, and the paper
describes the post as "early results on four programs using a prototype scaffold". The four
programs in the post are exactly the four in the repository.

### The work unit

One agent run reimplementing one target program in one language, from a new workspace to the
agent's own `submit()` call. The agent has execute-only access to the reference binary, the
program's documentation, and a `cases.jsonl` of visible test cases; it has no internet and no
third-party dependencies. The no-dependencies clause is not in any prompt: it is the blog's
own description of these runs, "The agent was not provided with internet access, preventing it
from looking up the original program's source code or using third-party dependencies", which
the paper repeats and sharpens into "agents cannot download dependencies in MirrorCode, they
must solve the task using only the standard library".

Source access is absent for gotree, cal and choose. **It is not absent for pkl**, and the pkl
prompt says so: "The Pkl standard library source is in pkl_docs/stdlib/ so you don't have to
reimplement it." The same prompt scopes the pkl task down to "Just `pkl eval` with default
settings", implements no command-line flags, and puts the binary serialization module, Pkl
projects and dependency notation, `package://` URIs and every URI scheme but `file:` out of
scope. The three pkl rows' `task_description` says this; the other ten say "no source access",
which holds for them. The completion criterion is the benchmark's:
the submitted program must produce byte-identical stdout, stderr and exit code to the
reference on every test case, visible and hidden, with hidden cases scored in a separate
container the agent never touches. The paper's primary threshold is 100% of tests passing;
99% or higher is its "substantial reimplementation".

The task prompt each agent received is retained verbatim in
`agent-work/sources/mirrorcode/mirrorcode-task-prompts.md`. It states the compile-and-invoke line, that
`cases.jsonl` takes precedence over any scope carve-out in the prompt, that hidden cases
exist, and "Don't attempt to cheat by wrapping another implementation or creating a lookup
table".

The scaffold is Inspect's ReAct agent with shell, `text_editor`, `evaluate_testcases` (a
scoring pass over visible cases that does not end the session) and `submit`, with Inspect's
`CompactionSummary` compaction so trajectories outlive the context window. The token budget
was one billion input-plus-output tokens per task for every run in this data.

### Targets

| Target | Reference language | Reference LoC | Visible | Hidden | Scored here |
|---|---|---|---|---|---|
| choose | Rust | 931 | 127 | 122 | 127 |
| cal | C | 984 | 764 | 601 | 1365 |
| gotree | Go | 16905 | 1899 | 102 | 2001 |
| pkl | Java | 61461 | 733 | 37 | 770 |

Reference LoC and the scored counts are the blog's own table; visible and hidden splits are
the paper's Table 4. Three of the four agree exactly. `choose` does not: the paper lists 122
hidden duals that the released runs do not contain, and the blog's table counts 127
end-to-end tests for choose. The hidden duals were added after these runs, so the choose runs
were graded on visible cases only.

### Compute

Every record publishes `input_tokens`, `input_tokens_cache_write`, `input_tokens_cache_read`,
`output_tokens` and `total_tokens`. The counters are additive: input + cache_write +
cache_read + output equals total for all 19 records, checked in `compute_rows.py` and
asserted there. This is the Anthropic form `DECISIONS.md` records, not OpenAI's partitioned
form.

The dataset's rule counts fresh input, cache creation and output, and excludes cache reads:

```
tokens        = input_tokens + input_tokens_cache_write + output_tokens
compute_flops = tokens * flops_per_token
```

`compute_flops` additionally carries the cached-context attention term, by the recipe in
`research/attention-correction.md`; the values quoted in this note are the parameter term alone.

`reasoning_tokens` is recorded for nine of the ten Opus 4.6 runs (5,559 to 50,969) and is
absent for the gotree runs of every generation, including Opus 4.6's. Under the Anthropic convention it is a subset of
`output_tokens`, not an additional term; the additivity check above confirms it, since
`total_tokens` is exactly the four-way sum with reasoning nowhere in it. It is therefore
already inside `output_tokens` and is not added again.

**Cache reads dominate the billed traffic and are excluded.** They run from 97.0% to 98.8%
of `total_tokens` in the ten Opus 4.6 runs, and from 79.2% to 98.6% in the nine older gotree
episodes, the low figure being the cache-thrashing Opus 4.5 episode discussed below. Charging the full prefix instead — the
source-total assumption — would raise every row by 14× to 83×. That scenario is recorded per
row in `calculations.json` as `full_prefix_scenario_flops` and is the largest single
accounting choice in this study.

**Cached-context attention is one-sided upward, and `research/attention-correction.md`
has since folded it into `compute_flops`.** Every one of these
runs appends its positions after a long cached prefix: the mean prefix per model call,
computed as (input + cache_write + cache_read) divided by the count of assistant messages in
the transcript, runs 47,700 to 100,200 tokens. Following the recipe the accepted Portal row
uses, attention costs `4 * layers * d_model * context_positions` per appended position at two
operations per multiply-add. At the three bracketing decoder shapes that row uses, the
term is 0.28× to 2.36× the parameter-only value, so a full operation count lands
roughly 1.3× to 3.4× higher. Per row:

| Point | Mean prefix per call | L=64, d=8192 | L=80, d=10240 | L=96, d=12288 |
|---|---|---|---|---|
| agen-mirrorcode-gotree-py-opus4 | 62047 | 0.36 | 0.56 | 0.81 |
| agen-mirrorcode-gotree-py-opus41 | 47673 | 0.28 | 0.43 | 0.62 |
| agen-mirrorcode-gotree-py-opus45 | 97750 | 1.02 | 1.60 | 2.31 |
| agen-mirrorcode-gotree-py-opus46 | 94215 | 0.99 | 1.54 | 2.22 |
| agen-mirrorcode-pkl-c-opus46 | 97672 | 1.02 | 1.60 | 2.30 |
| agen-mirrorcode-pkl-py-opus46 | 99396 | 1.04 | 1.63 | 2.35 |
| agen-mirrorcode-pkl-rust-opus46 | 97573 | 1.02 | 1.60 | 2.30 |
| agen-mirrorcode-cal-c-opus46 | 91862 | 0.96 | 1.51 | 2.17 |
| agen-mirrorcode-cal-py-opus46 | 100159 | 1.05 | 1.64 | 2.36 |
| agen-mirrorcode-cal-rust-opus46 | 92482 | 0.97 | 1.52 | 2.18 |
| agen-mirrorcode-choose-c-opus46 | 87387 | 0.92 | 1.43 | 2.06 |
| agen-mirrorcode-choose-py-opus46 | 70187 | 0.74 | 1.15 | 1.66 |
| agen-mirrorcode-choose-rust-opus46 | 72092 | 0.76 | 1.18 | 1.70 |

Columns are the ratio of the attention term to the recorded value. `compute_flops` stays on
the `2 * active_parameters` convention so these rows remain comparable with the existing
1,410, per `DECISIONS.md`.

Two approximations sit inside the prefix figure. Assistant messages are used as the API-call
count, which is right for this scaffold — every assistant message is one model response — but
a call retried after a transport error would be counted once. And the mean prefix is applied
uniformly to all appended positions, whereas early calls in a run sit behind a much shorter
prefix; the error is second-order against the 3× spread of the bracketing shapes.

### Model coefficients

All four models already exist in `../AI Compute vs Human Time/dataset/models.csv` and are
reused unchanged. `candidates/mirrorcode/models.csv` is therefore header-only.

| Run alias | model_id | flops_per_token | Active parameters |
|---|---|---|---|
| anthropic/claude-opus-4-20250514 | claude-opus-4 | 3.6e11 | 1.8e11, estimated |
| anthropic/claude-opus-4-1-20250805 | claude-opus-4-1 | 3.6e11 | 1.8e11, estimated |
| anthropic/claude-opus-4-5-20251101 | claude-opus-4-5 | 2.0e11 | 1.0e11, estimated |
| anthropic/claude-opus-4-6 | claude-opus-4-6 | 2.0e11 | 1.0e11, estimated |

The three dated aliases pin the API snapshot; the fourth record gives no date suffix. The
step from 3.6e11 to 2.0e11 between Opus 4.1 and 4.5 is the registry's, not this study's, and
it matters: it is why the Opus 4.5 row's FLOPs rise 10× while its token count rises 18×.
Both priors are `estimated` and under review folder-wide, so the ordering of the four gotree
rows on the compute axis depends on an assumption none of these sources makes.

### Human baseline

The only human quantity MirrorCode publishes is for gotree. Blog footnote 20, repeated in
paper section 4: four AI researchers and engineers who worked on MirrorCode estimated how
long a skilled software engineer would need to reimplement gotree without AI assistance,
passing all test cases, given only the information MirrorCode provides. The estimates were
1.5–2.5 weeks, 13–17 weeks, 3 weeks and 13 weeks.

These are judgment estimates, not timings. They carry `human_time_evidence = assumed`,
`human_time_subset = not_applicable` and `human_attempts = not_applicable`.
`human_time_statistic` is `point_estimate` on all thirteen rows, including the gotree ones.
Averaging four estimators is a statistic over estimators, not over human times, and `mean`
would tell a reader there was a sample of timed humans; the dataset's 756 analytic-estimate
rows all use `point_estimate`, and none uses `mean` with a `not_applicable` subset. How the
single estimate was formed is stated in every gotree row's notes.

Epoch states the same quantity in summary form in the paper's opening: "We believe this same
task would take a human engineer without AI assistance 2-17 weeks."

**Conversion.** Midpoints are 2.0, 15.0, 3.0 and 13.0 weeks; the arithmetic mean is 8.25
weeks and the median 8.0, so the dispersion between estimators barely moves the central value
even though the spread across them is elevenfold. A geometric mean would move it, to 5.85
weeks, and COLUMNS prefers the arithmetic mean. Under the folder's ruling a person-year is 2,000 active hours, so a full-time week is
40 active hours and the engagement these estimators describe is full-time on the task, an
on-task fraction of 1.0. gotree is therefore **330 active hours, 1,188,000 seconds**. The
span across estimators is 1.5 to 17 weeks, 60 to 680 hours.

**What is known about real humans on this benchmark.** No observed human has passed a
MirrorCode target completely. Paper section 2.2: "Human software engineers scored below 100%,
but were unable to identify how their implementation differed from the reference." Every
`match` row therefore compares an AI outcome against an estimate of a human outcome that has
not been observed on this benchmark, and the direction of that gap pushes the human times up,
not down.

**Cross-check.** Blog footnote 21 records the one real human attempt: on a simpler 2,000-LoC
MirrorCode task a human SWE did not finish in 20 hours and passed 42% of test cases. Epoch
extrapolates that linearly by LoC to "longer than six days" for gotree and "longer than 25
days" for Pkl, calling both soft lower bounds. Those phrasings recover as hour counts divided
by 24: 16,905 LoC at 20 h per 2,000 LoC is 169 hours, and 61,461 LoC is 615 hours. The 169
hours sits at half the contributors' mean and above their lowest estimate, which is the
expected relation between a lower bound taken from an incomplete attempt and a central
estimate of completion.

**Transfer to the other three targets.** The contributors' mean implies a rate of
330 / 16,905 = **19.52 active hours per 1,000 reference LoC**. Applied to reference LoC:

| Target | Reference LoC | Active hours | Seconds | Epoch's soft lower bound | Exponent 0.8 | Exponent 1.2 |
|---|---|---|---|---|---|---|
| gotree | 16905 | 330.0 | 1188000 | 169.1 | 330.0 | 330.0 |
| pkl | 61461 | 1199.8 | 4319176 | 614.6 | 926.8 | 1553.2 |
| cal | 984 | 19.2 | 69151 | 9.8 | 33.9 | 10.9 |
| choose | 931 | 18.2 | 65426 | 9.3 | 32.5 | 10.2 |

The exponent columns re-run the transfer as effort proportional to LoC raised to 0.8 and to
1.2, normalized at gotree, to show what a non-linear effort-size relation would do. Linear is
the central choice for one reason only: it is the rule Epoch itself applies in footnote 21,
and nothing in these sources supports picking a different exponent.

**The second work quantity, and why it is a sensitivity rather than a co-equal transfer.**
MirrorCode publishes end-to-end test counts for every target in the same blog table, and that
quantity transfers off the same donor: 330 hours over gotree's 2,001 cases is 0.1649 active
hours per case.

| Target | Reference LoC | LoC transfer, hours | End-to-end tests | Test-count transfer, hours | Ratio |
|---|---:|---:|---:|---:|---:|
| gotree | 16905 | 330.0 | 2001 | 330.0 | 1.0 |
| pkl | 61461 | 1199.8 | 770 | 127.0 | 9.4 |
| cal | 984 | 19.2 | 1365 | 225.1 | 11.7 |
| choose | 931 | 18.2 | 127 | 20.9 | 1.2 |

The two proxies agree within 15% for choose and disagree by roughly an order of magnitude, in
opposite directions, for cal and pkl. cal carries 1.39 end-to-end tests per reference line
against gotree's 0.118, which is what drives its half of the gap.

Lines of code stays the central proxy on all thirteen rows, and the test-count figures are
recorded in `calculations.json` as a named sensitivity only. The reason is that the test-count
proxy fails a check the LoC proxy passes: it makes pkl 1.2 times gotree in human time, against
a source that expects "months" for pkl and weeks for gotree. A proxy that produces that is not
a second defensible transfer, so `DECISIONS.md`'s rule of taking the geometric mean of two
defensible transfers does not bind here. Under the other reading the cal rows would move to
65.8 hours and the pkl rows to 390.3 hours.

What the disagreement does establish is the real width of the uncertainty, which the exponent
columns understate by about an order of magnitude for cal. The cal rows' `notes` therefore say
that lines of code is the weakest proxy for that target and one-sided downward there, and
quote the 225-hour figure; the choose rows quote the 20.9-hour figure, which corroborates
rather than contradicts; and the pkl rows say the opposite thing, below.

**The range on the transferred rows.** `human_time_low` and `human_time_high` take
the extremes over the named alternatives for that target. cal runs from 10.9 hours,
the exponent-1.2 transfer, to 225.1 hours, the test-count transfer this note flags as
the real width of the uncertainty there; choose runs from 10.2 to 32.5 hours, the two
exponent columns, with its test-count figure of 20.9 sitting inside them.

**The pkl transfer is an upper anchor, not a neutral central.** Its 61,461 lines are the whole
Pkl codebase. The runs reimplement `pkl eval` with default settings, no command-line flags,
and with the binary module, projects, `package://` and the non-`file:` URI schemes out of
scope, using a standard library whose source is handed to the agent and whose lines are inside
that 61,461 count. gotree's prompt carves out remote fetching, image output and randomized
commands, so some of this cancels in the rate, but pkl's carve-out is much larger and it goes
one way. The evidence does not support a scoped line count, so the number stands and the three
rows' `notes` state that 1,200 hours is an upper anchor for the scoped task.

**Method classification.** All thirteen rows use `human_time_method = estimated`. COLUMNS says
to classify the derivation rather than its final arithmetic step, and the derivation for the
nine transferred rows is a judgment estimate about one program, divided by that program's line
count and applied to a different program; the multiplication is the last step, not the
substance. The precedent agrees: in the reference dataset 743 rows pair `estimated` with
`assumed` and all 81 `transferred_timings` rows are `estimated`, while the 7 `work_rate` rows
with `assumed` evidence take their rate from a source-defined quantity rather than from another
task's estimate. `human_time_evidence` is `assumed` on all thirteen.

`human_skill` is `expert` throughout: the estimates name "a skilled software engineer", and
the one real baseline attempt was by a human SWE.

### Performance labels

The completion criterion is identical on both sides — the contributors were asked to estimate
time to "a complete pass of all test cases" — so the label follows the run's pass rate
against the benchmark's own thresholds.

- `match` where the run met or effectively met the 100% criterion: 2,000/2,001 for gotree
  (Epoch: "we are happy to call gotree effectively solved by Opus 4.6"), 1,365/1,365 and
  1,363/1,365 for cal, 127/127 for choose.
- `below` otherwise.

Seven `match`, six `below`. No row is `above`: the benchmark has no speed or quality metric
on which an agent could beat the estimated human outcome, only completeness.

### Comparison issues

`none_identified` on ten rows. The three choose rows carry `different_assessment`: the human
estimate targets a complete pass of visible and hidden cases, and these runs were graded on
127 visible cases with the hidden group empty, so the hold-out that makes a 100% score mean
"reimplemented rather than hardcoded" did not run for them.

The mechanism, not the missing duals as such, is the reason the flag is needed. Every prompt
exposes an `evaluate_testcases` tool that scores the agent's code against every case in
`cases.jsonl`. For gotree, cal and pkl the headline figure still contains cases the agent never
saw; for choose, 127/127 is a fit to the exact suite the agent optimized against. Two pieces of
evidence cut against reading that as hardcoding: the blog reports Opus 4.6's Rust choose
solution at 648 formatted lines, which is 70% of the 931-line reference and not the shape of a
lookup table, and Epoch's memorization screen concluded that the choose codebase cannot be
reproduced verbatim by these models.

The pkl standard library in the agent's workspace does not create an AI-versus-human input
difference either, because blog footnote 20 asks the estimators for the time "given only the
same information that MirrorCode provides" — the same workspace. That is why correction on the
pkl rows landed on `task_description` and the work quantity rather than on
`comparison_issues`.

Two candidate flags were considered and rejected. **Memorization** is a benchmark-wide
limitation rather than a difference in supplied inputs for these particular rows: Epoch's
screen found that choose, gotree and Pkl cannot be reproduced verbatim by these models, and
the one target with memorization evidence, cal, shows it for Opus 4 and 4.1, neither of which
appears in a cal row here. **Attempt selection** does not apply: where three episodes exist,
both the compute statistic and the performance evidence cover all three, so neither side
selects a subset the other does not.

## agen-mirrorcode-gotree-py-opus4

Three episodes, `eval_sets/gotree-oldopus-v01-ns5k39b82nbd4vre/2026-03-30T12-14-54+00-00_MirrorCode_mZ5ASFjJSMr7JZ4p9vUK83.fast_plaintext/gotree_python_ep001` through `ep003`, model alias `anthropic/claude-opus-4-20250514`.

| Episode | input | cache_write | cache_read | output | tokens counted | billed total | Tests | Assistant messages |
|---|---|---|---|---|---|---|---|---|
| ep001 | 147 | 210741 | 4170258 | 37681 | 248569 | 4418827 | 24/2001 | 93 |
| ep002 | 84 | 295923 | 6747040 | 73216 | 369223 | 7116263 | 307/2001 | 113 |
| ep003 | 105 | 134549 | 12061408 | 62880 | 197534 | 12258942 | 196/2001 | 159 |

Mean counted tokens 271,775.3; compute 271,775.3 × 3.6e11 = **9.7839e16 FLOPs**.

The blog's Opus 4 line — 307/2,001, 7M tokens, 116 messages — is ep002, whose billed total is
7,116,263 and whose last message index is 116. The blog's "In its worst run (run 3), passing
just 8% of visible tests" is ep003 at 153/1,899 visible, and its quoted "we're at 153 passing
tests!" is that count exactly. The three episodes therefore map to the blog's runs 1, 2 and 3
in order, which fixes the model-to-directory mapping for all three older generations.

ep001's 24 passes are all hidden cases with zero visible passes, so that submission did not
run at all against the visible suite. It is kept in the `all` subset.

Human time 1,188,000 s. Performance `below`: best episode 15% of tests.

## agen-mirrorcode-gotree-py-opus41

Three episodes under `..._MirrorCode_MQs95W4LcHNevN9cr7Ygfy.fast_plaintext/`, alias
`anthropic/claude-opus-4-1-20250805`.

| Episode | tokens counted | billed total | Tests | Visible | Assistant messages |
|---|---|---|---|---|---|
| ep001 | 227966 | 5774820 | 317/2001 | 286/1899 | 123 |
| ep002 | 560849 | 7338760 | 471/2001 | 441/1899 | 138 |
| ep003 | 118610 | 4368298 | 152/2001 | 133/1899 | 99 |

Mean 302,475.0 tokens; **1.0889e17 FLOPs** at 3.6e11. ep002 is the blog's Opus 4.1 line:
471/2,001, 7M billed, 141 messages (last index 141), "passing 23% of visible tests" against
441/1,899 = 23.2%.

Human time 1,188,000 s. Performance `below`: best episode 24%.

## agen-mirrorcode-gotree-py-opus45

Three episodes under `..._MirrorCode_6H9RmCuEeK8khuibQggYCD.fast_plaintext/`, alias
`anthropic/claude-opus-4-5-20251101`.

| Episode | input | cache_write | cache_read | output | tokens counted | billed total | Tests | Assistant messages |
|---|---|---|---|---|---|---|---|---|
| ep001 | 190008 | 805085 | 51255174 | 169774 | 1164867 | 52420041 | 946/2001 | 539 |
| ep002 | 201172 | 13415293 | 52442994 | 160984 | 13777449 | 66220443 | 75/2001 | 633 |
| ep003 | 571479 | 720794 | 117233925 | 345451 | 1637724 | 118871649 | 1265/2001 | 1289 |

Mean 5,526,680.0 tokens; **1.1053e18 FLOPs** at 2.0e11. ep003 is the blog's Opus 4.5 line:
1,265/2,001, 119M billed, 1,299 messages, "submits at message 1,299 passing 62%" against
1,176/1,899 = 61.9%.

**The mean is dominated by one episode's cache behavior.** ep002 wrote 13,415,293 cache-
creation tokens against 805,085 and 720,794 for its siblings, a seventeen-fold difference, while
producing the fewest output tokens and the worst score (0 of 1,899 visible). Cache creation is
real processed work and the dataset's rule counts it, so it stays in, but the mean of 5.53M is
3.4× the median of 1.64M and the dispersion is a harness artifact rather than a property of
the task. A reviewer preferring the median would move this row to 3.3e17 FLOPs, 3× the Opus 4.1 row
rather than 10× it. The mean is kept because COLUMNS prefers it and because
nothing identifies ep002 as invalid.

Human time 1,188,000 s. Performance `below`: best episode 63%.

## agen-mirrorcode-gotree-py-opus46

One run, `eval_sets/gotree-v03-w0yrevhbo2ep6388/2026-03-29T20-02-04+00-00_MirrorCode_2Eq9UuTDq9T6rmYyGKyADg.fast_plaintext/gotree_python`, alias `anthropic/claude-opus-4-6`. Only one episode was run for this model.

input 2,188,416; cache_write 2,411,220; cache_read 274,276,243; output 1,239,174; billed total
280,115,053; 2,960 assistant messages; 12 compactions; last message index 2,989.

Counted tokens 5,838,810; **1.1678e18 FLOPs** at 2.0e11.

Score 2,000/2,001: every one of 1,899 visible cases and 101 of 102 hidden. The single failure
is a hidden `gotree cut date` case where a date boundary falling exactly on a node makes the
solution emit a spurious extra root. Both the blog and the paper treat this as the ceiling
achieved on gotree by any model, and the blog's four-generation table gives 280M tokens and
2,989 messages, matching this record.

Human time 1,188,000 s. Performance `match`: the human estimate targets a complete pass and
the run is one hidden edge case short of one, which Epoch calls effectively solved.

The comparison to hold in view: 1.17e18 FLOPs against 330 hours of estimated expert time, the
single most informative point in this study, and the one whose human side is least
transferred.

## agen-mirrorcode-pkl-c-opus46

`eval_sets/ben-202603-mc-sc-opus-4-6-1b-v1-p1/pkl_c`, alias `anthropic/claude-opus-4-6`.

input 5,616,323; cache_write 5,933,482; cache_read 887,425,696; output 2,711,388; reasoning
10,971; billed total 901,686,889; 9,204 assistant messages; 31 compactions.

Counted tokens 14,261,193; **2.8522e18 FLOPs**. The largest row in the study.

Score 321/770 = 41.7% (307/733 visible, 14/37 hidden). The billed total is 90% of the
one-billion-token budget, matching the blog's account that Opus 4.6 "successfully used its
entire billion token inference budget, producing 2–3 million output tokens" on Pkl without
solving it. Output of 2.71M sits in that stated band.

Human time 4,319,176 s, transferred: 61,461 LoC × 19.52 h per 1,000 LoC, and an upper anchor
for the scoped task rather than a neutral central, for the reasons in
[Human baseline](#human-baseline). Performance `below`.

A curiosity that changes nothing: `pkl_c` and `pkl_rust` report exactly the same
`not_edge_and_exit_zero` rate, 0.4912718204488778, which is 197 of 401 exit-zero cases in both.
Two different implementations landing on the same count is either coincidence or a scorer
artifact. Neither row uses that figure — both quote the `all` rate — but a reader comparing the
two scorer blocks will notice.

## agen-mirrorcode-pkl-py-opus46

`eval_sets/ben-202603-mc-sc-opus-4-6-1b-v1-p1/pkl_python`, alias `anthropic/claude-opus-4-6`.

input 3,424,743; cache_write 3,767,119; cache_read 595,250,006; output 1,597,816; reasoning
16,533; billed total 604,039,684; 6,061 assistant messages; 19 compactions.

Counted tokens 8,789,678; **1.7579e18 FLOPs**.

**This run has no score.** `info.json` carries a RuntimeError from the scoring step — a
Kubernetes exec failure in `agent-env-...-agent-scoring-visible-0` while running
`batch_score_test_cases.py` — and `scores.txt` and `cases.jsonl` are both zero bytes. The
agent's own work completed; only the grading pass failed, so the compute is intact and
measured.

The performance label is transferred from the two sibling runs: the same model, target,
budget and scaffold scored 41.7% in C and 35.5% in Rust, and the blog states outright that
Pkl was not solved under a one-billion-token budget. `below` is the label; it is a transfer,
stated as such in `performance_evidence`, not an observed score for this run.

Human time 4,319,176 s, the same upper anchor. Performance `below`.

## agen-mirrorcode-pkl-rust-opus46

`eval_sets/ben-202603-mc-sc-opus-4-6-1b-v1-p1/pkl_rust`, alias `anthropic/claude-opus-4-6`.

input 4,886,910; cache_write 5,091,186; cache_read 891,499,670; output 2,211,682; reasoning
14,758; billed total 903,689,448; 9,239 assistant messages; 27 compactions.

Counted tokens 12,189,778; **2.4380e18 FLOPs**.

Score 273/770 = 35.5% (256/733 visible, 17/37 hidden). The blog's Pkl appendix analyses this
run's eager-evaluation mistake: the agent chose eager evaluation in its first draft against a
specification that repeatedly emphasises lazy evaluation, then patched around it for the rest
of the run.

Human time 4,319,176 s, the same upper anchor. Performance `below`.

## agen-mirrorcode-cal-c-opus46

`eval_sets/compaction-sc-secure-opus-4-6-v1-p1/cal_c`, alias `anthropic/claude-opus-4-6`.

input 196,514; cache_write 353,590; cache_read 44,278,441; output 243,536; reasoning 5,559;
billed total 45,072,081; 488 assistant messages; 1 compaction.

Counted tokens 793,640; **1.5873e17 FLOPs**.

Score 1,365/1,365: 764 visible and 601 hidden, all passing. This is a full solve on the
benchmark's own 100% threshold, with the hidden hold-out exercised.

Human time 69,151 s, transferred: 984 LoC × 19.52 h per 1,000 LoC. Performance `match`.

What `cal` requires is worth recording, because the LoC figure understates it, and the scope
claims are checkable against two retained artifacts: `agent-work/sources/mirrorcode/cal-manual.txt`, the
`cal_docs/manual.txt` shipped in this run's own workspace, and
`agent-work/sources/mirrorcode/cal-visible-case-coverage.md`, a count over this run's `cases.jsonl` of
which features the visible suite exercises. Byte-exact output is required across the default,
`--monday`, `--week`, vertical multi-month and day-of-year layouts, plus the Julian-to-Gregorian
reform with the eleven days removed in September 1752 and a `--reform` flag to move the
adoption date. Of the 1,365 cases, 255 pass week numbers, 278 a multi-month grid, 138
day-of-year numbering, 107 a September 1752 date, 75 an explicit `--reform` or `--iso`, 64 a
column width and 30 the vertical layout. The prompt excuses locales other than the default,
current-day highlighting and terminal coloring.

This is also the target where the human-time proxy is weakest. Transferring the gotree donor by
end-to-end test count instead of lines of code gives 225 hours against the row's 19.2, and the
direction is not symmetric: 1,365 byte-exact cases over 984 lines is the densest test-per-line
ratio of the four targets. The row's `notes` say so.

## agen-mirrorcode-cal-py-opus46

`eval_sets/compaction-sc-secure-opus-4-6-v1-p1/cal_python`, alias `anthropic/claude-opus-4-6`.

input 191,567; cache_write 344,543; cache_read 47,339,989; output 209,262; reasoning 19,186;
billed total 48,085,361; 478 assistant messages; 1 compaction.

Counted tokens 745,372; **1.4907e17 FLOPs**.

Score 1,363/1,365 = 99.85%: all 764 visible and 599 of 601 hidden. Two hidden cases short of
the 100% threshold, comfortably inside the paper's 99% "substantial reimplementation" band.

Human time 69,151 s. Performance `match`, with the two-case shortfall stated.

## agen-mirrorcode-cal-rust-opus46

`eval_sets/compaction-sc-secure-opus-4-6-v1-p1/cal_rust`, alias `anthropic/claude-opus-4-6`.

input 386,879; cache_write 532,132; cache_read 39,865,476; output 306,689; reasoning 48,509;
billed total 41,091,176; 441 assistant messages; 2 compactions.

Counted tokens 1,225,700; **2.4514e17 FLOPs**.

Score 1,365/1,365. Human time 69,151 s. Performance `match`.

The three cal runs bracket the language effect directly: same model, same target, same
criterion, 0.75M to 1.23M counted tokens, a 1.6-fold spread. The paper reports the same
qualitative finding across its whole suite — solve rates barely move with implementation
language, token usage moves a little.

## agen-mirrorcode-choose-c-opus46

`eval_sets/compaction-sc-secure-opus-4-6-v1-p1/choose_c`, alias `anthropic/claude-opus-4-6`.

input 7,612; cache_write 163,161; cache_read 22,287,564; output 102,519; reasoning 21,244;
billed total 22,560,856; 257 assistant messages; no compaction.

Counted tokens 273,292; **5.4658e16 FLOPs**. The smallest row in the study.

Score 127/127 over the visible suite, with the hidden group empty. The paper's Table 4 lists
122 hidden duals for choose that this eval set does not contain, and the blog's table counts
127 end-to-end tests for choose, so the duals postdate these runs. A 100% score here therefore
does not carry the anti-hardcoding guarantee that the same score carries for cal or gotree,
and the row is flagged `different_assessment`. What speaks against reading it as a fit to the
suite is the artifact: the blog records Opus 4.6's Rust choose solution at 648 formatted lines
against a 931-line reference.

Human time 65,426 s, transferred: 931 LoC × 19.52 h per 1,000 LoC. Performance `match` on the
criterion actually applied.

## agen-mirrorcode-choose-py-opus46

`eval_sets/compaction-sc-secure-opus-4-6-v1-p1/choose_python`, alias `anthropic/claude-opus-4-6`.

input 196,110; cache_write 270,389; cache_read 26,766,007; output 195,422; reasoning 50,969;
billed total 27,427,928; 388 assistant messages; 1 compaction.

Counted tokens 661,921; **1.3238e17 FLOPs**. Score 127/127, visible only.

Human time 65,426 s. Performance `match`. Same `different_assessment` flag.

## agen-mirrorcode-choose-rust-opus46

`eval_sets/compaction-sc-secure-opus-4-6-v1-p1/choose_rust`, alias `anthropic/claude-opus-4-6`.

input 4,292; cache_write 173,808; cache_read 13,879,881; output 125,725; reasoning 25,406;
billed total 14,183,706; 195 assistant messages; no compaction.

Counted tokens 303,825; **6.0765e16 FLOPs**. Score 127/127, visible only. This is the target's
own reference language, which is also the cheapest of the three choose runs, and the run whose
648-line solution the blog measures.

Human time 65,426 s. Performance `match`. Same `different_assessment` flag.

## Records inspected and not turned into rows

| Record | Why not |
|---|---|
| Epoch hub `mirrorcode.csv`, 8 model runs (claude-fable-5-1 0.733 down to gemini-3.1-pro 0.089) | Scores only. No log links, no token counters, no cost. The "Logs" and "Log viewer" columns are empty for every row, so there is no compute evidence of any kind. |
| The paper's main evaluation: Opus 4.7, GPT-5.5, Gemini 3.1 Pro Preview over 25 targets, three repetitions in six languages | No per-run usage is published. The paper gives cost per attempt (Appendix E, Table 8) and aggregate statements, and the repository holds none of these runs. Cost-inverted rows are permitted by `DECISIONS.md`, but the published costs are per-model-and-benchmark means rather than per-run figures, and the cache structure of the paper-era scaffold is undocumented, so a conversion would be a transfer on top of a transfer. |
| The paper's gotree headline (Opus 4.7, 14 hours, 2,000/2,001, $251) | A single quoted result with no released usage record. It is the paper's illustration, not a data release; the 2,000/2,001 in this study's data is a different run by a different model. |
| The 20-hour human baseline attempt on an unnamed 2,000-LoC target | The target is not named, the attempt did not complete, and the timing is censored at 20 hours with 42% of cases passing. There is no AI run on that target in the public data to pair it with. It is used as a cross-check on the transfer rate, not as a row. |

Reconciliation: 19 public run records exist; 19 are accounted for. Thirteen become rows;
the other six are the second and third episodes folded into the three multi-episode gotree
rows.

## Open questions for the reviewer

1. **The work quantity behind the transfer**, settled here in favour of lines of code but
   worth re-testing. One rate from one target sets human time for nine of thirteen rows, across
   a 66-fold size range. MirrorCode's other published quantity, end-to-end test count, agrees
   for choose and disagrees roughly tenfold in opposite directions for cal and pkl; taking both
   as defensible and applying the geometric-mean rule would move cal to 65.8 hours and pkl to
   390.3. The ruling recorded here is that the test-count proxy fails on pkl and so is not a
   co-equal transfer.
2. **The Opus 4.5 mean.** One of three episodes contributes 83% of that row's token count
   through cache-creation behavior that looks like harness thrashing, and it is also the
   worst-scoring episode. Mean versus median moves the row by 3.4×.
3. **Active parameters.** The 3.6e11 to 2.0e11 step between Opus 4.1 and Opus 4.5 is an
   inherited prior under folder-wide review. It compresses the apparent compute growth across
   the four gotree generations from 21× in tokens to 12× in FLOPs.
4. **`choose` scored on visible cases only.** Flagged as `different_assessment` rather than
   excluded. The alternative reading is that a 100% visible-only score does not evidence a
   reimplementation at all and the three rows should be dropped; the 648-line Rust solution and
   the memorization screen are the evidence against it.
5. **`pkl_python` has no score.** Its label is transferred from the two sibling runs. The
   alternative is `unknown`.
6. **The pkl work quantity.** 61,461 lines is the whole codebase against a scoped `pkl eval`
   task with a supplied standard library. The row keeps the number as an upper anchor because
   no scoped line count exists in the sources; a scoped count, if one could be established,
   would lower these three rows.
