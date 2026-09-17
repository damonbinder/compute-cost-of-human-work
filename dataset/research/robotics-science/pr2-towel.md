# PR2: unfold and fold one unfamiliar towel

## robo-towel-pr2

Primary sources are the [original ICRA 2010 towel-folding paper](https://people.eecs.berkeley.edu/~pabbeel/papers/Maitin-ShepardCusumano-TownerLeiAbbeel_ICRA2010.pdf), especially Sections V–VI and Figure 5, and its cited [anisotropic Huber-L1 optical-flow algorithm](https://bmva-archive.org.uk/bmvc/2009/Papers/Paper260/Paper260.pdf), Equations 14–17 and Sections 4–5. The original towel PDF and extracted text are retained in `agent-work/sources/pr2-towel-2010.*`.

Work: pick up one initially crumpled, previously unseen rectangular towel from the prepared table, find adjacent corners, untwist/spread it, make the two prescribed folds and place it on the stack. Include the procedure's internal recovery attempts. The study completed all 50 single-towel trials, with mean elapsed robot time 1,478 seconds. The row concerns the whole physical manipulation, not just corner detection or the final folding motions.

## Floating-point workload

This is a classical geometric-vision policy. Its variational optical flow performs real-valued image optimization; lack of a neural network does not make its work an integer-search metric problem. Estimate those floating-point updates directly. Do not convert GPU peak capacity or robot elapsed time into measured FLOPs.

The source provides **1,966 stereo image pairs on which the algorithm ran across 50 towels** (Section V), or **39.32 processed frames per towel**. Use this directly recorded total. The initial reconstruction from rounded episode/frame averages, 1.56×6.9 + 1.50×16.9 = 36.114, remains a useful cross-check, but is less complete than the recorded image total. The paper does not reconcile that difference; do not silently force them to agree.

For optional stereo, Section VI-B reports 153 detection attempts, with one producing no detection: **152 selected detections / 50 = 3.04 per towel**. These are a lower bound on frames triggering stereo. Footnote 9 says later motion-planning checks reject many detections and pipelining normally captures another two or three images after the first accepted detection. Use **one selected-candidate frame + 2.5 pipelined frames + one earlier rejected-candidate frame per selected detection**. This gives **3.04×4.5 = 13.68 optional stereo computations per towel**. The pipeline allowance assumes the just-detected stable corner commonly remains visible in the following images. The rejected-candidate allowance assumes one such frame per accepted detection; the source establishes their presence but not their number. Neither allowance is an observed stereo-trigger count. Thus the central recipe has **39.32 + 13.68 = 53 solver computations per towel**.

A selected-only reference is 42.36 computations; varying the extra pipeline/rejection allowance from zero to six frames per selected detection gives 42.36–60.60 computations, about 11.30–16.16 trillion FLOPs under the same solver recipe. This grounds the optional work in detections rather than assuming that half of every processed frame needs stereo.

Retain a separate implementation uncertainty: the paper's named computation unit may bundle forward/backward flow needed for confidence. Use its one baseline plus optional stereo unit centrally; do not add an automatic second directional pass. Up to a twofold change remains a sensitivity if the named unit bundles two full directional solver invocations. This revision does not resolve that ambiguity.

The foreground crop is limited to 2 megapixels. Use 2M processed pixels as the representative large-towel crop; this is a cap transferred into an assumed typical workload, not a measured mean crop. Transfer the original solver's high-accuracy configuration: ten warps, fifty iterations per warp and a pyramid scale factor of 0.8 in each spatial dimension. The total pyramid area is approximated by 2M/(1−0.8²). Finite small pyramid levels make a negligible difference to this sum.

Approximate each pixel iteration as 80 arithmetic operations, grounded in Equations 14–17. For each of two flow components, the primal update requires a two-by-two matrix/vector product, divergence and scaled addition (about 11 operations); the dual update requires gradient, another matrix/vector product, scaled vector updates and normalization (about 22). The auxiliary threshold update adds roughly ten shared operations. Rounding their sum, approximately 76, to 80 accommodates branch and boundary variation. Count ordinary scalar division and square root as one arithmetic operation, not as a GPU cycle count. Comparisons and memory accesses are not counted as floating-point arithmetic.

One solver computation is therefore approximately **2M/(1−0.8²) × 10 × 50 × 80 = 222,222,222,222 FLOPs**. Add 20% for pyramid preparation, warping, ROF preprocessing, border/corner/plane calculations and other visual checks during folding. The main optimization makes 500 pixel sweeps; the allowance represents another hundred comparable sweeps across all preprocessing and helper stages. It is an explicit aggregate approximation rather than an observed helper profile.

**Total = 53 × 222,222,222,222 × 1.2 ≈ 14,133,333,333,333 FLOPs per towel.** Use exact rational arithmetic before the displayed rounding. The native 5-second solver throughput gives about 44 GFLOPs/s for the estimated main kernel workload, a plausible achieved rate for the memory-intensive GTX 295 implementation. This is a sanity check, not the derivation.

Material sensitivities are actual crop area, solver settings transferred from the cited implementation, and the detection-based optional stereo allowance. A factor-of-three range is more meaningful than the many digits retained for reproducibility. Mechanical motor commands and trajectory bookkeeping are excluded; floating-point visual helpers are covered by the allowance. Internal manipulation retries are included through the full recorded image total and detection counts, so no success-rate multiplier is added.

## Human time and quality

Estimate **20 active seconds** for an ordinary adult at the same prepared table to produce a comparably folded towel: two seconds to pick it up, five to locate adjacent corners and open/untwist it, five to align/spread it, six for the two folds, and two to place the result on a nearby stack. This is not an already-flat-towel estimate. A 12–35-second range covers towel size, initial crumpling and alignment care. The target is the visibly serviceable folded stack shown by the study, not retail-perfect presentation.

Classify match for that comparable-quality target, supported by completion of all 50 robot trials. The assumed human duration is not a timed participant mean and does not assert zero human failures. Hands versus parallel grippers are the material tool difference. The computation is a reconstructed mean-workload recipe with assumed components, so point_estimate and not_applicable attempt/statistical-subset fields are used consistently with the other analytical robot recipes.

## Model record

Identify the complete PR2 geometric towel-folding policy with its Huber-L1 vision solver. Parameter and token fields are not_applicable. The paper's publication date does not establish when this exact integrated robot software became publicly available; leave its model release date blank.
