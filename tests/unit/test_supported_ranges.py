"""The declared input domain, and what happens at and outside its edges.

This module is regression cover for PL-0MLQ. `docs/MODEL.md` declared a
closed supported interval for each control, but only the interval for the
delivered concentration was enforced. `AgentUptakeSystem.set_cardiac_output(1000.0)`
was accepted and simulated. The interface's sliders were the only thing that
kept a run inside the domain that the verification gates cover.

Since `PL-0YYV`, each flow is a type: `FreshGasFlow`, `AlveolarVentilation`
and `CardiacOutput`. Each type can be built only through its guard, and every
field that stores a flow takes the type. The tests under "Each flow is a type"
check that the type accepts and rejects exactly what its guard does, and that
it keeps the value it was built from. They check that the type is required
wherever a flow is stored. Since `PL-LBQY`, that includes the write to the
compartment's field itself, whoever makes the write. Since `PL-LLMN`, they
also check that a flow is built from a number and nothing else, and that it
stores minus zero as zero. Since `PL-CN5S`, the case instant and the step
count are types too, `CaseInstant` and `StepCount`. The tests under "The case
instant and the step count are types" check them in the same way. Since
`PL-SZ6G`, those tests also check that the instant is built from an `int`
and nothing else, as the count is.

The endpoints are tested as carefully as the rejections. Every range is
closed, and both ends matter. One reference gate trajectory keeps cardiac
output at zero for its loading phase. The envelope corner that every reference
gate drives sits on all three maxima at once. A guard that quietly excluded an
endpoint would take a measured case out of the reachable domain without
failing anything.
"""

import copy
import pickle
import sys
from collections.abc import Callable
from dataclasses import replace
from decimal import Decimal
from math import inf, nan, nextafter
from typing import NamedTuple

import numpy
import pytest

from anesthesia_sim.app.formatting import format_flow
from anesthesia_sim.core.circuit import BreathingCircuit, DeliverableFreshGasFlowRange
from anesthesia_sim.core.concentration import Fraction, Percent
from anesthesia_sim.core.exceptions import (
    SimulationConfigurationError,
    SimulationDomainLimitError,
    SimulationExecutionError,
)
from anesthesia_sim.core.numerical_envelope import CompartmentVolume
from anesthesia_sim.core.simulation import SimulationState
from anesthesia_sim.core.simulation_step import SIMULATION_STEP_S
from anesthesia_sim.core.supported_ranges import (
    MAXIMUM_ALVEOLAR_VENTILATION_L_MIN,
    MAXIMUM_CARDIAC_OUTPUT_L_MIN,
    MAXIMUM_ELAPSED_SIMULATION_TIME_S,
    MAXIMUM_FRESH_GAS_FLOW_L_MIN,
    MAXIMUM_INPUT_FRACTION,
    MAXIMUM_STEP_COUNT,
    MINIMUM_ALVEOLAR_VENTILATION_L_MIN,
    MINIMUM_CARDIAC_OUTPUT_L_MIN,
    MINIMUM_FRESH_GAS_FLOW_L_MIN,
    AlveolarVentilation,
    CardiacOutput,
    CaseInstant,
    FreshGasFlow,
    StepCount,
    describe_count,
    require_alveolar_ventilation,
    require_cardiac_output,
    require_case_instant,
    require_fresh_gas_flow,
    require_held_within_input_ceiling,
    require_step_count,
    require_supported_alveolar_ventilation,
    require_supported_cardiac_output,
    require_supported_case_instant,
    require_supported_fresh_gas_flow,
    require_supported_run_length,
    require_supported_step_count,
    require_within_input_ceiling,
)
from anesthesia_sim.core.uptake_system import AgentUptakeSystem


class Control(NamedTuple):
    """One control, as the tests in this module need it.

    The record holds the control's guard, the type that only that guard
    builds, the closed interval that the guard declares, and the compartment
    of `AgentUptakeSystem` that stores the control.
    """

    name: str
    guard: Callable[[float], None]
    flow_type: type[float]
    minimum: float
    maximum: float
    stored_on: str


CONTROLS = (
    Control(
        "fresh_gas_flow_l_min",
        require_supported_fresh_gas_flow,
        FreshGasFlow,
        MINIMUM_FRESH_GAS_FLOW_L_MIN,
        MAXIMUM_FRESH_GAS_FLOW_L_MIN,
        "circuit",
    ),
    Control(
        "alveolar_ventilation_l_min",
        require_supported_alveolar_ventilation,
        AlveolarVentilation,
        MINIMUM_ALVEOLAR_VENTILATION_L_MIN,
        MAXIMUM_ALVEOLAR_VENTILATION_L_MIN,
        "alveoli",
    ),
    Control(
        "cardiac_output_l_min",
        require_supported_cardiac_output,
        CardiacOutput,
        MINIMUM_CARDIAC_OUTPUT_L_MIN,
        MAXIMUM_CARDIAC_OUTPUT_L_MIN,
        "patient",
    ),
)

CONTROL_IDS = [control.name for control in CONTROLS]


@pytest.mark.parametrize("control", CONTROLS, ids=CONTROL_IDS)
def test_accepts_both_endpoints_and_the_interior(control: Control) -> None:
    """The interval is closed, and the endpoints are the measured cases."""

    midpoint = (control.minimum + control.maximum) / 2.0

    for value in (control.minimum, midpoint, control.maximum):
        control.guard(value)


@pytest.mark.parametrize("control", CONTROLS, ids=CONTROL_IDS)
def test_rejects_the_smallest_value_above_the_maximum(control: Control) -> None:
    """The guard rejects every value from the first float above the maximum.

    A guard written with `>=` instead of `>` would pass every other test in
    this module. It would also make the envelope corner unreachable. The
    envelope corner is the operating point at which the exact-step reference
    gate measures.
    """

    with pytest.raises(SimulationConfigurationError):
        control.guard(nextafter(control.maximum, inf))


@pytest.mark.parametrize("control", CONTROLS, ids=CONTROL_IDS)
@pytest.mark.parametrize("scale", (2.0, 10.0, 100.0))
def test_rejects_a_flow_far_outside_the_domain(control: Control, scale: float) -> None:
    with pytest.raises(SimulationConfigurationError):
        control.guard(control.maximum * scale)


@pytest.mark.parametrize("control", CONTROLS, ids=CONTROL_IDS)
@pytest.mark.parametrize("value", (-1.0, -0.0001, nan, inf, -inf))
def test_rejects_a_value_that_is_negative_or_not_finite(control: Control, value: float) -> None:
    """One guard covers the whole domain, so NaN cannot slip past a comparison.

    `nan` compares false against every bound. A range check written as two
    comparisons and nothing else would accept it. The NaN would then silently
    poison every downstream state.
    """

    with pytest.raises(SimulationConfigurationError):
        control.guard(value)


