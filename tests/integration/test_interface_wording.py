"""Every string the dashboard shows is on a stored list that was checked by hand.

The interface's wording tests in `tests/integration/simulation_view/` refuse phrases
somebody thought of, such as an unhedged "end-tidal". A list of forbidden
phrases misses the wording nobody listed, so this test holds the text to an
allowed list instead (`PL-86VL`). It builds a dashboard that holds every
registered View, records every string it holds at fixed points of a run of
each agent, and compares them with `approved_interface_strings.json` beside
this file. The simulation is deterministic, so the strings at a fixed
simulated time are too. Hidden strings are included, because a hidden string
can be shown at any moment.

Each digit is replaced by `#`, and each superscript digit by `^`, before the
comparison. The test is about wording, and the numbers are the model's, which
other tests check. A changed model value would otherwise fail here with dozens
of changed numbers, and a real change of wording would be lost among them. The
number of digits and the place of the decimal point are kept, so a change in
how many decimals a value shows still fails here.

Most strings appear in a default run, which the points in `RECORDED_POINTS`
record. Others appear only after an event: a setting change, a mark or a
price set by the reader, a refused setting, or a halt or failure notice.
`EVENT_POINTS` brings each of those states about and records it too
(`PL-4G79`). The halt and failure states are the run-state tests' own
scenarios, `_ONE_STATE_SCENARIOS` in
`tests/integration/simulation_view/test_simulation_view_run_stops_itself.py`,
so a state added there is recorded here as well. Those scenarios build the
run-state tests' dashboard, which shows fewer Views than this test's own. Where
a scenario injects a failure, the reason it names is the test's, and only the
wording around it is the interface's. An event point records only the strings
that no default point shows, so its list holds what the event brings up and
the reviewer of a change reads each string once.

A change to any text on screen therefore fails here until the list is
rewritten. Whoever changes the wording checks each changed string, runs

    APPROVE_INTERFACE_WORDING=1 uv run pytest tests/integration/test_interface_wording.py

and commits the rewritten file, so that the reviewer of the pull request sees
every changed string in its diff. This is approval testing, in the sense of
a stored, reviewed output that a test compares against.

A session may rewrite the list itself. The change waits for the project
owner, a clinician, only when it changes clinical meaning: the name, label or
unit of a clinical value; whether a value reads as modeled or measured; what
a warning, halt, refusal or stated limitation tells a learner about a value
or what to do; or wording that reads as a recommendation. The pull request's
`Owner-read:` record says which it is, as for any other change to the
simulator. Any other change merges on green, such as a layout notice, a
document pointer, punctuation, a corrected typo, or the name of a control or
View that names no clinical value. Where a change fits both lists, it waits
for the owner: renaming the "Cardiac output" control names a clinical value
(`PL-NRP7`).

The application's version is written into one string, and changes with every
commit. It is replaced by `{version}` before its digits are masked.
"""

import json
import os
from collections.abc import Callable, Iterator, Mapping
from datetime import date
from pathlib import Path
from typing import Final

import pytest
from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QApplication

from anesthesia_sim.app import dashboard_frame as dashboard_frame_module
from anesthesia_sim.app.area_layout import AreaNotice
from anesthesia_sim.app.bookmarks import MacTarget, TimeBookmark
from anesthesia_sim.app.controller import BranchedCase, SimulationController
from anesthesia_sim.app.preferences import AgentPrice, LoadedPreferences, Preferences
from anesthesia_sim.app.run_series import RecordedQuantity
from anesthesia_sim.app.simulation_view import SimulationView
from anesthesia_sim.app.view_registry import REGISTERED
from anesthesia_sim.app.views import ConcentrationView
from anesthesia_sim.app_metadata import APP_BUILD_VERSION
from anesthesia_sim.core import supported_ranges as supported_ranges_module
from anesthesia_sim.core.concentration import MacMultiple, Percent
from anesthesia_sim.core.simulation_step import SIMULATION_STEP_S
from anesthesia_sim.core.supported_ranges import CaseInstant, FreshGasFlow
from anesthesia_sim.layout.model import LayoutModel
from anesthesia_sim.layout.run_identity import RunId, SessionToken
from anesthesia_sim.layout.tree import Area, AreaId, Orientation, Split, ViewKind, Window
from anesthesia_sim.layout.workspace import Origin, Workspace, WorkspaceName, WorkspaceSet
from tests.integration.simulation_view.simulation_view_support import (
    _delete_shown_views,
    _fork_panel,
    _halted_branch_view,
    _mark_editor,
    _real_step_failure,
)
from tests.integration.simulation_view.test_simulation_view_run_stops_itself import (
    _ONE_STATE_SCENARIOS,
)

