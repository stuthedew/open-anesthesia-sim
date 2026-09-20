"""What a mark refuses, and what the two collections hold apart.

`app/bookmarks.py` decides nothing about a run: it decides what a learner is
allowed to have *asked*. So the claims here are all about the boundary — which
values are refused and with what message — and about the collections keeping
the two kinds separable, which is the property `PL-LPLD` was scoped on.

Detection is `PL-CTD7` and has no test here, because nothing in that module
compares a mark against a state. A test asserting a crossing would pass against
an empty implementation and would say nothing about either item.
"""

import math

import pytest

from anesthesia_sim.app.bookmarks import BookmarkSet, MacTarget, TimeBookmark
from anesthesia_sim.app.run_series import COMPARTMENT_QUANTITIES, RecordedQuantity
from anesthesia_sim.core.concentration import MacMultiple
from anesthesia_sim.core.exceptions import SimulationConfigurationError


def _target(
    quantity: RecordedQuantity = RecordedQuantity.VESSEL_RICH,
    multiple: float = 0.8,
    label: str | None = None,
) -> MacTarget:
    """A MAC target, so a test states only the field it is about."""

    return MacTarget(quantity, MacMultiple(multiple), label)


# ------------------------------------------------------------ time bookmarks


def test_a_time_bookmark_holds_its_instant_and_no_name_by_default() -> None:
    bookmark = TimeBookmark(600.0)

    assert bookmark.instant_s == 600.0
    assert bookmark.label is None


def test_a_time_bookmark_keeps_the_name_it_was_given_without_surrounding_space() -> None:
    assert TimeBookmark(600.0, "  intubation  ").label == "intubation"


def test_a_time_bookmark_before_the_case_opened_is_refused() -> None:
    with pytest.raises(SimulationConfigurationError, match="opening at 0 s"):
        TimeBookmark(-1.0)


@pytest.mark.parametrize("instant_s", [math.inf, -math.inf, math.nan])
def test_a_time_bookmark_at_an_instant_no_clock_reaches_is_refused(instant_s: float) -> None:
    with pytest.raises(SimulationConfigurationError, match="finite instant"):
        TimeBookmark(instant_s)


def test_the_case_opening_itself_is_a_markable_instant() -> None:
    assert TimeBookmark(0.0).instant_s == 0.0


def test_a_blank_name_is_refused_rather_than_read_as_no_name() -> None:
    # An empty row in a list is indistinguishable from a rendering failure,
    # and `None` already means "list it under its own value".
    with pytest.raises(SimulationConfigurationError, match="blank"):
        TimeBookmark(600.0, "   ")


def test_no_mark_of_either_kind_carries_a_crossing_direction() -> None:
    # The scope floor took one from the reference simulator and the project
    # owner removed it on 2026-09-20: a height is a height, and a run that
    # passes through it going up and again coming down has reached what was
    # marked both times.
    assert not hasattr(TimeBookmark(600.0), "direction")
    assert not hasattr(_target(), "direction")


# --------------------------------------------------------------- MAC targets


def test_a_mac_target_names_the_compartment_it_is_read_against() -> None:
    target = _target(RecordedQuantity.MUSCLE)

    assert target.quantity is RecordedQuantity.MUSCLE
    assert target.mac_multiple == 0.8


@pytest.mark.parametrize("quantity", COMPARTMENT_QUANTITIES)
def test_every_drawn_compartment_may_carry_a_target(quantity: RecordedQuantity) -> None:
    # The scope floor is the six graphed compartments rather than the alveolar
    # trace alone (`PL-LPLD`), so this is the whole of what a picker may offer.
    assert _target(quantity).quantity is quantity


def test_the_wash_in_ratio_may_not_carry_a_target() -> None:
    # It is a quotient of two compartments rather than a concentration, so a
    # multiple of MAC of it is not a quantity the model holds - and it is the
    # one member of `RecordedQuantity` a compartment picker could offer by
    # mistake.
    with pytest.raises(SimulationConfigurationError, match="not one of"):
        _target(RecordedQuantity.WASH_IN_RATIO)


