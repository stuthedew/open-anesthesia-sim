"""Record what the interface tells a screen reader, for the tests that check it.

The interface sends each announcement, and each change to the concentration
chart's text, through `QAccessible.updateAccessibility` (`qt_widgets.announce`,
`qt_chart.ConcentrationChart`). PySide6 offers no way to install Qt's own
handler for those calls, so a test replaces the function for as long as it
runs. Only a call made from Python reaches the replacement. The interface
makes each of these calls from Python, and Qt's own widgets make theirs from
C++, which the replacement never sees. Each recorder replaces the function, so
a test uses one of them.
"""

from dataclasses import dataclass

import pytest
from PySide6.QtCore import QObject
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


@dataclass(frozen=True)
class TextChange:
    """One report that an object's accessible name or description changed.

    Attributes:
        source: The object whose text changed.
        kind: `QAccessible.Event.NameChanged` or `QAccessible.Event.DescriptionChanged`.
    """

    source: QObject
    kind: QAccessible.Event


def record_text_changes(monkeypatch: pytest.MonkeyPatch) -> list[TextChange]:
    """Return a list that collects each report of a changed name or description from now on.

    The event is copied as it arrives, as `record_announcements` copies an
    announcement. Any other accessibility event is passed over.
    """

    recorded: list[TextChange] = []
    kinds = (QAccessible.Event.NameChanged, QAccessible.Event.DescriptionChanged)

    def record(event: QAccessibleEvent) -> None:
        if event.type() in kinds:
            recorded.append(TextChange(event.object(), event.type()))

    monkeypatch.setattr(QAccessible, "updateAccessibility", staticmethod(record))

    return recorded
