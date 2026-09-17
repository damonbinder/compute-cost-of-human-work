# Who has published parameter-count estimates for frontier closed models

*Created 2026-09-13 12:52.*

Scope: every published estimate of total or active parameters located for the closed models in
`../../models.csv` and `../../../AI Compute vs Human Time/dataset/models.csv` whose
`active_parameters_basis` is `estimated`, with priority on the current frontier. This is a census of
estimates and estimators, not a synthesis: the point is to show the whole field, including the parts of
it that are empty. Machine-readable version in `estimate-survey.csv`, 102 rows, same content. Retained
extracts in `agent-work/sources/model-priors/survey/`. Neither `models.csv` was touched, and the three
existing reports (`openai.md`, `anthropic.md`, `google-xai-others.md`) were read but not edited; a
section below records where I think they are wrong.

## TL;DR

**No, nobody has done this well, and the reason is structural rather than lazy.** Five instruments exist.
One is a three-year-old insider leak covering one model. Two are serving-economics inversions, which are
the only route that targets active parameters and which carry a stated 2x error that is really closer to
3x once serving policy is admitted. One is a calibrated black-box probe published in July 2026, which is
the only instrument in the field with a cross-validated error bar, and which measures *total* parameters
and misses the one model with a known answer by 2.9x. The fifth is Elon Musk posting numbers on X, which
is the only channel through which any frontier lab has stated a size since 2020, and it only covers xAI.
Nothing else is evidence. Everything else in circulation traces back to one of these five, to a
withdrawn paper, or to nothing at all.

**Epoch AI comes closest on active parameters and IKP comes closest on total, and neither covers what the
dataset most needs.** Epoch is the only party that publishes an explicit active-parameter figure for any
current closed model: ~100B for GPT-5, and 10-30B for the mini reasoning line. It publishes **no**
parameter estimate for any OpenAI model after GPT-4o, for any Claude model ever, or for any Gemini model
ever; its `Parameters` field is blank on all of them and its model pages say "Unknown". The IKP paper
(arXiv 2604.24827) covers 201 models including 25 Claude rows, 11 Gemini rows, and 5 Grok rows, but it
estimates total rather than active, it reads safety-tuned models low by its own account, it excludes the
entire Gemini 3.x family by construction, and it has no row for Claude Opus 5, Claude Fable 5.1, GPT-5.6
Sol, or GPT-6 Astra.

**Best available figures for the six models named in the brief:**

| Model | Total (B) | Active (B) | Basis for the total | Basis for the active |
|---|---|---|---|---|
| GPT-6 Astra | 4800 | — | Ed Zitron on X, circa 2026-09-06, "per a source" | No published estimate exists |
| Claude Fable 5.1 | — | — | No estimate exists for 5.1; Fable 5 reads 5000 (FT) and 3500 (IKP) | No published estimate exists |
| GPT-5.6 Sol | 3200 | — | Ed Zitron on X, circa 2026-09-06, "per a source" | No published estimate exists |
| Claude Opus 5 | — | — | No published estimate exists | No published estimate exists |
| GPT-5 | 1800 | 100 | IKP factual-capacity probing, 90% interval 614-6300 | Epoch AI, from price, speed, and a stated comparison to Grok 2's 115B active |
| Gemini 3 Pro | — | — | Nothing usable; see below | No published estimate exists |

Read the em dashes literally. For four of the six models there is no published active-parameter figure of
any kind from any identifiable source, and for three of the six there is no published total either. The
dataset's numbers for those rows are not weakly-sourced versions of somebody's estimate; there is no
estimate for them to be weak versions of.

**GPT-5 is the exception, and it is the one place where the evidence converges.** Epoch's ~100B active and
IKP's 1.8T total imply 18x sparsity, against the 22.8x that OpenAI discloses for gpt-oss-120b. Two
instruments with unrelated failure modes, plus the developer's own architecture for a different model,
agree. That is the best-evidenced closed-model figure in the survey after GPT-4, and it is the reason the
dataset's 100B frontier prior is defensible even though nothing supports transferring it forward to Astra.

**Gemini 3 Pro is the worst-covered model in the survey and the circulating figures are all bad.** Epoch
says Unknown. IKP prints 7.3T for Gemini 3.1 Pro in a sensitivity table and then tells you not to use it,
because Gemini 3.1 Pro is the paper's own top calibration landmark and its score at that tier is inflated
by construction. The widely shared ~7.5T comes from a regression whose author labels it "vibe-mathing" and
whose unrestricted fit returned 2.3 quadrillion parameters. The "1.5T total, 200B active" figures that
dominate search results cite a "Gemini 3 technical brief from Google Research" that does not exist. The
only defensible statement about Gemini 3 Pro's active count is a serving bound of 70-320B, and the width
of that comes from not knowing how many chips it is sharded over.

Next action: nothing in this survey requires a dataset change on its own. What it should change is how the
three prior reports' confidence grades are read, and it adds one source—the IKP paper—that the
Anthropic and Google/xAI reports missed entirely.

## The five instruments, ranked

| Instrument | Constrains | Coverage | Stated error | Real error |
|---|---|---|---|---|
| Developer disclosure | both | gpt-oss, GPT-3, Codex, Grok-1, Grok-2, Gemini Nano, Gemini 1.5 Flash-8B | exact | exact |
| Insider leak | both | GPT-4 (2023); Sol and Astra totals (2026, unverifiable) | none stated | unbounded |
| Serving economics | active | every served model | 2x | 3x |
| Factual-capacity probing (IKP) | total | 201 models, but not the newest | 3.2x | 3x, biased low for Claude, 2.9x low on GPT-4 |
| Developer statements on X | total | xAI only | none stated | Epoch grades them Likely, 10x |

Three things follow from the table that are worth stating separately.

**Only one instrument measures the quantity the dataset stores.** `active_parameters` is what sets FLOPs
per token, and serving economics is the only route to it. Every other instrument measures total, and
converting total to active requires a sparsity assumption that has moved from 2.3x in 2024 to 17-33x in
2026. That conversion is the largest error term in the whole exercise and nobody has published a way to
constrain it for a closed model.

