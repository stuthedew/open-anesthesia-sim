"""Test what a mark rejects, and how the two collections keep the two kinds of mark apart.

`app/bookmarks.py` decides nothing about a run. It decides what a learner is
allowed to have *asked*. So the claims here are all about the boundary: which
values are refused, and with what message. They are also about the two
collections keeping the two kinds of mark separable, which is the property
`PL-LPLD` was scoped on.

Crossing detection arrived with `PL-CTD7` and is tested here too, in two
halves that stay apart. The predicates and the standings (each mark's status in
a run) are pure functions: two readings go in, and a result comes out. So they
are asserted directly, including the boundary cases that no live run
reproduces on demand. The halt itself is a property of the advance loop rather
than of a value. So it is asserted against a real `SimulationController`
stepped at 1× and at 300×. The claim that `PL-CTD7` exists to make is that
those two agree, and only running them can show it.
"""

import math

import pytest

from anesthesia_sim.app.bookmarks import (
    BookmarkCrossing,
    BookmarkSet,
    MacTarget,
    MarkStanding,
    TimeBookmark,
)
from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.app.formatting import mac_multiple
from anesthesia_sim.app.run_series import COMPARTMENT_QUANTITIES, RecordedQuantity
from anesthesia_sim.core.concentration import MacMultiple, Percent
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.simulation_step import SIMULATION_STEP_S
from anesthesia_sim.core.supported_ranges import (
    MAXIMUM_ELAPSED_SIMULATION_TIME_S,
    AlveolarVentilation,
    CaseInstant,
)

#: The burst of steps that one tick advances at 300× real time. That is the
#: coarsest rate that `app/playback.py` offers, and the worst case that `PL-CTD7`
#: is about: 30 simulated seconds with nothing serviced between the steps.
STEPS_PER_TICK_AT_300X = 30


def _target(
    quantity: RecordedQuantity = RecordedQuantity.VESSEL_RICH,
    multiple: float = 0.8,
    label: str | None = None,
) -> MacTarget:
    """Build a MAC target with defaults, so that a test states only the field it is about."""

    return MacTarget(quantity, MacMultiple(multiple), label)


# ------------------------------------------------------------ time bookmarks


def test_a_time_bookmark_holds_its_instant_and_no_name_by_default() -> None:
    bookmark = TimeBookmark(CaseInstant(600))

    assert bookmark.instant_s == 600
    assert bookmark.label is None


def test_a_time_bookmark_keeps_the_name_it_was_given_without_surrounding_space() -> None:
    assert TimeBookmark(CaseInstant(600), "  intubation  ").label == "intubation"


@pytest.mark.parametrize("instant_s", [-1, MAXIMUM_ELAPSED_SIMULATION_TIME_S + 1])
def test_an_instant_no_case_reaches_cannot_be_marked(instant_s: int) -> None:
    """No mark can be made before the case opens or past the span.

    `PL-CN5S`: the mark is built from a `CaseInstant`, which refuses each of
    these instants with a message that names the supported run length. So no set
    ever holds such a mark.
    """

    with pytest.raises(SimulationConfigurationError, match="outside the supported run length"):
        CaseInstant(instant_s)


@pytest.mark.parametrize("instant_s", [45.3, 600.0, math.inf, -math.inf, math.nan])
def test_an_instant_between_two_seconds_cannot_be_marked(instant_s: float) -> None:
    """No mark can be made at an instant that no clock reaches.

    A run stands only on whole seconds. So a `CaseInstant` refuses every
    `float`, even a whole one such as 600.0, and no set ever holds a mark
    inside a step (`PL-SZ6G`).
    """

    with pytest.raises(TypeError, match="has type float, not int"):
        CaseInstant(instant_s)  # type: ignore[arg-type]


@pytest.mark.parametrize("instant_s", [600, 600.0, math.nan])
def test_a_time_bookmark_refuses_an_instant_not_built_as_a_case_instant(instant_s: float) -> None:
    """The instant is refused whatever its value, because nothing has checked it (`PL-CN5S`)."""

    with pytest.raises(TypeError, match="instant_s of .* was not built as CaseInstant"):
        TimeBookmark(instant_s)  # type: ignore[arg-type]


def test_the_case_opening_itself_is_a_markable_instant() -> None:
    assert TimeBookmark(CaseInstant(0)).instant_s == 0


def test_a_blank_name_is_refused_rather_than_read_as_no_name() -> None:
    # An empty row in a list is indistinguishable from a rendering failure,
    # and `None` already means "list it under its own value".
    with pytest.raises(SimulationConfigurationError, match="blank"):
        TimeBookmark(CaseInstant(600), "   ")


def test_no_mark_of_either_kind_carries_a_crossing_direction() -> None:
    # The minimum scope, taken from the reference simulator, included a crossing
    # direction. The project owner removed it on 2026-09-20. A height is a
    # height, and a run that passes through it going up, and again coming down,
    # has reached the marked height both times.
    assert not hasattr(TimeBookmark(CaseInstant(600)), "direction")
    assert not hasattr(_target(), "direction")


# --------------------------------------------------------------- MAC targets


def test_a_mac_target_names_the_compartment_it_is_read_against() -> None:
    target = _target(RecordedQuantity.MUSCLE)

    assert target.quantity is RecordedQuantity.MUSCLE
    assert target.mac_multiple == 0.8


@pytest.mark.parametrize("quantity", COMPARTMENT_QUANTITIES)
def test_every_drawn_compartment_may_carry_a_target(quantity: RecordedQuantity) -> None:
    # The minimum scope covers the six graphed compartments, not the alveolar
    # trace alone (`PL-LPLD`). So these six are everything a picker may offer.
    assert _target(quantity).quantity is quantity


def test_the_wash_in_ratio_may_not_carry_a_target() -> None:
    # The wash-in ratio is a quotient of two compartments rather than a
    # concentration. So a multiple of MAC of it is not a quantity that the model
    # represents. It is also the one member of `RecordedQuantity` that a
    # compartment picker could offer by mistake.
    with pytest.raises(SimulationConfigurationError, match="not one of"):
        _target(RecordedQuantity.WASH_IN_RATIO)


@pytest.mark.parametrize("multiple", [0.0, -0.5, math.inf, math.nan])
def test_a_target_at_a_height_no_compartment_can_cross_is_refused(multiple: float) -> None:
    # Zero is rejected along with the negatives. Every compartment starts at
    # zero, so every run would already be at such a target before it began.
    with pytest.raises(SimulationConfigurationError, match="height above zero"):
        _target(multiple=multiple)


def test_a_target_refusal_names_the_height_that_failed() -> None:
    # `.claude/rules/sources-and-docstrings.md` requires a refusal to name what
    # was refused, so that a rejected setting stays traceable to the input
    # behind it.
    with pytest.raises(SimulationConfigurationError, match=r"-0\.5"):
        _target(multiple=-0.5)


