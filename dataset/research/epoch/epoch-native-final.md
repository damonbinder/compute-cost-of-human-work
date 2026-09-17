# Epoch: remaining native-log runs

These sixteen records use original Epoch `.eval` logs. Workload is total task-solving model work divided by completed evaluations, including incorrect answers. Uncompleted attempts contribute recorded work and the missing-work estimate below. This is an amortized cost per completed evaluation. It is not a mean over successful answers alone.

Human work and timing use the reviewed [SWE-bench](swebench.md), [SimpleQA](simpleqa.md), [GPQA](gpqa.md) and [OTIS](otis.md) definitions. Each SWE run has the same 484 submitted issues. GPQA has 198 questions × eight trials; OTIS has 45 × eight. SimpleQA has 1,000 single trials. Human time retains the full source task mix. Incomplete AI questions are identified below, and the CSV flags selection differences.

## Recorded counters

A printed zero cache counter can also mean the field was absent and defaulted to zero in the calculation. Qwen3.6 Plus SWE and the three Gemini3.1 Pro question runs omit cache fields. The Qwen events also omit raw provider responses; the retained Google responses contain no cache-count field. These inputs are treated as newly processed because no cache subtraction can be recovered, not because a zero hit count was measured.

Counter identities are checked for every summary and every inspected model call. The table uses `I` for source input, `O` for ordinary output, `R` for separately reported reasoning, `CR` for cache reads and `CW` for cache writes.

| Native endpoint | Source total | Included workload |
|---|---|---|
| `google/*` in this tranche | I + O + R | I − CR + O + R |
| `epoch/gemini-3.5-flash` | I + CR + O + R | I + O + R |
| `openai/*` | I + O | I − CR + O |
| Other `epoch/*`, and Anthropic | I + CR + CW + O | I + CW + O |

For Google, reasoning is additional to ordinary output. For the other providers it is included in output, or not separately identified. The `epoch/` adapters normalize cached input differently from `google/` and `openai/`; the native response spotchecks confirm this distinction. Each model's own counters are used, including Opus 4.7's tokenizer; no cross-tokenizer multiplier is applied. Post-answer graders do not help solve the task and are excluded. Their identities and counts are retained in the calculation audit. Cached-token attention is outside the shared parameter-multiplication estimate and is added to `compute_flops` separately (`research/attention-correction.md`).

Gemini 3.1 Pro customtools resumes an earlier run: its header counters cover the final 446 issues. Those counters exactly match that segment; compute uses all 484 summaries.

## Calls without usable counters

Thirteen complete archives were audited, including every incomplete sample and errors inside completed samples. The three larger SWE logs—Gemini 3.1 Pro customtools, Gemini 3 Flash and GPT-5 mini—have complete summary checks plus full event inspection of the first, median-workload and largest-workload samples. That limited event sample cannot exclude additional unreported work elsewhere.

Errors are classified from the original exception and traceback. Explicit quota, rate-limit and overload rejections receive no inference allowance. A response-header/body read failure, connection reset, gateway failure or empty response without usage may have performed work; its amount is unobserved.

For each such send, use half a comparable recorded call as the central allowance. This midpoint spans two scenarios: zero work and one comparable call's workload. For single-question benchmarks the donor is the mean of recorded calls for that same question, across available trials. For SWE it is the same issue's recorded call mean, not the cost of the entire issue. If no same-question call exists, use that run's call mean. These are explicit judgment assumptions; one donor call is a sensitivity case, not a proven upper bound on actual lost compute.