APPROVED_FILE = Path(__file__).with_name("approved_interface_strings.json")
APPROVE_VARIABLE = "APPROVE_INTERFACE_WORDING"
VERSION_PLACEHOLDER = "{version}"
# A superscript digit, as in a residual's power of ten, is masked as a raised
# `#`, so the exponent's length and its place are still checked (`PL-8V6L`).
_DIGITS_TO_HASH = str.maketrans(dict.fromkeys("0123456789", "#") | dict.fromkeys("⁰¹²³⁴⁵⁶⁷⁸⁹", "^"))

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
_SECONDS_PER_MINUTE = 60
# More steps than any point here takes: the longest, the supported run length
# shortened to 5 min, takes 300. A loop that stops at the budget reports where
# the run stood, where an unbounded loop would hang the suite with no message.
_STEP_BUDGET = 2000


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

    return text.replace(APP_BUILD_VERSION, VERSION_PLACEHOLDER).translate(_DIGITS_TO_HASH)


def _run_to(controller: SimulationController, elapsed_s: float) -> None:
    """Start `controller` if it is not running, step it to `elapsed_s` and pause it.

    Raises:
        AssertionError: The run stopped itself before `elapsed_s`, as on a mark
            or a failure, or did not reach it within `_STEP_BUDGET` steps.
    """

    if not controller.is_running:
        controller.start()

    for _ in range(_STEP_BUDGET):
        if controller.snapshot().elapsed_s >= elapsed_s:
            break

        if not controller.is_running:
            raise AssertionError(
                f"the run stopped itself at {controller.snapshot().elapsed_s} s, "
                f"before {elapsed_s} s"
            )

        controller.advance()
    else:
        raise AssertionError(f"the run did not reach {elapsed_s} s in {_STEP_BUDGET} steps")

    controller.pause()


def _run_until_it_stops(controller: SimulationController) -> None:
    """Start `controller` and step it until it stops itself, within `_STEP_BUDGET` steps."""

    controller.start()

    for _ in range(_STEP_BUDGET):
        if not controller.is_running:
            return

        controller.advance()

    raise AssertionError(
        f"the run was still running at {controller.snapshot().elapsed_s} s "
        f"after {_STEP_BUDGET} steps"
    )


def _strings_of(application: QApplication, view: SimulationView) -> list[str]:
    """Every string `view` holds now, masked and sorted."""

    application.processEvents()

    return sorted({_masked(text) for text in view.interface_strings()})


def _strings_but_area_notices(application: QApplication, view: SimulationView) -> list[str]:
    """Every string `view` holds now, masked and sorted, except an Area notice's.

    A dashboard that the run-state tests built is laid out in their smaller
    window, where some Areas are too small for their View. Which Area that is
    depends on the fonts: the container's font found the concentration chart's
    Area too small, and CI's found the Parameters Area too small (2026-11-22).
    The notice is about the layout and not about the run's state, so it is
    left out here (`PL-P6TK`).
    """

    notices = {
        _masked(label.text())
        for notice in view.findChildren(AreaNotice)
        for label in (notice.title_label, notice.body_label)
    }

    return [text for text in _strings_of(application, view) if text not in notices]


