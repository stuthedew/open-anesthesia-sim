"""Test, in one place, the shared rule for what a checked type may be built from.

`core/checked_number.py` sets the rule for every checked type: `Fraction`,
`Percent`, `MacPercent`, `SimulationStep`, the three flows, `CaseInstant`,
`StepCount`, `CompartmentVolume` and `PartitionCoefficient`. The rule says what
may be built into one, that none is built from another, and how a zero is
stored. Each type's own tests check that the type
follows the rule. These tests check the rule itself, so that a change to it
fails here before any type's tests fail (`PL-LLMN`, `PL-979Z`).
"""

import importlib
import itertools
import pickle
import pkgutil
import re
import struct
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
from anesthesia_sim.core.concentration import Fraction, MacPercent, Percent
from anesthesia_sim.core.exceptions import AnesthesiaSimulationError
from anesthesia_sim.core.numerical_envelope import CompartmentVolume, PartitionCoefficient
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

    The checked types are `float` subclasses too, and each type's own tests
    check that it passes. Building one here would make a slip in this module
    show up as that type's refusal at collection, and no test of the rule
    would run.
    """


INSIDE_EVERY_RANGE: dict[type[Any], float] = {
    FreshGasFlow: 0.05,
    AlveolarVentilation: 0.05,
    CardiacOutput: 0.05,
    SimulationStep: 0.05,
    CaseInstant: 0.05,
    Fraction: 0.05,
    Percent: 0.05,
    MacPercent: 0.05,
    StepCount: 1,
    CompartmentVolume: 0.05,
    PartitionCoefficient: 0.05,
}
"""For each checked type, a number that every other type's range accepts, with one exception.

0.05 is a supported step, a flow of 0.05 L/min, an instant of 0.05 s, a
fraction of 0.05, a dial at 0.05%, a volume of 0.05 L and a partition
coefficient of 0.05. A count of one step is an instant of 1 s, a flow of
1 L/min, a fraction of 1.0, a dial at 1%, a volume of 1 L and a coefficient
of 1. So when one of
these values, built as one type, is refused by another type, the refusal
comes from the type and not from the number. The one exception is the step
built from the count, because no whole number of seconds is a supported
step. There the range would refuse 1 s too, as a
`SimulationConfigurationError`. The `TypeError` that the pair test asserts
is what proves that the type was checked first. The values are built inside
each test rather than here, for the reason that `_AFloat` gives.
"""

NAMED_AS: dict[type[Any], str] = {
    FreshGasFlow: "fresh_gas_flow_l_min",
    AlveolarVentilation: "alveolar_ventilation_l_min",
    CardiacOutput: "cardiac_output_l_min",
    SimulationStep: "simulation_step_s",
    CaseInstant: "instant_s",
    Fraction: "fraction",
    Percent: "percent",
    MacPercent: "mac_percent",
    StepCount: "step_count",
    CompartmentVolume: "volume_l",
    PartitionCoefficient: "partition_coefficient",
}
"""The name that each constructor gives its value in a refusal.

The name is the constructor's parameter, with two exceptions. The step uses
the run's `simulation_step_s`, although its parameter is `seconds`. A
concentration, a volume and a partition coefficient use their default `name`."""

ORDERED_PAIRS = [
    (built_as, building)
    for built_as, building in itertools.product(INSIDE_EVERY_RANGE, repeat=2)
    if built_as is not building and not issubclass(built_as, building)
]
"""Every ordered pair of two checked types, except a type built from its own subtype.

`MacPercent` is a `Percent` that is above zero. So a `Percent` is rebuilt from a
`MacPercent` as from its own kind, because a MAC is a percent of one
atmosphere. The reverse is refused, because a `Percent` was not checked as a
MAC (`PL-F9TC`)."""

CONCENTRATION_FORM: dict[type[Any], str] = {
    Fraction: "Fraction",
    Percent: "Percent",
    MacPercent: "Percent",
}
"""The concentration form that a refusal names when it says to convert rather than rebuild.

