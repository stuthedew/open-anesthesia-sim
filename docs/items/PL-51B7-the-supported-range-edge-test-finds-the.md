---
id: PL-51B7
title: The supported-range edge test finds the functions behind the six guards other than the step's by parameter name on five classes kept by hand, so a function taking a guarded quantity under another name, RunDefinition's opened_at_s, is never drawn; a checked type per quantity, as SimulationStep is for the step, would let it find every one by type
status: untriaged
feature: numerical-domain
added: 2026-10-04
---

**Problem.** The supported-range edge test finds the functions behind the six guards other than the step's by parameter name on five classes kept by hand, so a function taking a guarded quantity under another name, RunDefinition's opened_at_s, is never drawn; a checked type per quantity, as SimulationStep is for the step, would let it find every one by type

**Question for the project owner, 2026-10-04:** give every supported-range
quantity a checked type now, in the three slices below? **Recommendation:**
yes, in that order. The answer is pending.

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