def test_a_target_keeps_the_name_it_was_given_without_surrounding_space() -> None:
    """A target's name is checked as a time bookmark's is: trimmed, and refused when blank.

    The marks panel lists a target under its name. A name lost here would list
    the target under its compartment and height instead, as if the learner had
    never named it.
    """

    assert _target(label="  wash-in  ").label == "wash-in"

    with pytest.raises(SimulationConfigurationError, match="blank"):
        _target(label="   ")


def test_two_targets_differing_only_in_label_name_one_crossing() -> None:
    assert _target(label="wash-in").crossing_key == _target(label="emergence").crossing_key


def test_a_different_height_on_one_compartment_is_a_different_crossing() -> None:
    assert _target(multiple=0.8).crossing_key != _target(multiple=0.5).crossing_key


# ------------------------------------------------------------- the two sets


def test_a_fresh_set_is_empty_in_both_collections() -> None:
    marks = BookmarkSet()

    assert marks.is_empty
    assert marks.time_bookmarks == ()
    assert marks.mac_targets == ()


def test_the_two_kinds_are_listed_apart_rather_than_filtered_out_of_one_list() -> None:
    marks = (
        BookmarkSet().with_time_bookmark(TimeBookmark(CaseInstant(600))).with_mac_target(_target())
    )

    assert marks.time_bookmarks == (TimeBookmark(CaseInstant(600)),)
    assert marks.mac_targets == (_target(),)
    assert not marks.is_empty


def test_adding_a_mark_leaves_the_set_it_was_added_to_alone() -> None:
    before = BookmarkSet()
    after = before.with_time_bookmark(TimeBookmark(CaseInstant(600)))

    assert before.time_bookmarks == ()
    assert after.time_bookmarks == (TimeBookmark(CaseInstant(600)),)


def test_marks_are_listed_in_the_order_they_were_added() -> None:
    marks = (
        BookmarkSet()
        .with_time_bookmark(TimeBookmark(CaseInstant(600)))
        .with_time_bookmark(TimeBookmark(CaseInstant(120)))
    )

    assert [bookmark.instant_s for bookmark in marks.time_bookmarks] == [600, 120]


def test_an_instant_already_marked_may_not_be_marked_again() -> None:
    marks = BookmarkSet().with_time_bookmark(TimeBookmark(CaseInstant(600)))

    with pytest.raises(SimulationConfigurationError, match="marked once"):
        marks.with_time_bookmark(TimeBookmark(CaseInstant(600), "second thoughts"))


def test_the_repeated_instant_refusal_is_pinned_whole() -> None:
    """Pin the whole sentence that the marks editor shows when an instant is marked twice.

    The test above matches only "marked once", which would pass even with the
    instant missing from the message (`PL-79PK`). The matching MAC-target message
    is not pinned. It names its crossing by the Python repr of an enum member,
    which is a defect of its own rather than a sentence to freeze.
    """

    marks = BookmarkSet().with_time_bookmark(TimeBookmark(CaseInstant(600)))

    with pytest.raises(SimulationConfigurationError) as refusal:
        marks.with_time_bookmark(TimeBookmark(CaseInstant(600), "second thoughts"))

    assert str(refusal.value) == (
        "an instant is marked once: a second time bookmark naming 600 would be a row no "
        "run could stop at on its own account"
    )


def test_a_crossing_already_marked_may_not_be_marked_again() -> None:
    marks = BookmarkSet().with_mac_target(_target())

    with pytest.raises(SimulationConfigurationError, match="marked once"):
        marks.with_mac_target(_target(label="again"))


def test_two_heights_on_one_compartment_are_two_crossings() -> None:
    marks = BookmarkSet().with_mac_target(_target(multiple=0.8))
    both = marks.with_mac_target(_target(multiple=0.5))

    assert len(both.mac_targets) == 2


def test_the_same_height_on_another_compartment_is_a_different_crossing() -> None:
    marks = BookmarkSet().with_mac_target(_target(RecordedQuantity.VESSEL_RICH))
    both = marks.with_mac_target(_target(RecordedQuantity.FAT))

    assert len(both.mac_targets) == 2


def test_removing_a_time_bookmark_leaves_the_targets_alone() -> None:
    marks = (
        BookmarkSet().with_time_bookmark(TimeBookmark(CaseInstant(600))).with_mac_target(_target())
    )
    after = marks.without_time_bookmark(TimeBookmark(CaseInstant(600)))

    assert after.time_bookmarks == ()
    assert after.mac_targets == (_target(),)


def test_adding_a_time_bookmark_leaves_the_targets_alone() -> None:
    """A time bookmark added to a set that already holds targets keeps every target, in order.

    The other tests add the time bookmark before any target, so they cannot
    tell this edit from one that builds the new set without its targets. A
    target dropped that way is a halt that never comes.
    """

    low = _target(multiple=0.5)
    high = _target(multiple=0.8)
    marks = BookmarkSet().with_mac_target(low).with_mac_target(high)

    after = marks.with_time_bookmark(TimeBookmark(CaseInstant(600)))

    assert after.mac_targets == (low, high)
    assert after.time_bookmarks == (TimeBookmark(CaseInstant(600)),)


def test_removing_one_target_leaves_the_other_targets_and_the_time_bookmarks_alone() -> None:
    """Removing the middle one of three targets keeps the first and the third, and every bookmark.

    So a removal that kept only the first target, only the last or none of
    them gives a different list from the right one.
    """

    bookmark = TimeBookmark(CaseInstant(600))
    low = _target(multiple=0.5)
    middle = _target(multiple=0.8)
    high = _target(multiple=1.2)
    marks = (
        BookmarkSet()
        .with_time_bookmark(bookmark)
        .with_mac_target(low)
        .with_mac_target(middle)
        .with_mac_target(high)
    )

    after = marks.without_mac_target(middle)

    assert after.mac_targets == (low, high)
    assert after.time_bookmarks == (bookmark,)


def test_a_time_bookmark_is_removed_by_its_instant_rather_than_by_its_name() -> None:
    marks = BookmarkSet().with_time_bookmark(TimeBookmark(CaseInstant(600), "intubation"))

    assert marks.without_time_bookmark(TimeBookmark(CaseInstant(600))).time_bookmarks == ()


def test_a_target_is_removed_by_its_crossing_rather_than_by_its_name() -> None:
    marks = BookmarkSet().with_mac_target(_target(label="wash-in"))

    assert marks.without_mac_target(_target()).mac_targets == ()


def test_removing_a_time_bookmark_that_is_not_there_is_refused() -> None:
    # Removing nothing silently would leave a panel reporting a deletion that
    # did not happen.
    with pytest.raises(SimulationConfigurationError, match="none to remove"):
        BookmarkSet().without_time_bookmark(TimeBookmark(CaseInstant(600)))


def test_removing_a_target_that_is_not_there_is_refused() -> None:
    with pytest.raises(SimulationConfigurationError, match="none to remove"):
        BookmarkSet().without_mac_target(_target())


def test_a_removal_refusal_names_the_crossing_it_could_not_find() -> None:
    with pytest.raises(SimulationConfigurationError, match="vessel_rich"):
        BookmarkSet().without_mac_target(_target())


