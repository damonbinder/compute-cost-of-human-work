"""Builds ../pricing-crosscheck.csv. Reads the two registries and the three proposal CSVs
read-only; writes only the one output file."""
import csv, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))          # claude-rows
DSET = os.path.normpath(os.path.join(ROOT, "..", "AI Compute vs Human Time", "dataset"))
MP = os.path.join(ROOT, "research", "model-priors")
OUT = os.path.join(MP, "pricing-crosscheck.csv")

import importlib.util
spec = importlib.util.spec_from_file_location("cm", os.path.join(HERE, "cost_model.py"))
cm = importlib.util.module_from_spec(spec); spec.loader.exec_module(cm)

# ---- price identities.  (input, cached_input, output, status, source)
A = "anthropic-pricing-2026-09-13"      # platform.claude.com/docs/en/about-claude/pricing
O = "openai-pricing-2026-09-13"         # developers.openai.com/api/docs/pricing
OL = "openai-ladder-extract"            # agent-work/sources/model-priors/openai/serving-economics-ladder.md
G = "google-pricing-2026-09-13"         # ai.google.dev/gemini-api/docs/pricing
GX = "google-xai-extract"               # agent-work/sources/model-priors/google-xai-others/pricing-and-throughput.md
X = "xai-docs-2026-09-13"               # docs.x.ai/docs/models
AR = "anthropic-report-extract"         # ../anthropic.md historical prices
NA = None

