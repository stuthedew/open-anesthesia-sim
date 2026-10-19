"""The layout as one value: every window's tree, and the operations a reader performs on it.

**The model is the layout's source of truth, not the widgets** (`PL-C842`).
`QSplitter.saveState()` was disqualified for the job because it records no View
identity: measured 2026-09-16 on PySide6 6.11.2, a three-pane splitter saves the
same 35 bytes for the same three children in reverse order, and
`restoreState()` reports success restoring them into a two-pane splitter. So
the layout is held here, as plain values a test can build, compare and print
with no `QApplication`, and one adapter module (`PL-W9P6`) builds the widget
tree from it. Nothing in this package imports Qt, which
`tools/import_boundary_check.py` enforces.

**A value, not an object that changes.** Every operation returns a new
`LayoutModel` and leaves the one it was called on as it was. A refused
operation raises `LayoutRefused` and so changes nothing anywhere, which also
makes trying an operation the way to ask whether it is available: the message
is the reason a menu shows beside the unavailable entry (`PL-M352`).

**Several windows from the first version** (`PL-HJPY`, ratified 2026-09-27).
`windows[0]` is the main window, and a layout always has one. A tree is a
rectangle and cannot span two windows, so each window has its own. Area ids
are unique across all of them and allocated from `next_area_id`, which only
rises, so an id is never handed out twice and state kept per Area id can never
be resurrected under another Area. `PL-HJPY` Q3 has the Workspace store that
counter; it is held here because the layout is what allocates, and
`layout/serialization.py` writes it beside the windows, where `PL-HJPY`'s
illustrated file has it.

**What the tree cannot express is refused, never approximated** (`PL-3J2P`).
A splitter tree is strictly less expressive than Blender's vertex-and-edge
screen. In Blender, joining two Areas that share a whole edge can leave a
pinwheel: five Areas that no straight cut divides. A tree cannot hold one, so
`join` refuses such a join. The limit then shows as an unavailable operation
rather than as a different layout from the one the reader asked for. `join`
also refuses a result that would nest a split deeper than
`TREE_DEPTH_MAXIMUM`, as `split` does. Every other join of two Areas sharing a
whole edge is taken, whichever splits they sit in (`PL-G60V`), because a
reader sees the rectangles and never the tree.

**What is not here yet.** Minimum sizes, the clamp on a drag and `too_small()`
are `PL-K285`'s; taking an Area into its own window is a later operation of
`ROADMAP.md` item 34. Closing an Area is a join that gives its place to a
neighbour, which the adapter's Area menu asks `join` for (`PL-2KXB`); what a Workspace carries beyond its layout
is `PL-WV9K`'s; and the file is `PL-SSQW`'s.
"""

from __future__ import annotations

import math
from bisect import bisect_left
from collections.abc import Iterator, Mapping
from collections.abc import Set as AbstractSet
from dataclasses import dataclass
from enum import Enum
from itertools import pairwise, product
from typing import Final

from anesthesia_sim.core.checked_number import shown
from anesthesia_sim.layout.exceptions import InvalidLayout, LayoutRefused, NotInLayout
from anesthesia_sim.layout.tree import (
    AREA_ID_MAXIMUM,
    TREE_DEPTH_MAXIMUM,
    Area,
    AreaId,
    Node,
    Orientation,
    Split,
    ViewKind,
    Window,
    areas_in,
)

__all__ = [
    "BORDER_ALIGNMENT_TOLERANCE",
    "MAIN_WINDOW",
    "Handle",
    "LayoutModel",
    "Neighbour",
    "Rectangle",
    "Side",
]

# How far apart, as a fraction of the window, two borders may lie and still be
# read as one line by `LayoutModel.borders()`. It absorbs the rounding of the
# arithmetic that places them - a border moved to a position lands within a
# few units in the last place of it - and nothing visible: two borders a pixel
# apart are two lines, as two edges with separate vertices are in Blender.
BORDER_ALIGNMENT_TOLERANCE: Final = 1e-9

# The main window's index in `LayoutModel.windows`. A layout always has this
# window, and only it may hold the per-substance tier of the unconditional
# set (`PL-HJPY`, `app/unconditional_set.py`).
MAIN_WINDOW: Final = 0


@dataclass(frozen=True, slots=True)
class Handle:
    """A border between two neighbouring children of one split: what a reader drags.

    Addressed by where it sits in one layout value: the window, the path of
    child indices from that window's tree down to the split, and the gap
    between the split's children - `index` 0 is the border between children 0
    and 1. A handle is read against the layout it was taken from, and
    `LayoutModel.handles()` lists that layout's.

    Raises:
        TypeError: a field is not an `int`, or is a `bool`, or `path` is not a
            tuple of them.
        InvalidLayout: a field is negative.
    """

    window: int
    path: tuple[int, ...]
    index: int

    def __post_init__(self) -> None:
        if not isinstance(self.path, tuple):
            raise TypeError(f"a handle's path is a tuple, not {type(self.path).__name__}")

        for name, value in (("window", self.window), ("index", self.index)) + tuple(
            ("path entry", step) for step in self.path
        ):
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"a handle's {name} is an int, not {type(value).__name__}")

            if value < 0:
                raise InvalidLayout(f"a handle's {name} counts from zero, not {shown(value)}")


@dataclass(frozen=True, slots=True)
class Rectangle:
    """Where an Area lies in its window, in fractions of the window.

    `left` and `right` are x positions from the window's left edge, and `top`
    and `bottom` are y positions from its top edge.
    """

    window: int
    left: float
    top: float
    right: float
    bottom: float


class Side(Enum):
    """Which side of an Area a neighbour lies on."""

    LEFT = "left"
    ABOVE = "above"
    RIGHT = "right"
    BELOW = "below"


@dataclass(frozen=True, slots=True)
class Neighbour:
    """An Area beside another, the side of it that it lies on, and whether they could join.

    `whole_edge` is true where the two share the whole of one edge, so that
    together they make a rectangle, which is what `join` asks first. A join
    that `whole_edge` allows can still be refused, as `join` says.
    """

    area_id: AreaId
    side: Side
    whole_edge: bool