def _strings_shown(
    application: QApplication,
    controller: SimulationController,
    preferences: LoadedPreferences | None = None,
    act: Callable[[SimulationView], None] | None = None,
) -> list[str]:
    """Every string a dashboard over `controller` holds once it has drawn, masked and sorted.

    The dashboard holds the run in a case, as the application's always does,
    so the Branch View shows its control and not the words for runs that
    belong to no case. Where `act` is given, it is done to the dashboard
    after the first frame, before the strings are recorded.
    """

    view = SimulationView(
        (controller,),
        case=BranchedCase(controller),
        workspaces=_every_view_in_one_column(),
        preferences=preferences,
    )

    try:
        view.resize(_WINDOW_WIDTH_PX, _WINDOW_HEIGHT_PX)
        view.show()
        application.processEvents()
        view.present(False)

        if act is not None:
            act(view)

        return _strings_of(application, view)
    finally:
        view.stop_timers()
        view.close()
        view.deleteLater()
        application.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        application.processEvents()


def _strings_at(application: QApplication, agent_id: str, elapsed_s: float | None) -> list[str]:
    """Every string the dashboard holds in a run of `agent_id` at `elapsed_s`, masked, sorted."""

    controller = SimulationController(agent_id=agent_id)

    if elapsed_s is not None:
        _run_to(controller, elapsed_s)

    return _strings_shown(application, controller)


def _after_a_setting_change(application: QApplication, _patch: pytest.MonkeyPatch) -> list[str]:
    """Sevoflurane at 2 min, with three kinds of line in the change record.

    The fresh gas flow changes once at 1 min, which the record words as a flow.
    The delivered concentration changes at 90 s and again at 100 s, with no
    new adjustment begun between them. The record words that as one change in
    percent, over an interval, of two settings.
    """

    controller = SimulationController()
    _run_to(controller, _SECONDS_PER_MINUTE)
    controller.set_fresh_gas_flow(FreshGasFlow(8.0))
    _run_to(controller, 90)
    controller.set_delivered_concentration_percent(Percent(3.0))
    _run_to(controller, 100)
    controller.set_delivered_concentration_percent(Percent(4.0))
    _run_to(controller, 2 * _SECONDS_PER_MINUTE)

    return _strings_shown(application, controller)


def _with_marks_set(application: QApplication, _patch: pytest.MonkeyPatch) -> list[str]:
    """Sevoflurane at 2 min, with a time mark ahead of the run and a MAC target on the alveoli."""

    controller = SimulationController()
    controller.add_time_bookmark(
        TimeBookmark(CaseInstant(10 * _SECONDS_PER_MINUTE), "the decision point")
    )
    controller.add_mac_target(MacTarget(RecordedQuantity.ALVEOLAR, MacMultiple(0.5)))
    _run_to(controller, 2 * _SECONDS_PER_MINUTE)

    return _strings_shown(application, controller)


def _stopped_on_a_mark(application: QApplication, _patch: pytest.MonkeyPatch) -> list[str]:
    """Sevoflurane stopped by the time mark at 1 min, which the run reached by itself."""

    controller = SimulationController()
    controller.add_time_bookmark(TimeBookmark(CaseInstant(_SECONDS_PER_MINUTE), "induction"))
    _run_until_it_stops(controller)

    assert controller.snapshot().elapsed_s == _SECONDS_PER_MINUTE
    return _strings_shown(application, controller)


def _a_mark_reached(application: QApplication, _patch: pytest.MonkeyPatch) -> list[str]:
    """Sevoflurane stopped on a MAC target it reached, then run on to 6 min.

    The default run's alveolar concentration crosses 0.5 xMAC at about 5 min
    and stops there. Run on past the mark, the run states it as reached.
    """

    controller = SimulationController()
    controller.add_mac_target(MacTarget(RecordedQuantity.ALVEOLAR, MacMultiple(0.5)))
    _run_until_it_stops(controller)
    _run_to(controller, 6 * _SECONDS_PER_MINUTE)

    return _strings_shown(application, controller)


def _marks_on_compared_runs(application: QApplication, _patch: pytest.MonkeyPatch) -> list[str]:
    """A trunk and a branch whose marks stand differently, and the trunk then failed.

    The branch opens at 60 s and stops on a 0.5 xMAC target that the trunk,
    paused at 60 s, has not reached (`_halted_branch_view`). A time mark at
    30 s comes before the branch opened. Two marks added after the fork, at
    90 s and at 0.8 xMAC in fat, are outstanding on the trunk, which a step
    failure then stops. Each row names the run each answer belongs to.
    """

    view = _halted_branch_view(application)

    try:
        editor = _mark_editor(view)
        editor.instant_spin.setValue(90)
        editor.add_time_button.click()
        editor.compartment_combo.setCurrentIndex(
            editor.compartment_combo.findData(RecordedQuantity.FAT.value)
        )
        editor.height_spin.setValue(0.8)
        editor.add_target_button.click()
        view.runs[0].halt(_real_step_failure())
        view.present(False)
        return _strings_but_area_notices(application, view)
    finally:
        _delete_shown_views(application)


