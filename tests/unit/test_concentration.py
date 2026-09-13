"""The one crossing between the two forms a concentration is written in.

`core/concentration.py` states the rule; this is what holds it. Two of the
tests below assert a *type* error rather than a runtime one, which needs a
word about the mechanism: `tests/` is outside `[tool.mypy] files`, so a
`# type: ignore` here is not checked by the gate — it is checked by
`tools/ignore_check.py`, which runs mypy over this tree with
`warn_unused_ignores` on and reports a directive that has stopped being
necessary. So a directive below going inert is a failing `make check`, and
that is the assertion. It costs nothing: that mypy run already happens
(`PL-WVSK`).
"""

import pytest

from anesthesia_sim.core.circuit import BreathingCircuit
from anesthesia_sim.core.concentration import (
    PERCENT_PER_UNIT_FRACTION,
    Fraction,
    Percent,
    fraction_from_percent,
    percent_from_fraction,
)
from anesthesia_sim.core.exceptions import SimulationConfigurationError

# Sevoflurane's vaporizer maximum, as a fraction. The band `PL-WVSK` measured
# is bounded above by exactly this: a percent mistaken for a fraction above it
# is refused by `BreathingCircuit._require_deliverable`, and below it is not.
SEVOFLURANE_MAXIMUM_FRACTION = Fraction(0.08)


@pytest.mark.parametrize(
    ("percent", "fraction"), [(0.0, 0.0), (2.0, 0.02), (8.0, 0.08), (18.0, 0.18), (100.0, 1.0)]
)
def test_the_two_forms_convert_both_ways(percent: float, fraction: float) -> None:
    """The dial readings the three shipped agents actually use, and both ends."""

    assert fraction_from_percent(Percent(percent)) == pytest.approx(fraction)
    assert percent_from_fraction(Fraction(fraction)) == pytest.approx(percent)


def test_the_factor_is_a_hundred_and_is_written_once() -> None:
    assert PERCENT_PER_UNIT_FRACTION == 100.0
    assert fraction_from_percent(Percent(PERCENT_PER_UNIT_FRACTION)) == 1.0


def test_a_percent_reaching_a_fraction_parameter_is_refused_by_mypy_alone() -> None:
    """The guarantee and its limit, in one test.

    `0.08` is a dial reading of 0.08% on a sevoflurane vaporizer. Passed as a
    fraction it is 8% — a hundredfold error, and the *full* dial rather than a
    rounding error. Every runtime guard accepts it: it is a finite number in
    [0, 1] and it does not exceed the vaporizer maximum, which is what makes
    this the band `PL-WVSK` was filed about rather than a case already caught.

    So the directive below is the whole of the safeguard, and the assertions
    are what a reader needs in order to believe that: the call goes through,
    and what it stored is 8%.
    """

    circuit = BreathingCircuit(max_delivered_partial_pressure_fraction=SEVOFLURANE_MAXIMUM_FRACTION)

    circuit.set_delivered_partial_pressure_fraction(Percent(0.08))  # type: ignore[arg-type]

    assert circuit.delivered_partial_pressure_fraction == 0.08
    assert percent_from_fraction(circuit.delivered_partial_pressure_fraction) == pytest.approx(8.0)


def test_a_bare_float_reaching_a_fraction_parameter_is_refused_too() -> None:
    """The other half, and the one that catches a *new* unconverted path.

    A percent mistaken for a fraction has to come from somewhere, and it
    usually arrives as an unannotated intermediate rather than as a value
    something already called a percent.
    """

    circuit = BreathingCircuit(max_delivered_partial_pressure_fraction=SEVOFLURANE_MAXIMUM_FRACTION)

    circuit.set_delivered_partial_pressure_fraction(0.02)  # type: ignore[arg-type]

    assert circuit.delivered_partial_pressure_fraction == 0.02


def test_the_runtime_guards_are_unchanged_by_any_of_this() -> None:
    """A `NewType` is erased at runtime, so the refusals still come from code.

    Stated as a test because the module docstring says it: reading
    `Fraction` as something that validates is the way this change could be
    mistaken for more than it is.
    """

    circuit = BreathingCircuit(max_delivered_partial_pressure_fraction=SEVOFLURANE_MAXIMUM_FRACTION)

    with pytest.raises(SimulationConfigurationError, match="must be between 0 and 1"):
        circuit.set_delivered_partial_pressure_fraction(Fraction(1.5))

    with pytest.raises(SimulationConfigurationError, match="exceeds the vaporizer maximum"):
        circuit.set_delivered_partial_pressure_fraction(Fraction(0.5))

    assert circuit.delivered_partial_pressure_fraction == 0.0
