"""The file that a reader's Workspaces are saved to, and what a launch does with what it finds.

Everything here was decided in `PL-SSQW` (project owner, 2026-09-27, ratified,
over the alternative that each answer names). `workspaces.json` is the first
state that the application writes outside its own tree.

**Where the file lives** (Q1). The store takes a directory and does not
resolve one itself. The application's entry point asks Qt for
`QStandardPaths.AppDataLocation` once it has set the organization and
application names. Qt's own table in `src/corelib/io/qstandardpaths.cpp`
(qt/qtbase, read 2026-09-27) gives macOS `~/Library/Application Support/<App>`,
Windows `%APPDATA%\\<Org>\\<App>` and Linux `~/.local/share/<App>`. The entry
point hands that location to `user_data_directory`, which applies the one
override, `USER_DIRECTORY_VARIABLE`, for a headless or portable run. A test
passes `tmp_path`. On Windows the file goes in Roaming rather than Local,
because it is machine-independent by design: sizes are fractions, and it holds
no window geometry (`PL-HJPY`). Blender's version-numbered configuration
directory is not adopted. Blender's preferences are not forward compatible,
and this file carries a `schema_version` for exactly that job. Nothing in this
package imports Qt, which `tools/import_boundary_check.py` enforces.

**One file, `workspaces.json`, holds the whole set** (Q2). The set has
invariants of its own: it is never empty, exactly one Workspace is active,
and the names are unique. A directory of separate files could not state them.

**The file is written only when the reader asks, and atomically** (Q3, Q4;
`PL-WV9K` Q4, project owner, 2026-09-27, specified: an explicit "Save as
default", like Blender's startup file, never an automatic save). `save` takes
these steps in order:

1. It writes the document to `workspaces.json.tmp` beside the file, flushes it
   and `fsync`s it.
2. It copies the current file to `workspaces.json.previous`, so that one prior
   generation survives a bad write of the new one. The copy goes through a
   temporary file of its own and a replace, so the previous generation is
   either whole or still the one before.
3. It replaces the target with `os.replace`. That call is atomic on POSIX and,
   unlike `os.rename`, it is allowed to replace an existing file on Windows
   (CPython `Doc/library/os.rst`, read 2026-09-27).
4. Last, it `fsync`s the directory, where the platform lets a directory be
   opened. This is a best effort, and it cannot fail a save once the file is
   written.

The previous generation is a copy rather than Blender's rename, so there is no
moment at which the directory has no current file. A torn current file can
therefore arise only from a crash during the replace, and the operating system
guarantees that such a crash leaves one of the two files whole. Each step that
fails names its own path, and what it was doing, in `WorkspaceFileError`, and
the temporary files are removed. A first run leaves no trace. Nothing is
written until the first "Save as default", which creates the directory.

**What a launch finds, and what it does** (Q5, Q6). All of it is returned in
`Loaded`, and none of it is silent:

- *No file.* The shipped set is shown, with no notice, and saving is on.
- *A file this build reads.* The set is shown as written. A file written by an
  older build is migrated in memory by `layout/migrations.py`. The reader is
  told only when a step was lossy, and at the next save the pre-migration file
  is kept once as `workspaces.v<N>.json`.
- *A file a newer build wrote.* The file is refused, and nothing touches it.
  The shipped set is shown, saving is off for the session, and the notice
  names the file, its version and this build's version. The file is the
  reader's work, and a roll-back that overwrote it would be the deletion that
  this policy exists to prevent. One alternative was to set the file aside
  under a dated name and start fresh. It was refused because it moves the
  reader's file without asking, to benefit a session that can just as well run
  read-only.
- *A file that cannot be read*, because of a permissions error or an I/O
  error, is handled as a newer file is, since nothing can be known about it. A
  file that is not UTF-8 text is invalid rather than unreadable: it was read,
  and it is not a document.
- *A file this build rejects as invalid* is set aside unchanged as
  `workspaces.invalid-<UTC time>.json`. Such a file is truncated, is not JSON,
  or breaks an invariant that `layout/serialization.py` names. The previous
  generation is loaded if it is valid, and the shipped set otherwise, and the
  notice says which. Saving continues, because the set-aside file is untouched
  evidence that the next save cannot damage. If the file cannot be set aside,
  saving is off instead, since a save would overwrite it. A previous
  generation that itself cannot be read, or is invalid, is left where it is
  and named in the notice. A previous generation that a newer build wrote turns saving off,
  whatever the current file contains, just as a newer current file does,
  because the second save would overwrite it.
- *No current file, but a previous generation that this build reads.* The
  previous generation is shown, with a notice. Without this case, a launch
  after a current file was set aside, with nothing saved since, would load the
  shipped set silently, while the reader's work sat beside it.
- *An unwritable directory* is found at `save`, which raises
  `WorkspaceFileError` naming the path and the reason. The action that asked
  for the save then reports the error where it was invoked, and the session
  continues.

An unknown View kind in a file that this build reads is not a file error. The
Workspace loads, and that Area shows the failure state from `PL-R1WQ`
(`LayoutModel.unknown_kinds`).

The shipped set comes from `PL-KXTL`. `layout/shipped.py` reads it from
`data/workspaces/` with the same reader as a learner's file. The store is
handed the set and does not know where it came from. `app/main.py` resolves
the directory and loads the set at launch, and the Layout menu in
`app/workspace_tabs.py` saves it (`PL-DWHG`).
"""

