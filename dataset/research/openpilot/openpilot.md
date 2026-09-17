# comma.ai openpilot highway lane-keeping and following

*Created 2026-09-14 13:46.*

Nine points, one per deployed openpilot driving model from November 2020 to
September 2026, all on the same work unit: one minute of highway lane centering
and following. Compute is counted operation by operation out of the ONNX graph
the device actually runs, times the 20 Hz rate the code fixes, times 60
seconds. Human time is the defined 60 seconds. Performance is `below` on every
row, because openpilot is a supervised Level 2 system and the human baseline is
a driver who needs no supervisor.

| Release | Date | Graphs counted | Parameters | MACs per inference | FLOPs per minute |
|---|---|---|---|---|---|
| v0.8 | 2020-11-29 | supercombo | 15819463 | 460656304 | 1106000000000 |
| v0.8.5 | 2021-06-12 | supercombo | 14689785 | 459430000 | 1103000000000 |
| v0.8.16 | 2022-08-31 | supercombo | 23510932 | 708168480 | 1700000000000 |
| v0.9.4 | 2023-07-27 | supercombo | 23681248 | 708339312 | 1700000000000 |
| v0.9.7 | 2024-06-14 | supercombo | 25641048 | 843997936 | 2026000000000 |
| v0.9.9 | 2025-06-19 | vision + policy | 25334308 | 843691184 | 2025000000000 |
| v0.11.1 | 2026-06-05 | vision + policy | 30003315 | 847030832 | 2033000000000 |
| v0.11.1 big | 2026-06-05 | big vision + big policy | 80131710 | 8781539888 | 21080000000000 |
| chestnut Cinque v2 | 2026-09-11 | big supercombo | 382254316 | 46729876480 | 112200000000000 |

## Compute

### The work unit and the rate

