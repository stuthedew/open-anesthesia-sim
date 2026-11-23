"""A record in `core/` that a pickle or a copy rebuilds runs its checks, and takes values by name.

`pickle`, `copy.copy` and `copy.deepcopy` rebuild an object without calling
its constructor. Before `PL-8W1Q`, a saved `Keyframe` whose `instant_s` was a
bare -50.0 loaded without error. Before `PL-HXNL`, a run's definition, its
patient, its uptake system and the data-file payloads still loaded without
their checks, and every frozen record saved its values in field order, so a
record saved before two fields of one type changed places would have loaded
with the two values swapped.

The first tests walk `core/` the way `tests/unit/test_record_writes.py` does,
so a new class that restores another way fails them.
"""

from __future__ import annotations

import copy
import dataclasses
import importlib
import inspect
import io
import json
import pickle
from collections.abc import Callable
from enum import Enum
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from anesthesia_sim import core
from anesthesia_sim.core import parameters
from anesthesia_sim.core.agent_simulation_validation import AgentSimulationValidator
from anesthesia_sim.core.checked_number import CheckedQuantity
from anesthesia_sim.core.checked_record import (
    require_state_by_name,
    restored_through_checks,
    state_by_name,
)
from anesthesia_sim.core.circuit import BreathingCircuit
from anesthesia_sim.core.concentration import Percent
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.governing_equations import STATE_SIZE
from anesthesia_sim.core.liquid_agent import LiquidDensity
from anesthesia_sim.core.parameters import load_agent_parameters
from anesthesia_sim.core.run_definition import RunDefinition
from anesthesia_sim.core.simulation import SimulationState
from anesthesia_sim.core.stored_states import Keyframe, StoredStates
from anesthesia_sim.core.supported_ranges import (
    AlveolarVentilation,
    CaseInstant,
    FreshGasFlow,
    StepCount,
)
from anesthesia_sim.core.uptake_system import AgentUptakeSystem

CORE = Path(core.__file__).resolve().parent
DATA = CORE.parent / "data"

# The start of the message that `require_state_by_name` gives for a state that
# is not a dict. The `__setstate__` that `dataclass` writes gives another, and
# Pydantic's gives none.
_BY_NAME_REFUSAL = "is restored from its field values by name"

# Every way an object can be rebuilt without its constructor: each pickle
# protocol, and the two copies.
_REBUILDS: tuple[tuple[str, Callable[[Any], Any]], ...] = (
    *(
        (
            f"pickle protocol {protocol}",
            lambda record, p=protocol: pickle.loads(pickle.dumps(record, p)),
        )
        for protocol in range(pickle.HIGHEST_PROTOCOL + 1)
    ),
    ("copy.copy", copy.copy),
    ("copy.deepcopy", copy.deepcopy),
)
_REBUILD_IDS = [how for how, _ in _REBUILDS]

# The rebuilds that copy what a record holds: a run refuses a shallow copy.
_DEEP_REBUILDS = tuple((how, rebuild) for how, rebuild in _REBUILDS if how != "copy.copy")
_DEEP_REBUILD_IDS = [how for how, _ in _DEEP_REBUILDS]
_PROTOCOLS = range(pickle.HIGHEST_PROTOCOL + 1)


def _core_classes() -> list[tuple[str, type]]:
    """Return every class defined in `core/` that a pickle or a copy rebuilds from a state.

    An exception is left out, because it is rebuilt from its arguments, and
    so is a checked quantity, which `CheckedQuantity.__reduce__` rebuilds
    through its constructor. An `Enum` is left out too, because a pickle or a
    copy returns the same member, looked up by its value.
    `test_every_enum_in_core_rebuilds_as_the_same_member_and_refuses_an_unknown_value`
    checks that.
    """

    found: list[tuple[str, type]] = []

    for path in sorted(CORE.glob("*.py")):
        module = importlib.import_module(f"anesthesia_sim.core.{path.stem}")
        found.extend(
            (f"{path.stem}.{name}", value)
            for name, value in vars(module).items()
            if inspect.isclass(value)
            and value.__module__ == module.__name__
            and not issubclass(value, (BaseException, CheckedQuantity, Enum))
        )

    return found


def _core_enums() -> list[tuple[str, type[Enum]]]:
    """Return every `Enum` defined in `core/`."""

    found: list[tuple[str, type[Enum]]] = []

    for path in sorted(CORE.glob("*.py")):
        module = importlib.import_module(f"anesthesia_sim.core.{path.stem}")
        found.extend(
            (f"{path.stem}.{name}", value)
            for name, value in vars(module).items()
            if inspect.isclass(value)
            and value.__module__ == module.__name__
            and issubclass(value, Enum)
        )

    return found


