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

**Re-entry is read from its record.** A filing's `reenters:` names the closed
item whose fix should have covered it, written by triage's generator check
(project owner, 2026-10-11, ratified, over recording it going forward only and
over shipping without the column). Neither proxy carries the fact: path
recurrence is the arithmetic above, and `root-cause-of:` records members filed
while their head was open.

**A line a successor head answers says so.** A head recorded after a closed
head's fix did not hold carries its own `reenters:` naming that head
(`PL-4097`), so it is counted among the re-entries it explains. The list names
it as the line's successor, read from the same record by `model.is_generator`,
so a reader can tell a settled line from an open one without knowing which
filings are heads (`PL-0WT0`). The answer holds while any successor is open.
Once every successor has closed, three filings that re-enter the line after
the last one closed list it as open again, as below (`PL-SFW9`).

**So does a line answered with no successor owed.** The item that gives that
answer names the line in its own `no-successor:` field, and the list names
that item and its status apart from both other headings (`PL-C4F0`). The
answer was once a paragraph in `PL-4097`'s brief, which nothing here read, so
every run re-asked it. The answer dates from the answering item's `added:`,
which does not move when the item closes, so closing it cannot hide filings
that came after. Three filings that re-enter the line after that date list it
as open again, so a recorded answer cannot hide a mechanism that has started
producing again.

**At release time it is silent unless an expectation failed.** `missed`
checks the last complete period against `PL-04KR`'s pre-registered
predictions, and `docket release` prints what it returns and nothing when it
returns nothing: the owner asked for a report that speaks when the trend is
not the expected one, not a number to watch (2026-09-19).

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
from dataclasses import dataclass, field
from datetime import date

from .config import Config
from .model import MIN_ROOT_CAUSE_ITEMS, Item, is_generator, is_under
from .trend import BY_WEEK, WINDOWS, _windows, window_label

#: What a filing with no `priority:` yet is counted as, so an untriaged capture
#: is shown rather than dropped from the mix.
UNBANDED = "-"

#: `PL-04KR`'s ceiling on new apparatus paths per filing: its baseline read
#: 1.16, 0.26, 0.21, 0.13 over the weeks to 2026-09-19, and the prediction is
#: that it stays at or below the last.
NEW_PATHS_CEILING = 0.13

#: The bands `PL-04KR` predicts no apparatus filing reaches. Its baseline read
#: 0, 2, 1, 0 P1 workflow filings a week; a P0 misses it by more.
UNEXPECTED_BANDS = ("P0", "P1")


def _generator_tier(item: Item) -> bool:
    """Whether `item`'s band records a rank rather than a severity.

    A head raised to `P1` by `generator: live` keeps the band once spent, and
    an `impairs-generators:` item ranks with it. `PL-04KR`'s baseline predates
    that rule (2026-09-21), and from 2026-09-28 to 10-11 heads and such items
    were 8 of the 9 `P1` apparatus filings, so counted, every cut would report
    a generator already found and already ranked.
    """
    return bool(item.root_cause_of or item.impairs_generators)


