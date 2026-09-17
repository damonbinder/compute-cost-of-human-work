# OpenAI active-parameter priors: evidence review and proposals

*Created 2026-09-13 12:01.*

Scope: every OpenAI record in `../../models.csv` (3 records) and in `../../../AI Compute vs Human Time/dataset/models.csv` (56 records), 59 in total. Per-record proposals are in `openai-proposals.csv`; source extracts with provenance are in `agent-work/sources/model-priors/openai/`. Neither models.csv was touched.

## TL;DR

Most of the dataset's OpenAI priors survive the review, and several that were recorded as weak guesses turn out to have independent support that nobody had yet connected to them. Fourteen records move at all; **five groups move by more than 1.5x**: GPT-6 Astra and the OpenAI internal Navier-Stokes model up 2x to 200B, GPT-5.6 Sol up 1.5x to 150B, the three GPT-3.5 Turbo records up 1.7x to 12B, and the three GPT-4 Turbo records down 1.57x to 175B. GPT-4.5 moves up 1.33x to 800B and the o1 records up 1.2x to 60B, both below the flagging threshold.

Three findings drive most of this. First, a new calibrated black-box instrument exists—the Incompressible Knowledge Probes paper (arXiv 2604.24827, July 2026)—which estimates **total** parameters for 201 models including almost the whole OpenAI lineup; it is not a substitute for the active counts this dataset needs, but crossed with plausible sparsity ratios it independently reproduces several existing priors and resolves two conflicts. Second, Epoch AI publishes **no** parameter estimate for any OpenAI model after GPT-4o—every GPT-4.1, o-series, GPT-5.x and GPT-6 row in their database has a blank Parameters field—so the `epochai.substack.com/notes-on-gpt-5-training-compute` citation the dataset leans on is a prose aside, not a database entry. Third, the widely cited Microsoft MEDEC "leak" is not a leak: the authors state their sizes were "mined from public articles only" and that they "cannot vouch for their accuracy", and its GPT-4o ~200B is Epoch's own published estimate read back out of the literature. Citing both double-counts one source.

Next action: Damon reviews the fourteen proposed changes in `openai-proposals.csv`, decides the five flagged ones, and I apply the accepted set to both registries in one pass.

## Methods, and what each route is worth

Six routes carry real information about OpenAI model sizes. They are not equally good, and critically they do not all measure the same quantity—three constrain **active** parameters, which is what this dataset stores, and three constrain **total**, which is not.

| Route | Constrains | Typical error | Where it bites |
|---|---|---|---|
| Official disclosure | both | exact | gpt-oss only |
| Leak plus compute corroboration | both | 1.3x | GPT-4 only |
| Serving throughput and price | active | 2–3x | every served model |
| Training compute inverted through C = 6ND | active | 3–5x | GPT-4.5, GPT-5 |
| Factual-capacity probing (IKP) | total | 3x stated, 3x observed bias | 2023–2026 models |
| Benchmark-score regression | neither, reliably | >10x | discard |

**Official disclosure.** Only gpt-oss-120b and gpt-oss-20b. The model card gives 116.83B total / 5.13B active and 20.91B total / 3.61B active, with 128 experts and top-4 routing, and states that routed-expert and attention parameters count towards active while embeddings do not. Grade A. These two are also the most useful thing OpenAI has ever published for this exercise, because they pin OpenAI's own sparsity ratios in 2025: 22.8x and 5.8x. Every active estimate derived from a total estimate below depends on a sparsity assumption, and these are the only OpenAI-specific anchors for it.

**Leak plus corroboration.** SemiAnalysis's July 2023 GPT-4 account gives 1.8T total across 120 layers, 16 experts of ~111B, 2 routed per token, ~280B active per forward pass, 13T training tokens. A secondary summary of the same leak gives 1.76T / 220B. What makes this usable rather than gossip is that it closes against an independent quantity: 6 x 2.8e11 x 1.3e13 = 2.2e25 FLOP, matching Epoch's separately estimated ~2.1e25 training compute for GPT-4. Grade B, with 220–280B as the honest spread.

