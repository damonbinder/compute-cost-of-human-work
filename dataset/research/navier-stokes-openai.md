# OpenAI resolving the Navier–Stokes Millennium Prize problem

*Created 2026-09-13 10:22.*
*Last revised 2026-09-16 11:44. The human side is rebuilt on Damon's 2026-09-16 ruling: it is the
solver's own active time conditional on success, and it is now priced by the research-mathematics
calibration in `research/math-human-time/math-human-time.md`, which Damon ruled the standing
method for these rows. The years-open construction of 90,575 hours is withdrawn, and so is the
single-anchor Chen-Hou route that replaced it, which survives below as corroboration.
The compute side is unchanged from the 2026-09-13 revision; see
`candidates/navier-stokes-openai/REVISION.md` and `reviews/navier-stokes-human-time-2026-09-16.md`.*

One point, `reas-navier-stokes-openai`. OpenAI's internal multi-agent system resolved Clay
alternatives (C) and (D) of the Navier–Stokes existence and smoothness problem in 88 hours,
followed by 17 hours of Lean formalization by GPT-6 Astra. Announced 8 September 2026.

## Summary

**x = 5.3611e7 seconds of human active time** (14,892 active hours, 7.4 person-years of 2,000
hours), an estimate with a range of 2.7857e7 to 1.636e8 seconds, that is 7,738 to 45,444 active
hours, or 3.9 to 22.7 person-years.
**y = 5.9834e23 FLOPs**, from 3.5343e11 total counted tokens at 6e11 FLOPs per token, times
1 + 1.822 for the attention term. The component build below still reaches 7.0685e22, which was
this note's figure at the 100B active parameters the model record carried before the
parameter-prior ruling moved it to 300B; the row is the live value and is not changed here.
Label: **`match`**, by construction, because the human side prices reproducing this deliverable
at comparable quality. No human has completed this unit of work.

Units, fixed once for the whole note, following `DECISIONS.md` and the accepted Portal row:
**r is appended tokens per output token, including the agent's own prior output re-entering its
own prefix, and k = 1 + r is total counted tokens per output token.** A re-entered token counts
as fresh input or cache creation, because it is prefilled again unless served from cache, and
its generation counts separately.

Three things carry the entry, in descending order of how much they move it.

1. **The human side is an estimate with no timing sample behind it.** `human_time_evidence`
   is `llm_estimate_judgment` and `human_attempts` is `not_applicable`. The figure is one
   anchor times one multiplier plus a separately reported Lean term, on Damon's 2026-09-16
   ruling that the quantity is the solver's own active time conditional on success. Every
   anchor is an elapsed window from the record with an assumed on-task fraction, and the
   fraction is the weakest factor in all five. The low and high scenarios span 13.2x. This is
   the weakest human baseline the schema permits, and it is the first thing a reviewer should
   attack.
2. **Only output tokens were published, so the input side is assumed.** OpenAI reported
   approximately 130 billion output tokens for Navier–Stokes and nothing about input, cache
   or hardware. The central takes **r = 1.72, k = 2.72**: 0.81 of re-entered own output at the
   inferred 5.4 turns per agent, plus 0.90 of external input built from seeding, peer messages
   and tool results separately. Output-only is the floor at 2.60e22 FLOPs; the settled Meta
   donor anchor transferred without adjustment would give 1.35e23.
3. **The model has no frozen weight identity.** An undisclosed internal model, in training
   since 28 August 2026, swapped mid-run for a further-trained version. Its active parameter
   count is the dataset's 100B frontier prior, not a disclosure, and 30–300B moves the result
   to 2.12e22–2.12e23.

Against those, two terms are one-sided and both understate. Cached-context attention adds
2.6x to 5.8x the parameter-only value at the 247,500-token average context this row's own dialog
geometry implies, and `research/attention-correction.md` now carries it inside
`compute_flops`. If the further-trained model inherits Astra's reported recurrent-depth
decoding, the coefficient scales with an undisclosed pass count.

