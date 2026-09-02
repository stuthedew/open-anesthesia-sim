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

PL-0MLQ applies the same distinction to the four controls a user sets. A
setting outside `core/supported_ranges.py` is refused by the compartment it
belongs to, which is what every `AgentUptakeSystem` setter forwards to, and
the run in progress stays trustworthy.

PL-006 adds the case where the distinction had been drawn in the wrong
place: `set_circuit_volume` destroyed agent and the *next* step failed for
it, reporting a numerical error for what was a setter's defect.
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
from anesthesia_sim.core.supported_ranges import MAXIMUM_CARDIAC_OUTPUT_L_MIN
from anesthesia_sim.core.uptake_system import MAXIMUM_SIMULATION_STEP_S, AgentUptakeSystem

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
# alveolar fraction, at the model's maximum supported cardiac output. A lung holding
# less than that at a fraction of 1 cannot supply it, so the alveolar guard
# rejects the negative amount the split asks it to hold.
BREAKDOWN_ALVEOLAR_GAS_VOLUME_L = 0.005


def _sevoflurane_at_one_mac() -> AgentUptakeSystem:
    return AgentUptakeSystem.for_agent("sevoflurane")


def _lungs_too_small_for_one_supported_step() -> AgentUptakeSystem:
    """A system whose alveolar store one supported step would overdraw."""

    agent = load_agent_parameters("isoflurane")
    patient_parameters = load_reference_adult_parameters()
    system = AgentUptakeSystem(
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
    system.set_cardiac_output(MAXIMUM_CARDIAC_OUTPUT_L_MIN)

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


@pytest.mark.parametrize(
    ("setter_name", "rejected_value"),
    [
        ("set_fresh_gas_flow", 500.0),
        ("set_alveolar_ventilation", 200.0),
        ("set_cardiac_output", 1000.0),
    ],
)
def test_a_setting_outside_the_supported_range_is_refused_by_the_system(
    setter_name: str, rejected_value: float
) -> None:
    """The three values PL-0MLQ found accepted, refused at the coupled system.

    `AgentUptakeSystem` forwards each of these to the compartment that owns
    the setting, so this is cover for the forwarding rather than a second
    guard: what it holds is that no supported entry point into `core/` can
    put the model outside the domain its error bound is measured over.
    """

    system = _sevoflurane_at_one_mac()

    with pytest.raises(SimulationConfigurationError, match="supported input range"):
        getattr(system, setter_name)(rejected_value)


@pytest.mark.parametrize(
    ("setter_name", "rejected_value"),
    [
        ("set_fresh_gas_flow", 500.0),
        ("set_alveolar_ventilation", 200.0),
        ("set_cardiac_output", 1000.0),
    ],
)
def test_a_refused_setting_leaves_the_run_trustworthy(
    setter_name: str, rejected_value: float
) -> None:
    """A refused setting is not a failed run, and must not read like one.

    This is the same distinction the refused step above draws: nothing has
    been miscalculated, so the caller keeps a run it can go on stepping and
    displaying. The system must therefore be advanceable afterwards, and its
    agent accounting must still close.
    """

    system = _sevoflurane_at_one_mac()
    system.advance(MAXIMUM_SIMULATION_STEP_S)
    before = system.total_stored_agent_l

    with pytest.raises(SimulationConfigurationError) as raised:
        getattr(system, setter_name)(rejected_value)

    assert not isinstance(raised.value, SimulationNumericalError)
    assert system.total_stored_agent_l == before

    result = system.advance(MAXIMUM_SIMULATION_STEP_S)

    assert result.agent_accounting.passes_validation


def test_changing_circuit_volume_mid_run_does_not_break_the_next_step() -> None:
    """Regression test for the defect PL-006 part 3 fixes.

    Reproduced against the shipped code before the fix, and the numbers here
    are that measurement rather than values read off the corrected run: a
    sevoflurane system stepped 60 s held 0.048288200 L of agent in the
    circuit, `set_circuit_volume(3.0)` left 0.024144100 L of it - 24.1 mL of
    equivalent agent gas destroyed by a setter - and the next `advance(0.1)`
    raised `AgentSimulationValidationError`.

    That failure mode is the reason this belongs with the other failure
    tests rather than only with the circuit's unit tests. The step that
    failed was correct; what was wrong happened before it, so the run was
    halted and the numerics blamed for a setter's defect. A conserving setter
    is what makes the two distinguishable again.

    `app/controller.py` compensated, so the shipped application never showed
    this. That is what made it worth fixing rather than leaving: the
    invariant held only for the one caller who knew to go the long way round.
    """

    system = _sevoflurane_at_one_mac()

    for _ in range(600):
        system.advance(MAXIMUM_SIMULATION_STEP_S)

    circuit_agent_before_l = system.circuit.agent_amount_l
    total_agent_before_l = system.total_stored_agent_l

    assert circuit_agent_before_l == pytest.approx(0.048288200)

    system.circuit.set_circuit_volume(3.0)

    assert system.circuit.agent_amount_l == pytest.approx(circuit_agent_before_l)
    assert system.total_stored_agent_l == pytest.approx(total_agent_before_l)

    result = system.advance(MAXIMUM_SIMULATION_STEP_S)

    assert result.agent_accounting.passes_validation