**Serving throughput and price.** Epoch's inference-economics model decomposes a forward pass into arithmetic, memory-read, network and latency terms and optimizes over parallelism and batch size; the batch size that matters is b* = p·C/(B·2 FLOP), the point at which parameter-read time equals arithmetic time. Read backwards, serial output speed at a serving-cost-minimizing batch bounds the parameters that must be read per token, and price per token bounds the FLOPs that must be paid for. Assumptions that move the answer: batch size (assumed at or near b*), numerical precision (FP8 or 4-bit quantization each cut memory traffic against a 16-bit baseline), tensor and pipeline parallelism layout, speculative decoding (which raises serial speed without raising parameters and is not observable from outside), and hardware generation. Epoch states 2x+ uncertainty from these; across a hardware generation I would use 3x.

Two facts discipline any use of price. OpenAI cut o3's price 80% on 2025-06-10 with the note "We optimized our inference stack that serves o3. Same exact model—just cheaper", which puts roughly a 5x margin overhang on reasoning-model list prices. And prices compared across years are confounded by hardware, roughly 2x per generation. So I apply square-root shrinkage to price ratios throughout: a 4x price gap is read as a 2x size gap. That is a deliberate choice, and it is the main reason Sol and Astra move less than their headline prices would suggest.

**Training compute inverted.** For GPT-4.5 and GPT-5, Epoch publishes training-compute estimates (3.8e26 "Likely", 6.6e25 "Speculative"). C = 6ND gives active parameters given a token count, but modern models are overtrained by wildly varying amounts—GPT-4 ran at D/N = 46, current small models run above 1000—so the token assumption dominates. Useful as a cross-check, not as a primary.

**Factual-capacity probing.** The IKP paper calibrates a log-linear map from factual-recall accuracy to parameter count on 93 open-weight models from 135M to 1.6T, R² = 0.910, leave-one-out median fold error 1.48x, 90% interval ~3.2x each way. It reports **total**, not active: the authors state total predicts MoE knowledge better than active (R² 0.67 against 0.41), and the two OpenAI models with published architectures confirm it—IKP reads gpt-oss-120b at 106B against 116.83B total and 5.13B active, and gpt-oss-20b at 16B against 20.91B total and 3.61B active.

Its calibration failure matters as much as its successes. GPT-4 is the only OpenAI model in the table with an independent total figure, and IKP reads it at 622B against the leaked 1.8T—low by 2.9x. It also ranks gpt-4-turbo above gpt-4, contradicting Epoch's "maybe smaller/sparser than GPT-4". Both are symptoms of the instrument tracking knowledge-per-parameter, which rises with training-data scale, as much as size. I therefore use IKP for within-era comparisons and for crossing into active counts via a sparsity assumption, never for cross-era ordering, and I treat its readings as biased low for pre-2024 models. Grade C on its own; grade B when it converges with serving evidence.

**Benchmark-score regression.** The cbowdon post regresses log10(parameters) on benchmark scores fit to open models. It returns GPT-4o at 26B and GPT-5 high at 635B—an ordering the serving data contradicts, since the two are within a factor of two on output speed. Benchmark score is driven by post-training and reasoning effort, which the regression only crudely adjusts for with a "very rough ballpark" 0.4x reasoning factor on 80% explained variance. Discarded except as a tiebreak.

### What does not count as evidence

The MEDEC paper is a literature compilation carrying an explicit disclaimer, and its GPT-4o ~200B and GPT-4o-mini ~8B are the same numbers already in the dataset from Epoch and from small-model priors. Only its o1-preview ~300B and o1-mini ~100B are not traceable to prior public estimates, and those still carry the disclaimer. Microsoft's CODEFUSION 20B for gpt-3.5-turbo comes from a paper that was withdrawn from arXiv; Epoch still carries it at "Likely" while simultaneously recording on its davinci-002 row that the paper "was reportedly retracted because the authors did not know the parameter count", an internal inconsistency worth knowing before leaning on it.

## Per-model findings

Sections group records that share an architecture identity. Every one of the 59 records appears in `openai-proposals.csv` with its own row.

