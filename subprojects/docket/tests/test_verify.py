"""Tests for the commission check.

Every test here asserts a *refusal*, bar one. That ratio is the point: this
command exists to catch the ways a green build can be reached without doing
the work, so a regression that made it accept everything must fail the suite
loudly. The accepting case is present so that "rejects everything" cannot pass
either.

The git history each case needs is built in a scratch repository rather than
mocked, because what is being tested is largely what git reports.
"""

from __future__ import annotations

import subprocess
from datetime import date
from pathlib import Path

from docket.config import Config
from docket.model import Item
from docket.verify import changed_paths, item_commits, verify, verify_batch

KEPT = "def test_a() -> None:\n    assert 1 == 1\n"

BRIEF = "**Problem.** P\n**Why it matters.** W\n**Done when.** D\n"


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)


def _repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    (root / "docs" / "items").mkdir(parents=True)
    (root / "tests").mkdir()
    (root / "src").mkdir()
    _git(root.parent, "init", "-q", str(root))
    _git(root, "config", "user.email", "t@example.com")
    _git(root, "config", "user.name", "T")
    (root / "tests" / "test_thing.py").write_text(KEPT)
    (root / "src" / "core.py").write_text("VALUE = 1\n")
    (root / "Makefile").write_text("check:\n\ttrue\n")
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "base")
    return root


def _item(**overrides: object) -> Item:
    base: dict[str, object] = dict(
        identifier="PL-K7QX",
        title="Do the thing",
        priority="P2",
        effort="S",
        status="ready",
        classes=("test",),
        touches=("tests/test_thing.py",),
        blocked_by=(),
        feature="",
        milestone="",
        added=date(2026, 8, 1),
        closed=None,
        commit="",
        reason="",
        body=BRIEF,
        verify="true",
        path="PL-K7QX-do-the-thing.md",
    )
    base.update(overrides)
    return Item(**base)  # type: ignore[arg-type]


def _config(**overrides: object) -> Config:
    settings: dict[str, object] = dict(
        protected_paths=("src",), gate_paths=("Makefile",), check_command="true"
    )
    settings.update(overrides)
    return Config(**settings)  # type: ignore[arg-type]


def _work(root: Path, message: str, path: str, text: str) -> None:
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text)
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", message)


