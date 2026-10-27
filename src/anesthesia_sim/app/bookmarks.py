"""What a learner marks on a case, and the two collections that hold the marks.

This module holds the vocabulary for referring to moments in a run *by time and by
threshold*. It sits alongside `app/control_record.py`, which says what a run can be set
to, and `app/run_series.py`, which says what each trace refers to. Like both of those
modules, it holds no simulation state, reads no snapshot and loads no GUI toolkit. A
`MacTarget` names a compartment and a height whether or not a run exists, exactly as a
`RecordedSeries` names a trace whether or not one has been drawn.

**Two kinds of mark, not one kind with a field that says which** (`PL-LPLD`, from the
Gas Man reference simulator by way of `ROADMAP.md` planned item 26, project owner
2026-08-25). A **time bookmark** is an instant. A **MAC target** is a height on a
named compartment. They are held in two collections because they ask two different
questions. A single list with a field naming the kind would force each piece of code
that uses it to work out again which kind each entry is. That code is this module, the
panel, and the crossing detection that `PL-CTD7` builds. The fields differ too: a
threshold names a compartment and a height, and an instant names neither.

**What these are not.** A mark is a question the learner asks of the case. It is
not a record of what happened in the case. `control_record.ControlChange` is that
record. It has one entry for each setting under which the model was integrated, and
re-applying it reproduces the run. Nothing here is re-applied, and nothing here changes
a run. That difference is why marks and control changes are carried differently across
a fork. A branch starts without its trunk's control timeline but with its trunk's
marks, and `docs/ARCHITECTURE.md` § "What a branch is" states the rule.

**This module detects crossings, but the loop that calls it lives elsewhere**
(`PL-CTD7`). A mark can report whether it lies between two readings, through
`TimeBookmark.crossed_between` and `MacTarget.crossed_between`.
`BookmarkSet.crossings_between` applies that test to every mark in a set.
`MarkStanding` records a mark's status on a run, such as passed or reached, once
every mark has been tested. None of this code *reads* a run.
`SimulationController.advance` passes the readings in, one pair per completed
simulation step.

Keeping the test here and the loop in the controller is what stops a halt from
overshooting a mark. If the crossing test ran only once per rendered frame, a halt
would land up to `multiplier x 0.1` s past the value the learner marked, where
`multiplier` is the playback speed. At 300x that is 30 simulated seconds
(`app/playback.py`, `PL-NBWP`). So the test has to be applied on every step, and
applying it is the job of the advance loop. Because this module holds no state, it is
safe to call from inside that loop. A test on two numbers cannot overshoot anything.
It also cannot carry a per-mark "armed" flag from one run to the next.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import StrEnum
from math import ceil, isfinite
from types import MappingProxyType

from anesthesia_sim.app.run_series import COMPARTMENT_QUANTITIES, RecordedQuantity
from anesthesia_sim.core.concentration import MacMultiple
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.simulation_step import SimulationStep, require_simulation_step
from anesthesia_sim.core.supported_ranges import CaseInstant, StepCount, require_case_instant

__all__ = [
    "BookmarkCrossing",
    "BookmarkSet",
    "BookmarkStandings",
    "MacTarget",
    "MarkStanding",
    "TimeBookmark",
]


class MarkStanding(StrEnum):
    """Where one mark stands on one run: six outcomes, not two.

    A mark is a question, so its standing is the answer so far. Two of the six
    outcomes are the obvious ones. The other four exist because reporting any of
    them as one of the obvious two would state something the model cannot
    support. `CLAUDE.md`'s safety-critical standard forbids that of a displayed
    value.

    **The two kinds of mark are answered in two vocabularies, and the clock
    decides the split** (`PL-3K9B`, project owner 2026-09-20). A time bookmark
    names an instant, and a run's clock only increases. So where the mark stands
    is a *position*: either ahead of the clock, or at or behind it. Nothing in
    the run's history can change that position. A MAC target names a height, and
    no clock orders heights. A compartment may arrive at a height, leave it and
    arrive again, so the only thing that can be said of a target is what the run
    *did*. So `PASSED` and `BEFORE_THIS_BRANCH` apply to time bookmarks and never
    to targets. `REACHED` applies to targets and never to bookmarks.
    `STILL_RUNNING`, `NOT_REACHED_WITHIN_CAP` and `NOT_REACHED_BEFORE_FAILURE`
    apply to both.

    **A bookmark that the run is at or behind is `PASSED`, not `REACHED`.** This
    is the same distinction seen from the other side. "Reached" is a historical
    claim. A run whose clock is taken backwards, by a rewind or by truncating at
    a mark and running on, falsifies that claim. Yet the mark stays perfectly
    reachable: it will stop the learner again. A positional word survives this,
    because it is worked out again from the clock every time the standing is
    drawn. The reference simulator avoids the question by giving a bookmark no
    standing at all. In Philip JH, *Workbook for Gas Man*, chapter 2 "Using
    Bookmarks", a bookmark is a pause point that fires on the original pass and
    on every replay alike, as `PL-3K9B` records. This panel draws a standing, so
    it needs a word that cannot be revoked.

    `NOT_REACHED_WITHIN_CAP` is separate from `STILL_RUNNING` because a threshold
    above a compartment's asymptote is never reached. The run stops at
    `docs/MODEL.md` § "Supported run length", and by then the question is
    settled. A row that still said "still running" would invite a learner to wait
    for something that cannot arrive.

    `BEFORE_THIS_BRANCH` is separate from `NOT_REACHED_WITHIN_CAP` for the
    mirror-image reason. A branch inherits its trunk's marks. So a time bookmark
    that lies before the branch's own fork instant comes across with the rest,
    and the branch can never reach it going forward. Unlike `STILL_RUNNING` and
    the cap, this case can be decided statically, from
    `ResumePoint.fork.instant_s`, without running anything. Telling a learner
    that the mark was "not reached within the cap" would say that running longer
    might reach it, which is false. The mark is inherited rather than dropped so
    that a trunk's list and a branch's list agree about which instants the case
    is marked at (`docs/ARCHITECTURE.md` § "What a branch is"). This standing is
    what says so on the row.

    A MAC target has no `BEFORE_THIS_BRANCH` case. A height is reachable from
    either side, so a branch may cross a height that its trunk never crossed.

    `NOT_REACHED_BEFORE_FAILURE` is the sixth outcome. It covers the one state
    that the other five cannot see: a run that `SimulationController.start`
    refuses to resume. A failed run's next step would raise, as its last one
    did, and `SimulationController.fail` says why resuming is not offered. So a
    mark that the failed run has not reached is not one it will reach later. Only
    a reset could reach it, and a reset starts a different run. This outcome is
    worded differently from the cap because the two stop a run for opposite
    reasons. At the cap, the model has answered the question and says that a
    longer run would not change the answer. In a failure, the model could not
    answer at all. Only these two refusals are in the vocabulary, because only
    these two are refusals. A *paused* run resumes, so `STILL_RUNNING` still
    applies to it, and the transport state stays off this row (`PL-N3N5`).
    """

    STILL_RUNNING = "still_running"
    """The run can still reach this mark, and has not yet."""

    PASSED = "passed"
    """This run's clock is at or behind this marked instant.

    This standing is positional and applies only to a time bookmark. So it
    still applies however the clock got there: by a step, by a fork taken at
    the mark, or because the learner marked an instant the run had already
    passed.
    """

    REACHED = "reached"
    """This run has stood on this mark at least once.

    Either the run halted on the mark, or the mark lies inside the step that
    the run stands on or opened on. That test uses the marks as they are when
    the standings are computed (`PL-1ZQ4`). This standing is historical and
    applies only to a MAC target, the one kind of mark that no clock orders.
    """

    NOT_REACHED_WITHIN_CAP = "not_reached_within_cap"
    """The run cannot reach this mark within the supported run length."""

    BEFORE_THIS_BRANCH = "before_this_branch"
    """This mark lies before this branch's fork instant, so no step can reach it."""

    NOT_REACHED_BEFORE_FAILURE = "not_reached_before_failure"
    """The run stopped on an error without reaching this mark, and cannot be resumed."""