from __future__ import annotations

import os
import shutil
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Final

from anesthesia_sim.layout.exceptions import (
    LayoutFormatError,
    LayoutRefused,
    UnsupportedSchemaVersion,
    WorkspaceFileError,
)
from anesthesia_sim.layout.migrations import LAYOUT_SCHEMA_VERSION, SchemaVersion
from anesthesia_sim.layout.serialization import (
    ReadWorkspaceSet,
    workspace_set_from_json,
    workspace_set_to_json,
)
from anesthesia_sim.layout.workspace import WorkspaceSet

__all__ = [
    "PENDING_FILE_NAME",
    "PREVIOUS_FILE_NAME",
    "USER_DIRECTORY_VARIABLE",
    "WORKSPACES_FILE_NAME",
    "Loaded",
    "Source",
    "WorkspaceStore",
    "kept_file_name",
    "set_aside_file_name",
    "user_data_directory",
]

# The environment variable that overrides the platform's user data directory,
# read by the entry point for a headless or portable run (`PL-SSQW` Q1).
USER_DIRECTORY_VARIABLE: Final = "ANESTHESIA_SIM_USER_DIR"

# The current file, the previous generation, and the file that a save writes
# before it replaces the current file, all in the store's directory.
WORKSPACES_FILE_NAME: Final = "workspaces.json"
PREVIOUS_FILE_NAME: Final = f"{WORKSPACES_FILE_NAME}.previous"
PENDING_FILE_NAME: Final = f"{WORKSPACES_FILE_NAME}.tmp"
_PREVIOUS_PENDING_FILE_NAME: Final = f"{PREVIOUS_FILE_NAME}.tmp"

# How the moment a file was set aside is written into its name: UTC, to the
# second, in the compact form of ISO 8601, so that the names sort in time order.
_SET_ASIDE_TIME_FORMAT: Final = "%Y%m%dT%H%M%SZ"


