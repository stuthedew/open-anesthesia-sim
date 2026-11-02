"""Unit tests for `layout/sizing.py`, which sizes layouts and finds Areas too small for a View.

`PL-K285` decided that a View's minimum size is a constraint (Q1). It also
decided that an Area which the layout cannot give that size says so, rather
than being clipped or collapsed (Q2, Q3). `PL-30L5` Q2 allows a split whose
halves are too small for their View, and the halves then say that they are
too small. Every expected size below is worked out by hand in the comment
beside it. Each comes from the fractions, the handle width and the rounding
that `pixel_sizes` documents, and none is read back from the function under
test.
"""

import inspect
from collections.abc import Mapping

import pytest

from anesthesia_sim.layout.exceptions import InvalidLayout
from anesthesia_sim.layout.model import LayoutModel
from anesthesia_sim.layout.shipped import shipped_workspace
from anesthesia_sim.layout.sizing import (
    Floor,
    PixelSize,
    TooSmall,
    apportion,
    border_range,
    border_share,
    drawn_bounds,
    minimum_extent,
    pixel_sizes,
    settle,
    split_sizes,
)
from anesthesia_sim.layout.tree import Area, AreaId, Orientation, Split, ViewKind, areas_in
from anesthesia_sim.layout.workspace import ShippedWorkspaceId

_HANDLE_PX = 8
_CHART = ViewKind("chart")
_PANEL = ViewKind("panel")


def _row(sizes: tuple[float, ...], *children: Area | Split) -> Split:
    return Split(Orientation.ROW, sizes, children)


def _column(sizes: tuple[float, ...], *children: Area | Split) -> Split:
    return Split(Orientation.COLUMN, sizes, children)


def _area(number: int, view: ViewKind = _CHART) -> Area:
    return Area(AreaId(number), view)


def _fixed(floors: Mapping[AreaId, PixelSize]) -> dict[AreaId, Floor]:
    """Return a floor for each Area that is its size in `floors` at every width."""

    return {area_id: Floor.fixed(size) for area_id, size in floors.items()}


def _each(tree: Area | Split, size: PixelSize) -> dict[AreaId, PixelSize]:
    return {area.id: size for area in areas_in(tree)}


def test_pixel_sizes_round_down_and_give_the_left_over_pixels_to_the_largest_losses() -> None:
    # 0.5, 0.3 and 0.2 of 984 are 492, 295.2 and 196.8. Rounded down they sum
    # to 983, and the one pixel left goes to 196.8, which lost the most.
    assert pixel_sizes((0.5, 0.3, 0.2), 984) == (492, 295, 197)


def test_a_split_no_bound_holds_is_laid_out_exactly_by_its_fractions() -> None:
    tree = _row((0.5, 0.3, 0.2), _area(1), _area(2), _area(3))
    laid_out = apportion(tree, PixelSize(1000, 600), _HANDLE_PX, _each(tree, PixelSize(10, 10)))

    # 1000 px minus two 8 px handles leaves 984, which is shared as in the test above.
    assert laid_out.splits[()] == (492, 295, 197)
    assert laid_out.areas == {
        AreaId(1): PixelSize(492, 600),
        AreaId(2): PixelSize(295, 600),
        AreaId(3): PixelSize(197, 600),
    }
    assert laid_out.unheld == ()


def test_an_area_whose_share_is_below_its_need_is_held_at_it_and_its_neighbour_gives_way() -> None:
    # This is the dashboard's shape in a 1200 px window. The accounting Area's
    # share is 0.18 of the 1192 px left after the handle, which would be
    # 214.56 px. That is less than the Area's need of 260.
    tree = _row((0.82, 0.18), _area(1), _area(2, _PANEL))
    bounds = {AreaId(1): PixelSize(400, 100), AreaId(2): PixelSize(260, 100)}
    laid_out = apportion(tree, PixelSize(1200, 500), _HANDLE_PX, bounds)

    # Area 2 is held at 260, and Area 1 takes the other 1192 - 260 = 932.
    assert laid_out.splits[()] == (932, 260)
    assert laid_out.unheld == ()


