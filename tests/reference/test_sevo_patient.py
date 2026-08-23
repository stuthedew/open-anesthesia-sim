import pytest

from anesthesia_sim.core.alveolar import AlveolarCompartment
from anesthesia_sim.core.circuit import BreathingCircuit
from anesthesia_sim.core.parameters import (
    AgentParameters,
    load_reference_adult_parameters,
    parse_agent_parameters,
)
from anesthesia_sim.core.patient import PatientCompartments
from anesthesia_sim.core.respiratory_system import (
    RespiratorySystem,
)

EQUILIBRIUM_FRACTION_TOLERANCE = 1e-12


def _run_for(
    system: RespiratorySystem,
    duration_s: float,
    simulation_step_s: float,
) -> None:
    """Advance a system for an exact number of fixed steps."""

    step_count = round(duration_s / simulation_step_s)

    for _ in range(step_count):
        system.advance(simulation_step_s)


def _synthetic_agent(blood_gas_partition_coefficient: float) -> AgentParameters:
    """Build an agent identical to sevoflurane except for solubility.

    Holds tissue:gas partition coefficients fixed so that only the
    blood:gas coefficient (and therefore blood capacity and every
    derived tissue:blood coefficient) differs between systems.
    """

    payload = {
        "schema_version": 1,
        "id": "synthetic-solubility-test-agent",
        "display_name": "Synthetic solubility test agent",
        "blood_gas_partition_coefficient": blood_gas_partition_coefficient,
        "tissue_gas_partition_coefficients": {
            "vessel_rich": 1.1,
            "muscle": 2.4,
            "fat": 34.0,
        },
        "max_delivered_concentration_percent": 8.0,
        "mac_percent": 2.0,
        "sources": [
            {
                "citation": "Synthetic parameters for directional solubility testing only.",
                "url": "https://example.com/synthetic-test-agent",
                "note": "Not a real agent; isolates the effect of blood:gas solubility only.",
            }
        ],
    }
    return parse_agent_parameters(payload)


def _build_system_with_blood_gas_coefficient(
    blood_gas_partition_coefficient: float,
) -> RespiratorySystem:
    agent = _synthetic_agent(blood_gas_partition_coefficient)
    patient_parameters = load_reference_adult_parameters()

    return RespiratorySystem(
        circuit=BreathingCircuit(),
        alveoli=AlveolarCompartment(
            gas_volume_l=patient_parameters.alveolar_gas_volume_l,
            alveolar_ventilation_l_min=(patient_parameters.default_alveolar_ventilation_l_min),
        ),
        patient=PatientCompartments.from_parameters(
            agent=agent,
            patient=patient_parameters,
        ),
    )


def test_no_delivered_agent_keeps_every_store_zero() -> None:
    system = RespiratorySystem.default()
    system.set_delivered_concentration(0.0)

    _run_for(
        system,
        duration_s=300.0,
        simulation_step_s=0.1,
    )

    validation = system.agent_simulation_validation

    assert system.total_stored_agent_l == 0.0
    assert validation.delivered_agent_l == 0.0
    assert validation.exhausted_agent_l == 0.0
    assert validation.unaccounted_agent_l == 0.0
    assert validation.passes_validation is True


def test_zero_ventilation_prevents_patient_delivery() -> None:
    system = RespiratorySystem.default()
    system.set_alveolar_ventilation(0.0)

    _run_for(
        system,
        duration_s=120.0,
        simulation_step_s=0.1,
    )

    assert system.circuit.circuit_concentration_fraction > 0.0
    assert system.alveoli.agent_amount_l == 0.0
    assert system.patient.total_agent_amount_l == 0.0
    assert system.agent_simulation_validation.passes_validation is True


def test_zero_cardiac_output_prevents_patient_uptake() -> None:
    system = RespiratorySystem.default()
    system.set_cardiac_output(0.0)

    _run_for(
        system,
        duration_s=120.0,
        simulation_step_s=0.1,
    )

    assert system.alveoli.concentration_fraction > 0.0
    assert system.patient.total_agent_amount_l == 0.0
    assert system.agent_simulation_validation.passes_validation is True


def test_higher_ventilation_increases_early_alveolar_fraction() -> None:
    lower_ventilation = RespiratorySystem.default()
    higher_ventilation = RespiratorySystem.default()

    lower_ventilation.set_alveolar_ventilation(2.0)
    higher_ventilation.set_alveolar_ventilation(8.0)

    _run_for(
        lower_ventilation,
        duration_s=30.0,
        simulation_step_s=0.1,
    )
    _run_for(
        higher_ventilation,
        duration_s=30.0,
        simulation_step_s=0.1,
    )

    assert (
        higher_ventilation.alveoli.concentration_fraction
        > lower_ventilation.alveoli.concentration_fraction
    )


