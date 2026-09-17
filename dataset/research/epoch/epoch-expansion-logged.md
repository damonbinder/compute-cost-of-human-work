# Epoch expansion: original logged benchmark workloads

The reviewed human baselines and qualifications in [GPQA](gpqa.md), [OTIS](otis.md), and [SimpleQA-Verified](simpleqa.md) apply to the same source-defined collections. Inputs and outputs here are native recorded workloads, not the older output-only approximation. Plans and dataset identity are checked per run. External reference-answer grading/extraction is outcome evaluation and excluded from solving compute.

For each run, the primary model is the header model. Aggregate all its summary usage, including recorded unsuccessful work, and divide by header results.completed_samples. Repeated epochs are repeated evaluation, not a multi-attempt answer-selection strategy. Mean per-question workload is not multiplied by the number of epochs. Rejected requests add no work; missing response costs are estimated where supported by the [failure audit](epoch-native-usage-audit.md). The source metric may average per-question epoch scores; retain that metric rather than silently replace it with a differently weighted raw success fraction.

Reasoning tokens are included once: the code checks the native identity total = input + output for every selected run. Cache reads are a subset of input and are subtracted; cache writes, when separately reported, are added. Read exclusion approximates cached computation; attention over the reads is priced separately in `compute_flops` (`research/attention-correction.md`). No model token types are inferred from dollar billing.

Claude Opus 4.6 uses the authorized current shared registry assumption of 100B active parameters (200B FLOPs/token), with its existing canonical identity. This is an estimated coefficient, not a disclosed architecture. All its points are derived_assumed_inputs even though token counters are native. Other selected models retain the independently sourced reported coefficients in models.md.


## lang-epoch-simpleqa-opus46

Source: https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/Q7FaUG2XfWePaAjfapJ9dr.eval. Model: claude-opus-4-6; max_tokens=128000.

Native accounting: `{"accuracy": 0.431, "completed": 1000, "config": {"max_retries": 8, "max_tokens": 128000}, "excluded_outcome_evaluator_tokens": {"google/gemini-2.0-flash-001": 1839031}, "primary": "anthropic/claude-opus-4-6", "samples_in_log": 1000, "usage": {"input_tokens": 32285, "input_tokens_cache_read": 0, "input_tokens_cache_write": 0, "output_tokens": 73249, "total_tokens": 105534}}`.

Tokens per completed sample = 105.534; multiply by 200000000000 FLOPs/token = **2.11068e+13 FLOPs**. AI source accuracy 43.1% across 1000 scored completions. Human experienced fact-checker target is assumed approximately 95% on Verified; the original different-sample third-rater agreement was 94.4%.


## lang-epoch-simpleqa-opus46-32k

Source: https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/R9WmNXSxUCeVqBcZjTgEDa.eval. Model: claude-opus-4-6; max_tokens=128000; reasoning_tokens=32000.

Native accounting: `{"accuracy": 0.464859437751004, "completed": 996, "config": {"max_retries": 8, "max_tokens": 128000, "reasoning_tokens": 32000}, "excluded_outcome_evaluator_tokens": {"google/gemini-2.0-flash-001": 1826162}, "primary": "anthropic/claude-opus-4-6", "samples_in_log": 1000, "usage": {"input_tokens": 61058, "input_tokens_cache_read": 0, "input_tokens_cache_write": 0, "output_tokens": 536692, "reasoning_tokens": 239642, "total_tokens": 597750}}`.

Tokens per completed sample = 600.15060241; multiply by 200000000000 FLOPs/token = **1.20030120482e+14 FLOPs**. AI source accuracy 46.4859% across 996 scored completions. Human experienced fact-checker target is assumed approximately 95% on Verified; the original different-sample third-rater agreement was 94.4%.


## lang-epoch-simpleqa-opus46-max

Source: https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/VbtRTM4jN7xRfNyzRC4kXx.eval. Model: claude-opus-4-6; reasoning_effort=xhigh.

Native accounting: `{"accuracy": 0.41041041041041043, "completed": 999, "config": {"max_retries": 8, "reasoning_effort": "xhigh"}, "excluded_outcome_evaluator_tokens": {"google/gemini-2.0-flash-001": 1809083}, "primary": "anthropic/claude-opus-4-6", "samples_in_log": 1000, "usage": {"input_tokens": 49217, "input_tokens_cache_read": 0, "input_tokens_cache_write": 0, "output_tokens": 744307, "reasoning_tokens": 300821, "total_tokens": 793524}}`.

