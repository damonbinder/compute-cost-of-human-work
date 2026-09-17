# Active-parameter ranges: where each low and high bound comes from

*Created 2026-09-14 10:36.*

## TL;DR

`models.csv` now carries `active_parameters_low` and `active_parameters_high` on all 133 rows whose
`active_parameters_basis` is `estimated`, and on no other row. 104 of the 133 take a range stated
outright in `accepted-priors.csv`, in one of the three prior reports, or in the row's own note. The
other 29 are set here, by the reasoning the reports use for that model's class, and every one of
them has a line below. No central estimate moved, and no central falls outside its own range. The
median range spans a factor of 5.0, from 0.45x the central to 2.14x it, which is the shape the
grade-C priors in the reports already had.

## What the bounds mean

The bounds are the sensitivity range the prior argues, not a confidence interval. A row's FLOPs per
token is twice its active parameter count, so a bar from low to high is exactly the factor by which
that row's compute figure moves if the parameter prior is wrong in the direction of either bound.
Reported counts carry no bounds: the bar exists to show parameter-count uncertainty, and a reported
count has none worth drawing. `not_applicable` rows carry none either.

Precedence, where more than one source states a range: `accepted-priors.csv` first, then the prior
report for that provider (`anthropic.md`, `openai.md`, `google-xai-others.md`), then the row's own
note in `models.csv`. The reports are the later and more considered analysis, so where a row note
and its report disagree the report wins. Eight rows disagree that way and are listed at the end.

## Ranges set here

These rows have no stated range in any source. Each takes the range its class is argued to, and the
line says which argument.

**GPT-4 Turbo — 110-350B on a 275B central.** `gpt-4-1106-preview`, `gpt-4-0125-preview`,
`gpt-4-turbo-2024-04-09`. `openai.md` proposes 175B for these three and does not carry it, calling
the move "a judgment call rather than a finding", and names 118B as the geometric midpoint between
GPT-4 and GPT-4o that it thinks overshoots. The low bound covers that midpoint with room below it;
the high bound is GPT-4 original's own high, since family coherence is the reason 275B stands.

**GPT-4o — 25-100B on a 50B central.** `gpt-4o-2024-08-06`, `gpt-4o-2024-05-13`,
`gpt-4o-2024-11-20`, `gpt-4o-metr`, `gpt-4o-arc-alias`, `gpt-4o-audio-preview-2024-10-01`,
`gpt-4.1-2025-04-14`. Epoch's 200B total is stated as able to be "off by a factor of 2", which sets
the low bound at a quarter-activated 100B total. The high bound is Epoch's own pessimistic case, the
400B total that gives 100B active. GPT-4.1 joins the class because `openai.md` holds it at or below
GPT-4o's active count on serving evidence.

**o3 — 20-100B on a 50B central.** `o3-2025-04-16`, `o3-codeforces-checkpoint`. The report bounds
o3 "at GPT-4o scale or smaller" from a sustainable price below GPT-4o's, so the high bound is
GPT-4o's and the low bound sits below GPT-4o's to carry the "or smaller".

**GPT-4.1 mini — 10-50B on a 24B central.** Two lines agree at 24-25B and neither is architectural.
Grade-C class default, 0.4x to 2.1x, the band the reports give comparable mini-tier priors.

**Early ChatGPT — 60-200B on a 175B central.** `chatgpt-gpt35-2022`. The central is a GPT-3-scale
proxy for the davinci-lineage backend the product ran from 30 November 2022 to 12 February 2023. The
low bound was 12B until 2026-09-16, read across from the GPT-3.5 Turbo reconciliation; that model
did not serve the product in this window, and the floor is now the 60B the 90% cost reduction "since
December" supports, per `openai.md#chatgpt-backend-2022-23`. The high bound is GPT-3's own count.

**davinci-002 — 40-200B on a 175B central.** `davinci-002-metr`. `openai.md` states the low bound
directly, to carry the tenfold price drop from the legacy davinci endpoint. The high bound is GPT-3's
count with rounding room, since nothing argues the alias is larger than the model it stands in for.

**Kimi K3 — 85-165B on a 104B central.** The 2.78T total is confirmed by the safetensors index; only
the activation is an aggregator figure at Speculative confidence. Applying the reference class's own
2026 sparsity span of 17-33x to that total gives 84-164B, rounded.

**Exact counts with an identity gap — 0.8x to 1.2x.** `grok-2-1212` (115B), `open-mistral-7b`
(7.3B), `text-davinci-002` (175B). Each number is grade A and each row is `estimated` only because
the weights cannot be tied to the API revision or endpoint the row names. There is no size argument
to range over, so the band is a conventional allowance for the identification, not for the
arithmetic.

**Architecture-derived research models — 0.9x to 1.1x.** `gulordava-english-lstm-650`, the seven
`implicit-cot-gpt2-*` rows, and the two `fair-negotiator-2017-*` rows. These counts are computed
from published architectures, and the only live uncertainty is a counting convention: tied against
untied embeddings, unused input-vocabulary rows, one extra special token. Those move the count by a
few percent, and the band is a conservative stand-in for them. These bars are the narrowest in the
file by design.

## Where a row note and its report disagree

The columns follow the report. These eight row notes still quote the older range and should be
reconciled when their notes are next touched.

| model_id | Row note | Report | Applied |
|---|---|---|---|
| gpt-5-6-luna | 3-24 | 3-20 | 3-20 |
| claude-sonnet-4 | 50-200 | 45-220 | 45-220 |
| claude-opus-4-8 | 25-400 | 40-240 | 40-240 |
| claude-opus-5 | 30-300 | 45-260 | 45-260 |
| gemini-1.5-pro-naturalplan | 30-300 | 35-250 | 35-250 |
| gemini-1.5-pro-hourvideo | 30-300 | 35-250 | 35-250 |
| gemini-3-pro-preview | 30-300 | 50-320 | 50-320 |
| qwq-plus | 16-72 | 20-72 | 20-72 |

Units are billions of active parameters.

## Rows the reports hold at a central their own range is not centred on

The 2026-09-13 ruling took only the enumerated changes, so several rows keep a central the report
recommended moving while taking the range the report drew around the value it recommended. Every
one of these centrals still falls inside its range, and the gap is the report's proposal rather
than an inconsistency: `gemini-3-pro` and its three family members at 100B inside 50-320B drawn
around 130B, `grok-4.20-beta-0309b-reasoning` at 115B inside 25-180B drawn around 70B,
`gpt-4.5-preview-2025-02-27` at 600B inside 400-1600B drawn around 800B, the three o1 records at
50B inside 25-200B drawn around 60B, `qwen3.7-max` at 100B inside 50-150B drawn around 90B, and
`claude-2.0` and `claude-2.1` at 100B inside 60-250B drawn around 130B.
