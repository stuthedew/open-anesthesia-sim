---
id: PL-3800
title: require_positive_finite and require_nonnegative_finite admit True (BreathingCircuit(circuit_volume_l=True) holds True, a 1 L circuit) and a Decimal (AlveolarCompartment(gas_volume_l=Decimal('2.5')) holds the Decimal), and refuse a str with math.isfinite's own TypeError, so every field they guard and SimulationStep, whose guard is built on the first, have the holes PL-LLMN closes for the flows and the concentrations; none is reachable from the interface; bring both guards to require_a_number in core/checked_number.py (found working PL-LLMN)
priority: P1
effort: S
status: done
classes: safety, defect
feature: parse-dont-validate
milestone: v0.5.23
touches: src/anesthesia_sim/core/validation.py, src/anesthesia_sim/core/simulation_step.py, src/anesthesia_sim/core/checked_number.py, tests/unit/test_validation.py, tests/unit/test_simulation_step.py, docs/MODEL.md, docs/ARCHITECTURE.md
added: 2026-10-05
closed: 2026-10-11
pr: 1397
payoff: a programming slip can no longer build a circuit, a lung, a tissue or a run's step from True as a plausible 1, and every refused volume, coefficient or step is named in the simulator's own exception
verify: grep -q 'def test_each_guard_refuses_what_is_not_a_number_and_an_overflowing_int_in_its_own_words' tests/unit/test_validation.py && grep -q 'def test_a_step_refuses_a_bool_a_decimal_and_an_overflowing_int_in_its_own_words' tests/unit/test_simulation_step.py
---

**Problem.** require_positive_finite and require_nonnegative_finite admit True (BreathingCircuit(circuit_volume_l=True) holds True, a 1 L circuit) and a Decimal (AlveolarCompartment(gas_volume_l=Decimal('2.5')) holds the Decimal), and refuse a str with math.isfinite's own TypeError, so every field they guard and SimulationStep, whose guard is built on the first, have the holes PL-LLMN closes for the flows and the concentrations; none is reachable from the interface; bring both guards to require_a_number in core/checked_number.py (found working PL-LLMN)

**Reproduced 2026-10-05, at triage.** On Python 3.14.7, against `main` at
`b67dace8`,
`uv run python -c "from decimal import Decimal; from anesthesia_sim.core.circuit import BreathingCircuit; from anesthesia_sim.core.alveolar import AlveolarCompartment; from anesthesia_sim.core.simulation_step import SimulationStep; print(repr(BreathingCircuit(circuit_volume_l=True).circuit_volume_l), repr(AlveolarCompartment(gas_volume_l=Decimal('2.5')).gas_volume_l), repr(SimulationStep(Decimal('0.05')))); SimulationStep(10**400)"`
printed `True Decimal('2.5') 0.05` and then raised `OverflowError: int too
large to convert to float` from `math.isfinite` in `require_positive_finite`.
So a circuit of `True` litres was built and held, a `Decimal` gas volume was
held as the `Decimal`, and a `Decimal` step was converted and held. Run the
same way, `BreathingCircuit(circuit_volume_l='6')` and `SimulationStep('0.05')`
raised `TypeError: must be real number, not str`, and
`BreathingCircuit(circuit_volume_l=10**400)` the same `OverflowError`.

**Wider: an `int` past the float range, folded from `PL-21V4`.** `PL-21V4`
recorded `FreshGasFlow(10**400)` and `SimulationStep(10**400)` raising
`OverflowError`. The flow half was closed by `PL-LLMN`, whose closed-interval
comparison refuses it with `SimulationConfigurationError` (re-run 2026-10-05);
the step half is `math.isfinite` in `require_positive_finite`, which this item
rewrites, so it was dropped into this one rather than worked as a second change
to the same two lines.

