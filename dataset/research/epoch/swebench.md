# SWE-bench Verified: original effort estimates and Epoch model work

## Human effort

The work unit is one issue-equivalent from the exact set of 484 issue IDs listed in each selected Epoch run. A model receives the issue and repository and runs a bash/editor agent. Success is the original fail-to-pass and pass-to-pass test suite. The human comparison concerns understanding the problem, devising a solution and writing the code, with prior repository familiarization excluded.

[Original annotation instructions](https://cdn.openai.com/introducing-swe-bench-verified/swe-b-annotation-instructions.pdf), section 3, question 3.1 (PDF page 4), ask professional annotators to estimate this work for an experienced engineer who already spent a few hours becoming familiar with the codebase. Annotators inspect the original PR and tests to make the estimate; the hypothetical worker does not receive the gold patch. The source is an estimate, not a timing experiment. Its rubric also allows the annotator to assume sufficiently clarified high-level requirements where the original issue was ambiguous; it does not establish that humans solved every issue from the exact original prompt. The PDF's final bin text loses the greater-than symbol; the [original release](https://openai.com/index/introducing-swe-bench-verified/) explicitly defines it as over four hours. The release also explicitly warns that these estimates presume the engineer can figure out the solution and do not imply a 100% solve rate for typical engineers.

Original data: [princeton-nlp/SWE-bench_Verified Parquet](https://huggingface.co/datasets/princeton-nlp/SWE-bench_Verified/resolve/main/data/test-00000-of-00001.parquet), downloaded fresh as `agent-work/sources/epoch/swe-verified.parquet`, with SHA256 recorded in `agent-work/sources/epoch/legacy-accounting/expansion-03/calculations.json`. The downloaded 500 records contain 194 under-15-minute, 261 15–60-minute, 42 1–4-hour and 3 over-4-hour labels. This differs by two records from the release article's 196/easy figure. We use the actual record-level labels joined by exact ID, not the article's plot counts. Epoch's selected 484 contain 185, 254, 42 and 3 respectively.

We assign 7.5, 37.5, 150 and 360 minutes to those bins. The first three are arithmetic interval midpoints, a transparent within-bin mean assumption without recorded durations. The open upper bin uses six hours: the three actual tasks require broad refactoring, parser extensions, and mathematical distribution support, but are bounded patches rather than an unspecified multiday project. Four to ten hours for that bin is a sensitivity range, not a measured interval. Jointly varying all four bin values to [5,20,90,240] and [12,50,210,600] minutes gives the sensitivity reported per point. No artificial human sample count is assigned. Averaging estimated bin values remains `estimated`/`assumed`/`point_estimate`, not arithmetic on observed timings.

Task/patch inspection supports the interpretation of the bins, without pretending patch length determines time:

- `astropy__astropy-14309`, under 15 minutes: format detection falls through after an unsuccessful suffix check; the fix returns that check's Boolean. A supplied traceback and a local branch correction fit a short, familiar-code fix.
- `astropy__astropy-14995`, under 15 minutes: mask propagation tests the operand instead of its mask; reproduction and intended copying behavior are supplied.
- `astropy__astropy-12907`, 15–60 minutes: nested compound-model separability requires preserving the right-hand matrix block. The one-line patch still requires tracing shape/semantics; its size does not justify classifying it as immediate work.
- `astropy__astropy-13033`, 15–60 minutes: misleading TimeSeries required-column exceptions need scalar/list formatting and corrected error content.
- `astropy__astropy-13398`, 1–4 hours: direct terrestrial-to-observed coordinate transforms span registration, reference frames and numerical transformation functions; supplied proposed code helps but requires integration.
- `astropy__astropy-13579`, 1–4 hours: sliced WCS inverse conversion substitutes the physically correct fixed coordinates for dropped world axes; modest code size conceals domain reasoning.
- `pydata__xarray-6992`, over 4 hours: index refactor inconsistencies require changes across set/reset-index bookkeeping, variable/coordinate/index sets and conversions.
- `sphinx-doc__sphinx-7590`, over 4 hours: C++ user-defined literal support affects literal parsing, suffix rules, AST objects, references and IDs across C/C++ domain code.
- `sympy__sympy-13878`, over 4 hours: predefined CDFs for numerous distributions require formula implementation, support boundaries, special functions and symbolic-versus-numeric behavior, with issue-provided test examples.

All listed issue texts and complete original gold/test patches are retained in the original Parquet. The inspection covers two examples in each closed bin and all three in the open bin. We do not substitute our own patch-length model for the professional estimates.

## Performance and scope

The human target is a correct patch conditional on having the capacity to solve the issue. That is not an observed success probability across attempts. The model's observed probability is passing benchmark tests. [The original source's 2026 audit](https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/) identified incorrect rejection of valid patches and prior exposure to solutions; its deliberately difficult 138-task audit is not treated as a random estimate of the whole benchmark's error rate. We judge these three model runs **below the assumed complete-correct-patch target**, rather than treating lack of a human reliability experiment as sufficient for unknown. This is a qualitative target comparison, not a claim that all expert attempts succeed or that native test failures equal incorrect patches. `different_assessment` and `different_attempt_selection` mark the test-versus-correct-patch target and conditional human effort versus all model attempts. No claim is made that this represents uncontaminated new professional work.

The direction judgment combines the native result gap with direct inspection. Inspection then confirms substantive failures alongside misleading test failures:

- All three models on `django__django-10999` implement exactly the negative-duration lookahead fix suggested in the issue. The gold patch instead changes duration sign semantics. Two failing new tests therefore cannot fairly be treated as proof the models ignored the requested behavior. This is an inspected example of assessment overreach.
- GPT-5.3 Codex on `django__django-10097` produces the same authentication regex change as the gold patch, but the run reports 12 test errors (and 1,858 passes across both test groups). This is another concrete reason not to interpret native failure as incorrect code.
- Gemini 3 Pro on `django__django-11451` adds a missing-username return but omits the missing-password condition explicitly proposed in the issue; six new tests fail. The patch does not complete the stated correction.
- Opus 4.6 on `django__django-13023` changes `django/forms/fields.py` while the issue explicitly concerns a **model** DecimalField during model saving; it leaves the target model-field converter untouched, and both new tests fail. This is a wrong-component fix, not merely hidden naming requirements.
- GPT-5.3 Codex on `django__django-13112` changes migration relation resolution but leaves the foreign-key deconstruction path lowercasing the app label. The model-saving/migration problem described in the issue is therefore not fully addressed. The new test errors; the wrong-path omission is visible directly in the code comparison.
- Both Opus 4.6 and GPT-5.3 Codex on `django__django-13512` correct editable JSON form rendering but not readonly admin rendering. This is only weak evidence of incomplete work, because the issue emphasizes editing; it is not counted as an unambiguous model error.

The small inspection sample is chosen for understandable under-15-minute tasks, not for prevalence estimation. It establishes that both substantive errors and assessment defects are present. Taken with the remaining large overall test gap, the best judgment is below a completed correct deliverable, with uncertain magnitude. It does not justify a numerical “corrected solve rate.” Complete-fix human effort is compared against **all-attempt** model mean compute; this selection difference is explicitly retained rather than dividing model compute by successes to fabricate a completion cost.


## Model and workload accounting

Initial tranche uses three already reviewed model identities and shared 100B active-parameter assumptions from the authorized current production registry. No architecture is claimed disclosed. Native token usage is complete across the 484 summaries for these runs. Shell execution and deterministic grading do not add model FLOPs. There are no recorded helper-model calls. Attention costs for cached contexts remain outside the shared 2P approximation.

Do not apply one provider's counters to another: the Anthropic SWE log has *uncached* input plus separately reported cache reads and writes in its source total. Google includes cache reads inside input, but reports native reasoning additionally to ordinary output. OpenAI includes cache reads inside input and reasoning inside output. The per-run identities and current counter arithmetic below are replayed by [the read-only accounting check](reproduction.md). The original difficulty-bin join is retained in `agent-work/sources/epoch/legacy-accounting/expansion-03/calculations.json`. Headers and summaries are original remote .eval ZIP members retrieved by HTTP range, not whole-log approximations.

<!-- GENERATED POINTS -->

## agen-epoch-swebench-gemini3pro

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/5XdYZBG5Wy8DUMRqcYv4fn.eval); primary `google/gemini-3-pro-preview`; bash agent with 2,000,000-token limit and generation reasoning effort `provider default`. The header lists 484 unique issue IDs, all present once in summaries. All 484 complete; 353 pass, matching source accuracy 0.729338842975. Only the primary model appears in recorded usage. Failed attempts remain included. The header started at 2026-02-13T13:25:25+00:00 and reports only its final 203-task execution segment. Every header counter exactly equals the sum for those 203 summaries starting at or after that timestamp. The other 281 summaries started earlier. Full-summary input is 1,576,232,700 versus header input 666,218,811; the full 484-summary workload is used.

