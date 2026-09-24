"""Choosing what to work on, and grouping work into things worth shipping.

Two failure modes this module exists to prevent, both of them expensive and
neither visible from a single item.

The first is scatter: picking the highest-priority item each time produces a
project where fifteen features are each five percent done and nothing is
finished. Work that belongs to a feature already underway is worth more than
equally-ranked work that starts a new one, because a finished feature can
ship and a half-finished one cannot. Among several underway, the one nearest
finishing wins, for the same reason: it is the one a session can actually
close.

The second is starting what someone else is already doing. That is knowable
from branch names, so it is checked rather than left to memory.
"""

from __future__ import annotations

from collections.abc import Collection, Mapping
from dataclasses import dataclass, field
from datetime import date

from .model import (
    CLOSED_STATUSES,
    EFFORTS,
    LANE_CROSSING,
    LANE_UNPLACED,
    MIN_RECURRENCES,
    PRIORITIES,
    Item,
    impairs_generators_soundly,
    is_generator,
    ranks_as_generator,
    recurrence_count,
)
from .roadmap import EXCLUDED, IN_SCOPE, OUT_OF_SCOPE, UNPLACED, MilestoneStates, Scope


@dataclass(frozen=True)
class Feature:
    """A coherent chunk of functionality, which may span several items."""

    name: str
    items: list[Item]

    @property
    def done(self) -> list[Item]:
        return [i for i in self.items if i.status == "done"]

    @property
    def open_items(self) -> list[Item]:
        return [i for i in self.items if i.is_open]

    @property
    def is_complete(self) -> bool:
        return bool(self.items) and not self.open_items

    @property
    def progress(self) -> float:
        return len(self.done) / len(self.items) if self.items else 0.0

    @property
    def is_underway(self) -> bool:
        """Started but not finished - the state worth finishing before starting more."""
        return bool(self.done) and bool(self.open_items)


@dataclass(frozen=True)
class Cluster:
    """A generator and the items its `root-cause-of:` names - the unit that drains.

    `Feature` above is the analogue, and the reason this is a second type
    rather than a reuse of it is the head. A feature is a set of items sharing
    a name, and its own progress is the whole of its story; a cluster has an
    item *above* it whose status answers a different question. Every generator
    this project has recorded is closed while most of what each one named is
    not, so a reader taking `done` on the head for the cluster's state reads
    the work as finished when 58 of 99 members are open (`PL-XF5V`).

    **The buckets are split by the head's own close date, not merged into one
    count, because a third of the edges cannot be ordered.** `closed:` is a
    date and not a timestamp, so a member closed on the head's close date may
    have closed with it or hours after it - 32 of this store's 99 member
    closures are that case. A single "open at the head's close" number would
    have to pick one reading and print it as fact. Naming the same-day bucket
    separately says exactly what the date supports, which is the floor
    `.claude/rules/apparatus-standard.md` sets for an answer this package
    gives.
    """

    head: Item
    members: list[Item]

    @property
    def done(self) -> list[Item]:
        return [i for i in self.members if i.status == "done"]

    @property
    def open_items(self) -> list[Item]:
        return [i for i in self.members if i.is_open]

    @property
    def is_drained(self) -> bool:
        """Every member closed - the state that makes a generator finished work."""
        return bool(self.members) and not self.open_items

    @property
    def closed_since_head(self) -> list[Item]:
        """Members closed strictly after the head did: the drain since the fix.

        The trend the present split cannot carry. "58 of 99 open" was derived
        twice two days apart and came back unchanged, and it was the
        *unchanged* that made the answer useful; nothing stored that, and this
        recovers it from the dates already in the store rather than from a new
        field (project owner, 2026-09-21).
        """
        if self.head.closed is None:
            return []
        return [i for i in self.members if i.closed is not None and i.closed > self.head.closed]

    @property
    def closed_with_head(self) -> list[Item]:
        """Members whose `closed:` is the head's own date - the unorderable bucket."""
        if self.head.closed is None:
            return []
        return [i for i in self.members if i.closed is not None and i.closed == self.head.closed]

    @property
    def closed_before_head(self) -> list[Item]:
        """Members already closed when the head closed.

        A head is filed once a mechanism is seen standing under three items,
        which can be after some of them were worked singly, so this is not
        drain and is counted apart from it.
        """
        if self.head.closed is None:
            return [i for i in self.members if not i.is_open]
        return [i for i in self.members if i.closed is not None and i.closed < self.head.closed]


def clusters(items: list[Item], known: Collection[str] | None = None) -> dict[str, Cluster]:
    """Every sound generator head with the members it names, by head id.

    Soundness is `is_generator`'s test, which is the same one `checks.py` and
    `recommend` apply - so a claim this report counts is exactly a claim the
    checker accepts and the ranking lifts. A head whose field is faulty is
    left out here and named by `format_clusters` instead of being silently
    dropped: an unsound claim is invisible to `docket next` too, and a report
    that omitted it without saying so would hand over a partial reading as a
    complete one.

    Members are looked up across every item, the closed ones included, for the
    reason `generators_explaining` gives: a root cause still explains an item
    that has since closed, and a cluster whose edges decayed as it drained
    could never report that it had drained.
    """
    by_id = {item.identifier: item for item in items if item.identifier}
    resolved = set(by_id) if known is None else set(known)
    heads = [item for item in items if item.identifier and is_generator(item, resolved)]
    return {
        head.identifier: Cluster(
            head,
            sorted(
                (by_id[m] for m in dict.fromkeys(head.root_cause_of) if m in by_id),
                key=lambda i: i.sort_key(),
            ),
        )
        for head in sorted(heads, key=lambda i: i.identifier)
    }


@dataclass(frozen=True)
class Overlap:
    """Two sound generator heads whose clusters touch, and how.

    `first` is the head with the lower id, so a pair reads the same whichever
    head a reader started from. `shared` is the members both name, by id;
    `first_names_second` and `second_names_first` say that one head's own
    members include the other head - the nesting case, which is a pair even
    where no member is shared.
    """

    first: Item
    second: Item
    shared: tuple[str, ...]
    first_names_second: bool
    second_names_first: bool


def overlaps(groups: Mapping[str, Cluster]) -> list[Overlap]:
    """Every pair of sound heads whose member lists share an id, or nest.

    **A fact about two lists, not a verdict that the heads share a record.**
    Triage compared each new item with one head at a time and never compared
    heads with each other, so one record read by several readers got a head
    per reader (`PL-5MYR`). The intersection is the decidable half of that
    comparison: on 2026-09-23 it named 11 pairs sharing a member, plus one
    pair that only nests - `PL-BHVM` names `PL-R808` - and recovered three of
    the five shared records `PL-T7Y1`'s audit verified and both of its
    misattributions. It cannot see a shared record whose members are
    disjoint, and it missed two of the audit's five that way (`PL-J6HP` with
    `PL-WD5Z`, `PL-6TP8` with `PL-1P5V`); that is what each head's `misread:`
    line is for, and comparing those lines is a session's judgment.

    Only the heads `clusters` accepts, so a pair here is one `docket check`
    and the ranking both recognise. Ordered by the pair's ids, lower first.
    """
    heads = sorted(groups.values(), key=lambda cluster: cluster.head.identifier)
    members = {
        cluster.head.identifier: {item.identifier for item in cluster.members} for cluster in heads
    }
    found: list[Overlap] = []
    for index, first in enumerate(heads):
        one = first.head.identifier
        for second in heads[index + 1 :]:
            other = second.head.identifier
            shared = tuple(sorted(members[one] & members[other]))
            first_names_second = other in members[one]
            second_names_first = one in members[other]
            if shared or first_names_second or second_names_first:
                found.append(
                    Overlap(first.head, second.head, shared, first_names_second, second_names_first)
                )
    return found


