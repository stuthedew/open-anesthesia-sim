"""Every string the dashboard shows is on a list that a person has approved.

The interface's wording tests in `test_simulation_view.py` refuse phrases
somebody thought of, such as an unhedged "end-tidal". A list of forbidden
phrases misses the wording nobody listed, so this test holds the text to an
allowed list instead (`PL-86VL`). It builds a dashboard that holds every
registered View, records every string it holds at fixed points of a run of
each agent, and compares them with `approved_interface_strings.json` beside
this file. The simulation is deterministic, so the strings at a fixed
simulated time are too. Hidden strings are included, because a hidden string
can be shown at any moment.

Each digit is replaced by `#` before the comparison. The test is about
wording, and the numbers are the model's, which other tests check. A changed
model value would otherwise fail here with dozens of changed numbers, and a
real change of wording would be lost among them. The number of digits and the
place of the decimal point are kept, so a change in how many decimals a value
shows still fails here.

The recorded points use the default settings with no change by the learner.
A string that appears only after a setting changes, with a bookmark or a
price, or in a halt or failure notice, is not recorded, and this test does
not hold it.

A change to any text on screen therefore fails here until a person approves
it. To approve, check the new wording, run

    APPROVE_INTERFACE_WORDING=1 uv run pytest tests/integration/test_interface_wording.py

and commit the rewritten file, so that the reviewer of the pull request sees
every changed string in its diff. This is approval testing, in the sense of
a stored, human-approved output that a test compares against.

The application's version is written into one string, and changes with every
commit. It is replaced by `{version}` before its digits are masked.
"""

import json
import os
import re
from collections.abc import Iterator
from pathlib import Path

import pytest
from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QApplication

from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.app.dashboard_frame import SIMULATION_STEP_S
from anesthesia_sim.app.simulation_view import SimulationView
from anesthesia_sim.app.view_registry import REGISTERED
from anesthesia_sim.app_metadata import APP_BUILD_VERSION
from anesthesia_sim.layout.model import LayoutModel
from anesthesia_sim.layout.tree import Area, AreaId, Orientation, Split, ViewKind, Window
from anesthesia_sim.layout.workspace import Origin, Workspace, WorkspaceName, WorkspaceSet

APPROVED_FILE = Path(__file__).with_name("approved_interface_strings.json")
APPROVE_VARIABLE = "APPROVE_INTERFACE_WORDING"
VERSION_PLACEHOLDER = "{version}"
_DIGIT = re.compile(r"[0-9]")

#: The points at which the strings are recorded, each an agent and a simulated
#: time. Sevoflurane, the default agent, is recorded before Start, during
#: wash-in and later in the case. Desflurane and isoflurane are recorded during
#: wash-in, because some strings name the agent or its own values. A time of
#: `None` is a run that has not started.
RECORDED_POINTS: dict[str, tuple[str, float | None]] = {
    "not started": ("sevoflurane", None),
    "2 min": ("sevoflurane", 120.0),
    "10 min": ("sevoflurane", 600.0),
    "desflurane, 2 min": ("desflurane", 120.0),
    "isoflurane, 2 min": ("isoflurane", 120.0),
}

#: The window size. Changing it changed no string on 2026-11-11 (1000, 1400
#: and 1900 px wide gave the same strings), but a fixed size keeps the test
#: from depending on that.
_WINDOW_WIDTH_PX = 1400
_WINDOW_HEIGHT_PX = 4000


def _every_view_in_one_column() -> WorkspaceSet:
    """One Workspace with one Area for each registered View, so every View is built."""

    kinds = tuple(REGISTERED)
    count = len(kinds)
    areas = tuple(Area(AreaId(number), ViewKind(kind)) for number, kind in enumerate(kinds, 1))
    split = Split(Orientation.COLUMN, tuple(1.0 / count for _ in kinds), areas)

    return WorkspaceSet(
        (
            Workspace(
                WorkspaceName("Every View"),
                Origin.mine(),
                LayoutModel((Window(split),), AreaId(count + 1)),
            ),
        ),
        0,
    )


@pytest.fixture(scope="module")
def application() -> Iterator[QApplication]:
    existing = QApplication.instance()

    yield existing if isinstance(existing, QApplication) else QApplication([])


def _masked(text: str) -> str:
    """`text` with the version replaced and each digit replaced by `#`."""

    return _DIGIT.sub("#", text.replace(APP_BUILD_VERSION, VERSION_PLACEHOLDER))


def _strings_at(application: QApplication, agent_id: str, elapsed_s: float | None) -> list[str]:
    """Every string the dashboard holds in a run of `agent_id` at `elapsed_s`, masked, sorted."""

    controller = SimulationController(agent_id=agent_id)

    if elapsed_s is not None:
        controller.start()

        for _ in range(round(elapsed_s / SIMULATION_STEP_S)):
            controller.advance(SIMULATION_STEP_S)

        controller.pause()

    view = SimulationView((controller,), workspaces=_every_view_in_one_column())

    try:
        view.resize(_WINDOW_WIDTH_PX, _WINDOW_HEIGHT_PX)
        view.show()
        application.processEvents()
        view.present(False)
        application.processEvents()
        strings = {_masked(text) for text in view.interface_strings()}
    finally:
        view.stop_timers()
        view.close()
        view.deleteLater()
        application.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        application.processEvents()

    return sorted(strings)


def _differences(approved: dict[str, list[str]], shown: dict[str, list[str]]) -> list[str]:
    """One line for each string added or removed at each point, for the failure message."""

    lines: list[str] = []

    for point in RECORDED_POINTS:
        before = set(approved.get(point, []))
        now = set(shown[point])
        lines.extend(f"  {point}, new: {text!r}" for text in sorted(now - before))
        lines.extend(f"  {point}, gone: {text!r}" for text in sorted(before - now))

    return lines


def test_every_string_the_view_shows_is_on_the_approved_list(application: QApplication) -> None:
    """A string added, changed or removed fails until the approved list is updated."""

    shown = {
        point: _strings_at(application, agent_id, seconds)
        for point, (agent_id, seconds) in RECORDED_POINTS.items()
    }

    if os.environ.get(APPROVE_VARIABLE) == "1":
        APPROVED_FILE.write_text(
            json.dumps(shown, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
        )

    approved = json.loads(APPROVED_FILE.read_text(encoding="utf-8"))
    differences = _differences(approved, shown)

    assert not differences, (
        "The interface's wording differs from the approved list:\n"
        + "\n".join(differences)
        + f"\nIf the new wording is right, run {APPROVE_VARIABLE}=1 uv run pytest "
        "tests/integration/test_interface_wording.py and commit "
        f"{APPROVED_FILE.name}."
    )


def test_a_changed_string_is_reported_as_one_gone_and_one_new() -> None:
    """The failure message names both sides of a change, at the point where it happened."""

    approved = {point: ["Fresh gas flow", "Cardiac output"] for point in RECORDED_POINTS}
    shown = {point: ["Fresh gas flow", "Cardiac output"] for point in RECORDED_POINTS}
    shown["2 min"] = ["Fresh gas flow", "ET sevo"]

    assert _differences(approved, shown) == [
        "  2 min, new: 'ET sevo'",
        "  2 min, gone: 'Cardiac output'",
    ]
