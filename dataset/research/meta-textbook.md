# Meta FAIR automatic textbook formalization — Claude Opus 4.5

*Created 2026-09-13 10:31.*
*Last revised 2026-09-16 11:44. The human side is rebuilt on the research-mathematics
calibration in `research/math-human-time/math-human-time.md`, Damon's standing method of
2026-09-16 for research-mathematics rows. The figure falls 22%, from 12,000 active hours to
9,313, and the two estimates were independent, so the agreement is a corroboration of both. The
compute side is unchanged.*

## Summary

One candidate row, `reas-lean-textbook-algcomb-opus45`, for the one-week run in which 30,046
Claude Opus 4.5 agents formalized Darij Grinberg's graduate algebraic combinatorics textbook into
Lean 4 and proved all 340 designated target theorems and definitions (arXiv:2604.03071).

- **Compute: 1.67e22 FLOPs.** 83,176M input plus 561.2M output tokens at the dataset's
  `claude-opus-4-5` coefficient of 2e11 FLOPs per token. **No prompt caching applied**, so the
  harness re-processed each agent's entire dialog on every one of its turns and all 83.2B input
  positions are real forward passes. No caching directives exist anywhere in the released code,
  and caching is documented as impossible on the compatibility endpoint that code calls; the run's
  own configuration is not published, which is the limit on the determination. **The gap between
  this figure and the 7.09e20 appended basis is a property of the harness, not of the task**: the
  same work on a caching harness would have cost a fraction of it. That basis is the counterfactual
  the paper itself priced at $100K, and 23.6x is the ceiling on the gap rather than its realized
  size, since cache TTL would cap the saving. Coordinator ruling, 2026-09-13: gross is central,
  appended is carried as the scenario.
- **Human: 33,526,800 seconds (9,313 active hours, 4.7 person-years at 2,000 hours each), expert,
  range 7,823 to 21,731 hours.** An estimate, not a timing. Built from 117,350 human-idiom lines
  of Lean — 500 pages of main text at the calibration's 235 formal lines per textbook or
  blueprint page — over its 12.6 formal lines per active hour, measured on eight completed
  formalization projects. The withdrawn route, 90,000 human-equivalent lines at 15,000 lines per
  expert person-year, gave 12,000 hours from a different numerator and a different rate; the two
  agree to within 22%.
- **Performance: match**, by construction, since the human estimate targets the same deliverable.
  Flagged `different_assessment` and `different_inputs_or_tools`.

- **Transfer anchor for the FLT and Navier-Stokes rows: r = 4.2 appended input tokens per output
  token, band 3.5 to 5.3, so k = 1 + r = 5.2, band 4.5 to 6.3.** Appendix A's 2/(T+1) is convex in
  T, so applying it once at the aggregate overstates; applied to Table 2's eight roles it gives
  4.21, and to Table 3's outcome classes 4.58. See `#transfer-anchor`.

The two numbers a reviewer should attack are the caching call, which moves compute by a factor
of 24, and the 235 lines per textbook page, which sets the size of the human job and is the one
factor in the human side with no counterpart in this project's own record.

## Sources and their locators

| What | Where |
|---|---|
| The paper | arXiv:2604.03071v1, https://arxiv.org/html/2604.03071v1, retrieved 2026-09-13. Submitted 3 Apr 2026; internal dateline "March 31, 2026" |
| Tables 1, 2, 3, the cost paragraph and Appendix A, verbatim | `agent-work/sources/meta-textbook/paper-token-tables.md` |
| The same tables as machine-readable input | `agent-work/sources/meta-textbook/paper-token-tables.json` |
| The orchestration code | https://github.com/facebookresearch/repoprover, cloned 2026-09-13 |
| Call path, token counters, caching absence, and Anthropic's compatibility-layer documentation | `agent-work/sources/meta-textbook/repoprover-api-extracts.md` |
| The delivered artifact | https://github.com/facebookresearch/algebraic-combinatorics at `b6022318e986a0c20764569208ba8ebbe1c04dbf` (2026-04-01) |
| My own measurements of that artifact | `agent-work/sources/meta-textbook/algcomb-repo-measurements.md`, reproducible with `research/meta-textbook/measure_repo.py` |
| Human-side anchors, verbatim | `agent-work/sources/meta-textbook/human-formalization-anchors.md` |
| All arithmetic | `research/meta-textbook/calculations.py` writing `agent-work/derived/meta-textbook/calculations.json` |
| Source textbook | Darij Grinberg, "An Introduction to Algebraic Combinatorics", arXiv:2506.00738v1, 31 May 2025, 703 pages |
| Model record | `../AI Compute vs Human Time/dataset/models.csv`, id `claude-opus-4-5` (read-only reference; nothing in that folder was modified) |

