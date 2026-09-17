# BooookScore: generating a memoir summary

## writing-book-summary-heart-gpt4

The task is to read Rob Delaney’s *A Heart That Works* and produce a roughly 720-word summary comparable to the released GPT-4 output. It includes source reading and composition, and excludes separate coherence annotation.

The original study is [Chang et al., BooookScore](https://arxiv.org/abs/2310.00785v4), Sections 2–3 and Appendices A, D and M. The record key is `a-heart-that-works.epub` in the raw and cleaned `gpt4-4096-hier` files at [commit 094bf69](https://github.com/lilakk/BooookScore/tree/094bf69bc55317b728b4b2bb679c287e0176ae6c). Retained sources are under `agent-work/sources/book-summary/`; the retained manifest checks their hashes.

### Output and human target

The complete cleaned summary was inspected. Its 721 whitespace-separated words cover Henry’s illness, the family’s hospital and home life, his death and their bereavement. It is readable, but a later recollection precedes the death account and some transitions are awkward. The human target is comparable breadth and finish, without AI assistance. This defines match; it is not a measured human comparison or a claim that every fact was verified against the memoir.

The researchers did not release the source book, so its complete text was not read for this reconstruction. The unabridged author-read audio is listed at 3 hours 25 minutes by [the audiobook retailer](https://www.audiobooks.com/audiobook/heart-that-works/638924). That supplies a scale check, not a silent-reading measurement.

### Human time

The estimate is **190 active minutes**, for a fluent adult reader able to compose a competent summary, initially unfamiliar with the book. The source-size reconstruction below implies approximately **32,947 words**. Transfer the 238 words/minute rate from [Brysbaert (2019)](https://biblio.ugent.be/publication/8647789): about **138.4 minutes reading**. Add estimated task-specific work: 15 minutes selecting and ordering the major events from reading notes, 25 minutes drafting the short narrative, and 15 minutes checking names/order and revising. The resulting 193.4 minutes is rounded to the nearest ten minutes.

This is `llm_estimate_from_data`, with `point_estimate`, subset `all` and an unknown attempt count. Brysbaert’s original paper, p. 5, computes 238 WPM as the unweighted mean of 190 study rates involving 18,573 participants; Table 1 mixes fiction, nonfiction, unspecified genres and some other Latin-alphabet languages. The paper subsequently presents 238 as its English nonfiction benchmark. Those study and participant totals do not establish the number of timed reading attempts. They are not a sample of memoir summarizers.

The donor studies concern reading for comprehension or pleasure; they exclude proofreading and studying for fact retrieval. Note-taking and composition therefore need the added judgment above. Dividing by the mean rate gives time at that rate, not the mean of individual completion times. The estimate is deliberately not labeled a measured mean.

Use **150–300 active minutes** as a sensitivity: efficient reading and concise notes versus slower reading and more revisits to the text. Emotional breaks are excluded. Book length, prose conversion, familiarity and rereading requirements remain uncertain. The source-size assumption affects both reading time and AI input compute, so some correlation between the axes is constructed.

### Compute

The released record contains **12 initial chunk summaries and one merged summary**. Its cleaned final differs from the merged response. Count the additional GPT-4 cleanup described in Appendix D.1 and M.3; exclude the separate summary-evaluation calls. This is one recorded book-generation run, including its estimated retries: compute statistic `total`, subset `all`, and one AI attempt.

The historical chunking implementation is [scripts/chunk_data.py at 34d4cbd](https://github.com/lilakk/BooookScore/blob/34d4cbd0cdc25b813afcf78adcb075c156e4a2a4/scripts/chunk_data.py), with the accompanying `scripts/utils.py`. These original files are retained as `paper-era-chunk_data.py` and `paper-era-utils.py`; their Git blobs match the deletion patches in the April 2024 package refactor. The original code splits GPT-2 token sequences at 4,096 tokens, trims to sentence punctuation and carries the remainder forward. The later cl100k paragraph-packing implementation is not the basis of this estimate.

The authors’ public-domain example, *Reminiscences of Pioneer Days in St. Paul*, supplies a source-text calibration. Replaying historical slicing with equivalent GPT-2 BPE gives 15 nonfinal chunks averaging 4,075.9 tokens, with a 4,022–4,094 range. Use **4,080 GPT-2 tokens for each of 11 nonfinal chunks**, and an assumed half-full final chunk of 2,048: **46,928 GPT-2 tokens**. The calibration text is not this memoir, and the hidden final occupancy is not observed.

The complete example contains 61,281 GPT-2 tokens, 57,158 cl100k tokens and 43,024 whitespace-separated words. Transfer its ratios, **0.93272 cl100k tokens per GPT-2 token** and **0.70208 words per GPT-2 token**, to the inferred input. This gives approximately **43,771 GPT-4 input-text tokens** and 32,947 words. These are text/tokenizer transfers, not exact book counts. The twelve retained memoir summaries supply an alternate prose conversion: 4,638 cl100k / 4,735 GPT-2 tokens and 3,921 words. The calculator retains this alternate rather than assuming that generated summary prose has the same distribution as source-book text.

Retokenize retained outputs and reconstructed prompts with cl100k. The initial and merge templates agree with paper Appendix M.2; cleanup agrees with M.3. The paper’s 1,200-token final limit and the code’s 0.65 level ratio set prompt word budgets. All twelve chunk summaries fit in the single observed merge. Retained counts are 4,638 chunk-output tokens, 4,857 merge-input tokens, 881 merge-output tokens, and 1,030 cleanup-input plus 871 cleanup-output tokens. Prompt framing adds an assumed seven tokens per call. Exact original request formatting and native usage are unavailable.

The hierarchy retries empty, overlong or improperly terminated generations, retaining only the eventual output. Allow **5% extra hierarchical work** for discarded generations. This is an expected-work assumption, supported only in scale by the paper’s statement that hierarchical merging is less prone to overruns than incremental updating. Alternatives use zero or 25% extra work. Source-size alternatives use 3,700-token nonfinal chunks and a 512-token final chunk, or all chunks at the GPT-2 cap. The latter is an occupancy scenario under the conversion assumption, not a hard upper bound on compute. No prefix cache is assumed for this early GPT-4 run.

Total estimated workload is **60,884.4069 text tokens**, with **3.3486424 × 10^16 weight-matrix FLOPs** using the shared 550 billion FLOPs/token coefficient. The primary model remains `gpt-4-original-unspecified`, with 275 billion assumed active parameters. OpenAI’s [technical report](https://arxiv.org/abs/2303.08774) does not disclose this architecture. Appendix D describes an Azure “gpt-4 2023-03-15” checkpoint, while the public historical wrapper calls the generic `gpt-4` name. That source label is retained without treating it as a verified OpenAI checkpoint ID or release date.

The main workload is established from this book’s own twelve chunks; the missing occupancy and text conversion are assumed inputs. Thus `derived_assumed_inputs` is appropriate. The source paper’s 190,000-token corpus mean is not used: it cannot be reconciled with only 3,408 released bottom-level chunks across 100 books at a 4,096 cap.

### Reproduction

With Python 3.10+ and tiktoken (reviewed with 0.14.0), run from the published dataset directory:

```sh
python research/book-summary/recompute.py --sources sources/book-summary --config research/book-summary/config.json --output /path/to/new-result.json
```

The replay is offline, reads retained vocabulary files, checks source hashes and refuses an existing output. It extracts the public-domain example as inert pickle string opcodes; it does not deserialize arbitrary pickle objects. `calculations.json` retains central inputs, source calibrations and all sensitivities.

### Current-schema attention and range

The September15 reference registry retains GPT-4's275B active-parameter estimate and adds73 full-attention layers of width14336. Use that shared shape without changing the registry. Each of the12 initial summaries, the merge and the cleanup is a separate causal context. For each reconstructed call of length n, sum n(n+1)/2 attended positions; apply the same5% discarded-work allowance to the hierarchy's weight and attention terms. The resulting position-weighted mean context is 2168.231. This avoids treating the entire book workflow as one long conversation.

Attention adds 1.650265% to the weight term, producing 3.403903856e+16 FLOPs. The current model band200–350B gives 2.480431682e+16–4.326517638e+16 FLOPs. Each bound recomputes the model's attention shape using the current OpenAI0.65 full-attention share and rounded dense-bracket rule. Context is reconstructed per call, so the cache-implied context band does not apply. The range does not include the book-length, tokenizer-transfer, retry or human-time scenarios, which remain separate in the calculation.

The source identifies one complete book-generation work unit: compute statistic total, subset all, one AI attempt. Human timing remains an estimate transferred from reading-rate data, with unknown donor attempt count. No source payment or native usage total is available for this book, so both cost amounts and the AI price date are blank and both cost bases are not_available.