The original Inspect [0.3.174 request hooks](https://github.com/UKGovernmentBEIS/inspect_ai/blob/0.3.174/src/inspect_ai/model/_providers/util/hooks.py) and [active-event counter](https://github.com/UKGovernmentBEIS/inspect_ai/blob/0.3.174/src/inspect_ai/log/_samples.py) show that an event's `retries` count records additional SDK network sends. The same mechanisms were checked at [0.3.239](https://github.com/UKGovernmentBEIS/inspect_ai/blob/0.3.239/src/inspect_ai/model/_providers/util/hooks.py). An exposed failed event therefore represents `1 + retries` sends. For its earlier SDK sends, the central estimate assumes the same failure class as the final exposed error; the individual earlier error types are not retained. SDK retries inside an eventual successful event have no individual error log: their central unresolved share is the run's observed ratio of read/ambiguous sends to all classified failed sends, then the same half-call allowance is applied. Their sensitivity runs from zero to one donor call per send. This mixture transfer is a separate assumption.

GPT-5.4's exposed errors fail while reading response headers. Most otherwise successful records with internal retries have roughly 282 seconds of overhead per retry. This supports treating them as unresolved work, but does not prove that generation completed. The central GPQA and OTIS estimates are dominated by these allowances. Their CSV notes identify that fact and the values below retain the zero-to-one-call scenarios.

## Verification

`agent-work/sources/epoch/native-final-accounting/expansion-14/usage-reconstruction.json` contains the per-error decisions, SDK counts, same-question donor sizes and scenarios. The sixteen `*-events.json` files reconcile original event counters to summaries. `native-audit-acquisition.json` and `full-log-acquisition.json` identify retained originals and hashes. A standalone calculation replay is `python research/epoch/recompute_native_final.py agent-work/sources/epoch --output /tmp/epoch14-replay.json` from the published dataset directory. It rebuilds the recorded sums, source score reduction and missing-work scenarios from retained summaries and event audit records; it makes no model calls and does not alter sources.

Performance is independently reconstructed from outcomes: mean correctness within each question, then equal weight across questions having a completed trial, as in the source's reduction. This differs from pooling all completed trials when some questions have fewer returns. Published scores and the individual correct/completed counts are both retained below. Failed API returns do not become correct answers.

Model release dates, parameter sources and shared scenarios are in [model evidence](epoch-native-final-models.md).


## agen-epoch-swebench-dsv4promax

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/WUk3f44JhxtAJaSxi6gFZR.eval); endpoint `epoch/deepseek-v4-pro`; model `deepseek-v4-pro-preview`. reasoning_effort=max. 484 submitted records; 483 completed evaluations.

Counters: input_tokens=93,494,654; input_tokens_cache_read=775,633,408; input_tokens_cache_write=0; output_tokens=9,358,007; reasoning_tokens=5,839,937; total_tokens=878,486,069. all summaries equal header.

Recorded included workload 102,852,661 + estimated missing-work allowance 318720.299479 = 103171381.299 tokens; divide by 483 = **213605.344305 tokens per completed evaluation**. Multiply by 98000000000 FLOPs/token = **2.09333237419e+16 FLOPs**.

Zero-to-one-comparable-call scenario for unmeasured work: **212945.467909–232289.487789 tokens**, or **2.08686558551e+16–2.27643698034e+16 FLOPs**, holding model size fixed. The central allowance is 0.309% of compute. This is a sensitivity scenario, not a confidence interval.

Event audit: all_samples; classified failed sends {"rate_limit_rejection": 14832, "response_header_read_failure": 102}; 1924 untyped SDK retries before eventual success, assigned unresolved fraction 0.00683005.

Performance: 77.6397516% under the source question-mean reduction; 375/483 completed trials correct. Human baseline: [swebench](swebench.md); category `below`.

Questions with no completed trial: `django__django-16560`. The AI score omits them; recorded and estimated work still enters compute.


## agen-epoch-swebench-gemini31pro-ct

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/8QQQWDgmmEsmQVUJWcxx4P.eval); endpoint `google/gemini-3.1-pro-preview-customtools`; model `gemini-3.1-pro-preview-customtools`. 484 submitted records; 484 completed evaluations.

Counters: input_tokens=1,165,003,954; input_tokens_cache_read=1,039,853,655; input_tokens_cache_write=0; output_tokens=3,702,645; reasoning_tokens=37,052,317; total_tokens=1,205,758,916. Header matches final 446-sample segment; full 484 summaries used..

Recorded included workload 165,905,261 + estimated missing-work allowance 0 = 165905261 tokens; divide by 484 = **342779.464876 tokens per completed evaluation**. Multiply by 200000000000 FLOPs/token = **6.85558929752e+16 FLOPs**.

Zero-to-one-comparable-call scenario for unmeasured work: **342779.464876–342779.464876 tokens**, or **6.85558929752e+16–6.85558929752e+16 FLOPs**, holding model size fixed. The central allowance is 0% of compute. This is a sensitivity scenario, not a confidence interval.

Event audit: first_median_largest_workload_samples; classified failed sends {"overload_rejection": 3}; 0 untyped SDK retries before eventual success, assigned unresolved fraction 0.

Performance: 75.6198347% under the source question-mean reduction; 366/484 completed trials correct. Human baseline: [swebench](swebench.md); category `below`.

