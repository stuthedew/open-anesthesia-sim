"""A throwaway pytest plugin for a Mac runner: keep each window off the screen at the size asked for.

The runner's screen is 1024 by 768, and macOS shrinks a shown window to fit it.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget

_show = QWidget.show


def _show_off_screen(self: QWidget) -> None:
    if self.isWindow():
        self.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
    _show(self)


QWidget.show = _show_off_screen  # type: ignore[method-assign]
