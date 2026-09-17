# DeepSeek-Prover-V2: construct a Lean proof

## reas-lean-minif2f-deepseekprov2-cot32

One representative theorem from the 244-problem MiniF2F test set, with its formal statement and any answer already supplied. Generate 32 complete reasoning-and-proof candidates, and accept a proof if Lean verifies it. The human target is an experienced Lean/mathlib user with competition-mathematics experience, working without an LLM, producing verified proofs at approximately the model's 82.4% completion level. The estimated human effort is **one hour per attempted theorem**, including unsuccessful work. This is a formal proof-construction task, not an informal contest answer or learning Lean.

The original [DeepSeek paper](https://arxiv.org/abs/2504.21801v1), Table 1, reports **82.4% ±0.6% pass@32** for 671B CoT. Table 3 reports **6,751.9 generated tokens on average** for this model/mode on MiniF2F-test. This already includes the natural-language reasoning and Lean code: no extra imagined hidden-reasoning multiplier is added. The table does not identify its exact number of sampled responses or explicitly give success-conditioned counts. We interpret the unqualified generation average as covering generated attempts, consistent with its comparison of CoT and non-CoT generation cost; a twofold response-length sensitivity covers possible selection/configuration differences. The 217 released test proofs support pass@8192=88.9%, not a claim that those same 217 pass at 32 samples.

### Original input reconstruction

The [pinned original repository](https://github.com/deepseek-ai/DeepSeek-Prover-V2/tree/e598a57ea3284997d4a2a168a069fdd5064afbc8) has a successful-proof archive: 217 test and 221 validation files. Validation includes curriculum-training work and is excluded. We take the statement/header before `:= by` from each test file, replace its proof with `sorry`, and apply the original README's CoT prompt and released one-user chat template. The appendix supplies the corresponding prompt form. No successful proof body enters the prompt.

For the 27 absent test statements, the [original V1.5 dataset](https://github.com/deepseek-ai/DeepSeek-Prover-V1.5) supplies predecessor statements as **input-length proxies**. These are not asserted to reproduce every correction in V2's evaluation. The paper adopted Kimina corrections and three additional corrections, two in validation and one in test. Successful V2 declarations supersede predecessor text for 217 inputs. The Kimina original solution archive is retained as a cross-check, not silently substituted as the exact V2 task set. Missing source revisions chiefly affect this small input term; they do not license using predecessor validity to reinterpret the paper's score.

The actual released V2 tokenizer gives **237.0123 input tokens on average**, maximum 539. A 25% increase in every input changes total compute by under 1%. There is no native per-call input counter, but the actual tokenizer, prompt template and 217 original declarations make this a substantially narrower assumption than a generic token allowance. `task-inspection.json` retains 30 seeded examples, including unreleased failures; it is an inspection selection, not the scored cohort.

### Compute and sampling scope

V2 is trained on the original DeepSeek-V3-Base architecture. The [original V3 description](https://huggingface.co/deepseek-ai/DeepSeek-V3) reports 37B active of 671B total parameters. The retained V2 config agrees on 61 layers, 7168 width, 256 routed experts, eight selected experts plus one shared expert, and three initial dense layers. The coefficient is the same **74e9 FLOPs per token** used for the source architecture. No model weights are loaded.

The central parameter-multiplication estimate is:

`32 × (237.012295 + 6751.9) × 74e9 = 1.6549744315e16 FLOPs`.

Count all 32 requested candidates, including failed proofs. The predecessor's original `Sampling.sample` submits every request before retrieving outputs; `SearchProcess.run` collects all samples before summarizing verification. Its generator uses vLLM with `n=1` per request, without explicit prefix-cache enabling. This supports a **separate-prefill, compact live-request execution assumption**, not a claim that V2's unreleased inference harness is identical. It avoids imposing a fixed padded longest-branch cost from an unrelated framework. Sharing the input cache once instead gives **1.6006038110e16 FLOPs**, only 3.3% lower. Unknown engine grouping matters less here than in a long-input task because generated reasoning dominates.

Half/double the reported output mean gives **8.55549e15 / 3.25382e16 FLOPs**. These are source-interpretation scenarios, not evidence that the published average omitted half the work. The source quick-start's 8192-token maximum is not used as an observed length. That example is not the released evaluation configuration. No inference-time 7B helper is added: recursive 7B subgoal solving is part of training-data construction, whereas final V2 inference generates whole proofs. Prior V3 pretraining, V2 training and validation-curriculum search are outside this inference point. Lean's symbolic checking and integer tactic work are not converted from CPU seconds into invented FLOPs. Standard `params_tokens` omits cached-context attention and small scalar arithmetic; the attention term is added back in `compute_flops` (`research/attention-correction.md`).

`compute_evidence=derived_assumed_inputs`, `compute_statistic=point_estimate`, and attempts/subset `not_applicable` describe an analytic average-task workload, not a recovered collection of counted AI runs. The 32 samples are part of the point's work unit, not 32 observed timing records. `tokens_accounting=input_output` describes the counted text positions under the compact-request assumption.

### Human effort: source anchor and task-specific adjustments

The original [Collins et al. controlled study](https://arxiv.org/abs/2606.04273v1) is more relevant than informal competition clocks. Seven retained participants each completed three unaided tasks and three AI-assisted tasks; an eighth participant was excluded because videos were not separately recorded. Time is summed from recorded problem-solving sessions, not the two-week calendar window. All had undergraduate mathematics experience; four self-classified as advanced/expert in Lean, three as beginners. Unaided participants could use an editor and Lean compiler. Figure 9 gives approximate unaided mean minutes: number theory **45**, analysis **72**, counting **137**, geometry **155**, topology **206**, visual counting **78**. These are graph-read, rounded timings, not exact recovered logs. The source's data repository is currently restricted; no access was attempted.

The donor tasks included both statement and proof formalization, with informal proofs supplied. MiniF2F supplies the formal statement and answer, removing representation design, but requires finding a proof strategy. Therefore neither its ~120-minute overall average nor its measured accuracy is copied. The advanced/expert subgroup's unaided correctness was only about 42% on that particular six-task collection; it does not establish MiniF2F human accuracy.

Inspection matters. More than half of MiniF2F consists of 130 MATH arithmetic/algebra/number-theory questions. Examples include evaluating a fixed product modulo 10, proving `x/50=40 → x=2000`, or solving gcd/lcm constraints. Existing `norm_num`, arithmetic tactics and library lemmas often eliminate most mathematical search for an experienced user. Some tasks instead need coercions, finite-cardinality arguments, real powers or factorial/divisor lemmas. Generated proofs can be very verbose: their line counts are not treated as necessary human work. AMC tasks range from direct algebra to counting; AIME examples involve nontrivial Diophantine reasoning. The 20 IMO/shortlist problems include functional equations and substantial trigonometric identities. Their formalization can take hours even when the mathematical answer is supplied.

A duration model calibrated to the recorded range, then adjusted for this actual mix, is:

| Original task group | Count | Estimated active minutes per attempt | Reason for adjustment |
|---|---:|---:|---|
| MATH | 130 | 20 | Below the donor's 45-minute congruence task: statement already supplied and many instances close with standard arithmetic/library tactics; retain debugging time. |
| AMC | 45 | 60 | Around the donor's simple number-theory/analysis range; supplied encoding saves work but proof discovery and counting introduce it. |
| AIME | 15 | 120 | Multi-step number theory/algebra and library translation; closer to the donor's counting task than a short numeric evaluation. |
| Custom algebra/number theory/induction | 34 | 60 | Established lemmas and induction patterns, with coercion and tactic-debugging effort. |
| IMO/shortlist | 20 | 240 | Allow several hours for the hard tail, informed by the donor's geometry/topology durations; some remain unsuccessful. |

Weighted mean: **57.13 minutes**, rounded to **60 minutes**. These are professional-effort judgments tied to observed task-duration scales, not a mechanical conversion from score to hours. The human target is approximate 80% completion, not a claim that one hour guarantees a proof of every theorem. Some straightforward problems take minutes and some hard problems consume hours without success. The actual source does not identify how much effort this population needs for exactly 82.4%; that is the main uncertainty. The bounds re-run the weighted mean at each group's ends rather than halving and doubling the total. At 10, 40, 90, 60 and 240 minutes down the table's rows the mean is **36 minutes**; at 35, 90, 180, 90 and 360 it is **88 minutes**. The IMO and shortlist tail moves it most per attempt and the 130 MATH items most in aggregate, because they are more than half the set.

Because the recorded durations substantively calibrate the component scale, evidence is `transferred_timings`, method `estimated`, statistic `point_estimate`. The timing donor is **21 unaided task sessions (seven people × three)**, including unsuccessful attempts: attempts 21, subset all. Those are donor sessions, not a fictional human MiniF2F evaluation.

Performance is **match by target construction**: estimate effort for the human to deliver formal proofs at approximately the AI's completion level. It is not a measured head-to-head result and does not import the donor's 42% accuracy. Both target performers get the same formal statements and use Lean/mathlib without an LLM helper for the human; no comparison flag is added solely because duration is estimated or its timing donor differs. The supplied answers are explicit in the work unit, so this cannot be read as unaided informal contest solving.

### Model release and reproduction

The model's original Hugging Face history and retained release-tree inventory show complete numbered weight shards on **April 30, 2025**. This is a public model release, not merely the paper date. The registry model is `deepseek-prover-v2-671b`, company DeepSeek, reported active parameters 37B. It is separate from general-purpose V3 despite sharing architecture.

Install `tokenizers`; run `python research/deepseek-prover-v2/recompute.py --sources agent-work/sources/deepseek-prover-v2 --output /path/to/new.json`. The calculator reads original statement archives, predecessor JSONL, original README prompt and tokenizer; it never runs proofs or models. Output must be new and outside sources. The calculation also retains a non-CoT32 workload for an alternative setting; it is not an additional proposed row. Source hashes are retained in the output and manifest.
