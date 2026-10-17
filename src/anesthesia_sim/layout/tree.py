"""The values a layout is built from: an Area, a Split, and one window's tree.

A window's content is a tree. Its leaves are **Areas**, each holding one View,
named by its kind; its inner nodes are **Splits**, each dividing its rectangle
among two or more children along one axis (`PL-C842`, `PL-3J2P`). The words
are Blender's, as `.claude/rules/ui-areas.md` fixes them, and `View` replaces
Blender's `Editor` there for the reason given.

**A split is a row or a column, never "horizontal" or "vertical".** Blender
names a split by the line it draws, so its *horizontal split* stacks two
Areas one above the other; Qt names a splitter by the direction it lays its
children out in, so its `Qt.Horizontal` puts them side by side. The two read
opposite ways, and a saved file outlives any reader's memory of which
convention it used. `ROW` lays children out left to right and `COLUMN` stacks
them top to bottom, in the words CSS flexbox and Flutter use for the same
thing, and the adapter (`PL-W9P6`) maps them onto Qt's orientations.

**Sizes are fractions of the split's extent**, one per child, each above zero
and together one, never pixels, so a file reads the same on any screen
(`PL-HJPY` Q5). How small an Area may be is a property of the screen it is
shown on, and is `PL-K285`'s.

**A tree takes one form, wherever no four Areas meet at a point.** A split
holds at least two children, and never a child split of its own orientation: a
row inside a row is the same rectangle divided the same way as one wider row,
and the model writes it as the wider row. That leaves one tree per arrangement
except where four Areas meet at a point. Elsewhere, two Areas that sit next to
each other in one split are exactly the pairs the tree can join, however it
was built (`PL-3J2P`'s refusal, which the model in `layout/model.py`
implements). Where four Areas do meet at a point - a 2x2 grid - either of the
two cuts through it can be the outer one, so the arrangement has two trees:
which two Areas are siblings, and so whether a join is available, depends on
which cut came first. Whether a join should re-slice such a junction is an
open decision (`PL-G60V`). A window's tree also nests no deeper than
`TREE_DEPTH_MAXIMUM`.

**An Area is addressed by an id, a whole number from 1** that the layout
allocates and never reuses, so state kept per Area id cannot be resurrected
under a different Area (`PL-HJPY` Q3). **A View kind is an opaque tag**: the
layout checks its syntax, keeps it verbatim and never asks what it names, so
nothing here knows a concrete View exists (`PL-R1WQ` Q1). A tag no View is
registered under is the registry's question and not a malformed layout
(`PL-SSQW` Q5).

**Each id and each tag is a type built only through its check**, the pattern
`.claude/rules/core-domain.md` gives `core/`: `AreaId` is an `int` and
`ViewKind` a `str` that refuse, as they are built, what could not be one, and
every record past that point holds the type rather than checking a bare value
again.
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

# The largest an Area id can be: 2**53 - 1, the top of the range of integers
# RFC 8259 section 6 names as the one every JSON implementation agrees on
# exactly. An id is a key a saved file is read back by, so one a reader could
# round to its neighbour is not an id. It bounds the layout's counter too,
# which stays above every id in use and so cannot pass it: the last id the
# layout allocates is 2**53 - 2, and no Area ever holds this one. Allocation
# runs in sequence from 1, so no layout reaches either by use.
AREA_ID_MAXIMUM: Final = 2**53 - 1

# The deepest a split may sit in a window's tree, the root split being one
# deep: the most splits on any path from a window's tree down to an Area. A
# path that deep alternates row and column at every level, since a split never
# holds one of its own orientation, so 16 of its splits divide the window across
# and 16 down it, each giving at least one Area a share of its own: 17 Areas
# stand side by side along the path and 17 stacked, and the smallest of the
# stacked is at most a seventeenth of the window's height, under 64 px of a
# 1080 px screen. No workspace a screen shows comes near that. It also sits far below
# the recursion ceiling: the reader recurses three frames a level and the
# operations two, so a tree this deep costs about a hundred of the thousand
# frames Python allows by default, wherever its caller stands (`PL-1FT6`).
TREE_DEPTH_MAXIMUM: Final = 32

# The longest a View kind tag may be, in characters (`PL-R1WQ` Q1). A tag is
# an identifier a developer types once beside a factory and a file repeats
# verbatim, so the bound is generous for a name and short enough that a tag
# can never be mistaken for prose.
VIEW_KIND_MAXIMUM_LENGTH: Final = 40

# `PL-R1WQ` Q1's syntax: lowercase snake case, beginning with a letter, at any
# length - each kind of tag bounds its own. Matched whole with `fullmatch`,
# because `$` also matches before a trailing newline and would admit "chart\n".
_TAG: Final = re.compile(r"[a-z][a-z0-9_]*")


def is_tag(text: str) -> bool:
    """Whether `text` is a tag: lowercase letters, digits and underscores, beginning with a letter.

    The one grammar every tag in the package shares - a View kind, a shipped
    Workspace's id - so a second copy of it cannot drift from this one.
    """

    return _TAG.fullmatch(text) is not None


# How far a split's sizes may sum from exactly one. An operation rescales each
# split it rebuilds to sum to one before working on it (`layout/model.py`), so
# the most a split built by this code misses one by is the few units in the
# last place one operation's rounding adds, which no later operation inherits.
# A file can hold sizes anywhere inside this and is read as written, and one
# whose sizes miss one by more was not written by this code, and is refused
# rather than rescaled. The reader holds a file to the same bound as a split
# built in code, so whatever the model holds it writes and reads back equal.
LAYOUT_SIZE_SUM_TOLERANCE: Final = 1e-9


class AreaId(int):
    """An Area's id: a whole number from 1 to `AREA_ID_MAXIMUM`, built only through that check.

    It compares, hashes and prints as the `int` it was built from, so a
    mapping keyed by Area id finds it from either. The layout allocates ids in
    sequence and never hands one out twice (`LayoutModel.next_area_id`).

    Raises:
        TypeError: the value is not an `int`, or is a `bool`, which subclasses
            `int` and would make `True` the Area with id 1.
        InvalidLayout: the value is below 1 or above `AREA_ID_MAXIMUM`.
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
    """The kind of View an Area holds: an opaque tag, built only through its syntax check.

    The syntax is `PL-R1WQ` Q1's - lowercase letters, digits and underscores,
    beginning with a letter, at most `VIEW_KIND_MAXIMUM_LENGTH` long. It
    compares and hashes as the `str` it was built from, so a registry keyed by
    plain strings finds it.

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
    """Children side by side, left to right; the borders between them are vertical lines."""

    COLUMN = "column"
    """Children stacked, top to bottom; the borders between them are horizontal lines."""


@dataclass(frozen=True, slots=True)
class Area:
    """A leaf of the tree: one View, of the kind named, at an id unique to its layout.

    Raises:
        TypeError: `id` was not built as an `AreaId` - a bare `int`, or
            `True`, would otherwise name an Area unchecked - or `view` as a
            `ViewKind`.
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
        InvalidLayout: the split holds fewer than two children; its sizes are
            not one per child; a size is not finite and above zero; the sizes
            miss a sum of one by more than `LAYOUT_SIZE_SUM_TOLERANCE`, which
            the message names; or a child is a split of the same orientation,
            which the one form a tree takes writes as part of this split.
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

    How deep the tree nests is checked by the `LayoutModel` holding it, against
    `TREE_DEPTH_MAXIMUM`, not here.

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
