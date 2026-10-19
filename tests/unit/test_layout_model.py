"""Unit tests for the layout model: `layout/tree.py` and `layout/model.py`.

`PL-1FT6` built the model `PL-C842` decided - a pure-Python tree of Splits and
Areas that is the layout's source of truth, with no widget anywhere in it - so
every test here runs with no `QApplication`, and the first asserts that
importing the package loads no toolkit at all.

The design these hold the code to was decided before it was written:
`PL-3J2P` took the tree knowing it is strictly less expressive than Blender's
screen, on the ground that the limit shows up as an operation refused rather
than as a wrong layout, which is what
`test_a_join_the_tree_cannot_express_is_refused` holds; `PL-HJPY` put a set of
windows in the root from the first version, with Area ids unique across all
of them and never handed out twice, and the border chain stopping at a
window's edge; `PL-R1WQ` made a View kind an opaque tag the model checks the
syntax of and nothing else. The serialized form is in
`tests/unit/test_layout_serialization.py`; the round trip and the version-1
window set the brief names are asserted here as well, so its `verify:` line
covers its whole definition of done.
"""

import json
import math
import re
import subprocess
import sys

import pytest

from anesthesia_sim.layout.exceptions import InvalidLayout, LayoutRefused, NotInLayout
from anesthesia_sim.layout.model import (
    BORDER_ALIGNMENT_TOLERANCE,
    Handle,
    LayoutModel,
    Neighbour,
    Rectangle,
    Side,
)
from anesthesia_sim.layout.serialization import (
    LAYOUT_SCHEMA_VERSION,
    layout_from_dict,
    layout_from_json,
    layout_to_dict,
    layout_to_json,
)
from anesthesia_sim.layout.tree import (
    AREA_ID_MAXIMUM,
    LAYOUT_SIZE_SUM_TOLERANCE,
    TREE_DEPTH_MAXIMUM,
    VIEW_KIND_MAXIMUM_LENGTH,
    Area,
    AreaId,
    Node,
    Orientation,
    Split,
    ViewKind,
    Window,
)

CHART = ViewKind("concentration_chart")
ACCOUNTING = ViewKind("agent_accounting")
WASH_IN = ViewKind("wash_in")

ROW = Orientation.ROW
COLUMN = Orientation.COLUMN


def area(number: int, view: ViewKind = CHART) -> Area:
    return Area(AreaId(number), view)


def row(sizes: tuple[float, ...], *children: Node) -> Split:
    return Split(ROW, sizes, children)


def column(sizes: tuple[float, ...], *children: Node) -> Split:
    return Split(COLUMN, sizes, children)


def layout(*trees: Node) -> LayoutModel:
    """A layout of one window per tree, its counter one above the highest id."""

    windows = tuple(Window(tree) for tree in trees)
    highest = max(held.id for window in windows for held in _areas(window.tree))

    return LayoutModel(windows, AreaId(highest + 1))


def _areas(node: Node) -> list[Area]:
    if isinstance(node, Area):
        return [node]

    return [held for child in node.children for held in _areas(child)]


def rectangles(model: LayoutModel, window: int = 0) -> dict[int, tuple[float, float, float, float]]:
    """Each Area's (left, top, right, bottom) in fractions of its window, worked out independently.

    Written here rather than read from the model, so a test asserting where
    an Area sits is not asserting the model's arithmetic against itself.
    """

    found: dict[int, tuple[float, float, float, float]] = {}

    def place(node: Node, left: float, top: float, right: float, bottom: float) -> None:
        if isinstance(node, Area):
            found[int(node.id)] = (left, top, right, bottom)
            return

        start = left if node.orientation is ROW else top
        length = (right - left) if node.orientation is ROW else (bottom - top)

        for index, child in enumerate(node.children):
            near = start + length * sum(node.sizes[:index])
            far = start + length * sum(node.sizes[: index + 1])

            if node.orientation is ROW:
                place(child, near, top, far, bottom)
            else:
                place(child, left, near, right, far)

    place(model.windows[window].tree, 0.0, 0.0, 1.0, 1.0)

    return found


def split_at(model: LayoutModel, path: tuple[int, ...], window: int = 0) -> Split:
    """The split at `path` in a window's tree, which the test asserts is one."""

    node = model.windows[window].tree

    for step in path:
        assert isinstance(node, Split)
        node = node.children[step]

    assert isinstance(node, Split)

    return node


def cut_down(depth: int) -> LayoutModel:
    """Area 1 cut in half `depth` times by the model's own `split`, alternating axis.

    Area 1 keeps the part before each cut, so the deepest split, `depth` deep,
    is at the path `(0,) * (depth - 1)`, and Area 1 is its first child.
    """

    model = LayoutModel.single_area(CHART)

    for level in range(depth):
        model, _ = model.split(AreaId(1), (ROW, COLUMN)[level % 2], 0.5)

    return model


def nested(depth: int) -> Split:
    """The same shape built directly, unchecked: `depth` splits, Areas 1 to `depth` + 1."""

    tree = row((0.5, 0.5), area(1), area(2))

    for level in range(1, depth):
        tree = (column if level % 2 else row)((0.5, 0.5), tree, area(level + 2))

    return tree


def buried(tree: Split, levels: int) -> LayoutModel:
    """`tree` nested `levels` splits deep: each split around it holds one more Area, from id 100.

    The splits alternate in orientation outward from `tree`'s own, so `tree`
    is `levels + 1` deep and the splits it holds sit deeper still.
    """

    orientation = tree.orientation

    for level in range(levels):
        orientation = COLUMN if orientation is ROW else ROW
        tree = Split(orientation, (0.5, 0.5), (tree, area(100 + level)))

    return layout(tree)


def joined_places(
    places: dict[int, tuple[float, float, float, float]], keep: int, remove: int
) -> dict[int, tuple[float, float, float, float]]:
    """Each Area's rectangle after a join, from the rectangles before it: `keep` takes both."""

    kept, removed = places[keep], places[remove]
    after = {number: place for number, place in places.items() if number != remove}
    after[keep] = (
        min(kept[0], removed[0]),
        min(kept[1], removed[1]),
        max(kept[2], removed[2]),
        max(kept[3], removed[3]),
    )

    return after


def assert_places(
    model: LayoutModel, expected: dict[int, tuple[float, float, float, float]]
) -> None:
    """Assert each Area of the main window lies where `expected` says, to within rounding."""

    found = rectangles(model)

    assert found.keys() == expected.keys()

    for number, place in expected.items():
        assert found[number] == pytest.approx(place), number


# --- The package is pure Python --------------------------------------------------


def test_importing_the_layout_package_loads_no_toolkit() -> None:
    """`PL-C842`: the model is plain Python a test drives with no widget library loaded.

    `tools/import_boundary_check.py` refuses a `PySide6` or `pyqtgraph`
    import written under `layout/`; this asserts the same of everything the
    package reaches when it is imported, in a fresh interpreter, since this
    test process may already hold Qt from another test.
    """

    probe = (
        "import sys\n"
        "import anesthesia_sim.layout.model, anesthesia_sim.layout.serialization\n"
        "loaded = sorted(name for name in sys.modules "
        "if name.split('.')[0] in {'PySide6', 'pyqtgraph', 'shiboken6', 'numpy'})\n"
        "print(loaded)\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", probe], capture_output=True, text=True, check=True
    )

    assert result.stdout.strip() == "[]"


# --- The values a layout is built from -------------------------------------------


def test_an_area_id_is_a_whole_number_from_one_to_the_largest_json_holds_exactly() -> None:
    """Ids are allocated from 1 and are keys a file is read back by (`layout/tree.py`).

    `True` is refused although it is an `int`, since it would be the Area with
    id 1, and an int too long to print is refused by its length rather than
    escaping as the `ValueError` printing it would raise.
    """

    assert AreaId(1) == 1
    assert AreaId(AREA_ID_MAXIMUM) == 2**53 - 1

    for refused in (0, -1, AREA_ID_MAXIMUM + 1, -(10**5000)):
        with pytest.raises(InvalidLayout, match="an Area id is a whole number from 1"):
            AreaId(refused)

    for wrong in (True, 1.0, "1", None):
        with pytest.raises(TypeError, match="an Area id is an int"):
            AreaId(wrong)  # type: ignore[arg-type]


def test_a_view_kind_is_a_tag_of_the_syntax_the_registry_decided() -> None:
    """`PL-R1WQ` Q1: lowercase snake case, beginning with a letter, at most 40 long."""

    longest = "a" * VIEW_KIND_MAXIMUM_LENGTH

    for tag in ("a", "concentration_chart", "chart_2", longest):
        assert ViewKind(tag) == tag

    for refused in ("", "Chart", "2chart", "_chart", "chart-x", "chart x", "chart\n", "ǆ"):
        with pytest.raises(InvalidLayout, match="a View kind is a tag"):
            ViewKind(refused)

    with pytest.raises(InvalidLayout, match="at most 40 long"):
        ViewKind(longest + "a")

    with pytest.raises(TypeError, match="a View kind is a str"):
        ViewKind(7)  # type: ignore[arg-type]


