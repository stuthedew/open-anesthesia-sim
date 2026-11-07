---
id: PL-3K13
title: Copy edit docs/machine-abstraction.md and docs/machine-survey.md with the fixed copy editor, section by section, keeping every fact a contributor needs
status: done
feature: repo-copy-edit
touches: docs/machine-abstraction.md, docs/machine-survey.md
added: 2026-11-07
closed: 2026-11-07
pr: 2048
verify: grep -q 'Five entries of that matrix belong to the breathing circuit' docs/machine-abstraction.md && grep -q '^## The headline finding, because it decides the abstraction' docs/machine-survey.md
---

**Problem.** docs/machine-abstraction.md and docs/machine-survey.md had not been through the copy editor since that tool was fixed (`PL-HGZS`, #2038). The project owner asked on 2026-11-05 for every human-facing document to be copy edited, skipping text the copy editor had already edited, and chose to line edit each document now and restructure it later (thread "Copy edit the entire repository").

**How.** Each section was line-edited alone with the four-read audit, for the readers that `.claude/rules/plain-writing.md` names for each document. In machine-abstraction.md, 12 of 16 sections were rewritten; in machine-survey.md, 19 of 22. The edits were checked for any value, equation, code name, citation or date they dropped. The only loss was the survey's pointer to the citation rule (`.claude/rules/citing-sources.md`), which is a rule for writers and lives in its own file. The closing prose review then read the 42 changed passages and rewrote 36. The few code names it dropped (`variable_bypass`, `fixed_volume_percent`, `reference_circle_system.json`) are still in the tables or entries the sentences pointed at, and the dropped owner decision of 2026-09-20 is still recorded in the survey's section on unknown values. Runs and replies are in `/mnt/project-files/v0.7.0/repo-copy-edit/runs/docs-machine-abstraction-md/`, `runs/docs-machine-survey-md/` and `runs/close-out/`.

One fix rode the branch as its own commit. The machine abstraction said that five entries of the system matrix involve the fresh gas flow. The code builds four (`src/anesthesia_sim/core/governing_equations.py`); the fifth entry the paragraph lists holds the ventilation and the circuit volume.

The structure reads are filed under the `machine-docs-structure` feature as `PL-39ZK` and `PL-3MTS`. The closing review's queries, sentences it found contradicted elsewhere or missing a fact, are filed under the same feature as `PL-37N4` and `PL-8ZD7`.

**Done when.** Every section of both documents has been line-edited, and no value, equation, code name or citation a reader uses was lost.

**Generator check.** The owner asked for this work (2026-11-05, "copy edit entire repo"). It is one area of a repository-wide copy edit, not a defect, so no mechanism caused it.
