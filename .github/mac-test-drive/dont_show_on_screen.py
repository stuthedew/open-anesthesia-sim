"""Throwaway pytest plugin: keep each test window off the runner's small screen.

The macOS runner's screen is 1024 by 768, and macOS shrinks a shown window to
fit it, so a test that asks for a 1366 by 768 window gets a smaller one. A
window marked never to be put on screen keeps the size it is given and still
lays out its text with macOS's own font and style.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget

_show = QWidget.show


def _show_off_screen(self: QWidget) -> None:
    if self.isWindow():
        self.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
    _show(self)


QWidget.show = _show_off_screen
