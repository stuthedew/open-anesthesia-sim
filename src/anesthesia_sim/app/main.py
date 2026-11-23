"""The application entry point: one case, one window, two timers.

`uv run anesthesia-sim` runs `main()` below. The window opens maximized
(`PL-Z4K6`). A maximized window lets the readout row use as many columns as
the screen allows. On a 1366 px laptop that is seven readouts across, which the
fraction of the screen described below missed by a few pixels. Behind the
maximized state, the window also has a normal geometry. That geometry is a
fraction of the screen's available area, centred on it (`PL-005`), and never a
fixed pixel size. `qt_widgets.initial_window_geometry` derives it from the
screen that the application is given, and the reader gets it back when they
un-maximize the window. Maximized is not full screen. The title bar and window
controls stay, and on macOS a maximized window is the zoomed window. So
`PL-005`'s refusal of a full-screen start does not apply to it. Maximized is
also the reference's own default window state (`docs/interface-provenance.md`
§ "Adopted").

The first frame is drawn before the window is sized. A readout stays empty
until a frame fills it, and an empty label claims less width than its value
needs, so a window sized from the empty dashboard could open narrower than its
own minimum. The timers start after the window is shown, so the first thing a
reader sees is a drawn, paused run. The charts' first frame is sampled before
their plots are laid out, and the platform applies the maximized size later
still. Each chart then needs a new frame at its new width on the next render
tick (`ConcentrationChart.owes_a_frame`).

**What is opened is a case, not a run** (`PL-VKJW`). `BranchedCase` makes two
runs on one axis into one patient under two managements, rather than two
unrelated sessions (`docs/ARCHITECTURE.md` § "What a branch is"). So the case
is built here, at the entry point, and the dashboard opens on the case's
trunk. The learner adds the second run themselves, by taking a branch.

**The interface's colours are declared on the application before the first
widget exists** (`PL-KRZW`). Qt's palette follows the host's appearance, but
every colour that this interface declares is a light-theme value. So, without
the declaration, the parts of the window that no stylesheet applies to, such as
the page's scroll bars, were drawn in a dark host's colours around a light
window. `qt_widgets.declare_application_colours` makes that declaration, and
its docstring explains why it is a palette rather than a colour-scheme hint.
This module owns only the ordering: a widget built before the call would be
laid out under the host's palette.

**The reader's saved Workspaces are loaded here, once** (`PL-DWHG`). `main()`
gives Qt the organization and application names. It then asks Qt for the
`QStandardPaths.AppDataLocation` directory, which the module docstring of
`layout/store.py` lists for each platform. `open_workspaces` applies the one
override, the `ANESTHESIA_SIM_USER_DIR` environment variable. It loads
`workspaces.json` from the resulting directory, or uses the shipped set when
there is no file. The dashboard receives the loaded set and two more things.
One is the store itself, so that the Layout menu's "Save as default" can
write to it. The other is the store's notice, which the tab strip shows.
Where the platform reports no directory, the session has no store, so
nothing is saved, and a notice tells the reader why.

**The reader's preferences are loaded here too, from the same directory**
(`PL-B396`). `open_preferences` loads `preferences.json` beside
`workspaces.json`, through `app/preferences.py`, which owns the file. The
dashboard receives what was loaded and the store, so that a change of
preference, such as the agent cost View's unit, is saved and survives a
restart. Where there is no directory, the session uses the default
preferences, and the agent cost View says that a change will not be kept.

**A failure that stops a run is also written to a file in the same directory**
(`PL-TWZY`). The halt banner words a failure for the learner, and leaves out
the exception's own message where that message is written for a developer. So
`open_failure_log` sends the log records of `anesthesia_sim` to
`failures.log` beside `workspaces.json`, as well as to standard error, where
Python prints them when nothing else is set. A learner who opened the
application from an icon has no terminal, and the file keeps the record for
whoever looks into the fault. The file is capped in size, and one older file
is kept.
"""

import logging
import os
import sys
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from logging.handlers import RotatingFileHandler
from pathlib import Path

from PySide6.QtCore import QStandardPaths
from PySide6.QtWidgets import QApplication, QMainWindow

