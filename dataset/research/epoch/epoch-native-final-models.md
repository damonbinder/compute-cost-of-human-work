# Epoch native expansion: model evidence

This note supports the 12 model records used by the 16 expansion-14 runs. The native endpoints are preserved in `native-final-model-plan.json`; they are not replaced by whatever newer model currently answers a similar alias. None of these exact models was already in the registry checked for this submission. Existing family records were compared only after reopening the original evidence.

The coefficient is twice active parameters. It approximates text-model matrix operations, omitting context-dependent attention, speculative-decoding work and differences between prompt processing and generation; the attention term is added back in each row's `compute_flops` (`research/attention-correction.md`). Weight precision does not change the FLOP convention. Token workload, cache treatment and missing-call estimates belong in the companion usage note.

| Model | Public availability | Active parameters | Basis | Parameter sensitivity |
|---|---|---:|---|---:|
| DeepSeek V4-Pro preview | 2026-04-24 | 49B | Reported | — |
| Gemini 3.1 Pro preview | 2026-02-19 | 100B | Estimated family transfer | 30–300B |
| Gemini 3.1 Pro preview customtools | 2026-02-19 | 100B | Same family transfer | 30–300B |
| Gemini 3 Flash preview | 2025-12-17 | 40B | Estimated peer transfer | 10–150B |
| Gemini 3.5 Flash | 2026-05-19 | 40B | Same Flash assumption | 10–150B |
| GLM-5.2 | 2026-06-16 | 40B | Estimated from family configuration | 35–45B |
| GPT-5 mini 2025-08-07 | 2025-08-07 | 20B | Estimated small-model transfer | 10–40B |
| GPT-5.4 2026-03-05 | 2026-03-05 | 100B | Estimated GPT-5 transfer | 50–200B |
| Kimi K2.6 | 2026-04-20 | 32B | Reported | — |
| Claude Opus 4.7 | 2026-04-16 | 100B | Estimated Opus transfer | 50–200B |
| Qwen3.6-Plus | 2026-04-02 | 17B | Estimated preceding-Plus transfer | 8–68B |
| Qwen3.7-Max | 2026-05-21 | 100B | Estimated frontier-model transfer | 30–300B |

These are sensitivity scenarios, not confidence intervals or hard bounds. They scale the coefficient directly. A reported parameter count does not remove attention and workload-accounting limitations. The Flash and Qwen3.7 assumptions have the weakest model-specific support; downstream comparisons should expose their broad scenarios.

## deepseek-v4-pro-preview

