---
id: PL-0GJC
title: The simulation step is a bare float in 15 signatures and 2 fields, and its 1 ms floor is checked at 4 call sites, so each entry point that skips the check becomes a capture: carry it as a SimulationStep type that refuses an unsupported step when it is constructed
priority: P2
effort: M
status: needs-decision
classes: refactor
feature: numerical-domain
touches: src/anesthesia_sim/core/simulation_step.py, src/anesthesia_sim/core/uptake_system.py, src/anesthesia_sim/core/supported_ranges.py, src/anesthesia_sim/core/simulation.py, src/anesthesia_sim/app/playback.py, src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/chart_frame.py, tests, docs/MODEL.md, docs/ARCHITECTURE.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-03 session that claimed it
added: 2026-10-03
payoff: a run's step is checked once, where it is chosen, so the next function written to take one cannot be the next entry point that forgot the 1 ms floor
---

**Problem.** The simulation step is a bare float in 15 signatures and 2 fields, and its 1 ms floor is checked at 4 call sites, so each entry point that skips the check becomes a capture: carry it as a SimulationStep type that refuses an unsupported step when it is constructed

**Found 2026-10-03**, answering the project owner's question how to stop the
day's predictable failures recurring. `PL-74T0`'s third cluster is one fact
captured five times - `PL-YZ17`, `PL-5F76`, `PL-BPRK`, `PL-WP52` and
`PL-6QYJ`, after `PL-73ZN`, `PL-BMY5` and `PL-8H2R` - and each fix added the
guard one function was missing. Counted on `main` at `7a6ec289`:
`simulation_step_s: float` is 15 parameters across `core/` and `app/` (four of
them the guard and count functions in `supported_ranges.py` and
`uptake_system.py`) and 2 dataclass fields, and
`require_supported_simulation_step` is called from 4 places -
`SimulationState.__post_init__`, `SimulationState.advance`,
`AgentUptakeSystem.advance` and `app/playback.py`'s `steps_per_tick`. Each
compartment's own `advance` checks only `require_positive_finite`, which is
`PL-WP52`'s open question.

**Why it matters.** The five captures were one fact - that a run's step lies
inside the supported range - re-checked by hand wherever the last fix reached,
and each entry point that missed it handed the arithmetic a step nothing had
verified. Below the floor, rounding is a growing share of what each step
changes and the number it produces stays plausible (`docs/MODEL.md` §
"Supported simulation step"); far below it, `maximum_step_count` raised
`OverflowError` from outside the simulator's own exceptions (`PL-YZ17`). A step
checked once, where it is chosen, turns the next forgotten check into a mypy
error in `src/` and a `TypeError` anywhere else, rather than another capture.

**Decided 2026-10-03: yes** (project owner, 2026-10-03, ratified, over a
guard added to each compartment by hand and over the `NewType` and
frozen-dataclass designs): the step becomes the `float` subclass recommended
below, with the runtime backstop the holes paragraph names.

**Recommended:** a `SimulationStep` class that subclasses `float` and calls
`require_supported_simulation_step` in its `__new__`, taken by every function
that now takes `simulation_step_s: float`. Construction becomes the one place a
step is checked, `mypy --strict` refuses a bare float at every annotated
parameter, and `PL-WP52` is answered by the type rather than by a fifth guard:
a compartment cannot be handed a step nobody checked. Checked in a scratch
module with mypy 1.20.2 `--strict` on Python 3.11: mypy refused a bare `0.5`
for each of the three designs here, and at runtime the float subclass and a
frozen dataclass refused `4.7e-304` while a `NewType` cast returned it
unchanged. Arithmetic on the subclass returns a plain `float`, so a derived
quantity does not carry the step's guarantee by mistake.

Why not the other two:

- **`NewType`**, the pattern `src/anesthesia_sim/core/concentration.py` uses
  for `Fraction` and `Percent`, is the static half only. It suits a unit label,
  where every float is a valid value; a step has a range, and a cast is an
  unchecked assertion - `src/` already holds 24 `Fraction(...)` casts.
