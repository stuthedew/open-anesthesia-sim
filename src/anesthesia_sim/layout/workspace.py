"""A Workspace, and the ordered set of them a reader works in.

`docs/interface-provenance.md` adopts Blender's two levels: a **Workspace** is
a task-level object a reader switches between as a tab, and a layout is the
geometry of Areas in its windows (`PL-C842`, `PL-WV9K`). The layout is
`layout/model.py`'s; this module is what a Workspace carries beside it and how
the set of them behaves, as `PL-WV9K` decided (project owner, 2026-09-27,
ratified, over the alternative each answer names).

**What a Workspace carries** (`PL-WV9K` Q1): a `name`, unique in its set; an
`origin`, shipped under an id or the reader's own; its `LayoutModel`; and
`view_state`, each View's own saved state, held per Area id and per View kind
as a JSON object this module never reads (`PL-TH35`). Nothing else: no reader
preferences, which `ROADMAP.md` v0.6.0 entry 11 routes to a tier of their own,
no run data, and no window geometry. The run a Workspace pins is `PL-7Z84`'s,
and arrives with the run identity it holds.

**One retained entry per View kind per Area.** When an Area's View changes
and changes back, the outgoing View's state is kept under its kind rather than
destroyed, so the Area shows what it showed before: Blender's per-Area list of
`SpaceLink`s, bounded by construction at one entry per editor type, which
`docs/interface-provenance.md` records under "What survives a resize, a split,
a join, and a swap". State for an Area the layout no longer holds is dropped
when the layout changes: an Area id is never reused (`PL-HJPY` Q3), so that
state could never be shown again.

**The set is ordered, has one active Workspace, and is never empty**
(`PL-WV9K` Q2). `remove` raises `LastWorkspace` where it would empty the set:
`ROADMAP.md` item 34 takes Blender's refusal to delete the last workspace as
"a floor it enforces structurally rather than by warning", and a property of
the type is what structural means. Blender's `ED_workspace_delete` returns
false when the list `is_single()`
(`source/blender/editors/screen/workspace_edit.cc`, read 2026-09-27). Names
are unique, so a tab names one Workspace.

**Shipped against the reader's own** (`PL-WV9K` Q3): `Origin` says which, and
a shipped Workspace is edited in place, since a copy-on-write fork was refused
as a hidden mode. "Reset this Workspace" replaces it from its shipped JSON
through `WorkspaceSet.replace`, "Restore shipped Workspaces" is `add`, and a
duplicate of any Workspace is the reader's own.

**Values, as the layout is.** Every operation returns a new set and leaves the
one it was called on as it was; a refused one raises and changes nothing. The
file the set is saved to is `layout/store.py`'s.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from types import MappingProxyType
from typing import Final

from anesthesia_sim.core.checked_number import shown
from anesthesia_sim.layout.exceptions import (
    InvalidLayout,
    LastWorkspace,
    LayoutRefused,
    NotInWorkspaceSet,
)
from anesthesia_sim.layout.model import LayoutModel
from anesthesia_sim.layout.tree import AreaId, ViewKind, is_tag

__all__ = [
    "MINE",
    "SHIPPED_PREFIX",
    "Origin",
    "ShippedWorkspaceId",
    "ViewState",
    "Workspace",
    "WorkspaceName",
    "WorkspaceSet",
]

# The written forms of an origin, which `Origin.written` writes and
# `Origin.from_written` reads: the reader's own, or shipped under an id.
MINE: Final = "mine"
SHIPPED_PREFIX: Final = "shipped:"

# The word a duplicate's name carries after its source's: "<name> (copy)",
# then "<name> (copy 2)" and on where that is taken too.
_COPY_WORD: Final = "copy"


class WorkspaceName(str):
    """A Workspace's name as its tab shows it, built only through its check.

    Raises:
        TypeError: the name is not a `str`.
        InvalidLayout: the name is empty, begins or ends with whitespace, or
            holds a character that does not print - a newline or a control
            character, which a tab could not show.
    """

    __slots__ = ()

    def __new__(cls, name: str) -> WorkspaceName:
        if not isinstance(name, str):
            raise TypeError(f"a Workspace name is a str, not {type(name).__name__}")

        if not name:
            raise InvalidLayout("a Workspace name is not empty")

        if name != name.strip():
            raise InvalidLayout(
                f"a Workspace name has no leading or trailing whitespace, and {name!r} does"
            )

        if not name.isprintable():
            raise InvalidLayout(
                f"a Workspace name holds printing characters only, and {name!r} does not"
            )

        return super().__new__(cls, name)


class ShippedWorkspaceId(str):
    """The id a shipped Workspace is known by: the stem of its file under `data/workspaces/`.

    A tag, as `layout/tree.py`'s `is_tag` defines one, of any length: the
    shipped ones are bounded by the file names they are the stems of, and a
    reader's file naming a longer one names nothing shipped, which the
    interface reports as a Workspace of unknown origin rather than as a
    malformed file.

    Raises:
        TypeError: the id is not a `str`.
        InvalidLayout: the id is not a tag of lowercase letters, digits and
            underscores beginning with a letter.
    """

    __slots__ = ()

    def __new__(cls, shipped_id: str) -> ShippedWorkspaceId:
        if not isinstance(shipped_id, str):
            raise TypeError(f"a shipped Workspace id is a str, not {type(shipped_id).__name__}")

        if not is_tag(shipped_id):
            raise InvalidLayout(
                "a shipped Workspace id is a tag of lowercase letters, digits and underscores, "
                f"beginning with a letter, not {shipped_id!r}"
            )

        return super().__new__(cls, shipped_id)


@dataclass(frozen=True, slots=True)
class Origin:
    """Where a Workspace came from: shipped under `shipped_id`, or the reader's own when `None`.

    Written as `"mine"` or `"shipped:<id>"` by `written`, and read back by
    `from_written`; the grammar lives here and nowhere else.

    Raises:
        TypeError: `shipped_id` is neither `None` nor a `ShippedWorkspaceId`.
    """

    shipped_id: ShippedWorkspaceId | None

    def __post_init__(self) -> None:
        if self.shipped_id is not None and not isinstance(self.shipped_id, ShippedWorkspaceId):
            raise TypeError(
                "an origin's shipped_id is a ShippedWorkspaceId or None, not "
                f"{type(self.shipped_id).__name__}"
            )

    @classmethod
    def mine(cls) -> Origin:
        """The reader's own: made, duplicated or saved by them."""

        return cls(None)

    @classmethod
    def shipped(cls, shipped_id: ShippedWorkspaceId) -> Origin:
        """Shipped with the application under `shipped_id`, whether or not since edited."""

        return cls(shipped_id)

    @property
    def is_shipped(self) -> bool:
        return self.shipped_id is not None

    def written(self) -> str:
        """The origin as a file holds it: `"mine"`, or `"shipped:"` and the id."""

        if self.shipped_id is None:
            return MINE

        return f"{SHIPPED_PREFIX}{self.shipped_id}"

    @classmethod
    def from_written(cls, written: str) -> Origin:
        """The origin `written` names, as `written()` wrote it.

        Raises:
            TypeError: `written` is not a `str`.
            InvalidLayout: `written` is neither `"mine"` nor `"shipped:"`
                followed by a valid id.
        """

        if not isinstance(written, str):
            raise TypeError(f"an origin is written as a str, not {type(written).__name__}")

        if written == MINE:
            return cls.mine()

        if written.startswith(SHIPPED_PREFIX):
            return cls.shipped(ShippedWorkspaceId(written[len(SHIPPED_PREFIX) :]))

        raise InvalidLayout(
            f"an origin is written {MINE!r} or {SHIPPED_PREFIX!r} followed by the shipped "
            f"Workspace's id, not {written!r}"
        )


