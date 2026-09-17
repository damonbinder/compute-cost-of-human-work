# Pricing and throughput cross-check on the proposed active-parameter priors

*Created 2026-09-13 13:00.*

Scope: every closed model in either registry whose `active_parameters_basis` is `estimated`, plus
Claude Fable 5 and 5.1 as reference rows. 110 rows, machine-readable in `pricing-crosscheck.csv`.
Retained sources in `agent-work/sources/model-priors/pricing/`; arithmetic in `pricing/cost_model.py`
with its output in `pricing/calculations.txt`, and the CSV builder in `pricing/build_csv.py`.
Neither `models.csv` nor any of the three prior reports was touched.

## TL;DR

Pricing supports Damon's ordering but is much weaker on Fable than on Astra, and it is worthless at
the level. **The level fails by 11x to 47x**: a 100B-active model on GB300 NVL72 at FP4 costs
$0.03 per million input tokens and $0.17 per million output tokens to serve, against list prices of
$5 and $25 for Opus 5, and the gap is not margin—reconciling it against SemiAnalysis's reported 70%
Anthropic inference margin needs a further 11x to 47x of non-model cost. Only within-lab ratios at
one date carry anything. Those give **Astra at 2.50x GPT-5.6 Sol on every price component, at 0.90x
Sol's decode speed**, which is the one signature in the whole set that cannot be a serving-priority
premium: Anthropic's fast mode proves a 2x price step can buy 2.5x speed and zero parameters, and
Astra's step goes the other way. **Fable 5.1 is 2.0x Opus 5 on price and 1.00x on decode speed at
matched effort** (47-50 tok/s for both at low, medium, and high), which is exactly the fast-mode
signature, so the Fable premium is the weakest large price step in the set.

On the numbers: **200B for Astra is a central verging on a floor, not a ceiling**—the pricing
column's own central is 250B, and equalizing Astra's markup against OpenAI's own ladder gives 333B.
**150B for Fable 5.1 sits on the pricing column's central of 136B** and is well supported.
**150B for Sol is what pricing gives to two significant figures.** **100B for Opus 5 is what pricing
gives, because Anthropic has not moved the Opus price in nine months and five releases**, so the
route has no within-line resolution at all. The two proposals pricing actively contradicts are
Gemini 3.5 Flash at 40B, whose markup is 2.3x Google's ladder median, and Grok 4.20 at 70B, whose
markup is the lowest in the set at 21x. Cross-lab pricing also contradicts Gemini 3.1 Pro at 130B,
which is a reason to discard cross-lab pricing rather than the prior.

Next action: Damon rules on Astra. The pricing column would carry 250B central, 100-600B; it does
not object to 200B, and it does object to anything below about 150B.

---

## 1. What this column adds

The three prior reports each touched price and each backed away. The Anthropic report ruled route P
"not usable" and used it only as a weak ordinal signal above 2x. The OpenAI report used price with a
square-root shrinkage, justified by OpenAI's own 80% cut to o3 on fixed weights. The Google and xAI
report used within-ladder ratios only, and never at better than one significant figure.

All three were right to be cautious and none of them built the cost side. That is what is here: a
bottom-up serving-cost model, calibrated against measured throughput for open models whose active
parameter counts are known, so that "what would this model cost to serve" is a number rather than an
intuition. Three things fall out that none of the three reports could have:

- **The size of the gap between list price and marginal serving cost, and its spread.** The
  price-to-marginal-decode-cost multiple, evaluated at each model's own proposed prior, runs from
  21x to 244x across the set. That 11.7x spread is the noise floor of any price-based size
  inference, and it is larger than every size ratio anyone is arguing about.
- **A test that separates a size premium from a serving premium.** Price and decode speed respond to
  different things. A premium that buys speed is a serving tier. A premium that costs speed is
  either more parameters or more compute per token. Astra and Fable fall on opposite sides of this
  test, which is the single most useful result in this note.
- **A reason to prefer face-value price ratios to the square-root shrinkage.** Two biases run in
  opposite directions and roughly cancel. Flagships carry wider margins, which inflates price
  ratios. Fixed per-token costs that do not scale with active parameters—attention over a long KV
  cache above all—dilute the size signal, which means a given size ratio produces a *smaller* price
  ratio. Section 5 puts numbers on both.

### What this column cannot do

It cannot reach a level. It cannot compare across labs, because Anthropic's reported inference
margin is 70% with an API gross margin above 80% while OpenAI's reported consolidated gross margin
is 33%, and no OpenAI API-only figure is published. It cannot compare across years, because the
hardware moved roughly 2x per generation and the whole market repriced. And it cannot see inside a
price identity: Anthropic sells the same Opus 5 weights at $5/$25 and at $10/$50.

---

## 2. The economics

### The chip, and dollars per FLOP

