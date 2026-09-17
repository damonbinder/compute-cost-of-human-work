# FrontierMath Erdős — GPT-6 Astra resolving five open Erdős problems

*Created 2026-09-16 08:07.*
*Last revised 2026-09-16 11:44, revision 7. Revision 2 replaced the compute side, which is now
built from measured per-attempt token counters rather than inverted from cost, because the five
submission repositories were found. Revision 3 made `human_time` the active time the person who
solved the problem spent, conditional on that person succeeding, with no multiple for other
people's failed attempts. Revisions 4 and 5 fix the arithmetic: every anchor is now
people × elapsed days × 8 h/day × an on-task fraction with each factor pointed at the record or
labelled as an assumption, each row is one anchor times one stated multiplier, and the
formalization rate comes from Li's own Lean work rather than the Imperial FLT project's.
Revision 6 removes the divide-by-three that revisions 1 to 5 applied to the measured Lean line
counts: it was an analogy, not a measurement. Years open and the partial-result counts are
reported as sanity checks and used in no figure. Revision 7 replaces the anchor-times-multiplier
construction and Li's 31.7 lines-per-hour formalization rate with the research-mathematics
calibration of `research/math-human-time/math-human-time.md`, which Damon ruled on 2026-09-16 to
be the standing method for research-mathematics rows. The anchors survive as corroboration and,
on #548, as the direct record the method's step 4 prefers.*

## Summary

Five candidate rows, one per Erdős problem GPT-6 Astra resolved in Epoch AI's FrontierMath
Erdős (FME): 68 problems open as of August 2026, selected by Thomas Bloom for mathematical
interest and difficulty, stated in Lean 4 and graded by the Lean FRO's Comparator, with five
models each given one attempt per problem at $300 and 72 hours. Only Astra resolved anything.

| Row | Problem | compute_flops | tokens | $ | human hours | Solve | Lean | FLOPs per human second |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `reas-erdos1-astra` | 1 | 2.3740e19 | 34580000 | 894.50 | 239 | 47 | 193 | 2.76e13 |
| `reas-erdos74-astra` | 74 | 4.2306e18 | 6340000 | 158.83 | 248 | 48 | 200 | 4.74e12 |
| `reas-erdos126-astra` | 126 | 5.7025e18 | 8432500 | 211.00 | 301 | 59 | 243 | 5.26e12 |
| `reas-erdos548-astra` | 548 | 9.6712e18 | 13790000 | 363.00 | 160 | 61 | 99 | 1.68e13 |
| `reas-erdos571-astra` | 571 | 1.5795e19 | 21750000 | 617.00 | 1031 | 207 | 825 | 4.26e12 |

All five are `match` by construction, `human_time_evidence = llm_estimate_from_data`,
`compute_evidence = derived_assumed_inputs`, and both sides select successful attempts:
`compute_subset = successful` and `human_time_subset = successful`.

**The compute side is now measured.** Each of the five per-problem submission repositories
publishes, per attempt, the input, output, cache-read and cache-write token counts from the
harness's own eval logs. Pricing those counters at Astra's published rates reproduces thirteen
of the fourteen reported dollar figures to within 1.4% and the fourteenth to within 4.4%, so the
counters and the dollars corroborate each other and neither is assumed. What remains assumed is the 300B
active-parameter prior, which every frontier row in the collection carries.