@pytest.mark.parametrize("control", CONTROLS, ids=CONTROL_IDS)
def test_the_refusal_names_the_setting_the_value_and_the_interval(control: Control) -> None:
    """A refusal that a caller cannot act on is barely better than a wrong number."""

    rejected = control.maximum * 10.0

    with pytest.raises(SimulationConfigurationError) as raised:
        control.guard(rejected)

    message = str(raised.value)

    assert control.name in message
    assert str(rejected) in message
    assert f"{control.minimum} to {control.maximum} L/min" in message


# --- Each flow is a type, built only through its guard (PL-0YYV) ------------
#
# The guard above runs once, where a flow is built as its type. Every field and
# signature past that point takes the type, so the check is made nowhere else.
# That design is only as good as the type. The type has to keep the value it was
# built from exactly, and refuse in the guard's own words. It has to come back
# from a copy as itself. It has to be required wherever a bare float could
# otherwise be stored in its place.


@pytest.mark.parametrize("control", CONTROLS, ids=CONTROL_IDS)
def test_the_type_holds_the_value_it_was_built_from_exactly(control: Control) -> None:
    """At either end and between, the type keeps the float it was given, bit for bit.

    A type that rounded or re-derived its value would move the envelope corner
    at which the reference gates measure. `hex` compares the bits rather than
    the printed digits. Two of the values carry a full mantissa. Rounding to
    any number of decimals would leave the endpoints where they are, so only
    values like these can show that the type rounds.
    """

    midpoint = (control.minimum + control.maximum) / 2.0
    full_mantissa = (nextafter(control.maximum, -inf), control.maximum / 3.0)

    for value in (control.minimum, midpoint, control.maximum, *full_mantissa):
        built = control.flow_type(value)

        assert isinstance(built, control.flow_type)
        assert isinstance(built, float)
        assert built.hex() == float(value).hex()


@pytest.mark.parametrize("control", CONTROLS, ids=CONTROL_IDS)
def test_the_type_refuses_what_its_guard_refuses_in_the_guards_words(control: Control) -> None:
    """The type and its guard share one check, so they reject the same values in the same words."""

    for value in (nextafter(control.maximum, inf), control.maximum * 10.0, -1.0, nan, inf, -inf):
        with pytest.raises(SimulationConfigurationError) as by_the_guard:
            control.guard(value)

        with pytest.raises(SimulationConfigurationError) as by_the_type:
            control.flow_type(value)

        assert str(by_the_type.value) == str(by_the_guard.value)


@pytest.mark.parametrize("control", CONTROLS, ids=CONTROL_IDS)
def test_arithmetic_on_a_flow_is_a_plain_float(control: Control) -> None:
    """A quantity derived from a flow is not a checked flow, and must not look like one.

    Two flows at the maximum sum to a value above the maximum. If the sum were
    still the type, it would promise a check that never ran. A subclass of
    `float` returns `float` from every operator, so the promise applies only
    to what was actually built.
    """

    at_maximum = control.flow_type(control.maximum)

    assert type(at_maximum + at_maximum) is float
    assert type(at_maximum / 60.0) is float
    assert type(-at_maximum) is float


@pytest.mark.parametrize("control", CONTROLS, ids=CONTROL_IDS)
def test_a_flow_survives_copy_and_pickle_as_its_type(control: Control) -> None:
    """A copied or stored record keeps its flows as checked types, not plain floats.

    `dataclasses.replace` copies the fields it is not given, and a saved run
    would come back through `pickle`. Each of these rebuilds the flow through
    the type's own constructor, so the guard runs again and the type is kept.
    """

    built = control.flow_type(control.maximum)

    for copied in (copy.copy(built), copy.deepcopy(built), pickle.loads(pickle.dumps(built))):
        assert type(copied) is control.flow_type
        assert copied == built


@pytest.mark.parametrize("control", CONTROLS, ids=CONTROL_IDS)
def test_a_bare_float_is_refused_wherever_a_flow_is_stored(control: Control) -> None:
    """A float that was never built as the type is refused where it would be stored.

    This holds whether or not the float is in range. The static half of the
    check is the annotation. A caller outside `mypy`'s reach, such as a
    notebook, a test or a deserializer, never sees the annotation. The runtime
    half lives where a flow is stored: the compartment's setter, its
    constructor, and the settings record. Each of them refuses a bare float and
    names the type to build. The forwarding setter on `AgentUptakeSystem` leads
    to the same refusal. The test uses the value the compartment already
    stores, so what is refused is the missing check and not the number.
    Nothing changes when the value is refused.
    """

    system = AgentUptakeSystem.default()
    compartment = getattr(system, control.stored_on)
    setter = f"set_{control.name.removesuffix('_l_min')}"
    held = getattr(compartment, control.name)
    bare = float(held)
    refused = f"not built as {control.flow_type.__name__}"

    assert type(held) is control.flow_type

    with pytest.raises(TypeError) as raised:
        getattr(compartment, setter)(bare)

    assert str(raised.value) == (
        f"{control.name} of {bare!r} was not built as {control.flow_type.__name__}, it is "
        f"float: build it as {control.flow_type.__name__}(...) where it is set, which checks "
        'it against the supported range once (docs/INTERFACE.md, "Supported input ranges")'
    )

    with pytest.raises(TypeError, match=refused):
        getattr(system, setter)(bare)

    with pytest.raises(TypeError, match=refused):
        replace(compartment, **{control.name: bare})

    with pytest.raises(TypeError, match=refused):
        replace(system.equation_settings(), **{control.name: bare})

    assert getattr(compartment, control.name) is held


@pytest.mark.parametrize("control", CONTROLS, ids=CONTROL_IDS)
def test_another_flows_type_is_refused_as_a_swapped_argument(control: Control) -> None:
    """The refusal names a flow of another type by that type, and prescribes no rebuild.

    A fresh gas flow that arrives where a cardiac output belongs is a swapped
    argument. A refusal that prescribed `CardiacOutput(4.0)` would have the
    caller check and store the wrong quantity under the right type. So the
    message names the type that the value was built as, and prescribes nothing.
    """

    system = AgentUptakeSystem.default()
    compartment = getattr(system, control.stored_on)
    setter = getattr(compartment, f"set_{control.name.removesuffix('_l_min')}")
    held = getattr(compartment, control.name)
    other = next(each for each in CONTROLS if each.flow_type is not control.flow_type)

    with pytest.raises(TypeError) as raised:
        setter(other.flow_type(float(held)))

    message = str(raised.value)

    assert f"was built as {other.flow_type.__name__}" in message
    assert f"{control.flow_type.__name__}(" not in message
    assert getattr(compartment, control.name) is held


