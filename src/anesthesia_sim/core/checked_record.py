"""Restore a checked record from a pickle or a copy through its constructor's checks.

A checked record is a frozen dataclass in this package that checks its fields
in `__post_init__`. Each one gives itself a `__setstate__` that calls
`restore_through_checks`, so a record rebuilt by `pickle`, `copy.copy` or
`copy.deepcopy` is checked as the constructor checks it.
`tests/unit/test_record_restores.py` walks `core/` and fails for a checked
record that restores without its checks (`PL-8W1Q`).
"""

from __future__ import annotations

from dataclasses import fields

__all__ = ["restore_through_checks"]


def restore_through_checks(record: object, state: object) -> None:
    """Restore an unpickled or copied record by building it again through its constructor.

    Unpickling or copying a frozen record creates an empty object and passes
    the saved field values to `__setstate__`. The `__setstate__` that
    `dataclass` generates writes each value straight into its slot, so
    `__post_init__` never runs. A saved settings record whose state held a
    cardiac output of 1000.0 as a bare `float` loaded without error, and a
    `RunDefinition` opened under it advanced. A saved fresh gas flow of NaN
    also loaded (`PL-S11T`, measured 2026-10-25). A saved `Keyframe` whose
    `instant_s` was a bare -50.0 loaded too (`PL-8W1Q`).
    `CheckedQuantity.__reduce__` (`core/checked_number.py`) protects a value
    that was pickled as its checked type. It does not protect a field whose
    saved state holds a bare number.

    So each checked record's `__setstate__` calls this function. The function
    builds a new record from the saved values, which runs every check that the
    constructor runs. It then copies the checked fields into the restored
    object. A state that the constructor would refuse is refused on load, with
    the constructor's own exception.

    The check sits in `__setstate__` rather than in `__reduce__` for this
    reason. Every pickle protocol, `copy.copy` and `copy.deepcopy` restore the
    record through `__setstate__`, and so does a pickle written before this
    function existed. A `__reduce__` that called the constructor would change
    only how a record is written from now on. A saved or edited state in the
    form that `dataclass` writes would still load through `__setstate__`.

    This function protects against a saved value that is wrong, not against a
    pickle crafted as an attack. A pickle can call any function that can be
    imported, so a crafted pickle can still write a record's slots directly.
    A pickle is trusted input.

    The state holds the field values in field order, without their names, as
    `dataclass` writes it. Suppose the order of the fields changes. A record
    saved before that change would then load its values into the wrong fields,
    wherever those values still pass the checks. A saved-run file format that
    stores each value with its field name would close that gap; the first
    loader of saved runs chooses the format (`PL-HXNL`).

    Args:
        record: The empty record that `pickle` or `copy` created. Its type is
            the dataclass whose constructor is run.
        state: What the record's `__getstate__` returned when it was saved:
            its field values, in field order.

    The record must be a frozen dataclass with `slots=True`, because only then
    is its saved state the list of field values that this function reads. Every
    field must be one that the constructor takes. `tests/unit/test_record_restores.py`
    holds every checked record in `core/` to both.

    Raises:
        TypeError: the state is not a list or tuple of exactly the record's
            field values, the record has a field that the constructor does
            not take, or the constructor refuses a value's type.
        SimulationConfigurationError: the constructor refuses a value.
    """

    record_type = type(record)

    if not isinstance(state, (list, tuple)):
        raise TypeError(
            f"{record_type.__name__} is restored from a list of its field values, "
            f"not a {type(state).__name__}"
        )

    record_fields = fields(record_type)  # type: ignore[arg-type]
    derived = [field.name for field in record_fields if not field.init]

    if derived:
        raise TypeError(
            f"{record_type.__name__} cannot be restored through its constructor, because "
            f"the constructor does not take {', '.join(derived)}"
        )

    names = tuple(field.name for field in record_fields)

    if len(state) != len(names):
        raise TypeError(
            f"{record_type.__name__} is restored from its {len(names)} field values, "
            f"not from {len(state)}"
        )

    checked = record_type(**dict(zip(names, state, strict=True)))

    for name in names:
        object.__setattr__(record, name, getattr(checked, name))