def test_every_enum_in_core_rebuilds_as_the_same_member_and_refuses_an_unknown_value() -> None:
    """A pickle or a copy of an `Enum` member returns that member, and no other value loads.

    This is why `_core_classes` leaves an `Enum` out. The lookup by value is
    the enum's check, so a saved value it does not hold fails to load.
    """

    enums = _core_enums()
    assert enums, "core/ defines an Enum, so this test must find at least one"

    for key, enum in enums:
        for member in enum:
            for how, rebuild in _REBUILDS:
                assert rebuild(member) is member, (key, member, how)

        with pytest.raises(ValueError, match="is not a valid"):
            enum(object())


def test_every_class_in_core_restores_by_name_through_its_checks() -> None:
    """Each class's `__setstate__` refuses a state that is not a dict of values by name."""

    unchecked = []

    for key, cls in _core_classes():
        empty: Any = object.__new__(cls)

        try:
            empty.__setstate__(object())
        except TypeError as error:
            if _BY_NAME_REFUSAL in str(error):
                continue

        unchecked.append(key)

    assert not unchecked, (
        "these classes restore from a pickle or a copy without their checks, or not by name; "
        "decorate a dataclass whose constructor takes every field with "
        "core.checked_record.restored_through_checks, or give the class a __setstate__ that "
        "calls core.checked_record.require_state_by_name: " + ", ".join(unchecked)
    )


def test_every_class_in_core_saves_its_state_with_a_getstate_of_its_own() -> None:
    """No class keeps the `__getstate__` of `object`, `dataclass` or Pydantic."""

    unnamed = [
        key
        for key, cls in _core_classes()
        if not cls.__getstate__.__module__.startswith("anesthesia_sim.core")
    ]

    assert not unnamed, "these classes save their state another way: " + ", ".join(unnamed)


def test_the_walk_finds_the_records_that_the_items_named() -> None:
    """The walk is not empty: it finds the records `PL-S11T`, `PL-8W1Q` and `PL-HXNL` named."""

    found = {key for key, _ in _core_classes()}

    assert {
        "governing_equations.UptakeEquationSettings",
        "run_definition.RunSegment",
        "run_definition.RunDefinition",
        "stored_states.Keyframe",
        "stored_states.StoredStates",
        "liquid_agent.LiquidDensity",
        "patient.PatientCompartments",
        "uptake_system.AgentUptakeSystem",
        "simulation.SimulationState",
        "parameters.AgentParameters",
        "parameters._AgentPayload",
        "parameters._ReferenceAdultPayload",
        "parameters._BreathingCircuitPayload",
    } <= found


class _ForgingPickler(pickle.Pickler):
    """Pickle an object as `pickle` would, with one value of `target`'s saved state replaced.

    The state is written in the form that the protocol uses, so loading it
    takes the path that a saved file would take. Only the one saved value
    differs, as a hand edit of a saved run would change it.
    """

    def __init__(
        self, buffer: io.BytesIO, protocol: int, target: object, name: str, value: object
    ) -> None:
        super().__init__(buffer, protocol=protocol)
        self._protocol = protocol
        self._target = target
        self._name = name
        self._value = value

    def reducer_override(self, obj: object) -> object:
        if obj is not self._target:
            return NotImplemented

        constructor, arguments, state = obj.__reduce_ex__(self._protocol)[:3]

        return constructor, arguments, {**state, self._name: self._value}


def _load_forged(
    saved: object, protocol: int, name: str, value: object, target: object = None
) -> object:
    """Pickle `saved` with `target`'s (or `saved`'s own) `name` replaced by `value`, and load it."""

    buffer = io.BytesIO()
    forged_in = saved if target is None else target
    _ForgingPickler(buffer, protocol, forged_in, name, value).dump(saved)

    return pickle.loads(buffer.getvalue())


def _run_of(seconds: int) -> SimulationState:
    """A sevoflurane run stepped for `seconds`, with the fresh gas flow changed at 1 s."""

    state = SimulationState()
    state.advance()
    state.uptake_system.set_fresh_gas_flow(FreshGasFlow(2.0))

    for _ in range(seconds - 1):
        state.advance()

    return state


