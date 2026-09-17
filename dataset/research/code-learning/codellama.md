# Llama2 to CodeLlama

[Rozière et al.](https://arxiv.org/html/2308.12950v3), sections2.1,2.6 and Table2, reports500billion further code-heavy training tokens plus long-context fine-tuning. These are the base CodeLlama models, with neither the extra Python specialization nor instruction fine-tuning. [Meta's original release](https://about.fb.com/news/2023/08/code-llama-ai-for-coding/) establishes August24,2023 for both sizes.

The reported7B and34B nominal parameter counts give the shared coefficient2P. Training uses6PT; the shared inference coefficient is not multiplied directly by training tokens. For7B, LCFT is3,000steps×2million tokens=6billion tokens; for34B it is11,000×1million=11billion. Totals are506billion and511billion. The source rounds batch sizes to millions; these totals preserve its reporting precision. A monitoring allowance adds one forward token per100update tokens; it is assumed because monitoring counters are not reported. Sensitivity allows0–10% monitoring-token volume and0–30% extra training operations for attention/other omitted arithmetic. Prior Llama2 training and unrelated ablations are excluded. See [calculate.py](calculate.py).

[Python learning estimates](../python-learning-review/python-learning.md) defines ordinary learners' initial skills and estimated additional practice. The human target is Python HumanEval only. AI training spans other languages, infilling and long contexts; the row does not price acquisition of all those capabilities by a human. The two starting Llama2 models already solve some Python problems; counting a full beginner programming course again would overstate the marginal transition.

## agen-codexfer-codellama7b

HumanEval greedy pass@1 improves12.2%→33.5%. The corroborating3-shot MBPP score improves20.8%→41.4%, but MBPP is not used to calibrate hours. Human estimate: 90 additional hours, with 30–300-hour scenarios, from elementary Python at the stated starting score to more robust composed-function solving.

## agen-codexfer-codellama34b

HumanEval greedy pass@1 improves22.6%→48.8%; MBPP33.8%→55.0%. Human estimate: 140 additional hours, with 50–450-hour scenarios, from common Python list/string operations at the stated starting score to wider algorithm patterns and robust multi-step specification handling. Neither score is labeled a novice-to-junior employment transition.
