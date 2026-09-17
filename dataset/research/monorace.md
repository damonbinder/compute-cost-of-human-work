# MonoRace — one A2RL x DCL race against the champion FPV pilots (arXiv 2601.15222)

*Created 2026-09-13 12:10.*
*Revised 2026-09-13 12:31 as Revision 1, after `reviews/monorace-independent.md`;
see `candidates/monorace/REVISION.md`. Revision 2 on 2026-09-13 12:44. No value changed.*

## Summary

One candidate row, `robo-drone-monorace`, at **1.105e13 FLOPs** against **19.863 seconds** of
world-class human time, i.e. 5.56e11 FLOPs per human-second. The work unit is one complete
organizer-timed race run on the April 2025 A2RL x DCL track — two laps through eleven gates, timed
from the first passage of Gate 1 to the second passage of Gate 11. The AI side is MonoRace's fastest
completed run, 16.59 s on the organizers' VTx RF timing (16.56 s on the drone's own state estimate).
The human side is the mean of the three champion pilots' fastest completed runs in the same knockout
tournament: Platon Cheremnykh 19.14 s, Killian Rousseau 19.71 s, Yuki Hashimoto 20.74 s. Performance
is **`above`**: MonoRace won the AI vs Human challenge and no human completion in the tournament was
within 2.5 s of its time.

Compute is an operation count over the two published networks at their published rates. GateNet, a
U-Net with the paper's channel ladder at f = 4 over a 384×384 crop, is **7.401e9 FLOPs per forward
pass at 90 Hz**, and carries 99.998% of the total; the 24→64→64→64→4 G&CNet at 500 Hz is 19,968
FLOPs per call and is numerically irrelevant. The dominant assumptions are the two decoder details
the paper leaves open — the transposed convolution's kernel size and whether the "adding" of skip
connections is literal — which bracket the total between **1.09e13 and 1.49e13** (0.99× to 1.35× the
central value). The input channel count is the third, and it moves the total by 1.1%.

Three things a reviewer should look at first:

1. **The human statistic selects each pilot's fastest completion, and two of those three runs were
   flown against another human, not against the AI.** Killian's 19.71 s and Platon's 19.14 s are from
   the runner-up heat; in their own heats against MonoRace, Killian recorded no completion and Vicent
   recorded none either. An all-completions mean over the six recorded human finishes is 22.122 s and
   would make the AI look better, not worse.
2. **The final was a double non-completion.** Figure 1D records `x` for both MAVLAB's M16 and Yuki
   Hashimoto in heat 8, yet the organizers classified MAVLAB first and Hashimoto second. The `above`
   label therefore rests on the recorded times across the tournament and the organizers'
   classification, not on a head-to-head finish in the final.
3. **The decoder is 43% of GateNet's arithmetic and is the part the paper under-specifies.** The
   encoder ladder is fully determined by the published diagram; the decoder's upsampling kernel and
   skip-combination rule are not.

---

## Source and what it actually publishes

Bahnam SA, Ferede R, Blaha TM, Lang AE, Lucassen E, Missinne Q, Verraest AEC, De Wagter C, de Croon
GCHE. *MonoRace: Winning Champion-Level Drone Racing with Robust Monocular AI.* arXiv:2601.15222v1
[cs.RO], 21 January 2026, CC BY 4.0. Control & Operation, Delft University of Technology (MAVLab).
The full PDF text layer is retained at
`agent-work/sources/monorace/monorace-2601.15222v1-pdftext.txt`, every passage used is quoted with its line
number in `agent-work/sources/monorace/key-passages.md`, and event records are in
`agent-work/sources/monorace/event-records.md`. Provenance: `agent-work/sources/monorace/MANIFEST.md`.

Reported by the paper, and used here:

| Quantity | Value | Where |
|---|---|---|
| Camera capture | 820 × 616 at 90 Hz, 155° × 115° FoV | Perception, l.838 |
| GateNet input | 384 × 384 crop, f = 4 | Perception l.840; Training setup l.901 |
| GateNet ladder | inc-64/f, down1-128/f, down2-256/f, down3-512/f, down4-512/f; up1-256/f, up2-128/f, up3-64/f, up4-64/f; five 1×1 heads | Network diagram |
| GateNet blocks | "double 3×3 convolutional layers with batch normalization and ReLU" | l.872 |
| Decoder skips | "a transposed convolution and batch normalization, followed by adding the skip connections" | l.877 |
| Vision rate | 90 Hz, sustained on the Jetson Orin NX | l.838; Fig. 5 |
| G&CNet | three fully connected layers, 64 neurons each, 24 observations in, 4 motor commands out | l.1583 |
| G&CNet rate | 500 Hz on an STM32H743 | l.123, l.750 |
| Race unit | two laps, 11 gates with 1.5 m openings, timed Gate 1 first passage to Gate 11 second passage | l.137 |
| Track | 76 × 18 × 5.4 m flown volume inside a 100 × 30 m hall | l.137, l.618 |
| AI fastest completion | 16.56 s onboard, 16.59 s organizer-timed | l.163; Fig. 1D |
| Knockout times | Fig. 1D bracket, VTx RF timing | Fig. 1D |
| Real-flight trial counts | M16 4 trials / 1 completion; 82 trials / 64 completions across six policies | Fig. 2 tables |

