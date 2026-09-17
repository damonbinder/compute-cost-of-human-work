# Human learning time for the Latxa score transitions

**The human-learning estimate in this note is superseded.** On 2026-09-14 the
human side of every row it covers was re-estimated as the active hours to reach the
capability the run bought, read off a published hours-to-proficiency table, rather
than the hours to move a benchmark score. The current figures, the method and the
per-row arithmetic are in [skill-acquisition human learning time](../../skill-acquisition-human-time.md).
Everything else here — the endpoints, the task inspection and the compute
reconstruction — still stands.

Proposed central estimates: **500 active hours (1,800,000 seconds)** to reach about **45%** EusProficiency accuracy, and **1,000 hours (3,600,000 seconds)** to reach about **61%**. These are task-inspected learning estimates, not measured learning curves.

## Defined human target

The learner is an ordinary literate Spanish-speaking adult with negligible Basque, initially near the four-choice guessing baseline. This population makes the local Basque curriculum a relevant planning reference; it is not a universal estimate for every first language. The learner uses ordinary instruction, dictionaries and practice without AI. Practice teaches language and comparable question forms, not the answers to the held-out benchmark. At evaluation, the learner gets the same written questions, four options and five worked examples, without lookup or corrective feedback. The target is average accuracy across this question distribution, not passing every question, producing extended Basque prose, or obtaining C1 certification. Active learning includes instruction, study and formative practice; it excludes calendar gaps and a separate final benchmark sitting.

The retained native results are **25.9044% → 45.0184%** for Llama 2 13B → Latxa 13B v1.1 and **24.1633% → 60.6113%** for the corresponding 70B models. Both starting scores are effectively at the 25% guessing floor. We do not assign different prerequisite human learning to those small baseline fluctuations. Prior Spanish literacy is already present, analogous to comparing additional model training from an existing base rather than charging all human childhood learning.

## What the questions require

