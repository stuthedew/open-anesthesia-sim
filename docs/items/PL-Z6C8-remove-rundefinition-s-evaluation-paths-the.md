---
id: PL-Z6C8
title: Remove RunDefinition's evaluation paths, the propagator store and the tolerance constants they needed, and rewrite the rule and the specification sections that describe a run as its definition
priority: P1
effort: L
status: blocked
classes: refactor, safety
feature: run-computed-one-way
touches: src/anesthesia_sim/core, src/anesthesia_sim/app, tests, docs/MODEL.md, docs/INTERFACE.md, docs/ARCHITECTURE.md, .claude/rules/run-is-its-definition.md
blocked-by: PL-FST0
deferred-from: v0.7.0 - filed 2026-11-21, after the gate froze, as the build of the design the owner chose in PL-7CY5; each of the four pull requests leaves main releasable, so the release does not wait for the feature to finish
added: 2026-11-21
---

**Problem.** Remove RunDefinition's evaluation paths, the propagator store and the tolerance constants they needed, and rewrite the rule and the specification sections that describe a run as its definition

**Why it matters.** Once every reader reads the stored states, the closed-form evaluation paths and the allowances that reconcile them have no use, and keeping them leaves a second way to compute a state. The owner chose this design on 2026-11-21 in `PL-7CY5` (one rule for computing a run), which holds the counts, the measurements and the sources. The four items of the feature `run-computed-one-way` are built in this order: `PL-SZ6G`, `PL-MH9J`, `PL-FST0`, `PL-Z6C8`.

**What it changes.** It removes `RunDefinition.state_at`, `evaluate`, `evaluate_anchored`, `DisplayState` and the kept propagators in `core/run_definition.py`; `LIVE_READING_GAP` and the two-readings half of `HEIGHT_BAND` in `app/bookmarks.py`; `_GRID_UNIT_COUNT_TOLERANCE` in `app/chart_time_base.py`; and `STEP_COUNT_TOLERANCE` in `app/playback.py` where the playback tick is held in whole milliseconds. It rewrites `docs/INTERFACE.md` § "The canonical evaluation rule" and the sections of `docs/MODEL.md` and `docs/ARCHITECTURE.md` that describe a run as its definition. `PL-GJ1W` (each comparison picks its own tolerance) then resumes on the allowances that remain.

**Done when.** No module in `src/` computes a run's state except the step that stores it, the listed constants are gone or each states why it stays, and the documents describe the stored states.

**Generator check.** Work the owner asked for on 2026-11-21, building the design that `PL-7CY5` decided. It is not a head. The fact is `PL-GJ1W`'s, how far a computed value can be from the exact one: it deletes the allowances that existed only to reconcile two routes to one state.
