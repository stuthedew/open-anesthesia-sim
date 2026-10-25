"""The values a layout is built from: an Area, a Split, and one window's tree.

A window's content is a tree. Its leaves are **Areas**, and each Area holds one
View, named by its kind. Its inner nodes are **Splits**, and each Split divides
its rectangle among two or more children along one axis (`PL-C842`,
`PL-3J2P`). The terms come from Blender, as `.claude/rules/ui-areas.md` defines
them. That rule uses `View` in place of Blender's `Editor`, and gives the
reason.

**A split is a row or a column, never "horizontal" or "vertical".** Blender
names a split by the line it draws, so its *horizontal split* stacks two Areas
one above the other. Qt names a splitter by the direction in which it lays out
its children, so its `Qt.Horizontal` puts them side by side. The two
conventions mean opposite things, and a saved file outlives any reader's memory
of which convention it used. `ROW` lays children out left to right, and
`COLUMN` stacks them top to bottom. These are the words that CSS flexbox and
Flutter use for the same thing. The adapter (`PL-W9P6`) maps them onto Qt's
orientations.

**Sizes are fractions of the split's extent, never pixels**, so a file gives
the same layout on any screen (`PL-HJPY` Q5). A split has one size per child.
Each size is greater than zero, and together they sum to one. How small an Area
may be is a property of the screen it is shown on, so `layout/sizing.py`
decides it against an extent in pixels (`PL-K285`).

**A tree has only one form, except where four Areas meet at a point.** A split
has at least two children, and never has a child split of its own orientation.
A row inside a row is the same rectangle divided the same way as one wider row,
so the model writes it as the wider row. That leaves one tree for each
arrangement, except where four Areas meet at a point, as in a 2x2 grid. There,
either of the two cuts through the point can be the outer one. So the
arrangement has two trees, and which two Areas are siblings depends on which
cut came first. Nothing offered to the reader depends on that choice. A join
works from the rectangles, not the tree, and re-slices a junction where it
needs to (`PL-G60V`, in `layout/model.py`). A window's tree also nests no
deeper than `TREE_DEPTH_MAXIMUM`.

**An Area is addressed by an id, a whole number from 1.** The layout allocates
ids and never reuses one, so state kept for an Area id cannot reappear under a
different Area (`PL-HJPY` Q3). **A View kind is an opaque tag.** The layout
checks its syntax, keeps it verbatim and never asks what it names, so nothing
in this package knows that any concrete View exists (`PL-R1WQ` Q1). A tag
under which no View is registered is for the View registry to report. It does
not make the layout malformed (`PL-SSQW` Q5).

**Each id and each tag is a type that can be built only by passing its
check.** This is the pattern that `.claude/rules/core-domain.md` sets for
`core/`. `AreaId` is an `int` and `ViewKind` is a `str`. Each rejects an
invalid value when it is built. Every record after that point stores the type,
rather than checking a bare value again.
"""

from __future__ import annotations

import math
import re
from collections.abc import Iterator
from dataclasses import dataclass
from enum import Enum
from typing import Final

from anesthesia_sim.core.checked_number import shown
from anesthesia_sim.layout.exceptions import InvalidLayout

__all__ = [
    "AREA_ID_MAXIMUM",
    "LAYOUT_SIZE_SUM_TOLERANCE",
    "TREE_DEPTH_MAXIMUM",
    "VIEW_KIND_MAXIMUM_LENGTH",
    "Area",
    "AreaId",
    "Node",
    "Orientation",
    "Split",
    "ViewKind",
    "Window",
    "areas_in",
    "is_tag",
]

# The largest value an Area id can have: 2**53 - 1. RFC 8259 section 6 names
# this as the top of the range of integers on which every JSON implementation
# agrees exactly. A saved file is read back by its ids, so a value that a
# reader could round to its neighbour cannot serve as an id. The maximum also
# bounds the layout's counter. The counter is always greater than every id in
# use, and it cannot pass the maximum. So the last id that the layout allocates
# is 2**53 - 2, and no Area ever has the maximum itself as its id. Allocation
# runs in sequence from 1, so no layout reaches either value in use.
AREA_ID_MAXIMUM: Final = 2**53 - 1

