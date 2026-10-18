"""The Workspaces shipped with the application, read from `data/workspaces/`.

`PL-KXTL` ships three Workspaces as validated, versioned JSON beside the other
shipped data files. Each is a Workspace set document holding one Workspace,
the form a reader's own file takes, so each is read by
`workspace_set_from_json`, the reader `layout/store.py` uses. A shipped file
therefore cannot hold anything a reader's file could not.

**One file per Workspace, named by its id.** "Reset this Workspace" replaces
one Workspace from its own shipped file (`PL-WV9K` Q3), so `shipped_workspace`
reads one file, and `shipped_workspaces` reads them all in tab order, the
first active. The file's stem is the Workspace's `ShippedWorkspaceId`, and the
origin written inside the file must name the same id.

**Shipped files are held to the current version.** A shipped file travels
with the build that reads it, so it is never migrated: one written at any
other `schema_version` is refused. That is `core/parameters.py`'s rule for
the files that ship with the code, which `PL-SSQW` kept for shipped files
while deciding a different one for the reader's.

**Every refusal is `ShippedWorkspaceError`, naming the file.** A shipped file
that does not read is a defect of the build, never the reader's doing, so
nothing here sets it aside or falls back from it. A JSON file in the
directory that `SHIPPED_WORKSPACE_IDS` does not list is refused too, since it
would otherwise never be read.

Whether each View kind the files name is registered is the View registry's
question (`PL-R1WQ` Q4), and is checked once the registry exists.
"""

from __future__ import annotations

from importlib.resources import files
from importlib.resources.abc import Traversable
from typing import Final

from anesthesia_sim.layout.exceptions import (
    InvalidLayout,
    LayoutFormatError,
    ShippedWorkspaceError,
    UnsupportedSchemaVersion,
)
from anesthesia_sim.layout.migrations import LAYOUT_SCHEMA_VERSION
from anesthesia_sim.layout.serialization import workspace_set_from_json
from anesthesia_sim.layout.workspace import Origin, ShippedWorkspaceId, Workspace, WorkspaceSet

__all__ = [
    "SHIPPED_WORKSPACES_PACKAGE",
    "SHIPPED_WORKSPACE_IDS",
    "shipped_workspace",
    "shipped_workspaces",
]

# The package the shipped files are read from.
SHIPPED_WORKSPACES_PACKAGE: Final = "anesthesia_sim.data.workspaces"

# The shipped Workspaces in the order their tabs stand. The first is active
# on a first run.
SHIPPED_WORKSPACE_IDS: Final = (
    ShippedWorkspaceId("default"),
    ShippedWorkspaceId("induction"),
    ShippedWorkspaceId("maintenance"),
)

_SUFFIX: Final = ".json"


def shipped_workspace(
    shipped_id: ShippedWorkspaceId, source: Traversable | None = None
) -> Workspace:
    """The shipped Workspace named `shipped_id`, as its file holds it.

    `source` is the directory to read from. It defaults to the shipped
    package, and a test passes a directory of its own.

    Raises:
        TypeError: `shipped_id` is not a `ShippedWorkspaceId`.
        ShippedWorkspaceError: no shipped Workspace has that id, or its file
            cannot be read, is not a Workspace set document of the current
            version, holds other than one Workspace, or holds one whose origin
            does not name the file's id. The message names the file.
    """

    if not isinstance(shipped_id, ShippedWorkspaceId):
        raise TypeError(
            f"a shipped Workspace's id is a ShippedWorkspaceId, not {type(shipped_id).__name__}"
        )

    if shipped_id not in SHIPPED_WORKSPACE_IDS:
        raise ShippedWorkspaceError(
            f"no Workspace is shipped as {shipped_id!r}; the shipped ones are "
            + ", ".join(repr(str(known)) for known in SHIPPED_WORKSPACE_IDS)
        )

    return _read(_directory(source), shipped_id)


def shipped_workspaces(source: Traversable | None = None) -> WorkspaceSet:
    """Every shipped Workspace, in `SHIPPED_WORKSPACE_IDS` order, with the first active.

    `source` is the directory to read from, as `shipped_workspace` takes it.

    Raises:
        ShippedWorkspaceError: a file `shipped_workspace` would refuse; a JSON
            file in the directory that no id names; or two shipped
            Workspaces sharing a name, which a set refuses.
    """

    directory = _directory(source)
    listed = {f"{shipped_id}{_SUFFIX}" for shipped_id in SHIPPED_WORKSPACE_IDS}
    unlisted = sorted(
        entry.name
        for entry in directory.iterdir()
        if entry.name.endswith(_SUFFIX) and entry.name not in listed
    )

    if unlisted:
        raise ShippedWorkspaceError(
            f"{', '.join(unlisted)} in {SHIPPED_WORKSPACES_PACKAGE} is named by no shipped "
            "Workspace id, so it would never be read; list its stem in SHIPPED_WORKSPACE_IDS "
            "or remove it"
        )

    workspaces = tuple(_read(directory, shipped_id) for shipped_id in SHIPPED_WORKSPACE_IDS)

    try:
        return WorkspaceSet(workspaces, 0)
    except InvalidLayout as error:
        raise ShippedWorkspaceError(f"the shipped Workspaces do not form a set: {error}") from None


def _directory(source: Traversable | None) -> Traversable:
    return files(SHIPPED_WORKSPACES_PACKAGE) if source is None else source


def _read(directory: Traversable, shipped_id: ShippedWorkspaceId) -> Workspace:
    """The one Workspace in `directory`'s file for `shipped_id`, checked against the id."""

    name = f"{shipped_id}{_SUFFIX}"
    where = f"{SHIPPED_WORKSPACES_PACKAGE}/{name}"

    try:
        text = directory.joinpath(name).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise ShippedWorkspaceError(f"{where} could not be read: {error}") from None

    try:
        read = workspace_set_from_json(text)
    except (LayoutFormatError, UnsupportedSchemaVersion) as error:
        raise ShippedWorkspaceError(f"{where} is not a Workspace set document: {error}") from None

    if read.written_at != LAYOUT_SCHEMA_VERSION:
        raise ShippedWorkspaceError(
            f"{where} is written at schema version {read.written_at}, and a shipped file is "
            f"written at this build's version, {LAYOUT_SCHEMA_VERSION}, since it is never migrated"
        )

    held = read.workspaces.workspaces

    if len(held) != 1:
        raise ShippedWorkspaceError(f"{where} holds one Workspace, not {len(held)}")

    workspace = held[0]
    expected = Origin.shipped(shipped_id)

    if workspace.origin != expected:
        raise ShippedWorkspaceError(
            f"{where} holds a Workspace whose origin is {workspace.origin.written()!r}, and a "
            f"shipped file's Workspace names its own file's id, {expected.written()!r}"
        )

    return workspace
