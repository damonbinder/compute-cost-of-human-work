# Active-parameter priors for Google, xAI and other closed models

*Created 2026-09-13 11:56.*

Scope: every Google and xAI row in `../../models.csv` and
`../../../AI Compute vs Human Time/dataset/models.csv`, plus every other row
whose `active_parameters_basis` is `estimated` and whose company is neither
OpenAI nor Anthropic. Proposals only — neither `models.csv` is edited here.
Machine-readable version in `google-xai-others-proposals.csv`. Retained source
extracts in `agent-work/sources/model-priors/google-xai-others/`.

## TL;DR

Nothing in scope is disclosed. Google has never published a parameter count for
any Gemini model above Nano-2, xAI has published one only for Grok-1 and Grok-2,
and Alibaba has published none for its hosted `-max`, `-plus` and `-turbo`
aliases. So this is a question about which reference class to transfer from, and
the answer that matters most is that **the reference class has moved and the
dataset's priors have not.** Disclosed frontier mixture-of-experts models have
gone from roughly 2x sparsity in 2024 (Grok-2: 270B total, 115B active) to 25-33x
in 2026 (Kimi K3: 2.8T total, 104B active; Qwen3.8-Max: 2.4T total, 95B active),
and active counts have stayed flat at 17-40B for everything except the very
largest models. Nothing publicly disclosed, at any date, exceeds 115B active.

Seven rows move by more than 1.5x, in four directions: **Gemini 2.0 Flash and
both Gemini 2.5 Flash rows down** from 40B to 25B, **Grok 3 and Grok 4 up** from
115B to 200B, **Grok 4.20 down** from 115B to 70B, and **qwen-turbo down** from
14B to 6B. Everything else holds its central value; several rows get a wider
stated range or a better-grounded basis instead, and two rows should change
`active_parameters_basis` from `estimated` to `reported`: `gemini-1.5-flash-8b-001`,
which Google states is 8B, and `glm-5.2`, whose 40B is now corroborated
independently by Epoch at Confident. The Grok 4 change matters most
for the dataset: the 115B there is a transfer from Grok-2's released weights, and
Grok-2 is the single most architecturally atypical model in the whole reference
class — a 2024 design with a giant always-on shared MLP and only 2.35x sparsity.
Transferring it forward two years is transferring exactly the wrong number.

On the convention: **2N is fine at 4k context and badly wrong at 128k**, and it
is worst for the sparse models it is most often applied to. For a 100B-active
frontier proxy, attention adds 5% at 4k, 43% at 32k and 172% at 128k on a decode
step. For a 22B-active model like Qwen3-235B-A22B, whose attention stack is sized
for a 235B model, attention already exceeds 2N at 32k. The dataset should keep 2N
as the headline coefficient and carry a context-dependent correction separately,
because the correction depends on the workload, not the model.

---

## Methods

### What counts as evidence

Ranked, best first.

1. **Architecture-derived counting from published weights.** Grok-2's
   `config.json` reproduces its published 115,019,056,768 active and
   269,515,497,472 total counts to within 0.11% and 0.00% respectively
   (`convention_arithmetic.py`). Where this is available it is not an estimate.
2. **Official statements of size.** Google's developer blog calls Gemini 1.5
   Flash-8B an "8 billion parameter version" of 1.5 Flash. Mistral's Large 3
   release states "41B active and 675B total". These are grade A.
3. **Epoch AI's database.** Epoch tracks total and active parameters for 3,612
   models with an explicit confidence scale — Confident (+/-3x at 90%), Likely
   (+/-10x), Speculative (+/-31x). For several models in scope Epoch's note is
   the only quantitative public claim that exists, and for Grok 4.20, Grok 4.3
   and Grok 4.5 the underlying evidence is Elon Musk stating a number on X.
   Treating a Musk post as a disclosure is uncomfortable, but it is a statement
   by the developer about its own model, and Epoch records it as such. I follow
   Epoch and mark it B, not A.
4. **Within-provider price ladders.** Input price tracks prefill, which is
   compute-bound and roughly linear in active parameters. The margin term does
   not cancel between providers or across years, but it partly cancels within
   one provider's ladder at one date. I use only within-ladder ratios, and never
   as better than one-significant-figure evidence.
5. **Decode throughput against memory bandwidth.** A decode step must stream the
   active weights out of HBM, so `N_active <= K * BW * eta / (bytes_per_param *
   tokens_per_second)`, where K is the number of chips the model is sharded over
   and eta is achieved bandwidth utilization. K is not observable, which makes
   this an upper bound with a free multiplicative parameter. It is worth
   computing anyway, because it rules out some claims.
6. **Family and peer transfer.** What the dataset already does. Explicitly the
   weakest, and the grade-C default.

### What I refuse to use

Content-farm articles asserting parameter counts. Searching for Gemini 3 Pro's
size returns confident claims of 1.5T, 1.8T and "approximately 200 billion
active" from SEO blogs citing a "Gemini 3 technical brief from Google Research"
that does not exist — the actual Gemini 3 Pro model card contains the same
architecture boilerplate as the 2.5 report and no numbers. One widely-shared
estimate of ~7.5T total for Gemini 3 Pro is a public regression fit whose author
labels it "vibe-mathing". None of these enter any estimate below.

### Confidence grades

- **A** — disclosed by the developer, or derived arithmetically from published
  weights. Expected error under 1.2x.
- **B** — strong indirect evidence: a developer statement short of a spec, a
  same-family open model the provider has tied the alias to, or two independent
  quantitative lines agreeing. Expected error under 2x.
