"""This module holds every window's tree as one value, and the operations a reader performs on it.

**The model is the layout's source of truth, not the widgets** (`PL-C842`).
`QSplitter.saveState()` was rejected for the job because it records no View
identity. Measured on 2026-09-16 with PySide6 6.11.2, a three-pane splitter
saves the same 35 bytes for its three children as for the same three in
reverse order. `restoreState()` also reports success when it restores those
bytes into a two-pane splitter. So the layout is held here, as plain values
that a test can build, compare and print without a `QApplication`. One adapter
module (`PL-W9P6`) builds the widget tree from those values.
`tools/import_boundary_check.py` enforces that nothing in this package imports
Qt.

**The layout is a value, not an object that changes.** Every operation returns
a new `LayoutModel` and leaves the one it was called on unchanged. A refused
operation raises `LayoutRefused` and changes nothing anywhere. So trying an
operation is also the way to ask whether it is available. The exception's
message is the reason that a menu shows beside the unavailable entry
(`PL-M352`).

**The layout supports several windows from its first version** (`PL-HJPY`,
ratified 2026-09-27). `windows[0]` is the main window, and a layout always has
one. A tree is a rectangle and cannot span two windows, so each window has its
own tree. Area ids are unique across all the windows. They are allocated from
`next_area_id`, which only rises, so an id is never handed out twice. State
kept for one Area id can therefore never come back under another Area.
`PL-HJPY` Q3 has the Workspace store that counter. The counter is held in this
model because the layout is what allocates ids. `layout/serialization.py`
writes it beside the windows, where the illustrated file in `PL-HJPY` puts it.

**What the tree cannot express is refused, never approximated** (`PL-3J2P`).
A splitter tree is strictly less expressive than Blender's vertex-and-edge
screen. In Blender, joining two Areas that share a whole edge can leave a
pinwheel: five Areas that no straight cut divides. A tree cannot hold a
pinwheel, so `join` refuses such a join. The limit then shows as an unavailable
operation, rather than as a layout different from the one the reader asked for.
`join` also refuses a result that would nest a split deeper than
`TREE_DEPTH_MAXIMUM`, as `split` does. Every other join of two Areas that share
a whole edge is carried out, whichever splits they sit in (`PL-G60V`), because
a reader sees the rectangles and never the tree.

**The model enforces only one minimum size, and it is geometric.** Otherwise,
how small an Area may be depends on the screen. So `layout/sizing.py` decides
it against an extent in pixels, and the adapter stops a drag at that size
(`PL-K285`). The geometric minimum is that an Area must be wider and taller
than `BORDER_ALIGNMENT_TOLERANCE` of its window. Otherwise `borders()` and
`join` would treat its two edges as one line, and no drag could give it room
again (`PL-391Y`).

**What is not here yet.** Taking an Area into its own window is a later
operation in `ROADMAP.md` item 34. Closing an Area is a join that gives its
place to a neighbour, and the adapter's Area menu asks `join` for it
(`PL-2KXB`). `PL-WV9K` covers what a Workspace carries beyond its layout, and
`PL-SSQW` covers the file.
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

# The largest distance, as a fraction of the window, at which `LayoutModel.borders()` treats
# two borders as one line. It absorbs only the rounding in the arithmetic that places
# borders: a border moved to a position lands within a few units in the last place of that
# position. It absorbs nothing visible. Two borders a pixel apart are two lines, just as two
# edges with separate vertices are two lines in Blender. An Area's width and height must
# also exceed this value, so that an Area's two edges are never treated as one line
# (`PL-391Y`).
BORDER_ALIGNMENT_TOLERANCE: Final = 1e-9

# The main window's index in `LayoutModel.windows`. A layout always has this
# window, and only it may hold the per-substance tier of the unconditional
# set (`PL-HJPY`, `app/unconditional_set.py`).
MAIN_WINDOW: Final = 0


@dataclass(frozen=True, slots=True)
class Handle:
    """A border between two neighbouring children of one split, which a reader drags.

    A handle is addressed by where it sits in one layout value. It names the
    window, the path of child indices from that window's tree down to the
    split, and the gap between two of the split's children. `index` 0 is the
    border between children 0 and 1. A handle has meaning only in the layout
    it was taken from, and `LayoutModel.handles()` lists that layout's handles.

    Raises:
        TypeError: a field is not an `int` or is a `bool`, or `path` is not a
            tuple of such ints.
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
    """An Area beside another, the side of the other Area it lies on, and whether they could join.

    `whole_edge` is true when the two share the whole of one edge, so that
    together they make a rectangle. `join` checks this first. A join that
    `whole_edge` allows can still be refused, for the reasons `join` gives.
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
    """Where a handle lies, in fractions of its window, as `borders()` and `resize()` use it.

    A row's handles are vertical lines, and a column's handles are horizontal
    lines. So `across` is a row handle's x and a column handle's y, and
    `start` and `end` are where the line begins and ends. `low` and `high` are
    where the handle's split begins and ends along its own axis. `resize()`
    lays out the split's children between them.
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
        """Return where the rectangle starts and ends along `orientation`'s axis.

        That axis is the one that a split of `orientation` divides.
        """

        if orientation is Orientation.ROW:
            return self.left, self.right

        return self.top, self.bottom

    def with_span(self, orientation: Orientation, low: float, high: float) -> _Rect:
        """Return the rectangle with its span along `orientation`'s axis replaced."""

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
    """A layout holds every window's tree and the counter that supplies the next Area's id.

    Raises:
        TypeError: a field is not of its declared type.
        InvalidLayout: the layout has no window. Or a window's tree holds a split
            deeper than `TREE_DEPTH_MAXIMUM`, and the message gives the split's
            path. Or an Area is no wider or no taller than
            `BORDER_ALIGNMENT_TOLERANCE` of its window, and the message gives the
            Area's size. Or two Areas share an id. Or `next_area_id` is not
            greater than every id in use.
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

        # Check the depth before any code below recurses through a tree. A tree
        # that is too deep would make that code end in a `RecursionError`,
        # rather than in this refusal.
        for index, window in enumerate(self.windows):
            too_deep = _split_past_depth_maximum(window.tree)

            if too_deep is not None:
                raise InvalidLayout(
                    f"window {index}'s tree holds a split {len(too_deep) + 1} deep, at path "
                    f"{too_deep}, and a split sits at most {TREE_DEPTH_MAXIMUM} deep in a "
                    "window's tree"
                )

        for index, window in enumerate(self.windows):
            narrow = _too_narrow(window.tree)

            if narrow is not None:
                raise InvalidLayout(f"in window {index}, {_narrow_reason(*narrow)}")

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
        """Return a layout of one window holding one Area, with id 1, that shows `view`.

        Raises:
            TypeError: `view` was not built as a `ViewKind`.
        """

        _require_view_kind(view)

        first = AreaId(1)

        return cls((Window(Area(first, view)),), AreaId(first + 1))

    def areas(self) -> tuple[Area, ...]:
        """Return every Area: the windows in order, and each window's Areas in reading order."""

        return tuple(area for window in self.windows for area in areas_in(window.tree))

    def area(self, area_id: AreaId) -> Area:
        """Return the Area whose id is `area_id`.

        Raises:
            TypeError: `area_id` was not built as an `AreaId`.
            NotInLayout: no Area of this layout holds `area_id`.
        """

        return self._locate(area_id)[1]

    def rectangle(self, area_id: AreaId) -> Rectangle:
        """Return where the Area whose id is `area_id` lies in its window.

        Raises:
            TypeError: `area_id` was not built as an `AreaId`.
            NotInLayout: no Area of this layout holds `area_id`.
        """

        place, _ = self._locate(area_id)
        rect = _rect_at(self.windows[place.window].tree, place.path)

        return Rectangle(place.window, rect.left, rect.top, rect.right, rect.bottom)

    def neighbours(self, area_id: AreaId) -> tuple[Neighbour, ...]:
        """Return the Areas whose edge meets an edge of this Area for some length, by side.

        Two Areas that touch only at a corner are not neighbours. The result
        is ordered by side: left, above, right, then below. Along each side, it
        is ordered from the top or from the left. A menu uses the result to
        list the Areas that this Area can be joined with, and to show the ones
        it cannot be joined with (`PL-2KXB`).

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

    def edges(self, area_id: AreaId) -> tuple[tuple[Side, Handle], ...]:
        """Return the border on each side of this Area, ordered left, above, right, below.

        A side that lies along the window's edge has no border and is left
        out. The border on a side is the handle nearest the Area in the tree.
        That handle belongs to the deepest split that lays out the Area's
        branch along that side's axis. Within that split, it lies between the
        Area's branch and the next child. So moving it resizes this Area from
        that side. The Area menu uses these borders to offer a resize without a
        drag (`PL-M352`).

        Raises:
            TypeError: `area_id` was not built as an `AreaId`.
            NotInLayout: no Area of this layout holds `area_id`.
        """

        place, _ = self._locate(area_id)
        tree = self.windows[place.window].tree
        found: dict[Side, Handle] = {}

        for depth in range(len(place.path) - 1, -1, -1):
            split = _node_at(tree, place.path[:depth])

            if isinstance(split, Area):
                continue

            index = place.path[depth]
            row = split.orientation is Orientation.ROW
            before, after = (Side.LEFT, Side.RIGHT) if row else (Side.ABOVE, Side.BELOW)

            if index > 0:
                found.setdefault(before, Handle(place.window, place.path[:depth], index - 1))

            if index < len(split.children) - 1:
                found.setdefault(after, Handle(place.window, place.path[:depth], index))

        return tuple((side, found[side]) for side in Side if side in found)

    def handles(self) -> tuple[Handle, ...]:
        """Return every handle: the windows in order, and each window's splits depth first."""

        return tuple(
            handle
            for index, window in enumerate(self.windows)
            for handle in _segments(index, window.tree)
        )

    def borders(self, handle: Handle) -> tuple[Handle, ...]:
        """Return the border that `handle` belongs to: every handle on its line connected to it.

        `PL-3J2P` measured the one thing that a splitter tree loses compared
        with Blender's screen. Where two borders cross, each one is a single
        line in Blender, and dragging it moves its whole length. A tree can
        store at most one of the two as a single handle. `PL-3J2P` recorded
        this query as the remedy, rather than a change of representation. The
        query finds the handles that are collinear with `handle` and connected
        to it end to end. It follows them from one to the next, as Blender's
        `screen_geom_select_connected_edge` does
        (`source/blender/editors/screen/screen_geometry.cc`, `blender/blender`
        `main`, read 2026-10-12). A drag then moves them together. Each handle
        is compared with the handle that reached it, rather than with
        `handle`. So the border is the same set, whichever of its handles the
        query starts from. The result includes `handle` and is ordered along
        the line, from top to bottom or from left to right.

        **The border stops at the window's edge.** Each window has its own
        tree, and two windows' borders can be collinear on a screen and still
        be unrelated (`PL-HJPY` Q4).

        **The query finds a line's handles by where they lie.** Blender
        follows shared vertices, and its border drag merges no vertices:
        `area_move_exit` in `screen_ops.cc` removes duplicate edges and leaves
        the vertices alone. So in Blender, two edges that a drag brings into
        line stay two edges until the reader merges them on purpose. Here, two
        borders brought into line, to within `BORDER_ALIGNMENT_TOLERANCE`, are
        one line from then on, because a tree has no vertices to keep them
        apart.

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
        """Cut an Area in two, and return the new layout and the new Area's id.

        The cut lies at `at`, a fraction of the Area's width for a `ROW` and of
        its height for a `COLUMN`. The Area keeps the part before the cut. A new
        Area takes the part after it and shows the same kind of View. This
        follows Blender, whose split duplicates its editor, and `PL-TH35` Q10,
        which has the new Area start from a copy of the source Area's state.

        The Area may already sit in a split along the same axis as the cut. Then
        the cut adds a child to that split rather than nesting another split,
        because a tree takes only that one form (`layout/tree.py`). That split's
        sizes are first rescaled to sum to one (`_summing_to_one`).

        Raises:
            TypeError: an argument is not of its declared type. In particular,
                `at` must be a `float`, so an `int` is refused.
            NotInLayout: no Area of this layout holds `area_id`.
            LayoutRefused: one of these is true. `at` does not lie strictly
                between 0 and 1. Or `at` is so close to one end that a part would
                be no wider or no taller than `BORDER_ALIGNMENT_TOLERANCE` of the
                window, and the message gives the part's size (`PL-391Y`). Or the
                cut would nest a split deeper than `TREE_DEPTH_MAXIMUM`. A cut
                along the axis of the split that holds the Area never does this,
                because it adds a child rather than a level. Or `next_area_id` has
                reached `AREA_ID_MAXIMUM`, so no id is left to hand out.
                `next_area_id` cannot pass that maximum while it stays above every
                id in use.
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

        # The layout held no Area this narrow before the cut, so any such Area
        # found now is one of the two parts.
        narrow = _too_narrow(tree)

        if narrow is not None:
            raise LayoutRefused(
                f"a cut at {at!r} of Area {area_id}'s {measure} leaves a part too small: "
                f"{_narrow_reason(*narrow, verb='would be')}"
            )

        return (
            LayoutModel(self._with_tree(place.window, tree), AreaId(self.next_area_id + 1)),
            added.id,
        )

    def join(self, keep: AreaId, remove: AreaId) -> LayoutModel:
        """Merge two neighbouring Areas into one: `keep` takes `remove`'s space.

        `keep` keeps its View. `remove` and its View leave the layout, and the
        id of `remove` is not handed out again. Two Areas can join when they
        share the whole of one edge, so that together they make a rectangle.
        Blender's `area_getorientation`
        (`source/blender/editors/screen/screen_edit.cc`, `blender/blender`
        `main`, read 2026-10-18) also decides from the two Areas' corners
        alone, though it accepts part of an edge and trims the rest
        (`docs/interface-provenance.md`).

        **Whether a join is carried out depends on the rectangles alone, never
        on the order in which the splits were made** (`PL-G60V`). Where four
        Areas meet at a point, two different trees can hold the same
        rectangles (`layout/tree.py`). So two Areas that share an edge may sit
        in different splits, and the join does not look for the pair in one
        split. Instead it re-slices the region of the lowest split that holds
        both (`_resliced`). It merges the two Areas into one rectangle. Then it
        divides the region again by straight cuts, which are the only way a
        tree divides anything. Every other Area keeps its rectangle, and the
        rebuilt splits take their sizes from where their borders lie.

        On its first try, the join keeps whole each subtree that holds neither
        Area of the pair, so that it changes no split it does not need to.
        But a subtree's own border can lie on the only line that divides the
        region. Then the join is tried again from every Area in the region, so
        that whether it is carried out still depends on the rectangles alone.

        A result can need one more level of splits than the tree had. Where
        that would exceed `TREE_DEPTH_MAXIMUM` inside the lowest split, the
        region of each split above it is re-sliced in turn, up to the whole
        window. Cutting a larger region the other way first can make the
        result fit. So the refusal for depth also depends on the rectangles
        alone.

        Raises:
            TypeError: an argument was not built as an `AreaId`.
            NotInLayout: no Area of this layout holds one of the ids.
            LayoutRefused: one of these is true. The two ids are the same. The
                Areas are in different windows. They do not share the whole of
                one edge. No straight cut divides the Areas that the join would
                leave: this is `PL-3J2P`'s refusal of a layout that a tree
                cannot hold, such as the pinwheel. Or every tree that could
                hold the result, re-sliced from any split up to the whole
                window, would nest a split deeper than `TREE_DEPTH_MAXIMUM`,
                which `split` also refuses.
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

        # A result too deep for the lowest split's region can fit when a larger
        # region higher up is first cut the other way. So each split above is
        # tried in turn, up to the whole window. Where the lowest region has no
        # straight cut, no region above it has one either.
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

    def position(self, handle: Handle) -> float:
        """Where `handle` lies across its axis, as a fraction of its window.

        A row's border lies at an x and a column's at a y. A drag starts from
        here, and `resize()` takes the place it moves to in the same units.

        Raises:
            TypeError: `handle` is not a `Handle`.
            NotInLayout: `handle` is not a border of this layout.
        """

        return self._segments_of(handle)[handle].across

    def resize(self, handle: Handle, position: float, *, alone: bool = False) -> LayoutModel:
        """Move a border, and every handle that `borders()` joins to it, to `position`.

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

        A split's sizes are fractions of its own extent, its length along its
        axis. So when a drag widens or narrows a split, the split's sizes are
        worked out again from where its borders lie in the window, with the
        moved borders at `position` (`_dragged`). A split whose extent does not
        change, and which holds no moved handle, keeps its sizes exactly. A
        handle already at `position` is not moved, so a drag to where a border
        already lies returns an equal layout.

        **With `alone`, only `handle` moves**, and the other handles on its
        line stay where they are. This is a drag with Shift held. The Blender
        Manual describes that drag as moving only the border under the pointer
        (`interface/window_system/areas.html` § "Resizing", read 2026-10-11),
        and `PL-RQT1` Q3 kept it.

        Raises:
            TypeError: `handle` is not a `Handle`, `position` not a `float`,
                or `alone` not a `bool`.
            NotInLayout: `handle` is not a border of this layout.
            LayoutRefused: `position` is not finite, or it would leave an Area
                beside the line no wider or no taller than
                `BORDER_ALIGNMENT_TOLERANCE` of the window. That happens in
                three cases. `position` lies at or past the far edge of that
                Area, which is another border or the window's edge. Or
                `position` lies within the tolerance of that far edge, or so close
                that the stored sizes would round the gap away. Or two handles of
                one split lie on the line, since moving both to one place leaves
                no room for the children between them. The message names the
                Areas left with no room. The adapter stops a drag at each Area's
                minimum size before the drag reaches this method
                (`layout/sizing.py`).
        """

        _require_float("position", position)

        if not isinstance(alone, bool):
            raise TypeError(f"alone is a bool, not {type(alone).__name__}")

        segments = self._segments_of(handle)
        tree = self.windows[handle.window].tree

        if not math.isfinite(position):
            raise LayoutRefused(f"a border cannot move to {position!r}")

        # The line's handles, grouped by the split that each one divides. One
        # split can hold two of them, and every one of them is moved.
        moved: dict[tuple[int, ...], set[int]] = {}

        for member in (handle,) if alone else _chain(handle, segments):
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
        moves with it. `PL-TH35` Q10 decided that a swap moves each View with
        its state. The two places keep their sizes.

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
        """Show another kind of View in an Area. The Area keeps its id and its place.

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
        """Return the Areas whose View kind is not in `known`, in the order `areas()` gives.

        The layout keeps no list of View kinds (`PL-R1WQ` Q1). The caller
        passes in the registry's tags, and a test can pass any set it likes. An
        Area returned here does not make the layout malformed. The file still
        loads, and the adapter draws that Area's failure state with its tag
        unchanged. So a later save writes back what was read (`PL-R1WQ` Q2,
        `PL-SSQW` Q5).

        Raises:
            TypeError: `known` is not a set. Otherwise a single tag, which is a
                `str`, would be treated as a set of its letters.
        """

        if not isinstance(known, AbstractSet):
            raise TypeError(f"known is a set of View kind tags, not {type(known).__name__}")

        return tuple(area for area in self.areas() if area.view not in known)

    def _locate(self, area_id: AreaId) -> tuple[_Place, Area]:
        """Return where the Area whose id is `area_id` sits, and the Area itself.

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
        """Return the place of every handle in `handle`'s window.

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
    """Return the path to the first split deeper than `TREE_DEPTH_MAXIMUM`, or `None`.

    Splits are searched in reading order. The tree is walked with a list
    rather than by recursion. So a tree built in code that is too deep to
    recurse through is refused here, rather than by a `RecursionError`. The
    walk goes no further down any path than the first split past the maximum.
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
    """Return `sizes` divided by their exactly rounded sum, ready to rebuild a split from.

    A split's sizes may differ from a sum of one by up to
    `LAYOUT_SIZE_SUM_TOLERANCE`. A file that this code did not write can
    contain such sizes, and the file reader accepts them. Arithmetic on those
    sizes can carry a sum from just inside the tolerance to just outside it.
    An operation on a layout that the file reader accepted would then raise
    `InvalidLayout`, and `PL-1FT6`'s review found a join doing so. Once the
    sizes are divided by their sum, their sum differs from one by a unit in
    the last place. The operation's own rounding adds a unit or two, and no
    operation inherits the previous one's error. Where the sum is exactly
    one, the division changes nothing. Elsewhere, each size moves by at most
    the tolerance's share of it, which nothing on a screen shows.

    This approach was chosen over a file reader stricter than the in-memory
    check. Such a reader would refuse to read back a layout held in memory
    whose sizes sum to a value between the reader's bound and the in-memory
    bound. `join` and `resize` work out a split's sizes afresh from where its
    borders lie, and those sizes come as close to summing to one as this
    function's result does. They use this function only for a split that they
    merge another split into (`_flattened`).
    """

    total = math.fsum(sizes)

    return tuple(size / total for size in sizes)


def _dragged(
    tree: Node, moved: Mapping[tuple[int, ...], AbstractSet[int]], position: float
) -> dict[tuple[int, ...], tuple[float, ...]]:
    """Return the new sizes of every split that a drag changes, keyed by the split's path.

    `moved` maps each split's path to the indices of that split's handles that
    move to `position`, a fraction of the window. Every other border stays
    where it lies in the window. The function walks down the tree from the
    window. Each split's extent along its axis is wherever its parent now
    places it. A split gets new sizes when its extent changed or when it holds
    a moved handle. Each new size is the distance between a pair of
    neighbouring borders, with the moved borders at `position`, divided by the
    split's new extent. Every other split keeps its sizes and is left out of
    the result.

    Raises:
        LayoutRefused: a child would be left no wider or no taller than
            `BORDER_ALIGNMENT_TOLERANCE` of the window. This happens when a
            border or an edge now lies at, past or within that tolerance of the
            border or edge on the child's far side. It also happens when the
            sizes that the tree would store place those two that close. A split
            whose own extent is zero is refused the same way, before any size is
            divided by that extent. The message names the first such split in
            depth-first order: its children left with no room, and its Areas.
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

            # The tree stores fractions, and placing a border again from those
            # fractions can make a gap a little smaller through rounding. So the
            # check is repeated on the borders that the stored sizes will produce.
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
    """Return the children of `split` that the borders `placed` leave too narrow.

    A child is too narrow by the same test that `_too_narrow` applies.
    `placed` holds one more border than `split` has children, in fractions of
    the window, so each child lies between a border and the next one.
    """

    return tuple(
        child
        for child, (near, far) in zip(split.children, pairwise(placed), strict=True)
        if not far - near > BORDER_ALIGNMENT_TOLERANCE
    )