def test_a_split_whose_children_need_more_than_it_has_is_laid_out_by_its_fractions() -> None:
    tree = _row((0.5, 0.5), _area(1), _area(2))
    laid_out = apportion(tree, PixelSize(508, 300), _HANDLE_PX, _each(tree, PixelSize(300, 100)))

    # Two 300 px needs are more than the 500 px left after the handle, so the
    # fractions decide: 250 each, and the split is reported as not held.
    assert laid_out.splits[()] == (250, 250)
    assert laid_out.unheld == ((),)


def test_a_child_too_tall_for_its_row_leaves_the_row_unheld() -> None:
    tree = _row((0.5, 0.5), _area(1), _area(2))
    bounds = {AreaId(1): PixelSize(10, 10), AreaId(2): PixelSize(10, 400)}

    assert apportion(tree, PixelSize(600, 300), _HANDLE_PX, bounds).unheld == ((),)


def test_minimum_extent_sums_along_each_split_and_takes_the_largest_across_it() -> None:
    # A row that holds a column (of Areas 1 and 3) and Area 2.
    tree = _row((0.82, 0.18), _column((0.56, 0.44), _area(1), _area(3)), _area(2, _PANEL))
    bounds = {
        AreaId(1): PixelSize(438, 585),
        AreaId(3): PixelSize(309, 361),
        AreaId(2): PixelSize(228, 224),
    }

    # The column is max(438, 309) = 438 wide and 585 + 8 + 361 = 954 tall.
    # The row is 438 + 8 + 228 = 674 wide and max(954, 224) = 954 tall.
    assert minimum_extent(tree, _HANDLE_PX, bounds) == PixelSize(674, 954)


def test_settle_draws_every_area_the_extent_can_give_its_need() -> None:
    tree = _row((0.82, 0.18), _area(1), _area(2, _PANEL))
    needs = {AreaId(1): PixelSize(400, 100), AreaId(2): PixelSize(260, 100)}
    floors = _each(tree, PixelSize(40, 30))
    fit = settle(tree, PixelSize(1200, 500), _HANDLE_PX, needs, _fixed(floors), kept=frozenset())

    assert fit.drawn == {AreaId(1), AreaId(2)}
    assert fit.too_small == ()
    assert fit.bounds == needs
    assert fit.apportionment.splits[()] == (932, 260)


def test_a_split_whose_halves_the_extent_cannot_hold_leaves_a_half_too_small() -> None:
    # Area 2 of a two-Area row was split in two, so Area 4 is new. Three
    # 400 px needs are more than the 1008 - 2 * 8 = 992 px that the row has.
    tree = _row((0.5, 0.25, 0.25), _area(1), _area(2), _area(4))
    needs = _each(tree, PixelSize(400, 100))
    floors = _each(tree, PixelSize(40, 30))
    fit = settle(tree, PixelSize(1008, 300), _HANDLE_PX, needs, _fixed(floors), kept={AreaId(1)})

    # One of the split's new halves drops to its floor before Area 1 does,
    # because the split did not touch Area 1. Dropping one half is enough,
    # since 400 + 400 + 40 = 840 fits in 992. The halves have equal shares, so
    # the later one, Area 4, drops. Area 2's share of 248 is less than 400, so
    # Area 2 is held at 400. Area 1's share of what is left, 0.5 / 0.75 of 592,
    # is 394.67. That is also less than 400, so Area 1 is held too. Area 4
    # takes the other 992 - 800 = 192.
    assert fit.apportionment.splits[()] == (400, 400, 192)
    assert fit.drawn == {AreaId(1), AreaId(2)}
    assert fit.too_small == (TooSmall(AreaId(4), PixelSize(400, 100), PixelSize(192, 300)),)
    assert fit.bounds == {
        AreaId(1): PixelSize(400, 100),
        AreaId(2): PixelSize(400, 100),
        AreaId(4): PixelSize(40, 30),
    }


def test_a_split_whose_halves_the_extent_can_hold_takes_their_room_from_the_neighbour() -> None:
    tree = _row((0.5, 0.25, 0.25), _area(1), _area(2), _area(4))
    needs = _each(tree, PixelSize(300, 100))
    floors = _each(tree, PixelSize(40, 30))
    fit = settle(tree, PixelSize(1008, 300), _HANDLE_PX, needs, _fixed(floors), kept={AreaId(1)})

    # 248 is less than 300, so both halves are held at 300. Area 1 takes the
    # other 992 - 600 = 392, which is still more than its own 300.
    assert fit.apportionment.splits[()] == (392, 300, 300)
    assert fit.drawn == {AreaId(1), AreaId(2), AreaId(4)}