PRICE = {
 # --- Anthropic, current
 "claude-opus-5":            ("Claude Opus 5",        5.0, 0.50, 25.0, "current", A),
 "claude-opus-5-max":        ("Claude Opus 5",        5.0, 0.50, 25.0, "current", A),
 "claude-opus-4-8":          ("Claude Opus 4.8",      5.0, 0.50, 25.0, "current", A),
 "claude-opus-4-7":          ("Claude Opus 4.7",      5.0, 0.50, 25.0, "current", A),
 "claude-opus-4-6":          ("Claude Opus 4.6",      5.0, 0.50, 25.0, "current", A),
 "claude-opus-4-5":          ("Claude Opus 4.5",      5.0, 0.50, 25.0, "current", A),
 "claude-sonnet-4-6":        ("Claude Sonnet 4.6",    3.0, 0.30, 15.0, "current", A),
 "claude-sonnet-4-5":        ("Claude Sonnet 4.5",    3.0, 0.30, 15.0, "current", A),
 "claude-haiku-4-5":         ("Claude Haiku 4.5",     1.0, 0.10,  5.0, "current", A),
 # --- Anthropic, retired but still listed
 "claude-opus-4-1":          ("Claude Opus 4.1",     15.0, 1.50, 75.0, "retired_listed", A),
 "claude-opus-4":            ("Claude Opus 4",       15.0, 1.50, 75.0, "retired_listed", A),
 "claude-sonnet-4":          ("Claude Sonnet 4",      3.0, 0.30, 15.0, "retired_listed", A),
 "claude-3-5-haiku-20241022":("Claude Haiku 3.5",     0.80,0.08,  4.0, "retired_listed", A),
 # --- Anthropic, delisted; launch prices from the Anthropic report's extracts
 "claude-3-opus-20240229":   ("Claude 3 Opus",       15.0, NA,  75.0, "delisted_launch_price", AR),
 "claude-3-sonnet-20240229": ("Claude 3 Sonnet",      3.0, NA,  15.0, "delisted_launch_price", AR),
 "claude-3-haiku-20240307":  ("Claude 3 Haiku",       0.25,NA,   1.25,"delisted_launch_price", AR),
 "claude-3-5-sonnet-20240620":("Claude 3.5 Sonnet",   3.0, NA,  15.0, "delisted_launch_price", AR),
 "claude-3-5-sonnet-20241022":("Claude 3.5 Sonnet",   3.0, NA,  15.0, "delisted_launch_price", AR),
 "claude-3-7-sonnet":        ("Claude 3.7 Sonnet",    3.0, NA,  15.0, "delisted_launch_price", AR),
 "claude-2.0":               ("Claude 2",             NA,  NA,  NA,   "not_retrieved", NA),
 "claude-2.1":               ("Claude 2.1",           NA,  NA,  NA,   "not_retrieved", NA),
 "anthropic-internal-research-flt-2026-08": ("internal, never sold", NA, NA, NA, "never_public", NA),
 # --- reference rows, no registry row
 "REF-claude-fable-5-1":     ("Claude Fable 5.1",    10.0, 0.25, 50.0, "current", A),
 "REF-claude-fable-5":       ("Claude Fable 5",      10.0, 1.00, 50.0, "current", A),
 # --- OpenAI, current
 "gpt-6-astra":              ("GPT-6 Astra",         10.0, 1.00, 50.0, "current", O),
 "gpt-5-6-sol":              ("GPT-5.6 Sol",          4.0, 0.40, 20.0, "current", O),
 "gpt-5-6-luna":             ("GPT-5.6 Luna",         0.20,0.02,  1.20,"current", O),
 "gpt-5.4-2026-03-05":       ("GPT-5.4",              2.50,0.25, 15.0, "current", O),
 "gpt-5":                    ("GPT-5",                1.25,0.125,10.0, "current", O),
 "gpt-5-high":               ("GPT-5",                1.25,0.125,10.0, "current", O),
 "gpt-5-metr":               ("GPT-5",                1.25,0.125,10.0, "current", O),
 "gpt-5-chat":               ("GPT-5",                1.25,0.125,10.0, "current", O),
 "gpt-5-codex":              ("GPT-5",                1.25,0.125,10.0, "current", O),
 "gpt-5-mini-2025-08-07":    ("GPT-5 mini",           0.25,0.025, 2.0, "current", O),
 "gpt-5-nano":               ("GPT-5 nano",           0.05,0.005, 0.40,"current", O),
 "o3-2025-04-16":            ("o3 (repriced)",        2.0, 0.50,  8.0, "current", O),
 "o3-codeforces-checkpoint": ("o3 (repriced)",        2.0, 0.50,  8.0, "current", O),
 "gpt-4.1-2025-04-14":       ("GPT-4.1",              2.0, 0.50,  8.0, "current", O),
 # --- OpenAI, prices from the retained ladder extract
 "gpt-4-turbo-2024-04-09":   ("GPT-4 Turbo",         10.0, NA,   30.0, "delisted_launch_price", OL),
 "gpt-4-1106-preview":       ("GPT-4 Turbo",         10.0, NA,   30.0, "delisted_launch_price", OL),
 "gpt-4-0125-preview":       ("GPT-4 Turbo",         10.0, NA,   30.0, "delisted_launch_price", OL),
 "gpt-4-0314":               ("GPT-4",               30.0, NA,   60.0, "delisted_launch_price", OL),
 "gpt-4-0613":               ("GPT-4",               30.0, NA,   60.0, "delisted_launch_price", OL),
 "gpt-4-original-unspecified":("GPT-4",              30.0, NA,   60.0, "delisted_launch_price", OL),
 "gpt-4-base-2023-report":   ("GPT-4",               30.0, NA,   60.0, "delisted_launch_price", OL),
 "gpt-4-2023-03-01-internal":("GPT-4",               30.0, NA,   60.0, "delisted_launch_price", OL),
 "gpt-4-bar-exam-preview":   ("GPT-4",               30.0, NA,   60.0, "delisted_launch_price", OL),
 "gpt-4o-2024-08-06":        ("GPT-4o",               2.50,NA,   10.0, "delisted_launch_price", OL),
 "gpt-4o-2024-05-13":        ("GPT-4o",               2.50,NA,   10.0, "delisted_launch_price", OL),
 "gpt-4o-2024-11-20":        ("GPT-4o",               2.50,NA,   10.0, "delisted_launch_price", OL),
 "gpt-4o-metr":              ("GPT-4o",               2.50,NA,   10.0, "delisted_launch_price", OL),
 "gpt-4o-arc-alias":         ("GPT-4o",               2.50,NA,   10.0, "delisted_launch_price", OL),
 "gpt-4o-audio-preview-2024-10-01":("GPT-4o audio",   NA,  NA,   NA,   "not_retrieved", NA),
 "gpt-4o-mini-2024-07-18":   ("GPT-4o mini",          0.15,NA,    0.60,"delisted_launch_price", OL),
 "o1-2024-12-17":            ("o1",                  15.0, NA,   60.0, "delisted_launch_price", OL),
 "o1-preview-2024-09-12":    ("o1-preview",          15.0, NA,   60.0, "delisted_launch_price", OL),
 "o1-metr":                  ("o1",                  15.0, NA,   60.0, "delisted_launch_price", OL),
 "o1-mini-2024-09-12":       ("o-series mini",        1.10,NA,    4.40,"delisted_launch_price", OL),
 "o3-mini-2025-01-31":       ("o-series mini",        1.10,NA,    4.40,"delisted_launch_price", OL),
 "o4-mini-2025-04-16":       ("o-series mini",        1.10,NA,    4.40,"delisted_launch_price", OL),
 "gpt-4.5-preview-2025-02-27":("GPT-4.5 preview",    75.0, NA,  150.0, "withdrawn_2025-07-14", OL),
 "gpt-4.1-nano-2025-04-14":  ("GPT-4.1 nano",         0.10,NA,    0.40,"delisted_launch_price", OL),
 # --- OpenAI, price not retrieved
 "gpt-4.1-mini-2025-04-14":  ("GPT-4.1 mini",         NA, NA, NA, "not_retrieved", NA),
 "gpt-5.1-2025-11-13":       ("GPT-5.1",              NA, NA, NA, "not_retrieved", NA),
 "gpt-5.2-2025-12-11":       ("GPT-5.2",              NA, NA, NA, "not_retrieved", NA),
 "gpt-5-3-codex":            ("GPT-5.3-Codex",        NA, NA, NA, "not_retrieved", NA),
 "gpt-3.5-turbo-0125":       ("GPT-3.5 Turbo",        NA, NA, NA, "not_retrieved", NA),
 "gpt-3.5-turbo-1106":       ("GPT-3.5 Turbo",        NA, NA, NA, "not_retrieved", NA),
 "gpt-3.5-turbo-instruct":   ("GPT-3.5 Turbo Instruct", NA, NA, NA, "not_retrieved", NA),
 "text-davinci-002":         ("text-davinci-002",     NA, NA, NA, "not_retrieved", NA),
 "davinci-002-metr":         ("davinci-002",          2.00, NA, 2.00, "delisted_launch_price", OL),
 "chatgpt-gpt35-2022":       ("ChatGPT web, no API",  NA, NA, NA, "never_public", NA),
 "github-copilot-2022-08":   ("subscription, no API", NA, NA, NA, "never_public", NA),
 "openai-ns-2026-09-internal":("internal, never sold",NA, NA, NA, "never_public", NA),
 # --- Google, current
 "gemini-3.1-pro-preview":   ("Gemini 3.1 Pro",       2.00,0.20, 12.0, "current", G),
 "gemini-3.1-pro-preview-customtools":("Gemini 3.1 Pro", 2.00,0.20,12.0,"current", G),
 "gemini-3.5-flash":         ("Gemini 3.5 Flash",     1.50,0.15,  9.0, "current", G),
 "gemini-3.1-flash-lite-preview":("Gemini 3.1 Flash-Lite",0.25,0.025,1.50,"current", G),
 "gemini-2.5-pro":           ("Gemini 2.5 Pro",       1.25,0.125,10.0, "current", G),
 "gemini-2.5-pro-preview-06-05":("Gemini 2.5 Pro",    1.25,0.125,10.0, "current", G),
 "gemini-2.5-pro-03-25":     ("Gemini 2.5 Pro",       1.25,0.125,10.0, "current", G),
 "gemini-2.5-flash":         ("Gemini 2.5 Flash",     0.30,0.03,  2.50,"current", G),
 "gemini-2.5-flash-preview-05-20":("Gemini 2.5 Flash",0.30,0.03,  2.50,"current", G),
 # --- Google, delisted
 "gemini-3-pro":             ("Gemini 3 Pro",         NA, NA, NA, "not_retrieved", NA),
 "gemini-3-deep-think-preview":("Gemini 3 Deep Think",NA, NA, NA, "not_retrieved", NA),
 "gemini-3-flash-preview":   ("Gemini 3 Flash preview",0.50,NA,  3.00,"delisted_launch_price", GX),
 "gemini-2.0-flash-001":     ("Gemini 2.0 Flash",     NA, NA, NA, "not_retrieved", NA),
 "gemini-2.0-pro-exp-02-05": ("Gemini 2.0 Pro exp",   NA, NA, NA, "never_public", NA),
 "gemini-1.5-pro-001":       ("Gemini 1.5 Pro",       NA, NA, NA, "not_retrieved", NA),
 "gemini-1.5-pro-002":       ("Gemini 1.5 Pro",       NA, NA, NA, "not_retrieved", NA),
 "gemini-1.5-pro-naturalplan":("Gemini 1.5 Pro",      NA, NA, NA, "not_retrieved", NA),
 "gemini-1.5-flash-001":     ("Gemini 1.5 Flash",     0.075,NA, NA, "delisted_launch_price", GX),
 "gemini-1.5-flash-002":     ("Gemini 1.5 Flash",     0.075,NA, NA, "delisted_launch_price", GX),
 "gemini-1.5-flash-8b-001":  ("Gemini 1.5 Flash-8B",  0.0375,NA,NA, "delisted_launch_price", GX),
 "gemini-1.0-pro-001":       ("Gemini 1.0 Pro",       NA, NA, NA, "not_retrieved", NA),
 # --- xAI
 "grok-4":                   ("Grok 4",               3.00,NA,  15.0, "current", GX),
 "grok-4.20-beta-0309b-reasoning":("Grok 4.20",       1.25,0.20, 2.50,"current", X),
 "grok-3-beta":              ("Grok 3",               NA, NA, NA, "not_retrieved", NA),
 "grok-3-mini-beta":         ("Grok 3 mini",          0.30,NA,   0.50,"delisted_launch_price", GX),
 "grok-2-1212":              ("Grok 2",               NA, NA, NA, "not_retrieved", NA),
 # --- others
 "glm-5.2":                  ("GLM-5.2",              NA, NA, NA, "not_retrieved", NA),
 "qwen-max-2025-01-25":      ("qwen-max",             1.60,NA, NA, "delisted_launch_price", GX),
 "qwen-plus-2025-01-25":     ("qwen-plus",            0.40,NA, NA, "delisted_launch_price", GX),
 "qwen-turbo-2024-11-01":    ("qwen-turbo",           0.05,NA, NA, "delisted_launch_price", GX),
 "qwq-plus":                 ("qwq-plus",             NA, NA, NA, "not_retrieved", NA),
 "qwen3.6-plus":             ("qwen3.6-plus",         NA, NA, NA, "not_retrieved", NA),
 "qwen3.7-max":              ("qwen3.7-max",          NA, NA, NA, "not_retrieved", NA),
 "mistral-large-2402":       ("Mistral Large",        8.00,NA, 24.0, "delisted_launch_price", GX),
 "open-mistral-7b":          ("open-mistral-7b",      NA, NA, NA, "not_retrieved", NA),
}

