# ARC-AGI-3: GPT-6 Astra on the 55-environment semi-private set

*Created 2026-09-13 17:39.*
*Last revised 2026-09-13 18:26, on the independent review and the coordinator's
rulings. Change log in `candidates/arc-agi-3/REVISION.md`.*

## TL;DR

Nine rows, all GPT-6 Astra on the ARC-AGI-3 Semi-Private set, one work unit each:
**one previously unseen interactive environment played from the first frame to the last
level, on first exposure, with no instructions.** A human does that in **486 seconds**
(median successful attempt in ARC's own 2,893-attempt timed study). Astra under ARC's
Provider Adapter harness scores 96.7% to 99.95% on RHAE, a metric normalised so that 100%
*is* the median human who solved the level, for **9.7e18 to 1.23e19 FLOPs per
environment**; those six rows are labelled `above`, because the metric is censored at
parity and the uncensored action counts put the agent at 37.8% to 47.8% of the human
baseline. Under ARC's Standard harness it scores 54.8% to 62.7% for **2.3e19 to 3.6e19
FLOPs**, labelled `below`. Thirty leaderboard entries fall below half the human baseline
and are recorded in `candidates/arc-agi-3/dispositions.csv` rather than built.

The compute is inverted from ARC's published per-run dollar figures, as Damon directed,
but the inversion is much better anchored than the scouting note expected. Two things
turned up that the scouting pass did not have:

1. **ARC's own cost model is in its source code, in both benchmarking repositories:**
   `cost = gross_input_tokens x input_price + output_tokens x output_price`, with the
   gross input counter priced at the full input rate. Neither repository contains a
   cached-input rate anywhere. So the dollar figure is a linear function of two token
   counts, not four.
2. **Per-call provider usage counters are published** for the companion ARC-AGI-3 Public
   Demo runs—same model, same harness, same reasoning effort, same harness code, only
   the environments differ—through the replay recordings the results page links. The
   two ratios the inversion needs (output per gross input token, and the cached share of
   gross input) are therefore **measured on 300 runs and 143,016 model calls**, not
   assumed.

The residual uncertainty is stated per row: if ARC did price cache reads at the cached
rate after all, every figure rises by 1.17x (Standard) or 1.79x (Provider Adapter); the
ruled 100-600B active-parameter range moves them 0.33-2.0x; and cached-context attention,
omitted by the dataset's convention, would add roughly another 0.55-1.44x on top.

## Shared evidence

Retained sources are in `agent-work/sources/arc-agi-3/`, listed with their URLs and retrieval
times in `agent-work/sources/arc-agi-3/MANIFEST.md`. Scripts are in `research/arc-agi-3/`;
[Reproduction](#reproduction) gives the commands.

### The benchmark and the work unit

ARC-AGI-3 is a set of interactive, turn-based environments. Each is a 64x64 grid of 16
colours; the agent sees a frame or a short animation, picks one action from a small action
set (five key actions, undo, and a click at (x, y) on the grid), and the environment
advances. An environment is a sequence of at least six levels; it is **solved only if the
test taker completes every level, on first exposure, with no instructions about the goal
or the mechanics** (technical report, sections 2.3 and 5).

Three datasets (report, Table 1): Public Demo 25 environments, Semi-Private 55,
Fully Private 55. The leaderboard entries priced here are all on the **Semi-Private 55**.
The report states plainly that the private environments "are significantly more difficult
for both humans and AI" than the public ones, and that ARC will never report public-set
scores on the official leaderboard.

The row's work unit is **one environment**, matching the human study's unit (one attempt
at one environment) and the benchmark's own reporting unit (the total score is the mean of
the 55 environment scores).

### Scoring: RHAE, normalised so 100% is the median human

RHAE (Relative Human Action Efficiency) scores a level by the agent's action count against
a human baseline, squared:

```
S(l,e) = min(1.15, (h(l,e) / a(l,e))^2)
E(e)   = min( sum_{l<=k} w_l / sum_l w_l ,  sum_l w_l S(l,e) / sum_l w_l ),  w_l = l
T      = mean over environments of E(e)
```

`h(l,e)` is **the upper-median action count among the human testers who completed that
level**—ARC moved the baseline from the 2nd-best human to the median human, and raised
the per-level cap from 100% to 115%, in the April 2026 scoring update, and the report and
both 2026 blog posts all describe the current rule the same way. The first term of `E(e)`
caps an environment at the level-weighted fraction of levels completed, so an agent cannot
buy a high score by being efficient on the easy levels and failing the hard ones.

Two consequences matter for these rows. **100% is human parity by construction**, so the
performance comparison needs no external anchor: the leaderboard score *is* the ratio to
the human baseline. And **the metric cannot express superhuman efficiency beyond 1.15 per
level**, which is why a configuration that used 62% fewer actions than the human baseline
still reports 98.55%.

The chance floor is essentially zero: an environment was only accepted if "a random policy
should not successfully solve a level more often than 1 in 10,000 times" (report, 3.5.2),
and the squared efficiency term drives a lucky solve's credit lower still. The exclusion
guide's half-of-human line therefore sits at RHAE 0.5.

Agents are stopped at **five times the human baseline median action count per level**
(report, 4.3), which the harness implements as `MAX_ACTIONS_BASELINE_MULTIPLIER: 5.0`.

### The human study

From the technical report, sections 5.1 and 5.3, and the April 2026 human-dataset post:

| Quantity | Value |
|---|---|
| Participants | 486 |
| Candidate environments tested | 414 |
| Recorded attempts | 2893 |
| Total recorded play time, hours | 427.9 |
| Median attempt duration, seconds | 444 |
| Median successful attempt, seconds | 486 |
| Median unsuccessful attempt, seconds | 354 |
| Testers per environment | 10 |
| Soft time limit, seconds | 1200 |
| Hard cutoff, seconds | 1800 |
| Session length, seconds | 5400 |
| Environments per session | 9 |
| Participation fee, USD, low | 115 |
| Participation fee, USD, high | 140 |
| Solve bonus per environment, USD | 5 |

Testing ran three days a week, in person, in a San Francisco centre, with participants
drawn from the general public and not selected for puzzle skill. Every participant saw an
environment once, took a single attempt, and could reset the current level but not revisit
a completed one. ARC states the humans and the models got the same system prompt and the
same information, and that the participants were not told this was an AI test.

**Solvability.** Every environment in the benchmark was beaten by at least two of about
ten independent first-exposure testers and many by six or more, which is the acceptance bar;
ARC's claim is that ARC-AGI-3 is 100% solvable by humans with no task-specific training.
An individual attempt fails often: on the released public-demo set, 144 of 339 sessions
(42.5%) solved the environment.

**The released replay dataset.** ARC open-sourced the public-demo half of the study—340
step-by-step human replays on the 25 public environments, mirrored on Hugging Face at
`magic-sword/arc_agi_3_public_demo_human_testing`. `research/arc-agi-3/human_durations.py`
takes each session's first and last event timestamp; 339 of 340 sessions carry at least two
timestamps. Measured there:

| Statistic | All attempts | Successful | Unsuccessful |
|---|---|---|---|
| n | 339 | 144 | 195 |
| Mean, seconds | 626 | 706 | 567 |
| Median, seconds | 529 | 655 | 380 |

These are longer than the study-wide medians (444 / 486 / 354), which is the opposite of
what "the public set is easier" suggests and is worth stating: the public environments run
to 6-10 levels and were designed to be engaging, while a failed attempt on a hard private
environment ends early. The whole-study statistic is the one used, because it is the only
one whose environment pool contains the 55 environments these rows score.

### The two harnesses

Both are ARC's own, in `github.com/arcprize/arc-agi-3-benchmarking`, and both share the
action budget, the environments and the scoring. Neither gives the model tools.

- **Standard** (`state: manual_rolling`). A provider-neutral text conversation. The frame
  is rendered as text—`State`, `Levels completed`, then up to seven animation frames
  each printed as 64 rows of 64 integers, then the available actions. There are no images
  anywhere in this harness. The system prompt is: "You are playing a game. Your goal is to
  win. Include any context you want to carry forward in your reply, along with the action
  you want to take. The final action mentioned in your reply will be executed next turn."
  The conversation grows and is trimmed from the front, oldest user/assistant pair first,
  whenever its estimated size exceeds `MAX_CONTEXT_LENGTH: 175_000`—estimated at one
  character per token.
- **Provider Adapter** (`state: continuous_conversation`). The OpenAI Responses API with
  `previous_response_id`, `store: false`, `include: ["reasoning.encrypted_content"]` and
  server-side `compaction` at a 175,000-token threshold, so the model's opaque reasoning
  state survives between turns and the transcript is compacted rather than truncated. Its
  system prompt drops the carry-forward instruction.

One rendered frame block is 12,608 characters, and the first call of a run—system
prompt, one frame and the action list—measures 12,424 to 12,468 tokens across a sample of
runs, the Provider Adapter consistently a little lower than the Standard harness because
its system prompt drops the carry-forward instruction. The harness's
one-character-per-token estimate is therefore accurate to a few percent, and the context
grows by about 12,450 tokens a turn. It reaches its cap, around 161,900 tokens, within
thirteen turns and stays there.

### What is published, and what is not

Published: the leaderboard payload (`arcprize.org/media/data/leaderboard/v3.json`, 39
entries, each with a score and a total dollar cost, generated 2026-09-04); the per-model
results page, which prints the six-by-two grid of **public-demo** per-environment scores
and links a replay for every cell; the ARC blog post of 3 September 2026; the technical
report; the harness source; and the human-study dataset for the public environments.

Not published: any token count for the semi-private runs, and any per-environment
semi-private score. ARC's own results repositories on Hugging Face cover ARC-AGI-1 and 2
only. The scorecard API (`/api/scorecard/<id>`) requires a key.

**But the public-demo runs carry their counters.** The results page links a replay session
GUID for each of its 300 cells. `/api/sessions/<guid>` returns the run's config id, score,
action count, per-level scores, per-level actions and per-level human baseline actions;
`/api/recordings/<game_id>/<guid>` streams the run as NDJSON, one line per environment
step, and each agent line carries `action_input.reasoning`, the provider response envelope
the harness attached, including the raw `usage` block: `input_tokens`,
`input_tokens_details.cached_tokens`, `output_tokens`,
`output_tokens_details.reasoning_tokens`. The harness truncates the `output` and
`reasoning` text of that payload to fit ARC's 16,000-byte metadata limit but never touches
the usage block (`benchmarking/action_metadata.py`). All 300 runs were pulled this way;
the aggregate is in `agent-work/sources/arc-agi-3/astra-public-demo-usage-2026-09-13.csv`, and
the recordings themselves, 3-60 MB each, were streamed and discarded rather than retained.

Measured across all 300 public-demo runs: 143,931 actions, 143,016 recorded model calls,
19.94 billion gross input tokens, 5.12 billion cached, 57.8 million output, of which
50.7 million are reasoning tokens.

## Human baseline

**Value used: 486 seconds**—8.1 minutes, the median duration of a successful attempt in
the technical report, section 5.3.1, converted to seconds.

- `human_skill` is `typical`: members of the general public, recruited without selection
  for puzzle-solving experience or ability, across a range of education, income, job
  sector and age.
- `human_time_scope` is `task_performance`; `human_time_evidence` is `task_timings`, the
  source's own aggregate of recorded timings for this task at this skill level.
- `human_time_method` is `other_calculation`: a median over recorded timings is arithmetic
  on observations, not a judgment-based estimate, following this folder's ruling that
  source-published statistics are not `reported`.
- `human_time_statistic` is `median` and `human_time_subset` is `successful`. The median
  is what ARC publishes; it does not publish a mean for the successful subset, and the
  arithmetic mean over *all* attempts is available (below) but describes a different
  population.
- `human_attempts` is **blank**: a contributing sample plainly exists, but ARC publishes
  the 2,893 attempt total without splitting it into successes and failures, and the solve
  rate is not stated study-wide. The released public-demo subset solved 144 of 339, but
  transferring that rate to the whole study would be an invention, not a count.

**Why the successful subset.** RHAE's denominator is the median human *who completed the
level*. The AI's score is therefore measured against a human who did the job, and the
matching duration is the duration of a human who did the job. Pairing a completer-based
score with an all-attempts duration would compare two different people. The consequence is
recorded as `different_attempt_selection`, since the AI compute averages over all 55
environments, solved or not.

### Alternative human statistics

Scenarios, not hedges in the CSV.

| Population and statistic | Seconds | Basis |
|---|---|---|
| Median successful attempt, whole study (the value used) | 486 | Report 5.3.1, n unpublished |
| Median attempt, whole study | 444 | Report 5.3.1 |
| Median unsuccessful attempt, whole study | 354 | Report 5.3.1 |
| Mean attempt, whole study | 532 | 427.9 h / 2,893 attempts |
| Mean successful attempt, public demo | 706 | Released replays, n=144 |
| Median successful attempt, public demo | 655 | Released replays, n=144 |
| Mean attempt, public demo | 626 | Released replays, n=339 |

The spread across these is 1.0x to 1.45x, and the direction of the public-demo figures is
upward, so 486 seconds is the low end of the defensible range. Nothing in the evidence
supports a semi-private-only duration: ARC did not publish the timing split by dataset,
and the released replays cover the public set only.

**Actions, as a second axis.** The human baseline action counts *are* published per
environment for the public set, through the session API. Across the 25 public
environments the human baseline totals a mean of 685 actions per environment (median 638,
range 171 to 1,843) over 6 to 10 levels. Astra under the Provider Adapter at max effort
used 6,485 actions against those environments' 17,135 baseline actions, 37.8% of the human
count; ARC's blog states the same result as an unweighted per-level mean, "51.7% fewer
actions per level", and "fewer actions than the human baseline on 96.0% of levels".

### Human cost

ARC publishes the per-game figure directly: participants "were paid $115 per 90-minute
session, plus $5 per game completed. Participants attempted approximately nine games per
session, roughly **$12.78 per attempted game before bonuses**." That is the value in
`human_cost_usd`, on the `reported_payment` basis. Two qualifications, both in the note
rather than the CSV: the figure is per *attempted* game while `human_time` is a successful
attempt, so a solved game actually cost ARC $17.78; and the report gives the participation
fee as a $115-$140 range while the blog quotes $115.

## Compute

Arithmetic is reproduced by `research/arc-agi-3/compute_arc3.py`; its output is retained
at `agent-work/derived/arc-agi-3/calculations.json`, with a flat summary in
`agent-work/derived/arc-agi-3/inversion-summary.csv`.

### ARC's cost model, established from its own code

The published figure is a total dollar cost per run and nothing else, so the conversion
has to be justified. It is, unusually, justified by ARC's own source:

The excerpts below are retained verbatim, with both commit hashes, in
`agent-work/sources/arc-agi-3/arcprize-benchmarking-cost-model-2026-09-13.md`.

`arc-agi-3-benchmarking/benchmarking/runtime_models.py`, in
`action_metadata_from_model_response`:

```python
input_cost = calculate_cost(model_response.usage.input_tokens, pricing.get("input", 0.0))
output_cost = calculate_cost(model_response.usage.output_tokens, pricing.get("output", 0.0))
```

`usage.input_tokens` is the provider's **gross** input counter, which on the OpenAI APIs
includes the cached tokens; `pricing` is a two-key block, `input` and `output`, and the
config file carries provider list prices in it. The inclusion is visible in the counters
themselves: the second call of every run reports a cached count equal to the first call's
whole input, the third the second's, and so on up the growth phase. The older ARC-AGI-1 and 2 harness computes
the same way (`arc-agi-benchmarking/src/arc_agi_benchmarking/utils/update_pricing.py`:
`prompt_cost = prompt_tokens * input_cost_per_token`, with reasoning tokens priced at the
output rate). **Neither repository contains a cached-input price anywhere**, and the Claude
adapter's own comment—"Log SDK cost for comparison (they may use different cache
pricing)"—says as much. ARC's testing policy says only that it uses "retail pricing …
typically measured in price per million tokens".