As a plausibility check on a row where both sides are estimated, 5.9834e23 / 5.3611e7 is
**1.12e16 FLOPs per human second**, a high outlier in the collection. The ratio is worked
through against the percentiles in [The ratio this implies](#the-ratio-this-implies).

The one piece of this row that is measured rather than reported or assumed is the Lean
artifact, which I downloaded and counted myself.

## What was resolved

The Clay problem, in Fefferman's formulation
(`https://www.claymath.org/wp-content/uploads/2022/06/navierstokes.pdf`), asks for one of four
statements. (A) and (B) assert existence and smoothness on R³ and on R³/Z³; (C) and (D) assert
breakdown on the same two domains. OpenAI established (C) and (D).

The inputs were the problem statement and the open literature, reached through a cached snapshot
of the internet, together with code execution. The 166 pages include three appendices: Appendix A
at p. 126, B at p. 144, C at p. 157, references at p. 165. `task_description` in the CSV carries
the short form of all of this.

Paper Theorem 1.1, verbatim from the 166-page PDF:

> For every ν > 0 there exist a force f ∈ C∞c (R³ × (0, ∞); R³), a compact set K ⊂ R³, and
> smooth velocity and pressure fields u, p on R³ × [0, 1) satisfying [the incompressible
> Navier–Stokes system with u(·, 0) = 0] such that supp u(·, t) ∪ supp p(·, t) ⊂ K for every
> 0 ≤ t < 1, sup ‖u(t)‖L²(R³) < ∞, lim sup ‖u(t)‖L∞(R³) = ∞.

The fluid starts from rest, a smooth compactly supported force drives it, kinetic energy stays
bounded throughout, and the velocity becomes unbounded at t = 1. Corollary 10.6 transfers the
construction to the torus, which is (D). The solution is an inward-spiraling, axially
stretching vortex.

The paper carries no human co-author: the author line is "OPENAI", and there is no
acknowledgements section naming a human verifier.

### The work unit is the proof and the formalization together

OpenAI presents one deliverable in two parts: "We're sharing both a writeup of the proof and a
formalization in Lean." The run structure separates them—88 hours of the internal model for
the mathematics, then "an additional 17 hours via GPT-6 Astra" for Lean—so separate rows were
considered and rejected.

The compute evidence does not separate. The published sentence is "In the process of resolving
the Navier–Stokes problem, the agents sent 2.7 million messages and used approximately 130
billion output tokens", and whether that 130 billion includes the formalization is not stated.
A formalization row would therefore have a blank compute value, and the mathematics row would
lose the artifact that is the only concrete check on its claim.

The question turns out not to change the disposition, on either of two estimators, though they
disagree by a factor of 38 and the artifact-shaped one is the more favourable.

- **Artifact-shaped.** The retained Navier–Stokes Lean text is 22,829,692 bytes, about 6.5
  million tokens at 3.5 characters per token. At 100 failed attempts per accepted line,
  formalization output is 6.5e8 tokens, 0.5% of the published 130 billion.
- **Throughput-shaped.** 17 hours against the mathematics run's 88, at a comparable fleet, is
  19% of the run's token-hours, or about 2.5e10 tokens, 19% of the published total.

The second is the one to plan against, and it still does not force two rows: the published
figure cannot be split either way, the deliverable OpenAI presents is the pair, and a
formalization row would carry a blank compute value while the mathematics row lost the only
concrete check on its claim. One row, covering both.

### Verification, and what it does not establish

I downloaded `openai/NavierStokesAndEuler` at head commit `f9e8bc5b` and counted it. Whole
repository: 2,659 `.lean` files, 641,332 lines, 36,825 theorem or lemma declarations at line
start, **zero `axiom` declarations**, and exactly five occurrences of `sorry`, all of them in
`ComparatorChallenges/NavierStokes.lean` and `ComparatorChallenges/Euler.lean`, which the
repository's own README describes as challenge placeholders. The Navier–Stokes subtree alone is
816 files, 429,279 lines and 26,185 declarations. Lean 4.34.0-rc2. Full method and commands in
`agent-work/sources/navier-stokes-openai/lean-repo-measurements.txt`.

The two alternative-(C)/(D) results are `NavierStokes.Comparator.navier_stokes_breakdown_R3`
and `NavierStokes.Comparator.navier_stokes_breakdown_periodic`, both in
`NavierStokes/ComparatorSolution.lean`, which ends with `#print axioms` on each.
`formalization.yaml` declares zero `sorry` and exactly `propext`, `Classical.choice` and
`Quot.sound` for both.

Four limits on that:

- **These are file-level counts, not a kernel check.** I did not run `lake build`, `comparator`,
  `lean4export` or `nanoda`. The Anthropic Fermat's Last Theorem release published all four;
  this one publishes the recipe and no result.
- **No third party has publicly replicated the check** as of 13 September 2026. The repository
  has no issues, open or closed.
- **`formalization.yaml` records `review: status: "self-assessed"`.**
- **Clay has not recognized the result.** Its president Martin Bridson stressed that the
  Institute requires peer-reviewed publication followed by further scrutiny. OpenAI says it
  does not intend to claim the prize.

One real independence check does exist on the statement rather than the proof: the Comparator
challenge statements are adapted from DeepMind's Formal Conjectures formalization of the
Millennium problem, so the theorem being proved is not one OpenAI wrote for itself.

## Compute

### What was published

| Quantity | Value | Scope |
|---|---:|---|
| Output tokens | 130000000000 | Navier–Stokes only |
| Messages | 2700000 | Navier–Stokes only |
| Output tokens | 300000000000 | All attempted problems |
| Messages | 4900000 | All attempted problems |
| Concurrent agents | 10000 | The group that produced the resolution |
| Mathematics run | 88 | Hours |
| Lean formalization | 17 | Hours |

Nothing else. No input tokens, no cache counters, no GPU-hours, no dollar figure from OpenAI
itself. Navier–Stokes took 43% of the all-problems output total.

Output per message is 130e9 / 2.7e6 = **48,148 tokens**. That is far too large for one model
call's visible reply, so a "message" is an inter-agent communication backed by an undisclosed
number of model calls, not a model call. The arithmetic below is built so that this does not
matter: it works on aggregate ratios, not per-call quantities.

### Estimating the input side

`DECISIONS.md` requires the central value to represent total processed tokens with a stated
input-side basis. The donor is the Meta FAIR textbook run, whose anchor is settled in
`research/meta-textbook.md#transfer-anchor` and in `DECISIONS.md` under "Applying the transfer
anchor".

**Units.** r is appended tokens per output token, **including the agent's own prior output
re-entering its own prefix**. k = 1 + r is total counted tokens per output token.
`compute_flops` = k × 130e9 × 2e11.

The convention behind that: under `params_tokens` a re-entered token counts as fresh input or
cache creation, because it is prefilled again unless served from cache, and its generation counts
separately. The accepted Portal row does exactly this, and its decomposition is the precedent —
`tokens` = 5,356,638 = 3,758,297 fresh input plus 1,598,341 output, where the fresh input
includes up to 1,598,341 of re-entered output on top of 197,331 of tool results.

#### Reading the settled anchor

`research/meta-textbook.md#transfer-anchor` owns the donor derivation. Its final figures:

| Quantity | Central | Band |
|---|---:|---:|
| Non-output appended per output token | 3.2 | — |
| r, appended per output token | 4.2 | 3.5 to 5.3 |
| k = 1 + r, total processed per output token | 5.2 | 4.5 to 6.3 |

**r already includes the model's own output re-entering the next prompt**, so total processed is
1 + r rather than r. Re-entered assistant output is a cache-creation position that is processed
again, not a cache read, and COLUMNS excludes only cache reads. The independent review of this
row proposed relabelling the donor's headline as k instead; the donor note and `DECISIONS.md` both
reject that, because it drops the output generation itself. This row follows the convention above,
which is also the one the accepted Portal row exhibits.

The donor central is Appendix A's equal-chunk model applied per role across Table 2's eight roles.
Its band runs from a front-loaded profile at the measured fixed tool prefix up to a single
aggregate application of the same model, and that aggregate, the 5.3 upper bound, overstates,
because 2/(T+1) is convex in T and the agent population is heterogeneous.

One refinement this row carries and the donor's headline does not. The headline charges every
output token one re-entry, but the final turn's output never re-enters, so the exact term is
(T−1)/T. At the donor's T = 54.76 that agrees to within 2%. At the turn counts inferred below it
is 0.81 rather than 1.00, an 18% difference, so this row uses the exact form.
`research/flt-anthropic.md` uses the same convention.

#### What dialog length this run implies

The donor note warns that a transfer must carry T, because 2/(T+1) is a strong function of it.
Here that conversion never runs, because OpenAI published no gross input counter. T matters for
two other reasons: whether the donor's turn shape transfers, and what the re-entry term is.

Output per message is 130e9 / 2.7e6 = 48,148 tokens, against Meta's 341 per turn. If the 10,000
concurrent agents were the whole population, T would be 2.7e6 / 1e4 = 270 turns, and the dialog
would reach 270 × 48,148 = **1.3e7 tokens counting output alone**, before a single input token.
That exceeds any deployed context window by an order of magnitude, so the 10,000 is concurrency
and instances turn over, as the post's wording says.

Bounding dialog length by a context cap bounds T from above, and hence the instance count
A = 2.7e6 / T from below. Dialog length is T × 48,148 × (1 + r_external): the generation pass and
the re-entry pass do not lengthen the dialog, so this check uses the external input only, not k.

| Context cap | External input per output | Max turns per agent | Min instances | Instance lifetime at 10,000 concurrent over 88 h |
|---|---:|---:|---:|---:|
| 200000 | 0.00 | 4.2 | 650000 | 1.4 h |
| 200000 | 0.90 | 2.2 | 1235000 | 0.7 h |
| 200000 | 3.20 | 1.0 | 2730000 | 0.3 h |
| 1000000 | 0.00 | 20.8 | 130000 | 6.8 h |
| 1000000 | 0.90 | 10.9 | 247000 | 3.6 h |
| 1000000 | 3.20 | 4.9 | 546000 | 1.6 h |

**T here is single digits to low tens against the donor's 54.76**, and A is in the hundreds of
thousands. That is self-consistent with 10,000 concurrent agents over 88 hours at instance
lifetimes of one to a few hours.

That moves r three ways.

- **Down, and hard, through the external term's denominator.** The donor's non-output appended
  per output token is 3.2, set by short agents reading large Lean compiler output against small
  patches. This run's output per turn is 141x the donor's 341 tokens, and peer messages, code
  results and literature reads do not scale with reasoning length, so matching 3.2 would need
  about 154,000 tokens of external material appended per turn. Nothing in the harness description
  supplies that.
- **Up, through seeding.** Short dialogs mean many more instances, each seeded once with a system
  prompt, the problem statement and prior-round context. Seeding is charged once per instance and
  is the one external term that grows as T falls. At A = 5e5 and 100,000 seeded tokens it is
  5.0e10 tokens, 0.38 per output token, the largest single external component.
- **Down, through the re-entry term.** (T−1)/T falls from 0.982 at the donor's T to 0.815 at
  T = 5.4.

#### Building r from components

| Component | Central basis | Tokens | Per output token |
|---|---|---:|---:|
| Instance seeding | 500000 instances x 100000 tokens | 5.00e10 | 0.38 |
| Peer messages read | 2.7e6 messages x 5000-token body x fan-out 3 | 4.05e10 | 0.31 |
| Tool results | 2.7e6 turns x 10000 tokens of code output and cached-internet reads | 2.70e10 | 0.21 |
| External input subtotal | | 1.18e11 | 0.90 |
| Re-entered own output | (T−1)/T at T = 5.4 | 1.06e11 | 0.81 |
| **r, appended per output** | | **2.23e11** | **1.72** |

The message body is taken at roughly a tenth of the 48,148 output tokens per message, the rest
being private reasoning that is never transmitted.

Each scenario closes on its own dialog geometry, the check the donor note applies to itself:

| Scenario | Instances | Seed tokens | Fan-out | Tool tokens/turn | External | Turns/agent | Re-entered | r | k | Dialog length | Lifetime |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Low | 260000 | 50000 | 1 | 3000 | 0.27 | 10.4 | 0.90 | 1.17 | 2.17 | 633000 | 3.4 h |
| Central | 500000 | 100000 | 3 | 10000 | 0.90 | 5.4 | 0.81 | 1.72 | 2.72 | 495000 | 1.8 h |
| High | 1300000 | 200000 | 10 | 30000 | 3.66 | 2.1 | 0.52 | 4.18 | 5.18 | 466000 | 0.7 h |

All three land between 466,000 and 633,000 tokens of dialog and between 0.7 and 3.4 hours of
instance life, which is the range a system running 10,000 agents concurrently for 88 hours can
actually sustain. The re-entry term moves against the external term across the scenarios, because
heavier external input forces shorter dialogs, which narrows the spread in k.

#### Scenarios

| Scenario | r | k | Tokens | FLOPs | Basis |
|---|---:|---:|---:|---:|---|
| Floor, generation only | 0.00 | 1.00 | 1.3000e11 | 2.6000e22 | The published quantity alone |
| Server-side KV retention | 0.90 | 1.90 | 2.4750e11 | 4.9500e22 | Own output never re-prefilled; external input only |
| Low | 1.17 | 2.17 | 2.8208e11 | 5.6416e22 | Light seeding, no fan-out, small tool results |
| **Central** | **1.72** | **2.72** | **3.5343e11** | **7.0685e22** | The component build above |
| High | 4.18 | 5.18 | 6.7341e11 | 1.3468e23 | Heavy seeding, fan-out 10, large tool results |
| Donor transferred unchanged | 4.20 | 5.20 | 6.7600e11 | 1.3520e23 | Meta's anchor with no turn-shape adjustment |

The floor sits 2.7x below the central and the unadjusted donor transfer 1.9x above, so the whole
input-side question moves the row by less than a factor of six end to end. The donor transfer and
this row's own high scenario now land within 0.4% of each other, at k = 5.20 and 5.18, by
different routes: the donor gets there from short input-heavy dialogs, this row from heavy
seeding across very many short instances.

The server-side KV retention row is named rather than dropped. It is the outcome if the harness
keeps KV state across turns so the agent's own output is never re-prefilled, which is a plausible
implementation for a first-party internal system and is not covered by any other scenario. It is
the value this row carried at revision 1.

**One knob is held fixed across the three scenarios**: the message body, taken at 5,000 tokens,
roughly a tenth of the 48,148 output tokens per message, on the reading that most output is
private reasoning that is never transmitted. That fraction is not evidenced. It happens not to
matter, because transmitting the **entire** output at the central fan-out of 3 would put the peer
term alone at r = 3.0, which lands near the high scenario: the band therefore already covers the
fully-transmitted-output case.

The cache-read exclusion remains the larger accounting choice, though less dramatic than a
naive reading suggests. A harness with no prompt caching would re-prefill the whole prefix every
turn, giving k = (1 + external)(T+1)/2 + 1: that is 4.8 at T = 3, 7.1 at the inferred T = 5.4,
11.5 at T = 10 and 30.5 at T = 30, or 1.25e23 to 7.93e23 FLOPs. Meta's own run is the case where
this scenario is the central rather than a counterfactual, because RepoProver could not cache;
nothing in the OpenAI post suggests the same, so it is a scenario here. None of these is used.

### Cache accounting form

OpenAI's usage counters partition input into ordinary, cached and cache-write, where
Anthropic's are additive; `DECISIONS.md` records the difference. It does not bite here, because
no counters of either form were published. The estimate is built from scratch on the forwarded-
positions definition, which is the quantity COLUMNS wants regardless of which counter shape a
provider uses.

### Cached-context attention, one-sided upward

Every long-context run carries a quantified scenario for the attention term the
`2 × active_parameters` convention omits and `research/attention-correction.md` folds into
`compute_flops`, using `4 · layers · d_model · N_context` per
appended position, with bracketing architectures. The three shapes are the ones
`research/portal-astra.md` uses, so the two Astra-family rows stay comparable.

Context length is not reported, so it is taken from this row's own dialog geometry rather than
guessed. A position appended to a linearly growing dialog of final length L sees an average
context of L/2, and the closure table above gives L = 466,000 to 633,000:

| Scenario | Dialog length | Average context |
|---|---:|---:|
| High | 466000 | 233000 |
| Central | 495000 | 247500 |
| Low | 633000 | 316500 |

| Shape | 4·L·d | FLOPs per position at N=247,500 | Attention total | Ratio to 7.0685e22 |
|---|---:|---:|---:|---:|
| L=64, d=8192 | 2.10e6 | 5.198e11 | 1.8344e23 | 2.60 |
| L=80, d=10240 | 3.28e6 | 8.118e11 | 2.8663e23 | 4.06 |
| L=96, d=12288 | 4.72e6 | 1.168e12 | 4.1275e23 | 5.84 |

At the central context the omitted term is **2.6x to 5.8x the recorded value**, and across all
nine combinations of shape and context it spans 2.44x to 7.47x. That is well above the 1.4x–3.1x
the Portal row found, because this run's contexts are roughly twice Portal's 130,000. Like
Portal's, the omission can only understate.

**Which context cap the central adopts.** All three scenarios put the dialog between 466,000 and
633,000 tokens, so all three require a working context above the RepoProver-like 200,000 and
inside the 1,000,000 bracket, or else routine compaction. The central adopts the 1,000,000 cap
with no routine compaction. If instead the system compacted, each compaction re-prefills the new
prefix, which would add passes this row does not count: that loose end and the attention
term both point the same way, and both are one-sided.

### Other sensitivities

| Sensitivity | FLOPs | Ratio to central |
|---|---:|---:|
| 30B active parameters | 2.1206e22 | 0.30 |
| 100B active, central | 7.0685e22 | 1.00 |
| 300B active parameters | 2.1206e23 | 3.00 |
| Recurrent depth, two passes | 1.4137e23 | 2.00 |
| Recurrent depth, four passes | 2.8274e23 | 4.00 |

### What is excluded, and why it matters

The 130 billion covers the agents working on Navier–Stokes, including the groups prompted with
the (A) and (B) proof variants that did not succeed, so `compute_subset` is `all`. It excludes
three things that materially contributed:

- **The Euler warm-up.** "Once we saw the Euler solution, we thought that Navier–Stokes was the
  most promising problem to work on"; agents were then "prompted with the Euler resolution".
  That was nearly 100 agents over about 50 hours, and its tokens sit in the 300 billion
  all-problems figure, not the 130 billion.
- **Codex cross-pollination.** Codex consolidated insights across agent groups between rounds,
  and "the group that found the solution to Navier–Stokes was guided in such a way". No Codex
  token count is published at any scope, but the quantity is boundable and the bound is small.
  A consolidation pass reads a digest of each group's intermediate results. Taking one
  agent-dialog-sized digest per group, 5.0e5 tokens on this row's own geometry, at ten groups
  and ten rounds over 88 hours, gives 5.1e7 tokens and **1.0e19 FLOPs at the primary model's
  coefficient**, which COLUMNS permits for a helper. That is 0.014% of the recorded total. A
  deliberately conservative variant at a hundred groups gives 5.0e8 tokens and 1.0e20 FLOPs,
  0.14%. For Codex to reach even 10% of the row it would have to process 3.5e10 tokens, about
  70,000 group-round consolidations at digest scale against a plausible tens to hundreds. The
  round count and digest size are both unpublished, so this is a structural estimate rather
  than a measurement, but it is not close enough to matter.
- **The further training itself.** The internal model was still in training throughout, and
  agents were moved to a further-trained version mid-run. Part of the capability that produced
  the result arrived as training compute, which `compute_scope = inference` excludes by
  definition and no figure covers.

All three push the true total up. They are the reason `comparison_issues` carries
`different_attempt_selection`.

## Model identity

The model is described only as "an internal model that is significantly more capable than
GPT-6 Astra", in training since 28 August 2026, with training still ongoing at publication, and
it changed during the run: "When a further trained version of our internal model became
available over the course of the effort, we updated our agents to that model."

So there is no frozen weight identity for this row. A new record, `openai-ns-2026-09-internal`,
covers the pair as one identity, with the swap stated in its notes. The dataset has precedent
for this shape: `gpt-4-2023-03-01-internal`, `o3-codeforces-checkpoint` and `palm-540b-original`
all carry a blank `model_release_date` and blank `model_release_source` because no public
availability is established. This record does the same.

Its shared numerical assumptions are **identical to the `gpt-6-astra` record** now in this
folder's root `models.csv`: 100B active parameters, `estimated`, 2e11 FLOPs per token,
`two_active_parameters`. That is deliberately conservative in the one direction the evidence
points—OpenAI calls the model significantly more capable than Astra, and a more capable model
is not usually smaller—so the coefficient is a floor on the likely size rather than a central
estimate of it. Raising it would have broken comparability with every other frontier row, which
the dataset's convention exists to preserve.

`gpt-6-astra` itself is included in this study's `models.csv` with byte-identical values,
because it performed the 17-hour formalization half of the work unit. Only
`openai-ns-2026-09-internal` needs copying into the root `models.csv` on acceptance; the Astra
record is already there. `formalization.yaml`
independently confirms the attribution: `automation: methods: agent, models: GPT-6 Astra,
framework: Codex`.

The Astra record's warning carries over. Astra is reported to use recurrent-depth decoding; if
the internal model inherits it, the per-token coefficient scales with an undisclosed pass count.

## Human time

**5.3611e7 seconds—14,892 active hours, 7.4 person-years of 2,000 hours—with 2.7857e7 to
1.636e8 seconds as the range, that is 7,738 to 45,444 active hours, or 3.9 to 22.7
person-years.** `human_time_evidence` is `llm_estimate_from_data`, because both terms rest on
the calibration's tables of recorded timelines rather than on judgment; `human_attempts` is 38,
the calibration's 30 resolved problems in the fit plus its 8 formalization projects;
`human_time_subset` is `successful` and `human_time_statistic` is `point_estimate`.

**The quantity, per Damon's ruling of 2026-09-16** (`DECISIONS.md`, and the worked precedent in
`research/frontiermath-erdos/frontiermath-erdos.md#human-time`). `human_time` is the summed
active time of the people who do solve it, from sitting down with the problem to a written proof
of the same result, conditional on their succeeding. It is not the years the problem stood open,
not the field's cumulative effort since Leray, and it carries no multiple for other people's
failed attempts.

