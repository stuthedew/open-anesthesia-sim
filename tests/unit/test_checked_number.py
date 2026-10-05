"""What every checked type is built from, pinned once where the rule is written.

`core/checked_number.py` decides for `Fraction`, `Percent` and the three flows
what may be built into one and how a zero is held; each type's own tests hold
it to the rule, and these hold the rule itself, so that a change here fails
before any type does (`PL-LLMN`).
"""

from decimal import Decimal
from fractions import Fraction as RationalFraction
from math import inf, nan

import numpy
import pytest

from anesthesia_sim.core.checked_number import negative_zero_as_zero, require_a_number
from anesthesia_sim.core.exceptions import AnesthesiaSimulationError
from anesthesia_sim.core.supported_ranges import FreshGasFlow


@pytest.mark.parametrize(
    "value",
    [0, 1, -3, 10**5000, 0.0, -0.0, 2.5, nan, inf, numpy.float64(2.5), FreshGasFlow(4.0)],
    ids=[
        "0",
        "1",
        "-3",
        "10**5000",
        "0.0",
        "-0.0",
        "2.5",
        "nan",
        "inf",
        "numpy.float64",
        "FreshGasFlow",
    ],
)
def test_an_int_or_a_float_is_a_number_whatever_it_holds(value: object) -> None:
    """The type is all this decides: the range, and finiteness, are each type's own.

    A `float` subclass is a `float`, so a NumPy double and a value already built
    as a checked type pass, and so does an `int` of any length - a count or a
    flow too long to print is refused by its own range, in its own words.
    """

    require_a_number("value", value)


@pytest.mark.parametrize(
    "value",
    [
        True,
        False,
        numpy.True_,
        numpy.int64(1),
        numpy.float32(1.0),
        Decimal("1"),
        Decimal("sNaN"),
        RationalFraction(1, 2),
        "1.0",
        None,
    ],
    ids=lambda value: f"{type(value).__module__}.{type(value).__name__}",
)
def test_what_is_not_an_int_or_a_float_is_refused_naming_the_value_and_its_type(
    value: object,
) -> None:
    """A `TypeError` outside the simulator's hierarchy, since the caller's code is what is wrong.

    A `bool` is an `int` to Python and is refused all the same, and so is the
    NumPy `bool`, which is not a `bool`: the check admits two types rather
    than refusing one. A NumPy scalar narrower than a double, a `Decimal` and a
    stdlib `Fraction` are refused rather than converted, so a value rounded or
    held in another arithmetic never reads as the number it was.
    """

    with pytest.raises(TypeError) as raised:
        require_a_number("cardiac_output_l_min", value)

    assert not isinstance(raised.value, AnesthesiaSimulationError)
    assert str(raised.value) == (
        f"cardiac_output_l_min of {value!r} is a {type(value).__name__}, not an int or a float: "
        "build it from a number, which is then checked against its range"
    )


def test_negative_zero_is_held_as_zero_and_every_other_number_as_itself() -> None:
    """Only the sign of a zero changes, since only a zero can carry a sign a comparison misses."""

    assert negative_zero_as_zero(-0.0).hex() == (0.0).hex()
    assert negative_zero_as_zero(0.0).hex() == (0.0).hex()
    assert negative_zero_as_zero(0) == 0.0

    for number in (5e-324, -5e-324, 0.1, 10.0, 1, nan, inf, -inf):
        assert negative_zero_as_zero(number) is number
