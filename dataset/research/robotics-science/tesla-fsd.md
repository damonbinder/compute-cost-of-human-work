**Disposition: unresolved compute. Retain the hardware ceiling and utilization scenarios below as research context; no active numeric row uses the proposed 40% duty. The human definition remains valid, with human_time_method work_rate.**

# Tesla HW3: one hour of supervised city driving

## robo-drive-fsd

The unit is one hour of FSD v12 city-driving assistance on the HW3 computer. This is not a claim of driverless operation. Tesla's [support description](https://www.tesla.com/support/fsd) requires an attentive supervising driver and explicitly distinguishes assistance from autonomy. The human baseline is an ordinary licensed driver manually performing the same one-hour trip, **3600 seconds**, a defined duration. Record below for independent driving capability, with different inputs/tools: FSD requires human backup and uses a multi-camera stack. Do not transfer current collision statistics to v12 or claim a measured intervention-free success rate.

### Original hardware evidence and numerical assumptions

Tesla's [Hot Chips 2019 original slides](https://old.hotchips.org/hc31/HC31_2.3_Tesla_Hotchips_ppt_Final_0817.pdf), saved at `agent-work/sources/robotics-science/tesla-hw3-2019.pdf`, describe the HW3 chip. Each chip has two independent 96×96 MAC arrays, a 2 GHz-plus design clock, twelve CPU cores and a GPU. The redundant vehicle computer uses two chips. Both computations count, even when producing redundant driving decisions.

The slides label approximately 80% utilization as a **design goal**, optimized for batch one; this is not a measured v12 utilization. For a bounded central estimate assume 80% useful array execution while neural work is running, and 50% active duty across the driving hour. Effective utilization is therefore 40%. Continuous camera processing makes substantial duty plausible, while sensor cadence, synchronization, memory movement, unaccelerated kernels and control margins make continuous peak implausible. The exact v12 model is undisclosed, so the utilization transfer is the major assumption.

Compute the algorithmic arithmetic capacity from the array, rather than silently relabeling advertised INT8 TOPS as measured FLOPs:

2 chips × 2 arrays/chip × 96×96 MACs/cycle × 2e9 cycles/s × 2 operations/MAC = 147.456e12 FLOP-equivalent operations/s at peak.

Charge 3600×0.4 of this capacity, plus **1%** for neural/helper arithmetic outside the MAC arrays (CPU/GPU postprocessing, geometry and control calculations): **214,460,006,400,000,000 algorithmic FLOP-equivalent operations**. The helper allowance is assumed; most board bandwidth, logging and control instructions are not floating-point AI work. Do not multiply every CPU or GPU peak by the whole hour as if all units ran dense inference continuously.

This follows the dataset's normal two-operations-per-neural-MAC convention even if the implementation uses quantized arithmetic. It is not a count of literal floating-point machine instructions. The original fixed chip architecture constrains the estimate; its 2019 model and throughput are not substituted as measured v12 workloads.

With 25–80% active duty at the same 80% array efficiency, effective utilization spans 20–64%, giving **1.07e17–3.43e17** including the 1% helper allowance. A lower actual clock or use of one chip for part of the stack would reduce the estimate. The row is a hardware-utilization estimate, not measured inference FLOPs.

### Additional investigation and identity

Tesla's [AI page](https://www.tesla.com/AI) describes per-camera networks and a collection of 48 networks, but does not identify this as the v12 graph. It therefore does not justify a 48-network multiplier. A later original engineering [statement by Ashok Elluswamy](https://x.com/aelluswamy/status/1826352855265194167), reproduced as an embedded post in reporting dated August 22, 2024, describes a smaller HW3 model and required compiler kernels for the larger model. Direct retrieval of that post was blocked. It is contextual evidence against substituting a HW4 model; no numerical count relies on it.

The evaluated v12 revision and its exact first public availability date are unresolved. The model identifies the v12-on-HW3 family; leave exact release blank. Public availability need not mean public weights. Token and parameter coefficients are not applicable to the hardware-time estimate.

## Further calibration investigation

A primary simulation study, [Odema et al., 2024](https://arxiv.org/html/2411.16007v1), reconstructs a Tesla-style HydraNet perception pipeline and reports accelerator utilization. This is a useful bounded alternative, but it is not the v12 end-to-end stack. It assumes eight camera feature extractors, spatial/temporal attention and perception heads. Transferring its total to v12 would also need planning/control work and a mapping to the deployed input cadence. Table II gives aggregate utilization for alternative chiplet schedules, but its latency labels and numerical scales differ across rows and its averages cannot be combined unambiguously with runtime to infer fixed operation counts. We do not treat 19.11% simulated PE utilization as measured v12 duty.

Public descriptions of v13's 36-Hz full-resolution HW4 inputs likewise do not establish v12-on-HW3's work per driving second. The hardware slides' approximately 80% figure is a design target. Adding a guessed active duty to that target is not sufficiently calibrated by continuous camera input alone. After these source and comparable-architecture checks, retain the original ID as unresolved actual workload, not excluded for quantized arithmetic. A reliable per-update graph/cost with cadence, or a reasonably transferable running-stack profile, could resolve it without exact logs.
