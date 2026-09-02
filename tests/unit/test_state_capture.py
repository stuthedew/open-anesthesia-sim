"""What `capture_state()` covers, checked against the compartments themselves.

PL-026 made `RespiratorySystem.advance()` transactional by capturing every
dynamic value before the step and restoring it on failure. `docs/
WORKING_NOTES.md` records the one real risk in that design: a snapshot that
silently stops covering everything. A field added to a compartment later,
with no matching line in its `capture_state()`, would leave a partial
restore that looks like a complete one - and unlike the failure it exists to
prevent, that one is invisible, because the values it leaves behind are the
ones the failed step wrote.

Nothing about the model can decide whether a new field is trajectory or
setting; a person has to. So these tests make the decision *unavoidable*
rather than trying to make it automatically. Every field of every
compartment is classified in the table below, and three things are checked
against it:

1. the classification covers the compartment exactly, so a new field of any
   kind fails here until it is classified;
2. `restore_state()` restores exactly the fields classified as run state;
   and
3. `reset()` clears exactly those same fields, which is the cross-check -
   a new dynamic field wired into `reset()`, as it must be for Reset to
   work, but not into `capture_state()`, fails on this one.

The perturbation below writes fields directly rather than through their
setters, deliberately: what is being measured is which fields a method
writes, and a setter would reject most of the values used to measure it.
"""

from collections.abc import Callable
from dataclasses import dataclass, fields
from typing import Any

import pytest

from anesthesia_sim.core.agent_simulation_validation import AgentSimulationValidator
from anesthesia_sim.core.alveolar import AlveolarCompartment
from anesthesia_sim.core.blood import VenousBloodCompartment
from anesthesia_sim.core.circuit import BreathingCircuit
from anesthesia_sim.core.patient import PatientCompartmentsState
from anesthesia_sim.core.respiratory_system import RespiratorySystem, RespiratorySystemState
from anesthesia_sim.core.tissue import TissueGroup


@dataclass(frozen=True)
class _Compartment:
    """One compartment and the classification of every field it declares."""

    label: str
    build: Callable[[], Any]
    run_state_fields: frozenset[str]
    setting_fields: frozenset[str]


# Every compartment below is built mid-run rather than empty, and no two run
# state values are the same number. An empty compartment would let a
# `capture_state()` that returned a hardcoded default pass as a correct one,
# because the default and the captured value would agree.


def _breathing_circuit() -> BreathingCircuit:
    return BreathingCircuit(circuit_concentration_fraction=0.013)


def _alveolar_compartment() -> AlveolarCompartment:
    return AlveolarCompartment(agent_amount_l=0.029)


def _tissue_group() -> TissueGroup:
    return TissueGroup(
        name="vessel_rich",
        volume_l=6.0,
        perfusion_fraction=1.0,
        blood_gas_partition_coefficient=0.65,
        tissue_gas_partition_coefficient=1.14,
        blood_flow_l_min=3.75,
        agent_amount_l=0.41,
    )


def _venous_blood() -> VenousBloodCompartment:
    return VenousBloodCompartment(
        volume_l=5.0,
        blood_gas_partition_coefficient=0.65,
        blood_flow_l_min=5.0,
        agent_amount_l=0.23,
    )


def _agent_simulation_validator() -> AgentSimulationValidator:
    return AgentSimulationValidator(
        initial_agent_l=0.31, delivered_agent_l=0.79, exhausted_agent_l=0.17
    )


COMPARTMENTS = (
    _Compartment(
        label="BreathingCircuit",
        build=_breathing_circuit,
        run_state_fields=frozenset({"circuit_concentration_fraction"}),
        setting_fields=frozenset(
            {
                "circuit_volume_l",
                "fresh_gas_flow_l_min",
                "delivered_concentration_fraction",
                "max_delivered_concentration_fraction",
            }
        ),
    ),
    _Compartment(
        label="AlveolarCompartment",
        build=_alveolar_compartment,
        run_state_fields=frozenset({"agent_amount_l"}),
        setting_fields=frozenset({"gas_volume_l", "alveolar_ventilation_l_min"}),
    ),
    _Compartment(
        label="TissueGroup",
        build=_tissue_group,
        run_state_fields=frozenset({"agent_amount_l"}),
        setting_fields=frozenset(
            {
                "name",
                "volume_l",
                "perfusion_fraction",
                "blood_gas_partition_coefficient",
                "tissue_gas_partition_coefficient",
                "blood_flow_l_min",
            }
        ),
    ),
    _Compartment(
        label="VenousBloodCompartment",
        build=_venous_blood,
        run_state_fields=frozenset({"agent_amount_l"}),
        setting_fields=frozenset(
            {"volume_l", "blood_gas_partition_coefficient", "blood_flow_l_min"}
        ),
    ),
    _Compartment(
        label="AgentSimulationValidator",
        build=_agent_simulation_validator,
        # `initial_agent_l` is run state rather than a setting: it anchors
        # the current accounting period, and `reset()` - which is what
        # clears run state everywhere else in `core/` - is what writes it.
        run_state_fields=frozenset({"initial_agent_l", "delivered_agent_l", "exhausted_agent_l"}),
        setting_fields=frozenset(),
    ),
)


def _perturb(value: object) -> object:
    """Return a value guaranteed to differ from the one given."""

    if isinstance(value, str):
        return f"{value} (perturbed)"

    if isinstance(value, float):
        return value + 1.0

    raise AssertionError(f"no perturbation defined for {type(value).__name__}")


