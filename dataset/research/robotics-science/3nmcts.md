**Disposition: unresolved compute. The architecture counts and two-hour matched-output human estimate remain useful, but the 50% neural-duty scenario below is not an accepted workload estimate. No active numeric row uses it.**

# 3N-MCTS: a ten-step drug-intermediate route

## sci-retrosynth-mcts

The work is the ten-step route in Figure 8 of the original [2017 manuscript](https://arxiv.org/abs/1708.04202v1), locally `agent-work/sources/robotics-science/3nmcts-v1.pdf`, page 18. This is a concrete complex intermediate with a heteroaromatic fragment and a cyclic peptide-like fragment. The displayed proposal includes functional-group changes, fragment coupling and ring construction. It resembles a published synthesis, but is a proposed route, without reaction conditions, experimental execution or yield verification. The source says this example was found autonomously within 30 seconds. We charge a 30-second search, including explored alternatives, rather than ten isolated network predictions. This is the original manuscript configuration, not an assumed later commercial product.

### Human work and quality

Estimate 120 minutes of active work by a synthetic organic chemist to produce a comparably detailed, plausible structural route from the target, with reaction references and building-block lookup allowed. The displayed target is considerably harder than a single retrosynthetic disconnection: its two branches must meet with compatible functionality and protection, and the cyclic branch requires a credible closure strategy. Allocate about 20 minutes to map the target and branch structure, 50 minutes to propose and check the ten transformations, 30 minutes to check precursor availability and branch compatibility, and 20 minutes to draw and reconcile the scheme. This is a two-hour central estimate, with roughly one to four hours plausible for familiarity differences. It does not include proving the chemistry in a laboratory or writing a literature-quality synthesis paper.

The match judgment targets the displayed provisional scheme. The paper's separate blinded study of 45 postgraduate chemists found no significant preference between literature and MCTS routes on nine equal-length route pairs; that supports plausibility but is not a measured human production time or a score for Figure 8. Record different assessment and different inputs/tools because the program has its extracted transform library and building-block database, while the estimated chemist uses conventional references.

### Compute reconstruction

Figure 10 reports: expansion input 32,681, hidden width 512, five highway layers and 301,671-way output; rollout input 8,192, hidden 512 and 17,134-way output; scope filter product input 16,384 through width 1,024 and five highway layers, plus reaction input 2,048 through width 1,024, followed by cosine/sigmoid. A highway layer has a transform matrix and a transform-gate matrix, with the carry gate tied to one minus the transform gate. Count multiply and add separately. Dropout is inactive at inference. Dense matrix terms give:

- Expansion: 2 × (32681×512 + 5×2×512² + 512×301671) = 347,619,328 FLOPs.
- Rollout: 2 × (8192×512 + 512×17134) = 25,933,824 FLOPs.
- Filter: 2 × (16384×1024 + 5×2×1024² + 2048×1024) = 58,720,256 FLOPs per reaction, before small nonlinear terms.

The source reports 90 ms and 10 ms for expansion and rollout inference, on the CPU of a 24-core host with one search thread and no GPU. These yield effective dense throughputs 3.862 and 2.593 GFLOP/s. We use their geometric mean, 3.165 GFLOP/s, as a central effective rate for the mixture of similarly structured fully connected networks. No CPU peak or 24-core multiplication enters the estimate.

Assume half of the 30-second search is spent executing neural arithmetic; the rest covers fingerprints, graph matching, rule application, tree traversal, Python/framework overhead and building-block lookups. This is material and unmeasured. The paper's top-50 expansion truncation and depth-25 rollout bound mean work is not just one network call per displayed reaction. As a plausibility check, about 46 expansion calls, 138 rollout calls and 460 scope checks would occupy roughly 15 seconds using source expansion/rollout latencies and filter throughput inferred above. Those are illustrative counts, not logs; caching scope-product embeddings or different search branching changes the mixture. We do not add them a second time.

Compute = 30 × 0.5 × sqrt((347619328/0.09)×(25933824/0.01)) = **47,473,936,195 FLOPs**, rounded to an integer. The reported-latency proxy includes ordinary nonlinear layers implicitly; the quantity being estimated is useful dense neural FLOPs, not arbitrary CPU instruction counts. Varying neural duty from 25% to 75% and throughput between the two reported-network rates gives 19.45–86.90 GFLOPs. Thus precision beyond about a factor of two is unwarranted. The 30-second allowance also avoids claiming the exact stopping instant from the phrase 'within 30 s'.

The model has no shared language-token coefficient; numeric feature dimensions are not tokens. No exact public weight-release date is established. Architecture-derived compute uses no total-parameter field.

## Further workload investigation

The original Methods state that the search phases continue until a time or iteration budget is exhausted and then select a route. This supports charging a complete chosen budget, but Figure 8 only reports finding the example within 30 seconds; it does not establish that its specific run used that exact budget or duration. The proposed 30-second charge was an assumption.

Comparable primary sources inspected include [AiZynthFinder 4.0](https://doi.org/10.1186/s13321-024-00860-x) and [Roucairol and Cazenave's search comparison](https://www.lamsade.dauphine.fr/~cazenave/papers/retrosynthesis2024.pdf), the latter saved in agent-work/sources/robotics-science/retrosynthesis-search-comparison-2024.pdf. They report search times, iteration limits and backend improvements, but not a matched three-network timing partition. AiZynthFinder's 1.7-fold speedup when replacing TensorFlow inference with ONNX constrains a backend-sensitive component, but that component includes framework overhead and cannot be equated to dense arithmetic in the original Theano implementation. The comparable planner also changes the rollout mechanism and model/filter use. Its runtime or iteration limit cannot serve as the missing call count for this ten-step example.

The reported 90/10 ms network latencies remain a useful throughput scale, but without a constrained count of evaluated molecules/reactions, the mixture duty fraction is not sufficiently established. Neither top-50 expansion nor depth-25 rollout is an average. Retain the original lead as unresolved rather than treating the illustrative calls as independent evidence. This is not a requirement for exact logs: a reasonably matched trace, documented call aggregate, or timing partition would suffice. Developer organizations are University of Münster and Shanghai University; the author names belong in citations.