# ---- measured throughput, Artificial Analysis, retrieved 2026-09-13. (tok/s, latency_s, config)
THRU = {
 "GPT-6 Astra":        (54, 332.50, "max effort; AA provider page"),
 "GPT-5.6 Sol":        (60, 140.60, "max effort"),
 "GPT-5.6 Luna":       (112, 139.52, "max effort"),
 "GPT-5.4":            (132, 105.82, "xhigh effort"),
 "GPT-5":              (76, 74.41, "high effort"),
 "GPT-5 mini":         (96, 84.08, "high effort"),
 "GPT-5 nano":         (143, 109.60, "high effort"),
 "o3 (repriced)":      (107, None, "median across providers; 152 on OpenAI's own API"),
 "GPT-4.1":            (130, None, "approximate, from the retained OpenAI ladder"),
 "GPT-4.1 nano":       (117, None, "retained OpenAI ladder"),
 "GPT-4o":             (124, None, "retained OpenAI ladder; 124-145 range"),
 "GPT-4o mini":        (150, None, "retained OpenAI ladder"),
 "GPT-4 Turbo":        (32, None, "OpenAI endpoint; 136 on Azure"),
 "o-series mini":      (209, None, "o3-mini; o4-mini high is 136"),
 "Claude Fable 5.1":   (67, 278.20, "max effort with fallback; xhigh 60, high 49"),
 "Claude Fable 5":     (66, 99.67, "with fallback"),
 "Claude Opus 5":      (51, 79.03, "max effort; model page gives 52.7 t/s, TTFT 52.98s"),
 "Claude Opus 4.8":    (58, 29.32, "max effort"),
 "Claude Opus 4.7":    (44, 21.61, "max effort"),
 "Claude Opus 4.6":    (44.3, None, "max effort, model page; Vertex series 43"),
 "Claude Opus 4.5":    (44.5, None, "AA model page; Vertex series 40"),
 "Claude Opus 4.1":    (24, None, "OpenRouter/Vertex, unexcitedneurons series"),
 "Claude Opus 4":      (23, None, "OpenRouter/Vertex, unexcitedneurons series"),
 "Claude Sonnet 4.6":  (45.9, None, "max effort, model page; Vertex series 51"),
 "Claude Sonnet 4.5":  (47.3, None, "reasoning, model page; Vertex series 41"),
 "Claude Haiku 4.5":   (85, 20.31, "reasoning; 78 t/s non-reasoning at 0.74s"),
 "Gemini 3.1 Pro":     (128, None, "Gemini 3 Pro Preview measurement, carried forward"),
 "Gemini 2.5 Pro":     (120.7, None, "AA"),
 "Gemini 3.5 Flash":   (221.0, None, "AA"),
 "Gemini 3 Flash preview": (218, None, "AA"),
 "Gemini 2.5 Flash":   (280, None, "derived from AA's 22% gap to Gemini 3 Flash"),
 "Grok 4":             (132, None, "AA"),
 "Grok 4.20":          (100.8, None, "0309 v2 reasoning; TTFT 19.4s"),
}


