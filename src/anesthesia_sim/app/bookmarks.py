"""What a learner marks on a case, and the two collections the marks are held in.

The vocabulary a run is *addressed by time and by threshold*, alongside
`app/control_record.py` for what a run can be set to and `app/run_series.py`
for what a trace names. Like both of those it holds no simulation state, reads
no snapshot and loads no toolkit: a `MacTarget` names a compartment and a
height whether or not a run exists, exactly as a `RecordedSeries` names a trace
whether or not one has been drawn.

**Two kinds, not one kind with a flavour field** (`PL-LPLD`, from the Gas Man
reference simulator by way of `ROADMAP.md` planned item 26, project owner
2026-08-25). A **time bookmark** is an instant; a **MAC target** is a height on
a named compartment. They are held in two collections because they are two
different questions, and a single list with a discriminant would make every
reader of it — this module, the panel, and the detection `PL-CTD7` builds —
re-derive which kind each entry is before it could do anything with it. The
fields differ too: a threshold names a compartment and a height, and an
instant names neither.

**What these are not.** A mark is a question the learner asks of the case, not
a record of what happened in it: `control_record.ControlChange` is the record,
one entry per setting the model integrated under, and re-applying it reproduces
the run. Nothing here is re-applied and nothing here changes a run. That
difference is why the two are carried differently across a fork —
`SimulationController.resumed_at` starts a branch with an empty control
timeline and with its trunk's marks — and `docs/ARCHITECTURE.md`
§ "What a branch is" states it.

**Detection is here; the loop that calls it is not** (`PL-CTD7`). A mark
answers whether it lies between two readings — `TimeBookmark.crossed_between`
and `MacTarget.crossed_between`, swept by `BookmarkSet.crossings_between` —
and `MarkStanding` names where a mark stands on a run once the sweeping has
been done. What none of it does is *read* a run: the readings are handed in,
one pair per completed simulation step, by `SimulationController.advance`.

That is the split the overshoot hazard turns on. A crossing tested once per
rendered frame lands up to `multiplier x 0.1` s past the value the learner
marked — 30 simulated seconds at 300x (`app/playback.py`, `PL-NBWP`) — so the
test has to be applied on every step, and applying it is the advance loop's
job. Holding no state is what makes this module safe to call from inside
that loop: a predicate over two numbers cannot overshoot anything, and it
cannot carry a per-mark armed flag between runs.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import StrEnum
from math import isfinite
from types import MappingProxyType

from anesthesia_sim.app.run_series import COMPARTMENT_QUANTITIES, RecordedQuantity
from anesthesia_sim.core.concentration import MacMultiple
from anesthesia_sim.core.exceptions import SimulationConfigurationError

__all__ = [
    "BookmarkCrossing",
    "BookmarkSet",
    "BookmarkStandings",
    "MacTarget",
    "MarkStanding",
    "TimeBookmark",
]


class MarkStanding(StrEnum):
    """Where one mark stands on one run: four outcomes, and not three.

    A mark is a question, so its standing is the answer so far. Three of the
    four are the obvious ones; the fourth exists because reporting it as one
    of the other three would state something the model cannot support, which
    `CLAUDE.md`'s safety-critical standard forbids of a displayed value.

    `NOT_REACHED_WITHIN_CAP` is separate from `STILL_RUNNING` because a
    threshold above a compartment's asymptote is never reached: the run stops
    at `docs/MODEL.md` § "Supported run length" having answered the question,
    and a row that still read "still running" would invite a learner to wait
    for something that cannot arrive.

    `BEFORE_THIS_BRANCH` is separate from `NOT_REACHED_WITHIN_CAP` for the
    mirror-image reason. A branch inherits its trunk's marks, so a time
    bookmark lying before the branch's own fork instant comes across with the
    rest and the branch can never reach it going forward — and unlike the
    other three this is decidable statically, from `ResumePoint.elapsed_s`,
    without running anything. Telling a learner it was "not reached within the
    cap" would say that running longer might reach it, which is false. It is
    inherited rather than dropped so that a trunk's list and a branch's do not
    disagree about what the case is marked at (`docs/ARCHITECTURE.md`
    § "What a branch is"); this is the vocabulary that says so on the row.

    A MAC target has no `BEFORE_THIS_BRANCH` case: a height is reachable from
    either side, so a branch may cross one its trunk never did.
    """

    STILL_RUNNING = "still_running"
    """The run can still reach this mark, and has not yet."""

    REACHED = "reached"
    """This run has halted on this mark at least once."""

    NOT_REACHED_WITHIN_CAP = "not_reached_within_cap"
    """The run cannot reach it inside the supported run length."""

    BEFORE_THIS_BRANCH = "before_this_branch"
    """It stands before this branch's fork instant, so no step can reach it."""


