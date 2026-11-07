---
id: PL-B7V7
title: Audit the line edit of docs/machine-abstraction.md and docs/machine-survey.md (#2048) section by section for dropped statements, qualifiers, requirements and reasons, as the MODEL.md audit did, and restore each
status: done
feature: repo-copy-edit
touches: docs/machine-abstraction.md, docs/machine-survey.md
added: 2026-11-07
closed: 2026-11-07
pr: 2051
verify: grep -q 'Inlet position is the variable that tests' docs/machine-survey.md && grep -q 'The line is decidable rather than a matter of judgment' docs/machine-abstraction.md
---

**Problem.** Audit the line edit of docs/machine-abstraction.md and docs/machine-survey.md (#2048) section by section for dropped statements, qualifiers, requirements and reasons, as the MODEL.md audit did, and restore each

**Why.** `#2048` (`PL-3K13`) line-edited both documents with the copy editor and checked the result only for dropped numbers, code names, citations and dates. On `docs/MODEL.md` the same edit, checked the same way, passed that check yet had dropped or weakened about 120 statements in 42 of 78 edited sections, found only when six review agents compared each section's old and new text (`PL-95SW`). The two machine documents were edited by the same tool and have not had that comparison.

**How.** Split both documents at their headings, at the fork of `#2048` and on `main`. For each section the edit changed, have a reviewer list every statement, qualifier, requirement ("must", "only", "never"), scope limit or stated reason present in the old text and missing or weaker in the new, quoting both. The brief the `PL-95SW` audit used is in `/mnt/project-files/v0.7.0/repo-copy-edit/audit-BRIEF.md`. Restore each finding in place; put a section back to its old wording where it lost three or more.

**Done when.** Every section `#2048` changed has been compared, and each statement the comparison found missing or weakened is back.

**What was found.** Three review agents compared each of the 31 sections `#2048` changed with its text before the edit. In the abstraction, 10 of 12 sections had lost or changed a statement, and two bold leads that other paragraphs cite ("The admission rule", "Two refusals") were gone. In the survey, 13 of 19 had: for example, the record that `Candries et al.` and `Hoffmann et al.` were once wrongly cited as evidence of practice, the owner's decision to wait for the machine abstraction before changing the default flow, and Meyer et al.'s vaporizer figures newly attributed to the Tec 6. The findings are in the project's shared folder, `v0.7.0/repo-copy-edit/audit-findings/machine-docs/`.

**What was done.** Fifteen sections that lost two or more statements, or whose cited bold lead was gone, are back to their earlier wording: seven in the abstraction and eight in the survey. The abstraction keeps the corrected count of the matrix entries that hold the fresh gas flow, the one factual fix `#2048` made. Eight single losses in other sections are restored in place. One finding was not taken: the survey's sources list once said ISO 80601-2-13 was the only standard the document names without saying what it requires, which was inexact, since ISO 5360 is named the same way.

**Generator check.** One mechanism, the copy editor dropping requirements, qualifiers and reasons, caused these losses. It is filed as `PL-F0Q2`, and the remaining copy edits wait for its fix (project owner, 2026-11-07).