def test_a_split_refuses_what_is_not_a_layout() -> None:
    """Each invariant a split states of itself, refused as it is built, by name."""

    one, two = area(1), area(2)
    cases: list[tuple[tuple[float, ...], tuple[Node, ...], str]] = [
        ((1.0,), (one,), "two or more children"),
        ((0.5, 0.25, 0.25), (one, two), "one per child"),
        ((1.0, 0.0), (one, two), "above zero"),
        ((1.5, -0.5), (one, two), "above zero"),
        ((math.nan, 0.5), (one, two), "above zero"),
        ((math.inf, 0.5), (one, two), "above zero"),
        ((0.5, 0.25), (one, two), "sum to one"),
    ]

    for sizes, children, invariant in cases:
        with pytest.raises(InvalidLayout, match=invariant):
            Split(ROW, sizes, children)

    with pytest.raises(TypeError, match="a split's size is a float"):
        Split(ROW, (1, 0.5), (one, two))

    with pytest.raises(TypeError, match="an Area or a Split"):
        Split(ROW, (0.5, 0.5), (one, "two"))  # type: ignore[arg-type]


def test_sizes_that_miss_one_only_by_rounding_are_accepted() -> None:
    """Sizes that are one to any reader can sum, exactly rounded, to a unit in the last place short.

    The check sums with `math.fsum`, which rounds once, so it is not a tenth
    ten times that shows the tolerance at work: those sum to exactly one that
    way, though adding them one by one, without compensation, gives
    0.9999999999999999. One hundredth, twenty-nine and seventy do miss one,
    and are accepted.
    """

    tenths = (0.1,) * 10
    hundredths = (0.01, 0.29, 0.7)

    assert abs(math.fsum(tenths) - 1) <= LAYOUT_SIZE_SUM_TOLERANCE
    assert math.fsum(hundredths) == 1 - sys.float_info.epsilon / 2

    Split(ROW, tenths, tuple(area(number) for number in range(1, 11)))
    Split(ROW, hundredths, (area(1), area(2), area(3)))


def test_the_sum_of_a_splits_sizes_is_held_to_the_tolerance_and_no_further() -> None:
    """`LAYOUT_SIZE_SUM_TOLERANCE`, a billionth, is the bound, and the refusal says what it is.

    Sizes a thousandth of the tolerance off one, or nine tenths of it, are
    read as summing to one; eleven tenths of it off, or twice it, are
    refused. The operations rescale each split they rebuild
    (`test_every_operation_works_on_sizes_the_reader_accepts_at_the_edge_of_the_tolerance`),
    so the bound is the reader's, and the model's own splits sit far inside it.
    """

    assert LAYOUT_SIZE_SUM_TOLERANCE == 1e-9

    for offset in (1e-12, 0.9 * LAYOUT_SIZE_SUM_TOLERANCE):
        Split(ROW, (0.5, 0.5 + offset), (area(1), area(2)))

    for offset in (1.1 * LAYOUT_SIZE_SUM_TOLERANCE, 2 * LAYOUT_SIZE_SUM_TOLERANCE):
        with pytest.raises(
            InvalidLayout, match=re.escape(f"to within {LAYOUT_SIZE_SUM_TOLERANCE!r}")
        ):
            Split(ROW, (0.5, 0.5 + offset), (area(1), area(2)))


def test_a_split_never_holds_a_split_of_its_own_orientation() -> None:
    """A row inside a row is one wider row, so a tree takes one form (`layout/tree.py`).

    The form is one only where no four Areas meet at a point. Where they do,
    either cut through the point can be the outer one, so a join reads the
    rectangles rather than which two Areas share a split, as
    `test_where_four_areas_meet_a_join_is_taken_whichever_cut_came_first`
    holds the model to.
    """

    with pytest.raises(InvalidLayout, match="a row split never holds another row split"):
        row((0.5, 0.5), area(1), row((0.5, 0.5), area(2), area(3)))

    row((0.5, 0.5), area(1), column((0.5, 0.5), area(2), area(3)))


def test_a_layout_refuses_no_window_a_shared_id_and_a_counter_it_has_passed() -> None:
    """`PL-HJPY` Q1 and Q3: a main window always, ids unique across windows, never reused."""

    with pytest.raises(InvalidLayout, match="at least one window"):
        LayoutModel((), AreaId(1))

    with pytest.raises(InvalidLayout, match="two Areas hold the id 1"):
        LayoutModel((Window(area(1)), Window(area(1))), AreaId(2))

    with pytest.raises(InvalidLayout, match="next_area_id is 2 and an Area already holds the id 2"):
        LayoutModel((Window(row((0.5, 0.5), area(1), area(2))),), AreaId(2))

    LayoutModel((Window(row((0.5, 0.5), area(1), area(2))),), AreaId(9))


def test_a_layout_refuses_a_tree_nested_past_the_depth_maximum() -> None:
    """`TREE_DEPTH_MAXIMUM`, checked before anything recurses through the tree.

    The refusal names the window and the path of the first split too deep.
    A tree far deeper than Python could recurse through is refused the same
    way, rather than by the `RecursionError` walking it would end in.
    """

    deepest = LayoutModel((Window(nested(TREE_DEPTH_MAXIMUM)),), AreaId(TREE_DEPTH_MAXIMUM + 2))

    assert len(deepest.areas()) == TREE_DEPTH_MAXIMUM + 1

    with pytest.raises(
        InvalidLayout,
        match=re.escape(
            f"window 0's tree holds a split {TREE_DEPTH_MAXIMUM + 1} deep, at path "
            f"{(0,) * TREE_DEPTH_MAXIMUM}, and a split sits at most {TREE_DEPTH_MAXIMUM} deep"
        ),
    ):
        LayoutModel((Window(nested(TREE_DEPTH_MAXIMUM + 1)),), AreaId(TREE_DEPTH_MAXIMUM + 3))

    with pytest.raises(InvalidLayout, match="window 1's tree holds a split"):
        LayoutModel((Window(area(5000)), Window(nested(2000))), AreaId(5001))


# --- Split ------------------------------------------------------------------------


def test_a_new_layout_is_one_window_holding_one_area() -> None:
    model = LayoutModel.single_area(CHART)

    assert model.areas() == (area(1),)
    assert model.next_area_id == 2
    assert len(model.windows) == 1
    assert model.handles() == ()


def test_split_cuts_an_area_where_asked_and_the_new_area_shows_the_same_view() -> None:
    """`PL-TH35` Q10: the new Area starts as a copy of the source, as Blender's split does.

    The Area keeps the part before the cut and the new one takes the rest,
    with the id the counter held.
    """

    model, added = LayoutModel.single_area(ACCOUNTING).split(AreaId(1), ROW, 0.7)

    assert added == 2
    assert model.next_area_id == 3
    assert model.windows[0].tree == row((0.7, 1 - 0.7), area(1, ACCOUNTING), area(2, ACCOUNTING))
    assert rectangles(model)[1] == pytest.approx((0.0, 0.0, 0.7, 1.0))
    assert rectangles(model)[2] == pytest.approx((0.7, 0.0, 1.0, 1.0))


def test_split_along_its_splits_axis_adds_a_child_and_moves_no_border() -> None:
    """The one form: cutting a row's Area across the row widens the row, not the tree.

    Every border that was there stays where it was; only the cut Area's
    space is divided.
    """

    model = layout(row((0.25, 0.75), area(1), area(2)))
    before = rectangles(model)

    split, added = model.split(AreaId(2), ROW, 0.4)

    assert isinstance(split.windows[0].tree, Split)
    assert [len(split.windows[0].tree.children), added] == [3, 3]
    assert rectangles(split)[1] == pytest.approx(before[1])
    assert rectangles(split)[2] == pytest.approx((0.25, 0.0, 0.25 + 0.75 * 0.4, 1.0))
    assert rectangles(split)[3] == pytest.approx((0.25 + 0.75 * 0.4, 0.0, 1.0, 1.0))


def test_split_across_its_splits_axis_nests_a_split_in_the_areas_place() -> None:
    model, added = layout(row((0.5, 0.5), area(1), area(2))).split(AreaId(1), COLUMN, 0.25)

    assert model.windows[0].tree == row(
        (0.5, 0.5), column((0.25, 0.75), area(1), area(added)), area(2)
    )


def test_a_cut_outside_the_area_is_refused_and_the_layout_is_unchanged() -> None:
    """A cut lies strictly inside the Area; the ends and beyond leave a part with no size."""

    model = LayoutModel.single_area(CHART)
    copy = layout_to_json(model)

    for at in (0.0, 1.0, -0.25, 1.5, math.nan, math.inf):
        with pytest.raises(LayoutRefused, match="falls outside it"):
            model.split(AreaId(1), COLUMN, at)

    assert layout_to_json(model) == copy

    with pytest.raises(LayoutRefused, match="leaves a part with no size"):
        layout(row((0.5, 0.5), area(1), area(2))).split(AreaId(1), ROW, 5e-324)


def test_a_split_past_the_last_id_is_refused() -> None:
    """The counter cannot pass `AREA_ID_MAXIMUM`, so a layout that has reached it refuses."""

    full = LayoutModel((Window(area(1)),), AreaId(AREA_ID_MAXIMUM))

    with pytest.raises(LayoutRefused, match="cannot make another Area"):
        full.split(AreaId(1), ROW, 0.5)


