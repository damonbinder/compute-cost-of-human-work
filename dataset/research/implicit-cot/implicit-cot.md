# Implicit chain-of-thought inference

Original [study](https://arxiv.org/abs/2405.14838) and [author artifact](https://github.com/da03/Internalize_CoT_Step_by_Step/tree/c2e3891d8d577beeaff03fa3b076d1e4db96cfe8). Retained code, logs and configurations are in sources. These are inference comparisons for the task-specific fine-tunes; their earlier training is excluded. The old lead's20-digit claim is unsupported: the artifact supplies successful4–9digit models and a partially internalized11-digit model, while20digits appears only as an additional dataset.

## Native workload

Parsed every input/target/prediction block after removing interleaved stderr progress displays. Verified reconstructed correct counts against all printed accuracies. Each multiplication set has1,000cases; each GSM8K set has1,319. The loader's printed1,000 does not replace the actual GSM8K count. Errors remain in compute. The11-digit output includes remaining intermediate arithmetic; those tokens are counted. Each historical log uses batch size1 and one returned sequence. The retained May24,2024 model implementation uses the ordinary generation configuration and does not set do_sample=True; explicit sampling was added in January2025. Describe the logged work as one autoregressive response, not a sampled response based on newer code. KV caching is enabled by the base configuration.

Retokenize the actual displayed input and generated text with the original GPT-2 vocabulary, preserving spaces and the answer marker, and add the input EOS separator. The May24,2024 training code removes CoT tokens up to—but excluding—the second separator. Fully internalized targets therefore begin with EOS followed by the answer. Every visible4/5/7/9-digit prediction and every nonempty GSM8K prediction begins exactly with ` #### `, consistent with that structure.

The historical double-EOS logits processor initializes its baseline before the first generated token, while the stopping criterion initializes after that token. If generation begins with EOS, the stopping criterion misses it; after the normal final EOS, the logits processor forces one extra EOS and only then does generation stop. Thus use **three hidden output EOS tokens** for the fully internalized rows, including the one empty GSM8K-small output as the same stopping-rule estimate. The partially internalized11-digit outputs start with arithmetic text, so use two. Sources are the retained May2024 train/model/utils files. The tokenizer omits EOS from displayed text; token IDs are not logged, so this remains a reconstruction. Keep the two-EOS alternative and a one-additional-token sensitivity. Underlying tokenizer boundary reconstruction can also differ slightly from the missing exact IDs.

The shared2P×(input+output) convention is an inference approximation, not an exact count of decoder input positions; in cached generation the final predicted token is not forwarded again. No task-specific claim of exact operation instrumentation is made.

For GPT-2 dimensions d,L,V and context capacity S, the tied-embedding parameter count is `L*(12*d*d+13*d)+V*d+S*d+2*d`:124,439,808 for small and354,823,168 for medium. Configurations establish the dimensions; counts are derived. FLOPs use2P times mean input/output workload. The approximation omits context-dependent attention and small non-matrix operations; the attention term is added back in `compute_flops` (`research/attention-correction.md`). No helper inference is present in the task execution. The calculator retains each case and a one-extra-special-token sensitivity.

Exact first public days of these task-specific checkpoint revisions were not established. Their base GPT-2 release is not assigned to the fine-tunes.

## Human multiplication estimate

The baseline is an ordinary adult attempting written long multiplication in conventional notation, using paper and pencil without a calculator and with normal checking. It does not select a cohort already achieving95%accuracy.

A closer original source is [Ganor-Stern2018](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2018.01316/full), Materials and Methods and “The Developmental Pattern in the Exact Calculation Task”. Twenty-five college students (mean age23.1;23female) each attempted twenty2×2-digit products, in two paper-and-pencil batches of ten. There was no time limit and calculators were prohibited. Batch elapsed times were divided by problem count. Adults averaged **18.12seconds per problem and62%correct**, with all problems included. These are a measured timing and measured accuracy for two-digit products; neither is an observation on4–11-digit products. The problem set excluded ties and operands ending in zero.

The component budget is roughly2seconds per single-digit product including carry and writing,1second per digit-addition when combining rows, another n²seconds for checking/corrections, and2nseconds for setup/transcription. This gives `2n²+n(n−1)+n²+2n =4n²+n`. At n=2 it predicts18seconds, closely agreeing with the independently located18.12-second study result. Retain the rounded central estimates70,110,200,330,500seconds for n=4,5,7,9,11. The calculator also retains the unrounded source-calibrated expression `(4n²+n)*(18.12/18)`. The bounds sit on the growth exponent rather than on the total, because the study pins the duration at n=2 and every remaining risk is in how fast the work grows with length. Write the duration as 18.12×(n/2)^b. The elementary-operation count itself—n² single-digit products and n(n−1) digit additions—grows as n², which is b=2 and reproduces the centrals. b=1.5 allows the per-operation pace to rise as the procedure becomes rhythmic over a long problem; b=2.5 allows the procedural and checking burden to grow with length, which is the amplification named next. Those two exponents give 51–103 seconds at n=4, 72–179 at n=5, 119–415 at n=7, 173–778 at n=9 and 234–1,286 at n=11. The bar widens with n because the extrapolation does. This is a mechanistic extrapolation from smaller written problems, not a measured long-product timing curve or a regression with an observed confidence interval. Larger products may amplify procedural and checking burden beyond the quadratic budget; the scenarios cover substantial variability rather than certify its bound.

The earlier [mental-multiplication study](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2016.00072/full) is background on component/carry burden, not the timing calibration. The new written evidence replaces the unsupported95%ordinary-adult accuracy assumption. It is not converted into a precise predicted accuracy at every length. The best directional comparison is **above** for all five AI settings: their73.9–100%exact accuracy on longer products exceeds the measured62%two-digit baseline, and extending the written algorithm is unlikely to improve ordinary-adult accuracy without extra training or specialist selection. This is a transfer judgment; differences between the sampled adult population, permitted checking and digit distributions limit it. In particular, the11-digit classification is less secure than the near-perfect shorter AI results. No measured human parity frontier is claimed.

AI reads reversed space-separated digits; human work uses conventional numerals and written intermediate work, flagged different_inputs_or_tools. The human target itself remains exact multiplication at the row’s stated digit length; the shorter study supplies timing and performance evidence, not a substitute human task.

## Human GSM8K estimate

Use the independently reviewed [GSM8K human study](https://link.springer.com/article/10.1007/s10994-026-07029-7):60seconds transfers its median five-minute/five-question batch duration;84% accuracy is on50 original questions. The allocation is an estimate, not an observed individual-question mean. Human calculators and the different question sample are flagged. The detailed existing source review is [here](../cost-of-pass/cost-of-pass.md#gsm8k-human-time). Both fine-tunes are below this baseline.

## Point results

## reas-implicit-cot-mult11

739/1000 correct; mean input25 and output76tokens including the stated separator reconstruction. Total101tokens ×248879616FLOPs/token =25136841216FLOPs. Human500seconds under the method above.

## reas-implicit-cot-mult4

1000/1000 correct; mean input11 and output14tokens including the stated separator reconstruction. Total25tokens ×248879616FLOPs/token =6221990400FLOPs. Human70seconds under the method above.

## reas-implicit-cot-mult5

996/1000 correct; mean input13 and output16tokens including the stated separator reconstruction. Total29tokens ×248879616FLOPs/token =7217508864FLOPs. Human110seconds under the method above.

## reas-implicit-cot-mult7

945/1000 correct; mean input17 and output20tokens including the stated separator reconstruction. Total37tokens ×248879616FLOPs/token =9208545792FLOPs. Human200seconds under the method above.

## reas-implicit-cot-mult9

988/1000 correct; mean input21 and output24tokens including the stated separator reconstruction. Total45tokens ×248879616FLOPs/token =11199582720FLOPs. Human330seconds under the method above.

## reas-implicit-cot-gsm8k-medium

460/1319 correct; mean input58.5353 and output7.2229tokens including the stated separator reconstruction. Total65.7581501tokens ×709646336FLOPs/token =46665030290.3FLOPs. Human60seconds under the method above.

## reas-implicit-cot-gsm8k-small

397/1319 correct; mean input58.5353 and output7.22441tokens including the stated separator reconstruction. Total65.7596664tokens ×248879616FLOPs/token =16366240525.4FLOPs. Human60seconds under the method above.

## Reproduction

`python3 -m pip install -r requirements.txt` installs the pinned tokenizer dependency. Run `python3 recompute.py SOURCE_DIR NEW_OUTPUT_JSON`; the output path must be outside the source directory and must not already exist. Retained calculations are excluded from their own source-hash input to keep reproduction stable.

## Contributing timing samples

The multiplication donor comprises 25 adults × 20 products = 500 attempts, recorded in 50 ten-problem timing batches. These are calibration observations on two-digit products, not 500 observations at each extrapolated length. The all subset includes incorrect answers in the elapsed batch time. The GSM timing donor count is unreported and remains blank; its all subset describes the reported batch timing, not the separate accuracy sample.
