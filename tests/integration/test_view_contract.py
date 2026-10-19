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
import json
from collections.abc import Iterator
from pathlib import Path
from typing import get_protocol_members

import pytest
from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QApplication, QWidget

from anesthesia_sim.app import area_layout
from anesthesia_sim.app.chart_time_base import FIT_RUN_KEY, time_base_for_span
from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.app.simulation_view import SimulationView
from anesthesia_sim.app.view_contract import (
    STATE_VERSION_KEY,
    UNREADABLE_STATE_TEXT,
    View,
    ViewContext,
    ViewRequests,
    unreadable_state_text,
)
from anesthesia_sim.app.view_registry import (
    CONCENTRATION_CHART,
    REGISTERED,
    WASH_IN,
    RegisteredView,
)
from anesthesia_sim.app.views import ConcentrationView, WashInView
from anesthesia_sim.layout.shipped import shipped_workspace
from anesthesia_sim.layout.tree import AreaId
from anesthesia_sim.layout.workspace import ShippedWorkspaceId

# The notice, written out here rather than read from the module that writes it.
_NOTICE = "This View's saved settings could not be read, so it shows its default settings."

_REQUESTS = ViewRequests(lambda: None, lambda _quantity, _shown: None)

_ENTRIES = list(REGISTERED.values())


@pytest.fixture(scope="module")
def application() -> Iterator[QApplication]:
    existing = QApplication.instance()

    yield existing if isinstance(existing, QApplication) else QApplication([])


@pytest.fixture
def dashboard(application: QApplication) -> Iterator[SimulationView]:
    view = SimulationView((SimulationController(),))
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

    assert members == {"refresh", "owes_a_frame", "frame_request", "save_state", "painted_strings"}
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


# ------------------------------------------------------------------ saved state


@pytest.mark.parametrize("entry", _ENTRIES, ids=[entry.kind for entry in _ENTRIES])
def test_a_view_reads_back_the_state_it_saved(
    application: QApplication, entry: RegisteredView
) -> None:
    """The state is JSON-shaped and carries its version, and the View built from it says nothing."""

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
    """`PL-TH35` Q4: defaults drawn without a word would be the stale-state failure."""

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
        None: max(view.chart.plot_width_px() for view in charts)
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
        assert again.frame_request().time_base == time_base_for_span(900.0)  # type: ignore[union-attr]
        assert again.time_base_selector.currentData() == "900.0"
        assert again.state_notice.isHidden()
    finally:
        first.deleteLater()
        again.deleteLater()


@pytest.mark.parametrize("kind", _CHARTS)
def test_a_chart_built_with_nothing_saved_fits_the_run(
    application: QApplication, kind: str
) -> None:
    view = _chart(kind)

    try:
        assert view.frame_request().time_base is None  # type: ignore[union-attr]
        assert view.save_state() == {STATE_VERSION_KEY: 2, "time_base_s": FIT_RUN_KEY}
        assert view.time_base_selector.currentData() == FIT_RUN_KEY
    finally:
        view.deleteLater()


@pytest.mark.parametrize("kind", _CHARTS)
def test_a_version_1_chart_state_reads_as_fit_run_without_a_notice(
    application: QApplication, kind: str
) -> None:
    """Version 1 held no setting, so nothing saved is lost and nothing is said."""

    view = _chart(kind, {STATE_VERSION_KEY: 1})

    try:
        assert view.frame_request().time_base is None  # type: ignore[union-attr]
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
        # A rung only fitting reaches, which the control cannot show.
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
        assert view.frame_request().time_base is None  # type: ignore[union-attr]
        assert not view.state_notice.isHidden()
        assert view.state_notice.text() == _NOTICE
    finally:
        view.deleteLater()


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
        assert view.frame_request().time_base == time_base_for_span(900.0)  # type: ignore[union-attr]
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
