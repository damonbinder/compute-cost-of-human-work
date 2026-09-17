# GPT-6 Astra completing the Factorio base game

*Created 2026-09-13 10:03.*
*Last revised 2026-09-13 13:35, re-running the inversion at the ruled 300B GPT-6 Astra prior. Change log in `candidates/factorio-astra/REVISION.md`.*

## Summary

One GPT-6 Astra run driven through Codex `/goal` by the operator Mira played the
Factorio base game with enemies enabled from a fresh map to the rocket launch,
finishing on 11 September 2026. The victory dialog in the posted screenshot reads
**Time played: 43:40:46**, or 157,246 in-game seconds; the operator's `/goal`
clock reads 4 days 11 hours, a lower bound of 385,200 wall-clock seconds. Astra
planned; a GPT-5.6 Luna worker at medium effort executed scripts as a subagent.

**No token counters, logs or replay have been published.** The only compute
evidence is the operator's statement that "At API pricing, logs indicate it
would've cost about $4500". This row therefore inverts a dollar figure, which
Damon has ruled acceptable provided the conversion is explicit. The conversion
runs through OpenAI's list prices at the run date and the structure of the one
contemporaneous run of the same model that did publish counters, the cozyblaze
Portal run, whose own cost reconstruction reproduces its overlay's $571.33
estimate to 0.5%.

**Two quantities can be carried across from that donor, and they disagree by a
factor of 2.2.** Transferring its dollars per billed unit—equivalently its
cache-read amplification **α = 50.80**—gives 3.7305e19 FLOPs. Transferring its
mean cached prefix and its 25.58 seconds per call instead, and letting α fall out
at **13.64**, gives 8.1592e19. Both are defensible transfers of the same donor.
**The central is their geometric mean, 5.5170e19 FLOPs at α = 28.63**, reported
as the inversion at that single α so tokens, positions and FLOPs stay consistent.
Following the accepted Portal row, the donor's 36.19% image share of billed units
is carried too, so `tokens` is the **120,493,163 text-token** remainder and the
56,936,361 image patch positions are charged in `compute_flops`.

The human unit is the same completion: HowLongToBeat's Factorio main-story mean
of **201,181 seconds over 279 polled completions**. Both sides meet the game's
own victory condition, so the comparison is `match`.

Four things move the number, in descending order.

1. **Which donor quantity is transferred.** The structural range is
   **3.7e19 to 8.2e19**, and the central is the geometric mean of its two ends,
   not a point estimate with error bars. The α sweep is the same axis seen
   another way: α = 25 gives 5.99e19 and α = 100 gives 2.17e19.
2. **The 300B active-parameter prior is not an OpenAI disclosure.** The ruled
   100–600B range moves the result to 1.93e19–1.09e20.
