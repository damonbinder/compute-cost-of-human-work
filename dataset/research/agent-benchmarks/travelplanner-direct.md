# TravelPlanner: reconstructed direct planning

## agen-work-travelplanner-gpt4o-direct-scope

One itinerary from the 1,000-query TravelPlanner test set, averaged across the released GPT-4o direct-prompting runs. Queries require three-, five- or seven-day trips, one to three destination cities, transport, accommodation, meals and attractions within budget and other stated constraints. This is planning from supplied reference data, not making bookings or travelling.

### Original records and workload

The follow-up study is [Programming over Thinking, v4](https://arxiv.org/html/2601.09097v4), Appendix B.1 (GPT-4o-2024-11-20), Table 1 (23.6% final success for direct prompting), and Appendix G/Table 7 (token claims). Its [original repository](https://github.com/DerrickGXD/SCOPE) supplies `output/travel_planner_direct_gpt-4o.json`, all 1,000 reference records, and `baselines/run_directreasoning_travel_planner.py`. The retained tree pins the source revision; the baseline file was introduced on 3 July 2026, alongside the released data.

The output file contains query, natural-language plan, wall time and parsed plan. It contains no native usage counters or API retry records. The released script writes two usage fields absent from every saved record and uses a different output basename; it does not exactly reproduce the saved file format. The reconstruction therefore assumes its prompt and reference transformations describe the calls that produced those plans. The retained source performs one direct model call, then a separate model call to convert the answer for grading. The work unit ends at the natural-language plan, so the grading conversion is excluded. There are no helper calls in direct plan generation. Reported grading still depends on that conversion and can reflect extraction errors.

`recompute.py` reconstructs the supplied reference formatting and planner prompt, then tokenizes each input and retained output using `o200k_base`. It does not execute agents or generated code. The three imported source functions only restructure travel dictionaries. A seven-token API framing allowance is assumed per call. Results:

| Quantity | Mean per query |
|---|---:|
| Input content tokens | 8,502.119 |
| API framing allowance | 7 |
| Output tokens | 348.95 |
| Counted tokens | 8,858.069 |
| FLOPs, using the existing model coefficient of 100 billion/token | 885,806,900,000,000 |

This is a **full-prefix reconstruction**, not recovered provider usage. No cache counters are available. The released code is assumed to describe the calls that generated the retained plans. Input framing is a negligible allowance; exact historical prompt identity and caching are the material limits. Unrecorded rejected or lost API calls cannot be reconstructed from the output file; the estimate covers the retained completed call per query. GPT-4o has no separately metered hidden reasoning stream in this source.

**Do not substitute the paper's token table.** Table 7 reports 1,055 input and 335 output tokens for GPT-4o direct TravelPlanner. These disagree with the released code and outputs: the first reconstructed input alone contains 4,424 content tokens, and the mean is 8,502.119. The retained output mean is also 348.95 rather than 335. The discrepancy is unresolved; the candidate uses the inspectable records. Changing the assumed framing from 7 to zero alters the estimate by under 0.1%. A hypothetical 50% input cache-read share would approximately halve the input contribution, but there is no evidence to adopt that share.

### Human effort and comparison

The [original TravelPlanner paper](https://arxiv.org/html/2402.01622v4), Section 3.3, describes 20 graduate-student annotators constructing feasible plans. Table 3's caption says **interviews** suggested around 12 minutes per plan. It does not supply clocks or individual duration records. Thus the candidate uses `assumed`, `estimated`, `point_estimate`, with no recorded human attempts. It does not turn the interview estimate into a measured mean or infer a sample count from the 20 annotators.

The central estimate is **720 active seconds** for a trained planner to construct a valid itinerary for the same final test query and transformed reference choices supplied to the AI, using ordinary sorting, arithmetic and note-taking tools. It transfers the original reported estimate to the test-workload mix, not to professional open-web holiday planning. This is an expert baseline in familiarity with the task's constraints, not a claim that the annotators were travel agents. A 6–24 minute sensitivity is appropriate: supplied choices avoid open-ended research, but multi-city accommodation/occupancy/budget interactions can require revisions.

Input/output inspection covered source IDs 1, 180, 334, 500, 667, 820 and 1000, spanning all horizons, single-person and group requests, cuisine, room rules and transport constraints. ID 1 supplies 20 attractions, 24 restaurants, 13 accommodation choices and 12 transport choices. Its model answer chooses a room costing 981 per night for two nights on a 1,900 total budget: the accommodation alone exceeds the budget. ID 500 adds two travellers and visitor-permitted accommodation; ID 1000 requires three cities, five travellers, several cuisines, visitor permission and no flights. Producing a feasible plan requires filtering compatible transport and rooms, checking nights/occupancy and costs, filling distinct meal/attraction choices, and writing/checking the itinerary. It does not require reading all database rows or performing the trip itself. These observations support an order-of-ten-minutes task estimate without treating a component breakdown as measured data.

AI performance is **below** the valid-plan human target: the study reports 23.6% satisfying all constraints for its GPT-4o direct configuration. The model revision is identified by Appendix B.1; the retained file name and script default are generic GPT-4o labels, not native endpoint records. Performance is linked to these outputs through the published configuration and file naming, not independently recomputed from per-case success flags. The original human plans were checked and repaired; their existence does not establish a 100% first-attempt human success rate. The large gap supports the estimated direction without making that claim.

The original human timing evidence comes from an earlier annotation process. The released AI preprocessing removes flight dates and journey durations and supplies a curated reference subset; original human annotation used the source environment. The original authors also tightened budgets using the constructed plans and repaired query/plan pairs. Those facts limit the timing and quality transfer. The estimated human target here instead uses the same final query and transformed reference choices as the AI, so these source-history differences do not establish different target conditions; `comparison_issues` is `none_identified`.

### Reproduction

Install `tiktoken`, then run:

```sh
python recompute.py --source-dir /absolute/path/to/retained/sources --output /absolute/path/to/new-calculation.json
```

The output contains all 1,000 item counts and hashes of the exact three inputs. It refuses to overwrite an existing file or write into the source directory. No temporary dependencies or model/API credentials are used by the script.