- **C** — family or peer transfer, or a single weak signal. Expected error 3x,
  and the low-high range is where the information actually is.

### The reference class

Every frontier-scale mixture-of-experts model with a disclosed or
near-disclosed active count, which is the comparison set every grade-C estimate
below is transferring from. Dense models are marked.

| Model | Date | Total (B) | Active (B) | Sparsity | Basis |
|---|---|---|---|---|---|
| Grok-1 | 2023-11-04 | 314 | 79 | 4.0 | disclosed |
| Mixtral 8x22B | 2024-04-17 | 141 | 39 | 3.6 | disclosed |
| Grok-2 | 2024-08-13 | 270 | 115 | 2.3 | released weights |
| Mistral Large 2 | 2024-07-24 | 123 | 123 | dense | disclosed |
| DeepSeek-V3 | 2024-12-24 | 671 | 37 | 18.1 | disclosed |
| Qwen3-235B-A22B | 2025-04-29 | 235 | 22 | 10.7 | disclosed |
| Llama-4-Maverick | 2025-04-05 | 400 | 17 | 23.5 | disclosed |
| Kimi K2 | 2025-07-11 | 1040 | 32 | 32.5 | disclosed |
| Qwen3-Coder-480B-A35B | 2025-07-22 | 480 | 35 | 13.7 | disclosed |
| GLM-4.5 | 2025-07-28 | 355 | 32 | 11.1 | disclosed |
| gpt-oss-120b | 2025-08-05 | 117 | 5.1 | 22.9 | disclosed |
| Qwen3-Max | 2025-09-05 | ~1000 | ~70 | ~14 | Epoch estimate |
| MiniMax-M2 | 2025-10-27 | 229 | 10 | 22.9 | disclosed |
| Mistral Large 3 | 2025-12-02 | 675 | 41 | 16.5 | disclosed |
| GLM-4.7 | 2025-12-22 | 358 | 32 | 11.2 | disclosed |
| GLM-5 | 2026-02-12 | 744 | 40 | 18.6 | disclosed |
| Qwen3.5-397B-A17B | 2026-02-15 | 397 | 17 | 23.4 | disclosed |
| Kimi K2.5 | 2026-02-02 | 1040 | 32 | 32.5 | disclosed |
| DeepSeek-V4-Flash | 2026-04-24 | 284 | 13 | 21.8 | Epoch, Likely |
| DeepSeek-V4-Pro | 2026-04-24 | 1600 | 49 | 32.7 | Epoch, Likely |
| MiniMax-M3 | 2026-06-01 | 428 | 23 | 18.6 | disclosed (corrected 2026-09-13 from 22: the developer summary says about 23B activated and the released config counts 23.3B; the root registry record is 23B) |
| GLM-5.2 | 2026-06-16 | 744 | 40 | 18.6 | Epoch, Confident |
| Kimi K3 | 2026-07-16 | 2800 | 104 | 26.9 | Epoch, Speculative |
| Qwen3.8-Max | 2026-07-19 | 2400 | 95 | 25.3 | Epoch, Confident |
| GLM-5.3-Flash | 2026-08-20 | 320 | 18 | 17.8 | Epoch, Likely |

Three things fall out of this table and they drive most of what follows.

**Active counts are flat over three years.** The median is 32B in 2024 and 32B in
2026. Total parameters rose about 10x over the same window; sparsity absorbed all
of it. Serving economics, not capability, appear to set the active count, and
serving economics have not changed much.

**Nothing exceeds 115B active, ever.** The largest disclosed active count in the
table is Grok-2's, and the largest in 2026 is Kimi K3's 104B on a 2.8T-total
model. The dataset's shared 100B frontier prior therefore sits at the very top of
the observed distribution rather than in the middle of it. That is defensible for
a closed flagship — closed models are generally larger than the open frontier —
but it should be understood as an aggressive prior, not a neutral one.

**Grok-2 is an outlier and a bad source for transfer.** Its 2.35x sparsity is the
lowest in the table, because 62% of its active parameters sit in an always-on
shared MLP with `intermediate_size` 32768, twice the width of its routed experts.
Every 2026 model in the table is 17-33x sparse. Transferring Grok-2's 115B to
Grok 3, Grok 4 and Grok 4.20 propagates an architecture nobody builds any more.

### Reported-basis open models already in the registries

Listed because the brief asks for them as the reference class, and because they
are the rows a reader should compare any proposal against. No changes proposed to
any of these.

| model_id | Total (B) | Active (B) | In registry as |
|---|---|---|---|
| deepseek-v3, deepseek-v3-0324, deepseek-v3.2 | 671 | 37 | reported |
| deepseek-r1, deepseek-r1-0528 | 671 | 37 | reported |
| kimi-k2-instruct, kimi-k2.5, kimi-k2.6 | 1040 | 32 | reported |
| llama-4-scout | 109 | 17 | reported |
| llama-4-maverick | 400 | 17 | reported |
| glm-4.7 | 358 | 32 | reported |
| glm-5 | 744 | 40 | reported |
| gpt-oss-120b | 117 | 5.1 | reported |
| gpt-oss-20b | 21 | 3.6 | reported |
| qwen3-235b-a22b-instruct-2507, -thinking-2507 | 235 | 22 | reported |
| reka-flash-3 | 20.9 | 20.9 (dense) | reported |
| gemma-2-9b-it, gemma-2-27b-it, gemma-3-27b-it | dense | 9.2 / 27.2 / 27.0 | reported |

