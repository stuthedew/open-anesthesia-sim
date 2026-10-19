"""`tests/conftest.py` deletes the windows the tests built when the session ends (`PL-CW51`).

The conftest's module docstring says why. Qt keeps some parentless widgets of
its own, such as the one each `QGraphicsLayoutStyleInfo` holds for a pyqtgraph
plot's layout, and deleting one of those before its plot crashes the process.
So the cleanup chooses only the windows Python built. These tests build one
dashboard, check which of its new windows the cleanup chooses, and check that
deleting those leaves none of the dashboard's widgets alive, Qt's own included.
They render under the `offscreen` platform that `tests/conftest.py` selects.
"""

import importlib.util
from collections.abc import Iterator
from pathlib import Path
from types import ModuleType

import pytest
import shiboken6
from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QApplication, QWidget

from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.app.simulation_view import SimulationView

CONFTEST = Path(__file__).parents[1] / "conftest.py"


def _conftest() -> ModuleType:
    """The conftest loaded under a name of its own, since every conftest is `conftest`."""

    spec = importlib.util.spec_from_file_location("tests_conftest", CONFTEST)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CLEANUP = _conftest()


@pytest.fixture(scope="module")
def application() -> Iterator[QApplication]:
    existing = QApplication.instance()

    yield existing if isinstance(existing, QApplication) else QApplication([])


def _address(widget: QWidget) -> int:
    """The address of the widget's C++ object, which stays the same across Python wrappers."""

    address: int = shiboken6.getCppPointer(widget)[0]
    return address


def _new_windows(application: QApplication, before: set[int]) -> list[QWidget]:
    return [window for window in application.topLevelWidgets() if _address(window) not in before]


def test_the_cleanup_deletes_a_dashboard_and_the_widgets_qt_built_for_it(
    application: QApplication,
) -> None:
    """The dashboard is chosen, Qt's own widget is not, and deleting the dashboard takes both.

    Only this test's windows are deleted, so a window another test in this
    worker still holds is left alone.
    """

    before = {_address(window) for window in application.topLevelWidgets()}
    view = SimulationView((SimulationController(),))
    view.show()
    application.processEvents()
    view.present(False)
    built = _new_windows(application, before)

    chosen = CLEANUP.windows_built(built)
    # A menu built with a parent is a window too, and goes with its parent.
    left_to_qt = [window for window in built if window.parent() is None and window not in chosen]

    assert view in chosen
    # The plain widget a plot's layout style holds, which Qt deletes itself.
    assert any(type(window) is QWidget for window in left_to_qt)
    assert not any(shiboken6.createdByPython(window) for window in left_to_qt)

    for window in chosen:
        window.deleteLater()

    application.sendPostedEvents(None, QEvent.Type.DeferredDelete)

    assert not any(shiboken6.isValid(window) for window in built)
    assert _new_windows(application, before) == []
