---
id: PL-B9PY
title: Decompose SimulationView so two runs can be rendered at once
priority: P2
effort: M
status: needs-decision
classes: refactor
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

**Blocked on two things, and only one of them was ever an item.** `PL-WB0X`
(split `simulation_view.py`), which had to land first because this operates on
what that leaves behind — **closed 2026-09-03**; and v0.5.0 being scoped, since
the decomposition's shape follows from how comparison renders two runs. Do not
design it before that milestone has a goal, required scope and definition of
done — guessing at the target shape is how a refactor becomes speculative
generality.

**Status is `needs-decision` rather than `blocked`, and the reason is the
second blocker.** `blocked-by` can only name a queue item, and scoping v0.5.0
is a design round on `ROADMAP.md` rather than an item — so once `PL-WB0X`
closed there was nothing left for the field to hold, and `blocked` with an
empty field is a store error. `ready` would be worse: it invites a session to
start a refactor against a target shape nobody has decided, which this brief
forbids two paragraphs up. `needs-decision` is the accurate one, because the
next step here genuinely is a decision — what v0.5.0's comparison renders —
and it is not this item's to make. Promoting to `ready` was attempted and
reverted on 2026-09-03, when `PL-WB0X` closed and the "every blocker has
closed" advisory fired on the strength of the field alone. `PL-W8XP` carries
the general case.

**Where it belongs on the plan.** Gate 1, which `ROADMAP.md`'s timeline records
as frozen when v0.5.0 is scoped and shipping inside v0.5.0. This is the half of
`PL-WB0X`'s original scope that stays there; the two extractions moved into
v0.4.0's Required scope on 2026-09-02 (project owner), because they gate
`PL-DHV7` (MAC multiples as a display unit) and the milestone's chart work.

**Decision needed.** What v0.5.0's side-by-side comparison actually renders —
two full dashboards, two chart traces on one axis, or one dashboard with a
switchable run — because the decomposition's shape follows from it and from
nothing else. That is a `ROADMAP.md` scoping round for v0.5.0, not a question
this item can answer for itself; it becomes `ready` the moment that milestone
has a goal, required scope and definition of done.

**Done when.** Rendering a second run requires no change to the classes this
item creates: whatever v0.5.0's comparison turns out to be, one run's widgets,
its controller reference, its event handling and its refresh path are held by
something instantiable more than once, and `tests/unit/test_simulation_view.py`
builds two of them against two controllers and drives both. No displayed value,
format or behavior changes for a single run — the existing view tests are what
holds that, as they were for `PL-WB0X`.

**Found.** 2026-09-02, resolving `PL-WB0X`'s three contradictory placements —
the instance `PL-4C41` (a brief can contradict itself about its own sequencing)
was filed against. One item cannot sit in two milestones, so the split is what
makes the approved placement representable.
