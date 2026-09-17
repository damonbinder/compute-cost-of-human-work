#!/usr/bin/env python3
"""Build research/cost/list-prices.csv from the retained price sheets.

Usage:
    python3 build_list_prices.py <dataset_models.csv> <claude_rows_models.csv> <out.csv>

Dependencies: Python 3 standard library only.

Every row is one (model_id, provider, price period). Prices are USD per million
tokens, first-party standard tier unless the provider column says otherwise.
The evidence for each figure is the file named in source_url; the retained
copies are under agent-work/sources/cost/.
"""
import csv, sys

RETRIEVED = "2026-09-13"

# ---------------------------------------------------------------- source URLs
OA      = "https://developers.openai.com/api/docs/pricing"
OA24_05 = "https://web.archive.org/web/20240519124245/https://openai.com/api/pricing/"
OA24_12 = "https://web.archive.org/web/20241220/https://openai.com/api/pricing/"
OA25_03 = "https://web.archive.org/web/20250320/https://openai.com/api/pricing/"
OA25_04 = "https://web.archive.org/web/20250425/https://openai.com/api/pricing/"
OA25_06 = "https://web.archive.org/web/20250620/https://openai.com/api/pricing/"
OA23_06 = "https://web.archive.org/web/20230601/https://openai.com/pricing"
OALAD   = "https://x.com/OpenAIDevs/status/1932532777565446348"
OA26_07 = "https://web.archive.org/web/20260729103109/https://developers.openai.com/api/docs/pricing"
OA26_08 = "https://web.archive.org/web/20260821103049/https://developers.openai.com/api/docs/pricing"
AN      = "https://platform.claude.com/docs/en/about-claude/pricing"
AN24_04 = "https://web.archive.org/web/20240401/https://www.anthropic.com/pricing"
GG      = "https://ai.google.dev/gemini-api/docs/pricing"
GG24_07 = "https://web.archive.org/web/20240701/https://ai.google.dev/pricing"
GG24_12 = "https://web.archive.org/web/20241201/https://ai.google.dev/pricing"
GG25_06 = "https://web.archive.org/web/20250601/https://ai.google.dev/gemini-api/docs/pricing"
GG25_12 = "https://web.archive.org/web/20251215/https://ai.google.dev/gemini-api/docs/pricing"
XAI     = "https://docs.x.ai/developers/pricing"
XAI2    = "https://x.com/xai/status/1868045132760842734"
DS      = "https://api-docs.deepseek.com/quick_start/pricing"
DS25_01 = "https://web.archive.org/web/20250105/https://api-docs.deepseek.com/quick_start/pricing"
DS25_02 = "https://web.archive.org/web/20250210/https://api-docs.deepseek.com/quick_start/pricing"
DS25_03 = "https://web.archive.org/web/20250301/https://api-docs.deepseek.com/quick_start/pricing"
DS25_09 = "https://web.archive.org/web/20250905/https://api-docs.deepseek.com/quick_start/pricing"
DS25_10 = "https://web.archive.org/web/20251015/https://api-docs.deepseek.com/quick_start/pricing"
MI      = "https://mistral.ai/pricing/api"
MI24_11 = "https://web.archive.org/web/20241101/https://mistral.ai/technology/"
ALI     = "https://www.alibabacloud.com/help/en/model-studio/model-pricing"
ALI25_04= "https://web.archive.org/web/20250401/https://www.alibabacloud.com/help/en/model-studio/models"
MOON    = "https://platform.kimi.ai/docs/pricing/chat"
ZAI     = "https://docs.z.ai/guides/overview/pricing"
TG      = "https://www.together.ai/pricing"
TG25_02 = "https://web.archive.org/web/20250215/https://www.together.ai/pricing"
TG25_06 = "https://web.archive.org/web/20250601/https://www.together.ai/pricing"
FW      = "https://docs.fireworks.ai/serverless/pricing"
SEC     = "agent-work/sources/cost/live/secondary-price-points-2026-09-13.md"
COP     = "../AI Compute vs Human Time/dataset/sources/cost-of-pass/paper.txt (Table 4)"

rows = []
def P(ids, provider, start, end, inp, cached, cwrite, out,
      reasoning, batch, longctx, url):
    """Add one price-period row for each model_id in ids."""
    if isinstance(ids, str):
        ids = [ids]
    for mid in ids:
        rows.append(dict(model_id=mid, provider=provider,
                         price_sheet_start=start, price_sheet_end=end,
                         input_usd_per_m=inp, cached_input_usd_per_m=cached,
                         cache_write_usd_per_m=cwrite, output_usd_per_m=out,
                         reasoning_billed_as=reasoning, batch_discount=batch,
                         long_context_rule=longctx, source_url=url,
                         retrieved=RETRIEVED))

def NOPRICE(ids, provider, note):
    """Model with no published per-token list price."""
    P(ids, provider, "", "", "", "", "", "", "not_applicable", "", note,
      "not_applicable")

# =========================================================== OPENAI ==========
# Prompt caching launched 2024-10-01 on the 4o and o1 families only; earlier
# periods therefore carry no cached-input rate. Batch API (50%) from 2024-04-15.
# Cache writes are free on every OpenAI model up to and including GPT-5.5: the
# Cache writes column reached the pricing page on 2026-07-09 with the GPT-5.6
# launch, and prints "-" on gpt-5.5 and every older row there. From GPT-5.6 on
# the write is billed at 1.25x the model's uncached input rate, so cwrite is
# filled on the GPT-5.6 and GPT-6 rows and blank everywhere else.
OAB, OAR, NOC = "0.5", "output", "none"

P("text-davinci-002", "openai", "2022-03-15", "2024-01-04", "20.00", "", "", "20.00",
  "no_reasoning_tokens", NOC,
  "one usage rate covers prompt and completion: the 2023-06 sheet lists InstructGPT Davinci at 0.0200 per 1K tokens. Endpoint deprecated 2024-01-04", OA23_06)
P("gpt-3-davinci-175b", "openai", "2022-09-01", "2024-01-04", "20.00", "", "", "20.00",
  "no_reasoning_tokens", NOC,
  "the base davinci completions endpoint shared the 0.0200 per 1K usage rate on the same sheet but is not named separately on it; the 2020-2022 launch-era rate (0.06 per 1K) was not retrieved from a first-party sheet", OA23_06)