def test_kept_areas_are_let_go_only_once_the_others_are_at_their_floors() -> None:
    tree = _row((0.5, 0.5), _area(1), _area(2))
    needs = _each(tree, PixelSize(300, 100))
    floors = _each(tree, PixelSize(40, 30))
    fit = settle(tree, PixelSize(408, 300), _HANDLE_PX, needs, _fixed(floors), kept={AreaId(1)})

    # Two 300 px needs are more than the 400 px that the row has. The change
    # did not leave Area 2 in place, so Area 2 is let go to its 40 px floor.
    # That leaves room to hold Area 1 at its need. Area 1 gets 300, and Area 2
    # gets the other 100.
    assert fit.apportionment.splits[()] == (300, 100)
    assert fit.drawn == {AreaId(1)}

    narrower = settle(
        tree, PixelSize(208, 300), _HANDLE_PX, needs, _fixed(floors), kept={AreaId(1)}
    )

    # At 200 px no Area can be held at a 300 px need. So Area 1 is let go too,
    # and the fractions give each Area 100.
    assert narrower.apportionment.splits[()] == (100, 100)
    assert narrower.drawn == frozenset()
    assert {entry.area_id for entry in narrower.too_small} == {AreaId(1), AreaId(2)}


def test_a_too_small_area_is_drawn_again_once_the_extent_can_give_it_its_need() -> None:
    tree = _row((0.5, 0.25, 0.25), _area(1), _area(2), _area(4))
    needs = _each(tree, PixelSize(400, 100))
    floors = _each(tree, PixelSize(40, 30))
    small = settle(tree, PixelSize(1008, 300), _HANDLE_PX, needs, _fixed(floors), kept={AreaId(1)})
    wider = settle(tree, PixelSize(1616, 300), _HANDLE_PX, needs, _fixed(floors), kept=small.drawn)

    # 1616 - 16 = 1600 px is room for three 400 px needs, because 0.25 of 1600 is exactly 400.
    assert wider.apportionment.splits[()] == (800, 400, 400)
    assert wider.drawn == {AreaId(1), AreaId(2), AreaId(4)}
    assert wider.too_small == ()


def test_a_shipped_workspace_on_a_small_extent_names_its_too_small_areas_and_none_has_no_size() -> (
    None
):
    model = shipped_workspace(ShippedWorkspaceId("induction")).layout
    tree = model.windows[0].tree
    # The induction Workspace is a row(0.75, 0.25) with two children: a
    # column(0.6, 0.4) of Areas 1 and 2, and Area 3. Each Area needs 300 by 300.
    needs = _each(tree, PixelSize(300, 300))
    floors = _each(tree, PixelSize(60, 40))
    fit = settle(tree, PixelSize(508, 408), _HANDLE_PX, needs, _fixed(floors), kept=frozenset())

    # The Areas need 300 + 8 + 300 = 608 px of width and 608 px of height. The
    # window has only 508 by 408 px, so it is 100 px short across and 200 px
    # short down, 300 px in all. No single drop clears both. Dropping Area 1 or
    # Area 2 shortens the column to 300 + 8 + 40 = 348 but leaves the width, and
    # dropping Area 3 leaves the height. Each pair of Areas clears both. Areas 2
    # and 3 have the smallest share of the pairs, 0.75 * 0.4 + 0.25 = 0.55,
    # against 0.7 for Areas 1 and 3 and 0.75 for Areas 1 and 2. So Areas 2 and
    # 3 drop.
    #
    # The row's 500 px give 375 and 125, which are at least the column's 300
    # and Area 3's 60. The column's 400 px would give 240 and 160, so Area 1 is
    # held at its 300, and Area 2 takes the other 100.
    assert fit.apportionment.areas == {
        AreaId(1): PixelSize(375, 300),
        AreaId(2): PixelSize(375, 100),
        AreaId(3): PixelSize(125, 408),
    }
    assert fit.drawn == {AreaId(1)}
    assert [entry.area_id for entry in fit.too_small] == [AreaId(2), AreaId(3)]
    assert all(
        size.width_px > 0 and size.height_px > 0 for size in fit.apportionment.areas.values()
    )


