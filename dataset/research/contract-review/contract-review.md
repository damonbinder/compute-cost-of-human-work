# Procurement-contract review

## lang-work-contract-review-gpt4-1106

One complete review against a supplied scenario and checklist: identify issues and locate their clauses. GPT-4 returns a structured report with a determination, relevant clauses, explanatory rationale and any assumptions for each check. The comparator is a junior lawyer doing that review work. This is professional analysis, not contract drafting or providing legal advice to a client.

[Martin et al.](https://arxiv.org/abs/2401.16212v1) tested ten procurement contracts from the US and New Zealand. Table 4 gives mean junior-lawyer time of 56.17 minutes; Tables 2–3 give determination/localization F1 of .860/.667 for juniors and .871/.686 for GPT-4-1106. The broad comparison is **match** across both dimensions. Senior lawyers established the reference; their 43.46-minute timing is not substituted for the junior baseline. LPOs are a different group with different timings and scores.

Human time is **56.17 × 60 = 3,370.2 seconds**. This is a reported mean converted to seconds, not a researcher duration estimate. The contributing reviewer/attempt count is not published; ten contracts does not establish ten timed attempts across all reviewers. Therefore human_attempts is blank, not not_applicable. The source does not document pauses or a full individual timing distribution. We use its task-duration aggregate without claiming stopwatch-level active-time verification. All reviewed work enters the source mean; we do not select successful issue decisions.

### Cost-derived workload

Table 5 reports **$0.25 mean API cost per contract**. Section 4.2.3 says costs were computed from average input/output tokens and provider prices, but it does not publish those counts. The [original November 2023 launch announcement](https://openai.com/index/new-models-and-developer-products-announced-at-devday/) identifies gpt-4-1106-preview and prices input/output at $10/$30 per million tokens. The author’s retained 2025 whitepaper repeats the cost; it is not an independent measurement.

Let I and O be the average input and output tokens. The reported cost implies:

`0.00001 I + 0.00003 O = 0.25`, so `I + O = 25,000 − 2 O`.

Without another assumption, this bounds total work between about 8,333 and 25,000 tokens. The main estimate assumes one whole-document response, consistent with the large-context methodology and Appendix A prompt. It does not assume that the paper publishes native call counts. The 1106 endpoint capped a response at 4,096 tokens, confirmed by a [contemporary first-person API error](https://community.openai.com/t/gpt-4-1106-preview-context-length/485573) and corroborated by [official Turbo-preview documentation](https://developers.openai.com/api/docs/models/gpt-4-turbo-preview). The current documentation defaults to a later alias; it alone would not establish the historical endpoint.

Under the single-response assumption, total work is **16,808–25,000 tokens**. The central estimate is **18,000 tokens**, comprising **14,500 assumed input tokens and 3,500 assumed output tokens**. These components reproduce the reported $0.25 at the original prices. Neither component is observed.

This choice accounts for the actual experiment. It included a GPT-3.5 model with a 16K context window, while the GPT-4 prompt requests an explanatory report on all checklist items. An input scale around 14,500 tokens and a substantial output below 4,096 are compatible with those conditions. The original interval midpoint of 20,904 tokens would infer 18,856 input tokens. Different model-specific prompts prevent a strict cross-model bound, but the smaller input estimate is more consistent with the study's whole-document setup.

As a diagnostic, at the same assumed input scale the reported GPT-3.5 cost of $0.05 permits 1,625 output tokens using its original $3/$4 per million rates, for 16,125 total tokens. GPT-4-32k's $1.24 permits about 3,083 output tokens at $60/$120 per million. The prices come from OpenAI's [June 2023 update](https://openai.com/index/function-calling-and-other-api-updates/) and [GPT-4 launch](https://openai.com/index/gpt-4-research/). These checks allow different outputs and do not establish equal prompts, native lengths or a measured mean. The paper's 16,000-token model-selection threshold is context capacity, not an observed prompt length.

The full original contracts, checklists and outputs were not published, so no selected replacement contract is presented as an exact token reconstruction. The original midpoint remains an alternate in calculations.json. The single-response range is about **7% below to 39% above** the new central estimate. Including rounding of the reported cost to the nearest cent widens the token bounds to 16,308–25,500. Multiple responses remove the per-contract output cap and require the wider price-only range. If reported costs omit unsuccessful paid requests, one additional comparable request doubles work. These scenarios are not confidence intervals and remain conditional on the source cost being correct.

Use the existing shared GPT-4-1106 assumption of 275B active parameters and **550 billion FLOPs/token**:

`18,000 × 550,000,000,000 = 9.9 × 10^15 FLOPs`.

The coefficient is a shared architectural estimate, not a provider disclosure. Half/double active size gives half/double compute. Count full input and output under the 2P approximation; no cache decomposition or helper calls are reported. The source’s preparation/prompt-development work is excluded from this inference task, just as prior lawyer instruction is outside each review. No model or legal service is being run here.

### Limits worth retaining

The API-cost estimate is the weak part of this point. Other models’ costs in the same table, particularly the very small Claude total for a full contract, raise a source-consistency concern. They are not silently corrected. The other GPT costs are only plausibility diagnostics for the assumed input scale, not equations solved under an equal-output assumption. The GPT-4 number itself is arithmetically feasible at the documented rates, but only the authors’ missing usage records could verify it. The dataset marks compute as derived_assumed_inputs.

No concrete mismatch in supplied task or scoring is identified for the selected junior-lawyer comparison. Missing documentation alone does not create a comparison flag. The estimate is useful as a coarse, explicitly cost-derived point; it should not be mistaken for measured FLOPs.

### Reproduction

Standard-library Python, no network or model calls:

```sh
python3 research/contract-review/recompute.py --sources agent-work/sources/contract-review --output /path/to/new-calculation.json
```

From the candidate folder use research/recompute.py and sources. Source hashes, extracted factual inputs, original PDFs and pricing/limit locators are retained. The calculator requires a new output path and preserves source files.
