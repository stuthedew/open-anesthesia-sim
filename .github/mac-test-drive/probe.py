"""One-off probe: draw the Maintenance Workspace at 1 h on macOS and check the schematic's labels.

Run by the mac-test-drive workflow on a macOS runner under Qt's native
`cocoa` platform, so text is laid out in macOS's own system font and style.
Throwaway: this file and the workflow live only on a thread branch.
"""

import os
import sys
import tempfile

from PySide6.QtCore import QPoint, QRect
from PySide6.QtGui import QFont, QFontInfo, QFontMetrics
from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QScrollArea

from anesthesia_sim.app.controller import BranchedCase, SimulationController
from anesthesia_sim.app.main import open_dashboard
from anesthesia_sim.app.qt_schematic import ContainerNames, SchematicCanvas
from anesthesia_sim.app.qt_widgets import declare_application_colours
from anesthesia_sim.app.views import CompartmentSchematicView
from anesthesia_sim.layout.store import USER_DIRECTORY_VARIABLE

OUT = sys.argv[1]
SIZES = [(1366, 768), (1470, 850), (1512, 917), (1728, 1052)]

app = QApplication([])
declare_application_colours(app)
if os.environ.get("PROBE_SYSTEM_FONT"):
    app.setFont(QFont(".AppleSystemUIFont", 13))
print("platform:", app.platformName(), "| style:", app.style().name())
info = QFontInfo(app.font())
print("application font:", app.font().family(), "->", info.family(), info.pointSizeF(), "pt")
screen = app.primaryScreen()
print("runner screen:", screen.geometry(), "available:", screen.availableGeometry(), "dpr:", screen.devicePixelRatio())

case = BranchedCase(SimulationController())
view = open_dashboard(case, "", {USER_DIRECTORY_VARIABLE: tempfile.mkdtemp()})
view.resize(*SIZES[0])
view.show()
app.processEvents()
view.present(False)
names = [str(w.name) for w in view._tabs._workspaces.workspaces]
view._tabs.activate(names.index("Maintenance"))
app.processEvents()
view.present(False)
app.processEvents()
next(b for b in view.findChildren(QPushButton) if b.text() == "Start").click()
controller = case.trunk
while controller.snapshot().elapsed_s < 3600:
    controller.advance()

failures = 0
for width, height in SIZES:
    view.resize(width, height)
    for _ in range(3):
        app.processEvents()
        view.present(False)
    app.processEvents()
    schematic = next(v for v in view.layout_container.views() if isinstance(v, CompartmentSchematicView))
    viewport_owner = schematic.parentWidget()
    while viewport_owner is not None and not isinstance(viewport_owner, QScrollArea):
        viewport_owner = viewport_owner.parentWidget()
    viewport = viewport_owner.viewport() if viewport_owner is not None else schematic
    visible_rect = QRect(QPoint(0, 0), viewport.size())
    print(f"\n== {width}x{height}: schematic Area viewport {viewport.width()}x{viewport.height()}")
    window_rect = QRect(QPoint(0, 0), view.size())
    for label in view.findChildren(QLabel):
        if not label.isVisible() or not label.text():
            continue
        metrics = QFontMetrics(label.font())
        box = label.contentsRect()
        text = label.text()
        if "<" in text:
            continue
        if label.wordWrap():
            needed = metrics.boundingRect(box, int(label.alignment()) | 0x1000, text).height()
            fits = needed <= box.height() + 1
        else:
            needed_w = max(metrics.horizontalAdvance(line) for line in text.split("\n"))
            fits = needed_w <= box.width() + 1
        if not fits:
            failures += 1
            print(f"  CUT anywhere in the window: {text[:80]!r} ({box.width()}x{box.height()})")
        if any(key in text for key in ("Tensions are", "Amounts are", "Model outputs")) and schematic.isAncestorOf(label) is False:
            top_left = label.mapTo(view, QPoint(0, 0))
            print(f"  {'OK ' if fits else 'CUT'} pinned row line | in window: {window_rect.contains(QRect(top_left, label.size()))} | {text!r}")
    for label in schematic.findChildren(QLabel):
        if not label.isVisible() or not label.text():
            continue
        text = label.text()
        metrics = QFontMetrics(label.font())
        box = label.contentsRect()
        if label.wordWrap():
            needed = metrics.boundingRect(box, int(label.alignment()) | 0x1000, text).height()
            fits = needed <= box.height() + 1
            how = f"needs {needed} px high, has {box.height()}"
        else:
            lines = text.split("\n")
            needed_w = max(metrics.horizontalAdvance(line) for line in lines)
            needed_h = metrics.lineSpacing() * len(lines)
            fits = needed_w <= box.width() + 1 and needed_h <= box.height() + 1
            how = f"needs {needed_w}x{needed_h} px, has {box.width()}x{box.height()}"
        top_left = label.mapTo(viewport, QPoint(0, 0))
        in_view = visible_rect.contains(QRect(top_left, label.size()))
        flag = "OK " if fits else "CUT"
        failures += 0 if fits else 1
        print(f"  {flag} {'in view ' if in_view else 'scrolled'} | {how} | {text[:70]!r}")
    for canvas in [*schematic.findChildren(SchematicCanvas), *view.findChildren(ContainerNames)]:
        hint = canvas.minimumSizeHint()
        fits = canvas.width() >= hint.width() and canvas.height() >= hint.height()
        failures += 0 if fits else 1
        print(f"  {'OK ' if fits else 'CUT'} {type(canvas).__name__} {canvas.width()}x{canvas.height()}, needs {hint.width()}x{hint.height()}")
    print("  grab saved:", view.grab().save(f"{OUT}/mac-maintenance-1h-{width}x{height}.png"))

print("\nlabels or canvases that do not fit:", failures)
sys.exit(1 if failures else 0)
