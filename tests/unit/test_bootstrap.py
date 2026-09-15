from importlib.metadata import distribution
from importlib.resources import files
from typing import Any

import pytest
from PySide6.QtWidgets import QApplication, QMainWindow

import anesthesia_sim
import anesthesia_sim.app.main as app_main
from anesthesia_sim.app.qt_widgets import WINDOW_SCREEN_FRACTION, initial_window_geometry
from anesthesia_sim.app.simulation_view import SimulationView
from anesthesia_sim.app_metadata import APP_DISPLAY_NAME


def test_import() -> None:
    assert anesthesia_sim is not None


def test_package_ships_a_py_typed_marker() -> None:
    """PEP 561: without this file nothing outside the package sees its types.

    The annotations in `src/` are only visible to a type checker running over
    other code - `tools/`, a test, an installed consumer - if the package
    declares itself typed. The marker is an empty file, so nothing else in the
    suite would notice its removal; this asserts it through the package's own
    resource loader, which reads it where an importer would rather than where
    the repository happens to keep it.
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
    monkeypatch: Any,
) -> None:
    """`main()` builds the window on the screen it is given and hands control to Qt.

    The real widgets are built under the offscreen platform, so the window,
    its title, its central view and the first drawn frame are read back
    rather than mocked; only the application object is wrapped, so that the
    event loop `main()` ends in is recorded instead of run (`PL-005`,
    `PL-25KS`). The window is closed and its timers stopped afterwards, so a
    later test's event processing never meets a tick from this one.
    """

    application = QApplication.instance() or QApplication([])
    exec_calls: list[int] = []
    windows: list[QMainWindow] = []

    class _RecordingApplication:
        def __init__(self, argv: list[str]) -> None:
            del argv

        def primaryScreen(self) -> Any:  # Qt spells this in camelCase.
            return QApplication.primaryScreen()

        def exec(self) -> int:
            exec_calls.append(1)
            return 0

    class _RecordingWindow(QMainWindow):
        def __init__(self) -> None:
            super().__init__()
            windows.append(self)

    monkeypatch.setattr(app_main, "QApplication", _RecordingApplication)
    monkeypatch.setattr(app_main, "QMainWindow", _RecordingWindow)

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

        available = QApplication.primaryScreen().availableGeometry()
        assert window.geometry() == initial_window_geometry(
            available, window.minimumSizeHint(), WINDOW_SCREEN_FRACTION
        )
        assert not window.isFullScreen()
    finally:
        view = windows[0].centralWidget() if windows else None
        if isinstance(view, SimulationView):
            view.stop_timers()
        for window in windows:
            window.close()
            window.deleteLater()
        application.processEvents()
