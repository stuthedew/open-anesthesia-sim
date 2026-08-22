import pytest

from anesthesia_sim.app.controller import SimulationController


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
    assert snapshot.concentration_history == ((0.0, 0.0),)


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
    assert after.circuit_concentration_fraction == pytest.approx(
        before.circuit_concentration_fraction
    )
    assert after.circuit_volume_l == 5.0
    assert after.fresh_gas_flow_l_min == 3.0
    assert after.delivered_concentration_fraction == 0.06