@pytest.mark.parametrize("control", CONTROLS, ids=CONTROL_IDS)
@pytest.mark.parametrize(
    "other",
    [StepCount(600), CaseInstant(600), Fraction(0.5), Percent(2.0)],
    ids=lambda other: type(other).__name__,
)
def test_a_count_or_an_instant_handed_in_as_a_flow_is_refused_as_a_swapped_argument(
    control: Control, other: object
) -> None:
    """The refusal names what the value was built as, and does not say to rebuild it as this flow.

    Until `PL-848D`, `_require_built` named only the other two flows. So a
    `StepCount(5)` handed in as a fresh gas flow was told to build
    `FreshGasFlow(...)` from it. That is the rebuild that the flows' refusal of
    each other exists to prevent. Every checked quantity now shares one record
    (`core/checked_number.py`). So a count, an instant and both forms of a
    concentration are refused in the same words as the other flows, and
    nothing is written.
    """

    system = AgentUptakeSystem.default()
    compartment = getattr(system, control.stored_on)
    setter = getattr(compartment, f"set_{control.name.removesuffix('_l_min')}")
    held = getattr(compartment, control.name)

    with pytest.raises(TypeError) as raised:
        setter(other)

    assert str(raised.value) == (
        f"{control.name} of {other!r} was built as {type(other).__name__}, which is not "
        f"{control.flow_type.__name__}: it is another quantity, so build "
        f"{control.flow_type.__name__} from the value that {control.name} should hold, not "
        "from this one (core/checked_number.py)"
    )
    assert getattr(compartment, control.name) is held


NOT_A_NUMBER = (True, numpy.True_, Decimal("2.5"), Decimal("sNaN"), "2.5")
"""Values that are not numbers, and what a flow built from each did before `PL-LLMN`.

`True` and `numpy.True_` were each built as a flow of 1.0 L/min, and the
`Decimal` as a flow of 2.5 L/min. The signalling NaN escaped as
`math.isfinite`'s `ValueError`, and the string escaped as its `TypeError`.
Neither error named the setting or the range. The NumPy `bool` is here
because it is not a `bool`: a guard that refuses only `bool` accepts it.
"""


@pytest.mark.parametrize("control", CONTROLS, ids=CONTROL_IDS)
def test_the_type_refuses_what_is_not_a_number_and_holds_negative_zero_as_zero(
    control: Control,
) -> None:
    """A flow is built from an int or a float and nothing else, and has no sign at zero.

    The guard and the type both refuse each value in `NOT_A_NUMBER`, before
    any comparison reads it. The refusal is a `TypeError` in the simulator's
    words that names the setting, the value and its type. It reports a
    programming error in the caller, as `require_fresh_gas_flow` does for a
    bare float, and not a refused setting. Minus zero is the supported zero
    that arithmetic can reach with a sign. So it is stored as zero, and
    `format_flow` prints it as the flow it is, where it used to print
    `-0.0 L/min`. An `int` is accepted just as a `float` is, and both keep the
    number they were built from (`PL-LLMN`).
    """

    for value in NOT_A_NUMBER:
        for build in (control.guard, control.flow_type):
            with pytest.raises(TypeError) as raised:
                build(value)  # type: ignore[arg-type]

            message = str(raised.value)

            assert message.startswith(
                f"{control.name} of {value!r} has type {type(value).__name__}"
            )
            assert "not int or float" in message

    from_negative_zero = control.flow_type(-0.0)

    assert from_negative_zero.hex() == (0.0).hex()
    assert format_flow(from_negative_zero) == "0.0 L/min"

    for number in (1, 1.0, numpy.float64(1.0)):
        built = control.flow_type(number)

        assert type(built) is control.flow_type
        assert built.hex() == (1.0).hex()


_SUPPORTED_RANGE_SOURCE = (
    "which is the domain this compartment model is claimed to represent a patient over "
    '(docs/INTERFACE.md, "Supported input ranges")'
)


@pytest.mark.parametrize(
    ("flow_type", "refused", "expected"),
    [
        (
            FreshGasFlow,
            10.5,
            "fresh_gas_flow_l_min of 10.5 is outside the supported input range of 0.0 to "
            f"10.0 L/min, {_SUPPORTED_RANGE_SOURCE}",
        ),
        (
            AlveolarVentilation,
            12.5,
            "alveolar_ventilation_l_min of 12.5 is outside the supported input range of 0.0 "
            f"to 12.0 L/min, {_SUPPORTED_RANGE_SOURCE}",
        ),
        (
            CardiacOutput,
            -1.0,
            "cardiac_output_l_min of -1.0 is outside the supported input range of 0.0 to "
            f"10.0 L/min, {_SUPPORTED_RANGE_SOURCE}",
        ),
    ],
    ids=["fresh-gas-flow", "alveolar-ventilation", "cardiac-output"],
)
def test_a_setting_s_range_refusal_is_pinned_whole(
    flow_type: Callable[[float], float], refused: float, expected: str
) -> None:
    """The whole sentence the "Setting refused" banner shows for each flow control.

    `refused_setting_notice` prints a refusal word for word, so the sentence
    is what a learner reads. The other tests here match only a phrase of it,
    and such a match passes even when the name, the value or the interval is
    wrong (`PL-79PK`). The interval in each expected sentence is copied by
    hand from `docs/INTERFACE.md` §
    "Supported input ranges": 0 to 10 L/min of fresh gas, 0 to 12 L/min of
    alveolar ventilation and 0 to 10 L/min of cardiac output.
    """

    with pytest.raises(SimulationConfigurationError) as refusal:
        flow_type(refused)

    assert str(refusal.value) == expected


@pytest.mark.parametrize("control", CONTROLS, ids=CONTROL_IDS)
def test_an_int_past_the_float_range_is_refused_against_the_interval(control: Control) -> None:
    """An `int` too large for a `float` is outside every interval here, and is refused as such.

    `math.isfinite` raises `OverflowError` when it converts such an int. That
    is the same escape in Python's words that `PL-7N8P` records for the case
    instant. The closed interval instead compares the int exactly. An int too
    long to print is named by its length, as a refused count is (`PL-5F76`).
    """

    with pytest.raises(SimulationConfigurationError, match="is outside the supported input range"):
        control.flow_type(10**400)

    with pytest.raises(SimulationConfigurationError) as raised:
        control.guard(10**5000)

    assert f"{control.name} of <more than {sys.get_int_max_str_digits():,} digits> is" in str(
        raised.value
    )