**Serving economics has a confound that its practitioners do not price.** Anthropic sells a fast mode that
serves the same weights at "roughly 2.5x normal speed", and OpenAI cut o3's price 80% with the note "Same
exact model—just cheaper". Per-user throughput and list price are product decisions. The stated 2x error
bars on Epoch's and unexcitedneurons' estimates cover precision and hardware; they do not cover the lab
deciding to serve the same weights faster.

**The one instrument with a published error bar fails its own calibration check.** IKP reads GPT-4 at 622B
total against the leaked 1.8T, low by 2.9x, and ranks GPT-4 Turbo above GPT-4. Those are exactly the
comparisons where its confound bites: the probe measures knowledge per parameter, which rises with
training-data scale, so older models read small. Its two successes—gpt-oss-120b at 106B against 116.83B,
gpt-oss-20b at 16B against 20.91B—are both 2025 models, and both are models the paper misclassifies as
dense when they are disclosed mixture-of-experts.

## Every estimate found

Figures are as the source stated them. Where a source gave only a range, the range appears in the cell; the
CSV carries lower and upper bound columns for those rows. Units are billions of parameters throughout.
Rows marked `non_estimate` in the CSV are explicit statements that a figure is unknown, and they appear
here with em dashes in both numeric columns.



### OpenAI