**The human side is the ruled quantity: what the solve cost the person who solved it**, priced
by the research-mathematics calibration in `research/math-human-time/math-human-time.md`. Each
artifact's measured Lean line count is converted to written pages at 417 formal lines per
research-paper page, the pages are charged at the size class's hours per page from thirty
resolved research problems, and the formalization is charged at 12.6 formal lines per active
hour from eight completed projects measured on both ends. #548 is the exception the method
provides for: Riordan and Scott worked that exact argument in a dated eight-day window, so its
solve term is that direct record rather than the class rate. The arithmetic is in
[Human time](#human-time), one line each.

Six revisions walked the human side down by two to three orders of magnitude, and the
calibration moves it back up by 1.2 to 1.8×, essentially all of it the formalization rate:

| Problem | Rev 1 | Rev 2 | Rev 3 | Rev 6 | **Rev 7** | Solve | Lean |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | 31320 | 1138 | 438 | 194 | **239** | 47 | 193 |
| 74 | 16731 | 523 | 393 | 158 | **248** | 48 | 200 |
| 126 | 12880 | 553 | 423 | 175 | **301** | 59 | 243 |
| 548 | 41220 | 6470 | 220 | 101 | **160** | 61 | 99 |
| 571 | 53561 | 7289 | 1289 | 563 | **1031** | 207 | 825 |

The arithmetic is in `research/frontiermath-erdos/compute_frontiermath_erdos.py`, its output in
`research/frontiermath-erdos/calculations.json`. `research/frontiermath-erdos/build_rows.py`
wrote the rows' first submission and is superseded: `points.csv` is hand-maintained, and the
human-time columns, their range and their evidence label now come from the calibration.

## What FME is, and what one unit of work is

Source: Adamczewski and Bloom, *FrontierMath Erdős*, `https://epoch.ai/files/frontiermath-erdos.pdf`,
announced at `https://epoch.ai/latest/announcing-frontiermath-erdos`. Benchmark and scaffold at
`https://github.com/epoch-research/LeanOpenProblems`. Per-problem submissions at
`https://github.com/tadamcz/erdos{1,74,126,548,571}`.

- **The problems.** 68 conjectures covering 65 problems, chosen by Bloom from the 652 open
  problems on `erdosproblems.com`, which he curates, on the stated necessary condition that a
  solution "would be, if produced by a human, worthy of a paper in a high-level journal, and be
  of interest to many people in the relevant field". 50 statements come from Google DeepMind's
  Formal Conjectures; 18 were autoformalized by Epoch and reviewed by Bloom.
- **The deliverable.** A Lean 4 proof of the trusted statement or of its negation. Comparator
  compiles the submission in a pristine sandboxed toolchain with no network, requires the
  submitted theorem and every declaration it depends on to be identical to the trusted copy,
  replays the whole proof term through the Lean kernel from scratch, and permits only `propext`,
  `Quot.sound` and `Classical.choice`.
- **The harness.** Inspect's `deepagent` in the default configuration — bash, a text editor, a
  budget tool, subagents, persistent memory and a todo list — or a basic ReAct agent for the
  larger-budget attempts, inside a network-isolated container carrying Lean 4 v4.27.0 with
  Mathlib, SageMath, Python with sympy/mpmath/numpy/pantograph, and an offline snapshot of the
  LaTeX sources of 476,000 pure-mathematics arXiv papers dated to 2022.
- **The models.** A pre-release GPT-6 Astra, GPT-5.6 Sol, GPT-5.5, Claude Fable 5.1 and Claude
  Fable 5. Astra scored 3%, two of 68; the other four scored 0%.

One unit of work is **one open Erdős problem resolved in Lean to Comparator's standard**, and
that is the same unit on both sides.

<a id="work-unit"></a>

## The work unit for the non-benchmark solves

Epoch reports the benchmark run in Table 2 (#74 at $222 and 10 h, #126 at $172 and 10 h) and
every resolution across every attempt in Table 3, including additional attempts at larger
budgets and in a different agent configuration.

| Problem | Result | Resolved in | Cost and working time of each resolution |
|---|---|---|---|
| 1 | disproof | 2 of 5 | $405 (27 h), $1,384 (84 h) |
| 74 | disproof | 7 of 7 | $47 (5 h), $84 (6 h), $150 (8 h), $183 (12 h), $218 (15 h), $222 (10 h), $271 (19 h) |
| 126 | proof | 5 of 5 | $154 (8 h), $172 (10 h), $194 (9 h), $247 (16 h), $249 (17 h) |
| 548 | proof | 1 of 4 | $363 (20 h) |
| 571 | proof | 1 of 4 | $617 (41 h) |

**Decision: each row's compute is the mean over that problem's resolutions whose token counters
are published**, with `compute_subset = successful` and `ai_attempts` the count of those. Four
alternatives were considered and rejected: the benchmark-run attempt alone, which exists for
only two of the five and is one draw from a $47 to $271 spread; the cheapest resolution, which
is the cherry-pick the FME paper was written against; total spend per resolution including
failures, which is the quantity I would rather have and which Epoch publishes only as a
$220,000 aggregate over all additional attempts; and one collection row, which the 2026-09-14
ruling reserves for the case where the only evidence is a per-task average, not this one, where
each problem has its own measured counters.

**On #74 and #126 the selection costs nothing**, because 7 of 7 and 5 of 5 attempts resolved
the problem: the successful-attempt mean is also the all-attempt mean, so those two rows omit
`different_attempt_selection`. #1, #548 and #571 carry it.

Fourteen of the sixteen resolutions have counters. The two that do not, #74 at $222 and #126 at
$172, postdate the 2026-09-06 repository snapshot, and both are mid-range in cost, so dropping
them moves each row's mean cost by under 5%.

<a id="verification"></a>

## Verification, the artifacts, and what each proof is

Comparator's guarantee is narrow and strong: **the proof is correct**. It proves the trusted
statement itself and not a lookalike, no dependency was redefined, nothing rests on an added
axiom or a `sorry`, and the kernel replayed the whole proof term in a container the agent could
not reach. Each submission repository re-runs that check in CI, and all five set
`enable_nanoda: true`, adding a replay through NanoDa, a second Lean kernel written in Rust.

### The artifacts, measured

I cloned all five repositories at their 2026-09-06 commits and counted them
(`wc -l` over `*.lean`; commits `0e39515`, `e127ee5`, `2516785`, `82ffb75`, `62d1aa9`).

| Problem | Repository | Resolutions published | Primary module lines | All resolution modules | Repository total |
|---|---|---:|---:|---|---:|
| 1 | `tadamcz/erdos1` | 2 | 2427 | 2427, 2101 | 4608 |
| 74 | `tadamcz/erdos74` | 6 | 2516 | 1230, 1408, 1968, 1999, 2243, 2516 | 11481 |
| 126 | `tadamcz/erdos126` | 4 | 3058 | 838, 1545, 2342, 3058 | 7866 |
| 548 | `tadamcz/erdos548` | 1 | 1243 | 1243 | 1311 |
| 571 | `tadamcz/erdos571` | 1 | 10390 | 10390 | 10460 |

**The line counts do not track the problems' reputations, and that is the study's most
informative fact.** Erdős–Sós, the problem with a survey devoted to its partial results, has
the smallest artifact of the five at 1,243 lines. The rational-exponents conjecture has the
largest at 10,390, eight times Erdős–Sós and four times anything else.

### What kind of object each proof is

Taken from each repository's README, which paraphrases the module documentation the model wrote,
and from Bloom's summaries in the FME appendix.

- **#1, disproof, 2,427 lines.** A counterexample construction. Linear algebra produces a
  sequence of n × n rational matrices with determinant tending to zero and properties from which
  large sum-distinct sets follow. It is **ineffective**: no bound on how large n must be in
  terms of ε. Bloom reinterpreted it in terms of lattices, which he found more natural.
- **#74, disproof, 2,516 lines.** An elementary induction. Every one of the six resolutions in
  fact proves 3-colourability, a strictly stronger statement than the negation advertised.
  Bloom's initial reading finds three distinct arguments among the six. The cheapest, $47 over
  5 hours of working time, is 1,999 lines.
- **#126, proof, 3,058 lines.** Elementary, and far stronger than the question. The four
  resolutions prove polynomial lower bounds f(n) ≫ n^c at c = 1/8 (the primary), 1/3, 1/2 and
  1/5, against the superlogarithmic growth Erdős asked for, which puts the truth between n^(1/2)
  and Erdős–Turán's own n/log n upper bound.
- **#548, proof, 1,243 lines.** One counting identity and an induction. Count permutation words
  of the host vertices together with a prefix ending at a neighbour of the first vertex; two
  reversible word operations drive an induction on the target tree; the state count 2|E|(n−1)!
  is at most the rooted-copy count plus (k−2)n!, so a tree-free graph has 2|E| ≤ (k−2)n. Bloom:
  "surprisingly short and elegant".
- **#571, proof, 10,390 lines.** A real structural theorem. It builds balanced rooted models for
  every rational parameter and proves closure operations that preserve the extremal-number
  behaviour — edge subdivision by paths of arbitrary length, hubs added to each colour class,
  and positive rooted powers. Bloom judges it the most difficult of the five, and the
  repository's own note says its relation to the existing literature "has not yet been worked
  out".

**What they lean on.** Mathlib, and nothing else. Every resolution is a self-contained module
over Mathlib v4.28.0 whose only imported mathematics is the library; the statement definitions
come verbatim from Formal Conjectures at commit `488aade2` (#1, #74, #126) or from Epoch's own
autoformalization reviewed by Bloom (#548, #571). None of them cites or imports a result from
the partial-results literature on its problem. That is a real finding rather than an absence of
evidence: whatever the arguments owe to prior work, they do not owe it in the form of a lemma
taken off the shelf.

### What verification does not establish

- **One of the five has been read by outside experts; the others have not.** Riordan and Scott
  did read #548 — see the human-time anchors below. For the other four, the review status
  recorded in each `formalization.yaml` is the same: mechanically verified by Comparator, plus
  "preliminary informal reading of the argument by Thomas F. Bloom", plus "no independent
  refereeing". Bloom's own expositions on `erdosproblems.com` are described in the FME paper as
  placeholders until human experts prepare a proper paper.
- **Correct is not the same as strong** (#1's ineffectivity) and correct is not the same as
  understood (#571's relation to prior work).
- **#548's formal statement is marginally weaker than the classical one.** When (k−1)n is odd,
  the classical "more than (k−1)n/2 edges" holds one edge earlier than the benchmark's
  "at least (k−1)n/2 + 1". The proof's internal counting lemma derives the sharp classical
  bound, but only the advertised statement is compared. Recorded in the row's notes.
- **Contamination is addressed by problem choice, not protocol.** No proof of any of the 68
  existed in August 2026, so a model whose cutoff predates that date cannot have memorized one.

<a id="compute"></a>

## Compute

### The published counters

Each repository's README carries, per resolution, the attempt's cost at Astra's rates, its
working time from the harness's eval logs, and its input / output / cache-read / cache-write
token counts in millions. Counted positions under COLUMNS' `params_tokens` rule are fresh input
plus cache creation plus output, with cache reads excluded.

| Problem | Attempt | $ | Working h | Input M | Output M | Cache read M | Cache write M | Counted M | α |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | default, 28 Aug | 405 | 27.1 | 0.05 | 3.3 | 74 | 13.4 | 16.75 | 4.42 |
| 1 | ReAct, larger budget | 1384 | 84.0 | 0.41 | 8.6 | 410 | 43.4 | 52.41 | 7.82 |
| 74 | default, 28 Aug | 218 | 14.5 | 0.04 | 1.7 | 44 | 7.2 | 8.94 | 4.92 |
| 74 | ReAct, larger budget | 47 | 5.0 | 0.02 | 0.3 | 16 | 1.1 | 1.42 | 11.27 |
| 74 | ReAct, larger budget | 84 | 5.8 | 0.04 | 0.7 | 18 | 2.4 | 3.14 | 5.73 |
| 74 | default, 2 Sep | 150 | 8.2 | 0.06 | 1.1 | 30 | 5.2 | 6.36 | 4.72 |
| 74 | default, 31 Aug | 183 | 11.5 | 0.03 | 1.5 | 34 | 6.1 | 7.63 | 4.46 |
| 74 | default, 28 Aug re-run | 271 | 18.5 | 0.05 | 2.0 | 65 | 8.5 | 10.55 | 6.16 |
| 126 | default, 28 Aug | 247 | 15.8 | 0.06 | 1.8 | 53 | 8.3 | 10.16 | 5.22 |
| 126 | default, 31 Aug | 154 | 8.4 | 0.02 | 0.9 | 38 | 5.5 | 6.42 | 5.92 |
| 126 | default, 2 Sep | 194 | 9.5 | 0.03 | 1.3 | 40 | 7.0 | 8.33 | 4.80 |
| 126 | ReAct, larger budget | 249 | 17.0 | 0.02 | 1.7 | 77 | 7.1 | 8.82 | 8.73 |
| 548 | ReAct, larger budget | 363 | 20.5 | 0.19 | 2.1 | 113 | 11.5 | 13.79 | 8.19 |
| 571 | ReAct, larger budget | 617 | 41.3 | 0.35 | 3.3 | 222 | 18.1 | 21.75 | 10.21 |

**The counters and the dollars corroborate each other.** Pricing each row's four counts at
$10 / $50 / $1 / $12.50 per million — Astra's rates as OpenAI provided them on 2026-09-03 and as
the READMEs restate them — reproduces the reported dollar figure to within 1.4% on thirteen of
the fourteen, and to within 0.7% on eleven. The one larger miss is 4.4%, on the $47 attempt,
whose counts are the smallest and so the most affected by the READMEs' rounding to one or two
significant figures in millions. Nothing in this study needs a cost inversion, and `compute_method` is
`params_tokens` on measured tokens.

### From counters to FLOPs

`tokens` is the mean counted total over the row's resolutions. `attention_context` takes the
cache-implied tier of `research/attention-correction.md#cache-implied-context`, at **the row's
own cached-against-uncached split** rather than a transferred one — the tier COLUMNS prefers
and the strongest available here: α is pooled cache reads over pooled counted tokens, and the
mean attended context is α × 2,800 new tokens per call, bounded by half the counted tokens and
by the 200,000 cap, neither of which binds on any row.

| Problem | Counted tokens | α | attention_context | attention_ratio | compute_flops |
|---|---:|---:|---:|---:|---:|
| 1 | 34580000 | 6.998 | 19595 | 0.1442 | 2.3740e19 |
| 74 | 6340000 | 5.442 | 15237 | 0.1121 | 4.2306e18 |
| 126 | 8432500 | 6.167 | 17267 | 0.1271 | 5.7025e18 |
| 548 | 13790000 | 8.194 | 22944 | 0.1689 | 9.6712e18 |
| 571 | 21750000 | 10.207 | 28579 | 0.2103 | 1.5795e19 |

The attention term is 11% to 21% of the parameter-only value, which is small for an agentic run
and is a consequence of the harness's cache behaviour: these agents re-read a prefix of only
tens of thousands of tokens, five to ten times per new token written, rather than the
six-figure prefixes the Portal and Navier–Stokes rows carry.

`compute_evidence` is `derived_assumed_inputs` and not `derived_supported_inputs`, following the
sixteen official Terminal-Bench 2.1 rows, which are in exactly this position: measured token
counters against an estimated active-parameter prior, where the prior is the substantial assumed
input.

### Scenarios

| Scenario | #74 | #571 | Ratio to central |
|---|---:|---:|---:|
| Central | 4.231e18 | 1.579e19 | 1.00 |
| Parameter term only, no attention | 3.804e18 | 1.305e19 | 0.90, 0.83 |
| Cheapest resolution of this problem | 9.475e17 | 1.579e19 | 0.22, 1.00 |
| Dearest resolution of this problem | 7.040e18 | 1.579e19 | 1.66, 1.00 |
| Cache reads charged a weights pass | 2.725e19 | 1.770e20 | 6.4, 11.2 |
| Astra 100B active | — | — | 0.33 |
| Astra 600B active | — | — | 2.00 |

The cache-read row is the accounting counterfactual, not a live scenario: it is what the total
would be if every re-read prefix position took a full forward pass, which COLUMNS excludes
because it does not.

Two omissions push the recorded value up and are not priced. Lean compilation, Mathlib builds
and SageMath runs are conventional computation and contribute nothing under this schema although
they dominate the wall clock. And Astra is reported to use recurrent-depth decoding; if the
pre-release checkpoint does, the per-token coefficient scales with an undisclosed pass count.

### The range

`compute_flops_low` and `compute_flops_high` combine exactly the two uncertainties COLUMNS
names, recomputed through the attention recipe at each end rather than scaled: Astra's ruled
100–600B band with the attention shape each end implies under the estimated-shape rule at
OpenAI's 0.65 layer share — (52, 10240) at 100B and (94, 18560) at 600B against (75, 14720) at
300B — and the new-tokens-per-call constant at the 10th and 90th percentiles of the sixteen
Terminal-Bench 2.1 submissions, 1,976 and 19,088 against the 2,800 the central uses, applied to
this row's own α.

| Problem | low | central | high | Span | Context low | Context high |
|---|---:|---:|---:|---:|---:|---:|
| 1 | 7.935e18 | 2.3740e19 | 7.373e19 | 9.29 | 13829 | 133583 |
| 74 | 1.413e18 | 4.2306e18 | 1.220e19 | 8.64 | 10753 | 103870 |
| 126 | 1.905e18 | 5.7025e18 | 1.705e19 | 8.95 | 12185 | 117708 |
| 548 | 3.234e18 | 9.6712e18 | 3.160e19 | 9.77 | 16192 | 156414 |
| 571 | 5.284e18 | 1.5795e19 | 5.567e19 | 10.54 | 20169 | 194829 |

Spans of 8.6 to 10.5 against a collection median of 5.5 and a p10-to-p90 of 2.8 to 14.3. The
200,000 cap does not bind at either end on any row.

**One discrepancy to flag.** `research/compute-range/compute-range.md` states the endpoint
formula with the superseded percentiles 1,866 and 13,368 in its "Which rows get a context band"
block, while its own percentile table, `COLUMNS.md` and `compute_range.py` all give the
consistent 1,976 and 19,088. COLUMNS is authoritative and is what these rows follow; the note's
formula block is stale text from the earlier build.

## Model record

**No new model record is needed.** The rows use `gpt-6-astra` as it stands in
`dataset/models.csv`: release date 2026-09-03, 300B active parameters `estimated`, 6e11 FLOPs
per token, 75 layers at 14,720 wide, `estimated`. The 300B is Damon's 2026-09-13 ruling on the
pricing cross-check, not an OpenAI disclosure, and the 100–600B band is in the range columns.

Epoch used "a pre-release version of GPT-6 Astra", recorded in `source_record` rather than
minted as a separate identity. The dollar figures are computed at the released model's published
rates, and a pre-release checkpoint of a released model is closer to a configuration than to the
never-released internal model the Navier–Stokes row had to mint a record for. One caveat worth
carrying: the FME harness metered spend at stand-in GPT-5.6 Sol prices during the run, which is
why the repositories' file names carry dollar figures about half the true ones; the README tables
reprice at Astra's own rates, and those repriced figures are what the rows use.

<a id="human-time"></a>

## Human time

**The quantity, per Damon's ruling of 2026-09-16.** How long it took the person who solved it,
conditional on that person succeeding: the summed active time a strong combinatorialist who did
solve this problem would spend, from sitting down with it to a written proof of the same result.
Not the time the field spent, not what it would cost humanity to get there, and no multiple for
other people's failed attempts. That matches the dataset's successful-attempt human timings
elsewhere and matches the AI side here, which is a mean over successful resolutions.

Two consequences. The `(1 + F) × attempt` construction of revision 2 is gone, along with the
partial-result counts that drove it. And `different_attempt_selection` comes off all five rows:
both sides now select successful attempts, so the flag has nothing left to describe.

**The method, per Damon's ruling of 2026-09-16.** These five rows are priced by the
research-mathematics calibration in `research/math-human-time/math-human-time.md`, which is now
the standing method for research-mathematics rows. It has two tables behind it: thirty-five
resolved research problems giving hours per written page by size class, and twelve formalization
projects giving formal lines per active hour. Both tables read the same quantity these rows
need, and both are built from recorded timelines rather than from judgment, so
`human_time_evidence` is `llm_estimate_from_data` rather than the `llm_estimate_judgment` the
earlier revisions carried. `human_time_subset = successful`, `human_time_statistic =
point_estimate`, and `human_attempts` is the count of contributing donor records: 38 on four of
the rows, the calibration's 30 resolved problems in the fit plus its 8 formalization projects,
and 9 on #548, whose solve term is one direct record rather than the class rate.

**The anchors below are kept as corroboration.** Four of the five are rows of the calibration's
own Table 1 — Erdős 1026, Riordan and Scott on #548, the Erdős 52 collaboration, and
Sothanaphan's write-up of #728 — so they now enter the class rates rather than setting a figure
directly. The exception is A2, which is a direct record on this study's own problem and
supersedes the class rate at step 4 of the method.

**The anchor-times-multiplier construction is withdrawn**, and with it the judgment multipliers
of 1.0, 1.2, 1.5 and 3.0 that revisions 4 to 6 applied. The calibration reads each row's size
off its measured artifact instead, which is why #571 moves most: its 3.0 was flagged in this note
as the least defensible figure in it, and 24.9 estimated pages is a measurement.

**Li's 31.7 formal lines per active hour is also withdrawn**, superseded by the calibration's
12.6. The 31.7 divided an estimate by an estimate: Li never published a line count, so 4,160
lines was inferred from 26 pages at Odd Order's 160 lines per page, and this note flagged that
step as its weak link. The calibration's 12.6 is the median over eight projects measured on both
ends, with a band of 5.4 to 15.0 — a dispersion of 2.8, the tightest number in that note. It
sits between the 31.7 and `research/flt-anthropic.md`'s Imperial figure of 5.88, both of which
it replaces.

<a id="anchors"></a>

### The anchors

Corroboration, and the source of #548's direct record. A5 is listed for the record and is no
longer used for anything: it set the withdrawn 31.7 lines-per-hour rate.

| Key | Arithmetic | Summed active hours, band | What it measures |
|---|---|---:|---|
| **A1** | 6 people × 2 d × 8 h/d × 0.25 | **24**, 12 to 36 | Erdős #1026: a small, obscure problem closed under directed attention |
| **A2** | 2 × 8 d × 8 h/d × 0.40 | **51**, 26 to 77 | Riordan and Scott on #548: digesting, simplifying and extending a short argument already in hand, on this study's own problem |
| **A3** | 4 × 7 d × 8 h/d × 0.35 | **78**, 45 to 112 | Bloom, Sawin, Schildkraut and Zhelezov on Erdős #52: resolving a Bloom top-ten problem and writing 25 pages |
| **A4** | 1 × 28 d × 8 h/d × 0.30 | **67**, 34 to 112 | Sothanaphan on #728: writing a 20-page paper from a finished AI Lean proof |
| **A5** | 1 × 41 d × 8 h/d × 0.40 | **131**, 66 to 197 | Eric Li on #550: formalizing one's own short, self-contained 26-page proof in Lean |

Where each factor comes from, and which are assumptions.

- **A1.** People: Tao's blog post of 8 December 2025 names about six contributors making
  identifiable inputs. Days: Tao, that all key inputs were "assembled within 48 hours".
  Fraction: **pointed, not assumed** — the same post times the individual contributions at
  "within hours", "less than an hour after that" and "approximately an hour of run time", which
  is one to three hours each over the window, so an eighth to three-eighths of one working day.
- **A2.** People: two authors on `arXiv:2609.15893`. Days: 6 September, when the submission
  repositories were pushed, to their 14 September submission. Fraction: **my assumption.** Both
  are Oxford professors with teaching and administration, but 14 September falls before
  Michaelmas term starts, so the fraction is set above a term-time one; 0.40 is 3.2 hours a day
  each for eight straight days including a weekend.
- **A3.** People: four authors on `arXiv:2605.28781`. Days: 20 May, the AI disproof of #90 that
  the erdosproblems wiki records as having inspired the paper, to their 27 May submission.
  Fraction: **my assumption.** Four working mathematicians in late May, out of term in both the
  UK and the US, collaborating intensively; 0.35 is 2.8 hours a day each. Four people full time
  for a week would be 224 hours, and they were not full time on it.
- **A4.** People: sole author of `arXiv:2601.07421`. Days: about four weeks spanning v1 to v5,
  the last dated 27 January 2026, against an AI resolution earlier that January. Fraction: **my
  assumption**, and lower than A2's and A3's because this is one author over a month rather than
  a collaborative burst.
- **A5.** People: sole author of `arXiv:2606.23659`. Days: v1 on 22 June 2026 to v2 on 2 August
  2026, whose comment reads "The proof has been formally verified in Lean". Fraction: **my
  assumption**, set above term time because the window is the long vacation.

**The whole anchor set lies between 24 and 131 summed active hours**, and the only figure above
100 is a formalization. Two of the five bear directly on this study: A2 is problem #548 itself,
and A3 is one of Bloom's own ten favourite Erdős problems, resolved by humans including Bloom.
Read against the calibration, these anchors are all short-class solves and they sit inside its
short-class total-hours band of 28 to 504, which is the check they now provide.

**Not an anchor.** Noga Alon's "a few dozen Erdős problems over his career" (Quanta, August
2026) is about 36 problems over a career from 1979, one per 1.3 years. It does not convert to
hours without his time allocation, so it is used only as a direction check — it points the same
way, at tens of hours per successful solve rather than thousands — and contributes to no figure.

### What is not in the anchor set

No paper resolving an Erdős problem that I could reach states its own duration in an
acknowledgement: not the #52 paper, not Li's, not Riordan and Scott's. Quanta's survey of the
field quotes no mathematician on how long a problem takes. So every anchor above is an elapsed
window with an assumed on-task fraction, and the fraction is the weakest factor in all five.
Halving every fraction halves every row.

### Sizing and placing each problem

Steps 2, 3 and 5 of the method. No paper exists for any of the five, so the written size is
estimated from the measured Lean artifact at the calibration's **417 formal lines per
research-paper page**, and the page count sets the size class and its rate.

| Problem | Measured lines | Pages at 417/pp | Class | h/page | **Solve hours** |
|---|---:|---:|---|---:|---:|
| 1 | 2427 | 5.8 | short | 8.0 | **47** |
| 74 | 2516 | 6.0 | short | 8.0 | **48** |
| 126 | 3058 | 7.3 | short | 8.0 | **59** |
| 548 | 1243 | 3.0 | short | direct record | **61** |
| 571 | 10390 | 24.9 | medium | 8.3 | **207** |

**#548 keeps its direct record**, because step 4 of the method prefers one to any rate: A2's
51 hours times the 1.2 cold-start multiplier this note argued, 61 hours. Riordan and Scott
worked that exact argument in a dated eight-day window, which no rate can improve on. At the
short-class rate the same row would price at 24 hours, so the direct record is the more
expensive of the two readings and is kept for being the better evidence rather than the larger
number.

**#571 crosses into the medium class**, at 24.9 estimated pages against the other four's 3 to 7.
That is where the old judgment multiplier of 3 used to sit, and the calibration replaces it with
a measurement: the artifact is four times any other of the five, and the class break at twelve
pages is what registers it.

**The 417 is the method's largest discretionary step** and the note that sets it says so: the
lines-per-research-paper-page ratio has a dispersion of 7.3 across its four projects, against
1.9 for the blueprint ratio. A blueprint ratio is not available here, because none of the five
artifacts has one.

<a id="lean-component"></a>

### The Lean component

`hours = measured lines ÷ 12.6 formal lines per active hour`, the calibration's Table 2 median
over eight completed projects, each with a measured line count and a measured author-day record.

| Problem | Measured lines | **Lean hours at 12.6** | At 15.0 | At 5.4 |
|---|---:|---:|---:|---:|
| 1 | 2427 | **193** | 162 | 449 |
| 74 | 2516 | **200** | 168 | 466 |
| 126 | 3058 | **243** | 204 | 566 |
| 548 | 1243 | **99** | 83 | 230 |
| 571 | 10390 | **825** | 693 | 1924 |

**No compression is applied to the measured line counts**, which is unchanged from revision 6.
Nothing here measures a boilerplate or redundancy share of these files, and the calibration's
rate has Mathlib-idiom Lean in its numerator, so **the Lean term is an upper bound**: a human
would write fewer lines than the machine did, and any compression only lowers it. The
calibration's own method section makes the same point at step 6 and asks that the term be
labelled a bound where only the machine artifact is measured, which is the case on all five.

### The numbers

<a id="human-time-1"></a>
<a id="human-time-74"></a>
<a id="human-time-126"></a>
<a id="human-time-548"></a>
<a id="human-time-571"></a>

| Problem | Solve | Lean | **Central hours** | Low | High | Excluding Lean |
|---|---:|---:|---:|---:|---:|---:|
| 1 | 47 | 193 | **239** | 186 | 694 | 47 |
| 74 | 48 | 200 | **248** | 192 | 719 | 48 |
| 126 | 59 | 243 | **301** | 234 | 874 | 59 |
| 548 | 61 | 99 | **160** | 144 | 291 | 61 |
| 571 | 207 | 825 | **1031** | 720 | 2422 | 207 |

**The bounds are the calibration's own dispersion and nothing else.** No default factor is
applied anywhere. On the solve term the low and high are the size class's minimum and maximum
hours per page over the resolved problems in that class — **4.1 and 42.0 for short**, **1.1 and
20.0 for medium** — applied to the same page count as the central. On the Lean term they are the
formalization rate's band, **15.0 lines per active hour at the low end and 5.4 at the high**.
The page ratio itself is held at 417 at both ends, because moving it would move the page count
and the class rate together and compound one discretionary step with another. #548's band is
narrower than its siblings' for a reason worth stating: its solve term is a direct record, which
carries no class dispersion, so its band is the formalization rate's alone.

**The ruling reorders the five, and the calibration keeps that order.** #548 is the cheapest
human task at 160 hours, despite being the problem with a survey devoted to its failed partial
results, and #571 the dearest at 1,031. Conditional on success, a solve costs what the argument
that exists costs, not what the problem's history cost.

**The Lean term is now 62% to 81% of each total**, up from 39% to 58% at revision 6, and the
whole of the rise is the rate: 12.6 against 31.7 is a factor of 2.5 on a term that was already
half of each row. The `Excluding Lean` column is the mathematics alone, and it is the column to
read if a reader wants these rows priced on a deliverable without a formal artifact.

<a id="years-open"></a>

### Years open, reported and not used

| Problem | Posed | Years open at resolution | Erdős prize | Times Erdős restated it in print | Documented partial results |
|---|---|---:|---:|---:|---:|
| 1 | 1931 | 95 | $500 | 25 | 2 |
| 74 | 1982 | 44 | $500 | 12 | 0 |
| 126 | 1934 | 92 | $250 | 4 | 0 |
| 548 | 1962 | 64 | $100 | 5 | about 20 |
| 571 | 1974 | 52 | none | 6 | about 20 |

**No figure above uses any column of this table**, and the last column is kept only as the
record of what revision 2 used. Tao's wiki says why years open is not a difficulty measure: "If
an Erdős problem was posed N years ago and was recently solved by AI, it may be tempting to
conclude: 'the problem resisted all human attempts at solution for N years' in order to imply
the problem is difficult. Instead, it could be that the problem has received little attention."
Under the ruled quantity even the partial-result count is beside the point, because it counts
other people's failures.

The check the table provides: years open ranks the five 1 > 126 > 548 > 571 > 74, the
partial-result count ranks them 548 = 571 > 1 > 74 = 126, and the figures above rank them
571 > 1 > 126 > 74 > 548. Only the third agrees with the three independent difficulty judgments
on record — Bloom calling #571 the hardest and #548's proof short and elegant, Astra resolving
#74 on 7 of 7 attempts and #126 on 5 of 5 against 1 of 4 on #548 and #571, and the artifact
sizes themselves.

### `human_skill` is `expert`

The population is the research community in extremal graph theory and additive number theory:
substantial professional training and experience, which is COLUMNS' `expert`. Riordan and Scott,
and Bloom's own co-authors on #52, are the concrete instances behind A2 and A3, and they are
exactly that population. `world_class` is arguable on #571, Bloom's own top-ten pick; the FLT
row faced the same call and kept `expert` so that the donor rate and the target population
match.

### Sanity checks

- Against the batch's two neighbours, now priced by the same calibration: Navier–Stokes 14,892
  hours for a Millennium problem, FLT 27,758 for formalizing a known proof, and these five at
  160 to 1,031. Those two price a whole programme and a whole library; these price one person's
  successful attempt at one theorem, which is the ruled quantity and a different thing. All
  three sets now sit on one method, so the spread between them is the spread in the
  deliverables rather than in the constructions.
- The Lean component is 62% to 81% of each total, and uncompressed it is an upper bound.
- **The ratios are among the collection's cheapest.** 4.3e12 to 2.8e13 FLOPs per human second
  against a collection 95th percentile of 2.57e14, and the five rank 849th, 888th, 919th,
  1,301st and 1,396th of 1,683. The finding is unchanged by the calibration: a few hundred
  dollars of API spend bought what a strong combinatorialist would spend six to twenty-six weeks
  of concentrated work on.

## Performance and comparison

`performance_vs_human = match` on all five, by construction. COLUMNS: "When human time
explicitly estimates reproducing the AI output at comparable quality, use match by
construction." The human estimate prices exactly this deliverable.

**What the label rests on: no human result exists.** No human resolved any of these five
problems, so there is no observed human performance in any of these rows, and
`performance_evidence` says so rather than implying one. `above` would assert victory over a
baseline that does not exist; `unknown` would discard the matched-quality estimate the schema
provides for. What `match` does not mean is parity of achievement: on every one of these five
the AI did something no human has done.

`comparison_issues`, now two values on every row:

- **`different_inputs_or_tools`**, all five. The agent had Lean with Mathlib, SageMath, Python
  with a numerical stack, pantograph, subagents, persistent memory, and an offline snapshot of
  476,000 arXiv mathematics papers. The human baseline is unassisted. The difference is not all
  in the agent's favour — its snapshot stops in 2022 and a human has everything to 2026, and the
  container has no network — but it is concrete and the flag records it.
- **`different_assessment`**, all five. The AI result is machine-checked and, on four of the
  five, unrefereed and not yet digested; a human result of this class would be refereed and
  placed in context. The human estimate includes a write-up the AI side did not produce, and the
  AI side includes a kernel check no human proof of this class gets. The asymmetry runs both
  ways and the flag says the assessments differ. #548 is the partial exception: Riordan and
  Scott have now read and simplified that argument.
- **`different_attempt_selection` is not flagged on any row**, which changed at revision 3.
  Both sides now select successful attempts: the AI figure is the mean over verified resolutions
  and the human figure is the solver's own time conditional on succeeding. The failed attempts'
  spend on #1, #548 and #571 is still unpublished, and under the ruled quantity that is no
  longer a comparison defect, because neither side counts failures.

Considered and not flagged. `different_task` does not apply: both sides are priced on the same
statement to the same verification standard. An estimated human baseline is not itself a flag,
per COLUMNS.

## Reproducing

```
python3 research/frontiermath-erdos/compute_frontiermath_erdos.py \
    --out research/frontiermath-erdos/calculations.json

python3 research/frontiermath-erdos/build_rows.py \
    --calculations  research/frontiermath-erdos/calculations.json \
    --points-header points.csv \
    --out           /path/to/points-fragment.csv
```

Python 3.9 or later, standard library only. `compute_frontiermath_erdos.py` reads nothing: every
input is a named constant at the top of the file with its source in the comment above it, so the
published token counters, the prices, the parameter priors, the percentiles of the
new-tokens-per-call constant, the measured Lean line counts, the attempt cost, the failed-attempt
counts and the calibration's rates are all in one place and all auditable. The rates themselves
are derived in `research/math-human-time/compute_math_human_time.py`, which reads the two
calibration CSVs; this script carries their published values as constants and does not recompute
them. `build_rows.py` wrote the rows' first submission and is superseded — `points.csv` is
hand-maintained — so its text and its `human_time_evidence` reflect revision 6 and not the rows
as they now stand.

To re-measure the artifacts:

```
for n in 1 74 126 548 571; do
  git clone --depth 1 https://github.com/tadamcz/erdos$n.git
  (cd erdos$n && git log -1 --format=%H && wc -l Erdos$n/Resolutions/*.lean)
done
```

The commits the counts above were taken at are `0e39515`, `e127ee5`, `2516785`, `82ffb75` and
`62d1aa9`, all pushed 2026-09-06.

## Not used

- **The 63 unresolved conjectures.** 66 of Astra's 68 benchmark attempts ran to the $300 cap
  without a verified submission, 59 conjectures were attempted two to six more times for 269
  further attempts with no resolution, and four models resolved nothing at all. No row is
  proposed for any of them under the uninformative-failure ruling. The count is what the five
  rows should be read against and it belongs in a write-up rather than in `points.csv`.
- **The $220,000 aggregate.** The right numerator for a cost-per-resolution figure, and not
  splittable by problem. Worth quoting: five resolutions for $220,000 of additional attempts is
  $44,000 each all in, against Epoch's own $10,000 estimate from the benchmark run's 3% rate at
  $300 an attempt. Even at $44,000 the human comparison is not close.
- **The repositories' file-name dollar figures.** `Erdos571_325usd_42h.lean` and its siblings
  carry the harness's stand-in GPT-5.6 Sol metering, about half the true Astra cost, and the `h`
  in the file name is wall clock rather than working time. The README tables carry the repriced
  figures and the working times, and those are what the rows use.
- **Years open, prize values, Erdős's restatement counts and the partial-result counts.**
  Reported in one table as a sanity check and used in no figure. The partial-result counts drove
  revision 2's human side and are out under Damon's ruling, because they count other people's
  failed attempts.
- **Astra's own working time.** Five to 84 hours per resolution, recorded nowhere in the rows:
  it is the agent's clock, not its compute, and the human figure is active hours rather than
  elapsed time.
- **The nine Erdős problems resolved by Tsoukalas et al.'s proof-search agent**, and the OpenAI
  and Anthropic results on #90, #146 and #183. Different work units, different systems, and none
  inside FME's controlled protocol.
