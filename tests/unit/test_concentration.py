"""The two checked forms a concentration is written in, and the one crossing
between them.

`core/concentration.py` states the rule; this is what holds it. `Fraction` and
`Percent` are checked against their ranges when they are built, so the edges
of each range are pinned here once, on the constructor, rather than at each
place a value is held (`PL-4R3W`).

Several tests below hand a value of the wrong type to a parameter `mypy` would
refuse it for, which needs a word about the mechanism: `tests/` is outside
`[tool.mypy] files`, so a `# type: ignore` here is not checked by the gate — it
is checked by `tools/ignore_check.py`, which runs mypy over this tree with
`warn_unused_ignores` on and reports a directive that has stopped being
necessary. So a directive below going inert is a failing `make check`, and
that is the assertion that `mypy` still refuses the call. What the call does at
run time is the test's own assertion: since `PL-4R3W` each of them is refused
there too (`PL-WVSK`).
"""

import copy
import pickle
import struct
import sys
from collections.abc import Callable
from dataclasses import replace
from decimal import Decimal
from math import inf, nan, nextafter
from typing import Any

import numpy
import pytest

from anesthesia_sim.app.formatting import format_percent
from anesthesia_sim.core.circuit import BreathingCircuit, BreathingCircuitState
from anesthesia_sim.core.concentration import (
    PERCENT_PER_UNIT_FRACTION,
    Fraction,
    Percent,
    fraction_from_percent,
    percent_from_fraction,
    require_fraction,
    require_percent,
)
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.parameters import load_sevoflurane_parameters
from anesthesia_sim.core.simulation_step import SimulationStep
from anesthesia_sim.core.supported_ranges import (
    AlveolarVentilation,
    CardiacOutput,
    CaseInstant,
    FreshGasFlow,
    StepCount,
)
from anesthesia_sim.core.uptake_system import AgentUptakeSystem

# Sevoflurane's vaporizer maximum, in the percent its dial reads. Since
# `PL-NJPB` the dial is set in percent, so a missing conversion runs the other
# way: a fraction mistaken for a percent is a hundred times too small and lands
# between 0% and 1%, under this maximum and under every shipped agent's, so
# `BreathingCircuit._require_deliverable` refuses none of them.
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


@pytest.mark.parametrize("value", [0.0, 5e-324, 0.02, nextafter(1.0, 0.0), 1.0])
def test_a_fraction_from_0_through_1_is_the_number_it_was_built_from(value: float) -> None:
    """Both ends are fractions, and so is the closest float to each, unrounded."""

    fraction = Fraction(value)

    assert isinstance(fraction, float)
    assert float(fraction).hex() == value.hex()


@pytest.mark.parametrize(
    "value", [nextafter(0.0, -1.0), -0.001, nextafter(1.0, inf), 1.001, inf, -inf, nan]
)
def test_a_fraction_outside_0_to_1_cannot_be_built(value: float) -> None:
    """The one place a fraction's range is checked, at each edge and past it.

    The two `nextafter` values are the first floats outside the range. Before
    `PL-4R3W` this was `require_fraction` in `core/validation.py`, called at each
    of the twelve places a value entered.
    """

    with pytest.raises(SimulationConfigurationError, match=r"is outside 0 to 1"):
        Fraction(value)


