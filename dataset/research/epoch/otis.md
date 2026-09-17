# OTIS Mock AIME: representative exam-question effort

The source-defined set is all 45 questions from the 2024, 2025 I and 2025 II papers. [Original contest page](https://web.evanchen.cc/mockaime.html) specifies three hours per 15-question paper and prohibited computational aids. Human is a trained contest participant, not an average adult. AI responds independently to each question; human allocates effort across the complete exam.

## Human allowance versus observed timings

Human time = **10,800 seconds / 15 = 720 seconds per question-equivalent**, assuming a participant works for the full allowance. This is **assumed active time**, not a recorded mean duration and not the time needed to solve every question. It includes effort on unsolved questions. Human attempt count is not applicable to this duration assumption, even though performance has observed participants.

[2024 report](https://web.evanchen.cc/exams/sols-OTIS-Mock-AIME-2024.pdf), §3.1, score frequencies for scores 0–15: `[2,5,3,5,9,9,15,16,11,6,3,4,1,1,1,1]`; N=92, mean=6.2934783/15. [2025 report](https://web.evanchen.cc/exams/sols-OTIS-Mock-AIME-2025.pdf), §3.1: I frequencies `[0,2,2,2,3,3,10,10,12,16,8,6,4,3,1,0]`, N=82, mean=8/15; II `[0,0,0,0,3,7,6,12,16,21,20,21,8,1,0,0]`, N=115, mean=8.9043478/15. Equal weighting of papers, matching the 45-question AI set, gives 51.5507%. The 2025 introduction reports 83/116 instead, while the actual frequency tables sum to 82/115; use the tables and preserve this discrepancy. These are submissions, not measured timed attempts contributing to the duration statistic.

Actual testsolver statistics in both reports offer a useful cross-check, not an interchangeable baseline: timings select correct first answers, use prepublication versions, and permit answer checks. For example, 2025 I.1 has median 1:20 among 30 first-try correct solvers, I.10 9:30 among 2, I.13 24:52 among 2, and I.15 has no first-try solve. The exam allowance is preferable for the entire set because it accounts for unsuccessful effort rather than dropping the hardest questions. These data make a 12-minute budget plausible, but do not prove all contestants used the whole budget.

## Input and compute assumptions

All45 original question texts were subsequently recovered from a public Epoch evaluation archive. We count each full question with the later run’s short instruction and12 assumed chat positions. This transfers the historical task content, while the historical wrapper remains estimated. See [input reconstruction and per-model counts](epoch-otis-input-correction.md). The earlier fixed200-token assumption is no longer used.

Mean outputs and best-scored accuracies come directly from [Epoch’s original output-length CSV](https://epoch.ai/data-insights/output-length). Compute is the reconstructed mean input plus reported mean output, multiplied by the shared model coefficient. Known reasoning is included in the output counter and is not added twice. Unreported historical cache decomposition remains an assumption.

<!-- generated-point-appendix -->

## reas-epoch-otis-llama3-70b

Original Epoch identifier `Meta-Llama-3-70B-Instruct`, benchmark `OTIS Mock AIME 2024-2025`. Mean input 187.155555556 + reported mean output 705.266666667 = 892.422222222 tokens. Shared coefficient 140000000000 FLOPs/token gives **1.24939111111e+14 FLOPs**. Human time remains720 seconds under the full-exam-effort assumption. Performance category is `below` relative to51.5507% human accuracy. [Complete calculation](epoch-otis-input-correction.md#reas-epoch-otis-llama3-70b).

## reas-epoch-otis-qwen25-32b

Original Epoch identifier `qwen2.5-32b-instruct`, benchmark `OTIS Mock AIME 2024-2025`. Mean input 195.288888889 + reported mean output 841.755555556 = 1037.04444444 tokens. Shared coefficient 65000000000 FLOPs/token gives **6.74078888889e+13 FLOPs**. Human time remains720 seconds under the full-exam-effort assumption. Performance category is `below` relative to51.5507% human accuracy. [Complete calculation](epoch-otis-input-correction.md#reas-epoch-otis-qwen25-32b).

## reas-epoch-otis-v3-0324

Original Epoch identifier `DeepSeek-V3-0324`, benchmark `OTIS Mock AIME 2024-2025`. Mean input 184.311111111 + reported mean output 3179 = 3363.31111111 tokens. Shared coefficient 74000000000 FLOPs/token gives **2.48885022222e+14 FLOPs**. Human time remains720 seconds under the full-exam-effort assumption. Performance category is `below` relative to51.5507% human accuracy. [Complete calculation](epoch-otis-input-correction.md#reas-epoch-otis-v3-0324).
