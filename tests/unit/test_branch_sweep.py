"""Tests for `tools/branch_sweep.py`, the daily sweep of finished `claude/` branches.

The rule is tested with each detector's answer substituted, since every
detector has tests of its own: what is pinned here is how their answers
combine, and that one which cannot answer sweeps nothing. The push is tested
against real repositories, a bare `origin` and clones of it, because its safety
is git's: the atomic transaction, and the lease that leaves a branch pushed to
since alone.
"""

from __future__ import annotations

import os
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

import branch_sweep
import pytest
from branch_sweep import (
    GRACE,
    Branch,
    Declined,
    Readings,
    archive_ref,
    branches,
    decide,
    main,
    read_pull_requests,
    read_stranded,
    sweep,
)
from docket.vcs import StrandedEdit, StrandedItem, StrandedReport
from open_pull_requests import PullRequest

NOW = datetime(2026, 9, 27, 6, 17, tzinfo=UTC)
NAME = "claude/done-q7x2kd"


def _branch(committed: datetime) -> Branch:
    return Branch(NAME, "a" * 40, committed)


def test_a_branch_nothing_holds_is_swept_once_its_grace_period_is_over() -> None:
    old, fresh = (
        _branch(NOW - GRACE - timedelta(minutes=1)),
        _branch(NOW - GRACE + timedelta(minutes=1)),
    )
    swept, kept = decide([old, fresh], Readings(), NOW)
    assert swept.kept == ()
    assert kept.kept == ("last commit 71h ago, inside the 72h grace period",)


@pytest.mark.parametrize("ref", [NAME, f"origin/{NAME}"])
def test_a_reason_keeps_the_branch_under_either_spelling_of_its_name(ref: str) -> None:
    # `docket` names the tracking ref and GitHub names the branch. A reason
    # filed under a spelling `decide` does not look up would sweep the branch.
    readings = Readings()
    readings.keep(ref, "pull request #7 is open from it")
    [verdict] = decide([_branch(NOW - 2 * GRACE)], readings, NOW)
    assert verdict.kept == ("pull request #7 is open from it",)


def test_a_pull_request_keeps_both_its_branches_and_an_unanswered_listing_declines(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(branch_sweep, "repo_slug", lambda: "owner/repo")
    listing = (PullRequest(7, "stacked", "claude/top-x1b2c3", "claude/under-y4d5f6"),)
    monkeypatch.setattr(branch_sweep, "open_pull_requests", lambda slug: listing)
    readings = Readings()
    read_pull_requests(Path("."), NOW, readings)
    assert readings.kept == {
        "claude/top-x1b2c3": ["pull request #7 is open from it"],
        "claude/under-y4d5f6": ["pull request #7 is open onto it"],
    }
    # No listing, and a listing whose base went missing, are not "nothing open".
    monkeypatch.setattr(branch_sweep, "open_pull_requests", lambda slug: None)
    with pytest.raises(Declined):
        read_pull_requests(Path("."), NOW, Readings())
    baseless = (PullRequest(8, "t", "claude/top-x1b2c3"),)
    monkeypatch.setattr(branch_sweep, "open_pull_requests", lambda slug: baseless)
    with pytest.raises(Declined):
        read_pull_requests(Path("."), NOW, Readings())


def test_an_edit_keeps_its_branch_only_while_main_holds_the_item_open(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    items = [
        SimpleNamespace(identifier="PL-QP7N", status="ready"),
        SimpleNamespace(identifier="PL-D9NX", status="done"),
    ]
    report = StrandedReport(
        items=(StrandedItem("PL-K3ST", "lost", "p", ("origin/claude/lost-a1b2c3",)),),
        edits=(
            StrandedEdit("PL-QP7N", "open", "p", "p", ("origin/claude/open-d4f5g6",)),
            StrandedEdit("PL-D9NX", "closed", "p", "p", ("origin/claude/closed-h7j8k9",)),
        ),
    )
    monkeypatch.setattr(branch_sweep, "read_items", lambda directory: items)
    monkeypatch.setattr(branch_sweep, "stranded", lambda *args, **kwargs: report)
    readings = Readings()
    read_stranded(tmp_path, NOW, readings)
    assert readings.kept == {
        "claude/lost-a1b2c3": ["the only copy of PL-K3ST"],
        "claude/open-d4f5g6": ["an edit to PL-QP7N, open on main, that main lacks"],
    }
    assert readings.notes == {"claude/closed-h7j8k9": ["an edit to PL-D9NX, which main has closed"]}


def _git(cwd: Path, *args: str, date: str = "") -> str:
    env = {**os.environ, "GIT_AUTHOR_DATE": date, "GIT_COMMITTER_DATE": date} if date else None
    done = subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True, env=env
    )
    return done.stdout.strip()


def _clone(remote: Path, where: Path, *args: str) -> Path:
    subprocess.run(["git", "clone", "-q", *args, str(remote), str(where)], check=True)
    for key, value in (("user.email", "t@example.com"), ("user.name", "T")):
        _git(where, "config", key, value)
    return where


@pytest.fixture
def forge(tmp_path: Path) -> Path:
    """A clone that has fetched `main` and one finished branch, last committed in 2000."""
    remote = tmp_path / "origin.git"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(remote)], check=True)
    work = _clone(remote, tmp_path / "work")
    _git(work, "commit", "-q", "--allow-empty", "-m", "base")
    _git(work, "push", "-q", "origin", "HEAD:refs/heads/main")
    _git(work, "commit", "-q", "--allow-empty", "-m", "work", date="2000-01-01T00:00:00Z")
    _git(work, "push", "-q", "origin", f"HEAD:refs/heads/{NAME}")
    _git(work, "fetch", "-q", "origin")
    return work


