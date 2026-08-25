import pytest

from anesthesia_sim.core.agent_simulation_validation import AgentSimulationValidator
from anesthesia_sim.core.exceptions import (
    AgentSimulationValidationError,
    AnesthesiaSimulationError,
    SimulationExecutionError,
    SimulationNumericalError,
)


def test_exact_accounting_passes_validation() -> None:
    validator = AgentSimulationValidator()
    validator.record_external_agent_transfer(delivered_agent_l=1.0, exhausted_agent_l=0.25)

    check = validator.check_agent_accounting(currently_stored_agent_l=0.75)

    assert check.unaccounted_agent_l == pytest.approx(0.0)
    assert check.absolute_error_l == pytest.approx(0.0)
    assert check.passes_validation is True


def test_missing_agent_fails_validation() -> None:
    validator = AgentSimulationValidator()
    validator.record_external_agent_transfer(delivered_agent_l=1.0, exhausted_agent_l=0.25)

    check = validator.check_agent_accounting(currently_stored_agent_l=0.70)

    assert check.unaccounted_agent_l == pytest.approx(0.05)
    assert check.absolute_error_l == pytest.approx(0.05)
    assert check.passes_validation is False


def test_unexpected_extra_agent_fails_validation() -> None:
    validator = AgentSimulationValidator()
    validator.record_external_agent_transfer(delivered_agent_l=1.0, exhausted_agent_l=0.25)

    check = validator.check_agent_accounting(currently_stored_agent_l=0.80)

    assert check.unaccounted_agent_l == pytest.approx(-0.05)
    assert check.absolute_error_l == pytest.approx(0.05)
    assert check.passes_validation is False


def test_initial_agent_is_included_in_accounting() -> None:
    validator = AgentSimulationValidator(initial_agent_l=0.5)

    check = validator.check_agent_accounting(currently_stored_agent_l=0.5)

    assert check.unaccounted_agent_l == pytest.approx(0.0)
    assert check.passes_validation is True


def test_require_valid_raises_specific_project_exception() -> None:
    validator = AgentSimulationValidator()
    validator.record_external_agent_transfer(delivered_agent_l=1.0, exhausted_agent_l=0.25)
    check = validator.check_agent_accounting(currently_stored_agent_l=0.70)

    with pytest.raises(AgentSimulationValidationError, match="Agent accounting validation failed"):
        validator.require_valid_agent_accounting(check)


def test_accounting_exception_inherits_project_hierarchy() -> None:
    error = AgentSimulationValidationError("test failure")

    assert isinstance(error, SimulationNumericalError)
    assert isinstance(error, SimulationExecutionError)
    assert isinstance(error, AnesthesiaSimulationError)


def test_reset_clears_recorded_external_agent() -> None:
    validator = AgentSimulationValidator()
    validator.record_external_agent_transfer(delivered_agent_l=1.0, exhausted_agent_l=0.25)

    validator.reset(initial_agent_l=0.2)

    assert validator.initial_agent_l == 0.2
    assert validator.delivered_agent_l == 0.0
    assert validator.exhausted_agent_l == 0.0
