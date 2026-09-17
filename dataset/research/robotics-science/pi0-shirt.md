# pi0: fold one already-flat shirt

## robo-shirt-pi0

Primary source: [original pi0 paper](https://arxiv.org/html/2410.24164v1), Figures 5–7 and Appendices B, D and E. Original PDF/text retained as `agent-work/sources/pi0-v1.*`. Figure 7 was visually inspected on PDF page 7. Select the full 700k-step base model, evaluated without task-specific post-training on Bi-ARX. It succeeds on all ten shirt trials (four small shirts and one medium shirt, twice each). The task starts with a flat shirt and ends after folding both sleeves inward and making one half-fold along its length. Do not substitute complex laundry retrieval from a crumpled bin.

## Completion duration and human work

The 15,000-step/five-minute evaluation limit is not a completion-time measurement. Estimate **40 seconds of robot execution** for the three folds: roughly eight seconds per fold for approach, grasp, transport and release, plus sixteen seconds of alignment, regrasping and settling across the sequence. The figure shows repeated bimanual manipulation, not one atomic fold action. A 25–75-second range is appropriate; compute scales linearly with this substantial duration assumption. This is a completed-task recipe, not an observed mean. It excludes work before the timed flat-shirt state and retries of entire trials.

Estimate **15 active human seconds** for an ordinary adult at the same prepared table: three seconds to align the flat shirt, three seconds per sleeve fold, four seconds for the lengthwise half-fold and two seconds to smooth/check the result. A ten-to-twenty-five-second range allows for garment size and care. Match targets the serviceable three-fold output shown by the study; no human-perfect-completion claim is inferred from selecting completed work. Hands and robot parallel grippers differ.

## Separate component accounting

Bi-ARX supplies three cameras and a 14-dimensional state/action vector. Appendix D reports one inference every **0.5 seconds**, executing 25 of the 50 predicted action samples at 50 Hz. Each inference caches the observation prefix and performs ten flow-matching steps on the action chunk. Thus the estimated completion uses **80 calls**, not 2,000 full image-forward passes and not forty calls from assuming execution of all fifty predicted actions.

Use the original PaliGemma family: approximately 400M SigLIP visual parameters plus the Gemma 2B transformer, with a separate approximately 300M action expert. The [PaliGemma paper](https://arxiv.org/html/2407.07726v1) identifies the visual/language components. Use 224-pixel images with 14-pixel patches, or 256 image positions per camera, and assume 20 prompt positions including framing/padding. The exact 2024 robot preprocessing configuration is not separately disclosed; 224 pixels is the supported base configuration.

Per call, count:

- Visual backbone: 2×400M×256×3 = 614,400,000,000 FLOPs.
- Gemma observation prefix: 2×2B×(3×256+20) = 3,152,000,000,000 FLOPs, computed once and cached during flow integration.
- Robot state: 2×300M×1 = 600,000,000 FLOPs, computed once and cached.
- Action expert: 2×300M×50×10 = 300,000,000,000 FLOPs. All fifty predicted actions are processed at each integration step even though only 25 are executed.

The matrix subtotal is **4,067,000,000,000 FLOPs per call**. Add five percent for context-dependent attention products, visual-to-language projection and small action/time embeddings. This is a small component allowance: attention over roughly 788 prefix positions and fifty queries adds order 0.1 trillion operations in the language stack; action cross-attention adds another order 0.06 trillion. The allowance is not generic GPU utilization. Token embedding lookup and an unused vocabulary output head are not separately multiplied across image positions.

**Total = 4,067,000,000,000 × 1.05 × 80 = 341,628,000,000,000 FLOPs.** Prior pretraining and the optional high-level language planner used for other tasks are excluded. The flat-shirt evaluation is commanded directly to the base policy.

The current author implementation [Gemma configuration](https://github.com/Physical-Intelligence/openpi/blob/main/src/openpi/models/gemma.py) confirms eight query heads for both experts, whereas the original appendix prints num_heads=18 alongside depth=18. This likely typographical discrepancy does not affect the nominal-parameter central recipe; it should not be used to inflate attention by 18/8. Current code is corroboration of the architecture family, not proof of the exact 2024 checkpoint or deployment duration.

## Fields and release provenance

The token field counts only the twenty language prompt positions across eighty calls: **1,600 input tokens**, input_output. Visual patch and continuous action positions remain separate in the component recipe. They are not added to text tokens. Model encoder_parameters is 400M for visual encoding; decoder_parameters is the approximately 2.3B combined language/action transformers, whose different workloads must remain separate. Both are nominal reported component counts; no single token coefficient applies to this recipe.

The later openpi weight release does not by itself establish public availability of the exact full-700k model evaluated in the original Figure 7. Leave its model-release date blank.
