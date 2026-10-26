"""Tests of the two checked forms of a concentration, and of the conversion between them.

`core/concentration.py` states the rules that these tests check. Below, a "crossing" means
one of the two functions that convert between the forms. `Fraction` and `Percent` check
their ranges when they are built. So the tests below check the edges of each range once,
on the constructor, rather than at each place that stores a value (`PL-4R3W`).

Several tests below pass a value of the wrong type to a parameter, in a call that `mypy`
would reject. The mypy gate does not check the `# type: ignore` on such a call, because
`tests/` is outside `[tool.mypy] files`. Instead, `tools/type_ignore_check.py` checks it.
That tool runs mypy over this tree with `warn_unused_ignores` on, and reports any directive
that is no longer needed. So if a directive below stops having an effect, `make check`
fails. That failure is what shows that `mypy` still rejects the call. The test's own
assertion covers what the call does at run time. Each of these calls is also rejected at
run time, and has been since `PL-4R3W` (`PL-WVSK`).
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
    MacPercent,
    Percent,
    fraction_from_percent,
    percent_from_fraction,
    require_fraction,
    require_mac_percent,
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

# This is sevoflurane's vaporizer maximum, in the percent that its dial reads.
# Since `PL-NJPB` the dial is set in percent, so a missing conversion now goes
# the other way. A fraction mistaken for a percent is a hundred times too small
# and lands between 0% and 1%. That is less than this maximum and less than
# every shipped agent's maximum, so `BreathingCircuit._require_deliverable`
# refuses none of these mistaken values.
SEVOFLURANE_MAXIMUM_PERCENT = Percent(8.0)


@pytest.mark.parametrize(
    ("percent", "fraction"), [(0.0, 0.0), (2.0, 0.02), (8.0, 0.08), (18.0, 0.18), (100.0, 1.0)]
)
def test_the_two_forms_convert_both_ways(percent: float, fraction: float) -> None:
    """The cases are the dial readings the three shipped agents use, and both ends of the range."""

    assert fraction_from_percent(Percent(percent)) == pytest.approx(fraction)
    assert percent_from_fraction(Fraction(fraction)) == pytest.approx(percent)


def test_the_factor_is_a_hundred_and_is_written_once() -> None:
    assert PERCENT_PER_UNIT_FRACTION == 100.0
    assert fraction_from_percent(Percent(PERCENT_PER_UNIT_FRACTION)) == 1.0


@pytest.mark.parametrize("value", [0.0, 5e-324, 0.02, nextafter(1.0, 0.0), 1.0])
def test_a_fraction_from_0_through_1_is_the_number_it_was_built_from(value: float) -> None:
    """Both ends are fractions, as is the nearest float inside each end, and none is rounded."""

    fraction = Fraction(value)

    assert isinstance(fraction, float)
    assert float(fraction).hex() == value.hex()


@pytest.mark.parametrize(
    "value", [nextafter(0.0, -1.0), -0.001, nextafter(1.0, inf), 1.001, inf, -inf, nan]
)
def test_a_fraction_outside_0_to_1_cannot_be_built(value: float) -> None:
    """The constructor is the one place that checks a fraction's range, at each edge and beyond.

    The two `nextafter` values are the first floats outside the range. Before
    `PL-4R3W` this check was `require_fraction` in `core/validation.py`, which
    was called at each of the twelve places where a value entered.
    """

    with pytest.raises(SimulationConfigurationError, match=r"is outside 0 to 1"):
        Fraction(value)


@pytest.mark.parametrize(
    ("concentration", "name"), [(Fraction, "fraction"), (Percent, "percent")], ids=repr
)
def test_a_concentration_refuses_what_is_not_a_number_and_holds_negative_zero_as_zero(
    concentration: type[float], name: str
) -> None:
    """A concentration is built only from an int or a float, with no sign at zero (`PL-LLMN`).

    The concentrations had the same gaps as the flows. They are kept
    consistent with the flows on purpose, so that one rule covers all of them.
    `Fraction(True)` was a fraction of 1.0, and `Percent(Decimal('2.5'))` was
    accepted, although a slip like that gives a plausible concentration. A
    string was refused in `math.isfinite`'s words, and a signalling NaN escaped
    as that function's `ValueError`. `Fraction(-0.0)` stored minus zero, which
    `format_percent` printed as `-0.00%`. Each of these is now a `TypeError`
    that names the value under the name it was built with, before any
    comparison uses it. Minus zero is stored as the zero it is. An `int`
    beyond the float range is compared exactly and refused against the range,
    and one too long to print is named by how long it is. Before, `math.isfinite`
    raised `OverflowError` for such an `int`, and building the message itself
    raised `ValueError`.
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
    """`True` times a hundred is 100.0, which is a percent inside the range (`PL-LLMN`).

    Each crossing does its arithmetic before a constructor sees the result. So
    a `bool` came through as a stored value, and `format_percent(True)` printed
    `100.00%`. A `str` or a `Decimal` was refused only as an unsupported
    operand, in Python's words. `PL-LLMN` put the constructors' own number rule
    ahead of the arithmetic. Since `PL-1DP1`, each crossing asks the wider
    question that every place storing a concentration asks: was the value
    built as that form at all? So each of these values is refused in the words
    of `require_percent` or `require_fraction`, before any arithmetic. The
    constructor that the message names would refuse it again, as not a number.
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
    """A fraction one rounding step above 1 is refused under the name it was given.

    This is the regression test for moving the refusal out of each
    compartment's setter and into the constructor (`PL-4R3W`). A setter used to
    name the compartment in the refusal (`PL-SPN6`). The constructor now runs
    first. So unless the caller names the fraction it builds, the notice for a
    halted run cannot say which of the five compartments or the circuit refused
    it. `1.0000000000000002` is `nextafter(1.0, inf)`, the value that a 100%
    dial's exact path rounds towards.
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
    """Pin the whole sentence that the "Setting refused" banner shows for a dial above 100%.

    The test above anchors only the start of the message, so the range and the
    cited section could change without any test noticing (`PL-79PK`).
    """

    with pytest.raises(SimulationConfigurationError) as refusal:
        Percent(150.0, name="delivered_concentration_percent")

    assert str(refusal.value) == (
        "delivered_concentration_percent of 150.0 is outside 0 to 100, the range a percent "
        'of one atmosphere takes (docs/MODEL.md, "Concentrations")'
    )