**No retained artifact shows ARC pricing an Astra run directly.** Every `cost` block in
the 300 recordings reads `input_cost: 0.0, output_cost: 0.0, total_cost: 0.0`, because the
Astra configurations ran with an empty `pricing: {}` block, exactly as the published Sol
Provider Adapter configuration does. ARC therefore priced these runs after the fact rather
than during them, which the ARC-AGI-1 and 2 repository's `update_pricing.py` exists to do,
by the same gross-input rule. The ruling here rests on that code and on cross-check 1, not
on a priced recording.

So, writing `I` for gross input tokens and `O` for output tokens,

```
cost = I * P_input / 1e6 + O * P_output / 1e6
```

with GPT-6 Astra's list prices, USD per million text tokens: input 10.00, cached input
1.00, output 50.00 (`research/cost/list-prices.csv`, price sheet from 2026-09-03;
transcribed in `agent-work/sources/factorio-astra/openai-list-prices-2026-09-13.json`). The
long-context tier starts above 272,000 input tokens and never binds: the harness caps the
context at 175,000 estimated tokens and the measured mean call is 125,000 to 146,000.

### The donor: measured per-call usage on the public demo set

One published number cannot fix two unknowns, so the inversion needs the ratio of output
to gross input. Recovering the dataset's counted-token quantity needs one more, the cached
share of gross input, because COLUMNS `params_tokens` removes cache reads from the
parameter-multiplication term. Both are measured on the companion public-demo runs of the
**same configuration**—same model, same harness, same reasoning effort, same harness
code, same frame format, run on 2026-08-31—differing only in which environments were
played.

