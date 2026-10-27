# Blind review findings, coded from pull request descriptions

`docs/blind-review-findings.tsv` lists every blind generalist review finding that
the descriptions of 41 merged simulator pull requests describe, one row per
finding. It was coded on 2026-10-26, before any merged `Blind-review:` record
used the per-pass form that `PL-0BRY` added. Every record merged by then gave
only totals for all passes together, so this table is the only per-finding data
from that period (`PL-D29S`).

From now on, `uv run python tools/blind_review_report.py` reads each pass from
the `Blind-review:` records themselves. Use this table as a baseline to compare
that report against, not as a source to extend.

## What it covers

The rows cover every pull request merged on `main` after `#1767` and up to
`#1863` that owed a blind review pass and carried a `Blind-review:` record:

- 26 pull requests that ran two passes: #1772, #1775, #1778, #1782, #1784,
  #1798, #1806, #1808, #1817, #1819, #1826, #1827, #1829, #1831, #1833, #1835,
  #1836, #1837, #1840, #1841, #1853, #1855, #1860, #1861, #1862 and #1863.
- 15 pull requests that ran one pass: #1766, #1773, #1774, #1777, #1779, #1792,
  #1797, #1805, #1812, #1813, #1815, #1816, #1852, #1856 and #1858.

`#1765` owed a pass and has no record, so it has no rows.

## How each column was coded

A subagent read each description and coded the rows. The session that ran it
checked six rows against the descriptions, which were all six of the pass-2
findings counted as new and blocking or should-fix. All six matched.

- `pr` is the pull request number. Its squash commit on `main` carries the
  description as its body, which
  `git log -1 --format=%b <commit>` prints.
- `pass` is 1 or 2, or `?` where the description does not say which pass found
  the finding.
- `finding_label` is the reviewer's own label, such as `F2`, or `-` where the
  description gives none.
- `severity` is the reviewer's severity: `blocking`, `should-fix` or
  `optional`. It is `?` where the description does not give it.
- `outcome` is what the authoring session did with the finding: `fixed`,
  `filed` or `rejected`. This is the author's own judgment, not an independent
  check.
- `repeat_of` names the pass-1 finding that a pass-2 finding repeats, such as
  `1F3`, or `1?` where that pass-1 finding has no label. It is `-` otherwise. A
  pass-2 finding counts as new only because its description does not say it
  repeats, so "new" is an inference from what the description leaves out.
- `category` is the kind of fault:
  - `code-bug`: the code behaves wrongly.
  - `missing-guard`: an input or edge case that the code failed to refuse or
    handle.
  - `test-gap`: a test that is missing, vacuous, or tests the wrong thing.
  - `doc-claim-wrong`: a document, docstring or comment that states something
    false or overstated.
  - `doc-unclear`: wording that misleads without being false.
  - `clinical-accuracy`: a clinical or scientific value, unit or reference
    claim that is wrong.
  - `process`: a record, trailer or item brief.
  - `other`.

  Where two categories fitted, the coder picked one. For example, a
  misleading learner-facing banner is coded `doc-unclear` and not
  `clinical-accuracy`.
- `target` is where the fault was: `simulator-code` (`src/`),
  `simulator-tests`, `MODEL.md-or-README`, `apparatus` (`tools/`, `bin/`,
  `subprojects/`, `.claude/`, and documents other than `docs/MODEL.md`), or
  `?`.
- `summary` is one short sentence.
- `body_line` is the line in the squash commit's body where the description
  states the finding.

## What the rows cannot show

- 29 of the 111 rows from two-pass pull requests have `pass` set to `?`.
- Five one-pass pull requests found nothing, so they have no rows: #1777,
  #1812, #1813, #1815 and #1856. The table therefore names 36 pull requests,
  not 41.
- 57 of the 133 rows have no severity.
- The descriptions count a fault that both passes found in different ways.
  #1775 and #1826 count it once, and the rest count it once per pass. So a
  pull request's row count can be larger than the findings total in its record.
- #1829's record is not internally consistent. It gives 7 findings, but 7 fixed
  and 1 filed, because one finding was both fixed and filed.
- A fault that neither pass found does not appear here at all.

## What the rows showed on 2026-10-26

In the two-pass pull requests, 41 findings can be traced to pass 1 and 41 to
pass 2. Of pass 2's 41, 26 repeat a pass-1 finding and 15 are new. The 15 new
ones are 6 should-fix, 8 optional and 1 of unknown severity, and none is
blocking. The 6 new should-fix findings come from 6 different pull requests.

A Lincoln-Petersen capture-recapture estimate from those counts is
41 × 41 / 26 ≈ 65 faults. The two passes found 56 distinct faults, which
leaves about 9. **That figure is a lower bound, not a point estimate.** The
estimate assumes the two passes find faults independently. They do not: both
run the same model on the same brief, so they tend to find, and miss, the same
faults, and that pushes the estimate down. The 29 findings with no recorded
pass are left out of it as well.

The literature on software inspections points the same way. Briand, El Emam,
Freimut and Laitenberger evaluated capture-recapture models for estimating how
many defects an inspection leaves. They recommended a model that lets faults
differ in how easily they are found, with its Jackknife estimator. A record of
the same authors' work reports that with fewer than four inspectors, no model
was accurate enough, and that the estimates could be far too low. Here there are
two passes. (L. C. Briand, K. El Emam, B. G. Freimut, O. Laitenberger, "A
Comprehensive Evaluation of Capture-Recapture Models for Estimating Software
Defect Content", IEEE Transactions on Software Engineering 26(6):518-540, 2000,
doi:10.1109/32.852741.) The session that wrote this note could not reach the
full text. The four-inspector finding was checked only against a repository
record of the authors' work, so check it in the published paper before quoting
it further.
