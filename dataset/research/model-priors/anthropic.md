# Anthropic model priors — active parameters and FLOPs per token

*Created 2026-09-13 11:52.*

## TL;DR

Anthropic has never disclosed a parameter count, layer count, hidden dimension, expert count, or
even a dense/MoE classification for any Claude model, in any model card, system card, announcement,
or interpretability paper. Epoch's database leaves `Parameters` empty on all eighteen of its Claude
rows. So every number below is grade B or C; there is no grade A anywhere in this provider.

The registry's current priors are mostly right, and I recommend keeping 100B active for the whole
Sonnet line and the whole Opus 4.5-and-later line. Four records should change. **Claude 3 Opus 180B
to 300B**, because its current value is transferred backwards from Opus 4/4.1 across two hardware
eras and a precision change, in the wrong direction, and two independent routes put it at 240-370B.
**Claude Haiku 4.5 20B to 40B**, because its 20B is inherited from a 2024 guess about Haiku 3 and
the measured throughput puts it at 47-53B under the same calibration that gives Opus 100B.
**Claude 3.5 Haiku 20B to 30B**, on Anthropic's own 4x price increase "to reflect its increase in
intelligence". **The internal FLT research model 100B to 150B**, because its stated anchor is Fable
5.1, which is a tier above Opus rather than an Opus-class model.

The Opus 4/4.1 180B, which the Codex build derived from throughput and memory bandwidth, survives,
but only just, and I downgrade it from a model-specific measurement to a weak signal. The reason is
in the methods section: Anthropic sells a "fast mode" that runs the same named model at 2.5x normal
speed, which means per-user throughput is a product tier, not a hardware limit, and the method's
honest error bar is a factor of 2.5 rather than the source's stated 50%.

## Methods, and what each route is worth

### Route T: decode throughput against effective memory bandwidth

In memory-bound batched decoding, one decoding step reads the active weights once and emits one
token for every sequence in the batch, so per-user throughput is roughly
`bandwidth / (bytes_per_active_param x active_params)`. Invert it and you get active parameters from
a throughput measurement, given a bandwidth and a precision.