| Harness | Effort | Runs | Model calls | Gross input | Cached share k | Output/input r | Mean context per call |
|---|---|---:|---:|---:|---:|---:|---:|
| Standard | max | 25 | 10816 | 1544507000 | 0.1712 | 0.011299 | 142798 |
| Standard | xhigh | 25 | 15807 | 2288122000 | 0.1829 | 0.004468 | 144754 |
| Standard | high | 25 | 14034 | 2015523000 | 0.1747 | 0.002582 | 143617 |
| Standard | medium | 25 | 18018 | 2627726000 | 0.1688 | 0.000810 | 145839 |
| Standard | low | 25 | 20599 | 3003322000 | 0.1446 | 0.000557 | 145799 |
| Standard | none | 25 | 20588 | 2971224000 | 0.1552 | 0.000397 | 144318 |
| Provider Adapter | max | 25 | 6481 | 812876000 | 0.4855 | 0.001090 | 125424 |
| Provider Adapter | xhigh | 25 | 6810 | 862383000 | 0.4965 | 0.000656 | 126635 |
| Provider Adapter | high | 25 | 7078 | 901138000 | 0.4963 | 0.000923 | 127315 |
| Provider Adapter | medium | 25 | 7014 | 890422000 | 0.5063 | 0.005870 | 126949 |
| Provider Adapter | low | 25 | 7587 | 970662000 | 0.5035 | 0.005046 | 127937 |
| Provider Adapter | none | 25 | 8184 | 1050873000 | 0.5107 | 0.007176 | 128406 |

Gross input is rounded to the nearest thousand in this table only; the script uses the
exact counters.

