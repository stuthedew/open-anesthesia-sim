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

**Detection is deliberately absent.** Whether a run has crossed a target, and
what stopping on the crossing step costs, is `PL-CTD7` and belongs in the
advance loop. Nothing here compares a mark against a state, so nothing here can
overshoot one.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from math import isfinite

from anesthesia_sim.app.run_series import COMPARTMENT_QUANTITIES, RecordedQuantity
from anesthesia_sim.core.concentration import MacMultiple
from anesthesia_sim.core.exceptions import SimulationConfigurationError

__all__ = ["BookmarkSet", "MacTarget", "TimeBookmark"]


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
    `RunDefinition` opens a branch at the fork instant rather than re-basing to
    zero, so one number means the same thing on every run of a case.

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
