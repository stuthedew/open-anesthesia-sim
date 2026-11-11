---
id: PL-KGY1
title: Copy edit docs/ARCHITECTURE.md with the fixed copy editor, section by section, keeping every fact a contributor needs
status: done
feature: repo-copy-edit
milestone: v0.6.17
touches: docs/ARCHITECTURE.md
added: 2026-11-05
closed: 2026-11-05
pr: 2044
verify: grep -q 'imports between them run in one' docs/ARCHITECTURE.md && grep -q '^## Where new code belongs' docs/ARCHITECTURE.md
---

**Problem.** docs/ARCHITECTURE.md had not been through the copy editor since that tool was fixed (`PL-HGZS`, #2038). The project owner asked on 2026-11-05 for every human-facing document to be copy edited, skipping text the copy editor had already edited (thread "Copy edit the entire repository"). He chose on 2026-11-05 to line edit each document now and restructure it later.

**How.** Each of the fourteen sections was line-edited alone with the four-read audit, for a contributor who knows anesthesia and Python but not this repository's names. The edits were checked for any module, function, file name, number or item id they dropped: every name dropped from one place is still given elsewhere, and only decision history (eight item ids and four dates) left the document. The closing prose review then read the fifteen changed passages. Runs and replies are in `/mnt/project-files/v0.7.0/repo-copy-edit/runs/docs-ARCHITECTURE-md/`. The structure read's findings are filed under the `architecture-md-structure` feature: the restructure as `PL-SVGH`, and six contradictions or missing definitions as `PL-G1J9`, `PL-6G7N`, `PL-HLTR`, `PL-4CZW`, `PL-GSPR` and `PL-SMKL`.

**Done when.** Every section has been line-edited, and no module, function, file name, value or citation a contributor uses was lost.

**Generator check.** The owner asked for this work (2026-11-05, "copy edit entire repo"). It is one area of a repository-wide copy edit, not a defect, so no mechanism caused it.