The current serving generation for merchant inference is the Blackwell Ultra rack, GB300 NVL72.
SemiAnalysis's InferenceX publishes both the specification and a two-tier cost of ownership from its
AI Cloud TCO model, which is the right basis: a lab serving its own models pays something at or
below the hyperscaler tier, and nobody serving at scale pays the merchant on-demand rate, which
currently sits at a median $16.00 per GPU-hour for GB200 NVL72 against the TCO model's $1.86.

| Chip | FP4 dense TFLOP/s | FP8 dense TFLOP/s | Usable HBM GB | HBM TB/s | All-in kW | Hyperscaler USD/chip-hr | Retail USD/chip-hr |
|---|---|---|---|---|---|---|---|
| GB300 NVL72 | 15000 | 5000 | 278 | 8.0 | 2.12 | 2.31 | 5.00 |
| GB200 NVL72 | 10000 | 5000 | 186 | 8.0 | 1.87 | 1.86 | 4.00 |
| B300 | 13500 | 4500 | 268 | 8.0 | 1.90 | 2.26 | 4.25 |
| B200 | 9000 | 4500 | 180 | 8.0 | 1.71 | 1.73 | 3.70 |
| MI355X | 10066 | 5033 | 288 | 8.0 | 2.09 | 1.50 | 2.90 |
| H200 SXM | — | 1979 | 141 | 4.8 | 1.37 | 1.22 | 2.90 |
| TPU v7 Ironwood | — | 4614 | 192 | 7.37 | — | 1.60 | — |

The Ironwood row is the weakest: Google publishes no per-chip-hour price, and $1.60 is
SemiAnalysis's estimate of Anthropic's negotiated rate rather than a list price.

Dollars per FLOP at 100% utilization, hyperscaler tier:

| Chip and precision | USD per FLOP | Relative to GB300 FP4 |
|---|---|---|
| GB300 FP4 | 4.28e-20 | 1.00 |
| MI355X FP4 | 4.14e-20 | 0.97 |
| B300 FP4 | 4.65e-20 | 1.09 |
| GB200 FP4 | 5.17e-20 | 1.21 |
| B200 FP4 | 5.34e-20 | 1.25 |
| MI355X FP8 | 8.28e-20 | 1.94 |
| TPU v7 FP8 | 9.63e-20 | 2.25 |
| GB200 FP8 | 1.03e-19 | 2.42 |
| GB300 FP8 | 1.28e-19 | 3.00 |
| H200 FP8 | 1.71e-19 | 4.00 |

The FP4-to-FP8 spread is 2.2x to 3.0x on the same silicon, and the hyperscaler-to-retail spread is a
further 2.2x. Before any model assumption enters, a cost-per-token figure carries a 5x band from
precision and procurement alone. That band matters here because nobody knows what precision Claude
or GPT-6 is served at, and because Anthropic runs on three fleets at once.

### Utilization, prefill and decode separately

I calibrated utilization rather than assuming it, using InferenceX's TCO feed: output tokens per
second per chip on the measured throughput-versus-interactivity Pareto frontier, at a fixed
interactivity tier, for models whose active parameter counts are disclosed or Epoch-estimated. The
tier is 50 output tokens per second per user, which is where the frontier closed models actually
serve—Astra at 50-54, Opus 5 at 48-51, Fable 5.1 at 47-67.

On a workload of n input tokens per output token, FLOPs per output token are 2P(n+1). Writing a for
chip-seconds per input token and b for chip-seconds per output token, the 8192/1024 and 1024/1024
workloads give two equations in two unknowns, and separate prefill from decode.

| Model | Active B | Chip | tok/s/chip at 8:1 | Aggregate MFU at 8:1 | tok/s/chip at 1:1 | Prefill MFU | Decode FLOP utilization | Implied decode batch |
|---|---|---|---|---|---|---|---|---|
| DeepSeek-R1-0528 | 37 | GB300 | 4500 | 0.200 | 8710 | 0.322 | 0.050 | 33 |
| DeepSeek-R1-0528 | 37 | GB200 | 4208 | 0.280 | 9047 | 0.407 | 0.080 | 36 |
| DeepSeek-R1-0528 | 37 | B200 | 3135 | 0.232 | 7223 | 0.319 | 0.073 | 29 |
| DeepSeek-V4-Pro | 49 | GB300 | 5073 | 0.298 | 6479 | — | 0.044 | 30 |
| Kimi-K2.5 | 32 | GB300 | 2784 | 0.107 | 6647 | 0.143 | 0.035 | 24 |
| Kimi-K2.5 | 32 | GB200 | 2897 | 0.167 | 5713 | 0.263 | 0.043 | 19 |
| MiniMax-M3 | 22 | GB200 | 1092 | 0.043 | 1370 | 0.166 | 0.006 | 3 |
| MiniMax-M3 | 22 | B200 | 2200 | 0.097 | 2801 | 0.351 | 0.014 | 6 |
| gpt-oss-120b | 5.1 | GB200 | 11986 | 0.110 | 38420 | 0.124 | 0.057 | 26 |
| gpt-oss-120b | 5.1 | B200 | 5297 | 0.054 | 14725 | 0.066 | 0.022 | 9 |