@dataclass(frozen=True, slots=True)
class _Place:
    """Where a node sits: its window, and the path of child indices from that window's tree."""

    window: int
    path: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class _Segment:
    """Where a handle lies, in fractions of its window: what `borders()` and `resize()` read.

    A row's handles are vertical lines and a column's horizontal ones, so
    `across` is a row handle's x and a column handle's y, and `start` and
    `end` run along the line. `low` and `high` are where the handle's split
    begins and ends along its own axis, which `resize()` lays its children
    out between.
    """

    orientation: Orientation
    across: float
    start: float
    end: float
    low: float
    high: float


@dataclass(frozen=True, slots=True)
class _Rect:
    """A rectangle in fractions of its window: x from the left edge, y from the top."""

    left: float
    top: float
    right: float
    bottom: float

    def span(self, orientation: Orientation) -> tuple[float, float]:
        """Where the rectangle begins and ends along the axis a split of `orientation` divides."""

        if orientation is Orientation.ROW:
            return self.left, self.right

        return self.top, self.bottom

    def with_span(self, orientation: Orientation, low: float, high: float) -> _Rect:
        """The rectangle with its span along `orientation`'s axis replaced."""

        if orientation is Orientation.ROW:
            return _Rect(low, self.top, high, self.bottom)

        return _Rect(self.left, low, self.right, high)


# The whole of a window, which each window's tree divides.
_WINDOW: Final = _Rect(0.0, 0.0, 1.0, 1.0)


class _NoStraightCut(Exception):
    """No straight line crosses the whole of a region without entering a piece of it."""


class _TooDeep(Exception):
    """Slicing a region would nest splits deeper than the levels left for it."""


