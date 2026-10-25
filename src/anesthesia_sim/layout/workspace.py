"""A Workspace, and the ordered set of them a reader works in.

`docs/interface-provenance.md` adopts Blender's two levels. A **Workspace** is
a task-level object that a reader switches to by its tab. A layout is the
geometry of the Areas in a Workspace's windows (`PL-C842`, `PL-WV9K`).
`layout/model.py` defines the layout. This module defines what a Workspace
carries beside its layout, and how a set of Workspaces behaves. `PL-WV9K`
decided both (project owner, 2026-09-27, ratified, over the alternative that
each of its answers names).

**What a Workspace carries, and so what its saved form contains** (`PL-WV9K`
Q1). A Workspace has these fields:

- a `name`, unique within its set;
- an `origin`, which says whether it was shipped under an id or is the
  reader's own;
- its layout, a `LayoutModel`;
- `view_state`, each View's own saved state, stored per Area id and per View
  kind as a JSON object that this module never inspects (`PL-TH35`);
- `pinned_run`, the identity of the run its Views show, or `None`
  (`PL-7Z84`).

A Workspace carries nothing else. It carries no reader preferences, which
`ROADMAP.md` v0.6.0 entry 11 assigns to a tier of their own. It carries no run
data and no window geometry. Runs belong to the session rather than to a
Workspace. So switching Workspaces changes which run a View shows, and never
changes the run itself.

**A pin names a run. When the pinned run is absent, the Workspace says so
rather than showing another run** (`PL-WV9K` Q6, `PL-7Z84`). When a Workspace
is unpinned, its Views show the runs the session has open. When it is pinned,
they show the pinned run alone. When the pinned run is not open, `shown_runs`
returns `PinnedRunAbsent` and no run at all, so a caller cannot draw another
run in its place. An absent pinned run is the usual case for a pin read back
from the saved file. Nothing saves a run from one session to the next, and an
identity from another session never matches one created in this session
(`layout/run_identity.py`).

**Each Area keeps one state entry per View kind.** When an Area's View changes
to another kind, the outgoing View's state is kept under its kind rather than
destroyed. So when the Area changes back, it shows what it showed before. This
follows Blender's per-Area list of `SpaceLink`s, which by construction holds
at most one entry per editor type. `docs/interface-provenance.md` records it
under "What survives a resize, a split, a join, and a swap". When the layout
changes, the state of any Area that the layout no longer contains is dropped.
An Area id is never reused (`PL-HJPY` Q3), so that state could never be shown
again.

**The set is ordered, has one active Workspace, and is never empty**
(`PL-WV9K` Q2). `remove` raises `LastWorkspace` when removing would empty the
set. `ROADMAP.md` item 34 takes Blender's refusal to delete the last workspace
as "a floor it enforces structurally rather than by warning". Here,
"structurally" means that the rule is a property of the type. Blender's
`ED_workspace_delete` returns false when the list `is_single()`
(`source/blender/editors/screen/workspace_edit.cc`, read 2026-09-27). Names
are unique, so each tab names exactly one Workspace.

**Shipped Workspaces and the reader's own** (`PL-WV9K` Q3). `Origin` says
which kind a Workspace is. A shipped Workspace is edited in place. A
copy-on-write fork was rejected, because it would be a hidden mode. "Reset
this Workspace" replaces a shipped Workspace from its shipped JSON through
`WorkspaceSet.replace`. "Restore shipped Workspaces" uses `add`. A duplicate
of any Workspace is the reader's own.

**Workspaces and sets are values, as the layout is.** Every operation returns
a new Workspace or set and leaves the one it was called on unchanged. A
refused operation raises an exception and changes nothing. `layout/store.py`
owns the file that the set is saved to.
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
from anesthesia_sim.layout.run_identity import RunId
from anesthesia_sim.layout.tree import AreaId, ViewKind, is_tag

__all__ = [
    "MINE",
    "SHIPPED_PREFIX",
    "Origin",
    "PinnedRunAbsent",
    "ShippedWorkspaceId",
    "ViewState",
    "Workspace",
    "WorkspaceName",
    "WorkspaceSet",
]

# The two written forms of an origin, which `Origin.written` writes and
# `Origin.from_written` reads. The first marks the reader's own Workspace, and
# the second comes before a shipped Workspace's id.
MINE: Final = "mine"
SHIPPED_PREFIX: Final = "shipped:"

# The word added to a duplicate's name, after its source's name: "<name> (copy)".
# Where that name is taken, the next is "<name> (copy 2)", and so on.
_COPY_WORD: Final = "copy"


class WorkspaceName(str):
    """A Workspace's name as its tab shows it, which can be built only through its check.

    Raises:
        TypeError: the name is not a `str`.
        InvalidLayout: the name is empty, begins or ends with whitespace, or
            contains a character that does not print, such as a newline or a
            control character, which a tab could not show.
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

    The id is a tag, as `is_tag` in `layout/tree.py` defines one, of any
    length. The shipped ids are limited in length by the file names whose
    stems they are. A reader's file that names a longer id names nothing
    shipped. The interface reports such a Workspace as one of unknown origin,
    rather than treating the file as malformed.

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

    `written` writes an origin as `"mine"` or `"shipped:<id>"`, and
    `from_written` reads it back. This class is the only place that defines
    that grammar.

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
        """Return the origin of the reader's own Workspace: one they made, duplicated or saved."""

        return cls(None)

    @classmethod
    def shipped(cls, shipped_id: ShippedWorkspaceId) -> Origin:
        """Return the origin of a Workspace shipped under `shipped_id`, edited since or not."""

        return cls(shipped_id)

    @property
    def is_shipped(self) -> bool:
        return self.shipped_id is not None

    def written(self) -> str:
        """Return the origin as a file stores it: `"mine"`, or `"shipped:"` followed by the id."""

        if self.shipped_id is None:
            return MINE

        return f"{SHIPPED_PREFIX}{self.shipped_id}"

    @classmethod
    def from_written(cls, written: str) -> Origin:
        """Return the origin that `written` names, in the form that `written()` writes.

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
"""Each View's saved state, stored per Area id and per View kind.

