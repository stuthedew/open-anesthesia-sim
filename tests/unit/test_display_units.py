"""Each unit the interface states comes from one `DisplayUnit` member (`PL-G84G`, `PL-Q3G9`).

The expected spellings below are typed from what a reader sees and from what the
run record has always written. They are not read from the code under test. So a
change to a member's spelling fails here, and the change has to be a deliberate
decision rather than unnoticed drift.
"""

from __future__ import annotations

import pytest

from anesthesia_sim.app import dashboard_frame
from anesthesia_sim.app.agent_cost import LIQUID_CAPTION_TEMPLATE, VAPOUR_CAPTION_TEMPLATE
from anesthesia_sim.app.compartment_schematic import AMOUNT_CONDITION_LINES
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
from anesthesia_sim.app.formatting import MAC_UNIT_SUFFIX, format_flow
from anesthesia_sim.core.liquid_agent import REFERENCE_PRESSURE_PA, REFERENCE_TEMPERATURE_CELSIUS


@pytest.mark.parametrize(
    ("unit", "recorded", "label", "axis_title"),
    [
        (DisplayUnit.FLOW, "L/min", "L/min", "L/min"),
        (DisplayUnit.CONCENTRATION, "percent of 1 atm", "%", "% of 1 atm"),
        (DisplayUnit.MAC_MULTIPLE, "multiple of MAC", "×MAC", "×MAC"),
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


def test_the_fork_point_entry_is_sized_from_the_clocks_own_format() -> None:
    """The widest entry is measured from text that `format_elapsed` writes.

    The measure below counts each character as 1 and adds 10 for each "9". The
    elapsed time has an hours part, a minutes part and a seconds part. For each
    part, the widest text is the first value, counting upward, that has the most
    nines and the most characters. That gives 19h, 19m and 19.9s. "9h" scores 12
    and "19h" scores 13. "19.9s" scores 25, against 24 for "9.9s".
    """

    def advance_px(text: str) -> int:
        return len(text) + 10 * text.count("9")

    entry = widest_fork_point_label(advance_px)

    assert entry == MARK_FORK_LABEL_TEMPLATE.format(instant="19h19m19.9s")


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
    assert (
        AMOUNT_CONDITION_LINES == f"Amounts are millilitres of vapour at 20 °C and 1 atm.\n{body}"
    )
    assert VAPOUR_CAPTION_TEMPLATE.endswith(" at 20 °C and 1 atm.")
    assert LIQUID_CAPTION_TEMPLATE.endswith(" at 20 °C.")
