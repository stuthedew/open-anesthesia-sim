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

Both fields are checked at every write to them, in `__setattr__`, so the
clock can be moved only to a count and a step the simulator checked: by the
constructor, by `advance()` and `reset()`, and by an assignment made past
them, which `mypy --strict` refuses in `src/` and which a test, a notebook or
a value typed `Any` can still make (`PL-8W1W`).

It deliberately re-exports nothing. `circuit`, `alveoli` and `patient` were
properties here as well as attributes of the system, which gave every
compartment two reachable paths and this class a facade that only shortened
a name rather than expressing an intention. Callers reach
`uptake_system.circuit` (PL-006).
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
    """Refuse a count and a step no supported run could be standing at.

    The relation between the two fields of `SimulationState`, which holds both
    and so is the record to check it (`.claude/rules/core-domain.md`): each was
    checked for what it is alone when it was built, and what is left is
    whether the count has a step to multiply by and whether their product is
    inside the supported run length. `SimulationState.__setattr__` asks it at
    every write to either field.

    Raises:
        SimulationConfigurationError: the count is past zero with no step to
            multiply it by, or the two put the run past the supported run
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
    """Own elapsed time and the complete agent uptake simulation."""

    uptake_system: AgentUptakeSystem = field(default_factory=AgentUptakeSystem.default)
    step_count: StepCount = StepCount(0)
    """How many simulation steps this run has completed.

    A `StepCount`, so whole and nonnegative by construction; whether the
    count fits inside the supported run length depends on the step below, so
    `__setattr__` checks the pair at every write to either.
    """
    simulation_step_s: SimulationStep | None = None
    """The step every one of those steps was taken at, or `None` before the
    first one.

    Set by the first `advance()` and cleared only by `reset()`, so a run has
    one cadence for its whole length. A state constructed part-way through a
    run has to say what step it reached its count at: the count alone does
    not carry a time.
    """

    if not TYPE_CHECKING:  # pragma: no branch - TYPE_CHECKING is False at run time
        # Hidden from `mypy` on purpose. A class that defines `__setattr__` is
        # one `mypy` lets assign any attribute name, typed by the method's
        # `value`, so with the guard in view a misspelt field written in `src/`
        # would pass `--strict` and fail at run time against the slots. Hidden,
        # `mypy` reads the dataclass's fields and their types as before, and
        # this is the runtime half for the callers it does not read; its lines
        # are checked by their tests rather than by `mypy`, as the
        # compartments' guards are (`PL-LBQY`, found at review).

        def __setattr__(self, name: str, value: object) -> None:
            """Write a field, refusing a count or a step no supported run could be standing at.

            The run's clock is the count times the step, so these two fields
            are where it is kept, and this is where what is kept is checked,
            for every writer at once: the constructor, `advance()`, `reset()`,
            and an assignment made past them by a caller `mypy` does not read
            - a test, a notebook, a value typed `Any`. Until `PL-8W1W` only
            the constructor checked the pair, in a `__post_init__` this guard
            replaces: a fresh state took a bare count of 5 and read 0 s; one
            step on, it took a bare `float` step of 0.5 s, five times the
            largest supported, and its clock read 3.0 s for a system advanced
            0.1 s; a count of -3 was then taken and refused only when
            `elapsed_s` was next read, as a run-length error naming an instant
            nobody handed in. Nothing is written when a value is refused, so
            the field holds what it held.

            Each field is checked for its type, and the pair for the relation
            `_require_a_run_could_stand_at` states: a count past zero with no
            step to multiply it by, or a pair past the supported run length. So
            a state built part-way through a run - which a branch always is,
            since it continues its parent's count - is refused where it is
            built rather than by its first `advance()`, until which a snapshot,
            a readout or a chart axis would present it as an ordinary run
            (`PL-BMY5`). A count exactly at the limit is accepted, because a
            run may stand there; it is the step from it that `advance()`
            refuses. The constructor writes the count before the step, as a
            copy or a pickle restoring the slots does, so the count's first
            write has no step yet to check the pair against and is checked for
            its type alone; the step's write that follows checks the pair, and
            every write after it does. `dataclasses.replace`, a copy and a
            pickle write through this path too, the last two because this is a
            `slots=True` dataclass, whose state a copy or a pickle restores one
            field at a time through `__setattr__` where a `__dict__` would be
            updated past it.

            The pair is all the write checks beyond the types. A checked count
            inside the run length, or a checked step, is written whoever
            writes it: that a run keeps the step it took its first step at is
            a relation between a step offered and the step held, and stays
            `advance()`'s own.

            Raises:
                TypeError: `name` is `step_count` and `value` was not built as
                    a `StepCount`, or `name` is `simulation_step_s` and `value`
                    is neither `None` nor built as a `SimulationStep`, so
                    nothing has checked it (`core/supported_ranges.py`,
                    `core/simulation_step.py`).
                SimulationConfigurationError: the count would be past zero
                    with no step to multiply it by, or the pair would put the
                    run past the supported run length,
                    `core/supported_ranges.py`'s
                    `require_supported_step_count`.
            """

            if name == "step_count":
                require_step_count(value)

                if hasattr(self, "simulation_step_s"):
                    _require_a_run_could_stand_at(value, self.simulation_step_s)
            elif name == "simulation_step_s":
                if value is not None:
                    require_simulation_step(value)

                _require_a_run_could_stand_at(self.step_count, value)

            super().__setattr__(name, value)

    @property
    def elapsed_s(self) -> CaseInstant:
        """Simulated time reached, in seconds: the steps taken times the step.

        One multiplication, rounded once, rather than a sum rounded at every
        step, so the value depends on how far the run has gone and not on the
        arithmetic that got it there.

        Built as a `CaseInstant` here, where the product becomes an instant of
        the case, because it is the instant a run's definition is moved to and
        a mark is crossed at. It is never refused: `__setattr__` holds the
        pair to `maximum_step_count` at every write to either field, and
        `advance` refuses the step that would pass it, both decided on this
        same product (`PL-8H2R`), so the product is inside the supported run
        length whenever the state is one a run could stand in.
        """

        if self.simulation_step_s is None:
            return CaseInstant(0.0)

        return CaseInstant(self.step_count * self.simulation_step_s)

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
        self.step_count = StepCount(self.step_count + 1)

        return result

    def reset(self) -> None:
        """Clear dynamic state while preserving user settings.

        The count is cleared before the step: zero steps of the held step is
        inside the span, and a count of zero needs no step, where clearing the
        step first would leave a count past zero with none, which
        `__setattr__` refuses.
        """

        self.step_count = StepCount(0)
        self.simulation_step_s = None
        self.uptake_system.reset()
