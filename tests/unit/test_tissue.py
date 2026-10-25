import copy
import pickle
import re
from dataclasses import astuple, replace
from math import exp, inf, nan, nextafter

import pytest

from anesthesia_sim.core.concentration import Fraction
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.numerical_envelope import CompartmentVolume, PartitionCoefficient
from anesthesia_sim.core.supported_ranges import CardiacOutput
from anesthesia_sim.core.tissue import TissueGroup

BLOOD_FLOW_L_MIN = 1.0
"""The flow at which these tests perfuse a tissue, in L/min, unless a test says otherwise.

Since `PL-HQF5` a tissue group stores no flow, so each closed form takes the flow as an argument.
"""


# The end of a shared guard's refusal message, which names the refused value and the reason
# (`PL-T137`). The guard's own tests check each reason. The tests here check the field name.
REFUSAL_REASON = r", and [^ ]+ is (?:not finite|not greater than zero|negative)$"


def _build_tissue() -> TissueGroup:
    return TissueGroup(
        name="test",
        volume_l=CompartmentVolume(2.0),
        perfusion_fraction=0.2,
        blood_gas_partition_coefficient=PartitionCoefficient(0.5),
        tissue_gas_partition_coefficient=PartitionCoefficient(2.0),
    )


def test_rejects_empty_tissue_name() -> None:
    with pytest.raises(SimulationConfigurationError, match="^name must be a nonempty string$"):
        TissueGroup(
            name=" ",
            volume_l=CompartmentVolume(2.0),
            perfusion_fraction=0.2,
            blood_gas_partition_coefficient=PartitionCoefficient(0.5),
            tissue_gas_partition_coefficient=PartitionCoefficient(2.0),
        )


def test_rejects_perfusion_fraction_above_one() -> None:
    with pytest.raises(
        SimulationConfigurationError, match="^test perfusion_fraction must not exceed 1$"
    ):
        TissueGroup(
            name="test",
            volume_l=CompartmentVolume(2.0),
            perfusion_fraction=1.1,
            blood_gas_partition_coefficient=PartitionCoefficient(0.5),
            tissue_gas_partition_coefficient=PartitionCoefficient(2.0),
        )


def test_rejects_agent_amount_above_tissue_capacity() -> None:
    with pytest.raises(
        SimulationConfigurationError,
        match=(
            r"^test agent_amount_l of 4.1 L is more than the 4.0 L the test tissue holds at a "
            r'partial pressure of one atmosphere \(docs/MODEL.md, "Tissue compartments"\)$'
        ),
    ):
        TissueGroup(
            name="test",
            volume_l=CompartmentVolume(2.0),
            perfusion_fraction=0.2,
            blood_gas_partition_coefficient=PartitionCoefficient(0.5),
            tissue_gas_partition_coefficient=PartitionCoefficient(2.0),
            agent_amount_l=4.1,
        )


def test_an_agent_amount_past_capacity_is_refused_at_the_write() -> None:
    """An assignment straight onto the amount meets the constructor's refusal, and writes nothing.

    This is the tissue's counterpart of the test of the same name in
    `tests/unit/test_alveolar.py`. Until `PL-544D`, `TissueGroup` guarded no write at all.
    So an amount past `capacity_l` was stored, and its quotient was refused only when the
    snapshot built the `Fraction`. The write is now refused in the constructor's own words,
    and the field keeps the value it had. `dataclasses.replace` and a copy write through the
    same `__setattr__`. An amount equal to the capacity itself is written.
    """

    tissue = _build_tissue()
    tissue.set_partial_pressure_fraction(Fraction(0.4))
    held = tissue.agent_amount_l
    past_capacity = tissue.capacity_l * 1.0000001
    refused = (
        rf"^test agent_amount_l of {re.escape(repr(past_capacity))} L is more than the 4.0 L "
        r"the test tissue holds at a partial pressure of one atmosphere \(docs/MODEL.md, "
        r'"Tissue compartments"\)$'
    )

    with pytest.raises(SimulationConfigurationError, match=refused):
        tissue.agent_amount_l = past_capacity

    assert tissue.agent_amount_l == held

    for not_an_amount in (-0.1, float("inf"), float("nan")):
        with pytest.raises(SimulationConfigurationError, match="agent_amount_l"):
            tissue.agent_amount_l = not_an_amount

        assert tissue.agent_amount_l == held

    with pytest.raises(SimulationConfigurationError, match=refused):
        replace(tissue, agent_amount_l=past_capacity)

    smuggled = copy.copy(tissue)
    object.__setattr__(smuggled, "agent_amount_l", past_capacity)

    with pytest.raises(SimulationConfigurationError, match=refused):
        copy.copy(smuggled)

    tissue.agent_amount_l = tissue.capacity_l

    assert tissue.partial_pressure_fraction == 1.0


