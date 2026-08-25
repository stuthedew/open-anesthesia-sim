from math import exp, inf

import pytest

from anesthesia_sim.core.blood import VenousBloodCompartment
from anesthesia_sim.core.exceptions import SimulationConfigurationError


def _build_venous_blood(*, blood_flow_l_min: float = 5.0) -> VenousBloodCompartment:
    return VenousBloodCompartment(
        volume_l=1.0, blood_gas_partition_coefficient=0.65, blood_flow_l_min=blood_flow_l_min
    )


def test_rejects_agent_amount_above_venous_blood_capacity() -> None:
    with pytest.raises(
        SimulationConfigurationError, match="^agent_amount_l exceeds venous blood capacity$"
    ):
        VenousBloodCompartment(
            volume_l=1.0,
            blood_gas_partition_coefficient=0.65,
            blood_flow_l_min=5.0,
            agent_amount_l=0.66,
        )


def test_capacity_uses_volume_and_partition_coefficient() -> None:
    venous = _build_venous_blood()

    assert venous.capacity_l == 0.65


def test_one_time_constant_reaches_expected_fraction() -> None:
    venous = _build_venous_blood()

    venous.advance(tissue_return_fraction=1.0, simulation_step_s=venous.time_constant_s)

    assert venous.concentration_fraction == pytest.approx(1.0 - exp(-1.0))


def test_zero_blood_flow_preserves_venous_state() -> None:
    venous = _build_venous_blood(blood_flow_l_min=0.0)
    venous.set_concentration_fraction(0.25)

    amount_before = venous.agent_amount_l
    amount_change = venous.advance(tissue_return_fraction=1.0, simulation_step_s=60.0)

    assert venous.time_constant_s == inf
    assert amount_change == 0.0
    assert venous.agent_amount_l == amount_before


def test_washout_returns_negative_amount_change() -> None:
    venous = _build_venous_blood()
    venous.set_concentration_fraction(0.5)

    amount_change = venous.advance(tissue_return_fraction=0.0, simulation_step_s=10.0)

    assert amount_change < 0.0
    assert 0.0 < venous.concentration_fraction < 0.5


def test_changing_flow_preserves_stored_agent() -> None:
    venous = _build_venous_blood()
    venous.set_concentration_fraction(0.25)
    amount_before = venous.agent_amount_l

    venous.set_blood_flow(7.0)

    assert venous.blood_flow_l_min == 7.0
    assert venous.agent_amount_l == amount_before


def test_reset_clears_agent_and_preserves_parameters() -> None:
    venous = _build_venous_blood()
    venous.set_concentration_fraction(0.25)

    venous.reset()

    assert venous.agent_amount_l == 0.0
    assert venous.volume_l == 1.0
    assert venous.blood_flow_l_min == 5.0
