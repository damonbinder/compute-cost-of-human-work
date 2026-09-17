# Human learning estimates

**The human-learning estimate in this note is superseded.** On 2026-09-14 the
human side of every row it covers was re-estimated as the active hours to reach the
capability the run bought, read off a published hours-to-proficiency table, rather
than the hours to move a benchmark score. The current figures, the method and the
per-row arithmetic are in [skill-acquisition human learning time](../skill-acquisition-human-time.md).
Everything else here — the endpoints, the task inspection and the compute
reconstruction — still stands.

This note documents the Kotlin, OCaml and Racket learning estimates. The five Python learning estimates are in [Python learning estimates](../python-learning-review/python-learning.md). These are estimates for ordinary adult learners with the starting skills specified below. None of the sources measures hours to the stated HumanEval score. The target is one independently written function per unseen problem, scored against hidden tests, without an AI assistant, solution lookup or execution feedback during assessment. Normal textbooks, instruction, code execution and feedback are allowed during learning. The recorded time includes that learning and practice, not a separate final examination. A learner who never reaches the target is outside this conditional duration estimate; no completion probability is established.

HumanEval asks for short functions from descriptions and examples. Inspection of the original [164 problems](https://github.com/openai/human-eval/blob/master/data/HumanEval.jsonl.gz) found elementary expressions, list filtering and accumulation, string processing, nested loops, elementary number theory and multi-step edge-case handling. Examples inspected include IDs0,1,2,3,7,10,20,25,30,40,50,60,70,80,90,100,110,120,130,140,150,160. A score of13% does not require13% of a programming degree, and49% does not establish employability. Random guessing is not a useful route to passing arbitrary function tests; unlike multiple choice, there is no25% or50% chance baseline to subtract.

## Timing and curriculum anchors

* [Cornell CS3110 warmup](https://www.cs.cornell.edu/courses/cs3110/2020sp/a0/) reports mean6.4hours, SD3.4, on a similar easier assignment in the previous year. The2020 task is three documented/tested functions: date validation, Collatz iteration and generalized Fibonacci; it uses material from lectures1–4. The [2019 syllabus](https://www.cs.cornell.edu/courses/cs3110/2019fa/syllabus.html) requires earlier programming courses and reports10–12median weekly assignment hours. Neither timing is an entire language-learning duration.
* [JetBrains Kotlin Koans](https://play.kotlinlang.org/koans/overview) targets Java programmers and describes learning syntax/idioms in a few hours, based on its surveys. This is not a timed HumanEval study; we treat the numerical duration below as assumed, rather than treating that promotional phrase as a measurement.
* [UW CSE341's2020 calendar](https://courses.cs.washington.edu/courses/cse341/20sp/calendar.html) introduces Racket after students have studied StandardML. The first Racket assignment spans basic functions/collections and more advanced streams/macros. It supports the scope of a short transfer module, not the conversion of calendar days to active hours. Prior ML experience makes it an easier transfer than our central Python/Java baseline.

University learners are more selected and have stronger support than the ordinary learners targeted here. The ranges allow slower acquisition, less support and differences in prior mathematical fluency. They are sensitivity scenarios, not confidence intervals. Formal tutoring/teacher preparation is not added as learner time. Actual score-linked learning curves would be a substantial improvement.

## Point estimates

| Point suffix | Starting skills and additional learning | Central hours | Sensitivity hours |
|---|---|---:|---:|
| kotlin7b | Already writes short Java/Python programs and some Kotlin, targeting26.09% initially. Refresh Kotlin functions, nullability, strings/collections and idioms with Koans, then practice docstring-to-function problems. Budget roughly one working day; no Android/app-development curriculum. |8|3–24|
| mplt-ocaml1b | Already writes basic Python functions but almost no correct OCaml. Introductory OCaml expressions/types/functions/list recursion plus short exercises: one Cornell warmup-sized practice block and several hours of instruction/review. Target9.7%, not general functional-programming proficiency. |10|4–30|
| mplt-ocaml15b | Already solves a range of short Python problems and has rudimentary OCaml. Add types/options, list/string operations and recursion, then mixed unaided function-writing practice. About two initial assignment-sized practice blocks plus instruction/review. |20|8–50|
| mplt-racket15b | Already solves short Python programs and some basic Racket forms. Improve Racket list/string library use, recursion/higher-order operations and translating a specification into a complete function. One focused transfer module; no interpreters or advanced macros. |12|4–35|

The hours are selected from these content and workload comparisons. No numerical score is multiplied by hours, and differences between rows are not fitted to an assumed smooth learning curve. In particular the two CodeLlama rows are additional practice from different starts; their values need not equal differences between the three Codex estimates. The matched human endpoints are assumptions to be tested, not observed human benchmark results.

## Comparison conditions

All nine human endpoints target unseen problems and first-submission correctness. MultiPL-T selects model checkpoints using the assessment benchmark, unlike that assumed human protocol; those three rows also flag different_assessment. Estimated hours and lack of a measured human learning curve do not themselves establish a different assessment or population. The concrete difference is how capability is acquired: human learning includes instruction, explanations and execution feedback during practice; AI learning uses each study’s training corpus and checkpoint-selection process. `different_inputs_or_tools` records this distinction for all nine rows. The Code Llama rows target Python function writing as one capability acquired during broader model training; they do not assign human time for mastering all its other languages or long-context abilities. That scope is explicit, without asserting that the compared Python endpoint is a different task.

## Direct Racket teaching anchor

[UW CSE413 Spring 2021](https://courses.cs.washington.edu/courses/cse413/21sp/calendar/lecturelist.html) devotes its first six 50-minute lectures to Racket basics, lists, functions, let, tail recursion and map/filter: five scheduled contact hours. This supports a focused transfer module plus practice for someone who already programs; it does not measure time to the 11.8%–21% HumanEval performance. The 12-hour Racket estimate remains plausible, with an independently considered 8–50-hour learning-route scenario. Later interpreter/advanced-language material is not required for the stated modest target. Original course pages and inspected benchmark prompts are retained in agent-work/sources/learning-duration-review/.

## Contributing timing samples

The five Python estimates use separate task-inspected learning budgets, documented in [Python learning estimates](../python-learning-review/python-learning.md); their human_attempts and human_time_subset are not_applicable. The OCaml estimates transfer Cornell assignment timings. Their source does not provide the contributing response count, so human_attempts is blank and human_time_subset is all. These are assignment donors, not HumanEval learners. Kotlin and Racket also use assumed durations and retain not_applicable.
