"""The what's-left pick list: the gate's open work by feature, and the build that can start now.

`docket picks` answers the question a "what's left" report puts on every
reading, which `next`, `wave`, `status`, `gate` and the digest each answer a
part of. Until `PL-G2HP` a helper rebuilt it by script for every report -
grouping `wave`'s open gate ids by each item's `feature:`, taking lanes from
`Item.lane` and the build from the roadmap's `Required scope` - so the list
was re-derived at full cost where every part of it is decidable from the
store and the plan.

Pure, like `plan`: the command hands in the items, the `Wave`, the ids in
flight and the boundary, and this decides the lines. What a line *buys* in a
sentence, and which line to recommend, are judgment and stay the reply's.

The rules, decided at triage and recorded in `PL-G2HP`'s brief:

- **Population.** The open items of `GateStatus.clearable`, exactly as `wave`
  counts them. What the milestone clears itself and what waits outside the
  gate are counted in one closing line and never offered.
- **Grouping.** By `feature:`. A feature holding two or more of those items
  gets a line of its own; one holding a single item, and items carrying no
  feature, collapse into one line per lane, in `plan.GATE_LANES` order.
- **A live generator head** leads with a line of its own, because `next`
  ranks one above everything here. It is taken out of the grouping, so no
  item is on two lines.
- **Build.** Each `Required scope` entry of the gate's milestone holding an
  item `plan.offerable` now, with how many of the scope's other open items
  wait on it through `blocked-by`.
- **At most `MAX_LINES` lines.** Heads, lane lines and build entries are placed
  first; feature lines fill what is left, largest first, and a feature that
  does not fit folds into its items' lane lines. Build entries past the cap
  collapse into one line.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Collection, Iterable, Mapping
from dataclasses import dataclass

from .model import Item, ranks_as_generator
from .plan import GATE_LANES, Recommendation, awaits_decision, offerable, recommend
from .roadmap import CLEAR, Wave

#: The cap on pick lines: the Report paragraph's "at most eight lines" in the
#: Projects trial's instructions, which the list was built to answer.
MAX_LINES = 8

#: What a line is, which decides how it is rendered.
HEAD = "head"
FEATURE = "feature"
LANE = "lane"
BUILD = "build"
#: Build entries past the cap, collapsed into one line.
BUILD_REST = "build-rest"

#: The bold lead a `Required scope` entry opens with, which names it.
_BOLD_LEAD_RE = re.compile(r"\*\*(?P<lead>.+?)\*\*")


@dataclass(frozen=True)
class PickLine:
    """One line of the list: a group of items a reader can name back."""

    kind: str
    #: The feature, the lane, the head's id, or the scope entry's bold lead.
    name: str
    items: tuple[Item, ...]
    #: Each lane the items sit in with its count, in `GATE_LANES` order.
    lanes: tuple[tuple[str, int], ...]
    awaiting: int
    blocked: int
    in_flight: int
    #: `plan.recommend` over this line's items alone, or `None` where none of
    #: them can be started now.
    pick: Recommendation | None
    #: The `Required scope` entry's number, counted from 1, for a build line.
    entry: int = 0
    #: For a build line, the scope's other open items waiting on the items it
    #: offers through `blocked-by`, at any depth and directly - what starting
    #: it begins to unblock. An item of the same entry that waits on them is
    #: counted, since it is held by them like any other.
    waiting_on_it: int = 0
    waiting_directly: int = 0
    #: For a build line, the scope's open items other than the ones it offers.
    scope_others: int = 0
    #: For the collapsed build line, the entry numbers it holds.
    entries: tuple[int, ...] = ()


@dataclass(frozen=True)
class Picks:
    """The list, and the counts that frame it."""

    milestone: str
    #: Entries `GateStatus.clearable` holds - `wave`'s "N this gate can clear".
    clearable: int
    lines: tuple[PickLine, ...]
    #: Features of two or more items folded into lane lines to keep to the cap.
    folded: tuple[tuple[str, int], ...]
    self_cleared: int
    blocked_outside: int
    #: Whether the beat is still clearing the gate, which the roadmap does
    #: before any build work.
    build_waits: bool
    #: Clearable gate ids led on a generator line rather than grouped.
    led: tuple[str, ...] = ()
    #: Each list entry the plan was not read whole at (`Wave.unread`), so a
    #: count above may be short, named as `wave` names it (`PL-GMR6`).
    unread: tuple[str, ...] = ()


def _lanes(items: Iterable[Item], workflow_paths: tuple[str, ...]) -> tuple[tuple[str, int], ...]:
    found = [item.lane(workflow_paths) for item in items]
    return tuple((lane, found.count(lane)) for lane in GATE_LANES if lane in found)


def _line(
    kind: str,
    name: str,
    items: Iterable[Item],
    in_flight: Collection[str],
    workflow_paths: tuple[str, ...],
    rank: Callable[[list[Item]], Recommendation | None],
    *,
    entry: int = 0,
    waiting: tuple[int, int, int] = (0, 0, 0),
    entries: tuple[int, ...] = (),
) -> PickLine:
    members = tuple(items)
    return PickLine(
        kind=kind,
        name=name,
        items=members,
        lanes=_lanes(members, workflow_paths),
        awaiting=sum(1 for item in members if awaits_decision(item)),
        blocked=sum(1 for item in members if item.status == "blocked"),
        in_flight=sum(1 for item in members if item.identifier in in_flight),
        pick=rank(list(members)),
        entry=entry,
        waiting_on_it=waiting[0],
        waiting_directly=waiting[1],
        scope_others=waiting[2],
        entries=entries,
    )


def bold_lead(text: str) -> str:
    """The name a `Required scope` entry gives itself: its bold lead, less a closing stop."""
    found = _BOLD_LEAD_RE.search(text)
    return found.group("lead").rstrip(".") if found else text.split(". ", 1)[0]


def _waiting_on(
    targets: frozenset[str], open_items: Mapping[str, Item], scope: Collection[str]
) -> tuple[int, int]:
    """How many of `scope`'s open items wait on `targets`, at any depth and directly.

    The walk passes through any open item, in the scope or not, because a
    scope item waiting on an item that waits on the entry is held by the entry
    all the same; only scope items are counted. A closed blocker ends a chain.
    """
    memo: dict[str, bool] = {}

    def reaches(identifier: str, seen: frozenset[str]) -> bool:
        if identifier in memo:
            return memo[identifier]
        item = open_items.get(identifier)
        found = item is not None and any(
            blocker in targets or (blocker not in seen and reaches(blocker, seen | {blocker}))
            for blocker in item.blocking_items
            if blocker in open_items
        )
        memo[identifier] = found
        return found

    others = [i for i in scope if i in open_items and i not in targets]
    directly = sum(1 for i in others if targets & set(open_items[i].blocking_items))
    return sum(1 for i in others if reaches(i, frozenset({i}))), directly


def picks(
    items: list[Item],
    plan: Wave,
    in_flight: Collection[str],
    *,
    workflow_paths: tuple[str, ...] = (),
    generator_paths: tuple[str, ...] = (),
    protected_paths: tuple[str, ...] = (),
    gate_paths: tuple[str, ...] = (),
    limit: int = MAX_LINES,
) -> Picks:
    """The pick list for `plan`'s recorded gate, ranked the way `next` ranks.

    Raises `ValueError` where the plan records no gate: there is then no list
    to print, and `docket wave` says which beat is due instead.
    """
    gate = plan.gate
    if gate is None:
        raise ValueError("the plan records no gate")

    def rank(members: list[Item]) -> Recommendation | None:
        found = recommend(
            members,
            in_flight,
            limit=1,
            scope=plan.scope,
            workflow_paths=workflow_paths,
            generator_paths=generator_paths,
            protected_paths=protected_paths,
            gate_paths=gate_paths,
        )
        return found[0] if found else None

    by_id = {item.identifier: item for item in items}
    open_items = {item.identifier: item for item in items if item.is_open}
    known = frozenset(by_id)

    heads = [item for item in items if item.is_open and ranks_as_generator(item, known)]
    head_ids = {item.identifier for item in heads}
    population: list[Item] = []
    for identifier in dict.fromkeys(i for entry in gate.clearable for i in entry.ids):
        if identifier in open_items:
            population.append(open_items[identifier])
    led = tuple(item.identifier for item in population if item.identifier in head_ids)
    grouped = [item for item in population if item.identifier not in head_ids]

    by_feature: dict[str, list[Item]] = {}
    for item in grouped:
        if item.feature:
            by_feature.setdefault(item.feature, []).append(item)
    candidates = sorted(
        (name for name, members in by_feature.items() if len(members) >= 2),
        key=lambda name: (-len(by_feature[name]), name),
    )

    def lane_count(shown: Collection[str]) -> int:
        rest = [item for item in grouped if not item.feature or item.feature not in shown]
        return len(_lanes(rest, workflow_paths))

    scope_ids = gate.milestone.own_scope_ids
    builds: list[PickLine] = []
    for number, entry in enumerate(gate.milestone.scope_entries, start=1):
        members = [by_id[i] for i in entry.ids if i in by_id]
        startable = offerable(members, in_flight)
        if not startable:
            continue
        targets = frozenset(item.identifier for item in startable)
        waiting, directly = _waiting_on(targets, open_items, scope_ids)
        others = sum(1 for i in scope_ids if i in open_items and i not in targets)
        builds.append(
            _line(
                BUILD,
                bold_lead(entry.text),
                startable,
                in_flight,
                workflow_paths,
                rank,
                entry=number,
                waiting=(waiting, directly, others),
            )
        )

    room = limit - len(heads) - lane_count(())
    if len(builds) > max(room, 1):
        kept, rest = builds[: max(room - 1, 0)], builds[max(room - 1, 0) :]
        builds = [
            *kept,
            _line(
                BUILD_REST,
                "",
                (item for line in rest for item in line.items),
                in_flight,
                workflow_paths,
                rank,
                entries=tuple(line.entry for line in rest),
            ),
        ]

    shown: list[str] = []
    for name in candidates:
        if len(heads) + lane_count([*shown, name]) + len(builds) + len(shown) + 1 <= limit:
            shown.append(name)

    lines = [
        _line(HEAD, item.identifier, (item,), in_flight, workflow_paths, rank) for item in heads
    ]
    lines += [
        _line(FEATURE, name, by_feature[name], in_flight, workflow_paths, rank) for name in shown
    ]
    ungrouped = [item for item in grouped if not item.feature or item.feature not in shown]
    for lane in GATE_LANES:
        in_lane = [item for item in ungrouped if item.lane(workflow_paths) == lane]
        if in_lane:
            lines.append(_line(LANE, lane, in_lane, in_flight, workflow_paths, rank))
    lines += builds

    return Picks(
        milestone=gate.milestone.label,
        clearable=len(gate.clearable),
        lines=tuple(lines),
        folded=tuple((name, len(by_feature[name])) for name in candidates if name not in shown),
        self_cleared=len(gate.self_cleared),
        blocked_outside=len(gate.blocked_outside),
        build_waits=plan.beat == CLEAR,
        led=led,
        unread=plan.unread,
    )
