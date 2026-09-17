# Berkeley Crossword Solver without local search

## crossword-nyt-2021-03-23-berkeley-bp

One complete solve of Dan Schoenholz's March 23, 2021 NYT crossword: 15 × 15 cells, 76 clues and 185 letters. The work starts with the trained model and its prepared answer index, reads the clues and grid, and returns a filled grid. The released BP-only recipe costs **474,053,630,544 FLOPs**. Amy Reynaldo reported **4:00**, or **240 seconds**, for this exact puzzle.

This is the 2022 Berkeley Crossword Solver (BCS) with local search disabled. It is separate from the original Dr.Fill and the 2021 tournament hybrid. It does not resolve the older Dr.Fill compute lead.

### Evidence and configuration

The [authors' repository](https://github.com/albertkx/Berkeley-Crossword-Solver/tree/3dc64ad2fb83eaa5b84062c3f37e9f2b1affd804) supplies the puzzle, solver and configuration. `master/README.md` specifies `max_candidates=500000` and `num_iters=10`. Set `iterative_improvement_steps=0` to take the return before `setup_t5_reranker` in `BPSolver.solve`. This removes the local-search stage ablated in [paper Table 4](https://aclanthology.org/2022.acl-long.219.pdf). ByT5 and the GPT-2 segmenter perform no calls in this configuration.

The DPR submodule is pinned at `f0a2d940376987324d9a7d667ee1cdf7dc78e6c4`. Its `HFBertEncoder` loads BERT-base-uncased and returns the final CLS state. The original checkpoint's retained first 262,144 bytes contain the complete metadata pickle. Opcode inspection, without executing pickle code, recovers `sequence_length=32` and `projection_dim=0`. `BertTensorizer` pads every clue to 32 positions; batching does not reduce those positions. The workload is therefore **76 × 32 = 2,432 encoder positions**, including padding and special tokens. No text generation or token cache is involved.

The encoder has 12 layers, width 768, intermediate width 3,072 and 12 heads. Its 109,482,240 parameters include the pooler: the underlying BERT forward computes the pooler before the DPR wrapper discards that output. The separate answer encoder is not called during a solve; source instructions prepare its embeddings beforehand. The registered model is the crossword-trained clue encoder, with an encoder operation recipe rather than a shared 2P coefficient.

The [first checkpoint upload](https://huggingface.co/albertxu/Berkeley-Crossword-Solver/commit/9d9f8b8173a41c36aa1032cdaa8eda45d58a937a) was May 20, 2022. Its tree contains the same checkpoint and wordlist hashes as the current release. The [same-day authors' announcement](https://bairblog.github.io/2022/05/20/crosswords/) links the code release. The release date is **2022-05-20**, not the earlier BERT release or the 2021 hybrid competition date.

### Operation count

The calculator reads the original puzzle and answer list. `DPRForCrossword` selects FAISS `IndexFlatIP`, and the requested 500,000 results are clamped to all **437,724 indexed answers**. Consequently the length-filtered domains can be counted without knowing the neural scores. Source canonicalization removes non-ASCII letters and uppercases the answer; score normalization precedes duplicate-string merging. The one duplicated seven-letter answer matters for four clue domains.

| Answer length | Puzzle clues | Retrieved answers of that length | Unique BP candidates |
|---|---:|---:|---:|
| 3 | 21 | 5,874 | 5,874 |
| 4 | 22 | 16,836 | 16,836 |
| 5 | 19 | 29,433 | 29,433 |
| 6 | 2 | 36,582 | 36,582 |
| 7 | 4 | 44,989 | 44,988 |
| 8 | 4 | 47,126 | 47,126 |
| 11 | 2 | 38,044 | 38,044 |
| 15 | 2 | 36,134 | 36,134 |

For sequence length S, width d, intermediate width f and layer count K, BERT matrix work per clue is `K × (8Sd² + 4Sdf + 4S²d) + 2d²`. The last term is the executed pooler. Retrieval contributes `2 × 768 × 437724` operations per clue. Additions, biases, attention normalization, residuals, layer normalization, GELU and pooler tanh are included separately.

For each clue with length L, M raw candidates and N unique candidates, candidate-score preparation costs `7M − 1` scalar operations, and variable initialization costs `9N`. With one operation per exp/log, each BP iteration costs `L × (57N + 104)` for variable-to-letter messages plus `(L + 5)N` for variable normalization. Each letter cell adds 156 operations per iteration and 52 at initialization. These include the dense 26 × N multiply and reduction at every crossing; the stored one-hot array is not treated as sparse execution. Python's `sum` of NumPy arrays also executes its initial zero-plus-array addition.

The released `solve` calls greedy decoding **twice**, restoring the candidate state after each. Each pass adds a length-dependent log offset to every candidate, costing `N + 2` operations per clue. Subsequent ranking, string compatibility checks and index gathers perform no floating arithmetic. They can take CPU time, but are outside the FLOP quantity. No search-path multiplier is needed for these floating operations.

| Component | FLOPs |
|---|---:|
| BERT matrices | 416,080,723,968 |
| BERT scalar arithmetic | 1,092,602,764 |
| Flat answer retrieval | 51,098,148,864 |
| Candidate-score normalization | 11,500,595 |
| BP initialization | 14,796,161 |
| Ten variable-message passes | 5,572,381,610 |
| Ten variable-normalization passes | 179,901,780 |
| Ten letter-normalization passes | 288,600 |
| Both greedy decodes | 3,286,202 |
| **Total** | **474,053,630,544** |

Multiply-adds count as two operations regardless of precision. The scalar recipe counts exp, log, sqrt, erf and tanh as one operation each and uses an explicit mean/variance layer-normalization expression. Counting each special function as 20 operations gives **478,269,478,452 FLOPs**, 0.89% higher. Kernel-specific scalar algorithms are not measured. Five or twenty BP iterations give 471,177,344,549 or 479,806,202,534 FLOPs; those are alternative configurations, not uncertainty intervals with the reported accuracy held fixed. The central uses the released ten iterations.

This is `derived_supported_inputs` and `operation_count`: source dimensions and workload determine the main arithmetic. It is an analytic recipe, not a recorded run; `compute_subset` and `ai_attempts` are `not_applicable`.

### Human time and quality

[Amy's original write-up](https://crosswordfiend.com/2021/03/22/tuesday-march-23-2021/) labels the NYT solve `4:00 (Amy)` and publishes the completed grid. Its constructor, date and theme agree with the released puzzle. The unusual long fills append ION to familiar expressions; the shorter clues mix definitions, names, general knowledge and wordplay. This is a complete crossword solve, not 76 independent fact-recall questions.

Use `human_skill=expert`. The [official 2021 ACPT standings](https://docs.google.com/spreadsheets/d/1lOyPqyAh6r2Q488U_Z_e2kUYerq0Op9QYBD_RBNwtn4/edit) identify Amy Reynaldo at rank 55, Division B, with one incorrect letter across seven attempted puzzles. Those tournament outcomes support her expertise; they do not contribute timing observations. The time field uses her one recorded solve of this puzzle, `task_timings`, `unit_conversion`, `point_estimate`, and `human_attempts=1`. `all` means the one published timed attempt, not all her lifetime solves. The blog timing is self-reported; start/stop events and an attention trace are not retained. No writing-up time is added.

Classify BCS BP-only **below**, as a transfer of puzzle-completion reliability. Table 4 reports **44.3% perfect puzzles** on its NYT 2021 ablation, while Amy completed this puzzle and her separate tournament record has six perfect puzzles out of seven. The ablation cohort includes a range of daily difficulties; this Tuesday is easier than the late-week puzzles. There is no released BP-only outcome for this particular input. `different_assessment` records the different evaluation sets. The label is not a claim that BCS failed this puzzle, nor that this human succeeds on every puzzle.

The main-results table lists 234 NYT tests, but 44.3% is not obtainable by rounding an integer numerator over 234 to one decimal. The paper provides no separate ablation run list. Preserve its percentage without inventing a success count or treating the exact ablation denominator as resolved.

### Reproduction

Run `python3 -B recompute.py --sources /absolute/path/to/sources --output /absolute/path/to/new-result.json`. Python 3.9+ and the standard library suffice. The output path must be new and outside the evidence tree. The calculator parses the original inputs, reports all components and sensitivities, and hashes the retained source files. It does not execute the solver, load model weights, or modify evidence. `calculations.json` is the retained result. The source manifest gives original locators and hashes; pinned source blobs and the released wordlist hash were also checked directly.