Model-size scenario 30–300B active gives 2.05667678926e+16–2.05667678926e+17 FLOPs at the central workload.


## agen-epoch-swebench-gemini35flash

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/dwRzFGTghYEy4HNZajJXoc.eval); endpoint `epoch/gemini-3.5-flash`; model `gemini-3.5-flash`. reasoning_effort=high. 484 submitted records; 484 completed evaluations.

Counters: input_tokens=137,691,740; input_tokens_cache_read=438,116,660; input_tokens_cache_write=0; output_tokens=1,729,046; reasoning_tokens=5,841,270; total_tokens=583,378,716. all summaries equal header.

Recorded included workload 145,262,056 + estimated missing-work allowance 0 = 145262056 tokens; divide by 484 = **300128.214876 tokens per completed evaluation**. Multiply by 80000000000 FLOPs/token = **2.40102571901e+16 FLOPs**.

Zero-to-one-comparable-call scenario for unmeasured work: **300128.214876–300128.214876 tokens**, or **2.40102571901e+16–2.40102571901e+16 FLOPs**, holding model size fixed. The central allowance is 0% of compute. This is a sensitivity scenario, not a confidence interval.

Event audit: all_samples; classified failed sends {"service_unavailable": 28}; 0 untyped SDK retries before eventual success, assigned unresolved fraction 0.

Performance: 79.338843% under the source question-mean reduction; 384/484 completed trials correct. Human baseline: [swebench](swebench.md); category `below`.

Model-size scenario 10–150B active gives 6.00256429752e+15–9.00384644628e+16 FLOPs at the central workload.


## agen-epoch-swebench-gemini3flash

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/jxoyMNmTnYirjLJN6wRNmG.eval); endpoint `google/gemini-3-flash-preview`; model `gemini-3-flash-preview`. 484 submitted records; 484 completed evaluations.

Counters: input_tokens=586,965,501; input_tokens_cache_read=446,939,896; input_tokens_cache_write=0; output_tokens=2,616,522; reasoning_tokens=11,611,239; total_tokens=601,193,262. all summaries equal header.

Recorded included workload 154,253,366 + estimated missing-work allowance 0 = 154253366 tokens; divide by 484 = **318705.301653 tokens per completed evaluation**. Multiply by 80000000000 FLOPs/token = **2.54964241322e+16 FLOPs**.

Zero-to-one-comparable-call scenario for unmeasured work: **318705.301653–318705.301653 tokens**, or **2.54964241322e+16–2.54964241322e+16 FLOPs**, holding model size fixed. The central allowance is 0% of compute. This is a sensitivity scenario, not a confidence interval.

Event audit: first_median_largest_workload_samples; classified failed sends {}; 0 untyped SDK retries before eventual success, assigned unresolved fraction 0.5.

Performance: 75.4132231% under the source question-mean reduction; 365/484 completed trials correct. Human baseline: [swebench](swebench.md); category `below`.

Model-size scenario 10–150B active gives 6.37410603306e+15–9.56115904959e+16 FLOPs at the central workload.


## agen-epoch-swebench-glm52max

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/4AfhcmYVNrw6gM5u8CQsyy.eval); endpoint `epoch/glm-5.2`; model `glm-5.2`. reasoning_effort=max. 484 submitted records; 483 completed evaluations.

Counters: input_tokens=28,029,103; input_tokens_cache_read=1,238,851,264; input_tokens_cache_write=0; output_tokens=15,330,555; reasoning_tokens=6,306,895; total_tokens=1,282,210,922. all summaries equal header.

Recorded included workload 43,359,658 + estimated missing-work allowance 7833.33179696 = 43367491.3318 tokens; divide by 483 = **89787.7667325 tokens per completed evaluation**. Multiply by 80000000000 FLOPs/token = **7.1830213386e+15 FLOPs**.

Zero-to-one-comparable-call scenario for unmeasured work: **89771.5486542–89803.9848108 tokens**, or **7.18172389234e+15–7.18431878486e+15 FLOPs**, holding model size fixed. The central allowance is 0.0181% of compute. This is a sensitivity scenario, not a confidence interval.

Event audit: all_samples; classified failed sends {"empty_response_without_usage": 4, "response_body_read_failure": 1}; 5 untyped SDK retries before eventual success, assigned unresolved fraction 1.

