"""The adapter between the layout model and the widgets, driven headless.

`app/area_layout.py` is the one module that builds splitters (`PL-W9P6`).
These tests hold what it promises: each split in the model is a splitter and
each Area its View, the splitters take the model's sizes, a reader's drag
changes the model and every widget follows the model, and a layout the model
refuses changes nothing. Each expected size is worked out here from the
pixels, never read back from the adapter. They render under the `offscreen`
platform `tests/conftest.py` selects.
"""

from collections.abc import Iterator

import pytest
from PySide6.QtCore import QEvent, QPoint, QPointF, Qt
from PySide6.QtGui import QEnterEvent, QImage
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QSplitter, QWidget

from anesthesia_sim.app.area_layout import AreaLayout
from anesthesia_sim.app.theme import AREA_HANDLE_LINE_WIDTH, AREA_HANDLE_WIDTH, PRIMARY
from anesthesia_sim.layout.model import Handle, LayoutModel
from anesthesia_sim.layout.tree import Area, AreaId, Node, Orientation, Split, ViewKind, Window

_VIEW = ViewKind("test_view")

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


class _Views:
    """Hands each Area a plain widget, the same one each time it is asked."""

    def __init__(self) -> None:
        self.by_id: dict[int, QWidget] = {}
        self.asked: list[int] = []

    def __call__(self, area: Area) -> QWidget:
        self.asked.append(area.id)
        view = self.by_id.get(area.id)

        if view is None:
            view = QWidget()
            view.setObjectName(f"view{area.id}")
            # Small enough that Qt's own minimum never stops a drag here.
            view.setMinimumSize(10, 10)
            self.by_id[area.id] = view

        return view


@pytest.fixture(scope="module")
def application() -> Iterator[QApplication]:
    existing = QApplication.instance()

    yield existing if isinstance(existing, QApplication) else QApplication([])


@pytest.fixture
def views() -> _Views:
    return _Views()


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
    views: _Views,
    size: tuple[int, int] = (_SIDE_PX, _SIDE_PX),
) -> AreaLayout:
    container = AreaLayout(model, views)
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
    application: QApplication, shown: list[AreaLayout], views: _Views
) -> None:
    """A column holding a row of Areas 1 and 2 above Area 3 is two splitters, nested."""

    model = _layout(_column((0.5, 0.5), _row((0.5, 0.5), _area(1), _area(2)), _area(3)), 4)
    container = _show(application, shown, model, views)
    splitters = _splitters(container)

    assert set(splitters) == {(), (0,)}
    assert splitters[()].orientation() == Qt.Orientation.Vertical
    assert splitters[(0,)].orientation() == Qt.Orientation.Horizontal
    assert splitters[()].widget(0) is splitters[(0,)]
    assert splitters[()].widget(1) is views.by_id[3]
    assert splitters[(0,)].widget(0) is views.by_id[1]
    assert splitters[(0,)].widget(1) is views.by_id[2]
    assert sorted(views.asked) == [1, 2, 3]


def test_every_handle_is_live_and_no_area_can_be_dragged_to_nothing(
    application: QApplication, shown: list[AreaLayout], views: _Views
) -> None:
    """The handles v0.4.26 built inert are enabled, the width `PL-RQT1` set, with split cursors."""

    model = _layout(_column((0.5, 0.5), _row((0.5, 0.5), _area(1), _area(2)), _area(3)), 4)
    splitters = _splitters(_show(application, shown, model, views))
    cursors = {(): Qt.CursorShape.SplitVCursor, (0,): Qt.CursorShape.SplitHCursor}

    for path, splitter in splitters.items():
        assert not splitter.childrenCollapsible()
        assert splitter.handleWidth() == AREA_HANDLE_WIDTH
        assert splitter.handle(1).isEnabled()
        assert splitter.handle(1).cursor().shape() == cursors[path]


def test_a_layout_of_one_area_is_its_view_alone(
    application: QApplication, shown: list[AreaLayout], views: _Views
) -> None:
    container = _show(application, shown, LayoutModel.single_area(_VIEW), views)

    assert _splitters(container) == {}
    assert views.by_id[1].parentWidget() is container
    assert views.by_id[1].isVisible()


def test_the_splitters_take_the_sizes_the_model_holds(
    application: QApplication, shown: list[AreaLayout], views: _Views
) -> None:
    """A quarter and three quarters of 400 px are 100 px and 300 px."""

    container = _show(application, shown, _layout(_row((0.25, 0.75), _area(1), _area(2)), 3), views)

    assert _splitters(container)[()].sizes() == [100, 300]