P("davinci-002-metr", "openai", "2023-08-22", "", "2.00", "", "", "2.00", "no_reasoning_tokens", OAB,
  NOC, OA24_05)
# gpt-4-0314 is priced at the 32K tier, not the 8K one. METR's exports bill its
# 1,546 HCAST runs at 60.76 USD per million counted tokens, which exceeds the 8K
# tier's 60.00 output price and so cannot be produced by any mix of components at
# that tier, and sits 1.3% above the 32K tier's 60.00 input price. HCAST tasks need
# the long context, so the 32K deployment is also what the runs would have used.
P("gpt-4-0314", "openai", "2023-03-14", "2024-06-06",
  "60.00", "", "", "120.00", "no_reasoning_tokens", OAB,
  "the 32K tier; the 8K tier on the same sheet is 30.00 input, 60.00 output, and METR's per-run billing on this model rejects it", OA24_05)
P(["gpt-4-0613", "gpt-4-original-unspecified"], "openai", "2023-03-14", "2024-06-06",
  "30.00", "", "", "60.00", "no_reasoning_tokens", OAB, "gpt-4-32k tier: 60.00 input, 120.00 output", OA24_05)
P(["gpt-4-1106-preview", "gpt-4-0125-preview", "gpt-4-turbo-2024-04-09"], "openai", "2023-11-06", "",
  "10.00", "", "", "30.00", "no_reasoning_tokens", OAB, NOC, OA24_05)
P("gpt-3.5-turbo-1106", "openai", "2023-11-06", "", "1.00", "", "", "2.00", "no_reasoning_tokens", OAB, NOC, OA24_05)
P("gpt-3.5-turbo-0125", "openai", "2024-01-25", "", "0.50", "", "", "1.50", "no_reasoning_tokens", OAB, NOC, OA24_05)
P("gpt-3.5-turbo-instruct", "openai", "2023-09-18", "", "1.50", "", "", "2.00", "no_reasoning_tokens", OAB, NOC, OA24_05)
# GPT-4o
P("gpt-4o-2024-05-13", "openai", "2024-05-13", "", "5.00", "", "", "15.00", "no_reasoning_tokens", OAB,
  "the dated 05-13 snapshot kept 5.00/15.00 after the gpt-4o alias was cut to 2.50/10.00 on 2024-08-06, and never carried a cached-input rate", OA24_12)
P(["gpt-4o-metr", "gpt-4o-arc-alias"], "openai", "2024-05-13", "2024-08-05", "5.00", "", "", "15.00",
  "no_reasoning_tokens", OAB,
  "snapshot unspecified in the registry; priced as the gpt-4o alias. If the row is in fact pinned to 2024-05-13 the rate stays 5.00/15.00 throughout", OA24_05)
P(["gpt-4o-metr", "gpt-4o-arc-alias"], "openai", "2024-08-06", "2024-09-30", "2.50", "", "", "10.00",
  "no_reasoning_tokens", OAB, "gpt-4o alias rate", OA24_12)
P(["gpt-4o-metr", "gpt-4o-arc-alias"], "openai", "2024-10-01", "", "2.50", "1.25", "", "10.00",
  "no_reasoning_tokens", OAB, "gpt-4o alias rate; cached input 0.5x on the 4o family", OA24_12)
P("gpt-4o-2024-08-06", "openai", "2024-08-06", "2024-09-30", "2.50", "", "", "10.00",
  "no_reasoning_tokens", OAB, NOC, OA24_12)
P(["gpt-4o-2024-08-06", "gpt-4o-2024-11-20"], "openai", "2024-10-01", "", "2.50", "1.25", "", "10.00",
  "no_reasoning_tokens", OAB, "cached input 0.5x on the 4o family; later OpenAI models use 0.1x", OA24_12)
P("gpt-4o-mini-2024-07-18", "openai", "2024-07-18", "2024-09-30", "0.15", "", "", "0.60",
  "no_reasoning_tokens", OAB, NOC, OA24_05)
P("gpt-4o-mini-2024-07-18", "openai", "2024-10-01", "", "0.15", "0.075", "", "0.60",
  "no_reasoning_tokens", OAB, NOC, OA24_12)
P("gpt-4o-audio-preview-2024-10-01", "openai", "2024-10-17", "", "2.50", "", "", "10.00",
  "no_reasoning_tokens", NOC,
  "text rate shown; audio tokens billed separately at 100.00 input / 200.00 output", OA24_12)
# o-series
P(["o1-2024-12-17", "o1-metr"], "openai", "2024-12-05", "", "15.00", "7.50", "", "60.00", OAR, OAB, NOC, OA24_12)
P("o1-preview-2024-09-12", "openai", "2024-09-12", "2024-09-30", "15.00", "", "", "60.00", OAR, OAB, NOC, OA24_12)
P("o1-preview-2024-09-12", "openai", "2024-10-01", "", "15.00", "7.50", "", "60.00", OAR, OAB, NOC, OA24_12)
P("o1-mini-2024-09-12", "openai", "2024-09-12", "2025-01-30", "3.00", "1.50", "", "12.00", OAR, OAB, NOC, OA24_12)
P("o1-mini-2024-09-12", "openai", "2025-01-31", "", "1.10", "0.55", "", "4.40", OAR, OAB,
  "aligned to the o3-mini tier when o3-mini launched", SEC)
P("o3-mini-2025-01-31", "openai", "2025-01-31", "", "1.10", "0.55", "", "4.40", OAR, OAB, NOC, OA25_03)
P("o4-mini-2025-04-16", "openai", "2025-04-16", "", "1.10", "0.275", "", "4.40", OAR, OAB, NOC, OA25_04)
P("o3-2025-04-16", "openai", "2025-04-16", "2025-06-09",
  "10.00", "2.50", "", "40.00", OAR, OAB, NOC, OA25_04)
P("o3-2025-04-16", "openai", "2025-06-10", "",
  "2.00", "0.50", "", "8.00", OAR, OAB,
  "80% cut on 2025-06-10 with the weights unchanged: 'Same exact model - just cheaper'", OALAD)
NOPRICE("o3-codeforces-checkpoint", "not_api_served",
        "early evaluation checkpoint, never sold; the public o3 released 2025-04-16 listed at 10.00/2.50/40.00 and was cut to 2.00/0.50/8.00 on 2025-06-10")