- **A frozen dataclass** validating in `__post_init__`, the shape
  `src/anesthesia_sim/core/tissue.py`'s states use, refuses just as well but
  puts `.seconds` into every equation that divides by the step, against
  `.claude/rules/core-domain.md`'s "the equation visible rather than buried".

**Two holes the type leaves, both measured.** `pyproject.toml`'s
`[tool.mypy] files` holds `src`, `tools`, `.claude/hooks` and
`subprojects/docket/src`, not `tests`, so the 212 places in 29 test files that
pass a step are never type-checked. And a value typed `Any` passes mypy: an
`Any`-typed `4.7e-304` reached the scratch function and returned `inf`.
pyqtgraph is untyped here. So each run-level entry keeps one
`isinstance(step, SimulationStep)` check that raises, or `tests` joins mypy's
scope under `check_untyped_defs`, after counting the errors that surfaces.

**What undoing it would cost.** 15 parameter and 2 field annotations, 23 call
sites in `src/` (a grep for `.advance(`, `.advance_fresh_gas(` and
`simulation_step_s=`), and the 212 test call sites if tests construct the type.
Nothing stored or displayed changes, so reverting is the annotations alone.

If the owner takes this, `PL-74T0` records this item as its third cluster's
head. The same shape fits the other ranges `supported_ranges.py` declares, but
the step is the one with five captures behind it, so it goes first and alone.

**Decision needed.** Whether a compartment stepped on its own takes this type.
The case ratified on 2026-10-03 did not carry one cost, found when the work
began: `require_supported_simulation_step` checks the 0.1 s ceiling as well as
the floor, and the ceiling is the coupled system's - how long its settings are
held constant - which the guard's own docstring and `docs/MODEL.md` §
"Supported simulation step" both say binds the run and not a compartment.
Taken by `BreathingCircuit.advance_fresh_gas` and `.advance`,
`TissueGroup.advance` and `VenousBloodCompartment.advance`, the type would refuse a
compartment stepped alone at 1 s, which is correct today. The floor alone is
`PL-WP52`'s question, and it asks for a compartment to be measured alone first.

**Recommended:** this item covers the run's step - the 10 parameters and 2
fields that take the step a run is taken at - and the compartment clause of
"Done when" moves to `PL-WP52`, which decides a compartment's floor on its
measurement and, if the answer is yes, whether a floor-only type carries it.
The alternative is a second, floor-only type the compartments take now, which
answers `PL-WP52` without the measurement. The run's half is the same under
either answer, so it is built while this is open.

**Built 2026-10-03, the run's half, while the question is open.**
`core/simulation_step.py` now holds the two bounds, their guard and
`SimulationStep`, moved out of `core/uptake_system.py` because
`supported_ranges.py` needs the type and `uptake_system.py` already imports it.
The 10 parameters and 2 fields take a `SimulationStep`; the four run entries
call `require_simulation_step`, which raises `TypeError` for anything else;
`app/dashboard_frame.py`'s shipped step is built as one; 124 places in 20
existing test files build the step, so each refusal test there now meets the
constructor's refusal with the same message; and
`tests/unit/test_simulation_step.py` pins the type and the four entries. One
test was passing for the wrong reason once the check landed - it injects a
`TypeError` mid-step and expected to see it, and a bare float raised one first -
and now builds its step. The compartments are unchanged. The `verify:` is
removed until the answer: no command can tell the two answers' remaining work
apart, and the one written for the run's half passes now, which
`docket check` refuses on an open item.

**Done when.** Every function that takes a run's step takes a
`SimulationStep`; the step is checked once, when constructed; a compartment
refuses a step below `MINIMUM_SIMULATION_STEP_S`; and a test pins that a bare
float reaching a run's entry raises instead of computing.