def unsound_generator_claims(items: list[Item]) -> list[Item]:
    """Items carrying `root-cause-of:` that `is_generator` refuses.

    What `clusters` could not count, so that the report can say so. `docket
    check` is a separate command and a store is routinely read before it is
    validated, so these exist in practice rather than in principle.
    """
    known = {item.identifier for item in items if item.identifier}
    return sorted(
        (i for i in items if i.root_cause_of and not is_generator(i, known)),
        key=lambda i: i.identifier,
    )


def generator_defects(items: list[Item], generator_paths: tuple[str, ...]) -> list[Item]:
    """Items on the generator tier by `impairs-generators:` - tier, but no cluster.

    They rank with a generator and have no members, so they are neither a
    cluster nor absent from the question "are the generators dealt with": a
    count of heads that ignored them is off by the number of them, which is
    how `PL-XF5V`'s own brief came to say twelve heads over a table of eleven.
    """
    return sorted(
        (i for i in items if impairs_generators_soundly(i, generator_paths)),
        key=lambda i: i.identifier,
    )


@dataclass(frozen=True)
class Gate:
    """Every open debt item in the store, split by the `feature` it carries.

    What a freeze starts from, and not the rule it ends with. `ROADMAP.md` §
    "Debt inside the milestone's own scope" decides which debt a milestone
    clears *itself* by whether its `Required scope` names the id, and
    `roadmap.gate_status` applies that test to the frozen list. A feature is a
    fact in the file and a reasonable first cut, but the two sets differ in
    both directions: an item can carry the feature without being named, and
    be named without carrying it. So nothing reading this calls `inside` what
    the milestone clears itself - `PL-YVP7` was filed on that reading, and
    `PL-RFHH` is why the output stopped offering it.
    """

    feature: str
    #: Open debt carrying the feature.
    inside: list[Item]
    #: Every other open debt item.
    outside: list[Item]

    @property
    def items(self) -> list[Item]:
        return self.outside + self.inside


def effort_total(items: list[Item]) -> str:
    """The sizes in a batch, largest first: the shape a plan records them in."""
    counts = {effort: sum(1 for i in items if i.effort == effort) for effort in reversed(EFFORTS)}
    parts = [f"{count} {effort}" for effort, count in counts.items() if count]
    unsized = sum(1 for i in items if i.effort not in EFFORTS)
    if unsized:
        parts.append(f"{unsized} unsized")
    return ", ".join(parts) if parts else "nothing"


def is_debt(item: Item, debt_classes: tuple[str, ...]) -> bool:
    """Whether an open item is recorded debt rather than new work.

    Two rules, and the second wins where they meet. Debt is what the classes
    say it is - `defect`, `safety`, `science`, `refactor`, `perf` here - and
    an unanswered decision is debt whatever it is about, because a decision
    left open stops being one anybody can make. So a `feature`-classed item
    sitting at `needs-decision` is debt: what is owed is the decision, not the
    feature.
    """
    if not item.is_open:
        return False
    if item.status == "needs-decision":
        return True
    return any(cls in debt_classes for cls in item.classes)


def is_new_work(
    item: Item, new_work_classes: tuple[str, ...], debt_classes: tuple[str, ...]
) -> bool:
    """Whether an open item is new work, which `docket next --oldest` leaves out.

    The one exclusion from what that command treats as owed. Everything else a
    session marked as wanting doing and set aside is owed, including the
    `docs`, `infra` and `test` work `is_debt` never counts - which is the
    at-risk set, because no gate will ever hold it (`PL-Q89J`).

    `is_debt` wins where the two meet: a `needs-decision` item is owed whatever
    it is about, and a debt class beside a new-work one keeps the item owed.
    Otherwise `docket gate` and `--oldest` could disagree about one item, which
    is the hazard the flag's name was chosen to avoid.
    """
    if is_debt(item, debt_classes):
        return False
    return any(cls in new_work_classes for cls in item.classes)


def gate(items: list[Item], feature: str, debt_classes: tuple[str, ...]) -> Gate:
    """Every open debt item in the store, split by whether it carries `feature`.

    It computes the list and nothing else. Whether an item is *really* debt,
    whether the gate should open, and what is written into the plan are
    judgments, and recording the frozen list stays a deliberate act - the
    command removes the transcription, not the decision.
    """
    debt = sorted((i for i in items if is_debt(i, debt_classes)), key=lambda i: i.sort_key())
    inside = [i for i in debt if feature and i.feature == feature]
    outside = [i for i in debt if not (feature and i.feature == feature)]
    return Gate(feature=feature, inside=inside, outside=outside)


def features(items: list[Item]) -> dict[str, Feature]:
    grouped: dict[str, list[Item]] = {}
    for item in items:
        if item.feature:
            grouped.setdefault(item.feature, []).append(item)
    return {
        name: Feature(name, sorted(grouped[name], key=lambda i: i.sort_key()))
        for name in sorted(grouped)
    }


#: Where the plan places an item, as a sort position. In-scope work is
#: preferred over out-of-scope work absolutely rather than inside a band,
#: because the priority field cannot express the phase: `docket check` pins
#: `safety` and `science` items to `P1`, so the top band is product work by
#: construction and a tie-breaker inside a band would never fire in the case
#: this exists for. Work the roadmap places nowhere sits between the two - it
#: is not what the step is for, and nothing says it is excluded either. Work
#: the anchor has ruled out sorts below all of it: the roadmap has taken a
#: decision about that id, where an out-of-scope one is only waiting for its
#: own step to come round (`PL-6P9Y`).
PLACEMENT_ORDER = {IN_SCOPE: 0, UNPLACED: 1, OUT_OF_SCOPE: 2, EXCLUDED: 3}


@dataclass(frozen=True)
class Recommendation:
    """One suggested next piece of work, and why it is being suggested."""

    item: Item
    reason: str
    #: What the plan says about this item, when a roadmap was read: empty for
    #: work it places in the current step or nowhere at all, and the milestone
    #: naming it otherwise.
    scoped_to: str = ""
    #: How many items this one is the recorded root cause of, or `0`. Carried
    #: here rather than re-derived by each reader, for the reason `scoped_to`
    #: is: resolving the claim needs the whole store, and `format_digest`'s
    #: `Top:` line has only the `Recommendation`. Without it that line shows a
    #: `P2` leading a queue with `P1`s in it and nothing saying why, which is
    #: the first thing every session reads.
    generator: int = 0
    #: Whether this item ranked as a defect in the generator machinery - the
    #: tier's other entrance, carried separately because it is a different
    #: claim with a different warrant. A generator names the items standing on
    #: it and the count is the evidence; a machinery defect names none, and
    #: what a reader checks instead is the declared prose. Folding the two
    #: into one count would print "root cause of 0 items" on an item that
    #: outranks every `P1`.
    impairs_generators: bool = False
    #: The blocked live generator heads this item is an open blocker of, by id,
    #: or `()` - the rank those heads cannot hold while blocked, passed down to
    #: the work they wait on (`generator_blockers`). Carried for the reason
    #: `generator` is: the digest's `Top:` line has only the `Recommendation`,
    #: and the build item a design round filed would lead it as a bare `P2`.
    unblocks: tuple[str, ...] = ()
    #: Whether a cheaper model may take this item, from `Item.delegability`.
    #: Carried here for the reason `scoped_to` and `generator` are: the answer
    #: needs `protected_paths` and `gate_paths`, which `describe` cannot
    #: reach. Defaults to `False`, so a caller threading no configuration
    #: offers nothing - the same fail-closed reading `delegability` gives an
    #: empty `protected_paths`, arrived at from the other end.
    delegable: bool = False

    def describe(self) -> str:
        marks = [m for m in (self.item.effort, self.item.status) if m]
        if self.item.model_guidance:
            marks.append(f"{self.item.model_guidance} - use your strongest model")
        elif self.delegable:
            # `elif` rather than a second `if`, mirroring `render._marks`. The
            # two are already mutually exclusive - `delegability` returns the
            # guidance string itself whenever `model_guidance` is set - so this
            # says so where a reader looks, rather than leaving them to check.
            # Which model is cheaper is deliberately not named here: the answer
            # dates, and `docs/maintainer.md` is where a dated instance lives.
            marks.append("delegable - a cheaper model may take this")
        if self.generator:
            marks.append(f"root cause of {self.generator} items")
        if self.impairs_generators:
            marks.append("defect in the generator machinery")
        if self.unblocks:
            marks.append(f"unblocks generator {', '.join(self.unblocks)}")
        if self.scoped_to:
            marks.append(f"scoped to {self.scoped_to}, not this step")
        head = f"{self.item.priority} {self.item.identifier} {self.item.title}"
        # Consequence before mechanism, which is the order the `docket` skill
        # requires of a reply offering an item: the title above names what the
        # work does, `reason` below says why it ranked, and neither answers
        # "why would I want this". A pick carrying no payoff reads exactly as
        # it did before.
        lines = [f"{head} ({', '.join(marks)})"]
        if self.item.payoff:
            lines.append(f"    payoff: {self.item.payoff}")
        lines.append(f"    {self.reason}")
        return "\n".join(lines)