| Model | Total (B) | Active (B) | Source | Date | Method | Corroboration |
|---|---|---|---|---|---|---|
| GPT-3 (davinci) | 174.6 | 174.6 | OpenAI, Language Models are Few-Shot Learners, Table D.1 | 2020-05-28 | Stated in the paper; dense, so active equals total | Exact. Epoch records 1.746e11 at Confident |
| text-davinci-002 (InstructGPT 175B) | 175 | 175 | OpenAI, Training language models to follow instructions | 2022-01-27 | We train three model sizes (1.3B, 6B, and 175B parameters) | Exact for the size; residual doubt is which checkpoint the API alias serves |
| gpt-3.5-turbo | — | 7 | Finlayson et al., arXiv 2403.09539 | 2024-03-14 | Softmax bottleneck: SVD of API logits measures d_model at 4096; 7B is then inferred from a dense rule of thumb the authors themselves flag as failing for MoE | The d_model measurement is uncontested; the 7B inference is contradicted by CODEFUSION 20B and by IKP 246B total |
| gpt-3.5-turbo, ada, babbage | — | — | Carlini et al., arXiv 2403.06634 (ICML 2024) | 2024-03-11 | Logit-subspace SVD attack recovers the embedding projection layer; confirms ada h=1024, babbage h=2048, and recovers gpt-3.5-turbo hidden dimension exactly | Corroborates the Finlayson method. The gpt-3.5-turbo value was withheld at OpenAI request and never published, so no parameter count follows |
| gpt-3.5-turbo | — | 20 | Microsoft CODEFUSION, arXiv 2310.17680 Table 1 | 2023-10-26 | Stated in a table with no derivation; the paper was withdrawn from arXiv | Epoch carries 20B at Likely while its own davinci-002 note says the paper was retracted because the authors did not know the parameter count |
| GPT-4 | 1800 | 280 | SemiAnalysis (Dylan Patel, Gerald Wong) | 2023-07-10 | Reported architecture: 120 layers, 16 experts of about 111B, top-2 routing, 13T training tokens | Corroborated: 6 x 2.8e11 x 1.3e13 = 2.2e25 FLOP against Epoch independent 2.1e25 training compute. Contradicted by IKP, which reads 622B total, low by 2.9x |
| GPT-4 | 1800 | 280 | Epoch AI model database | 2023-2026 | Records the SemiAnalysis leak at Likely confidence and quotes the 1.76T / 220B variant | Not independent of the SemiAnalysis row |
| GPT-4 Turbo | — | — | Epoch AI model database | 2023-2026 | Not known. Maybe smaller/sparser than GPT-4 | IKP contradicts the direction, reading Turbo at 1.05T above GPT-4 at 622B, which is IKP worst regime |
| GPT-4o | 200 | 50 | Epoch AI (Ege Erdil), Frontier language models have become much smaller, and How much energy does ChatGPT use | 2024-12-13 | Inference economics: 100-150 tok/s at $10/Mtok output against GPT-4 Turbo 55 tok/s at $30/Mtok, giving about an eighth of GPT-4; active from a quarter-activation assumption applied to the 200B central | Self-stated error a factor of 2. Order of magnitude corroborated by IKP 392B total at 2024-era sparsity. Note the widely misread 100B active is the pessimistic case built on the 400B tail |
| GPT-4o | 200 | — | Microsoft MEDEC, arXiv 2412.19260 | 2024-12-26 | Sizes mined from public articles only; authors cannot vouch for their accuracy | Not independent: this is Epoch own 200B read back out of the literature. Citing both double-counts one source |
| GPT-4o mini | 8 | — | Microsoft MEDEC, arXiv 2412.19260 | 2024-12-26 | Same compilation and disclaimer | Same 8B small-model guess that circulates everywhere; IKP reads 92B total, consistent at about 10x sparsity |
| o1-preview | 300 | — | Microsoft MEDEC, arXiv 2412.19260 | 2024-12-26 | Same compilation and disclaimer | One of only two MEDEC figures not traceable to a prior public estimate; no independent corroboration exists |
| o1-mini | 100 | — | Microsoft MEDEC, arXiv 2412.19260 | 2024-12-26 | Same compilation and disclaimer | Contradicted by Epoch 60-120B total for the mini reasoning line, which is derived rather than compiled |
| o1-mini, o3-mini, o4-mini | 60-120 | 10-30 | Epoch AI model database note | 2024-2026 | Inference economics at 150-200 tok/s and $4.40/Mtok output | The only active-parameter figure Epoch states for any closed OpenAI model. Corroborated by measured throughput (o3-mini 209 tok/s, o4-mini high 136) and by IKP 62B total for o3-mini |
| GPT-4.5 | 6000 | 600 | Nathan Lambert, Interconnects | 2025-02-28 | 5X parameters + 2X dataset size = 10X compute relative to GPT-4; author caveat that this is not based on leaked information and carries big error bars | Consistent with Epoch 3.8e26 training compute inverted at a token-to-parameter ratio of 100, which gives 800B active. Nothing contradicts it |
| GPT-5 | — | 100 | Epoch AI, Notes on GPT-5 training compute | 2025-10-13 | A mid-sized frontier model with about 100B active params, akin to Grok 2 (115B active), GPT-4o, and Claude Sonnet, from price, speed and prevailing industry trends | Corroborated twice: 5e25 FLOP over at least 30T tokens gives 83-167B active through C=6ND, and IKP 1.8T total implies 18x sparsity against OpenAI own disclosed 22.8x for gpt-oss-120b |
| GPT-5 high | — | 635 | cbowdon, Estimating GPT parameter counts | 2025 | Regression of log10(parameters) on family, a reasoning flag and eight benchmark scores, fit to open models; 80 percent of variance; a very rough 0.4x reasoning factor | Contradicted by serving data: it puts GPT-4o at 26B and GPT-5 at 635B while the two are within a factor of two on output speed |
| GPT-5.6 Sol | 3200 | — | Ed Zitron, X | 2026-09-06 | Per a source; no architecture, no activation fraction, no corroborating detail. Date inferred from the search index; x.com is not fetchable | No independent corroboration. Its 1.5x ratio to the Astra figure is consistent with the price and speed step between the two models |
| GPT-5.6 Sol | 5000 | — | @TokenGremlin, X | 2026-08 | Self-described estimate; the explanatory post could not be retrieved | Contradicts Zitron 3.2T by 1.6x. Anonymous, no published method |
| GPT-6 Astra | 4800 | — | Ed Zitron, X | 2026-09-06 | Per a source; significantly bigger model too weight wise. Date inferred from the search index | The only size claim for Astra with any attributed provenance. Post-dates IKP, so no instrument covers it. Epoch lists Parameters Unknown |
| GPT-6 Astra | 8000 | — | @TokenGremlin, X | 2026-08 | Self-described estimate; method not retrievable | Contradicts Zitron 4.8T by 1.7x |
| GPT-6 Astra (Bel pre-train) | 10000 | — | @synthwavedd, X, relayed by note.com and content sites | 2026-08-25 | Unattributed claim that OpenAI completed a pre-trained model called Bel with over 10 trillion parameters | Unfounded. OpenAI has announced neither Bel nor Doug; the most careful secondary account treats it as speculation and notes the figure is meaningless without an activation fraction |
| GPT-6 Astra | — | — | Epoch AI model page and database | 2026-09-13 | Parameters: Unknown. Training compute: Unknown | Absence of any Epoch figure for a model released ten days earlier |
| gpt-oss-120b | 116.83 | 5.13 | OpenAI gpt-oss model card, arXiv 2508.10925 | 2025-08-05 | 36 layers, 128 experts, top-4 routing; routed-expert and attention parameters count towards active, embeddings do not | Exact. Pins OpenAI own 2025 sparsity ratio at 22.8x, which is the anchor every total-to-active conversion in this survey uses |
| gpt-oss-20b | 20.91 | 3.61 | OpenAI gpt-oss model card, arXiv 2508.10925 | 2025-08-05 | 24 layers, top-4 routing | Exact. Sparsity 5.8x |
| GPT-5.5 Pro (think) | 5300 | — | Bojie Li, arXiv 2604.24827 (IKP) | 2026-07-05 | Factual-capacity probing; total, not active | No model-specific corroboration; the instrument's own calibration checks are above |
| GPT-5.5 | 4700 | — | Bojie Li, arXiv 2604.24827 (IKP) | 2026-07-05 | Factual-capacity probing; total, not active | No model-specific corroboration; the instrument's own calibration checks are above |
| GPT-5.4 Pro | 2400 | — | Bojie Li, arXiv 2604.24827 (IKP) | 2026-07-05 | Factual-capacity probing; total, not active | No model-specific corroboration; the instrument's own calibration checks are above |
| GPT-4.1 | 2200 | — | Bojie Li, arXiv 2604.24827 (IKP) | 2026-07-05 | Factual-capacity probing; total, not active | No model-specific corroboration; the instrument's own calibration checks are above |
| GPT-5 Pro | 2100 | — | Bojie Li, arXiv 2604.24827 (IKP) | 2026-07-05 | Factual-capacity probing; total, not active | No model-specific corroboration; the instrument's own calibration checks are above |
| o3 | 2100 | — | Bojie Li, arXiv 2604.24827 (IKP) | 2026-07-05 | Factual-capacity probing; total, not active | No model-specific corroboration; the instrument's own calibration checks are above |
| GPT-5 (think) | 2000 | — | Bojie Li, arXiv 2604.24827 (IKP) | 2026-07-05 | Factual-capacity probing; total, not active | No model-specific corroboration; the instrument's own calibration checks are above |
| GPT-5 | 1800 | — | Bojie Li, arXiv 2604.24827 (IKP) | 2026-07-05 | Factual-capacity probing; total, not active | Implies 18x sparsity against Epoch 100B active, in line with OpenAI own disclosed 22.8x for gpt-oss-120b. The strongest single cross-check in this survey |
| o1 | 1300 | — | Bojie Li, arXiv 2604.24827 (IKP) | 2026-07-05 | Factual-capacity probing; total, not active | No model-specific corroboration; the instrument's own calibration checks are above |
| GPT-5.4 | 1100 | — | Bojie Li, arXiv 2604.24827 (IKP) | 2026-07-05 | Factual-capacity probing; total, not active | No model-specific corroboration; the instrument's own calibration checks are above |
| GPT-5.3 | 1100 | — | Bojie Li, arXiv 2604.24827 (IKP) | 2026-07-05 | Factual-capacity probing; total, not active | No model-specific corroboration; the instrument's own calibration checks are above |
| GPT-4 Turbo | 1050 | — | Bojie Li, arXiv 2604.24827 (IKP) | 2026-07-05 | Factual-capacity probing; total, not active | Ranks above GPT-4, contradicting Epoch maybe smaller/sparser. Cross-era ordering is the instrument weakest regime |
| GPT-5.2 Pro | 639 | — | Bojie Li, arXiv 2604.24827 (IKP) | 2026-07-05 | Factual-capacity probing; total, not active | No model-specific corroboration; the instrument's own calibration checks are above |
| GPT-5.1 | 634 | — | Bojie Li, arXiv 2604.24827 (IKP) | 2026-07-05 | Factual-capacity probing; total, not active | No model-specific corroboration; the instrument's own calibration checks are above |
| GPT-4 | 622 | — | Bojie Li, arXiv 2604.24827 (IKP) | 2026-07-05 | Factual-capacity probing; total, not active | Calibration failure: 622B against the leaked 1.8T total, low by 2.9x. This is the only OpenAI model in the table with an independent total |
| GPT-5.2 | 571 | — | Bojie Li, arXiv 2604.24827 (IKP) | 2026-07-05 | Factual-capacity probing; total, not active | No model-specific corroboration; the instrument's own calibration checks are above |
| GPT-4.1 mini | 501 | — | Bojie Li, arXiv 2604.24827 (IKP) | 2026-07-05 | Factual-capacity probing; total, not active | No model-specific corroboration; the instrument's own calibration checks are above |
| GPT-4o | 392 | — | Bojie Li, arXiv 2604.24827 (IKP) | 2026-07-05 | Factual-capacity probing; total, not active | No model-specific corroboration; the instrument's own calibration checks are above |
| o4-mini (think) | 370 | — | Bojie Li, arXiv 2604.24827 (IKP) | 2026-07-05 | Factual-capacity probing; total, not active | No model-specific corroboration; the instrument's own calibration checks are above |
| GPT-5.4 mini | 339 | — | Bojie Li, arXiv 2604.24827 (IKP) | 2026-07-05 | Factual-capacity probing; total, not active | No model-specific corroboration; the instrument's own calibration checks are above |
| gpt-3.5-turbo | 246 | — | Bojie Li, arXiv 2604.24827 (IKP) | 2026-07-05 | Factual-capacity probing; total, not active | No model-specific corroboration; the instrument's own calibration checks are above |
| gpt-oss-120b (think) | 106 | — | Bojie Li, arXiv 2604.24827 (IKP) | 2026-07-05 | Factual-capacity probing; total, not active | No model-specific corroboration; the instrument's own calibration checks are above |
| GPT-5 mini (think) | 105 | — | Bojie Li, arXiv 2604.24827 (IKP) | 2026-07-05 | Factual-capacity probing; total, not active | No model-specific corroboration; the instrument's own calibration checks are above |
| GPT-5 mini | 93 | — | Bojie Li, arXiv 2604.24827 (IKP) | 2026-07-05 | Factual-capacity probing; total, not active | No model-specific corroboration; the instrument's own calibration checks are above |
| GPT-4o mini | 92 | — | Bojie Li, arXiv 2604.24827 (IKP) | 2026-07-05 | Factual-capacity probing; total, not active | No model-specific corroboration; the instrument's own calibration checks are above |
| GPT-4.1 nano | 71 | — | Bojie Li, arXiv 2604.24827 (IKP) | 2026-07-05 | Factual-capacity probing; total, not active | No model-specific corroboration; the instrument's own calibration checks are above |
| o3-mini | 62 | — | Bojie Li, arXiv 2604.24827 (IKP) | 2026-07-05 | Factual-capacity probing; total, not active | No model-specific corroboration; the instrument's own calibration checks are above |
| GPT-5 nano | 23 | — | Bojie Li, arXiv 2604.24827 (IKP) | 2026-07-05 | Factual-capacity probing; total, not active | No model-specific corroboration; the instrument's own calibration checks are above |
| gpt-oss-20b (think) | 16 | — | Bojie Li, arXiv 2604.24827 (IKP) | 2026-07-05 | Factual-capacity probing; total, not active | No model-specific corroboration; the instrument's own calibration checks are above |
| GPT-5.4 nano | 9.9 | — | Bojie Li, arXiv 2604.24827 (IKP) | 2026-07-05 | Factual-capacity probing; total, not active | No model-specific corroboration; the instrument's own calibration checks are above |