# ---- per-identity verdict from the pricing column alone
VERDICT = {
 "GPT-6 Astra": ("supports, and points slightly higher than 200B",
   "2.5x Sol and 1.77x GPT-5.5 on the blended 7:2:1 price, at one date on one fleet. Face-value "
   "reading gives 250B on a 100B Sol and 375B on a 150B Sol; markup-equalization against OpenAI's "
   "own ladder gives 333B. Only the sqrt reading lands at or below 200B (158-237B). Pricing makes "
   "200B a central-to-low figure, not a ceiling. The recurrent-depth report is the reason not to "
   "push the central up: looped compute raises prefill cost and price without raising parameters."),
 "GPT-5.6 Sol": ("supports 150B",
   "2.30x GPT-5 on the blended price across 11 months. Deflating by the roughly 2x per-generation "
   "hardware improvement the OpenAI report assumes leaves about 1.5x on a same-hardware basis, "
   "which is the proposed 150B against a 100B GPT-5 to two significant figures."),
 "Claude Fable 5.1": ("supports 150B as a floor; its own central is nearer 190B",
   "2.0x Opus 5 on input and output, 1.86x on the blended price after Fable's 0.025x cache-read "
   "multiple. Face value on a 100B Opus 5 gives 186B; sqrt gives 137B. Fable sits exactly at the "
   "median markup of Anthropic's own ladder, so within-lab pricing is fully consistent with 150B. "
   "Cross-lab it is identical to Astra to the dollar, which cannot both be true of two models of "
   "different size unless margins differ."),
 "Claude Fable 5": ("same as Fable 5.1", "Identical list price. The only change at 5.1 was the "
   "cache-read multiple, 0.10x to 0.025x, which is a packaging move for agentic re-reads."),
 "Claude Opus 5": ("supports keeping 100B; cannot discriminate within the Opus line",
   "$5/$25 has been unchanged across Opus 4.5, 4.6, 4.7, 4.8 and 5, nine months and a hardware "
   "generation. Price carries no within-line information. The one large move in the family is the "
   "3x cut from Opus 4.1's $15/$75, which happened while Anthropic's inference margin rose from "
   "38% to 70%, so it is a cost step and not a margin step."),
 "Claude Opus 4.1": ("supports 180B being above the Opus 4.5+ line",
   "3x the Opus 4.5+ price at a rising-margin moment. A 3x cost reduction over 2.4 months is far "
   "more than hardware alone delivers, so some of it is the model. The registry's 1.8x step from "
   "180B to 100B is the conservative reading of a 3x price step."),
 "Claude Haiku 4.5": ("weakly supports the move from 20B to 40B",
   "$1/$5 is one third of Sonnet 4.5's $3/$15 and one fifth of Opus's $5/$25. On a 100B Sonnet the "
   "price ratio gives 33B at face value. That is nearer 40B than 20B, but a third of the price is "
   "also exactly what a tier boundary looks like."),
 "Claude Sonnet 4.6": ("cannot discriminate",
   "Sonnet held $3/$15 from Sonnet 4 through 4.6, then Sonnet 5 cut to $2/$10 and made the "
   "introductory price permanent. A cut announced as introductory and then kept is a competitive "
   "decision, not a size disclosure."),
 "GPT-5": ("supports 100B as the anchor", "The anchor the rest of the OpenAI ladder is read "
   "against. Its own markup, 58x marginal decode cost at 100B, is at the low end of OpenAI's "
   "range, which is what a volume tier looks like."),
 "GPT-5.6 Luna": ("supports 8B", "$0.20/$1.20 is within 4% of GPT-5.4 nano's $0.20/$1.25, and its "
   "markup at 8B, 88x, sits exactly on OpenAI's ladder median. No reason to move."),
 "GPT-5 nano": ("cannot discriminate", "$0.05/$0.40 gives the lowest markup in the OpenAI set, 29x "
   "at 8B. Either the nano tier was sold below the ladder margin for share, or it is smaller than "
   "8B. Pricing cannot separate those."),
 "Gemini 3.1 Pro": ("contradicts the proposed 130B if read cross-lab; supports it within Google",
   "$2/$12 is one fifth of Astra and Fable on input. Read against them it would put Google's "
   "flagship at 40-80B. Read within Google's own ladder it is 1.33x Gemini 3.5 Flash and 8x "
   "Flash-Lite, consistent with the proposed 130B/40B/20B. Google serves on its own TPUs at an "
   "internal cost no merchant buyer pays, so the cross-lab reading is the one to discard."),
 "Gemini 2.5 Pro": ("supports 100B within Google's ladder",
   "12.5:3:1 Pro:Flash:Flash-Lite input ratio at the 2.5 generation, which the Google report "
   "already uses. Pricing adds nothing new."),
 "Gemini 3.5 Flash": ("contradicts holding Flash at 40B, mildly",
   "$1.50/$9.00 gives a 131x markup at 40B, the highest in Google's set and 2.3x the Google median. "
   "Either Flash grew past 40B or Google is pricing the Flash tier on capability. Google's own "
   "cross-generation price rise, 3.5 Flash above 2.5 Pro, says the second."),
 "Gemini 3.1 Flash-Lite": ("cannot discriminate", "44x markup at 20B, at Google's ladder median. "
   "Consistent with 20B and with anything from 10B to 40B."),
 "Grok 4": ("cannot discriminate", "$3/$15 gives a 44x markup at the proposed 200B, half OpenAI's "
   "ladder median and a quarter of Anthropic's. Either Grok 4 is smaller than 200B or xAI prices "
   "below the market. xAI's subsequent moves, Grok 4.20 at a 2:1 output:input ratio and Grok 4.6 "
   "at 3:1 where everyone else runs 5:1 to 8:1, say the second."),
 "Grok 4.20": ("contradicts 70B on a naive read; discarded",
   "$1.25/$2.50 gives a 21x markup at 70B, the lowest in the whole set, and the 2:1 output:input "
   "ratio is unique. Naively that reads as a 15-30B model. xAI is pricing decode at a discount "
   "nobody else offers, so this is the clearest case in the set of positioning swamping cost."),
}
VERDICT.update({
 "Claude Opus 4.5": ("supports keeping 100B", "Same $5/$25 as Opus 4.6, 4.7, 4.8 and 5. The Opus "
   "line has one price and no within-line resolution. The 3x cut from Opus 4.1 lands at this model "
   "and is the only Opus price signal in the record."),
 "Claude Opus 4.6": ("supports keeping 100B", "Same $5/$25 as the rest of the Opus line; no signal."),
 "Claude Opus 4.7": ("supports keeping 100B", "Same $5/$25 as the rest of the Opus line; no signal. "
   "Fast mode is not offered on 4.7 and returns an error, so the fast-tier confound does not apply."),
 "Claude Opus 4.8": ("supports keeping 100B", "Same $5/$25 as the rest of the Opus line, while the "
   "fast tier fell 3x from $30/$150 to $10/$50. A serving-side gain shows up in the fast tier and "
   "not the standard one, which is what the price record shows here."),
 "Claude Opus 4": ("supports 180B being above the Opus 4.5+ line", "Shares Opus 4.1's $15/$75. See "
   "the Opus 4.1 row."),
 "Claude Sonnet 4.5": ("cannot discriminate", "$3/$15 from Sonnet 4 through Sonnet 4.6, then $2/$10 "
   "at Sonnet 5. A flat price across three releases and then a cut announced as introductory is a "
   "competitive record, not a size record. Its 88x markup at 100B is at Anthropic's ladder median "
   "less a flagship premium, which is what a volume tier looks like."),
 "Claude Sonnet 4": ("cannot discriminate", "Shares Sonnet 4.5's $3/$15."),
 "Claude Haiku 3.5": ("weakly supports the move from 20B to 30B", "Launched at $1/$5, four times "
   "Haiku 3's $0.25/$1.25, then cut 20% to $0.80/$4 five weeks later. A 4x launch step cut 20% "
   "within five weeks is the Anthropic report's own reading and pricing adds nothing to it."),
 "GPT-5.4": ("supports 100B", "$2.50/$15 gives an 88x markup at 100B, exactly OpenAI's ladder "
   "median. Consistent with the shared GPT-5 family prior and with no step up at the point releases."),
 "GPT-5 mini": ("supports 20B", "$0.25/$2 is one fifth of GPT-5 on both components, and its 58x "
   "markup at 20B is identical to GPT-5's at 100B. The mini tier is priced exactly one fifth of the "
   "full tier, which is the same ratio the priors carry."),
 "o3 (repriced)": ("cannot discriminate", "The repricing from $10/$40 to $2/$8 with the weights "
   "held fixed is the single strongest piece of evidence in this note that price levels are not "
   "model sizes. The post-cut $2/$8 gives a 94x markup at 50B, near OpenAI's ladder median, which "
   "tells you the cut moved o3 from a launch premium to the ladder and nothing about its size."),
 "GPT-4.1": ("cannot discriminate", "Same $2/$8 as post-cut o3 and a 94x markup at 50B. GPT-4.1 is "
   "priced below GPT-4o at comparable speed, which bounds its active count at or below GPT-4o's; "
   "that is the OpenAI report's reading and pricing does not improve on it."),
 "Gemini 2.5 Flash": ("supports the move from 40B to 25B, weakly", "$0.30/$2.50 against DeepSeek's "
   "own $0.27 input for a disclosed 37B-active model. Google is not selling below cost, so its cost "
   "is under DeepSeek's price. That is a bound rather than an estimate, and it is the same argument "
   "the Google report already makes."),
})
DEFAULT_HIST = ("historical price only",
  "Launch or delisted price. Cross-era price ratios are confounded by roughly 2x per hardware "
  "generation and by the industry-wide repricing of 2024-2026, so no size inference is drawn.")