def _pinned_by_class(item: Item, config: Config, apparatus: frozenset[str]) -> bool:
    """Whether `item`'s band records its class rather than an apparatus severity.

    `docket check` pins a `safety_classes` item to `P0` or `P1`. A simulator
    item of that kind often also declares an instruction file, such as a rule
    under `.claude/rules/` that the change keeps true, and so counts as an
    apparatus filing. Counted as an unexpected band, it reported a broken
    prediction that nothing in the apparatus broke: `PL-HQF5` and `PL-4RL2` in
    the week to 2026-10-18 (`PL-00TR`). A pinned item that reaches any other
    apparatus path still counts, because a safety-classed defect in the
    apparatus is the severity the prediction is about.
    """
    return (
        any(cls in config.safety_classes for cls in item.classes)
        and bool(config.instruction_paths)
        and all(is_under(path, config.instruction_paths) for path in apparatus)
    )


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
    #: Of `filed`, the filings carrying `reenters:` - a shipped fix that did
    #: not reach them. A sweep's own filings are left out with the rest of
    #: `by_head`, so a campaign cannot read as fixes failing.
    reentries: int = 0
    #: Of `filed`, those in `UNEXPECTED_BANDS` for a reason other than the
    #: generator tier or a class pin on a simulator item: what `PL-04KR`'s
    #: prediction is about.
    severe: Mapping[str, int] = field(default_factory=dict)

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
    #: Each closed item that `MIN_ROOT_CAUSE_ITEMS` or more filings re-enter,
    #: with those filings: triage's "three post-close instances of one head"
    #: rule, a generator whose fix did not hold. Counted over the filings
    #: `filed` counts, for the reason `reentries` is.
    reentered: Mapping[str, tuple[str, ...]] = field(default_factory=dict)
    #: For each id in `reentered` a successor answers, the heads whose
    #: `reenters:` names it, by id. Read over every item rather than over the
    #: filings counted, since the record makes a head the successor whether or
    #: not its own `touches` made it an apparatus filing. A line whose heads
    #: have all closed is left out once `MIN_ROOT_CAUSE_ITEMS` filings re-enter
    #: it after the last head closed.
    successors: Mapping[str, tuple[Item, ...]] = field(default_factory=dict)
    #: For each id in `reentered` with no successor, the items whose
    #: `no-successor:` names it and which fewer than `MIN_ROOT_CAUSE_ITEMS`
    #: filings re-enter it after, by id. Read over every item, as `successors`
    #: is.
    answered: Mapping[str, tuple[Item, ...]] = field(default_factory=dict)


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
    reentering: dict[str, list[str]] = {}
    for _, item in filings:
        if item.identifier not in swept:
            for closed in dict.fromkeys(item.reenters):
                reentering.setdefault(closed, []).append(item.identifier)
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
                reentries=sum(1 for item in organic if item.reenters),
                severe=dict(
                    Counter(
                        item.priority
                        for item in organic
                        if item.priority in UNEXPECTED_BANDS
                        and not _generator_tier(item)
                        and not _pinned_by_class(item, config, named[item.identifier])
                    )
                ),
            )
        )
    reentered = {
        closed: tuple(filed)
        for closed, filed in sorted(reentering.items())
        if len(filed) >= MIN_ROOT_CAUSE_ITEMS
    }
    known = {item.identifier for item in items if item.identifier}
    added = {item.identifier: item.added for item in items}
    successors = {
        closed: heads
        for closed, filed in reentered.items()
        if (
            heads := tuple(
                sorted(
                    (
                        item
                        for item in items
                        if closed in item.reenters and is_generator(item, known)
                    ),
                    key=lambda head: head.identifier,
                )
            )
        )
        and _successors_hold(heads, filed, added)
    }
    answered = {
        closed: answers
        for closed, filed in reentered.items()
        if closed not in successors
        and (
            answers := tuple(
                sorted(
                    (
                        item
                        for item in items
                        if closed in item.no_successor
                        and _reentered_after(filed, added, item.added) < MIN_ROOT_CAUSE_ITEMS
                    ),
                    key=lambda answer: answer.identifier,
                )
            )
        )
    }
    return Inflow(
        periods=tuple(periods),
        anchor=anchor,
        by=by,
        excluded=excluded,
        reentered=reentered,
        successors=successors,
        answered=answered,
    )


def _successors_hold(
    heads: Sequence[Item], filed: Sequence[str], added: Mapping[str, date | None]
) -> bool:
    """Whether `heads` still answer a line that `filed` re-enter.

    An open head is still working on the line, so it answers it. Once every
    head has closed, the line counts as answered only until
    `MIN_ROOT_CAUSE_ITEMS` filings re-enter it after the last head closed,
    which is the test a `no-successor:` answer already meets (`PL-SFW9`).
    A closed head with no `closed:` date gives no date to count from, so
    every filing counts against it.
    """
    if any(head.is_open for head in heads):
        return True
    dates = [head.closed for head in heads]
    last = None if None in dates else max(day for day in dates if day is not None)
    return _reentered_after(filed, added, last) < MIN_ROOT_CAUSE_ITEMS


def _reentered_after(
    filed: Sequence[str], added: Mapping[str, date | None], answer: date | None
) -> int:
    """How many of `filed` were filed after `answer`, the date a line was answered.

    An answer with no date has none to count from, so every filing counts.
    """
    return sum(
        1 for identifier in filed if answer is None or (added.get(identifier) or answer) > answer
    )


def missed(report: Inflow, today: date) -> tuple[str, ...]:
    """Each of `PL-04KR`'s predictions the last complete period broke, or `()`.

    The last complete period is the last one that ended before `today`: the
    one holding today is still being filed into, and a short count read as a
    fall is the reassuring direction. Re-entry is compared with the complete
    period before it, since the prediction is that it is flat or falling.
    The predictions are stated per week, so `report` is read by week.
    """
    complete = [period for period in report.periods if period.end < today]
    if not complete:
        return ()
    last = complete[-1]
    out: list[str] = []
    ratio = last.new_paths_per_item
    if ratio is not None and ratio > NEW_PATHS_CEILING:
        out.append(
            f"{last.new_paths} new apparatus paths over {last.filed + last.by_head} filings, "
            f"{ratio:.2f} a filing, above the {NEW_PATHS_CEILING} ceiling: the surface is "
            "still growing"
        )
    if last.severe:
        counted = ", ".join(f"{last.severe[band]} {band}" for band in sorted(last.severe))
        out.append(
            f"{counted} apparatus filing(s) outside the generator tier, where none was expected"
        )
    if len(complete) > 1 and last.reentries > complete[-2].reentries:
        out.append(
            f"{last.reentries} re-entries against {complete[-2].reentries} the period before: "
            "fixes are not holding"
        )
    return tuple(f"{last.label}: {line}" for line in out)
