# Competitive robotic table tennis

## physical-table-tennis-dambrosio2024-minute

The point represents **60 seconds of active table-tennis play**, at the operating rates of D’Ambrosio et al.'s 2024 competitive robot. Compute is **30,385,148,843,700 FLOPs**, about 3.04 × 10¹³. This is a rate observation, not the cost or recorded duration of one match. It excludes pauses between points, prior training, and the human opponent's work from AI compute. Human time is the defined 60 seconds, with no contributing timing sample.

### Original evidence and human comparison

- [2024 competitive study, original version](https://arxiv.org/abs/2408.03906v1): retained as `competitive.pdf` and `competitive.html`. Section II.A identifies the deployed cameras and perception system; II.C–D describes the controllers; VI.D–E and Table VIII give further architectures. Section III.B–C and Figures 7–9 report match rules and human results.
- [2023 deployed system](https://roboticsproceedings.org/rss19/p006.pdf): retained as `system-rss2023.pdf`. Section II.B and Appendix E.3/Table II, PDF pages 4–5 and 21–22, supply the exact detector workload. This is the system explicitly referenced by the 2024 study, which retains the paired 125 Hz camera/perception rate.
- [2020 controller architecture](https://arxiv.org/abs/2003.14398v1): retained as `gated-controller.pdf`. Figure 2, Table I and Section IV.A, PDF page 3, establish the two gated hidden layers and ungated output followed by the 2024 controller.
- [Authors' project page](https://sites.google.com/view/competitive-robot-table-tennis): retained as `project.html`. It links the paper, match videos and released ball-state dataset, but does not establish a public release of the policy weights. The model release date remains blank; 7 August 2024 is a paper date.

The robot won 13/29 matches overall. There were 7 beginner, 11 intermediate, 5 advanced and 6 advanced-plus opponents (Figure 8). It won all beginner matches, 55% of intermediate matches, and no advanced matches. Thus the intermediate result is 6/11 matches; it also won 50% of points against that group (Section III.C). This supports `match` with intermediate recreational amateurs, classified `typical`. These players were assessed by a professional coach; their experience is described in Figure 7. The comparison is transferred from the matches to the defined operating interval, not measured separately for a one-minute sample.

The main study used modified rules: humans always served, and scoring began only after the robot returned the serve and the ball landed on the human side. All three games were played. Protective stops and very high balls were lets. Consequently this is amateur rally performance under the study rules, not evidence of parity at serving or regulation tournament play. A later five-person rules variation in Section III.G is a different assessment and is not combined with the main result.

The robot received the opponent's paddle pose from a 20-camera motion-capture system. The human was not supplied corresponding numerical paddle state. This concrete information difference is flagged `different_inputs_or_tools`; the flag is not based merely on the robot's embodiment or its use of cameras.

### Ball perception

Two cameras each provide 125 frames per second. The detector receives single-channel raw Bayer crops of **512 × 1024**, not the cameras' full 1280 × 1024 sensor area or the 64 × 64 patches used during training. Table II's input-channel entry of 8 conflicts with its first layer's 128 parameters: a 4 × 4 kernel and eight output channels require one input channel. The text and Figure 10 independently specify single-channel Bayer input, resolving that table error.

For each convolution, multiply its kernel weights by output spatial positions, two cameras, and two operations per multiply-add. Bias parameters are separated from weights. Dilation changes where the kernel is applied, not its multiply count. The two temporal buffers concatenate saved features; they do not rerun the preceding network on old frames.

| Layer | Output per camera | Kernel weights | FLOPs per paired frame, matrix operations |
|---|---:|---:|---:|
| First spatial convolution | 256 × 512 × 8 | 128 | 67,108,864 |
| After first temporal buffer | 256 × 512 × 8 | 1,152 | 603,979,776 |
| Downsampling convolution | 128 × 256 × 16 | 2,048 | 268,435,456 |
| After second temporal buffer | 128 × 256 × 64 | 18,432 | 2,415,919,104 |
| Prediction head | 128 × 256 × 5 | 5,120 | 671,088,640 |

The second and fourth kernels are 3 × 3, reconstructed from Table II's input/output channels and parameter counts. The fourth layer has 64 biases and the head has 5. The three batch-normalization layers have 64 trainable scale/offset parameters together. All parameters sum to the reported architecture's 27,013.

Matrix operations total 4,026,531,840 per paired frame. Add biases, two operations per inference batch-normalization affine transform, and one elementary operation per ReLU, as stated in Table II. Dropout is inactive. This logical, unfused operation convention gives 4,051,304,448 per paired frame and **30,384,783,360,000** over 7,500 paired frames. Matrix operations alone give 30,198,988,800,000, 0.61% less than the complete estimate. These are architecture counts, not hardware utilization or execution-time measurements.

### Controllers and helpers

Only the selected low-level controller executes at each 50 Hz step; the 17-policy library is not 17 concurrent neural passes. The 2024 model has 10,676 parameters, filters 76/96/8, dilation 1/2/4, valid padding, and input 8 timesteps × 16 features. Kernel size 2 and gating of the first two layers reconcile the exact count:

`(2×16×76 + 76) + (2×38×96 + 96) + (2×48×8 + 8) = 10,676`.

Temporal lengths are 7, 5 and 1, so matrix operations total 108,544 per call. Biases and an explicit elementary-operation allowance for tanh/sigmoid gates raise this to 112,608. At 3,000 calls per minute it costs 337,824,000 FLOPs.

The following small-module allowances avoid treating undisclosed details as zero work:

| Component | Source architecture and counting assumption | FLOPs per minute |
|---|---|---:|
| FiLM adapter | Reported 2,800 parameters plus eight action scales/offsets. Count one adapter on every LLC call, although only some library policies use it. | 16,848,000 |
| HLC style network | Reported 4,500 parameters, eight-step input. Allow eight temporal uses per parameter. One decision per incoming ball; assume one incoming ball/second. | 4,320,000 |
| HLC spin classifier | Reported 18 inputs and hidden widths 128/64. Assume two output logits, ReLU hidden activations, and five calls per incoming ball; actual use is on serves. | 6,491,700 |

One incoming ball/second is an accounting assumption, not an observed rally rate. The spin allowance follows the source's five-query voting rule and deliberately applies it to every incoming ball. Exact style/FiLM widths and their usage frequencies are not published. All four neural control components together contribute **0.0012%** of total compute. A stress case with tenfold LLC work, eightfold FiLM parameter reuse, and both HLC networks evaluated at every 125 Hz camera step increases the total by **0.0127%**. These omissions in detail do not make the dominant compute input assumed: image shapes, weights and camera rate are supplied by the source. The point uses `derived_supported_inputs`.

The other HLC components use stored skill descriptors, KD-tree queries, five heuristics and scalar bandit preferences (II.D.4–6); they do not execute the other LLC networks. Their non-neural bookkeeping is outside the neural-operation total. As a scale check, even exhaustive six-dimensional distance evaluation over all 28,000 states in all 13 rally tables would require only `60 × 13 × 28,000 × 17 = 371,280,000` arithmetic operations at the assumed event rate, another 0.0012%. The source actually uses KD-trees. Camera acquisition, LED motion capture, referee logic, classical triangulation/filtering and motor power are also outside the neural FLOP count. The post-hoc trajectory optimizer used to label training spin data is not an inference helper.

### Reproduction

`recipe.json` records the architecture inputs, source locators and small-component assumptions. `calculations.json` contains every layer and component total, sensitivities and source hashes. `recompute.py` requires Python 3.10+ and the standard library only. It verifies the retained originals against `agent-work/sources/table-tennis/source-manifest.json` and requires a new output file outside the evidence directory. From the published dataset directory:

```sh
python3 -B research/table-tennis/recompute.py \
  --sources agent-work/sources/table-tennis \
  --recipe research/table-tennis/recipe.json \
  --output /tmp/table-tennis-recomputed.json
```

For the candidate, use this batch's `sources` directory and `research/recipe.json` as the two inputs. No source files, robot code or benchmark tasks are executed.