The DeepSeek-V4-Pro prefill decomposition returns a physically impossible 1.07, which means its two
workloads came from differently-optimized configurations; its decode residual is still usable.
Across the nine admissible decompositions: prefill utilization median 0.26, range 0.07-0.41; decode
FLOP utilization median 0.043, range 0.006-0.080; implied concurrent decode batch median 24, range
3-36. I carry **0.30 prefill and 0.05 decode** as centrals, round numbers inside the calibrated
band. On the level, this puts DeepSeek-R1 at 37B active on GB300 at $0.14 per million output tokens
inclusive of eight million input tokens, which the next section checks against the one production
disclosure that exists.

### The one production disclosure that validates the calibration

DeepSeek published its actual V3/R1 serving economics on 2025-03-01, the only production figure of
this kind any lab has released. Over 24 hours: 226.75 nodes of eight H800s on average, costed at $2
per GPU-hour for $87,072 per day; 608B input tokens of which 56.3% hit the on-disk KV cache, and
168B output tokens; 73.7k input tokens per second per node in prefill and 14.8k output tokens per
second per node in decode. DeepSeek's own headline was a theoretical daily revenue of $562,027 at R1
list prices and a 545% cost-profit ratio.

| Quantity | DeepSeek disclosure, H800 at FP8, 37B active | This model, GB300 at FP4 |
|---|---|---|
| Blended USD per million tokens, 78:22 mix | 0.112 | 0.022 at 37B |
| Prefill utilization, cache hits excluded | 0.30 | 0.30 assumed |
| Decode FLOP utilization | 0.138 at roughly 20-25 tok/s/user | 0.05 at 50 tok/s/user |
| Implied concurrent decode batch | 29 | 24 median, 3-36 range |

The prefill number is the striking one. Stripping the 56.3% cache hits from the input stream leaves
266B tokens actually prefilled, which is 298 TFLOP/s per H800 against a 989 TFLOP/s dense FP8 peak,
or 30% utilization, the figure I chose independently from InferenceX. The decode figure is higher
than my 5% because DeepSeek serves at a lower interactivity target than the 50 tokens per second per
user the frontier closed models hold, and a lower target buys a bigger batch. The 5.1x cost gap is
the H800-to-GB300 hardware and precision step at a similar hourly rate.

The headline that matters for section 3: **DeepSeek's own disclosed compute cost is 15% of its own
list revenue, at the cheapest serious prices in the market.** A 6.5x markup over compute is the
industry floor, not its ceiling.

The low decode figure is not an error and it is the most important number in this section. A 100B
model at FP4 sharded eight ways would stream its weights fast enough for 900 output tokens per
second per user; the measured frontier rate is 50. The factor of 18 is attention over a long KV
cache, expert-routing all-to-all, and kernel overhead. Decode is not weight-streaming-bound in
production, which is a problem for the throughput route as well as this one.

### Cost per million tokens

GB300 NVL72, FP4, prefill 0.30, decode 0.05:

| Active parameters B | USD/Mtok input, hyperscaler | USD/Mtok output, hyperscaler | USD/Mtok input, retail | USD/Mtok output, retail |
|---|---|---|---|---|
| 20 | 0.0057 | 0.0342 | 0.0123 | 0.0741 |
| 40 | 0.0114 | 0.0684 | 0.0247 | 0.1481 |
| 100 | 0.0285 | 0.1711 | 0.0617 | 0.3704 |
| 150 | 0.0428 | 0.2567 | 0.0926 | 0.5556 |
| 200 | 0.0570 | 0.3422 | 0.1235 | 0.7407 |
| 300 | 0.0856 | 0.5133 | 0.1852 | 1.1111 |
| 600 | 0.1711 | 1.0267 | 0.3704 | 2.2222 |

The modeled output-to-input cost ratio is 6.0, the ratio of the two utilizations. Every lab prices
output at 5x to 8x input, so the *shape* of the price structure tracks the cost structure closely,
even though the level does not. Grok 4.20 at 2x and Grok 4.6 at 3x are the only exceptions in the
set, and they are xAI pricing decode below its cost share.

The one correction that does not scale with P is attention over the KV cache, and it runs against
the size signal. Decode attention FLOPs relative to 2P, for a 64-layer, 8-KV-head, 128-dimension
proxy:

| Active parameters B | 4k context | 32k | 128k | 1M |
|---|---|---|---|---|
| 40 | 1.01 | 1.11 | 1.43 | 4.28 |
| 100 | 1.01 | 1.04 | 1.17 | 2.31 |
| 200 | 1.00 | 1.02 | 1.09 | 1.66 |

Astra and Fable 5.1 both carry 1M-token context windows and both are sold for agentic work. In that
regime a large fraction of decode cost is context, not parameters, and the fraction is *larger* for
the smaller model. This is the dilution effect that makes face-value price ratios understate size
ratios, and it is why I do not apply the square-root shrinkage.

---

## 3. The level fails, and by how much