Two models named in the brief are absent from both registries: **Kimi K3**
(Epoch: 2.8T total, 104B active, Speculative, 2026-07-16) and any **Reka** model
other than Reka Flash 3. If Kimi K3 rows are added later, 104B active is the
number to use, grade C.

---

## Google

Everything Google has ever disclosed about Gemini sizes is in
`agent-work/sources/model-priors/google-xai-others/google-architecture-disclosures.md`.
The short version: Gemini 1.0 is "Transformer decoders" with Nano-1 at 1.8B and
Nano-2 at 3.25B and no other number; Gemini 1.5 Pro is sparse MoE; Gemini 1.5
Flash is a *dense* transformer decoder online-distilled from "the much larger"
1.5 Pro; Flash-8B is "single-digit billion parameter" and officially 8B; Gemini
2.5 and 3 are sparse MoE with distillation at "Flash size and below"; Gemini 3
Flash "is based on Gemini 3 Pro". No expert count, no top-k, no width, no depth,
for any model.

That leaves the price ladder as the only quantitative within-family signal. It is
internally consistent and it is worth stating once, because it drives the Flash
proposals. Within one generation, at one date:

| Generation | Pro input $/1M | Flash input $/1M | Flash-Lite input $/1M | Pro:Flash:Lite |
|---|---|---|---|---|
| 2.5 | 1.25 | 0.30 | 0.10 | 12.5 : 3 : 1 |
| 3.0 | 2.00 (3.1 Pro) | 0.50 (launch) | 0.25 (3.1 Lite) | 8 : 2 : 1 |
| 3.5 | — | 1.50 | 0.30 | — : 5 : 1 |

Anchoring the 2.5 ladder on a 100B Pro gives Flash 24B and Flash-Lite 8B.
Anchoring the 3.x ladder on a 130B Pro gives Flash-Lite 16B and Flash 33B. Both
land the Flash tier in the 20-35B band where every disclosed 2025-26 model at
that price point sits, and both put the current 40B prior above it.

Note what does *not* work: comparing prices across generations. Gemini 3.5 Flash
at $1.50/$9.00 is priced above Gemini 2.5 Pro at $1.25/$10.00. Flash is being
priced on capability, not cost, so only within-generation ratios are usable.

Throughput is consistent with the same picture but does not pin it. Gemini 3 Pro
Preview serves at 128 output tokens/s and Gemini 2.5 Pro at 120.7. On TPU v6e
(1.64 TB/s HBM) sharded 16 ways at 70% achieved bandwidth, 128 tokens/s implies
at most 143 GB of weights streamed per token, or 143B parameters at fp8. On
Ironwood (7.37 TB/s) sharded 8 ways the same speed implies at most 322B. The
bound moves by more than a factor of two on an assumption about K that I cannot
observe, so it constrains Gemini Pro to "somewhere between 70B and 320B" and no
better. It does usefully exclude a 1T-active reading, and it is the reason I am
comfortable that the Pro prior is the right order of magnitude.

### gemini-1.0-pro-001 — hold 70B, widen to 20-200B, grade C

Current prior 70B, transferred from Llama 2 70B as a contemporary serving peer.
The Gemini 1.0 report describes the family as Transformer decoders with no
mention of mixture-of-experts anywhere, in explicit contrast to the 1.5 report,
so treating 1.0 Pro as dense is right. Pre-training took "a matter of weeks,
leveraging a fraction of the Ultra's resources", and Epoch puts Ultra at 5e25
FLOP (Speculative). Beyond that there is nothing. Google's own contemporary dense
ladder topped out at PaLM 2-L, which Epoch records at 340B, and Gemini 1.0 Pro
was positioned well below that. 70B is as good a guess as any; the range is the
content.

### gemini-1.5-pro-001, -002, -naturalplan — hold 100B, widen to 35-250B, grade C

Sparse MoE, disclosed as such, with no count. The 2024 disclosed peers are
Grok-2 at 115B active and DeepSeek-V3 at 37B active — a 3x spread with Gemini 1.5
Pro sitting between them on capability. Google's own MoE precedent is relevant
and pushes up: GLaM (2021) ran 1.2T total with 97B activated per token, so a
100B-active Google MoE is not an extrapolation for Google the way it is for
DeepSeek. I would keep 100B and widen the sensitivity, which is currently stated
as "factor two" in some rows and 30-300B in others. 35-250B is my read and it
should be stated identically on every Pro row.

### gemini-1.5-flash-001, -002 — hold 27B, narrow to 12-40B, upgrade to grade B

Currently 27B transferred from Gemma 2 27B. This is a better-founded transfer
than the row notes suggest, and it deserves a grade upgrade rather than a value
change. The 1.5 report says Flash is a dense transformer decoder, online-distilled
from Pro, and that it does parallel attention and feedforward computation — so a
dense Gemma-class count is the right shape, not just the right scale. The price
anchor agrees: 1.5 Flash was $0.075/1M input against Flash-8B's $0.0375, a 2x
ratio on a model officially stated at 8B. Two independent lines land at 16-27B.
Keep 27B, narrow to 12-40B.

### gemini-1.5-flash-8b-001 — hold 8B, grade A, change basis to `reported`

Google's developer blog describes it as "an 8 billion parameter version of the
Gemini 1.5 Flash model", and the 1.5 report puts it in the "single-digit billion
parameter" class. That is a developer statement of size. The `active_parameters_basis`
on this row should be `reported`, not `estimated`. It is the one Gemini row where
the dataset knows the answer.

