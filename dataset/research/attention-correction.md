# Attention in compute_flops

`compute_flops` is the best estimate of total FLOPs, so it carries the attention
term rather than leaving it alongside. This note holds the recipe, the attention
shape assumed for every model, the mean attended context assumed for every
corrected row, and the separate treatment of the METR rows, whose token counter
is inclusive of cache reads and whose own billing says none were served. It
replaces the convention under which the `params_tokens` rows priced only
projection and feedforward matrices.

The script is `research/attention-correction/apply_attention.py`, with the
architecture table in `research/attention-correction/architectures.py`. Its
per-row output is `agent-work/derived/attention-correction/corrections.csv`.

## The recipe

A decoder-only transformer with `L` layers, `n_q` query heads of width `d_head`,
and `d_attn = n_q · d_head` spends, per query position attending over `N_ctx`
keys and per layer, one length-`d_head` dot product per head per key in `QK^T`
and the same count again in `A·V`. At two FLOPs per multiply-add,

```
attention FLOPs per processed position = 4 · L · d_attn · N_ctx
parameter FLOPs per processed position = 2 · N_active
attention_ratio  r                     = 2 · L · d_attn · N_ctx / N_active
```

This is the forward third of PaLM's `12·L·H·Q·T`
([Chowdhery et al. (2022)](https://arxiv.org/pdf/2204.02311), §2).
[Kaplan et al. (2020)](https://ar5iv.labs.arxiv.org/html/2001.08361) Table 1
gives `2·n_layer·n_ctx·d_attn`, which counts one of the two matmuls and so
halves the term; PaLM's is the one used here. For a dense transformer with the
standard 4× MLP, non-embedding parameters are about `12·L·d_model²` and
`d_attn = d_model`, which collapses the ratio to `r ≈ N_ctx / (6 · d_model)`.

Three things follow that the previous convention got wrong.

**The width is the query width, not the model width.** `d_attn` is `n_q · d_head`.
It equals `d_model` for Llama-style models and does not in general: `gpt-oss-120b`
is 2,880 wide with 64 heads of 64, so `d_attn = 4096`, and DeepSeek-V3's MLA
carries 128 heads of 192-wide query/key and 128-wide value against a 7,168-wide
model, an effective 20,480.

**An MoE model keeps its full `L · d_attn` while `N_active` is small.** The ratio
has `N_active` in the denominator and the attention shape in the numerator, and
mixture-of-experts routing cuts the first without touching the second. On the
2024 to mid-2025 full-attention MoEs a dense bracket sized to the active count
understates `r` by 1.6–3.0×. It does not follow that a 2026 model is in that
mode, and the shapes section below sets out why not.

**A cache read contributes attention but not a weights pass.** Cached prefix
tokens are keys, not queries: they raise the context that every position
appended after them attends over, and they take no forward pass through the
weights. So the correct accounting counts attention for cached-prefix positions
that were attended over, and counts the parameter term only on positions that
were actually processed.

Writing `P` for processed positions and `N̄` for their mean attended context, a
row's compute is

```
compute_flops = 2 · N_active · P  +  4 · L · d_attn · N̄ · P
```

For a `params_tokens` row the counted tokens are the processed positions, so
this is the previous value times `(1 + r)`. For a row whose counted total
includes cache reads, `P` is the counted total itself where the source's own
billing shows the prefix was recomputed; see the METR section.

`attention_context` records `N̄` and `attention_ratio` records `r`, so any reader
can divide the term back out.

<a id="model-architectures"></a>

## Model architectures

`models.csv` carries `attention_layers` (`L`), `attention_width` (`d_attn`) and
`attention_basis`. `L` counts only layers whose attention cost grows with
context: sliding-window, banded and linear-attention layers are excluded,
because their per-position cost is bounded by the window or by the recurrent
state.

**`attention_basis = reported`** covers 88 models whose configuration is public.
The parameter counts for these already cite the configuration or model card that
fixes the shape; the values are read from the same place. The cases where the
shape is not simply `L` full layers at `d_model` wide:

| Model | L | d_attn | Why |
|---|---:|---:|---|
| DeepSeek-V3, -V3-0324, -V3.2, R1, R1-0528, Prover-V2 | 61 | 20480 | MLA: 128 heads of 192-wide query/key and 128-wide value, against `d_model` 7168 |
| Kimi K2, K2.5, K2.6 | 61 | 10240 | MLA: 64 heads at the same latent shape |
| Kimi K3 | 24 | 7168 | 69 of 93 layers are KDA linear attention, per `research/apex-agents.md` |
| gpt-oss-120b | 18 | 4096 | half of 36 layers run a 128-token banded window; 64 heads of 64 |
| gpt-oss-20b | 12 | 4096 | half of 24 layers banded; same head shape |
| Gemma 2 9B, 2 27B | 21, 23 | 4096 | alternating local and global attention, global layers only |
| Gemma 3 27B | 10 | 4096 | 5:1 local-to-global interleave over 62 layers |
| Llama 4 Scout, Maverick | 12 | 5120 | chunked attention on three layers in four |
| PaLM 540B, Minerva 62B | 118, 64 | 12288, 8192 | multi-query attention, `n_q · d_head` |

DeepSeek-V3.2's sparse attention reads a fixed 2,048 selected tokens rather than
the whole prefix, so its three rows are an upper bound. The MLA figures are the
prefill form; the absorbed decode form is more expensive still.

**`attention_basis = estimated`** covers every model whose architecture is not
disclosed, which is all of the closed frontier models and so most of the rows.
The shape has to be consistent with the active-parameter prior that
`active_parameters` already carries, and there is no total-parameter estimate in
the file to bracket against. A dense decoder has about `12 · L · d²`
non-embedding parameters, and large models sit near an aspect ratio
`d = 128 · L` — GPT-3 at 96/12288, Llama 3.1 70B at 80/8192, Llama 3.1 405B at
126/16384. Solving the two together gives a dense layer count

```
L_dense = (N_active / 196608)^(1/3)          d_attn = 128 · L_dense
```

which at 1e11 active returns 80 layers and 10,240 wide.

**That dense count is an upper bound for a 2026 frontier model, not a central
estimate.** Tested against the 88 models whose configuration is public, the rule
reproduces dense decoders to within 3% — it was fitted to them — and on
mixture-of-experts models it is bimodal. The 2024 to mid-2025 full-attention MoEs
exceed it by 1.6 to 3.0×: DeepSeek V3, Kimi K2, Qwen3-235B, GLM-4.7. Every
frontier-scale architecture disclosed since March 2025 falls below it, because
each moves some layers to a local window or a linear state: Gemma 3 at 0.12× on a
5:1 local-to-global interleave, Llama 4 at 0.25× on chunked attention in three
layers of four, gpt-oss at 0.66× and 0.55× on a 128-token banded window over
alternating layers, DeepSeek V3.2 on a fixed 2,048-token sparse selection, and
Kimi K3 at 0.21× with 69 of 93 layers on KDA linear attention. Nothing disclosed
after mid-2025 sits in the upper mode, and the largest-total disclosed model in
the collection, Kimi K3 at 2.78T, is the lowest of all. The audit in
`agent-work/reviews/attention-audit.md` works the comparison through model by
model.

**So the estimated shape takes a per-family share of the dense layer count.** The
share multiplies `L` and not `d_attn`, because removing layers from the
context-growing count is the mechanism every disclosed reduction uses; the query
width is untouched. `attention_basis` stays `estimated`, because none of this is
a disclosure.

| Family | Models | Share of `L_dense` | The evidence it rests on |
|---|---:|---:|---|
| OpenAI | 54 | 0.65 | gpt-oss, OpenAI's only architectural disclosure: a 128-token banded window on half the layers, 64 heads of 64 against a 2,880-wide model, at 0.66× and 0.55× the dense rule |
| Anthropic | 25 | 0.70 | Nothing disclosed — no parameter count, layer count or hidden dimension has ever been published. The share is the midpoint of the disclosed 2026 designs, held slightly above OpenAI's because there is no own-family evidence to move it further |
| Google | 26 | 0.25 | Gemma 2 at a 1:1 local-to-global interleave and Gemma 3 at 5:1 with a 1,024-token window are the Gemini-derived open releases, and a served 1M-token window is hard to reconcile with full attention on every layer |
| xAI | 7 | 1.00 | Grok-2's released `config.json` is 64 layers at 8,192 against 115B active, which is the dense rule to within 1%. No Grok 3 or later disclosure, so the share stays at the rule |
| Other closed | 23 | 0.70 | GLM, Qwen-Max, Kimi, MiniMax, Muse and the rest have sibling open weights showing the same bimodality — GLM-4.7 2.96×, Kimi K2 1.64×, Qwen3-235B 2.59×, Kimi K3 0.21× — resolving downward through 2026 |

The small dense research models in the registry — the BabyLM and BabyBERTa runs,
the FAIR negotiator, Pegasus, RetroDFMR — keep the plain rule, because the rule
is accurate on dense architectures and the frontier argument does not reach them.

The argument on the other side is real and is not quantified here. A closed model
at 100B active is presumed to be a large MoE, and its attention stack belongs to a
multi-trillion-parameter model rather than to a 100B dense one, which the
disclosed full-attention MoEs put at 1.6–3.0×. It is outweighed by the
local-attention evidence, which every 2026 disclosure supports and which reaches
the same models. In the same direction as the shares above,
[MInference 1.0 (2024)](https://arxiv.org/pdf/2407.02490) removes 95% of
long-context prefill attention at comparable accuracy, so the dense recipe is in
any case an upper bound on what a tuned serving stack spends.

Applying the shares moved 128 estimated models and 1,304 rows, at a median factor
of 0.90 on `compute_flops` and p10 0.75. On the primary set — inference rows at
`match` or better — the median FLOPs per human-second moves from 4.72e12 to
4.02e12 and the share above a 1e13 brain anchor from 33.1% to 29.7%. The script is
`research/attention-correction/apply_audit.py` and its per-row output is
`agent-work/derived/attention-correction/audit-corrections.csv`.


Providers charge cached input at 5–10% of fresh input while the arithmetic here
puts a cached token's marginal compute well under 1% of a fresh token's. That
gap is memory bandwidth, not FLOPs, so cache prices cannot be inverted into a
FLOP correction.

<a id="mean-attended-context"></a>

## The mean attended context

`attention_context` is `N̄`, the mean context the processed positions attended
over. It is set in order of precedence, and a lower tier is used only where no
higher one is available.

1. **The run's own per-call or per-turn records**, where the source publishes
   them.
2. **A cache-implied mean prefix**, `N̄ = alpha · n`, from a cached against
   uncached token split — the run's own where it publishes one, otherwise a
   same-model run in a comparable agentic harness that does.
3. **Half the counted tokens**.

The 200,000 cap applies to the result of every tier, including a measured one.

**A transferred estimate is preferred to falling straight to the cap.** Where a
row would otherwise have no context at all, a tier-2 figure rests on a same-model
run's measured cache structure and the bare cap rests on nothing. The transfer
carries its own error and the tables below name what was transferred from where,
so a reader can see how far each value travelled. The cap still binds the
result.

**From the run's own records, where one measures or derives a context.** These
are the per-point values. `reas-navier-stokes-openai` is the one that exceeds the
cap and keeps its value, because it is a single published reasoning dialog rather
than a compacting agent harness.

| Row | N̄ | Basis |
|---|---:|---|
| `game-factorio-gpt6astra`, `game-portal-gpt6astra` | 130000 | measured mean prefix in both Astra runs |
| `reas-navier-stokes-openai` | 247500 | dialog geometry in `research/navier-stokes-openai.md` |
| `reas-lean-textbook-algcomb-opus45` | 33410 | `RMS² / (2 · mean)` over the run's 1,645,274 full-prefix calls, mean prompt 50,554 and RMS 58,113 |
| `reas-flt-lean-anthropic-internal` | 100000 | the note's central for a Claude Code agent session |
| `reas-zeta-zeros-anthropic-internal` | 100000 | transferred from the Fermat row's central, the same Claude Code agent harness |
| `agen-lumen-d1…d5-gemini31pro` | 1984–6943 | each phase's mean input length per call, from `research/lumen.md` |
| `reas-cf-o3` | 9000 | 1,162 generated candidates share the counted total |
| `lang-lait-novel-opening-gpt54` | 9000 | 1,449 agent jobs over 15 runs |
| `lang-book-coherence-gpt4-inc`, `-hier` | 1382, 982 | 98 annotation records share the counted total |
| `agen-ahc058-ale-agent` | 9000 | ALE-Bench measured one-shot per-call cadence |
| `reas-lean-minif2f-deepseekprov2-cot32` | 3495 | 32 independent proof samples |
| `reas-math-minerva62b-majority256` | 155 | 256 sampled solutions |

The last six are work units that are `k` independent sub-runs rather than one
trajectory. Half the counted tokens is not a context for those: the counted
total is `k` trajectories, and the context is half the per-sub-run share.

**From a per-source mean, where the source gives turn or call counts but not
per-row logs.**

| source_dataset | N̄ | Basis |
|---|---:|---|
| GDPval, GDPval / GDPval-AA v2, GDPval gold subset | 108500 | 1.443e9 gross input over 220 tasks at Artificial Analysis's 60.47 mean turns; transferred to the invoice-derived original GDPval rows |
| GAIA, HAL agent traces | 12000 | measured per-call prefixes of 3.6k–29.7k |
| ALE-Bench leaderboard | 9000 | 2,727 input plus about 12k output, one-shot |
| BALROG | 3000 | bounded history window on a 424-token shared prefix |
| ARC-AGI-3 Semi-Private leaderboard | 135000 | 300 session records, 125k–146k per call |
| APEX-Agents | 90731 | input tokens per run over 40 calls |
| BankerToolBench | 118004 | measured 39.5k and 14.2k prefixes with the donor cadence |
| TextQuests | 45000 | the prefix re-read on each of ~12,500 calls averages 40k–51k |
| ARTEMIS | 50000 | the note brackets the mean prefix at 20k–100k |

<a id="cache-implied-context"></a>

### The cache-implied mean prefix

Cache reads are the sum of the per-call prefixes. On call `i` an append-only
harness re-reads `prefix_i` tokens from cache and processes `n_i` new ones, so
the run's cache-read total is `C = Σ prefix_i` while its counted total, which
excludes cache reads, is `P = Σ n_i`. With the new tokens per call roughly
constant at `n`, the call count is `P / n` and

```
N̄ = C / (P / n) = alpha · n            alpha = C / P
```

`alpha` is the cache-read multiple the split gives, and `n` is 2,800 throughout
— the median over the sixteen Terminal-Bench 2.1 official submissions, the same
constant the METR trajectory length below uses. Inverting the relation consistently on
those sixteen gives `n` from 1,758 to 19,121, with 336,382 on the degenerate
`gpt-5.5` Codex run. `N̄` is then held at `P / 2` where the cache-implied figure
exceeds it, since a prefix cannot average more than half a dialog processed
once, and at 200,000 as below.

**What the tier actually imposes.** The derivation above is not the only reading
of the same split. Under the linear growth it assumes, cache reads are
`C = n·k(k−1)/2` over `k` calls and the counted total is `P = n·k`, so

```
alpha = C / P = (k − 1) / 2
```

and the split alone fixes the call count, with no `n` needed. Substituting that
`k` back returns `N̄ = C / k = P / 2` — the half-the-counted-tokens fallback this
tier was written to replace. So the tier is not a second, independent route to
`N̄`. It imposes an assumed call count, `k = P / n`, over the `k = 2·alpha + 1`
the split itself implies, and what it returns is the fallback scaled by
`n / n_row`, where `n_row = P / (2·alpha + 1)` is the row's own implied new
tokens per call. On the Terminal-Bench 4.0 Claude Code block `n_row` is about
13,000, so the tier cuts those contexts several-fold below what the row's own
split implies.

**The reconciliation is re-prefill after cache expiry.** A share of the counted
tokens is not new positions at all: it is prefix re-processed after the cache
entry expired — Anthropic's five-minute TTL against an agent that spends minutes
inside a single tool call. Re-prefill inflates `P` and so deflates `alpha`, which
is exactly the direction needed, and SWE-Marathon's measured Claude Code turn
counts, 119 at the median against the 41 that `2·alpha + 1` would imply for a run
of Terminal-Bench 4.0's size, say the deflation is large. Re-prefilled positions
also attend over their own partial prefix rather than the full one, so the true
`N̄` on that share is lower again. The tier lands in the right place; this is the
reason, and the earlier text asserted a derivation that contradicts it.

The tier has two forms. Where the run publishes its own split the alpha is
measured on the row itself and only `n` is transferred. Where it does not, the
alpha comes from a run of the same model in a comparable agentic harness that
does — the donor method, whose worked example is `research/vals-ksp/vals-ksp.md`:
the six KSP rows have no token counters at all, so each takes the alpha of a
Terminal-Bench run of its own model, giving contexts of 21,498 to 62,037 against
the 200,000 cap the first build of those rows used, and the two independent
donors available for GPT-5.6 Sol agree to 6%. A donor's harness is not the row's
harness and its cache structure is a property of both, which is the error this
form carries and the cap does not.

| Source | Rows | Median N̄ | alpha from |
|---|---:|---:|---|
| Terminal-Bench 4.0 official leaderboard | 240 | 62130 | the cell's own Harbor Hub per-trial cache reads |
| Terminal-Bench-Science 0.1 official leaderboard | 157 | 84800 | the trial's own Harbor Hub cache reads |
| Artificial Analysis Terminal-Bench v4.0 board | 4 | 18819 | the board's own `cacheableInput` against its counted total |
| Vals AI Time Horizon Index: KSP | 6 | 33806 | transferred, one Terminal-Bench donor run per model |
| Epoch AI SWE-bench Verified bins | 92 | 20103 | each bin's own per-instance cache reads |
| `agen-omegause-officeval-minimaxm3` | 1 | 77924 | the row's own inverted cache structure, `alpha` 27.83 |

The OmegaUse row is the one place where this tier and the row's note disagree.
`research/omegause-officeval.md` reconstructs the context the other way, fixing
the call count from the served share alone and reading the mean prefix as half a
547,222-token final context; that returns 273,611, above the cap and above any
context window MiniMax M3 serves. Fixing the call count from `n` instead returns
77,924 over 196 calls, and that is the value the row carries.

**Otherwise, half the counted tokens.** An append-only agent dialog processed
once grows its prefix linearly to the counted total, so the length-weighted mean
prefix is half of it. This is exact for a single call and a mild overestimate
for a multi-call row whose prefix is re-read in full, where the position-weighted
mean is nearer a third of the final length.

**The 200,000 cap.** Wherever `N̄` would exceed 200,000 it is held there, and
since the audit that is a rule about the attended context rather than about how
the figure was obtained. The justification is compaction: an agent harness that
would otherwise grow past a model's window compacts instead, and the attended
context resets with it. Compaction does not care whether `N̄` came from half the
counted tokens, from a cache split, or from a measured turn count.

That last case is the change. The 213 SWE-Marathon rows take `N̄` as gross tokens
over the rollout's own measured turn count, which ran to 575,020 on one row, and
they were exempt from the cap on the grounds that the figure is measured. It is
measured as gross-over-turns, which is not an attended context once the harness
compacts — and `research/swe-marathon/swe-marathon.md` already flags 29 rows
whose implied trajectory exceeds the model's own context window, which is direct
evidence that those runs compacted. Fifty-five of the 213 were above 200,000 and
are now held there, at a median factor of 0.79 on those rows.

One row keeps a context above the cap: `reas-navier-stokes-openai` at 247,500.
It is a single reasoning dialog whose geometry the source publishes, not a
compacting agent harness, so the argument for the cap does not reach it.

A hundred and fourteen rows are held by the cap, and on those the correction is
an upper bound: the cap is doing the work that a call count would otherwise do.
Fifty-five are the SWE-Marathon rows above. Thirty-one reach it through the tier
above rather than through half the counted tokens — 21 Terminal-Bench-Science
rows and 10 Terminal-Bench 4.0 rows whose own cache reads imply a prefix past
200,000 — and those are the best-founded of the capped set.

The remaining twenty-eight have no usable split, for one of two reasons.

| Rows | Why no cache-implied context |
|---|---|
| RE-Bench (8), Vending-Bench 2 (4), the two ARC-AGI Deep Think rows, `game-pokemon-crystal-gemini3pro-red` | `tokens_accounting` is `input_output`: the counted total already charges re-read prefix as newly processed, so `P` is not `Σ n_i` and `alpha · n` does not describe these runs. Taking `P` as the counted total and the context from the trajectory geometry, as the METR section below does, is what these need |
| AI Village (6), MirrorCode (6) | No same-model run in the collection publishes a split: Claude 3.7 Sonnet, Opus 4.1, Sonnet 4.5, GPT-5, Gemini 2.5 Pro, Opus 4.5 and Opus 4.6 are all absent from the Terminal-Bench boards |
| `agen-tbench21-gpt55-codex` | The run publishes its own split and the split is degenerate. Its alpha of 1.145 returns a 3,206-token prefix for a run whose counted tokens `research/terminal-bench.md` establishes are largely repeated re-prefill rather than a cached dialog, so `n = 2,800` is the assumption that fails, not the alpha |

`game-pokemon-crystal-gemini3pro-red` is the least founded of them: its counted
total is a full-prefix approximation over a whole playthrough, four orders of
magnitude above any context the harness held.

The Epoch SWE-bench block moved as a unit on a second ruling. Its 92 rows carried
a median `attention_context` of 64,464 from half the counted tokens while two
independent routes put their mean prefix near 17k–20k: the bins' own
transcript-length bracket, median 17,282, and their own cache reads, median
20,103. The cache-implied value is the one applied, and where the two disagree by
more than 2× — 27 of the 92 — the row's `notes` states the bracket figure.
`research/epoch-swebench-bins.md#cached-context-attention` carries the comparison.

<a id="training-rows"></a>

## The training rows

Forty-six rows are `operation_count` at a training scope. Most already price
attention from the architecture — Latxa, the BabyLM and BabyBERTa runs, Swallow,
Llammas, AceGPT, searchless chess and Cicero all carry an explicit `S`-dependent
term, and the Gulordava LSTM has no attention to price. Ten rows did not: they
approximate a weight update as `6ND` and a monitoring forward as `2ND`, which
omits training attention exactly as `2N` omitted inference attention.

**The multiplier is three.** PaLM's training cost is `6N + 12·L·H·Q·T` per
token, so the attention term is three times the forward count `4·L·d_attn·N_ctx`
— the same 3× that takes `2N` to `6N`, since backward costs twice forward and
attention is recomputed alongside the weight matrices. A forward-only monitoring
position keeps the 1× form. Either way a component's attention is its
weight-matrix term times

```
r = 2 · L · d_attn · N_ctx / N_active
```

so `attention_ratio` means the same thing on a training row as on an inference
one, and no separate training ratio is needed.

**The context is the mean attended context, not the sequence length.** A causal
pass over a packed length-`S` sequence gives position `i` a prefix of `i`, so
the length-weighted mean is `(S+1)/2`. That is the same quantity
`attention_context` already records on the inference rows, and it is what the
notes that already price attention use: Swallow's `2LD(S+1)` per token is
`4·L·d_attn·(S+1)/2`. Writing `S` itself would be the dense non-causal count and
would double the term.

**Where components differ, the row takes the weight-FLOP-weighted mean.** A row
that trains at one length and monitors at another, or that runs a helper model,
gets one `attention_context`: the mean over the positions its own
`model_id` processes, weighted by each component's weight-matrix FLOPs. The
identity `r = 2·L·d_attn·attention_context / N_active` then holds exactly on the
row. Helper models are priced at their own shape and their own context inside
`compute_flops`, and do not enter `attention_context`.

The script is `research/attention-correction/training_attention.py`; its
per-component output is
`agent-work/derived/attention-correction/training-components.json`.

### Sequence lengths

| Rows | Sequence length | Source |
|---|---|---|
| Codex 300M, 2.5B, 12B | 2048 | [Brown et al. (2020)](https://arxiv.org/abs/2005.14165) Table 2.1: the GPT-3 family trains at `n_ctx = 2048`. [Chen et al. (2021)](https://arxiv.org/abs/2107.03374) §3.2 fine-tunes from that family at the same learning rate and states no change |
| Code Llama 7B, 34B | 4096, then 16384 | [Rozière et al. (2023)](https://arxiv.org/html/2308.12950v3) §2.4 and Appendix: 500B code tokens at 4,096, long-context fine-tuning at 16,384 over 6B tokens for 7B and 11B for 34B |
| Kotlin Kexer | 512 | The [model card](https://huggingface.co/JetBrains/CodeLlama-7B-Kexer) gives a 256-example batch at about 130K tokens per step, which is 256 × 512 |
| MultiPL-T OCaml 1B, OCaml 15B, Racket 15B | 2048 | `max_seq_length=2048` in the authors' [`training_starcoder1b/demo.py`](https://github.com/nuprl/MultiPL-T/blob/main/training_starcoder1b/demo.py), packed |
| Llama-2-13B binary memorization | 1032 training, 1024 evaluation | `research/memorization-leads/memorization.md#operation-count`: a 1,025-token string padded by the collator to a multiple of eight, and metric callbacks that trim the last position |

Code Llama's two stages give a length-weighted mean attended context of 2,121
for 7B and 2,181 for 34B. Kexer's 512 is inferred from the card's tokens-per-step
figure rather than stated; at the unpadded 233-token mean example length the
term would be about half as large, which moves the row by 0.5%. The Codex length
is the family default rather than a reported one — the later deployed
`code-davinci` product served 4,096, which would double these three rows'
attention term. Neither uncertainty gets a `compute_flops_low`/`high` bar,
because that range carries exactly the parameter band and the cache-implied
context and none of these ten models has a parameter band.

### What changed

| Row | N̄ | r | Before | After | Factor |
|---|---:|---:|---:|---:|---:|
| `agen-codexfer-codex300m` | 1024.5 | 0.0839 | 1.81e20 | 1.95e20 | 1.084 |
| `agen-codexfer-codex2p5b` | 1024.5 | 0.0362 | 1.50e21 | 1.56e21 | 1.037 |
| `agen-codexfer-codex12b` | 1024.5 | 0.0213 | 7.22e21 | 7.37e21 | 1.021 |
| `agen-codexfer-codellama7b` | 2121.4 | 0.0794 | 2.13e22 | 2.30e22 | 1.079 |
| `agen-codexfer-codellama34b` | 2180.8 | 0.0504 | 1.05e23 | 1.10e23 | 1.050 |
| `agen-codexfer-kotlin7b` | 256.5 | 0.0096 | 8.25e17 | 8.33e17 | 1.009 |
| `agen-codexfer-mplt-ocaml1b` | 964.2 | 0.0833 | 1.37e20 | 1.38e20 | 1.005 |
| `agen-codexfer-mplt-ocaml15b` | 963.4 | 0.0305 | 1.43e20 | 1.44e20 | 1.006 |
| `agen-codexfer-mplt-racket15b` | 945.4 | 0.0299 | 7.94e19 | 7.99e19 | 1.006 |
| `memo-binary-1024-llama2-13b` | 514.0 | 0.0162 | 9.40e16 | 9.56e16 | 1.016 |

The median factor is 1.021, against 1.26 on the inference rows. (The three Codex
rows' figures here are post-audit: their shape is the OpenAI family's 0.65 share
of the dense layer bracket, not the bracket itself.) Training
contexts are short — a packed 2,048-token sequence against a model sized to
process it — where the agentic inference rows carry tens of thousands of tokens
of re-read prefix against a comparable parameter count. The three MultiPL-T rows
barely move because synthetic-curriculum generation, not the fine-tune, is
99% of each row.

The StarCoderBase shapes behind the MultiPL-T rows moved from the estimated
bracket to their released configurations at the same time: 24 layers at 2,048
for the 1B and 40 at 6,144 for the 15B, both multi-query, so `d_attn = n_q ·
d_head` equals `d_model`.

<a id="metr-cache-reads"></a>

## The METR rows: the counted total is the processed total

The 283 `source_total` rows are METR's two time-horizon exports. Vivaria's
prompt totals include cache reads and writes
(`research/metr/cache-accounting.md`), so the counted total `C` is, per call,
the whole prefix plus the output, summed over calls. Whether a position inside
it took a pass through the weights depends on whether the provider served it
from a cache, and the counter does not say.

The exports' `generation_cost` field does. Divided by `tokens_count` it gives a
billed price per counted token, and on HCAST that price sits at or above the
model's uncached input price on every alias whose rate card is identified. A
cache-read tier is priced at a tenth to a half of the input rate, so a
substantial cache-read share would drive the billed price below it, and none of
these aliases goes there. The scaffolds recomputed the prefix. Damon ruled on
2026-09-16 that the dataset measures compute as actually run, so

```
P = C
```

on every one of these rows, and the weight-matrix term is `2 · N_active · C`.

`P` was previously rebuilt as `min(C, sqrt(2·C·n))` at `n = 2,800`, which is the
perfect-caching case and kept 12% of the counted tokens at a one-hour task. That
relation survives as the **trajectory length**: with a prefix growing linearly
over `k = T/n` calls, `C ≈ T·k/2`, so `sqrt(2·C·n) = T`. `n` is the scaffold's
per-call cadence and not a caching assumption, so it stays at 2,800 and now
enters only the attended context.

```
T = min(C, sqrt(2 · C · n))          N̄ = T · ((P − T) / 3 + T / 2) / P
```

The context is that geometry integrated over the run. A call at fraction `s` of
the way through has prefix `T·s`; it processes its `n` new tokens at a mean
context of `T·s`, and the prefix positions it re-processes sit at a mean context
of `T·s/2`. Integrating and dividing by `P` gives the expression above. It
returns `T/2` when nothing is re-processed, which is the old central and is what
all 56 SWAA rows get, since they are single calls with `T = C`; it tends to
`T/3` when the whole prefix is recomputed on a run long enough that `C ≫ T`. `P`
is floored at `T`, because every token of the final trajectory was processed at
least once.

212 of the 283 rows moved, by a median factor of 4.33 and a maximum of 31.2; the
other 71 are single-call runs where `P = C` already. The median METR row's
`attention_ratio` is now 0.076: the weight-matrix term grew by the full
cache-read multiple while the context fell from `T/2` to about `T/3`. The
per-alias billing arithmetic, the four aliases with no billing anywhere, and the
one alias whose provider is unidentified are in
`agent-work/reviews/metr-billing-rebuild-2026-09-16.md`; the script is
`research/metr/metr_billing_rebuild.py`.

## What the correction did

1,358 rows changed: all 1,342 `params_tokens` rows and 16 `operation_count`
rows whose recipe applies the shared coefficient to a text backbone and says the
attention term is left out. Every other `operation_count` row either counts its
attention products from the architecture already — the encoder and
encoder-decoder recipes, the RULER rows, the 405B needle row — or runs no
language backbone at all.

| | Value |
|---|---:|
| Rows changed | 1358 |
| Rows raised | 901 |
| Rows within 2% | 245 |
| Rows lowered | 212 |
| attention_ratio, median | 0.43 |
| Correction factor, p10 / median / p90 | 0.34 / 1.26 / 2.78 |

On the primary set — inference rows where the AI reaches `match` or better — the
median FLOPs per human-second moves from 3.66e12 to 5.61e12 and the share above
a 1e13 brain anchor from 27.1% to 36.2%. Excluding GDPval the median moves the
other way, from 4.02e12 to 2.63e12, because the METR block falls further than
the rest of the file rises.

The rows that move most upward are the long agentic ones whose context is held
at the cap, and the GDPval block, which moves as a unit by 2.78×. The rows that
move most downward are METR HCAST runs with the largest counted totals, which
fall by up to 14×: a bigger inclusive counter implies more calls over the same
dialog, not more processed tokens. **That half of the pass was reversed on
2026-09-16**, when METR's own `generation_cost` showed the scaffolds had
recomputed the prefix rather than cached it; the METR section above carries the
current recipe and the figures in this table are the 2026-09-14 pass as it
stood.

## The fallback-order pass

The precedence above was ruled after the original correction, which had no
cache-implied tier and sent every row without a measured context to half the
counted tokens and then to the cap. Applying the order moved 233 rows, all
downward.

| | Value |
|---|---:|
| Rows changed | 275 |
| Terminal-Bench 4.0, from the cell's own cache reads | 222 |
| Epoch SWE-bench bins, from the bin's own cache reads | 52 |
| `agen-omegause-officeval-minimaxm3` | 1 |
| Correction factor, p10 / median / p90 | 0.30 / 0.53 / 0.84 |
| Rows at the cap, before / after | 205 / 59 |

All 92 Epoch SWE-bench rows were recomputed; on 40 of them the append-only bound
`P / 2` was already tighter than the cache-implied figure, so the value did not
move.

On the primary set — inference rows at `match` or better — the median FLOPs per
human-second moves from 4.78e12 to 4.71e12 and the share above a 1e13 brain
anchor from 35.5% to 33.0%. The Epoch block contributes nothing to that: all 92
of its rows are labelled `below` and sit outside the primary set. The file-wide
median `attention_ratio` falls from 0.44 to 0.39.
