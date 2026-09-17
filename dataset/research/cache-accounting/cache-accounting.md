# Unreported prompt-cache use

Known cache reads are excluded from the parameter-multiplication term. When the original source omits that component, full-prefix processing remains an explicit assumption; missing values do not establish zero cache hits.

Three ARC Fireworks configurations send identical paired prompts sequentially, with millisecond gaps. [Fireworks documents automatic prompt caching](https://docs.fireworks.ai/guides/prompt-caching), but the retained run records do not identify actual hits. If only the second identical prompt were fully cached, Kimi K2.5, DeepSeek V3.2 and GLM5 workload estimates would decrease 9.02%, 11.41% and 10.02% respectively. These are sensitivity scenarios, not corrections. The central values are unchanged and classified derived_assumed_inputs. The accompanying calculator reproduces the pairing and weighted counts from the dataset sources.

The [Inspect 0.3.174 Google adapter](https://github.com/UKGovernmentBEIS/inspect_ai/blob/0.3.174/src/inspect_ai/model/_providers/google.py) does not populate cache counters. The three retained Gemini 3.1 Pro question runs also lack the field in raw provider responses. Qwen 3.6 Plus SWE has neither cache components nor raw provider responses. Their printed zero cache counts are calculation defaults, not observed zero usage. No recoverable numerical subtraction was found.

Retained provider documentation, adapter code and source hashes are in agent-work/sources/cache-accounting/. METR’s separate source-total limitation is documented in research/metr/cache-accounting.md.
