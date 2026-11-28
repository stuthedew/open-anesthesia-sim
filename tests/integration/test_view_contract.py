"""The View contract, checked against every View this build registers (`PL-TH35`).

`app/view_contract.py` states the contract and its pruning rule: every member
of `View` has a call site in the adapter, and every registered kind builds a
View that satisfies the contract. These tests enforce that rule. They also
check what each shipped View owes a reader: saved state it can read, and a
notice where it cannot. In a real dashboard, they check that charts at one
window share a frame and that each chart's window is its own (`PL-L59K`).
They render under the `offscreen` platform that `tests/conftest.py` selects.
"""

import ast
import difflib
import itertools
import json
from collections.abc import Callable, Iterator, Sequence
from dataclasses import dataclass, fields, replace
from pathlib import Path
from typing import Final, NamedTuple, get_protocol_members

import numpy as np
import pyqtgraph as pg
import pytest
from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QBrush, QColor, QPen
from PySide6.QtWidgets import QApplication, QGraphicsView, QLabel, QScrollBar, QVBoxLayout, QWidget

from anesthesia_sim.app import area_layout
from anesthesia_sim.app import simulation_view as simulation_view_module
from anesthesia_sim.app.bookmarks import TimeBookmark
from anesthesia_sim.app.chart_time_base import FIT_RUN_KEY, ChartWindow, time_base_for_span
from anesthesia_sim.app.controller import BranchedCase, SimulationController
from anesthesia_sim.app.formatting import AgentAmountUnit, ChartCeiling
from anesthesia_sim.app.main import open_dashboard
from anesthesia_sim.app.preferences import PREFERENCES_FILE_NAME
from anesthesia_sim.app.qt_chart import _LineSwatch
from anesthesia_sim.app.run_presentation import RunPresentation, ShownFrame, ValuesStanding
from anesthesia_sim.app.run_series import COMPARTMENT_QUANTITIES, RecordedQuantity
from anesthesia_sim.app.simulation_view import SimulationView
from anesthesia_sim.app.view_contract import (
    STATE_VERSION_KEY,
    UNREADABLE_STATE_TEXT,
    CasePresentation,
    View,
    ViewContext,
    ViewRequests,
    ViewTick,
    unreadable_state_text,
)
from anesthesia_sim.app.view_registry import (
    COMPARTMENT_SCHEMATIC,
    CONCENTRATION_CHART,
    REGISTERED,
    WASH_IN,
    RegisteredView,
)
from anesthesia_sim.app.views import CompartmentSchematicView, ConcentrationView, WashInView
from anesthesia_sim.core.supported_ranges import CaseInstant
from anesthesia_sim.layout.serialization import workspace_set_to_json
from anesthesia_sim.layout.shipped import shipped_workspace
from anesthesia_sim.layout.store import USER_DIRECTORY_VARIABLE, WORKSPACES_FILE_NAME
from anesthesia_sim.layout.tree import AreaId
from anesthesia_sim.layout.workspace import ShippedWorkspaceId
from tests.integration.simulation_view.simulation_view_support import (
    _EVERY_VIEW,
    _advance,
    _branched_case,
    _failing_assembly,
    _select_agent,
    _set_delivered_percent,
    _set_fresh_gas_flow,
    _settle,
    _take_fork,
    _widget_state,
)

# The notice, written out here rather than read from the module that writes it.
_NOTICE = "This View's saved settings could not be read, so it shows its default settings."

_REQUESTS = ViewRequests(
    frame=lambda: None,
    compartment=lambda _quantity, _shown: None,
    agent_cost_unit=lambda _unit: None,
    chart_ceiling=lambda _ceiling: None,
    agent_price=lambda _agent, _price: None,
    refused_entries_discard=lambda: None,
    adjustment_start=lambda _run: None,
    setting=lambda _run, _control, _value, _input: None,
    preview=lambda _run, _control, _value: None,
    preview_end=lambda _run: None,
    mark_entry=lambda _entry: None,
    mark_edit=lambda _button, _entry: None,
    mark_remove=lambda _button, _row: None,
    mark_undo=lambda: None,
    branch_point=lambda _point: None,
    branch=lambda: None,
    branch_here=lambda: None,
)

_ENTRIES = list(REGISTERED.values())


@pytest.fixture(scope="module")
def application() -> Iterator[QApplication]:
    existing = QApplication.instance()

    yield existing if isinstance(existing, QApplication) else QApplication([])


@pytest.fixture
def dashboard(application: QApplication) -> Iterator[SimulationView]:
    view = SimulationView((SimulationController(),), workspaces=_EVERY_VIEW)
    view.resize(1600, 1000)
    view.show()
    application.processEvents()
    view.present(False)

    yield view

    view.stop_timers()
    view.close()
    view.deleteLater()
    application.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    application.processEvents()


def _built(entry: RegisteredView, saved: object = None) -> QWidget:
    view = entry.factory(ViewContext(_REQUESTS, saved))  # type: ignore[arg-type]
    assert isinstance(view, QWidget), f"{entry.kind}: the factory built no widget"

    return view


# ------------------------------------------------------------- the pruning rule


def test_every_member_of_the_contract_has_a_call_site_in_the_adapter() -> None:
    """A member nothing calls is deleted, not kept for later (`docs/interface-provenance.md`)."""

    source = Path(area_layout.__file__).read_text(encoding="utf-8")
    called = {node.attr for node in ast.walk(ast.parse(source)) if isinstance(node, ast.Attribute)}
    members = get_protocol_members(View)

    assert members == {
        "scope",
        "refresh",
        "owes_a_frame",
        "frame_request",
        "save_state",
        "painted_strings",
    }
    assert members <= called, f"never called by the adapter: {sorted(members - called)}"


@pytest.mark.parametrize("entry", _ENTRIES, ids=[entry.kind for entry in _ENTRIES])
def test_every_registered_kind_builds_a_widget_that_satisfies_the_contract(
    application: QApplication, entry: RegisteredView
) -> None:
    view = _built(entry)

    try:
        assert isinstance(view, View), f"{entry.kind}: the View lacks a member of the contract"
        assert view.owes_a_frame, f"{entry.kind}: a View never drawn owes no frame"
    finally:
        view.deleteLater()


def test_the_shared_layout_holds_every_registered_view() -> None:
    """The layout that the run-state tests build holds every kind the registry holds (`PL-B8DL`).

    Those tests walk the widgets of the layout they build. A kind left out of
    it is outside every one of them, as the compartment schematic and the
    agent cost View were for three weeks after they were registered.
    """

    kinds = [area.view for area in _EVERY_VIEW.current.layout.areas()]

    assert sorted(kinds) == sorted(REGISTERED)
    assert len(kinds) == len(set(kinds)), "a kind stands in two Areas"


# ------------------------------------------------------------------ saved state


@pytest.mark.parametrize("entry", _ENTRIES, ids=[entry.kind for entry in _ENTRIES])
def test_a_view_reads_back_the_state_it_saved(
    application: QApplication, entry: RegisteredView
) -> None:
    """The saved state is JSON-shaped and carries its version.

    The View built from that state shows no notice.
    """

    first = _built(entry)
    assert isinstance(first, View)
    saved = first.save_state()
    again = _built(entry, json.loads(json.dumps(dict(saved))))

    try:
        assert isinstance(saved[STATE_VERSION_KEY], int)
        assert again.state_notice.isHidden()  # type: ignore[attr-defined]
    finally:
        first.deleteLater()
        again.deleteLater()