DEFAULT_NONE = ("no usable price", "No list price retrieved for this identity.")

def load_props():
    props = {}
    for f in ("openai-proposals.csv", "anthropic-proposals.csv",
              "google-xai-others-proposals.csv"):
        for r in csv.DictReader(open(os.path.join(MP, f))):
            key = r["model_id"].strip()
            if key == "(no registry row)":
                key = "REF-" + r["model"].strip().lower().replace(" ", "-").replace(".", "-")
            props[key] = r
    return props

def num(x):
    try:
        return float(x.replace(",", "").replace("B", "").strip()) if x else None
    except Exception:
        return None

def main():
    props = load_props()
    rows = []
    seen = set()
    for path, reg in ((os.path.join(DSET, "models.csv"), "dataset"),
                      (os.path.join(ROOT, "models.csv"), "claude-rows")):
        for r in csv.DictReader(open(path)):
            if r["active_parameters_basis"] != "estimated":
                continue
            if r["company"] in ("Gulordava et al. research team", "Facebook",
                                "OpenAI; Allen Institute for Artificial Intelligence; Harvard University"):
                continue
            if r["model_id"] in seen:
                continue
            seen.add(r["model_id"])
            rows.append((r, reg))
    # the two reference rows
    # Release dates are left blank: establishing them is the Anthropic report's job, not this one.
    for mid, name, comp, date in (("REF-claude-fable-5-1", "Claude Fable 5.1", "Anthropic", ""),
                                  ("REF-claude-fable-5", "Claude Fable 5", "Anthropic", "")):
        rows.append(({"model_id": mid, "model": name, "company": comp,
                      "model_release_date": date, "active_parameters": ""}, "reference (no registry row)"))

    fields = ["model_id", "model", "company", "registry", "model_release_date",
              "price_identity", "price_status", "input_usd_per_mtok",
              "cached_input_usd_per_mtok", "cached_input_multiple", "output_usd_per_mtok",
              "output_to_input_price_ratio", "batch_discount", "reasoning_token_pricing",
              "price_source", "price_retrieved", "output_tokens_per_sec",
              "aa_latency_to_first_answer_token_s", "throughput_config_note",
              "throughput_source", "throughput_retrieved", "current_active_prior",
              "proposed_active_central", "proposed_low", "proposed_high",
              "modeled_cost_in_usd_per_mtok", "modeled_cost_out_usd_per_mtok",
              "markup_output_over_marginal_cost", "pricing_evidence", "notes"]
    out = []
    for r, reg in sorted(rows, key=lambda t: (t[0]["company"], t[0]["model_release_date"] or "0",
                                              t[0]["model_id"])):
        mid = r["model_id"]
        pid, pin, pc, pout, status, psrc = PRICE.get(mid, (None, None, None, None, "not_retrieved", None))
        th = THRU.get(pid, (None, None, None))
        pr = props.get(mid, {})
        cur = num(pr.get("current_active_prior", "")) or (float(r["active_parameters"]) if r.get("active_parameters") else None)
        cen = num(pr.get("proposed_active_central", ""))
        lo = num(pr.get("proposed_low", ""))
        hi = num(pr.get("proposed_high", ""))
        P = cen or cur
        ci = co = mk = None
        if P:
            ci, co = cm.cost_per_mtok(P)
            if pout:
                mk = pout / co
        batch = "0.5x" if psrc in (A, O, G) else ""
        out.append({
            "model_id": mid, "model": r["model"], "company": r["company"], "registry": reg,
            "model_release_date": r["model_release_date"],
            "price_identity": pid or "", "price_status": status,
            "input_usd_per_mtok": pin if pin is not None else "",
            "cached_input_usd_per_mtok": pc if pc is not None else "",
            "cached_input_multiple": (round(pc / pin, 4) if (pc and pin) else ""),
            "output_usd_per_mtok": pout if pout is not None else "",
            "output_to_input_price_ratio": (round(pout / pin, 2) if (pout and pin) else ""),
            "batch_discount": batch,
            "reasoning_token_pricing": ("billed at the output rate; no separate rate published"
                                        if pout else ""),
            "price_source": psrc or "", "price_retrieved": ("2026-09-13" if psrc else ""),
            "output_tokens_per_sec": th[0] if th[0] is not None else "",
            "aa_latency_to_first_answer_token_s": th[1] if th[1] is not None else "",
            "throughput_config_note": th[2] or "",
            "throughput_source": ("artificialanalysis.ai" if th[0] else ""),
            "throughput_retrieved": ("2026-09-13" if th[0] else ""),
            "current_active_prior": int(cur) if cur else "",
            "proposed_active_central": int(cen) if cen else "",
            "proposed_low": int(lo) if lo else "", "proposed_high": int(hi) if hi else "",
            "modeled_cost_in_usd_per_mtok": round(ci, 5) if ci else "",
            "modeled_cost_out_usd_per_mtok": round(co, 5) if co else "",
            "markup_output_over_marginal_cost": round(mk) if mk else "",
            "pricing_evidence": (VERDICT.get(pid, DEFAULT_HIST if pout else DEFAULT_NONE))[0],
            "notes": (VERDICT.get(pid, DEFAULT_HIST if pout else DEFAULT_NONE))[1],
        })
    with open(OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for o in out:
            w.writerow(o)
    print("wrote", OUT, len(out), "rows")
    npriced = sum(1 for o in out if o["price_status"] == "current")
    print("  current list price:", npriced, " any price:",
          sum(1 for o in out if o["output_usd_per_mtok"] != ""),
          " throughput:", sum(1 for o in out if o["output_tokens_per_sec"] != ""))

if __name__ == "__main__":
    main()