def _too_narrow(tree: Node) -> tuple[Area, Orientation, float] | None:
    """The first Area, in reading order, no wider or no taller than `BORDER_ALIGNMENT_TOLERANCE`.

    Returns that Area, the axis along which it is too small, and its size
    along that axis as a fraction of the window. Returns `None` when every
    Area is larger. An Area this small would have its two edges treated as one
    line, so `join` and `borders()` could not tell them apart (`PL-391Y`).
    """

    for path, area in _area_paths(tree, ()):
        rect = _rect_at(tree, path)

        for orientation in Orientation:
            low, high = rect.span(orientation)

            if not high - low > BORDER_ALIGNMENT_TOLERANCE:
                return area, orientation, high - low

    return None


def _narrow_reason(area: Area, orientation: Orientation, size: float, verb: str = "is") -> str:
    """Return why the Area that `_too_narrow` found is refused, worded as a refusal message."""

    measure = "wide" if orientation is Orientation.ROW else "tall"

    return (
        f"Area {area.id} {verb} {size!r} of the window {measure}, and an Area is more than "
        f"{BORDER_ALIGNMENT_TOLERANCE!r} of its window {measure}, so that its two edges are "
        "never read as one line"
    )


def _fractions(placed: tuple[float, ...]) -> tuple[float, ...]:
    """Return the share that each gap takes of the span from the first border to the last."""

    extent = placed[-1] - placed[0]

    return tuple((far - near) / extent for near, far in pairwise(placed))


