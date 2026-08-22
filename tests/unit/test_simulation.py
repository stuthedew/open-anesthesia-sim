import pytest

from anesthesia_sim.core.simulation import SimulationState


def test_advance_uses_explicit_time_step() -> None:
    state = SimulationState(time_constant_s=10.0)

    state.advance(2.5)

    assert state.elapsed_s == pytest.approx(2.5)
    assert 0.0 < state.response_fraction < 1.0


def test_changing_time_constant_recomputes_current_response() -> None:
    state = SimulationState(time_constant_s=10.0, elapsed_s=10.0)
    original_response = state.response_fraction

    state.set_time_constant(20.0)

    assert state.elapsed_s == pytest.approx(10.0)
    assert state.response_fraction < original_response


def test_reset_restores_origin() -> None:
    state = SimulationState()
    state.advance(1.0)

    state.reset()

    assert state.elapsed_s == pytest.approx(0.0)
    assert state.response_fraction == pytest.approx(0.0)


@pytest.mark.parametrize("simulation_step_s", [0.0, -0.1])
def test_rejects_nonpositive_time_step(
    simulation_step_s: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="simulation_step_s must be positive",
    ):
        SimulationState().advance(simulation_step_s)


@pytest.mark.parametrize("time_constant_s", [0.0, -1.0])
def test_rejects_nonpositive_time_constant(
    time_constant_s: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="time_constant_s must be positive",
    ):
        SimulationState(time_constant_s=time_constant_s)


def test_rejects_negative_initial_elapsed_time() -> None:
    with pytest.raises(
        ValueError,
        match="elapsed_s must be nonnegative",
    ):
        SimulationState(elapsed_s=-1.0)