@pytest.mark.parametrize("control", CONTROLS, ids=CONTROL_IDS)
def test_a_bare_float_written_onto_a_compartment_is_refused_at_the_write(control: Control) -> None:
    """Assigning straight to the field is a fifth way to set a flow, and meets the same refusal.

    `mypy` refuses `circuit.fresh_gas_flow_l_min = 1000.0` in `src/`, and the
    compartments' own methods write the field from a checked flow. So an
    unchecked write comes from a caller that `mypy` does not read. Until
    `PL-LBQY`, such a write was caught only when the next step rebuilt the
    settings. By then the snapshot had copied the bare float and the readout
    had shown it. The compartment's `__setattr__` now runs the flow's
    `require_*` at the write, in that function's words, and leaves the field
    holding its old value. So the settings that a snapshot is built from never
    see the bare float. A flow built as its type is written, by the setter and
    by assignment alike. The type is all that the write checks, so the setter
    alone checks its own relations, such as the machine's range and the tissue
    flows. The constructor, `dataclasses.replace`, a copy and a pickle all
    write through the same `__setattr__`. A copy and a pickle do so because the
    compartment is a `slots=True` dataclass whose state is restored one field
    at a time. So each of the four refuses a bare float smuggled past the
    guard, before the patient's `__post_init__` can touch a tissue flow.
    """

    system = AgentUptakeSystem.default()
    compartment = getattr(system, control.stored_on)
    held = getattr(compartment, control.name)
    refused = f"{control.name} of {float(held)!r} was not built as {control.flow_type.__name__}"

    with pytest.raises(TypeError, match=refused):
        setattr(compartment, control.name, float(held))

    assert getattr(compartment, control.name) is held
    assert getattr(system.equation_settings(), control.name) is held

    rebuilt = control.flow_type(float(held))
    setattr(compartment, control.name, rebuilt)

    assert getattr(compartment, control.name) is rebuilt

    with pytest.raises(
        TypeError, match=f"{control.name} of True was not built as {control.flow_type.__name__}"
    ):
        setattr(compartment, control.name, True)

    assert getattr(compartment, control.name) is rebuilt

    with pytest.raises(TypeError, match=refused):
        replace(compartment, **{control.name: float(held)})

    smuggled = copy.copy(compartment)
    object.__setattr__(smuggled, control.name, float(held))

    with pytest.raises(TypeError, match=refused):
        copy.copy(smuggled)

    with pytest.raises(TypeError, match=refused):
        pickle.loads(pickle.dumps(smuggled))


def test_a_cardiac_output_written_past_set_cardiac_output_is_refused_at_the_write() -> None:
    """A new cardiac output written straight to the field is refused, not stored.

    The test above checks the type of every flow at the write. Before
    `PL-KFNP`, the type was all that the patient's write checked. So a
    `CardiacOutput(6.0)` assigned past `set_cardiac_output` was stored, while
    every stored flow stayed at its share of 5.0. Since `PL-HQF5`, no
    compartment stores a flow. The refusal is kept so that the setter remains
    the one way to change the output. The message names the refused output,
    the output the patient keeps, and `set_cardiac_output`. The field and the
    settings record keep their values, and the run can still step. The check
    is on the value, so writing the output that the patient already holds is
    accepted. The field and the setter both refuse a wrong type before
    anything changes. The setter moves every flow. The expected flows are the
    reference adult's fractions (0.76, 0.18 and 0.06, copied by hand from
    `data/patients/reference_adult.json`) times 10.0 L/min, worked out here.
    The constructor, `dataclasses.replace`, a copy and a pickle each build a
    patient at the output written (`PL-KFNP`).
    """

    system = AgentUptakeSystem.default()
    patient = system.patient
    held = patient.cardiac_output_l_min
    settings = system.equation_settings()

    with pytest.raises(SimulationConfigurationError) as raised:
        patient.cardiac_output_l_min = CardiacOutput(6.0)

    assert str(raised.value) == (
        "a cardiac output of 6.0 L/min written straight onto the patient was refused. The "
        "patient keeps its cardiac output of 5.0 L/min. Change the output with "
        "set_cardiac_output, the one way a cardiac output is changed "
        '(docs/INTERFACE.md, "Supported input ranges")'
    )
    assert patient.cardiac_output_l_min is held
    assert system.equation_settings() == settings
    system.advance()

    with pytest.raises(SimulationConfigurationError, match="written straight onto the patient"):
        patient.cardiac_output_l_min = CardiacOutput(nextafter(float(held), inf))

    rewritten = CardiacOutput(float(held))
    patient.cardiac_output_l_min = rewritten

    assert patient.cardiac_output_l_min is rewritten

    with pytest.raises(TypeError, match="not built as CardiacOutput"):
        patient.cardiac_output_l_min = 6.0  # type: ignore[assignment]

    with pytest.raises(TypeError, match="not built as CardiacOutput"):
        patient.set_cardiac_output(10.0)  # type: ignore[arg-type]

    assert patient.cardiac_output_l_min is rewritten

    patient.set_cardiac_output(CardiacOutput(10.0))

    assert patient.cardiac_output_l_min == 10.0
    assert [
        tissue.blood_flow_l_min for tissue in system.equation_settings().tissues
    ] == pytest.approx([7.6, 1.8, 0.6], abs=1e-12)

    for built in (
        replace(patient),
        copy.copy(patient),
        copy.deepcopy(patient),
        pickle.loads(pickle.dumps(patient)),
    ):
        assert built.cardiac_output_l_min == 10.0
        assert [
            tissue.blood_flow_l_min_at(built.cardiac_output_l_min) for tissue in built.tissues
        ] == pytest.approx([7.6, 1.8, 0.6], abs=1e-12)


# --- The supported run length (PL-Y5WR) -------------------------------------
#
# This is the fifth bound, and the only one on the run rather than on a
# setting. It is regression cover for a limit that was declared in conversation
# on 2026-08-25, recorded in a dropped item, and enforced nowhere. A run could
# reach day 45 of a cap set at 30 days and go on displaying two-decimal
# concentrations, in a regime over which `docs/MODEL.md` already declines to
# validate the model.
#
# The boundary is pinned in both directions on purpose. A guard that refused
# one step early would take the endpoint out of the closed interval, although
# every other range in this module includes its endpoints. A guard that
# refused one step late would let a run display a state outside the declared
# domain, which is the defect itself.


def test_the_supported_run_length_is_twenty_four_hours() -> None:
    """The declared number, pinned so a silent edit fails rather than ships.

    `docs/INTERFACE.md` § "Supported run length" argues for this value from what
    the model omits, and `core/supported_ranges.py` carries the argument and
    its source. Changing the value is a safety-critical change, and this test
    catches a change made by accident.

    This is the one test meant to fail when the number changes. The tests that
    check text or counts derived from the limit read
    `MAXIMUM_ELAPSED_SIMULATION_TIME_S` rather than restating it (`PL-T5J5`).
    So a deliberate change edits the constant, this test and that section of
    `docs/MODEL.md`.
    """

    assert MAXIMUM_ELAPSED_SIMULATION_TIME_S == 86_400
    assert type(MAXIMUM_ELAPSED_SIMULATION_TIME_S) is int
    assert MAXIMUM_ELAPSED_SIMULATION_TIME_S / 3600 == 24.0


def test_the_last_step_a_run_may_take_lands_on_the_boundary_exactly() -> None:
    """The span is a whole number of one-second steps, and the last one lands on its end.

    A learner watching a run to its limit therefore reads the limit itself. A
    count one step to either side lands one second away, so this test pins
    the count as well. The count is whole, so no rounding decides where the
    last step lands. Until `PL-SZ6G` the count was worked out from a float
    step, and a quotient put it one step to either side of the span at some
    steps (`PL-8H2R`).
    """

    assert type(MAXIMUM_STEP_COUNT) is int
    assert MAXIMUM_STEP_COUNT * SIMULATION_STEP_S == MAXIMUM_ELAPSED_SIMULATION_TIME_S


