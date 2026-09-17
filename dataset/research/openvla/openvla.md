# OpenVLA: putting corn on a plate

## phys-openvla-corn-placement-demos

One completed placement of a yellow toy corn on a pink plate, with other objects in a small tabletop sink. Compute is the mean reconstructed work of both clips published under **Put Yellow Corn on Pink Plate** in the original project's **Sample OpenVLA Rollout Videos → Real-World Bridge V2 WidowX Robot Rollouts**. This is a selected successful demonstration sample, not the average of all evaluation attempts.

The estimate is **178.37 trillion FLOPs and 5 seconds of human active effort** per completed placement. The human target is the demonstrated outcome, so `match` is conditional on that output quality. It is not a claim of equal overall success probabilities.

### Task and selection

The [original project page](https://openvla.github.io/) links these two videos, retained under `agent-work/sources/openvla/videos/` relative to the dataset directory:

| Original filename | Encoded frames | Encoded seconds | Estimated policy calls |
|---|---:|---:|---:|
| `openvla--put_corn_on_plate--clutter.mp4` | 38 | 3.8 | 38 |
| `openvla--put_corn_on_plate--clutter--2.mp4` | 47 | 4.7 | 47 |

Both start with the gripper above the sink, approach the corn among distractors, grasp it, move it to the plate and release it. The second places the corn on a plate toward the rear; the first places it near the front. Neither requires opening packaging, preparing food, walking, learning a robot interface or arranging the initial scene. The clips and reconstructed contact sheets permit inspection of the initial and final states. All their frames are retained; there is no trimming after a favorable frame.

The original paper's [Appendix B.1.1 and Table 4](https://arxiv.org/html/2406.09246v3) report **9 points across 10 evaluation attempts** on this named task. A trial earns 1 for placement, 0.5 for approaching the correct object, and 0 otherwise. The paper does not give the full-success count separately: 9 points could represent nine full successes, or eight successes and two partials. The published demonstration clips are not identified with particular Table 4 trial records. Their successful selection does not turn that broader score into 100% performance.

### Policy-call estimate

The published [Bridge evaluation loop](https://github.com/openvla/openvla/blob/c8f03f48af692657d3060c19588038c7220e9af9/experiments/robot/bridge/run_bridgev2_eval.py) appends one camera observation to `replay_images` immediately before each `get_action` query. The associated `bridgev2_utils.py` writes every such observation to a replay video. The central estimate transfers that convention to these original clips: **one recorded frame per complete policy query**, averaging 42.5 calls. It includes the query following the final saved observation; it does not subtract one merely because the next resulting state is absent. There is no separately documented planner or learned control helper in this policy loop. Conventional robot actuation and camera processing are outside neural FLOPs.

The exact website-video export recipe and native action logs are unavailable. These videos are encoded at 10 fps. The page says this section is sped up 1.5×, whereas the subsequently published replay helper writes at 5 fps. Those facts do not establish a common wall clock. Treating video duration ×1.5×5 Hz as the call estimate gives 31.875 calls on average, 25% below the central estimate. The frame-based recipe avoids treating a nominal controller rate as measured throughput, but could still miss dropped frames, duplicate frames, an initial crop or processing outside the clip. A doubled-call scenario covers substantial frame dropping. One fewer or additional call per clip changes FLOPs by 2.35%. No episode-step limit is used as observed duration.

### Architecture and arithmetic

The model is the original **OpenVLA-7B** generalist, which the project identifies as controlling WidowX without task-specific fine-tuning. Its [release configuration and implementation](https://huggingface.co/openvla/openvla-7b/tree/742ce85fb9176ed3dc6474e80e3812fb554baa8f) are retained alongside the repository's pinned Timm 0.9.10 and Transformers 4.40.1 source. The June release and current configuration files are identical. The later action wrapper conditionally avoids adding a duplicate empty token; for the prompt below it produces the same input as the release wrapper.

Each call processes one RGB observation, resized separately to 224×224 for two encoders:

| Component | Executed structure | FLOPs per call |
|---|---|---:|
| DINOv2 ViT-L/14 with registers | 256 patches + 1 class + 4 register positions; width 1,024; MLP width 4,096; 24 blocks | 165.103 billion |
| SigLIP ViT-SO400M/14 | 256 patches; width 1,152; MLP width 4,304; 27 blocks | 219.485 billion |
| Fused projector | Concatenate features into 2,176 dimensions; linear widths 2,176 → 8,704 → 4,096 → 4,096; two GELUs | 36.561 billion |
| Llama 2 decoder and vocabulary head | 32 blocks; width 4,096; MLP width 11,008; 32 attention and KV heads; vocabulary 32,064 | 3,775.748 billion |
| **Total** | One image-conditioned seven-dimensional action | **4,196.896 billion** |

Although OpenVLA requests second-to-last visual features, Timm 0.9.10 `_intermediate_layers` loops through **all** blocks. It does not exit at the selected layer. Both encoders therefore incur their complete block computation. The final visual norms and SigLIP attention-pooling head are stored but are not executed by this route.

The released SentencePiece tokenizer counts the official prompt template with the named task:

```text
In: What action should the robot take to put yellow corn on pink plate?
Out:
```

Including BOS and the release wrapper's appended empty token gives **22 text positions**. The precise native instruction string is not logged with the clips; this is the published template with the exact displayed task. A four-position variation changes total FLOPs by about 1.3%.

The two visual feature streams are concatenated along their feature dimension, producing **256 visual positions**, not 512. Prefill therefore has 278 positions. The model generates seven action symbols for three translation coordinates, three rotation coordinates and the gripper. Its within-call KV cache processes six additional action positions after prefill; predicting the seventh output does not require forwarding that last output again. The seven-output count comes from the defined action dimension and trained output format. Early EOS remains possible in the generic generation API, but is not an observed event in these clips; seven valid dimensions are the task-based central assumption. No image/history cache is carried between control calls.

For decoder width `h`, MLP width `m` and processed positions `n`, linear block work is `2 × 32 × n × (4h² + 3hm)`. The six incremental forwards reuse prior keys and values. Causal attention counts both matrix products over the permitted query–key pairs; full-square prefill attention is also retained as a scenario. Transformers 4.40.1 applies the vocabulary projection to **all** returned hidden positions, including prefill, so its cost is `2 × n × h × 32064`. The recipe separately counts visual patch projection, visual attention, MLPs, projector layers and decoder attention.

Multiply-adds count as two FLOPs regardless of numerical precision. Explicit small scalar allowances cover biases, normalization, activation, positional rotation, residual addition and attention scaling/softmax; each transcendental is counted as one scalar operation. This is an arithmetic convention, not a kernel instruction measurement. Scalars add 0.061% to the matrix-and-attention count. The result is insensitive to small differences in their fused implementation. Image resizing, data movement, integer token decoding and robot mechanics are excluded.

The CSV's **935 text tokens** are 22 ×42.5 repeated prompt positions. Visual positions and generated action symbols are retained separately in the calculation. `input_output` is appropriate here because all text input is fresh per control call and the output contains no text tokens. It does not imply that visual or action computation is absent.

### Human effort

The target is an ordinary adult with functional arm and hand mobility, already within reach of the same sink, using their hand to make a comparable completed placement. There is a concrete embodiment difference: the AI controls a robot gripper from camera images; the human has direct vision and hand contact. `different_inputs_or_tools` records it.

[Choi et al. (2023), Table 2 and §§2.2–2.3](https://www.frontiersin.org/journals/neurology/articles/10.3389/fneur.2023.1225425/full) provide a movement-time anchor: 20 healthy adults reached to a glass 30 cm away in 1.00 seconds and transported it toward the mouth in 1.32 seconds, on average. Each contributed the middle three of five recorded trials; **60 contributing calibration attempts** are counted. The study also timed replacement and return, which are excluded here because the target requires one transfer. This is a transfer from comfortable cup movements, not a recorded corn-placement timing.

The inspected corn is large and readily graspable, with no precision insertion. It needs a short transfer across the sink. We retain the measured 2.32-second reach/transport anchor, add an assumed 2 seconds to take in the short instruction and locate the corn and plate, and 0.7 seconds for release and checking. The 5.02-second recipe is rounded to **5 seconds**. An efficient familiar user may need around 3 seconds; a more deliberate first encounter may need 8 seconds. These are scenarios, not confidence bounds. The estimate excludes prior practice, resetting the scene and bringing the person to the table.

`human_time_evidence=transferred_timings` reflects the substantive movement-time calibration. `human_time_method=estimated` reflects the task transfer and added allowances. `human_time_statistic=point_estimate` avoids treating the adjusted target as an observed mean. `human_time_subset=all` refers to all 60 trials contributing to the donor's reported means, not its separately excluded familiarization/fatigue trials or a successful-trial filter.

### Model record

The [official README](https://github.com/openvla/openvla/blob/c8f03f48af692657d3060c19588038c7220e9af9/README.md) dates the initial public release to **2024-06-13**. Earlier private preparation is not used as a release date. Published architecture arithmetic gives **6,738,939,904 decoder parameters** and **802,297,280 visual-encoder/projector parameters**. Their sum, **7,541,237,184**, exactly matches the model repository's retained safetensors metadata. Encoder parameters include its unexecuted pooling/final normalization weights; their FLOPs are excluded. There is no shared FLOPs-per-token coefficient for this multimodal architecture.

### Replay

Install `av`, `sentencepiece` and `Pillow`. Run the following with the actual source directory and a **new** output directory:

```sh
python recompute.py --source-dir /path/to/openvla/sources --output-dir /path/to/new-output
```

The script checks all retained source hashes, decodes both videos, tokenizes the prompt, reconciles parameters, counts operations and writes calculations plus inspection sheets. It requires no model weights, GPU, external service, repository working directory or temporary dependency path. `calculations.json` contains the exact per-component values, both attempt estimates and all scenarios.