The row's existing note that "separate multimodal components are not quantified"
is correct and should stay — Flash-8B is natively multimodal, so vision and audio
positions run through the same 8B stack and 2N covers them, but any separate
front-end is not counted.

### gemini-2.0-flash-001, gemini-2.5-flash, gemini-2.5-flash-preview-05-20 — 40B to 25B, range 10-55B, grade C

This is the change I am most confident in. The 40B prior was transferred from
DeepSeek-V3 (37B) and Mixtral 8x22B (39B), the two largest-active disclosed MoEs
of 2024. Three years on, the disclosed models that actually occupy the Flash
price and speed band are smaller: MiniMax-M2 10B, DeepSeek-V4-Flash 13B,
Qwen3.5-397B-A17B 17B, GLM-5.3-Flash 18B, Llama-4-Maverick 17B, Kimi K2 and
GLM-4.5 both 32B. The 2024 anchor was the top of its distribution and the band it
was anchoring to has since resolved below it.

Three lines agree on 25B. The 2.5 price ladder anchored on a 100B Pro gives 24B.
Gemini 2.5 Flash serves at roughly 280 output tokens/s against Kimi K2 Thinking's
82 tokens/s — Kimi K2 is a disclosed 32B-active model, and while TPU serving is
better than the GPU deployments Kimi is measured on, a 3.4x speed advantage is
hard to get without a smaller active count. And Google's $0.30/1M input against
DeepSeek's own $0.27/1M for a 37B-active model implies Google's cost is well
under DeepSeek's price, since Google is not selling at cost.

Note Gemini 2.0 Flash and 2.5 Flash are treated identically here. Nothing
distinguishes them on the available evidence, and they were priced identically.

### gemini-2.0-pro-exp-02-05, gemini-2.5-pro, gemini-2.5-pro-preview-06-05, gemini-2.5-pro-03-25 — hold 100B, widen to 40-250B, grade C

Same reasoning as 1.5 Pro, one generation on. The 2.5 report confirms sparse MoE
and confirms that Flash and below are distilled, which implies Pro is the teacher
and therefore materially larger — but "materially larger than an undisclosed
number" is not a constraint. Throughput at 120.7 tokens/s is consistent with
anything from 70B to 320B depending on sharding. Hold at 100B.

### gemini-3-pro, gemini-3.1-pro-preview, gemini-3.1-pro-preview-customtools, gemini-3-deep-think-preview — 100B to 130B, range 50-320B, grade C

A 1.3x uplift, below the threshold at which I would flag it as a change, and I
want to be clear it is below the resolution of the evidence too. Holding all four
at 100B is defensible. The case for moving is that the top of the disclosed
reference class moved: the largest disclosed active count went from 37B in 2024
to 95-104B in 2026, on 2.4-2.8T-total models. Gemini 3 Pro is a 2026 closed
flagship with a 1M-token context and a 64k output limit, and closed flagships are
generally larger than the open frontier. Against that, Gemini 3 Pro serves at 128
tokens/s versus 2.5 Pro's 120.7, which shows no step change in serving cost, and
the price went up only 1.6x from 2.5 Pro to 3.1 Pro.

Deep Think gets the same per-token coefficient as Pro. It is a serving mode over
more tokens, not a different weight identity, and the existing row already
handles it that way by applying the coefficient to reported aggregate tokens.

### gemini-3-flash-preview, gemini-3.5-flash — hold 40B, range 15-90B, grade C

Deliberately not cut alongside the 2.x Flash rows. The Flash tier repriced
between generations: Gemini 3 Flash launched at $0.50/1M input against 2.5
Flash's $0.30, and Gemini 3.5 Flash sits at $1.50/$9.00, above Gemini 2.5 Pro.
The 3.x ladder anchored on a 130B Pro puts Flash at about 33B. Gemini 3 Flash
serves at 218 tokens/s and 3.5 Flash at 221, both slower than 2.5 Flash's ~280,
which is what you expect if the Flash tier grew. 40B is the top of the range I
would defend but it is inside it, and the 1.6x gap between the 2.x Flash proposal
and the 3.x Flash proposal is itself a claim the evidence supports.

The Gemini 3 Flash model card's "based on Gemini 3 Pro" establishes lineage, not
size, and the existing row notes say so correctly.

### gemini-3.1-flash-lite-preview — hold 20B, widen to 6-45B, grade C

Two anchors, neither strong. The 3.1 ladder at $0.25 input against 3.1 Pro's
$2.00 is 8x, giving 16B on a 130B Pro. Half of Gemini 3 Flash's $0.50 gives 20B
on a 40B Flash. Disclosed models in the Lite band run 3.6-18B — gpt-oss-20b at
3.6B, MiniMax-M2 at 10B, DeepSeek-V4-Flash at 13B, GLM-5.3-Flash at 18B — which
argues the low end of the range is live in a way the current row does not convey.
The row currently carries the dataset's shared small-tier assumption with no
stated sensitivity; the range is the change.

---

## xAI

### grok-2-1212 — hold 115B, grade A on the number, keep `estimated` on the row

The released weights give 269,515,497,472 total and 115,019,056,768 active, and
`config.json` reproduces both: 64 layers at hidden size 8192, 64 query heads and
8 KV heads at head dimension 128, an always-on shared MLP at intermediate size
32768, and 8 routed experts at 16384 with top-2 routing. Summing the layers gives
1.1489e11 active, 0.11% under the published figure, and 2.6951e11 total, exact.
The arithmetic is in `convention_arithmetic.py`.

