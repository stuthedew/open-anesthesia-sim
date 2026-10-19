"""How a layout is drawn in whole pixels, and which Areas cannot be given the size their View needs.

A layout stores fractions, so a file reads the same on any screen (`PL-HJPY`
Q5). How small an Area may be is a property of the screen, so it is decided
here, against an extent in pixels, and never stored in the layout. `PL-K285`
decided the rules (project owner, 2026-09-27, ratified), and `PL-30L5` Q2
changed one of them (project owner, 2026-10-11, ratified). This module holds
them as pure functions of a window's tree, with no toolkit, so a test drives
them with no `QApplication`. The adapter, `app/area_layout.py`, draws exactly
the sizes this module gives.

**A View's minimum size is a constraint, not a request** (`PL-K285` Q1). Each
Area has a *need*: the least size at which its View can be drawn. Where the
layout can give every Area its need, it does. An Area whose share of its split
would be smaller than its need is held at its need, and the other children of
that split give up the room in proportion to their fractions. So a View is
never drawn smaller than it needs and never clipped. The stored fractions are
not changed: they are the reader's proportions, and they apply again once the
extent is large enough.

**An Area that cannot be given its need says so** (`PL-K285` Q2 and Q3,
`PL-30L5` Q2). That happens where the reader's own operation asks for more
than the extent holds: a split whose halves are smaller than their View needs,
a View chosen for an Area too small for it, or a layout opened at a smaller
size than it was arranged at. Such an Area is *too small*. It is held only at
its *floor*, the least size at which it can show its header and one line of a
notice, and the adapter draws `PL-DB5G`'s notice there, stating the size the
View needs and the size the Area has. Nothing is clipped, and nothing is
collapsed to zero extent, which is what Blender does with
`RGN_FLAG_TOO_SMALL` (`docs/interface-provenance.md`).

**Which Areas are too small is decided once per change, by `settle`.** Every
Area is first tried at its need. Where a split cannot hold its children's
needs, the Areas under it that the latest change did not leave in place are
let go to their floors first, and the Areas it left in place only after them.
So a split's new halves report themselves too small, rather than taking the
room from an Area the reader did not touch. Then every Area that still has its
need is drawn, and the rest are too small. A too-small Area is drawn again as
soon as a later change, such as a border drag or a larger window, can give it
its need.

**Pixels are apportioned as the adapter's splitters lay them out.** A split of
`n` children gives up `n - 1` handles of `handle_px` along its axis, and shares
the rest. Each share is rounded by `pixel_sizes`, which is the one rounding
the adapter uses, so the sizes here are the sizes on screen.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from collections.abc import Set as AbstractSet
from dataclasses import dataclass
from types import MappingProxyType

from anesthesia_sim.core.checked_number import shown
from anesthesia_sim.layout.exceptions import InvalidLayout
from anesthesia_sim.layout.tree import Area, AreaId, Node, Orientation, Split, areas_in

__all__ = [
    "Apportionment",
    "Fit",
    "PixelSize",
    "TooSmall",
    "apportion",
    "minimum_extent",
    "pixel_sizes",
    "settle",
]


@dataclass(frozen=True, slots=True)
class PixelSize:
    """A width and a height in whole logical pixels, each zero or more.

    Raises:
        TypeError: a field is not an `int`, or is a `bool`.
        InvalidLayout: a field is negative.
    """

    width_px: int
    height_px: int

    def __post_init__(self) -> None:
        for name, value in (("width_px", self.width_px), ("height_px", self.height_px)):
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"a pixel size's {name} is an int, not {type(value).__name__}")

            if value < 0:
                raise InvalidLayout(f"a pixel size's {name} is zero or more, not {shown(value)}")

    def covers(self, other: PixelSize) -> bool:
        """Whether this size is at least `other` on both axes."""

        return self.width_px >= other.width_px and self.height_px >= other.height_px

    def along(self, orientation: Orientation) -> int:
        """The extent along `orientation`'s axis: the width for a row, the height for a column."""

        return self.width_px if orientation is Orientation.ROW else self.height_px

    def across(self, orientation: Orientation) -> int:
        """The extent across `orientation`'s axis: the height for a row, the width for a column."""

        return self.height_px if orientation is Orientation.ROW else self.width_px


@dataclass(frozen=True, slots=True)
class TooSmall:
    """An Area the layout cannot give the size its View needs.

    Attributes:
        area_id: The Area.
        needed: The least size its View can be drawn at.
        available: The size the Area is drawn at.
    """

    area_id: AreaId
    needed: PixelSize
    available: PixelSize


@dataclass(frozen=True, slots=True)
class Apportionment:
    """A window's tree laid out in whole pixels.

    Attributes:
        areas: Each Area's size, in reading order.
        splits: Each split's children's sizes along its axis, in order, by the
            path of child indices from the tree's root to the split. This is
            what the adapter hands each splitter.
        unheld: The path of every node that could not be given its bound, in
            the order they were laid out. A split is listed where its
            children's bounds along its axis need more than it has, or where
            one child's bound across it is more than it has. An Area is listed
            where the tree is that Area alone and the extent is less than its
            bound. Empty when every Area has at least its bound.
    """

    areas: Mapping[AreaId, PixelSize]
    splits: Mapping[tuple[int, ...], tuple[int, ...]]
    unheld: tuple[tuple[int, ...], ...]


