"""The shared numeric guards raise inside the project's hierarchy.

These tests cover the guards separately from the compartments that call
them, because the guard functions are the one place where the exception
type is decided. If a guard went back to raising a bare `ValueError`, `app/`
could no longer recognise a core failure, and no single compartment test
would notice. For the same reason, these tests also check what each guard
accepts at all: a number inside the range that a `float` can represent. That
check dates from `PL-3800`.
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
    """Each guard accepts its own boundary value.

    Since `PL-4R3W`, a fraction's own edges are checked by its constructor, and
    `test_concentration.py` tests them.
    """

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
"""Values that each guard accepted before `PL-3800`, and what happened to each.

`True` and `numpy.True_` each passed, because a comparison treats each as
the number 1. So `BreathingCircuit(circuit_volume_l=True)` held a 1 L
circuit. The `Decimal` was stored as given and entered the arithmetic as a
decimal. The signalling NaN escaped as the `ValueError` from
`math.isfinite`, and the string escaped as its `TypeError`. Neither error
named the field or its constraint. The first five values are the list used
for the flows, `NOT_A_NUMBER` in `test_supported_ranges.py`. The two NumPy
scalars are neither an `int` subclass nor a `float` subclass, and
`require_a_number` accepts only those. A value rounded in a narrower format
must be converted by its caller, so that the rounded value is never taken for
the number it was before rounding (`core/checked_number.py`).
"""


@pytest.mark.parametrize(
    ("guard", "name"),
    [(require_positive_finite, "volume_l"), (require_nonnegative_finite, "agent_amount_l")],
)
def test_each_guard_refuses_what_is_not_a_number_and_an_overflowing_int_in_its_own_words(
    guard, name: str
) -> None:
    """A guard accepts only an int or a float inside the range that a float can represent.

    Each value in `NOT_A_NUMBER` is rejected with a `TypeError` that names
    the field, the value and its type in the simulator's words. The
    rejection comes before any comparison uses the value. The signalling NaN
    and the string would each raise in a comparison or in `isfinite`, in
    Python's words, so the message shows that the rejection came first.

    An `int` beyond the float range used to make `isfinite` raise
    `OverflowError` while converting it. Such an `int` is now rejected inside
    the simulator's own hierarchy, with a message that names the field, the
    value and the bound. An `int` too long to print is described by its
    length, as a rejected count is (`PL-5F76`). The bound is closed. The
    largest float itself is accepted, as a `float` or as the `int` it
    converts to. So is every `int` and `float` that the guard accepted
    before, a NumPy double among them.
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


@pytest.mark.parametrize(
    ("guard", "value", "reason"),
    [
        (require_positive_finite, -2.5, "-2.5 is not greater than zero"),
        (require_positive_finite, 0.0, "0.0 is not greater than zero"),
        (require_positive_finite, -0.0, "-0.0 is not greater than zero"),
        (require_positive_finite, nan, "nan is not finite"),
        (require_positive_finite, inf, "inf is not finite"),
        (require_nonnegative_finite, -2.5, "-2.5 is negative"),
        (require_nonnegative_finite, nan, "nan is not finite"),
        (require_nonnegative_finite, -inf, "-inf is not finite"),
    ],
)
def test_a_rejected_value_appears_in_the_message(guard, value: float, reason: str) -> None:
    """A rejection message names the rejected value and the reason (`PL-T137`).

    Before that change, `gas_volume_l` gave the same message for `-0.0`, `nan` and
    `-2.5`. A value that is not finite and a value below the range need
    different fixes.
    """

    with pytest.raises(SimulationConfigurationError) as refusal:
        guard("gas_volume_l", value)

    assert str(refusal.value).startswith("gas_volume_l must be")
    assert str(refusal.value).endswith(f", and {reason}")


def test_require_within_vaporizer_maximum_rejects_within_the_hierarchy() -> None:
    """The only guard that compares two values rejects in the circuit's wording (`PL-BBMG`)."""

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