def test_a_set_built_directly_from_repeated_marks_is_refused_too() -> None:
    # The collection enforces the invariant, not the method that adds a mark.
    # So a caller that constructs a set directly cannot get round it.
    with pytest.raises(SimulationConfigurationError, match="marked once"):
        BookmarkSet((TimeBookmark(CaseInstant(600)), TimeBookmark(CaseInstant(600))))


# ------------------------------------------------------- crossing predicates
#
# A crossing is a transition between two readings, not a comparison made at one
# reading (project owner, 2026-09-20). Everything below depends on that. At the
# boundary cases, a rule that compared a single reading would either stall a run
# forever on a height it settled at, or halt it again the moment it was resumed.


def _readings(**multiples: float) -> dict[RecordedQuantity, MacMultiple]:
    """Build the readings on one side of a step, for every compartment a target could use.

    Compartments that are not named read zero, which is where a case opens. So a
    test states only the compartment it is about.
    """

    readings = {quantity: MacMultiple(0.0) for quantity in COMPARTMENT_QUANTITIES}
    readings.update(
        {RecordedQuantity(name): MacMultiple(value) for name, value in multiples.items()}
    )

    return readings


def test_a_time_bookmark_is_crossed_by_the_step_that_reaches_it() -> None:
    bookmark = TimeBookmark(CaseInstant(30))

    assert bookmark.crossed_between(CaseInstant(29), CaseInstant(30))
    assert bookmark.crossed_between(CaseInstant(29), CaseInstant(31))


def test_a_time_bookmark_is_not_crossed_again_by_the_step_after_it() -> None:
    """Each step covers an interval open below and closed above, so an instant is reached once."""

    bookmark = TimeBookmark(CaseInstant(30))

    assert not bookmark.crossed_between(CaseInstant(30), CaseInstant(31))
    assert not bookmark.crossed_between(CaseInstant(28), CaseInstant(29))


# ----------------------------------------------- the step that reaches a mark
#
# `TimeBookmark.steps_to_reach` is the inverse of `crossed_between`. The count it
# returns is the step that the predicate names as the crossing step. So that
# count is where a halt stops and where `resumed_at_mark` forks (`PL-W4XQ`). The
# tests below check it against the predicate itself, and against the count of
# seconds, which is the count of one-second steps.


def _reaching_step_is_the_crossing_one(instant_s: int) -> bool:
    """Return whether `steps_to_reach` names the step that `crossed_between` says reaches it."""

    bookmark = TimeBookmark(CaseInstant(instant_s))
    count = bookmark.steps_to_reach()

    if count == 0:
        return instant_s == 0

    return bookmark.crossed_between(
        CaseInstant((count - 1) * SIMULATION_STEP_S), CaseInstant(count * SIMULATION_STEP_S)
    )


def test_every_instant_a_learner_can_type_is_reached_on_the_step_the_halt_names() -> None:
    """Check all 3 601 whole seconds up to an hour, the dialog's own resolution.

    Each instant is reached by exactly the step that `crossed_between` picks.
    """

    misses = [
        instant_s for instant_s in range(3_601) if not _reaching_step_is_the_crossing_one(instant_s)
    ]

    assert misses == []


def test_every_instant_is_reached_by_the_step_that_lands_on_it() -> None:
    """A step is one second, so a mark at N seconds is reached by step N."""

    misses = [
        count
        for count in range(1, 3_601)
        if TimeBookmark(CaseInstant(count)).steps_to_reach() != count
    ]

    assert misses == []


def test_a_mark_at_the_case_s_opening_is_reached_by_no_step() -> None:
    """A run is already at that instant before it steps, and `crossed_between` never fires there."""

    assert TimeBookmark(CaseInstant(0)).steps_to_reach() == 0


def test_the_last_supported_instant_is_reached_on_the_last_supported_step() -> None:
    """At the far boundary, the count stays inside the supported span and does not run past it."""

    last = TimeBookmark(CaseInstant(MAXIMUM_ELAPSED_SIMULATION_TIME_S))
    count = last.steps_to_reach()

    assert count * SIMULATION_STEP_S == MAXIMUM_ELAPSED_SIMULATION_TIME_S
    assert _reaching_step_is_the_crossing_one(MAXIMUM_ELAPSED_SIMULATION_TIME_S)


def test_a_held_bookmark_is_found_by_its_instant_and_returned_as_the_set_holds_it() -> None:
    """The lookup returns the bookmark as the set stores it, with its label.

    The standings are keyed by the stored bookmark, label included, so that is the
    bookmark a caller needs in order to look up its standing.
    """

    marks = BookmarkSet().with_time_bookmark(TimeBookmark(CaseInstant(600), "intubation"))

    assert marks.held_time_bookmark(TimeBookmark(CaseInstant(600))) == TimeBookmark(
        CaseInstant(600), "intubation"
    )


def test_a_bookmark_the_set_does_not_hold_is_refused_by_its_instant() -> None:
    with pytest.raises(SimulationConfigurationError, match="no time bookmark stands at 10m,"):
        BookmarkSet().held_time_bookmark(TimeBookmark(CaseInstant(600)))


def test_a_target_is_crossed_by_the_step_that_reaches_its_height() -> None:
    target = _target(multiple=0.8)

    assert target.crossed_between(MacMultiple(0.79), MacMultiple(0.81))
    assert target.crossed_between(MacMultiple(0.79), MacMultiple(0.80))


def test_a_target_is_crossed_going_down_as_well_as_going_up() -> None:
    """A target carries no direction, so a wash-out crosses it as a wash-in does."""

    target = _target(multiple=0.8)

    assert target.crossed_between(MacMultiple(0.81), MacMultiple(0.79))
    assert target.crossed_between(MacMultiple(0.81), MacMultiple(0.80))


def test_a_target_a_run_settles_exactly_on_is_crossed_once_and_not_again() -> None:
    """This is the case in which a rule comparing one reading would never let a run past.

    If the rule were "the reading is at or above the height", every later step of
    a run sitting exactly on the height would report a crossing, and the run
    could not be advanced at all.
    """

    target = _target(multiple=0.8)

    assert target.crossed_between(MacMultiple(0.79), MacMultiple(0.80))
    assert not target.crossed_between(MacMultiple(0.80), MacMultiple(0.80))


def test_a_target_is_not_crossed_by_leaving_its_height_in_either_direction() -> None:
    """Leaving the height is not a crossing, so a halted run resumes without halting there again."""

    target = _target(multiple=0.8)

    assert not target.crossed_between(MacMultiple(0.80), MacMultiple(0.81))
    assert not target.crossed_between(MacMultiple(0.80), MacMultiple(0.79))