@dataclass(frozen=True, slots=True)
class Fit:
    """What `settle` decided: which Areas are drawn, which are too small, and every size.

    Attributes:
        apportionment: Every Area's and every split's size in pixels.
        bounds: The least size each Area is held at: its need where it is
            drawn, and its floor where it is too small. The adapter sets each
            Area's minimum size to this, so the window's minimum is the sum
            of these bounds rather than of every need.
        drawn: The Areas given their need, which draw their View.
        too_small: The Areas that are not, in reading order, with the size
            each needs and has.
    """

    apportionment: Apportionment
    bounds: Mapping[AreaId, PixelSize]
    drawn: frozenset[AreaId]
    too_small: tuple[TooSmall, ...]


def pixel_sizes(fractions: tuple[float, ...], available: int) -> tuple[int, ...]:
    """Whole-pixel sizes in the proportion of `fractions`, summing to `available`.

    Each size is rounded down, and the pixels that leaves over go one each to
    the sizes that lost the most, so the sizes sum to `available` exactly and
    no size is more than a pixel from its share. Ties go to the earlier size.
    """

    exact = [fraction * available for fraction in fractions]
    sizes = [math.floor(share) for share in exact]
    left_over = max(0, min(len(sizes), available - sum(sizes)))
    by_loss = sorted(range(len(sizes)), key=lambda index: (sizes[index] - exact[index], index))

    for index in by_loss[:left_over]:
        sizes[index] += 1

    return tuple(sizes)


def minimum_extent(tree: Node, handle_px: int, bounds: Mapping[AreaId, PixelSize]) -> PixelSize:
    """The least extent at which every Area of `tree` can be given its bound.

    A row needs the sum of its children's widths and its handles, and the
    tallest of their heights; a column the same with the axes exchanged.

    Raises:
        TypeError: `handle_px` is not an `int`, or is a `bool`.
        InvalidLayout: `handle_px` is negative.
        KeyError: `bounds` holds no bound for an Area of `tree`.
    """

    _require_handle(handle_px)

    return _minimum_extent(tree, handle_px, bounds)


def apportion(
    tree: Node, extent: PixelSize, handle_px: int, bounds: Mapping[AreaId, PixelSize]
) -> Apportionment:
    """Lay `tree` out in `extent`, giving each Area at least its bound wherever the extent allows.

    At each split, a child whose share would be less than its bound along the
    split's axis is held at its bound, and the other children share the rest
    in proportion to their fractions (`_held_sizes`). Where no child is held,
    the sizes are exactly `pixel_sizes` of the split's fractions. Where the
    split's children need more than it has, they are given `pixel_sizes` of
    its fractions, and the split is listed in `unheld`.

    Raises:
        TypeError: `extent` is not a `PixelSize`, or `handle_px` not an `int`.
        InvalidLayout: `handle_px` is negative.
        KeyError: `bounds` holds no bound for an Area of `tree`.
    """

    if not isinstance(extent, PixelSize):
        raise TypeError(f"an extent is a PixelSize, not {type(extent).__name__}")

    _require_handle(handle_px)

    areas: dict[AreaId, PixelSize] = {}
    splits: dict[tuple[int, ...], tuple[int, ...]] = {}
    unheld: list[tuple[int, ...]] = []

    def visit(node: Node, path: tuple[int, ...], size: PixelSize) -> None:
        if isinstance(node, Area):
            areas[node.id] = size

            if path == () and not size.covers(bounds[node.id]):
                unheld.append(path)

            return

        orientation = node.orientation
        count = len(node.children)
        # Each child is given a pixel at least, as the adapter's splitters
        # always have been, so no Area is laid out with no extent at all.
        available = max(size.along(orientation) - handle_px * (count - 1), count)
        across = size.across(orientation)
        least = [_minimum_extent(child, handle_px, bounds) for child in node.children]
        held = _held_sizes(node.sizes, tuple(each.along(orientation) for each in least), available)

        if held is None or any(each.across(orientation) > across for each in least):
            unheld.append(path)

        sizes = held if held is not None else pixel_sizes(node.sizes, available)
        splits[path] = sizes

        for index, (child, along) in enumerate(zip(node.children, sizes, strict=True)):
            child_size = (
                PixelSize(along, across)
                if orientation is Orientation.ROW
                else PixelSize(across, along)
            )
            visit(child, path + (index,), child_size)

    visit(tree, (), extent)

    return Apportionment(MappingProxyType(areas), MappingProxyType(splits), tuple(unheld))