@pytest.mark.parametrize(
    ("concentration", "name"), [(Fraction, "fraction"), (Percent, "percent")], ids=repr
)
def test_a_concentration_refuses_what_is_not_a_number_and_holds_negative_zero_as_zero(
    concentration: type[float], name: str
) -> None:
    """Built from an int or a float and nothing else, with no sign at zero (`PL-LLMN`).

    The same holes the flows had, kept consistent with them on purpose so one
    rule settles all: `Fraction(True)` was a fraction of 1.0 and
    `Percent(Decimal('2.5'))` was admitted, where a slip is a plausible
    concentration; a string was refused in `math.isfinite`'s words and a
    signalling NaN escaped as its `ValueError`; and `Fraction(-0.0)` held
    minus zero, which `format_percent` printed as `-0.00%`. Each is now a
    `TypeError` naming the value under the name it was built with, before any
    comparison reads it, and minus zero is held as the zero it is. An `int`
    past the float range is compared exactly and refused against the range,
    one too long to print named by how long it is, where `math.isfinite`
    raised `OverflowError` and the message itself raised `ValueError`.
    """

    for value in (True, numpy.True_, Decimal("2.5"), Decimal("sNaN"), "0.5"):
        with pytest.raises(TypeError) as raised:
            concentration(value, name="alveolar " + name)  # type: ignore[call-arg]

        assert str(raised.value).startswith(
            f"alveolar {name} of {value!r} has type {type(value).__name__}, not int or float"
        )

    from_negative_zero = concentration(-0.0)

    assert type(from_negative_zero) is concentration
    assert from_negative_zero.hex() == (0.0).hex()

    for number in (1, 1.0, numpy.float64(1.0)):
        assert concentration(number).hex() == (1.0).hex()

    assert format_percent(Fraction(-0.0)) == "0.00%"

    with pytest.raises(
        SimulationConfigurationError, match=f"^{name} of 1" + "0" * 400 + " is outside"
    ):
        concentration(10**400)

    with pytest.raises(SimulationConfigurationError) as refused:
        concentration(-(10**5000))

    assert str(refused.value).startswith(
        f"{name} of -<more than {sys.get_int_max_str_digits():,} digits> is outside"
    )


@pytest.mark.parametrize(
    ("crossing", "name", "form"),
    [(fraction_from_percent, "percent", Percent), (percent_from_fraction, "fraction", Fraction)],
    ids=["fraction_from_percent", "percent_from_fraction"],
)
def test_a_crossing_refuses_what_is_not_a_number_before_converting_it(
    crossing: Callable[[Any], float], name: str, form: type[float]
) -> None:
    """`True` times a hundred is 100.0, a percent the range admits (`PL-LLMN`).

    Each crossing does its arithmetic before a constructor sees the result, so
    a `bool` came through as a held value - `format_percent(True)` printed
    `100.00%` - and a `str` or a `Decimal` was refused as Python's unsupported
    operand. `PL-LLMN` put the constructors' own number rule ahead of the
    arithmetic; since `PL-1DP1` each crossing asks the wider question every
    place a concentration is held asks, whether the value was built as the form
    at all, so each of these is refused in `require_percent`'s or
    `require_fraction`'s words, before any arithmetic, and the constructor it
    names refuses it again as not a number.
    """

    for value in (True, numpy.True_, Decimal("50"), "50"):
        with pytest.raises(TypeError) as raised:
            crossing(value)

        assert str(raised.value).startswith(
            f"{name} of {value!r} was not built as {form.__name__}, it is {type(value).__name__}"
        )

    with pytest.raises(TypeError, match="^fraction of True was not built as Fraction, it is bool"):
        format_percent(True)  # type: ignore[arg-type]


def test_a_refused_fraction_is_named_as_it_was_built() -> None:
    """A fraction a rounding past 1 is refused under the name it was given.

    The regression for the refusal moving out of each compartment's setter and
    into the constructor (`PL-4R3W`). A setter used to name the compartment in
    the refusal (`PL-SPN6`); the constructor now runs first, so unless the
    caller names the fraction it builds, the halted-run notice cannot say which
    of the five compartments and the circuit refused. `1.0000000000000002` is
    `nextafter(1.0, inf)`, the value a 100% dial's exact path rounds towards.
    """

    with pytest.raises(
        SimulationConfigurationError,
        match=r"^alveolar partial_pressure_fraction of 1\.0000000000000002 is outside 0 to 1, ",
    ):
        Fraction(1.0000000000000002, name="alveolar partial_pressure_fraction")


@pytest.mark.parametrize("value", [0.0, 5e-324, 8.0, nextafter(100.0, 0.0), 100.0])
def test_a_percent_from_0_through_100_is_the_number_it_was_built_from(value: float) -> None:
    percent = Percent(value)

    assert isinstance(percent, float)
    assert float(percent).hex() == value.hex()


@pytest.mark.parametrize(
    "value", [nextafter(0.0, -1.0), -0.001, nextafter(100.0, inf), 150.0, inf, -inf, nan]
)
def test_a_percent_outside_0_to_100_cannot_be_built(value: float) -> None:
    with pytest.raises(SimulationConfigurationError, match=r"is outside 0 to 100"):
        Percent(value)


