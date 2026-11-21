---
paths:
  - "/src/anesthesia_sim/core/run_definition.py"
  - "/src/anesthesia_sim/core/simulation.py"
  - "/src/anesthesia_sim/core/stored_states.py"
  - "/src/anesthesia_sim/app/controller.py"
  - "/src/anesthesia_sim/app/run_series.py"
  - "/src/anesthesia_sim/app/chart_frame.py"
---

# Each second of a run has one stored state, and every reader takes it from the run's record

A run takes one step per second. Each step appends the state it wrote to the
run's record, `SimulationState.stored_states`, a `StoredStates` in
`src/anesthesia_sim/core/stored_states.py`. The record holds one state for
each whole second, from the second the run opened at to the second it has
reached.

The owner chose this design in `PL-7CY5` (project owner, 2026-11-21,
ratified, on the thread's decision card, over one rule at tenths of a second
and over keeping a run as its settings with every state computed from them).
`PL-MH9J` built the record. Before it, a state was computed by three routes
that agreed only to rounding, and a MAC target once read as reached on a run
and not on a branch opened at the same step (`PL-QVBR`).

## Read a reached second's state from the record

Code that shows a state, tests a mark against one or opens a branch from one
calls `stored_states.state_at(CaseInstant(second))`. The controller's readers
are the instances to copy, in `src/anesthesia_sim/app/controller.py`:

- `snapshot()` reads the readouts' six fractions through `_stored_fractions`.
- `drawn_window` reads the chart's states at the seconds that
  `drawn_seconds` returns (`src/anesthesia_sim/app/chart_time_base.py`).
- `_step_ending_here` reads the two states that decide whether a step
  crossed a mark.
- `_open_at` opens a branch with its parent's stored states up to the fork,
  and places the branch's system at the last of them.

The step is the only code that computes the state of a reached second. A
second reader reads the record again. It does not step again, apply a
formula, or read a compartment back from the uptake system: 9% to 14% of the
fractions read back from a compartment differ in the last bit from the
fraction the step wrote (`PL-MH9J`, measured 2026-11-21).

## Draw and show whole seconds only

The record holds no state between two seconds, and `StoredStates.state_at`
refuses a second it does not hold. A chart point, a readout and a mark each
fall on a whole second. A value between two stored seconds would be a second
route to a displayed number, so nothing interpolates one.

## Keep states in the record and nowhere else

A reader takes the states it needs from the record each time it runs. It
keeps no list of states of its own between calls. A branch holds its own
record. It is a copy of its parent's record up to the fork
(`StoredStates.through`), and the branch's steps append to the copy
(`PL-FST0`). So a branch opens at any whole second that its parent has
reached.

The record also stores, for each second, the compensation terms of the
delivered and the exhausted totals (`TotalsCompensation`). A branch continues
both totals from the terms stored for the fork, so its totals equal its
parent's bit for bit while no setting differs. Code that places a system at
a stored state passes the terms stored beside it
(`AgentUptakeSystem.resume_at`).

## The preview computes by formula until `PL-Z6C8`

`preview_window` shows what the run would do past the second it has reached,
so the record holds no state for it. It opens a prediction from the stored
state at the reach and evaluates it with `RunDefinition.evaluate_anchored`.
`RunDefinition` still holds a run's settings and one keyframe per setting
change, and its `state_at`, `evaluate` and `evaluate_anchored` remain for
the preview and for tests. `PL-Z6C8` removes the evaluation paths that
nothing reads and decides how the preview is computed.

## `RecordedQuantity` and `RecordedSeries` name a trace

`run_series.RecordedQuantity` and `RecordedSeries` name what a trace is: one
substance's values for one quantity. `RecordedSeries` binds a trace to one
pair of substance and quantity, so a value cannot be drawn under another
agent's name (`PL-2FM6`). The states behind a trace are in the run's
`StoredStates`.

## A window with more seconds than columns

The chart draws one stored state per column, both ends of the window and
each second at which a setting changed. Between two of those seconds it also
draws the second at which each compartment is highest and the second at which
it is lowest, where that value lies outside the values at both ends
(`extreme_seconds` in `src/anesthesia_sim/app/chart_time_base.py`,
`PL-BLZJ`). `PL-8LXM` holds the earlier M4 implementation, the Jugel et al.
2014 citation and the analysis of where that implementation departed from the
paper's Theorem 1.

## Why these six paths

`core/simulation.py` holds the step that stores each state, and
`core/stored_states.py` holds the record. `core/run_definition.py` holds the
evaluation paths that a new reader must not use for a reached second.
`app/controller.py` holds the readers, `app/run_series.py` holds the drawn
window they fill, and `app/chart_frame.py` draws it.
