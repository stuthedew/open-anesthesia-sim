"""Exception hierarchy for the cases that the layout package rejects.

Every exception that the layout package raises for a failure it detects is a
subclass of `LayoutError`. A caller can therefore catch every rejection as one
exception type. The caller can also tell a rejection apart from a programming
error that passes through the same call, such as a `TypeError` for an argument
of the wrong type. `LayoutError` does not inherit from
`ValueError`, for the first of the two reasons that `core/exceptions.py` gives
for its own base class. If it did, a bare `ValueError` raised somewhere else in
a call would look like a rejection made by the layout.

Each subclass means something different to a caller, and an interface acts on
that difference:

- `LayoutRefused` - the layout cannot perform an operation. Examples are a join
  that the tree cannot express, a border moved past its neighbour, and a cut
  outside the Area being split. Nothing is wrong with the layout. The layout is
  a value and stays unchanged. The message gives the reason as a sentence that
  a menu can show beside the unavailable entry (`PL-M352`).
- `NotInLayout` - an Area id or a handle that this layout does not contain.
  This is a stale reference, so the error is the caller's rather than the
  layout's.
- `InvalidLayout` - a value, built in code, that cannot be part of a layout.
  Examples are a view kind that is not a tag, an Area id less than one, and a
  split whose sizes do not sum to one.
- `LayoutFormatError` - a serialized layout that does not describe a valid
  layout. `PL-SSQW` Q5 decided how this case is handled. The message names the
  invariant that failed and where it failed, and the reader's file is set aside
  rather than repaired.
- `UnsupportedSchemaVersion` - a serialized layout written in a schema version
  newer than this build can read. It is not a `LayoutFormatError`, because
  `PL-SSQW` Q5 handles the two cases differently. An invalid file is set aside
  and the session goes on saving. A newer file is left untouched and the
  session saves nothing.
- `LastWorkspace` - a `LayoutRefused` for removing a Workspace when that would
  leave the set with none. `ROADMAP.md` item 34 requires the type itself to
  reject that removal.
- `NotInWorkspaceSet` - a position that the Workspace set does not contain.
  Like `NotInLayout`, this is the caller's error.
- `WorkspaceFileError` - the store could not write, copy or set aside a file.
  The message names the path and the operating system's reason. The action that
  asked for the write can then report both at the place where it was invoked.
- `ShippedWorkspaceError` - a Workspace file shipped under `data/workspaces/`
  is not a valid Workspace. That is a defect of this build and never the
  reader's doing, so nothing sets the file aside or falls back from it.
"""

from __future__ import annotations

from pathlib import PurePath

from anesthesia_sim.core.checked_number import shown

__all__ = [
    "InvalidLayout",
    "LastWorkspace",
    "LayoutError",
    "LayoutFormatError",
    "LayoutRefused",
    "NotInLayout",
    "NotInWorkspaceSet",
    "ShippedWorkspaceError",
    "UnsupportedSchemaVersion",
    "WorkspaceFileError",
]


class LayoutError(Exception):
    """Base exception for everything the layout package refuses."""


class LayoutRefused(LayoutError):
    """Raised when an operation cannot be performed on this layout.

    The layout is an immutable value, so a refused operation leaves the
    caller's layout exactly as it was. A caller can therefore find out whether
    an operation is available by trying it. When the operation is not
    available, the message gives the reason.
    """


class NotInLayout(LayoutError):
    """Raised when an Area id or a handle names nothing that this layout contains."""


class InvalidLayout(LayoutError):
    """Raised when a value built in code cannot be part of a layout or of a Workspace set.

    Each message names the invariant that the value broke. Examples are a split
    whose sizes do not sum to one, two Workspaces with the same name, and a
    migration table with a gap in it. When a serialized layout breaks an
    invariant, reading it raises `LayoutFormatError` instead, and that message
    also gives the place in the document where the invariant broke.
    """


class LayoutFormatError(LayoutError):
    """Raised when a serialized layout does not describe a valid layout.

    The message names the invariant that failed and the place in the document
    where it failed, so the file can be repaired by hand or reported. Nothing is
    substituted and nothing is dropped. A layout that cannot be read is rejected
    as a whole (`PL-SSQW` Q5).
    """


class UnsupportedSchemaVersion(LayoutError):
    """Raised when a serialized layout was written by a newer build.

    A newer file is the reader's own work, so it is rejected and left
    untouched, and the session that opened it saves nothing. `PL-SSQW` Q5
    decided this (project owner, 2026-09-27, ratified, over setting the file
    aside and starting fresh).
    """

    # `found` and `supported` are `SchemaVersion` values, built by the code that reads
    # the file. They are typed here as `int`, the type that `SchemaVersion` subclasses.
    # `layout/migrations.py` defines `SchemaVersion` and imports this module, so naming
    # `SchemaVersion` here would make the two modules import each other (`PL-8JV2`).
    def __init__(self, found: int, supported: int) -> None:
        super().__init__(
            f"this layout was written at schema version {shown(found)}, and this build reads "
            f"versions up to {supported}; a newer build wrote it, so it is left untouched"
        )
        self.found = found
        self.supported = supported


class LastWorkspace(LayoutRefused):
    """Raised when removing a Workspace would leave the set with none.

    `ROADMAP.md` item 34 adopts Blender's refusal to delete the last
    workspace as "a floor it enforces structurally rather than by warning".
    `PL-WV9K` Q2 (project owner, 2026-09-27, ratified) puts that rule in the
    type. The set is a value, so a rejected removal leaves it unchanged. The
    interface also disables the remove action when only one Workspace is
    left, so this error is never the first sign a reader gets that the last
    Workspace cannot be removed.
    """


class NotInWorkspaceSet(LayoutError):
    """Raised when a position names no Workspace that this set contains."""


class WorkspaceFileError(LayoutError):
    """Raised when the store could not write, copy or set aside a file.

    `PL-SSQW` Q6 decided that a failed save is reported at the place where
    the reader asked for the save. The report gives the path and the
    operating system's reason, and the session continues. The original
    operating-system error is kept as `error`.
    """

    def __init__(self, doing: str, path: PurePath, error: OSError) -> None:
        super().__init__(f"could not {doing} {path}: {error}")
        self.path = path
        self.error = error


class ShippedWorkspaceError(LayoutError):
    """Raised when a Workspace file shipped with the application is not a valid Workspace.

    The message names the file and what is wrong with it. A first run shows the
    shipped set, and every fallback in `layout/store.py` falls back to it. There
    is nothing further to fall back on, so the build is broken, and reporting
    that is the only safe response.
    """
