"""Check what `capture_state()` covers, against the compartments themselves.

PL-026 made `AgentUptakeSystem.advance()` transactional by capturing every
dynamic value before the step and restoring it on failure. `docs/
WORKING_NOTES.md` records the one real risk in that design: a snapshot that
silently stops covering everything. Suppose a field is added to a compartment
later, with no matching line in its `capture_state()`. A restore would then be
partial but look complete. Unlike the failure that the restore exists to
prevent, this failure is invisible, because the values it leaves behind are
the ones the failed step wrote.

Nothing about the model can decide whether a new field is trajectory or a
setting. A person has to decide. So these tests make the decision
*unavoidable* rather than trying to make it automatically. Every field of
every compartment is classified in the table below, and three things are
checked against it:

1. the classification covers the compartment exactly, so a new field of any
   kind fails here until it is classified;
2. `restore_state()` restores exactly the fields classified as run state;
   and
3. `reset()` clears exactly those same fields, which is the cross-check. A
   new dynamic field that is wired into `reset()`, as it must be for Reset to
   work, but not into `capture_state()` fails this check.

The perturbation below writes fields directly rather than through their
setters. That is deliberate: what is being measured is which fields a method
writes, and most fields have no setter. The write itself refuses whatever the
field's constructor would refuse (`PL-LBQY`, `PL-19Y0`). So each value written
must be one that the field accepts. A value of a checked type is built as that
type again: a flow is raised by one litre a minute, and a percent or a
fraction is halved. A plain number is halved too, and each compartment below
is built holding little enough agent to leave room for that.
"""

from collections.abc import Callable
from dataclasses import dataclass, fields
from typing import Any

import pytest

from anesthesia_sim.core.agent_simulation_validation import AgentSimulationValidator
from anesthesia_sim.core.alveolar import AlveolarCompartment
from anesthesia_sim.core.blood import VenousBloodCompartment
from anesthesia_sim.core.circuit import BreathingCircuit, DeliverableFreshGasFlowRange
from anesthesia_sim.core.concentration import Fraction, Percent
from anesthesia_sim.core.governing_equations import (
    TISSUE_GROUP_COUNT,
    TissueGroupEquationSettings,
    UptakeEquationSettings,
)
from anesthesia_sim.core.patient import PatientCompartmentsState
from anesthesia_sim.core.simulation_step import SimulationStep
from anesthesia_sim.core.supported_ranges import AlveolarVentilation, CardiacOutput, FreshGasFlow
from anesthesia_sim.core.tissue import TissueGroup
from anesthesia_sim.core.uptake_system import AgentUptakeSystem, AgentUptakeSystemState


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
    """Build a circuit with a machine range declared, unlike every shipped profile.

    `data/machines/reference_circle_system.json` records `None` for the range.
    A `None` here would make the perturbation below untestable, because there
    is no second value of `NoneType` to write. Declaring a range costs nothing
    and measures more. The field is a setting, so a rollback that restored it
    would swap the machine under a run in progress (`PL-8PS6`).
    """

    return BreathingCircuit(
        circuit_volume_l=6.0,
        max_delivered_concentration_percent=Percent(100.0),
        inspired_partial_pressure_fraction=Fraction(0.013),
        deliverable_fresh_gas_flow_range=DeliverableFreshGasFlowRange(
            minimum_l_min=0.5, maximum_l_min=8.0
        ),
    )


def _alveolar_compartment() -> AlveolarCompartment:
    return AlveolarCompartment(
        gas_volume_l=2.5, alveolar_ventilation_l_min=AlveolarVentilation(4.0), agent_amount_l=0.029
    )


def _tissue_group() -> TissueGroup:
    return TissueGroup(
        name="vessel_rich",
        volume_l=6.0,
        perfusion_fraction=1.0,
        blood_gas_partition_coefficient=0.65,
        tissue_gas_partition_coefficient=1.14,
        agent_amount_l=0.41,
    )


def _venous_blood() -> VenousBloodCompartment:
    return VenousBloodCompartment(
        volume_l=5.0, blood_gas_partition_coefficient=0.65, agent_amount_l=0.23
    )


def _agent_simulation_validator() -> AgentSimulationValidator:
    return AgentSimulationValidator(
        initial_agent_l=0.31, delivered_agent_l=0.79, exhausted_agent_l=0.17
    )


