---
id: PL-C3K1
title: tools/rules_paths_check.py keeps the apparatus path set in two copies that a new apparatus path must be added to by hand
priority: P3
effort: M
status: done
classes: defect
feature: standing-weight
milestone: v0.6.21
touches: tools/rules_paths_check.py, tests/unit/test_rules_paths_check.py, CLAUDE.md, .claude/rules/apparatus-standard.md
deferred-from: v0.7.0 - present at the freeze, with three copies then, but a workflow check with no connection to anything on the frozen list or in v0.7.0 Required scope, and it changes nothing a learner sees
added: 2026-11-21
closed: 2026-11-22
pr: 2240
payoff: a new apparatus path costs one edit instead of a red run and two more edits
tests: tests/unit/test_rules_paths_check.py::test_a_path_added_to_workflow_paths_alone_is_refused_until_written, tests/unit/test_rules_paths_check.py::test_write_adds_the_new_path_and_keeps_the_rest_of_the_rule
---

**Problem.** tools/rules_paths_check.py keeps the apparatus path set in two copies that a new apparatus path must be added to by hand

**Why it matters.** All 6 of `tools/rules_paths_check.py`'s CI refusals that `PL-LY24` counted asked for a new workflow path to be added "to the three copies of the set", and none found a misanchored glob, which is the check's main rule. Two copies of one list, each also held to `docket.toml`'s `workflow_paths`, break `CLAUDE.md`'s rule that a shared fact has one source of truth, and each new apparatus path costs a red run.

**Checked 2026-11-21**, at `a5d582f0c`, by `PL-SRNF` (correct two queue records). Two copies remain, where the refusals above named three. `PL-2PJ6` (move the history out of the launch instructions) removed the copy in `.claude/rules/expert-review.md`. The check now compares the list in `CLAUDE.md` § "Proactive expert review and domain best practices" with the `paths:` of `.claude/rules/apparatus-standard.md`, and both with `workflow_paths`. Its refusal says "add it to both copies of the set".

**What to do.** Read the apparatus path set from one home, and derive the other use from it.

**Done when.** A new path added to `docket.toml`'s `workflow_paths` needs no second edit, and the check still refuses a misanchored glob.

**Checked 2026-11-22.** The two copies are still there. `APPARATUS_LISTS` in `tools/rules_paths_check.py` names the list in `CLAUDE.md`, the check reads `.claude/rules/apparatus-standard.md`'s `paths:` as the other copy, and its refusal still says "add it to both copies of the set". At the freeze the check held three copies (`git show 0947408:tools/rules_paths_check.py`).

**Generator check.** The fact misread is which paths the apparatus standard governs. Two files state it, and a check holds them to each other instead of both reading one record. No head states this fact. `PL-8ZGY` states which lane each tracked path is in, a different fact that this set is checked against. This is a one-off.

**Done 2026-11-22.** The one home is `docket.toml`'s `workflow_paths`, less the entries under `tests/` and those `LANE_ONLY` in `tools/rules_paths_check.py` names. `.claude/rules/apparatus-standard.md`'s `paths:` has to be literal, because the harness reads it, so it is now written rather than copied: `make check` runs `tools/rules_paths_check.py --write`, which rewrites that list from the home and names each glob it adds. CI runs the check without `--write` and refuses a list that differs, naming the command. The prose copy in `CLAUDE.md` § "Proactive expert review and domain best practices" now gives examples and points at the rule's `paths:` instead of listing the set. One behaviour changed on purpose: a new `workflow_paths` entry is apparatus unless `LANE_ONLY` names it, where before the check refused it until a session placed it. The `--write` line saying what it added is where that decision is now taken. Writing the list also replaced `/subprojects/docket/**` with `/subprojects/**`, matching the lane, and `subprojects/` holds only `docket/` today. `tools/doc_check.py`'s `GATE_ONLY` records the two modes, since the gates run them differently on purpose.

Files checked in the docs sweep: `CLAUDE.md`, `.claude/rules/apparatus-standard.md`, `docs/apparatus.md`, `Makefile`, `.github/workflows/quality.yml`, `tools/doc_check.py`, and `tests/unit/test_rules_paths_check.py`'s module docstring.
