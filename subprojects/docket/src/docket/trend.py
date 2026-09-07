"""How the balance between the two halves of the project has moved over time.

`docket status` and `docket wave` say where the project stands now. Neither
looks backwards, so "has the apparatus been taking more of the work lately, or
less" could only be answered by a session reading the whole store and the whole
history and classifying both by hand - a full-context derivation of something
entirely decidable, paid again by every session ever asked.

Three measures, and the reason there are three is that no one of them is honest
alone:

- **Closed items** are the obvious count and the most misleading. Apparatus
  work arrives in many small items; measured on this store, workflow items
  average well under the size of product ones, so counting them overstates the
  apparatus by roughly half.
- **Effort-weighted closures** correct for that, at the cost of leaning on a
  size ladder that is a convention rather than a measurement.
- **Churn** - lines written and removed - is the only one read from what
  actually changed rather than from what an item declared, so it is the one
  that still answers when `touches` is missing or wrong. It has its own
  distortion, which is why the queue store is excluded: `docs/items` sits
  inside `workflow_paths`, so every capture and every triage pass would
  otherwise read as apparatus work.

Like `wave`, this computes and decides nothing. Whether the balance it prints
is the right one is a judgment about the project, and a tool that answered it
would be re-opening the same question every run without being able to see what
the run was for.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date, timedelta

from .config import Config
from .model import (
    LANE_CROSSING,
    LANE_PRODUCT,
    LANE_UNPLACED,
    LANE_WORKFLOW,
    PRIORITIES,
    Item,
    is_under,
)
from .release import NOTES_DIR
from .vcs import Churn

QUEUE = "queue"
APPARATUS = "apparatus"
SIM_CODE = "code"
SIM_DOCS = "docs"
ROADMAP = "roadmap"

#: The apparatus half, split so the queue store can be set aside. It is inside
#: `workflow_paths` and belongs there - editing it is apparatus work - but it
#: is also written by every session that captures a finding while doing
#: something else, so counting it makes product sessions look like workflow
#: ones.
WORKFLOW_BUCKETS = (APPARATUS, QUEUE)
#: The product half. `roadmap` is separate because a roadmap file is prose
#: about what the product will be, and a period spent rewriting it is not a
#: period spent building anything.
PRODUCT_BUCKETS = (SIM_CODE, SIM_DOCS, ROADMAP)
BUCKETS = WORKFLOW_BUCKETS + PRODUCT_BUCKETS

#: What each size counts for when closures are weighted rather than counted.
#:
#: A convention, not a measurement, and it is printed alongside the column it
#: produces so a reader can discount it. The ladder is superlinear because the
#: sizes are not a scale - an `L` is aspirational scope that has not been
#: broken down yet, and treating it as three `S` items would understate it as
#: badly as treating every item alike does. An unsized item counts as one,
#: which is the smallest thing it could be, so a store with sizing gaps
#: understates rather than invents.
EFFORT_POINTS: Mapping[str, int] = {"S": 1, "M": 3, "L": 8}

BY_DAY = "day"
BY_WEEK = "week"
WINDOWS: Mapping[str, int] = {BY_DAY: 1, BY_WEEK: 7}


def bucket(path: str, config: Config) -> str:
    """Which half of the project a changed file sits in, and where inside it.

    Tested in the order the categories overlap: the queue store is inside
    `workflow_paths`, and the roadmap deliberately is not, so both have to be
    settled before the general question is asked. `workflow_paths` itself is
    the same boundary `Item.lane` reads, so the churn column and the item
    columns are answering with one rule rather than two that can drift.
    """
    if is_under(path, (config.items_dir,)):
        return QUEUE
    if is_under(path, config.workflow_paths):
        return APPARATUS
    if is_under(path, (config.roadmap_file, NOTES_DIR)):
        return ROADMAP
    if is_under(path, config.code_paths):
        return SIM_CODE
    return SIM_DOCS


def _share(workflow: float, product: float) -> float | None:
    """The workflow fraction of the two, or nothing where neither moved.

    `None` rather than zero, because a period in which nothing happened has no
    balance to report and printing `0%` would read as a period of pure product
    work.
    """
    total = workflow + product
    return workflow / total if total else None


@dataclass(frozen=True)
class Period:
    """One window of the history, on all three measures."""

    start: date
    end: date
    #: Items closed in the window, by lane. Every lane, including the two that
    #: are not a side: work reaching both halves needs a session that can hold
    #: the whole change, and work declaring no `touches` can be placed by
    #: nobody. Folding either into a side would be a verdict the data does not
    #: support, and dropping them is how work goes missing.
    closed: Mapping[str, int]
    #: The same closures, weighted by `EFFORT_POINTS`.
    weighted: Mapping[str, int]
    #: Lines added plus deleted in the window, by bucket.
    churn: Mapping[str, int]

    @property
    def label(self) -> str:
        """The window, with the year written once where both ends share it.

        `2026-08-21..08-27` rather than the pair of full dates: the repeated
        year is four characters of every row that carry no information, and
        the table is read by scanning down a column.
        """
        if self.start == self.end:
            return self.start.isoformat()
        end = self.end.isoformat()
        if self.start.year == self.end.year:
            end = end[len("2026-") :]
        return f"{self.start.isoformat()}..{end}"

    @property
    def is_empty(self) -> bool:
        return not sum(self.closed.values()) and not sum(self.churn.values())

    @property
    def closed_share(self) -> float | None:
        """Workflow's share of the closures a lane could place."""
        return _share(self.closed.get(LANE_WORKFLOW, 0), self.closed.get(LANE_PRODUCT, 0))

    @property
    def weighted_share(self) -> float | None:
        return _share(self.weighted.get(LANE_WORKFLOW, 0), self.weighted.get(LANE_PRODUCT, 0))

    @property
    def apparatus_lines(self) -> int:
        return self.churn.get(APPARATUS, 0)

    @property
    def product_lines(self) -> int:
        return sum(self.churn.get(name, 0) for name in PRODUCT_BUCKETS)

    @property
    def churn_share(self) -> float | None:
        """Apparatus's share of the churn, with the queue store excluded."""
        return _share(self.apparatus_lines, self.product_lines)