@dataclass(frozen=True, slots=True)
class LayoutModel:
    """Every window's tree, and the counter the next Area's id comes from.

    Raises:
        TypeError: a field is not of its declared type.
        InvalidLayout: the layout has no window; a window's tree holds a split
            deeper than `TREE_DEPTH_MAXIMUM`, which the message names with its
            path; two Areas share an id; or `next_area_id` is not above every
            id in use.
    """

    windows: tuple[Window, ...]
    next_area_id: AreaId

    def __post_init__(self) -> None:
        if not isinstance(self.windows, tuple):
            raise TypeError(f"a layout's windows are a tuple, not {type(self.windows).__name__}")

        for window in self.windows:
            if not isinstance(window, Window):
                raise TypeError(f"a layout's window is a Window, not {type(window).__name__}")

        if not isinstance(self.next_area_id, AreaId):
            raise TypeError(
                f"a layout's next_area_id is an AreaId, not {type(self.next_area_id).__name__}"
            )

        if not self.windows:
            raise InvalidLayout("a layout holds at least one window, the main window")

        # Before anything below recurses through a tree, which one too deep
        # would end in a `RecursionError` rather than in this refusal.
        for index, window in enumerate(self.windows):
            too_deep = _split_past_depth_maximum(window.tree)

            if too_deep is not None:
                raise InvalidLayout(
                    f"window {index}'s tree holds a split {len(too_deep) + 1} deep, at path "
                    f"{too_deep}, and a split sits at most {TREE_DEPTH_MAXIMUM} deep in a "
                    "window's tree"
                )

        allocated: set[AreaId] = set()

        for area in self.areas():
            if area.id in allocated:
                raise InvalidLayout(
                    f"two Areas hold the id {area.id}, and an id names one Area across all "
                    "of a layout's windows"
                )

            allocated.add(area.id)

        highest = max(allocated)

        if self.next_area_id <= highest:
            raise InvalidLayout(
                f"next_area_id is {self.next_area_id} and an Area already holds the id {highest}; "
                "the next id is above every id in use, so none is handed out twice"
            )

    @classmethod
    def single_area(cls, view: ViewKind) -> LayoutModel:
        """A layout of one window holding one Area, id 1, showing `view`.

        Raises:
            TypeError: `view` was not built as a `ViewKind`.
        """

        _require_view_kind(view)

        first = AreaId(1)

        return cls((Window(Area(first, view)),), AreaId(first + 1))

    def areas(self) -> tuple[Area, ...]:
        """Every Area: the windows in order, each window's in reading order."""

        return tuple(area for window in self.windows for area in areas_in(window.tree))

    def area(self, area_id: AreaId) -> Area:
        """The Area holding `area_id`.

        Raises:
            TypeError: `area_id` was not built as an `AreaId`.
            NotInLayout: no Area of this layout holds `area_id`.
        """

        return self._locate(area_id)[1]

    def rectangle(self, area_id: AreaId) -> Rectangle:
        """Where the Area holding `area_id` lies in its window.

        Raises:
            TypeError: `area_id` was not built as an `AreaId`.
            NotInLayout: no Area of this layout holds `area_id`.
        """

        place, _ = self._locate(area_id)
        rect = _rect_at(self.windows[place.window].tree, place.path)

        return Rectangle(place.window, rect.left, rect.top, rect.right, rect.bottom)

    def neighbours(self, area_id: AreaId) -> tuple[Neighbour, ...]:
        """The Areas whose edge meets an edge of this one for some length, by side.

        Two Areas that touch only at a corner are not neighbours. The result
        is ordered by side - left, above, right, below - and along each side
        from the top or the left. A menu reads it to list the Areas an Area
        can be joined with, and to show the ones it cannot (`PL-2KXB`).

        Raises:
            TypeError: `area_id` was not built as an `AreaId`.
            NotInLayout: no Area of this layout holds `area_id`.
        """

        place, _ = self._locate(area_id)
        tree = self.windows[place.window].tree
        own = _rect_at(tree, place.path)
        found: list[tuple[int, float, Neighbour]] = []

        for path, area in _area_paths(tree, ()):
            if area.id == area_id:
                continue

            other = _rect_at(tree, path)
            side = _side_of(own, other)

            if side is None:
                continue

            along = other.top if side in (Side.LEFT, Side.RIGHT) else other.left
            whole = _share_a_whole_edge(own, other)
            found.append((list(Side).index(side), along, Neighbour(area.id, side, whole)))

        return tuple(neighbour for _, _, neighbour in sorted(found, key=lambda entry: entry[:2]))

    def handles(self) -> tuple[Handle, ...]:
        """Every handle: the windows in order, each window's splits depth first."""

        return tuple(
            handle
            for index, window in enumerate(self.windows)
            for handle in _segments(index, window.tree)
        )

    def borders(self, handle: Handle) -> tuple[Handle, ...]:
        """The border `handle` belongs to: every handle on its line that it connects to.

        `PL-3J2P` measured the one thing a splitter tree costs against
        Blender's screen: where two borders cross, each is one line in Blender
        and dragging it moves its whole length, and a tree holds at most one of
        the two as a single handle. The answer it recorded is this query rather
        than a change of representation - the handles collinear with
        `handle` and connected to it end to end, found by following them from
        one to the next as Blender's `screen_geom_select_connected_edge` does
        (`source/blender/editors/screen/screen_geometry.cc`, `blender/blender`
        `main`, read 2026-10-12), so a drag moves them together. Each handle
        is compared with the one that reached it rather than with `handle`,
        so the border is the same set whichever of its handles it is asked
        from. The result includes `handle` and is ordered along the line, top
        to bottom or left to right.

        **It stops at the window's edge**, because each window has its own
        tree, and two windows' borders can be collinear on a screen and still
        be unrelated (`PL-HJPY` Q4).

        **It reads the line from where the borders are.** Blender follows
        shared vertices, and its border drag merges none - `area_move_exit` in
        `screen_ops.cc` removes duplicate edges and leaves the vertices alone -
        so two edges a drag brings into line stay two until the reader merges
        them on purpose. Here two borders brought into line, to within
        `BORDER_ALIGNMENT_TOLERANCE`, are one line from then on, since a tree
        has no vertices to keep them apart.

        Raises:
            TypeError: `handle` is not a `Handle`.
            NotInLayout: `handle` is not a border of this layout.
        """

        segments = self._segments_of(handle)

        return _chain(handle, segments)

    def span(self, handle: Handle) -> tuple[float, float]:
        """Where `handle`'s split begins and ends along its axis, in fractions of its window.

        A row's span runs from left to right, and a column's from top to
        bottom. A toolkit reports a drag as a share of the one splitter that
        was dragged. The adapter (`app/area_layout.py`) reads this span to
        turn that share into the position in the window that `resize()`
        takes, so it does not work the split's place out a second time.

        Raises:
            TypeError: `handle` is not a `Handle`.
            NotInLayout: `handle` is not a border of this layout.
        """

        segment = self._segments_of(handle)[handle]

        return segment.low, segment.high

    def split(
        self, area_id: AreaId, orientation: Orientation, at: float
    ) -> tuple[LayoutModel, AreaId]:
        """Cut an Area in two; return the new layout and the new Area's id.

        The cut runs across the Area at `at`, a fraction of its width for a
        `ROW` and of its height for a `COLUMN`: the Area keeps the part before
        the cut, and a new Area takes the part after it, showing the same kind
        of View, as Blender's split duplicates its editor and `PL-TH35` Q10 has
        the new Area start from a copy of the source's state. Splitting an
        Area along the axis its split already divides adds a child to that
        split rather than nesting another, which is the one form a tree takes
        (`layout/tree.py`); that split's sizes are rescaled to sum to one
        first (`_summing_to_one`).

        Raises:
            TypeError: an argument is not of its declared type; `at` is not a
                `float`.
            NotInLayout: no Area of this layout holds `area_id`.
            LayoutRefused: `at` does not lie strictly between 0 and 1, or is
                so close to one end that a part would have no size; the cut
                would nest a split deeper than `TREE_DEPTH_MAXIMUM`, which a
                cut along the axis of the split holding the Area never does,
                since it adds a child rather than a level; or `next_area_id`
                has reached `AREA_ID_MAXIMUM`, which it cannot pass while it
                stays above every id in use, so no id is left to hand out.
        """

        if not isinstance(orientation, Orientation):
            raise TypeError(f"orientation is an Orientation, not {type(orientation).__name__}")

        _require_float("at", at)

        place, source = self._locate(area_id)
        measure = "width" if orientation is Orientation.ROW else "height"

        if not 0 < at < 1:
            raise LayoutRefused(
                f"a cut at {at!r} of Area {area_id}'s {measure} falls outside it: a cut lies "
                "strictly between 0 and 1 of the Area"
            )

        if self.next_area_id == AREA_ID_MAXIMUM:
            raise LayoutRefused(
                f"this layout cannot make another Area: the next id it would hand out, "
                f"{self.next_area_id}, is the largest an Area id can be, and its counter, which "
                "stays above every id in use, cannot pass it"
            )

        added = Area(self.next_area_id, source.view)
        tree = self.windows[place.window].tree
        parent = _place_of_parent(place)
        holder = _node_at(tree, parent.path) if parent is not None else None

        if parent is not None and isinstance(holder, Split) and holder.orientation is orientation:
            position = place.path[-1]
            sizes = _summing_to_one(holder.sizes)
            kept = sizes[position] * at
            given = sizes[position] - kept

            if kept <= 0 or given <= 0:
                raise LayoutRefused(
                    f"a cut at {at!r} of Area {area_id}'s {measure} leaves a part with no size"
                )

            divided = Split(
                orientation,
                sizes[:position] + (kept, given) + sizes[position + 1 :],
                holder.children[:position] + (source, added) + holder.children[position + 1 :],
            )
            tree = _replaced(tree, parent.path, divided)
        else:
            # The cut nests a split where the Area was, one level below the
            # splits already above it.
            depth = len(place.path) + 1

            if depth > TREE_DEPTH_MAXIMUM:
                raise LayoutRefused(
                    f"a {orientation.value} split of Area {area_id} would sit {depth} deep, and "
                    f"a split sits at most {TREE_DEPTH_MAXIMUM} deep in a window's tree"
                )

            tree = _replaced(tree, place.path, Split(orientation, (at, 1 - at), (source, added)))

        return (
            LayoutModel(self._with_tree(place.window, tree), AreaId(self.next_area_id + 1)),
            added.id,
        )

    def join(self, keep: AreaId, remove: AreaId) -> LayoutModel:
        """Merge two neighbouring Areas into one: `keep` takes `remove`'s space.

        `keep` keeps its View; `remove` and its View leave the layout, and its
        id is not handed out again. Two Areas join where they share the whole
        of one edge, so that together they make a rectangle. Blender's
        `area_getorientation` (`source/blender/editors/screen/screen_edit.cc`,
        `blender/blender` `main`, read 2026-10-18) also decides from the two
        Areas' corners alone, though it accepts part of an edge and trims the
        rest (`docs/interface-provenance.md`).

        **Whether a join is taken depends on the rectangles alone, never on
        the order the splits were made in** (`PL-G60V`). Where four Areas meet
        at a point, two trees hold the same rectangles (`layout/tree.py`), and
        two Areas that share an edge may sit in different splits. So the join
        does not look for the pair in one split. It re-slices the region of
        the lowest split holding both (`_resliced`): it merges the two Areas
        into one rectangle and divides the region again by straight cuts, the
        only way a tree divides anything. Every Area keeps its rectangle, and
        the splits built again take their sizes from where their borders lie.

        It tries first with each subtree beside the pair kept whole, so that
        a join changes no split it need not. A subtree's own border can lie
        on the only line that divides the region, though, and then the join
        is tried again from every Area in the region, so that whether it is
        taken depends on the rectangles alone.

        A result can need one level of splits more than the tree held. Where
        that passes `TREE_DEPTH_MAXIMUM` inside the lowest split, the region of
        each split above it is re-sliced in turn, up to the whole window,
        because cutting a larger region the other way first can fit. So the
        depth refusal also depends on the rectangles alone.

        Raises:
            TypeError: an argument was not built as an `AreaId`.
            NotInLayout: no Area of this layout holds one of the ids.
            LayoutRefused: the two ids are the same; the Areas are in
                different windows; they do not share the whole of one edge;
                no straight cut divides the Areas the join would leave, which
                is `PL-3J2P`'s refusal of what a tree cannot hold, such as the
                pinwheel; or every tree holding the result, re-sliced from any
                split up to the whole window, would nest a split deeper than
                `TREE_DEPTH_MAXIMUM`, which `split` refuses as well.
        """

        kept, _ = self._locate(keep)
        removed, _ = self._locate(remove)

        if keep == remove:
            raise LayoutRefused(f"Area {keep} cannot be joined to itself")

        if kept.window != removed.window:
            raise LayoutRefused(
                f"Area {keep} and Area {remove} are in different windows, and a join merges "
                "two Areas of one window"
            )

        tree = self.windows[kept.window].tree
        common = _common_prefix(kept.path, removed.path)
        holder = _split_at(tree, common)
        region = _rect_at(tree, common)
        whole = _pieces(holder, region, {keep, remove}, opened=False)
        kept_rect = next(rect for rect, node in whole if _is_area(node, keep))
        removed_rect = next(rect for rect, node in whole if _is_area(node, remove))

        if not _share_a_whole_edge(kept_rect, removed_rect):
            raise LayoutRefused(
                f"Area {keep} and Area {remove} cannot be joined: the layout joins two Areas "
                "only where they sit next to each other along the whole of one edge, so that "
                "together they make a rectangle, and these do not"
            )

        merged = _Rect(
            min(kept_rect.left, removed_rect.left),
            min(kept_rect.top, removed_rect.top),
            max(kept_rect.right, removed_rect.right),
            max(kept_rect.bottom, removed_rect.bottom),
        )

        # A tree too deep for the lowest split's region can fit when a region
        # higher up is cut first the other way, so each split above is tried
        # in turn, up to the whole window. Where the lowest region has no
        # straight cut, none above it has one either.
        for level in range(len(common), -1, -1):
            path = common[:level]
            holder = _split_at(tree, path)
            region = _rect_at(tree, path)
            attempts = tuple(
                [
                    (merged if _is_area(node, keep) else rect, node)
                    for rect, node in _pieces(holder, region, {keep, remove}, opened=opened)
                    if not _is_area(node, remove)
                ]
                for opened in (False, True)
            )

            try:
                resliced = _resliced(tree, path, region, attempts)
            except _NoStraightCut:
                raise LayoutRefused(
                    f"Area {keep} and Area {remove} cannot be joined: no straight cut divides "
                    "the Areas the join would leave, and a layout is made only of straight cuts "
                    "across a rectangle"
                ) from None
            except _TooDeep:
                continue

            return LayoutModel(self._with_tree(kept.window, resliced), self.next_area_id)

        raise LayoutRefused(
            f"joining Area {keep} and Area {remove} would nest a split more than "
            f"{TREE_DEPTH_MAXIMUM} deep, the most a split sits in a window's tree"
        )

    def resize(self, handle: Handle, position: float) -> LayoutModel:
        """Move a border, and every handle `borders()` joins to it, to `position`.

        `position` is a fraction of the window: an x for a row's border and a y
        for a column's. **Only the borders on that line move** (`PL-5HSG`).
        Every other border keeps its place in the window, so only the Areas
        with an edge on the line change size. Blender's `area_move_apply_do`
        (`source/blender/editors/screen/screen_ops.cc`, `blender/blender`
        `main`, read 2026-10-18) does the same: it moves only the vertices
        flagged as on the dragged line. In `row[1, column[row[2, 4], 3]]`,
        dragging the root border from 0.5 to 0.25 widens Area 2 and leaves
        Area 4 a quarter of the window wide, with its border with Area 2 still
        at 0.75.

        A split's sizes are fractions of its own extent. So a split that a
        drag widens or narrows has its sizes worked out again from where its
        borders lie in the window, with the moved ones at `position`
        (`_dragged`). A split whose extent does not change and which holds no
        moved handle keeps its sizes exactly. A handle already at `position`
        is not moved, so a drag to where a border lies returns an equal layout.

        Raises:
            TypeError: `handle` is not a `Handle`, or `position` not a `float`.
            NotInLayout: `handle` is not a border of this layout.
            LayoutRefused: `position` is not finite, or would leave an Area
                beside the line with no size. That happens when `position`
                lies at or past the far edge of that Area, which is another
                border or the window's edge, or so close to it that the stored
                sizes would round the gap away, and when two handles of one split
                lie on the line, since moving both to one place leaves the
                children between them none. The message names the Areas left
                with no room. `PL-K285` adds minimum sizes, which clamp a drag
                before it gets here.
        """

        _require_float("position", position)

        segments = self._segments_of(handle)
        tree = self.windows[handle.window].tree

        if not math.isfinite(position):
            raise LayoutRefused(f"a border cannot move to {position!r}")

        # The line's handles by the split each divides, since one split can
        # hold two of them and every one is moved.
        moved: dict[tuple[int, ...], set[int]] = {}

        for member in _chain(handle, segments):
            if segments[member].across != position:
                moved.setdefault(member.path, set()).add(member.index)

        if not moved:
            return self

        return LayoutModel(
            self._with_tree(handle.window, _with_sizes(tree, (), _dragged(tree, moved, position))),
            self.next_area_id,
        )

    def swap(self, first: AreaId, second: AreaId) -> LayoutModel:
        """Exchange where two Areas sit, in one window or across two.

        Each Area keeps its id and its View, so whatever is kept per Area id
        travels with it, as `PL-TH35` Q10 has a swap move each View with its
        state. The places keep their sizes.

        Raises:
            TypeError: an argument was not built as an `AreaId`.
            NotInLayout: no Area of this layout holds one of the ids.
            LayoutRefused: the two ids are the same.
        """

        exchanged = {first: self._locate(second)[1], second: self._locate(first)[1]}

        if first == second:
            raise LayoutRefused(f"Area {first} cannot be swapped with itself")

        return LayoutModel(
            tuple(Window(_with_areas(window.tree, exchanged)) for window in self.windows),
            self.next_area_id,
        )

    def set_view(self, area_id: AreaId, view: ViewKind) -> LayoutModel:
        """Show another kind of View in an Area; its id and its place stay.

        Raises:
            TypeError: `area_id` was not built as an `AreaId`, or `view` as a
                `ViewKind`.
            NotInLayout: no Area of this layout holds `area_id`.
        """

        _require_view_kind(view)

        replaced = {area_id: Area(self._locate(area_id)[1].id, view)}

        return LayoutModel(
            tuple(Window(_with_areas(window.tree, replaced)) for window in self.windows),
            self.next_area_id,
        )

    def unknown_kinds(self, known: AbstractSet[str]) -> tuple[Area, ...]:
        """The Areas whose View kind is not in `known`, in the order `areas()` gives.

        The layout holds no list of View kinds (`PL-R1WQ` Q1): the registry's
        tags are passed in, and a test passes any set it likes. An Area named
        here is not a malformed layout - the file loads, and the adapter draws
        that Area's failure state with its tag unchanged, so a later save
        writes back what was read (`PL-R1WQ` Q2, `PL-SSQW` Q5).

        Raises:
            TypeError: `known` is not a set - a single tag, being a `str`,
                would otherwise be read as a set of its letters.
        """

        if not isinstance(known, AbstractSet):
            raise TypeError(f"known is a set of View kind tags, not {type(known).__name__}")

        return tuple(area for area in self.areas() if area.view not in known)

    def _locate(self, area_id: AreaId) -> tuple[_Place, Area]:
        """Where the Area holding `area_id` sits, and the Area.

        Raises:
            TypeError: `area_id` was not built as an `AreaId`.
            NotInLayout: no Area of this layout holds it.
        """

        if not isinstance(area_id, AreaId):
            raise TypeError(
                f"an Area is addressed by an AreaId, not {type(area_id).__name__}: build it "
                "as AreaId(...), or take it from the layout"
            )

        for index, window in enumerate(self.windows):
            for path, area in _area_paths(window.tree, ()):
                if area.id == area_id:
                    return _Place(index, path), area

        raise NotInLayout(f"no Area of this layout holds the id {area_id}")

    def _segments_of(self, handle: Handle) -> dict[Handle, _Segment]:
        """Every handle's place in `handle`'s window.

        Raises:
            TypeError: `handle` is not a `Handle`.
            NotInLayout: `handle` is not a border of this layout.
        """

        if not isinstance(handle, Handle):
            raise TypeError(f"a border is addressed by a Handle, not {type(handle).__name__}")

        if handle.window < len(self.windows):
            segments = _segments(handle.window, self.windows[handle.window].tree)

            if handle in segments:
                return segments

        raise NotInLayout(
            f"this layout has no border at window {shown(handle.window)}, split path "
            f"{tuple(shown(step) for step in handle.path)}, index {shown(handle.index)}"
        )

    def _with_tree(self, index: int, tree: Node) -> tuple[Window, ...]:
        return self.windows[:index] + (Window(tree),) + self.windows[index + 1 :]


