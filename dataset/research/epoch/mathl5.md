# MATH Level 5: task-specific estimate

Work is one uniformly sampled Level-5 test question across all seven subjects. This is a **judgment-based human baseline**: its duration and approximately 90% accuracy target are assumptions, with the evidence and sensitivity described below.

## Original questions and input compute

The [authors' repository](https://github.com/hendrycks/math) links a [public dataset distribution](https://huggingface.co/datasets/qwedsacf/competition_math). We separately downloaded all seven standard test-partition Parquets from [EleutherAI's dataset distribution](https://huggingface.co/datasets/EleutherAI/hendrycks_math), retaining 5,000 test records and exactly 1,324 Level-5 problems. The distribution matches the source MATH task structure, rather than relying on the lead label alone. Original problem/solution records remain in the Parquets. The generator selects by literal `level == 'Level 5'`.

Input counting uses the three saved family tokenizers on the full problem, including Asymptote text where present, plus **50 assumed instruction/chat tokens**. The exact old Epoch MATH wrapper was not recovered; no few-shot examples are presumed. This yields means 135.9796 (Llama), 138.5801 (Qwen), 134.3369 (DeepSeek). [Epoch's output-length data](https://epoch.ai/data-insights/output-length) supplies the output means and accuracy, with the exact identifier/benchmark combination in each row. Compute = 2 × active parameters × (estimated input + reported output). Both wrapper and template-transfer assumptions remain explicit. Models here are non-reasoning configurations; their visible output is the source output workload, with no separate reasoning amount added.

## Human estimate

[MATH paper §3.1, “Human-Level Performance,” PDF page 5](https://arxiv.org/pdf/2103.03874) timed six people for one hour on 20 mixed problems. The paper's 18/20 (90%) result describes an IMO gold medalist; Appendix A.6 presents the test material; it is not an observed Level-5 score. Treating 60/20 = 3 minutes as Level-5 timing would be a bad transfer. Our baseline instead is a highly accomplished competition solver, given an **assumed average active-effort budget of 600 seconds per attempted Level-5 problem**, targeting about 90% accuracy as an explicit assumption. The longer allowance is a judgment for the harder selected set, not a measured multiplier.

Inspection covered contrasting subject/problem types: a complex-number system requiring products and a square root; classifying quartic polynomials satisfying P(x²)=P(x)P(-x), which requires multiple coefficient cases; converting a repeating decimal and reciprocating it, which is short once the representation is recognized; a square/equilateral-triangle problem using 30-60-90 ratios; a piecewise-linear graph whose invertibility is controlled by the extremal slopes; and finding a reflection matrix's eigenvector. The set contains 307 algebra, 280 intermediate algebra, 193 prealgebra, 154 number theory, 135 precalculus, 132 geometry and 123 counting/probability items. Thus “Level 5” does not mean every item is a late olympiad problem. This assumed ten-minute average active-effort budget is meant to cover both quick recognitions and extended algebra/casework. Its bounds are read off the OTIS testsolving table cited below rather than taken as a factor on the central. Twenty-nine of the thirty problems there have a recorded median first-try solve; the mean of those medians is 415 seconds, the mean over AIME positions 1–10 is 248 seconds, and the mean over positions 11–15 is 785 seconds. Those two subset means are the bounds, 250 and 785 seconds: the low is the reading in which this set's 193 prealgebra, 307 algebra and 123 counting items put it in the early-AIME band, and the high is the reading in which the late intermediate-algebra, precalculus and geometry items dominate. The central sits above the midpoint because the OTIS medians are conditional on a correct first-try solve and charge nothing for the checking a 90% target needs.

The [OTIS original testsolving tables](https://web.evanchen.cc/exams/sols-OTIS-Mock-AIME-2025.pdf), §4.1, supply a reasonableness check: actual successful first-attempt medians range from a little over a minute on early exercises to over 20 minutes on difficult geometry. They do not directly measure MATH. Human can view diagrams while the selected text-only models receive source diagram code, a real supplied-information difference. Quality approximately 90% remains an assumption, so the original mixed-test gold medal performance is not presented as a measured matched-set result. AI scores 22.55%, 56.07%, and 75.55% are below that target.

No training or acquisition claim is made. The original mixed-difficulty test is supporting evidence, not a measurement of this Level-5 endpoint.

<!-- generated-point-appendix -->

## reas-epoch-mathl5-llama3-70b

Model: Meta-Llama-3-70B-Instruct. Source: https://epoch.ai/data-insights/output-length; scatter_data.csv Identifier=Meta-Llama-3-70B-Instruct, Benchmark=MATH level 5; performance: Best score (across scorers).

Inputs/accounting: `{"accuracy": 0.225547583081571, "input": 135.9796072507553, "output": 343.607250755287}`.

Counted tokens per work unit = 479.586858; coefficient = 1.4e+11 FLOPs/token; product = **6.71421601208e+13 FLOPs**. Human = 600 seconds. AI exact-answer accuracy 22.5548%. Human baseline is an assumed highly accomplished competition solver (IMO-gold-medalist level) targeting approximately 90% correct on this set, not an observed Level-5 human score.

## reas-epoch-mathl5-qwen25-32b

Model: Qwen2.5-32B-Instruct. Source: https://epoch.ai/data-insights/output-length; scatter_data.csv Identifier=qwen2.5-32b-instruct, Benchmark=MATH level 5; performance: Best score (across scorers).

Inputs/accounting: `{"accuracy": 0.5607061933534743, "input": 138.5800604229607, "output": 666.1555891238671}`.

Counted tokens per work unit = 804.7356495; coefficient = 6.5e+10 FLOPs/token; product = **5.23078172205e+13 FLOPs**. Human = 600 seconds. AI exact-answer accuracy 56.0706%. Human baseline is an assumed highly accomplished competition solver (IMO-gold-medalist level) targeting approximately 90% correct on this set, not an observed Level-5 human score.

## reas-epoch-mathl5-v3-0324

Model: DeepSeek-V3-0324. Source: https://epoch.ai/data-insights/output-length; scatter_data.csv Identifier=DeepSeek-V3-0324, Benchmark=MATH level 5; performance: Best score (across scorers).

Inputs/accounting: `{"accuracy": 0.75547583081571, "input": 134.3368580060423, "output": 1498.9977341389729}`.

Counted tokens per work unit = 1633.334592; coefficient = 7.4e+10 FLOPs/token; product = **1.20866759819e+14 FLOPs**. Human = 600 seconds. AI exact-answer accuracy 75.5476%. Human baseline is an assumed highly accomplished competition solver (IMO-gold-medalist level) targeting approximately 90% correct on this set, not an observed Level-5 human score.
