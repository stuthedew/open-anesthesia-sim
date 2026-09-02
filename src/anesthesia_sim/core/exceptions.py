"""Exception hierarchy for errors raised by the simulation core.

Every failure the core detects — a rejected argument, a violated numeric
guard, a step whose numerics broke down — is raised as a subclass of
`AnesthesiaSimulationError`, so a caller can catch simulation failure as
one thing and distinguish it from a programming error (`TypeError`,
`AttributeError`, ...) that happens to pass through the same call.

`AnesthesiaSimulationError` deliberately does **not** inherit from
`ValueError`. Doing so would be the smaller change but would defeat the
purpose twice over: a bare `ValueError` raised by a core guard still would
not be an `AnesthesiaSimulationError`, so the distinction the caller needs
would remain unavailable; and Pydantic treats a `ValueError` raised inside
a validator as a validation failure, so a project exception that is also a
`ValueError` could be silently absorbed into a `ValidationError` by
`core/parameters.py` rather than reaching the caller as itself.

The two branches below mean different things to a caller, and the
difference is what the interface acts on:

- `SimulationConfigurationError` — a value was rejected before it could be
  simulated. Nothing has been miscalculated; the requested setting simply
  did not take effect, and the run (if any) is still trustworthy.
- `SimulationExecutionError` — a step that had already begun could not be
  completed, and the run must stop rather than continue. What the model
  holds is the last completed step: `AgentUptakeSystem.advance()` rolls
  the failed step back before raising, so the values are a real solution
  of the model rather than an artifact of how far into the step the
  operators got. Stopping is required all the same — the model reached a
  state it could not step from, so the same step would fail again.
"""


class AnesthesiaSimulationError(Exception):
    """Base exception for errors raised by the simulation project."""


class SimulationConfigurationError(AnesthesiaSimulationError):
    """Raised when a value handed to the core is invalid or inconsistent.

    Raised by the shared guards in `core/validation.py`, by compartment
    constructors and setters, and by the parameter-file loaders. Detected
    before any state is changed, so the caller can correct the value and
    carry on.
    """


class SimulationExecutionError(AnesthesiaSimulationError):
    """Raised when a running simulation cannot continue safely.

    A step that had begun could not be completed, or a caller asked a
    halted run to continue. Where a step is what failed,
    `AgentUptakeSystem.advance()` rolls it back before raising, so the
    state left behind is the last completed step rather than a partly
    applied one; the run still has to stop.
    """


class SimulationNumericalError(SimulationExecutionError):
    """Raised when a numerical invariant is violated.

    Distinct from `SimulationConfigurationError` in that the inputs were
    valid: it is the step itself that produced a state the model cannot
    represent — a negative compartment amount, a fraction outside zero
    through one — typically because the step was too large for the
    operator split in `AgentUptakeSystem.advance()`.
    """


class AgentSimulationValidationError(SimulationNumericalError):
    """Raised when delivered agent cannot be fully accounted for."""