TOO_SMALL_FOR_THE_AGENT_HELD = (
    r"^test {field} of 0.5 is too small for the 2.0 L of agent the test tissue holds: it would "
    r"leave room for 1.0 L at a partial pressure of one atmosphere \(docs/MODEL.md, "
    r'"Tissue compartments"\)$'
)


@pytest.mark.parametrize(
    ("field", "value", "error", "message"),
    [
        pytest.param(
            "name",
            "",
            SimulationConfigurationError,
            "^name must be a nonempty string$",
            id="empty-name",
        ),
        pytest.param(
            "name",
            "  ",
            SimulationConfigurationError,
            "^name must be a nonempty string$",
            id="blank-name",
        ),
        pytest.param("name", 5, TypeError, "^name of 5 has type int, not str$", id="int-name"),
        pytest.param(
            "volume_l",
            0.0,
            TypeError,
            "^test volume_l of 0.0 was not built as CompartmentVolume, it is float",
            id="zero-volume",
        ),
        pytest.param(
            "volume_l",
            -1.0,
            TypeError,
            "^test volume_l of -1.0 was not built as CompartmentVolume, it is float",
            id="negative-volume",
        ),
        pytest.param(
            "volume_l",
            nan,
            TypeError,
            "^test volume_l of nan was not built as CompartmentVolume, it is float",
            id="nan-volume",
        ),
        pytest.param(
            "volume_l",
            "2",
            TypeError,
            "^test volume_l of '2' was not built as CompartmentVolume, it is str",
            id="str-volume",
        ),
        pytest.param(
            "volume_l",
            CompartmentVolume(0.5),
            SimulationConfigurationError,
            TOO_SMALL_FOR_THE_AGENT_HELD.format(field="volume_l"),
            id="volume-under-the-agent-held",
        ),
        pytest.param(
            "perfusion_fraction",
            0.0,
            SimulationConfigurationError,
            "^test perfusion_fraction must be positive and finite" + REFUSAL_REASON,
            id="zero-perfusion-fraction",
        ),
        pytest.param(
            "perfusion_fraction",
            7.0,
            SimulationConfigurationError,
            "^test perfusion_fraction must not exceed 1$",
            id="perfusion-fraction-above-one",
        ),
        pytest.param(
            "perfusion_fraction",
            nan,
            SimulationConfigurationError,
            "^test perfusion_fraction must be positive and finite" + REFUSAL_REASON,
            id="nan-perfusion-fraction",
        ),
        pytest.param(
            "blood_gas_partition_coefficient",
            0.0,
            TypeError,
            "^test blood_gas_partition_coefficient of 0.0 was not built as PartitionCoefficient, "
            "it is float",
            id="zero-blood-gas-coefficient",
        ),
        pytest.param(
            "blood_gas_partition_coefficient",
            inf,
            TypeError,
            "^test blood_gas_partition_coefficient of inf was not built as PartitionCoefficient, "
            "it is float",
            id="infinite-blood-gas-coefficient",
        ),
        pytest.param(
            "tissue_gas_partition_coefficient",
            0.0,
            TypeError,
            "^test tissue_gas_partition_coefficient of 0.0 was not built as PartitionCoefficient, "
            "it is float",
            id="zero-tissue-gas-coefficient",
        ),
        pytest.param(
            "tissue_gas_partition_coefficient",
            PartitionCoefficient(0.5),
            SimulationConfigurationError,
            TOO_SMALL_FOR_THE_AGENT_HELD.format(field="tissue_gas_partition_coefficient"),
            id="tissue-gas-coefficient-under-the-agent-held",
        ),
        pytest.param(
            "perfusion_fraction",
            0.3,
            SimulationConfigurationError,
            "^the test tissue group's perfusion fraction of 0.2 cannot be written again, "
            "as 0.3, once the group is built",
            id="perfusion-fraction-rewritten",
        ),
        pytest.param(
            "blood_flow_l_min",
            1.0,
            AttributeError,
            "^'TissueGroup' object has no attribute 'blood_flow_l_min'",
            id="blood-flow-is-no-field",
        ),
        pytest.param(
            "volume",
            1.0,
            AttributeError,
            "^'TissueGroup' object has no attribute 'volume'",
            id="misspelt-field",
        ),
    ],
)
def test_a_direct_write_is_held_to_the_constructors_checks(
    field: str, value: object, error: type[Exception], message: str
) -> None:
    """An assignment that bypasses the constructor and the setters is refused as they refuse it.

    Until `PL-19Y0`, only the agent amount was checked at the write (`PL-544D`). So
    `perfusion_fraction = 7.0` and `volume_l = -1.0` were each accepted on a built tissue. A
    valid perfusion fraction is refused too, because the fraction is written once
    (`PL-Z0HN`), and a blood flow is not a field that can be written (`PL-HQF5`). A volume or
    a tissue:gas coefficient is also checked against the agent that the tissue holds.
    Lowering either one shrinks the capacity, and the partial pressure is the amount held
    divided by that capacity. A value of 0.5 for either one, with 2.0 L of agent held, would
    put this tissue at two atmospheres. A name that is not a field passes the guard to the
    slots, which refuse it. So a misspelt write cannot leave the intended field unchanged
    while appearing to succeed. Nothing is written when a value is refused.
    """

    tissue = _build_tissue()
    tissue.set_partial_pressure_fraction(Fraction(0.5))
    held = astuple(tissue)

    with pytest.raises(error, match=message):
        setattr(tissue, field, value)

    assert astuple(tissue) == held


