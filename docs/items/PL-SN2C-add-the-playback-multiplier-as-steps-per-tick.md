---
id: PL-SN2C
title: Add the playback multiplier as steps per tick, with the rate always visible
priority: P2
effort: M
status: blocked
blocked-by: PL-VM40
classes: feature, ux
feature: teachable-case
touches: src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/controller.py, docs/MODEL.md
added: 2026-08-25
---
**Problem.** The simulation advances at 1x real time. Sevoflurane's muscle group has
a time constant of about 135 min at reference settings and fat about 42 h, so the
two compartments that make uptake and distribution worth teaching cannot be watched
at all: reaching three muscle time constants takes nearly seven hours of sitting in
front of the application.

**Why it matters.** Context-sensitive emergence - the reason a three-hour case wakes
up differently from a twenty-minute one - is the payload of this whole class of
simulator, and it is currently unreachable. This is the single change that turns the
existing model from correct into teachable. Promotes `ROADMAP.md` planned-milestone
item 25.

**Where.** `app/simulation_view.py` (the run loop and the header clock).

**Safety notes.** The multiplier changes how many 0.1 s steps are taken per tick and
must never change the step size. A larger step would change the displayed values in
response to a *view* control - the same number meaning something different
depending on how fast the user was watching - which is a determinism failure
regardless of the solver: two learners comparing the same case at different speeds
would see different numbers. `docs/MODEL.md` § "Selected method (as implemented)"
states this as the reason the step is fixed, explicitly rather than incidentally:
0.1 s is fixed "for *determinism* - removing the step-size divergence and the
machine-speed dependence that make a run irreproducible on another computer -
rather than for accuracy". Depends on PL-VM40, without which
the number of steps taken is machine-dependent and the run is not reproducible at
any rate.

*Reworded 2026-09-03.* This paragraph previously argued the rule from the
operator-splitting error and from the error bound § "Displayed precision" derives
the two-decimal readout from. `PL-GS5X` (replace the operator split with the exact
matrix exponential, v0.4.1) removes the splitting error at any step size and
`PL-X9KD` re-derives that section, so both halves of the old argument expire one
release after this item ships. The rule survives on determinism alone, which is
the ground it should have been on.

**Human factors.** The current rate is a mode, and a hidden mode is the failure this
project's interface rules exist to prevent: a clock advancing at 60x beside numbers
that look like a live case is misreadable at a glance. Show the multiplier beside
the elapsed-time readout at all times, including at 1x.

**Done when.** A three-hour case can be run and watched end to end in a few minutes
of wall clock; the simulation step is 0.1 s at every multiplier, asserted by test;
the recorded history is element-wise identical at every multiplier, asserted by
test; and the active rate is visible whenever the clock is.

**Blocked on `PL-VM40` (2026-09-04, project owner, deciding `PL-5WFS`).**
Sequencing only, and it is this item's own statement rather than a new
judgment: the paragraph above already says it depends on `PL-VM40`, "without
which the number of steps taken is machine-dependent and the run is not
reproducible at any rate". That sentence lived in prose, where the ranking
cannot read it; this field is the same statement where `bin/docket next` can.

The order was correct before this edit only by accident — `PL-VM40` is `P1`
and this is `P2`, so the band happened to separate them. Nothing would have
held if either had been re-banded.