### GPT-3 and davinci (175B): no change, grade A to C

`gpt-3-davinci-175b` is exact: GPT-3 Table D.1 gives 174,600 million, dense, so active equals total. `text-davinci-002` rests on the InstructGPT paper's "We train three model sizes (1.3B, 6B, and 175B parameters)"; the residual uncertainty is identity rather than size, so grade B.

`davinci-002-metr` and `chatgpt-gpt35-2022` are weaker. Epoch's davinci-002 row is "Speculative" with "Parameter count may be 175B". One signal cuts against it that I have not seen raised: OpenAI priced the 2023 davinci-002 endpoint at $2.00 per Mtok against the legacy davinci endpoint's $20.00, a tenfold drop for a model presented as a GPT-3-class base replacement. Some of that is 2023 serving improvements; probably not all of it. I hold the central at 175B, because METR uses the alias precisely as its GPT-3 data point, and drop the low bound to 40B to carry the anomaly. That is the `davinci-002-metr` bound; `chatgpt-gpt35-2022` has its own window and its own floor, in the section that follows.

<a id="chatgpt-backend-2022-23"></a>

### The ChatGPT backend, November 2022 to February 2023: low bound UP to 60B, grade C

Added 2026-09-16, after the studies sitting on `chatgpt-gpt35-2022` were dated against the product's backend history.

