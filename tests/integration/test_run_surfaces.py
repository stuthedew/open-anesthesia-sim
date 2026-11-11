"""Integration tests for one run's panels shown in more than one Area.

`app/run_surfaces.py` holds two of the widgets that draw one run's values in
an Area: the setting controls and the accounting panel (`PL-9LNF`). An Area
can be split, so a second Area can show the same View of the same run. Each
View builds its own widget for the run and writes it from the run's
presentation on every tick (`PL-RF2S`). These tests choose the same View for
a second Area, and check that both draw the run. Each expected value is built
from `app/dashboard_frame.py` or `app/formatting.py` and the controller, never
read off a panel.

The lines that depend on a chart's window belong to each chart (`PL-L59K`).
The last test checks that two charts at different windows each show their own
lines.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QApplication

from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.app.dashboard_frame import (
    ACCOUNTING_HEADING,
    SIMULATION_STEP_S,
    accounting,
    slider_position,
)
from anesthesia_sim.app.formatting import FLOW_DISPLAY_DECIMALS, format_flow
from anesthesia_sim.app.run_surfaces import AccountingPanel, ParameterControls
from anesthesia_sim.app.simulation_view import SimulationView
from anesthesia_sim.app.view_registry import (
    AGENT_ACCOUNTING,
    CONCENTRATION_CHART,
    PARAMETER_CONTROLS,
    WASH_IN,
)
from anesthesia_sim.app.views import AccountingView, ConcentrationView, ParameterControlsView
from anesthesia_sim.core.concentration import Percent
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

_WINDOW_WIDTH_PX = 1400
_WINDOW_HEIGHT_PX = 1000


@pytest.fixture(scope="module")
def application() -> Iterator[QApplication]:
    existing = QApplication.instance()

    yield existing if isinstance(existing, QApplication) else QApplication([])


#: The dashboard that the current test shows. It is deleted before the next one
#: is shown, and at the end of the module. `_SHOWN_VIEWS` in
#: `test_simulation_view.py` gives the reason: a view left to the garbage
#: collector is deleted whenever a collection happens to run, which is a fatal
#: error.
_SHOWN_VIEWS: list[SimulationView] = []


def _settle(application: QApplication) -> None:
    application.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    application.processEvents()


def _delete_shown_views(application: QApplication) -> None:
    for view in _SHOWN_VIEWS:
        view.stop_timers()
        view.close()
        view.deleteLater()

    _SHOWN_VIEWS.clear()
    _settle(application)


@pytest.fixture(scope="module", autouse=True)
def _torn_down_views(application: QApplication) -> Iterator[None]:
    yield

    _delete_shown_views(application)


def _shown_view(application: QApplication, controller: SimulationController) -> SimulationView:
    _delete_shown_views(application)
    view = SimulationView((controller,), workspaces=_EVERY_VIEW)
    _SHOWN_VIEWS.append(view)
    view.resize(_WINDOW_WIDTH_PX, _WINDOW_HEIGHT_PX)
    view.show()
    application.processEvents()
    view.present(False)

    return view


def _advance(controller: SimulationController, seconds: float) -> None:
    for _ in range(round(seconds / SIMULATION_STEP_S)):
        controller.advance(SIMULATION_STEP_S)


def _drawn(panel: AccountingPanel) -> tuple[str, str, str, str]:
    """Return what one accounting panel shows: its heading, status, detail and amounts."""

    return (
        panel._accounting_heading_text.text(),
        panel._agent_accounting_status_text.text(),
        panel._agent_accounting_detail_text.text(),
        panel._agent_amounts_text.text(),
    )


def _expected(controller: SimulationController) -> tuple[str, str, str, str]:
    """Return what a lone run's accounting panel should show, from the controller's snapshot."""

    shown = accounting(controller.snapshot())

    return (ACCOUNTING_HEADING, shown.status.text, shown.detail, shown.amounts)


def _accounting_panels(view: SimulationView) -> list[AccountingPanel]:
    """The first run's accounting panel in each Area that shows the accounting View."""

    return [
        shown.panels[0]
        for shown in view.layout_container.views()
        if isinstance(shown, AccountingView)
    ]


def _dials(view: SimulationView) -> list[ParameterControls]:
    """The first run's four dials in each Area that shows the setting controls View."""

    rows = [
        shown.rows[0]
        for shown in view.layout_container.views()
        if isinstance(shown, ParameterControlsView)
    ]

    return [row.controls for row in rows if row.controls is not None]


