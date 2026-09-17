# Shared list-price table for cost backfills

*Created 2026-09-13 14:12.*
*Last revised 2026-09-13 18:55 (OpenAI cache-write charge on GPT-5.6 and later).*

## TL;DR

`list-prices.csv` carries 313 rows covering all 285 model records in the two registries — one row
per (model, provider, price period). **152 models have a published per-token list price**; 36 are
open weights the row's own source ran on a self-hosted endpoint and 95 were never sold through a
per-token API, so both get a row with blank prices and a stated reason. Two more (Whisper tiny.en
and large-v2) are API-served but billed per audio minute, not per token. **Twenty models changed
price during their life and carry more than one period** — the ones that will bite a backfill are
`gpt-4o-2024-05-13` (never cut to $2.50/$10, unlike the alias), `o3` (80% cut on 2025-06-10),
the three GPT-5.6 models (Terra and Luna cut on 2026-07-30, Sol on 2026-08-21),
`o1-mini` ($3/$12 until 2025-01-30), DeepSeek's four repricings, Gemini 1.5's 2024-10-01 cut, and
Gemini 2.5 Flash's move off a separate thinking rate at GA. **Two providers bill reasoning tokens at
a rate other than the ordinary output rate** and a backfill that misses this will understate a
reasoning row's cost by up to 5.8x: Gemini 2.5 Flash **Preview** (thinking $3.50 against
non-thinking $0.60) and Alibaba's Qwen-Plus and Qwen-Turbo (thinking $4.00 against $1.20, $0.50
against $0.20). Everywhere else reasoning tokens sit inside the output counter and bill at the
output rate.

## What a backfill agent must know before pricing anything

1. **Pick the row whose `price_sheet_start` <= run date and whose `price_sheet_end` is blank or >=
   run date.** A blank end means the sheet was still in force at retrieval (2026-09-13).
2. **A dated snapshot is not the alias.** `gpt-4o-2024-05-13` stayed at $5/$15 for its whole life
   and was never prompt-cache-eligible; the `gpt-4o` alias fell to $2.50/$10 on 2024-08-06. The two
   METR/ARC GPT-4o records have the alias treatment, because their registry entries say the snapshot
   is unspecified; if a row turns out to be pinned to 05-13, use the 05-13 line instead.
3. **Check `reasoning_billed_as` before pricing a reasoning row.** `output` means the counter
   already contains the reasoning tokens and the output rate applies. `separate_thinking_rate` means
   the provider publishes a distinct, higher rate and `long_context_rule` gives it.
   `no_reasoning_tokens` means the model has no hidden reasoning channel — visible chain of thought
   from an open model is ordinary output.
4. **Cached input is a *separate rate on a separate counter*, not a discount on input.** The dataset
   already excludes cache reads from the FLOP term; cost must not. Price cache reads at
   `cached_input_usd_per_m` and gross input at `input_usd_per_m`.
5. **Three providers charge for the cache write, and OpenAI is one of them from GPT-5.6 onward.**
   Anthropic bills 1.25x base input for the 5-minute write and 2x for the 1-hour write, named in
   `long_context_rule` where it differs. Alibaba charges 1.25x for explicit cache creation.
   **OpenAI charges 1.25x base input on GPT-5.6 and later only** — the seven rows for
   `gpt-5-6-sol`, `gpt-5-6-terra`, `gpt-5-6-luna` and `gpt-6-astra`. Every other OpenAI row, and
   every row from every other provider, charges nothing to write, and the blank cell says so.
   `research/cost/openai-cache-write.md` has the dated evidence and the exposure.
6. **Long-context surcharges are real and are in `long_context_rule`**, not in the price columns.
   Google tiers Pro-class models at a 200k-prompt boundary (128k on the 1.5 generation); xAI tiers
   every current model at 200k; OpenAI's 2026 models bill a long-context variant at 2x standard;
   Anthropic charges nothing extra for the 1M window on Claude 4.6 and later.
7. **Batch is 50% off nearly everywhere — but not at xAI (20%, and only on four models) and not at
   all at DeepSeek, Moonshot or Z.ai.** `batch_discount` is the fraction off; `none` means no batch
   API for that model at that date.
