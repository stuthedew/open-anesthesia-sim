"""Tests of the adapter between the layout model and the widgets, run headless.

`app/area_layout.py` is the one module that builds splitters (`PL-W9P6`).
These tests check what it promises. Each split in the model is a splitter,
and each Area holds its View. The splitters take the model's sizes. A
reader's drag changes the model, and every widget follows the model. A layout
that the model rejects changes nothing. An Area whose View kind the registry
does not hold shows only the failure notice, while its neighbours draw as
usual (`PL-R1WQ`). Each Area's View is built by its registry entry's factory.
The tests also check that the adapter keeps its side of the View contract
(`PL-TH35`): every Area gets a View of its own, a View's state is kept when
the View is replaced, and every View is drawn from one tick. Each expected
size is worked out here from the pixels, never read back from the adapter.
The tests render under the `offscreen` platform that `tests/conftest.py`
selects.
"""

from collections.abc import Iterator, Mapping

import pytest
from PySide6.QtCore import QCoreApplication, QEvent, QPoint, QPointF, Qt
from PySide6.QtGui import QEnterEvent, QImage
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QLabel, QScrollArea, QSplitter, QVBoxLayout, QWidget

from anesthesia_sim.app.area_layout import (
    AREA_MENU_LABEL,
    CLOSE_AREA_LABEL,
    JOIN_WITH_LABEL,
    SPLIT_SIDE_BY_SIDE_LABEL,
    SPLIT_STACKED_LABEL,
    SWAP_WITH_LABEL,
    AreaFrame,
    AreaLayout,
    AreaMenu,
    AreaNotice,
    AreaOperation,
    JoinPreview,
    SplitPreview,
    ViewChooser,
    _AreaHandle,
)
from anesthesia_sim.app.chart_frame import RunInput, assemble_chart_frame
from anesthesia_sim.app.compartment_selection import CompartmentSelection
from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.app.dashboard_frame import run_label
from anesthesia_sim.app.run_series import COMPARTMENT_QUANTITIES
from anesthesia_sim.app.theme import AREA_HANDLE_LINE_WIDTH, AREA_HANDLE_WIDTH, PRIMARY
from anesthesia_sim.app.view_contract import (
    STATE_VERSION_KEY,
    SavedState,
    ViewContext,
    ViewRequests,
    ViewTick,
)
from anesthesia_sim.app.view_registry import RegisteredView, RetiredTag, registry, retirements
from anesthesia_sim.layout.model import Handle, LayoutModel
from anesthesia_sim.layout.run_identity import RunId, SessionToken
from anesthesia_sim.layout.sizing import PixelSize
from anesthesia_sim.layout.tree import Area, AreaId, Node, Orientation, Split, ViewKind, Window

_VIEW = ViewKind("test_view")
_UNKNOWN = ViewKind("retired_view")

# Every test View built, in the order it was built. `_forget_the_views` empties
# it before each test.
_BUILT: list[_TestView] = []

# Every test View refreshed, in the order the adapter refreshed it.
_REFRESHED: list[_TestView] = []

# A View asks the dashboard for nothing here.
_REQUESTS = ViewRequests(lambda _time_base: None, lambda _quantity, _shown: None)


class _TestView(QWidget):
    """A View that draws nothing, and records what it was built from and shown.

    Args:
        context: What the View is built from.
    """

    def __init__(self, context: ViewContext) -> None:
        super().__init__()
        self.context = context
        self.ticks: list[ViewTick] = []
        self.width_px: float | None = None
        self.setting = 0
        # Small enough that Qt's own minimum never stops a drag here.
        self.setMinimumSize(10, 10)
        _BUILT.append(self)

        if context.saved_state is not None:
            setting = context.saved_state["setting"]
            assert isinstance(setting, int)
            self.setting = setting

    def refresh(self, tick: ViewTick) -> None:
        self.ticks.append(tick)
        _REFRESHED.append(self)

    @property
    def owes_a_frame(self) -> bool:
        return not self.ticks

    def frame_width_px(self) -> float | None:
        return self.width_px

    def save_state(self) -> SavedState:
        return {STATE_VERSION_KEY: 1, "setting": self.setting}

    def painted_strings(self) -> tuple[str, ...]:
        return (f"painted {self.setting}",)


class _OtherView(_TestView):
    """The View of `_OTHER`, told apart from `_TestView` by its class."""


class _ThirdView(_TestView):
    """The View of `_THIRD`."""


# The tests draw a View kind of their own, so they register it themselves.
_REGISTERED = registry(RegisteredView(_VIEW, "Test view", _TestView))

# A container this size leaves 800 px for the children of a split of two, once
# the 8 px handle is taken out, so a fraction reads straight off as pixels. A
# quarter of it is wider than an Area's header, which an Area is never drawn
# narrower than (`PL-K285`).
_SIDE_PX = 800 + AREA_HANDLE_WIDTH


def _area(number: int) -> Area:
    return Area(AreaId(number), _VIEW)


def _layout(tree: Node, next_id: int) -> LayoutModel:
    return LayoutModel((Window(tree),), AreaId(next_id))


def _row(sizes: tuple[float, ...], *children: Node) -> Split:
    return Split(Orientation.ROW, sizes, children)


def _column(sizes: tuple[float, ...], *children: Node) -> Split:
    return Split(Orientation.COLUMN, sizes, children)


@pytest.fixture(scope="module")
def application() -> Iterator[QApplication]:
    existing = QApplication.instance()

    yield existing if isinstance(existing, QApplication) else QApplication([])


@pytest.fixture(autouse=True)
def _forget_the_views() -> Iterator[None]:
    _BUILT.clear()
    _REFRESHED.clear()
    yield
    _BUILT.clear()
    _REFRESHED.clear()


@pytest.fixture
def shown(application: QApplication) -> Iterator[list[AreaLayout]]:
    """Every container a test shows, closed after it."""

    containers: list[AreaLayout] = []
    yield containers

    for container in containers:
        container.close()
        container.deleteLater()

    application.processEvents()


def _show(
    application: QApplication,
    shown: list[AreaLayout],
    model: LayoutModel,
    size: tuple[int, int] = (_SIDE_PX, _SIDE_PX),
) -> AreaLayout:
    container = AreaLayout(model, _REQUESTS, registered=_REGISTERED)
    container.resize(*size)
    container.show()
    application.processEvents()
    shown.append(container)

    return container


def _splitters(container: AreaLayout) -> dict[tuple[int, ...], QSplitter]:
    """Each splitter the container holds, by the path of the split it draws."""

    return {splitter.path: splitter for splitter in container.findChildren(QSplitter)}  # type: ignore[attr-defined]


def _drag(application: QApplication, splitter: QSplitter, index: int, by_px: int) -> None:
    """Drag `splitter`'s handle `index` by `by_px` along the splitter's axis, as a mouse does."""

    handle = splitter.handle(index)
    start = handle.rect().center()
    step = (
        QPoint(by_px, 0)
        if splitter.orientation() == Qt.Orientation.Horizontal
        else QPoint(0, by_px)
    )
    QTest.mousePress(handle, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, start)
    QTest.mouseMove(handle, start + step)
    QTest.mouseRelease(
        handle, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, start + step
    )
    application.processEvents()


def _content(widget: QWidget) -> QWidget:
    """What the Area `widget` draws shows under its header: its View or its notice."""

    assert isinstance(widget, AreaFrame), f"{widget!r} is not an Area's frame"

    return widget.content


def _tree(container: AreaLayout) -> Node:
    return container.model.windows[0].tree


def _primary_pixels(image: QImage) -> int:
    return sum(
        1
        for x in range(image.width())
        for y in range(image.height())
        if image.pixelColor(x, y).name().upper() == PRIMARY.upper()
    )


# ------------------------------------------------------------ building


