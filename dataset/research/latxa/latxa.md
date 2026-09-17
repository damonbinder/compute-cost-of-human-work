# Latxa v1.1: learning the EusProficiency contrasts

This reconstruction uses the original Latxa v1.1 training configuration and released evaluation records. It does not reuse the earlier dataset's human-time estimate. The [human-learning record](human-learning/latxa-human-learning.md) explains the independently reviewed estimates: 500 active hours to the 13B endpoint and 1,000 hours to the 70B endpoint. These are assumed focused-learning routes, not measured score-to-hours curves.

## Target and model versions

The [original paper](https://arxiv.org/html/2403.20266v1) reports continued pretraining of Llama 2 on Basque and some English. Use v1.1, corresponding to that paper's enlarged corpus, rather than the earlier v1 or later v1.2 correction. The [author repository](https://github.com/hitz-zentroa/latxa/tree/7eccd872eb515104ee6e2f721c1f56fc63647a54) supplies the retained launch scripts, model/base/hyperparameter configurations and native results.

| Model | Original Llama 2 score | Latxa v1.1 score |
|---|---:|---:|
| 13B | 25.9044% | 45.0184% |
| 70B | 24.1633% | 60.6113% |

These are five-shot four-option accuracy on the 5,169 released [EusProficiency questions](https://huggingface.co/datasets/HiTZ/EusProficiency), not general Basque proficiency percentages. A random chooser averages 25%. The roughly 60% endpoint belongs to 70B, not 13B. The human task starts near guessing and targets the corresponding final accuracy. The model's small deviation from chance does not establish an observed novice-human proficiency difference.

The questions come from the EGA atarikoa preliminary exam. They include idioms, word meanings, pragmatic replies, morphosyntax and paraphrase. Passing or partially answering this written multiple-choice component is distinct from earning a full qualification with writing, listening and speaking. The human estimate should cover learning the tested distinctions, not all of the model's earlier general pretraining or all Basque skills.

## Compute

Each launch uses 256 sequences per global update, 4,096 positions per sequence and 10,000 updates: **10,485,760,000 training positions**. The paper's 10B is rounded. These are processed positions from the configured run, not the distinct corpus size.

For 13B, 16 nodes × 4 GPUs, tensor parallelism 2, microbatch 8 and accumulation 1 give 32 data replicas × 8 = 256. For 70B, 64 nodes × 4 GPUs, tensor parallelism 4, pipeline parallelism 8, microbatch 8 and accumulation 4 give 8 replicas × 8 × 4 = 256. Native evaluation paths identify global_step10000. No model weights were downloaded.

The public configuration gives 13,015,864,320 and 68,976,648,192 unique parameters. The calculation uses actual projection dimensions, grouped-query attention for 70B, SwiGLU and untied vocabulary heads. Input embeddings are lookups, not a dense multiplication. Matrix multiplication counts a multiply and add as two FLOPs.

Both base configurations explicitly enable activation checkpointing for each transformer block. Three forward-equivalents approximate ordinary forward/backward work; an additional transformer-block forward charges recomputation. The output vocabulary head is not a checkpointed block. The configured FlashAttention receives causal-triangular attention accounting, with one additional QK rematerialization in backward. A small 14-operations-per-parameter-per-update optimizer allowance is explicit. This remains dominant-operation accounting, not measured hardware telemetry or a count of every scalar kernel.

The exact installed GPT-NeoX commit is unreported. The retained [February 8, 2024 implementation](https://github.com/EleutherAI/gpt-neox/tree/f7373f806689cb270677dd48bffddf4a32bfadce) is a contemporaneous proxy. Its code identifies checkpointed transformer blocks, linear checkpoint scheduling, validation iteration behavior and forward verification when saving checkpoints. The implementation transfer is an assumption, not an assertion that this commit was used.

The 13B configuration validates every 100 updates, while 70B validates every 10; each validation iteration processes one global batch. Add final validation and test: 102 and 1,002 batches. The ten validation data paths are blended into one dataset, not ten separate evaluations at each check. The 13B configuration additionally performs forward verification when saving checkpoints; 99 scheduled saves plus the final save give 100 checks. The 70B configuration disables that verification. Unlogged training interruptions or duplicated work are not recovered; an extra restart-check scenario is retained.

The final target assessment uses the actual 5,169 question texts, the released tokenizer and the native five-shot prompt format. Exact historical few-shot identities are not available. A seeded reconstruction chooses five other examples for each question; four answer likelihood evaluations are charged centrally, with shared-prefix reuse as an alternative. Thus prompt positions are reconstructed, not reported API tokens. Final scoring centrally assumes triangular attention as well; the training FlashAttention setting does not prove the later HF inference kernel. A dense final-assessment scenario isolates this small uncertainty (the entire assessment is about 0.026% of total compute). The native result's harness hash 75a76af could not be resolved in the public upstream repository; the calculation does not claim an exact replay of that implementation. Other unrelated benchmark assessments in the paper are outside this defined learning target.

| Model | Training FLOPs | Validation and save-check FLOPs | Final target assessment | Total FLOPs, including optimizer |
|---|---:|---:|---:|---:|
| 13B | 1.15382e21 | 5.79971e18 | 3.02121e17 | 1.159923e21 |
| 70B | 6.01197e21 | 1.50032e20 | 1.60943e18 | 6.163623e21 |

The calculation retains no-checkpointing, dense-attention, omitted/doubled-validation and shared-prefix alternatives. These are sensitivity scenarios, not confidence intervals. Human estimates and model coefficient assumptions need separate assessment; numerical replay alone does not validate them.

## Release dates

The original HF public histories distinguish repository creation from actual complete weights. The 13B [February 16 commit](https://huggingface.co/HiTZ/latxa-13b-v1.1/tree/5446f63e3363933d065cedaac3b4be27225035dd) contains all three shards and tokenizer files. For 70B, the February 16 commit titled “add model and tokenizer” contains only README and .gitattributes; the [February 17 commit](https://huggingface.co/HiTZ/latxa-70b-v1.1/tree/d9551039ba79298e8ca1849860667a972127cc49) contains all fifteen shards and tokenizer files. Use **2024-02-16** and **2024-02-17** as the best available release-date estimates from complete artifacts. Historical repository visibility was not independently verified. The January announcement concerns v1; the March paper is not the release date.

## Replay

`recompute.py --sources SOURCE_DIR --output NEW_JSON` needs sentencepiece and does not run a model. The output must be new and outside sources. `calculations.json` retains source hashes, prompt-length counts, architecture arithmetic, endpoint scores and scenarios. Source configuration files preserve their original JSON-with-comments syntax; the reader strips comments and trailing commas only.