P("gpt-4.5-preview-2025-02-27", "openai", "2025-02-27", "2025-07-14", "75.00", "37.50", "", "150.00",
  "no_reasoning_tokens", OAB, "API access withdrawn 2025-07-14", OA25_03)
P("gpt-4.1-2025-04-14", "openai", "2025-04-14", "", "2.00", "0.50", "", "8.00", "no_reasoning_tokens", OAB, NOC, OA25_04)
P("gpt-4.1-mini-2025-04-14", "openai", "2025-04-14", "", "0.40", "0.10", "", "1.60", "no_reasoning_tokens", OAB, NOC, OA25_04)
P("gpt-4.1-nano-2025-04-14", "openai", "2025-04-14", "", "0.10", "0.025", "", "0.40", "no_reasoning_tokens", OAB, NOC, OA25_04)
# GPT-5 family
P(["gpt-5", "gpt-5-high", "gpt-5-metr", "gpt-5-chat"], "openai", "2025-08-07", "",
  "1.25", "0.125", "", "10.00", OAR, OAB, NOC, OA)
P("gpt-5-mini-2025-08-07", "openai", "2025-08-07", "", "0.25", "0.025", "", "2.00", OAR, OAB, NOC, OA)
P("gpt-5-nano", "openai", "2025-08-07", "", "0.05", "0.005", "", "0.40", OAR, OAB, NOC, OA)
P("gpt-5-codex", "openai", "2025-09-15", "", "1.25", "0.125", "", "10.00", OAR, OAB,
  "priced at the GPT-5 rate; no separate Codex line on the price sheet", SEC)
P("gpt-5.1-2025-11-13", "openai", "2025-11-13", "", "1.25", "0.125", "", "10.00", OAR, OAB, NOC, OA)
P("gpt-5.2-2025-12-11", "openai", "2025-12-11", "", "1.75", "0.175", "", "14.00", OAR, OAB, NOC, OA)
P("gpt-5-3-codex", "openai", "2026-02-05", "", "1.75", "0.175", "", "14.00", OAR, OAB, NOC, OA)
P("gpt-5.4-2026-03-05", "openai", "2026-03-05", "", "2.50", "0.25", "", "15.00", OAR, OAB,
  "long-context variant billed at 2x standard; regional data residency +10% on models after 2026-03-05", OA)
P("gpt-5-5", "openai", "2026-04-23", "", "5.00", "0.50", "", "30.00", OAR, OAB,
  "long-context variant billed at 2x standard", OA)
P("gpt-5-6-luna", "openai", "2026-07-09", "2026-07-29", "1.00", "0.10", "1.25", "6.00", OAR, OAB,
  "long-context variant billed at 2x standard on input, cached input and cache writes; "
  "launch rate, cut 80% on 2026-07-30", OA26_07)
P("gpt-5-6-luna", "openai", "2026-07-30", "", "0.20", "0.02", "0.25", "1.20", OAR, OAB,
  "long-context variant billed at 2x standard on input, cached input and cache writes; "
  "permanent 80% cut, not a promotion", OA)
P("gpt-5-6-sol", "openai", "2026-07-09", "2026-08-20", "5.00", "0.50", "6.25", "30.00", OAR, OAB,
  "long-context variant billed at 2x standard on input, cached input and cache writes; "
  "fast mode 2x (10.00/60.00); launch rate, in force until the 2026-08-21 promotional cut", OA26_08)
P("gpt-5-6-sol", "openai", "2026-08-21", "", "4.00", "0.40", "5.00", "20.00", OAR, OAB,
  "long-context variant billed at 2x standard on input, cached input and cache writes; "
  "fast mode 2x (8.00/40.00); promotional rate, 'available at least through November 21, 2026' "
  "- reverts to 5.00/0.50/6.25/30.00 if withdrawn", OA)
P("gpt-5-6-terra", "openai", "2026-07-09", "2026-07-29", "2.50", "0.25", "3.125", "15.00", OAR, OAB,
  "long-context variant billed at 2x standard on input, cached input and cache writes; "
  "launch rate, cut 20% on 2026-07-30", OA26_07)
P("gpt-5-6-terra", "openai", "2026-07-30", "", "2.00", "0.20", "2.50", "12.00", OAR, OAB,
  "long-context variant billed at 2x standard on input, cached input and cache writes; "
  "permanent 20% cut, not a promotion", OA)
P("gpt-6-astra", "openai", "2026-09-03", "", "10.00", "1.00", "12.50", "50.00", OAR, OAB,
  "long context input 20.00 / output 75.00 above the short-context window", OA)
NOPRICE(["gpt-4-base-2023-report", "gpt-4-2023-03-01-internal", "gpt-4-bar-exam-preview"], "not_api_served",
        "pre-release GPT-4 snapshot, never sold on the API; the public gpt-4 rate is not this model's list price")
NOPRICE("openai-ns-2026-09-internal", "not_api_served", "internal research model, never offered for sale")
NOPRICE(["codex-300m-research", "codex-2-5b-research", "codex-12b-research"], "not_api_served",
        "2021 Codex research models, never separately priced")
NOPRICE("github-copilot-2022-08", "not_api_served", "seat subscription, not token-metered")
NOPRICE("chatgpt-gpt35-2022", "not_api_served", "ChatGPT web preview, free and not token-metered")
NOPRICE("dactyl-adr-xxl-vision", "not_api_served", "robotics research system, never API-served")
P(["whisper_tiny_en", "whisper_large_v2"], "openai", "2023-03-01", "", "", "", "", "",
  "not_applicable", NOC,
  "Whisper API is billed per audio minute (0.006 USD per minute, rounded to the nearest second), not per token, so no per-token rate exists. The weights are open and both checkpoints are commonly self-hosted", OA23_06)
NOPRICE(["implicit-cot-gpt2-mult11", "implicit-cot-gpt2-mult4", "implicit-cot-gpt2-mult5",
         "implicit-cot-gpt2-mult7", "implicit-cot-gpt2-mult9", "implicit-cot-gpt2-gsm8k-medium",
         "implicit-cot-gpt2-gsm8k-small"], "self_hosted",
        "GPT-2 research fine-tunes, open weights, no hosted endpoint")
# gpt-oss: open weights, served by third parties
P("gpt-oss-120b", "together", "2025-08-05", "", "0.15", "", "", "0.60", OAR, NOC,
  "open weights; Together serverless rate. No row source in either registry names a specific host", TG)
