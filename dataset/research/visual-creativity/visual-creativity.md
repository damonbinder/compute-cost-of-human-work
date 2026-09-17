# One self-guided drawing from an ambiguous shape

This point estimates one image-generation execution and one ordinary person's attempt to turn an ambiguous shape into a drawing. It covers the Self-Guided condition of the [TCIA study](https://arxiv.org/abs/2511.16814v1). It excludes prior model training and the subsequent rating experiment.

## Human time

The [published procedure, sections 5.2–5.3](https://doi.org/10.1002/advs.202524142) fixes the ideation interval and caps drawing time. It does not report mean drawing times. I inspected the original figure 2: the nonartist examples are brief outline drawings, such as a butterfly, a boat and a face, with little shading. The estimate covers that level of work under the experiment's procedure.

| Component | Seconds | Basis |
|---|---:|---|
| Think of images based on the shape | 45 | Prescribed interval |
| List ideas and choose one | 15 | Judgment; a few short ideas |
| Draw the selected idea | 75 | Judgment from the simple line drawings; below the two-minute cap |
| Total | 135 | Sum |

A faster case uses 5 seconds listing and 45 drawing, giving 95 seconds overall. A slower case uses 30 seconds listing and the full 120 drawing, giving 195 seconds. These are scenarios, not measured quantiles. The central is `llm_estimate_judgment`: the prescribed ideation interval is one input, but the full work unit does not fix its duration. No human timing observations feed it, so attempts and subset are `not_applicable`. The 26 nonartists and 265 retained drawings are performance evidence, not timing samples. The human target is the observed nonartist quality, not a constructed match to AI quality.

## Performance

The authors' [public analysis](https://osf.io/bs3k9/overview?view_only=0206a9899d0c48eaba49ced3a4ea4773), retained as `visual-creativity-analysis.html` and `.Rmd`, reports estimated marginal means from the creativity-by-category-by-rater model. The human-rater cells are used; GPT ratings are excluded from this comparison.

| Drawing group | Human-rater estimated marginal mean | Retained drawings |
|---|---:|---:|
| Nonartists | 3.22 | 265 |
| Self-Guided AI | 2.75 | 222 |

The factor score combines liking, vividness, originality, aesthetics, and curiosity/interest. The analysis linearly transforms the factor predictions to a 1–7 scale. These numbers are neither success probabilities nor a percentage of human capability. The paper also finds the Self-Guided condition worse than nonartists in the human-only analysis. `below` is appropriate: the example drawings perform the requested job, but human judges find them less creative. Even subtracting the scale minimum as a rough check gives (2.75−1)/(3.22−1) = 0.79, comfortably above the current half-score exclusion guide; the actual classification rests on the drawings and ratings, not that ratio.

Images containing text, pseudo-text or colours were removed before rating. The total AI generation count before this filter is not reported consistently: the supplement calls the retained counts generated counts. The compute recipe covers one unselected execution, while the quality evidence covers retained images. `different_attempt_selection` records this. The human removal rate is not borrowed to estimate AI retries. The human sample count has its own source inconsistency: the methods say 660 images, although 324 artist plus 312 nonartist images total 636. This discrepancy does not determine either axis here.

The Self-Guided AI prompt is “Children monochromatic drawing”; it receives the supplied shape through Canny ControlNet. Humans mentally generate, list and select ideas, then draw on paper, without being told the creativity purpose. This tool/prompt difference is recorded. The AI fine-tuning set includes drawings from the human comparison cohort, so this is not a held-out test of general creativity.

## Compute

[Supplement S2](https://pmc.ncbi.nlm.nih.gov/articles/PMC13170252/) reports SDXL Base 1.0 with TCIA LoRA, Automatic1111, DPM++ 2M, 30 sampling steps, CFG 7–8 and Canny ControlNet. CFG evaluates two branches. The historical ControlNet hook stops only when `step / total_steps > end`, giving 7, 10 or 13 active calls for ends 0.2, 0.3 or 0.4. The central uses 10. DPM++ 2M evaluates the denoiser once per step; “2M” does not mean two denoiser calls per step.

The source gives 1024×1024 for training but does not explicitly establish inference resolution. The central assumes SDXL's usual 1024 generation. A 512 scenario is also calculated. The exact ControlNet checkpoint is unreported; the central uses the original full SDXL Canny architecture, with the small variant as a scenario. LoRA is treated as merged into the base linear weights, with one merge charged to this standalone execution.

`visual-creativity-count.py` profiles published architectures on meta tensors: no model weights, generated images or GPU execution are needed. PyTorch counts matrix multiplication, convolution and attention at two operations per multiply-add. The script adds scalar operations, residual additions, sampler work, two text encoders, and one VAE image decode. Both spatial self-attention and text cross-attention are already included. No LLM attention surcharge is added. The model has no shared per-token attention shape, so the point's two attention fields are blank.

| Component | FLOPs |
|---|---:|
| 30 UNet evaluations, two CFG branches each | 406,930,860,755,520 |
| 10 full ControlNet evaluations, two branches each | 60,010,021,310,400 |
| VAE decode | 10,495,343,536,896 |
| Two CLIP text encoders | 222,741,133,360 |
| One-time LoRA merge | 99,342,024,704 |
| Sampler and CFG scalar allowance | 31,457,280 |
| Total | 477,758,340,218,160 |

The text-token field is 308 processed encoder positions: two encoders × two CFG branches × padded length 77. It includes padding and empty negative conditioning, not image patches. Fresh conditioning is charged once. Reusing the loaded model and cached text lowers the total by less than 0.1%. Canny preprocessing is a conventional image operator rather than a neural model and is excluded. External human/AI grading is outside image generation and excluded.

| Scenario | FLOPs |
|---|---:|
| 512 resolution, full ControlNet, end 0.3 | 112,474,582,852,144 |
| 768 resolution, full ControlNet, end 0.3 | 257,414,489,614,256 |
| 1024 resolution, small ControlNet, end 0.3 | 428,495,880,262,960 |
| 1024 resolution, full ControlNet, end 0.3 | 477,758,340,218,160 |

The point has no numeric low/high bars: current COLUMNS limits them to shared active-parameter priors and the cache-derived context constant, neither of which applies here. The substantial resolution and checkpoint uncertainties remain in this recipe. `derived_assumed_inputs` describes them. No discard correction is applied to one generation. The calculator separately shows hypothetical cost per retained image as F/(1−d) for stated discard fractions; those are not observed costs or the CSV's work unit.

## Model

The model is the TCIA-adapted SDXL, not the publicly released base alone. The adapted weights were not released. Its registry date is 2025-11-20, the [first public preprint](https://arxiv.org/abs/2511.16814v1), under the current announcement-date convention.

| Architecture source | Revision |
|---|---|
| [SDXL Base 1.0](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/tree/462165984030d82259a11f4367a4eed129e94a7b) | 462165984030d82259a11f4367a4eed129e94a7b |
| [Full Canny ControlNet](https://huggingface.co/diffusers/controlnet-canny-sdxl-1.0/tree/eb115a19a10d14909256db740ed109532ab1483c) | eb115a19a10d14909256db740ed109532ab1483c |
| [Small Canny ControlNet](https://huggingface.co/diffusers/controlnet-canny-sdxl-1.0-small/tree/edd85f64c5f87dfb6d73762949d9daca16389518) | edd85f64c5f87dfb6d73762949d9daca16389518 |

The two text encoders contain 123,060,480 and 694,659,840 parameters, totaling 817,720,320. The UNet has 2,567,463,684 parameters. A single 2P coefficient is inappropriate for this repeated spatial network; the operation recipe accounts for each module separately.

## Reproduce

The required public configuration JSONs are included in `visual-creativity-inputs/`; the script does not require the large retained source archive or any downloaded weights. Install torch 2.8.0, diffusers 0.35.1, transformers 4.56.1 and accelerate 1.10.1 in a temporary environment. From the study's research directory:

```sh
python visual-creativity-count.py --sources visual-creativity-inputs --assumptions visual-creativity-assumptions.json --output /tmp/visual-creativity-new.json
```

The output must not exist. Original PDFs, source code and authors' analysis files are retained separately under `agent-work/sources/visual-creativity/`. They are provenance; published config inputs and links above support reproduction independently of that directory. No dollar amounts for this work unit were reported, so both cost bases are `not_available`.
