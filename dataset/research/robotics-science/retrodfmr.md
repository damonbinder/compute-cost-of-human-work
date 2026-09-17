# RetroDFM-R: one explained retrosynthetic disconnection

## sci-retrosynth-llm

The assigned source is [the original July 2025 RetroDFM-R paper](https://arxiv.org/html/2507.17448v1), not a GPT-5 study. Preserve the task ID and correct the model identity. The original PDF and extracted text are retained under `agent-work/sources/retrodfmr-v1.*`.

Define the work as one first-pass, single-step proposal for the product in Figure 2B: a heteroaromatic biaryl bearing a protected aminopyrrolidine substituent. Given its SMILES, produce precursor SMILES and a short explanation considering alternative disconnections, then select one. Stop at this proposal; exclude literature verification, experimental conditions optimization, multistep route development and laboratory synthesis. This matches the actual displayed output's scope and specificity.

## Model and processed workload

Section 3.3 identifies a dense Llama-3-8B architecture, initialized from ChemDFM-v1.5: 32 layers, width 4096, feed-forward width 14336, eight K/V heads and 32 query heads. Use the reported nominal 8B size, giving 16 billion FLOPs per processed token. This is the shared two-active-parameters approximation, not a hardware runtime conversion.

The original paper does not provide per-example token usage or an unabridged machine-readable rollout. Figure 2B is a concrete workload anchor: the displayed rationale has 191 whitespace-delimited words and 1,490 normalized characters, excluding the SMILES and molecule diagrams. These counts are retained in `research/retrodfmr-example-counts.json`. Chemical terminology, punctuation and hyphenated identifiers make a generic words-to-tokens rule optimistic. At an assumed 3.5 characters/token it is about 426 tokens; round to 450. Allow 100 tokens for the precursor strings, answer tags and termination, and 150 for the product SMILES, instruction and chat framing. Thus estimate **700 processed tokens**, including prompt and generated reasoning exactly once.

**Compute = 700 × 16,000,000,000 = 11,200,000,000,000 FLOPs.** A 500–1,200-token range allows for formatting, an abbreviated printed rationale or different prompt framing; the central value represents one generation comparable to the displayed example. It is not the total search budget that selected a favorable figure example.

Use no repeated sampling, rooted-SMILES augmentation or answer beam search. The paper separately evaluates single predictions without those augmentations (Table 1, 59% exact match); its 65% headline belongs to augmented inference. Neither aggregate score is needed to establish a measured success probability for this particular proposal. The task is an illustrative one-generation reconstruction, not a claim that the displayed selected example was generated with no preceding rejected samples. The inference-only work excludes distillation teachers used during training and forward-synthesis models used as evaluators.

The authors' public repository, freshly cloned in `agent-work/sources/retrodfm-r`, has an initial release on 2026-08-25 and subsequently revised model and evaluation details. Full history was inspected. It does not establish the exact original-v1 checkpoint release or justify importing its settings into the 2025 reconstruction. Leave model release date blank.

## Human work at comparable quality

Estimate **10 active minutes (600 seconds)** for a trained synthetic chemist to make a comparably detailed first-pass proposal, using a non-AI molecular viewer/sketcher if useful. The product is more involved than a simple textbook bond cleavage, but the two candidate transformations are familiar and the output stops well short of a validated route.

Allocate about two minutes to read/depict the supplied structure and identify protection and stereochemistry; three minutes to consider the two main bond disconnections and select one; two minutes to construct/check the precursor representations; and three minutes to write a roughly 190-word explanation with the displayed level of selectivity discussion. This assumes a practiced chemist and a prepared drawing environment. A six-to-twenty-minute range covers familiarity and representation-entry speed. No observed human timing is claimed.

Classify **match** because the human estimate targets a proposal at the inspected output's level of detail and plausibility. It does not target a fully vetted synthetic procedure or require the model's broad feasibility assertions to be experimentally true. The authors themselves discuss hallucinations elsewhere in the paper; producing a provisional proposal is the relevant work here. Human and model receive the product without the true precursor answer. Source-selected example performance is not transferred into a general chemist-versus-model accuracy claim.