def test_a_reading_within_one_part_in_a_hundred_thousand_of_the_height_is_at_it() -> None:
    """A reading that settles on the height and moves by a unit in the last place crosses it once.

    `PL-QVBR` made the height a band one part in a hundred thousand wide on
    either side. Without the band, a canonical reading that moved between the
    height and the float below it crossed the height each time it returned.
    """

    target = _target(multiple=1.0)
    inside_below = MacMultiple(1.0 - 0.9e-5)
    inside_above = MacMultiple(1.0 + 0.9e-5)

    assert target.crossed_between(MacMultiple(0.99), inside_below)
    assert target.crossed_between(MacMultiple(1.0 - 1.1e-5), inside_below)
    assert target.crossed_between(MacMultiple(1.01), inside_above)
    assert not target.crossed_between(inside_below, inside_above)
    assert not target.crossed_between(MacMultiple(math.nextafter(1.0, 0.0)), MacMultiple(1.0))
    assert not target.crossed_between(inside_above, MacMultiple(1.01))
    assert not target.crossed_between(MacMultiple(0.99), MacMultiple(1.0 - 1.1e-5))


def test_a_reading_exactly_on_the_lower_edge_of_the_band_is_inside_it() -> None:
    """The band includes its lower edge, and the next float below that edge is outside it.

    The target is at 1.00 ×MAC, so the band around it has a half-width of
    `HEIGHT_BAND`, which is 1e-5, times 1.0. Multiplying by 1.0 adds no rounding,
    which leaves the lower edge at exactly `1.0 - 1e-5`. A step that lands on
    the edge from below therefore crosses the target, and a step from the edge
    to 1.00 ×MAC crosses nothing.
    """

    target = _target(multiple=1.0)
    lower_edge = MacMultiple(1.0 - 1e-5)
    just_below = MacMultiple(math.nextafter(1.0 - 1e-5, 0.0))

    assert target.crossed_between(MacMultiple(0.99), lower_edge)
    assert not target.crossed_between(lower_edge, MacMultiple(1.0))
    assert not target.crossed_between(MacMultiple(0.99), just_below)
    assert target.crossed_between(just_below, lower_edge)


def test_a_reading_exactly_on_the_upper_edge_of_the_band_is_inside_it() -> None:
    """The band includes its upper edge, and the next float above that edge is outside it.

    This mirrors the test of the lower edge, for a reading that falls onto the
    target from above.
    """

    target = _target(multiple=1.0)
    upper_edge = MacMultiple(1.0 + 1e-5)
    just_above = MacMultiple(math.nextafter(1.0 + 1e-5, 2.0))

    assert target.crossed_between(MacMultiple(1.01), upper_edge)
    assert not target.crossed_between(upper_edge, MacMultiple(1.0))
    assert not target.crossed_between(MacMultiple(1.01), just_above)
    assert target.crossed_between(just_above, upper_edge)


@pytest.mark.parametrize("height", [0.5, 2.0])
def test_the_band_around_a_target_is_the_same_share_of_any_height(height: float) -> None:
    """The band reaches one part in a hundred thousand of the height on either side, at any height.

    The tests above use a target at 1.00 ×MAC. There, a band that is a share
    of the height and a band that is divided by the height have the same
    width. At 0.5 and 2.0 ×MAC the two widths differ by a factor of four. A
    reading 0.9 parts in a hundred thousand from the height is inside the
    band, and a reading 1.1 parts away is outside it, above and below.
    """

    target = _target(multiple=height)

    for side in (1.0, -1.0):
        start = MacMultiple(height * (1.0 + side * 0.01))
        inside = MacMultiple(height * (1.0 + side * 0.9e-5))
        outside = MacMultiple(height * (1.0 + side * 1.1e-5))

        assert target.crossed_between(start, inside)
        assert not target.crossed_between(start, outside)


def test_a_step_that_crossed_nothing_is_reported_as_no_crossing() -> None:
    marks = (
        BookmarkSet().with_time_bookmark(TimeBookmark(CaseInstant(30))).with_mac_target(_target())
    )

    assert (
        marks.crossings_between(
            before_s=CaseInstant(10),
            after_s=CaseInstant(11),
            before=_readings(vessel_rich=0.1),
            after=_readings(vessel_rich=0.2),
        )
        is None
    )


def test_one_step_can_cross_a_marked_instant_and_a_marked_height_at_once() -> None:
    target = _target(multiple=0.8)
    marks = BookmarkSet().with_time_bookmark(TimeBookmark(CaseInstant(30))).with_mac_target(target)

    crossing = marks.crossings_between(
        before_s=CaseInstant(29),
        after_s=CaseInstant(30),
        before=_readings(vessel_rich=0.79),
        after=_readings(vessel_rich=0.81),
    )

    assert crossing == BookmarkCrossing(
        CaseInstant(30), (TimeBookmark(CaseInstant(30)),), (target,)
    )


def test_a_reading_missing_a_marked_compartment_is_refused() -> None:
    marks = BookmarkSet().with_mac_target(_target(RecordedQuantity.FAT))
    short = {RecordedQuantity.VESSEL_RICH: MacMultiple(0.1)}

    with pytest.raises(SimulationConfigurationError, match="no fat compartment"):
        marks.crossings_between(
            before_s=CaseInstant(0), after_s=CaseInstant(1), before=short, after=short
        )


def test_a_crossing_naming_no_mark_at_all_is_refused() -> None:
    with pytest.raises(SimulationConfigurationError, match="at least one mark"):
        BookmarkCrossing(CaseInstant(30))


def test_a_crossing_refuses_an_instant_not_built_as_a_case_instant() -> None:
    """A run stores the crossing it halted on, so the crossing checks its instant (`PL-CN5S`)."""

    with pytest.raises(TypeError, match="instant_s of 30.0 was not built as CaseInstant"):
        BookmarkCrossing(30.0, (TimeBookmark(CaseInstant(30)),))  # type: ignore[arg-type]


# ------------------------------------------------------------------ standings


def _standings(
    marks: BookmarkSet,
    *,
    reached_crossings: frozenset[tuple[RecordedQuantity, float]] = frozenset(),
    opened_at_s: int = 0,
    elapsed_s: int | None = None,
    stopped_at_cap: bool = False,
    run_failed: bool = False,
) -> object:
    """Compute this set's standings with defaults, so that a test states only the fact it is about.

    `elapsed_s` defaults to the run's own opening, which describes a run that has
    not stepped. Every marked instant is still ahead of such a run. So a test
    about something other than the clock does not get its result quietly from the
    clock. The instants are built as `CaseInstant`s here, as a run's own clock
    builds them, so that a test can state them as plain numbers.
    """

    return marks.standings(
        reached_crossings=reached_crossings,
        opened_at_s=CaseInstant(opened_at_s),
        elapsed_s=CaseInstant(opened_at_s if elapsed_s is None else elapsed_s),
        stopped_at_cap=stopped_at_cap,
        run_failed=run_failed,
    )


def test_a_mark_the_run_can_still_reach_stands_as_still_running() -> None:
    bookmark = TimeBookmark(CaseInstant(600))
    target = _target()
    marks = BookmarkSet().with_time_bookmark(bookmark).with_mac_target(target)

    standings = _standings(marks)

    assert standings.of_time_bookmark(bookmark) is MarkStanding.STILL_RUNNING
    assert standings.of_mac_target(target) is MarkStanding.STILL_RUNNING


