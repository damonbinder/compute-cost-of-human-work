# Codex Python fine-tuning

[Chen et al.,2021](https://arxiv.org/abs/2107.03374), sections3.1–3.4 and Table1, is the original source. It fine-tunes GPT-family checkpoints for100billion Python-code tokens. The starting GPT models have near-zero HumanEval performance; their prior web/text training is excluded. The source does not establish that their pretraining contained literally no code. The three research checkpoints below have no verified exact first-public release day; neither the paper date nor a later Codex product release is assigned to them.

Training is approximated by6PT, with a multiply-add counted twice. The reported nominal parameter counts are used consistently. A monitoring allowance of one forward token per100training tokens adds0.333% to6PT; the paper does not supply counters for intermediate evaluations. The sensitivity runs from6PT alone to1.30×6PT plus monitoring at10% of training tokens. This covers a conventional attention/accounting allowance, not a measured training-compute interval. It excludes unrelated model-size experiments, Codex-S supervised fine-tuning and separate later task-performance runs. The Python dataset itself is collected human code, so there is no synthetic-data helper here. Arithmetic is in [calculate.py](calculate.py), with inputs and outputs retained under sources.

The human estimates and inspected problem examples are in [Python learning estimates](../python-learning-review/python-learning.md). Humans start unable to write these Python functions; the target is comparable first-submission functional correctness. This is a narrow acquisition comparison, not a claim that an introductory course exactly reproduces Codex's pattern of successes and failures. The AI pass@1 values are estimated by sampling at an appropriate temperature; humans are assigned a single unaided final submission per unseen problem. Sampled pass@1 is not a demand that the human solve every item or make100attempts.

## agen-codexfer-codex300m

300million reported parameters;100billion training tokens; near0%→13.17% HumanEval pass@1. Human estimate: 35 hours, with 12–100-hour scenarios, from no programming to basic expressions, functions and simple list/string operations.

## agen-codexfer-codex2p5b

2.5billion reported parameters;100billion training tokens; near0%→21.36% pass@1. Human estimate: 70 hours, with 25–200-hour scenarios, from no programming to broader list/string transformations and boundary handling.

## agen-codexfer-codex12b

12billion reported parameters;100billion training tokens; near0%→28.81% pass@1. Human estimate: 110 hours, with 40–350-hour scenarios, from no programming to composed functions, simple counting/search and mixed problem practice. The paper's much higher pass@100 is not the endpoint used here.