**Why the cached share is so low on the Standard harness, and why it is stable.** Reading
the per-call series of one long run (KA59 at max effort, 785 calls) shows the mechanism
exactly. The context grows by one rendered frame block per turn—call 1 sends 12,461
tokens with nothing cached, call 2 sends 24,915 with 12,458 cached, call 13 sends 161,856
with 149,408 cached, a cached fraction climbing 0.50, 0.67, ... 0.923. At about 161,900
tokens the trimmer starts removing the oldest user/assistant pair every turn to stay under
the 175,000-character estimate, which changes the prefix after the system message and
drops the cache hit to zero. The steady state is therefore an essentially uncached
re-prefill of a ~150,000-token context on every turn, with occasional hits when a
multi-frame turn forces several pairs out at once and the conversation rebuilds. Averaged
over a run that is k = 0.15 to 0.18, and the value is set by the harness's cap and frame
size rather than by the environment, which is what makes it transferable.

The Provider Adapter's compaction reuses about half the prefix, k = 0.49 to 0.51.

### The inversion

For each configuration, with the published cost `C`:

```
I      = C * 1e6 / (P_input + r * P_output)
O      = r * I
cached = k * I
counted tokens T = I - cached + O          (fresh input + cache creation + output,
                                            cache creation zero: see below)
compute_flops = T * 6e11                   (gpt-6-astra, 300B active, 2 * active)
```

and the row records `T / 55` and `flops / 55`, the mean over the 55 environments.

**Cache creation is zero as measured, not as assumed.** Every usage block in the 300
recordings carries `input_tokens_details` with `cached_tokens` and nothing else, so no
cache-write counter was reported for these runs; write-side tokens sit inside the gross
input counter and are already counted as fresh input. The reason is not that OpenAI charges
nothing to write—the folder's own retained Astra price sheet prints a $12.50 cache-write
rate and the page's 1.25x rule—but that no separate write counter exists in what the
provider returned here.

| Harness | Effort | RHAE | Cost, USD | USD/env | Tokens/env | FLOPs/env |
|---|---|---:|---:|---:|---:|---:|
| Provider Adapter | high | 0.9995 | 18816.63 | 342.12 | 17184165 | 1.0310e+19 |
| Provider Adapter | max | 0.9855 | 17331.95 | 315.13 | 16158018 | 9.6948e+18 |
| Provider Adapter | xhigh | 0.9844 | 18147.19 | 329.95 | 16580737 | 9.9484e+18 |
| Provider Adapter | medium | 0.9844 | 19284.78 | 350.63 | 17018076 | 1.0211e+19 |
| Provider Adapter | low | 0.9803 | 21297.92 | 387.23 | 18943551 | 1.1366e+19 |
| Provider Adapter | none | 0.9672 | 23456.66 | 426.48 | 20440242 | 1.2264e+19 |
| Standard | max | 0.6271 | 26097.50 | 474.50 | 37729644 | 2.2638e+19 |
| Standard | xhigh | 0.5934 | 37317.39 | 678.50 | 54522575 | 3.2714e+19 |
| Standard | high | 0.5482 | 40704.72 | 740.09 | 60489354 | 3.6294e+19 |
| Standard | medium | 0.3859 | 48090.35 | 874.37 | 72454230 | 4.3473e+19 |
| Standard | low | 0.1745 | 38166.47 | 693.94 | 59232963 | 3.5540e+19 |
| Standard | none | 0.3518 | 49791.11 | 905.29 | 76363497 | 4.5818e+19 |

The last three lines are not rows; they are here because the disposition reasons quote
them.

Note the shape of the result: **more reasoning effort costs less**, because the model
solves an environment in fewer actions and therefore fewer calls. ARC says so in the blog
post, and the inverted token counts reproduce it.

**Where the uncertainty lives: `r` is second-order and `k` is first-order.** `r` enters
only through the price per gross input token, `10 + 50r`, where `50r / (10 + 50r)` is
0.33% to 3.46% on the six Provider Adapter rows and 1.3% to 5.3% on the three Standard
rows. Halving or doubling `r` moves `game-arcagi3-astra-std-max`, the row with the largest
`r`, by 3.8%, and every other row by under 2%. `k` enters the counted total directly,
through the factor `(1 - k + r)`, so an error in `k` passes through almost one for one.
Every sensitivity below is therefore a test of `k`.

One shape in the donor's output counters is unexplained and worth stating, because it is
the kind of thing that would matter if `r` mattered: output per call runs 83 to 137 tokens
at the Provider Adapter's xhigh, high and max efforts but 646 to 921 at low, medium and
none, the reverse of the Standard harness, which is monotone from 57 at none to 1,614 at
max, and many Provider Adapter calls record 6 output tokens with 0 reasoning tokens. The
configuration labels are confirmed by the session API's own `config` field, so the pattern
is real; it is presumably an artifact of how the Responses API reports usage when encrypted
reasoning state is carried and compacted rather than regenerated.

### Only one transfer, and how much it could be wrong

The folder's geometric-mean rule applies when two transfers of the same donor are equally
defensible and disagree. Here they do not disagree. The alternatives were computed:
taking `k` and `r` from the donor runs the configuration **won** moves the result by 0 to
+8% (median +1%); taking them from the runs it **lost** moves it by -4% to 0%. The mix is
a property of the harness's context cap, not of the environment, so a single transfer is
used and the spread is reported rather than averaged away.

The transfer that could be wrong is a different one: the donor set is 25 public
environments and the priced run is 55 harder ones. That does not enter the mix ratios; it
would enter only if a different environment set changed the cached share.

**The mechanism test is run length, not difficulty.** `k` is set by the trim or compaction
cycle, so it varies with how long a run is, and length is what differs between the sets.
Sorting the 150 donor runs of each harness into quartiles by model calls:

| Harness | Q1 | Q2 | Q3 | Q4 |
|---|---|---|---|---|
| Standard, calls | 75-186 | 188-357 | 357-841 | 854-4212 |
| Standard, mean k | 0.323 | 0.183 | 0.190 | 0.151 |
| Provider Adapter, calls | 75-132 | 134-220 | 226-428 | 431-1310 |
| Provider Adapter, mean k | 0.464 | 0.546 | 0.560 | 0.522 |