def set_aside_file_name(when: datetime, attempt: int = 0) -> str:
    """Return the name for an invalid file set aside at `when`, numbered if two fall in one second.

    `attempt` counts the names already taken in that second, starting from 0.
    An `attempt` of 0 adds no number to the name.

    Raises:
        TypeError: `attempt` is not an `int`, or is a `bool`, which would
            write `-True` into the name.
        ValueError: `attempt` is negative, which would write a second hyphen
            into the name.
    """

    if isinstance(attempt, bool) or not isinstance(attempt, int):
        raise TypeError(f"an attempt is an int, not {type(attempt).__name__}")

    if attempt < 0:
        raise ValueError(f"an attempt counts from 0, not {attempt}")

    stamp = when.astimezone(UTC).strftime(_SET_ASIDE_TIME_FORMAT)
    suffix = "" if attempt == 0 else f"-{attempt}"

    return f"workspaces.invalid-{stamp}{suffix}.json"


def kept_file_name(written_at: SchemaVersion) -> str:
    """Return the name for the pre-migration file, which records the version it was written at.

    Raises:
        TypeError: `written_at` is not an `int`, or is a `bool`, which would
            name the file `workspaces.vTrue.json`.
        InvalidLayout: `written_at` is less than 1, a version no build wrote.
    """

    # The name is built through the type even from a `SchemaVersion`, so that a
    # caller the type checker does not cover cannot name a version that does
    # not exist.
    return f"workspaces.v{SchemaVersion(written_at)}.json"


def user_data_directory(
    standard_location: str | os.PathLike[str], environment: Mapping[str, str]
) -> Path:
    """Return the directory that the reader's state is kept in.

    The result is the value of `USER_DIRECTORY_VARIABLE` when `environment`
    sets it to a non-empty value. Otherwise it is `standard_location`, the directory that Qt
    reports for `QStandardPaths.AppDataLocation` once the entry point has set
    the organization and application names (`PL-SSQW` Q1).

    Raises:
        LayoutRefused: neither names a directory, so the session has nowhere
            to save. That happens when the override is unset or empty and the
            platform reported no location, which Qt signals with an empty
            string.
    """

    override = environment.get(USER_DIRECTORY_VARIABLE, "")

    if override:
        return Path(override)

    if not os.fspath(standard_location):
        raise LayoutRefused(
            "there is no directory to keep the reader's Workspaces in: the platform reported no "
            f"application data location and {USER_DIRECTORY_VARIABLE} is unset or empty"
        )

    return Path(standard_location)


class Source(Enum):
    """Which set a launch is showing."""

    FILE = "file"
    """`workspaces.json`, as written, or migrated if an older build wrote it."""

    PREVIOUS = "previous"
    """`workspaces.json.previous`, the previous generation, recovered in place of the file."""

    SHIPPED = "shipped"
    """The shipped set: no file, or none that could be used."""


@dataclass(frozen=True, slots=True)
class Loaded:
    """What `WorkspaceStore.load` found and decided, for the interface to show and act on.

    `notice` is `None` when nothing happened that the reader needs to know
    about, which is the case on a first run and for a file read as written.
    Otherwise it is the sentence that the interface shows, naming the file and
    what was done. `writable` is `False` when saving is off for the session,
    and `save` refuses while it is. `set_aside` is the path that an invalid
    file was moved to. `written_at` is the version that the loaded file was
    written at, or `None` when the shipped set is shown.
    """

    workspaces: WorkspaceSet
    source: Source
    writable: bool
    notice: str | None
    set_aside: Path | None
    written_at: SchemaVersion | None


