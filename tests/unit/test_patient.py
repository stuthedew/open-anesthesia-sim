from copy import deepcopy
from dataclasses import replace

import pytest

from anesthesia_sim.core.concentration import Fraction
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.parameters import (
    load_agent_parameters,
    load_reference_adult_parameters,
    load_sevoflurane_parameters,
)
from anesthesia_sim.core.patient import FLOW_FRACTION_TOLERANCE, PatientCompartments
from anesthesia_sim.core.simulation_step import SimulationStep
from anesthesia_sim.core.supported_ranges import MAXIMUM_CARDIAC_OUTPUT_L_MIN, CardiacOutput
from anesthesia_sim.core.uptake_system import AgentUptakeSystem


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


@pytest.mark.parametrize(
    ("agent_id", "blood_gas", "tissue_gas"),
    [
        # Each agent's blood:gas coefficient and its vessel-rich, muscle and
        # fat tissue:gas coefficients, typed from the agent's data file under
        # src/anesthesia_sim/data/agents/ on 2026-10-17. The files' `sources`
        # notes say where each value comes from.
        ("sevoflurane", 0.65, (1.1, 2.4, 34.0)),
        ("desflurane", 0.42, (0.54, 0.97, 13.0)),
        ("isoflurane", 1.3, (2.1, 4.5, 70.0)),
    ],
)
def test_each_tissue_group_takes_its_own_agents_coefficients(
    agent_id: str, blood_gas: float, tissue_gas: tuple[float, float, float]
) -> None:
    """Each tissue group is built with its own coefficient for the running agent.

    `PatientCompartments.from_parameters` maps an agent's three tissue:gas
    coefficients onto the three groups. Before this test, only golden numbers
    measured from the code's own output caught a group built with another
    group's coefficient, so a mapping that was wrong when they were measured
    would have been certified (`PL-WMN7`). Here the expected values are typed
    from the data files. All three agents are checked, so a mapping that read
    one agent's values for every agent fails too.

    The tissue:blood coefficient is the tissue:gas coefficient divided by the
    blood:gas one, since `docs/MODEL.md` § "Tissue compartments" writes a
    tissue's capacity both as V x tissue:blood x blood:gas and as
    V x tissue:gas. The test does that division itself. The perfusion
    fractions are the reference adult's, typed from
    src/anesthesia_sim/data/patients/reference_adult.json.
    """

    patient = PatientCompartments.from_parameters(
        agent=load_agent_parameters(agent_id), patient=load_reference_adult_parameters()
    )
    groups = (patient.vessel_rich, patient.muscle, patient.fat)

    assert [group.name for group in groups] == ["vessel_rich", "muscle", "fat"]
    assert [group.tissue_gas_partition_coefficient for group in groups] == list(tissue_gas)
    assert [group.blood_gas_partition_coefficient for group in groups] == [blood_gas] * 3
    assert [group.tissue_blood_partition_coefficient for group in groups] == [
        coefficient / blood_gas for coefficient in tissue_gas
    ]
    assert [group.perfusion_fraction for group in groups] == [0.76, 0.18, 0.06]
    assert patient.venous_blood.blood_gas_partition_coefficient == blood_gas


def test_allocates_cardiac_output_to_tissues() -> None:
    patient = _build_patient()
    cardiac_output_l_min = patient.cardiac_output_l_min

    assert patient.vessel_rich.blood_flow_l_min_at(cardiac_output_l_min) == pytest.approx(
        5.0 * 0.76
    )
    assert patient.muscle.blood_flow_l_min_at(cardiac_output_l_min) == pytest.approx(5.0 * 0.18)
    assert patient.fat.blood_flow_l_min_at(cardiac_output_l_min) == pytest.approx(5.0 * 0.06)
    assert cardiac_output_l_min == 5.0


def _assert_perfused_at_5_l_min(patient: PatientCompartments) -> None:
    assert patient.cardiac_output_l_min == 5.0
    assert [
        tissue.blood_flow_l_min_at(patient.cardiac_output_l_min) for tissue in patient.tissues
    ] == [5.0 * tissue.perfusion_fraction for tissue in patient.tissues]