def _perturb_every_field(compartment: Any) -> dict[str, object]:
    """Write a different value into every field; return what was written."""

    perturbed: dict[str, object] = {}

    for compartment_field in fields(compartment):
        original = getattr(compartment, compartment_field.name)
        replacement = _perturb(original)

        assert replacement != original, compartment_field.name

        setattr(compartment, compartment_field.name, replacement)
        perturbed[compartment_field.name] = replacement

    return perturbed


def _fields_restored_to_their_original_value(compartment: Any) -> frozenset[str]:
    """Return the fields a capture-then-restore round trip brings back.

    Measured against the value the compartment started with rather than
    against "was written at all", so that a `capture_state()` recording a
    constant instead of reading the field fails here.
    """

    state = compartment.capture_state()
    original = {
        compartment_field.name: getattr(compartment, compartment_field.name)
        for compartment_field in fields(compartment)
    }

    _perturb_every_field(compartment)
    compartment.restore_state(state)

    return frozenset(
        name for name, value in original.items() if getattr(compartment, name) == value
    )


def _fields_written_back_by(compartment: Any, recover: Callable[[], None]) -> frozenset[str]:
    """Return the fields `recover()` writes, of those perturbed first."""

    perturbed = _perturb_every_field(compartment)
    recover()

    return frozenset(
        name for name, value in perturbed.items() if getattr(compartment, name) != value
    )


@pytest.mark.parametrize("compartment", COMPARTMENTS, ids=lambda case: case.label)
def test_every_compartment_field_is_classified(compartment: _Compartment) -> None:
    """A field that is neither run state nor a setting fails here first.

    This is the test that makes the other two mean something: they compare
    behavior against the table, and this one holds the table to the code.
    """

    declared = {compartment_field.name for compartment_field in fields(compartment.build())}

    assert not (compartment.run_state_fields & compartment.setting_fields)
    assert compartment.run_state_fields | compartment.setting_fields == declared


@pytest.mark.parametrize("compartment", COMPARTMENTS, ids=lambda case: case.label)
def test_capture_and_restore_cover_exactly_the_run_state(compartment: _Compartment) -> None:
    """Every dynamic field comes back, and no setting is undone with it."""

    built = compartment.build()

    restored = _fields_restored_to_their_original_value(built)

    assert restored == compartment.run_state_fields


@pytest.mark.parametrize("compartment", COMPARTMENTS, ids=lambda case: case.label)
def test_reset_clears_exactly_what_capture_state_captures(compartment: _Compartment) -> None:
    """The cross-check on the two lists that have to agree.

    `reset()` and `capture_state()` are written independently and answer the
    same question - which values carry the run rather than describe the
    model - so they are each other's audit. A dynamic field added to one and
    not the other is what this catches.
    """

    built = compartment.build()

    cleared = _fields_written_back_by(built, built.reset)

    assert cleared == compartment.run_state_fields


def _capturable_field_names(composite: Any) -> frozenset[str]:
    """Names of a composite's fields that are themselves capturable."""

    return frozenset(
        composite_field.name
        for composite_field in fields(composite)
        if hasattr(getattr(composite, composite_field.name), "capture_state")
    )


def test_the_patient_state_covers_every_patient_compartment() -> None:
    """A fourth tissue group would have to be captured to be added."""

    patient = RespiratorySystem.for_agent("sevoflurane").patient

    assert {f.name for f in fields(patient)} == {
        "cardiac_output_l_min",
        "vessel_rich",
        "muscle",
        "fat",
        "venous_blood",
    }
    assert {f.name for f in fields(PatientCompartmentsState)} == _capturable_field_names(patient)

    # Cardiac output is the one field left out, and deliberately: it is a
    # setting the user owns, and every tissue blood flow is derived from it,
    # so restoring it would undo a change the run had accepted.
    assert "cardiac_output_l_min" not in {f.name for f in fields(PatientCompartmentsState)}


def test_the_system_state_covers_every_part_of_the_system() -> None:
    """Same guard one level up, where a sixth compartment would be added."""

    system = RespiratorySystem.for_agent("sevoflurane")

    assert {f.name for f in fields(RespiratorySystemState)} == _capturable_field_names(system)
    assert {f.name for f in fields(system)} == _capturable_field_names(system)


def test_restoring_the_system_cannot_raise_on_a_state_a_run_produced() -> None:
    """Rollback runs while a failure is already being handled.

    It restores by direct field assignment for that reason, and the
    behavior worth pinning is the consequence: a state captured from a real
    run restores onto a system whose settings have since moved, without
    consulting a guard that could reject it.
    """

    system = RespiratorySystem.for_agent("sevoflurane")

    for _ in range(10):
        system.advance(0.1)

    state = system.capture_state()

    system.set_cardiac_output(10.0)
    system.set_fresh_gas_flow(0.5)
    system.set_alveolar_ventilation(1.0)
    system.circuit.set_circuit_volume(0.5)

    system.restore_state(state)

    assert system.capture_state() == state

    # The settings the rollback must not have touched.
    assert system.patient.cardiac_output_l_min == 10.0
    assert system.circuit.fresh_gas_flow_l_min == 0.5
    assert system.alveoli.alveolar_ventilation_l_min == 1.0
    assert system.circuit.circuit_volume_l == 0.5
