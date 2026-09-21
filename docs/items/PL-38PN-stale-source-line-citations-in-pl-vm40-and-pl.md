---
id: PL-38PN
title: Stale source line citations in PL-VM40 and PL-L2F2 point at lines the files no longer have
priority: P3
effort: S
status: dropped
classes: docs
touches: docs/items/PL-VM40-derive-simulated-time-from-a-step-count-and.md, docs/items/PL-L2F2-the-fixed-volume-alveolus-blocks-nitrous-oxide.md
added: 2026-09-03
closed: 2026-09-21
reason: `.claude/rules/citation-drift.md`'s closed-brief clause. Its whole remaining deliverable is repointing line citations inside `PL-VM40` and `PL-L2F2`, both `status: done` (closed 2026-09-04 and 2026-09-07), where the rule says drift "is not a finding: do not repair it, do not file an item about it, and do not count it when sizing a cluster". The line-anchor ban refuses the same work a second time over - re-pointing a number at a fresh number mints the next drift, which this item and `PL-JXVD` are the rule's own worked example of. `PL-RFSL` holds the finding and this is its first ending; re-judged in `PL-PT7M`'s pass, 2026-09-21
---

**Problem.** Two open items cite source lines that have moved:

- `PL-VM40` places the run loop in `src/anesthesia_sim/app/simulation_view.py`
  "around line 943". The loop is `_run_simulation_timer` at `:1149`.
- `PL-L2F2` cites `core/alveolar.py:24` and `:63`. The corresponding
  definitions are at `:32` and `:68` (`AlveolarCompartment` and
  `apply_blood_uptake`).

**Why it matters.** Individually trivial; the pattern is not. A line number in a
brief is a promise that a session can go straight to the code, and a wrong one
costs a search plus the doubt about whether the *rest* of the brief is describing
the current tree. `PL-VM40` is a `P1` in the milestone now being implemented, so
the cost lands soon.

The general form is worth a moment's thought rather than a fix-and-forget:
`tools/doc_check.py` already decides whether a cited path exists, and this is the
same question one level finer — does the cited *line* still hold the symbol the
sentence names. A citation shaped `file.py:NN (symbol_name)` would be
mechanically checkable; a bare `:NN` is not. Whether that is worth building is a
separate judgment, and `CLAUDE.md`'s gate applies: only if the work recurs and
the answer is deterministic.

**Where.** `docs/items/PL-VM40-*.md`, `docs/items/PL-L2F2-*.md`.

**Done when.** Both citations point at the current lines, and the decision about
whether to make line citations checkable is recorded either way.

**Found.** Session auditing which open items the v0.4.1 `core/` pass would
invalidate, 2026-09-03.

**Swept 2026-09-19 under `PL-6ZQY` (crossing-lane consolidation). Partly overtaken, and the
correction it offers can no longer be copied.** The decision half of the
`Done when` is recorded: `PL-J7C5` closed 2026-09-14 (#552) and answers **no** -
a line citation in an item brief is a dated measurement rather than a live
specification, so it is not made checkable and it stays. Both cited items have
also closed (`PL-VM40`, `PL-L2F2`), so no session will follow these pointers to
code; the problem statement's "two **open** items" is stale.

Neither citation has been corrected, so the remainder is real - but **this
brief's own replacement numbers are now wrong**, and re-deriving them is the
work rather than transcribing them:

- `_run_simulation_timer` at `:1149` - the function does not exist in `src/` at
  all, and `simulation_view.py` is 580 lines. The loop moved to
  `run_view.py` (`:901`, `:906`) through the `PL-B9PY` decomposition and the
  PySide6 port.
- `core/alveolar.py` `:32` and `:68` - `AlveolarCompartment` is at `:39`, and
  `apply_blood_uptake` no longer exists: `PL-GS5X` removed it when the operator
  split became the exact matrix exponential, which `alveolar.py:7-8` records.

`PL-JXVD` is the open item recording exactly this second-order staleness, and
its own table has gone stale the same way.