def _require_view_kind(view: object) -> None:
    if not isinstance(view, ViewKind):
        raise TypeError(
            f"a View kind is a ViewKind, not {type(view).__name__}: build it as ViewKind(...), "
            "which checks the tag's syntax"
        )


def _require_float(name: str, value: object) -> None:
    if not isinstance(value, float):
        raise TypeError(f"{name} is a float, a fraction, not {type(value).__name__}")


def _place_of_parent(place: _Place) -> _Place | None:
    return _Place(place.window, place.path[:-1]) if place.path else None


def _split_past_depth_maximum(tree: Node) -> tuple[int, ...] | None:
    """The path to the first split, in reading order, deeper than `TREE_DEPTH_MAXIMUM`, or `None`.

    Walked with a list rather than by recursion, so a tree built in code too
    deep to recurse through is refused here rather than by a `RecursionError`,
    and the walk goes no further down any path than the first split past the
    maximum.
    """

    pending: list[tuple[tuple[int, ...], Node]] = [((), tree)]

    while pending:
        path, node = pending.pop()

        if isinstance(node, Split):
            if len(path) >= TREE_DEPTH_MAXIMUM:
                return path

            pending.extend(
                reversed([(path + (index,), child) for index, child in enumerate(node.children)])
            )

    return None


def _summing_to_one(sizes: tuple[float, ...]) -> tuple[float, ...]:
    """`sizes` divided by their exactly rounded sum: what an operation rebuilds a split from.

    A split's sizes may miss a sum of one by up to `LAYOUT_SIZE_SUM_TOLERANCE`,
    and a file this code did not write can hold such sizes, which the reader
    accepts. Arithmetic on them can carry a sum just inside the tolerance to
    just outside it, so an operation on a layout the reader accepted would
    raise `InvalidLayout`: `PL-1FT6`'s review found a join doing so. Divided
    by their sum first, the sizes miss one by a unit in the last place, the
    operation's own rounding adds a unit or two, and no operation inherits
    the last one's error. Where the sum is exactly one the division changes
    nothing; elsewhere each size moves by at most the tolerance's share of it,
    which nothing on a screen shows. This is chosen over a reader stricter
    than the in-memory check, which would refuse to read back a layout held
    in memory between the two bounds. `join` and `resize` work a split's sizes
    out afresh from where its borders lie, which sum to one as nearly, and use
    this only for a split they merge another into (`_flattened`).
    """

    total = math.fsum(sizes)

    return tuple(size / total for size in sizes)


