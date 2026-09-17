# AlphaStar training

## game-sc2-train-alphastar

Train the three AlphaStar Final race policies from random initialization through human-replay imitation, winning-replay fine-tuning and the 44-day league. The league includes all 12 learning agents: three main agents, three main exploiters and six league exploiters. The result is three separate policies, one each for Terran, Protoss and Zerg. Human work is the summed game-specific experience of three selected Grandmaster players, representing three race specialists. It is not three times the experience needed for one person to learn all races.

Central values: **7.5764e22 neural FLOPs and 17,075,108.6 human seconds** (4,743.1 person-hours). The sources establish Grandmaster-level performance for AI and humans, so `match` means a broad skill-level comparison. It does not imply identical opponents, game versions, or a measured human route to the exact 2019 AlphaStar policy.

### Original evidence

* [Vinyals et al., *Grandmaster level in StarCraft II using multi-agent reinforcement learning*](https://doi.org/10.1038/s41586-019-1724-z), Nature, 2019: main league/evaluation sections; Methods: Architecture, Supervised learning, Reinforcement learning, Infrastructure and Evaluation; Extended Data Fig. 6 and Table 1. `agent-work/sources/alphastar-training/alphastar-paper.pdf` is an archival copy of the original article, [retrieved here](https://gwern.net/doc/reinforcement-learning/model-free/alphastar/2019-vinyals.pdf). Publisher HTML and the [original DeepMind announcement](https://deepmind.google/blog/alphastar-grandmaster-level-in-starcraft-ii-using-multi-agent-reinforcement-learning/) are retained too.
* [Original supplementary data](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41586-019-1724-z/MediaObjects/41586_2019_1724_MOESM2_ESM.zip), retained as `alphastar-supp-data.zip`: `Supplementary Information/detailed-architecture.txt`, nested `pseudocode.zip` and `bnet.json`. The publisher's reporting summary is retained separately. The architecture describes input preprocessing, every major network block and five training-only baselines. The pseudocode establishes the frozen teacher and the three separate supervised learners.
* [Thompson et al., *Video Game Telemetry as a Critical Tool in the Study of Complex Skill Learning*](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0075129), 2013, especially Methods: Data Collection, Exclusion Criteria and Sample Characteristics; [authors' original SkillCraft data deposited at UCI](https://archive.ics.uci.edu/dataset/272/skillcraft1+master+table+dataset). Retained study HTML, metadata and `skillcraft.zip`.

The source manifest records URLs and SHA-256 hashes. No inherited point values are used.

### Human learning history

`SkillCraft1_Dataset.csv` contains 35 rows with `LeagueIndex=7` (Grandmaster), all with a numerical `TotalHours`. Those values are self-reported hours of StarCraft II play. Their mean is 1,581.0286 hours, median 1,250 hours and range 240–10,000 hours. We retain all 35 without an additional filter. The source paper excluded the Grandmaster group from its classifier analysis because it was small and mixed professionals with top casual players; the authors retained these records in the public dataset. The 55 professional replay records are a different group, with missing survey histories, and are not substituted.

`3 specialists × mean(35 Grandmaster TotalHours) × 3,600 = 17,075,108.6 person-seconds`.

This is a synthesis from individual histories, not 35 observed three-person teams. `successful` selects people who attained the Grandmaster learning endpoint; it does not filter their experience to winning games. `human_attempts=35` identifies the contributing histories. `world_class` describes the selected achievers, not an assumption that ordinary learners will reach their level at the same speed. Because the source cohort and game version differ from the 2019 target, `transferred_timings` / `estimated` / `point_estimate` are used.

Starting experience is material. The study's wider survey group had mean 4.07 years of StarCraft I experience; the 35 Grandmasters' individual predecessor-game histories are absent from the released table. The baseline therefore counts StarCraft II-specific play after starting the game with unspecified prior RTS experience. It excludes prior StarCraft I time, off-game study and coaching. Self-reports are not monitored active-time logs, and they measure accumulated experience at survey, not time of first Grandmaster attainment.

The source games are from 2011, mainly version 1.3.6; AlphaStar's 2019 evaluation used balance patch 4.9.3. Grandmaster historically means the top 200 regional players; AlphaStar's paper places its agents above 99.8% of approximately 90,000 active European players. The broad rank transfer is useful, but neither the league names nor those percentages establish identical difficulty. The races of the 35 survey participants are absent, so the three-specialist calculation assumes comparable learning effort by race.

The one 10,000-hour report raises the mean: removing only that report would give 14,400,847.1 seconds for three people; using the source median gives 13,500,000 seconds. Neither replaces the central all-record mean. The bounds come from the donor set's own dispersion instead. The mean is tail-driven: one 10,000-hour report out of 35 carries 248 of its 1,581 hours. The low is therefore the source median, 1,250 hours a person, 13,500,000 seconds, and the high recomputes the mean with one further report at the observed 10,000-hour maximum, 1,815 hours a person, 19,602,000 seconds. Neither is a confidence interval or a measured extra learning stage, and the excluded prior StarCraft I experience and off-game study push the same way as the high without being carried by it.

### Performance and comparison conditions

The original `bnet.json` has 90 AlphaStar Final games: Terran 18/30 wins, Protoss 25/30, Zerg 18/30; 61/90 in total. Their mixed opponent ratings mean this win percentage is not a win rate against a fixed Grandmaster cohort. The paper's fitted ratings put all three agents at Grandmaster level. The timing cohort's35 records also have verified Grandmaster league labels. These support broad `match` independently of how their duration is estimated.

AlphaStar uses structured lists of visible units and numerical attributes, not human visual perception. Extended Data Table 1 explicitly includes information humans must infer or remember, such as attack cooldowns and armour upgrades, and entities occluded by other entities. The camera and action-rate restrictions improve comparability but do not remove that difference. `different_inputs_or_tools` records it; `different_task` and `different_assessment` record the old-game/rank-cohort transfer. No generic embodiment flag is used.

### Workload

The paper's Infrastructure section reports about 50,000 processed agent steps per second per learner, 12 learner/actor setups and 44 days. It states that received trajectories are replayed twice. Treating twice as two total learner uses gives:

`12 × 44 × 86,400 × 50,000 = 2.28096e12 processed learner steps`;

`generated home-policy steps = 2.28096e12 / 2 = 1.14048e12`.

This uses the reported approximate rate throughout the run; it is not a recovered utilization trace. Scenarios vary the average rate 0.8–1.2× and replay reuse 2–3. The source's approximately 130 million league games would imply 8,773 home-policy steps/game under the central count. Because the paper does not provide per-game step totals for those games, this is a diagnostic, not a second workload to add.

The original `ActorLoop` in `pseudocode/alphastar.py` computes a student action, an opponent action, and frozen supervised-teacher logits inside each environment step. All three forwards are counted for every generated home step. The teacher is not another trainable league member. Old opponent snapshots also receive no separately duplicated gradient cost. The simplified pseudocode steps both sides together; the central estimate assumes equal home/opponent step counts, with 0.5–2× opponent-step sensitivity. Different action delays can change that ratio in the actual asynchronous implementation.

### Per-step operations

The source reports 55 million policy weights used during inference, 139 million during training. A plain 2P policy approximation would miss large repeated spatial and entity calculations. The calculator instead starts with 2×55 million operations for one use of each policy weight, adds repeated matrix applications beyond the first, then adds attention products that have no learned weights. This is an operation recipe, not a text-token coefficient.

| Repeated component | Source dimensions or assumption |
|---|---|
| Entity input projection | 512 slots, 3,585 input features projected to 256; width/projection convention borrowed from the reproduction below |
| Entity transformer | 3 layers, 2 heads, 128-dimensional Q/K/V;256→1,024→256 MLP; explicit QK and AV products |
| Entity output/scatter | 256→256 and256→32 matrices applied over entity slots |
| Spatial encoder | 128² map;52 preprocessed channels→32; stride2/kernel 4 convolutions to64²×64,32²×128,16²×128 |
| Spatial residual blocks | 4 blocks, 2 convolutions/block, 128 channels, kernel 3 at16² |
| Location decoder | 132→128 at16²;4 gated residual blocks; kernel 4 transpose convolutions 128→128→64→16→1, from 16² up to 256² |
| Unit-selection heads | Separate selected/target key projections; up to 64 recurrent selections with 32-dimensional keys/LSTM and 1024-dimensional autoregressive state |

The transposed-convolution arithmetic uses each input position's kernel applications, not the enlarged output area multiplied by a dense full kernel. Boundary and activation differences are within the explicit 3% remaining-operations allowance. All individual terms are in `calculations.json`.

The paper does not specify the complete categorical vocabulary width or the initial projection implementation. For those inputs only, the recipe uses the [mini-AlphaStar authors' original reconstruction](https://github.com/liuruoze/mini-AlphaStar), pinned commit `554206724da64b684308634fff54d3828a6114a2`: named full-size `AlphaStar_Arch_Hyper_Parameters.embedding_size=3585`, and `EntityEncoder.embedd` projecting it to 256. These are transferred implementation assumptions, not DeepMind disclosures. Its spatial/location implementation also supports the conventional two-convolution residual block. The disclosed original paper dimensions override the smaller reproduction's spatial/input scales.

The central count assumes all 512 padded entity slots and the full location/selection heads execute. The source describes missing-slot masks, but does not publish the compiled execution graph. If inactive heads or absent entities avoid computation, less work is done. The compact scenario uses 128 entity slots, 1,800 input features, 25% location-head execution and 8 selected units; the larger scenario keeps 512 slots, 4,500 input features and 10% remaining-operations allowance. The one-use 2P term stays as a small conservative allowance even when a head is skipped.

Central policy forward is **7.08746e9 FLOPs**. For training-only processing, the full 139−55=84 million parameter remainder is allocated one application per learner step, adding 168 million FLOPs. Detailed baselines consume scalar features and LSTM output rather than repeating the full spatial policy network. This allocation is a coarse allowance for value/baseline computation, not a recovered critic graph. Multiplying policy-plus-baseline forward cost by 3 approximates forward and backward training; 2.5–3.5 is tested. The policy's LSTM, one-use projections and ordinary heads are already included through the 55 million parameter term and are not added again.

### Supervised initialization and evaluation

The original paper reports 971,000 human replays, followed by fine-tuning on 16,000 winning high-MMR games. Its released `supervised.py` trains three race-specific policies from random weights, then fine-tunes them, but runs without a published stopping count. No numerical epoch count is presented as observed.

Central initialization assumes 10 passes and 1,635 action steps per player replay. The step scale comes from the SkillCraft study's mean moves/player/game; transferring 2011 human actions to 2019 filtered replay steps is approximate. Two player trajectories per replay are counted for the main dataset, one winning trajectory for fine-tuning. Across all three races this gives 31.7517 billion initial steps plus 261.6 million fine-tuning steps. Do not multiply those totals by three again: the race partition already exhausts the replay players.

The 10-pass prior comes from the mini-AlphaStar authors' README, which recommends 10 epochs after finding more prone to overfitting in their smaller experiment. It is not evidence of the actual AlphaStar schedule. The broad scenario varies 1–100 passes and 800–5,000 steps/player/replay. Initialization plus fine-tuning is 0.90% of the central total; its uncertainty does not dominate the central estimate.

Extended Data Fig. 6 shows 6,000 evaluator tasks for 192,000 concurrent training games. Assuming equal per-task progress, evaluator home steps are 6,000/192,000 of generated home steps. Each evaluation counts both policies' forwards, with no teacher. This produces 5.05194e20 FLOPs, 0.67% of total. Relative evaluator progress 0.5–2× is tested. The few hundred supervised/midpoint Battle.net checks are negligible within this allowance; the final 90-game performance attempt is not a separate learning stage.

The paper also mentions held-out validation agents trained to follow human strategies, without reporting their distinct training schedule or whether all share existing supervised weights. We allow one additional copy of the entire three-race supervised/fine-tuning budget for that training (0.90% of central total), varying zero to three such budgets. This is an explicit missing-helper allowance, not an invented number of measured validation agents. It avoids silently treating unidentified training as zero. Independent ablations, January's earlier AlphaStar, game-engine simulation and non-neural coordinator/data movement are excluded.

| Component | Central FLOPs |
|---|---:|
| All 12 league learners' updates | 4.96482e22 |
| Student rollout inference | 8.08310e21 |
| Opponent rollout inference | 8.08310e21 |
| Frozen teacher inference | 8.08310e21 |
| League evaluation | 5.05194e20 |
| Supervised initialization | 6.75116e20 |
| Winning-replay fine-tuning | 5.56224e18 |
| Held-out policy training allowance | 6.80679e20 |
| **Total** | **7.57641e22** |

No hardware peak is multiplied by an arbitrary utilization to set the central point. As a check, [Google's TPUv3 specification](https://docs.cloud.google.com/tpu/docs/v3) reports 123 TFLOP/s/chip and two cores/chip. The source 128-core learner and 128-core actor groups imply approximately 13.8% learner and 6.8% actor arithmetic utilization under this recipe. Those are consequences of the operation estimate, not measured AlphaStar hardware utilization. Different historical clock rates would change the utilization percentages, not this operation count.

### Sensitivity and reproduction

The compact-execution scenario gives 2.76695e22 FLOPs, compared with 8.36073e22 for the larger-execution scenario. Combining all low assumptions gives 1.61465e22; all high assumptions, including much more supervised/helper training, gives 2.28214e23. This wide envelope exposes execution and workload assumptions; it is not a statistical interval. The row is `derived_assumed_inputs` / `operation_count`.

Python 3 standard library only:

```sh
python3 research/recompute.py --sources sources --recipe research/recipe.json --output /absolute/path/to/new-alphastar-calculation.json
```

After publication use the actual directories, for example `--sources /path/to/dataset/sources/alphastar-training --recipe /path/to/dataset/research/alphastar-training/recipe.json`, and invoke the published script by its absolute path. The script verifies original-source hashes, reconstructs the 35 human records directly from the ZIP, reads native Battle.net results, and refuses an existing output or any output inside the source directory. It does not modify evidence.

The existing `alphastar-final-2019` model record is reused unchanged after checking its 55 million inference weights against the original paper. No token coefficient applies. The public availability of the exact final policies is not established; publication date is not substituted for release date.
