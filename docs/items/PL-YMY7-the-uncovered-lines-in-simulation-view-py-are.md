---
id: PL-YMY7
title: The uncovered lines in `simulation_view.py` are Flet-construction paths, not guards
status: ready
priority: P3
effort: S
classes: test, docs
feature: core-guard-coverage
touches: docs/items/PL-7YZH-test-the-two-failure-paths-in-simulation-view.md
added: 2026-08-25
---

**Problem.** Thirteen uncovered statements in `app/simulation_view.py` (lines
402, 472-486, 529-539, 572, 621, 650, 724, 795, 1162-1168) are Flet control
construction and one exception handler, not validation guards. They need a
live rendering harness to exercise, which the project does not have.

**Why it matters.** They look like ordinary coverage debt in a report and are
not - they overlap PL-027's territory (confirming behavior on a live Flet
client), and treating them as mechanical test-writing would send a worker
flailing at something that cannot be proved by a command. Recording the
distinction stops the next reader of a coverage report from filing it as
routine backfill.

**Done when.** Either a rendering-harness approach is decided (with PL-027) or
these lines are explicitly excluded from any coverage expectation, with the
reason recorded.

**The coverage command shape cannot be written for this item at all**
(recorded 2026-09-02 while working `PL-5TN8`). `uv run pytest
--cov=anesthesia_sim.app.simulation_view --cov-fail-under=100` is unreachable
by construction: the item's own finding is that the remaining statements need
a live rendering harness the project does not have, so the command would fail
forever and could never be satisfied by doing the work this item describes.
The item's `touches` names a `docs/items/` file and its classes are `test,
docs` - its work product is a recorded decision, and the command that proves
it is the paired doc shape, not a coverage threshold.

**The line numbers above have drifted.** They were written 2026-08-25 as
"lines 402, 472-486, 529-539, 572, 621, 650, 724, 795, 1162-1168", thirteen
statements. Measured on this checkout 2026-09-02: **eleven** statements, at
`369, 439-440, 451, 487-493, 511, 535, 551, 594, 647`, out of 282 (96%). The
finding is unchanged - they are still Flet construction plus one exception
handler - but the citation is stale, so re-measure before acting on it rather
than reading those numbers as current.