The scouting inventory at `research/scouting/long-running-feats.md` supplied the lead. Every
number below was re-derived from the paper and the public code; none was inherited from it. One of its figures is wrong and is corrected here: the paper was submitted 3 April 2026, not 31
March.

On the target count, the paper is consistent and the row follows it. Section 3.2: "we designate
340 definitions and theorems in the Latex source as targets of the formalization." Section 3.3:
"formalizing all 340 target theorems and definitions. Four initial targets were correctly
reclassified as exercises in the source and not attempted." Table 1 reads 340 targets of which 340
proved, and the artifact's `README.md` agrees. The requirement is therefore **340 targets, all of
them met**. `manifest.json` carries 344 entries because it retains the four reclassified
exercises, and `SUMMARY.md` and `CONTENTS.md` present that as 340 of 344, or 99%. That is a fair
description of the manifest and the wrong description of the completion criterion, and the row
does not use it as a denominator.

## What was produced

The unit of work is one continuous goal-directed run. A multi-agent scaffold called RepoProver
launched 30,046 Claude Opus 4.5 agents in eight roles onto a shared git repository over one week
of wall-clock runtime, restarting the orchestrator several times on its own performance problems.
Each agent worked on a short-lived git worktree and submitted a pull request that had to merge
cleanly, build, and pass both a mathematical review agent and an engineering review agent before
it entered the main branch.

The deliverable is the Lean 4 repository. Measured at the released head:

| Quantity | Value |
|---|---|
| Lean source files | 52 |
| Lines of Lean | 130,062 |
| Lean declarations | ~5,900 (the paper's figure; my line-oriented count is a lower bound and I did not reproduce it) |
| Designated targets, in scope | 340 across 45 chapters |
| Targets proved | 340 |
| Entries retained in `manifest.json` | 344, the 340 in scope plus 4 reclassified as exercises |
| `sorry` tactic uses | 5, all inside the 4 exercise targets |
| Lean toolchain | `leanprover/lean4:v4.28.0`, mathlib pinned at `v4.28.0` |

"Proved" means what the repository's own assessment policy says it means: "A theorem is marked
PROVED only if it and all its transitive dependencies are `sorry`-free." The repository pins Lean
4.28.0 and mathlib `v4.28.0` and the paper reports the build passing, which would put every
declaration through the Lean elaborator and kernel except where a tactic deliberately steps
outside it; that exception is the qualification in the performance section below. I did not run
`lake build`, so the build is attributed rather than observed here.

The source is a 703-page arXiv posting, of which roughly 500 pages are main text; the appendix of
over 200 exercises is out of scope, and the paper prices the run at "around $200 per page" against
that ~500-page body. The targets were chosen by a prompted LLM over the LaTeX source, and the
subject matter was chosen because it is reachable from mathlib but largely absent from it: formal
power series, integer partitions and q-series, permutations, determinants, sign-reversing
involutions, symmetric functions through the Littlewood-Richardson rule, and lattice paths.

**The equivalent human deliverable** is the same repository: Lean 4 statements and complete proofs
for those same 340 targets, against the same mathlib, sorry-free through all transitive
dependencies, built by qualified formalizers without AI assistance. That is what the human-time
estimate below prices.

## reas-lean-textbook-algcomb-opus45

### Compute

**The token totals.** Table 2 of the paper gives per-role counts and its own totals: 30,046
agents, 83,176M input tokens, 561.2M output tokens, 1,645,274 turns, 54.8 turns per agent. The
column sums reproduce the printed totals to rounding (83,175 against 83,176; 561.0 against 561.2;
counts and turns exact), and the prose repeats them: "a total of 83B input tokens (with multiple
counting in multi-turn dialogs) and 561M output tokens".

Table 3, the same tokens broken down by outcome instead of by role, covers 29,691 agents and
80,686M input tokens. It is short by 355 agents and 2,490M input tokens and the paper does not
reconcile the two. I use Table 2, which is the set the prose quotes and the larger of the two;
the difference is 3% of the input total and would not change the row.

**Price cross-check on the transcription.** At Claude Opus 4.5 list pricing of $5 and $25 per
million tokens, Table 2's totals give $415,880 of input and $14,030 of output, $429,910 in all.
The paper states $430K uncached with $14K of it output. The transcription and the pricing are
therefore both right.

**Caching: the decisive question, and the answer.** The paper's Appendix A defines its input
counter C as "total number of tokens processed in inputs, with double counting due to reprocessing
of previous messages", and opens: "our logs only contain the total number of input and output
tokens per agent dialog, ignoring input caching efficiencies". So 83,176M is the full re-read
prefix summed over every turn of every agent, not a fresh-input counter. Whether those positions
were actually computed depends on whether the API served them from a cache.

It did not, on the evidence available, though that evidence is about the released code rather
than about the run's own configuration, which is not published.