def test_a_split_that_leaves_an_area_no_width_is_refused() -> None:
    """A cut that leaves a part no wider or taller than `BORDER_ALIGNMENT_TOLERANCE` is refused.

    This is the reproducer from `PL-391Y`. `split(1, ROW, 5e-324)` used to
    succeed, leaving Area 1 with a width of 5e-324 of the window. `borders()`
    and `join` treated that Area's two edges as one line, and no drag could
    widen it again. Each refusal names the part and its size, which this test
    works out from the cut.
    """

    whole = layout(area(1))

    with pytest.raises(LayoutRefused, match=r"Area 1 would be 5e-324 of the window wide"):
        whole.split(AreaId(1), ROW, 5e-324)

    near_end = 1.0 - 5e-10
    pattern = rf"Area 2 would be {re.escape(repr(1.0 - near_end))} of the window tall"

    with pytest.raises(LayoutRefused, match=pattern):
        whole.split(AreaId(1), COLUMN, near_end)

    # Along the axis of the split that holds it, the cut adds a child, and the
    # part is measured against the window rather than the split.
    halves = layout(row((0.5, 0.5), area(1), area(2)))

    # Half of 1e-9 of the window, placed after the border at 0.5.
    pattern = rf"Area 2 would be {re.escape(repr((0.5 + 5e-10) - 0.5))} of the window wide"

    with pytest.raises(LayoutRefused, match=pattern):
        halves.split(AreaId(2), ROW, 1e-9)

    taken, added = halves.split(AreaId(2), ROW, 4e-9)

    assert rectangles(taken)[2] == pytest.approx((0.5, 0.0, 0.5 + 2e-9, 1.0), abs=1e-15)
    assert added == AreaId(3)


def test_a_layout_holding_an_area_no_wider_than_the_alignment_tolerance_is_refused() -> None:
    """An Area's width is a fraction of the window, however the sizes that give it are nested.

    Each size here is far above the tolerance on its own. Area 3 is a tenth of
    a column that is a hundred-millionth of the window wide. So Area 3 is 1e-9
    of the window wide, and its two edges would be treated as one line.
    """

    edge = 1.0 - 5e-10
    pattern = rf"in window 0, Area 2 is {re.escape(repr(1.0 - edge))} of the window wide"

    with pytest.raises(InvalidLayout, match=pattern):
        layout(row((edge, 5e-10), area(1), area(2)))

    # PL-25D9's layout, whose join of Areas 1 and 4 was refused, cannot be
    # built, since its Area 2 is 5e-10 of the window wide.
    with pytest.raises(InvalidLayout, match=r"in window 0, Area 2 is [0-9.e-]+ of the window wide"):
        layout(
            column(
                (0.5, 0.5),
                row((0.5, 5e-10, 0.5 - 5e-10), area(1), area(2), area(3)),
                row((0.5, 0.5), area(4), area(5)),
            )
        )

    with pytest.raises(InvalidLayout, match=r"in window 0, Area 3 is [0-9.e-]+ of the window wide"):
        layout(
            row(
                (1.0 - 1e-8, 1e-8),
                area(1),
                column((0.5, 0.5), row((0.9, 0.1), area(2), area(3)), area(4)),
            )
        )


def test_the_last_id_a_layout_hands_out_is_one_below_the_maximum() -> None:
    """The counter stays above every id in use and cannot pass `AREA_ID_MAXIMUM`.

    So the last id handed out is 2**53 - 2, the refusal after it names the
    counter's value rather than an id an Area holds, and no Area can hold the
    maximum itself.
    """

    model, last = LayoutModel((Window(area(1)),), AreaId(AREA_ID_MAXIMUM - 1)).split(
        AreaId(1), ROW, 0.5
    )

    assert last == AREA_ID_MAXIMUM - 1 == 2**53 - 2
    assert model.next_area_id == AREA_ID_MAXIMUM

    with pytest.raises(
        LayoutRefused,
        match=re.escape(
            f"the next id it would hand out, {AREA_ID_MAXIMUM}, is the largest an Area id can be"
        ),
    ):
        model.split(AreaId(1), ROW, 0.5)

    with pytest.raises(InvalidLayout, match=f"an Area already holds the id {AREA_ID_MAXIMUM}"):
        LayoutModel((Window(area(AREA_ID_MAXIMUM)),), AreaId(AREA_ID_MAXIMUM))


def test_a_cut_that_would_nest_past_the_depth_maximum_is_refused() -> None:
    """A cut across the deepest split's axis would add a level; one along it adds a child.

    The layout the model builds at the maximum is read back equal, so no
    layout it holds is one it cannot save.
    """

    model = cut_down(TREE_DEPTH_MAXIMUM)
    along = split_at(model, (0,) * (TREE_DEPTH_MAXIMUM - 1)).orientation
    across = COLUMN if along is ROW else ROW

    with pytest.raises(
        LayoutRefused,
        match=re.escape(
            f"a {across.value} split of Area 1 would sit {TREE_DEPTH_MAXIMUM + 1} deep, and a "
            f"split sits at most {TREE_DEPTH_MAXIMUM} deep in a window's tree"
        ),
    ):
        model.split(AreaId(1), across, 0.5)

    widened, _ = model.split(AreaId(1), along, 0.5)

    assert len(widened.areas()) == TREE_DEPTH_MAXIMUM + 2
    assert layout_from_json(layout_to_json(widened)) == widened


# --- Join -------------------------------------------------------------------------


def test_join_gives_the_kept_area_both_spaces_and_drops_the_other() -> None:
    model = layout(row((0.25, 0.25, 0.5), area(1, CHART), area(2, WASH_IN), area(3, ACCOUNTING)))

    joined = model.join(AreaId(3), AreaId(2))

    assert joined.windows[0].tree == row((0.25, 0.75), area(1, CHART), area(3, ACCOUNTING))
    assert joined.next_area_id == model.next_area_id


def test_a_join_that_leaves_one_child_gives_the_split_way_to_it() -> None:
    model = layout(row((0.5, 0.5), area(1), column((0.5, 0.5), area(2), area(3))))

    assert model.join(AreaId(2), AreaId(3)).windows[0].tree == row((0.5, 0.5), area(1), area(2))
    assert layout(column((0.5, 0.5), area(1), area(2))).join(AreaId(2), AreaId(1)).windows[
        0
    ].tree == area(2)


def test_a_join_the_tree_cannot_express_is_refused() -> None:
    """`PL-3J2P`'s refusal: a layout a splitter tree cannot hold is not offered.

    Blender joins any two Areas sharing a whole edge, and `PL-3J2P` found
    that one such join leaves every layout a tree can hold: six Areas built
    by full-span cuts, whose left column is in two parts, join into the
    five-Area pinwheel no sequence of full-span cuts produces. This builds
    those six - the pinwheel with its left bar cut at two thirds - and asks
    for the join. The two parts share their whole edge, as the independent
    geometry below confirms. No straight cut divides the five Areas the join
    would leave, so the tree refuses rather than return a layout other than
    the one asked for, and the layout it was asked of is unchanged.
    """

    third, two_thirds = 1 / 3, 2 / 3
    six = layout(
        column(
            (two_thirds, 1 - two_thirds),
            row(
                (two_thirds, 1 - two_thirds),
                column((0.5, 0.5), area(1), row((0.5, 0.5), area(4), area(5))),
                area(2),
            ),
            row((third, 1 - third), area(6), area(3)),
        )
    )
    upper, lower = rectangles(six)[4], rectangles(six)[6]
    copy = layout_to_json(six)

    assert (upper[0], upper[2]) == pytest.approx((lower[0], lower[2]))
    assert upper[3] == pytest.approx(lower[1])

    with pytest.raises(LayoutRefused, match="no straight cut divides the Areas the join would"):
        six.join(AreaId(4), AreaId(6))

    assert layout_to_json(six) == copy


def test_a_join_of_areas_that_do_not_share_a_whole_edge_is_refused() -> None:
    """The cases Blender refuses as well, or trims: no side by side pair, no join."""

    partial = layout(row((0.5, 0.5), area(1), column((0.5, 0.5), area(2), area(3))))
    apart = layout(row((0.25, 0.25, 0.5), area(1), area(2), area(3)))
    windows = LayoutModel((Window(area(1)), Window(area(2))), AreaId(3))

    with pytest.raises(LayoutRefused, match="only where they sit next to each other"):
        partial.join(AreaId(1), AreaId(2))

    # Neighbouring places in two different splits: Area 1 is the root's first
    # child and Area 3 the column's second, so it is the split, not the place
    # in it, that keeps them apart.
    with pytest.raises(LayoutRefused, match="only where they sit next to each other"):
        partial.join(AreaId(1), AreaId(3))

    with pytest.raises(LayoutRefused, match="only where they sit next to each other"):
        apart.join(AreaId(1), AreaId(3))

    with pytest.raises(LayoutRefused, match="in different windows"):
        windows.join(AreaId(1), AreaId(2))

    with pytest.raises(LayoutRefused, match="cannot be joined to itself"):
        apart.join(AreaId(2), AreaId(2))


