"""The shape of the core's exception hierarchy, as a contract.

These tests check a design decision more than a behavior, and the rest of
the codebase depends on that decision. `app/` catches
`AnesthesiaSimulationError` to decide whether a run is still trustworthy.
That works only if every core failure is inside the hierarchy and nothing
else is.
"""

import pytest

from anesthesia_sim.core.exceptions import (
    AgentSimulationValidationError,
    AnesthesiaSimulationError,
    SimulationConfigurationError,
    SimulationDomainLimitError,
    SimulationExecutionError,
    SimulationNumericalError,
)


@pytest.mark.parametrize(
    "error_type",
    [
        SimulationConfigurationError,
        SimulationExecutionError,
        SimulationDomainLimitError,
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

    It stays rejected for two reasons, and this test would catch a regression
    on either. First, a caller could no longer tell a simulation failure from
    an ordinary `ValueError` raised by a library or a bug. Second, Pydantic
    treats a `ValueError` raised inside a validator as a validation failure.
    `core/parameters.py` would then silently turn a project exception into a
    `ValidationError`, instead of letting the caller receive the original
    exception.
    """

    assert not issubclass(AnesthesiaSimulationError, ValueError)

    for error_type in (
        SimulationConfigurationError,
        SimulationExecutionError,
        SimulationNumericalError,
        AgentSimulationValidationError,
    ):
        assert not issubclass(error_type, ValueError)


def test_reaching_the_supported_domain_stops_the_run_but_is_not_a_failure() -> None:
    """`SimulationDomainLimitError` is a subclass of the branch that stops a run.

    Two requirements apply, and they pull in opposite directions. First, the
    error must be a `SimulationExecutionError`, so that a caller which knows
    only the base classes stops the run. That is the safe default, because
    `PL-Y5WR` exists to prevent a run from continuing past the supported
    domain. Second, the error must be distinguishable from the other
    execution errors. The interface decides from the type whether to tell a
    reader that the simulator broke. Saying so about a model that stopped
    exactly where `docs/MODEL.md` says it must would misreport a correct
    result (`docs/MODEL.md`, "Supported run length").
    """

    assert issubclass(SimulationDomainLimitError, SimulationExecutionError)
    assert not issubclass(SimulationDomainLimitError, SimulationConfigurationError)
    assert not issubclass(SimulationDomainLimitError, SimulationNumericalError)
    assert not issubclass(SimulationNumericalError, SimulationDomainLimitError)