**Two constructions are withdrawn.** Revisions through 2026-09-13 recorded 90,575 hours, built
as five experts over the thirteen years from the Luo–Hou numerics of 2013 to the proof of 2026.
That is a years-open figure wearing a headcount, and Damon ruled it out: "Years open doesn't
make any sense. That's not a logical way to consider the human time." The revision that replaced
it priced the row off a single anchor, Chen and Hou's 6,205 hours times a judgment multiplier of
1.5, and that too is superseded: **a single neighbouring paper's elapsed window is one draw from
a distribution whose dispersion within class is a factor of ten**, and the multiplier was a
judgment with no measurement behind it. The anchors survive below as corroboration, and they
corroborate well — see the agreement to within 1% at the end of this section.

**The method, per Damon's ruling of 2026-09-16.** This row is priced by the research-mathematics
calibration in `research/math-human-time/math-human-time.md`, the standing method for
research-mathematics rows. Two tables carry it: thirty-five resolved research problems giving
hours per written page by size class, and twelve formalization projects giving formal lines per
active hour. The mathematics term is the page count at the large class's rate, and the
formalization term is the human-idiom line count at the measured rate.

**The anchors below are kept as corroboration.** Four of the five are rows of the calibration's
own Table 1 — Alpöge and Buckmaster, Wang and Zahl on Kakeya, Deng–Hani–Ma on Boltzmann, and
Chen and Hou on Euler — so they now enter the large-class rate rather than setting the figure
directly. Each anchor is `people × elapsed calendar days × 8 hours per working day × the
fraction of that time actually on this problem`. The 8-hour working day is `DECISIONS.md`'s
2,000-hour person-year over 250 working days. Elapsed days are calendar days, so the fraction
absorbs weekends and the teaching, refereeing and other projects these people carried.