def test_a_refused_percent_is_named_as_it_was_built() -> None:
    """A percent is refused under the name its caller gives it, as a fraction is.

    The dial's handler names the percent it builds (`app/run_view.py`), so a
    setting refused here says which control it came from rather than
    "percent".
    """

    with pytest.raises(
        SimulationConfigurationError,
        match=r"^delivered_concentration_percent of 150\.0 is outside 0 to 100, ",
    ):
        Percent(150.0, name="delivered_concentration_percent")


def test_a_refused_dial_setting_is_pinned_whole() -> None:
    """The whole sentence the "Setting refused" banner shows for a dial past 100%.

    The test above anchors only the start of the message, so the range and
    the section it cites could change unseen (`PL-79PK`).
    """

    with pytest.raises(SimulationConfigurationError) as refusal:
        Percent(150.0, name="delivered_concentration_percent")

    assert str(refusal.value) == (
        "delivered_concentration_percent of 150.0 is outside 0 to 100, the range a percent "
        'of one atmosphere takes (docs/MODEL.md, "Concentrations")'
    )


def test_a_refused_compartment_fraction_is_pinned_whole() -> None:
    """The whole sentence a halt shows when a compartment's fraction leaves 0 to 1.

    A step, a snapshot and a chart frame each build a compartment's fraction
    under the compartment's name, and the "Simulation stopped" banner prints
    the refusal word for word. The tests of those paths anchor only its start
    (`PL-79PK`).
    """

    with pytest.raises(SimulationConfigurationError) as refusal:
        Fraction(1.0000001, name="alveolar partial_pressure_fraction")

    assert str(refusal.value) == (
        "alveolar partial_pressure_fraction of 1.0000001 is outside 0 to 1, the range a "
        'fraction of one atmosphere takes (docs/MODEL.md, "Concentrations")'
    )


def test_neither_type_can_be_built_from_the_other() -> None:
    """Rebuilding a concentration as the other type is the conversion missed.

    `mypy` passes both calls, because each type is a `float` and the other's
    constructor takes one, so the constructor is what refuses them, with the
    advice `require_fraction` and `require_percent` give: convert, since a
    rebuild keeps the number and changes what it means a hundredfold.
    """

    with pytest.raises(
        TypeError,
        match=r"^delivered_concentration_percent of 0\.08 is a Fraction, not a Percent: "
        r"convert it with percent_from_fraction, ",
    ):
        Percent(Fraction(0.08), name="delivered_concentration_percent")

    with pytest.raises(
        TypeError,
        match=r"^fraction of 0\.5 is a Percent, not a Fraction: convert it with "
        r"fraction_from_percent, ",
    ):
        Fraction(Percent(0.5))


def test_neither_conversion_takes_the_form_it_converts_to() -> None:
    """A value already in the form a crossing returns is refused before the arithmetic runs.

    `fraction_from_percent(Fraction(0.5))` was a `Fraction` of 0.005 and
    `percent_from_fraction(Percent(0.5))` a `Percent` of 50.0 - a 0.5% dial
    shown as 50% - because each crossing did its arithmetic first and the
    constructor then saw a plain `float` inside its range (`PL-SWD1`). The
    directives are `mypy`'s refusal of both calls; the `TypeError` is the
    run-time one, and it says to use the value as it is rather than to convert
    it, since the remedy the constructors give, convert, is the error here. A
    value of each crossing's own form converts as before, and the display
    formatter built on the display crossing refuses with it.
    """

    with pytest.raises(TypeError) as to_the_model_form:
        fraction_from_percent(Fraction(0.5))  # type: ignore[arg-type]

    assert str(to_the_model_form.value) == (
        "percent of 0.5 is already a Fraction, not a Percent to convert: dividing it by a "
        "hundred would hold a concentration a hundred times too small, so use it as the "
        "Fraction it is (core/concentration.py)"
    )

    with pytest.raises(TypeError) as to_the_display_form:
        percent_from_fraction(Percent(0.5))  # type: ignore[arg-type]

    assert str(to_the_display_form.value) == (
        "fraction of 0.5 is already a Percent, not a Fraction to convert: multiplying it by a "
        "hundred would hold a concentration a hundred times too large, so use it as the "
        "Percent it is (core/concentration.py)"
    )

    with pytest.raises(TypeError, match="^fraction of 0.5 is already a Percent, not a Fraction"):
        format_percent(Percent(0.5))  # type: ignore[arg-type]

    assert fraction_from_percent(Percent(0.5)) == Fraction(0.005)
    assert percent_from_fraction(Fraction(0.5)) == Percent(50.0)


