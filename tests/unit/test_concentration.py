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

# Sevoflurane's vaporizer maximum, in the percent its dial reads. Since
# `PL-NJPB` the dial is set in percent, so a missing conversion now runs the
# other way: a fraction mistaken for a percent is a hundred times too small and
# lands between 0% and 1%, under this maximum and under every shipped agent's,
# so `BreathingCircuit._require_deliverable` refuses none of them.
SEVOFLURANE_MAXIMUM_PERCENT = Percent(8.0)


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


def test_a_fraction_reaching_a_percent_parameter_is_refused_by_mypy_alone() -> None:
    """The guarantee and its limit, in one test.

    `0.08` is sevoflurane's full dial, 8%, written as a fraction. Passed as a
    percent it is 0.08% — a hundredfold error, and the vaporizer all but off
    rather than at its maximum. Every runtime guard accepts it: it is a finite
    number in [0, 100] and it does not exceed the vaporizer maximum. Since the
    dial is set in percent (`PL-NJPB`) the same is true of every fraction from
    0 through 1, so this is the band `PL-WVSK` was filed about, turned the
    other way, rather than a case already caught.

    So the directive below is the whole of the safeguard, and the assertions
    are what a reader needs in order to believe that: the call goes through,
    and what it stored is 0.08%.
    """

    circuit = BreathingCircuit(max_delivered_concentration_percent=SEVOFLURANE_MAXIMUM_PERCENT)

    circuit.set_delivered_concentration_percent(Fraction(0.08))  # type: ignore[arg-type]

    assert circuit.delivered_concentration_percent == 0.08
    assert circuit.delivered_partial_pressure_fraction == pytest.approx(0.0008)


def test_a_bare_float_reaching_a_percent_parameter_is_refused_too() -> None:
    """The other half, and the one that catches a *new* unconverted path.

    A fraction mistaken for a percent has to come from somewhere, and it
    usually arrives as an unannotated intermediate rather than as a value
    something already called a fraction. `0.02` is a 2% setting as a
    fraction, and what the circuit stores is 0.02%.
    """

    circuit = BreathingCircuit(max_delivered_concentration_percent=SEVOFLURANE_MAXIMUM_PERCENT)

    circuit.set_delivered_concentration_percent(0.02)  # type: ignore[arg-type]

    assert circuit.delivered_concentration_percent == 0.02


def test_the_runtime_guards_are_unchanged_by_any_of_this() -> None:
    """A `NewType` is erased at runtime, so the refusals still come from code.

    Stated as a test because the module docstring says it: reading
    `Percent` as something that validates is the way this change could be
    mistaken for more than it is.
    """

    circuit = BreathingCircuit(max_delivered_concentration_percent=SEVOFLURANE_MAXIMUM_PERCENT)

    with pytest.raises(SimulationConfigurationError, match="must be between 0 and 100"):
        circuit.set_delivered_concentration_percent(Percent(150.0))

    with pytest.raises(SimulationConfigurationError, match="exceeds the vaporizer maximum"):
        circuit.set_delivered_concentration_percent(Percent(50.0))

    assert circuit.delivered_concentration_percent == 0.0
