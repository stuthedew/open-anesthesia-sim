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
from PySide6.QtCore import QEvent, QPoint, QRect, Qt
from PySide6.QtGui import QImage, QKeyEvent
from PySide6.QtWidgets import QAbstractButton, QApplication, QLabel, QScrollArea, QWidget

from anesthesia_sim.app.area_layout import AreaFrame
from anesthesia_sim.app.controller import BranchedCase, SimulationController
from anesthesia_sim.app.qt_schematic import RunSchematic
from anesthesia_sim.app.simulation_view import SimulationView
from anesthesia_sim.app.theme import VIEW_HEADING_SPACING
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

# Beside the parameter controls, a window this tall leaves the page's view
# taller than the schematic's header and pinned row, so its values can show
# below them, and the page still scrolls down.
_BESIDE_WINDOW_PX = (1400, 500)

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
@pytest.mark.parametrize("arranged", ["over", "beside"])
def test_a_page_scrolled_down_keeps_each_area_s_header_and_pinned_row_over_its_values(
    application: QApplication, shown: list[SimulationView], kind: ViewKind, arranged: str
) -> None:
    """`PL-DKQ5`: no value is seen while the page has scrolled its Area's header or pinned row away.

    The View is in the first Area, over the parameter controls in a window
    1400 by 400, or beside them in a window 1400 by 500. Over them, the
    schematic's Area is too short to draw, so the schematic is checked beside
    them, where its Area is as tall as theirs. Halfway down, the header
    starts to show a pinned run's name. Before the fix, the page carried the
    header and the pinned row above the window's edge with the View's lower
    part still in view: the wash-in plot without its line saying it is
    modelled, for one.
    """

    layout, size = (
        (_column_of(kind), _SHORT_WINDOW_PX)
        if arranged == "over"
        else (_beside(kind), _BESIDE_WINDOW_PX)
    )
    view = _paused_dashboard(application, shown, layout, size)
    page = view._page_scroll
    bar = page.verticalScrollBar()
    top = view.layout_container.frame(AreaId(1))

    # The premise: the page scrolls far enough to carry the top Area's header
    # out of the window.
    bar.setValue(0)
    application.processEvents()
    assert bar.maximum() > top.mapTo(page.viewport(), QPoint(0, 0)).y() + top.header.height()

    seen: set[AreaId] = set()
    painted: set[AreaId] = set()

    for position in range(bar.maximum() + 1):
        bar.setValue(position)

        if position == bar.maximum() // 2:
            top.show_pin("Run 1", absent=False)

        application.processEvents()
        where = f"{kind} {arranged} at page scroll {position}"
        seen |= _check_every_area(view, where, _wholly_in_every_box)
        painted |= _check_chrome_drawn_over_its_view(view, where)

    # The View's own Area was checked, not only the Area beside it, and so
    # was the surface of a header standing over its View. Only an Area too
    # short for its View, which shows a notice instead, is left out.
    drawn = top.view_scroll is not None and not top.view_scroll.isHidden()
    assert drawn or arranged == "over", (kind, arranged)

    if drawn:
        assert AreaId(1) in seen, (kind, arranged, seen)
        assert AreaId(1) in painted, (kind, arranged, painted)


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

    seen: set[AreaId] = set()

    for vertical in sorted({0, down.maximum()}):
        down.setValue(vertical)

        for position in range(across.maximum() + 1):
            across.setValue(position)
            application.processEvents()
            seen |= _check_every_area(
                view, f"{kind} at page scroll {position} across, {vertical} down", _starts_in_view
            )

    assert AreaId(1) in seen, (kind, seen)