def _checked_label(label: str | None) -> str | None:
    """Refuse a label that is present but blank.

    Raises:
        SimulationConfigurationError: If `label` is empty or only whitespace.
            A blank name is not the same as no name. A label of `None` makes
            the row show the mark's own value. A blank label would show an
            empty row, which a reader cannot tell apart from a rendering
            failure.
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
    """An instant in the case that a learner wants the run to stop at and return to.

    The instant is in the **case's** own simulated time. A branch shares that
    time axis with its trunk: `ResumePoint.fork.instant_s` is on it, and
    `RunDefinition` opens a branch at a keyframe of the case rather than
    resetting the clock to zero. So one number means the same instant on every
    run of a case.

    Attributes:
        instant_s: The simulated time, in seconds from the case's opening. It
            is a `CaseInstant`, so it is finite, at or after that opening, and
            inside the supported run length. A mark before the case began, or
            past the last instant any run of the case may reach, cannot be
            made at all (`PL-CN5S`).
        label: What to call the bookmark in a list, or `None` to list it under
            its own time. The default is `None` rather than a generated name,
            so that nothing invents a name the learner did not choose.

    Raises:
        TypeError: If `instant_s` is not a `CaseInstant`, which means nothing
            has checked it against the case's span (`core/supported_ranges.py`).
        SimulationConfigurationError: If `label` is present and blank.
    """

    instant_s: CaseInstant
    label: str | None = None

    def __post_init__(self) -> None:
        require_case_instant("instant_s", self.instant_s)
        object.__setattr__(self, "label", _checked_label(self.label))

    def crossed_between(self, before_s: CaseInstant, after_s: CaseInstant) -> bool:
        """Whether this instant lies in the span that one simulation step covered.

        The test is `before_s < instant_s <= after_s`. The span is open where
        the step began and closed where it ended. So the step that *lands on or
        passes* the instant is the one that reaches it, and the next step does
        not reach it again. A run's clock only increases, so the span has a
        direction, and a run crosses one instant at most once.

        Args:
            before_s: The run's elapsed simulated time before the step, in
                seconds of the case's own time.
            after_s: The run's elapsed simulated time after the step, on the
                same axis. Both values are `SimulationState.elapsed_s`
                readings, so both are exact multiples of the run's step.

        Returns:
            Whether the step reached this bookmark.
        """

        return before_s < self.instant_s <= after_s

    def steps_to_reach(self, simulation_step_s: SimulationStep) -> StepCount:
        """How many steps a run at `simulation_step_s` must complete to reach this instant.

        This is `crossed_between` applied the other way round, on a run's own
        step grid. The step that ends at this count is the one that
        `crossed_between` says reaches the mark. So it is the step a halt stops
        on. `count x step`, the product that `SimulationState.elapsed_s` forms,
        is the instant at which a branch taken at the mark opens
        (`SimulationController.resumed_at_mark`). The count is zero for a mark
        at the case's opening, because a run stands on that mark before any
        step and no step crosses it.

        **The count comes from the rule, not from rounding** (`PL-W4XQ`). The
        quotient `instant_s / simulation_step_s` is itself rounded, so its
        ceiling can land one step late. For example, `0.30000000000000004 / 0.1`
        is 3.0000000000000004, though the third step's own product equals that
        instant. So the ceiling is only a first guess. The code then moves the
        guess to the right step by applying the two comparisons that
        `crossed_between` makes to the step products themselves. `round` would
        be worse than late: it puts a mark that lies inside a step on the step
        *before* it, and no halt stops there.

        Args:
            simulation_step_s: The simulation step that the run uses.

        Returns:
            The number of completed steps at which the run first stands at or
            past this instant.

        Raises:
            TypeError: If `simulation_step_s` is not a `SimulationStep`, so
                nothing has checked it against the supported range
                (`core/simulation_step.py`).
        """

        require_simulation_step(simulation_step_s)

        count = ceil(self.instant_s / simulation_step_s)

        while count > 0 and (count - 1) * simulation_step_s >= self.instant_s:
            count -= 1

        while count * simulation_step_s < self.instant_s:
            count += 1

        return StepCount(count)


@dataclass(frozen=True, slots=True)
class MacTarget:
    """A height on one compartment at which a learner wants the run to stop.

    **Stored as a multiple of the agent's 1 MAC rather than as a percent of
    it.** The interface already shows every compartment in that unit
    (`docs/MODEL.md` § "MAC multiples as a display unit"). `core/concentration.py`
    states the hazard that a second unit would add. The forms of one
    concentration differ by factors of a hundred, and each conversion between
    them is a place where a correct number can take on the wrong meaning. A
    target stored in the same unit as the readouts is compared with them
    without any conversion.

    **A target claims what the readout beside it claims, and no more.** On the
    alveolar compartment, a multiple of 1 MAC is the conventional reading. On
    the circuit, mixed-venous, vessel-rich, muscle and fat compartments, it is
    only a partial-pressure ratio. MAC is defined for an alveolar
    concentration, and this model has no age, no second agent and no
    depth-of-anesthesia endpoint. `formatting.mac_multiple` states that limit
    in full, and marking a height does not widen it.

    Because a target is a multiple rather than an absolute concentration, it
    survives a change of agent intact. 0.8 ×MAC is 0.8 ×MAC of whichever agent
    is running, which is the comparison a learner switching agents wants. That
    is why `SimulationController.set_agent` keeps the marks, just as it keeps
    the other settings.

    **A target has no crossing direction** (project owner, 2026-09-20).
    `PL-LPLD`'s minimum scope took a direction from the reference simulator
    (rising, falling or either), and it is not wanted. A height is a height. A
    run that passes through it on the way up and again on the way down has
    reached what the learner marked both times. So a target names a compartment
    and a height and nothing else. Those two values are also what make two
    targets the same question (`crossing_key`). This is recorded here because
    the reference simulator has the field, and a later reader of the reference
    would otherwise put the field back.

    Attributes:
        quantity: The compartment that the height is read against, named in
            the same vocabulary as the chart traces and the readouts.
        mac_multiple: The height, as a multiple of the running agent's 1 MAC.
        label: What to call the target in a list, or `None` to list it under
            its own compartment and height.

    Raises:
        SimulationConfigurationError: If `quantity` is not one of
            `run_series.COMPARTMENT_QUANTITIES`, if `mac_multiple` is not
            finite and strictly positive, or if `label` is present and blank.
            `WASH_IN_RATIO` is the quantity this check refuses. It is a
            quotient of two compartments rather than a concentration, so a
            multiple of MAC of it is not a quantity the model has. It is also
            the one member of `RecordedQuantity` that a compartment picker
            could otherwise offer. Zero is refused along with negative values
            because every compartment starts at zero, so every run would
            stand on such a target before it began.
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
        """What makes two targets the same question, ignoring the label.

        The key is a compartment and a height. Two targets that agree on both
        name one height, so a run would stop at the same place however many
        entries the list had. That is why `BookmarkSet` refuses the second
        target rather than listing a row that adds nothing to the one above it.
        """

        return (self.quantity, self.mac_multiple)

    def crossed_between(self, before: MacMultiple, after: MacMultiple) -> bool:
        """Whether the compartment passed through this height during one step.

        **A transition between two readings, never a comparison at one reading**
        (project owner, 2026-09-20, with the decision that a target halts on
        every crossing). Suppose the test were "the reading is at or above the
        height". A run that settles exactly on the height would then pass the
        test on every later step and could never be advanced past it. Also, a
        comparison at a single reading cannot say *which* step crossed, and
        that is the thing `PL-CTD7` exists to get right.

        **Closed on the arriving side and open on the departing side, in both
        directions.** A step that lands exactly on the height crosses it. A run
        that then stays there crosses nothing further. A run that later leaves
        the height, in either direction, does not cross it again on the way
        out. This asymmetry makes the halt safe to resume from. A halt leaves
        the run paused *on* the crossing step, so the next step's `before` is
        the halt's own reading. A rule closed on both sides would halt the run
        again at once and never let it pass the target. No per-target armed
        flag is needed for this. The arithmetic alone does it.

        Both directions count, because a target has no crossing direction (see
        the class docstring). A case taken up through 0.8 ×MAC and back down
        through it has reached what the learner marked twice, and it halts
        twice.

        Args:
            before: The reading of this target's compartment before the step,
                as a multiple of the running agent's 1 MAC. That is the unit
                the target is stored in, so no conversion happens here.
            after: The same compartment's reading after the step, in the same
                unit and from the same agent. Dividing the two readings by
                different agents' MAC would compare a correct number with the
                wrong divisor. That is why `SimulationController` converts both
                readings with the one `formatting.mac_multiple` and the
                snapshot's own `agent_mac_percent`.

        Returns:
            Whether the step crossed this height, in either direction.
        """

        height = self.mac_multiple

        return before < height <= after or before > height >= after


