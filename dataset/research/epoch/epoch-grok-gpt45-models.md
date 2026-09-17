# Epoch: GPT-4.5 and Grok model assumptions

The four API identities are copied from Epoch's original output table. `grok-3-mini-beta_high` is the `grok-3-mini-beta` model at high reasoning effort. It does not create a second parameter coefficient. All four active counts are marked `estimated`: neither an analyst hypothesis nor a transfer between model revisions is a vendor disclosure. FLOPs per token are twice active parameters under the dataset convention.

## gpt45

[OpenAI's February 27, 2025 announcement](https://openai.com/index/introducing-gpt-4-5/) made GPT-4.5 available through the API as a research preview. The [API model page](https://developers.openai.com/api/docs/models/gpt-4.5-preview) identifies `gpt-4.5-preview-2025-02-27`. The [system card](https://cdn.openai.com/gpt-4-5-system-card-2272025.pdf) describes increased pretraining scale without disclosing parameter count or expert routing.

Central active size is **600B**, following Nathan Lambert's original [February 28 estimate](https://www.interconnects.ai/p/gpt-45-not-a-frontier-model), under “What GPT-4.5 is good for.” His hypothesis combines roughly tenfold training compute, an illustrative fivefold parameter/twofold data split, and GPT-4-like sparsity. He explicitly gives about 600B active and warns that the estimate is speculative. The intermediate quantities are approximate and do not form an exact reconstruction of 600B; this is an analyst's model-specific judgment, not a calculation from disclosed architecture. The **200–1,200B** sensitivity spans the older GPT-4 scale he cites through twice his central estimate. It is not a confidence interval. The central coefficient is **1.2e12 FLOPs/token**.

## grok2

xAI's [December 12, 2024 announcement, “API access”](https://x.ai/news/grok-1212#api-access), explicitly names `grok-2-1212` and says the new models are being added. We use December 12 as the earliest announced public availability. The [later API changelog](https://docs.x.ai/developers/release-notes) instead puts this release under December 14; that conflict remains visible in the model row. The original August Grok-2 release is not the December revision's date.

The original [xAI weight repository](https://huggingface.co/xai-org/grok-2/tree/daf4395a80ad177386cfe39641b64fc12b1d70ed) says these weights were trained and used in 2024, without identifying the exact API revision. Its [config](https://huggingface.co/xai-org/grok-2/blob/daf4395a80ad177386cfe39641b64fc12b1d70ed/config.json) supplies 64 layers, width 8,192, eight experts of intermediate width 16,384 with two selected per token, and a residual dense MLP of width 32,768. There are 64 query heads and eight key/value heads of width 128. The [inference code linked by the release](https://github.com/sgl-project/sglang/blob/97a38ee85ba62e268bde6388f1bf8edfe2ca9d76/python/sglang/srt/models/grok.py) instantiates and executes both the residual MLP and routed experts.

Only the 39 safetensor metadata headers were downloaded; no weight arrays. Their shapes give:

| Components | Parameters |
|---|---:|
| Input embedding and output head | 2,147,483,648 |
| Attention projections | 9,663,676,416 |
| Always-active dense MLPs | 51,539,607,552 |
| Norm weights and routers | 6,299,648 |
| All routed experts | 206,158,430,208 |
| Shared subtotal | 63,357,067,264 |
| Shared plus two of eight routed experts | **114,896,674,816** |
| Total stored weights | **269,515,497,472** |

Each expert is split across eight tensor-parallel shards; summing those shards reconstructs each expert once. `recompute_grok_gpt45_table.py` verifies every header hash and the per-expert dimensions. The count includes both vocabulary matrices under the dataset's common 2P convention, although an input embedding lookup itself does not perform a dense multiplication.

We transfer this released-model count to `grok-2-1212`, rounded to **115B active**, hence **2.3e11 FLOPs/token**. The exact API-to-weight link remains unconfirmed. An **80–150B** sensitivity allows a roughly ±30% architecture difference around the released count; it is a judgmental transfer scenario, not an observed variation.

## grok3

Epoch identifies the non-thinking API endpoint `grok-3-beta`. xAI's [February announcement](https://x.ai/news/grok-3) describes consumer beta availability and says API access is still coming. Its [API changelog](https://docs.x.ai/developers/release-notes#grok-3-models-launch-on-api) dates the API launch **April 3, 2025**. We use that date for the beta API record; Epoch's table instead lists April 9. Current provider pages redirect the beta name to a later stable model and cannot establish the historical beta's first day. This date discrepancy is disclosed rather than replacing the beta with the stable model.

Central size is **115B active**, transferred from the directly reconstructed Grok-2 family anchor above. No Grok-3 expert count or active size was recovered. The announcement's larger training-compute claim does not determine parameter growth without a training-token count or allocation rule. We therefore use the same family scale as a weak prior rather than infer size from price, output speed or benchmark score. The **50–500B** sensitivity allows a smaller active route or roughly fourfold active growth. Coefficient: **2.3e11 FLOPs/token**. The large range matters more than small input-token corrections.

## grok3mini

The same API changelog supports **April 3, 2025**, with the same April 9 discrepancy in Epoch. This row describes `grok-3-mini-beta`; high reasoning effort belongs to the observations. The [original xAI announcement](https://x.ai/news/grok-3) distinguishes the smaller model as an efficient reasoning model; it does not report its size.

We use **20B active**, the midpoint of Epoch's original **10–30B** active-size estimate for the contemporary smaller reasoning model `o4-mini-2025-04-16_medium`, retained in the data table of [Epoch's capabilities analysis](https://epoch.ai/data-insights/ai-capabilities-progress-has-sped-up). This is a named peer transfer, not evidence that the two models share an architecture. The **5–60B** sensitivity allows a fourfold smaller or threefold larger active model. Coefficient: **4e10 FLOPs/token**. The wider transfer range deliberately exceeds the donor estimate's range.

## Retained evidence

Original model pages, config and tokenizer are in `agent-work/sources/epoch/grok-gpt45-models/`. `provenance.json` records URLs and hashes. The pinned weight revision is `daf4395a80ad177386cfe39641b64fc12b1d70ed`; `grok2-headers/manifest.json` records each original shard URL and the exact byte range of its retained header. The token-count script accepts the sources directory as an argument and reproduces the architecture arithmetic without network access.