def _checked_label(label: str | None) -> str | None:
    """Refuse a label that is present but says nothing.

    Raises:
        SimulationConfigurationError: If `label` is whitespace or empty. A
            blank name is not the same as no name: `None` renders as the
            mark's own value, and a blank one would render as an empty row a
            reader cannot tell from a rendering failure.
    """

    if label is None:
        return None

    stripped = label.strip()

    if not stripped:
        raise SimulationConfigurationError(
            f"a mark's label is either absent or says something; given {label!r}, which is "
            "blank. Leave it unset to have the mark listed under its own value"
        )

    return stripped


@dataclass(frozen=True, slots=True)
class TimeBookmark:
    """An instant of the case a learner wants the run stopped at and returned to.

    The instant is in the **case's** own simulated time, which is the axis a
    branch shares with its trunk — `ResumePoint.elapsed_s` is on it and
    `RunDefinition` opens a branch at a keyframe of the case rather than
    re-basing to zero, so one number means the same thing on every run of a
    case.

    Attributes:
        instant_s: The simulated time, in seconds from the case's opening.
        label: What to call it in a list, or `None` to list it under its own
            time. `None` rather than a generated name so that nothing
            fabricates a name the learner did not choose.

    Raises:
        SimulationConfigurationError: If `instant_s` is negative or not
            finite, or if `label` is present and blank. A case opens at zero,
            so a negative instant is before the run began and cannot be
            reached; a non-finite one cannot be compared against a clock.
    """

    instant_s: float
    label: str | None = None

    def __post_init__(self) -> None:
        if not isfinite(self.instant_s) or self.instant_s < 0.0:
            raise SimulationConfigurationError(
                f"a time bookmark stands at a finite instant from the case's opening at 0 s; "
                f"given {self.instant_s} s"
            )

        object.__setattr__(self, "label", _checked_label(self.label))

    def crossed_between(self, before_s: float, after_s: float) -> bool:
        """Whether this instant lies in the span one simulation step covered.

        `before_s < instant_s <= after_s` — open where the step began and
        closed where it ended, so the step that *lands on or passes* the
        instant is the one that reaches it and the step after does not reach
        it again. A run's clock only increases, so the span is directed and
        one instant is crossed at most once a run.

        Args:
            before_s: The run's elapsed simulated time before the step, in
                seconds of the case's own time.
            after_s: Its elapsed simulated time after the step, on the same
                axis. Both are `SimulationState.elapsed_s` readings, so both
                are exact multiples of the run's step.

        Returns:
            Whether the step reached this bookmark.
        """

        return before_s < self.instant_s <= after_s


