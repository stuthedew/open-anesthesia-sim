"""Every number a `core/` dataclass defaults a field to is one the provenance
table selects, unless it is empty state or the whole (`PL-65HT`).

`tools/doc_check.py`'s `check_provenance` holds `docs/MODEL.md`'s provenance
table to the data files in both directions, so a scientific constant that
never entered a data file is invisible to it. `PL-4YY1` found two that way, as
`BreathingCircuit` field defaults, and moved them into the machine file; this
is the screen for the next one. Each default is read through
`dataclasses.fields()`, so one spelled as a named constant is read as surely
as a literal, and it must appear in the table's Selected-value column.

**A screen, not a proof.** It matches values rather than names, since pairing
a field with its row would need a mapping kept by hand (`gas_volume_l` is
documented as `alveolar_gas_volume_l`). So a new constant equal to any value
the table already selects passes: 6.0 L is the vessel-rich tissue volume as
well as the circuit volume. Each default is pinned to its own file's value by
`test_the_bare_circuit_defaults_match_the_shipped_machine_file` and
`test_the_bare_alveolar_defaults_match_the_shipped_patient_file`.

Empty state and the whole carry no science and are not screened: 0 and 1, or
0 and 100 for a `Percent`, the same two bounds on the dial's own scale.
`BreathingCircuit`'s vaporizer maximum defaults to 100, meaning no device
limit declared. Only a field's own scalar default is read, a factory's
included; a tuple of numbers, a `ClassVar`, or a module constant no field
defaults to is not.
"""

from __future__ import annotations

import dataclasses
import importlib
import inspect
import pkgutil
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import doc_check

import anesthesia_sim.core
from anesthesia_sim.core.concentration import Percent

REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclasses.dataclass(frozen=True)
class _Default:
    """One numeric field default, and the class that declares it."""

    owner: str
    field: str
    value: float


def _core_dataclasses() -> list[type[Any]]:
    """Every dataclass defined under `core/`, the package's own module included."""

    modules = [anesthesia_sim.core] + [
        importlib.import_module(module.name)
        for module in pkgutil.walk_packages(
            anesthesia_sim.core.__path__, f"{anesthesia_sim.core.__name__}."
        )
    ]

    return [
        member
        for module in modules
        for member in vars(module).values()
        if inspect.isclass(member)
        and dataclasses.is_dataclass(member)
        and member.__module__ == module.__name__
    ]


def _numeric_defaults(classes: Iterable[type[Any]]) -> list[_Default]:
    """Each class's numeric field defaults, a default factory's result included."""

    defaults = []
    for cls in classes:
        for field in dataclasses.fields(cls):
            if field.default is not dataclasses.MISSING:
                value = field.default
            elif field.default_factory is not dataclasses.MISSING:
                value = field.default_factory()
            else:
                continue

            if isinstance(value, (int, float)) and not isinstance(value, bool):
                defaults.append(_Default(f"{cls.__module__}.{cls.__qualname__}", field.name, value))

    return defaults


def _empty_or_whole(value: float) -> bool:
    """Zero, or the whole of the value's own scale: 1, or 100 for a `Percent`."""

    whole = 100.0 if isinstance(value, Percent) else 1.0
    return value in (0.0, whole)


def _selected_values() -> frozenset[float]:
    """Every number in the Selected-value column of `docs/MODEL.md`'s provenance table.

    Read through the parser `check_provenance` uses, so the table compared
    against here is the one that check holds to the data files.
    """

    rows, note = doc_check._provenance_rows(
        (REPO_ROOT / doc_check.MODEL).read_text(encoding="utf-8")
    )
    assert rows, note or "docs/MODEL.md has no provenance table under 'Parameter provenance'"
    column = doc_check.PROVENANCE_HEADER.index("Selected value")

    return frozenset(
        float(number)
        for _line, cells in rows
        for number in doc_check.NUMBER_RE.findall(cells[column])
    )


def _unsourced(defaults: Iterable[_Default], selected: frozenset[float]) -> list[_Default]:
    """The defaults that are neither empty nor whole and that `selected` does not hold."""

    return [
        default
        for default in defaults
        if not _empty_or_whole(default.value) and default.value not in selected
    ]


def test_every_constant_a_core_dataclass_defaults_to_is_a_value_the_provenance_table_selects() -> (
    None
):
    """A fifth `core/` constant cannot arrive with no data file behind it.

    The four there today - the alveolar gas volume and ventilation, the
    circuit volume and the fresh gas flow - each restate a data file's value,
    and pass. The walk is required to have read something, so a change that
    stopped it finding the package's modules fails here rather than passing an
    empty screen.
    """

    defaults = _numeric_defaults(_core_dataclasses())
    assert defaults, (
        "the walk over anesthesia_sim.core found no numeric field default at all, so it "
        "read no module and this screen governs nothing"
    )

    unsourced = _unsourced(defaults, _selected_values())

    assert not unsourced, (
        "; ".join(f"{default.owner}.{default.field} = {default.value!r}" for default in unsourced)
        + ": a numeric field default in core/ that docs/MODEL.md's provenance table selects "
        "nowhere is a scientific constant no data file holds, and tools/doc_check.py's "
        "check_provenance cannot see it. Store it in the data file it belongs to, with a row "
        "in that table, as PL-4YY1 did for the circuit's volume and fresh gas flow, or build "
        "the field without a default. This is a screen, not a proof: it matches values rather "
        "than names, so a new constant equal to a value the table already selects passes it."
    )


def test_the_screen_refuses_an_unsourced_default_and_passes_empty_state_and_the_whole() -> None:
    """Each branch of the comparison, on a dataclass built to reach it.

    A dead space of 0.15 L is `PL-65HT`'s own example of a constant entering
    `core/` with no source, and 0.35 L the same arriving through a factory. A
    1% dial is a value on a `Percent`'s scale that is neither empty nor whole,
    where 1 on any other scale is the whole. A volume of 6.0 L passes because
    the set it is compared against selects 6.0, which is the screen's limit
    and no proof of where that field's value came from.
    """

    @dataclasses.dataclass
    class Airway:
        dead_space_l: float = 0.15
        dial_percent: Percent = Percent(1.0)
        vaporizer_maximum_percent: Percent = Percent(100.0)
        unit_fraction: float = 1.0
        step_count: int = 0
        bypassed: bool = True
        volume_l: float = 6.0
        label: str = "airway"
        washout_l: float = dataclasses.field(default_factory=lambda: 0.35)

    unsourced = _unsourced(_numeric_defaults([Airway]), frozenset({6.0}))

    assert [default.field for default in unsourced] == ["dead_space_l", "dial_percent", "washout_l"]
