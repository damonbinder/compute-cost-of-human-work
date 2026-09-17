# Game training

*Last revised 2026-09-14 17:07.*

This batch reconstructs learning costs from the original training papers and human experience studies. Human experience among people who reached a rank is not a prediction that every beginner can reach it in that time.

## game-dota2-train-openaifive

### Work and comparison

Train the shared OpenAI Five policy from random initialization on 30 June 2018 to the checkpoint that beat OG 2–0 on 13 April 2019. The policy controls five heroes with shared weights and separate recurrent states. This is the paper’s reconstructed retained training lineage, including its changing architecture and environment. Its simplified history excludes computation before the last restart; it does not recover all actual June–April project expenditure. It is not the later Rerun experiment, the entire research project, or inference during the subsequent public Arena.

The human comparison is the summed Dota 2 playing and practice time of the
**five players who lost that match**: Johan "N0tail" Sundstein, Sébastien "Ceb"
Debs, Jesse "JerAx" Vainikka, Anathan "ana" Pham and Topias "Topson"
Taavitsainen, the reigning International champions. The five-person quantity
reflects the learned team capability, not five independent AI networks trained
from scratch. The estimate counts Dota 2 play and game-specific practice,
excluding earlier DotA and other games. `human_skill=world_class`.

The AI evaluation used a restricted 17-hero pool, with several scripted actions and direct semantic state observations; the humans played ordinary Dota. These are concrete task and input differences. The practice rate behind the human time is measured on a different esports population, recorded as `different_human_baseline`. The paper describes an approximately 217 ms AI reaction time, not the earlier system's 80 ms figure.

### Human calculation

The quantity is the hours these five people spent actually playing and
practising Dota 2 while learning it, to the level the run demonstrated:
beating the reigning International champions. It is career span times a
measured professional practice rate.

