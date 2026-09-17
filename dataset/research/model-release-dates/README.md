# Model release dates for the 78 undated registry records

*Created 2026-09-14 08:12.*
*Last revised 2026-09-14 09:06 — the 11 blanks resolved under Damon's no-blanks ruling.*

## TL;DR

All 78 model records that carried an empty `model_release_date` in the unified `models.csv` were
researched against primary sources. **All 78 are now dated**: 67 in the first pass, and the 11 the
first pass left blank under Damon's ruling of 2026-09-14 that the registry carries no blanks.
`dates.csv` carries one row per record: `model_id`, `model_release_date`, `model_release_source`
(the text written into the registry) and `basis` (what establishes the date). 73 of the 78 belong to the Codex registry and are applied by step 11 of
`../../../AI Compute vs Human Time unified/tools/build_unified.py`; the other five are owned by this
batch, and the two of them that could be dated — `srt-h-2025` and `monorace-racing-system` — were
written straight into this folder's `../../models.csv`.

Three findings worth carrying: the three MultiPL-T fine-tunes **do** have exact public revision
dates on Hugging Face, correcting `research/code-learning/multipl-t.md`, which says no first-public
date was established; the AlphaCode paper's arXiv v1 was submitted 2022-02-08 despite its 2203
identifier; and LeNet-5 and R2BERT cannot be dated to a day by any record, so each takes the first
of its publication month under the ruling.

## The convention used

`model_release_date` is the date the model first became publicly available, per `COLUMNS.md`.
These 78 records are mostly research artefacts whose weights were never distributed, so under
Damon's instruction the paper date is the release date, and the source field says so. Applied in
this order:

1. **Released weights**: the commit that published them (Hugging Face or GitHub), not the
   repository's creation date.
2. **Vendor or institution announcement**, where the model is a product or a demonstrated system
   rather than a paper: the page's own published-date metadata.
3. **Paper date** otherwise: the arXiv v1 submission date, or the journal's online publication date
   where there is no preprint. Where both exist, the earlier one is used and the later one is named
   in `basis`.
4. **Otherwise, under Damon's ruling of 2026-09-14, the date the capability is on the record.** The
   release date answers "when did this capability exist", so an unreleased or internal model takes
   the date the result it produced was announced; a model known only through the paper or
   evaluation that used it takes that publication's date; a fixed program rather than a trained
   model takes the date of the work it appears in; and a month-only publication takes the venue's
   or paper's actual day where a record gives one, otherwise the first of the month, with
   `model_release_source` saying so. No record is left blank.

Every date comes from a machine-readable primary record: arXiv abstract pages (submission history),
Crossref `published-online`, publisher page `datePublished` metadata, the Hugging Face commits API,
the GitHub commits API, or NCBI. Two publishers block automated retrieval — `openai.com` and
`jamanetwork.com` — and the three records that would have used them say so in `basis`.

## The 11 resolved under the no-blanks ruling

The first pass left these blank; the ruling of 2026-09-14 dates them. Each takes the date its
capability is on the public record, not a date its weights became downloadable.