@pytest.mark.parametrize("kind", _KINDS, ids=str)
def test_shift_tab_up_a_scrolled_page_never_leaves_the_focus_under_an_area_s_header(
    application: QApplication, shown: list[SimulationView], kind: ViewKind
) -> None:
    """`PL-DKQ5`: a control given the focus by the keyboard stands clear of its Area's header.

    The View is in the top Area of a column over the parameter controls, in
    a window 1400 by 400, and the page is scrolled to its foot. The focus
    then moves back through every control with Shift+Tab. Each control that
    takes it in an Area must be in view, and its part in view clear of the
    header and pinned row that stand over the top of the Area's part in view. Qt's own
    scroll box stops 50 px inside its edge, which a header and a pinned row
    of two lines are taller than.
    """

    view = _paused_dashboard(application, shown, _column_of(kind), _SHORT_WINDOW_PX)
    page = view._page_scroll
    page.verticalScrollBar().setValue(page.verticalScrollBar().maximum())
    application.processEvents()
    areas = view.layout_container
    frames = [areas.frame(area.id) for area in areas.model.areas()]
    focusable = [
        widget
        for frame in frames
        for widget in frame.body.findChildren(QWidget)
        if widget.focusPolicy() & Qt.FocusPolicy.TabFocus and widget.isVisible()
    ]
    assert focusable, kind
    # The window must be the active one for a widget in it to hold the focus.
    view.activateWindow()
    focusable[-1].setFocus(Qt.FocusReason.TabFocusReason)
    application.processEvents()
    assert application.focusWidget() is focusable[-1], "the window did not take the focus"
    checked = 0

    for _ in range(3 * len(focusable)):
        # Sent straight to the focused widget, as Qt's own key handling would.
        # `QTest.keyClick` needs a native window, which a window kept off a
        # Mac runner's screen does not have.
        press = QKeyEvent(
            QEvent.Type.KeyPress, Qt.Key.Key_Backtab, Qt.KeyboardModifier.ShiftModifier
        )
        QApplication.sendEvent(application.focusWidget(), press)
        application.processEvents()
        focused = application.focusWidget()
        assert focused is not None, f"{kind}: Shift+Tab left no widget with the focus"
        holder = next((frame for frame in frames if frame.body.isAncestorOf(focused)), None)

        if holder is None or holder.chrome.isAncestorOf(focused):
            continue

        checked += 1
        label = focused.text() if isinstance(focused, QAbstractButton) else ""
        name = f"{kind}: {type(focused).__name__} {focused.accessibleName() or label!r}"
        shown = _part_on_page(page, focused)
        assert not shown.isEmpty(), f"{name} is not in view"
        assert not shown.intersects(_on_page(page, holder.chrome)), (
            f"{name} is under its Area's header"
        )

    assert checked, kind


def _check_every_area(
    view: SimulationView, where: str, in_view: Callable[[QScrollArea, QWidget], bool]
) -> set[AreaId]:
    """Assert that every Area with a value seen has its header and pinned row in view above it.

    `in_view` says whether a line of the header or the pinned row counts as
    in view. Returns each Area in which a value was seen, so a test can check
    that it checked the Area it is about.
    """

    page = view._page_scroll
    areas = view.layout_container
    seen_in: set[AreaId] = set()

    for area in areas.model.areas():
        frame = areas.frame(area.id)

        if frame.view_scroll is None or frame.view_scroll.isHidden():
            continue

        chrome = _on_page(page, frame.chrome)
        # A value counts as seen wherever its whole width and any part of its
        # height are in view below the header, so a canvas taller than the
        # window counts as well. A value cut at the window's right edge is
        # `PL-BQB6`'s.
        seen = [value for value in _values(frame) if not _below(page, value, chrome).isEmpty()]

        if not seen:
            continue

        seen_in.add(area.id)
        highest = min(_below(page, value, chrome).top() for value in seen)
        qualifiers: list[QLabel | QAbstractButton] = [frame.chooser, *_labels_in(frame.pinned_row)]

        if frame.pin_label.isVisible():
            qualifiers.append(frame.pin_label)

        for qualifier in qualifiers:
            text = qualifier.text()
            assert in_view(page, qualifier), f"{where}: {text!r} is not in view"
            assert _on_page(page, qualifier).bottom() < highest, f"{where}: {text!r} is below"
            # A line squeezed below its least width is cut inside the Area,
            # beside a control, where it reads as a whole line.
            least = qualifier.minimumSizeHint().width()
            assert qualifier.width() >= least, f"{where}: {text!r} is {qualifier.width()} px"

        # A control at the pinned row's right end, such as the schematic's
        # axis top, stays in view with its Area wherever the Area's part in
        # view is as wide as the header and the row need.
        if _part_on_page(page, frame).width() >= frame.chrome.minimumSizeHint().width():
            for control in _controls_in(frame.pinned_row):
                shown = _clipped(page, control).size()
                assert shown == control.size(), f"{where}: {control.accessibleName()!r} is cut"

        for run in frame.content.findChildren(RunSchematic):
            if any(run.isAncestorOf(value) for value in seen):
                # The run's name stands below its Area's header, not under it.
                name_on_page = _on_page(page, run.name_text)
                assert not name_on_page.intersects(chrome), (
                    f"{where}: {run.name_text.text()!r} is under its Area's header"
                )
                view_top = max(_on_page(page, frame.view_scroll.viewport()).top(), 0)
                assert name_on_page.top() >= view_top, (
                    f"{where}: {run.name_text.text()!r} is above the part in view"
                )
                left = run.name_text.mapTo(page.viewport(), QPoint(0, 0)).x()
                assert left >= 0, f"{where}: {run.name_text.text()!r} starts {-left} px left"
                # The name is whole wherever the part of its run in view is
                # wide enough to hold it, beside the share caption's least
                # width and the gap before it. Where it is not, its end is cut
                # at the run's edge (`PL-BQB6`).
                least = run.name_text.minimumSizeHint().width()
                beside = VIEW_HEADING_SPACING + run.share_text.minimumSizeHint().width()

                if least + beside <= _part_on_page(page, run).width():
                    assert run.name_text.width() >= least, (
                        f"{where}: {run.name_text.text()!r} is cut to {run.name_text.width()} px"
                    )

                caption_text = run.share_text.text()
                needed = run.share_text.fontMetrics().horizontalAdvance(caption_text)

                if run.share_text.width() < needed:
                    caption = run.share_text.grab().toImage()
                    assert caption.isNull() or _blank(caption), f"{where}: a cut share caption"

    return seen_in


