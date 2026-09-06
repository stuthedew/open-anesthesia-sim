import pytest
from mass_balance_gate import MASS_BALANCE_RELATIVE_GATE

from anesthesia_sim.core.alveolar import AlveolarCompartment
from anesthesia_sim.core.circuit import BreathingCircuit
from anesthesia_sim.core.parameters import load_agent_parameters, load_reference_adult_parameters
from anesthesia_sim.core.patient import PatientCompartments
from anesthesia_sim.core.uptake_system import AgentUptakeSystem

EQUILIBRIUM_FRACTION_TOLERANCE = 1e-12

# The dial every system below runs at. Both agents run at the same one, so
# the only thing differing between two systems is the agent's own parameters,
# which is the claim these gates make. 4% is inside both calibrated ranges -
# isoflurane's 5% maximum is the lower of the two, desflurane reaches 18% -
# and each circuit carries its own agent's maximum, so construction refuses
# this value if it ever stops being deliverable.
#
# Deliberately not the 0.05 the equilibrium test fills every compartment to:
# at that dial the circuit would already sit at its own delivered
# concentration, and that test's `set_fresh_gas_flow(0.0)` would stop being
# load-bearing - it would pass at any flow, testing less than it reads as.
DELIVERED_CONCENTRATION_FRACTION = 0.04


def _run_for(system: AgentUptakeSystem, duration_s: float, simulation_step_s: float) -> None:
    """Advance a system for an exact number of fixed steps."""

    step_count = round(duration_s / simulation_step_s)

    for _ in range(step_count):
        system.advance(simulation_step_s)


def _build_system_for_agent(agent_id: str) -> AgentUptakeSystem:
    """Build a patient system for a named built-in agent.

    Proves the v0.1.0 core is agent-generic: only the agent parameters
    change here, not any governing equation or compartment structure.

    Built by hand rather than through `AgentUptakeSystem.for_agent()`
    precisely to keep that true of the circuit as well: `for_agent()`
    starts each agent at its own 1 MAC, which would leave the two systems
    below differing in two things at once.
    """

    agent = load_agent_parameters(agent_id)
    patient_parameters = load_reference_adult_parameters()

    return AgentUptakeSystem(
        circuit=BreathingCircuit(
            delivered_concentration_fraction=DELIVERED_CONCENTRATION_FRACTION,
            max_delivered_concentration_fraction=(
                agent.max_delivered_concentration_percent / 100.0
            ),
        ),
        alveoli=AlveolarCompartment(
            gas_volume_l=patient_parameters.alveolar_gas_volume_l,
            alveolar_ventilation_l_min=(patient_parameters.default_alveolar_ventilation_l_min),
        ),
        patient=PatientCompartments.from_parameters(agent=agent, patient=patient_parameters),
    )


@pytest.mark.parametrize("agent_id", ["isoflurane", "desflurane"])
def test_wash_in_and_washout_validates_agent_simulation(agent_id: str) -> None:
    system = _build_system_for_agent(agent_id)

    _run_for(system, duration_s=600.0, simulation_step_s=0.1)

    system.set_delivered_concentration(0.0)

    _run_for(system, duration_s=600.0, simulation_step_s=0.1)

    validation = system.agent_simulation_validation

    assert validation.passes_validation is True
    # The relative residual, not the absolute one: the absolute figure scales
    # with the dial and the run length, so asserting it measures this test's
    # setup rather than conservation (`PL-4GN8`). `mass_balance_gate` carries
    # the measurements the bound comes from.
    assert validation.relative_error <= MASS_BALANCE_RELATIVE_GATE
    assert validation.delivered_agent_l > 0.0
    assert validation.exhausted_agent_l > 0.0


@pytest.mark.parametrize("agent_id", ["isoflurane", "desflurane"])
def test_equilibrium_produces_no_net_internal_transfer(agent_id: str) -> None:
    """Required test from docs/MODEL.md, repeated per agent.

    If F_C = F_A = F_a = F_v = F_i, every internal transfer rate must be
    zero regardless of which agent's partition coefficients are in use.
    """

    system = _build_system_for_agent(agent_id)
    system.set_fresh_gas_flow(0.0)

    equilibrium_fraction = 0.05

    system.circuit.set_agent_amount(system.circuit.circuit_volume_l * equilibrium_fraction)
    system.alveoli.set_concentration_fraction(equilibrium_fraction)
    system.patient.vessel_rich.set_partial_pressure_fraction(equilibrium_fraction)
    system.patient.muscle.set_partial_pressure_fraction(equilibrium_fraction)
    system.patient.fat.set_partial_pressure_fraction(equilibrium_fraction)
    system.patient.venous_blood.set_concentration_fraction(equilibrium_fraction)

    system.agent_simulation_validator.reset(initial_agent_l=system.total_stored_agent_l)

    result = system.advance(0.1)

    assert result.circuit_to_alveolar_agent_l == pytest.approx(
        0.0, abs=EQUILIBRIUM_FRACTION_TOLERANCE
    )
    assert result.patient_agent_change_l == pytest.approx(0.0, abs=EQUILIBRIUM_FRACTION_TOLERANCE)
    assert system.agent_simulation_validation.passes_validation is True


def test_desflurane_alveolar_circuit_ratio_rises_faster_than_isoflurane() -> None:
    """Directional solubility check using real agent data, not synthetic.

    Desflurane (blood:gas 0.42) is markedly less soluble than isoflurane
    (blood:gas 1.3, per the shared Gas Man source table cited in both
    data files). A less soluble agent's alveolar fraction should approach
    its circuit/inspired fraction faster, matching the emergence-time
    ordering (desflurane fastest, then sevoflurane, then isoflurane)
    reported by De Wolf et al. 2012 for the same reference table.
    """

    desflurane = _build_system_for_agent("desflurane")
    isoflurane = _build_system_for_agent("isoflurane")

    _run_for(desflurane, duration_s=60.0, simulation_step_s=0.1)
    _run_for(isoflurane, duration_s=60.0, simulation_step_s=0.1)

    desflurane_ratio = (
        desflurane.alveoli.concentration_fraction
        / desflurane.circuit.circuit_concentration_fraction
    )
    isoflurane_ratio = (
        isoflurane.alveoli.concentration_fraction
        / isoflurane.circuit.circuit_concentration_fraction
    )

    assert desflurane_ratio > isoflurane_ratio