Each state is a JSON object that the Workspace never reads.
"""


@dataclass(frozen=True, slots=True)
class PinnedRunAbsent:
    """A Workspace's pinned run is not open, so its Views show no run.

    `Workspace.shown_runs` returns a `PinnedRunAbsent` in place of the runs
    to show. The absence is then a value that a caller has to handle, rather
    than an empty tuple that it could pass on. A View bound to the pin says in
    its Area that the run is absent, and draws no value.

    Raises:
        TypeError: `pinned` is not a `RunId`.
    """

    pinned: RunId

    def __post_init__(self) -> None:
        if not isinstance(self.pinned, RunId):
            raise TypeError(f"a pinned run is a RunId, not {type(self.pinned).__name__}")


@dataclass(frozen=True, slots=True)
class Workspace:
    """A named layout with each View's own saved state, shown as one tab of the set.

    `view_state` is stored as the JSON it will be written as. It is a private
    copy, read-only at its two outer levels and at the top level of each
    state. `state_of` reads a state back and returns a copy of it. Every Area
    id in `view_state` names an Area that the layout contains. A View's state
    is a record of named fields, so each entry is a JSON object whose keys are
    strings at every depth. The View decides what the fields mean.

    `pinned_run` is the run that the Workspace's Views show. `None` means that
    they show the runs the session has open. `shown_runs` works out which runs
    to show.

    Raises:
        TypeError: a field is not of its declared type. Or a `view_state` key
            is not an `AreaId` or a `ViewKind`. Or a state is not a mapping.
            Or a state, or a mapping nested in it at any depth, has a key that
            is not a string. `json` would otherwise rewrite such keys as
            strings, and two keys could then become one.
        InvalidLayout: `view_state` names an Area that the layout does not
            contain. Or it contains a state that is not JSON: a value that
            `json` cannot write, or `NaN` or infinity, which the file rejects.
    """

    name: WorkspaceName
    origin: Origin
    layout: LayoutModel
    view_state: ViewState = field(default_factory=dict)
    pinned_run: RunId | None = None

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

        if self.pinned_run is not None and not isinstance(self.pinned_run, RunId):
            raise TypeError(
                f"a Workspace's pinned_run is a RunId or None, not {type(self.pinned_run).__name__}"
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
        """Return a copy of the state kept for the View of kind `view` in Area `area_id`.

        Return `None` when no state is kept for it. The caller may change the
        copy, and the Workspace keeps its own.
        """

        state = self.view_state.get(area_id, {}).get(view)

        return None if state is None else _json_round_trip(state)

    def with_view_state(
        self, area_id: AreaId, view: ViewKind, state: Mapping[str, object]
    ) -> Workspace:
        """Return this Workspace with `state` kept for the View of kind `view` in Area `area_id`.

        One entry is kept per kind per Area. So a state already kept for that
        kind is replaced, and the states kept for other kinds are left as they
        were.

        Raises:
            NotInLayout: `area_id` names no Area in the layout.
            TypeError, InvalidLayout: for the same reasons that the constructor
                raises them for a state.
        """

        self.layout.area(area_id)

        kinds = dict(self.view_state.get(area_id, {}))
        kinds[view] = state

        return replace(self, view_state={**self.view_state, area_id: kinds})

    def with_layout(self, layout: LayoutModel) -> Workspace:
        """Return this Workspace showing `layout`, keeping the state of each Area in `layout`.

        The state kept for an Area that is not in the new layout is dropped.
        That Area's id is never reused, so nothing could show the state again.

        Raises:
            TypeError: `layout` is not a `LayoutModel`.
        """

        if not isinstance(layout, LayoutModel):
            raise TypeError(f"a Workspace's layout is a LayoutModel, not {type(layout).__name__}")

        held = {area.id for area in layout.areas()}
        kept = {area_id: kinds for area_id, kinds in self.view_state.items() if area_id in held}

        return replace(self, layout=layout, view_state=kept)

    def pinned_to(self, run: RunId | None) -> Workspace:
        """Return this Workspace pinned to `run`, or unpinned when `run` is `None`.

        Raises:
            TypeError: `run` is neither `None` nor a `RunId`.
        """

        return replace(self, pinned_run=run)

    def shown_runs(self, open_runs: tuple[RunId, ...]) -> tuple[RunId, ...] | PinnedRunAbsent:
        """Return the runs that this Workspace's Views show, out of the runs the session has open.

        When the Workspace is unpinned, this returns every open run, in the
        order given. When it is pinned, this returns the pinned run alone if
        that run is open, and `PinnedRunAbsent` if it is not. No other run is
        ever returned in place of a pinned run.

        Raises:
            TypeError: `open_runs` is not a tuple of `RunId`s.
            ValueError: `open_runs` names one run twice.
        """

        if not isinstance(open_runs, tuple) or not all(isinstance(run, RunId) for run in open_runs):
            raise TypeError("the open runs are a tuple of RunIds")

        if len(set(open_runs)) != len(open_runs):
            raise ValueError("the open runs name each run once")

        if self.pinned_run is None:
            return open_runs

        if self.pinned_run in open_runs:
            return (self.pinned_run,)

        return PinnedRunAbsent(self.pinned_run)

    def renamed(self, name: WorkspaceName) -> Workspace:
        """Return this Workspace under `name`. The set checks whether the name is free.

        Raises:
            TypeError: `name` is not a `WorkspaceName`.
        """

        return replace(self, name=name)

    def as_mine(self) -> Workspace:
        """Return this Workspace as the reader's own, whatever its origin was."""

        return replace(self, origin=Origin.mine())


