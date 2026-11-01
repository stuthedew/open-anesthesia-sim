"""The steps that write a reader's file to disk atomically, shared by every store that keeps one.

Two stores keep a file in the reader's data directory: the Workspaces
(`layout/store.py`) and the preferences (`app/preferences.py`). Both write a
file the same way. They write the whole text to a temporary file beside the
target and `fsync` it, replace the target with `os.replace`, and then make a
best effort to `fsync` the directory. `layout/store.py` gives the reasons for
each step (`PL-SSQW`). The steps live here once, so the two stores cannot come
to write a file in two different ways (`PL-93B3`).

Nothing here imports Qt or chooses a directory. Each store takes its directory
from its caller.
"""

from __future__ import annotations

import os
from pathlib import Path

__all__ = ["remove_quietly", "sync_directory_quietly", "write_synced"]


def write_synced(path: Path, text: str) -> None:
    """Write `text` to `path` and `fsync` it, so it is on the disk before anything points at it."""

    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())


def sync_directory_quietly(directory: Path) -> None:
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


def remove_quietly(path: Path) -> None:
    """Remove `path` if it can be removed, and do nothing if it cannot.

    A store calls this to clear a temporary file after a failed save. The save
    has already failed and says why, so a second error here would only hide
    the first.
    """

    try:
        path.unlink()
    except OSError:
        return
