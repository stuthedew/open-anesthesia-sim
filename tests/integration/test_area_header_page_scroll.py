"""An Area's header and its View's pinned row stay in view wherever a page scroll leaves a value.

A window smaller than the dashboard scrolls the whole page, Areas and all. The
page can carry an Area's top past the window's edge while the lower part of
its View stays in view. The Area's header names the View, and the row the View
keeps above its scroll box states its units and that its values are modelled
(`PL-26BZ`). So a value seen without them could be read in the wrong unit or
taken for a measurement (`PL-DKQ5`). NUREG-0700 Rev. 3 (U.S. Nuclear
Regulatory Commission, 2020), guideline 1.5-15, p. 1-59, asks that general
labels "remain along the top (or bottom) and left (or right) edges of the
display" while it scrolls.

Each test puts every registered View in turn in an Area at the window's top,
beside or over the parameter controls, with a branch open. The controls need
their whole height and width, so the page scrolls. The test then scrolls the
page through every position. Where a value of any View is wholly in view and
clear of the Area's header, the header's View chooser and every line of the
View's pinned row are wholly in view too, above that value. What counts as in
view is worked out here from where each widget stands, not read from the code
that places the header. The tests render under the `offscreen` platform that
`tests/conftest.py` selects.
"""

from collections.abc import Callable, Iterator

import pytest
from PySide6.QtCore import QEvent, QPoint, QRect
from PySide6.QtWidgets import QAbstractButton, QApplication, QLabel, QScrollArea, QWidget

from anesthesia_sim.app.area_layout import AreaFrame
from anesthesia_sim.app.controller import BranchedCase, SimulationController
from anesthesia_sim.app.qt_schematic import RunSchematic
from anesthesia_sim.app.simulation_view import SimulationView
from anesthesia_sim.app.view_registry import (
    AGENT_ACCOUNTING,
    AGENT_COST,
    COMPARTMENT_SCHEMATIC,
    CONCENTRATION_CHART,
    PARAMETER_CONTROLS,
    REGISTERED,
    WASH_IN,
)
from anesthesia_sim.layout.model import LayoutModel
from anesthesia_sim.layout.tree import Area, AreaId, Orientation, Split, ViewKind, Window
from anesthesia_sim.layout.workspace import Origin, Workspace, WorkspaceName, WorkspaceSet

SECONDS_PER_MINUTE = 60

#: Every registered View, in the order the View chooser lists them.
_KINDS = tuple(entry.kind for entry in REGISTERED.values())

# The wide Views that stand beside the View under test in the sideways test.
_WIDE = (COMPARTMENT_SCHEMATIC, AGENT_COST, WASH_IN, CONCENTRATION_CHART)

# A window this short scrolls the page with every View at its top, because
# the parameter controls are held at their whole height with two runs open.
_SHORT_WINDOW_PX = (1400, 400)

# How far the page scrolls sideways at least, once the window has been made
# narrow enough.
_SIDEWAYS_SCROLL_PX = 120


@pytest.fixture(scope="module")
def application() -> Iterator[QApplication]:
    existing = QApplication.instance()

    yield existing if isinstance(existing, QApplication) else QApplication([])


@pytest.fixture
def shown(application: QApplication) -> Iterator[list[SimulationView]]:
    """The dashboards a test shows, closed and deleted when it ends."""

    views: list[SimulationView] = []

    yield views

    for view in views:
        view.stop_timers()
        view.close()
        view.deleteLater()

    application.sendPostedEvents(None, QEvent.Type.DeferredDelete)


@pytest.mark.parametrize("kind", _KINDS, ids=str)
def test_a_page_scrolled_down_keeps_each_area_s_header_and_pinned_row_over_its_values(
    application: QApplication, shown: list[SimulationView], kind: ViewKind
) -> None:
    """`PL-DKQ5`: no value is seen while the page has scrolled its Area's header or pinned row away.

    The View is in the top Area of a column, over the parameter controls, in
    a window 1400 by 400. Before the fix, the page carried the header and the
    pinned row above the window's edge with the View's lower part still in
    view: the schematic's tension lines, for one, past about 71 px of scroll.
    """

    view = _paused_dashboard(application, shown, _column_of(kind), _SHORT_WINDOW_PX)
    page = view._page_scroll
    bar = page.verticalScrollBar()
    top = view.layout_container.frame(AreaId(1))

    # The premise: the page scrolls far enough to carry the top Area's header
    # out of the window.
    bar.setValue(0)
    application.processEvents()
    assert bar.maximum() > top.mapTo(page.viewport(), QPoint(0, 0)).y() + top.header.height()

    seen_anywhere = False

    for position in range(bar.maximum() + 1):
        bar.setValue(position)
        application.processEvents()
        seen_anywhere |= _check_every_area(
            view, f"{kind} at page scroll {position}", _wholly_in_every_box
        )

    assert seen_anywhere, kind


