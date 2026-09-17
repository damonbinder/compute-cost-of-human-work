# Dactyl: execute a supplied one-handed cube sequence

## robo-cube-dactyl

Primary source: [original Dactyl paper](https://arxiv.org/html/1910.07113v1), Sections 6–8, Tables 13, 17 and 21. Original PDF and text are retained in agent-work/sources/. The quantitative robot experiment executes a prescribed fair scrambling sequence from the solved state, equivalent to reversing that sequence to solve the cube. It does not measure the robot discovering a solution plan. The matched human work is therefore to execute the same supplied sequence one-handed, not to mentally solve an unknown cube.

The fixed sequence has 26 quarter face rotations and 17 whole-cube flips. Select the best ADR (XXL) policy with visual pose and Giiker face-angle sensors. It achieves the complete 43-subgoal sequence in 2 of 10 trials; the purely visual variant achieves none. Table 21 reports 6.55 seconds per flip and 11.79 per face rotation. A complete-sequence workload estimate is `17×6.55 + 26×11.79 = 417.89 seconds`. This transfers average subgoal costs to a complete sequence; it is not a recorded mean duration of successful whole-cube runs. Failed attempts and the source's continuation beyond the 43rd success are not represented as independently observed usage. The scope stops at the 43rd successful subgoal. Compute estimates a completed sequence; failed whole-sequence attempts are excluded. It is neither the average cost of an arbitrary attempt nor total cost until obtaining success.

## Neural operations

Table 13 reports 13,863,132 policy parameters plus 267,776 shared input-embedding parameters. Approximate one recurrent step as two operations per activated parameter: 28,261,816 FLOPs. The value network is a training-only critic and excluded. The policy is a 2,048-unit input layer followed by a 1,024-unit LSTM. Its stated action rate is 12.5 Hz.

The substantial vision work is also included. Table 17 specifies three 200×200 RGB camera inputs, a custom 64-channel 5×5 stride-2 valid convolution and a 2×2 stride-1 pool before a ResNet-50 bottleneck stack, followed by another 2×2 stride-1 pool. The three flattened towers feed 512 and 256 dense layers and a 280-output head. `count_dactyl.py` counts the custom stem and standard bottleneck matrix operations. Table 17's shorthand does not fully pin down internal downsampling padding; use common SAME-padded 3×3 bottlenecks, with downsampling on the middle convolution. The resulting spatial sizes are 97→49→25→13, then 12 after the final pool. This is an architectural reconstruction, not a profiler measurement.

Assume one three-camera inference per 12.5 Hz control step. The source explicitly establishes this frequency for control and electronic cube readings, but not an independent vision scheduler, so visual cadence is an assumption. Use the full published visual head even though electronic readings supply face angles in this selected configuration; removing its unused outputs has negligible effect on the total. Multiply both vision and policy operations by 417.89×12.5. All intermediate counts are saved in `research/dactyl-operations.json`. Conventional state tracking, motor control and the supplied solution sequence are not extra learned-model calls. Training and simulation are excluded.

## Human active-time estimate

Estimate **36 seconds** for a practiced one-handed cube manipulator to follow the prescribed sequence on a familiar, freely turning cube: about 16 seconds for 26 quarter turns (0.6 s each), 10 seconds for 17 reorientations (0.6 s each), and 10 seconds to consult the sequence, pause and verify progress. The source sequence contains 18 written moves because several are double turns. This allowance is materially more than just a motor-speed multiplication: the person must keep place in the supplied instructions and confirm the endpoint. An approximate 20–60 second range covers handling fluency and reading overhead. This is an explicit task-based estimate; it is not a recorded speedcubing result or general-public performance.

A practiced person is expected to execute this finite supplied sequence reliably, whereas the selected robot finishes 2/10 attempts. Classify below. The human has ordinary visual/tactile feedback and a freely manipulable cube; the robot uses visual pose plus internal angle sensing and a fixed robot hand. This material tool difference is disclosed. The absence of a measured human success rate is not converted into an invented 100% figure.

## Model release provenance

The paper supplies architecture descriptions but no exact evaluated ADR (XXL) policy and visual checkpoint release date was established. Leave model release date blank; paper publication is not evidence of weight availability.
