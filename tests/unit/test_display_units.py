"""Each unit the interface states comes from one `DisplayUnit` member (`PL-G84G`, `PL-Q3G9`).

The expected spellings below are typed from what a reader sees and from what the
run record has always written. They are not read from the code under test. So a
change to a member's spelling fails here, and the change has to be a deliberate
decision rather than unnoticed drift.
"""

from __future__ import annotations

import ast
from datetime import date
from pathlib import Path

import pytest

from anesthesia_sim.app import dashboard_frame, display_units
from anesthesia_sim.app.agent_cost import (
    LIQUID_CAPTION_TEMPLATE,
    UNIT_CHOICES,
    VAPOUR_CAPTION_TEMPLATE,
)
from anesthesia_sim.app.compartment_schematic import AMOUNT_UNIT_TEXT
from anesthesia_sim.app.control_record import (
    CONTROL_INPUT_DISPLAY_UNITS,
    CONTROL_INPUT_UNITS,
    ControlInput,
)
from anesthesia_sim.app.dashboard_frame import (
    MARK_FORK_LABEL_TEMPLATE,
    PARAMETER_CONTROLS,
    widest_fork_point_label,
)
from anesthesia_sim.app.display_units import (
    REFERENCE_CONDITION_LABEL,
    REFERENCE_TEMPERATURE_LABEL,
    DisplayUnit,
)
from anesthesia_sim.app.formatting import (
    MAC_UNIT_SUFFIX,
    AgentAmountUnit,
    format_agent_residual,
    format_agent_volume,
    format_flow,
)
from anesthesia_sim.app.preferences import AgentPrice
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.liquid_agent import REFERENCE_PRESSURE_PA, REFERENCE_TEMPERATURE_CELSIUS


@pytest.mark.parametrize(
    ("unit", "recorded", "label", "axis_title"),
    [
        (DisplayUnit.FLOW, "L/min", "L/min", "L/min"),
        (DisplayUnit.CONCENTRATION, "percent of 1 atm", "%", "% of 1 atm"),
        (DisplayUnit.MAC_MULTIPLE, "multiple of MAC", "×MAC", "×MAC"),
        (DisplayUnit.AGENT_VAPOUR_MILLILITRES, "millilitres of vapour", "mL vapour", "mL vapour"),
        (DisplayUnit.AGENT_VAPOUR_LITRES, "litres of vapour", "L vapour", "L vapour"),
        (
            DisplayUnit.AGENT_LIQUID_MILLILITRES,
            "millilitres of liquid",
            "mL of liquid",
            "mL of liquid",
        ),
        (DisplayUnit.ACCOUNTED_AGENT_LITRES, "litres of equivalent pure agent gas", "L", "L"),
    ],
)
def test_each_unit_has_the_spellings_a_reader_meets(
    unit: DisplayUnit, recorded: str, label: str, axis_title: str
) -> None:
    assert (unit.recorded, unit.label, unit.axis_title) == (recorded, label, axis_title)


def test_a_controls_slider_label_and_recorded_unit_are_one_member() -> None:
    """The label beside each slider and the unit recorded for its changes name the same unit."""

    assert {control.control for control in PARAMETER_CONTROLS} == set(ControlInput)

    for control in PARAMETER_CONTROLS:
        unit = CONTROL_INPUT_DISPLAY_UNITS[control.control]

        assert control.unit == unit.label
        assert CONTROL_INPUT_UNITS[control.control] == unit.recorded


def test_a_slider_label_follows_its_controls_member(monkeypatch: pytest.MonkeyPatch) -> None:
    """Moving a control to another member moves its slider label with it.

    This test shows that the label is read from the member, and is not a copy
    that happens to match it.
    """

    moved = {**CONTROL_INPUT_DISPLAY_UNITS, ControlInput.FRESH_GAS_FLOW: DisplayUnit.CONCENTRATION}
    monkeypatch.setattr(dashboard_frame, "CONTROL_INPUT_DISPLAY_UNITS", moved)

    assert PARAMETER_CONTROLS[0].control is ControlInput.FRESH_GAS_FLOW
    assert PARAMETER_CONTROLS[0].unit == "%"


def test_the_formatters_write_the_members_labels() -> None:
    assert format_flow(4.0) == "4.0 L/min"
    assert MAC_UNIT_SUFFIX == " ×MAC"
    assert format_agent_volume(12.34) == "12.3 L"
    assert format_agent_residual(0.0) == "0 L"
    assert format_agent_residual(3e-13) == "<10⁻¹² L"
    assert format_agent_residual(float("inf")) == "inf L"


def test_the_cost_views_unit_names_are_the_members_full_spellings() -> None:
    """The selector names each unit as its `DisplayUnit` member writes it in full (`PL-2TWX`)."""

    assert UNIT_CHOICES == (
        (AgentAmountUnit.MILLILITRES_OF_LIQUID, "millilitres of liquid"),
        (AgentAmountUnit.LITRES_OF_VAPOUR, "litres of vapour"),
    )


def test_a_refused_bottle_volume_names_its_unit_from_the_member() -> None:
    with pytest.raises(
        SimulationConfigurationError, match="isoflurane bottle volume in millilitres of liquid"
    ):
        AgentPrice("isoflurane", 20.47, 0.0, "USD", date(2008, 3, 5))


# --- no spelling of an agent amount's unit outside the units module (`PL-2TWX`) ---

_APP = Path(display_units.__file__).parent

#: Every spelling of an agent amount's unit that is long enough to find in a
#: string without guessing. The accounting panel's bare "L" is not: a search for
#: one letter would report most strings in the package.
_AMOUNT_SPELLINGS = sorted(
    {
        spelling.casefold()
        for unit in DisplayUnit
        if "AGENT" in unit.name
        for spelling in (unit.recorded, unit.label, unit.axis_title)
        if len(spelling) > 1
    }
)