@dataclass(frozen=True)
class OfferedReport:
    """Which ids `next` is about to offer, and whether that could be settled.

    A type rather than the `frozenset[str]` this used to be, for the reason
    `FlightReport` gives about its own ids: ranking reads in-flight work, a
    ref whose commits this checkout cannot walk contributes nothing to that
    reading, and a bare set is exactly the shape that cannot say so. The
    advisories computed from it - which item is next and names no `verify:`
    command - then rest on a partial answer with nothing saying they do.

    `declined` is the sentence explaining what went unread, empty when the
    ranking was whole. Worded by the caller, which is the one place that knows
    what it could not read; this module only carries it to the checker.
    """

    ids: frozenset[str] = frozenset()
    declined: str = ""


@dataclass(frozen=True)
class SetAside:
    """Startable work a lane could not claim, so that no lane hides any.

    A lane is a filter, and a filter that drops 19% of a queue without saying
    so is how work goes missing for months. The two reasons are separated
    because they call for different repairs: `crossing` needs a session that
    can hold both halves, while `unplaced` needs somebody to write a
    `touches` line.
    """

    #: Startable items reaching both halves of the project.
    crossing: list[Item] = field(default_factory=list)
    #: Startable items declaring no `touches`, so no lane can place them.
    unplaced: list[Item] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.crossing) + len(self.unplaced)


def set_aside(
    items: list[Item],
    in_flight: Collection[str] | None = None,
    *,
    workflow_paths: tuple[str, ...] = (),
    effort: str | None = None,
) -> SetAside:
    """What a lane filter would drop, split by why it could not be placed.

    Takes the same exclusions `recommend` does - in flight, and the effort
    filter - so the count reported beside a ranking describes that ranking,
    rather than a queue neither session was looking at.
    """
    held = [
        item
        for item in _startable(items, in_flight, effort=effort)
        if item.lane(workflow_paths) in (LANE_CROSSING, LANE_UNPLACED)
    ]
    return SetAside(
        crossing=[i for i in held if i.lane(workflow_paths) == LANE_CROSSING],
        unplaced=[i for i in held if i.lane(workflow_paths) == LANE_UNPLACED],
    )


def _startable(
    items: list[Item], in_flight: Collection[str] | None = None, *, effort: str | None = None
) -> list[Item]:
    """Work that could be begun now, before any lane narrows it.

    Shared by `recommend` and `set_aside` so the two cannot disagree about
    what "startable" means - the set-aside count is only honest if it is
    counted from the same population the ranking drew from.
    """
    flight = in_flight or set()
    return [
        item
        for item in items
        if item.is_open
        and not item.is_untriaged
        and item.status != "blocked"
        and item.identifier not in flight
        and (effort is None or item.effort == effort)
    ]


def promotable(items: list[Item]) -> list[Item]:
    """Blocked items whose every recorded item blocker has closed.

    `_startable` filters on `status` alone and never opens `blocked_by`, so an
    item stays out of the ranking until somebody grooms the status by hand -
    however long ago the thing it waited for closed. `docket check` has derived
    this same set all along and says so in an advisory. This exports the
    reading so `docket next` can name the ids at the moment a session is
    choosing, rather than leaving them to a command it has no reason to run:
    on 2026-09-17 the head of the chain holding three more of v0.5.0's own
    scope was invisible that way (`PL-6T44`).

    **Candidates, never a verdict.** That every blocker has closed is a fact
    about the field; that nothing *else* holds the item is not, and the
    difference is most of the answer. Of 13 items reached this way across two
    grooming passes (`PL-JFQ3`, 2026-09-16; `PL-8G48`, 2026-09-20), 6 were
    genuinely startable - the rest were already done inside another item, or
    had a user-facing question written into them since triage, or waited on
    something nobody had declared. So callers name these and must not rank
    them: a recomputed status would have put an unbuildable item into `P1` and
    onto the debt gate, because leaving `blocked` is what ends the
    `anticipated` exemption.

    Item blockers only. A milestone blocker clears when a scoping round
    happens, which takes the roadmap to answer and is a different question
    from this one; `checks.py` keeps that branch, and `PL-162Y` is whether
    `next` should name those too.

    An id the store cannot place counts as unresolved, which is the
    fail-closed half: a `blocked-by` naming nothing is not evidence that the
    blocker closed.
    """
    resolved = {
        item.identifier for item in items if item.identifier and item.status in CLOSED_STATUSES
    }
    return sorted(
        (
            item
            for item in items
            if item.status == "blocked"
            and item.blocked_by
            and not item.blocking_milestones
            and set(item.blocking_items) <= resolved
        ),
        key=lambda item: item.identifier,
    )


def generator_blockers(items: list[Item]) -> dict[str, tuple[Item, ...]]:
    """Open items a blocked live generator waits on, each with the heads it unblocks.

    A head at `blocked` is startable by nothing, so `recommend` never ranks it
    and its `generator: live` lifts nothing - and the items it waits on carry no
    claim of their own, so each ranks on its band. That is the shape a design
    round leaves when it decomposes a generator's fix, because `status: ready`
    may not declare an open blocker: `PL-MB2W`'s round blocked the head on
    eight build items, and the one startable among them dropped to an ordinary
    `P2` among 149 (`PL-QFWF`). The rank is the head's, and it passes to what
    the head waits on, since that is the work paying the generator down now.

    **Only what the head holds itself.** The test is `ranks_as_generator`, so a
    spent or unqualified head passes nothing and its blockers rank on their
    bands, as it would. Only a `blocked` head passes it, since blocking is what
    took it off the tier: a `ready` or `needs-decision` head is startable and
    holds the rank itself, and an untriaged one has not been seated to hold any.

    **Direct blockers only.** A blocker that is blocked itself passes nothing
    further down. The tier is the one rank above a `safety`-classed `P1`, and
    each edge between a head and what it lifts is a hand-written `blocked-by`
    nothing checks for this purpose, so one edge from a head whose claim
    `docket check` validates is the narrowest reading covering the recorded
    shape - a head blocked on each of its build items. A chain, or a head
    waiting on a milestone alone, still lifts nothing, and `unranked_generators`
    names the head instead of ranking further down (`PL-4RK2`).

    Keyed by blocker id, heads in id order. Every open blocker is listed,
    startable or not: `recommend` ranks only what it can start, and `docket
    show` asks about the one item it was handed, where a blocker still waiting
    on another is on the tier as a blocked head is - from the moment it can
    be started.
    """
    known = {item.identifier for item in items if item.identifier}
    open_ids = {item.identifier for item in items if item.identifier and item.is_open}
    lifted: dict[str, list[Item]] = {}
    for head in sorted(items, key=lambda i: i.identifier):
        if head.status != "blocked" or not ranks_as_generator(head, known):
            continue
        for blocker in dict.fromkeys(head.blocking_items):
            if blocker in open_ids and blocker != head.identifier:
                lifted.setdefault(blocker, []).append(head)
    return {blocker: tuple(heads) for blocker, heads in lifted.items()}


