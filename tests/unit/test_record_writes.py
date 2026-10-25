"""Each mutable record in `core/` says how a later write to each of its fields is kept safe.

Some records check a rule across their fields only when they are built. A later
write can then leave such a record breaking the rule. Four defects had that
shape (`PL-N7MM`). A copied patient rewrote its original's flows. A run clock
was assigned in a way that bypassed its check. A tissue perfusion fraction was
changed on a built patient. A core setting was changed past the run's recorded
definition.

So these tests walk every class in `core/`. A class whose instances cannot be
written passes without an entry. Such classes are frozen dataclasses, frozen
Pydantic payloads, exceptions, and value types such as `Percent` that hold no
field. Every other class must appear in `WRITES` below, with one entry for each
of its fields. Each entry says which of six kinds of write the field takes:

- `ONCE`: the field is written when the record is built, and a later write is
  refused, even of the value it already holds.
- `CHECKED`: a later write is checked against the record's rule. The entry
  gives a value that passes the field's own check but breaks the rule, and the
  test writes it and expects a refusal.
- `ACCOUNTED`: the field holds agent, or a total of it, and the rule that
  ties it to the other fields is the uptake system's accounting identity. The
  system checks that identity at every step and at every read of its
  accounting. A failure at a step halts the run. The entry builds a system
  holding agent, finds the record in it and gives a value that breaks the
  identity. The test writes it and expects the next accounting read to fail.
- `OWN`: no rule ties the field to another field, so the field's own check is
  all that a write needs. The entry says why.
- `PRIVATE`: the field is private to its module and written only by the
  record's own methods. The entry says why.
- `GAP`: a rule ties the field to another field and nothing checks it yet. The
  entry names the open item that will.

A new mutable class, or a new field on one, fails the first test until it is
given an entry. A guard that stops refusing a write fails the test for its
kind.
"""

from __future__ import annotations

import dataclasses
import importlib
import inspect
from collections.abc import Callable, Iterable
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

import pytest
from pydantic import BaseModel

from anesthesia_sim import core
from anesthesia_sim.core.alveolar import AlveolarCompartment
from anesthesia_sim.core.blood import VenousBloodCompartment
from anesthesia_sim.core.circuit import BreathingCircuit, DeliverableFreshGasFlowRange
from anesthesia_sim.core.concentration import Percent
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.parameters import load_agent_parameters, load_reference_adult_parameters
from anesthesia_sim.core.patient import PatientCompartments
from anesthesia_sim.core.simulation import SimulationState
from anesthesia_sim.core.simulation_step import MAXIMUM_SIMULATION_STEP_S, SimulationStep
from anesthesia_sim.core.supported_ranges import (
    AlveolarVentilation,
    CardiacOutput,
    FreshGasFlow,
    StepCount,
)
from anesthesia_sim.core.tissue import TissueGroup
from anesthesia_sim.core.uptake_system import AgentUptakeSystem

CORE = Path(core.__file__).resolve().parent

ONCE = "once"
CHECKED = "checked"
ACCOUNTED = "accounted"
OWN = "own"
PRIVATE = "private"
GAP = "gap"


@dataclass(frozen=True)
class Write:
    """How one field of a mutable record is kept safe when it is written after the record is built.

    Attributes:
        kind: one of the six kinds the module docstring describes.
        build: for `ONCE` and `CHECKED`, a function that builds the record.
            For `ACCOUNTED`, a function that builds an uptake system holding
            agent.
        breaking: for `CHECKED` and `ACCOUNTED`, a function that returns, for
            the record, a value that passes the field's own check but breaks
            the record's rule.
        locate: for `ACCOUNTED`, a function that returns the record from the
            system that `build` returns.
        why: for `ACCOUNTED`, `OWN`, `PRIVATE` and `GAP`, why a write to the
            field needs no check at the moment it is made. A `GAP` entry names
            its open item.
    """

    kind: str
    build: Callable[[], Any] | None = None
    breaking: Callable[[Any], object] | None = None
    locate: Callable[[AgentUptakeSystem], Any] | None = None
    why: str = ""


