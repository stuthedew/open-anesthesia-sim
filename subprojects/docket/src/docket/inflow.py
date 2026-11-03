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

**So does a sweep recorded only as a sweep.** An item whose `sweep:` says its
work is a deliberate search files dozens of items that no head's
`root-cause-of:` names. Counted as ordinary inflow, `PL-K88Z`'s inventory put
9 filings and 5 re-entries into the week of 2026-10-19 (`PL-CJGH`). Which
item's work filed each item is read from git by `vcs.filing_parents`, and
only where some item records a sweep, so a store with none asks git nothing.
Where git cannot answer, the column prints `?` and the report says why, since
those filings are then counted as ordinary.

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

**The product lane counts the other half of that population** (`PL-K5CX`):
an item with a product path that triage's generator check asks about, which is
product work not classed only as new work. `Item.generator_question_paths`
decides both halves. Its question is not the apparatus one, since product
features keep arriving: it is whether a product head's fix held, read from the
same `reenters:` record. `PL-04KR`'s predictions are about the apparatus, so
`missed` reads only the apparatus report.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date

from .config import Config
from .model import (
    LANE_PRODUCT,
    LANE_WORKFLOW,
    MIN_ROOT_CAUSE_ITEMS,
    Item,
    is_generator,
    is_under,
    owner_set_priority,
)
from .trend import BY_WEEK, WINDOWS, _windows, window_label
from .vcs import FilingParents

#: What a filing with no `priority:` yet is counted as, so an untriaged capture
#: is shown rather than dropped from the mix.
UNBANDED = "-"

#: `PL-04KR`'s ceiling on new apparatus paths per filing: its baseline read
#: 1.16, 0.26, 0.21, 0.13 over the weeks to 2026-09-19, and the prediction is
#: that it stays at or below the last. `missed` reads it only in a week whose
#: count of new paths did not fall, for the reason given there (`PL-2T7X`).
NEW_PATHS_CEILING = 0.13

#: The feature that items about `PL-04KR`'s predictions are filed under, so a
#: missed week's investigation is listed where the next cut tells a session
#: to look before filing another (`PL-P6KV`).
INFLOW_FEATURE = "convergence-visibility"

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


