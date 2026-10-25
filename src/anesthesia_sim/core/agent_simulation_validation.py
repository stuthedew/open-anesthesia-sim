"""Check that a simulation run neither creates nor loses anesthetic agent.

This is mass-balance accounting. It checks the delivered, exhausted and stored
agent against the accounting identity documented on `AgentSimulationValidator`.
"""

from dataclasses import dataclass, field
from math import isfinite
from typing import TYPE_CHECKING

from anesthesia_sim.core.checked_number import require_a_number, shown
from anesthesia_sim.core.exceptions import (
    AgentSimulationValidationError,
    SimulationConfigurationError,
)
from anesthesia_sim.core.validation import require_nonnegative_finite

AGENT_ACCOUNTING_ABSOLUTE_TOLERANCE_L = 1e-12
AGENT_ACCOUNTING_RELATIVE_TOLERANCE = 1e-9
MINIMUM_RELATIVE_SCALE_L = 1e-15

#: The three totals that `AgentSimulationValidator.__setattr__` requires to be
#: nonnegative and finite.
_ACCOUNTING_TOTALS = frozenset({"initial_agent_l", "delivered_agent_l", "exhausted_agent_l"})

#: The compensation terms of the two running totals. `__setattr__` requires
#: each to be finite. A term may be negative. With `_ACCOUNTING_TOTALS`, these
#: are all of the validator's fields.
_COMPENSATION_TERMS = frozenset({"delivered_compensation_l", "exhausted_compensation_l"})


def _compensated_sum(total: float, compensation: float, addend: float) -> tuple[float, float]:
    """Add `addend` to a running total by Kahan's compensated summation.

    `compensation` is how much larger `total` became than it should have when
    rounding last changed it, negative when `total` became smaller. It is
    taken off the next addend, so rounding cannot build up one addition at a
    time. The function returns the new total and the new compensation.

    The computed total of n nonnegative addends is within (2u + O(n u^2)) of
    the exact sum, relative to it, where u = 2**-53 is the unit roundoff. At
    the step counts this model supports, the O(n u^2) term is negligible, so
    the error does not grow with the run's length (Higham, *Accuracy and
    Stability of Numerical Algorithms*, 2nd ed., SIAM, 2002, section 4.3,
    equation 4.8). Plain addition's error does grow with it, by up to u per
    addition. `docs/MODEL.md` § "Mass-balance identity" gives what each
    measured over a 24 h run at the step floor (`PL-XST1`).

    Neumaier's variant, which CPython's `sum` uses, keeps the plain running
    sum and adds the compensation only at the end. That would leave the stored
    total as inaccurate as plain addition does, and every reader of the total
    would have to add the compensation to it. Kahan's form keeps the stored
    total accurate, so the totals mean what they meant before.
    """

    corrected = addend - compensation
    summed = total + corrected
    return summed, (summed - total) - corrected


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
    """The validator's run state: the three totals of one accounting period and two compensations.

    All three totals are captured, including `initial_agent_l`. That total is
    the anchor of the current accounting period, not a setting. `reset()`
    writes it, and `reset()` is also what clears run state everywhere else in
    `core/`. The accounting identity on `AgentSimulationValidator` only means
    something when all three totals are read at the same instant. Restoring two
    of them alongside a third that had changed would leave a validator
    describing no real period.

    The compensation term of each running total is captured with it. A total
    restored without its compensation would round differently on the next
    step than the run it was captured from. Then a step retried after a
    rollback would not give the same result as the step that was undone, and
    `CLAUDE.md` requires identical inputs to give identical results.
    """

    initial_agent_l: float
    delivered_agent_l: float
    exhausted_agent_l: float
    delivered_compensation_l: float
    exhausted_compensation_l: float


@dataclass(slots=True)
class AgentSimulationValidator:
    """Validate that the simulation neither creates nor loses agent.

    The accounting identity is:

        initial agent + delivered agent
        =
        exhausted agent + currently stored agent

    The delivered and exhausted totals are running sums of one transfer per
    step, so a run of many steps adds many small amounts to a large total.
    Each total is kept by compensated summation, with its compensation term
    in a field of its own (`_compensated_sum`, `PL-XST1`). Plain addition let
    rounding build up once per step. Over a 24 h run at the 1 ms step floor it
    used up a quarter of `AGENT_ACCOUNTING_RELATIVE_TOLERANCE`, as
    `docs/MODEL.md` § "Mass-balance identity" records.
    """

    initial_agent_l: float = 0.0
    delivered_agent_l: float = 0.0
    exhausted_agent_l: float = 0.0
    delivered_compensation_l: float = field(default=0.0, init=False)
    exhausted_compensation_l: float = field(default=0.0, init=False)

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
            """Write a total or a compensation, refusing a value that cannot be one.

            Each total is stored in one place, its slot, so its check is made
            here. The one check therefore covers the constructor,
            `record_external_agent_transfer`, `reset`, `restore_state`, and a
            direct assignment that bypasses all of them, as
            `BreathingCircuit.__setattr__` explains (`PL-LBQY`, `PL-19Y0`).
            Nothing is written when a value is refused, and the constructor
            makes no check of its own. No total is checked against another, so
            the order of the writes does not matter. A sum that overflows to an
            infinity is refused where it is written, rather than carried into
            the accounting identity. A compensation term may be negative, but
            it must be finite, or the next sum it corrects would not be.

            Raises:
                TypeError: `value` is not an `int` or a `float`
                    (`require_a_number`).
                SimulationConfigurationError: a total is negative or not
                    finite, or a compensation term is not finite.
            """

            if name in _ACCOUNTING_TOTALS:
                require_nonnegative_finite(name, value)
            elif name in _COMPENSATION_TERMS:
                require_a_number(name, value)

                if not isfinite(value):
                    raise SimulationConfigurationError(
                        f"{name} must be finite, and {shown(value)} is not"
                    )

            super().__setattr__(name, value)

    def record_external_agent_transfer(
        self, delivered_agent_l: float, exhausted_agent_l: float
    ) -> None:
        """Record agent entering and leaving the modeled system.

        Each transfer is added to its running total by `_compensated_sum`.
        Both new totals are checked before either is written, so a total
        refused here leaves the validator as it was.

        Raises:
            TypeError: a transfer is not an `int` or a `float`.
            SimulationConfigurationError: a transfer, or the total it would
                make, is negative or not finite.
        """

        require_nonnegative_finite("delivered_agent_l", delivered_agent_l)
        require_nonnegative_finite("exhausted_agent_l", exhausted_agent_l)

        delivered_total_l, delivered_compensation_l = _compensated_sum(
            self.delivered_agent_l, self.delivered_compensation_l, delivered_agent_l
        )
        exhausted_total_l, exhausted_compensation_l = _compensated_sum(
            self.exhausted_agent_l, self.exhausted_compensation_l, exhausted_agent_l
        )
        require_nonnegative_finite("delivered_agent_l", delivered_total_l)
        require_nonnegative_finite("exhausted_agent_l", exhausted_total_l)

        self.delivered_agent_l = delivered_total_l
        self.exhausted_agent_l = exhausted_total_l
        self.delivered_compensation_l = delivered_compensation_l
        self.exhausted_compensation_l = exhausted_compensation_l

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
            delivered_compensation_l=self.delivered_compensation_l,
            exhausted_compensation_l=self.exhausted_compensation_l,
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
        self.delivered_compensation_l = state.delivered_compensation_l
        self.exhausted_compensation_l = state.exhausted_compensation_l

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
        self.delivered_compensation_l = 0.0
        self.exhausted_compensation_l = 0.0
