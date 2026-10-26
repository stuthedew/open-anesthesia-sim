"""`tools/blind_review_report.py` must count each pass's findings and name what it could not count.

The report is what the monthly model review reads to decide whether the second
blind pass still earns its cost (`PL-0BRY`). A pull request it drops in silence
skews that count without anyone seeing it, so each way of not being counted is
pinned here beside the counts themselves. The repository is a clone of a bare
`origin` whose pull heads sit at `refs/pull/<n>/head`, as GitHub keeps them,
and which the clone has not fetched.
"""

from __future__ import annotations

import subprocess
from collections.abc import Sequence
from pathlib import Path

import pytest
from blind_review_report import Declined, PassRow, TotalsRow, build, network_git, render
from docket.vcs import GitCall

APP = "src/anesthesia_sim/app/panel.py"
CORE = "src/anesthesia_sim/core/uptake.py"


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    ).stdout


class Origin:
    """A bare remote and an author's clone that merges pull requests into it by squash."""

    def __init__(self, tmp_path: Path) -> None:
        self.remote = tmp_path / "origin.git"
        self.author = tmp_path / "author"
        _git(tmp_path, "init", "-q", "--bare", "-b", "main", str(self.remote))
        _git(tmp_path, "clone", "-q", str(self.remote), str(self.author))
        for key, value in (("user.email", "t@example.com"), ("user.name", "T")):
            _git(self.author, "config", key, value)
        _git(self.author, "checkout", "-qb", "main")
        self._write("README.md", "seed\n")
        _git(self.author, "add", "-A")
        _git(self.author, "commit", "-qm", "seed (#1)")
        _git(self.author, "push", "-q", "origin", "main")

    def _write(self, path: str, text: str) -> None:
        target = self.author / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")

    def merge(self, number: int, path: str, record: str | None, *, head: bool = True) -> str:
        """Squash-merge pull request `number`, which changes `path`, and return its head."""
        _git(self.author, "checkout", "-qb", f"pr{number}", "main")
        self._write(path, f"X = {number}\n")
        _git(self.author, "add", "-A")
        _git(self.author, "commit", "-qm", f"PL-B1C2: change {path}")
        if record is not None:
            _git(
                self.author,
                "commit",
                "-q",
                "--allow-empty",
                "-m",
                f"record\n\nBlind-review: {record}",
            )
        tip = _git(self.author, "rev-parse", "HEAD").strip()
        if head:
            _git(self.author, "push", "-q", "origin", f"HEAD:refs/pull/{number}/head")
        _git(self.author, "checkout", "-q", "main")
        _git(self.author, "merge", "-q", "--squash", f"pr{number}")
        _git(self.author, "commit", "-qm", f"PL-B1C2: change {path} (#{number})")
        _git(self.author, "push", "-q", "origin", "main")
        return tip

    def reader(self, tmp_path: Path) -> Path:
        """A fresh clone over `file://`, which copies `main` and none of the pull heads."""
        root = tmp_path / "reader"
        _git(tmp_path, "clone", "-q", f"file://{self.remote}", str(root))
        return root


@pytest.fixture
def origin(tmp_path: Path) -> Origin:
    return Origin(tmp_path)


def test_each_pass_is_counted_and_every_gap_is_named(origin: Origin, tmp_path: Path) -> None:
    origin.merge(2, APP, "pass 1: blocking fixed, optional rejected")
    origin.merge(3, CORE, "passes 2, findings 3, fixed 2, filed 1, rejected 0")
    origin.merge(
        4, CORE, "pass 1: should-fix fixed; pass 2: blocking fixed repeat, should-fix filed"
    )
    origin.merge(5, APP, None)
    origin.merge(6, APP, "pass 1: none", head=False)
    origin.merge(7, "docs/notes.md", None)
    origin.merge(8, CORE, "pass 1: optional fixed")
    origin.merge(9, APP, "pass 1: blocking fiddled")
    root = origin.reader(tmp_path)

    report = build(root, 1, network_git(root))

    assert (report.merged, report.owed_nothing, report.owed) == (8, 1, 7)
    assert report.by_pass == {
        1: PassRow(
            pull_requests=3,
            findings=4,
            fixed_or_filed=3,
            new=3,
            new_serious=2,
            rejected=1,
            with_new=3,
        ),
        2: PassRow(
            pull_requests=1,
            findings=2,
            fixed_or_filed=2,
            new=1,
            new_serious=1,
            rejected=0,
            with_new=1,
        ),
    }
    assert report.older == {2: TotalsRow(pull_requests=1, findings=3, fixed=2, filed=1, rejected=0)}
    assert (report.second_owed, report.second_new_serious) == (1, 1)
    assert report.gaps == [
        (5, "it owed 1 pass and has no Blind-review record"),
        (6, "origin holds no refs/pull/6/head"),
        (8, "counted, but its record lists 1 of the 2 passes it owed"),
        (
            9,
            "its Blind-review record does not parse "
            "(pass 1: 'fiddled' is not one of fixed, filed, rejected)",
        ),
    ]
    shown = "\n".join(render(report))
    assert "| 2 | 1 | 2 | 2 | 1 | 1 | 0 | 1 |" in shown
    assert "- #6: origin holds no refs/pull/6/head" in shown


def test_a_head_that_cannot_be_fetched_is_named(origin: Origin, tmp_path: Path) -> None:
    """A failed fetch is a gap, and the heads in the same batch are still read."""
    origin.merge(2, APP, "pass 1: blocking fixed")
    lost = origin.merge(3, APP, "pass 1: blocking fixed")
    root = origin.reader(tmp_path)
    real = network_git(root)

    def git(args: Sequence[str]) -> GitCall:
        if args[0] == "fetch" and lost in args:
            return GitCall(tuple(args), 128, b"", "fatal: remote error: not our ref")
        return real(args)

    report = build(root, 1, git)

    assert report.gaps == [(3, f"its head {lost[:12]} could not be fetched")]
    assert report.by_pass[1].pull_requests == 1


def test_a_merge_that_owed_nothing_asks_the_remote_nothing(origin: Origin, tmp_path: Path) -> None:
    origin.merge(2, "docs/notes.md", None)
    root = origin.reader(tmp_path)

    def git(args: Sequence[str]) -> GitCall:
        raise AssertionError(f"asked the remote {args}")

    report = build(root, 1, git)

    assert (report.merged, report.owed_nothing, report.gaps) == (1, 1, [])


def test_a_remote_that_will_not_list_its_heads_declines(origin: Origin, tmp_path: Path) -> None:
    origin.merge(2, APP, "pass 1: none")
    root = origin.reader(tmp_path)

    def git(args: Sequence[str]) -> GitCall:
        return GitCall(tuple(args), 128, b"", "fatal: unable to access")

    with pytest.raises(Declined, match="did not list the pull heads"):
        build(root, 1, git)


def test_a_since_no_merge_names_declines(origin: Origin, tmp_path: Path) -> None:
    root = origin.reader(tmp_path)

    with pytest.raises(Declined, match="names #99"):
        build(root, 99, network_git(root))


def test_a_shallow_clone_declines(origin: Origin, tmp_path: Path) -> None:
    origin.merge(2, APP, "pass 1: none")
    root = tmp_path / "shallow"
    _git(tmp_path, "clone", "-q", "--depth", "1", f"file://{origin.remote}", str(root))

    with pytest.raises(Declined, match="shallow"):
        build(root, 1, network_git(root))