@pytest.mark.parametrize("kind", _KINDS, ids=str)
def test_a_page_scrolled_sideways_starts_each_area_s_header_and_pinned_row_in_view(
    application: QApplication, shown: list[SimulationView], kind: ViewKind
) -> None:
    """`PL-DKQ5`: no value is seen while the page has scrolled its header or pinned row aside.

    The View is in the left Area of a row, beside three wide Views, in a
    window narrow enough that the page scrolls at least 120 px sideways. Each run's name, the
    general label of the run's heading in the compartment schematic, must
    start in view as well. Before the fix, a page scrolled to its right end
    hid the start of the View chooser's name and of the pinned row's lines,
    and of the run's name in the schematic.
    """

    view = _paused_dashboard(application, shown, _row_of(kind), _SHORT_WINDOW_PX)
    page = view._page_scroll
    across = page.horizontalScrollBar()
    down = page.verticalScrollBar()
    width = _SHORT_WINDOW_PX[0]
    view.resize(width, 1000)
    application.processEvents()

    while across.maximum() < _SIDEWAYS_SCROLL_PX and width > view.minimumSizeHint().width():
        width -= 10
        view.resize(width, 1000)
        application.processEvents()

    # The premise: the page scrolls sideways.
    assert across.maximum() >= _SIDEWAYS_SCROLL_PX, (width, across.maximum())

    seen_anywhere = False

    for vertical in sorted({0, down.maximum()}):
        down.setValue(vertical)

        for position in range(across.maximum() + 1):
            across.setValue(position)
            application.processEvents()
            seen_anywhere |= _check_every_area(
                view, f"{kind} at page scroll {position} across, {vertical} down", _starts_in_view
            )

    assert seen_anywhere, kind


def _check_every_area(
    view: SimulationView, where: str, in_view: Callable[[QScrollArea, QWidget], bool]
) -> bool:
    """Assert that every Area with a value seen has its header and pinned row in view above it.

    `in_view` says whether a line of the header or the pinned row counts as
    in view. Returns whether any value was seen, so a test can check that it
    checked something.
    """

    page = view._page_scroll
    areas = view.layout_container
    seen_anywhere = False

    for area in areas.model.areas():
        frame = areas.frame(area.id)

        if frame.view_scroll is None or frame.view_scroll.isHidden():
            continue

        chrome = _on_page(page, frame.chrome)
        seen = [
            value
            for value in _values(frame)
            if _wholly_in_every_box(page, value) and not _on_page(page, value).intersects(chrome)
        ]

        if not seen:
            continue

        seen_anywhere = True
        highest = min(_on_page(page, value).top() for value in seen)
        qualifiers: list[QLabel | QAbstractButton] = [frame.chooser, *_labels_in(frame.pinned_row)]

        if frame.pin_label.isVisible():
            qualifiers.append(frame.pin_label)

        for qualifier in qualifiers:
            text = qualifier.text()
            assert in_view(page, qualifier), f"{where}: {text!r} is not in view"
            assert _on_page(page, qualifier).bottom() < highest, f"{where}: {text!r} is below"

        for run in frame.content.findChildren(RunSchematic):
            if any(run.isAncestorOf(value) for value in seen):
                left = run.name_text.mapTo(page.viewport(), QPoint(0, 0)).x()
                assert left >= 0, f"{where}: {run.name_text.text()!r} starts {-left} px left"

    return seen_anywhere


def _values(frame: AreaFrame) -> list[QWidget]:
    """Return each widget of the frame's View that draws a value or a line, and holds no other.

    These are the View's labels, plots and canvases. A widget with children
    is left out, because its children are counted.
    """

    widgets = [frame.content, *frame.content.findChildren(QWidget)]

    return [
        widget
        for widget in widgets
        if widget.isVisible()
        and widget.width() > 0
        and widget.height() > 0
        and not any(child.isVisible() for child in widget.findChildren(QWidget))
    ]


