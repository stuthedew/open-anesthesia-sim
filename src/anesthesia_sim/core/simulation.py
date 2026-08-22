from dataclasses import dataclass, field
from math import isfinite

from anesthesia_sim.core.circuit import BreathingCircuit


@dataclass(slots=True)
class SimulationState:
    """Explicit simulation time and the modeled breathing circuit."""

    circuit: BreathingCircuit = field(default_factory=BreathingCircuit)
    elapsed_s: float = 0.0

    def __post_init__(self) -> None:
        if not isfinite(self.elapsed_s) or self.elapsed_s < 0:
            raise ValueError("elapsed_s must be nonnegative and finite")

    def advance(self, simulation_step_s: float) -> None:
        self.circuit.advance(simulation_step_s)
        self.elapsed_s += simulation_step_s

    def reset(self) -> None:
        self.elapsed_s = 0.0
        self.circuit.reset()