1. **No caching directives exist anywhere in the released code.** RepoProver calls the model
   exactly once, in `_call_with_retry`, with a request body of `model`, `max_tokens`,
   `temperature`, `messages` and `tools` and nothing else. A repository-wide search for
   `cache_control`, `ephemeral`, `prompt_cach`, `cache_creation` and `cache_read` returns no
   matches, and there is no `extra_body` anywhere. This holds whatever endpoint was used.
2. **Caching is documented as impossible on the default endpoint.** The client is the OpenAI SDK
   pointed at `https://api.anthropic.com/v1/`. Anthropic's documentation for that compatibility
   layer states plainly: "Prompt caching is not supported, but it is supported in the Anthropic
   SDKs", and lists `usage.prompt_tokens_details`, where a cached-token count would appear, as
   "Always empty".
3. **A small signal that the default endpoint is the one that was used.** The client sets
   `default_headers={"anthropic-beta": ""}`, a header that means nothing anywhere except
   `api.anthropic.com`.

The limit on this is worth stating plainly rather than glossing. **The run's own configuration is
not committed anywhere in the repository**: `PROVIDER_DEFAULT_MODELS["anthropic"]` is
`claude-sonnet-4-20250514` while the run used Claude 4.5 Opus, and `configs/example.yaml` carries
no provider, model or `base_url`. So item 2 establishes impossibility on a path that item 3 makes
likely but does not confirm. The empty `prompt_tokens_details` is consistent with the paper's
"our logs unfortunately do not contain token caching statistics" and is the simplest explanation
for it, but it is an inference about why the authors lacked the numbers, not proof, and a proxy
that failed to surface cache counters would look the same.

So the $100K in the abstract and the conclusion is a counterfactual price for a caching
configuration the released code does not implement. The price the run would actually have been
billed is $430K. This matters for the row because the parameter-multiplication term counts
forward passes, and under COLUMNS' `params_tokens` rule the applicable clause is the documented
processing estimate supported by the implementation evidence, which here says every input
position was processed once.

**The value.**

    compute_flops = (83,176e6 + 561.2e6) x 2e11 = 1.674744e22 FLOPs
    tokens        = 83,737,200,000, accounted as input_output

`tokens_accounting` is `input_output`, not `input_cache_creation_output`, and `compute_method` is
`params_tokens` with **nothing removed from the parameter-multiplication term**. Both follow from
the same fact: the counters partition into prompt tokens and completion tokens and nothing else,
there is no cache-creation counter, and there are no cache reads to exclude because none occurred.
COLUMNS' instruction to "include material padding or repeated forwards implied by the same
implementation" is what governs here, and the repeated forwards are the 27.9x re-read of each
dialog prefix.

**The appended-basis scenario, which is the counterfactual the paper itself priced.** The $100K in
the abstract is what this run would have cost on a caching harness, and the matching compute
figure is what it would have spent there. The residual uncertainty that would make that scenario
the truth is narrow and specific: `base_url` is configurable, so Meta may have routed through an
internal gateway that inserted cache breakpoints, in which case only newly added positions would
have been computed. Appendix A's own geometry gives the size of that
scenario: with C = 83,176M, N = 30,046 and T = 54.76, the average tokens added per turn is
m = 2C/(N·T·(T+1)) = 1,813, the average final dialog length is L = T·m = 99,296, and the distinct
input positions are N·L = 2.983e9, a factor of 27.9 below C. Compute would then be
(2.983e9 + 0.561e9) x 2e11 = 7.09e20, a factor of 23.6 below the recorded value. I reproduce the
paper's own $100K from this same geometry ($100,370 against its $100K), which is a check that I
have read Appendix A correctly rather than evidence that caching happened.

One more thing about that scenario: 7.09e20 is a floor for it, not its value. The saving a
caching harness realizes is capped by cache TTL as well as by geometry. Anthropic's default cache
is five minutes and Appendix A prices the one-hour tier, and Figure 5's own account of the run,
"NFS bottlenecks, git worktree timeouts and merge queue congestion", describes exactly the
conditions in which inter-turn gaps exceed a TTL and a prefix has to be rewritten. The true cached
figure would sit above 7.09e20, which makes the gap to the recorded value smaller than 23.6x and
strengthens rather than weakens the gross ruling.

**What the 23.6x factor is and is not.** It is the re-read multiple C/(N*L) = 27.9 on the input
side, diluted by output tokens that are generated once. It is a fact about the harness, not about
the difficulty of formalizing the textbook: an identical run on a caching harness would have
delivered the same 340 proved targets for about a twenty-fourth of the FLOPs. A reader comparing
this row against other agentic rows should read it as a measurement of what was spent, not as a
measurement of what the work unit requires.

**Helpers and omissions.** Every agent in the tables is Claude Opus 4.5 and no second model is
named, so no helper coefficient is needed. Four workloads sit inside the stated work unit and
outside the counted total, all of them unquantified in the source and all of them additive:

