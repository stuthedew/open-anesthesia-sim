"""Shared numeric-range guards used by every core compartment's
`__post_init__` and setters, so invalid state is rejected at the same
boundary everywhere instead of trusted or coerced silently.

Every guard raises `SimulationConfigurationError`: a value was rejected
before it changed anything. A guard reached partway through a step means
something different — the numerics broke down rather than the caller
passing a bad value — and `AgentUptakeSystem.advance()` is what turns it
into `SimulationNumericalError`, because it is the only frame that knows a
step was in progress. It is also the only one that can undo that step, and
does: the guard fires after earlier sub-exchanges have already written
their compartments, so the step is rolled back before the numerical error
is raised. See `core/exceptions.py` for why the hierarchy is kept separate
from `ValueError`.

**What `name` has to carry.** Each guard raises `f"{name} ..."` and nothing
else, so `name` is the whole of what a reader is told about *which* value was
refused — and that reader is usually looking at a banner rather than a
traceback, since `app/dashboard_frame.py` renders a refused setting verbatim
and `AgentUptakeSystem.advance()` wraps a refused step into the halted-run
notice. A bare parameter name identifies the value only where one object can
raise it. Where several can, the caller prefixes the owner: the instance's own
`name` where it has one — `f"{self.name} partial_pressure_fraction"`, as
`governing_equations.py`'s `TissueGroupEquationSettings` already does for its
volume and flow — and the compartment's domain word where it does not,
`"alveolar ..."` and `"venous ..."`. `PL-SPN6` is what the bare name cost:
`PL-9SH6` left the alveolar compartment, the venous pool and all three tissue
groups raising one string, so a refused resume could not say which of the five
had refused. The prefix is built at the call site rather than from a parameter
here, so the sentence a reader will see is readable in the line that raises it.
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


def require_fraction(name: str, value: float) -> None:
    """Require a finite dimensionless fraction from zero through one.

    Named for the range it checks rather than for a quantity, which is what
    `PL-6KNM` settled: every one of its callers is guarding a partial-pressure
    fraction, and the guard cannot tell which $`F`$ it is guarding — nor does
    it need to, since a fraction of an atmosphere, a
    perfusion fraction and a MAC-awake ratio all live in [0, 1]. Its two
    siblings above name a property of the number for the same reason. Which
    quantity a value *is* is the `NewType`s in `core/concentration.py`, and
    they are separate on purpose: a type marks a boundary and checks nothing,
    this checks a value and marks nothing.
    """

    if not isfinite(value) or not 0.0 <= value <= 1.0:
        raise SimulationConfigurationError(f"{name} must be between 0 and 1")
