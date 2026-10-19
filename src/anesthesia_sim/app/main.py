"""The application entry point: one case, one window, two timers.

`uv run anesthesia-sim` runs `main()` below. The window opens maximized
(`PL-Z4K6`), so the readout row gets the widest rung the screen affords -
seven across on a 1366 px laptop, which the fraction below missed by a few
pixels - over a normal geometry that is a fraction of the screen's available
area and centred (`PL-005`), never at a pixel size:
`qt_widgets.initial_window_geometry` derives it from the screen the
application is given, and it is what the reader gets back on un-maximizing.
Maximized is not full screen: the title bar and window controls stay, and on
macOS it is the zoomed window, so `PL-005`'s refusal of a full-screen start
does not reach it. It is also the reference's own default window state
(`docs/interface-provenance.md` § "Adopted"). The first frame is drawn after
the window is shown, because a frame is assembled from the plot's laid-out
width, and the timers start after that so the first thing a reader sees is
a drawn, paused run; the platform applies the maximized size afterwards, and each chart
then owes the render tick a frame at its new width
(`ConcentrationChart.owes_a_frame`).

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

**The reader's saved Workspaces are loaded here, once** (`PL-DWHG`). `main()`
gives Qt the organization and application names. It then asks Qt for the
`QStandardPaths.AppDataLocation` directory, which the module docstring of
`layout/store.py` lists for each platform. `open_workspaces` applies the one
override, the `ANESTHESIA_SIM_USER_DIR` environment variable. It loads
`workspaces.json` from the resulting directory, or the shipped set where
there is no file. The dashboard receives the loaded set and two more things.
One is the store itself, so that the Layout menu's "Save as default" can
write to it. The other is the store's notice, which the tab strip shows.
Where the platform reports no directory, the session has no store, so
nothing is saved, and a notice tells the reader why.
"""

import os
import sys
from collections.abc import Callable, Mapping
from dataclasses import dataclass

from PySide6.QtCore import QStandardPaths
from PySide6.QtWidgets import QApplication, QMainWindow

from anesthesia_sim.app.controller import BranchedCase, SimulationController
from anesthesia_sim.app.qt_widgets import (
    WINDOW_SCREEN_FRACTION,
    declare_application_colours,
    initial_window_geometry,
)
from anesthesia_sim.app.simulation_view import SimulationView
from anesthesia_sim.app_metadata import APP_DISPLAY_NAME, APP_ORGANIZATION_NAME
from anesthesia_sim.layout.exceptions import LayoutRefused
from anesthesia_sim.layout.shipped import shipped_workspaces
from anesthesia_sim.layout.store import WorkspaceStore, user_data_directory
from anesthesia_sim.layout.workspace import WorkspaceSet


@dataclass(frozen=True, slots=True)
class LaunchWorkspaces:
    """The Workspaces a launch opens on, and where they can be saved.

    Attributes:
        workspaces: The set the dashboard opens on.
        store: The store the set was loaded from, which "Save as default"
            writes to, or `None` where there is no directory to save in.
        notice: What the reader is told about the load, or `None` where
            nothing happened that they should know.
    """

    workspaces: WorkspaceSet
    store: WorkspaceStore | None
    notice: str | None


def open_workspaces(
    standard_location: str,
    environment: Mapping[str, str],
    shipped: Callable[[], WorkspaceSet] = shipped_workspaces,
) -> LaunchWorkspaces:
    """Load the reader's Workspaces from their data directory, by `layout/store.py`'s policy.

    Args:
        standard_location: The directory Qt reports for
            `QStandardPaths.AppDataLocation`, or an empty string where the
            platform reports none.
        environment: The process environment, read for the override that
            `user_data_directory` applies.
        shipped: Returns the shipped set, shown where no file can be used.

    Returns:
        The loaded set with its store and notice. Where neither the override
        nor the platform names a directory, the result holds the shipped set,
        no store, and a notice saying that nothing will be saved this session.

    Raises:
        ShippedWorkspaceError: The shipped set cannot be read. That is a
            defect of the build rather than anything the reader did.
    """

    try:
        directory = user_data_directory(standard_location, environment)
    except LayoutRefused as refusal:
        return LaunchWorkspaces(
            shipped(),
            None,
            f"{refusal}. The shipped Workspaces are shown and nothing will be saved this session",
        )

    store = WorkspaceStore(directory)
    loaded = store.load(shipped())

    return LaunchWorkspaces(loaded.workspaces, store, loaded.notice)


def main() -> None:
    """Launch the application and run its event loop until the window closes.

    Raises:
        RuntimeError: If the platform reports no primary screen, since
            there is then nothing to size the window from; a window opened
            at a guessed size could hide its own content.
    """

    app = QApplication(sys.argv[:1])
    app.setOrganizationName(APP_ORGANIZATION_NAME)
    app.setApplicationName(APP_DISPLAY_NAME)
    declare_application_colours(app)
    launch = open_workspaces(
        QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation), os.environ
    )
    case = BranchedCase(SimulationController())
    view = SimulationView(
        (case.trunk,),
        case=case,
        workspaces=launch.workspaces,
        store=launch.store,
        notice=launch.notice,
    )
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
    window.showMaximized()
    view.present(False)
    view.start_simulation_timer()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