def test_replace_leaves_the_original_perfused_at_its_own_output() -> None:
    """Regression (`PL-Z0T3`): a copy at another output rewrote the original's flows.

    `dataclasses.replace` hands its copy the original's own tissue groups and
    venous pool, and the constructor set the copy's flows on them, so the
    original went on recording 5 L/min while perfused at 10, and its next step
    was refused as a numerical failure though nothing numerical had failed.
    `PL-Z0T3` refused such a copy. Since `PL-HQF5` no compartment stores a
    flow, so the copy is built, shares the compartments, and is perfused at
    its own output while the original stays perfused at its own.
    """

    system = AgentUptakeSystem.default()
    patient = system.patient

    copied = replace(patient, cardiac_output_l_min=CardiacOutput(10.0))

    assert copied.vessel_rich is patient.vessel_rich
    assert copied.vessel_rich.blood_flow_l_min_at(copied.cardiac_output_l_min) == pytest.approx(
        10.0 * 0.76
    )
    _assert_perfused_at_5_l_min(patient)
    system.advance(SimulationStep(0.1))


def test_a_deep_copy_takes_another_output_without_the_original() -> None:
    """A copy with compartments of its own takes another output, and the original keeps its own."""

    system = AgentUptakeSystem.default()
    patient = system.patient
    copied = deepcopy(patient)

    copied.set_cardiac_output(CardiacOutput(10.0))

    assert copied.cardiac_output_l_min == 10.0
    _assert_perfused_at_5_l_min(patient)
    system.advance(SimulationStep(0.1))


def test_a_compartment_blood_flow_is_the_patients_output_and_nothing_else() -> None:
    """Changing the output moves every compartment's flow, and no write moves one alone.

    Each compartment stored its own flow until `PL-HQF5`. A tissue's or the
    venous pool's `set_blood_flow` could then leave a flow that the cardiac
    output did not give it. The tissue half was refused only at the next step.
    The venous half was never refused, because no step reads the pool's flow.
    Neither compartment now has a flow field or a setter. Each tissue's flow
    is formed from its patient's output when it is read. The expected flows
    are the reference adult's fractions (0.76, 0.18 and 0.06, typed from
    `data/patients/reference_adult.json`) times the output, worked here.
    """

    patient = _build_patient()

    for compartment in (*patient.tissues, patient.venous_blood):
        assert not hasattr(compartment, "blood_flow_l_min")
        assert not hasattr(compartment, "set_blood_flow")

        with pytest.raises(AttributeError, match="blood_flow_l_min"):
            compartment.blood_flow_l_min = 99.0

    for cardiac_output_l_min, expected_l_min in (
        (5.0, (3.8, 0.9, 0.3)),
        (7.5, (5.7, 1.35, 0.45)),
        (0.0, (0.0, 0.0, 0.0)),
    ):
        patient.set_cardiac_output(CardiacOutput(cardiac_output_l_min))

        assert [
            tissue.blood_flow_l_min_at(patient.cardiac_output_l_min) for tissue in patient.tissues
        ] == pytest.approx(expected_l_min, abs=1e-12)


def test_a_perfusion_fraction_written_on_a_built_patient_is_refused() -> None:
    """A fraction cannot be changed, or a new tissue group swapped in, once the patient is built.

    Regression (`PL-Z0HN`). `vessel_rich.perfusion_fraction = 0.5` was accepted
    on a built patient, so the fractions summed to 0.74. Nothing checked them
    again, so every later cardiac output change was refused, and its
    write-back moved the vessel-rich flow from 3.8 to 2.5 L/min under a
    banner saying nothing had changed. A tissue group now refuses a second
    write of its fraction, and the patient refuses a replacement group that
    would leave the fractions summing to anything but 1. Deleting the
    fraction or the group first is refused too, since a write after a
    deletion would bypass both checks. Every refusal leaves the patient as it
    was, perfused at 3.8, 0.9 and 0.3 L/min.
    """

    patient = _build_patient()
    vessel_rich = patient.vessel_rich

    with pytest.raises(
        SimulationConfigurationError,
        match="^the vessel_rich tissue group's perfusion fraction of 0.76 cannot be written "
        "again, as 0.5, once the group is built",
    ):
        vessel_rich.perfusion_fraction = 0.5

    with pytest.raises(
        SimulationConfigurationError,
        match="^the vessel_rich tissue group's perfusion_fraction cannot be deleted",
    ):
        del vessel_rich.perfusion_fraction

    with pytest.raises(
        SimulationConfigurationError, match="^the patient's vessel_rich cannot be deleted"
    ):
        del patient.vessel_rich

    with pytest.raises(TypeError, match="^fat of 1.0 has type float, not TissueGroup$"):
        patient.fat = 1.0  # type: ignore[assignment]

    with pytest.raises(
        SimulationConfigurationError, match="^tissue perfusion fractions must sum to 1$"
    ):
        patient.vessel_rich = replace(vessel_rich, perfusion_fraction=0.5)

    assert patient.vessel_rich is vessel_rich
    assert vessel_rich.perfusion_fraction == 0.76
    _assert_perfused_at_5_l_min(patient)

    patient.vessel_rich = replace(vessel_rich, volume_l=7.0)

    assert patient.vessel_rich.volume_l == 7.0
    assert patient.total_perfusion_fraction == pytest.approx(1.0, abs=FLOW_FRACTION_TOLERANCE)


