# Missing Epoch mathematics observations

Four original output-table records: three OTIS configurations and the Mistral API Mixtral observation on MATH Level5. These are source-key coverage gaps, not new benchmark releases. The API `open-mixtral-8x7b` and HF `Mixtral-8x7B-Instruct-v0.1` rows have different reported outputs and scores; they remain separate observations with the same model coefficient. [Mistral’s model page](https://docs.mistral.ai/models/mixtral-8x7b-0-1) identifies the API alias and v0.1 architecture. No additional model row is needed.

## Human baselines

OTIS uses the [original three-hour,15-question format](https://web.evanchen.cc/mockaime.html). Assuming the participant uses that allowance gives720 active seconds per question-equivalent, including unsuccessful effort. It is estimated, not a measured mean. The source score tables in the [2024 report](https://web.evanchen.cc/exams/sols-OTIS-Mock-AIME-2024.pdf)§3.1 and [2025 report](https://web.evanchen.cc/exams/sols-OTIS-Mock-AIME-2025.pdf)§3.1 give92,82,115 official submissions. The2025 introduction says83/116, but its detailed frequency tables and accompanying sentence say82/115. We use the latter. Equal weighting of papers gives51.5507246% accuracy; populations are trained contest participants. Llama2’s0% is below, DeepSeekR1’s53.33% broadly matches, and o3’s83.89% is above. The `different_assessment` flag captures humans allocating effort over a whole paper versus AI answering isolated questions. Source successful-only testsolver clocks are not substituted for all-effort exam time.

MATH uses the existing explicitly assumed600-second mean effort budget for an IMO-gold-level solver targeting roughly90% correct across1,324 Level5 questions. Rechecking original question records confirms a mixture of algebra, geometry, counting, number theory and shorter prealgebra exercises. This is not a measured90% Level5 human result. The [MATH paper](https://arxiv.org/abs/2103.03874) timed a mixed20-question test for one hour; its gold-medalist18/20 does not measure this harder subset. The600-second judgment and5–20minute sensitivity allow for harder problems than that mixed set, while OTIS testsolver tables provide a separate plausibility check. Humans see rendered diagrams; text AI receives Asymptote code. The [shared MATH baseline](../epoch/mathl5.md) records fuller question inspection. No human attempt count is invented for either duration assumption.

## Compute reconstruction

OTIS input uses all45 original question texts recovered from the original public Epoch archive identified by each record in `otis-original-question-text.json`. The later run’s short instruction is transferred to historical configurations, with12 assumed wrapper positions. MATH counts all1,324 literal Level5 test statements from the seven original task-distribution Parquets, plus50 assumed instruction/chat positions. Known output reasoning is already in the source output mean and is not counted again. Historical input/cache/retry logs are absent: full fresh input is an assumption, not observed zero cache reuse.

Llama2 uses the public NousResearch mirror’s actual SentencePiece vocabulary, https://huggingface.co/NousResearch/Llama-2-70b-chat-hf/resolve/d2b9264/tokenizer.model. The `.json` path does not exist; it was not an access restriction. DeepSeekR1 uses the explicitly transferred DeepSeekV3-0324 family tokenizer, retained from https://huggingface.co/deepseek-ai/DeepSeek-V3-0324/resolve/main/tokenizer.json. o3 uses OpenAI’s o200k public rank table and tokenizer definition. Mixtral uses its original https://huggingface.co/mistralai/Mixtral-8x7B-Instruct-v0.1/resolve/main/tokenizer.json. Hashes identify exact retained copies. No model weights are downloaded or run.

The shared coefficients are2×70B for Llama2,2×37B for R1,2×assumed50B for o3 and2×12.9B active for Mixtral. Formula: (mean reconstructed input + reported mean output)×coefficient. Context-dependent attention is omitted by this approximation and added back in `compute_flops` (`research/attention-correction.md`). The model CSV retains the coefficient’s original evidence; undisclosed o3 size remains estimated. `compute_statistic=mean` records the source workload’s averaging, not a claim that the FLOPs are directly measured. `compute_evidence=derived_assumed_inputs` records the uncertain inputs. Both subset and attempt count are not_applicable for these normalized benchmark aggregates.

Run `python3 /path/research/recompute.py --sources /path/sources --models /path/models.csv --selection /path/research/selection.json --output /path/new-output.json`. Requires tokenizers, sentencepiece, tiktoken and pyarrow. This reads retained data only and refuses output inside the sources or an existing output file. It also recomputes OTIS human accuracy directly from the retained report text tables and retains all question input counts.

## reas-epoch-otis-llama2-70b

Original identifier `Llama-2-70b-chat-hf`, benchmark `OTIS Mock AIME 2024-2025`. Input209.2 + output711.466666667 = 920.666666667 text tokens. At140000000000 FLOPs/token: **1.28893333333e+14 FLOPs**. Human720seconds. Changing wrapper length by20 positions changes total compute by2.17%.

## reas-epoch-otis-r1

Original identifier `DeepSeek-R1`, benchmark `OTIS Mock AIME 2024-2025`. Input184.311111111 + output10790.4222222 = 10974.7333333 text tokens. At74000000000 FLOPs/token: **8.12130266667e+14 FLOPs**. Human720seconds. Changing wrapper length by20 positions changes total compute by0.182%.

## reas-epoch-otis-o3high

Original identifier `o3-2025-04-16_high`, benchmark `OTIS Mock AIME 2024-2025`. Input186.6 + output13525.1777778 = 13711.7777778 text tokens. At100000000000 FLOPs/token: **1.37117777778e+15 FLOPs**. Human720seconds. Changing wrapper length by20 positions changes total compute by0.146%.

## reas-epoch-mathl5-openmixtral8x7b

Original identifier `open-mixtral-8x7b`, benchmark `MATH level 5`. Input143.9418429 + output595.256042296 = 739.197885196 text tokens. At25800000000 FLOPs/token: **1.90713054381e+13 FLOPs**. Human600seconds. Changing wrapper length by20 positions changes total compute by2.71%.
