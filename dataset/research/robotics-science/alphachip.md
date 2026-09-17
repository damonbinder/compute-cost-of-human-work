**Disposition: unresolved compute for the proprietary TPU work unit. The hardware-duty scenario below is retained as rejected research context, not an active dataset candidate. The directly reconstructable public Ariane run has a separate ID and note, research/ariane.md.**

# AlphaChip: per-design optimization of one TPU floorplan

## sci-chip-floorplan-alphachip

Use the original [2021 Nature study](https://doi.org/10.1038/s41586-021-03544-w), available as the original publisher PDF on a [Cambridge course page](https://www.cl.cam.ac.uk/~ey204/teaching/ACS/R244_2021_2022/papers/Mirhoseini_NATURE_2021.pdf), saved at `agent-work/sources/robotics-science/alphachip-2021.pdf`. Extended Data Figure 5 identifies a real TPU block and compares the human and automated placements. The automated result has wirelength 55.42 m versus 57.07 m for the human layout, with six hours versus several weeks elapsed. Images are blurred, so exact netlist size and individual placements cannot be recovered from them.

The work unit starts from the pretrained placement policy and a new block netlist and ends with a comparable usable floorplan. It includes per-design PPO weight updates, rollout generation, and selection; it excludes the prior 48-hour, 20-block pretraining. Classify as additional_training, paired with human task_performance: here weight updates are the optimization method used to solve a particular design problem, not an attempt to teach the human a general profession. This distinction is explicit in the task description.

The selected wirelength comparison is evidence of comparable output, not a claim that all physical-design metrics improve. The paper also describes an eight-hour average production flow with extra simulated annealing and commercial placement operations. Its six-hour Figure 5 result is not a measure of a complete chip tapeout. We count the six-hour learned optimization run and an explicit helper allowance; do not charge eight hours of GPUs or silently call the subsecond zero-shot model the six-hour result.

### Human duration

Estimate **80 active expert hours**. Interpret 'several weeks' as a central three elapsed workweeks, then allocate two thirds of nominal 40-hour weeks to active design work. The rest permits unattended placement/routing jobs, queued feedback and other work. This gives 3×40×2/3 = 80 hours, or 288,000 seconds. The active fraction is an assumption, not reported time tracking. The substantive work includes reading connectivity and physical constraints, choosing macro groups and channels, several revisions after EDA feedback, and reconciling the final placement. It excludes chip architecture design, detailed routing and fabrication. At two to four elapsed weeks and 40–80% active effort, the range is 32–128 hours. This source-grounded duration is preferable to converting several weeks directly into continuous labor. Human attempts are unknown/not applicable to this constructed duration.

### Hardware and implementation investigation

The main text reports 16 workers for the fine-tuning results, each one NVIDIA Volta GPU plus ten CPUs. Extended Data Table 1 reports four PPO epochs, batch 64 per GPU, 32 actors per GPU and two episodes per rollout. The model uses 32-dimensional graph embeddings with repeated 65×32 edge transforms, plus five small deconvolutions with 16, 8, 4, 2 and 1 channels. This workload contains scatter/gather and small matrix operations, sequential policy collection and CPU placement/reward evaluation; it is not a sustained large-GEMM training job.

Inspect the source released after the study at [initial commit 633da7f](https://github.com/google-research/circuit_training/tree/633da7f), saved as `agent-work/sources/robotics-science/alphachip-model-2021.py`, `alphachip-observation-2021.py`, and `alphachip-train-2021.py`. It uses ordinary floating-point TensorFlow operations and explicit float32 feature casts; no mixed-precision policy appears in these paths. Its default graph width is 8 rather than the paper's 32, so we do not substitute its exact shapes into the original experiment. Current code also differs. These findings support ordinary FP32 throughput as the appropriate central hardware basis, not the 125-TFLOP FP16 Tensor Core peak. V100 predates TF32.

[NVIDIA's original V100 datasheet](https://images.nvidia.com/content/technologies/volta/pdf/tesla-volta-v100-datasheet-letter-fnl-web.pdf) gives 14 TFLOP/s for PCIe and 15.7 for SXM2/NVLink. The paper does not specify the board variant; assume SXM2 at 15.7 TFLOP/s. This changes the result by only 11% relative to PCIe.

### Central estimate and sensitivity

Assume effective useful arithmetic is **10% of ordinary FP32 peak over the six-hour allocation**. The explicit decomposition is 20% arithmetic utilization during active neural kernels × 50% average duty after collection, synchronization and CPU reward waits. Neither fraction is measured. The low matrix widths and data-dependent graph aggregation justify a considerable gap from dense peak; batch 64 and multiple actors make a near-zero-duty assumption inappropriate. A 5–20% effective range is appropriate for this reconstruction. No claim of a universal 10% coefficient is made.

GPU work = 16×6×3600×15.7e12×0.10 = 542,592,000,000,000,000 FLOPs.

Add **10%** for floating-point placement/reward, postprocessing and other associated CPU helper work: 54,259,200,000,000,000 FLOPs. This is an intentionally explicit approximate allowance, not ten CPUs times a fabricated CPU peak. Some helper search and bookkeeping is integer work and is not converted to FLOPs. Total = **596,851,200,000,000,000 FLOPs**.

The helper allowance corresponds to roughly 15.7 GFLOP/s averaged over each of 160 allocated CPUs across six hours, reasonable for scattered graph/geometry work rather than vectorized peak. Its purpose is to retain helpers despite no public implementation of the proprietary final EDA settings. The uncertainty is dominated by GPU duty: 5–20% plus the same proportional helper allowance gives 2.98e17–1.19e18 FLOPs. If the production postprocessing belonged outside the Figure 5 six-hour run, this allowance covers modest additional CPU work; it does not assert a measured full production total.

The [2022 correction](https://doi.org/10.1038/s41586-022-04657-6) adds the code repository. The [2024 addendum](https://doi.org/10.1038/s41586-024-08032-5) names the method AlphaChip; it is not evidence that the 2021 checkpoint was released on that date. Leave exact model release date blank. Graph positions are not language tokens, and no total-parameter estimate is needed for this hardware-time calculation.