Performance: 78.6749482% under the source question-mean reduction; 380/483 completed trials correct. Human baseline: [swebench](swebench.md); category `below`.

Questions with no completed trial: `django__django-10097`. The AI score omits them; recorded and estimated work still enters compute.

Model-size scenario 35–45B active gives 6.28514367127e+15–8.08089900592e+15 FLOPs at the central workload.


## agen-epoch-swebench-gpt5mini

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/7nvdQy3AwKtoay2FBvfST5.eval); endpoint `openai/gpt-5-mini-2025-08-07`; model `gpt-5-mini-2025-08-07`. reasoning_effort=medium. 484 submitted records; 484 completed evaluations.

Counters: input_tokens=290,706,940; input_tokens_cache_read=147,169,536; input_tokens_cache_write=0; output_tokens=4,332,566; reasoning_tokens=3,181,111; total_tokens=295,039,506. all summaries equal header.

Recorded included workload 147,869,970 + estimated missing-work allowance 0 = 147869970 tokens; divide by 484 = **305516.466942 tokens per completed evaluation**. Multiply by 40000000000 FLOPs/token = **1.22206586777e+16 FLOPs**.

Zero-to-one-comparable-call scenario for unmeasured work: **305516.466942–305516.466942 tokens**, or **1.22206586777e+16–1.22206586777e+16 FLOPs**, holding model size fixed. The central allowance is 0% of compute. This is a sensitivity scenario, not a confidence interval.

Event audit: first_median_largest_workload_samples; classified failed sends {}; 0 untyped SDK retries before eventual success, assigned unresolved fraction 0.5.

Performance: 64.6694215% under the source question-mean reduction; 313/484 completed trials correct. Human baseline: [swebench](swebench.md); category `below`.

Model-size scenario 10–40B active gives 6.11032933884e+15–2.44413173554e+16 FLOPs at the central workload.


## agen-epoch-swebench-kimik26

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/bUPtAK7spEwvmiC8pi6afc.eval); endpoint `epoch/kimi-k2.6`; model `kimi-k2.6`. 484 submitted records; 484 completed evaluations.

Counters: input_tokens=21,624,437; input_tokens_cache_read=665,450,368; input_tokens_cache_write=0; output_tokens=7,221,879; reasoning_tokens=0; total_tokens=694,296,684. all summaries equal header.

Recorded included workload 28,846,316 + estimated missing-work allowance 703.22972973 = 28847019.2297 tokens; divide by 484 = **59601.2794003 tokens per completed evaluation**. Multiply by 64000000000 FLOPs/token = **3.81448188162e+15 FLOPs**.

Zero-to-one-comparable-call scenario for unmeasured work: **59599.8264463–59602.7323543 tokens**, or **3.81438889256e+15–3.81457487067e+15 FLOPs**, holding model size fixed. The central allowance is 0.00244% of compute. This is a sensitivity scenario, not a confidence interval.

Event audit: all_samples; classified failed sends {"overload_rejection": 4, "rate_limit_rejection": 862, "response_header_read_failure": 1}; 0 untyped SDK retries before eventual success, assigned unresolved fraction 0.0011534.

Performance: 76.6528926% under the source question-mean reduction; 371/484 completed trials correct. Human baseline: [swebench](swebench.md); category `below`.


## agen-epoch-swebench-opus47max

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/nCmGWWMBip2s9AVEZNYXDX.eval); endpoint `anthropic/claude-opus-4-7`; model `claude-opus-4-7`. reasoning_effort=max. 484 submitted records; 484 completed evaluations.

Counters: input_tokens=152,618; input_tokens_cache_read=1,255,052,364; input_tokens_cache_write=26,698,678; output_tokens=10,934,652; reasoning_tokens=1,282,914; total_tokens=1,292,838,312. all summaries equal header.

Recorded included workload 37,785,948 + estimated missing-work allowance 662.598360656 = 37786610.5984 tokens; divide by 484 = **78071.5095007 tokens per completed evaluation**. Multiply by 200000000000 FLOPs/token = **1.56143019001e+16 FLOPs**.

Zero-to-one-comparable-call scenario for unmeasured work: **78070.1404959–78072.8785056 tokens**, or **1.56140280992e+16–1.56145757011e+16 FLOPs**, holding model size fixed. The central allowance is 0.00175% of compute. This is a sensitivity scenario, not a confidence interval.

