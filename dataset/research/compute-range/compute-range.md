# The compute_flops range

*Created 2026-09-14 13:25.*
*Last revised 2026-09-16 15:05, after the METR rows' processed positions became
the counted total itself and their band became the context alone.*

`compute_flops_low` and `compute_flops_high` bracket `compute_flops` against two
named uncertainties and nothing else: the model's active-parameter range, and
the new-tokens-per-call constant, which sets the mean attended context on the
rows that took it from the cache-implied route and on the METR rows, whose
trajectory length it fixes. Both ends are recomputed through the
recipe of `research/attention-correction.md`, not applied as a multiplier,
because the attention shape of an `estimated` model is itself a function of the
active-parameter count and moves with it.

The script is `research/compute-range/compute_range.py`, with the per-row
cache-read multiples in `research/compute-range/cache-alpha.csv`. Its per-row
output is `agent-work/derived/compute-range/ranges.csv` and its run summary
`agent-work/derived/compute-range/run.json`.

## The recipe at each end

A row's compute is a term in the weight matrices, a term in the attention
products, and on a few `operation_count` rows a remainder that is neither:

```
compute_flops = other  +  2 · N_active · P  +  4 · L · d_attn · N̄ · P
```

`P` is the processed positions, `N̄` the mean attended context, and `L` and
`d_attn` the attention shape. The low end takes the low parameter count with the
attention shape that goes with it and the low context; the high end takes all
three high:

```
low  = other + 2 · N_low  · P + 4 · L(N_low)  · d(N_low)  · N̄_low  · P
high = other + 2 · N_high · P + 4 · L(N_high) · d(N_high) · N̄_high · P
```

For `attention_basis = estimated` the shape at each end is
`L = share · (N / 196608)^(1/3)`, `d_attn = 128 · (N / 196608)^(1/3)` at the
model family's full-attention layer share, the rule of
`research/attention-correction.md#model-architectures` applied to that end's
parameter count rather than to the central. For `attention_basis = reported` the
shape is a fact about the model and is held fixed at both ends. The shape rule
is worth a factor of about 2 on the attention term across a 5× parameter band —
`L` and `d_attn` each scale as `N^(1/3)`, so `L · d_attn` scales as `N^(2/3)` —
and taking it at the central instead would understate the bar's asymmetry.

`P` is recovered from the row itself rather than from `tokens`. For a
`params_tokens` row, `compute_flops = 2 · N_active · P · (1 + r)` with `r` the
`attention_ratio` recomputed from the recorded context, so
`P = compute_flops / (2 · N_active · (1 + r))` and `other = 0`. That equals
`tokens` on 969 of the 988 rows where the two can be compared; on the other
nineteen — the Noy and Zhang, LUMEN, BALROG-VLM, ARTEMIS and patient-message
rows — the counted total covers a helper model as well, and `P` is the effective
processed-position count at the primary model's coefficient. For the sixteen
`operation_count` rows that apply the shared coefficient to a text backbone, `P`
is `tokens`, the parameter-proportional part is `2 · N_active · tokens`, and the
remainder — a vision or audio encoder — is held fixed at both ends. For the
three rows with a parameter range and no attention term at all, the architecture
op count is proportional to the parameter count throughout, so the whole figure
scales.

`P` is the same at both ends everywhere, the 283 METR `source_total` rows
included — see the METR section below. On the `operation_count` rows it is fixed
at both ends.

<a id="the-constant"></a>

## The constant's percentiles

`research/attention-correction.md#cache-implied-context` sets a cache-implied
context as `N̄ = alpha · n`, with `alpha = C / P` the run's cache-read multiple
and `n` the new tokens per call, held at 2,800 everywhere. The sixteen official
Terminal-Bench 2.1 leaderboard submissions are the only agent runs in the
collection publishing `uncached_input_tokens`, `cached_input_tokens` and
`output_tokens` per trial, so they are what the constant rests on. Inverting the
same relation on each, `n = P² / (2·C_cache)` with `P` the uncached plus output
per trial and `C_cache` the cached reads alone — the same quantity
`alpha = C_cache / P` is defined against. An earlier build put `P + cached` in
that denominator, which understated every value by `(alpha + 1) / alpha`:

| Submission | n | n, earlier build |
|---|---:|---:|
| glm-5.1 max, Claude Code | 1758 | 1651 |
| openai/gpt-5.6-terra max, Codex | 1928 | 1846 |
| gpt-5.6-sol max, Codex | 2024 | 1913 |
| cursor/grok-4.5, Cursor CLI | 2089 | 1886 |
| openai/gpt-5.6-luna max, Codex | 2094 | 2020 |
| anthropic/claude-sonnet-5 high, Claude Code | 2095 | 1978 |
| anthropic/claude-opus-4-7 max, Terminus 2 | 2830 | 2605 |
| anthropic/claude-opus-4-7 max, Claude Code | 3034 | 2867 |
| anthropic/claude-opus-4-8 high, Claude Code | 3049 | 2700 |
| anthropic/claude-fable-5 high, Terminus 2 | 4676 | 3676 |
| anthropic/claude-fable-5 xhigh, Claude Code | 5980 | 5090 |
| gemini/gemini-3.1-pro-preview high, Gemini CLI | 7962 | 6990 |
| gemini/gemini-3-pro-preview high, Gemini CLI | 10279 | 8810 |
| gemini/gemini-3-pro-preview high, Terminus 2 | 19054 | 13275 |
| gemini/gemini-3.1-pro-preview high, Terminus 2 | 19121 | 13460 |
| openai/gpt-5.5 xhigh, Codex | 336382 | 179554 |

| Statistic | n | n, earlier build |
|---|---:|---:|
| 10th percentile | 1976 | 1866 |
| median | 3041 | 2783 |
| 90th percentile | 19088 | 13368 |

Percentiles interpolate linearly between order statistics. **The central stays at
2,800.** The consistent median is 3,041 against the earlier 2,783, a 9.3% move,
which is inside the rounding the figure already carries, and three independent
sources that count calls rather than inferring them bracket 2,800 from both
sides: GAIA's 57 measured per-run call counts give 1,415, SWE-Marathon's 2,129
measured rollout turn counts give 1,475, and GDPval's 60.47 measured mean turns
give 3,588. The bar is therefore 0.71× to 6.8× the central.

The distribution is bimodal, and the split is by model rather than by harness:
every value above 7,000 is a Gemini model, under Gemini CLI and under Terminus 2
alike, while Anthropic models under Terminus 2 give 2,830 and 4,676. No row in
the affected set is a Gemini model under either of those harnesses, so the upper
mode widens the bar without any row sitting in it. The `gpt-5.5` Codex outlier at
336,382 sits above the 90th percentile and does not set it; its own note records
that its counted tokens are largely repeated re-prefill rather than a cached
dialog, so it is the assumption `n = 2,800` that fails on that run, not the
arithmetic.

Each row's `alpha` is a property of the run. Holding `alpha` fixed and varying
`n` is therefore the right shape for the bar: it asks what the row's own measured
cache structure implies if the per-call cadence is at the edge of the range the
sixteen runs show, rather than re-deriving the cache structure.

<a id="the-context-band"></a>

## Which rows get a context band

The 505 rows whose `attention_context` came from the cache-implied route, and no
others. At each end,

```
N̄_low  = min( alpha · 1976,  counted tokens / 2,  200000 )
N̄_high = min( alpha · 19088, counted tokens / 2,  200000 )
```

with the same two bounds the central respects. `research/compute-range/cache-alpha.csv`
carries each row's `alpha` and where it came from.

| Rows | alpha from |
|---:|---|
| 240 | Terminal-Bench 4.0, the cell's own Harbor Hub per-trial cache reads |
| 157 | Terminal-Bench-Science 0.1, the trial's own Harbor Hub cache reads |
| 92 | Epoch AI SWE-bench bins, each bin's own per-instance cache reads |
| 6 | Vals AI KSP, one transferred Terminal-Bench donor run per model |
| 4 | Artificial Analysis Terminal-Bench v4.0, the board's own `cacheableInput` |
| 1 | `agen-omegause-officeval-minimaxm3`, the row's own inverted cache structure, alpha 27.83 |
| 5 | FrontierMath Erdős, each problem's own pooled cache reads over its published resolutions |

Reproducing `min(alpha · 2800, counted / 2, 200000)` returns the recorded
`attention_context` on all 505 to within the six significant figures the column
carries. The six Vals KSP rows used the unrounded 2,783 rather than 2,800, a
0.6% difference that sits well inside the band.

On 57 of the 505 both ends are held by the same bound — the half-counted-tokens
value on most, the 200,000 cap on the rest — so the band collapses; 48 of those
keep a parameter range and 9 end up with no bar. Of the 59 rows at the cap, the
31 that reach it through the cache-implied tier take `high = 200000`, and 23 of
them get a low end below the cap from the cache-implied value at the low
constant; the 28 with no donor take no context band at all, because there is no
cache structure to vary.

Rows whose context came from the run's own per-call or per-turn records, from a
per-source mean over published turn counts, or from half the counted tokens
carry no context band. None of those three moves with the constant. Their bar is
the parameter range alone.

## What the range does not cover

Everything in this file is a sensitivity range on two inputs. It is not a
confidence interval on a row's FLOPs, and the largest identified errors in the
collection are outside it.

**Borrowed token counts.** A row whose `compute_evidence` is
`transferred_workload` takes its workload from a different work unit, and the
transfer error is not represented here. So is the donor structure behind the six
Vals KSP rows: their `alpha` comes from a Terminal-Bench run of the same model
in a different harness, and the bar varies `n` while holding that borrowed
`alpha` fixed.