@pytest.mark.parametrize("entry", _ENTRIES, ids=[entry.kind for entry in _ENTRIES])
def test_a_view_built_from_state_it_cannot_read_says_so(
    application: QApplication, entry: RegisteredView
) -> None:
    """`PL-TH35` Q4: drawing the defaults without a notice would be the stale-state failure."""

    view = _built(entry, {STATE_VERSION_KEY: 999})

    try:
        assert not view.state_notice.isHidden()  # type: ignore[attr-defined]
        assert view.state_notice.text() == _NOTICE  # type: ignore[attr-defined]
    finally:
        view.deleteLater()


def test_saved_state_is_readable_only_at_the_views_own_version() -> None:
    assert UNREADABLE_STATE_TEXT == _NOTICE
    assert unreadable_state_text(None, 1) is None
    assert unreadable_state_text({STATE_VERSION_KEY: 1}, 1) is None
    assert unreadable_state_text({STATE_VERSION_KEY: 1, "zoom": 2}, 1) is None

    for saved in (
        {},
        {STATE_VERSION_KEY: 2},
        {STATE_VERSION_KEY: "1"},
        # Neither passes for 1, though `True == 1` and `1.0 == 1` in Python.
        {STATE_VERSION_KEY: True},
        {STATE_VERSION_KEY: 1.0},
        [STATE_VERSION_KEY, 1],
        "state_version=1",
    ):
        assert unreadable_state_text(saved, 1) == _NOTICE, saved


def test_a_version_that_is_not_an_int_is_refused() -> None:
    for version in (True, 1.0, "1"):
        with pytest.raises(TypeError, match="a saved-state version is an int"):
            unreadable_state_text(None, version)  # type: ignore[arg-type]


# ------------------------------------------------------------ in the dashboard


def test_every_kind_chosen_in_an_area_is_drawn_at_once(
    application: QApplication, dashboard: SimulationView
) -> None:
    """A chosen View is drawn as soon as it is built, and drawing it halts no run."""

    for entry in _ENTRIES:
        dashboard.layout_container.choose_view(AreaId(1), entry.kind)
        view = dashboard.layout_container.frame(AreaId(1)).content

        assert isinstance(view, View), entry.kind
        assert not view.owes_a_frame, f"{entry.kind}: chosen, and still owes its first frame"
        assert not any(run.controller.has_failed for run in dashboard.runs), entry.kind


def test_two_areas_of_the_chart_draw_one_frame_sampled_for_the_wider(
    application: QApplication, dashboard: SimulationView
) -> None:
    """`PL-TH35` Q3 and Q8: one View per Area, and one frame for plots at one window (`PL-9LNF`)."""

    dashboard.layout_container.choose_view(AreaId(3), CONCENTRATION_CHART)
    dashboard.present(False)
    charts = [
        view for view in dashboard.layout_container.views() if isinstance(view, ConcentrationView)
    ]

    assert len(charts) == 2
    assert charts[0] is not charts[1]
    assert charts[0].chart.frame is not None
    assert charts[0].chart.frame is charts[1].chart.frame
    assert dashboard.layout_container.frame_requests() == {
        ChartWindow(None, None): max(view.chart.plot_width_px() for view in charts)
    }


# ------------------------------------------------------------- a chart's window


_CHARTS = (CONCENTRATION_CHART, WASH_IN)


def _chart(kind: str, saved: object = None) -> ConcentrationView | WashInView:
    view = _built(REGISTERED[kind], saved)
    assert isinstance(view, ConcentrationView | WashInView)

    return view


def _pick(chart: ConcentrationView | WashInView, key: str) -> None:
    index = chart.time_base_selector.findData(key)
    assert index >= 0, f"the time-base control does not offer {key!r}"
    chart.time_base_selector.setCurrentIndex(index)


@pytest.mark.parametrize("kind", _CHARTS)
def test_a_chart_saves_its_window_and_is_built_again_at_it(
    application: QApplication, kind: str
) -> None:
    """`PL-L59K`: the window is the chart's own state, version 2."""

    first = _chart(kind)
    _pick(first, "900.0")
    saved = json.loads(json.dumps(dict(first.save_state())))
    again = _chart(kind, saved)

    try:
        assert saved == {STATE_VERSION_KEY: 2, "time_base_s": 900.0}
        assert again.frame_request() is not None
        assert again.frame_request().window.time_base == time_base_for_span(900.0)  # type: ignore[union-attr]
        assert again.time_base_selector.currentData() == "900.0"
        assert again.state_notice.isHidden()
    finally:
        first.deleteLater()
        again.deleteLater()


@pytest.mark.parametrize("kind", _CHARTS)
def test_a_chart_built_with_draw_saved_fits_the_run(application: QApplication, kind: str) -> None:
    view = _chart(kind)

    try:
        assert view.frame_request().window.time_base is None  # type: ignore[union-attr]
        assert view.save_state() == {STATE_VERSION_KEY: 2, "time_base_s": FIT_RUN_KEY}
        assert view.time_base_selector.currentData() == FIT_RUN_KEY
    finally:
        view.deleteLater()


@pytest.mark.parametrize("kind", _CHARTS)
def test_a_version_1_chart_state_reads_as_fit_run_without_a_notice(
    application: QApplication, kind: str
) -> None:
    """Version 1 stored no setting, so nothing saved is lost and no notice is shown."""

    view = _chart(kind, {STATE_VERSION_KEY: 1})

    try:
        assert view.frame_request().window.time_base is None  # type: ignore[union-attr]
        assert view.state_notice.isHidden()
    finally:
        view.deleteLater()


@pytest.mark.parametrize("kind", _CHARTS)
@pytest.mark.parametrize(
    "saved",
    [
        {STATE_VERSION_KEY: 2},
        {STATE_VERSION_KEY: 2, "time_base_s": None},
        {STATE_VERSION_KEY: 2, "time_base_s": "900"},
        {STATE_VERSION_KEY: 2, "time_base_s": "Fit run"},
        # A rung that only fitting reaches, which the control cannot show.
        {STATE_VERSION_KEY: 2, "time_base_s": 60.0},
        {STATE_VERSION_KEY: 2, "time_base_s": 901.0},
        {STATE_VERSION_KEY: 2, "time_base_s": True},
        {STATE_VERSION_KEY: 1, "time_base_s": 900.0},
        {STATE_VERSION_KEY: 3, "time_base_s": 900.0},
    ],
)
def test_a_chart_whose_saved_window_cannot_be_read_fits_the_run_and_says_so(
    application: QApplication, kind: str, saved: dict[str, object]
) -> None:
    view = _chart(kind, saved)

    try:
        assert view.frame_request().window.time_base is None  # type: ignore[union-attr]
        assert not view.state_notice.isHidden()
        assert view.state_notice.text() == _NOTICE
    finally:
        view.deleteLater()