Implied P from list output price at an assumed gross margin, GB300 FP4, hyperscaler tier, decode
utilization 0.05. Implied P is exactly proportional to (1 - margin) and to the utilization
assumption, so the whole table is one number scaled two ways.

| Assumed margin | GPT-6 Astra, B | Claude Opus 5, B | Gemini 3.1 Pro, B |
|---|---|---|---|
| 0.50 | 14610 | 7305 | 3506 |
| 0.70 | 8766 | 4383 | 2104 |
| 0.90 | 2922 | 1461 | 701 |
| 0.99 | 292 | 146 | 70 |

Sensitivity to both assumptions at once, for Astra's $50 output price, in trillions of active
parameters:

| Decode FLOP utilization | Margin 0.50 | 0.70 | 0.90 | 0.99 |
|---|---|---|---|---|
| 0.02 | 5.84 | 3.51 | 1.17 | 0.12 |
| 0.05 | 14.61 | 8.77 | 2.92 | 0.29 |
| 0.10 | 29.22 | 17.53 | 5.84 | 0.58 |
| 0.20 | 58.44 | 35.06 | 11.69 | 1.17 |

Only the bottom-left corner touches a credible number, and that corner is a 99% margin over marginal
decode cost. Read the other way: for Astra's $50 output price to be consistent with a 200B active
model on GB300 at FP4, the effective margin over marginal decode cost has to be 98.5% at the retail
TCO tier and 99.3% at the hyperscaler tier. Those are price-to-cost multiples of 68x and 146x.

That is not a claim that the labs earn 99% margins. It is a measurement of everything in a served
token that is not the model's active parameters: fleet duty cycle well below a benchmark's,
provisioning for peak, long-context attention and KV residency, free and consumer tiers, safety
classifiers and other side models, retries, and research amortization. Anchoring on SemiAnalysis's
reported 70% Anthropic inference margin, which is defined as revenue minus the compute cost of
serving that inference, Opus 5 at Artificial Analysis's 7:2:1 cache-input-output blend prices at
$3.85 per million tokens and therefore costs $1.16 to serve. The same blend on the model above
costs $0.025 to $0.054 at 100B and $0.050 to $0.107 at 200B. **The non-model wedge is 11x to 47x**,
and it has to be common between two models before their price ratio means anything about their
sizes.

### Markup at each model's own proposed prior

The useful version of the same calculation. M is list output price divided by modeled marginal
decode cost, evaluated at the prior each of the three reports proposes.

| Model | Proposed active B | USD/Mtok in | USD/Mtok out | Modeled cost out | M output | Output:input price |
|---|---|---|---|---|---|---|
| Claude Opus 4.1 | 180 | 15.00 | 75.00 | 0.3080 | 244 | 5.0 |
| Claude Fable 5.1 | 150 | 10.00 | 50.00 | 0.2567 | 195 | 5.0 |
| Claude Fable 5 | 150 | 10.00 | 50.00 | 0.2567 | 195 | 5.0 |
| GPT-5.5 | 100 | 5.00 | 30.00 | 0.1711 | 175 | 6.0 |
| GPT-6 Astra | 200 | 10.00 | 50.00 | 0.3422 | 146 | 5.0 |
| Claude Opus 5 | 100 | 5.00 | 25.00 | 0.1711 | 146 | 5.0 |
| Gemini 3.5 Flash | 40 | 1.50 | 9.00 | 0.0684 | 131 | 6.0 |
| GPT-5.4 | 100 | 2.50 | 15.00 | 0.1711 | 88 | 6.0 |
| GPT-5.6 Luna | 8 | 0.20 | 1.20 | 0.0137 | 88 | 6.0 |
| Claude Sonnet 4.6 | 100 | 3.00 | 15.00 | 0.1711 | 88 | 5.0 |
| GPT-5.6 Sol | 150 | 4.00 | 20.00 | 0.2567 | 78 | 5.0 |
| Claude Haiku 4.5 | 40 | 1.00 | 5.00 | 0.0684 | 73 | 5.0 |
| GPT-5 | 100 | 1.25 | 10.00 | 0.1711 | 58 | 8.0 |
| Gemini 2.5 Pro | 100 | 1.25 | 10.00 | 0.1711 | 58 | 8.0 |
| Gemini 3.1 Pro | 130 | 2.00 | 12.00 | 0.2224 | 54 | 6.0 |
| Gemini 3.1 Flash-Lite | 20 | 0.25 | 1.50 | 0.0342 | 44 | 6.0 |
| Grok 4 | 200 | 3.00 | 15.00 | 0.3422 | 44 | 5.0 |
| GPT-5 nano | 8 | 0.05 | 0.40 | 0.0137 | 29 | 8.0 |
| Grok 4.20 | 70 | 1.25 | 2.50 | 0.1198 | 21 | 2.0 |