def test_where_four_areas_meet_a_join_is_taken_whichever_cut_came_first() -> None:
    """A 2x2 grid is two trees, and a join reads the rectangles, never which tree holds them.

    Cut across first, the grid is a column of two rows; cut down first, a row
    of two columns. Which two Areas sit in one split differs between them,
    and before `PL-G60V` a join depended on it: Area 1 could join the Area
    beside it in one tree and the Area below it in the other. Now each join
    of two Areas that share an edge is taken from both trees, in either
    order, and gives the rectangles worked out here from the grid's
    quarters. The two pairs that meet only at the centre share no edge and
    are refused from both.
    """

    across_first = layout(
        column((0.5, 0.5), row((0.5, 0.5), area(1), area(2)), row((0.5, 0.5), area(3), area(4)))
    )
    down_first = layout(
        row((0.5, 0.5), column((0.5, 0.5), area(1), area(3)), column((0.5, 0.5), area(2), area(4)))
    )
    quarters = {
        1: (0.0, 0.0, 0.5, 0.5),
        2: (0.5, 0.0, 1.0, 0.5),
        3: (0.0, 0.5, 0.5, 1.0),
        4: (0.5, 0.5, 1.0, 1.0),
    }

    assert rectangles(across_first) == rectangles(down_first) == quarters

    for first, second in ((1, 2), (1, 3), (2, 4), (3, 4)):
        for keep, remove in ((first, second), (second, first)):
            for model in (across_first, down_first):
                joined = model.join(AreaId(keep), AreaId(remove))

                assert rectangles(joined) == joined_places(quarters, keep, remove)

    assert down_first.join(AreaId(1), AreaId(3)).windows[0].tree == row(
        (0.5, 0.5), area(1), column((0.5, 0.5), area(2), area(4))
    )
    assert across_first.join(AreaId(1), AreaId(2)).windows[0].tree == column(
        (0.5, 0.5), area(1), row((0.5, 0.5), area(3), area(4))
    )
    assert across_first.join(AreaId(1), AreaId(3)).windows[0].tree == row(
        (0.5, 0.5), area(1), column((0.5, 0.5), area(2), area(4))
    )
    assert down_first.join(AreaId(1), AreaId(2)).windows[0].tree == column(
        (0.5, 0.5), area(1), row((0.5, 0.5), area(3), area(4))
    )

    for model in (across_first, down_first):
        for keep, remove in ((1, 4), (2, 3)):
            with pytest.raises(LayoutRefused, match="only where they sit next to each other"):
                model.join(AreaId(keep), AreaId(remove))


def test_a_join_across_a_junction_cuts_the_region_into_every_strip_it_holds() -> None:
    """Three columns of two rows: joining two Areas of the first column leaves three strips.

    The rows hold Areas 1, 2, 3 above and 4, 5, 6 below, so Areas 1 and 4
    sit in different splits. Joined, the left third is one Area, and the
    region is cut down at both thirds at once, since a row never holds a
    row: one split of three children, not two nested ones.
    """

    third = 1 / 3
    model = layout(
        column(
            (0.5, 0.5),
            row((third, third, 1 - 2 * third), area(1), area(2), area(3)),
            row((third, third, 1 - 2 * third), area(4), area(5), area(6)),
        )
    )

    joined = model.join(AreaId(1), AreaId(4))
    tree = joined.windows[0].tree

    assert_places(joined, joined_places(rectangles(model), 1, 4))
    assert isinstance(tree, Split)
    assert tree.orientation is ROW
    assert [_areas(child) for child in tree.children] == [
        [area(1)],
        [area(2), area(5)],
        [area(3), area(6)],
    ]


def test_a_join_merges_a_re_sliced_region_into_the_split_above_it() -> None:
    """A row inside a row is one wider row, so a region re-sliced down continues the row above.

    The grid fills the right half of a row. Joining its two left Areas
    leaves the grid's region cut down its middle, along the row's own axis,
    so the merged Area and the column beside it become children of the row.
    """

    model = layout(
        row(
            (0.5, 0.5),
            area(5),
            column(
                (0.5, 0.5), row((0.5, 0.5), area(1), area(2)), row((0.5, 0.5), area(3), area(4))
            ),
        )
    )

    assert model.join(AreaId(1), AreaId(3)).windows[0].tree == row(
        (0.5, 0.25, 0.25), area(5), area(1), column((0.5, 0.5), area(2), area(4))
    )


def test_a_join_keeps_the_splits_beside_it_as_they_were() -> None:
    """A subtree beside the pair is kept whole, even where its own border could cut the region.

    The grid beside Areas 1 and 2 has a border down its middle that crosses
    the whole window. Joining Areas 1 and 2 needs no cut there, so the grid
    stays a column of two rows rather than being opened into the window's
    row.
    """

    grid = column((0.5, 0.5), row((0.5, 0.5), area(3), area(4)), row((0.5, 0.5), area(5), area(6)))
    model = layout(row((0.25, 0.25, 0.5), area(1), area(2), grid))

    assert model.join(AreaId(1), AreaId(2)).windows[0].tree == row((0.5, 0.5), area(1), grid)


def test_a_join_opens_a_split_beside_it_where_that_splits_border_is_the_only_cut() -> None:
    """Where only a border inside a subtree beside the pair divides the region, the join opens it.

    Areas 7 and 9 share their whole edge, and joined they span two thirds
    of the window's width along its foot. The only straight cut through the
    result runs down at one third, through the middle of the row holding
    Areas 2 and 3, which holds neither Area joined. Kept whole, that row
    would leave no cut at all, so the join is taken from the Areas
    themselves, and Areas 2 and 3 end in different splits.
    """

    third = 1 / 3
    model = layout(
        row(
            (2 * third, 1 - 2 * third),
            column(
                (0.5, 0.5),
                row((0.5, 0.5), area(2), area(3)),
                row((0.5, 0.5), area(4), column((0.5, 0.5), area(5), area(7))),
            ),
            column((0.75, 0.25), area(8), area(9)),
        )
    )

    joined = model.join(AreaId(9), AreaId(7))

    assert_places(joined, joined_places(rectangles(model), 9, 7))


def test_a_join_needing_a_split_past_the_depth_maximum_is_refused() -> None:
    """A join can need a level more than the tree held, and is refused past the maximum depth.

    Below Area 1 lie two rows of two, their borders in line. Joining the two
    right-hand Areas leaves a column on the left inside a row, one level
    deeper than the rows were, and no other tree holds those rectangles.
    With the rows at the maximum depth the join is refused, and one level
    higher it is taken.
    """

    eighth = 0.125
    rows = column(
        (0.75, eighth, eighth),
        area(1),
        row((1 - eighth, eighth), area(2), area(3)),
        row((1 - eighth, eighth), area(4), area(5)),
    )
    deepest = buried(rows, TREE_DEPTH_MAXIMUM - 2)
    higher = buried(rows, TREE_DEPTH_MAXIMUM - 3)

    with pytest.raises(LayoutRefused, match=f"more than {TREE_DEPTH_MAXIMUM} deep"):
        deepest.join(AreaId(5), AreaId(3))

    assert_places(higher.join(AreaId(5), AreaId(3)), joined_places(rectangles(higher), 5, 3))


def test_a_join_too_deep_cut_one_way_is_taken_cut_the_other() -> None:
    """Where cutting along the split's own axis would pass the depth maximum, the join cuts across.

    Three rows of two lie at the maximum depth inside a row. Joining the top
    two left Areas, a cut across first would leave the merged Area and a
    column beside it in a row one level deeper. A cut down first gives two
    columns, which join the row above, so the join is taken that way.
    """

    third = 1 / 3
    grid = column(
        (third, third, 1 - 2 * third),
        row((0.5, 0.5), area(1), area(2)),
        row((0.5, 0.5), area(3), area(4)),
        row((0.5, 0.5), area(5), area(6)),
    )
    model = buried(grid, TREE_DEPTH_MAXIMUM - 2)

    joined = model.join(AreaId(1), AreaId(3))

    assert_places(joined, joined_places(rectangles(model), 1, 3))


def test_a_join_too_deep_for_its_split_is_taken_by_cutting_a_split_above_first() -> None:
    """Whether a join fits the depth maximum depends on the rectangles, not on the tree.

    The two trees hold the same rectangles: a cut down at x = 0.75 and a cut
    across at y = 0.25 meet at a point, and each tree takes a different one
    first. Joining Areas 9 and 12 needs one level more inside the lowest split
    holding both. In the tree that cut down first, that split is too deep, and
    the join was refused there. Cutting the region of a split above it across
    first fits, as the other tree shows, so both now take the join.
    """

    upper = row((1 / 3, 0.5, 1 / 6), area(7), area(8), area(9))
    lower = row((0.5, 1 / 3, 1 / 6), area(10), area(11), area(12))
    down_first = column(
        (0.5, 0.5),
        row(
            (0.75, 0.25),
            column((0.25, 0.75), area(1), area(2)),
            column((0.25, 0.375, 0.375), area(5), upper, lower),
        ),
        area(99),
    )
    across_first = column(
        (0.125, 0.375, 0.5),
        row((0.75, 0.25), area(1), area(5)),
        row((0.75, 0.25), area(2), column((0.5, 0.5), upper, lower)),
        area(99),
    )

    for tree in (down_first, across_first):
        model = buried(tree, TREE_DEPTH_MAXIMUM - 4)

        assert_places(model.join(AreaId(9), AreaId(12)), joined_places(rectangles(model), 9, 12))