def settle(
    tree: Node,
    extent: PixelSize,
    handle_px: int,
    needs: Mapping[AreaId, PixelSize],
    floors: Mapping[AreaId, PixelSize],
    kept: AbstractSet[AreaId],
) -> Fit:
    """Decide which Areas of `tree` can be given their need in `extent`, and lay every one out.

    `kept` names the Areas that were drawn before the change being settled
    and that the change left with the same View in the same place. Every
    Area is tried at its need. While some split cannot hold its children's
    bounds, the first such split's Areas that are not in `kept` are let go to
    their floors, and where none is left to let go, its Areas in `kept` are.
    An Area whose floor is more than its need is held at its floor. Every
    Area that is then given its need is drawn, and every other is too small.

    Raises:
        TypeError: `extent` is not a `PixelSize`, or `handle_px` not an `int`.
        InvalidLayout: `handle_px` is negative.
        KeyError: `needs` or `floors` holds no size for an Area of `tree`.
    """

    areas = tuple(areas_in(tree))
    bounds = {area.id: _larger(needs[area.id], floors[area.id]) for area in areas}

    while True:
        laid_out = apportion(tree, extent, handle_px, bounds)

        if not laid_out.unheld:
            break

        under = tuple(area.id for area in areas_in(_node_at(tree, laid_out.unheld[0])))
        holding = [area_id for area_id in under if bounds[area_id] != floors[area_id]]
        let_go = [area_id for area_id in holding if area_id not in kept] or holding

        if not let_go:
            # Every Area under the split is at its floor already, so the
            # extent is below what even the floors need. The sizes are the
            # fractions', and every Area below its need is too small.
            break

        for area_id in let_go:
            bounds[area_id] = floors[area_id]

    drawn = frozenset(area.id for area in areas if laid_out.areas[area.id].covers(needs[area.id]))
    final = {
        area.id: _larger(needs[area.id], floors[area.id]) if area.id in drawn else floors[area.id]
        for area in areas
    }
    too_small = tuple(
        TooSmall(area.id, needs[area.id], laid_out.areas[area.id])
        for area in areas
        if area.id not in drawn
    )

    return Fit(laid_out, MappingProxyType(final), drawn, too_small)


def _held_sizes(
    fractions: tuple[float, ...], bounds: tuple[int, ...], available: int
) -> tuple[int, ...] | None:
    """Sizes summing to `available`, each at least its bound, in proportion to `fractions` above it.

    A child whose proportional share of what is left would be less than its
    bound is held at its bound, and the others share what remains, until no
    share is less than its bound. Where none is held, the result is exactly
    `pixel_sizes(fractions, available)`. Returns None where the bounds sum to
    more than `available`.
    """

    if sum(bounds) > available:
        return None

    plain = pixel_sizes(fractions, available)

    if all(size >= bound for size, bound in zip(plain, bounds, strict=True)):
        return plain

    held: set[int] = set()

    while True:
        free = available - sum(bounds[index] for index in held)
        loose = [index for index in range(len(fractions)) if index not in held]

        if not loose:
            break

        weight = math.fsum(fractions[index] for index in loose)
        short = [index for index in loose if fractions[index] / weight * free < bounds[index]]

        if not short:
            break

        held.update(short)

    sizes = list(bounds)
    loose = [index for index in range(len(fractions)) if index not in held]
    free = available - sum(bounds[index] for index in held)

    if loose:
        weight = math.fsum(fractions[index] for index in loose)
        shares = pixel_sizes(tuple(fractions[index] / weight for index in loose), free)

        for index, share in zip(loose, shares, strict=True):
            sizes[index] = share
    else:
        # Every child is held, so the pixels left over above the bounds go
        # to the children in proportion to their fractions.
        for index, extra in enumerate(pixel_sizes(fractions, free)):
            sizes[index] += extra

    return tuple(sizes)


def _minimum_extent(node: Node, handle_px: int, bounds: Mapping[AreaId, PixelSize]) -> PixelSize:
    if isinstance(node, Area):
        return bounds[node.id]

    least = [_minimum_extent(child, handle_px, bounds) for child in node.children]
    along = sum(each.along(node.orientation) for each in least) + handle_px * (len(least) - 1)
    across = max(each.across(node.orientation) for each in least)

    if node.orientation is Orientation.ROW:
        return PixelSize(along, across)

    return PixelSize(across, along)


def _larger(first: PixelSize, second: PixelSize) -> PixelSize:
    return PixelSize(max(first.width_px, second.width_px), max(first.height_px, second.height_px))


def _node_at(tree: Node, path: tuple[int, ...]) -> Node:
    node = tree

    for step in path:
        if not isinstance(node, Split):
            raise LookupError(f"the tree has no node at {path}")

        node = node.children[step]

    return node


def _require_handle(handle_px: object) -> None:
    if isinstance(handle_px, bool) or not isinstance(handle_px, int):
        raise TypeError(f"a handle's width is an int, not {type(handle_px).__name__}")

    if handle_px < 0:
        raise InvalidLayout(f"a handle's width is zero or more pixels, not {shown(handle_px)}")