Median 88, range 21-244, spread 11.7x. Within-lab medians: Anthropic 195, OpenAI 88, Google 58,
xAI 44. Anthropic's ladder carries 2.2x OpenAI's markup at the priors the two reports propose, and
4.4x xAI's. Either Anthropic's models are systematically larger than proposed, or its margins are
wider. The reported margins say the second, and say it loudly: Anthropic's API gross margin above
80% against OpenAI's consolidated 33%. **Cross-lab price comparison is therefore biased toward
overstating Anthropic sizes by something like a factor of two, and the same logic understates
Google's and xAI's.**

---

## 4. Three price moves that bound what a price step can mean

Before reading any ratio, note what each lab has demonstrated it will do to a price with the weights
held fixed.

- **OpenAI cut o3 by 80% on 2025-06-10**, stating "We optimized our inference stack that serves o3.
  Same exact model—just cheaper". A 5x step, no weight change, no hardware generation change.
- **Anthropic sells Opus 5 and Opus 4.8 in fast mode at $10/$50 against $5/$25 standard**, exactly
  2x, for output at "roughly 2.5x normal speed". Same weights, same date, same fleet. The previous
  generation's fast tier was $30/$150, so the fast price fell 3x while the standard price did not
  move.
- **Anthropic cut Fable cache reads 4x at the 5.0-to-5.1 point release**, from $1.00 to $0.25 per
  million, a 0.10x multiplier to 0.025x, while leaving base input at $10 and output at $50. Every
  other Claude model still uses 0.10x.

The second of these is the binding one for this exercise. **Anthropic's own price list contains a 2x
step that provably buys no parameters, and the Fable 5.1 versus Opus 5 step is exactly 2x.** Price
alone cannot establish that Fable is larger than Opus, because a 2x Anthropic price step with a
speed increase attached is precisely what the fast tier is. The 2.5x Astra versus Sol step is
likewise inside the 5x that OpenAI has demonstrated is non-model.

---

## 5. The relative read

### Within-lab ratios at one date

All rows are current list prices retrieved 2026-09-13. Blend is the Artificial Analysis 7:2:1
cache-input-output weighting, which is the closest thing to a realized mix.

| Pair | Input | Output | Cached input | Blended | sqrt | ^1.5 |
|---|---|---|---|---|---|---|
| GPT-6 Astra / GPT-5.6 Sol | 2.50 | 2.50 | 2.50 | 2.50 | 1.58 | 3.95 |
| GPT-6 Astra / GPT-5.5 | 2.00 | 1.67 | 2.00 | 1.77 | 1.33 | 2.36 |
| GPT-6 Astra / GPT-5 | 8.00 | 5.00 | 8.00 | 5.76 | 2.40 | 13.81 |
| GPT-5.6 Sol / GPT-5 | 3.20 | 2.00 | 3.20 | 2.30 | 1.52 | 3.49 |
| GPT-5.5 / GPT-5 | 4.00 | 3.00 | 4.00 | 3.25 | 1.80 | 5.87 |
| Claude Fable 5.1 / Claude Opus 5 | 2.00 | 2.00 | 0.50 | 1.86 | 1.37 | 2.54 |
| Claude Opus 5 / Claude Sonnet 5 | 2.50 | 2.50 | 2.50 | 2.50 | 1.58 | 3.95 |
| Claude Sonnet 5 / Claude Haiku 4.5 | 2.00 | 2.00 | 2.00 | 2.00 | 1.41 | 2.83 |
| Claude Opus 4.1 / Claude Opus 5 | 3.00 | 3.00 | 3.00 | 3.00 | 1.73 | 5.20 |
| Gemini 3.1 Pro / Gemini 3.5 Flash | 1.33 | 1.33 | 1.33 | 1.33 | 1.15 | 1.54 |
| Gemini 3.1 Pro / Gemini 3.1 Flash-Lite | 8.00 | 8.00 | 8.00 | 8.00 | 2.83 | 22.63 |
| Gemini 3.1 Pro / Gemini 2.5 Pro | 1.60 | 1.20 | 1.60 | 1.30 | 1.14 | 1.48 |
| Grok 4 / Grok 4.6 | 1.50 | 2.50 | — | 1.71 | 1.31 | 2.24 |

Three structural facts about these ladders are worth recording before any inference.

Anthropic's output-to-input ratio is exactly 5.0 on every model from Haiku 3.5 to Fable 5.1, across
four years and three architectures. It is a convention and it carries zero information. OpenAI's
moved from 8.0 at GPT-5 to 6.0 at GPT-5.4 and 5.5, to 5.0 at Sol and Astra, which is consistent with
prefill becoming a larger share of cost as context windows went to 1M, and is far too coarse to
detect anything else. Google runs 6.0 to 8.3 and xAI runs 2.0 to 3.0.

Cached-input multiples are 0.10x almost everywhere. OpenAI moved from 0.25x at o3 and GPT-4.1 to
0.10x from GPT-5 onward. Anthropic is 0.10x everywhere except Fable 5.1 and Mythos 5.1 at 0.025x.
Google is 0.10x throughout. That uniformity means the cached column adds nothing to the ratios
except in the one Fable case, where it runs the other way.

