# Accepted Copilot completion text

## code-copilot-cups-accepted-completion-2022

The point is **2.462 × 10¹³ FLOPs per distinct accepted suggestion**, compared with an assumed **20 seconds** for a programmer already familiar with the task to write comparable short fragments. It covers the requests with at least one displayed choice in all 21 released study sessions. It includes rejected choices and estimated undisplayed alternatives from those requests. It does not estimate every request made to the service during the sessions.

The unit is the source-recorded suggestion text, not verified newly inserted code. Accepted text can include comments, partial names or longer functions. Acceptance also does not establish correctness or retention in the final file.

## Original records

[Mozannar et al., Reading Between the Lines](https://arxiv.org/html/2210.14306v5), §3 and its Copilot-version footnote, identify the August 2022 system. The [original repository](https://github.com/microsoft/coderec_programming_states/tree/f24f92e35d44be902d04c559d36f8837be1bd523) is pinned at `f24f92e35d44be902d04c559d36f8837be1bd523`. Its `data_labeled_study.pkl` has Git blob `a0ec747fd7f74c79206b937f786c9690bb5816d6`. The native sessions run from August 8 through August 18, 2022.

All 3,490 raw event rows are retained: 1,150 Shown, 1,239 Replay, 386 Accepted, 710 Rejected and five Browsing. These are event counts, not calls or independent suggestions. The paper’s filtered labeled-segment counts are not the compute denominator. The tasks cover data manipulation, machine learning, algorithmic problems, data analysis, classes, editing code, logistic regression and tests.

The author-hosted [study archive](https://storage.googleapis.com/public-research-data-mozannar/copilot_study_data.zip), object generation `1708656924204117`, supplies final code and four processed log files. Only the central-directory range and initial code/log byte range were downloaded; participant videos were not retrieved. The retained 26 code/log members have matching ZIP CRCs. They establish that session 16 uses C++, session 17 JavaScript, and the other sessions Python. Session indices are zero-based, as are event locators below.

The repository’s `when_to_show/extended_logs/extended_logs.py` joins suggestion text through completion ID and choice index, then obtains prompts from hypothetical-prompt fields or a preceding event. The released pickle omits those original IDs and cursor positions. Of 1,023 reconstructed choices, 665 have stored-prompt lengths different from their native `promptCharLen`; another 50 have empty prompt strings. For example, session 17/event 14 records `rEach((num,index)=>{` although the stored prompt already contains `nums.forEach((num,index)=>{`. Session 8/event 125 repeats a `get_text` comment already in its stored prompt. These pairs cannot establish an inserted diff or the exact cursor context.

## Request and acceptance reconstruction

Strings are JSON-decoded once. A choice is identified by session, stored prompt and suggestion, native output-token count and log-probability fields, together with the original issuance clock reconstructed as event time minus `timeSinceIssuedMs`. Matching frames cluster within 10 ms. The largest within-choice clock discrepancy is 8 ms; 10 and 25 ms both yield 1,023 choices. A 1 ms threshold incorrectly splits more jittered display/acceptance frames and gives 1,077 groups.

Choices sharing session, issuance clock and native prompt length identify **1,018 requests**. Five requests have two distinct observed alternatives. Cache displays and accept/reject events do not create additional generation work. Four choices have two acceptance events at different timestamps, sometimes with changed display-length fields. The denominator therefore counts **382 distinct generated choices accepted at least once**, rather than claiming all 386 acceptance events inserted their full stored strings anew. All native acceptance events and their grouping remain in `calculations.json`.

## Compute

### Historical implementation

The retained [official Copilot client](https://github.com/github/copilot.vim/tree/6c5abda66350773ae2f8fade2e931b3beb51843f), dated August 5, 2022, is the latest agent revision before these sessions. `copilot/dist/agent.js` has Git blob `65ea565c1c01531a090aa2b276fe084beb211955`. It is evidence for a contemporary implementation, not proof of the exact VS Code client build or server experiments used by the study.

Relevant functions in the retained original are `convertToAPIChoice`, `telemetrizePromptLength`, `getGhostText`, the generation-setting function immediately around `forceSingleLine`, and `InlineSuggestCount`. `convertToAPIChoice` obtains `numTokens` from the returned log-probability token array. Later whitespace removal, single-line slicing and cached typed-prefix handling can alter display text without recounting these tokens. Native positive output counts therefore take precedence over tokenizing the displayed string.

The original vocabulary and byte-to-Unicode mapping exactly reproduce the retained 50,280-token p50k mergeable-rank table. The calculator checks that identity before tokenization. The source’s non-FIM telemetry uses `promptCharLen`; FIM reports separately named prefix/suffix length fields. This reconstruction assumes the recorded ordinary prefix and no chat wrapper.

### Counted work and assumptions

- **Input:** native prompt characters multiplied by the token-per-character ratio of that choice’s retained prompt. The 50 empty prompts borrow the nearest nonempty prompt’s ratio within the same session. This uses the native length while allowing for the released prompt join’s inaccuracies; it is an estimate, not an exact prompt replay.
- **Output:** positive native `numTokens` once. For 57 choices with zero counters but nonempty output, use tokenized suggestion length. Add one assumed termination token per generated candidate; stop-token inclusion is not documented in the released counters.
- **Same-request alternatives:** the historical client normally requests three candidates for parser-handled multiline completions and one for single-line or server-handled completions; cycling and experiments can override this. Multiline status is inferred from recorded line count or a prefix ending at a Python/JavaScript block opener. C++ uses server handling. Observed alternative counts are always a floor. These rules produce **1,314 generated candidates**, of which **291 are estimated unseen alternatives**. Their output length is the mean of the observed choices from the same request. The configured 500-token cap is not counted as actual usage.
- **Cache:** client replay and typed-prefix cache hits reuse a previously generated choice and are deduplicated. Central input counts charge a full prefix for each newly generated candidate because server-side shared prefill is not documented. A shared-prefix scenario is retained. There is no separate reported reasoning stream.
- **Small client scores:** the implementation calculates two short linear confidence/quantile scores per display. A conservative 100 scalar operations for each of the 2,394 display/browse events adds 239,400 operations across the cohort. Displayed or accepted events do not cause another transformer call solely by appearing in the data.

Estimated totals are 368,930.683 input tokens and 22,896.5 output tokens, or 391,827.183 tokens. With the model coefficient below:

`FLOPs per accepted choice = (391827.1828310954 × 24,000,000,000 + 239400) / 382`

The point’s `tokens` field is 1,025.7256 input-plus-output tokens per accepted choice. `compute_statistic=total_per_completed_sample` expresses this amortization. `compute_subset=all` includes the rejected and other nonaccepted work within the defined request cohort. `ai_attempts=not_applicable` avoids presenting requests or normalizing fragments as independent task runs.

| Changed assumption, otherwise central | FLOPs per accepted choice |
|---|---:|
| Central | 2.462 × 10¹³ |
| Observed choices only; no unseen alternatives | 1.948 × 10¹³ |
| One shared prompt prefill per request | 2.002 × 10¹³ |
| Stored prompt strings without native-length alignment | 2.546 × 10¹³ |
| Three candidates for every request | 5.816 × 10¹³ |
| 4B / 24B active parameters | 0.821 / 4.923 × 10¹³ |
| Divide by all 386 acceptance events | 2.436 × 10¹³ |

These are separate assumption checks, not a confidence interval. Entirely unshown or canceled requests cannot be identified from the released display-state data and fall outside the stated cohort.

## Model

The model is the unidentified production Copilot checkpoint used in August 2022. The [Codex paper](https://arxiv.org/html/2107.03374v2), abstract and §3, reports a 12B research model and explicitly distinguishes the production version powering Copilot. **12B active parameters is a weak family transfer**, with 4–24B sensitivity; it is not a disclosure of the study model’s size. The coefficient is twice that assumption, 24 billion FLOPs per processed token, omitting context-dependent attention, which `compute_flops` carries separately (`research/attention-correction.md`).

GitHub announced [public preview on June 29, 2021](https://github.blog/news-insights/product-news/introducing-github-copilot-ai-pair-programmer/) and [general availability on June 21, 2022](https://github.blog/news-insights/product-news/github-copilot-is-generally-available-to-all-developers/). Neither identifies when the August 2022 weights became available. The [February 2023 upgrade announcement](https://github.blog/ai-and-ml/github-copilot/github-copilot-now-has-a-better-ai-model-and-new-capabilities/) confirms subsequent Codex and completion-pipeline changes. The model release date remains blank.

## Human time

The estimate is for a programmer who already understands the local task and relevant library, writing comparable short code or comment fragments without a coding assistant. It excludes learning the task from scratch and proving that a whole program is correct. It targets the quality of the source-recorded accepted text, including its imperfections. This makes `match` the assumed target, not a measured unaided success result.

The 382 distinct accepted texts average 54.2 characters and 1.79 reported lines; 125 contain at most 20 characters and 83 contain a newline. Inspection includes partial identifiers and comment endings, routine estimator calls, constructors, pandas transformations, and occasional multi-line loops. Larger accepted suggestions can be faulty: acceptance is not a correctness test. Repeated prompt/comment material also means these lengths are not measured net additions to the file.

A **20-second** central estimate allows a familiar programmer to choose or adapt a short local fragment, type it and check that it fits the immediate intent. As a scale check, roughly 54 characters at an assumed five characters per second takes about 11 seconds, leaving about nine seconds for local selection and inspection; this is not a measured typing model. **8–60 seconds** spans an obvious partial-name completion through a longer fragment requiring additional thought. The central judgment reflects this mix, rather than treating every suggestion as a complete line or requiring fresh problem solving for each one.

The study records AI-assisted reviewing and acceptance, with no unaided writing control. None of those timings enter the 20 seconds; `human_attempts` and `human_time_subset` are therefore `not_applicable`. The concrete input difference is that a human programmer knows the task instructions and intended solution, whereas Copilot receives the code prefix. The study deliberately presented task instructions as images to avoid direct copying into Copilot. This is recorded as `different_inputs_or_tools`.

## Reproduction

Use explicit paths; outputs must be new and outside the source evidence. The extractor requires Python with pandas and NumPy and verifies the original Git blob before restricted loading. The calculator requires Python and tiktoken and uses only retained vocabulary files; no API requests or notebooks are executed.

```sh
python3 -B research/copilot-cups/extract_logs.py --source agent-work/sources/copilot-cups/data_labeled_study.pkl --output /tmp/cups-logs-new.json
python3 -B research/copilot-cups/recompute.py --sources agent-work/sources/copilot-cups --logs /tmp/cups-logs-new.json --models research/copilot-cups/model-inputs.csv --output /tmp/cups-calculation-new.json
```

Paths above show the published layout; supply the corresponding explicit paths for another layout. `agent-work/sources/copilot-cups/source-manifest.json` hashes all retained original and extracted source files. `verify_sources.py --sources <source-directory> --output <new-json>` separately checks 16 pinned Git objects and 26 original ZIP members with the Python standard library. `calculations.json` retains request components, deduplication membership, donor prompt locators, accepted texts and sensitivity results.