def test_a_refused_compartment_fraction_is_pinned_whole() -> None:
    """Pin the whole sentence that a halt shows when a compartment's fraction leaves 0 to 1.

    A step, a snapshot and a chart frame each build a compartment's fraction
    under the compartment's name, and the "Simulation stopped" banner prints
    the refusal message word for word. The tests of those paths anchor only the
    start of the message (`PL-79PK`).
    """

    with pytest.raises(SimulationConfigurationError) as refusal:
        Fraction(1.0000001, name="alveolar partial_pressure_fraction")

    assert str(refusal.value) == (
        "alveolar partial_pressure_fraction of 1.0000001 is outside 0 to 1, the range a "
        'fraction of one atmosphere takes (docs/MODEL.md, "Concentrations")'
    )


def test_neither_type_can_be_built_from_the_other() -> None:
    """Rebuilding a concentration as the other type is a missed conversion.

    `mypy` accepts both calls, because each type is a `float` and the other
    type's constructor takes a `float`. So the constructor is what refuses
    them. It gives the same advice that `require_fraction` and
    `require_percent` give, which is to convert. A rebuild keeps the number but
    changes its meaning a hundredfold.
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

    `fraction_from_percent(Fraction(0.5))` used to return a `Fraction` of
    0.005. `percent_from_fraction(Percent(0.5))` returned a `Percent` of 50.0,
    so a 0.5% dial was shown as 50%. Each crossing did its arithmetic first,
    and the constructor then saw a plain `float` inside its range (`PL-SWD1`).
    The directives record that `mypy` rejects both calls. The `TypeError` is
    the run-time refusal. Its message says to use the value as it is rather
    than to convert it, because converting, the remedy that the constructors
    suggest, is the mistake here. A value in each crossing's own input form
    converts as before. The display formatter, which is built on the display
    crossing, refuses the same value that crossing refuses.
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
    """The refusal names the quantity the value was built as, with no advice to rebuild or convert.

    A `SimulationStep(0.05)` arriving where a fraction belongs, or a
    `FreshGasFlow(2.0)` arriving where the dial setting belongs, is a swapped
    argument. It is not the missed conversion that each concentration type
    refuses in the other. Until `PL-CX2C`, `require_fraction` and
    `require_percent` knew only about each other. So each told the caller to
    build its type from the value: a concentration of 0.05 from a step, or a
    dial at 2% from a flow. Every later check accepts such a value. All checked
    quantities are now handled by one module (`core/checked_number.py`). So the
    refusal names the type that the value was built as, and prescribes nothing.
    It does so wherever a concentration is stored: at the constructor and,
    since `PL-SWD1`, at the two crossings as well. Before that,
    `fraction_from_percent(FreshGasFlow(2.0))` returned a `Fraction` of 0.02,
    and `percent_from_fraction(CaseInstant(0.5))` returned a `Percent` of 50.0.
    The arithmetic had run on the number before the constructor saw a plain
    `float`.
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
    """`require_fraction` and `require_percent` format a value with `shown`, as constructors do.

    Until `PL-CX2C` each formatted the value with `repr`. So a bare `int` with
    more digits than CPython will print raised `ValueError` while the
    `TypeError` message was being built. `PL-5F76` had closed the same escape
    for the count.
    """

    named = f"<more than {sys.get_int_max_str_digits():,} digits>"

    with pytest.raises(TypeError) as as_a_fraction:
        require_fraction("fraction", 10**5000)

    with pytest.raises(TypeError) as as_a_percent:
        require_percent("percent", 10**5000)

    assert str(as_a_fraction.value).startswith(f"fraction of {named} was not built as Fraction")
    assert str(as_a_percent.value).startswith(f"percent of {named} was not built as Percent")