@dataclass(frozen=True, slots=True)
class MacTarget:
    """A height on one compartment a learner wants the run stopped at.

    **Held as a multiple of the agent's 1 MAC rather than as a percent of it.**
    That is the unit the interface already reads every compartment in
    (`docs/MODEL.md` § "MAC multiples as a display unit"), and
    `core/concentration.py` states the hazard a second unit would add: the
    forms of one concentration differ by factors of a hundred, and each
    crossing between them is a place where a correct number acquires the wrong
    meaning. A target stored in the unit the readouts are drawn in is compared
    against them without a conversion at all.

    **What a target asserts is what the readout beside it asserts, and no
    more.** On the alveolar compartment a multiple of 1 MAC is the conventional
    reading. On the circuit, mixed-venous, vessel-rich, muscle and fat
    compartments it is a partial-pressure ratio and nothing else — MAC is
    defined for an alveolar concentration, and this model has no age, no second
    agent and no depth-of-anesthesia endpoint. `formatting.mac_multiple` is
    where that is stated in full; marking a height does not widen it.

    Because it is a multiple rather than an absolute concentration, a target
    survives a change of agent intact: 0.8 ×MAC is 0.8 ×MAC of whichever agent
    is running, which is the comparison a learner switching agents is asking
    for, and it is why `SimulationController.set_agent` keeps the marks it
    keeps the other settings.

    **A target carries no crossing direction** (project owner, 2026-09-20).
    `PL-LPLD`'s scope floor took one from the reference simulator — rising,
    falling or either — and it is not wanted: a height is a height, and a run
    that passes through it on the way up and again on the way down has reached
    what the learner marked both times. So a target names a compartment and a
    height and nothing else, which is also what makes two of them the same
    question (`crossing_key`). Recorded here because the reference has the
    field and a later reading of it would otherwise put the field back.

    Attributes:
        quantity: The compartment the height is read against, in the same
            vocabulary the chart traces and the readouts are addressed by.
        mac_multiple: The height, as a multiple of the running agent's 1 MAC.
        label: What to call it in a list, or `None` to list it under its own
            compartment and height.

    Raises:
        SimulationConfigurationError: If `quantity` is not one of
            `run_series.COMPARTMENT_QUANTITIES`, if `mac_multiple` is not
            finite and strictly positive, or if `label` is present and blank.
            `WASH_IN_RATIO` is the quantity this refuses: it is a quotient of
            two compartments rather than a concentration, so a multiple of MAC
            of it is not a quantity the model holds — and it is the one member
            of `RecordedQuantity` a compartment picker could otherwise offer.
            Zero is refused with the negatives because a compartment opens at
            zero, so every run would stand on such a target before it began.
    """

    quantity: RecordedQuantity
    mac_multiple: MacMultiple
    label: str | None = None

    def __post_init__(self) -> None:
        if self.quantity not in COMPARTMENT_QUANTITIES:
            offered = ", ".join(quantity.value for quantity in COMPARTMENT_QUANTITIES)
            raise SimulationConfigurationError(
                f"a MAC target is read against one compartment; given {self.quantity.value!r}, "
                f"which is not one of {offered}"
            )

        if not isfinite(self.mac_multiple) or self.mac_multiple <= 0.0:
            raise SimulationConfigurationError(
                f"a MAC target stands at a finite height above zero; given {self.mac_multiple} ×MAC"
            )

        object.__setattr__(self, "label", _checked_label(self.label))

    @property
    def crossing_key(self) -> tuple[RecordedQuantity, float]:
        """What makes two targets the same question, label aside.

        A compartment and a height. Two targets agreeing on both name one
        height, so a run would stop at the same place however many entries the
        list held — which is why `BookmarkSet` refuses the second rather than
        listing a row that adds nothing to the one above it.
        """

        return (self.quantity, self.mac_multiple)

    def crossed_between(self, before: MacMultiple, after: MacMultiple) -> bool:
        """Whether the compartment passed through this height across one step.

        **A transition between two readings, never a comparison at one**
        (project owner, 2026-09-20, with the decision that a target halts on
        every crossing). Tested as "the reading is at or above the height", a
        run that settles exactly on the height would satisfy the test on every
        subsequent step and could never be advanced past it — and a comparison
        at a single reading cannot say *which* step crossed, which is the
        thing `PL-CTD7` exists to get right.

        **Closed on the arriving side, open on the departing side, in both
        directions.** A step that lands exactly on the height crosses it; a
        run that then sits there crosses nothing further, and a run that later
        leaves the height in either direction does not cross it again on the
        way out. That asymmetry is what makes the halt safe to resume from: a
        halt leaves the run paused *on* the crossing step, so the next step's
        `before` is the halt's own reading, and a rule closed on both sides
        would halt the run again immediately and never let it pass the target
        at all. No per-target armed flag carries that — it is the arithmetic.

        Both directions count, because a target carries no crossing direction
        (see this class's own docstring): a case taken up through 0.8 ×MAC and
        back down through it has reached what the learner marked twice, and
        halts twice.

        Args:
            before: This target's compartment before the step, as a multiple
                of the running agent's 1 MAC — the unit the target is held in,
                so no conversion happens here.
            after: The same compartment after the step, in the same unit and
                from the same agent. Reading the two against different agents'
                MAC would compare a correct number with the wrong divisor,
                which is why `SimulationController` converts both with the one
                `formatting.mac_multiple` and the snapshot's own
                `agent_mac_percent`.

        Returns:
            Whether the step crossed this height, in either direction.
        """

        height = self.mac_multiple

        return before < height <= after or before > height >= after


