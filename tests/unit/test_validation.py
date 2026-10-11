"""The shared numeric guards raise inside the project's hierarchy.

Covered separately from the compartments that call them because the
guard functions are the single place the type is decided: a guard that
reverted to a bare `ValueError` would leave `app/` unable to recognise a
core failure, without any individual compartment test noticing. What each
guard is willing to read at all - a number, inside the range a `float` holds -
is pinned here for the same reason, since `PL-3800`.
"""

import sys
from decimal import Decimal
from math import inf, nan

import numpy
import pytest

from anesthesia_sim.core.concentration import Percent
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.validation import (
    require_nonnegative_finite,
    require_positive_finite,
    require_within_vaporizer_maximum,
)


@pytest.mark.parametrize("value", [0.0, -1.0, inf, -inf, nan])
def test_require_positive_finite_rejects_within_the_hierarchy(value: float) -> None:
    with pytest.raises(SimulationConfigurationError, match="volume_l must be positive and finite"):
        require_positive_finite("volume_l", value)


@pytest.mark.parametrize("value", [-0.1, inf, -inf, nan])
def test_require_nonnegative_finite_rejects_within_the_hierarchy(value: float) -> None:
    with pytest.raises(
        SimulationConfigurationError, match="agent_amount_l must be nonnegative and finite"
    ):
        require_nonnegative_finite("agent_amount_l", value)


@pytest.mark.parametrize(
    ("guard", "value"), [(require_positive_finite, 0.5), (require_nonnegative_finite, 0.0)]
)
def test_guards_accept_their_boundary_values(guard, value: float) -> None:
    """A fraction's own edges are its constructor's since `PL-4R3W`, in `test_concentration.py`."""

    guard("value", value)


NOT_A_NUMBER = (
    True,
    numpy.True_,
    Decimal("2.5"),
    Decimal("sNaN"),
    "2.5",
    numpy.float32(2.5),
    numpy.int64(2),
)
"""What each guard read before `PL-3800`, and what came of it.

`True` and `numpy.True_` each passed as the 1 it is to a comparison, so
`BreathingCircuit(circuit_volume_l=True)` held a 1 L circuit; the `Decimal`
was held as given and entered the arithmetic as one; the signalling NaN
escaped as `math.isfinite`'s `ValueError` and the string as its `TypeError`,
naming neither the field nor its constraint. The first five are the flows'
list, `NOT_A_NUMBER` in `test_supported_ranges.py`. The two NumPy scalars are
neither an `int` nor a `float` subclass, which is all `require_a_number`
admits: a value rounded in a narrower format is converted by its caller, never
read as the number it was (`core/checked_number.py`).
"""


@pytest.mark.parametrize(
    ("guard", "name"),
    [(require_positive_finite, "volume_l"), (require_nonnegative_finite, "agent_amount_l")],
)
def test_each_guard_refuses_what_is_not_a_number_and_an_overflowing_int_in_its_own_words(
    guard, name: str
) -> None:
    """A guard reads an int or a float inside the range a float holds, and nothing else.

    Each of `NOT_A_NUMBER` is refused with a `TypeError` in the simulator's
    words naming the field, the value and its type, before any comparison
    reads it - the signalling NaN and the string would each raise in a
    comparison or in `isfinite`, in Python's words, so the message is what
    shows the refusal came first. An `int` past the float range, which
    `isfinite` raised `OverflowError` converting, is refused inside the
    simulator's own hierarchy, naming the field, the value and the bound; one
    too long to print is named by how long it is, as a refused count is
    (`PL-5F76`). The bound is closed: the largest float itself, as a `float`
    or as the `int` it converts to, is admitted, and so is every `int` and
    `float` the guard admitted before, a NumPy double among them.
    """

    for value in NOT_A_NUMBER:
        with pytest.raises(TypeError) as raised:
            guard(name, value)

        message = str(raised.value)

        assert message.startswith(f"{name} of {value!r} has type {type(value).__name__}")
        assert "not int or float" in message

    largest = sys.float_info.max
    bound = f"is outside the range a float holds, -{largest!r} to {largest!r}"

    for value in (2**1024, 10**400, -(10**400)):
        with pytest.raises(SimulationConfigurationError) as refused:
            guard(name, value)

        assert str(refused.value) == f"{name} of {value} {bound}"

    with pytest.raises(SimulationConfigurationError) as too_long:
        guard(name, 10**5000)

    assert (
        str(too_long.value)
        == f"{name} of <more than {sys.get_int_max_str_digits():,} digits> {bound}"
    )

    for admitted in (1, 1.0, numpy.float64(1.0), largest, int(largest)):
        guard(name, admitted)


def test_require_within_vaporizer_maximum_rejects_within_the_hierarchy() -> None:
    """The one relation among the guards refuses in the circuit's sentence (`PL-BBMG`)."""

    with pytest.raises(
        SimulationConfigurationError,
        match=r"delivered_concentration_percent exceeds the vaporizer maximum "
        r"\(20% requested, 8% maximum\)",
    ):
        require_within_vaporizer_maximum(
            "delivered_concentration_percent", Percent(20.0), Percent(8.0)
        )


@pytest.mark.parametrize("dialled", [0.0, 7.999, 8.0])
def test_require_within_vaporizer_maximum_accepts_up_to_the_maximum(dialled: float) -> None:
    require_within_vaporizer_maximum(
        "delivered_concentration_percent", Percent(dialled), Percent(8.0)
    )
