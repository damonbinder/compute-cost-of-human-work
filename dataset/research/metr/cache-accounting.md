# METR token-counter interpretation

## What the counter is

At [public Vivaria commit 20a6c290](https://github.com/METR/vivaria/tree/20a6c290c3c11f701af95a559d9d0c64dd6105d4), shared/src/types.ts defines prompt totals to include cache reads and writes. The OpenAI and Anthropic passthrough handlers implement this inclusive count. The August 2025 runs-view migration adds prompt, output and caller-supplied serial-action tokens without subtracting cache reads. The public API does not establish whether serial-action counts overlap other generations in these historical runs. The Inspect importer can discard cache components, so even a later zero cache field would require checking against the original provider usage.

So `tokens_count` is, per call, the whole prefix plus the output, summed over calls. Whether a position inside it took a pass through the weights depends on whether the provider served it from a cache, and the counter does not say.

## What the exports contain

The two released time-horizon exports carry 65,637 run records over 23 fields, and one of them answers the question the counter leaves open. **`generation_cost` is a summed per-call billing figure**, nonzero on 22,282 runs and dispersed run to run: on almost every alias the number of distinct values equals the number of runs. The exceptions are the aliases whose input and output prices are equal — `davinci-002`, `DeepSeek-V3`, `Qwen2-72B` — and on those the billed cost is exactly `tokens_count` times the single rate. That fixes the accounting: the billed components sum to the counted total, and nothing is billed that the counter does not also count.

Time Horizon 1.0 carries the field on every alias but `GPT-2` and `human`. Time Horizon 1.1 carries it on exactly two, `GPT-4 0314` and `o1-preview`, the two aliases that kept the old `modular-public` and `duet` scaffolds; all nineteen Inspect-scaffold aliases in 1.1 have none. The absence is a property of the Inspect export and is not evidence about those runs.

An earlier version of this note said the exports hold "totals without prompt, output, cache or serial-action components" and closed the question, concluding that "a supported revision would require per-run components". `generation_cost` is not a decomposition, but it constrains one.

## Reading the billing

Dividing `generation_cost` by `tokens_count` gives a billed price per counted token. A counted token is fresh input, a cache read or output, in shares `u`, `c` and `o` of the counted total summing to one, and the processed fraction is `f = u + o`, because a cached prefix position is a key and not a query. Then

```
q = u · p_in + c · p_cache + o · p_out
```

at the vendor's three rates in dollars per million tokens. Holding the output share of each call's *new* tokens at `β` gives `o = β · f` and closes the system:

```
f = (q − p_cache) / (p_in − p_cache + β · (p_out − p_in))
```

`β = 0.3191` is the median of `output / (uncached + output)` over the sixteen official Terminal-Bench 2.1 leaderboard submissions, the same donor set that supplies the new-tokens-per-call constant. `β = 0` gives the largest processed fraction the price admits and `β = 1` the smallest, so the expression is monotone in the one transferred quantity.

## What the billing says: the prefix was recomputed

On HCAST, the billed price sits **at or above the model's uncached input price** on every alias whose rate card is identified, at every token quintile. That is what a run costs when it recomputes its prefix on every call. A cache-read tier is priced at a large discount — 10% of input for Anthropic and for the GPT-5 era, 50% for o1 and GPT-4o — for the same reason a cache read is cheap to compute, so a substantial cache-read share drives the billed price below the input price and none of these aliases goes there.

Three aliases had no cached tier at any date, `GPT-4 0314`, `GPT-4 Turbo` and `gpt-3.5-turbo-instruct`, and they are the control: 1.01 to 1.06 times their input price, implying 1% to 6% output. The nine Anthropic aliases sit at 1.18 to 1.42 with 5% to 11% output, the same shape one notch up, and Anthropic caching is opt-in per request. The billed price falls toward the input price as the counted total grows on every alias, which is what a falling output share does and not what a fixed cache hit rate does.

Automatic caching was available on the OpenAI and Google aliases and did not fire here. o1 bills at 2.50 times its input price and Gemini 2.5 Pro Preview at 2.45, with 0.3% and 0.0% of HCAST runs below the input price. Where it did fire it is visible: 79% of GPT-4o's RE-Bench runs bill below the input price against 9.1% of its HCAST runs, and RE-Bench re-sends a long fixed prompt. Two aliases show a discount throughout, `Grok 4` at 0.735 of its input price and `gpt-oss-120b` at 0.457 of the only card published for it, which refutes the card rather than measuring a share.

**Whether a scaffold cached is a fact about the run, not an uncertainty.** Damon ruled on 2026-09-16 that the dataset determines which it was and commits to the answer, so the processed fraction is a determination and carries no band in `compute_flops_low` or `compute_flops_high`. He also ruled that the dataset measures compute as actually run. Caching a scaffold did not use is compute the scaffold spent. So the processed fraction on the `source_total` rows is **1**: `P = C`.

## What this replaced

Until 2026-09-16 the dataset rebuilt the processed positions as `P = min(C, sqrt(2·C·n))` with `n = 2,800`, which is the perfect-caching case and kept 12% of the counted tokens at a one-hour task. That relation survives as the **trajectory length**: with a prefix growing linearly over `k = T/n` calls, `C ≈ T·k/2` and `sqrt(2·C·n) = T`. `n` is the scaffold's per-call cadence, not a caching assumption, so `T` stays at `n = 2,800` and now enters only the attended context. The error was equating the positions charged a weights pass with the trajectory length.

Only three of the eleven aliases the dataset draws on are billed on their own runs, `gpt-oss-120b`, `DeepSeek-R1` and `GPT-4 0314`. The other eight are Time Horizon 1.1 Inspect aliases with no cost record at all, and their determination is **transferred** from their vendor's other aliases in the collection, including the four whose own model was billed under Time Horizon 1.0: caching is requested by the harness, and the Inspect harness is not the harness that was billed. None of the eight is a measurement, and `compute_evidence` is `derived_assumed_inputs` on all 283 rows.

`gpt-oss-120b` is the one alias whose own billing cannot be read. Its 577 HCAST runs bill at 0.457 of Together's input price, and Together publishes no cached tier, so under that card nothing can land below the input price: the card is refuted rather than a cache share measured, and METR's provider for this open-weight model is not identified anywhere in the exports or the fetched `flock-public` snapshot. A sub-reference price is what a different provider's rate card looks like — a dozen providers serve gpt-oss-120b at published rates spread over a factor of three — and the alternative asks this one alias to have cached under `flock-public` while the nine other aliases on that scaffold with an identified card all recomputed the prefix. Damon ruled for the provider reading on 2026-09-16, so `gpt-oss-120b` takes its scaffold's pattern.

The full per-alias arithmetic, the rate cards and their dates, the treatment of the four aliases with no billing anywhere, and what the revision did to the file are in `agent-work/reviews/metr-billing-rebuild-2026-09-16.md`. The recipe as applied is `research/attention-correction.md#metr-cache-reads` and the script is `research/metr/metr_billing_rebuild.py`, whose `--audit` mode reprints the billing table from the exports. Relevant original code and export hashes are retained in agent-work/sources/metr/cache-accounting/.