### Anthropic

| Model | Total (B) | Active (B) | Source | Date | Method | Corroboration |
|---|---|---|---|---|---|---|
| Claude 2 | 130 | — | Alan D. Thompson, LifeArchitect The Memo | 2023-07 | No reproducible calculation published | Coincides with training compute inverted at era-appropriate token ratios (118-180B active), which is weak convergence rather than corroboration |
| Claude 3 Sonnet | 70 | — | Alan D. Thompson, LifeArchitect Claude 3 special edition | 2024-03 | No reproducible calculation published | Nothing independent exists for this model |
| Claude 3 Opus | 2000 | — | Alan D. Thompson, LifeArchitect Claude 3 special edition | 2024-03 | No reproducible calculation published | The dataset rejects the chain that turns this into an active count. Training compute at era-appropriate ratios gives 244-370B active, which is not derivable from the 2T |
| Claude 3 Haiku | — | 20 | Alan D. Thompson, LifeArchitect | 2024-03 | No reproducible calculation published | The only cross-check available is Epoch 10-30B active for the o4-mini class |
| Claude 3.5 Sonnet | 400 | — | Epoch AI (Ege Erdil), Frontier language models have become much smaller | 2024-12-13 | Inference economics: served at around 60 tokens per second at $15 per million output tokens, with speed not declining much at 100K context | The 100B active the dataset carries comes from applying Epoch separate quarter-activation convention, not from this post. IKP has no Claude 3.5 Sonnet row |
| Claude 3.5 Sonnet | 175 | — | Microsoft MEDEC, arXiv 2412.19260 | 2024-12-26 | Approximately 175B parameters, no source cited; authors state most numbers of parameters are estimate reported to provide more context | Weight near zero. 175B is GPT-3 parameter count, the commonest placeholder in papers that need a number for a closed model |
| Claude Opus 4 | — | 174-196 | unexcitedneurons, Estimating the size of Claude Opus | 2026-03-12 | OpenRouter decode throughput divided by an effective bandwidth of 4.0-4.5 TB/s calibrated by running the same inversion on three open models of known active size on Vertex, at FP8 | Directionally corroborated by a 3x list-price cut at the 4.1 to 4.5 transition. Confounded by Anthropic own fast mode, which serves fixed weights at 2.5x the per-user rate |
| Claude Opus 4.1 | — | 167-188 | unexcitedneurons | 2026-03-12 | Same method | Same confound |
| Claude Opus 4.5 | — | 100-113 | unexcitedneurons | 2026-03-12 | Same method | Independently reproduced at 90-101B using Artificial Analysis throughput, a 1.11x agreement |
| Claude Opus 4.6 | 1660-3270 | 93-105 | unexcitedneurons | 2026-03-12 | Same method for active; total is the active figure expanded across a range of assumed sparsity ratios. The source explicitly rejects 10T-plus totals for this class | IKP reads Opus 4.6 think at 1.6T total, inside the stated band. Contradicts the LifeArchitect 5T |
| Claude Opus 4.6 | 5000 | — | Alan D. Thompson, LifeArchitect, reported by buttondown The LLM Parameter Lie | 2026-02 | No method published; recorded second-hand because Thompson own pages now gate the figure to institutional clients | Contradicted by the 1.66-3.27T total band from throughput and by IKP 1.6T. The 5T is 1.5-3x above both |
| Claude Mythos 5 | 8000 | — | Financial Times, via Reuters wire | 2026-08-07 | Attributed to industry estimates, not to Anthropic or a named source. Total parameters; no activation fraction given | Internally contradicted: Anthropic states Fable and Mythos share identical model weights, so the two figures cannot both be right |
| Claude Fable 5 | 5000 | — | Financial Times, via Reuters wire | 2026-08-07 | Attributed to industry estimates; total parameters | Corroborated by IKP 3.5T total, which sits inside IKP 3.2x interval and within 1.4x of the FT figure. This is the best-corroborated total for any Anthropic model |
| Claude Opus 5 | 5000 | 500-1000 | aithinkerlab | 2026-08 | Three stated source types: an Elon Musk post the page concedes it cannot locate, an inference from an unverified 10T Mythos architecture, and unattributed forum cost data | Discard. The page also asserts Opus 5 is not an officially announced product, which is false |
| All Claude models | — | — | Epoch AI model database | 2026-09-13 | Parameters field blank on all eighteen Claude rows, from Claude through Opus 5 and Fable 5 / Mythos 5 | Epoch has never published a parameter estimate for any Anthropic model |
| Claude Fable 5 | — | — | Artificial Analysis model page | 2026-09-13 | Anthropic has not disclosed the model size or parameter count | Artificial Analysis publishes throughput and price and no size for any closed model |
| Claude Fable 5 | 3500 | — | Bojie Li, arXiv 2604.24827 (IKP) | 2026-07-05 | Factual-capacity probing; total, not active | Agrees with the FT 5T within 1.4x and inside the 3.2x interval. Two independent routes, which no other Anthropic model has |
| Claude Opus 4.6 (think) | 1600 | — | Bojie Li, arXiv 2604.24827 (IKP) | 2026-07-05 | Factual-capacity probing; total, not active | Read as a lower bound: the paper states that heavily safety-tuned models systematically read smaller than their weights |
| Claude Opus 4.5 | 892 | — | Bojie Li, arXiv 2604.24827 (IKP) | 2026-07-05 | Factual-capacity probing; total, not active | Read as a lower bound: the paper states that heavily safety-tuned models systematically read smaller than their weights |
| Claude Opus 4.1 (think) | 847 | — | Bojie Li, arXiv 2604.24827 (IKP) | 2026-07-05 | Factual-capacity probing; total, not active | Read as a lower bound: the paper states that heavily safety-tuned models systematically read smaller than their weights |
| Claude Sonnet 4.6 (think) | 766 | — | Bojie Li, arXiv 2604.24827 (IKP) | 2026-07-05 | Factual-capacity probing; total, not active | Read as a lower bound: the paper states that heavily safety-tuned models systematically read smaller than their weights |
| Claude Opus 4.7 (think) | 738 | — | Bojie Li, arXiv 2604.24827 (IKP) | 2026-07-05 | Factual-capacity probing; total, not active | Read as a lower bound: the paper states that heavily safety-tuned models systematically read smaller than their weights |
| Claude Sonnet 5 | 584 | — | Bojie Li, arXiv 2604.24827 (IKP) | 2026-07-05 | Factual-capacity probing; total, not active | Read as a lower bound: the paper states that heavily safety-tuned models systematically read smaller than their weights |
| Claude Opus 4.8 | 236 | — | Bojie Li, arXiv 2604.24827 (IKP) | 2026-07-05 | Factual-capacity probing; total, not active | The paper own analysis attributes the 4.6 to 4.7 to 4.8 decline to rising refusal rates rather than to size, so this figure is not usable as a size ordering |
| Claude Opus 5, Claude Fable 5.1, Claude Mythos 5.1 | — | — | Bojie Li, arXiv 2604.24827 (IKP) | 2026-07-05 | No row exists for any of the three. The Anthropic set stops at Fable 5, Opus 4.8 and Sonnet 5 | The only calibrated instrument that covers closed models does not cover the three Anthropic models the dataset most needs |

