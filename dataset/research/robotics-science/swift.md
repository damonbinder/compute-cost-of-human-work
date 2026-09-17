# Swift: one racing lap, normalized from the fastest complete races

## robo-drone-swift

Primary source: [authors' published paper](https://rpg.ifi.uzh.ch/docs/Nature23_Kaufmann.pdf), especially Methods and Extended Data Table 1d. Original PDF, text extraction and a rendered table are preserved under agent-work/sources/.

The table reports fastest complete three-lap races: Swift 17.46 s; champions Vanover 17.96 s, Bitmatta 18.74 s and Schaepper 21.16 s. The work unit is one lap averaged within these selected races, including one-third of the starting overhead. Human active time = (17.96+18.74+21.16)/9 = **6.428888889 seconds**; three selected successful human race records contribute. Swift time per lap =17.46/3 =5.82 s. We do not present this as the fastest flying lap or as an average across every race. The robot is above on this selected race-speed comparison; the paper's broader description is champion-level. Humans and autonomous system used matched flight hardware with ballast replacing the autonomous computer/camera, but their perception/control interfaces differ.

## Neural computation

Two AI components are included, not merely the small racing policy:

1. Published policy 31→128→128→4: 2×(31×128+128²+128×4)=**41728 FLOPs/call**. Figure 2a explicitly reports a 100 Hz policy cadence.
2. Published gate detector: six-level U-Net, channels[8,16,16,16,16,16], kernels[3,3,3,5,7,7],384×384 grayscale input and final 12-filter layer. The paper does not fully specify skip/upsampling details; assume standard two-convolution levels, five 2×2 stride 2 transpose-convolution upsamplers, concatenated skip features, and a final 3×3 layer. Explicit convolutions in calculations.py total **2,222,014,464 FLOPs/call**. Figure 2a explicitly reports a 30 Hz detector cadence. Its separately reported 40 ms latency does not exactly equal the reciprocal call rate; the direct system diagram is stronger evidence for call cadence.

Total =5.82×(30×2,222,014,464 +100×41,728) = **387,988,011,110.4 FLOPs per normalized lap**. This is derived_assumed_inputs, not a hardware-time or measured-operations value. The conventional visual-inertial estimator and low-level motor control are outside AI-model FLOPs. No training or simulation is counted. Perception overwhelmingly dominates; alternative U-Net block topology or image cadence could change this estimate by roughly a factor of two. The observed per-pass GPU latency does not itself supply a FLOP count.

## Model release provenance

The paper does not release the evaluated system source/checkpoints (see Code availability). No exact evaluated-weights public release date is established, so the model release date remains blank.
