---
id: PL-0GJC
title: The simulation step is a bare float in 15 signatures and 2 fields, and its 1 ms floor is checked at 4 call sites, so each entry point that skips the check becomes a capture: carry it as a SimulationStep type that refuses an unsupported step when it is constructed
status: untriaged
feature: numerical-domain
added: 2026-10-03
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

**Done when.** Every function that takes a run's step takes a
`SimulationStep`; the step is checked once, when constructed; a compartment
refuses a step below `MINIMUM_SIMULATION_STEP_S`; and a test pins that a bare
float reaching a run's entry raises instead of computing.
