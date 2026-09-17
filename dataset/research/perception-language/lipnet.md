# Lipreading a GRID sentence

## perc-lipread-lipnet

[LipNet paper](https://arxiv.org/html/1611.01599), sections 4.2–4.3 and Table 3, supplies the protocol, performance and network. Three experienced lipreaders received grammar instruction and ten minutes of annotated examples, then annotated evaluation clips. Their mean word error rate was 47.7%; LipNet's unseen-speaker WER was 11.4%. Use that split, not the headline overlapped-speaker result. The task is a six-word, three-second silent clip.

Human time is **15 seconds**, an estimate, not a reported trial duration. Assumed workflow: six seconds to view twice, about seven seconds to enter a short six-word response, and two seconds to choose/check ambiguous words. A plausible range is 8–30 seconds. The target is the observed human baseline, not AI-level accuracy. The paper does not establish replay count or response time; the ten-minute familiarization is excluded from subsequent task performance. Human attempts are not applicable to this constructed duration estimate. Expert denotes experienced lipreaders, not typical hearing adults.

## Computation

The [authors' implementation](https://github.com/bshillingford/LipNet/blob/master/exp/0001.lua), retained in `agent-work/sources/perception-language/lipnet-0001.lua`, resolves an inconsistency in Table 3: convolution layers two and three use spatial stride one, consistent with the reported output shapes. Layer one uses stride two. Count multiply plus add as two operations.

For 75 frames:

| Component | FLOPs |
| --- | ---: |
| Conv 3→32, kernel 3×5×5, output 75×25×50 | 1,350,000,000 |
| Conv 32→64, kernel 3×5×5, output 75×12×25 | 6,912,000,000 |
| Conv 64→96, kernel 3×3×3, output 75×6×12 | 1,791,590,400 |
| Bidirectional GRU, input 1,728, hidden 256 | 457,113,600 |
| Bidirectional GRU, input 512, hidden 256 | 176,947,200 |
| Linear 512→28 at 75 positions | 2,150,400 |
| Total | **10,689,801,600** |

Convolution count is twice output elements times input channels times kernel volume. Each GRU contributes 2 × 75 × 2 directions × 3 gates × 256 × (input size + 256). This is the dominant matrix-operation estimate for one forward pass; biases, activations and pooling are small omitted terms. The paper's character-level CTC beam search and n-gram scorer are not additional neural passes. Their arithmetic is not included in this estimate. Input is the prepared mouth crop; face detection/cropping is outside the stated work unit. Humans see the original face video, flagged as different inputs. No training compute is counted.

The exact evaluated checkpoint's public release date is not established. The authors publish code, but the inspected repository does not supply the evaluated weights. Do not substitute the paper date. This is not a token-based model, so shared token coefficients and encoder/decoder parameter fields are not applicable.