### Google DeepMind

| Model | Total (B) | Active (B) | Source | Date | Method | Corroboration |
|---|---|---|---|---|---|---|
| Gemini 1.0 Nano-1 | 1.8 | 1.8 | Gemini 1.0 technical report | 2023-12-06 | Stated in the report; dense | Exact. One of only three Gemini sizes Google has ever stated |
| Gemini 1.0 Nano-2 | 3.25 | 3.25 | Gemini 1.0 technical report | 2023-12-06 | Stated in the report; dense | Exact |
| Gemini 1.5 Flash-8B | 8 | 8 | Google for Developers blog | 2024-10-03 | An 8 billion parameter version of the Gemini 1.5 Flash model; the 1.5 report puts it in the single-digit billion class | Exact. Dense, so total equals active |
| Gemini 2.5 Pro | 3000 | — | Bojie Li, arXiv 2604.24827 (IKP) | 2026-07-05 | Factual-capacity probing; total, not active | The only quantitative estimate of any kind for any Gemini Pro model. Not corroborated by anything; serving bounds put active at 70-320B, which is consistent at 10-40x sparsity |
| Gemini 3.1 Pro | 7300 | — | Bojie Li, arXiv 2604.24827 (IKP), Table 16 | 2026-07-05 | Factual-capacity probing; total, not active | Not independent of the landmark construction. The paper says landmark models should be excluded from estimation targets |
| Gemini 3 Pro | 7500 | — | @scaling01 (Lisan al Gaib), X | 2025-11-19 | Benchmark regression restricted post hoc to sparse MoE reasoning models; the author calls it vibe-mathing | The unrestricted fit returned 2.3 quadrillion parameters, and the restriction that fixed it was chosen after seeing the answer. Its agreement with the IKP 7.3T is not corroboration, since both are regressions on capability-correlated scores |
| Gemini 3 Pro | 1000 | 175 | SEO articles citing a Gemini 3 technical brief from Google Research | 2025-2026 | Over 1 trillion total with 15-20 percent active, sourced to a document that does not exist | Discard. The actual Gemini 3 Pro model card repeats the 2.5 report architecture boilerplate and contains no numbers |
| All Gemini models | — | — | Epoch AI model database and model pages | 2026-09-13 | Parameters blank on every Gemini row. epoch.ai/models/gemini-3-pro shows Parameters: Unknown, Training compute: Unknown | Epoch has never published a parameter estimate for any Gemini model |

