# BALROG Crafter episodes, 26 model runs

*Created 2026-09-13 09:20.*
*Last revised 2026-09-13 11:08 after independent review and a CSV text-length pass; see candidates/balrog/REVISION.md.*

**Summary.** 26 candidate rows, all on one work unit: one episode of Crafter under the BALROG
harness. The AI side comes from the 26 public BALROG submissions whose per-environment summary
records `input_tokens` and `output_tokens` (out of 44 submissions in the repository; the other 18
record no token counters). The human side comes from the 100-episode Crafter Human Expert Dataset,
which supports a directly commensurable score—the same "distinct achievements unlocked out of 22"
metric BALROG uses—of 63.18% against AI results from 12.7% to 57.3%, and an average episode of
619.02 environment steps. `compute_flops` spans 7.5e14 (Llama-3.2-1B) to 1.33e17 (Gemini 2.5 Pro
with vision) per episode; `human_time` is 123.8 s for every row. The two assumptions that dominate:
the human duration is a step count converted at the Crafter GUI's 5 steps per second rather than a
recorded timing, and seven of the 26 runs (six Gemini language-only runs plus Grok 4) have output
counters that exclude hidden reasoning tokens, making those FLOP values lower bounds.

A third fact belongs in the headline because it cuts the other way. AI episodes averaged 216.80
steps, every one of the 260 ending in death, against the human 619.02, so `human_time` covers 2.86
times more environment interaction than `compute_flops` does. Scoring the human episodes at each
run's own mean episode length reverses the four `match` rows: at a matched step budget the human
score is 47.91–52.68%, below all four AI results. The labels stay on the episode-level metric,
because the termination rule is the same on both sides and the episode is BALROG's own reporting
unit, but the matched-quantity number is carried in `performance_evidence` on those rows.