The recovered semi-private runs imply 250 to 321 calls per environment on the Provider
Adapter, against a donor range of 259 to 327: the same regime, where donor `k` is flat, so
no correction is indicated. On the Standard harness the three rows imply 315, 458 and 509
calls per environment against donor means of 433, 632 and 561, which lands in the donor's
second and third quartiles at `k` near 0.19 rather than the token-weighted 0.171 to 0.183
the rows use. **At `k = 0.19` the three Standard rows are 1% to 2% high.** That is smaller
than the won/lost bound and points the same way, and it replaces a proxy test with the
mechanism. No correction is applied: 2% sits inside the noise of every other axis, and the
donor's own token-weighted value is the quantity the rest of the arithmetic is built on.

### Cross-checks

1. **Work per environment.** Pricing the donor's own measured counters through ARC's cost
   model gives a public-demo cost per environment; the leaderboard gives a semi-private
   cost per environment. Their ratio is the implied work ratio between the two
   environment sets. For the Provider Adapter it is **0.945 to 0.979 across all six
   efforts**—the semi-private runs did essentially the same work per environment as the
   public ones, which is what a harness scoring ~100% RHAE on both sets should do, since
   RHAE ~100% pins its action count to the human baseline. For the Standard harness it is
   0.58 to 0.91. **This check is corroborative, not dispositive.** The report calls the
   private environments "significantly more difficult", which on its face predicts a ratio
   above 1 for an agent pinned near 100% RHAE; the counter is that the public environments
   run to 6 to 10 levels with a mean human baseline of 685 actions and the released public
   replays take longer than the study-wide median, so the public set is plausibly the
   longer one. The code evidence is what carries the pricing ruling.
2. **The pricing rule.** Under the alternative reading—that ARC priced cache reads at
   $1 per million after all—the same ratio becomes 1.70 to 1.76 for the Provider
   Adapter, meaning the semi-private environments would have to take 70% more work per
   environment at an unchanged score. The code evidence and this check point the same way,
   so the naive rule is the central and the discounted rule is a scenario.
3. **ARC's own published statistics, reproduced on the overlap.** ARC states that the
   Provider Adapter "used 49% fewer total tokens across the 167 game-reasoning pairs both
   harnesses solved" and ran "approximately 3.66x faster by aggregate recorded elapsed
   time", both across Public and Semi-Private together. Restricted to the public half,
   which is all that is measurable here, the extracted counters give **41.1% fewer total
   tokens across the 57 public pairs both harnesses solved**, and an elapsed-time ratio of
   2.64x over all public runs, 2.90x over the both-solved pairs. Same direction, same
   order; the remainder of ARC's statistic comes from the 110 semi-private pairs. The
   saving is on the input side in absolute terms and on the output side in proportion:
   41.0% fewer input tokens against 73.7% fewer output tokens.
4. **Action efficiency, and ARC's two published statistics reproduced.** The session API's
   per-level baselines total 17,135 human actions over the 25 public environments;
   Provider Adapter max used 6,485, or 37.8%. Computing ARC's own two statistics on the
   public half alone gives **51.4% fewer actions per level** on an unweighted mean and
   fewer actions than the baseline on **97.3% of levels**, against ARC's 51.7%
   and 96.0% across both sets. That is close corroboration that the note reads those
   statistics the way ARC computes them.

### Compute scenarios

One at a time, all judgmental rather than confidence intervals, as ratios to the row's
recorded value. Retained in `agent-work/derived/arc-agi-3/calculations.json`.

| Scenario | Provider Adapter rows | Standard rows |
|---|---|---|
| Central | 1.00 | 1.00 |
| ARC priced cache reads at the $1 cached rate | 1.77 to 1.80 | 1.15 to 1.19 |
| Mix taken from the donor runs the config won | 1.00 to 1.01 | 1.00 to 1.08 |
| Mix taken from the donor runs the config lost | 0.96, none effort only | 0.98 to 1.00 |
| Astra 100B active | 0.33 | 0.33 |
| Astra 600B active | 2.00 | 2.00 |
| Recurrent-depth decoding, two passes per token | 2.00 | 2.00 |
| Cached-context attention added, mid shape | +0.98 to +1.02 | +0.87 to +0.90 |
| Cached-context attention added, shape range | +0.61 to +1.44 | +0.55 to +1.27 |

The compounded plain statement: the structural axis that would move a row most is the
pricing rule, and it is one-sided upward; the parameter prior spans 0.33x to 2.0x; and the
attention term, now inside `compute_flops`, is worth roughly as much again as the parameter term.

### Cached-context attention

`compute_flops` now carries the attention term itself, by the recipe in
`research/attention-correction.md`; the scenario below is this note's own bracket for it. These runs are the most extreme case in this batch: essentially
the entire context is re-prefilled on every call.

Attention costs `4 * layers * d_model * context_depth` per processed position, counting a
multiply-add as two operations, the recipe the dataset's RULER row uses. A call whose
cached share is `f` re-prefills the last `(1 - f)` of its context, so its fresh positions
sit at depths from `f*N` to `N` and average `N * (1 + f) / 2`; generated positions sit at
depth `N`. With the measured mean context `N` per call and the measured `k`:

| Assumed shape | Dense-equivalent parameters | 4*L*d | Added, Standard rows | Added, Provider Adapter rows |
|---|---:|---:|---:|---:|
| L=80, d=12288 | 1.45e11 | 3.93e6 | 0.55-0.56x | 0.61-0.64x |
| L=96, d=16384 | 3.09e11 | 6.29e6 | 0.87-0.90x | 0.98-1.02x |
| L=120, d=18432 | 4.89e11 | 8.85e6 | 1.23-1.27x | 1.37-1.44x |

The three shapes bracket the ruled 300B active prior on the standard block's
`12 * layers * d_model^2` count. Astra's architecture is not disclosed. A full operation
count including attention would put these rows 1.55x to 2.44x above their recorded values;
the omission is one-sided.

### What the compute total includes, and what it misses

It includes every model call the harness made for the stated work: exploration, failed
levels, and the reasoning tokens, which are inside the output counter and billed at the
output rate. There is exactly one model in the loop—no helper, no judge, no tool—and
the frames are text, so there are no image positions to separate and `tokens` is the whole
counted workload rather than a text remainder.

**Retries are not a source of bias in either direction**, contrary to what the first
submission said. `benchmarking/agent.py` accumulates the usage of every attempt within a
turn before recording it:

```python
accumulated_usage = accumulated_usage + model_response.usage
model_response = model_response.model_copy(update={"usage": accumulated_usage})
```

The accumulated object is what `_save_step` records, what
`action_metadata_from_model_response` prices, and what the recordings carry, so a
parse-failure retry sits inside both the donor counters and ARC's cost. A call that raises
before that line—a transport error or an empty response—`continue`s, so its tokens are
in neither. The environment's own bookkeeping calls cost nothing.

