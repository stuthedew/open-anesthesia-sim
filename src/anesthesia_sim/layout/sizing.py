"""How a layout is drawn in whole pixels, and which Areas cannot get the size their View needs.

A layout stores fractions, so a file gives the same layout on any screen
(`PL-HJPY` Q5). How small an Area may be is a property of the screen, so it is
decided here, against an extent in pixels, and never stored in the layout.
`PL-K285` decided the rules (project owner, 2026-09-27, ratified), and
`PL-30L5` Q2 changed one of them (project owner, 2026-10-11, ratified). This
module implements them as pure functions of a window's tree, with no toolkit,
so a test drives them with no `QApplication`. The adapter,
`app/area_layout.py`, draws exactly the sizes this module gives.

**A View's minimum size is a constraint, not a request** (`PL-K285` Q1). Each
Area has a *need*: the least size at which its View can be drawn. Where the
layout can give every Area its need, it does. An Area whose share of its split
would be smaller than its need is held at its need, and the other children of
that split give up the room in proportion to their fractions. So a View is
never drawn smaller than it needs and never clipped. The stored fractions are
not changed: they are the reader's proportions, and they apply again once the
extent is large enough.

**An Area that cannot be given its need says so** (`PL-K285` Q2 and Q3,
`PL-30L5` Q2). This happens when something the reader does asks for more room
than the extent has: a split whose halves are smaller than their View needs, a
View chosen for an Area too small for it, or a layout opened at a smaller size
than it was arranged at. Such an Area is *too small*, and it is given only its
*floor*. The floor is the least size at which the Area can show its header, the
notice's title, and a short statement of the size the View needs and the size
the Area has (`PL-Y65Q`). The adapter draws `PL-DB5G`'s notice in the Area, and
adds the notice's advice sentence only where the Area has room for it. The
adapter gives its host, as the adapter's least size, the `minimum_extent` of
every Area held at its `drawn_bound`: the larger of its need and its floor. A
host that can grow, such as the dashboard's scrolling page, grows to that size
instead, so no Area in it is too small. Nothing is
clipped, and nothing is collapsed to zero extent. Collapsing to zero is what
Blender does with `RGN_FLAG_TOO_SMALL` (`docs/interface-provenance.md`).

**Which Areas are too small is decided once per change, by `settle`.** Every
Area is first tried at its need. When the extent cannot hold every need, Areas
drop to their floors one at a time until the rest fit, so a small shortfall
blanks only the Areas that must give way (`PL-QZ7Z`). The Areas that the latest
change did not leave in place drop first. The Areas that the change left in
place drop only after them. So a split's new halves report themselves too
small, rather than taking the room from an Area the reader did not touch. Then
every Area that still has its need is drawn, and the rest are too small. A
too-small Area is drawn again as soon as a later change, such as a border drag
or a larger window, can give it its need.

**Pixels are apportioned as the adapter's splitters lay them out.** A split of
`n` children spends `n - 1` handles, each `handle_px` wide, along its axis,
and shares the rest among its children. Each share is rounded by
`pixel_sizes`, which is the one rounding that the adapter uses, so the sizes
here are the sizes on screen.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping
from collections.abc import Set as AbstractSet
from dataclasses import dataclass
from types import MappingProxyType

from anesthesia_sim.core.checked_number import shown
from anesthesia_sim.layout.exceptions import InvalidLayout
from anesthesia_sim.layout.tree import Area, AreaId, Node, Orientation, areas_in

__all__ = [
    "Apportionment",
    "Fit",
    "PixelSize",
    "TooSmall",
    "apportion",
    "border_share",
    "drawn_bounds",
    "minimum_extent",
    "pixel_sizes",
    "settle",
    "split_sizes",
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
        bounds: The least size each Area is held at: its `drawn_bounds`
            entry where it is drawn, and its floor where it is too small. The
            adapter sets each Area's frame's minimum size to this, so Qt never
            draws an Area below it.
        drawn: The Areas given their need, which draw their View.
        too_small: The Areas that are not given their need, in reading
            order, each with the size it needs and the size it has.
    """

    apportionment: Apportionment
    bounds: Mapping[AreaId, PixelSize]
    drawn: frozenset[AreaId]
    too_small: tuple[TooSmall, ...]


def pixel_sizes(fractions: tuple[float, ...], available: int) -> tuple[int, ...]:
    """Whole-pixel sizes in the proportion of `fractions`, summing to `available`.

    Each size is rounded down. The pixels left over then go, one each, to the
    sizes that lost the most in rounding. So the sizes sum to `available`
    exactly, and no size is more than a pixel from its share. Ties go to the
    earlier size.
    """

    exact = [fraction * available for fraction in fractions]
    sizes = [math.floor(share) for share in exact]
    left_over = max(0, min(len(sizes), available - sum(sizes)))
    by_loss = sorted(range(len(sizes)), key=lambda index: (sizes[index] - exact[index], index))

    for index in by_loss[:left_over]:
        sizes[index] += 1

    return tuple(sizes)


