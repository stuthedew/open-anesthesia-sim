---
id: PL-51B7
title: The supported-range edge test finds the functions behind the six guards other than the step's by parameter name on five classes kept by hand, so a function taking a guarded quantity under another name, RunDefinition's opened_at_s, is never drawn; a checked type per quantity, as SimulationStep is for the step, would let it find every one by type
priority: P2
effort: M
status: done
classes: defect, test
feature: parse-dont-validate
touches: tests/unit/test_supported_range_edges.py
blocked-by: PL-0YYV, PL-CN5S
added: 2026-10-04
closed: 2026-10-04
pr: 1360
payoff: the edge test draws every function and record field that holds a guarded quantity, whatever it is named, so a way in added later is tested at its edges the day it is written
verify: ! grep -qF 'parameters.get(name) is checked' tests/unit/test_supported_range_edges.py
---

**Problem.** The supported-range edge test finds the functions behind the six guards other than the step's by parameter name on five classes kept by hand, so a function taking a guarded quantity under another name, RunDefinition's opened_at_s, is never drawn; a checked type per quantity, as SimulationStep is for the step, would let it find every one by type

**Question for the project owner, 2026-10-04:** give every supported-range
quantity a checked type now, in the three slices below? **Recommendation:**
yes, in that order.

**Decided 2026-10-04: build it, in that order** (project owner, 2026-10-04,
ratified, over a range check in the settings record alone and over building
the types only once another unchecked way in turned up, which the owner
refused in their own words as good enough and hope).

[superseded 2026-10-04: the Ship v0.6.0 project builds all three slices,
filed as items of their own, below] At the owner's direction, slice 1 went to
the session holding `PL-HSFV`'s claim, on branch `claude/bold-goodall-ekvvcr`.
Slices 2 and 3 follow it in order.

**Filed as three items, built by the Ship v0.6.0 project** (project owner,
2026-10-04, over building slice 1 on pull request 1342, which merged as
records only). Slice 1 is `PL-0YYV` and closes `PL-HSFV` with it; slice 2 is
`PL-CN5S`, blocked by slice 1; slice 3 is this item, blocked by both. All
three are on v0.6.0's frozen list with the rest of the `parse-dont-validate`
feature, there at the owner's direction the same day. One item per slice
because each slice is one pull request: a claim, a `verify:` and a `touches`
audit that each describe one change.

**Why it matters.** This test is the check that every function behind a
supported-range guard is exercised at the guard's IEEE 754 edges (`PL-V10T`).
Re-read 2026-10-04: for a guard whose quantity is still a bare `float`, `_takes`
draws a function only where `parameters.get(name) is checked`, `name` being
the guard's own parameter, and only on a class in `RECEIVERS`. So
`RunDefinition.__init__`'s `opened_at_s`, against the guard's `instant_s`, is
never drawn, and nor is a value carried inside a record, the gap `PL-HSFV`
went through. The test passes while those ways in go untested.

**Done when.** Slices 1 and 2 have landed, and
`tests/unit/test_supported_range_edges.py` finds every function and dataclass
field behind a guard by the guard's type, with the name matching in `_takes`
deleted, so it draws `UptakeEquationSettings`'s three flows and
`RunDefinition`'s instants at their edges.

**What it is.** Each quantity gets a type the way `PL-0GJC` gave the run's
step one, and every signature and record field in `core/` and `app/` that
holds the quantity takes the type. Three slices, each green on its own and
none redone by the next:

1. `FreshGasFlow`, `AlveolarVentilation` and `CardiacOutput`, in L/min:
   `float` subclasses built only through their `require_supported_*` guard,
   with a runtime check at each public entry point that refuses a bare
   `float`, as `require_simulation_step` does for the step.
   `UptakeEquationSettings`'s three flow fields take them, so the record
   `PL-HSFV` ran - cardiac output 1000 L/min - cannot be built, and the range
   check once recommended for that record on its own is never built. Closes
   `PL-HSFV`.
2. `CaseInstant`, in s, for `RunDefinition`, `app/bookmarks.py` and the
   instants a run is moved to; and `StepCount`, an `int` subclass checking
   what a count can be checked for alone - whole and nonnegative, which
   `simulation.py`'s `_require_step_count` checks today. A count's supported
   range depends on the step, so `SimulationState` keeps checking the pair.
3. The edge test, `tests/unit/test_supported_range_edges.py`, finds every
   function and dataclass field behind a guard by the guard's type, and its
   name matching is deleted. One way of finding them, and it reaches a value
   carried inside a record, the gap `PL-HSFV` went through. Closes this item.

