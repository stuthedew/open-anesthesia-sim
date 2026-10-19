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
from PySide6.QtWidgets import QApplication, QLabel, QSplitter, QWidget

from anesthesia_sim.app.area_layout import AreaFrame, AreaLayout, AreaNotice, ViewChooser
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

# A container this size leaves 400 px for the children of a split of two, once
# the 8 px handle is taken out, so a fraction reads straight off as pixels.
_SIDE_PX = 400 + AREA_HANDLE_WIDTH


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
    """A quarter and three quarters of 400 px are 100 px and 300 px."""

    container = _show(application, shown, _layout(_row((0.25, 0.75), _area(1), _area(2)), 3))

    assert _splitters(container)[()].sizes() == [100, 300]


def test_a_layout_of_two_windows_is_refused() -> None:
    """This build opens one window, so an Area in a second would not be drawn at all."""

    model = LayoutModel((Window(_area(1)), Window(_area(2))), AreaId(3))

    with pytest.raises(ValueError, match="draws one window, and the layout holds 2"):
        AreaLayout(model, _REQUESTS, registered=_REGISTERED)


# --------------------------------------------------------- a reader's drag


def test_a_drag_on_a_border_changes_the_layout_model(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    """Dragging the border 100 px right of the middle of 400 px leaves it three quarters across."""

    container = _show(application, shown, _layout(_row((0.5, 0.5), _area(1), _area(2)), 3))
    changed: list[LayoutModel] = []
    container.layout_changed.connect(changed.append)

    _drag(application, _splitters(container)[()], 1, 100)

    tree = _tree(container)
    assert isinstance(tree, Split)
    assert tree.sizes == pytest.approx((0.75, 0.25), abs=1 / 400)
    assert changed == [container.model]
    assert _splitters(container)[()].sizes() == [300, 100]


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

    _drag(application, splitters[(0,)], 1, -100)

    tree = _tree(container)
    assert isinstance(tree, Split)

    for row in tree.children:
        assert isinstance(row, Split)
        assert row.sizes == pytest.approx((0.25, 0.75), abs=1 / 400)

    assert splitters[(0,)].sizes() == [100, 300]
    assert splitters[(1,)].sizes() == [100, 300]


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

    _drag(application, splitters[(0,)], 1, -100)

    tree = _tree(container)
    assert isinstance(tree, Split)
    bottom = tree.children[1]
    assert isinstance(bottom, Split)
    assert bottom.sizes == (0.7, 0.3)
    assert splitters[(1,)].sizes() == [280, 120]


def test_a_drag_the_model_refuses_changes_nothing(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    """Dragging the top border to 0.75 would carry the bottom one past its neighbour at 0.6.

    The bottom row's first border is on the top border's line, so it moves
    with it, and moving it to 0.75 would leave Area 4, between 0.5 and 0.6,
    with no width. The model refuses the drag, so neither the model nor the
    dragged splitter changes, and nothing is announced.
    """

    model = _layout(
        _column(
            (0.5, 0.5),
            _row((0.5, 0.5), _area(1), _area(2)),
            _row((0.5, 0.1, 0.4), _area(3), _area(4), _area(5)),
        ),
        6,
    )
    container = _show(application, shown, model)
    changed: list[LayoutModel] = []
    container.layout_changed.connect(changed.append)
    splitters = _splitters(container)

    _drag(application, splitters[(0,)], 1, 100)

    assert container.model == model
    assert changed == []
    assert splitters[(0,)].sizes() == [200, 200]


def test_a_resize_keeps_the_fractions_and_changes_no_model(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    """After a drag to three quarters, a window twice as wide draws 600 px and 200 px."""

    container = _show(application, shown, _layout(_row((0.5, 0.5), _area(1), _area(2)), 3))
    _drag(application, _splitters(container)[()], 1, 100)
    dragged = container.model
    changed: list[LayoutModel] = []
    container.layout_changed.connect(changed.append)

    container.resize(800 + AREA_HANDLE_WIDTH, _SIDE_PX)
    application.processEvents()

    assert container.model == dragged
    assert changed == []
    assert _splitters(container)[()].sizes() == [600, 200]


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
    assert splitter.sizes() == [100, 300]
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
    assert splitter.sizes() == [100, 300]
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
        [RunInput(run_label(0), controller, snapshot, ())],
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