COMPARTMENTS = (
    _Compartment(
        label="BreathingCircuit",
        build=_breathing_circuit,
        run_state_fields=frozenset({"inspired_partial_pressure_fraction"}),
        setting_fields=frozenset(
            {
                "circuit_volume_l",
                "fresh_gas_flow_l_min",
                "delivered_concentration_percent",
                "max_delivered_concentration_percent",
                "deliverable_fresh_gas_flow_range",
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
            }
        ),
    ),
    _Compartment(
        label="VenousBloodCompartment",
        build=_venous_blood,
        run_state_fields=frozenset({"agent_amount_l"}),
        setting_fields=frozenset({"volume_l", "blood_gas_partition_coefficient"}),
    ),
    _Compartment(
        label="AgentSimulationValidator",
        build=_agent_simulation_validator,
        # `initial_agent_l` is run state rather than a setting. It anchors the
        # current accounting period, and `reset()` writes it. Everywhere else
        # in `core/`, `reset()` is what clears run state. The two compensation
        # terms are run state too, because a running total is not complete
        # without its own compensation term (`PL-XST1`).
        run_state_fields=frozenset(
            {
                "initial_agent_l",
                "delivered_agent_l",
                "exhausted_agent_l",
                "delivered_compensation_l",
                "exhausted_compensation_l",
            }
        ),
        setting_fields=frozenset(),
    ),
)


def _perturb(value: object) -> object:
    """Return a value that its field accepts and that is sure to differ from the one given."""

    if isinstance(value, str):
        return f"{value} (perturbed)"

    if isinstance(value, (FreshGasFlow, AlveolarVentilation, CardiacOutput)):
        # Arithmetic on a flow gives a plain float, which the field refuses at
        # the write. So the perturbed flow is built as its type again.
        return type(value)(value + 1.0)

    if isinstance(value, (Percent, Fraction)):
        # The value is halved rather than raised. A fraction has no room above
        # 1, and a vaporizer maximum of 100% has no room above 100. A dial of
        # zero moves to 1%, which is less than the halved maximum written
        # after it.
        return type(value)(value / 2.0 if value else 1.0)

    if isinstance(value, float):
        # A plain float is halved for the same reason: a perfusion fraction has no room above 1.
        return value / 2.0 if value else 1.0

    if isinstance(value, DeliverableFreshGasFlowRange):
        return DeliverableFreshGasFlowRange(
            minimum_l_min=value.minimum_l_min + 1.0, maximum_l_min=value.maximum_l_min + 1.0
        )

    raise AssertionError(f"no perturbation defined for {type(value).__name__}")


def _perturb_every_field(compartment: Any) -> dict[str, object]:
    """Write a different value into every field, and return the values written."""

    perturbed: dict[str, object] = {}

    for compartment_field in fields(compartment):
        original = getattr(compartment, compartment_field.name)
        replacement = _perturb(original)

        assert replacement != original, compartment_field.name

        if compartment_field.name == "perfusion_fraction":
            # A tissue's perfusion fraction can be written only once, when the
            # group is built (`PL-Z0HN`). So the changed value is written in a
            # way that bypasses that guard.
            object.__setattr__(compartment, compartment_field.name, replacement)
        else:
            setattr(compartment, compartment_field.name, replacement)
        perturbed[compartment_field.name] = replacement

    return perturbed


def _fields_restored_to_their_original_value(compartment: Any) -> frozenset[str]:
    """Return the fields a capture-then-restore round trip brings back.

    Each field is compared with the value the compartment started with, not
    with "was written at all". So a `capture_state()` that records a constant
    instead of reading the field fails here.
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
    """Perturb every field, then return the fields that `recover()` overwrites."""

    perturbed = _perturb_every_field(compartment)
    recover()

    return frozenset(
        name for name, value in perturbed.items() if getattr(compartment, name) != value
    )


@pytest.mark.parametrize("compartment", COMPARTMENTS, ids=lambda case: case.label)
def test_every_compartment_field_is_classified(compartment: _Compartment) -> None:
    """A field that is neither run state nor a setting fails here first.

    This is the test that gives the other two their meaning. They compare
    behavior against the table, and this one checks the table against the code.
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
    """Cross-check the two lists that have to agree.

    `reset()` and `capture_state()` are written independently, and they answer
    the same question: which values carry the run rather than describe the
    model. So each one audits the other. This test catches a dynamic field that
    was added to one and not the other.
    """

    built = compartment.build()

    cleared = _fields_written_back_by(built, built.reset)

    assert cleared == compartment.run_state_fields