@pytest.mark.parametrize(
    "other",
    [
        SimulationStep(0.05),
        StepCount(1),
        CaseInstant(0.5),
        FreshGasFlow(2.0),
        AlveolarVentilation(4.0),
        CardiacOutput(5.0),
    ],
    ids=lambda other: type(other).__name__,
)
def test_another_quantity_handed_in_as_a_concentration_is_refused_as_a_swapped_argument(
    other: object,
) -> None:
    """Named as the quantity it was built as, and not told to rebuild or to convert.

    A `SimulationStep(0.05)` arriving where a fraction belongs, or a
    `FreshGasFlow(2.0)` where the dial does, is a swapped argument and not the
    missed conversion the two types refuse in each other. Until `PL-CX2C`
    `require_fraction` and `require_percent` knew only each other, so each
    told the caller to build the type from the value - a concentration of
    0.05 from a step, a dial at 2% from a flow - which every later check
    admits. Every checked quantity is one record (`core/checked_number.py`),
    so the refusal names the type the value was built as and prescribes
    nothing, where a concentration is held, at the constructor and, since
    `PL-SWD1`, at the two crossings alike: `fraction_from_percent(FreshGasFlow(2.0))`
    was a `Fraction` of 0.02 and `percent_from_fraction(CaseInstant(0.5))` a
    `Percent` of 50.0, the arithmetic having run on the number before the
    constructor saw a plain `float`.
    """

    with pytest.raises(TypeError) as as_a_fraction:
        require_fraction("alveolar partial_pressure_fraction", other)

    with pytest.raises(TypeError) as as_a_percent:
        require_percent("delivered_concentration_percent", other)

    with pytest.raises(TypeError) as to_the_model_form:
        fraction_from_percent(other)  # type: ignore[arg-type]

    with pytest.raises(TypeError) as to_the_display_form:
        percent_from_fraction(other)  # type: ignore[arg-type]

    assert str(as_a_fraction.value) == (
        f"alveolar partial_pressure_fraction of {other!r} was built as "
        f"{type(other).__name__}, which is not Fraction: it is another quantity, so build "
        "Fraction from the value that alveolar partial_pressure_fraction should hold, not "
        "from this one (core/checked_number.py)"
    )
    assert str(as_a_percent.value) == (
        f"delivered_concentration_percent of {other!r} was built as {type(other).__name__}, "
        "which is not Percent: it is another quantity, so build Percent from the value that "
        "delivered_concentration_percent should hold, not from this one "
        "(core/checked_number.py)"
    )
    assert str(to_the_model_form.value) == (
        f"percent of {other!r} was built as {type(other).__name__}, which is not Percent: it is "
        "another quantity, so build Percent from the value that percent should hold, not from "
        "this one (core/checked_number.py)"
    )
    assert str(to_the_display_form.value) == (
        f"fraction of {other!r} was built as {type(other).__name__}, which is not Fraction: it "
        "is another quantity, so build Fraction from the value that fraction should hold, not "
        "from this one (core/checked_number.py)"
    )


def test_a_count_too_long_to_print_is_named_where_a_concentration_is_held() -> None:
    """`require_fraction` and `require_percent` print through `shown`, as the constructors do.

    Until `PL-CX2C` each printed with `repr`, so a bare `int` past the digits
    CPython prints raised `ValueError` while the `TypeError` was being
    written, the escape `PL-5F76` closed for the count.
    """

    named = f"<more than {sys.get_int_max_str_digits():,} digits>"

    with pytest.raises(TypeError) as as_a_fraction:
        require_fraction("fraction", 10**5000)

    with pytest.raises(TypeError) as as_a_percent:
        require_percent("percent", 10**5000)

    assert str(as_a_fraction.value).startswith(f"fraction of {named} was not built as Fraction")
    assert str(as_a_percent.value).startswith(f"percent of {named} was not built as Percent")