def test_a_join_that_merges_into_the_split_above_may_reach_the_depth_maximum() -> None:
    """A region one level deeper than its place is taken when it merges into the split above.

    Joining Areas 1 and 2 leaves a column holding the merged Area beside a
    row of Areas 4 and 5 and, under it, Area 3 beside them. Cut down first,
    the region becomes a row, which merges into the row above it, so the
    result fits the maximum although the region alone counted one level too
    many.
    """

    grid = column(
        (0.5, 0.5),
        row((0.5, 0.5), area(1), area(3)),
        row((0.5, 0.25, 0.25), area(2), area(4), area(5)),
    )
    model = buried(grid, TREE_DEPTH_MAXIMUM - 2)

    assert_places(model.join(AreaId(1), AreaId(2)), joined_places(rectangles(model), 1, 2))


def test_a_join_reads_two_edges_that_differ_only_by_rounding_as_one() -> None:
    """Edges within `BORDER_ALIGNMENT_TOLERANCE` are one edge, to a join as to `borders()`.

    The top row's second border is placed at 0.1 + 0.2, which is
    0.30000000000000004, and the bottom row's border at 0.3. Areas 3 and 5
    therefore share their left edge only to within rounding. Compared
    exactly, they would share no whole edge, and no line would cross the
    window at 0.3.
    """

    model = layout(
        column(
            (0.5, 0.5),
            row((0.1, 0.2, 0.7), area(1), area(2), area(3)),
            row((0.3, 0.7), area(4), area(5)),
        )
    )
    places = rectangles(model)

    assert places[3][0] != places[5][0]
    assert abs(places[3][0] - places[5][0]) <= BORDER_ALIGNMENT_TOLERANCE

    assert_places(model.join(AreaId(3), AreaId(5)), joined_places(places, 3, 5))


def test_a_chain_of_borders_wider_than_the_tolerance_is_cut_where_it_enters_no_area() -> None:
    """A chain of edges, each within the tolerance of the next, is cut where it enters no Area.

    This tests `PL-8GLZ`. Area 2's left edge is at 0.5, Area 4's is at 0.5 + 6e-10,
    and Area 6's is at 0.5 + 1.2e-9. Followed from edge to edge, they form one line,
    but that line is wider than `BORDER_ALIGNMENT_TOLERANCE`. Joining Areas 1 and 3
    leaves Area 7 across every horizontal cut, so the region must be cut along that
    line. When the cut was drawn at the line's first edge, it entered Area 5, which
    ends at 0.5 + 1.2e-9, and the join was refused. Drawn at 0.5 + 6e-10, the cut
    enters no Area by more than the tolerance. So the join succeeds, and every Area
    keeps its place.
    """

    step = 6e-10
    left, right = 0.5, 0.75
    upper, lower = left + step, left + 2 * step
    model = layout(
        column(
            (1 / 3, 2 / 3),
            row((left, 1 - left), area(1), area(2)),
            row(
                (right, 1 - right),
                column(
                    (0.5, 0.5),
                    row((upper / right, 1 - upper / right), area(3), area(4)),
                    row((lower / right, 1 - lower / right), area(5), area(6)),
                ),
                area(7),
            ),
        )
    )
    places = rectangles(model)

    assert places[6][0] - places[2][0] > BORDER_ALIGNMENT_TOLERANCE

    assert_places(model.join(AreaId(1), AreaId(3)), joined_places(places, 1, 3))


def test_an_id_is_never_handed_out_twice() -> None:
    """`PL-HJPY` Q3: state kept per Area id must not reach an Area that never had it."""

    model, second = LayoutModel.single_area(CHART).split(AreaId(1), ROW, 0.5)
    model = model.join(AreaId(1), second)
    model, third = model.split(AreaId(1), ROW, 0.5)

    assert third not in (AreaId(1), second)
    assert third > second


# --- Resize, and the border a drag reads -----------------------------------------


def test_resize_moves_only_the_two_children_a_border_divides() -> None:
    model = layout(row((0.25, 0.25, 0.5), area(1), area(2), area(3)))

    moved = model.resize(Handle(0, (), 0), 0.4)

    assert isinstance(moved.windows[0].tree, Split)
    assert moved.windows[0].tree.sizes == pytest.approx((0.4, 0.1, 0.5))
    assert rectangles(moved)[3] == pytest.approx(rectangles(model)[3])


def test_resize_places_a_nested_border_where_it_is_dragged() -> None:
    """`position` is a fraction of the window, whatever share of it the border's split holds.

    Each row here is a split three deep, in the upper right quarter of the
    window, so where a border sits in its split and where it sits in the
    window differ. In the second, the border dragged is the row's second, so
    the two children it divides begin after the first, a quarter of the way in.
    """

    halves = layout(
        row((0.5, 0.5), area(1), column((0.5, 0.5), row((0.5, 0.5), area(2), area(3)), area(4)))
    )
    thirds = layout(
        row(
            (0.5, 0.5),
            area(1),
            column((0.5, 0.5), row((0.25, 0.25, 0.5), area(2), area(3), area(5)), area(4)),
        )
    )

    moved = halves.resize(Handle(0, (1, 0), 0), 0.8)

    assert rectangles(moved)[2] == pytest.approx((0.5, 0.0, 0.8, 0.5))
    assert rectangles(moved)[3] == pytest.approx((0.8, 0.0, 1.0, 0.5))
    assert rectangles(moved)[4] == rectangles(halves)[4]

    moved = thirds.resize(Handle(0, (1, 0), 1), 0.7)

    assert split_at(moved, (1, 0)).sizes == pytest.approx((0.25, 0.15, 0.6))
    assert rectangles(moved)[3][2] == pytest.approx(0.7)


def test_a_drag_moves_only_the_borders_on_its_line() -> None:
    """`PL-5HSG`: a border no reader touched keeps its place in the window, as in Blender.

    The root border here divides Area 1 from a column whose upper row holds
    Areas 2 and 4. Dragged from 0.5 to 0.25, the column widens, but the
    border between Areas 2 and 4 lies on no moved line, so it stays at 0.75.
    Area 2 takes all the width the drag gives, and Area 4 keeps its quarter
    of the window. Blender's `area_move_apply_do` moves only the vertices on
    the dragged line, which is what the project owner chose. The row's sizes
    are worked out again, as fractions of its new width. The same holds with
    that border at 0.625, where the row comes out halved, and with a third
    Area in the row. Area 3, below, has its left edge on the line, so it
    widens with the column, and the column's own border does not move.
    """

    model = layout(
        row((0.5, 0.5), area(1), column((0.5, 0.5), row((0.5, 0.5), area(2), area(4)), area(3)))
    )

    moved = model.resize(Handle(0, (), 0), 0.25)

    assert rectangles(model)[4] == (0.75, 0.0, 1.0, 0.5)
    assert rectangles(moved)[4] == pytest.approx((0.75, 0.0, 1.0, 0.5))
    assert rectangles(moved)[2] == pytest.approx((0.25, 0.0, 0.75, 0.5))
    assert rectangles(moved)[3] == pytest.approx((0.25, 0.5, 1.0, 1.0))
    assert split_at(moved, (1, 0)).sizes == pytest.approx((2 / 3, 1 / 3))

    model = layout(
        row((0.5, 0.5), area(1), column((0.5, 0.5), row((0.25, 0.75), area(2), area(4)), area(3)))
    )

    moved = model.resize(Handle(0, (), 0), 0.25)

    assert rectangles(moved)[4] == pytest.approx((0.625, 0.0, 1.0, 0.5))
    assert rectangles(moved)[2] == pytest.approx((0.25, 0.0, 0.625, 0.5))
    assert split_at(moved, (1, 0)).sizes == (0.5, 0.5)

    three = layout(
        row(
            (0.5, 0.5),
            area(1),
            column((0.5, 0.5), row((0.25, 0.25, 0.5), area(2), area(4), area(5)), area(3)),
        )
    )

    widened = three.resize(Handle(0, (), 0), 0.25)

    assert rectangles(widened)[2] == pytest.approx((0.25, 0.0, 0.625, 0.5))
    assert rectangles(widened)[4] == pytest.approx(rectangles(three)[4])
    assert rectangles(widened)[5] == pytest.approx(rectangles(three)[5])


def test_a_drag_past_a_border_beside_its_line_is_refused() -> None:
    """A border that stays put limits a drag, as the window's edge does.

    Dragged from 0.5 to 0.75 or past it, the root border would reach the
    border between Areas 2 and 4, which does not move, and leave Area 2 no
    room. While each child kept its proportions that border moved ahead of
    the drag, and the drag was taken. Short of it, the drag is taken and
    Area 2 narrows to what is left.
    """

    model = layout(
        row((0.5, 0.5), area(1), column((0.5, 0.5), row((0.5, 0.5), area(2), area(4)), area(3)))
    )
    copy = layout_to_json(model)

    for position in (0.75, 0.8):
        with pytest.raises(LayoutRefused, match="no room for Area 2$"):
            model.resize(Handle(0, (), 0), position)

    assert layout_to_json(model) == copy
    assert rectangles(model.resize(Handle(0, (), 0), 0.7))[2] == pytest.approx(
        (0.7, 0.0, 0.75, 0.5)
    )