The row keeps `estimated` because of a provenance gap the existing note already
records: the released weights are described as "the model trained and used at xAI
in 2024" and the row is the December `grok-2-1212` API revision. The number is
grade A; the identification of the number with the row is not.

Worth carrying forward into the rows below: 2.35x sparsity, the lowest in the
reference class, with 62% of active parameters in the shared MLP.

### grok-3-beta, grok-4 — 115B to 200B, range 80-450B, grade C

Both currently carry Grok-2's 115B as a family transfer. Epoch records Grok 3 at
3e12 total parameters (Likely) and Grok 4 at 3e12 (Speculative, with a cited
rumour of 2.4T), and Epoch's Grok 4 compute note assumes Grok 4 shares Grok 3's
pre-training, which is why I give the two rows the same active count.

The transfer fails on its own terms. If Grok 3 has roughly 3T total parameters
and kept Grok-2's 2.35x sparsity, it would activate 1.3T parameters per token,
which cannot be served at Grok 4's measured 132 output tokens/s at any plausible
sharding. So the sparsity ratio must have risen sharply, and the question is how
far. At the 15-30x that the rest of the 2026 reference class runs, 3T total gives
100-200B active.

The bandwidth bound brackets the top. At 132 tokens/s on eight H200s at fp8 with
70% achieved bandwidth, the model streams at most 204 GB per token, so at most
204B active; on eight H100s the same speed caps it at 142B; sharded 16 ways the
caps double. A model whose speed is a selling point will not be running at a
small fraction of its bandwidth bound, so the observed speed reads as 140-400B
worth of capacity being used rather than as an unconstrained ceiling.

200B central, 80-450B. The low end preserves the possibility that the 3T total is
wrong; the high end is where the bandwidth bound sits under generous sharding.
This is the change most consequential for the dataset, since Grok 4 carries
points.

### grok-3-mini-beta — hold 20B, range 8-50B, grade C

Currently transferred from Epoch's o4-mini estimate. Nothing xAI-specific exists.
Grok 3 mini was priced at $0.30/$0.50 per 1M, at the bottom of xAI's ladder,
which is consistent with a small-tier model but does not size it. Hold.

### grok-4.20-beta-0309b-reasoning — 115B to 70B, range 25-180B, grade C

The one xAI row with a developer statement attached. Epoch records Grok 4.20 at
5e11 total parameters (Likely), sourced to Musk on X: "This is just our V8 small
foundation model, so 500B params". The same foundation appears again under Grok
4.3, where Musk says "Grok 4.4 will be twice the size (1T)", and again in
coverage of Grok 4.5 as built on a 1.5T V9 foundation, "about 3x larger than
v8-small". The 500B figure is consistent across three separate statements, and
all of them read as total parameters.

So Grok 4.20 is a *smaller* foundation model than Grok 4, not a peer of it, and
giving both rows 115B is wrong regardless of which direction Grok 4 moves. Two
lines size it. At 8-20x sparsity, 500B total gives 25-60B active. On xAI's own
price ladder, Grok 4.20's $1.25/1M input against Grok 4's $3.00 is 42%, which on
a 200B Grok 4 gives 83B. I take 70B as the midpoint of those and carry a wide
range, because the two lines disagree by 2x.

Two details support the low end. Grok 4.20's output price is $2.50/1M, only twice
its input price, where every other model in the comparison set runs 5-10x; xAI is
not treating its decode as expensive. And it serves at 100.8 tokens/s despite
being a reasoning configuration with a 19.4s time to first token.

The row's existing caveat — that the mapping from the evaluation suffix `0309b`
to the documented `0309` snapshot is unresolved — is unaffected and should stay.

---

## Alibaba, Z.ai and Mistral

### qwen-max-2025-01-25 — hold 37B, range 15-90B, grade C

Qwen2.5-Max, mixture-of-experts, size never disclosed; Epoch's confidence is
Unknown. The current 37B comes from DeepSeek-V3 as a named contemporary MoE peer,
which is the right peer — the two models were released within a month of each
other and benchmarked against each other. The successor Qwen3-Max is estimated by
Epoch at roughly 70B active on a >1T-total model, reasoning from the
Qwen3-235B-A22B and Qwen3-Coder-480B-A35B architectures, so the Max tier grew
after this row's date. Hold 37B for the January 2025 snapshot.

### qwen-plus-2025-01-25 — hold 21B, range 8-45B, grade B-

Transferred from DeepSeek-V2.5, which activates 21B. Independently, Alibaba's
Plus tier has since been shown to track its open flagship: Epoch lists "Qwen 3.5
Plus (hosted 397B-A17B)", tying the alias to a 17B-active open model. A
Plus-tier active count of 17-22B is now supported by two lines rather than one.
Hold the value, upgrade the grade.

### qwen-turbo-2024-11-01 — 14B to 6B, range 2-18B, grade C

Currently transferred from Qwen2-57B-A14B. Two independent lines put the Turbo
tier well below that.

Alibaba's own price ladder at the time set Turbo at $0.05/1M input against Plus
at $0.40 and Max at $1.60 — Turbo is one eighth of Plus. On a 21B Plus that is
2.6B; on a 37B Max it is 1.2B. And the tier's successor is explicitly small:
Epoch's note on Qwen3.7 Flash records that "Qwen3.5 Flash and Qwen3.6 Flash were
both based on the 35B-A3B open weight models. Likely a 35B MoE with 3B active
parameters."