3. **Cached-context attention is one-sided upward.** At this run's prefix
   lengths this note's own scenario puts it at **4.58e19 to 2.05e20** on top of
   the parameter-only value, quantified in [Compute scenarios](#compute-scenarios);
   `research/attention-correction.md` has since folded the term into
   `compute_flops`.
4. **The Astra/Luna cost split is a judgment.** It barely registers now: Luna is
   roughly 48 times cheaper per billed unit and 37.5 times smaller per token, so
   a 0–10% cost share moves total FLOPs only −1% to +2%, even though it moves the
   token count by a factor of six.

## Shared evidence

Everything below comes from `agent-work/sources/factorio-astra/`, whose `MANIFEST.md` lists
each file, its URL and its retrieval time. The tweets were read through
`api.fxtwitter.com`, the images pulled from `pbs.twimg.com` at `name=orig` and
read directly here rather than through anyone's description.

### The run and its work unit

The brief, from the opening post of 6 September
(`https://x.com/_Mira___Mira_/status/2096713682818630027`), was: "Pick any seed
you want, and the deliverable is a replay file that launches the rocket in the
base game". The operator adds that she "only gave the initial /goal and 1
instruction to 'use Luna medium for the worker for speed/efficiency'".

The completion post of 11 September
(`https://x.com/_Mira___Mira_/status/2098343807410712814`, 460,163 views) reads
in full: "GPT-6 Astra has just beaten a standard game of Factorio with enemies
enabled after nearly 44 hours in-game time, and 4 days 11 hours on his Codex
/goal clock. At API pricing, logs indicate it would've cost about $4500. It could
probably be 50x cheaper by offloading more to Luna and providing some standard
scripts for common tasks. My next test might be Astra coaching Muse Spark or Qwen
3.8 27B into solving a random seed, now that we have successful logs to review."

The attached screenshot, retained as
`victory-screenshot-2098343807410712814.jpg` and read here, is Factorio's
victory dialog: title **Victory!**, **Time played: 43:40:46**, body
"Congratulations! You have beaten the game by launching a rocket into space!",
buttons Finish / Save replay / Credits / Continue. The debug overlay behind it
reads `Resolution: 1280X800`, `Entities Total: 133730, Active: 5892`, and the
alert panel reads "Rocket silo finished". The window title is "Remote view".
43:40:46 is 157,246 seconds.

So the work unit is **one base-game Factorio playthrough from a fresh map to the
rocket launch, with enemies enabled**, including all intermediate design work,
failures and retries. This is the game's own win condition and its own completion
dialog; there is no ambiguity about what "beaten" means here. The human unit is
one player finishing Factorio's main story, whose only formal win condition is
the same rocket launch.

Two qualifications on the map. The brief let the agent pick its own seed, and
Factorio's map-generator settings beyond the seed are not recorded anywhere in
the published evidence; "a standard game with enemies enabled" is the operator's
description, not a settings dump. And the client is a 2.x build (the quality
icons, the remote view and the 2.0 UI are visible in every screenshot), whereas
HowLongToBeat's Factorio entry dates from the 1.0 release. The rocket-launch
completion criterion is unchanged across those versions.

### The wall clock is a lower bound

The `/goal` clock of "4 days 11 hours" is the operator's only statement about
elapsed time, and two things about it are worth stating rather than assuming
away.

- The opening post is timestamped **2026-09-06 21:34:31Z** and the completion
  post **2026-09-11 09:32:03Z**. That interval is 4 days 11 hours 57 minutes 32
  seconds. The operator's figure is indistinguishable from the gap between her
  own two posts.
- The opening post's screenshots already show the run well under way. Read
  directly: `setup-04` is a four-drill coal outpost with `Engine` research at
  93%, and `setup-01` is a belted base with science labs running, chemical
  plants and `Logistics 2` in progress, which is several in-game hours later.
  The post text says the agent had already designed blueprints and rushed
  construction robots.

So **385,200 seconds is a lower bound on the agent's wall clock**, not a
measurement of it. Astra's release on 2026-09-03 caps the elapsed time at about
725,000 seconds. This cuts in the row's favor: every implied call cadence below
is also a lower bound, so the gap against the donor's 25.58 seconds per call is
smaller than the raw figures suggest.

### What the operator published, and what she did not

Published: the victory screenshot, four mid-run screenshots from 6 September, one
page of the agent's own run notes from 9 September, the two clock figures, and
the $4,500 cost statement. Zvi Mowshowitz's 12 September post repeats the same
figures from the same tweet and adds nothing independent.

Not published, as of 13 September 2026: any token counter, any per-model split,
any call count, the logs (the operator says "we have successful logs to review",
so they exist privately), and the promised YouTube replay video. I checked for a
follow-up and found none.

### The harness

From the opening post: the agent "works by pausing the game, loading the save on
a 'disposable' headless client, using Lua to test his designs, writes scripts to
issue the inputs, and then unpauses, uses a subagent to run the scripts, takes
screenshots to check for misplaced belts or inserters". It "designed a bunch of
blueprints using scripts, and he rushed to construction robots in the live game
so he can import and place them". The operator notes it is "not playing in
realtime", so the game is frozen while the agent thinks.

The four setup screenshots corroborate this. One shows Factorio's **Import
string** dialog open with a long base64 blueprint blob pasted into it; one shows
a blueprint ghost labeled "Original 24 furnace ore smelter"; one shows an early
coal outpost; one shows a belted mid-game base with biters walking in the open,
which is the only direct visual evidence that enemies were enabled. All four
carry the same `Resolution: 1280X800` debug overlay.

The agent's own notes page
(`https://x.com/_Mira___Mira_/status/2097676806732370049`, retained as
`astra-notes-2097676806732370049.png` and read here) is a wall of compressed
shorthand with four visible timestamps on 9 September at 12:45Z, 12:49Z, 13:00Z
and 13:11Z. What it establishes about the harness, rather than about Factorio:
artifacts are written to a `.runtime/` directory as `.lua`, `.json` and `.jpg`
files, numbered into the fifties by the third day; the worker is addressed by
name and can fail ("Luna twiceBadRequest beforeusefulstatus"); ownership of the
screenshot channel is handed between root and worker ("ownership explicitly
handed native_image_guide; no rootnative while worker active"); some steps
explicitly involve no image ("No image/native involved"); and the agent tracks
blueprint SHA hashes, tick numbers and production rates in text. It is
corroboration that the run was long and real. It is not compute evidence, and I
have not tried to turn its four timestamps into a call rate.

## Compute

The arithmetic is reproduced by
`research/factorio-astra/compute_factorio_astra.py`, whose output is retained at
`agent-work/derived/factorio-astra/calculations.json`. Model records and their parameter
priors are in [Model records](#model-records).

### Prices at the run date

From the two first-party OpenAI model pages, retrieved 13 September 2026 and
transcribed into `agent-work/sources/factorio-astra/openai-list-prices-2026-09-13.json`.
USD per million text tokens.

| Model | Input | Cached input | Cache write | Output |
|---|---:|---:|---:|---:|
| gpt-6-astra | 10.00 | 1.00 | 12.50 | 50.00 |
| gpt-5.6-luna | 0.20 | 0.02 | 0.25 | 1.20 |

Both pages add that prompts above 272K input tokens are billed at 2x the input
and cache rates and 1.5x output for the whole request, that Fast mode is 2x the
applicable rates, and that cache writes are 1.25x the uncached input rate.
Neither price changed between the run and the retrieval: the API changelog
records Astra's release on 3 September and Luna's last price change on 30 July,
when Luna fell 80% to these rates. Three of the four Astra figures and three of
the four Luna figures are printed on the pages; **Luna's $0.25 cache write is
derived from the 1.25x rule rather than transcribed**, and the retained file now
says so. It is unused, because cache creation is held at zero.

### Why the cost has to be inverted, and how

Billing units and FLOPs are different quantities, and the dataset says so
plainly: billing units are not direct task FLOP measurements, and a proxy has to
justify its conversion. Here the conversion is exact in one direction—the
operator's $4,500 is a linear function of four token counts—and the problem is
that four unknowns cannot be recovered from one number without structure.

The structure comes from the dataset's own billed-unit convention. Under COLUMNS
`params_tokens`, known cache reads are removed from the parameter-multiplication
term and fresh input, cache creation and output are retained. Write:

- `B` = billed units = fresh input + cache creation + output, the quantity the
  row actually needs;
- `α` = cache-read tokens per billed unit;
- `β` = output share of billed units.

Then, with cache creation at zero (see below), cost in dollars per million billed
units is

```
price_per_million_billed = α * P_cached + (1 - β) * P_input + β * P_output
```

and `B = cost / price_per_million_billed * 1e6`. Substituting Astra's prices,
`price = α + 8.096 + 9.521 = α + 17.617`. β matters an order of magnitude less
than α: at α = 28.6, moving β from 0.19 to 0.05 or to 0.40 changes the price per
billed unit by −12% and +19%, against the factor of 3.7 that α spans across the
range considered here.

α has a physical reading: it is the mean cached prefix divided by the mean number
of newly processed tokens per call, roughly `context_length / tokens_per_turn`.
An agent that re-reads a 128,000-token prefix to add 2,500 new tokens has α ≈ 51.

### Calibrating on the Portal run

The one contemporaneous run that published counters is the cozyblaze Portal
agent: the same model, eleven days earlier, also driven through Codex, also a
long-horizon game agent taking screenshots. Its `evidence/summary.json` is
retained at `agent-work/sources/portal-astra/summary.json` and is an input to this script,
as is the accepted row's `agent-work/derived/portal-astra/calculations.json` for the image
split.

```
input 433,210,793  (cached 426,415,104)   cache write 0   output 1,598,341
fresh input = 433,210,793 - 426,415,104 = 6,795,689
billed units = 6,795,689 + 0 + 1,598,341 = 8,394,030
α = 426,415,104 / 8,394,030 = 50.7998
β =   1,598,341 / 8,394,030 =  0.190414
```

**The reconstruction checks out against an independent figure.** Pricing those
four counters at the list rates above gives $574.29. The livestream overlay at
completion displayed `EST. API COST $571.33`, at a session clock of 23:38:19
against a final 23:42:34—a slightly earlier snapshot, and 0.52% lower. That
agreement is worth more than it looks: it confirms the list prices, confirms that
OpenAI reports cached tokens inside the input counter rather than beside it, and
confirms that automatic caching in the Responses API carries no separate
cache-write charge. Cache creation is therefore held at zero for Factorio too.
Explicit prompt-caching controls shipped with GPT-5.6 and would produce
cache-write charges at $12.50; if this harness used them, the true α is lower
than the one used here and the token total higher.

Per call, using the overlay's 3,337 tool calls: mean prefix 129,820 tokens, of
which 127,784 cached; 2,036 fresh input and 479 output; 2,515 billed units;
25.578 seconds of wall clock.

### Two transfers, not one

The first submission carried α across and stopped there. That is one of two
defensible transfers of this donor, and it is the lower one.

**The mean prefix is better founded than α.** A thread that grows to a window cap
and compacts back to a floor has a mean prefix of `(floor + cap) / 2`, which
depends on the window and the compaction policy and not on the turn size or the
call count. The donor fits that model coherently: its measured mean prefix of
129,820 against the overlay's 258,400-token Codex window implies a
post-compaction floor of 1,241 tokens, and its 8,394,030 units of new content
then imply 8,394,030 / 257,159 = 32.6 compaction cycles over 3,337 calls, about
one per 102 calls. Both runs are Codex `/goal` threads driving the same model, so
the ~128,000-token cached prefix is a well-founded quantity to carry across. α is
`prefix / turn size` and inherits every uncertainty in the turn size, which is
exactly the thing that differs between a Portal turn and a Factorio turn.

So the second transfer holds the donor's cached prefix and its seconds per call,
and lets α fall out. At the lower-bound wall clock of 385,200 seconds and the
donor's 25.578 seconds per call, the Astra budget of $4,410 buys 15,060 calls at
$0.2928 each. Of that, 127,784 cached tokens cost $0.1278, leaving $0.1650 for
new content at `0.8096 * 10 + 0.1904 * 50 = 17.617` dollars per million, so
**9,369 billed units per call** and **α = 127,784 / 9,369 = 13.64**.

| Branch | α | Astra billed units | FLOPs | Seconds per Astra call |
|---|---:|---:|---:|---:|
| Cost transfer (donor $/billed unit) | 50.80 | 6.446e7 | 3.7305e19 | ≥15.0 |
| **Central (geometric mean)** | **28.63** | **9.536e7** | **5.5170e19** | **≥18.0** |
| Cadence transfer (donor prefix and s/call) | 13.64 | 1.411e8 | 8.1592e19 | 25.58 by construction |

**Both run-specific arguments push the same way, up.** A Factorio turn plausibly
carries more text than a Portal turn—Lua scripts, entity dumps, blueprint
strings and a growing notes file against Portal's screenshot and position
readout—which lowers α and raises the total. And the Factorio loop unpauses the
game and waits for scripts to execute in real time, which lengthens the per-call
wall clock; at a pinned prefix a longer call means fewer calls, more dollars per
call, and therefore a *larger* turn and a *lower* α, which also raises the total.
The first submission said this second argument pointed to higher α. That was
wrong: it only does so if the mean prefix is allowed to rise with the call
length, and the mean prefix is the one quantity the shared window pins.

There is a real argument on the other side. The donor ran at
`reasoning_effort = max` and this run's effort is not stated, so a faster cadence
is expected if the effort was lower, and the operator's one instruction optimized
for "speed/efficiency". A 20-second cadence at the lower-bound wall clock gives
α = 22.3 and 6.3993e19, still above the cost branch. That argument supports the
cost branch; it does not make the cost branch the middle of the band, which is
why the central moved.

### The Astra and Luna split

The worker's share of the $4,500 is not published, and nothing in the evidence
bounds it. The operator's "It could probably be 50x cheaper by offloading more to
Luna and providing some standard scripts for common tasks" does not: at the 2%
share used here a full swap to Luna gives 24.9x, not 50x, so read as a bound the
sentence would imply Luna ≈ 0% and the central would violate it. The sentence is
also half about reducing total work through a script library rather than
reallocating it.

**The central gives Luna 2% of the cost, $90, with a 0–10% range. This is a
judgment.** It is deliberately not zero, because a worker that executes every
script and reports back is not free. An order-of-magnitude sanity check supports
it: a worker invoked about once per Astra call on a short context, at roughly
$0.39 per million billed units, would consume tens of millions of units for tens
of dollars, which is the same order as $90.

What matters is that this choice is nearly irrelevant to the FLOP total while
being decisive for the token total, and the 300B ruling widened that gap. At the
central α, Luna costs $0.963 per million billed units against Astra's $46.25, so
$90 buys it 93,457,442 units—about as many as Astra gets for $4,410. But Luna's
coefficient is 1.6e10 FLOPs per token against Astra's 6e11, so those tokens
contribute 2.5% of total FLOPs, down from 7.3% at the old prior. Across the 0–10%
range the token count moves by a factor of six while total FLOPs move −1% to +2%.
A reader who cares about FLOPs can ignore the split; a reader who quotes the
`tokens` field cannot.

Luna's own α is assumed equal to Astra's, which treats the worker as a similarly
structured growing thread. A short-context worker at α = 10 would buy more Luna
tokens for the same money and raise the total 2%.

### Images

Following the accepted `game-portal-gpt6astra` row, the donor's image share of
billed units is transferred alongside its cache structure rather than left
undifferentiated. The donor's numbers, from `agent-work/derived/portal-astra/calculations.json`:
3,037,392 billable image units out of 8,394,030 billed units is a **36.185%
image share**, and 2,531,160 patch positions against those billable units is
**0.8333 positions per billable unit**, the reciprocal of the 1.2 billing
multiplier. So each billed unit carries

```
backbone positions per billed unit = 0.63815 + 0.36185 * 0.83333 = 0.93969
```

and `tokens` is the 63.815% text remainder. At the central that is
**120,493,163 text tokens** and **56,936,361 image patch positions**, and
`compute_flops` multiplies each model's positions by its own coefficient. At the
cost-transfer α the same arithmetic gives Astra 2.33e7 billable image units,
4.11e7 text tokens and 1.94e7 patch positions, which reproduces the review's
figures.

This run's own screenshots are 1280x800, not the donor's mostly 1280x720:
`ceil(1280/32) * ceil(800/32) = 40 * 25 = 1,000` patches and, at the 1.2
multiplier, 1,200 billable units each.

**The transferred share is probably too high, and the note should say so.** The
donor's image share is large precisely because its text turns were small—one
screenshot and a position readout per call against 2,515 billed units. A Factorio
turn carrying Lua scripts and entity dumps has more text per screenshot. Read
literally, 36.185% of the central's 188,816,796 billed units is 68.3 million
billable image units, or 56,936 screenshots at 1,200 each: one every 6.8 seconds
of the lower-bound wall clock, against the donor's one per 26.2 seconds. That is
a strain. The direction is benign and bounded: a lower image share raises both
the text count and the position count, and the limit at zero image share is the
`No image share separated` scenario at 1.06 times the central. The share is
transferred anyway because consistency with the accepted Portal row is the
default and the whole effect is 6%.

The alternative of separating images out of Astra's units only, leaving the
worker's as text, is priced as a scenario: 5.5260e19 FLOPs, within 0.2% of the
central, with 154,325,000 text tokens. The uniform treatment is used because the
agent's own notes show the screenshot channel being handed between root and
worker rather than held by either.

### Result

```
central α = 28.6296
Astra: $4,410 / 46.2461 per million  =  95,359,354 billed units
Luna:  $   90 /  0.9630 per million  =  93,457,442 billed units
total billed units                   = 188,816,796
tokens (text)      = 0.63815 * 188,816,796 = 120,493,163
patch positions    = 0.30154 * 188,816,796 =  56,936,361
Astra positions    = 0.93969 * 95,359,354  =  89,608,367
Luna  positions    = 0.93969 * 93,457,442  =  87,821,156
compute_flops = 89,608,367 * 6e11 + 87,821,156 * 1.6e10
              = 5.37650e19 + 1.40514e18
              = 5.517015877342947e19
```

`compute_method` is `operation_count`, and `tokens_accounting` is
`input_cache_creation_output`, both following the accepted Portal row: the
multiplied position count is not the CSV `tokens` field, because text tokens
exclude the image workload, which is charged separately. The first submission
used `params_tokens` and `source_total`; the review was right that there is no
source total to speak of, since the operator published no counter and the
quantity is constructed here to exactly the
`fresh input + cache creation + output` definition.

`compute_evidence` is `derived_assumed_inputs`: the workload magnitude is set by
this run's own logged spend, and only the mix that converts it is assumed. It is
not `transferred_workload`, which COLUMNS reserves for a workload borrowed from
another task or a collection average; the $4,500 belongs to this work unit, and
COLUMNS routes "estimating this task's workload from its own quantities or
constraints" to `derived_assumed_inputs`. The donor here is external—a
different game, harness and operator—which is a weaker relationship than the
`collection-work/DECISIONS.md` precedent for response-length calibration inside
one benchmark, and the classification rests on the $4,500 being this run's own
quantity rather than on that precedent.

### Turn-structure cross-check

Pick a mean prefix and a mean number of newly processed tokens per call; the cost
of one call follows, hence a call count, hence billed units and an implied
cadence against the donor's 25.578 seconds. The wall clock in the last column is
the lower-bound 385,200 seconds, so every cadence figure is a lower bound.

| Mean prefix | Billed units per call | Implied α | Post-compaction floor | Astra calls | Seconds per call |
|---:|---:|---:|---:|---:|---:|
| 129,820 | 2,515 | 50.8 | 1,241 | 25,625 | ≥15.0 |
| 129,820 | 5,000 | 25.2 | 1,241 | 20,621 | ≥18.7 |
| 129,820 | 9,368 | 13.1 | 1,241 | 15,352 | ≥25.1 |
| 200,000 | 2,515 | 78.7 | 141,600 | 18,202 | ≥21.2 |
| 200,000 | 5,000 | 39.2 | 141,600 | 15,526 | ≥24.8 |
| 200,000 | 9,368 | 20.5 | 141,600 | 12,338 | ≥31.2 |

The first submission's grid also carried a 258,400-token mean prefix. Those cells
are dropped: 258,400 is the window, and a mean equal to the cap is unattainable
for any thread that compacts. The 200,000 rows are kept but are weak for the same
reason—they need a post-compaction floor of 141,600 tokens against the donor's
implied 1,241—and no claim is made that the central sits in the middle of a
band built on them. Restricted to the measured prefix, the central's 4,463 billed
units per call and ≥18.0 seconds per call sit between the two transfers, which is
what the geometric mean is.

**The cross-check does discriminate one thing.** The largest unpriced risk in the
inversion is that the operator's "$4,500 at API pricing" charged cache reads at
the full $10 input rate rather than the $1 cached rate, which is a common way to
compute a cost from a token log. That reading gives $525.61 per million billed
units, 8.39 million Astra units and **4.8588e18 FLOPs, 11 times below the
central**. It is rejected cleanly: 8.39 million units at the donor's turn size is
3,335 calls, or **115.5 seconds per call**, which no agent loop of this kind runs
at, and the lower-bound wall clock only makes that worse. The wording points the
same way—"At API pricing ... it would've cost" reads as a token count
multiplied by list prices, which is the inverse of what this row computes.

### Compute scenarios

One-at-a-time, all judgmental rather than confidence intervals. Retained in
`agent-work/derived/factorio-astra/calculations.json`.

| Scenario | Text tokens | FLOPs | Ratio to central |
|---|---:|---:|---:|
| Central, α = 28.63 | 1.205e8 | 5.5170e19 | 1.00 |
| Cost transfer, α = 50.80 | 8.197e7 | 3.7305e19 | 0.68 |
| Cadence transfer, 385,200 s wall clock, α = 13.64 | 1.766e8 | 8.1592e19 | 1.48 |
| Cadence transfer, 430,000 s wall clock | 1.611e8 | 7.4254e19 | 1.35 |
| Cadence transfer, 470,000 s wall clock | 1.472e8 | 6.7702e19 | 1.23 |
| Cadence transfer, 518,400 s wall clock | 1.303e8 | 5.9771e19 | 1.08 |
| Cadence transfer at 20 s per call | 1.394e8 | 6.3993e19 | 1.16 |
| α = 25 | 1.305e8 | 5.9864e19 | 1.09 |
| α = 100 | 4.795e7 | 2.1706e19 | 0.39 |
| α = 200 | 2.601e7 | 1.1734e19 | 0.21 |
| α = 0, no prompt caching at all | 3.069e8 | 1.4461e20 | 2.62 |
| Luna cost share 0% | 6.210e7 | 5.4862e19 | 0.99 |
| Luna cost share 10% | 3.541e8 | 5.6402e19 | 1.02 |
| Luna worker on short contexts, α_Luna = 10 | 1.581e8 | 5.6057e19 | 1.02 |
| Astra 100B active | 1.205e8 | 1.9327e19 | 0.35 |
| Astra 600B active | 1.205e8 | 1.0894e20 | 1.97 |
| Luna 3B active | 1.205e8 | 5.4292e19 | 0.98 |
| Luna 24B active | 1.205e8 | 5.7980e19 | 1.05 |
| Long-context tier on every request | 6.378e7 | 2.9088e19 | 0.53 |
| Fast mode throughout | 6.025e7 | 2.7585e19 | 0.50 |
| Recurrent depth, two passes per token | 1.205e8 | 1.0894e20 | 1.97 |
| Recurrent depth, four passes per token | 1.205e8 | 2.1647e20 | 3.92 |
| No image share separated | 1.205e8 | 5.8711e19 | 1.06 |
| Image share on Astra's units only | 1.543e8 | 5.5260e19 | 1.00 |
| Operator priced cache reads at the input rate | 1.080e7 | 4.8588e18 | 0.09 |
| Arithmetic ceiling, every dollar on fresh input | 2.872e8 | 2.5372e20 | 4.60 |

Notes on the bounding rows. **α = 0** is the no-caching case: every prefix token
charged fresh, so the billed total is everything the model saw. **Fast mode** and
**long-context** are the two price-tier risks in the same direction: both model
pages price Fast mode at 2x the applicable rates, and the accepted Portal note
records that the donor session switched into Fast mode partway, so a run that
used it bought half as many tokens per dollar. Neither touches α, which comes
from counters. **The arithmetic ceiling** spends the whole $4,500 on fresh input
at $10 per million with no cache reads and no output at all; it is not physical,
but nothing at standard-tier prices can exceed 450,000,000 billed units, so
2.54e20 FLOPs is a hard cap on this row under the 300B prior.

**A plain statement of the range.** On the structural-transfer axis—which donor
quantity is carried across—the row runs from **3.7e19 to 8.2e19**, and the
central is the geometric mean of those two ends. The active-parameter prior is a
separate axis: the ruled 100–600B range multiplies by 0.35 to 1.97, giving
**1.9e19 to 1.1e20** overall. The price-tier risks (Fast mode, long context) take
roughly half off; the hard floor under the discriminated naive-pricing reading is
4.9e18 and the hard ceiling is 2.5e20.

### Cached-context attention

Per `collection-work/DECISIONS.md`, `compute_flops` stays on the dataset-wide
`2 * active_parameters` convention, which prices projection and feedforward
matrices and nothing else. For a run that appends essentially every position
after a six-figure prefix, that omission is large and one-sided: it can only
understate.

Attention FLOPs per appended position are `4 * layers * d_model *
context_positions`, counting the QK and attention-value products at two
operations per multiply-add. This is the recipe `dataset/research/ruler/ruler.md`
uses and that `research/portal-astra.md` reproduced against it. Applied to
Astra's 89,608,367 appended positions at the central:

| Assumed shape | Dense-equivalent parameters | 4·L·d | Prefix 130,000 | Prefix 258,400 |
|---|---:|---:|---:|---:|
| L=80, d=12288 | 145B | 3.93e6 | 4.581e19 (0.83x) | 9.105e19 (1.65x) |
| L=96, d=16384 | 309B | 6.29e6 | 7.329e19 (1.33x) | 1.457e20 (2.64x) |
| L=120, d=18432 | 489B | 8.85e6 | 1.031e20 (1.87x) | 2.049e20 (3.71x) |

The layer counts and widths are not free: each is checked against the standard
block's `12 * layers * d_model^2` dense-equivalent parameter count, and the three
bracket the ruled 300B active prior at 145B, 309B and 489B. The shapes moved with
the prior at this revision; Astra's architecture is not disclosed. A full
operation count including cached-context attention would land at roughly
**1.0e20 to 2.6e20**—1.8x to 4.7x the parameter-only value, and larger than every
other scenario except the arithmetic ceiling. Luna's attention is left out; at
nano scale over a worker's shorter contexts it is a percent-level term inside a
term that is already only 2.5% of the total.

## Human baseline

HowLongToBeat's Factorio page (`https://howlongtobeat.com/game/17455`, retrieved
2026-09-13), parsed from the page's embedded `__NEXT_DATA__` rather than its
rounded display strings. The whole payload is retained alongside the extracted
fields.

| Statistic | Seconds | Polled |
|---|---:|---:|
| Main story, average | 201181 | 279 |
| Main story, median | 180000 | 279 |
| Main story, HowLongToBeat headline | 190591 | 279 |
| Main story, rushed | 109696 | 279 |
| Main story, leisure | 461806 | 279 |
| Main + extras, average | 368138 | 117 |
| Completionist, average | 899560 | 47 |
| All styles, average | 319370 | 443 |

**Value used: 201,181 seconds, the arithmetic mean of 279 main-story
completions.** COLUMNS prefers the arithmetic mean where the source offers one,
so the mean is used rather than the 180,000-second median or the 190,591-second
headline. The same field choice was made for the Portal row, so the two are
comparable.

- `human_skill` is `typical`. HowLongToBeat's submitters are self-selected people
  who play and log games. They are not selected for skill at Factorio, and they
  are not novices at games in general.
- `human_time_scope` is `task_performance` and `human_time_evidence` is
  `task_timings`: recorded timings for the stated task and population,
  aggregated by the source.
- `human_time_method` is `other_calculation`. The source averaged raw
  observations, which is arithmetic on recorded timings rather than a
  judgment-based estimate. `reported` is reserved for a single recorded timing
  taken directly in seconds.
- `human_time_subset` is `successful` with `human_attempts` 279. Main-story times
  come only from players who finished. This is a selection rule, not a human
  success rate: the same page lists 1,806 users who completed the game against
  613 who retired it.

Limitations worth stating, and this baseline is weaker than Portal's.

- The sample is 279, not Portal's 8,059, and Factorio's times are self-reported
  for a game that runs tens of hours, so recall is coarse.
- Factorio has no story campaign in the 2.x base game, so "Main Story" is what
  each submitter took it to mean. The game's only formal win condition is the
  rocket launch, and the victory dialog says so, which is the reason to treat the
  two criteria as the same. But some submissions may time something else, and
  HowLongToBeat does not publish the raw entries, so the mean cannot be
  recomputed or filtered. The CSV `performance_evidence` no longer asserts that
  every submission meets the same criterion.
- The HowLongToBeat entry is dated to the 1.0 release of 2020 and covers the 2.x
  base game under the same id, without separating versions. Factorio: Space Age
  is a separate entry (id 153222, headline main story 495,523 seconds over 27
  polled submissions) and is not used.
- The page counts 339 replays, and whether a replay can add a second main-story
  entry is not documented, so 279 is the source's polled count rather than a
  verified count of distinct players.

### Alternative human populations

Scenarios, not hedges in the CSV. speedrun.com leaderboards retrieved 2026-09-13
and retained.

| Population | Seconds | Basis |
|---|---:|---|
| Typical player, main story, mean | 201181 | HowLongToBeat, n=279 (the value used) |
| Typical player, main story, median | 180000 | HowLongToBeat, n=279 |
| Self-described speedrunners | 33016 | HowLongToBeat speedrun style, mean, n=11 |
| World class, Default Settings world record | 7141 | speedrun.com run yvk04e8m, 2026-08-22 |
| World class, Any% world record | 4736 | speedrun.com run z1945rwm, 2024-06-18 |
| World class, 100% world record | 15174 | speedrun.com run ywx2nr0m, 2024-10-20 |

A `world_class` row against the 7,141-second Default Settings record would be a
different point, not a correction to this one. A single record holder is not a
timing sample; speedrun.com times real elapsed time, not the in-game clock, which
is the wrong axis for an agent that plays with the game paused; the category
rules allow only blueprints created during the run and forbid importing them,
where this run built by pasting strings it had generated on a separate client;
and Default Settings additionally requires a random map, which a chosen seed
would not satisfy.

## Performance and comparison

`performance_vs_human` is `match`. The agent met the game's own victory
condition, and the human times are completions of the same game whose only formal
win condition is that rocket launch. Nothing in the evidence grades the two on a
quality scale beyond finishing. What the source does not supply is each
submitter's own criterion, since HowLongToBeat publishes no raw entries for game
17455; the CSV says that rather than claiming otherwise.

The two AI clocks are context, not the comparison axis.

- **In-game 157,246 seconds**, read from the victory dialog's Time played field.
  That is 0.78 times the human mean, but the game is frozen while the agent
  thinks, so its in-game timer excludes exactly the deliberation the human figure
  includes. Calling the run faster than a typical player on this basis would be
  an artifact of the harness.
- **Wall clock at least 385,200 seconds** on the `/goal` thread, at least 1.9
  times the human mean. This is the operator's stated figure, which coincides
  with the interval between her two posts while the earlier post already showed a
  mid-game base.

`comparison_issues`:

- `different_inputs_or_tools`. The agent pauses the game to think, loads the save
  on a separate headless client to test designs in Lua, writes scripts that issue
  input actions programmatically, imports blueprint strings it generated
  offline, and delegates execution to a second model. A human plays in real time
  with mouse and keyboard, builds by hand, and cannot fork the world to test a
  design. The planning and puzzle component of Factorio is intact for the agent;
  the manual execution component is largely removed.
- `different_attempt_selection`. The human times are polled only from players who
  completed and submitted; the AI figure is the one published run. Whether any
  earlier failed GPT-6 Astra attempt at this work unit exists is not recoverable
  from the released evidence.

I considered `different_task` and did not use it. The map generator settings are
the agent's own choice and are unverified, but so are every HowLongToBeat
submitter's, and the quantity of work and completion criterion are identical.
The unverified settings are named in `notes` instead.

One weakness of the task itself, not a `comparison_issues` value: Factorio is
extensively documented, with wikis, blueprint libraries and ratio calculators in
the training data, and the brief did not disable web search. Nothing in the
evidence establishes whether the agent looked anything up.

## Model records

### gpt-6-astra

**Reused unchanged, and now at the ruled prior.** The row is copied
byte-for-byte from this folder's accepted `models.csv`, so it cannot drift from
the registry: release date 2026-09-03 from the OpenAI API changelog, **300B
active parameters and 6e11 FLOPs per token**, basis `estimated`.

The first submission used the shared 100B frontier-scale prior. Damon's
parameter-prior ruling of 2026-09-13, recorded in
`collection-work/DECISIONS.md`, replaced it with **300B active, sensitivity
100–600B**, on the pricing cross-check in `research/model-priors/`, whose own
central is 250B and whose markup-equalizing figure against OpenAI's own ladder is
333B. It is a judgment, not an OpenAI disclosure, and it remains grade C. The
row's dependent quantities were recomputed by rerunning the retained script, not
by scaling the published value, and the attention shapes below moved with it.
Astra is reported to use recurrent-depth or looped-transformer decoding, which
would multiply the per-token coefficient by an undisclosed number of passes.

### gpt-5-6-luna

New record. No GPT-5.6 Luna row exists in
`../AI Compute vs Human Time/dataset/models.csv`, checked across all 266 rows,
or in this folder's `models.csv`; `gpt-5-6-sol` does exist in the dataset, and
this id follows its spelling.

**Release date 2026-07-09.** The OpenAI API changelog's 9 July entry reads
"Released the GPT-5.6 model family, including GPT-5.6 Sol for frontier
capability, GPT-5.6 Terra for a balance of intelligence and cost, and GPT-5.6
Luna for efficient, high-volume workloads", with availability in the Responses,
Chat Completions and Batch APIs. The existing `gpt-5-6-sol` record carries the
same date from the launch page rather than the changelog; both are cited here.

**8B active parameters, 1.6e10 FLOPs per token, `estimated`, unchanged by the
2026-09-13 ruling.** OpenAI discloses
no architecture, but its own model page says Luna "roughly corresponds to the
nano model tier used in earlier GPT-5 families". That first-party positioning
statement is what makes this a documented prior rather than a price-based guess:
it names the tier, and the dataset already has a nano-tier prior. `gpt-5-nano`,
`gpt-4.1-nano-2025-04-14`, `gpt-4o-mini-2024-07-18` and `gemini-1.5-flash-8b-001`
all carry 8e9 active parameters, traced in
`dataset/research/epoch/epoch-small-models.md` to the named Ministral 8B and
Llama 3 8B comparators. That note's scenario range for the nano prior is 3–24B,
which is carried here.

**The tier statement establishes the tier, not the size, and the anchor is two
generations old.** Ministral 8B and Llama 3 8B date from 2024; tier names persist
across generations while the models behind them move. Luna carries a
1,050,000-token context, a 128,000-token maximum output and reasoning effort up
to `max`, none of which a 2024 8B model offered. The 3–24B scenario covers this
and Luna is 7.3% of the total, so nothing numerical turns on it, but the prior
should not be read as an 8B measurement of Luna.

Two things are deliberately not used. Luna's price is not evidence of its
size—$0.20 per million input tokens happens to equal GPT-5.4 nano's rate, but a
price ratio is a business decision, and the dataset's rule is that billing units
do not establish FLOPs. And the naming change from mini/nano to Sol/Terra/Luna is
not treated as a size claim; the tier statement on the model page is.

Reasoning effort is a task configuration rather than a separate weight identity,
following the existing `gpt-5` and `gpt-6-astra` records, so the run's "Luna
medium" is recorded in `source_record` rather than in a separate model id.

## game-factorio-gpt6astra

Checked against the union of 1,485 point ids across the dataset's 1,410, this
folder's 10 accepted rows and the eight candidate batches; no Factorio row
exists, and the `game-<game>-<model>` form follows `game-portal-gpt6astra` and
`game-pokemon-crystal-gemini3pro-red`.

| Field | Value |
|---|---|
| compute_flops | 5.517015877342947e+19 |
| tokens | 120493162.62828633 |
| tokens_accounting | input_cache_creation_output |
| compute_method | operation_count |
| compute_evidence | derived_assumed_inputs |
| compute_statistic | total |
| compute_subset | all |
| ai_attempts | 1 |
| human_time | 201181 |
| human_skill | typical |
| human_time_statistic | mean |
| human_time_subset | successful |
| human_attempts | 279 |
| human_time_method | other_calculation |
| human_time_evidence | task_timings |
| performance_vs_human | match |
| comparison_issues | different_inputs_or_tools; different_attempt_selection |

The CSV text fields are held at or under the longest value the production dataset
already contains for each one—585 of 586 for `notes`, 553 of 560 for
`task_description`, 333 of 337 for `performance_evidence`, 434 of 455 for
`source_record`, 187 of 220 for `compute_source`, and 364 of 365 for the
`gpt-5-6-luna` model note. They carry only the qualifications needed to read the
row: cost-inverted compute with its two transfer branches and stated range, the
transferred image share, the harness difference, and the wall clock as a lower
bound. Everything else is here, and `research/factorio-astra/build_rows.py`
enforces the caps at write time.

Ratio for orientation: 5.5170e19 FLOPs against 201,181 human seconds is
2.742e14 FLOPs per human second for this work unit. The two branches give
1.854e14 and 4.056e14, and the accepted Portal row at the same ruled prior gives
4.059e14—so the cadence transfer puts Factorio level with Portal per human
second, to three significant figures, and the cost transfer puts it at half. That
is an observation about two runs of one model in similar harnesses, not evidence
for either branch, but it is the kind of consistency a reader will look for.
Including the cached-context attention term, as `research/attention-correction.md`
now does, puts this row at 5.0e14 to 1.3e15.

## Reproducing

```
python3 research/factorio-astra/compute_factorio_astra.py \
    --portal-summary      agent-work/sources/portal-astra/summary.json \
    --portal-calculations agent-work/derived/portal-astra/calculations.json \
    --prices              agent-work/sources/factorio-astra/openai-list-prices-2026-09-13.json \
    --hltb                agent-work/sources/factorio-astra/howlongtobeat-factorio-17455.json \
    --out                 agent-work/derived/factorio-astra/calculations.json

python3 research/factorio-astra/build_rows.py \
    --calculations    agent-work/derived/factorio-astra/calculations.json \
    --points-header   points.csv \
    --models-header   models.csv \
    --astra-model-row models.csv \
    --out-points      candidates/factorio-astra/points.csv \
    --out-models      candidates/factorio-astra/models.csv
```

Standard library only. Both scripts take explicit input and output paths, read
only retained evidence files and the accepted Portal row's own calculations, and
write new outputs rather than modifying any of them. The judgment inputs—the
Luna cost share, the wall-clock scenarios, the α sweep and the attention
shapes—are named constants at the top of `compute_factorio_astra.py`.
`build_rows.py` takes every numeric CSV field from `calculations.json`, so the
row cannot drift from the arithmetic; it copies the shared `gpt-6-astra` model
row byte-for-byte from this folder's accepted `models.csv` and refuses to write
unless that row's active-parameter count matches the one the calculations
actually used, so a prior change cannot land in one file and not the other. It
also refuses to write if any text field exceeds the dataset maximum, or if a
cited `research/` or `agent-work/sources/` path is followed directly by punctuation that
validate.py would capture as part of the path.

## Not used

- **The three other Astra Factorio runs.** Daniel Vestøl's Space Age run was at
  its third planet on 9 September with no completion post by 13 September;
  `psihius` reports a Space Age rocket launch and two colonized planets on
  Hacker News with the game unfinished; Derya Unutmaz instructed Astra to play
  for fifteen minutes and it stopped there. None is a completed work unit and
  none has any compute evidence. **There is no second completed Astra Factorio
  run to document.**
- **The agent's notes timestamps.** Four entries over 26 minutes on one day is
  not a call rate, and converting it into one would manufacture the call count
  the row is missing.
- **Ryan Madden's 2025 Claude Code Factorio attempts**, which reached green
  science with no rocket and published no counters, and Anthropic's Fable 5
  launch-post Factorio demo, which states no completion criterion and no result.
- **The Factorio Learning Environment benchmark**, which is a different work unit
  and belongs to a separate collection.