def test_neither_conversion_can_refuse_a_value_of_its_own_type() -> None:
    """Each crossing builds the checked type, and no value of the other refuses it.

    Division and multiplication round monotonically and 100 maps exactly to 1,
    so a percent from 0 through 100 gives a fraction from 0 through 1 and back.
    Pinned over every 0.001% step of the range and both ends' neighbours,
    because the claim is about rounding, which only a sweep tests.
    """

    percents = [step / 1000 for step in range(100_001)]
    percents += [5e-324, nextafter(100.0, 0.0)]

    for value in percents:
        fraction = fraction_from_percent(Percent(value))
        assert type(fraction) is Fraction
        assert type(percent_from_fraction(fraction)) is Percent

    for value in (5e-324, nextafter(1.0, 0.0), 1.0):
        assert type(percent_from_fraction(Fraction(value))) is Percent


def test_arithmetic_on_a_concentration_is_a_plain_float() -> None:
    """A computed value carries no proof, so it is built into the type again.

    That is the module docstring's first limit, and why `AgentUptakeSystem`
    builds each fraction a step computes as a `Fraction` before any
    compartment holds it.
    """

    fraction = Fraction(0.5)
    percent = Percent(2.0)

    assert type(fraction * 2.0) is float
    assert type(fraction + fraction) is float
    assert type(percent / 100.0) is float
    assert type(percent - percent) is float


def test_a_copied_or_pickled_concentration_is_still_checked() -> None:
    """A `Fraction` or `Percent` copied for a branch, or saved, is still of its own type.

    A copy, a deep copy and a pickle each rebuild through the constructor
    rather than around it. The next test checks that a pickle edited outside
    the range is refused when it is loaded.
    `tests/unit/test_checked_number.py` checks it for every checked type at
    every pickle protocol (`PL-5D1Z`).
    """

    for value in (Fraction(0.02), Percent(8.0)):
        for copied in (copy.copy(value), copy.deepcopy(value), pickle.loads(pickle.dumps(value))):
            assert type(copied) is type(value)
            assert copied == value


@pytest.mark.parametrize(
    ("saved", "tampered_value", "refusal"),
    [
        (Fraction(0.5), 1.5, "^fraction of 1.5 is outside 0 to 1"),
        (Percent(8.0), 150.0, "^percent of 150.0 is outside 0 to 100"),
    ],
)
def test_a_pickle_edited_past_the_range_is_refused_when_it_is_loaded(
    saved: float, tampered_value: float, refusal: str
) -> None:
    """Loading a pickle at the default protocol runs the constructor's check.

    The saved value is overwritten in the bytes, as a file edited by hand would
    be, so a load that went around the constructor would hand back the type
    holding a value outside its range.
    """

    pickled = pickle.dumps(saved)
    tampered = pickled.replace(struct.pack(">d", saved), struct.pack(">d", tampered_value))

    assert tampered != pickled

    with pytest.raises(SimulationConfigurationError, match=refusal):
        pickle.loads(tampered)


def test_a_fraction_reaching_a_percent_parameter_is_refused() -> None:
    """The missing conversion the types exist for, refused by `mypy` and at run time.

    `0.08` is sevoflurane's full dial, 8%, written as a fraction. Passed as a
    percent it would be 0.08% — a hundredfold error, the vaporizer all but off
    rather than at its maximum — and nothing after this would refuse it: it is
    under the vaporizer maximum. The directive is `mypy`'s refusal; the
    `TypeError` is the run-time one `PL-4R3W` added, and it says to convert.
    """

    circuit = BreathingCircuit(max_delivered_concentration_percent=SEVOFLURANE_MAXIMUM_PERCENT)

    with pytest.raises(
        TypeError,
        match="^delivered_concentration_percent of 0.08 is a Fraction, not a Percent: convert it",
    ):
        circuit.set_delivered_concentration_percent(Fraction(0.08))  # type: ignore[arg-type]

    assert circuit.delivered_concentration_percent == 0.0


def test_a_percent_reaching_a_fraction_parameter_is_refused() -> None:
    """The same missing conversion in the other direction, a hundred times too large."""

    circuit = BreathingCircuit()

    with pytest.raises(
        TypeError,
        match="^inspired_partial_pressure_fraction of 0.5 is a Percent, not a Fraction: convert it",
    ):
        circuit.set_inspired_partial_pressure_fraction(Percent(0.5))  # type: ignore[arg-type]

    assert circuit.inspired_partial_pressure_fraction == 0.0


