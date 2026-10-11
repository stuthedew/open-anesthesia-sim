"""What a checked type is built from, pinned once where the rule is written.

`core/checked_number.py` decides for every checked type - `Fraction`,
`Percent`, `SimulationStep`, the three flows, `CaseInstant` and `StepCount` -
what may be built into one, that none is built from another, and how a zero is
held; each type's own tests hold it to the rule, and these hold the rule
itself, so that a change here fails before any type does (`PL-LLMN`,
`PL-979Z`).
"""

import importlib
import itertools
import pkgutil
import sys
from decimal import Decimal
from fractions import Fraction as RationalFraction
from math import inf, nan
from typing import Any

import numpy
import pytest

import anesthesia_sim.core
from anesthesia_sim.core.checked_number import (
    CheckedQuantity,
    negative_zero_as_zero,
    require_a_number,
    require_not_another_quantity,
    shown,
)
from anesthesia_sim.core.concentration import Fraction, Percent
from anesthesia_sim.core.exceptions import AnesthesiaSimulationError
from anesthesia_sim.core.simulation_step import SimulationStep
from anesthesia_sim.core.supported_ranges import (
    AlveolarVentilation,
    CardiacOutput,
    CaseInstant,
    FreshGasFlow,
    StepCount,
)


class _AFloat(float):
    """A `float` subclass with no check of its own, standing in for the checked types.

    The checked types are `float` subclasses too, and each one's own tests hold
    that it passes; building one here would make a slip in this module report
    as that type's refusal at collection, with no test of the rule run.
    """


INSIDE_EVERY_RANGE: dict[type[Any], float] = {
    FreshGasFlow: 0.05,
    AlveolarVentilation: 0.05,
    CardiacOutput: 0.05,
    SimulationStep: 0.05,
    CaseInstant: 0.05,
    Fraction: 0.05,
    Percent: 0.05,
    StepCount: 1,
}
"""A number to build each checked type from that every other type's range admits, bar one.

0.05 is a supported step, a flow of 0.05 L/min, an instant of 0.05 s, a
fraction of 0.05 and a dial at 0.05%, and a count of one step is an instant of
1 s, a flow of 1 L/min, a fraction of 1.0 and a dial at 1%. So whatever
refuses one of these built as another type refuses the type, not the number -
except the step built from the count, since no whole number of seconds is a
supported step: there the range would refuse 1 s too, as a
`SimulationConfigurationError`, and the `TypeError` the pair test asserts is
what proves the type was read first. The values are built inside each test
rather than here, as `_AFloat` says.
"""

NAMED_AS: dict[type[Any], str] = {
    FreshGasFlow: "fresh_gas_flow_l_min",
    AlveolarVentilation: "alveolar_ventilation_l_min",
    CardiacOutput: "cardiac_output_l_min",
    SimulationStep: "simulation_step_s",
    CaseInstant: "instant_s",
    Fraction: "fraction",
    Percent: "percent",
    StepCount: "step_count",
}
"""What each constructor calls its value in a refusal: its parameter, the run's
`simulation_step_s` for the step, whose parameter is `seconds`, or a
concentration's default `name`."""

ORDERED_PAIRS = [
    (built_as, building)
    for built_as, building in itertools.product(INSIDE_EVERY_RANGE, repeat=2)
    if built_as is not building
]


def _every_subclass(base: type) -> list[type]:
    found: list[type] = []

    for subclass in base.__subclasses__():
        found.append(subclass)
        found.extend(_every_subclass(subclass))

    return found


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
    already built as a checked type, which each type's own tests hold - whether
    it is the type in hand is `require_not_another_quantity`'s question, asked
    before this one; so does an `int` of any length - a count or a flow too
    long to print is refused by its own range, in its own words.
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


def test_a_value_built_as_another_quantity_is_refused_by_name_and_anything_else_passes() -> None:
    """The rule itself: the type in hand and an unbuilt value pass, another quantity does not.

    It decides the type and nothing about the number, so a bare `float`, an
    `int`, a `bool`, a string and a `float` subclass nobody checked all pass
    to whatever reads the number next. What it refuses it names in full - the
    parameter, the value, the type it was built as and the type in hand - and
    it prescribes no rebuild, since the rebuild is the error. A count is any
    whole nonnegative number however long, so the value it prints goes through
    `shown`, where `repr` of a count past the digits CPython prints raised
    `ValueError` while the refusal was being written (`PL-5F76`).
    """

    for value in (CaseInstant(600.0), 600.0, 600, True, "600", None, _AFloat(600.0)):
        require_not_another_quantity("opening_s", value, CaseInstant)

    with pytest.raises(TypeError) as raised:
        require_not_another_quantity("opening_s", StepCount(600), CaseInstant)

    assert not isinstance(raised.value, AnesthesiaSimulationError)
    assert str(raised.value) == (
        "opening_s of 600 was built as StepCount, which is not CaseInstant: it is another "
        "quantity, so build CaseInstant from the value that opening_s should hold, not from "
        "this one (core/checked_number.py)"
    )

    with pytest.raises(TypeError) as too_long:
        CaseInstant(StepCount(10**5000))

    assert str(too_long.value).startswith(
        f"instant_s of <more than {sys.get_int_max_str_digits():,} digits> was built as StepCount"
    )