def test_a_run_may_complete_the_step_that_reaches_the_boundary() -> None:
    """The interval is closed, like the three flow ranges above it."""

    require_supported_run_length(StepCount(MAXIMUM_STEP_COUNT - 1))


def test_the_step_that_would_cross_the_boundary_is_refused() -> None:
    """When a run stands exactly on the limit, the next step is the one refused."""

    with pytest.raises(SimulationDomainLimitError):
        require_supported_run_length(StepCount(MAXIMUM_STEP_COUNT))


def test_a_run_already_past_the_boundary_is_refused_too() -> None:
    """A count beyond the limit is refused too, not only a count equal to it.

    The guard uses `>=` rather than `==`, so a count past the boundary cannot
    keep stepping just because it never met the boundary exactly. A
    `SimulationState` can no longer be built at such a count, because
    `require_supported_step_count` refuses it first (`PL-BMY5`). So on that
    path this guard is the second guard, not the only one.
    """

    with pytest.raises(SimulationDomainLimitError):
        require_supported_run_length(StepCount(MAXIMUM_STEP_COUNT + 500))


def test_the_run_length_refusal_says_what_was_reached_and_why() -> None:
    """A boundary given without a reason looks like an arbitrary restriction.

    The message carries the time reached, the limit, and where the limit is
    argued. It carries them for the same reason that the flow refusals carry
    theirs. A reader who cannot trace a refusal to the domain it protects
    cannot tell a modelling limit from a bug.
    """

    with pytest.raises(SimulationDomainLimitError) as raised:
        require_supported_run_length(StepCount(MAXIMUM_STEP_COUNT))

    message = str(raised.value)

    assert f"reached {MAXIMUM_ELAPSED_SIMULATION_TIME_S} s of simulated time" in message
    assert f"{MAXIMUM_ELAPSED_SIMULATION_TIME_S:g} s" in message
    assert f"({MAXIMUM_ELAPSED_SIMULATION_TIME_S / 3600:g} h)" in message
    assert "leaves out metabolism" in message
    assert "fat flow is uncertain" in message
    assert "grows as a run goes on" in message
    assert "not claimed to represent a patient past this length" in message
    assert "dominate" not in message
    assert "validated" not in message
    assert "Supported run length" in message


def test_the_run_length_refusal_is_not_a_configuration_error() -> None:
    """Nothing handed in was wrong, so "correct it and carry on" is not offered.

    The interface uses the exception's type to decide whether to tell a reader
    that the simulator broke. So the type is part of the displayed output
    rather than an implementation detail (`docs/INTERFACE.md`, "Supported run
    length").
    """

    with pytest.raises(SimulationDomainLimitError) as raised:
        require_supported_run_length(StepCount(MAXIMUM_STEP_COUNT))

    assert not isinstance(raised.value, SimulationConfigurationError)
    assert isinstance(raised.value, SimulationExecutionError)


# --- A point on the span handed in rather than reached (PL-BMY5, PL-73ZN) ---
#
# A branch is built where its parent stood: a `SimulationState` at the parent's
# step count, and a `RunDefinition` that opens at one of the parent's
# keyframes. Those are values that a caller passes, so they are refused as
# configuration errors. The step-count guard has to agree with the step's
# guard about where the span ends. Otherwise a branch taken where its parent
# stopped would be refused, or a branch that no run could reach would be
# accepted.


def test_a_run_may_be_built_where_stepping_stops_it_and_no_further() -> None:
    """The count a run stops on is legal to stand on and illegal to step from.

    Both guards read `MAXIMUM_STEP_COUNT`, so they agree. Where the count
    falls is the next test's question. This test asks only that the two count
    guards agree.
    """

    limit = MAXIMUM_STEP_COUNT

    require_supported_run_length(StepCount(limit - 1))
    require_supported_step_count(StepCount(limit))

    with pytest.raises(SimulationDomainLimitError):
        require_supported_run_length(StepCount(limit))

    with pytest.raises(SimulationConfigurationError, match="supported run length"):
        require_supported_step_count(StepCount(limit + 1))


def _accepted(guard: Callable[[], None]) -> bool:
    try:
        guard()
    except SimulationConfigurationError:
        return False

    return True


@pytest.mark.parametrize("steps_past_the_limit", [-1, 0, 1])
def test_the_step_count_and_the_case_instant_bound_the_same_span(steps_past_the_limit: int) -> None:
    """The count guard accepts a count exactly where the instant guard accepts its instant.

    A branch at a bookmark is built from its parent's step count, and a branch
    at a control event is built from its parent's instant. So the two guards
    have to put the end of the span in the same place. Otherwise the same fork
    would be built one way and refused the other. Until `PL-SZ6G` the step was
    a `float`, and at a step that did not divide the span the two guards
    disagreed by one step (`PL-8H2R`).
    """

    step_count = MAXIMUM_STEP_COUNT + steps_past_the_limit

    by_count = _accepted(lambda: require_supported_step_count(StepCount(step_count)))
    by_instant = _accepted(lambda: require_supported_case_instant(step_count * SIMULATION_STEP_S))

    assert by_count == by_instant
    assert by_count == (steps_past_the_limit <= 0)


def test_the_step_count_refusal_names_the_count_the_step_and_the_limit() -> None:
    """The refusal gives the count handed in beside the largest count allowed.

    It names the one-second step, so a reader knows what each count measures.
    The limit is read from its constant, which
    `test_the_supported_run_length_is_twenty_four_hours` pins.
    """

    limit = MAXIMUM_STEP_COUNT

    with pytest.raises(SimulationConfigurationError) as raised:
        require_supported_step_count(StepCount(limit + 1))

    message = str(raised.value)

    assert f"{limit + 1} steps of 1 s" in message
    assert f"at most {limit}" in message
    assert f"{MAXIMUM_ELAPSED_SIMULATION_TIME_S:g} s" in message
    assert f"({MAXIMUM_ELAPSED_SIMULATION_TIME_S / 3600:g} h)" in message
    assert "Supported run length" in message


def test_a_step_count_too_long_to_print_is_refused() -> None:
    """The count is refused with the simulator's own error, and named by its length (`PL-5F76`).

    CPython will not print an integer longer than `sys.get_int_max_str_digits`
    digits. So a refusal that printed the count raised `ValueError` while the
    message was being written. The run-length refusal, which then multiplied
    the count by a `float` step, raised `OverflowError`. Either error escaped
    the simulator's exceptions, where every guard here promises one of its own.
    """

    too_long = 10**5000
    named = f"<more than {sys.get_int_max_str_digits():,} digits>"

    with pytest.raises(SimulationConfigurationError) as past_the_span:
        SimulationState(step_count=StepCount(too_long))

    with pytest.raises(SimulationConfigurationError) as negative:
        StepCount(-too_long)

    with pytest.raises(SimulationDomainLimitError) as stepped_from:
        require_supported_run_length(StepCount(too_long))

    assert f"a run of {named} steps of 1 s" in str(past_the_span.value)
    assert f"not -{named}" in str(negative.value)
    assert f"reached {named} s of simulated time" in str(stepped_from.value)