def _definition_of_three_stretches() -> RunDefinition:
    """A run's definition with three stretches, opening at 0 s, 30 s and 90 s, reached at 120 s."""

    system = AgentUptakeSystem.default()
    definition = RunDefinition(system.equation_settings(), opened_at_s=CaseInstant(0))

    for opened_at_s, ventilation_l_min in ((30, 5.0), (90, 6.0)):
        definition.advance_to(CaseInstant(opened_at_s))
        system.set_alveolar_ventilation(AlveolarVentilation(ventilation_l_min))
        definition.record_change(system.equation_settings())

    definition.advance_to(CaseInstant(120))

    return definition


@pytest.mark.parametrize(("how", "rebuild"), _DEEP_REBUILDS, ids=_DEEP_REBUILD_IDS)
def test_a_rebuilt_run_holds_what_was_saved_and_steps_on_like_it(
    how: str, rebuild: Callable[[Any], Any]
) -> None:
    """A run, its system, its patient, its record and every record inside them rebuild unchanged.

    The expected values come from a second run built the same way and stepped
    once more beside the rebuilt one. A rebuild that dropped the accounting's
    compensation terms, or anchored the accounting again, would round its next
    total differently.
    """

    run = _run_of(seconds=5)
    fresh = _run_of(seconds=5)
    rebuilt = rebuild(run)

    assert rebuilt.step_count == fresh.step_count, how
    assert rebuilt.uptake_system == fresh.uptake_system, how
    assert rebuilt.stored_states.state_at(CaseInstant(3)) == fresh.stored_states.state_at(
        CaseInstant(3)
    ), how

    assert rebuilt.advance().state == fresh.advance().state, how
    assert (
        rebuilt.uptake_system.agent_simulation_validator.capture_state()
        == fresh.uptake_system.agent_simulation_validator.capture_state()
    ), how


@pytest.mark.parametrize(("how", "rebuild"), _REBUILDS, ids=_REBUILD_IDS)
def test_a_rebuilt_definition_holds_its_three_stretches(
    how: str, rebuild: Callable[[Any], Any]
) -> None:
    definition = _definition_of_three_stretches()
    rebuilt = rebuild(definition)

    assert [segment.opened_at_s for segment in rebuilt.segments] == [0, 30, 90], how
    assert rebuilt.segments == definition.segments, how
    assert rebuilt.reached_s == 120, how


@pytest.mark.parametrize(("how", "rebuild"), _REBUILDS, ids=_REBUILD_IDS)
@pytest.mark.parametrize(
    ("folder", "payload_type"),
    [
        ("agents", parameters._AgentPayload),
        ("patients", parameters._ReferenceAdultPayload),
        ("machines", parameters._BreathingCircuitPayload),
    ],
)
def test_a_rebuilt_payload_of_each_shipped_file_equals_the_one_loaded(
    folder: str, payload_type: type[Any], how: str, rebuild: Callable[[Any], Any]
) -> None:
    for path in sorted((DATA / folder).glob("*.json")):
        payload = payload_type.model_validate(json.loads(path.read_text(encoding="utf-8")))

        assert rebuild(payload) == payload, f"{path.name}, {how}"


def test_a_record_saved_before_two_fields_changed_places_loads_each_value_into_its_own_field() -> (
    None
):
    """A saved state is matched to the fields by name, whatever order the fields come in.

    A liquid density and its standard deviation are both bare `float` fields,
    so swapped, both would pass every check. A record whose fields are listed
    in the other order stands in for the same record after a reorder.
    """

    saved = load_agent_parameters("sevoflurane").liquid_density.__getstate__()

    @restored_through_checks
    @dataclasses.dataclass(frozen=True, slots=True)
    class ReorderedDensity:
        measured_at_celsius: float
        standard_deviation_g_ml: float
        g_ml: float

    restored: Any = object.__new__(ReorderedDensity)
    restored.__setstate__(saved)

    assert restored.g_ml == saved["g_ml"]
    assert restored.standard_deviation_g_ml == saved["standard_deviation_g_ml"]
    assert restored.g_ml > 10 * restored.standard_deviation_g_ml


def test_a_state_saved_in_field_order_without_names_is_refused() -> None:
    """The form `dataclass` writes is refused, because nothing in it says which value is which."""

    density = load_agent_parameters("sevoflurane").liquid_density
    empty: Any = object.__new__(LiquidDensity)

    with pytest.raises(TypeError, match=f"^LiquidDensity {_BY_NAME_REFUSAL}, not from a tuple$"):
        empty.__setstate__(tuple(state_by_name(density).values()))


def _keyframe() -> Keyframe:
    """A keyframe at 60 s, whose state is not checked by the keyframe itself."""

    return Keyframe(CaseInstant(60), tuple(float(index) for index in range(STATE_SIZE)))