def _tissue_group() -> TissueGroup:
    """A group holding 4 L of agent in a capacity of 20 L (10 L times a coefficient of 2)."""

    return TissueGroup(
        name="muscle",
        volume_l=10.0,
        perfusion_fraction=0.2,
        blood_gas_partition_coefficient=0.65,
        tissue_gas_partition_coefficient=2.0,
        agent_amount_l=4.0,
    )


def _venous_blood() -> VenousBloodCompartment:
    """A pool holding 1 L of agent in a capacity of 1.3 L (2 L times a coefficient of 0.65)."""

    return VenousBloodCompartment(
        volume_l=2.0, blood_gas_partition_coefficient=0.65, agent_amount_l=1.0
    )


def _alveoli() -> AlveolarCompartment:
    """Alveoli holding 0.5 L of agent in 2.5 L of gas."""

    return AlveolarCompartment(
        gas_volume_l=2.5, alveolar_ventilation_l_min=AlveolarVentilation(4.0), agent_amount_l=0.5
    )


def _circuit() -> BreathingCircuit:
    """A circuit dialled to 2% under an 8% maximum, at 2 L/min on a 0.5 to 8 L/min machine."""

    return BreathingCircuit(
        circuit_volume_l=6.0,
        fresh_gas_flow_l_min=FreshGasFlow(2.0),
        delivered_concentration_percent=Percent(2.0),
        max_delivered_concentration_percent=Percent(8.0),
        deliverable_fresh_gas_flow_range=DeliverableFreshGasFlowRange(
            minimum_l_min=0.5, maximum_l_min=8.0
        ),
    )


def _patient() -> PatientCompartments:
    return PatientCompartments.from_parameters(
        agent=load_agent_parameters("sevoflurane"), patient=load_reference_adult_parameters()
    )


def _halved_fraction(field: str) -> Callable[[PatientCompartments], TissueGroup]:
    """Return a copy of the patient's group `field` at half its perfusion fraction."""

    def breaking(patient: PatientCompartments) -> TissueGroup:
        group: TissueGroup = getattr(patient, field)

        return replace(group, perfusion_fraction=group.perfusion_fraction / 2)

    return breaking


def _system_holding_agent() -> AgentUptakeSystem:
    """The default sevoflurane system after 20 of its largest steps at its opening settings."""

    system = AgentUptakeSystem.default()

    for _ in range(20):
        system.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))

    return system


def _accounted(
    locate: Callable[[AgentUptakeSystem], Any], breaking: Callable[[Any], object], why: str
) -> Write:
    return Write(ACCOUNTED, _system_holding_agent, breaking, locate, why)


_ACCOUNTING = (
    "The identity ties the field to every other store of agent in the system, and the "
    "system checks it at every step and at every read of its accounting."
)


def _state_part_way() -> SimulationState:
    return SimulationState(step_count=StepCount(3), simulation_step_s=SimulationStep(0.1))