@dataclass(frozen=True)
class Trend:
    """The history, and where the queue now points."""

    periods: tuple[Period, ...]
    #: Open items by lane - the leading indicator the closed columns lag.
    open_lanes: Mapping[str, int]
    #: Open items in the top band, by lane. A band nothing occupies is a
    #: sharper statement about a half of the project than any count of the
    #: whole queue.
    top_band: Mapping[str, int]
    top_band_name: str
    by: str
    #: False where git could not be read, so the churn columns are absent
    #: rather than zero.
    has_churn: bool


def _windows(first: date, last: date, span: int) -> list[tuple[date, date]]:
    """Fixed windows from the first day with anything in it.

    Anchored at the start of the history rather than counted back from today,
    so the same store answers the same way tomorrow. Counting back would move
    every boundary each day and make two runs of the command disagree about
    what happened in August.
    """
    out: list[tuple[date, date]] = []
    start = first
    while start <= last:
        out.append((start, min(start + timedelta(days=span - 1), last)))
        start += timedelta(days=span)
    return out


def _first_day(items: Sequence[Item], churn: Churn) -> date | None:
    """The earliest day any column has something to say about.

    Closures and commits only. An item's capture date feeds no column here, so
    anchoring on it would shift every window by however long the queue existed
    before anything closed - moving boundaries for a date the report does not
    otherwise read.
    """
    days = [day for day in churn.by_day]
    days += [item.closed for item in items if item.closed]
    return min(days) if days else None


def analyze(
    items: Sequence[Item],
    churn: Churn,
    config: Config,
    *,
    by: str = BY_WEEK,
    today: date | None = None,
) -> Trend:
    """The whole report, from the store and the history together."""
    last = today or date.today()
    first = _first_day(items, churn)
    span = WINDOWS.get(by, WINDOWS[BY_WEEK])

    periods: list[Period] = []
    for start, end in _windows(first, last, span) if first else []:
        closed: Counter[str] = Counter()
        weighted: Counter[str] = Counter()
        for item in items:
            if item.closed and start <= item.closed <= end:
                lane = item.lane(config.workflow_paths)
                closed[lane] += 1
                weighted[lane] += EFFORT_POINTS.get(item.effort or "", 1)
        lines: Counter[str] = Counter()
        for day, paths in churn.by_day.items():
            if start <= day <= end:
                for path, count in paths.items():
                    lines[bucket(path, config)] += count
        periods.append(
            Period(
                start=start,
                end=end,
                closed=dict(closed),
                weighted=dict(weighted),
                churn=dict(lines),
            )
        )

    open_items = [item for item in items if item.is_open]
    # The highest band anything is actually sitting in, rather than a fixed
    # one. `P0` is a hotfix here and is empty in a healthy store, so naming it
    # unconditionally would spend the sharpest line in the report saying that
    # four lanes hold nothing.
    top_band = next(
        (band for band in PRIORITIES if any(item.priority == band for item in open_items)),
        PRIORITIES[1],
    )
    return Trend(
        periods=tuple(period for period in periods if not period.is_empty),
        open_lanes=dict(Counter(item.lane(config.workflow_paths) for item in open_items)),
        top_band=dict(
            Counter(
                item.lane(config.workflow_paths) for item in open_items if item.priority == top_band
            )
        ),
        top_band_name=top_band,
        by=by,
        has_churn=bool(churn),
    )


LANES = (LANE_WORKFLOW, LANE_PRODUCT, LANE_CROSSING, LANE_UNPLACED)
