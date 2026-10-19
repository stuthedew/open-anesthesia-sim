"""The View contract, checked against every View this build registers (`PL-TH35`).

`app/view_contract.py` states the contract and its pruning rule: every member
of `View` has a call site in the adapter, and every registered kind builds a
View that satisfies the contract. These tests enforce that rule. They also
check what each shipped View owes a reader: saved state it can read, and a
notice where it cannot. In a real dashboard, they check that every View is
drawn from one shared frame. They render under the `offscreen` platform that
`tests/conftest.py` selects.
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
    AGENT_ACCOUNTING,
    CONCENTRATION_CHART,
    PARAMETER_CONTROLS,
    REGISTERED,
    WASH_IN,
    RegisteredView,
)
from anesthesia_sim.app.views import ConcentrationView
from anesthesia_sim.layout.model import LayoutModel
from anesthesia_sim.layout.tree import Area, AreaId, Orientation, Split, Window
from anesthesia_sim.layout.workspace import Origin, Workspace, WorkspaceName, WorkspaceSet

#: One Workspace that holds every View this build registers. Each test then
#: finds the View it reads, whichever Workspace is shipped first. The
#: parameter controls run across the top. Under them, the concentration chart
#: sits over the F_A/F_I plot, beside the accounting. That was the dashboard's
#: layout before it began opening on the shipped Workspaces (`PL-2KXB`).
_EVERY_VIEW = WorkspaceSet(
    (
        Workspace(
            WorkspaceName("Every View"),
            Origin.mine(),
            LayoutModel(
                (
                    Window(
                        Split(
                            Orientation.COLUMN,
                            (0.25, 0.75),
                            (
                                Area(AreaId(4), PARAMETER_CONTROLS),
                                Split(
                                    Orientation.ROW,
                                    (0.82, 0.18),
                                    (
                                        Split(
                                            Orientation.COLUMN,
                                            (0.55, 0.45),
                                            (
                                                Area(AreaId(1), CONCENTRATION_CHART),
                                                Area(AreaId(3), WASH_IN),
                                            ),
                                        ),
                                        Area(AreaId(2), AGENT_ACCOUNTING),
                                    ),
                                ),
                            ),
                        )
                    ),
                ),
                AreaId(5),
            ),
        ),
    ),
    0,
)

# The notice, written out here rather than read from the module that writes it.
_NOTICE = "This View's saved settings could not be read, so it shows its default settings."

_REQUESTS = ViewRequests(lambda _time_base: None, lambda _quantity, _shown: None)

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

    assert members == {"refresh", "owes_a_frame", "frame_width_px", "save_state", "painted_strings"}
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
    """`PL-TH35` Q3 and Q8: one View per Area, and one frame for every plot (`PL-9LNF`)."""

    dashboard.layout_container.choose_view(AreaId(3), CONCENTRATION_CHART)
    dashboard.present(False)
    charts = [
        view for view in dashboard.layout_container.views() if isinstance(view, ConcentrationView)
    ]

    assert len(charts) == 2
    assert charts[0] is not charts[1]
    assert charts[0].chart.frame is not None
    assert charts[0].chart.frame is charts[1].chart.frame
    assert dashboard.layout_container.frame_width_px() == max(
        view.chart.plot_width_px() for view in charts
    )