WRITES: dict[str, dict[str, Write]] = {
    "agent_simulation_validation.AgentSimulationValidator": {
        total: _accounted(
            lambda system: system.agent_simulation_validator,
            lambda validator, total=total: getattr(validator, total) + 1.0,
            _ACCOUNTING,
        )
        for total in ("initial_agent_l", "delivered_agent_l", "exhausted_agent_l")
    }
    | {
        term: Write(
            OWN,
            why=(
                "The term only corrects the next addition to its total, by less than one unit "
                "in the last place of that total. No rule ties its value to another field. A "
                "wrong term moves the next total, which the accounting identity checks at that "
                "step (PL-XST1)."
            ),
        )
        for term in ("delivered_compensation_l", "exhausted_compensation_l")
    },
    "alveolar.AlveolarCompartment": {
        "gas_volume_l": Write(CHECKED, _alveoli, lambda alveoli: 0.25),
        "alveolar_ventilation_l_min": Write(
            OWN, why="The ventilation is tied to no other field. Its type carries its range check."
        ),
        "agent_amount_l": Write(CHECKED, _alveoli, lambda alveoli: 5.0),
    },
    "blood.VenousBloodCompartment": {
        "volume_l": Write(CHECKED, _venous_blood, lambda blood: 1.0),
        "blood_gas_partition_coefficient": Write(CHECKED, _venous_blood, lambda blood: 0.1),
        "agent_amount_l": Write(CHECKED, _venous_blood, lambda blood: 2.0),
    },
    "circuit.BreathingCircuit": {
        "circuit_volume_l": _accounted(
            lambda system: system.circuit,
            lambda circuit: circuit.circuit_volume_l * 2.0,
            "The circuit stores its agent as a fraction of its volume, so a volume written "
            "directly changes the agent the circuit holds. `set_circuit_volume` is the "
            "write that conserves the agent. " + _ACCOUNTING,
        ),
        "fresh_gas_flow_l_min": Write(CHECKED, _circuit, lambda circuit: FreshGasFlow(9.0)),
        "delivered_concentration_percent": Write(CHECKED, _circuit, lambda circuit: Percent(9.0)),
        "inspired_partial_pressure_fraction": Write(
            OWN, why="The inspired fraction is tied to no other field of the circuit."
        ),
        "max_delivered_concentration_percent": Write(
            CHECKED, _circuit, lambda circuit: Percent(1.0)
        ),
        "deliverable_fresh_gas_flow_range": Write(
            CHECKED,
            _circuit,
            lambda circuit: DeliverableFreshGasFlowRange(minimum_l_min=3.0, maximum_l_min=8.0),
        ),
    },
    "patient.PatientCompartments": {
        "cardiac_output_l_min": Write(
            CHECKED, _patient, lambda patient: CardiacOutput(patient.cardiac_output_l_min + 1.0)
        ),
        "vessel_rich": Write(CHECKED, _patient, _halved_fraction("vessel_rich")),
        "muscle": Write(CHECKED, _patient, _halved_fraction("muscle")),
        "fat": Write(CHECKED, _patient, _halved_fraction("fat")),
        "venous_blood": Write(
            GAP,
            why=(
                "A replaced pool's agent is held to the accounting identity, which the "
                "system checks at every step and read. Its blood:gas coefficient should "
                "equal the tissue groups' own copies, and nothing checks that, at a write "
                "or when the patient is built (PL-YXGX)."
            ),
        ),
    },
    "run_definition.RunDefinition": {
        field: Write(
            PRIVATE, why="Written only by the run definition's own methods, which hold its rules."
        )
        for field in ("_last_window_propagators", "_reached_s", "_segments")
    },
    "run_definition._WindowPropagators": {
        field: Write(
            PRIVATE,
            why="A private helper built and discarded inside one call to evaluate_anchored.",
        )
        for field in ("_kept", "used")
    },
    "simulation.SimulationState": {
        "uptake_system": Write(ONCE, SimulationState),
        "step_count": Write(CHECKED, SimulationState, lambda state: StepCount(1)),
        "simulation_step_s": Write(CHECKED, _state_part_way, lambda state: None),
    },
    "tissue.TissueGroup": {
        "name": Write(OWN, why="The name labels the group's messages and enters no rule."),
        "volume_l": Write(CHECKED, _tissue_group, lambda group: 1.0),
        "perfusion_fraction": Write(ONCE, _tissue_group),
        "blood_gas_partition_coefficient": Write(
            GAP,
            why=(
                "No rule of the group ties it to another of the group's fields. Its "
                "agreement with the venous pool's copy is not checked anywhere (PL-YXGX)."
            ),
        ),
        "tissue_gas_partition_coefficient": Write(CHECKED, _tissue_group, lambda group: 0.1),
        "agent_amount_l": Write(CHECKED, _tissue_group, lambda group: 40.0),
    },
    "uptake_system.AgentUptakeSystem": {
        **{
            part: Write(ONCE, AgentUptakeSystem.default)
            for part in ("circuit", "alveoli", "patient", "agent_simulation_validator")
        },
        **{
            field: Write(
                PRIVATE,
                why=(
                    "The cached propagator and its key, written by _propagator_for and "
                    "keyed by the settings they were built from."
                ),
            )
            for field in ("_propagator", "_propagator_key")
        },
    },
}