@dataclass(frozen=True)
class UnrankedGenerator:
    """A blocked live generator head whose rank reaches nothing `next` can offer."""

    head: Item
    #: What the head waits on and cannot start: its open item blockers in the
    #: order `blocked-by` writes them, an id the store cannot place included,
    #: then the milestones that have not cleared for it. Empty where every
    #: blocker it names has closed or cleared, or where it names none but itself.
    waiting_on: tuple[str, ...]
    #: Startable or in-flight items at the far end of a chain - reached through
    #: blockers that are themselves `blocked`, by id. The work the rank would
    #: reach if the head's own `blocked-by` named it, which is the remedy.
    behind: tuple[str, ...]


def unranked_generators(
    items: list[Item],
    in_flight: Collection[str] | None = None,
    *,
    milestones: MilestoneStates | None = None,
) -> list[UnrankedGenerator]:
    """Blocked live generator heads whose rank reaches no item `next` could offer.

    `generator_blockers` passes a blocked head's rank one edge down, to the
    open items its own `blocked-by` names, and deliberately no further. So a
    head whose every open blocker is itself blocked, untriaged or unknown, or
    which waits on a milestone alone, is ranked by nothing, and until this
    nothing said so: the tier exists so a live generator is paid down before
    the sessions it taxes, and in these shapes it went unranked silently
    (`PL-4RK2`).

    **Named, never ranked - the chain is not followed.** Each edge past the
    first is a `blocked-by` written for sequencing and never checked for what
    it would now buy, which is the one rank above a `safety`-classed `P1`. So
    this reports the shape and the startable work behind it (`behind`), and
    the remedy is a person writing that work into the head's own `blocked-by`,
    where the rank then passes by the reading above. That is the recorded
    decision about the evidence one more edge needs, made per head rather than
    once for every chain.

    **Carried** means some open direct blocker is startable - `recommend`
    ranks it on the tier - or in flight, where a session is paying the edge
    down now. A head in flight is left out for the second reason. A head
    whose every blocker has closed or cleared is named too, with nothing in
    `waiting_on`: `promotable` or `docket check` says the status is stale, and
    this says the item it would restore is a live generator.

    A milestone blocker clears as `docket check` reads it - scoped, and not
    one whose scope names the head, which waits for the release instead - so
    `milestones` is the roadmap's `MilestoneStates`. `None`, an unread
    roadmap, clears none of them, and the caller says it could not tell.

    The traversal behind a chain passes only through `blocked` items, since
    an untriaged one has not been seated to wait on anything, and is
    cycle-safe. It collects only open items the store holds, since writing a
    closed or unknown id into `blocked-by` would pass the rank to nothing.
    `in_flight` is the ids the ranking excluded, exactly as in `recommend`;
    `None` excludes nothing and counts nothing as in flight.
    """
    flight = set(in_flight or ())
    known = {item.identifier for item in items if item.identifier}
    by_id = {item.identifier: item for item in items if item.identifier}
    offered = {item.identifier for item in _startable(items, flight)} | flight

    def still_open(identifier: str) -> bool:
        # An id the store cannot place is unresolved, as `promotable` reads it:
        # a `blocked-by` naming nothing is not evidence that the blocker closed.
        found = by_id.get(identifier)
        return found is None or found.is_open

    unranked: list[UnrankedGenerator] = []
    for head in sorted(items, key=lambda i: i.identifier):
        if (
            head.status != "blocked"
            or head.identifier in flight
            or not ranks_as_generator(head, known)
        ):
            continue
        direct = [
            b for b in dict.fromkeys(head.blocking_items) if b != head.identifier and still_open(b)
        ]
        if any(b in offered for b in direct):
            continue
        behind: set[str] = set()
        seen = {head.identifier}
        frontier = [b for b in direct if b in by_id and by_id[b].status == "blocked"]
        while frontier:
            current = frontier.pop()
            if current in seen:
                continue
            seen.add(current)
            for upstream in by_id[current].blocking_items:
                found = by_id.get(upstream)
                if found is None or not found.is_open:
                    continue
                if upstream in offered:
                    behind.add(upstream)
                elif found.status == "blocked":
                    frontier.append(upstream)
        pending = [
            version
            for version in dict.fromkeys(head.blocking_milestones)
            if milestones is None
            or not milestones.is_cleared(version)
            or milestones.ships_with(version, head.identifier)
        ]
        unranked.append(
            UnrankedGenerator(
                head=head, waiting_on=(*direct, *pending), behind=tuple(sorted(behind))
            )
        )
    return unranked


def recurring(items: list[Item], in_flight: Collection[str] | None = None) -> list[Item]:
    """Open items the store has now absorbed three or more filings of.

    The evidence a generator claim rests on, arriving without anybody having to
    notice it. `CLAUDE.md` ranks a root cause above every band but `P0` because
    "every session it stands through pays it again", and a re-filing is that
    sentence happening: a session hit the defect, had no idea an item existed,
    and paid the diagnosis a second time. Until `bin/docket new` recorded the
    match, that evidence existed only in prose - `PL-STC4`'s brief names its own
    duplication three times and nothing was promoted until a session read the
    cluster by hand, five captures in.

    **The generator rule's own number, counted in filings rather than in
    items** (`MIN_RECURRENCES`, which is `MIN_ROOT_CAUSE_ITEMS - 1`). The item
    is itself the first filing, so two recurrences is three filings of one
    defect - the three items a generator is the root cause of. Written as a
    literal three this would have demanded a fourth filing, which is a stricter
    bar than the generator rule wearing its number: measured over the five
    recorded clusters, the slug-rename one (`PL-LBR6` with `PL-5QLP` and
    `PL-QMC0`, recorded as a generator by hand) peaks at two and would never
    have surfaced. Deriving it keeps the project arguing about one threshold
    rather than two.

    **Candidates, never a verdict, and this one may not even rank.**
    `promotable` above is named-but-not-ranked because a closed blocker is not
    evidence that nothing else holds an item; this is named-but-not-ranked for a
    stronger reason. The count is built from a title-similarity match, which
    `README.md` refuses to let write `root-cause-of:` at all - "the one place in
    the store where a typo would buy a promotion". So ranking on this field
    would buy exactly the promotion that validation exists to refuse, one
    indirection away. A reader opens both briefs and writes the claim by hand,
    as they always have; what has changed is that the cluster is now *seen*.

    An item already carrying a sound generator claim is left out, and that
    stays `is_generator` rather than `ranks_as_generator` after `PL-T7QR` split
    the two. A head recorded and marked `spent` is not on the tier, so the
    wider test is tempting - but the line this list produces asks a reader to
    write `root-cause-of:`, which such an item already carries, and an offer
    naming the wrong field is worse than no offer. What a spent head accruing
    fresh recurrences deserves is a line of its own saying the verdict has been
    falsified, which is `PL-5DPF`.

    **Named only where a promotion could still move something, which is the
    window `root-cause-of:` acts in.** The field changes a queue position and
    nothing else, so a claim written onto an id `recommend` does not rank is
    read by nothing - it builds its generator map from the startable set.
    Closed and in flight are the two states that put an id outside that set
    for good, and in both this line asks a reader to confirm a promotion that
    cannot rank. `PL-W7WL` was ratified onto the tier on 2026-09-21 and the
    write would have done nothing: the item was being implemented while the
    reader answered. `PL-GYRX` was dropped on 2026-09-19 reasoning the same
    way about `impairs-generators:`, the sibling entrance - two instances of
    one hole, which is what made it `PL-CJ5R` rather than an accident.

    **`untriaged` and `blocked` stay, though `_startable` excludes them too.**
    Their windows have not opened rather than closed. A claim written onto an
    untriaged item ranks the moment triage seats it, and is the thing a triage
    pass most wants to know before choosing a band; one on a blocked item
    ranks when its blocker clears. Dropping them would trade this defect for
    the same defect pointing the other way, and neither is the state the two
    recorded instances were in.

    **The suppression is only as complete as the flight read.** An unpushed
    branch is in no ref, so an item being implemented in another container is
    still named here - which is the state `PL-W7WL` was actually in. `None`
    excludes nothing on that ground, exactly as in `recommend`; callers pass
    `FlightReport.ids` and print what went unread beside the answer.
    """
    flight = in_flight or set()
    return sorted(
        (
            item
            for item in items
            if item.status not in CLOSED_STATUSES
            and item.identifier not in flight
            and recurrence_count(item) >= MIN_RECURRENCES
            and not is_generator(item, {i.identifier for i in items if i.identifier})
        ),
        key=lambda item: (-recurrence_count(item), item.identifier),
    )


