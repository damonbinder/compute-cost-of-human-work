# Circle-packing algorithm search

## research-vesper-openevolve-gpt52

The point covers the GPT-5.2/OpenEvolve condition in Table 1 of [Ishibashi et al. (2026)](https://arxiv.org/html/2605.15221v1). It searches for a program packing 26 circles inside a unit square, maximizing the sum of radii. The table reports averages of 1,671 generated algorithms per run, a 40M-token ceiling per run and the best valid score 2.41852 across two runs. Both searches count toward that selected result: approximately 80M tokens and 3,342 calls. This condition has no coding agent, no hack-detection agent and no database-observation agent. All candidate-generation work, including rejected candidates, is counted toward the final result. Post-hoc assessment is outside this work unit.

The source's rounded 23.9K tokens per algorithm implies 39.94M total; use 40M per run, 80M total, as the approximate consumed workload. Appendix A describes stateless calls with previous programs supplied in the prompt. Treat the unspecified total as full input plus output, with one call per algorithm and equal lengths for attention. No cache discount is claimed without its decomposition. This can overstate fresh-token work if cached tokens enter the total; call-length variation can change attention. The source's blended-price cost is an estimate, so the dollar field is empty.

## Human time

The human target is a valid program attaining the delivered score, not a new record. A numerical-programming expert can meet it with a simple construction, without an extended optimization campaign. Place 25 equal circles on a 5-by-5 square grid. The gap between four neighboring circles fits a circle of radius (sqrt(2)-1) times the large radius. Set the large radius to 2.41852/(25+sqrt(2)-1), approximately 0.0951641. All circles fit, and their radii sum to 2.41852. The calculation script checks every boundary and pairwise clearance.

Estimate **one hour** of active expert work: about 15 minutes to choose and derive the construction, 25 minutes to implement the required array-returning program, and 20 minutes to verify non-overlap, boundaries and score and resolve interface errors. This is a judgment estimate, not an observed timing. The bounds re-run the three components. The grid construction is immediate for a numerical expert, giving 5, 20 and 15 minutes, 40 minutes in all. One rework cycle on the array-returning interface and the scoring check gives 20, 35, 30 and 25 minutes, 110 minutes. A human could instead use a standard constrained optimizer; that does not justify charging days for a score already achieved by this elementary construction. The geometric check establishes the plausibility of the solution route, not the timing itself. Human comparison assumes comparable output quality by construction.

The original generated program was not released with this paper. Its post-hoc screen excludes scores over 3; it does not establish an independent geometric audit of this artifact. The reported 2.41852 is plausible, with no suspicious raw-score jump in this condition. Our geometric check verifies the human comparison route, not the AI artifact. The [OpenEvolve example](https://github.com/algorithmicsuperintelligence/openevolve/blob/main/examples/circle_packing/initial_program.py) was inspected for its centers/radii interface, but its current version is not asserted to be the experiment's starting revision. The human estimate includes implementing the interface from scratch rather than crediting an unverified starting program.

## Compute and model

Use the existing GPT-5.2 registry prior: 100B active parameters, 40–250B sensitivity, 52 attention layers and width 10,240. These are shared estimates, not disclosed architecture. The model is the paper's GPT-5.2, not its GPT-5.2-Codex conditions. The [release announcement](https://openai.com/index/introducing-gpt-5-2/) establishes first public availability on 11 December 2025.

For counted tokens T and call count K, Q=(T/K+1)/2 and F=T*(2N+4LHQ). Parameter-range endpoints recompute the shared estimated shape: dense=(N/196608)^(1/3), L=0.65*dense, H=128*dense. Q is held fixed because it is not obtained by the cache-implied route. These bounds exclude token/cache and human-time uncertainty.

Run `python research/vesper-calculate.py --inputs research/vesper-inputs.json --models models.csv --output calculation.json` from the package directory. The retained JSON contains the source quantities and assumptions. The script uses only the Python standard library and writes a new result.
