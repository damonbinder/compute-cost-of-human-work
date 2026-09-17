# RT-2: pick one named tabletop object

## robo-pick-rt2

Primary source: [RT-2 original paper](https://arxiv.org/html/2307.15818v1), Sections 3.3–4.1, Appendices D, F and H. Choose a concrete representative instruction, “pick banana,” from the unseen-object easy group. The work ends with the identified object securely lifted; there is no navigation, placement or multi-step language plan. The selected model is RT-2-PaLI-X-55B, not PaLM-E or the chain-of-thought extension. Its easy unseen-object group success is 70%; this is group-level evidence transferred to the representative pick, not a banana-specific measured score.

## Compute estimate

The original architecture uses a 22B vision transformer followed by a 32B encoder-decoder language backbone. Counting merely the 7–8 output action tokens times all 55B parameters would omit most visual work. The image embeddings are themselves processed by the language encoder on every policy observation.

Use a representative 224×224 input image with 14×14 patches, giving 256 image positions, plus an assumed 20-token task prefix. The 224-pixel configuration is a supported PaLI-X resolution, but the exact RT-2 deployment resolution is not stated; this is an assumption. Larger images are a material sensitivity. [PaLI-X architecture and resolution details](https://openaccess.thecvf.com/content/CVPR2024/papers/Chen_On_Scaling_Up_a_Multilingual_Vision_and_Language_Model_CVPR_2024_paper.pdf) support the model family and 224-pixel regime.

Approximate the 32B language backbone as 14B encoder and 18B decoder parameters. The exact split is not disclosed in the RT-2 paper; the larger decoder share allows for cross-attention. For a nine-position action output (eight action values plus termination), the major matrix terms per decision are:

- Vision: 2×22B×256.
- Language encoder: 2×14B×276.
- Decoder: 2×18B×9.
- Source-side cross-attention key/value projection correction: 2×1.8B×(276−9). The assumed 1.8B is the source K/V projection share of the decoder; the subtraction avoids counting the nine positions already included by the coarse decoder term.

This gives **20,277,200,000,000 FLOPs per decision**. Attention matrix multiplication, small projections and activation operations are omitted; for these short sequences they are small relative to the parameter matrix products. A 25% change in encoder/decoder allocation has much less effect than a change in image resolution.

The source reports 1–3 Hz policy operation. Use its midpoint, **2 Hz**, and estimate **10 seconds for one completed robotic pick**: roughly 3 seconds for approach/localization, 4 for slow alignment and closure, and 3 for lift and settling with repeated low-rate feedback. This is an explicit motor-execution estimate, not an observed trial mean. It implies twenty complete observations/action decisions, or **405,544,000,000,000 FLOPs**. A 5–20-second pick and 1–3 Hz rate give 5–60 calls; 448-pixel images would roughly quadruple dominant visual/encoder work. The central estimate is a best-supported illustrative completion cost. Failed whole-task attempts and retries until success are excluded.

## Human active time and quality

Estimate **3 seconds** for an ordinary adult to identify the named banana among a few visible familiar tabletop objects, reach, close a hand and lift it securely: about 0.5 seconds for identification, 1 second to reach, 0.5 seconds to grasp and 1 second to lift/check. This assumes the object is within reach and tools/setup are already positioned. A 2–5-second range covers ordinary placement variability. It does not include placing the object elsewhere or returning the hand for another cycle.

The ordinary human is assumed reliably capable of this familiar-object pick. The selected model's 70% easy-unseen-object group result indicates a meaningful deficit, so classify below; the speed estimate alone does not establish parity. Human hands and robot parallel grippers differ.

## Model release provenance

The source reports the evaluated RT-2-PaLI-X-55B but does not establish public availability of the exact robot-finetuned weights. Leave release date blank. Encoder/decoder allocations are explicitly estimated; no shared token coefficient is used for this multimodal operation recipe.

## Retained evidence and reproduction

The original PaLI-X CVPR paper is retained as `agent-work/sources/robotics-science/pali-x-cvpr2024.pdf` and extracted text. Section 3 identifies 50 layers in each language encoder/decoder and the native 224-pixel first-stage resolution; its video section identifies 16×16 patch positions at this resolution. `python3 build_tranche3.py` records the component arithmetic in `research/tranche3-operations.json`. The model table encoder total is 22B vision plus 14B language; these components process different sequence lengths and must not be treated as one shared per-token coefficient.

## Reviewed accounting and comparison

The token field records 9 × 20 = **180 decoder-processed positions**. Visual patches and language-encoder positions remain separate component workloads and are excluded from this token total. The easy-unseen-object group combines picks and relocations, so its transferred performance evidence is flagged `different_assessment`, alongside the human-hand/robot-gripper tool difference.
