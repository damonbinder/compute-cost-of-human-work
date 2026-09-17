# METR expanded model coefficients

All sizes below are estimates, not vendor disclosures for these exact aliases. FLOPs/token = 2 × active parameters, counting multiply and add separately. The shared method excludes context-dependent attention and cache-specific savings; `compute_flops` adds the attention term and rebuilds the processed positions (`research/attention-correction.md`). Sizes are never fitted to human duration or task performance. Separate model IDs preserve unresolved snapshots/configurations without inventing a revision. Release dates follow the pinned METR release registry; davinci-002 has no exact public release date established here.

The currently reviewed production model registry was consulted only under the parent's explicit instruction to share already-reviewed model assumptions. Its GPT-4o coefficient is **50B active**, and GPT-5 is **100B active**. No old task estimates or legacy notes were consulted.

| Model ID | Active parameters | FLOPs/token | Basis |
|---|---:|---:|---|
| davinci-002-metr | 175B | 350B | Original GPT-3 family transfer |
| gpt-4-0314 | 275B | 550B | Epoch arithmetic-equivalent model |
| claude-3-5-sonnet-20241022 | 100B | 200B | 400B total estimate × assumed quarter activation |
| claude-3-7-sonnet | 100B | 200B | Sonnet-family transfer |
| gpt-4o-metr | 50B | 100B | Reviewed shared GPT-4o central estimate |
| gpt-5-metr | 100B | 200B | Reviewed shared GPT-5 central estimate |
| o1-metr | 50B | 100B | GPT-4o-family proxy |
| claude-opus-4-6 | 100B | 200B | Original serving-throughput analysis |
| gemini-3-pro | 100B | 200B | Contemporary frontier-model peer transfer |
| gpt-5-3-codex | 100B | 200B | GPT-5-family transfer |

## davinci-002-metr