| model_id | Date | What the date is |
|---|---|---|
| `openai-ns-2026-09-internal` | 2026-09-08 | OpenAI's announcement of the Navier-Stokes result this model produced. Never released. |
| `anthropic-internal-research-flt-2026-08` | 2026-09-04 | Anthropic's post announcing the Fermat's Last Theorem formalization this model produced. Never released. |
| `gector-peet-2025-unspecified` | 2025-10-05 | arXiv v1 of the PEET study, the only record of this configuration. |
| `github-copilot-2022-08` | 2022-10-25 | arXiv v1 of Mozannar et al., the study that used the production checkpoint. |
| `gemini-1.5-pro-naturalplan` | 2024-06-06 | arXiv v1 of the Natural Plan paper that ran the build. |
| `gemini-1.5-pro-hourvideo` | 2024-11-07 | arXiv v1 of the HourVideo paper that ran the build. |
| `amazon-sparrow-architecture-proxy` | 2022-11-10 | Amazon's Sparrow introduction, the announcement of the deployed capability the proxy stands for (`article:published_time`). |
| `binary64-affine-converter` | 2026-09-14 | Not a model: the date of the work it appears in, this dataset's own derivation note. |
| `pr2-geometric-towel-2010` | 2010-05-03 | ICRA 2010: Crossref dates the publication 2010-05 and the proceedings' conference 2010-05-03 to 2010-05-07, so the first proceedings day. |
| `lenet-5-original` | 1998-11-01 | Proc. IEEE 86(11), November 1998. No record gives a day, so the first of the month. |
| `r2bert-base-2020` | 2020-11-01 | Findings of EMNLP 2020, November 2020 in both the ACL Anthology and Crossref. No record gives a day, so the first of the month. |

Three of these were choices between two defensible dates, all resolved toward the ruling's
"when did this capability exist":

- **`github-copilot-2022-08` takes the study's arXiv v1, not Copilot's 2022-06-21 general
  availability.** The record is the undated August 2022 production checkpoint, not the product, and
  the GA date does not date those weights.
- **`pr2-geometric-towel-2010` takes 2010-05-03, not 2010-05-01.** Crossref's event metadata gives a
  day for the proceedings; the ruling prefers a real venue date over the first of the month. The
  same reasoning cannot rescue `r2bert-base-2020`, whose Crossref event record is itself month-only.
- **`binary64-affine-converter` takes this repository's note, not IEEE 754.** The arithmetic has been
  available since binary64 existed, but the ruling's clause for a fixed program names the work it
  appears in, and that work is the derivation note.

The eleven `models.csv` rows keep their `notes`, several of which still say the release date is
blank or not imputed. Those sentences are now stale and are for Damon to rule on separately.

## Judgment calls a reader might want to overturn

- **`cassie-100m-2022` is dated 2022-09-27, not 2025-08-05.** The controller's only full description
  is the 2025 sprint paper, but the record is explicitly the 2022 trials, and Oregon State announced
  the record run this controller set on 2022-09-27. Using the paper would place a 2022 artefact three
  years late. `basis` records both.
- **`openai-five-finals-2019` is dated 2019-04-13**, the day the checkpoint played the Finals
  publicly, rather than 2019-12-13, the Dota 2 paper. The checkpoint was never distributed and is
  named for that match.
- **`gpt-4-2023-03-01-internal` is dated 2023-03-15**, the technical report's arXiv v1. Its
  `2023-03-01` label is a snapshot date, not a publication, and the record's own notes say it does
  not establish availability.
- **`arcface-ms1mv2-r100` and `pigeon-cvpr2024` use the preprint, not the CVPR proceedings**, since
  both preprints are years earlier and the records' architectures are the preprints'.
- **`open-mistral-7b` is dated to the Mistral 7B weight release (2023-09-27)**, not to the API
  alias's appearance on La Plateforme, because the record's coefficient is the original 7.3B model.

## What was corrected in existing notes

`research/code-learning/multipl-t.md` states that no exact first-public release dates for the three
selected fine-tunes were established, and that repository creation dates do not establish those
revisions' publication. The Hugging Face commits API does establish them: the three pinned
revisions were pushed on 2023-08-14, 2023-08-14 and 2023-08-12. The note is not edited here; the
dates and their commit URLs are in `dates.csv`.

## How it is applied

Step 11 of `tools/build_unified.py` reads `research/model-release-dates/dates.csv` from this batch
and writes the date and source onto Codex-registry records whose `model_release_date` is blank. It
fails the build if the file names a model ID the registry does not have, or if a non-blank date in
the registry disagrees with the file — so this correction cannot silently overwrite a dated record,
and the five batch-owned IDs, which arrive already dated through the batch registry, are verified
rather than rewritten.
