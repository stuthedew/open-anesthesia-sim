---
id: PL-B7V7
title: Audit the line edit of docs/machine-abstraction.md and docs/machine-survey.md (#2048) section by section for dropped statements, qualifiers, requirements and reasons, as the MODEL.md audit did, and restore each
status: untriaged
feature: repo-copy-edit
touches: docs/machine-abstraction.md, docs/machine-survey.md
added: 2026-11-07
---

**Problem.** Audit the line edit of docs/machine-abstraction.md and docs/machine-survey.md (#2048) section by section for dropped statements, qualifiers, requirements and reasons, as the MODEL.md audit did, and restore each

**Why.** `#2048` (`PL-3K13`) line-edited both documents with the copy editor and checked the result only for dropped numbers, code names, citations and dates. On `docs/MODEL.md` the same edit, checked the same way, passed that check yet had dropped or weakened about 120 statements in 42 of 78 edited sections, found only when six review agents compared each section's old and new text (`PL-95SW`). The two machine documents were edited by the same tool and have not had that comparison.

**How.** Split both documents at their headings, at the fork of `#2048` and on `main`. For each section the edit changed, have a reviewer list every statement, qualifier, requirement ("must", "only", "never"), scope limit or stated reason present in the old text and missing or weaker in the new, quoting both. The brief the `PL-95SW` audit used is in `/mnt/project-files/v0.7.0/repo-copy-edit/audit-BRIEF.md`. Restore each finding in place; put a section back to its old wording where it lost three or more.

**Done when.** Every section `#2048` changed has been compared, and each statement the comparison found missing or weakened is back.
