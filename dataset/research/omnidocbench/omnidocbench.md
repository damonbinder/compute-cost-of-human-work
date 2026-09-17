# English document pages converted to Markdown

## perc-ocr-gpt4o-omnidocbench-en

One page drawn uniformly from the **290 English pages in OmniDocBench v1.0**, converted from its image into Markdown text, LaTeX equations and HTML tables. The output preserves headings, paragraphs, lists and reading order; it includes captions and visible page furniture but does not redraw figures or reproduce page typography. The AI setting is the paper's **GPT-4o-2024-08-06**. The human is a document transcriber comfortable with scientific notation, LaTeX and a table editor, using the same page image and ordinary editing tools without OCR or other AI assistance.

The central estimates are **2.9610 × 10¹⁴ FLOPs** and **1,500 person-seconds (25 minutes)** per page. Compute averages a reconstruction over all 290 pages. Human time averages a component recipe over the same pages, then rounds to a minute. Neither number is a mean of observed task-run timings or native model counters.

### Which source records

The original [dataset v1.0](https://huggingface.co/datasets/opendatalab/OmniDocBench/tree/f5f559bddf50e36f7f9899d842d0006f13ce8afc) has 981 pages: 290 labelled `english`, 612 `simplified_chinese` and 79 `en_ch_mixed`. The language field alone selects the point. The complete original annotation JSON is retained, including page dimensions, text, tables, equations and original page identifiers. Later 1,355/1,651-page versions are not mixed into this observation.

For visual inspection, sort the English filenames by SHA256 of `omnidocbench-gpt4o-pilot-2026-09-12|` followed by the filename and take the first ten. `selection.json` records this rule and the images. Selection preceded inspection and uses neither model scores nor output availability. All ten source images have dimensions matching their annotations. The ten inform the human workflow; the numerical workload uses all 290 pages, not just those ten.

The [CVPR paper](https://openaccess.thecvf.com/content/CVPR2025/papers/Ouyang_OmniDocBench_Benchmarking_Diverse_PDF_Document_Parsing_with_Comprehensive_Annotations_CVPR_2025_paper.pdf), Figure 1, names the August snapshot. Table 2 reports the English evaluation. The original `metrics/show_result.py` reads the EN column from `language: english`, confirming the same page-level language subset rather than all English text spans on mixed-language pages. The [supplement](https://openaccess.thecvf.com/content/CVPR2025/supplemental/Ouyang_OmniDocBench_Benchmarking_Diverse_CVPR_2025_supplemental.pdf), Section IV, says GPT-4o used default settings.

No attributable, complete set of original GPT-4o prediction files or usage counters was found in the public v1 repository, releases or dataset. Demo Markdown files do not identify their producing model. They are not treated as GPT-4o outputs. This is a reconstruction of the published setting, not a newly run model experiment.

### Output and prompt reconstruction

The retained [author inference script](https://github.com/opendatalab/OmniDocBench/blob/337cc26965893db3ef53ddc119a6d6bb5bde096f/tools/model_infer/gpt_4o_inf.py) supplies one page image and one text instruction to one GPT-4o call. It requests Markdown, LaTeX and HTML, explicitly ignores figures, and discards usage counters. No separate OCR/helper model appears in that inference path. The repository revision is later reference code: its default directories refer to masked-table images and its API model string is an unsnapshotted `gpt-4o`. Consequently, the paper establishes the full-page setting and model revision; this code supplies an approximate prompt/call template, not authenticated native request provenance.

For each original page, `recompute.py` joins annotated text blocks, HTML tables and display LaTeX with blank lines, adds Markdown heading markers, and counts the resulting text with the original `o200k_base` vocabulary. Headers and footers are retained because the prompt requests all text and the supplement shows GPT-4o retaining them. Figure regions and boxes with no annotated transcription are excluded from this length proxy. Inline spans are not added again: their content is already in the parent text. The script keeps the annotation's actual LaTeX strings rather than silently repairing them. It does not assert that all annotation strings are flawless.

This gives **1,171.255 output tokens/page**. The literal Python prompt has 301 tokens, plus an assumed 12 message/special positions, for **1,484.255 text tokens/page**. A single `\frac` escape in the original non-raw Python string becomes a form-feed character; the count follows the evaluated source literal and records this fact. Its small effect does not establish which historical prompt bytes were used.

Ground-truth output length is an estimate of generation length. Real GPT-4o can omit content, choose different markup, add material, or fail altogether. The sample is not selected for successful parsing. Output lengths at 75% and 150% of the proxy give compute of **2.6682 × 10¹⁴** and **3.5467 × 10¹⁴** FLOPs with other assumptions fixed. Empty files and missing retry work cannot be recovered without the native calls; no measured zero is asserted for either. The central setting assumes one completed generation per page. The code does not show model-based evaluation or helper calls inside that task.

### Visual and language arithmetic

The shared GPT-4o prior is **50 billion active parameters**, hence **10¹¹ FLOPs per processed backbone position**. [Epoch's size discussion](https://epoch.ai/gradient-updates/how-much-energy-does-chatgpt-use) gives a central 200B total-parameter estimate and discusses one-quarter activation; this dataset combines those assumptions. It does not copy the source's pessimistic 400B-total/100B-active energy case. None is a disclosed GPT-4o architecture. The [August 6 release announcement](https://openai.com/index/introducing-structured-outputs-in-the-api/) independently identifies the model snapshot. The existing shared model row is reused unchanged.

Separate three quantities:

1. **Crop geometry:** the original dimensions are scaled to fit 2,048 pixels on the longest side and 768 on the shortest side, then covered by 512-pixel tiles plus an overview. The [official image guide](https://developers.openai.com/api/docs/guides/images-vision) describes these GPT-4o high-detail rules. This retained guide is current documentation of the older model, not a native log of its 2024 preprocessing. The historical request omits `detail`; high detail is assumed for these dense full-page images. This gives **5.5586 crops/page** including the overview.
2. **Physical visual positions:** each crop is assumed to use a ViT-bigG-14-like encoder at 224 pixels, generating 256 patch representations passed to the backbone, or **1,423.0069 visual positions/page**. This is an architectural proxy. Neither GPT-4o's actual encoder nor its compression of patches into backbone positions is public. The billable 85-plus-170-per-tile rule would give 859.9655 billing units/page; it does not establish physical operations and is not used as the backbone count.
3. **Vision encoder:** the original [OpenCLIP configuration](https://github.com/mlfoundations/open_clip/blob/c62bf7d0eba36b38909be25528a7412fc20a35f7/src/open_clip/model_configs/ViT-bigG-14.json) has 48 layers, width 1,664, MLP width 8,192, 14-pixel patches and 257 positions including the class token. It is a proxy for GPT-4o, consistent with the existing rounded 2B visual-encoder assumption, not a claim that GPT-4o runs OpenCLIP.

For one crop, with n=257, d=1,664, m=8,192 and L=48, the encoder matrix arithmetic is:

`2 × 256 × (14² × 3) × d + L × (8nd² + 4ndm + 4n²d)`

This counts patch embedding, Q/K/V/output projections, MLP projections and both attention matrix products at two operations per multiply-add. It gives **967,491,772,416 FLOPs/crop**, or **5.3779 × 10¹² FLOPs/page**. The class token is processed by the encoder but is not assumed to add a backbone patch position. The unused contrastive text tower and pooled contrastive head are not part of this patch-feature proxy. Biases, normalization, activation functions and an undisclosed multimodal projector are not separately recovered. Doubling the entire counted frontend would raise the point by only 1.82%; a materially different visual representation is assessed separately below.

Total:

`10¹¹ × (1,484.2552 text positions + 1,423.0069 visual positions) + 5.3779 × 10¹² = 2.9610 × 10¹⁴ FLOPs/page`.

The text-token CSV field contains **only text positions**. Context-dependent language-model attention is omitted by the shared 2P approximation and added back in `compute_flops` (`research/attention-correction.md`). Every page is a single independent call with the image placed before its text instruction. A shared prompt therefore does not demonstrate a reusable prefix across different images. Missing cache counters are treated as a full-input assumption, not observed zero cache reads. Even hypothetical reuse of the entire 313-position text prompt would lower compute by 10.6%; there is no evidence to subtract it centrally.

One-at-a-time sensitivities, not confidence bounds:

| Changed assumption | FLOPs/page |
|---|---:|
| 25B / 100B active backbone parameters | 1.5074 × 10¹⁴ / 5.8683 × 10¹⁴ |
| Pool each crop to 64 backbone positions | 1.8938 × 10¹⁴ |
| 336-pixel proxy encoder, 576 patch positions/crop | 4.8100 × 10¹⁴ |
| Overview only | 1.7499 × 10¹⁴ |

These separate the documented crop geometry from undocumented encoder size, resolution and patch compression. Low-detail processing may also change parsing quality; its arithmetic is not a second performance observation.

### Human work

The target is checked manual page conversion, not editing an AI draft. Text and numbers must be correct, tables must preserve cells and merges, equations must render correctly, and the sequence must be readable. An ordinary table editor can generate HTML; the human does not type every HTML tag. Editor shortcuts and copying repeated formatting are allowed. No plotting, recreation of photographs, mathematical problem solving or interpretation of scientific claims is included.

[Dhakal et al., CHI 2018](https://userinterfaces.aalto.fi/136Mkeystrokes/resources/chi-18-analysis.pdf), Table 1 and “Typing Speed,” report **51.56 standard five-character WPM**, SD 20.20, in a large self-selected transcription sample. The measured uncorrected character error rate is 1.167%. Participants first read the sentence; timing is first-to-last keypress and already includes editing while typing. This transfers a baseline for ordinary text entry, not a measured professional document-parsing rate or final checked accuracy. Applying an inverse mean speed does not recover the population's mean completion time. Accordingly, the human statistic is a point estimate, with 2,534,400 contributing sentence-transcription attempts (168,960 included participants × 15), subset all. The source excludes incomplete sessions, participant error rates above 25%, technical faults and long interruptions; the included sentence trials still contain errors. This is the timing donor count, not 2,534,400 observed page conversions.

The all-page workload averages 3,064.68 non-math text characters, 226.68 table-content characters, 32.75 table cells, 0.438 tables and 201.02 LaTeX characters across 8.51 formulas or inline math fragments. Formula delimiters are removed for human character workload; HTML tags are excluded from table typing. The recipe uses these original quantities:

| Component | Assumption | Mean seconds/page |
|---|---|---:|
| Plain text entry | 51.56 five-character WPM | 713.3 |
| Compare plain text against image | 12.5 characters/second | 245.2 |
| Table content entry and navigation | Same text-entry rate + 2 seconds/cell | 118.3 |
| Check table cells | 2 seconds/cell | 65.5 |
| Set up table shape/merges/export | 60 seconds/table | 26.3 |
| Enter equations | 1.5 LaTeX characters/second + 5 seconds/formula | 176.6 |
| Check equation rendering | 25% of character-entry time + 4 seconds/formula | 67.6 |
| Initial view and document structure | 30 seconds/page + 2 seconds/output block | 62.3 |
| Total before rounding | | **1,474.9** |

Only the baseline typing rate is measured. Checking, table navigation, equation entry and formatting allowances are estimates grounded in the inspected pages. They are additive activities; checking is not included twice in the measured typing rate, which covers corrections made during entry but not a later page-to-output comparison. The final rounded point is **1,500 seconds**.

The table-heavy sample pages require entering 249 and 305 cells, including group headings and significance markers; their estimates are 34.6 and 30.1 minutes. The proof page requires 1,951 LaTeX characters in 22 display/inline fragments, giving 35.8 minutes without solving the proofs. The dense reference page contains 11,133 text characters and 62 blocks, giving 60.6 minutes. In contrast, the illustrated consumer infographic requires only 4.7 minutes and a chapter contents page 6.9 minutes. `inspection.md` records all ten observations. These differences are why the recipe uses actual content rather than one fixed duration for any page.

A faster workflow (78 WPM, faster checking/formatting, 3 LaTeX characters/second) gives **889 seconds/page**; a slower one (26 WPM, slower checking/formatting, 0.75 LaTeX characters/second) gives **2,890 seconds/page**. The approximate upper/lower-decile typing speeds calibrate these scenarios, but the full scenarios are assumptions about skill and workflow, not empirical quantiles or confidence limits. Specialized transcribers may type faster than the original self-selected cohort while spending more time checking formulas and dense tables.

### Quality

The original paper's **Table 2**, English GPT4o row, gives text normalized edit distance **0.144**, formula edit distance **0.425**, formula CDM **72.8**, table TEDS **72.0**, table edit distance **0.234**, reading-order edit distance **0.128**, and overall edit score **0.233**. These are collection-level measures for the source-defined English set, not an accuracy obtained by subtracting a score from 100%. The 72.8 figure is formula CDM, not table TEDS.

The classification is **below** checked expert transcription. It is an estimate: an expert who enters and checks the contents is expected to make substantially fewer text, structure and equation errors than these aggregate results. There is no measured unaided expert cohort or claim of perfect human transcription. The original GT was produced using model-assisted preannotation and human corrections; its annotation process cannot establish our unaided human time or accuracy. During inspection, the PCB table also showed a likely incorrect chemical group heading in the GT, so annotations are treated as a workload and scoring reference rather than infallible truth.

Published output examples help interpret the errors without being used to select the workload. Supplement Figure S3 shows an English GPT-4o output retaining headers and page information. Figure S14 shows GPT-4o turning a Chinese recipe's ingredient prose into an HTML table and inserting image placeholders; this is a structure error, not merely a different line break. That Chinese example illustrates the kind of output failure, not the English score. Some page furniture is ignored by the benchmark; both work estimates include its transcription, while the performance classification concerns the scored core text/table/formula/reading-order output. Exact preservation of visual typography is not the target.

### Reproduction

Use Python 3 with `tiktoken` and `Pillow` installed. From the published dataset root:

```sh
python3 research/omnidocbench/recompute.py agent-work/sources/omnidocbench /path/to/new-omnidoc-output
```

The output directory must not exist and must be outside the source directory. The script loads the retained tokenizer locally, writes the 290 output-length proxies and all per-page quantities, and produces `calculations.json`. It does not download data, call a model, overwrite source files or edit CSVs. For this candidate, use `research/recompute.py sources /path/to/new-output` from the batch directory. Source hashes and exact publication paths are recorded in `agent-work/sources/omnidocbench/manifest.json`.