def _pick_ceiling(
    view: ConcentrationView | CompartmentSchematicView, ceiling: ChartCeiling
) -> None:
    """Pick `ceiling` on `view`'s axis-top control, sending the signals a reader's choice sends.

    Qt sets the index and then sends `activated`, which `setCurrentIndex` alone
    never sends.
    """

    index = view.ceiling_selector.findData(ceiling.name)
    assert index >= 0, f"the axis-top control does not offer {ceiling!r}"
    view.ceiling_selector.setCurrentIndex(index)
    view.ceiling_selector.activated.emit(index)


@pytest.mark.parametrize("kind", [CONCENTRATION_CHART, COMPARTMENT_SCHEMATIC])
def test_a_top_picked_on_a_chart_or_schematic_is_asked_for_and_saved_with_neither(
    application: QApplication, kind: str
) -> None:
    """`PL-7LZ7`: the axis top is the reader's preference, so a View only asks for it."""

    picks: list[ChartCeiling] = []
    view = REGISTERED[kind].factory(ViewContext(replace(_REQUESTS, chart_ceiling=picks.append)))
    assert isinstance(view, ConcentrationView | CompartmentSchematicView)

    try:
        _pick_ceiling(view, ChartCeiling.HIGH)

        assert picks == [ChartCeiling.HIGH]
        assert "ceiling_mac" not in view.save_state()
    finally:
        view.deleteLater()


@pytest.mark.parametrize("ceiling_mac", [4.5, 1.5, 3.0, 2.0, "3", True, None, 0.0])
def test_a_concentration_chart_saved_with_a_top_of_its_own_opens_without_a_notice(
    application: QApplication, ceiling_mac: object
) -> None:
    """`PL-7LZ7`: a chart saved by v0.6.22 to v0.6.24 keeps its window and drops its old top.

    Those builds saved each chart's own top under "ceiling_mac". The top is now
    the reader's preference, so the chart passes over whatever the key holds,
    and its state is not unreadable for it.
    """

    view = _chart(
        CONCENTRATION_CHART,
        {STATE_VERSION_KEY: 2, "time_base_s": 900.0, "ceiling_mac": ceiling_mac},
    )

    try:
        assert view.frame_request().window.time_base == time_base_for_span(900.0)  # type: ignore[union-attr]
        assert view.state_notice.isHidden()
        assert view.save_state() == {STATE_VERSION_KEY: 2, "time_base_s": 900.0}
    finally:
        view.deleteLater()


def _marks_every(step_mac: float, top_mac: float) -> list[float]:
    """Return the schematic's mark heights for MAC labels every `step_mac`, as shares of the top.

    The bottom and the top carry no mark, so the marks run from one step up to
    one step below the top.
    """

    count = round(top_mac / step_mac)

    return [index * step_mac / top_mac for index in range(1, count)]


def _assert_every_view_at(
    charts: Sequence[ConcentrationView],
    schematic: CompartmentSchematicView,
    label: str,
    top_percent: float,
    marks: Sequence[float],
) -> None:
    """Check that every chart and the schematic draw against one top, and name it alike."""

    frames = [chart.chart.frame for chart in charts]
    assert all(frame is frames[0] for frame in frames), "the charts draw different frames"
    assert frames[0] is not None
    assert frames[0].axis_top_percent == pytest.approx(top_percent)
    (run,) = schematic.schematics
    assert run.canvas.marks == pytest.approx(marks)
    assert f"0 to {top_percent:g}% of 1 atm ({label})" in run.scale_text.text()

    for view in (*charts, schematic):
        assert view.ceiling_selector.currentText() == label


def test_a_top_picked_on_any_chart_or_schematic_redraws_every_one_at_it(
    application: QApplication, dashboard: SimulationView
) -> None:
    """`PL-7LZ7`: every concentration chart and every schematic draws against one top.

    A top is picked on the second chart, then on the schematic, and each pick
    is drawn at once. The expected tops are the multiple times the running
    agent's MAC, read from its snapshot. The schematic's marks stand at the
    chart's MAC labels, every quarter MAC at 1.5 ×MAC and every half MAC at
    4.5 ×MAC, as `docs/INTERFACE.md` § "The chart's fixed MAC axis" says, and
    `_marks_every` writes them out as shares of the top.
    """

    dashboard.layout_container.choose_view(AreaId(2), CONCENTRATION_CHART)
    dashboard.present(False)
    views = dashboard.layout_container.views()
    charts = [view for view in views if isinstance(view, ConcentrationView)]
    (schematic,) = [view for view in views if isinstance(view, CompartmentSchematicView)]
    wash_in = next(view for view in views if isinstance(view, WashInView))
    mac_percent = dashboard.runs[0].controller.snapshot().agent_mac_percent
    presented = dashboard.presented_frames

    assert len(charts) == 2
    _assert_every_view_at(charts, schematic, "3 ×MAC", 3.0 * mac_percent, _marks_every(0.5, 3.0))

    _pick_ceiling(charts[1], ChartCeiling.LOW)

    assert dashboard.presented_frames == presented + 1, "the pick was not drawn at once"
    _assert_every_view_at(charts, schematic, "1.5 ×MAC", 1.5 * mac_percent, _marks_every(0.25, 1.5))
    assert wash_in.chart.frame is charts[0].chart.frame

    _pick_ceiling(schematic, ChartCeiling.HIGH)

    assert dashboard.presented_frames == presented + 2, "the pick was not drawn at once"
    _assert_every_view_at(charts, schematic, "4.5 ×MAC", 4.5 * mac_percent, _marks_every(0.5, 4.5))
    assert not any(view.owes_a_frame for view in (*charts, schematic, wash_in))


def test_a_top_picked_before_a_restart_is_the_top_after_it(
    application: QApplication, tmp_path: Path
) -> None:
    """`PL-7LZ7`: the top is saved once, in the reader's preferences, and read at launch.

    Both dashboards are opened as `main()` opens one, over one data directory.
    The second loads the preferences file that the first saved.
    """

    directory = tmp_path / "user"
    directory.mkdir()
    (directory / WORKSPACES_FILE_NAME).write_text(
        workspace_set_to_json(_EVERY_VIEW), encoding="utf-8"
    )
    opened: list[SimulationView] = []

    def opened_dashboard() -> SimulationView:
        view = open_dashboard(
            BranchedCase(SimulationController()), "", {USER_DIRECTORY_VARIABLE: str(directory)}
        )
        opened.append(view)
        view.resize(1600, 1000)
        view.show()
        application.processEvents()
        view.present(False)

        return view

    try:
        first = opened_dashboard()
        chart = next(
            view for view in first.layout_container.views() if isinstance(view, ConcentrationView)
        )
        _pick_ceiling(chart, ChartCeiling.HIGH)
        saved = json.loads((directory / PREFERENCES_FILE_NAME).read_text(encoding="utf-8"))

        assert saved["chart_axis_top_mac"] == 4.5

        first.stop_timers()
        first.close()
        restarted = opened_dashboard()
        views = restarted.layout_container.views()
        charts = [view for view in views if isinstance(view, ConcentrationView)]
        (schematic,) = [view for view in views if isinstance(view, CompartmentSchematicView)]
        mac_percent = restarted.runs[0].controller.snapshot().agent_mac_percent

        _assert_every_view_at(
            charts, schematic, "4.5 ×MAC", 4.5 * mac_percent, _marks_every(0.5, 4.5)
        )
    finally:
        for view in opened:
            view.stop_timers()
            view.close()
            view.deleteLater()

        application.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        application.processEvents()


