---
id: PL-B9PY
title: Decompose SimulationView so two runs can be rendered at once
priority: P2
effort: M
status: ready
classes: refactor
feature: scenario-branching
touches: src/anesthesia_sim/app/simulation_view.py, tests/unit/test_simulation_view.py
verify: uv run pytest tests/unit/test_simulation_view.py && grep -q 'def test_two_run_views_drive_two_controllers' tests/unit/test_simulation_view.py
added: 2026-09-02
---

> **This ships in v0.5.0, on Flet, and is rewritten by the Qt port after it.**
> It was briefly listed as work `v0.5.1` would throw away; that was wrong and is
> corrected in `ROADMAP.md` § "v0.5.1" - Gate 1 places this under "Cleared by
> v0.5.0 itself", because decomposing this class so two runs render is what the
> branched-run milestone *is*. Deferring it behind the port would defer the MVP.
> The duplication is the accepted price of shipping the MVP first. What the port
> owes this item is its **shape**: the Qt view is built decomposed from the
> start, so this design is a required input to `PL-25KS`. 2026-09-10.

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

**Blocked on two things, only one of which was ever an item. Both have
cleared.** `PL-WB0X` (split `simulation_view.py`), which had to land first
because this operates on what that leaves behind — **closed 2026-09-03**; and
v0.5.0 being scoped, since the decomposition's shape follows from how
comparison renders two runs — **scoped 2026-09-06**, with a goal, required
scope, definition of done and an explicit out-of-scope list in `ROADMAP.md`
§ "v0.5.0 - the case you can branch". The caution that stood here — do not
design this before that milestone has a goal, required scope and definition of
done, because guessing at the target shape is how a refactor becomes
speculative generality — is satisfied rather than lifted. The shape is now
read from that section; it is still not guessed.

**Promoted to `ready` on 2026-09-08 (project owner), and the history is worth
keeping because the identical promotion was wrong five days earlier.**
`needs-decision` was accurate while v0.5.0 was unscoped: `blocked-by` can only
name a queue item, and scoping v0.5.0 is a design round on `ROADMAP.md` rather
than an item — so once `PL-WB0X` closed there was nothing left for the field to
hold, and `blocked` with an empty field is a store error, while `ready` would
have invited a session to start a refactor against a target shape nobody had
decided. A promotion attempted on 2026-09-03 was reverted for exactly that
reason: the "every blocker has closed" advisory fired on the strength of the
field alone, which could not see the second blocker. What changed on 2026-09-06
is the thing the field was never able to say — the milestone is scoped, so the
condition this brief states for its own promotion is met. `PL-W8XP` (an item
blocked on a milestone being scoped cannot say so) carries the general case;
`PL-MKFG` carries the two days this item then spent at a status that kept
`bin/docket next` from ranking it.

**Where it belongs on the plan.** Gate 1, **frozen 2026-09-06** and shipping
inside v0.5.0, where this is the ninth of the eighteen entries in that
milestone's Required scope. This is the half of
`PL-WB0X`'s original scope that stays there; the two extractions moved into
v0.4.0's Required scope on 2026-09-02 (project owner), because they gate
`PL-DHV7` (MAC multiples as a display unit) and the milestone's chart work.

**Decision made, 2026-09-06 (project owner), and it is the second of the two
chart traces on one axis.** The question this brief held open — two full
dashboards, two chart traces on one axis, or one dashboard with a switchable
run — is answered by `PL-8PSW` (overlay two branches on one time axis) in
v0.5.0's Required scope: **two branches overlaid on one time axis**, with two
stacked panels sharing a time axis considered and rejected the same day, on the
evidence that shared-space line graphs are the more efficient technique for
comparisons over small visual spans. The channel assignment followed on
2026-09-07 (`PL-HLD5`): the compartment keeps line style *and* colour exactly
as the single-run chart draws them, the run is carried on line width, and at
most two compartments are drawn while two branches are shown — the cap being
what frees width for the run rather than a convenience. `ROADMAP.md`'s
out-of-scope list bounds it further: never more than two runs displayed at
once.

So the target shape is settled enough to build against. One run's widgets,
controller reference, event handling and refresh path move into something
instantiable twice; the chart, the time base and the compartment selection are
*shared* across both instances rather than duplicated into each, because the
comparison draws both runs on one axis under one selection. Two independent
dashboards is the reading this decision rules out.

**Done when.** Rendering a second run requires no change to the classes this
item creates: one run's widgets, its controller reference, its event handling
and its refresh path are held by something instantiable more than once, and
`tests/unit/test_simulation_view.py` carries
`test_two_run_views_drive_two_controllers`, which builds two of them against
two controllers and drives both. No displayed value, format or behavior changes
for a single run — the existing view tests are what holds that, as they were
for `PL-WB0X`, and all 192 of them pass today.

**Found.** 2026-09-02, resolving `PL-WB0X`'s three contradictory placements —
the instance `PL-4C41` (a brief can contradict itself about its own sequencing)
was filed against. One item cannot sit in two milestones, so the split is what
makes the approved placement representable.
