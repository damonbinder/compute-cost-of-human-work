# PEGASUS news summarization

## lang-summarize-xsum-pegasus-humanstudy

### Task and original records

[Lai et al. (2022)](https://aclanthology.org/2022.naacl-main.35/) recruited experienced writers to summarize supplied articles, with unassisted writing as one condition. The selected point covers the 120 XSum articles in that condition. It excludes post-editing: reading and writing an original summary are the human work being compared with automatic generation.

The [author release](https://github.com/vivlai/post-editing-effectiveness-summarization/tree/e4e147ed9203f3bee90211a425cb044157a32ecf) contains 1,440 summary/rating records in summaries_and_ratings.p. The release has an error: task_str says XSum throughout, and the same 120 XSum article strings are attached to both task_id halves. The task_id=2 summaries concern Reddit posts instead. For example, a bathroom anecdote is attached to a BBC-books article. Those 720 records cannot supply valid article-to-summary compute inputs and are excluded.

The 720 records with task_id=1 are coherent: 120 unique article IDs, each with six summary conditions and the same article across those conditions. The Manual and AI-generated subsets each contain 120 summaries. Their quality means reproduce the XSum bars in Figure 2. Additional direct inspection of IDs100,3037,6786 verifies relevant article-summary pairs. Articles average223.192 whitespace words; Manual summaries36.9 and model summaries17.333. Differences in output length are outcomes of the same task, not a separate quantity target imposed on one group.

The pickle is parsed symbolically by read_pickle_data.py using pickletools. It never invokes embedded globals, constructors or pickle.load. Array buffers are decoded as plain numbers and strings. The original file is retained unchanged with its hash; the calculator explicitly selects task_id=1 rather than trusting task_str.

### Human time and performance

Section3.3 specifies writing, journalism or communication expertise. Twelve people in each condition wrote ten summaries, giving120 unassisted XSum attempts. Figure3 reports a mean4.05minutes, or243seconds. Section3.6 defines this as time to read and write each summary. Do not use4.10minutes, which is the human-post-edit condition, or the whole study duration including tutorials/surveys. The figure was visually checked. Individual timing records are not released; the published mean is rounded to0.01minute.

Classify human_time_evidence=task_timings, human_time_method=unit_conversion, human_time_statistic=mean, human_attempts=120. Twelve is the participant count, not the attempt count. No selection on summary quality is applied.

The source’s overall-quality scale is1–7. Native averages are5.58 for Manual and4.193333 for AI-generated, matching Figure2. Thus performance_vs_human=below. This is not a comparison with the publisher’s introductory reference sentence: its4.4718 rating is a different baseline. Nor does the original2020 PEGASUS paper’s human-parity result supersede this study’s directly timed expert comparison. The same supplied articles and rubric were used; none_identified is appropriate for known comparison differences.

### Model and inference calculation

Section3.1 identifies the public google/pegasus-xsum checkpoint. Its model card describes the mixed/stochastic PEGASUS release, distinct from the original paper’s HugeNews-only model. The study does not retain the weight revision, library version, batching, generation overrides or per-step trajectories. Use the public pre-study configuration at a0aa5531c00f59a32a167b75130805098b046f9c and Transformers4.11.0 as an explicit implementation assumption. The model configuration itself names4.11.0.dev0. Source files are retained; no generation was rerun.

The architecture is16encoder/16decoder layers, width1024, feed-forward4096, vocabulary96103. The shared model record uses the paper’s rounded568M total; the operation recipe uses dimensions directly. Input embedding is a lookup, not a vocabulary projection. The decoder output vocabulary projection is included.

The original SentencePiece vocabulary yields mean275.0167 input positions including EOS; maximum390, so none needs the512-position truncation limit. Re-tokenized saved summaries plus EOS average21.8167positions, maximum63. They exclude the decoder-start token: each generated token is predicted by one decoder step consuming the start or previous output token. Re-tokenizing decoded text is a proxy for the original winning trajectory, not a native usage counter.

Defaults specify8beams and max_length64 including the start token, so at most63decoder steps. Hugging Face caches both self-attention and cross-attention keys/values. Its score-dependent stopping condition can finish earlier, but the retained winning summary does not reveal how long competing beams continued. For each article, calculate costs at the observed winning-length proxy and at63steps, then use their midpoint. This is a bounded judgment under the stated defaults, not an observed stopping-time expectation or an unconditional upper/lower bound on historical hardware operations.

For input length N, decoder steps D, layers L=16, width H=1024, vocabulary V=96103 and beams B=8:

- Encoder: L × (24NH² + 4N²H), once before beam expansion.
- Decoder cross-attention key/value projections: B × L × 4NH², once per beam, then cached.
- Decoder: B × [L × (28DH² + 4H D(D+1)/2 + 4NHD) + 2HVD]. This includes self-attention, cross-attention query/output, feed-forward and vocabulary projections.

Matrix multiply-adds count as two operations. Norms, activations, softmax, sampling/sorting and integer bookkeeping are omitted. There are no task helper models. Prior training and external human-quality assessment are outside this inference work unit.

Averaging the120 per-article midpoint recipes gives **496,465,614,028.8 FLOPs**. Conditional lower/upper means are383,237,489,459.2 and609,693,738,598.4. Padding every input to512 instead gives736,347,150,609.1 at the same midpoint stopping assumption. Single-example unpadded processing is the central assumption; historical batching was not reported. Accordingly compute_evidence=derived_assumed_inputs and compute_statistic=point_estimate. No recorded attempt-level compute sample is claimed; ai_attempts and compute_subset are not_applicable. The token field is339.2667 mean decoder positions across beams; encoder counts remain separately in the recipe.

The original TensorFlow PEGASUS code was also inspected but is not used for this point. It runs beam search to the full configured length and repeats uncached memory projections in its source graph. Transferring that recipe to this Hugging Face study would materially overstate compute. Separate source-level calculations remain in the collection review, not this point’s FLOP value.

### Release and reproduction

The Hugging Face [history](https://huggingface.co/api/models/google/pegasus-xsum/commits/main) and [8August2020 tree](https://huggingface.co/api/models/google/pegasus-xsum/tree/4d33b01d79672f27f001f6abade33f22d993b151) show a2.274GB TensorFlow weight file, tokenizer and configuration. Model release date is2020-08-08; it is not the study publication date. Later PyTorch and Flax uploads do not establish which version the study executed.

Run `python research/recompute.py SOURCE_DIRECTORY --output NEW_JSON` with sentencepiece installed. The calculator reads the original serialized records without executing them, checks task joins, counts text tokens and reports each article’s conditional bounds. It refuses to overwrite output. Source inputs and numeric results are retained in sources and research/calculations.json.
