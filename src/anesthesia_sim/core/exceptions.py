"""Exception hierarchy for errors raised by the simulation core.

The core raises every failure it detects as a subclass of
`AnesthesiaSimulationError`. Such a failure may be a rejected argument, a
violated numeric guard, or a step whose numerical method broke down. A caller
can therefore catch every simulation failure as one type, and can tell it
apart from a programming error (`TypeError`, `AttributeError`, ...) that
happens to pass through the same call.

`AnesthesiaSimulationError` deliberately does **not** inherit from
`ValueError`. Inheriting from it would be the smaller change, but it would
defeat the purpose in two ways. First, a bare `ValueError` raised by a core
guard would still not be an `AnesthesiaSimulationError`, so the caller still
could not make the distinction it needs. Second, Pydantic treats a
`ValueError` raised inside a validator as a validation failure. A project
exception that was also a `ValueError` could then be silently absorbed into a
`ValidationError` by `core/parameters.py`, instead of reaching the caller as
itself.

The two branches below mean different things to a caller, and the interface
acts on the difference:

- `SimulationConfigurationError` means that a value was rejected before it
  could be simulated. Nothing has been miscalculated. The requested setting
  did not take effect, and the run, if there is one, can still be trusted.
- `SimulationExecutionError` means that the run must stop rather than
  continue. Whatever the cause, the model holds the state of the last
  completed step. Usually the cause is a step that had already begun and
  could not be completed. `AgentUptakeSystem.advance()` rolls that step back
  before raising. The stored values are then a real solution of the model,
  not an artifact of how far into the step the operators got. The run must
  still stop, because the same step would fail again.
- `SimulationDomainLimitError` is a subclass of `SimulationExecutionError`.
  It is the one case in which nothing went wrong. The run reached the end of
  what the model claims to represent, and the step that would have crossed
  that boundary was refused before it began. The run stops for a different
  reason, and the interface must say so in different words.
"""


class AnesthesiaSimulationError(Exception):
    """Base exception for errors raised by the simulation project."""


class SimulationConfigurationError(AnesthesiaSimulationError):
    """Raised when a value handed to the core is invalid or inconsistent.

    The shared guards in `core/validation.py`, the compartment constructors
    and setters, and the parameter-file loaders raise it. The error is
    detected before any state changes, so the caller can correct the value
    and carry on.
    """


class SimulationExecutionError(AnesthesiaSimulationError):
    """Raised when a running simulation cannot continue safely.

    Either a step that had begun could not be completed, or a caller asked a
    halted run to continue. When a step failed, `AgentUptakeSystem.advance()`
    rolls it back before raising. The state left behind is then the last
    completed step rather than a partly applied one. The run still has to
    stop.
    """


class SimulationDomainLimitError(SimulationExecutionError):
    """Raised when a run reaches a declared limit of the supported domain.

    Today that limit is the supported run length. `core/supported_ranges.py`
    refuses the step that would take the elapsed simulated time past
    `MAXIMUM_ELAPSED_SIMULATION_TIME_S`.

    **Nothing failed, and that distinction is the reason the class exists.**
    The inputs were valid and the step was never attempted. Every value the
    model holds comes from a completed step, at a simulated time inside the
    supported span. What has ended is the claim that a further step would
    represent a patient. Refusing that step is the same kind of act as
    `require_supported_cardiac_output` refusing 1000 L/min. The difference is
    that this refusal arrives in the middle of a run, because a run length is
    something the run reaches, not a value that is set.

    It is still a `SimulationExecutionError`, because the run must stop.
    There is no value to correct, and the next step would be refused in the
    same way. So the description of `SimulationConfigurationError`, "the
    requested setting did not take effect and the run carries on", does not
    fit it. Placing it under the execution branch also makes the default
    safe. A caller that knows only the base classes stops the run, which is
    correct. Only a caller that catches this type specifically needs to know
    that stopping here is not a fault. A caller that presents it as a fault
    has a defect, because `docs/MODEL.md` § "Supported run length" requires
    the screen to tell the two apart.
    """


class SimulationNumericalError(SimulationExecutionError):
    """Raised when a numerical invariant is violated.

    It differs from `SimulationConfigurationError` in that the inputs were
    valid. The step itself produced a state that the model cannot represent,
    such as a negative compartment amount or a fraction outside zero through
    one.

    The shipped propagator cannot drive a fraction below zero at any step
    size. The system matrix is a Metzler matrix: every entry off its diagonal
    is nonnegative. So the matrix exponential is nonnegative in every entry.
    That argument says nothing about the upper bound. Rounding can carry a
    fraction just above 1 from a state already at 1, and that state needs a
    100% dial that no supported setting reaches. The error covers that state.
    It also covers a model extension whose matrix is not a pure transfer
    system, meaning a matrix with an off-diagonal entry that is not a transfer
    rate. `docs/MODEL.md` § "Supported simulation step" says so (`PL-PM67`).

    `AgentUptakeSystem.advance` also raises this error when the settings
    record from which a step builds its propagator cannot be built. The
    record's own refusal is attached as the cause.
    """


class AgentSimulationValidationError(SimulationNumericalError):
    """Raised when delivered agent cannot be fully accounted for.

    `AgentUptakeSystem.advance()` rolls the step back before this error reaches a
    caller. The run's own accounting then holds the last completed step's totals,
    which passed their check. So the failing check travels with the error, as
    `check`, and the interface shows the rejected step's verdict and totals from
    it (`PL-HF4B`).
    """

    def __init__(self, message: str, *, check: object = None) -> None:
        """Build the error.

        `check` is typed `object` because this module imports nothing from the
        core. Every core module imports this one, so an import of the check's
        type here would make a cycle. `agent_simulation_validation.rejected_check`
        reads the check back as its own type.

        Args:
            message: What failed, with the rejected step's totals.
            check: The failing `AgentSimulationValidationResult` of the rejected
                step, or `None` where the error was raised without one.
        """

        super().__init__(message)
        self.check = check