**Server-side compaction is an unquantified boundary.** The Provider Adapter's context runs
up to about 188,000 tokens and then drops back to 75,000-100,000, so OpenAI is generating
compaction summaries whose own cost does not appear in the per-call usage. If ARC's
published figure is the sum of the recorded counters then the inversion recovers exactly
the recorded work and the question does not arise; if OpenAI billed compaction separately,
provider-billed work exceeds what these rows record.

## Performance and comparison

**`above` for the six Provider Adapter rows** (coordinator's ruling of 2026-09-13, on the
independent review; the first submission carried `match`). The benchmark's metric is
normalised so that 100% is the median human who completed the level, and these six score
96.7% to 99.95% over 55 environments—but **the metric is censored at parity by
construction**, and it is visibly at the ceiling: `E(e)` is the minimum of the
completion-fraction cap and the weighted mean of level scores, every level score is capped
at 1.15, and on the public set the Provider Adapter scored exactly 100.0% on all 25
environments at three of the six efforts with level scores of 115 throughout. That is a
ceiling, not a tie.

The metric's own uncensored input settles it. Across the 25 public environments the
Provider Adapter used **37.8% to 47.8% of the human baseline action count** depending on
effort and beat the baseline on **93.4% to 98.4%** of levels, a factor of
roughly 2.1 to 2.6 against the upper-median human who completed the level, holding across
all six efforts. ARC's own reading is that Astra "matched and surpassed human parity". All
six move together, because the uncensored evidence is qualitatively identical across them,
and each row's `performance_evidence` carries the censoring sentence and its own uncensored
figures.

`far_above` would be wrong. Its test is that the human basically does not do the job, and
RHAE's denominator is by construction a human who completed the level; because the baseline
is the upper-median of completers, about half the completing humans beat it on each level.
The human does the job. The consequence for the dataset is the honest one: about 1e19 FLOPs
per environment buys roughly twice the median completer's action efficiency, so parity
costs somewhat less than these rows record.

**`below` for the three Standard rows.** RHAE 0.6271, 0.5934 and 0.5482, against a human
baseline of 1.0 and a chance floor of about zero: ratios of 0.63, 0.59 and 0.55, all above
the half-of-human guide. The semi-private per-environment outcomes are not published, but
an environment score is capped at the level-weighted fraction of levels completed, so a
mean of 0.55 to 0.63 over 55 environments requires completing most of the levels of most
of them: on an eight-level environment the cap is 0.58 at six levels and 0.78 at seven.
On the companion public-demo set the same three configurations solved 12, 10 and 11 of 25
environments outright. That is the "does the job somewhat worse" limb.

`comparison_issues`, the same three on every row:

- **`different_attempt_selection`.** The human duration is the median of successful
  attempts; the AI compute is the mean over all 55 environments, solved or not. On the
  Standard rows that is the larger asymmetry, since roughly half the AI's environments end
  unsolved.
- **`different_task`.** ARC's duration statistic pools 2,893 attempts over 414 candidate
  environments, while the priced runs are on the 55 semi-private ones, which ARC says are
  significantly more difficult. The per-level *action* baselines that set the score are
  measured on the same environments; only the duration is pooled.
- **`different_inputs_or_tools`.** The human plays a rendered 64x64 grid in a browser and
  sees every animation frame; the agent reads the grid as rows of integers and gets at
  most seven interpolated frames per turn, and its history is truncated at the harness's
  context cap or compacted by the provider. ARC's position is that the two sides receive
  the same information; the encoding, the animation subsampling and the memory limit are
  concrete differences, and they run against the agent rather than for it.

Not used: `different_assessment`. Both sides are scored by the same per-level action
counts against the same baselines, on environments neither had seen.

