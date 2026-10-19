"""The adapter between the layout model and the widgets, driven headless.

`app/area_layout.py` is the one module that builds splitters (`PL-W9P6`).
These tests hold what it promises: each split in the model is a splitter and
each Area its View, the splitters take the model's sizes, a reader's drag
changes the model and every widget follows the model, and a layout the model
refuses changes nothing. An Area whose View kind the registry does not hold
shows the failure notice and nothing else, while its neighbours draw as usual
(`PL-R1WQ`). Each expected size is worked out here from the
pixels, never read back from the adapter. They render under the `offscreen`
platform `tests/conftest.py` selects.
"""

from collections.abc import Callable, Iterator, Mapping

import pytest
from PySide6.QtCore import QEvent, QPoint, QPointF, Qt
from PySide6.QtGui import QEnterEvent, QImage
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QLabel, QSplitter, QWidget

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
    ViewChooser,
)
from anesthesia_sim.app.theme import AREA_HANDLE_LINE_WIDTH, AREA_HANDLE_WIDTH, PRIMARY
from anesthesia_sim.app.view_registry import RegisteredView, RetiredTag, registry, retirements
from anesthesia_sim.layout.model import Handle, LayoutModel
from anesthesia_sim.layout.tree import Area, AreaId, Node, Orientation, Split, ViewKind, Window

_VIEW = ViewKind("test_view")
_UNKNOWN = ViewKind("retired_view")

# The tests draw a View kind of their own, so they register it themselves.
_REGISTERED = registry(RegisteredView(_VIEW, "Test view"))

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
    container = AreaLayout(model, views, registered=_REGISTERED)
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
    assert _content(splitters[()].widget(1)) is views.by_id[3]
    assert _content(splitters[(0,)].widget(0)) is views.by_id[1]
    assert _content(splitters[(0,)].widget(1)) is views.by_id[2]
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
    assert views.by_id[1].parentWidget() is container.frame(AreaId(1))
    assert container.frame(AreaId(1)).parentWidget() is container
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
        AreaLayout(model, views, registered=_REGISTERED)


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

    assert _content(splitter.widget(0)) is second
    assert _content(splitter.widget(1)) is first
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
    assert views.by_id[1].parentWidget() is container.frame(AreaId(1))
    assert removed.parentWidget() is None


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
    application: QApplication, shown: list[AreaLayout], views: _Views
) -> None:
    """The middle Area of three fails alone, and its neighbours draw their Views."""

    model = _layout(_row((0.25, 0.5, 0.25), _area(1), Area(AreaId(2), _UNKNOWN), _area(3)), 4)
    container = _show(application, shown, model, views, (800 + 2 * AREA_HANDLE_WIDTH, 400))
    splitter = _splitters(container)[()]
    notice = _content(splitter.widget(1))

    assert _content(splitter.widget(0)) is views.by_id[1]
    assert _content(splitter.widget(2)) is views.by_id[3]
    assert isinstance(notice, AreaNotice)
    assert notice.isVisible()
    assert _texts(notice) == [_NOTICE_TITLE, _NOTICE_BODY]
    assert views.asked == [1, 3]
    assert splitter.sizes() == [200, 400, 200]


def test_the_model_keeps_the_unknown_kind_so_a_save_writes_back_what_was_read(
    application: QApplication, shown: list[AreaLayout], views: _Views
) -> None:
    """A drag beside the failed Area changes its size and never its kind."""

    model = _layout(_row((0.5, 0.5), _area(1), Area(AreaId(2), _UNKNOWN)), 3)
    container = _show(application, shown, model, views)

    _drag(application, _splitters(container)[()], 1, 100)

    assert container.model.unknown_kinds(_REGISTERED.keys()) == (Area(AreaId(2), _UNKNOWN),)
    assert container.model != model