**Resolved-trials-only averaging.** Where a benchmark aggregate divides a run
total by resolved trials rather than by attempts, the grain of the resulting
per-task figure is a modelling choice, not a measured quantity, and it does not
move across the bar.

**The attention-shape rule.** `research/attention-correction.md` now takes a
per-family share of the dense layer count for an `estimated` model, on the
evidence that every frontier architecture disclosed since March 2025 moves layers
to a local window or a linear state. The share itself is an assumption worth
about 0.4× to 1.5× on the attention term and it is not in the bar: the shape
moves across the bar only through the parameter count, never through the rule.

**The cap and the fallback.** The 200,000 cap and half the counted tokens are
bounds with no run behind them on the rows they hold. They bound both ends here
rather than being varied.

**Whether a counted total's cache reads were served from a cache.** On the METR
rows that is determined and not banded, and on four of their eleven aliases the
determination is transferred from the same model under a different harness and
on four more from the vendor's other aliases. The transfers are argued in
`agent-work/reviews/metr-billing-rebuild-2026-09-16.md` and none of them is in
the bar.

**Everything on the human side.** `human_time`, its statistic, its subset and
the performance comparison are untouched. A ratio of FLOPs to human seconds
carries this bar on the numerator only.

<a id="the-metr-rebuild"></a>

## The METR rows: the constant moves the context, not the processed count

The 283 METR `source_total` rows do not take their context from a cache-implied
alpha. Their counted total `C` charges every position of every call, and METR's
own `generation_cost` field says the scaffolds recomputed the prefix rather than
caching it (`research/attention-correction.md#metr-cache-reads`), so every
counted position took a weights pass:

```
P = C          T = min(C, sqrt(2 · C · n))          N̄ = T · ((P − T)/3 + T/2) / P
```

**Whether a scaffold cached is a fact about the run, not an uncertainty.** Damon
ruled on 2026-09-16 that the dataset determines which it was and commits to the
answer; the determination is per alias, from its own billing where it exists and
from its vendor's or scaffold's pattern where it does not, and it is argued in
`agent-work/reviews/metr-billing-rebuild-2026-09-16.md`. It carries no band, so
`P = C` at both ends of the bar.

What the constant still moves on these rows is the trajectory length `T`, and
through it the attended context. Each end reruns that geometry at that end's
`n`, and the bounds are the extremes over the two:

```
low  = min over n in {1976, 19088} of  2 · N_low  · C + 4 · L(N_low)  · d(N_low)  · N̄(n) · C
high = max over n in {1976, 19088} of  2 · N_high · C + 4 · L(N_high) · d(N_high) · N̄(n) · C
```

The extremes are taken rather than the ends in order, because `T` saturates at
`C` for a row whose counted total is a single call and the mapping is then flat
rather than monotone. All 56 SWAA rows are in that regime at both ends, and
their bar is the parameter range alone.

The 200,000 cap is not applied here, because the central on this branch does not
apply it either: `N̄` on a trajectory geometry is not the half-the-counted-tokens
fallback the cap was written to bound.

All 283 rows carry a bar, the eighteen `DeepSeek-R1` rows among them: their
parameter count is reported, but the context band applies. The median METR bar
spans 5.7 from low to high and the widest 9.6, against 12.8 and 30.5 while the
constant moved the processed count as well, so the widest rows in the file are
no longer METR rows.

## Coverage and what the bar looks like

1,414 of the 1,684 rows carry a bar. Rows combining both uncertainties,
parameter-only rows and context-only rows — an open-weight model with a reported
parameter count on a cache-implied or METR row — all appear.

| Rows without a bar | Why |
|---:|---|
| 106 | An attention term on a reported parameter count, with no context band: neither uncertainty applies |
| 131 | No attention term and no parameter range |
| 9 | A cache-implied row with a reported parameter count whose context band collapsed onto a bound |
| 5 | `compute_method = reported`: the FLOPs do not derive from a parameter count |

The median row spans a factor of 5.4 from low to high and the widest 14.1. The
floor is the parameter band's own shape — the median `active_parameters` range
spans 5.0 — widened where a second band applies and by the shape rule that makes
the attention term move as `N^(2/3)` on top of it. The widest row in the file is
`media-blender-cabin-gpt-5-6-terra-ultra` at 14.1, and the next five are
Terminal-Bench 4.0 and Terminal-Bench-Science cells at 12.5 to 13.2, where a
cache-implied context band sits on top of a wide parameter prior; `reas-epoch-mathl5-qwenturbo24` at 8.9 and the
o1 rows at 8.0 are the widest carried by a parameter prior alone. METR HCAST
rows held first place at up to 30.5 until 2026-09-16, when the constant's
percentiles stopped setting their band, and they now reach 9.6.
