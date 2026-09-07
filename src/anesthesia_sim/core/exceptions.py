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
- `SimulationExecutionError` — the run must stop rather than continue,
  and what the model holds either way is the last completed step. Usually
  a step that had already begun could not be completed;
  `AgentUptakeSystem.advance()` rolls that step back before raising, so
  the values are a real solution of the model rather than an artifact of
  how far into the step the operators got, and stopping is required all
  the same because the same step would fail again.
- `SimulationDomainLimitError`, a subclass of the above, is the one case
  where nothing went wrong: the run reached the end of what the model is
  claimed to represent, and the step that would have crossed the boundary
  was refused before it began. The run stops for a different reason and
  the interface must say so differently.
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


class SimulationDomainLimitError(SimulationExecutionError):
    """Raised when a run reaches a declared limit of the supported domain.

    Today that is the supported run length: `core/supported_ranges.py`
    refuses the step that would take elapsed simulated time past
    `MAXIMUM_ELAPSED_SIMULATION_TIME_S`.

    **Nothing failed, and the distinction is the point of the class.** The
    inputs were valid, the step was never attempted, and every value the
    model holds is a completed step's at a simulated time inside the
    supported span. What ended is the claim that a further step would stand
    for a patient - the same act as `require_supported_cardiac_output`
    refusing 1000 L/min, arriving mid-run because a run length is reached
    rather than set.

    It is a `SimulationExecutionError` all the same, because the run must
    stop: there is no value to correct and the next step would be refused
    identically, so `SimulationConfigurationError`'s "the requested setting
    did not take effect and the run carries on" does not describe it.
    Sitting under the execution branch also makes the default safe - a
    caller that knows only the base classes stops the run, which is right,
    and only a caller that catches this type specifically needs to know
    that stopping here is not a fault. One that presents it as a fault has
    a defect: `docs/MODEL.md` § "Supported run length" requires the two be
    told apart on screen.
    """


class SimulationNumericalError(SimulationExecutionError):
    """Raised when a numerical invariant is violated.

    Distinct from `SimulationConfigurationError` in that the inputs were
    valid: it is the step itself that produced a state the model cannot
    represent — a negative compartment amount, a fraction outside zero
    through one.

    No step size can reach this through the shipped propagator, whatever its
    size: the system matrix is Metzler, so the exponential of it is entrywise
    nonnegative. It is cover for a model extension whose matrix is not a pure
    transfer system, and `docs/MODEL.md` § "Supported simulation step" says so.
    """


class AgentSimulationValidationError(SimulationNumericalError):
    """Raised when delivered agent cannot be fully accounted for."""
