"""Check that a simulation run neither creates nor loses anesthetic agent.

This is mass-balance accounting. It checks the delivered, exhausted and stored
agent against the accounting identity documented on `AgentSimulationValidator`.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from anesthesia_sim.core.exceptions import AgentSimulationValidationError
from anesthesia_sim.core.validation import require_nonnegative_finite

AGENT_ACCOUNTING_ABSOLUTE_TOLERANCE_L = 1e-12
AGENT_ACCOUNTING_RELATIVE_TOLERANCE = 1e-9
MINIMUM_RELATIVE_SCALE_L = 1e-15

#: The three totals that `AgentSimulationValidator.__setattr__` requires to be
#: nonnegative and finite. They are all of the validator's fields.
_ACCOUNTING_TOTALS = frozenset({"initial_agent_l", "delivered_agent_l", "exhausted_agent_l"})


@dataclass(frozen=True, slots=True)
class AgentSimulationValidationResult:
    """Result of checking whether all agent is accounted for."""

    initial_agent_l: float
    delivered_agent_l: float
    exhausted_agent_l: float
    currently_stored_agent_l: float
    unaccounted_agent_l: float
    absolute_error_l: float
    relative_error: float
    passes_validation: bool


@dataclass(frozen=True, slots=True)
class AgentSimulationValidatorState:
    """The validator's run state, which is the three totals of one accounting period.

    All three totals are captured, including `initial_agent_l`. That total is
    the anchor of the current accounting period, not a setting. `reset()`
    writes it, and `reset()` is also what clears run state everywhere else in
    `core/`. The accounting identity on `AgentSimulationValidator` only means
    something when all three totals are read at the same instant. Restoring two
    of them alongside a third that had changed would leave a validator
    describing no real period.
    """

    initial_agent_l: float
    delivered_agent_l: float
    exhausted_agent_l: float


@dataclass(slots=True)
class AgentSimulationValidator:
    """Validate that the simulation neither creates nor loses agent.

    The accounting identity is:

        initial agent + delivered agent
        =
        exhausted agent + currently stored agent
    """

    initial_agent_l: float = 0.0
    delivered_agent_l: float = 0.0
    exhausted_agent_l: float = 0.0

    if not TYPE_CHECKING:  # pragma: no branch - TYPE_CHECKING is False at run time
        # The `__setattr__` below is hidden from `mypy` on purpose, as
        # `AlveolarCompartment.__setattr__` is. For a class that defines
        # `__setattr__`, `mypy` allows assignment to any attribute name, typed
        # by the method's `value` parameter. With the method visible, a
        # misspelt field name written in `src/` would pass `--strict` and then
        # fail at run time against the slots. With the method hidden, `mypy`
        # checks the dataclass's fields and their types as before. The method
        # is the run-time check for the callers that `mypy` does not check.
        # Its lines are checked by their tests rather than by `mypy`
        # (`PL-LBQY`, found at review).

        def __setattr__(self, name: str, value: object) -> None:
            """Write a total, refusing a value that the constructor would refuse.

            Each total is stored in one place, its slot, so its check is made
            here. The one check therefore covers the constructor,
            `record_external_agent_transfer`, `reset`, `restore_state`, and a
            direct assignment that bypasses all of them, as
            `BreathingCircuit.__setattr__` explains (`PL-LBQY`, `PL-19Y0`).
            Nothing is written when a value is refused, and the constructor
            makes no check of its own. No total is checked against another, so
            the order of the writes does not matter. A sum that overflows to an
            infinity is refused where it is written, rather than carried into
            the accounting identity.

            Raises:
                TypeError: `value` is not an `int` or a `float`
                    (`require_a_number`).
                SimulationConfigurationError: `value` is negative or not
                    finite.
            """

            if name in _ACCOUNTING_TOTALS:
                require_nonnegative_finite(name, value)

            super().__setattr__(name, value)

    def record_external_agent_transfer(
        self, delivered_agent_l: float, exhausted_agent_l: float
    ) -> None:
        """Record agent entering and leaving the modeled system."""

        require_nonnegative_finite("delivered_agent_l", delivered_agent_l)
        require_nonnegative_finite("exhausted_agent_l", exhausted_agent_l)

        self.delivered_agent_l += delivered_agent_l
        self.exhausted_agent_l += exhausted_agent_l

    def check_agent_accounting(
        self, currently_stored_agent_l: float
    ) -> AgentSimulationValidationResult:
        """Calculate whether all delivered agent is accounted for."""

        require_nonnegative_finite("currently_stored_agent_l", currently_stored_agent_l)

        unaccounted_agent_l = (
            self.initial_agent_l
            + self.delivered_agent_l
            - self.exhausted_agent_l
            - currently_stored_agent_l
        )
        absolute_error_l = abs(unaccounted_agent_l)

        accounting_scale_l = max(
            self.initial_agent_l + self.delivered_agent_l, MINIMUM_RELATIVE_SCALE_L
        )
        relative_error = absolute_error_l / accounting_scale_l

        passes_validation = (
            absolute_error_l <= AGENT_ACCOUNTING_ABSOLUTE_TOLERANCE_L
            or relative_error <= AGENT_ACCOUNTING_RELATIVE_TOLERANCE
        )

        return AgentSimulationValidationResult(
            initial_agent_l=self.initial_agent_l,
            delivered_agent_l=self.delivered_agent_l,
            exhausted_agent_l=self.exhausted_agent_l,
            currently_stored_agent_l=currently_stored_agent_l,
            unaccounted_agent_l=unaccounted_agent_l,
            absolute_error_l=absolute_error_l,
            relative_error=relative_error,
            passes_validation=passes_validation,
        )

    def require_valid_agent_accounting(
        self, currently_stored_agent_l: float
    ) -> AgentSimulationValidationResult:
        """Halt the run if this validator's own accounting no longer balances.

        Raises `AgentSimulationValidationError` when the accounting identity
        is off by more than both tolerances. Raises
        `SimulationConfigurationError` when `currently_stored_agent_l` is
        negative or not finite. Otherwise returns the passing check, which
        `AgentUptakeSystem.advance()` reports in `UptakeStepResult`.
        `check_agent_accounting()` does the same arithmetic without the halt,
        for the display path.

        The method takes the currently stored amount rather than a completed
        `AgentSimulationValidationResult`. That way, the period it judges is
        always this validator's own. The earlier signature accepted another
        validator's result and silently let it pass. It would also have named
        that other period's totals in the halt message (`PL-X204`).
        """

        check = self.check_agent_accounting(currently_stored_agent_l)

        if check.passes_validation:
            return check

        raise AgentSimulationValidationError(
            "Agent accounting validation failed: "
            f"unaccounted={check.unaccounted_agent_l:.6e} L, "
            f"absolute_error={check.absolute_error_l:.6e} L, "
            f"relative_error={check.relative_error:.6e}, "
            f"initial={check.initial_agent_l:.6e} L, "
            f"delivered={check.delivered_agent_l:.6e} L, "
            f"exhausted={check.exhausted_agent_l:.6e} L, "
            "currently_stored="
            f"{check.currently_stored_agent_l:.6e} L"
        )

    def capture_state(self) -> AgentSimulationValidatorState:
        """Record run state so a failed step can be rolled back."""

        return AgentSimulationValidatorState(
            initial_agent_l=self.initial_agent_l,
            delivered_agent_l=self.delivered_agent_l,
            exhausted_agent_l=self.exhausted_agent_l,
        )

    def restore_state(self, state: AgentSimulationValidatorState) -> None:
        """Restore run state previously captured by `capture_state()`.

        The fields are assigned through `__setattr__`, which cannot refuse a
        state that `capture_state()` produced. Each total passed the same check
        when it was written, and no total is checked against anything else that
        could have changed since. So rolling back cannot itself raise an error.
        See `BreathingCircuit.restore_state()`.
        """

        self.initial_agent_l = state.initial_agent_l
        self.delivered_agent_l = state.delivered_agent_l
        self.exhausted_agent_l = state.exhausted_agent_l

    def reset(self, initial_agent_l: float = 0.0) -> None:
        """Begin a new accounting period.

        Raises:
            TypeError: `initial_agent_l` is not an `int` or a `float`.
            SimulationConfigurationError: `initial_agent_l` is negative or not
                finite. The write makes both checks itself, in
                `__setattr__`, before either other total is cleared. So
                nothing changes when the value is refused.
        """

        self.initial_agent_l = initial_agent_l
        self.delivered_agent_l = 0.0
        self.exhausted_agent_l = 0.0
