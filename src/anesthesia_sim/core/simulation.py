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

Each step's state is stored, one for each second, in `stored_states`
(`core/stored_states.py`). The clock and that record move together: a step
stores its state and then moves the count, and a count that the record has
not reached is refused. So every second the clock has passed has exactly one
stored state, and everything that shows or tests a state of the run reads it
there (`PL-MH9J`).

The class deliberately exposes none of the uptake system's attributes as its
own. `circuit`, `alveoli` and `patient` used to be properties here as well as
attributes of the system. That gave every compartment two access paths. It
also gave this class a facade that only shortened a name and expressed no
intention. Callers use `uptake_system.circuit` (PL-006).
"""

from dataclasses import InitVar, dataclass, field
from typing import TYPE_CHECKING

from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.simulation_step import SIMULATION_STEP_S
from anesthesia_sim.core.stored_states import StoredStates
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
    opening_state: InitVar[tuple[float, ...] | None] = None
    """The state to store for the second the run opens at, or None to read it from the system.

    A branch passes the state that its parent stored for the fork, so that
    the branch's first stored state is its parent's, bit for bit. A fraction
    read back from a compartment can differ in its last bit from the fraction
    that was written to it, because the compartment holds an amount. A state
    is accepted only where writing it would leave `uptake_system` exactly as
    it is (`AgentUptakeSystem.stands_at`).
    """
    stored_states: StoredStates = field(init=False)
    """The state of every second from the run's opening to `elapsed_s`.

    It is built with the state and never replaced. `advance()` appends to it,
    and `reset()` restarts it.
    """

    def __post_init__(self, opening_state: tuple[float, ...] | None) -> None:
        """Open the record of stored states at the second the run opens at.

        Raises:
            SimulationConfigurationError: `opening_state` is not a state that
                the equations can be applied to, or `uptake_system` does not
                stand at it.
        """

        if opening_state is None:
            opening_state = self.uptake_system.case_state()
        elif not self.uptake_system.stands_at(opening_state):
            raise SimulationConfigurationError(
                "the opening state is not the state the uptake system stands at, so the "
                "run's first stored state would describe another system: place the system "
                "with AgentUptakeSystem.resume_at, and pass the same state"
            )

        self.stored_states = StoredStates(opening_state, self.elapsed_s)

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

            The stored states are written once too, and the count is held
            to them (`PL-MH9J`). Once the state has its record, a count is
            accepted only where it is the second that the record has reached.
            `advance()` and `reset()` change the record first and the count
            second, so each of their writes passes. A count written by any
            other caller would leave a second with no stored state, or a
            stored state past the clock, and is refused. The record itself is
            accepted only where it reaches the count the state holds. A copy
            and a pickle restore the count before the record, so both pass.

            Raises:
                TypeError: `name` is `step_count` and `value` was not built as
                    a `StepCount`, so nothing has checked it
                    (`core/supported_ranges.py`).
                SimulationConfigurationError: the count would put the run past
                    the supported run length, as checked by
                    `require_supported_step_count` in `core/supported_ranges.py`.
                    Or the count is not the second that the stored states have
                    reached. Or `name` is `uptake_system` or `stored_states`
                    and the state already has one. Or the stored states do not
                    reach the count the state holds.
            """

            if name == "step_count":
                require_step_count(value)
                require_supported_step_count(value)

                if hasattr(self, "stored_states"):
                    _require_count_the_record_reaches(value, self.stored_states)
            elif name == "uptake_system" and hasattr(self, name):
                raise SimulationConfigurationError(
                    "the run's uptake system cannot be replaced once the run's state is "
                    "built, because the step count says how far that system has been "
                    "advanced: build a new state for the new system"
                )
            elif name == "stored_states":
                if hasattr(self, name):
                    raise SimulationConfigurationError(
                        "the run's stored states cannot be replaced once the run's state is "
                        "built, because they are the record of the steps the run took: build "
                        "a new state"
                    )

                if isinstance(value, StoredStates):
                    _require_count_the_record_reaches(self.step_count, value)

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

        The step's state is stored before the count moves, so the record
        always reaches the clock. If the record refuses the state, the system
        is put back as it was before the step, and the count does not move.
        The record refuses only a state that the equations cannot be applied
        to, which a completed step does not produce.

        Raises:
            SimulationDomainLimitError: the run has reached the supported run
                length.
            SimulationNumericalError: `AgentUptakeSystem.advance()` could not
                complete the step, and has rolled it back.
            SimulationConfigurationError: the record of stored states refused
                the step's state (`StoredStates.append`). The step was rolled
                back.
        """

        require_supported_run_length(self.step_count)

        state_before_step = self.uptake_system.capture_state()
        result = self.uptake_system.advance()
        stored = False

        try:
            self.stored_states.append(result.state)
            stored = True
        finally:
            if not stored:
                self.uptake_system.restore_state(state_before_step)

        self.step_count = StepCount(self.step_count + 1)

        return result

    def reset(self) -> None:
        """Clear dynamic state while preserving user settings.

        The run starts over from the case's opening, so its stored states
        start over too, from the state of the reset system at second 0.
        """

        self.uptake_system.reset()
        self.stored_states.restart_from(self.uptake_system.case_state(), CaseInstant(0))
        self.step_count = StepCount(0)


def _require_count_the_record_reaches(step_count: object, stored_states: StoredStates) -> None:
    """Refuse a step count that is not the second the stored states have reached.

    Raises:
        SimulationConfigurationError: the count, as an instant of the case,
            is not `stored_states.reached_s`.
    """

    if step_count != stored_states.reached_s // SIMULATION_STEP_S:
        raise SimulationConfigurationError(
            f"the run's clock cannot be moved to step {step_count}, because the run stores "
            f"one state for each second up to {stored_states.reached_s} s: only a step "
            "moves the clock, and it stores its state first"
        )
