# Noy–Zhang professional writing

Ten task comparisons use the study’s raw ChatGPT outputs and unaided professional responses. This is not the human-plus-ChatGPT treatment’s time saving. Consulting tasks remain outside this tranche because their six pasted reference documents require recovery.

## Sources

- Noy and Zhang, [original paper](https://shakkednoy.com/Noy%20Zhang%20NBER%20SI.pdf), and [supplement](https://shakkednoy.com/ChatGPT_SM.pdf), especially C.5 and Table S.3.
- [Public replication package](https://osf.io/xd7qw/): original surveys, grading tables and scripts. `source-manifest.json` records retained hashes; OSF listings retain file download URLs.
- `fullsurvey.csv` is a numeric/categorical analytical extract. `fullsurvey_fulltext.csv` removes unnecessary network, location and contact columns. The two extract provenance files record original and derived hashes. Original downloads are retained outside the product in the batch’s source archive.

The cleaned participant sample reproduces the paper’s 453 people. Following the original main-text script’s grader-list export and supplementary Python analysis reproduces Table S.3: 67 unique ChatGPT answers, 408 completed ratings, 122 graders, overall mean4.879901960784314. Its “Mean Human Grade” column concerns people who used ChatGPT, so it is not our unaided baseline.

## Human time

Start from the original consent, completion, duplicate, manual quality and prior-grader exclusions in `clean.do`. Join the full-text/tool responses by the selected survey response ID, checking participant, occupation and start date; do not join an arbitrary earlier survey by participant ID. Keep the linear and convex incentive arms; exclude the arm forced to stop after15minutes. Retain first tasks without reported ChatGPT use and second tasks explicitly reported as no use. The first-task question was only asked after reporting second-task ChatGPT use; following the original appendix, a skipped first-task response is treated as no use. This relies on the survey’s elicitation assumption, not direct confirmation for every participant.

Exclude reported other AI writing tools, Grammarly and free-text You.com use on either task. AI writing and Grammarly codes1/3 agree between the data dictionary and survey; other tool code labels conflict with the analysis code, so no finer classification is inferred from them. Ordinary search, word processors and provided examples remain permitted human aids. Self-reports may miss unreported assistance.

Sum the four reported time components—brainstorming, rough drafting, editing and other work—and convert minutes to seconds. Use the arithmetic mean among eligible, graded responses for each occupation/task. This is `task_timings` with `other_calculation`, not an estimated work-rate conversion. Human attempts count those responses. Participant exclusions remove invalid/noncompliant submissions; no grade threshold is applied to the retained attempts.

`summary.json` also gives medians and automatic task-page means. The self-reported totals reproduce the paper’s timing construct and include claimed planning/editing; they are not stopwatch measurements of active work. The page timer is often materially shorter, especially for marketing. Neither is silently substituted for the other. The same person can contribute both tasks; rows and observations are therefore correlated.

## Performance

Use overall professional quality grades on the original1–7 scale. Both human and AI answers use the same raw grader pool used in the paper’s pure-ChatGPT analysis. Average repeated ratings within grader/answer, then across graders, then equally across answers. The human scores concern exactly the timed human cohort. Match each displayed graded essay to the selected response’s actual task submission, allowing only HTML/whitespace and quote-format changes. Exclude ratings of another occupation/survey, the opposite task, an AI-assisted retry, or missing displayed text. An ungraded timed response is excluded from this paired cohort. The mapping audit retains1,355exact and8quote-format matches, and identifies23excluded slots; no actual low-quality answer is discarded merely for its grade. These are our task-specific reanalyses, not reported headline treatment effects.

Eighteen completed AI ratings are attached to the wrong email prompt: an AccureCo reorganization answer under the WorkCo virtual-office prompt, or vice versa. The same text also appears under its correct prompt. `misplaced-ai-ratings.json` preserves these cases. Exclude only the misplaced ratings, retaining all unique answers and their correct-prompt ratings. The occupation-level published table above remains separately reproduced without this repair.

Grant-cover-letter scores differ only modestly (about0.2–0.3points) and are classified broadly comparable. The other tasks show roughly1.2–2points higher AI scores and are classified above. These labels summarize substantive differences; they are not statistical equivalence tests. Humans had ordinary web/writing tools, product images for marketing and linked examples for grant/analysis tasks. ChatGPT received copied task text; these input differences are flagged. The manager cohort’s reorganization prompt itself says “HR professional”; this is retained in its description.

## Compute

C.5 says the authors pasted the complete task prompt into a blank ChatGPT chat and collected varied responses by regenerating or repasting. Consulting additionally pasted three documents; it is excluded here. The retained raw answers provide actual response lengths, rather than the requested400/500-word limits. One generated answer is the work unit; grading replications do not multiply its generation cost.

Render the stored task and answer HTML to text, normalize whitespace and tokenize with the retained official `cl100k_base` ranks. The original request strings, tokenizer and hidden system message are unavailable. Add50system/wrapper positions, consistent with the early-ChatGPT patient-message recipe. Different copy/paste formatting and regenerated-prefix caching remain assumptions; count the full prefix for each answer because no native cache records exist.

Use the existing early-ChatGPT175B dense-parameter proxy:350billionFLOPs per primary token. This is not a disclosed GPT-3.5 size. It is shared with the patient-message model record, rather than inferred from later GPT-3.5-Turbo experiments.

The field window, 27 January to 24 February 2023, straddles the 13 February 2023 switch of the ChatGPT product to the Turbo backend, so which model produced these answers is a live question. They stay on the December record. C.5’s pure-ChatGPT answers were produced by the authors, not by participants, so the participants’ session dates do not date them, and the replication package records no generation date. What it does record is when each answer first reached a grader, which bounds generation from above: over the retained grader pool, excluding retries and the consultant occupation, 51 of the 62 unique answers were in front of a grader before 13 February 2023, the earliest on 6 February. The remaining 11 first appear between 13 and 18 February, which is an upper bound and not a date. So the generation these rows price is davinci-lineage, and `research/model-priors/openai.md#chatgpt-backend-2022-23` scopes that record to 30 November 2022 through 12 February 2023, with a 60B rather than 12B low bound on active parameters.

Include the launch-era moderation helper using the same explicit recipe as [patient-message research](../patient-message/patient-message.md):1.3B parameters, one input and one output scan, four extra positions, `p50k_base`. The original moderation paper describes a lightweight GPT decoder but does not disclose its size or actual per-chat routing. These are assumptions, not measured calls. Text tokens total primary and helper positions; compute applies350billion and2.6billionFLOPs/token separately. Do not multiply the combined token count by the primary coefficient.

`task-texts.json` retains each unique answer’s text, prompt, token breakdown and grade; `summary.json` retains per-task means. Material sensitivity cases are the primary model size (7/44/175/350B), system/wrapper allowance (0/50/200), alternate primary tokenizer, moderation size and number of scans, and automatic versus self-reported human times. No confidence interval is inferred from those scenarios.

## Reproduction and remaining review

Run `recompute.py --sources PATH --output NEW_DIRECTORY` with Python, pandas, numpy, openpyxl and tiktoken. It uses retained token ranks and makes no model/API calls. The initial reliability-filter reconstruction is retained as a diagnostic; the final candidate uses the published raw-ChatGPT grader pool for both groups, not an asymmetric reliability filter.

Independent review corrected the source-response join and human grading-slot mapping. Root replay reproduces the corrected outputs. The early-ChatGPT model record uses first public family availability; the study does not identify its January–February 2023 backend revision, and the grading dates that place the answers before the 13 February 2023 Turbo switch are in Compute above. No new parameter measurement is inferred.