Both lines point at single digits. I take 6B rather than 3B because the 2024
Turbo predates the 35B-A3B line and Qwen2-57B-A14B is a real contemporary that
the tier could plausibly have been, and because the price ladder is weak evidence
in a market where Alibaba was pricing the cheap tier for share. 2-18B carries the
disagreement.

### qwq-plus — hold 32B, range 20-72B, grade B

Alibaba positions QwQ-Plus as an enhanced QwQ, and QwQ-32B is a disclosed 32.5B
dense model with 64 layers. Epoch has no separate number. A same-family transfer
where the provider names the family is about as good as grade-B transfers get.
Hold. The existing 16-72B sensitivity is fine; I narrow the low end to 20B
because a hosted "enhanced" variant of a 32B model is unlikely to be half its
size.

### qwen3.6-plus — hold 17B, range 10-35B, grade B

Transferred from Qwen3.5-397B-A17B, which Epoch confirms is the model behind the
hosted Plus alias in the adjacent generation. Hold.

### qwen3.7-max — 100B to 90B, range 50-150B, grade B-

An 11% move, below any reporting threshold, but it upgrades the grade from a bare
frontier-scale assumption to an interpolation between two Epoch entries. Qwen3-Max
(2025-09) is estimated at roughly 70B active on about 1T total. Qwen3.8-Max
(2026-07) is recorded at 2.4T total and 95B active with Confident confidence, as
is the matching open release Qwen3.8-2.4T-A95B. Qwen3.7-Max sits between them at
2026-05. 90B, closer to the later anchor because Alibaba's open 2.4T-A95B release
suggests the jump happened before 3.8.

### glm-5.2 — hold 40B, change basis to `reported`, grade A-

Epoch records GLM-5.2 at 744e9 total parameters with Confident confidence and the
note "40 billion active", and the GLM-5.3 entry corroborates it: "Same base model
as GLM-5.2, which had 744B total and 40B active." The current row already carries
40B, derived by the dataset from matching GLM-5 projection and expert dimensions
in `config.json`. Two independent derivations agreeing, one of them from published
config files, is a reported count rather than an estimate. The row's caveat that
GLM-5.2 changes sparse-attention indexer sharing is a real reason its active
count is not *directly* published, so A- rather than A.

### mistral-large-2402 — hold 123B, widen to 70-200B, grade C

Mistral has never disclosed the February 2024 model's architecture, and Epoch's
confidence on it is Speculative with no number. The current 123B is transferred
from Mistral Large 2 (2407), which Mistral does disclose as 123B dense. The
transfer direction is backwards — inferring a predecessor from a successor — and
Mistral has changed architecture family twice since, going sparse for Large 3
(675B total, 41B active). It is still the best available anchor, since Mistral
Large 1 was priced above Large 2 ($8/$24 against $3/$9) and was the flagship. Hold
the value, widen the range to carry the direction-of-transfer problem.

### open-mistral-7b — hold 7.3B, grade A, consider basis `reported`

Mistral's own announcement states 7.3B parameters for Mistral 7B, and the
safetensors total for `Mistral-7B-v0.1` is 7,241,732,096. The row's `estimated`
basis exists because Epoch records an API alias without a weight revision, which
is a revision-identification problem rather than a size problem. The number is
grade A; whether the basis should change depends on how strictly the dataset
reads "calculated directly from its published architecture" when the weight
revision behind the alias is unconfirmed. I would leave it `estimated` and say so
in the note, consistent with `grok-2-1212`.

### Out of interest but inside the filter

`gulordava-english-lstm-650` (39.3M active, a two-layer 650-unit LSTM) and the two
`fair-negotiator-2017` rows (1.64M) carry `estimated` bases and are neither Google
nor xAI, so they meet the scope filter literally. Both are small research models
whose sizes are derivable from published architectures, and neither is a frontier
mixture-of-experts question. No change proposed and no work done on them.

---

## The 2 x active-parameters convention

The dataset's `flops_per_token` is `2 * active_parameters`, and `COLUMNS.md` is
explicit that this "omits context-dependent attention costs and differences
between prompt, generation and cached-token processing". That framing is right.
What follows is how large the omissions are for models of the sizes estimated
above, and what a careful dataset should do about each.

All arithmetic is in `convention_arithmetic.py`, output retained at
`agent-work/sources/model-priors/google-xai-others/convention-arithmetic-output.txt`.

### Attention

A decode step at context length L must score the new query against L keys and
sum L values. Counting a multiply and an add as two operations, consistent with
the `two_active_parameters` convention:

    F_attn(decode at context L) = 2 * n_layers * (d_q + d_v) * L

where `d_q = n_heads * head_dim` is the total query width and `d_v = n_heads *
v_head_dim`. For standard attention with equal head dimensions this is
`4 * n_layers * d_q * L`. Grouped-query attention does not change it: GQA
reduces the number of *key and value* heads, which cuts KV-cache memory and
bandwidth, but every query head still attends over the full key set, so the FLOPs
follow the query width.

Prefill is half that per token. Over a causal prompt of length L the mean token
attends to L/2 predecessors, so the per-token average is `n_layers * (d_q + d_v)
* L`, and the whole-prompt cost is `n_layers * (d_q + d_v) * L^2`.

Attention as a share of 2N, for disclosed configurations and for two proxies at
the scales estimated above:

| Model | 2N (FLOP/token) | 4k decode | 4k prefill | 32k decode | 32k prefill | 128k decode | 128k prefill |
|---|---|---|---|---|---|---|---|
| Grok-2 (64L, d_q 8192, 115B active) | 2.30e11 | 3.7% | 1.9% | 30% | 15% | 120% | 60% |
| Gemini-Pro proxy (80L, d_q 8192, 100B active) | 2.00e11 | 5.4% | 2.7% | 43% | 21% | 172% | 86% |
| Gemini-Flash proxy (48L, d_q 5120, 25B active) | 5.00e10 | 8.1% | 4.0% | 64% | 32% | 258% | 129% |
| Qwen3-235B-A22B (94L, d_q 8192, 22B active) | 4.40e10 | 29% | 14% | 229% | 115% | 918% | 459% |
| GLM-4.5 (92L, d_q 12288, 32B active) | 6.40e10 | 29% | 14% | 232% | 116% | 926% | 463% |
| DeepSeek-V3, naive MLA (61L, 37B active) | 7.40e10 | 28% | 14% | 221% | 111% | 885% | 443% |
| DeepSeek-V3, absorbed MLA | 7.40e10 | 94% | 47% | 752% | 376% | 3009% | 1505% |

Layer counts and widths for the disclosed models are from their published
`config.json` files. The two proxy configurations assume 80 layers at width 8192
and 48 layers at width 5120, which are the shapes a dense-equivalent model of
those active sizes would have and are stated as assumptions, not findings.

Three things follow.

**The error is a function of sparsity, not of size.** Attention cost scales with
`n_layers * d_q`, which is set by the model's *dense* dimensions, while 2N scales
with the *active* count. A 22B-active model built inside a 235B-total shell
carries a 235B-scale attention stack, so its attention-to-2N ratio is five times
worse than Grok-2's at the same context. Since the whole trend in the reference
class is toward higher sparsity, the 2N convention is getting worse over time for
exactly the models the dataset most wants to cover.

**Interleaved local attention cuts the long-context term by 5-6x, and it is the
single largest unknown here.** Gemma 3 alternates five sliding-window layers with
a 1024-token window against one global layer. Under that pattern the mean
effective context per layer at 128k is 22,699 rather than 131,072, a 5.77x
reduction; at 32k it is 6,315, a 5.19x reduction. Google has not said whether
Gemini uses the same pattern, but Gemma is built from Gemini research and the
1M-token context window is hard to serve without something of the kind. If Gemini
does interleave, the 172% figure for the Pro proxy at 128k decode becomes about
30%. The dataset cannot resolve this, and should say so rather than pick a side.

**Multi-head latent attention trades FLOPs for bandwidth, and which number is
right depends on the kernel.** DeepSeek-V3 and Kimi K2 compress KV to a 512-wide
latent. Computed naively the attention cost is ordinary; computed in the absorbed
form used for bandwidth-bound decoding, each of 128 heads attends over a 576-wide
latent instead of a 192-wide head, and the FLOP count triples. Serving stacks
typically use the naive form for prefill and the absorbed form for decode, so a
single model has two defensible attention FLOP counts differing by 3.4x. This is
not a rounding issue and it is a reason to keep attention out of the shared
per-token coefficient entirely.

### Mixture-of-experts routing

Negligible as FLOPs. The router is one `d_model x n_experts` projection per
layer, so its cost relative to 2N is `n_layers * d_model * n_experts / N`:

| Configuration | Router share of 2N |
|---|---|
| 80 layers, d 8192, 256 experts, 100B active | 0.17% |
| 94 layers, d 4096, 128 experts, 22B active | 0.22% |
| 61 layers, d 7168, 384 experts, 32B active | 0.53% |

The real MoE overheads are not arithmetic. Expert-parallel all-to-all
communication, capacity-factor padding, and expert load imbalance all cost
latency and hardware-time, and they are the reason a MoE's achieved utilization
is lower than a dense model's. None of that is FLOPs, so none of it belongs in
`flops_per_token`. It belongs in `hardware_time` estimates, where the dataset
already has a separate method.

One genuine arithmetic subtlety: shared or always-on experts must be counted in
the active total. Grok-2 is the extreme case, with 62% of its active parameters
in a shared MLP; DeepSeek-V3 and Kimi K2 each have one shared expert alongside
their routed ones. Any active count taken from a config file has to include them,
and all the disclosed counts in the reference class do.

### Multi-token prediction and speculative decoding

DeepSeek-V3 trains a multi-token-prediction module and reports using it for
speculative decoding at inference. When a model drafts k tokens ahead and
verifies them with the full model, the FLOPs per *accepted* token rise, because
rejected drafts were still forwarded:

| Draft depth k | Acceptance 0.6 | 0.8 | 0.9 |
|---|---|---|---|
| 1 | 1.25x | 1.11x | 1.05x |
| 2 | 1.53x | 1.23x | 1.11x |
| 3 | 1.84x | 1.36x | 1.16x |

So speculative decoding makes 2N an *under*-estimate by 5-50%, in a way that is
invisible from the outside because the provider bills only accepted tokens. This
is small compared with the attention term and small compared with the 3x active
parameter uncertainty on every closed row, and I would not correct for it. It is
worth one sentence in the column documentation, because the direction is
consistent: every serving optimization that trades FLOPs for latency pushes the
true number above 2N.

### Looped and recurrent-depth decoding

The one failure mode that can break the convention outright. GPT-6 Astra is
reported to use recurrent-depth or looped-transformer decoding, in which the same
layer stack is run multiple times per token; the dataset's `gpt-6-astra` row
already flags that this "would multiply the per-token coefficient by an
undisclosed number of passes", and the Portal and Factorio research notes carry
two-pass and four-pass scenario rows.