- **Compaction calls.** RepoProver compacts an agent's context when the next prompt would exceed
  150,000 tokens. Compaction is recorded on a separate `"compaction"` event which does not
  increment the recorder's running totals, and `count_tokens.py` sums only `msg` events, so these
  forward passes are outside Table 2. Each is one call of roughly 150K input tokens. The number of
  compactions is not published.
- **The first hours of the run.** Figure 5's caption: "Detailed token statistics are not available
  for the first hours of the run."
- **Short debugging runs**, which Figure 5 says are excluded.
- **The manually launched status agents.** The authors "manually interrupted the run a few times
  and launched CLI agents" to produce status reports, and did not implement them in the code base,
  so their tokens are not in the run's logs. They also used "a prompted LLM" to designate the
  targets before the run.

**Retries, failures and aborted work are inside the unit, not outside it.** Only 3,490 of 29,691
classified agents merged a pull request, and 53% of Table 3's input tokens went to aborted agents
that were dropped across orchestrator restarts. All of it is counted, which is what
`compute_subset = all` on a single continuous goal run means. The paper expects a "3-10x decrease
in inference cost" from fixing the orchestration; that is a claim about a future run, not a
correction to this one.

**Method and evidence labels.** `compute_method = params_tokens`; `compute_statistic = total`;
`compute_subset = all`; `ai_attempts = 1`, since a continuous goal run counts as one attempt
including its restarts. `compute_evidence = derived_assumed_inputs`: the token counts are
measured and reported, but the 100B active parameter size behind the coefficient is the dataset's
Opus-family assumption and is the substantial assumed input. At 30B and 300B the value moves to
5.02e21 and 5.02e22.

**Attention.** The 2 x active_parameters convention omits attention over the context, which
`research/attention-correction.md` has since folded into `compute_flops`, and
this run re-reads its whole prefix on every one of 1,645,274 calls at a mean prompt length of
50,554 tokens, so the term is large. Under Appendix A's geometry the sum of squared prompt
lengths over the run is N·m²·T(T+1)(2T+1)/6 = 5.56e15, with an RMS prompt length of 58,113. Using
the 4·n_layers·d_model·n_context recipe, so that a prefill of N positions costs about
2·n_layers·d_model·N², and bracketing architectures at ~100B dense-equivalent active parameters:

| Architecture | n_layers | d_model | Attention FLOPs | As a fraction of the recorded value |
|---|---|---|---|---|
| Wide, shallow | 48 | 13312 | 7.62e21 | 0.46 |
| Central | 80 | 10240 | 9.76e21 | 0.58 |
| Narrow, deep | 126 | 8192 | 1.23e22 | 0.74 |

These use the per-role sum of squared prompt lengths, 5.90e15, rather than the single aggregate
application, 5.56e15. Unlike the transfer anchor, this term is robust to the population's
heterogeneity: correcting for it moves the attention estimate by 6%, against 21% for the anchor,
and in the opposite direction, because the sum of squares is dominated by the long-dialog roles
the aggregate form under-weights. The term is one-sided and would add 0.46 to 0.74 times the
recorded value. It is the largest
attention correction of any row in this folder, because unlike a cached agent loop every prefix
token here is attended over afresh on every turn. Per `DECISIONS.md` the recorded `compute_flops`
stays on the dataset's convention; changing that convention is a dataset-wide decision.

### Human baseline

`human_time = 33,526,800` seconds. This is **9,313 active hours**, summed across whatever team
size is used, which is 4.7 person-years at the 2,000 active hours per person-year that
`DECISIONS.md` fixes.

**The method, per Damon's ruling of 2026-09-16.** This row is priced by the
research-mathematics calibration in `research/math-human-time/math-human-time.md`, the standing
method for research-mathematics rows. `human_time_evidence = llm_estimate_from_data`, because
the rate comes from the calibration's eight completed formalization projects, each measured on
both ends; `human_time_subset = successful`, `human_attempts = 8` for those projects,
`human_time_statistic = point_estimate`.

**There is no solve term.** Step 1 of the method asks what mathematics the human has to find,
and here the answer is none: Grinberg's textbook contains every proof written out in full, so
the job is translation. The whole figure is the formalization term.

**Step 1: the human-idiom size of the deliverable.** The calibration's Table 2 splits its size
ratio by what counts as a page, and the split is the practical finding: a research paper
written for experts compresses at 417 formal lines per page with a spread of 7.3×, and a
blueprint or textbook — prose written so a non-expert can follow every step — compresses at
**235 formal lines per page with a spread of only 1.9×**. A textbook is blueprint-grade prose,
so the blueprint ratio applies, and it is the tighter of the two.

    500 pages of main text x 235 lines per textbook page  =  117,350 human-idiom lines

