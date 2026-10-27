"""Size a layout in whole pixels, and find the Areas that cannot get the size their View needs.

A layout stores fractions, so a file gives the same layout on any screen
(`PL-HJPY` Q5). How small an Area may be is a property of the screen. So it is
decided here, against an extent in pixels, and never stored in the layout.
`PL-K285` decided the rules (project owner, 2026-09-27, ratified), and
`PL-30L5` Q2 changed one of them (project owner, 2026-10-11, ratified). This
module implements them as pure functions of a window's tree, without the GUI
toolkit, so a test drives them with no `QApplication`. The adapter,
`app/area_layout.py`, draws exactly the sizes this module gives.

**A View's minimum size is a constraint, not a request** (`PL-K285` Q1). Each
Area has a *need*: the least size at which its View can be drawn. Where the
layout can give every Area its need, it does. An Area whose share of its split
would be smaller than its need is *held* at its need. The other children of
that split give up the room in proportion to their fractions. So a View is
never drawn smaller than its need, and never clipped. The stored fractions are
not changed. They are the reader's proportions, and they apply again once the
extent is large enough.

**An Area that cannot be given its need says so** (`PL-K285` Q2 and Q3,
`PL-30L5` Q2). This happens when something the reader does asks for more room
than the extent has. Examples are a split whose halves are smaller than their
Views need, a View chosen for an Area too small for it, or a layout opened at a
smaller size than it was arranged at. Such an Area is *too small*, and it is
given only its *floor*. In place of its View, the adapter draws a notice in it
(`PL-DB5G`). The floor is the least size at which the Area can show its header,
the notice's title, and a short statement of the size the View needs and the
size the Area has (`PL-Y65Q`). The adapter adds the notice's advice sentence
only where the Area has room for it. The adapter tells its host how small the
adapter may be. That least size is the `minimum_extent` of every Area held at
its `drawn_bounds` entry, which is the larger of its need and its floor. A
host that can grow, such as the dashboard's scrolling page, grows to that size,
so no Area in it is too small. Nothing is clipped, and nothing is collapsed to zero
extent. Collapsing to zero is what Blender does with `RGN_FLAG_TOO_SMALL`
(`docs/interface-provenance.md`).

**Which Areas are too small is decided once per change, by `settle`.** Every
Area is first tried at its need. When the extent cannot hold every need, the
fewest Areas that must give way drop to their floors. So a small shortfall
blanks only those Areas (`PL-QZ7Z`). The Areas that the latest change did not
leave in place drop first. The Areas that the change left in place drop only
where the others are not enough. So a split's new halves report themselves
too small, rather than taking the room from an Area the reader did not touch.
Then every Area that still has its need is drawn, and the rest are too small.
A too-small Area is drawn again as soon as a later change, such as a border
drag or a larger window, can give it its need.

**Pixels are shared out as the adapter's splitters lay them out.** A split of
`n` children has `n - 1` handles along its axis, each `handle_px` wide, and
shares the rest of its length among its children. `pixel_sizes` rounds each
share to whole pixels. It is the only rounding that the adapter uses, so the
sizes here are the sizes on screen.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping
from collections.abc import Set as AbstractSet
from dataclasses import dataclass
from itertools import combinations
from types import MappingProxyType
from typing import Final

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
    """Hold what `settle` decided: which Areas are drawn, which are too small, and every size.

    Attributes:
        apportionment: Every Area's and every split's size in pixels.
        bounds: The least size at which each Area is held. That is its
            `drawn_bounds` entry where the Area is drawn, and its floor where it
            is too small. The adapter sets the minimum size of each Area's frame
            to this bound, so Qt never draws an Area smaller than it.
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

    `bounds` holds each child's bound along the axis. `available` is the number
    of pixels the children share once the handles are taken out. A child whose
    share would be less than its bound is held at its bound, and the others
    share the rest by their fractions (`_held_sizes`). Where the bounds need
    more than `available`, the sizes are the ones that `pixel_sizes` gives for
    the fractions alone.
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
    at this bound. The adapter's least size is the `minimum_extent` of these
    bounds (`PL-C9XP`). A sum of the needs alone would understate that least
    size.

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

    The fractions of the split's children along its axis are `fractions`, and
    their bounds are `bounds`. The children share `available` pixels, as
    `split_sizes` lays them out. Border `index` lies between child `index` and
    the child after it. Moving the border changes only those two children's
    fractions. A held child can still move another border on screen, since it
    takes its pixels from every child that is not held. `offset_px` is where the
    border is to be drawn, given as the pixels of the children before it.

    While a child is held at its bound, a whole range of shares draws the
    border in the same place. So the pointer is mapped through the drawn sizes,
    not through the fractions alone (`PL-97WX`). Of the shares that draw the
    border at `offset_px`, the result is the one nearest `offset_px /
    available`, which is the share that the fractions alone would give. Where
    no child is held, the result is usually that share. The rounding in
    `pixel_sizes` can still leave the border drawn one pixel from the pointer.
    That is because a larger share does not always round to more pixels before
    the border. The border cannot be drawn past the place where a child beside
    it reaches its bound, so an `offset_px` past that place is taken as that
    place.

    The result is None when the border is already drawn at `offset_px`, or as
    near to it as it can be drawn. A press, or a nudge toward an Area held at its
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
    """Return the least share from `first` to `last` at which `reached` is true, or None.

    `reached` is false below some share and true from that share up to `last`.
    The share is found by halving the interval until no float lies between its
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

    `kept` names the Areas that were drawn before the change being settled, and
    that the change left with the same View in the same place. Every Area is
    first held at its `drawn_bounds` entry, the larger of its need and its
    floor. Where the extent cannot hold those bounds, some Areas drop to their
    floors. The Areas that drop are the fewest that must give way, so a small
    shortfall blanks only those (`PL-QZ7Z`). The rules below choose the Areas
    to drop. Each rule decides only among the choices that the rules before it
    leave tied.

    1. Leave the least shortfall that dropping Areas can reach. Where the floors
       fit, that is no shortfall.
    2. Drop the fewest Areas in `kept`, so a change's new Areas give way before
       the Areas it did not touch.
    3. Drop the fewest Areas in all.
    4. Drop the smallest share of the window, so the Views that the reader gave
       the least room give way first.
    5. Drop the later Areas in reading order.

    Where the tree has at most `_EXACT_SEARCH_AREAS` Areas, every subset of them
    is weighed. In a larger tree, Areas are dropped one at a time, each chosen
    by the same rules, until the shortfall is the least it can be. Every Area
    that is then given its need is drawn, and every other Area is too small.

    Raises:
        TypeError: `extent` is not a `PixelSize`, or `handle_px` is not an `int`.
        InvalidLayout: `handle_px` is negative.
        KeyError: `needs` or `floors` has no size for an Area of `tree`.
    """

    areas = tuple(areas_in(tree))
    held = drawn_bounds({area.id: needs[area.id] for area in areas}, floors)
    laid_out = apportion(tree, extent, handle_px, held)

    if laid_out.unheld:
        dropped = _dropped(tree, extent, handle_px, held, floors, kept)
        bounds = {
            area.id: floors[area.id] if area.id in dropped else held[area.id] for area in areas
        }
        laid_out = apportion(tree, extent, handle_px, bounds)

    drawn = frozenset(area.id for area in areas if laid_out.areas[area.id].covers(needs[area.id]))
    final = {area.id: held[area.id] if area.id in drawn else floors[area.id] for area in areas}
    too_small = tuple(
        TooSmall(area.id, needs[area.id], laid_out.areas[area.id])
        for area in areas
        if area.id not in drawn
    )

    return Fit(laid_out, MappingProxyType(final), drawn, too_small)