def test_settle_releases_only_the_areas_that_must_give_way() -> None:
    """`PL-QZ7Z`: a window a few pixels short blanks only the Areas that must give way."""

    floors_60 = PixelSize(40, 60)

    # Three Areas in a column each need 300 px of height, and the column has
    # 700 px. The needs take 3 * 300 + 2 * 8 = 916 px. Dropping one Area leaves
    # 300 + 300 + 60 + 16 = 676, which fits. Dropping any one Area clears the
    # whole shortfall, so Area 1, which has the smallest share at 0.2, drops.
    column = _column((0.2, 0.4, 0.4), _area(1), _area(2), _area(3))
    every = frozenset(area.id for area in areas_in(column))
    fit = settle(
        column,
        PixelSize(400, 700),
        _HANDLE_PX,
        _each(column, PixelSize(100, 300)),
        _fixed(_each(column, floors_60)),
        kept=every,
    )

    # The column's 684 px would give 136.8, 273.6 and 273.6. Areas 2 and 3 are
    # held at 300, and Area 1 takes the other 84.
    assert fit.apportionment.splits[()] == (84, 300, 300)
    assert fit.drawn == {AreaId(2), AreaId(3)}
    assert [entry.area_id for entry in fit.too_small] == [AreaId(1)]

    # Two halves of a row each need 300 px, and the row has 500 px. The needs
    # take 608. With one half at its 177 px floor, the row needs
    # 300 + 8 + 177 = 485, which fits. The halves' shares are equal, so the
    # later one, Area 2, drops. Area 1 is held at 300 of the 492 px, and Area 2
    # takes 192.
    row = _row((0.5, 0.5), _area(1), _area(2))
    fit = settle(
        row,
        PixelSize(500, 400),
        _HANDLE_PX,
        _each(row, PixelSize(300, 100)),
        _fixed(_each(row, PixelSize(177, 60))),
        kept=frozenset({AreaId(1), AreaId(2)}),
    )

    assert fit.apportionment.splits[()] == (300, 192)
    assert fit.drawn == {AreaId(1)}
    assert [entry.area_id for entry in fit.too_small] == [AreaId(2)]

    # An Area sits above a row of two Areas, and each needs 300 px of height.
    # The column has 590 px, and the needs take 300 + 8 + 300 = 608. Dropping
    # Area 2 or Area 3 alone leaves the row 300 px tall and gains nothing.
    # Dropping Area 1 leaves 60 + 8 + 300 = 368, which fits. So Area 1 drops,
    # whether or not the Areas are in `kept`. The column's 582 px would give
    # 291 each, so the row is held at 300, and Area 1 takes 282.
    stacked = _column((0.5, 0.5), _area(1), _row((0.5, 0.5), _area(2), _area(3)))
    needs = _each(stacked, PixelSize(200, 300))
    floors = _each(stacked, floors_60)

    for kept in (frozenset(), frozenset(area.id for area in areas_in(stacked))):
        fit = settle(stacked, PixelSize(600, 590), _HANDLE_PX, needs, _fixed(floors), kept=kept)

        assert fit.apportionment.splits[()] == (282, 300)
        assert fit.drawn == {AreaId(2), AreaId(3)}
        assert [entry.area_id for entry in fit.too_small] == [AreaId(1)]


def test_a_new_area_whose_drop_gains_nothing_keeps_its_view() -> None:
    # A row of Areas 1 and 2 sits above Area 3, and each Area needs 300 px of
    # height. The column has 590 px, and the needs take 300 + 8 + 300 = 608.
    # Area 1 is new, and Areas 2 and 3 are kept. Dropping Area 1 gains nothing,
    # since Area 2 still holds the row at 300. Dropping Area 2 gains nothing
    # either. Dropping Area 3 alone leaves 300 + 8 + 60 = 368, so Area 3 is the
    # one Area that gives way. The column's 582 px would give 291 each, so the
    # row is held at 300 and Area 3 takes 282.
    stacked = _column((0.5, 0.5), _row((0.5, 0.5), _area(1), _area(2)), _area(3))
    fit = settle(
        stacked,
        PixelSize(600, 590),
        _HANDLE_PX,
        _each(stacked, PixelSize(200, 300)),
        _fixed(_each(stacked, PixelSize(40, 60))),
        kept=frozenset({AreaId(2), AreaId(3)}),
    )

    assert fit.apportionment.splits[()] == (300, 282)
    assert fit.drawn == {AreaId(1), AreaId(2)}
    assert [entry.area_id for entry in fit.too_small] == [AreaId(3)]


