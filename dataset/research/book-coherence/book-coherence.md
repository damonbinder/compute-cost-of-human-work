# Coherence annotation of book summaries

## Human effort and quality

The [study](https://arxiv.org/abs/2310.00785v4), Sections 3–4, asks experienced proofreaders to mark confusing spans and explain their questions, without consulting the underlying book. It reports roughly 30 minutes per summary. This is a source estimate, not a released set of clocks: `human_time_evidence=assumed`, `human_time_method=estimated`, and no timing sample count. The 1,800-second center applies to both summary styles; 15–45 minutes is a judgment sensitivity.

The released validation records for incremental summaries distinguish full and partial agreement. After excluding the two demonstration books also excluded from compute, full agreement is 460/711 human annotations (64.7%) versus 359/669 AI annotations (53.7%). Across all 88 validation books, the original human count is 499/768 (65.0%); the AI count is unchanged. Because our task includes acceptable explanatory questions, use `below`. The paper’s 79.7% human and 78.2% AI precision counts partial agreement too: the span is confusing, but its question can fail one or more standards. That broader result concerns span legitimacy, not equally good complete annotations. Recall is not measured. For hierarchical summaries, the direction is transferred from the same annotation method; direct hierarchical validation is not supplied. Humans can connect two spans or mark several sentences together; the AI processes individual sentences. This is `different_assessment`. Neither side is being paid here to read or summarize an entire novel or verify the summary against the book.

## Records

The [released code and annotations](https://github.com/lilakk/BooookScore/tree/094bf69bc55317b728b4b2bb679c287e0176ae6c) supply 100 cleaned summaries per style and 98 GPT-4 annotation records per style. The two absent books, `the-faraway-world.epub` and `the-ferryman.epub`, are excluded; their incremental summaries appear verbatim as the prompt demonstrations. They are not presumed to have no errors. A present JSON null means no errors and remains included.

All included summaries exactly match the corresponding human-annotation text. The released annotations retain only parsed error questions and types, not complete API responses or usage. The human half-hour estimate and precision comparison describe the broader study; they are not separately measured for our 98-record subsets.

## Compute

The original scorer sends the entire summary and the same example-rich prompt once for every sentence. It keeps only flagged sentences in its output dictionary. We reconstruct every sentence call, including those returning no confusion and repeated sentence occurrences. No API request or model inference is executed during reconstruction.

The April 2024 package commit `9fabd0f` renamed `prompts/get_gpt4_annotations.txt` to `prompts/get_annotations.txt` with **zero changes**. Its retained deletion patch provides the earlier scorer. The earlier API wrapper defaults to `gpt-4` and sends a single user message. It does not identify an API snapshot. An imported MiniLM model is loaded but never called by the annotation path; no helper inference is silently omitted.

Tokenization uses cl100k_base for GPT-4. The earlier wrapper's separate GPT-2 counting utility is not called by this annotation path. Seven framing tokens per call are assumed. Sentence splitting uses the source's NLTK 3.8.1 algorithm, with official English Punkt parameter tables loaded as plain text, without loading untrusted pickle files. Every retained error sentence exactly matches a reconstructed sentence. Historical parameter identity is not established, but this agreement supports the reconstruction.

Canonical responses are rebuilt in the requested two-line format from stored questions/types; unflagged sentences use the requested no-confusion response. This estimates output length, not original response bytes. No cache discounts are assumed. Retries after invalid or failed calls are allowed by the original code but not logged; the center counts one completed response per sentence. A 10% extra-call scenario multiplies the FLOP center by 1.1 and is not an observed retry rate.

| Quantity | Hierarchical summaries | Incremental summaries |
|---|---:|---:|
| Included summaries | 98 | 98 |
| Sentence calls | 3,336 | 4,559 |
| Reconstructed input positions, including framing | 18,823,564 | 26,485,012 |
| Canonical output positions | 35,297 | 54,777 |
| Mean total tokens per summary | 192,437.3571 | 270,814.1735 |
| FLOPs per summary | 1.0584054643e17 | 1.4894779541e17 |

The shared original-GPT-4 coefficient is 550 billion FLOPs/token (275 billion active parameters), an existing architecture assumption rather than a disclosure. Changing that shared coefficient scales both rows. Context-dependent attention is outside this approximation and is added back in `compute_flops` (`research/attention-correction.md`).

Response reconstruction has modest influence: assigning the original 100-token maximum to every sentence increases mean token totals to 195,481.2653 and 274,907.2653, respectively, about 1.6% and 1.5% above center. This does not bound unknown repeated calls. The center is an analytic workload estimate, not a measured attempt-level compute mean.

[recompute.py](recompute.py) regenerates [calculations.json](agent-work/derived/book-coherence/calculations.json), including each book's counts. Retained source files and hashes are in the source manifest. The original books are not required or redistributed for this task.
