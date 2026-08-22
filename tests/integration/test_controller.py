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


def test_reset_pauses_and_clears_response_history() -> None:
    controller = SimulationController()
    controller.start()
    controller.advance(0.1)

    controller.reset()

    snapshot = controller.snapshot()
    assert snapshot.is_running is False
    assert snapshot.elapsed_s == 0.0
    assert snapshot.response_fraction == 0.0
    assert snapshot.response_history == ((0.0, 0.0),)


def test_changing_time_constant_updates_current_point_without_reset() -> None:
    controller = SimulationController(time_constant_s=10.0)
    controller.start()
    controller.advance(10.0)
    before = controller.snapshot()

    controller.set_time_constant(20.0)

    after = controller.snapshot()
    assert after.elapsed_s == before.elapsed_s
    assert after.response_fraction < before.response_fraction
    assert after.response_history[-1] == (
        after.elapsed_s,
        after.response_fraction,
    )
