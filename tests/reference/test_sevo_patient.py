import pytest

from anesthesia_sim.core.respiratory_system import (
    RespiratorySystem,
)


def _run_for(
    system: RespiratorySystem,
    duration_s: float,
    simulation_step_s: float,
) -> None:
    """Advance a system for an exact number of fixed steps."""

    step_count = round(duration_s / simulation_step_s)

    for _ in range(step_count):
        system.advance(simulation_step_s)


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
