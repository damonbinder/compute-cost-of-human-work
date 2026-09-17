# Cassie: 100 m track running

## Work unit

A timed run ends at the finish line. Preparation and post-finish standing are excluded. This point compares racing performance, not merely eventual completion: the robot is slower than the world-class human baseline. It is an imperfect comparison with useful directly timed human evidence.

The [sprint paper, Sections II, V and VI](https://arxiv.org/html/2508.03070v1) reports three successful hardware times: 26.11, 24.37 and 27.38 seconds, plus two early falls. Only successful runs enter this compute mean. The controller runs at 40 Hz and outputs 10 joint targets. A separate standing policy operates outside the timed running interval. State includes 35 proprioceptive coordinates, phase, two gait parameters and forward-speed command. Operator commands are involved.

The [university announcement](https://news.oregonstate.edu/news/bipedal-robot-developed-oregon-state-achieves-guinness-world-record-100-meters) gives a best time of 24.73 seconds, whereas the paper table says 24.37. Retain the paper's full three-run set; using 24.73 instead changes mean compute by less than 0.5%. Neither is treated as the mean.

## Human time

The [Norwegian athletics federation's complete championship results](https://www.friidrett.no/siteassets/stevner/resultater/tidligere/documents/2009/berlin160809.html), final section, records all eight finishers in the Berlin 2009 men's 100 m final:

9.58, 9.71, 9.84, 9.93, 9.93, 10.00, 10.00, 10.34 seconds.

Sum 79.33 / 8 = **9.91625 seconds**. These are recorded race times, so evidence is task_timings; calculating their mean is other_calculation. World_class identifies the selected finalists. No general-population speed is inferred. Human starts use blocks and automated timing, unlike robot standing starts and hand timing; the large speed difference does not depend on those small timing differences. Race time includes reaction to the start signal.

## Compute

The sprint paper cites the predecessor's architecture but omits hidden sizes. [Siekmann et al., Section IV](https://arxiv.org/html/2011.01387v2) specifies two 128-unit LSTM layers at 40 Hz. Transfer those hidden sizes to the sprint controller; retain its explicit 10-output head rather than the predecessor's 30-output head. Assume two phase coordinates as in the predecessor, giving d=35+2+2+1=40 inputs. This is derived_assumed_inputs, not a disclosed checkpoint count.

Count one multiply and one add as two FLOPs. Four LSTM gates per layer, hidden size h=128:

- Layer 1: 8 h(d+h) = 172032 FLOPs.
- Layer 2: 8 h(2 h) = 262144 FLOPs.
- Output head: 2 h×10 = 2560 FLOPs.
- Total matrix work: **436736 FLOPs per policy call**.

Mean successful duration = (26.11+24.37+27.38)/3 = 25.9533333333 s.

Compute = 436736 × 40 × 25.9533333333 = **453390199.4667 FLOPs**.

This is approximate neural policy matrix work. Small gate nonlinearities, bias/state arithmetic and the conventional PD controller are excluded. One scalar phase instead of two changes the total by about 0.2%; hidden-size uncertainty matters much more. A doubled hidden size would increase the estimate by roughly fourfold. Training, controller development and trials outside the included three are excluded, as compute_subset states. No token count applies.

## Review questions

Check the architecture transfer and racing-performance interpretation independently. The human timing requires no estimate. Exact public release of the task-specific trained policy was not established; neither robot trial date nor later paper-upload date is substituted for it.
