---
id: PL-WK2B
title: docs/INTERFACE.md says each chart point is computed by formula from the run's definition and that no stored series lies behind a trace, but the chart reads the run's stored states
status: done
feature: interface-matches-its-spec
touches: docs/INTERFACE.md
added: 2026-11-22
closed: 2026-11-22
pr: 2234
verify: ! grep -qF 'No stored series of values lies behind a trace' docs/INTERFACE.md
---

**Problem.** docs/INTERFACE.md says each chart point is computed by formula from the run's definition and that no stored series lies behind a trace, but the chart reads the run's stored states

**Where.** Three passages of `docs/INTERFACE.md` describe a design the code
no longer has. Under the section on what the chart draws: "The model computes
each point from the run's definition, which gives the run's state at any
instant directly, by formula. No stored series of values lies behind a trace,
so none can disagree with it." In the developer note on the interface
boundary: "The controller evaluates them from the run's definition
(`SimulationController.drawn_window`, `core/run_definition.py`). Keeping no
stored samples of the run is a decision…", and "The stored state drawn at a
control change is a keyframe, not one propagated from an earlier instant."
The headings are those on the branch of `PL-SY7G` (the sorting of
`docs/INTERFACE.md`), which leaves the three passages word for word.

**What the code does.** `SimulationController.drawn_window` in
`src/anesthesia_sim/app/controller.py` returns "the states to plot across an
axis, each read from this run's stored states", the state the run stored for
each whole second (`SimulationState.stored_states`), so a point on a trace is
the value the readout showed at that second (`PL-MH9J`, #2180).

**Why it matters.** `docs/INTERFACE.md` is the specification a contributor
reads before changing the chart. A contributor who trusts it may add a
second, formula-based path for drawn values, which could then disagree with
the readout, the stale-state hazard the stored states exist to remove.

**Fix.** Rewrite the three passages to say what the code does, with the
reason from `PL-MH9J`, and check the rest of `docs/INTERFACE.md` for other
statements that predate whole-second stepping.

**Found by** the first pass of `PL-SY7G`, 2026-11-22, and checked against
`drawn_window`'s docstring.

**Generator check.** A one-off. The three passages described the chart's design before whole-second stepping (#2180, PL-MH9J) brought in the stored states, and that change rewrote the sections it knew of but not these. The interface document's sort (`PL-SY7G`) read every paragraph against the code, and its blind review caught them. The cause, a design change that leaves an older description elsewhere in the specification, is what the sort by reader and its reviews exist to find.

**Closed 2026-11-22 by `PL-SY7G`** (#2234). Its review fold rewrote the three passages: each drawn point is now the state the run stored for that second (`SimulationController.drawn_window`, `SimulationState.stored_states`), and the state drawn at a control change is the stored one, like every other.
