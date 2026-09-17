# Physician time for the original Ayers forum reply

Recommended **120 seconds**, with **80–230 seconds** as the bounds. This estimates an ordinary physician's first forum reply at the original human quality and length. It does not estimate producing the longer, higher-rated AI answer.

## Work inspected

[Ayers et al. (2023)](https://jamanetwork.com/journals/jamainternalmedicine/fullarticle/2804309), Methods/Results and the example-response table, use 195 question–physician pairs. Questions average 180 words; first physician replies average 52 words, versus 211 for ChatGPT. The table's six examples concern a swallowed object, a head injury, a chemical splash, a lump, painful swelling and a lingering cough. The human replies are brief risk assessments, reassurance, warning signs or recommendations to seek examination. They are not comprehensive medical reports. The table summarizes the questions for privacy, so its shorter summaries cannot replace the original 180-word input mean. No time is recorded for these replies.

The target includes reading the supplied question, applying clinical knowledge, composing the short first answer and a brief check before posting. It excludes subsequent thread exchanges, obtaining an examination or records, prescribing, and coordinating care. The original study's preference for AI answers remains a separate performance result. Time is not scaled to the AI's 211-word output or adjusted upward until quality matches it.

## Timed calibration

[Tai-Seale et al. (2024)](https://jamanetwork.com/journals/jamanetworkopen/fullarticle/2817615), Table 1, reports three baseline cohorts before AI access. All three contribute rather than selecting one arm:

| T0 cohort | Replies | Read median (IQR), seconds | Reply median (IQR), seconds | Reply length median (IQR), characters |
|---|---:|---:|---:|---:|
| Immediate group, before activation | 713 | 26 (11–69) | 70 (38–122) | 214 (124–361) |
| Delayed group, before activation | 813 | 25 (10–67) | 71 (37–128) | 276 (154–457) |
| No-activation group, T0 | 2,154 | 21 (9–54) | 58 (28–124) | 210 (115–371) |

Its “Outcomes Assessment” defines read time as the interval from the last message selection to starting a reply, and reply time as reply start to send. These are EHR event intervals, not direct observation of continuous attention. The clinical setting covers refills, results, paperwork and general questions; input-message lengths are not reported. Component medians cannot establish a median total, and their weighted average would not recover a pooled median. No such statistic is calculated here.

[Ferguson et al. (2023)](https://medinform.jmir.org/2023/1/e43567/), Methods/Results, independently reports **3.83 minutes** per portal message from 2,061 messages timestamped by two physicians during February 2020–February 2021. The report does not specify timer start/end events or interruption handling. Its broader clinical portal work is useful context for several-minute messages, but is not the chosen forum duration and does not add 2,061 attempts to the calibration sample.

## Transfer and estimate

Use about **40 seconds** to read and interpret the 180-word question, then **80 seconds** to formulate, type and briefly check the 52-word reply. These are assumed activity budgets, not observed component means. The reading allowance corresponds to about 270 words/minute; the reply allowance to 39 finished words/minute including formulation. The inspected responses are short and often address one immediate concern, making extensive drafting or a literature search unnecessary for the target actually observed.

The clinical study's 58–71-second reply medians concern short responses of 210–276 characters. A 52-word English reply is usually somewhat longer; 80 seconds is a modest increase for the actual output quantity. This is not a linear character-count conversion, because thought and EHR actions also consume the source clock. The forum task removes clinical-record navigation and care-management workflow, while an unfamiliar question still needs interpretation. A 40-second reading allowance is more conservative than copying the portal study's 21–26-second read medians when the source does not report comparable input lengths.

The bounds are the two measured studies rather than a factor on the central. The low adds the portal study's own medians together, 21 seconds reading and 58 seconds replying: 80 seconds. The high is Ferguson's 3.83 minutes per portal message, 230 seconds, a measured mean over 2,061 messages for work that also carries the record navigation the forum task lacks. Neither is a confidence interval or a claim about every physician's reply time. The central estimate is 120 seconds by judgment, not the sum of measured medians or the time spent on a clinical encounter.

## Recommended fields and counts

| Field | Value |
|---|---|
| `human_time` | `120` |
| `human_skill` | `expert` |
| `human_time_scope` | `task_performance` |
| `human_time_evidence` | `transferred_timings` |
| `human_time_method` | `estimated` |
| `human_time_statistic` | `point_estimate` |
| `human_time_subset` | `all` |
| `human_attempts` | `3680` |

The 3,680 count is the number of distinct T0 clinical replies contributing to the calibration. Each has reading, reply and length measurements; count it once, not three times. This is neither a count of timed Reddit replies nor the 195 original quality comparisons or 585 rater judgments. The donor clinical messages have different content and workflow. Those transfer limitations belong in the notes; the estimated human task remains the original forum reply, so the donor alone does not establish a different-task comparison. The AI's `above` performance label should continue to describe the original forum comparison.

Suggested point note: “Human time estimates an ordinary 52-word first forum reply, calibrated from 3,680 pre-AI clinical messages; the EHR timings concern different questions and workflow. It does not estimate reproducing the longer AI reply.”

## Sources and reproduction

The original open-access XMLs are retained from Europe PMC as `tai-seale2024.xml` and `ferguson2023.xml`; `source-manifest.json` records their URLs, sizes and hashes. `ayers-paper.txt` is extracted from the original PDF supplied in the parent batch; its provenance and PDF hash are recorded in the manifest. `assumptions.json` stores the chosen activity budgets.

`recompute_human.py` requires Python 3.9+ standard library only. It verifies the retained source hashes, reads the three T0 rows directly from the original XML, counts unique contributing replies once, and applies the explicit assumptions. Use actual source and new output paths:

```sh
python3 -B /path/to/recompute_human.py \
  --sources /path/to/published/human-sources \
  --output /tmp/patient-message-human-replay.json
```

The script does not modify evidence or access any patient system. `human-calculations.json` is the retained output for review.
