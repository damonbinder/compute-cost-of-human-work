# MNIST: original LeNet-5 inference

## perc-mnist-lenet5

The unit is one clean 28×28 MNIST test digit, centered/padded to 32×32, assigned one of ten labels. The human is an ordinary adult familiar with Arabic numerals; prior literacy is outside this inference comparison. This is a matched-quality time estimate targeting approximately 99% accuracy, not a measurement of human performance. No ensemble, training, artificial distortion or repeated test-time augmentation is included.

## Primary sources

* LeCun, Bottou, Bengio and Haffner, *Gradient-Based Learning Applied to Document Recognition*, original 1998 manuscript: https://leon.bottou.org/publications/pdf/ieee-1998.pdf, retained as `agent-work/sources/mnist/lecun-1998.pdf`. Pages 7–8 (architecture and Table I) and page 12 (Figure 9) were visually inspected because extracted text is garbled. Figure 9 gives original LeNet-5 error 0.95%; the separate distortion-trained row is 0.8% and the boosted row is another model. The graph's digit templates and input examples establish the work as isolated numeral recognition, without word context or document layout.
* Roest and Ramakrishnan, CCNeuro abstract, https://www2.securecms.com/CCNeuro/docs-0/5928ba3f68ed3f0d4a8a2589.pdf, retained as `agent-work/sources/mnist/roest-timing.pdf`. Five participants judged target presence in digits at different noise levels. Figure 2 was visually inspected: the low/zero-noise human response-time curve is approximately 1.1 seconds (at 1600-pixel rendering, y=1335 corresponds to zero, y=1108 to 2.5 s, and the initial curve near y=1231 gives 1.15 s). This is a coarse visual reading, not raw trial data. The low-noise timing point draws on five participants each judging 40 digits at that noise level: 200 donor attempts, subset all. The abstract reports no correct-response-only timing filter; the other noise conditions are not additional observations underlying this endpoint. The task is binary presence detection, not ten-way classification.

## Human estimate

Central active response time is **1.5 seconds** per digit, excluding between-trial fixation, confidence questionnaires, setup and prior learning. The empirical anchor is the approximately 1.1-second low-noise digit decision above. Ten possible keys increase response selection compared with a binary response, but the intended clean digit task removes the noise manipulation and explicit target search. The central estimate adds 0.4 seconds for choosing and entering a numeral from ten keys rather than selecting a binary response: a judgment-based interface and response-selection allowance, not a measured effect or rounding operation. It assumes an ordinary numeral reader rather than a practiced keypad operator. At this pace a reader has enough time to inspect the whole tiny glyph and enter its identity; the central target is approximately the model's 99% correct labels, allowing a minority of ambiguous or mislabeled digits. The estimate does not presume perfect human performance or label ambiguous digits correctly by fiat. The bounds bracket the one thing the transfer turns on, how much of the 1.1-second anchor is response selection rather than perception. If none of it is, the ten-way task inherits the anchor unchanged, 1.1 seconds. If all of it is, Hick's law scales it by log2(11)/log2(3) and it becomes 2.4 seconds. Those are the bounds, and the 1.5-second central sits between them. More time alone is not asserted to resolve inherently ambiguous samples.

`transferred_timings` describes the duration's empirical anchor; `estimated` describes the substantive transfer. The final human work unit and target match the AI by construction, so comparison_issues is none_identified; the timing-source task difference is explicit in CSV notes and is not presented as a direct matched experiment. This choice and the attainable approximately 99% target warrant independent judgment review.

Additional checks did not supply a cleaner direct timing baseline. RTNet (https://www.nature.com/articles/s41562-024-01914-8) tested eight-way noisy recognition with brief displays and confidence responses; this is also a transfer. Its linked OSF resource was inaccessible and was not circumvented. The sometimes-repeated 97.27% 'MNIST human accuracy' in https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0085175 traces in reference 112 to Chaaban and Scheessele's **USPS**, not MNIST, study and is not used here. A Concordia thesis lead returned 403 and is not treated as inspected evidence.

## Compute

`research/calculate.py` reproduces all terms; `research/calculations.json` retains the results. A weighted dot product plus bias costs 2n scalar operations for n inputs (n multiplications, n−1 additions and one bias). Trainable subsampling is a four-pixel sum (three additions), scale and bias: five operations per output. The architecture count is:

| Component | FLOPs |
|---|---:|
| C1: 6×28×28×25 MAC | 235200 |
| S2: 6×14×14 outputs ×5 | 5880 |
| C3: 60 map edges ×25 weights ×100 positions ×2 | 300000 |
| S4: 16×5×5 outputs ×5 | 2000 |
| C5: 120×16×25 MAC | 96000 |
| F6: 84×120 MAC | 20160 |
| 8084 scaled tanh activations ×7 | 56588 |
| Ten 84-dimensional Euclidean RBF distances | 2510 |
| 32×32 affine pixel normalization | 2048 |
| Total | **720386** |

C3's table has 6×3 + 6×4 + 3×4 + 1×6 = 60 map connections. This gives 150000 weight multiplications, not the prose's inconsistent 156000 connection count. The output is a squared Euclidean distance to fixed 84-dimensional templates: 84 subtractions, 84 squares and 83 additions per class, not a modern fully connected softmax. Integer argmin/label dispatch is not converted into FLOPs.

The original source does not establish a particular hardware implementation of tanh. Central seven-operation accounting uses five scalar operations for tanh (via an exponential and elementary arithmetic) and two scale multiplications for 1.7159·tanh(2x/3). An exponential is one scalar-operation convention here, not a claim about its machine instruction count. Three to twelve operations per scaled activation gives 688050–760806 FLOPs (about ±6%). This small implementation allowance is why compute evidence is derived_assumed_inputs. Pixel resampling/centering is not learned-model inference; normalization has nevertheless been included. No text-token coefficient applies. A publication year alone does not establish first public model availability, so release date is blank.