def split_sizes(
    fractions: tuple[float, ...], bounds: tuple[int, ...], available: int
) -> tuple[int, ...]:
    """Return the sizes along a split's axis that `apportion` gives its children.

    `bounds` holds each child's bound along the axis, and `available` the
    pixels the children share once the handles are taken out. Each child is
    held at its bound where its share would be less, and the others share the
    rest by their fractions (`_held_sizes`). Where the bounds need more than
    `available`, the sizes are `pixel_sizes` of the fractions alone.
    """

    held = _held_sizes(fractions, bounds, available)

    return held if held is not None else pixel_sizes(fractions, available)


def drawn_bounds(
    needs: Mapping[AreaId, PixelSize], floors: Mapping[AreaId, PixelSize]
) -> dict[AreaId, PixelSize]:
    """Return the size at which each Area is held while it draws its View.

    That size is the larger of the Area's need and its floor on each axis.

    An Area whose floor is wider or taller than its View's need is held at the
    floor on that axis, so its header still fits. `settle` holds a drawn Area
    at this bound, and the adapter's least size is the `minimum_extent` of
    these bounds (`PL-C9XP`). The sum of the needs alone would understate it.

    Raises:
        KeyError: `floors` has no size for an Area in `needs`.
    """

    return {area_id: _larger(need, floors[area_id]) for area_id, need in needs.items()}


def border_share(
    fractions: tuple[float, ...],
    index: int,
    bounds: tuple[int, ...],
    available: int,
    offset_px: int,
) -> float | None:
    """Return the share of a split that lies before border `index` once it is drawn at `offset_px`.

    The split's children have sizes `fractions` and bounds `bounds` along its
    axis, and share `available` pixels, as `split_sizes` lays them out. Border
    `index` lies between child `index` and the child after it, and moving it
    changes only those two children. `offset_px` is where the border is to be
    drawn: the pixels of the children before it.

    Where a child is held at its bound, every share in a range draws the
    border in one place. So the pointer is mapped through the drawn sizes, not
    through the fractions alone (`PL-97WX`). Of the shares that draw the
    border at `offset_px`, the result is the one nearest `offset_px /
    available`, the share that the fractions alone would give. Where no child
    is held, it is that share exactly. The border cannot be drawn past the
    place where a child beside it reaches its bound, so an `offset_px` past
    that place is taken as that place.

    The result is None when the border is already drawn at `offset_px`, or as
    near it as it can be drawn. A press, or a nudge toward an Area held at its
    bound, then leaves the stored fractions exactly as they were.

    Raises:
        IndexError: `index` is not a border of the split.
    """

    if not 0 <= index < len(fractions) - 1:
        raise IndexError(f"a split of {len(fractions)} children has no border {index}")

    before = math.fsum(fractions[:index])
    end = math.fsum(fractions[: index + 2])

    def drawn(share: float) -> int:
        trial = fractions[:index] + (share - before, end - share) + fractions[index + 2 :]

        return sum(split_sizes(trial, bounds, available)[: index + 1])

    # The ends themselves would leave a child with no share at all, so the
    # border's range is measured one float inside them.
    first, last = math.nextafter(before, end), math.nextafter(end, before)
    target = min(max(offset_px, drawn(first)), drawn(last))

    if target == drawn(before + fractions[index]):
        return None

    # The shares that draw the border at `target` run from the first share
    # that reaches it to the share just before the first that passes it.
    reaches = _first_share(first, last, lambda share: drawn(share) >= target)
    beyond = _first_share(first, last, lambda share: drawn(share) > target)
    passes = last if beyond is None else math.nextafter(beyond, first)
    assert reaches is not None, "the target is clamped to where the border can be drawn"

    return min(max(target / available, reaches), passes)


def _first_share(first: float, last: float, reached: Callable[[float], bool]) -> float | None:
    """Return the least share from `first` to `last` at which `reached` holds, or None.

    `reached` fails up to some share and holds from there to `last`. The
    share is found by halving the interval until no float lies between its
    ends.
    """

    if reached(first):
        return first

    if not reached(last):
        return None

    low, high = first, last

    while True:
        middle = (low + high) / 2

        if middle in (low, high):
            return high

        if reached(middle):
            high = middle
        else:
            low = middle


