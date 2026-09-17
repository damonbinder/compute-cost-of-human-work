# Human baseline review for phototest.tif

An 80-second central estimate is defensible for an ordinary computer user using a text editor and checking the result, but the proposed 66 seconds of typing plus 15 seconds for everything else understates initial reading and proofing. The actual image supports a more suitable calculation because much of its text repeats.

The inspected 640 × 480 image is clear black print with 60 words, one two-digit number, simple punctuation and eight printed lines. After whitespace normalization it contains 284 characters. The 45-character sentence “The quick brown dog jumped over the lazy fox.” occurs four times consecutively. Type the introductory text and that sentence once, then copy and paste the sentence three times. Only 146 characters need fresh entry. Preserve text and punctuation; reproducing the image's line wraps is not required for the normalized-text comparison.

[Dhakal et al.](https://userinterfaces.aalto.fi/136Mkeystrokes/) report 51.56 standard five-character words per minute (SD 20.20), with 1.167% mean uncorrected character error. Participants read and memorized each sentence before typing. Timing runs from first to last keypress, so it excludes initial reading. The speed includes corrections made during typing; multiplying it by a keystrokes-per-character factor would double-count those edits. Their source population is self-selected, mainly young people interested in typing, not a representative sample of all adults.

Use the measured speed as a transferred work-rate input, not a human timing observation on this image:

| Component | Seconds | Basis |
|---|---:|---|
| Fresh entry | 33.98 | 146 / 5 / 51.56 × 60 |
| Initial reading | 15 | 60 / 238 × 60 = 15.13 seconds using the [original reading-rate meta-analysis](https://biblio.ugent.be/publication/8647789); transfer to this short image |
| Selecting and pasting three repeats | 10 | Allowance for ordinary editor operations and confirming repeat count |
| Final comparison and correction | 20 | Allowance for checking this short, clear source; not a measured proofreading rate |
| Total | 78.98 | Round to 80 seconds |

Without the copying shortcut, typing all 284 characters requires 66.10 seconds at the same rate; adding initial reading and checking gives 101.10 seconds. This is a useful alternative workflow, not the observed population mean.

Inverting mean WPM does not produce mean completion time. Here the rate's coefficient of variation is 0.392. A second-order inverse-rate approximation increases the typing component by about 15.35%, putting the copying workflow at 84.20 seconds and fresh typing at 111.24 seconds. That approximation is a sensitivity calculation, not a fitted speed distribution or a recovered timing statistic. A point estimate around 80 seconds remains appropriate; do not label it `mean`.

Use a 60–170-second sensitivity range. About 60 seconds represents a fast, copying workflow at the paper's approximate 90th-percentile speed (78 WPM), with 10 seconds reading, 7 seconds copying and 20 seconds checking. About 170 seconds represents fresh typing at its approximate 10th-percentile speed (26 WPM), with 15 seconds reading and 25 seconds checking. These are workflow/population scenarios, not a confidence interval.

The AI's exact output can be checked on this one image. The human target is a checked transcription at comparable quality; no human trial on this image establishes exact accuracy or proves that 20 seconds of checking removes every error. The 1.167% source error rate is unproofread residual error in a different task and must not be described as the post-check human score here. A `match` classification is by the estimated reproduction target, stated explicitly.

Recommended human fields: `human_skill=typical`, `human_time=80`, `human_time_statistic=point_estimate`, `human_time_evidence=transferred_timings`, `human_time_method=estimated`, `human_time_subset=all`, blank `human_attempts`. The typing donor has 2,534,400 sentence trials (168,960 × 15), while the reading meta-analysis's passage-attempt count is unrecovered; the combined count is therefore blank. An estimated baseline alone does not require a comparison-issue flag.

Reproduce with `python3 research/ocr/review_human.py agent-work/sources/ocr /tmp/ocr-human-review-new.json`. The standard-library calculator reads retained text and assumptions and refuses to overwrite an existing output.