def _unexpected_band(item: Item, config: Config) -> bool:
    """Whether `item`'s band is the apparatus severity `PL-04KR` predicts none reaches.

    Three readings of a `P0` or `P1` are left out, because each band records
    something other than how severe an apparatus finding is:

    - **The generator tier**, where the band records a rank (`_generator_tier`).
    - **An owner-set priority**, where the band records the owner's order,
      read from `owner-priority:` by `model.owner_set_priority`. `PL-JRVV`
      was placed at `P1` that way in the week of 2026-10-19 (`PL-P6KV`).
    - **An item outside the workflow lane**, read from `Item.lane`. Such an
      item edits the product as well, so its band can come from the product
      half: a `safety` class pins it to `P1` whatever the apparatus paths are.
      `PL-04KR`'s baseline of 0, 2, 1 and 0 `P1` filings a week counted
      workflow-lane items, and only that population reproduces it over the
      store on 2026-11-03. Counted, crossing items reported `PL-HQF5` and
      `PL-4RL2` for the week to 2026-10-18 (`PL-00TR`), and `PL-M85T`,
      `PL-RNYV` and `PL-S79P` for the week to 10-25 (`PL-P6KV`). The cost is
      that an apparatus defect that also edits a product file is not counted:
      `PL-7FPD` declared `pyproject.toml`, while its twin `PL-H57W` counted.
    """
    return (
        item.priority in UNEXPECTED_BANDS
        and item.lane(config.workflow_paths) == LANE_WORKFLOW
        and not _generator_tier(item)
        and not owner_set_priority(item)
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
    #: `by_head` and `by_sweep`, so a campaign cannot read as fixes failing.
    reentries: int = 0
    #: Of `filed`, the workflow-lane filings in `UNEXPECTED_BANDS` whose band
    #: records severity rather than a rank: what `PL-04KR`'s prediction is
    #: about. `_unexpected_band` says which are left out.
    severe: Mapping[str, int] = field(default_factory=dict)
    #: Apparatus filings that an item's work filed while that item was open,
    #: where the item's `sweep:` records a deliberate search. Counted apart
    #: for the reason `by_head` is. A filing a head also names is counted
    #: there and not here.
    by_sweep: int = 0

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
    def total(self) -> int:
        """Every apparatus filing in the period: ordinary, a head's and a sweep's."""
        return self.filed + self.by_head + self.by_sweep

    @property
    def new_paths_per_item(self) -> float | None:
        """New paths over every apparatus filing, the sweep's included: a sweep names paths too."""
        return self.new_paths / self.total if self.total else None


@dataclass(frozen=True)
class Inflow:
    periods: tuple[InflowPeriod, ...]
    #: The first apparatus filing, which the windows are counted from, or
    #: nothing where there is none.
    anchor: date | None
    by: str
    #: What was left out of the apparatus test, for the key.
    excluded: tuple[str, ...]
    #: Which half of the generator check's population was counted:
    #: `LANE_WORKFLOW` for apparatus filings, `LANE_PRODUCT` for product ones.
    lane: str = LANE_WORKFLOW
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
    #: Why a sweep's filings could not be told apart, or `""`. Set only where
    #: some item records `sweep:` and git could not say which item's work
    #: filed each item. Those filings are then counted in `filed`.
    sweeps_unread: str = ""


def apparatus_paths(item: Item, config: Config, excluded: tuple[str, ...]) -> frozenset[str]:
    """The paths `item` declares under `workflow_paths`, store paths left out."""
    return frozenset(
        path.strip().strip("/")
        for path in item.generator_question_paths(config.workflow_paths, config.new_work_classes)
        if is_under(path, config.workflow_paths) and not is_under(path, excluded)
    )


def product_paths(item: Item, config: Config) -> frozenset[str]:
    """The product paths for which triage's generator check asks `item` where it came from."""
    return frozenset(
        path.strip().strip("/")
        for path in item.generator_question_paths(config.workflow_paths, config.new_work_classes)
        if not is_under(path, config.workflow_paths)
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


def _filed_by_sweep(items: Sequence[Item], filing: FilingParents) -> set[str]:
    """Each id a sweep's work filed between the sweep's filing and its close.

    The window is the one `_filed_by_head` uses. A commit led by the sweep's id
    after the sweep closed is a later correction to it, and what that commit
    files is an ordinary capture.
    """
    sweeps = {item.identifier: item for item in items if item.sweep}
    out: set[str] = set()
    for item in items:
        when = item.added
        if when is None:
            continue
        for parent in filing.parents.get(item.identifier, ()):
            sweep = sweeps.get(parent)
            if sweep is None or sweep.added is None or when < sweep.added:
                continue
            if sweep.closed is None or when <= sweep.closed:
                out.add(item.identifier)
    return out


def analyze(
    items: Sequence[Item],
    config: Config,
    *,
    by: str = BY_WEEK,
    today: date | None = None,
    lane: str = LANE_WORKFLOW,
    filing: FilingParents | None = None,
) -> Inflow:
    """Count the filings in `items` period by period.

    `filing` is `vcs.filing_parents`' answer. It is needed only where an item
    records `sweep:`, and a caller with no such item passes nothing.
    """
    if lane == LANE_PRODUCT:
        excluded: tuple[str, ...] = ()
        named = {item.identifier: product_paths(item, config) for item in items}
    else:
        excluded = store_paths(config)
        named = {item.identifier: apparatus_paths(item, config, excluded) for item in items}
    filings = sorted(
        ((item.added, item) for item in items if item.added is not None and named[item.identifier]),
        key=lambda pair: (pair[0], pair[1].identifier),
    )
    if not filings:
        return Inflow(periods=(), anchor=None, by=by, excluded=excluded, lane=lane)

    headed = _filed_by_head(items)
    sweeps_unread = ""
    by_sweep: set[str] = set()
    if any(item.sweep for item in items):
        if filing is None:
            sweeps_unread = "nothing read which item's work filed each item"
        elif filing.declined:
            sweeps_unread = filing.declined
        else:
            by_sweep = _filed_by_sweep(items, filing) - headed
    swept = headed | by_sweep
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
                by_head=sum(1 for item in window if item.identifier in headed),
                by_sweep=sum(1 for item in window if item.identifier in by_sweep),
                priorities=dict(Counter(item.priority or UNBANDED for item in organic)),
                new_paths=sum(1 for day in first_named.values() if start <= day <= end),
                reentries=sum(1 for item in organic if item.reenters),
                severe=dict(
                    Counter(item.priority for item in organic if _unexpected_band(item, config))
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
        lane=lane,
        reentered=reentered,
        successors=successors,
        answered=answered,
        sweeps_unread=sweeps_unread,
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

    The new-paths ceiling breaks only in a week whose count of new paths is
    at least the count of the complete week before it (`PL-2T7X`). The
    ceiling is a ratio per filing, so it rises whenever filings fall faster
    than new paths. The week of 2026-10-26 named 11 new paths, down from 34,
    over 19 filings, down from 117, and read 0.58 against the 0.13 ceiling.
    The surface grew more slowly that week, which is the convergence
    `PL-04KR` expects. This relaxes the prediction only where the count fell:
    every earlier week reads as it did, so the two weeks that broke the
    ceiling while their counts rose, from 2026-10-12 and 2026-10-19, still
    break it. A first complete week has no week before it, and is read
    against the ceiling alone.
    """
    if report.lane != LANE_WORKFLOW:
        return ()
    complete = [period for period in report.periods if period.end < today]
    if not complete:
        return ()
    last = complete[-1]
    out: list[str] = []
    ratio = last.new_paths_per_item
    before = complete[-2].new_paths if len(complete) > 1 else None
    if (
        ratio is not None
        and ratio > NEW_PATHS_CEILING
        and (before is None or last.new_paths >= before)
    ):
        against = "" if before is None else f", against {before} new the period before"
        out.append(
            f"{last.new_paths} new apparatus paths over {last.total} filings, "
            f"{ratio:.2f} a filing, above the {NEW_PATHS_CEILING} ceiling{against}: the "
            "surface is still growing"
        )
    if last.severe:
        counted = ", ".join(f"{last.severe[band]} {band}" for band in sorted(last.severe))
        out.append(
            f"{counted} apparatus filing(s) in the workflow lane whose band no rank or owner "
            "set, where none was expected"
        )
    if len(complete) > 1 and last.reentries > complete[-2].reentries:
        out.append(
            f"{last.reentries} re-entries against {complete[-2].reentries} the period before: "
            "fixes are not holding"
        )
    lines = [f"{last.label}: {line}" for line in out]
    if lines and report.sweeps_unread:
        lines.append(
            "a sweep's filings could not be told apart, so these counts include them: "
            f"{report.sweeps_unread}"
        )
    return tuple(lines)
