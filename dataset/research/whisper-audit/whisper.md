# Whisper transcription audit

The [Whisper paper](https://cdn.openai.com/papers/whisper.pdf), Table1 and AppendixD.1.1 Table8, reports the architecture dimensions and greedy English recognition results. The retained original [model](https://github.com/openai/whisper/blob/v20230314/whisper/model.py), [decoder](https://github.com/openai/whisper/blob/v20230314/whisper/decoding.py), [tokenizer](https://github.com/openai/whisper/blob/v20230314/whisper/tokenizer.py) and [audio](https://github.com/openai/whisper/blob/v20230314/whisper/audio.py) code establish the inference recipe. The newer model.py originally collected for this audit is retained separately; the dated code controls the calculation.

## Operations

Both observations use known English, greedy decoding, no timestamps, one audio window and no fallback. Audio is padded to30seconds:3,000mel frames, then1,500encoder positions. The tiny.en architecture has width384, four encoder/decoder layers and vocabulary51,864; large-v2 uses1280,32 and51,865. Each attention layer has dense Q/K/V/output projections and a4×width MLP.

Let S=1,500, d=width, L=layers, n=generated lexical tokens, p=prompt length and T=n+p. Counting two operations per multiply-add:

```
encoder = 2*(3000*3*80*d + 1500*3*d*d)
          + L*(24*S*d*d + 4*S*S*d)
pairs = p*p + sum(k for k in range(p+1, T+1))
decoder = L*(4*S*d*d + 28*T*d*d + 4*T*S*d + 4*d*pairs)
          + 2*T*d*vocabulary
```

The decoder projects audio keys/values once, then reuses them. Text keys/values are cached across generated tokens. The first prompt forward computes its full masked attention matrix; later forwards process one new position. Vocabulary projection is charged for every computed position, including the initial prompt. Biases, layer norms, nonlinearities, softmax and signal preprocessing are omitted; the estimate covers dominant neural matrix arithmetic. No multiply-add is removed because of half precision.

For tiny.en, the no-timestamp prompt is start-of-transcript plus no-timestamps: p=2. The multilingual model additionally uses English and transcribe: p=4. EOS is predicted from the final lexical position and is not then processed in another forward. Thus100lexical tokens require102or104processed positions, rather than the old blanket105. This is a small numerical correction, not a change in the assumed speech content. Matrix parameter counts in the existing shared model records remain correct under their stated exclusions.

[calculate.py](calculate.py), Python3 standard library only, takes explicit source/output directories and reproduces the components from `inputs.json`.

## whisper_tiny_en_clean30s

Assume75spoken words and100lexical tokens in a clear30-second English read-speech window. Corrected compute:47,196,340,224FLOPs, including36,937,728,000encoder FLOPs. Human time remains120seconds. Greedy test-clean WER5.6% is a benchmark transfer; comparable lexical accuracy is the specified human target, not a measured human result. Sensitivity75–140lexical tokens gives45.5–49.8GFLOPs.

## whisper_large_v2_clean30s

Same work unit and content assumptions. Corrected compute:2,780,174,192,640FLOPs, including2,272,665,600,000encoder FLOPs. Human time remains120seconds. Greedy test-clean WER2.7% is a benchmark transfer; the human target matches by construction. Sensitivity75–140lexical tokens gives2.73–2.85TFLOPs.

[Rev’s manual-transcription guide](https://webflow.rev.com/blog/how-to-transcribe-an-interview) estimates four work hours per audio hour for an average person, including pausing, replaying and editing. This is a provider estimate, not a recorded timing study. Applying4:1to clear read speech is reasonable as a central work-rate assumption;3:1–6:1gives90–180seconds for these windows. Neither a human learning curve nor a quality-specific speed curve was measured. Therefore `human_time_evidence=assumed` and `human_time_method=work_rate` remain appropriate. The assumed human and AI targets use the same input quantity and lexical criterion; benchmark transfers alone do not establish a different AI–human task or assessment. Proposed `comparison_issues=none_identified` replaces the old flags, with the transfer stated in notes.

## perc-asr-parity-whisper

Replace the nonexistent interpolated50M model with actual tiny.en. Work unit: one representative five-second clear English read-speech clip, about12.5words/17lexical tokens, with the same greedy no-timestamp configuration. The input still pads to30seconds. Compute is41,723,535,360FLOPs and19processed text positions. This is not one-sixth of the30-second point.

The original [Deep Speech2 paper](https://proceedings.mlr.press/v48/amodei16.pdf), section6.1 and Table4, reports5.83% LibriSpeech test-clean WER for a two-worker procedure. Each worker transcribes independently without automatic correction, replay is allowed, and the better transcript is chosen using the reference. Average effort is27seconds per transcription for clips averaging about5seconds across the study. Human effort for the two transcripts is therefore estimated at54person-seconds. This is a transfer from the study’s mixed test-set timing to a representative clear read-speech clip; it is not a task-specific observed mean. Sensitivity36–81seconds allows the corpus/length transfer and short-clip handling overhead to vary. The two workers are a workflow count, not the unknown sample size underlying the reported27-second mean. Human_attempts is blank and subset all: both transcripts contribute to the transferred timing, regardless of which is selected for accuracy. The publication does not identify a timing-trial count for the mixed-corpus mean.

Whisper tiny.en’s5.6% greedy test-clean WER is broadly comparable to the source’s5.83%, supporting `match` rather than a fictional interpolated architecture. These are separate studies: Whisper’s normalizer differs from the original DS2 scoring pipeline. The human score also benefits from reference-informed best-of-two selection; it is not an individual worker’s accuracy or an ordinary deliverable-selection process. Record `different_assessment` for normalization and reference-based transcript selection. Workers themselves did not receive the reference, so this does not establish different inputs or tools. Both human transcription efforts are included; no successful-only time subset is used. The row does not claim exact parity under one common re-scoring pipeline.

The one-minute Whisper-large lead and real-time tiny.en dictation lead add no distinct observed workload or human protocol to the existing30-second rows. Mark `covered_related`; the paper alone does not establish a separate live incremental-dictation implementation or latency constraint. Multiplying the existing task by two would add no independent evidence.
