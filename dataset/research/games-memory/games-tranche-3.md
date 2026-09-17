# Go and simulated racing: inference

Three new candidates; earlier five rows remain unchanged. FLOPs count model execution with multiply and add separate. The racing rows describe real-time gameplay, not physical driving. Training, rendering and game simulation are outside their inference scope. Numerical recipes and sensitivities are in calculations-tranche-3.json and calculations-tranche-3.py.

## gt2020

Primary source: [Fuchs et al.](https://arxiv.org/html/2008.07971v2), §III-B architecture, §IV conditions, Table I performance, §VI-B evaluation frequency and §VI-H version limitation. Setting A uses Audi TT Cup2016. Its best AI lap is75.913s; best human76.062s. This tiny gap supports broadly comparable elite performance, despite the paper's superhuman title. The source's later-update experiments cannot be pooled with these historical timings.

The deployed policy has two 256-unit hidden layers and two control dimensions. Table II gives 13 rangefinders and 10 curvature measurements; §III-B gives velocity3, acceleration3, heading1, prior steering1 and contact1. Together these are 32 inputs. Evaluation operates at60Hz; training at10Hz. Count a Gaussian mean and scale for each of the two control outputs (four scalar outputs). The total learning-system parameter count is not needed to establish the actor width. Only the actor runs during deployment.

Recipe: `2*(32*256 +256*256 +256*4)`, plus hidden biases/ReLUs and100 operations for output transformations, gives150,632FLOPs/action. Multiply by60Hz*60s. Only the actor runs during deployment. Using the entire advertised parameter total would substantially overcount.

Human60s is the task's specified duration, not a completion-time estimate or recorded-attempt statistic. `work_rate` encodes one minute times60seconds/minute. The performance observation is race speed; neither human nor AI completion probability is being inferred. Precision of numerical state versus human visual input is flagged.

## sophy

Primary source: [Wurman et al. author PDF](https://sam.barrettnexus.com/publications/papers/nature22.pdf), printedpp.227–229/main Fig.3 and Methods: Game environment, Actions, Features, Training algorithm, and Human–agent differences. October2021 team result104–52 supports above-world-class race performance. Do not use the July network or July time-trial results to establish this architecture's performance.

October policy: four2048-unit hidden layers,10Hz actions, two Gaussian control dimensions. Course geometry contributes60 3D positions on each of three lines, hence540 inputs. Vehicle, track and control state add roughly28; nearby cars add relative position, velocity and acceleration. Exact packed feature width is not reported here. The agent gets numerical state; humans can additionally control gearing/traction.

**Our reconstruction:** use640 inputs, approximately568 base plus up to eight9-component opponent slots. This is a rounded allowance, not a claim that eight slots were used. Even568–740 inputs changes the total only−1.1% to+1.5%, because the three2048-square hidden matrices dominate. Four Gaussian outputs and small bias/activation/output-transform allowances give27,820,136FLOPs/action;600 actions give16,692,081,600FLOPs per minute. Dropout and feature arithmetic are small relative to the matrices; no Q/value network is needed for acting. Use derived_assumed_inputs because exact input packing is unresolved.

Human60s is exact by the normalized gameplay unit. Team race performance is transferred to one car's minute of control; this does not claim that every minute or car won. It is the same deployed policy and racing activity. No attempt counts apply to either analytic duration or operation recipe.

## alphagozero

Primary source: [Silver et al. original paper](https://ai6034.mit.edu/wiki/images/Nature24270_AlphaGoZero.pdf), Fig.3a; Methods Neural network architecture, Evaluator, Self-play and Evaluation. Fig.3's20-block three-day learning curve uses0.4s searches and ends above AlphaGo Lee. Evaluator/self-play use1600 simulations. The Elo scale is anchored through human matches. The separate100–0 match used long tournament clocks and is **not** the performance result attached here.

The20 blocks mean one stem plus19 residual blocks, each with two convolutions. Inputs19×19×17, width256. Policy head:1×1conv to2channels then722→362. Value head:1×1conv to1channel then361→256→1. Random symmetry is one transform per leaf, not an eight-pass ensemble.

**Our arithmetic:** spatial MACs sum the stem,38 residual convolutions and both heads. Count two operations/MAC, inference batchnorm as scale+offset, ReLUs and skip additions. Result16,224,527,019FLOPs/evaluation.Ordinary tree reuse retains the next root between moves. The nominal 1600 evaluations give25,959,243,230,400FLOPs/move; do not add a fresh root evaluation on every move. Terminal leaves may avoid a network call; this is the nominal search recipe, not profiler output. Integer Go rules and tree bookkeeping are not represented as floating-point neural compute.

**Human-time evidence and judgment:** [Fan Hui’s DeepMind-published game-1 commentary](https://deepmind-media.storage.googleapis.com/alphago/pdf-files/english/ls-vs-ag1/LS%20vs%20AG%20-%20G1%20-%20English.pdf), PDF pp.17–22, reports Lee’s remaining minutes as90 after move57,87 at61 and83 after73. AlphaGo has78 minutes after73. Both began with120 minutes. Lee’s first smoking break is described after77 (PDF p.24); the selected prefix precedes it.

These rounded, overlapping prefixes imply own-clock averages of62.1,63.9 and60seconds per Lee move, not independent timing samples. Through move73 there are37 Lee moves: his own clock consumes37minutes and AlphaGo’s42minutes. Own-clock effort is60seconds/move. Adding half the opponent’s clock gives94.1seconds; full engagement gives128.1seconds. These are engagement scenarios, not measured active-thinking durations or confidence bounds.

Select **60seconds**, Lee's own clock, with **60 to 128.1seconds** as the range. The 120-second central this replaces was 94% of the whole elapsed move cycle, and the engagement fraction that justified it is not measured; the own clock is. Under the convention stated in `chess.md#the-clock-convention` and applied on 2026-09-17, the own-clock reading is the central, the own-plus-opponent reading is the ceiling, and the low sits at the central because in a title match idle time inside the player's own turn is small and thinking on the opponent's turn is nonnegative. The derivation is in `../alphago-zero/alphago-zero.md#human-active-time`. This transfers an early-game prefix from one long-clock match to a representative elite move; it does not claim a measured full-game mean. Classify transferred_timings/estimated/point_estimate, with 37 contributing human move attempts, subset all, timed cumulatively in one game prefix. The overlapping clock checkpoints do not add new attempts. Performance remains above, based on Fig.3’s human-anchored Elo assessment, not on a claim that additional human time guarantees matching AI quality. Keep different_assessment for that transfer.

## Review status

The initial snapshot is in snapshots/tranche-3-before-review. REVIEW-3.md requested the directly supported Fuchs feature count, ordinary Go root reuse and a sourced human-effort transfer. Those corrections are applied here. Sophy’s row and research section are unchanged. The Go engagement assumption is settled by the 2026-09-17 clock convention: 60seconds central and ceiling 128.1, with 94.1 an interior reading.
