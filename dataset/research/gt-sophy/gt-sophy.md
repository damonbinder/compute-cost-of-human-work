# GT Sophy: a source-defined time-trial lap

## Source and overlap

Original [Wurman et al. Nature paper](https://www.nature.com/articles/s41586-021-04357-7), freely hosted in full with supplementary material by [coauthor Peter Stone](https://www.cs.utexas.edu/~pstone/Papers/bib2html-links/nature22.pdf), retained as agent-work/sources/gt-sophy/paper.pdf and paper.txt. Sources/figure1.png renders the complete original Figure1 page at200dpi; timings are read only to0.1s, not invented millisecond precision. The original [author repository](https://github.com/SonyResearch/gt_sophy_public) provides October race videos; its tree and README are retained. No race video was downloaded or timed.

The existing game-gt-sophy-minute row describes **October head-to-head racing**, with a four-hidden-layer policy. This proposed July2 time-trial observation instead uses two hidden layers and a measured lap work unit. It is a distinct policy/task setting, not a rescaling duplicate. Preserve the October row. Its source independently supports10Hz, four2048-wide hidden layers, two Gaussian action dimensions and the October104–52 team result. Its approximate640-feature allowance is explicitly uncertain; hidden matrices dominate. Its normalized60-second duration is a defined unit, not an observed lap time. The before/ CSVs preserve that original row/model untouched.

## Human and AI laps

Main Figure1e shows100 laps from the July2,2021 time-trial policy on Lago Maggiore GP. The paragraph “Time trials” states that this mean is about equal to the fastest recorded human lap; the comparison uses the same car. Figure1d describes over17,700 human best-lap records, and1e isolates the fastest five. These are leaderboard best laps, not17,700 timed attempts contributing to our selected human value.

Visual reading of the0.1-second x-axis in1e puts the fastest human marker around114.18s and the AI histogram center around114.2s. Retain **114.2s for each**, rounded to the plot's reliable precision; do not treat the two rounded numbers as equality of exact clocks. The source's own text supports broad match. Human n=1 is the selected fastest recorded lap; the number of earlier attempts that driver made is not reported or counted. AI n=100 is explicitly given in the caption. The AI mean includes those100 plotted laps; no inference is made about other failed training/evaluation laps outside that plotted sample.

Human time is direct recorded task timing read approximately from a plot (`task_timings`, `reported`), with `point_estimate` indicating a single approximate selected value rather than a sample mean. `successful` means this is a valid selected best lap. All prior practice and earlier unsuccessful attempts are outside this one-lap inference comparison. The different-attempt-selection flag is essential: mean AI versus best human does not compare average human reliability. Both sides use the same lap-time scoring, so no extra different_assessment flag is added solely to restate this selection difference.

The numerical-state/map input advantage is concrete. Humans drive from the rendered view; the AI receives state and track geometry. Conversely humans can change gearing, traction control and brake balance, which the API did not permit the AI to control. Those differences belong in different_inputs_or_tools. No human-learning claim is made.

## Policy operations

Main Figure2 caption explicitly identifies the July2 time-trial network as2048×2; the Methods four-layer description and supplementary network table concern **October competitive racing**. Do not apply the October architecture to July laps. Methods “Game environment” states10Hz actions. “Actions” describes two continuous controls with Gaussian means and diagonal variances, giving four scalar policy outputs. Only the policy acts; the two Q-networks/target copies are training machinery, not inference helpers. Map transformations, game physics and controller bookkeeping are not neural helper calls.

The listed course representation is60three-dimensional points on each of three lines:540 coordinates. Reconstruct a central568 input features:9velocity/angular-velocity/acceleration components,4tyre loads,4slip angles,2progress sine/cosine terms,1surface-inclination scalar,3orientation components,2barrier/off-course flags and3previous-control scalars, plus540course coordinates. The source does not publish exact tensor packing or orientation representation.568 is an explicit estimate;560–580 tests this small first-layer ambiguity. Time-trial inputs do not add racing opponent slots.

Dominant matrix arithmetic at one multiply and one add per weight:

`2 × (568×2048 + 2048×2048 + 2048×4)`.

Add4,096hidden bias additions,4,096ReLU operations,4output biases and a20-operation allowance for squashing/variance transforms. This is10,739,736FLOPs/action. Sampling/dropout and standardized feature arithmetic are negligible relative to the matrices and not measured op traces.10actions/s×114.2s gives1,142 nominal policy calls per mean lap, hence **12,264,778,512FLOPs**. Rare network delays and plot rounding make this a reconstructed mean, not an exact recorded call count. Input dimension560–580 changes the result by less than0.5%; half a plotted tenth changes duration-derived work by0.044%. No training, self-play or critics are added to this inference point.

The July checkpoint was private. Publication on February9,2022 is not its public model release; neither is the later commercial Sophy release. New model release fields remain blank, all text-token coefficients not_applicable.

## Reproduction

Python standard library only:

```sh
python3 /path/research/recompute.py --sources /path/sources --output /path/new-calculations.json
```

The script reads retained sources for hashes, reconstructs the arithmetic from explicit inputs, refuses existing outputs and refuses writes inside sources. It does not run a policy, solve a benchmark, estimate timings from video length, or claim automated plot digitization. Its source-defined lap-time inputs are the documented rounded visual readings.