def test_each_split_is_a_splitter_and_each_area_its_view(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    """A column holding a row of Areas 1 and 2 above Area 3 is two splitters, nested."""

    model = _layout(_column((0.5, 0.5), _row((0.5, 0.5), _area(1), _area(2)), _area(3)), 4)
    container = _show(application, shown, model)
    splitters = _splitters(container)

    assert set(splitters) == {(), (0,)}
    assert splitters[()].orientation() == Qt.Orientation.Vertical
    assert splitters[(0,)].orientation() == Qt.Orientation.Horizontal
    assert splitters[()].widget(0) is splitters[(0,)]
    assert len(_BUILT) == 3
    assert _content(splitters[(0,)].widget(0)) is _BUILT[0]
    assert _content(splitters[(0,)].widget(1)) is _BUILT[1]
    assert _content(splitters[()].widget(1)) is _BUILT[2]
    assert container.views() == tuple(_BUILT)


def test_every_handle_is_live_and_no_area_can_be_dragged_to_nothing(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    """The handles v0.4.26 built inert are enabled, the width `PL-RQT1` set, with split cursors."""

    model = _layout(_column((0.5, 0.5), _row((0.5, 0.5), _area(1), _area(2)), _area(3)), 4)
    splitters = _splitters(_show(application, shown, model))
    cursors = {(): Qt.CursorShape.SplitVCursor, (0,): Qt.CursorShape.SplitHCursor}

    for path, splitter in splitters.items():
        assert not splitter.childrenCollapsible()
        assert splitter.handleWidth() == AREA_HANDLE_WIDTH
        assert splitter.handle(1).isEnabled()
        assert splitter.handle(1).cursor().shape() == cursors[path]


def test_a_layout_of_one_area_is_its_view_alone(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    container = _show(application, shown, LayoutModel.single_area(_VIEW))

    assert _splitters(container) == {}
    (view,) = _BUILT
    assert view.parentWidget() is container.frame(AreaId(1))
    assert container.frame(AreaId(1)).parentWidget() is container
    assert view.isVisible()


def test_the_splitters_take_the_sizes_the_model_holds(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    """A quarter and three quarters of 800 px are 200 px and 600 px."""

    container = _show(application, shown, _layout(_row((0.25, 0.75), _area(1), _area(2)), 3))

    assert _splitters(container)[()].sizes() == [200, 600]


def test_a_layout_of_two_windows_is_refused() -> None:
    """This build opens one window, so an Area in a second would not be drawn at all."""

    model = LayoutModel((Window(_area(1)), Window(_area(2))), AreaId(3))

    with pytest.raises(ValueError, match="draws one window, and the layout holds 2"):
        AreaLayout(model, _REQUESTS, registered=_REGISTERED)


# --------------------------------------------------------- a reader's drag


def test_a_drag_on_a_border_changes_the_layout_model(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    """Dragging the border 200 px right of the middle of 800 px leaves it three quarters across."""

    container = _show(application, shown, _layout(_row((0.5, 0.5), _area(1), _area(2)), 3))
    changed: list[LayoutModel] = []
    container.layout_changed.connect(changed.append)

    _drag(application, _splitters(container)[()], 1, 200)

    tree = _tree(container)
    assert isinstance(tree, Split)
    assert tree.sizes == pytest.approx((0.75, 0.25), abs=1 / 800)
    assert changed == [container.model]
    assert _splitters(container)[()].sizes() == [600, 200]


def test_a_drag_moves_every_handle_on_the_dragged_line(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    """Two rows stacked, each split at the middle: dragging the top border moves the bottom one.

    The two borders are one line, as they are one edge in Blender, so the
    model moves both (`PL-5HSG`) and the bottom splitter's widgets follow the
    model though nobody dragged that splitter.
    """

    model = _layout(
        _column(
            (0.5, 0.5), _row((0.5, 0.5), _area(1), _area(2)), _row((0.5, 0.5), _area(3), _area(4))
        ),
        5,
    )
    container = _show(application, shown, model)
    splitters = _splitters(container)

    _drag(application, splitters[(0,)], 1, -200)

    tree = _tree(container)
    assert isinstance(tree, Split)

    for row in tree.children:
        assert isinstance(row, Split)
        assert row.sizes == pytest.approx((0.25, 0.75), abs=1 / 800)

    assert splitters[(0,)].sizes() == [200, 600]
    assert splitters[(1,)].sizes() == [200, 600]


def test_a_drag_leaves_a_border_on_another_line_where_it_was(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    """The bottom border, at 0.7, is not on the top border's line at 0.5, so it stays."""

    model = _layout(
        _column(
            (0.5, 0.5), _row((0.5, 0.5), _area(1), _area(2)), _row((0.7, 0.3), _area(3), _area(4))
        ),
        5,
    )
    container = _show(application, shown, model)
    splitters = _splitters(container)

    _drag(application, splitters[(0,)], 1, -200)

    tree = _tree(container)
    assert isinstance(tree, Split)
    bottom = tree.children[1]
    assert isinstance(bottom, Split)
    assert bottom.sizes == (0.7, 0.3)
    assert splitters[(1,)].sizes() == [560, 240]


def _press(
    handle: QWidget, modifier: Qt.KeyboardModifier = Qt.KeyboardModifier.NoModifier
) -> QPoint:
    start = handle.rect().center()
    QTest.mousePress(handle, Qt.MouseButton.LeftButton, modifier, start)

    return start


def _along(splitter: QSplitter, by_px: int) -> QPoint:
    if splitter.orientation() == Qt.Orientation.Horizontal:
        return QPoint(by_px, 0)

    return QPoint(0, by_px)


_PAST_A_NEIGHBOUR = _layout(
    _column(
        (0.5, 0.5),
        _row((0.5, 0.5), _area(1), _area(2)),
        _row((0.5, 0.3, 0.2), _area(3), _area(4), _area(5)),
    ),
    6,
)


def test_a_drag_stops_where_a_neighbour_reaches_its_least_size_and_its_line_turns_warning(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    """`PL-RQT1` Q3: the border goes no further, and both handles on its line say so.

    The bottom row's first border is on the top border's line, so it moves
    with it. Area 4 lies between that border and the next one, at 0.8 of
    the window. A drag of 300 px to the right would carry the line to 0.875,
    past 0.8. So the line stops where Area 4 is as narrow as Qt would draw
    it: the least size its frame is held at, plus the handle width the
    adapter allows for, short of 0.8 of the container's width.
    """

    container = _show(application, shown, _PAST_A_NEIGHBOUR)
    splitters = _splitters(container)
    top, bottom = splitters[(0,)].handle(1), splitters[(1,)].handle(1)
    least = container.frame(AreaId(4)).minimumWidth()
    expected = 0.8 - (least + AREA_HANDLE_WIDTH) / container.width()
    assert isinstance(top, _AreaHandle) and isinstance(bottom, _AreaHandle)

    start = _press(top)
    back = top.mapToGlobal(start + _along(splitters[(0,)], 10))
    QTest.mouseMove(top, start + _along(splitters[(0,)], 300))
    application.processEvents()

    assert container.model.position(Handle(0, (0,), 0)) == pytest.approx(expected, abs=1e-5)
    assert container.model.position(Handle(0, (1,), 0)) == pytest.approx(expected, abs=1e-5)
    assert top.lit and top.warning
    assert bottom.lit and bottom.warning
    assert not splitters[()].handle(1).lit

    # The handle has moved, and QTest places the pointer relative to it.
    QTest.mouseMove(top, top.mapFromGlobal(back))
    application.processEvents()

    assert not top.warning
    assert container.model.position(Handle(0, (0,), 0)) == pytest.approx(410 / 800)

    QTest.mouseRelease(
        top, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, start + QPoint(10, 0)
    )
    application.processEvents()

    assert not top.warning and not bottom.warning


def test_a_drag_with_shift_moves_only_the_border_under_the_pointer(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    """The two rows' borders are one line, but with Shift held only the top one moves."""

    model = _layout(
        _column(
            (0.5, 0.5), _row((0.5, 0.5), _area(1), _area(2)), _row((0.5, 0.5), _area(3), _area(4))
        ),
        5,
    )
    container = _show(application, shown, model)
    splitters = _splitters(container)
    top, bottom = splitters[(0,)].handle(1), splitters[(1,)].handle(1)
    assert isinstance(top, _AreaHandle) and isinstance(bottom, _AreaHandle)

    start = _press(top, Qt.KeyboardModifier.ShiftModifier)
    QTest.mouseMove(top, start + QPoint(-200, 0))
    application.processEvents()

    assert top.lit and not bottom.lit

    QTest.mouseRelease(
        top, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.ShiftModifier, start + QPoint(-200, 0)
    )
    application.processEvents()

    tree = _tree(container)
    assert isinstance(tree, Split)
    upper, lower = tree.children
    assert isinstance(upper, Split) and isinstance(lower, Split)
    assert upper.sizes == pytest.approx((0.25, 0.75), abs=1 / 800)
    assert lower.sizes == (0.5, 0.5)
    assert splitters[(0,)].sizes() == [200, 600]
    assert splitters[(1,)].sizes() == [400, 400]


def test_escape_returns_a_border_drag_to_where_it_started(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    """The Areas followed the pointer live, so Escape announces the layout it returns to."""

    model = _layout(_row((0.5, 0.5), _area(1), _area(2)), 3)
    container = _show(application, shown, model)
    changed: list[LayoutModel] = []
    container.layout_changed.connect(changed.append)
    splitter = _splitters(container)[()]
    handle = splitter.handle(1)

    start = _press(handle)
    QTest.mouseMove(handle, start + QPoint(200, 0))
    application.processEvents()

    assert splitter.sizes() == [600, 200]

    QTest.keyClick(handle, Qt.Key.Key_Escape)
    QTest.mouseRelease(
        handle, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, start + QPoint(200, 0)
    )
    application.processEvents()

    assert container.model == model
    assert splitter.sizes() == [400, 400]
    assert changed[-1] == model and len(changed) == 2


def test_a_resize_keeps_the_fractions_and_changes_no_model(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    """After a drag to three quarters, a window twice as wide draws 1200 px and 400 px."""

    container = _show(application, shown, _layout(_row((0.5, 0.5), _area(1), _area(2)), 3))
    _drag(application, _splitters(container)[()], 1, 200)
    dragged = container.model
    changed: list[LayoutModel] = []
    container.layout_changed.connect(changed.append)

    container.resize(1600 + AREA_HANDLE_WIDTH, _SIDE_PX)
    application.processEvents()

    assert container.model == dragged
    assert changed == []
    assert _splitters(container)[()].sizes() == [1200, 400]


# ---------------------------------------------------- a layout set in code


def test_new_sizes_keep_every_view_where_it_is(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    container = _show(application, shown, _layout(_row((0.5, 0.5), _area(1), _area(2)), 3))
    splitter = _splitters(container)[()]
    changed: list[LayoutModel] = []
    container.layout_changed.connect(changed.append)

    resized = container.model.resize(Handle(0, (), 0), 0.25)
    container.set_model(resized)
    application.processEvents()

    assert container.model == resized
    assert _splitters(container)[()] is splitter
    assert splitter.sizes() == [200, 600]
    assert changed == []
    assert len(_BUILT) == 2


def test_a_swap_moves_each_view_to_the_other_area(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    """The splitters are built again, and each View is moved, not made again."""

    container = _show(application, shown, _layout(_row((0.25, 0.75), _area(1), _area(2)), 3))
    first, second = _BUILT

    container.set_model(container.model.swap(AreaId(1), AreaId(2)))
    application.processEvents()
    splitter = _splitters(container)[()]

    assert _content(splitter.widget(0)) is second
    assert _content(splitter.widget(1)) is first
    assert first.isVisible() and second.isVisible()
    assert splitter.sizes() == [200, 600]
    assert _BUILT == [first, second]


def test_a_view_the_new_layout_does_not_hold_leaves_the_container(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    """Joining Area 2 into Area 1 leaves one View; the other is taken out and deleted."""

    container = _show(application, shown, _layout(_row((0.5, 0.5), _area(1), _area(2)), 3))
    kept, removed = _BUILT
    deleted: list[bool] = []
    removed.destroyed.connect(lambda: deleted.append(True))

    container.set_model(container.model.join(AreaId(1), AreaId(2)))
    application.processEvents()

    assert _splitters(container) == {}
    assert kept.parentWidget() is container.frame(AreaId(1))
    assert removed.parentWidget() is None
    assert container.views() == (kept,)

    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)

    assert deleted, "the View no Area shows was kept alive"


# ------------------------------------------------- an unknown View kind

# The notice's two lines, written out here rather than read from the module
# that writes them (`PL-DB5G` Q2).
_NOTICE_TITLE = "This Area's View is not in this build."
_NOTICE_BODY = (
    "It was saved as the View kind 'retired_view'. This build does not know it. "
    "Choose a View from the menu above. The saved name is kept until you do."
)


def _texts(widget: QWidget) -> list[str]:
    """Every string `widget` and its descendants show, in the order they were built."""

    return [label.text() for label in widget.findChildren(QLabel) if label.isVisible()]


def test_an_area_of_an_unknown_kind_shows_the_notice_and_nothing_else(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    """The middle Area of three fails alone, and its neighbours draw their Views."""

    model = _layout(_row((0.25, 0.5, 0.25), _area(1), Area(AreaId(2), _UNKNOWN), _area(3)), 4)
    container = _show(application, shown, model, (800 + 2 * AREA_HANDLE_WIDTH, 400))
    splitter = _splitters(container)[()]
    notice = _content(splitter.widget(1))

    assert _content(splitter.widget(0)) is _BUILT[0]
    assert _content(splitter.widget(2)) is _BUILT[1]
    assert isinstance(notice, AreaNotice)
    assert notice.isVisible()
    assert _texts(notice) == [_NOTICE_TITLE, _NOTICE_BODY]
    assert len(_BUILT) == 2
    assert splitter.sizes() == [200, 400, 200]


def test_the_model_keeps_the_unknown_kind_so_a_save_writes_back_what_was_read(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    """A drag beside the failed Area changes its size and never its kind."""

    model = _layout(_row((0.5, 0.5), _area(1), Area(AreaId(2), _UNKNOWN)), 3)
    container = _show(application, shown, model)

    _drag(application, _splitters(container)[()], 1, 100)

    assert container.model.unknown_kinds(_REGISTERED.keys()) == (Area(AreaId(2), _UNKNOWN),)
    assert container.model != model


def test_a_layout_of_one_unknown_area_is_the_notice_alone(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    container = _show(application, shown, _layout(Area(AreaId(1), _UNKNOWN), 2))

    assert _splitters(container) == {}
    assert [type(child) for child in container.findChildren(AreaNotice)] == [AreaNotice]
    assert _texts(container) == [_NOTICE_TITLE, _NOTICE_BODY]
    assert _BUILT == []


def test_a_rebuild_deletes_the_notices_the_old_layout_drew(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    """Replacing the failed Area's layout leaves no notice behind, not even a hidden one."""

    model = _layout(_row((0.5, 0.5), _area(1), Area(AreaId(2), _UNKNOWN)), 3)
    container = _show(application, shown, model)

    container.set_model(_layout(_row((0.5, 0.5), _area(1), _area(2)), 3))
    application.processEvents()

    assert container.findChildren(AreaNotice) == []
    assert _content(_splitters(container)[()].widget(1)) is _BUILT[-1]
    assert len(_BUILT) == 2


def test_the_default_registry_holds_no_test_kind(application: QApplication) -> None:
    """Built with the shipped registry, the adapter draws a test-only kind as a failure."""

    container = AreaLayout(_layout(_area(1), 2), _REQUESTS)

    try:
        assert len(container.findChildren(AreaNotice)) == 1
        assert _BUILT == []
    finally:
        container.deleteLater()


# ------------------------------------------------------------- the handle


def test_a_handle_draws_nothing_at_rest_and_lights_its_whole_line_under_the_pointer(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    """`PL-RQT1` Q1 and Q2: a gap at rest, and a line on every handle a drag would move.

    The top and bottom borders are one line, so the pointer over the top one
    lights both, while the column's own handle, on another line, stays dark.
    """

    model = _layout(
        _column(
            (0.5, 0.5), _row((0.5, 0.5), _area(1), _area(2)), _row((0.5, 0.5), _area(3), _area(4))
        ),
        5,
    )
    splitters = _splitters(_show(application, shown, model))
    top, bottom, across = (splitters[path].handle(1) for path in ((0,), (1,), ()))

    assert [_primary_pixels(handle.grab().toImage()) for handle in (top, bottom, across)] == [
        0,
        0,
        0,
    ]

    point = QPointF(top.rect().center())
    QApplication.sendEvent(top, QEnterEvent(point, point, point))

    # A 2 px line down the whole height of each lit handle, and none across.
    assert [_primary_pixels(handle.grab().toImage()) for handle in (top, bottom, across)] == [
        AREA_HANDLE_LINE_WIDTH * top.height(),
        AREA_HANDLE_LINE_WIDTH * bottom.height(),
        0,
    ]

    QApplication.sendEvent(top, QEvent(QEvent.Type.Leave))

    assert [_primary_pixels(handle.grab().toImage()) for handle in (top, bottom, across)] == [
        0,
        0,
        0,
    ]


# ------------------------------------------------- the header and the chooser

_OTHER = ViewKind("other_view")
_THIRD = ViewKind("third_view")

# Three kinds, so the chooser's order and its one checked entry are told apart
# from an order or a check that only happens to match.
_THREE = registry(
    RegisteredView(_VIEW, "Test view", _TestView),
    RegisteredView(_OTHER, "Other view", _OtherView),
    RegisteredView(_THIRD, "Third view", _ThirdView),
)


def _show_with(
    application: QApplication,
    shown: list[AreaLayout],
    model: LayoutModel,
    registered: Mapping[str, RegisteredView] = _THREE,
    retired: Mapping[str, RetiredTag] | None = None,
) -> AreaLayout:
    container = AreaLayout(
        model, _REQUESTS, registered=registered, retired={} if retired is None else retired
    )
    container.resize(800 + AREA_HANDLE_WIDTH, 400)
    container.show()
    application.processEvents()
    shown.append(container)

    return container


def _entries(chooser: ViewChooser) -> list[tuple[str, bool]]:
    menu = chooser.menu()
    assert menu is not None

    return [(action.text(), action.isChecked()) for action in menu.actions()]


def _pick(application: QApplication, chooser: ViewChooser, title: str) -> None:
    """Trigger the chooser's menu entry `title`, as a reader's click on it does."""

    menu = chooser.menu()
    assert menu is not None
    (action,) = [action for action in menu.actions() if action.text() == title]
    action.trigger()
    application.processEvents()


def test_every_area_has_a_header_whose_chooser_names_its_view(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    """`PL-MS34` Q2: the chooser is the header's first control and shows the View's title."""

    model = _layout(_row((0.5, 0.5), Area(AreaId(1), _VIEW), Area(AreaId(2), _OTHER)), 3)
    container = _show_with(application, shown, model)

    for area_id, title in ((1, "Test view"), (2, "Other view")):
        frame = container.frame(AreaId(area_id))

        assert frame.chooser.text() == title
        assert frame.header.layout().itemAt(0).widget() is frame.chooser
        assert frame.header.isVisible() and frame.chooser.isVisible()
        assert frame.header.geometry().bottom() < frame.content.geometry().top()
        assert frame.chooser.focusPolicy() == Qt.FocusPolicy.StrongFocus


def test_the_chooser_lists_every_registered_kind_in_order_with_the_current_one_checked(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    """`PL-RBXL` Q2: a plain menu in registry order, whatever the layout names."""

    model = _layout(_row((0.5, 0.5), Area(AreaId(1), _OTHER), Area(AreaId(2), _OTHER)), 3)
    container = _show_with(application, shown, model)

    assert _entries(container.frame(AreaId(1)).chooser) == [
        ("Test view", False),
        ("Other view", True),
        ("Third view", False),
    ]


def test_choosing_a_view_sets_it_in_that_area_and_nowhere_else(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    model = _layout(_row((0.5, 0.5), Area(AreaId(1), _VIEW), Area(AreaId(2), _VIEW)), 3)
    container = _show_with(application, shown, model)
    changed: list[LayoutModel] = []
    container.layout_changed.connect(changed.append)
    replaced = container.frame(AreaId(1)).content
    kept = container.frame(AreaId(2)).content

    _pick(application, container.frame(AreaId(1)).chooser, "Other view")

    expected = _layout(_row((0.5, 0.5), Area(AreaId(1), _OTHER), Area(AreaId(2), _VIEW)), 3)
    assert container.model == expected
    assert changed == [expected]
    assert isinstance(container.frame(AreaId(1)).content, _OtherView)
    assert container.frame(AreaId(1)).chooser.text() == "Other view"
    assert container.frame(AreaId(2)).content is kept
    assert replaced.parentWidget() is None


def test_choosing_the_view_already_shown_changes_nothing(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    model = _layout(_row((0.5, 0.5), Area(AreaId(1), _VIEW), Area(AreaId(2), _OTHER)), 3)
    container = _show_with(application, shown, model)
    frame = container.frame(AreaId(1))
    changed: list[LayoutModel] = []
    container.layout_changed.connect(changed.append)

    _pick(application, frame.chooser, "Test view")

    assert container.model == model
    assert changed == []
    assert container.frame(AreaId(1)) is frame


def test_two_areas_of_one_kind_each_get_a_view_of_their_own(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    """`PL-TH35` Q8: the factory builds a View for each Area, so neither Area is a notice."""

    model = _layout(_row((0.5, 0.5), _area(1), _area(2)), 3)
    container = _show_with(application, shown, model)
    first, second = (container.frame(AreaId(n)).content for n in (1, 2))

    assert isinstance(first, _TestView) and isinstance(second, _TestView)
    assert first is not second
    assert container.findChildren(AreaNotice) == []
    assert first.isVisible() and second.isVisible()


def test_a_view_replaced_and_chosen_again_comes_back_with_its_state(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    """A replaced View's state is kept under its Area and kind (`PL-TH35` Q10).

    Area 2 shows the same kind and keeps its own setting. So the test shows
    that the state is kept apart by Area as well as by kind.
    """

    model = _layout(_row((0.5, 0.5), _area(1), _area(2)), 3)
    container = _show_with(application, shown, model)
    first = container.frame(AreaId(1)).content
    assert isinstance(first, _TestView)
    first.setting = 7

    _pick(application, container.frame(AreaId(1)).chooser, "Other view")
    other = container.frame(AreaId(1)).content

    assert isinstance(other, _OtherView)
    assert other.context.saved_state is None

    _pick(application, container.frame(AreaId(1)).chooser, "Test view")
    back = container.frame(AreaId(1)).content

    assert isinstance(back, _TestView) and back is not first
    assert back.context.saved_state == {STATE_VERSION_KEY: 1, "setting": 7}
    assert back.setting == 7
    second = container.frame(AreaId(2)).content
    assert isinstance(second, _TestView)
    assert second.setting == 0


def _broken(_context: ViewContext) -> _TestView:
    raise RuntimeError("no chart to draw on")


def test_a_view_that_cannot_be_built_is_a_notice_in_its_area_alone(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    """A factory that raises, or builds no View, leaves its Area saying so and the rest drawn.

    A widget that cannot be refreshed would leave its Area showing a stale
    picture. A raise from the chooser's menu would be lost, and it left the
    layout half built: the Area's old View moved into a frame never shown.
    """

    cases = (
        (_broken, "Building 'Third view' failed: RuntimeError: no chart to draw on."),
        (
            lambda _context: QWidget(),
            "Building 'Third view' failed: TypeError: the factory for the View kind "
            "'third_view' returned a QWidget, which is not a QWidget that satisfies the "
            "View contract.",
        ),
    )

    for built, body in cases:
        registered = registry(
            RegisteredView(_VIEW, "Test view", _TestView),
            RegisteredView(_OTHER, "Other view", _OtherView),
            RegisteredView(_THIRD, "Third view", built),
        )
        model = _layout(_row((0.5, 0.5), Area(AreaId(1), _VIEW), Area(AreaId(2), _OTHER)), 3)
        container = _show_with(application, shown, model, registered=registered)
        kept = container.frame(AreaId(1)).content

        _pick(application, container.frame(AreaId(2)).chooser, "Third view")
        notice = container.frame(AreaId(2)).content

        assert isinstance(notice, AreaNotice)
        assert _texts(notice) == [
            "This Area's View could not be built.",
            f"{body} Choose a View from the menu above.",
        ]
        assert container.frame(AreaId(1)).content is kept
        assert kept.isVisible()
        assert container.model.area(AreaId(2)).view == _THIRD

        _pick(application, container.frame(AreaId(2)).chooser, "Other view")

        assert isinstance(container.frame(AreaId(2)).content, _OtherView)


def _tick() -> ViewTick:
    """A tick from one run that has not started, as the dashboard assembles one."""

    controller = SimulationController()
    snapshot = controller.snapshot()
    selection = CompartmentSelection(COMPARTMENT_QUANTITIES, 1)
    frame = assemble_chart_frame(
        [RunInput(run_label(RunId(SessionToken("0" * 32), 1)), controller, snapshot, ())],
        None,
        selection.shown,
        plot_width_px=400.0,
    )

    return ViewTick(frame, (snapshot,), (), None, selection)


def test_every_view_is_drawn_from_the_one_tick_in_reading_order(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    """The adapter hands each View the same tick, and owes a frame until each has drawn one."""

    model = _layout(_row((0.25, 0.5, 0.25), _area(1), Area(AreaId(2), _OTHER), _area(3)), 4)
    container = _show_with(application, shown, model)
    tick = _tick()

    for setting, view in enumerate(_BUILT):
        view.setting = setting

    assert container.owes_a_frame

    container.refresh(tick)

    assert [view.ticks for view in _BUILT] == [[tick], [tick], [tick]]
    assert _REFRESHED == _BUILT
    assert not container.owes_a_frame
    assert [text for _, text in container.painted_strings()] == [
        "painted 0",
        "painted 1",
        "painted 2",
    ]


def test_the_frame_is_sampled_for_the_widest_view_that_draws_one(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    """A View that draws no frame asks for no width, and with none asking the width is 0."""

    model = _layout(_row((0.25, 0.5, 0.25), _area(1), _area(2), _area(3)), 4)
    container = _show_with(application, shown, model)

    assert container.frame_width_px() == 0.0

    _BUILT[0].width_px = 300.0
    _BUILT[2].width_px = 650.5

    assert container.frame_width_px() == 650.5


def test_an_unknown_kind_can_be_replaced_from_its_own_chooser(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    """The notice's chooser lists every kind, none checked, and a choice replaces the notice."""

    model = _layout(_row((0.5, 0.5), Area(AreaId(1), _VIEW), Area(AreaId(2), _UNKNOWN)), 3)
    container = _show_with(application, shown, model)
    chooser = container.frame(AreaId(2)).chooser

    assert chooser.text() == "retired_view"
    assert [checked for _, checked in _entries(chooser)] == [False, False, False]

    _pick(application, chooser, "Other view")

    assert isinstance(container.frame(AreaId(2)).content, _OtherView)
    assert container.findChildren(AreaNotice) == []


def test_a_renamed_kind_is_offered_its_new_tag_and_never_mapped_to_it(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    """`PL-R1WQ` Q3: the notice offers the rename, and only the reader's click takes it."""

    retired = retirements(_THREE, RetiredTag(_UNKNOWN, "0.7.0", _OTHER))
    model = _layout(_row((0.5, 0.5), Area(AreaId(1), _VIEW), Area(AreaId(2), _UNKNOWN)), 3)
    container = _show_with(application, shown, model, retired=retired)
    notice = container.frame(AreaId(2)).content

    assert isinstance(notice, AreaNotice)
    assert notice.offer_button is not None
    assert notice.offer_button.text() == "Show 'Other view'"
    assert container.model.area(AreaId(2)).view == _UNKNOWN

    notice.offer_button.click()
    application.processEvents()

    assert container.model.area(AreaId(2)).view == _OTHER
    assert isinstance(container.frame(AreaId(2)).content, _OtherView)


def test_a_removed_or_unknown_kind_offers_no_button(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    gone = ViewKind("gone_view")
    retired = retirements(_THREE, RetiredTag(gone, "0.7.0"))
    model = _layout(_row((0.5, 0.5), Area(AreaId(1), gone), Area(AreaId(2), _UNKNOWN)), 3)
    container = _show_with(application, shown, model, retired=retired)

    for area_id in (1, 2):
        notice = container.frame(AreaId(area_id)).content
        assert isinstance(notice, AreaNotice)
        assert notice.offer_button is None


# ------------------------------------------------------------ the Area menu

# Three Areas: Area 1 on the left half, and Areas 2 and 3 stacked on the right.
# Area 1 meets both along part of its right edge, and 2 and 3 share a whole edge.
_LEFT_AND_STACK = _layout(_row((0.5, 0.5), _area(1), _column((0.5, 0.5), _area(2), _area(3))), 4)


def _operation(
    container: AreaLayout, area_id: int, label: str, group: str | None = None
) -> AreaOperation:
    (found,) = [
        operation
        for operation in container.operations(AreaId(area_id))
        if operation.label == label and operation.group == group
    ]

    return found


def _labels(container: AreaLayout, area_id: int) -> list[tuple[str | None, str, bool]]:
    return [
        (operation.group, operation.label, operation.available)
        for operation in container.operations(AreaId(area_id))
    ]


def test_every_header_ends_with_the_area_menu(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    """`PL-MS34` Q2: chooser first, then a stretch, then the Area menu."""

    container = _show(application, shown, _LEFT_AND_STACK, size=(800, 600))

    for number in (1, 2, 3):
        frame = container.frame(AreaId(number))
        row = frame.header.layout()
        assert row is not None

        assert isinstance(frame.menu, AreaMenu)
        assert frame.menu.text() == AREA_MENU_LABEL
        assert row.itemAt(0).widget() is frame.chooser
        assert row.itemAt(row.count() - 1).widget() is frame.menu


def test_the_menu_offers_each_operation_and_shows_a_join_the_layout_cannot_make(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    """A neighbour along part of an edge is listed and unavailable, never left out (`PL-2KXB`)."""

    container = _show(application, shown, _LEFT_AND_STACK, size=(800, 600))

    assert _labels(container, 1) == [
        (None, SPLIT_SIDE_BY_SIDE_LABEL, True),
        (None, SPLIT_STACKED_LABEL, True),
        (JOIN_WITH_LABEL, "Test view, on the right", False),
        (JOIN_WITH_LABEL, "Test view, on the right", False),
        (SWAP_WITH_LABEL, "Test view, above, on the right", True),
        (SWAP_WITH_LABEL, "Test view, below, on the right", True),
        (None, CLOSE_AREA_LABEL, False),
    ]
    assert _labels(container, 2) == [
        (None, SPLIT_SIDE_BY_SIDE_LABEL, True),
        (None, SPLIT_STACKED_LABEL, True),
        (JOIN_WITH_LABEL, "Test view, on the left", False),
        (JOIN_WITH_LABEL, "Test view, below", True),
        (SWAP_WITH_LABEL, "Test view, below, on the left", True),
        (SWAP_WITH_LABEL, "Test view, below", True),
        (None, CLOSE_AREA_LABEL, True),
    ]

    refused = container.operations(AreaId(1))[2]

    assert "do not share a whole edge" in refused.refusal
    assert "Area 1" not in refused.refusal
    assert "only Area" not in _operation(container, 1, CLOSE_AREA_LABEL).refusal
    assert "none can take its place" in _operation(container, 1, CLOSE_AREA_LABEL).refusal


def test_join_split_swap_and_close_each_draw_the_layout_worked_out_by_hand(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    """Each expected layout is built here, not read back from the model."""

    container = _show(application, shown, _LEFT_AND_STACK, size=(800, 600))
    changes: list[LayoutModel] = []
    container.layout_changed.connect(changes.append)

    container.perform(_operation(container, 2, "Test view, below", JOIN_WITH_LABEL))
    application.processEvents()

    assert container.model == _layout(_row((0.5, 0.5), _area(1), _area(2)), 4)
    assert changes == [container.model]

    container.perform(_operation(container, 1, SPLIT_SIDE_BY_SIDE_LABEL))
    application.processEvents()

    assert container.model == _layout(_row((0.25, 0.25, 0.5), _area(1), _area(4), _area(2)), 5)

    container.perform(_operation(container, 4, CLOSE_AREA_LABEL))
    application.processEvents()

    # Area 4's first neighbour sharing a whole edge is Area 1 on its left.
    assert container.model == _layout(_row((0.5, 0.5), _area(1), _area(2)), 5)

    view_of_1 = _content(container.frame(AreaId(1)))
    container.perform(_operation(container, 1, "Test view, on the right", SWAP_WITH_LABEL))
    application.processEvents()

    assert container.model == _layout(_row((0.5, 0.5), _area(2), _area(1)), 5)
    assert _content(container.frame(AreaId(1))) is view_of_1
    assert len(changes) == 4


def _settings(container: AreaLayout) -> dict[int, int]:
    """Each Area's `_TestView` setting, by Area id, in reading order."""

    shown: dict[int, int] = {}

    for area in container.model.areas():
        view = container.frame(area.id).content
        assert isinstance(view, _TestView)
        shown[int(area.id)] = view.setting

    return shown


def test_the_new_half_of_a_split_starts_from_a_copy_of_the_cut_views_state(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    """`PL-TH35` Q10: a split from the menu or by the corner copies the source's settings.

    Three Areas each hold a different setting, so a copy taken from the wrong
    Area, or given to an Area the split did not make, changes the result.
    """

    container = _show(application, shown, _LEFT_AND_STACK, size=(800, 600))

    for area_id, setting in ((1, 5), (2, 7), (3, 9)):
        view = container.frame(AreaId(area_id)).content
        assert isinstance(view, _TestView)
        view.setting = setting

    source = container.frame(AreaId(2)).content
    container.perform(_operation(container, 2, SPLIT_SIDE_BY_SIDE_LABEL))
    application.processEvents()

    assert _settings(container) == {1: 5, 2: 7, 4: 7, 3: 9}
    assert container.frame(AreaId(2)).content is source
    assert container.frame(AreaId(4)).content is not source

    _corner_drag(container, 1, [(100, 300), (200, 300)])
    container.corner_released(_global(container, 200, 300))
    application.processEvents()

    assert _settings(container) == {1: 5, 5: 5, 2: 7, 4: 7, 3: 9}


def test_a_split_is_refused_where_a_half_could_not_hold_its_header(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    """`PL-30L5` Q2: below the header row and one line of a notice, a half is refused."""

    container = _show(application, shown, LayoutModel.single_area(_VIEW), size=(800, 40))
    stacked = _operation(container, 1, SPLIT_STACKED_LABEL)

    assert not stacked.available
    assert "too small to hold its header" in stacked.refusal
    assert _operation(container, 1, SPLIT_SIDE_BY_SIDE_LABEL).available

    with pytest.raises(ValueError, match="unavailable"):
        container.perform(stacked)

    assert container.model == LayoutModel.single_area(_VIEW)


def test_a_lone_area_can_be_split_and_nothing_else(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    container = _show(application, shown, LayoutModel.single_area(_VIEW), size=(800, 600))

    assert _labels(container, 1) == [
        (None, SPLIT_SIDE_BY_SIDE_LABEL, True),
        (None, SPLIT_STACKED_LABEL, True),
        (None, CLOSE_AREA_LABEL, False),
    ]
    assert "only Area" in _operation(container, 1, CLOSE_AREA_LABEL).refusal


def test_the_drawn_menu_disables_each_unavailable_entry_and_says_why(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    """The reader sees the entry, greyed, with its reason as the tooltip."""

    container = _show(application, shown, _LEFT_AND_STACK, size=(800, 600))
    button = container.frame(AreaId(1)).menu
    assert button is not None
    button.fill()
    menu = button.menu()
    top = {action.text(): action for action in menu.actions()}

    assert list(top) == [
        SPLIT_SIDE_BY_SIDE_LABEL,
        SPLIT_STACKED_LABEL,
        JOIN_WITH_LABEL,
        SWAP_WITH_LABEL,
        CLOSE_AREA_LABEL,
    ]
    assert not top[CLOSE_AREA_LABEL].isEnabled()
    assert "none can take its place" in top[CLOSE_AREA_LABEL].toolTip()

    join = top[JOIN_WITH_LABEL].menu()
    assert join is not None
    assert [action.isEnabled() for action in join.actions()] == [False, False]
    assert all("whole edge" in action.toolTip() for action in join.actions())

    swap = top[SWAP_WITH_LABEL].menu()
    assert swap is not None
    swap.actions()[0].trigger()
    application.processEvents()

    assert container.model == _layout(
        _row((0.5, 0.5), _area(2), _column((0.5, 0.5), _area(1), _area(3))), 4
    )


def test_a_lone_areas_drawn_menu_shows_join_and_swap_unavailable(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    container = _show(application, shown, LayoutModel.single_area(_VIEW), size=(800, 600))
    button = container.frame(AreaId(1)).menu
    assert button is not None
    button.fill()
    top = {action.text(): action for action in button.menu().actions()}

    assert not top[JOIN_WITH_LABEL].isEnabled()
    assert not top[SWAP_WITH_LABEL].isEnabled()


# ------------------------------------------------------------ the corner drag


def _global(container: AreaLayout, x: int, y: int) -> QPoint:
    return container.mapToGlobal(QPoint(x, y))


def _corner_drag(container: AreaLayout, area: int, path: list[tuple[int, int]]) -> None:
    """Press in Area `area`'s top-left corner and move through `path`, in container pixels."""

    corner = container.frame_rect(AreaId(area)).topLeft() + QPoint(4, 4)
    container.corner_pressed(AreaId(area), container.mapToGlobal(corner))

    for x, y in path:
        container.corner_moved(_global(container, x, y))


def test_each_area_has_a_zone_at_every_corner_that_shows_a_grip_only_while_the_pointer_is_in_it(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    """`PL-30L5` Q1: a cross cursor over a 16 px zone, and a grip only in the Area being handled."""

    from anesthesia_sim.app.theme import AREA_CORNER_ZONE

    container = _show(application, shown, _LEFT_AND_STACK, size=(800, 600))
    frame = container.frame(AreaId(1))

    assert len(frame.corners) == 4
    assert {(zone.x(), zone.y()) for zone in frame.corners} == {
        (0, 0),
        (frame.width() - AREA_CORNER_ZONE, 0),
        (0, frame.height() - AREA_CORNER_ZONE),
        (frame.width() - AREA_CORNER_ZONE, frame.height() - AREA_CORNER_ZONE),
    }
    assert all(zone.cursor().shape() == Qt.CursorShape.CrossCursor for zone in frame.corners)

    QApplication.sendEvent(frame, QEvent(QEvent.Type.Leave))

    assert not any(zone.grip_shown for zone in frame.corners)

    QApplication.sendEvent(
        frame,
        QEnterEvent(QPointF(50, 50), QPointF(50, 50), QPointF(frame.mapToGlobal(QPoint(50, 50)))),
    )

    assert all(zone.grip_shown for zone in frame.corners)
    assert not any(zone.grip_shown for zone in container.frame(AreaId(2)).corners)

    QApplication.sendEvent(frame, QEvent(QEvent.Type.Leave))

    assert not any(zone.grip_shown for zone in frame.corners)


def test_a_header_control_starts_after_the_corner_zone(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    """The zone must not take the chooser's first click (`PL-30L5` Q1)."""

    from anesthesia_sim.app.theme import AREA_CORNER_ZONE

    container = _show(application, shown, _LEFT_AND_STACK, size=(800, 600))
    frame = container.frame(AreaId(1))
    assert frame.menu is not None

    assert frame.chooser.mapTo(frame, QPoint(0, 0)).x() >= AREA_CORNER_ZONE
    assert frame.menu.mapTo(frame, QPoint(frame.menu.width(), 0)).x() <= (
        frame.width() - AREA_CORNER_ZONE
    )


def test_a_corner_drag_inside_its_area_previews_the_split_and_makes_it_on_release(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    """A sideways drag cuts left and right through the pointer; nothing changes until release."""

    container = _show(application, shown, LayoutModel.single_area(_VIEW), size=(800, 600))
    before = container.model

    _corner_drag(container, 1, [(100, 50), (200, 60)])
    preview = container.preview

    assert isinstance(preview, SplitPreview)
    assert preview.orientation is Orientation.ROW
    assert preview.at == pytest.approx(200 / 800)
    assert preview.result is not None
    assert container.model == before

    container.corner_released(_global(container, 200, 60))
    application.processEvents()

    assert container.model == _layout(_row((0.25, 0.75), _area(1), _area(2)), 3)
    assert container.preview is None


def test_a_downward_corner_drag_previews_a_cut_into_top_and_bottom(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    container = _show(application, shown, LayoutModel.single_area(_VIEW), size=(800, 600))

    _corner_drag(container, 1, [(30, 300)])
    preview = container.preview

    assert isinstance(preview, SplitPreview)
    assert preview.orientation is Orientation.COLUMN
    assert preview.at == pytest.approx(300 / 600)


def test_a_split_too_close_to_an_edge_is_previewed_refused_and_release_does_nothing(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    """`PL-30L5` Q2: below the header and a line of text, the line turns WARNING."""

    container = _show(application, shown, LayoutModel.single_area(_VIEW), size=(800, 600))
    before = container.model

    _corner_drag(container, 1, [(30, 20)])
    preview = container.preview

    assert isinstance(preview, SplitPreview)
    assert preview.result is None

    container.corner_released(_global(container, 30, 20))
    application.processEvents()

    assert container.model == before


def test_a_corner_drag_into_a_neighbour_previews_the_join_and_makes_it_on_release(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    """The Area dragged from keeps its View and takes the other's place."""

    container = _show(application, shown, _LEFT_AND_STACK, size=(800, 600))
    lower = container.frame_rect(AreaId(3)).center()
    corner = container.frame_rect(AreaId(2)).topLeft() + QPoint(4, 4)
    container.corner_pressed(AreaId(2), container.mapToGlobal(corner))
    container.corner_moved(container.mapToGlobal(lower))
    preview = container.preview

    assert isinstance(preview, JoinPreview)
    assert (preview.keep, preview.remove) == (AreaId(2), AreaId(3))
    assert preview.result is not None

    container.corner_released(container.mapToGlobal(lower))
    application.processEvents()

    assert container.model == _layout(_row((0.5, 0.5), _area(1), _area(2)), 4)


def test_a_join_the_layout_cannot_make_is_previewed_refused_and_release_does_nothing(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    """Area 1 meets Area 2 along only part of its edge, so the two cannot be joined."""

    container = _show(application, shown, _LEFT_AND_STACK, size=(800, 600))
    before = container.model
    upper = container.frame_rect(AreaId(2)).center()
    _corner_drag(container, 1, [])
    container.corner_moved(container.mapToGlobal(upper))
    preview = container.preview

    assert isinstance(preview, JoinPreview)
    assert preview.result is None

    container.corner_released(container.mapToGlobal(upper))
    application.processEvents()

    assert container.model == before


def test_escape_cancels_a_corner_drag_and_changes_nothing(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    """Driven through the zone itself, with the mouse and the keyboard."""

    container = _show(application, shown, LayoutModel.single_area(_VIEW), size=(800, 600))
    before = container.model
    (zone,) = [
        zone for zone in container.frame(AreaId(1)).corners if (zone.x(), zone.y()) == (0, 0)
    ]

    QTest.mousePress(zone, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, QPoint(4, 4))
    QTest.mouseMove(zone, QPoint(200, 60))
    application.processEvents()

    assert isinstance(container.preview, SplitPreview)

    QTest.keyClick(zone, Qt.Key.Key_Escape)
    QTest.mouseRelease(
        zone, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, QPoint(200, 60)
    )
    application.processEvents()

    assert container.preview is None
    assert container.model == before


def test_a_drag_through_the_zone_with_the_mouse_makes_the_split(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    container = _show(application, shown, LayoutModel.single_area(_VIEW), size=(800, 600))
    (zone,) = [
        zone for zone in container.frame(AreaId(1)).corners if (zone.x(), zone.y()) == (0, 0)
    ]

    QTest.mousePress(zone, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, QPoint(4, 4))
    QTest.mouseMove(zone, QPoint(400, 60))
    QTest.mouseRelease(
        zone, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, QPoint(400, 60)
    )
    application.processEvents()

    assert container.model == _layout(_row((0.5, 0.5), _area(1), _area(2)), 3)


def test_the_overlay_draws_the_split_line_in_primary_and_a_refused_one_in_warning(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    from anesthesia_sim.app.theme import WARNING

    container = _show(application, shown, LayoutModel.single_area(_VIEW), size=(800, 600))

    _corner_drag(container, 1, [(200, 60)])
    painted = container.grab().toImage()

    assert painted.pixelColor(200, 300).name().upper() == PRIMARY.upper()

    _corner_drag(container, 1, [(30, 20)])
    painted = container.grab().toImage()

    assert painted.pixelColor(30, 300).name().upper() == WARNING.upper()
    container.corner_cancelled()


# ------------------------------------------- an Area too small for its View

_BIG = ViewKind("big_view")


class _BigView(_TestView):
    """The View of `_BIG`, whose registry entry declares a minimum of 300 by 200 px."""


# The test View and one that declares a minimum, so a test can tell an Area
# held at its View's need from one held only at its header.
_SIZED = registry(
    RegisteredView(_VIEW, "Test view", _TestView),
    RegisteredView(_BIG, "Big view", _BigView, minimum=PixelSize(300, 200)),
)

# Under its header, a View is drawn below the header row and the 1 px rule.
_CHROME_PX = 27


def _show_sized(
    application: QApplication, shown: list[AreaLayout], model: LayoutModel, size: tuple[int, int]
) -> AreaLayout:
    container = AreaLayout(model, _REQUESTS, registered=_SIZED, retired={})
    container.resize(*size)
    container.show()
    application.processEvents()
    shown.append(container)

    return container


@pytest.fixture
def hosts(application: QApplication) -> Iterator[list[QWidget]]:
    """Every host a test shows a container in, closed after it."""

    shown_hosts: list[QWidget] = []
    yield shown_hosts

    for host in shown_hosts:
        host.close()
        host.deleteLater()

    application.processEvents()


def _host_sized(
    application: QApplication, hosts: list[QWidget], model: LayoutModel, size: tuple[int, int]
) -> tuple[QWidget, AreaLayout]:
    """Show `model` filling a window held at `size`, as a screen too small for it holds one.

    The window cannot grow to the layout's least size, so the layout is
    given less than its Areas need.
    """

    host = QWidget()
    column = QVBoxLayout(host)
    column.setContentsMargins(0, 0, 0, 0)
    container = AreaLayout(model, _REQUESTS, registered=_SIZED, retired={})
    column.addWidget(container)
    host.setFixedSize(*size)
    host.show()
    application.processEvents()
    hosts.append(host)

    return host, container


def _too_small_texts(width_px: int, height_px: int) -> list[str]:
    """The notice's two lines for a Big view in an Area `width_px` by `height_px` under its header.

    Written out here rather than read from the module that writes them
    (`PL-DB5G` Q3).
    """

    return [
        "Too small for Big view.",
        f"It needs at least 300 by 200 px; this Area is {width_px} by {height_px}. "
        "Drag a border to enlarge it, or choose a smaller View from the menu above.",
    ]


def test_the_header_and_the_rule_are_the_chrome_these_tests_allow_for(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    container = _show_sized(application, shown, LayoutModel.single_area(_BIG), (608, 600))
    frame = container.frame(AreaId(1))

    assert frame.content.geometry().top() == _CHROME_PX
    assert frame.content.height() == 600 - _CHROME_PX


def test_a_split_into_halves_too_small_shows_the_size_the_view_needs_and_nothing_else(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    """`PL-30L5` Q2: the split is allowed, and each half states what it lacks (`PL-DB5G` Q4).

    500 px less the 8 px handle leaves two halves of 246 px, short of the
    View's 300. Each View is hidden, not deleted, and no Area shows a value.
    """

    container = _show_sized(application, shown, LayoutModel.single_area(_BIG), (500, 600))
    operation = _operation(container, 1, SPLIT_SIDE_BY_SIDE_LABEL)
    assert operation.available

    container.perform(operation)
    application.processEvents()

    assert _splitters(container)[()].sizes() == [246, 246]
    assert [entry.area_id for entry in container.too_small()] == [AreaId(1), AreaId(2)]

    for area_id in (AreaId(1), AreaId(2)):
        frame = container.frame(area_id)
        assert not frame.content.isVisible()
        assert _texts(frame) == _too_small_texts(246, 600 - _CHROME_PX)

    assert len(_BUILT) == 2


def test_the_notice_restates_the_size_as_the_area_grows_and_clears_once_it_is_enough(
    application: QApplication, hosts: list[QWidget]
) -> None:
    """At 560 px each half is 276; at 608 px each is the 300 the View needs, and draws it."""

    model = _layout(_row((0.5, 0.5), Area(AreaId(1), _BIG), Area(AreaId(2), _BIG)), 3)
    host, container = _host_sized(application, hosts, model, (500, 600))
    first = container.frame(AreaId(1))
    assert _texts(first) == _too_small_texts(246, 600 - _CHROME_PX)

    host.setFixedSize(560, 600)
    application.processEvents()

    assert _texts(first) == _too_small_texts(276, 600 - _CHROME_PX)

    host.setFixedSize(608, 600)
    application.processEvents()

    assert container.too_small() == ()
    assert _splitters(container)[()].sizes() == [300, 300]
    assert first.content.isVisible() and _texts(first) == []
    assert container.model == model


def test_a_drag_stops_where_the_neighbour_reaches_its_views_declared_need(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    """`PL-K285` Q1: a drag cannot make an Area too small for the View it draws.

    The right-hand Area's View needs 300 px. A drag of 200 px right from the
    middle of 800 px would leave it 200, so the border stops with it at 300.
    """

    model = _layout(_row((0.5, 0.5), _area(1), Area(AreaId(2), _BIG)), 3)
    container = _show_sized(application, shown, model, (_SIDE_PX, 600))

    _drag(application, _splitters(container)[()], 1, 200)

    # The border stops the handle's width short of the Area's need, as
    # `PL-RQT1` Q3's stop does for any neighbour.
    assert container.model.position(Handle(0, (), 0)) == pytest.approx(
        1 - (300 + AREA_HANDLE_WIDTH) / _SIDE_PX, abs=1e-5
    )
    assert _splitters(container)[()].sizes()[1] >= 300
    assert container.too_small() == ()


def test_a_view_chosen_for_an_area_too_small_for_it_is_shown_as_too_small(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    """`PL-K285` Q3: choosing it is allowed, and the Area states the size it needs.

    Each half of 392 px is 196. The Big view needs 300, which would leave
    its neighbour less than its header, so the neighbour keeps its View and
    the chosen one is too small.
    """

    model = _layout(_row((0.5, 0.5), _area(1), _area(2)), 3)
    container = _show_sized(application, shown, model, (400, 600))

    container.choose_view(AreaId(2), _BIG)
    application.processEvents()

    assert [(entry.area_id, entry.needed) for entry in container.too_small()] == [
        (AreaId(2), PixelSize(300, 200 + _CHROME_PX))
    ]
    assert _texts(container.frame(AreaId(2))) == _too_small_texts(196, 600 - _CHROME_PX)
    assert container.frame(AreaId(1)).content.isVisible()
    assert _splitters(container)[()].sizes() == [196, 196]


def test_a_neighbour_gives_way_to_hold_a_chosen_view_at_its_need(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    """Where the neighbour can give the room and keep its header, it does, and the model stays."""

    model = _layout(_row((0.5, 0.5), _area(1), _area(2)), 3)
    container = _show_sized(application, shown, model, (_SIDE_PX, 600))

    container.choose_view(AreaId(2), _BIG)
    application.processEvents()

    assert container.too_small() == ()
    assert _splitters(container)[()].sizes() == [400, 400]

    container.resize(600, 600)
    application.processEvents()

    # 592 px between them: the Big view keeps its 300 and the other takes the rest.
    assert _splitters(container)[()].sizes() == [292, 300]
    assert container.model == model.set_view(AreaId(2), _BIG)


def test_a_layout_opened_in_a_window_too_small_for_it_draws_no_area_below_its_header(
    application: QApplication, hosts: list[QWidget]
) -> None:
    """`PL-K285` Q2: no Area is drawn at a zero or clipped size, and each says what it lacks.

    At 400 by 300 px no Big view can have its 300 by 227, so each is too
    small.
    """

    _, container = _host_sized(application, hosts, LayoutModel.single_area(_VIEW), (400, 300))
    model = _layout(
        _column(
            (0.5, 0.5),
            _row((0.5, 0.5), Area(AreaId(1), _BIG), Area(AreaId(2), _BIG)),
            Area(AreaId(3), _BIG),
        ),
        4,
    )

    container.set_model(model)
    application.processEvents()

    assert (container.width(), container.height()) == (400, 300)
    assert {entry.area_id for entry in container.too_small()} == {AreaId(1), AreaId(2), AreaId(3)}

    for area_id in (AreaId(1), AreaId(2), AreaId(3)):
        frame = container.frame(area_id)
        assert frame.width() >= frame.minimumWidth() > 0
        assert frame.height() >= frame.minimumHeight() > 0
        assert not frame.content.isVisible()


def test_a_layout_in_a_scrolling_page_makes_the_page_the_size_its_areas_need(
    application: QApplication, hosts: list[QWidget]
) -> None:
    """`PL-K285` Q2: no Area is too small where its host can grow, as the dashboard's page does.

    The page fills a 400 px viewport until the layout needs more. Two Big
    views side by side need 608 px, so the page grows to that and scrolls.
    """

    page = QScrollArea()
    page.setWidgetResizable(True)
    container = AreaLayout(LayoutModel.single_area(_VIEW), _REQUESTS, registered=_SIZED, retired={})
    page.setWidget(container)
    page.resize(400, 400)
    page.show()
    application.processEvents()
    hosts.append(page)

    container.set_model(_layout(_row((0.5, 0.5), Area(AreaId(1), _BIG), Area(AreaId(2), _BIG)), 3))
    application.processEvents()

    assert container.too_small() == ()
    assert container.width() == 608
    assert _splitters(container)[()].sizes() == [300, 300]


def test_the_least_size_of_the_layout_is_the_sum_of_what_its_areas_need(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    """`PL-K285` Q4: Qt's minimum is the model's, so the window cannot be made smaller.

    Two Big views side by side need 300 + 8 + 300 px across. Each Big view
    needs 200 px and the 27 px header and rule, so the column needs two of
    those with the handle between them.
    """

    model = _layout(
        _column(
            (0.5, 0.5),
            _row((0.5, 0.5), Area(AreaId(1), _BIG), Area(AreaId(2), _BIG)),
            Area(AreaId(3), _BIG),
        ),
        4,
    )
    container = _show_sized(application, shown, model, (_SIDE_PX, _SIDE_PX))
    need = 200 + _CHROME_PX

    assert container.minimum_extent() == PixelSize(608, 2 * need + AREA_HANDLE_WIDTH)
    hint = container.minimumSizeHint()
    assert (hint.width(), hint.height()) == (608, 2 * need + AREA_HANDLE_WIDTH)


def test_the_least_size_is_what_the_views_need_even_where_their_areas_are_too_small(
    application: QApplication, hosts: list[QWidget]
) -> None:
    """A host that cannot give the room is still told how much would draw every View."""

    model = _layout(_row((0.5, 0.5), Area(AreaId(1), _BIG), Area(AreaId(2), _BIG)), 3)
    _, container = _host_sized(application, hosts, model, (500, 600))

    assert len(container.too_small()) == 2
    hint = container.minimumSizeHint()
    assert (hint.width(), hint.height()) == (608, 200 + _CHROME_PX)
