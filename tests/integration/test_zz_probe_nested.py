from __future__ import annotations

from PySide6.QtCore import QPoint, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QWidget

from anesthesia_sim.layout.tree import Area, AreaId
from tests.integration.test_layout_adapter import (
    _BIG,
    _column,
    _host_sized,
    _layout,
    _press,
    _row,
    _splitters,
    _tree,
    application,  # noqa: F401
    hosts,  # noqa: F401
)


def _big(n: int) -> Area:
    return Area(AreaId(n), _BIG)


def _dump(container):
    for path, s in sorted(_splitters(container).items()):
        print(" splitter", path, s.orientation(), "size", s.size().toTuple(), "sizes", s.sizes(),
              "min", s.minimumSizeHint().toTuple())
    print(" fit splits", dict(container._fit.apportionment.splits))
    print(" tree", _tree(container))


def test_probe_nested_overfull_ancestor(application, hosts) -> None:
    # outer column overfull along height; inner column (inside the row) shares the axis.
    model = _layout(
        _column((0.9, 0.1), _row((0.5, 0.5), _column((0.5, 0.5), _big(1), _big(2)), _big(3)), _big(4)),
        5,
    )
    for height in (250, 400, 440):
        _, container = _host_sized(application, hosts, model, (900, height))
        print("HEIGHT", height, "container", container.size().toTuple())
        _dump(container)
        inner = _splitters(container)[(0, 0)]
        drawn = inner.sizes()
        changed = []
        container.layout_changed.connect(changed.append)
        handle = inner.handle(1)
        start = _press(handle)
        QTest.mouseMove(handle, start)
        application.processEvents()
        print(" after zero move: tree", _tree(container), "changed", len(changed), "warning", handle.warning)
        QTest.mouseMove(handle, start + QPoint(0, 20))
        application.processEvents()
        print(" after +20: tree", _tree(container), "changed", len(changed), "sizes", inner.sizes(), "was", drawn, "warning", handle.warning)
        QTest.mouseRelease(handle, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, start)
        application.processEvents()


def test_probe_nested_dump(application, hosts) -> None:
    model = _layout(
        _column((0.9, 0.1), _row((0.5, 0.5), _column((0.5, 0.5), _big(1), _big(2)), _big(3)), _big(4)),
        5,
    )
    for height in (250, 300):
        _, container = _host_sized(application, hosts, model, (900, height))
        print("HEIGHT", height)
        _dump(container)
        for n in (1, 2, 3, 4):
            f = container.frame(AreaId(n))
            print("  area", n, "geom", f.size().toTuple(), "min", f.minimumSize().toTuple())
        print("  too_small", [e.area_id for e in container.too_small()])


def test_probe_reverse_nested(application, hosts) -> None:
    model = _layout(
        _row((0.9, 0.1), _column((0.5, 0.5), _row((0.5, 0.5), _big(1), _big(2)), _big(3)), _big(4)),
        5,
    )
    for width in (300, 400, 500):
        _, container = _host_sized(application, hosts, model, (width, 900))
        print("WIDTH", width)
        _dump(container)
        inner = _splitters(container)[(0, 0)]
        drawn = inner.sizes()
        frames = [container.frame(AreaId(n)).geometry().getRect() for n in (1, 2)]
        changed = []
        container.layout_changed.connect(changed.append)
        handle = inner.handle(1)
        start = _press(handle)
        QTest.mouseMove(handle, start)
        application.processEvents()
        print(" zero move: inner", _tree(container).children[0].children[0].sizes, "changed", len(changed), "warning", handle.warning)
        QTest.mouseMove(handle, start + QPoint(20, 0))
        application.processEvents()
        print(" +20: inner", _tree(container).children[0].children[0].sizes, "changed", len(changed), "sizes", inner.sizes(), "was", drawn,
              "frames", [container.frame(AreaId(n)).geometry().getRect() for n in (1, 2)], "was", frames, "warning", handle.warning)
        QTest.mouseRelease(handle, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, start)
        application.processEvents()