def test_a_count_too_long_to_print_is_named_when_it_was_not_built_as_one() -> None:
    """The type refusals name a bare count the way the range refusals do (`PL-CN5S`).

    Each type refusal prints the value it was given. Without `shown`, a bare
    count longer than `sys.get_int_max_str_digits` digits would raise
    `ValueError` while the `TypeError` was being written. `PL-5F76` closed
    that escape for the count, and `PL-CN5S` never opened it for the instant.
    `PL-848D` closed it for the three flows, which printed with `repr` until
    then.
    """

    too_long = 10**5000
    named = f"<more than {sys.get_int_max_str_digits():,} digits>"

    with pytest.raises(TypeError) as as_a_count:
        require_step_count(too_long)

    with pytest.raises(TypeError) as as_an_instant:
        require_case_instant("instant_s", too_long)

    assert f"step_count of {named} was not built as StepCount, it is int" in str(as_a_count.value)
    assert f"instant_s of {named} was not built as CaseInstant, it is int" in str(
        as_an_instant.value
    )

    for control, require_built in zip(
        CONTROLS,
        (require_fresh_gas_flow, require_alveolar_ventilation, require_cardiac_output),
        strict=True,
    ):
        with pytest.raises(TypeError) as as_a_flow:
            require_built(too_long)

        expected = f"{control.name} of {named} was not built as {control.flow_type.__name__}"

        assert expected in str(as_a_flow.value)


@pytest.mark.parametrize("instant_s", [0, 3_600, MAXIMUM_ELAPSED_SIMULATION_TIME_S])
def test_a_case_instant_is_supported_over_the_closed_span(instant_s: int) -> None:
    """Both ends are included, like every interval here, so a run may stand on the far end."""

    require_supported_case_instant(instant_s)


INSTANTS_OUTSIDE_THE_SPAN = (
    MAXIMUM_ELAPSED_SIMULATION_TIME_S + 1,
    MAXIMUM_ELAPSED_SIMULATION_TIME_S + 3_600,
    -1,
    -3_600,
    10**400,
    -(10**400),
)
"""Whole seconds outside the span: the first one past each end, and others further out.

`10**400` is an `int` too large for a `float`. The guard compares it exactly,
as an `int`, and refuses it against the run length as it refuses any other.
"""

FLOAT_INSTANTS = (
    0.0,
    -0.0,
    2.0,
    2.5,
    3_600.0,
    float(MAXIMUM_ELAPSED_SIMULATION_TIME_S),
    nextafter(MAXIMUM_ELAPSED_SIMULATION_TIME_S, inf),
    nextafter(0.0, -inf),
    -1.0,
    nan,
    inf,
    -inf,
    numpy.float64(1.0),
)
"""Floats that an instant is never built from, inside the span, at its edges and outside it.

Each was either accepted or refused against the run length while an instant
was a `float`. `0.0`, `2.0`, `3_600.0` and the run length itself are whole and
inside the span. `-0.0` was stored as zero. The two `nextafter` values are the
first floats outside each end. `nan` fails every comparison.
"""


@pytest.mark.parametrize("instant_s", INSTANTS_OUTSIDE_THE_SPAN, ids=describe_count)
def test_a_case_instant_outside_the_span_is_refused(instant_s: int) -> None:
    """A whole second outside the span is refused on either side, as a refused setting is.

    The first second past the far end and the first second before induction
    are both refused, so the interval is closed exactly at 0 and at the run
    length. One expression refuses every case with one message, as
    `_require_supported` does for the flows.
    """

    with pytest.raises(SimulationConfigurationError, match="supported run length"):
        require_supported_case_instant(instant_s)


@pytest.mark.parametrize("instant_s", FLOAT_INSTANTS, ids=repr)
def test_a_float_is_refused_as_a_case_instant_whatever_it_holds(instant_s: float) -> None:
    """An instant is an `int`, so a `float` is refused before its value is read (`PL-SZ6G`).

    A run moves only by the one-second step, so every instant that it reaches
    is a whole number of seconds. `2.0` is whole and is refused all the same,
    because a `float` handed in is a sign that something computed the instant
    by arithmetic that can round. The refusal is a `TypeError`, as when a
    count refuses a `float`. It is a programming error in the caller, not a
    refused setting. So a float outside the span, `nan` and an infinity meet
    the same refusal as a float inside it, and none of them reaches the
    comparison with the run length. Minus zero has no stored form, because it
    is a `float` too.
    """

    for build in (require_supported_case_instant, CaseInstant):
        with pytest.raises(TypeError) as raised:
            build(instant_s)  # type: ignore[arg-type]

        assert str(raised.value) == (
            f"instant_s of {instant_s!r} has type {type(instant_s).__name__}, not int: an "
            "instant of the case is a whole number of seconds, because a run moves only by "
            "the 1 s step (core/simulation_step.py)"
        )


def test_the_case_instant_refusal_names_the_instant_and_the_span() -> None:
    """The whole sentence is pinned, with the instant printed as it was handed in.

    The span in the expected sentence is 0 to 86 400 s, which is 24 hours. It
    is read from the constant that
    `test_the_supported_run_length_is_twenty_four_hours` pins.
    """

    past = MAXIMUM_ELAPSED_SIMULATION_TIME_S + 1

    with pytest.raises(SimulationConfigurationError) as raised:
        require_supported_case_instant(past)

    assert str(raised.value) == (
        f"a case instant of {past} s is outside the supported run length of 0 to "
        f"{MAXIMUM_ELAPSED_SIMULATION_TIME_S} s "
        f"({MAXIMUM_ELAPSED_SIMULATION_TIME_S // 3600} h), the span this model is claimed to "
        'represent a patient over (docs/INTERFACE.md, "Supported run length")'
    )


# --- The case instant and the step count are types (PL-CN5S) ----------------
#
# These types work as each flow does above. The instant is checked against the
# span once, where it is built as a `CaseInstant`. The count is checked once,
# where it is built as a `StepCount`, for what a count can be checked for on
# its own: that it is whole and nonnegative. How many steps a run may complete
# is the run's limit, so that half of the check stays with the record that
# holds the run's clock, `SimulationState`. Each type keeps what it was built
# from, refuses in its check's own words, and comes back from a copy as itself.
# The test modules of the records that store these types check that each
# record refuses a value that was never built as the type.


