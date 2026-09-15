"""The application entry point: one run, one window, two timers.

`uv run anesthesia-sim` runs `main()` below. The window opens on a fraction
of the screen's available area and centred (`PL-005`), never full-screen and
never at a pixel size: `qt_widgets.initial_window_geometry` derives it from
the screen the application is given. The first frame is drawn after the
window is shown, because a frame is assembled from the plot's laid-out
width, and the timers start after that so the first thing a reader sees is
a drawn, paused run.
"""

import sys

from PySide6.QtWidgets import QApplication, QMainWindow

from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.app.qt_widgets import WINDOW_SCREEN_FRACTION, initial_window_geometry
from anesthesia_sim.app.simulation_view import SimulationView
from anesthesia_sim.app_metadata import APP_DISPLAY_NAME


def main() -> None:
    """Launch the application and run its event loop until the window closes.

    Raises:
        RuntimeError: If the platform reports no primary screen, since
            there is then nothing to size the window from; a window opened
            at a guessed size could hide its own content.
    """

    app = QApplication(sys.argv[:1])
    controller = SimulationController()
    view = SimulationView((controller,))
    window = QMainWindow()
    window.setWindowTitle(APP_DISPLAY_NAME)
    window.setCentralWidget(view)
    screen = app.primaryScreen()

    if screen is None:
        raise RuntimeError("no primary screen is available to open the window on")

    window.setGeometry(
        initial_window_geometry(
            screen.availableGeometry(), window.minimumSizeHint(), WINDOW_SCREEN_FRACTION
        )
    )
    window.show()
    view.present(False)
    view.start_simulation_timer()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