@pytest.mark.parametrize(
    ("built_as", "building"),
    ORDERED_PAIRS,
    ids=[f"{building.__name__}-from-{built_as.__name__}" for built_as, building in ORDERED_PAIRS],
)
def test_no_checked_type_is_built_from_another_checked_quantity(
    built_as: type[Any], building: type[Any]
) -> None:
    """Every ordered pair of checked types refuses, before any comparison reads the number.

    `mypy --strict` passes each of these calls but the seven that build
    `StepCount` from a float type, a checked `float` being a `float` and an
    `int` admitted where a `float` is annotated, so the constructor is the one
    check a slip of this shape meets, and until `PL-979Z` it checked the
    number against its own range and held a count of 600 steps as an instant
    of 600 s. The number is inside the range of the type being built
    (`INSIDE_EVERY_RANGE`, which names the one pair where it is not), so what
    refuses it is the type, and the refusal names the parameter, the value,
    the type it was built as and the type asked for, and prescribes no
    rebuild. `Fraction` and `Percent` keep their own refusal of each other,
    which says to convert, since that pair is a missed conversion rather than
    a swapped argument. A `TypeError` outside the simulator's hierarchy, since
    the caller's code is what is wrong; a `SimulationConfigurationError` here
    would mean the range read the number first.
    """

    value = built_as(INSIDE_EVERY_RANGE[built_as])

    with pytest.raises(TypeError) as raised:
        building(value)

    assert not isinstance(raised.value, AnesthesiaSimulationError)

    if {built_as, building} == {Fraction, Percent}:
        assert str(raised.value).startswith(
            f"{NAMED_AS[building]} of {value!r} is a {built_as.__name__}, not a "
            f"{building.__name__}: convert it with"
        )
    else:
        assert str(raised.value) == (
            f"{NAMED_AS[building]} of {value!r} was built as {built_as.__name__}, which is not "
            f"{building.__name__}: it is another quantity, so build {building.__name__} from "
            f"the value that {NAMED_AS[building]} should hold, not from this one "
            "(core/checked_number.py)"
        )


@pytest.mark.parametrize("checked", list(INSIDE_EVERY_RANGE), ids=lambda checked: checked.__name__)
def test_a_checked_type_is_rebuilt_from_its_own_kind(checked: type[Any]) -> None:
    """The type in hand passes, so an instant is rebuilt from an instant as before.

    It holds the same number it was built from.
    """

    built = checked(INSIDE_EVERY_RANGE[checked])
    rebuilt = checked(built)

    assert type(rebuilt) is checked
    assert rebuilt == built


@pytest.mark.parametrize("checked", list(INSIDE_EVERY_RANGE), ids=lambda checked: checked.__name__)
def test_the_number_comes_before_the_base_in_every_checked_type(checked: type[Any]) -> None:
    """`float` or `int` first and `CheckedQuantity` after, as `CheckedQuantity` says.

    `mypy` takes the nearest common base of two checked types as the type of
    a container holding both; with the base first that is `CheckedQuantity`
    rather than `float`, which refused a `float` variable in the interface
    (`app/dashboard_frame.py`). `mypy` catches it there today, and this holds
    the order where it is decided, so a refactor of that one variable cannot
    lose the guard.
    """

    mro = checked.__mro__
    number = int if issubclass(checked, int) else float

    assert mro.index(number) < mro.index(CheckedQuantity)


def test_every_checked_type_in_core_is_one_the_pairs_above_run() -> None:
    """A checked type added to `core/` joins the pairs above or fails here.

    The record of which types are checked is the class hierarchy, so this
    reads it, from every module under `core/`, rather than keeping a second
    list: a type that subclasses `CheckedQuantity` with no number here is one
    no pair above refuses, and the test that would have caught it never ran.
    Only the package's own classes count, so a subclass a test defines is not
    read as a checked type the simulator ships.
    """

    for module in pkgutil.walk_packages(
        anesthesia_sim.core.__path__, f"{anesthesia_sim.core.__name__}."
    ):
        importlib.import_module(module.name)

    shipped = {
        subclass
        for subclass in _every_subclass(CheckedQuantity)
        if subclass.__module__.startswith("anesthesia_sim.")
    }

    assert shipped == set(INSIDE_EVERY_RANGE)


def test_negative_zero_is_held_as_zero_and_every_other_number_as_itself() -> None:
    """Only the sign of a zero changes, since only a zero can carry a sign a comparison misses."""

    assert negative_zero_as_zero(-0.0).hex() == (0.0).hex()
    assert negative_zero_as_zero(0.0).hex() == (0.0).hex()
    assert negative_zero_as_zero(0).hex() == (0.0).hex()

    for number in (5e-324, -5e-324, 0.1, 10.0, 1, nan, inf, -inf):
        assert negative_zero_as_zero(number) is number
