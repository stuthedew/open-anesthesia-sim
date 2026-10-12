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
screen: two Areas that share a whole edge but sit in different splits - the
pinwheel's case - can be joined there and cannot be joined here. `join` refuses
them, which is the limit surfacing as an unavailable operation rather than as
a different layout than the one the reader asked for.

**What is not here yet.** Minimum sizes, the clamp on a drag and `too_small()`
are `PL-K285`'s; closing an Area and taking one into its own window are later
operations of `ROADMAP.md` item 34; what a Workspace carries beyond its layout
is `PL-WV9K`'s; and the file is `PL-SSQW`'s.
"""

from __future__ import annotations

import math
from collections.abc import Iterator, Mapping
from collections.abc import Set as AbstractSet
from dataclasses import dataclass
from typing import Final

from anesthesia_sim.core.checked_number import shown
from anesthesia_sim.layout.exceptions import InvalidLayout, LayoutRefused, NotInLayout
from anesthesia_sim.layout.tree import (
    AREA_ID_MAXIMUM,
    Area,
    AreaId,
    Node,
    Orientation,
    Split,
    ViewKind,
    Window,
    areas_in,
)

__all__ = ["BORDER_ALIGNMENT_TOLERANCE", "Handle", "LayoutModel"]

# How far apart, as a fraction of the window, two borders may lie and still be
# read as one line by `LayoutModel.borders()`. It absorbs the rounding of the
# arithmetic that places them - a border moved to a position lands within a
# few units in the last place of it - and nothing visible: two borders a pixel
# apart are two lines, as two edges with separate vertices are in Blender.
BORDER_ALIGNMENT_TOLERANCE: Final = 1e-9


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
class _Place:
    """Where a node sits: its window, and the path of child indices from that window's tree."""

    window: int
    path: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class _Segment:
    """Where a handle lies, in fractions of its window: what `borders()` and `resize()` read.

    A row's handles are vertical lines and a column's horizontal ones, so
    `across` is a row handle's x and a column handle's y, and `start` and
    `end` run along the line. `low` and `high` are the outer edges of the two
    children the handle divides, which bound where it can move, and `extent`
    is its split's length along the split's axis.
    """

    orientation: Orientation
    across: float
    start: float
    end: float
    low: float
    high: float
    extent: float