Grinberg's book is 703 pages, of which about 500 are main text. The artifact itself is 130,062
machine-written lines, which is not the same quantity and is not used: the paper documents its
own duplication — an N-partition type independently defined three times and still not fully
unified at release, a Bender-Knuth involution defined twice and wrongly in both versions before
being fixed, agents that "against explicit order" built out incomplete Pfaffian and FKT theory
for Kasteleyn's formula, and "a few superficial files that essentially restate theory about
formal power series or the fundamental theorem of symmetric functions from mathlib".
`SUMMARY.md` reports 174K lines added against 47K removed. **That the two counts land 11%
apart is a check on the 235 and not a use of the artifact**: a machine-written count above a
human-idiom estimate is the expected direction, and the margin here is small because the source
left nothing to discover.

**Step 2: the rate.** `hours = human-idiom lines ÷ 12.6 formal lines per active hour`, the
calibration's median over eight projects, band 5.4 to 15.0, a dispersion of 2.8. It is the
tightest number in that note: five independent Lean projects measured the same way land between
8.6 and 15.0, and the two Coq-era projects at 5.2 and 5.4, which is a 2.4× tooling improvement
over fifteen years in the right direction and of the right size.

    117,350 / 12.6  =  9,313 h  =  4.7 person-years of 2,000 hours

**Step 3: the range.**

| Scenario | Human-idiom lines | Lines per active hour | Hours | Seconds | Hours per target |
|---|---:|---:|---:|---:|---:|
| Low | 117350 | 15.0 | 7823 | 28162800 | 23.0 |
| **Central** | 117350 | 12.6 | **9313** | 33526800 | 27.4 |
| High | 117350 | 5.4 | 21731 | 78231600 | 63.9 |

**The bounds are the calibration's own dispersion and nothing else.** No default factor is
applied. They are the formalization rate's measured band across its eight projects. The page
ratio is held at 235 at both ends, because varying it alongside the rate would compound two
discretionary steps; its own dispersion is 216 to 414, and the high end of that would raise the
central to 16,429 hours on its own.

**The per-target column is the sanity check I trust most**: 27 hours of expert time per target
theorem or definition, averaged over a set running from one-line definitions to the
Littlewood-Richardson rule and the Bender-Knuth involutions the paper calls "the most
challenging part of the project". That is the right order, and it is close to the 35 the
withdrawn route gave.

**Population.** `human_skill = expert`. Producing sorry-free Lean 4 proofs against mathlib at
graduate-textbook level needs substantial relevant training; the realistic population is mathlib
contributors and research-level proof engineers. Not `world_class`, which would imply selection
at the top of a competitive field rather than professional competence.

**On the hours-per-year conversion.** `DECISIONS.md`, "Person-years and active hours" (Damon,
2026-09-13), fixes one person-year at 2,000 active hours and requires any less-than-full-time
engagement to be stated as an on-task fraction rather than smuggled into a lower hours-per-year
figure. No fraction is applied here and none is hidden: the calibration's 12.6 is lines per
*active* hour, measured as author-days times a stated hours-per-session factor, so it already
prices sessions rather than calendar employment.

**What the paper gives, and what it does not.** The paper's only human comparison is a price:
"This price tag approaches, and may even undercut, the one required for a formalization by a team
of human experts", and "it required one week, dwarfing typical human project timelines". No
headcount, no duration and no hours appear anywhere in it. A dollar figure is not a timing and is
not used as one here.

#### The withdrawn route, and why its agreement matters

The earlier estimate took **90,000 human-equivalent lines at 15,000 lines per expert
person-year**, giving 6.0 person-years, 12,000 hours, with 5,600 to 26,000 as the bracket. Its
size came from Gonthier et al.'s ~160 lines per page of informal text applied to Grinberg's
500 pages and then raised by judgment; its rate came from three anchors — seL4 at 15,000 and
10,000 lines per person-year, and the Imperial FLT project at 10,000 to 15,000 once its FTE
assumption was stated — with 15,000 taken as the top of the band.

**Both factors are replaced and the answer barely moves**, from 12,000 hours to 9,313, 22%
apart. The numerators differ — 90,000 lines against 117,350 — and so do the rates: 15,000 lines
per person-year is 7.5 lines per active hour, against the calibration's 12.6. The two errors
run opposite ways and mostly cancel. That is a corroboration rather than a coincidence, because
the two routes share no input: the calibration's page ratio is measured on four projects with
both a line count and a page count, and its hourly rate on eight with both a line count and an
author-day record, where the withdrawn route used one informal-text ratio from 2013 and three
project-level person-year totals.

The Imperial FLT anchor inside the withdrawn route carries the defect the calibration
identifies: its denominator was funded FTE, not observed work, and the grant runs 1.4 to 1.9×
above the project's commit record. Restated on the observed record the same project gives 13.5
lines per active hour, inside the calibration's band.