@dataclass(frozen=True, slots=True)
class WorkspaceSet:
    """The reader's Workspaces, in tab order, with the one they are working in.

    `active` is a position in `workspaces`. The set is never empty and no two
    Workspaces share a name. Every operation returns a new set. A refused
    operation raises an exception and leaves this set as it was.

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
        """Return the position of the Workspace named `name`.

        Raises:
            TypeError: `name` is not a `WorkspaceName`.
            NotInWorkspaceSet: no Workspace of that name is in the set.
        """

        if not isinstance(name, WorkspaceName):
            raise TypeError(f"a Workspace's name is a WorkspaceName, not {type(name).__name__}")

        for position, workspace in enumerate(self.workspaces):
            if workspace.name == name:
                return position

        raise NotInWorkspaceSet(f"no Workspace in the set is named {name!r}")

    def add(self, workspace: Workspace, at: int | None = None) -> WorkspaceSet:
        """Return the set with `workspace` inserted at `at`, and made active.

        By default, `at` is the end of the set.

        Raises:
            TypeError: `workspace` is not a `Workspace`, or `at` is not an `int`.
            NotInWorkspaceSet: `at` is neither a position in the set nor the
                position after its last.
            LayoutRefused: a Workspace of that name is already in the set.
        """

        if not isinstance(workspace, Workspace):
            raise TypeError(f"a set holds Workspaces, not {type(workspace).__name__}")

        position = len(self.workspaces) if at is None else self._position(at, inclusive=True)
        self._require_free(workspace.name)

        workspaces = (*self.workspaces[:position], workspace, *self.workspaces[position:])

        return WorkspaceSet(workspaces, position)

    def duplicate(self, index: int) -> WorkspaceSet:
        """Return the set with a copy of the Workspace at `index` inserted after it.

        The copy is the reader's own, and it becomes active. It is named after
        its source with " (copy)" added. Where that name is taken, it gets
        " (copy 2)", and so on. So the two tabs can be told apart.

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
        """Return the set with the Workspace at `index` renamed to `name`.

        Raises:
            TypeError: `index` is not an `int`, or `name` is not a `WorkspaceName`.
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
        """Return the set with the Workspace at `index` moved to `to`.

        The Workspace that was active stays active.

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
        """Return the set without the Workspace at `index`.

        If the removed Workspace was active, the Workspace that moves into its
        position becomes active. If the removed Workspace was also the last
        one, the new last Workspace becomes active instead.

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
        """Return the set with the Workspace at `index` made active.

        Raises:
            TypeError: `index` is not an `int`.
            NotInWorkspaceSet: `index` is not a position in the set.
        """

        return WorkspaceSet(self.workspaces, self._position(index))

    def replace(self, index: int, workspace: Workspace) -> WorkspaceSet:
        """Return the set with `workspace` in place of the one at `index`.

        A layout operation, a change to a View's saved state, and a reset from
        shipped JSON all reach the set this way. The caller rebuilds the
        Workspace and puts it back with this method.

        Raises:
            TypeError: `index` is not an `int`, or `workspace` is not a `Workspace`.
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
        """Return `index` as a position in the set, or one past its end when `inclusive`."""

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
    """Return `state` as the read-only JSON object it will be written as.

    Reject a `state` that is not a JSON object.
    """

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
    """Return a fresh copy of `state` as JSON reads it back: plain dicts and lists, sharing nothing.

    Raises:
        TypeError, ValueError: `json` cannot write `state`, because it contains
            a value of a type that `json` has no form for, or `NaN` or infinity.
    """

    loaded: dict[str, object] = json.loads(json.dumps(dict(state), allow_nan=False))

    return loaded


def _copy_name(name: WorkspaceName, taken: set[WorkspaceName]) -> WorkspaceName:
    """Return the first candidate name for a copy of `name` that is not in `taken`.

    The candidates, in order, are "<name> (copy)", "<name> (copy 2)", "<name> (copy 3)" ...
    """

    candidate = WorkspaceName(f"{name} ({_COPY_WORD})")
    count = 1

    while candidate in taken:
        count += 1
        candidate = WorkspaceName(f"{name} ({_COPY_WORD} {count})")

    return candidate
