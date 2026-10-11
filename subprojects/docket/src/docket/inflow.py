"""What the apparatus is still being handed, period by period.

`docket trend` looks backwards at what was *closed*. Nothing looked at what was
*filed*, so "is the accumulation slowing?" - the question that says whether the
apparatus lane is converging or being patched one instance at a time - could
only be answered by a session scripting it over the whole store at full context
(`PL-WXKD`). This reports the decidable half of that question. Whether the
numbers it prints are the expected ones is the judgment half, and stays a
session's: like `trend`, it computes and decides nothing.

Three things it deliberately does not do, each refused once already:

- **No single score.** An open-backlog ratio was refuted as a health measure
  (`PL-03XH`), and the owner ruled out any ratio or backlog count for this
  question (`PL-04KR`). Every column is a count or a rate of one thing.
- **No raw path recurrence.** Nearly every filing names a path some closed
  item touched within the 30 days before it - 93% to 100% of each week's
  apparatus filings from 2026-08-31 on, measured 2026-10-11 at file
  granularity as well as at the declared paths - because the surface is small
  and every file in it has been worked recently. A column that reads the same
  every week changes no decision.
- **No backlog columns.** What is still open is `docket status`'s question.

**Who counts.** An item filed with a `touches` path under `workflow_paths`,
whatever its lane, which is the population triage's generator check asks about
(`PL-4NZ7`). The queue store and the notes file are left out of that test and
of the path count, for the reason `trend` leaves the store out of its churn:
they sit inside `workflow_paths`, so every capture made while doing something
else would otherwise read as apparatus inflow.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date

from .config import Config
from .model import Item, is_under
from .trend import BY_WEEK, WINDOWS, _windows, window_label

#: What a filing with no `priority:` yet is counted as, so an untriaged capture
#: is shown rather than dropped from the mix.
UNBANDED = "-"


@dataclass(frozen=True)
class InflowPeriod:
    """One window of filings."""

    start: date
    end: date
    #: Apparatus filings no head explained when they arrived - the inflow the
    #: question is about.
    filed: int
    #: Apparatus filings a head's `root-cause-of:` names, filed while that head
    #: was open: the members a sweep filed, or new instances of a cause already
    #: found. Counted apart because a deliberate sweep files dozens at once, and
    #: folded in it reads as the regression it was hunting - the 2026-09-17 to
    #: 09-19 window had to be cut from `PL-04KR`'s baseline by hand for exactly
    #: that, and in the week to 2026-10-11 it was 60 filings against 46 no head
    #: explained, most of them `PL-R417`'s sweep.
    by_head: int
    #: `filed` by `priority:`, untriaged as `UNBANDED`.
    priorities: Mapping[str, int]
    #: Apparatus paths no earlier filing named. Falling towards zero says the
    #: surface has been covered, which is what tells exhaustion from failure.
    new_paths: int

    @property
    def label(self) -> str:
        return window_label(self.start, self.end)

    @property
    def days(self) -> int:
        return (self.end - self.start).days + 1

    @property
    def per_day(self) -> float:
        """`filed` per day, so a short final window compares with the full ones."""
        return self.filed / self.days

    @property
    def new_paths_per_item(self) -> float | None:
        """New paths over every apparatus filing, the sweep's included: a sweep names paths too."""
        total = self.filed + self.by_head
        return self.new_paths / total if total else None


@dataclass(frozen=True)
class Inflow:
    periods: tuple[InflowPeriod, ...]
    #: The first apparatus filing, which the windows are counted from, or
    #: nothing where there is none.
    anchor: date | None
    by: str
    #: What was left out of the apparatus test, for the key.
    excluded: tuple[str, ...]


def apparatus_paths(item: Item, config: Config, excluded: tuple[str, ...]) -> frozenset[str]:
    """The paths `item` declares under `workflow_paths`, store paths left out."""
    return frozenset(
        path.strip().strip("/")
        for path in item.touches
        if is_under(path, config.workflow_paths) and not is_under(path, excluded)
    )


def store_paths(config: Config) -> tuple[str, ...]:
    """The bookkeeping paths inside `workflow_paths`: the queue store and the notes file."""
    return tuple(path for path in (config.items_dir, config.notes_file) if path)


def _filed_by_head(items: Sequence[Item]) -> set[str]:
    """Each id a head names that was filed between the head's filing and its close.

    A member filed after its head closed is not here: that is a fix that did not
    hold, which is inflow, not a sweep.
    """
    added = {item.identifier: item.added for item in items}
    out: set[str] = set()
    for head in items:
        if not head.root_cause_of or head.added is None:
            continue
        for member in head.root_cause_of:
            when = added.get(member)
            if when is None or when < head.added:
                continue
            if head.closed is None or when <= head.closed:
                out.add(member)
    return out


def analyze(
    items: Sequence[Item], config: Config, *, by: str = BY_WEEK, today: date | None = None
) -> Inflow:
    excluded = store_paths(config)
    named = {item.identifier: apparatus_paths(item, config, excluded) for item in items}
    filings = sorted(
        ((item.added, item) for item in items if item.added is not None and named[item.identifier]),
        key=lambda pair: (pair[0], pair[1].identifier),
    )
    if not filings:
        return Inflow(periods=(), anchor=None, by=by, excluded=excluded)

    swept = _filed_by_head(items)
    first_named: dict[str, date] = {}
    for when, item in filings:
        for path in named[item.identifier]:
            first_named.setdefault(path, when)

    anchor = filings[0][0]
    periods = []
    for start, end in _windows(anchor, today or date.today(), WINDOWS.get(by, WINDOWS[BY_WEEK])):
        window = [item for when, item in filings if start <= when <= end]
        organic = [item for item in window if item.identifier not in swept]
        periods.append(
            InflowPeriod(
                start=start,
                end=end,
                filed=len(organic),
                by_head=len(window) - len(organic),
                priorities=dict(Counter(item.priority or UNBANDED for item in organic)),
                new_paths=sum(1 for day in first_named.values() if start <= day <= end),
            )
        )
    return Inflow(periods=tuple(periods), anchor=anchor, by=by, excluded=excluded)
