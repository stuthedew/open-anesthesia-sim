"""The dashboard, driven headless against real runs.

These tests cover the page and its window.

`simulation_view_support.py` describes the whole suite.
"""

import pytest
from PySide6.QtCore import QPoint
from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QScrollArea, QSlider, QWidget

from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.app.simulation_view import SimulationView
from anesthesia_sim.app.theme import PARAMETER_SLIDER_LEAST_LENGTH
from anesthesia_sim.app.view_registry import (
    AGENT_ACCOUNTING,
    COMPARTMENT_SCHEMATIC,
    PARAMETER_CONTROLS,
    REGISTERED,
)
from anesthesia_sim.app.views import (
    AccountingView,
    ConcentrationView,
    ParameterControlsView,
    WashInView,
)
from anesthesia_sim.layout.tree import AreaId
from anesthesia_sim.layout.workspace import WorkspaceName
from tests.integration.simulation_view.simulation_view_support import (
    _SHOWN_VIEWS,
    _WINDOW_HEIGHT_PX,
    _WINDOW_WIDTH_PX,
    _accounting,
    _accounting_panel,
    _advance,
    _branched_case,
    _concentration,
    _delete_shown_views,
    _dials,
    _middle_of,
    _page_of,
    _record_panels,
    _settle,
    _shown_view,
    _take_fork,
    _wash_in,
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

    At the fixed test size, the Areas' least heights add up to more than the
    room between the region and the disclaimer. So the Areas are at their least
    height and the page scrolls by the difference. Since `PL-CBYS`, the page
    grows past its window only where the window is too small for those least
    heights, and a View taller than its Area scrolls inside the Area.

    Once the window is tall enough for the page to stop scrolling, every extra
    pixel of height makes the Areas taller, while the region that holds the
    readouts keeps its height. The test measures the readout section inside the
    region, where the section has been since `PL-NWTM`. The setting controls
    have been a View in an Area since `PL-2KXB`, so they take their share of
    the Areas' height.
    """

    controller = SimulationController()
    view = _shown_view(application, controller)
    chart_row = view.layout_container
    readout_section = view.unconditional_region
    scroll, _ = _middle_of(view)
    bar = scroll.verticalScrollBar()

    assert abs(readout_section.height() - readout_section.sizeHint().height()) <= 2
    assert chart_row.height() == chart_row.minimumSizeHint().height()

    settled_chart_row_height = chart_row.height()
    spare = 400
    hidden = bar.maximum()
    view.resize(_WINDOW_WIDTH_PX, view.height() + hidden + spare)
    application.processEvents()

    assert bar.maximum() == 0
    assert abs(readout_section.height() - readout_section.sizeHint().height()) <= 2
    assert chart_row.height() >= settled_chart_row_height + spare - 2

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
    taller once the event loop had run. At the test size the window is too
    small for the Areas' least heights, so since `PL-CBYS` the height they ask
    for is their own least height, not a height that the page worked out.
    """

    view = _shown_view(application, SimulationController())
    areas = view.layout_container

    assert areas.height() == areas.minimumSizeHint().height()
    application.processEvents()
    assert areas.height() == areas.minimumSizeHint().height()


_COMMON_SCREENS_PX = ((1366, 768), (1920, 1080))
"""A laptop screen and a desktop screen, the two sizes `PL-CBYS` measured."""


def _shipped_view_at(
    application: QApplication,
    workspace: str,
    width_px: int,
    height_px: int,
    *,
    branched: bool = False,
) -> SimulationView:
    """A dashboard over the shipped Workspaces, on `workspace`, at 300 s of one run.

    With `branched`, a branch is taken at 60 s in the Default Workspace,
    which shows the branch control, before the switch to `workspace`. The
    dashboard draws a frame again after the switch, as its render timer
    would, so the Views that the switch built show the runs.
    """

    from anesthesia_sim.layout.shipped import shipped_workspaces

    case = _branched_case()
    case.trunk.start()
    _advance(case.trunk, 300)
    _delete_shown_views(application)
    view = SimulationView((case.trunk,), case=case, workspaces=shipped_workspaces())
    _SHOWN_VIEWS.append(view)
    view.resize(width_px, height_px)
    view.show()
    application.processEvents()
    view.present(False)

    if branched:
        _take_fork(view, 60.0)
        _settle(application)
        assert len(view.runs) == 2

    view.tab_strip.activate(view.workspaces.position_of(WorkspaceName(workspace)))
    _settle(application)
    view.present(False)
    _settle(application)

    return view


def _shipped_workspace_names() -> tuple[str, ...]:
    from anesthesia_sim.layout.shipped import shipped_workspaces

    return tuple(str(workspace.name) for workspace in shipped_workspaces().workspaces)


@pytest.mark.parametrize(("width_px", "height_px"), _COMMON_SCREENS_PX)
@pytest.mark.parametrize("workspace", _shipped_workspace_names())
def test_no_shipped_workspace_scrolls_the_page(
    application: QApplication, workspace: str, width_px: int, height_px: int
) -> None:
    """`PL-CBYS`: on a laptop or a desktop screen, the Areas fit above the disclaimer.

    Before the change the page grew to hold every View's content. At 1366 by
    768 the Induction Workspace's page scrolled 832 px, and its wash-in chart
    opened below the fold. Now a View that needs more room than its Area
    scrolls inside the Area, so the page itself never scrolls at these sizes.
    No View scrolls sideways either, because an Area's least width comes from
    its View's content.
    """

    view = _shipped_view_at(application, workspace, width_px, height_px)
    page, _ = _middle_of(view)
    areas = view.layout_container

    assert page.verticalScrollBar().maximum() == 0
    assert page.horizontalScrollBar().maximum() == 0

    for area in areas.model.areas():
        frame = areas.frame(area.id)
        assert frame.view_scroll is not None, f"Area {area.id} ({area.view}) shows a notice"
        assert frame.content.isVisible(), f"Area {area.id} ({area.view}) hides its View"
        assert frame.view_scroll.horizontalScrollBar().maximum() == 0, (
            f"the {area.view} View scrolls sideways in its Area"
        )


def test_a_view_taller_than_its_area_scrolls_inside_the_area(application: QApplication) -> None:
    """`PL-CBYS`: the compartment schematic on a laptop is shown whole, by scrolling its own Area.

    In the Maintenance Workspace at 1366 by 768, with a branch open, the
    schematic shows one drawing for each run, and the two are taller than its
    Area. The View stays shown, with no notice in its place, and its Area's
    scroll bar covers the height the View does not get. The concentration plot
    is wholly on screen in its own Area. Until `PL-D5J4` the wash-in chart in
    Induction was the View that scrolled at this size with one run.
    """

    view = _shipped_view_at(application, "Maintenance", 1366, 768, branched=True)
    areas = view.layout_container
    (schematic,) = (area for area in areas.model.areas() if area.view == COMPARTMENT_SCHEMATIC)
    frame = areas.frame(schematic.id)
    scroll = frame.view_scroll

    assert scroll is not None
    assert frame.content.isVisible()
    bar = scroll.verticalScrollBar()
    assert bar.maximum() > 0
    assert bar.maximum() == frame.content.height() - scroll.viewport().height()

    chart = _concentration(view).chart
    around = [area for area in view.findChildren(QScrollArea) if area.isAncestorOf(chart)]
    assert len(around) == 2, "the plot is not in its Area's scroll and the page's"

    for area in around:
        top = chart.mapTo(area.viewport(), QPoint(0, 0)).y()
        assert 0 <= top, f"the plot's top is {-top} px above a scroll box"
        assert top + chart.height() <= area.viewport().height(), "the plot runs below a scroll box"


#: What each shipped Workspace must show whole at 1366 by 768 (`PL-D5J4`). The
#: wash-in curve is Induction's lesson. The share bar is Maintenance's
#: (`PL-PR1W`), with the lines under it that name each segment, so that no
#: segment is told apart by colour alone. The Edit bookmarks button opens the
#: bookmarks editor, in each Workspace that shows the bookmarks.
_LESSONS_WHOLE_AT_1366: dict[str, frozenset[str]] = {
    "Default": frozenset({"Edit bookmarks"}),
    "Induction": frozenset({"wash-in plot", "Edit bookmarks"}),
    "Maintenance": frozenset({"share bar", "share lines"}),
}


def _lesson_widgets(view: SimulationView) -> dict[str, QWidget]:
    """The shown wash-in plot, share bar, share lines and Edit bookmarks button, by name."""

    from anesthesia_sim.app.dashboard_frame import EDIT_BOOKMARKS_LABEL
    from anesthesia_sim.app.qt_schematic import RunSchematic

    found: dict[str, QWidget] = {}

    for wash_in in view.findChildren(WashInView):
        if wash_in.isVisible():
            found["wash-in plot"] = wash_in.chart

    for schematic in view.findChildren(RunSchematic):
        if schematic.isVisible():
            found["share bar"] = schematic.share_bar
            found["share lines"] = schematic.share_text

    for button in view.findChildren(QPushButton):
        if button.isVisible() and button.text() == EDIT_BOOKMARKS_LABEL:
            found["Edit bookmarks"] = button

    return found


@pytest.mark.parametrize("workspace", sorted(_LESSONS_WHOLE_AT_1366))
def test_each_shipped_workspace_shows_its_lesson_whole_at_1366_by_768(
    application: QApplication, workspace: str
) -> None:
    """`PL-D5J4`: a Workspace named for a task shows that task's View whole on a laptop screen.

    Before the fix, at 1366 by 768, Induction's wash-in curve started at its
    Area's lower edge, Maintenance's share bar and the lines under it were
    below the schematic's Area, and the Edit bookmarks button was cut by the
    Bookmarks Area's lower edge in all three Workspaces. Each widget must be
    shown, and wholly inside every scroll box around it, without the reader
    scrolling. The set of widgets each Workspace must show is written out, so
    a Workspace cannot pass by leaving its lesson out.
    """

    view = _shipped_view_at(application, workspace, 1366, 768)
    found = _lesson_widgets(view)

    assert set(found) == _LESSONS_WHOLE_AT_1366[workspace]

    for name, widget in found.items():
        assert _wholly_in_view(view, widget), f"the {name} is not wholly on screen in {workspace}"


@pytest.mark.parametrize(("width_px", "height_px"), _COMMON_SCREENS_PX)
@pytest.mark.parametrize("workspace", _shipped_workspace_names())
def test_the_parameters_area_is_not_far_taller_than_its_controls(
    application: QApplication, workspace: str, width_px: int, height_px: int
) -> None:
    """`PL-4JCC`: on a laptop or desktop screen, the Parameters Area holds its controls and no more.

    Before the fix, at 1920 by 1080, the Area below its header was 239 px tall
    in Default and Induction for about 90 px of controls, and that height was
    lost to the Views beside it. Below its header the Area is now no taller
    than the View's declared least height. The whole row of controls is inside
    it, with no scroll bar, because a row cut at the Area's edge reads as a
    row with no values.
    """

    view = _shipped_view_at(application, workspace, width_px, height_px)
    areas = view.layout_container
    (parameters,) = (area for area in areas.model.areas() if area.view == PARAMETER_CONTROLS)
    scroll = areas.frame(parameters.id).view_scroll

    assert scroll is not None
    assert scroll.height() <= REGISTERED[PARAMETER_CONTROLS].minimum.height_px
    assert scroll.verticalScrollBar().maximum() == 0


@pytest.mark.parametrize(("width_px", "height_px"), _COMMON_SCREENS_PX)
@pytest.mark.parametrize("workspace", _shipped_workspace_names())
def test_the_parameters_area_shows_both_runs_dials_once_a_branch_is_taken(
    application: QApplication, workspace: str, width_px: int, height_px: int
) -> None:
    """`PL-D5J4`: once a branch is taken, no run's row of dials scrolls out of the Parameters Area.

    The View shows one row of dials for each run. Before the fix, the Area
    kept the height of one row, so the second run's dials were hidden below
    its edge. A reader could then move the first run's dials while believing
    they were looking at the branch's. The Area now grows to hold every row,
    and the whole of the View is inside it.
    """

    view = _shipped_view_at(application, workspace, width_px, height_px, branched=True)
    areas = view.layout_container
    (parameters,) = (area for area in areas.model.areas() if area.view == PARAMETER_CONTROLS)
    scroll = areas.frame(parameters.id).view_scroll
    (controls,) = (shown for shown in view.findChildren(ParameterControlsView) if shown.isVisible())

    assert scroll is not None
    assert len(controls.findChildren(QSlider)) == 8
    assert scroll.verticalScrollBar().maximum() == 0


@pytest.mark.parametrize("workspace", _shipped_workspace_names())
def test_every_parameter_slider_is_long_enough_to_drag_at_1366_by_768(
    application: QApplication, workspace: str
) -> None:
    """`PL-V4Q8`: no setting slider is too short for a reader to drag to a chosen value.

    Before the fix, in Default and Induction at every window size, the four
    sliders were 52, 85, 54 and 43 px long, so a drag moved several steps for
    each pixel. The value now has a row of its own above the slider, and the
    slider has a least length, so every slider is at least that long and
    wholly on screen.
    """

    view = _shipped_view_at(application, workspace, 1366, 768)
    (controls,) = (shown for shown in view.findChildren(ParameterControlsView) if shown.isVisible())
    sliders = controls.findChildren(QSlider)

    assert len(sliders) == 4

    for slider in sliders:
        assert slider.width() >= PARAMETER_SLIDER_LEAST_LENGTH
        assert _wholly_in_view(view, slider)


@pytest.mark.parametrize("workspace", ("Default", "Induction"))
def test_a_chart_views_least_width_holds_every_row_above_its_plot(
    application: QApplication, workspace: str
) -> None:
    """`PL-CBYS`: no row above a chart's plot is cut off at the right in a narrow Area.

    The window statement, the reference values and the legend sit in a box
    that scrolls up and down and never sideways. An Area is never made
    narrower than its View's least width. So that width must hold the widest
    of those rows, with room for the box's scroll bar. Before the fix the box
    reported a least width of its own scroll bar alone. The concentration
    View's least width was then 357 px, and its MAC-awake line needs 410 px.
    In an Area dragged to its narrowest, that line lost the end of its band
    and its unit.
    """

    view = _shipped_view_at(application, workspace, 1366, 768)

    for chart_view in (*view.findChildren(ConcentrationView), *view.findChildren(WashInView)):
        if not chart_view.isVisible():
            continue

        (key,) = chart_view.findChildren(QScrollArea)
        rows = key.widget()
        assert rows is not None
        needed = rows.minimumSizeHint().width() + key.verticalScrollBar().sizeHint().width()

        assert key.minimumSizeHint().width() >= needed, type(chart_view).__name__
        assert chart_view.minimumSizeHint().width() >= needed, type(chart_view).__name__


def test_the_wash_in_view_never_scrolls_modelled_away_from_a_whole_plot(
    application: QApplication,
) -> None:
    """`PL-CBYS`: the line saying the plot is modelled never scrolls in the box above the plot.

    The safety standard requires those three words beside the plot
    (`PL-F9TQ`). The box above a chart's plot is squeezed before the plot is,
    so it can show its first two rows while the plot is whole. With the line
    as the box's third row, the Induction Workspace at 1366 by 948 to 1366 by
    1028 showed the whole wash-in plot with the line scrolled out of the box's
    view. It is now a row of its own under the heading, so wherever the View
    fits its Area, the line is on screen. Where the View is taller than its
    Area, as at 1366 by 768, the line and the plot cannot both be on screen;
    `PL-26BZ` holds that question.
    """

    view = _shipped_view_at(application, "Induction", 1366, 768)
    wash_in = _wash_in(view)
    line = _modelled_line(view)
    areas = view.layout_container
    (frame,) = (
        areas.frame(area.id)
        for area in areas.model.areas()
        if areas.frame(area.id).content is wash_in
    )
    inside = [box for box in frame.findChildren(QScrollArea) if box.isAncestorOf(line)]

    assert line.isVisible()
    assert inside == [], "the line is in a box that scrolls inside the Area"


@pytest.mark.parametrize(("width_px", "height_px"), _COMMON_SCREENS_PX)
@pytest.mark.parametrize("workspace", _shipped_workspace_names())
def test_the_wash_in_curve_is_never_on_screen_without_modelled(
    application: QApplication, workspace: str, width_px: int, height_px: int
) -> None:
    """`PL-26BZ`: wherever the wash-in plot is in view, the line saying it is modelled is too.

    The safety standard requires a predicted value to be told apart from a
    measurement on screen, and the F_A/F_I curve is a prediction
    (`PL-F9TQ`). In the Induction Workspace at 1366 by 768 the wash-in View is
    taller than its Area and scrolls inside it. Before the fix, the line sat
    under the heading, so a reader who scrolled down to the curve scrolled
    the line out of the Area. The test scrolls the View through its whole
    range, a few pixels at a time, and at each position checks the line
    wherever any part of the plot is in view.
    """

    view = _shipped_view_at(application, workspace, width_px, height_px)
    shown = [wash_in for wash_in in view.findChildren(WashInView) if wash_in.isVisible()]

    for wash_in in shown:
        line = _modelled_line(view)
        areas = view.layout_container
        (frame,) = (
            areas.frame(area.id)
            for area in areas.model.areas()
            if areas.frame(area.id).content is wash_in
        )
        assert frame.view_scroll is not None
        bar = frame.view_scroll.verticalScrollBar()

        for position in range(0, bar.maximum() + 1, 4):
            bar.setValue(position)
            application.processEvents()

            if not _partly_in_view(view, wash_in.chart):
                continue

            assert _wholly_in_view(view, line), (
                f"at scroll {position} of {bar.maximum()} the plot is in view and the line is not"
            )


def _modelled_line(view: SimulationView) -> QLabel:
    """The line that says the one shown wash-in View's values are modelled."""

    (wash_in,) = (wash_in for wash_in in view.findChildren(WashInView) if wash_in.isVisible())

    return wash_in.modelled_label


def _partly_in_view(view: SimulationView, widget: QWidget) -> bool:
    """Whether any of `widget` is inside the view of every scroll area around it."""

    for box in view.findChildren(QScrollArea):
        if not box.isAncestorOf(widget):
            continue

        top = widget.mapTo(box.viewport(), QPoint(0, 0)).y()

        if top + widget.height() <= 0 or top >= box.viewport().height():
            return False

    return True


def _wholly_in_view(view: SimulationView, widget: QWidget) -> bool:
    """Whether all of `widget` is inside the view of every scroll area around it."""

    for box in view.findChildren(QScrollArea):
        if not box.isAncestorOf(widget):
            continue

        top = widget.mapTo(box.viewport(), QPoint(0, 0)).y()

        if top < 0 or top + widget.height() > box.viewport().height():
            return False

    return widget.isVisible()


def test_a_view_kept_across_a_rebuild_keeps_its_scroll_position(application: QApplication) -> None:
    """`PL-CBYS`: splitting one Area does not scroll a View in another Area back to its top.

    Each rebuild of the layout gives every View a new frame and a new scroll
    box. In the Maintenance Workspace at 1366 by 768, with a branch open, the
    compartment schematic scrolls inside its Area. Before the fix, a reader who had
    scrolled such a View to the end found it back at the top after splitting a
    different Area, though the same View was kept. Before `PL-CBYS` the scroll
    sat inside the View and moved with it.
    """

    from anesthesia_sim.app.area_layout import SPLIT_SIDE_BY_SIDE_LABEL

    view = _shipped_view_at(application, "Maintenance", 1366, 768, branched=True)
    areas = view.layout_container
    (scrolled,) = (area for area in areas.model.areas() if area.view == COMPARTMENT_SCHEMATIC)
    kept = areas.frame(scrolled.id).content
    scroll = areas.frame(scrolled.id).view_scroll
    assert scroll is not None
    bar = scroll.verticalScrollBar()
    assert bar.maximum() > 0, "the schematic does not scroll at this size"
    bar.setValue(bar.maximum())
    scrolled_to = bar.value()
    other = next(
        area
        for area in areas.model.areas()
        if area.id != scrolled.id
        and any(
            operation.label == SPLIT_SIDE_BY_SIDE_LABEL and operation.available
            for operation in areas.operations(area.id)
        )
    )
    (split,) = (
        operation
        for operation in areas.operations(other.id)
        if operation.label == SPLIT_SIDE_BY_SIDE_LABEL
    )

    areas.perform(split)
    _settle(application)

    frame = areas.frame(scrolled.id)
    assert frame.content is kept
    assert frame.view_scroll is not None
    assert frame.view_scroll.verticalScrollBar().value() == scrolled_to


def test_the_page_scrolls_only_where_the_window_is_too_small_for_every_view(
    application: QApplication,
) -> None:
    """`PL-CBYS`: in a window too small for every View, the page grows and no Area loses its View.

    `docs/INTERFACE.md` § "Minimum displayed outputs" says that a reader who
    chooses a View sees the View itself, never only a notice that the Area is
    too small. So where the Areas' least heights add up to more than the
    window has, the page grows past the window and scrolls by the difference,
    and no Area swaps its View for the notice.
    """

    view = _shipped_view_at(application, "Induction", 1366, 500)
    page, middle = _middle_of(view)
    areas = view.layout_container

    assert page.verticalScrollBar().maximum() > 0
    assert areas.height() == areas.minimumSizeHint().height()
    assert page.verticalScrollBar().maximum() == middle.height() - page.viewport().height()

    for area in areas.model.areas():
        frame = areas.frame(area.id)
        assert frame.view_scroll is not None, f"Area {area.id} shows a notice"
        assert frame.content.isVisible(), f"Area {area.id} hides its View behind a notice"
