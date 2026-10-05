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
from dataclasses import replace
from math import inf, nan, nextafter

import pytest

from anesthesia_sim.core.circuit import BreathingCircuit, BreathingCircuitState
from anesthesia_sim.core.concentration import (
    PERCENT_PER_UNIT_FRACTION,
    Fraction,
    Percent,
    fraction_from_percent,
    percent_from_fraction,
)
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.parameters import load_sevoflurane_parameters
from anesthesia_sim.core.simulation_step import SimulationStep
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
    """A state copied for a branch, or saved, keeps a value still of its type.

    A copy, a deep copy and a pickle at the default protocol each rebuild
    through the constructor rather than around it, which the test below pins
    for the pickle. A pickle at protocol 0 or 1 does not, which `PL-5D1Z`
    records for every checked type.
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

    with pytest.raises(TypeError, match="^inspired_partial_pressure_fraction of 0.0 was not built"):
        system.circuit.set_inspired_partial_pressure_fraction(0.0)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="^delivered_concentration_percent of 2.0 was not built"):
        system.circuit.set_delivered_concentration_percent(2.0)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="^alveolar partial_pressure_fraction of 0.0 was not built"):
        system.alveoli.set_partial_pressure_fraction(0.0)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="^venous partial_pressure_fraction of 0.0 was not built"):
        venous.set_partial_pressure_fraction(0.0)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="^fat partial_pressure_fraction of 0.0 was not built"):
        fat.set_partial_pressure_fraction(0.0)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="^tissue_return_partial_pressure_fraction of 0.0 was"):
        venous.advance(0.0, step)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="^arterial_partial_pressure_fraction of 0.0 was not"):
        fat.advance(0.0, step)  # type: ignore[arg-type]

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
