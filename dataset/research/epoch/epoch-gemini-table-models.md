# Gemini 1.5 and 2.0: model assumptions

The six records preserve Epoch's exact API identifiers. Google does not report their parameter counts. The values below are shared estimates for text inference under the dataset's `2 × active_parameters` convention. They are not total MoE sizes or counts inferred from API prices.

## Gemini 1.5 Flash

Use **27B active parameters** for both `gemini-1.5-flash-001` and `gemini-1.5-flash-002`. The original [Gemini 1.5 report](https://storage.googleapis.com/deepmind-media/gemini/gemini_v1_5_report.pdf), §3.2 and model-card Table 45, identifies Flash as a dense decoder distilled from the much larger Pro. Section 8 identifies Flash-8B as its smaller counterpart. These facts establish architecture and a relative scale, not a parameter count.

The numerical anchor is Google's contemporary [Gemma 2 27B](https://arxiv.org/abs/2408.00118), a disclosed dense decoder from the same organization and model-generation period. We use its rounded text-model scale as a weak peer estimate for the larger Flash tier. Flash and Gemma 2 are different models; neither the report nor their performance proves equal size. The choice favors a named dense architecture over an unspecified MoE prior. A scenario of **8–100B active** covers approximately the small Flash sibling through a substantially larger dense model. It is not a probability interval. Both snapshots share the central coefficient because the [002 release](https://developers.googleblog.com/updated-gemini-models-reduced-15-pro-pricing-increased-rate-limits-and-more/) identifies an update within that family and supplies no evidence of a size change; unchanged size remains an assumption.

## Gemini Pro

Use **100B active parameters** for `gemini-1.5-pro-001`, `gemini-1.5-pro-002` and `gemini-2.0-pro-exp-02-05`. The 1.5 report §3.1 identifies Pro as sparse MoE. It describes an efficient successor to Gemini 1.0 Ultra, but does not disclose expert dimensions, routing counts or total parameters. Google's [2.0 release](https://blog.google/innovation-and-ai/models-and-research/google-deepmind/gemini-model-updates-february-2025/) positions Pro as its strongest model for coding and complex prompts, without a size disclosure.

The numerical anchor is [Epoch's original GPT-5 estimate](https://epochai.substack.com/p/notes-on-gpt-5-training-compute), “Pre-training”: approximately 100B active, explicitly placed alongside GPT-4o and Claude Sonnet as medium-sized frontier models. Transferring that scale to Gemini's Pro tier is a weak cross-provider estimate. It is consistent with the registry's later Gemini Pro assumptions, but those stored values are not its evidence. Nothing here establishes that performance, speed or release chronology maps uniquely to parameter count. The three revisions share this coarse prior rather than introducing unsupported snapshot-specific differences. Use **30–300B active** as sensitivity scenarios.

## Gemini 2.0 Flash

Use **40B active parameters** for `gemini-2.0-flash-001`. Its [original model card](https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-2-0-Flash-Model-Card.pdf), printed page 1, places Gemini 2.0 in the sparse MoE architecture family. This is a material difference from dense Gemini 1.5 Flash; we do not transfer that model's total parameter count as if it were an active MoE count.

Original contemporaneous efficient MoEs give an explicit scale: [DeepSeek-V3](https://huggingface.co/deepseek-ai/DeepSeek-V3), introduction and model-download table, reports 37B active; [Mixtral 8×22B](https://mistral.ai/news/mixtral-8x22b/) reports 39B active. We round their common scale to 40B. This is a peer estimate, not a reconstruction of Gemini's routing or experts. Use **10–150B active** scenarios. The central coefficient agrees with the later Flash registry prior, but the original 2024 peer disclosures independently supply this estimate's numerical anchors.

These scenarios change FLOPs linearly at fixed tokens. They are not confidence bounds and do not assert that larger departures are impossible. Model-specific input/output token counts carry the observed workload differences; guessed changes in architecture do not.

## Release dates

| Exact API identifier | First public date used | Original source |
|---|---|---|
| `gemini-1.5-flash-001` | 2024-05-23 | [Gemini API changelog, May 23, 2024](https://ai.google.dev/gemini-api/docs/changelog#may-23-2024) explicitly names stable 001. |
| `gemini-1.5-pro-001` | 2024-05-23 | The same entry explicitly names Pro 001. |
| `gemini-1.5-flash-002` | 2024-09-24 | [Gemini API changelog, September 24, 2024](https://ai.google.dev/gemini-api/docs/changelog#september-24-2024) explicitly names both stable 002 models; the dated developer release corroborates it. |
| `gemini-1.5-pro-002` | 2024-09-24 | Same stable 002 release. |
| `gemini-2.0-flash-001` | 2025-02-05 | [Gemini API changelog, February 5, 2025](https://ai.google.dev/gemini-api/docs/changelog#february-5-2025) explicitly names stable 001. The December 2024 experimental model is a different identity. |
| `gemini-2.0-pro-exp-02-05` | 2025-02-05 | Same changelog explicitly names this public experimental revision; the dated Google announcement confirms availability. |

Vertex's [May 24, 2024 release notes](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/release-notes#May_24_2024) name both 001 models one day later. We use the earlier Gemini API date for first public availability. This changes Pro 001's date from the May 24 value in Epoch's table; Flash 001's May 23 value is corroborated. The earlier 1.5 previews are separate endpoints and do not establish stable 001 availability.

Retained original source files, URLs and SHA256 hashes are in `agent-work/sources/epoch/gemini-table-models/provenance.json`. The original 1.5 technical report is retained at `agent-work/sources/epoch/gemini15-original-report.pdf`.