def placement_line(
    scope: Scope | None,
    identifier: str,
    *,
    ranks_above_bands: bool = False,
    closed: bool = False,
    blocked: bool = False,
) -> str:
    """One short phrase saying where the plan places an id, or `""`.

    `docket next` states the relation inside a ranked item's reason, which
    only reaches a session that asked for a ranking. Naming an item reaches
    `docket show` instead, and until `PL-J790` that printed priority, effort,
    status and `touches` and nothing about the plan - on the path the project
    owner usually starts work on, and the one `next` never sees.

    Deliberately shorter than the reason lines above, and deliberately not
    shared with them: this is a header field beside `touches`, where a
    sentence explaining the ranking would not fit. What the two must agree on
    is the *relation*, which is `scope.placement` in both.

    `ranks_above_bands` is the caller saying this item is on the generator
    tier - a sound `root-cause-of:` or a sound `impairs-generators:`. Only the
    unplaced branch reads it, and only to drop a clause: "it ranks on its band
    alone" is false of such an item, which ranked above every band. `recommend`
    already refuses that sentence for the same reason, and until now `docket
    show` asserted it on every generator in the store - on the path the project
    owner usually starts work on, where `next`'s corrected wording never
    reaches. The relation itself is unchanged, so the two still agree.

    `closed` drops the rank clause's claim altogether, and wins over
    `ranks_above_bands`: a closed item ranks on no band and no tier, so either
    sentence would be false of it. `docket show` printed "it ranks above every
    band but P0" under closed generator heads, and "it ranks on its band alone"
    under every other closed item (`PL-BBT8`).

    `blocked` qualifies `ranks_above_bands` rather than replacing it: a blocked
    item is startable by nothing, so "it ranks above every band" is false of it
    now and true only once it can start. `docket show` said it of `PL-MB2W`, a
    live head blocked on its build items, while `next` ranked those items and
    not the head (`PL-4RK2`). A blocked item off the tier keeps "on its band
    alone", which names the band it will rank on, and is not changed here.
    """

    if scope is None or not scope.anchor:
        return ""

    where = scope.placement(identifier)
    if where == IN_SCOPE:
        if scope.clearing:
            return f"on the debt gate recorded under {scope.anchor}"
        return f"in scope for {scope.anchor}"
    if where == OUT_OF_SCOPE:
        placed_by = scope.milestone(identifier)
        # While a gate is being cleared, `later` also holds the anchor's own
        # scope mapped to the anchor - so "outside what v0.5.0 names; placed by
        # v0.5.0" is accurate and reads as a bug. It is the commonest case
        # there is while a gate is open, and it says something different.
        # `milestone()` answers with a bare `v0.5.0` while `anchor` carries the
        # roadmap's label - "v0.5.0 - the case you can branch" - so comparing
        # them directly never matches. The anchor's first token is the version.
        if placed_by and scope.anchor.split()[0] == placed_by:
            return f"in the scope of {scope.anchor}, which clearing its gate comes before"
        return f"outside what {scope.anchor} names; placed by {placed_by}"
    if where == EXCLUDED:
        return f"explicitly out of scope for {scope.anchor}"
    if closed:
        return f"placed by no section of {scope.anchor} - it is closed, so it ranks nowhere"
    if ranks_above_bands and blocked:
        return (
            f"placed by no section of {scope.anchor} - it is blocked, so it ranks nowhere "
            f"until it can start, and then above every band but P0"
        )
    if ranks_above_bands:
        return f"placed by no section of {scope.anchor} - it ranks above every band but P0"
    return f"placed by no section of {scope.anchor} - it ranks on its band alone"


#: The tags `placement_mark` draws, with the clause that defines each one. The
#: caller prints the clause for the tags it actually used, which is what keeps a
#: bare row from reading as "nobody looked" - the failure `PL-J790` named, met
#: here by a legend rather than by a sentence on every row.
PLACEMENT_MARKS = {
    "[gate]": "on its frozen list",
    "[after the gate]": "in its Required scope, which clearing the gate comes before",
    "[in scope]": "in its Required scope",
    "[ruled out]": "under its Explicitly out of scope heading",
}


def placement_mark(scope: Scope | None, identifier: str) -> str:
    """The same relation as `placement_line`, compressed to a tag, or `""`.

    `format_status` prints two dozen rows on one screen, so the sentence above
    does not fit and a sentence per row would bury the handful that matter -
    five of this store's twenty-four feature rows were on the gate when
    `PL-BZCM` was written. The relation is what the two must agree on, and that
    is `scope.placement` in both.

    A later milestone's section is named by its version, which is what a reader
    needs in order to place it; the fourth answer - no section places the id -
    is deliberately no tag at all, because it is the common case and a legend
    can define a blank row once.
    """
    if scope is None or not scope.anchor:
        return ""
    where = scope.placement(identifier)
    if where == IN_SCOPE:
        return "[gate]" if scope.clearing else "[in scope]"
    if where == OUT_OF_SCOPE:
        placed_by = scope.milestone(identifier)
        # While a gate is open, `later` also carries the anchor's own scope
        # under the anchor's version - the commonest case there is, and a
        # different statement from "a later milestone names this". The anchor
        # carries the roadmap's label and `milestone()` a bare version, so the
        # comparison is on the label's first token, as `placement_line` does.
        if placed_by and scope.anchor.split()[0] == placed_by:
            return "[after the gate]"
        return f"[{placed_by}]" if placed_by else ""
    if where == EXCLUDED:
        return "[ruled out]"
    return ""