def test_step_refinement_converges() -> None:
    coarse = RespiratorySystem.default()
    fine = RespiratorySystem.default()

    _run_for(
        coarse,
        duration_s=60.0,
        simulation_step_s=0.1,
    )
    _run_for(
        fine,
        duration_s=60.0,
        simulation_step_s=0.05,
    )

    assert coarse.alveoli.concentration_fraction == pytest.approx(
        fine.alveoli.concentration_fraction,
        rel=5e-3,
        abs=1e-8,
    )
    assert coarse.patient.vessel_rich.partial_pressure_fraction == pytest.approx(
        fine.patient.vessel_rich.partial_pressure_fraction,
        rel=5e-3,
        abs=1e-8,
    )
    assert coarse.patient.mixed_venous_fraction == pytest.approx(
        fine.patient.mixed_venous_fraction,
        rel=5e-3,
        abs=1e-8,
    )


def test_long_wash_in_and_washout_validate_agent_simulation() -> None:
    system = RespiratorySystem.default()

    _run_for(
        system,
        duration_s=600.0,
        simulation_step_s=0.1,
    )

    system.set_delivered_concentration(0.0)

    _run_for(
        system,
        duration_s=600.0,
        simulation_step_s=0.1,
    )

    validation = system.agent_simulation_validation

    assert validation.passes_validation is True
    assert validation.absolute_error_l <= 1e-12
    assert validation.delivered_agent_l > 0.0
    assert validation.exhausted_agent_l > 0.0


def test_reset_clears_system_and_validation_accounting() -> None:
    system = RespiratorySystem.default()

    _run_for(
        system,
        duration_s=60.0,
        simulation_step_s=0.1,
    )

    assert system.total_stored_agent_l > 0.0
    assert system.agent_simulation_validation.delivered_agent_l > 0.0

    system.reset()

    validation = system.agent_simulation_validation

    assert system.total_stored_agent_l == 0.0
    assert validation.initial_agent_l == 0.0
    assert validation.delivered_agent_l == 0.0
    assert validation.exhausted_agent_l == 0.0
    assert validation.currently_stored_agent_l == 0.0
    assert validation.unaccounted_agent_l == 0.0
    assert validation.absolute_error_l == 0.0
    assert validation.passes_validation is True


def test_equilibrium_produces_no_net_internal_transfer() -> None:
    """All connected compartments at one fraction must not exchange agent.

    Required test from docs/MODEL.md: if F_C = F_A = F_a = F_v = F_i, every
    internal transfer rate must be zero. Fresh gas flow is held at zero so
    the only transfers under test are the internal circuit-alveolar,
    tissue, and venous exchanges.
    """

    system = RespiratorySystem.default()
    system.set_fresh_gas_flow(0.0)

    equilibrium_fraction = 0.05

    system.circuit.set_agent_amount(system.circuit.circuit_volume_l * equilibrium_fraction)
    system.alveoli.set_concentration_fraction(equilibrium_fraction)
    system.patient.vessel_rich.set_partial_pressure_fraction(equilibrium_fraction)
    system.patient.muscle.set_partial_pressure_fraction(equilibrium_fraction)
    system.patient.fat.set_partial_pressure_fraction(equilibrium_fraction)
    system.patient.venous_blood.set_concentration_fraction(equilibrium_fraction)

    # Re-baseline agent accounting: the compartment stores above were set
    # directly rather than delivered, so the validator's initial reference
    # amount must match the state actually under test.
    system.agent_simulation_validator.reset(initial_agent_l=system.total_stored_agent_l)

    result = system.advance(0.1)

    assert result.circuit_to_alveolar_agent_l == pytest.approx(
        0.0, abs=EQUILIBRIUM_FRACTION_TOLERANCE
    )
    assert result.patient_agent_change_l == pytest.approx(0.0, abs=EQUILIBRIUM_FRACTION_TOLERANCE)
    assert system.circuit.circuit_concentration_fraction == pytest.approx(equilibrium_fraction)
    assert system.alveoli.concentration_fraction == pytest.approx(equilibrium_fraction)
    assert system.patient.vessel_rich.partial_pressure_fraction == pytest.approx(
        equilibrium_fraction
    )
    assert system.patient.muscle.partial_pressure_fraction == pytest.approx(equilibrium_fraction)
    assert system.patient.fat.partial_pressure_fraction == pytest.approx(equilibrium_fraction)
    assert system.patient.mixed_venous_fraction == pytest.approx(equilibrium_fraction)
    assert system.agent_simulation_validation.passes_validation is True


def test_higher_blood_gas_solubility_slows_alveolar_to_circuit_rise() -> None:
    """Higher blood:gas solubility must slow the rise of F_A / F_C.

    Required test from docs/MODEL.md: increasing the blood:gas partition
    coefficient must increase blood capacity and slow this ratio's approach
    to one, in an otherwise identical synthetic system.
    """

    low_solubility = _build_system_with_blood_gas_coefficient(0.3)
    high_solubility = _build_system_with_blood_gas_coefficient(3.0)

    _run_for(low_solubility, duration_s=60.0, simulation_step_s=0.1)
    _run_for(high_solubility, duration_s=60.0, simulation_step_s=0.1)

    low_ratio = (
        low_solubility.alveoli.concentration_fraction
        / low_solubility.circuit.circuit_concentration_fraction
    )
    high_ratio = (
        high_solubility.alveoli.concentration_fraction
        / high_solubility.circuit.circuit_concentration_fraction
    )

    assert high_ratio < low_ratio
