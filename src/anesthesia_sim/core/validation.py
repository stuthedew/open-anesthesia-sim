from math import isfinite


def require_positive_finite(name: str, value: float) -> None:
    """Require a finite numeric value greater than zero."""

    if not isfinite(value) or value <= 0.0:
        raise ValueError(f"{name} must be positive and finite")


def require_nonnegative_finite(name: str, value: float) -> None:
    """Require a finite numeric value greater than or equal to zero."""

    if not isfinite(value) or value < 0.0:
        raise ValueError(f"{name} must be nonnegative and finite")


def require_concentration_fraction(name: str, value: float) -> None:
    """Require a finite concentration fraction from zero through one."""

    if not isfinite(value) or not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be between 0 and 1")
