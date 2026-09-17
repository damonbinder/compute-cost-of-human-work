# Mobile ALOHA: two complete manipulation tasks

## Sources and scope

Fresh primary sources: [paper](https://arxiv.org/html/2401.02117v1), [data-collection source](https://github.com/MarkFzp/mobile-aloha), [policy source](https://github.com/MarkFzp/act-plus-plus). Repository commits are in agent-work/sources/robotics-science/manifest.json. The selected model is ACT with static/mobile co-training, not diffusion or nearest-neighbour imitation. Task-level outputs include all subtasks, not just the action named in the old lead.

## Shared operation calculation

The paper's Table 6 specifies ResNet 18, three 480×640 cameras, transformer width 512, feedforward 3200, four encoder and seven decoder layers, and 45 action queries. Actual policy construction supplies 14 proprioceptive inputs,16 output actions, and a zero latent at inference. The training-only variational encoder is not evaluated. The image feature maps are 15×20 each, giving 900 image positions plus latent and proprioception =902 encoder positions. Four ResNet stages [64,128,256,512] with two basic blocks each are counted directly at their spatial dimensions. `calculations.py` records every convolution and attention-matrix term. Per forward pass:

- Three backbones: 3×22,206,873,600 FLOPs.
- Encoder: 37,876,957,184.
- Decoder: 10,286,925,824.
- Projections and heads: 472,689,664.
- Total: **115,257,193,472 FLOPs**.

This counts multiply+add as two operations. Normalization, activation, positional encoding and ordinary control arithmetic are omitted, a small approximation compared with the included convolutions/linear/attention operations. The same encoder memory projection is recomputed for each decoder layer, as the implementation does.

Crucially, this controller does **not** call its network at every 50 Hz action step. The paper describes chunk execution with base delay. `imitate_episodes.py` uses 45−13=32 control steps between calls on real hardware, and performs 10 network warmup passes at the start. We include those 10 passes in complete attempt compute. Each configured attempt therefore has ceil(episode_len/32)+10 calls. This is a configured full-attempt operation recipe, not measured mean run usage: early stopping could reduce some failed attempts. We use point_estimate/not_applicable for compute statistic/subset and ai_attempts, while recording empirical task success independently.

## robo-cabinet-aloha

Work: approach and open both doors, grasp the pot, place it in the cabinet, and close the cabinet. Co-trained ACT completed 17/20 evaluation attempts. The public task configuration uses 1500 control steps (30 seconds); 47 operational calls +10 warmups =57 calls; **6,569,660,027,904 FLOPs**.

Human baseline is the paper's actual eight-participant teleoperation study, final fifth trial: mean **36 seconds**. Participants were computer-science graduate students aged 21–26, all new to Mobile ALOHA, with mixed prior teleoperation experience, after 3 minutes familiarization and an expert demonstration. We classify novice for this short task-specific training. These are eight recorded participant task-completion timings, not the autonomous training demonstrations. The whole human task uses the same robot and interface without neural autonomy, so it is not an unaided freehand kitchen timing. General setup and previous learning are excluded. The paper plots completed trials and reports their mean; treat the timing subset as successful, without inventing a human total-attempt success rate. Robot 17/20 completion is broadly comparable to successful novice task delivery, but no formal equality of reliability is established. The human and robot scopes include closing the doors.

## robo-shrimp-aloha

Work: add oil to the pan, add one shrimp, manipulate/flip it with a spatula, and transfer it into the bowl. The paper evaluates completion of these actions; it does not establish a temperature or food-safety endpoint. Co-trained ACT completed 2/5 attempts. It specifies a 75-second task, matching the public truncated 3750-step configuration. 118 operational calls +10 warmups =128; **14,752,920,764,416 FLOPs**.

No direct freehand human timing is reported. Estimate **40 seconds of active work** for an ordinary home cook with the ingredients, hot pan, spatula and serving bowl already positioned as in the scene: oil handling/pouring/replacing 5 s; take and add shrimp 5 s; acquire spatula and approach the pan 5 s; position and turn shrimp 8 s; use pan/spatula to transfer into bowl 12 s; release/reposition utensils 5 s. These are an explicit motor-work estimate, not sampled observations. They cover the task's whole action sequence and allow deliberate handling of a small slippery item. Passive preheating/cooking waits and kitchen cleanup are excluded for both work definitions. A 20–60 s active range is plausible depending on placement and handling. Typical humans should carry out this ordinary sequence more reliably than 2/5; classify AI below against that assumed task baseline, not match merely because time was estimated.

The configured neural workload is an assumption about a complete attempted episode, not the observed mean of the 5 performance trials. The nontruncated 4500-step task is not selected because it does not match the paper's 75-second description. Current cabinet source includes supplemental datasets; we transfer its episode length/delay recipe to the paper configuration rather than claim the fetched code is the evaluated checkpoint.

## Model release provenance

The fresh public repository READMEs provide hardware, data collection and checkpoint-training/evaluation instructions, but do not establish a release date for the exact co-trained evaluation weights. The model release date remains blank; the January 2024 paper date is not substituted for a weights release.
