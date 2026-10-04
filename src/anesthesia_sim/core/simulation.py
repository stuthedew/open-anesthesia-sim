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
different one rather than deriving a time from a mixture: `elapsed_s` has
one step to multiply by only if there is one. The run no longer records
samples at all (`PL-2FM6`), so the readers that used to map between a
sample index and a time are gone with it; what remains is that a step count
means a time, which is what `elapsed_s` is.

It deliberately re-exports nothing. `circuit`, `alveoli` and `patient` were
properties here as well as attributes of the system, which gave every
compartment two reachable paths and this class a facade that only shortened
a name rather than expressing an intention. Callers reach
`uptake_system.circuit` (PL-006).
"""

from dataclasses import dataclass, field

from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.simulation_step import SimulationStep, require_simulation_step
from anesthesia_sim.core.supported_ranges import (
    require_supported_run_length,
    require_supported_step_count,
)
from anesthesia_sim.core.uptake_system import AgentUptakeSystem, UptakeStepResult


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
    simulation_step_s: SimulationStep | None = None
    """The step every one of those steps was taken at, or `None` before the
    first one.

    Set by the first `advance()` and cleared only by `reset()`, so a run has
    one cadence for its whole length. A state constructed part-way through a
    run has to say what step it reached its count at: the count alone does
    not carry a time.
    """

    def __post_init__(self) -> None:
        """Refuse a state no supported run could be standing in.

        A state built part-way through a run - which a branch always is, since
        it continues its parent's count - is checked against the supported run
        length here, where it is built, rather than by its first `advance()`:
        until then a snapshot, a readout or a chart axis would present it as an
        ordinary run (`PL-BMY5`). A count exactly at the limit is accepted,
        because a run may stand there; it is the step from it that is refused.

        Raises:
            TypeError: `simulation_step_s` is neither `None` nor a
                `SimulationStep`, so nothing has checked it against the
                supported range (`core/simulation_step.py`).
            SimulationConfigurationError: `step_count` is not a whole,
                nonnegative number; the count is past zero with no step to
                multiply it by; or the two put the run past the supported run
                length, `core/supported_ranges.py`'s
                `require_supported_step_count`.
        """

        _require_step_count(self.step_count)

        if self.simulation_step_s is not None:
            require_simulation_step(self.simulation_step_s)
            require_supported_step_count(self.step_count, self.simulation_step_s)
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

    def advance(self, simulation_step_s: SimulationStep) -> UptakeStepResult:
        """Advance the complete system and time as one operation.

        The step is a `SimulationStep`, so it was checked against the
        supported range when it was built, and anything else is refused here
        before elapsed time moves rather than left to
        `AgentUptakeSystem.advance()`, so that this class states its own
        contract. The second check is this class's alone: a run keeps the
        step it took its first step at, so no recorded history mixes two
        cadences, and a caller that catches the
        `SimulationConfigurationError` it raises still holds a run it can
        trust.

        The count and the step are recorded after the system has advanced,
        so a step that could not be completed leaves simulated time exactly
        where the last completed step left it.

        The run length is checked here too, and it is the one guard this
        class could not delegate: the supported span is a limit on elapsed
        simulated time, which this class counts in `step_count`. A
        compartment advanced on its own has no run length to be past the end
        of, which is why the three flow ranges are enforced on the
        compartments and this is not.

        Raises `SimulationDomainLimitError` when the run has reached the
        supported length. That is not a failure - see
        `core/supported_ranges.py` § `require_supported_run_length` - and
        the step is refused before anything advances, so the state left
        behind is a completed step inside the supported span.

        Raises:
            TypeError: `simulation_step_s` is not a `SimulationStep`
                (`core/simulation_step.py`).
            SimulationConfigurationError: the step differs from the one this
                run took its first step at.
            SimulationDomainLimitError: the run has reached the supported run
                length.
            SimulationNumericalError: `AgentUptakeSystem.advance()` could not
                complete the step, and has rolled it back.
        """

        require_simulation_step(simulation_step_s)

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
