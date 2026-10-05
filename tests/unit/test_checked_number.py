"""What a checked type is built from, pinned once where the rule is written.

`core/checked_number.py` decides for `Fraction`, `Percent` and the three flows
what may be built into one and how a zero is held; each type's own tests hold
it to the rule, and these hold the rule itself, so that a change here fails
before any type does (`PL-LLMN`).
"""

import sys
from decimal import Decimal
from fractions import Fraction as RationalFraction
from math import inf, nan

import numpy
import pytest

from anesthesia_sim.core.checked_number import negative_zero_as_zero, require_a_number, shown
from anesthesia_sim.core.exceptions import AnesthesiaSimulationError


class _AFloat(float):
    """A `float` subclass with no check of its own, standing in for the checked types.

    The checked types are `float` subclasses too, and each one's own tests hold
    that it passes; building one here would make a slip in this module report
    as that type's refusal at collection, with no test of the rule run.
    """


def test_a_refused_value_is_shown_as_itself_and_a_count_too_long_to_print_by_its_length() -> None:
    """What a refusal prints for the value that failed it.

    A string keeps its quotes, so `'2.5'` cannot be read as the number 2.5;
    an `int` prints in digits up to the limit CPython prints at all, and past
    it as more than that many, with its sign, where `repr` raises `ValueError`
    and a refusal built on it escaped the simulator's own exceptions
    (`PL-5F76`, `PL-LLMN`).
    """

    assert shown(2.5) == "2.5"
    assert shown(-0.0) == "-0.0"
    assert shown(nan) == "nan"
    assert shown(7) == "7"
    assert shown(True) == "True"
    assert shown("2.5") == "'2.5'"
    assert shown(Decimal("2.5")) == "Decimal('2.5')"
    assert shown(numpy.float64(2.5)) == repr(numpy.float64(2.5))
    assert shown(10**400) == str(10**400)
    assert shown(10**5000) == f"<more than {sys.get_int_max_str_digits():,} digits>"
    assert shown(-(10**5000)) == f"-<more than {sys.get_int_max_str_digits():,} digits>"


@pytest.mark.parametrize(
    "value",
    [0, 1, -3, 10**5000, 0.0, -0.0, 2.5, nan, inf, numpy.float64(2.5), _AFloat(4.0)],
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
        "float-subclass",
    ],
)
def test_an_int_or_a_float_is_a_number_whatever_it_holds(value: object) -> None:
    """The type is all this decides: the range, and finiteness, are each type's own.

    A `float` subclass is a `float`, so a NumPy double passes, as does a value
    already built as a checked type, which each type's own tests hold; so does
    an `int` of any length - a count or a flow too long to print is refused by
    its own range, in its own words.
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
    ids=[
        "True",
        "False",
        "numpy.True_",
        "numpy.int64",
        "numpy.float32",
        "Decimal('1')",
        "Decimal('sNaN')",
        "fractions.Fraction",
        "str",
        "None",
    ],
)
def test_what_is_not_an_int_or_a_float_is_refused_naming_the_value_and_its_type(
    value: object,
) -> None:
    """A `TypeError` outside the simulator's hierarchy, since the caller's code is what is wrong.

    A `bool` is an `int` to Python and is refused all the same, and so is the
    NumPy `bool`, which is not a `bool`: the check admits two types rather
    than refusing one. A NumPy scalar narrower than a double, a `Decimal` and a
    stdlib `Fraction` are refused rather than converted, so a value rounded or
    held in another arithmetic never reads as the number it was. The message
    says `has type int64`, not `is a int64`, since the type's name is not a
    word and a NumPy integer's reader would call it an int.
    """

    with pytest.raises(TypeError) as raised:
        require_a_number("cardiac_output_l_min", value)

    assert not isinstance(raised.value, AnesthesiaSimulationError)
    assert str(raised.value) == (
        f"cardiac_output_l_min of {value!r} has type {type(value).__name__}, not int or float: "
        "build it from an int or a float, which is then checked against its range "
        "(core/checked_number.py)"
    )


def test_negative_zero_is_held_as_zero_and_every_other_number_as_itself() -> None:
    """Only the sign of a zero changes, since only a zero can carry a sign a comparison misses."""

    assert negative_zero_as_zero(-0.0).hex() == (0.0).hex()
    assert negative_zero_as_zero(0.0).hex() == (0.0).hex()
    assert negative_zero_as_zero(0).hex() == (0.0).hex()

    for number in (5e-324, -5e-324, 0.1, 10.0, 1, nan, inf, -inf):
        assert negative_zero_as_zero(number) is number