<a id="anchors"></a>

### The anchors

Five logged human resolutions of long-open problems in PDE and analysis, chosen for scope
comparable to a 166-page quantitative analytic proof rather than for fame.

| Key | Arithmetic | Summed active hours, band | What it measures |
|---|---|---:|---|
| **A1** | 2 × 330 d × 8 h/d × 0.35 | **1848**, 1320 to 2640 | Alpöge and Buckmaster to smooth-forcing blowup for Euler, IPM and Boussinesq — the immediately adjacent result, by the people who got it |
| **A2** | 2 × 860 d × 8 h/d × 0.30 | **4128**, 2752 to 6192 | Wang and Zahl from the sticky-Kakeya paper to the 127-page three-dimensional Kakeya set conjecture |
| **A3** | 3 × 273 d × 8 h/d × 0.55 | **3604**, 2948 to 4586 | Deng, Hani and Ma to the 192-page long-time derivation of the Boltzmann equation, the analytic core of Hilbert's sixth |
| **A4** | 2 × 1108 d × 8 h/d × 0.35 | **6205**, 4432 to 8864 | Chen and Hou from the C^{1,α} blowup theorem to the 159-page smooth-data Boussinesq and 3D Euler blowup proof |
| **A5** | 1 × 2557 d × 8 h/d × 0.60 + 2 × 400 d × 8 h/d × 0.45 | **15154**, 11125 to 19822 | Wiles to Fermat's Last Theorem, then the Taylor–Wiles year that closed the gap |

