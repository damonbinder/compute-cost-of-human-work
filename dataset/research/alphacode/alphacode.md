# AlphaCode: one million candidates per programming problem

## reas-codecontests-alphacode-ensemble-1m

The point estimates **2.90 × 10¹⁹ FLOPs and 2,100 human active seconds per problem**, averaged over the original 117 CodeContests validation problems. The AI uses 500,000 samples from AlphaCode 41B and 500,000 from AlphaCode 9B, then example-test filtering and clustering to select at most ten submissions. Its reported solve rate is **35.5%**. The human baseline is an experienced competitive programmer, roughly Codeforces 1900–2100, attempting each unfamiliar problem for at most one active hour. **Below** is an estimated comparison with this stronger population; there is no measured human score on the 117-problem set.

Both coordinates are estimates. The sample count, model dimensions and validation result are reported. Large-model sample lengths and physical padding/reuse behavior are not published. Human duration comes from task inspection, with unsuccessful work included.

`compute_evidence=derived_assumed_inputs`: the million-sample workload and 117-problem cohort belong to this observation; 400 decoder steps is an assumed input calibrated from the smaller-model subset, not a borrowed complete task-compute total or a native large-model count.

## Source and work unit

Li et al., [Competition-Level Code Generation with AlphaCode](https://arxiv.org/abs/2203.07814), Table 3 and §4.1 specify the models. Appendix C.1 and Table A2 specify equal-sized 41B/9B pools and the validation 10@1M result. Appendix A.1 averages clustering performance across five subsamples; 35.5% is not an integer count of successful problems. Our work unit is one application of that sampling budget, not every research rerun or every checkpoint tried while developing the system.

The [author-organization CodeContests dataset](https://huggingface.co/datasets/deepmind/code_contests/tree/802411c3010cb00d1b05bad57ca77365a3c699d6) contains the original descriptions, public tests, hidden/generated tests and human programs. `valid.parquet` contains 117 records. Their seven rating-bucket counts exactly match Table A8: 29, 18, 20, 19, 15, 8 and 8. The source split spans July 15–September 20, 2021. All 117 are retained; the point is not conditioned on model success.

The source's separate December 2021 Codeforces competition experiment does **not** establish this point's compute. Appendix D.1 assigns hypothetical 3,750 TPUv4 plus 3,750 TPUv4i resources for two-hour simulated contest timing; this is not measured accelerator work. Appendix D.2 reuses the first generated pool for three evaluations. The exact pool size for that contest simulation was not recovered. We therefore do not multiply peak throughput by two hours or count only ten selected programs, and do not relabel this validation configuration as a native contest result. The original lead `reas-cf-alphacode` is related to this documented configuration, with that distinction retained.

## Generation length: original tokens, limited transfer

The authors' [Zenodo release](https://zenodo.org/records/6975437) contains the original visualization website. We retained its unchanged index, vocabulary and 141 `data.json` files. The 833 MB nested archive, including attention tensors, stays in `source-archive/` outside publication. The member CRC32 and hash are recorded in `agent-work/sources/alphacode/acquisition.json`.

The website says its regular examples were randomly selected, keeping at most one passing and one failing program per problem and language. Seven additional examples have editorial commentary. Every record has 30 decoder layers and 11 heads, identifying **AlphaCode 1B**, not either large model. Each prompt array has 1,535 displayed positions and decoder arrays have 767, one short of their model sequence dimensions. Blank positions at the ends include padding and suppressed special tokens. We count through the last nonblank code token and allow one additional end-of-code step, capped at 768. The blank rendering does not recover the actual EOS token ID, so that one-position allowance remains an assumption.

The calibration uses only regular, non-editorial examples whose names match the 117 validation records. This leaves one unsuccessful C++ and one unsuccessful Python example for each of 36 problems:

| Native 1B sample group | Records | Mean decoder steps, including EOS allowance |
|---|---:|---:|
| C++, unsuccessful | 36 | 450.44 |
| Python, unsuccessful | 36 | 312.31 |
| C++, successful | 32 | 431.84 |
| Python, successful | 26 | 292.15 |

Equal language weighting gives **381.375 steps** for the unsuccessful examples. Failed samples dominate the full generation pool: §4.5 reports that example filtering removes more than 99% of generated programs. We use a **rounded 400 decoder steps per candidate** for both large models. This transfers lengths from a smaller model and a 36-problem display subset; it is not a native large-model average. Longer or shorter large-model outputs and different lengths on omitted harder problems are material limitations. We use neither ground-truth solution length nor the 768-position limit as if it were observed output usage.

The main estimate charges a padded **1,536-position encoder pass per candidate**. The architecture and displayed tensors support this shape, but the visualization is not an execution trace of large-model sampling. Decoder generation stops logically at end-of-code (§4.1); physical batching may nevertheless continue arithmetic for finished slots. The 768-position scenario captures that possible extra work. Logical output tokens alone do not settle physical padding cost.

Metadata are drawn from 28 ratings, 50 tag combinations and two languages (§C.2), giving 2,800 possible encoder strings per problem/model. The central estimate assumes repeated samples are separately encoded, as in ordinary independent batched encoder-decoder calls. No source shows encoder sharing across samples. An alternative encodes each of the 2,800 possible strings only once per model and reuses both encoder outputs and cross-attention K/V. Randomized metadata prevent treating the whole million-sample pool as one identical prompt. Decoder self-attention K/V are cached within each generation in every scenario.

## Architecture and arithmetic

The 9B model has width 3,072, four K/V heads, eight encoder blocks and 48 decoder blocks. The 41B model has width 6,144, 16 K/V heads, eight encoder blocks and 56 decoder blocks. Query head width is 128, feed-forward width is six times model width, and vocabulary size is 8,000. Table 3 reports rounded totals of 8.7B and 41.1B weights.

Let `d` be model width, `k` the combined K/V width, `e` encoder positions and `t` decoder steps. Every multiply-add counts as two operations, including bfloat16 execution. Per block, encoder projection weights are `14*d² + 2*d*k`; decoder projection weights are `16*d² + 4*d*k`. The model registry records these transformer projection counts, not a misleading shared FLOPs-per-token coefficient for both networks. Embedding lookup arithmetic is not charged as a dense matrix multiplication; the vocabulary output projection is counted separately.

The recipe sums:

- Encoder projections: `2*e*Nenc*(14*d² + 2*d*k)`.
- Encoder score/value attention products: `4*Nenc*e²*d`.
- Decoder cross-attention K/V preparation, once per encoder input: `2*e*Ndec*2*d*k`.
- Decoder projections at every step: `2*t*Ndec*(16*d² + 2*d*k)`.
- Cached causal decoder score/value products: `2*Ndec*d*t*(t+1)`.
- Decoder cross-attention score/value products: `4*Ndec*d*e*t`.
- Vocabulary projection: `2*t*d*8000`.

At `e=1536,t=400`, one 9B sample costs **1.03684 × 10¹³** FLOPs and one 41B sample **4.75806 × 10¹³**. The formula keeps attention and cross-K/V preparation separate; multiplying total encoder-plus-decoder parameters by every token would count the wrong operations.

Sections 4.6 and C.4 describe a separate learned test-input generator, producing **50 test inputs**. Its size and mean output length are undisclosed. We assume the 41B architecture and 256 decoder steps per input, including the same encoder work: **1.85251 × 10¹⁵ FLOPs** per problem, about **0.0064%** of the total. Using 9B/128 steps or 41B/768 steps barely changes the point. C.4's **8,192** is the cap on existing candidate programs considered for clustering, not a count of neural test-input generations.

Total per problem is **28,976,390,274,337,996,800 FLOPs**. The exact digits reproduce the chosen recipe; they do not imply that the estimate is precise. `tokens=400,012,800` counts decoder text positions only: one million times 400, plus 50 times 256. Encoder positions remain in the operation calculation. Compilation, executing candidates/tests, clustering, ordinary host code, layer normalization, nonlinearities and other elementwise operations are outside this dominant neural matrix-arithmetic estimate. No extra neural ranker is identified in the source's final filtering/clustering procedure.

Public availability of the weights or an API was not established. Both model release dates remain blank; the paper date is not used as a release date.

## Human effort and comparison

The human receives the same plain-text task statement and examples, with a normal editor, compiler/interpreter and local testing. They may make at most ten external submissions. The endpoint is acceptance under the CodeContests tests, or stopping after one active hour. They do not receive an editorial, a human solution, actual hidden tests or AI help. The inspected human programs inform the estimator about task demands; they are not supplied to the hypothetical participant.

The one-hour cap is an explicit standalone practice-attempt assumption, not a source measurement. It permits substantial work on a difficult individual problem within the scale of the source's multi-hour contests, while avoiding an assumption that a 1900–2100 competitor eventually solves a 3300-rated problem. Unsuccessful hard attempts count at that cap. The source's two-hour contest simulation is context for this choice, not a conversion to a recorded 35-minute human time.

Two problems were selected from each published rating bucket using `random.Random(1172022 + bucket_lower)` on name-sorted records, without looking at model outcomes. All fourteen descriptions, tests, a source human program, timing judgments and reasons are retained in `human-assumptions.json`. The problems require distinct work, rather than merely typing their final code:

| Bucket; population count | Inspected work | Estimated active minutes for the two examples |
|---|---|---:|
| 800–1100; 29 | MEXor Mixup: prefix XOR and exceptional cases. Infinity Table: square-shell indexing and boundaries. | 12, 10 |
| 1200–1500; 18 | Mocha and Hiking: insertion-point proof. Backspace: backward matching and parity. | 18, 22 |
| 1600–1900; 20 | Array Differentiation: signed zero-sum reduction. Domino: dimension and tiling parity constraints. | 35, 28 |
| 2000–2300; 19 | Permutation Shift: prune candidate shifts and count cycles. Non-Decreasing Dilemma: segment-tree merge state and updates. | 48, 55 |
| 2400–2700; 15 | Top-Notch Insertions: ordering reconstruction and counting. Sports Betting: probability over subset states. | 60, 60 |
| 2800–3100; 8 | Palindromic Hamiltonian Path: path/color-state enumeration. Bridge Club: weighted hypercube pairing. | 60, 60 |
| 3200–3500; 8 | Stations: advanced interval updates. Gates to Another World: compressed hypercube connectivity. | 60, 60 |

Weighting the two-example bucket means by the full population counts gives **35.4487 minutes**, rounded to **35 minutes / 2,100 seconds** in the CSV. The scenarios in the assumption file give roughly **24–44 minutes**. Allowing 90 minutes instead of 60 on the 31 highest-rated problems gives about **43 minutes**. These ranges describe alternative judgments, not confidence intervals. There are no recorded human attempts behind this estimate, so human_attempts is not_applicable.

The original AlphaCode ensemble's separate contest assessment gives estimated rating 1238 and a mean placement around the middle of participants (§5.1). A 1900–2100 competitor is a substantially stronger algorithmic programmer. A [contemporary contest coach's account](https://codeforces.com/blog/entry/68288) supports that skill distinction, but supplies no task timings or score for these 117 problems; its Elo-MMR table is not silently substituted for Codeforces ratings. Together with the inspected 47 relatively accessible problems at ratings up to 1500 and another 20 at 1600–1900, this supports a **directional below** estimate for the 35.5% AI result. It does not establish a particular human percentage. The larger AI pool and the validation distribution limit transfer from its original contest rating.

Passing CodeContests tests is not proof of complete Codeforces correctness. The source's separate 50-solution audit found false positives and algorithmically slow accepted programs; those percentages concern a selected 1B audit and are not applied numerically to this ensemble. The estimated human target uses the same test-based endpoint. Missing direct human observations and the contest-rating transfer are evidence limitations, not known differences in the assumed assessment; comparison_issues is none_identified.

## Sensitivities and replay

| Alternative | FLOPs relative to central |
|---|---:|
| 200 decoder steps | 0.693 |
| 600 decoder steps | 1.309 |
| All 768 decoder positions, including possible batch padding | 1.569 |
| Transfer the native 1B unsuccessful mean directly | 0.971 |
| Unpadded encoder length transferred from those 1B examples | 0.815 |
| Cache all 2,800 encoder contexts once per model | 0.615 |
| 200 decoder steps plus encoder sharing | 0.308 |

The length, padding and sharing assumptions have much greater numerical importance than the test-input helper. They are alternatives, not a fitted probability distribution.

`recompute.py` requires Python 3 and `pyarrow` (tested with version 25.0.1). It checks every retained source hash, rereads the 117 records and native token arrays, verifies the seeded human selection and produces a new JSON output. It does not call a model or change source evidence. From any working directory:

```sh
python /absolute/path/research/recompute.py \
  --sources /absolute/path/sources \
  --human-assumptions /absolute/path/research/human-assumptions.json \
  --output /new/path/alphacode-calculations.json
```

The retained `calculations.json` contains per-model terms, all native example locators, bucket weights and scenario totals. The original large archive is not needed to replay the calculation.