def test_a_height_the_run_halted_on_stands_as_reached() -> None:
    """`REACHED` is a target's own standing, and only a target can have it.

    A height is not ordered by a clock. A compartment arrives at it, leaves it,
    and may arrive again. So the only thing that can be said of a height is what
    the run *did*, and that is what `REACHED` says.
    """

    target = _target()
    marks = BookmarkSet().with_mac_target(target)

    standings = _standings(marks, reached_crossings=frozenset({target.crossing_key}))

    assert standings.of_mac_target(target) is MarkStanding.REACHED


def test_an_instant_the_run_halted_on_stands_as_passed_rather_than_reached() -> None:
    """The two kinds of mark use different standings, and this is where they could be confused.

    The run halted on this instant and stands on it, which is the historical
    claim that `REACHED` makes. But the standing is still the positional one.
    A clock taken backwards would revoke the history, while the mark stayed
    perfectly reachable (`PL-3K9B`).
    """

    bookmark = TimeBookmark(CaseInstant(600))
    marks = BookmarkSet().with_time_bookmark(bookmark)

    standings = _standings(marks, elapsed_s=600)

    assert standings.of_time_bookmark(bookmark) is MarkStanding.PASSED
    assert standings.of_time_bookmark(bookmark) is not MarkStanding.REACHED


def test_a_relabelled_mark_keeps_what_the_run_did_with_it() -> None:
    """The mark is matched the way `without_mac_target` matches, so a rename is not a new mark."""

    renamed = _target(label="second gas on")
    marks = BookmarkSet().with_mac_target(renamed)

    standings = _standings(marks, reached_crossings=frozenset({_target().crossing_key}))

    assert standings.of_mac_target(renamed) is MarkStanding.REACHED


def test_a_target_still_outstanding_at_the_supported_run_length_says_it_was_not_reached() -> None:
    """A threshold above a compartment's asymptote, which is never reached.

    The run stops at the limit in `docs/INTERFACE.md` § "Supported run length", and
    by then it has answered the question. So the row must not go on saying that
    the run is still working on it.
    """

    above_the_asymptote = _target(multiple=0.95)
    marks = BookmarkSet().with_mac_target(above_the_asymptote)

    standings = _standings(marks, stopped_at_cap=True)

    assert standings.of_mac_target(above_the_asymptote) is MarkStanding.NOT_REACHED_WITHIN_CAP


def test_a_bookmark_before_a_branch_fork_reads_apart_from_the_cap_case() -> None:
    """The fourth outcome, and the reason there are four rather than three.

    A branch inherits its trunk's marks. So a bookmark before the fork is carried
    over, and the branch can never reach it going forward. Reporting it as "not
    reached within the cap" would say that running longer might reach it, which
    is false.
    """

    inherited = TimeBookmark(CaseInstant(120))
    marks = BookmarkSet().with_time_bookmark(inherited)

    standings = _standings(marks, opened_at_s=300)

    assert standings.of_time_bookmark(inherited) is MarkStanding.BEFORE_THIS_BRANCH
    assert standings.of_time_bookmark(inherited) is not MarkStanding.NOT_REACHED_WITHIN_CAP


def test_a_mark_outstanding_on_a_failed_run_is_not_reported_as_still_reachable() -> None:
    """The sixth outcome (`PL-N3N5`), for the state that the other five cannot express.

    `SimulationController.start` refuses a failed session with "cannot resume a
    failed simulation ... reset it first", because its next step would raise as
    its last one did. `STILL_RUNNING` says that the run *can still reach* the
    mark and has not reached it yet. The first half of that is false for every
    mark that such a run has not reached.

    Both kinds of mark are asserted, because the failure ends a clock and a
    height alike. That is why the outcome is a standing for both kinds rather
    than for the bookmark alone.
    """

    bookmark = TimeBookmark(CaseInstant(600))
    target = _target()
    marks = BookmarkSet().with_time_bookmark(bookmark).with_mac_target(target)

    standings = _standings(marks, run_failed=True)

    assert standings.of_time_bookmark(bookmark) is MarkStanding.NOT_REACHED_BEFORE_FAILURE
    assert standings.of_mac_target(target) is MarkStanding.NOT_REACHED_BEFORE_FAILURE


def test_a_failed_run_reads_apart_from_one_that_ran_out_of_supported_time() -> None:
    """The two refusals stop a run for opposite reasons, so they are two different standings.

    At the cap, the model has answered the question, and a longer run would not
    change the answer. In a failure, the model could not answer at all. Reporting
    a failure as the cap would tell a learner that the mark lies beyond what the
    model supports. That is a claim about the model rather than about this run. A
    fresh run, started by the reset that the failure demands, would show the
    claim to be false.
    """

    bookmark = TimeBookmark(CaseInstant(600))
    marks = BookmarkSet().with_time_bookmark(bookmark)

    failed = _standings(marks, run_failed=True)

    assert failed.of_time_bookmark(bookmark) is MarkStanding.NOT_REACHED_BEFORE_FAILURE
    assert failed.of_time_bookmark(bookmark) is not MarkStanding.NOT_REACHED_WITHIN_CAP
    assert _standings(marks, stopped_at_cap=True).of_time_bookmark(bookmark) is (
        MarkStanding.NOT_REACHED_WITHIN_CAP
    )


def test_the_cap_answers_for_a_run_standing_at_it_that_then_failed() -> None:
    """A run that carries both refusals reports the cap, and this is why.

    `SimulationController.advance` takes no step on a stopped run. So a run that
    stands at the cap and has failed was failed by a setting *after* it ran out
    of supported time. The cap is the limit within which the mark went unreached,
    and the failure came after the question had been answered. The cap is also
    the more durable of the two, because it is the one that the reset would not
    clear.
    """

    bookmark = TimeBookmark(CaseInstant(600))
    target = _target()
    marks = BookmarkSet().with_time_bookmark(bookmark).with_mac_target(target)

    standings = _standings(marks, stopped_at_cap=True, run_failed=True)

    assert standings.of_time_bookmark(bookmark) is MarkStanding.NOT_REACHED_WITHIN_CAP
    assert standings.of_mac_target(target) is MarkStanding.NOT_REACHED_WITHIN_CAP


def test_a_failure_stops_a_clock_without_taking_it_back() -> None:
    """A failure does not revoke the two standings that describe what has already happened.

    A marked instant at or behind the clock was passed, and a height the run
    halted on was reached, whatever stopped the run afterwards. Reporting either
    as unreached would withdraw a true claim about the case. That would be the
    mirror image of the defect that this outcome was added for.
    """

    passed = TimeBookmark(CaseInstant(30))
    reached = _target()
    marks = BookmarkSet().with_time_bookmark(passed).with_mac_target(reached)

    standings = _standings(
        marks, elapsed_s=60, reached_crossings=frozenset({reached.crossing_key}), run_failed=True
    )

    assert standings.of_time_bookmark(passed) is MarkStanding.PASSED
    assert standings.of_mac_target(reached) is MarkStanding.REACHED


