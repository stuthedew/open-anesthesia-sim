---
id: PL-LLMN
title: _require_supported admits -0.0 (shown as -0.0 L/min), True (as 1.0 L/min) and Decimal, and refuses a str with math.isfinite's own TypeError rather than the simulator's wording; none is reachable from the sliders (found reviewing #1350)
priority: P1
effort: S
status: done
classes: safety, defect
feature: parse-dont-validate
touches: src/anesthesia_sim/core/checked_number.py, src/anesthesia_sim/core/supported_ranges.py, src/anesthesia_sim/core/concentration.py, src/anesthesia_sim/app/formatting.py, tests/unit/test_checked_number.py, tests/unit/test_supported_ranges.py, tests/unit/test_concentration.py, tests/unit/test_simulation.py, docs/MODEL.md, docs/ARCHITECTURE.md, docs/items/PL-848D-require-simulation-step-advises-rebuilding-what.md
added: 2026-10-04
closed: 2026-10-05
pr: 1370
payoff: a flow is never shown with a minus sign, a programming slip never becomes a plausible 1.0 L/min, and every refused flow names its setting and range
verify: grep -q 'def test_the_type_refuses_what_is_not_a_number_and_holds_negative_zero_as_zero' tests/unit/test_supported_ranges.py
---

**Problem.** _require_supported admits -0.0 (shown as -0.0 L/min), True (as 1.0 L/min) and Decimal, and refuses a str with math.isfinite's own TypeError rather than the simulator's wording; none is reachable from the sliders (found reviewing #1350)

**Reproduced 2026-10-04** on `main` at `8f24fe78`:
`uv run python -c "from decimal import Decimal; from anesthesia_sim.app.controller import SimulationController; from anesthesia_sim.app.dashboard_frame import setting_readouts; from anesthesia_sim.core.supported_ranges import AlveolarVentilation, CardiacOutput, FreshGasFlow; c = SimulationController(fresh_gas_flow_l_min=FreshGasFlow(True), alveolar_ventilation_l_min=AlveolarVentilation(Decimal('2.5')), cardiac_output_l_min=CardiacOutput(-0.0)); print([r.value_text for r in setting_readouts(c.snapshot())]); FreshGasFlow('2.5')"`
printed `['1.0 L/min', '2.00%', '2.5 L/min', '-0.0 L/min']`, then raised
`TypeError: must be real number, not str` from `math.isfinite`. The
controller's public constructor took all three, the setting readouts printed
a fresh gas flow of `True` as 1.0 L/min and a cardiac output of minus zero as
`-0.0 L/min`, and the string was refused in Python's words, naming neither the
setting nor the interval. Two more of the kind, found while reproducing:
`FreshGasFlow(Decimal('sNaN'))` escapes as a `ValueError` ("cannot convert
signaling NaN to float"), and `FreshGasFlow(numpy.True_)` holds 1.0 though
`numpy.True_` is not a `bool`, so a check for `bool` alone would miss it.
`#1354` leaves `_require_supported` as it is, so the fault survives it, and
adds a fourth type with it: run from the branch's `supported_ranges.py`, its
`CaseInstant`, built through `require_supported_case_instant`, which has the
same shape, admits `-0.0`, `True` and `Decimal('2.5')` and refuses `'2.5'`
with the same `TypeError`, while its `StepCount` refuses `True` with
`SimulationConfigurationError`.

**Why it matters.** None of the four is reachable from the interface: a
slider's value is its integer position over a power of ten, never minus zero,
a `bool`, a `Decimal` or a string, and the data-file loader refuses minus
zero, a `bool` and anything but an `int` or a `float` before a flow is built.
What reaches them is a caller building the type itself, such as a notebook, a
test or a value typed `Any`, which is the caller the types exist for. For that
caller a `bool` becomes a plausible 1.0 L/min without complaint, the silent
coercion of invalid data that `CLAUDE.md`'s safety-critical standard forbids;
minus zero is the supported zero printed with a sign no flow can have; and a
string or a signaling NaN is refused in Python's words, naming neither the
setting nor the interval that `_require_supported`'s docstring says every
refusal names.

**Done when.** `FreshGasFlow`, `AlveolarVentilation` and `CardiacOutput` built
from `-0.0` hold `0.0`, so `format_flow` prints `0.0 L/min`; refusing it
instead would refuse the supported zero that arithmetic can reach as minus
zero. Built from a `bool`, `numpy.True_`, a `Decimal` (`Decimal('sNaN')`
included) or a `str`, each raises a `TypeError` in the simulator's own words,
naming the setting, the value and its type, before any comparison runs, as
`_require_built` words a value of the wrong type: it is a programming error in
the caller rather than a refused setting. An `int` and a `float` are admitted
as today. A test in `tests/unit/test_supported_ranges.py` named
`test_the_type_refuses_what_is_not_a_number_and_holds_negative_zero_as_zero`
pins it for all three. `#1354` landed first, so the same refusal for `CaseInstant` is `PL-7N8P`'s,
best worked in this branch, and `StepCount`'s refusal of a `bool` is brought to
the same exception here.

**Wider since `PL-4R3W` (2026-10-05).** `Fraction` and `Percent` in
`core/concentration.py` became checked types of the same shape, and share each
hole, kept consistent on purpose so that one rule settles all of them:
`Fraction(-0.0)` holds minus zero and `format_percent` prints it as `-0.00%`,
`Fraction(True)` holds `1.0`, `Percent(Decimal('2.5'))` is admitted, a `str` is
refused with `math.isfinite`'s own `TypeError` and `Decimal('sNaN')` escapes as
a `ValueError` - each reproduced on that branch. None is reachable from the
interface, for the reason given above. The concentrations' half belongs in
this item's fix, `core/concentration.py` and `tests/unit/test_concentration.py`
beside the flows' files.