Event audit: all_samples; classified failed sends {"overload_rejection": 2, "response_body_read_failure": 1}; 0 untyped SDK retries before eventual success, assigned unresolved fraction 0.333333.

Performance: 83.4710744% under the source question-mean reduction; 404/484 completed trials correct. Human baseline: [swebench](swebench.md); category `below`.

Model-size scenario 50–200B active gives 7.80715095007e+15–3.12286038003e+16 FLOPs at the central workload.


## agen-epoch-swebench-qwen36plus

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/8HV4HP9EM5KuLSwzifuLye.eval); endpoint `epoch/qwen3.6-plus`; model `qwen3.6-plus`. 484 submitted records; 484 completed evaluations.

Counters: input_tokens=731,713,880; input_tokens_cache_read=0; input_tokens_cache_write=0; output_tokens=11,401,185; reasoning_tokens=7,146,508; total_tokens=743,115,065. all summaries equal header.

Recorded included workload 743,115,065 + estimated missing-work allowance 14448.7887324 = 743129513.789 tokens; divide by 484 = **1535391.55741 tokens per completed evaluation**. Multiply by 34000000000 FLOPs/token = **5.22033129521e+16 FLOPs**.

Zero-to-one-comparable-call scenario for unmeasured work: **1535361.70455–1535421.41028 tokens**, or **5.22022979545e+16–5.22043279497e+16 FLOPs**, holding model size fixed. The central allowance is 0.00194% of compute. This is a sensitivity scenario, not a confidence interval.

Event audit: all_samples; classified failed sends {"response_body_read_failure": 1}; 0 untyped SDK retries before eventual success, assigned unresolved fraction 1.

Performance: 57.8512397% under the source question-mean reduction; 280/484 completed trials correct. Human baseline: [swebench](swebench.md); category `below`.

Model-size scenario 8–68B active gives 2.45662649186e+16–2.08813251808e+17 FLOPs at the central workload.


## agen-epoch-swebench-qwen37max

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/83hhDhcT9UUrZ2NiUbWSUU.eval); endpoint `epoch/qwen3.7-max`; model `qwen3.7-max`. 484 submitted records; 484 completed evaluations.

Counters: input_tokens=86,837,304; input_tokens_cache_read=187,754,922; input_tokens_cache_write=6,842,887; output_tokens=12,076,867; reasoning_tokens=9,481,576; total_tokens=293,511,980. all summaries equal header.

Recorded included workload 105,757,058 + estimated missing-work allowance 0 = 105757058 tokens; divide by 484 = **218506.318182 tokens per completed evaluation**. Multiply by 200000000000 FLOPs/token = **4.37012636364e+16 FLOPs**.

Zero-to-one-comparable-call scenario for unmeasured work: **218506.318182–232371.730467 tokens**, or **4.37012636364e+16–4.64743460933e+16 FLOPs**, holding model size fixed. The central allowance is 0% of compute. This is a sensitivity scenario, not a confidence interval.

Event audit: all_samples; classified failed sends {"rate_limit_rejection": 8400}; 1040 untyped SDK retries before eventual success, assigned unresolved fraction 0.

Performance: 77.2727273% under the source question-mean reduction; 374/484 completed trials correct. Human baseline: [swebench](swebench.md); category `below`.

Model-size scenario 30–300B active gives 1.31103790909e+16–1.31103790909e+17 FLOPs at the central workload.


## lang-epoch-simpleqa-gemini31pro

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/Z8qvnF3dcQV6bRWrCxqPGr.eval); endpoint `google/gemini-3.1-pro-preview`; model `gemini-3.1-pro-preview`. 1000 submitted records; 1000 completed evaluations.

Counters: input_tokens=24,215; input_tokens_cache_read=0; input_tokens_cache_write=0; output_tokens=117,783; reasoning_tokens=1,885,418; total_tokens=2,027,416. all summaries equal header.

Recorded included workload 2,027,416 + estimated missing-work allowance 0 = 2027416 tokens; divide by 1000 = **2027.416 tokens per completed evaluation**. Multiply by 200000000000 FLOPs/token = **4.054832e+14 FLOPs**.

Zero-to-one-comparable-call scenario for unmeasured work: **2027.416–2027.416 tokens**, or **4.054832e+14–4.054832e+14 FLOPs**, holding model size fixed. The central allowance is 0% of compute. This is a sensitivity scenario, not a confidence interval.