def test_a_mac_handed_in_as_a_fraction_is_refused() -> None:
    """The divisor of every MAC multiple shown, a hundred times too small.

    Sevoflurane's MAC is 2%, and as a fraction it is 0.02: held as the
    percent, it would put 1 MAC at "100.00 ×MAC". The agent's parameters
    refuse it when they are built, which `dataclasses.replace` does, so a
    MAC edited in a test or a notebook meets the check a file's MAC meets.
    """

    sevoflurane = load_sevoflurane_parameters()

    with pytest.raises(
        TypeError, match="^mac_percent of 0.02 is a Fraction, not a Percent: convert it"
    ):
        replace(sevoflurane, mac_percent=Fraction(0.02))  # type: ignore[arg-type]


def test_a_percent_built_from_a_fractions_value_is_not_caught() -> None:
    """The module docstring's third limit, pinned so it cannot be read as more.

    A percent built from a fraction's *value* is a valid percent, so the type
    cannot refuse it and the vaporizer maximum passes it. Only the dial's
    writers each passing a value already in percent stands against it.
    """

    circuit = BreathingCircuit(max_delivered_concentration_percent=SEVOFLURANE_MAXIMUM_PERCENT)

    circuit.set_delivered_concentration_percent(Percent(0.08))

    assert circuit.delivered_partial_pressure_fraction == pytest.approx(0.0008)


def test_a_bare_float_is_refused_wherever_a_concentration_is_held() -> None:
    """A value nobody built is refused before anything moves, at every entry point.

    `mypy` refuses a bare `float` at each of these in `src/`, but it does not
    read `tests/`, and it passes a value typed `Any`. This is the runtime half:
    a `TypeError`, because passing the wrong type is a programming error rather
    than a setting the simulator rejected (`core/exceptions.py`). Every value is
    inside its range, so what is refused is the type and nothing else, and each
    refusal names the value it was handed in as.
    """

    system = AgentUptakeSystem.default()
    settings = system.equation_settings()
    agent = load_sevoflurane_parameters()
    venous = system.patient.venous_blood
    fat = system.patient.fat
    vector_before = system.state_vector()
    step = SimulationStep(0.1)

    with pytest.raises(TypeError) as as_a_fraction:
        system.circuit.set_inspired_partial_pressure_fraction(0.0)  # type: ignore[arg-type]

    assert str(as_a_fraction.value) == (
        "inspired_partial_pressure_fraction of 0.0 was not built as Fraction, it is float: "
        "build it as Fraction(...) where it is computed, which checks it against 0 to 1 once "
        '(docs/MODEL.md, "Concentrations")'
    )

    with pytest.raises(TypeError) as as_a_percent:
        system.circuit.set_delivered_concentration_percent(2.0)  # type: ignore[arg-type]

    assert str(as_a_percent.value) == (
        "delivered_concentration_percent of 2.0 was not built as Percent, it is float: build "
        "it as Percent(...) where it is set, which checks it against 0 to 100 once "
        '(docs/MODEL.md, "Concentrations")'
    )

    with pytest.raises(TypeError, match="^alveolar partial_pressure_fraction of 0.0 was not built"):
        system.alveoli.set_partial_pressure_fraction(0.0)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="^venous partial_pressure_fraction of 0.0 was not built"):
        venous.set_partial_pressure_fraction(0.0)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="^fat partial_pressure_fraction of 0.0 was not built"):
        fat.set_partial_pressure_fraction(0.0)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="^venous tissue_return_partial_pressure_fraction of 0.0"):
        venous.advance(0.0, step, 5.0)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="^fat arterial_partial_pressure_fraction of 0.0 was"):
        fat.advance(0.0, step, 0.3)  # type: ignore[arg-type]

    assert system.state_vector() == vector_before

    with pytest.raises(TypeError, match="^delivered_concentration_percent of 2.0 was not built"):
        BreathingCircuit(delivered_concentration_percent=2.0)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="^max_delivered_concentration_percent of 8.0 was not"):
        BreathingCircuit(max_delivered_concentration_percent=8.0)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="^inspired_partial_pressure_fraction of 0.0 was not built"):
        BreathingCircuit(inspired_partial_pressure_fraction=0.0)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="^inspired_partial_pressure_fraction of 0.0 was not built"):
        BreathingCircuitState(inspired_partial_pressure_fraction=0.0)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="^delivered_concentration_percent of 2.0 was not built"):
        replace(settings, delivered_concentration_percent=2.0)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="^max_delivered_concentration_percent of 8.0 was not"):
        replace(settings, max_delivered_concentration_percent=8.0)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="^max_delivered_concentration_percent of 8.0 was not"):
        replace(agent, max_delivered_concentration_percent=8.0)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="^mac_percent of 2.0 was not built"):
        replace(agent, mac_percent=2.0)  # type: ignore[arg-type]


