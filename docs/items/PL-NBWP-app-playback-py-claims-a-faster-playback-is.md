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

**Measured 2026-09-06, before the decision, because all three options need the
same numbers and the item's own estimate was an extrapolation.** Harness in the
session scratchpad; it drives `AgentUptakeSystem` directly and never imports
`app/`, and its 1x column reproduces `docs/MODEL.md` § "Supported simulation
step"'s published table to the digit (6.66e-3, 5.03e-2, 1.43e-1 pp), which is
what makes the other columns comparable with it.

Worst displacement of any of the six displayed compartment fractions when the
control change lands one *tick* later instead of one *step* later, over all
three agents, in percentage points of one atmosphere:

| Manoeuvre | 1x | 5x | 20x | 60x | 300x |
| --- | --- | --- | --- | --- | --- |
| Case opening: dial off to 1 MAC, reference flows | 6.7e-3 | 3.3e-2 | 1.3e-1 | 3.8e-1 | 1.5 |
| Unperfused load, then perfusion on and dial off | 5.0e-2 | 2.5e-1 | 9.8e-1 | 2.8 | 10.0 |
| Ventilator start at the envelope corner | 1.4e-1 | 7.0e-1 | 2.5 | 5.8 | 10.4 |

Desflurane binds every cell; the compartment is alveolar except the two circuit
cells at 60x and 300x on the unperfused load and every cell of the case opening.

**Three corrections this forces to the paragraphs above.**

1. **The displacement is not linear in the delay, and this item's "Timing
   displacement is exactly linear" over-states 300x by about four times.**
   `docs/MODEL.md`'s linearity statement is about halving the *step* at 1x and
   is not touched; extrapolating it across a 30 s delay is what fails, because
   the transient saturates. Linear from the 1x ventilator start would predict
   43 pp at 300x against 10.4 pp measured; the error is 3% at 5x, 12% at 20x,
   32% at 60x and 76% at 300x.

2. **The burst is not the binding term, so servicing events inside it buys
   almost nothing.** A step costs 33.1 us here, so a burst occupies 0.03 ms of
   the 100 ms tick at 1x, 0.17 at 5x, 0.66 at 20x, 2.0 at 60x and 9.9 at 300x -
   at worst a tenth of the tick. Simulated time is frozen for the other nine
   tenths, so a control event arriving then is already applied before the next
   burst and lands on the same tick boundary either way. Interruptibility
   changes the outcome only for the ~10% of events at 300x that arrive during
   the burst itself, and for those it makes *which step* the change lands on a
   function of where the host's scheduler happened to be. It does not move the
   bound; it makes the resolution non-uniform and host-dependent.

3. **The reachable grid, not a lateness, is what the rate coarsens.** The
   recorded `ControlChange.elapsed_s` is `SimulationState.elapsed_s` at the
   moment of the call and the setting first acts over the step beginning there,
   at every rate, so the control timeline is never wrong and nothing lands
   later than it is stamped. What the rate decides is which simulated instants
   a live control action can be placed at: multiples of `multiplier x 0.1` s.
   The table above is therefore the cost of one grid step, which is the right
   quantity for the disclosure and not a lag.

**Two facts the options should be weighed against.**

- **The display is coarser than the control grid at every rate, by exactly
  two.** `RENDER_INTERVAL_S` is 0.2 real s against the 0.1 s tick, so frames
  are 0.2, 1, 4, 12 and 60 simulated seconds apart at the five rates while the
  grid is 0.1, 0.5, 2, 6 and 30. Tightening the grid below the frame interval
  buys resolution no reader can observe unless the render cadence moves too.
- **An exact route already exists and is free.** `_run_simulation_timer`
  skips the burst while `is_running` is false and the controller's four setters
  apply unconditionally, so pause, change, resume times a control change to the
  step at any rate. It is documented nowhere.

**Done when.** One of the three options is chosen, and after it the three places
agree with each other and with the behaviour: `playback.py`'s docstring,
`core/uptake_system.py`'s `MAXIMUM_SIMULATION_STEP_S` comment, and
`docs/MODEL.md` § "Supported simulation step" each state the control resolution
*as a function of the playback rate*, or state a bound the implementation now
actually holds at every rate. If the behaviour changes rather than the prose, a
test pins it — a control change applied during a fast burst takes effect within
the stated resolution — because a claim about interruptibility that no test
holds is how this one survived.
