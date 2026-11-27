"""Record what the interface asks a screen reader to read out, for the tests that check it.

The interface sends each announcement through `QAccessible.updateAccessibility`
(`qt_widgets.announce`). PySide6 offers no way to install Qt's own handler for
those calls, so a test replaces the function for as long as it runs. Only a
call made from Python reaches the replacement, and the interface makes each
announcement from Python.
"""

from dataclasses import dataclass

import pytest
from PySide6.QtGui import QAccessible, QAccessibleAnnouncementEvent, QAccessibleEvent

#: What a screen reader is asked to do with an announcement: interrupt what it
#: is reading, or wait until speech pauses.
ASSERTIVE = QAccessible.AnnouncementPoliteness.Assertive
POLITE = QAccessible.AnnouncementPoliteness.Polite


@dataclass(frozen=True)
class Announcement:
    """One message the interface asked a screen reader to read out.

    Attributes:
        message: The words to read.
        politeness: `ASSERTIVE` or `POLITE`.
    """

    message: str
    politeness: QAccessible.AnnouncementPoliteness


def record_announcements(monkeypatch: pytest.MonkeyPatch) -> list[Announcement]:
    """Return a list that collects each announcement the interface makes from now on.

    The event is copied as it arrives, because Qt may reuse or delete it once
    the call returns. Any other accessibility event is passed over.
    """

    recorded: list[Announcement] = []

    def record(event: QAccessibleEvent) -> None:
        if isinstance(event, QAccessibleAnnouncementEvent):
            recorded.append(Announcement(event.message(), event.politeness()))

    monkeypatch.setattr(QAccessible, "updateAccessibility", staticmethod(record))

    return recorded