def test_where_even_the_floors_do_not_fit_only_the_areas_that_cause_it_give_way() -> None:
    # Area 1 sits beside a column of Areas 2 and 3 in a window 100 px tall.
    # The column's floors alone need 60 + 8 + 60 = 128 px, so the window is
    # 28 px short whatever drops. Dropping both Areas 2 and 3 brings the
    # shortfall down to that 28 px. Dropping only one leaves the column
    # 60 + 8 + 80 = 148 px tall. Area 1 does not need to drop. The row's 992 px
    # would give Area 1 only 99.2, so it is held at its 200 px need, and the
    # column takes the other 792.
    tree = _row((0.1, 0.9), _area(1), _column((0.5, 0.5), _area(2), _area(3)))
    fit = settle(
        tree,
        PixelSize(1000, 100),
        _HANDLE_PX,
        {**_each(tree, PixelSize(300, 80)), AreaId(1): PixelSize(200, 80)},
        _fixed(_each(tree, PixelSize(60, 60))),
        kept=frozenset(),
    )

    assert fit.apportionment.splits[()] == (200, 792)
    assert fit.drawn == {AreaId(1)}
    assert [entry.area_id for entry in fit.too_small] == [AreaId(2), AreaId(3)]


def test_a_tree_too_large_to_weigh_every_subset_drops_one_area_at_a_time() -> None:
    # A row holds eleven Areas. That is one more than the most for which
    # `settle` weighs every subset. The row is 6 px short of the
    # 11 * 100 + 10 * 8 = 1180 px that the needs take. Dropping any one Area is
    # enough, and the shares are equal, so the last Area drops. The other ten
    # are each held at 100 px of the 1094 px, and Area 11 takes the other 94.
    tree = _row((1 / 11,) * 11, *(_area(number) for number in range(1, 12)))
    fit = settle(
        tree,
        PixelSize(1174, 100),
        _HANDLE_PX,
        _each(tree, PixelSize(100, 50)),
        _fixed(_each(tree, PixelSize(40, 30))),
        kept=frozenset(),
    )

    assert fit.apportionment.splits[()] == (100,) * 10 + (94,)
    assert [entry.area_id for entry in fit.too_small] == [AreaId(11)]


def test_drawn_bounds_take_the_larger_of_the_need_and_the_floor_on_each_axis() -> None:
    needs = {AreaId(1): PixelSize(160, 300), AreaId(2): PixelSize(400, 50)}
    floors = {AreaId(1): PixelSize(177, 60), AreaId(2): PixelSize(177, 60)}

    assert drawn_bounds(needs, _fixed(floors)) == {
        AreaId(1): PixelSize(177, 300),
        AreaId(2): PixelSize(400, 60),
    }


def _notice_floor(width_px: int) -> int:
    """Return a floor's height: 150 px below 300 px wide, and 80 px from 300 px."""

    return 150 if width_px < 300 else 80


def test_a_floor_is_computed_only_at_a_width() -> None:
    """`PL-16BG`: no caller can compute a floor without naming the Area's drawn width.

    `AreaLayout._floor` used to default the width to 0, and the check that refuses a split
    relied on that default (`PL-7DXG`). `Floor.at` takes the width as a required argument.
    So a caller that leaves out the width fails mypy, and the call raises an error in this
    test. This test fails if `Floor.at` is given a default width again.
    """

    floor = Floor(100, lambda width_px: _notice_floor(width_px))
    width = inspect.signature(Floor.at).parameters["drawn_width_px"]

    assert width.default is inspect.Parameter.empty

    with pytest.raises(TypeError):
        floor.at()  # type: ignore[call-arg]


def test_a_floor_is_measured_at_the_width_it_is_drawn_at() -> None:
    """A floor's height follows its drawn width, and a width below its own is its own."""

    floor = Floor(100, lambda width_px: _notice_floor(width_px))

    assert floor.at(0) == PixelSize(100, 150)
    assert floor.at(299) == PixelSize(100, 150)
    assert floor.at(300) == PixelSize(100, 80)
    assert Floor.fixed(PixelSize(40, 30)).at(500) == PixelSize(40, 30)
    # A part 400 px wide and 80 px tall holds the floor measured at 400 px. A part
    # 200 px wide and 80 px tall does not, because at 200 px the floor is 150 px.
    assert floor.fits_in(PixelSize(400, 80))
    assert not floor.fits_in(PixelSize(200, 80))
    assert not floor.fits_in(PixelSize(99, 500))