Not published, and therefore assumed or excluded: GateNet's input channel count; the transposed
convolution's kernel size; the inference precision and the achieved Orin NX utilization (irrelevant
under an operation count); any weights or code release; the human pilots' drone configuration.

---

## The work unit

The organizers define the unit, which is why this row uses it rather than normalizing to a lap. A
run is timed from the first passage of Gate 1 to the second passage of Gate 11, covering two laps
less the closing Gate 11 → Gate 1 leg of the second lap. Both sides are timed over exactly this
interval by the same VTx RF system, so the comparison is exact at the level of the run and only
approximate at the level of a lap: dividing by 2 gives the time for 10.5 of the 11 inter-gate
segments, understating a true lap by about 4.5% on both sides equally. The normalized figures are
8.295 s per lap for MonoRace and 9.932 s per lap for the pilots, and `compute_flops_per_lap` in
`agent-work/derived/monorace/calculations.json` carries the halved compute for anyone who wants the
Swift-comparable unit; the row itself is per race.

Taking the run rather than the lap also removes the start-overhead allocation the Swift row had to
make. The organizers' clock starts at Gate 1, after the launch and the run-up, for AI and human
alike. Flight before Gate 1 and after Gate 11 is outside the unit on both sides, so the compute the
drone spends taxiing to the start line is excluded along with the pilot's time there.

---

## robo-drone-monorace

### Human time

Figure 1D is the organizers' bracket, timed by a VTx-based RF system. Reassembled
(`agent-work/sources/monorace/key-passages.md`), the human completions are:

| Pilot | Quarter-final | Semi-final | Runner-up heat | Final | Fastest completion (s) |
|---|---|---|---|---|---|
| Killian Rousseau | 24.07 | none recorded | 19.71 | — | 19.71 |
| Yuki Hashimoto | 23.06 | 20.74 | — | none recorded | 20.74 |
| Platon Cheremnykh | 26.01 | none recorded | 19.14 | — | 19.14 |
| Vicent | none recorded | — | — | — | none |

`human_time` = (19.71 + 20.74 + 19.14) / 3 = **19.863333333333333 s**, a mean over three recorded
successful attempts, one per pilot. This is the construction the dataset's Swift row already uses —
each champion's fastest complete race, averaged — and it is the conservative choice here, since
every wider selection is slower. The alternatives, all in `calculations.json`:

| Selection | Human time (s) | n | Note |
|---|---|---|---|
| Fastest completion per pilot (used) | 19.863 | 3 | Excludes Vicent, who recorded none |
| All recorded human completions | 22.122 | 6 | Includes the three slow quarter-finals |
| Fastest human completion of the tournament | 19.14 | 1 | Platon Cheremnykh, runner-up heat |

Vicent is excluded because he has no recorded completion, not because the selection rule drops him;
`human_time_subset = successful` and `human_attempts = 3` describe exactly the three runs that
enter the mean. `human_time_method = other_calculation`: this is arithmetic on recorded timings, not
a judgment-based estimate. `human_time_evidence = task_timings`: the organizers recorded these
pilots on this track over this unit.

`human_skill = world_class` is established directly. Hashimoto was the FAI World Drone Racing
Champion and took drone-racing gold at The World Games 2025; Rousseau won the FAI Drone Racing World
Cup and led qualification at a later FAI world championship; all four were the leading finishers of
the DCL Falcon Cup held in the same hall on the same dates. The paper calls them "three world
champion-level FPV pilots" and TU Delft's release "three former DCL world champions". Sources in
`agent-work/sources/monorace/event-records.md`.

One caveat that belongs in the note rather than the CSV: the DCL Falcon Cup ran in the same hall on
the same dates. DCL's own report of the Finals gives Hashimoto "the fastest overall time in the
finals, clocking an impressive 0:55.843" and Vicent Mayans "the fastest individual lap of the entire
event" at 9.405 s (retained in `agent-work/sources/monorace/event-records.md`). Neither is used. The 55.843 s
is a different race format over a different number of laps, and the 9.405 s lap is not established
to be over the A2RL knockout layout or measured on the same interval. The lap figure is worth
keeping in view anyway, because it is the only human per-lap number in the sweep and it sits above
MonoRace's 8.295 s normalized lap rather than below it.