Including recovered or estimated missing work, tokens per completed evaluation = 795.11343175; × 200000000000 FLOPs/token = **1.5902268635e+14 FLOPs**. [Failure accounting](epoch-native-usage-audit.md#lang-epoch-simpleqa-opus46-max). AI source accuracy 41.041% across 999 scored completions. Human experienced fact-checker target is assumed approximately 95% on Verified; the original different-sample third-rater agreement was 94.4%.


## reas-epoch-gpqa-dsv32

Source: https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/CDdjbqiYYPtEBGoZLMPM3n.eval. Model: deepseek-v3.2; default generation configuration.

Native accounting: `{"accuracy": 0.8342352092352093, "completed": 1578, "config": {"max_retries": 8}, "excluded_outcome_evaluator_tokens": {}, "primary": "deepseek/deepseek-reasoner", "samples_in_log": 1584, "usage": {"input_tokens": 392207, "input_tokens_cache_read": 299200, "output_tokens": 11524683, "reasoning_tokens": 11310864, "total_tokens": 11916890}}`.

Including recovered or estimated missing work, tokens per completed evaluation = 7390.28119533; × 74000000000 FLOPs/token = **5.46880808455e+14 FLOPs**. [Failure accounting](epoch-native-usage-audit.md#reas-epoch-gpqa-dsv32). AI source accuracy 83.4235% across 1578 completed evaluation samples; second expert validators answered 161/198 correctly (81.31%); Diamond selection forces the first expert to be correct, so 81.31% is biased upward. Four-choice guessing is 25%.


## reas-epoch-gpqa-gptoss120b

Source: https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/LC5Rhog6wt2PT84CtJ483h.eval. Model: gpt-oss-120b; reasoning_effort=high.

Native accounting: `{"accuracy": 0.7575757575757576, "completed": 396, "config": {"max_retries": 20, "reasoning_effort": "high"}, "excluded_outcome_evaluator_tokens": {}, "primary": "together/openai/gpt-oss-120b", "samples_in_log": 396, "usage": {"input_tokens": 126972, "output_tokens": 4320887, "total_tokens": 4447859}}`.

Tokens per completed sample = 11231.9671717; multiply by 10200000000 FLOPs/token = **1.14566065152e+14 FLOPs**. AI source accuracy 75.7576% across 396 completed evaluation samples; second expert validators answered 161/198 correctly (81.31%); Diamond selection forces the first expert to be correct, so 81.31% is biased upward. Four-choice guessing is 25%.


## reas-epoch-gpqa-opus46-32k

Source: https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/DiXCMhdfhcjaCUSzYWgACy.eval. Model: claude-opus-4-6; max_tokens=128000; reasoning_tokens=32000.

Native accounting: `{"accuracy": 0.9053030303030303, "completed": 1584, "config": {"max_retries": 8, "max_tokens": 128000, "reasoning_tokens": 32000}, "excluded_outcome_evaluator_tokens": {}, "primary": "anthropic/claude-opus-4-6", "samples_in_log": 1584, "usage": {"input_tokens": 513984, "input_tokens_cache_read": 0, "input_tokens_cache_write": 0, "output_tokens": 9382301, "reasoning_tokens": 3648323, "total_tokens": 9896285}}`.

Tokens per completed sample = 6247.65467172; multiply by 200000000000 FLOPs/token = **1.24953093434e+15 FLOPs**. AI source accuracy 90.5303% across 1584 completed evaluation samples; second expert validators answered 161/198 correctly (81.31%); Diamond selection forces the first expert to be correct, so 81.31% is biased upward. Four-choice guessing is 25%.


## reas-epoch-gpqa-opus46-64k

Source: https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/eB9e2mtd5nRwqdFyLEsz6k.eval. Model: claude-opus-4-6; max_tokens=128000; reasoning_tokens=64000.

Native accounting: `{"accuracy": 0.8876262626262627, "completed": 1582, "config": {"max_retries": 8, "max_tokens": 128000, "reasoning_tokens": 64000}, "excluded_outcome_evaluator_tokens": {}, "primary": "anthropic/claude-opus-4-6", "samples_in_log": 1584, "usage": {"input_tokens": 512944, "input_tokens_cache_read": 0, "input_tokens_cache_write": 0, "output_tokens": 10943671, "reasoning_tokens": 4253537, "total_tokens": 11456615}}`.

Tokens per completed sample = 7241.85524652; multiply by 200000000000 FLOPs/token = **1.4483710493e+15 FLOPs**. AI source accuracy 88.7626% across 1582 completed evaluation samples; second expert validators answered 161/198 correctly (81.31%); Diamond selection forces the first expert to be correct, so 81.31% is biased upward. Four-choice guessing is 25%.


## reas-epoch-gpqa-qwen3thinking

Source: https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/gu39ndv9QxWP3NRxSUJRaX.eval. Model: qwen3-235b-a22b-thinking-2507; default generation configuration.

Native accounting: `{"accuracy": 0.8005050505050505, "completed": 396, "config": {"max_retries": 20}, "excluded_outcome_evaluator_tokens": {}, "primary": "alibaba/qwen3-235b-a22b-thinking-2507", "samples_in_log": 396, "usage": {"input_tokens": 106848, "output_tokens": 3263626, "reasoning_tokens": 2954506, "total_tokens": 3370474}}`.

Tokens per completed sample = 8511.2979798; multiply by 44000000000 FLOPs/token = **3.74497111111e+14 FLOPs**. AI source accuracy 80.0505% across 396 completed evaluation samples; second expert validators answered 161/198 correctly (81.31%); Diamond selection forces the first expert to be correct, so 81.31% is biased upward. Four-choice guessing is 25%.


## reas-epoch-otis-dsv32

Source: https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/8szQqvTsGG8gJ2TiFReRn9.eval. Model: deepseek-v3.2; default generation configuration.

Native accounting: `{"accuracy": 0.878174603174603, "completed": 356, "config": {"max_retries": 8}, "excluded_outcome_evaluator_tokens": {"google/gemini-2.0-flash-001": 303042}, "primary": "deepseek/deepseek-reasoner", "samples_in_log": 360, "usage": {"input_tokens": 62825, "input_tokens_cache_read": 51200, "output_tokens": 6568473, "reasoning_tokens": 6389557, "total_tokens": 6631298}}`.

Including recovered or estimated missing work, tokens per completed evaluation = 18639.180517; × 74000000000 FLOPs/token = **1.37929935826e+15 FLOPs**. [Failure accounting](epoch-native-usage-audit.md#reas-epoch-otis-dsv32). AI source accuracy 87.8175% across 356 completed evaluation samples. Human contest score frequencies imply 51.5507% under equal weighting of the three papers.


## reas-epoch-otis-gptoss120b

Source: https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/3QjP5HPi8tKUzHtNJktfv4.eval. Model: gpt-oss-120b; reasoning_effort=high.

Native accounting: `{"accuracy": 0.8888888888888888, "completed": 90, "config": {"max_retries": 20, "reasoning_effort": "high"}, "excluded_outcome_evaluator_tokens": {"google/gemini-2.0-flash-001": 131399}, "primary": "together/openai/gpt-oss-120b", "samples_in_log": 90, "usage": {"input_tokens": 21744, "output_tokens": 1910780, "total_tokens": 1932524}}`.

Tokens per completed sample = 21472.4888889; multiply by 10200000000 FLOPs/token = **2.19019386667e+14 FLOPs**. AI source accuracy 88.8889% across 90 completed evaluation samples. Human contest score frequencies imply 51.5507% under equal weighting of the three papers.


## reas-epoch-otis-opus46-32k

Source: https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/kZ3VgrQJxfKQ5msjpmSaAz.eval. Model: claude-opus-4-6; max_tokens=128000; reasoning_tokens=32000.

Native accounting: `{"accuracy": 0.9305555555555556, "completed": 360, "config": {"max_retries": 8, "max_tokens": 128000, "reasoning_tokens": 32000}, "excluded_outcome_evaluator_tokens": {"google/gemini-2.0-flash-001": 429762}, "primary": "anthropic/claude-opus-4-6", "samples_in_log": 360, "usage": {"input_tokens": 82864, "input_tokens_cache_read": 0, "input_tokens_cache_write": 0, "output_tokens": 5774222, "reasoning_tokens": 2279270, "total_tokens": 5857086}}`.

Tokens per completed sample = 16269.6833333; multiply by 200000000000 FLOPs/token = **3.25393666667e+15 FLOPs**. AI source accuracy 93.0556% across 360 completed evaluation samples. Human contest score frequencies imply 51.5507% under equal weighting of the three papers.


## reas-epoch-otis-opus46-64k

Source: https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/TUPC8VdX4jApFa4MGfNP4t.eval. Model: claude-opus-4-6; max_tokens=128000; reasoning_tokens=64000.

Native accounting: `{"accuracy": 0.9444444444444444, "completed": 360, "config": {"max_retries": 8, "max_tokens": 128000, "reasoning_tokens": 64000}, "excluded_outcome_evaluator_tokens": {"google/gemini-2.0-flash-001": 436810}, "primary": "anthropic/claude-opus-4-6", "samples_in_log": 360, "usage": {"input_tokens": 82864, "input_tokens_cache_read": 0, "input_tokens_cache_write": 0, "output_tokens": 6390291, "reasoning_tokens": 2470886, "total_tokens": 6473155}}`.

Tokens per completed sample = 17980.9861111; multiply by 200000000000 FLOPs/token = **3.59619722222e+15 FLOPs**. AI source accuracy 94.4444% across 360 completed evaluation samples. Human contest score frequencies imply 51.5507% under equal weighting of the three papers.


## reas-epoch-otis-qwen3thinking

Source: https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/XWpHpVPCaVjcwPpdpXuuGH.eval. Model: qwen3-235b-a22b-thinking-2507; default generation configuration.

Native accounting: `{"accuracy": 0.8666666666666667, "completed": 45, "config": {"max_retries": 8}, "excluded_outcome_evaluator_tokens": {"google/gemini-2.0-flash-001": 62456}, "primary": "alibaba/qwen3-235b-a22b-thinking-2507", "samples_in_log": 45, "usage": {"input_tokens": 8608, "output_tokens": 1206779, "reasoning_tokens": 1157289, "total_tokens": 1215387}}`.

Tokens per completed sample = 27008.6; multiply by 44000000000 FLOPs/token = **1.1883784e+15 FLOPs**. AI source accuracy 86.6667% across 45 completed evaluation samples. Human contest score frequencies imply 51.5507% under equal weighting of the three papers.