8. **Claude 4.7 and later use a different tokenizer** that produces about 30% more tokens for the
   same text. A cost transferred from an earlier Claude by token count will understate.

## Conventions

- All prices are USD per million tokens, first-party, **standard tier**: not batch, not flex, not
  priority, not fast mode, global routing, no data-residency multiplier.
- Where a provider tiers by prompt size, the price columns carry the **lower (short-prompt) tier**
  and `long_context_rule` carries the upper tier in full.
- Where a provider publishes peak and off-peak rates (DeepSeek), the price columns carry **peak**,
  and `long_context_rule` carries the off-peak rate and window.
- `price_sheet_end` blank = still in force at retrieval. A filled end date is the last day the sheet
  applied, inclusive.
- `provider` is the entity whose sheet the price comes from: `openai`, `anthropic`, `google`, `xai`,
  `deepseek`, `alibaba`, `mistral`, `moonshot`, `zai`, `together`, `fireworks` — or `self_hosted`
  (open weights the row's source ran itself, no list price) or `not_api_served` (never sold per
  token).
- Blank price cells mean the provider published no rate for that category, not zero. A genuine zero
  is written `0.00` (only Gemini 2.5 Pro's free experimental window).
- `batch_discount` is the fraction off standard (`0.5`, `0.2`) or `none`.
- `long_context_rule` doubles as the row's note column; it carries context tiering first and any
  other qualification after it.

## Coverage

| Class | Models | Rows |
|---|---|---|
| Priced at a first-party API | 123 | 146 |
| Priced at a third-party host only | 29 | 30 |
| API-served, not token-priced (Whisper) | 2 | 2 |
| Open weights, self-hosted by the row's source, no list price | 36 | 36 |
| Never sold through a per-token API | 95 | 95 |
| **Total** | **285** | **313** |

Four models carry both a first-party and a third-party row, because the registries' own sources used
the third-party host while a first-party price also exists: `deepseek-v3`, `deepseek-v3-0324`,
`deepseek-r1`, `deepseek-r1-0528` (DeepSeek's own API and Together). Counting those on the
third-party side as well, 33 models have a Together or Fireworks price across 34 rows.

Models carrying more than one price period: `gpt-4o-metr`, `gpt-4o-arc-alias`, `gpt-4o-2024-08-06`,
`gpt-4o-mini-2024-07-18`, `o1-preview-2024-09-12`, `o1-mini-2024-09-12`, `o3-2025-04-16`,
`gpt-5-6-sol`, `gpt-5-6-terra`, `gpt-5-6-luna`,
`gemini-1.5-pro-001`, `gemini-1.5-pro-hourvideo`, `gemini-1.5-pro-naturalplan`,
`gemini-1.5-flash-001`, `gemini-2.5-pro-03-25`, `claude-3-5-haiku-20241022`, `deepseek-v3`,
`deepseek-v3-0324`, `deepseek-r1`, `deepseek-r1-0528`.

### Self-hosted, no list price (36)

The registry rows that use these ran them on their own hardware or on an endpoint with no published
price. The BALROG submissions are the largest group: `llama-3.2-1b-instruct`, `llama-3.2-3b-instruct`,
`qwen2.5-7b-instruct`, `deepseek-r1-distill-qwen-32b`, `reka-flash-3` and `phi-4` all ran on
self-hosted vLLM or NVIDIA NIM endpoints, which is why the study's own note treats their cache
behaviour as undocumented. The rest are open-weight research checkpoints with no hosted endpoint at
all (Latxa, Swallow, AceGPT, Llammas, Code Llama, MultiPL-T StarCoder, RoBERTa, NLLB, OpenVLA, the
implicit-CoT GPT-2 fine-tunes, Gemma 2 and 3, Qwen1.5, Qwen2.5-Math, Eurus-2-PRIME, RetroDFM-R,
Phi-3-medium, DeepSeek-Prover-V2). Where a third-party rate exists but no row names that host, the
rate is stated in `long_context_rule` as a reference without being promoted into the price columns.

### Never API-served (95)

Robotics policies, Atari and board-game agents, CNNs and detectors, speech and vision models,
BabyLM-scale research models, internal checkpoints (`openai-ns-2026-09-internal`,
`anthropic-internal-research-flt-2026-08`, `o3-codeforces-checkpoint`, the three pre-release GPT-4
snapshots, the three 2021 Codex research models), and two products that are not token-metered at all
(`github-copilot-2022-08`, a seat subscription; `chatgpt-gpt35-2022`, the free web preview).
`gemini-2.0-pro-exp-02-05` and `gemini-3-deep-think-preview` are here too: both were preview
endpoints that never carried a paid per-token rate.

### Where a third-party host was used

Recorded where the registry or a research note names the host:

| Models | Host | Where the host is named |
|---|---|---|
| Llama 3.1-8B, Llama 3.3-70B, Llama 3.1-405B, DeepSeek-R1 | Together | Cost-of-Pass Table 4: "open-source models are queried through a single provider ... (TogetherAI, in our case)" |
| DeepSeek models in the HAL GAIA runs | Together | `research/gaia.md`: "The Together-hosted DeepSeek runs report no cache counter at all" |
| Llama-4-Maverick-17B-128E-Instruct-FP8 | Together | `research/videogamebench.md`: the harness billed at `together_ai/...` rates |
| DeepSeek-R1-0528 on Kaggle Game Arena | Together-consistent $3/$7 | `research/game-arena.md` recovers a "$3/$7 per million host pair" from the cost column; Together's 2025-06 sheet is exactly that |
| Kimi K2.5, DeepSeek V3.2 in the Epoch runs | Fireworks | Epoch's Inspect log model ids `fireworks/kimi-k2p5`, `fireworks/deepseek-v3p2` |

For every other open-weight model with no named host, the Together or Fireworks serverless rate is
given where one is published (the size-bucket rates in particular), because a list price with a
named provider is more useful to a backfill than a blank, and `long_context_rule` says so on the
row. GLM-5 and Kimi K2.5 also appear in Epoch logs under first-party ids (`zhipu/glm-5`,
`moonshot/kimi-k2.5`); those are priced first-party.

## Per-provider notes on cached and reasoning tokens

### OpenAI

Prompt caching launched 2024-10-01 and initially covered only the 4o and o1 families; models older
than that (GPT-4, GPT-4 Turbo, GPT-3.5 Turbo, the davinci completions endpoints) never had a cached
rate, and the table leaves those cells blank. The **cached-input multiple changed twice**: 0.5x on
the 4o family, o1, o1-mini and o3-mini; 0.25x on GPT-4.1 and on o3 and o4-mini; 0.1x from GPT-5
onward. Read it off the row rather than applying a single multiplier across the ladder. Caching is automatic on
prefixes of at least 1,024 tokens and is not opt-in, so a run with a long shared prefix will have
cached reads even if the harness never asked for them — check the usage counter rather than
assuming. Reasoning tokens are inside `completion_tokens` and bill
at the output rate; the pricing page says nothing about them, which is itself the fact worth
recording. Batch and flex are both 50%. From 2026 the larger models publish a long-context variant
at 2x standard, and models released after 2026-03-05 carry a 10% uplift for regional data residency.
**The cache write became a charge on 2026-07-09 and applies to GPT-5.6 and later only.** The
Cache writes column reached `developers.openai.com/api/docs/pricing` on GPT-5.6 launch day: the
2026-07-07 capture has no such column anywhere, and the 2026-07-09 capture carries it in every tier
table at 1.25x input on the three GPT-5.6 rows, with `-` on gpt-5.5, gpt-5.5-pro, the whole 5.4
line and every older model. The live page still reads that way, and the prompt-caching guide states
it as a rule: "For GPT-5.6 and later, cache writes cost 1.25x the standard, uncached input-token
rate", against "No additional cache-write charge" for GPT-5.5 and for "Other earlier models". So
`cache_write_usd_per_m` is filled on the seven GPT-5.6 and GPT-6 rows and blank on the other 53
OpenAI rows, where the blank means the page prints `-` and nothing is billed. The charge is **not
additive**: `input_tokens` partitions into ordinary, cached-read and written tokens, and each
bucket bills at its own rate. Written tokens are reported separately as
`usage.input_tokens_details.cache_write_tokens`, but no harness or leaderboard behind any row in
this folder records that counter, so a row's uncached-input residual silently contains its writes.
`research/cost/openai-cache-write.md` bounds what that costs, row by row.

The single largest trap is **o3**: $10/$2.50/$40 from 2025-04-16, cut 80% to $2/$0.50/$8 on
2025-06-10 with the weights unchanged ("Same exact model - just cheaper"). Any o3 row dated before
2025-06-10 costs five times what the current sheet implies.

The **GPT-5.6 family repriced twice in its first six weeks**, and the current sheet is not the rate
the family launched at. All three launched 2026-07-09 at $5.00/$0.50/$30.00 (Sol), $2.50/$0.25/$15.00
(Terra) and $1.00/$0.10/$6.00 (Luna). On 2026-07-30 OpenAI cut Terra 20% and Luna 80%, permanently.
On 2026-08-21 it cut Sol to $4.00/$0.40/$20.00 under a **promotion** the page marks "available at
least through November 21, 2026" — the only promotional rate anywhere on OpenAI's sheet, and the one
row here whose current price has a stated expiry. Sol's row therefore reverts to $5.00/$0.50/$30.00
if the promotion lapses; the Terra and Luna cuts carry no such condition. A July 2026 workload priced
off the current sheet is 1.25x low on Sol input, 1.5x low on Sol output, 1.25x low on Terra and 5x
low on Luna. Both harnesses that publish their own price table — ALE-Bench's `calc_cost.py` and Andon
Labs' Vending-Bench 2 — still bill the whole family at the launch rates, so a leaderboard dollar
figure for these models is a launch-rate figure regardless of when it was published.
`research/cost/gpt56-repricing.md` has the capture-by-capture evidence and the affected rows.

### Anthropic

**Charges for the cache write** on every model, and has since caching launched: 1.25x base input
for the 5-minute TTL, 2x for the 1-hour TTL. OpenAI reached the same 1.25x write on GPT-5.6 in
July 2026, and Alibaba charges it on explicit cache creation, so Anthropic is no longer alone; it
is still the only one that charges it everywhere.
Cache reads are 0.1x base input on every model except Claude Fable 5.1 and Mythos 5.1, where they
are 0.025x. Caching is opt-in per request via `cache_control`,
so a harness that never sends the field produces zero cache tokens and pays full input on every
call — `research/balrog.md` and `research/gaia.md` both establish exactly this for their Claude
runs, which means those rows' input is gross and must be priced gross. Caching arrived with the
2024-08-14 public beta (Claude 3.5 Sonnet and Claude 3 Haiku) and reached Claude 3 Opus and Claude
3.5 Haiku later that autumn; Claude 3 Sonnet never got it, and Claude 2.x had neither caching nor a
Batch API. Those availability dates come from the feature announcements rather than from a retained
price sheet, so treat a cache rate on a mid-2024 Claude row as needing a check against the run's own
usage counters. The Batch API arrived 2024-10-08 at 50%.
Extended-thinking tokens are inside `output_tokens` and bill at the output rate. Claude 4.6 and
later include the full 1M window at standard rates, so there is no long-context surcharge to apply;
`inference_geo: "us"` multiplies every category by 1.1, and Bedrock/Vertex regional endpoints carry
a 10% premium. Claude 4.7 and later use a newer tokenizer producing about 30% more tokens for the
same text.

Price levels moved once in a way that matters: Opus went from $15/$75 (Opus 4, 4.1) to $5/$25 with
Opus 4.5 on 2025-11-24 and has stayed there. Claude 3.5 Haiku launched at $1/$5 and was cut to
$0.80/$4 about two weeks later.

### Google

Context caching is a separate lower input rate (roughly 0.1x, and 0.25x on the 1.5 generation) plus
a **storage charge per token-hour** — $1.00/1M/hour on Flash-class, $4.50 on Pro-class — which is
the one recurring charge in this whole table that is not per token processed. Implicit caching needs
a shared prefix of at least 1,024 tokens (2,048 on Pro), which is why `research/balrog.md` concludes
no Gemini caching occurred in those runs.

Thinking tokens: every current row is labelled "Output price (including thinking tokens)", so they
bill at the output rate. The exception is **Gemini 2.5 Flash Preview (05-20)**, which published two
output rates — $0.60 non-thinking and $3.50 thinking — and the split disappeared at GA on
2025-06-17 when the model repriced to $0.30/$2.50. A 2.5-Flash-preview row priced at the GA rate
will be wrong in whichever direction its thinking fraction runs.

Prompt-size tiering: 128k boundary on Gemini 1.5, 200k on 2.5 Pro and 3.x Pro, none on Flash.
Gemini 1.5 Pro and Flash were cut hard on 2024-10-01 (Pro $3.50/$10.50 to $1.25/$5.00; Flash
$0.35/$1.05 to $0.075/$0.30), which straddles several of the 1.5-era rows. Batch is 50%. The 3.6,
3.7 and 3.8 Flash prices are promotional and double on 2027-01-01.

### xAI

The only provider whose batch discount is not 50%: 20%, and only on grok-4.3, the two grok-4.20-0309
variants and grok-4.20-multi-agent. Prompt caching is automatic and free to write, with a separate
cached-input rate. Every current model is tiered at a 200k-prompt boundary at exactly 2x. Reasoning
tokens are "billed for the model used in the request" at standard rates. Grok 2, Grok 3, Grok 3 mini
and Grok 4 have been removed from the page and their prices come from dated secondary sources
(xAI's own launch post for Grok 2); none of them published a cached-input rate.

### DeepSeek

Cache hits are a separate input rate at roughly 0.1x with **no cache-write charge**. Reasoning is
explicit in the sheet's own footnote: "The output token count of deepseek-reasoner includes all
tokens from CoT and the final answer, and they are priced equally." No batch API. The price history
is the busiest of any provider and a run date is essential:

| Window | deepseek-chat (hit/miss/out) | deepseek-reasoner (hit/miss/out) |
|---|---|---|
| 2024-12-26 to 2025-02-08 | 0.014 / 0.14 / 0.28 (launch discount) | — |
| 2025-01-20 to 2025-08-20 | 0.07 / 0.27 / 1.10 | 0.14 / 0.55 / 2.19 |
| 2025-08-21 to 2025-09-28 | 0.07 / 0.56 / 1.68 | 0.07 / 0.56 / 1.68 |
| 2025-09-29 onward | 0.028 / 0.28 / 0.42 | 0.028 / 0.28 / 0.42 |

From 2025-02-26 to 2025-08-20 an off-peak window (16:30-00:30 UTC) cut deepseek-chat 50% and
deepseek-reasoner 75%; the completion timestamp decided the tier. That discount was withdrawn with
the V3.1 sheet. The current sheet has a different structure again: deepseek-flash and deepseek-v4-pro
with a peak window of 01:00-04:00 and 06:00-10:00 UTC on weekdays and off-peak at half.

### Alibaba

Explicit cache creation is billed at **125% of the standard input price** and cache hits at 10% —
the same shape as Anthropic. Qwen-Plus and Qwen-Turbo publish a **separate, higher thinking-mode
output rate** ($4.00 against $1.20, and $0.50 against $0.20), which together with Gemini 2.5 Flash
Preview is the only place in the table where reasoning is not billed at the ordinary output rate.
Batch is 50% on the Max/Turbo/Flash lines and is not published on the Plus line. Prices are tiered
by prompt size on the Plus and Flash lines; the 0-256K tier is what the table carries.

### Mistral

Batch is 50% and cached input is "-90% on input token", but Mistral publishes no per-model cached
rate, so `cached_input_usd_per_m` is blank throughout and a backfill that needs it should apply 0.1x
and say so. None of the 2024-2025 model versions is still on the live page; every Mistral figure in
the table comes from the archived 2024-11-01 sheet or, for `mistral-large-2402`,
`mistral-large-2411` and Mistral Small 3, from dated secondary sources. No Mistral model in scope
has a reasoning channel.

### Moonshot, Z.ai

Both bill a cache hit at a separate lower input rate and charge nothing for the write (Z.ai's cached
input storage is explicitly "Limited-time Free"). Neither publishes a batch discount or a separate
reasoning rate, so thinking tokens bill at the output rate. Moonshot retired kimi-k2.5 and the
moonshot-v1 series on 2026-08-31, so a K2.5 row dated after that has no live first-party price and
should use the Fireworks endpoint Epoch actually used.

### Together, Fireworks

Both price open weights **flat** in the 2024-2025 era — input and output at the same rate, by
parameter-count bucket, with a handful of named models broken out. Together moved to split
input/output rates during 2025 (Llama 4 at launch; DeepSeek-R1 changed from $7.00 flat to $3.00
input / $7.00 output between the 2025-02 capture and 2025-03-26, the latest date the split rate
can have started on the Cost-of-Pass run records; the row starts there). Neither publishes a cached-input
rate for these endpoints, and neither publishes a batch discount, so `batch_discount` is `none` and
the cache columns are blank on every third-party row. That blank is a real property of the price
sheet, not missing research: a cost inverted from one of these rates cannot be decomposed into
cached and uncached input.

## What is weakest here

- **The Mistral 2402/2411 and Small 3 figures, and the Grok 2/3/4 and Kimi K2/K2.5 figures, rest on
  dated secondary sources**, because the first-party pages have dropped them and the archived xAI
  and Moonshot pages render their tables client-side, so the archived HTML carries no numbers. Each
  is listed in `agent-work/sources/cost/live/secondary-price-points-2026-09-13.md` with what corroborates it.
- **`gpt-3-davinci-175b` is the one price I would not lean on.** The 2023-06 sheet lists InstructGPT
  Davinci at $0.02/1K and does not name the base `davinci` endpoint separately; the launch-era rate
  of $0.06/1K is not retrieved. The row says so.
- **Third-party size-bucket rates assigned to models no registry row places at a host** (Gemma is
  the clearest case, and it is left unpriced for that reason) are a convenience, not evidence about
  what any run cost. Every such row says which bucket it came from.
- **`o1-mini`'s 2025-01-31 reprice date is inferred** from the alignment of the o-series mini tier
  when o3-mini launched. It is not corroborated by Cost-of-Pass: that experiment's retained
  records price o1-mini at $3.00/$12.00 while pricing o3-mini at $1.10/$4.40 in the same March
  2025 runs, most likely a stale hardcoded rate in its config, so those records neither confirm
  nor date the change. The 2024-12-20 capture establishes the earlier $3/$12 directly; the
  changeover day does not have a first-party source.

## gpt-4-0314 is the 32K tier

The March 2023 GPT-4 sheet carries two tiers, 8K at $30 input and $60 output and 32K at
$60 and $120, and nothing on the sheet says which one a given run used. METR's exports
settle it for `gpt-4-0314`: 1,546 HCAST runs bill at 60.76 USD per million counted tokens,
which exceeds the 8K tier's output price and so cannot be produced by any mix of input,
cached and output tokens at that tier, and which sits 1.3% above the 32K tier's input
price with the residual accounted for by a 1% output share. HCAST tasks need the long
context, so the 32K deployment is also what the runs would have used. The row moved to
$60 and $120 on 2026-09-16. Only the six METR `gpt-4-0314` rows read this card and all
six carry METR's own reported `ai_cost_usd`, so no value in `points.csv` moves with it.
`gpt-4-0613` and `gpt-4-original-unspecified` keep the 8K tier: no comparable billing
exists for them, and `gpt-4-original-unspecified` names an unidentified deployment.

## Reproducing

```
python3 research/cost/build_list_prices.py \
    "../AI Compute vs Human Time/dataset/models.csv" \
    models.csv \
    research/cost/list-prices.csv
```

The script holds the price spec inline and reads the two registries only to fix the model list and
its ordering; it writes a new CSV and touches nothing else. Any model in either registry that the
spec does not name gets a blank-price row rather than being silently dropped, so the output always
has every model_id. Retained price sheets are under `agent-work/sources/cost/`, with `agent-work/sources/cost/PROVENANCE.md`
mapping every file to its URL and capture date.
