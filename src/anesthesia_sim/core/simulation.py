"""The simulation state keeps elapsed simulated time beside the agent uptake system.

SimulationState keeps simulated time as explicit, deterministic state, rather
than deriving it from the wall clock (see CLAUDE.md's architecture
discipline).

Time is stored as a count of steps taken. Each step is one second
(`core/simulation_step.py`), so the count is the simulated time in seconds,
and `elapsed_s` returns it as an instant of the case. Both are whole numbers.
So two runs given identical inputs record identical instants, and a replayed
or forked run is compared with the original element by element (`PL-VM40`,
`PL-SZ6G`). Until `PL-SZ6G` the step was a tenth of a second and the time was
the count times the step, a rounded product.

The step count is checked at every write, in `__setattr__`. So the clock can
be moved only to a count that the simulator has checked. Writes come from the
constructor, from `advance()` and `reset()`, and from a direct assignment that
bypasses those methods. `mypy --strict` rejects such an assignment in `src/`,
but a test, a notebook or a value typed `Any` can still make one (`PL-8W1W`).
The uptake system whose steps the clock counts is written once, when the
state is built. A later write to it is refused (`PL-N7MM`).

The class deliberately exposes none of the uptake system's attributes as its
own. `circuit`, `alveoli` and `patient` used to be properties here as well as
attributes of the system. That gave every compartment two access paths. It
also gave this class a facade that only shortened a name and expressed no
intention. Callers use `uptake_system.circuit` (PL-006).
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.simulation_step import SIMULATION_STEP_S
from anesthesia_sim.core.supported_ranges import (
    CaseInstant,
    StepCount,
    require_step_count,
    require_supported_run_length,
    require_supported_step_count,
)
from anesthesia_sim.core.uptake_system import AgentUptakeSystem, UptakeStepResult


@dataclass(slots=True)
class SimulationState:
    """Owns the elapsed simulated time and the complete agent uptake simulation."""

    uptake_system: AgentUptakeSystem = field(default_factory=AgentUptakeSystem.default)
    step_count: StepCount = StepCount(0)
    """How many simulation steps this run has completed.

    It is a `StepCount`, so it is whole and nonnegative by construction.
    `__setattr__` checks it against the supported run length at every write.
    A state constructed part-way through a run, as a branch is, is built at
    the count its parent stood at.
    """

    if not TYPE_CHECKING:  # pragma: no branch - TYPE_CHECKING is False at run time
        # Hidden from `mypy` on purpose. When a class defines `__setattr__`,
        # `mypy` lets code assign any attribute name, typed by the method's
        # `value` parameter. So with this guard visible, a misspelt field
        # written in `src/` would pass `--strict` and fail at run time against
        # the slots. With the guard hidden, `mypy` checks the dataclass's
        # fields and their types as before. This guard is the runtime check for
        # the callers that `mypy` does not check. Its lines are checked by
        # their tests rather than by `mypy`, as the compartments' guards are
        # (`PL-LBQY`, found at review).

        def __setattr__(self, name: str, value: object) -> None:
            """Write a field, refusing a step count that no supported run could have.

            The run's clock is the step count, so this method checks every
            value written to it, whoever writes it. The writers are the
            constructor, `advance()` and `reset()`. A direct assignment can
            also bypass those methods, from a caller that `mypy` does not
            check, such as a test, a notebook or a value typed `Any`. Until
            `PL-8W1W`, only the constructor checked the count. A fresh state
            accepted a plain count of 5 that was not built as a `StepCount`,
            and a count of -3 after it. Nothing is written when a value is
            rejected, so the field keeps the value it had.

            The count is checked for its type and then against the supported
            run length. So an invalid state built part-way through a run is
            rejected where it is built, not at its first `advance()`. A branch
            is always built part-way through a run, because it continues its
            parent's count. If such a state were rejected only at its first
            `advance()`, a snapshot, a readout or a chart axis would present
            it as an ordinary run until then (`PL-BMY5`). A count exactly at
            the limit is accepted, because a run may be at the limit.
            `advance()` rejects the next step from there.

            `dataclasses.replace`, a copy and a pickle also write through this
            method. A copy and a pickle do so because this is a `slots=True`
            dataclass. They restore the state of such a dataclass one field at
            a time through `__setattr__`. For a class with a `__dict__`, they
            would update the `__dict__` directly and bypass `__setattr__`.

            The uptake system is written once, when the state is built. The
            count says how far that system has been advanced. If another
            system were written in its place, the clock would count steps that
            the new system never took, and nothing could detect the mismatch.
            Nothing in `src/` replaces the uptake system, so a later write is
            refused (`PL-N7MM`). The constructor, a copy and a pickle write it
            onto a state that has none yet, so those writes are accepted.

            Raises:
                TypeError: `name` is `step_count` and `value` was not built as
                    a `StepCount`, so nothing has checked it
                    (`core/supported_ranges.py`).
                SimulationConfigurationError: the count would put the run past
                    the supported run length, as checked by
                    `require_supported_step_count` in `core/supported_ranges.py`.
                    Or `name` is `uptake_system` and the state already has one.
            """

            if name == "step_count":
                require_step_count(value)
                require_supported_step_count(value)
            elif name == "uptake_system" and hasattr(self, name):
                raise SimulationConfigurationError(
                    "the run's uptake system cannot be replaced once the run's state is "
                    "built, because the step count says how far that system has been "
                    "advanced: build a new state for the new system"
                )

            super().__setattr__(name, value)

        def __delattr__(self, name: str) -> None:
            """Refuse to delete any field.

            The checks in `__setattr__` treat a field that the state does not
            have yet as one that the constructor is writing. So a field that was
            deleted and then written again would bypass them. No field of a
            built state is ever meant to be absent, so every deletion is
            refused.

            Raises:
                SimulationConfigurationError: always.
            """

            raise SimulationConfigurationError(
                f"the run's {name} cannot be deleted, because a value written after it "
                "would bypass the checks made when the state is built: build a new state"
            )

    @property
    def elapsed_s(self) -> CaseInstant:
        """Return the simulated time reached, in whole seconds: the steps taken times the step.

        The step is one second, so the product is a whole number and nothing
        is rounded. It is built as a `CaseInstant` here, where it becomes an
        instant of the case. It is the instant that a run's definition is
        moved to, and the instant at which a mark is crossed. It is never
        rejected: `__setattr__` keeps the count within `MAXIMUM_STEP_COUNT` at
        every write, and `advance` rejects the step that would pass it.
        """

        return CaseInstant(self.step_count * SIMULATION_STEP_S)

    def advance(self) -> UptakeStepResult:
        """Advance the complete system and time by one step, as one operation.

        The step is `SIMULATION_STEP_S`, one second, and a caller cannot ask
        for another (`core/simulation_step.py`).

        The count is recorded after the system has advanced. So a step that
        could not be completed leaves simulated time exactly where the last
        completed step left it.

        The run length is checked here too, and it is the one guard that this
        class could not delegate. The supported span is a limit on elapsed
        simulated time, which this class counts in `step_count`. A compartment
        advanced on its own has no run length to exceed. That is why the three
        flow ranges are enforced on the compartments and the run length is
        not.

        Raises `SimulationDomainLimitError` when the run has reached the
        supported length. That is not a failure (see
        `core/supported_ranges.py` § `require_supported_run_length`). The step
        is rejected before anything advances, so the state left behind is a
        completed step inside the supported span.

        Raises:
            SimulationDomainLimitError: the run has reached the supported run
                length.
            SimulationNumericalError: `AgentUptakeSystem.advance()` could not
                complete the step, and has rolled it back.
        """

        require_supported_run_length(self.step_count)

        result = self.uptake_system.advance()

        self.step_count = StepCount(self.step_count + 1)

        return result

    def reset(self) -> None:
        """Clear dynamic state while preserving user settings."""

        self.step_count = StepCount(0)
        self.uptake_system.reset()