@dataclass(frozen=True, slots=True)
class BookmarkCrossing:
    """The marks that one simulation step passed through, and where the step landed.

    `SimulationController.advance` halts on this value. It has two collections
    rather than one discriminated list, for the same reason that `BookmarkSet`
    has two: a reader, or a status line, can address one kind without
    filtering out the other. Both may be non-empty, because one step can cross
    a marked instant and a marked height at once. At least one of them is
    non-empty, because a step that crossed nothing is not reported at all.

    Attributes:
        instant_s: The simulated time of the step that crossed the marks, in
            the case's own seconds. It is the completed step's own instant, so
            it lies on the run's `simulation_step_s` grid rather than on the
            coarser `multiplier ×` grid that a tick boundary can reach.
            `docs/MODEL.md` § "Halting on a marked crossing" states why that
            matters.
        time_bookmarks: The marked instants the step reached, in the order the
            set lists them.
        mac_targets: The marked heights the step crossed, in the order the set
            lists them.

    Raises:
        TypeError: If `instant_s` is not a `CaseInstant`
            (`core/supported_ranges.py`).
        SimulationConfigurationError: If both collections are empty.
    """

    instant_s: CaseInstant
    time_bookmarks: tuple[TimeBookmark, ...] = ()
    mac_targets: tuple[MacTarget, ...] = ()

    def __post_init__(self) -> None:
        require_case_instant("instant_s", self.instant_s)

        if not self.time_bookmarks and not self.mac_targets:
            raise SimulationConfigurationError(
                "a crossing names at least one mark; a step that crossed nothing is reported "
                "as no crossing at all rather than as an empty one"
            )


