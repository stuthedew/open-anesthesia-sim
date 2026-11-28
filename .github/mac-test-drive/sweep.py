"""One-off probe: find the smallest window in which the Maintenance schematic shows whole on macOS.

Throwaway, on a thread branch only. Draws the Maintenance Workspace at 1 h
under Qt's native cocoa platform, in the style named by PROBE_STYLE (the
platform's own when unset), and prints, for each window size, how many
pixels of the schematic's values fall below the part in view.
"""

import os
import sys
import tempfile

from PySide6.QtCore import QPoint, Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QScrollArea

from anesthesia_sim.app.controller import BranchedCase, SimulationController
from anesthesia_sim.app.main import open_dashboard
from anesthesia_sim.app.qt_schematic import SchematicCanvas
from anesthesia_sim.app.qt_widgets import declare_application_colours
from anesthesia_sim.app.views import CompartmentSchematicView
from anesthesia_sim.layout.store import USER_DIRECTORY_VARIABLE

app = QApplication([])
if os.environ.get("PROBE_STYLE"):
    app.setStyle(os.environ["PROBE_STYLE"])
declare_application_colours(app)
print("platform:", app.platformName(), "| style:", app.style().name())

screen = app.primaryScreen()
print("screen:", screen.geometry(), "available:", screen.availableGeometry())
plain = QMainWindow()
plain.resize(600, 400)
plain.show()
for _ in range(20):
    app.processEvents()
print("a shown window's frame:", plain.frameGeometry(), "and its inside:", plain.geometry())
plain.close()

case = BranchedCase(SimulationController())
view = open_dashboard(case, "", {USER_DIRECTORY_VARIABLE: tempfile.mkdtemp()})
view.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
view.resize(1366, 768)
view.show()
app.processEvents()
view.present(False)
names = [str(w.name) for w in view._tabs._workspaces.workspaces]
view._tabs.activate(names.index("Maintenance"))
app.processEvents()
view.present(False)
next(b for b in view.findChildren(QPushButton) if b.text() == "Start").click()
controller = case.trunk
while controller.snapshot().elapsed_s < 3600:
    controller.advance()


def settle(width: int, height: int) -> None:
    view.resize(width, height)
    for _ in range(3):
        app.processEvents()
        view.present(False)
    app.processEvents()


def overflow() -> tuple[int, int, int]:
    schematic = next(
        v for v in view.layout_container.views() if isinstance(v, CompartmentSchematicView)
    )
    owner = schematic.parentWidget()
    while owner is not None and not isinstance(owner, QScrollArea):
        owner = owner.parentWidget()
    viewport = owner.viewport()
    canvas = schematic.findChildren(SchematicCanvas)[0]
    top = canvas.mapTo(viewport, QPoint(0, 0)).y()
    return top + canvas.height() - viewport.height(), top, viewport.height()


settle(1366, 768)
print("\nAreas at 1366x768 (view, x, y, width, height):")
areas = view.layout_container
for area in areas.model.areas():
    frame = areas.frame(area.id)
    corner = frame.mapTo(view, QPoint(0, 0))
    print(f"  {area.view}: {corner.x()}, {corner.y()}, {frame.width()}, {frame.height()}")

for width in (1366, 1440, 1512):
    print(
        f"\nwidth {width}: height -> px of the values below the part in view (canvas top, viewport height)"
    )
    smallest = None
    for height in range(700, 821, 4):
        settle(width, height)
        below, top, viewport_height = overflow()
        if below <= 0 and smallest is None:
            smallest = height
        if height % 20 == 0 or (smallest == height):
            print(f"  {height}: {below} ({top}, {viewport_height})")
    print(f"  smallest height at which the values show whole: {smallest}")
sys.exit(0)
