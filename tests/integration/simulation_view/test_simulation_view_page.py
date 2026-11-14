"""The dashboard, driven headless against real runs.

These tests cover the page and its window.

`simulation_view_support.py` describes the whole suite.
"""

from PySide6.QtWidgets import QApplication, QWidget

from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.app.view_registry import AGENT_ACCOUNTING
from anesthesia_sim.app.views import AccountingView
from anesthesia_sim.layout.tree import AreaId
from tests.integration.simulation_view.simulation_view_support import (
    _WINDOW_HEIGHT_PX,
    _WINDOW_WIDTH_PX,
    _accounting,
    _accounting_panel,
    _concentration,
    _dials,
    _middle_of,
    _page_of,
    _record_panels,
    _settle,
    _shown_view,
)

# ---------------------------------------------------------------- the page


def test_the_dashboard_fits_its_window_without_a_horizontal_scrollbar(
    application: QApplication,
) -> None:
    """Nothing holds the page wider than the window: the sidebar and every slider are on screen.

    The readout row reports a one-column minimum and the legend rows wrap.
    So the page's minimum width is well inside the window, and the scroll
    area never widens it. The chart column alone asks for less than a
    thousand pixels.

    The record panels measured are the ones the page holds, as the test below
    proves. They used to come from a second build of the panels, and those
    panels had no parent. `mapTo(page, ...)` assumes that the page is an
    ancestor and checks nothing. So the last two assertions compared
    coordinates that were never on the page, and they could not fail
    (`PL-JS0X`).
    """

    controller = SimulationController()
    view = _shown_view(application, controller)
    scroll, middle = _middle_of(view)
    page = _page_of(view)

    assert middle.minimumSizeHint().width() <= scroll.viewport().width()
    assert middle.width() == scroll.viewport().width()
    assert scroll.horizontalScrollBar().maximum() == 0
    assert page.width() <= view.width()
    assert _concentration(view).minimumSizeHint().width() < 1000

    for slider in _dials(view.runs[0]).sliders:
        right_edge = slider.mapTo(page, slider.rect().bottomRight()).x()

        assert right_edge <= page.width(), "a setting control is laid beyond the page"

    for panel in _record_panels(view.runs[0]):
        assert page.isAncestorOf(panel), "a record panel measured is not on the page"
        assert panel.mapTo(page, panel.rect().bottomRight()).x() <= page.width()


def test_the_sidebar_panels_measured_are_the_ones_the_page_holds(application: QApplication) -> None:
    """Each panel the width test measures is the page's only panel of its kind, and is shown.

    Each panel is matched against the page's own children by the object name
    that scopes the panel's stylesheet. So a rebuilt panel fails here. So does
    a widget that might come to sit between the heading and the panel. The
    second build of the panels, which this check replaced, also moved the
    run's live labels out of the column that the earlier assertions had
    measured (`PL-JS0X`, `PL-N67T`).
    """

    view = _shown_view(application, SimulationController())
    page = _page_of(view)
    accounting, timeline = _record_panels(view.runs[0])

    for panel, name in ((accounting, "accountingPanel"), (timeline, "controlTimelinePanel")):
        assert page.findChildren(QWidget, name) == [panel], f"{name} is not the page's own"
        assert panel.isVisible(), f"{name} is not shown"


def test_a_second_build_of_the_record_panels_leaves_the_run_labels_on_screen(
    application: QApplication,
) -> None:
    """A second accounting View, or a second ask for the control-change panel, moves no label.

    The method that built both panels used to build two new panels on every
    call and lay the run's own labels into them. A layout takes a widget from
    wherever it sits. So a second call moved the accounting status, its
    amounts and the control changes into panels with no parent, and they
    vanished from the sidebar a learner was reading (`PL-N67T`). Each label
    must be on screen and in its shared column before the call as well as
    after it, so the test cannot pass on a column that never showed them. The
    overflow line is hidden while nothing overflows, so the test checks only
    that it is in its column. The accounting View builds the accounting panel,
    in the sidebar or any other Area that shows the View, so a second
    accounting View builds a panel of its own and leaves the first where it
    is (`PL-NWTM`, `PL-9LNF`, `PL-RF2S`). The control-change panel stays in
    the unconditional region's record column, so a second ask returns the
    placed one.
    """

    view = _shown_view(application, SimulationController())
    run = view.runs[0]
    sidebar = _accounting(view)
    records = view._record_column.parentWidget()
    placed = _record_panels(run)
    shown = (
        (_accounting_panel(run)._accounting_heading_text, sidebar),
        (_accounting_panel(run)._agent_accounting_status_text, sidebar),
        (_accounting_panel(run)._agent_accounting_detail_text, sidebar),
        (_accounting_panel(run)._agent_amounts_text, sidebar),
        (run._control_timeline_heading_text, records),
        (run._control_timeline_text, records),
    )

    assert sidebar is not None and records is not None

    for label, column in shown:
        assert label.isVisible(), "a run label is off screen before the second call"
        assert column is not None and column.isAncestorOf(label), (
            "a run label is outside its column to begin with"
        )

    again = run.build_control_record()
    view.layout_container.choose_view(AreaId(3), AGENT_ACCOUNTING)
    _settle(application)
    (second,) = (
        panel
        for chosen in view.layout_container.views()
        if isinstance(chosen, AccountingView) and chosen is not sidebar
        for panel in chosen.panels
    )

    for label, column in shown:
        assert label.isVisible(), "a second call took a run label off screen"
        assert column is not None and column.isAncestorOf(label), (
            "a second call moved a run label out of its column"
        )

    assert records.isAncestorOf(run._control_timeline_overflow_text)
    assert second is not placed[0], "the second View took the placed accounting panel"
    assert again is placed[1], "a second call built a new control-change panel"