def _dragged(
    tree: Node, moved: Mapping[tuple[int, ...], AbstractSet[int]], position: float
) -> dict[tuple[int, ...], tuple[float, ...]]:
    """The new sizes of every split a drag changes, keyed by the split's path.

    `moved` names, for each split by its path, the indices of its handles that
    move to `position`, a fraction of the window. Every other border stays
    where it lies in the window. Walking down from the window, each split's
    extent along its axis is where its parent now places it. A split whose
    extent changed, or which holds a moved handle, gets new sizes: the
    distance between each pair of neighbouring borders, with the moved ones at
    `position`, divided by its new extent. Every other split keeps its sizes,
    and is left out of the result.

    Raises:
        LayoutRefused: a child would be left with no width or height,
            because a border or an edge now lies at or past the one on the
            child's far side, or because the sizes the tree would store place
            the two together. A split whose own extent is nothing is refused
            the same way, before any size is divided by that extent.
            The message names that split's children left with no room, and
            its Areas. The first such split in depth-first order is named.
    """

    resized: dict[tuple[int, ...], tuple[float, ...]] = {}

    def visit(node: Node, path: tuple[int, ...], was: _Rect, now: _Rect) -> None:
        if isinstance(node, Area):
            return

        low, high = now.span(node.orientation)
        bounds = _boundaries(*was.span(node.orientation), node.sizes)
        indices = moved.get(path, frozenset())
        placed = bounds

        if indices or (low, high) != was.span(node.orientation):
            placed = (
                low,
                *(
                    position if index in indices else bounds[index + 1]
                    for index in range(len(node.children) - 1)
                ),
                high,
            )
            squeezed = _squeezed(node, placed)
            sizes = () if squeezed else _fractions(placed)

            # The tree stores fractions, and placing a border from them again
            # can round a sliver of 1e-16 to nothing, so the check is repeated
            # on the borders the stored sizes will give.
            if not squeezed:
                squeezed = _squeezed(node, _boundaries(low, high, sizes))

            if squeezed:
                raise LayoutRefused(
                    f"moving the border to {position!r} of the window would leave no room for "
                    f"{_describe(*squeezed)}"
                )

            resized[path] = sizes

        for index, child in enumerate(node.children):
            visit(
                child,
                path + (index,),
                was.with_span(node.orientation, bounds[index], bounds[index + 1]),
                now.with_span(node.orientation, placed[index], placed[index + 1]),
            )

    visit(tree, (), _WINDOW, _WINDOW)

    return resized