P("gpt-oss-20b", "together", "2025-08-05", "", "0.05", "", "", "0.20", OAR, NOC,
  "open weights; Together serverless small-model rate", TG)

# ======================================================== ANTHROPIC ==========
# Prompt caching GA 2024-08-14 (3.5 Sonnet, 3 Haiku) and 2024-11-04 (3 Opus, 3.5 Haiku);
# Batch API (50%) from 2024-10-08. Cache write = 1.25x input (5m) unless noted.
ANB, ANR = "0.5", "output"
P(["claude-2.0", "claude-2.1"], "anthropic", "2023-07-11", "2025-07-21", "8.00", "", "", "24.00",
  "no_reasoning_tokens", NOC, "no prompt caching and no Batch API on Claude 2", AN24_04)
P("claude-3-opus-20240229", "anthropic", "2024-03-04", "", "15.00", "1.50", "18.75", "75.00",
  "no_reasoning_tokens", ANB, "caching available from 2024-11-04", AN24_04)
P("claude-3-sonnet-20240229", "anthropic", "2024-03-04", "", "3.00", "", "", "15.00",
  "no_reasoning_tokens", ANB, "prompt caching never offered on Claude 3 Sonnet", AN24_04)
P("claude-3-haiku-20240307", "anthropic", "2024-03-13", "", "0.25", "0.03", "0.30", "1.25",
  "no_reasoning_tokens", ANB, "caching available from 2024-08-14", AN24_04)
P(["claude-3-5-sonnet-20240620", "claude-3-5-sonnet-20241022"], "anthropic", "2024-06-20", "",
  "3.00", "0.30", "3.75", "15.00", "no_reasoning_tokens", ANB, "caching available from 2024-08-14", AN)
P("claude-3-5-haiku-20241022", "anthropic", "2024-11-04", "2024-11-19", "1.00", "0.10", "1.25", "5.00",
  "no_reasoning_tokens", ANB, "launch price", AN)
P("claude-3-5-haiku-20241022", "anthropic", "2024-11-20", "", "0.80", "0.08", "1.00", "4.00",
  "no_reasoning_tokens", ANB, "20% cut; 1h cache write 1.60", AN)
P("claude-3-7-sonnet", "anthropic", "2025-02-24", "", "3.00", "0.30", "3.75", "15.00", ANR, ANB,
  "first Claude with extended thinking; thinking tokens are inside output_tokens", AN)
P("claude-opus-4", "anthropic", "2025-05-22", "", "15.00", "1.50", "18.75", "75.00",
  ANR, ANB, "1h cache write 30.00", AN)
P("claude-opus-4-1", "anthropic", "2025-08-05", "", "15.00", "1.50", "18.75", "75.00",
  ANR, ANB, "1h cache write 30.00; window starts at the Opus 4.1 release date", AN)
P("claude-sonnet-4", "anthropic", "2025-05-22", "", "3.00", "0.30", "3.75", "15.00", ANR, ANB,
  "1M-context beta: 6.00 input / 22.50 output above 200k prompt tokens", AN)
P("claude-sonnet-4-5", "anthropic", "2025-09-29", "", "3.00", "0.30", "3.75", "15.00", ANR, ANB,
  "1M-context beta: 6.00 input / 22.50 output above 200k prompt tokens", AN)
P("claude-haiku-4-5", "anthropic", "2025-10-15", "", "1.00", "0.10", "1.25", "5.00", ANR, ANB,
  "1h cache write 2.00", AN)
P("claude-opus-4-5", "anthropic", "2025-11-24", "", "5.00", "0.50", "6.25", "25.00", ANR, ANB,
  "1h cache write 10.00", AN)
P("claude-opus-4-6", "anthropic", "2026-02-05", "", "5.00", "0.50", "6.25", "25.00", ANR, ANB,
  "full 1M window at standard rates from Claude 4.6; inference_geo=us multiplies all rates by 1.1", AN)
P("claude-sonnet-4-6", "anthropic", "2026-02-17", "", "3.00", "0.30", "3.75", "15.00", ANR, ANB,
  "full 1M window at standard rates", AN)
P("claude-opus-4-7", "anthropic", "2026-04-16", "", "5.00", "0.50", "6.25", "25.00", ANR, ANB,
  "full 1M window at standard rates; new tokenizer produces about 30% more tokens for the same text", AN)
P("claude-opus-4-8", "anthropic", "2026-05-28", "", "5.00", "0.50", "6.25", "25.00", ANR, ANB,
  "full 1M window at standard rates; fast mode 2x (10.00/50.00); newer tokenizer", AN)
P(["claude-opus-5", "claude-opus-5-max"], "anthropic", "2026-07-24", "", "5.00", "0.50", "6.25", "25.00",
  ANR, ANB, "full 1M window at standard rates; fast mode 2x (10.00/50.00); newer tokenizer", AN)
NOPRICE("anthropic-internal-research-flt-2026-08", "not_api_served",
        "internal research model, never offered for sale; described as roughly comparable to Claude Fable 5.1 (10.00/0.25/50.00 on the public sheet)")

# =========================================================== GOOGLE ==========
GGB, GGR = "0.5", "output"
P("gemini-1.0-pro-001", "google", "2024-02-15", "", "0.50", "", "", "1.50", "no_reasoning_tokens", NOC,
  "no context caching on Gemini 1.0", GG24_07)
P(["gemini-1.5-pro-001", "gemini-1.5-pro-hourvideo", "gemini-1.5-pro-naturalplan"], "google",
  "2024-05-23", "2024-09-30", "3.50", "0.875", "", "10.50", "no_reasoning_tokens", NOC,
  ">128k prompt: input 7.00, output 21.00, cache 1.75", GG24_07)
P(["gemini-1.5-pro-001", "gemini-1.5-pro-002", "gemini-1.5-pro-hourvideo", "gemini-1.5-pro-naturalplan"],
  "google", "2024-10-01", "", "1.25", "0.3125", "", "5.00", "no_reasoning_tokens", GGB,
  ">128k prompt: input 2.50, output 10.00, cache 0.625", GG24_12)
P("gemini-1.5-flash-001", "google", "2024-05-23", "2024-09-30", "0.35", "0.0875", "", "1.05",
  "no_reasoning_tokens", NOC, ">128k prompt: input 0.70, output 2.10, cache 0.175", GG24_07)
