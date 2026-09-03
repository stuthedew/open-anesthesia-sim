---
id: PL-38PN
title: Stale source line citations in PL-VM40 and PL-L2F2 point at lines the files no longer have
status: ready
priority: P3
effort: S
classes: docs
touches: docs/items/PL-VM40-derive-simulated-time-from-a-step-count-and.md, docs/items/PL-L2F2-the-fixed-volume-alveolus-blocks-nitrous-oxide.md
verify: python3 tools/doc_check.py check && ! grep -q 'line 943' docs/items/PL-VM40-derive-simulated-time-from-a-step-count-and.md
added: 2026-09-03
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