type ViewState = Mapping[AreaId, Mapping[ViewKind, Mapping[str, object]]]
"""Each View's saved state: per Area id, per View kind, a JSON object the Workspace never reads."""


@dataclass(frozen=True, slots=True)
class Workspace:
    """A named layout with each View's own saved state: one tab of the set.

    `view_state` is held as the JSON it will be written as - a private copy,
    read-only at its two outer levels and at the top of each state, read back
    through `state_of`, which hands out a copy - and every Area id in it is an
    Area the layout holds. A View's state is a record of named fields, so each
    entry is a JSON object whose keys are strings at every depth; what the
    fields mean is the View's.

    Raises:
        TypeError: a field is not of its declared type; a `view_state` key is
            not an `AreaId` or a `ViewKind`; or a state is not a mapping, or
            holds a mapping at any depth, whose keys are not all strings,
            which `json` would otherwise rewrite as strings and could run
            together.
        InvalidLayout: `view_state` names an Area the layout does not hold, or
            holds a state that is not JSON - a value `json` cannot write, or
            `NaN` or infinity, which the file refuses.
    """

    name: WorkspaceName
    origin: Origin
    layout: LayoutModel
    view_state: ViewState = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.name, WorkspaceName):
            raise TypeError(
                f"a Workspace's name is a WorkspaceName, not {type(self.name).__name__}"
            )

        if not isinstance(self.origin, Origin):
            raise TypeError(f"a Workspace's origin is an Origin, not {type(self.origin).__name__}")

        if not isinstance(self.layout, LayoutModel):
            raise TypeError(
                f"a Workspace's layout is a LayoutModel, not {type(self.layout).__name__}"
            )

        if not isinstance(self.view_state, Mapping):
            raise TypeError(
                f"a Workspace's view_state is a mapping, not {type(self.view_state).__name__}"
            )

        held = {area.id for area in self.layout.areas()}
        copied: dict[AreaId, Mapping[ViewKind, Mapping[str, object]]] = {}

        for area_id, kinds in self.view_state.items():
            if not isinstance(area_id, AreaId):
                raise TypeError(f"view_state is keyed by AreaId, not {type(area_id).__name__}")

            if area_id not in held:
                raise InvalidLayout(
                    f"view_state names Area {area_id}, which the layout does not hold"
                )

            if not isinstance(kinds, Mapping):
                raise TypeError(
                    f"the state of Area {area_id} is a mapping by View kind, not "
                    f"{type(kinds).__name__}"
                )

            copied[area_id] = MappingProxyType(
                {kind: _json_copy(area_id, kind, state) for kind, state in kinds.items()}
            )

        object.__setattr__(self, "view_state", MappingProxyType(copied))

    def state_of(self, area_id: AreaId, view: ViewKind) -> dict[str, object] | None:
        """A copy of the state kept for the View of kind `view` in Area `area_id`, or `None`.

        The copy is the caller's to change; the Workspace holds its own.
        """

        state = self.view_state.get(area_id, {}).get(view)

        return None if state is None else _json_round_trip(state)

    def with_view_state(
        self, area_id: AreaId, view: ViewKind, state: Mapping[str, object]
    ) -> Workspace:
        """This Workspace with `state` kept for the View of kind `view` in Area `area_id`.

        One entry is kept per kind per Area, so a state already kept for that
        kind is replaced and every other kind's is left.

        Raises:
            NotInLayout: `area_id` names no Area the layout holds.
            TypeError, InvalidLayout: as the constructor raises them for the
                state.
        """

        self.layout.area(area_id)

        kinds = dict(self.view_state.get(area_id, {}))
        kinds[view] = state

        return replace(self, view_state={**self.view_state, area_id: kinds})

    def with_layout(self, layout: LayoutModel) -> Workspace:
        """This Workspace showing `layout`, keeping the state of every Area the new layout holds.

        State kept for an Area the new layout does not hold is dropped: its id
        is never reused, so nothing could show it again.

        Raises:
            TypeError: `layout` is not a `LayoutModel`.
        """

        if not isinstance(layout, LayoutModel):
            raise TypeError(f"a Workspace's layout is a LayoutModel, not {type(layout).__name__}")

        held = {area.id for area in layout.areas()}
        kept = {area_id: kinds for area_id, kinds in self.view_state.items() if area_id in held}

        return replace(self, layout=layout, view_state=kept)

    def renamed(self, name: WorkspaceName) -> Workspace:
        """This Workspace under `name`. Whether the name is free is the set's question."""

        return replace(self, name=name)

    def as_mine(self) -> Workspace:
        """This Workspace as the reader's own, whatever it was."""

        return replace(self, origin=Origin.mine())