@dataclass(frozen=True, slots=True)
class BookmarkStandings:
    """Where each of a run's marks stands, keyed by the mark itself.

    **Keyed rather than ordered.** This is a matter of presentation
    correctness, not of lookup convenience. A row that looked up its standing
    by position could be rebound to its neighbour's standing by an edit to
    either collection. A mark listed as reached when the run reached a
    different one is a wrong label on a correct value, and `CLAUDE.md` treats
    that as a safety failure. A mark is frozen and hashable, so it can serve
    as the key to its own standing.

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
                for a set that contains this bookmark. Raising rather than
                returning `STILL_RUNNING` is deliberate. A default here would
                draw a row claiming that the run can still reach a mark nobody
                evaluated, which is a plausible-looking answer where there is
                none.
        """

        return _looked_up(self.time_bookmarks, bookmark, "time bookmark")

    def of_mac_target(self, target: MacTarget) -> MarkStanding:
        """This target's standing, raising as `of_time_bookmark` does."""

        return _looked_up(self.mac_targets, target, "MAC target")


def _looked_up[Mark: (TimeBookmark, MacTarget)](
    standings: Mapping[Mark, MarkStanding], mark: Mark, what: str
) -> MarkStanding:
    """Return one mark's standing, or raise an error naming the mark that was not evaluated.

    The type parameter is constrained to the two kinds of mark rather than
    taking a union of the two mapping types. A union would leave the key type
    unrelated to the mark passed in, so the type checker could not prove the
    indexing correct. That would be a real gap in the signature, not something
    to silence at the call site.
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
    """The two collections, stored together and listed apart.

    The set is frozen, and every edit returns a new set, for the same reason as
    the rest of this layer's values. A `SimulationSnapshot` carries one of these
    sets to the panel that lists it. If the panel could change the collection,
    the displayed list and the run it claims to describe could drift apart
    within a tick.

    The two tuples are separate members rather than one list with a
    discriminant. That lets a reader, such as a panel, address one kind without
    filtering out the other.

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
        """Whether nothing at all is marked, which is the state of a fresh case."""

        return not self.time_bookmarks and not self.mac_targets

    def with_time_bookmark(self, bookmark: TimeBookmark) -> BookmarkSet:
        """This set with `bookmark` added at the end.

        Raises:
            SimulationConfigurationError: If an instant that is already marked
                is marked again. One instant is one stop however many rows name
                it, so a second entry would be a row that never causes a halt
                of its own.
        """

        return BookmarkSet((*self.time_bookmarks, bookmark), self.mac_targets)

    def without_time_bookmark(self, bookmark: TimeBookmark) -> BookmarkSet:
        """This set with the bookmark at `bookmark`'s instant removed.

        The match is on the instant rather than on the whole value. So the
        bookmark is still removed when the caller did not reproduce its label.

        Raises:
            SimulationConfigurationError: If no bookmark is at that instant.
                Silently removing nothing would leave a panel reporting a
                deletion that did not happen.
        """

        kept = tuple(held for held in self.time_bookmarks if held.instant_s != bookmark.instant_s)

        if len(kept) == len(self.time_bookmarks):
            raise SimulationConfigurationError(
                f"no time bookmark stands at {bookmark.instant_s} s, so there is none to remove"
            )

        return BookmarkSet(kept, self.mac_targets)

    def held_time_bookmark(self, bookmark: TimeBookmark) -> TimeBookmark:
        """The bookmark this set contains at `bookmark`'s instant, exactly as the set stores it.

        The match is on the instant, as in `without_time_bookmark`, so a caller
        can name a mark without reproducing its label. The returned bookmark
        carries the label stored in the set, and that bookmark is the key that
        a `BookmarkStandings` looks up.

        Raises:
            SimulationConfigurationError: If no bookmark is at that instant.
                The message names the instant.
        """

        for held in self.time_bookmarks:
            if held.instant_s == bookmark.instant_s:
                return held

        raise SimulationConfigurationError(
            f"no time bookmark stands at {bookmark.instant_s} s, so there is no mark there"
        )

    def with_mac_target(self, target: MacTarget) -> BookmarkSet:
        """This set with `target` added at the end.

        Raises:
            SimulationConfigurationError: If the same compartment and height
                are already marked, for the reason that `with_time_bookmark`
                gives.
        """

        return BookmarkSet(self.time_bookmarks, (*self.mac_targets, target))

    def without_mac_target(self, target: MacTarget) -> BookmarkSet:
        """This set with the target that names `target`'s crossing removed.

        The match is on `MacTarget.crossing_key`, so the label plays no part.

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
        before_s: CaseInstant,
        after_s: CaseInstant,
        before: Mapping[RecordedQuantity, MacMultiple],
        after: Mapping[RecordedQuantity, MacMultiple],
    ) -> BookmarkCrossing | None:
        """Which of these marks one simulation step passed through.

        `SimulationController.advance` calls this once per completed step, with
        the readings from either side of that step. Testing every step is the
        whole point. A test applied once per rendered frame would place the
        halt up to `multiplier × simulation_step_s` past the value the learner
        marked, which is 30 simulated seconds at 300×. The same bookmark would
        then stop the run at a different concentration depending on the
        playback speed (`PL-NBWP`, `docs/MODEL.md` § "Supported simulation
        step").

        Args:
            before_s: The elapsed simulated time before the step, in the case's
                own seconds.
            after_s: The elapsed simulated time after the step, on the same
                axis.
            before: The reading of every compartment a target could name,
                before the step, as multiples of the running agent's 1 MAC.
            after: The same compartments after the step, in the same unit and
                against the same agent's MAC.

        Returns:
            The marks this step crossed, or `None` if it crossed nothing. The
            method returns `None` rather than an empty crossing, so a caller
            cannot halt a run on a value that says nothing happened.

        Raises:
            SimulationConfigurationError: If either reading omits a
                compartment that one of these targets names. Comparing against
                a missing reading is not allowed. A target that is silently
                skipped is a halt that never comes, and that is the failure
                this whole mechanism exists to prevent.
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
        reached_instants_s: frozenset[CaseInstant],
        reached_crossings: frozenset[tuple[RecordedQuantity, float]],
        opened_at_s: CaseInstant,
        elapsed_s: CaseInstant,
        stopped_at_cap: bool,
        run_failed: bool,
    ) -> BookmarkStandings:
        """Where each of these marks stands on one run.

        Every mark gets a standing, so a panel drawing this set can show one
        beside every row. The reader is then not left to infer from silence
        that nothing has happened. That silence is the "run stopping silently
        at the cap" that this mechanism was built to replace.

        Args:
            reached_instants_s: The instants this run has already halted on
                or stood on. Those are the instants inside the step the run
                opened on, if it is a branch, or inside the step it stands on
                while stopped.
            reached_crossings: The `MacTarget.crossing_key`s that the run has
                already halted on or stood on, in the same sense. Both sets are
                matched the way `without_time_bookmark` and
                `without_mac_target` match, so relabelling a mark does not
                reset what the run did.
            opened_at_s: Where this run began, in the case's own time: zero on
                a trunk, and `ResumePoint.fork.instant_s` on a branch. A time
                bookmark before this instant is `BEFORE_THIS_BRANCH`, because
                no step of this run can reach it. Even a reset returns a branch
                to its fork rather than to the case's opening.
            elapsed_s: Where the run's clock is now, on the same axis. Given
                these two instants, a marked instant's standing is a position
                rather than a history. `_time_bookmark_standing` explains what
                that gives, and `MarkStanding.PASSED` explains why it is the
                honest answer. A MAC target uses neither instant, because no
                clock orders a height.
            stopped_at_cap: Whether the run is at the supported run length
                and its next step is refused. Every mark still outstanding is
                then `NOT_REACHED_WITHIN_CAP`. No mark lies beyond that length,
                because a `TimeBookmark` past it cannot be built. So no mark
                could have been given that standing any sooner.
            run_failed: Whether the run is halted by a failure rather than
                paused. This is `SimulationController.has_failed`, the other
                state that `SimulationController.start` refuses to resume.
                Every mark still outstanding is then
                `NOT_REACHED_BEFORE_FAILURE`. Like `stopped_at_cap`, the
                argument is required and has no default. A caller that left it
                out would draw every mark on a run that cannot step again as
                one the run can still reach. That is the kind of
                plausible-looking row that `CLAUDE.md`'s safety-critical
                standard rejects in favour of an obvious answer (`PL-N3N5`).

        Returns:
            One standing per mark, keyed by the mark.

        Raises:
            SimulationConfigurationError: If `elapsed_s` is before
                `opened_at_s`. A run's clock starts at the run's own beginning
                and only increases. So if the two are reversed, a caller has
                paired one run's clock with another run's opening. Every
                bookmark row drawn from that pairing would then be placed
                against a run that does not exist. The method raises rather
                than clamping, because a clamp would give a plausible answer.
        """

        if elapsed_s < opened_at_s:
            raise SimulationConfigurationError(
                f"a run's clock stands at or after its own beginning; given a run opened at "
                f"{opened_at_s} s standing at {elapsed_s} s, so the marks cannot be placed "
                "against it"
            )

        return BookmarkStandings(
            time_bookmarks=MappingProxyType(
                {
                    bookmark: _time_bookmark_standing(
                        bookmark,
                        reached_instants_s=reached_instants_s,
                        opened_at_s=opened_at_s,
                        elapsed_s=elapsed_s,
                        stopped_at_cap=stopped_at_cap,
                        run_failed=run_failed,
                    )
                    for bookmark in self.time_bookmarks
                }
            ),
            mac_targets=MappingProxyType(
                {
                    target: _mac_target_standing(
                        target,
                        reached_crossings=reached_crossings,
                        stopped_at_cap=stopped_at_cap,
                        run_failed=run_failed,
                    )
                    for target in self.mac_targets
                }
            ),
        )


