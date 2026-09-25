"""Tests for `bin/docket claim` and `bin/docket yield`, against real git.

A bare repository stands in for `origin` and each session is a clone of it,
because what is under test is what a fetch, a push and the remote's hooks do
to a claim: a pre-receive hook is how a push fails, and a post-receive hook is
how another session's claim lands in the minute between this one's fetch and
its push. Every commit is dated through the environment and every read is
given `--now`, so no lease is judged against the clock.
"""

from __future__ import annotations

import os
import stat
import subprocess
from collections.abc import Mapping
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from docket import claiming
from docket.claims import (
    BY_OVER,
    BY_YIELD,
    CUTOVER_MARKER,
    LIVE,
    RELEASED,
    SESSION_VARIABLE,
    holdings,
)
from docket.cli import main

#: When this session claims. The base sits a month earlier, and a rival's claim
#: an hour earlier, so the rival orders first wherever both are live.
T0 = datetime(2026, 9, 1, 12, 0, tzinfo=UTC)
MINUTE = timedelta(minutes=1)
HOUR = timedelta(hours=1)
DAY = timedelta(days=1)

#: The attribution line every claim here is written with.
ATTRIBUTION = "Co-Authored-By: T <t@example.com>"

BRANCH = "claude/work-b7xq2n"
RIVAL = "claude/rival-k2m9p4"


