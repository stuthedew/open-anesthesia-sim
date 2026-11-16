"""A checked record in `core/` that is rebuilt by a pickle or a copy runs its constructor's checks.

A checked record is a frozen dataclass that checks its fields in `__post_init__`.
`pickle`, `copy.copy` and `copy.deepcopy` rebuild such a record without calling
its constructor, so before `PL-8W1Q` a saved `Keyframe` whose `instant_s` was a
bare -50.0 loaded without error. Each checked record now restores through
`core/checked_record.py`'s `restore_through_checks`. The first test walks
`core/` the way `tests/unit/test_record_writes.py` does, so a new checked
record that restores without its checks fails it.
"""

from __future__ import annotations

import copy
import dataclasses
import importlib
import inspect
import pickle
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from anesthesia_sim import core
from anesthesia_sim.core.checked_record import restore_through_checks
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.governing_equations import STATE_SIZE
from anesthesia_sim.core.run_definition import DisplayState, Keyframe, SampledWindow
from anesthesia_sim.core.supported_ranges import CaseInstant

CORE = Path(core.__file__).resolve().parent

# The message that `restore_through_checks` gives for a state that is not a list
# of field values. The `__setstate__` that `dataclass` generates gives another.
_HELPER_REFUSAL = "is restored from a list of its field values"

# Every way a record can be rebuilt without its constructor: each pickle
# protocol, and the two copies.
_REBUILDS: tuple[tuple[str, Callable[[object], object]], ...] = (
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


def _checked_records() -> list[tuple[str, type]]:
    """Return every frozen dataclass in `core/` that checks its fields in `__post_init__`."""

    found: list[tuple[str, type]] = []

    for path in sorted(CORE.glob("*.py")):
        module = importlib.import_module(f"anesthesia_sim.core.{path.stem}")
        found.extend(
            (f"{path.stem}.{name}", value)
            for name, value in vars(module).items()
            if inspect.isclass(value) and value.__module__ == module.__name__
        )

    return [
        (key, cls)
        for key, cls in found
        if dataclasses.is_dataclass(cls)
        and cls.__dataclass_params__.frozen  # type: ignore[attr-defined]
        and getattr(cls, "__post_init__", None) is not None
    ]


def test_every_checked_record_restores_through_its_checks() -> None:
    """Each checked record restores through `restore_through_checks`, not the dataclass default."""

    unchecked = []

    for key, cls in _checked_records():
        empty: Any = object.__new__(cls)

        try:
            empty.__setstate__(object())
        except TypeError as error:
            if _HELPER_REFUSAL in str(error):
                continue

        unchecked.append(key)

    assert not unchecked, (
        "these checked records restore from a pickle or a copy without their checks; give each "
        "a __setstate__ that calls core.checked_record.restore_through_checks: "
        + ", ".join(unchecked)
    )


def test_every_checked_record_has_the_shape_that_restore_through_checks_reads() -> None:
    """Each checked record is slotted, and its constructor takes exactly its fields.

    A frozen dataclass without `slots=True` saves its state as a dict. A field
    with `init=False` cannot be passed to the constructor, and an `InitVar` is
    a constructor argument that the saved state does not hold. The helper
    cannot rebuild a record of any of these shapes, so it could not be copied.
    """

    misshapen = [
        key
        for key, cls in _checked_records()
        if "__slots__" not in vars(cls)
        or list(inspect.signature(cls).parameters)
        != [field.name for field in dataclasses.fields(cls)]
    ]

    assert not misshapen, (
        "these checked records are not slotted, or their constructor does not take exactly "
        "their fields, so restore_through_checks cannot rebuild them: " + ", ".join(misshapen)
    )


def test_the_walk_finds_the_checked_records_that_the_item_named() -> None:
    """The walk is not empty: it finds the records `PL-S11T` and `PL-8W1Q` named."""

    found = {key for key, _ in _checked_records()}

    assert {
        "governing_equations.UptakeEquationSettings",
        "governing_equations.TissueGroupEquationSettings",
        "run_definition.Keyframe",
        "run_definition.SampledWindow",
        "circuit.BreathingCircuitState",
        "circuit.DeliverableFreshGasFlowRange",
        "liquid_agent.LiquidDensity",
        "parameters.AgentParameters",
        "parameters.BreathingCircuitParameters",
        "parameters.ReferenceAdultParameters",
        "parameters.SupportedSchemaVersions",
    } <= found


def _keyframe() -> Keyframe:
    """A keyframe at 60 s, whose state is not checked by the keyframe itself."""

    return Keyframe(CaseInstant(60.0), tuple(float(index) for index in range(STATE_SIZE)))


def _keyframe_holding(instant_s: object) -> Keyframe:
    """A keyframe whose `instant_s` slot holds `instant_s`, written past the constructor.

    This is how a keyframe saved by an older or edited file looks once it is
    loaded: the slot holds whatever the file held.
    """

    record = object.__new__(Keyframe)
    object.__setattr__(record, "instant_s", instant_s)
    object.__setattr__(record, "state", _keyframe().state)

    return record


@pytest.mark.parametrize(("how", "rebuild"), _REBUILDS, ids=[how for how, _ in _REBUILDS])
def test_a_rebuilt_keyframe_equals_the_one_saved(
    how: str, rebuild: Callable[[object], object]
) -> None:
    keyframe = _keyframe()
    restored = rebuild(keyframe)

    assert restored == keyframe, how
    assert type(restored.instant_s) is CaseInstant, how


@pytest.mark.parametrize(("how", "rebuild"), _REBUILDS, ids=[how for how, _ in _REBUILDS])
def test_a_saved_keyframe_holding_a_bare_negative_instant_is_refused(
    how: str, rebuild: Callable[[object], object]
) -> None:
    """A bare -50.0 is neither a checked instant nor at or after induction (`PL-8W1Q`)."""

    with pytest.raises(TypeError, match="instant_s"):
        rebuild(_keyframe_holding(-50.0))


def test_a_saved_sampled_window_whose_times_and_states_differ_in_length_is_refused() -> None:
    """The relation between two fields is checked on a restore too, not only each field's type."""

    state = DisplayState(_keyframe().state)
    window = SampledWindow((0.0, 1.0, 2.0), (state, state, state))
    broken = object.__new__(SampledWindow)
    object.__setattr__(broken, "times_s", window.times_s)
    object.__setattr__(broken, "states", (state, state))

    with pytest.raises(SimulationConfigurationError, match="3 instants and 2 states"):
        copy.copy(broken)


def test_a_record_with_a_field_the_constructor_does_not_take_is_refused_by_name() -> None:
    @dataclasses.dataclass(frozen=True, slots=True)
    class Derived:
        value: float
        twice: float = dataclasses.field(init=False)

        def __post_init__(self) -> None:
            object.__setattr__(self, "twice", 2 * self.value)

    empty = object.__new__(Derived)

    with pytest.raises(TypeError, match="does not take twice"):
        restore_through_checks(empty, [1.0, 2.0])


def test_a_state_with_the_wrong_number_of_values_is_refused() -> None:
    empty = object.__new__(Keyframe)

    with pytest.raises(TypeError, match="restored from its 2 field values, not from 3"):
        empty.__setstate__([CaseInstant(60.0), _keyframe().state, 0.0])