def test_two_accounting_views_of_one_run_both_draw(application: QApplication) -> None:
    """A second accounting View shows the run at once, and both update on the next frame.

    Before `PL-9LNF`, the run held one accounting panel. A second Area that
    held that panel would have taken it out of the first Area.
    """

    controller = SimulationController()
    controller.start()
    _advance(controller, 300.0)
    view = _shown_view(application, controller)

    view.layout_container.choose_view(AreaId(3), AGENT_ACCOUNTING)
    _settle(application)
    first, second = _accounting_panels(view)

    assert second is not first
    assert _drawn(second) == _expected(controller)
    assert _drawn(first) == _expected(controller)

    _advance(controller, 300.0)
    view.present(False)

    assert _drawn(first) == _expected(controller)
    assert _drawn(second) == _expected(controller)


def test_a_dial_moved_in_one_view_sets_the_run_and_moves_the_dial_in_the_other(
    application: QApplication,
) -> None:
    """A slider moved in a second setting controls View sets the run, and both Views show it.

    The second View asks the dashboard for the change and names the run. The
    run applies it and rewrites its own readouts at once, and the dashboard
    hands every View the runs at once too, with no frame. So the first View's
    dial shows the new value before the render tick draws the frame
    (`PL-RF2S`). The frame that follows leaves both dials on that value.
    """

    controller = SimulationController()
    view = _shown_view(application, controller)
    view.layout_container.choose_view(AreaId(3), PARAMETER_CONTROLS)
    _settle(application)
    first, second = _dials(view)
    frames = view.presented_frames

    assert second is not first

    second._fresh_gas_flow_slider.slider.setValue(slider_position(7.0, FLOW_DISPLAY_DECIMALS))

    assert view.presented_frames == frames, "the change drew a frame at once"
    assert float(controller.snapshot().fresh_gas_flow_l_min) == pytest.approx(7.0)
    assert first._fresh_gas_flow_slider.value_label.text() == format_flow(7.0)
    assert second._fresh_gas_flow_slider.value_label.text() == format_flow(7.0)

    view.present(False)

    assert first._fresh_gas_flow_slider.value_label.text() == format_flow(7.0)
    assert second._fresh_gas_flow_slider.value_label.text() == format_flow(7.0)


def test_replacing_one_of_two_views_leaves_the_other_drawing(application: QApplication) -> None:
    """A View that a reader replaces takes its panels with it, and the other goes on drawing."""

    controller = SimulationController()
    controller.start()
    _advance(controller, 300.0)
    view = _shown_view(application, controller)
    view.layout_container.choose_view(AreaId(3), AGENT_ACCOUNTING)
    _settle(application)
    # Area 3 comes before the sidebar's Area in reading order.
    _, kept = _accounting_panels(view)

    view.layout_container.choose_view(AreaId(3), WASH_IN)
    _settle(application)

    assert _accounting_panels(view) == [kept]

    _advance(controller, 300.0)
    view.present(False)

    assert _drawn(kept) == _expected(controller)


def test_each_chart_names_only_the_clipped_traces_its_own_window_shows(
    application: QApplication,
) -> None:
    """Each chart owns its off-scale line, and writes it from its own window (`PL-L59K`).

    A sevoflurane dial setting of 8% is 4 MAC, and the plot's ceiling is
    3 MAC. So ten minutes at 8% carries the circuit trace above the plot.
    Twenty-five minutes at 0% then bring every trace back below the ceiling.
    A chart that fits the run still draws the excursion and says so. A
    15-minute chart has moved past the excursion, and a notice there would
    name a clipped trace that the chart does not draw.
    """

    controller = SimulationController()
    controller.start()
    controller.set_delivered_concentration_percent(Percent(8.0))
    _advance(controller, 600.0)
    controller.set_delivered_concentration_percent(Percent(0.0))
    _advance(controller, 1500.0)
    view = _shown_view(application, controller)
    view.layout_container.choose_view(AreaId(3), CONCENTRATION_CHART)
    charts = [
        chart for chart in view.layout_container.views() if isinstance(chart, ConcentrationView)
    ]
    selector = charts[1].time_base_selector
    selector.setCurrentIndex(selector.findData("900.0"))
    fitted, zoomed = charts[0].off_scale.lines, charts[1].off_scale.lines

    assert charts[1].chart.frame is not None
    assert charts[1].chart.frame.start_s > 600.0, "the 15-minute window still shows the dial at 8%"
    assert len(fitted) == len(zoomed) == 1
    assert fitted[0].isHidden() is False
    assert "Circuit" in fitted[0].text()
    assert zoomed[0].isHidden() is True