P(["gemini-1.5-flash-001", "gemini-1.5-flash-002"], "google", "2024-10-01", "", "0.075", "0.01875", "",
  "0.30", "no_reasoning_tokens", GGB, ">128k prompt: input 0.15, output 0.60, cache 0.0375", GG24_12)
P("gemini-1.5-flash-8b-001", "google", "2024-10-03", "", "0.0375", "0.01", "", "0.15",
  "no_reasoning_tokens", GGB, ">128k prompt: input 0.075, output 0.30, cache 0.02", GG24_12)
P("gemini-2.0-flash-001", "google", "2025-02-05", "", "0.10", "0.025", "", "0.40", "no_reasoning_tokens",
  GGB, "audio input 0.70; no prompt-size tier", GG25_12)
NOPRICE("gemini-2.0-pro-exp-02-05", "not_api_served",
        "experimental endpoint, free preview only, never carried a paid rate")
P("gemini-2.5-pro-03-25", "google", "2025-03-25", "2025-04-03", "0.00", "0.00", "", "0.00", GGR, NOC,
  "exp-03-25 and preview-03-25 were free experimental endpoints; paid preview pricing began 2025-04-04", GG25_06)
P(["gemini-2.5-pro-03-25", "gemini-2.5-pro-preview-06-05", "gemini-2.5-pro"], "google", "2025-04-04", "",
  "1.25", "0.125", "", "10.00", GGR, GGB, ">200k prompt: input 2.50, output 15.00, cache 0.25", GG25_12)
P("gemini-2.5-flash-preview-05-20", "google", "2025-05-20", "2025-06-16", "0.15", "0.0375", "", "0.60",
  "separate_thinking_rate", GGB,
  "thinking output billed at 3.50 against 0.60 non-thinking; audio input 1.00", GG25_06)
P("gemini-2.5-flash", "google", "2025-06-17", "", "0.30", "0.03", "", "2.50", GGR, GGB,
  "audio input 1.00; single output rate covers thinking from GA; deprecation scheduled 2026-10-16", GG)
P("gemini-3-pro", "google", "2025-11-18", "", "2.00", "0.20", "", "12.00", GGR, GGB,
  ">200k prompt: input 4.00, output 18.00, cache 0.40", GG25_12)
P("gemini-3-flash-preview", "google", "2025-12-17", "", "0.50", "0.05", "", "3.00", GGR, GGB,
  "audio input 1.00", GG)
NOPRICE("gemini-3-deep-think-preview", "not_api_served",
        "Deep Think preview was gated to Ultra subscribers for the November 2025 evaluation; no per-token API rate published")
P(["gemini-3.1-pro-preview", "gemini-3.1-pro-preview-customtools"], "google", "2026-02-19", "",
  "2.00", "0.20", "", "12.00", GGR, GGB,
  ">200k prompt: input 4.00, output 18.00, cache 0.40; priority tier 3.60/21.60", GG)
P("gemini-3.1-flash-lite-preview", "google", "2026-03-03", "", "0.25", "0.025", "", "1.50", GGR, GGB,
  "audio input 0.50", GG)
P("gemini-3.5-flash", "google", "2026-05-19", "", "1.50", "0.15", "", "9.00", GGR, GGB, NOC, GG)
# Gemma: open weights
P(["gemma-2-9b-it", "gemma-2-27b-it", "gemma-3-27b-it"], "self_hosted", "", "", "", "", "", "",
  "no_reasoning_tokens", "",
  "open weights; free of charge on the Gemini API free tier and not sold per token there. Third-party serverless rates existed (Together size buckets, OpenRouter) but no registry row names a host", "")
NOPRICE(["dqn_2015_pong", "dqn_2015_breakout", "dqn-nature-2015-frostbite", "muzero-atari-standard",
         "alphazero-chess-2017", "alphago-zero-20block-3day", "alphago-zero-40block-40day",
         "alphastar-final-2019", "gnome-structural-ensemble", "rt2-pali-x-55b", "lipnet-grid-unseen",
         "searchless-chess-270m", "table-tennis-dambrosio2024", "facenet-nn1",
         "gulshan-dr-inception-v3-ensemble", "mckinney-mammography-ensemble-2020",
         "circuit-training-ariane-2022", "minerva-62b", "palm-540b-original",
         "tesseract-eng-best-2017-09-14", "bert-base-uncased", "bert-large-uncased",
         "efficientnet_b7_original", "mobilenet_v3_large_original", "pegasus-xsum-hf"],
        "not_api_served", "research or in-product model, never sold through a per-token API")

# ============================================================== XAI ==========
P("grok-2-1212", "xai", "2024-12-12", "", "2.00", "", "", "10.00", "no_reasoning_tokens", NOC,
  "no cached-input rate published at launch", XAI2)
P("grok-3-beta", "xai", "2025-04-09", "", "3.00", "", "", "15.00", "no_reasoning_tokens", NOC, NOC, SEC)
P("grok-3-mini-beta", "xai", "2025-04-09", "", "0.30", "", "", "0.50", "output", NOC, NOC, SEC)
P("grok-4", "xai", "2025-07-09", "", "3.00", "", "", "15.00", "output", NOC,
  "256k context; xAI published no separate cached rate for Grok 4", SEC)
P("grok-4.20-beta-0309b-reasoning", "xai", "2026-03-10", "", "1.25", "0.20", "", "2.50", "output", "0.2",
  ">=200k prompt: input 2.50, cached 0.40, output 5.00. Batch is 20% off, not 50%", XAI)

# ========================================================= DEEPSEEK ==========
DSC = "cache-hit input is a separate lower rate; DeepSeek charges nothing for the cache write"
P("deepseek-llm-67b-chat", "together", "2023-11-29", "", "0.90", "", "", "0.90", "no_reasoning_tokens",
  NOC, "open weights; Together serverless flat rate", TG25_02)
P("deepseek-v3", "deepseek", "2024-12-26", "2025-02-08", "0.14", "0.014", "", "0.28",
  "no_reasoning_tokens", NOC,
  "launch discount through 2025-02-08 16:00 UTC; standard rate behind it was 0.27/0.07/1.10", DS25_01)
P(["deepseek-v3", "deepseek-v3-0324"], "deepseek", "2025-02-09", "2025-08-20", "0.27", "0.07", "", "1.10",
  "no_reasoning_tokens", NOC,
  "deepseek-chat endpoint; from 2025-02-26 a 50%-off off-peak window applied 16:30-00:30 UTC", DS25_03)