@pytest.mark.parametrize("protocol", _PROTOCOLS)
def test_a_saved_keyframe_holding_a_bare_negative_instant_is_refused(protocol: int) -> None:
    """A bare -50.0 is neither a checked instant nor at or after induction (`PL-8W1Q`)."""

    with pytest.raises(TypeError, match="instant_s"):
        _load_forged(_keyframe(), protocol, "instant_s", -50.0)


@pytest.mark.parametrize("protocol", _PROTOCOLS)
def test_a_saved_patient_whose_fractions_do_not_sum_to_one_is_refused(protocol: int) -> None:
    """The patient checks the sum only in its constructor, which a restore now runs."""

    patient = AgentUptakeSystem.default().patient

    with pytest.raises(SimulationConfigurationError, match="perfusion fractions"):
        _load_forged(patient, protocol, "vessel_rich", patient.muscle)


@pytest.mark.parametrize("protocol", _PROTOCOLS)
def test_a_saved_system_whose_accounting_does_not_balance_is_refused(protocol: int) -> None:
    """A system restored with another accounting would report agent it never received."""

    system = _run_of(seconds=3).uptake_system
    other = AgentSimulationValidator(initial_agent_l=1.0)

    with pytest.raises(SimulationConfigurationError, match="accounting does not balance"):
        _load_forged(system, protocol, "agent_simulation_validator", other)


def test_a_saved_system_with_a_dial_above_the_input_ceiling_is_refused() -> None:
    """A vaporizer that reaches 100% passes the circuit, and the system's ceiling refuses 99.5%."""

    system = AgentUptakeSystem.default()
    state = system.__getstate__()
    circuit = BreathingCircuit(
        **{
            **state_by_name(system.circuit),
            "max_delivered_concentration_percent": Percent(100.0),
            "delivered_concentration_percent": Percent(99.5),
        }
    )
    empty: Any = object.__new__(AgentUptakeSystem)

    with pytest.raises(SimulationConfigurationError, match="delivered_concentration_percent"):
        empty.__setstate__({**state, "circuit": circuit})


@pytest.mark.parametrize("protocol", _PROTOCOLS)
def test_a_saved_validator_holding_a_negative_total_is_refused(protocol: int) -> None:
    with pytest.raises(SimulationConfigurationError, match="delivered_agent_l"):
        _load_forged(AgentSimulationValidator(), protocol, "delivered_agent_l", -1.0)


@pytest.mark.parametrize("protocol", _PROTOCOLS)
def test_a_saved_run_whose_count_is_not_where_its_record_ends_is_refused(protocol: int) -> None:
    """A count of 2 over states stored to 3 s would put the clock one second behind the record."""

    with pytest.raises(SimulationConfigurationError, match="stores states up to 3 s"):
        _load_forged(_run_of(seconds=3), protocol, "step_count", StepCount(2))


def test_a_shallow_copy_of_a_run_is_refused() -> None:
    """A copy sharing the original's system would step it under the original (blind review).

    The copy would hold a record of its own. Stepping the copy ten seconds
    moved the shared system, and the original's next step then stored an
    alveolar fraction of 0.00272 as its 6 s state, where a fresh run gives
    0.00113.
    """

    with pytest.raises(TypeError, match="cannot be copied shallowly"):
        copy.copy(_run_of(seconds=5))


@pytest.mark.parametrize("protocol", _PROTOCOLS)
def test_a_saved_system_holding_a_part_of_another_type_is_refused(protocol: int) -> None:
    """A part's state record has the part's amounts but no methods, and failed at the next step."""

    system = _run_of(seconds=3).uptake_system

    with pytest.raises(
        TypeError,
        match="^the system's alveoli has type AlveolarCompartmentState, not AlveolarCompartment$",
    ):
        _load_forged(system, protocol, "alveoli", system.alveoli.capture_state())


def test_a_run_whose_system_is_not_an_uptake_system_is_refused() -> None:
    """The constructor used to accept any object as the system, and failed later."""

    with pytest.raises(TypeError, match="^uptake_system has type dict, not AgentUptakeSystem$"):
        SimulationState(uptake_system={})  # type: ignore[arg-type]


@pytest.mark.parametrize("protocol", _PROTOCOLS)
def test_a_saved_definition_that_goes_back_in_time_is_refused(protocol: int) -> None:
    """A reached second before the last stretch opens would leave that stretch unreached."""

    with pytest.raises(SimulationConfigurationError, match="cannot go back from 90 s to 60 s"):
        _load_forged(_definition_of_three_stretches(), protocol, "reached_s", CaseInstant(60))


