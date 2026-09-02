---
id: PL-B9PY
title: Decompose SimulationView so two runs can be rendered at once
priority: P2
effort: M
status: blocked
classes: refactor
blocked-by: PL-WB0X
touches: src/anesthesia_sim/app/simulation_view.py, tests/unit/test_simulation_view.py
added: 2026-09-02
---

**Problem.** `SimulationView` is one class holding one run's widgets and one
`SimulationController` reference. Even after `PL-WB0X` (split
`simulation_view.py`) extracts the formatters and the chart-series shaping,
what remains — widget construction, event handling, refresh and failure
handling — is built around the assumption that there is exactly one run on
screen.

**Why it matters.** This is stage 3 of `PL-WB0X`, split out so that item can
carry the two extractions v0.4.0 needs while this waits for the milestone that
actually requires it. v0.5.0 — the case you can branch — is bookmarks, forking
and *side-by-side comparison of two branches*, which means two runs rendered at
once. A single class holding one run's widgets and one controller reference is
the shape that genuinely fails there, rather than merely being inconvenient.
That is the argument the size of the module alone does not make, and it is why
this stage is not pulled forward with the other two.

**Where.** `app/simulation_view.py` — what remains of `SimulationView` after
`PL-WB0X`'s two extractions land: the `_build_*` group, the `_handle_*` group,
the refresh path, and the failure path.

**Blocked on two things.** `PL-WB0X` (split `simulation_view.py`), which must
land first because this operates on what that leaves behind; and v0.5.0 being
scoped, since the decomposition's shape follows from how comparison renders two
runs. Do not design it before that milestone has a goal, required scope and
definition of done — guessing at the target shape is how a refactor becomes
speculative generality.

**Where it belongs on the plan.** Gate 1, which `ROADMAP.md`'s timeline records
as frozen when v0.5.0 is scoped and shipping inside v0.5.0. This is the half of
`PL-WB0X`'s original scope that stays there; the two extractions moved into
v0.4.0's Required scope on 2026-09-02 (project owner), because they gate
`PL-DHV7` (MAC multiples as a display unit) and the milestone's chart work.

**Found.** 2026-09-02, resolving `PL-WB0X`'s three contradictory placements —
the instance `PL-4C41` (a brief can contradict itself about its own sequencing)
was filed against. One item cannot sit in two milestones, so the split is what
makes the approved placement representable.