def _labels_in(row: QWidget | None) -> list[QLabel]:
    """Return the visible labels of a View's pinned row, or none where the View has no row."""

    if row is None:
        return []

    return [label for label in row.findChildren(QLabel) if label.isVisible() and label.text()]


def _on_page(page: QScrollArea, widget: QWidget) -> QRect:
    """Return where `widget` stands, in the page viewport's pixels."""

    return QRect(widget.mapTo(page.viewport(), QPoint(0, 0)), widget.size())


def _wholly_in_every_box(page: QScrollArea, widget: QWidget) -> bool:
    """Return whether all of `widget` lies inside the viewport of every scroll box around it."""

    if not widget.isVisible():
        return False

    for box in [page, *page.findChildren(QScrollArea)]:
        if box.isAncestorOf(widget):
            viewport = box.viewport()
            placed = QRect(widget.mapTo(viewport, QPoint(0, 0)), widget.size())

            if not viewport.rect().contains(placed):
                return False

    return True


def _starts_in_view(page: QScrollArea, widget: QWidget) -> bool:
    """Return whether the left end of `widget`, at its whole height, is inside every box around it.

    A line that starts in view can be read from its start. Where the
    window's right edge cuts across an Area, a long line can still run past
    that edge (`PL-BQB6`).
    """

    if not widget.isVisible():
        return False

    for box in [page, *page.findChildren(QScrollArea)]:
        if box.isAncestorOf(widget):
            viewport = box.viewport()
            placed = QRect(widget.mapTo(viewport, QPoint(0, 0)), widget.size())
            start = QRect(placed.left(), placed.top(), 1, placed.height())

            if not viewport.rect().contains(start):
                return False

    return True


def _column_of(kind: ViewKind) -> WorkspaceSet:
    """Return one Workspace whose top Area shows `kind`, over the parameter controls.

    Where `kind` is the parameter controls, the lower Area shows the agent
    accounting instead.
    """

    other = AGENT_ACCOUNTING if kind == PARAMETER_CONTROLS else PARAMETER_CONTROLS

    return _workspace(Orientation.COLUMN, (kind, other))


def _row_of(kind: ViewKind) -> WorkspaceSet:
    """Return one Workspace whose left Area shows `kind`, beside three wide Views.

    The four Views' least widths add up to more than the window's least
    width, which the region above the page sets, so the page scrolls sideways.
    """

    others = [other for other in _WIDE if other != kind][:3]

    return _workspace(Orientation.ROW, (kind, *others))


def _workspace(orientation: Orientation, kinds: tuple[ViewKind, ...]) -> WorkspaceSet:
    """Return one Workspace of one Area for each of `kinds`, in order, sharing its room evenly."""

    areas = tuple(Area(AreaId(index + 1), kind) for index, kind in enumerate(kinds))
    tree = Split(orientation, tuple(1 / len(areas) for _ in areas), areas)

    return WorkspaceSet(
        (
            Workspace(
                WorkspaceName(f"{kinds[0]} first"),
                Origin.mine(),
                LayoutModel((Window(tree),), AreaId(len(areas) + 1)),
            ),
        ),
        0,
    )


def _paused_dashboard(
    application: QApplication,
    shown: list[SimulationView],
    workspaces: WorkspaceSet,
    size: tuple[int, int],
) -> SimulationView:
    """Return a dashboard at `size`, paused 10 minutes into a run, with a branch open.

    The branch opens at the run's last second. The page's scroll that a
    branch holds on the concentration chart is ended, so the test's own
    scrolls are the only ones.
    """

    controller = SimulationController()
    controller.start()

    while controller.snapshot().elapsed_s < 10 * SECONDS_PER_MINUTE:
        controller.advance()

    controller.pause()
    case = BranchedCase(controller)
    view = SimulationView((controller,), case=case, workspaces=workspaces)
    shown.append(view)
    view.resize(*size)
    view.show()
    application.processEvents()
    view.present(False)
    view._show_branch(case.fork_here())
    application.processEvents()
    view.present(False)
    view._release_chart_view()
    application.processEvents()

    return view
