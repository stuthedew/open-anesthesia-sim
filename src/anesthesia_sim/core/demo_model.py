from math import exp


def response(elapsed_s: float, time_constant_s: float) -> float:
    """Return the dimensionless response for the demonstration model.

    The time constant is the simulated time required to reach about 63.2% of
    the final response. This is an architecture demo, not a physiological model.
    """
    if elapsed_s < 0:
        raise ValueError("elapsed_s must be nonnegative")
    if time_constant_s <= 0:
        raise ValueError("time_constant_s must be positive")
    return 1.0 - exp(-elapsed_s / time_constant_s)