The [original dataset card](https://huggingface.co/datasets/HiTZ/EusProficiency) identifies 5,169 questions from 1998–2008 EGA initial tests. Each retained question has four choices. `question-inspection.json` preserves a seeded random sample of 60, chosen without looking at model successes: 19 primarily morphosyntax, 19 idiom/pragmatic replies, nine vocabulary/collocation, seven sentence meaning/paraphrase, and six orthography/standard forms. These are reviewer-assigned dominant demands, not official labels; some overlap.

Examples illustrate why a single grammar rule count would be misleading. Items 25 and 2858 test number/date forms; 1007 tests a common verb construction; 666 and 1554 require subordinating or relative structures. Items 1794 and 3603 distinguish concrete vocabulary, while 2778 and 4342 concern nonliteral expressions. Items 782 and 1050 require abstract paraphrases, and 4631 combines quantification and negation. The higher score needs broader coverage, but the lower score does not require mastery of all these topics.

For scale only, an idealized learner who knows some answers and guesses uniformly on everything else needs 26.7% known-answer equivalents to score 45.0%, or 47.5% to score 60.6%: `(accuracy−0.25)/0.75`. Real learners partly eliminate distractors, make mistakes and generalize across items, so these are **not mastery estimates, a CEFR conversion, or a score-to-hours formula**. They show why demanding full C1 competence would overstate the target.

The [original 2008 rules](https://www.euskadi.eus/bopv2/datos/2008/01/0800180a.pdf), Article 2, specify 100 initial-test items, of which 12–18 test listening with three options. Remaining items have four options and wrong answers incur no penalty. The nominal qualifying threshold was 75, adjustable to admit about half the candidates. Written and oral phases follow separately. Thus neither the full exam threshold nor the later 65-item format is a direct threshold on the collected written-only questions. The two target percentages do not establish a qualification.

## Learning evidence

[HABE's curriculum](https://www.habe.euskadi.eus/curriculo-basico-de-ensenanza-de-euskera-a-personas-adultas-heoc/webhabe00-edukiak/es/) supplies planning hours for instruction plus personal learning. Its increments through A1/A2/B1/B2/C1 are 200/300/400/600/750 hours, giving cumulative 200/500/900/1,500/2,250 hours. They cover all four language skills and depend on starting level. The retained 2015 Spanish curriculum, printed page 13, verifies both components visually. Its language-content tables put common vocabulary and frequent synonyms at A2/B1 (printed 89/118), with broader general vocabulary and numerous synonyms at B2 (152). These are useful content and scale references; they do not say what score a student obtains on EusProficiency.

[Perales and Cenoz 2002](https://www.researchgate.net/publication/249025395_The_Effect_of_Individual_and_Contextual_Factors_in_Adult_Second-language_Acquisition_in_the_Basque_Country), “The Study,” pp. 4–5, report 411 adult learners in nine schools, described as lower-intermediate/B1. Instruction-dominant learners had received 300 classroom hours; the current course contributed about 80. Other learners entered that level with more prior exposure and fewer lessons. The relevant subgroup size and personal-study totals are unspecified. Outcomes are interviews, writing and teacher/self assessments, not this MC test. The author's [companion original paper](https://ojs.ehu.eus/index.php/psicodidactica/article/download/134/130/0), p.36, confirms the cohort/level and describes a strong oral-communication component. This evidence makes lower-hour routes plausible, but does not establish 300 total active hours to B1 or to either target score. It is a contextual check, not a numerical calibration used in the main recipe.

## Proposed focused learning route

The central recipe deliberately selects written-recognition work instead of charging an entire qualification. Component times below are judgments; their contents are grounded in the inspected tasks.

| Active learning component | Hours | Basis for the allowance |
|---|---:|---|
| Reading and core language foundation | 300 | Recognize common words and function words, case endings, basic auxiliary agreement, word order and everyday short sentences. This is a selected portion of the 500-hour introductory four-skill planning allowance. It removes extensive conversational fluency, listening comprehension and productive composition practice; some guided sentence production remains useful for learning forms. The 300 is not the study's 300 classroom hours reclassified as total effort. |
| Intermediate written recognition and practice | 200 | Consolidate frequent written forms, subordinate/relative constructions, standard spelling, common lexical contrasts and routine conversational responses represented in the sample. This supports a limited but useful subset of the item distribution; it does not presume command of the harder idioms and abstract paraphrases. |
| Additional broad written usage | 500 | Expand beyond common vocabulary to less frequent collocations and idioms, practice contextual appropriateness and abstract paraphrase, and consolidate interacting agreement/clause distinctions. Broad, varied reading and spaced correction are needed for unfamiliar examples, rather than memorizing a short list of grammar rules. |

The lower endpoint uses the first two components: **300 + 200 = 500 hours**. The higher uses all three: **300 + 200 + 500 = 1,000 hours**. The 500-hour expansion is a broad learning budget selected for this more demanding recognition target, not a constant number of hours per additional percentage point. Its size could change substantially with learner background and instruction quality. The route has no claim to be the optimal training curriculum, nor is it a prediction that every learner reaches the endpoint at that hour.

The first 500 hours are below the full B1 planning allowance; 1,000 hours is below the full B2 allowance. That is intentional for focused recognition without certification in productive or listening skills. These comparisons are cross-checks, not definitions of the target CEFR level.

## Alternatives and limits

For the 45% target, use **250–1,000 hours** as a route sensitivity: the lower scenario permits highly focused reading/form study and effective distractor elimination; the upper permits slower vocabulary acquisition, forgetting and a less specialized course. For the 61% target, use **500–2,000 hours**: an efficient focused route may approach the lower estimate, while weaker transfer of textbook knowledge to idioms and contextual contrasts may require prolonged reading and practice. These are assumptions, not confidence intervals or established lower/upper bounds. The upper scenario remains below the full C1 planning allowance, but that allowance itself is not a guaranteed maximum.

The important missing evidence is a cohort with initial near-chance scores, logged active learning and repeated held-out tests from this item distribution. None was found. A qualification's scheduled hours and a four-skill assessment cannot supply that curve. The two proposed points are still useful as explicitly estimated matched-endpoint learning comparisons, with this limitation attached to the times rather than hidden in the performance label.

## Recommended fields

Use `human_skill=typical`, `human_time_scope=skill_acquisition`, `human_time_method=estimated`, `human_time_evidence=assumed`, `human_time_statistic=point_estimate`, `human_time_subset=not_applicable`, and `human_attempts=not_applicable`. The central duration is a selected learning route based on planning allowances and task inspection. The 411-person paper is contextual evidence, not a measured timing sample for the numerical estimate; do not populate human_attempts with 411.

Use `performance_vs_human=match` because the human learning target explicitly reproduces the observed ending MC accuracy. State that this is an assumed matched-quality human endpoint, not an observed learner score. `comparison_issues=different_inputs_or_tools` records explicit human instruction/references versus continued corpus training. No `different_assessment` follows merely from the curriculum or empirical study using other tests: the specified target assessment is the same retained question distribution.

Concise proposed note: “Human learning time assumes focused written recognition by a Spanish-literate adult starting near chance. Curriculum hours guide scale; no measured learning curve maps hours to these scores. Human instruction and practice differ from corpus training.”

## Reproduction

Use Python 3, standard library only:

```
python /path/to/research/human-learning/recompute-human.py /path/to/sources/human-learning /path/to/new-output
```

Keep the assumptions and question-inspection files beside the script. It verifies the retained source hashes, sample identities and native scores, then recomputes the explicit hour sums, unit conversions and separate guessing diagnostic. It writes new outputs and does not run a model or modify source data.
