"""Where simulator defects land, read at each release cut (`PL-36R0`).

A source file that keeps collecting defects for different reasons usually has
a design problem that no single item names. Kim, Zimmermann, Whitehead and
Zeller, "Predicting Faults from Cached History", ICSE 2007, found in seven
projects that 10% of the files, chosen from the recent history of faults and
changes, held 73% to 95% of the later faults, and that faults arrive in bursts
in the same files. Triage's generator check reads each filing
for the fact it misread, so it cannot see unrelated misreads landing in one
file.

This module counts, for each simulator source file, the defect-classed items
filed in the weeks before a cut whose `touches` declare it. A declared file is
an item's scope rather than proof that the fault lay there, so the reading is
a lead for a design review and never a gate.

The reading names a file only where a review is owed. That is a file among the
`HOTSPOT_FILES` with the most such items that no design review covers. A
design review is an item filed under `REVIEW_FEATURE` whose `touches` name the
file. An open review covers its files. A finished one covers them until
`MIN_ROOT_CAUSE_ITEMS` more defects are filed against the file after it
closed, which is triage's rule for a fix that did not hold.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

from .config import Config
from .inflow import TREND_WEEKS
from .model import MIN_ROOT_CAUSE_ITEMS, Item, is_under

#: How many of the files with the most defects are read at a cut. Few enough
#: that each can have a design review, and close to the 10% of files that Kim
#: et al. (2007) found holding most faults: about 70 source files collected a
#: defect in the eight weeks to 2026-11-23.
HOTSPOT_FILES = 5

#: The weeks before the cut whose filings are counted. They are as many as the
#: inflow trend test reads, so one cut reports on one stretch of time.
HOTSPOT_WEEKS = TREND_WEEKS

#: The feature a design review of a hotspot is filed under.
REVIEW_FEATURE = "hotspot-review"

#: The class that marks an item as a defect. The project's safety classes
#: count too, since each marks work in which a wrong value could mislead.
DEFECT_CLASS = "defect"


@dataclass(frozen=True)
class Hotspot:
    """One source file among those with the most defects in the window."""

    path: str
    #: Defect-classed items filed in the window that declare the file.
    defects: int
    #: The file's length today, so a reader can weigh the count by size.
    lines: int
    #: The source file those defects most often declare alongside this one,
    #: and how many do, or `None` and 0 where none declares another.
    partner: str | None
    together: int
    #: Design reviews whose `touches` name the file, open or closed.
    reviews: tuple[Item, ...]
    #: Defects filed against the file after its last finished review closed,
    #: or `None` where it has no finished review.
    since_review: int | None

    @property
    def last_review(self) -> Item | None:
        """The finished review that closed last, or `None`."""
        return last_finished(self.reviews)

    @property
    def owed(self) -> bool:
        """Whether no open review covers the file and no finished one still does."""
        if any(review.is_open for review in self.reviews):
            return False
        return self.since_review is None or self.since_review >= MIN_ROOT_CAUSE_ITEMS


@dataclass(frozen=True)
class Hotspots:
    """The files with the most defects filed from `start` to `end`, most first."""

    start: date
    end: date
    #: The classes an item counted carries at least one of.
    classes: tuple[str, ...]
    files: tuple[Hotspot, ...]

    @property
    def owed(self) -> tuple[Hotspot, ...]:
        return tuple(hotspot for hotspot in self.files if hotspot.owed)


def last_finished(reviews: Sequence[Item]) -> Item | None:
    """The review among `reviews` that was done and closed last, or `None`.

    A dropped review did not happen, so it covers nothing.
    """
    done = [review for review in reviews if review.status == "done" and review.closed]
    return max(done, key=lambda review: (review.closed, review.identifier), default=None)


def read(items: Sequence[Item], config: Config, root: Path, today: date) -> Hotspots:
    """Read the files with the most defects filed in the `HOTSPOT_WEEKS` before `today`.

    A file counts when an item's `touches` name it, it lies under
    `product_paths`, it is Python source rather than a document or a data
    file, and it exists under `root` today. A file since removed or renamed
    cannot be reviewed, so it is left out. A defect filed on `today` itself is
    left out with the rest of the day still to come.
    """
    end = today - timedelta(days=1)
    start = today - timedelta(days=7 * HOTSPOT_WEEKS)
    exists: dict[str, bool] = {}

    def sources(item: Item) -> tuple[str, ...]:
        found = []
        for path in dict.fromkeys(item.touches):
            if not path.endswith(".py") or not is_under(path, config.product_paths):
                continue
            if path not in exists:
                exists[path] = (root / path).is_file()
            if exists[path]:
                found.append(path)
        return tuple(found)

    classes = (DEFECT_CLASS, *config.safety_classes)
    defects = [
        item for item in items if item.added and any(name in classes for name in item.classes)
    ]
    declared = {item.identifier: sources(item) for item in defects}
    window = [item for item in defects if item.added and start <= item.added <= end]
    counts = Counter(path for item in window for path in declared[item.identifier])
    top = sorted(counts, key=lambda path: (-counts[path], path))[:HOTSPOT_FILES]
    reviews = [item for item in items if item.feature == REVIEW_FEATURE]

    files = []
    for path in top:
        partners = Counter(
            other
            for item in window
            if path in declared[item.identifier]
            for other in declared[item.identifier]
            if other != path
        )
        partner = min(partners, key=lambda other: (-partners[other], other), default=None)
        covering = tuple(
            sorted(
                (review for review in reviews if is_under(path, review.touches)),
                key=lambda review: review.identifier,
            )
        )
        last = last_finished(covering)
        since = (
            None
            if last is None or last.closed is None
            else sum(
                1
                for item in defects
                if item.added and item.added > last.closed and path in declared[item.identifier]
            )
        )
        with (root / path).open(encoding="utf-8") as text:
            lines = sum(1 for _ in text)
        files.append(
            Hotspot(
                path=path,
                defects=counts[path],
                lines=lines,
                partner=partner,
                together=partners[partner] if partner else 0,
                reviews=covering,
                since_review=since,
            )
        )
    return Hotspots(start=start, end=end, classes=classes, files=tuple(files))