### xAI

| Model | Total (B) | Active (B) | Source | Date | Method | Corroboration |
|---|---|---|---|---|---|---|
| Grok-1 | 314 | 79 | xAI weight release | 2023-11-04 | Published architecture | Exact |
| Grok-2 | 269.5 | 115.0 | xAI weight release and config.json | 2024-08-13 | 64 layers, hidden 8192, an always-on shared MLP at intermediate 32768 and 8 routed experts at 16384 with top-2 routing; summing the layers reproduces the published totals to 0.11 percent and 0.00 percent | Exact on the number. The identification of these weights with the December grok-2-1212 API revision is the open question, not the arithmetic |
| Grok 3 | 3000 | — | Epoch AI model database | 2025-02-17 | Recorded at Likely confidence with no parameters note | IKP reads 2.1T, inside Epoch band. At the 15-30x sparsity of the 2026 reference class, 3T total implies 100-200B active |
| Grok 4 | 3000 | — | Epoch AI model database | 2025-07-09 | Recorded at Speculative confidence, citing a rumour of 2.4T | Epoch published figure is 1.25x above the rumour it cites; IKP reads 2.0T, closer to the rumour than to Epoch entry |
| Grok 4 | 2400 | — | @kalomaze, X, cited by Epoch | 2025-07 | Unexplained assertion | Bracketed by Epoch 3T and IKP 2.0T |
| Grok 4.20 | 500 | — | Elon Musk on X, recorded by Epoch at Likely | 2026-02-17 | This is just our V8 small foundation model, so 500B params | Corroborated by IKP 689B within 1.4x. This is the closest agreement between a developer statement and an independent instrument anywhere in the survey |
| Grok 4.3, Grok 4.4 | 500 | — | Elon Musk on X, recorded by Epoch at Likely | 2026-04-17 | Supplemental training has been added to 4.3. Grok 4.4 will be twice the size (1T) | Consistent with the 4.20 statement; the 500B V8 foundation appears in three separate Musk statements |
| Grok 4.5 | 1500 | — | Elon Musk on X, recorded by Epoch at Likely | 2026-07-08 | Stated on X that Grok 4.5 would have 1.5 trillion parameters, presumably total | Consistent with the V9 foundation described as about 3x larger than v8-small. No independent check; IKP has no Grok 4.5 row |
| Grok-3 | 2100 | — | Bojie Li, arXiv 2604.24827 (IKP) | 2026-07-05 | Factual-capacity probing; total, not active | Grok-4.20 agrees with Musk 500B within 1.4x; Grok-3 and Grok-4 sit 1.4-1.5x below Epoch 3T, inside both error bars |
| Grok-4 | 2000 | — | Bojie Li, arXiv 2604.24827 (IKP) | 2026-07-05 | Factual-capacity probing; total, not active | Grok-4.20 agrees with Musk 500B within 1.4x; Grok-3 and Grok-4 sit 1.4-1.5x below Epoch 3T, inside both error bars |
| Grok-4.20 | 689 | — | Bojie Li, arXiv 2604.24827 (IKP) | 2026-07-05 | Factual-capacity probing; total, not active | Grok-4.20 agrees with Musk 500B within 1.4x; Grok-3 and Grok-4 sit 1.4-1.5x below Epoch 3T, inside both error bars |

### Moonshot

| Model | Total (B) | Active (B) | Source | Date | Method | Corroboration |
|---|---|---|---|---|---|---|
| Kimi K3 | 2800 | 104 | Epoch AI model database | 2026-07-16 | Recorded at Speculative confidence; 104 billion active parameters | The largest active count in the 2026 open reference class, and the anchor the dataset 100B frontier prior leans on |

### Alibaba

| Model | Total (B) | Active (B) | Source | Date | Method | Corroboration |
|---|---|---|---|---|---|---|
| Qwen3.8-Max | 2400 | 95 | Epoch AI model database | 2026-07-19 | Recorded at Confident; 2.4T total, 95B active | Second-largest disclosed 2026 active count |

### Z.ai

| Model | Total (B) | Active (B) | Source | Date | Method | Corroboration |
|---|---|---|---|---|---|---|
| GLM-5.2 | 744 | 40 | Epoch AI model database | 2026-06-16 | Recorded at Confident; 40 billion active | IKP reads 1.0T total against a known 744B, high by 1.4x, which is well inside its interval |

## Where estimates disagree, and which has the better basis

**GPT-4: SemiAnalysis 1.8T total / 280B active against IKP 622B total.** SemiAnalysis wins, decisively. Its
figures close against an independently estimated quantity: 6 x 2.8e11 x 1.3e13 = 2.2e25 FLOP against Epoch's
2.1e25 training-compute estimate, which was derived without reference to the leak. IKP's miss here is the
best available evidence about how far IKP can be trusted on models older than its calibration set.

**GPT-4o: Epoch 200B total against IKP 392B total.** Epoch wins for the purpose at hand, because its route
constrains memory traffic per token directly and the dataset stores active. The two are not really in
conflict: a 392B-total model at 2024-era sparsity of about 8x has roughly 50B active, which is Epoch's
central reading of its own 200B figure. The trap is Epoch's energy article, which computes 100B active as
an explicitly "pessimistic" case on the 400B tail; that number gets quoted as though it were the central.