def _time_bookmark_standing(
    bookmark: TimeBookmark,
    *,
    reached_instants_s: frozenset[CaseInstant],
    opened_at_s: CaseInstant,
    elapsed_s: CaseInstant,
    stopped_at_cap: bool,
    run_failed: bool,
) -> MarkStanding:
    """One marked instant's standing, testing the six cases in an order that keeps them exclusive.

    **For a clock that only moves forward, the question is where the instant
    is, not what the run did** (`PL-3K9B`, project owner 2026-09-20,
    ratified). A run's clock only increases and never goes below
    `opened_at_s`. So a marked instant is either still ahead of the run or it
    is not. The halt set cannot settle this. The set records the instants at
    which this run *stopped*, and an instant can be behind the clock without
    the run ever having stopped there. Every case the item measured falls in
    that gap: a branch opening on the mark it forked at, a branch opening at a
    control event the mark sits on, a mark typed in behind a running clock, and
    a mark removed and added again. Each of them showed `STILL_RUNNING`, which
    says the run can still reach the mark, and in none of them could any step
    ever make that true.

    So the clock decides, in this order:

    1. **The halt set** comes first, because it covers the one case that the
       comparison below cannot see. A halt lands on the step that *crossed*
       the mark, so a fork taken there opens at the crossing step's own
       instant. That instant is at the marked instant or one step past it.
       For an instant that is not a multiple of the step in binary, it is past
       the marked instant by a few parts in 1e16. For example, with `45.3`
       marked and `45.300000000000004` forked at, the branch opens after its
       own mark. Only asking again about the step the branch opened on shows
       that the two are one crossing.
    2. **`opened_at_s <= instant_s <= elapsed_s`**: the run has been at that
       instant, whatever put it there.
    3. **`BEFORE_THIS_BRANCH`**, tested with a strict `<`, for an instant
       behind the run's own beginning. Its meaning and its wording are
       unchanged. Any instant that gets this far has not been claimed by 1 or
       2, so this case still only ever applies to a mark a branch inherited.
    4. **The cap**, then **the failure**, then **still running**.

    The cap outranks the failure when a run has both, because the cap came
    first. `SimulationController.advance` takes no step on a stopped run. So a
    run that is at the cap and has failed was failed by a setting made *after*
    it had already run out of supported time. The cap is then what the mark
    went unreached within. The cap is also the more durable answer of the two.
    A mark that the cap leaves ahead of the clock lies past the last instant a
    run at this step can stand on, so the fresh run that a reset would give
    also stops short of it. A mark that is merely unreached before a failure
    is not out of reach.

    `REACHED` is not among these cases. It is a historical claim, it is the
    answer that `_mac_target_standing` gives, and `MarkStanding` gives the
    argument for keeping the two vocabularies apart.
    """

    if bookmark.instant_s in reached_instants_s:
        return MarkStanding.PASSED

    if opened_at_s <= bookmark.instant_s <= elapsed_s:
        return MarkStanding.PASSED

    if bookmark.instant_s < opened_at_s:
        return MarkStanding.BEFORE_THIS_BRANCH

    if stopped_at_cap:
        return MarkStanding.NOT_REACHED_WITHIN_CAP

    if run_failed:
        return MarkStanding.NOT_REACHED_BEFORE_FAILURE

    return MarkStanding.STILL_RUNNING