def test_a_refused_saved_top_is_named_on_every_chart_and_schematic_until_a_top_is_picked(
    application: QApplication, tmp_path: Path
) -> None:
    """`PL-7LZ7`: a saved top off the choices is drawn at 3 xMAC, and every View says so.

    The file is one that a reader edited by hand. The notice is written out by
    hand. Picking 3 xMAC on the schematic, the top already shown, keeps it and
    clears the notice on every View at once. A control that asked only when
    the shown top changed left the notice in place for a reader who wanted
    3 xMAC.
    """

    directory = tmp_path / "user"
    directory.mkdir()
    (directory / WORKSPACES_FILE_NAME).write_text(
        workspace_set_to_json(_EVERY_VIEW), encoding="utf-8"
    )
    (directory / PREFERENCES_FILE_NAME).write_text(
        json.dumps(
            {
                "schema_version": 2,
                "agent_cost_unit": "millilitres of liquid",
                "agent_prices": [],
                "chart_axis_top_mac": 7,
            }
        ),
        encoding="utf-8",
    )
    view = open_dashboard(
        BranchedCase(SimulationController()), "", {USER_DIRECTORY_VARIABLE: str(directory)}
    )

    try:
        view.resize(1600, 1000)
        view.show()
        application.processEvents()
        view.present(False)
        views = view.layout_container.views()
        charts = [shown for shown in views if isinstance(shown, ConcentrationView)]
        (schematic,) = [shown for shown in views if isinstance(shown, CompartmentSchematicView)]
        mac_percent = view.runs[0].controller.snapshot().agent_mac_percent

        _assert_every_view_at(charts, schematic, "3 ×MAC", 3 * mac_percent, _marks_every(0.5, 3))
        for shown in [*charts, schematic]:
            assert not shown.ceiling_notice.isHidden()
            assert shown.ceiling_notice.text() == (
                "The saved axis top, 7, is not one of the choices, 1.5, 3 or 4.5 ×MAC, so every "
                "chart and schematic shows 3 ×MAC. Choose a top to replace it."
            )

        _pick_ceiling(schematic, ChartCeiling.STANDARD)

        for shown in [*charts, schematic]:
            assert shown.ceiling_notice.isHidden()
        saved = json.loads((directory / PREFERENCES_FILE_NAME).read_text(encoding="utf-8"))
        assert saved["chart_axis_top_mac"] == 3.0
    finally:
        view.stop_timers()
        view.close()
        view.deleteLater()
        application.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        application.processEvents()