def test_an_inherited_bookmark_on_a_failed_branch_still_reads_before_the_branch() -> None:
    """The statically decidable standing takes precedence over the failure, as it does over the cap.

    This branch could not have reached an instant before the fork even if it had
    run perfectly. So naming the failure would suggest that the failure is the
    reason. A reset also returns a branch to its fork rather than to the case's
    opening, so the next run of the branch cannot reach the instant either.
    """

    inherited = TimeBookmark(CaseInstant(120))
    marks = BookmarkSet().with_time_bookmark(inherited)

    standings = _standings(marks, opened_at_s=300, run_failed=True)

    assert standings.of_time_bookmark(inherited) is MarkStanding.BEFORE_THIS_BRANCH


def test_a_mark_the_run_has_passed_does_not_read_as_still_reachable() -> None:
    """Test the defect that `PL-3K9B` names, at the comparison that caused it.

    `STILL_RUNNING` says that the run can still reach the mark. A clock only
    increases, so an instant at or behind it can never be reached again, whatever
    put the clock there. Both halves are asserted, because the failure was a row
    that showed the wrong one of the two standings, not a row that showed
    nothing.
    """

    at_the_fork = TimeBookmark(CaseInstant(300))
    behind_the_clock = TimeBookmark(CaseInstant(120))
    marks = BookmarkSet().with_time_bookmark(at_the_fork).with_time_bookmark(behind_the_clock)

    standings = _standings(marks, elapsed_s=300)

    assert standings.of_time_bookmark(at_the_fork) is MarkStanding.PASSED
    assert standings.of_time_bookmark(at_the_fork) is not MarkStanding.STILL_RUNNING
    assert standings.of_time_bookmark(behind_the_clock) is MarkStanding.PASSED
    assert standings.of_time_bookmark(behind_the_clock) is not MarkStanding.STILL_RUNNING


def test_a_bookmark_at_a_branch_s_own_fork_instant_reads_passed() -> None:
    """Case A: the branch opens exactly at the mark, so no step it takes can cross the mark.

    `TimeBookmark.crossed_between` needs `before_s < instant_s`, and the branch's
    first `before_s` is the fork itself. So the halt set can never acquire this
    instant, however long the branch runs. The clock comparison is what decides
    this standing.
    """

    at_the_fork = TimeBookmark(CaseInstant(300))
    marks = BookmarkSet().with_time_bookmark(at_the_fork)

    standings = _standings(marks, opened_at_s=300, elapsed_s=300)

    assert standings.of_time_bookmark(at_the_fork) is MarkStanding.PASSED


def test_a_bookmark_at_the_case_s_opening_reads_passed_on_an_ordinary_trunk() -> None:
    """The same arithmetic with no branch in it at all.

    `crossed_between` needs `before_s < 0`, and no run's clock is negative. So
    a mark at induction could never enter the halt set either. It is a strange
    thing to mark, but not an impossible one.
    """

    induction = TimeBookmark(CaseInstant(0))
    marks = BookmarkSet().with_time_bookmark(induction)

    assert _standings(marks, elapsed_s=60).of_time_bookmark(induction) is MarkStanding.PASSED


def test_a_clock_standing_before_its_own_run_s_opening_is_refused() -> None:
    """The standings are refused rather than placing every row against a run that does not exist.

    The opening and the clock are one run's own numbers. If they are crossed
    over, they must come from two different runs. Clamping would give a
    plausible result, and the safety-critical standard prefers an obvious
    failure to that outcome.
    """

    marks = BookmarkSet().with_time_bookmark(TimeBookmark(CaseInstant(120)))

    with pytest.raises(SimulationConfigurationError, match="at or after its own beginning"):
        _standings(marks, opened_at_s=300, elapsed_s=299)


def test_a_bookmark_at_the_end_of_the_run_length_waits_for_the_run_to_get_there() -> None:
    """The far end is markable and reachable, so nothing about it is decided early.

    A mark past the span was once given `NOT_REACHED_WITHIN_CAP` immediately, so
    that a learner was not left waiting out a simulated day for it. Since
    `PL-CN5S`, no such mark can be made, because the `CaseInstant` it would be
    built from is refused. So the mark left at the edge is the span's own end,
    which a run reaches and crosses like any other mark.
    """

    at_the_end = TimeBookmark(CaseInstant(MAXIMUM_ELAPSED_SIMULATION_TIME_S))
    marks = BookmarkSet().with_time_bookmark(at_the_end)
    at_the_cap = _standings(marks, stopped_at_cap=True, elapsed_s=MAXIMUM_ELAPSED_SIMULATION_TIME_S)

    assert _standings(marks).of_time_bookmark(at_the_end) is MarkStanding.STILL_RUNNING
    assert at_the_cap.of_time_bookmark(at_the_end) is MarkStanding.PASSED


def test_a_standing_asked_for_a_mark_that_was_never_evaluated_is_refused() -> None:
    """The request is refused, because a default would draw a row for a mark nobody evaluated."""

    standings = _standings(BookmarkSet())

    with pytest.raises(SimulationConfigurationError, match="does not hold the MAC target"):
        standings.of_mac_target(_target())

    with pytest.raises(SimulationConfigurationError, match="does not hold the time bookmark"):
        standings.of_time_bookmark(TimeBookmark(CaseInstant(30)))


# ---------------------------------------------------- halting on a crossing
#
# This is the half that has to be run rather than asserted directly. `PL-CTD7`
# claims that the halt lands on the step that crossed, whatever the playback
# multiplier. So these tests drive a real `SimulationController` the way
# `run_view.step_tick` drives one: a burst of steps with nothing serviced
# between them.


def _step_until_halt(run: SimulationController, *, limit: int = 2_000) -> BookmarkCrossing | None:
    """Advance one step at a time until the run halts, or `limit` steps pass.

    Returns:
        The crossing that the run halted on, or `None` if it never halted. It
        returns `None` rather than raising, so that a test can assert that a run
        was *not* stopped.
    """

    for _ in range(limit):
        run.advance()

        if not run.is_running:
            return run.snapshot().bookmark_halt

    return None


def _tick_until_halt(
    run: SimulationController, *, steps_per_tick: int, limit: int = 2_000
) -> BookmarkCrossing | None:
    """Advance in whole bursts, the way a tick at `multiplier ×` does, until the run halts.

    Nothing is read between the steps of a burst. That is exactly the condition
    that made per-frame detection overshoot: the run is asked whether it is still
    running only after the burst has finished.
    """

    for _ in range(0, limit, steps_per_tick):
        for _ in range(steps_per_tick):
            run.advance()

        if not run.is_running:
            return run.snapshot().bookmark_halt

    return None


def _alveolar_mac_multiple_after(*, steps: int) -> MacMultiple:
    """Return the alveolar reading after `steps` steps of an unmarked default run.

    The run is a fresh one, so the reading does not come from the run that a
    test goes on to mark. A step stores one state, and the readout, a halt
    and a branch all read it (`PL-MH9J`).
    """

    run = SimulationController()
    run.start()

    for _ in range(steps):
        run.advance()

    return _alveolar_mac_multiple(run)