Where each factor comes from, and which are assumptions.

- **A1.** People: two. Days: **pointed, not assumed** — Alpöge's email to Buckmaster of
  19 September 2025 opened the collaboration and the results were obtained on 15 August 2026,
  330 days, with Lean verification about a week later
  (`https://en.wikipedia.org/wiki/Navier%E2%80%93Stokes_priority_controversy`). Fraction: **my
  assumption.** They worked it "in secrecy" alongside an NYU professorship and an industry job,
  which is a part-time shape; 0.35 is 2.8 hours a day each, every calendar day for eleven months.
  **This anchor is heavily AI-assisted** — they used large language models from both Anthropic
  and OpenAI, and Tao's post of 7 September 2026 says "the arguments here are heavily
  AI-assisted" — so as a measure of unassisted human time it is biased low, and it is used as
  the low corner rather than the central for that reason.
- **A2.** People: two authors. Days: `arXiv:2210.09581` v1 on 18 October 2022, the trilogy's
  first paper, to `arXiv:2502.17655` v1 on 24 February 2025, 127 pages, 860 days. Fraction:
  **my assumption.** Both are full-time faculty (UBC and NYU/IAS) carrying teaching and other
  programmes; 0.30 is 2.4 hours a day each. Tao's own account is that he watched their gradual
  progress over about five years, so the 860-day window is the tighter reading and the fraction
  is not pushed down to cover the longer one.