def test_a_chart_keeps_its_plot_when_handed_the_kept_frame_it_already_shows(
    application: QApplication, dashboard: SimulationView, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A kept frame that a chart at 4.5 ×MAC already draws leaves its plot alone.

    Before `PL-7LZ7`, a chart at a top other than the standard one drew a copy
    of the shared frame. The check for whether the plot already showed a kept
    frame compared the kept frame with that copy, so it never matched. On a
    tick that kept the frame after the plot had widened, the chart emptied its
    plot and said nothing could be drawn, while a chart at 3 ×MAC kept its
    traces (blind review of `PL-K1VH`, both passes). Every chart now draws the
    frame it is handed, at the top in the reader's preferences.
    """

    chart = next(
        view for view in dashboard.layout_container.views() if isinstance(view, ConcentrationView)
    )
    ticks: list[ViewTick] = []
    refresh = chart.refresh
    monkeypatch.setattr(chart, "refresh", lambda tick: (ticks.append(tick), refresh(tick))[1])
    _pick_ceiling(chart, ChartCeiling.HIGH)
    drawn_tick = ticks[-1]
    assert drawn_tick.frame is not None and drawn_tick.frame.frame is not None
    source = drawn_tick.frame.frame
    drawn = chart.chart.frame
    assert drawn is source
    assert drawn.ceiling is ChartCeiling.HIGH
    # The plot is now wider than the width the kept frame was sampled for.
    monkeypatch.setattr(chart.chart, "plot_width_px", lambda: source.plot_width_px + 50.0)

    refresh(
        replace(
            drawn_tick, frame=ShownFrame(ValuesStanding.KEPT, source, drawn_tick.frame.selection)
        )
    )

    assert chart.chart.frame is drawn, "the chart emptied a plot that showed the kept frame"
    assert chart.withheld_text.isHidden()


def test_the_shipped_induction_chart_is_built_on_the_15_minute_window(
    application: QApplication,
) -> None:
    """`PL-L59K`: the state `induction.json` ships is one the chart reads without a notice."""

    induction = shipped_workspace(ShippedWorkspaceId("induction"))
    chart_area = next(
        area.id for area in induction.layout.areas() if area.view == CONCENTRATION_CHART
    )
    view = _chart(CONCENTRATION_CHART, induction.view_state[chart_area][CONCENTRATION_CHART])

    try:
        assert view.frame_request().window.time_base == time_base_for_span(900.0)  # type: ignore[union-attr]
        assert view.time_base_selector.currentData() == "900.0"
        assert view.state_notice.isHidden()
    finally:
        view.deleteLater()


def test_a_window_picked_in_one_chart_changes_only_that_chart(
    application: QApplication, dashboard: SimulationView
) -> None:
    """`PL-L59K`: each chart owns its window (project owner, 2026-10-19)."""

    dashboard.layout_container.choose_view(AreaId(2), CONCENTRATION_CHART)
    dashboard.present(False)
    charts = [
        view for view in dashboard.layout_container.views() if isinstance(view, ConcentrationView)
    ]
    wash_in = next(
        view for view in dashboard.layout_container.views() if isinstance(view, WashInView)
    )
    presented = dashboard.presented_frames

    _pick(charts[1], "900.0")

    assert dashboard.presented_frames == presented + 1, "the pick was not drawn at once"
    zoomed, fitted = charts[1].chart.frame, charts[0].chart.frame
    assert zoomed is not None and fitted is not None
    assert not zoomed.fitted and zoomed.time_base == time_base_for_span(900.0)
    assert (zoomed.start_s, zoomed.stop_s) == (0.0, 900.0)
    assert fitted.fitted
    assert charts[0].time_base_selector.currentData() == FIT_RUN_KEY
    assert charts[1].time_base_selector.currentData() == "900.0"
    # The F_A/F_I plot fits the run too, so it shares the first chart's frame.
    assert wash_in.chart.frame is fitted
    assert not any(view.owes_a_frame for view in (*charts, wash_in))
    assert not any(run.controller.has_failed for run in dashboard.runs)


# ------------------------------------------- a state drawn alike whatever came before


def _pen_reading(pen: QPen | None) -> tuple[object, ...] | None:
    """A pen as a reader sees it: its colour, width, line style and dash pattern."""

    if pen is None:
        return None

    return (
        pen.color().name(QColor.NameFormat.HexArgb),
        pen.widthF(),
        pen.style().name,
        tuple(pen.dashPattern()),
    )


def _brush_reading(brush: QBrush | None) -> tuple[object, ...] | None:
    """A fill as a reader sees it: its colour and its pattern."""

    if brush is None:
        return None

    return (brush.color().name(QColor.NameFormat.HexArgb), brush.style().name)


def _drawn_by(item: object) -> tuple[object, ...] | None:
    """What one visible item of a plot draws, or None for an item that draws nothing.

    A curve with fewer than two points and a scatter with no point draw
    nothing, so they are left out. A curve, a scatter's points, a line and
    a band are read with their pens and fills, because a trace's colour,
    width and dash say which compartment and which run it is
    (`chart_frame.run_trace_style`). For an axis, the reading is its title
    and the labels it was given (`qt_chart._axis_ticks` reads the same
    field).
    """

    reading: list[object] = [type(item).__name__]

    if isinstance(item, pg.PlotCurveItem | pg.ScatterPlotItem):
        x, y = item.getData()
        points = 0 if x is None else len(x)

        if points < (2 if isinstance(item, pg.PlotCurveItem) else 1):
            return None

        reading.extend((tuple(np.asarray(x).tolist()), tuple(np.asarray(y).tolist())))

        if isinstance(item, pg.PlotCurveItem):
            brush = item.opts["brush"]
            reading.extend(
                (
                    _pen_reading(item.opts["pen"]),
                    None if brush is None else _brush_reading(pg.mkBrush(brush)),
                    item.opts["fillLevel"],
                )
            )
        else:
            reading.append(
                tuple(
                    (
                        _pen_reading(spot.pen()),
                        _brush_reading(spot.brush()),
                        spot.symbol(),
                        spot.size(),
                    )
                    for spot in item.points()
                )
            )
    elif isinstance(item, pg.InfiniteLine):
        # pyqtgraph keeps a line's position as an int 0 until the line is moved
        # away from where it was built, because it skips a move to an equal
        # position. So a line placed at 0.0 reads 0 on a new chart and 0.0 on
        # one that drew another position first, at the same place on screen.
        reading.extend((float(item.value()), item.angle % 180, _pen_reading(item.pen)))
    elif isinstance(item, pg.LinearRegionItem):
        reading.extend(
            (
                tuple(item.getRegion()),
                _brush_reading(item.brush),
                tuple(_pen_reading(line.pen) for line in item.lines),
            )
        )
    elif isinstance(item, pg.TextItem):
        reading.append(item.textItem.toPlainText())
    elif isinstance(item, pg.AxisItem):
        reading.extend((item.labelText, repr(item._tickLevels)))

    return tuple(reading)


#: pyqtgraph's angles, in degrees, for a vertical and a horizontal `InfiniteLine`.
_VERTICAL_DEGREES: Final = 90
_HORIZONTAL_DEGREES: Final = 0


def _axes_placing(drawn: tuple[object, ...]) -> tuple[str, ...]:
    """The axes along which a plot's range places one drawn item, given what `_drawn_by` read.

    A curve, a scatter, a band and a text are placed along both axes. A
    vertical line is placed along the time axis only, and a horizontal line
    along the value axis only.
    """

    if drawn[0] in ("PlotCurveItem", "ScatterPlotItem", "LinearRegionItem", "TextItem"):
        return ("time", "value")

    if drawn[0] == "InfiniteLine":
        return {_VERTICAL_DEGREES: ("time",), _HORIZONTAL_DEGREES: ("value",)}[drawn[2]]

    return ()


def _plotted(view: QGraphicsView) -> list[tuple[object, ...]]:
    """What a plot draws: each visible item that draws something, and the ranges that place them.

    The range on one axis is read only while some drawn item is placed along
    that axis (`_axes_placing`). A withheld plot keeps the range of its last
    frame, and that range then places nothing a reader can see.
    """

    items = [item for item in view.scene().items() if item.isVisible()]
    drawn = [reading for item in items if (reading := _drawn_by(item)) is not None]
    placed = {axis for reading in drawn for axis in _axes_placing(reading)}

    for item in items:
        if isinstance(item, pg.ViewBox):
            ranges = dict(zip(("time", "value"), item.viewRange(), strict=True))
            drawn.extend((f"ViewBox, {axis} axis", tuple(ranges[axis])) for axis in sorted(placed))

    return drawn


class _Seen(NamedTuple):
    """What a reader sees of one widget itself."""

    kind: str
    hidden: bool
    enabled: bool
    style_sheet: str
    #: Everything else the widget shows: its text, value or painted strings,
    #: and for a legend swatch its pen and whether it is drawn.
    shown: tuple[object, ...]

    def paints(self) -> bool:
        """Whether the widget itself shows anything: a style sheet, or some text, value or mark.

        A plain container shows nothing itself, and its children are read on
        their own.
        """

        return bool(self.style_sheet or self.shown)


def _seen(widget: QWidget) -> _Seen:
    """What a reader sees of one widget itself, with a painted string's View named by its type.

    `AreaLayout.painted_strings` pairs each string with the View that paints
    it, so the View is named by its type here. Its address differs between
    two dashboards that show the same thing. A legend swatch draws a line
    and no text, so its pen and whether it is drawn are read from it
    (`qt_chart._LineSwatch`). The pen's dash is the second cue beside the
    colour for a reader who cannot tell the colours apart (`PL-88MK`).
    """

    kind, hidden, enabled, style_sheet, *rest = (
        tuple(
            (type(pair[0]).__name__, *pair[1:])
            if isinstance(pair, tuple) and pair and isinstance(pair[0], QWidget)
            else pair
            for pair in part
        )
        if isinstance(part, tuple)
        else part
        for part in _widget_state(widget)
    )

    if isinstance(widget, _LineSwatch):
        rest.extend((_pen_reading(widget._pen), widget._filled, widget._vertical))

    return _Seen(str(kind), bool(hidden), bool(enabled), str(style_sheet), tuple(rest))


#: The names that Qt gives the private widgets holding a `QScrollArea`'s two scroll bars.
_SCROLL_BAR_CONTAINERS: Final = frozenset({"qt_scrollarea_hcontainer", "qt_scrollarea_vcontainer"})


def _chain(widget: QWidget, root: QWidget) -> str:
    """The type of the widget and of up to five widgets above it, inside `root`, nearest first."""

    names: list[str] = []
    current: QWidget | None = widget

    while current is not None and len(names) < 6:
        names.append(type(current).__name__)
        current = None if current is root else current.parentWidget()

    return " < ".join(names)


def _screen(root: QWidget) -> list[tuple[str, str]]:
    """Everything a reader can see under `root`, found by a walk rather than a list.

    Each widget that `root` would show is read with `_seen`: its text,
    value, enabled state, style sheet and painted strings, and a legend
    swatch's pen. A plot's scene is read item by item (`_drawn_by`), so a
    curve, a line, a band, a pen or an axis label left from an earlier
    state is a difference, as a label's text is. A plain container with no
    style sheet paints nothing itself, and its children are read on their
    own, so it is left out. The entries are sorted, so two screens that
    list the same widgets in another order compare equal.

    A scroll bar is left out. Its range and whether it shows follow the
    height the page was last laid out at, which states nothing about a run,
    and Qt shows a bar by showing a private container (`PL-WM5P`, `PL-CSK0`).
    """

    screen: list[tuple[str, str]] = []

    for widget in (root, *root.findChildren(QWidget)):
        if isinstance(widget, QScrollBar) or widget.objectName() in _SCROLL_BAR_CONTAINERS:
            continue

        if not widget.isVisibleTo(root):
            continue

        chain = _chain(widget, root)
        seen = _seen(widget)

        if seen.paints():
            screen.append((chain, repr(seen)))

        if isinstance(widget, QGraphicsView) and widget.scene() is not None:
            screen.extend((f"{chain} :: item", repr(drawn)) for drawn in _plotted(widget))

    return sorted(screen)


#: The size every dashboard of the walk below is shown at, as `_EVERY_VIEW` needs.
_WALK_SIZE_PX: Final = (1400, 2800)


class _Frames:
    """Whether the dashboards' frames fail, switched as a state of the walk needs.

    Both dashboards share the switch, because the second is built over the
    runs that the first left.
    """

    def __init__(self) -> None:
        self._patch = pytest.MonkeyPatch()

    def fail(self, failing: bool) -> None:
        self._patch.undo()

        if failing:
            self._patch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)


@dataclass(frozen=True)
class _State:
    """One state of the dashboard in the walk, and the two ways of reaching it.

    Attributes:
        name: What the state is, in a reader's words.
        enter: What a dashboard that has shown the states before this one
            does to reach it. It may change the runs.
        again: What a new dashboard, built over the runs as `enter` left them,
            does to show the same state. It must leave the runs as they are,
            apart from a Reset of a run already at its opening. A dashboard
            keeps the values of the last frame it drew until a run starts
            over, so a halt after a start-over is reached by a Reset here.
        shown: The compartments the charts show. The selection belongs to
            the dashboard, so both dashboards are given it.
        unit: The agent cost View's unit, one of the reader's preferences,
            given to both dashboards for the same reason.
    """

    name: str
    enter: Callable[[SimulationView, _Frames], None]
    again: Callable[[SimulationView, _Frames], None]
    shown: tuple[RecordedQuantity, ...]
    unit: AgentAmountUnit


def _draw(view: SimulationView, frames: _Frames) -> None:
    """Let frames draw, and change nothing else: the state's own present draws the frame."""

    frames.fail(False)


def _take_the_fork(view: SimulationView, frames: _Frames) -> None:
    frames.fail(False)
    _take_fork(view, 60.0)


def _ask_the_trunk_s_reset(view: SimulationView, frames: _Frames) -> None:
    """Give the branch work that a Reset of the trunk would discard, and press the trunk's Reset."""

    frames.fail(False)
    _set_fresh_gas_flow(view.runs[1], 3.0)
    _press_the_trunk_s_reset(view, frames)


def _press_the_trunk_s_reset(view: SimulationView, frames: _Frames) -> None:
    view.runs[0]._reset_button.click()


def _branch_at_induction(view: SimulationView) -> None:
    """Run the restarted trunk to 2 minutes, draw it, and branch it at induction."""

    trunk = view.runs[0]
    assert len(view.runs) == 1, "the trunk's Reset kept the branch"
    trunk.controller.start()
    _advance(trunk.controller, 120)
    trunk.controller.pause()
    # The branch control offers the instants of the frame last drawn.
    view.present(False)
    _settle(QApplication.instance())
    _take_fork(view, 0.0)


def _discard_the_branch_and_branch_again(view: SimulationView, frames: _Frames) -> None:
    """Answer the open Reset question by discarding the branch, then branch the trunk again.

    The new branch sits where the discarded one sat, so a View that kept the
    discarded run's widgets or values for that place shows them beside the
    new run's name.
    """

    frames.fail(False)
    dialog = view.runs[0]._reset_dialog
    assert dialog is not None, "the trunk's Reset asked nothing"
    dialog.discard_button.click()
    _branch_at_induction(view)


def _drop_the_branch_and_branch_again(view: SimulationView, frames: _Frames) -> None:
    """Drop a branch that has no work with the trunk's Reset, then branch the trunk again.

    A dashboard numbers the runs it opens and never reuses a number. So the
    fresh dashboard drops a branch too, and names the new branch as the
    first dashboard does.
    """

    frames.fail(False)
    view.runs[0]._reset_button.click()
    _branch_at_induction(view)


def _mark_and_reset_while_frames_fail(view: SimulationView, frames: _Frames) -> None:
    """Add a mark, then press the trunk's Reset as frames fail, which drops the branch unasked.

    The branch was taken at induction and has no work of its own, so the
    Reset has nothing to ask.
    """

    frames.fail(True)
    view.runs[0].controller.add_time_bookmark(TimeBookmark(CaseInstant(30), "check"))
    view.runs[0]._reset_button.click()
    assert len(view.runs) == 1, "the trunk's Reset kept the branch"


def _reset_while_frames_fail(view: SimulationView, frames: _Frames) -> None:
    frames.fail(True)
    view.runs[0]._reset_button.click()


def _run_on_with_a_dial_moved(view: SimulationView, frames: _Frames) -> None:
    """Start the halted run over, run it to 5 minutes and move its delivered dial."""

    frames.fail(False)
    run = view.runs[0]
    run._reset_button.click()
    run.controller.start()
    _advance(run.controller, 300)
    run.controller.pause()
    _set_delivered_percent(run, 3.0)


def _ask_for_desflurane(view: SimulationView, frames: _Frames) -> None:
    frames.fail(False)
    _select_agent(view.runs[0], "desflurane")
    assert view.runs[0]._new_case_dialog is not None, "the agent change asked nothing"


def _start_desflurane_while_frames_fail(view: SimulationView, frames: _Frames) -> None:
    frames.fail(True)
    dialog = view.runs[0]._new_case_dialog
    assert dialog is not None
    dialog.discard_button.click()


def _draw_then_fail(view: SimulationView, frames: _Frames) -> None:
    """Draw a frame of the run as it stands, then make the next frame fail."""

    frames.fail(False)
    view.present(False)
    frames.fail(True)


def _run_on_then_fail(view: SimulationView, frames: _Frames) -> None:
    """Start the halted run over, run it to 2 minutes, draw it, and make the next frame fail."""

    frames.fail(False)
    run = view.runs[0]
    run._reset_button.click()
    run.controller.start()
    _advance(run.controller, 120)
    run.controller.pause()
    _draw_then_fail(view, frames)


_CIRCUIT, _ALVEOLAR = RecordedQuantity.CIRCUIT, RecordedQuantity.ALVEOLAR

#: The states the walk shows, in order. It includes a halt after a Reset and a
#: halt after an agent change, each with no frame drawn since, a halt that
#: keeps the last frame, two compared runs, a new branch in the place of a
#: dropped one, and the two open questions. Every
#: field of the tick a View is handed changes between some state and the one
#: after it, as `test_each_field_of_a_view_tick_changes_between_two_states_of_the_walk`
#: checks.
_STATES: Final = (
    _State(
        "one run drawn",
        _draw,
        _draw,
        tuple(COMPARTMENT_QUANTITIES),
        AgentAmountUnit.LITRES_OF_VAPOUR,
    ),
    _State(
        "two runs compared, drawn",
        _take_the_fork,
        _draw,
        (_CIRCUIT, _ALVEOLAR),
        AgentAmountUnit.MILLILITRES_OF_LIQUID,
    ),
    _State(
        "the trunk's Reset asks whether to discard the branch",
        _ask_the_trunk_s_reset,
        _press_the_trunk_s_reset,
        (RecordedQuantity.FAT, _ALVEOLAR),
        AgentAmountUnit.MILLILITRES_OF_LIQUID,
    ),
    _State(
        "a new branch compared in place of the one the trunk's Reset discarded",
        _discard_the_branch_and_branch_again,
        _drop_the_branch_and_branch_again,
        (RecordedQuantity.VESSEL_RICH, _ALVEOLAR),
        AgentAmountUnit.LITRES_OF_VAPOUR,
    ),
    _State(
        "halt after a Reset that no frame draws, with a mark added",
        _mark_and_reset_while_frames_fail,
        _reset_while_frames_fail,
        (RecordedQuantity.MUSCLE,),
        AgentAmountUnit.LITRES_OF_VAPOUR,
    ),
    _State(
        "one run drawn at 5 minutes after a dial change",
        _run_on_with_a_dial_moved,
        _draw,
        (_CIRCUIT, RecordedQuantity.VESSEL_RICH, RecordedQuantity.FAT),
        AgentAmountUnit.MILLILITRES_OF_LIQUID,
    ),
    _State(
        "an agent change asks whether to start a new case",
        _ask_for_desflurane,
        _ask_for_desflurane,
        (_ALVEOLAR,),
        AgentAmountUnit.MILLILITRES_OF_LIQUID,
    ),
    _State(
        "halt after an agent change that no frame draws",
        _start_desflurane_while_frames_fail,
        _reset_while_frames_fail,
        tuple(COMPARTMENT_QUANTITIES),
        AgentAmountUnit.LITRES_OF_VAPOUR,
    ),
    _State(
        "halt that keeps the last frame drawn",
        _run_on_then_fail,
        _draw_then_fail,
        (RecordedQuantity.MIXED_VENOUS, _CIRCUIT),
        AgentAmountUnit.MILLILITRES_OF_LIQUID,
    ),
)


def _choose(view: SimulationView, state: _State) -> None:
    """Give the dashboard the state's compartments and unit, as a reader's clicks would ask."""

    for quantity in COMPARTMENT_QUANTITIES:
        if quantity not in state.shown:
            view._handle_compartment_request(quantity, False)

    for quantity in state.shown:
        view._handle_compartment_request(quantity, True)

    view._handle_agent_cost_unit_request(state.unit)


def _show(view: SimulationView, state: _State, frames: _Frames, *, again: bool) -> None:
    (state.again if again else state.enter)(view, frames)
    _choose(view, state)
    view.present(False)
    _settle(QApplication.instance())


def _dashboard(application: QApplication, case: BranchedCase) -> SimulationView:
    view = SimulationView((case.trunk, *case.branches), case=case, workspaces=_EVERY_VIEW)
    view.resize(*_WALK_SIZE_PX)
    view.show()
    application.processEvents()
    view.present(False)
    _settle(application)

    return view


def _close(application: QApplication, view: SimulationView) -> None:
    view.stop_timers()
    view.close()
    view.deleteLater()
    _settle(application)


class _Recorder:
    """The last tick each kind of View was handed, kept under the name of the View's class."""

    def __init__(self) -> None:
        self.ticks: dict[str, ViewTick] = {}
        self._patch = pytest.MonkeyPatch()
        self._followed: set[int] = set()

    def follow(self, view: SimulationView) -> None:
        """Record each tick that the dashboard hands any of its Views from now on."""

        for shown in view.layout_container.views():
            if id(shown) in self._followed:
                continue

            self._followed.add(id(shown))
            draw = shown.refresh  # type: ignore[attr-defined]

            def record(
                tick: ViewTick,
                draw: Callable[[ViewTick], None] = draw,
                kind: str = type(shown).__name__,
            ) -> None:
                self.ticks[kind] = tick
                draw(tick)

            self._patch.setattr(shown, "refresh", record)

    def stop(self) -> None:
        self._patch.undo()


@dataclass(frozen=True)
class _Walk:
    """What the walk recorded at each state: the ticks each kind was handed, and both screens."""

    ticks: tuple[dict[str, ViewTick], ...]
    screens: tuple[tuple[list[tuple[str, str]], list[tuple[str, str]]], ...]


@pytest.fixture(scope="module")
def walk(application: QApplication) -> Iterator[_Walk]:
    """Show every state of `_STATES` in turn to one dashboard, and each again to a new one."""

    frames = _Frames()
    case = _branched_case()
    first = _dashboard(application, case)
    recorder = _Recorder()
    ticks: list[dict[str, ViewTick]] = []
    screens: list[tuple[list[tuple[str, str]], list[tuple[str, str]]]] = []

    try:
        for state in _STATES:
            recorder.follow(first)
            _show(first, state, frames, again=False)
            ticks.append(dict(recorder.ticks))
            seen = _screen(first.window())
            assert first.case is not None
            second = _dashboard(application, first.case)

            try:
                _show(second, state, frames, again=True)
                screens.append((seen, _screen(second.window())))
            finally:
                _close(application, second)
    finally:
        frames.fail(False)
        recorder.stop()
        _close(application, first)

    yield _Walk(tuple(ticks), tuple(screens))


#: The parameter that stands for the whole dashboard, beside each registered kind.
_WHOLE_DASHBOARD: Final = "the whole dashboard"

#: The size each View is shown at on its own, so that both instances lay it out alike.
_VIEW_SIZE_PX: Final = (700, 900)


def _differences(history: list[tuple[str, str]], fresh: list[tuple[str, str]]) -> str:
    """The entries that only one of two screens shows, each marked with the screen that shows it."""

    lines = difflib.unified_diff(
        [" | ".join(entry) for entry in history],
        [" | ".join(entry) for entry in fresh],
        "after the state before",
        "shown fresh",
        lineterm="",
        n=0,
    )

    return "\n".join(line for line in lines if not line.startswith("@@"))


def _drawn_alone(
    application: QApplication, entry: RegisteredView, ticks: Sequence[ViewTick]
) -> list[tuple[str, str]]:
    """What a new View of this kind shows after it is handed these ticks in turn.

    The View is shown inside a window of its own, as an Area holds it, so it
    is laid out at one size and deleted with that window.
    """

    window = QWidget()
    view = _built(entry)
    assert isinstance(view, View)
    view.setParent(window)

    try:
        window.resize(*_VIEW_SIZE_PX)
        view.resize(*_VIEW_SIZE_PX)
        window.show()
        application.processEvents()

        for tick in ticks:
            view.refresh(tick)
            _settle(application)

        return _screen(view)
    finally:
        window.deleteLater()
        _settle(application)


@pytest.mark.parametrize("kind", [*REGISTERED, _WHOLE_DASHBOARD])
def test_every_registered_view_draws_a_state_alike_whatever_it_drew_before(
    application: QApplication, walk: _Walk, kind: str
) -> None:
    """A View, and the dashboard, show a state the same whether or not they showed another first.

    Every widget, painted canvas and plot keeps what was last written to it.
    So a value from an earlier state stays on screen wherever the writing of
    a later state does not reach: a halt that leaves a panel unwritten
    (`PL-X7D5`, `PL-5JTH`), a painted amount kept after a start-over
    (`PL-0G2P`), a branch control left live (`PL-RF2S`). Each earlier test
    listed the widgets it checked, and each escape was a widget its list did
    not reach.

    This test lists nothing. `_STATES` is shown in turn to one dashboard, and
    each state is shown again to a new dashboard built over the runs as the
    first left them. For the whole dashboard, the two screens must read alike
    (`_screen`), so the second state of each pair in the walk is drawn the
    same after the first. For each registered kind, every tick that the walk
    handed that kind is handed to a new View after each other one, and to a
    View that was handed nothing before. The two must read alike for every
    ordered pair of states.

    The comparison reads what each widget says and what each plot draws
    rather than the pixels. Pixels compared across two instances differ
    where equal states are laid out unequally, as a panel stretched to the
    height that two runs once needed (the item, design point 6).
    """

    if kind == _WHOLE_DASHBOARD:
        for state, (history, fresh) in zip(_STATES, walk.screens, strict=True):
            assert history == fresh, (
                f"{state.name}: the dashboard shows this state differently after the state "
                f"before it than when it is shown fresh. Each entry below is a widget or a "
                f"plotted item, then what it shows:\n{_differences(history, fresh)}"
            )

        return

    entry = REGISTERED[kind]
    name = type(_built(entry)).__name__
    ticks = [state_ticks[name] for state_ticks in walk.ticks]

    for after, (state, tick) in enumerate(zip(_STATES, ticks, strict=True)):
        fresh = _drawn_alone(application, entry, (tick,))

        for before, earlier in enumerate(_STATES):
            if before == after:
                continue

            history = _drawn_alone(application, entry, (ticks[before], tick))
            assert history == fresh, (
                f"{kind}: '{state.name}' is drawn differently after '{earlier.name}' than when "
                f"it is drawn fresh. Each entry below is a widget or a plotted item, then what "
                f"it shows:\n{_differences(history, fresh)}"
            )


def _changed_fields(before: ViewTick, after: ViewTick) -> set[str]:
    """The fields of a tick, and of each value it carries, that differ between two ticks."""

    changed = {
        f"ViewTick.{field.name}"
        for field in fields(ViewTick)
        if getattr(before, field.name) != getattr(after, field.name)
    }
    # Runs are compared one by one, at the same place in each tick, as a View
    # draws them. A run that only one tick holds changes no field, so a
    # change in the number of runs alone does not count as a change.
    changed.update(
        f"RunPresentation.{field.name}"
        for field in fields(RunPresentation)
        for earlier, later in zip(before.runs, after.runs, strict=False)
        if getattr(earlier, field.name) != getattr(later, field.name)
    )
    changed.update(
        f"CasePresentation.{field.name}"
        for field in fields(CasePresentation)
        if getattr(before.case, field.name) != getattr(after.case, field.name)
    )

    if before.frame is not None and after.frame is not None:
        changed.update(
            f"ShownFrame.{field.name}"
            for field in fields(ShownFrame)
            if getattr(before.frame, field.name) != getattr(after.frame, field.name)
        )

    return changed


def test_each_field_of_a_view_tick_changes_between_two_states_of_the_walk(walk: _Walk) -> None:
    """Every field that a View is handed changes between two states that the walk shows in turn.

    The test above finds a value left from an earlier state only where that
    value changes from one state to the next. So every field of `ViewTick`,
    and of the run, case and frame values it carries, must differ between
    the ticks of two states shown one after the other. A field added later
    fails here until a state of `_STATES` changes it.
    """

    expected = {
        f"{value.__name__}.{field.name}"
        for value in (ViewTick, RunPresentation, CasePresentation, ShownFrame)
        for field in fields(value)
    }
    changed: set[str] = set()

    for before, after in itertools.pairwise(walk.ticks):
        for name in before.keys() & after.keys():
            changed |= _changed_fields(before[name], after[name])

    assert sorted(expected - changed) == [], (
        "no two states of the walk shown one after the other differ in these fields: add a "
        "state to _STATES that changes each one"
    )


def test_a_run_added_or_dropped_changes_no_field_of_the_runs_both_ticks_hold(walk: _Walk) -> None:
    """A field of a run counts as changed only where one run's value of it changed.

    Two ticks that differ only in how many runs they hold show the same
    values for the runs they share. So a change in the run count must not
    count every field of a run as changed. If it did, the test above could
    never fail for a field of `RunPresentation`, because the walk adds and
    drops a branch.
    """

    compared = next(tick for ticks in walk.ticks for tick in ticks.values() if len(tick.runs) > 1)
    trunk_only = replace(compared, runs=compared.runs[:1])

    assert (
        sorted(
            name
            for name in _changed_fields(compared, trunk_only)
            if name.startswith("RunPresentation.")
        )
        == []
    )


@dataclass
class _Stage:
    """A small window holding one label, one plotted curve and one legend swatch."""

    window: QWidget
    label: QLabel
    curve: pg.PlotCurveItem
    swatch: _LineSwatch


def _staged(application: QApplication) -> _Stage:
    window = QWidget()
    layout = QVBoxLayout(window)
    label = QLabel("1.2%")
    plot = pg.PlotWidget()
    curve = pg.PlotCurveItem(
        x=[0.0, 60.0, 120.0], y=[0.0, 1.0, 1.5], pen=pg.mkPen("#1f77b4", width=2)
    )
    plot.addItem(curve)
    # A fixed range, so that a change to a pen cannot move the range and be
    # found that way instead.
    plot.setRange(xRange=(0.0, 120.0), yRange=(0.0, 2.0), padding=0.0)
    plot.disableAutoRange()
    swatch = _LineSwatch(QPen(QColor("#1f77b4"), 2.0), 24, 12)

    for widget in (label, plot, swatch):
        layout.addWidget(widget)

    window.resize(400, 400)
    window.show()
    _settle(application)

    return _Stage(window, label, curve, swatch)


def _dashed(stage: _Stage) -> None:
    pen = QPen(QColor("#1f77b4"), 2.0)
    pen.setStyle(Qt.PenStyle.DashLine)
    stage.swatch.set_pen(pen)


#: One stale value of each kind that the walk must find, each written by changing one thing.
_STALE_VALUES: Final[dict[str, Callable[[_Stage], None]]] = {
    "a label's text": lambda stage: stage.label.setText("1.3%"),
    "a curve's point": lambda stage: stage.curve.setData(x=[0.0, 60.0, 120.0], y=[0.0, 1.0, 1.6]),
    "a curve's colour": lambda stage: stage.curve.setPen(pg.mkPen("#d62728", width=2)),
    "a curve's width": lambda stage: stage.curve.setPen(pg.mkPen("#1f77b4", width=1)),
    "a curve's dash": lambda stage: stage.curve.setPen(
        pg.mkPen("#1f77b4", width=2, style=Qt.PenStyle.DashLine)
    ),
    "a swatch's dash": _dashed,
    "a swatch left empty": lambda stage: stage.swatch.set_filled(False),
}


@pytest.mark.parametrize("change", sorted(_STALE_VALUES))
def test_the_walk_reads_a_stale_value_of_each_kind_as_a_difference(
    application: QApplication, change: str
) -> None:
    """The reading that the walk compares changes when one label, point or pen changes.

    The walk test passes whenever its two readings are equal, so it would
    also pass if the reading stopped seeing a kind of value. This test
    changes one value of each kind on a small window and requires the
    reading to change with it.
    """

    stage = _staged(application)

    try:
        before = _screen(stage.window)
        _STALE_VALUES[change](stage)
        _settle(application)
        after = _screen(stage.window)
    finally:
        stage.window.deleteLater()
        _settle(application)

    assert before != after, f"the walk's reading does not change when {change} changes"
