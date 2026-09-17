# ACT / ALOHA manipulation: initial tranche

Original sources: [Zhao et al.](https://arxiv.org/pdf/2304.13705), sections IV-C, V-A/B, Figure 6, Table II, Appendix C/Table III; [ResNet paper Table 1](https://arxiv.org/pdf/1512.03385). Task sequences were inspected through their detailed Figure 6 descriptions, not inferred from titles.

Reported shared facts: ACT processes four 480×640 views with ResNet18, yielding 1200 spatial features plus joints and style inputs. Its transformer has width512, feedforward3200, four encoder and seven decoder layers, and 100 action positions. Temporal ensembling queries every control step, at 50Hz. Expert demonstrations last 8–14s across tasks. There are 50 demonstrations per task here. ACT is evaluated 25 times per task.

## Work and human estimate

Estimate the FULL evaluation horizon, not time to first successful completion. The [original project page](https://tonyzhaozh.github.io/aloha/) states episode lengths of600–1000 steps for the displayed policies. The [public ALOHA task config](https://raw.githubusercontent.com/tonyzhaozh/aloha/main/aloha_scripts/constants.py) specifies1000 for aloha_wear_shoe and DT=.02. The [ACT evaluator](https://raw.githubusercontent.com/tonyzhaozh/act/main/imitate_episodes.py) imports this setting, loops max_timesteps even after successful completion, and queries each step with temporal aggregation. Therefore use1000 calls for shoe. Current code is not a preserved log of thepaper's25trials; this is a supported configuration transfer, not measured paper FLOPs.

Bounded cup search: thepublic constants list only shoe, while theproject page gives a600–1000-step range spanning its demonstrated tasks, including cup. Use the midpoint800steps for a full cup evaluation episode, rather than transferring8–14s successful human demonstration time. This gives a16s nominal horizon with a12–20s supported range, or±25% compute. This remains a cross-task AI-horizon estimate because cup-specific config was not located. The public demonstration horizon is stronger evidence than teacher execution duration.

Human duration remains the cross-task8–14s midpoint11s, not a measured task mean. Human demo completion and full AI evaluation horizon intentionally differ; the AI may keep issuing commands after completion. AI attempt counts remain not_applicable for the analytic workload. The human timing donor consists of 350 retained real-robot demonstrations across the six tasks (five sets of 50 and one of 100), all collected by one operator. Use human_attempts=350 and human_time_subset=successful: the retained demonstration duration excludes the operator mistakes and resets described in Section V-B. These are not 350 timed cup or shoe trials.

The human operates the same hardware through ALOHA. This avoids interpreting teleoperation time as bare-hand time. Successful demonstrations provide the human target. Cup's84% success is labeled below; shoe's92% is broadly comparable and labeled match, with different_attempt_selection; no all-attempt human success rate is claimed.

## Architecture operation calculation

Let S=1202 visual/joint/style positions, K=100 action queries, D=512, F=3200. Count multiply-add as two operations. Four ResNet18 backbones cost approximately

`Ccnn = 4 × 2 × 1.8e9 × (480×640)/(224×224)`.

The ResNet paper's nominal 1.8 billion operations are multiply-accumulate counts (also reproducible by summing Table1 conv shapes); scale by area. This neglects minor boundary rounding and removes neither tiny classifier nor pooling contributions, making it an approximation.

Transformer encoder: `Ce = 4 × (8SD² + 4SDF + 4S²D)`.

Transformer decoder, retaining both self and cross attention: `Cd = 7 × (12KD² + 4SD² + 4KDF + 4K²D + 4KSD)`.

Input/output projections: `Cp = 2×1200D² + 2×(14+32)D + 2KD×14`.

`Cforward = Ccnn+Ce+Cd+Cp = 159,701,336,858.12244` FLOPs. The last reported digits have no precision significance. Multiply by800 for cup (`127,761,069,486,497.95` FLOPs), or1000 for shoe (`159,701,336,858,122.44` FLOPs). All four image models are included. The training-only CVAE encoder is discarded at inference. Norms/activation/softmax and small non-model controller arithmetic are omitted.

Main text specifies 512 feature channels; an Appendix C diagram prints 728. We use the main text's standard ResNet18 output of512, treating the figure value as an inconsistency. A 728-to512 projection changes only a small fraction of total compute. The rough 10ms GPU latency was investigated, but not used: unspecified precision/utilization would create a less defensible FLOP conversion.

## act_cup_episode

Inputs: cup randomized on a15cm line. Tip it into the other gripper, lift, pry the lid open. ACT final success84%=21/25. Human11s, AI1.278e14 FLOPs.

## act_shoe_episode

Inputs: shoe randomized on a15cm line, fixed mannequin foot. Lift, insert with heel seated, support and secure velcro strap. ACT final success92%=23/25. Human11s, AI1.597e14 FLOPs.

The shared human timing estimate does not imply equal task difficulty. The AI horizons are independently anchored in deployment evidence; exact paper-run trajectories would improve precision. No distinct learning row is inferred from demonstration minutes: these are teacher performance time, not learner acquisition time.

Theproject page specifies chunk90 while paper TableIII and released architecture default use100. Theoperation recipe retains100, transferring thehorizon evidence across this small config difference. ChangingK from100 to90 reduces per-call FLOPs by approximately0.6%, substantially smaller than cup horizon uncertainty.

The donor-count audit additionally retained original ACT/Ahn/Bindemann evidence in agent-work/sources/timing-donor-audit/.
