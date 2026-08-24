---
id: PL-009
title: Playback speed multiplier
priority: P3
effort: L
status: needs-decision
classes: feature
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/simulation_view.py
added: 2026-08-23
---

**Problem.** No faster-than-real-time playback. Target is real time up to
roughly 120x and beyond, comparable to the Gas Man reference simulator.
**Why it matters.** Wash-in and washout of a low-solubility agent take
clinical minutes to tens of minutes; watching them in real time is a poor
use of a learner's attention.
**Where.** `app/controller.py`, `app/simulation_view.py`; sim time is
already explicit state independent of wall-clock time, so going faster
mostly means calling `advance()` more times per render tick.
**Decision needed.** Scope this into a `ROADMAP.md` milestone before any
implementation starts — it is an `L` and must not be started from this
entry. The scoping has to settle how the multiplier is exposed without
creating a hidden mode, and how it interacts with the fixed
`SIMULATION_STEP_S = 0.1`.
**Note.** The PL-001 blocker is cleared: render cadence is now independent
of simulation cadence, and frame cost no longer grows with run length, so a
multiplier no longer multiplies a growing bottleneck.
**Done when.** A scoped milestone exists in `ROADMAP.md`, or the idea is
deliberately retired.

---