This is the only model-specific quantitative route that exists for Claude, and it is the basis of
the registry's Opus numbers. The original is
[unexcitedneurons (2026)](https://unexcitedneurons.substack.com/p/estimating-the-size-of-claude-opus),
published 2026-03-12, which calibrates effective bandwidth at 4.0-4.5 TB/s by running the same
inversion backwards on three open models of known active size on Google Vertex (DeepSeek V3.1 at
37.5B active gives 4.39 TB/s, GLM-4.7 at 33.6B gives 4.44, Kimi K2 Thinking gives 4.17), then
divides that bandwidth by each Claude model's OpenRouter throughput.

I extended the series to the models the post does not cover using Artificial Analysis P50
measurements retrieved 2026-09-13. The two measurement series can be compared on four models, and
they agree to within 15%: Opus 4.6 1.03, Opus 4.5 1.11, Sonnet 4.5 1.15, Sonnet 4.6 0.90. That
agreement is what licenses the extension.

Results under the source's FP8 assumption, in billions of active parameters:

| Model | Vertex series | Artificial Analysis series |
|---|---|---|
| Opus 4 | 174-196 | — |
| Opus 4.1 | 167-188 | — |
| Opus 4.5 | 100-113 | 90-101 |
| Opus 4.6 | 93-105 | 90-102 |
| Opus 4.7 | — | 91-102 |
| Opus 4.8 | — | 69-78 |
| Opus 5 | — | 78-88 |
| Fable 5 | — | 61-68 |
| Fable 5.1 | — | 60-67 |
| Sonnet 4.5 | 98-110 | 85-95 |
| Sonnet 4.6 | 78-88 | 87-98 |
| Haiku 4.5 | — | 47-53 |

**Typical error: a factor of 2.5, and biased in a direction that changes by model.** Four separate
things move the answer, and only the first is in the source's stated error bar.

1. **Precision.** BF16 halves every number; a hybrid of FP8 dense weights with FP4 experts, at
   0.68-0.73 bytes per active parameter, multiplies them by about 1.4. The FP8 numbers above become
   127-154B for Opus 4.6 and 65-78B for Haiku 4.5 under the hybrid.
2. **Serving policy, which is the big one.** Anthropic sells Opus 4.8 in a fast mode at "roughly
   2.5x normal speed" for 2x the price, with no separate model card, no separate system card, and a
   `claude-opus-5-fast` slug sitting next to the standard `claude-opus-5` on OpenRouter. The same
   weights are served at 2.5x the per-user token rate when Anthropic chooses to. Route T applied to
   fast mode would report a model 2.5x smaller than route T applied to standard mode. That is the
   error bar.
3. **Hardware.** Anthropic states it runs Claude on "AWS Trainium, Google TPUs, and NVIDIA GPUs".
   The calibration assumes Claude on Vertex sits behind the same effective bandwidth as DeepSeek and
   GLM on Vertex. Ironwood TPU is 192 GB HBM3e at 7.2 TB/s per chip against Trainium2's 96 GB at
   2.9 TB/s, so a wrong guess about which fleet served a given measurement is worth more than a
   factor of two on its own. The measured cross-provider spread on fixed weights is smaller but not
   nothing: Sonnet 4.5 runs at 48.7 t/s on Bedrock and 38.5 on Azure, a spread of 1.27x.
4. **Speculative decoding.** MTP-style speculative decoding raises tokens/sec above the
   bandwidth-per-step limit, so it inflates apparent bandwidth. The calibration absorbs it only if
   Claude and the three open reference models use it to the same degree, which nobody knows. The
   source says so: "I have no clue what optimizations Opus may have, which can range from native FP4
   experts to spec decoding with MTP to whatever."

The diagnostic that settles how much to trust route T's cross-model comparisons is in the table
above. It reports Fable 5.1, which Anthropic prices at 2x Opus 5 and positions a tier above it, as
the *smallest* frontier model in the list. It reports Opus and Sonnet as the same size throughout
the 4.5-4.7 era. Both readings are implausible, and both have the same explanation: Anthropic has
been optimizing serving speed hard and advertising it ("Fable-level intelligence, Opus-level price,
Sonnet-speed. In our tests it was about twice as fast as Opus 5"). Route T is therefore usable for
order of magnitude and for a within-model change over time where nothing else moved, and not usable
for ranking two contemporaneous models.

### Route C: training compute with an assumed token-to-parameter ratio

`C = 6 N_active D`. Write `D = R N_active` and `N_active = sqrt(C / 6R)`. Epoch publishes training
compute for four Claude models: Claude 2 at 3.87e24, Claude 3 Opus at 1.64e25, Claude 3.5 Sonnet at
2.7e25, Claude 3.7 Sonnet at 3.35e25. Three are flagged Speculative and one Likely.

The formula is exact where both sides are known. GPT-4 at 2.1e25 FLOP with R = 46, its leaked
13T tokens over ~280B active, returns 276B. DeepSeek-V3 at 3.4e24 with R = 400 returns 37.6B against
a published 37B. So the arithmetic is not the problem; R is.

| R (tokens per active parameter) | Claude 2 | Claude 3 Opus | Claude 3.5 Sonnet | Claude 3.7 Sonnet |
|---|---|---|---|---|
| 20 | 180 | 370 | 474 | 528 |
| 46 | 118 | 244 | 313 | 348 |
| 100 | 80 | 165 | 212 | 236 |
| 200 | 57 | 117 | 150 | 167 |
| 400 | 40 | 83 | 106 | 118 |

**Typical error: a factor of 3, entirely from R.** R ran at 20 for Chinchilla-optimal dense models,
46 for GPT-4, and 400 for DeepSeek-V3, and it has risen monotonically as the industry moved to
sparse MoE and heavy over-training. The route is therefore only useful where the era pins R. For
2023-era models it does: Claude 2 and Claude 3 Opus predate the sparse-MoE over-training regime, so
R = 20-46 is the live range and the route is informative. For 2024-onward models it is not: the
2.7e25 for Claude 3.5 Sonnet is consistent with anything from 106B to 474B depending on a ratio
nobody has published.

### Route S: total parameters times an assumed sparsity

Only available for the Fable/Mythos class, where the Financial Times reported industry estimates of
about 8T total for Mythos 5 and about 5T for Fable 5 on 2026-08-07. Applying contemporaneous
sparsity references to 5T total gives 186B active at Kimi K3's 27x (2.8T total over 104B active),
156B at DeepSeek-like 32x, and 104B at Kimi K2-like 48x.

**Typical error: a factor of 2, plus an unresolved inconsistency in the input.** Anthropic states
that Fable and Mythos "are the same model, but with different levels of safeguards", and the Fable
5.1 & Mythos 5.1 system card says they "share identical model weights". Two shared-weight models
cannot have different parameter counts, so the FT's 8T and 5T are not jointly reliable. What
survives is the multi-trillion order of magnitude for the class, which is corroborated
independently by route T's MoE expansion of Opus 4.6 to 1.66-3.27T total.

### Route P: price

Not usable, and I want to record why rather than leave it as an open lead. Claude's list prices sit
8 to 20 times above open MoEs of known size: Opus at $25 per million output tokens against
DeepSeek V3.1 at $1.68 with 37B active, Kimi K2 at $2.50 with 32B active, GLM-4.6 at $2.20 with 32B
active. SemiAnalysis's reported ~70% Anthropic inference margin, up from ~38% a year earlier, says
list price is roughly 3x serving cost and the multiple is moving fast. A price ratio between two
Anthropic models is a packaging decision: Opus 4.8 costs the same $5/$25 as Opus 4.7 while its fast
mode fell from $30/$150 to $10/$50, and Claude 3.5 Haiku launched at 4x Claude 3 Haiku's price then
was cut 20% five weeks later. Price is used below only as a weak ordinal signal, and only where it
moved by more than 2x.

### What is deliberately not used

No score-to-size inference. No latency-to-size inference (time to first token is a prefill and
queueing measurement, not a weight-reading one). No inference from context window or tokenizer. The
tokenizer change at Claude 4.7 and later, which produces "approximately 30% more tokens for the same
text", changes tokens per unit of text and not FLOPs per token, so it does not enter here.

## Model by model

Confidence grades: **A** disclosed or near-official; **B** strong indirect evidence, meaning
credible leaks corroborated by throughput or pricing analysis; **C** family transfer or a single
weak signal. Nothing in this provider reaches A.

### claude-2.0 and claude-2.1 — change 100B to 130B, grade C

Current 100B is transferred backwards from later Sonnet estimates, with the registry note conceding
"the older architectures are not established". Route C is unusually informative here because the era
pins R: Claude 2 is a July 2023 dense model from before the sparse-MoE over-training regime, so
R = 20-46 is the live range, giving 118-180B. Alan Thompson's July 2023 note independently proposed
130B, with no reproducible calculation behind it but landing in the same place. Two weak lines
converging on 120-180B is worth more than a backward transfer from a 2025 model.

Recommend **130B active, 60-250B**, for both 2.0 and 2.1. The low end covers R = 100 and the
possibility that Epoch's Speculative 3.87e24 is high; the high end covers a sub-Chinchilla token
budget. No evidence distinguishes 2.1 from 2.0, and Anthropic described 2.1 as a context and
accuracy release, so they share a value. This is a 1.3x change and below any threshold that would
move a conclusion; take it or leave it.

### claude-3-opus-20240229 — change 180B to 300B, grade C

This is the change I am most confident about, and the current value is the registry's weakest link.
180B is transferred from the Opus 4/4.1 bandwidth estimate, which the registry note is explicit
about. That transfer crosses fifteen months, a hardware generation, a precision convention (BF16
serving was standard in early 2024; the Opus 4 estimate assumes FP8), and the industry-wide
2024-2025 scale-down, and it runs in the wrong direction: it imports a post-shrink number into a
pre-shrink model.

Three lines put Claude 3 Opus higher.

- Route C at the era-appropriate R: 370B at Chinchilla R = 20, 244B at GPT-4's R = 46, from Epoch's
  1.64e25.
- Peer anchor. Claude 3 Opus was the March 2024 model that matched GPT-4, whose leaked configuration
  is about 1.8T total over about 280B active. Reading Opus 3's total across at GPT-4's 6.4x sparsity
  from unexcitedneurons' 1.66-3.27T frontier-total band gives 260-510B.
- [Epoch's own framing](https://epoch.ai/gradient-updates/frontier-language-models-have-become-much-smaller):
  "the scale-down from GPT-4 and Claude 3 Opus to current frontier models is probably close to an
  order of magnitude". The registry currently encodes a scale-down of 1.8x from Claude 3 Opus to
  Opus 4.5, which is not that.

Anthropic's $75 per million output tokens for Opus 3, the highest output price any major lab has
charged before or since and five times what it wanted for Sonnet 3, is a weak fourth line pointing
the same way.

Recommend **300B active, 120-600B**. Note that this partially reverses the existing note's rejection
of an upward move. That note rejected the specific chain of Thompson's unexplained 2T total times an
assumed quarter activation, which is correct to reject on both legs. It then adopted a transfer that
is weaker still. 300B is not that chain; it is the midpoint of route C at R = 20-46 and of the
GPT-4 peer read.

### claude-3-sonnet-20240229 — keep 100B, grade C

No training-compute estimate exists for this model, so route C is unavailable and route T did not
exist yet. What remains is the price tier ($3/$15, the same as every later Sonnet), Anthropic's
statement that Sonnet 3 is faster than Claude 2, and Thompson's unexplained 70B. Keep **100B,
40-200B**. The wide low end reflects the Thompson figure and the speed claim; I would not defend the
central against 70B if someone preferred it.

### claude-3-haiku-20240307 — keep 20B, grade C

The weakest-evidenced row in the family, and I could not improve it. Haiku 3 launched at $0.25/$1.25,
five times below Claude 3 Sonnet, with Anthropic emphasising ingestion and generation speed. Thompson
proposed 20B without a calculation. Epoch's [o4-mini range of 10-30B](https://epoch.ai/data-insights/ai-capabilities-progress-has-sped-up)
is the only cross-family plausibility check available. Keep **20B, 8-45B**, and keep the existing
note's caveat that dense execution is assumed at this scale.

### claude-3-5-sonnet-20240620 and claude-3-5-sonnet-20241022 — keep 100B, grade C

Three estimates exist and they do not agree.

- Epoch's 400B total times the quarter-active convention gives 100B, which is what the registry uses.
  Note that the 400B itself comes from a 2024 inference-economics guess ("Sonnet is served only at
  around 60 tokens per second", "$15 per million output tokens"), not an architecture, and the
  quarter-active convention is imported from Epoch's separate GPT-4o energy analysis.
- Microsoft's MEDEC paper states "Claude 3.5 Sonnet (2024-10-22), the latest model (approximately
  175B parameters)". The authors disclaim it in the same section: "Most numbers of parameters are
  estimate reported to provide more context." No source is cited. I weight this near zero, and note
  that 175B is exactly GPT-3's parameter count, which is the single most common placeholder in
  papers that need a number for a closed model.
- Route C on Epoch's 2.7e25 spans 106B at R = 400 to 313B at R = 46, which is to say it is
  uninformative for a mid-2024 model.

Keep **100B, 50-250B** for both snapshots, with the range widened upward from the registry's current
50-200B to carry the route C and MEDEC pressure. Anthropic's own contribution is Amodei's "Claude 3.5
Sonnet is a mid-sized model that cost a few $10M's to train", which supports the tier and not the
number.

### claude-3-5-haiku-20241022 — change 20B to 30B, grade C

The weakest of my four proposed changes, offered because 20B here is a pure transfer from Haiku 3
that ignores the one concrete signal available. Anthropic raised the price fourfold over Haiku 3, to
$1/$5 from $0.25/$1.25, and said explicitly: "we've increased pricing for Claude 3.5 Haiku to reflect
its increase in intelligence". They also reported it surpassing Claude 3 Opus on many benchmarks. A
4x price move is one of the few price signals in this provider large enough to clear the noise floor
established in route P. Against that, the price was cut to $0.80/$4 five weeks later, and capability
gains at fixed size were the defining feature of the 2024-2025 period.

Recommend **30B, 12-60B**. A 1.5x change on a 4x price move is deliberately conservative; the
evidence supports "larger than Haiku 3" and does not support a specific multiple.

### claude-3-7-sonnet — keep 100B, grade C

Epoch rates its 3.35e25 training compute "Likely" rather than Speculative, the best-graded compute
figure for any Claude model, but route C converts it to anything from 118B to 348B depending on R.
No throughput series covers it. Keep **100B, 50-250B** as a Sonnet-line transfer, with the same
reasoning as the 3.5 Sonnet snapshots.

### claude-opus-4 and claude-opus-4-1 — keep 180B, downgrade to grade B-minus

This is the record the brief asks me to check, and the answer is that the argument holds up better
than I expected but is worth less than its current framing implies.

What it gets right: it is model-specific, it uses a single provider and a single measurement source
across all six Claude models it covers, and it calibrates the bandwidth constant against three open
models of known active size rather than assuming a datasheet number. The FP8 arithmetic is correct:
4.0-4.5 TB/s over 23 tokens/sec is 174-196B for Opus 4, over 24 is 167-188B for Opus 4.1. Rounding
both to 180B is reasonable.

What it gets wrong, or rather what it cannot see: the 1.67x throughput gap between Opus 4.1 at 24
tokens/sec and Opus 4.5 at 40, which is the entire basis for treating these two models as bigger than
everything after them, is smaller than the 2.5x that Anthropic itself achieves on fixed weights by
selling a fast mode. The gap also coincides with the arrival of Project Rainier's Trainium2 capacity
at scale and the Google TPU expansion, either of which can move throughput by more than 1.67x with
the weights unchanged. The source's stated "50% error bars" cover the precision question only.

What keeps 180B rather than collapsing it to 100B: the 1.67x throughput step is corroborated by an
independent 3x list-price cut at the same model transition, $15/$75 down to $5/$25. Two different
signals moving together across the same boundary is better evidence of a real efficiency step than
either alone, even though neither identifies how much of it was architecture and how much was fleet.

Recommend **keeping 180B, widening to 80-360B**, and restating the basis as a weak model-specific
signal rather than a serving-bandwidth measurement. The low end is the BF16 scenario, the high end
the hybrid FP8/FP4 scenario at 238-288B plus headroom.

### claude-sonnet-4 — keep 100B, grade C

A transfer from Sonnet 4.5's route T estimate, which is what the registry note already says. No
model-specific measurement exists; Artificial Analysis does not report an output speed for it and the
Vertex series does not cover it. Keep **100B, 45-220B**.

### claude-sonnet-4-5 — keep 100B, grade B-minus

The best-measured Sonnet. Two independent measurement series: Vertex at 41 tokens/sec giving 98-110B,
Artificial Analysis at 47.3 giving 85-95B. Both bracket 100B under FP8. The hybrid-precision scenario
would put it at 116-161B. Keep **100B, 45-220B**.

Worth recording for the dataset's own sake: the cross-provider spread on this exact model, 48.7
tokens/sec on Bedrock against 38.5 on Azure, is 1.27x, and it is the cleanest available measurement
of how much of route T's signal is serving rather than architecture.

### claude-sonnet-4-6 — keep 100B, grade B-minus

The two series disagree in direction here: Vertex at 51 tokens/sec gives 78-88B, Artificial Analysis
at 45.9 gives 87-98B, a 1.11x disagreement that is itself within the measurement noise established
above. The registry note already says 100B is "a deliberately rounded family prior, with 50-200B
sensitivity, not a claim that the central FP8 estimate for 4.6 was 100B", which is exactly right.
Keep **100B, 40-210B**.

### claude-haiku-4-5 — change 20B to 40B, grade C-plus

The strongest case for change after Claude 3 Opus. The current 20B is transferred from the Haiku 3
prior, which is Thompson's unexplained 2024 guess about a model two generations older and roughly a
fifth of the price. Three lines put Haiku 4.5 higher.

- Route T. Artificial Analysis measures 85 tokens/sec reasoning and 78 non-reasoning, giving 47-53B
  and 51-58B under the same FP8 calibration that produces the 100B the registry accepts for Opus 4.5.
  It is not coherent to accept the calibration for Opus and reject it for Haiku.
- Capability. Anthropic claims "similar levels of coding performance [to Claude Sonnet 4] but at
  one-third the cost and more than twice the speed", and that Haiku 4.5 "even surpasses Claude
  Sonnet 4 at certain tasks, like using computers". A model at Sonnet 4's capability is a poor fit
  for a fifth of Sonnet 4's assumed active size.
- Price. $1/$5 against Sonnet's $3/$15 is exactly one third, which at face value would put Haiku at
  33B against a 100B Sonnet.

Pulling the other way: Anthropic also says Haiku 4.5 runs "up to 4-5 times faster than Sonnet 4.5",
which read as a per-token rate would give 20-25B. That claim is inconsistent with the measured 85
against 47.3 tokens/sec, 1.8x, so it is almost certainly an end-to-end figure including token counts
and time to first token, not a decode rate. And route T is least reliable for small models, where
kernel-launch, collective-communication, and scheduler floors stop throughput scaling with size.

Recommend **40B, 15-80B**, below the 47-53B route T reading precisely because of that small-model
floor, and well above 20B. This doubles every FLOP figure for every Haiku 4.5 point in the registry,
so it is the change with the largest downstream effect.

### claude-opus-4-5 and claude-opus-4-6 — keep 100B, grade B-minus

Best-supported Opus records. Opus 4.5 at 40 tokens/sec on Vertex gives 100-113B and at 44.5 on
Artificial Analysis gives 90-101B; Opus 4.6 at 43 gives 93-105B and at 44.3 gives 90-102B. Four
readings, two sources, all bracketing 100B under FP8. Keep **100B, 50-250B** for both. The upper end
carries the hybrid FP8/FP4 scenario, which puts Opus 4.6 at 127-154B, and I would not be surprised
if that scenario turned out to be the real one; it is not the central because nothing establishes
which precision Anthropic serves.

The corresponding total-parameter estimate, if anyone needs one, is 1.66-3.27T depending on assumed
sparsity, and the source explicitly rejects 10T-plus totals for this class.

### claude-opus-4-7 — keep 100B, grade C

Artificial Analysis measures 44 tokens/sec at max effort, giving 91-102B, which is the first
model-specific measurement this record has had; the registry currently carries a transfer from the
4.5/4.6 analysis. The measurement and the transfer agree, so the number does not move but the basis
improves. Keep **100B, 45-250B**.

### claude-opus-4-8 — keep 100B, grade C

Route T reads it smaller than its predecessors: 58 tokens/sec gives 69-78B. I decline to move the
central down on that, for two reasons. Opus 4.8 is precisely the model whose fast mode demonstrates
that Anthropic was pushing serving throughput hard in this release, so a throughput gain is the
expected artifact of the serving work rather than evidence about weights. And Anthropic held the
price at $5/$25, identical to Opus 4.7, while cutting fast-mode price threefold, which is what a
serving-side gain looks like rather than an architecture-side one. Keep **100B, 40-240B**, and note
the downward pressure honestly rather than encoding it.

### claude-opus-5 and claude-opus-5-max — keep 100B, grade C

Same model, two effort configurations, one coefficient. Route T at 51-52.7 tokens/sec gives 78-88B.
The registry's existing bases, a Kimi K3 reference transfer at 104B activated in a 2.8T MoE, and the
Opus family prior, both give 100B. Three lines within 25% of each other is as good as this provider
gets. Keep **100B, 45-260B**. [Epoch's model page](https://epoch.ai/models/claude-opus-5) lists
parameters unknown, which remains true.

Effort configuration changes the number of tokens generated, not the FLOPs per token, so `max` and
the generic row share the coefficient. That is already how the registry treats them.

### Claude Fable 5 and Claude Fable 5.1 — reference models, 150B, grade C

Neither has a registry row. They matter because the internal research model's identity is defined by
reference to Fable 5.1, so a number for Fable is a number for that row.

Anthropic's position is unambiguous and near-official: Fable and Mythos are the same weights with
different safeguards, stated on the announcement page, in the pricing footnote, and in the system
card ("share identical model weights and differ only in the safeguards wrapped around them"). For the
June pair, Fable 5's classifiers route flagged cybersecurity, biology-and-chemistry and distillation
requests to Claude Opus instead, which is a routing difference and not a weights difference. So Fable
and Mythos share a parameter count at each version, and the FT's separate 8T and 5T figures cannot
both be right.

Route S is the usable route. Taking the FT's 5T total for the class and applying contemporaneous
sparsity references gives 186B at Kimi K3's 27x, 156B at DeepSeek-like 32x, 104B at Kimi K2-like 48x.

Route T reads Fable 5.1 at 60-67B, smaller than Opus 5, which I reject. Fable sits a tier above Opus
in Anthropic's own lineup, is priced at twice Opus, and Anthropic advertises its speed as an
engineering result rather than a consequence of being small: "Fable-level intelligence, Opus-level
price, Sonnet-speed. In our tests it was about twice as fast as Opus 5 and used half as many tokens."
A model whose selling point is that it was made fast is the worst possible subject for an inference
that assumes throughput reflects size.

Recommend **150B active, 60-400B** for both Fable 5 and Fable 5.1, and the same for Mythos 5 and 5.1
should they ever need rows. The low end concedes route T; the high end covers Mythos at the FT's 8T
with modest sparsity. Fable 5.1 gets the same number as Fable 5: Anthropic describes 5.1 as about
25% cheaper for typical workloads and faster, which is an efficiency claim, and there is no basis to
separate them.

### anthropic-internal-research-flt-2026-08 — change 100B to 150B, grade C

Anthropic described it only as "a general-purpose internal research model roughly comparable to
Claude Fable 5.1". The registry currently gives it 100B, the shared frontier prior carried by the
Opus records and by gpt-6-astra. That is the wrong anchor: the model's own stated comparability class
is Fable, which is a tier above Opus, priced at twice Opus, and estimated at multi-trillion total by
the only reporting that exists. If the description is taken at face value, the model should carry
Fable's number, not Opus's.

Recommend **150B active, 55-400B**, matching the Fable 5.1 recommendation. The one-and-a-half-fold
move is small relative to the row's other uncertainties: the research note's own input-token
reconstruction carries a 3.6e21-to-1.2e22 band, a factor of 3.3, and the human side carries
24,000-300,000 hours, a factor of 12.5. Changing this coefficient moves the row's FLOPs by 1.5x and
does not change which estimate dominates its error budget.

Two caveats specific to this row. "Roughly comparable" is a capability statement, and a research
model can reach a given capability at a different size than a shipped one, in either direction.
And the model is never served to customers, so route T can never be applied to it; its number will
always be a transfer.

## What would actually settle this

In rough order of value: an Anthropic disclosure, which has not happened once in four years and
should not be planned for; a leak with architecture in it, noting that the March 2026 Fortune leak
contained none; Epoch populating its `Parameters` column for any Claude model; a throughput analysis
run against fast-mode and standard-mode endpoints of the same model, which would measure the
serving-policy confound directly instead of bounding it at 2.5x; or a statement from Anthropic about
which fleet serves which endpoint, which would remove the largest single term in route T's error.

Retained extracts and provenance: `agent-work/sources/model-priors/anthropic/`. Arithmetic:
`research/model-priors/anthropic/compute_priors.py`, output in the sibling `calculations.json`.