def _squeezed(split: Split, placed: tuple[float, ...]) -> tuple[Node, ...]:
    """The children of `split` that the borders `placed` leave no width or height.

    `placed` holds one more border than `split` has children, in the window's
    fractions, so each child lies between a border and the next one.
    """

    return tuple(
        child
        for child, (near, far) in zip(split.children, pairwise(placed), strict=True)
        if not far > near
    )


def _fractions(placed: tuple[float, ...]) -> tuple[float, ...]:
    """The share of the span from the first border to the last that each gap takes."""

    extent = placed[-1] - placed[0]

    return tuple((far - near) / extent for near, far in pairwise(placed))


def _other(orientation: Orientation) -> Orientation:
    """The axis across `orientation`'s: a column for a row, a row for a column."""

    return Orientation.COLUMN if orientation is Orientation.ROW else Orientation.ROW


def _is_area(node: Node, area_id: AreaId) -> bool:
    return isinstance(node, Area) and node.id == area_id


def _common_prefix(first: tuple[int, ...], second: tuple[int, ...]) -> tuple[int, ...]:
    """The longest path both paths begin with: the lowest split holding the two nodes."""

    length = 0

    for step, other in zip(first, second, strict=False):
        if step != other:
            break

        length += 1

    return first[:length]


def _rect_at(tree: Node, path: tuple[int, ...]) -> _Rect:
    """Where the node `path` leads to from `tree` lies in its window.

    Raises:
        NotInLayout: the path steps into an Area, or past a split's last child.
    """

    rect = _WINDOW
    node = tree

    for index in path:
        if isinstance(node, Area) or index >= len(node.children):
            raise NotInLayout(f"the path {path} leads to no node of this tree")

        bounds = _boundaries(*rect.span(node.orientation), node.sizes)
        rect = rect.with_span(node.orientation, bounds[index], bounds[index + 1])
        node = node.children[index]

    return rect


def _close(first: float, second: float) -> bool:
    """Whether two edges are one edge, to within `BORDER_ALIGNMENT_TOLERANCE`, as in `borders()`."""

    return abs(first - second) <= BORDER_ALIGNMENT_TOLERANCE


def _share_a_whole_edge(first: _Rect, second: _Rect) -> bool:
    """Whether two rectangles meet along the whole of an edge of each, so together they make one."""

    for orientation in Orientation:
        first_low, first_high = first.span(orientation)
        second_low, second_high = second.span(orientation)
        across = _other(orientation)

        if (_close(first_high, second_low) or _close(second_high, first_low)) and all(
            _close(edge, other)
            for edge, other in zip(first.span(across), second.span(across), strict=True)
        ):
            return True

    return False


def _side_of(own: _Rect, other: _Rect) -> Side | None:
    """Which side of `own` the rectangle `other` lies on, where their edges meet for some length."""

    def overlap(first: tuple[float, float], second: tuple[float, float]) -> bool:
        return min(first[1], second[1]) - max(first[0], second[0]) > BORDER_ALIGNMENT_TOLERANCE

    across_rows = overlap((own.top, own.bottom), (other.top, other.bottom))
    across_columns = overlap((own.left, own.right), (other.left, other.right))

    if across_rows and _close(other.right, own.left):
        return Side.LEFT

    if across_rows and _close(other.left, own.right):
        return Side.RIGHT

    if across_columns and _close(other.bottom, own.top):
        return Side.ABOVE

    if across_columns and _close(other.top, own.bottom):
        return Side.BELOW

    return None