@dataclass(frozen=True, slots=True)
class WorkspaceSet:
    """The reader's Workspaces, in tab order, with the one they are working in.

    `active` is a position in `workspaces`. The set is never empty and no two
    Workspaces share a name. Every operation returns a new set and refuses by
    raising, leaving this one as it was.

    Raises:
        TypeError: a field is not of its declared type.
        InvalidLayout: the set is empty, two Workspaces share a name, or
            `active` is not a position in it.
    """

    workspaces: tuple[Workspace, ...]
    active: int

    def __post_init__(self) -> None:
        if not isinstance(self.workspaces, tuple):
            raise TypeError(f"a set's workspaces are a tuple, not {type(self.workspaces).__name__}")

        for workspace in self.workspaces:
            if not isinstance(workspace, Workspace):
                raise TypeError(f"a set holds Workspaces, not {type(workspace).__name__}")

        if isinstance(self.active, bool) or not isinstance(self.active, int):
            raise TypeError(f"a set's active position is an int, not {type(self.active).__name__}")

        if not self.workspaces:
            raise InvalidLayout("a Workspace set holds at least one Workspace")

        seen: set[WorkspaceName] = set()

        for workspace in self.workspaces:
            if workspace.name in seen:
                raise InvalidLayout(
                    f"two Workspaces are named {workspace.name!r}, and names are unique so a "
                    "tab names one Workspace"
                )

            seen.add(workspace.name)

        if not 0 <= self.active < len(self.workspaces):
            raise InvalidLayout(
                f"the active position is {shown(self.active)}, and this set's positions run "
                f"from 0 to {len(self.workspaces) - 1}"
            )

    @property
    def current(self) -> Workspace:
        """The Workspace the reader is working in."""

        return self.workspaces[self.active]

    def position_of(self, name: WorkspaceName) -> int:
        """Where the Workspace named `name` sits.

        Raises:
            NotInWorkspaceSet: no Workspace of that name is in the set.
        """

        for position, workspace in enumerate(self.workspaces):
            if workspace.name == name:
                return position

        raise NotInWorkspaceSet(f"no Workspace in the set is named {name!r}")

    def add(self, workspace: Workspace, at: int | None = None) -> WorkspaceSet:
        """The set with `workspace` inserted at `at` - the end, by default - and active.

        Raises:
            TypeError: `workspace` is not a `Workspace`, or `at` is not an `int`.
            NotInWorkspaceSet: `at` is not a position in the set or the one
                after its last.
            LayoutRefused: a Workspace of that name is already in the set.
        """

        if not isinstance(workspace, Workspace):
            raise TypeError(f"a set holds Workspaces, not {type(workspace).__name__}")

        position = len(self.workspaces) if at is None else self._position(at, inclusive=True)
        self._require_free(workspace.name)

        workspaces = (*self.workspaces[:position], workspace, *self.workspaces[position:])

        return WorkspaceSet(workspaces, position)

    def duplicate(self, index: int) -> WorkspaceSet:
        """The set with a copy of the Workspace at `index` after it, the reader's own and active.

        The copy is named after its source with " (copy)", or " (copy 2)" and
        on where that name is taken, so the two tabs read apart.

        Raises:
            TypeError: `index` is not an `int`.
            NotInWorkspaceSet: `index` is not a position in the set.
        """

        position = self._position(index)
        source = self.workspaces[position]
        taken = {workspace.name for workspace in self.workspaces}
        copy = source.renamed(_copy_name(source.name, taken)).as_mine()

        return self.add(copy, at=position + 1)

    def rename(self, index: int, name: WorkspaceName) -> WorkspaceSet:
        """The set with the Workspace at `index` named `name`.

        Raises:
            TypeError: `index` is not an `int`, or `name` not a `WorkspaceName`.
            NotInWorkspaceSet: `index` is not a position in the set.
            LayoutRefused: another Workspace already has that name.
        """

        position = self._position(index)

        if not isinstance(name, WorkspaceName):
            raise TypeError(f"a Workspace's name is a WorkspaceName, not {type(name).__name__}")

        if name != self.workspaces[position].name:
            self._require_free(name)

        return self._with(position, self.workspaces[position].renamed(name))

    def move(self, index: int, to: int) -> WorkspaceSet:
        """The set with the Workspace at `index` moved to `to`; the active Workspace stays active.

        Raises:
            TypeError: `index` or `to` is not an `int`.
            NotInWorkspaceSet: `index` or `to` is not a position in the set.
        """

        source = self._position(index)
        target = self._position(to)
        moved = list(self.workspaces)
        workspace = moved.pop(source)
        moved.insert(target, workspace)

        return WorkspaceSet(tuple(moved), moved.index(self.current))

    def remove(self, index: int) -> WorkspaceSet:
        """The set without the Workspace at `index`.

        Where the removed Workspace was active, the one that takes its
        position is, or the new last one where it was last.

        Raises:
            TypeError: `index` is not an `int`.
            NotInWorkspaceSet: `index` is not a position in the set.
            LastWorkspace: the set holds one Workspace, which cannot be removed.
        """

        position = self._position(index)

        if len(self.workspaces) == 1:
            raise LastWorkspace(
                f"the set holds one Workspace, {self.workspaces[0].name!r}, and a reader always "
                "has one, so it cannot be removed"
            )

        remaining = (*self.workspaces[:position], *self.workspaces[position + 1 :])

        if position < self.active:
            active = self.active - 1
        elif position == self.active:
            active = min(position, len(remaining) - 1)
        else:
            active = self.active

        return WorkspaceSet(remaining, active)

    def activate(self, index: int) -> WorkspaceSet:
        """The set with the Workspace at `index` active.

        Raises:
            TypeError: `index` is not an `int`.
            NotInWorkspaceSet: `index` is not a position in the set.
        """

        return WorkspaceSet(self.workspaces, self._position(index))

    def replace(self, index: int, workspace: Workspace) -> WorkspaceSet:
        """The set with `workspace` in place of the one at `index`.

        How a layout operation, a View's saved state or a reset from shipped
        JSON reaches the set: the Workspace is rebuilt and put back.

        Raises:
            TypeError: `index` is not an `int`, or `workspace` not a `Workspace`.
            NotInWorkspaceSet: `index` is not a position in the set.
            LayoutRefused: another Workspace already has the new one's name.
        """

        position = self._position(index)

        if not isinstance(workspace, Workspace):
            raise TypeError(f"a set holds Workspaces, not {type(workspace).__name__}")

        if workspace.name != self.workspaces[position].name:
            self._require_free(workspace.name)

        return self._with(position, workspace)

    def _position(self, index: int, *, inclusive: bool = False) -> int:
        """`index` as a position in the set, or one past its end where `inclusive`."""

        if isinstance(index, bool) or not isinstance(index, int):
            raise TypeError(f"a position in the set is an int, not {type(index).__name__}")

        last = len(self.workspaces) if inclusive else len(self.workspaces) - 1

        if not 0 <= index <= last:
            raise NotInWorkspaceSet(
                f"the set has no position {shown(index)}: its positions run from 0 to {last}"
            )

        return index

    def _require_free(self, name: WorkspaceName) -> None:
        if any(workspace.name == name for workspace in self.workspaces):
            raise LayoutRefused(
                f"a Workspace named {name!r} is already in the set, and names are unique so a "
                "tab names one Workspace"
            )

    def _with(self, position: int, workspace: Workspace) -> WorkspaceSet:
        workspaces = (*self.workspaces[:position], workspace, *self.workspaces[position + 1 :])

        return WorkspaceSet(workspaces, self.active)