def test_settle_measures_a_too_small_areas_floor_at_the_width_it_draws_the_area() -> None:
    """`PL-9Z74`: a wide too-small Area is held at its lower floor, so a neighbour keeps its View.

    Two Areas are stacked in a window 400 px wide and 308 px tall. The handle between them
    takes 8 px, so the two Areas share 308 - 8 = 300 px of height. Each View needs 300 px of
    width and 200 px of height. Each floor is 100 px wide. Its height is 150 px for an Area
    drawn less than 300 px wide, and 80 px for one drawn 300 px wide or more.

    At the floors' own width, 100 px, both floors are 150 px tall. One Area at its need and
    one at its floor would need 200 + 150 = 350 px, so both drop and both are too small. But
    both are drawn 400 px wide, where each floor is 80 px tall. Then 200 + 80 = 280 px fits
    in the 300 px. The later Area drops to its floor, and the earlier keeps its View. The
    earlier Area is held at its need of 200 px, and the later Area gets the other 100 px.
    """

    tree = _column((0.5, 0.5), _area(1), _area(2))
    needs = _each(tree, PixelSize(300, 200))
    floors = {area_id: Floor(100, lambda width_px: _notice_floor(width_px)) for area_id in needs}
    fit = settle(tree, PixelSize(400, 308), _HANDLE_PX, needs, floors, kept=frozenset())

    assert fit.drawn == {AreaId(1)}
    assert fit.apportionment.splits[()] == (200, 100)
    assert fit.bounds == {AreaId(1): PixelSize(300, 200), AreaId(2): PixelSize(100, 80)}
    assert fit.too_small == (TooSmall(AreaId(2), PixelSize(300, 200), PixelSize(400, 100)),)

    # With each floor fixed at its height at 100 px wide, neither Area keeps its View.
    tallest = _fixed(_each(tree, PixelSize(100, 150)))
    blanked = settle(tree, PixelSize(400, 308), _HANDLE_PX, needs, tallest, kept=frozenset())

    assert blanked.drawn == frozenset()


def test_drawn_bounds_measure_each_floor_at_the_width_of_its_need() -> None:
    """A drawn Area is at least as wide as its need, so its floor is measured at that width.

    Area 1 needs 300 by 60 px. At 300 px wide its floor is 80 px tall, so Area 1 is held
    80 px tall. Area 2 needs 200 by 60 px. At 200 px wide its floor is 150 px tall.
    """

    needs = {AreaId(1): PixelSize(300, 60), AreaId(2): PixelSize(200, 60)}
    floors = {area_id: Floor(100, lambda width_px: _notice_floor(width_px)) for area_id in needs}

    assert drawn_bounds(needs, floors) == {
        AreaId(1): PixelSize(300, 80),
        AreaId(2): PixelSize(200, 150),
    }


def test_a_border_held_by_its_neighbours_need_maps_the_pointer_through_the_drawn_sizes() -> None:
    """`PL-97WX`: the share comes from the drawn sizes, not the fractions."""

    # A row of 800 px is split 0.7 / 0.3, and its right child needs 300. The
    # right child's share, 240, is less than that. So the child is held at 300,
    # and the border is drawn at 500, not at the 560 that 0.7 would give.
    fractions, bounds = (0.7, 0.3), (10, 300)

    assert border_share(fractions, 0, bounds, 800, 500) is None
    # The right child cannot be drawn narrower, so the border cannot move right.
    assert border_share(fractions, 0, bounds, 800, 501) is None
    assert border_share(fractions, 0, bounds, 800, 700) is None

    # With the border one pixel left, at 499, the right child's share is 301.
    # That is more than its bound, so no child is held, and the share is the
    # one that the fractions give, 499 / 800.
    left = border_share(fractions, 0, bounds, 800, 499)
    assert left == 499 / 800
    assert split_sizes((left, 1 - left), bounds, 800) == (499, 301)

    # Toward the middle, the share again follows the pointer exactly.
    assert border_share(fractions, 0, bounds, 800, 400) == 0.5

    # Far to the left, the border stops where the left child reaches its 10 px
    # bound, and the share is the one that draws it there: 10 / 800.
    far = border_share(fractions, 0, bounds, 800, 0)
    assert far == 10 / 800
    assert split_sizes((far, 1 - far), bounds, 800) == (10, 790)