### AI compute

`compute_method = operation_count`, following the Swift row exactly: matrix and convolution
arithmetic only, two operations per multiply-add, batch normalization, ReLU, max-pooling and the
sigmoid excluded, and the conventional parts of the pipeline — undistortion, adaptive cropping, the
QuAdGate corner detector, the homography outlier rejection, the PnP solve, the EKF and the 500 Hz
local filter — outside the AI-model total. No training or simulation compute is counted.

Script: `research/monorace/gatenet_flops.py`, run as

```
python3 research/monorace/gatenet_flops.py \
  --inputs research/monorace/monorace-inputs.json \
  --out <a fresh path outside this folder>
```

Standard library only; both paths explicit; it reads only the inputs file and writes only the output
file. `agent-work/derived/monorace/calculations.json` is the retained evidence and was produced by this
command; reproduce to a new path and compare rather than overwriting it.

**GateNet.** The paper's diagram with f = 4 gives channel widths 16, 32, 64, 128, 128 down and 64,
32, 16, 16 up, over a 384 × 384 input at five resolutions (384, 192, 96, 48, 24). Every block is two
3 × 3 convolutions. Per forward pass:

| Block | Resolution | FLOPs |
|---|---|---|
| inc (3→16→16) | 384² | 806,879,232 |
| down1 (16→32→32) | 192² | 1,019,215,872 |
| down2 (32→64→64) | 96² | 1,019,215,872 |
| down3 (64→128→128) | 48² | 1,019,215,872 |
| down4 (128→128→128) | 24² | 339,738,624 |
| up1 (convT 128, 128→64→64) | 48² | 585,105,408 |
| up2 (convT 64, 64→32→32) | 96² | 585,105,408 |
| up3 (convT 32, 32→16→16) | 192² | 585,105,408 |
| up4 (convT 16, 16→16→16) | 384² | 1,434,451,968 |
| five 1×1 heads | 24²–384² | 6,930,432 |
| **Total** | | **7,400,964,096** |

The encoder is 56.8% of this and is fully determined by the published diagram. `up4` is the single
largest block because it runs two 16-channel convolutions at full 384² resolution.

The transposed convolutions are counted as channel-preserving 2 × 2 stride-2 operations at their
input positions, which is what "adding the skip connections" requires: the upsampled tensor must
match the encoder skip's channel count for an addition to be defined. This is the same assumption
the Swift row's script already makes.

**G&CNet.** 2 × (24·64 + 64·64 + 64·64 + 64·4) = 19,968 FLOPs per call. The paper's text says 24
observations; its Figure 5 draws 20, which is also what the listed observation components sum to
(3 + 3 + 3 + 3 + 4 + 3 + 1). Using 20 lowers the per-call count by 512 FLOPs, which at 500 Hz is
256,000 of 666,096,752,640 per second, or 0.38 parts per million, so the discrepancy is recorded and
ignored.

**Per second and per race.**

- GateNet: 7,400,964,096 × 90 Hz = 6.6609e11 FLOPs/s
- G&CNet: 19,968 × 500 Hz = 9.984e6 FLOPs/s (1.5e-5 of the total)
- System: 6.66097e11 FLOPs/s
- One race at 16.59 s: **1.1050545126e13 FLOPs**

At the paper's own onboard timing of 16.56 s the total is 1.1031e13, a 0.2% difference. The
organizer time is used so that the AI and human durations come from the same clock.

The two figures are the same run. Figure 2 gives M16 one successful completion in four real
flights, with both its mean and its fastest completion time at 16.56 s, and Figure 1D shows M16
completing only once in the tournament, in semi-final heat 6 at 16.59 s. The footnote to Figure 1
attributes the discrepancy to the two timing methods.

### Scenarios for the assumed inputs

| Scenario | FLOPs per call | Race total | Ratio to central |
|---|---|---|---|
| Central: 3-channel input, 2 × 2 transposed conv, added skips | 7.4010e9 | 1.1051e13 | 1.00 |
| Grayscale (1-channel) input | 7.3160e9 | 1.0924e13 | 0.99 |
| 4 × 4 transposed convolutions | 8.3069e9 | 1.2403e13 | 1.12 |
| Concatenated rather than added skips | 9.0997e9 | 1.3587e13 | 1.23 |
| Concatenated skips and 4 × 4 transposed convolutions | 1.0006e10 | 1.4940e13 | 1.35 |