@pytest.mark.parametrize(
    "instant_s",
    [
        0,
        1,
        3_600,
        MAXIMUM_ELAPSED_SIMULATION_TIME_S // 3,
        MAXIMUM_ELAPSED_SIMULATION_TIME_S - 1,
        MAXIMUM_ELAPSED_SIMULATION_TIME_S,
    ],
)
def test_a_case_instant_is_the_instant_it_was_built_from_exactly(instant_s: int) -> None:
    """An instant keeps the whole second it was built from, at the span's ends and between."""

    built = CaseInstant(instant_s)

    assert type(built) is CaseInstant
    assert isinstance(built, int)
    assert int(built) == instant_s
    assert str(built) == str(instant_s)


def test_a_case_instant_refuses_what_its_guard_refuses_in_the_guards_words() -> None:
    """The type and its guard share one check, so they reject the same values in the same words."""

    for instant_s in INSTANTS_OUTSIDE_THE_SPAN:
        with pytest.raises(SimulationConfigurationError) as by_the_guard:
            require_supported_case_instant(instant_s)

        with pytest.raises(SimulationConfigurationError) as by_the_type:
            CaseInstant(instant_s)

        assert str(by_the_type.value) == str(by_the_guard.value)


def test_a_case_instant_refuses_what_is_not_an_int_and_names_an_overflowing_int() -> None:
    """An instant is built from an `int` and nothing else, in the simulator's own words.

    The guard and the type both refuse each value in `NOT_A_NUMBER`, before
    any comparison reads it. The refusal is a `TypeError` in the simulator's
    words that names the value and its type, as the count's refusal does
    (`PL-LLMN`). Until `PL-7N8P`, `True` and `numpy.True_` were each an
    instant of 1 s on the case's axis, and `Decimal('2.5')` was an instant of
    2.5 s. The string and the signalling NaN escaped in `math.isfinite`'s
    words. A NumPy integer is not an `int`, so it is refused with them. An
    `int` past the float range is compared exactly and refused against the
    run length, in the same words as any other instant outside it. An int too
    long to print is named by its length, as a refused count is (`PL-5F76`).
    Zero has one form, the `int`, and an instant built from the `int` 1 holds
    1.
    """

    for value in (*NOT_A_NUMBER, numpy.int64(1), None):
        for build in (require_supported_case_instant, CaseInstant):
            with pytest.raises(TypeError) as raised:
                build(value)  # type: ignore[arg-type]

            message = str(raised.value)

            assert message.startswith(
                f"instant_s of {value!r} has type {type(value).__name__}, not int: "
            )

    with pytest.raises(SimulationConfigurationError, match="supported run length") as by_the_type:
        CaseInstant(10**400)

    with pytest.raises(SimulationConfigurationError) as by_the_guard:
        require_supported_case_instant(10**400)

    assert str(by_the_type.value) == str(by_the_guard.value)
    assert f"a case instant of {10**400} s is outside the supported run length" in str(
        by_the_guard.value
    )

    with pytest.raises(SimulationConfigurationError) as too_long:
        require_supported_case_instant(10**5000)

    assert (
        f"a case instant of <more than {sys.get_int_max_str_digits():,} digits> s is outside"
        in str(too_long.value)
    )

    assert str(CaseInstant(-0)) == "0"

    built = CaseInstant(1)

    assert type(built) is CaseInstant
    assert int(built) == 1


def _id(value: object) -> str:
    """Return a parameter's test id, naming a count too long to print by its length."""

    return describe_count(value) if isinstance(value, int) else repr(value)


@pytest.mark.parametrize("step_count", [0, 1, 86_400, 2**63, 10**5000], ids=_id)
def test_a_step_count_is_any_whole_nonnegative_count_however_long(step_count: int) -> None:
    """On its own, a count is checked only for being whole and nonnegative.

    A count past the span is built here, because how many steps a run may
    complete is the run's limit and not the count's. `SimulationState` refuses
    such a count where it stores it, and names a count too long to print by
    its length.
    """

    built = StepCount(step_count)

    assert type(built) is StepCount
    assert isinstance(built, int)
    assert built == step_count


@pytest.mark.parametrize("step_count", [-1, -(10**5000)], ids=_id)
def test_a_step_count_refuses_what_is_not_a_whole_nonnegative_count(step_count: object) -> None:
    """The refusal uses the words that `SimulationState` used before the count was a type.

    A count below zero would stand before the run began. It is the one refusal
    left as a configuration error, because a value that is not an `int` at all
    is a programming error, as the next test shows.
    """

    with pytest.raises(SimulationConfigurationError, match="whole, nonnegative number of steps"):
        StepCount(step_count)  # type: ignore[arg-type]


@pytest.mark.parametrize("step_count", [2.5, 2.0, nan, inf, True, False, "3", None], ids=_id)
def test_a_step_count_refuses_what_is_not_an_int_as_a_programming_error(step_count: object) -> None:
    """The refusal is a `TypeError`, as when a flow refuses what is not a number (`PL-LLMN`).

    `2.0` is whole and is refused all the same. A count is an `int`, so a
    `float` handed in is a sign that something computed it as a time. A
    `bool` is an `int` to Python and is refused with the rest, which
    `SimulationState` did not do before the count was a type: `True` is not a
    count of steps. Until `PL-LLMN`, these were configuration errors. A caller
    that caught the exception a refused setting raises would have caught its
    own mistake along with it.
    """

    with pytest.raises(TypeError) as raised:
        StepCount(step_count)  # type: ignore[arg-type]

    assert str(raised.value).startswith(
        f"step_count of {_id(step_count)} has type {type(step_count).__name__}, not int"
    )


def test_arithmetic_on_an_instant_or_a_count_is_a_plain_number() -> None:
    """A value derived from an instant or a count is not checked, and must not look checked.

    The instant one step past the end of the span is outside the span. So is
    the count one step past the last step that a run may take. If either sum
    were still the type, it would promise a check that never ran.
    `SimulationState` builds the type again where it stores the next count and
    where it reports the instant it stands at.
    """

    at_the_end = CaseInstant(MAXIMUM_ELAPSED_SIMULATION_TIME_S)
    at_the_limit = StepCount(MAXIMUM_STEP_COUNT)

    assert type(at_the_end + SIMULATION_STEP_S) is int
    assert type(at_the_end - at_the_end) is int
    assert type(-at_the_end) is int
    assert type(at_the_limit + 1) is int
    assert type(at_the_limit * SIMULATION_STEP_S) is int
    assert type(-at_the_limit) is int


@pytest.mark.parametrize("built", [CaseInstant(600), StepCount(6_000)], ids=repr)
def test_an_instant_and_a_count_survive_copy_and_pickle_as_their_types(built: object) -> None:
    """Each is rebuilt through its type's constructor, which checks it again and keeps the type."""

    for copied in (copy.copy(built), copy.deepcopy(built), pickle.loads(pickle.dumps(built))):
        assert type(copied) is type(built)
        assert copied == built