Anthropic has held Opus at $5/$25 through Opus 4.5, 4.6, 4.7, 4.8, and 5—nine months and a hardware
generation. The Opus line has no within-line price signal at all.

### Reading a price ratio as a size ratio

Two biases, opposite in sign and comparable in size.

**Margin premium inflates the ratio.** A flagship at an 80% margin against a mid-tier at 60% inflates
the price ratio by (1-0.60)/(1-0.80) = 2.0 with no size difference whatsoever. The measured
within-lab markup spread supports premia of this order: Anthropic's ladder runs 73x to 244x, a 3.3x
range, and OpenAI's runs 29x to 175x, a 6.0x range.

**Fixed per-token cost deflates the ratio.** If a fraction f of per-token cost scales with active
parameters and the rest does not, a size ratio r produces a price ratio of f·r + (1-f). Inverting,
the implied size ratio is (price ratio - 1 + f)/f. At the 1M contexts Astra and Fable are sold for,
the attention table above puts f nearer 0.4 to 0.6 than 1.0, and at f = 0.5 a 2.5x price ratio
implies a 4.0x size ratio.

These cancel to within their own uncertainty, which is why I take the **face-value blended price
ratio as the central**, sqrt as the low reading, and ^1.5 as the high reading. This differs from the
OpenAI report, which applies sqrt shrinkage as its central on the strength of the o3 repricing. The
o3 event bounds the *level*, not the *ratio*; it says price contains 5x of non-model, not that price
ratios are square-rooted. Where the two methods disagree most is exactly on Astra, and the OpenAI
report's 200B is the more conservative number of the two.

| Comparison | Blended price ratio | sqrt reading | Face value | ^1.5 reading |
|---|---|---|---|---|
| Astra vs Sol, on a 100B Sol | 2.50 | 158 | 250 | 395 |
| Astra vs Sol, on a 150B Sol | 2.50 | 237 | 375 | 593 |
| Astra vs GPT-5, on a 100B GPT-5 | 5.76 | 240 | 576 | 1381 |
| Fable 5.1 vs Opus 5, on a 100B Opus 5 | 1.86 | 137 | 186 | 254 |

The Astra-versus-GPT-5 row is the cross-year comparison and should be discounted for the roughly 2x
per hardware generation that separates August 2025 from September 2026; that takes the face-value
576B to about 290B.

---

## 6. Price against throughput, which is where the discrimination is

Price and decode speed respond to different physical quantities. Input price tracks prefill, which
is compute-bound and linear in FLOPs per token. Decode speed tracks bytes streamed per token and the
attention work over the KV cache. A model with more active parameters is both more expensive and
slower. A model given serving priority is more expensive and faster. **The sign of the speed
difference separates the two, and it is the only clean discriminator in this whole exercise.**

Matched-effort decode speed, Artificial Analysis, retrieved 2026-09-13:

| Effort | GPT-6 Astra | GPT-5.6 Sol | Claude Fable 5.1 | Claude Opus 5 |
|---|---|---|---|---|
| low | 51 | — | 47 | 48 |
| medium | 50 | — | 50 | 48 |
| high | 50 | — | 49 | 50 |
| xhigh | 51 | — | 60 | 51 |
| max | 54 | 60 | 67 | 51 |

Astra is 0.90x Sol at the only effort level where both are measured, and it is the slowest model in
OpenAI's lineup at every effort level: 50-54 against GPT-5's 76, GPT-5.5's 85, and GPT-5.4's 132.
Fable 5.1 and Opus 5 are within 4% of each other at low, medium, and high, and Fable pulls ahead
only at xhigh and max, where the max row is measured "with fallback".

So:

- **Astra: 2.50x the price, 0.90x the speed.** Paying more and getting less. That is not a serving
  premium. It is more parameters, more passes over the same parameters, or a longer effective
  context, and the price and speed data cannot separate those three. It is, however, exactly the
  signature you would expect of a costlier model per token.
- **Fable 5.1: 2.00x the price, 1.00x the speed at matched effort.** Paying more and getting the
  same, trending to faster at high effort. Anthropic advertises the speed as an engineering result:
  "Fable-level intelligence, Opus-level price, Sonnet-speed. In our tests it was about twice as fast
  as Opus 5 and used half as many tokens." Combined with the fast tier, which sells exactly 2x price
  for 2.5x speed on fixed weights, the Fable premium has an available explanation that requires no
  extra parameters at all.

The bracket that follows: the speed ratio is the low reading on the size ratio and the price ratio
is the high reading, since serving optimization biases speed up and margin biases price up.

| Comparison | Speed ratio reading | Price ratio reading | Geometric central | Applied to the anchor |
|---|---|---|---|---|
| Astra vs Sol | 1.11 | 2.50 | 1.67 | 250B on a 150B Sol; 167B on a 100B Sol |
| Astra vs GPT-5 | 1.41 | 5.76 hardware-deflated to 2.88 | 2.01 | 201B on a 100B GPT-5 |
| Fable 5.1 vs Opus 5 | 1.00 | 1.86 | 1.36 | 136B on a 100B Opus 5 |
| Sol vs GPT-5 | 1.27 | 2.30 | 1.71 | 171B on a 100B GPT-5 |
| Opus 5 vs Opus 4.5 | 0.87 | 1.00 | 0.93 | 93B on a 100B Opus 4.5 |

