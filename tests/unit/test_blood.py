import copy
import pickle
import re
from dataclasses import astuple, replace
from math import exp, inf, nan, nextafter

import pytest

from anesthesia_sim.core.blood import VenousBloodCompartment
from anesthesia_sim.core.concentration import Fraction
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.numerical_envelope import CompartmentVolume, PartitionCoefficient

BLOOD_FLOW_L_MIN = 5.0
"""The blood flow, in L/min, at which these tests mix the pool, unless a test says otherwise.

The pool has stored no flow since `PL-HQF5`, so each closed form takes the flow
as an argument.
"""


# The end of a shared guard's refusal message, which names the refused value and
# the reason (`PL-T137`). The guard's own tests pin each reason. These tests pin
# the field name.
REFUSAL_REASON = r", and [^ ]+ is (?:not finite|not greater than zero|negative)$"


def _build_venous_blood() -> VenousBloodCompartment:
    return VenousBloodCompartment(
        volume_l=CompartmentVolume(1.0), blood_gas_partition_coefficient=PartitionCoefficient(0.65)
    )


def test_rejects_agent_amount_above_venous_blood_capacity() -> None:
    with pytest.raises(
        SimulationConfigurationError,
        match=(
            r"^venous agent_amount_l of 0.66 L is more than the 0.65 L the venous blood holds "
            r'at a partial pressure of one atmosphere \(docs/MODEL.md, "Blood compartments"\)$'
        ),
    ):
        VenousBloodCompartment(
            volume_l=CompartmentVolume(1.0),
            blood_gas_partition_coefficient=PartitionCoefficient(0.65),
            agent_amount_l=0.66,
        )


TOO_SMALL_FOR_THE_AGENT_HELD = (
    r"^venous {field} of {value} is too small for the 0.325 L of agent the venous blood holds: it "
    r"would leave room for {room} L at a partial pressure of one atmosphere "
    r'\(docs/MODEL.md, "Blood compartments"\)$'
)


@pytest.mark.parametrize(
    ("field", "value", "error", "message"),
    [
        pytest.param(
            "volume_l",
            0.0,
            TypeError,
            "^venous volume_l of 0.0 was not built as CompartmentVolume, it is float",
            id="zero-volume",
        ),
        pytest.param(
            "volume_l",
            nan,
            TypeError,
            "^venous volume_l of nan was not built as CompartmentVolume, it is float",
            id="nan-volume",
        ),
        pytest.param(
            "volume_l",
            "1",
            TypeError,
            "^venous volume_l of '1' was not built as CompartmentVolume, it is str",
            id="str-volume",
        ),
        pytest.param(
            "volume_l",
            CompartmentVolume(0.4),
            SimulationConfigurationError,
            TOO_SMALL_FOR_THE_AGENT_HELD.format(field="volume_l", value="0.4", room="0.26"),
            id="volume-under-the-agent-held",
        ),
        pytest.param(
            "blood_gas_partition_coefficient",
            -0.65,
            TypeError,
            "^venous blood_gas_partition_coefficient of -0.65 was not built as "
            "PartitionCoefficient, it is float",
            id="negative-blood-gas-coefficient",
        ),
        pytest.param(
            "blood_gas_partition_coefficient",
            PartitionCoefficient(0.2),
            SimulationConfigurationError,
            TOO_SMALL_FOR_THE_AGENT_HELD.format(
                field="blood_gas_partition_coefficient", value="0.2", room="0.2"
            ),
            id="blood-gas-coefficient-under-the-agent-held",
        ),
        pytest.param(
            "blood_flow_l_min",
            5.0,
            AttributeError,
            "^'VenousBloodCompartment' object has no attribute 'blood_flow_l_min'",
            id="blood-flow-is-no-field",
        ),
        pytest.param(
            "agent_amount_l",
            0.65 * 1.0000001,
            SimulationConfigurationError,
            rf"^venous agent_amount_l of {re.escape(repr(0.65 * 1.0000001))} L is more than the "
            r"0.65 L the venous blood holds at a partial pressure of one atmosphere "
            r'\(docs/MODEL.md, "Blood compartments"\)$',
            id="amount-past-capacity",
        ),
        pytest.param(
            "agent_amount_l",
            -0.1,
            SimulationConfigurationError,
            "^venous agent_amount_l must be nonnegative and finite" + REFUSAL_REASON,
            id="negative-amount",
        ),
        pytest.param(
            "agent_amount_l",
            nan,
            SimulationConfigurationError,
            "^venous agent_amount_l must be nonnegative and finite" + REFUSAL_REASON,
            id="nan-amount",
        ),
        pytest.param(
            "volume",
            1.0,
            AttributeError,
            "^'VenousBloodCompartment' object has no attribute 'volume'",
            id="misspelt-field",
        ),
    ],
)
def test_a_direct_write_is_held_to_the_constructors_checks(
    field: str, value: object, error: type[Exception], message: str
) -> None:
    """A direct assignment is refused as the constructor and the setters would refuse it.

    Until `PL-19Y0`, the venous pool checked nothing after its constructor. So
    an amount greater than its capacity, written onto a built pool, was stored
    and read back as a partial pressure fraction of 1.0000001. The capacity is
    the volume times the blood:gas coefficient. A write of the volume, the
    coefficient or the amount is refused if it would leave the capacity less
    than the agent the pool holds. A name that is not a field passes through the guard to the slots,
    which refuse it. So a misspelt write cannot leave its intended field
    unchanged while appearing to succeed. Nothing is written when a value is
    refused.
    """

    venous = _build_venous_blood()
    venous.set_partial_pressure_fraction(Fraction(0.5))
    held = astuple(venous)

    with pytest.raises(error, match=message):
        setattr(venous, field, value)

    assert astuple(venous) == held