@pytest.fixture(autouse=True)
def _no_session(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep the session running the suite out of every claim written here."""
    monkeypatch.delenv(SESSION_VARIABLE, raising=False)


def _item(identifier: str, status: str = "ready") -> str:
    return f"---\nid: {identifier}\ntitle: {identifier}\nstatus: {status}\n---\n\n**Problem.** x\n"


def _git(root: Path, *args: str, when: datetime | None = None) -> str:
    env = None
    if when is not None:
        env = os.environ | {
            "GIT_AUTHOR_DATE": when.isoformat(),
            "GIT_COMMITTER_DATE": when.isoformat(),
        }
    done = subprocess.run(
        ["git", *args], cwd=root, check=True, capture_output=True, text=True, env=env
    )
    return done.stdout


class _Clone:
    """One session's checkout of the remote."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.items = root / "docs" / "items"
        for name, value in (("user.email", "t@example.com"), ("user.name", "T")):
            self.git("config", name, value)

    def git(self, *args: str, when: datetime | None = None) -> str:
        return _git(self.root, *args, when=when)

    def head(self) -> str:
        return self.git("rev-parse", "HEAD").strip()

    def commit(
        self, message: str, *, when: datetime, files: Mapping[str, str] | None = None
    ) -> str:
        for path, text in (files or {}).items():
            target = self.root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
        self.git("add", "-A")
        self.git("commit", "-q", "--allow-empty", "-m", message, when=when)
        return self.head()

    def claim_by_hand(self, key: str, *, when: datetime) -> str:
        """A claim commit on the branch `HEAD` is on, written as `claim` writes one."""
        branch = self.git("rev-parse", "--abbrev-ref", "HEAD").strip()
        return self.commit(f"{key}: start\n\nClaim: {key} {branch}\n{ATTRIBUTION}", when=when)


class _Remote:
    """A bare `origin` whose `main` holds three items and, unless unmarked, the marker."""

    def __init__(self, tmp_path: Path, *, marked: bool = True) -> None:
        self.tmp = tmp_path
        self.path = tmp_path / "origin.git"
        _git(tmp_path, "-c", "init.defaultBranch=main", "init", "-q", "--bare", str(self.path))
        seed = self.clone("seed")
        files = {
            "docs/items/PL-B1B1-held.md": _item("PL-B1B1"),
            "docs/items/PL-C2C2-other.md": _item("PL-C2C2"),
            "docs/items/PL-D3D3-stopped.md": _item("PL-D3D3", "blocked"),
        }
        if marked:
            files[CUTOVER_MARKER] = "# the claim writer\n"
        seed.commit("base", when=T0 - 30 * DAY, files=files)
        seed.git("push", "-q", "origin", "HEAD:refs/heads/main")

    def clone(self, name: str, branch: str = "") -> _Clone:
        root = self.tmp / name
        _git(self.tmp, "clone", "-q", str(self.path), str(root))
        made = _Clone(root)
        if branch:
            made.git("checkout", "-q", "-b", branch)
        return made

    def hook(self, name: str, script: str) -> None:
        path = self.path / "hooks" / name
        path.write_text(f"#!/bin/sh\n{script}\n", encoding="utf-8")
        path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    def tip(self, branch: str) -> str:
        """The branch's tip on the remote, or `""` where the remote has no such branch."""
        done = subprocess.run(
            ["git", "rev-parse", "--verify", "--quiet", f"refs/heads/{branch}"],
            cwd=self.path,
            capture_output=True,
            text=True,
            check=False,
        )
        return done.stdout.strip()

    def rival(self) -> _Clone:
        """Another session holding PL-B1B1 on its own pushed branch, claimed an hour before T0."""
        other = self.clone("rival", RIVAL)
        other.claim_by_hand("PL-B1B1", when=T0 - HOUR)
        other.git("push", "-q", "-u", "origin", RIVAL)
        return other


def _docket(monkeypatch: pytest.MonkeyPatch, clone: _Clone, *argv: str, when: datetime = T0) -> int:
    """Run one command in `clone`, any commit it makes dated `when`."""
    monkeypatch.setenv("GIT_AUTHOR_DATE", when.isoformat())
    monkeypatch.setenv("GIT_COMMITTER_DATE", when.isoformat())
    return main([*argv, "--items", str(clone.items), "--now", (when + MINUTE).isoformat()])


def _claim(monkeypatch: pytest.MonkeyPatch, clone: _Clone, *argv: str) -> int:
    return _docket(monkeypatch, clone, "claim", *argv, "--trailer", ATTRIBUTION)


def _trailer(clone: _Clone, key: str, rev: str = "HEAD") -> str:
    fmt = f"--format=%(trailers:key={key},valueonly,unfold,separator=%x1e)"
    return clone.git("log", "-1", fmt, rev).strip()


def test_a_claim_is_one_empty_commit_holding_the_record_and_the_attribution_together(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The record and the attribution share the last paragraph, where git reads both.

    Nothing staged rides the claim, the branch is pushed with its upstream set,
    and the claim reads back live - to this checkout and to a fresh clone.
    """
    remote = _Remote(tmp_path)
    work = remote.clone("work", BRANCH)
    (work.root / "staged.py").write_text("x = 1\n", encoding="utf-8")
    work.git("add", "staged.py")
    monkeypatch.setenv(SESSION_VARIABLE, "cse_01ABCDEF")

    assert _claim(monkeypatch, work, "PL-B1B1", "pl-c2c2") == claiming.CLAIMED

    out = capsys.readouterr().out
    assert "PL-B1B1, PL-C2C2: claim written on" in out and "and pushed" in out
    assert work.git("log", "-1", "--format=%s").strip() == "PL-B1B1, PL-C2C2: start"
    assert work.git("diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD").strip() == ""
    assert work.git("diff", "--cached", "--name-only").strip() == "staged.py"
    assert _trailer(work, "Claim").split("\x1e") == [
        f"PL-B1B1 {BRANCH} cse_01ABCDEF",
        f"PL-C2C2 {BRANCH} cse_01ABCDEF",
    ]
    assert _trailer(work, "Co-Authored-By") == "T <t@example.com>"
    assert remote.tip(BRANCH) == work.head()
    assert work.git("rev-parse", "--abbrev-ref", "@{u}").strip() == f"origin/{BRANCH}"

    observer = remote.clone("observer")
    for root in (work.root, observer.root):
        read = holdings(root, now=T0 + HOUR)
        assert [(hold.key, hold.state, hold.session) for hold in read.holds] == [
            ("PL-B1B1", LIVE, "cse_01ABCDEF"),
            ("PL-C2C2", LIVE, "cse_01ABCDEF"),
        ]


def test_an_item_another_branch_holds_first_exits_3_and_writes_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """All or nothing: the item this branch could have had is not claimed either."""
    remote = _Remote(tmp_path)
    remote.rival()
    work = remote.clone("work", BRANCH)
    before = work.head()

    assert _claim(monkeypatch, work, "PL-C2C2", "PL-B1B1") == claiming.HELD_ELSEWHERE

    out = capsys.readouterr().out
    assert f"PL-B1B1: origin/{RIVAL} holds it first" in out
    assert "nothing was written" in out
    assert f"--over origin/{RIVAL}" in out
    assert work.head() == before
    assert remote.tip(BRANCH) == ""


def test_over_takes_the_named_claim_over_by_its_own_commit_and_records_why(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The takeover names the claim commit rather than the branch tip, and sorts ahead of it."""
    remote = _Remote(tmp_path)
    rival = remote.rival()
    held_by = rival.head()
    rival.commit("PL-B1B1: later work", when=T0 - MINUTE, files={"src/w.py": "w = 1\n"})
    rival.git("push", "-q")
    work = remote.clone("work", BRANCH)

    code = _claim(
        monkeypatch, work, "PL-B1B1", "--over", RIVAL, "--reason", "the owner handed it over"
    )

    assert code == claiming.CLAIMED
    assert _trailer(work, "Claim") == f"PL-B1B1 {BRANCH} over {RIVAL}@{held_by}"
    assert work.git("log", "-1", "--format=%b").split("\n\n")[0] == "the owner handed it over"
    read = holdings(work.root, now=T0 + HOUR)
    assert [(hold.ref, hold.state, hold.released_by) for hold in read.holds] == [
        (BRANCH, LIVE, ""),
        (f"origin/{RIVAL}", RELEASED, BY_OVER),
    ]


def test_a_branch_containing_the_holders_tip_continues_it_without_being_asked(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A continuation is a takeover the history already proves, so it needs no `--over`."""
    remote = _Remote(tmp_path)
    rival = remote.rival()
    work = remote.clone("work", BRANCH)
    work.git("merge", "-q", "--no-edit", f"origin/{RIVAL}", when=T0 - MINUTE)

    assert _claim(monkeypatch, work, "PL-B1B1") == claiming.CLAIMED

    assert _trailer(work, "Claim") == f"PL-B1B1 {BRANCH} over {RIVAL}@{rival.head()}"
    assert f"continues {RIVAL}" in work.git("log", "-1", "--format=%b")
    order = holdings(work.root, now=T0 + HOUR).order("PL-B1B1")
    assert [hold.ref for hold in order] == [BRANCH]


def test_work_the_holder_pushed_after_the_branch_took_its_copy_is_no_continuation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    remote = _Remote(tmp_path)
    rival = remote.rival()
    work = remote.clone("work", BRANCH)
    work.git("merge", "-q", "--no-edit", f"origin/{RIVAL}", when=T0 - MINUTE)
    rival.commit("PL-B1B1: more", when=T0 - MINUTE, files={"src/w.py": "w = 1\n"})
    rival.git("push", "-q")

    assert _claim(monkeypatch, work, "PL-B1B1") == claiming.HELD_ELSEWHERE


def test_a_claim_pushed_in_the_same_minute_that_orders_first_exits_3_with_the_yield_line(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The fetch before the write cannot see it; the fetch after the push does.

    The rival's claim is already on the remote under a ref no fetch copies,
    and the remote publishes it as a branch when this session's push lands.
    """
    remote = _Remote(tmp_path)
    rival = remote.clone("rival", RIVAL)
    rival.claim_by_hand("PL-B1B1", when=T0 - HOUR)
    rival.git("push", "-q", "origin", "HEAD:refs/hidden/rival")
    remote.hook("post-receive", f"git update-ref refs/heads/{RIVAL} {rival.head()}")
    work = remote.clone("work", BRANCH)

    assert _claim(monkeypatch, work, "PL-B1B1") == claiming.HELD_ELSEWHERE

    out = capsys.readouterr().out
    assert "and pushed" in out
    assert "just written, orders behind it" in out
    assert "bin/docket yield PL-B1B1" in out
    assert remote.tip(BRANCH) == work.head()


def test_a_push_that_fails_exits_4_and_says_the_claim_is_local(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    remote = _Remote(tmp_path)
    remote.hook("pre-receive", "echo 'refused by the test' >&2; exit 1")
    work = remote.clone("work", BRANCH)
    before = work.head()

    assert _claim(monkeypatch, work, "PL-B1B1") == claiming.LOCAL_ONLY

    out = capsys.readouterr().out
    assert "it is local" in out and "refused by the test" in out
    assert f"git push --set-upstream origin {BRANCH}" in out
    assert work.git("rev-parse", "HEAD~1").strip() == before
    assert _trailer(work, "Claim") == f"PL-B1B1 {BRANCH}"
    assert remote.tip(BRANCH) == ""


def test_a_branch_with_an_upstream_is_committed_and_left_for_the_session_to_push(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Its pull request may be armed, and a push would merge the claim away with it."""
    remote = _Remote(tmp_path)
    work = remote.clone("work", BRANCH)
    work.commit(
        "PL-F4F4: capture", when=T0 - HOUR, files={"docs/items/PL-F4F4-new.md": _item("PL-F4F4")}
    )
    work.git("push", "-q", "-u", "origin", BRANCH)
    pushed = work.head()

    assert _claim(monkeypatch, work, "PL-F4F4") == claiming.CLAIMED

    out = capsys.readouterr().out
    assert "not pushed" in out and "Disarm auto-merge" in out
    assert remote.tip(BRANCH) == pushed != work.head()
    assert [hold.key for hold in holdings(work.root, now=T0 + HOUR).holds] == ["PL-F4F4"]


def test_a_fetch_that_fails_refuses_before_anything_is_written(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    remote = _Remote(tmp_path)
    work = remote.clone("work", BRANCH)
    work.git("remote", "set-url", "origin", str(tmp_path / "gone.git"))
    before = work.head()

    assert _claim(monkeypatch, work, "PL-B1B1") == claiming.REFUSED

    assert "cannot be ruled out; nothing was written" in capsys.readouterr().out
    assert work.head() == before


@pytest.mark.parametrize(
    ("case", "key", "said"),
    [
        ("detached", "PL-B1B1", "HEAD is detached"),
        ("default", "PL-B1B1", "the default branch"),
        ("unknown", "PL-Z9Z9", "HEAD holds no item PL-Z9Z9"),
        ("blocked", "PL-D3D3", "PL-D3D3 is `blocked` in HEAD's copy"),
        ("unmarked", "PL-B1B1", "would be read by the old rules"),
        ("elsewhere", "PL-B1B1", f"{BRANCH} pushes to origin/other"),
    ],
)
def test_a_claim_that_could_not_hold_is_refused_before_anything_is_written(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    case: str,
    key: str,
    said: str,
) -> None:
    """Each would print success over a claim no reader credits, which is worse than refusing."""
    remote = _Remote(tmp_path, marked=case != "unmarked")
    work = remote.clone("work", "" if case == "default" else BRANCH)
    if case == "detached":
        work.git("checkout", "-q", "--detach")
    if case == "elsewhere":
        # Tracking the default branch is the harness's shape and is claimed;
        # tracking a branch of another name is not.
        work.git("push", "-q", "origin", "HEAD:refs/heads/other")
        work.git("branch", "-q", "--set-upstream-to", "origin/other")
    before = work.head()

    assert _claim(monkeypatch, work, key) == claiming.REFUSED

    assert said in capsys.readouterr().out
    assert work.head() == before


@pytest.mark.parametrize(
    "argv",
    [
        ("PL-B1B1", "--over", RIVAL),
        ("PL-B1B1", "--reason", "no takeover to explain"),
        ("PL-B1B1", "--trailer", "not a trailer"),
        ("PL-B1B1", "--trailer", f"Claim: PL-C2C2 {BRANCH}"),
        ("NOT-AN-ID",),
    ],
)
def test_a_malformed_request_is_a_usage_error_and_writes_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, argv: tuple[str, ...]
) -> None:
    remote = _Remote(tmp_path)
    work = remote.clone("work", BRANCH)
    before = work.head()

    assert _claim(monkeypatch, work, *argv) == claiming.USAGE

    assert work.head() == before


def test_claiming_what_the_branch_already_holds_writes_nothing_more(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    remote = _Remote(tmp_path)
    work = remote.clone("work", BRANCH)
    assert _claim(monkeypatch, work, "PL-B1B1") == claiming.CLAIMED
    claimed = work.head()
    capsys.readouterr()

    assert _claim(monkeypatch, work, "PL-B1B1") == claiming.CLAIMED

    assert "already holds it first; nothing written" in capsys.readouterr().out
    assert work.head() == claimed


def test_yield_ends_the_claim_and_refuses_one_the_branch_never_made(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    remote = _Remote(tmp_path)
    work = remote.clone("work", BRANCH)
    assert _claim(monkeypatch, work, "PL-B1B1") == claiming.CLAIMED
    claimed = work.head()

    code = _docket(monkeypatch, work, "yield", "PL-B1B1", "--trailer", ATTRIBUTION, when=T0 + HOUR)

    assert code == claiming.CLAIMED
    assert work.git("log", "-1", "--format=%s").strip() == "PL-B1B1: yield"
    assert _trailer(work, "Yield") == f"PL-B1B1 {BRANCH}"
    assert _trailer(work, "Co-Authored-By") == "T <t@example.com>"
    assert "not pushed" in capsys.readouterr().out
    read = holdings(work.root, now=T0 + 2 * HOUR)
    assert [(hold.commit, hold.state, hold.released_by) for hold in read.holds] == [
        (claimed, RELEASED, BY_YIELD)
    ]

    yielded = work.head()
    assert _docket(monkeypatch, work, "yield", "PL-C2C2") == claiming.REFUSED
    assert "holds no claim on PL-C2C2" in capsys.readouterr().out
    assert work.head() == yielded


def test_running_claim_again_after_a_failed_push_is_the_retry_not_a_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The branch holds the item locally, and a claim no other session sees holds nothing."""
    remote = _Remote(tmp_path)
    remote.hook("pre-receive", "exit 1")
    work = remote.clone("work", BRANCH)
    assert _claim(monkeypatch, work, "PL-B1B1") == claiming.LOCAL_ONLY
    claimed = work.head()

    assert _claim(monkeypatch, work, "PL-B1B1") == claiming.LOCAL_ONLY
    (remote.path / "hooks" / "pre-receive").unlink()
    capsys.readouterr()
    assert _claim(monkeypatch, work, "PL-B1B1") == claiming.CLAIMED

    assert "and pushed" in capsys.readouterr().out
    assert work.head() == claimed == remote.tip(BRANCH)


def test_a_branch_on_the_remote_without_tracking_is_not_pushed_onto(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The remote's copy is what a pull request is open on, whatever the tracking setting says."""
    remote = _Remote(tmp_path)
    work = remote.clone("work", BRANCH)
    work.commit(
        "PL-F4F4: capture", when=T0 - HOUR, files={"docs/items/PL-F4F4-new.md": _item("PL-F4F4")}
    )
    work.git("push", "-q", "origin", BRANCH)
    pushed = work.head()

    assert _claim(monkeypatch, work, "PL-F4F4") == claiming.CLAIMED

    assert f"on the remote as origin/{BRANCH}" in capsys.readouterr().out
    assert remote.tip(BRANCH) == pushed != work.head()


@pytest.mark.parametrize("upstream", [False, True], ids=["ref-only", "ref-and-upstream"])
def test_a_stale_tracking_ref_for_a_branch_the_remote_lacks_is_pushed_through(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    upstream: bool,
) -> None:
    """The harness writes `refs/remotes/origin/<branch>` at session start for a branch nobody
    has pushed, sometimes with the tracking setting too, and a fetch that does not prune keeps
    it; read as the remote's copy, it left every fresh session's claim unpushed (`PL-WX87`).
    """
    remote = _Remote(tmp_path)
    work = remote.clone("work", BRANCH)
    work.git("update-ref", f"refs/remotes/origin/{BRANCH}", "HEAD")
    if upstream:
        work.git("branch", "-q", f"--set-upstream-to=origin/{BRANCH}")

    assert _claim(monkeypatch, work, "PL-B1B1") == claiming.CLAIMED

    out = capsys.readouterr().out
    assert "and pushed" in out and "on the remote" not in out
    assert remote.tip(BRANCH) == work.head()


def test_a_claim_whose_branch_the_remote_deleted_is_pushed_again_not_reported_held(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The clone's tracking ref still carries the claim, and no other session can see it."""
    remote = _Remote(tmp_path)
    work = remote.clone("work", BRANCH)
    assert _claim(monkeypatch, work, "PL-B1B1") == claiming.CLAIMED
    claimed = work.head()
    _git(remote.path, "update-ref", "-d", f"refs/heads/{BRANCH}")
    capsys.readouterr()

    assert _claim(monkeypatch, work, "PL-B1B1") == claiming.CLAIMED

    assert "and pushed" in capsys.readouterr().out
    assert remote.tip(BRANCH) == claimed == work.head()


def test_a_remote_that_cannot_be_asked_leaves_the_claim_local_and_says_so(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Neither pushed blind nor said to be on the remote on the strength of the clone's ref."""
    remote = _Remote(tmp_path)
    work = remote.clone("work", BRANCH)
    work.git("update-ref", f"refs/remotes/origin/{BRANCH}", "HEAD")
    work.git("remote", "set-url", "origin", str(tmp_path / "gone.git"))

    assert _claim(monkeypatch, work, "PL-B1B1", "--no-fetch") == claiming.LOCAL_ONLY

    out = capsys.readouterr().out
    assert "`git ls-remote origin` failed" in out and "It is local" in out
    assert "on the remote as" not in out
    assert _trailer(work, "Claim") == f"PL-B1B1 {BRANCH}"
    claimed = work.head()

    # The retry cannot say the claim is local: an earlier push may have put it there.
    assert _claim(monkeypatch, work, "PL-B1B1", "--no-fetch") == claiming.LOCAL_ONLY

    out = capsys.readouterr().out
    assert "unknown too" in out and "It is local" not in out
    assert work.head() == claimed


def test_a_branch_tracking_the_default_branch_is_pushed_with_an_upstream_of_its_own(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The web harness's own shape (the stress test's scenario u): a session branch made
    with `git checkout -b <branch> --track origin/main`.

    That upstream is not the branch's own, and the remote has no copy of the
    branch for a pull request to be open on, so the claim is pushed at once,
    and the push gives the branch its own upstream.
    """
    remote = _Remote(tmp_path)
    work = remote.clone("work")
    work.git("checkout", "-q", "-b", BRANCH, "--track", "origin/main")
    main = remote.tip("main")

    assert _claim(monkeypatch, work, "PL-B1B1") == claiming.CLAIMED

    assert "and pushed" in capsys.readouterr().out
    assert remote.tip(BRANCH) == work.head()
    assert remote.tip("main") == main
    assert work.git("rev-parse", "--abbrev-ref", "@{u}").strip() == f"origin/{BRANCH}"


def test_a_branch_tracking_the_default_branch_already_on_the_remote_is_given_its_push_command(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Pushed without `-u`, it may carry an armed pull request, so it is not pushed onto.

    A bare `git push` there goes to the default branch or is refused, so the
    message names the one command that pushes the branch to its own copy.
    """
    remote = _Remote(tmp_path)
    work = remote.clone("work")
    work.git("checkout", "-q", "-b", BRANCH, "--track", "origin/main")
    work.commit(
        "PL-F4F4: capture", when=T0 - HOUR, files={"docs/items/PL-F4F4-new.md": _item("PL-F4F4")}
    )
    work.git("push", "-q", "origin", BRANCH)
    pushed = work.head()

    assert _claim(monkeypatch, work, "PL-F4F4") == claiming.CLAIMED

    out = capsys.readouterr().out
    assert f"on the remote as origin/{BRANCH}" in out
    assert f"git push --set-upstream origin {BRANCH}" in out
    assert remote.tip(BRANCH) == pushed != work.head()


def test_a_legacy_claim_shared_by_merging_the_holder_is_continued_not_tied(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """An old-rule claim counts for every branch reaching its commit, so after a merge two
    branches hold it on one commit, and whichever a checkout lists first would win the tie.

    Claiming again then writes nothing more, although the hold still reads as old-rule.
    """
    remote = _Remote(tmp_path, marked=False)
    rival = remote.clone("rival", RIVAL)
    rival.commit("PL-B1B1: start", when=T0 - HOUR)
    rival.git("push", "-q", "-u", "origin", RIVAL)
    landing = remote.clone("landing")
    landing.commit("the claim writer lands", when=T0 - HOUR, files={CUTOVER_MARKER: "# w\n"})
    landing.git("push", "-q", "origin", "main")
    work = remote.clone("work", BRANCH)
    work.git("merge", "-q", "--no-edit", f"origin/{RIVAL}", when=T0 - MINUTE)

    assert _claim(monkeypatch, work, "PL-B1B1") == claiming.CLAIMED

    assert _trailer(work, "Claim") == f"PL-B1B1 {BRANCH} over {RIVAL}@{rival.head()}"
    observer = remote.clone("observer")
    assert [hold.ref for hold in holdings(observer.root, now=T0 + HOUR).order("PL-B1B1")] == [
        f"origin/{BRANCH}"
    ]
    claimed = work.head()
    capsys.readouterr()
    assert _claim(monkeypatch, work, "PL-B1B1") == claiming.CLAIMED
    assert "already holds it first; nothing written" in capsys.readouterr().out
    assert work.head() == claimed


def test_a_claim_on_a_branch_whose_content_has_landed_names_that_as_the_cause(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    remote = _Remote(tmp_path)
    work = remote.clone("work", BRANCH)
    work.commit("PL-B1B1: the work", when=T0 - DAY, files={"src/w.py": "w = 1\n"})
    work.git("push", "-q", "-u", "origin", BRANCH)
    landing = remote.clone("landing")
    landing.commit("PL-B1B1: the work (#1)", when=T0 - HOUR, files={"src/w.py": "w = 1\n"})
    landing.git("push", "-q", "origin", "main")

    assert _claim(monkeypatch, work, "PL-C2C2") == claiming.REFUSED

    assert "the branch reads as landed" in capsys.readouterr().out