def test_a_layout_of_one_unknown_area_is_the_notice_alone(
    application: QApplication, shown: list[AreaLayout], views: _Views
) -> None:
    container = _show(application, shown, _layout(Area(AreaId(1), _UNKNOWN), 2), views)

    assert _splitters(container) == {}
    assert [type(child) for child in container.findChildren(AreaNotice)] == [AreaNotice]
    assert _texts(container) == [_NOTICE_TITLE, _NOTICE_BODY]
    assert views.asked == []


def test_a_rebuild_deletes_the_notices_the_old_layout_drew(
    application: QApplication, shown: list[AreaLayout], views: _Views
) -> None:
    """Replacing the failed Area's layout leaves no notice behind, not even a hidden one."""

    model = _layout(_row((0.5, 0.5), _area(1), Area(AreaId(2), _UNKNOWN)), 3)
    container = _show(application, shown, model, views)

    container.set_model(_layout(_row((0.5, 0.5), _area(1), _area(2)), 3))
    application.processEvents()

    assert container.findChildren(AreaNotice) == []
    assert _content(_splitters(container)[()].widget(1)) is views.by_id[2]


def test_the_default_registry_holds_no_test_kind(application: QApplication, views: _Views) -> None:
    """Built with the shipped registry, the adapter draws a test-only kind as a failure."""

    container = AreaLayout(_layout(_area(1), 2), views)

    try:
        assert len(container.findChildren(AreaNotice)) == 1
        assert views.asked == []
    finally:
        container.deleteLater()


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


# ------------------------------------------------- the header and the chooser

_OTHER = ViewKind("other_view")
_THIRD = ViewKind("third_view")

# Three kinds, so the chooser's order and its one checked entry are told apart
# from an order or a check that only happens to match.
_THREE = registry(
    RegisteredView(_VIEW, "Test view"),
    RegisteredView(_OTHER, "Other view"),
    RegisteredView(_THIRD, "Third view"),
)


class _ViewsByKind(_Views):
    """Hands each Area a widget of its own for its kind, or None for `_THIRD`."""

    def __call__(self, area: Area) -> QWidget | None:  # type: ignore[override]
        if area.view == _THIRD:
            self.asked.append(area.id)
            return None

        return super().__call__(Area(AreaId(area.id * 10 + (area.view == _OTHER)), area.view))


