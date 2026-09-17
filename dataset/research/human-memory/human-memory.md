# Fixed-story recall with Llama 3 8B

## Sources and work unit

[Wang et al., Simulating Human Memory with Language Models](https://arxiv.org/abs/2605.25680), May25,2026, and [author repository](https://github.com/nickatomlin/simulating-memory), pinned to commit431474a92c1993c7d10e1e4ac4034f6a26be8903. Original task code, prompts, outputs, human records, and four transcripts are retained under sources. Only prompting conditionC1 (TaskPr: ordinary task instruction) is used. C2/C3/C4 human simulation and the compactor are excluded.

Each point is one reading-and-free-recall attempt on a named, fixed story. Humans have five minutes to read, then the story disappears and they type their recollection, using original words where possible. The model receives the entire story in one request and retains it in context while answering. This is a concrete different_inputs_or_tools condition. It is an imperfect memory comparison, not evidence that models retain information without contextual access.

The source stories contain948–2338 whitespace-separated words. The full story is supplied and full generated recall is counted; the output is not constrained to200words.

## Human records and time

The released folder contains56 JSON records:53 completed sessions with positive task durations and three started/incomplete records lacking completed-task timings. All53 completed records are used without selection on score or duration, including long sessions. There are52 distinct participant IDs: participant0063 completed two different stories. No same-story repeat is counted. These are released-session observations, not a reconstruction of the paper's stated50-person cohort. The public src/score.py similarly loads every scored JSON record; no participant eligibility list or cohort filter is provided. Do not claim the published50-person sample size for these subsets.

Human time is the arithmetic mean of duration_ms/1000 for that story. The recorded started_at-to-completed_at intervals differ from duration_ms by only0–24milliseconds, consistent with near-contemporaneous timestamp/counter sampling. This is the recorded task-session clock, covering study and typing, used as an active-engagement proxy. No pause/focus events or finer study/typing timestamps are released. No idle interval is invented or subtracted. The five-minute study interval is included once; the recorded durations already include it. The largest durations are1206.616s for Eyespy and1466.095s for Oregon Trail; they remain in the mean. Medians and all included run IDs are retained in calculations.json for sensitivity. Completed means a response was submitted, not that a correctness threshold was passed.

Human_time_evidence is task_timings, method other_calculation, statistic mean. The browser-clock-to-active-time limitation is explicit; review retained these as recorded task timings, consistent with other task-session measurements. Recruitment specifies US-based native English speakers experienced on Prolific, not memory specialists. Typical is appropriate, but eligibility of every extra released participant cannot be independently verified.

## Performance

Use released embeddingSimilarity, not BLEU. The original scorer explicitly says browser BLEU is near-zero across participants and uses embedding similarity instead. The model scorer uses all-MiniLM-L6-v2, with source and recall first normalized and truncated to200words each. The human platform's actual implementation is not released here; the model code explicitly describes this as matching that platform's200-word truncation. This is a shared scoring convention, not an exact-recall accuracy percentage. It emphasizes the story beginning and cannot establish factual correctness or coverage of the entire narrative. Embedding model calls are external scoring and excluded from task compute.

Baseball's mean similarity difference is small (0.637 versus0.611): classify broadly match. Eyespy0.760versus0.619, Pieman0.880versus0.613, OregonTrail0.737versus0.534: classify above on the reported recall-similarity criterion. These are judgments about the observed metric, not universal thresholds or exact-word claims. All attempts, not only good outputs, contribute. A quick text check of the first Baseball output finds a factual reversal: it attributes the sports/slang defense to Joe rather than Clara. That illustrates why similarity is not factual perfection.

## Compute

The selected hosted model directory is meta-llama_llama-3-8b-instruct. Reuse the existing Meta-Llama-3-8B-Instruct model record (released April18,2024),8B reported parameters and16B FLOPs/token. This is not GPT4 and not Llama3.1. The original Meta Llama3 tokenizer implementation/README are retained. The unmodified public [NousResearch Llama3 tokenizer distribution](https://huggingface.co/NousResearch/Meta-Llama-3-70B-Instruct/resolve/main/tokenizer.json) provides the family vocabulary; a previously retained copy is included here. No gated model access was used. The same generation-family vocabulary serves8B and70B, but no native API token counters are retained, so the hosted wrapper remains an assumption.

Tokenize each exact recall_prompt and llm_recall. Add10 input framing tokens for the original single-user Llama3 chat format and one output end-of-turn token. No system message is supplied in semantic_story_recall.py. The source's OpenAI-compatible adapter submits one user message. Count full fresh input plus generated output per attempt; average then multiply by16e9. No cache-read fields, finish reasons or raw usage objects survive in these records. This is explicit full-prefix accounting, not an assertion that server prompt reuse never occurred. Repeated prompts could have benefited from a provider cache. Source code retries API errors but the records do not identify failed-call work; no extra unobserved successful generations are imputed. Max reconstructed input+output is below4k tokens, within Llama3's8k context. The native output is used, never the configured max-token budget.

Attention over context, small non-matrix operations and provider precision differences are not reconstructed by2P/token. Compute_evidence is derived_assumed_inputs because of missing hosted token/cache accounting, rather than falsely claiming native counts. Tokens_accounting is input_output.

## Reproduce

Install the tokenizers package in the chosen Python environment, then run research/recompute.py SOURCE_DIR --output NEW_OUTPUT_JSON. The script reads only retained files and refuses to overwrite an output. calculations.json contains means, medians, task/run counts, raw selection IDs, scores, and text counts. No model inference is performed.

## Dispositions and schema

Digit span raw data are retained, but only whole adaptive-battery duration is recorded. Dividing that by trial count would conflate varying lengths, adaptive stopping, and response effort. A fixed-length point would need a justified timing reconstruction; no such point is submitted here. Narrative recall covers the related passage-memory lead, with explicit new IDs.

Review added memory_recall to COLUMNS.md: retaining and recalling supplied information after exposure. It covers these tasks without treating them as research or durable skill acquisition.