def holds_no_writable_field(cls: type) -> bool:
    """Return whether no field of an instance of `cls` can be written once it is built.

    An exception is not a record and is passed too.
    """

    if issubclass(cls, BaseException):
        return True

    if dataclasses.is_dataclass(cls):
        return bool(cls.__dataclass_params__.frozen)  # type: ignore[attr-defined]

    if issubclass(cls, BaseModel):
        return bool(cls.model_config.get("frozen"))

    # A value type such as `Percent`: every class it inherits from, other than
    # an immutable built-in number, declares an empty `__slots__`.
    return all(
        vars(base).get("__slots__") == ()
        for base in cls.__mro__
        if base not in (object, float, int)
    )


def fields_of(cls: type) -> set[str]:
    """Return the names of the fields an instance of `cls` holds."""

    if dataclasses.is_dataclass(cls):
        return {field.name for field in dataclasses.fields(cls)}

    return {
        name
        for base in cls.__mro__
        for name in (
            (vars(base).get("__slots__", ()),)
            if isinstance(vars(base).get("__slots__", ()), str)
            else vars(base).get("__slots__", ())
        )
    }


def unexplained(
    classes: Iterable[tuple[str, type]], writes: dict[str, dict[str, Write]]
) -> list[str]:
    """Return one line for each mutable class or field that `writes` gives no entry."""

    lines = []

    for key, cls in classes:
        if holds_no_writable_field(cls):
            continue

        entries = writes.get(key)

        if entries is None:
            lines.append(f"{key} can be written after it is built and has no entry in WRITES")
            continue

        lines.extend(
            f"{key}.{name} has no entry in WRITES"
            for name in sorted(fields_of(cls) - entries.keys())
        )
        lines.extend(
            f"{key}.{name} has an entry in WRITES but is not a field"
            for name in sorted(entries.keys() - fields_of(cls))
        )

    return lines


def core_classes() -> list[tuple[str, type]]:
    """Return every class defined in a module of `core/`, as `module.Class` and the class."""

    found: list[tuple[str, type]] = []

    for path in sorted(CORE.glob("*.py")):
        module = importlib.import_module(f"anesthesia_sim.core.{path.stem}")
        found.extend(
            (f"{path.stem}.{name}", value)
            for name, value in vars(module).items()
            if inspect.isclass(value) and value.__module__ == module.__name__
        )

    return found


ITEMS = Path(__file__).resolve().parents[2] / "docs" / "items"


def _open_items_named(text: str) -> list[str]:
    """Return the queue items that `text` names and that are still open.

    A `GAP` entry says that nothing checks a field's rule yet, and it names the open item
    that will add the check. The entry is accurate only while that item is open. Once the
    item is closed, the test fails until the entry is changed to the kind of write that the
    item built.
    """

    named = {word.strip("().,;") for word in text.split() if word.strip("(").startswith("PL-")}
    found = []

    for name in sorted(named):
        for path in ITEMS.glob(f"{name}-*.md"):
            front = path.read_text(encoding="utf-8").split("\n---\n", 1)[0]

            if "\nstatus: done" not in front and "\nstatus: dropped" not in front:
                found.append(name)

    return found


