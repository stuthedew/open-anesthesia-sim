---
id: PL-848D
title: require_simulation_step advises rebuilding what it refuses from the same value - SimulationStep(0.1) for a CaseInstant(0.1) handed in as the step, which would build a 0.1 s step from an instant - and _require_built names only the three flows as swapped arguments; both print with repr, so an int past 4,300 digits raises ValueError instead of TypeError (measured 2026-10-04); bring both to the refusal require_case_instant and require_step_count use, _CHECKED_QUANTITIES and _shown (found folding #1354's review)
priority: P2
effort: S
status: ready
classes: defect
feature: parse-dont-validate
touches: src/anesthesia_sim/core/simulation_step.py, src/anesthesia_sim/core/supported_ranges.py, tests/unit/test_simulation_step.py, tests/unit/test_supported_ranges.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-04 triage pass
added: 2026-10-04
payoff: a quantity handed in where the step or a flow belongs is named as the swapped argument it is, never prescribed a rebuild that stores the wrong quantity under the right type, and no refusal of either check can itself raise
verify: grep -q 'def test_another_quantity_handed_in_as_the_step_is_refused_as_a_swapped_argument' tests/unit/test_simulation_step.py && grep -q 'def test_a_step_a_count_or_an_instant_handed_in_as_a_flow_is_refused_as_a_swapped_argument' tests/unit/test_supported_ranges.py
---

**Problem.** require_simulation_step advises rebuilding what it refuses from the same value - SimulationStep(0.1) for a CaseInstant(0.1) handed in as the step, which would build a 0.1 s step from an instant - and _require_built names only the three flows as swapped arguments; both print with repr, so an int past 4,300 digits raises ValueError instead of TypeError (measured 2026-10-04); bring both to the refusal require_case_instant and require_step_count use, _CHECKED_QUANTITIES and _shown (found folding #1354's review)

**Reproduced 2026-10-04, at triage.** On Python 3.14.7, against `main` at
`8cc0698d`,
`uv run python -c "from anesthesia_sim.core.simulation_step import require_simulation_step as step; from anesthesia_sim.core.supported_ranges import CaseInstant, StepCount, require_fresh_gas_flow as flow; exec('for check, value in ((step, CaseInstant(0.1)), (flow, StepCount(5)), (step, 10**5000), (flow, 10**5000)):\n try: check(value)\n except Exception as e: print(type(e).__name__, e)')"`
printed four refusals. The step's check told a `CaseInstant(0.1)` to "build
the run's step as SimulationStep(0.1) where it is chosen", and the fresh gas
flow's told a `StepCount(5)` to "build it as FreshGasFlow(...) where it is
set": each prescribed a rebuild of a value already built and checked as
another quantity. The other two raised `ValueError` ("Exceeds the limit (4300
digits) for integer string conversion") from the `repr` each message prints,
where both Raises sections name `TypeError`. `require_case_instant` and
`require_step_count` already name a value built as any of
`_CHECKED_QUANTITIES` as a swapped argument and print through `_shown`, so the
fault is the step's check and `_require_built` alone. Found while reproducing:
`core/supported_ranges.py` imports `SimulationStep` from
`core/simulation_step.py`, so the step's check cannot import those two from
there without a cycle; where they come to live is the work's choice.

**Why it matters.** Nothing in the interface hands either check anything but
the type it asks for, and a swapped argument is refused today all the same, so
no value is computed from one. What goes wrong is the advice handed to the
caller these refusals are written for - a notebook, a test, a value typed
`Any` - since, followed, it builds a step from an instant or a flow from a
step count, which passes every check and stores the wrong quantity under the
right type, the prescription `_require_built`'s own docstring says a refusal
must not make. A bare `int` too long to print makes the refusal itself raise
`ValueError`, escaping a caller that catches the `TypeError` both checks
document, the escape `PL-5F76` closed for the count.

**Done when.** `require_simulation_step`, and `_require_built` behind the
three flows' `require_*`, name a value built as another of the checked
quantities - for the step a `CaseInstant`, a `StepCount` or a flow, and for a
flow a `SimulationStep`, a `StepCount` or a `CaseInstant` as well as the other
flows it names today - as the type it was built as, and prescribe no rebuild
from its value, as `require_case_instant` and `require_step_count` do. Each
names a bare `int` too long to print as more than CPython's printable digits,
raising the `TypeError` its Raises section names rather than `ValueError`. A
bare `float` is still told to build the type, as today. Tests named
`test_another_quantity_handed_in_as_the_step_is_refused_as_a_swapped_argument`
in `tests/unit/test_simulation_step.py` and
`test_a_step_a_count_or_an_instant_handed_in_as_a_flow_is_refused_as_a_swapped_argument`
in `tests/unit/test_supported_ranges.py` pin the swapped arguments, and
`test_a_count_too_long_to_print_is_named_when_it_was_not_built_as_one` is
extended to the step's check and the three flows'.
