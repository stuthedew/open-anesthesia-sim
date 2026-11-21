---
id: PL-C3K1
title: tools/rules_paths_check.py keeps the apparatus path set in three copies that a new apparatus path must be added to by hand
status: untriaged
feature: standing-weight
added: 2026-11-21
---

**Problem.** tools/rules_paths_check.py keeps the apparatus path set in three copies that a new apparatus path must be added to by hand

**Why it matters.** All 6 of `tools/rules_paths_check.py`'s CI refusals that `PL-LY24` counted asked for a new workflow path to be added "to the three copies of the set", and none found a misanchored glob, which is the check's main rule. Three copies of one list break `CLAUDE.md`'s rule that a shared fact has one source of truth, and each new apparatus path costs a red run.

**What to do.** Read the apparatus path set from one home, and derive the other two uses from it.

**Done when.** A new path added to `docket.toml`'s `workflow_paths` needs no second edit, and the check still refuses a misanchored glob.