- **A3.** People: three authors. Days: the November 2023 Deng–Hani preprint announcing the
  forthcoming extension of Lanford's theorem, to `arXiv:2408.07818` v1 on 14 August 2024,
  192 pages, 273 days. Fraction: **my assumption, and the highest in the set**, because the
  record says so: Hani describes constant video calls, "some of them happened very late at
  night, or very early in the morning", over a process that "takes months"
  (Quanta, 11 June 2025). 0.55 is 4.4 hours a day each including weekends. The window's start is
  an announcement rather than a start of work, so this anchor is the most likely of the five to
  be short.
- **A4.** People: two authors. Days: `arXiv:1910.00173` v1 on 1 October 2019, the C^{1,α}
  theorem that set up the smooth-data problem, to `arXiv:2210.07191` v1 on 13 October 2022,
  159 pages plus a 25-page supplement, 1,108 days. Fraction: **my assumption.** Chen was a
  doctoral student and then postdoc for whom this was the main programme, which argues well
  above 0.35; Hou is a senior professor, which argues below; both published other papers inside
  the window. 0.35 is the average of those, 2.8 hours a day each.
- **A5.** People: one, then two. Days: Ribet's 1986 link to Taniyama–Shimura to the Cambridge
  lectures of 23 June 1993, seven years, then about 400 days from the referee's gap to the
  October 1994 Taylor–Wiles fix. Fraction: **my assumption, and the highest defensible one in
  the record for a single person.** Wiles abandoned all research not bearing on the theorem, cut
  conferences and colloquia, and reduced lecturing and tutoring to a minimum; 0.60 is 4.8 hours
  a day, every calendar day, for seven years. This is the upper anchor precisely because nothing
  else in the record documents that level of sustained exclusivity.

**The whole anchor set lies between 1,848 and 15,154 summed active hours**, and only Wiles is
five figures. The four non-Wiles anchors, all of them team proofs of 127 to 192 pages produced
inside three years, span 1,848 to 6,205. Nothing in the record supports a five-figure
mathematics term short of the Wiles shape, which is why the 65,000-hour discovery figure of the
previous revision was an order of magnitude out.

### What is not in the anchor set

No paper here states its own duration in an acknowledgement, so every anchor is an elapsed
window with an assumed on-task fraction, and the fraction is the weakest factor in all five.
Halving every fraction halves every anchor and roughly halves the mathematics term. Perelman
was considered and dropped: the 1995-to-2002 window is real but he published nothing about his
allocation, he was at Steklov without teaching for part of it, and three preprints totalling
68 pages are a different deliverable shape from a 166-page worked analytic proof.
Buckmaster–Vicol's Navier–Stokes nonuniqueness (`arXiv:1709.10033`, 36 pages) was dropped on
size: at a fifth of the page count it would set the scale by a paper that is not of this kind.

### Sizing this row

Steps 2, 3 and 5 of the method. The deliverable's written mathematics is on the record and does
not have to be inferred: **166 pages** of analytic proof of Clay alternatives (C) and (D). That
is the large size class, above the method's sixty-page break, and the class rate is the median
hours per page over the eight large results in Table 1 of the calibration.

    166 pages x 56.6 h/page  =  9,396 h of mathematics

**The class rate is read off eight large results across four fields**, spanning 18.8 to 196.5
hours per page: Kakeya at 32.5, Boltzmann at 18.8, Chen–Hou at 33.7, Wiles at 117.4, Zhang at
75.6, the sofa problem at 37.6, Kepler at 99.4 and diagonal Ramsey at 196.5. The 56.6 is their
median. Nothing about this row's own neighbourhood picks a corner of that range, so the median
is what applies.