@dataclass(frozen=True, slots=True)
class BookmarkCrossing:
    """The marks one simulation step passed through, and where it landed.

    What `SimulationController.advance` halts on. Two collections rather than
    one discriminated list, for the reason `BookmarkSet` holds two: a reader —
    or a status line — addresses one kind without filtering the other out of
    the way. Both may be non-empty, because one step can cross a marked
    instant and a marked height at once; at least one of them is, because a
    crossing that crossed nothing is not reported at all.

    Attributes:
        instant_s: The simulated time of the step that crossed them, in the
            case's own seconds — the completed step's own instant, so it is on
            the run's `simulation_step_s` grid rather than on the coarser
            `multiplier ×` grid a tick boundary can reach. `docs/MODEL.md`
            § "Halting on a marked crossing" states what that buys.
        time_bookmarks: The marked instants the step reached, in the order the
            set lists them.
        mac_targets: The marked heights the step crossed, in the order the set
            lists them.
    """

    instant_s: float
    time_bookmarks: tuple[TimeBookmark, ...] = ()
    mac_targets: tuple[MacTarget, ...] = ()

    def __post_init__(self) -> None:
        if not self.time_bookmarks and not self.mac_targets:
            raise SimulationConfigurationError(
                "a crossing names at least one mark; a step that crossed nothing is reported "
                "as no crossing at all rather than as an empty one"
            )


@dataclass(frozen=True, slots=True)
class BookmarkStandings:
    """Where each of a run's marks stands, keyed by the mark itself.

    **Keyed rather than ordered**, which is a presentation-correctness
    property rather than a lookup convenience: a row that looked its standing
    up by position could be rebound to its neighbour's by an edit to either
    collection, and a mark listed as reached when the run reached a different
    one is the wrong label on a correct value that `CLAUDE.md` treats as a
    safety failure. A mark is frozen and hashable, so it can address its own
    answer.

    Attributes:
        time_bookmarks: Each marked instant's standing.
        mac_targets: Each marked height's standing.
    """

    time_bookmarks: Mapping[TimeBookmark, MarkStanding]
    mac_targets: Mapping[MacTarget, MarkStanding]

    def of_time_bookmark(self, bookmark: TimeBookmark) -> MarkStanding:
        """This bookmark's standing.

        Raises:
            SimulationConfigurationError: If these standings were not computed
                for a set holding this bookmark. Raising rather than returning
                `STILL_RUNNING` is deliberate: a default here would draw a row
                asserting the run can still reach a mark nobody evaluated,
                which is a plausible-looking answer where there is none.
        """

        return _looked_up(self.time_bookmarks, bookmark, "time bookmark")

    def of_mac_target(self, target: MacTarget) -> MarkStanding:
        """This target's standing, raising as `of_time_bookmark` does."""

        return _looked_up(self.mac_targets, target, "MAC target")


