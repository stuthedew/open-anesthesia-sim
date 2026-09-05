---
id: PL-SN2C
title: Add the playback multiplier as steps per tick, with the rate always visible
priority: P2
effort: M
status: done
classes: feature, ux
feature: teachable-case
milestone: v0.4.0
touches: src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/playback.py, src/anesthesia_sim/app/formatting.py, docs/MODEL.md, docs/ARCHITECTURE.md, tests/unit/test_playback.py, tests/unit/test_simulation_view.py, tests/integration/test_sevo_controller.py
blocked-by: PL-VM40
added: 2026-08-25
closed: 2026-09-05
pr: 331
verify: uv run pytest tests/unit/test_simulation_view.py tests/integration/test_sevo_controller.py && grep -q 'def test_the_run_loop_takes_the_playback_rates_steps_per_tick' tests/unit/test_simulation_view.py && grep -q 'def test_the_recorded_history_is_identical_at_every_playback_rate' tests/integration/test_sevo_controller.py
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

**Block cleared 2026-09-04.** `PL-VM40` shipped in v0.3.9, so simulated time
is already an exact function of an integer step count and the run loop
already refuses to catch up to the wall clock. The field above is kept as
the record of why this waited.

**Landed 2026-09-05.** `app/playback.py` holds the rate as a value and
converts it into the number of *whole* steps a tick takes -
`multiplier x tick interval / step` - refusing a rate that does not land on
one rather than rounding it, because the only two ways to round it are a
step of a different size or a run advancing at a rate other than the one it
displays. `SIMULATION_TICK_INTERVAL_S` is named apart from
`SIMULATION_STEP_S` for the same reason: they are equal, and the equality is
what makes "60x real time" true, so it is stated where a test can check it
rather than assumed by a loop that sleeps one and steps the other.

The ladder is 1x, 5x, 20x, 60x and 300x, chosen by what each lets a reader
*watch* in about three minutes: three minutes of case, fifteen minutes, an
hour, a whole three-hour case, and fifteen hours - past three time constants
of the muscle group (about 6.75 h), which is the compartment this item
exists to make reachable. Nothing faster is offered: fat's time constant is
about 42 h, so no rate that leaves the chart legible reaches three of them.

The rate is drawn twice from one formatting function - on the control that
sets it, and in the slot the six compartment panels give to a MAC multiple,
directly under the clock - so the control and the readout cannot state the
same mode differently. It is drawn at 1x too, because a label that appeared
only above real time would make its own *absence* the signal.

*Not covered here, and not a gap in this item.* The chart still draws a
window of at most 300 simulated seconds, so at 60x and above it scrolls past
in seconds. The readouts are correct at every rate and the axis says which
simulated seconds it is showing, so nothing is misleading - it is unreadable
rather than wrong. `PL-SSBP` (add the chart time-base selector with 15, 30
and 60 minute scales plus Fit run) is the item that makes the fast rates
legible on the chart, and it is the next one this feature offers.
