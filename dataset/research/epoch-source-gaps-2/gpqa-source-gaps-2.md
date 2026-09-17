# Remaining GPQA source-table records

This batch reconstructs the 21 remaining GPQA Diamond keys in the retained Epoch output-length table after excluding the four rows reviewed in epoch-source-gaps. A check of production model IDs plus GPQA tasks found no existing counterpart, including aliases. Phi-3's whitespace mismatch was already covered for MATH, not GPQA. Mixtral has two distinct source-table configurations with different measured output means and scores; they share one model record. This is source-record coverage, not a claim that these observations are independent experiments or all possible GPQA settings.

## Human baseline

The baseline is the **second expert validator**: a contractor holding or pursuing a PhD in the question's own scientific domain, hired by the [original GPQA paper](https://arxiv.org/abs/2311.12022) (§2.1, §2.3, §3.1, Appendix A.5.2) to answer the revised question after the writer acted on the first expert's feedback. Experts may use Google provided they declare it, must write an explanation, and after seeing the correct answer must give feedback and suggest revisions; on Diamond they reported sufficient expertise on 97.0% of validations. The revised question is the text the AI is scored on, so this expert is doing the AI's task, plus the explanation and feedback work.

From the [retained Diamond CSV](https://openaipublic.blob.core.windows.net/simple-evals/gpqa_diamond.csv), `Validator Answered Correctly_EV_2` gives **161/198 = 81.3131%**, reproducing the paper's Table 2 Diamond figure of 81.3%, and `Self-reported time (minutes)_EV_2` over the same 198 attempts gives a mean of **1,560.909090909091 seconds** (26.02 minutes; median 1,200 seconds; range 2 to 360 minutes; 48 reports under 15 minutes, which are retained). No filter on correctness or speed. The times are self-reported and cover explanation and feedback as well as answering, so they bound time-to-answer from above. 32 distinct people supplied the 198 second validations, and the same 198 observations are reused across every model row rather than being independent human samples per row.

Diamond admits a question only when the first expert validator answered it correctly, so `Validator Answered Correctly_EV_1` is 1 on all 198 records and the pooled two-expert figure of 359/396 = 90.66% measures the selection rule. The second expert's 81.31% is the only expert number the selection does not force, and the paper (§3.2) places true expert accuracy on Diamond between the unselected extended-set 64.8% and this 81.3%.

This replaces the earlier non-expert-validator baseline of 131/594 = 22.05%, which sat below the 25% four-choice guessing rate: that human did not do the task, so labelling an AI above or far above them said nothing. Re-anchored 2026-09-14.

Labelling follows `../COLUMNS.md`. The expert is 56.31 points above the 25% chance floor, so half of that puts the `below` floor at **53.16%**; rows under it are withheld to `agent-work/removed/excluded.csv`. `far_above` would require the AI more than 112.6 points above chance and is unreachable on a four-choice benchmark. Within the retained range, a score within five percentage points of 81.31% is `match` (76.31-86.31%), below that band `below`, above it `above`.

## Compute recipe

The [original Epoch table](https://epoch.ai/data-insights/output-length) supplies mean output tokens, including reasoning tokens, and mean accuracy. It supplies no native prompts, input/cache decomposition or failed-call usage. We use the [author's evaluator](https://gist.github.com/tadamcz/a61515465e34a3c66f3a78673502bc3f), all 198 actual questions and four answer choices, plus 12 assumed chat-wrapper positions. The retained gist revision is `69ce610eab3ffc263ade42676e29c478087dd658`; the downloaded metadata was updated in August 2026. It supports a prompt reconstruction, not proof of the exact prompt served in each historical run. Answer order is fixed only to count input tokens. An independent check on the preceding four GPQA rows found negligible length effects from reordering the four choices.

The central workload is reconstructed mean input plus reported mean output, multiplied by the model's shared FLOPs-per-token coefficient. Output reasoning is already included. There is no benchmark-size or repeated-epoch multiplier: this work unit is one normalized question, and the source does not establish an attempt count. No unlogged retries or helper calls are invented. Full fresh input is assumed because native cache data are absent; cached-context attention, if present, is not separately measured. All points therefore use `derived_assumed_inputs`, even when the model size is reported. The coefficient's usual context-dependent attention omission also applies; `compute_flops` carries that term separately (`research/attention-correction.md`).

`calculations.json` retains all 198 input counts per configuration, the exact source row, arithmetic, source hashes, and two scenarios: ±20 wrapper positions and ±50% reconstructed input. These scenarios are sensitivity checks, not confidence intervals or native measurements. Unknown cache and serving wrappers remain unresolved. For the closed OpenAI models, their shared parameter priors remain estimated and scale the whole point proportionally.

## Tokenizers and model evidence

Original immutable repositories provide DeepSeek LLM, Qwen 1.5, Yi, Phi-3, Mistral v0.1/v0.3, Mixtral v0.1, NeMo and Ministral 8B tokenizers. The published 8B Ministral vocabulary is an explicit same-release-family proxy for the closed 3B model. The unresolved `open-mistral-7b` API alias uses the original v0.1 vocabulary as a family proxy; its model date stays blank.

Meta's model cards are original evidence for Llama identities, sizes and release dates. Their tokenizer downloads require access, so this batch uses explicitly identified public NousResearch mirrors for Llama 2, Llama 3 and Llama 3.1. These are mirror records, not newly signed Meta artifacts. The Llama 2 SentencePiece file replaces the earlier unrelated Phi-3 proxy for this new observation.

The [Gemma 2 paper](https://arxiv.org/html/2408.00118v1), section 3.1, explicitly shares the Gemma 1 tokenizer. We use Google's public `gemma_pytorch` SentencePiece file at commit `33b652c465537c6158f9a472ea5700e5e770ad3f`. Table 2 reports 917,962,752 embedding plus 8,324,201,984 other parameters, matching the shared 9,242,164,736 count. This is a supported vocabulary identity, not an unrelated tokenizer proxy.

OpenAI's retained [tiktoken model mapping](https://github.com/openai/tiktoken/blob/0.14.0/tiktoken/model.py) maps GPT-3.5/GPT-4 to cl100k_base and o1 to o200k_base. Both original BPE files and the original regex definitions are retained; reconstruction is offline. GPT-3.5's 7B conditional estimate comes from the [original output-rank experiment](https://arxiv.org/html/2403.09539v2#S4), with the same estimate transferred to 1106. The experiment does not disclose routing or layer depth. GPT-4-0613 and o1 retain their shared assumed architecture priors, not reported sizes; the model CSV links their existing derivations. These rows do not infer parameters from scores or price.

The original DeepSeek card supplies 67B; original Meta cards supply dense Llama 2 70B and Llama 3/3.1 8B; original Yi cards/configs supply both 34B revisions; Microsoft's card supplies dense Phi-3-medium 14B. Mistral's [Ministraux release](https://mistral.ai/news/ministraux/) identifies 3B and 8B and public availability on October 16, 2024. Shared model records are copied unchanged after this identity/architecture check. Existing corrected release dates are retained rather than copying the source table's dates (notably GPT-3.5-0125, Gemma 2, Mistral v0.3, Yi-34B and Phi-3).

## Qwen models

The original [Qwen1.5-32B announcement](https://qwenlm.github.io/blog/qwen1.5-32b/) is dated **2024-04-02** and announces both the base and chat weights, one day before Epoch's table date. The [Qwen1.5 announcement](https://qwenlm.github.io/blog/qwen1.5/) establishes **2024-02-04** availability for 72B. The earlier page has since added later sizes; its conclusion still describes the original six sizes including 72B. Do not use that page's updated size list to backdate 32B.

Both are dense transformer decoders. Original configs give 32B: 64 layers, hidden width 5,120, FFN width 27,392, 40 query heads and 8 KV heads; 72B: 80 layers, hidden width 8,192, FFN width 24,576, 64 query/KV heads. Both use vocabulary 152,064 with untied embeddings. Their shared coefficients use the rounded published **32B** and **72B** counts, or **64B** and **144B FLOPs/token**. A direct tensor-dimension check, including QKV biases, RMS norms and embeddings/output head, gives 32,512,218,112 and 72,287,920,128 parameters. Using those exact totals instead changes compute by 1.60% and 0.40%. This small rounding choice does not establish equally precise physical FLOPs. Tokenizers downloaded from the two original immutable repositories are byte-identical.

## Reproduction

Use Python 3.10 or later with `tokenizers`, `sentencepiece` and `tiktoken` installed. The recorded library versions are in calculations.json. No network, inference service, API key or special working directory is needed.

```sh
python research/recompute.py SOURCE_DIRECTORY --selection research/selection.json --models models.csv --output NEW_JSON
```

Use absolute paths when running outside the batch. The output must be new and outside the source directory. The numerical replay itself needs only the three tokenizer libraries above. Primary downloads, public mirrors and failed gated accesses are identified in `agent-work/sources/models/downloads*.json`; `research/source-manifest.json` lists retained file hashes and original locators.

## reas-epoch-gpqa-ds67b

Original table key: `deepseek-llm-67b-chat` × `GPQA diamond`. AI score **24.621212%**, withheld: below the 53.16% floor against the 81.31% expert baseline. Mean input **284.035353535**, reported output **371.277777778**, total **655.313131313** text tokens; coefficient **134000000000** gives **8.7811959596e+13 FLOPs**. Original model tokenizer. Changing the input estimate by ±50% changes total FLOPs by ±21.67%; ±20 wrapper positions changes it by ±3.05%.

## reas-epoch-gpqa-gpt35-0125

Original table key: `gpt-3.5-turbo-0125` × `GPQA diamond`. AI score **27.178030%**, withheld: below the 53.16% floor against the 81.31% expert baseline. Mean input **269.813131313**, reported output **108.641414141**, total **378.454545455** text tokens; coefficient **14000000000** gives **5.29836363636e+12 FLOPs**. Official tokenizer family mapping; model size remains the shared conditional estimate. Changing the input estimate by ±50% changes total FLOPs by ±35.65%; ±20 wrapper positions changes it by ±5.28%.

## reas-epoch-gpqa-gpt35-1106

Original table key: `gpt-3.5-turbo-1106` × `GPQA diamond`. AI score **28.030303%**, withheld: below the 53.16% floor against the 81.31% expert baseline. Mean input **269.813131313**, reported output **97.974747475**, total **367.787878788** text tokens; coefficient **14000000000** gives **5.14903030303e+12 FLOPs**. Official tokenizer family mapping; model size transfers the shared conditional 0125 estimate. Changing the input estimate by ±50% changes total FLOPs by ±36.68%; ±20 wrapper positions changes it by ±5.44%.

## reas-epoch-gpqa-gpt4-0613

Original table key: `gpt-4-0613` × `GPQA diamond`. AI score **30.650253%**, withheld: below the 53.16% floor against the 81.31% expert baseline. Mean input **269.813131313**, reported output **216.474747475**, total **486.287878788** text tokens; coefficient **550000000000** gives **2.67458333333e+14 FLOPs**. Official tokenizer family mapping; model size remains the shared GPT-4 family estimate. Changing the input estimate by ±50% changes total FLOPs by ±27.74%; ±20 wrapper positions changes it by ±4.11%.

## reas-epoch-gpqa-gemma2-9b

Original table key: `gemma-2-9b-it` × `GPQA diamond`. AI score **27.462121%**, withheld: below the 53.16% floor against the 81.31% expert baseline. Mean input **266.535353535**, reported output **317.893939394**, total **584.429292929** text tokens; coefficient **18484329472** gives **1.08027836036e+13 FLOPs**. Original Google vocabulary; Gemma 2 paper explicitly shares the Gemma 1 tokenizer. Changing the input estimate by ±50% changes total FLOPs by ±22.80%; ±20 wrapper positions changes it by ±3.42%.

## reas-epoch-gpqa-llama2-70b

Original table key: `Llama-2-70b-chat-hf` × `GPQA diamond`. AI score **26.325758%**, withheld: below the 53.16% floor against the 81.31% expert baseline. Mean input **305.126262626**, reported output **445.914141414**, total **751.040404040** text tokens; coefficient **140000000000** gives **1.05145656566e+14 FLOPs**. Public NousResearch mirror of the original Llama 2 vocabulary; exact serving wrapper is unavailable. Changing the input estimate by ±50% changes total FLOPs by ±20.31%; ±20 wrapper positions changes it by ±2.66%.

## reas-epoch-gpqa-llama3-8b

Original table key: `Meta-Llama-3-8B-Instruct` × `GPQA diamond`. AI score **26.073232%**, withheld: below the 53.16% floor against the 81.31% expert baseline. Mean input **269.707070707**, reported output **378.924242424**, total **648.631313131** text tokens; coefficient **16000000000** gives **1.03781010101e+13 FLOPs**. Public NousResearch mirror of the named model tokenizer. Changing the input estimate by ±50% changes total FLOPs by ±20.79%; ±20 wrapper positions changes it by ±3.08%.

## reas-epoch-gpqa-llama31-8b

Original table key: `Llama-3.1-8B-Instruct` × `GPQA diamond`. AI score **25.946970%**, withheld: below the 53.16% floor against the 81.31% expert baseline. Mean input **269.707070707**, reported output **1043.449494949**, total **1313.156565657** text tokens; coefficient **16000000000** gives **2.10105050505e+13 FLOPs**. Public NousResearch mirror of the named model tokenizer. Changing the input estimate by ±50% changes total FLOPs by ±10.27%; ±20 wrapper positions changes it by ±1.52%.

## reas-epoch-gpqa-ministral3b

Original table key: `ministral-3b-2410` × `GPQA diamond`. AI score **25.252525%**, withheld: below the 53.16% floor against the 81.31% expert baseline. Mean input **268.247474747**, reported output **461.681818182**, total **729.929292929** text tokens; coefficient **6000000000** gives **4.37957575758e+12 FLOPs**. Original Ministral 8B tokenizer used as an explicit same-release-family proxy for the closed 3B endpoint. Changing the input estimate by ±50% changes total FLOPs by ±18.37%; ±20 wrapper positions changes it by ±2.74%.

## reas-epoch-gpqa-ministral8b

Original table key: `ministral-8b-2410` × `GPQA diamond`. AI score **27.146465%**, withheld: below the 53.16% floor against the 81.31% expert baseline. Mean input **268.247474747**, reported output **506.762626263**, total **775.010101010** text tokens; coefficient **16000000000** gives **1.24001616162e+13 FLOPs**. Original released Ministral 8B tokenizer; historical provider wrapper is unavailable. Changing the input estimate by ±50% changes total FLOPs by ±17.31%; ±20 wrapper positions changes it by ±2.58%.

## reas-epoch-gpqa-mistral7bv03

Original table key: `Mistral-7B-Instruct-v0.3` × `GPQA diamond`. AI score **15.183081%**, withheld: below the 53.16% floor against the 81.31% expert baseline. Mean input **302.101010101**, reported output **481.308080808**, total **783.409090909** text tokens; coefficient **14000000000** gives **1.09677272727e+13 FLOPs**. Original v0.3 tokenizer. Changing the input estimate by ±50% changes total FLOPs by ±19.28%; ±20 wrapper positions changes it by ±2.55%.

## reas-epoch-gpqa-mistral7b-api

Original table key: `open-mistral-7b` × `GPQA diamond`. AI score **13.226010%**, withheld: below the 53.16% floor against the 81.31% expert baseline. Mean input **302.101010101**, reported output **456.828282828**, total **758.929292929** text tokens; coefficient **14600000000** gives **1.10803676768e+13 FLOPs**. Original v0.1 tokenizer used as a family proxy: the served API alias revision is unresolved. Changing the input estimate by ±50% changes total FLOPs by ±19.90%; ±20 wrapper positions changes it by ±2.64%.

## reas-epoch-gpqa-nemo

Original table key: `open-mistral-nemo-2407` × `GPQA diamond`. AI score **29.892677%**, withheld: below the 53.16% floor against the 81.31% expert baseline. Mean input **268.247474747**, reported output **392.595959596**, total **660.843434343** text tokens; coefficient **24000000000** gives **1.58602424242e+13 FLOPs**. Original released NeMo tokenizer. Changing the input estimate by ±50% changes total FLOPs by ±20.30%; ±20 wrapper positions changes it by ±3.03%.

## reas-epoch-gpqa-mixtral8x7b

Original table key: `Mixtral-8x7B-Instruct-v0.1` × `GPQA diamond`. AI score **30.587121%**, withheld: below the 53.16% floor against the 81.31% expert baseline. Mean input **302.101010101**, reported output **467.732323232**, total **769.833333333** text tokens; coefficient **25800000000** gives **1.98617e+13 FLOPs**. Original released tokenizer; this is the source table HF-style configuration. Changing the input estimate by ±50% changes total FLOPs by ±19.62%; ±20 wrapper positions changes it by ±2.60%.

## reas-epoch-gpqa-mixtral8x7b-api

Original table key: `open-mixtral-8x7b` × `GPQA diamond`. AI score **29.829545%**, withheld: below the 53.16% floor against the 81.31% expert baseline. Mean input **302.101010101**, reported output **510.934343434**, total **813.035353535** text tokens; coefficient **25800000000** gives **2.09763121212e+13 FLOPs**. Original released tokenizer for the v0.1 family; distinct source table API configuration with different scores and output length. Changing the input estimate by ±50% changes total FLOPs by ±18.58%; ±20 wrapper positions changes it by ±2.46%.

## reas-epoch-gpqa-qwen15-32b

Original table key: `qwen1.5-32b-chat` × `GPQA diamond`. AI score **30.744949%**, withheld: below the 53.16% floor against the 81.31% expert baseline. Mean input **273.808080808**, reported output **408.818181818**, total **682.626262626** text tokens; coefficient **64000000000** gives **4.36880808081e+13 FLOPs**. Original named-model tokenizer. Changing the input estimate by ±50% changes total FLOPs by ±20.06%; ±20 wrapper positions changes it by ±2.93%.

## reas-epoch-gpqa-qwen15-72b

Original table key: `qwen1.5-72b-chat` × `GPQA diamond`. AI score **28.819444%**, withheld: below the 53.16% floor against the 81.31% expert baseline. Mean input **273.808080808**, reported output **397.131313131**, total **670.939393939** text tokens; coefficient **144000000000** gives **9.66152727273e+13 FLOPs**. Original named-model tokenizer. Changing the input estimate by ±50% changes total FLOPs by ±20.40%; ±20 wrapper positions changes it by ±2.98%.

## reas-epoch-gpqa-yi15-34b

Original table key: `Yi-1.5-34B-Chat` × `GPQA diamond`. AI score **31.976010%**, withheld: below the 53.16% floor against the 81.31% expert baseline. Mean input **293.489898990**, reported output **732.065656566**, total **1025.555555556** text tokens; coefficient **68000000000** gives **6.97377777778e+13 FLOPs**. Original named-model tokenizer. Changing the input estimate by ±50% changes total FLOPs by ±14.31%; ±20 wrapper positions changes it by ±1.95%.

## reas-epoch-gpqa-yi34b

Original table key: `Yi-34B-Chat` × `GPQA diamond`. AI score **14.741162%**, withheld: below the 53.16% floor against the 81.31% expert baseline. Mean input **293.489898990**, reported output **331.373737374**, total **624.863636364** text tokens; coefficient **68000000000** gives **4.24907272727e+13 FLOPs**. Original named-model tokenizer. Changing the input estimate by ±50% changes total FLOPs by ±23.48%; ±20 wrapper positions changes it by ±3.20%.

## reas-epoch-gpqa-phi3-medium

Original table key: `Phi-3-medium-128k-instruct ` × `GPQA diamond`. AI score **27.588384%**, withheld: below the 53.16% floor against the 81.31% expert baseline. Mean input **305.126262626**, reported output **502.444444444**, total **807.570707071** text tokens; coefficient **28000000000** gives **2.2611979798e+13 FLOPs**. Original named-model tokenizer. Trailing whitespace in the original table identifier is retained for the exact join. Changing the input estimate by ±50% changes total FLOPs by ±18.89%; ±20 wrapper positions changes it by ±2.48%.

## reas-epoch-gpqa-o1high

Original table key: `o1-2024-12-17_high` × `GPQA diamond`. AI score **76.767677%**, classified **match** against the 81.31% expert baseline. Mean input **265.626262626**, reported output **6357.838383838**, total **6623.464646465** text tokens; coefficient **100000000000** gives **6.62346464646e+14 FLOPs**. Official tokenizer family mapping; high reasoning effort. Shared active-size prior is estimated, not provider-reported. Changing the input estimate by ±50% changes total FLOPs by ±2.01%; ±20 wrapper positions changes it by ±0.30%.