**The old single-anchor route agrees to within 1%, and that is the strongest corroboration this
row has.** Chen and Hou's 6,205 hours times 1.5 gave 9,308 against the method's 9,396. The two
are not built from the same thing: one is a single neighbouring PDE paper's elapsed window with
a judgment multiplier on top, the other the median hours-per-page of eight large results across
four fields with no multiplier at all. They were not tuned to each other, and the agreement is
not an artifact of Chen–Hou sitting inside Table 1, because one row of eight moves the median
hardly at all.

**The central sits well below its elapsed bound.** Chen and Hou's window at an on-task fraction
of one is 2 × 1108 × 8 = 17,728 hours, and the whole of Table 1's large class has the same
property: no central in it sits at its bound.

<a id="lean-component"></a>

### The Lean component

`hours = human-idiom Lean lines ÷ 12.6 formal lines per active hour`, the calibration's Table 2
median over eight completed projects, each with a measured line count and a measured author-day
record. The 12.6 supersedes both rates this note previously weighed — Li's 31.7, whose numerator
was an unpublished line count inferred from a page count, and the Imperial project's 5.88, whose
denominator was a funded head-count rather than an observed work record. Neither was measured on
both ends; all eight of the calibration's projects are.

**The line count is taken per page of source mathematics, not from the machine artifact**, which
is unchanged in principle from the previous revision and changed in its ratio. No blueprint
exists for this proof, so the research-paper ratio applies rather than the blueprint one:

    166 pages x 417 lines/page  =  69,255 human-idiom lines
    69,255 / 12.6               =   5,496 h of formalization

The previous revision reached 4,517 hours from 166 × 160 lines per page over the Imperial 5.88.
The rise to 5,496 is 22%, and both of its factors moved: the page ratio rises from Odd Order's
160 to the calibration's measured 417, and the rate rises from 5.88 to 12.6. They move in
opposite directions and mostly cancel, which is why a 2.6× change in one factor and a 2.1×
change in the other land a fifth apart.

**The delivered machine artifact bounds this from above and nothing more.** The Navier–Stokes
Lean subtree is 429,279 measured lines
(`agent-work/sources/navier-stokes-openai/lean-repo-measurements.txt`), which is 2,586 lines per
page against the calibration's 417. A human would write far fewer than that for 166 pages, so
the machine count is not a size estimate for the human job and is not used as one.

### The numbers

| Term | Basis | Low | **Central** | High |
|---|---|---:|---:|---:|
| Mathematics | 166 pages x the large class's h/page | 3121 | **9396** | 32619 |
| Formalization | 69,255 human-idiom lines / lines per active hour | 4617 | **5496** | 12825 |
| **Total hours** | | **7738** | **14892** | **45444** |
| Seconds | | 27856800 | 53611200 | 163598400 |
| Person-years of 2,000 h | | 3.9 | 7.4 | 22.7 |

**The bounds are the calibration's own dispersion and nothing else.** No default factor is
applied. The mathematics term takes the large class's minimum and maximum hours per page,
**18.8 and 196.5**, on the same 166 pages; the formalization term takes the rate's band,
**15.0 formal lines per active hour at the low end and 5.4 at the high**. The page ratio is
held at 417 at both ends, because moving it would move the line count and would compound one
discretionary step with another.

The span is 5.9×, narrower than the previous revision's 13.2× and for a good reason: the old
span compounded an anchor choice, a fraction and a multiplier, all three of them judgments,
where this one is the observed spread of two measured rates. It is not a claim that the row is
better determined than it was. The dispersion within the large class is a factor of ten on
hours per page and cannot be argued away, and the calibration says so in its own words.

**The change from the previous revision is 8% up**, 13,825 hours to 14,892, which is inside any
reasonable band. That is the shape the calibration should have on a row whose case-by-case work
was already careful.

### The ratio this implies

At the row's 5.9834e23 FLOPs, 5.3611e7 seconds of human time is **1.12e16 FLOPs per human
second**. Against the collection that is above the 95th percentile of 2.57e14 and above the 99th
of 9.2e15, and it ranks 1,667th of 1,683 rows. The row is a high outlier, and that is the
ruling's doing rather than a defect: pricing one successful team's own active time, rather than
a field-length programme, is what moves these rows up.

### Comparison with the Fermat's Last Theorem row in this batch

`research/flt-anthropic.md` prices a neighbouring unit at 27,758 active hours, and this row is
**1.9x below** it. The two are now on the same quantity: Damon's ruling brought FLT onto the
calibration in the same pass that brought this row, and the question this section used to leave
open is settled.

**FLT fell by a factor of three, and the reason has nothing to do with the rates.** Its old
84,000 hours costed the Imperial College FLT project by its funding — 4 to 6 all-in
person-years scaled to a five-year plan, times a remainder multiplier. The calibration costs
the same project by its commit record instead: 727 distinct non-bot author-days, which is 4,362
active hours, against the 6,101 to 8,200 the fellowship's money buys over the same window. The
grant overstates the work by 1.4 to 1.9×, and pricing the observed record rather than the
funded head-count is what moved the row. The remainder multiplier of 2.5 survives unchanged.

What separates the two rows now is the deliverable, not the construction. This row prices one
team's own active time on a 166-page analytic proof plus its formalization; FLT prices the
whole reduction to the 1980s plus everything the Anthropic artifact additionally proves, on a
work record that is an ongoing multi-contributor project rather than one solve.

### Human skill

`world_class`. Resolving a Millennium Prize problem is by definition performance at the highest
professional level, and the population that could produce this analytic proof is a handful of
people. The formalization component is priced at experienced-Lean-formalizer rates inside a
world-class-led effort, which is how such projects are actually staffed; the binding constraint
on the work unit is the analytic half.

## Performance and comparison

`performance_vs_human = match`. COLUMNS is explicit: "When human time explicitly estimates
reproducing the AI output at comparable quality, use match by construction." The human estimate
above prices exactly this deliverable—the analytic proof of (C) and (D) plus its Lean
formalization—so `match` follows from the construction rather than from a comparison of two
observed results.