Unchanged:

- The tissue and venous blood flows. No supported-range guard bounds them,
  and the record's sum check ties them to a cardiac output that is now
  checked.
- The circuit's deliverable-flow limit, which is the machine's statement
  rather than the model's. It stays on `BreathingCircuit` (`PL-8PS6`).

The data files' `default_*_l_min` values are parsed into the types where the
patient and the circuit are built from them. `docs/MODEL.md` § "Supported
input ranges" says where each range is enforced, and changes with slice 1.

**What it costs.** Counted on `main` at `45f8e9f3`:

- 42 signatures and fields in nine modules of `core/` and `app/` take a flow
  or an instant under the guard's own name. That is a floor, since a count by
  name misses the renamed ones this item is about.
- 53 call sites in `src/`.
- 375 call sites in 26 test files.

For scale, `PL-0GJC` changed 15 parameters and 2 fields. A notebook caller
writes `CardiacOutput(5.0)` where it wrote `5.0`, as it already writes
`SimulationStep(0.1)`.

**Why this replaces the advice this item was filed with.** The first
recommendation was to build the types only if another unchecked way in turned
up. It was wrong on two counts:

- **It used the wrong heuristic.** That was the rule of three. Fowler's
  *Refactoring* attributes it to Don Roberts, as a guard against extracting
  an abstraction before enough cases show what it should be. Here the
  abstraction was already chosen and proven: `PL-0GJC` built it the day
  before.
- **It skipped the count** that `.claude/rules/expert-review.md` § "Count
  what undoing it would cost" requires. The step's range, checked by hand at
  each entry point, was captured eight times before it was typed (`PL-0GJC`
  lists them). The flows are checked the same way, and `PL-HSFV` is their
  first leak. Waiting for the next one is the hope this project's horizon
  rules out.

The project owner refused the deferral on 2026-10-04, in the session that
filed this item. `PL-YJY3` records why the rule did not stop it.

**Built 2026-10-04, as slice 3, in the Ship v0.6.0 project.** A function is
behind a guard wherever one of its parameters is annotated with a type the
guard's quantities are checked as, on any class and under any name; `_takes`
and `TAKEN` are deleted. Measured on this branch, the test finds 50
guard-and-function pairs where `main`'s found 32, and loses none. The 18 it
adds are `RunDefinition.__init__` and `Keyframe.__init__`; the circuit's, the
alveolar compartment's and the patient's constructors and flow setters;
`UptakeEquationSettings.__init__` once per flow; the three bookmark
constructors' and methods' instants; and `SimulationController.resumed_at` and
`BranchedCase.fork_at`.

- **Records.** A constructor is drawn from the record `RECEIVERS` builds, with
  only the drawn field replaced. Cardiac output is built through `TIED`,
  because the settings record checks that the tissue flows sum to it. A
  constructor that refuses a value its guard admits fails the test by name,
  so a tie nobody wrote into `TIED` cannot quietly draw nothing. Three records
  hold a checked quantity and only store it: `RunFrame`, `SimulationSnapshot`
  and `ResumePoint`. None computes with it; `SimulationSnapshot.has_recorded_run`
  only compares two instants.
- **A type taken twice.** `TimeBookmark.crossed_between`,
  `BookmarkSet.crossings_between` and `BookmarkSet.standings` each take two
  instants. The drawn value goes in the first place and every admitted edge
  in turn in the second, so the edge-by-edge product is covered. Handing the
  drawn value to both places, which was the first draft, can never draw a
  span with a mark inside it. The bookmark receivers now mark the middle of
  the span for the same reason.
- **The allowance for infinity.** `BreathingCircuit.time_constant_s` may
  compute `inf`, at zero flow and where a subnormal flow overflows the
  quotient. Nothing else may.

**Checked by planting defects, one at a time.** Each defect below was put into
`src/` alone, the edge test was run against it, and the tree was restored with
`git checkout`: `RunDefinition` opened at the span's end divides by zero; a
bookmark crossed at the span's end divides by zero; the circuit's time
constant is `nan` at the flow maximum; the settings record's ventilation per
second overflows at zero. `main`'s test passes all four and this one fails on
each. It runs in about 5.5 s where `main`'s took about 19.5 s, because each
signature's type hints are read once rather than on every draw.

**Found on the way, filed and not fixed:** `PL-B26Y`. The circuit's own
fresh-gas step reports a `nan` exhaust at an admitted subnormal flow. This
test cannot reach it, because the circuit's own step takes a `float`
(`PL-0GJC`).