Native counters: input 1,576,232,700; output 4,346,893; cache read 1,458,153,901; cache write 0; reasoning 6,373,961; source total 1,586,953,554. Accounting: input - cache_read + output + reasoning; native reasoning is additional to output. Included 128,799,653 tokens / 484 = 266114.985537 per issue × shared coefficient 200000000000 = 5.32229971074e+16 FLOPs per issue. The source total identity is asserted in the generator to prevent reasoning/cache double counting.

Human task selection joins the exact header IDs to original difficulty labels: {'<15 min fix': 185, '15 min - 1 hour': 254, '1-4 hours': 42, '>4 hours': 3}. Weighted duration 2267.66528926 seconds; sensitivity 1302.27272727–3166.11570248 seconds. Model identity and its authorized existing 100B active-parameter assumption are copied from the shared registry without numerical changes.


## agen-epoch-swebench-opus46

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/aQiAg6mt8HPHXjKcJvax2d.eval); primary `anthropic/claude-opus-4-6`; bash agent with 2,000,000-token limit and generation reasoning effort `provider default`. The header lists 484 unique issue IDs, all present once in summaries. All 484 complete; 366 pass, matching source accuracy 0.756198347107. Only the primary model appears in recorded usage. Failed attempts remain included. Header usage reconciles exactly to all sample summaries.