def _looked_up[Mark: (TimeBookmark, MacTarget)](
    standings: Mapping[Mark, MarkStanding], mark: Mark, what: str
) -> MarkStanding:
    """One mark's standing, or a refusal naming the mark that was not evaluated.

    Constrained to the two kinds rather than taking a union of the two mapping
    types, because a union leaves the key type unrelated to the mark handed in
    and the index unprovable - a real gap in the signature rather than
    something to silence at the call.
    """

    try:
        return standings[mark]
    except KeyError:
        raise SimulationConfigurationError(
            f"these standings were computed for a set that does not hold the {what} {mark!r}, "
            "so there is no answer to draw for it"
        ) from None


@dataclass(frozen=True, slots=True)
class BookmarkSet:
    """The two collections, held together and listed apart.

    Frozen, and every edit returns a new set, for the reason the rest of this
    layer's values are: a `SimulationSnapshot` carries one of these to the
    panel that lists it, and a collection the panel could mutate would let a
    displayed list and the run it claims to describe drift apart within a tick.

    The two tuples are separate members rather than one list with a
    discriminant, which is what lets a reader — and a panel — address one kind
    without filtering the other out of the way.

    Attributes:
        time_bookmarks: The marked instants, in the order they were added.
        mac_targets: The marked heights, in the order they were added.
    """

    time_bookmarks: tuple[TimeBookmark, ...] = ()
    mac_targets: tuple[MacTarget, ...] = ()

    def __post_init__(self) -> None:
        _refuse_repeats(
            (bookmark.instant_s for bookmark in self.time_bookmarks),
            what="time bookmark",
            named="an instant",
        )
        _refuse_repeats(
            (target.crossing_key for target in self.mac_targets),
            what="MAC target",
            named="a compartment and a height",
        )

    @property
    def is_empty(self) -> bool:
        """Whether nothing at all is marked, which is what a fresh case holds."""

        return not self.time_bookmarks and not self.mac_targets

    def with_time_bookmark(self, bookmark: TimeBookmark) -> BookmarkSet:
        """This set with `bookmark` added at the end.

        Raises:
            SimulationConfigurationError: If an instant already marked is
                marked again. One instant is one stop however many rows name
                it, so a second entry would be a row a run could never halt
                at on its own account.
        """

        return BookmarkSet((*self.time_bookmarks, bookmark), self.mac_targets)

    def without_time_bookmark(self, bookmark: TimeBookmark) -> BookmarkSet:
        """This set with the bookmark standing at `bookmark`'s instant removed.

        Matched on the instant rather than on the whole value, so a row
        removed from a list carrying a label the caller did not reproduce
        still goes.

        Raises:
            SimulationConfigurationError: If no bookmark stands at that
                instant. Silently removing nothing would leave a panel
                reporting a deletion that did not happen.
        """

        kept = tuple(held for held in self.time_bookmarks if held.instant_s != bookmark.instant_s)

        if len(kept) == len(self.time_bookmarks):
            raise SimulationConfigurationError(
                f"no time bookmark stands at {bookmark.instant_s} s, so there is none to remove"
            )

        return BookmarkSet(kept, self.mac_targets)

    def with_mac_target(self, target: MacTarget) -> BookmarkSet:
        """This set with `target` added at the end.

        Raises:
            SimulationConfigurationError: If the same compartment, height and
                is already marked, for the reason `with_time_bookmark`
                gives.
        """

        return BookmarkSet(self.time_bookmarks, (*self.mac_targets, target))

    def without_mac_target(self, target: MacTarget) -> BookmarkSet:
        """This set with the target naming `target`'s crossing removed.

        Matched on `MacTarget.crossing_key`, so the label plays no part.

        Raises:
            SimulationConfigurationError: If no target names that crossing.
        """

        kept = tuple(held for held in self.mac_targets if held.crossing_key != target.crossing_key)

        if len(kept) == len(self.mac_targets):
            raise SimulationConfigurationError(
                f"no MAC target stands at {target.mac_multiple} ×MAC on the "
                f"{target.quantity.value} compartment, so there is none to remove"
            )

        return BookmarkSet(self.time_bookmarks, kept)

    def crossings_between(
        self,
        *,
        before_s: float,
        after_s: float,
        before: Mapping[RecordedQuantity, MacMultiple],
        after: Mapping[RecordedQuantity, MacMultiple],
    ) -> BookmarkCrossing | None:
        """Which of these marks one simulation step passed through.

        Called once per completed step, from `SimulationController.advance`,
        with the readings from either side of that step. Testing every step is
        the whole point: a test applied once per rendered frame would place
        the halt up to `multiplier × simulation_step_s` past the value the
        learner marked — 30 simulated seconds at 300× — so the same bookmark
        would stop the run at a different concentration depending on how fast
        it was being played (`PL-NBWP`, `docs/MODEL.md` § "Supported
        simulation step").

        Args:
            before_s: Elapsed simulated time before the step, in the case's
                own seconds.
            after_s: Elapsed simulated time after it, on the same axis.
            before: Every compartment a target could name, before the step, as
                multiples of the running agent's 1 MAC.
            after: The same compartments after it, in the same unit and
                against the same agent's MAC.

        Returns:
            The marks this step crossed, or `None` where it crossed nothing.
            `None` rather than an empty crossing, so a caller cannot halt a
            run on a value that says nothing happened.

        Raises:
            SimulationConfigurationError: If either reading omits a
                compartment one of these targets names. Comparing against a
                missing reading is not available: a target silently skipped
                is a halt that never comes, which is the failure this whole
                mechanism exists to prevent.
        """

        _require_readings(before, self.mac_targets, "before")
        _require_readings(after, self.mac_targets, "after")

        crossed_instants = tuple(
            bookmark
            for bookmark in self.time_bookmarks
            if bookmark.crossed_between(before_s, after_s)
        )
        crossed_heights = tuple(
            target
            for target in self.mac_targets
            if target.crossed_between(before[target.quantity], after[target.quantity])
        )

        if not crossed_instants and not crossed_heights:
            return None

        return BookmarkCrossing(after_s, crossed_instants, crossed_heights)

    def standings(
        self,
        *,
        reached_instants_s: frozenset[float],
        reached_crossings: frozenset[tuple[RecordedQuantity, float]],
        opened_at_s: float,
        run_length_cap_s: float,
        stopped_at_cap: bool,
    ) -> BookmarkStandings:
        """Where each of these marks stands on one run.

        Every mark gets an answer, so a panel drawing this set can state one
        beside every row rather than leaving the reader to infer from silence
        that nothing has happened — which is the "run stopping silently at the
        cap" this item exists to replace.

        Args:
            reached_instants_s: The instants this run has already halted on.
            reached_crossings: The `MacTarget.crossing_key`s it has already
                halted on. Both are matched the way `without_time_bookmark`
                and `without_mac_target` match, so relabelling a mark does not
                reset what the run did.
            opened_at_s: Where this run began, in the case's own time: zero on
                a trunk, and `ResumePoint.elapsed_s` on a branch. A time
                bookmark before it is `BEFORE_THIS_BRANCH`, because a reset
                returns a branch to its fork rather than to the case's
                opening, so no step of this run can reach it.
            run_length_cap_s: `MAXIMUM_ELAPSED_SIMULATION_TIME_S`, passed in
                rather than imported so this module keeps naming no core
                range of its own. A bookmark beyond it is reported as
                unreachable within the cap at once rather than after a
                simulated day of waiting.
            stopped_at_cap: Whether the run is standing at that limit with the
                next step refused. Everything still outstanding is then
                `NOT_REACHED_WITHIN_CAP`.

        Returns:
            One standing per mark, keyed by the mark.
        """

        return BookmarkStandings(
            time_bookmarks=MappingProxyType(
                {
                    bookmark: _time_bookmark_standing(
                        bookmark,
                        reached_instants_s=reached_instants_s,
                        opened_at_s=opened_at_s,
                        run_length_cap_s=run_length_cap_s,
                        stopped_at_cap=stopped_at_cap,
                    )
                    for bookmark in self.time_bookmarks
                }
            ),
            mac_targets=MappingProxyType(
                {
                    target: _mac_target_standing(
                        target, reached_crossings=reached_crossings, stopped_at_cap=stopped_at_cap
                    )
                    for target in self.mac_targets
                }
            ),
        )