P(["deepseek-r1", "deepseek-r1-0528"], "deepseek", "2025-01-20", "2025-08-20", "0.55", "0.14", "", "2.19",
  "output", NOC,
  "deepseek-reasoner endpoint; CoT tokens are inside output and priced equally. From 2025-02-26 a 75%-off off-peak window applied 16:30-00:30 UTC", DS25_03)
P(["deepseek-v3", "deepseek-v3-0324", "deepseek-r1", "deepseek-r1-0528"], "deepseek", "2025-08-21",
  "2025-09-28", "0.56", "0.07", "", "1.68", "output", NOC,
  "V3.1 sheet; both endpoints repriced to one rate and the off-peak discount was withdrawn", DS25_09)
P("deepseek-v3.2", "deepseek", "2025-09-29", "", "0.28", "0.028", "", "0.42", "output", NOC,
  "V3.2-Exp from 2025-09-29 and V3.2 from 2025-12-01 at the same rate; 128k context", DS25_10)
P("deepseek-v4-pro-preview", "deepseek", "2026-04-24", "", "1.32", "0.044", "", "3.96", "output", NOC,
  "peak rate shown; off-peak is half (0.66 / 0.022 / 1.98). Peak is 01:00-04:00 and 06:00-10:00 UTC Mon-Fri", DS)
# DeepSeek open weights on third-party hosts, where a registry row's source used one
P("deepseek-r1", "together", "2025-01-20", "2025-03-25", "7.00", "", "", "7.00", "output", NOC,
  "Together flat rate; the provider used by Cost-of-Pass and by the HAL GAIA DeepSeek runs", TG25_02)
P("deepseek-r1", "together", "2025-03-26", "", "3.00", "", "", "7.00", "output", NOC,
  "Together split the R1 rate; in force by 2025-03-26 on the Cost-of-Pass run records "
  "(see list-prices.md), earlier than the 2025-06 capture; matches the 3/7 pair recovered "
  "from the Kaggle Game Arena cost column", TG25_06)
P("deepseek-r1-0528", "together", "2025-06-01", "", "3.00", "", "", "7.00", "output",
  NOC, "Together split the R1 rate; matches the 3/7 pair recovered from the Kaggle Game Arena cost column", TG25_06)
P(["deepseek-v3", "deepseek-v3-0324"], "together", "2024-12-26", "", "1.25", "", "", "1.25",
  "no_reasoning_tokens", NOC, "Together flat rate", TG25_02)
P("deepseek-r1-distill-llama-70b", "together", "2025-01-20", "", "2.00", "", "", "2.00", "output", NOC,
  "Together flat rate; open weights", TG25_02)
NOPRICE("deepseek-r1-distill-qwen-32b", "self_hosted",
        "the BALROG submission ran it on a self-hosted vLLM endpoint; Together did not list a 32B R1 distill")
P("deepseek-prover-v2-671b", "self_hosted", "", "", "", "", "", "", "output", "",
  "open weights, no first-party API endpoint; DeepSeek never listed deepseek-prover on its price sheet", "")

# ========================================================== ALIBABA ==========
ALB = "0.5"
P("qwen-turbo-2024-11-01", "alibaba", "2024-11-15", "", "0.05", "0.005", "0.0625", "0.20",
  "separate_thinking_rate", ALB,
  "thinking-mode output 0.50 against 0.20 non-thinking; cache create 1.25x input, cache hit 0.1x", ALI25_04)
P("qwen-plus-2025-01-25", "alibaba", "2025-01-30", "", "0.40", "0.04", "0.50", "1.20",
  "separate_thinking_rate", ALB,
  "thinking-mode output 4.00 against 1.20 non-thinking; 0-256K prompt tier", ALI25_04)
P("qwen-max-2025-01-25", "alibaba", "2025-01-28", "", "1.60", "0.16", "2.00", "6.40", "output", ALB,
  "cache create 1.25x input, cache hit 0.1x", ALI25_04)
P("qwq-plus", "alibaba", "2025-03-06", "", "0.80", "", "", "2.40", "output", NOC,
  "no batch or cache rate published for qwq-plus", ALI25_04)
P("qwen3.6-plus", "alibaba", "2026-04-02", "", "0.50", "0.05", "0.625", "3.00", "output", NOC,
  "0-256K prompt tier; no batch rate listed for the Plus line", ALI)
P("qwen3.7-max", "alibaba", "2026-05-21", "", "2.50", "0.25", "3.125", "7.50", "output", ALB,
  "cache create 1.25x input, cache hit 0.1x", ALI)
# Qwen open-weight checkpoints, served by third parties
P("qwen2-72b-instruct", "together", "2024-06-06", "", "0.90", "", "", "0.90", "no_reasoning_tokens",
  NOC, "open weights; Together serverless flat rate", TG25_02)
P("qwen2.5-72b-instruct", "together", "2024-09-19", "", "1.20", "", "", "1.20", "no_reasoning_tokens",
  NOC, "open weights; Together serverless flat rate", TG25_02)
P("qwen2.5-32b-instruct", "together", "2024-09-19", "", "0.80", "", "", "0.80", "no_reasoning_tokens",
  NOC, "open weights; Together 21.1B-41B size bucket", TG25_02)
NOPRICE("qwen2.5-7b-instruct", "self_hosted",
        "the BALROG submission ran it on a self-hosted vLLM endpoint. Together's listed rate for Qwen2.5 7B was 0.30 flat")
P("qwq-32b", "together", "2025-03-06", "", "1.20", "", "", "1.20", "output", NOC,
  "open weights; Together's QwQ 32B serverless rate", TG25_02)
P(["qwen3-235b-a22b-thinking-2507", "qwen3-235b-a22b-instruct-2507"], "fireworks", "2025-07-21", "",
  "1.20", "", "", "1.20", "output", NOC,
  "open weights; Fireworks MoE 56.1B-176B bucket is 1.20 flat. No registry row names a host", FW)
NOPRICE(["qwen1.5-32b-chat", "qwen1.5-72b-chat", "qwen2.5-math-1.5b-instruct"], "self_hosted",
        "open weights, no hosted endpoint named by any registry row")

# =========================================================== MISTRAL =========
MIB = "0.5"
P("mistral-large-2402", "mistral", "2024-02-26", "2024-07-23", "8.00", "", "", "24.00",
  "no_reasoning_tokens", NOC, "launch price on La Plateforme", SEC)