def placement_clause(scope: Scope | None, identifier: str) -> str:
    """The same relation again, in the fewest plain words, or `""`.

    The third renderer of `scope.placement`, and the one written for a reader
    who is not inside the ranking. `placement_line` puts the relation in a
    sentence for `docket show`; `placement_mark` compresses it to a tag for a
    `docket status` row; this is for the two places that name an item with no
    room for either - the `Lane of this answer:` line and the digest's
    `By lane:` line, which until `PL-Z27P` printed a bare id and title.

    Those two are where the project owner meets the workflow lane, once per
    `docket next` and once per session, and a bare id there is the whole of
    what they had to go on: "I don't know why it's selected" (2026-09-19). A
    title is written for the session that will implement the item, so it names
    a mechanism rather than a consequence, and nothing beside it said whether
    the item was gate work, a band below the gate, or unplaced.

    The gate is named only while one is open, which is what `scope.clearing`
    says. With the gate clear there is no gate to be off, and "not on the gate"
    would be true of every item in the store and informative about none.
    """
    if scope is None or not scope.anchor:
        return ""
    where = scope.placement(identifier)
    if where == IN_SCOPE:
        return "on the debt gate" if scope.clearing else f"in scope for {scope.anchor}"
    if where == EXCLUDED:
        return f"ruled out of {scope.anchor}"
    if where == OUT_OF_SCOPE:
        placed_by = scope.milestone(identifier)
        # The anchor's own `Required scope` is mapped to the anchor while its
        # gate is open, and that is the commonest reading there is - it says
        # "this is the milestone's own work, which the gate comes before",
        # never "a later release owns this". `placement_line` draws the same
        # distinction on the same test, the anchor's first token.
        if placed_by and scope.anchor.split()[0] == placed_by:
            return "not on the gate; it is what the gate clears the way for"
        if not placed_by:
            return "not on the gate"
        return f"not on the gate; placed by {placed_by}"
    return "not on the gate" if scope.clearing else "placed by no section"


def _named_ids(identifiers: tuple[str, ...], limit: int = 3) -> str:
    """A few ids in full, then a count of the rest.

    A generator naming nineteen items would otherwise put nineteen ids in a
    `docket next` reason line. The first few are what a reader checks the
    claim against; the count is what tells them how much more there is.
    """
    shown = ", ".join(identifiers[:limit])
    rest = len(identifiers) - limit
    return f"{shown} and {rest} more" if rest > 0 else shown


def _clipped(text: str, limit: int = 160) -> str:
    """One field's prose, bounded so it cannot take over a reason line.

    `impairs-generators` is written to be read - it is the only evidence a
    reader has for a promotion above every band - so the line quotes it rather
    than pointing at `docket show`. A field long enough to bury the three
    recommendations around it defeats that, which is the same concern
    `_named_ids` answers for nineteen ids. Clipped on a word boundary so the
    fragment reads as a sentence rather than as a truncated token.
    """
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0] + "..."


def _placed(
    scope: Scope | None, item: Item, reason: str, *, ranks_on_band: bool
) -> tuple[str, str]:
    """`reason` with the plan's placement of `item` stated on it, and the milestone scoping it.

    Shared by `recommend` and `longest_waiting`, so the two cannot describe one
    item's placement differently. What differs between them is how the item
    ranked, and exactly one sentence here states that: an unplaced item "ranks
    on its band alone", which is true of `recommend`'s ordinary pick and false
    of a generator, which ranked above every band, and of every `--oldest`
    pick, which ranked by age. `ranks_on_band` is the caller saying which.
    """
    if scope is None:
        return reason, ""
    where = scope.placement(item.identifier)
    scoped_to = ""
    if where == IN_SCOPE:
        # Three arrangements, and conflating them is what PL-1J0P fixed.
        # The step usually *is* the milestone placing the id. But the
        # roadmap lets a gate ship as its own version, and then the id is
        # on a list recorded under one milestone and cleared by another -
        # and separately, a milestone's `Required scope` becomes current
        # work only once its gate is clear. Saying "the step the project is
        # on" of either told every session the project was on a release it
        # had not reached.
        if scope.clearing and scope.step_label:
            # Which row is current, and never which row clears the gate.
            # The two labels differ here, and the shorter sentence naming
            # one as clearing the other was read as the plan's own answer:
            # `ROADMAP.md`'s timeline makes the gate a row of its own, and
            # "The cadence" has cleared gate work ship inside the milestone
            # that recorded it rather than in the patch track beneath it -
            # so "v0.4.x - the code is the model clears it" told every
            # session a patch may carry the gate, on the one question the
            # cadence exists to settle (`PL-TNB6`). `Scope` carries no row
            # for the gate itself, so the honest line says where the
            # project stands and leaves the clearing to the milestone the
            # gate is recorded under, which the first clause already names.
            reason = (
                f"On the debt gate recorded under {scope.anchor}, which clears before "
                f"that milestone is implemented; the project stands on "
                f"{scope.step_label}. {reason}"
            )
        elif scope.clearing:
            # "debt gate", in those words, because this is the branch that
            # fires on the ordinary arrangement - a milestone clearing its
            # own gate - and it was the one wording in the project that
            # never said "gate" at all. `placement_line` says "on the debt
            # gate recorded under", `placement_mark` draws `[gate]`, and
            # `ROADMAP.md` calls it the debt gate; only `docket next` - the
            # command that actually hands over the work - called it "the
            # frozen list", which is the store's internal name for the
            # recorded list rather than the thing the project owner is
            # tracking. So every gate item this project has ever offered
            # was offered without being announced as gate work, and the
            # owner reported exactly that: `next` "hasn't recommended a
            # gate item in a while, or at least hasn't called something a
            # gate item if it was" (2026-09-19). The relation was right
            # throughout; only the noun was unreadable (`PL-MN0F`).
            reason = (
                f"On the debt gate recorded under {scope.anchor}, "
                f"the step the project is on. {reason}"
            )
        elif scope.step_label:
            reason = (
                f"In scope for {scope.anchor}, which the step the project is on "
                f"({scope.step_label}) comes before. {reason}"
            )
        else:
            reason = f"In scope for {scope.anchor}, the step the project is on. {reason}"
    elif where == UNPLACED and scope.anchor:
        # The third placement said nothing until PL-J790, and silence is
        # not one of the three answers: a session reading a reason line
        # with no gate sentence cannot tell "no section places this" from
        # "nobody looked". The wording has to stay narrow, though. `Scope`
        # reads a section's frozen list and its `Required scope` and
        # nothing else, so a timeline row places nothing here - `PL-FZ6T`
        # is unplaced by this test while `ROADMAP.md`'s `v0.4.x` row names
        # it outright. Saying "the roadmap places this nowhere" would have
        # every session assert that falsehood.
        placed_nowhere = (
            f"Placed by no section of {scope.anchor}: neither its frozen list nor "
            f"its `Required scope` names this id. A timeline row or prose may still "
            f"place it."
        )
        # The tail states how the item ranked, and for a generator that
        # sentence is false - it did not rank on its band, it ranked above
        # every band - as it is for an `--oldest` pick, which age ranked.
        # Two claims about one ranking, in one reason line, is the
        # apparatus floor broken where a reader can see both.
        if ranks_on_band:
            placed_nowhere = (
                f"Placed by no section of {scope.anchor}: neither its frozen "
                f"list nor its `Required scope` names this id, so it is neither "
                f"preferred nor excluded and ranks on its band alone. A timeline "
                f"row or prose may still place it."
            )
        reason = f"{reason} {placed_nowhere}"
    elif where == OUT_OF_SCOPE:
        scoped_to = scope.milestone(item.identifier)
        reason = (
            f"{reason} Outside what {scope.anchor} names: this id appears in "
            f"{scoped_to}'s section, which the current step has not reached."
        )
    elif where == EXCLUDED:
        # A decision rather than a delay, so the sentence says so and the
        # item sorts below out-of-scope work rather than level with it.
        # `scoped_to` stays empty: no milestone *places* this id, and
        # naming the excluding one there would read as one that does.
        reason = (
            f"{reason} Explicitly out of scope for {scope.anchor}: its section names "
            f"this id under that heading, so the roadmap has ruled on it."
        )
    return reason, scoped_to


