# Independent model coefficients and availability

All coefficients use the specified 2 × active parameters approximation, not latency, price, or total MoE size. The convention omits context-dependent attention, speculative-decoding implementation details and processing differences between prefills and generation; the attention term is added back in each row's `compute_flops` (`research/attention-correction.md`). Model dates were researched independently; the scatter CSV's dates are not adopted as release evidence.

| Model | Active parameters | First public release | Original evidence |
|---|---:|---|---|
| Llama 3 70B Instruct | 70B | 2024-04-18 | [Meta model card, model table and release field](https://huggingface.co/meta-llama/Meta-Llama-3-70B-Instruct) |
| Qwen2.5 32B Instruct | 32.5B | 2024-09-19 | [Qwen model card](https://huggingface.co/Qwen/Qwen2.5-32B-Instruct); [dated Qwen launch](https://qwenlm.github.io/blog/qwen2.5/) |
| DeepSeek V3 0324 | 37B | 2025-03-24 | [original V3 active count](https://api-docs.deepseek.com/news/news1226/); [revision card](https://huggingface.co/deepseek-ai/DeepSeek-V3-0324); [dated API change](https://api-docs.deepseek.com/updates/#date-2025-03-24) |
| DeepSeek V3.2 | 37B | 2025-12-01 | [provider technical documentation, pages 2–3](https://fe-static.deepseek.com/chat/transparency/deepseek-v3.2-model-card-0414-EN.pdf) |
| gpt-oss-120b | 5.1B | 2025-08-05 | [OpenAI release](https://openai.com/index/introducing-gpt-oss/) |
| Qwen3 235B A22B Thinking 2507 | 22B | 2025-07-25 | [Qwen model card](https://huggingface.co/Qwen/Qwen3-235B-A22B-Thinking-2507); [official dated repository news](https://github.com/QwenLM/Qwen3#news) |

DeepSeek V3.2's downloaded `config.json` and [technical paper §2](https://arxiv.org/html/2512.02556v1) establish the sparse-attention architecture; the later official model card explicitly supplies the rounded 37B active count, so we do not manufacture a more precise count by adding an independently guessed indexer size to that reported total. [December 1 API history](https://api-docs.deepseek.com/updates/#date-2025-12-01) maps both chat/reasoner aliases to V3.2; the selected reasoning run was December 16. Current API aliases subsequently changed, making run date important.

Qwen2.5's original card reports 32.5B total versus 31.0B non-embedding; we use the reported full dense count consistently with the dataset's shared coefficient convention. Qwen3's 235B total is not its active count. gpt-oss's 120B marketing label likewise is not its per-token active computation.