@dataclass(frozen=True, slots=True)
class LayoutModel:
    """Every window's tree, and the counter the next Area's id comes from.

    Raises:
        TypeError: a field is not of its declared type.
        InvalidLayout: the layout has no window; two Areas share an id; or
            `next_area_id` is not above every id in use.
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
        """A layout of one window holding one Area, id 1, showing `view`."""

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
        `main`, read 2026-10-12), so a drag moves them together. The result
        includes `handle` and is ordered along the line, top to bottom or left
        to right.

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
        (`layout/tree.py`).

        Raises:
            TypeError: an argument is not of its declared type; `at` is not a
                `float`.
            NotInLayout: no Area of this layout holds `area_id`.
            LayoutRefused: `at` does not lie strictly between 0 and 1, or is
                so close to one end that a part would have no size; or this
                layout has allocated the last id, `AREA_ID_MAXIMUM`.
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
                f"this layout cannot make another Area: its ids have reached {AREA_ID_MAXIMUM}, "
                "the largest an Area id can be"
            )

        added = Area(self.next_area_id, source.view)
        tree = self.windows[place.window].tree
        parent = _place_of_parent(place)
        holder = _node_at(tree, parent.path) if parent is not None else None

        if parent is not None and isinstance(holder, Split) and holder.orientation is orientation:
            position = place.path[-1]
            kept = holder.sizes[position] * at
            given = holder.sizes[position] - kept

            if kept <= 0 or given <= 0:
                raise LayoutRefused(
                    f"a cut at {at!r} of Area {area_id}'s {measure} leaves a part with no size"
                )

            divided = Split(
                orientation,
                holder.sizes[:position] + (kept, given) + holder.sizes[position + 1 :],
                holder.children[:position] + (source, added) + holder.children[position + 1 :],
            )
            tree = _replaced(tree, parent.path, divided)
        else:
            tree = _replaced(tree, place.path, Split(orientation, (at, 1 - at), (source, added)))

        return (
            LayoutModel(self._with_tree(place.window, tree), AreaId(self.next_area_id + 1)),
            added.id,
        )

    def join(self, keep: AreaId, remove: AreaId) -> LayoutModel:
        """Merge two neighbouring Areas into one: `keep` takes `remove`'s space.

        `keep` keeps its View; `remove` and its View leave the layout, and its
        id is not handed out again. Two Areas join only where they sit next to each other in one
        split, so the result is a rectangle the tree can hold; where the split
        is left with one child it gives way to that child.

        Raises:
            TypeError: an argument was not built as an `AreaId`.
            NotInLayout: no Area of this layout holds one of the ids.
            LayoutRefused: the two ids are the same; the Areas are in different
                windows; or they are not next to each other in one split,
                which is `PL-3J2P`'s refusal - including two Areas that share
                a whole edge from different splits, which Blender would join.
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

        parent = _place_of_parent(kept)

        if (
            parent is None
            or parent != _place_of_parent(removed)
            or abs(kept.path[-1] - removed.path[-1]) != 1
        ):
            raise LayoutRefused(
                f"Area {keep} and Area {remove} cannot be joined: the layout joins two Areas "
                "only where they sit next to each other in the same split, and these do not"
            )

        tree = self.windows[kept.window].tree
        holder = _split_at(tree, parent.path)
        keeping = kept.path[-1]
        removing = removed.path[-1]
        sizes = list(holder.sizes)
        children = list(holder.children)
        sizes[keeping] += sizes[removing]
        del sizes[removing]
        del children[removing]

        merged: Node = (
            children[0]
            if len(children) == 1
            else Split(holder.orientation, tuple(sizes), tuple(children))
        )

        return LayoutModel(
            self._with_tree(kept.window, _replaced(tree, parent.path, merged)), self.next_area_id
        )

    def resize(self, handle: Handle, position: float) -> LayoutModel:
        """Move a border, and every handle `borders()` joins to it, to `position`.

        `position` is a fraction of the window: an x for a row's border and a y
        for a column's. Each handle moved changes only the two children it
        divides, so every other Area keeps its size, which is how a border drag
        behaves in Blender.

        Raises:
            TypeError: `handle` is not a `Handle`, or `position` not a `float`.
            NotInLayout: `handle` is not a border of this layout.
            LayoutRefused: `position` would leave a child of one of the moved
                handles with no size - it lies at or past a neighbouring border
                or the edge of the split - or is not finite. `PL-K285` adds
                minimum sizes, which clamp a drag before it gets here.
        """

        _require_float("position", position)

        segments = self._segments_of(handle)
        tree = self.windows[handle.window].tree
        resized: dict[tuple[int, ...], tuple[float, ...]] = {}

        if not math.isfinite(position):
            raise LayoutRefused(f"a border cannot move to {position!r}")

        for member in _chain(handle, segments):
            segment = segments[member]
            holder = _split_at(tree, member.path)
            first, second = member.index, member.index + 1
            squeezed: int | None

            if position <= segment.low:
                squeezed = first
            elif position >= segment.high:
                squeezed = second
            else:
                # Inside the two children's span, so the split has an extent to divide by.
                before = (position - segment.low) / segment.extent
                after = holder.sizes[first] + holder.sizes[second] - before
                squeezed = first if before <= 0 else second if after <= 0 else None
                sizes = list(holder.sizes)
                sizes[first] = before
                sizes[second] = after
                resized[member.path] = tuple(sizes)

            if squeezed is not None:
                raise LayoutRefused(
                    f"moving the border to {position!r} of the window would leave no room "
                    f"for {_describe(holder.children[squeezed])}"
                )

        return LayoutModel(
            self._with_tree(handle.window, _with_sizes(tree, (), resized)), self.next_area_id
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
                node.orientation,
                bounds[index + 1],
                start,
                end,
                bounds[index],
                bounds[index + 2],
                high - low,
            )

        for index, child in enumerate(node.children):
            if row:
                visit(child, path + (index,), bounds[index], top, bounds[index + 1], bottom)
            else:
                visit(child, path + (index,), left, bounds[index], right, bounds[index + 1])

    visit(tree, (), 0.0, 0.0, 1.0, 1.0)

    return segments


def _chain(handle: Handle, segments: Mapping[Handle, _Segment]) -> tuple[Handle, ...]:
    """The handles on `handle`'s line connected to it end to end, ordered along the line."""

    seed = segments[handle]
    on_line = [
        candidate
        for candidate, segment in segments.items()
        if segment.orientation is seed.orientation
        and abs(segment.across - seed.across) <= BORDER_ALIGNMENT_TOLERANCE
    ]
    chain = {handle}
    frontier = [handle]

    while frontier:
        reached = segments[frontier.pop()]

        for candidate in on_line:
            segment = segments[candidate]

            if candidate not in chain and (
                abs(segment.start - reached.end) <= BORDER_ALIGNMENT_TOLERANCE
                or abs(reached.start - segment.end) <= BORDER_ALIGNMENT_TOLERANCE
            ):
                chain.add(candidate)
                frontier.append(candidate)

    return tuple(sorted(chain, key=lambda member: segments[member].start))


def _describe(node: Node) -> str:
    """A node as a refusal names it: "Area 3", or "Areas 3, 4 and 5" for a split."""

    ids = [str(area.id) for area in areas_in(node)]

    if len(ids) == 1:
        return f"Area {ids[0]}"

    return f"Areas {', '.join(ids[:-1])} and {ids[-1]}"