def _time_bookmark_standing(
    bookmark: TimeBookmark,
    *,
    reached_instants_s: frozenset[float],
    opened_at_s: float,
    run_length_cap_s: float,
    stopped_at_cap: bool,
) -> MarkStanding:
    """One marked instant's standing, in the order the four cases exclude each other.

    `BEFORE_THIS_BRANCH` is tested first because it is a fact about the run's
    own beginning rather than about what has happened since, and it is the one
    answer no amount of running can change.
    """

    if bookmark.instant_s < opened_at_s:
        return MarkStanding.BEFORE_THIS_BRANCH

    if bookmark.instant_s in reached_instants_s:
        return MarkStanding.REACHED

    if stopped_at_cap or bookmark.instant_s > run_length_cap_s:
        return MarkStanding.NOT_REACHED_WITHIN_CAP

    return MarkStanding.STILL_RUNNING


def _mac_target_standing(
    target: MacTarget,
    *,
    reached_crossings: frozenset[tuple[RecordedQuantity, float]],
    stopped_at_cap: bool,
) -> MarkStanding:
    """One marked height's standing.

    Three cases rather than four: a height is reachable from either side, so a
    branch may cross one its trunk never did and there is no
    `BEFORE_THIS_BRANCH` for a target to be in.
    """

    if target.crossing_key in reached_crossings:
        return MarkStanding.REACHED

    if stopped_at_cap:
        return MarkStanding.NOT_REACHED_WITHIN_CAP

    return MarkStanding.STILL_RUNNING