def test_neither_conversion_can_refuse_a_value_of_its_own_type() -> None:
    """Each crossing builds the checked type, and no valid value of the other type is refused.

    Division and multiplication round monotonically, and 100 maps exactly to 1.
    So a percent from 0 through 100 gives a fraction from 0 through 1, and the
    fraction converts back to a valid percent. The test pins this over every
    0.001% step of the range and the nearest float inside each end, because the
    claim is about rounding, and only a sweep tests rounding.
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
    """A computed value carries no proof of its range, so it must be built into the type again.

    That is the first limit that the concentration module's docstring states.
    It is also why `AgentUptakeSystem` builds each fraction that a step
    computes as a `Fraction` before any compartment stores it.
    """

    fraction = Fraction(0.5)
    percent = Percent(2.0)

    assert type(fraction * 2.0) is float
    assert type(fraction + fraction) is float
    assert type(percent / 100.0) is float
    assert type(percent - percent) is float


def test_a_copied_or_pickled_concentration_is_still_checked() -> None:
    """A `Fraction` or `Percent` copied for a branch, or saved, is still of its own type.

    A copy, a deep copy and a pickle each rebuild the value through the
    constructor rather than bypassing it. The next test checks that a pickle
    edited outside the range is refused when it is loaded.
    `tests/unit/test_checked_number.py` checks the same behaviour for every
    checked type at every pickle protocol (`PL-5D1Z`).
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

    The test overwrites the saved value in the pickled bytes, as a hand edit of
    a file would. A load that bypassed the constructor would then return the
    type holding a value outside its range.
    """

    pickled = pickle.dumps(saved)
    tampered = pickled.replace(struct.pack(">d", saved), struct.pack(">d", tampered_value))

    assert tampered != pickled

    with pytest.raises(SimulationConfigurationError, match=refusal):
        pickle.loads(tampered)


def test_a_fraction_reaching_a_percent_parameter_is_refused() -> None:
    """The missing conversion that the types exist to catch is refused by `mypy` and at run time.

    `0.08` is sevoflurane's full dial setting, 8%, written as a fraction.
    Passed as a percent, it would be 0.08%. That is a hundredfold error, with
    the vaporizer almost off rather than at its maximum. Nothing after this
    point would refuse it, because it is less than the vaporizer maximum. The
    directive records that `mypy` rejects the call. The `TypeError` is the
    run-time refusal that `PL-4R3W` added, and its message says to convert.
    """

    circuit = BreathingCircuit(
        circuit_volume_l=6.0, max_delivered_concentration_percent=SEVOFLURANE_MAXIMUM_PERCENT
    )

    with pytest.raises(
        TypeError,
        match="^delivered_concentration_percent of 0.08 is a Fraction, not a Percent: convert it",
    ):
        circuit.set_delivered_concentration_percent(Fraction(0.08))  # type: ignore[arg-type]

    assert circuit.delivered_concentration_percent == 0.0


def test_a_percent_reaching_a_fraction_parameter_is_refused() -> None:
    """The same missing conversion the other way round makes a value a hundred times too large."""

    circuit = BreathingCircuit(
        circuit_volume_l=6.0, max_delivered_concentration_percent=Percent(100.0)
    )

    with pytest.raises(
        TypeError,
        match="^inspired_partial_pressure_fraction of 0.5 is a Percent, not a Fraction: convert it",
    ):
        circuit.set_inspired_partial_pressure_fraction(Percent(0.5))  # type: ignore[arg-type]

    assert circuit.inspired_partial_pressure_fraction == 0.0


def test_a_mac_handed_in_as_a_fraction_is_refused() -> None:
    """A MAC given as a fraction shrinks the divisor of every displayed MAC multiple a hundredfold.

    Sevoflurane's MAC is 2%, which is 0.02 as a fraction. Stored as the
    percent, 0.02 would show 1 MAC as "100.00 ×MAC". The agent's parameters
    refuse it when they are built, and `dataclasses.replace` builds them. So a
    MAC edited in a test or a notebook meets the same check as a MAC in a file.
    """

    sevoflurane = load_sevoflurane_parameters()

    with pytest.raises(
        TypeError, match="^mac_percent of 0.02 is a Fraction, not a Percent: convert it"
    ):
        replace(sevoflurane, mac_percent=Fraction(0.02))  # type: ignore[arg-type]


@pytest.mark.parametrize("value", [nextafter(0.0, 1.0), 1.2, 2.0, 6.0, 100.0])
def test_a_mac_above_zero_is_the_number_it_was_built_from(value: float) -> None:
    """A `MacPercent` is a `Percent` above zero, and stores the number as given."""

    built = MacPercent(value)

    assert type(built) is MacPercent
    assert isinstance(built, Percent)
    assert built == value


def test_a_mac_of_zero_is_refused_where_it_is_built_and_pinned_whole() -> None:
    """Every displayed MAC multiple divides by the MAC, so a zero MAC is refused once, when built.

    `PL-F9TC` moved this refusal here from the five formatters that divided
    by a MAC and from `AgentParameters`. The message names the value as the
    type stores it, so an `int` zero and minus zero both appear as 0.0.
    """

    for zero in (0.0, -0.0, 0):
        with pytest.raises(SimulationConfigurationError) as refused:
            MacPercent(zero)

        assert str(refused.value) == (
            "mac_percent of 0.0 is not a MAC: a MAC is above 0%, because every MAC multiple "
            "shown divides by it"
        )

    with pytest.raises(SimulationConfigurationError, match="^desflurane_mac of 0.0 is not a MAC"):
        MacPercent(0.0, name="desflurane_mac")

    with pytest.raises(SimulationConfigurationError, match="^mac_percent of 150.0 is outside 0"):
        MacPercent(150.0)


def test_only_a_mac_built_as_one_passes_where_a_mac_is_required() -> None:
    """A dial setting is a `Percent` too, so it is refused where a MAC is required.

    A `MacPercent` passes wherever a `Percent` is required, since it is one.
    """

    require_mac_percent("mac_percent", MacPercent(2.0))
    require_percent("mac_percent", MacPercent(2.0))

    for unchecked in (2.0, Percent(2.0)):
        with pytest.raises(TypeError, match="^mac_percent of 2.0 was not built as MacPercent"):
            require_mac_percent("mac_percent", unchecked)

    with pytest.raises(TypeError, match="^mac_percent of 2.0 was built as Percent"):
        MacPercent(Percent(2.0))

    with pytest.raises(TypeError, match="is a Fraction, not a Percent: convert it"):
        require_mac_percent("mac_percent", Fraction(0.02))


def test_a_percent_built_from_a_fractions_value_is_not_caught() -> None:
    """Pin the concentration module's third limit, so no one takes the types to cover more.

    A percent built from a fraction's *value* is a valid percent, so the type
    cannot refuse it, and the vaporizer maximum accepts it. The only
    protection is that every code path that writes the dial passes a value
    already in percent.
    """

    circuit = BreathingCircuit(
        circuit_volume_l=6.0, max_delivered_concentration_percent=SEVOFLURANE_MAXIMUM_PERCENT
    )

    circuit.set_delivered_concentration_percent(Percent(0.08))

    assert circuit.delivered_partial_pressure_fraction == pytest.approx(0.0008)


def test_a_bare_float_is_refused_wherever_a_concentration_is_held() -> None:
    """A value not built as a checked type is refused at every entry point, before anything changes.

    `mypy` rejects a bare `float` at each of these entry points in `src/`. But
    it does not check `tests/`, and it accepts a value typed `Any`. This test
    covers the run-time half. The refusal is a `TypeError`, because passing the
    wrong type is a programming error rather than a setting the simulator
    rejected (`core/exceptions.py`). Every value is inside its range, so only
    the type is refused. Each refusal names the value and the parameter that it
    was passed as.
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
        BreathingCircuit(
            circuit_volume_l=6.0,
            max_delivered_concentration_percent=Percent(100.0),
            delivered_concentration_percent=2.0,  # type: ignore[arg-type]
        )

    with pytest.raises(TypeError, match="^max_delivered_concentration_percent of 8.0 was not"):
        BreathingCircuit(circuit_volume_l=6.0, max_delivered_concentration_percent=8.0)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="^inspired_partial_pressure_fraction of 0.0 was not built"):
        BreathingCircuit(
            circuit_volume_l=6.0,
            max_delivered_concentration_percent=Percent(100.0),
            inspired_partial_pressure_fraction=0.0,  # type: ignore[arg-type]
        )

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
    """A bare number carries no form, so the crossing cannot convert it (`PL-1DP1`).

    `fraction_from_percent(50.0)` used to return a `Fraction` of 0.5. Every
    place that stores a percent had refused the same 50.0 since `PL-4R3W`, so
    the crossing was the one place where a number of unknown form could still
    enter. The refusal now comes from `require_percent`, in its words. It names
    the constructor to call where the form is known, and nothing is converted.
    `mypy` rejects the call in `src/`, which the directive asserts. The
    `TypeError` is the run-time half, for a caller that `mypy` does not check.
    A value built as that form converts as before.
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
    """In the display direction, a bare 0.5 could be a fraction or a 0.5% dial (`PL-1DP1`).

    `percent_from_fraction(0.5)` used to return a `Percent` of 50.0, and
    `format_percent(0.5)` printed `50.00%`, whichever the 0.5 was. The number
    carries no form that tells the two apart. `PL-4R3W` had chosen to take that
    as a reason to accept the number as given, but it is the reason the number
    cannot be converted. The crossing now refuses it as `require_fraction`
    refuses a bare float wherever a fraction is stored. The formatter built on
    the crossing refuses it too, so nothing is printed.
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
    """A dial setting meets two refusals, each in its own place.

    The constructor checks a percent's range, so `Percent(150.0)` never
    reaches the circuit. The vaporizer maximum is a relation that the circuit
    enforces, so the circuit is what refuses 50% against a maximum of 8%
    (`PL-BBMG`). Neither refusal moves the dial.
    """

    circuit = BreathingCircuit(
        circuit_volume_l=6.0, max_delivered_concentration_percent=SEVOFLURANE_MAXIMUM_PERCENT
    )

    with pytest.raises(SimulationConfigurationError, match="percent of 150.0 is outside 0 to 100"):
        circuit.set_delivered_concentration_percent(Percent(150.0))

    with pytest.raises(SimulationConfigurationError, match="exceeds the vaporizer maximum"):
        circuit.set_delivered_concentration_percent(Percent(50.0))

    assert circuit.delivered_concentration_percent == 0.0


@pytest.mark.parametrize(
    ("agent", "mac_percent"), [("sevoflurane", 2.0), ("isoflurane", 1.2), ("desflurane", 6.0)]
)
def test_a_run_opens_with_its_dial_built_as_a_setting_not_as_the_mac(
    agent: str, mac_percent: float
) -> None:
    """The opening dial is at 1 MAC, but it is a dial setting and not the agent's MAC.

    When the opening setting was built from the agent's `MacPercent` itself,
    it passed a MAC check until the learner first moved the dial. So a dial
    setting passed to a formatter in place of the MAC showed a correct-looking
    1.00 ×MAC when the run opened, and failed only later, mid-run (`PL-F9TC`,
    blind review). The expected MACs are the values in the shipped data files,
    typed out here by hand.
    """
    dial = AgentUptakeSystem.for_agent(agent).circuit.delivered_concentration_percent

    assert type(dial) is Percent
    assert dial == mac_percent
    with pytest.raises(TypeError, match="was not built as MacPercent"):
        require_mac_percent("mac_percent", dial)
