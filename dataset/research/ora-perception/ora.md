# Recognizing corrupted handwritten digits

## ora-mnist-c-recognition

The [original study](https://pmc.ncbi.nlm.nih.gov/articles/PMC11175536/) reports mean human recognition latency of 1,130 ms for correct answers. This gives 1.13 seconds by unit conversion. The interval runs from image onset to the recognition keypress; the later digit-entry accuracy check and preceding fixation are excluded. The successful-trial count is not reported. The methods describe 143 participants, whereas the results say 146; neither number is an attempt count.

The images were chosen because ORA recognized them correctly, with varying numbers of processing steps. Humans made errors on these same images. Classify the AI as above for this selected set, with `different_attempt_selection`: this is a comparison conditioned on the AI's correct recognition, not general digit-recognition superiority. Human timing also selects correct answers. Exact human accuracy percentages were not recovered from Figure 6; the paper's qualitative comparison and stimulus-selection procedure establish the direction. The figure endpoint returned a cache miss, and direct retrieval returned a challenge page; no figure values were invented.

## Computation

Use the authors' [implementation at commit 5c60925238ec9a465f0c290a38a24c84fe3cb311](https://github.com/ahnchive/ORA-recognition/tree/5c60925238ec9a465f0c290a38a24c84fe3cb311). Retained files are `agent-work/sources/ora-perception/ourmodel.py`, `agent-work/sources/ora-perception/generate_stimuli_exp1_RT.ipynb` and `agent-work/sources/ora-perception/params.txt`.

The stimulus notebook explicitly sets five global steps and three routing iterations. The forward method actually executes all five global steps, then selects the answer at the first qualifying confidence threshold. Its reported one-to-five-step recognition time is therefore not an early-exit compute measurement. Count the full executed path once per image, excluding offline work selecting the experimental stimuli.

The encoder's two initial convolutions produce widths 26 and 24. Four residual stages have widths 24, 12, 6 and 3 and channel counts 32, 64, 128 and 256. Each stage has four convolutions; the last three also have a projection shortcut. This is 166,719,744 FLOPs per global step at two operations per multiply-add.

The decoder has layers 160→512→1024→784, costing 2,818,048 FLOPs per call. Each of the first two routing iterations reconstructs all ten classes, and one final reconstruction supplies the next spatial mask: 21 decoder calls per global step. Include capsule projection (737,280), six weighted reductions including the executed visualization reductions (552,960), and two agreement updates (184,320).

Total dominant arithmetic is **5 × (166,719,744 + 21×2,818,048 + 737,280 + 552,960 + 184,320) = 1,136,866,560 FLOPs**. `agent-work/sources/ora-perception/calculations.py` and `agent-work/sources/ora-perception/calculations.json` retain each convolution. Bias, normalization, activation, masking and small scalar operations are omitted under this matrix-operation convention; they are small relative to the convolutions and repeated dense decoding. This is an architecture calculation, not a measured profiler total.

The notebook refers to a historical `rrcapsnet` checkpoint path while the current repository labels the model directory `our-resnet`; its printed architecture agrees with the retained configuration. The operation count uses that documented architecture and evaluation settings. The exact model availability date has not been established; no paper date is substituted.