def _typed_amount_units(source: str, *, skip_class: str | None = None) -> list[tuple[int, str]]:
    """List each string in `source` that types an agent amount's unit, with its line.

    Docstrings are left out, because they describe the code and are not shown.
    Every other string is read, including each fixed part of an f-string. The
    body of the class `skip_class` is left out when one is named.
    """

    tree = ast.parse(source)
    prose: set[int] = set()
    skipped: set[int] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            prose.add(id(node.value))

        if isinstance(node, ast.ClassDef) and node.name == skip_class:
            skipped.update(id(inner) for inner in ast.walk(node))

    return sorted(
        (node.lineno, node.value)
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and id(node) not in prose
        and id(node) not in skipped
        and any(spelling in node.value.casefold() for spelling in _AMOUNT_SPELLINGS)
    )


def test_the_search_for_a_typed_amount_unit_finds_one_in_each_kind_of_string() -> None:
    """The search reads plain strings and f-strings, in any case, and leaves docstrings out."""

    source = (
        "def caption(amount: float) -> str:\n"
        '    """Return the amount in litres of vapour."""\n'
        '    return f"{amount} L vapour"\n'
        'NAME = "Millilitres of liquid"\n'
        'OTHER = "Show as"\n'
        "class Stored:\n"
        '    UNIT = "litres of vapour"\n'
    )

    assert _typed_amount_units(source) == [
        (3, " L vapour"),
        (4, "Millilitres of liquid"),
        (7, "litres of vapour"),
    ]
    assert _typed_amount_units(source, skip_class="Stored") == [
        (3, " L vapour"),
        (4, "Millilitres of liquid"),
    ]


def test_no_agent_amount_unit_is_spelled_outside_the_units_module() -> None:
    """Every module of `app/` reads an agent amount's unit from `DisplayUnit` (`PL-2TWX`).

    `docs/INTERFACE.md` § "The compartment schematic: what its heights, amounts
    and share bar assert" says that each spelling is defined once, in
    `app/display_units.py`. A spelling typed in another module would stay as it
    is when the member's spelling changes, and the two places would then name
    one amount in two ways.

    One class is left out. `AgentAmountUnit`'s values are the words that the
    preferences file stores for a unit. They are not shown, and they must not
    change when a spelling on screen does, or a saved file would stop being
    read. The last assert fails if the class stops holding such words, so the
    exception cannot outlive its reason.
    """

    typed = {
        path.name: found
        for path in sorted(_APP.glob("*.py"))
        if path.name != "display_units.py"
        and (
            found := _typed_amount_units(
                path.read_text(encoding="utf-8"),
                skip_class="AgentAmountUnit" if path.name == "formatting.py" else None,
            )
        )
    }

    assert typed == {}

    stored_words = _typed_amount_units((_APP / "formatting.py").read_text(encoding="utf-8"))

    assert sorted(word for _, word in stored_words) == sorted(
        member.value for member in AgentAmountUnit
    )


def test_the_fork_point_entry_is_sized_from_the_clocks_own_format() -> None:
    """The widest entry is measured from text that `format_elapsed` writes.

    The measure below counts each character as 1 and adds 10 for each "9". The
    elapsed time has an hours part, a minutes part and a seconds part. For each
    part, the widest text is the first value, counting upward, that has the most
    nines and the most characters. That gives 19h, 19m and 19s. "9h" scores 12
    and "19h" scores 13. "19s" scores 13, against 12 for "9s".
    """

    def advance_px(text: str) -> int:
        return len(text) + 10 * text.count("9")

    entry = widest_fork_point_label(advance_px)

    assert entry == MARK_FORK_LABEL_TEMPLATE.format(instant="19h19m19s")


def test_the_reference_condition_label_names_the_conversions_temperature_and_pressure() -> None:
    """The label states the condition at which `core/liquid_agent.py` converts vapour (`PL-RJN9`).

    The expected text is typed from `docs/MODEL.md` § "Agent amount", which states
    every amount at 20 °C and one standard atmosphere. The constants are checked
    against the same figures, so a change to either constant fails here and has
    to change the label's expected text with it.
    """

    assert REFERENCE_TEMPERATURE_CELSIUS == 20.0
    assert REFERENCE_PRESSURE_PA == 101_325.0
    assert REFERENCE_TEMPERATURE_LABEL == "20 °C"
    assert REFERENCE_CONDITION_LABEL == "20 °C and 1 atm"


def test_every_agent_amount_unit_names_the_reference_condition() -> None:
    """The accounting panel, the schematic and the agent cost View each name 20 °C and 1 atm.

    An amount of vapour means nothing without its temperature and pressure, and
    the amounts held in the body are stated at 20 °C though they are at body
    temperature (`PL-HQPF`). The liquid figure names only its temperature, since
    a liquid's volume barely changes with pressure. The accounting panel and
    the schematic also say that the amounts held in the body read high under
    that label, because they are body-temperature gas (blind review of
    `PL-HQPF`).
    """

    body = "Amounts in the body read high,\nas they are gas at body temperature."

    assert dashboard_frame.ACCOUNTING_UNIT_CAPTION == (
        f"Litres of equivalent pure agent gas,\nat 20 °C and 1 atm.\n{body}"
    )
    assert AMOUNT_UNIT_TEXT == "Amounts are millilitres of vapour at 20 °C and 1 atm."
    assert VAPOUR_CAPTION_TEMPLATE.endswith(" at 20 °C and 1 atm.")
    assert LIQUID_CAPTION_TEMPLATE.endswith(" at 20 °C.")
