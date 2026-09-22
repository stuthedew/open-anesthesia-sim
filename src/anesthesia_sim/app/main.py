"""The application entry point: one case, one window, two timers.

`uv run anesthesia-sim` runs `main()` below. The window opens on a fraction
of the screen's available area and centred (`PL-005`), never full-screen and
never at a pixel size: `qt_widgets.initial_window_geometry` derives it from
the screen the application is given. The first frame is drawn after the
window is shown, because a frame is assembled from the plot's laid-out
width, and the timers start after that so the first thing a reader sees is
a drawn, paused run.

**What is opened is a case, not a run** (`PL-VKJW`). `BranchedCase` is what
makes two runs on one axis one patient under two managements rather than two
unrelated sessions (`docs/ARCHITECTURE.md` § "What a branch is"), so it is
built here, at the entry point, and the dashboard is opened over its trunk.
The learner adds the second run themselves, by taking a branch.

**The interface's colours are declared on the application before the first
widget exists** (`PL-KRZW`). Qt's palette follows the host appearance, and
every colour this interface declares is a light-theme value, so the chrome no
stylesheet reaches - the page's scroll bars - drew a dark host's surfaces
around a light window. `qt_widgets.declare_application_colours` is what that
declaration is and why it is a palette rather than a colour-scheme hint; the
ordering here is the part that belongs to this module, since a widget built
before the call would be laid out under the host's palette.
"""

import sys

from PySide6.QtWidgets import QApplication, QMainWindow

from anesthesia_sim.app.controller import BranchedCase, SimulationController
from anesthesia_sim.app.qt_widgets import (
    WINDOW_SCREEN_FRACTION,
    declare_application_colours,
    initial_window_geometry,
)
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
    declare_application_colours(app)
    case = BranchedCase(SimulationController())
    view = SimulationView((case.trunk,), case=case)
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
