from math import inf

import pytest

from anesthesia_sim.core.alveolar import AlveolarCompartment
from anesthesia_sim.core.exceptions import SimulationConfigurationError


def test_time_constant_is_the_ventilatory_turnover_of_the_gas_volume() -> None:
    alveoli = AlveolarCompartment(
        gas_volume_l=2.5,
        alveolar_ventilation_l_min=5.0,
    )

    assert alveoli.time_constant_s == pytest.approx(30.0)


def test_zero_ventilation_gives_an_infinite_time_constant() -> None:
    alveoli = AlveolarCompartment(
        alveolar_ventilation_l_min=0.0,
    )

    assert alveoli.time_constant_s == inf


def test_positive_blood_uptake_removes_alveolar_agent() -> None:
    alveoli = AlveolarCompartment()
    alveoli.set_concentration_fraction(0.08)
    amount_before = alveoli.agent_amount_l

    alveoli.apply_blood_uptake(0.01)

    assert alveoli.agent_amount_l == pytest.approx(amount_before - 0.01)


def test_negative_blood_uptake_returns_agent_to_alveoli() -> None:
    alveoli = AlveolarCompartment()
    alveoli.set_concentration_fraction(0.02)
    amount_before = alveoli.agent_amount_l

    alveoli.apply_blood_uptake(-0.01)

    assert alveoli.agent_amount_l == pytest.approx(amount_before + 0.01)


def test_rejects_blood_uptake_larger_than_available_amount() -> None:
    alveoli = AlveolarCompartment()
    alveoli.set_concentration_fraction(0.01)

    with pytest.raises(
        SimulationConfigurationError,
        match="resulting_agent_amount_l",
    ):
        alveoli.apply_blood_uptake(alveoli.agent_amount_l + 0.001)


def test_changing_ventilation_preserves_alveolar_agent() -> None:
    alveoli = AlveolarCompartment()
    alveoli.set_concentration_fraction(0.05)
    amount_before = alveoli.agent_amount_l

    alveoli.set_alveolar_ventilation(8.0)

    assert alveoli.alveolar_ventilation_l_min == 8.0
    assert alveoli.agent_amount_l == amount_before


def test_reset_clears_agent_and_preserves_settings() -> None:
    alveoli = AlveolarCompartment(
        gas_volume_l=3.0,
        alveolar_ventilation_l_min=5.0,
    )
    alveoli.set_concentration_fraction(0.05)

    alveoli.reset()

    assert alveoli.agent_amount_l == 0.0
    assert alveoli.concentration_fraction == 0.0
    assert alveoli.gas_volume_l == 3.0
    assert alveoli.alveolar_ventilation_l_min == 5.0