def test_a_capacity_at_the_agent_held_is_written_and_a_copy_is_held_to_it_too() -> None:
    """The capacity bound is closed, and `replace`, a copy and a pickle meet the same checks.

    A volume or a tissue:gas coefficient that gives a capacity equal to the agent held means
    a partial pressure of exactly one atmosphere, and that value is written. The
    coefficient's capacity is formed with the volume, not with the blood:gas coefficient,
    which this tissue holds at a quarter of its tissue:gas coefficient.
    `dataclasses.replace` builds a new tissue through its constructor's writes. A copy and a
    pickle restore the fields one at a time through `__setattr__`. So a perfusion fraction
    planted by bypassing the guard is refused when a copy or a pickle is made, rather than
    carried into the new tissue (`PL-19Y0`).
    """

    tissue = _build_tissue()
    tissue.set_partial_pressure_fraction(Fraction(0.5))
    refused = "^test perfusion_fraction must not exceed 1$"

    with pytest.raises(SimulationConfigurationError, match=refused):
        replace(tissue, perfusion_fraction=7.0)

    smuggled = copy.copy(tissue)
    object.__setattr__(smuggled, "perfusion_fraction", 7.0)

    with pytest.raises(SimulationConfigurationError, match=refused):
        copy.copy(smuggled)

    with pytest.raises(SimulationConfigurationError, match=refused):
        pickle.loads(pickle.dumps(smuggled))

    tissue.volume_l = CompartmentVolume(1.0)

    assert tissue.partial_pressure_fraction == 1.0

    tissue.volume_l = CompartmentVolume(2.0)
    tissue.tissue_gas_partition_coefficient = PartitionCoefficient(1.0)

    assert tissue.partial_pressure_fraction == 1.0


@pytest.mark.parametrize("blood_flow_l_min", [-1.0, inf, nan])
def test_a_refused_blood_flow_leaves_the_flow_as_it_was(blood_flow_l_min: float) -> None:
    """A flow at which the closed form cannot be evaluated is refused, and nothing changes.

    The flow was a stored field until `PL-HQF5`, and writing that field refused such a flow
    (`PL-19Y0`). The flow is now the argument of `time_constant_s` and `advance`, which
    refuse it in the same words before anything changes.
    """

    tissue = _build_tissue()
    tissue.set_partial_pressure_fraction(Fraction(0.4))
    held = astuple(tissue)

    with pytest.raises(
        SimulationConfigurationError,
        match="^test blood_flow_l_min must be nonnegative and finite" + REFUSAL_REASON,
    ):
        tissue.time_constant_s(blood_flow_l_min)

    with pytest.raises(
        SimulationConfigurationError,
        match="^test blood_flow_l_min must be nonnegative and finite" + REFUSAL_REASON,
    ):
        tissue.advance(
            arterial_partial_pressure_fraction=Fraction(1.0),
            simulation_step_s=1.0,
            blood_flow_l_min=blood_flow_l_min,
        )

    assert astuple(tissue) == held