Native counters: input 4,857,726; output 1,756,066; cache read 111,880,959; cache write 6,149,371; reasoning 0; source total 124,644,122. Accounting: input + cache_write + output; cache_read is separate and excluded. Included 12,763,163 tokens / 484 = 26370.1714876 per issue × shared coefficient 200000000000 = 5.27403429752e+15 FLOPs per issue. The source total identity is asserted in the generator to prevent reasoning/cache double counting.

Human task selection joins the exact header IDs to original difficulty labels: {'<15 min fix': 185, '15 min - 1 hour': 254, '1-4 hours': 42, '>4 hours': 3}. Weighted duration 2267.66528926 seconds; sensitivity 1302.27272727–3166.11570248 seconds. Model identity and its authorized existing 100B active-parameter assumption are copied from the shared registry without numerical changes.


## agen-epoch-swebench-gpt53codex

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/6w5buMbgeEqtRoE55cLZVv.eval); primary `openai/gpt-5.3-codex`; bash agent with 2,000,000-token limit and generation reasoning effort `high`. The header lists 484 unique issue IDs, all present once in summaries. All 484 complete; 362 pass, matching source accuracy 0.747933884298. Only the primary model appears in recorded usage. Failed attempts remain included. Header usage reconciles exactly to all sample summaries.

Native counters: input 250,791,240; output 7,008,896; cache read 158,370,432; cache write 0; reasoning 5,930,473; source total 257,800,136. Accounting: input - cache_read + output; native reasoning is a subset of output. Included 99,429,704 tokens / 484 = 205433.272727 per issue × shared coefficient 200000000000 = 4.10866545455e+16 FLOPs per issue. The source total identity is asserted in the generator to prevent reasoning/cache double counting.

Human task selection joins the exact header IDs to original difficulty labels: {'<15 min fix': 185, '15 min - 1 hour': 254, '1-4 hours': 42, '>4 hours': 3}. Weighted duration 2267.66528926 seconds; sensitivity 1302.27272727–3166.11570248 seconds. Model identity and its authorized existing 100B active-parameter assumption are copied from the shared registry without numerical changes.
