# Dex-Net 2.0: grasping one unfamiliar tabletop object

## robo-grasp-dexnet

Use the exact [March 2017 v 1 paper](https://arxiv.org/html/1703.09312v1), rather than silently mixing later revisions. Table IV evaluates 50 trials across 10 unfamiliar household/office objects: the GQ network trained on all Dex-Net 2.0 achieved 80% success (40/50). The criterion is more than touching or briefly lifting: retain the object while lifting, moving it sideways and shaking. A correct-object selection task or multi-object bin-picking cycle is not included. The physical sample constrained object weight below 250 g and height above 1 cm.

## Compute

Appendix B sets the candidate-generation target M=1000; one GQ-CNN evaluation ranks each candidate. We approximate 1000 candidates, acknowledging height discretization/rejection can alter the exact count. Figure 4 gives 32×32 depth input, four 64-channel convolutions with kernels 7,5,3,3, one 2×2 maxpool between the second and third convolution, image FC1024, height branch FC16, joined FC1024, and 2-way output. SAME padding is inferred from the reported approximately 18 million parameters: 16×16×64→1024 alone uses 16.8 million. Valid convolutions would be inconsistent with that total.

Count all convolutional matrix work plus dense layers, multiply+add separately:

2×[32²×1×64×7² +32²×64²×5² +2×16²×64²×3² +16384×1024 +1×16 +(1024+16)×1024 +1024×2].

The exact value is in calculations.json. Multiply by 1000 for the one-attempt neural workload. Preprocessing, candidate geometry and conventional robot control are not separate AI models. This is a supported architecture-based approximation with an assumed exact candidate count, not the invalid approximation 2×18M once per entire grasp. Published 0.8 s is planning latency, not robot cycle duration, and is not used for either human time or FLOP conversion.

## Human work estimate

Estimate **5 seconds active time** for an ordinary adult facing one of these small tabletop objects, required to satisfy the same lift/move/shake criterion: inspect and choose grip 0.5 s, reach 1 s, close 0.5 s, lift 0.5 s, move 1 s, controlled shake/retention check 1.5 s. This is an explicit motor-work assumption based on the inspected benchmark actions, not a measured ergonomic time. It excludes object setup/reset and any prior learning. Human hands and robot parallel jaws differ materially. For these lightweight common objects an ordinary adult is expected to complete the operation reliably; AI 40/50 indicates a noticeable deficit, so below is preferable to asserting parity from an estimated time. No invented human success count is supplied. A 3–8 s active range represents placement and caution variability.

## Model release provenance

The authors announced pretrained GQ-CNN models from the paper on [27 June 2017](https://bair.berkeley.edu/blog/2017/06/27/dexnet-2.0/). This establishes public availability of the paper model family, but the announcement does not identify an immutable checkpoint for the exact March v1 physical evaluation. Keep the exact evaluated-model release date blank rather than equating the later family release with that checkpoint.
