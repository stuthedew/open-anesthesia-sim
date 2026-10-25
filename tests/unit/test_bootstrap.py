from importlib.metadata import distribution
from importlib.resources import files
from pathlib import Path
from typing import Any

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QApplication, QMainWindow

import anesthesia_sim
import anesthesia_sim.app.main as app_main
from anesthesia_sim.app.controller import BranchedCase
from anesthesia_sim.app.qt_widgets import WINDOW_SCREEN_FRACTION, initial_window_geometry
from anesthesia_sim.app.simulation_view import SimulationView
from anesthesia_sim.app.theme import INK, PANEL
from anesthesia_sim.app_metadata import APP_DISPLAY_NAME, APP_ORGANIZATION_NAME
from anesthesia_sim.layout.store import USER_DIRECTORY_VARIABLE, WORKSPACES_FILE_NAME


def test_import() -> None:
    assert anesthesia_sim is not None


def test_package_ships_a_py_typed_marker() -> None:
    """PEP 561: without this file nothing outside the package sees its types.

    A type checker running over other code, such as `tools/`, a test or an
    installed consumer, sees the annotations in `src/` only if the package
    declares itself typed. The marker is an empty file, so nothing else in the
    suite would notice if it were removed. This test checks for it through the
    package's own resource loader. The loader finds the file where an importer
    would, rather than where the repository happens to keep it.
    """
    assert files("anesthesia_sim").joinpath("py.typed").is_file()


def test_console_script_points_to_application_launcher() -> None:
    package = distribution("anesthesia-sim")

    console_script = next(
        entry_point
        for entry_point in package.entry_points
        if entry_point.group == "console_scripts" and entry_point.name == "anesthesia-sim"
    )

    assert console_script.value == ("anesthesia_sim.app.main:main")


def test_application_launcher_opens_a_sized_window_and_runs_the_event_loop(
    monkeypatch: Any, tmp_path: Path
) -> None:
    """`main()` builds the window on the screen it is given and hands control to Qt.

    The real widgets are built under the offscreen platform, so the window,
    its title, its central view and the first drawn frame are read back
    rather than mocked. Only the application object is wrapped, so that the
    event loop that `main()` ends in is recorded instead of run (`PL-005`,
    `PL-25KS`). The window is closed and its timers stopped afterwards, so a
    later test's event processing never meets a tick from this one.

    **What it opens is a case** (`PL-VKJW`). `BranchedCase` and everything
    under it had shipped while nothing in `src/` constructed one. So the
    branching that v0.5.0 is named for could not be reached from the entry
    point that the console script runs. This test asserts that the shipped
    path builds a case, rather than a dashboard that only a test can hand a
    second run.

    **And it declares this interface's colours before it builds anything**
    (`PL-KRZW`). Qt's application palette follows the host appearance, so a
    widget constructed before the declaration is laid out with a dark host's
    surface colours. `tests/integration/test_dark_appearance.py` checks what
    the declaration *contains*. The ordering is the half that belongs to
    `main()`. The order is recorded as a timeline rather than as two separate
    assertions, because either assertion alone passes with the call in the
    wrong place.

    **And it opens maximized over a sized normal geometry** (`PL-Z4K6`,
    `PL-005`). The offscreen platform records the requested state at once, but
    applies the maximized size only when events are processed. So the test
    asserts the flag that Qt records and the normal geometry that a reader gets
    back on un-maximizing. It never asserts the geometry that the platform
    happens to have produced by the time the assertion runs.

    **And it names the application before it asks where the reader's data
    lives, then loads the saved Workspaces from there** (`PL-DWHG`). Qt files
    the data directory under those two names. The test sets the override to
    an empty temporary directory. So the shipped set opens, "Save as default"
    offers to save a file in that directory, and nothing has been written to
    it.
    """

    application = QApplication.instance() or QApplication([])
    exec_calls: list[int] = []
    windows: list[QMainWindow] = []
    declared: list[QPalette] = []
    timeline: list[str] = []
    names: list[tuple[str, str]] = []

    class _RecordingApplication:
        def __init__(self, argv: list[str]) -> None:
            del argv

        def setOrganizationName(self, name: str) -> None:  # Qt spells this in camelCase.
            timeline.append("named")
            names.append(("organization", name))

        def setApplicationName(self, name: str) -> None:  # Qt spells this in camelCase.
            names.append(("application", name))

        def palette(self) -> QPalette:
            return QApplication.palette()

        def setPalette(self, palette: QPalette) -> None:  # Qt spells this in camelCase.
            timeline.append("declared")
            declared.append(palette)

        def primaryScreen(self) -> Any:  # Qt spells this in camelCase.
            return QApplication.primaryScreen()

        def exec(self) -> int:
            exec_calls.append(1)
            return 0

    class _RecordingWindow(QMainWindow):
        def __init__(self) -> None:
            super().__init__()
            windows.append(self)

    def _recording_view(*args: Any, **kwargs: Any) -> SimulationView:
        timeline.append("built the first widget")

        return SimulationView(*args, **kwargs)

    monkeypatch.setattr(app_main, "QApplication", _RecordingApplication)
    monkeypatch.setattr(app_main, "QMainWindow", _RecordingWindow)
    monkeypatch.setattr(app_main, "SimulationView", _recording_view)
    # The saved Workspaces are read from a temporary directory, never from
    # the user's own (`PL-DWHG`).
    monkeypatch.setenv(USER_DIRECTORY_VARIABLE, str(tmp_path))

    with pytest.raises(SystemExit) as exit_info:
        app_main.main()

    try:
        assert exit_info.value.code == 0
        assert exec_calls == [1]
        (window,) = windows
        view = window.centralWidget()
        assert isinstance(view, SimulationView)
        assert window.windowTitle() == APP_DISPLAY_NAME
        assert view.presented_frames == 1
        assert isinstance(view.case, BranchedCase)
        assert view.case.trunk is view.runs[0].controller
        assert view.case.branches == ()
        assert view.case.fork_points_s == (0.0,)

        available = QApplication.primaryScreen().availableGeometry()
        assert window.windowState() & Qt.WindowState.WindowMaximized
        assert not window.isFullScreen()
        assert window.normalGeometry() == initial_window_geometry(
            available, window.minimumSizeHint(), WINDOW_SCREEN_FRACTION
        )

        assert timeline == ["named", "declared", "built the first widget"]
        assert names == [("organization", APP_ORGANIZATION_NAME), ("application", APP_DISPLAY_NAME)]
        entry = view.tab_strip.save_entry()
        assert entry.question is not None
        assert str(tmp_path / WORKSPACES_FILE_NAME) in entry.question.text
        assert list(tmp_path.iterdir()) == []
        (palette,) = declared
        surface = palette.color(QPalette.ColorGroup.Active, QPalette.ColorRole.Window)
        ink = palette.color(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText)
        assert (surface.name().upper(), ink.name().upper()) == (PANEL.upper(), INK.upper())
    finally:
        view = windows[0].centralWidget() if windows else None
        if isinstance(view, SimulationView):
            view.stop_timers()
        for window in windows:
            window.close()
            window.deleteLater()
        application.processEvents()


