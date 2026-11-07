---
id: PL-ZMBN
title: Copy edit docs/interface-provenance.md with the fixed copy editor, section by section, keeping every fact a contributor needs
status: done
feature: repo-copy-edit
touches: docs/interface-provenance.md
added: 2026-11-05
closed: 2026-11-07
pr: 2045
verify: grep -q "uses Blender's words for two of its three layout concepts" docs/interface-provenance.md && grep -q 'Prune the contract of a View' docs/interface-provenance.md
---

**Problem.** docs/interface-provenance.md had not been through the copy editor since that tool was fixed (`PL-HGZS`, #2038). The project owner asked on 2026-11-05 for every human-facing document to be copy edited, skipping text the copy editor had already edited (thread "Copy edit the entire repository"). They chose on 2026-11-05 to line edit each document now and restructure it later.

**How.** Each of the thirty-one sections was line-edited alone with the four-read audit, for a contributor who knows anesthesia and Python but not this repository's names. Twenty-nine were rewritten; "How this study was conducted, and where it could not reach" and "What a later design thread owes this study" were kept. The edits were checked for any Blender file, function, struct, number, date or item id they dropped: every name dropped from one place is still given elsewhere in the document, and the one bold phrase that `ROADMAP.md` and `src/anesthesia_sim/app/view_contract.py` quote ("Prune the contract") was restored. The closing prose review then read the thirty-two changed passages and rewrote twenty-four; the only code name it dropped, `curl`, is still given in § "Pages read on 2026-10-25". Runs and replies are in `/mnt/project-files/v0.7.0/repo-copy-edit/runs/docs-interface-provenance-md/`.

Two fixes rode the branch as their own commits. The naming paragraph and the adopted-terms paragraph both said the project uses Blender's word "editor" for what occupies an area; `.claude/rules/ui-areas.md` calls it a View, and both paragraphs now say so.

The structure read's findings are filed under the `interface-provenance-structure` feature: the restructure as `PL-T8RL`, and seven contradictions or missing facts as `PL-QXYW`, `PL-68M1`, `PL-Y9F0`, `PL-2WBR`, `PL-JVK4`, `PL-41CR` and `PL-ZD8Y`.

**Done when.** Every section has been line-edited, and no Blender file, function, value or citation a contributor uses was lost.

**Generator check.** The owner asked for this work (2026-11-05, "copy edit entire repo"). It is one area of a repository-wide copy edit, not a defect, so no mechanism caused it.
