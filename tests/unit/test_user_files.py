"""Unit tests for `user_files.py`: the steps that write a reader's file to disk.

The Workspaces store and the preferences store both write their file through
these steps, and their own tests check what each store does with them. The
tests here check the two promises that no store test can see. The file holds
UTF-8 whatever the platform's own text encoding is. The directory is flushed
where the platform lets a directory be opened, and the flush is skipped quietly
where it does not.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

from anesthesia_sim.user_files import sync_directory_quietly

#: The settings that make a child interpreter's default text encoding ASCII, as
#: it is on a platform whose locale is not UTF-8. `PYTHONUTF8=0` turns off the
#: UTF-8 mode that Python 3.15 starts in by default. `LC_ALL=C` selects the C
#: locale, and `PYTHONCOERCECLOCALE=0` stops Python from replacing that locale
#: with a UTF-8 one.
ASCII_PLATFORM = {"PYTHONUTF8": "0", "LC_ALL": "C", "PYTHONCOERCECLOCALE": "0"}


def run_where_the_platform_encoding_is_ascii(source: str, *arguments: str) -> list[str]:
    """Run `source` in a child interpreter set up as a platform whose locale is not UTF-8.

    The interpreter that runs the tests starts in UTF-8 mode, so a file it
    opens without naming an encoding is UTF-8 anyway. The child is given
    `ASCII_PLATFORM` instead. `source` must be ASCII, because that platform
    decodes the child's command line as ASCII too. The child's `sys.argv[1:]`
    is `arguments`.

    Returns the lines that `source` prints. The calling test is skipped where
    the platform gives the child a UTF-8 locale all the same, because it could
    then tell nothing. It fails, with the child's error output, where the
    child fails.
    """

    child = subprocess.run(
        [sys.executable, "-c", f"import locale\nprint(locale.getencoding())\n{source}", *arguments],
        env={**os.environ, **ASCII_PLATFORM},
        capture_output=True,
        text=True,
        check=False,
    )
    lines = child.stdout.splitlines()

    if lines and lines[0].lower().replace("-", "") == "utf8":
        pytest.skip("this platform gave the child interpreter a UTF-8 locale")

    assert child.returncode == 0, child.stderr

    return lines[1:]


def test_a_written_file_holds_utf8_whatever_the_platform_encoding_is(tmp_path: Path) -> None:
    """A file written where the platform's encoding is ASCII still holds its text as UTF-8.

    Both stores read their file back as UTF-8. A file written in the
    platform's own encoding would hold other bytes for a name such as
    "Réveil", or would fail to save at all where that encoding has no such
    letter. The expected bytes are the text's UTF-8 encoding, worked out here.
    """

    path = tmp_path / "workspaces.json"
    text = '{"name": "Réveil, 0,5 µg"}\n'

    run_where_the_platform_encoding_is_ascii(
        "import sys\n"
        "from pathlib import Path\n"
        "from anesthesia_sim.user_files import write_synced\n"
        f"write_synced(Path(sys.argv[1]), {ascii(text)})\n",
        str(path),
    )

    assert path.read_bytes() == text.encode("utf-8")


def test_the_directory_is_flushed_where_the_platform_can_open_one(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """On a platform with `O_DIRECTORY`, the directory itself is opened and `fsync`ed.

    A replaced file is safe on the disk only once the directory entry that
    names it is, so a save that skipped this step could lose the new file to a
    power cut after it reported success. Nothing on the disk shows whether the
    flush ran, so the test records each `fsync` and checks that the directory
    was the one flushed.
    """

    if getattr(os, "O_DIRECTORY", None) is None:
        pytest.skip("this platform cannot open a directory to flush it")

    flushed: list[tuple[int, int]] = []
    real_fsync = os.fsync

    def recording_fsync(descriptor: int) -> None:
        status = os.fstat(descriptor)
        flushed.append((status.st_dev, status.st_ino))
        real_fsync(descriptor)

    monkeypatch.setattr(os, "fsync", recording_fsync)
    directory = tmp_path.stat()

    sync_directory_quietly(tmp_path)

    assert flushed == [(directory.st_dev, directory.st_ino)]


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
