"""Exception hierarchy for errors raised by the simulation core."""


class AnesthesiaSimulationError(Exception):
    """Base exception for errors raised by the simulation project."""


class SimulationConfigurationError(AnesthesiaSimulationError):
    """Raised when simulation configuration is inconsistent."""


class SimulationExecutionError(AnesthesiaSimulationError):
    """Raised when a running simulation cannot continue safely."""


class SimulationNumericalError(SimulationExecutionError):
    """Raised when a numerical invariant is violated."""


class AgentSimulationValidationError(SimulationNumericalError):
    """Raised when delivered agent cannot be fully accounted for."""
