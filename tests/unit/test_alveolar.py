import pytest

from anesthesia_sim.core.alveolar import AlveolarCompartment
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.supported_ranges import MAXIMUM_ALVEOLAR_VENTILATION_L_MIN


def test_rejects_agent_amount_above_alveolar_capacity() -> None:
    with pytest.raises(
        SimulationConfigurationError,
        match="^agent_amount_l exceeds the alveolar capacity for a concentration fraction of 1$",
    ):
        AlveolarCompartment(agent_amount_l=2.6)


def test_changing_ventilation_preserves_alveolar_agent() -> None:
    alveoli = AlveolarCompartment()
    alveoli.set_concentration_fraction(0.05)
    amount_before = alveoli.agent_amount_l

    alveoli.set_alveolar_ventilation(8.0)

    assert alveoli.alveolar_ventilation_l_min == 8.0
    assert alveoli.agent_amount_l == amount_before


def test_reset_clears_agent_and_preserves_settings() -> None:
    alveoli = AlveolarCompartment(gas_volume_l=3.0, alveolar_ventilation_l_min=5.0)
    alveoli.set_concentration_fraction(0.05)

    alveoli.reset()

    assert alveoli.agent_amount_l == 0.0
    assert alveoli.concentration_fraction == 0.0
    assert alveoli.gas_volume_l == 3.0
    assert alveoli.alveolar_ventilation_l_min == 5.0


def test_accepts_ventilation_at_both_ends_of_the_supported_range() -> None:
    """Zero is apnoea, a supported and deliberately teachable input; the
    maximum is the corner of the settings envelope the gates measure at."""

    for alveolar_ventilation_l_min in (0.0, MAXIMUM_ALVEOLAR_VENTILATION_L_MIN):
        alveoli = AlveolarCompartment(alveolar_ventilation_l_min=alveolar_ventilation_l_min)

        assert alveoli.alveolar_ventilation_l_min == alveolar_ventilation_l_min

        alveoli.set_alveolar_ventilation(alveolar_ventilation_l_min)

        assert alveoli.alveolar_ventilation_l_min == alveolar_ventilation_l_min


def test_rejects_ventilation_above_the_supported_range() -> None:
    """Regression (PL-0MLQ): 200 L/min was accepted and simulated."""

    alveoli = AlveolarCompartment(alveolar_ventilation_l_min=4.0)

    with pytest.raises(SimulationConfigurationError, match="supported input range"):
        alveoli.set_alveolar_ventilation(200.0)

    assert alveoli.alveolar_ventilation_l_min == 4.0


def test_rejects_construction_with_ventilation_above_the_supported_range() -> None:
    with pytest.raises(SimulationConfigurationError, match="supported input range"):
        AlveolarCompartment(alveolar_ventilation_l_min=200.0)