class WorkspaceStore:
    """The reader's `workspaces.json` in one directory: `load` at launch, `save` when asked.

    A store `load`s before it `save`s, since whether saving is allowed is a
    fact about the file that was found.
    """

    def __init__(self, directory: Path, clock: Callable[[], datetime] | None = None) -> None:
        """Create a store for `directory`, which need not exist yet.

        `clock` gives the time that set-aside files are named for.

        Raises:
            TypeError: `directory` is not a `Path`.
        """

        if not isinstance(directory, Path):
            raise TypeError(f"a store's directory is a Path, not {type(directory).__name__}")

        self._directory = directory
        self._clock = _utc_now if clock is None else clock
        self._loaded: Loaded | None = None

    @property
    def directory(self) -> Path:
        """The directory the file is kept in, for the interface to name beside a notice."""

        return self._directory

    @property
    def path(self) -> Path:
        """Where `workspaces.json` is, or will be."""

        return self._directory / WORKSPACES_FILE_NAME

    @property
    def loaded(self) -> Loaded | None:
        """The `Loaded` result of the last `load` or `save`, or `None` before the first `load`.

        The interface reads its `writable` and `notice` fields. They decide
        whether "Save as default" is offered, and give the reason when it is not.
        """

        return self._loaded

    def load(self, shipped: WorkspaceSet) -> Loaded:
        """Decide and return what this launch shows, by the policy in the module docstring.

        `shipped` is the set that is shown when no file can be used.

        Raises:
            TypeError: `shipped` is not a `WorkspaceSet`.
        """

        if not isinstance(shipped, WorkspaceSet):
            raise TypeError(f"the shipped set is a WorkspaceSet, not {type(shipped).__name__}")

        loaded = self._load(shipped)
        self._loaded = loaded

        return loaded

    def save(self, workspaces: WorkspaceSet) -> Path:
        """Write `workspaces` as the reader's default, atomically, and return the file's path.

        Raises:
            TypeError: `workspaces` is not a `WorkspaceSet`.
            LayoutRefused: nothing has been loaded, or the load found a file
                that a newer build wrote or that could not be read, so saving
                is off for the session. The message says which.
            WorkspaceFileError: the directory could not be created, or a file
                could not be written, copied or replaced. The message names
                the path that the step was working on and the operating
                system's reason, and the current file is left as it was.
        """

        if not isinstance(workspaces, WorkspaceSet):
            raise TypeError(f"a set is saved from a WorkspaceSet, not {type(workspaces).__name__}")

        if self._loaded is None:
            raise LayoutRefused(
                f"nothing has been loaded from {self._directory}, so whether saving there is safe "
                "is not known; load first"
            )

        if not self._loaded.writable:
            raise LayoutRefused(f"saving is off for this session: {self._loaded.notice}")

        text = workspace_set_to_json(workspaces)
        pending = self._directory / PENDING_FILE_NAME
        previous = self._directory / PREVIOUS_FILE_NAME
        previous_pending = self._directory / _PREVIOUS_PENDING_FILE_NAME
        kept = self._pre_migration_keep()

        try:
            _attempt(
                "create the directory",
                self._directory,
                lambda: self._directory.mkdir(parents=True, exist_ok=True),
            )

            if kept is not None:
                source, target = kept
                _attempt(
                    "keep the pre-migration file as",
                    target,
                    lambda: shutil.copyfile(source, target),
                )

            _attempt("write", pending, lambda: _write_synced(pending, text))

            if self.path.exists():
                _attempt(
                    "copy the previous generation to",
                    previous,
                    lambda: _copy_replacing(self.path, previous_pending, previous),
                )

            _attempt("replace", self.path, lambda: os.replace(pending, self.path))
        except WorkspaceFileError:
            _remove_quietly(pending)
            _remove_quietly(previous_pending)
            raise

        self._loaded = Loaded(
            workspaces, Source.FILE, True, None, self._loaded.set_aside, LAYOUT_SCHEMA_VERSION
        )
        _sync_directory_quietly(self._directory)

        return self.path

    def _load(self, shipped: WorkspaceSet) -> Loaded:
        try:
            text = self.path.read_text(encoding="utf-8")
        except FileNotFoundError, NotADirectoryError:
            return self._without_current_file(shipped)
        except UnicodeDecodeError as error:
            return self._set_aside(shipped, f"the file is not UTF-8 text: {error}")
        except OSError as error:
            return Loaded(
                shipped,
                Source.SHIPPED,
                False,
                f"{self.path} could not be read ({error}), so the shipped Workspaces are shown "
                "and nothing will be saved this session; the file is left as it is",
                None,
                None,
            )

        try:
            read = workspace_set_from_json(text)
        except UnsupportedSchemaVersion as error:
            return Loaded(
                shipped,
                Source.SHIPPED,
                False,
                f"{self.path} was written at schema version {error.found} by a newer build, and "
                f"this build reads versions up to {error.supported}, so the shipped Workspaces "
                "are shown and nothing will be saved this session; the file is left untouched",
                None,
                None,
            )
        except LayoutFormatError as error:
            return self._set_aside(shipped, str(error))

        previous = self._read_previous()

        if isinstance(previous, UnsupportedSchemaVersion):
            return Loaded(
                read.workspaces,
                Source.FILE,
                False,
                f"{self._directory / PREVIOUS_FILE_NAME} was written at schema version "
                f"{previous.found} by a newer build, which the second save from this build would "
                "overwrite, so nothing will be saved this session; the saved Workspaces are shown"
                + _lossy_suffix(read),
                None,
                read.written_at,
            )

        return Loaded(
            read.workspaces, Source.FILE, True, _lossy_notice(read), None, read.written_at
        )

    def _without_current_file(self, shipped: WorkspaceSet) -> Loaded:
        """Handle a missing `workspaces.json`: a first run, unless a previous generation exists."""

        previous = self._directory / PREVIOUS_FILE_NAME
        rescued = self._read_previous()

        if rescued is None:
            return Loaded(shipped, Source.SHIPPED, True, None, None, None)

        if isinstance(rescued, str):
            return Loaded(
                shipped,
                Source.SHIPPED,
                True,
                f"there is no {self.path}, and {previous} could not be used ({rescued}) and is "
                "left where it is, so the shipped Workspaces are shown",
                None,
                None,
            )

        if isinstance(rescued, UnsupportedSchemaVersion):
            return Loaded(
                shipped,
                Source.SHIPPED,
                False,
                f"there is no {self.path}, and {previous} was written at schema version "
                f"{rescued.found} by a newer build, which this build would overwrite at the next "
                "save; the shipped Workspaces are shown and nothing will be saved this session",
                None,
                None,
            )

        return Loaded(
            rescued.workspaces,
            Source.PREVIOUS,
            True,
            f"there is no {self.path}, so the previous default, {previous}, is shown; "
            '"Save as default" keeps it' + _lossy_suffix(rescued),
            None,
            rescued.written_at,
        )

    def _set_aside(self, shipped: WorkspaceSet, reason: str) -> Loaded:
        """Set an invalid current file aside, then load the previous generation or the shipped set.

        `reason` is the format error's message, which is carried into the notice.
        """

        try:
            set_aside = self._set_aside_path()
            os.rename(self.path, set_aside)
        except OSError as error:
            return Loaded(
                shipped,
                Source.SHIPPED,
                False,
                f"{self.path} is not a Workspace file this build reads ({reason}), and could not "
                f"be set aside ({error}), so the shipped Workspaces are shown and nothing will "
                "be saved this session; the file is left as it is",
                None,
                None,
            )

        previous = self._directory / PREVIOUS_FILE_NAME
        rescued = self._read_previous()
        opening = (
            f"{self.path} is not a Workspace file this build reads ({reason}); it was set aside "
            f"unchanged as {set_aside}"
        )

        if rescued is None:
            return Loaded(
                shipped,
                Source.SHIPPED,
                True,
                f"{opening}, and the shipped Workspaces are shown",
                set_aside,
                None,
            )

        if isinstance(rescued, str):
            return Loaded(
                shipped,
                Source.SHIPPED,
                True,
                f"{opening}; {previous} could not be used ({rescued}) and is left where it is, "
                "so the shipped Workspaces are shown",
                set_aside,
                None,
            )

        if isinstance(rescued, UnsupportedSchemaVersion):
            return Loaded(
                shipped,
                Source.SHIPPED,
                False,
                f"{opening}; {previous} was written at schema version {rescued.found} by a newer "
                "build, so the shipped Workspaces are shown and nothing will be saved this "
                "session",
                set_aside,
                None,
            )

        return Loaded(
            rescued.workspaces,
            Source.PREVIOUS,
            True,
            f"{opening}, and the previous default, {previous}, is shown" + _lossy_suffix(rescued),
            set_aside,
            rescued.written_at,
        )

    def _read_previous(self) -> ReadWorkspaceSet | UnsupportedSchemaVersion | str | None:
        """Read the previous generation, and return it or the reason it cannot be used.

        The result is the previous generation as read, or the refusal when a
        newer build wrote it, or a string saying why it could not be used, or
        `None` when there is no previous generation.
        """

        try:
            text = (self._directory / PREVIOUS_FILE_NAME).read_text(encoding="utf-8")
        except FileNotFoundError, NotADirectoryError:
            return None
        except UnicodeDecodeError as error:
            return f"it is not UTF-8 text: {error}"
        except OSError as error:
            return f"it could not be read: {error}"

        try:
            return workspace_set_from_json(text)
        except UnsupportedSchemaVersion as error:
            return error
        except LayoutFormatError as error:
            return str(error)

    def _set_aside_path(self) -> Path:
        """Return a path in the directory where no file exists yet, named for this moment."""

        now = self._clock()
        attempt = 0

        while (candidate := self._directory / set_aside_file_name(now, attempt)).exists():
            attempt += 1

        return candidate

    def _pre_migration_keep(self) -> tuple[Path, Path] | None:
        """Return the file an older build wrote and where to keep it, or `None` if no copy is due.

        The pre-migration file is kept only once.
        """

        if self._loaded is None or self._loaded.written_at is None:
            return None

        if self._loaded.written_at >= LAYOUT_SCHEMA_VERSION:
            return None

        kept = self._directory / kept_file_name(self._loaded.written_at)
        source = (
            self.path
            if self._loaded.source is Source.FILE
            else self._directory / PREVIOUS_FILE_NAME
        )

        if kept.exists() or not source.exists():
            return None

        return source, kept