**Why it matters.** Nothing in the interface reaches either guard with
anything but a `float`: the volumes and coefficients come from the data files,
whose loader admits only an `int` or a `float`, and the step is the shipped
constant. What reaches them is a caller building a compartment, a settings
record or a step itself - a notebook, a test, a value typed `Any` - and for
that caller `True` becomes a plausible 1 L circuit, lung, venous pool or tissue
with no refusal, the silent coercion of invalid data `CLAUDE.md`'s
safety-critical standard forbids. A `Decimal` is held as given and enters the
arithmetic as one, and a `str` or an `int` past the float range escapes as
Python's own exception, naming neither the field nor its constraint, so a
caller catching the `SimulationConfigurationError` the guards raise does not
catch it. These are the last guards in `core/` with the holes `PL-LLMN` and
`PL-7N8P` closed for the flows, the concentrations and the case instant, and
`core/checked_number.py`'s module docstring already names them as this item's.

**Done when.** `require_positive_finite` and `require_nonnegative_finite` run
`require_a_number` first, so a `bool`, `numpy.True_`, a `Decimal`
(`Decimal('sNaN')` included), a `str` and a NumPy scalar that is neither an
`int` nor a `float` subclass are refused with its `TypeError`, naming the
field, the value and its type, before any comparison reads the value. An `int`
past the float range is refused with `SimulationConfigurationError` naming the
field and the value through `shown`, never as `OverflowError`, so
`SimulationStep(10**400)` is refused in the simulator's words like any other
step outside its range. An `int` or a `float` the guard admits today is
admitted as today. Both guards' docstrings gain a Raises section naming each
exception and when, which is `PL-HXKC`'s ask for these two, and
`core/checked_number.py`'s module docstring stops calling them outstanding.
Tests named
`test_each_guard_refuses_what_is_not_a_number_and_an_overflowing_int_in_its_own_words`
in `tests/unit/test_validation.py` and
`test_a_step_refuses_a_bool_a_decimal_and_an_overflowing_int_in_its_own_words`
in `tests/unit/test_simulation_step.py` pin it.

**Closed 2026-10-11, in `#1397`.** Both guards run `require_a_number` and then
a private `_require_within_the_float_range` in `core/validation.py`, which
compares an `int` against `sys.float_info.max` exactly, before the test each
has always made; `SimulationStep` inherits both through the first. Three calls
taken here rather than put to the owner, each with one clearly correct side:

- **The sentence a sign, a NaN or an infinity is refused in is unchanged**
  (`volume_l must be positive and finite`). Ten tests outside this item's
  `touches` pin it anchored at both ends (`tests/unit/test_governing_equations.py`,
  `tests/unit/test_circuit.py`), and naming the value in it is `PL-T137`'s
  own Done when. Only the new refusal, of an `int` past the float range, names
  the value, in the shape `PL-T137` asks for: `volume_l of 10...0 is outside
  the range a float holds, -1.7976931348623157e+308 to 1.7976931348623157e+308`,
  an `int` too long to print named by how long it is through `shown`.
- **The bound is the closed interval, not `float`'s rounding.** `float()`
  rounds the few `int`s between `sys.float_info.max` and 2**1024 - 2**970 down
  to the largest float, so `math.isfinite` admitted them; the interval refuses
  them with the rest. That is the one `int` the Done when's "admitted as
  today" no longer admits, at a magnitude of 1.8e308 no volume, coefficient,
  amount or step takes, and it buys a rule that converts nothing and has no
  rounding in it, as `_require_supported` in `core/supported_ranges.py` already
  compares.
- **The helper stays private to `core/validation.py`.** Every other guard in
  `core/` has a supported range to refuse such an `int` against; only these two
  have the sign alone, so nothing else would call it.

Reproduced on `main` at `7f970bbe` before the fix with the brief's command:
`True`, `Decimal('2.5')` and `0.05` held, `SimulationStep(True)` refused as a
1 s step, the string refused in `isfinite`'s words, and `10**400`
`OverflowError` from both a circuit and a step. The two tests the `verify:`
names fail on that tree (3 failures across both) and pass here. Nothing on
screen changes.
