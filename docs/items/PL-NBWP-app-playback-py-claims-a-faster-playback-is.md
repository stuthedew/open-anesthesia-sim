---
id: PL-NBWP
title: app/playback.py claims a faster playback is 'never a modelling one', but the uninterruptible tick burst makes control resolution multiplier x 0.1 s - 30 s at 300x
priority: P1
effort: M
status: needs-decision
classes: safety, docs
feature: presentation-safety
touches: src/anesthesia_sim/app/playback.py, src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/core/uptake_system.py, docs/MODEL.md
added: 2026-09-06
---

**Problem.** `src/anesthesia_sim/app/playback.py`'s module docstring states that
playing a run faster is "a *scheduling* change and never a modelling one: the
same steps are taken, in the same order, at the same size". That holds for a run
nobody touches. It is false for a run in which a control moves, and the
interface exists to be touched.

`steps_per_tick` returns `multiplier * tick_interval_s / simulation_step_s`,
which with the shipped constants is exactly `multiplier`.
`simulation_view.py:3011-3015` then takes those steps in a plain
`for _ in range(steps)` loop with no `await` in it, and Flet dispatches sync
handlers inline on the same event loop, so no control event can land inside a
burst. The interval over which a control change is invisible to the model is
therefore `SIMULATION_TICK_INTERVAL_S x multiplier` - 0.1 s at 1x, but 0.5, 2, 6
and 30 simulated seconds at 5x, 20x, 60x and 300x.

**Why it matters.** `core/uptake_system.py`'s `MAXIMUM_SIMULATION_STEP_S` is now
a *declared control-resolution tolerance* (`PL-X9KD`), measured in percentage
points of displacement per step of delay. That derivation is stated at 1x and is
the only rate at which it holds. Timing displacement is exactly linear in the
delay, and `PL-X9KD` measured a ventilator start at 1.4e-1 pp per 0.1 s of
delay, so at 300x the same manoeuvre is displaced by 30 s and the alveolar
reading by something of order tens of percentage points. A reader changing a
setting at speed is watching a trajectory whose control timing is coarser than
anything the documentation states, and nothing fails.

**Where.** `src/anesthesia_sim/app/playback.py` module docstring;
`src/anesthesia_sim/app/simulation_view.py:3005-3015` (`_run_simulation_timer`'s
burst); `core/uptake_system.py`'s `MAXIMUM_SIMULATION_STEP_S` comment and
`docs/MODEL.md` § "Supported simulation step", both of which state the tolerance
without naming the rate it holds at.

**Decision needed.** What the application promises about control timing at
speed, choosing among the three options below. This is the owner's call rather
than an implementation choice: the cheapest answer is to keep the behaviour and
correct the claims, which changes what a reader is told the tool guarantees.
`PL-NBCJ` is blocked on the answer.

**Options, not yet decided.** Service pending control events between steps of a
burst; or cap the burst; or leave the behaviour and correct the claim in all
three places, disclosing the per-rate control resolution. The last is the
cheapest and may be right for a teaching tool - a reader at 300x is watching a
wash-in, not titrating - but it is the project owner's call because it decides
what the application promises.

**Found.** `PL-X9KD`, 2026-09-06, while measuring what control-timing
quantization costs a displayed value.

**Verified at triage, 2026-09-06.** Both mechanical claims hold in the tree as
it stands. `playback.py`'s docstring says playing faster is "a *scheduling*
change and never a modelling one: the same steps are taken, in the same order,
at the same size", and `simulation_view.py`'s run timer awaits
`SIMULATION_TICK_INTERVAL_S` and then runs `for _ in range(steps):
self._controller.advance(SIMULATION_STEP_S)` with no `await` inside the loop, so
the burst is uninterruptible as described.

**Classed `safety` at triage, and that is the load-bearing call.** Nothing here
computes a wrong number — every step is exact and the trajectory is
reproducible. What is wrong is what the reader is told about it: `docs/MODEL.md`
states the control-resolution tolerance without naming the rate it holds at, and
the module that converts a selected rate into steps asserts that the rate cannot
affect the model. Both are true at 1x only. `CLAUDE.md`'s standard makes that a
safety question rather than a documentation one — "the correct number with the
wrong ... stale state ... is still a safety failure" — because a reader who
moves a control at 60x is shown a trajectory whose control timing is six
simulated seconds coarser than anything the documentation admits to, and nothing
in the interface says so. `PL-NBCJ` is blocked on this item's answer.

**Done when.** One of the three options is chosen, and after it the three places
agree with each other and with the behaviour: `playback.py`'s docstring,
`core/uptake_system.py`'s `MAXIMUM_SIMULATION_STEP_S` comment, and
`docs/MODEL.md` § "Supported simulation step" each state the control resolution
*as a function of the playback rate*, or state a bound the implementation now
actually holds at every rate. If the behaviour changes rather than the prose, a
test pins it — a control change applied during a fast burst takes effect within
the stated resolution — because a claim about interruptibility that no test
holds is how this one survived.
