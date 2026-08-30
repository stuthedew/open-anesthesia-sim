"""How a failed step reports itself, and how a rejected argument does not.

Regression cover for the first half of PL-018: a step that breaks down
used to raise a bare `ValueError` from deep inside a compartment, which a
caller could not tell apart from a programming error and so could not act
on.

Also cover for PL-VP7N, which added the other half of the same distinction:
a step larger than `MAXIMUM_SIMULATION_STEP_S` is refused as a
configuration error before the step begins, because the operator split has
no measured error bound there and the number it would return would be wrong
in the first digit the interface displays.
"""

from math import inf, nan

import pytest

from anesthesia_sim.core.alveolar import AlveolarCompartment
from anesthesia_sim.core.circuit import BreathingCircuit
from anesthesia_sim.core.exceptions import (
    AnesthesiaSimulationError,
    SimulationConfigurationError,
    SimulationNumericalError,
)
from anesthesia_sim.core.parameters import load_agent_parameters, load_reference_adult_parameters
from anesthesia_sim.core.patient import PatientCompartments
from anesthesia_sim.core.respiratory_system import MAXIMUM_SIMULATION_STEP_S, RespiratorySystem

# An alveolar gas volume no patient has, and that is the point: after PL-VP7N
# no supported step can break the split on the reference adult, so the only
# way to reach the breakdown path through the public interface is a system
# whose capacity is smaller than one supported step's transfer. That is not a
# hypothetical shape - it is what a future parameter set (a paediatric patient
# file, a far more soluble agent) could produce at a step this module still
# accepts, which is why the guard has to stay and has to be covered.
#
# The arithmetic: one step of blood uptake removes about
# Q * lambda_b/g * dt = (10/60) * 1.3 * 0.1 = 0.022 L of isoflurane per unit
# alveolar fraction, at the interface's maximum cardiac output. A lung holding
# less than that at a fraction of 1 cannot supply it, so the alveolar guard
# rejects the negative amount the split asks it to hold.
BREAKDOWN_ALVEOLAR_GAS_VOLUME_L = 0.005
MAX_CARDIAC_OUTPUT_L_MIN = 10.0


def _sevoflurane_at_one_mac() -> RespiratorySystem:
    return RespiratorySystem.for_agent("sevoflurane")


def _lungs_too_small_for_one_supported_step() -> RespiratorySystem:
    """A system whose alveolar store one supported step would overdraw."""

    agent = load_agent_parameters("isoflurane")
    patient_parameters = load_reference_adult_parameters()
    system = RespiratorySystem(
        circuit=BreathingCircuit(
            delivered_concentration_fraction=(agent.mac_percent / 100.0),
            max_delivered_concentration_fraction=(
                agent.max_delivered_concentration_percent / 100.0
            ),
        ),
        alveoli=AlveolarCompartment(
            gas_volume_l=BREAKDOWN_ALVEOLAR_GAS_VOLUME_L,
            alveolar_ventilation_l_min=(patient_parameters.default_alveolar_ventilation_l_min),
        ),
        patient=PatientCompartments.from_parameters(agent=agent, patient=patient_parameters),
    )
    system.set_cardiac_output(MAX_CARDIAC_OUTPUT_L_MIN)

    return system


def test_a_step_that_breaks_down_raises_a_numerical_error() -> None:
    system = _lungs_too_small_for_one_supported_step()

    with pytest.raises(SimulationNumericalError) as raised:
        system.advance(MAXIMUM_SIMULATION_STEP_S)

    # Not a configuration error: the arguments were valid, the numerics
    # were not. A caller keys its response off exactly this distinction.
    assert not isinstance(raised.value, SimulationConfigurationError)
    assert isinstance(raised.value, AnesthesiaSimulationError)


def test_a_failed_step_names_the_step_and_keeps_the_failing_guard() -> None:
    """The message must stay diagnosable back to the invariant that broke."""

    system = _lungs_too_small_for_one_supported_step()

    with pytest.raises(SimulationNumericalError) as raised:
        system.advance(MAXIMUM_SIMULATION_STEP_S)

    assert f"{MAXIMUM_SIMULATION_STEP_S} s" in str(raised.value)
    assert "resulting_agent_amount_l" in str(raised.value)

    cause = raised.value.__cause__
    assert isinstance(cause, SimulationConfigurationError)
    assert "resulting_agent_amount_l" in str(cause)


def test_a_step_above_the_maximum_simulation_step_is_refused() -> None:
    """The defect PL-VP7N fixes: 30 s used to return a plausible number.

    It is a configuration error rather than a numerical one, and the
    difference is the whole point. Nothing has been miscalculated - the
    argument was refused - so a caller holds a run it can still trust and
    can retry with a supported step. Reporting it as a numerical failure
    would tell that caller to throw away state that is fine.
    """

    system = _sevoflurane_at_one_mac()

    with pytest.raises(SimulationConfigurationError, match="applicability domain") as raised:
        system.advance(30.0)

    assert not isinstance(raised.value, SimulationNumericalError)


def test_a_refused_maximum_simulation_step_leaves_the_run_untouched() -> None:
    """A refused step must not have moved the system part of the way."""

    system = _sevoflurane_at_one_mac()
    system.advance(MAXIMUM_SIMULATION_STEP_S)
    before = system.total_stored_agent_l

    with pytest.raises(SimulationConfigurationError):
        system.advance(MAXIMUM_SIMULATION_STEP_S * 2.0)

    assert system.total_stored_agent_l == before
    assert system.agent_simulation_validation.passes_validation


def test_the_maximum_simulation_step_itself_is_accepted() -> None:
    """The domain is closed at its endpoint, which is the step that ships."""

    system = _sevoflurane_at_one_mac()

    result = system.advance(MAXIMUM_SIMULATION_STEP_S)

    assert result.fresh_gas_exchange.delivered_agent_l > 0.0
    assert result.agent_accounting.passes_validation


def test_the_maximum_simulation_step_does_not_bind_a_bare_compartment() -> None:
    """The bound is the coupled split's, not any one compartment's.

    A compartment advanced alone is solved exactly at any step, so there is
    no splitting error to bound and nothing to refuse; `tests/unit/
    test_circuit.py` steps a bare circuit 60 s and compares it against the
    analytic solution. Putting the guard on a compartment would break that
    test and would also misstate where the error comes from.
    """

    circuit = BreathingCircuit()
    step_s = 60.0

    assert step_s > MAXIMUM_SIMULATION_STEP_S

    circuit.advance_fresh_gas(step_s)

    assert circuit.circuit_concentration_fraction > 0.0


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
