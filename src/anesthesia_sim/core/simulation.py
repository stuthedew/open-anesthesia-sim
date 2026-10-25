"""The simulation state keeps elapsed simulated time beside the agent uptake system.

SimulationState keeps simulated time as explicit, deterministic state, rather
than deriving it from the wall clock (see CLAUDE.md's architecture
discipline).

Time is stored as a count of steps taken. It is read back as that count times
the run's step size. It is never accumulated by adding one step at a time.
The reason is not accuracy. Over a four-hour run the two methods disagree by
nanoseconds, and a running sum of tenths is sometimes the closer decimal
approximation of the two. The reason is that a product depends on nothing but
how far the run has gone. A sum also depends on the order and number of the
additions that produced it. Ten steps of 0.1 s sum to 0.9999999999999999 but
multiply to 1.0. So two runs given identical inputs record identical instants,
whatever the machine did between the steps. A replayed or forked run is
compared with the original element by element, and that comparison relies on
this property (PL-VM40).

A run takes one step size and keeps it. `advance()` rejects a different step
size rather than computing a time from a mixture of sizes. The reason is that
`elapsed_s` multiplies the count by a single step size, which is correct only
if the run has used just one. The run no longer records samples at all
(`PL-2FM6`), so the functions that used to convert between a sample index and
a time are gone too. What remains is the step count, which stands for a time,
and `elapsed_s`, which returns that time.

The step count and the step size are checked at every write, in
`__setattr__`. So the clock can be moved only to a count and a step that the
simulator has checked. Writes come from the constructor, from `advance()` and
`reset()`, and from a direct assignment that bypasses those methods.
`mypy --strict` rejects such an assignment in `src/`, but a test, a notebook
or a value typed `Any` can still make one (`PL-8W1W`). The uptake system whose
steps the clock counts is written once, when the state is built. A later write
to it is refused (`PL-N7MM`).

The class deliberately exposes none of the uptake system's attributes as its
own. `circuit`, `alveoli` and `patient` used to be properties here as well as
attributes of the system. That gave every compartment two access paths. It
also gave this class a facade that only shortened a name and expressed no
intention. Callers use `uptake_system.circuit` (PL-006).
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.simulation_step import SimulationStep, require_simulation_step
from anesthesia_sim.core.supported_ranges import (
    CaseInstant,
    StepCount,
    describe_count,
    require_step_count,
    require_supported_run_length,
    require_supported_step_count,
)
from anesthesia_sim.core.uptake_system import AgentUptakeSystem, UptakeStepResult


def _require_a_run_could_stand_at(
    step_count: StepCount, simulation_step_s: SimulationStep | None
) -> None:
    """Refuse a step count and a step that no supported run could be at.

    This checks the relation between the two fields of `SimulationState`. That
    class holds both fields, so it is the record on which to check the relation
    (`.claude/rules/core-domain.md`). Each field was checked on its own when it
    was built. What remains is whether the count has a step to multiply by,
    and whether their product lies inside the supported run length.
    `SimulationState.__setattr__` calls this function at every write to either
    field.

    Raises:
        SimulationConfigurationError: the count is greater than zero with no
            step to multiply it by, or the two put the run past the supported run
            length, `core/supported_ranges.py`'s
            `require_supported_step_count`.
    """

    if simulation_step_s is not None:
        require_supported_step_count(step_count, simulation_step_s)
    elif step_count > 0:
        raise SimulationConfigurationError(
            f"step_count is {describe_count(step_count)} but no simulation_step_s was "
            "given, so the simulated time those steps reached is unknown"
        )


@dataclass(slots=True)
class SimulationState:
    """Owns the elapsed simulated time and the complete agent uptake simulation."""

    uptake_system: AgentUptakeSystem = field(default_factory=AgentUptakeSystem.default)
    step_count: StepCount = StepCount(0)
    """How many simulation steps this run has completed.

    It is a `StepCount`, so it is whole and nonnegative by construction.
    Whether the count fits inside the supported run length depends on the step
    below. So `__setattr__` checks the pair at every write to either field.
    """
    simulation_step_s: SimulationStep | None = None
    """The step at which every one of those steps was taken, or `None` before the first step.

    The first `advance()` sets it, and only `reset()` clears it, so a run has
    one cadence for its whole length. A state constructed part-way through a
    run must say at what step it reached its count, because the count alone
    does not give a time.
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
            """Write a field, refusing a step count or step size that no supported run could have.

            The run's clock is the step count times the step size, so these two
            fields hold the clock. This method checks every value written to
            them, whoever writes it. The writers are the constructor,
            `advance()` and `reset()`. A direct assignment can also bypass
            those methods, from a caller that `mypy` does not check, such as a
            test, a notebook or a value typed `Any`. Until `PL-8W1W`, only the
            constructor checked the pair, in a `__post_init__` that this guard
            replaces. A fresh state accepted a plain count of 5 that was not
            built as a `StepCount`, and its clock read 0 s. One step later, it
            accepted a plain `float` step of 0.5 s, five times the largest
            supported step. Its clock then read 3.0 s for a system advanced
            0.1 s. A count of -3 was then accepted. It was rejected only when
            `elapsed_s` was next read, as a run-length error that named an
            instant nobody had passed in. Nothing is written when a value is
            rejected, so the field keeps the value it had.

            Each field is checked for its type. The pair is checked against
            `_require_a_run_could_stand_at`. That check rejects a count greater
            than zero with no step to multiply it by. It also rejects a pair
            that would put the run past the supported run length. So an invalid
            state built part-way through a run is rejected where it is built,
            not at its first `advance()`. A branch is always built part-way
            through a run, because it continues its parent's count. If such a
            state were rejected only at its first `advance()`, a snapshot, a
            readout or a chart axis would present it as an ordinary run until
            then (`PL-BMY5`). A count exactly at the limit is accepted, because
            a run may be at the limit. `advance()` rejects the next step from
            there.

            The constructor writes the count before the step. A copy or a
            pickle does the same when it restores the slots. So the count's
            first write has no step yet to check the pair against, and only its
            type is checked. The write of the step that follows checks the
            pair, and so does every write after it. `dataclasses.replace`, a
            copy and a pickle also write through this method. A copy and a
            pickle do so because this is a `slots=True` dataclass. They restore
            the state of such a dataclass one field at a time through
            `__setattr__`. For a class with a `__dict__`, they would update the
            `__dict__` directly and bypass `__setattr__`.

            Apart from the types, a write of either field checks only the pair.
            A count that has passed its own check and lies inside the run
            length is written, whoever writes it. So is a step that has passed
            its own check. This method does not enforce the rule that a run
            keeps the step size of its first step. That rule compares the step
            offered with the step stored, so it stays the job of `advance()`.

            The uptake system is written once, when the state is built. The
            count and the step say how far that system has been advanced. If
            another system were written in its place, the clock would count
            steps that the new system never took, and nothing could detect the
            mismatch. Nothing in `src/` replaces the uptake system, so a later
            write is refused (`PL-N7MM`). The constructor, a copy and a pickle
            write it onto a state that has none yet, so those writes are
            accepted.

            Raises:
                TypeError: `name` is `step_count` and `value` was not built as
                    a `StepCount`, or `name` is `simulation_step_s` and `value`
                    is neither `None` nor built as a `SimulationStep`, so
                    nothing has checked it (`core/supported_ranges.py`,
                    `core/simulation_step.py`).
                SimulationConfigurationError: the count would be greater than
                    zero with no step to multiply it by. Or the pair would put
                    the run past the supported run length, as checked by
                    `require_supported_step_count` in `core/supported_ranges.py`.
                    Or `name` is `uptake_system` and the state already has one.
            """

            if name == "uptake_system":
                if hasattr(self, name):
                    raise SimulationConfigurationError(
                        "the run's uptake system cannot be replaced once the run's state is "
                        "built, because the step count says how far that system has been "
                        "advanced: build a new state for the new system"
                    )
            elif name == "step_count":
                require_step_count(value)

                if hasattr(self, "simulation_step_s"):
                    _require_a_run_could_stand_at(value, self.simulation_step_s)
            elif name == "simulation_step_s":
                if value is not None:
                    require_simulation_step(value)

                _require_a_run_could_stand_at(self.step_count, value)

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
        """Return the simulated time reached, in seconds: the steps taken times the step.

        It is one multiplication, rounded once, rather than a sum rounded at
        every step. So the value depends on how far the run has gone, and not
        on the arithmetic that got it there.

        The product is built as a `CaseInstant` here, where it becomes an
        instant of the case. It is the instant that a run's definition is
        moved to, and the instant at which a mark is crossed. It is never
        rejected. `__setattr__` keeps the pair within `maximum_step_count` at
        every write to either field, and `advance` rejects the step that would
        pass it. Both decisions use this same product (`PL-8H2R`). So the
        product is inside the supported run length whenever the state is one
        that a run could be in.
        """

        if self.simulation_step_s is None:
            return CaseInstant(0.0)

        return CaseInstant(self.step_count * self.simulation_step_s)

    def advance(self, simulation_step_s: SimulationStep) -> UptakeStepResult:
        """Advance the complete system and time as one operation.

        The step is a `SimulationStep`, so it was checked against the
        supported range when it was built. Anything else is rejected here,
        before elapsed time moves, rather than left to
        `AgentUptakeSystem.advance()`, so that this class states its own
        contract. The second check belongs to this class alone. A run keeps
        the step size of its first step, so no recorded history mixes two
        cadences.
        A caller that catches the `SimulationConfigurationError` it raises
        still has a run it can trust.

        The count and the step are recorded after the system has advanced. So
        a step that could not be completed leaves simulated time exactly where
        the last completed step left it.

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
            TypeError: `simulation_step_s` is not a `SimulationStep`
                (`core/simulation_step.py`).
            SimulationConfigurationError: the step differs from the step size
                of this run's first step.
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
        self.step_count = StepCount(self.step_count + 1)

        return result

    def reset(self) -> None:
        """Clear dynamic state while preserving user settings.

        The count is cleared before the step. Zero steps of the stored step is
        inside the span, and a count of zero needs no step. Clearing the step
        first would leave a count greater than zero with no step, which
        `__setattr__` rejects.
        """

        self.step_count = StepCount(0)
        self.simulation_step_s = None
        self.uptake_system.reset()