def test_a_drag_refuses_a_gap_the_stored_sizes_would_round_away() -> None:
    """A drag is refused when the Area it narrows would have no width once the sizes are stored.

    The check once looked at the sizes the drag computed, not at the borders
    those sizes give. A drag to 0.9999999999999999 gave Area 4 a size of about
    1.7e-16, which passed the check. But the border placed from the stored sizes
    lands on 1.0, the window's edge. The layout then held an Area with no width,
    and a drag inside a split of no width divided by zero. A drag that leaves an
    Area some width, but no more than `BORDER_ALIGNMENT_TOLERANCE`, is refused
    in the same way, because a layout cannot hold that Area (`PL-391Y`).
    """

    model = layout(
        row(
            (1 / 3, 2 / 3),
            area(1),
            column((0.5, 0.5), row((0.375, 0.125, 0.5), area(2), area(3), area(4)), area(5)),
        )
    )

    with pytest.raises(LayoutRefused, match="no room for Area 4$"):
        model.resize(Handle(0, (1, 0), 1), 0.9999999999999999)

    flat = layout(
        row((0.5, 0.5), area(1), column((0.5, 0.5), row((0.5, 0.5), area(2), area(3)), area(4)))
    )

    with pytest.raises(LayoutRefused, match="no room for Area 2$"):
        flat.resize(Handle(0, (1, 0), 0), 0.5 + BORDER_ALIGNMENT_TOLERANCE / 2)


def test_a_drag_leaves_a_split_off_its_line_exactly_as_it_was() -> None:
    """A split whose extent is the same and which holds no moved handle keeps its sizes as stored.

    Worked out again from where its borders lie, a row of a tenth, two tenths
    and seven tenths comes back with 0.20000000000000004 for its middle size.
    The drag here moves only the top row's border, so the bottom row is left
    as it was, to the last bit.
    """

    bottom = row((0.1, 0.2, 0.7), area(3), area(4), area(5))
    model = layout(column((0.5, 0.5), row((0.5, 0.5), area(1), area(2)), bottom))

    dragged = model.resize(Handle(0, (0,), 0), 0.25)

    assert dragged.windows[0].tree.children[1] == bottom
    assert rectangles(dragged)[1] == pytest.approx((0.0, 0.0, 0.25, 0.5))


def test_a_drag_to_where_the_border_lies_returns_an_equal_layout() -> None:
    """A handle already at `position` is left as it is, not recomputed from where it lies.

    Recomputed, a row of a tenth, two tenths and seven tenths came back with
    0.20000000000000004 for its middle size, unequal to the layout dragged.
    """

    model = layout(row((0.1, 0.2, 0.7), area(1), area(2), area(3)))

    assert model.resize(Handle(0, (), 0), 0.1) == model
    assert model.resize(Handle(0, (), 1), rectangles(model)[2][2]) == model


def test_borders_follows_a_line_through_its_crossings() -> None:
    """Three rows cut at one x make one vertical border, and a drag moves all three handles.

    The junction where each meets the next is a crossing of two lines, and at
    a crossing Blender's border is one line: the thing `PL-3J2P` measured a
    tree to lose, and recovers by this query.
    """

    model = layout(
        column(
            (0.25, 0.25, 0.5),
            row((0.5, 0.5), area(1), area(2)),
            row((0.5, 0.5), area(3), area(4)),
            row((0.5, 0.5), area(5), area(6)),
        )
    )
    line = (Handle(0, (0,), 0), Handle(0, (1,), 0), Handle(0, (2,), 0))

    for handle in line:
        assert model.borders(handle) == line

    moved = model.resize(Handle(0, (1,), 0), 0.3)

    for left in (1, 3, 5):
        assert rectangles(moved)[left][2] == pytest.approx(0.3)


def test_borders_stops_where_the_line_breaks() -> None:
    """Collinear is not enough: the handles must also meet end to end.

    Two columns cut at the same height with a full-height Area between them
    have collinear borders an Area separates, and Blender moves those
    independently; so does this. A row cut off the line in the middle of
    three ends the line there, and the rows above and below it are then not
    connected to each other either.
    """

    separated = layout(
        row(
            (0.25, 0.5, 0.25),
            column((0.5, 0.5), area(1), area(2)),
            area(3),
            column((0.5, 0.5), area(4), area(5)),
        )
    )
    broken = layout(
        column(
            (0.25, 0.25, 0.5),
            row((0.5, 0.5), area(1), area(2)),
            row((0.75, 0.25), area(3), area(4)),
            row((0.5, 0.5), area(5), area(6)),
        )
    )

    assert separated.borders(Handle(0, (0,), 0)) == (Handle(0, (0,), 0),)
    assert separated.borders(Handle(0, (2,), 0)) == (Handle(0, (2,), 0),)

    for handle in (Handle(0, (0,), 0), Handle(0, (1,), 0), Handle(0, (2,), 0)):
        assert broken.borders(handle) == (handle,)


def test_borders_reads_the_line_to_within_rounding_and_no_further() -> None:
    """Rounding never splits a line; a border a visible distance off it is not on it."""

    near = 0.5 + BORDER_ALIGNMENT_TOLERANCE / 2
    far = 0.5 + BORDER_ALIGNMENT_TOLERANCE * 2

    for offset, joined in ((near, True), (far, False)):
        model = layout(
            column(
                (0.5, 0.5),
                row((0.5, 0.5), area(1), area(2)),
                row((offset, 1 - offset), area(3), area(4)),
            )
        )

        assert (len(model.borders(Handle(0, (0,), 0))) == 2) is joined


def test_borders_is_one_set_whichever_of_its_handles_is_asked() -> None:
    """Each handle is compared with the one that reached it, so the line is the same from each.

    Three rows cut 0.6 of the tolerance apart in turn: the top and bottom
    handles are further apart than the tolerance, but each is within it of
    the middle one, so all three are one line from every one of them, and a
    drag from the top moves the bottom row too.
    """

    step = 0.6 * BORDER_ALIGNMENT_TOLERANCE
    model = layout(
        column(
            (0.25, 0.25, 0.5),
            row((0.5, 0.5), area(1), area(2)),
            row((0.5 + step, 0.5 - step), area(3), area(4)),
            row((0.5 + 2 * step, 0.5 - 2 * step), area(5), area(6)),
        )
    )
    line = (Handle(0, (0,), 0), Handle(0, (1,), 0), Handle(0, (2,), 0))

    for handle in line:
        assert model.borders(handle) == line

    moved = model.resize(Handle(0, (0,), 0), 0.4)

    for left in (1, 3, 5):
        assert rectangles(moved)[left][2] == pytest.approx(0.4)


def test_a_drag_moves_every_handle_on_its_line_or_is_refused() -> None:
    """Two handles of one split on the line are both moved, and no handle is left behind.

    The upper row's middle Area is one and a half times
    `BORDER_ALIGNMENT_TOLERANCE` wide, just above the narrowest width a layout
    allows. The lower row's border lies halfway across it. So both of the
    middle Area's borders lie within the tolerance of the lower row's border,
    on its line. Moving that line moves both borders, which leaves the middle
    Area no room. So the drag is refused, and the message names that Area. The
    drag once moved one of the two borders and left the other where it was.
    """

    sliver = 1.5 * BORDER_ALIGNMENT_TOLERANCE
    model = layout(
        column(
            (0.5, 0.5),
            row((0.5, sliver, 0.5 - sliver), area(1), area(2), area(3)),
            row((0.5 + sliver / 2, 0.5 - sliver / 2), area(4), area(5)),
        )
    )
    lower = Handle(0, (1,), 0)

    assert model.borders(lower) == (Handle(0, (0,), 0), Handle(0, (0,), 1), lower)

    for position in (0.5 + sliver / 2, 0.4):
        with pytest.raises(LayoutRefused, match="would leave no room for Area 2"):
            model.resize(lower, position)


def test_a_drag_with_shift_moves_only_the_border_under_the_pointer() -> None:
    """`alone` moves one handle, and the other handles on its line stay where they were.

    Three rows are stacked, each split at the middle, so the three borders
    are one line at 0.5. Without `alone`, moving the middle row's border to
    0.25 moves all three. With it, only the middle row becomes a quarter and
    three quarters, and the rows above and below keep their halves.
    """

    model = layout(
        column(
            (1 / 3, 1 / 3, 1 / 3),
            row((0.5, 0.5), area(1), area(2)),
            row((0.5, 0.5), area(3), area(4)),
            row((0.5, 0.5), area(5), area(6)),
        )
    )
    middle = Handle(0, (1,), 0)

    together = model.resize(middle, 0.25)
    alone = model.resize(middle, 0.25, alone=True)

    for path in ((0,), (1,), (2,)):
        assert split_at(together, path).sizes == pytest.approx((0.25, 0.75))

    assert split_at(alone, (1,)).sizes == pytest.approx((0.25, 0.75))
    assert split_at(alone, (0,)).sizes == (0.5, 0.5)
    assert split_at(alone, (2,)).sizes == (0.5, 0.5)
    assert alone.borders(middle) == (middle,)