Event audit: all_samples; classified failed sends {}; 0 untyped SDK retries before eventual success, assigned unresolved fraction 0.5.

Performance: 77.3% under the source question-mean reduction; 773/1000 completed trials correct. Human baseline: [simpleqa](simpleqa.md); category `below`.

Model-size scenario 30–300B active gives 1.2164496e+14–1.2164496e+15 FLOPs at the central workload.


## lang-epoch-simpleqa-gpt54xhigh

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/fjyvZwR5cfCATJMKfVV9Ap.eval); endpoint `openai/gpt-5.4-2026-03-05`; model `gpt-5.4-2026-03-05`. reasoning_effort=xhigh. 1000 submitted records; 997 completed evaluations.

Counters: input_tokens=71,219; input_tokens_cache_read=0; input_tokens_cache_write=0; output_tokens=4,870,160; reasoning_tokens=4,842,172; total_tokens=4,941,379. all summaries equal header.

Recorded included workload 4,941,379 + estimated missing-work allowance 1403197.41876 = 6344576.41876 tokens; divide by 997 = **6363.66742102 tokens per completed evaluation**. Multiply by 200000000000 FLOPs/token = **1.2727334842e+15 FLOPs**.

Zero-to-one-comparable-call scenario for unmeasured work: **4956.24774323–7771.08709881 tokens**, or **9.91249548646e+14–1.55421741976e+15 FLOPs**, holding model size fixed. The central allowance is 22.1% of compute. This is a sensitivity scenario, not a confidence interval.

Event audit: all_samples; classified failed sends {"response_header_read_failure": 198}; 88 untyped SDK retries before eventual success, assigned unresolved fraction 1.

Performance: 44.8345035% under the source question-mean reduction; 447/997 completed trials correct. Human baseline: [simpleqa](simpleqa.md); category `below`.

Questions with no completed trial: `138`, `622`, `955`. The AI score omits them; recorded and estimated work still enters compute.

Model-size scenario 50–200B active gives 6.36366742102e+14–2.54546696841e+15 FLOPs at the central workload.


## reas-epoch-gpqa-gemini31pro

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/kR9F3oHBCnwQW4AiTPKwpd.eval); endpoint `google/gemini-3.1-pro-preview`; model `gemini-3.1-pro-preview`. 1584 submitted records; 1540 completed evaluations.

Counters: input_tokens=388,307; input_tokens_cache_read=0; input_tokens_cache_write=0; output_tokens=1,011,564; reasoning_tokens=7,817,019; total_tokens=9,216,890. all summaries equal header.

Recorded included workload 9,216,890 + estimated missing-work allowance 451503.707359 = 9668393.70736 tokens; divide by 1540 = **6278.17773205 tokens per completed evaluation**. Multiply by 200000000000 FLOPs/token = **1.25563554641e+15 FLOPs**.

Zero-to-one-comparable-call scenario for unmeasured work: **5984.99350649–6571.36195761 tokens**, or **1.1969987013e+15–1.31427239152e+15 FLOPs**, holding model size fixed. The central allowance is 4.67% of compute. This is a sensitivity scenario, not a confidence interval.

Event audit: all_samples; classified failed sends {"connection_reset_during_read": 44}; 0 untyped SDK retries before eventual success, assigned unresolved fraction 1.

Performance: 94.4434373% under the source question-mean reduction; 1466/1540 completed trials correct. Human baseline: [gpqa](gpqa.md); category `above`.

Questions with no completed trial: `recVvpD8miVjmmyfe`. The AI score omits them; recorded and estimated work still enters compute.

Model-size scenario 30–300B active gives 3.76690663923e+14–3.76690663923e+15 FLOPs at the central workload.


## reas-epoch-gpqa-gpt54xhigh

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/fFatyce8UvpN7ZivdmrhAy.eval); endpoint `openai/gpt-5.4-2026-03-05`; model `gpt-5.4-2026-03-05`. reasoning_effort=xhigh. 1584 submitted records; 1541 completed evaluations.

Counters: input_tokens=396,064; input_tokens_cache_read=10,752; input_tokens_cache_write=0; output_tokens=7,578,734; reasoning_tokens=7,160,123; total_tokens=7,974,798. all summaries equal header.

Recorded included workload 7,964,046 + estimated missing-work allowance 17526923.1311 = 25490969.1311 tokens; divide by 1541 = **16541.8359059 tokens per completed evaluation**. Multiply by 200000000000 FLOPs/token = **3.30836718119e+15 FLOPs**.

