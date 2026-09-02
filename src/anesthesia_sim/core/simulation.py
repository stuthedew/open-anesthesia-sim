"""SimulationState: owns elapsed simulation time alongside the agent uptake
system, so simulated time is explicit, deterministic state rather than
derived from the wall clock (see CLAUDE.md's architecture discipline).

It deliberately re-exports nothing. `circuit`, `alveoli` and `patient` were
properties here as well as attributes of the system, which gave every
compartment two reachable paths and this class a facade that only shortened
a name rather than expressing an intention. Callers reach
`uptake_system.circuit` (PL-006).
"""

from dataclasses import dataclass, field

from anesthesia_sim.core.uptake_system import (
    AgentUptakeSystem,
    UptakeStepResult,
    require_supported_simulation_step,
)
from anesthesia_sim.core.validation import require_nonnegative_finite


@dataclass(slots=True)
class SimulationState:
    """Own elapsed time and the complete agent uptake simulation."""

    uptake_system: AgentUptakeSystem = field(default_factory=AgentUptakeSystem.default)
    elapsed_s: float = 0.0

    def __post_init__(self) -> None:
        require_nonnegative_finite("elapsed_s", self.elapsed_s)

    def advance(self, simulation_step_s: float) -> UptakeStepResult:
        """Advance the complete system and time as one operation.

        The step is checked here as well as in `AgentUptakeSystem.advance()`,
        rather than left to it, so that this class states its own contract:
        a step outside the operator split's applicability domain is refused
        before elapsed time moves, and a caller that catches
        `SimulationConfigurationError` still holds a run it can trust.
        """

        require_supported_simulation_step(simulation_step_s)

        result = self.uptake_system.advance(simulation_step_s)
        self.elapsed_s += simulation_step_s

        return result

    def reset(self) -> None:
        """Clear dynamic state while preserving user settings."""

        self.elapsed_s = 0.0
        self.uptake_system.reset()
