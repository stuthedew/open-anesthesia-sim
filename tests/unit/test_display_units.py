"""Each unit the interface states comes from one `DisplayUnit` member (`PL-G84G`, `PL-Q3G9`).

The expected spellings below are typed from what a reader sees and from what the
run record has always written. They are not read from the code under test. So a
change to a member's spelling fails here, and the change has to be a deliberate
decision rather than unnoticed drift.
"""

from __future__ import annotations

import pytest

from anesthesia_sim.app import dashboard_frame
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
from anesthesia_sim.app.display_units import DisplayUnit
from anesthesia_sim.app.formatting import MAC_UNIT_SUFFIX, format_flow


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
    """The label beside each slider and the unit its changes record name one unit."""

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
