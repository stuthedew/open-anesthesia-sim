---
id: PL-TFX5
title: Fork a run at any control-input event or bookmark, flat rather than as a tree
priority: P2
effort: L
status: blocked
blocked-by: PL-J2TD
classes: feature
feature: scenario-branching
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/core, tests/unit, tests/integration, docs/ARCHITECTURE.md
added: 2026-09-06
---

**Problem.** Comparing two managements of the same case - coast on low flow
versus hold 0.5 MAC, then compare time to a wake-up threshold - currently means
building the whole case twice, and the two runs then differ by every small
thing that was not reproduced identically.

**Why it matters.** This is the educational payload of the whole milestone: it
isolates the variable under study. A learner reading a comparison of two
independently built runs cannot tell which differences they caused.

**Shape (project owner, 2026-08-25).** Flat, not a tree: one trunk run with N
branches taken from points on it. Sub-forks of forks are deliberately out -
they multiply without bound and buy little over re-branching from the trunk.

**Branch points.** Any recorded control-input-timeline event is a valid branch
point, not only a placed bookmark. This generalizes the reference simulator's
single-track truncate-and-continue behavior into true forking, where the
pre-change branch is kept rather than discarded so both are available for
comparison.

**What a branch inherits.** Its parent's agent and its patient, rather than
re-choosing either: changing agent is already an explicit new case (`PL-R3KB`,
v0.4.0), and a branch that could change it would be a second case wearing a
comparison's clothes.

**Where.** `src/anesthesia_sim/app/controller.py`;
`docs/ARCHITECTURE.md` records what a branch is and what it shares with its
parent.

**Done when.** A run can be forked at any recorded control event or bookmark;
the trunk survives the fork; branches of branches are refused rather than
silently flattened; and the branch carries its parent's agent and patient. The
reproduction property is `PL-Z3W6`.
