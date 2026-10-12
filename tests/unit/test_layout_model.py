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
from anesthesia_sim.layout.model import BORDER_ALIGNMENT_TOLERANCE, Handle, LayoutModel
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

    With two forms, whether two Areas were next to each other in one split -
    which is what `join` asks - would depend on how the tree was built rather
    than on where they are. The form is one only where no four Areas meet at
    a point: where they do, either cut through the point can be the outer one,
    which `test_where_four_areas_meet_a_join_depends_on_which_cut_came_first`
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
    geometry below confirms, and sit in different splits; the tree refuses
    rather than return a layout other than the one asked for, and the layout
    it was asked of is unchanged.
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

    with pytest.raises(LayoutRefused, match="only where they sit next to each other"):
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


def test_where_four_areas_meet_a_join_depends_on_which_cut_came_first() -> None:
    """A 2x2 grid is two trees, and the one form a tree takes does not choose between them.

    Cut across first, the grid is a column of two rows; cut down first, a row
    of two columns. The four rectangles are the same, but which two Areas sit
    in one split differs, so joining the top-left Area to the one below it is
    refused in the first and allowed in the second, and joining it to the one
    beside it the reverse. This holds today's behaviour. Whether a join should
    re-slice a junction where four Areas meet, so that both are allowed, is an
    open decision filed as `PL-G60V`.
    """

    across_first = layout(
        column((0.5, 0.5), row((0.5, 0.5), area(1), area(2)), row((0.5, 0.5), area(3), area(4)))
    )
    down_first = layout(
        row((0.5, 0.5), column((0.5, 0.5), area(1), area(3)), column((0.5, 0.5), area(2), area(4)))
    )

    assert rectangles(across_first) == rectangles(down_first)

    with pytest.raises(LayoutRefused, match="only where they sit next to each other"):
        across_first.join(AreaId(1), AreaId(3))

    with pytest.raises(LayoutRefused, match="only where they sit next to each other"):
        down_first.join(AreaId(1), AreaId(2))

    assert down_first.join(AreaId(1), AreaId(3)).windows[0].tree == row(
        (0.5, 0.5), area(1), column((0.5, 0.5), area(2), area(4))
    )
    assert across_first.join(AreaId(1), AreaId(2)).windows[0].tree == column(
        (0.5, 0.5), area(1), row((0.5, 0.5), area(3), area(4))
    )


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


def test_a_drag_keeps_each_childs_proportions_so_a_border_inside_one_moves() -> None:
    """Where this differs from Blender's border drag, held as it is until `PL-5HSG` decides.

    The root border here divides Area 1 from a column whose upper row holds
    Areas 2 and 4. Dragged from 0.5 to 0.25, the column widens and its rows
    keep their proportions, so Area 4 widens from 0.25 to 0.375 of the
    window and the border between Areas 2 and 4 moves from 0.75 to 0.625,
    though it lies on no moved line. Blender moves only the vertices on the
    dragged line (`area_move_apply_do`), so there Area 4 would keep its
    width; `docs/interface-provenance.md` names the difference.
    """

    model = layout(
        row((0.5, 0.5), area(1), column((0.5, 0.5), row((0.5, 0.5), area(2), area(4)), area(3)))
    )

    moved = model.resize(Handle(0, (), 0), 0.25)

    assert rectangles(model)[4] == (0.75, 0.0, 1.0, 0.5)
    assert rectangles(moved)[4] == pytest.approx((0.625, 0.0, 1.0, 0.5))
    assert rectangles(moved)[2] == pytest.approx((0.25, 0.0, 0.625, 0.5))
    assert split_at(moved, (1, 0)).sizes == (0.5, 0.5)


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

    The upper row's middle Area is a millionth of a millionth of the window
    wide, so both of its borders are on the line through the lower row's.
    Moving the line moves both, which leaves that Area no room, so the drag
    is refused and names it, where it once moved one of the two and left
    the other where it was.
    """

    sliver = 1e-12
    model = layout(
        column(
            (0.5, 0.5),
            row((0.5, sliver, 0.5 - sliver), area(1), area(2), area(3)),
            row((0.5, 0.5), area(4), area(5)),
        )
    )
    lower = Handle(0, (1,), 0)

    assert model.borders(lower) == (Handle(0, (0,), 0), Handle(0, (0,), 1), lower)

    for position in (0.5 + sliver / 2, 0.4):
        with pytest.raises(LayoutRefused, match="would leave no room for Area 2"):
            model.resize(lower, position)


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


def test_a_border_cannot_move_onto_or_past_a_neighbouring_border() -> None:
    """Without minimum sizes (`PL-K285`'s) the limit is that every child keeps some size.

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
    `InvalidLayout`, which no operation's Raises list names; each split an
    operation rebuilds is now rescaled to sum to one first, so the result
    sums to one and reads back equal.
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
        document = {"schema_version": 1, "next_area_id": 4, "windows": [{"tree": tree}]}

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

    assert LAYOUT_SCHEMA_VERSION == 1
    assert written == {
        "next_area_id": 2,
        "windows": [{"tree": {"area": 1, "view": "concentration_chart"}}],
    }
    assert layout_to_json(LayoutModel.single_area(CHART)).startswith('{\n  "schema_version": 1,')


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