def test_a_border_between_two_unheld_children_maps_the_pointer_by_the_fractions() -> None:
    # Nothing is held, so the border at 0.5 of 800 is drawn at 400, and 480
    # is a share of 480 / 800 = 0.6.
    fractions, bounds = (0.25, 0.25, 0.5), (10, 10, 10)

    assert border_share(fractions, 1, bounds, 800, 400) is None

    moved = border_share(fractions, 1, bounds, 800, 480)
    assert moved == 0.6
    assert moved is not None
    # The first child keeps its 0.25, and only the two beside the border change.
    assert split_sizes((0.25, moved - 0.25, 1 - moved), bounds, 800) == (200, 280, 320)


def test_a_border_ranges_between_the_bounds_of_the_children_beside_it() -> None:
    # A row of 800 px is split 0.7 / 0.3. The left child needs 10 px and the right
    # child 300 px, so the border can be drawn from 10 to 800 - 300 = 500.
    assert border_range((0.7, 0.3), 0, (10, 300), 800) == (10, 500)

    # In a row of three split 0.25 / 0.25 / 0.5, border 1 lies between the middle and
    # the third child. Its range starts where the middle child is held at its 20 px
    # bound. The other two children then share the remaining 780 px by their fractions,
    # 0.25 to 0.5 + 0.25, because the middle child's 0.25 has passed to the third child.
    # So the first child gets 195 px, and the border is drawn at 195 + 20 = 215. The
    # range ends where the third child is held at its 30 px bound, at 800 - 30 = 770.
    assert border_range((0.25, 0.25, 0.5), 1, (10, 20, 30), 800) == (215, 770)


def test_a_border_cannot_move_where_its_childrens_bounds_need_more_than_the_split_has() -> None:
    """`PL-MH5T`: below the bounds, no share moves the border on screen, so none is offered."""

    # Three children need 124 px each, 372 px in all, from a split of 284 px.
    fractions, bounds = (0.4026, 0.4646, 0.1328), (124, 124, 124)

    assert border_range(fractions, 0, bounds, 284) is None
    assert border_range(fractions, 1, bounds, 284) is None
    assert border_share(fractions, 1, bounds, 284, 150) is None
    assert border_share(fractions, 1, bounds, 284, 0) is None


def test_border_range_refuses_a_border_the_split_does_not_have() -> None:
    with pytest.raises(IndexError):
        border_range((0.5, 0.5), 1, (10, 10), 800)


def test_border_share_refuses_a_border_the_split_does_not_have() -> None:
    with pytest.raises(IndexError):
        border_share((0.5, 0.5), 1, (10, 10), 800, 400)


def test_settle_holds_a_floor_above_a_need() -> None:
    model = LayoutModel.single_area(_CHART)
    tree = model.windows[0].tree
    fit = settle(
        tree,
        PixelSize(500, 500),
        _HANDLE_PX,
        {AreaId(1): PixelSize(0, 0)},
        {AreaId(1): Floor.fixed(PixelSize(60, 40))},
        kept=frozenset(),
    )

    assert fit.bounds == {AreaId(1): PixelSize(60, 40)}
    assert fit.drawn == {AreaId(1)}


@pytest.mark.parametrize(
    ("width", "height", "error"),
    [(-1, 0, InvalidLayout), (0, -1, InvalidLayout), (True, 0, TypeError), (1.0, 0, TypeError)],
)
def test_a_pixel_size_refuses_a_negative_or_non_integer_field(
    width: object, height: object, error: type[Exception]
) -> None:
    with pytest.raises(error):
        PixelSize(width, height)  # type: ignore[arg-type]


@pytest.mark.parametrize(("handle", "error"), [(-1, InvalidLayout), (True, TypeError)])
def test_apportion_refuses_a_negative_or_non_integer_handle(
    handle: object, error: type[Exception]
) -> None:
    tree = _row((0.5, 0.5), _area(1), _area(2))

    with pytest.raises(error):
        apportion(tree, PixelSize(100, 100), handle, _each(tree, PixelSize(1, 1)))  # type: ignore[arg-type]
