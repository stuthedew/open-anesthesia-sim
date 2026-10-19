"""Unit tests for `layout/sizing.py`: a layout in pixels, and the Areas too small for a View.

`PL-K285` decided that a View's minimum size is a constraint (Q1) and that an
Area the layout cannot give that size states it rather than being clipped or
collapsed (Q2, Q3). `PL-30L5` Q2 has a split whose halves are too small for
their View allowed, the halves then stating it. Every expected size below is
worked out by hand in the comment beside it, from the fractions, the handle
width and the rounding `pixel_sizes` documents, and never read back from the
function under test.
"""

import pytest

from anesthesia_sim.layout.exceptions import InvalidLayout
from anesthesia_sim.layout.model import LayoutModel
from anesthesia_sim.layout.shipped import shipped_workspace
from anesthesia_sim.layout.sizing import (
    PixelSize,
    TooSmall,
    apportion,
    minimum_extent,
    pixel_sizes,
    settle,
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


def _each(tree: Area | Split, size: PixelSize) -> dict[AreaId, PixelSize]:
    return {area.id: size for area in areas_in(tree)}


def test_pixel_sizes_round_down_and_give_the_left_over_pixels_to_the_largest_losses() -> None:
    # 0.5, 0.3 and 0.2 of 984 are 492, 295.2 and 196.8. Rounded down they sum
    # to 983, and the one pixel left goes to 196.8, which lost the most.
    assert pixel_sizes((0.5, 0.3, 0.2), 984) == (492, 295, 197)


def test_a_split_no_bound_holds_is_laid_out_exactly_by_its_fractions() -> None:
    tree = _row((0.5, 0.3, 0.2), _area(1), _area(2), _area(3))
    laid_out = apportion(tree, PixelSize(1000, 600), _HANDLE_PX, _each(tree, PixelSize(10, 10)))

    # 1000 px less two 8 px handles leaves 984, shared as the test above.
    assert laid_out.splits[()] == (492, 295, 197)
    assert laid_out.areas == {
        AreaId(1): PixelSize(492, 600),
        AreaId(2): PixelSize(295, 600),
        AreaId(3): PixelSize(197, 600),
    }
    assert laid_out.unheld == ()


def test_an_area_whose_share_is_below_its_need_is_held_at_it_and_its_neighbour_gives_way() -> None:
    # The dashboard's shape at a 1200 px window: the accounting Area's 0.18
    # of the 1192 px left after the handle would be 214.56 px, below its 260.
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
    # fractions decide: 250 each, and the split is named as not held.
    assert laid_out.splits[()] == (250, 250)
    assert laid_out.unheld == ((),)


def test_a_child_too_tall_for_its_row_leaves_the_row_unheld() -> None:
    tree = _row((0.5, 0.5), _area(1), _area(2))
    bounds = {AreaId(1): PixelSize(10, 10), AreaId(2): PixelSize(10, 400)}

    assert apportion(tree, PixelSize(600, 300), _HANDLE_PX, bounds).unheld == ((),)


def test_minimum_extent_sums_along_each_split_and_takes_the_largest_across_it() -> None:
    # A row of a column (Areas 1 and 3) and Area 2.
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
    fit = settle(tree, PixelSize(1200, 500), _HANDLE_PX, needs, floors, kept=frozenset())

    assert fit.drawn == {AreaId(1), AreaId(2)}
    assert fit.too_small == ()
    assert fit.bounds == needs
    assert fit.apportionment.splits[()] == (932, 260)


def test_a_split_whose_halves_the_extent_cannot_hold_leaves_the_halves_too_small() -> None:
    # Area 2 of a two-Area row was split in two, so Area 4 is new. Three
    # 400 px needs are more than the 1008 - 2 * 8 = 992 px the row has.
    tree = _row((0.5, 0.25, 0.25), _area(1), _area(2), _area(4))
    needs = _each(tree, PixelSize(400, 100))
    floors = _each(tree, PixelSize(40, 30))
    fit = settle(tree, PixelSize(1008, 300), _HANDLE_PX, needs, floors, kept={AreaId(1)})

    # The halves are let go to their floors first, which Area 1, untouched by
    # the split, keeps its need. The fractions then give 496, 248 and 248.
    assert fit.apportionment.splits[()] == (496, 248, 248)
    assert fit.drawn == {AreaId(1)}
    assert fit.too_small == (
        TooSmall(AreaId(2), PixelSize(400, 100), PixelSize(248, 300)),
        TooSmall(AreaId(4), PixelSize(400, 100), PixelSize(248, 300)),
    )
    assert fit.bounds == {
        AreaId(1): PixelSize(400, 100),
        AreaId(2): PixelSize(40, 30),
        AreaId(4): PixelSize(40, 30),
    }


def test_a_split_whose_halves_the_extent_can_hold_takes_their_room_from_the_neighbour() -> None:
    tree = _row((0.5, 0.25, 0.25), _area(1), _area(2), _area(4))
    needs = _each(tree, PixelSize(300, 100))
    floors = _each(tree, PixelSize(40, 30))
    fit = settle(tree, PixelSize(1008, 300), _HANDLE_PX, needs, floors, kept={AreaId(1)})

    # 248 is below 300, so both halves are held at 300, and Area 1 takes the
    # other 992 - 600 = 392, which is still above its own 300.
    assert fit.apportionment.splits[()] == (392, 300, 300)
    assert fit.drawn == {AreaId(1), AreaId(2), AreaId(4)}


def test_kept_areas_are_let_go_only_once_the_others_are_at_their_floors() -> None:
    tree = _row((0.5, 0.5), _area(1), _area(2))
    needs = _each(tree, PixelSize(300, 100))
    floors = _each(tree, PixelSize(40, 30))
    fit = settle(tree, PixelSize(408, 300), _HANDLE_PX, needs, floors, kept={AreaId(1)})

    # Two 300 px needs are more than the 400 px the row has. Area 2, which
    # the change did not leave in place, is let go to its 40 px floor, and
    # that leaves room to hold Area 1 at its need: 300 for Area 1, and the
    # other 100 for Area 2.
    assert fit.apportionment.splits[()] == (300, 100)
    assert fit.drawn == {AreaId(1)}

    narrower = settle(tree, PixelSize(208, 300), _HANDLE_PX, needs, floors, kept={AreaId(1)})

    # At 200 px nothing holds a 300 px need, so Area 1 is let go too, and the
    # fractions give each Area 100.
    assert narrower.apportionment.splits[()] == (100, 100)
    assert narrower.drawn == frozenset()
    assert {entry.area_id for entry in narrower.too_small} == {AreaId(1), AreaId(2)}


def test_a_too_small_area_is_drawn_again_once_the_extent_can_give_it_its_need() -> None:
    tree = _row((0.5, 0.25, 0.25), _area(1), _area(2), _area(4))
    needs = _each(tree, PixelSize(400, 100))
    floors = _each(tree, PixelSize(40, 30))
    small = settle(tree, PixelSize(1008, 300), _HANDLE_PX, needs, floors, kept={AreaId(1)})
    wider = settle(tree, PixelSize(1616, 300), _HANDLE_PX, needs, floors, kept=small.drawn)

    # 1616 - 16 = 1600 holds three 400 px needs: 0.25 of 1600 is exactly 400.
    assert wider.apportionment.splits[()] == (800, 400, 400)
    assert wider.drawn == {AreaId(1), AreaId(2), AreaId(4)}
    assert wider.too_small == ()


def test_a_shipped_workspace_on_a_small_extent_names_its_too_small_areas_and_none_has_no_size() -> (
    None
):
    model = shipped_workspace(ShippedWorkspaceId("induction")).layout
    tree = model.windows[0].tree
    # Induction is row(0.75, 0.25) of column(0.6, 0.4) of Areas 1 and 2, and
    # Area 3. Each needs 300 by 300.
    needs = _each(tree, PixelSize(300, 300))
    floors = _each(tree, PixelSize(60, 40))
    fit = settle(tree, PixelSize(508, 408), _HANDLE_PX, needs, floors, kept=frozenset())

    # 300 + 8 + 300 = 608 px wide is needed and 508 is there, so every Area
    # is let go to its floor and the fractions decide: the row's 500 px give
    # 375 and 125, and the column's 400 give 240 and 160.
    assert fit.apportionment.areas == {
        AreaId(1): PixelSize(375, 240),
        AreaId(2): PixelSize(375, 160),
        AreaId(3): PixelSize(125, 408),
    }
    assert [entry.area_id for entry in fit.too_small] == [AreaId(1), AreaId(2), AreaId(3)]
    assert all(
        size.width_px > 0 and size.height_px > 0 for size in fit.apportionment.areas.values()
    )


def test_settle_holds_a_floor_above_a_need() -> None:
    model = LayoutModel.single_area(_CHART)
    tree = model.windows[0].tree
    fit = settle(
        tree,
        PixelSize(500, 500),
        _HANDLE_PX,
        {AreaId(1): PixelSize(0, 0)},
        {AreaId(1): PixelSize(60, 40)},
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