def test_work_inside_the_declared_scope_is_accepted(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    _work(
        root,
        "PL-K7QX add a test",
        "tests/test_thing.py",
        KEPT + "\n\ndef test_b() -> None:\n    assert 2 == 2\n",
    )
    assert verify(root, _item(), _config(), "HEAD~1").passed


def test_a_file_outside_touches_is_rejected(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    _work(root, "PL-K7QX stray edit", "tests/other.py", "x = 1\n")
    report = verify(root, _item(), _config(), "HEAD~1")
    assert not report.passed
    assert any("touches" in c.name and not c.passed for c in report.checks)


def test_editing_a_protected_path_is_rejected(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    _work(root, "PL-K7QX touch the core", "src/core.py", "VALUE = 2\n")
    report = verify(root, _item(touches=("src/core.py",)), _config(), "HEAD~1")
    assert not report.passed
    assert any("protected" in c.name and not c.passed for c in report.checks)


def test_editing_the_gate_is_rejected(tmp_path: Path) -> None:
    """Changing the thing that measures the work invalidates the measurement."""
    root = _repo(tmp_path)
    _work(root, "PL-K7QX relax the build", "Makefile", "check:\n\ttrue\n\n")
    report = verify(root, _item(touches=("Makefile",)), _config(), "HEAD~1")
    assert not report.passed
    assert any("checks themselves" in c.name and not c.passed for c in report.checks)


def test_an_added_suppression_is_rejected(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    _work(
        root,
        "PL-K7QX silence it",
        "tests/test_thing.py",
        KEPT + "\n\ndef test_b() -> None:  # type: ignore[misc]\n    assert 2 == 2\n",
    )
    report = verify(root, _item(), _config(), "HEAD~1")
    assert not report.passed
    assert any("suppression" in c.name and not c.passed for c in report.checks)


def test_a_removed_assertion_is_rejected(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    _work(root, "PL-K7QX drop it", "tests/test_thing.py", "def test_a() -> None:\n    pass\n")
    report = verify(root, _item(), _config(), "HEAD~1")
    assert not report.passed
    assert any("assertion" in c.name and not c.passed for c in report.checks)


def test_a_failing_verify_command_is_rejected(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    _work(
        root,
        "PL-K7QX add a test",
        "tests/test_thing.py",
        KEPT + "\n\ndef test_b() -> None:\n    assert 2 == 2\n",
    )
    report = verify(root, _item(verify="false"), _config(), "HEAD~1")
    assert not report.passed


def test_a_failing_project_check_is_rejected(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    _work(
        root,
        "PL-K7QX add a test",
        "tests/test_thing.py",
        KEPT + "\n\ndef test_b() -> None:\n    assert 2 == 2\n",
    )
    report = verify(root, _item(), _config(check_command="false"), "HEAD~1")
    assert not report.passed


def test_an_item_with_no_verify_command_cannot_be_verified(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    report = verify(root, _item(verify=""), _config(), "HEAD")
    assert not report.passed
    assert len(report.checks) == 1


def test_uncommitted_work_is_counted(tmp_path: Path) -> None:
    """A branch is not clean because its damage has not been committed yet."""
    root = _repo(tmp_path)
    _work(
        root,
        "PL-K7QX add a test",
        "tests/test_thing.py",
        KEPT + "\n\ndef test_b() -> None:\n    assert 2 == 2\n",
    )
    (root / "src" / "core.py").write_text("VALUE = 99\n")
    assert "src/core.py" in changed_paths(root, "HEAD~1", ())


def test_the_diff_is_scoped_to_the_item_s_own_commits(tmp_path: Path) -> None:
    """A batch branch carries several items; each is judged on its own commits.

    Without this, one item checked against the whole branch fails on every
    other item's files, which is both wrong and useless.
    """
    root = _repo(tmp_path)
    base = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=True
    ).stdout.strip()
    _work(
        root,
        "PL-K7QX mine",
        "tests/test_thing.py",
        KEPT + "\n\ndef test_b() -> None:\n    assert 2 == 2\n",
    )
    _work(root, "PL-ZZZZ theirs", "tests/other.py", "x = 1\n")
    commits = item_commits(root, base, "PL-K7QX")
    assert len(commits) == 1
    assert changed_paths(root, base, commits) == ("tests/test_thing.py",)
    assert verify(root, _item(), _config(), base).passed


def test_the_item_s_own_file_is_always_in_scope(tmp_path: Path) -> None:
    """A worker is asked to append a `**Worked.**` note, so its own file counts."""
    root = _repo(tmp_path)
    _work(
        root, "PL-K7QX note", "docs/items/PL-K7QX-do-the-thing.md", "---\nid: PL-K7QX\n---\n\nx\n"
    )
    assert verify(root, _item(), _config(), "HEAD~1").passed


def test_a_base_with_nothing_between_it_and_head_is_not_a_pass(tmp_path: Path) -> None:
    """An empty diff must never read as verified work.

    Found by a test that passed the literal string "HEAD" as the base: every
    path check then had nothing to look at and every one of them passed, so a
    branch with no work in it reported ACCEPT. A mistyped or stale base is the
    likeliest way to reach this, and it is precisely the case where a
    confident green is worst.
    """
    root = _repo(tmp_path)
    report = verify(root, _item(), _config(), "HEAD")
    assert not report.passed
    assert any("something to verify" in c.name for c in report.checks)


def _runs(root: Path) -> int:
    """How many times the project-wide check has been run in this repository."""
    log = root / "runs.txt"
    return len(log.read_text().splitlines()) if log.is_file() else 0


def test_a_batch_runs_the_project_wide_check_once(tmp_path: Path) -> None:
    """Five re-proofs of a proved thing is how a reviewer learns to skip the command."""
    root = _repo(tmp_path)
    _work(
        root,
        "PL-K7QX add a test",
        "tests/test_thing.py",
        KEPT + "\ndef test_b() -> None:\n    assert 2 == 2\n",
    )
    _work(
        root, "PL-B2B2 add another", "tests/other.py", "def test_c() -> None:\n    assert 3 == 3\n"
    )
    config = _config(check_command="echo ran >> runs.txt")
    items = [
        _item(),
        _item(identifier="PL-B2B2", path="PL-B2B2-do-the-other.md", touches=("tests/other.py",)),
    ]

    reports = verify_batch(root, items, config, "HEAD~2")

    assert [report.passed for report in reports] == [True, True]
    assert _runs(root) == 1
    assert all(any("project's own checks" in c.name for c in r.checks) for r in reports)


def test_a_single_item_still_runs_the_project_wide_check(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    _work(
        root,
        "PL-K7QX add a test",
        "tests/test_thing.py",
        KEPT + "\ndef test_b() -> None:\n    assert 2 == 2\n",
    )

    report = verify(root, _item(), _config(check_command="echo ran >> runs.txt"), "HEAD~1")

    assert report.passed
    assert _runs(root) == 1


def test_each_item_in_a_batch_keeps_its_own_command(tmp_path: Path) -> None:
    """Four can be accepted and the fifth rejected, which is the point of the split."""
    root = _repo(tmp_path)
    _work(
        root,
        "PL-K7QX add a test",
        "tests/test_thing.py",
        KEPT + "\ndef test_b() -> None:\n    assert 2 == 2\n",
    )
    _work(
        root, "PL-B2B2 add another", "tests/other.py", "def test_c() -> None:\n    assert 3 == 3\n"
    )
    items = [_item(), _item(identifier="PL-B2B2", path="PL-B2B2-do-the-other.md", verify="false")]

    reports = verify_batch(root, items, _config(), "HEAD~2")

    assert [report.passed for report in reports] == [True, False]


def test_an_item_with_nothing_to_verify_does_not_hold_up_the_batch(tmp_path: Path) -> None:
    """Its report stops before the shared check, which says nothing about it."""
    root = _repo(tmp_path)
    _work(
        root,
        "PL-K7QX add a test",
        "tests/test_thing.py",
        KEPT + "\ndef test_b() -> None:\n    assert 2 == 2\n",
    )
    items = [_item(identifier="PL-B2B2", path="PL-B2B2.md", verify=""), _item()]

    reports = verify_batch(root, items, _config(check_command="echo ran >> runs.txt"), "HEAD~1")

    assert [report.passed for report in reports] == [False, True]
    assert reports[0].stopped_early
    assert _runs(root) == 1
