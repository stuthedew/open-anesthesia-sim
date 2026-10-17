"""The file a reader's Workspaces are saved to, and what a launch does with what it finds.

Everything here was decided in `PL-SSQW` (project owner, 2026-09-27, ratified,
over the alternative each answer names), and this is the first state the
application writes outside its own tree.

**Where the file lives** (Q1). The store takes a directory and resolves none:
the application's entry point asks Qt for `QStandardPaths.AppDataLocation`
once it has set the organization and application names - macOS
`~/Library/Application Support/<App>`, Windows `%APPDATA%\\<Org>\\<App>`,
Linux `~/.local/share/<App>`, from Qt's own table in
`src/corelib/io/qstandardpaths.cpp` (qt/qtbase, read 2026-09-27) - and hands
the answer to `user_data_directory`, which applies the one override,
`USER_DIRECTORY_VARIABLE`, for a headless or portable run. A test passes
`tmp_path`. Roaming rather than Local on Windows because the file is
machine-independent by design: sizes are fractions and it holds no window
geometry (`PL-HJPY`). Blender's version-numbered configuration directory is
not adopted; its preferences are not forward compatible, and this file carries
a `schema_version` for exactly that job. Nothing in this package imports Qt,
which `tools/import_boundary_check.py` enforces.

**One file, `workspaces.json`, holding the whole set** (Q2), because the
set's invariants - never empty, one active, names unique - are the set's and a
directory of files cannot state them.

**Written only on the reader's word, and atomically** (Q3, Q4; `PL-WV9K` Q4,
project owner, 2026-09-27, specified: an explicit "Save as default", like
Blender's startup file, never an automatic save). `save` writes the document
to `workspaces.json.tmp` beside the file, flushes it and `fsync`s it, copies
the current file to `workspaces.json.previous` - through a temporary of its
own and a replace, so the previous generation is whole or the one before -
so one prior generation survives a bad write of the new one, then replaces
the target with `os.replace` - atomic on POSIX and, unlike `os.rename`,
allowed to replace an existing file on Windows (CPython `Doc/library/os.rst`,
read 2026-09-27) - and last `fsync`s the directory where the platform lets one
be opened, a best effort that cannot fail a save the file already holds. The
previous generation is a copy rather than Blender's rename, so there is no
instant at which the directory holds no current file. A torn current file
therefore arrives only through a crash mid-replace, which the operating system
guarantees leaves either file whole. Each step that fails names its own path
and what it was doing in `WorkspaceFileError`, and the temporary files are
removed. A first run leaves no trace: nothing is written until the first
"Save as default", when the directory is created.

**What a launch finds, and what it does** (Q5, Q6), all of it returned in
`Loaded` and none of it silent:

- *No file.* The shipped set, nothing said, saving on.
- *A file this build reads.* The set, as written; one written by an older
  build is migrated in memory by `layout/migrations.py`, the reader is told
  only where a step was lossy, and the pre-migration file is kept once as
  `workspaces.v<N>.json` at the next save.
- *A file a newer build wrote.* Refused, touched by nothing: the shipped set
  is shown, saving is off for the session, and the notice names the file, its
  version and this build's. The file is the reader's work, and a roll-back
  that overwrote it would be the deletion this policy exists to refuse. An
  alternative, setting it aside under a dated name and starting fresh, was
  refused because it moves the reader's file unasked for the benefit of a
  session that can equally run read-only.
- *A file that cannot be read* - permissions, an I/O error - is answered as a
  newer one is, since nothing can be known about it. A file that is not UTF-8
  text is invalid rather than unreadable: it was read, and it is not a document.
- *A file this build refuses as invalid* - truncated, not JSON, or breaking an
  invariant `layout/serialization.py` names - is set aside unchanged as
  `workspaces.invalid-<UTC time>.json`, the previous generation is loaded
  where it validates and the shipped set otherwise, the notice says which,
  and saving continues: the set-aside file is untouched evidence and the next
  save cannot damage it. Where it cannot be set aside, saving is off instead,
  since a save would overwrite it. A previous generation that itself refuses
  to read is left where it is and named in the notice, and one a newer build
  wrote turns saving off whatever the current file holds, as a newer current
  file does, since the second save would overwrite it.
- *No current file, but a previous generation that reads.* The previous
  generation, with a notice: a current file set aside at an earlier launch and
  not saved since would otherwise load the shipped set silently, with the
  reader's work beside it.
- *An unwritable directory* is met at `save`, which raises
  `WorkspaceFileError` naming the path and the reason, so the action that
  asked reports it where it was invoked; the session continues.

An unknown View kind in a file that reads is not a file error: the Workspace
loads and that Area shows `PL-R1WQ`'s failure state (`LayoutModel.unknown_kinds`).

The shipped set is `PL-KXTL`'s, read from `data/workspaces/` by the same
reader as a learner's file; the store is handed it and does not know where it
came from. Wiring the store into the application is the adapter's
(`PL-W9P6`): nothing under `app/` calls it yet.
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
from anesthesia_sim.layout.migrations import LAYOUT_SCHEMA_VERSION
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

# The file, the generation before it, and the file a save is written to
# before it replaces the current one, all in the store's directory.
WORKSPACES_FILE_NAME: Final = "workspaces.json"
PREVIOUS_FILE_NAME: Final = f"{WORKSPACES_FILE_NAME}.previous"
PENDING_FILE_NAME: Final = f"{WORKSPACES_FILE_NAME}.tmp"
_PREVIOUS_PENDING_FILE_NAME: Final = f"{PREVIOUS_FILE_NAME}.tmp"

# How the moment a file was set aside is written into its name: UTC, to the
# second, in the compact form of ISO 8601, which sorts as it reads.
_SET_ASIDE_TIME_FORMAT: Final = "%Y%m%dT%H%M%SZ"


def set_aside_file_name(when: datetime, attempt: int = 0) -> str:
    """The name an invalid file is set aside under at `when`, numbered where a second holds two."""

    stamp = when.astimezone(UTC).strftime(_SET_ASIDE_TIME_FORMAT)
    suffix = "" if attempt == 0 else f"-{attempt}"

    return f"workspaces.invalid-{stamp}{suffix}.json"


def kept_file_name(written_at: int) -> str:
    """The name the pre-migration file is kept under: the version it was written at."""

    return f"workspaces.v{written_at}.json"


def user_data_directory(
    standard_location: str | os.PathLike[str], environment: Mapping[str, str]
) -> Path:
    """The directory the reader's state is kept in.

    `USER_DIRECTORY_VARIABLE` where `environment` sets it to a non-empty
    value, and otherwise `standard_location`, the directory Qt reports for
    `QStandardPaths.AppDataLocation` once the entry point has set the
    organization and application names (`PL-SSQW` Q1).

    Raises:
        LayoutRefused: neither names a directory - the override is unset or
            empty and the platform reported no location, which Qt signals
            with an empty string - so the session has nowhere to save.
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
    """`workspaces.json`, as written, or migrated where an older build wrote it."""

    PREVIOUS = "previous"
    """`workspaces.json.previous`: the generation before, rescued."""

    SHIPPED = "shipped"
    """The shipped set: no file, or none that could be used."""


