"""Tests for `tools/readme_hold_check.py`, the guard on the deleted root README.

The rule has one condition, so the tests are not about parsing. They are about
the two things that decide whether the guard is worth having at all.

**It must fail on a stub.** The previous remedy was a `.claude/rules/` freeze,
which loads only when a session *reads* the file - so a session writing a
short placeholder never met it (`PL-BTSW`, one day after the freeze was
written; `PL-3V4N` for the diagnosis). A guard that passed a two-line README
would reproduce that failure exactly, since a stub is read as instruction and
drifts like any other document.

**The failure must say what to do instead.** The reader has something they
wanted the README to say. A message that only refuses leaves them to work out
where it goes, and the answer - file it, and wait for `PL-N092` - is not
guessable from the refusal.

The scope test is the third: `subprojects/docket/README.md` is the queue
tool's manual and was never in scope. Reaching it is the unanchored-name
mistake `PL-ZQ35` records, arriving in a different tool.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import readme_hold_check


def _run(root: Path, monkeypatch: pytest.MonkeyPatch) -> int:
    monkeypatch.setattr("sys.argv", ["readme_hold_check.py", "--root", str(root)])
    return readme_hold_check.main()


def test_a_checkout_without_the_file_passes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    assert _run(tmp_path, monkeypatch) == 0
    assert capsys.readouterr().err == ""


def test_a_restored_readme_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "README.md").write_text("# Open Anesthesia Simulator\n", encoding="utf-8")

    assert _run(tmp_path, monkeypatch) == 1
    assert capsys.readouterr().out == ""


def test_a_stub_fails_too(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The placeholder is the case the guard exists for, not the exception to it."""
    (tmp_path / "README.md").write_text("See docs/.\n", encoding="utf-8")

    assert _run(tmp_path, monkeypatch) == 1


def test_the_failure_names_the_item_that_lifts_the_hold_and_where_to_file_instead(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "README.md").write_text("# Anything\n", encoding="utf-8")

    _run(tmp_path, monkeypatch)

    message = capsys.readouterr().err
    assert "PL-N092" in message
    assert "bin/docket new" in message


def test_a_readme_below_the_root_is_untouched(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`subprojects/docket/README.md` is the queue tool's manual and is not held."""
    nested = tmp_path / "subprojects" / "docket"
    nested.mkdir(parents=True)
    (nested / "README.md").write_text("# docket\n", encoding="utf-8")

    assert _run(tmp_path, monkeypatch) == 0