def _entries(kind: str) -> list[Any]:
    return [
        pytest.param(key, field, write, id=f"{key}.{field}")
        for key, entries in WRITES.items()
        for field, write in entries.items()
        if write.kind == kind
    ]


def test_every_field_of_every_mutable_record_in_core_has_an_entry() -> None:
    classes = core_classes()
    mutable = {key for key, cls in classes if not holds_no_writable_field(cls)}

    assert unexplained(classes, WRITES) == []
    assert sorted(WRITES.keys() - mutable) == []


@pytest.mark.parametrize(("key", "field", "write"), _entries(ONCE))
def test_a_field_written_once_refuses_a_later_write(key: str, field: str, write: Write) -> None:
    assert write.build is not None
    record = write.build()
    held = getattr(record, field)

    with pytest.raises(SimulationConfigurationError):
        setattr(record, field, held)

    assert getattr(record, field) is held

    with pytest.raises(SimulationConfigurationError):
        delattr(record, field)

    assert getattr(record, field) is held


@pytest.mark.parametrize(("key", "field", "write"), _entries(CHECKED))
def test_every_cross_field_invariant_holds_after_a_field_write(
    key: str, field: str, write: Write
) -> None:
    assert write.build is not None
    assert write.breaking is not None
    record = write.build()
    held = getattr(record, field)

    with pytest.raises(SimulationConfigurationError):
        setattr(record, field, write.breaking(record))

    assert getattr(record, field) is held


@pytest.mark.parametrize(("key", "field", "write"), _entries(ACCOUNTED))
def test_a_write_that_breaks_the_accounting_fails_the_next_accounting_read(
    key: str, field: str, write: Write
) -> None:
    assert write.build is not None
    assert write.locate is not None
    assert write.breaking is not None
    system = write.build()
    record = write.locate(system)

    assert system.agent_simulation_validation.passes_validation

    setattr(record, field, write.breaking(record))

    assert not system.agent_simulation_validation.passes_validation


@pytest.mark.reads_item_store
@pytest.mark.parametrize(
    ("key", "field", "write"),
    _entries(ACCOUNTED) + _entries(OWN) + _entries(PRIVATE) + _entries(GAP),
)
def test_a_field_written_without_a_check_at_the_write_says_why(
    key: str, field: str, write: Write
) -> None:
    assert write.why.strip()

    if write.kind == PRIVATE:
        assert field.startswith("_") or key.split(".")[-1].startswith("_")

    if write.kind == GAP:
        assert _open_items_named(write.why)


def test_every_entry_is_of_a_known_kind() -> None:
    kinds = {write.kind for entries in WRITES.values() for write in entries.values()}

    assert kinds <= {ONCE, CHECKED, ACCOUNTED, OWN, PRIVATE, GAP}


def test_a_mutable_class_with_no_entry_is_named() -> None:
    @dataclass
    class Probe:
        volume_l: float
        amount_l: float

    assert unexplained([("probe.Probe", Probe)], {}) == [
        "probe.Probe can be written after it is built and has no entry in WRITES"
    ]


def test_a_field_with_no_entry_and_an_entry_with_no_field_are_named() -> None:
    @dataclass
    class Probe:
        volume_l: float
        amount_l: float

    writes = {"probe.Probe": {"volume_l": Write(OWN, why="a probe"), "gone": Write(OWN)}}

    assert unexplained([("probe.Probe", Probe)], writes) == [
        "probe.Probe.amount_l has no entry in WRITES",
        "probe.Probe.gone has an entry in WRITES but is not a field",
    ]


def test_records_that_cannot_be_written_are_passed() -> None:
    @dataclass(frozen=True)
    class Frozen:
        volume_l: float

    class Plain:
        __slots__ = ("volume_l",)

    assert holds_no_writable_field(Frozen)
    assert holds_no_writable_field(Percent)
    assert not holds_no_writable_field(Plain)
    assert fields_of(Plain) == {"volume_l"}