def test_application_launcher_refuses_to_open_with_no_primary_screen(
    monkeypatch: Any, tmp_path: Path
) -> None:
    """With no primary screen there is nothing to size the window from (`PL-NC2P`).

    `main()` raises rather than opening a window at a guessed size, which
    could hide its own content. The window is never shown and the event loop
    never runs.
    """

    application = QApplication.instance() or QApplication([])
    exec_calls: list[int] = []
    windows: list[QMainWindow] = []

    class _ScreenlessApplication:
        def __init__(self, argv: list[str]) -> None:
            del argv

        def setOrganizationName(self, name: str) -> None:  # Qt spells this in camelCase.
            del name

        def setApplicationName(self, name: str) -> None:  # Qt spells this in camelCase.
            del name

        def palette(self) -> QPalette:
            return QApplication.palette()

        def setPalette(self, palette: QPalette) -> None:  # Qt spells this in camelCase.
            del palette

        def primaryScreen(self) -> None:  # Qt spells this in camelCase.
            return None

        def exec(self) -> int:
            exec_calls.append(1)
            return 0

    class _RecordingWindow(QMainWindow):
        def __init__(self) -> None:
            super().__init__()
            windows.append(self)

    monkeypatch.setattr(app_main, "QApplication", _ScreenlessApplication)
    monkeypatch.setattr(app_main, "QMainWindow", _RecordingWindow)
    monkeypatch.setenv(USER_DIRECTORY_VARIABLE, str(tmp_path))

    try:
        with pytest.raises(RuntimeError, match="no primary screen is available"):
            app_main.main()

        assert exec_calls == []
        (window,) = windows
        assert not window.isVisible()
    finally:
        for window in windows:
            view = window.centralWidget()
            if isinstance(view, SimulationView):
                view.stop_timers()
            window.close()
            window.deleteLater()
        application.processEvents()
