from math import exp, inf

import pytest

from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.tissue import TissueGroup


def _build_tissue(
    *,
    blood_flow_l_min: float = 1.0,
) -> TissueGroup:
    return TissueGroup(
        name="test",
        volume_l=2.0,
        perfusion_fraction=0.2,
        blood_gas_partition_coefficient=0.5,
        tissue_gas_partition_coefficient=2.0,
        blood_flow_l_min=blood_flow_l_min,
    )


def test_rejects_empty_tissue_name() -> None:
    with pytest.raises(
        SimulationConfigurationError,
        match="^name must be a nonempty string$",
    ):
        TissueGroup(
            name=" ",
            volume_l=2.0,
            perfusion_fraction=0.2,
            blood_gas_partition_coefficient=0.5,
            tissue_gas_partition_coefficient=2.0,
        )


def test_rejects_perfusion_fraction_above_one() -> None:
    with pytest.raises(
        SimulationConfigurationError,
        match="^perfusion_fraction must not exceed 1$",
    ):
        TissueGroup(
            name="test",
            volume_l=2.0,
            perfusion_fraction=1.1,
            blood_gas_partition_coefficient=0.5,
            tissue_gas_partition_coefficient=2.0,
        )


def test_rejects_agent_amount_above_tissue_capacity() -> None:
    with pytest.raises(
        SimulationConfigurationError,
        match="^agent_amount_l exceeds the tissue capacity for a concentration fraction of 1$",
    ):
        TissueGroup(
            name="test",
            volume_l=2.0,
            perfusion_fraction=0.2,
            blood_gas_partition_coefficient=0.5,
            tissue_gas_partition_coefficient=2.0,
            agent_amount_l=4.1,
        )


def test_capacity_uses_volume_and_tissue_gas_coefficient() -> None:
    tissue = _build_tissue()

    assert tissue.capacity_l == 4.0


def test_derives_tissue_blood_partition_coefficient() -> None:
    tissue = _build_tissue()

    assert tissue.tissue_blood_partition_coefficient == 4.0


def test_one_time_constant_reaches_expected_fraction() -> None:
    tissue = _build_tissue()

    tissue.advance(
        arterial_fraction=1.0,
        simulation_step_s=tissue.time_constant_s,
    )

    assert tissue.partial_pressure_fraction == pytest.approx(1.0 - exp(-1.0))


def test_zero_flow_preserves_tissue_state() -> None:
    tissue = _build_tissue(blood_flow_l_min=0.0)
    tissue.set_partial_pressure_fraction(0.25)

    amount_before = tissue.agent_amount_l
    amount_change = tissue.advance(
        arterial_fraction=1.0,
        simulation_step_s=60.0,
    )

    assert tissue.time_constant_s == inf
    assert amount_change == 0.0
    assert tissue.agent_amount_l == amount_before
    assert tissue.partial_pressure_fraction == 0.25


def test_washout_returns_agent_to_blood() -> None:
    tissue = _build_tissue()
    tissue.set_partial_pressure_fraction(0.8)

    amount_change = tissue.advance(
        arterial_fraction=0.0,
        simulation_step_s=10.0,
    )

    assert amount_change < 0.0
    assert 0.0 < tissue.partial_pressure_fraction < 0.8


def test_exact_update_is_independent_of_step_size() -> None:
    one_step = _build_tissue()
    many_steps = _build_tissue()

    one_step.advance(
        arterial_fraction=0.08,
        simulation_step_s=60.0,
    )

    for _ in range(600):
        many_steps.advance(
            arterial_fraction=0.08,
            simulation_step_s=0.1,
        )

    assert many_steps.agent_amount_l == pytest.approx(
        one_step.agent_amount_l,
        rel=1e-12,
    )


def test_changing_flow_preserves_stored_agent() -> None:
    tissue = _build_tissue()
    tissue.set_partial_pressure_fraction(0.4)
    amount_before = tissue.agent_amount_l

    tissue.set_blood_flow(3.0)

    assert tissue.blood_flow_l_min == 3.0
    assert tissue.agent_amount_l == amount_before


def test_reset_clears_agent_and_preserves_parameters() -> None:
    tissue = _build_tissue()
    tissue.set_partial_pressure_fraction(0.4)

    tissue.reset()

    assert tissue.agent_amount_l == 0.0
    assert tissue.partial_pressure_fraction == 0.0
    assert tissue.volume_l == 2.0
    assert tissue.blood_flow_l_min == 1.0


@pytest.mark.parametrize(
    "invalid_value",
    [0.0, -1.0, float("inf"), float("nan")],
)
def test_rejects_invalid_tissue_volume(
    invalid_value: float,
) -> None:
    with pytest.raises(SimulationConfigurationError, match="volume_l"):
        TissueGroup(
            name="test",
            volume_l=invalid_value,
            perfusion_fraction=0.2,
            blood_gas_partition_coefficient=0.5,
            tissue_gas_partition_coefficient=2.0,
        )