**gpt-3.5-turbo: Finlayson 7B against CODEFUSION 20B against IKP 246B total.** The measurement that
survives all three is d_model = 4096, recovered from the rank of API logits. The 7B is an inference
conditional on the model being dense, and the authors say so. An MoE with d_model = 4096, 10-25B active,
and a couple of hundred billion total satisfies all three at once. Carlini et al. recovered the same
model's hidden dimension exactly and did not publish the value, at OpenAI's request, so the strongest
measurement anyone has made of this model is in someone's drawer.

**Claude Fable 5: FT 5T total against IKP 3.5T total.** They agree, and this is the only Anthropic model
where two independent routes land within 1.4x of each other. IKP has the better method: it has a
published calibration and a cross-validated interval, where the FT figure is unattributed "industry
estimates". But IKP reads safety-tuned models low by its own analysis, which pushes the truth up toward
the FT figure rather than down. I would take 3.5-5T total for the Fable/Mythos class and treat that as the
best-supported total-parameter statement about any Anthropic model, ever.

**Claude Opus 4.6: unexcitedneurons 1.66-3.27T total against LifeArchitect 5T against IKP 1.6T.** The two
quantitative routes agree at 1.6-3.3T and the 5T sits above both. LifeArchitect publishes no method, and
the figure reaches us second-hand through a newsletter because Thompson's own pages now gate the number to
institutional clients. Take 1.6-3.3T.

**Claude Opus 4.8: IKP 236B total against everything else.** Reject the IKP number as a size statement. The
paper's own Section 6.6 attributes the Opus 4.6 → 4.7 → 4.8 accuracy decline to rising refusal rates and
says "within-family ordering near the frontier tracks refusal policy as much as capacity". Reading 236B as
a size would make Opus 4.8 an eighth the size of Opus 4.6, which nothing else supports.

**Grok 4.20: Musk 500B total against IKP 689B total.** They agree within 1.4x, which is the closest
agreement between a developer statement and an independent instrument anywhere in this survey. Musk's
statement has the better basis because it is the developer describing his own model, and the same 500B V8
foundation appears in three separate statements across five months. It is also the one case where a
black-box instrument has been checked against a closed-model figure from the lab and passed.

**Grok 3 and Grok 4: Epoch 3T total against IKP 2.0-2.1T against the kalomaze rumor of 2.4T.** All three sit
inside each other's error bars, and the rumor is in the middle. Epoch's own Grok 4 note cites the 2.4T
rumor and then records 3e12, so Epoch's published figure is 1.25x above the only evidence it names. I would
use 2.4T and note that Epoch's Grok 3 row, at Likely rather than Speculative, is doing the real work.

**GPT-6 Astra: Zitron 4.8T against TokenGremlin 8T against the synthwavedd 10T.** Zitron's has the better
basis, and the bar is low. It is the only one attributed to a source rather than presented as an estimate,
it comes from a named journalist with a record of internal-numbers reporting on OpenAI, and it is paired
with a Sol figure that makes the generational step 1.5x, which the price and speed ladder supports. The 8T
is an anonymous account's estimate with an unretrievable method. The 10T traces to an August 2026 X post
about a "Bel" pre-train that OpenAI has never acknowledged, and the content sites that repeat it offer no
attribution at all. None of the three is checkable.

**Gemini 3 Pro: IKP 7.3T against scaling01's 7.5T.** Their agreement is a coincidence, not corroboration.
Both are regressions on capability-correlated scores, so they share the confound that makes benchmark-based
size estimation fail, and IKP's author excludes the model from estimation on top of that. Neither should be
used.

## What nobody has estimated at all

This is the part of the survey that matters most for the dataset, because it is where the registry's numbers
have no external referent whatsoever.

- **Active parameters for any Anthropic model, from anyone, ever.** The only quantitative route that has
  been run is unexcitedneurons' throughput inversion, published 2026-03-12, and it covers Opus 4, 4.1, 4.5,
  4.6, Sonnet 4.5, and Sonnet 4.6. Opus 4.7, Opus 4.8, Opus 5, Fable 5, and Fable 5.1 have no published
  active-parameter estimate from any source. Epoch's field is blank on all eighteen Claude rows. Artificial
  Analysis states outright that "Anthropic has not disclosed the model size or parameter count".
- **Active parameters for any Gemini model above Flash-8B.** Google has disclosed Nano-1, Nano-2, and
  Flash-8B, and nothing else in four years and four generations. No analyst has published an active-parameter
  estimate for any Gemini Pro model.
- **Anything at all for Claude Opus 5, Claude Fable 5.1, and Claude Mythos 5.1.** They post-date IKP's
  evaluation window, Epoch lists them Unknown, and no leak or analyst post names a figure. The only thing in
  circulation is aithinkerlab's "5T total, 500B-1T active", which rests on a Musk post the page admits it
  cannot find.
- **Anything at all for GPT-5.6 Sol or GPT-6 Astra other than Zitron's totals.** No active figure, no
  architecture, no expert count, no layer count. Epoch lists both Unknown. IKP predates both.
- **Any loop count for Astra.** The Information reported recurrent depth from a single anonymous source;
  OpenAI has not confirmed it. Jakub Pachocki's remark that Astra's computation-graph depth is "within a
  factor of two of GPT-4" is the only near-official statement, and when Transformer asked for more, OpenAI
  pointed back at the tweet.
- **Any regulatory disclosure, anywhere.** The EU AI Act's GPAI regime turns on training compute (10^25
  FLOP), not on parameters, and its Annex XI documentation runs to the AI Office rather than to the public.
  US export-control thresholds are compute thresholds. The Frontier Model Forum publishes safety frameworks,
  not architectures. The one academic audit of frontier model documentation against Annex IV
  (arXiv 2512.12443, covering Gemini 3, Grok 4.1, Llama 4, GPT-5, and Claude 4.5) does not include parameter
  count among its scored subsections at all, which tells you how uniformly absent the disclosure is.

