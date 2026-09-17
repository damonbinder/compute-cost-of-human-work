# GPT-6 Astra completing Portal

*Created 2026-09-13 09:06.*
*Last revised 2026-09-13 13:32, recomputed at the ruled 300B-active GPT-6 Astra prior. Change log in `candidates/portal-astra/REVISION.md`.*

## Summary

One continuous GPT-6 Astra run at `max` reasoning effort played Portal (2007)
from a new game to the end of the credits on 4–5 September 2026, driven by
`cozyblazex` through a published harness. The operator released the controller,
the SourcePauseTool patch, the game configuration, a 6,925-record sanitized
session log and an `evidence/summary.json` carrying cumulative thread token usage
split into cached and fresh input. Excluding the 426,415,104 cache reads, the run
charges **8,394,030 billed units**; removing the estimated **3,037,392 billable
image units** for 3,262 screenshots leaves **5,356,638 text tokens**, and adding
back **2,531,160 image patch positions** gives **7,887,798 processed positions**
and **4.7327e18 FLOPs** at the ruled 300B-active-parameter prior. The human
baseline is HowLongToBeat's Portal main-story **mean of 11,660 seconds over 8,059
completions**. Both sides finish the game, so the comparison is `match`.

Two things move the number, and they are of comparable size.

1. **The 300B active-parameter prior is a ruling, not an OpenAI disclosure.** It
   rests on the September 2026 pricing cross-check, whose own central is 250B and
   whose markup-equalizing figure is 333B. The ruled sensitivity **100–600B**
   moves the result to **1.58e18–9.47e18**, 0.33x to 2.0x.