def test_a_swept_branch_is_deleted_and_its_tip_kept_under_the_archive(forge: Path) -> None:
    [branch] = branches(forge)
    assert branch.name == NAME
    assert sweep(branch, forge) == ""
    remote = _git(forge, "ls-remote", "origin")
    assert f"{branch.tip}\t{archive_ref(branch)}" in remote
    assert f"refs/heads/{NAME}" not in remote


def test_a_branch_pushed_to_since_it_was_read_is_left_alone(forge: Path, tmp_path: Path) -> None:
    [branch] = branches(forge)
    other = _clone(tmp_path / "origin.git", tmp_path / "other", "-b", NAME)
    _git(other, "commit", "-q", "--allow-empty", "-m", "more")
    _git(other, "push", "-q", "origin", NAME)
    assert sweep(branch, forge) != ""
    remote = _git(forge, "ls-remote", "origin")
    assert f"{_git(other, 'rev-parse', 'HEAD')}\trefs/heads/{NAME}" in remote
    # Atomic: the archive ref went nowhere either.
    assert "refs/archive" not in remote


def test_a_dry_run_pushes_nothing_and_apply_sweeps(
    forge: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(branch_sweep, "READERS", ())
    assert main([], root=forge) == 0
    assert f"refs/heads/{NAME}" in _git(forge, "ls-remote", "origin")
    assert capsys.readouterr().out.startswith("Would sweep")
    assert main(["--apply"], root=forge) == 0
    assert f"refs/heads/{NAME}" not in _git(forge, "ls-remote", "origin")
    assert f"restore: git fetch origin refs/archive/{NAME}/" in capsys.readouterr().out


def test_a_reading_that_cannot_answer_sweeps_nothing(
    forge: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def declining(root: Path, now: datetime, readings: Readings) -> None:
        raise Declined("GitHub's open pull requests could not be listed")

    monkeypatch.setattr(branch_sweep, "READERS", (declining,))
    assert main(["--apply"], root=forge) == 1
    assert f"refs/heads/{NAME}" in _git(forge, "ls-remote", "origin")
    assert (
        capsys.readouterr().out
        == "Nothing swept: GitHub's open pull requests could not be listed.\n"
    )