# `settle` weighs every subset of a tree's Areas when the tree has at most this
# many Areas. That is at most 1024 subsets, and each costs one walk of the tree.
# For ten Areas in a window too small for any of them, this took about 12 ms.
# For twelve Areas, it took 48 ms. For a larger tree, `settle` drops one Area at
# a time instead, which can drop more Areas than it needs to.
_EXACT_SEARCH_AREAS: Final = 10


def _dropped(
    tree: Node,
    extent: PixelSize,
    handle_px: int,
    held: Mapping[AreaId, PixelSize],
    floors: Mapping[AreaId, PixelSize],
    kept: AbstractSet[AreaId],
) -> frozenset[AreaId]:
    """Return the Areas that `settle` drops to their floors, by the rules its docstring lists."""

    order = [area.id for area in areas_in(tree)]
    reading = {area_id: index for index, area_id in enumerate(order)}
    shares = _shares(tree)
    # An Area already held at its floor gains nothing by dropping.
    holding = [area_id for area_id in order if held[area_id] != floors[area_id]]
    loose = [area_id for area_id in holding if area_id not in kept]
    fixed = [area_id for area_id in holding if area_id in kept]

    def shortfall(dropped: AbstractSet[AreaId]) -> int:
        bounds = {
            area_id: floors[area_id] if area_id in dropped else held[area_id] for area_id in order
        }
        least = _minimum_extent(tree, handle_px, bounds)

        return max(0, least.width_px - extent.width_px) + max(0, least.height_px - extent.height_px)

    def rank(dropped: AbstractSet[AreaId]) -> tuple[float, tuple[int, ...]]:
        return (
            math.fsum(shares[area_id] for area_id in dropped),
            tuple(sorted(-reading[area_id] for area_id in dropped)),
        )

    best = shortfall(frozenset(holding))

    if len(order) <= _EXACT_SEARCH_AREAS:
        for from_kept in range(len(fixed) + 1):
            for from_loose in range(len(loose) + 1):
                reaching = [
                    frozenset(first + second)
                    for first in combinations(fixed, from_kept)
                    for second in combinations(loose, from_loose)
                    if shortfall(frozenset(first + second)) == best
                ]

                if reaching:
                    return min(reaching, key=rank)

    dropped: frozenset[AreaId] = frozenset()

    while shortfall(dropped) > best:
        candidates = [area_id for area_id in loose if area_id not in dropped] or [
            area_id for area_id in fixed if area_id not in dropped
        ]
        choice = min(
            candidates,
            key=lambda area_id: (shortfall(dropped | {area_id}), rank(dropped | {area_id})),
        )
        dropped |= {choice}

    return dropped


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