def test_fraction_from_percent_refuses_a_bare_float() -> None:
    """A number nobody built carries no form, so the crossing cannot convert it (`PL-1DP1`).

    `fraction_from_percent(50.0)` was a `Fraction` of 0.5 while every place a
    percent is held had refused the same 50.0 since `PL-4R3W`, so the crossing
    was where a number of unknown form still entered. The refusal is
    `require_percent`'s, in its words, naming the constructor to build where
    the form is known, and nothing is converted. `mypy` refuses the call in
    `src/`, which the directive asserts; the `TypeError` is the run-time half,
    for a caller it does not read. A value built as the form converts as before.
    """

    with pytest.raises(TypeError) as refused:
        fraction_from_percent(50.0)  # type: ignore[arg-type]

    assert str(refused.value) == (
        "percent of 50.0 was not built as Percent, it is float: build it as Percent(...) "
        'where it is set, which checks it against 0 to 100 once (docs/MODEL.md, "Concentrations")'
    )

    with pytest.raises(TypeError, match="^percent of 50 was not built as Percent, it is int"):
        fraction_from_percent(50)  # type: ignore[arg-type]

    narrower = numpy.float64(50.0)

    with pytest.raises(TypeError) as not_the_type:
        fraction_from_percent(narrower)  # type: ignore[arg-type]

    assert str(not_the_type.value).startswith(
        f"percent of {narrower!r} was not built as Percent, it is float64"
    )

    assert fraction_from_percent(Percent(50.0)) == Fraction(0.5)


def test_percent_from_fraction_refuses_a_bare_float() -> None:
    """The display direction, where a 0.5 could be a fraction or a 0.5% dial (`PL-1DP1`).

    `percent_from_fraction(0.5)` was a `Percent` of 50.0 and `format_percent(0.5)`
    printed `50.00%`, whichever the 0.5 was: the number carries no form to tell
    them apart, which is why it cannot be converted rather than a reason to
    take it as given, as `PL-4R3W` had chosen. Refused as `require_fraction`
    refuses a bare float wherever a fraction is held, and the formatter built
    on the crossing refuses with it, so nothing is printed.
    """

    with pytest.raises(TypeError) as refused:
        percent_from_fraction(0.5)  # type: ignore[arg-type]

    assert str(refused.value) == (
        "fraction of 0.5 was not built as Fraction, it is float: build it as Fraction(...) "
        "where it is computed, which checks it against 0 to 1 once "
        '(docs/MODEL.md, "Concentrations")'
    )

    with pytest.raises(TypeError, match="^fraction of 0.5 was not built as Fraction, it is float"):
        format_percent(0.5)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="^fraction of 1 was not built as Fraction, it is int"):
        percent_from_fraction(1)  # type: ignore[arg-type]

    assert percent_from_fraction(Fraction(0.5)) == Percent(50.0)
    assert format_percent(Fraction(0.005)) == "0.50%"


def test_a_percent_past_100_is_refused_where_it_is_built_and_the_maximum_where_it_is_set() -> None:
    """The two refusals a dial meets, each in its own place.

    A percent's range is the constructor's, so `Percent(150.0)` never reaches
    the circuit; the vaporizer maximum is a relation the circuit holds, so it is
    the circuit that refuses 50% against 8% (`PL-BBMG`). Neither moves the dial.
    """

    circuit = BreathingCircuit(max_delivered_concentration_percent=SEVOFLURANE_MAXIMUM_PERCENT)

    with pytest.raises(SimulationConfigurationError, match="percent of 150.0 is outside 0 to 100"):
        circuit.set_delivered_concentration_percent(Percent(150.0))

    with pytest.raises(SimulationConfigurationError, match="exceeds the vaporizer maximum"):
        circuit.set_delivered_concentration_percent(Percent(50.0))

    assert circuit.delivered_concentration_percent == 0.0