If mathlib's aggregate throughput were the right rate rather than a project-specific one, the
figure would run past 20 person-years and outside this range. I did not use it, because
mathlib's cost includes generality, API design and review burden that a one-off textbook
project does not carry, and because no contributor-hour accounting for mathlib exists.

**Cost cross-check, kept separate from the timing.** At a fully loaded $150K per expert
person-year, the central 4.7 person-years is about $700K of salary. The paper's $100K would be
0.67 person-years, about seven times below this estimate; the $430K the run would actually have
been billed is about 2.9 person-years, which lands within the range. So the paper's headline
claim survives at the price the run really carried and overstates the margin at the price it
quotes. This is a cost observation. It sets no field and contributes nothing to `human_time`.

### Performance

`performance_vs_human = match`, by construction under COLUMNS' rule that a human-time estimate
explicitly targeting work of comparable quality to the AI output makes the comparison a match.
The human target is the same 340 proved targets in the same repository shape, and there is no
observed human result to compare against, because nobody has formalized this textbook by hand.

**The standard the AI met.** All 340 designated targets are proved, each sorry-free through its
transitive dependencies. The repository pins `leanprover/lean4:v4.28.0` and mathlib `v4.28.0` and
the paper reports the build passing; I did not run `lake build`, and the repository's only GitHub
workflow is a Pages deploy rather than Lean CI, so the build is attributed to the paper and the
toolchain pins rather than observed here.
The 5 remaining `sorry` tactics sit inside the 4 initial targets the system correctly reclassified
as exercises in the source and did not attempt, and the repository states that "there are no
theorems blocked by upstream sorries".

**Two qualifications, both of which I established rather than took from the paper.**

First, "kernel-checked" is not exactly right. I count 170 `native_decide` tactic invocations, 141
of them outside `example` blocks: 116 in `lemma`, 21 in `theorem`, 4 in `def`. `native_decide`
closes a goal by compiling and running a decision procedure and adds the `Lean.ofReduceBool`
axiom, so the result is trusted from the compiled evaluator rather than reduced by the kernel.
Load-bearing instances exist: `cauchyMatEval_det_three` through `cauchyMatEval_det_seven` in
`DesnanotJacobi.lean` feed the `thm.det.cauchy` target, and `pentagonalCoeff_zero` is a `@[simp]`
theorem. The repository contains no `#print axioms` anywhere, the PROVED criterion checks
`sorry`-freeness only, and no independent kernel replay is published. The contrast with
`anthropics/fermats-last-theorem`, which bans `native_decide` outright and ships a
`#guard_msgs`-checked axiom audit plus two external checkers, is the standard this artifact does
not meet.

Second, faithfulness to the source was assessed by review agents plus manual spot checks, in the
authors' own words: "We generally observed a high statement formalization quality bar imposed by
the review agents and manually spot-checked key statements and definitions. This gives us a high
degree of confidence in the overall correctness of the formalization, but it remains a possibility
that individual theorems and definitions have not been translated semantically faithfully." A
human formalization project would have every target statement read by a human. The blueprint
website exists so the community can check, but no such check is reported.

Both go in `comparison_issues` as `different_assessment`, and the direction is worth stating: the
human baseline is priced for a deliverable that is *better* than the one delivered. "Qualified
formalizers without AI assistance" implies every target statement read by a human and, on the FLT
project's standard this note cites approvingly, no `native_decide` at all. So `match` by
construction prices somewhat more work than the AI performed, which biases `human_time` upward and
makes the row conservative rather than generous toward the AI.

`different_inputs_or_tools` covers a second concrete difference: the agents had no internet access
and worked from the LaTeX source plus mathlib search tools, a git subset and an allowlisted shell,
while the human baseline assumes the ordinary working conditions of a formalizer, including the
literature and the Lean community. The restriction runs against the AI, and the paper imposed it
to rule out copying.

I did not flag `different_attempt_selection`. Both sides are all-inclusive: the compute counts
every agent including the 53% of input tokens burned on aborted ones, and the human rate anchors
are whole-project efforts that likewise include their own dead ends.

### Task category

`mathematics_puzzles`. COLUMNS names proofs explicitly under that category and instructs
classifying the whole task rather than its output format. The work is producing proofs of stated
mathematical theorems; the human time I estimate is dominated by writing those proofs, and so is
the agents' token spend.

