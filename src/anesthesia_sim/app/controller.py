from dataclasses import dataclass

from anesthesia_sim.core.simulation import SimulationState


@dataclass(frozen=True, slots=True)
class SimulationSnapshot:
    """Read-only simulation data exposed to the user interface."""

    is_running: bool
    time_constant_s: float
    elapsed_s: float
    response_fraction: float
    response_history: tuple[tuple[float, float], ...]


class SimulationController:
    """Own run controls and response history for one app session."""

    def __init__(self, time_constant_s: float = 10.0) -> None:
        self._state = SimulationState(time_constant_s=time_constant_s)
        self._is_running = False
        self._response_history: list[tuple[float, float]] = [(0.0, 0.0)]

    @property
    def is_running(self) -> bool:
        return self._is_running

    def snapshot(self) -> SimulationSnapshot:
        return SimulationSnapshot(
            is_running=self._is_running,
            time_constant_s=self._state.time_constant_s,
            elapsed_s=self._state.elapsed_s,
            response_fraction=self._state.response_fraction,
            response_history=tuple(self._response_history),
        )

    def start(self) -> None:
        self._is_running = True

    def pause(self) -> None:
        self._is_running = False

    def reset(self) -> None:
        self.pause()
        self._state.reset()
        self._response_history = [(0.0, 0.0)]

    def set_time_constant(self, time_constant_s: float) -> None:
        self._state.set_time_constant(time_constant_s)
        self._response_history[-1] = (
            self._state.elapsed_s,
            self._state.response_fraction,
        )

    def advance(self, simulation_step_s: float) -> None:
        if not self._is_running:
            return

        self._state.advance(simulation_step_s)
        self._response_history.append((self._state.elapsed_s, self._state.response_fraction))