ChatGPT ran a dense davinci-lineage GPT-3.5 from launch until February 2023. The turbo-class model entered the product as an opt-in Plus alpha on 9 February 2023 and became the Plus default on 13 February, the same day the free plan got a model change framed as capacity relief—"performance improvements to the ChatGPT model on our free plan in order to serve more users", in the [ChatGPT release notes](https://chatgpt.tech.blog/2023/02/22/chatgpt-release-notes/) as reproduced on 22 February 2023. Two backend snapshot names developers recovered in early February 2023, `text-chat-davinci-002-20221122` and `text-chat-davinci-002-20230126`, put both the launch backend and the [30 January 2023 factuality-and-math update](https://www.searchenginejournal.com/chatgpt-update-improved-math-capabilities/478057/) inside the davinci-002 lineage; the names and their recovery are in [0xdevalias's notes](https://github.com/0xdevalias/poc-chatgpt/blob/main/leaked-model.md).

OpenAI's [1 March 2023 API announcement](https://openai.com/index/introducing-chatgpt-and-whisper-apis/) that `gpt-3.5-turbo` "is the same model used in the ChatGPT product" describes the post-13-February product and is not retroactive. The same post dates its 90% cost reduction "since December", which makes December the expensive baseline; a reading in which December's ChatGPT was already the cheap model leaves that figure with nothing to measure against.

**The low bound goes from 12B to 60B, and the record is scoped to 30 November 2022 through 12 February 2023.** The 12B floor was imported from the turbo evidence base, and none of that evidence bears on this window: the d_model = 4096 measurement is on the 0125 snapshot accessed in February 2024, and the withdrawn CODEFUSION 20B is on the 2023 API model. The floor this window does support comes from the cost reduction. If the 90% cut "since December" were entirely size, the December model scales to 120B active against the 12B turbo central and to 70B against the 7B dense reading. Both land below 175B, which is why 60B is the floor and why 175B stays a lineage-based central rather than being promoted on the cost argument. The central stays 175B and the high bound stays 200B, so no row's `compute_flops` or `compute_flops_high` moves.

No row sits on the post-switch backend. The patient-message sessions are 22–23 December 2022. Noy and Zhang's field window runs 27 January to 24 February 2023 and straddles the flip, but its ChatGPT answers were produced by the authors rather than by participants, and 51 of the 62 unique answers were already in front of a grader before 13 February, the earliest on 6 February—so the answers the rows price were generated on this record's backend. `research/noy-zhang/noy-zhang.md` carries the grading dates. The one open case is `writing-chatgpt-gec-conll14-17`, whose study does not date its ChatGPT sessions at all.

Contemporary HumanEval samples under the two ChatGPT web slugs are why the February cheapness reads as a different model rather than a compressed copy of the December one: [saschaschramm/chatgpt](https://github.com/saschaschramm/chatgpt) measured 56.10% pass@1 under `text-davinci-002-render` on 3 December 2022 against 70.12% under the Turbo slug `text-davinci-002-render-sha` on 19 February 2023, with `gpt-3.5-turbo-0301` later at 74.39%.

### GPT-3.5 Turbo (7B): UP to 12B, grade C, flagged

Three sources conflict, and they reconcile under one architecture.

The softmax-bottleneck paper measures d_model = 4096 for gpt-3.5-turbo, recovering it from the rank of API logit outputs. That is a measurement, and it is the hardest fact anyone has about this model. The authors then infer "around 7 billion" parameters "based on the fact that most known transformer-based LLMs with embedding size 4,096 have approximately 7 billion parameters"—and flag the exception themselves, that MoE architectures "tend to have many more parameters per embedding dimension". The 7B figure is an inference conditional on density, which the measurement does not establish.

Microsoft's withdrawn CODEFUSION table says 20B, carried by Epoch at "Likely". IKP reads 246B total. An MoE with d_model = 4096, roughly 10–25B active and a couple of hundred billion total satisfies all three at once, and is an architecture OpenAI demonstrably builds. I propose 12B, the geometric midpoint of the dense reading and the CODEFUSION figure, range 6–25B. This applies to the 0125, 1106 and Instruct records; the Instruct record already retains 20B and 175B as scenarios, and the 20B scenario becomes the upper part of the new central range rather than a separate branch.

### GPT-4, original (275B): no change, grade B

Six records share this identity: `gpt-4-0314`, `gpt-4-0613`, `gpt-4-base-2023-report`, `gpt-4-2023-03-01-internal`, `gpt-4-bar-exam-preview`, `gpt-4-original-unspecified`. The SemiAnalysis 280B and the secondary 220B bracket the dataset's 275B, and the compute closure described above makes this the best-evidenced non-disclosed number in the set. Range 200–350B.

### GPT-4 Turbo (275B): DOWN to 175B, grade C, flagged

Epoch's note on both Turbo snapshots reads "Not known. Maybe smaller/sparser than GPT-4." The serving evidence agrees in direction: $10/$30 per Mtok against GPT-4 original's $30/$60, output price halved eight months later, and Epoch's own frontier-size article uses Turbo's 55 tok/s as the stepping stone between GPT-4 and a GPT-4o it puts at an eighth of GPT-4's size.

This is the one proposal I would describe as a judgment call rather than a finding. The geometric midpoint between GPT-4's 280B and GPT-4o's 50B is 118B, which I think overshoots. IKP actively contradicts the direction, reading gpt-4-turbo at 1.05T against gpt-4 at 622B—but that is exactly the cross-era comparison the instrument is worst at. Keeping 275B for family coherence is defensible and costs a factor of 1.57 on three records.

### GPT-4o and GPT-4o-mini: no change, grade B and C

Epoch's 200B total for GPT-4o comes from serving economics: 100–150 tok/s at $10/Mtok output against GPT-4 Turbo's 55 tok/s at $30/Mtok, giving "around an eighth of the size of GPT-4", with the estimate able to be "off by a factor of 2". Their energy article then writes "Pessimistically taking the high estimate of total parameters, and assuming ¼ are activated at a time suggests 100 billion active parameters". Note the word: 100B active is the conservative case built on the 400B tail. The central reading is 200B x ¼ = 50B, which is what the dataset carries and what the dataset's note correctly describes. IKP's 392B total at 2024-era ~8x sparsity lands in the same place.

For GPT-4o-mini, IKP reads 92B total, which at ~10x sparsity gives ~9B active. The existing 8B prior, recorded as a "weak small-model size prior", now has an independent line of support it did not have. Same for `gpt-4.1-nano` (IKP 71B total) and `gpt-5-nano` (IKP 23B total). No numbers change; the basis improves.

`gpt-4o-audio-preview-2024-10-01` keeps the 50B backbone and its separately stored Whisper-large-proxy acoustic encoder.

### GPT-4.5 (600B): UP to 800B, grade B

Three routes, all landing at or above the current value. Lambert's 5–7T total and ~600B active from "5X parameters + 2X dataset size = 10X compute", with his own "big error bars" caveat. Epoch's training compute of 3.8e26 FLOP at "Likely", from 187M H100-hours at 20–40% utilization: inverted at GPT-4's overtraining ratio it gives 1.2T active, at D/N = 100 it gives 800B. And the price, $75/$150 per Mtok, 15x GPT-4o's output price nine months later and the highest OpenAI has ever charged, with API access withdrawn on 2025-07-14 rather than repriced. I propose 800B, range 400B–1.6T. Below the flagging threshold at 1.33x.

### GPT-4.1 and GPT-4.1-mini: no change, grade C

IKP puts GPT-4.1 at 2.2T total, above every other pre-GPT-5.5 OpenAI model. GPT-4.1 is nonetheless priced below GPT-4o at comparable speed, which bounds its active count at or below GPT-4o's. Both hold if GPT-4.1 is sparser: more total, similar active. The dataset stores active, so the serving evidence governs and 50B stands.

GPT-4.1-mini is the nicest convergence in the set. Its prior came from a reported accuracy comparison with Mistral Small 24B, which establishes nothing about architecture. IKP independently reads 501B total, which at ~20x 2025-era sparsity gives ~25B active. I round 24B to 25B, a 1.04x change of no consequence, but the basis moves from "weak size prior" to two independent lines agreeing.

### o1 and o1-preview (50B): UP to 60B, grade C

Two signals point above the GPT-4o transfer, and both are weak. o1 launched at $15/$60 per Mtok, six times GPT-4o's output price; and IKP reads 1.3T total against GPT-4o's 392B. The price signal is undercut by OpenAI's own o3 repricing, which showed reasoning-model list prices carrying roughly 5x margin. MEDEC's o1-preview ~300B is the only figure in that paper not traceable to a prior public estimate, but it carries the blanket disclaimer. Artificial Analysis publishes no throughput for o1, so the route that would settle this is unavailable. 60B, range 25–200B, 1.2x and below the threshold.

### The mini reasoning models (20B): no change, grade B

Epoch's database note, attached verbatim to o1-mini, o3-mini and o4-mini alike: "we suspect total parameter count around 60B-120B, active parameters around 10B-30B. Given these models are served at 150-200 tok/s, at $4.40/Mtok output, inference economics suggests...". This is Epoch applying their own published method and stating an **active** figure, which almost nothing else in the OpenAI set does. Measured throughput corroborates: o3-mini at 209 tok/s, o4-mini high at 136. The dataset's 20B is the centre of their range. I raise the confidence grade to B; the number is unchanged. `gpt-5-mini` inherits this by transfer and is separately supported by IKP's 93B total.

### o3 (50B): no change, grade C

o3 runs at 107 tok/s median and 152 on OpenAI's own API, comparable to GPT-4o, and OpenAI repriced it to $2/$8—below GPT-4o's $10 output—while stating the model was unchanged. A sustainable price below GPT-4o's bounds o3 at GPT-4o scale or smaller. IKP's 2.1T is a total reading and consistent with a sparser model at the same active size. The early Codeforces checkpoint inherits this.

### The GPT-5 family (100B): no change, grade B for GPT-5, C for the rest

Epoch's ~100B active for GPT-5 comes from price, speed, and a stated comparison to Grok 2's 115B active. Two checks support it. Training compute of 6.6e25 FLOP with their assumed "at least 30 trillion tokens, possibly several times more" gives 167B at 30T and 83B at 60T. Throughput: 76 tok/s against GPT-4o's 124, roughly 1.6x slower on better hardware. IKP's 1.8T total implies ~18x sparsity at 100B active, in line with gpt-oss-120b's disclosed 22.8x.

The point releases are the interesting part. IKP reads GPT-5.1 at 634B, GPT-5.2 at 571B, GPT-5.3 at 1.1T and GPT-5.4 at 1.1T—all **below** GPT-5's own 1.8T—and the paper reads this literally, concluding the point releases share a similar parameter budget while GPT-5.5 is the genuine scale-up. Since they are also priced at or near GPT-5's level, there is no basis to move any of `gpt-5-chat`, `gpt-5-codex`, `gpt-5.1`, `gpt-5.2`, `gpt-5-3-codex` or `gpt-5.4` off the shared prior. They stay at 100B with range 40–250B.

### GPT-5.6 Sol (100B): UP to 150B, grade C, flagged

OpenAI's own model page says Sol "roughly corresponds to the unsuffixed model tier used in earlier GPT-5 families", which fixes the tier and licenses the GPT-5 anchor. The serving ladder then argues the tier itself grew: $4/$20 per Mtok against GPT-5's $1.25/$10, twice the output price eleven months later on better hardware, and 60 tok/s against GPT-5's 76. Square-root shrinkage on the price ratio gives 100B x √2 = 141B. I propose 150B, range 60–400B. This sits exactly on the flagging threshold and is the change I hold most loosely of the five.

### GPT-5.6 Luna (8B): no change, grade C

OpenAI's model page states Luna "roughly corresponds to the nano model tier used in earlier GPT-5 families" and prices it at $0.20/$1.20, matching GPT-5.4 nano's $0.20/$1.25. So the tier attribution in the current record is OpenAI's own statement rather than an inference, which is stronger than the note gives it credit for.

Two considerations pull against each other and cancel. The nano tier repriced upward between GPT-5 nano ($0.05/$0.40) and the 2026 nano models, which would argue for growth—but Luna also carries a 1.05M context window against GPT-5 nano's 400K, and long-context KV traffic raises serving cost independently of parameters. Against that, IKP reads GPT-5.4 nano, Luna's price-identical sibling, at 9.9B **total**, the smallest OpenAI entry in its whole table, which argues the nano tier did not grow and might even imply an active count below 8B. Holding at 8B, range 3–20B.

### GPT-6 Astra (100B): UP to 200B, grade C, flagged

Epoch's model page lists Parameters: Unknown and Training compute: Unknown for a model released 2026-09-03. There is no disclosure, no leak of a size, and no academic estimate—the IKP paper predates Astra.

The serving ladder is the only usable evidence, and it happens to be unusually well suited here. Astra is $10/$50 per Mtok, 2.5x GPT-5.6 Sol's $4/$20, and is the slowest model in OpenAI's lineup at 50–54 tok/s across every reasoning-effort setting, against Sol's 60 and GPT-5's 76. Square-root shrinkage on the price ratio against the GPT-5 anchor gives 100B x √5 = 224B; I round to 200B, range 70–600B.

**On recurrent depth.** The Information reported on 2026-09-01, from a single anonymous source, that OpenAI incorporated a limited form of recurrent depth—a looped transformer—into Astra. OpenAI has not confirmed it. The only near-official statement is Jakub Pachocki's, on X, that Astra's computation-graph depth is "within a factor of two of GPT-4", offered as evidence that Astra is not a "neuralese" model; Transformer reports that when it asked for more, "OpenAI directed Transformer back to Pachocki's tweet". Astra's system card confirms the consequence without the mechanism, stating Astra is less monitorable through chain of thought and can solve harder tasks without verbalized reasoning.

What recurrence would do to a 2-x-active-parameters coefficient is multiply it, because looping buys compute without buying parameters. Published reference points, none of them Astra: Nanbeige4.2 applies a 22-block stack twice for 2x; Ouro-Thinking applies 48 blocks four times for 4x; Huginn uses ~32 passes on 3.5B parameters for roughly 14x in FLOP-equivalent terms; SMELT applies the middle half of its blocks twice while narrowing the hidden dimension to hold compute fixed, which is deliberately FLOP-neutral. One correction worth recording: several secondary write-ups attribute the SMELT description to Astra. It describes the SMELT paper.

The reason I am comfortable proposing a number anyway is that price per token and serial output speed both respond to total FLOPs and memory traffic per emitted token, so they absorb the loop multiplier automatically. It does not matter whether Astra's extra compute comes from more parameters or more passes over the same parameters—the serving ladder measures the product, which is the quantity the coefficient stands in for. The record's existing note, that recurrent depth "would multiply the per-token coefficient by an undisclosed number of passes", is right about the mechanism but implies the multiplier is unbounded from outside. It is not: the price and speed data bound it.

A separate point the record should probably carry: Astra emits substantially fewer output tokens per task than a comparably capable verbalized-reasoning model, which moves total task FLOPs in the opposite direction from the per-token coefficient.

### OpenAI internal Navier-Stokes model (100B): UP to 200B, grade C, flagged

Never released, no price, no throughput, no disclosure. The record ties its assumptions to `gpt-6-astra`, so it moves with Astra. I hold it at parity rather than above, because "significantly more capable than GPT-6 Astra" is a post-training and scaffolding claim as much as a scale claim, and widen the upper bound to 800B instead.

### gpt-oss: no change, grade A

The only disclosed numbers. 5.13B and 3.61B active; the dataset's 5.1B and 3.6B are the rounded forms and its notes already carry the exact figures.

### Codex research models and the non-LM records: no change, grade A

`codex-12b-research` and `codex-300m-research` are stated in the Codex paper and recorded by Epoch; `codex-2-5b-research` comes from the same size sweep. All dense, so total equals active. `whisper_tiny_en`, `whisper_large_v2`, `dactyl-adr-xxl-vision` and `openai-five-finals-2019` set active_parameters to not_applicable by design—encoder/decoder or RL-policy records with no token coefficient—and nothing about them is in question.

## Where the evidence conflicts, and what I weighted

**IKP totals against Epoch totals for GPT-4o-era models.** IKP reads GPT-4o at 392B total and GPT-4.1 at 2.2T; Epoch reads GPT-4o at 200B. I weight Epoch for GPT-4o because its route constrains the memory traffic per token directly, and I weight neither heavily for GPT-4.1 because the serving evidence pins active independently of whatever the total is. The reconciliation that makes both sets of numbers livable is rising sparsity: OpenAI's own disclosed 22.8x for gpt-oss-120b is far above GPT-4's 6.4x, and a 2T-total model at 20x sparsity has 100B active.

**IKP ordering against Epoch's qualitative ordering in the GPT-4 era.** IKP puts gpt-4-turbo above gpt-4 and reads gpt-4 at 0.35x its leaked total. Epoch says Turbo is "maybe smaller/sparser". I weight Epoch, because IKP's own calibration miss on the one model with a known answer is in exactly this era and direction.

**Dense 7B against CODEFUSION 20B for gpt-3.5-turbo.** I weight the d_model = 4096 measurement as fact and the 7B as a conditional inference, treat the withdrawn 20B as weak but not worthless given Epoch still carries it, and take a midpoint that an MoE architecture makes consistent with both plus IKP's 246B total.

**Epoch's own 100B against its own 50B for GPT-4o.** Not really a conflict once read carefully: 100B is the explicitly "pessimistic" case on the 400B tail, 50B is the central. The dataset already has this right, and it is worth not "fixing" it later on a careless reading of the energy article.

## What I looked for and did not find

- Any OpenAI disclosure of parameter counts for any model other than gpt-oss, GPT-3, Codex and Whisper.
- Any Epoch AI parameter estimate, in the database or in prose, for GPT-4.1, GPT-4.5, the o-series full models, or anything in the GPT-5 or GPT-6 families. The database fields are blank and the model pages say Unknown.
- Any credible leak of GPT-4.5, GPT-5 or GPT-6 architecture comparable to the SemiAnalysis GPT-4 account. Nothing exists.
- Any energy-consumption analysis independent of Epoch's. The published ones reuse Epoch's 200B GPT-4o figure.
- Any distillation or academic paper stating an OpenAI model's size from privileged access. The academic estimates are all black-box: the softmax-bottleneck hidden-size measurement, and the IKP factual-capacity instrument.
- Any statement from OpenAI on Astra's loop count, loop scope, or whether its recurrence is FLOP-neutral. Only Pachocki's factor-of-two depth remark.