2. **Cached-context attention is one-sided upward.** The `2 * active_parameters`
   coefficient prices matrix work only. This run appends every position after a
   ~130,000-token prefix, so the attention on top of the parameter-only value is
   **2.15e18 to 4.84e18**, 0.45x to 1.02x of it. `research/attention-correction.md`
   folds the term into `compute_flops` for every row in the file; it is priced
   here in [Compute scenarios](#compute-scenarios).

Astra is reported to use "recurrent depth" decoding, which would multiply a
parameter-only coefficient by its pass count. That is no longer a separate
multiplier on top: the prior is derived from price per token and serial output
speed, both of which respond to FLOPs per emitted token however those FLOPs
arise, so a loop multiplier is already inside the 300B figure.

Everything else is measured or read off the released artifacts: the counters, the
cache split, the 3,262 screenshots, the 1280x720 full-resolution size recovered
from the agent's own screen-to-world helper, and the 8,059-completion human
sample.

## Shared evidence

### The run and its work unit

Primary artifact: `https://github.com/cozyblaze/portal-agent`, cloned at commit
`31311b8fde8f242cc403bd51d45cb615ed645e4b` on 2026-09-13. The repository is the
setup actually used, not a reconstruction; `docs/publication.md` records what was
stripped from the release (screenshots, reasoning payloads, host prompts, device
metadata, original call identifiers).

The goal is record 1 of the session log, verbatim:

> `/goal You are controlling Portal. Your goal is to progress through the game and reach the end credits. Do not cheat/look up information about the game online.`

Record 6925, the last: "The credits played through to the end. The game is now at
the main menu." The only other user message in the whole log is record 6904,
"leave the credit rolling". Both are retained in
`agent-work/sources/portal-astra/session-excerpts.jsonl`. `messages_by_role` in the scan
confirms exactly two user messages across 6,925 records, which is the operator's
claim that the agent handled gameplay throughout.

The harness, from `docs/how-it-works.md` and `controller/mcp/portal-documentation.md`:
Portal is paused while the model thinks. Each turn the agent receives a
screenshot, the world-space player origin and the camera angles, then queues a
TAS-style plan of up to 1,000 steps and 6,600 ticks (about 99 seconds at the
configured ~67 ticks/s) and lets it play back. `sv_cheats 1` was enabled for
debugging commands and `sv_accelerate`, `sv_friction` and `sv_stopspeed` were
raised to reduce sliding (`game-config/autoexec.cfg`). Web search and general
shell and browser tools were disabled. The game is Source Unpack 2.6, build 5135.

`evidence/README.md` and the repository README record that the session was
resumed after capacity errors and switched to Fast mode partway. Under COLUMNS
this is still one continuous goal run, so `ai_attempts` is 1. The interruptions
left no recoverable trace: the exporter drops host and system records, so no
error record survives, and the exported timeline has no gap longer than 313
seconds (between sequences 3192 and 3193) across 85,643 seconds, with only 53
gaps of two minutes or more. A request rejected before dispatch contributes no
forward pass, and nothing in the export suggests completed responses were lost,
so no retry allowance is added.

### Counters and what they mean

`evidence/summary.json`, retained verbatim at `agent-work/sources/portal-astra/summary.json`:

| Field | Value |
|---|---:|
| input_tokens | 433210793 |
| cached_input_tokens | 426415104 |
| cache_write_input_tokens | 0 |
| output_tokens | 1598341 |
| reasoning_output_tokens | 1181102 |
| total_tokens | 434809134 |
| elapsed_to_completion_seconds | 85354 |
| source_records | 26460 |
| exported_records | 6925 |
| removed_images | 3263 |

`evidence/README.md` states the counter semantics directly: "Cached input is
included in input-token counts; reasoning output is included in output-token
counts." That makes `input_tokens` a superset of `cached_input_tokens`, and
`total_tokens` is `input_tokens + output_tokens` exactly (433,210,793 +
1,598,341 = 434,809,134), which confirms the reading. So fresh input is
433,210,793 − 426,415,104 = **6,795,689**, and output is counted once at
1,598,341 with its reasoning share inside it.

**Cache writes are inside the input count, not beside it.** OpenAI's
prompt-caching guide partitions the input counter three ways —
`ordinary_input_tokens = input_tokens − cached_tokens − cache_write_tokens` —
and states that cache-write pricing is not an additive fee: an input token is
billed at the uncached, cached or cache-write rate, and writing happens on the
same forward pass as processing. Two consequences. Subtracting the cache reads
already leaves every newly processed input token, so a reported
`cache_write_input_tokens` of zero cannot conceal processed work. And adding a
cache-creation counter on top of that subtraction would double-count it; the
figure here is unaffected only because the counter is zero. COLUMNS' `params_tokens`
wording ("count fresh input, cache creation and output") is written for
Anthropic-style counters, which report cache creation additional to input; it is
flagged for the specification in the review report.

Three independent cross-checks support the counters:

- **Cost, which confirms the split and not merely the total.** At OpenAI list
  prices ($10/M input, $1/M cached input, $50/M output) the final counters imply
  $574.29 against the overlay's **$571.33**, read at slightly earlier counter
  values. Better, the overlay's figure can be solved for the split it was
  computed from: at its own 430.7M input and 1.6M output,
  `(430.7 − C) × 10 + C × 1 + 1.6 × 50 = 571.33` gives C = 423.96M cached and
  6.74M fresh, against the final 6.796M. The cached/fresh decomposition is
  therefore corroborated directly, not just inferred from a matching total.
- **Context size, order of magnitude only.** The overlay reads CONTEXT 50%
  (130.0k / 258.4k). Dividing the cache reads by that context gives
  426,415,104 / 130,000 ≈ 3,280, the same order as the log's 3,269 tool calls.
  Three counters disagree on what a tool call is — the overlay reads TOOL CALLS
  3,337 and `summary.json` sums to 3,306 MCP method calls — so this check
  establishes that the prefix was held near 130k throughout, nothing finer.
- **Screenshots.** The log contains 3,262 structured image blocks plus one text
  echo of an image block, together matching the exporter's `removed_images: 3263`.

One limitation remains. The export omits 19,535 of 26,460 source records,
explicitly including context-compaction, history and note tool records. The token
counters are cumulative reported thread usage and do cover that work, but the log
does not show it, so the text side of the workload cannot be reconstructed record
by record.

### Screenshot count and resolution, established from the log

**Count.** 3,262 images were sent. The log carries 3,263 occurrences of
`image_omitted`, but one of them is a text echo: at `call-00002` the agent printed
the MCP result with `text({index:i,result:r.value})` before emitting the image
with `image(c)`, so the same image appears once as a structured block and once as
a string inside a text payload. The exporter's `removed_images: 3263` counts the
echo too, which is why a naive count agrees with it.

**Resolution.** The repository does not record the game's video mode, and SPT
captures whatever `GetBackBufferDimensions` returns (`spt/portal-agent.patch`).
The resolution is nevertheless recoverable from the agent's own code. Twice
during the run the agent defined a screen-to-world helper (records 3186 and 4753,
retained):

```js
portalAimPixel = async function(px,py){ ... u=(px-640)/480, v=(360-py)/480; ... }
```

and later the same helper with the divisor changed from 480 to 640. The divisor
is a field-of-view calibration; the principal point is **(640, 360)** in both, so
the full-resolution screenshot is **1280x720**. The 153 recorded calls span x from
172 to 1238 and y from 46 to 646, consistent with 1280x720 and impossible on the
640x360 reduction.

The token arithmetic bounds the resolution from above independently. Fresh input
is 6,795,689. The agent's own 1,598,341 output tokens must re-enter the prompt as
input, and the tool results it read are 197,331 tokens, so image billing cannot
exceed about 5.00M. At a 1920x1080 backbuffer the 2,571 full-resolution images
alone would bill 2,571 × 2,448 = 6,293,808 units, leaving 501,881 of fresh input
for the 691 reduced images, the re-entering output, every tool result and every
compaction rewrite. That is impossible; 1280x720 fits with room to spare.

**Classification.** `controller/index.mjs` reduces screenshots taller than 360
pixels to 360 by default (`fit360p`, preserving aspect ratio) and returns the
native size when `fullRes: true` is passed; `portal_screenshot` always captures at
full resolution. Each image is attributed to the options of the cell that
produced it:

| Image source | Count | Pixels |
|---|---:|---|
| `fullRes: true` or `portal_screenshot` | 2571 | 1280x720 |
| controller default | 691 | 640x360 |
| total | 3262 | — |

Eight of those images arrived late. A cell that outruns its turn returns "Script
running with cell ID N", the agent then issues a `wait` call carrying
`{"cell_id": "N"}`, and the image comes back in the wait's result, whose own input
carries no `fullRes` flag. `scan_session.py` resolves each wait to the cell that
announced its id and classifies by that cell: seven of the eight ran
`t.run({fullRes: true})` and one (`call-00004`) was a default run. The retained
scan lists all eight resolutions and reports none unresolved.

No cell is ambiguous. `call-03037`, which returns three images, loops three times
calling `portal.screenshot({fullRes: true})` after a `run({screenshot: false})`, so
all three are genuinely full resolution.

## Compute

The model record and its parameter prior are in [Model record](#model-record).
The arithmetic is reproduced by
`research/portal-astra/compute_portal_astra.py`, whose output is retained at
`agent-work/derived/portal-astra/calculations.json`.

### Cache accounting

Following COLUMNS `params_tokens` and `collection-work/DECISIONS.md`, known cache
reads are removed from the parameter-multiplication term and the native
components are retained. Because OpenAI partitions cache writes inside the input
counter rather than beside it, the charged quantity is the input counter net of
cache reads, plus output counted once including reasoning:

```
charged units = (input_tokens - cached_input_tokens) + output
              = (433,210,793 - 426,415,104) + 1,598,341
              = 8,394,030
```

This is the rare case where the decomposition is published rather than assumed,
which is the gap flagged for the Gemini Crystal row in
`../AI Compute vs Human Time/dataset/research/pokemon-agents/pokemon-crystal.md`.

**Attention over the cached context is, for this row, of the same order as the
whole parameter-only value.** The convention costs a position
at `2 * active_parameters`, which prices the projection and feedforward matrices
and nothing else. A row whose positions are appended after a few thousand tokens
of context loses little to that; this run appends essentially every one of its
7,887,798 positions after a ~130,000-token prefix. The dataset's own
explicit-attention row, `memo-ruler-passkey-131072-llama31-8b`, puts attention at 70.5% of central
compute at a 130,893-token context. The magnitude here is quantified in
[Compute scenarios](#compute-scenarios): at the ruled 300B prior the term
is 0.45x to 1.02x of the parameter-only value, comparable to the parameter sensitivity
and, unlike it, one-directional. `compute_flops` is left on the convention so the
row stays comparable with the other 1,410 points; the reviewer has raised the
dataset-level question separately.

### Text and visual split

OpenAI's images-and-vision guide puts `gpt-6-astra` in the patch-tokenization
family: patches are 32x32 and the billable count is `ceil(patches * 1.2)` for
Astra. Resolution settings turn out not to matter here. 1280x720 is 920 patches,
comfortably under Astra's 2,500-patch `detail: high` budget, and `original` and
`auto` preserve submitted dimensions, so every detail level except `low` yields
the same 920 patches and 1,104 billable units. (Images from `portal_exec` reach
the model as MCP image content under the `auto` default: `emitImage` in
`controller/index.mjs` returns through the `globalThis.nodeRepl` branch that
`controller/mcp/portal-mcp-server.mjs` installs, never reaching the
`codex.emitImage` call that would set `detail: "original"`.) The rules as read are
summarized in `agent-work/sources/portal-astra/openai-astra-image-and-release.md`.

| Image | Patches | Billable units |
|---|---:|---:|
| 1280x720 | ceil(1280/32) * ceil(720/32) = 40 * 23 = 920 | ceil(920 * 1.2) = 1104 |
| 640x360 | ceil(640/32) * ceil(360/32) = 20 * 12 = 240 | ceil(240 * 1.2) = 288 |

```
billable image units = 2,571 * 1,104 + 691 * 288 = 3,037,392
image patch positions = 2,571 *   920 + 691 * 240 = 2,531,160
```

That these billable units sit inside the reported `input_tokens` rather than
beside it is documented behaviour: OpenAI's vision guide converts image inputs
into billable input tokens and the Responses API reports them in
`usage.input_tokens`. The scenario table prices the alternative anyway. So the
text-token workload is the remainder:

```
text tokens = 8,394,030 - 3,037,392 = 5,356,638
```

The 1.2 multiplier is a billing multiplier, not a position count, so the backbone
is charged one position per patch rather than per billable unit. That is the same
separation the dataset already makes for ImageNet and Pokémon Crystal
("visual accounting units are not assumed to be physical positions"), though here
the published tokenizer makes the patch-to-position mapping much less speculative
than a CLIP proxy. Projecting each patch to exactly one decoder position remains
an assumption about Astra's adapter.

Two smaller effects, both left unpriced. Each image's billable units are
subtracted once, which assumes every image is charged fresh exactly once; a
compaction that preserves images, or a lapsed cache, would re-charge one. The
direction is mild and the exposure small — OpenAI's 30-minute cached-prefix
lifetime against a 26-second mean turn interval makes lapses rare, and charging
every image twice would move backbone positions down about 6%. And no separate
vision-encoder term is added: following the GDPval treatment, image preprocessing
is folded into the approximation rather than given a fictitious disclosed
encoder. This diverges from the nearer precedent, Pokémon Crystal, which adds an
explicit CLIP ViT-bigG frontend term; the divergence is immaterial, since a
ViT-scale patch embedder at 2B parameters over 2,531,160 patches would contribute
about 1.0e16 FLOPs, roughly 0.2% of the total and well inside the parameter
uncertainty.

### Result

```
backbone positions = 5,356,638 text + 2,531,160 visual = 7,887,798
compute_flops      = 2 * 300e9 * 7,887,798 = 4.7326788e18
```

`compute_method` is `operation_count` rather than `params_tokens` because the
multiplied position count is not the CSV `tokens` field: text tokens exclude the
image workload, which is charged separately. `compute_evidence` is
`derived_assumed_inputs`, driven by the assumed model size rather than by the
token counters, which are measured for this work.

### Does the text remainder make sense

A partial bottom-up check. Tokenizing the log's own text with `o200k_base`, the
tool results the agent read total 197,331 tokens and the JavaScript it wrote
totals 295,040 against a reported non-reasoning output of 417,239 — the gap being
the tool-call envelope and the 19,535 omitted records. Fresh input text is
5,356,638 − 1,598,341 = 3,758,297, of which 197,331 is tool-result text, leaving
3,560,966. The model's own output re-enters the prompt on the next turn as fresh
input (up to 1,598,341), and each context compaction rewrites the prefix so the
new prefix is charged fresh once; the residual after output is about 1.96M, or
roughly fifteen 130k prefix rewrites across 24 hours. The decomposition is
coherent, which it would not be if the image estimate were badly wrong: charging
every image at the 30,000-patch cap would leave a negative text remainder, and
the 1080p case fails the same test as shown above.

### Compute scenarios

Retained in `agent-work/derived/portal-astra/calculations.json`. One-at-a-time, all
judgmental rather than confidence intervals.

| Scenario | FLOPs | Ratio to central |
|---|---:|---:|
| Central, 300B active | 4.7327e18 | 1.00 |
| 100B active parameters, ruled low | 1.5776e18 | 0.33 |
| 600B active parameters, ruled high | 9.4654e18 | 2.00 |
| Billable image units charged as positions | 5.0364e18 | 1.06 |
| Image tokens additional to, not inside, the input counter | 6.5551e18 | 1.39 |
| Plus cached-context attention, L=64, d=8192 | 6.8831e18 | 1.45 |
| Plus cached-context attention, L=96, d=12288 | 9.5712e18 | 2.02 |
| Recurrent depth, two passes on a parameter-only coefficient | 9.4654e18 | 2.00 |
| Recurrent depth, four passes on a parameter-only coefficient | 1.8931e19 | 4.00 |
| Full prefix charged, no cache-read exclusion | 2.6058e20 | 55.06 |

**Cached-context attention.** Attention FLOPs per appended position are
`4 * layers * d_model * context_positions`, counting the QK and attention-value
products at two operations per multiply-add. This is the recipe
`dataset/research/ruler/ruler.md` uses, and it reproduces that note's own figure:
at L=32, d=4096 and N=130,893.424 its causal triangle `4Ld * N(N+1)/2` gives
4.491e15, 70.49% of that row's 6.3716e15 central value, which is the 70.5% the
note states. Applying it here at N = 130,000 over 7,887,798 appended positions:

| Assumed shape | 4·L·d | FLOPs per position | Attention total | Ratio to 4.7327e18 |
|---|---:|---:|---:|---:|
| L=64, d=8192 | 2.10e6 | 2.73e11 | 2.1504e18 | 0.45 |
| L=80, d=10240 | 3.28e6 | 4.26e11 | 3.3601e18 | 0.71 |
| L=96, d=12288 | 4.72e6 | 6.13e11 | 4.8385e18 | 1.02 |

Attention cost depends on layer count and model width, not on how many experts a
position activates, so the shapes are not re-derived from the new prior; they
bracket a frontier decoder's geometry. A model at 300B active plausibly sits at or
above the top of the bracket, which would make this figure conservative. Astra's
architecture is not disclosed. A full operation count including cached-context
attention would land at roughly **6.9e18–9.6e18**, 1.45x to 2.0x the recorded
value. Unlike the parameter prior this is one-sided: the omission can only
understate, never overstate.

The cache-read row is the reason the published decomposition matters in the other
direction: charging the full prefix would inflate the estimate 55-fold. The
recurrent-depth rows are retained to show what an explicit pass count would do to
a parameter-only coefficient, but they are not additive on top of the central
value: the price-and-output-speed route behind the 300B prior measures FLOPs per
emitted token, so it already absorbs any loop multiplier, as
`research/model-priors/openai.md` sets out.

## Human baseline

HowLongToBeat's Portal page (`https://howlongtobeat.com/game/7230`, retrieved
2026-09-13) supplies the timings, parsed from the page's embedded JSON rather
than its rounded display strings. Retained at
`agent-work/sources/portal-astra/howlongtobeat-portal-7230.json`, with the whole payload
alongside it.

| Statistic | Seconds | Polled |
|---|---:|---:|
| Main story, average | 11660 | 8059 |
| Main story, median | 10800 | 8059 |
| Main story, HowLongToBeat headline | 11230 | 8059 |
| Main story, rushed | 6515 | 8059 |
| Main story, leisure | 30815 | 8059 |
| Main + extras, average | 19866 | 2325 |
| Completionist, average | 39769 | 1141 |
| All styles, average | 16098 | 11525 |

**Value used: 11,660 seconds, the arithmetic mean of 8,059 main-story
completions.** COLUMNS prefers the arithmetic mean where the source offers one,
so the mean is used rather than the more commonly quoted 10,800-second median.

- `human_skill` is `typical`. HowLongToBeat's submitters are self-selected people
  who play and log games; they are not selected for skill at Portal, and they are
  not novices at games in general. Portal's main story is the same completion
  criterion the agent was given: reach the end.
- `human_time_scope` is `task_performance` and `human_time_evidence` is
  `task_timings`. These are recorded timings for the stated task and population,
  aggregated by the source.
- `human_time_method` is `other_calculation`: the source averaged raw
  observations. That is arithmetic on recorded timings, not a judgment-based
  estimate, and COLUMNS asks for the substantive derivation rather than the final
  arithmetic step. `reported` is defined as a recorded timing taken directly in
  seconds, singular; 11,660 is a statistic over 8,059 timings, which is why the
  row also carries `human_time_statistic = mean`. The independent review
  confirmed this against precedent.
- `human_time_subset` is `successful` with `human_attempts` 8,059. The polled
  main-story times come only from players who finished. This is a selection rule,
  not a human success rate: the same page lists 1,171 users who retired the game
  against 42,752 who completed it.

Limitations worth stating. The times are self-reported and unverified, and
self-report on a game this short is coarse. HowLongToBeat does not publish the
raw submissions, so the mean cannot be recomputed. The page also counts 1,506
replays, and whether a replay can add a second main-story entry is not
documented, so 8,059 is the source's polled count rather than a verified count of
distinct players.

### Alternative human populations

Kept here as scenarios rather than as hedges in the CSV.

| Population | Seconds | Basis |
|---|---:|---|
| Typical player, main story, mean | 11660 | HowLongToBeat, n=8059 (the value used) |
| Typical player, main story, median | 10800 | HowLongToBeat, n=8059 |
| Self-described speedrunners | 2821 | HowLongToBeat speedrun style, mean, n=185 |
| World class, Glitchless world record | 863.43 | speedrun.com run z0de5gey, 2024-02-19 |
| World class, Inbounds world record | 433.425 | speedrun.com run ylwnxvnz, 2026-08-31 |
| World class, Out of Bounds world record | 305.955 | speedrun.com run yvkowwxm, 2026-08-11 |

A `world_class` row against the 863-second Glitchless record would be a different
point, not a correction to this one: a single record holder is not a timing
sample, the speedrun categories permit routing knowledge the agent was told not
to use, and the glitch categories are a different task. Retained at
`agent-work/sources/portal-astra/speedrun-portal-leaderboards.json`.

## Performance and comparison

`performance_vs_human` is `match`. The criterion is completion, the agent met it,
and every contributing human time is also a completion. Nothing in the evidence
grades the two on a quality scale beyond finishing.

The two AI clocks are context, not the comparison axis, and they point in
opposite directions:

- **In-game 6,817.42 seconds**, read from the overlay's timer at completion
  (1:53:37.42), with per-chamber splits from 04/05 at 9:30 through e02 at
  1:53:37. The log corroborates the order of magnitude: the tick counts visible
  in exported tool results sum to 429,972 ticks, 6,417 seconds at ~67 ticks/s.
  That is a lower bound: only 2,543 of the 3,269 tool results carry a tick
  figure in the text export, and loading and cutscene time is not in it.
- **Wall clock 85,354 seconds** to completion, from `summary.json`, which is 7.3
  times the human mean.

Neither is a like-for-like speed comparison. Portal is paused while the agent
thinks, so its in-game timer excludes exactly the deliberation that the human
figure includes. Calling the run faster than a human on the strength of 6,817
seconds would be an artifact of the harness. The dataset's axes are FLOPs and
human active seconds; these clocks stay in the notes.

`comparison_issues`:

- `different_inputs_or_tools`. The agent played with `sv_cheats 1` enabled,
  raised movement cvars, exact world-space position and camera-angle readouts,
  and queued deterministic input plans with the game frozen between decisions. A
  human plays in real time with mouse and keyboard and no position readout. The
  execution and reflex component of Portal is largely removed for the agent, and
  the puzzle component is not. `sv_cheats 1` did not hand the agent cheats: the
  MCP sandbox exposes only the documented `portal` object, and the independent
  review searched all 6,925 records and found no console command, no `noclip`, no
  `impulse 101` and no map warp — the only recoveries are ordinary in-game
  checkpoint reloads. The flag is a prerequisite for SPT's own plumbing.
- `different_attempt_selection`. The human times are polled only from players who
  completed and submitted; the AI figure is the one published run. The same
  operator ran the same harness lineage with Claude Fable 5, Opus 4.8 and two
  Opus 5 configurations between June and July 2026 and all failed partway, and no
  counters were published for any of them. Whether any earlier GPT-6 Astra
  attempt at this work unit exists is not recoverable from the released evidence.

The raised `sv_accelerate`, `sv_friction` and `sv_stopspeed` change the game's
physics rather than the agent's inputs, so `different_task` is arguable. It is not
used: the chambers, puzzles, quantity of work and completion criterion are
identical, the cvars are named concretely in `notes` as COLUMNS asks, and no other
game row carries that value for a harness-side change. The review left the call
open for Damon.

One weakness of the task itself, not a `comparison_issues` value: Portal is among
the most documented games in existence, so a run that completes it does not
demonstrate unfamiliar-game capability even with lookups disabled.

## Model record

New model `gpt-6-astra`. No GPT-6 Astra record exists in
`../AI Compute vs Human Time/dataset/models.csv`, checked 2026-09-13 across all
266 model rows.

**Release date 2026-09-03.** OpenAI's API changelog entry for that date reads
"Released GPT-6 Astra, our most capable model" and records availability in the
Chat Completions and Responses APIs
(`https://developers.openai.com/api/docs/changelog`, retrieved 2026-09-13). This
is public API availability, which is how the run reached the model; paid ChatGPT
plans followed on 2026-09-04, which Wikipedia's infobox calls the stable public
release against a 2026-09-03 limited preview. The changelog date is taken, which
follows the `gpt-5.4-2026-03-05` precedent of using the changelog entry, and both
dates are recorded in `models.csv` so the choice is visible rather than implied.
`https://openai.com/index/gpt-6-astra/` returns HTTP 403 to this environment and
was not read.

**300B active parameters, 6e11 FLOPs per processed position, `estimated`.**
Ruled by Damon on 2026-09-13 and recorded in
`research/model-priors/accepted-priors.csv`; it replaces the earlier flat 100B
frontier-scale transfer, which the prior review found rested on an Epoch prose
aside rather than an Epoch database entry, since Epoch publishes no parameter
estimate for any OpenAI model after GPT-4o.

The basis is inference economics plus a price ratio, set out in
`research/model-priors/openai.md` and `research/model-priors/pricing-crosscheck.md`.
Astra lists at $10/$50 per Mtok, 2.5x GPT-5.6 Sol, and is the slowest model in
OpenAI's lineup at 50–54 tok/s against GPT-5's 76; square-root shrinkage on the
price ratio is applied throughout because OpenAI has cut a reasoning model's price
80% on the same weights and because prices across hardware generations are
confounded. The pricing column's own central is 250B and equalizing Astra's markup
against OpenAI's own ladder gives 333B; the ruling sits between them. **100–600B is
the ruled sensitivity**, giving 1.58e18–9.47e18 FLOPs, 0.33x to 2.0x. This is a
grade C estimate: no disclosure, no leak, and no academic estimate exists, since
the factual-capacity probing paper predates Astra.

Astra is reported to use "recurrent depth" or looped transformers, a technique
that reuses the same layers for multiple passes, which would multiply a
parameter-only coefficient by the pass count. The report is a single anonymous
source and OpenAI has not confirmed it. It does not need a separate allowance
here: price per token and serial output speed both respond to total FLOPs per
emitted token, so the serving route that produced the 300B figure absorbs a loop
multiplier whether or not one exists. The two-pass and four-pass scenario rows
show what an explicit pass count would do to a parameter-only coefficient, not an
additional factor on top of the central value.

Reasoning effort is a task configuration rather than a separate weight identity,
following the existing `gpt-5` record, so the run's `max` effort is recorded in
`source_record` rather than in a separate model id.

## game-portal-gpt6astra

Values for the one point, with the derivations above.

| Field | Value |
|---|---|
| compute_flops | 4732678800000000000, written as an exact integer in the CSV; 4.7326788e18 |
| tokens | 5356638 |
| tokens_accounting | input_cache_creation_output |
| compute_method | operation_count |
| compute_evidence | derived_assumed_inputs |
| compute_statistic | total |
| compute_subset | all |
| ai_attempts | 1 |
| human_time | 11660 |
| human_skill | typical |
| human_time_statistic | mean |
| human_time_subset | successful |
| human_attempts | 8059 |
| human_time_method | other_calculation |
| human_time_evidence | task_timings |
| performance_vs_human | match |
| comparison_issues | different_inputs_or_tools; different_attempt_selection |

Ratio for orientation: 4.7327e18 FLOPs against 11,660 human seconds is
4.059e14 FLOPs per human second for this work unit. The ruled 100–600B
sensitivity spans 1.4e14 to 8.1e14, and including the omitted cached-context
attention would put the central at 5.9e14 to 8.2e14.

## Reproducing

```
git clone https://github.com/cozyblaze/portal-agent
git -C portal-agent checkout 31311b8fde8f242cc403bd51d45cb615ed645e4b
python3 research/portal-astra/scan_session.py \
    --session portal-agent/evidence/session.sanitized.jsonl \
    --out     agent-work/sources/portal-astra/session-scan.json
python3 research/portal-astra/compute_portal_astra.py \
    --summary agent-work/sources/portal-astra/summary.json \
    --scan    agent-work/sources/portal-astra/session-scan.json \
    --out     agent-work/derived/portal-astra/calculations.json
```

Both scripts take explicit input and output paths and write new outputs rather
than modifying the retained evidence. `scan_session.py` needs only the standard
library; it additionally records `o200k_base` counts when `tiktoken` is
importable, and those counts feed only the corroborating decomposition above.

## Not used

- The four earlier Portal runs on the same harness lineage (Claude Fable 5, Opus
  4.8, Opus 5 at 256k and 1M) published no usage counters, only video lengths and
  chamber progress, and the harness changed between them. They would be matched
  below-human companions on an identical work unit if the operator released the
  sessions.
- Press coverage of the run adds no counters beyond the repository and the
  overlay.