def test_a_layout_of_two_windows_is_refused(views: _Views) -> None:
    """This build opens one window, so an Area in a second would not be drawn at all."""

    model = LayoutModel((Window(_area(1)), Window(_area(2))), AreaId(3))

    with pytest.raises(ValueError, match="draws one window, and the layout holds 2"):
        AreaLayout(model, views)


# --------------------------------------------------------- a reader's drag


def test_a_drag_on_a_border_changes_the_layout_model(
    application: QApplication, shown: list[AreaLayout], views: _Views
) -> None:
    """Dragging the border 100 px right of the middle of 400 px leaves it three quarters across."""

    container = _show(application, shown, _layout(_row((0.5, 0.5), _area(1), _area(2)), 3), views)
    changed: list[LayoutModel] = []
    container.layout_changed.connect(changed.append)

    _drag(application, _splitters(container)[()], 1, 100)

    tree = _tree(container)
    assert isinstance(tree, Split)
    assert tree.sizes == pytest.approx((0.75, 0.25), abs=1 / 400)
    assert changed == [container.model]
    assert _splitters(container)[()].sizes() == [300, 100]


def test_a_drag_moves_every_handle_on_the_dragged_line(
    application: QApplication, shown: list[AreaLayout], views: _Views
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
    container = _show(application, shown, model, views)
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
    application: QApplication, shown: list[AreaLayout], views: _Views
) -> None:
    """The bottom border, at 0.7, is not on the top border's line at 0.5, so it stays."""

    model = _layout(
        _column(
            (0.5, 0.5), _row((0.5, 0.5), _area(1), _area(2)), _row((0.7, 0.3), _area(3), _area(4))
        ),
        5,
    )
    container = _show(application, shown, model, views)
    splitters = _splitters(container)

    _drag(application, splitters[(0,)], 1, -100)

    tree = _tree(container)
    assert isinstance(tree, Split)
    bottom = tree.children[1]
    assert isinstance(bottom, Split)
    assert bottom.sizes == (0.7, 0.3)
    assert splitters[(1,)].sizes() == [280, 120]


def test_a_drag_the_model_refuses_changes_nothing(
    application: QApplication, shown: list[AreaLayout], views: _Views
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
    container = _show(application, shown, model, views)
    changed: list[LayoutModel] = []
    container.layout_changed.connect(changed.append)
    splitters = _splitters(container)

    _drag(application, splitters[(0,)], 1, 100)

    assert container.model == model
    assert changed == []
    assert splitters[(0,)].sizes() == [200, 200]


def test_a_resize_keeps_the_fractions_and_changes_no_model(
    application: QApplication, shown: list[AreaLayout], views: _Views
) -> None:
    """After a drag to three quarters, a window twice as wide draws 600 px and 200 px."""

    container = _show(application, shown, _layout(_row((0.5, 0.5), _area(1), _area(2)), 3), views)
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
    application: QApplication, shown: list[AreaLayout], views: _Views
) -> None:
    container = _show(application, shown, _layout(_row((0.5, 0.5), _area(1), _area(2)), 3), views)
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
    assert views.asked == [1, 2]


def test_a_swap_moves_each_view_to_the_other_area(
    application: QApplication, shown: list[AreaLayout], views: _Views
) -> None:
    """The splitters are built again, and each View is moved, not made again."""

    container = _show(application, shown, _layout(_row((0.25, 0.75), _area(1), _area(2)), 3), views)
    first, second = views.by_id[1], views.by_id[2]

    container.set_model(container.model.swap(AreaId(1), AreaId(2)))
    application.processEvents()
    splitter = _splitters(container)[()]

    assert splitter.widget(0) is second
    assert splitter.widget(1) is first
    assert first.isVisible() and second.isVisible()
    assert splitter.sizes() == [100, 300]


def test_a_view_the_new_layout_does_not_hold_leaves_the_container(
    application: QApplication, shown: list[AreaLayout], views: _Views
) -> None:
    """Joining Area 2 into Area 1 leaves one View; the other is handed back unparented."""

    container = _show(application, shown, _layout(_row((0.5, 0.5), _area(1), _area(2)), 3), views)
    removed = views.by_id[2]

    container.set_model(container.model.join(AreaId(1), AreaId(2)))
    application.processEvents()

    assert _splitters(container) == {}
    assert views.by_id[1].parentWidget() is container
    assert removed.parentWidget() is None


# ------------------------------------------------------------- the handle


def test_a_handle_draws_nothing_at_rest_and_lights_its_whole_line_under_the_pointer(
    application: QApplication, shown: list[AreaLayout], views: _Views
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
    splitters = _splitters(_show(application, shown, model, views))
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