`match` is also the more conservative of the available labels. `above` would assert that the
AI beat a human baseline that does not exist, and would stake the row on a verification question
nobody outside OpenAI has settled. `unknown` would throw away a matched-quality estimate the
schema explicitly provides for. The scouting pass leaned toward `above` or `unknown`; COLUMNS'
matched-quality rule fits the evidence better than either.

On admissibility, the nearest dataset precedent is the pair `reas-imo-alphaproof` and
`reas-imo-deepthink`, both dispositioned `unresolved_compute` in the project's coverage file
because configuration-specific compute for those systems was never reported. This row clears
that bar for one reason: OpenAI published a token count scoped to this work unit. The
active-parameter coefficient is assumed here just as it was there, but the workload is not.

`comparison_issues = different_inputs_or_tools; different_assessment; different_attempt_selection`.

- **`different_inputs_or_tools`.** The system had, and the unassisted human baseline does not, a
  cached snapshot of the internet, code execution, its own Euler resolution supplied as a seed
  prompt ("we shifted agents away from the other Millennium Problems and prompted these agents
  with the Euler resolution"), and Codex-consolidated insights from other agent groups. That is a
  concrete difference in supplied information and permitted tools, and it is distinct from the
  scope-of-counted-work point below.
- **`different_assessment`.** The AI result is assessed by a Lean kernel check the repository
  reports on itself, with `review: status: "self-assessed"` and no published third-party
  replication. A human proof of this class would be assessed by referees over years, which is
  what Clay requires before a prize and what has not happened.
- **`different_attempt_selection`.** The 130 billion tokens are scoped to Navier–Stokes, but
  the resolution depended on work outside that scope: the Euler warm-up that seeded the agents,
  the Codex cross-pollination that guided the winning group, and the further training delivered
  mid-run. The human estimate includes the failed and preparatory work its scenarios describe;
  the AI figure excludes the analogous work by construction.

Not flagged: `different_task` (both sides are priced on the same two deliverables) and
`different_human_baseline` (there is one population and it is the one being estimated). An
estimated human baseline is not by itself a flag, per COLUMNS.

**A specification gap to raise at merge.** COLUMNS defines `different_attempt_selection` as "AI
compute and human time select different outcome subsets, such as all versus successful attempts".
What this row flags with it is work excluded from the counted total within a single attempt, not
a subset of attempts. It is the closest available value and is kept, but it is a gap of the same
kind `DECISIONS.md` already logs for variable-length episodes, and it should be raised rather
than left looking like a clean fit.

## reas-navier-stokes-openai

Resolving Clay alternatives (C) and (D) of the Navier–Stokes existence and smoothness problem:
a 166-page analytic proof of finite-time blowup from rest under smooth compactly supported
forcing with bounded kinetic energy, on R³ and on R³/Z³, together with its Lean 4 formalization.
One continuous goal run of 88 hours by a coordinating multi-agent system on an undisclosed
OpenAI internal model, then 17 hours of Lean formalization by GPT-6 Astra.

- `compute_flops` = **5.983359555555555e23**, from 353425925925.9259 tokens at the model's own
  coefficient, i.e. the published 1.30e11 output tokens times k = 2.7187.
- `tokens_accounting` = `input_cache_creation_output`; cache reads excluded per COLUMNS.
- `human_time` = **53611200** seconds, from 14,892 active hours, 7.4 person-years of 2,000
  hours; `human_time_low` = 27856800, `human_time_high` = 163598400.
- `human_time_evidence` = `llm_estimate_from_data`, `human_time_subset` = `successful`,
  `human_attempts` = 38.
- `ai_attempts` = 1. A continuous goal run is one attempt regardless of intermediate agents,
  retries and the model swap.
- `compute_statistic` = `total`, `compute_subset` = `all`, `compute_evidence` =
  `derived_assumed_inputs`, `compute_method` = `params_tokens`.
- `performance_vs_human` = `match`; `comparison_issues` =
  `different_inputs_or_tools; different_assessment; different_attempt_selection`.

## Reproducing

```
cd "AI Compute vs Human Time claude-rows"
python3 research/navier-stokes-openai/compute.py \
    --sources agent-work/sources/navier-stokes-openai \
    --output /path/to/new-calculations.json
```

Python 3.8 or later, standard library only. The script takes explicit paths, never writes into
`agent-work/sources/`, and does not modify the retained `agent-work/derived/navier-stokes-openai/calculations.json`.
Every number in this note comes out of it.

To re-measure the Lean artifact, the commands are listed verbatim in
`agent-work/sources/navier-stokes-openai/lean-repo-measurements.txt`, along with the tarball SHA-256. Note
that the repository's `main` branch can move; the measurements are pinned to commit `f9e8bc5b`.

## Not used

- **Cost as a compute cross-check.** New Scientist's "$15m of AI effort", the New York Times'
  electricity figure and Noam Brown's confirmation that the result "cost millions of dollars"
  are all consistent with 130 billion output tokens at Astra-class prices, but none is an
  OpenAI accounting statement, and the token count is better evidence than a cost derived from
  it. `DECISIONS.md` permits cost-only rows; this row does not need one.
- **The Euler result.** Nearly 100 agents over about 50 hours resolved unforced Euler
  regularity, in the same repository and the same announcement. Its tokens are not separable
  from the 300 billion all-problems aggregate, so no row is proposed. Its compute is also
  excluded from this row, which is one reason for `different_attempt_selection`.
- **The priority dispute.** Buckmaster's accusation that OpenAI used customer data, OpenAI's
  denial, and the surrounding coverage bear on credit and conduct, not on the compute or the
  human time. The Buckmaster–Alpöge timeline is used only as a human-effort anchor.
  `agent-work/sources/navier-stokes-openai/expert-commentary-and-verification.md` retains the detail.
