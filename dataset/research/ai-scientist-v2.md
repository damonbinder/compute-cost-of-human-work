# AI Scientist-v2: compositional regularization

## research-ai-scientist-v2-compositional

Compute is a reconstruction from the actual kind of experiment and the published harness, not recovered usage. Human time is a judgment about reproducing the delivered investigation from its supplied idea.

## Work and original evidence

The [technical report](https://arxiv.org/html/2504.08066v1), §4.2 and Appendix A, identifies Claude 3.5 Sonnet v2 for code and GPT-4o for feedback, with allocations of 21/12/12/12 experiment nodes. These are allocations, not recorded counts. Humans selected ideas and manuscripts across seeds; the individual experiment/writeup runs were autonomous. We count one selected run, not the cost of searching until an acceptable paper appeared.

The [actual annotated manuscript](https://github.com/SakanaAI/AI-Scientist-ICLR2025-Workshop-Experiment/blob/master/compositional-regularization/annotated_paper.pdf) was downloaded and read. It contains a four-page main paper, references and appendices with nine numbered figures. It tests a temporal-embedding penalty on small recurrent models trained on synthetic arithmetic, with architecture and regularization sweeps. Appendix D supplies 64 hidden units, embeddings 16–128, batch 32 and nominally 30 epochs; annotations correct some reported settings and flag train/test overlap and misleading captions. The central target is this limited negative-result investigation, not a convincing demonstration of compositional generalization.

The [announcement](https://sakana.ai/ai-scientist-first-publication/) reports workshop scores 6/7/6. Withdrawal under the prearranged protocol means this is an acceptance-worthy submission, not a published conference paper.

## Compute reconstruction

The code was inspected at original commit [f85bb03](https://github.com/SakanaAI/AI-Scientist-v2/tree/f85bb03). `parallel_agent.py` establishes the call families; `launch_scientist_bfts.py` names the writing helpers; `backend_anthropic.py` sends ordinary Bedrock requests without cache controls. The release configuration differs from Appendix A, so the paper's 57-node allocation takes precedence. Using 57 as the actual count is an explicit estimate: the artifact reaches sweeps and ablations, but its node ledger is unavailable. Smaller realized counts would reduce compute.

All assumed call counts and token lengths are in `research/ai-scientist-v2-workload.json`. They are the central reconstruction, not measurements. `research/ai-scientist-v2-calculate.py` accepts explicit input/output paths and uses Python's standard library. Pass the workload file to `--workload`, the dataset's models.csv to `--models`, and a new JSON output path to `--output`. Derived results are retained outside the product in agent-work/derived/ai-scientist-v2-20260915/.

| Component | Central assumption and rationale |
|---|---|
| Experiment generation | 57 calls, each 9,000 input + 3,000 output tokens. A complete small PyTorch program plus plan is regenerated, rather than a patch. Input includes earlier code, idea, instructions and accumulated summaries. |
| Metric parsing | 48 calls, 4,000 + 1,000 tokens: original program plus a short extraction program. |
| Plotting | 48 calls, 7,000 + 2,000 tokens: experiment code, metrics and plot instructions; failed nodes do not produce this stage. |
| Experiment proposals | 24 calls, 10,000 + 500 tokens, for the two 12-node tuning/ablation stages. |
| Valid nodes | 48/57 assumed, not observed. The simple task and completed sequence of ablations motivate a predominantly working search, with nine unsuccessful nodes. |
| Seed evaluation | Twelve additional feedback-only nodes: three seeds across four stages. These reuse experiment/plot/metric code. |
| GPT-4o helpers | Execution checks, metric parsing, plot review, summaries and stage management, with separate counts in JSON. Their prompts contain subsets of the same code and results. |
| Writing | Six o1-preview calls: initial draft, three reflections, figure-selection revision and final revision in the released writer. Gross input grows across six history-preserving calls (15k, 23k, 32k, 41k, 50k, 59k); 12,000 output tokens/call includes an assumed 6,000 reasoning tokens alongside a 6,000-token manuscript. Hidden reasoning is not observed. |
| Citations and final reviews | Twenty GPT-4o citation rounds, eight text/figure reviews, and three o3-mini plot-aggregation calls. Initial launcher defaults determine these helper-model assumptions. |
| Additional calls | 10% over the table, a workload scenario for formatting failures, plot retries and other small calls, not observed retries. |

The prompt lengths are judgments informed by the source's prompt composition and this deliverable's small program and manuscript. They were not tokenized from an original run: no original run transcript is available. Node counts, valid-node fraction, helper lengths and hidden reasoning are the dominant uncertainty. The published implementation makes the estimate more constrained than assigning a typical benchmark bill, but does not make these quantities measured.

The Anthropic route lacks cache controls, so its full input takes a weights pass. OpenAI caching is default-on: GPT-4o helpers and o3-mini plot aggregation subtract an assumed 1,024-token repeated prefix per call, representing recurring instructions and idea context before node-specific content. Metric-interpretation calls have only 1,000 total input tokens, below the cache minimum, so none of their input is cached. The o1 writer preserves history; passes 2–6 subtract 90% of the previous pass input as cache reads (13,500 / 20,700 / 28,800 / 36,900 / 45,000 tokens). The 90% allows prefix mismatch and cache expiration; neither cache share is measured. Processed tokens exclude these reads. Attention retains the prefix: Q = cached + (fresh input + output + visual positions + 1)/2, then a position-weighted mean for the primary-model field. This is a direct call reconstruction, not the cache-implied 2,800-token route.

Visual reviews assume three images per relevant call, each represented by a 24 × 24 grid (576 positions) after resizing to 336 pixels with 14-pixel patches, plus 381 billion encoder FLOPs per image (24 layers, width 1024, MLP width 4096, 577 positions including CLS; full self-attention). The grid follows the open CLIP ViT-L/14-336 architecture as an explicit proxy, not a disclosure of GPT-4o architecture or a conversion of billing tokens. A 12 × 12 to 48 × 48 grid is an appropriate sensitivity scenario. These image positions stay out of `tokens`. Proxy architecture: https://huggingface.co/openai/clip-vit-large-patch14-336/blob/main/config.json. This is an approximate closed-model image calculation; it is a small part of total compute. Neither an image token count nor encoder architecture was reported for these runs.

Experimental models are included: 200 fits (roughly three per allocated node plus reruns), each on 1,000 examples for 30 epochs, sequence length five, with a 64-wide embedding and 64-unit LSTM. Training gate-matrix work is `fits * examples * epochs * length * 3 * (8*h*(d+h) + 2*h)`; add a 200-example evaluation pass per epoch. This yields 6.30e12 FLOPs. It approximates RNN/attention variants by the LSTM. Even multiplying these fits by 100 leaves this term around 0.1% of the total, so deriving a precise hidden sweep count would not improve the plotted estimate materially. GPU elapsed time is not substituted for arithmetic.

Central total: **5.70e17 FLOPs**, with **3,459,535.2 estimated fresh text tokens** across all models. The CSV model-only sensitivity range is 2.89e17–1.34e18; it excludes workload and human uncertainty, as required by COLUMNS.md. Source input assumptions remain fixed while shared model parameter/shape priors move. Primary model is the existing `claude-3-5-sonnet-20241022`; other existing registry models supply their own coefficients. No new model records are needed.

Workload scenarios: halving or doubling all estimated call workloads changes total FLOPs approximately twofold; changing both calls and average sequence lengths together can exceed that. These are scenarios, not confidence bounds. A reasonable order-of-magnitude interpretation is several times 1e17, not six significant figures of measured precision.

The official [README FAQ](https://github.com/SakanaAI/AI-Scientist-v2#frequently-asked-questions) describes typical experiment API costs of $15–20 and writing around $5. This is a cross-check only, not this paper's expenditure. The reconstructed call workload is on the same rough spending scale under the period's common tariffs. It is not used as a numerator or recorded in `ai_cost_usd`.

## Human-time estimate

**40 active hours**, with a 16–80-hour judgment scenario, for an ML researcher familiar with PyTorch and recurrent models. The researcher receives the idea and related-work leads, not the final answer or experimental code; they produce a similarly limited study and manuscript without an AI assistant. Waiting for small fits is not charged as active work. The final author's red review annotations are not part of the deliverable to reproduce.

The central allocation is six hours checking the limited related work and planning, ten building/debugging the synthetic-task pipeline, twelve conducting and inspecting sweeps/ablations, four making figures and interpreting results, and eight drafting/revising the paper and appendix. This is a judgment breakdown, not five measurements. The small synthetic dataset and standard architectures keep implementation modest; the number of figures, experiment variants and complete writeup keep it above a one-day coding task. A researcher with reusable scripts might take two days; an unfamiliar expert who explores unproductive variants could take two weeks.

We are not estimating the time to fix every flaw or to make the work publishable at a main conference. Nor do we count discovering the supplied research idea, generating other candidate papers, obtaining peer reviews or acquiring ML expertise. `human_time_evidence=llm_estimate_judgment`; no human attempt sample exists. `performance_vs_human=match` follows from targeting this actual output's quality, not from treating a workshop rating as a timed human baseline.