The band is 1.09e13 to 1.49e13. It is one-sided above the central value, because the two
architecture readings that would raise the count — concatenation and a larger upsampling kernel —
are both plausible departures from what the paper says, while the only downward scenario is a
grayscale input that the orange-gate segmentation task and the training pipeline's HSV colour
augmentation argue against. The concatenated reading is the likelier of the two upward ones: the
published ladder — 64, 128, 256, 512, 512 down and 256, 128, 64, 64 up, with the repeated 512 and
the repeated 64 — is the exact channel signature of the widely forked public U-Net implementation
with its bilinear flag set, and that implementation concatenates. The paper replaced the bilinear
upsampler with a transposed convolution, so its channel bookkeeping no longer follows the fork
either way, and the central here follows what the paper actually writes. A faithful port of that
implementation, with the transposed convolution halving the channel count before concatenation,
gives 8.099e9 per call and 1.209e13 per race, inside the band. This is considerably tighter than Swift's "roughly a factor of two",
because MonoRace publishes the channel ladder, the block structure and the scale factor explicitly.

`compute_evidence = derived_assumed_inputs`. The case for `derived_supported_inputs` is real — the
encoder, which is 57% of the arithmetic, needs no assumption at all — but the decoder's parameter
count is assumed and it moves the total by up to 35%, which is the kind of substantial assumed input
the field is for. The Swift row's identical situation is labelled the same way.

### Performance

MonoRace won the Grand Challenge, the AI vs Human challenge and the Drag Race, and placed third in
the Multi-Drone race for lack of collision avoidance. In the AI vs Human knockout the organizers
recorded MAVLAB's M17 at 17.18 s in the quarter-final against Vicent, who did not complete, and
M16 at 16.59 s in the semi-final against Killian Rousseau, who did not complete. The final against
Yuki Hashimoto records no time for either competitor, and the organizers classified MAVLAB first,
Hashimoto second and Cheremnykh third.

`performance_vs_human = above`. Both AI completions in the tournament are faster than every one of
the six recorded human completions; the gap to the best human run of the whole tournament is 2.55 s
on a 16.59 s run, or 15%. MonoRace never recorded a completion in the same heat as a human who also
completed — Vicent recorded no time in heat 1, Killian none in heat 6, and neither competitor did in
heat 8 — so every comparison here is cross-heat, over an identical unit, track and clock, and it is
the `different_attempt_selection` flag that carries that difference. Completion rates within the
tournament were similar on the two sides: MAVLAB finished 2 of its 3 heats, the four pilots 6 of
their 10. The paper's own framing is that the system was "outperforming all
competing AI teams and three world champion FPV pilots in direct knockout heats".

For context on reliability rather than speed, the paper's Figure 2 gives M16 one completion in four
real flights (25%) — its own heading, and a population with no human counterpart, since those four
trials include the 16.59 s semi-final run alongside practice — while the most conservative policy
M23 completed 38 of 43 flights (88.4%)
at a mean of 23.69 s. That mean is slower than each of the three pilot-best times this row uses and
slower than four of the six recorded human completions, but faster than the other two (24.07 and
26.01 s), and M23's own fastest completion of 22.75 s is faster than three of the six. The deployed
choice was the fast, fragile end of that trade-off. This does not change the label, which is about
the compared runs, but it is the main thing a reader should know about the AI's variance.

### Comparison issues

`different_inputs_or_tools; different_attempt_selection`.

**Inputs and hardware.** MonoRace sees one forward-looking 155° × 115° rolling-shutter camera at
90 Hz plus an onboard IMU, and derives its state from gate segmentation, a PnP solve and an EKF with
a drone dynamics model. A human FPV pilot sees an analog or digital video downlink from a comparable
forward camera in goggles, from a fixed position at the side of the track, with transmission latency
and no numerical state feedback. The AI additionally holds the gates' known geometry as a prior,
which the pilot holds only as learned track knowledge. Against that, the pilot has parallax-free
practice on the track and human recovery behaviour the AI lacks. On hardware, the AI configuration
is the organizer-supplied drone with 5.1-inch propellers, a race autopilot board, the camera and a
Jetson Orin NX companion computer; TU Delft's release captions the platform as "designed by the
organizers, A2RL and DCL for use by the AI teams and human pilots", but no source retrieved states
the human pilots' race configuration, and TII describes the autonomous drones as having "no onboard
human control capability". Whether the pilots carried the same companion-computer mass is therefore
not established, and the flag covers both the perception asymmetry and that open hardware question.