def _pieces(
    node: Node, rect: _Rect, joined: AbstractSet[AreaId], *, opened: bool
) -> list[tuple[_Rect, Node]]:
    """What a join re-slices `node`'s region from, each with the rectangle it fills.

    With `opened` false, a subtree holding neither Area in `joined` is one
    piece, kept whole, and a split holding either is opened down to the Areas
    themselves. With `opened` true, every split is opened, and the pieces are
    the region's Areas.
    """

    if isinstance(node, Area) or not (opened or any(area.id in joined for area in areas_in(node))):
        return [(rect, node)]

    bounds = _boundaries(*rect.span(node.orientation), node.sizes)

    return [
        piece
        for index, child in enumerate(node.children)
        for piece in _pieces(
            child,
            rect.with_span(node.orientation, bounds[index], bounds[index + 1]),
            joined,
            opened=opened,
        )
    ]


def _resliced(
    tree: Node, path: tuple[int, ...], region: _Rect, attempts: tuple[list[tuple[_Rect, Node]], ...]
) -> Node:
    """`tree` with the split at `path`, which fills `region`, divided again among some pieces.

    `attempts` holds the ways to divide the region into pieces, tried in
    order: the first that gives a tree is taken. For each, the region is cut
    first along the axis that the split there divides. A join that still
    allows a cut along that axis therefore keeps it, and the other axis is
    used only where no such cut exists. Below the first cut the axis is decided:
    a strip between two cuts cannot be cut again along the same axis, or the
    cut would have crossed the whole region and been taken already. Where
    both first cuts give a tree, the first that nests no split past
    `TREE_DEPTH_MAXIMUM` is taken. A result whose first cut runs along the
    axis of the split above `path` is merged into that split
    (`_flattened`), the one form a tree takes (`layout/tree.py`).

    Raises:
        _NoStraightCut: no straight cut divides the pieces of any attempt.
        _TooDeep: every tree this region can hold nests a split past
            `TREE_DEPTH_MAXIMUM`.
    """

    holder = _split_at(tree, path)
    deep = False

    for pieces, orientation in product(attempts, (holder.orientation, _other(holder.orientation))):
        try:
            # One level more than the place allows, since a result merged
            # into the split above takes a level away; the whole tree is
            # held to the maximum below.
            sliced = _sliced(pieces, region, orientation, TREE_DEPTH_MAXIMUM - len(path) + 1)
        except _NoStraightCut:
            continue
        except _TooDeep:
            deep = True
            continue

        result = _placed(tree, path, sliced)

        if _split_past_depth_maximum(result) is None:
            return result

        deep = True

    if deep:
        raise _TooDeep

    raise _NoStraightCut


def _sliced(
    pieces: list[tuple[_Rect, Node]], region: _Rect, orientation: Orientation, levels: int
) -> Node:
    """`pieces`, which fill `region`, as one tree whose first cuts run along `orientation`'s axis.

    The region is cut along every line that crosses it whole (`_full_cuts`),
    all at once, since a split never holds one of its own orientation. Each
    strip between two cuts is then sliced the same way across the other
    axis. A size is the strip's width divided by the region's, from where
    the cuts lie.

    Raises:
        _NoStraightCut: no line along `orientation`'s axis crosses the
            region whole, or no line across that axis crosses one of the
            strips between the cuts, and so on down.
        _TooDeep: the tree would need more than `levels` levels of splits.
    """

    if len(pieces) == 1:
        return pieces[0][1]

    if levels == 0:
        raise _TooDeep

    cuts = _full_cuts(pieces, region, orientation)

    if not cuts:
        raise _NoStraightCut

    low, high = region.span(orientation)
    bounds = (low, *cuts, high)
    strips: list[list[tuple[_Rect, Node]]] = [[] for _ in pairwise(bounds)]

    for rect, node in pieces:
        start, end = rect.span(orientation)
        strips[bisect_left(cuts, (start + end) / 2)].append((rect, node))

    children = tuple(
        _sliced(strip, region.with_span(orientation, near, far), _other(orientation), levels - 1)
        for strip, (near, far) in zip(strips, pairwise(bounds), strict=True)
    )

    return _flattened(
        orientation, tuple((far - near) / (high - low) for near, far in pairwise(bounds)), children
    )


def _full_cuts(
    pieces: list[tuple[_Rect, Node]], region: _Rect, orientation: Orientation
) -> tuple[float, ...]:
    """Where a straight line crosses the whole of `region` without entering a piece, in order.

    The lines tried run across `orientation`'s axis, so a row's are vertical,
    one at each piece's leading edge. Edges within `BORDER_ALIGNMENT_TOLERANCE`
    of each other are one line, followed from one to the next as `borders()`
    follows one, and an edge that close to the region's own edge is that
    edge. A line enters a piece that begins before it and ends after it, each
    by more than the tolerance.
    """

    low, high = region.span(orientation)
    spans = [rect.span(orientation) for rect, _ in pieces]
    lines: list[list[float]] = []

    for start in sorted(start for start, _ in spans):
        if not low + BORDER_ALIGNMENT_TOLERANCE < start < high - BORDER_ALIGNMENT_TOLERANCE:
            continue

        if lines and _close(start, lines[-1][-1]):
            lines[-1].append(start)
        else:
            lines.append([start])

    return tuple(
        line[0]
        for line in lines
        if not any(
            begin < line[0] - BORDER_ALIGNMENT_TOLERANCE
            and end > line[0] + BORDER_ALIGNMENT_TOLERANCE
            for begin, end in spans
        )
    )


def _flattened(
    orientation: Orientation, sizes: tuple[float, ...], children: tuple[Node, ...]
) -> Split:
    """A split of `children`, with each child split of the same orientation merged into it.

    A row inside a row is one wider row (`layout/tree.py`), so the inner
    split's children take its place, each given its share of the place's
    size. The inner sizes are rescaled to sum to one first
    (`_summing_to_one`), so the merged sizes sum to one as nearly as the
    outer ones do.
    """

    merged_sizes: list[float] = []
    merged_children: list[Node] = []

    for size, child in zip(sizes, children, strict=True):
        if isinstance(child, Split) and child.orientation is orientation:
            merged_sizes.extend(size * share for share in _summing_to_one(child.sizes))
            merged_children.extend(child.children)
        else:
            merged_sizes.append(size)
            merged_children.append(child)

    return Split(orientation, tuple(merged_sizes), tuple(merged_children))