def _other(orientation: Orientation) -> Orientation:
    """Return the orientation other than `orientation`: a column for a row, a row for a column."""

    return Orientation.COLUMN if orientation is Orientation.ROW else Orientation.ROW


def _is_area(node: Node, area_id: AreaId) -> bool:
    return isinstance(node, Area) and node.id == area_id


def _common_prefix(first: tuple[int, ...], second: tuple[int, ...]) -> tuple[int, ...]:
    """Return the longest path that both paths begin with.

    That path leads to the lowest split holding both nodes.
    """

    length = 0

    for step, other in zip(first, second, strict=False):
        if step != other:
            break

        length += 1

    return first[:length]


def _rect_at(tree: Node, path: tuple[int, ...]) -> _Rect:
    """Return where the node that `path` leads to from `tree` lies in its window.

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
    """Return whether two edges are one edge, to within `BORDER_ALIGNMENT_TOLERANCE`.

    The test is the same one that `borders()` uses.
    """

    return abs(first - second) <= BORDER_ALIGNMENT_TOLERANCE


def _share_a_whole_edge(first: _Rect, second: _Rect) -> bool:
    """Return whether two rectangles meet along a whole edge of each, so together they form one."""

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
    """Return the side of `own` that the rectangle `other` lies on.

    Return `None` unless their edges meet for some length.
    """

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
    """Return the pieces a join re-slices `node`'s region from, each with the rectangle it fills.

    When `opened` is false, a subtree that holds neither Area in `joined` is
    one piece and is kept whole. A split that holds either Area is opened into
    its children, and each child is treated the same way. When `opened` is
    true, every split is opened, and the pieces are the region's Areas.
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
    """Return `tree` with the split at `path`, which fills `region`, divided again into pieces.

    `attempts` holds the ways to divide the region into pieces. They are tried
    in order, and the first that gives a tree is taken. For each attempt, the
    region is first cut along the axis that the split at `path` divides. So a
    join that still allows a cut along that axis keeps it, and the other axis
    is used only where no such cut exists. Below the first cut, the axis is
    fixed. A strip between two cuts cannot be cut again along the same axis,
    because such a cut would have crossed the whole region and been taken
    already. Where both first cuts give a tree, the first one that nests no
    split past `TREE_DEPTH_MAXIMUM` is taken. A result whose first cut runs
    along the axis of the split above `path` is merged into that split
    (`_flattened`). The merge keeps the tree in its single form, in which no
    split has a child split of its own orientation (`layout/tree.py`).

    Raises:
        _NoStraightCut: no straight cut divides the pieces of any attempt.
        _TooDeep: every tree this region can hold nests a split past
            `TREE_DEPTH_MAXIMUM`.
    """

    holder = _split_at(tree, path)
    deep = False

    for pieces, orientation in product(attempts, (holder.orientation, _other(holder.orientation))):
        try:
            # Allow one level more than the place allows, because a result
            # merged into the split above loses a level. The check below
            # applies the maximum to the whole tree.
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
    """Build a tree from `pieces`, which fill `region`, with first cuts along `orientation`'s axis.

    The region is cut along every line that crosses all of it (`_full_cuts`),
    all at once, because a split never holds a split of its own orientation.
    Each strip between two cuts is then sliced the same way across the other
    axis. Each size is the strip's extent along `orientation`'s axis divided
    by the region's extent along it, measured from where the cuts lie.

    Raises:
        _NoStraightCut: no line along `orientation`'s axis crosses the whole
            region, or no line across that axis crosses the whole of one of
            the strips between the cuts, and so on down.
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
    """Return, in order, where a straight line crosses all of `region` without entering a piece.

    The lines tried run across `orientation`'s axis, so for a row they are
    vertical. One line is tried at each piece's leading edge. Edges within
    `BORDER_ALIGNMENT_TOLERANCE` of each other count as one line. That line is
    followed from one edge to the next, as `borders()` follows a line. An edge
    that close to the region's own edge counts as the region's edge. A line
    enters a piece when the piece begins before the line and ends after it,
    each by more than the tolerance.

    A line followed that way can be wider than the tolerance. So whether the
    cut enters a piece depends on which of the line's edges it is drawn at.
    The cut is drawn at the first edge at which it enters no piece
    (`PL-8GLZ`). When the cut was drawn at the first edge alone, it entered a
    piece that ended at the last edge, and a join that a tree could hold was
    refused.
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

    def enters_none(at: float) -> bool:
        return not any(
            begin < at - BORDER_ALIGNMENT_TOLERANCE and end > at + BORDER_ALIGNMENT_TOLERANCE
            for begin, end in spans
        )

    cuts = (next((edge for edge in line if enters_none(edge)), None) for line in lines)

    return tuple(cut for cut in cuts if cut is not None)


