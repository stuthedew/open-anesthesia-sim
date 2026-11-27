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

from __future__ import annotations

from enum import Enum


class AnesthesiaSimulationError(Exception):
    """Base exception for errors raised by the simulation project."""


class SimulationConfigurationError(AnesthesiaSimulationError):
    """Raised when a value handed to the core is invalid or inconsistent.

    The shared guards in `core/validation.py`, the compartment constructors
    and setters, and the parameter-file loaders raise it. The error is
    detected before any state changes, so the caller can correct the value
    and carry on.
    """


class SettingLimit(Enum):
    """Which limit refused a setting, so that a reader of the refusal can be told in its own words.

    Members:
        SUPPORTED_INPUT_RANGE: The range of a flow over which the model is
            claimed to represent a patient (`core/supported_ranges.py`).
        PERCENT: The range that any percent of one atmosphere takes, 0 to 100
            (`core/concentration.py`).
        VAPORIZER_MAXIMUM: The highest concentration that the vaporizer of the
            running agent delivers (`core/validation.py`).
        MACHINE_RANGE: The fresh gas flows that the anesthesia machine in use
            can set (`core/circuit.py`).
    """

    SUPPORTED_INPUT_RANGE = "the model's supported input range"
    PERCENT = "the range of a percent"
    VAPORIZER_MAXIMUM = "the vaporizer's maximum"
    MACHINE_RANGE = "the machine's range"


class SettingOutsideRange(SimulationConfigurationError):
    """Raised when a setting lies outside the range that one limit allows.

    The message is written for a developer. It names the value by its field
    name in the code and says where the limit is documented. The interface
    shows a user a sentence of its own instead, which names the control by
    its label on screen. So the field refused, the value, the limit and which
    limit refused it travel with the error as fields, and the interface builds
    that sentence from them rather than from the message (`PL-8QFW`).

    The fields are keyword arguments that the constructor requires, so the
    error cannot be built from its message alone, as Python rebuilds an
    exception when it is copied or pickled, or as a caller that rewords a
    refusal builds `type(refusal)(message)`. `__reduce__` rebuilds it with its
    fields, and `reworded` gives a caller the copy with a new message.
    """

    def __init__(
        self,
        message: str,
        *,
        quantity: str,
        requested: float,
        lowest: float,
        highest: float,
        limit: SettingLimit,
    ) -> None:
        """Build the error.

        Args:
            message: The refusal, for a developer.
            quantity: The name of the field that refused the value, as the
                message names it, such as `"cardiac_output_l_min"`.
            requested: The value that was refused, in the unit of that field.
            lowest: The lowest value the limit allows, in the same unit.
            highest: The highest value the limit allows, in the same unit.
            limit: Which limit refused the value.
        """

        super().__init__(message)
        self.quantity = quantity
        self.requested = requested
        self.lowest = lowest
        self.highest = highest
        self.limit = limit

    def reworded(self, message: str) -> SettingOutsideRange:
        """Return this refusal with `message` in place of its own, and every field kept."""

        return SettingOutsideRange(
            message,
            quantity=self.quantity,
            requested=self.requested,
            lowest=self.lowest,
            highest=self.highest,
            limit=self.limit,
        )

    def __reduce__(self) -> tuple[object, ...]:
        """Rebuild the error with its fields when it is copied or pickled."""

        return (_rebuilt_setting_outside_range, (str(self), *self._fields()), self.__dict__)

    def _fields(self) -> tuple[object, ...]:
        return (self.quantity, self.requested, self.lowest, self.highest, self.limit)


def _rebuilt_setting_outside_range(
    message: str,
    quantity: str,
    requested: float,
    lowest: float,
    highest: float,
    limit: SettingLimit,
) -> SettingOutsideRange:
    """Rebuild a copied or pickled `SettingOutsideRange` through its constructor."""

    return SettingOutsideRange(
        message, quantity=quantity, requested=requested, lowest=lowest, highest=highest, limit=limit
    )


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
    has a defect, because `docs/INTERFACE.md` § "Supported run length" requires
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
    This argument does not bound a fraction from above. Rounding can carry a
    fraction just above 1 from a state already at 1. Since `PL-9B1M`, no
    supported setting or opening state reaches a fraction of 1, because the
    coupled model's inputs stop at 0.99. But a state handed to `resume_at` or
    to `predicted_states` is checked only against the range 0 through 1, so it
    can still hold a fraction of 1. This error is raised for such a state,
    whether the fraction is computed by a step or by a prediction.

    It is also raised for a model extension whose matrix is not a pure
    transfer system, that is, a matrix with an off-diagonal entry that is not
    a transfer rate. `docs/VERIFICATION.md` § "Step atomicity" states that
    limit (`PL-PM67`).

    `AgentUptakeSystem.advance` also raises this error when a step cannot
    build the settings record from which it builds its propagator. The
    exception that the record raised is attached as the cause.
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
        core. Every core module imports this one, so importing the check's type
        here would make an import cycle. `agent_simulation_validation.rejected_check`
        gives the check back its type.

        Args:
            message: What failed, with the rejected step's totals.
            check: The failing `AgentSimulationValidationResult` of the rejected
                step, or `None` where the error was raised without one.
        """

        super().__init__(message)
        self.check = check