def _with_a_price_set(application: QApplication, _patch: pytest.MonkeyPatch) -> list[str]:
    """Sevoflurane at 2 min, with the reader's price for sevoflurane, so a cost is shown."""

    price = AgentPrice("sevoflurane", 150.0, 250.0, "USD", date(2026, 1, 1))
    preferences = LoadedPreferences(Preferences().with_price(price), writable=True, notice=None)
    controller = SimulationController()
    _run_to(controller, 2 * _SECONDS_PER_MINUTE)

    return _strings_shown(application, controller, preferences)


def _a_refused_setting(application: QApplication, _patch: pytest.MonkeyPatch) -> list[str]:
    """Isoflurane at 2 min, with 50% dialled past the vaporizer's maximum, which is refused."""

    controller = SimulationController(agent_id="isoflurane")
    _run_to(controller, 2 * _SECONDS_PER_MINUTE)
    view = SimulationView((controller,), workspaces=_every_view_in_one_column())

    try:
        view.resize(_WINDOW_WIDTH_PX, _WINDOW_HEIGHT_PX)
        view.show()
        application.processEvents()
        view.present(False)
        view.runs[0]._handle_delivered_concentration_change(50.0)
        view.present(False)
        return _strings_of(application, view)
    finally:
        view.stop_timers()
        view.close()
        view.deleteLater()
        application.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        application.processEvents()


