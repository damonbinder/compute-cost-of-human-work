# GPT-4o native-audio transcription

## perc-asr-gpt4o

Work unit: one60-second recording of clear English speech, transcribed to plain text with one native-audio request and no previous conversation. Assume150spoken words and200output text tokens. The instruction asks for an English transcript only; allow20text tokens for its wording and message framing. The human target is comparable lexical accuracy, with replay and ordinary typing tools but no ASR assistance.

The [original empirical study](https://arxiv.org/html/2502.09940v1), footnote1, tested `gpt-4o-audio-preview-2024-10-01`. Section4.6/Figure11 reports English speech recognition better than the Whisper-LLaMA baseline, supporting transcription capability; this is not a measured human comparison or an absolute WER for this constructed minute. Human performance matches by the stated target. [Rev’s estimate](https://webflow.rev.com/blog/how-to-transcribe-an-interview) of four work hours per audio hour gives240seconds; a3:1–6:1scenario gives180–360seconds. This is an assumed rate, not recorded task timing.

The [provider changelog](https://developers.openai.com/api/docs/changelog) says the audio-preview Chat Completions model was released October17,2024, sharing the Realtime API’s underlying model. Use that endpoint release day; the October1snapshot suffix is not itself proof of Chat Completions availability. This is distinct from the text-only GPT-4o snapshots and from the later `gpt-4o-transcribe` product.

## Compute

The [original October2024 announcement](https://openai.com/index/introducing-the-realtime-api/), “Availability & pricing”, gives audio input at$100per million tokens and approximately$0.06per audio minute, with the same prices for Chat Completions. Those two provider statements imply approximately600billed audio positions per minute. This reconstructs the original billing rate; it does not infer FLOPs from dollar cost. A short retained source extraction records both numbers and the locator.

**The central architecture proxy assumes one backbone position per billed audio position. That mapping is not disclosed.** Thus the backbone processes600audio positions plus220text positions. Applying the shared GPT-4o50B-active-parameter assumption gives:

```
backbone = 2*50e9*(600 + 20 + 200) = 8.2e13 FLOPs
```

The consistent size prior is the central200B total estimate in the original [Epoch analysis](https://epoch.ai/gradient-updates/how-much-energy-does-chatgpt-use), multiplied by its assumed one-quarter activation. Epoch’s pessimistic energy example instead uses400B total/100B active; neither is a provider disclosure. Transferring50B active to this audio snapshot is an explicit family assumption.

**Audio feature extraction is additional to backbone arithmetic.** Use two30-second Whisper-large encoder passes as an acoustic-front-end proxy:32layers, width1280,80mel channels and1,500encoder positions per pass, including convolutions and attention. The source-based operation recipe is in [whisper.md](whisper.md). It adds4.5453312e12FLOPs, for total8.65453312e13, stored as8.65e13. The actual GPT-4o acoustic front end is undisclosed; this does not claim that GPT-4o runs Whisper or first produces a transcript. Whisper supplies a concrete speech-encoder scale rather than a visual-encoder or hardware-utilization guess. No audio is generated, so no vocoder/output-audio work is counted. No separate moderation call is invented.

Sensitivity varies active size25–100B, actual backbone audio positions0.5–2times the billing proxy, output text150–300tokens, and acoustic-front-end cost0.5–2times the proxy. The high case also adds10%backbone attention overhead. Combined scenarios are2.58e13–3.43e14FLOPs, not confidence bounds. This architectural conversion dominates the uncertainty; the frontend central component is only5.3%of total. Cache reuse is assumed within generation; the fresh audio/instruction context is processed once, and there are no repeated conversation turns or retries in this defined one-request work unit.

Only220text tokens enter the CSV `tokens` field, using `input_output`. Audio positions are retained separately in the calculation. `compute_method=operation_count` and `compute_evidence=derived_assumed_inputs` distinguish this explicit composite proxy from a measured operation count. `comparison_issues=none_identified` concerns the defined matched-quality task; it does not certify the architecture or timing assumptions. The code uses Python3 standard library only and accepts source/output directories.