def _flattened(
    orientation: Orientation, sizes: tuple[float, ...], children: tuple[Node, ...]
) -> Split:
    """Return a split of `children`, with each child split of the same orientation merged into it.

    A row inside a row is one wider row (`layout/tree.py`). So the inner
    split's children take its place, and each gets its share of that place's
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
    """Return `tree` with `node` at `path`, merged into the split above where `node` continues it.

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
    """Return the node that `path` leads to from `tree`.

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
    """Return the split that `path` leads to from `tree`.

    Raises:
        NotInLayout: the path leads to an Area, or to no node at all.
    """

    node = _node_at(tree, path)

    if isinstance(node, Area):
        raise NotInLayout(f"the path {path} leads to an Area, not a split")

    return node


def _replaced(node: Node, path: tuple[int, ...], replacement: Node) -> Node:
    """Return `node`'s tree with the node at `path` replaced, and every split above it rebuilt.

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
    """Return `node`'s tree, with the split at each path in `sizes` given the sizes stored there."""

    if isinstance(node, Area):
        return node

    children = tuple(
        _with_sizes(child, path + (index,), sizes) for index, child in enumerate(node.children)
    )

    return Split(node.orientation, sizes.get(path, node.sizes), children)


def _with_areas(node: Node, areas: Mapping[AreaId, Area]) -> Node:
    """Return `node`'s tree, with each Area whose id is a key of `areas` replaced by its value."""

    if isinstance(node, Area):
        return areas.get(node.id, node)

    return Split(
        node.orientation, node.sizes, tuple(_with_areas(child, areas) for child in node.children)
    )


