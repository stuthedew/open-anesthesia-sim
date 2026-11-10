"""Render the screenshot of the interface that `README.md` shows.

The image is the real Qt dashboard, built and painted with no display under
Qt's `offscreen` platform, as `.claude/skills/run-the-app/SKILL.md` describes.
It shows the default Workspace after ten simulated minutes of the shipped
default case: sevoflurane delivered at 2.00% (1.00 ×MAC), a fresh gas flow of
4.0 L/min, an alveolar ventilation of 4.0 L/min and a cardiac output of
5.0 L/min, played at 1× real time. Those are the settings a new case opens
with, so the image shows what a reader sees when they press Start and wait.

The README shows a frozen copy of displayed clinical values, so the image must
keep three things in one frame: the agent's name, the 1 MAC value that each
×MAC figure is divided by, and the playback rate. The whole window is grabbed
at 1440 by 1300 pixels, which holds the page from the title bar to the
disclaimer, so no number is cut off from its units or its label.

**When to retake it.** Run this script again, and commit the new image with
the README caption updated to the version it prints, whenever a change alters
what the default Workspace shows: a readout, a label, a legend, a control, the
layout, or a value the default case produces. A stale image shows a display
that no longer exists, which is worse than no image.

**What the image cannot show exactly.** The container draws with the fonts it
has installed, so the type in the image can differ from what the project
owner's machine draws. The version string in the image is the build that
rendered it, including the commit when that build is between releases.

Run it from the repository root with `uv run python tools/readme_screenshot.py`.
It prints the path it wrote and the version shown in the image.
"""

import os
from pathlib import Path

#: Where `README.md` reads the image from.
SCREENSHOT_PATH = Path("assets/screenshots/dashboard.png")

#: Ten minutes shows the circuit near its plateau while the alveolar and
#: vessel-rich traces are still rising, so the image shows uptake in progress.
SIMULATED_S = 600.0

#: Wide enough for the readout row and the settings panel to sit side by side,
#: and tall enough for the whole page to fit without the scroll area cutting it.
WIDTH_PX, HEIGHT_PX = 1440, 1300


def main() -> None:
    """Render the dashboard in the default case and save it to `SCREENSHOT_PATH`."""

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    from PySide6.QtWidgets import QApplication, QPushButton

    from anesthesia_sim.app.controller import BranchedCase, SimulationController
    from anesthesia_sim.app.dashboard_frame import SIMULATION_STEP_S
    from anesthesia_sim.app.qt_widgets import declare_application_colours
    from anesthesia_sim.app.simulation_view import SimulationView
    from anesthesia_sim.app_metadata import APP_BUILD_VERSION

    app = QApplication([])
    declare_application_colours(app)
    case = BranchedCase(SimulationController())
    view = SimulationView((case.trunk,), case=case)
    view.resize(WIDTH_PX, HEIGHT_PX)
    view.show()
    app.processEvents()
    view.present(False)

    next(b for b in view.findChildren(QPushButton) if b.text() == "Start").click()
    for _ in range(round(SIMULATED_S / SIMULATION_STEP_S)):
        case.trunk.advance(SIMULATION_STEP_S)

    view.present(False)
    app.processEvents()

    SCREENSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not view.grab().save(str(SCREENSHOT_PATH)):
        raise SystemExit(f"could not write {SCREENSHOT_PATH}")
    print(f"wrote {SCREENSHOT_PATH}, showing version {APP_BUILD_VERSION}")


if __name__ == "__main__":
    main()
