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