def _mac_target_standing(
    target: MacTarget,
    *,
    reached_crossings: frozenset[tuple[RecordedQuantity, float]],
    stopped_at_cap: bool,
    run_failed: bool,
) -> MarkStanding:
    """One marked height's standing.

    There are four cases rather than six, and the two missing cases are the
    two that the clock supplies. A height is reachable from either side, so a
    branch may cross a height that its trunk never crossed. A target therefore
    cannot be `BEFORE_THIS_BRANCH`. A compartment may also arrive at a height,
    leave it and arrive again, so there is no position for `PASSED` to name
    either. What the run did is the only thing that can be said of a target,
    which is why `REACHED` belongs here.
    """

    if target.crossing_key in reached_crossings:
        return MarkStanding.REACHED

    if stopped_at_cap:
        return MarkStanding.NOT_REACHED_WITHIN_CAP

    if run_failed:
        return MarkStanding.NOT_REACHED_BEFORE_FAILURE

    return MarkStanding.STILL_RUNNING


def _require_readings(
    readings: Mapping[RecordedQuantity, MacMultiple], targets: tuple[MacTarget, ...], side: str
) -> None:
    """Refuse a reading set that omits a compartment one of these targets names.

    Args:
        readings: The readings passed in for one side of a step.
        targets: The marked heights that will be compared against the readings.
        side: `"before"` or `"after"`, so the message says which reading was
            incomplete rather than only that one was.

    Raises:
        SimulationConfigurationError: If a compartment is missing. The message
            names the first missing compartment.
    """

    for target in targets:
        if target.quantity not in readings:
            raise SimulationConfigurationError(
                f"the {side} reading names no {target.quantity.value} compartment, so the "
                f"target at {target.mac_multiple} ×MAC on it cannot be tested for a crossing"
            )


def _refuse_repeats(keys: Iterable[object], what: str, named: str) -> None:
    """Refuse a collection that contains two marks naming one crossing.

    Args:
        keys: What makes each mark distinct, in the collection's own order.
        what: The kind of mark, for the message.
        named: What the key is, in the reader's words, for the message.

    Raises:
        SimulationConfigurationError: If any key repeats. The message names
            the first repeat rather than the count, so it says which entry to
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