def test_a_tissue_is_perfused_at_its_fraction_of_the_cardiac_output() -> None:
    """$`Q_i = f_iQ`$: a 0.2 fraction of 6.5 L/min is 1.3 L/min, computed when it is read.

    The expected flow is worked by hand. A bare `float` is refused, because
    only a `CardiacOutput` carries the supported range (`PL-HQF5`).
    """

    tissue = _build_tissue()

    assert tissue.blood_flow_l_min_at(CardiacOutput(6.5)) == pytest.approx(1.3, rel=1e-15)

    with pytest.raises(TypeError, match="CardiacOutput"):
        tissue.blood_flow_l_min_at(6.5)  # type: ignore[arg-type]


def test_capacity_uses_volume_and_tissue_gas_coefficient() -> None:
    tissue = _build_tissue()

    assert tissue.capacity_l == 4.0


def test_derives_tissue_blood_partition_coefficient() -> None:
    tissue = _build_tissue()

    assert tissue.tissue_blood_partition_coefficient == 4.0


def test_one_time_constant_reaches_expected_fraction() -> None:
    tissue = _build_tissue()

    tissue.advance(
        arterial_partial_pressure_fraction=Fraction(1.0),
        simulation_step_s=tissue.time_constant_s(BLOOD_FLOW_L_MIN),
        blood_flow_l_min=BLOOD_FLOW_L_MIN,
    )

    assert tissue.partial_pressure_fraction == pytest.approx(1.0 - exp(-1.0))


def test_a_larger_or_more_soluble_tissue_has_a_longer_time_constant() -> None:
    """`docs/MODEL.md` § "Directional tissue-capacity test".

    Increasing either $V_i$ or $\\lambda_{i:b}$, with flow held constant, must
    lengthen the tissue time constant.

    Three groups that are otherwise identical, at one blood flow, isolate the two factors.
    The second raises the volume alone. The third raises the tissue:gas coefficient alone,
    which raises $\\lambda_{i:b}$ because the blood:gas coefficient is held fixed. The
    intermediate assertions state that each variant moved only its own factor. The one flow
    is passed to all three, so a change to the fixture cannot leave the directional claims
    below passing for the wrong reason.
    """

    baseline = _build_tissue()
    larger = TissueGroup(
        name="larger",
        volume_l=CompartmentVolume(3.0),
        perfusion_fraction=0.2,
        blood_gas_partition_coefficient=PartitionCoefficient(0.5),
        tissue_gas_partition_coefficient=PartitionCoefficient(2.0),
    )
    more_soluble = TissueGroup(
        name="more soluble",
        volume_l=CompartmentVolume(2.0),
        perfusion_fraction=0.2,
        blood_gas_partition_coefficient=PartitionCoefficient(0.5),
        tissue_gas_partition_coefficient=PartitionCoefficient(3.0),
    )

    assert larger.volume_l > baseline.volume_l
    assert larger.tissue_blood_partition_coefficient == (
        baseline.tissue_blood_partition_coefficient
    )

    assert more_soluble.volume_l == baseline.volume_l
    assert more_soluble.tissue_blood_partition_coefficient > (
        baseline.tissue_blood_partition_coefficient
    )

    assert larger.time_constant_s(BLOOD_FLOW_L_MIN) > baseline.time_constant_s(BLOOD_FLOW_L_MIN)
    assert more_soluble.time_constant_s(BLOOD_FLOW_L_MIN) > baseline.time_constant_s(
        BLOOD_FLOW_L_MIN
    )


def test_zero_flow_preserves_tissue_state() -> None:
    tissue = _build_tissue()
    tissue.set_partial_pressure_fraction(Fraction(0.25))

    amount_before = tissue.agent_amount_l
    amount_change = tissue.advance(
        arterial_partial_pressure_fraction=Fraction(1.0),
        simulation_step_s=60.0,
        blood_flow_l_min=0.0,
    )

    assert tissue.time_constant_s(0.0) == inf
    assert amount_change == 0.0
    assert tissue.agent_amount_l == amount_before
    assert tissue.partial_pressure_fraction == 0.25