def recommend(
    items: list[Item],
    in_flight: Collection[str] | None = None,
    *,
    effort: str | None = None,
    limit: int = 3,
    scope: Scope | None = None,
    lane: str | None = None,
    workflow_paths: tuple[str, ...] = (),
    generator_paths: tuple[str, ...] = (),
    protected_paths: tuple[str, ...] = (),
    gate_paths: tuple[str, ...] = (),
) -> list[Recommendation]:
    """Rank the work worth starting now.

    Order of precedence, highest first: anything at `P0`, because that is what
    `P0` means; then a recorded *generator*; then what the roadmap's current
    step includes, when a `scope` is supplied; then work in a feature already
    underway, nearest to finished first; then the highest-priority item that is
    ready to start. Items already in flight on a branch are excluded outright
    rather than ranked low - recommending work somebody is doing is worse than
    recommending nothing.

    A `P0` outranks the phase, unchanged: a hotfix is not deferred because the
    milestone is about something else. Everything below it is reordered by
    placement rather than filtered by it. Out-of-scope work stays in the list,
    carrying the milestone that names it, because "is this really out of
    scope?" is a judgment and hiding the item would be a verdict this cannot
    support - where saying which milestone names its id is a fact it can.

    A generator - an item carrying a sound `root-cause-of:` - sits directly
    below `P0` and above everything else, including a `safety`- or
    `science`-classed `P1`. That placement was asked of the project owner and
    confirmed twice (2026-09-17): *"We constantly add more P1 as we develop, so
    these never get done and the bugs pile up."* Promotion inside a band was
    the alternative and is refused, because the band a generator would be
    promoted within is itself growing, so its position in absolute terms never
    moves. The safety floor is not weakened by this - a clinical defect that
    has to be fixed now is what `P0` is for, and `P0` still outranks a
    generator.

    That tier has a second entrance: an item carrying a sound
    `impairs-generators:`, which claims to be a defect in the machinery that
    identifies and ranks generators (project owner, 2026-09-19). Same tier,
    not a sub-order - "the same priority as a generator" is what was asked
    for, so between the two the ordinary terms below decide. The warrant is
    the generator argument one level up: a generator is paid again by every
    session it stands through, and a broken identification path means the
    generator is never recorded, so nothing pays anything until somebody
    notices by hand. `generator_paths` is what refutes a false claim; see
    `model.generator_defect_faults` for why it cannot establish a true one.

    A head the tier would rank but that is `blocked` hands its rank to the open
    items it waits on (`generator_blockers`), so a generator whose fix a design
    round decomposed keeps the tier instead of sinking into its band
    (`PL-QFWF`). That is not a third entrance: the claim is still the head's,
    and the blocker's reason line names the head it unblocks. A head whose rank
    reaches nothing startable that way is not ranked further down but named,
    by `unranked_generators` (`PL-4RK2`).

    **Two tests, on different axes, and only the second one ranks.** The
    count - three or more items standing on one mechanism - decides whether a
    generator is *recorded*; the recurrence verdict on `generator:` decides
    whether it ranks here (project owner, 2026-09-21, ratified, over keeping
    the count for both and accepting that any three-item cluster outranks a
    `safety`-classed `P1`). The tier is the only rank above a safety item, so
    what earns it is a claim about future inflow - this mechanism is still
    being handed members, so every session it stands through pays it again -
    rather than a claim about the damage the existing three already did. A
    cluster whose mechanism is spent is recorded all the same, for the audit,
    and is ranked here on its own band. `model.ranks_as_generator` is the
    shared test; `model.is_generator` remains what `clusters` and
    `generators_explaining` read, since a spent root cause still explains its
    members.

    The verdict is a session's judgment, written into the store rather than
    inferred from the brief: `CLAUDE.md` refuses to script the judgment half,
    and reading "still generating" out of prose would be guessing at exactly
    that half. Recording alone does not rank - a sound claim carrying no
    verdict is ranked on its band and reported by `docket check` - because
    `check` runs separately from this, so the unvalidated state has to be the
    one that cannot buy a promotion.

    Soundness is re-decided here rather than assumed from the field's presence,
    against every id in `items` including closed ones: a root cause still
    explains an item that has since closed, so a claim must not decay as its
    cluster is worked. That shared predicate is why this and `docket check`
    cannot disagree about what a claim is.

    A `lane` narrows the candidates to one half of the project before any of
    that runs, so two sessions can rank simultaneously without arriving at the
    same item. It filters and never reorders: a lane changes which work is
    eligible, not what the project's priorities are, so the `P0` rule, the
    roadmap's phase and the finish-a-feature preference apply inside a lane
    exactly as they do across the whole queue. The feature-progress reading is
    deliberately computed from *all* items rather than from the lane's, since
    how near a feature is to done is a fact about the feature and not about
    who is looking at it. Work the lane cannot place is dropped here and
    counted by `set_aside`, never silently discarded.
    """
    startable = [
        item
        for item in _startable(items, in_flight, effort=effort)
        if lane is None or item.lane(workflow_paths) == lane
    ]
    known = {item.identifier for item in items if item.identifier}
    generating = {
        item.identifier: item.root_cause_of for item in startable if ranks_as_generator(item, known)
    }
    impairing = {
        item.identifier: item.impairs_generators
        for item in startable
        if impairs_generators_soundly(item, generator_paths)
    }
    # From every item rather than from `startable`: the heads are blocked, so
    # the startable set is exactly what cannot contain them.
    unblocking = generator_blockers(items)
    on_tier = generating.keys() | impairing.keys() | unblocking.keys()
    underway = {
        item.identifier: feature
        for feature in features(items).values()
        if feature.is_underway
        for item in feature.open_items
    }

    def placement(item: Item) -> str:
        return scope.placement(item.identifier) if scope is not None else UNPLACED

    def rank(item: Item) -> tuple[int, int, int, int, int, int, int, str]:
        """Hotfix, then a generator, then the plan, then band, then the feature.

        `P0` is lifted out of the band comparison so that the phase cannot
        reorder a hotfix; below it, what the current step includes comes ahead
        of what it does not, because the band cannot express the phase. The
        feature preference stays a tie-breaker inside a band, never across
        bands: a P1 defect does not wait because a P3 feature is half built.

        `generator` sits between the two for the same reason `hotfix` is
        lifted out: the band cannot express "this is why three other items
        exist". It is above `PLACEMENT_ORDER` as well as above `band`, so a
        generator the roadmap places nowhere still outranks in-scope work -
        which is what "above everything but P0" means, and the whole of what
        was decided. One term carries both entrances to the tier, rather than
        two terms ordering them against each other, because the decision was
        that a machinery defect ranks at *the same* priority as a generator -
        and the blockers of a blocked head, whose rank it is.

        Two terms carry that preference, not one. `finishes` is the binary
        question - is this item in a feature already underway - and `remaining`
        orders the ones that are by how much of their feature is left, fewest
        first. Without the second term the tie fell through to effort, so the
        smaller item won and a feature 30% done outranked one 75% done, while
        the rationale line and `CLAUDE.md` both said the opposite (PL-B0YN).
        `remaining` is 0 for an item outside any underway feature, which never
        competes with an item inside one because `finishes` has already
        separated them.
        """
        hotfix = 0 if item.priority == "P0" else 1
        generator = 0 if item.identifier in on_tier else 1
        band = PRIORITIES.index(item.priority) if item.priority in PRIORITIES else len(PRIORITIES)
        feature = underway.get(item.identifier)
        finishes = 1 if feature is None else 0
        remaining = 0 if feature is None else len(feature.open_items)
        return (
            hotfix,
            generator,
            PLACEMENT_ORDER[placement(item)],
            band,
            finishes,
            remaining,
            item.sort_key()[1],
            item.identifier,
        )

    ranked: list[Recommendation] = []
    for item in sorted(startable, key=rank):
        if item.priority == "P0":
            reason = "P0: this comes before feature work."
        elif item.identifier in generating:
            explains = generating[item.identifier]
            # Says "ranked as a generator" in those words, because a reader
            # meeting a `P2` at the top of a list with `P1`s below it needs to
            # know the ranking meant it. Naming the ids it explains is the
            # other half: the claim is a recorded fact, so the line that acts
            # on it shows the record rather than asserting the conclusion.
            reason = (
                f"Ranked as a generator: the recorded root cause of {len(explains)} "
                f"items ({_named_ids(explains)}). This is above every band but P0 - "
                f"a mechanism three items stand on is paid again by every session it "
                f"stands through, and patching them one at a time closes items while "
                f"leaving it running."
            )
        elif item.identifier in impairing:
            # A separate sentence from the generator's, because the warrant is
            # different and a reader checking the claim needs the one that
            # applies. A generator shows its items; this shows the declared
            # prose, which is the only evidence there is that the machinery is
            # impaired at all.
            reason = (
                f"Ranked as a defect in the generator machinery: "
                f"{_clipped(impairing[item.identifier])} This is the generator tier - "
                f"above every band but P0 - because while identification or ranking is "
                f"broken a generator is not recorded, and an unrecorded generator is "
                f"ranked by nothing. Nothing in the store would say one went unfound."
            )
        elif item.identifier in unblocking:
            heads = unblocking[item.identifier]
            # The head's own evidence, count and all, because the rank is the
            # head's: a reader checking why a `P2` leads the list checks that
            # head's claim, and this is the line that has to point at it.
            if len(heads) == 1:
                (head,) = heads
                blocked_on_it = (
                    f"{head.identifier}, a live generator - the recorded root cause of "
                    f"{len(head.root_cause_of)} items - that is blocked on it"
                )
            else:
                blocked_on_it = (
                    f"{_named_ids(tuple(h.identifier for h in heads))}, live generators "
                    f"blocked on it"
                )
            reason = (
                f"Ranked on the generator tier as a blocker of {blocked_on_it}. A blocked "
                f"head is startable by nothing, so its rank passes to the work it waits "
                f"on - above every band but P0 - or a generator whose fix was decomposed "
                f"into build items would be ranked by nothing."
            )
        elif item.identifier in underway:
            feature = underway[item.identifier]
            left = len(feature.open_items)
            # Only the last open item finishes anything. Saying "Finishes" of
            # the other kind asserted and then withdrew the same claim in one
            # sentence, which taught a reader to discount the whole line -
            # including the cases where it is true (PL-G1MF).
            if left == 1:
                reason = (
                    f"Finishes '{feature.name}' - its last open item. "
                    f"A shipped feature beats progress on several."
                )
            else:
                reason = (
                    f"Advances '{feature.name}', which is {int(feature.progress * 100)}% done "
                    f"({left} items left). A shipped feature beats progress on several, "
                    f"so the feature nearest done ranks first."
                )
        else:
            reason = f"Highest-priority work that is ready to start ({item.priority})."

        reason, scoped_to = _placed(
            scope, item, reason, ranks_on_band=item.identifier not in on_tier
        )
        ranked.append(
            Recommendation(
                item,
                reason,
                scoped_to=scoped_to,
                generator=len(generating.get(item.identifier, ())),
                impairs_generators=item.identifier in impairing,
                unblocks=tuple(h.identifier for h in unblocking.get(item.identifier, ())),
                delegable=item.delegability(protected_paths, gate_paths) is None,
            )
        )

    return ranked[:limit]