The alternative I considered and rejected is `coding`, and its strongest form is quantitative:
maintainer agents consumed 44,770M of the 83,176M input tokens, 54% of the run, against provers'
25,012M or 30%, so by compute the majority of the run was repository maintenance rather than proof
search. The paper frames the task the same way ("a formalization project is nothing more than a
code repository in a special-purpose programming language that needs to build without errors") and
claims "a record in multi-agent software engineering". But the merge queues, review cycles and refactoring churn are overhead created by running
30,000 agents in parallel on one repository, not intrinsic to the work unit; a human team doing
the same job would spend its time on the mathematics. The dataset's existing Lean row,
`reas-lean-minif2f-deepseekprov2-cot32`, is also `mathematics_puzzles`. A reviewer who disagrees
should say so; the choice is close.

### Model record

`model_id = claude-opus-4-5`, reused unchanged from
`../AI Compute vs Human Time/dataset/models.csv`: 2e11 FLOPs per token, 1e11 active parameters,
`estimated`, released 2025-11-24. No new model is added by this row, so
`candidates/meta-textbook/models.csv` carries the header only.

The row's `source_record` was trimmed to the dataset's length norm, so three details it used to
carry live here instead: the source textbook is Darij Grinberg, "An Introduction to Algebraic
Combinatorics", arXiv:2506.00738v1; the model was called through Anthropic's OpenAI SDK
compatibility endpoint; and the run configuration is as below.

The paper names the model as "Claude 4.5 Opus" and gives no API snapshot string; the released
configuration defaults to a different model and does not record the one used. The price
cross-check above is consistent with Opus 4.5 list pricing and rules out a cheaper tier. Note that
`temperature` was set to 0.7 and no `thinking` parameter was passed, so the output counter is
plain completion tokens with no separately billed reasoning.

## Transfer anchor

*Appended input tokens per output token, for rows that transfer this run's dialog shape.*

The FLT and Navier-Stokes rows use this run as the donor for how much input a long agentic dialog
carries per output token. This section is shared evidence: it describes the dialogs, not this
row's compute, which is settled separately in `#compute`.

### Three quantities, and which is which

The three get confused, so they are named once here and used consistently.

| Quantity | Definition |
|---|---|
| Non-output appended per output token | Tool results, user turns and system prompt appended to dialogs, per output token. Excludes the model's own output. |
| **r**, total appended per output token | All distinct input positions ever appended, per output token. **Includes the model's own output re-entering the next prompt**, except the final turn's, which is never re-appended. |
| **k = 1 + r**, total processed per output token | Every appended input position plus the output generation itself. |

k is the quantity COLUMNS' `params_tokens` counts, because re-entered assistant output is a
cache-creation position that is processed again, not a cache read, and the clause excludes only
cache reads. **r must not be relabelled as k.** `reviews/navier-stokes-openai-independent.md` §9
records as required that this note relabel its headline figure as k with r alongside, on the
reading that appended/output is already total processed. That reading drops the output generation
itself and would move the FLT row down 19% for the wrong reason. This note's own cached scenario
is internally consistent with the convention above: `tokens_if_caching_had_applied` = N·L + output,
i.e. k = 1 + r, and `research/flt-anthropic.md` uses the same convention. Flagged for the
coordinator.

### Why the aggregate application is an upper bound

Appendix A models an agent as appending m tokens per turn and re-reading the whole prefix, so the
gross counter is C = N·m·T(T+1)/2 and the tokens ever appended are N·L = 2C/(T+1). For a single
agent the identity is exact. Summed over a heterogeneous population it is not: 2/(T+1) is convex
in T, and agents with large C also have large T, so applying it once at the aggregate overstates.
The population here is heterogeneous, with role-level T from 12.7 to 235.1 and an input-weighted
mean T of about 101 against an unweighted 54.8.

The paper supplies two independent partitions, and applying the identical model within each gives:

| Application | Appended | Non-output / output | r | k |
|---|---|---|---|---|
| Front-loaded profile per role, B = 10,000 | 2,122.7M | 2.80 | 3.78 | 4.78 |
| **Per role, Table 2's eight roles** | **2,362.7M** | **3.23** | **4.21** | **5.21** |
| Per outcome, Table 3's seven classes, on Table 3's own output | 2,487.2M | 3.60 | 4.58 | 5.58 |
| Once at the aggregate | 2,983.4M | 4.33 | 5.32 | 6.32 |

Both finer partitions land below the aggregate, which is what convexity predicts, and within-role
heterogeneity pushes further in the same direction. So 5.32 is an upper bound under Appendix A's
model, not a central. Note what this correction is and is not: 2/(T+1) is the donor-side conversion
from the gross counter the paper reports to the appended tokens the anchor needs, so T belongs to
the measurement of this run rather than to the ratio being transferred. See the recommendation
below.

### What bounds the low end

The harness carries a large fixed prefix on every request. Measuring the released tool schemas
directly: `FILE_READ_TOOLS` 4,001 characters, `FILE_WRITE_TOOLS` 9,575, `GIT_WORKTREE_TOOLS`
11,876, `MATHLIB_TOOLS` 4,593, `SHELL_TOOLS` 870, `LEAN_TOOLS` 830, totalling 31,745 characters or
about 7,936 tokens, and the mode system prompts in `contributor.py` add another 347 to 2,144
tokens. Every request re-sends the whole `tools` array, so every first prompt carries roughly
8,300 to 10,100 tokens before any task content.

That kills the growing-append profile this note previously used as its upper bound: a profile in
which turn i appends a·i puts about 1,800 tokens in the opening turn, which this harness cannot
produce. Front-loading is established by the code; growth is not. Running the front-loaded model
per role at B = 10,000, which the measured prefix supports, gives 3.78.

### Recommendation

**r central 4.2, band 3.5 to 5.3.** Equivalently, non-output appended per output token 3.2, and
**k = 1 + r central 5.2, band 4.5 to 6.3**. The central is Appendix A's model applied to Table 2's
eight roles, with the outcome partition's 4.58 as the nearby alternative. The band runs from the
front-loaded profile at the measured fixed prefix up to the single aggregate application, and its
dominant source of spread is between-agent heterogeneity, the one effect measurable from the
source; within-role heterogeneity is not measurable and pushes down.

**What the transfer actually depends on, and it is not dialog length.** Write the ratio out:
r = N·L / output = N·T·m / (N·T · output-per-turn) = m / output-per-turn. **T cancels.** r is the
per-turn composition of a dialog, the appended tokens per turn divided by the output tokens per
turn, and nothing else. The figures above bear this out exactly: 1,436.0 appended per turn against
341.1 output per turn is 4.21, and the aggregate's 1,813.3 against the same 341.1 is 5.32.

T enters this section only on the donor side, as the conversion from Meta's gross counter C to
appended tokens, because C = N·m·T(T+1)/2 is the quantity the paper reports and m is not. A target
harness that reports appended tokens directly needs no T at all. The per-role spread is therefore a
**composition** effect, not a dialog-length effect: roles differ in how many tool-result and user
tokens they pull in per turn relative to what they generate, and applying 2/(T+1) once at the
aggregate conflates that variation with the mean turn count.

So a row transferring 4.2 should check the target harness's **per-turn composition** — roughly how
many tokens of tool results, retrieved files and user content land in the context for each token
the model writes — against RepoProver's mix of truncated file reads, mathlib greps, Lean REPL
replies and `lake build` output. Its dialog length is not the thing to match.

Two caveats for anyone transferring it. Table 2's Sketcher row implies a mean prompt of 1,180
tokens over 5,084 turns, below the ~7,900-token tool array every request carries, so either
sketcher agents ran without tools or that row is mis-tabulated; it is 6M of 83,176M and nothing
turns on it. And the whole construction rests on Appendix A's equal-chunk model, which is the
paper's own heuristic rather than a measurement.

## Open items for the reviewer

1. **The caching call.** Everything about compute rests on it. The documentation quote is
   unambiguous and the code is clean, but `base_url` is configurable and the paper's authors
   evidently believed caching applied. If a reviewer can establish that Meta's internal gateway
   cached, the row becomes 7.09e20.
2. **The size, not the rate.** The rate is now the calibration's 12.6 formal lines per active
   hour over eight projects measured on both ends, which is the tightest number available and
   needs no better anchor. What is left load-bearing is **235 formal lines per textbook page**:
   it comes from four projects with both a line count and a blueprint or textbook page count,
   its dispersion is 216 to 414, and none of the four is a graduate combinatorics textbook. A
   measured line-to-page ratio for a formalized textbook would tighten the row more than
   anything else.
3. **Settled: gross is central.** Coordinator ruling of 2026-09-13. The dataset measures compute
   actually spent, COLUMNS directs that repeated forwards implied by the implementation be
   included, and the absent `cache_control`, Anthropic's documentation, the empty
   `prompt_tokens_details` and the paper's missing cache statistics are that implementation
   evidence. The appended basis of 7.09e20 stays as the scenario, labelled as the counterfactual
   the paper priced at $100K. The residual uncertainty is the configurable `base_url`: an internal
   Meta proxy that inserted cache breakpoints would make the scenario the truth. The transfer
   anchor above is unaffected either way, since it measures the dialog rather than the harness.
4. **The transfer anchor's convexity correction.** The central moved from 5.32 to 4.21 on the
   review, and the rows that consume it should be rechecked against the new figure rather than the
   old one. No specification gap accompanies it: `tokens_accounting` stays `input_output`, which is
   the dataset's established convention for full-prefix rows, and an earlier draft's claim that
   COLUMNS lacks a value for a re-read prefix was wrong, since `decoder_processed` explicitly
   "includes prompt, special, padding or repeated positions".
5. **`native_decide`.** I have established that 141 non-example declarations use it and that no
   axiom audit is published. I have not established how many of the 340 targets transitively
   depend on it, which would need a build. If a reviewer builds the repository, `#print axioms` on
   each target would settle it.
