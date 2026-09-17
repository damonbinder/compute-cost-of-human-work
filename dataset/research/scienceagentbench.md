# ScienceAgentBench

Three candidate comparisons from the April 21, 2025 HAL evaluation of o3-2025-04-16 with medium reasoning and self-debug. Each describes one executed scientific-analysis program. Human time estimates an expert producing equivalent work unaided from the same prepared inputs; it does not estimate doing the underlying research study or collecting its data.

## Evidence and scope

- [Original benchmark paper](https://arxiv.org/html/2410.05080v3), §§2–4: benchmark design, program evaluation and annotation-time context. First preprint October 2024; ICLR 2025.
- [Recorded run](https://huggingface.co/datasets/agent-evals/hal_traces/resolve/main/scienceagentbench_sab_selfdebug_o3_medium_1745186112_UPLOAD.zip). Retained selected task records are in `scienceagentbench-inputs.json`: configuration, original prompts and responses, native usage, assessment feedback, cost and response identities. The encrypted original's SHA256 is retained. HAL's public trace-reader is documented in its [README](https://github.com/princeton-pli/hal-harness), with public decryption code in `hal/utils/decrypt.py`.
- Run implementation: [commit eb094b928198c6e1029a8e0c247576c78a1fe9f7](https://github.com/OSU-NLP-Group/hal-harness/tree/eb094b928198c6e1029a8e0c247576c78a1fe9f7). Retained `scienceagentbench-harness-main.py` and `scienceagentbench-harness-agent.py` show automatic execution and error feedback. Despite a prompt referring to a user executing programs, no human debugger intervenes.
- [Task annotation sheet](https://huggingface.co/datasets/osunlp/ScienceAgentBench/blob/main/ScienceAgentBench.csv). Selected annotations are retained as supplementary context; the recorded 2025 prompts define the actual inputs, not a later annotation version.

I read all three generated programs and original task prompts, plus all nine visual-grader explanations. I did not view original plots. Historical and current official benchmark-artifact SharePoint links were inaccessible (the current link redirects to organizational login). The trace includes grading text but not original image files. No synthetic plot is substituted. These candidates have therefore had code and source-result inspection, not independent visual verification.

The source's three plot comparisons are performed by a model and can miss scientific errors. Their average passed the source threshold; this establishes the source's result, not a validated scientific finding. In particular, task 83 has only moderate agreement with the reference temperature surface. Human estimates target each submitted program's actual level of analysis and reported output quality. `match` is by construction, not a claim that an observed human completed it in our estimated time.

## Workload calculation

Native events contain both an OpenAI call and a LiteLLM wrapper for the same response. Deduplicate by response ID. Across the entire archive this changes 920,682 prompt / 1,230,834 completion tokens to 460,341 / 615,417; the selected rows use only their own unique response counters. Output counters already include hidden reasoning. All selected calls report zero cached tokens. No additional tool or helper model is invoked by the agent loop. External visual grading is outside the task.

For each unique call, P = prompt + completion and the causal attended-position sum is P(P+1)/2. Sum these across calls, including the failed initial attempt and corrective call for task 84. Mean context = total attended-position sum / total P. This uses actual per-call lengths rather than treating several calls as a single growing sequence. Attention over hidden reasoning is counted; the server's internal reasoning processing is otherwise assumed to follow this ordinary causal recipe.

The current released o3 registry prior is 50 billion active parameters, 41 attention layers, width 8,064. FLOPs = 2NP + 4LWA. Lower and upper bounds use N = 20B / 100B and the documented OpenAI family shape rule: dense = (N/196608)^(1/3), L = 0.65 dense, W = 128 dense. Per-call context stays fixed. These are parameter-prior bounds only. PCA, UMAP, interpolation and raster arithmetic are conventional scientific computations, not additional neural model training; the stated neural-compute accounting adds no transformer-model work for them. No image input is sent to o3.

`scienceagentbench-calculate.py` rebuilds the exact CSV with explicit input, header and output paths, using Python's standard library. The embedded model snapshot prevents silent changes in registry priors. The per-task costs are the source's recorded amounts, not the doubled logging aggregate or the repriced modern leaderboard: $0.06974, $0.09111 and $0.21089. They reproduce the trace-period $10/M input and $40/M output rates, with no cache reads. They are source-reported API estimates, not evidence of an invoice.

## Human-time approach

The paper says adapting existing programs required roughly 2.5–3 hours per task on average. That is context only: no timed donor attempts or measured rate enters these estimates. Our examples have a prepared input path/schema and modest deliverables; they should not inherit three hours indiscriminately. I estimated active work from the actual submitted operations, allowing an expert to use ordinary documentation and Python packages, but no AI or reference solution. Waiting for numerical routines to finish is excluded. The short component budgets below are explicit judgments, not observations. They include writing, running, checking and saving a program, not just typing its final lines. There is no claim that the human must use identical code or produce a pixel-identical stochastic embedding.

### research-sab-heart-cell-umap-o3

Task 69: one call, 530 input + 1,611 completion = 2,141 tokens; 832 reasoning tokens are already in completion. Submitted program is retained in `scienceagentbench-69-submitted.py`.

The actual sequence reads the supplied AnnData file, filters genes detected in fewer than three cells, normalizes to 10,000 counts, log-transforms, selects 2,000 variable genes, scales, computes 30 PCs, 15-neighbor graph and UMAP, then plots the existing cell-type annotation. No cell-type classifier or novel biological interpretation is performed. The original task's reference tutorial is `scverse/scvi-tutorials/quick_start/api_overview.ipynb`, but the submitted program uses Scanpy's standard workflow rather than training scVI.

**Human estimate: 1 hour.** Approximately 10 minutes inspecting AnnData fields and count conventions, 20 implementing the standard analysis sequence, 20 running and checking filtering/embedding/label choice, and 10 formatting and saving the plot. This is a routine task for an expert already familiar with single-cell Python tools. The bounds run the same budget without a debugging round, 10, 20, 10 and 10 minutes, 50 minutes, against the paper's own 2.5–3 hour per-task average for adapting existing programs, taken at 3 hours, which a task this routine should not exceed. Neither is a statistical interval. Data collection, cell annotation and interpretation of the heart atlas are excluded.

The source's visual scores are 75/90/85. Feedback reports recognizable cell-type structure but different cluster positions and a doublet label absent from the reference. This fits an executable exploratory plot, not biological validation. The human target is that level of work.

### research-sab-urban-heat-o3

Task 83: one call, 815 input + 2,074 completion = 2,889 tokens; 896 reasoning tokens included. Program retained in `scienceagentbench-83-submitted.py`.

The prompt supplies temperature points, a preview including `TemperatureF`, and census polygon columns including `OBJECTID` and elderly density. The program harmonizes coordinate systems, fits linear-variogram OrdinaryKriging on a 200×200 grid, spatially joins interpolated grid points to blocks, averages within each block and highlights the highest quartile of elderly density. It does not fit alternative variograms, cross-validate interpolation or produce a public-health report.

**Human estimate: 2 hours.** Approximately 20 minutes checking coordinates/attributes, 35 implementing and running interpolation, 35 doing the polygon aggregation and elderly-density overlay, and 30 inspecting and exporting the result. The main effort beyond a stock interpolation example is maintaining consistent geometry and grouping through the spatial join. The bounds run the same budget with the spatial join going cleanly, 20, 25, 30 and 20 minutes, 95 minutes, against the paper's own 2.5–3 hour per-task average, taken at 3 hours. Waiting for grid computation is excluded from both.

The three visual scores are all 60. Feedback says the result's temperature range is lower and narrower than the reference, with different highlighted areas. The matched target is an exploratory map of this imperfect quality, not a scientifically validated temperature exposure analysis. Source evaluation success is not treated as exact numerical agreement.

### research-sab-burn-scar-o3

Task 84: two calls, total 3,069 input + 4,505 completion = 7,574 tokens; 1,664 reasoning tokens included. Program retained in `scienceagentbench-84-submitted.py`.

The initial program failed because the output directory was created after an earlier write operation; the automatic harness supplied the error, and the second response created the directory before writing. Both calls are counted. The final code reads aligned pre/post rasters, chooses bands heuristically, computes NBR and its difference, thresholds at 0.27, extracts polygons and renders the map. The implementation's `min_pixels` filter actually compares coordinate area, and its Sentinel-specific band branch is shadowed by an earlier condition. These are flaws in generality/scientific handling, not missing collection effort. The map passes the source evaluator, whose feedback describes matching burn shapes but less labeling than the reference. We do not assert the heuristics would work on arbitrary sensor data or validate exact burned area.

**Human estimate: 1.5 hours.** Approximately 15 minutes inspecting raster layout/alignment, 25 implementing NBR change and thresholding, 25 polygon extraction and map/export code, and 25 running/debugging and checking output. This targets an exploratory image-processing script on supplied aligned rasters, not selecting imagery, atmospheric correction, field validation or publishing a fire-impact study. The bounds run the same budget with no band-selection or output-path trouble, 15, 20, 20 and 15 minutes, 70 minutes, against the paper's own 2.5–3 hour per-task average, taken at 3 hours.

Visual scores are 85/90/90. Matched human quality includes the limited labels and heuristic processing rather than silently pricing a fully validated remote-sensing analysis.
