# Waymo fifth-generation driving: unresolved compute basis

## robo-drive-waymo

The intended work is one hour of city driving by the fifth-generation Waymo Driver. Human time would be the defined 3600 seconds of driving; the reason for this disposition is the aggregate compute basis, not human duration or neural quantization.

Original sources inspected:

- [2020 fifth-generation introduction](https://waymo.com/blog/2020/03/introducing-5th-generation-waymo-driver/) and [design account](https://waymo.com/blog/2020/03/designing-5th-generation-waymo-driver/): establish the integrated sensors and onboard compute, without naming compute components or neural architecture dimensions.
- [2024 sixth-generation introduction](https://waymo.com/blog/2024/08/meet-the-6th-generation-waymo-driver/): establishes that the later generation is a different sensor/hardware system. Its reduced camera count cannot be assigned to the fifth generation.
- [2026 original compute-team account](https://community.waymo.com/blog/2026/08/look-under-our-trunk/): identifies a heterogeneous redundant system, a new custom 5nm front-end ASIC subsystem exceeding 1000 TOPS, and 20-fold raw compute growth over eight years. The ASIC subsystem is only one part of the latest system, before the core ML processing, and is not identified as fifth-generation hardware.
- [Compute lead Daniel Rosenband's GTC 2026 talk](https://www.nvidia.com/en-us/on-demand/session/gtc26-s82484/): an additional primary lead. Search indexing exposes introductory transcript and a fifth-generation camera-count reference; the directly retrieved page did not expose the full talk or a fifth-generation numerical workload.

Bounded alternative estimates were considered. Multiplying the 2026 subsystem capacity by an arbitrary utilization would estimate a newer front-end only, leaving both the fifth-generation transfer and core inference unresolved. Dividing its capacity by 20 also fails: the growth statement concerns the full system over eight years, not a fifth-generation-to-latest ratio for the same subsystem. Counting camera images and borrowing a ResNet would provide one vision component, but no source identifies its fraction of the deployed driver or the lidar/radar, fusion, prediction, planning and redundant workload. Relative sensor count is not a defensible full-system multiplier from Tesla's camera-only computer.

Quantized neural MACs are eligible for the dataset's usual algorithmic two-operations-per-MAC estimate. This is **not** a metric exclusion based on INT8 or a demand for exact execution logs. In contrast to HW3, the public sources inspected do not establish even a model-specific aggregate hardware capacity or a reasoned workload basis; capacity alone would still not establish actual work. In contrast to ARMBench, they do not provide a deployed-component workload or closely scoped set of pipeline baselines from which to reconstruct the total. An invented platform specification plus an assumed utilization plus a generation transfer would dominate the number.

Disposition: `unresolved_compute`, retaining the ID and these original source leads. Reopen if a fifth-generation compute bill of materials, aggregate throughput with clear precision/convention, representative model graph, or measured component allocation becomes available. No numeric candidate is created and no zero compute is implied.
