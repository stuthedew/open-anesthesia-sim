"""Exception hierarchy for what the layout package refuses.

Every failure the layout package detects is a subclass of `LayoutError`, so a
caller can catch a refused layout as one thing and tell it apart from a
programming error - a `TypeError` for an argument of the wrong type - passing
through the same call. `LayoutError` does not inherit from `ValueError`, for
the first of the two reasons `core/exceptions.py` gives for its own base: a
bare `ValueError` from somewhere else in a call would then read as a refusal
the layout made.

The branches mean different things to a caller, and the difference is what an
interface acts on:

- `LayoutRefused` - an operation this layout cannot perform: a join the tree
  cannot express, a border moved past its neighbour, a cut outside the Area
  being split. Nothing is wrong with the layout, which is a value and is
  unchanged; the reason is a sentence a menu can show beside the unavailable
  entry (`PL-M352`).
- `NotInLayout` - an Area id or a handle this layout does not hold: a stale
  reference, which is the caller's error rather than the layout's.
- `InvalidLayout` - a value that cannot be part of a layout, built in code: a
  view kind that is not a tag, an Area id below one, a split whose sizes do not
  sum to one.
- `LayoutFormatError` - a serialized layout that does not describe a valid
  one. `PL-SSQW` Q5 decided it: the message names the invariant that failed and
  where, and the reader's file is set aside rather than repaired.
- `UnsupportedSchemaVersion` - a serialized layout newer than this build
  reads. Not a `LayoutFormatError`, because `PL-SSQW` Q5 answers the two
  differently: an invalid file is set aside and the session saves on, a newer
  one is left untouched and the session saves nothing.
- `LastWorkspace` - a `LayoutRefused`: removing the Workspace would leave the
  set with none, which `ROADMAP.md` item 34's floor refuses by the type.
- `NotInWorkspaceSet` - a position the Workspace set does not hold: the
  caller's error, as `NotInLayout` is.
- `WorkspaceFileError` - the store could not write, copy or set aside a file.
  The message names the path and the operating system's reason, so the action
  that asked for the write can report both where it was invoked.
- `ShippedWorkspaceError` - a Workspace file shipped under `data/workspaces/`
  does not read as one. That is a defect of this build, never the reader's
  doing, so nothing sets the file aside or falls back from it.
"""

from __future__ import annotations

from pathlib import PurePath
from typing import TYPE_CHECKING

from anesthesia_sim.core.checked_number import shown

if TYPE_CHECKING:
    # `layout/migrations.py` imports this module, so the type is named for the
    # checker alone.
    from anesthesia_sim.layout.migrations import SchemaVersion

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
    caller's layout exactly as it was. Trying an operation is therefore also
    how a caller asks whether it is available: the message is the reason.
    """


class NotInLayout(LayoutError):
    """Raised when an Area id or a handle names nothing this layout holds."""


class InvalidLayout(LayoutError):
    """Raised when a value built in code cannot be part of a layout or of a Workspace set.

    Each message names the invariant the value broke: a split whose sizes do
    not sum to one, two Workspaces of one name, a migration table with a gap in
    it. Reading a serialized layout raises `LayoutFormatError` instead, with the
    place in the document where the invariant broke.
    """


class LayoutFormatError(LayoutError):
    """Raised when a serialized layout does not describe a valid layout.

    The message names the invariant that failed and the place in the document
    it failed at, so the file can be repaired by hand or reported. Nothing is
    substituted and nothing is dropped: a layout that does not read is refused
    whole (`PL-SSQW` Q5).
    """


class UnsupportedSchemaVersion(LayoutError):
    """Raised when a serialized layout was written by a newer build.

    `PL-SSQW` Q5 (project owner, 2026-09-27, ratified, over setting the file
    aside and starting fresh): a newer file is the reader's own work, so it is
    refused and left untouched, and the session it was opened in saves nothing.
    """

    def __init__(self, found: SchemaVersion, supported: SchemaVersion) -> None:
        super().__init__(
            f"this layout was written at schema version {shown(found)}, and this build reads "
            f"versions up to {supported}; a newer build wrote it, so it is left untouched"
        )
        self.found = found
        self.supported = supported


class LastWorkspace(LayoutRefused):
    """Raised when removing a Workspace would leave the set with none.

    `ROADMAP.md` item 34 adopts Blender's refusal to delete the last
    workspace as "a floor it enforces structurally rather than by warning",
    and `PL-WV9K` Q2 (project owner, 2026-09-27, ratified) puts it in the
    type: the set is a value and is unchanged. The interface also disables
    the action for a lone Workspace, so this is never the first thing a
    reader meets.
    """


class NotInWorkspaceSet(LayoutError):
    """Raised when a position names no Workspace this set holds."""


class WorkspaceFileError(LayoutError):
    """Raised when the store could not write, copy or set aside a file.

    `PL-SSQW` Q6: a failed save is reported where the reader asked for it,
    with the path and the operating system's reason, and the session
    continues. The error that was raised is kept as `error`.
    """

    def __init__(self, doing: str, path: PurePath, error: OSError) -> None:
        super().__init__(f"could not {doing} {path}: {error}")
        self.path = path
        self.error = error


class ShippedWorkspaceError(LayoutError):
    """Raised when a Workspace file shipped with the application does not read as one.

    The message names the file and what is wrong with it. The shipped set is
    what a first run shows and what every fallback in `layout/store.py` falls
    back to, so there is nothing further to fall back on: the build is broken,
    and saying so is the only safe answer.
    """