**Span.** Each player's Dota 2 career to April 2019 is documented.
[N0tail](https://en.wikipedia.org/wiki/N0tail) moved from Heroes of Newerth to
Fnatic's Dota 2 team on 30 March 2012, seven years.
[Ceb](https://en.wikipedia.org/wiki/Ceb_(gamer)) began competing in 2011 with
Team Shakira, eight. [JerAx](https://en.wikipedia.org/wiki/JerAx), also out of
Heroes of Newerth, started with Rat in the dark in 2013, six.
[ana](https://en.wikipedia.org/wiki/Ana_(gamer)), born 26 October 1999, played
heavily enough to leave school before joining Invictus Gaming's in-house league
in 2016, and is credited with six.
[Topson](https://liquipedia.net/dota2/Topson) played Dota from childhood and
turned professional at the end of 2016, and is credited with eight. The mean is
**7.0 years** a player.

**Rate.**
[Pluss et al. (2022)](https://doi.org/10.1016/j.chb.2022.107421) recorded
game-specific practice weekly for 52 consecutive weeks from 30 Counter-Strike
players, and the 18 professionals among them averaged **30.9 ± 8.2 hours a week**
of total game-specific practice, of which 19.6 ± 6.9 was competitive play. It is
the only year-long measurement of a professional esports practice week, and the
52 weeks include the off-season, so it is already a year-round figure.

`7.0 years × 52 weeks × 30.9 hours = 11,248 hours = 40,491,360 seconds` for one
player (the five spans are 7, 8, 6, 6 and 8 years; the mean is used). One policy
plays all five heroes, so the human counterpart is one person learning the game,
not the team's summed careers; the team sum of 56,238 hours was the first
reading and is rejected (Damon, 2026-09-15).

Two cross-checks, one on each side. ana is documented as having played 10 hours
a day or more before turning professional, 70 hours a week, which over the same
span puts one player at 25,500 hours; the measured rate
is conservative against it. In the other direction, the
[Röhlcke et al.](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0206555)
cohort of 30 players at MMR 5,000 or above reports a mean 5,264.4 games, which
at the paper's typical 40-minute game is 3,510 hours a player; 11,248 is 3.2
times that, the right ordering between a 5,600-MMR amateur and a world
champion. The scenarios are 8,300 hours at a standard deviation below the
measured rate and 25,500 at ana's documented rate.

`human_time_evidence=llm_estimate_from_data`: the rate is a recorded timing of
another population mapped onto this one, and the donor sample is Pluss's 18
professionals. The one-player figure is a point estimate. Nothing here fills
in unmeasured experience in predecessor games, and nothing measures the extra
practice needed to form a coordinated fixed team.

**Superseded: 63,172,400 seconds (17,548 hours).** The first version priced five
Röhlcke achievers at 5,264.4 games and 40 minutes a game, on
`llm_estimate_judgment`, with 47,379,300–94,758,600 seconds as its scenario band
and 60,000,000 at the source median. It is superseded because the endpoint it
measures is 5,000 MMR, not the champions the AI beat: the definition charges the
hours to the level the run demonstrated. The new figure is 3.2 times higher, and
the row's `human_skill` moves from `expert` to `world_class`. The retained
workbook selection is kept in `five-calculations.json` and the cross-check
above.

### Neural compute

Original source: [OpenAI, *Dota 2 with Large Scale Deep Reinforcement Learning*](https://cdn.openai.com/dota-2.pdf), especially §3.2, §4.1, Appendix A, Tables 1–2, Appendix H, Appendix J, Appendix M.3 and Appendix N. Retained as `agent-work/sources/games-training/openai-five.pdf`.

The three counted parts are:

| Part | FLOPs | Basis |
|---|---:|---|
| Optimization | 6.6528e22 | Source's 770 PFLOP/s-days × 86,400 × 1e15 |
| Training-game policy inference, both sides | 2.4640e22 | Source optimization, sample reuse and a forward/backward estimate |
| Training evaluation | 1.1555e20 | Source evaluation cadence; estimated game duration and forward cost |
| **Total** | **9.1284e22** | Sum of all three parts |

**Optimization.** Appendix A profiles the changing TensorFlow graphs per segment and multiplies by actual optimization steps and GPU count. Its April 13 value is 770±50 PFLOP/s-days. This already includes the policy/value network, auxiliary heads, metric logging and numerical checks; do not multiply by five heroes again. The source uses a simplified retained history rather than a complete event ledger. Appendix A explicitly excludes computation before the last restart; the count must not be described as fully recovering restart/revert expenditure. The later 820 PFLOP/s-day value ends April 22 and is not substituted here. Appendix A explicitly excludes rollout inference. Its dollar-budget percentages do not measure FLOPs and are not used to multiply this number.

**Rollouts.** Appendix M.3 defines sample reuse as consumed training samples divided by incoming samples. Table 2 gives a fluctuating 0.8–2.7 for this run. Let R be the effective reuse and q the share of simulated hero trajectories supplying current-policy training data. With forward-plus-backward approximately three policy forwards,

`rollout FLOPs = optimization FLOPs / (3 × R × q)`.

Both teams' policy computations are included. Section 3.2 and Appendix N report 80% current-versus-current games and 20% current-versus-past games. Assuming both current teams' trajectories are eligible in self-play, but only the current side in past-opponent games, q=(0.8×2+0.2×1)/2=0.9. Only the shared current policy is optimized; past snapshots incur forward passes, not separately added gradient training. The publication does not explicitly state whether both teams' trajectories enter the buffer in every self-play game. This is an assumption, with a one-contributing-team alternative q=0.5 retained below. Treating both sides as an external evaluation environment would incorrectly omit a substantial part of this learning process.

The central R=1 follows the final system’s stated target in main §4.4. Treating it as the effective value for the whole history remains an assumption. The following experience calculation is only a conditional cross-check. The [original Finals announcement](https://openai.com/index/openai-five-defeats-dota-2-world-champions/) reports about 45,000 simulated years, including about 10,000 by the 2018 International. Table 1 puts the early network near 43.4 million parameters and its LSTM expansion on August 26; the final network has 158,502,815 parameters. An approximate history check, at 30/4 policy steps per second and ten hero forwards per game step, is:

`365.25 × 86,400 × 7.5 × 10 × 2 × (10,000×43,436,520 + 35,000×158,502,815) = 2.8316e22 rollout FLOPs`.

Under its game-year interpretation, this simple check implies R≈0.87 under the central training/forward conversion, close to unit reuse and within the reported range. It does not independently establish the historical effective reuse or resolve the blog’s experience-unit ambiguity. It gives a full total 9.4960e22, 4.0% above the central estimate. It is not added to the central rollout estimate. The check assumes the blog's experience means simulated game time, approximates the first architecture change using the International cutoff, and applies 2P despite repeated observation processing. The central profile-ratio method avoids applying final parameter count to the whole training history. The retained blog file is a labelled transcription of its input facts: the page was readable through the web tool but a direct download returned 403.

**Evaluation.** Appendix J reports 750 reference games per logged rating and approximately two-hour updates. At the paper's roughly 180 active training days, that is approximately 1.62 million games. We transfer the human study's typical 40-minute game, use ten heroes, 7.5 policy steps/second, and `1.25×2×158,502,815` FLOPs per hero forward. The 1.25 factor allows for repeated observation processing absent from a simple parameter count. Using the final network for the entire history also allows for smaller early policies and reference-pool calibration whose separate game count is not given. Evaluation contributes 0.13% of the total; even tripling this component changes the total by less than 0.3%. This is an allowance grounded in the source cadence, not a claim to recover an evaluation log. The slightly different April 13/April 22 active-day endpoints are negligible at that share.

No game-engine CPU simulation, Redis transfers or non-neural orchestration is converted into neural FLOPs. They are outside this arithmetic definition. No additional neural teacher or pretrained policy is described for this run. Pre-run ablations and discarded independent research experiments are excluded. Earlier architecture segments preserved by surgery are included in the final policy lineage, but the source excludes pre-last-restart work and simplifies the retained history. No complete cost of abandoned branches is recovered. The two OG performance games and later Arena deployment are not added as a separate post-training task run.

### Sensitivity and reproduction

The portable calculation varies source optimization between 720–820 PFLOP/s-days, training/forward ratio 2.5–3.5, reuse 0.8–2.7, and training-eligible trajectory share 0.5–1.0. The resulting combined range is **6.8906e22–1.4181e23** FLOPs. Varying just q from 0.9 to 0.5 raises the central total to 1.1100e23. These are explicit operating assumptions, not statistically estimated confidence limits. The point is `derived_assumed_inputs` / `operation_count`.

Python 3 standard library only. The script reads the original XLSX directly, verifies all retained Five source hashes, and refuses existing outputs or outputs inside the evidence folder:

```sh
python3 research/recompute-five.py --sources sources --recipe research/five-recipe.json --output /absolute/path/to/new-five-calculation.json
```

After incorporation, use the actual published paths, for example `--sources /path/to/dataset/sources/games-training --recipe /path/to/dataset/research/games-training/five-recipe.json`; invoke the script from that published research folder or by its absolute path. No temporary-folder layout or network access is required.

### Model identity

`openai-five-finals-2019` identifies the April 13 champion-match checkpoint. Its weights were not released. Arena began April 18, after further training, so that date does not establish public access to this exact checkpoint; the model release date remains blank. The model is non-token: shared per-token fields are `not_applicable`. The final 158,502,815-parameter architecture belongs in the operation recipe, not in a text-token coefficient.