def _require_readings(
    readings: Mapping[RecordedQuantity, MacMultiple], targets: tuple[MacTarget, ...], side: str
) -> None:
    """Refuse a reading set that omits a compartment one of these targets names.

    Args:
        readings: What was handed in for one side of a step.
        targets: The marked heights that will be compared against it.
        side: `"before"` or `"after"`, so the message says which reading was
            short rather than only that one was.

    Raises:
        SimulationConfigurationError: Naming the first compartment missing.
    """

    for target in targets:
        if target.quantity not in readings:
            raise SimulationConfigurationError(
                f"the {side} reading names no {target.quantity.value} compartment, so the "
                f"target at {target.mac_multiple} ×MAC on it cannot be tested for a crossing"
            )


def _refuse_repeats(keys: Iterable[object], what: str, named: str) -> None:
    """Refuse a collection holding two marks that name one crossing.

    Args:
        keys: What makes each mark distinct, in the collection's own order.
        what: The kind, for the message.
        named: What the key is, in the reader's words, for the message.

    Raises:
        SimulationConfigurationError: If any key repeats, naming the first
            repeat rather than the count, so the message says which entry to
            look at.
    """

    seen: set[object] = set()

    for key in keys:
        if key in seen:
            raise SimulationConfigurationError(
                f"{named} is marked once: a second {what} naming {key!r} would be a row no "
                "run could stop at on its own account"
            )

        seen.add(key)