Zero-to-one-comparable-call scenario for unmeasured work: **5168.10253082–27915.5692811 tokens**, or **1.03362050616e+15–5.58311385621e+15 FLOPs**, holding model size fixed. The central allowance is 68.8% of compute. This is a sensitivity scenario, not a confidence interval.

Event audit: all_samples; classified failed sends {"response_header_read_failure": 1608}; 168 untyped SDK retries before eventual success, assigned unresolved fraction 1.

Performance: 93.6397148% under the source question-mean reduction; 1447/1541 completed trials correct. Human baseline: [gpqa](gpqa.md); category `above`.

Questions with no completed trial: `recWxGU8Q4YReJ1tb`. The AI score omits them; recorded and estimated work still enters compute.

Model-size scenario 50–200B active gives 1.65418359059e+15–6.61673436238e+15 FLOPs at the central workload.


## reas-epoch-otis-gemini31pro

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/bXgZZgzRE3wXoSRUgrbsVf.eval); endpoint `google/gemini-3.1-pro-preview`; model `gemini-3.1-pro-preview`. 360 submitted records; 337 completed evaluations.

Counters: input_tokens=57,590; input_tokens_cache_read=0; input_tokens_cache_write=0; output_tokens=374,538; reasoning_tokens=3,926,419; total_tokens=4,358,547. all summaries equal header.

Recorded included workload 4,358,547 + estimated missing-work allowance 193371.276812 = 4551918.27681 tokens; divide by 337 = **13507.1758956 tokens per completed evaluation**. Multiply by 200000000000 FLOPs/token = **2.70143517912e+15 FLOPs**.

Zero-to-one-comparable-call scenario for unmeasured work: **12933.3738872–14080.9779039 tokens**, or **2.58667477745e+15–2.81619558079e+15 FLOPs**, holding model size fixed. The central allowance is 4.25% of compute. This is a sensitivity scenario, not a confidence interval.

Event audit: all_samples; classified failed sends {"connection_reset_during_read": 23}; 0 untyped SDK retries before eventual success, assigned unresolved fraction 1.

Performance: 100% under the source question-mean reduction; 337/337 completed trials correct. Human baseline: [otis](otis.md); category `above`.

Questions with no completed trial: `2024-Mock-AIME-Problem-14`, `2025-II-Mock-AIME-Problem-15`. The AI score omits them; recorded and estimated work still enters compute.

Model-size scenario 30–300B active gives 8.10430553735e+14–8.10430553735e+15 FLOPs at the central workload.


## reas-epoch-otis-gpt54xhigh

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/HVsPchr34pWYHNuv5sKYyK.eval); endpoint `openai/gpt-5.4-2026-03-05`; model `gpt-5.4-2026-03-05`. reasoning_effort=xhigh. 360 submitted records; 317 completed evaluations.

Counters: input_tokens=73,129; input_tokens_cache_read=0; input_tokens_cache_write=0; output_tokens=2,863,481; reasoning_tokens=2,586,502; total_tokens=2,936,610. all summaries equal header.

Recorded included workload 2,936,610 + estimated missing-work allowance 16522833.0285 = 19459443.0285 tokens; divide by 317 = **61386.2556104 tokens per completed evaluation**. Multiply by 200000000000 FLOPs/token = **1.22772511221e+16 FLOPs**.

Zero-to-one-comparable-call scenario for unmeasured work: **9263.75394322–113508.757278 tokens**, or **1.85275078864e+15–2.27017514555e+16 FLOPs**, holding model size fixed. The central allowance is 84.9% of compute. This is a sensitivity scenario, not a confidence interval.

Event audit: all_samples; classified failed sends {"response_header_read_failure": 1341}; 80 untyped SDK retries before eventual success, assigned unresolved fraction 1.

Performance: 99.702381% under the source question-mean reduction; 316/317 completed trials correct. Human baseline: [otis](otis.md); category `above`.

Questions with no completed trial: `2024-Mock-AIME-Problem-14`, `2025-I-Mock-AIME-Problem-14`, `2025-II-Mock-AIME-Problem-14`. The AI score omits them; recorded and estimated work still enters compute.

Model-size scenario 50–200B active gives 6.13862556104e+15–2.45545022442e+16 FLOPs at the central workload.

[Prompt-cache evidence and sensitivity](../cache-accounting/cache-accounting.md).