def _boundaries(low: float, high: float, sizes: tuple[float, ...]) -> tuple[float, ...]:
    """Return where a split's children begin and end along its axis: one boundary more than sizes.

    Each inner boundary is placed from the exactly rounded sum of the sizes
    before it, so it does not depend on the order in which the sizes were
    added. The last boundary is `high` itself, rather than a sum that might
    round short of it.
    """

    extent = high - low
    inner = tuple(low + extent * math.fsum(sizes[:count]) for count in range(1, len(sizes)))

    return (low, *inner, high)


def _segments(window: int, tree: Node) -> dict[Handle, _Segment]:
    """Return every handle in one window's tree, depth first, with where each one lies."""

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
    """Return the handles on `handle`'s line that connect to it end to end, ordered along the line.

    Each candidate is compared with the handle that reached it, never with
    `handle` itself. Two handles within the tolerance of each other are on one
    line, whichever of them the search starts from. So the line is the same
    set from every handle on it, and each handle may lie up to the tolerance
    away from the one before. Handles of one split share their span along the
    line, and are ordered across it.
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
    """Return the nodes as a refusal names them.

    One Area is "Area 3". A split, or several nodes, is "Areas 3, 4 and 5".
    """

    ids = [str(area.id) for node in nodes for area in areas_in(node)]

    if len(ids) == 1:
        return f"Area {ids[0]}"

    return f"Areas {', '.join(ids[:-1])} and {ids[-1]}"