def test_an_amount_at_capacity_is_written_and_a_copy_is_held_to_it_too() -> None:
    """The capacity bound is closed, and `replace`, a copy and a pickle meet the same checks.

    An amount equal to the capacity is a partial pressure of exactly one
    atmosphere, and it is written. `dataclasses.replace` builds a new pool
    through its constructor's writes. A copy and a pickle restore the fields
    one at a time through `__setattr__`. So an amount planted by bypassing the
    guard is refused when the copy or the pickle is made, rather than carried
    into the new pool (`PL-19Y0`).
    """

    venous = _build_venous_blood()
    past_capacity = venous.capacity_l * 1.0000001
    refused = (
        rf"^venous agent_amount_l of {re.escape(repr(past_capacity))} L is more than the "
        r"0.65 L the venous blood holds at a partial pressure of one atmosphere "
        r'\(docs/MODEL.md, "Blood compartments"\)$'
    )

    with pytest.raises(SimulationConfigurationError, match=refused):
        replace(venous, agent_amount_l=past_capacity)

    smuggled = copy.copy(venous)
    object.__setattr__(smuggled, "agent_amount_l", past_capacity)

    with pytest.raises(SimulationConfigurationError, match=refused):
        copy.copy(smuggled)

    with pytest.raises(SimulationConfigurationError, match=refused):
        pickle.loads(pickle.dumps(smuggled))

    venous.agent_amount_l = venous.capacity_l

    assert venous.partial_pressure_fraction == 1.0


def test_a_coefficient_is_held_to_the_agent_through_the_capacity_it_leaves() -> None:
    """A blood:gas coefficient is checked through the capacity it gives, not by its value alone.

    The capacity is the volume times the coefficient. A 2 L pool at half its
    1.3 L capacity holds 0.65 L. A coefficient of 0.4 leaves 0.8 L of room and
    is written, although 0.4 alone is less than the amount of agent held. A
    coefficient of 0.3 leaves 0.6 L and is refused (`PL-19Y0`).
    """

    venous = VenousBloodCompartment(
        volume_l=CompartmentVolume(2.0), blood_gas_partition_coefficient=PartitionCoefficient(0.65)
    )
    venous.set_partial_pressure_fraction(Fraction(0.5))

    venous.blood_gas_partition_coefficient = PartitionCoefficient(0.4)

    assert venous.capacity_l == pytest.approx(0.8)

    with pytest.raises(SimulationConfigurationError, match=r"leave room for 0\.6 L "):
        venous.blood_gas_partition_coefficient = PartitionCoefficient(0.3)


@pytest.mark.parametrize("blood_flow_l_min", [-1.0, inf, nan])
def test_a_refused_blood_flow_leaves_the_flow_as_it_was(blood_flow_l_min: float) -> None:
    """A flow at which the closed form cannot be evaluated is refused, and nothing changes.

    The flow was a stored field until `PL-HQF5`, and a write to that field
    refused such a flow (`PL-19Y0`). The flow is now an argument of
    `time_constant_s` and `advance`, which refuse it in the same words before
    anything changes.
    """

    venous = _build_venous_blood()
    venous.set_partial_pressure_fraction(Fraction(0.4))
    held = astuple(venous)

    with pytest.raises(
        SimulationConfigurationError,
        match="^venous blood_flow_l_min must be nonnegative and finite" + REFUSAL_REASON,
    ):
        venous.time_constant_s(blood_flow_l_min)

    with pytest.raises(
        SimulationConfigurationError,
        match="^venous blood_flow_l_min must be nonnegative and finite" + REFUSAL_REASON,
    ):
        venous.advance(
            tissue_return_partial_pressure_fraction=Fraction(1.0),
            simulation_step_s=1.0,
            blood_flow_l_min=blood_flow_l_min,
        )

    assert astuple(venous) == held


