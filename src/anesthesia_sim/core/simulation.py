from dataclasses import dataclass

from anesthesia_sim.core.demo_model import response


@dataclass(slots=True)
class SimulationState:
    """Mutable state for the deterministic demonstration model."""

    time_constant_s: float = 10.0
    elapsed_s: float = 0.0
    response_fraction: float = 0.0

    def __post_init__(self) -> None:
        if self.time_constant_s <= 0:
            raise ValueError("time_constant_s must be positive")
        if self.elapsed_s < 0:
            raise ValueError("elapsed_s must be nonnegative")
        self.response_fraction = response(self.elapsed_s, self.time_constant_s)

    def set_time_constant(self, time_constant_s: float) -> None:
        """Change response speed without resetting simulated time."""
        if time_constant_s <= 0:
            raise ValueError("time_constant_s must be positive")
        self.time_constant_s = time_constant_s
        self.response_fraction = response(self.elapsed_s, self.time_constant_s)

    def advance(self, simulation_step_s: float) -> None:
        """Advance by an explicit amount of simulated time."""
        if simulation_step_s <= 0:
            raise ValueError("simulation_step_s must be positive")
        self.elapsed_s += simulation_step_s
        self.response_fraction = response(self.elapsed_s, self.time_constant_s)

    def reset(self) -> None:
        self.elapsed_s = 0.0
        self.response_fraction = 0.0
