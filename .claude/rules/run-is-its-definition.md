---
paths:
  - "/src/anesthesia_sim/core/run_definition.py"
  - "/src/anesthesia_sim/core/simulation.py"
  - "/src/anesthesia_sim/app/controller.py"
  - "/src/anesthesia_sim/app/run_series.py"
  - "/src/anesthesia_sim/app/chart_frame.py"
---

# The run is its definition, so there is no sample store to add to

The run is its definition - patient, agents and the ordered control-input
timeline. Every compartment value at every instant is a closed-form function
of it, so the chart evaluates rather than reads back, and there is no sample
store to add to. Storage is warranted only for a series that **cannot be
re-derived from its inputs**, which nothing in the simulator produces.

That is a precondition on the files this rule loads for rather than a
prohibition to argue with. It is written down because "record each sample as
the simulation steps" is the obvious design, it is what this project did for
nine releases, and after `PL-T691` it is wrong - so a session re-introducing a
store does it while believing it is being helpful, with every instinct pointing
that way.

## Nothing in the tree would catch it

A cache of samples beside a closed-form sampler is correct on the frame it is
written, plausible to a reviewer, and a second source of truth for the same
trace. Every test still passes, because each source is self-consistent on its
own; the two disagree only once one of them goes stale, which is a run later
and a reader's problem rather than a suite's. `CLAUDE.md` § "Safety-critical
clinical-output standard" makes a second divergent source for a displayed
clinical value a safety failure rather than a design preference - a reader
comparing a readout against the curve beside it is comparing two answers to one
question and has no way to know it.

## The test is what the collection is indexed by

Not "is this a cache?", which admits and refuses the right things by accident.
Ask what one entry corresponds to.

- **Indexed by something in the definition** - one state per control event, one
  at the run's opening - is part of the answer rather than a record of it.
  `run_definition.Keyframe` is exactly this: how many there are is fixed by the
  definition, each is computed canonically, and a change to the definition
  invalidates the segment that would have read it. Two runs built from
  identical definitions hold identical keyframes.
- **Indexed by the watching** - one entry per step taken, per frame drawn, per
  window scrolled, per instant a reader happened to look at - is a record of
  the run. It grows with elapsed time rather than with the definition, so it is
  a function of the definition *and* of how the run was observed. That second
  argument is the second source of truth: two runs built from identical
  definitions can hold different ones.

The second is what "cannot be re-derived from its inputs" rules out, and
nothing in this simulator produces it.

## If the motivation is speed, it was measured and it is not there

The instinct that a long run must be slow to draw is the usual reason a store
gets proposed. `docs/MODEL.md` § "The run is that record, and every state is
derived from it" answers it with numbers: a one-hour window at 600 columns
costs 10.6 ms on a two-hour run and 13.0 ms on a thirty-day one, against
62.6 ms at four hours and 207.7 ms at twelve on the recorded path. Answering a
window stopped depending on how long the run has been going, which is the whole
of what the change bought.

Where cost does still move is the number of control changes inside the window,
since each stretch in view needs its own propagator: 14.2 ms with two changes
in view, 231 ms with sixty, about 1.1 s with six hundred. That is the regime
where the columns are sparser than the changes, in which sampling 600 instants
aliases the run whatever it samples - a question about what to draw, which
storage answers no part of.

## Two names here say "recorded" and mean "addressed"

`run_series.RecordedQuantity` and `RecordedSeries` name what a trace *is* - one
substance's values for one quantity - and they predate the change. Nothing is
recorded behind either, and `RecordedSeries` was kept deliberately when the
store went, because binding a trace to one substance-and-quantity pair is a
presentation-safety guard rather than a storage concern (`PL-2FM6`). Read them
as the vocabulary a drawn value is addressed by. Do not read them as evidence
that a record exists somewhere to be extended.

## If you do have a series that cannot be re-derived

Then this rule does not reach it and the downsampling question is a real one.
`PL-8LXM`, the item that deleted the chart-downsampling module, preserves the
prior M4 implementation, the Jugel et al. 2014 citation in full, and the
analysis of what M4 does and does not guarantee - including where that
implementation departed from the paper's Theorem 1. Start from the item rather
than from scratch.

That pointer rides on the rule and is not the reason for it. A rule whose only
job is remembering a deleted file fires forever and changes no decision, which
is what `CLAUDE.md` § "Prefer deterministic tooling over repeated model work"
calls a defect in the check. This one earns its place every time it fires,
because the regression it prevents is likelier than the recovery it enables.

## Why these five paths

`PL-49R8` named three, two of them by description because the tree was expected
to move under them, and it has: the sampler entry point from `PL-T691` is
`core/run_definition.py`; the chart-series module it named is now
`app/run_series.py`, split out of the controller by `PL-RD3B`; and what replaced
`app/simulation_view.py`'s frame path is `app/chart_frame.py`.

Two more are here because the rule's own opening sentence names them.
`core/simulation.py` holds the stepper, which is where "record each sample as
the simulation steps" would literally be written. `app/controller.py` is where
the sample store actually lived - `RunHistory`, `SimulationHistorySample` and
the M4 aggregate cache were 531 of its lines until `PL-2FM6` deleted them - and
it still holds `drawn_window`, the chart's read, which is the method a cache
would be hung on.