openpilot's `modeld` process runs the deployed driving graph once per camera
frame. `ModelConstants.MODEL_RUN_FREQ = 20` in
[selfdrive/modeld/constants.py](https://github.com/commaai/openpilot/blob/master/openpilot/selfdrive/modeld/constants.py)
on the current master, and `DT_MDL = 0.05` in
[common/realtime.py](https://github.com/commaai/openpilot/blob/master/openpilot/common/realtime.py)
carries the same 20 Hz back through every release in the table, including
v0.8 in November 2020. One minute of driving is therefore 1,200 forward passes
of every graph in the deployed set.

Where the deployment splits the model into a vision graph and a policy graph —
v0.9.8 through v0.11.x — both run on every frame inside the same `run()` call
in `selfdrive/modeld/modeld.py`, so the two per-inference counts add before
multiplying by 1,200. The master branch merged them back into one
`driving_supercombo.onnx`.

### Counting the graph

[count_onnx_flops.py](count_onnx_flops.py) loads each ONNX file, runs ONNX shape
inference, and walks the node list charging multiply-accumulates: output
elements times kernel elements times input channels per group for `Conv`,
`M * K * N` for `Gemm`, output elements times the contracted dimension for
`MatMul`, and the product of all labelled dimensions for `Einsum`. Every graph
counted here resolved completely — no node was left with unknown shapes.
[flops_per_minute.py](flops_per_minute.py) turns those per-inference counts into
the per-minute figures above; both write to `agent-work/derived/openpilot/`.

FLOPs are two per multiply-accumulate, the dataset's convention, regardless of
the precision the device executes in. The chestnut weights ship as fp16 and the
comma three models are quantized further on device; neither changes the
operation count.

What the count covers is the driving graph and nothing else. Excluded:
`dmonitoringmodeld`, which watches the driver rather than the road and is part
of the supervision requirement rather than of the driving; the image warp and
YUV conversion that prepare the camera buffers; the Kalman filters and the
lateral and longitudinal controllers in `controlsd`, which are not neural. The
controllers run at 100 Hz but are a few hundred floating-point operations a
cycle, far below the resolution of these totals.

### Where the models came from

The deployed weights are in the openpilot repository under Git LFS, hosted on
Hugging Face at `commaai/openpilot-lfs` as declared in the repository's
`.lfsconfig`. Each file was pulled at the release tag whose row it backs and
its SHA-256 checked against the LFS pointer. Paths moved over the period:
`models/supercombo.onnx` at v0.8 and v0.8.5, `selfdrive/modeld/models/supercombo.onnx`
from v0.8.16 to v0.9.7, `selfdrive/modeld/models/driving_vision.onnx` plus
`driving_policy.onnx` from v0.9.8, and
`openpilot/selfdrive/modeld/models/driving_supercombo.onnx` on master.
Retained copies sit in `agent-work/sources/openpilot/`, which is not shipped.

### The big models and chestnut

Files prefixed `big_` are the models for comma's external-GPU hardware. The
`modeld_pkl_path` helper in `selfdrive/modeld/helpers.py` selects the `big_`
weights when `usbgpu_present()` finds the AMD device, and master's `modeld.py`
gates the same choice on `chestnut_present()`, logging a `chestnutGpuState`
service. The v0.11.1 `big_driving_vision.onnx` plus `big_driving_policy.onnx`
pair is the pre-launch version of that path at 80 million parameters; master's
`big_driving_supercombo.onnx` is the model chestnut runs today.

[comma's chestnut announcement](https://blog.comma.ai/chestnut/) of 12 August
2026 states that "Compared to the latest on-device model, the first
chestnut-class model has 30x more parameters, 100x more FLOPs, and room to go
even bigger", and that "We're launching chestnut with a new 1B parameter driving
model in the upcoming openpilot 0.11.2 release". That 1B model is not in the
public repository: 0.11.2 has not been tagged, and the big model currently on
master is the one committed on 11 September 2026 as "Cinque v2", at 382,254,316
parameters and 93.46 GFLOPs per inference. The row uses the counted model, not
the announcement, and does not assert the announced one.

The two disagree, and the direction matters for anyone reading the row as
comma's latest. Against the concurrent small model (30,003,321 parameters,
1.694 GFLOPs per inference on master), the counted big model is 12.7 times the
parameters and 55 times the FLOPs. comma's 30x and 100x describe a larger model
than the one shipping on master; taken literally they would put the announced
1B model at about 169 GFLOPs per inference, or 2.0e14 FLOPs per minute, roughly
1.8 times the row. comma's 30x parameter ratio does check out against our
small-model count — 1B over 30M is 30x — which is a useful independent
confirmation that the graph count for the small model is right.

The hardware bounds all of this from above. chestnut is an AMD Radeon RX 9060
8GB, and comma describes comma four plus chestnut as comparable to Tesla HW4.
At 20 Hz the counted model asks 1.87 TFLOP/s of sustained throughput, and even
the announced 1B model would ask about 3.4 TFLOP/s — both well inside what that
part delivers, so the hardware statement is consistent with the count without
constraining it tightly.

## Human time

A licensed driver spends the same 60 seconds keeping the lane and following the
car in front. The duration is fixed by the real-time work unit, so it is a
`defined_duration` with no completion-time sample behind it, exactly as for
`physical-dave2-steering-minute`. Skill is `typical`: an ordinary licensed
driver, not a selected or professional one.

Only the one-minute unit is built. One hour was considered and rejected: no
source establishes that openpilot completes an arbitrary unsupervised hour of
highway driving. comma's own target for calling openpilot 1.0 is "at least a
1000 hours between unplanned disengagements", stated in
[the road to openpilot 1.0](https://blog.comma.ai/the-road-to-openpilot-1-0/) as
something still ahead of them, and the marketing claim that openpilot "can drive
for hours without intervention" is not a measurement. The minute is the longest
unit the evidence supports.

## Performance and human comparison

Every row is `below`: openpilot does the job of lane centering and following,
noticeably worse than an unsupervised human, because it requires a supervisor
who is expected to take over.

The Level 2 character is comma's own statement, not an outside characterization.
[openpilot's SAFETY.md](https://github.com/commaai/openpilot/blob/master/docs/SAFETY.md)
describes openpilot as "an Adaptive Cruise Control (ACC) and Automated Lane
Centering (ALC) system", a "failsafe passive system" developed "to follow
industry standards of safety for Level 2 Driver Assistance Systems", whose first
design requirement is that "The driver must always be capable to immediately
retake manual control of the vehicle". A driver monitoring model runs alongside
the driving model to enforce that. The human baseline drives the minute with no
one watching.

Three quantitative anchors sit under the label, and none of them is a per-mile
disengagement rate, because comma does not publish one.

- **Fleet engagement.** [comma's openpilot page](https://comma.ai/openpilot),
  read 14 September 2026, reports that "Our 20,000+ users have driven over 300
  million miles with a device running openpilot" and that over 56% of those
  miles were driven by openpilot. comma's [autonomy post](https://blog.comma.ai/autonomy/)
  of July 2024 gave "over 50% of miles" on a fleet of 10,000+ devices. The
  engaged fraction is comma's own headline metric, chosen, as
  [the road to openpilot 1.0](https://blog.comma.ai/the-road-to-openpilot-1-0/)
  explains, because disengagements are expected on a Level 2 system. Roughly
  half of the fleet's miles are driven by the human, which is a direct statement
  that the system does not cover the driving task the human covers.
- **comma's own unmet reliability bar.** The 1,000 hours between unplanned
  disengagements that comma sets as the precondition for a 1.0 release is a
  standard comma says it has not met.
- **Third-party evaluation.** Consumer Reports' November 2020 evaluation of
  active driving assistance systems ranked the comma two running openpilot
  first of seven systems tested, ahead of Cadillac Super Cruise and Tesla
  Autopilot, scoring capability and performance, keeping the driver engaged,
  ease of use, clarity about when it is safe to use, and response to an
  unresponsive driver. That places openpilot at or above its commercial Level 2
  peers and says nothing about parity with an unsupervised driver. It is the
  only independent evaluation covering openpilot in the period, and it applies
  to the v0.8-era model.

The later rows carry no version-specific external evaluation. The label rests on
the Level 2 design requirement, which every release in the table shares, and on
the fleet engagement statistics, which are contemporaneous with the later rows.
The direction of travel across releases — comma's stated goal of increasing time
between disengagements, and the engaged share rising from over 50% to over 56% —
supports the later models being at least as capable as v0.8, not less, so the
common `below` label does not flatter the older rows at the newer ones' expense.

Two comparison issues are flagged on every row. `different_inputs_or_tools`:
the model sees a pair of cropped, warped camera crops at 256x128 and a feature
buffer, while the human has direct vision, peripheral vision, mirrors and
vehicle motion cues. `different_assessment`: nothing here is a paired trial on
the same minute of road. The AI side is a fleet aggregate and a ranked
third-party test, the human side an assumed competent baseline.

Lane changes, turns between roads, navigation and non-highway driving are
outside the stated work unit on both sides. openpilot's lane change assist is
driver-initiated and its speed ceiling is around 92 mph, neither of which binds
inside the unit.

## physical-lanekeep-openpilot-v08-minute

openpilot v0.8, released 29 November 2020, running `models/supercombo.onnx` at
the v0.8 tag. One graph, 460,656,304 MACs per inference, 15,819,463 parameters.
Single road camera, 12x128x256 input. This is the model the Consumer Reports
November 2020 evaluation was testing on the comma two.

## physical-lanekeep-openpilot-v085-minute

openpilot v0.8.5, released 12 June 2021. 459,430,000 MACs per inference,
14,689,785 parameters. Architecturally the same single-camera supercombo as v0.8
with a slightly smaller head; the per-minute compute is within 0.3% of the v0.8
row.

## physical-lanekeep-openpilot-v0816-minute

openpilot v0.8.16, released 31 August 2022, running
`selfdrive/modeld/models/supercombo.onnx`. 708,168,480 MACs per inference,
23,510,932 parameters. The first counted release taking two camera streams,
`input_imgs` and `big_input_imgs`, which is where the step up from the v0.8 rows
comes from.

## physical-lanekeep-openpilot-v094-minute

openpilot v0.9.4, released 27 July 2023. 708,339,312 MACs per inference,
23,681,248 parameters. Same convolutional backbone as v0.8.16; the graph adds a
`nav_features` input and a 99-step feature buffer, which cost almost nothing
next to the vision trunk.

## physical-lanekeep-openpilot-v097-minute

openpilot v0.9.7, released 14 June 2024. 843,997,936 MACs per inference,
25,641,048 parameters. The backbone grows to 794M convolutional MACs and the
graph gains a 34M-MAC attention-style `MatMul` block over the feature buffer.

## physical-lanekeep-openpilot-v099-minute

openpilot v0.9.9, released 19 June 2025, running `driving_vision.onnx` and
`driving_policy.onnx` on every frame. 804,984,192 plus 38,706,992 MACs per
inference, 25,334,308 parameters together. The split is a deployment change, not
a capability change; the total is within 0.1% of v0.9.7.

## physical-lanekeep-openpilot-v0111-minute

openpilot v0.11.1, released 5 June 2026, the last tagged release before
chestnut. 810,658,608 plus 36,372,224 MACs per inference, 30,003,315 parameters.
This is the "latest on-device model" that comma's chestnut announcement compares
against, and its parameter count is what makes comma's 30x ratio land on a 1B
model.

## physical-lanekeep-openpilot-v0111big-minute

openpilot v0.11.1's external-GPU model, `big_driving_vision.onnx` plus
`big_driving_policy.onnx`, selected when `usbgpu_present()` finds the AMD device.
8,745,167,664 plus 36,372,224 MACs per inference, 80,131,710 parameters — ten
times the compute of the on-device model at the same release, on the same
driving task. Shipped in the public release branch two months before the
chestnut hardware launch.

## physical-lanekeep-openpilot-chestnut-minute

The chestnut-class model on the openpilot master branch,
`openpilot/selfdrive/modeld/models/big_driving_supercombo.onnx`, committed 11
September 2026 as "Cinque v2". 46,729,876,480 MACs per inference, 382,254,316
parameters stored fp16, a 32x32x512 feature buffer, and a `MatMul`-dominated
graph — 45.4G of the 46.7G MACs are `MatMul`, against 1.3G of convolution, so
the architecture has moved from a convolutional trunk with small heads to
something transformer-shaped.

comma's announced 1B-parameter model for openpilot 0.11.2 is not this model and
is not public; the reconciliation is in the compute section above. The row is
the counted graph.
