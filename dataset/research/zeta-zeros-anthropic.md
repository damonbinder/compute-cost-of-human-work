# Zeta zeros on the critical line — Anthropic, August 2026

*Created 2026-09-16 11:52.*

## Summary

One candidate row, `reas-zeta-zeros-anthropic-internal`. An unreleased research version of Claude,
run in Claude Code by a non-mathematician who prompted it to "take a real stab" at the Riemann
hypothesis, raised the unconditional lower bound on the proportion of nontrivial zeta zeros that are
simple and on the critical line from 5/12 = 41.6% to 0.6725, and the distinct-zero proportion from
0.6603 to 0.83625. The result is written up as Alpöge–Furman, [arXiv:2608.13637](https://arxiv.org/abs/2608.13637),
21 pages, and formalized sorry-free in Lean 4 at `anthropics/formal-math` under `zeta23/`.

Recorded values: **compute_flops 9.66e19**, **tokens 1.6151e8** (`input_cache_creation_output`),
**human_time 627,480 seconds** (174.3 active expert hours), `performance_vs_human = match` by
construction. That is **1.54e14 FLOPs per human-second**.

The arithmetic, in one line each:

- **Compute.** `3.1e7 output tokens × (1 + 4.21) = 1.6151e8 processed positions;
  × (2 × 1.5e11 + 4 × 64 × 11648 × 1e5) = 9.66e19 FLOPs.` The 3.1e7 is Anthropic's, exact. The
  4.21 is the Fermat row's transferred appended-token ratio, the 1.5e11 is the Anthropic
  internal-research-model prior, and the 1e5 context is the Fermat row's central for a Claude Code
  agent session.
- **Human.** `21 pages × 8.3 hours per page = 174.3 active hours`, the medium-class rate from
  `research/math-human-time/math-human-time.md#table1`, range 23.1 to 420 hours from that class's
  own 1.1 and 20.0 hours per page.

**Two things a reviewer should attack first, and one finding that changes the work unit.**

1. **The Lean formalization is outside the work unit, and this differs from the brief.** Anthropic's
   31 million output tokens covers the two Claude Code sessions that *found* the bound and drafted
   the paper. The blog states the Lean was produced separately — "In parallel, Claude worked with
   another member of staff, Eric Easley, to produce a Lean formalization" — and the artifact's own
   `formalization.yaml` records `cost: wall_time: not tracked, spend_usd: not tracked` and a human
   direction structure (the paper's authors directing, Easley orchestrating) that the blog's 60
   subagents do not contain. No compute figure exists for the Lean. So the row prices the research
   run on both sides and excludes the Lean from both. Had the Lean been kept on the human side it
   would have added 695 to 8,177 hours against no compute at all, swamping a 174-hour solve term.
   Details in [What the 31 million output tokens covers](#work-unit).
2. **The r = 4.21 input-side transfer**, inherited whole from `research/flt-anthropic.md#compute`
   and resting on the premise that the Claude Code harness cached. Same lever, same size: uncached,
   the gross count is far larger.
3. **The 8.3 hours per page**, a class median over six medium-class human solves whose own
   dispersion is a factor of 18.

## Shared evidence

### What was published, and when

The [Anthropic post](https://www.anthropic.com/research/riemann-zeta) is the compute record, updated
13 August 2026 with a revised version of the paper. The relevant sentences, verbatim:

> An unreleased research version of Claude found the new lower bound over two sessions in Claude
> Code, using a total of 31 million output tokens.

> Jarred Sumner, an Anthropic staff member (and non-mathematician), prompted Claude to "take a real
> stab" at the hypothesis itself, leaving the mathematical choices from there up to the model.
> Initially, Claude generated and tried 650 ideas, none of which worked. Jarred prompted Claude to
> try again, and it spent a day and a half coordinating about 60 Claude subagents, which this time
> went much deeper: between them, they ran 2,400 shell commands and wrote hundreds of Python
> scripts. The subagents ran thousands of numerical checks against known zeta zeros and refereed one
> another's work.

> Having found this new result while attempting the task, Claude tested its work by having various
> subagents review the proofs, search for counterexamples, download 54 papers from the arXiv to
> check that its finding hadn't already been made, and independently re-prove its finding from
> scratch. Claude volunteered to write its findings up as a paper, and recommended that a human
> number theorist validate its findings.

> In parallel, Claude worked with another member of staff, Eric Easley, to produce a Lean
> formalization of the result, which passes the standard validation tool comparator.

The post's footnote gives the subagent role split, recorded in
`agent-work/scouting/long-running-feats.md` as 2 developing the core mathematical ideas, 13
contributing supporting ideas, 30 attempting approaches that did not work, 13 validators and 2
assisting with the initial paper writing — 60 in all. That is the whole compute record: no input
tokens, no cache counters, no dollars, no GPU-hours, no model size, no wall clock beyond "a day and
a half".

<a id="work-unit"></a>

### What the 31 million output tokens covers

**Inside.** Both sessions. The first session's 650 generated-and-failed ideas are inside, because
the sentence attaches the total to "found the new lower bound over two sessions" and the 650 are
what session one did. The second session's 60 subagents are inside for the same reason, and that
includes the 30 that attempted approaches which did not work, the 13 validators, the 2,400 shell
commands' outputs re-entering the context, the thousands of numerical checks, the 54 downloaded
arXiv papers, the independent re-proof from scratch, and the 2 subagents that assisted with the
initial paper write-up. **The run's compute therefore includes its own failed work**, which is
exactly the selection the human side also takes: the summed active time of the person who does
succeed, dead ends and all, excluding other people's failures.

**Outside, and unmeasured.** The Lean formalization. Three independent pieces of evidence put it
outside the 31 million:

- The blog puts it in a separate sentence with a different collaborator and the words "in
  parallel", after the paper write-up has already been described.
- The subagent role split has no formalization role. Two wrote paper prose; none wrote Lean.
- `zeta23/formalization.yaml` records the automation cost as `wall_time: not tracked`,
  `spend_usd: not tracked`, `hardware: not recorded`, and describes a differently-run project:
  "Humans — the paper's authors, with Eric Easley orchestrating the Lean work — directed the
  project, chose the targets and reviewed the outputs". The 1.5-day run's human input was
  "mostly limited to sending Claude messages of encouragement".

The repository's own commit history cannot substitute for a compute figure either: it is a curated
release, 30 commits from 7 August to 5 September 2026, mostly Palomar-layout and CI work, so
author-days measure the release and not the formalization.

**Also outside.** The paper's 13 August revision, and the informal condensed note, which is the two
Anthropic mathematicians' own work rather than Claude's.

### The deliverable, measured

- **Paper.** Alpöge–Furman, arXiv:2608.13637, submitted 13 August 2026, revised 19 August 2026,
  **21 pages** per the arXiv Comments field, which also reads "Proof discovered autonomously by
  Claude (Anthropic); verified and communicated by the listed authors." math.NT; MSC 11M06, 11M26,
  15A42. Abstract: at least two thirds of the nontrivial zeros counted with multiplicity are simple
  and on the critical line and at least five sixths are distinct, against previous unconditional
  records of 5/12 and 0.6603; with the Montgomery–Taylor window the constants become 0.6725 and
  0.8362. The device is a rank-trace inequality applied to a finite compression of Weil's Hermitian
  form with Sylvester's law of inertia handling off-line pairs, which makes Montgomery's 1973
  deduction unconditional. The analytic inputs are Aryan's and Baluyot–Goldston–Suriajaya–
  Turnage-Butterbaugh's, with Bombieri (2000).
- **Lean.** `github.com/anthropics/formal-math`, `zeta23/`, Apache-2.0, Lean `v4.33.0-rc2` on
  Mathlib `51e6992`. My own measurement from a clone on 16 September 2026: **326 `.lean` files,
  103,032 lines**, of which 102,265 are the `Zeta23/` proof development. Seventeen trusted statements
  in `Challenge.lean` plus six on the zeros of ξ′ in `Challenge/XiPrime.lean`, `sorry`-free outside
  those trusted files, `#print axioms` returning exactly `propext, Classical.choice, Quot.sound` on
  all 23, Comparator plus lean4export plus the NanoDa kernel in CI under a Landrun sandbox. I did
  not build it or run the kernel; the verification claims are the repository's.

### Verification and review

Two Anthropic mathematicians, Levent Alpöge and Ralph Furman, studied and validated the paper and
produced a condensed informal note; they are its listed authors. Brian Conrey and Dan Goldston,
both specialists in exactly this area, examined the paper. `formalization.yaml` records the review
status as `author-verified`: Furman read the 17 challenge statements against the paper, the ξ′
challenge module is agent-reviewed, and journal peer review is pending.

### Model identity

The blog says only "an unreleased research version of Claude". No name, no comparability anchor, no
size, no architecture.

**A new `models.csv` record is needed; neither an existing Claude record nor the Fermat one fits.**
Every released Claude record is excluded by the blog's own words. The Fermat record,
`anthropic-internal-research-flt-2026-08`, is the near miss and is rejected on its date: its
`model_release_date` is 2026-09-04, the date Anthropic announced the Fermat result, and under the
`model_release_date` rule a never-released model takes the date of the result it produced. The zeta
result was announced 2026-08-10, so reusing the Fermat record would date the model a month after
the result it is being used to price. The new record is
**`anthropic-internal-research-zeta-2026-08`**, release date 2026-08-10.

Whether the two internal models are the same model is unresolved and cannot be resolved from what is
published. They are both unreleased Anthropic research models driving Claude Code multi-agent
harnesses in the same fortnight, which is suggestive and is not evidence.

**The coefficient is 150B active, 3e11 FLOPs per token**, the same figure
`research/model-priors/anthropic.md` recommends for the Fermat internal model and carries for Fable
5 and Fable 5.1, with the same 55B to 400B sensitivity band. The Fermat record's 150B rests on a
stated Fable 5.1 anchor and this one has no anchor at all, so the choice is a transfer: an
unreleased Anthropic research model of the same month is priced as the other one. The alternative is
the dataset's shared frontier closed-model prior of 100B, which would put this model a tier below
the Fermat one on no evidence either way and move `compute_flops` to 6.68e19. The band already
spans both.

Attention shape follows `research/attention-correction.md#model-architectures` at
`attention_basis = estimated`: `L_dense = (1.5e11 / 196608)^(1/3) = 91`, Anthropic's 0.70 share
gives **64 layers**, width **11648**. Identical to the Fermat record, because the active-parameter
prior is identical.

## reas-zeta-zeros-anthropic-internal

### Compute

**Floor.** `3.1e7 × 3e11 = 9.3e18 FLOPs` in the weight matrices, or 1.85e19 with the attention term
at the central context. This counts no prompt, no system or tool definition, no shell output fed
back to a subagent, no downloaded arXiv paper, and no cache creation. It is a bound.

**The input side.** The published figure is output-only, so the input side is reconstructed by the
route `agent-work/DECISIONS.md` fixes and `research/flt-anthropic.md#compute` works out: counted
tokens are `(1 + r) × output` with `r` the appended tokens per output token, transferred from Meta
FAIR's textbook formalization at **r = 4.21**, giving **k = 5.21** and **1.6151e8 counted tokens**.

This transfer is a better fit here than it is on Fermat, for one reason and against one.

- **For.** The donor's composition is tool-result-heavy, short-output turns. The zeta run ran 2,400
  shell commands and hundreds of Python scripts, downloaded 54 arXiv papers and ran thousands of
  numerical checks, all of which return tool results into the context, and 60 subagents refereeing
  one another's work is a structure that re-reads other agents' text. That is the donor's profile.
- **Against.** A mathematics-idea run emits long reasoning and long prose per turn, which divides a
  similar tool-result volume into more output and lowers r. The Fermat note makes the same argument
  and lands at r = 3.15 under it.

The scenario table is at the central 150B and the 1e5 context:

| Scenario | k | Tokens counted | compute_flops |
|---|---:|---:|---:|
| Output only (floor) | 1.00 | 3.10e7 | 1.85e19 |
| Transfer band, low | 3.00 | 9.30e7 | 5.56e19 |
| Donor append-profile, low | 4.50 | 1.40e8 | 8.34e19 |
| **Central (recorded)** | **5.21** | **1.6151e8** | **9.66e19** |
| Donor append-profile, high | 6.30 | 1.95e8 | 1.17e20 |
| Transfer band, high | 10.00 | 3.10e8 | 1.85e20 |

**The caching premise.** The appended basis is selected over the gross one because Claude Code runs
against the Anthropic API, where the cache point moves forward automatically as a conversation
grows. That is inferred from the harness's name, not observed; Anthropic published no cache
counters. It is the same premise the Fermat row rests on and it is the largest unevidenced lever
here too.

**Attention.** `attention_context = 100,000`, the Fermat row's central for a Claude Code agent
session, carried across because the harness is the same and no per-call records are published. The
tier ladder in `research/attention-correction.md#mean-attended-context` would otherwise fall to half
the counted tokens, 8.1e7, which the 200,000 cap would hold at 200,000; a same-harness transfer is
preferred to the bare cap, and it is the more conservative of the two. `attention_ratio = 0.994`, so
attention is very nearly half the recorded total.

**Recorded.** `compute_flops = 9.6613473088e19`, `compute_method = params_tokens`,
`compute_evidence = derived_assumed_inputs`, `compute_statistic = total`, `compute_subset = all`,
`ai_attempts = 1` — two sessions of one continuous goal run, which COLUMNS counts as one attempt.

**Range.** `compute_flops_low = 4.2491e19`, `compute_flops_high = 2.2268e20`. Only the parameter
band applies: 55B and 400B active, with the attention shape re-derived by the same rule at each end
(46 layers at 8,320 wide, and 89 at 16,256), and the context held at 100,000. No context band,
because `attention_context` here is a same-harness transfer rather than the cache-implied route, and
`research/compute-range/compute-range.md` gives a context band only to rows on that route.

**Accounting limitations, all one-sided upward.**

- The Lean formalization's compute is not in the total and is not published anywhere. See
  [the work-unit section](#work-unit). It is excluded from the human side too, so the row stays
  matched, but the published deliverable is larger than the row prices.
- The 13 August revision of the paper is not described as inside the 31 million.
- Anthropic does not say whether the 31 million includes extended thinking tokens. The API counts
  thinking inside output tokens, so on the natural reading it does.
- The Python scripts, the 2,400 shell commands and the numerical checks against known zeta zeros are
  conventional computation, not neural work, and are nil in FLOPs under this schema.
- No helper model is identified. The 60 subagents are priced at the primary model's coefficient
  throughout, which is the explicit assumption COLUMNS permits; if the 13 validators or the 30
  failed-approach agents ran on something smaller, the total is overstated.

### Human baseline

The standing method is `research/math-human-time/math-human-time.md#method`, applied step by step.

**1. The deliverable.** A 21-page research paper in analytic number theory. Its content is a single
new idea — treat the whole space at once, with positive and negative definiteness together and the
quadratic form allowed to be non-diagonal, and read off a rank-trace inequality — applied to
analytic inputs that already exist in the literature (Aryan; Baluyot, Goldston, Suriajaya and
Turnage-Butterbaugh; Bombieri 2000). The blog's own technical summary says so: "The courage to treat
the entire space […] is in some sense the step that allows Claude to achieve the conclusion based on
the important prior work." That is the profile the calibration's short and medium classes describe —
one idea found and written inside a burst — and not the multi-year machinery-building programme its
large class describes.

**2. Size in pages.** 21, read off the arXiv Comments field. The line-count route is not needed and
is not used.

**3. Classify.** Number theory and analysis; a structural theorem obtained by a new device on
existing inputs; **medium** class, 13 to 60 pages.

**4. A direct record on this problem.** None exists. No human produced this result, and the prior
bounds (Levinson 1974, Conrey 1989, Pratt and coauthors 2020) carry no statement of their authors'
own time. Under the method's step 8 the history of the bound is a sanity check and never a figure.

**5. The class rate.** `21 pages × 8.3 hours per page = 174.3 active hours`.

The cross-check the method requires, against the nearest rows by area and character in
`math-human-time.md#table1`:

| Neighbour | Area | Pages | Active h | h/page |
|---|---|---:|---:|---:|
| `tao-discrepancy` | number theory | 29 | 32 | 1.1 |
| `erdos728-writeup` | number theory | 20 | 67 | 3.4 |
| `cairo-mizohata` | analysis | 15 | 300 | 20.0 |

The three bracket the class rate, 32 and 67 below and 300 above, and their median of 67 hours sits
2.6× below it, inside the 3× the method allows before the neighbours override the rate. So the rate
stands. Worth naming which way each neighbour leans: the two below are a blog-comment observation
turned into a paper in eight days and an AI-assisted Erdős write-up, and the one above is a single
author over five months on a PDE problem.

**6. Formalization.** No term. The Lean is outside the work unit, as
[the work-unit section](#work-unit) sets out, because the AI-side compute does not cover it.
Reported and not recorded, so the size of what is left out is visible: at the method's own rates a
human formalization of this paper is `21 × 417 / 12.6 = 695 hours`, and dividing the measured
103,032 machine-written lines by the human rate — which the method explicitly labels an upper bound,
since the rate's numerator is Mathlib-idiom Lean — gives 8,177 hours. Either figure would dominate
the row, which is why including it against no compute at all would be the wrong call rather than the
conservative one.

**7. The range.** The medium class's own dispersion in hours per page, 1.1 to 20.0:
**23.1 to 420 active hours**, 83,160 to 1,512,000 seconds. It is a dispersion, not a confidence
interval, and the central is the class median rather than the midpoint.

**The elapsed bound.** 174.3 hours is 21.8 working days of one person at 8 hours with no on-task
discount. That is the bound the method asks to be reported alongside; the central sits at it here
only because the rate is a per-page rate rather than a window times a fraction, and the six medium
rows behind it were themselves built at fractions of 0.25 to 0.50.

**The population.** `human_skill = expert`: analytic number theorists working on the distribution of
zeta zeros — Levinson's, Conrey's and Pratt's population, and Conrey and Goldston are the two who
read the paper. `world_class` is arguable and is not taken; the Navier–Stokes row uses it for a
Millennium problem and this is a real but incremental advance on a research frontier rather than one
of the seven.

**Recorded.** `human_time = 627480` seconds, `human_time_low = 83160`, `human_time_high = 1512000`,
`human_time_evidence = llm_estimate_from_data` (recorded timings of other problems mapped onto this
one), `human_time_statistic = point_estimate`, `human_time_subset = successful`,
`human_attempts = 30` — the donor sample is the thirty human solves in the fit of
`math-human-time.md#table1`, of which six are the medium class the rate comes from.

### Performance

`performance_vs_human = match`, **by construction, and the construction rests on what the deliverable
is**. No human has produced this result, so there is no observed human result and none is implied.
What the human duration prices is producing the same deliverable: an unconditional proof that more
than two thirds of the nontrivial zeta zeros are simple and on the critical line, at the same
constants, written up as the same 21-page paper. COLUMNS is explicit that where human time
explicitly estimates reproducing the AI output at comparable quality, the label is `match`.

The AI side of the criterion is met and externally examined rather than merely asserted: the paper
is validated by two mathematicians who put their names on it, examined by Conrey and Goldston, and
the headline theorems are formalized sorry-free in Lean on Mathlib alone with Comparator and a second
kernel in CI. Journal peer review is pending, and the row's `performance_evidence` says so.

### Comparison issues

`none_identified`. The human estimate and the AI run are the same unit — the same theorem at the
same constants, written up at the same length — and the Lean artifact is excluded from both sides
rather than from one.

Considered and not flagged:

- **The estimated human baseline.** COLUMNS is explicit that an estimated baseline alone is not a
  known difference.
- **The run's own failed work.** The 650 ideas, the 30 failed subagents and the 2,400 shell commands
  are inside the AI's counted compute, and the human quantity is the successful solver's own active
  time including their own dead ends, so the two selections match. The 2026-09-16 ruling says not to
  flag `different_attempt_selection` on this pairing.
- **The prior literature.** Aryan, Baluyot–Goldston–Suriajaya–Turnage-Butterbaugh, Bombieri and
  Montgomery are granted to both sides, as Mathlib is on the Fermat row.
- **The human prompting.** "Take a real stab", one "try again", and messages of encouragement. No
  mathematics, and the blog states the mathematical choices were left to the model.

## What a reviewer should attack

1. **The work unit, which differs from the brief's premise.** Damon's ruling named the whole run
   that produced the paper and the Lean. The published evidence puts the Lean in a separately
   directed, unmetered project, so the row prices the research run only and says so. If Damon wants
   the Lean inside, the honest form is a second row or a scenario, not a human-side term with no
   compute against it.
2. **r = 4.21 and the caching premise behind it.** Inherited whole from Fermat, transferred from a
   donor run in a different scaffold on a different model generation. The k = 3 to 10 band is meant
   to cover it.
3. **150B active with no stated anchor.** The Fermat record's 150B has a Fable 5.1 anchor; this one
   is a transfer from that record on nothing more than both models being unreleased Anthropic
   research models in the same fortnight. 100B is the defensible alternative and gives 6.68e19.
4. **8.3 hours per page.** A median over six medium-class solves whose own hours-per-page span 1.1
   to 20.0, applied to a paper in an area the calibration covers but on a problem it does not.
5. **`expert` rather than `world_class`**, given that the people who have moved this particular
   constant are Levinson, Conrey and Pratt.
6. **A 100,000-token mean context** transferred from the Fermat note's judgment for a Claude Code
   session, which is a judgment and not a measurement, and which sets nearly half the recorded FLOPs.

## Sources

- [Anthropic, Claude's progress on the Riemann hypothesis](https://www.anthropic.com/research/riemann-zeta), 10 August 2026, updated 13 August 2026
- Alpöge and Furman (2026), [arXiv:2608.13637](https://arxiv.org/abs/2608.13637), "More than two thirds of the zeta zeros are simple and on the critical line", 21 pages, v1 13 August 2026, v2 19 August 2026
- [anthropics/formal-math](https://github.com/anthropics/formal-math), `zeta23/`: `README.md`, `AUDIT.md`, `formalization.yaml`, `Challenge.lean`, `comparator.json`. Line counts and commit history are my own measurements from a clone on 16 September 2026
- [Aryan](https://arxiv.org/abs/1902.05473); [Baluyot, Goldston, Suriajaya and Turnage-Butterbaugh](https://arxiv.org/abs/2306.04799) and [its sequel](https://arxiv.org/abs/2501.14545); [Bombieri (2000)](https://eudml.org/doc/252338)
- Arithmetic: `research/zeta-zeros-anthropic/compute_zeta_zeros.py`, output in `agent-work/derived/zeta-zeros-anthropic/calculations.json`
- Method and rates: `research/math-human-time/math-human-time.md`; input-side reconstruction and the Claude Code caching premise: `research/flt-anthropic.md#compute`; attention recipe and shapes: `research/attention-correction.md`; parameter prior: `research/model-priors/anthropic.md`; range rules: `research/compute-range/compute-range.md` and `research/human-range/human-range.md`