def test_a_rollback_restores_the_captured_amount_past_the_capacity_guard() -> None:
    """`restore_state` writes what the pool held, whatever the capacity has become.

    This is the venous counterpart of the test of the same name in
    `tests/unit/test_alveolar.py`. A rollback that could raise would replace
    the step's own error, so the captured amount is written without passing
    the capacity guard (`PL-544D`, `PL-19Y0`). The test writes the volume by
    bypassing its own guard, which would refuse it, because the rollback is
    what is under test. The restored state is the one the step began from. It
    is over capacity, so the snapshot's `Fraction` is left to refuse it.
    """

    venous = _build_venous_blood()
    venous.set_partial_pressure_fraction(Fraction(0.4))
    captured = venous.capture_state()
    venous.set_partial_pressure_fraction(Fraction(0.5))
    object.__setattr__(venous, "volume_l", venous.volume_l / 4)

    venous.restore_state(captured)

    assert venous.agent_amount_l == captured.agent_amount_l
    assert venous.partial_pressure_fraction > 1.0


def test_capacity_uses_volume_and_partition_coefficient() -> None:
    venous = _build_venous_blood()

    assert venous.capacity_l == 0.65


def test_one_time_constant_reaches_expected_fraction() -> None:
    venous = _build_venous_blood()

    venous.advance(
        tissue_return_partial_pressure_fraction=Fraction(1.0),
        simulation_step_s=venous.time_constant_s(BLOOD_FLOW_L_MIN),
        blood_flow_l_min=BLOOD_FLOW_L_MIN,
    )

    assert venous.partial_pressure_fraction == pytest.approx(1.0 - exp(-1.0))


def test_zero_blood_flow_preserves_venous_state() -> None:
    venous = _build_venous_blood()
    venous.set_partial_pressure_fraction(Fraction(0.25))

    amount_before = venous.agent_amount_l
    amount_change = venous.advance(
        tissue_return_partial_pressure_fraction=Fraction(1.0),
        simulation_step_s=60.0,
        blood_flow_l_min=0.0,
    )

    assert venous.time_constant_s(0.0) == inf
    assert amount_change == 0.0
    assert venous.agent_amount_l == amount_before


def test_washout_returns_negative_amount_change() -> None:
    venous = _build_venous_blood()
    venous.set_partial_pressure_fraction(Fraction(0.5))

    amount_change = venous.advance(
        tissue_return_partial_pressure_fraction=Fraction(0.0),
        simulation_step_s=10.0,
        blood_flow_l_min=BLOOD_FLOW_L_MIN,
    )

    assert amount_change < 0.0
    assert 0.0 < venous.partial_pressure_fraction < 0.5


def test_reset_clears_agent_and_preserves_parameters() -> None:
    venous = _build_venous_blood()
    venous.set_partial_pressure_fraction(Fraction(0.25))

    venous.reset()

    assert venous.agent_amount_l == 0.0
    assert venous.volume_l == 1.0


def test_the_time_constant_is_formed_from_the_flow_it_is_given() -> None:
    """`time_constant_s` is $`60 V_v/Q`$ at the flow passed in (`PL-HQF5`).

    The expected values are worked out by hand for a 2.0 L pool:
    60 x 2.0 / 4.0 = 30 s at 4.0 L/min and 60 x 2.0 / 6.0 = 20 s at 6.0 L/min.
    Neither flow is 5 L/min, so a time constant computed at the reference
    patient's output fails. The volume is not 1 L, so dividing by it instead
    of multiplying fails too.
    """

    venous = VenousBloodCompartment(
        volume_l=CompartmentVolume(2.0), blood_gas_partition_coefficient=PartitionCoefficient(0.65)
    )

    assert venous.time_constant_s(4.0) == pytest.approx(30.0, rel=1e-15)
    assert venous.time_constant_s(6.0) == pytest.approx(20.0, rel=1e-15)


@pytest.mark.parametrize("factor", [1e200, 1e-200])
def test_a_capacity_that_overflows_is_refused_at_build(factor: float) -> None:
    """A volume and a coefficient that multiply out of range are refused (`PL-FNH3`, `PL-8LQZ`).

    A volume and a blood:gas coefficient of 1e200 once built a pool whose capacity was `inf`,
    and a pair of 1e-200 built one whose capacity was 0.0. The numerical envelope now refuses
    each factor when it is built, so neither pair can reach the venous pool (`PL-QX2G`).
    """

    shown = re.escape(repr(factor))

    with pytest.raises(
        SimulationConfigurationError,
        match=(
            rf"^venous volume_l of {shown} is outside the numerical envelope of "
            r"0\.01 to 10000 L,"
        ),
    ):
        CompartmentVolume(factor, name="venous volume_l")

    with pytest.raises(
        SimulationConfigurationError,
        match=(
            rf"^venous blood_gas_partition_coefficient of {shown} is outside the numerical "
            r"envelope of 0\.001 to 10000,"
        ),
    ):
        PartitionCoefficient(factor, name="venous blood_gas_partition_coefficient")


