import pytest

from anesthesia_sim.app.controller import SimulationController


def test_default_controller_starts_with_sevoflurane() -> None:
    controller = SimulationController()

    snapshot = controller.snapshot()

    assert snapshot.agent_id == "sevoflurane"
    assert snapshot.agent_display_name == "Sevoflurane"
    assert snapshot.max_delivered_concentration_percent == 8.0
    assert snapshot.delivered_concentration_fraction == pytest.approx(0.02)


def test_default_controller_starts_each_agent_at_its_own_one_mac() -> None:
    """A freshly constructed controller starts at 1 MAC, the standard
    clinical starting point, not a fixed raw percentage.
    """

    assert SimulationController(
        agent_id="sevoflurane"
    ).snapshot().delivered_concentration_fraction == pytest.approx(0.02)
    assert SimulationController(
        agent_id="isoflurane"
    ).snapshot().delivered_concentration_fraction == pytest.approx(0.012)
    assert SimulationController(
        agent_id="desflurane"
    ).snapshot().delivered_concentration_fraction == pytest.approx(0.06)


def test_explicit_delivered_concentration_still_clamps_to_the_agent_max() -> None:
    """An explicitly requested fraction above a vaporizer's real max is
    still clamped, independent of the 1-MAC default resolution.
    """

    controller = SimulationController(
        agent_id="isoflurane",
        delivered_concentration_fraction=0.08,
    )

    snapshot = controller.snapshot()

    assert snapshot.max_delivered_concentration_percent == 5.0
    assert snapshot.delivered_concentration_fraction == pytest.approx(0.05)


def test_set_agent_resets_delivered_concentration_to_the_new_agent_one_mac() -> None:
    """Switching agents must not carry over the old agent's raw percentage:
    the same percent means a different clinical depth per agent (e.g. 2%
    is 1 MAC of sevoflurane but only about a third of a MAC of desflurane).
    """

    controller = SimulationController(
        agent_id="sevoflurane",
        delivered_concentration_fraction=0.08,
    )

    controller.set_agent("isoflurane")
    snapshot = controller.snapshot()

    assert snapshot.max_delivered_concentration_percent == 5.0
    assert snapshot.delivered_concentration_fraction == pytest.approx(0.012)


def test_controller_can_be_constructed_for_a_different_agent() -> None:
    controller = SimulationController(agent_id="isoflurane")

    snapshot = controller.snapshot()

    assert snapshot.agent_id == "isoflurane"
    assert snapshot.agent_display_name == "Isoflurane"


def test_set_agent_starts_fresh_preserving_flow_settings_but_not_concentration() -> None:
    """Circuit, flow, ventilation, and cardiac output carry over; the
    delivered concentration resets to the new agent's own 1 MAC instead
    (see test_set_agent_resets_delivered_concentration_to_the_new_agent_one_mac).
    """

    controller = SimulationController(
        agent_id="sevoflurane",
        circuit_volume_l=5.0,
        fresh_gas_flow_l_min=3.0,
        delivered_concentration_fraction=0.03,
        alveolar_ventilation_l_min=5.5,
        cardiac_output_l_min=6.0,
    )
    controller.start()
    controller.advance(30.0)

    assert controller.snapshot().stored_agent_l > 0.0

    controller.set_agent("desflurane")
    snapshot = controller.snapshot()

    assert snapshot.agent_id == "desflurane"
    assert snapshot.agent_display_name == "Desflurane"
    assert snapshot.is_running is False
    assert snapshot.elapsed_s == 0.0
    assert snapshot.stored_agent_l == 0.0
    assert snapshot.agent_accounting_passes_validation is True

    assert snapshot.circuit_volume_l == 5.0
    assert snapshot.fresh_gas_flow_l_min == 3.0
    assert snapshot.delivered_concentration_fraction == pytest.approx(0.06)
    assert snapshot.alveolar_ventilation_l_min == 5.5
    assert snapshot.cardiac_output_l_min == 6.0


def test_set_agent_rejects_unknown_agent_id() -> None:
    controller = SimulationController()

    with pytest.raises(ValueError, match="unknown agent_id"):
        controller.set_agent("halothane")


def test_pause_blocks_advancement() -> None:
    controller = SimulationController()

    controller.advance(0.1)

    assert controller.snapshot().elapsed_s == 0.0


def test_start_advance_pause_sequence_is_deterministic() -> None:
    first = SimulationController()
    second = SimulationController()

    for controller in (first, second):
        controller.start()
        controller.advance(0.1)
        controller.advance(0.1)
        controller.pause()

    assert first.snapshot() == second.snapshot()


def test_reset_pauses_and_clears_concentration_history() -> None:
    controller = SimulationController()
    controller.start()
    controller.advance(0.1)

    controller.reset()

    snapshot = controller.snapshot()

    assert snapshot.is_running is False
    assert snapshot.elapsed_s == 0.0
    assert snapshot.circuit_concentration_fraction == 0.0
    assert snapshot.alveolar_concentration_fraction == 0.0
    assert snapshot.stored_agent_l == 0.0
    assert len(snapshot.concentration_history) == 1
    assert snapshot.concentration_history[0].elapsed_s == 0.0


def test_parameter_changes_do_not_reset_dynamic_state() -> None:
    controller = SimulationController()
    controller.start()
    controller.advance(10.0)
    before = controller.snapshot()

    controller.set_circuit_volume(5.0)
    controller.set_fresh_gas_flow(3.0)
    controller.set_delivered_concentration(0.06)

    after = controller.snapshot()

    assert after.elapsed_s == before.elapsed_s
    assert after.stored_agent_l == pytest.approx(before.stored_agent_l)
    assert after.circuit_volume_l == 5.0
    assert after.fresh_gas_flow_l_min == 3.0
    assert after.delivered_concentration_fraction == 0.06
