import pytest

from anesthesia_sim.app.controller import SimulationController


def _advance_for(
    controller: SimulationController,
    duration_s: float,
    simulation_step_s: float = 0.1,
) -> None:
    step_count = round(duration_s / simulation_step_s)

    for _ in range(step_count):
        controller.advance(simulation_step_s)


def test_snapshot_exposes_patient_and_agent_accounting_state() -> None:
    controller = SimulationController()

    snapshot = controller.snapshot()

    assert snapshot.alveolar_ventilation_l_min == 4.0
    assert snapshot.cardiac_output_l_min == 5.0
    assert snapshot.alveolar_concentration_fraction == 0.0
    assert snapshot.mixed_venous_concentration_fraction == 0.0
    assert snapshot.vessel_rich_partial_pressure_fraction == 0.0
    assert snapshot.muscle_partial_pressure_fraction == 0.0
    assert snapshot.fat_partial_pressure_fraction == 0.0
    assert snapshot.agent_accounting_passes_validation is True


def test_running_controller_advances_patient_and_named_history() -> None:
    controller = SimulationController()
    controller.start()

    _advance_for(controller, duration_s=60.0)

    snapshot = controller.snapshot()
    latest_sample = snapshot.concentration_history[-1]

    assert snapshot.circuit_concentration_fraction > 0.0
    assert snapshot.alveolar_concentration_fraction > 0.0
    assert snapshot.vessel_rich_partial_pressure_fraction > 0.0
    assert snapshot.stored_agent_l > 0.0
    assert snapshot.delivered_agent_l > 0.0
    assert snapshot.agent_accounting_passes_validation is True

    assert latest_sample.elapsed_s == pytest.approx(snapshot.elapsed_s)
    assert latest_sample.alveolar_concentration_fraction == pytest.approx(
        snapshot.alveolar_concentration_fraction
    )


def test_ventilation_and_cardiac_output_changes_preserve_state() -> None:
    controller = SimulationController()
    controller.start()
    _advance_for(controller, duration_s=30.0)
    before = controller.snapshot()

    controller.set_alveolar_ventilation(7.0)
    controller.set_cardiac_output(6.5)

    after = controller.snapshot()

    assert after.elapsed_s == before.elapsed_s
    assert after.stored_agent_l == pytest.approx(before.stored_agent_l)
    assert after.alveolar_concentration_fraction == pytest.approx(
        before.alveolar_concentration_fraction
    )
    assert after.alveolar_ventilation_l_min == 7.0
    assert after.cardiac_output_l_min == 6.5
    assert after.agent_accounting_passes_validation is True


def test_reset_preserves_all_user_settings() -> None:
    controller = SimulationController(
        circuit_volume_l=5.0,
        fresh_gas_flow_l_min=3.0,
        delivered_concentration_fraction=0.06,
        alveolar_ventilation_l_min=5.5,
        cardiac_output_l_min=6.0,
    )
    controller.start()
    _advance_for(controller, duration_s=30.0)

    controller.reset()

    snapshot = controller.snapshot()

    assert snapshot.is_running is False
    assert snapshot.elapsed_s == 0.0
    assert snapshot.stored_agent_l == 0.0

    assert snapshot.circuit_volume_l == 5.0
    assert snapshot.fresh_gas_flow_l_min == 3.0
    assert snapshot.delivered_concentration_fraction == 0.06
    assert snapshot.alveolar_ventilation_l_min == 5.5
    assert snapshot.cardiac_output_l_min == 6.0
    assert snapshot.agent_accounting_passes_validation is True
