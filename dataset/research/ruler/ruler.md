# RULER passkey retrieval

Two points estimate one Llama 3.1 8B Instruct retrieval at the original RULER 4K and 128K settings. The task is to return a seven-digit number associated with a named key in supplied text. The background repeats a short, irrelevant passage. The human has the document available and may use ordinary Find to locate and copy the number.

## Original result and task

The [August 6, 2024 paper](https://arxiv.org/html/2404.06654v3), Appendix A, identifies `meta-llama/Meta-Llama-3.1-8B-Instruct`. Section 4 specifies 500 examples per task and length, greedy generation, and vLLM. Appendix B identifies passkey retrieval as the single word–number needle in repeated filler (`niah_single_1`). Appendix E Table 10 reports **100% at both 4K and 128K**. These are the passkey results, not the thirteen-task composite or the separate essay-background task.

The source scorer checks whether the expected number appears anywhere in the generated response. It does not require a bare answer or reject extra text. The source's answer prefix encourages a short continuation. There are no released per-response usage records for these results. The compute values below reconstruct the task recipe; the 500 source examples establish performance, not an observed compute distribution.

## Reconstructing the input

Use original repository revision `dbc6a83c2f60d034dfaab8e7af42dde1a5d2e3dc`, August 1, 2024. Thirteen retained files match its Git blobs, including the generator, templates, task settings, tokenizer wrapper and serving configuration. The newer repository changed the generator and is not used for numerical inputs.

The historical generator chooses a random adjective–noun key and a random seven-digit value. It inserts one sentence into repeated copies of:

> The grass is green. The sky is blue. The sun is yellow. Here we go. There and back again.

The two independently reconstructed first examples use `wandering-age → 8090293` and `flagrant-woodshed → 1348050`. Complete reconstructed prompts and every key, value, insertion position and prompt hash are retained in `calculations.json`. They are reconstructions, not claimed original test records.

The word lists are from the original `wonderwords` 2.2.0 package. Its PyPI release dates to February 2021 and was the latest release before this August 2024 study. The source dependencies did not pin its version. We assume this release and the generator's default seed 42. The calculator reproduces the sorted unique adjective–noun product without materializing millions of strings; its indexed set has 6,175,260 members.

Appendix D Table 6 explicitly prints the Llama 3/3.1 chat wrapper, including BOS, user and assistant headers, and a prefilled answer prefix. This supplies the model-specific wrapper missing from the example shell configuration. We combine it with the historical task template and its singular-number substitution. The exact serving text was not archived; the printed wrapper and released generator are the reconstruction basis.

Meta's original HF tree gives the same Git blobs as the retained public mirror for both `config.json` and `tokenizer.json`. Thus this uses the actual Llama 3.1 vocabulary, rather than a different-family tokenizer. The generator uses tokenization without automatically added special tokens. The serving tokenizer's normal encoding adds one BOS, in addition to the explicit BOS in the paper's wrapper; the central count includes this extra position. Removing it is a recorded sensitivity.

Each repeated passage costs 24 tokens, including its boundary with the next line. The generator increases filler by 25 passages, about 600 tokens, until it would overflow. Its initial sizing probe counts the expected answer as well as the prompt and reserves another **128 tokens**. It then backs off one increment. Each final example is checked against the input-plus-128 limit. Newline removal is disabled in the historical task configuration.

Reconstructing 500 examples per setting gives:

| Nominal limit | Repeated passages | Generator prompt range | Mean processed input, including serving BOS |
|---|---:|---:|---:|
| 4,096 | 150 | 3,681–3,702 | 3,687.526 |
| 131,072 | 5,450 | 130,881–130,902 | 130,887.424 |

We do not substitute the nominal limit or `limit − 128` for actual input length. Seed or word-list differences mainly change the small key/instruction term; the 600-token filler increment is recovered directly.

## Output and cache assumptions

The 128-token setting is an output cap, not observed usage. The central completion is a leading space, the seven digits, a period and an end-of-turn token: **six generated tokens** under the original vocabulary. This is an estimate supported by the answer prefill and simple required payload. The calculator retains four-token bare-answer, twenty-token continuation and full 128-token-cap scenarios. At 4K, using the full cap increases compute by 3.8%; at 128K, by 0.16%.

Within generation, the KV cache avoids rerunning the prompt. The last prefill position predicts the first output token, and the last emitted token is not fed back; the Transformer therefore processes `N + O − 1` positions. The CSV's `tokens` is the conventional input-plus-generated total `N + O`.

The historical run configuration does not enable automatic prefix caching, and the retained vLLM configuration defaults it to false. We therefore charge each reconstructed task's full prompt. This is a source-supported implementation assumption, not a recovered cache counter. The source paper specifies vLLM but does not pin its actual experiment build; the repository's dependency version supplies the implementation reference. No model helper or retry loop is part of the task recipe. We do not add unobserved extra runs.

## Operation count

The primary Meta configuration gives 32 layers, width 4,096, MLP width 14,336, 32 query heads, eight KV heads, head width 128, and vocabulary 128,256. It specifies untied embeddings. The resulting total is **8,030,261,248 parameters**, consistent with the shared nominal 8B registry record, which is copied unchanged. The block projection matrices contain **6,979,321,856 parameters**. Input embedding lookup is not a dense vocabulary multiplication.

Let `d=4096`, `L=32`, `k=1024`, `i=14336`, `V=128256`, input length `N`, generated length `O`, and `G=O−1`.

- Transformer projections: `2 × L × (2d² + 2dk + 3di) × (N+G)`. This includes Q, K, V, attention output and all three gated-MLP matrices.
- Output projection: `2dV × O`. vLLM prunes unneeded prompt states before computing logits; the source does not request prompt log probabilities.
- Causal attention matrices: `4Ld × [N(N+1)/2 + GN + G(G+1)/2]`, counting both QK and attention–value multiplication at two operations per multiply-add.
- Scalar operations: an explicit approximate allowance of six operations per attended pair per head for score scaling/softmax, plus RMS normalization, residual additions, rotary positions, SwiGLU and output sampling. The complete expression is in the calculator. This adds 0.10% at 4K and 0.84% at 128K to the matrix-operation sum.

The calculation includes attention to every causal position; grouped-query attention reduces K/V projection size, not the number of query heads. It does not multiply by eight because the eight source GPUs divide the model's work. BF16 does not discount the arithmetic. Matrix-tile padding, kernel-specific scalar instruction choices and non-neural tokenization are not measured. The scalar allowance is an estimate, not a hardware profile.

The retained vLLM FlashAttention call is causal. The central recipe counts the causal triangle; a full-square prefill sensitivity increases the 4K estimate by 6.5% and the 128K estimate by 70.5%. This is an implementation sensitivity, not an assertion that the experiment computed the unused upper triangle. A separate all-prompt-output-head scenario increases the estimates by 7.0% and 2.2%. These identify the consequences of losing the source-supported inference optimizations.

## Human time

Estimate **10 active seconds** for an ordinary computer user familiar with Find, with **5–25 seconds** as scenarios. The supplied document is open and the question names the target key. The user reads the query, opens Find and enters or pastes the key, moves from a question/prefix occurrence to the matching fact, then copies and checks the seven digits. Roughly three seconds to orient to the question, four to locate the fact, and three to copy/check it support the central value. These are task-inspection judgments, not a fitted timing model or a measured sample.

Document length contributes little active effort in this workflow because the software searches the filler. The same central duration is therefore used at both context settings. This assumes ordinary responsive document search, not reading the whole passage or learning the key beforehand. The human quality target is returning the correct value reliably, broadly comparable to the source's 100% retrieval result. No human sample size or observed success percentage is implied.

The model receives the full prompt and has no Find tool. The human's document search is a concrete `different_inputs_or_tools` condition. `memory_recall` follows the schema's inclusion of retrieval from supplied material; the actual access conditions are stated in the task description.

## Point definitions

### memo-ruler-passkey-4096-llama31-8b

One passkey retrieval at the source's 4K setting. Estimated mean reconstructed input 3,687.526 plus six generated tokens: **3,693.526 tokens** and **5.5181288452890625e13 FLOPs**. Human time: **10 seconds**. Original AI result: 100% on 500 examples; assumed human target: reliable correct retrieval with document search.

### memo-ruler-passkey-131072-llama31-8b

One passkey retrieval at the source's 128K setting. Estimated mean reconstructed input 130,887.424 plus six generated tokens: **130,893.424 tokens** and **6.371559777089753e15 FLOPs**. Human time: **10 seconds**. Original AI result: 100% on 500 examples; the same human target and workflow apply. Attention matrices account for about 70.5% of central compute.

Both rows use `operation_count`, `derived_assumed_inputs`, and `compute_statistic=point_estimate`. The reconstructed sample is used to estimate a representative workload; it is not an observed attempt-level compute sample. AI subset/attempts are `not_applicable`. Human evidence is `assumed`, method `estimated`, statistic `point_estimate`, with subset/attempts `not_applicable`.

## Sources and reproduction

`source-manifest.json` in the source directory identifies retained originals, derived text and hash checks. The original paper is [RULER v3](https://arxiv.org/html/2404.06654v3). The [historical generator](https://github.com/NVIDIA/RULER/blob/dbc6a83c2f60d034dfaab8e7af42dde1a5d2e3dc/scripts/data/synthetic/niah.py) and [constants](https://github.com/NVIDIA/RULER/blob/dbc6a83c2f60d034dfaab8e7af42dde1a5d2e3dc/scripts/data/synthetic/constants.py) establish the work unit. The [Meta model card](https://github.com/meta-llama/llama-models/blob/main/models/llama3_1/MODEL_CARD.md) dates this model family to July 23, 2024. Configuration/tokenizer provenance is checked against Meta's original HF tree.

Install `tokenizers`. Run the calculator with explicit paths and a new output outside the retained sources:

```sh
python3 -B research/ruler/recompute.py --sources agent-work/sources/ruler --output /path/to/new-calculations.json
```

It reconstructs 1,000 prompts and counts operations without loading model weights, executing the original task scripts or calling an API. `calculations.json` includes the source hashes, architecture inputs, central components, alternative assumptions and per-example reconstruction audit.

These are additional, specifically documented RULER comparisons. They do not reconstruct the old 405B needle-in-a-novel lead; the model, text and available-document human workflow are explicit here.
