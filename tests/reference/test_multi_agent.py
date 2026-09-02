import pytest

from anesthesia_sim.core.alveolar import AlveolarCompartment
from anesthesia_sim.core.circuit import BreathingCircuit
from anesthesia_sim.core.parameters import load_agent_parameters, load_reference_adult_parameters
from anesthesia_sim.core.patient import PatientCompartments
from anesthesia_sim.core.uptake_system import AgentUptakeSystem

EQUILIBRIUM_FRACTION_TOLERANCE = 1e-12


def _run_for(system: AgentUptakeSystem, duration_s: float, simulation_step_s: float) -> None:
    """Advance a system for an exact number of fixed steps."""

    step_count = round(duration_s / simulation_step_s)

    for _ in range(step_count):
        system.advance(simulation_step_s)


def _build_system_for_agent(agent_id: str) -> AgentUptakeSystem:
    """Build a patient system for a named built-in agent.

    Proves the v0.1.0 core is agent-generic: only the agent parameters
    change here, not any governing equation or compartment structure.
    """

    agent = load_agent_parameters(agent_id)
    patient_parameters = load_reference_adult_parameters()

    return AgentUptakeSystem(
        circuit=BreathingCircuit(),
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
    assert validation.absolute_error_l <= 1e-12
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
    reported by Stadler et al. 2012 for the same reference table.
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
