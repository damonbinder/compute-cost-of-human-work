# Essay scoring

## Work and performance

The point is one Prompt 2 holistic score, not comments on the essay. [R2BERT](https://aclanthology.org/2020.findings-emnlp.141.pdf), Tables 1–2, reports approximately 350 words per essay and 0.719 quadratic weighted kappa for this prompt. Evaluation uses five train/validation/test folds. This is agreement with reference scores, not 71.9% accuracy. The human estimate explicitly targets comparable agreement; no measured human parity result is claimed.

The [ASAP++ prompt reproduction](https://lwsam.github.io/ASAP++/Prompt-2-Guidelines.pdf) identifies the library-censorship persuasive task. Its expanded trait guidelines help inspect the work but are not the model's target: this point requires one scalar score, not five trait scores. No actual essay collection was obtained for this reconstruction; length uses the paper's summary rather than invented individual essays.

## Compute

The paper specifies BERT-Base with a linear scoring head. Its 512-word wording is imprecise: BERT's limit applies to model-token positions. Exact tokenization, padding and inference sequence lengths are unavailable. Use a full 512-position pass as the central workload, including padding and special tokens. This is an assumed implementation workload, not an observed mean count. The point uses one forward pass per essay; folds and training epochs do not multiply inference work.

For sequence length S and width H=768, count 12 × (24SH² + 4S²H) for attention/MLP matrices and both attention products, plus 2H² for a pooler and 2H for the score head. Each multiply-add counts twice. Embedding lookup is not a dense multiplication by every vocabulary embedding. No training loss, optimizer or unused language-model vocabulary head is included. Bias, normalization, softmax and elementwise nonlinearities are omitted; they are small relative to these matrices. Whether the author used the pooler changes less than 0.002%.

This gives **96,637,945,344 FLOPs**. Unpadded 448 and 350 positions would give 83.50 and 63.97 billion. The 512-position assumption is deliberately visible in `compute_evidence`; it should be replaced if actual inference lengths become available. A batch dimension would amortize to the same per-essay dense operations. The human reads the whole essay, whereas the model truncates long inputs.

[recompute.py](recompute.py) produces [calculations.json](agent-work/derived/essay-scoring/calculations.json) using only Python's standard library.

## Human time

[ETS's GRE scoring study](https://files.eric.ed.gov/fulltext/EJ1202816.pdf), Table 3, reports a participant-average 203.82 seconds per validity response in operational scoring; the calibration mean is 190.80 seconds. The former is the closer reference. Validity essays were selected as clear examples of score levels (printed p. 4), so this timing does not sample every degree of essay ambiguity. These are different essays and raters, and this study does not measure ASAP timing or establish the requested QWK target.

Use **200 seconds** for a trained rater already familiar with the rubric to read and score the described essay. A task decomposition gives 105 seconds to read 350 words at an assumed 200 words/minute, 75 seconds to apply the rubric and consider ambiguous passages, and 20 seconds to check and enter the score. These are judgments, not timed substeps. They support the same order of magnitude as the GRE record; the slightly easier school-essay content does not warrant a precise scaling factor.

A **120–300 second** scenario covers quick familiar cases and difficult writing requiring rereading. Prior rater training and daily calibration are excluded, just as prior model training is excluded. No detailed feedback, second independent rating or adjudication is required. The estimate targets a single rater at model-comparable quality rather than recreating the full reference-label production process. This is `transferred_timings` plus `estimated`, with a blank human_attempts count and subset all. The donor includes 350 raters' operational validity-essay judgments, but the number of contributing ratings is unreported. Passing prior calibration is a rater qualification, not a correct-validity-rating-only timing filter.

## Model identity

The task-specific R2BERT weights were fine-tuned from BERT-Base. Public release of those exact weights and the cased/uncased variant were not established, so the release date is blank. The model CSV preserves the paper's rounded 110-million count; the FLOP recipe uses layer dimensions rather than that rounded storage total.