**No rows are drafted for NetHack, MiniHack, BabyAI, TextWorld or Baba Is AI.** See
[Environments excluded](#environments-excluded).

## Sources

| What | Locator |
|---|---|
| AI results and token counters | `https://github.com/balrog-ai/experiments`, commit `32574bb7d41256e2726899586ca1468a91cfc49f` (head, pushed 2026-03-18), `submissions/<LLM\|VLM>/<run>/crafter/crafter_summary.json`, the per-episode `crafter/default/default_run_NN.json`, and `submissions/<LLM\|VLM>/<run>/metadata.yaml` for the submission date |
| Harness code and configuration | `https://github.com/balrog-ai/BALROG`, inspected at commit `b7afe79e3e4265811cfa985ed7c95c4d1a11e3f5` (2026-04-09), which postdates every run; the full 46-commit history is retained so each run can be tied to the revision in force |
| Uniform-random floor | arXiv:2109.06780v2 Table B.1 random column, corroborated by `research/balrog/simulate_random_floor.py` |
| Benchmark description | arXiv:2411.13543v2, BALROG |
| Human episodes | `https://archive.org/details/crafter_human_dataset`, `dataset.zip`, md5 `0276dc7b875cd5aea22852a2b9f71a20`, 131,969,180 bytes, item public 2021-08-26, CC-BY-4.0 |
| Human study description | arXiv:2109.06780v2, Crafter, Section 4.4 and Table C.1 |
| Crafter code (human interface, recorder) | `https://github.com/danijar/crafter`, `main` |

Everything was retrieved on 2026-09-13. Retained extracts, with the code excerpts that establish
the work unit, the metric and the token counters, are in `agent-work/sources/balrog/`.

## Work unit

One Crafter episode. It is the same unit on both sides, and BALROG's own reporting unit: the
benchmark runs `eval.num_episodes.crafter: 10` episodes of the single `default` task and reports
`progression_percentage`, `average_steps`, `input_tokens` and `output_tokens` for that set.

An episode starts in a fresh procedurally generated 64x64 world and ends when the player dies or
the step cap is reached. BALROG caps episodes at `envs.crafter_kwargs.max_episode_steps: 2000`;
Crafter's own default is 10,000 and the human recordings are uncapped. Only 4 of the 100 human
episodes exceed 2,000 steps, and truncating all of them at 2,000 moves the human score from 63.182%
to 63.136%—0.05 points—so the differing cap is immaterial to the comparison and is not treated
as a separate comparison issue.

The agent acts once per environment step. `NaiveAgent.act`, `RobustNaiveAgent.act` and
`RobustCoTAgent.act` each issue exactly one `client.generate` call per step, so the number of model
calls in an episode equals its recorded `num_steps`. Prompts are the fixed instruction prompt (425
tokens under `cl100k_base`, retained verbatim at
`agent-work/sources/balrog/balrog-crafter-instruction-prompt.txt`) followed by a sliding window of the last 16
observations and the interleaved actions.

### Realized quantity of work

The unit definition is identical on both sides; the realized quantity is not.

| Side | Episodes | Mean steps | Median | Min | Max | Ended in death | Reached the cap |
|---|---|---|---|---|---|---|---|
| AI, all 26 runs | 260 | 216.80 |—| 34 | 554 | 260 | 0 |
| Human | 100 | 619.02 | 441 | 162 | 3143 |—| 4 exceed 2,000 |

Every one of the 260 AI episodes carries `done: true`; none was truncated by the 2,000-step cap. So
both sides play until the player dies, which is the same rule. But the human plays 2.86 times longer
before dying, so `human_time` covers 2.86 times more environment interaction than the mean
`compute_flops` it is set against. Per run the ratio is 2.0 (Gemini 3.1 Pro thinking, 302.5 steps) to
3.8 (Llama-3.2-3B, 161.8 steps); every row's `notes` carry its own figure.

The episode stays the unit and the labels stay on the episode-level metric, because the termination
rule is shared, surviving longer is part of playing better rather than a design difference, and the
episode is the unit BALROG itself reports. For the 22 `below` rows the short survival is part of the
worse performance and the comparison absorbs it. For the four `match` rows it is not absorbed, so
those rows also carry a matched-step human score; see
[Metric commensurability](#metric-commensurability).

## Metric commensurability

This is the load-bearing derivation, because it is what makes a human number comparable at all.

BALROG's Crafter score is not Crafter's own published score. `balrog/environments/crafter/env.py`
sets `progression = (number of the 22 achievements whose counter is greater than zero) / 22`, and
`balrog/utils.py` averages that over episodes. Crafter's own headline "human expert 50.5%" is a
different statistic—the geometric mean of the 22 per-achievement success rates across episodes —
and is **not** used here.

The Crafter paper's Table C.1 gives the per-achievement success rates over the 100 human episodes,
defined as "the fraction of all 100 recorded games during which the achievement has been unlocked at
least once". The mean over episodes of the achievement count is the sum of those 22 rates, so the
BALROG-equivalent human score is

    (86 + 12 + 92 + 53 + 67 + 100 + 100 + 31 + 84 + 89 + 8 + 26 + 22 + 78 + 78 + 100 + 45 + 32
     + 24 + 90 + 100 + 73) / 22 = 1390 / 22 = 63.1818%

Recomputing the same quantity episode by episode from the released `.npz` files
(`research/balrog/extract_crafter_human.py`) reproduces all 22 published success rates exactly, the
paper's statement that 5 of the 100 episodes unlock all 22 achievements, and a mean of 63.1818%.
Sample standard deviation across the 100 episodes is 15.35 points, standard error 1.535.

The best AI results are Grok 4 and Gemini 3 Pro at 57.27%, Gemini 2.5 Pro and Gemini 3.1 Pro
(thinking) at 55.00%. Nothing exceeds the human score, so no row is `above`.

**Performance rule.** `match` when the shortfall from 63.18% is under two combined standard errors,
`sqrt(ai_se^2 + 1.535^2)`, using each submission's own reported `standard_error`; `below` otherwise.
The data separate cleanly at that boundary: four runs sit at 1.24–1.40 combined standard errors and
the next closest is 2.78. BALROG computes its standard error as the population standard deviation
over 10 episodes divided by sqrt(10), which slightly understates the sampling error and therefore
makes the `match` label slightly harder to earn, not easier.

The rule divides by each run's own standard error, so a noisier run earns `match` more easily:
Gemini 3.1 Pro at 46.82 ± 4.17 is `below` at 3.68 while the same model with a thinking budget at
55.00 ± 6.44 is `match` at 1.24. All four `match` point estimates sit 6–8 points below the human
baseline, and failing to reject at n = 10 is not evidence of equivalence.

### Human score at a matched step budget

Because the AI dies sooner (see [Work unit](#work-unit)), the episode-level comparison gives the
human 2.86 times more play. The released human episodes carry the step at which each achievement was
first unlocked, so the human score can be recomputed at any step budget: count the achievements first
unlocked within the budget, and let an episode shorter than the budget contribute everything it
unlocked, which follows automatically because all of its unlock steps precede its length.

Evaluated at each run's own mean episode length, for the four `match` rows:

| point_id | AI mean steps | AI score (%) | Human score at that budget (%) | Human full-episode (%) |
|---|---|---|---|---|
| game-balrog-crafter-gemini3pro | 237.7 | 57.27 | 47.91 | 63.18 |
| game-balrog-crafter-grok4 | 261.7 | 57.27 | 49.45 | 63.18 |
| game-balrog-crafter-gemini25pro | 295.7 | 55.00 | 52.09 | 63.18 |
| game-balrog-crafter-gemini31prothinking | 302.5 | 55.00 | 52.68 | 63.18 |

All four exceed the human score once the step budget is matched, and the human standard error at
these budgets is 0.65–0.70 over the 100 episodes, so the gaps are not sampling noise. This does not
change the labels, which are defined on the episode-level metric, and it is not a licence to relabel
them `above`: the AI reaches those achievement counts by dying at step ~250, whereas the human at
step 250 is still alive and goes on to unlock more. The matched-step figure is recorded in
`performance_evidence` and `notes` on those four rows, and in the calculation JSON for all 26.

## Human baseline

**Population.** Five people, 100 episodes. The Crafter paper calls them human experts and says they
"were given the instructions of the game and allowed several hours of practice"; the archive.org item
describes them as "5 domain-familiar human players". Recorded as `expert`: substantial
task-specific practice, but this is not a claim about competitive or world-class play.

**Duration.** The released episodes carry no timestamps. What they carry is step counts, and the
recording interface fixes the step rate. `crafter/run_gui.py` advances exactly one environment step
per rendered frame, caps the frame rate with `clock.tick(args.fps)` at a default of `--fps 5`, and,
with the default `--wait False`, emits a `noop` whenever no key is held. The Crafter paper's own play
figure, printed in Section 2 immediately alongside the section that describes recording the 100
episodes, gives the command as `python3 -m crafter.run_gui` with no flags; the repository README
gives the same command. The paper is the stronger citation because it ties the interface to these
recordings.

That the recordings were made in that mode, rather than in the keypress-gated `--wait True` mode, is
excluded outright by the episodes themselves. Under `--wait True` the loop skips `env.step` entirely
when no key is held, except while the player is sleeping, so every recorded `noop` would have to be a
sleeping frame. Measuring sleeping frames directly as steps on which `inventory_energy` rises: 1,098
of the 61,902 steps, 1.77%. Measuring noops taken on non-sleeping frames: 23,466 steps, 37.91%. Under
`--wait True` that second number would be zero. The action histogram is retained at
`agent-work/sources/balrog/crafter-human-action-histogram.csv` and the per-episode counts at
`agent-work/sources/balrog/crafter-human-episodes.csv`.

    mean episode length   619.02 steps   (median 441, min 162, max 3143, total 61,902)
    human_time            619.02 / 5     = 123.804 s per episode
    median                441 / 5        = 88.2 s
    whole dataset         61,902 / 5     = 12,380 s = 3.44 h across 5 players

**Classification.** `human_time_method` is `work_rate`—a recorded work quantity times an explicit
time-per-unit rate. `human_time_evidence` is `assumed`, not `task_timings`: there are no timing
observations anywhere in the dataset, and the rate, although evidenced by the recording tool's
source and default and corroborated by the noop share, is not itself measured for these recordings.
`human_time_statistic` is `mean`, `human_time_subset` is `all`, `human_attempts` is 100—the
episode lengths that produce the mean are a real 100-episode sample.

**Alternative scenarios.** If the recordings used `--fps 10`, human_time halves to 61.9 s; at
`--fps 3` it rises to 206.3 s. If the pygame loop failed to keep up with 5 fps the true duration is
longer than 123.8 s, so the recorded value is, if anything, a floor. Using the median instead of the
mean gives 88.2 s. None of these change any performance label, because the label depends only on the
achievement metric.

## Compute

`compute_method` is `params_tokens`: the per-episode mean of `(input_tokens + output_tokens)`
multiplied by the model's `flops_per_token`. `compute_statistic` is `mean`, `compute_subset` is
`all`, `ai_attempts` is 10. The recorded per-environment totals were verified against the 260
retained per-episode records: for all 26 runs the episode `input_tokens`, `output_tokens`,
`num_steps` and `progression` sum or average exactly to the values in `crafter_summary.json`.

**`compute_evidence` is `derived_assumed_inputs` on all 26 rows.** Every row rests on at least one
substantial assumed input, and the assumptions differ by row rather than in kind: the fifteen rows
whose model record carries an estimated active-parameter count depend on that prior for the
coefficient; the twelve vLLM, NVIDIA NIM and xAI rows carry the full-prefix cache assumption; the
seven Gemini and Grok 4 rows depend on an unmeasured hidden-reasoning quantity; the two vision rows
depend on an image-position estimate. Which apply to which row is set out in the per-point sections
below; the CSV `notes` carry only the qualifications that change how a row reads. The
dataset's own practice settles the classification: across its 1,410 points, `derived_supported_inputs`
appears on 21 `params_tokens` rows and never once on a row whose model coefficient came from an
estimated parameter count, against 617 `derived_assumed_inputs` rows that did. Assigning the stronger
label to a Claude or GPT-5 row while assigning the weaker one to rows whose parameter counts are
exact published checkpoint totals would have inverted that ordering.

### What the counters contain

`balrog/client.py` records `usage.prompt_tokens` / `usage.completion_tokens` for OpenAI-compatible
endpoints (OpenAI, vLLM, NVIDIA NIM, xAI), `usage.input_tokens` / `usage.output_tokens` for the
Anthropic Messages API, `usage.inputTokens` / `usage.outputTokens` for AWS Bedrock Converse, and
`prompt_token_count` / `candidates_token_count` for Gemini.

**Cache.** No wrapper sends an Anthropic `cache_control` block, a Bedrock `cachePoint`, or a Gemini
`cached_content` handle, and `agent.cache_icl` is `False` in every submission used here. Anthropic
and Bedrock caching is opt-in per request, so for the six Claude runs no caching occurred and the
counters are the full processed prompt. OpenAI's automatic prompt caching and Gemini's implicit
caching both require a shared prefix of at least 1,024 tokens (2,048 for Gemini Pro); the only
prefix shared across calls after the history window fills is the instruction prompt, 424 tokens
before the 2025-07-18 spelling fix and 425 after, which is below both thresholds, so neither applies
either. What remains is self-hosted vLLM and the NVIDIA NIM endpoint, where block-level prefix reuse
is possible and undocumented for these runs, and xAI, whose caching terms are not documented. Those
twelve rows carry the full-prefix assumption, following the existing dataset's treatment of
unreported provider caching. **Sensitivity:** if the instruction prefix were served from cache on
every call after the first, the parameter-multiplication term would fall by 10.5% (Reka Flash 3) to
28.1% (Grok 3) across the twelve exposed runs. These are scenarios, not corrections; the central
values are unchanged.

**Reasoning tokens.** For the Anthropic, Bedrock, OpenAI, vLLM and NIM runs the recorded output
covers everything generated: Bedrock's `outputTokens` includes extended-thinking tokens (Claude Opus
4.5 thinking records 259.23 output tokens per call against 5.29 for the same model without
thinking), OpenAI's `completion_tokens` includes reasoning tokens, and the open models emit their
chain of thought in the visible content (DeepSeek-R1 1,996 output tokens per call, Reka Flash 3
2,159, R1-Distill-Qwen-32B 905).

For **seven** rows the counters do not: the six Gemini language-only runs and Grok 4. Each of the six
Gemini language-only runs records 1.63–1.78 output tokens per call, which is the length of an action
string such as "Move East", including the Gemini 3.1 Pro run configured with `thinking_budget: 1024`;
Grok 4 records 1.51. The mechanism is visible in the harness history: until commit `af7d1f1`
(2026-03-16), after the last Gemini submission used here, the Gemini wrapper recorded
`candidates_token_count`, which excludes `thoughts_token_count`; `thinking_budget` was already
supported at `b20b5e18` without `include_thoughts`, so a budgeted run can indeed record 1.69 output
tokens per call. The Grok 4 submission's own README warns that "while this is using the naive agent,
Grok4 could be reasoning before replying". The per-episode CSV trajectories retain no reasoning text
and no per-call usage for these runs, so the omitted quantity is not recoverable from the published
artifacts. Those seven rows' `compute_flops` are lower bounds; the row notes say so.
**Sensitivity:** an extra 200 hidden reasoning tokens per call would raise those totals by
10.9–12.4%; an extra 1,024 per call, the configured budget where one was set, by 56.1–63.4%.

**The vision Gemini 2.5 Pro run is not in that set.** It records 600.63 output tokens per call
(1,526,213 over 2,541 calls), two orders of magnitude above the six language-only Gemini runs and far
beyond any action string, and its saved trajectory shows one short action per step with an empty
`Reasoning` column. Whatever those tokens are, the counter is not reporting the action alone, so no
lower-bound clause is applied to `game-balrog-crafter-vlm-gemini25pro`. The run also called a
different endpoint from the language-only Gemini 2.5 Pro run (see
[Model assumptions](#model-assumptions)), which is the likeliest place the difference comes from, but
nothing in the retained record establishes the mechanism.

The input side dominates in every run except the four open reasoning models, so even the 1,024-token
scenario keeps the affected values inside a factor of 1.7.

**Grok 3 and GPT-5.** Grok 3 records 2.70 output tokens per call and GPT-5 10.80; neither was
reasoning materially. The GPT-5 submission README labels the run "minimal thinking" and states the
configuration is "as close as possible to the base model with no reasoning", but the reproduction
command it prints passes no `reasoning_effort`, and the recorded `generate_kwargs` do not contain
one. The effort setting behind the run therefore cannot be verified from the retained record; the
10.80 output tokens per call are consistent with the minimal label.

### Harness revisions in force

The 26 runs span 2024-11-11 to 2026-02-25 and no single harness revision produced them. Commit
`b7afe79e` is the revision **inspected** for this note, not the code behind any run: it is dated
2026-04-09, after every submission, and for the Gemini rows it carries the opposite token accounting
to the one those rows depend on. Each row's `source_record` therefore names the submission date from
its `metadata.yaml` and the newest harness commit available at that date; the full 46-commit history
is retained at `agent-work/sources/balrog/balrog-harness-commits.json`.

Two consequences are worth stating rather than leaving implicit. Five submissions dated 2024-11-11
predate the repository's first public commit `fba89e2` (2024-11-21) and were run on pre-release code,
which those rows' `source_record` says. The three AWS Bedrock submissions (2026-02-24) predate the
Bedrock client's merge at `bc2b7ff8` (2026-03-16), so they too ran code that was not in the
repository at their date; that one is recorded here and in their per-point sections rather than in
the CSV.

What is constant across every revision, checked commit by commit:

- `progression = (achievements with count > 0) / 22` in `balrog/environments/crafter/env.py` is
  byte-identical from `fba89e2` through head.
- `envs.crafter_kwargs.max_episode_steps: 2000` and `eval.num_episodes.crafter: 10` are unchanged in
  every revision of `config.yaml`.
- The instruction prompt changed exactly once, at `4dfee35` (2025-07-18), replacing "Collect
  Sampling" with "Collect Sapling". That moves the `cl100k_base` count from 424 to 425 tokens.

What is not constant, and therefore means per-call input-token counts are not strictly comparable
across the 26 runs:

- `c347aa8` (2025-01-28) reworded the invalid-action feedback appended to the next observation and
  made it configurable, defaulting on.
- `ec49c9b` (2025-04-24) swapped the semantic-array indices in `describe_env`, changing the content of
  the "You face X at your front" line.
- `393505a` (2025-08-19) rewrote 122 lines of the Crafter observation builder and added the
  `unique_items`, `precise_location`, `skip_items` and `edge_only_items` options, with `unique_items`
  defaulting to `True`, which deduplicates the listed items.

This affects the comparability of token counts between runs, not the metric, the cap, the episode
count or the work unit.

### Vision rows

Two submissions send one rendered 256x256 frame per step alongside the text
(`agent.max_image_history: 1`, `envs.crafter_kwargs.size: [256, 256]`). The reported `input_tokens`
bundle those image positions with text, so `tokens` subtracts an estimate of them while
`compute_flops` retains them, per the dataset's rule that `tokens` is text-only and FLOPs cover all
processed positions:

- `game-balrog-crafter-vlm-claude35sonnet`: 1,955 frames x (256 x 256 / 750) = 170,830.5 positions
  removed from text, 4.3% of the input.
- `game-balrog-crafter-vlm-gemini25pro`: 2,541 frames x 258 = 655,578 positions removed, 12.8% of
  the input.

Both conventions are the providers' billing formulas, not disclosed internal position counts, and
applying a text `flops_per_token` to them is an approximation, which is one of the reasons both
vision rows are `derived_assumed_inputs`. Comparing the language-only and vision Claude 3.5 Sonnet
runs, the vision run uses 206 more input tokens per call, more than the 87 estimated image positions;
the remainder is different episodes and seeds, so the residual does not sharpen the estimate.

`tokens_accounting` on these two rows is `decoder_processed` rather than `input_output`, because the
stored quantity is text positions with the image positions removed, which is what that value
describes and what `input_output` does not. The existing dataset's image-bearing rows leave image
positions inside an `input_output` or `source_total` count, so this is a departure from its practice
in favour of the COLUMNS definition; a schema owner may prefer consistency instead.

### Failed calls

`execute_with_retries` retries up to `max_retries` times on exception and contributes no tokens for
a call that raised. A call rejected before dispatch consumed nothing, but a call that timed out at
60 s after the provider began generating did consume work that is not counted. The submissions
retain no error logs, so this residual is not quantifiable; it pushes in the same direction as the
missing reasoning tokens.

## Model assumptions

Fifteen rows reuse model records from the existing dataset with their shared coefficients unchanged:
`deepseek-r1`, `llama-3.1-8b-instruct`, `llama-3.3-70b-instruct`, `mistral-nemo-2407`, `phi-4`,
`claude-3-5-sonnet-20240620`, `claude-3-5-haiku-20241022`, `claude-opus-4-5`, `gpt-5`, `grok-3-beta`,
`grok-4`, `gemini-2.5-flash`, `gemini-3-pro`, `gemini-3-flash-preview`, `gemini-3.1-pro-preview`.

The endpoint each run actually called was read from the `client.model_id` written into all ten of its
per-episode records, which the harness writes at run time, rather than from the run-level
`summary.json` or the README; every row's `source_record` names it. Three reuses involve an alias
rather than an exact string match, and are recorded here so a reviewer can check them: the Grok 3 run
calls `grok-3-latest` where the dataset record is `grok-3-beta`; the Gemini 3 Pro run calls
`gemini-3-pro-preview` where the record is `gemini-3-pro`; the Mistral run loads
`mistralai/Mistral-Nemo-Instruct-2407` where the record is the API alias `open-mistral-nemo-2407` with
a rounded 12B active count against the checkpoint's 12,247,782,400. The DeepSeek-R1 submission
directory is named `20240410_...`, which its own `metadata.yaml` and the repository's commit history
both date to 2025-04-10; the original January 2025 R1 is the only R1 that existed then, so the
`deepseek-r1` record applies rather than R1-0528.

Two upstream labelling errors are worth recording because they would mislead anyone joining on the
directory name. The `metadata.yaml` of both Claude 3.5 Sonnet submissions names
"Claude-3.5-Sonnet-2024-10-22" while the recorded configuration and all ten per-episode records say
`claude-3-5-sonnet-20240620`; the recorded configuration wins. The READMEs of both Claude 3.5 Sonnet
submissions print `client.model_id=gpt-4o-mini-2024-07-18` in their reproduction command, which is a
copy-paste error in the oldest submissions' documentation.

### The two Gemini 2.5 Pro runs called different endpoints

The language-only run's ten per-episode records all name `gemini-2.5-pro-preview-03-25`; the vision
run's all name `gemini-2.5-pro-exp-03-25`. Both run-level `summary.json` files say
`gemini-2.5-pro-exp-03-25` and both READMEs say `preview-03-25`, so the run-level files and the
READMEs each get one of the two wrong.

Google's API changelog dates `gemini-2.5-pro-exp-03-25` to 2025-03-25 as a free-tier experimental
release and `gemini-2.5-pro-preview-03-25` to 2025-04-04 as "a public preview Gemini 2.5 Pro version
with billing enabled", adding "you can continue to use gemini-2.5-pro-exp-03-25 on the free tier".
`preview-03-25` was repointed to the 05-06 model on 2025-05-06, after both runs on 2025-04-25. So at
the run date both aliases served the same March snapshot at different billing tiers.

A single record, `gemini-2.5-pro-03-25`, therefore covers both rows, with the alias each run used
named in that row's `source_record` and the relationship in the model record's `notes`. That keeps
the 100B active prior identical across the two rows, which is what matters for the arithmetic. The
unexplained residue is that the two endpoints reported output tokens two orders of magnitude apart
(1.74 against 600.63 per call) on the same snapshot; the changelog does not account for that, and
nothing in the retained record does either.

A fifteenth reuse is `phi-4`, which the dataset already carries at a rounded 14,000,000,000 active
parameters. The checkpoint's exact `safetensors` total is 14,659,507,200, 4.7% higher, but the folder
rule is that a reused `model_id` keeps identical shared assumptions, so the row uses the existing
28,000,000,000 FLOPs per token unchanged.

Seven new records are added in `candidates/balrog/models.csv`. Five are open-weight models whose
active parameter count is the published `safetensors` total from the model card, taken as `reported`:
Llama-3.2-1B-Instruct 1,235,814,400; Llama-3.2-3B-Instruct 3,212,749,824; Qwen2.5-7B-Instruct
7,615,616,512; DeepSeek-R1-Distill-Qwen-32B 32,763,876,352; Reka Flash 3 20,905,482,240. These
totals include embedding parameters, matching how the existing dataset records exact checkpoint
counts for Llama 2 70B, Swallow and Qwen2.5-Math-1.5B. Where the dataset instead carries a rounded
nominal count for a model this batch reuses, that record is left alone; the two conventions coexist
in the dataset already.

Two are closed models with `estimated` counts transferred from priors the dataset already uses:

- `claude-haiku-4-5`, 20B active, transferred from the Haiku-class prior applied to Haiku 3 and
  Haiku 3.5. Anthropic discloses nothing about Haiku 4.5's size, and Haiku 4.5 is a substantially
  more capable model than Haiku 3.5, so this is the weakest parameter assumption in the batch. A
  40B active size would double `game-balrog-crafter-claudehaiku45` to 3.5e16 FLOPs. The prior is
  internally consistent across three Haiku generations but not across vendors at the same tier: the
  dataset puts Gemini 2.5 Flash and Gemini 3 Flash, Haiku 4.5's rough peers, at 40B.
- `gemini-2.5-pro-03-25`, 100B active, transferred from the Gemini Pro frontier-model prior the
  dataset uses for Gemini 2.5 Pro and Gemini 3 Pro. This is a separate record from the dataset's
  `gemini-2.5-pro` because the March snapshot is an earlier revision than the June GA model.

Claude Opus 4.5 appears twice, once with and once without extended thinking. These are the same
weights under different inference configuration, so both rows use the `claude-opus-4-5` record and
the configuration is stated in `task_description`; the same applies to Gemini 3.1 Pro with and
without a thinking budget, and to Claude 3.5 Sonnet and Gemini 2.5 Pro across the language-only and
vision rows.

## Comparison issues

Every row carries `different_inputs_or_tools`, and nothing else. The concrete difference: the
language-only agent receives a natural-language description of the 9x9 local view plus a
16-observation history and chooses one of 17 named actions with no time limit per decision, while
the human sees the rendered game through a keyboard interface running in real time at 5 frames per
second. The vision rows narrow but do not close that gap—they add the rendered frame while keeping
the text description and the untimed decisions.

Not flagged, with reasons: the assessment is identical on both sides, computed from the same 22
achievement counters with the same definition, so no `different_assessment`; both sides use every
recorded attempt, so no `different_attempt_selection`; the episode-cap difference is measured above
at 0.05 points and is described in this note rather than flagged.

**A specification gap, surfaced rather than forced.** The 2.86-fold difference in realized play
described under [Work unit](#work-unit) is a real feature of the comparison and `comparison_issues`
has no value for it. `different_task` does not fit: the task definition, inputs, cap and termination
rule are identical, and the difference is an outcome of how the two sides play rather than a
difference in what they were asked to do. Forcing `different_task` would also collide with its own
definition, which is about task content and quantities of work as specified. The dataset has met this
shape before in the Pokemon Crystal row, where the AI's completed playthrough and the human estimate
also cover different realized amounts of play. This is left for the schema owner; meanwhile the
number is in every row's `notes` and the matched-step recomputation is in `performance_evidence` on
the rows where it changes the reading.

One difference is worth a reviewer's attention even though it is not a flag: the human experts had
"several hours of practice" at Crafter, while every model plays zero-shot with no prior episode in
context. BALROG supports in-context demonstrations but none of these submissions used them
(`agent.max_icl_history` is unused with `agent.type: naive`/`robust_naive`/`robust_cot`). That is a
property of the compared systems rather than of the task conditions, so it is stated in
`human_skill` and here rather than as a `comparison_issues` value.

## Chance floor

Five rows score close enough to a uniform-random policy that the question has to be asked. All 26
are included; five are flagged in `notes`.

**The floor is 10.35%.** The Crafter paper's own random column (arXiv:2109.06780v2 Table B.1,
"success rates on Crafter without rewards") gives the 22 per-achievement rates for a random policy,
defined the same way as the human table. They sum to 227.6, so the mean achievement count is 2.276
and BALROG's metric reads 227.6 / 22 = 10.345%. `research/balrog/simulate_random_floor.py` runs a
uniform-random policy under BALROG's exact environment settings, including the one noop step the
wrapper consumes at reset, and agrees: five replications of 200 episodes gave 10.114, 10.136, 10.364,
10.568 and 11.159 percent, pooling to 10.468%, with a mean within-replication standard error of 0.401
and mean episodes of 167–173 steps. Crafter's simulation is not bit-reproducible across processes, so
the script records every replication and the note uses the paper's figure as the published value and
the measured 0.40 as its standard error.

The floor is not "doing nothing". Almost all of it comes from four achievements a random policy gets
for free: `wake_up` 93.6%, `collect_sapling` 50.2%, `place_plant` 44.6%, `collect_wood` 24.4%. The
other sixteen sit between 0.0% and 4.4%.

**Which rows sit on it.** Using `z = (progression - 10.345) / sqrt(se_ai^2 + 0.40^2)` and flagging
below 2.5:

| point_id | Progression (%) | SE | z vs floor |
|---|---|---|---|
| game-balrog-crafter-llama32-1b | 12.73 | 1.91 | 1.22 |
| game-balrog-crafter-phi4 | 13.64 | 2.65 | 1.23 |
| game-balrog-crafter-qwen25-7b | 16.36 | 3.03 | 1.97 |
| game-balrog-crafter-r1distillqwen32b | 15.00 | 2.14 | 2.14 |
| game-balrog-crafter-llama32-3b | 17.27 | 2.79 | 2.46 |
| next closest, game-balrog-crafter-grok3 | 25.00 | 4.13 | 3.53 |

**The composition rejects random play decisively.** The aggregate hides the evidence. These runs do
not score 13–17% the way a random policy scores 10%; they forfeit the free achievements and earn ones
random play essentially never gets. Taking each run's strongest single achievement and computing the
binomial tail probability of its count in 10 episodes under the paper's random rate, with 0.0%
entries floored at 0.05% (half the paper's reporting resolution) and a Bonferroni factor of 22 for
the achievement that was selected:

| point_id | Strongest achievement | Count | Random rate | p x 22 |
|---|---|---|---|---|
| game-balrog-crafter-llama32-1b | defeat_zombie | 3/10 | 0.1% | 2.6e-06 |
| game-balrog-crafter-phi4 | eat_cow | 5/10 | 0.4% | 5.6e-09 |
| game-balrog-crafter-qwen25-7b | defeat_zombie | 6/10 | 0.1% | 4.6e-15 |
| game-balrog-crafter-r1distillqwen32b | defeat_zombie | 5/10 | 0.1% | 5.5e-12 |
| game-balrog-crafter-llama32-3b | collect_drink | 7/10 | 9.3% | 1.2e-04 |

Every one rejects the uniform-random null at corrected p below 1.3e-4. They hunt cows and fight
zombies, which random play does in 0.4% and 0.1% of episodes, and three of the five build a table.
What pulls the aggregate down is the other side of the ledger: they rarely choose Sleep, so they
forfeit `wake_up`, which random play collects 93.6% of the time. The per-episode achievement counters
that support this are retained in `agent-work/sources/balrog/balrog-crafter-episodes.csv`.

This is not the situation where a benchmark score at the guessing floor has no internal structure to
inspect. Here the decomposition is published and it separates playing from mashing. The `below`
labels are unaffected either way: the five sit 14 to 21 combined standard errors below the human
63.18%.

**Harness default actions.** The retained `failed_candidates` field records calls whose output
contained no parseable action, which the harness replaces with a default Noop while still charging
the model call. phi-4 is the extreme case at 35.6% of 2,116 calls, so about a third of its play is
the harness rather than the model; mistral-nemo is 22.9%, Llama-3.2-3B 19.8%, Reka Flash 3 14.6%,
Grok 4 12.4%, Qwen2.5-7B 10.1%, and every other run is under 11%. Every run's rate is in its
per-point section below and in `agent-work/sources/balrog/balrog-crafter-episodes.csv`; the three flagged rows
above 10% also carry it in the CSV `notes`, beside the floor flag it qualifies.

## Environments excluded

BALROG's other five environments have AI token counts of the same quality but no defensible human
time at the same work unit.

**NetHack (NLE).** The AI side is good: five episodes per submission, each a complete NetHack game
from a fresh character to a real end (the Gemini 3 Pro episode 00 record ends "DEATH: died. Killed by
a kobold zombie, while fainted from lack of food"), with the largest token workloads in the suite —
up to 280.6M input tokens for five episodes. The human side fails twice over. BALROG's progression
metric is not a human score: Appendix F.2 defines it as the probability that a human player who
reached a given dungeon or experience level goes on to win, built from the NLD-NAO human dataset, so
"1.76% progression" says the agent reached a depth from which humans ascend 1.76% of the time, not
that it did 1.76% of what a human does. And no human duration is available at this unit: NLD-NAO's
per-game metadata does include a `realtime` field in seconds, but the Dungeons and Data paper
(arXiv:2211.00539) reports only episode counts, scores and turns for its 1,511,228 human games, not
any duration statistic, and alt.org's public xlogfiles returned 404 on every path tried on
2026-09-13. Converting the AI's work unit to a human one would also need per-game time-to-depth data
rather than whole-game durations, since the agents die on dungeon levels 1–4 while the median NAO
game runs 3,766 turns. Revisit if the NAO xlogfile becomes reachable.

**BabyAI.** The BabyAI paper (arXiv:1810.08272) uses a *simulated* human teacher throughout; its
"human" references are all to that simulation or to motivation. No human play timings or scores.

**Baba Is AI.** The Cloos et al. paper (arXiv:2407.13729) mentions humans only in motivating the
rule-breaking premise. No human baseline of any kind.

**MiniHack and TextWorld.** No human timing or scoring evidence found for the specific task sets
BALROG selects.

BALROG's Table 1 offers "Time to Master for Humans" per environment (Seconds for BabyAI, Minutes for
TextWorld, Hours for Crafter, Baba Is AI and MiniHack, Years for NLE). These are unsourced
order-of-magnitude claims about mastery, not per-episode completion times, and are not used.

## Source reconciliation

The submissions repository holds 44 submission directories at commit
`32574bb7d41256e2726899586ca1468a91cfc49f`: 34 under `submissions/LLM/` and 10 under
`submissions/VLM/`. Disposition of every one:

- **26 drafted**, one Crafter row each. These are exactly the submissions that write
  per-environment summary files; each `crafter/crafter_summary.json` carries `input_tokens`,
  `output_tokens`, `average_steps`, `episodes_played` and `progression_percentage`, and each is
  accompanied by ten per-episode records.
- **18 excluded for absent compute evidence.** These older submissions (all from September to
  November 2024) contain only a top-level `summary.json` with per-environment progression and no
  token counters anywhere, and no per-environment or per-episode files: `LLM/20240924_naive-GPT4o`,
  `LLM/20240924_naive-GPT4o-mini`, `LLM/20240924_naive-Gemini-1.5-Flash`,
  `LLM/20240924_naive-Gemini-1.5-Pro`, `LLM/20240930_naive-Llama-3.1-70B-Instruct`,
  `LLM/20240930_naive-Llama-3.2-11B-Instruct`, `LLM/20240930_naive-Llama-3.2-90B-Instruct`,
  `LLM/20241115_naive-Qwen2-VL-72B-Instruct`, `LLM/20241115_naive-Qwen2-VL-7B-instruct`,
  `LLM/20241115_naive-Qwen2.5-72B-Instruct`, `VLM/20240924_naive-Gemini-1.5-Flash`,
  `VLM/20240924_naive-Gemini-1.5-Pro`, `VLM/20240930_naive-Llama-3.2-11B-Instruct`,
  `VLM/20240930_naive-Llama-3.2-90B-Instruct`, `VLM/20240930_naive-gpt-4o`,
  `VLM/20240930_naive-gpt-4o-mini`, `VLM/20241115_naive-Qwen2-VL-72B-Instruct`,
  `VLM/20241115_naive-Qwen2-VL-7B-instruct`. Two of them also record a `client.model_id` that
  contradicts the directory name (`LLM/20240930_naive-Llama-3.2-90B-Instruct` and
  `VLM/20241115_naive-Qwen2-VL-72B-Instruct` both name a different checkpoint), so their model
  identity would need resolving even if tokens appeared.

Across environments, the 26 drafted submissions also carry token counters for NetHack, MiniHack,
BabyAI, TextWorld and Baba Is AI—154 model-by-environment records in total, of which 26 are
drafted here. The other 128 are excluded on the human side, for the reasons in
[Environments excluded](#environments-excluded), not for want of compute evidence.

## Reproduction

    python3 research/balrog/extract_crafter_human.py \
        --dataset <unzipped crafter_human_dataset>/dataset \
        --out agent-work/sources/balrog/crafter-human-episodes.csv

    python3 research/balrog/simulate_random_floor.py \
        --out agent-work/derived/balrog/crafter-random-floor.json

    python3 research/balrog/build_balrog_rows.py \
        --sources agent-work/sources/balrog \
        --dataset-models "<dataset>/models.csv" \
        --candidate-models candidates/balrog/models.csv \
        --points-out <fresh dir>/points.csv \
        --calc-out   <fresh dir>/balrog-crafter-calculations.json

The build script asserts the per-episode records against the environment summaries before computing
anything, and writes every input, intermediate and result to the calculation JSON retained at
`agent-work/derived/balrog/balrog-crafter-calculations.json`; it uses the standard library only and is
deterministic. The extraction script needs `numpy`; the floor simulation needs `numpy` and `crafter`
(tested with 1.8.3) and, as its own output records, is not bit-reproducible, which is why its result
corroborates the published floor rather than supplying it.

## Per-point inputs and arithmetic

Every row below shares the human baseline, work unit, metric, and accounting rules stated above. Each entry gives only what differs: the submission it comes from, the endpoint it called and the harness revision then available, its recorded token and step counts, the coefficient applied, and the resulting values. Model calls are one per environment step, summed over the ten episodes. `compute_flops` is the per-episode mean, `flops_per_token * (input_tokens + output_tokens) / 10`. The matched budget is this run's mean episode length, at which the human episodes are rescored by counting only achievements first unlocked by that step.

### game-balrog-crafter-deepseekr1

Submission `submissions/LLM/20240410_robust_cot_DeepSeek-R1`, dated 2025-04-10, newest harness revision then available `f4d4ddd` (2025-04-10). Crafter task `default`, 10 episodes, 2114 model calls, 211.4 steps per episode on average, every episode ending in death. Endpoint `deepseek-ai/deepseek-r1` recorded in all ten per-episode records; model record `deepseek-r1`, 74000000000 FLOPs per token (reported active parameter count).

Recorded totals over the ten episodes: 3,636,763 input tokens, 4,220,494 output tokens (1996.45 output tokens per call); 35 calls (1.7%) produced no parseable action and were defaulted to Noop.
Per episode: 785,725.7 processed positions, of which 785,725.7 are text (`tokens`).
`compute_flops` = 74000000000 x 785,725.7 = 5.81437e+16.

Progression 36.364% +/- 3.803 against the human 63.182% +/- 1.535: shortfall 26.818 points, 6.54 combined standard errors, so `below`. At a matched budget of 211.4 steps the human score is 46.09% +/- 0.74, and human_time covers 2.9 times more play than compute_flops. 6.80 combined standard errors above the random floor.

### game-balrog-crafter-llama32-1b

Submission `submissions/LLM/20241030_naive-Llama-3.2-1B-Instruct`, dated 2024-11-11, predating the harness repository's first public commit, so run on pre-release code. Crafter task `default`, 10 episodes, 1858 model calls, 185.8 steps per episode on average, every episode ending in death. Endpoint `meta-llama/Llama-3.2-1B-Instruct` recorded in all ten per-episode records; model record `llama-3.2-1b-instruct`, 2471628800 FLOPs per token (reported active parameter count).

Recorded totals over the ten episodes: 3,029,554 input tokens, 5,802 output tokens (3.12 output tokens per call); 100 calls (5.4%) produced no parseable action and were defaulted to Noop.
Per episode: 303,535.6 processed positions, of which 303,535.6 are text (`tokens`).
`compute_flops` = 2471628800 x 303,535.6 = 7.50227e+14.

Progression 12.727% +/- 1.907 against the human 63.182% +/- 1.535: shortfall 50.455 points, 20.61 combined standard errors, so `below`. At a matched budget of 185.8 steps the human score is 43.23% +/- 0.74, and human_time covers 3.3 times more play than compute_flops. 1.22 combined standard errors above the random floor, within the flagged range.

### game-balrog-crafter-llama32-3b

Submission `submissions/LLM/20241030_naive-Llama-3.2-3B-Instruct`, dated 2024-11-11, predating the harness repository's first public commit, so run on pre-release code. Crafter task `default`, 10 episodes, 1618 model calls, 161.8 steps per episode on average, every episode ending in death. Endpoint `meta-llama/Llama-3.2-3B-Instruct` recorded in all ten per-episode records; model record `llama-3.2-3b-instruct`, 6425499648 FLOPs per token (reported active parameter count).

Recorded totals over the ten episodes: 2,846,868 input tokens, 4,644 output tokens (2.87 output tokens per call); 320 calls (19.8%) produced no parseable action and were defaulted to Noop.
Per episode: 285,151.2 processed positions, of which 285,151.2 are text (`tokens`).
`compute_flops` = 6425499648 x 285,151.2 = 1.83224e+15.

Progression 17.273% +/- 2.787 against the human 63.182% +/- 1.535: shortfall 45.909 points, 14.43 combined standard errors, so `below`. At a matched budget of 161.8 steps the human score is 39.36% +/- 0.79, and human_time covers 3.8 times more play than compute_flops. 2.46 combined standard errors above the random floor, within the flagged range.

### game-balrog-crafter-llama31-8b

Submission `submissions/LLM/20241101_naive-Llama-3.1-8B-Instruct`, dated 2024-11-11, predating the harness repository's first public commit, so run on pre-release code. Crafter task `default`, 10 episodes, 1907 model calls, 190.7 steps per episode on average, every episode ending in death. Endpoint `meta-llama/Meta-Llama-3.1-8B-Instruct` recorded in all ten per-episode records; model record `llama-3.1-8b-instruct`, 16000000000 FLOPs per token (reported active parameter count).

Recorded totals over the ten episodes: 3,183,723 input tokens, 5,327 output tokens (2.79 output tokens per call); 125 calls (6.6%) produced no parseable action and were defaulted to Noop.
Per episode: 318,905.0 processed positions, of which 318,905.0 are text (`tokens`).
`compute_flops` = 16000000000 x 318,905.0 = 5.10248e+15.

Progression 25.455% +/- 3.227 against the human 63.182% +/- 1.535: shortfall 37.727 points, 10.56 combined standard errors, so `below`. At a matched budget of 190.7 steps the human score is 43.77% +/- 0.78, and human_time covers 3.2 times more play than compute_flops. 4.65 combined standard errors above the random floor.

### game-balrog-crafter-claude35sonnet

Submission `submissions/LLM/20241103_Claude-3.5-Sonnet`, dated 2024-11-11, predating the harness repository's first public commit, so run on pre-release code. Crafter task `default`, 10 episodes, 1712 model calls, 171.2 steps per episode on average, every episode ending in death. Endpoint `claude-3-5-sonnet-20240620` recorded in all ten per-episode records; model record `claude-3-5-sonnet-20240620`, 200000000000 FLOPs per token (estimated active parameter count).

Recorded totals over the ten episodes: 3,102,483 input tokens, 15,227 output tokens (8.89 output tokens per call); 130 calls (7.6%) produced no parseable action and were defaulted to Noop.
Per episode: 311,771.0 processed positions, of which 311,771.0 are text (`tokens`).
`compute_flops` = 200000000000 x 311,771.0 = 6.23542e+16.

Progression 32.727% +/- 3.201 against the human 63.182% +/- 1.535: shortfall 30.455 points, 8.58 combined standard errors, so `below`. At a matched budget of 171.2 steps the human score is 40.91% +/- 0.79, and human_time covers 3.6 times more play than compute_flops. 6.94 combined standard errors above the random floor.

### game-balrog-crafter-qwen25-7b

Submission `submissions/LLM/20241115_naive-Qwen2.5-7B-it`, dated 2024-11-25, newest harness revision then available `31df8ef` (2024-11-22). Crafter task `default`, 10 episodes, 1787 model calls, 178.7 steps per episode on average, every episode ending in death. Endpoint `Qwen/Qwen2.5-7B-Instruct` recorded in all ten per-episode records; model record `qwen2.5-7b-instruct`, 15231233024 FLOPs per token (reported active parameter count).

Recorded totals over the ten episodes: 2,865,370 input tokens, 4,447 output tokens (2.49 output tokens per call); 180 calls (10.1%) produced no parseable action and were defaulted to Noop.
Per episode: 286,981.7 processed positions, of which 286,981.7 are text (`tokens`).
`compute_flops` = 15231233024 x 286,981.7 = 4.37109e+15.

Progression 16.364% +/- 3.029 against the human 63.182% +/- 1.535: shortfall 46.818 points, 13.79 combined standard errors, so `below`. At a matched budget of 178.7 steps the human score is 41.95% +/- 0.80, and human_time covers 3.5 times more play than compute_flops. 1.97 combined standard errors above the random floor, within the flagged range.

### game-balrog-crafter-claude35haiku

Submission `submissions/LLM/20241209_naive-claude-3-5-haiku`, dated 2024-12-11, newest harness revision then available `7fb3dbd` (2024-12-10). Crafter task `default`, 10 episodes, 1709 model calls, 170.9 steps per episode on average, every episode ending in death. Endpoint `claude-3-5-haiku-20241022` recorded in all ten per-episode records; model record `claude-3-5-haiku-20241022`, 40000000000 FLOPs per token (estimated active parameter count).

Recorded totals over the ten episodes: 3,223,211 input tokens, 7,712 output tokens (4.51 output tokens per call); 0 calls (0.0%) produced no parseable action and were defaulted to Noop.
Per episode: 323,092.3 processed positions, of which 323,092.3 are text (`tokens`).
`compute_flops` = 40000000000 x 323,092.3 = 1.29237e+16.

Progression 26.364% +/- 2.787 against the human 63.182% +/- 1.535: shortfall 36.818 points, 11.57 combined standard errors, so `below`. At a matched budget of 170.9 steps the human score is 40.77% +/- 0.80, and human_time covers 3.6 times more play than compute_flops. 5.69 combined standard errors above the random floor.

### game-balrog-crafter-mistralnemo

Submission `submissions/LLM/20241209_naive-mistral-nemo-instruct`, dated 2024-12-09, newest harness revision then available `67a8d26` (2024-12-05). Crafter task `default`, 10 episodes, 1906 model calls, 190.6 steps per episode on average, every episode ending in death. Endpoint `mistralai/Mistral-Nemo-Instruct-2407` recorded in all ten per-episode records; model record `mistral-nemo-2407`, 24000000000 FLOPs per token (reported active parameter count).

Recorded totals over the ten episodes: 3,420,049 input tokens, 5,587 output tokens (2.93 output tokens per call); 437 calls (22.9%) produced no parseable action and were defaulted to Noop.
Per episode: 342,563.6 processed positions, of which 342,563.6 are text (`tokens`).
`compute_flops` = 24000000000 x 342,563.6 = 8.22153e+15.

Progression 27.727% +/- 2.685 against the human 63.182% +/- 1.535: shortfall 35.455 points, 11.46 combined standard errors, so `below`. At a matched budget of 190.6 steps the human score is 43.77% +/- 0.78, and human_time covers 3.2 times more play than compute_flops. 6.40 combined standard errors above the random floor.

### game-balrog-crafter-llama33-70b

Submission `submissions/LLM/20241209_naive_Llama-3.3-70B-Instruct`, dated 2024-12-09, newest harness revision then available `67a8d26` (2024-12-05). Crafter task `default`, 10 episodes, 2314 model calls, 231.4 steps per episode on average, every episode ending in death. Endpoint `meta-llama/Llama-3.3-70B-Instruct` recorded in all ten per-episode records; model record `llama-3.3-70b-instruct`, 140000000000 FLOPs per token (reported active parameter count).

Recorded totals over the ten episodes: 3,736,389 input tokens, 5,755 output tokens (2.49 output tokens per call); 2 calls (0.1%) produced no parseable action and were defaulted to Noop.
Per episode: 374,214.4 processed positions, of which 374,214.4 are text (`tokens`).
`compute_flops` = 140000000000 x 374,214.4 = 5.239e+16.

Progression 28.636% +/- 4.068 against the human 63.182% +/- 1.535: shortfall 34.545 points, 7.94 combined standard errors, so `below`. At a matched budget of 231.4 steps the human score is 47.36% +/- 0.70, and human_time covers 2.7 times more play than compute_flops. 4.47 combined standard errors above the random floor.

### game-balrog-crafter-phi4

Submission `submissions/LLM/20250113_robust_naive_microsoft_phi-4`, dated 2025-01-13, newest harness revision then available `a5fa0e7` (2025-01-09). Crafter task `default`, 10 episodes, 2116 model calls, 211.6 steps per episode on average, every episode ending in death. Endpoint `microsoft/phi-4` recorded in all ten per-episode records; model record `phi-4`, 28000000000 FLOPs per token (reported active parameter count).

Recorded totals over the ten episodes: 3,884,066 input tokens, 33,420 output tokens (15.79 output tokens per call); 753 calls (35.6%) produced no parseable action and were defaulted to Noop.
Per episode: 391,748.6 processed positions, of which 391,748.6 are text (`tokens`).
`compute_flops` = 28000000000 x 391,748.6 = 1.0969e+16.

Progression 13.636% +/- 2.650 against the human 63.182% +/- 1.535: shortfall 49.545 points, 16.18 combined standard errors, so `below`. At a matched budget of 211.6 steps the human score is 46.09% +/- 0.74, and human_time covers 2.9 times more play than compute_flops. 1.23 combined standard errors above the random floor, within the flagged range.

### game-balrog-crafter-r1distillqwen32b

Submission `submissions/LLM/20250126_robust_cot_deepseek_R1_distill_qwen32B`, dated 2025-01-26, newest harness revision then available `301dc5a` (2025-01-24). Crafter task `default`, 10 episodes, 1998 model calls, 199.8 steps per episode on average, every episode ending in death. Endpoint `deepseek-ai/DeepSeek-R1-Distill-Qwen-32B` recorded in all ten per-episode records; model record `deepseek-r1-distill-qwen-32b`, 65527752704 FLOPs per token (reported active parameter count).

Recorded totals over the ten episodes: 2,918,389 input tokens, 1,809,127 output tokens (905.47 output tokens per call); 95 calls (4.8%) produced no parseable action and were defaulted to Noop.
Per episode: 472,751.6 processed positions, of which 472,751.6 are text (`tokens`).
`compute_flops` = 65527752704 x 472,751.6 = 3.09783e+16.

Progression 15.000% +/- 2.137 against the human 63.182% +/- 1.535: shortfall 48.182 points, 18.31 combined standard errors, so `below`. At a matched budget of 199.8 steps the human score is 44.64% +/- 0.78, and human_time covers 3.1 times more play than compute_flops. 2.14 combined standard errors above the random floor, within the flagged range.

### game-balrog-crafter-rekaflash3

Submission `submissions/LLM/20250313_robust_cot_Reka-Flash-3`, dated 2025-03-13, newest harness revision then available `67654e2` (2025-03-13). Crafter task `default`, 10 episodes, 1947 model calls, 194.7 steps per episode on average, every episode ending in death. Endpoint `RekaAI/reka-flash-3` recorded in all ten per-episode records; model record `reka-flash-3`, 41810964480 FLOPs per token (reported active parameter count).

Recorded totals over the ten episodes: 3,702,986 input tokens, 4,202,988 output tokens (2158.70 output tokens per call); 284 calls (14.6%) produced no parseable action and were defaulted to Noop.
Per episode: 790,597.4 processed positions, of which 790,597.4 are text (`tokens`).
`compute_flops` = 41810964480 x 790,597.4 = 3.30556e+16.

Progression 33.636% +/- 3.474 against the human 63.182% +/- 1.535: shortfall 29.545 points, 7.78 combined standard errors, so `below`. At a matched budget of 194.7 steps the human score is 44.32% +/- 0.77, and human_time covers 3.2 times more play than compute_flops. 6.66 combined standard errors above the random floor.

### game-balrog-crafter-gemini25pro

Submission `submissions/LLM/20250425_naive_Gemini-2.5-Pro-Exp-03-25`, dated 2025-04-25, newest harness revision then available `ec49c9b` (2025-04-24). Crafter task `default`, 10 episodes, 2957 model calls, 295.7 steps per episode on average, every episode ending in death. Endpoint `gemini-2.5-pro-preview-03-25` recorded in all ten per-episode records; model record `gemini-2.5-pro-03-25`, 200000000000 FLOPs per token (estimated active parameter count).

Recorded totals over the ten episodes: 5,286,229 input tokens, 5,131 output tokens (1.74 output tokens per call); 2 calls (0.1%) produced no parseable action and were defaulted to Noop.
Per episode: 529,136.0 processed positions, of which 529,136.0 are text (`tokens`).
`compute_flops` = 200000000000 x 529,136.0 = 1.05827e+17.

Progression 55.000% +/- 5.977 against the human 63.182% +/- 1.535: shortfall 8.182 points, 1.33 combined standard errors, so `match`. At a matched budget of 295.7 steps the human score is 52.09% +/- 0.67, and human_time covers 2.1 times more play than compute_flops. 7.45 combined standard errors above the random floor. The recorded output counter omits hidden reasoning, so compute_flops is a lower bound.

### game-balrog-crafter-grok3

Submission `submissions/LLM/20250425_naive_grok-3`, dated 2025-04-25, newest harness revision then available `ec49c9b` (2025-04-24). Crafter task `default`, 10 episodes, 1954 model calls, 195.4 steps per episode on average, every episode ending in death. Endpoint `grok-3-latest` recorded in all ten per-episode records; model record `grok-3-beta`, 230000000000 FLOPs per token (estimated active parameter count).

Recorded totals over the ten episodes: 2,945,986 input tokens, 5,284 output tokens (2.70 output tokens per call); 14 calls (0.7%) produced no parseable action and were defaulted to Noop.
Per episode: 295,127.0 processed positions, of which 295,127.0 are text (`tokens`).
`compute_flops` = 230000000000 x 295,127.0 = 6.78792e+16.

Progression 25.000% +/- 4.129 against the human 63.182% +/- 1.535: shortfall 38.182 points, 8.67 combined standard errors, so `below`. At a matched budget of 195.4 steps the human score is 44.36% +/- 0.77, and human_time covers 3.2 times more play than compute_flops. 3.53 combined standard errors above the random floor.

### game-balrog-crafter-grok4

Submission `submissions/LLM/20250713_naive_grok-4`, dated 2025-07-23, newest harness revision then available `4dfee35` (2025-07-18). Crafter task `default`, 10 episodes, 2617 model calls, 261.7 steps per episode on average, every episode ending in death. Endpoint `grok-4-latest` recorded in all ten per-episode records; model record `grok-4`, 230000000000 FLOPs per token (estimated active parameter count).

Recorded totals over the ten episodes: 4,629,787 input tokens, 3,954 output tokens (1.51 output tokens per call); 324 calls (12.4%) produced no parseable action and were defaulted to Noop.
Per episode: 463,374.1 processed positions, of which 463,374.1 are text (`tokens`).
`compute_flops` = 230000000000 x 463,374.1 = 1.06576e+17.

Progression 57.273% +/- 3.921 against the human 63.182% +/- 1.535: shortfall 5.909 points, 1.40 combined standard errors, so `match`. At a matched budget of 261.7 steps the human score is 49.45% +/- 0.65, and human_time covers 2.4 times more play than compute_flops. 11.91 combined standard errors above the random floor. The recorded output counter omits hidden reasoning, so compute_flops is a lower bound.

### game-balrog-crafter-gemini25flash

Submission `submissions/LLM/20250719-naive_gemini-2.5-flash`, dated 2025-07-22, newest harness revision then available `4dfee35` (2025-07-18). Crafter task `default`, 10 episodes, 1833 model calls, 183.3 steps per episode on average, every episode ending in death. Endpoint `gemini-2.5-flash` recorded in all ten per-episode records; model record `gemini-2.5-flash`, 80000000000 FLOPs per token (estimated active parameter count).

Recorded totals over the ten episodes: 3,161,574 input tokens, 3,266 output tokens (1.78 output tokens per call); 2 calls (0.1%) produced no parseable action and were defaulted to Noop.
Per episode: 316,484.0 processed positions, of which 316,484.0 are text (`tokens`).
`compute_flops` = 80000000000 x 316,484.0 = 2.53187e+16.

Progression 40.000% +/- 4.802 against the human 63.182% +/- 1.535: shortfall 23.182 points, 4.60 combined standard errors, so `below`. At a matched budget of 183.3 steps the human score is 42.73% +/- 0.78, and human_time covers 3.4 times more play than compute_flops. 6.15 combined standard errors above the random floor. The recorded output counter omits hidden reasoning, so compute_flops is a lower bound.

### game-balrog-crafter-gpt5minimal

Submission `submissions/LLM/20250808_naive_gpt-5-minimal`, dated 2025-08-19, newest harness revision then available `393505a` (2025-08-19). Crafter task `default`, 10 episodes, 2451 model calls, 245.1 steps per episode on average, every episode ending in death. Endpoint `gpt-5-2025-08-07` recorded in all ten per-episode records; model record `gpt-5`, 200000000000 FLOPs per token (estimated active parameter count).

Recorded totals over the ten episodes: 4,294,259 input tokens, 26,462 output tokens (10.80 output tokens per call); 11 calls (0.4%) produced no parseable action and were defaulted to Noop.
Per episode: 432,072.1 processed positions, of which 432,072.1 are text (`tokens`).
`compute_flops` = 200000000000 x 432,072.1 = 8.64144e+16.

Progression 39.091% +/- 4.126 against the human 63.182% +/- 1.535: shortfall 24.091 points, 5.47 combined standard errors, so `below`. At a matched budget of 245.1 steps the human score is 48.50% +/- 0.67, and human_time covers 2.5 times more play than compute_flops. 6.93 combined standard errors above the random floor.

### game-balrog-crafter-gemini3pro

Submission `submissions/LLM/20260203_naive_gemini-3-pro`, dated 2026-02-03, newest harness revision then available `b20b5e1` (2025-11-25). Crafter task `default`, 10 episodes, 2377 model calls, 237.7 steps per episode on average, every episode ending in death. Endpoint `gemini-3-pro-preview` recorded in all ten per-episode records; model record `gemini-3-pro`, 200000000000 FLOPs per token (estimated active parameter count).

Recorded totals over the ten episodes: 4,063,213 input tokens, 3,863 output tokens (1.63 output tokens per call); 0 calls (0.0%) produced no parseable action and were defaulted to Noop.
Per episode: 406,707.6 processed positions, of which 406,707.6 are text (`tokens`).
`compute_flops` = 200000000000 x 406,707.6 = 8.13415e+16.

Progression 57.273% +/- 4.416 against the human 63.182% +/- 1.535: shortfall 5.909 points, 1.26 combined standard errors, so `match`. At a matched budget of 237.7 steps the human score is 47.91% +/- 0.68, and human_time covers 2.6 times more play than compute_flops. 10.58 combined standard errors above the random floor. The recorded output counter omits hidden reasoning, so compute_flops is a lower bound.

### game-balrog-crafter-gemini3flash

Submission `submissions/LLM/20260213_naive_gemini-3-flash`, dated 2026-02-13, newest harness revision then available `b20b5e1` (2025-11-25). Crafter task `default`, 10 episodes, 2180 model calls, 218.0 steps per episode on average, every episode ending in death. Endpoint `gemini-3-flash-preview` recorded in all ten per-episode records; model record `gemini-3-flash-preview`, 80000000000 FLOPs per token (estimated active parameter count).

Recorded totals over the ten episodes: 3,978,636 input tokens, 3,874 output tokens (1.78 output tokens per call); 7 calls (0.3%) produced no parseable action and were defaulted to Noop.
Per episode: 398,251.0 processed positions, of which 398,251.0 are text (`tokens`).
`compute_flops` = 80000000000 x 398,251.0 = 3.18601e+16.

Progression 45.000% +/- 6.346 against the human 63.182% +/- 1.535: shortfall 18.182 points, 2.78 combined standard errors, so `below`. At a matched budget of 218.0 steps the human score is 46.59% +/- 0.70, and human_time covers 2.8 times more play than compute_flops. 5.45 combined standard errors above the random floor. The recorded output counter omits hidden reasoning, so compute_flops is a lower bound.

### game-balrog-crafter-gemini31pro

Submission `submissions/LLM/20260221_naive_gemini-3.1-pro`, dated 2026-02-21, newest harness revision then available `b20b5e1` (2025-11-25). Crafter task `default`, 10 episodes, 2345 model calls, 234.5 steps per episode on average, every episode ending in death. Endpoint `gemini-3.1-pro-preview` recorded in all ten per-episode records; model record `gemini-3.1-pro-preview`, 200000000000 FLOPs per token (estimated active parameter count).

Recorded totals over the ten episodes: 3,784,161 input tokens, 4,009 output tokens (1.71 output tokens per call); 0 calls (0.0%) produced no parseable action and were defaulted to Noop.
Per episode: 378,817.0 processed positions, of which 378,817.0 are text (`tokens`).
`compute_flops` = 200000000000 x 378,817.0 = 7.57634e+16.

Progression 46.818% +/- 4.168 against the human 63.182% +/- 1.535: shortfall 16.364 points, 3.68 combined standard errors, so `below`. At a matched budget of 234.5 steps the human score is 47.64% +/- 0.69, and human_time covers 2.6 times more play than compute_flops. 8.71 combined standard errors above the random floor. The recorded output counter omits hidden reasoning, so compute_flops is a lower bound.

### game-balrog-crafter-claudehaiku45

Submission `submissions/LLM/20260223_naive_claude-haiku-4.5`, dated 2026-02-24, newest harness revision then available `b20b5e1` (2025-11-25). Crafter task `default`, 10 episodes, 2339 model calls, 233.9 steps per episode on average, every episode ending in death. Endpoint `global.anthropic.claude-haiku-4-5-20251001-v1:0` recorded in all ten per-episode records; model record `claude-haiku-4-5`, 40000000000 FLOPs per token (estimated active parameter count).

Recorded totals over the ten episodes: 4,370,694 input tokens, 11,452 output tokens (4.90 output tokens per call); 1 calls (0.0%) produced no parseable action and were defaulted to Noop.
Per episode: 438,214.6 processed positions, of which 438,214.6 are text (`tokens`).
`compute_flops` = 40000000000 x 438,214.6 = 1.75286e+16.

Progression 24.091% +/- 3.152 against the human 63.182% +/- 1.535: shortfall 39.091 points, 11.15 combined standard errors, so `below`. At a matched budget of 233.9 steps the human score is 47.55% +/- 0.68, and human_time covers 2.6 times more play than compute_flops. 4.33 combined standard errors above the random floor.

### game-balrog-crafter-claudeopus45

Submission `submissions/LLM/20260224_naive_claude-opus-4.5`, dated 2026-02-24, newest harness revision then available `b20b5e1` (2025-11-25). Crafter task `default`, 10 episodes, 2229 model calls, 222.9 steps per episode on average, every episode ending in death. Endpoint `global.anthropic.claude-opus-4-5-20251101-v1:0` recorded in all ten per-episode records; model record `claude-opus-4-5`, 200000000000 FLOPs per token (estimated active parameter count).

Recorded totals over the ten episodes: 4,176,575 input tokens, 11,799 output tokens (5.29 output tokens per call); 5 calls (0.2%) produced no parseable action and were defaulted to Noop.
Per episode: 418,837.4 processed positions, of which 418,837.4 are text (`tokens`).
`compute_flops` = 200000000000 x 418,837.4 = 8.37675e+16.

Progression 49.545% +/- 3.113 against the human 63.182% +/- 1.535: shortfall 13.636 points, 3.93 combined standard errors, so `below`. At a matched budget of 222.9 steps the human score is 46.82% +/- 0.69, and human_time covers 2.8 times more play than compute_flops. 12.49 combined standard errors above the random floor.

### game-balrog-crafter-claudeopus45thinking

Submission `submissions/LLM/20260224_naive_claude-opus-4.5-thinking`, dated 2026-02-24, newest harness revision then available `b20b5e1` (2025-11-25). Crafter task `default`, 10 episodes, 2579 model calls, 257.9 steps per episode on average, every episode ending in death. Endpoint `global.anthropic.claude-opus-4-5-20251101-v1:0` recorded in all ten per-episode records; model record `claude-opus-4-5`, 200000000000 FLOPs per token (estimated active parameter count).

Recorded totals over the ten episodes: 5,303,170 input tokens, 668,545 output tokens (259.23 output tokens per call); 0 calls (0.0%) produced no parseable action and were defaulted to Noop.
Per episode: 597,171.5 processed positions, of which 597,171.5 are text (`tokens`).
`compute_flops` = 200000000000 x 597,171.5 = 1.19434e+17.

Progression 48.636% +/- 3.152 against the human 63.182% +/- 1.535: shortfall 14.545 points, 4.15 combined standard errors, so `below`. At a matched budget of 257.9 steps the human score is 48.95% +/- 0.64, and human_time covers 2.4 times more play than compute_flops. 12.05 combined standard errors above the random floor.

### game-balrog-crafter-gemini31prothinking

Submission `submissions/LLM/20260225_naive_gemini-3.1-pro-thinking`, dated 2026-02-25, newest harness revision then available `b20b5e1` (2025-11-25). Crafter task `default`, 10 episodes, 3025 model calls, 302.5 steps per episode on average, every episode ending in death. Endpoint `gemini-3.1-pro-preview` recorded in all ten per-episode records; model record `gemini-3.1-pro-preview`, 200000000000 FLOPs per token (estimated active parameter count).

Recorded totals over the ten episodes: 5,384,557 input tokens, 5,127 output tokens (1.69 output tokens per call); 0 calls (0.0%) produced no parseable action and were defaulted to Noop.
Per episode: 538,968.4 processed positions, of which 538,968.4 are text (`tokens`).
`compute_flops` = 200000000000 x 538,968.4 = 1.07794e+17.

Progression 55.000% +/- 6.443 against the human 63.182% +/- 1.535: shortfall 8.182 points, 1.24 combined standard errors, so `match`. At a matched budget of 302.5 steps the human score is 52.68% +/- 0.70, and human_time covers 2.0 times more play than compute_flops. 6.92 combined standard errors above the random floor. The recorded output counter omits hidden reasoning, so compute_flops is a lower bound.

### game-balrog-crafter-vlm-claude35sonnet

Submission `submissions/VLM/20241103_Claude-3.5-Sonnet`, dated 2024-11-11, predating the harness repository's first public commit, so run on pre-release code. Crafter task `default`, 10 episodes, 1955 model calls, 195.5 steps per episode on average, every episode ending in death. Endpoint `claude-3-5-sonnet-20240620` recorded in the run summary.json; the episode records omit it; model record `claude-3-5-sonnet-20240620`, 200000000000 FLOPs per token (estimated active parameter count).

Recorded totals over the ten episodes: 3,945,345 input tokens, 9,998 output tokens (5.11 output tokens per call); 10 calls (0.5%) produced no parseable action and were defaulted to Noop.
Billed image positions: 1955 frames x 87.3813 = 170,830.5, removed from the text-token field and kept in the FLOP total.
Per episode: 395,534.3 processed positions, of which 378,451.2 are text (`tokens`).
`compute_flops` = 200000000000 x 395,534.3 = 7.91069e+16.

Progression 37.273% +/- 3.136 against the human 63.182% +/- 1.535: shortfall 25.909 points, 7.42 combined standard errors, so `below`. At a matched budget of 195.5 steps the human score is 44.36% +/- 0.77, and human_time covers 3.2 times more play than compute_flops. 8.52 combined standard errors above the random floor.

### game-balrog-crafter-vlm-gemini25pro

Submission `submissions/VLM/20250425_naive_Gemini-2.5-Pro-Exp-03-25`, dated 2025-04-25, newest harness revision then available `ec49c9b` (2025-04-24). Crafter task `default`, 10 episodes, 2541 model calls, 254.1 steps per episode on average, every episode ending in death. Endpoint `gemini-2.5-pro-exp-03-25` recorded in all ten per-episode records; model record `gemini-2.5-pro-03-25`, 200000000000 FLOPs per token (estimated active parameter count).

Recorded totals over the ten episodes: 5,117,806 input tokens, 1,526,213 output tokens (600.63 output tokens per call); 10 calls (0.4%) produced no parseable action and were defaulted to Noop.
Billed image positions: 2541 frames x 258 = 655,578.0, removed from the text-token field and kept in the FLOP total.
Per episode: 664,401.9 processed positions, of which 598,844.1 are text (`tokens`).
`compute_flops` = 200000000000 x 664,401.9 = 1.3288e+17.

Progression 37.273% +/- 4.627 against the human 63.182% +/- 1.535: shortfall 25.909 points, 5.32 combined standard errors, so `below`. At a matched budget of 254.1 steps the human score is 48.73% +/- 0.66, and human_time covers 2.4 times more play than compute_flops. 5.80 combined standard errors above the random floor.
