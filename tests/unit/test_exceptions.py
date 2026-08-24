"""The shape of the core's exception hierarchy, as a contract.

These are not tests of behavior so much as of a design decision the rest
of the codebase depends on: `app/` catches `AnesthesiaSimulationError` to
decide whether a run is still trustworthy, and that only works if every
core failure is inside the hierarchy and nothing else is.
"""

import pytest

from anesthesia_sim.core.exceptions import (
    AgentSimulationValidationError,
    AnesthesiaSimulationError,
    SimulationConfigurationError,
    SimulationExecutionError,
    SimulationNumericalError,
)


@pytest.mark.parametrize(
    "error_type",
    [
        SimulationConfigurationError,
        SimulationExecutionError,
        SimulationNumericalError,
        AgentSimulationValidationError,
    ],
)
def test_every_core_error_is_catchable_as_one_type(
    error_type: type[AnesthesiaSimulationError],
) -> None:
    assert issubclass(error_type, AnesthesiaSimulationError)


def test_configuration_and_execution_are_separate_branches() -> None:
    """A caller must be able to tell a refused value from a failed run.

    If either were a subclass of the other, `app/` could not distinguish
    "your setting did not take, the run is fine" from "the run is no
    longer trustworthy" by exception type alone.
    """

    assert not issubclass(SimulationConfigurationError, SimulationExecutionError)
    assert not issubclass(SimulationExecutionError, SimulationConfigurationError)


def test_numerical_failures_are_execution_failures() -> None:
    assert issubclass(SimulationNumericalError, SimulationExecutionError)
    assert issubclass(AgentSimulationValidationError, SimulationNumericalError)


def test_core_errors_are_not_value_errors() -> None:
    """Inheriting from `ValueError` was the rejected alternative design.

    Two reasons it stays rejected, both regressions this test would catch:
    a caller could no longer separate a simulation failure from an
    ordinary `ValueError` raised by a library or a bug, and Pydantic
    treats a `ValueError` raised inside a validator as a validation
    failure, so `core/parameters.py` would silently absorb a project
    exception into a `ValidationError` instead of letting it reach the
    caller as itself.
    """

    assert not issubclass(AnesthesiaSimulationError, ValueError)

    for error_type in (
        SimulationConfigurationError,
        SimulationExecutionError,
        SimulationNumericalError,
        AgentSimulationValidationError,
    ):
        assert not issubclass(error_type, ValueError)