def _capturable_field_names(composite: Any) -> frozenset[str]:
    """Return the names of a composite's fields that are themselves capturable."""

    return frozenset(
        composite_field.name
        for composite_field in fields(composite)
        if hasattr(getattr(composite, composite_field.name), "capture_state")
    )


def test_the_patient_state_covers_every_patient_compartment() -> None:
    """A fourth tissue group could not be added without also being captured."""

    patient = AgentUptakeSystem.for_agent("sevoflurane").patient

    assert {f.name for f in fields(patient)} == {
        "cardiac_output_l_min",
        "vessel_rich",
        "muscle",
        "fat",
        "venous_blood",
    }
    assert {f.name for f in fields(PatientCompartmentsState)} == _capturable_field_names(patient)

    # Cardiac output is the one field left out, deliberately. It is a setting
    # that the user owns, and every tissue blood flow is derived from it. So
    # restoring it would undo a change that the run had accepted.
    assert "cardiac_output_l_min" not in {f.name for f in fields(PatientCompartmentsState)}


DERIVED_SYSTEM_FIELDS = frozenset({"_propagator", "_propagator_key"})
"""The system's fields that carry no trajectory and are deliberately not captured.

Both belong to the cached propagator, which is a function of the settings
alone. A step never writes the settings, and a rollback never restores them,
so the cache is still correct for whatever state a rollback leaves. The fields
are named here rather than filtered out by a rule, so that adding a field is
still a test failure that someone has to resolve. The guard below only means
something if a genuinely dynamic field cannot join this set by accident.
"""


def test_the_system_state_covers_every_part_of_the_system() -> None:
    """Apply the same guard one level up, where a sixth compartment would be added."""

    system = AgentUptakeSystem.for_agent("sevoflurane")
    field_names = {f.name for f in fields(system)}

    assert {f.name for f in fields(AgentUptakeSystemState)} == _capturable_field_names(system)
    assert field_names - DERIVED_SYSTEM_FIELDS == _capturable_field_names(system)
    assert DERIVED_SYSTEM_FIELDS <= field_names, (
        "a field named here as derived no longer exists; remove it from "
        "DERIVED_SYSTEM_FIELDS rather than leaving the exemption standing"
    )


def test_the_propagator_cache_is_not_restored_by_a_rollback() -> None:
    """A rollback leaves the cache alone, because it cannot invalidate it.

    The exemption above is safe only if it is true. What makes it true is that a
    propagator depends on settings rather than on the trajectory. Capture a
    state, change nothing but the trajectory, and restore. The same propagator
    must then still be the right one, which shows up as the next step producing
    exactly what it produced the first time.
    """

    system = AgentUptakeSystem.for_agent("sevoflurane")

    for _ in range(10):
        system.advance(SimulationStep(0.1))

    captured = system.capture_state()
    system.advance(SimulationStep(0.1))
    after_first_l = system.total_stored_agent_l

    system.restore_state(captured)
    system.advance(SimulationStep(0.1))

    assert system.total_stored_agent_l == after_first_l


def test_restoring_the_system_cannot_raise_on_a_state_a_run_produced() -> None:
    """Rollback runs while a failure is already being handled.

    For that reason it restores by direct field assignment. The behavior worth
    pinning is the consequence. A state captured from a real run restores onto
    a system whose settings have since moved, without consulting a guard that
    could reject it.
    """

    system = AgentUptakeSystem.for_agent("sevoflurane")

    for _ in range(10):
        system.advance(SimulationStep(0.1))

    state = system.capture_state()

    system.set_cardiac_output(CardiacOutput(10.0))
    system.set_fresh_gas_flow(FreshGasFlow(0.5))
    system.set_alveolar_ventilation(AlveolarVentilation(1.0))
    system.circuit.set_circuit_volume(0.5)

    system.restore_state(state)

    assert system.capture_state() == state

    # The settings the rollback must not have touched.
    assert system.patient.cardiac_output_l_min == 10.0
    assert system.circuit.fresh_gas_flow_l_min == 0.5
    assert system.alveoli.alveolar_ventilation_l_min == 1.0
    assert system.circuit.circuit_volume_l == 0.5


# `PL-R460`: the propagator cache is keyed on a raw tuple of floats rather than
# on `UptakeEquationSettings`. Building the settings object cost 7.2 us of a
# 33 us step, to answer a question whose answer is "no" on all but a few steps
# of a run. The key is safe only while it stays a bijection of the settings. If
# it stops being one, the failure is the kind this file exists for: silent, and
# invisible in the values it leaves behind. A setting with no entry in the key
# could change without the key moving, and the run would keep propagating with
# the matrix for the old setting.


