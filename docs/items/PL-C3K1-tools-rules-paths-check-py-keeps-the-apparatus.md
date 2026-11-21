---
id: PL-C3K1
title: tools/rules_paths_check.py keeps the apparatus path set in two copies that a new apparatus path must be added to by hand
status: untriaged
feature: standing-weight
added: 2026-11-21
---

**Problem.** tools/rules_paths_check.py keeps the apparatus path set in two copies that a new apparatus path must be added to by hand

**Why it matters.** All 6 of `tools/rules_paths_check.py`'s CI refusals that `PL-LY24` counted asked for a new workflow path to be added "to the three copies of the set", and none found a misanchored glob, which is the check's main rule. Two copies of one list, each also held to `docket.toml`'s `workflow_paths`, break `CLAUDE.md`'s rule that a shared fact has one source of truth, and each new apparatus path costs a red run.

**Checked 2026-11-21**, at `a5d582f0c`, by `PL-SRNF` (correct two queue records). Two copies remain, where the refusals above named three. `PL-2PJ6` (move the history out of the launch instructions) removed the copy in `.claude/rules/expert-review.md`. The check now compares the list in `CLAUDE.md` § "Proactive expert review and domain best practices" with the `paths:` of `.claude/rules/apparatus-standard.md`, and both with `workflow_paths`. Its refusal says "add it to both copies of the set".

**What to do.** Read the apparatus path set from one home, and derive the other use from it.

**Done when.** A new path added to `docket.toml`'s `workflow_paths` needs no second edit, and the check still refuses a misanchored glob.
