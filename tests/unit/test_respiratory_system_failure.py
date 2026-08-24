"""How a failed step reports itself, and how a rejected argument does not.

Regression cover for the first half of PL-018: a step that breaks down
used to raise a bare `ValueError` from deep inside a compartment, which a
caller could not tell apart from a programming error and so could not act
on.
"""

from math import inf, nan

import pytest

from anesthesia_sim.core.exceptions import (
    AnesthesiaSimulationError,
    SimulationConfigurationError,
    SimulationNumericalError,
)
from anesthesia_sim.core.respiratory_system import RespiratorySystem

# Large enough that the pairwise operator split drives the alveolar amount
# negative on the very first step from the initial state. This is the case
# the review harness reproduces as P1-1.
BREAKDOWN_STEP_S = 60.0


def _sevoflurane_at_one_mac() -> RespiratorySystem:
    return RespiratorySystem.for_agent("sevoflurane")


def test_a_step_that_breaks_down_raises_a_numerical_error() -> None:
    system = _sevoflurane_at_one_mac()

    with pytest.raises(SimulationNumericalError) as raised:
        system.advance(BREAKDOWN_STEP_S)

    # Not a configuration error: the arguments were valid, the numerics
    # were not. A caller keys its response off exactly this distinction.
    assert not isinstance(raised.value, SimulationConfigurationError)
    assert isinstance(raised.value, AnesthesiaSimulationError)


def test_a_failed_step_names_the_step_and_keeps_the_failing_guard() -> None:
    """The message must stay diagnosable back to the invariant that broke."""

    system = _sevoflurane_at_one_mac()

    with pytest.raises(SimulationNumericalError) as raised:
        system.advance(BREAKDOWN_STEP_S)

    assert "60.0 s" in str(raised.value)
    assert "resulting_agent_amount_l" in str(raised.value)

    cause = raised.value.__cause__
    assert isinstance(cause, SimulationConfigurationError)
    assert "resulting_agent_amount_l" in str(cause)


@pytest.mark.parametrize("simulation_step_s", [0.0, -0.1, inf, nan])
def test_an_invalid_step_is_a_configuration_error_and_changes_nothing(
    simulation_step_s: float,
) -> None:
    """A bad argument is rejected before the step starts, so state is intact.

    This is the case that must *not* be reported as a numerical failure:
    nothing was miscalculated, so a caller has no reason to distrust the
    state it already has.
    """

    system = _sevoflurane_at_one_mac()
    before = system.total_stored_agent_l

    with pytest.raises(SimulationConfigurationError, match="simulation_step_s"):
        system.advance(simulation_step_s)

    assert system.total_stored_agent_l == before


def test_a_rejected_setting_stays_a_configuration_error() -> None:
    """A refused vaporizer dial must not be reported as a broken run."""

    system = _sevoflurane_at_one_mac()
    before = system.circuit.delivered_concentration_fraction

    with pytest.raises(SimulationConfigurationError, match="vaporizer maximum"):
        system.set_delivered_concentration(0.5)

    assert system.circuit.delivered_concentration_fraction == before


def test_the_ordinary_step_is_unaffected() -> None:
    """The wrapper must not change a step that succeeds."""

    system = _sevoflurane_at_one_mac()
    result = system.advance(0.1)

    assert result.fresh_gas_exchange.delivered_agent_l > 0.0
    assert result.agent_accounting.passes_validation