@pytest.mark.parametrize("alone", [1, None, "yes"])
def test_resize_refuses_an_alone_that_is_not_a_bool(alone: object) -> None:
    model = layout(row((0.5, 0.5), area(1), area(2)))

    with pytest.raises(TypeError, match="alone is a bool"):
        model.resize(Handle(0, (), 0), 0.25, alone=alone)  # type: ignore[arg-type]


def test_position_is_where_a_border_lies_in_its_window() -> None:
    """A nested border's place is a fraction of the window, not of its own split.

    The lower row fills the right half of the window and is split at a
    quarter of its own width, so its border lies at 0.5 + 0.25 * 0.5 = 0.625.
    """

    model = layout(
        row((0.5, 0.5), area(1), column((0.4, 0.6), area(2), row((0.25, 0.75), area(3), area(4))))
    )

    assert model.position(Handle(0, (), 0)) == 0.5
    assert model.position(Handle(0, (1,), 0)) == pytest.approx(0.4)
    assert model.position(Handle(0, (1, 1), 0)) == pytest.approx(0.625)

    with pytest.raises(NotInLayout):
        model.position(Handle(0, (1, 1), 1))


def test_borders_joins_only_handles_of_its_own_orientation() -> None:
    """A row's border runs down the window and a column's across it; one never continues the other.

    The innermost column's border lies at a height of one half and ends a
    quarter of the way across; the root row's lies at one half across and
    begins a quarter of the way down. Compared as numbers, without their
    direction, the two would read as one line meeting end to end; they are
    perpendicular and do not touch.
    """

    model = layout(
        column(
            (0.25, 0.75),
            area(1),
            row(
                (0.5, 0.5),
                column(
                    (0.5, 0.5),
                    row((0.5, 0.5), column((2 / 3, 1 / 3), area(10), area(11)), area(12)),
                    area(13),
                ),
                area(14),
            ),
        )
    )
    down = Handle(0, (1,), 0)
    across = Handle(0, (1, 0, 0, 0), 0)

    assert rectangles(model)[10][2:] == pytest.approx((0.25, 0.5))
    assert rectangles(model)[14][:2] == pytest.approx((0.5, 0.25))
    assert model.borders(down) == (down,)
    assert model.borders(across) == (across,)


def test_borders_stops_at_the_window_edge() -> None:
    """`PL-HJPY` Q4: two windows' borders can be collinear on a screen and are unrelated."""

    tree = column((0.5, 0.5), row((0.5, 0.5), area(1), area(2)), row((0.5, 0.5), area(3), area(4)))
    second = column(
        (0.5, 0.5), row((0.5, 0.5), area(5), area(6)), row((0.5, 0.5), area(7), area(8))
    )
    model = layout(tree, second)

    assert model.borders(Handle(1, (0,), 0)) == (Handle(1, (0,), 0), Handle(1, (1,), 0))

    moved = model.resize(Handle(0, (0,), 0), 0.25)

    assert moved.windows[1] == model.windows[1]


def test_span_is_where_a_handles_split_begins_and_ends_in_its_window() -> None:
    """A row in the lower part of the right half spans that half, from 0.5 to 1.0 across.

    What the adapter reads to turn a drag inside one splitter into a position
    in the window (`PL-W9P6`), so each span is checked against the Areas'
    rectangles as `rectangles` works them out, not against the model.
    """

    model = layout(
        row((0.5, 0.5), area(1), column((0.25, 0.75), area(2), row((0.4, 0.6), area(3), area(4))))
    )
    placed = rectangles(model)

    assert model.span(Handle(0, (), 0)) == (0.0, 1.0)
    assert model.span(Handle(0, (1,), 0)) == (placed[2][1], placed[3][3]) == (0.0, 1.0)
    assert model.span(Handle(0, (1, 1), 0)) == (placed[3][0], placed[4][2]) == (0.5, 1.0)

    with pytest.raises(NotInLayout, match="no border at window 0"):
        model.span(Handle(0, (0,), 0))

    with pytest.raises(TypeError, match="addressed by a Handle"):
        model.span((0, (), 0))  # type: ignore[arg-type]


def test_a_border_cannot_move_onto_or_past_a_neighbouring_border() -> None:
    """The model holds no minimum sizes, so its limit is that every child keeps some size.

    On a line, the tightest of the handles it holds decides. The two rows'
    borders at one half are one line; the upper row's could go anywhere, but
    the lower row's meets its neighbour at a quarter, so moving the line to
    0.2 would leave no room for Area 4, which is the Area named.
    """

    model = layout(
        column(
            (0.5, 0.5),
            row((0.5, 0.5), area(1), area(2)),
            row((0.25, 0.25, 0.5), area(3), area(4), area(5)),
        )
    )

    with pytest.raises(LayoutRefused, match="no room for Area 4"):
        model.resize(Handle(0, (0,), 0), 0.2)

    with pytest.raises(LayoutRefused, match="no room for Area 2"):
        model.resize(Handle(0, (1,), 1), 1.0)

    with pytest.raises(LayoutRefused, match="no room for Areas 3, 4 and 5"):
        model.resize(Handle(0, (), 0), 1.0)

    for position in (math.nan, math.inf, -math.inf):
        with pytest.raises(LayoutRefused, match="cannot move to"):
            model.resize(Handle(0, (0,), 0), position)


# --- Swap, set_view, unknown kinds ------------------------------------------------


def test_swap_exchanges_places_and_each_area_keeps_its_id_and_view() -> None:
    """`PL-TH35` Q10: a swap moves each View with what is kept for it; the places keep their sizes.

    Across windows too, since ids are unique across them (`PL-HJPY` Q3).
    """

    model = LayoutModel(
        (Window(row((0.3, 0.7), area(1, CHART), area(2, WASH_IN))), Window(area(3, ACCOUNTING))),
        AreaId(4),
    )

    swapped = model.swap(AreaId(1), AreaId(2))
    across = model.swap(AreaId(3), AreaId(1))

    assert swapped.windows[0].tree == row((0.3, 0.7), area(2, WASH_IN), area(1, CHART))
    assert across.windows == (
        Window(row((0.3, 0.7), area(3, ACCOUNTING), area(2, WASH_IN))),
        Window(area(1, CHART)),
    )

    with pytest.raises(LayoutRefused, match="cannot be swapped with itself"):
        model.swap(AreaId(1), AreaId(1))


def test_set_view_changes_the_kind_and_nothing_else() -> None:
    model = layout(row((0.5, 0.5), area(1), area(2)))

    changed = model.set_view(AreaId(2), ACCOUNTING)

    assert changed.windows[0].tree == row((0.5, 0.5), area(1), area(2, ACCOUNTING))
    assert changed.next_area_id == model.next_area_id


def test_unknown_kinds_names_the_areas_whose_view_is_not_registered() -> None:
    """`PL-R1WQ` Q2: membership is a question asked with the registry's tags passed in."""

    model = layout(row((0.5, 0.5), area(1, CHART), area(2, ViewKind("retired_view"))))

    assert model.unknown_kinds({"concentration_chart"}) == (area(2, ViewKind("retired_view")),)
    assert model.unknown_kinds(frozenset({"concentration_chart", "retired_view"})) == ()

    with pytest.raises(TypeError, match="known is a set"):
        model.unknown_kinds("concentration_chart")  # type: ignore[arg-type]


# --- What every operation shares --------------------------------------------------


def test_every_operation_leaves_the_layout_it_was_called_on_as_it_was() -> None:
    """The layout is a value: trying an operation is how a menu asks whether it is available."""

    model = layout(column((0.5, 0.5), row((0.5, 0.5), area(1), area(2)), area(3)))
    before = layout_to_json(model)

    model.split(AreaId(3), ROW, 0.5)
    model.join(AreaId(1), AreaId(2))
    model.resize(Handle(0, (), 0), 0.25)
    model.swap(AreaId(1), AreaId(3))
    model.set_view(AreaId(2), WASH_IN)

    assert layout_to_json(model) == before


def test_every_operation_works_on_sizes_the_reader_accepts_at_the_edge_of_the_tolerance() -> None:
    """A file may hold sizes up to `LAYOUT_SIZE_SUM_TOLERANCE` off one, which no operation inherits.

    Each split here misses one by just under the tolerance: no code here
    writes such sizes, and the reader accepts them as written. The operation
    beside each once
    carried the sum past the tolerance by its own rounding and raised
    `InvalidLayout`, which no operation's Raises list names. Each split an
    operation rebuilds is now rescaled to sum to one first, or has its sizes
    worked out afresh from where its borders lie, so the result sums to one
    and reads back equal.
    """

    def joined(model: LayoutModel) -> LayoutModel:
        return model.join(AreaId(1), AreaId(2))

    def dragged(model: LayoutModel) -> LayoutModel:
        return model.resize(Handle(0, (), 0), 0.1)

    def cut(model: LayoutModel) -> LayoutModel:
        return model.split(AreaId(2), ROW, 0.3)[0]

    cases = (
        ([0.15374160573120305, 0.14373238441867855, 0.7025260108501183], joined),
        ([0.39159593793052766, 0.4750217800158873, 0.133382283053585], dragged),
        ([0.1862721291969395, 0.5213377493443648, 0.29239012045869567], cut),
    )

    for sizes, operation in cases:
        tree = {
            "split": "row",
            "sizes": sizes,
            "children": [{"area": number, "view": "concentration_chart"} for number in (1, 2, 3)],
        }
        document = {
            "schema_version": LAYOUT_SCHEMA_VERSION,
            "next_area_id": 4,
            "windows": [{"tree": tree}],
        }

        assert 0.99 * LAYOUT_SIZE_SUM_TOLERANCE < abs(math.fsum(sizes) - 1)

        result = operation(layout_from_json(json.dumps(document)))

        assert math.fsum(split_at(result, ()).sizes) == pytest.approx(1, abs=1e-15)
        assert layout_from_json(layout_to_json(result)) == result


