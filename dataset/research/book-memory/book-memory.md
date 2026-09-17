# Book-name cloze

## memo-book-name-cloze-gpt4

One missing character name in a short English-fiction passage, averaged over 9,057 released GPT-4 responses from 91 pre-1923 LitBank books. No title, author or external lookup is supplied. This is name recall from prior exposure, not verbatim recitation or learning to memorize a book.

The original [Chang et al. 2023 paper](https://aclanthology.org/2023.emnlp-main.453.pdf),§3–5, specifies 40–60 BookNLP-token passages, two prompt examples and 100 samples/book. It reports 24.4% GPT-4 accuracy for pre-1923LitBank. One author attempted the same task without external sources and scored 0%; the attempt count and timing are not given. The paper's human result covers an unspecified portion of the wider collection, not a measured typical-adult score on these 91 books.

[Original code and responses](https://github.com/bamman-group/gpt4-books/tree/ef7b1a6c2c0810527a21024a01138ff7f323f11f) are retained at that commit. The 91 files with Gutenberg-number names define the public-domain cohort. Ninety contain 100 responses; Sons and Lovers contains 57. All 91 downloaded bytes match the original Git blob identities. We use the 9,057 available responses, not invent 43 missing calls. Case-sensitive matching gives 2,190/9,057 = 24.1802%; case-insensitive matching gives 2,214/9,057 = 24.4452%, consistent with the paper's rounded 24.4%. The former and latter are both retained; normalization is explicit rather than silently repairing punctuation.

### Human duration and comparison

Baseline: a typical fluent-English adult reading an unidentified passage, trying to retrieve a name and entering a guess, without lookup. Estimated mean effort is 24.31 seconds: 9.31 seconds reading plus 12 seconds trying to retrieve/guess plus 3 seconds entering the name. The latter two components are judgments, not measured cloze response times. The full duration is `assumed` and `estimated`.

The [Brysbaert 2019 original meta-analysis](https://doi.org/10.1016/j.jml.2019.104047) reports 260 words/minute for adult silent fiction reading. A retained [copy of the article](https://gwern.net/doc/psychology/linguistics/2019-brysbaert.pdf) supplies that reading-rate anchor. The source passages average 40.335 whitespace-separated words, giving 40.335 × 60/260 = 9.308 seconds. General continuous reading is a transfer to this short retrieval task; the additional effort is separately allowed.

Ten passages selected by SHA-256(filename plus zero-based index), rather than accuracy, were inspected. They include ambiguous family conversations, a diagnosis anecdote, a hunting scene and recognizable Emma/Tarzan passages. Most offer no dependable name clue; a brief recall attempt followed by a guess is a more realistic task than lengthy deductive research. Twelve seconds permits rereading a clause and trying a familiar name. This is not a time limit or measured optimal stopping rule. A quick 320 wpm reader plus 5 seconds response effort gives 12.56 seconds; a deliberate 180 wpm reader plus 35 seconds gives 48.44 seconds. These are scenarios, not confidence bounds.

The best supported classification is `above`: GPT-4 achieves 24.45%, while the original human 0% and 0.6% common-name baseline support low unaided accuracy. This transfers a single author's result to typical readers and from an unspecified wider sample to this cohort. It does not assert every ordinary reader scores 0%, or that a literary specialist cannot outperform GPT-4. `different_human_baseline` and `different_assessment` expose those transfers. Human time does not target AI-matched accuracy, so match by construction would be wrong. Prior book familiarity is not controlled for either side; no external-tool difference is invented.

### Compute

The original two-example user prompt is extracted as a literal from the released script without executing its API call. Each actual passage and actual XML-wrapped output is tokenized with retained cl100k_base. All outputs are present; no reasoning multiplier is added. Per-response mean input is 193.7603 including 8 assumed chat-wrapper positions; mean output 7.76957. All input is treated as fresh because native cache counters are absent. This is a reconstructed workload, not a native token-usage measurement.

The registered original unspecified GPT-4 coefficient is 550 billion FLOPs/token, from the shared 275 billion active-parameter assumption. It is a model prior, not an architecture disclosure. Total 201.52987 tokens × 550 billion = 1.10841426520923e14 FLOPs per question. Native historical alias revisions are unavailable, so the existing unspecified-original identity is used. No helpers or sampling retries appear in the retained one-response-per-passage data; costs refer to those released responses and do not claim to recover unlogged unsuccessful calls. Context-dependent attention is omitted by the parameter-token approximation and added back in `compute_flops` (`research/attention-correction.md`).

Wrapper 4–16 positions changes compute to 1.0864e14–1.1524e14 F; 100B–550B active-parameter scenarios give 4.0306e13–2.2168e14 F. Model size dominates wrapper uncertainty. The benchmark-normalized analytic estimate uses ai_attempts=not_applicable; 9,057 questions remain in research, not a fabricated independent-run count. Human attempts are not_applicable because the duration has no recorded attempt sample.

### Reproduction

Python 3 with `tiktoken`. Run `recompute.py --sources /absolute/path/to/sources --output /absolute/path/to/new.json`. Retained source hashes and Git blob identities are checked. The output must be new and outside sources. `calculations.json` contains every count, both accuracy definitions, and scenarios. `selected-files.json` lists the original repository paths; `inspected-passages.json` records the deterministic inspection sample. Manifest hashes identify retained source bytes; original URLs and repository revision are specified above. No remote API or model inference is used.