P(["mistral-large-2407", "mistral-large-2411"], "mistral", "2024-07-24", "", "2.00", "", "", "6.00",
  "no_reasoning_tokens", MIB, "2411 replaced 2407 in place at the same rate", MI24_11)
P(["mistral-small-2501", "mistral-small-2503"], "mistral", "2025-01-30", "", "0.10", "", "", "0.30",
  "no_reasoning_tokens", MIB, "Mistral Small 3 rate, carried unchanged by 3.1 (2503)", SEC)
P("ministral-3b-2410", "mistral", "2024-10-16", "", "0.04", "", "", "0.04", "no_reasoning_tokens", MIB,
  NOC, MI24_11)
P("ministral-8b-2410", "mistral", "2024-10-16", "", "0.10", "", "", "0.10", "no_reasoning_tokens", MIB,
  NOC, MI24_11)
P("mistral-nemo-2407", "mistral", "2024-07-18", "", "0.15", "", "", "0.15", "no_reasoning_tokens", MIB,
  "open weights (Apache 2.0), also served first-party as open-mistral-nemo", MI24_11)
P(["open-mistral-7b", "mistral-7b-instruct-v0.3"], "mistral", "2023-09-27", "", "0.25", "", "", "0.25",
  "no_reasoning_tokens", MIB, "open weights, also served first-party as open-mistral-7b", MI24_11)
P("mixtral-8x7b-instruct-v0.1", "mistral", "2023-12-11", "", "0.70", "", "", "0.70",
  "no_reasoning_tokens", MIB, "open weights, also served first-party as open-mixtral-8x7b", MI24_11)
P("mixtral-8x22b-instruct-v0.1", "mistral", "2024-04-17", "", "2.00", "", "", "6.00",
  "no_reasoning_tokens", MIB, "open weights, also served first-party as open-mixtral-8x22b", MI24_11)

# =========================================================== MOONSHOT ========
P("kimi-k2-instruct", "moonshot", "2025-07-11", "", "0.60", "0.15", "", "2.50", "no_reasoning_tokens",
  NOC, "cache-hit input is a separate lower rate; no cache-write fee", SEC)
P("kimi-k2.5", "moonshot", "2026-01-27", "2026-08-31", "0.60", "0.10", "", "3.00", "output", NOC,
  "retired from the Moonshot API 2026-08-31. Epoch's runs used the Fireworks endpoint instead", SEC)
P("kimi-k2.6", "moonshot", "2026-04-20", "", "0.95", "0.16", "", "4.00", "output", NOC,
  "cache-hit input is a separate lower rate; no cache-write fee", MOON)
P("kimi-k3", "moonshot", "2026-07-16", "", "3.00", "0.30", "", "15.00", "output", NOC,
  "1,048,576-token context at one rate", MOON)

# =============================================================== Z.AI ========
P("glm-4.7", "zai", "2025-12-22", "", "0.60", "0.11", "", "2.20", "output", NOC,
  "cached-input storage is free; no batch rate published", ZAI)
P("glm-5", "zai", "2026-02-11", "", "1.00", "0.20", "", "3.20", "output", NOC,
  "cached-input storage is free; no batch rate published", ZAI)
P("glm-5.2", "zai", "2026-06-16", "", "1.40", "0.26", "", "4.40", "output", NOC,
  "cached-input storage is free; no batch rate published", ZAI)

# ============================================================= META ==========
TGF = "open weights; Together serverless flat rate (input = output)"
P("llama-2-70b-chat", "together", "2023-07-18", "", "0.90", "", "", "0.90", "no_reasoning_tokens", NOC,
  TGF + "; 41.1B-80B size bucket", TG25_02)
P("llama-2-70b", "together", "2023-07-18", "", "0.90", "", "", "0.90", "no_reasoning_tokens", NOC,
  TGF + "; 41.1B-80B size bucket", TG25_02)
P("llama-2-13b", "together", "2023-07-18", "", "0.30", "", "", "0.30", "no_reasoning_tokens", NOC,
  TGF + "; 8.1B-21B size bucket", TG25_02)
P("llama-3-8b-instruct", "together", "2024-04-18", "", "0.18", "", "", "0.18", "no_reasoning_tokens",
  NOC, TGF + "; 8B Turbo tier (Lite 0.10, Reference 0.20)", TG25_02)
P("llama-3-70b-instruct", "together", "2024-04-18", "", "0.88", "", "", "0.88", "no_reasoning_tokens",
  NOC, TGF + "; 70B Turbo tier (Lite 0.54, Reference 0.90)", TG25_02)
P(["llama-3.1-8b-instruct"], "together", "2024-07-23", "", "0.18", "", "", "0.18",
  "no_reasoning_tokens", NOC,
  TGF + "; 8B Turbo tier. This is the rate Cost-of-Pass Table 4 used", TG25_02)
P("llama-3.1-70b-instruct", "together", "2024-07-23", "", "0.88", "", "", "0.88", "no_reasoning_tokens",
  NOC, TGF + "; 70B Turbo tier", TG25_02)
P(["llama-3.1-405b-instruct", "llama-3.1-405b-base"], "together", "2024-07-23", "", "3.50", "", "",
  "3.50", "no_reasoning_tokens", NOC,
  TGF + "; 405B Turbo tier. This is the rate Cost-of-Pass Table 4 used", TG25_02)
P("llama-3.3-70b-instruct", "together", "2024-12-06", "", "0.88", "", "", "0.88", "no_reasoning_tokens",
  NOC, TGF + "; 70B Turbo tier. This is the rate Cost-of-Pass Table 4 used", TG25_02)
P("llama-3.2-90b-vision-instruct", "together", "2024-09-25", "", "1.20", "", "", "1.20",
  "no_reasoning_tokens", NOC, TGF + "; 90B Vision Turbo tier", TG25_02)
NOPRICE(["llama-3.2-1b-instruct", "llama-3.2-3b-instruct"], "self_hosted",
        "the BALROG submissions ran these on self-hosted vLLM endpoints. Together's up-to-3B Turbo rate was 0.06 flat")
P("llama-4-maverick", "together", "2025-04-05", "", "0.27", "", "", "0.85", "no_reasoning_tokens", NOC,
  "open weights; Together serverless. This is the rate the VideoGameBench harness billed at", TG25_06)