def _placed(tree: Node, path: tuple[int, ...], node: Node) -> Node:
    """`tree` with `node` at `path`, merged into the split above it where it continues that split.

    The split above is rescaled to sum to one first (`_summing_to_one`) where
    `node` is merged into it.
    """

    if not path:
        return node

    above = _split_at(tree, path[:-1])

    if not (isinstance(node, Split) and node.orientation is above.orientation):
        return _replaced(tree, path, node)

    index = path[-1]

    return _replaced(
        tree,
        path[:-1],
        _flattened(
            above.orientation,
            _summing_to_one(above.sizes),
            above.children[:index] + (node,) + above.children[index + 1 :],
        ),
    )


def _area_paths(node: Node, path: tuple[int, ...]) -> Iterator[tuple[tuple[int, ...], Area]]:
    if isinstance(node, Area):
        yield path, node
        return

    for index, child in enumerate(node.children):
        yield from _area_paths(child, path + (index,))


def _node_at(tree: Node, path: tuple[int, ...]) -> Node:
    """The node `path` leads to from `tree`.

    Raises:
        NotInLayout: the path steps into an Area, or past a split's last child.
    """

    node = tree

    for index in path:
        if isinstance(node, Area) or index >= len(node.children):
            raise NotInLayout(f"the path {path} leads to no node of this tree")

        node = node.children[index]

    return node


def _split_at(tree: Node, path: tuple[int, ...]) -> Split:
    """The split `path` leads to from `tree`.

    Raises:
        NotInLayout: the path leads to an Area, or to no node at all.
    """

    node = _node_at(tree, path)

    if isinstance(node, Area):
        raise NotInLayout(f"the path {path} leads to an Area, not a split")

    return node


def _replaced(node: Node, path: tuple[int, ...], replacement: Node) -> Node:
    """`node`'s tree with the node at `path` replaced, and every split above it rebuilt.

    Raises:
        NotInLayout: the path steps into an Area.
    """

    if not path:
        return replacement

    if isinstance(node, Area):
        raise NotInLayout(f"the path {path} steps into an Area, which holds no node")

    first, rest = path[0], path[1:]
    children = list(node.children)
    children[first] = _replaced(children[first], rest, replacement)

    return Split(node.orientation, node.sizes, tuple(children))


def _with_sizes(
    node: Node, path: tuple[int, ...], sizes: Mapping[tuple[int, ...], tuple[float, ...]]
) -> Node:
    """`node`'s tree with the split at each path in `sizes` given those sizes."""

    if isinstance(node, Area):
        return node

    children = tuple(
        _with_sizes(child, path + (index,), sizes) for index, child in enumerate(node.children)
    )

    return Split(node.orientation, sizes.get(path, node.sizes), children)


def _with_areas(node: Node, areas: Mapping[AreaId, Area]) -> Node:
    """`node`'s tree with each Area whose id is a key of `areas` replaced by its value."""

    if isinstance(node, Area):
        return areas.get(node.id, node)

    return Split(
        node.orientation, node.sizes, tuple(_with_areas(child, areas) for child in node.children)
    )


def _boundaries(low: float, high: float, sizes: tuple[float, ...]) -> tuple[float, ...]:
    """Where a split's children begin and end along its axis: one more boundary than sizes.

    Each inner boundary is placed from the exactly rounded sum of the sizes
    before it, so it does not depend on the order the sizes were added in, and
    the last is `high` itself rather than a sum that might round short of it.
    """

    extent = high - low
    inner = tuple(low + extent * math.fsum(sizes[:count]) for count in range(1, len(sizes)))

    return (low, *inner, high)


def _segments(window: int, tree: Node) -> dict[Handle, _Segment]:
    """Every handle in one window's tree, with where it lies, depth first."""

    segments: dict[Handle, _Segment] = {}

    def visit(
        node: Node, path: tuple[int, ...], left: float, top: float, right: float, bottom: float
    ) -> None:
        if isinstance(node, Area):
            return

        row = node.orientation is Orientation.ROW
        low, high = (left, right) if row else (top, bottom)
        start, end = (top, bottom) if row else (left, right)
        bounds = _boundaries(low, high, node.sizes)

        for index in range(len(node.children) - 1):
            segments[Handle(window, path, index)] = _Segment(
                node.orientation, bounds[index + 1], start, end, low, high
            )

        for index, child in enumerate(node.children):
            if row:
                visit(child, path + (index,), bounds[index], top, bounds[index + 1], bottom)
            else:
                visit(child, path + (index,), left, bounds[index], right, bounds[index + 1])

    visit(tree, (), 0.0, 0.0, 1.0, 1.0)

    return segments


def _chain(handle: Handle, segments: Mapping[Handle, _Segment]) -> tuple[Handle, ...]:
    """The handles on `handle`'s line connected to it end to end, ordered along the line.

    Each candidate is compared with the handle that reached it, never with
    `handle` itself: two handles within the tolerance of each other are on
    one line whichever is asked from, so the line is the same set from every
    handle on it, each one up to the tolerance off the one before. Handles of
    one split share their span along the line and are ordered across it.
    """

    orientation = segments[handle].orientation
    chain = {handle}
    frontier = [handle]

    while frontier:
        reached = segments[frontier.pop()]

        for candidate, segment in segments.items():
            if (
                candidate not in chain
                and segment.orientation is orientation
                and _close(segment.across, reached.across)
                and (_close(segment.start, reached.end) or _close(reached.start, segment.end))
            ):
                chain.add(candidate)
                frontier.append(candidate)

    return tuple(
        sorted(
            chain,
            key=lambda member: (
                segments[member].start,
                segments[member].across,
                member.path,
                member.index,
            ),
        )
    )


def _describe(*nodes: Node) -> str:
    """Nodes as a refusal names them: "Area 3", or "Areas 3, 4 and 5" for a split or several."""

    ids = [str(area.id) for node in nodes for area in areas_in(node)]

    if len(ids) == 1:
        return f"Area {ids[0]}"

    return f"Areas {', '.join(ids[:-1])} and {ids[-1]}"
