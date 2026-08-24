"""Shared numeric-range guards used by every core compartment's
`__post_init__` and setters, so invalid state is rejected at the same
boundary everywhere instead of trusted or coerced silently.

Every guard raises `SimulationConfigurationError`: a value was rejected
before it changed anything. A guard reached partway through a step means
something different — the numerics broke down rather than the caller
passing a bad value — and `RespiratorySystem.advance()` is what turns it
into `SimulationNumericalError`, because it is the only frame that knows a
step was in progress. See `core/exceptions.py` for why the hierarchy is
kept separate from `ValueError`.
"""

from math import isfinite

from anesthesia_sim.core.exceptions import SimulationConfigurationError


def require_positive_finite(name: str, value: float) -> None:
    """Require a finite numeric value greater than zero."""

    if not isfinite(value) or value <= 0.0:
        raise SimulationConfigurationError(f"{name} must be positive and finite")


def require_nonnegative_finite(name: str, value: float) -> None:
    """Require a finite numeric value greater than or equal to zero."""

    if not isfinite(value) or value < 0.0:
        raise SimulationConfigurationError(f"{name} must be nonnegative and finite")


def require_concentration_fraction(name: str, value: float) -> None:
    """Require a finite concentration fraction from zero through one."""

    if not isfinite(value) or not 0.0 <= value <= 1.0:
        raise SimulationConfigurationError(f"{name} must be between 0 and 1")
