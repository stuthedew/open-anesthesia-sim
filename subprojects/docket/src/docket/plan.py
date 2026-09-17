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

from collections.abc import Collection
from dataclasses import dataclass, field

from .model import EFFORTS, LANE_CROSSING, LANE_UNPLACED, PRIORITIES, Item, is_generator
from .roadmap import IN_SCOPE, OUT_OF_SCOPE, UNPLACED, Scope


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
class Gate:
    """The debt owed before a milestone begins, split by who clears it.

    The split is the whole of the answer. Debt inside the milestone's own
    scope is cleared *by* it - requiring otherwise is a rule with no
    satisfying order, since the milestone exists to clear those items - while
    everything else is cleared first. Which side an item falls on is decided
    by the `feature` it carries, which is a fact in the file rather than a
    reading of the milestone's prose.
    """

    feature: str
    #: Cleared by the milestone itself: open debt carrying its feature.
    inside: list[Item]
    #: Cleared before it begins: everything else that is open debt.
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


def gate(items: list[Item], feature: str, debt_classes: tuple[str, ...]) -> Gate:
    """Compute a milestone's debt gate: the open debt, split by feature.

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
#: is not what the step is for, and nothing says it is excluded either.
PLACEMENT_ORDER = {IN_SCOPE: 0, UNPLACED: 1, OUT_OF_SCOPE: 2}


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

    def describe(self) -> str:
        marks = [m for m in (self.item.effort, self.item.status) if m]
        if self.item.model_guidance:
            marks.append(f"{self.item.model_guidance} - use your strongest model")
        if self.generator:
            marks.append(f"root cause of {self.generator} items")
        if self.scoped_to:
            marks.append(f"scoped to {self.scoped_to}, not this step")
        head = f"{self.item.priority} {self.item.identifier} {self.item.title}"
        return f"{head} ({', '.join(marks)})\n    {self.reason}"


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


def placement_line(scope: Scope | None, identifier: str) -> str:
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
    return f"placed by no section of {scope.anchor} - it ranks on its band alone"


#: The tags `placement_mark` draws, with the clause that defines each one. The
#: caller prints the clause for the tags it actually used, which is what keeps a
#: bare row from reading as "nobody looked" - the failure `PL-J790` named, met
#: here by a legend rather than by a sentence on every row.
PLACEMENT_MARKS = {
    "[gate]": "on its frozen list",
    "[after the gate]": "in its Required scope, which clearing the gate comes before",
    "[in scope]": "in its Required scope",
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
    return ""


def _named_ids(identifiers: tuple[str, ...], limit: int = 3) -> str:
    """A few ids in full, then a count of the rest.

    A generator naming nineteen items would otherwise put nineteen ids in a
    `docket next` reason line. The first few are what a reader checks the
    claim against; the count is what tells them how much more there is.
    """
    shown = ", ".join(identifiers[:limit])
    rest = len(identifiers) - limit
    return f"{shown} and {rest} more" if rest > 0 else shown


def recommend(
    items: list[Item],
    in_flight: Collection[str] | None = None,
    *,
    effort: str | None = None,
    limit: int = 3,
    scope: Scope | None = None,
    lane: str | None = None,
    workflow_paths: tuple[str, ...] = (),
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

    Soundness is re-decided here rather than assumed from the field's presence,
    against every id in `items` including closed ones: a root cause still
    explains an item that has since closed, so a claim must not decay as its
    cluster is worked. `model.is_generator` is the shared test, so this and
    `docket check` cannot disagree about what a claim is.

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
        item.identifier: item.root_cause_of for item in startable if is_generator(item, known)
    }
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
        was decided.

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
        generator = 0 if item.identifier in generating else 1
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

        where = placement(item)
        scoped_to = ""
        if scope is not None and where == IN_SCOPE:
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
                reason = f"On {scope.anchor}'s frozen list, the step the project is on. {reason}"
            elif scope.step_label:
                reason = (
                    f"In scope for {scope.anchor}, which the step the project is on "
                    f"({scope.step_label}) comes before. {reason}"
                )
            else:
                reason = f"In scope for {scope.anchor}, the step the project is on. {reason}"
        elif scope is not None and where == UNPLACED and scope.anchor:
            # The third placement said nothing until PL-J790, and silence is
            # not one of the three answers: a session reading a reason line
            # with no gate sentence cannot tell "no section places this" from
            # "nobody looked". The wording has to stay narrow, though. `Scope`
            # reads a section's frozen list and its `Required scope` and
            # nothing else, so a timeline row places nothing here - `PL-FZ6T`
            # is unplaced by this test while `ROADMAP.md`'s `v0.4.x` row names
            # it outright. Saying "the roadmap places this nowhere" would have
            # every session assert that falsehood.
            reason = (
                f"{reason} Placed by no section of {scope.anchor}: neither its frozen "
                f"list nor its `Required scope` names this id, so it is neither "
                f"preferred nor excluded and ranks on its band alone. A timeline row "
                f"or prose may still place it."
            )
        elif scope is not None and where == OUT_OF_SCOPE:
            scoped_to = scope.milestone(item.identifier)
            reason = (
                f"{reason} Outside what {scope.anchor} names: this id appears in "
                f"{scoped_to}'s section, which the current step has not reached."
            )
        ranked.append(
            Recommendation(
                item,
                reason,
                scoped_to=scoped_to,
                generator=len(generating.get(item.identifier, ())),
            )
        )

    return ranked[:limit]