def _show_with(
    application: QApplication,
    shown: list[AreaLayout],
    model: LayoutModel,
    view_for: Callable[[Area], QWidget | None],
    registered: Mapping[str, RegisteredView] = _THREE,
    retired: Mapping[str, RetiredTag] | None = None,
) -> AreaLayout:
    container = AreaLayout(
        model, view_for, registered=registered, retired={} if retired is None else retired
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
    container = _show_with(application, shown, model, _ViewsByKind())

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
    container = _show_with(application, shown, model, _ViewsByKind())

    assert _entries(container.frame(AreaId(1)).chooser) == [
        ("Test view", False),
        ("Other view", True),
        ("Third view", False),
    ]


def test_choosing_a_view_sets_it_in_that_area_and_nowhere_else(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    views = _ViewsByKind()
    model = _layout(_row((0.5, 0.5), Area(AreaId(1), _VIEW), Area(AreaId(2), _VIEW)), 3)
    container = _show_with(application, shown, model, views)
    changed: list[LayoutModel] = []
    container.layout_changed.connect(changed.append)
    kept = views.by_id[20]

    _pick(application, container.frame(AreaId(1)).chooser, "Other view")

    expected = _layout(_row((0.5, 0.5), Area(AreaId(1), _OTHER), Area(AreaId(2), _VIEW)), 3)
    assert container.model == expected
    assert changed == [expected]
    assert container.frame(AreaId(1)).content is views.by_id[11]
    assert container.frame(AreaId(1)).chooser.text() == "Other view"
    assert container.frame(AreaId(2)).content is kept
    assert views.by_id[10].parentWidget() is None


def test_choosing_the_view_already_shown_changes_nothing(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    views = _ViewsByKind()
    model = _layout(_row((0.5, 0.5), Area(AreaId(1), _VIEW), Area(AreaId(2), _OTHER)), 3)
    container = _show_with(application, shown, model, views)
    frame = container.frame(AreaId(1))
    changed: list[LayoutModel] = []
    container.layout_changed.connect(changed.append)

    _pick(application, frame.chooser, "Test view")

    assert container.model == model
    assert changed == []
    assert container.frame(AreaId(1)) is frame


# The notices' text, written out here rather than read from the module.
_UNPLACED_TITLE = "This View cannot be shown in an Area of its own yet."
_UNPLACED_BODY = (
    "This build cannot put 'Third view' in an Area yet. Choose a View from the menu above."
)
_ELSEWHERE_TITLE = "This View is already shown in another Area."
_ELSEWHERE_BODY = "This build draws one 'Test view' at a time. Choose a View from the menu above."


def test_a_view_the_caller_cannot_draw_yet_is_a_notice_in_its_area(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    """Choosing a registered kind with no widget to give shows a notice, not a crash."""

    views = _ViewsByKind()
    model = _layout(_row((0.5, 0.5), Area(AreaId(1), _VIEW), Area(AreaId(2), _OTHER)), 3)
    container = _show_with(application, shown, model, views)

    _pick(application, container.frame(AreaId(2)).chooser, "Third view")
    notice = container.frame(AreaId(2)).content

    assert isinstance(notice, AreaNotice)
    assert _texts(notice) == [_UNPLACED_TITLE, _UNPLACED_BODY]
    assert container.frame(AreaId(1)).content is views.by_id[10]
    assert container.model.area(AreaId(2)).view == _THIRD
    assert container.frame(AreaId(2)).chooser.text() == "Third view"


def test_one_widget_handed_out_for_two_areas_draws_in_the_first_and_a_notice_in_the_second(
    application: QApplication, shown: list[AreaLayout], views: _Views
) -> None:
    """A widget cannot sit in two places, so the second Area says why it shows no View."""

    single = QWidget()
    single.setMinimumSize(10, 10)
    model = _layout(_row((0.5, 0.5), _area(1), _area(2)), 3)
    container = _show_with(application, shown, model, lambda area: single)
    second = container.frame(AreaId(2)).content

    assert container.frame(AreaId(1)).content is single
    assert isinstance(second, AreaNotice)
    assert _texts(second) == [_ELSEWHERE_TITLE, _ELSEWHERE_BODY]


def test_an_unknown_kind_can_be_replaced_from_its_own_chooser(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    """The notice's chooser lists every kind, none checked, and a choice replaces the notice."""

    views = _ViewsByKind()
    model = _layout(_row((0.5, 0.5), Area(AreaId(1), _VIEW), Area(AreaId(2), _UNKNOWN)), 3)
    container = _show_with(application, shown, model, views)
    chooser = container.frame(AreaId(2)).chooser

    assert chooser.text() == "retired_view"
    assert [checked for _, checked in _entries(chooser)] == [False, False, False]

    _pick(application, chooser, "Other view")

    assert container.frame(AreaId(2)).content is views.by_id[21]
    assert container.findChildren(AreaNotice) == []


def test_a_renamed_kind_is_offered_its_new_tag_and_never_mapped_to_it(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    """`PL-R1WQ` Q3: the notice offers the rename, and only the reader's click takes it."""

    views = _ViewsByKind()
    retired = retirements(_THREE, RetiredTag(_UNKNOWN, "0.7.0", _OTHER))
    model = _layout(_row((0.5, 0.5), Area(AreaId(1), _VIEW), Area(AreaId(2), _UNKNOWN)), 3)
    container = _show_with(application, shown, model, views, retired=retired)
    notice = container.frame(AreaId(2)).content

    assert isinstance(notice, AreaNotice)
    assert notice.offer_button is not None
    assert notice.offer_button.text() == "Show 'Other view'"
    assert container.model.area(AreaId(2)).view == _UNKNOWN

    notice.offer_button.click()
    application.processEvents()

    assert container.model.area(AreaId(2)).view == _OTHER
    assert container.frame(AreaId(2)).content is views.by_id[21]


def test_a_removed_or_unknown_kind_offers_no_button(
    application: QApplication, shown: list[AreaLayout]
) -> None:
    gone = ViewKind("gone_view")
    retired = retirements(_THREE, RetiredTag(gone, "0.7.0"))
    model = _layout(_row((0.5, 0.5), Area(AreaId(1), gone), Area(AreaId(2), _UNKNOWN)), 3)
    container = _show_with(application, shown, model, _ViewsByKind(), retired=retired)

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
    application: QApplication, shown: list[AreaLayout], views: _Views
) -> None:
    """`PL-MS34` Q2: chooser first, then a stretch, then the Area menu."""

    container = _show(application, shown, _LEFT_AND_STACK, views, size=(800, 600))

    for number in (1, 2, 3):
        frame = container.frame(AreaId(number))
        row = frame.header.layout()
        assert row is not None

        assert isinstance(frame.menu, AreaMenu)
        assert frame.menu.text() == AREA_MENU_LABEL
        assert row.itemAt(0).widget() is frame.chooser
        assert row.itemAt(row.count() - 1).widget() is frame.menu


def test_the_menu_offers_each_operation_and_shows_a_join_the_layout_cannot_make(
    application: QApplication, shown: list[AreaLayout], views: _Views
) -> None:
    """A neighbour along part of an edge is listed and unavailable, never left out (`PL-2KXB`)."""

    container = _show(application, shown, _LEFT_AND_STACK, views, size=(800, 600))

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
    application: QApplication, shown: list[AreaLayout], views: _Views
) -> None:
    """Each expected layout is built here, not read back from the model."""

    container = _show(application, shown, _LEFT_AND_STACK, views, size=(800, 600))
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


def test_a_split_is_refused_where_a_half_could_not_hold_its_header(
    application: QApplication, shown: list[AreaLayout], views: _Views
) -> None:
    """`PL-30L5` Q2: below the header row and one line of a notice, a half is refused."""

    container = _show(application, shown, LayoutModel.single_area(_VIEW), views, size=(800, 40))
    stacked = _operation(container, 1, SPLIT_STACKED_LABEL)

    assert not stacked.available
    assert "too small to hold its header" in stacked.refusal
    assert _operation(container, 1, SPLIT_SIDE_BY_SIDE_LABEL).available

    with pytest.raises(ValueError, match="unavailable"):
        container.perform(stacked)

    assert container.model == LayoutModel.single_area(_VIEW)


def test_a_lone_area_can_be_split_and_nothing_else(
    application: QApplication, shown: list[AreaLayout], views: _Views
) -> None:
    container = _show(application, shown, LayoutModel.single_area(_VIEW), views, size=(800, 600))

    assert _labels(container, 1) == [
        (None, SPLIT_SIDE_BY_SIDE_LABEL, True),
        (None, SPLIT_STACKED_LABEL, True),
        (None, CLOSE_AREA_LABEL, False),
    ]
    assert "only Area" in _operation(container, 1, CLOSE_AREA_LABEL).refusal


def test_the_drawn_menu_disables_each_unavailable_entry_and_says_why(
    application: QApplication, shown: list[AreaLayout], views: _Views
) -> None:
    """The reader sees the entry, greyed, with its reason as the tooltip."""

    container = _show(application, shown, _LEFT_AND_STACK, views, size=(800, 600))
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
    application: QApplication, shown: list[AreaLayout], views: _Views
) -> None:
    container = _show(application, shown, LayoutModel.single_area(_VIEW), views, size=(800, 600))
    button = container.frame(AreaId(1)).menu
    assert button is not None
    button.fill()
    top = {action.text(): action for action in button.menu().actions()}

    assert not top[JOIN_WITH_LABEL].isEnabled()
    assert not top[SWAP_WITH_LABEL].isEnabled()