P("llama-4-scout", "together", "2025-04-05", "", "0.18", "", "", "0.59", "no_reasoning_tokens", NOC,
  "open weights; Together serverless", TG25_06)
NOPRICE(["latxa-70b-v1.1", "latxa-13b-v1.1", "swallow-7b-base", "swallow-70b-base", "llammas-base-7b",
         "acegpt-7b-base", "acegpt-13b-base", "roberta-base", "code-llama-7b-base",
         "code-llama-34b-base", "code-llama-7b-kexer", "nllb-200-3.3b", "openvla-7b"],
        "self_hosted", "open-weight research checkpoint, no hosted per-token endpoint")

# ==================================================== OTHER OPEN WEIGHTS =====
NOPRICE("phi-4", "self_hosted",
        "the BALROG submission ran microsoft/phi-4 on a self-hosted vLLM endpoint. Together's 8.1B-21B size bucket, which a 14B model falls in, was 0.30 flat")
NOPRICE("phi-3-medium-128k-instruct", "self_hosted",
        "open weights; no registry row names a host")
P("dbrx-instruct", "together", "2024-03-27", "", "1.20", "", "", "1.20", "no_reasoning_tokens", NOC,
  "open weights; Together MoE 56.1B-176B bucket (132B total)", TG25_02)
P(["yi-1.5-34b-chat", "yi-34b-chat"], "together", "2023-11-23", "", "0.80", "", "", "0.80",
  "no_reasoning_tokens", NOC, "open weights; Together 21.1B-41B bucket", TG25_02)
P("llama-3.1-tulu-3-70b-dpo", "together", "2024-11-21", "", "0.90", "", "", "0.90",
  "no_reasoning_tokens", NOC, "open weights; Together 41.1B-80B bucket", TG25_02)
P("hermes-2-theta-llama-3-70b", "together", "2024-06-20", "", "0.90", "", "", "0.90",
  "no_reasoning_tokens", NOC, "open weights; Together 41.1B-80B bucket", TG25_02)
P("wizardlm-2-8x22b", "together", "2024-04-15", "", "1.20", "", "", "1.20", "no_reasoning_tokens", NOC,
  "open weights; Together MoE 56.1B-176B bucket (141B total)", TG25_02)
NOPRICE(["reka-flash-3", "eurus-2-7b-prime", "retrodfmr-8b-2025"], "self_hosted",
        "open weights; BALROG and the source papers ran self-hosted endpoints")

# ================================================== NOT API-SERVED (rest) ====
NOT_SERVED = [
 "act_aloha_2023","resnet50_original","resnet152_original","cassie-100m-2022",
 "mobile-aloha-act-cotrain","swift-racing-system","dexnet-2-gq-cnn","modelangelo-2024",
 "anymal-perceptive-2022","helix-s1-logistics-60h","pr2-geometric-towel-2010",
 "efficientzero-atari-2021","pi0-base-700k-2024","ora-resnet-mnist","chexnet-pneumonia-2017-v1",
 "maia-1500-v1","gt-fuchs2020-setting-a","gt-sophy-october2021","gt-sophy-july2021-time-trial",
 "amazon-sparrow-architecture-proxy","gector-peet-2025-unspecified","elc-bert-base-babylm-2023",
 "gpt-bert-base-babylm-2024","gpt-bert-small-babylm-2024","gulordava-english-lstm-650",
 "lenet-5-original","birdnet-v2.4","ecapa-tdnn-original-c1024","mbart-large-50-one-to-many-mmt",
 "arcface-ms1mv2-r100","esteva-skin-inception-v3","yolov8n-coco","yolov8s-coco","yolov8m-coco",
 "yolov8l-coco","yolov8x-coco","multipl-t-starcoder-1b-ocaml","multipl-t-starcoder-15b-ocaml",
 "multipl-t-starcoder-15b-racket","pigeon-cvpr2024","vits-ljspeech-2021","r2bert-base-2020",
 "openai-five-finals-2019","fair-negotiator-2017-likelihood","fair-negotiator-2017-rl",
 "berkeley-crossword-bert-2022","binary64-affine-converter","alphacode-41b","alphacode-9b",
 "babyberta-aochildes","vima-200m","stockfish-13-nnue-62ef826d1a6d","microsoft-combo6-2018",
 "nvidia-dave2-2016","monorace-racing-system","srt-h-2025","gemini-3.1-flash-lite-preview-DUP",
]
NOPRICE([m for m in NOT_SERVED if not m.endswith("-DUP")], "not_api_served",
        "task-specific or research model, never sold through a per-token API")

# =============================================================== emit ========
def main(dataset_models, claude_models, out_path):
    ids, order = set(), []
    for path in (dataset_models, claude_models):
        with open(path, newline="") as f:
            for r in csv.DictReader(f):
                if r["model_id"] not in ids:
                    ids.add(r["model_id"]); order.append(r["model_id"])
    covered = {r["model_id"] for r in rows}
    missing = [m for m in order if m not in covered]
    extra = sorted(covered - ids)
    if extra:
        raise SystemExit("rows for unknown model_ids: %s" % extra)
    for m in missing:
        rows.append(dict(model_id=m, provider="not_api_served", price_sheet_start="",
                         price_sheet_end="", input_usd_per_m="", cached_input_usd_per_m="",
                         cache_write_usd_per_m="", output_usd_per_m="",
                         reasoning_billed_as="not_applicable", batch_discount="",
                         long_context_rule="no published per-token list price found",
                         source_url="not_applicable", retrieved=RETRIEVED))
    pos = {m: i for i, m in enumerate(order)}
    rows.sort(key=lambda r: (pos[r["model_id"]], r["price_sheet_start"], r["provider"]))
    cols = ["model_id","provider","price_sheet_start","price_sheet_end","input_usd_per_m",
            "cached_input_usd_per_m","cache_write_usd_per_m","output_usd_per_m",
            "reasoning_billed_as","batch_discount","long_context_rule","source_url","retrieved"]
    with open(out_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print("models in registries: %d" % len(order))
    print("rows written: %d" % len(rows))
    print("models with at least one price: %d" % len({
        r["model_id"] for r in rows if r["input_usd_per_m"]}))
    print("models with no price: %d" % len(
        {r["model_id"] for r in rows} - {r["model_id"] for r in rows if r["input_usd_per_m"]}))
    if missing:
        print("fell through to the default no-price row: %s" % ", ".join(missing))

if __name__ == "__main__":
    main(*sys.argv[1:4])