# The greatest depth at which a split may sit in a window's tree, counting the
# root split as one deep. It is the largest number of splits on any path from
# the top of a window's tree down to an Area. A path that deep alternates row
# and column at every level, because a split never has a child of its own
# orientation. So 16 of its splits divide the window across, and 16 divide it
# down. Each of them gives at least one Area a share of its own. That puts 17
# Areas side by side along the path and 17 stacked, and the smallest of the
# stacked Areas is at most a seventeenth of the window's height. That is less
# than 64 px of a 1080 px screen. No workspace that a screen shows comes near
# that. The maximum is also far below Python's recursion limit. The reader
# recurses three frames per level and the operations two. So a tree this deep
# uses about a hundred of the thousand frames that Python allows by default,
# however deep in the stack its caller already is (`PL-1FT6`).
TREE_DEPTH_MAXIMUM: Final = 32

# The longest a View kind tag may be, in characters (`PL-R1WQ` Q1). A tag is
# an identifier a developer types once beside a factory and a file repeats
# verbatim, so the bound is generous for a name and short enough that a tag
# can never be mistaken for prose.
VIEW_KIND_MAXIMUM_LENGTH: Final = 40

# The tag syntax from `PL-R1WQ` Q1: lowercase snake case, beginning with a
# letter. The pattern sets no length, because each kind of tag sets its own
# limit. It is matched whole with `fullmatch`, because `$` also matches before a
# trailing newline and would accept "chart\n".
_TAG: Final = re.compile(r"[a-z][a-z0-9_]*")


def is_tag(text: str) -> bool:
    """Whether `text` is a tag: lowercase letters, digits and underscores, beginning with a letter.

    Every tag in the package shares this one grammar, such as a View kind or a
    shipped Workspace's id. Keeping it in one place means no second copy can
    drift from it.
    """

    return _TAG.fullmatch(text) is not None


# How far the sum of a split's sizes may differ from exactly one. An operation
# that rebuilds a split either rescales its sizes to sum to one before working
# on it, or works the sizes out afresh from where the split's borders lie
# (`layout/model.py`). So a split built by this code misses one by at most the
# few units in the last place that one operation's rounding adds, and no later
# operation inherits that error. A file may have sizes anywhere within this
# tolerance and is read as written. A file whose sizes miss one by more was not
# written by this code, and it is rejected rather than rescaled. The reader
# applies the same bound to a file as to a split built in code, so anything
# the model contains is written and read back unchanged.
LAYOUT_SIZE_SUM_TOLERANCE: Final = 1e-9


class AreaId(int):
    """An Area's id: a whole number from 1 to `AREA_ID_MAXIMUM`, built only through that check.

    It compares, hashes and prints as the `int` it was built from, so a
    mapping keyed by Area id finds an entry from either the id or the plain
    number. The layout allocates ids in sequence and never hands one out twice
    (`LayoutModel.next_area_id`).

    Raises:
        TypeError: the value is not an `int`, or is a `bool`, which subclasses
            `int` and would make `True` the Area with id 1.
        InvalidLayout: the value is less than 1 or greater than `AREA_ID_MAXIMUM`.
    """

    __slots__ = ()

    def __new__(cls, value: int) -> AreaId:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"an Area id is an int, not {type(value).__name__}")

        if not 1 <= value <= AREA_ID_MAXIMUM:
            raise InvalidLayout(
                f"an Area id is a whole number from 1 to {AREA_ID_MAXIMUM}, not {shown(value)}"
            )

        return super().__new__(cls, value)


class ViewKind(str):
    """The kind of View an Area holds, an opaque tag that is built only through its syntax check.

    The syntax comes from `PL-R1WQ` Q1: lowercase letters, digits and
    underscores, beginning with a letter, and at most `VIEW_KIND_MAXIMUM_LENGTH`
    characters long. A `ViewKind` compares and hashes as the `str` it was built
    from, so a registry keyed by plain strings finds it.

    Raises:
        TypeError: the tag is not a `str`.
        InvalidLayout: the tag does not have the syntax above.
    """

    __slots__ = ()

    def __new__(cls, tag: str) -> ViewKind:
        if not isinstance(tag, str):
            raise TypeError(f"a View kind is a str, not {type(tag).__name__}")

        if not is_tag(tag) or len(tag) > VIEW_KIND_MAXIMUM_LENGTH:
            raise InvalidLayout(
                f"a View kind is a tag of lowercase letters, digits and underscores, "
                f"beginning with a letter and at most {VIEW_KIND_MAXIMUM_LENGTH} long, "
                f"not {tag!r}"
            )

        return super().__new__(cls, tag)