def test_a_reference_the_layout_does_not_hold_is_refused() -> None:
    """A stale id or handle is the caller's error, and says which."""

    model = layout(column((0.5, 0.5), row((0.5, 0.5), area(1), area(2)), area(3)))

    with pytest.raises(NotInLayout, match="no Area of this layout holds the id 9"):
        model.set_view(AreaId(9), CHART)

    for stale in (Handle(1, (), 0), Handle(0, (), 1), Handle(0, (1,), 0), Handle(0, (0, 0), 0)):
        with pytest.raises(NotInLayout, match="no border at window"):
            model.borders(stale)

    with pytest.raises(InvalidLayout, match="counts from zero"):
        Handle(0, (-1,), 0)


def test_a_bare_value_is_refused_where_a_checked_type_is_required() -> None:
    """`mypy` reads `src/` and not a caller typed `Any`, so the types are required at run time.

    A bare `int` would find the Area it equals, and `True` the Area with id 1;
    both are refused as the programming error they are, before anything is
    looked up. The values a layout is built from check theirs the same way,
    so a part of the wrong type is refused before a layout holds it.
    """

    with pytest.raises(TypeError, match="an Area's id is an AreaId"):
        Area(1, CHART)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="an Area's view is a ViewKind"):
        Area(AreaId(1), "concentration_chart")  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="a split's orientation is an Orientation"):
        Split("row", (0.5, 0.5), (area(1), area(2)))  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="a split's children are a tuple"):
        Split(ROW, (0.5, 0.5), [area(1), area(2)])  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="a split's sizes are a tuple"):
        Split(ROW, [0.5, 0.5], (area(1), area(2)))  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="a window's tree is an Area or a Split"):
        Window("concentration_chart")  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="a layout's windows are a tuple"):
        LayoutModel([Window(area(1))], AreaId(2))  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="a layout's window is a Window"):
        LayoutModel((area(1),), AreaId(2))  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="a layout's next_area_id is an AreaId"):
        LayoutModel((Window(area(1)),), 2)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="a View kind is a ViewKind"):
        LayoutModel.single_area("concentration_chart")  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="a handle's path is a tuple"):
        Handle(0, [0], 0)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="a handle's window is an int"):
        Handle(True, (), 0)

    model = layout(row((0.5, 0.5), area(1), area(2)))

    with pytest.raises(TypeError, match="addressed by an AreaId"):
        model.area(1)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="addressed by an AreaId"):
        model.join(True, AreaId(2))  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="addressed by an AreaId"):
        model.swap(1, 1)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="a View kind is a ViewKind"):
        model.set_view(AreaId(1), "wash_in")  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="at is a float"):
        model.split(AreaId(1), ROW, 1)

    with pytest.raises(TypeError, match="orientation is an Orientation"):
        model.split(AreaId(1), "row", 0.5)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="position is a float"):
        model.resize(Handle(0, (), 0), 0)

    with pytest.raises(TypeError, match="addressed by a Handle"):
        model.borders((0, (), 0))  # type: ignore[arg-type]


# --- The serialized root ----------------------------------------------------------


def test_the_serialized_root_holds_a_window_set_at_version_one() -> None:
    """`PL-HJPY`: a root that gained a window set later would be a migration of learners' files."""

    written = layout_to_dict(LayoutModel.single_area(CHART))

    assert LAYOUT_SCHEMA_VERSION == 2
    assert written == {
        "next_area_id": 2,
        "windows": [{"tree": {"area": 1, "view": "concentration_chart"}}],
    }
    assert layout_to_json(LayoutModel.single_area(CHART)).startswith('{\n  "schema_version": 2,')


def test_a_layout_survives_the_round_trip_through_json_exactly() -> None:
    """Every operation's result, across two windows, read back equal to what was written."""

    model, added = LayoutModel.single_area(CHART).split(AreaId(1), ROW, 0.7)
    model, _ = model.split(added, COLUMN, 1 / 3)
    model = model.resize(Handle(0, (), 0), 0.61803398875)
    model = model.set_view(added, ACCOUNTING)
    model = LayoutModel(model.windows + (Window(area(9, WASH_IN)),), AreaId(10))

    assert layout_from_json(layout_to_json(model)) == model
    assert layout_from_dict(layout_to_dict(model)) == model
    assert layout_to_json(layout_from_json(layout_to_json(model))) == layout_to_json(model)


def test_rectangle_is_where_an_area_lies_in_its_window() -> None:
    """Worked by hand: Area 3 takes the right 0.75 of the window and the lower 0.6 of that."""

    model = layout(row((0.25, 0.75), area(1), column((0.4, 0.6), area(2), area(3))))

    assert model.rectangle(AreaId(3)) == Rectangle(0, 0.25, pytest.approx(0.4), 1.0, 1.0)
    assert model.rectangle(AreaId(1)) == Rectangle(0, 0.0, 0.0, 0.25, 1.0)

    with pytest.raises(NotInLayout, match="no Area of this layout holds the id 9"):
        model.rectangle(AreaId(9))


def test_neighbours_lists_each_area_an_edge_meets_by_side_and_whether_it_could_join() -> None:
    """In row[1, column[2, 3]], Area 1 meets both on its right, and neither along a whole edge."""

    model = layout(row((0.5, 0.5), area(1), column((0.5, 0.5), area(2), area(3))))

    assert model.neighbours(AreaId(1)) == (
        Neighbour(AreaId(2), Side.RIGHT, whole_edge=False),
        Neighbour(AreaId(3), Side.RIGHT, whole_edge=False),
    )
    assert model.neighbours(AreaId(2)) == (
        Neighbour(AreaId(1), Side.LEFT, whole_edge=False),
        Neighbour(AreaId(3), Side.BELOW, whole_edge=True),
    )
    assert model.neighbours(AreaId(3)) == (
        Neighbour(AreaId(1), Side.LEFT, whole_edge=False),
        Neighbour(AreaId(2), Side.ABOVE, whole_edge=True),
    )


def test_edges_gives_the_nearest_border_on_each_side_that_has_one() -> None:
    """In row[1, column[2, 3], 4], Area 2 has the row's side borders and the column's lower one."""

    model = layout(row((0.25, 0.5, 0.25), area(1), column((0.5, 0.5), area(2), area(3)), area(4)))

    assert model.edges(AreaId(1)) == ((Side.RIGHT, Handle(0, (), 0)),)
    assert model.edges(AreaId(2)) == (
        (Side.LEFT, Handle(0, (), 0)),
        (Side.RIGHT, Handle(0, (), 1)),
        (Side.BELOW, Handle(0, (1,), 0)),
    )
    assert model.edges(AreaId(3)) == (
        (Side.LEFT, Handle(0, (), 0)),
        (Side.ABOVE, Handle(0, (1,), 0)),
        (Side.RIGHT, Handle(0, (), 1)),
    )
    assert model.edges(AreaId(4)) == ((Side.LEFT, Handle(0, (), 1)),)

    for area_id in (1, 2, 3, 4):
        for _, handle in model.edges(AreaId(area_id)):
            assert handle in model.handles()


def test_edges_of_the_only_area_is_empty_and_an_unknown_area_is_refused() -> None:
    model = LayoutModel.single_area(CHART)

    assert model.edges(AreaId(1)) == ()

    with pytest.raises(NotInLayout):
        model.edges(AreaId(9))


def test_two_areas_that_meet_only_at_a_corner_are_not_neighbours() -> None:
    """In a two by two grid, the diagonal Areas share a point and no edge."""

    model = layout(
        row((0.5, 0.5), column((0.5, 0.5), area(1), area(2)), column((0.5, 0.5), area(3), area(4)))
    )

    assert model.neighbours(AreaId(1)) == (
        Neighbour(AreaId(3), Side.RIGHT, whole_edge=True),
        Neighbour(AreaId(2), Side.BELOW, whole_edge=True),
    )
    assert AreaId(1) not in {neighbour.area_id for neighbour in model.neighbours(AreaId(4))}


def test_a_lone_area_has_no_neighbours() -> None:
    assert LayoutModel.single_area(CHART).neighbours(AreaId(1)) == ()


def test_edges_gives_the_nearest_border_when_a_side_is_bordered_at_two_depths() -> None:
    """In row[column[row[2, 3], 4], 5], Area 2's right border is the inner row's, not the root's.

    Both borders lie to Area 2's right. The inner row's border moves only Area 2's right
    side. The root's border moves the whole left column.
    """

    model = layout(
        row((0.5, 0.5), column((0.5, 0.5), row((0.5, 0.5), area(2), area(3)), area(4)), area(5))
    )

    assert model.edges(AreaId(2)) == (
        (Side.RIGHT, Handle(0, (0, 0), 0)),
        (Side.BELOW, Handle(0, (0,), 0)),
    )
