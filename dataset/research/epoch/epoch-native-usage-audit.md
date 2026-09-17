# Native Epoch missing-usage and retry audit

The GLM missing-counter discovery prompted an audit of every earlier native run: three initial SimpleQA rows, thirteen expansion-01 runs and three expansion-03 SWE runs. `agent-work/sources/epoch/legacy-accounting/native-missing-usage-audit.json` records all 19 run counts and suspect IDs. Nineteen zero-primary-usage samples occur in six runs; the other thirteen runs, including all three SWE runs, have none. This is a zero-counter audit, not proof that every nonzero summary captures all earlier failed requests. Original full samples were retrieved directly from the public archive URLs in TASKS.json, retained as agent-work/sources/epoch/POINT_ID/audit-missing-samples. No historical estimates supplied the correction.

The historical recovery produced four corrected rows; its record-level decisions are retained in `agent-work/sources/epoch/legacy-accounting/native-audit-corrections/calculations.json`. None of the nineteen earlier samples retain substantive responses or native usage to recover exactly. A potentially executed request with no response is assigned its run's mean included-token workload across counter-bearing samples; explicit rejected requests are assigned zero. Mean imputation is an estimate, not observed execution. A connection failure may precede inference, and an aborted output may use less or more than a mean response. The point estimate favors accounting for lost model work while retaining those uncertainties.

Older Anthropic logs leave individual failed model events pending without an error field. A terminal RateLimitError establishes the last request's rejection, but not the earlier calls. The sequential backoff intervals (one representative series: 16.6, 42.8, 65.5, 54.6, 54.9, 119.1, 205.7 seconds, followed by a final 14.7-second failure) and terminal rate limiting support an assumed zero-work central estimate for the retry sequence. This is an inference about the preceding errors, not directly recorded per-event rejection. A sensitivity scenario assigns each unresolved earlier call one mean response. Distinct event UUIDs and timestamps identify separately initiated calls. The event's SDK `retries=2` field is retained for transparency but is not multiplied into an inferred request count: underlying SDK retry execution is not exposed. The separate sample error and logger messages are never counted again as model calls.

## lang-epoch-simpleqa-qwen3thinking

Sample 721 has one explicit input-filter rejection and gets zero primary work. Sample 797 instead reports **output** filtering during the response stream, without retained output or counters; it receives one observed-run mean. The 998 completed-evaluation denominator is unchanged. Correction adds 0.1002004% to recorded compute. The original description that both filtered records involved no work is superseded by this distinction.

## lang-epoch-simpleqa-opus46-32k

Four samples (323, 324, 328, 332) each contain eight distinct model events and terminate with RateLimitError. Last calls are evidenced rejected; the preceding backoff sequence is centrally assigned zero work. Assigning seven unresolved calls per sample a mean response instead would increase compute 2.811245%. The central estimate does not change the existing row.

## lang-epoch-simpleqa-opus46-max

Sample 290 raises IndexError in Anthropic's stream accumulator while processing a content-block delta. Some response generation is implicated, but text and usage are lost. One mean-imputed call increases compute 0.1001001%. The xhigh reasoning-effort configuration remains unchanged.

## reas-epoch-gpqa-dsv32

Six samples fail JSON parsing of the provider response at line 10 column 1, each after one model event. These errors do not evidence rejection before execution. Six mean-imputed responses increase compute 0.3802281%. Retained source errors and IDs are in calculations.json.

## reas-epoch-gpqa-opus46-64k

Two samples have eight model events each and end with RateLimitError. The rate-limit backoff sequence is centrally assigned zero work, leaving the existing row unchanged. Assigning fourteen earlier unresolved calls mean responses instead would increase compute 0.8849558%. The 64K reasoning budget and actual recorded output for other samples are unchanged.

## reas-epoch-otis-dsv32

Three samples have JSON-response parsing errors; a fourth has eight distinct calls ending in APIConnectionError whose traceback specifically identifies ConnectError before request dispatch. The connection-failure/backoff sequence is centrally assigned zero work. The three malformed-response calls receive the same run mean, increasing compute 0.8426966%. Earlier errors within the connection-failure retry sequence are not separately recorded; imputing its seven unresolved earlier calls would add a further 1.9662921% of recorded compute. Human time and accuracy judgments are unchanged.

## Nonzero spot check

`agent-work/sources/epoch/legacy-accounting/native-nonzero-spotcheck-plan.json` fixes a deterministic random sample (seed 20260912) of five counter-bearing samples for each of Anthropic, DeepSeek, Alibaba and Zhipu, drawn from affected runs. All 20 original files are retained under audit-nonzero-samples; results preserve event IDs, errors and usage. Nineteen samples have exactly one primary model event. One GLM-5 GPQA sample has ten: four timeouts, five rejected requests and one successful response. This triggered a complete audit of that bounded 198-question run, rather than extrapolating a prevalence estimate from one observation. Small clean samples for other providers do not prove no missing retries anywhere; no further extrapolated adjustment is made for those providers.

## reas-epoch-gpqa-glm5

The entire original GLM-5 GPQA archive (about 17 MB compressed) was downloaded; all 198 samples are retained under all-samples. Every distinct primary model event is recorded in `agent-work/sources/epoch/legacy-accounting/native-audit-corrections/glm5-retry-calculations.json`. There are 1,405 events: 812 explicit HTTP 429 rejections, 373 generic timeout errors whose full tracebacks **all** identify httpcore/httpx ConnectTimeout during connect_tcp, 22 generic connection errors whose tracebacks identify ReadError, one explicit ReadError, and 197 retained responses. Connection-establishment timeouts occur before dispatch and receive zero model work. The 23 response-read failures remain potentially executed. 147 samples have multiple events. Event UUID/timestamp uniqueness is checked per sample; tracebacks remain in original full samples.

Native successful-call time has mean 494.77s and median 288.01s. Inter-event intervals (including backoff/queue delay) have median 154.48s for generic timeouts and 134.54s for explicit rate rejections. These overlapping intervals do not support treating each timeout as a fully executed response. The traceback-level distinction is more informative than elapsed wall time and controls classification.

The earlier GLM zero-counter correction imputed seven generic failed calls. The run-wide audit replaces that assumption: all 23 read failures receive the mean of 197 known/reconstructed response workloads, 18,913.928934 tokens. This mean includes the tokenizer-reconstructed retained response previously missing usage. Subtracting the earlier seven-call imputation before applying the full audit avoids double counting. Total work divided by 197 completed evaluations gives **21,122.154140 tokens**, versus 19,585.997475 in the first repaired submission. Assigning zero work to all read failures instead gives **18,913.928934 tokens** per completion. The 0-to-one-mean-per-read-failure interval is an assumption sensitivity, not a confidence interval or hard bound: a read failure may happen after partial or unusually long generation. Recorded response-read errors imply the request reached the response phase, making the same-run mean a defensible central allocation in the absence of retained generation. No primary model work is assigned to rejected or pre-request connection failures.

Corrections change compute tokens, FLOPs, evidence classification and provenance/notes only; all human times, model coefficients, native scores and completed-evaluation denominators remain fixed. The historical generators are superseded as publication commands. Use [the read-only accounting check](reproduction.md) to verify current counter totals with the retained reviewed correction artifacts; this does not reclassify errors or rerun tokenizer recovery.
