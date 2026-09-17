# Epoch: final historical model identities and size estimates

These are four new model records and one unchanged shared record. Active parameter counts are estimates, distinct from the source's mean output tokens. The coefficient remains twice active parameters; the scenarios below are judgmental sensitivity ranges, not confidence intervals.

## gemini10pro

The exact model is `gemini-1.0-pro-001`. Google's [model lifecycle table, “Retired models”](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/learn/model-versions) gives its release date as **February 15, 2024**, corroborated by the [GA announcement](https://cloud.google.com/blog/products/ai-machine-learning/gemini-on-vertex-ai-expands). The December 2023 launch of the earlier `gemini-pro` alias is not used to backdate this stable revision.

The [original Gemini report](https://storage.googleapis.com/deepmind-media/gemini/gemini_1_report.pdf), Table 1, describes Pro as optimized for serving cost and latency, between Ultra and the on-device Nano models. It does not disclose Pro's parameter count. Table 2 compares its general text capabilities with contemporary models including Llama 2; that establishes the comparison class, not a parameter equation.

Central active size is **70B**, transferred from the contemporary general-purpose Llama 2 70B serving model, whose [original Meta model card](https://github.com/meta-llama/llama/blob/main/MODEL_CARD.md) reports the size. This is a weak peer prior for text inference, not a claim that the architectures or capabilities are identical. Neither a Gemini expert count nor a model-specific size measurement was recovered. The **20–200B** range allows substantially smaller or larger active models. Coefficient: **1.4e11 FLOPs/token**. It does not include a visual encoder workload because these observations use text inputs.

## qwenturbo24

The source identifies `qwen-turbo-2024-11-01`. Footnote 1 of the [Qwen2.5 report](https://arxiv.org/html/2412.15115v2) explicitly identifies that endpoint as Qwen2.5-Turbo. The team's [November 15, 2024 announcement](https://qwenlm.github.io/blog/qwen2.5-turbo/) releases its 1M-context version through the API. We use **November 15**, not the November 1 snapshot suffix. The announced context extension and the report's endpoint identity refer to the same Turbo version.

The report establishes a MoE architecture with shared experts and routed experts, but gives no active size. Central **14B** is transferred from the earlier same-family MoE [Qwen2-57B-A14B](https://huggingface.co/Qwen/Qwen2-57B-A14B-Instruct/blob/main/README.md), whose comparison table explicitly lists 14B activated parameters. Both are intended to provide efficient general text inference; this is an architectural-family prior, not a claim that Turbo is that checkpoint. A **4–40B** sensitivity allows different expert dimensions and routing. Coefficient: **2.8e10 FLOPs/token**.

## qwenplus25

The exact snapshot is `qwen-plus-2025-01-25`, without the experimental suffix used for a later Qwen Chat label. Alibaba's [release table](https://www.alibabacloud.com/help/en/model-studio/newly-released-models), under International deployment, lists this exact snapshot on **January 30, 2025**. The mainland table lists it on February 3. We use the earlier documented public deployment, rather than January 25 from the model name. The current [model page](https://www.alibabacloud.com/help/en/model-studio/qwen-plus) separately preserves this exact revision and its changes.

The Qwen2.5 report identifies the Plus family as MoE; its footnote leaves the new Plus endpoint unspecified, so it does not establish that its unreleased revision is the January snapshot. The family's [original September announcement](https://qwenlm.github.io/blog/qwen2.5/) directly compares Qwen-Plus with DeepSeek-V2.5. We use that named contemporary MoE peer's **21B active** size, reported in [DeepSeek's own model comparison](https://huggingface.co/deepseek-ai/DeepSeek-V3/blob/main/README.md), as the central estimate. This transfers an active-compute scale across models and a later Plus revision; it is not inferred from the reported performance advantage. The **8–80B** sensitivity allows substantial differences in expert activation. Coefficient: **4.2e10 FLOPs/token**.

## qwenmax25

The [Qwen team's January 28, 2025 announcement](https://qwenlm.github.io/blog/qwen2.5-max/) explicitly makes `qwen-max-2025-01-25` available through the API. The release date is therefore **January 28**, with January 25 retained in the snapshot identifier. The article identifies Qwen2.5-Max as a large MoE trained on over 20 trillion tokens, without disclosing active parameters.

The announcement directly names DeepSeek-V3 as its contemporary MoE comparison. We transfer **37B active** from that model's [original reported count](https://huggingface.co/deepseek-ai/DeepSeek-V3/blob/main/README.md). Both are large general-purpose MoEs, but their routing, total size and training efficiency may differ. Neither benchmark scores nor a “hundreds of billions” total-size label determine active size. The **15–150B** sensitivity spans roughly 0.4–4 times the chosen peer scale. Coefficient: **7.4e10 FLOPs/token**.

## gemini20pro

`gemini-2.0-pro-exp-02-05` is already in the accepted model registry. Its model row is copied exactly for consistency checks: February 5, 2025, **100B active**, **2e11 FLOPs/token**, with the existing **30–300B** scenario. The [original Google changelog](https://ai.google.dev/gemini-api/docs/changelog#february-5-2025) names this experimental release. The [accepted model evidence](epoch-gemini-table-models.md#gemini-pro) explains the weak shared frontier-model size prior; no new size claim is introduced here.

## Retained originals

`agent-work/sources/epoch/final-table-models/provenance.json` records original URLs, retained filenames and hashes. Google's tokenizer files and SDK mappings are retained under `agent-work/sources/epoch/gemini-table-models/`. Qwen's tokenizer is pinned to `Qwen/Qwen2.5-72B-Instruct` revision `495f39366efef23836d0cfae4fbe635880d2be31`; the model's scale is not used for the three API parameter estimates. Tokenizer identity and reconstruction are explained in [the observation note](epoch-final-table.md).