The one number in the set I would defend hardest is the Sol row, because two independent signals
agree in direction and within 1.8x of each other, and because the OpenAI report reached 150B by a
different route.

### Two further observations that belong to this column

**Token consumption per task runs the other way from price.** On Artificial Analysis's intelligence
index, Fable 5.1 emits 78k output tokens per task including 47k reasoning tokens, against Astra's
27k and 17k. At an identical $50 per million output tokens, Fable costs 2.9x as much to run a task
as Astra does. If the labs price to a target cost per task rather than per token, then Fable's
per-token price is *low* for its verbosity and Astra's is high, which pushes Astra's implied size up
and Fable's down. This is speculative and I would not weight it, but it runs in the same direction
as everything else in this section.

**Fable 5.1's 0.025x cache-read multiplier is a cost statement, not a size statement.** Anthropic
cut one price component 4x on its most expensive model without touching the others. A cache read
skips the prefill compute entirely and pays only KV residency and attention. Charging 2.5% of base
input for it says the marginal cost of a cache read is far below $0.25 per million tokens, which is
consistent with everything in section 2 and tells you nothing about P. It is worth recording because
it is the newest pricing datum in the set and it will be tempting to read as evidence of something.

---

## 7. Across labs

Astra and Fable 5.1 are priced identically to the dollar: $10 input, $50 output, 1M context. They
differ only in the cache-read multiple, 0.10x against 0.025x, which puts Astra 7% above Fable on the
7:2:1 blend. On the Artificial Analysis intelligence index they both score 53.

Under an equal-margin assumption that would make them the same size. The margin evidence says the
assumption is wrong in a known direction: Anthropic's reported API gross margin is above 80% and its
inference margin 70%, while OpenAI's reported consolidated gross margin is 33%, dragged down by a
free consumer tier that does not enter the API price. The two numbers are not like-for-like and no
OpenAI API-only figure exists, so this cannot be quantified. The direction is clear: **at equal
price, the higher-margin seller is serving the cheaper model, so Fable 5.1 is at or below Astra in
active parameters, not above.** That matters because Damon's framing groups them together.

The rest of the cross-lab picture is not usable and it is worth saying why in one place.
Gemini 3.1 Pro at $2/$12 is a fifth of Astra on input; read cross-lab that would put Google's
flagship at 40-80B against the proposed 130B. Google serves on TPUs it builds itself, at an internal
cost no merchant buyer pays, and Ironwood has no public price. Grok 4 at $3/$15 carries the lowest
markup of any flagship, 44x at 200B, and xAI's newer models price decode at 2x to 3x input where
everyone else runs 5x to 8x. Neither of those is a size signal. They are a vertically integrated
incumbent and a share-taking challenger.

---

## 8. Verdict on the four models

### GPT-6 Astra: 200B is a central verging on a floor, not a ceiling

Pricing's own central is 250B, which is the face-value price ratio on a 100B Sol and the
price-and-speed geometric central on the proposed 150B Sol. The bracket itself runs 111-250B on a
100B Sol and 167-375B on a 150B Sol. Markup-equalization against OpenAI's own ladder gives 333B.
Only the square-root reading lands at or below 200B, at 158-237B. Nothing in the pricing column argues for
less than about 150B, and several lines argue for more.

Two things keep me from pushing the central above 200B. Astra is the one model in the set where a
non-parameter explanation for a high price is independently reported: The Information's
recurrent-depth claim, if true, raises FLOPs per token without raising parameters, and prefill price
responds to FLOPs. And the 2.5x step sits inside the 5x that OpenAI demonstrated on o3 is not model.

**Carry 200B central, 100-600B**, noting that the pricing column alone would carry 250B. I would
reject a proposal below 150B on this evidence.

### Claude Fable 5.1: 150B is well supported and is the pricing column's own central

Price-and-speed bracket 100-186B, geometric central 136B. Face-value price ratio 186B. Fable sits
exactly at the median markup of Anthropic's own ladder at 150B, so the proposal is internally
consistent with how Anthropic prices everything else. What it does not do is establish that Fable is
larger than Opus: the 2x price step is the same size as the fast-mode step that provably buys no
parameters, and the decode speeds are identical at matched effort. So 150B is the right central and
the low end of the range needs to reach down to Opus's own number.

**Carry 150B central, 70-350B.** Fable 5 takes the same figure. The pricing column does not
distinguish Fable 5 from 5.1 at all; the only change was the cache-read multiple.

### GPT-5.6 Sol: 150B is what pricing gives

Blended price 2.30x GPT-5 across eleven months, deflated for hardware to about 1.5x, and a decode
speed 1.27x slower. Both routes agree, the geometric central is 171B, and the proposed 150B is
inside it. This is the best-supported of the four and the only one where the pricing column and the
OpenAI report reached a similar number by different routes.

