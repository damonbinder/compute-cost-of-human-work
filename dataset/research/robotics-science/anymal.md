# ANYmal perceptive locomotion: Etzel hiking loop

## robo-terrain-anymal

Primary source: [Miki et al., original paper](https://arxiv.org/html/2201.08117v1), hiking experiment, deployment section, Supplement S5–S6. The selected work is the entire 2.2 km Etzel loop with 120 m elevation gain. This concrete route replaces the unspecified terrain traversal in the lead.

The robot finished in 78 minutes, including stops to reattach a shoe and replace batteries. The cited planner gives 76 minutes for human hikers; the summit sign gives 35 minutes, but that covers only part of the route and is not used. Human time is therefore a route-planner estimate, not observed human trials: 76×60 = 4,560 seconds. It represents an ordinary capable hiker, rather than a world-class runner. No participant count is invented. The robot completed the route at broadly human hiking pace without locomotion failure; classify match for route traversal, while documenting the maintenance assistance and different sensing/body. The paper does not measure reliability across repeated whole-route trials.

## Inference operation count

Table S3 gives 133 proprioceptive features and 208 height samples (52 per foot). Supplement S6 gives four shared-weight height encoders, each 52→80→60→24; a two-layer GRU with 50 hidden units; belief and gate heads 50→64→64→120 and 50→64→64→96; and the student actor (133+120)→256→160→128→16. The GRU first layer input is the 133 proprioceptive features concatenated with 96 encoded heights, hence 229. Matrix multiply-adds count as two FLOPs; each GRU layer has three gates, giving 6×(input×hidden+hidden²). The privileged-information teacher encoder and reconstruction decoder are training/introspection components, not deployed inference, and are excluded. Conventional elevation-map processing and inverse kinematics are not neural model FLOPs.

Use the reported 50 Hz policy rate across the 78-minute route as a full-route workload approximation. Maintenance downtime is not separately timed, so this can modestly overcount active policy calls. The operation calculation in build_tranche2.py gives the exact central total. No learned visual backbone is added: depth/LiDAR point clouds feed the geometric elevation map. Minor activations/normalization are omitted.

## Release provenance

The paper describes the deployed architecture and training, but no exact evaluated weight release date was established from its data/material availability statement. Leave model release date blank instead of substituting the January 2022 paper date.