def _check_chrome_drawn_over_its_view(view: SimulationView, where: str) -> set[AreaId]:
    """Assert that each header standing over its View hides what is under it.

    Where the page has carried an Area's top above the window's edge, the
    part of the page under the Area's header must show the header as drawn
    on its own, so no value shows through it or is drawn over it. Returns
    each Area whose header was checked this way.
    """

    page = view._page_scroll
    areas = view.layout_container
    checked: set[AreaId] = set()

    for area in areas.model.areas():
        frame = areas.frame(area.id)
        drawn = _clipped(page, frame.chrome)
        # The header stands over its View once the Area's own top is above
        # the window's edge by more than a few pixels.
        if frame.mapTo(page.viewport(), QPoint(0, 0)).y() > -10 or drawn.height() < 10:
            continue

        alone = frame.chrome.grab(drawn).toImage()
        on_page = page.viewport().grab(drawn.translated(_on_page(page, frame.chrome).topLeft()))
        assert on_page.toImage() == alone, (
            f"{where}: something shows through Area {area.id}'s header"
        )
        checked.add(area.id)

    return checked


def _beside(kind: ViewKind) -> WorkspaceSet:
    """Return one Workspace whose left Area shows `kind`, beside the parameter controls.

    Where `kind` is the parameter controls, the right Area shows the agent
    accounting instead. Each Area is as tall as the parameter controls need,
    so the schematic draws while the page scrolls down.
    """

    other = AGENT_ACCOUNTING if kind == PARAMETER_CONTROLS else PARAMETER_CONTROLS

    return _workspace(Orientation.ROW, (kind, other))


def _blank(image: QImage) -> bool:
    """Return whether every pixel of `image` is the same, so nothing is drawn on it."""

    first = image.pixel(0, 0)

    return all(
        image.pixel(x, y) == first for x in range(image.width()) for y in range(image.height())
    )


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


def _below(page: QScrollArea, value: QWidget, chrome: QRect) -> QRect:
    """Return the part of `value` in view on the page that is below `chrome`, its Area's header."""

    shown = _part_on_page(page, value).intersected(page.viewport().rect())

    if shown.width() < value.width():
        return QRect()

    if shown.top() <= chrome.bottom() and shown.intersects(chrome):
        shown.setTop(chrome.bottom() + 1)

    return shown if shown.height() > 0 and shown.width() > 0 else QRect()


def _controls_in(row: QWidget | None) -> list[QWidget]:
    """Return the visible controls of a View's pinned row that Tab reaches."""

    if row is None:
        return []

    return [
        widget
        for widget in row.findChildren(QWidget)
        if widget.isVisible() and widget.focusPolicy() & Qt.FocusPolicy.TabFocus
    ]


def _clipped(page: QScrollArea, widget: QWidget) -> QRect:
    """Return the part of `widget` that every widget around it, up to the page, leaves drawn."""

    part = widget.rect()
    holder = widget.parentWidget()

    while holder is not None and holder is not page:
        part = part.intersected(QRect(widget.mapFrom(holder, QPoint(0, 0)), holder.size()))
        holder = holder.parentWidget()

    return part


def _part_on_page(page: QScrollArea, widget: QWidget) -> QRect:
    """Return the part of `widget` inside the viewport of each scroll box around it, on the page."""

    part = _on_page(page, widget)

    for box in [page, *page.findChildren(QScrollArea)]:
        if box.isAncestorOf(widget):
            part = part.intersected(_on_page(page, box.viewport()))

    return part


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
