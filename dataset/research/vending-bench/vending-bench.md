# Vending-Bench 2: one simulated business year

Four points compare the compute for one Vending-Bench 2 run with estimated human active management time at comparable final cash balance. A run targets 365 simulated days. These are business-management decisions through the simulation interface: finding suppliers, ordering, setting prices, checking stock and sales, and resolving problems. They do not include driving, carrying stock, waiting for deliveries or a year of calendar time.

## Original evidence

[Andon Labs’ V2 report](https://andonlabs.com/evals/vending-bench-2) supplies the task, system prompt and score definition. Its public page module `agent-work/sources/vending-bench/assets/26.kUxgg4v0.js`, literal `ct`, supplies separate average input/output tokens, run counts, token prices and cost summaries for 60 named models. The imported `agent-work/sources/vending-bench/assets/DAnYm5vA.js`, literal `m.vb2`, supplies per-model mean final balances, standard errors, sample counts and 365-day mean trajectories. These are original publisher aggregates, not independently obtained API logs. The retained report and modules are the September 2026 snapshot; neither module gives per-run identifiers or exact API revisions.

The four source labels join exactly across both tables. Cost and score counts agree: GPT-5.6 Sol and Opus 4.6 have five runs each; Opus 4.7 and Opus 5 have six. The visible heading saying five runs is stale. The stated benchmark includes bankruptcy termination; the source aggregate is used without filtering failed strategies. All four published average curves have 365 entries and all reported epochs have final values. These aggregates do not reveal whether individual trajectories were padded after early termination.

| Source label | Runs | Mean input tokens | Mean output tokens | Mean final cash balance | Standard error |
|---|---:|---:|---:|---:|---:|
| GPT-5.6 Sol | 5 | 66,208,258 | 284,368 | $9,619.37 | $1,337.80 |
| Claude Opus 4.6 | 5 | 135,113,544 | 272,240 | $8,017.59 | $1,366.99 |
| Claude Opus 4.7 | 6 | 109,520,875 | 439,787 | $10,936.76 | $1,181.31 |
| Claude Opus 5 | 6 | 108,801,181 | 439,900 | $11,181.87 | $2,093.58 |

The report’s statement that runs emit 60–100 million output tokens conflicts with these underlying values. We use the separate numeric fields, which also reproduce every one of the 60 plotted costs to within half a cent. The costs are calculated at uncached prices; they are not evidence that physical prompt caching was disabled. The simulation’s separate $100-per-million-output fee is a virtual business expense, not the provider price or a FLOP conversion.

## Compute accounting

Central FLOPs are `2 * active_parameters * (avg_input_tokens + avg_output_tokens)`, with one shared 100B active-parameter estimate per model, giving 200B FLOPs/token. The four totals are 1.32985252e19, 2.70771568e19, 2.19921324e19 and 2.18482162e19 FLOPs respectively. The token quantities are source-reported run averages; the parameter counts are estimates.

The central estimate processes the full reported input because no cache-read or cache-creation decomposition is exported. No physical cache saving is inferred from the price chart. The calculator retains scenarios counting 100%, 50%, 10% and 0% of input as fresh parameter work, always retaining output. These are sensitivity cases, not estimated cache-hit rates. Long-context attention is omitted by 2P and added back in `compute_flops` (`research/attention-correction.md`), so the 0%-fresh-input case is not a physical zero-input-compute bound.

The output field is treated as the source’s billable output quantity, including thinking once. There is no separate reasoning counter to add. Andon’s [Opus 4.8 analysis](https://andonlabs.com/blog/opus-4-8-vending-bench) establishes that thinking is used and describes roughly fivefold more reasoning for Max than High/Opus 4.7 Max. The same native cost table reports 1,603,705 output tokens for Opus 4.8 Max versus 414,486 High. This is consistent with thinking being represented, but does not independently prove the export’s counter definition. An extra million omitted output tokens would add 2e17 FLOPs, about 0.7–1.5% of these central totals. Raw API usage would settle this directly.

The V2 description supplies tools for moving stock and collecting money. It does not document the V1 LLM stock worker as a separate V2 model. The central calculation interprets the per-model published averages as the worker-side model workload; it does not add an invented helper count. Coverage of same-model helper calls, summarization, failed provider calls and search-answer LLMs is not specified in the exported data. This is a substantive scope limitation. If a helper ran outside these totals, its workload must be added with its own coefficient; the source does not establish that it is zero. Supplier/customer models are the simulated environment and are excluded from the target work. We do not add V1’s GPT-4o environment model to V2 worker compute.

## Model identities and sizes

The source labels are retained; dated API snapshots, sampling settings and exact effort are not supplied by the two data tables. The May 28 Andon post identifies its Opus 4.7 configuration as Max, but cannot establish that every later contribution to the six-run aggregate has identical settings. No unsupported effort label is added to the model ID. Opus 5 gets a generic registry row rather than reusing the existing explicitly Max-labelled row.

Official release evidence is retained for [Opus 4.6](https://www.anthropic.com/news/claude-opus-4-6) (February 5, 2026), [Opus 4.7](https://www.anthropic.com/news/claude-opus-4-7) (April 16), and [Opus 5](https://www.anthropic.com/news/claude-opus-5) (July 24). [GPT-5.6’s release announcement](https://openai.com/index/gpt-5-6/) establishes July 9 general availability; the original [system card](https://deploymentsafety.openai.com/gpt-5-6) retained locally has the same publication date and identifies Sol as the flagship. Earlier restricted partner preview access is not used as its public release date.

GPT-5.6 Sol’s 100B assumption transfers the scale of Epoch’s [original GPT-5 analysis](https://epochai.substack.com/p/notes-on-gpt-5-training-compute), which directly estimates about 100B active parameters from contemporary model scale, price and speed. This is a weak cross-generation prior, not a GPT-5.6 architecture reconstruction. Its purpose is a consistent starting estimate in the absence of disclosed dimensions; model efficiency improvements do not identify size.

Opus 4.6/4.7 retain the existing shared 100B coefficient after reopening the underlying [bandwidth analysis](https://unexcitedneurons.substack.com/p/estimating-the-size-of-claude-opus). That analysis obtains roughly 100–112.5B active for Opus 4.5 under FP8 from 4–4.5 TB/s divided by 40 tokens/s; mixed precision implies larger values. Its hardware/batch assumptions are consequential. Opus 5 uses the same rounded family prior and is consistent with the existing Opus 5 Max coefficient. No new speed/price inversion is performed. For all four models, 30–300B active is a broad scenario, producing 0.3–3 times central FLOPs. These are judgment ranges, not confidence intervals or reported architecture bounds.

## Human estimate

The original [Vending-Bench paper, v1](https://arxiv.org/html/2502.15840v1), sections 2.5 and 3.4, reports one person using a chat-and-tool interface for five hours. The participant had no task-specific preparation and reached day 67, with final net worth $844.05 and 344 items sold. They tried negotiations, product diversification and sales research, but missed the weekday sales pattern. The five hours are a session duration; the source gives no pause log separating interface waits from thinking. It is one contributing timing observation, not 67 human attempts.

That session calibrates the approximate effort of the simulation interface. The target here is an expert in inventory/business operations, unfamiliar with this particular simulator, who manages the year to a final cash balance comparable to each model’s mean (~$8,000–$11,200). The estimate does not ask the person to imitate every model message or achieve the paper’s speculative $63,000 strategy. It assumes active management, learning from supplied sales information, without AI help.

The 30-hour central estimate has four components, chosen from the actual workflow:

| Component | Assumed work | Active hours |
|---|---|---:|
| Initial setup | Read rules, discover initial suppliers, place first orders, learn the inventory/payment interface | 1.5 |
| Routine management | 3 minutes per simulated day, averaged across quiet days and reorder days | 18.25 |
| Weekly review | 8 minutes × 52 weeks for margin/sales-pattern checks, price/product changes and supplier comparisons | 6.93 |
| Exceptions | Additional supplier closures/scams, delayed orders, payment/refund disputes | 3 |
| Total before rounding | | 29.68 |

The routine allowance covers reading compact inventory and sales summaries, checking stock/cash, and executing or scheduling ordinary orders and transfers. It is not three minutes for each of the model’s thousands of messages. Weekly review is separate from ordinary replenishment: the source shows that pricing, negotiation and product choice materially distinguish stronger models. Exceptions reflect V2’s deliberately less reliable suppliers and customer demands. No physical transport or delivery wait is charged as human active time.

As a donor check, three minutes/day over the first 67 days gives 3.35 hours. Adding about an hour of novice setup and a modest initial set of price/supplier decisions is compatible with the original five-hour session. An expert may learn faster, while V2 requires more negotiation and exception handling. These considerations motivate the recipe rather than scaling five hours by 365/67 as the central derivation. The distinct score metric also prevents treating V1’s net worth as a measured V2 performance baseline.

The bounds re-run the table above at each line's plausible ends rather than halving and doubling its total. The low takes an hour of setup, 1.5 minutes a day of routine management, a four-minute weekly review and an hour of exceptions: 14.6 hours, 52,560 seconds. The high takes two hours of setup, six minutes a day, a fifteen-minute weekly review and six hours of exceptions: 57.5 hours, 207,000 seconds. Routine management moves the bound furthest because it carries 365 days. Those ranges reflect management cadence and the uncertain transfer, not sampling error. The source does not measure whether an expert reaches each target within 30 hours. The same central time across these four nearby score levels reflects unresolved differences within this range, not identical observed human effort.

`human_time_evidence=transferred_timings`, `human_time_method=estimated`, `human_time_statistic=point_estimate`, `human_attempts=1` and subset `all` record this derivation. The single novice session calibrates the estimate; it does not become a measured expert trial. Performance is `match` by the stated human target. No comparison flag is added solely because the timing donor was V1: both compared work units are the V2 task at the model’s target cash balance.

## vending-bench-2-gpt56sol

Source label GPT-5.6 Sol. Five-run token and score means; human target final cash balance about $9,619. Source total tokens 66,492,626; estimated FLOPs 1.32985252e19.

## vending-bench-2-opus46

Source label Claude Opus 4.6. Five-run token and score means; human target final cash balance about $8,018. Source total tokens 135,385,784; estimated FLOPs 2.70771568e19.

## vending-bench-2-opus47

Source label Claude Opus 4.7. Six-run token and score means; human target final cash balance about $10,937. Source total tokens 109,960,662; estimated FLOPs 2.19921324e19.

## vending-bench-2-opus5

Source label Claude Opus 5. Six-run token and score means; human target final cash balance about $11,182. Source total tokens 109,241,081; estimated FLOPs 2.18482162e19.

## Reproduction

Python 3, standard library only:

```sh
python3 -B /path/to/research/recompute.py --sources /path/to/sources --output /path/to/new-calculations.json
```

The script reads the retained public data literals without executing JavaScript, verifies all 60 cost calculations, checks the selected cohort counts and trajectory lengths, and computes FLOPs plus parameter/cache/human scenarios. `agent-work/sources/vending-bench/calculation-inputs.json` freezes the chosen model and human assumptions. Output paths inside the evidence directory are rejected. `agent-work/sources/vending-bench/source-manifest.json` records retained file hashes; `calculations.json` is the expected replay. There is no dependency on the candidate folder or network access.