@pytest.mark.parametrize("protocol", _PROTOCOLS)
def test_a_saved_definition_with_two_stretches_under_one_setting_is_refused(protocol: int) -> None:
    """A run records no stretch for settings that did not change, so the replay drops it.

    Three stretches are saved, the last one under the second one's settings
    at a later second. The replay records two, and the restore is refused
    rather than tidied.
    """

    definition = _definition_of_three_stretches()
    first, second, third = definition.segments
    repeated = (first, second, dataclasses.replace(third, settings=second.settings))

    with pytest.raises(SimulationConfigurationError, match="holds 3 stretches.*records 2"):
        _load_forged(definition, protocol, "segments", repeated)


def test_a_saved_definition_without_stretches_is_refused() -> None:
    empty: Any = object.__new__(RunDefinition)

    with pytest.raises(TypeError, match="nonempty tuple of RunSegment, not from a tuple"):
        empty.__setstate__({"segments": (), "reached_s": CaseInstant(0)})


def _saved_record() -> StoredStates:
    return _run_of(seconds=3).stored_states


@pytest.mark.parametrize("protocol", _PROTOCOLS)
def test_saved_stored_states_holding_a_state_that_is_not_finite_are_refused(protocol: int) -> None:
    record = _saved_record()
    values = record.__getstate__()["values"]
    forged = copy.copy(values)
    forged[2 * STATE_SIZE] = float("nan")

    with pytest.raises(SimulationConfigurationError, match="not finite|finite"):
        _load_forged(record, protocol, "values", forged)


@pytest.mark.parametrize("protocol", _PROTOCOLS)
def test_saved_stored_states_with_a_state_cut_short_are_refused(protocol: int) -> None:
    record = _saved_record()
    forged = record.__getstate__()["values"][:-1]

    with pytest.raises(SimulationConfigurationError, match="for each of the same number"):
        _load_forged(record, protocol, "values", forged)


def test_saved_stored_states_that_are_not_arrays_of_float_are_refused() -> None:
    state = _saved_record().__getstate__()
    empty: Any = object.__new__(StoredStates)

    with pytest.raises(TypeError, match="two arrays of float, not from a list and a array"):
        empty.__setstate__({**state, "values": list(state["values"])})


@pytest.mark.parametrize("protocol", _PROTOCOLS)
def test_a_saved_payload_whose_fractions_do_not_sum_to_one_is_refused(protocol: int) -> None:
    """Pydantic restored a payload's fields without running a validator (`PL-HXNL`)."""

    payload = parameters._ReferenceAdultPayload.model_validate(
        json.loads((DATA / "patients" / "reference_adult.json").read_text(encoding="utf-8"))
    )
    groups = payload.tissue_groups.model_dump()
    groups["muscle"]["perfusion_fraction"] = 0.5

    with pytest.raises(ValidationError, match="perfusion"):
        _load_forged(payload, protocol, "tissue_groups", groups)


@pytest.mark.parametrize("duplicate", [copy.copy, copy.deepcopy])
def test_a_copy_of_a_payload_with_a_value_written_past_its_checks_is_refused(
    duplicate: Callable[[Any], Any],
) -> None:
    """Pydantic's own copies copy the fields without a validator, and the payload's do not."""

    payload = parameters._LiquidDensityPayload.model_validate(
        json.loads((DATA / "agents" / "sevoflurane.json").read_text(encoding="utf-8"))[
            "liquid_density"
        ]
    )
    object.__setattr__(payload, "g_ml", -1.0)

    with pytest.raises(ValidationError):
        duplicate(payload)


def test_a_state_with_a_missing_and_an_unknown_name_is_refused_naming_both() -> None:
    empty: Any = object.__new__(Keyframe)

    with pytest.raises(TypeError, match="lacks state and holds unknown values$"):
        empty.__setstate__({"instant_s": CaseInstant(60), "values": ()})

    with pytest.raises(TypeError, match="lacks nothing and holds unknown 1, extra$"):
        require_state_by_name(empty, {"instant_s": 0, "extra": 0, 1: 0}, ("instant_s",))


def test_a_decorated_class_that_is_not_a_dataclass_is_refused_where_it_is_defined() -> None:
    with pytest.raises(TypeError, match="^Plain is not a dataclass$"):

        @restored_through_checks
        class Plain:
            pass


def test_a_record_with_a_field_the_constructor_does_not_take_is_refused_where_it_is_defined() -> (
    None
):
    with pytest.raises(TypeError, match="constructor takes value and the record's fields are"):

        @restored_through_checks
        @dataclasses.dataclass(frozen=True, slots=True)
        class Derived:
            value: float
            twice: float = dataclasses.field(init=False)