**Carry 150B central, 70-350B.**

### Claude Opus 5: 100B, and pricing has no resolution to offer

$5/$25 unchanged across five Opus releases and nine months, so no within-line signal exists. The
cross-tier signals fit 100B only loosely: Opus 5 is 2.5x Sonnet 5 on price, and the registry carries
Sonnet 4.6 at the same 100B as Opus, which a 2.5x price ratio does not fit. The Sonnet leg is
contaminated, because Sonnet 5 cut the price 33% from $3/$15, announced the cut as introductory
through 2026-08-31, then made it permanent, so I do not read the mismatch as evidence about Opus. Against Opus 4.5, price
identical and speed 1.15x faster, which reads as flat to slightly smaller.

The one real Opus price signal in the record is the 3x cut from Opus 4.1's $15/$75 to Opus 4.5's
$5/$25, which happened over 2.4 months while Anthropic's inference margin was rising from 38% to
70%. A price cut at a rising margin is a cost cut, and 3x over 2.4 months is more than hardware
delivers. That supports the registry's 180B-to-100B step for Opus 4/4.1 and arguably supports a
larger one.

**Carry 100B central, 45-260B, unchanged.**

---

## 9. Where pricing supports, contradicts, or cannot discriminate

Per-row verdicts are in `pricing-crosscheck.csv`, where every one of the 110 rows carries a
`pricing_evidence` verdict and a `notes` justification. The summary:

**Supports the proposal:** GPT-5.6 Sol at 150B, GPT-5.6 Luna at 8B, GPT-5.4 at 100B, GPT-5 mini at
20B, GPT-5 at 100B as the anchor, Claude Fable 5 and 5.1 at 150B, Claude Opus 5 and the whole
Opus 4.5-and-later line at 100B, Claude Opus 4 and 4.1 at 180B, and Gemini 2.5 Pro and 3.1 Pro at
100B and 130B read within Google's own ladder.

**Supports but points higher:** GPT-6 Astra, where the column's central is 250B against the proposed
200B.

**Weakly supports a proposed change:** Claude Haiku 4.5 from 20B to 40B, on a price one third of
Sonnet 4.5's, which at face value is 33B on a 100B Sonnet. Claude Haiku 3.5 from 20B to 30B, on the
4x launch step over Haiku 3, cut 20% within five weeks. Gemini 2.5 Flash from 40B to 25B, on Google
pricing input at $0.30 against DeepSeek's own $0.27 for a disclosed 37B-active model, which bounds
Google's cost below DeepSeek's price. In all three cases pricing is agreeing with an argument the
prior reports already made rather than adding a new line.

**Contradicts:** Gemini 3.5 Flash at 40B, whose 131x markup is 2.3x Google's ladder median and the
highest non-Pro figure in Google's set. Google's own cross-generation pricing says Flash is priced
on capability, so the contradiction is probably about margin rather than size, but it should be
recorded. Grok 4.20 at 70B, whose 21x markup is the lowest in the entire set and whose 2:1
output-to-input ratio is unique; a naive read gives 15-30B and should be discarded.

**Cannot discriminate:** nine identities with a current price, and every identity without one.
Among the priced: Claude Sonnet 4 and 4.5, because the Sonnet price was flat for three releases and
then cut with the cut announced as introductory; o3 and GPT-4.1, both at $2/$8 after the repricing
that proves the route's own weakness; GPT-5 nano, whose 29x markup is the lowest at OpenAI and is
equally consistent with a sub-8B model and with share pricing; Gemini 3.1 Flash-Lite; and Grok 4.
Among the unpriced: 74 of the 110 rows carry no current first-party list price, including every
GPT-4, GPT-4o, GPT-3.5, Claude 2 and 3, Gemini 1.x and 2.0, and Grok 2 and 3 row. For 33 of those a
launch or delisted price is retained in the CSV, but cross-era ratios are confounded by roughly 2x
per hardware generation and by the 2024-2026 repricing, so none of them is used. Every cross-lab
comparison is in this category too.

## 10. What would settle this

In rough order of value. A published inference gross margin per model tier, from any lab, which
would convert every ratio in section 5 into a size ratio directly. A same-date, same-model
measurement of standard-mode against fast-mode decode speed on Opus 5, which would measure the
serving-policy confound instead of bounding it at 2.5x. A statement of which fleet serves which
endpoint, which would remove the 5x precision-and-procurement band from section 2. An InferenceX
benchmark of a frontier open model at 1M context, which would pin the attention dilution term f that
decides between the sqrt and the face-value reading. And confirmation or denial of Astra's recurrent
depth, which is the only live hypothesis under which a 2.5x price step and a 0.90x speed step do not
mean more parameters.

Retained sources and provenance: `agent-work/sources/model-priors/pricing/`. Arithmetic:
`pricing/cost_model.py`, output in `pricing/calculations.txt`. CSV builder: `pricing/build_csv.py`.
