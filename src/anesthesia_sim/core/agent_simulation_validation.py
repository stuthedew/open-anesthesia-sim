"""Mass-balance accounting: verify that a simulation run neither creates nor
loses agent, by checking delivered/exhausted/stored agent against the
accounting identity documented on `AgentSimulationValidator`.
"""

from dataclasses import dataclass

from anesthesia_sim.core.exceptions import AgentSimulationValidationError
from anesthesia_sim.core.validation import require_nonnegative_finite

AGENT_ACCOUNTING_ABSOLUTE_TOLERANCE_L = 1e-12
AGENT_ACCOUNTING_RELATIVE_TOLERANCE = 1e-9
MINIMUM_RELATIVE_SCALE_L = 1e-15


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
    """The validator's run state: one accounting period's three totals.

    All three are captured, `initial_agent_l` included. It is the anchor of
    the current accounting period rather than a setting — `reset()` is what
    writes it, and `reset()` is what clears run state everywhere else in
    `core/` too — and the identity below only means anything with all three
    read from the same instant. Restoring two of them onto a third that had
    moved would leave a validator describing no real period.
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

    def __post_init__(self) -> None:
        require_nonnegative_finite("initial_agent_l", self.initial_agent_l)
        require_nonnegative_finite("delivered_agent_l", self.delivered_agent_l)
        require_nonnegative_finite("exhausted_agent_l", self.exhausted_agent_l)

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
            currently_stored_agent_l=(currently_stored_agent_l),
            unaccounted_agent_l=unaccounted_agent_l,
            absolute_error_l=absolute_error_l,
            relative_error=relative_error,
            passes_validation=passes_validation,
        )

    def require_valid_agent_accounting(
        self, currently_stored_agent_l: float
    ) -> AgentSimulationValidationResult:
        """Halt the run if this validator's own accounting no longer balances.

        Raises `AgentSimulationValidationError` when the identity above misses
        by more than both tolerances, and `SimulationConfigurationError` when
        `currently_stored_agent_l` is negative or not finite. Returns the
        passing check, which `AgentUptakeSystem.advance()` reports in
        `UptakeStepResult`; `check_agent_accounting()` is the same arithmetic
        without the halt, for the display path.

        It takes the store rather than a completed
        `AgentSimulationValidationResult` so that the period it rules on is
        necessarily this validator's own: the earlier signature accepted
        another validator's result, passed on it silently, and would have
        named that period's totals in the halt message (`PL-X204`).
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

        Assigns the fields directly, so that rolling back cannot itself
        raise; see `BreathingCircuit.restore_state()`.
        """

        self.initial_agent_l = state.initial_agent_l
        self.delivered_agent_l = state.delivered_agent_l
        self.exhausted_agent_l = state.exhausted_agent_l

    def reset(self, initial_agent_l: float = 0.0) -> None:
        """Begin a new accounting period."""

        require_nonnegative_finite("initial_agent_l", initial_agent_l)

        self.initial_agent_l = initial_agent_l
        self.delivered_agent_l = 0.0
        self.exhausted_agent_l = 0.0