def minimum_extent(tree: Node, handle_px: int, bounds: Mapping[AreaId, PixelSize]) -> PixelSize:
    """Return the least extent at which every Area of `tree` can be given its bound.

    A row needs the sum of its children's widths and its handles, and the
    tallest of their heights. A column needs the same with the axes exchanged.

    Raises:
        TypeError: `handle_px` is not an `int`, or is a `bool`.
        InvalidLayout: `handle_px` is negative.
        KeyError: `bounds` has no bound for an Area of `tree`.
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
        TypeError: `extent` is not a `PixelSize`, or `handle_px` is not an `int`.
        InvalidLayout: `handle_px` is negative.
        KeyError: `bounds` has no bound for an Area of `tree`.
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
        # Each child is given at least one pixel, as the adapter's splitters
        # have always done, so that no Area is laid out with no extent at all.
        available = max(size.along(orientation) - handle_px * (count - 1), count)
        across = size.across(orientation)
        least = [_minimum_extent(child, handle_px, bounds) for child in node.children]
        child_bounds = tuple(each.along(orientation) for each in least)

        if sum(child_bounds) > available or any(
            each.across(orientation) > across for each in least
        ):
            unheld.append(path)

        sizes = split_sizes(node.sizes, child_bounds, available)
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
    Area is first held at its `drawn_bounds` entry, the larger of its need and
    its floor. While the extent cannot hold those bounds, one Area at a time
    drops to its floor, so a small shortfall blanks only the Areas that must
    give way (`PL-QZ7Z`). The Areas not in `kept` drop before any Area in
    `kept`. Within each group, the next to drop is the one whose drop leaves
    the least shortfall. A tie goes to the Area with the smaller share of the
    window, which is the one the reader gave the least room, and then to the
    later Area in reading order.

    Once the bounds fit, each dropped Area is tried at its need again, the
    last dropped first. It keeps its need wherever the bounds still fit. So an
    Area dropped early, before a later drop made room, is drawn after all.
    Every Area that is then given its need is drawn, and every other Area is
    too small.

    Raises:
        TypeError: `extent` is not a `PixelSize`, or `handle_px` is not an `int`.
        InvalidLayout: `handle_px` is negative.
        KeyError: `needs` or `floors` has no size for an Area of `tree`.
    """

    areas = tuple(areas_in(tree))
    held = drawn_bounds({area.id: needs[area.id] for area in areas}, floors)
    bounds = dict(held)
    shares = _shares(tree)
    reading = {area.id: index for index, area in enumerate(areas)}
    dropped: list[AreaId] = []

    def fits() -> bool:
        return not apportion(tree, extent, handle_px, bounds).unheld

    def shortfall_without(area_id: AreaId) -> int:
        trial = {**bounds, area_id: floors[area_id]}
        least = _minimum_extent(tree, handle_px, trial)

        return max(0, least.width_px - extent.width_px) + max(0, least.height_px - extent.height_px)

    while not fits():
        holding = [area.id for area in areas if bounds[area.id] != floors[area.id]]
        candidates = [area_id for area_id in holding if area_id not in kept] or holding

        if not candidates:
            # Every Area is already at its floor, so the extent is less than
            # even the floors need. The splits' sizes then follow their
            # fractions alone, and every Area smaller than its need is too
            # small.
            break

        drop = min(
            candidates,
            key=lambda area_id: (shortfall_without(area_id), shares[area_id], -reading[area_id]),
        )
        bounds[drop] = floors[drop]
        dropped.append(drop)

    if fits():
        for area_id in reversed(dropped):
            bounds[area_id] = held[area_id]

            if not fits():
                bounds[area_id] = floors[area_id]

    laid_out = apportion(tree, extent, handle_px, bounds)
    drawn = frozenset(area.id for area in areas if laid_out.areas[area.id].covers(needs[area.id]))
    final = {area.id: held[area.id] if area.id in drawn else floors[area.id] for area in areas}
    too_small = tuple(
        TooSmall(area.id, needs[area.id], laid_out.areas[area.id])
        for area in areas
        if area.id not in drawn
    )

    return Fit(laid_out, MappingProxyType(final), drawn, too_small)


def _held_sizes(
    fractions: tuple[float, ...], bounds: tuple[int, ...], available: int
) -> tuple[int, ...] | None:
    """Return sizes summing to `available`: each at least its bound, the rest shared by `fractions`.

    A child whose proportional share of what is left would be less than its
    bound is held at its bound, and the other children share what remains.
    This repeats until no share is less than its bound. When no child is held,
    the result is exactly `pixel_sizes(fractions, available)`. Returns None
    when the bounds sum to more than `available`.
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
        # Every child is held, so the pixels left over beyond the bounds go
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


def _shares(tree: Node) -> dict[AreaId, float]:
    """Return each Area's share of the window: the product of its fractions on the way down."""

    shares: dict[AreaId, float] = {}

    def visit(node: Node, share: float) -> None:
        if isinstance(node, Area):
            shares[node.id] = share

            return

        for child, fraction in zip(node.children, node.sizes, strict=True):
            visit(child, share * fraction)

    visit(tree, 1.0)

    return shares


def _larger(first: PixelSize, second: PixelSize) -> PixelSize:
    return PixelSize(max(first.width_px, second.width_px), max(first.height_px, second.height_px))


def _require_handle(handle_px: object) -> None:
    if isinstance(handle_px, bool) or not isinstance(handle_px, int):
        raise TypeError(f"a handle's width is an int, not {type(handle_px).__name__}")

    if handle_px < 0:
        raise InvalidLayout(f"a handle's width is zero or more pixels, not {shown(handle_px)}")
