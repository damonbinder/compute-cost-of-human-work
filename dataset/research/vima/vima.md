# VIMA: one object into a receptacle

## phys-vima200m-visual-manipulation

One complete default VIMA-Bench visual-manipulation episode: identify the object and receptacle shown in the multimodal prompt, then pick and place the object into the receptacle with one distractor present. The estimate is **9.1476e11 FLOPs and 6 seconds of human effort**. AI acts in simulation using a robot suction primitive; the human estimate is a person manipulating corresponding physical objects within reach. This embodiment and input difference is explicit, not a measured human benchmark.

## Source task and performance

The [original paper](https://proceedings.mlr.press/v202/jiang23b/jiang23b.pdf), Appendix B task01 and Table16, reports 100% L1 visual-manipulation episode success for VIMA-200M. The [pinned task source](https://github.com/vimalabs/VIMABench/blob/97e0af11e126fd477c9d81eeabfb6c739021c680/vima_bench/tasks/task_suite/instruction_following/simple_manipulation.py) defaults to one dragged object, one base and one distractor. The workspace is 0.5×1m, in base.py. The object collection includes blocks and simple shapes; receptacles include hollow geometric bases, bowls and pans. The default prompt is `Put the {dragged_obj_1} into the {base_obj}.` Both placeholders supply object images. It does not require moving all objects, learning a new skill, or opening/assembling anything.

The source success is episode completion, not first-action success. Match is a best judgment for this straightforward human task, informed by the reported AI completion; no human completion cohort is supplied. The estimate permits correcting an initial grasp or placement. It does not claim 100% observed human accuracy.

The public 650K training trajectories are successful **scripted oracle** demonstrations. They cannot establish policy retry counts, and the 21GB archive was not downloaded. The released demo has `oracle_max_steps+2`; this task's default oracle_max_steps=3 already allows two mistakes. Five is a demo cap, not an observed mean or verified original paper cap.

## Workload estimate

One correct pick/place macro-action suffices. Central computation gives 75% weight to one-call cost and 25% to two-call cost: an explicit **1.25-call correction allowance**, not an observed distribution or a deduction from 100% success. This permits occasional correction while treating a simple one-object task with perfect reported episode success as usually solved without repeated rearrangement. One call and the full five-call released-demo budget are alternatives. The source does not calibrate the correction frequency; recovering evaluation trajectories would improve this part of the point.

There are two camera views (128×256 each) and three physical objects. Central uses three detected objects per view. Occlusion/false detections could change that count. The prompt has two single-object assets, each encoded in both views. Original tokenization gives seven text tokens including EOS, plus four visual object tokens: eleven T5 positions. Prompt encoding is performed once. Cached prior object/action embeddings are retained, but the policy reruns the history transformer and cross-attention at each action. At action k the sequence length is 6k+k−1.

All original task-execution neural components are counted:

- A Mask R-CNN R50-FPN detector on each current scene view. Paper C.4 explicitly names `mask_rcnn_R_50_FPN_3x`; the released demo instead uses simulator segmentation, which is **not** substituted for the detector in this paper-performance estimate.
- Four-layer, width768 ViT on each32×32 object crop (four patches plus class position), bounding-box MLP and object-fusion projection.
- T5-base encoder, all12layers, width768, FF3072. Frozen layers still run; the paper fine-tunes only its last two layers. No T5 decoder or vocabulary generation head is invoked.
- VIMA-200M policy's11cross/self-attention blocks, width768, GEGLU FF expansion4; observation/end-effector fusion, action embeddings and all12independent action-decoder MLPs.

The calculator counts two FLOPs per multiply-add. It includes quadratic attention, not just2Ptoken. Normalization, interpolation, softmax, nonlinearity, ROIAlign and non-neural simulator/control work are not individually profiled. The decision-making model's rounded200M is not used as an end-to-end parameter multiplier.

### Detector implementation assumption

The paper does not retain its actual evaluation detector resizing override or proposal counts. Use the named model's [original Detectron2 v0.6 defaults](https://github.com/facebookresearch/detectron2/blob/v0.6/detectron2/config/defaults.py) as the central implementation transfer: short edge800, max edge1333. A128×256 view becomes approximately667×1333, padded672×1344. Count the ResNet50 bottleneck stages, FPN convolutions, RPN, two1024-wide box FC layers and the mask head.

The default1000post-NMS RPN proposal limit is assumed filled for box scoring. This is a processing assumption, not a reported count. Three post-box detections receive mask processing. Original COCO80classes are retained as a small output-head proxy because VIMA's fine-tuned class-head dimensions are unavailable; original paper says predicted names are unused. Alternatives use100proposals and10mask detections. Their effect is modest compared with image resizing. The native128×256alternative falls to **1.1870e11 FLOPs**, about7.7×below central; this preprocessing uncertainty must remain visible. There is no evidence that the original evaluation definitely used native resolution or the default resize.

The one-call cost is7.31876e11F and five-call cost3.67449e12F. `calculations.json` preserves component counts. The default detector dominates; this is an architecture-and-workload estimate with assumed inputs, not measured inference telemetry.

## Human estimate

A typical adult already seated/standing within reach sees the short instruction and two object images, identifies the target among three tabletop items, then reaches, grasps, transfers and releases it into an accommodating receptacle. Charge approximately2seconds to read/locate and4seconds to execute and confirm the placement, rounded **6seconds**. The table dimensions constrain this to ordinary reaching, not walking or transporting an object between rooms. The bounds move the two components separately. A one-glance identification and a standard reach-and-place motion cycle, about two seconds at predetermined-motion-time rates, gives three seconds; reading the instruction and comparing both object images before acting, then re-seating an awkwardly gripped item, gives ten. This is a direct task-based judgment, not a measured movement-time study. No initial setup of the table, robot programming or learning to operate the benchmark is included on either side. Physical human handling versus simulated suction execution is recorded as different_inputs_or_tools.

## Model identity and date

The [original model card](https://github.com/vimalabs/VIMA/blob/8449837aa453f8ec9ba229cb956e3bbef5c796ea/model-card.md) identifies Stanford/NVIDIA VIMA models. The [first complete public weight commit](https://huggingface.co/VIMA/VIMA/tree/db745b2ba2f05d4f9ef6ecdbbe47b08244a04e3d), dated **2022-10-05**, contains the200Mcheckpoint (1.566GB), independently of the paper date. The registry records no universal FLOPs/token or activated-parameter coefficient for this multimodal system. T5 encoder111M and decision-making decoder200M are the paper's rounded component counts; the additional detector/object encoders are counted separately by operations. Historical checkpoint-to-final-paper revision equivalence is a family-level transfer; weights were not executed.

## Reproduction

`python research/recompute.py --sources SOURCE_DIR --output NEW_JSON` requires the `tokenizers` package. It reads retained source files and the actual prompt tokenizer, never executes model or simulator code, and rejects existing/source outputs. `download-urls.json` maps retained originals to URLs; calculation output hashes all source files. The assumptions are in the script and explained above. One bounded point is proposed; no near-identical language/object variants are added.
