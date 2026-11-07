---
id: PL-95SW
title: Copy edit docs/MODEL.md with the fixed copy editor, section by section, outside the sections already rewritten for clinicians, keeping every value, marker and citation
status: done
feature: repo-copy-edit
touches: docs/MODEL.md
added: 2026-11-07
closed: 2026-11-07
pr: 2049
verify: grep -q 'The guarantee does not cover four things, and none of them is a defect' docs/MODEL.md && grep -q 'deterministic replay passes (§ "Deterministic replay test")' docs/MODEL.md
---

**Problem.** Copy edit docs/MODEL.md with the fixed copy editor, section by section, outside the sections already rewritten for clinicians, keeping every value, marker and citation


**How.** Each section outside the ones already rewritten for clinicians was line-edited alone with the fixed copy editor (`PL-HGZS`), for the readers `.claude/rules/plain-writing.md` names for `docs/MODEL.md`. The project owner chose a line edit now and a restructure later (2026-11-05). The edit changed 78 of 124 sections and passed every check on numbers, equations, code names, citations, markers and dates.

Two blind reviews then found 8 statements the edit had dropped, which were restored. The project owner chose, on 2026-11-07, to have every edited section audited before the merge. Six review agents compared each section's old and new text and listed every statement, qualifier, requirement, scope limit or reason that was missing or weaker: about 120 in 42 sections. Fourteen sections that lost three or more, or whose figures lived only in prose, went back to `main`'s wording. In the other sections the 34 remaining findings were restored in place. The other findings were reworded bold leads; no file cites one. The audit's findings are in `/mnt/project-files/v0.7.0/repo-copy-edit/audit-findings/`.

One finding was rejected: a blind review asked that ten closed items' `verify:` lines follow phrases the edit moved. A closed item's `verify:` records what ran, and the store refuses an edit to it, so that finding was not taken.

**Done when.** Every section outside the clinician rewrite has been line-edited or put back to its old wording, and no value, equation, code name, citation, requirement or stated reason a reader uses was lost.

**Generator check.** The work was asked for (2026-11-05, "copy edit entire repo"). The losses it exposed come from one mechanism, the copy editor dropping requirements, qualifiers and reasons that no token check sees, filed as `PL-F0Q2`. The same edit on the machine documents is filed for the same audit as `PL-B7V7`.