**Attempt selection.** Both sides are represented by a fastest completed run, but out of unequal and
small numbers of attempts under a knockout structure that gave each competitor a different number of
runs, and MonoRace's figure is its single completion in four M16 flights. Two of the three human
times used were flown against another human rather than against the AI.

Not flagged: `different_assessment` (one track, one rule set, one timing system, same timed
interval, same two-lap objective, same day) and `different_human_baseline` (the humans are the
pilots who actually raced the AI, in the same tournament).

### Monocular input versus the human feed and versus Swift

The brief asks this to be recorded explicitly, because it is what makes the row worth having next
to `robo-drone-swift`.

| | MonoRace (2025) | Human FPV pilot | Swift (2023) |
|---|---|---|---|
| Primary vision | One onboard forward camera, 820 × 616 at 90 Hz, 155° × 115° | One forward camera on their own drone, downlinked to goggles | Intel RealSense stereo pair plus a front-looking camera for gate detection |
| Depth | Monocular; recovered from known gate geometry through PnP | Monocular; recovered by learned judgment | Stereo VIO |
| External infrastructure | None permitted at any stage, including for tuning | None | Motion capture available in the hall; used to supervise the learned residual observation model |
| Inertial sensing | Onboard IMU, accelerometer saturating in high-g turns | Vestibular only, and not on board | Onboard IMU through RealSense VIO |
| Where the loop closes | On board, camera to motor commands | Over an RF video downlink to a pilot and back over an RF control link | On board |
| Track knowledge | Gate positions as a prior, refined from onboard data only | Learned from practice | Gate positions and a mocap-trained residual model |

Two consequences. First, the input parity with the human is closer than Swift's: the paper's stated
goal was to remove the motion-capture dependence and reduce to "a single forward-looking camera and
onboard inertial sensors", which is the pilot's sensory situation minus the downlink. Second, the
tracks differ — MonoRace flew a 76 × 18 × 5.4 m course and reached 28.23 m/s, against Swift's
30 × 30 × 8 m course at about 22 m/s — so the two rows are not two measurements of one task and
should not be differenced as though they were.

Numerically, MonoRace spends 6.66e11 FLOPs per second of flight against Swift's 6.67e10, almost
exactly ten times as much, from a GateNet that is 3.3× Swift's U-Net per call and runs at three
times the rate. Per lap that is 5.53e12 against 3.88e11, a factor of 14.2, the extra 1.4× being
MonoRace's longer lap. Per human-second the two rows sit at 5.56e11 and 6.04e10.

### Model record

New record `monorace-racing-system` in `candidates/monorace/models.csv`, following the
`swift-racing-system` convention: token fields `not_applicable`, parameter fields `not_applicable`,
because the row is an operation count over convolutional and fully connected workloads with no
shared per-token coefficient. `encoder_parameters` and `decoder_parameters` are also
`not_applicable` rather than carrying GateNet's two halves, because COLUMNS defines those fields as
counts "used in an operation-count recipe" and this recipe multiplies per-layer channel widths by
per-layer output grids rather than any aggregate parameter count. The counts therefore live in the
record's notes.

Architecture-derived parameter counts, for the record's notes rather than for any FLOP arithmetic
(weights only, biases and batch-norm affine parameters excluded, computed from the same ladder as
the FLOPs):

| Component | Parameters |
|---|---|
| GateNet encoder | 587,952 |
| GateNet decoder | 236,800 |
| GateNet 1×1 heads | 256 |
| GateNet total | 825,008 |
| G&CNet | 9,984 |

These come from `gatenet_parameters` and `gcnet_parameters` in
`agent-work/derived/monorace/calculations.json`, computed by the same script from the same ladder. Under the
concatenated-skip scenario GateNet's decoder would hold 335,872 weights and the total would be
924,080; the paper's "adding" wording is taken at face value here.

`model_release_date` is left blank. The paper makes no code or weights availability statement, and
no release of the evaluated system was located — the same disposition the Swift record carries.

---

## What was not built

- **The January 2026 A2RL championship** (UMEX, 21–22 January 2026) is a separate event on a
  different track where Minchan Kim beat TII Racing 5–4 and TII set a 12.032 s fastest lap. It is a
  second year of the same series and a plausible future row, but it is not MonoRace's result and
  none of the numbers here transfer to it.
- **A Grand Challenge row.** The 15-minute individual trial is the event MonoRace also won, but the
  humans did not fly it, so it has no human baseline of its own.
- **A per-lap row.** The halved figures are in `calculations.json` for comparability with Swift, but
  a per-lap row would restate the same evidence with an extra approximation, so only the per-race
  row is drafted.