One trend worth recording: **the public estimate supply is shrinking, not growing.** Epoch populated
`Parameters` for GPT-4 in 2023 and has published nothing for any OpenAI model since GPT-4o. LifeArchitect
published round numbers for Claude and GPT models through 2024 and now gates them to institutional clients.
Artificial Analysis, which has the best throughput and price data in the field and is the input to
everyone else's estimates, has never published a size. The only direction the supply has grown is xAI, and
only because Musk posts.

## Corrections and gaps in the three existing reports

**`anthropic.md` and `google-xai-others.md` do not cite arXiv 2604.24827 at all.** This is the substantive
gap. `openai.md` treats the IKP paper as the single most important new instrument in the field and builds
several of its proposals on it; the other two reports were written within ten minutes of it and do not
mention it. The paper carries 25 Claude rows, 11 Gemini rows, and 5 Grok rows. Concretely, this costs:

- The Fable 5 corroboration. `anthropic.md` concludes that the FT's 8T/5T pair "cannot both be right" and
  that only "the multi-trillion order of magnitude for the class" survives. IKP independently reads Fable 5
  at 3.5T, which is inside its own 3.2x interval and within 1.4x of the FT's 5T. That is stronger than the
  report's conclusion allows and it favors the Fable half of the FT pair over the Mythos half.
- An independent check on Opus 4.5, 4.6, 4.7, and 4.8, and on Sonnet 4.6 and Sonnet 5, with the caveat that
  the paper's own analysis says the Claude ordering tracks refusal policy.
- The only quantitative estimate that exists for any Gemini Pro model (2.5 Pro at 3.0T total), and the
  reason the Gemini 3.x figure circulating at ~7.3-7.5T should be discarded rather than merely doubted.
- Corroboration of Musk's Grok 4.20 500B at 689B, and of the kalomaze 2.4T rumor for Grok 4 at 2.0T.

**`openai.md` misses Carlini et al., arXiv 2403.06634.** Its list of academic black-box work names only the
softmax-bottleneck hidden-size measurement and IKP. Carlini et al. (ICML 2024) is the stronger of the two
hidden-size papers: it recovers the full embedding projection layer, confirms ada at h=1024 and babbage at
h=2048, and recovers gpt-3.5-turbo's hidden dimension exactly, publishing everything except that last value
at OpenAI's request. It does not produce a parameter count, so it changes no proposal, but it belongs in the
methods section because it establishes that the measurement is cheap (under $2,000 for gpt-3.5-turbo) and
that the reason we do not have the number is a lab's request rather than a technical limit.

**`openai.md`'s IKP extract repeats an error in the paper.** The paper's full results table lists both
gpt-oss models with `Arch = dense`. They are disclosed mixture-of-experts. The calibration check the report
draws from them—IKP's 106B against a 116.83B total—is still the right comparison and still supports the
report's reading that IKP estimates total. But the misclassification also means the paper has the two
models it uses as OpenAI ground truth assigned to the wrong calibration subsets in its own Table 17, so the
dense (n=52) and MoE (n=41) sub-fits it reports are both slightly wrong.

**`openai.md`'s Astra section is superseded on one point.** It states there is "no disclosure, no leak of a
size, and no academic estimate" for Astra. Ed Zitron posted a sourced 4.8T total around 2026-09-06, a week
before the report was written. This does not change the report's proposal, which is about active parameters
and rests on the serving ladder, and 4.8T total against a 200B active proposal implies 24x sparsity, which
is close to OpenAI's disclosed 22.8x for gpt-oss-120b. So the leak, if real, supports the report's number
rather than displacing it. That is worth adding to the record.

**`anthropic.md` understates LifeArchitect's coverage.** It records Thompson's Claude estimates as stopping
at March 2024. He had a February 2026 figure of ~5T total for Claude Opus 4.6, which reaches the public
record only second-hand. The reason the report did not find it is that Thompson now gates his parameter
column to institutional clients, which is itself worth a line in the report's "what would settle this"
section.

**Nothing else in the three reports looks wrong to me.** `google-xai-others.md`'s refusal to use the SEO
claims about Gemini 3 Pro is correct and I reproduced the same search result. `openai.md`'s reading of the
MEDEC paper as a literature compilation rather than a leak is correct and important. `anthropic.md`'s
2.5x error bar on route T, derived from Anthropic's own fast mode, is the most useful methodological point
in the three reports and is not made anywhere in the published literature.

## Sources

Primary sources for each row are in the `source` column of `estimate-survey.csv`. Retained extracts with
provenance and retrieval notes:

- `agent-work/sources/model-priors/survey/ikp-non-openai-rows.md` — the Anthropic, Google, xAI, and other
  non-OpenAI rows of arXiv 2604.24827, extracted from the v2 HTML by direct download and table parsing.
- `agent-work/sources/model-priors/survey/leaks-and-analyst-claims-2026.md` — Zitron, TokenGremlin, synthwavedd,
  scaling01, LifeArchitect, aithinkerlab, kalomaze.
- `agent-work/sources/model-priors/survey/non-disclosure-statements.md` — every located explicit statement that a
  count is unknown.
- `agent-work/sources/model-priors/openai/`, `../anthropic/`, `../google-xai-others/` — the extracts retained by
  the three earlier reports, not duplicated here.

Key URLs not already carried by the earlier reports: https://arxiv.org/abs/2604.24827 (IKP, v2 2026-07-05);
https://arxiv.org/abs/2403.06634 (Carlini et al., ICML 2024); https://arxiv.org/abs/2512.12443 (AI
Transparency Atlas); https://epoch.ai/models/gpt-6-astra, https://epoch.ai/models/gemini-3-pro,
https://epoch.ai/models/claude-fable-5 (all "Unknown"); https://artificialanalysis.ai/models/claude-fable-5;
https://lifearchitect.ai/gpt-6/; https://x.com/edzitron/status/2096961600825462850;
https://x.com/scaling01/status/1990967279282987068;
https://buttondown.com/dodatathings/archive/the-llm-parameter-lie-what-actually-matters-in/;
https://unrote.com/ai/how-big-is-chatgpt/.

Retrieval limitation to note: x.com returns HTTP 402 to the fetch tool, so the four X posts in this survey
are recorded from search-index text and their dates are as reported by the index. Zitron's date in
particular is inferred and should be treated as approximate.