def test_washout_returns_agent_to_blood() -> None:
    tissue = _build_tissue()
    tissue.set_partial_pressure_fraction(Fraction(0.8))

    amount_change = tissue.advance(
        arterial_partial_pressure_fraction=Fraction(0.0),
        simulation_step_s=10.0,
        blood_flow_l_min=BLOOD_FLOW_L_MIN,
    )

    assert amount_change < 0.0
    assert 0.0 < tissue.partial_pressure_fraction < 0.8


def test_exact_update_is_independent_of_step_size() -> None:
    one_step = _build_tissue()
    many_steps = _build_tissue()

    one_step.advance(
        arterial_partial_pressure_fraction=Fraction(0.08),
        simulation_step_s=60.0,
        blood_flow_l_min=BLOOD_FLOW_L_MIN,
    )

    for _ in range(600):
        many_steps.advance(
            arterial_partial_pressure_fraction=Fraction(0.08),
            simulation_step_s=0.1,
            blood_flow_l_min=BLOOD_FLOW_L_MIN,
        )

    assert many_steps.agent_amount_l == pytest.approx(one_step.agent_amount_l, rel=1e-12)


def test_reset_clears_agent_and_preserves_parameters() -> None:
    tissue = _build_tissue()
    tissue.set_partial_pressure_fraction(Fraction(0.4))

    tissue.reset()

    assert tissue.agent_amount_l == 0.0
    assert tissue.partial_pressure_fraction == 0.0
    assert tissue.volume_l == 2.0


@pytest.mark.parametrize("invalid_value", [0.0, -1.0, float("inf"), float("nan")])
def test_rejects_invalid_tissue_volume(invalid_value: float) -> None:
    with pytest.raises(
        SimulationConfigurationError,
        match="^volume_l of .* is outside the numerical envelope of 0.01 to 10000 L",
    ):
        TissueGroup(
            name="test",
            volume_l=CompartmentVolume(invalid_value, name="volume_l"),
            perfusion_fraction=0.2,
            blood_gas_partition_coefficient=PartitionCoefficient(0.5),
            tissue_gas_partition_coefficient=PartitionCoefficient(2.0),
        )


@pytest.mark.parametrize(
    ("factor", "checked_type"),
    [
        ("volume_l", "CompartmentVolume"),
        ("tissue_gas_partition_coefficient", "PartitionCoefficient"),
    ],
)
def test_a_capacity_factor_that_is_not_a_number_is_refused_under_its_own_name(
    factor: str, checked_type: str
) -> None:
    """Each factor of the capacity refuses a non-number by its own name, at its own write.

    This is the tissue's counterpart of the test of the same shape in
    `tests/unit/test_alveolar.py`. `capacity_l` multiplies the volume by the coefficient.
    While the amount's write read both factors before `__post_init__` had checked them, a
    `str` in either one came back as the multiplication's own `TypeError`, which named
    neither factor. Only a `require_a_number` call on each factor prevented that
    (`PL-544D`, found at review). Since `PL-19Y0`, each factor's own write checks it first.
    """

    fields: dict[str, object] = dict(
        name="test",
        volume_l=CompartmentVolume(2.0),
        perfusion_fraction=0.2,
        blood_gas_partition_coefficient=PartitionCoefficient(0.5),
        tissue_gas_partition_coefficient=PartitionCoefficient(2.0),
    )
    fields[factor] = "2"

    with pytest.raises(
        TypeError, match=f"^test {factor} of '2' was not built as {checked_type}, it is str"
    ):
        TissueGroup(**fields)  # type: ignore[arg-type]


