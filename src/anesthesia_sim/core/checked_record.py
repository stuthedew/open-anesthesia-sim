"""Save a record by field name, and rebuild it through its checks when a pickle or a copy loads it.

`pickle`, `copy.copy` and `copy.deepcopy` rebuild an object without calling
its constructor. They create an empty object and pass its saved state to
`__setstate__`. So a record whose constructor checks its fields can come back
holding a value that the constructor would refuse, unless its `__setstate__`
runs those checks.

Every record in `core/` therefore saves its state as a dict from each field's
name to its value, and restores from that dict through its own checks.
`restored_through_checks` gives a dataclass whose constructor takes every
field both methods. A record with a constructor of another shape writes its
own pair, and checks the saved dict with `require_state_by_name`.
`tests/unit/test_record_restores.py` walks `core/` and fails for a record
that restores another way (`PL-8W1Q`, `PL-HXNL`).

**Why by name.** The `__getstate__` that `dataclass` writes for a frozen,
slotted record returns the field values in field order, without their names.
A record saved before two fields of one type changed places would then load
with the two values swapped, and both would pass every check. A liquid
density saved as `(density, standard deviation)` would load as a density of
about 0.01 g/mL. A dict keyed by field name loads each value into its own
field whatever the order, and a field renamed or removed since the save is
refused by name.

**What this protects against.** It protects against a saved value that is
wrong, or saved under an older shape of the record. It does not protect
against a pickle crafted as an attack. A pickle can call any function that
can be imported, so a crafted pickle can still write a record's slots
directly. The Python documentation warns against loading a pickle from an
untrusted source for that reason
(https://docs.python.org/3/library/pickle.html), so nothing here treats a
pickle as untrusted input.
"""

from __future__ import annotations

import inspect
from collections.abc import Collection, Mapping
from dataclasses import fields, is_dataclass

__all__ = [
    "require_state_by_name",
    "restore_through_checks",
    "restored_through_checks",
    "state_by_name",
]


def require_state_by_name(
    record: object, state: object, names: Collection[str]
) -> Mapping[str, object]:
    """Return `state` as a mapping from each of `names` to its saved value.

    Every record's `__setstate__` calls this before it rebuilds anything, so
    each one refuses a saved state of the wrong shape with the same message.

    Args:
        record: The empty record that `pickle` or `copy` created. Only its type
            is read, to name it in a refusal.
        state: What the record's `__getstate__` returned when it was saved.
        names: The names that the saved state must hold, and no others.

    Raises:
        TypeError: `state` is not a dict, or it does not hold exactly `names`.
            A state saved as a list or tuple of values in field order, as
            `dataclass` writes one, is refused, because its values cannot be
            matched to their fields by name.
    """

    record_type = type(record).__name__

    if not isinstance(state, dict):
        raise TypeError(
            f"{record_type} is restored from its field values by name, "
            f"not from a {type(state).__name__}"
        )

    missing = [name for name in names if name not in state]
    unknown = sorted(str(key) for key in state if key not in names)

    if missing or unknown:
        raise TypeError(
            f"{record_type} is restored from its field values by name, and the saved state "
            f"lacks {', '.join(missing) or 'nothing'} and holds unknown "
            f"{', '.join(unknown) or 'nothing'}"
        )

    return state


def state_by_name(record: object) -> dict[str, object]:
    """Return a dataclass record's state for a pickle or a copy: each field's name and value."""

    return {field.name: getattr(record, field.name) for field in fields(record)}  # type: ignore[arg-type]


def restore_through_checks(record: object, state: object) -> None:
    """Restore an unpickled or copied dataclass record by running its constructor on it.

    The function runs the record's own `__init__` on the empty record, with
    each saved value passed by its field name. So every check that the
    constructor makes is made, in `__post_init__` and in a `__setattr__` that
    guards each write, and a value that the constructor would refuse is refused
    on load, with the constructor's own exception.

    The check sits in `__setstate__` rather than in `__reduce__`. Every pickle
    protocol, `copy.copy` and `copy.deepcopy` restore the record through
    `__setstate__`, and so would a pickle written in another form. A
    `__reduce__` that called the constructor would change only how a record is
    written from now on.

    `restored_through_checks` installs this function as a record's
    `__setstate__`, and refuses a record that the constructor cannot rebuild.

    Raises:
        TypeError: the state is not a dict holding exactly the record's field
            names (`require_state_by_name`), or the constructor refuses a
            value's type.
        SimulationConfigurationError: the constructor refuses a value.
    """

    names = [field.name for field in fields(record)]  # type: ignore[arg-type]
    by_name = require_state_by_name(record, state, names)

    type(record).__init__(record, **by_name)


def restored_through_checks[Record: type](record_type: Record) -> Record:
    """Give a dataclass a `__getstate__` that saves by field name, and a `__setstate__` that checks.

    Apply it above `@dataclass`, so that it replaces the pair that `dataclass`
    writes for a frozen, slotted record. The record then saves its state with
    `state_by_name` and restores it with `restore_through_checks`.

    Raises:
        TypeError: `record_type` is not a dataclass, or its constructor does
            not take exactly its fields. A field with `init=False` is not
            passed to the constructor, and an `InitVar` is passed to it but is
            not saved, so the constructor cannot rebuild either record from
            its saved fields. Such a record writes its own `__getstate__` and
            `__setstate__`. The order does not matter, because every value is
            passed by name. The error is raised when the class is defined, so
            a misshapen record fails at import.
    """

    if not is_dataclass(record_type):
        raise TypeError(f"{record_type.__name__} is not a dataclass")

    names = sorted(field.name for field in fields(record_type))
    taken = sorted(inspect.signature(record_type).parameters)

    if taken != names:
        raise TypeError(
            f"{record_type.__name__} cannot be restored through its constructor, because the "
            f"constructor takes {', '.join(taken) or 'nothing'} and the record's fields are "
            f"{', '.join(names) or 'none'}"
        )

    record_type.__getstate__ = state_by_name  # type: ignore[method-assign,assignment]
    record_type.__setstate__ = restore_through_checks  # type: ignore[attr-defined]

    return record_type