from anesthesia_sim.app.controller import BranchedCase, SimulationController
from anesthesia_sim.app.preferences import LoadedPreferences, Preferences, PreferencesStore
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
    """Load the reader's Workspaces from their data directory, using `layout/store.py`'s policy.

    Args:
        standard_location: The directory Qt reports for
            `QStandardPaths.AppDataLocation`, or an empty string where the
            platform reports none.
        environment: The process environment, read for the override that
            `user_data_directory` applies.
        shipped: A function that returns the shipped set, which is shown when
            no file can be used.

    Returns:
        The loaded set with its store and notice. When neither the override
        nor the platform names a directory, the result contains the shipped set,
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


@dataclass(frozen=True, slots=True)
class LaunchPreferences:
    """The preferences a launch opens with, and where they can be saved.

    Attributes:
        loaded: What the store loaded, or the default preferences with a
            notice where there is no directory to load from.
        store: The store a change of preference is saved to, or `None` where
            there is no directory to save in.
    """

    loaded: LoadedPreferences
    store: PreferencesStore | None


def open_preferences(standard_location: str, environment: Mapping[str, str]) -> LaunchPreferences:
    """Load the reader's preferences from their data directory, the one Workspaces use.

    Args:
        standard_location: As `open_workspaces` takes it.
        environment: As `open_workspaces` takes it.

    Returns:
        What the store loaded, with the store. When neither the override nor
        the platform names a directory, the result holds the default
        preferences, no store, and a notice saying that no change of
        preference will be kept.
    """

    try:
        directory = user_data_directory(standard_location, environment)
    except LayoutRefused as refusal:
        return LaunchPreferences(
            LoadedPreferences(
                Preferences(),
                writable=False,
                notice=f"{refusal}. No change of preference will be kept after this session",
            ),
            None,
        )

    store = PreferencesStore(directory)

    return LaunchPreferences(store.load(), store)


FAILURE_LOG_NAME = "failures.log"
"""The file that a launch's failure records are written to, in the reader's data directory."""

FAILURE_LOG_MAX_BYTES = 1_000_000
"""The size at which the failure log is moved aside and a new one started.

A failure that repeats on every tick could otherwise fill the disk. One
megabyte holds a few hundred failures with their tracebacks.
"""


def open_failure_log(standard_location: str, environment: Mapping[str, str]) -> Path | None:
    """Write the package's error records to `failures.log` in the reader's data directory.

    The handler is added to the `anesthesia_sim` logger, so every module's
    logger under it reaches the file. The file is moved aside to
    `failures.log.1` when it reaches `FAILURE_LOG_MAX_BYTES`, and a new one is
    started.

    Args:
        standard_location: As `open_workspaces` takes it.
        environment: As `open_workspaces` takes it.

    Returns:
        The file's path, or None where neither the override nor the platform
        names a directory, or where the file cannot be opened there. The
        records then reach standard error only. The log exists to help find a
        fault, so a directory it cannot use never stops the application from
        opening. The Workspace and preference stores treat such a directory in
        the same way.
    """

    try:
        directory = user_data_directory(standard_location, environment)
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / FAILURE_LOG_NAME
        handler = RotatingFileHandler(
            path, maxBytes=FAILURE_LOG_MAX_BYTES, backupCount=1, encoding="utf-8"
        )
    except LayoutRefused, OSError:
        return None

    handler.setLevel(logging.ERROR)
    handler.setFormatter(logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s"))
    package = logging.getLogger("anesthesia_sim")
    package.addHandler(handler)
    # Python's last-resort handler prints to standard error only while no
    # handler is set anywhere on the way up. With the file's handler added,
    # standard error is added back explicitly.
    package.addHandler(logging.StreamHandler())

    return path


def open_dashboard(
    case: BranchedCase, standard_location: str, environment: Mapping[str, str]
) -> SimulationView:
    """Build the dashboard over `case`'s trunk, with the reader's Workspaces and preferences.

    `main()` calls this, and so do the tests of what survives a restart. So
    the wiring that saves the reader's choices is the one under test.

    Args:
        case: The case the dashboard opens on.
        standard_location: As `open_workspaces` takes it.
        environment: As `open_workspaces` takes it.

    Raises:
        ShippedWorkspaceError: As `open_workspaces` raises it.
    """

    launch = open_workspaces(standard_location, environment)
    preferences = open_preferences(standard_location, environment)

    return SimulationView(
        (case.trunk,),
        case=case,
        workspaces=launch.workspaces,
        store=launch.store,
        notice=launch.notice,
        preferences=preferences.loaded,
        preferences_store=preferences.store,
    )


def main() -> None:
    """Launch the application and run its event loop until the window closes.

    Raises:
        RuntimeError: If the platform reports no primary screen. Without
            one there is nothing to size the window from, and a window opened
            at a guessed size could hide its own content.
    """

    app = QApplication(sys.argv[:1])
    app.setOrganizationName(APP_ORGANIZATION_NAME)
    app.setApplicationName(APP_DISPLAY_NAME)
    declare_application_colours(app)
    data_location = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
    open_failure_log(data_location, os.environ)
    view = open_dashboard(BranchedCase(SimulationController()), data_location, os.environ)
    window = QMainWindow()
    window.setWindowTitle(APP_DISPLAY_NAME)
    window.setCentralWidget(view)
    screen = app.primaryScreen()

    if screen is None:
        raise RuntimeError("no primary screen is available to open the window on")

    # The module docstring says why the first frame comes first.
    view.present(False)
    window.setGeometry(
        initial_window_geometry(
            screen.availableGeometry(), window.minimumSizeHint(), WINDOW_SCREEN_FRACTION
        )
    )
    window.showMaximized()
    view.start_simulation_timer()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