@pytest.mark.parametrize("simulation_step_s", [nextafter(1e-3, 0.0), 1e-6, 1e-14, 5e-324])
def test_a_step_below_the_floor_is_refused_when_the_pool_is_stepped_alone(
    simulation_step_s: float,
) -> None:
    """`PL-WP52`: the venous pool stepped on its own refuses a step shorter than 1 ms.

    In the pool stepped alone, as in a run, rounding error grows as the step
    shrinks. This pool was held at a fraction of 0.01 and stepped toward 0.02 at
    5 L/min. Over 10 000 steps of 1e-14 s, its change was 4% wrong.
    The step is refused and the amount held does not change. A step equal to the
    smallest supported step is accepted. So is a step of 1 s, which is longer
    than the run's 0.1 s ceiling, because that ceiling does not apply to a
    compartment stepped alone. The expected smallest step, 0.001 s, is
    written out here rather than read from `MINIMUM_SIMULATION_STEP_S`.
    """

    venous = _build_venous_blood()
    held_l = venous.agent_amount_l

    with pytest.raises(
        SimulationConfigurationError,
        match=(
            rf"^venous simulation_step_s of {re.escape(str(simulation_step_s))} s is shorter "
            r"than the smallest supported step of 0\.001 s, below which rounding is a "
            r'growing share of what each step changes \(docs/MODEL.md, "Supported '
            r'simulation step"\)$'
        ),
    ):
        venous.advance(Fraction(0.02), simulation_step_s, BLOOD_FLOW_L_MIN)

    assert venous.agent_amount_l == held_l

    venous.advance(Fraction(0.02), 0.001, BLOOD_FLOW_L_MIN)
    venous.advance(Fraction(0.02), 1.0, BLOOD_FLOW_L_MIN)

    assert venous.agent_amount_l > held_l


@pytest.mark.parametrize(
    "simulation_step_s", [nextafter(86_400.0, inf), 1e6, 1.7976931348623157e308]
)
def test_a_step_past_the_run_length_is_refused_when_the_pool_is_stepped_alone(
    simulation_step_s: float,
) -> None:
    """`PL-YT3T`: the venous pool stepped on its own refuses a step longer than 24 h.

    Every compartment stepped alone has the same ceiling, the supported run length, so one
    function states which steps a compartment accepts. The step is refused and the amount held
    does not change. A step of exactly 86 400 s is accepted, and it brings the venous pool to
    its equilibrium, 0.02 of its capacity. The expected ceiling is written out here rather than
    read from `MAXIMUM_ELAPSED_SIMULATION_TIME_S`.
    """

    venous = _build_venous_blood()
    held_l = venous.agent_amount_l

    with pytest.raises(
        SimulationConfigurationError,
        match=(
            rf"^venous simulation_step_s of {re.escape(str(simulation_step_s))} s is longer "
            r"than the supported run length of 86400 s \(24 h\), the most simulated time "
            r"this model is claimed to represent a patient over, so no single step may be "
            r'longer \(docs/MODEL.md, "Supported simulation step"\)$'
        ),
    ):
        venous.advance(Fraction(0.02), simulation_step_s, BLOOD_FLOW_L_MIN)

    assert venous.agent_amount_l == held_l

    venous.advance(Fraction(0.02), 86_400.0, BLOOD_FLOW_L_MIN)

    assert venous.agent_amount_l == pytest.approx(0.02 * venous.capacity_l, rel=1e-15, abs=0.0)


@pytest.mark.parametrize("invalid_value", [0.0, -1.0, inf, nan])
def test_rejects_invalid_venous_volume(invalid_value: float) -> None:
    """A zero, negative or non-finite venous volume is refused at construction (`PL-X8F6`).

    Since `PL-QX2G`, the value is refused when its `CompartmentVolume` is built, before the
    pool exists. The pool itself refuses the value as a bare `float`, because a bare `float`
    was never checked against the envelope.
    """

    with pytest.raises(
        SimulationConfigurationError,
        match=r"^venous volume_l of .* is outside the numerical envelope of 0\.01 to 10000 L",
    ):
        VenousBloodCompartment(
            volume_l=CompartmentVolume(invalid_value, name="venous volume_l"),
            blood_gas_partition_coefficient=PartitionCoefficient(0.65),
        )

    with pytest.raises(
        TypeError, match=r"^venous volume_l of .* was not built as CompartmentVolume"
    ):
        VenousBloodCompartment(
            volume_l=invalid_value,  # type: ignore[arg-type]
            blood_gas_partition_coefficient=PartitionCoefficient(0.65),
        )