def _at_the_supported_run_length(application: QApplication, patch: pytest.MonkeyPatch) -> list[str]:
    """Sevoflurane stopped at the supported run length, shortened here to 5 min.

    The shortened length is the run-state tests' own way to reach it in a few
    seconds of testing (`_a_dial_moved_at_the_supported_run_length`). The
    notice names the length, and its digits are masked.
    """

    patch.setattr(supported_ranges_module, "MAXIMUM_STEP_COUNT", 300 // SIMULATION_STEP_S)
    controller = SimulationController()
    # Both marks lie beyond what the shortened run reaches, so each is stated
    # as not reached within the supported run length.
    controller.add_time_bookmark(TimeBookmark(CaseInstant(10 * _SECONDS_PER_MINUTE), "late"))
    controller.add_mac_target(MacTarget(RecordedQuantity.FAT, MacMultiple(0.8)))
    _run_until_it_stops(controller)

    return _strings_shown(application, controller)


def _approaching_the_supported_run_length(
    application: QApplication, patch: pytest.MonkeyPatch
) -> list[str]:
    """Sevoflurane paused 2 min into a run whose limit is moved to just past the warning.

    The banner that announces the stop opens `APPROACHING_LIMIT_NOTICE_S`
    before the supported run length (`PL-H2K2`). Reaching it at the real
    length takes more than 80 000 steps, so the banner's check reads a
    limit moved to two minutes past the warning's span, which puts the run
    inside it from its third minute. Only the banner's countdown reads the
    moved limit, and its digits are masked.
    """

    patch.setattr(
        dashboard_frame_module,
        "MAXIMUM_ELAPSED_SIMULATION_TIME_S",
        dashboard_frame_module.APPROACHING_LIMIT_NOTICE_S + 2 * _SECONDS_PER_MINUTE,
    )
    controller = SimulationController()
    _run_to(controller, 2 * _SECONDS_PER_MINUTE)

    return _strings_shown(application, controller)


def _in_the_run_state_scenario(
    name: str,
) -> Callable[[QApplication, pytest.MonkeyPatch], list[str]]:
    """Record the dashboard that one of the run-state tests' scenarios leaves."""

    def strings(application: QApplication, patch: pytest.MonkeyPatch) -> list[str]:
        run, _ = _ONE_STATE_SCENARIOS[name](application, patch)
        view = run.window()
        assert isinstance(view, SimulationView), type(view)

        try:
            return _strings_but_area_notices(application, view)
        finally:
            _delete_shown_views(application)

    return strings


def _branched_in_a_pinned_workspace(
    application: QApplication, _patch: pytest.MonkeyPatch
) -> list[str]:
    """A branch taken in a Workspace pinned to a run of an earlier session (`PL-YQ5J`).

    The trunk is paused at 1 min, and "Branch here" opens a branch there.
    The Workspace draws neither run, so the Branch View's caption says why.
    """

    trunk = SimulationController()
    _run_to(trunk, 60.0)
    layout = _every_view_in_one_column()
    earlier = RunId(SessionToken("f" * 32), 1)
    view = SimulationView(
        (trunk,),
        case=BranchedCase(trunk),
        workspaces=layout.replace(0, layout.current.pinned_to(earlier)),
    )

    try:
        view.resize(_WINDOW_WIDTH_PX, _WINDOW_HEIGHT_PX)
        view.show()
        application.processEvents()
        view.present(False)
        _fork_panel(view).here_button.click()
        return _strings_of(application, view)
    finally:
        view.stop_timers()
        view.close()
        view.deleteLater()
        application.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        application.processEvents()


def _with_a_window_held(application: QApplication, _patch: pytest.MonkeyPatch) -> list[str]:
    """Sevoflurane at 30 min, with the concentration chart at 15 minutes and moved one step back.

    The held window's axis title and the line naming what it shows appear only
    while a reader holds a chart's window back from the run (`PL-Z7LY`).
    """

    def hold(view: SimulationView) -> None:
        chart_view = next(
            widget for widget in view.findChildren(ConcentrationView) if widget.isVisible()
        )
        selector = chart_view.time_base_selector
        selector.setCurrentIndex(selector.findData("900.0"))
        chart_view._window.earlier_button.click()

    controller = SimulationController()
    _run_to(controller, 30 * _SECONDS_PER_MINUTE)

    return _strings_shown(application, controller, act=hold)


#: Each state that only an event brings up, and how the test brings it about.
#: The run-state tests' "drawn frame" is a default run, which `RECORDED_POINTS`
#: already covers.
EVENT_POINTS: Final[Mapping[str, Callable[[QApplication, pytest.MonkeyPatch], list[str]]]] = {
    "setting changed": _after_a_setting_change,
    "marks set": _with_marks_set,
    "stopped on a mark": _stopped_on_a_mark,
    "mark reached": _a_mark_reached,
    "marks on compared runs": _marks_on_compared_runs,
    "price set": _with_a_price_set,
    "setting refused": _a_refused_setting,
    "supported run length reached": _at_the_supported_run_length,
    "supported run length approaching": _approaching_the_supported_run_length,
    "branched in a pinned Workspace": _branched_in_a_pinned_workspace,
    "window held": _with_a_window_held,
    **{
        name: _in_the_run_state_scenario(name)
        for name in _ONE_STATE_SCENARIOS
        if name != "drawn frame"
    },
}


def _differences(approved: dict[str, list[str]], shown: dict[str, list[str]]) -> list[str]:
    """One line for each string added or removed at each point, for the failure message."""

    lines: list[str] = []

    for point in dict.fromkeys([*shown, *approved]):
        before = set(approved.get(point, []))
        now = set(shown.get(point, []))
        lines.extend(f"  {point}, new: {text!r}" for text in sorted(now - before))
        lines.extend(f"  {point}, gone: {text!r}" for text in sorted(before - now))

    return lines


def test_every_string_the_view_shows_is_on_the_approved_list(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A string added, changed or removed fails until the approved list is updated."""

    shown = {
        point: _strings_at(application, agent_id, seconds)
        for point, (agent_id, seconds) in RECORDED_POINTS.items()
    }

    in_a_default_run = set().union(*shown.values())

    for point, strings in EVENT_POINTS.items():
        with monkeypatch.context() as patch:
            shown[point] = sorted(set(strings(application, patch)) - in_a_default_run)

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
        f"{APPROVED_FILE.name}. This module's docstring says which changes wait "
        "for the project owner."
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