def test_the_propagator_cache_key_covers_every_equation_setting() -> None:
    """One key entry per settings field, counted rather than trusted.

    `tissues` expands to its groups instead of contributing one entry.
    `TissueGroupEquationSettings.name` contributes none, because
    `build_system_matrix()` never reads it. Hence the `- 1` in each count.
    Adding a field to either settings class without an entry in
    `_propagator_cache_key()` fails here.
    """

    system = AgentUptakeSystem.for_agent("sevoflurane")

    scalar_settings = len(fields(UptakeEquationSettings)) - 1
    per_tissue = len(fields(TissueGroupEquationSettings)) - 1
    expected = 1 + scalar_settings + TISSUE_GROUP_COUNT * per_tissue

    assert len(system._propagator_cache_key(0.1)) == expected
    assert len(system.equation_settings().tissues) == TISSUE_GROUP_COUNT


@pytest.mark.parametrize(
    ("move", "description"),
    [
        (lambda s: s.circuit.set_circuit_volume(7.0), "circuit volume"),
        (lambda s: setattr(s.alveoli, "gas_volume_l", 3.0), "alveolar volume"),
        (lambda s: setattr(s.patient.venous_blood, "volume_l", 6.0), "venous volume"),
        (lambda s: s.set_fresh_gas_flow(FreshGasFlow(3.0)), "fresh gas flow"),
        (lambda s: s.set_alveolar_ventilation(AlveolarVentilation(5.0)), "alveolar ventilation"),
        (lambda s: s.set_cardiac_output(CardiacOutput(6.0)), "cardiac output"),
        (
            lambda s: setattr(s.patient.venous_blood, "blood_gas_partition_coefficient", 0.9),
            "blood:gas partition coefficient",
        ),
        (
            lambda s: s.set_delivered_concentration_percent(Percent(3.0)),
            "delivered concentration percent",
        ),
        (
            lambda s: setattr(s.circuit, "max_delivered_concentration_percent", Percent(10.0)),
            "the vaporizer maximum, which no equation reads and the record carries (PL-BBMG)",
        ),
        (lambda s: setattr(s.patient.tissues[0], "volume_l", 9.0), "a tissue volume"),
        (
            lambda s: object.__setattr__(s.patient.tissues[1], "perfusion_fraction", 0.2),
            "a tissue blood flow, moved through a perfusion fraction written past its guard",
        ),
        (
            lambda s: setattr(s.patient.tissues[2], "tissue_gas_partition_coefficient", 90.0),
            "a tissue partition coefficient, moved through the gas coefficient it derives from",
        ),
    ],
)
def test_moving_any_setting_moves_the_propagator_cache_key(
    move: Callable[[AgentUptakeSystem], None], description: str
) -> None:
    """Check the property that the counting test above cannot establish.

    Where no setter exists, the case writes straight onto the compartment. That
    path has no guard of its own, and it is the one the key exists to catch.
    `_propagator_for()` compares values rather than trusting a setter to
    invalidate the cache. So a setting changed around the control surface must
    move the key just the same.
    """

    system = AgentUptakeSystem.for_agent("sevoflurane")
    before = system._propagator_cache_key(0.1)

    move(system)

    assert system._propagator_cache_key(0.1) != before, f"{description} left the key unchanged"


def test_a_step_after_a_setting_moved_propagates_with_the_new_matrix() -> None:
    """Check end to end that the key change affects the propagator, not just the tuple.

    Both systems take one step, have their ventilation changed, and take a
    second step. They differ only in that `rebuilt` has its propagator cache
    cleared before the second step, so it must build the matrix afresh. The
    two must agree. If the cache in `changed` returned the stale propagator,
    they would not.
    """

    changed = AgentUptakeSystem.for_agent("sevoflurane")
    changed.advance(SimulationStep(0.1))
    changed.set_alveolar_ventilation(AlveolarVentilation(8.0))
    changed.advance(SimulationStep(0.1))

    rebuilt = AgentUptakeSystem.for_agent("sevoflurane")
    rebuilt.advance(SimulationStep(0.1))
    rebuilt.set_alveolar_ventilation(AlveolarVentilation(8.0))
    rebuilt._propagator = None
    rebuilt._propagator_key = None
    rebuilt.advance(SimulationStep(0.1))

    assert changed.state_vector() == rebuilt.state_vector()