def test_tissue_return_is_flow_weighted() -> None:
    patient = _build_patient()
    patient.vessel_rich.set_partial_pressure_fraction(Fraction(0.08))
    patient.muscle.set_partial_pressure_fraction(Fraction(0.04))
    patient.fat.set_partial_pressure_fraction(Fraction(0.01))

    expected = 0.76 * 0.08 + 0.18 * 0.04 + 0.06 * 0.01

    assert patient.tissue_return_partial_pressure_fraction == pytest.approx(expected)


def _load_patient_stores(patient: PatientCompartments) -> None:
    """Put agent in every patient compartment without stepping anything.

    The setters rather than a step, because `PL-74R0` deleted
    `PatientCompartments.advance()`: it was an operator split whose answer
    moved with the step size, not a closed form. What the tests below assert
    is that a *setting* leaves stored agent alone and that `reset()` clears
    it, neither of which needs a trajectory to reach a loaded state.
    """

    patient.vessel_rich.set_partial_pressure_fraction(Fraction(0.08))
    patient.muscle.set_partial_pressure_fraction(Fraction(0.04))
    patient.fat.set_partial_pressure_fraction(Fraction(0.01))
    patient.venous_blood.set_partial_pressure_fraction(Fraction(0.05))


def test_the_patient_side_exposes_no_step_of_its_own() -> None:
    """Regression (`PL-74R0`): `PatientCompartments.advance()` is gone.

    A run advances one state vector through `AgentUptakeSystem.advance()`.
    This class composing its own step is what made it a split rather than a
    closed form, so the absence is the fix and not an accident of refactoring
    - `core/__init__.py` carries the measurement that decided it.
    """

    assert not hasattr(PatientCompartments, "advance")


def test_changing_output_preserves_stored_agent() -> None:
    patient = _build_patient()
    _load_patient_stores(patient)
    amount_before = patient.total_agent_amount_l

    patient.set_cardiac_output(CardiacOutput(7.0))

    assert amount_before > 0.0
    assert patient.total_agent_amount_l == pytest.approx(amount_before)


def test_reset_clears_all_patient_stores() -> None:
    patient = _build_patient()
    _load_patient_stores(patient)

    patient.reset()

    assert patient.total_agent_amount_l == 0.0
    assert patient.mixed_venous_partial_pressure_fraction == 0.0
    assert patient.cardiac_output_l_min == 5.0


def test_accepts_cardiac_output_at_both_ends_of_the_supported_range() -> None:
    """Zero is the loading phase of a reference gate trajectory, so it has to
    stay reachable; the maximum is the envelope corner the same gates measure
    at."""

    patient = _build_patient()

    for cardiac_output_l_min in (0.0, MAXIMUM_CARDIAC_OUTPUT_L_MIN):
        patient.set_cardiac_output(CardiacOutput(cardiac_output_l_min))

        assert patient.cardiac_output_l_min == cardiac_output_l_min


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
        patient.set_cardiac_output(CardiacOutput(1000.0))

    assert patient.cardiac_output_l_min == supported_output_l_min


def test_rejects_construction_with_cardiac_output_above_the_supported_range() -> None:
    agent = load_sevoflurane_parameters()
    parameters = replace(load_reference_adult_parameters(), default_cardiac_output_l_min=1000.0)

    with pytest.raises(SimulationConfigurationError, match="supported input range"):
        PatientCompartments.from_parameters(agent=agent, patient=parameters)
