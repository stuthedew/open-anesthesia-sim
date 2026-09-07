"""SimulationState: owns elapsed simulation time alongside the agent uptake
system, so simulated time is explicit, deterministic state rather than
derived from the wall clock (see CLAUDE.md's architecture discipline).

Time is held as a count of steps taken and read back as that count times
the step the run is taking, never accumulated one addition at a time. The
difference is not accuracy: over a four-hour run the two disagree by
nanoseconds, and a running sum of tenths is sometimes the closer decimal
approximation of the two. The difference is that a product is an exact
function of how far the run has gone, while a sum is a function of the
order and number of the additions that reached it - ten steps of 0.1 s sum
to 0.9999999999999999 and multiply to 1.0. Two runs given identical inputs
therefore record identical instants, whatever the machine did between the
steps, which is the property a replayed or forked run is compared against
element-wise (PL-VM40).

A run takes one step size and keeps it, and `advance()` refuses a
different one rather than deriving a time from a mixture. `elapsed_s` has
one step to multiply by only if there is one; and a history recorded at two
cadences has a sample spacing that is not a constant of the run, which
every reader that maps between a sample index and a time - a control
change's `sample_index`, a window's sample budget, the chart's grouping by
index - assumes it is.

It deliberately re-exports nothing. `circuit`, `alveoli` and `patient` were
properties here as well as attributes of the system, which gave every
compartment two reachable paths and this class a facade that only shortened
a name rather than expressing an intention. Callers reach
`uptake_system.circuit` (PL-006).
"""

from dataclasses import dataclass, field

from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.supported_ranges import require_supported_run_length
from anesthesia_sim.core.uptake_system import (
    AgentUptakeSystem,
    UptakeStepResult,
    require_supported_simulation_step,
)


def _require_step_count(step_count: int) -> None:
    """Require a whole, nonnegative number of completed steps."""

    if not isinstance(step_count, int) or step_count < 0:
        raise SimulationConfigurationError(
            f"step_count must be a whole, nonnegative number of steps, not {step_count!r}"
        )


@dataclass(slots=True)
class SimulationState:
    """Own elapsed time and the complete agent uptake simulation."""

    uptake_system: AgentUptakeSystem = field(default_factory=AgentUptakeSystem.default)
    step_count: int = 0
    """How many simulation steps this run has completed."""
    simulation_step_s: float | None = None
    """The step every one of those steps was taken at, or `None` before the
    first one.

    Set by the first `advance()` and cleared only by `reset()`, so a run has
    one cadence for its whole length. A state constructed part-way through a
    run has to say what step it reached its count at: the count alone does
    not carry a time.
    """

    def __post_init__(self) -> None:
        _require_step_count(self.step_count)

        if self.simulation_step_s is not None:
            require_supported_simulation_step(self.simulation_step_s)
        elif self.step_count > 0:
            raise SimulationConfigurationError(
                f"step_count is {self.step_count} but no simulation_step_s was given, so the "
                "simulated time those steps reached is unknown"
            )

    @property
    def elapsed_s(self) -> float:
        """Simulated time reached, in seconds: the steps taken times the step.

        One multiplication, rounded once, rather than a sum rounded at every
        step, so the value depends on how far the run has gone and not on the
        arithmetic that got it there.
        """

        if self.simulation_step_s is None:
            return 0.0

        return self.step_count * self.simulation_step_s

    def advance(self, simulation_step_s: float) -> UptakeStepResult:
        """Advance the complete system and time as one operation.

        The step is checked here as well as in `AgentUptakeSystem.advance()`,
        rather than left to it, so that this class states its own contract:
        a step longer than `MAXIMUM_SIMULATION_STEP_S` is refused before
        elapsed time moves, and a caller that catches
        `SimulationConfigurationError` still holds a run it can trust. The
        second check is this class's alone: a run keeps the step it took its
        first step at, so no recorded history mixes two cadences.

        The count and the step are recorded after the system has advanced,
        so a step that could not be completed leaves simulated time exactly
        where the last completed step left it.

        The run length is checked here too, and it is the one guard this
        class could not delegate: the supported span is a limit on elapsed
        simulated time, and `step_count` is the only record of that anywhere
        in `core/`. A compartment advanced on its own has no run length to
        be past the end of, which is why the three flow ranges are enforced
        on the compartments and this is not.

        Raises `SimulationDomainLimitError` when the run has reached the
        supported length. That is not a failure - see
        `core/supported_ranges.py` § `require_supported_run_length` - and
        the step is refused before anything advances, so the state left
        behind is a completed step inside the supported span.
        """

        require_supported_simulation_step(simulation_step_s)

        if self.simulation_step_s is not None and simulation_step_s != self.simulation_step_s:
            raise SimulationConfigurationError(
                f"this run is being taken at {self.simulation_step_s} s per step and cannot "
                f"switch to {simulation_step_s} s; reset it to run at a different step"
            )

        require_supported_run_length(self.step_count, simulation_step_s)

        result = self.uptake_system.advance(simulation_step_s)

        self.simulation_step_s = simulation_step_s
        self.step_count += 1

        return result

    def reset(self) -> None:
        """Clear dynamic state while preserving user settings."""

        self.step_count = 0
        self.simulation_step_s = None
        self.uptake_system.reset()