[DeepSeek's April 24 preview announcement](https://deepseek.com/en/news/v4-preview/) establishes public API availability and reports 1.6T total parameters, 49B active. The source run began June 18, before the August general release, so the correct record is the preview even though the native endpoint is `epoch/deepseek-v4-pro`. No finer checkpoint is established. Use 49B active and 98B FLOPs/token. The general coefficient does not model the context-dependent savings of DeepSeek's attention architecture.

## gemini-31-pro-previews

The [February 19 Gemini API changelog](https://ai.google.dev/gemini-api/docs/changelog) announces both `gemini-3.1-pro-preview` and the separate `gemini-3.1-pro-preview-customtools` endpoint. The latter prioritizes custom tools when both bash and custom tools are supplied. Keep separate model records, with one parameter assumption.

The [official 3.1 Pro card](https://deepmind.google/models/model-cards/gemini-3-1-pro/) states that it is based on Gemini 3 Pro. It does not disclose size. Use 100B active, transferring the existing Gemini 3 Pro assumption after verifying its numerical anchors: [Epoch's original GPT-5 estimate](https://epochai.substack.com/p/notes-on-gpt-5-training-compute) explicitly gives approximately 100B active, and [the original Opus analysis](https://unexcitedneurons.substack.com/p/estimating-the-size-of-claude-opus) gives roughly that scale under FP8 serving assumptions. Architecture lineage supports reusing the Pro assumption; it does not prove equal sizes. Retain the Pro family's 30–300B scenario.

## gemini-flash

[Google's December 17 launch](https://blog.google/innovation-and-ai/technology/developers-tools/build-with-gemini-3-flash/) establishes the Flash preview date. The [API changelog](https://ai.google.dev/gemini-api/docs/changelog) establishes general availability of `gemini-3.5-flash` on May 19. The [3 Flash card](https://deepmind.google/models/model-cards/gemini-3-flash/) identifies a Gemini 3 Pro lineage; the [3.5 Flash card](https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-3-5-Flash-Model-Card.pdf) identifies a 3 Flash lineage. Neither reports active size.

Use a shared 40B active estimate for this efficient-model tier. The numerical scale is a rounded peer prior from disclosed contemporary sparse models: [GLM-5, 40B](https://huggingface.co/zai-org/GLM-5), [Kimi K2.6, 32B](https://huggingface.co/moonshotai/Kimi-K2.6), and [DeepSeek V4-Pro, 49B](https://deepseek.com/en/news/v4-preview/). These are available architecture-scale anchors; they do not measure Flash. Google's speed-oriented design supports treating Flash separately from the Pro prior, but neither latency nor price is inverted into parameter count. The 10–150B scenario admits much smaller models as well as the entire central Pro scale. Both Flash versions share this assumption because no size change is established and the original cards identify their lineage.

## glm-52

The [official API release notes](https://docs.z.ai/release-notes/new-released) date GLM-5.2 to June 16. The later Hugging Face article is not its first public release.

The [GLM-5.2 configuration](https://huggingface.co/zai-org/GLM-5.2/blob/main/config.json) and [GLM-5 configuration](https://huggingface.co/zai-org/GLM-5/blob/main/config.json) share the main dimensions: 78 layers, width 6,144, three dense layers of intermediate width 12,288, MoE intermediate width 2,048, 256 routed experts with eight selected and one shared expert, and the same explicit low-rank attention projection dimensions. [GLM-5's model card](https://huggingface.co/zai-org/GLM-5) reports 40B active. These facts support a rounded 40B estimate for 5.2; its own card does not directly report that active count.

GLM-5.2 changes indexer sharing and context settings. Its [model card](https://huggingface.co/zai-org/GLM-5.2) reports a 2.9× per-token saving at 1M context from IndexShare. Do not divide the shared coefficient by 2.9: that context-dependent saving is not a uniform change in main active weights. The 35–45B scenario is an accounting stress test around the rounded family count, allowing for ancillary projections, output/embedding conventions and the improved MTP component. It is not a measured interval, and does not quantify the long-context attention term, which `compute_flops` carries separately (`research/attention-correction.md`). The public configuration is supporting architecture evidence, not proof of the exact API serving graph.

## gpt-5-mini-2025-08-07

The [OpenAI changelog](https://developers.openai.com/api/docs/changelog) announces the GPT-5 family, including mini, on August 7. The [model documentation](https://developers.openai.com/api/docs/models/gpt-5-mini) identifies the exact dated snapshot and describes a smaller, efficient GPT-5 variant; no count is disclosed.

Use 20B active as an explicit small-reasoning-model transfer. The original numerical anchor is [Epoch's capability-progress analysis](https://epoch.ai/data-insights/ai-capabilities-progress-has-sped-up), data-table row `o4-mini-2025-04-16_medium`, whose notes estimate 10–30B active. Its midpoint is 20B. This connects mini to an independently estimated small OpenAI reasoning model rather than assuming the full GPT-5 size. It does not establish equal architectures. The 10–40B scenario is wider than the donor's stated range to allow for the transfer. The retained HTML/text contains the table notes even when a browser text view omits them.

## gpt-54-2026-03-05

The [March 5 OpenAI changelog](https://developers.openai.com/api/docs/changelog) establishes public API release; the [model page](https://developers.openai.com/api/docs/models/gpt-5.4) identifies the exact snapshot. Use 100B active, transferring [Epoch's direct GPT-5 estimate](https://epochai.substack.com/p/notes-on-gpt-5-training-compute) within the full-size GPT-5 family. That article's number is already active parameters: do not divide it by four. No architecture disclosure establishes a size change in 5.4. The 50–200B scenario matches the existing later-GPT-5 family treatment.

## kimi-k26

[Kimi's original release account](https://www.kimi.com/en/help/agent/agent-overview) dates release and open sourcing to April 20. Its [original model summary](https://huggingface.co/moonshotai/Kimi-K2.6) reports 1T total, 32B active and the same architecture as K2.5; it separately lists a 400M vision encoder. Use the 32B language-model count for these text-only coding runs. Native INT4 weight format does not halve multiply/add FLOPs, and no image processing is inferred from model capability alone.

## claude-opus-4-7

[Anthropic's April 16 announcement](https://www.anthropic.com/news/claude-opus-4-7) establishes release and the exact API name. It does not disclose size. Use 100B active, transferring [Unexcitedneurons' original Opus 4.5/4.6 analysis](https://unexcitedneurons.substack.com/p/estimating-the-size-of-claude-opus). That work calibrates effective weight bandwidth on open models; 4–4.5 TB/s divided by 40 tokens/s gives 100–112.5 GB/token for Opus 4.5. Assuming one byte per parameter gives the approximately 100B-active anchor. Hardware, batching, quantization and speculative decoding can break the transfer, so retain a 50–200B scenario for 4.7.

Anthropic also reports a new tokenizer, producing approximately 1.0–1.35× as many tokens on the same input. The native run counters already reflect it. Do not multiply native tokens by 1.35.

## qwen36-plus

[Alibaba's April 2 announcement](https://www.alibabacloud.com/blog/alibaba-unveils-qwen3-6-plus-to-accelerate-agentic-ai-deployment-for-enterprises-and-alibabas-ai-applications_603000) establishes release. [Current original model documentation](https://www.alibabacloud.com/help/en/model-studio/qwen3-6-plus) maps the alias to the April 2 snapshot; the native run's alias alone does not independently prove the historical checkpoint.

The [Qwen3.5-397B-A17B model card](https://huggingface.co/Qwen/Qwen3.5-397B-A17B) explicitly identifies Qwen3.5-Plus as the corresponding hosted version with additional production features and reports 17B active for the open language model. Transfer 17B to the next Plus release as an estimate. No inspected original 3.6 source discloses a replacement parameter count. This family link is firmer than a generic flagship peer prior, but is not exact 3.6 architecture evidence. Use an 8–68B scenario, covering approximately one half to four times the assumed size.

## qwen37-max

[OpenRouter's own provider page](https://openrouter.ai/qwen/qwen3.7-max) explicitly records public release on May 21. [Alibaba's May 21 announcement](https://www.alibabacloud.com/blog/qwen3-7-the-agent-frontier_603154) corroborates the launch but says Model Studio availability is forthcoming; it is not alone sufficient to establish API availability that day.

[Alibaba's current model documentation](https://www.alibabacloud.com/help/en/model-studio/qwen3-7-max) maps the text-only alias to the May 20 snapshot and distinguishes both the preview and a June 8 multimodal snapshot. Snapshot dates are not automatically release dates. The June 19 native endpoint is unversioned; retain that unresolved revision in the record instead of calling it the June 8 model.

No parameter disclosure was established. Use a 100B active frontier-model prior from the original GPT-5/Opus numerical anchors above, with 30–300B sensitivity, consistently with the Pro peer treatment. Alibaba describes Max as the largest model in this series; that supports keeping it separate from the Plus transfer but does not determine a numerical count. The estimate is weak and could change substantially with architectural evidence.

## Retained evidence and registry check

Original responses and derived plain-text extracts are under `collection-work/batches/epoch/sources/native-final-models/`. `source-locators.json` records original URLs and retrieval date; `source-manifest.json` records file sizes and SHA-256 hashes. Empty JavaScript-only blog content and the generic Qwen update page are retained as retrieval artifacts, not evidence for the counts.

The current GPT-5 registry notes already cite Epoch's direct 100B-active estimate correctly: `research/fresh-five-models.md`, `research/metr/metr-expanded-models.md`, and `research/epoch/epoch-native-families.md`. No production correction is requested. This submission adds candidate model evidence only.
