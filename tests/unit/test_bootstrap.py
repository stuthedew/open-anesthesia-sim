from importlib.metadata import distribution
from importlib.resources import files
from typing import Any

import pytest
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QApplication, QMainWindow

import anesthesia_sim
import anesthesia_sim.app.main as app_main
from anesthesia_sim.app.controller import BranchedCase
from anesthesia_sim.app.qt_widgets import WINDOW_SCREEN_FRACTION, initial_window_geometry
from anesthesia_sim.app.simulation_view import SimulationView
from anesthesia_sim.app.theme import INK, PANEL
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

    **What it opens is a case** (`PL-VKJW`). `BranchedCase` and everything
    under it had shipped while nothing in `src/` constructed one, so the
    branching v0.5.0 is named for was unreachable from the entry point the
    console script runs. This is the assertion that the shipped path builds
    one, rather than a dashboard that can only be handed a second run by a
    test.

    **And it declares this interface's colours before it builds anything**
    (`PL-KRZW`). Qt's application palette follows the host appearance, so a
    widget constructed before the declaration is laid out in a dark host's
    surfaces; `tests/integration/test_dark_appearance.py` holds what the
    declaration *contains*, and the ordering is the half that belongs to
    `main()`. It is recorded as a timeline rather than as two separate
    assertions, because either one alone passes with the call in the wrong
    place.
    """

    application = QApplication.instance() or QApplication([])
    exec_calls: list[int] = []
    windows: list[QMainWindow] = []
    declared: list[QPalette] = []
    timeline: list[str] = []

    class _RecordingApplication:
        def __init__(self, argv: list[str]) -> None:
            del argv

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
        assert window.geometry() == initial_window_geometry(
            available, window.minimumSizeHint(), WINDOW_SCREEN_FRACTION
        )
        assert not window.isFullScreen()

        assert timeline == ["declared", "built the first widget"]
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
