---
id: PL-T9S5
title: Audit the line edit of docs/ARCHITECTURE.md (#2044) section by section for dropped statements, qualifiers, requirements and reasons, as PL-B7V7 did for the machine docs, and restore each: #2044 was checked only for dropped names, numbers and item ids, the same gap that lost statements in the MODEL.md, machine-doc and interface-provenance edits
status: untriaged
feature: architecture-md-structure
added: 2026-11-07
---

**Problem.** Audit the line edit of docs/ARCHITECTURE.md (#2044) section by section for dropped statements, qualifiers, requirements and reasons, as PL-B7V7 did for the machine docs, and restore each: #2044 was checked only for dropped names, numbers and item ids, the same gap that lost statements in the MODEL.md, machine-doc and interface-provenance edits

**Why.** `#2044` (`PL-KGY1`) line-edited every section of `docs/ARCHITECTURE.md` with the copy editor. Its pull request says what was checked: that every module, function and file name dropped from one place is still given elsewhere, and that only eight item ids and four dates left the document. Nothing compared statements. On `docs/MODEL.md` the same check passed while about 120 statements were lost or weakened (`PL-95SW`), and the machine documents (`PL-B7V7`) and `docs/interface-provenance.md` (`PL-S6WZ`) lost statements the same way.

**How.** This runs before the restructure, `PL-SVGH`, on the same branch. The line edit kept every heading, so each section can be compared with its own text before the edit (`3bbcd8e4^`, the fork of `#2044`), and the restructure's findings cite rows of that older text. Split the document at its headings, before and after `#2044`. For each section the edit changed, have a reviewer list every statement, qualifier, requirement ("must", "only", "never"), scope limit or stated reason present in the old text and missing or weaker in the new, quoting both, with the brief the `PL-95SW` audit used (`/mnt/project-files/v0.7.0/repo-copy-edit/audit-BRIEF.md`). Restore each finding in place. Put a section back to its earlier wording where it lost three or more. Decision history that `PL-SVGH` would cut anyway is recorded as a finding and left out.

**Done when.** Every section `#2044` changed has been compared, and each statement the comparison found missing or weakened is back, or is recorded here as one the restructure cuts on purpose, with the reason.

**Generator check.** One mechanism, the copy editor dropping requirements, qualifiers and reasons, caused these losses. It is filed as `PL-F0Q2`.