class Orientation(Enum):
    """The axis a split divides its rectangle along."""

    ROW = "row"
    """Children sit side by side, left to right. The borders between them are vertical lines."""

    COLUMN = "column"
    """Children are stacked, top to bottom. The borders between them are horizontal lines."""


@dataclass(frozen=True, slots=True)
class Area:
    """A leaf of the tree: one View of the named kind, at an id unique to its layout.

    Raises:
        TypeError: `id` was not built as an `AreaId`, or `view` was not built
            as a `ViewKind`. Without this check, a bare `int` or `True` could
            name an Area unchecked.
    """

    id: AreaId
    view: ViewKind

    def __post_init__(self) -> None:
        if not isinstance(self.id, AreaId):
            raise TypeError(f"an Area's id is an AreaId, not {type(self.id).__name__}")

        if not isinstance(self.view, ViewKind):
            raise TypeError(f"an Area's view is a ViewKind, not {type(self.view).__name__}")


@dataclass(frozen=True, slots=True)
class Split:
    """An inner node: a rectangle divided among two or more children along one axis.

    `sizes[i]` is the fraction of the split's extent along its axis that
    `children[i]` takes, in the order `orientation` lays them out.

    Raises:
        TypeError: a field is not of its declared type.
        InvalidLayout: the split has fewer than two children, or its sizes
            are not one per child, or a size is not a finite number greater
            than zero. Also raised when the sum of the sizes misses one by more than
            `LAYOUT_SIZE_SUM_TOLERANCE`, which the message names, or when a
            child is a split of the same orientation. A tree's single form
            writes such a child's children as part of this split.
    """

    orientation: Orientation
    sizes: tuple[float, ...]
    children: tuple[Node, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.orientation, Orientation):
            raise TypeError(
                f"a split's orientation is an Orientation, not {type(self.orientation).__name__}"
            )

        if not isinstance(self.children, tuple):
            raise TypeError(f"a split's children are a tuple, not {type(self.children).__name__}")

        if not isinstance(self.sizes, tuple):
            raise TypeError(f"a split's sizes are a tuple, not {type(self.sizes).__name__}")

        for child in self.children:
            if not isinstance(child, Area | Split):
                raise TypeError(
                    f"a split's child is an Area or a Split, not {type(child).__name__}"
                )

        for size in self.sizes:
            if not isinstance(size, float):
                raise TypeError(f"a split's size is a float, not {type(size).__name__}")

        if len(self.children) < 2:
            raise InvalidLayout(
                f"a split holds two or more children, and this one holds {len(self.children)}"
            )

        if len(self.sizes) != len(self.children):
            raise InvalidLayout(
                f"a split's sizes are one per child, and this one has {len(self.sizes)} sizes "
                f"for {len(self.children)} children"
            )

        for size in self.sizes:
            if not math.isfinite(size) or size <= 0:
                raise InvalidLayout(
                    f"each of a split's sizes is a fraction of its extent above zero, not {size!r}"
                )

        total = math.fsum(self.sizes)

        if abs(total - 1) > LAYOUT_SIZE_SUM_TOLERANCE:
            raise InvalidLayout(
                f"a split's sizes sum to one, to within {LAYOUT_SIZE_SUM_TOLERANCE!r}, and these "
                f"sum to {total!r}"
            )

        for child in self.children:
            if isinstance(child, Split) and child.orientation is self.orientation:
                raise InvalidLayout(
                    f"a {self.orientation.value} split never holds another "
                    f"{self.orientation.value} split: the same rectangle divided the same way "
                    f"is one {self.orientation.value}, so the inner split's children belong "
                    "in the outer one"
                )


type Node = Area | Split
"""A node of a window's tree: an Area at a leaf, a Split anywhere above one."""


@dataclass(frozen=True, slots=True)
class Window:
    """One window's tree. `LayoutModel.windows[0]` is the main window (`PL-HJPY` Q1).

    The `LayoutModel` that contains the window checks the tree's depth against
    `TREE_DEPTH_MAXIMUM`. This class does not.

    Raises:
        TypeError: `tree` is not an `Area` or a `Split`.
    """

    tree: Node

    def __post_init__(self) -> None:
        if not isinstance(self.tree, Area | Split):
            raise TypeError(
                f"a window's tree is an Area or a Split, not {type(self.tree).__name__}"
            )


def areas_in(node: Node) -> Iterator[Area]:
    """Every Area under `node`, in reading order: depth first, each split's children in order."""

    if isinstance(node, Area):
        yield node
        return

    for child in node.children:
        yield from areas_in(child)