The [original GPT-3 paper](https://arxiv.org/abs/2005.14165) reports its largest dense model as 175B. [OpenAI's replacement announcement](https://openai.com/index/gpt-4-api-general-availability/) makes davinci-002 the successor to curie/davinci and describes it as a new base GPT-3 model; it does not disclose davinci-002's size. METR calls the evaluated alias `davinci-002 (GPT-3)` but assigns the original GPT-3 date. We use 175B as a family-scale prior, not an architectural measurement of the replacement. Its much cheaper serving could reflect model compression or hardware/serving improvements; it cannot establish a parameter count. All 24 affected rows are explicit assumed-input estimates, highly sensitive to this transfer. The endpoint release date is **2023-08-22**, when [OpenAI explicitly made davinci-002 available](https://openai.com/index/gpt-3-5-turbo-fine-tuning-and-api-updates/). This supersedes the previous blank date and does not reuse the original GPT-3 launch. The announcement does not establish its parameter count.

## gpt-4-0314

[Epoch's original MoE inference analysis](https://epoch.ai/gradient-updates/moe-vs-dense-models-inference), section “Estimating the MoE inference edge,” estimates GPT-4 arithmetic equivalent to a 275B dense model. That is the relevant operation-based size, not its 1.8T total or its much larger memory-bound serving equivalent. We transfer this GPT-4 architecture estimate to the original 0314 alias. It is not an OpenAI-disclosed architecture. 275B × 2 = 550B FLOPs/token.

## claude-3-5-sonnet-20241022

[Epoch's original model-size analysis](https://epoch.ai/gradient-updates/frontier-language-models-have-become-much-smaller) estimates Sonnet 3.5 at **400B total**, not active. To convert total into an operation coefficient, use an explicit MoE activation prior of one-quarter, as used in [Epoch's ChatGPT energy model](https://epoch.ai/gradient-updates/how-much-energy-does-chatgpt-use): 400B × 0.25 = 100B. Applying GPT-4o's sparsity prior to Sonnet is our additional assumption; neither Sonnet's total nor its sparsity is disclosed. A 1/8 to 1/2 activation sensitivity gives 50–200B active at the same total. The ambiguous Sonnet 3.5 task lead is resolved to the source's New October 2024 variant, consistently across all 36 rows, rather than mixing old and new runs.

## claude-3-7-sonnet

[Anthropic's launch](https://www.anthropic.com/news/claude-3-7-sonnet) describes an upgraded Sonnet and hybrid reasoning, not parameter counts. We retain the 3.5 Sonnet central active-size estimate for this successor: 100B. This is an explicit same-family architecture-scale transfer, not a finding that their architectures match. Extra inference reasoning is already in native run tokens and must not be added again. A 50–200B sensitivity encompasses substantial family-scale uncertainty.

## gpt-4o-metr

[Epoch's energy analysis](https://epoch.ai/gradient-updates/how-much-energy-does-chatgpt-use) gives a central 200B total estimate and assumes a quarter active. Thus central active = 50B, not the 100B active from its pessimistic 400B-total energy case. This exactly retains the parent's reviewed registry coefficient. The METR alias does not establish the registry's August 6 snapshot; the separate METR ID preserves that distinction. No independently observed image-encoder calls occur in these exported text-agent workload totals.

## gpt-5-metr

[Epoch's original GPT-5 analysis](https://epochai.substack.com/p/notes-on-gpt-5-training-compute) estimates about 100B active from pricing, speed and industry context; this is the parent's reviewed coefficient. The METR alias names GPT-5, but its raw record does not identify the reasoning-effort API argument. Accordingly we keep a distinct configuration ID rather than claiming the registry's high-reasoning configuration, while transferring the same architecture coefficient. Reasoning contributes to source native tokens.

## o1-metr

No disclosed parameter count was found. Use the reviewed GPT-4o central 50B active as an explicit contemporary OpenAI-model scale proxy. This is weaker evidence than GPT-4o's own estimate: family/provider proximity does not prove equal size. Reasoning-model query length is represented in measured native tokens, not an arbitrary extra FLOP multiplier. A 25–150B sensitivity should be used for analyses sensitive to the o1 point positions. [Epoch's energy analysis](https://epoch.ai/gradient-updates/how-much-energy-does-chatgpt-use) specifically distinguishes longer reasoning from per-token work and acknowledges unknown reasoning architecture; it does not report o1 as 50B.

## claude-opus-4-6

The [original March 2026 analysis by Unexcitedneurons](https://unexcitedneurons.substack.com/p/estimating-the-size-of-claude-opus) estimates 4–4.5 TB/s effective Vertex weight bandwidth from three open-model serving rates. Dividing by Opus 4.6's reported 43 tokens/s gives 93–105 GB of weights per token. At assumed FP8 that is approximately 100B active; use this rounded central estimate. This is an original quantitative estimate, not a reposted rumor, but equal serving bandwidth and weight precision are unverified. BF16 implies roughly 50B and mixed FP8/FP4 roughly 130–150B. We preserve a 50–150B sensitivity, and do not confuse serving bytes with a measured operation count.

## gemini-3-pro

The [official model card](https://deepmind.google/models/model-cards/gemini-3-pro/) identifies a sparse MoE with a 1M context window, without disclosing size or sparsity. Searches found no sufficiently grounded public active-parameter estimate. The best available central proxy is therefore 100B, transferred from contemporary frontier reasoning models with independently researched size estimates (GPT-5 and Opus 4.6 above). The justification is model role/generation plus comparable deployed-model scale, not equality of benchmark ability or price. This is the weakest closed-model estimate here; 30–300B is a sensitivity interval, not a confidence interval. It remains a substantive estimated input requiring reviewer judgment, rather than being described as a measurement.

## gpt-5-3-codex

[OpenAI's launch](https://openai.com/index/introducing-gpt-5-3-codex/) identifies the coding successor and a 25% speed improvement, without an architecture disclosure. Transfer GPT-5's 100B active as an unchanged family-scale prior. A serving-speed improvement cannot uniquely distinguish hardware, caching, quantization, distillation or parameter changes and is not directly applied as a parameter reduction. A 50–200B sensitivity reflects that unresolved architecture transfer.