def _alveolar_mac_multiple(run: SimulationController) -> MacMultiple:
    """Return what the alveolar readout beside the target would show, in the target's unit."""

    snapshot = run.snapshot()

    return mac_multiple(snapshot.alveolar_partial_pressure_fraction, snapshot.agent_mac_percent)


def test_a_target_halts_on_every_crossing_in_either_direction() -> None:
    """Rising through 0.5 ×MAC and falling back through it stops the run twice.

    This follows the decision of 2026-09-20: a target carries no crossing
    direction. So a case that passes through a marked height on the way up, and
    again on the way down, has reached what the learner marked both times.
    Halting only once would make `MacTarget`'s own docstring false for the second
    crossing.
    """

    target = MacTarget(RecordedQuantity.ALVEOLAR, MacMultiple(0.5))
    run = SimulationController()
    run.add_mac_target(target)

    run.start()
    rising = _step_until_halt(run)

    assert rising is not None
    assert rising.mac_targets == (target,)

    # Turn the vaporizer off, so that the same height is crossed again coming down.
    run.set_delivered_concentration_percent(Percent(0.0))
    run.start()
    falling = _step_until_halt(run)

    assert falling is not None
    assert falling.mac_targets == (target,)
    assert falling.instant_s > rising.instant_s


def test_a_halt_lands_on_the_same_step_at_1x_and_at_300x() -> None:
    """The whole claim of `PL-CTD7`: the playback rate does not move the halt.

    A crossing tested once per rendered frame would land up to a tick's burst
    of steps late, which is 30 simulated seconds at 300×. The two
    runs below would then stop at different concentrations from one another,
    while both claimed to have stopped at 0.5 ×MAC.
    """

    target = MacTarget(RecordedQuantity.ALVEOLAR, MacMultiple(0.5))

    real_time = SimulationController()
    real_time.add_mac_target(target)
    real_time.start()
    at_1x = _step_until_halt(real_time)

    fast = SimulationController()
    fast.add_mac_target(target)
    fast.start()
    at_300x = _tick_until_halt(fast, steps_per_tick=STEPS_PER_TICK_AT_300X)

    assert at_1x is not None
    assert at_1x == at_300x
    assert _alveolar_mac_multiple(real_time) == _alveolar_mac_multiple(fast)


def test_a_halt_leaves_the_run_paused_on_the_crossing_step() -> None:
    """A halt pauses the run, so a control change made then acts where the learner was looking.

    A setting changed while the run plays first takes effect at a tick boundary
    (`PL-NBWP`). At 300× that is up to 30 simulated seconds after the value on
    screen. No step is taken while the run is paused. So a halt that pauses makes
    the pause, change and resume route automatic, rather than something the
    learner has to know.
    """

    target = MacTarget(RecordedQuantity.ALVEOLAR, MacMultiple(0.5))
    run = SimulationController()
    run.add_mac_target(target)
    run.start()

    halt = _tick_until_halt(run, steps_per_tick=STEPS_PER_TICK_AT_300X)
    snapshot = run.snapshot()

    assert halt is not None
    assert not snapshot.is_running
    assert snapshot.elapsed_s == halt.instant_s
    # The halt is neither a failure nor the end of the supported domain. It is an ordinary pause.
    assert snapshot.failure_reason is None
    assert snapshot.supported_limit_reason is None
    assert snapshot.bookmark_standings.of_mac_target(target) is MarkStanding.REACHED


def test_a_run_that_settles_exactly_on_a_target_halts_once_and_then_advances() -> None:
    """In this boundary case the height comes from the run itself, so the run lands on it exactly.

    A rule that also counted a step starting inside the band would report a
    crossing on every step after the run lands, and the run could never be
    advanced past the target at all. The height is a fresh run's reading at
    60 s. A branch opens from the state stored for the second it is taken at,
    so a branch taken at 60 s shows that reading.
    """

    height = _alveolar_mac_multiple_after(steps=60)

    run = SimulationController()
    run.add_mac_target(MacTarget(RecordedQuantity.ALVEOLAR, height))
    run.start()
    halt = _step_until_halt(run)

    assert halt is not None
    assert halt.instant_s == 60
    assert _alveolar_mac_multiple(run.resumed_here()) == height

    run.start()
    assert _step_until_halt(run, limit=60) is None
    assert run.is_running


def test_a_branch_opened_on_a_halting_step_agrees_with_the_trunk() -> None:
    """A trunk and a branch opened on its halting step agree on whether the target was reached.

    Each height is the reading of a fresh run after a whole number of steps,
    so the trunk's reading lands on it exactly at that step. Before `PL-QVBR`
    was fixed, the trunk halted on the reading of its stepped system and a
    branch opened on that step tested it from a second reading, computed by
    formula, which lay about 1e-14 to either side. The branch then showed the
    target as still running. A step now stores one state, and the trunk and
    the branch both read it (`PL-MH9J`). So at every instant the test tries,
    the trunk halts on that step, and the trunk and the branch report the
    same halt and the same standing.
    """

    for steps in range(10, 121, 10):
        target = MacTarget(RecordedQuantity.ALVEOLAR, _alveolar_mac_multiple_after(steps=steps))
        trunk = SimulationController()
        trunk.add_mac_target(target)
        trunk.start()
        halt = _step_until_halt(trunk, limit=steps + 5)

        assert halt is not None
        assert halt.instant_s == steps
        assert halt.mac_targets == (target,)

        branch = trunk.resumed_here()

        assert branch.snapshot().bookmark_halt == halt
        assert branch.bookmark_standings().of_mac_target(target) is MarkStanding.REACHED

        assert trunk.bookmark_standings().of_mac_target(target) is MarkStanding.REACHED


def test_a_target_marked_at_a_paused_run_s_reading_does_not_halt_it_on_the_next_step() -> None:
    """A target added at the reading where a paused run stands is reached once, there.

    The lifecycle review of `PL-ZR49`'s change found this case (`PL-QVBR`).
    The run then had two readings of the step it stood on, and the one a halt
    was first tested from lay one unit in the last place below the one that
    showed the target as reached. After Start, the run crossed the height
    again on the next step and halted on the same target twice. A step now
    has one reading (`PL-MH9J`). The test pauses on the rising curve at 69 s,
    the first second at which the old two readings differed that way.
    """

    run = SimulationController()
    run.start()

    for _ in range(69):
        run.advance()

    run.pause()

    target = MacTarget(RecordedQuantity.ALVEOLAR, _alveolar_mac_multiple(run))
    run.add_mac_target(target)

    assert run.bookmark_standings().of_mac_target(target) is MarkStanding.REACHED

    run.start()

    assert _step_until_halt(run, limit=2) is None
    assert run.bookmark_standings().of_mac_target(target) is MarkStanding.REACHED