def waiting_since(item: Item, today: date) -> str:
    """How long an item has waited, as the clause `docket next --oldest` prints.

    Read from `added` against `today`, so no git read is needed and a test can
    pin the date. An item with no `added` says it cannot be aged rather than
    claiming an age; `docket check` already errors on it.
    """
    if item.added is None:
        return "no `added` date, so how long it has waited cannot be read"
    days = (today - item.added).days
    return f"added {item.added.isoformat()}, {days} {'day' if days == 1 else 'days'} waiting"


@dataclass(frozen=True)
class Waiting:
    """What `docket next --oldest` answers, in the three parts it prints."""

    #: Startable owed work, longest-waiting first with `P0` above all of it,
    #: cut to the caller's limit.
    picks: list[Recommendation]
    #: Owed work at `needs-decision`, oldest first and uncut: named beside the
    #: picks and never ranked among them.
    decisions: list[Item]
    #: How many startable items were left out as new work, so the filter is
    #: never silent about what it dropped.
    new_work: int


def longest_waiting(
    items: list[Item],
    in_flight: Collection[str] | None = None,
    *,
    today: date,
    new_work_classes: tuple[str, ...],
    debt_classes: tuple[str, ...],
    effort: str | None = None,
    limit: int = 3,
    scope: Scope | None = None,
    lane: str | None = None,
    workflow_paths: tuple[str, ...] = (),
    generator_paths: tuple[str, ...] = (),
    protected_paths: tuple[str, ...] = (),
    gate_paths: tuple[str, ...] = (),
) -> Waiting:
    """Owed work in the order it has waited, for `docket next --oldest`.

    Every term `recommend` ranks on favours work that is newer, more urgent or
    more central, so an owed item that is none of those waits while new work
    keeps arriving above it. That is *starvation*, and the standard remedy in
    priority scheduling is *aging*: a request's priority rises the longer it
    waits. Pure age order is aging's extreme form, and the simplest to audit.
    It sits beside the plan rather than inside it: `recommend` is unchanged,
    and this answers the question a session asks when it wants what the plan
    keeps passing over (`PL-Q89J`, project owner, 2026-09-22, ratified, over
    a `--debt` filter in the plan's own order, which would have returned what
    `docket next` already returns).

    Longest-waiting first by `added`, ties by band and then id. `P0` stays on
    top whatever its age and whatever its status: a hotfix never waits behind
    an old doc fix, and is never moved onto the decisions line. An item with
    no `added` sorts last.

    The population is `_startable`'s, narrowed by `lane` the way `recommend`
    narrows it, less new work (`is_new_work`). Owed work at `needs-decision` is
    split out rather than ranked. Its next step is the project owner's answer
    rather than a session's work, and ranked by age the oldest unanswered
    decision would hold the top of this list for good - `PL-JW39`'s hazard in
    `next` itself.

    Each pick carries the placement sentence `recommend` writes, so an
    off-gate pick says so, and never the clause saying it "ranks on its band
    alone", which age makes false.
    """
    startable = [
        item
        for item in _startable(items, in_flight, effort=effort)
        if lane is None or item.lane(workflow_paths) == lane
    ]
    owed = [item for item in startable if not is_new_work(item, new_work_classes, debt_classes)]
    known = {item.identifier for item in items if item.identifier}
    unblocking = generator_blockers(items)

    def rank(item: Item) -> tuple[int, int, date, int, str]:
        hotfix = 0 if item.priority == "P0" else 1
        undated = 0 if item.added is not None else 1
        band = PRIORITIES.index(item.priority) if item.priority in PRIORITIES else len(PRIORITIES)
        return (hotfix, undated, item.added or date.max, band, item.identifier)

    def deciding(item: Item) -> bool:
        return item.status == "needs-decision" and item.priority != "P0"

    picks: list[Recommendation] = []
    for item in sorted((i for i in owed if not deciding(i)), key=rank)[:limit]:
        waited = waiting_since(item, today)
        waited = f"{waited[:1].upper()}{waited[1:]}."
        if item.priority == "P0":
            reason = f"P0: this comes before feature work, whatever its age. {waited}"
        else:
            reason = waited
        reason, scoped_to = _placed(scope, item, reason, ranks_on_band=False)
        picks.append(
            Recommendation(
                item,
                reason,
                scoped_to=scoped_to,
                generator=len(item.root_cause_of) if ranks_as_generator(item, known) else 0,
                impairs_generators=impairs_generators_soundly(item, generator_paths),
                unblocks=tuple(h.identifier for h in unblocking.get(item.identifier, ())),
                delegable=item.delegability(protected_paths, gate_paths) is None,
            )
        )
    return Waiting(
        picks=picks,
        decisions=sorted((i for i in owed if deciding(i)), key=rank),
        new_work=len(startable) - len(owed),
    )