def _attempt(doing: str, path: Path, action: Callable[[], object]) -> None:
    """Run one step of a save, naming `path` and `doing` if the operating system refuses it.

    Raises:
        WorkspaceFileError: `action` raised an `OSError`.
    """

    try:
        action()
    except OSError as error:
        raise WorkspaceFileError(doing, path, error) from None


def _write_synced(path: Path, text: str) -> None:
    """Write `text` to `path` and `fsync` it, so it is on the disk before anything points at it."""

    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())


def _copy_replacing(source: Path, pending: Path, target: Path) -> None:
    """Copy `source` over `target` via `pending`, so `target` is whole or still the one before."""

    shutil.copyfile(source, pending)
    os.replace(pending, target)


def _lossy_notice(read: ReadWorkspaceSet) -> str | None:
    if not read.lossy:
        return None

    return (
        f"the saved Workspaces were written at schema version {read.written_at} and were brought "
        f"to version {LAYOUT_SCHEMA_VERSION}: " + " ".join(read.lossy)
    )


def _lossy_suffix(read: ReadWorkspaceSet) -> str:
    notice = _lossy_notice(read)

    return "" if notice is None else f"; {notice}"


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _sync_directory_quietly(directory: Path) -> None:
    """Flush the directory's own entries where the platform lets a directory be opened.

    This is a best effort. The file is already on the disk and the directory
    already names it, so a filesystem that refuses to `fsync` a directory has
    not failed the save.
    """

    flag = getattr(os, "O_DIRECTORY", None)

    if flag is None:
        return

    try:
        descriptor = os.open(directory, os.O_RDONLY | flag)
    except OSError:
        return

    try:
        os.fsync(descriptor)
    except OSError:
        return
    finally:
        os.close(descriptor)


def _remove_quietly(path: Path) -> None:
    try:
        path.unlink()
    except OSError:
        return
