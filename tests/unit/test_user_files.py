"""Unit tests for `user_files.py`: the steps that write a reader's file to disk.

The Workspaces store and the preferences store both write their file through
these steps, and their own tests check what each store does with them. The
tests here check the two promises that no store test can see. The file holds
UTF-8 whatever the platform's own text encoding is. The directory is flushed
where the platform lets a directory be opened, and the flush is skipped quietly
where it does not.

Each test stands in for the platform it needs, so every test runs the same on
Linux, macOS and Windows.
"""

import io
import os
from pathlib import Path

import pytest

from anesthesia_sim.user_files import sync_directory_quietly, write_synced

#: A value of the test's own for `os.O_DIRECTORY`, which Windows does not define.
#: The stand-in for `os.open` only records it, so any bit that `os.O_RDONLY`
#: does not set will do.
DIRECTORY_FLAG = 0x10000

#: A descriptor of the test's own, which the stand-in for `os.open` returns.
DESCRIPTOR = 7


def make_the_platform_encoding_ascii(monkeypatch: pytest.MonkeyPatch) -> None:
    """Make a path opened for text use ASCII where the caller names no encoding.

    `Path.open`, `Path.read_text` and `Path.write_text` ask `io.text_encoding`
    for the encoding to use when the caller names none. Python 3.15 starts in
    UTF-8 mode, where the answer is UTF-8, so a file opened with no named
    encoding would pass a test with no stand-in. A reader can turn that mode
    off with `PYTHONUTF8=0`. The answer is then the locale's encoding, which
    is ASCII on a platform whose locale is ASCII, and the stand-in returns
    ASCII in the same case. The built-in `open` does not ask
    `io.text_encoding`, so the stand-in does not reach a file opened that way.
    """

    def ascii_where_none_is_named(encoding: str | None, stacklevel: int = 2) -> str:
        return "ascii" if encoding is None else encoding

    monkeypatch.setattr(io, "text_encoding", ascii_where_none_is_named)


def test_a_written_file_holds_utf8_whatever_the_platform_encoding_is(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A file written where the platform's encoding is ASCII still holds its text as UTF-8.

    Both stores read their file back as UTF-8. A file written in the
    platform's own encoding would hold other bytes for a name such as
    "Réveil", or would fail to save at all where that encoding has no such
    letter. The expected bytes are the text's UTF-8 encoding, worked out here.
    `make_the_platform_encoding_ascii` says which ways of opening a file the
    stand-in reaches.
    """

    path = tmp_path / "workspaces.json"
    text = '{"name": "Réveil, 0,5 µg"}\n'
    make_the_platform_encoding_ascii(monkeypatch)

    write_synced(path, text)

    assert path.read_bytes() == text.encode("utf-8")


def test_the_directory_is_flushed_where_the_platform_can_open_one(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Where `os` has `O_DIRECTORY`, the directory itself is opened, `fsync`ed and closed.

    A replaced file is safe on the disk only once the directory entry that
    names it is, so a save that skipped this step could lose the new file to a
    power cut after it reported success. Nothing on the disk shows whether the
    flush ran, so the test records each call instead. Stand-ins replace
    `O_DIRECTORY` and the three calls, so the test also runs on Windows, whose
    `os` has no `O_DIRECTORY`.
    """

    calls: list[tuple[str, object]] = []

    def recording_open(path: Path, flags: int, mode: int = 0o777) -> int:
        calls.append(("open", (path, flags)))
        return DESCRIPTOR

    def recording_fsync(descriptor: int) -> None:
        calls.append(("fsync", descriptor))

    def recording_close(descriptor: int) -> None:
        calls.append(("close", descriptor))

    monkeypatch.setattr(os, "O_DIRECTORY", DIRECTORY_FLAG, raising=False)
    monkeypatch.setattr(os, "open", recording_open)
    monkeypatch.setattr(os, "fsync", recording_fsync)
    monkeypatch.setattr(os, "close", recording_close)

    sync_directory_quietly(tmp_path)

    assert calls == [
        ("open", (tmp_path, os.O_RDONLY | DIRECTORY_FLAG)),
        ("fsync", DESCRIPTOR),
        ("close", DESCRIPTOR),
    ]


def test_a_platform_that_cannot_open_a_directory_skips_the_flush_quietly(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Where `os` has no `O_DIRECTORY`, as on Windows, nothing is flushed and nothing is raised.

    By then the file is already on the disk and its directory already names
    it, so the save has not failed. The test removes `O_DIRECTORY` from `os`
    to stand for such a platform.
    """

    flushed: list[int] = []
    monkeypatch.delattr(os, "O_DIRECTORY", raising=False)
    monkeypatch.setattr(os, "fsync", flushed.append)

    sync_directory_quietly(tmp_path)

    assert flushed == []