**`task_category` is `games`, and the divergence from the Codex dataset's ARC-AGI-1 and 2
rows, which are `mathematics_puzzles`, is deliberate** (coordinator's ruling, 2026-09-13).
ARC-AGI-1 and 2 present a rule-based transformation in full and ask for an answer;
ARC-AGI-3 is an interactive turn-based environment played over hundreds of actions with no
stated goal or mechanics, scored on action efficiency, and ARC calls them games throughout.
COLUMNS says to classify the whole task rather than its subject or component skills, and
the folder's other interactive rows—Portal, Factorio, Crafter—are all `games`. The
merge plan should record the split as intended so that a consistency pass does not align
ARC-AGI-3 to the ARC-AGI-1 and 2 rows.

One weakness of the source that is not a `comparison_issues` value, and is the reason ARC
built the semi-private set: a public-set score would be contaminated, because those 25
environments have been available since 2025. These rows are on the held-out 55, which is
what the official leaderboard exists to protect.

## Model record

`gpt-6-astra` is reused unchanged, copied byte for byte from this folder's accepted
`models.csv`: release date 2026-09-03 from the OpenAI API changelog, **300B active
parameters and 6e11 FLOPs per token**, basis `estimated`, under Damon's parameter-prior
ruling of 2026-09-13 with a stated 100-600B sensitivity. No new model record is created by
this study, and the row is identical to the one the Portal and Factorio rows use, so those
three sets cannot drift apart.

The ARC leaderboard's own `modelReleaseDate` for Astra is 2026-09-02 and the results page
dates it 2 September; the registry keeps 2026-09-03, the API changelog's release entry,
which is the date the model became generally available. The companion public-demo runs are
timestamped 2026-08-31 and 2026-09-01, before public release: ARC had pre-release access,
which is normal for its verification programme and is why `ai_cost_date` is the
2026-09-03 price-sheet date rather than a run date.

## Point entries

All nine share: `task_category` games; `model_id` gpt-6-astra; `compute_scope` inference;
`human_skill` typical; `human_time_scope` task_performance; `human_time` 486;
`compute_evidence` derived_assumed_inputs; `human_time_evidence` task_timings;
`human_time_statistic` median; `human_time_subset` successful; `human_attempts` blank;
`human_time_method` other_calculation; `compute_method` params_tokens; `compute_statistic`
mean; `compute_subset` all; `ai_attempts` 55; `tokens_accounting`
input_cache_creation_output; `ai_cost_basis` reported; `ai_cost_date` 2026-09-03;
`human_cost_usd` 12.78; `human_cost_basis` reported_payment.

`compute_evidence` is `derived_assumed_inputs` rather than `transferred_workload`: the
workload's magnitude is set by this run's own published spend, and only the mix that
converts dollars to tokens is carried from another work unit. COLUMNS routes "estimating
this task's workload from its own quantities or constraints" to `derived_assumed_inputs`,
and the Factorio row was classified the same way on the same reasoning.

Per-row figures below. `k` and `r` are the donor mix used for that row.

### game-arcagi3-astra-pa-high

Provider Adapter harness, high reasoning effort. Leaderboard entry
`openai-gpt-6-astra-high-provider-adapter`, RHAE **0.99945712321257**, cost
**$18,816.63138** for the 55-environment run.

```
k = 0.496321, r = 0.000923   (donor: 7,078 model calls over 25 runs; k and r are shown rounded,
    the script uses the exact counters)
price per million gross input = 10 + r * 50 = 10.046152
gross input = 18,816.63138e6 / 10.046152 = 1,873,018,830
cached      = k * gross input = 929,618,641
output      = r * gross input = 1,728,862
counted     = gross - cached + output = 945,129,050
flops       = counted * 6e11 = 5.6708e+20
per environment: 17,184,165 tokens, 1.0310e+19 FLOPs, $342.12
```

`performance_vs_human` `above`: the highest score on the ARC-AGI-3 leaderboard, and on the
public set this configuration used 41.3% of the human baseline actions and beat the
baseline on 95.6% of levels.

### game-arcagi3-astra-pa-max

Provider Adapter, max effort. `openai-gpt-6-astra-max-provider-adapter`, RHAE
**0.9855074288592295**, cost **$17,331.95327**.

```
k = 0.485548, r = 0.001090   (donor: 6,481 model calls over 25 runs; k and r are shown rounded,
    the script uses the exact counters)
price per million gross input = 10 + r * 50 = 10.054514
gross input = 17,331.95327e6 / 10.054514 = 1,723,798,259
cached      = k * gross input = 836,986,670
output      = r * gross input = 1,879,414
counted     = gross - cached + output = 888,691,003
flops       = counted * 6e11 = 5.3321e+20
per environment: 16,158,018 tokens, 9.6948e+18 FLOPs, $315.13
```

This is the configuration ARC analysed: on the public demo set it used 6,485 actions
against 17,135 human baseline actions, 37.8%, and beat the baseline on 97.3% of levels. ARC reports the same two statistics across both sets as 51.7% fewer actions
per level and 96.0% of levels. `above`, with the public-set figures in
`performance_evidence`.

### game-arcagi3-astra-pa-xhigh

Provider Adapter, xhigh effort. `openai-gpt-6-astra-xhigh-provider-adapter`, RHAE
**0.9844155844155843**, cost **$18,147.19112**.

```
k = 0.496483, r = 0.000656   (donor: 6,810 model calls over 25 runs; k and r are shown rounded,
    the script uses the exact counters)
price per million gross input = 10 + r * 50 = 10.032818
gross input = 18,147.19112e6 / 10.032818 = 1,808,783,126
cached      = k * gross input = 898,029,785
output      = r * gross input = 1,187,197
counted     = gross - cached + output = 911,940,538
flops       = counted * 6e11 = 5.4716e+20
per environment: 16,580,737 tokens, 9.9484e+18 FLOPs, $329.95
```

### game-arcagi3-astra-pa-medium

Provider Adapter, medium effort. `openai-gpt-6-astra-medium-provider-adapter`, RHAE
**0.9843861309255745**, cost **$19,284.77663**.

```
k = 0.506270, r = 0.005870   (donor: 7,014 model calls over 25 runs; k and r are shown rounded,
    the script uses the exact counters)
price per million gross input = 10 + r * 50 = 10.293522
gross input = 19,284.77663e6 / 10.293522 = 1,873,486,775
cached      = k * gross input = 948,490,765
output      = r * gross input = 10,998,178
counted     = gross - cached + output = 935,994,187
flops       = counted * 6e11 = 5.6160e+20
per environment: 17,018,076 tokens, 1.0211e+19 FLOPs, $350.63
```

### game-arcagi3-astra-pa-low

Provider Adapter, low effort. `openai-gpt-6-astra-low-provider-adapter`, RHAE
**0.9802838165829648**, cost **$21,297.92231**.

```
k = 0.503503, r = 0.005046   (donor: 7,587 model calls over 25 runs; k and r are shown rounded,
    the script uses the exact counters)
price per million gross input = 10 + r * 50 = 10.252307
gross input = 21,297.92231e6 / 10.252307 = 2,077,378,601
cached      = k * gross input = 1,045,966,030
output      = r * gross input = 10,482,726
counted     = gross - cached + output = 1,041,895,297
flops       = counted * 6e11 = 6.2514e+20
per environment: 18,943,551 tokens, 1.1366e+19 FLOPs, $387.23
```

### game-arcagi3-astra-pa-none

Provider Adapter, reasoning effort none. `openai-gpt-6-astra-none-provider-adapter`, RHAE
**0.9672021831785531**, cost **$23,456.66394**.

```
k = 0.510707, r = 0.007176   (donor: 8,184 model calls over 25 runs; k and r are shown rounded,
    the script uses the exact counters)
price per million gross input = 10 + r * 50 = 10.358798
gross input = 23,456.66394e6 / 10.358798 = 2,264,419,522
cached      = k * gross input = 1,156,455,582
output      = r * gross input = 16,249,374
counted     = gross - cached + output = 1,124,213,315
flops       = counted * 6e11 = 6.7453e+20
per environment: 20,440,242 tokens, 1.2264e+19 FLOPs, $426.48
```

The lowest-scoring Provider Adapter configuration and the most expensive: with no
reasoning budget the model needs more actions, and more actions is what the cost tracks.
It is still the weakest of the six on the uncensored axis as well, at 47.8% of the human
baseline actions against max's 37.8% and beating the baseline on 93.4% of levels against
max's 97.3%, and still `above`. It is also the only one of the six that did not solve every
environment, so it is the only one whose pooled denominator of 183 baselined levels exceeds
the 180 it completed; the other five completed all 183, which is why the two denominators
part company here and nowhere else.

### game-arcagi3-astra-std-max

Standard harness, max effort. `openai-gpt-6-astra-max`, RHAE **0.6271280210060628**, cost
**$26,097.50172**.

```
k = 0.171231, r = 0.011299   (donor: 10,816 model calls over 25 runs; k and r are shown rounded,
    the script uses the exact counters)
price per million gross input = 10 + r * 50 = 10.564971
gross input = 26,097.50172e6 / 10.564971 = 2,470,191,625
cached      = k * gross input = 422,972,924
output      = r * gross input = 27,911,709
counted     = gross - cached + output = 2,075,130,411
flops       = counted * 6e11 = 1.2451e+21
per environment: 37,729,644 tokens, 2.2638e+19 FLOPs, $474.50
```

`below`: 0.627 of the human baseline, comfortably above the half-of-human guide. On the
public demo set the same configuration solved 12 of 25 environments outright.

### game-arcagi3-astra-std-xhigh

Standard, xhigh effort. `openai-gpt-6-astra-xhigh`, RHAE **0.5934295409146055**, cost
**$37,317.38768**.

```
k = 0.182939, r = 0.004468   (donor: 15,807 model calls over 25 runs; k and r are shown rounded,
    the script uses the exact counters)
price per million gross input = 10 + r * 50 = 10.223399
gross input = 37,317.38768e6 / 10.223399 = 3,650,193,744
cached      = k * gross input = 667,761,126
output      = r * gross input = 16,309,005
counted     = gross - cached + output = 2,998,741,623
flops       = counted * 6e11 = 1.7992e+21
per environment: 54,522,575 tokens, 3.2714e+19 FLOPs, $678.50
```

### game-arcagi3-astra-std-high

Standard, high effort. `openai-gpt-6-astra-high`, RHAE **0.5481905163612231**, cost
**$40,704.72283**.

```
k = 0.174703, r = 0.002582   (donor: 14,034 model calls over 25 runs; k and r are shown rounded,
    the script uses the exact counters)
price per million gross input = 10 + r * 50 = 10.129077
gross input = 40,704.72283e6 / 10.129077 = 4,018,601,308
cached      = k * gross input = 702,061,041
output      = r * gross input = 10,374,195
counted     = gross - cached + output = 3,326,914,462
flops       = counted * 6e11 = 1.9961e+21
per environment: 60,489,354 tokens, 3.6294e+19 FLOPs, $740.09
```

The most expensive row in the set and the lowest-scoring of the three Standard rows: at
$740 per environment it spends 2.2 times what the best Provider Adapter configuration
spends to reach 55% of the human baseline instead of 100%. The pair is the clearest
statement this source makes—the same model on the same environments, parity or half
parity, depending on whether its context is managed by a rolling text window or by the
provider's own state and compaction.

## Dispositions

`candidates/arc-agi-3/dispositions.csv` records all 39 leaderboard entries and the 12
public-demo configurations. Built by `research/arc-agi-3/build_dispositions.py`.

**Thirty leaderboard entries are not rows** because their RHAE is below half the human
baseline on the benchmark's own metric, with a chance floor of about zero. The three
closest to the line are Astra Standard medium at 0.3859, Astra Standard none at 0.3518 and
Claude Opus 5 (High) at 0.3016. The close-call rule keeps a row within one standard error
of the 0.5 guide; the standard error of a mean over 55 environments cannot exceed
`0.5 / sqrt(55) = 0.0674` for a metric bounded in [0, 1], so an entry more than 0.0674
below 0.5 is excluded whatever its dispersion. Those three sit 1.69, 2.20 and 2.94 such
bounding standard errors below the guide; at the dispersion actually measured for the two
Astra configurations on the public set (per-environment SD 0.387 and 0.393) they sit 2.19
and 2.80. No entry is a close call.

Three entries—Claude Opus 4.8 (High), GPT-5.5 (High) and Opus 4.7 (High)—report a cost
of exactly $10,000, which is the per-run cap in ARC's testing policy ("We cap our
evaluations at $10,000 USD per run"); their scores are censored by that cap as well as
being far below the line. The Astra runs cost $17,000 to $50,000, so the published cap did
not apply to them, and the policy page is presumably stale on that point.

**The 12 public-demo configurations are not rows either**, and this is the disposition
most worth a second look. They have better compute evidence than the rows that were
built—the token counters are measured per call rather than inverted—and a measured
per-environment human duration from the released replays. They are not built because ARC
states that it will never report public-set scores on the official leaderboard, that the
public set is materially easier than the private set, and that evaluating on it "is
emphatically not a valid measure of progress"; the 25 environments have been public since
2025 and a score on them cannot be separated from exposure. Their measured counters serve
this study as the donor for the inversion instead, which is the use their evidence
supports.

## Reproduction

From this folder, in order. Each script takes explicit input and output paths and writes
new files rather than modifying the retained evidence.

```
python3 research/arc-agi-3/parse_results_page.py \
  agent-work/sources/arc-agi-3/arcprize-results-openai-gpt-6-astra-2026-09-13.html \
  /tmp/arc3-cells.csv

python3 research/arc-agi-3/fetch_sessions.py \
  agent-work/sources/arc-agi-3/astra-public-demo-cells-2026-09-13.csv \
  /tmp/arc3-sessions.json /tmp/arc3-runs.csv

python3 research/arc-agi-3/fetch_usage.py \
  research/arc-agi-3/astra-public-demo-runs.csv /tmp/arc3-usage.csv

python3 research/arc-agi-3/human_durations.py \
  <parquet-dir> /tmp/arc3-human-sessions.csv

python3 research/arc-agi-3/compute_arc3.py \
  agent-work/sources/arc-agi-3/arc-agi-3-leaderboard-v3-2026-09-13.json \
  agent-work/sources/arc-agi-3/astra-public-demo-usage-2026-09-13.csv \
  research/arc-agi-3/astra-public-demo-runs.csv \
  /tmp/arc3-calculations.json /tmp/arc3-inversion-summary.csv

python3 research/arc-agi-3/build_rows.py \
  agent-work/derived/arc-agi-3/calculations.json /tmp/arc3-points.csv

python3 research/arc-agi-3/build_dispositions.py \
  agent-work/sources/arc-agi-3/arc-agi-3-leaderboard-v3-2026-09-13.json \
  agent-work/sources/arc-agi-3/astra-public-demo-cells-2026-09-13.csv \
  /tmp/arc3-dispositions.csv
```

`build_rows.py` writes `candidates/arc-agi-3/points.csv` and `build_dispositions.py`
writes `candidates/arc-agi-3/dispositions.csv`; both are shown here writing elsewhere so a
reproduction does not overwrite the candidate files.

`human_durations.py` needs the released dataset's parquet shards; fetch them with
`hf download magic-sword/arc_agi_3_public_demo_human_testing --repo-type dataset
--local-dir <dir>` and pass `<dir>/data`. `fetch_sessions.py` and `fetch_usage.py` need
network access to `arcprize.org`; the usage pass streams about 6.2 GB of recordings and
retains none of it. The other three run offline against the retained sources.
