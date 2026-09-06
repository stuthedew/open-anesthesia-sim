---
id: PL-NBWP
title: app/playback.py claims a faster playback is 'never a modelling one', but the uninterruptible tick burst makes control resolution multiplier x 0.1 s - 30 s at 300x
status: untriaged
added: 2026-09-06
---

**Problem.** app/playback.py claims a faster playback is 'never a modelling one', but the uninterruptible tick burst makes control resolution multiplier x 0.1 s - 30 s at 300x

**Why it matters.**

**Where.**

**Done when.**

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

**Options, not yet decided.** Service pending control events between steps of a
burst; or cap the burst; or leave the behaviour and correct the claim in all
three places, disclosing the per-rate control resolution. The last is the
cheapest and may be right for a teaching tool - a reader at 300x is watching a
wash-in, not titrating - but it is the project owner's call because it decides
what the application promises.

**Found.** `PL-X9KD`, 2026-09-06, while measuring what control-timing
quantization costs a displayed value.