def test_a_rollback_restores_the_captured_amount_past_the_capacity_guard() -> None:
    """`restore_state` writes what the tissue held, whatever the capacity has become.

    This is the tissue's counterpart of the test of the same name in
    `tests/unit/test_alveolar.py` (`PL-544D`, found at review). The volume is written
    directly, bypassing its own guard, which since `PL-19Y0` would refuse it. The rollback
    then writes the captured amount, bypassing the capacity guard. The restored state is the
    one that the step began from, over capacity, for the snapshot's `Fraction` to refuse.
    """

    tissue = _build_tissue()
    tissue.set_partial_pressure_fraction(Fraction(0.4))
    captured = tissue.capture_state()
    tissue.set_partial_pressure_fraction(Fraction(0.5))
    object.__setattr__(tissue, "volume_l", tissue.volume_l / 4)

    tissue.restore_state(captured)

    assert tissue.agent_amount_l == captured.agent_amount_l
    assert tissue.partial_pressure_fraction > 1.0


def test_the_time_constant_is_formed_from_the_flow_it_is_given() -> None:
    """`time_constant_s` is $`60 V_i\\lambda_{i:b}/Q_i`$ at the flow passed in (`PL-HQF5`).

    The expected values are worked out by hand from the test tissue's
    parameters: a 2.0 L group with a tissue:blood coefficient of
    2.0 / 0.5 = 4.0. So 60 x 2.0 x 4.0 / 2.0 = 240 s at 2.0 L/min, and 96 s
    at 5.0 L/min. The test uses two flows, so a time constant formed at any single fixed flow fails.
    """

    tissue = _build_tissue()

    assert tissue.time_constant_s(2.0) == pytest.approx(240.0, rel=1e-15)
    assert tissue.time_constant_s(5.0) == pytest.approx(96.0, rel=1e-15)


@pytest.mark.parametrize("factor", [1e200, 1e-200])
def test_a_capacity_that_overflows_is_refused_at_build(factor: float) -> None:
    """A volume and a coefficient that multiply out of range are refused (`PL-FNH3`, `PL-8LQZ`).

    A volume and a tissue:gas coefficient of 1e200 once built a group whose capacity was `inf`,
    and a pair of 1e-200 built one whose capacity was 0.0. The numerical envelope now refuses
    each factor when it is built, so neither pair can reach a tissue group (`PL-QX2G`).
    """

    shown = re.escape(repr(factor))

    with pytest.raises(
        SimulationConfigurationError,
        match=rf"^test volume_l of {shown} is outside the numerical envelope of 0\.01 to 10000 L,",
    ):
        CompartmentVolume(factor, name="test volume_l")

    with pytest.raises(
        SimulationConfigurationError,
        match=(
            rf"^test tissue_gas_partition_coefficient of {shown} is outside the numerical "
            r"envelope of 0\.001 to 10000,"
        ),
    ):
        PartitionCoefficient(factor, name="test tissue_gas_partition_coefficient")


@pytest.mark.parametrize("simulation_step_s", [nextafter(1e-3, 0.0), 1e-6, 1e-14, 5e-324])
def test_a_step_below_the_floor_is_refused_when_a_tissue_is_stepped_alone(
    simulation_step_s: float,
) -> None:
    """`PL-WP52`: a tissue group stepped on its own refuses a step shorter than 1 ms.

    Rounding grows as the step shrinks in a tissue stepped alone, as it does in a run. A
    tissue built like this one, held at a fraction of 0.01 and stepped toward 0.02 at
    1 L/min, did not change at all over 10 000 steps of 1e-14 s, although the exact change
    is not zero. The step is refused, and the amount held does not change. The lower bound
    itself is accepted. So is a step of 1 s, which is longer than the run's 0.1 s upper
    bound, because that upper bound does not apply to a compartment stepped alone. The
    expected lower bound, 0.001 s, is written out here rather than read from
    `MINIMUM_SIMULATION_STEP_S`.
    """

    tissue = _build_tissue()
    held_l = tissue.agent_amount_l

    with pytest.raises(
        SimulationConfigurationError,
        match=(
            rf"^test simulation_step_s of {re.escape(str(simulation_step_s))} s is shorter "
            r"than the smallest supported step of 0\.001 s, below which rounding is a "
            r'growing share of what each step changes \(docs/MODEL.md, "Supported '
            r'simulation step"\)$'
        ),
    ):
        tissue.advance(Fraction(0.02), simulation_step_s, BLOOD_FLOW_L_MIN)

    assert tissue.agent_amount_l == held_l

    tissue.advance(Fraction(0.02), 0.001, BLOOD_FLOW_L_MIN)
    tissue.advance(Fraction(0.02), 1.0, BLOOD_FLOW_L_MIN)

    assert tissue.agent_amount_l > held_l