def test_a_value_not_built_as_the_type_is_refused_whatever_it_holds() -> None:
    """Each type refuses an unchecked value for the missing check, not for its number.

    An equal plain number, a `bool` and `None` are each refused by name. The
    refusal says what to build, without offering the value as the thing to
    build it from. `CaseInstant(True)` was built, as 1 s, until `PL-7N8P`, and
    `StepCount(None)` never was.
    """

    for unbuilt in (600.0, 600, True, None):
        with pytest.raises(TypeError, match="was not built as CaseInstant") as raised:
            require_case_instant("instant_s", unbuilt)

        assert f"it is {type(unbuilt).__name__}" in str(raised.value)
        assert "build it as CaseInstant(...)" in str(raised.value)
        # The refusal ends by naming the section that gives the run length,
        # which is in `docs/INTERFACE.md` since `PL-CTXZ` moved it there.
        assert str(raised.value).endswith(
            "which checks it against the supported run length once "
            '(docs/INTERFACE.md, "Supported run length")'
        )

    for unbuilt in (6_000, 6_000.0, True, None):
        with pytest.raises(TypeError, match="was not built as StepCount") as raised:
            require_step_count(unbuilt)

        assert f"it is {type(unbuilt).__name__}" in str(raised.value)
        assert "build it as StepCount(...)" in str(raised.value)

    require_case_instant("instant_s", CaseInstant(600))
    require_step_count(StepCount(6_000))


@pytest.mark.parametrize(
    "other",
    [
        StepCount(600),
        FreshGasFlow(4.0),
        AlveolarVentilation(4.0),
        CardiacOutput(5.0),
        Fraction(0.5),
        Percent(2.0),
    ],
    ids=lambda other: type(other).__name__,
)
def test_another_quantity_handed_in_as_an_instant_is_refused_as_a_swapped_argument(
    other: object,
) -> None:
    """The refusal names what the value was built as, and does not say to rebuild it as an instant.

    A count of 600 steps arriving where an instant belongs is a swapped
    argument. A refusal that prescribed `CaseInstant(600)` would
    have the caller build an instant of 600 s from it. That instant passes
    every check and is the wrong quantity, so the message prescribes nothing.
    """

    with pytest.raises(TypeError) as raised:
        require_case_instant("instant_s", other)

    message = str(raised.value)

    assert f"was built as {type(other).__name__}, which is not CaseInstant" in message
    assert "it is another quantity" in message
    assert "CaseInstant(" not in message


@pytest.mark.parametrize(
    "other",
    [
        CaseInstant(600),
        FreshGasFlow(4.0),
        AlveolarVentilation(4.0),
        CardiacOutput(5.0),
        Fraction(0.5),
        Percent(2.0),
    ],
    ids=lambda other: type(other).__name__,
)
def test_another_quantity_handed_in_as_a_count_is_refused_as_a_swapped_argument(
    other: object,
) -> None:
    """The refusal names what the value was built as, and does not say to rebuild it as a count."""

    with pytest.raises(TypeError) as raised:
        require_step_count(other)

    message = str(raised.value)

    assert f"was built as {type(other).__name__}, which is not StepCount" in message
    assert "it is another quantity" in message
    assert "StepCount(" not in message


# --- The model envelope against the machine's range (PL-8PS6) ---------------

# The two claims shared one pair of constants until PL-8PS6. The module above
# declares the *model's* envelope. A machine profile declares what that machine
# can physically set. The effective limit on the control is the intersection of
# the two. The test below pins that neither limit can be mistaken for the
# other. A machine range narrower than the envelope refuses in the machine's
# name. A flow outside the envelope is refused in the model's name, even on a
# machine that could deliver it.


def test_machine_deliverable_flow_range_is_separate_from_model_envelope() -> None:
    """Each limit refuses in its own name, so a reader can tell which limit applied.

    The safety property is the second assertion rather than the first. A
    machine whose flowmeter runs past the envelope must not widen the domain
    over which the compartment model is claimed to hold. So the flow that the
    machine *can* deliver is still refused, and the refusal says that the
    model refused it.
    """

    machine_range = DeliverableFreshGasFlowRange(
        minimum_l_min=0.5, maximum_l_min=MAXIMUM_FRESH_GAS_FLOW_L_MIN + 5.0
    )
    circuit = BreathingCircuit(
        circuit_volume_l=CompartmentVolume(6.0),
        max_delivered_concentration_percent=Percent(100.0),
        deliverable_fresh_gas_flow_range=machine_range,
    )

    with pytest.raises(SimulationConfigurationError) as below_the_machine:
        circuit.set_fresh_gas_flow(FreshGasFlow(0.2))

    with pytest.raises(SimulationConfigurationError) as above_the_model:
        circuit.set_fresh_gas_flow(FreshGasFlow(MAXIMUM_FRESH_GAS_FLOW_L_MIN + 1.0))

    assert "machine" in str(below_the_machine.value)
    assert "0.5 to 15.0 L/min" in str(below_the_machine.value)

    assert "compartment model is claimed to represent a patient over" in str(above_the_model.value)
    assert f"{MINIMUM_FRESH_GAS_FLOW_L_MIN} to {MAXIMUM_FRESH_GAS_FLOW_L_MIN} L/min" in str(
        above_the_model.value
    )

    assert circuit.fresh_gas_flow_l_min == 4.0


@pytest.mark.parametrize("capacity_l", [0.01, 0.2, 3.7, 6.0, 1e4])
def test_an_amount_set_at_the_input_ceiling_is_accepted_and_one_more_is_not(
    capacity_l: float,
) -> None:
    """The opening check compares amounts, so a fraction set at the ceiling passes (`PL-9B1M`).

    A compartment stores an amount and divides it by its capacity to report a
    fraction. So a fraction set to 0.99 can read back one unit in the last place
    higher. The check compares the amount with the capacity times the ceiling,
    which is the same product that the setter stores. The next float above that
    amount is rejected. The error message quotes the fraction that the
    compartment holds, and gives the limit as 0.99 of the ambient pressure.
    """

    at_the_ceiling = capacity_l * MAXIMUM_INPUT_FRACTION
    require_held_within_input_ceiling("venous pool", at_the_ceiling, capacity_l)

    with pytest.raises(SimulationConfigurationError) as raised:
        require_held_within_input_ceiling("venous pool", nextafter(at_the_ceiling, inf), capacity_l)

    message = str(raised.value)
    assert message.startswith("venous pool of 0.99"), message
    assert "is above 0.99 of the ambient pressure" in message, message


def test_a_dial_and_a_fraction_above_the_input_ceiling_are_refused_in_their_own_units() -> None:
    """A dial is quoted in percent and a fraction as a fraction, each against 0.99 atm."""

    require_within_input_ceiling("dial", Percent(99.0))
    require_within_input_ceiling("fraction", 0.99)

    with pytest.raises(
        SimulationConfigurationError, match=r"^dial of 99\.5% is above 99% of the ambient"
    ):
        require_within_input_ceiling("dial", Percent(99.5))

    with pytest.raises(
        SimulationConfigurationError, match=r"^fraction of 0\.995 is above 0\.99 of"
    ):
        require_within_input_ceiling("fraction", 0.995)