@pytest.mark.parametrize("multiple", [0.0, -0.5, math.inf, math.nan])
def test_a_target_at_a_height_no_compartment_can_cross_is_refused(multiple: float) -> None:
    # Zero goes with the negatives: a compartment opens at zero, so every run
    # would stand on such a target before it began.
    with pytest.raises(SimulationConfigurationError, match="height above zero"):
        _target(multiple=multiple)


def test_a_target_refusal_names_the_height_that_failed() -> None:
    # `.claude/rules/sources-and-docstrings.md`: a refusal names what was
    # refused, so a rejected setting stays traceable to the input behind it.
    with pytest.raises(SimulationConfigurationError, match=r"-0\.5"):
        _target(multiple=-0.5)


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
    marks = BookmarkSet().with_time_bookmark(TimeBookmark(600.0)).with_mac_target(_target())

    assert marks.time_bookmarks == (TimeBookmark(600.0),)
    assert marks.mac_targets == (_target(),)
    assert not marks.is_empty


def test_adding_a_mark_leaves_the_set_it_was_added_to_alone() -> None:
    before = BookmarkSet()
    after = before.with_time_bookmark(TimeBookmark(600.0))

    assert before.time_bookmarks == ()
    assert after.time_bookmarks == (TimeBookmark(600.0),)


def test_marks_are_listed_in_the_order_they_were_added() -> None:
    marks = (
        BookmarkSet()
        .with_time_bookmark(TimeBookmark(600.0))
        .with_time_bookmark(TimeBookmark(120.0))
    )

    assert [bookmark.instant_s for bookmark in marks.time_bookmarks] == [600.0, 120.0]


def test_an_instant_already_marked_may_not_be_marked_again() -> None:
    marks = BookmarkSet().with_time_bookmark(TimeBookmark(600.0))

    with pytest.raises(SimulationConfigurationError, match="marked once"):
        marks.with_time_bookmark(TimeBookmark(600.0, "second thoughts"))


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
    marks = BookmarkSet().with_time_bookmark(TimeBookmark(600.0)).with_mac_target(_target())
    after = marks.without_time_bookmark(TimeBookmark(600.0))

    assert after.time_bookmarks == ()
    assert after.mac_targets == (_target(),)


def test_a_time_bookmark_is_removed_by_its_instant_rather_than_by_its_name() -> None:
    marks = BookmarkSet().with_time_bookmark(TimeBookmark(600.0, "intubation"))

    assert marks.without_time_bookmark(TimeBookmark(600.0)).time_bookmarks == ()


def test_a_target_is_removed_by_its_crossing_rather_than_by_its_name() -> None:
    marks = BookmarkSet().with_mac_target(_target(label="wash-in"))

    assert marks.without_mac_target(_target()).mac_targets == ()


def test_removing_a_time_bookmark_that_is_not_there_is_refused() -> None:
    # Removing nothing silently would leave a panel reporting a deletion that
    # did not happen.
    with pytest.raises(SimulationConfigurationError, match="none to remove"):
        BookmarkSet().without_time_bookmark(TimeBookmark(600.0))


def test_removing_a_target_that_is_not_there_is_refused() -> None:
    with pytest.raises(SimulationConfigurationError, match="none to remove"):
        BookmarkSet().without_mac_target(_target())


def test_a_removal_refusal_names_the_crossing_it_could_not_find() -> None:
    with pytest.raises(SimulationConfigurationError, match="vessel_rich"):
        BookmarkSet().without_mac_target(_target())


def test_a_set_built_directly_from_repeated_marks_is_refused_too() -> None:
    # The invariant is the collection's rather than the adder's, so a caller
    # constructing one cannot get round it.
    with pytest.raises(SimulationConfigurationError, match="marked once"):
        BookmarkSet((TimeBookmark(600.0), TimeBookmark(600.0)))
