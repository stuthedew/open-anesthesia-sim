"""Tests for `tools/generator_check.py`, the self-reproducing-cluster advisory.

The check exists because `CLAUDE.md`'s "friction that compounds is recommended
the moment it is found" is prose, and prose needs a session to notice. `P2`
holds 187 items, so a cluster that hands back a new item for every one it
closes sits there indistinguishable from a typo (`PL-BHVM` did, for days).

The load-bearing test is `test_a_busy_cluster_is_not_a_generator`. Every
spawned child is attributed to the item that was being worked when it was
captured, so counting all of them rates any heavily-worked file a generator -
which is how `PL-BHVM` came to record `r_vcs = 1.05` as the lane's worst when
the same-cluster figure is 0.90, below the line entirely. A check that makes
that mistake is worse than no check, because its output looks authoritative.
Everything else here is the boundary of the rule.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))

import generator_check


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        env={
            "GIT_AUTHOR_NAME": "t",
            "GIT_AUTHOR_EMAIL": "t@t",
            "GIT_COMMITTER_NAME": "t",
            "GIT_COMMITTER_EMAIL": "t@t",
            "PATH": "/usr/bin:/bin",
        },
    )


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    _git(tmp_path, "init", "-q", "-b", "main")
    (tmp_path / "docs" / "items").mkdir(parents=True)
    return tmp_path


def _write(repo: Path, identifier: str, *, touches: str, status: str, priority: str = "P2") -> Path:
    path = repo / "docs" / "items" / f"{identifier}-x.md"
    path.write_text(
        f"---\nid: {identifier}\ntitle: {identifier} title\npriority: {priority}\n"
        f"status: {status}\ntouches: {touches}\n---\n\nbody\n",
        encoding="utf-8",
    )
    return path


def _commit(repo: Path, subject: str) -> None:
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", subject)


def _closers(repo: Path, path: str, count: int, *, kids_touch: str) -> None:
    """Close `count` items on `path`, each spawning one child touching `kids_touch`."""
    for n in range(count):
        parent = f"PL-C{n:03d}"
        _write(repo, parent, touches=path, status="done")
        _commit(repo, f"{parent}: capture")
        _write(repo, f"PL-K{n:03d}", touches=kids_touch, status="ready")
        _commit(repo, f"{parent}: work that spawned a finding")


def test_a_busy_cluster_is_not_a_generator(repo: Path) -> None:
    """Children landing elsewhere are captures, not reproduction."""
    _closers(repo, "src/thing.py", generator_check.MIN_CLOSED + 2, kids_touch="docs/other.md")
    _write(repo, "PL-OPEN", touches="src/thing.py", status="ready")
    _commit(repo, "PL-OPEN: capture")

    assert generator_check.clusters(repo) == []


def test_a_cluster_reproducing_into_itself_is_reported(repo: Path) -> None:
    _closers(repo, "src/thing.py", generator_check.MIN_CLOSED + 2, kids_touch="src/thing.py")

    reported = generator_check.clusters(repo)
    assert [row[1] for row in reported] == ["src/thing.py"]
    ratio, _, produced, closed, carriers = reported[0]
    assert ratio >= 1.0
    assert produced == closed
    assert [c[1] for c in carriers] == sorted(c[1] for c in carriers)


def test_a_cluster_with_nothing_open_is_history_not_friction(repo: Path) -> None:
    """A generator already closed out is not work anyone can act on."""
    _closers(repo, "src/thing.py", generator_check.MIN_CLOSED + 2, kids_touch="src/thing.py")
    for path in (repo / "docs" / "items").glob("PL-K*.md"):
        path.write_text(path.read_text().replace("status: ready", "status: done"), encoding="utf-8")
    _commit(repo, "PL-C000: close the children")

    assert generator_check.clusters(repo) == []


def test_too_few_closures_to_carry_a_ratio_are_not_reported(repo: Path) -> None:
    _closers(repo, "src/thing.py", generator_check.MIN_CLOSED - 1, kids_touch="src/thing.py")
    _write(repo, "PL-OPEN", touches="src/thing.py", status="ready")
    _commit(repo, "PL-OPEN: capture")

    assert generator_check.clusters(repo) == []


def test_the_store_is_never_a_cluster(repo: Path) -> None:
    """`docs/items` sits inside `workflow_paths`, so every capture would count."""
    _closers(repo, "docs/items", generator_check.MIN_CLOSED + 2, kids_touch="docs/items")
    _write(repo, "PL-OPEN", touches="docs/items/", status="ready")
    _commit(repo, "PL-OPEN: capture")

    assert generator_check.clusters(repo) == []


def test_a_capture_commit_spawns_nothing(repo: Path) -> None:
    """A commit leading with the ids it creates is a capture with no parent."""
    _write(repo, "PL-AAAA", touches="src/thing.py", status="done")
    _write(repo, "PL-BBBB", touches="src/thing.py", status="ready")
    _commit(repo, "PL-AAAA, PL-BBBB: capture two findings")

    parents = generator_check.creation_parents(repo)
    assert parents["PL-AAAA"] == set()
    assert parents["PL-BBBB"] == set()