def test_a_compartment_that_settles_on_a_target_halts_once() -> None:
    """A circuit that settles on its target halts once, and not again while it stays there.

    With no ventilation the patient takes up nothing, so the circuit settles
    on the delivered 2% of sevoflurane, which is 1.00 ×MAC. When the halt test
    compared the readings with the exact height, this run halted at the
    target 965 times in ten minutes, at the 0.1 s step that a run then
    took (`PL-QVBR`, 2026-11-01). The reading moved by one unit in the last
    place from step to step. A target's height is a narrow band
    (`HEIGHT_BAND` in `core/rounding.py`), so a reading that rounding moves
    back and forth inside the band crosses nothing.
    """

    target = MacTarget(RecordedQuantity.CIRCUIT, MacMultiple(1.0))
    run = SimulationController(
        alveolar_ventilation_l_min=AlveolarVentilation(0.0),
        delivered_concentration_percent=Percent(2.0),
    )
    run.add_mac_target(target)
    run.start()

    halt = _step_until_halt(run, limit=3_000)

    assert halt is not None
    assert halt.mac_targets == (target,)

    run.start()

    assert _step_until_halt(run, limit=600) is None
    assert run.bookmark_standings().of_mac_target(target) is MarkStanding.REACHED


def test_a_halt_target_removed_and_added_back_is_named_again_by_both_records() -> None:
    """The halt record and the target's row agree after the target is removed and added back.

    The run halts on a height that a stepped reading lands on exactly.
    Removing the target drops its key from the standings, and the target
    added back is a new mark. Both records test the new mark against the step
    the run stands on, using the canonical readings that decided the halt
    (`PL-QVBR`). So both records name it again, and so does a branch taken
    there. Before `PL-XV0D`'s fix, the halt record kept the old key, so the
    trunk could report stopping on a target that its own row listed as not
    reached.
    """

    measuring = SimulationController()
    measuring.start()

    for _ in range(60):
        measuring.advance()

    target = MacTarget(RecordedQuantity.ALVEOLAR, _alveolar_mac_multiple(measuring))
    run = SimulationController()
    run.add_mac_target(target)
    run.start()

    halt = _step_until_halt(run)

    assert halt is not None
    assert halt.mac_targets == (target,)

    run.remove_mac_target(target)

    assert run.snapshot().bookmark_halt is None

    run.add_mac_target(target)

    assert run.bookmark_standings().of_mac_target(target) is MarkStanding.REACHED
    assert run.snapshot().bookmark_halt == halt
    assert run.here_fork_point is not None
    assert run.here_fork_point.stopped_on_mark
    assert run.resumed_here().snapshot().bookmark_halt == halt


def test_a_time_bookmark_halts_the_run_on_the_step_that_reaches_it() -> None:
    run = SimulationController()
    run.add_time_bookmark(TimeBookmark(CaseInstant(30)))
    run.start()

    halt = _tick_until_halt(run, steps_per_tick=STEPS_PER_TICK_AT_300X)

    assert halt == BookmarkCrossing(CaseInstant(30), (TimeBookmark(CaseInstant(30)),))
    assert run.snapshot().elapsed_s == 30


def test_an_unmarked_run_takes_the_same_trajectory_as_one_that_halted() -> None:
    """Detection observes the run and does not change it.

    The marked run is stepped to the same instant through a halt and a resume,
    and it has to end where the unmarked run ends. `CLAUDE.md` requires
    deterministic results for identical inputs, and a halt is not an input.
    """

    marked = SimulationController()
    marked.add_time_bookmark(TimeBookmark(CaseInstant(30)))
    marked.start()

    for _ in range(60):
        marked.advance()

        if not marked.is_running:
            marked.start()

    unmarked = SimulationController()
    unmarked.start()

    for _ in range(60):
        unmarked.advance()

    assert marked.snapshot().elapsed_s == unmarked.snapshot().elapsed_s
    assert _alveolar_mac_multiple(marked) == _alveolar_mac_multiple(unmarked)


def test_resetting_forgets_what_the_run_did_with_the_marks_and_keeps_the_marks() -> None:
    bookmark = TimeBookmark(CaseInstant(30))
    run = SimulationController()
    run.add_time_bookmark(bookmark)
    run.start()
    _step_until_halt(run)

    run.reset()
    snapshot = run.snapshot()

    assert snapshot.bookmarks.time_bookmarks == (bookmark,)
    assert snapshot.bookmark_halt is None
    assert snapshot.bookmark_standings.of_time_bookmark(bookmark) is MarkStanding.STILL_RUNNING


def test_unmarking_the_instant_a_run_is_halted_on_clears_the_halt() -> None:
    """A halt naming a row nobody can see is stale state rather than a record."""

    bookmark = TimeBookmark(CaseInstant(30))
    run = SimulationController()
    run.add_time_bookmark(bookmark)
    run.start()

    assert _step_until_halt(run) is not None

    run.remove_time_bookmark(bookmark)

    assert run.snapshot().bookmark_halt is None


def test_removing_a_mark_that_is_not_there_is_refused_in_the_panels_words() -> None:
    """The refusal gives the instant as the marks panel writes it (`PL-3JTH`).

    The expected text is written out by hand: 60 s is "1m" in the panel.
    """

    with pytest.raises(SimulationConfigurationError) as refusal:
        BookmarkSet().without_time_bookmark(TimeBookmark(CaseInstant(60)))

    assert str(refusal.value) == "no time bookmark stands at 1m, so there is none to remove"


@pytest.mark.parametrize(
    ("position", "expected"), [(0, [5, 1, 2, 3]), (2, [1, 2, 5, 3]), (9, [1, 2, 3, 5])]
)
def test_a_mark_put_back_lands_at_its_position_or_at_the_end(
    position: int, expected: list[int]
) -> None:
    """`PL-5GX4`: an undone removal puts the mark back in its row, among three others."""

    held = BookmarkSet(
        tuple(TimeBookmark(CaseInstant(60 * n)) for n in (1, 2, 3)),
        tuple(_target(multiple=0.1 * n) for n in (1, 2, 3)),
    )
    times = held.with_time_bookmark_at(position, TimeBookmark(CaseInstant(300)))
    targets = held.with_mac_target_at(position, _target(multiple=0.5))

    assert [int(mark.instant_s) // 60 for mark in times.time_bookmarks] == expected
    assert [round(float(mark.mac_multiple) * 10) for mark in targets.mac_targets] == expected
    assert times.mac_targets == held.mac_targets
    assert targets.time_bookmarks == held.time_bookmarks


def test_a_mark_is_not_put_back_at_a_negative_position() -> None:
    """A negative index would count from the end and land the mark in the wrong row."""

    with pytest.raises(ValueError, match="not -1"):
        BookmarkSet().with_time_bookmark_at(-1, TimeBookmark(CaseInstant(60)))

    with pytest.raises(ValueError, match="not -1"):
        BookmarkSet().with_mac_target_at(-1, _target())


def test_a_mark_put_back_where_it_is_already_held_is_refused() -> None:
    held = BookmarkSet((TimeBookmark(CaseInstant(60)),), (_target(),))

    with pytest.raises(SimulationConfigurationError):
        held.with_time_bookmark_at(0, TimeBookmark(CaseInstant(60), "again"))

    with pytest.raises(SimulationConfigurationError):
        held.with_mac_target_at(0, _target(label="again"))
