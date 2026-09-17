# Whisper clear English transcription

Original sources: [Whisper paper](https://cdn.openai.com/papers/whisper.pdf), Table1 and AppendixD.1.1 Table8; [official model implementation](https://github.com/openai/whisper/blob/main/whisper/model.py); [official audio implementation](https://github.com/openai/whisper/blob/main/whisper/audio.py); [Rev's transcription-work estimate](https://webflow.rev.com/blog/how-to-transcribe-an-interview).

Work unit: one clear30s English speech window, known language, greedy decoding, no timestamps/fallback, compared with a human producing comparable lexical quality. This is an analytic workload representative of read speech, not a claim to have run a particular recording. Tiny.en greedy test-clean WER is5.6%; large-v2 is2.7%. These are source-defined benchmark errors, transferred to the constructed window. The performance label match is by the explicitly matched-quality human target, not a measured human test result.

## Human duration

Rev estimates four active human hours per hour of clear interview audio. It is a service-provider estimate, not recorded trial timings; evidence is assumed. Apply theexplicit work rate:30×4=120s. The target is lexical transcription, not exact formatting, diarization or word timestamps. For75 words in30s, this is37.5 output words/minute while listening, pausing and reviewing, a plausible ordinary-person work rate. The clear read-speech transfer is approximate: a fluent typist may be faster, unfamiliar terms slower. Matching the modest target error rates does not justify accelerating human work in direct proportion to WER; listening/typing dominates. No human attempts are invented.

## Operation recipe

The official architecture uses two convolutional audio layers to produce S=1500 positions per30s. Assume75 spoken words at150words/minute and4/3 tokenizer positions/word =100 lexical positions, plus5 prompt/special positions: T=105 decoder-processed text positions. These assumptions affect the decoder, not the1500 audio positions. There are no helper models. Language detection is disabled by known language. Decoder K/V is cached; beam width1 and no temperature fallback means no omitted retry multiplier.

For width d, layers L in EACH encoder/decoder, vocabulary V:

`encoder = 2(3000×3×80×d +1500×3d²) + L(24Sd²+4S²d)`.

`decoder = L(4Sd²+28Td²+4TSd+2T(T+1)d) +2TdV`.

Encoder includes convs, attention projections, MLP and attention matrices. Decoder includes one-time cross K/V projections, text self-attention/MLP/query+output projections, cross attention matrices, causal cached self attention, and vocabulary projection. Norms, biases, GELU and softmax are small and omitted. Audio/text positions are not added together. We do not use the invalid shortcut2×totalparameters×(audio+text tokens).

Approximate parameter counts for models.csv are independently reconstructed from those same source dimensions and code: encoder `12Ld²+3×80d+3d²`; decoder `16Ld²+Vd`. Counts omit norms/bias/positional matrices. Their basis is reported under COLUMNS.md: these are the recipe’s matrix-component counts calculated from published dimensions, not assumed dimensions. They document model size but the FLOP calculation uses architecture dimensions directly.

## whisper_tiny_en_clean30s

d=384,L=4,V=51864. Total47,394,938,880 FLOPs; human120s. Source greedy WER5.6%. Encoder/decoder parameter approximations are7,612,416 and29,352,960.

## whisper_large_v2_clean30s

d=1280,L=32,V=51865. Total2,782,036,953,600 FLOPs; human120s. Source greedy WER2.7%. Encoder/decoder parameter approximations are634,368,000 and905,248,000.

Thebenchmark utterances need not fill30s. Thefull-window normalization does not assert exact average FLOPs per benchmark question. It is a useful explicit quantity-of-work estimate; differences in input window duration and assessment are retained in CSV issues.