Nothing in the Google, xAI or Alibaba scope is reported to do this. Google
describes Gemini 3 Pro as a sparse MoE transformer with no mention of weight
reuse across passes; xAI has said nothing about architecture since Grok-2. But
this is the one architectural change that makes 2N wrong by an integer multiple
rather than by a percentage, and it is not detectable from price, speed or
benchmark scores. The right treatment is the one the dataset already uses: a
scenario row, not a central-estimate adjustment.

### Vision and audio

Gemini, Grok and Qwen-VL are natively multimodal in the sense that image and
audio positions are converted to tokens and run through the same decoder stack.
Providers bill those positions as tokens — Gemini charges a fixed token count per
image tile and a fixed rate per second of audio — so multiplying billed tokens by
2N does capture the decoder work, provided the token counts used are the billed
multimodal counts and not just the text tokens.

What it does not capture is any separate encoder in front of the decoder. The
dataset already handles this correctly with the `encoder_parameters` and
`decoder_parameters` columns and the `gpt-4o-2024-08-06` row's separate ViT-bigG
proxy. For Gemini the separate-encoder term is not quantifiable — Google
publishes nothing about the vision tower — and the existing `gemini-1.5-flash-8b-001`
note already says so. The honest position is that a natively multimodal model's
2N coefficient covers its text-equivalent work and understates by an unknown
amount that is bounded by the encoder's size, which for published vision towers
runs 0.4-2B parameters against 25-130B decoders, so under 10%.

`COLUMNS.md` already forbids adding image patches and audio frames into the
`tokens` column, and requires them to stay in the research-note calculation.
That is the right rule and this analysis does not change it.

### Cached context

The largest omission in practice, and it is a workload property rather than a
model property. The `params_tokens` method excludes cache reads from the
parameter-multiplication term, which is correct — a cache read does not re-run
the feedforward stack. But the cached positions still have to be attended to by
every subsequent token. On a long agentic run with a 128k cached prefix and a few
thousand fresh tokens, the parameter term counts only the fresh tokens while the
omitted attention term is proportional to the full 128k for every one of them.
For the Pro proxy that is up to 1.7x the counted cost, or about 0.3x if Gemini
interleaves local attention.

### What a careful dataset should do

1. **Keep 2N as the shared coefficient.** It is the right decomposition:
   2N is a model property and the corrections are workload properties. Folding a
   context-dependent term into a per-model constant would make the column mean
   different things for different rows.
2. **Carry the attention correction in the research note, per point, using the
   formula above and the point's actual context distribution.** Not as a global
   multiplier. A 4k-context benchmark and a 128k-context agentic run differ by
   30x in this term.
3. **State the layer count and query width used.** The correction cannot be
   computed without them, and for every closed model they are assumptions. The
   proxy configurations in the table above are the ones I would use, labelled as
   assumptions.
4. **Do not correct for routing, and do not correct for speculative decoding.**
   Both are under 1% and under 50% respectively, against a 3x uncertainty on the
   active count itself.
5. **Keep looped decoding as a scenario row** wherever a model is reported to use
   it, as the Astra rows already do.
6. **Treat the typical error of plain 2N as: negligible at 4k, tens of percent at
   32k, and a factor of 2-3 at 128k** for the model sizes estimated here — with
   the caveat that if the model interleaves local attention, the 128k error
   collapses to tens of percent as well, and that for very sparse models with
   dense-scale attention stacks the error is several times worse at every
   context.

---

## Sources

- Epoch AI, Data on AI Models, https://epoch.ai/data/ai-models and
  https://epoch.ai/data/all_ai_models.csv, retrieved 2026-09-13. Extract retained
  at `agent-work/sources/model-priors/google-xai-others/epoch-ai-database-extract.md`.
- Epoch AI, estimation methodology and confidence scale,
  https://epoch.ai/data/ai-models-documentation/estimation
- Gemini Team, Gemini 1.0 technical report,
  https://storage.googleapis.com/deepmind-media/gemini/gemini_1_report.pdf
- Gemini Team, Gemini 1.5 technical report,
  https://storage.googleapis.com/deepmind-media/gemini/gemini_v1_5_report.pdf
- Gemini Team, Gemini 2.5 technical report,
  https://storage.googleapis.com/deepmind-media/gemini/gemini_v2_5_report.pdf
- Google DeepMind, Gemini 3 Pro model card,
  https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-3-Pro-Model-Card.pdf
- Google DeepMind, Gemini 3 Flash model card,
  https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-3-Flash-Model-Card.pdf
- Google for Developers, Gemini 1.5 Flash-8B is now production ready,
  https://developers.googleblog.com/en/gemini-15-flash-8b-is-now-generally-available-for-use/
- Gemini API pricing, https://ai.google.dev/gemini-api/docs/pricing
- xAI, Grok-2 weights and config, https://huggingface.co/xai-org/grok-2 and
  https://huggingface.co/xai-org/grok-2/discussions/24
- Artificial Analysis model pages, https://artificialanalysis.ai/models — see
  `agent-work/sources/model-priors/google-xai-others/pricing-and-throughput.md` for
  the specific pages and figures used.
- Published `config.json` files for DeepSeek-V3, Kimi-K2-Instruct,
  Qwen3-235B-A22B and GLM-4.5 on Hugging Face, used for the attention arithmetic.