def _json_copy(area_id: AreaId, kind: object, state: object) -> Mapping[str, object]:
    """`state` as the JSON object it will be written as, read-only; refuses what is not one."""

    if not isinstance(kind, ViewKind):
        raise TypeError(
            f"the state of Area {area_id} is keyed by ViewKind, not {type(kind).__name__}"
        )

    if not isinstance(state, Mapping):
        raise TypeError(
            f"the state of Area {area_id}'s {kind} View is a mapping, not {type(state).__name__}"
        )

    pending: list[object] = [state]

    while pending:
        value = pending.pop()

        if isinstance(value, Mapping):
            for key, member in value.items():
                if not isinstance(key, str):
                    raise TypeError(
                        f"the state of Area {area_id}'s {kind} View is keyed by str at every "
                        f"depth, not {type(key).__name__}"
                    )

                pending.append(member)
        elif isinstance(value, list | tuple):
            pending.extend(value)

    try:
        return MappingProxyType(_json_round_trip(state))
    except (TypeError, ValueError) as error:
        raise InvalidLayout(
            f"the state of Area {area_id}'s {kind} View is not JSON a file can hold: {error}"
        ) from None


def _json_round_trip(state: Mapping[str, object]) -> dict[str, object]:
    """A fresh copy of `state` as JSON reads it back: plain dicts and lists, sharing nothing.

    Raises:
        TypeError, ValueError: `json` cannot write `state` - a value of a type
            it has no form for, or `NaN` or infinity.
    """

    loaded: dict[str, object] = json.loads(json.dumps(dict(state), allow_nan=False))

    return loaded


def _copy_name(name: WorkspaceName, taken: set[WorkspaceName]) -> WorkspaceName:
    """The first of "<name> (copy)", "<name> (copy 2)", "<name> (copy 3)" ... not in `taken`."""

    candidate = WorkspaceName(f"{name} ({_COPY_WORD})")
    count = 1

    while candidate in taken:
        count += 1
        candidate = WorkspaceName(f"{name} ({_COPY_WORD} {count})")

    return candidate