A `MacPercent` is in the percent form. So the refusal of a `Fraction` handed to
a `MacPercent` says to convert from a fraction to a percent, in the words that
`Percent` uses."""


def _every_subclass(base: type) -> list[type]:
    found: list[type] = []

    for subclass in base.__subclasses__():
        found.append(subclass)
        found.extend(_every_subclass(subclass))

    return found


def test_a_refused_value_is_shown_as_itself_and_a_count_too_long_to_print_by_its_length() -> None:
    """Check what a refusal prints for the value that failed the check.

    A string keeps its quotes, so `'2.5'` cannot be mistaken for the number
    2.5. An `int` prints in digits up to the limit at which CPython prints
    digits at all. Past that limit, it prints as more than that many digits,
    with its sign. There `repr` raises `ValueError`, and a refusal built on
    `repr` escaped the simulator's own exceptions (`PL-5F76`, `PL-LLMN`).
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
    """This check decides only the type, and each type checks its own range and finiteness.

    A `float` subclass is a `float`, so a NumPy double passes. So does a value
    already built as a checked type, as each type's own tests check. Whether
    that value is the type in hand is the question that
    `require_not_another_quantity` asks, before this one. An `int` of any
    length passes too. A count or a flow too long to print is refused by its
    own range, in its own words.
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
    """The error is a `TypeError` outside the simulator's hierarchy, as the caller's code is wrong.

    A `bool` is an `int` to Python, and it is refused all the same. So is the
    NumPy `bool`, which is not a `bool`. The check accepts two types rather
    than refusing one. A NumPy scalar narrower than a double, a `Decimal` and
    a stdlib `Fraction` are refused rather than converted. So a value that
    was rounded, or held in another arithmetic, is never treated as the
    number it was. The message says `has type int64`, not `is a int64`,
    because the type's name is not a word, and a reader would call a NumPy
    integer an int.
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

    The rule decides the type and nothing about the number. So a bare
    `float`, an `int`, a `bool`, a string and a `float` subclass that nobody
    checked all pass to whatever reads the number next. A refusal names
    everything in full: the parameter, the value, the type the value was
    built as, and the type in hand. It prescribes no rebuild, because the
    rebuild is the error. A count is any whole nonnegative number, however
    long, so the value that the refusal prints goes through `shown`. Calling
    `repr` on a count longer than the digits CPython prints raised
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
    """Every ordered pair of checked types is refused, before any comparison reads the number.

    `mypy --strict` accepts each of these calls except the seven that build
    `StepCount` from a float type. It accepts them because a checked `float`
    is a `float`, and an `int` is accepted where a `float` is annotated. So
    the constructor is the only check that a slip of this kind meets. Until
    `PL-979Z`, the constructor checked the number against its own range, and
    so it stored a count of 600 steps as an instant of 600 s. The number is
    inside the range of the type being built (`INSIDE_EVERY_RANGE` names the
    one pair where it is not). So what refuses it is the type. The refusal
    names the parameter, the value, the type the value was built as and the
    type asked for, and it prescribes no rebuild. `Fraction` and `Percent`
    keep their own refusal of each other, which says to convert, because that
    pair is a missed conversion rather than a swapped argument. The error is
    a `TypeError` outside the simulator's hierarchy, because the caller's
    code is what is wrong. A `SimulationConfigurationError` here would mean
    that the range checked the number first.
    """

    value = built_as(INSIDE_EVERY_RANGE[built_as])

    with pytest.raises(TypeError) as raised:
        building(value)

    assert not isinstance(raised.value, AnesthesiaSimulationError)

    if Fraction in {built_as, building} and {built_as, building} <= set(CONCENTRATION_FORM):
        assert str(raised.value).startswith(
            f"{NAMED_AS[building]} of {value!r} is a {CONCENTRATION_FORM[built_as]}, not a "
            f"{CONCENTRATION_FORM[building]}: convert it with"
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

    The rebuilt value holds the same number that it was built from.
    """

    built = checked(INSIDE_EVERY_RANGE[checked])
    rebuilt = checked(built)

    assert type(rebuilt) is checked
    assert rebuilt == built


@pytest.mark.parametrize("checked", list(INSIDE_EVERY_RANGE), ids=lambda checked: checked.__name__)
def test_the_number_comes_before_the_base_in_every_checked_type(checked: type[Any]) -> None:
    """`float` or `int` comes before `CheckedQuantity` in the bases, as `CheckedQuantity` says.

    `mypy` takes the nearest common base of two checked types as the type of
    a container holding both. With the base first, that type is
    `CheckedQuantity` rather than `float`, and `mypy` then refused a `float`
    variable in the interface (`app/dashboard_frame.py`). `mypy` catches that
    there today. This test enforces the order where it is decided, so that a
    refactor of that one variable cannot lose the guard.
    """

    mro = checked.__mro__
    number = int if issubclass(checked, int) else float

    assert mro.index(number) < mro.index(CheckedQuantity)


def test_every_checked_type_in_core_is_one_the_pairs_above_run() -> None:
    """A checked type added to `core/` joins the pairs above or fails here.

    The class hierarchy is the record of which types are checked. So this
    test reads the hierarchy, from every module under `core/`, rather than
    keeping a second list. A type that subclasses `CheckedQuantity` but has
    no number here is one that no pair above refuses, so the test that would
    have caught it never ran. Only the package's own classes count, so a
    subclass that a test defines is not treated as a checked type that the
    simulator ships.
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
    """Only the sign of a zero changes, as only a zero can carry a sign that a comparison misses."""

    assert negative_zero_as_zero(-0.0).hex() == (0.0).hex()
    assert negative_zero_as_zero(0.0).hex() == (0.0).hex()
    assert negative_zero_as_zero(0).hex() == (0.0).hex()

    for number in (5e-324, -5e-324, 0.1, 10.0, 1, nan, inf, -inf):
        assert negative_zero_as_zero(number) is number


OUTSIDE_ITS_RANGE: dict[type[Any], float] = {
    FreshGasFlow: 1000.0,
    AlveolarVentilation: 1000.0,
    CardiacOutput: 1000.0,
    SimulationStep: 5.0,
    CaseInstant: -1.0,
    Fraction: 1.5,
    Percent: 150.0,
    MacPercent: 150.0,
    StepCount: -5,
    CompartmentVolume: 1e-5,
    PartitionCoefficient: 1e5,
}
"""For each checked type, a number that its own range refuses, written into a pickle by hand."""


def _tampered(pickled: bytes, held: float, written: float, protocol: int) -> bytes:
    """Return `pickled` with the number it holds overwritten, as a hand edit would leave it.

    Protocol 0 writes a number as text, after `F` for a `float` and `I` for an
    `int`. Later protocols write a `float` as eight big-endian bytes after `G`,
    and a small nonnegative `int` as one byte after `K`. This function replaces
    that `K` and its byte with `J` and a signed four-byte `int`.
    """

    if protocol == 0:
        opcode = b"I" if isinstance(held, int) else b"F"
        old, new = opcode + repr(held).encode() + b"\n", opcode + repr(written).encode() + b"\n"
    elif isinstance(held, int):
        old, new = b"K" + bytes([held]), b"J" + struct.pack("<i", int(written))
    else:
        old, new = b"G" + struct.pack(">d", held), b"G" + struct.pack(">d", written)

    assert pickled.count(old) == 1

    return pickled.replace(old, new)


@pytest.mark.parametrize("protocol", range(pickle.HIGHEST_PROTOCOL + 1))
@pytest.mark.parametrize("checked", list(INSIDE_EVERY_RANGE), ids=lambda checked: checked.__name__)
def test_every_checked_type_unpickled_at_any_protocol_is_rebuilt_through_its_check(
    checked: type[Any], protocol: int
) -> None:
    """`PL-5D1Z`: a pickle at protocol 0 or 1 rebuilt a checked type, bypassing its own check.

    Those protocols rebuilt a `float` or `int` subclass through `float.__new__`
    or `int.__new__`. So a hand-edited file loaded a `Fraction` of 1.5 or a
    `StepCount` of -5, as the type whose job is to guarantee its range. The
    expected refusal is the one the constructor gives when it is called
    directly with the edited number. An unedited pickle loads as the type and
    value it saved.
    """

    held = INSIDE_EVERY_RANGE[checked]
    pickled = pickle.dumps(checked(held), protocol=protocol)
    loaded = pickle.loads(pickled)

    assert type(loaded) is checked
    assert loaded == held

    written = OUTSIDE_ITS_RANGE[checked]

    with pytest.raises(AnesthesiaSimulationError) as built_directly:
        checked(written)

    with pytest.raises(
        type(built_directly.value), match=f"^{re.escape(str(built_directly.value))}$"
    ):
        pickle.loads(_tampered(pickled, held, written, protocol))