def test_a_second_build_call_leaves_each_run_widget_on_screen(application: QApplication) -> None:
    """Asking a run again for its transport row or readouts hands back the placed one.

    Each of the three methods used to lay the run's live widgets into a new
    container on every call. So a second call took the Start button, the
    substance heading and the fresh gas flow slider off screen, and dropping
    its result deleted them (`PL-KZR1`). The check works like the sidebar's
    test above (`PL-N67T`). Every widget must be on the page before the call
    as well as after it, and each shown widget must stay shown, so the test
    cannot pass on a row that never showed them. Each case names a widget
    that has to be shown to begin with. The lone run's name and the agent
    chip are hidden in this state, so the test checks only that they are on
    the page. The setting controls are not among the cases, because the
    setting controls View builds them, and a second View builds its own for
    another Area (`tests/integration/test_run_surfaces.py`).
    """

    view = _shown_view(application, SimulationController())
    run = view.runs[0]
    page = _page_of(view)
    transport = (
        run._run_name_text,
        run._agent_dropdown,
        run._running_agent_display,
        run._start_button,
        run._pause_button,
        run._reset_button,
        run._playback_rate_dropdown,
        run._status_text,
    )
    readouts = (run._compartment_substance_text, run._interpretation_text, run._readout_row)
    cases = (
        ("transport row", run.build_transport_row, run._start_button, transport),
        ("readout section", run.build_readout_section, run._compartment_substance_text, readouts),
    )

    for name, build, witness, widgets in cases:
        placed = widgets[-1].parentWidget()
        shown = tuple(widget for widget in widgets if widget.isVisible())

        assert witness in shown, f"the {name} is off screen before the second call"
        assert all(page.isAncestorOf(widget) for widget in widgets), f"the {name} is off the page"

        again = build()
        _settle(application)

        assert all(widget.isVisible() for widget in shown), f"a second call hid the {name}"
        assert all(page.isAncestorOf(widget) for widget in widgets), f"the {name} left the page"
        assert again is placed, f"a second call built a new {name}"


def test_spare_height_goes_to_the_plots_and_not_to_the_readouts(application: QApplication) -> None:
    """The unconditional region keeps its own height, and the Areas take the rest.

    At the fixed test size, the page is taller than the window, so there is no
    spare height. From the first frame on, the Areas then have the height they
    ask for, which is their size hint. Before `PL-PHPZ`, the page laid out the
    Areas from a hint read before the Views had drawn. So the Areas' height
    depended on when the page was laid out.

    A window has spare height once it is tall enough for the scrolling middle to
    show all of its content. Every extra pixel of height makes the Areas taller,
    while the region that holds the readouts keeps its height. The test measures
    the readout section inside the region, where the section has been since
    `PL-NWTM`. The setting controls have been a View in an Area since `PL-2KXB`,
    so they take their share of the Areas' height.
    """

    controller = SimulationController()
    view = _shown_view(application, controller)
    chart_row = view.layout_container
    readout_section = view.unconditional_region
    scroll, middle = _middle_of(view)

    assert abs(readout_section.height() - readout_section.sizeHint().height()) <= 2
    assert chart_row.height() >= chart_row.minimumSizeHint().height()
    assert chart_row.height() == chart_row.sizeHint().height()

    settled_chart_row_height = chart_row.height()
    spare = 400
    hidden = max(0, middle.sizeHint().height() - scroll.viewport().height())
    view.resize(_WINDOW_WIDTH_PX, view.height() + hidden + spare)
    application.processEvents()

    assert abs(readout_section.height() - readout_section.sizeHint().height()) <= 2
    assert chart_row.height() >= settled_chart_row_height + spare - 2
    assert chart_row.height() > chart_row.sizeHint().height()

    view.resize(_WINDOW_WIDTH_PX, _WINDOW_HEIGHT_PX)
    application.processEvents()


def test_the_page_takes_the_height_the_areas_ask_for_after_the_views_draw(
    application: QApplication,
) -> None:
    """The Areas are as tall as their size hint straight after the first frame (`PL-PHPZ`).

    The setting controls sit in an Area above the charts. They build each
    run's dials on their first frame, which changes the Areas' size hint.
    Before the fix, the page kept the hint that it read before that frame. So
    after the frame the Areas were 62 px shorter than their hint, and 45 px
    taller once the event loop had run. The expected height is the Areas' own
    size hint, not a height that the page worked out.
    """

    view = _shown_view(application, SimulationController())
    areas = view.layout_container

    assert areas.height() == areas.sizeHint().height()
    application.processEvents()
    assert areas.height() == areas.sizeHint().height()