@dataclass(frozen=True, slots=True)
class Loaded:
    """What `WorkspaceStore.load` found and decided, for the interface to show and act on.

    `notice` is `None` where nothing happened that the reader should know,
    which is a first run and a file read as written; otherwise it is the
    sentence the interface shows, naming the file and what was done.
    `writable` is `False` where saving is off for the session, and `save`
    refuses while it is. `set_aside` is where an invalid file went.
    `written_at` is the version the loaded file was written at, or `None`
    where the shipped set is shown.
    """

    workspaces: WorkspaceSet
    source: Source
    writable: bool
    notice: str | None
    set_aside: Path | None
    written_at: int | None


class WorkspaceStore:
    """The reader's `workspaces.json` in one directory: `load` at launch, `save` on their word.

    A store `load`s before it `save`s, since whether saving is allowed is a
    fact about the file that was found.
    """

    def __init__(self, directory: Path, clock: Callable[[], datetime] | None = None) -> None:
        """A store over `directory`, which need not exist yet; `clock` names set-aside files.

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

    def load(self, shipped: WorkspaceSet) -> Loaded:
        """What this launch shows, by the policy above; `shipped` is shown where no file can be.

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
            LayoutRefused: nothing has been loaded, or the load found a file a
                newer build wrote or one that could not be read, so saving is
                off for the session; the message says which.
            WorkspaceFileError: the directory could not be created, or a file
                could not be written, copied or replaced; the message names
                the path the step was working on and the operating system's
                reason, and the current file is as it was.
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
        """No `workspaces.json`: a first run, unless a previous generation reads."""

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
        """An invalid current file: set it aside, then the previous generation or the shipped set.

        `reason` is the format error's message, carried into the notice.
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
        """The previous generation, as read; the refusal where a newer build wrote it; why it could
        not be used; or `None` where there is none."""

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
        """A path in the directory that nothing holds, named for this moment."""

        now = self._clock()
        attempt = 0

        while (candidate := self._directory / set_aside_file_name(now, attempt)).exists():
            attempt += 1

        return candidate

    def _pre_migration_keep(self) -> tuple[Path, Path] | None:
        """The file an older build wrote and where to keep it once, or `None` where none is owed."""

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
    """Run one step of a save, naming `path` and `doing` where the operating system refuses it.

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
    """Copy `source` over `target` by way of `pending`, so `target` is whole or the one before."""

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

    A best effort: the file is already on the disk and the directory already
    names it, and a filesystem that refuses to `fsync` a directory has not
    failed the save.
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
