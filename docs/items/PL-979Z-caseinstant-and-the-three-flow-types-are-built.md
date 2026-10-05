---
id: PL-979Z
title: CaseInstant and the three flow types are built from another checked quantity silently - CaseInstant(StepCount(600)) is an instant of 600 s, CaseInstant(FreshGasFlow(5.0)) one of 5 s and FreshGasFlow(CaseInstant(5.0)) a flow of 5 L/min - because require_a_number admits every int and float subclass and only the stored-value checks (require_case_instant, _require_built) name a swapped quantity; refuse another checked quantity at the constructor, as Fraction refuses a Percent (found reviewing PL-7N8P)
priority: P1
effort: M
status: ready
classes: safety, defect
feature: parse-dont-validate
touches: src/anesthesia_sim/core/checked_number.py, src/anesthesia_sim/core/supported_ranges.py, src/anesthesia_sim/core/simulation_step.py, src/anesthesia_sim/core/concentration.py, tests/unit/test_checked_number.py
added: 2026-10-05
payoff: a count, a flow, a step or a concentration handed where another quantity belongs is refused at construction, never held as a plausible instant, flow, step or concentration under the type meant to prove it was checked
verify: grep -q 'def test_no_checked_type_is_built_from_another_checked_quantity' tests/unit/test_checked_number.py
---

**Problem.** CaseInstant and the three flow types are built from another checked quantity silently - CaseInstant(StepCount(600)) is an instant of 600 s, CaseInstant(FreshGasFlow(5.0)) one of 5 s and FreshGasFlow(CaseInstant(5.0)) a flow of 5 L/min - because require_a_number admits every int and float subclass and only the stored-value checks (require_case_instant, _require_built) name a swapped quantity; refuse another checked quantity at the constructor, as Fraction refuses a Percent (found reviewing PL-7N8P)

**Reproduced 2026-10-05, at triage, and wider than the title.** On Python
3.14.7, against `main` at `b67dace8`,
`uv run python -c "from anesthesia_sim.core.supported_ranges import CaseInstant, StepCount, FreshGasFlow, CardiacOutput; from anesthesia_sim.core.simulation_step import SimulationStep; from anesthesia_sim.core.concentration import Fraction, Percent; print([type(v).__name__ + ' ' + repr(v) for v in (CaseInstant(StepCount(600)), CaseInstant(FreshGasFlow(5.0)), FreshGasFlow(CaseInstant(5.0)), CardiacOutput(FreshGasFlow(5.0)), SimulationStep(Fraction(0.05)), Fraction(SimulationStep(0.05)), Percent(FreshGasFlow(2.0)))])"`
printed `['CaseInstant 600.0', 'CaseInstant 5.0', 'FreshGasFlow 5.0',
'CardiacOutput 5.0', 'SimulationStep 0.05', 'Fraction 0.05', 'Percent 2.0']`.
So the hole is every `float` checked type, not only the four the title names:
`SimulationStep` takes any other quantity, and `Fraction` and `Percent` refuse
only each other. `StepCount` is the exception, since nothing else checked is an
`int`. **`mypy --strict` passes all of these** - a checked `float` subclass is a
`float`, and an `int` is accepted where a `float` is annotated - measured on a
scratch file the same day with `CaseInstant(StepCount(600))`,
`FreshGasFlow(CaseInstant(5.0))` and `Fraction(SimulationStep(0.05))`, so unlike
the swapped arguments `PL-848D` and `PL-CX2C` record at the stored-value
checks, a slip of this shape in `src/` would type-check.

**Why it matters.** Each constructor is the one check its quantity gets, and
holding the type is the proof it ran (`.claude/rules/core-domain.md`). Built
from another quantity, the check runs on the wrong number and passes whenever
the two ranges overlap - a 600-step count is a 600 s instant, a 5 L/min flow a
5 s instant, a 0.05 s step a fraction of 0.05 - and the result is held under the
right type, so every `require_*` downstream admits it. That is the swapped
argument the stored-value checks were written to name, arriving one call
earlier where nothing names it: a plausible wrong instant, flow, step or
concentration, which `CLAUDE.md`'s safety-critical standard forbids, and one no
tool here would catch in `src/`.

**Done when.** Every checked `float` type - the three flows, `CaseInstant`,
`SimulationStep`, `Fraction` and `Percent` - refuses a value built as any other
checked quantity with a `TypeError` naming the parameter, the value and the
type it was built as, before any comparison runs, as `Fraction` refuses a
`Percent` today; the same type is admitted, so rebuilding an instant from an
instant is unchanged, and `Fraction` and `Percent` keep their convert-advice for
each other. The list of checked types this reads is one list, shared with the
stored-value checks `PL-848D` and `PL-CX2C` widen; where it lives without an
import cycle between `core/concentration.py`, `core/simulation_step.py` and
`core/supported_ranges.py` is the implementer's call, and the three items are
best worked in one branch. A test in `tests/unit/test_checked_number.py` named
`test_no_checked_type_is_built_from_another_checked_quantity`, parametrized
over every ordered pair of checked types, pins it.
