"""Integration tests for the run surfaces a reader may place in more than one Area.

`app/run_surfaces.py` holds two of a run's surfaces that sit in an Area: the
setting controls and the accounting panel (`PL-9LNF`). An Area can be split,
so a second Area can show the same surface of the same run. These tests build
a second copy of each through `RunView`'s own build methods, and check that
both copies draw the run. Each expected value is built from
`app/dashboard_frame.py` or `app/formatting.py` and the controller, never read
off a copy.

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
from anesthesia_sim.app.run_surfaces import AccountingPanel
from anesthesia_sim.app.simulation_view import SimulationView
from anesthesia_sim.app.view_registry import (
    AGENT_ACCOUNTING,
    CONCENTRATION_CHART,
    PARAMETER_CONTROLS,
    WASH_IN,
)
from anesthesia_sim.app.views import ConcentrationView
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


#: The dashboard the test shows, deleted before the next is shown and at the
#: end of the module, for the reason `test_simulation_view.py`'s
#: `_SHOWN_VIEWS` gives: a view left to the garbage collector is deleted
#: whenever a collection happens to run, which is a fatal error.
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
    """What one accounting panel shows: its heading, status, detail and amounts."""

    return (
        panel._accounting_heading_text.text(),
        panel._agent_accounting_status_text.text(),
        panel._agent_accounting_detail_text.text(),
        panel._agent_amounts_text.text(),
    )


def _expected(controller: SimulationController) -> tuple[str, str, str, str]:
    """What a lone run's accounting panel should show, from the controller's snapshot."""

    shown = accounting(controller.snapshot())

    return (ACCOUNTING_HEADING, shown.status.text, shown.detail, shown.amounts)


def test_two_accounting_panels_of_one_run_both_draw(application: QApplication) -> None:
    """A second accounting panel shows the run at once, and both follow the next frame.

    Before `PL-9LNF` the build method handed back the panel already placed,
    so a second Area holding it would have taken it out of the first.
    """

    controller = SimulationController()
    controller.start()
    _advance(controller, 300.0)
    view = _shown_view(application, controller)
    run = view.runs[0]
    first = run._accounting_panels[0]

    second = run.build_accounting_panel()

    assert second is not first, "the second call handed back the placed panel"
    assert _drawn(second) == _expected(controller)
    assert _drawn(first) == _expected(controller)

    _advance(controller, 300.0)
    view.present(False)

    assert _drawn(first) == _expected(controller)
    assert _drawn(second) == _expected(controller)


def test_a_drag_on_one_copy_of_the_setting_controls_moves_the_other(
    application: QApplication,
) -> None:
    """A slider moved in a second copy sets the run, and the first copy shows the new value."""

    controller = SimulationController()
    view = _shown_view(application, controller)
    run = view.runs[0]
    first = run._setting_controls[0]
    second = run.build_parameter_controls()

    assert second is not first
    assert len(run._setting_controls) == 2

    second._fresh_gas_flow_slider.slider.setValue(slider_position(7.0, FLOW_DISPLAY_DECIMALS))
    view.present(False)

    assert float(controller.snapshot().fresh_gas_flow_l_min) == pytest.approx(7.0)
    assert first._fresh_gas_flow_slider.value_label.text() == format_flow(7.0)
    assert second._fresh_gas_flow_slider.value_label.text() == format_flow(7.0)


def test_deleting_one_copy_leaves_the_other_drawing(application: QApplication) -> None:
    """A copy Qt has destroyed is dropped, so the next frame writes only the copies left."""

    controller = SimulationController()
    controller.start()
    _advance(controller, 300.0)
    view = _shown_view(application, controller)
    run = view.runs[0]
    second = run.build_accounting_panel()
    controls = run.build_parameter_controls()

    run._accounting_panels[0].deleteLater()
    controls.deleteLater()
    _settle(application)

    assert list(run._accounting_panels) == [second]
    assert len(run._setting_controls) == 1

    _advance(controller, 300.0)
    view.present(False)

    assert _drawn(second) == _expected(controller)


def test_each_chart_names_only_the_clipped_traces_its_own_window_shows(
    application: QApplication,
) -> None:
    """The off-scale line belongs to the chart and is written from its window (`PL-L59K`).

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
