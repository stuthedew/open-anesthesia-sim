from dataclasses import replace

import pytest

from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.parameters import (
    load_reference_adult_parameters,
    load_sevoflurane_parameters,
)
from anesthesia_sim.core.patient import FLOW_FRACTION_TOLERANCE, PatientCompartments
from anesthesia_sim.core.supported_ranges import MAXIMUM_CARDIAC_OUTPUT_L_MIN


def _build_patient() -> PatientCompartments:
    return PatientCompartments.from_parameters(
        agent=load_sevoflurane_parameters(), patient=load_reference_adult_parameters()
    )


def test_rejects_perfusion_sum_outside_tolerance() -> None:
    agent = load_sevoflurane_parameters()
    parameters = load_reference_adult_parameters()
    invalid_parameters = replace(
        parameters,
        fat_perfusion_fraction=(parameters.fat_perfusion_fraction - 2.0 * FLOW_FRACTION_TOLERANCE),
    )

    with pytest.raises(
        SimulationConfigurationError, match="^tissue perfusion fractions must sum to 1$"
    ):
        PatientCompartments.from_parameters(agent=agent, patient=invalid_parameters)


def test_accepts_perfusion_sum_inside_tolerance() -> None:
    agent = load_sevoflurane_parameters()
    parameters = load_reference_adult_parameters()
    valid_parameters = replace(
        parameters,
        fat_perfusion_fraction=(parameters.fat_perfusion_fraction - 0.5 * FLOW_FRACTION_TOLERANCE),
    )

    patient = PatientCompartments.from_parameters(agent=agent, patient=valid_parameters)

    assert patient.total_perfusion_fraction == pytest.approx(1.0, abs=FLOW_FRACTION_TOLERANCE)


def test_builds_reference_patient_from_parameters() -> None:
    patient = _build_patient()

    assert patient.cardiac_output_l_min == 5.0
    assert patient.vessel_rich.volume_l == 6.0
    assert patient.muscle.volume_l == 33.0
    assert patient.fat.volume_l == 14.5
    assert patient.venous_blood.volume_l == 1.222
    assert patient.total_perfusion_fraction == pytest.approx(1.0)


def test_allocates_cardiac_output_to_tissues() -> None:
    patient = _build_patient()

    assert patient.vessel_rich.blood_flow_l_min == pytest.approx(5.0 * 0.76)
    assert patient.muscle.blood_flow_l_min == pytest.approx(5.0 * 0.18)
    assert patient.fat.blood_flow_l_min == pytest.approx(5.0 * 0.06)
    assert patient.venous_blood.blood_flow_l_min == 5.0


def test_tissue_return_is_flow_weighted() -> None:
    patient = _build_patient()
    patient.vessel_rich.set_partial_pressure_fraction(0.08)
    patient.muscle.set_partial_pressure_fraction(0.04)
    patient.fat.set_partial_pressure_fraction(0.01)

    expected = 0.76 * 0.08 + 0.18 * 0.04 + 0.06 * 0.01

    assert patient.tissue_return_fraction == pytest.approx(expected)


def test_venous_blood_follows_tissue_return() -> None:
    patient = _build_patient()
    patient.vessel_rich.set_partial_pressure_fraction(0.08)
    patient.muscle.set_partial_pressure_fraction(0.04)
    patient.fat.set_partial_pressure_fraction(0.01)

    patient.advance(arterial_fraction=0.08, simulation_step_s=10.0)

    assert patient.mixed_venous_fraction > 0.0
    assert patient.mixed_venous_fraction < patient.tissue_return_fraction


def test_zero_cardiac_output_prevents_uptake() -> None:
    patient = _build_patient()
    patient.set_cardiac_output(0.0)

    amount_change = patient.advance(arterial_fraction=0.08, simulation_step_s=60.0)

    assert amount_change == 0.0
    assert patient.total_agent_amount_l == 0.0


def test_higher_cardiac_output_increases_early_uptake() -> None:
    lower_output = _build_patient()
    higher_output = _build_patient()

    lower_output.set_cardiac_output(2.5)
    higher_output.set_cardiac_output(7.5)

    lower_uptake = lower_output.advance(arterial_fraction=0.08, simulation_step_s=10.0)
    higher_uptake = higher_output.advance(arterial_fraction=0.08, simulation_step_s=10.0)

    assert higher_uptake > lower_uptake


def test_changing_output_preserves_stored_agent() -> None:
    patient = _build_patient()
    patient.advance(arterial_fraction=0.08, simulation_step_s=60.0)
    amount_before = patient.total_agent_amount_l

    patient.set_cardiac_output(7.0)

    assert patient.total_agent_amount_l == pytest.approx(amount_before)


def test_reported_change_matches_patient_storage() -> None:
    patient = _build_patient()
    amount_before = patient.total_agent_amount_l

    reported_change = patient.advance(arterial_fraction=0.08, simulation_step_s=30.0)

    assert reported_change == pytest.approx(patient.total_agent_amount_l - amount_before)


def test_reset_clears_all_patient_stores() -> None:
    patient = _build_patient()
    patient.advance(arterial_fraction=0.08, simulation_step_s=60.0)

    patient.reset()

    assert patient.total_agent_amount_l == 0.0
    assert patient.mixed_venous_fraction == 0.0
    assert patient.cardiac_output_l_min == 5.0


def test_accepts_cardiac_output_at_both_ends_of_the_supported_range() -> None:
    """Zero is the loading phase of a reference gate trajectory, so it has to
    stay reachable; the maximum is the envelope corner the same gates measure
    at."""

    patient = _build_patient()

    for cardiac_output_l_min in (0.0, MAXIMUM_CARDIAC_OUTPUT_L_MIN):
        patient.set_cardiac_output(cardiac_output_l_min)

        assert patient.cardiac_output_l_min == cardiac_output_l_min
        assert patient.venous_blood.blood_flow_l_min == cardiac_output_l_min


def test_rejects_cardiac_output_above_the_supported_range() -> None:
    """Regression (PL-0MLQ): `set_cardiac_output(1000.0)` was accepted.

    At that setting the shipped split's error coefficient is 40 times the
    documented bound, which is 91 counts of the displayed resolution — an
    alveolar readout wrong in its first decimal while presenting itself as
    settled. `docs/MODEL.md` § "Supported input ranges" records the
    measurement.
    """

    patient = _build_patient()
    supported_output_l_min = patient.cardiac_output_l_min

    with pytest.raises(SimulationConfigurationError, match="supported input range"):
        patient.set_cardiac_output(1000.0)

    assert patient.cardiac_output_l_min == supported_output_l_min
    assert patient.venous_blood.blood_flow_l_min == supported_output_l_min


def test_rejects_construction_with_cardiac_output_above_the_supported_range() -> None:
    agent = load_sevoflurane_parameters()
    parameters = replace(load_reference_adult_parameters(), default_cardiac_output_l_min=1000.0)

    with pytest.raises(SimulationConfigurationError, match="supported input range"):
        PatientCompartments.from_parameters(agent=agent, patient=parameters)
