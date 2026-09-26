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


def _claim(monkeypatch: pytest.MonkeyPatch, clone: _Clone, *argv: str, when: datetime = T0) -> int:
    return _docket(monkeypatch, clone, "claim", *argv, "--trailer", ATTRIBUTION, when=when)


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
    assert "Run `bin/docket claim PL-B1B1` again" in out
    assert f"git push --set-upstream origin {BRANCH}" not in out
    assert work.git("rev-parse", "HEAD~1").strip() == before
    assert _trailer(work, "Claim") == f"PL-B1B1 {BRANCH}"
    assert remote.tip(BRANCH) == ""


def test_a_claim_left_unpushed_on_a_branch_the_remote_has_exits_4_because_no_other_session_sees_it(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The stress test's scenario i (`PL-1X56`): a captures-only push went first.

    Its pull request may be armed, so the claim is not pushed onto it - and
    until the session pushes, a second clone's read finds no hold, so the exit
    is the one a failed push gives rather than the one a pushed claim gets.
    Running `claim` again is not the retry it is after a failed push, since
    the branch is still on the remote: it names the same `claim --push` and
    exits 4. That, run once auto-merge is disarmed, publishes the claim.
    """
    remote = _Remote(tmp_path)
    work = remote.clone("work", BRANCH)
    work.commit(
        "PL-F4F4: capture", when=T0 - HOUR, files={"docs/items/PL-F4F4-new.md": _item("PL-F4F4")}
    )
    work.git("push", "-q", "-u", "origin", BRANCH)
    pushed = work.head()

    assert _claim(monkeypatch, work, "PL-F4F4") == claiming.LOCAL_ONLY

    out = capsys.readouterr().out
    assert "not pushed, so only this checkout can see it" in out
    assert "Disarm auto-merge" in out and "`bin/docket claim PL-F4F4 --push`, not `git push`" in out
    assert remote.tip(BRANCH) == pushed != work.head()
    assert [hold.key for hold in holdings(work.root, now=T0 + HOUR).holds] == ["PL-F4F4"]
    other = remote.clone("other")
    assert holdings(other.root, now=T0 + HOUR).holds == ()

    assert _claim(monkeypatch, work, "PL-F4F4") == claiming.LOCAL_ONLY

    out = capsys.readouterr().out
    assert "already holds it first" in out and "`bin/docket claim PL-F4F4 --push`" in out
    claimed = work.head()
    assert _claim(monkeypatch, work, "PL-F4F4", "--push") == claiming.CLAIMED

    assert "and pushed" in capsys.readouterr().out
    assert remote.tip(BRANCH) == claimed == work.head()
    other.git("fetch", "-q", "origin")
    assert [hold.key for hold in holdings(other.root, now=T0 + HOUR).holds] == ["PL-F4F4"]


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

    # The claim's push put the branch on the remote, so the yield is left for
    # the session to push, and exits 4 exactly as a claim left unpushed does.
    assert code == claiming.LOCAL_ONLY
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


def test_yield_run_again_after_its_push_failed_is_the_retry_not_a_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The claim reads as ended here, and every other session still reads it held (`PL-NNLM`).

    The reproduction: a claim pushed, then the remote lacking the branch and
    refusing pushes. The rerun used to exit 0 saying the claim had ended,
    with the remote still carrying no copy of the branch.
    """
    remote = _Remote(tmp_path)
    work = remote.clone("work", BRANCH)
    assert _claim(monkeypatch, work, "PL-B1B1") == claiming.CLAIMED
    _git(remote.path, "update-ref", "-d", f"refs/heads/{BRANCH}")
    remote.hook("pre-receive", "exit 1")
    yield_ = ("yield", "PL-B1B1", "--trailer", ATTRIBUTION)
    assert _docket(monkeypatch, work, *yield_, when=T0 + HOUR) == claiming.LOCAL_ONLY
    yielded = work.head()

    assert _docket(monkeypatch, work, *yield_, when=T0 + HOUR) == claiming.LOCAL_ONLY
    (remote.path / "hooks" / "pre-receive").unlink()
    capsys.readouterr()
    assert _docket(monkeypatch, work, *yield_, when=T0 + HOUR) == claiming.CLAIMED

    assert "and pushed" in capsys.readouterr().out
    assert work.head() == yielded == remote.tip(BRANCH)
    # Once the remote carries it, a rerun has nothing left to do.
    assert _docket(monkeypatch, work, *yield_, when=T0 + HOUR) == claiming.CLAIMED
    assert "has already ended; nothing written" in capsys.readouterr().out
    assert work.head() == yielded == remote.tip(BRANCH)


def test_yield_run_again_on_a_branch_the_remote_holds_without_it_exits_4_and_names_the_push(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A yield held back, since a pull request may be armed there, stays local and says so."""
    remote = _Remote(tmp_path)
    work = remote.clone("work", BRANCH)
    assert _claim(monkeypatch, work, "PL-B1B1") == claiming.CLAIMED
    claimed = work.head()
    yield_ = ("yield", "PL-B1B1", "--trailer", ATTRIBUTION)
    assert _docket(monkeypatch, work, *yield_, when=T0 + HOUR) == claiming.LOCAL_ONLY
    yielded = work.head()
    capsys.readouterr()

    assert _docket(monkeypatch, work, *yield_, when=T0 + HOUR) == claiming.LOCAL_ONLY

    assert f"git push --set-upstream origin {BRANCH}" in capsys.readouterr().out
    assert work.head() == yielded
    assert remote.tip(BRANCH) == claimed


def _order(clone: _Clone, key: str = "PL-B1B1") -> list[str]:
    """Who holds `key` as a fresh fetch of this clone reads it, first first."""
    clone.git("fetch", "-q", "origin")
    return [hold.ref for hold in holdings(clone.root, now=T0 + HOUR).order(key)]


def test_a_claim_confirmed_first_is_not_displaced_by_one_published_later_through_push(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The stress test's scenario i2 (`PL-ZLJ9`): claims order by author date, not push time.

    This branch is on the remote, so its claim is left unpushed and exits 4.
    Another session then claims and reads back as holding, since nothing it
    can fetch says otherwise. Published now, this branch's earlier claim would
    order first and take the item from it; `claim --push` withdraws it with a
    yield instead, left unpushed, which rides whatever push publishes the claim.
    """
    remote = _Remote(tmp_path)
    work = remote.clone("work", BRANCH)
    work.commit("groundwork", when=T0 - HOUR, files={"src/w.py": "w = 1\n"})
    work.git("push", "-q", "-u", "origin", BRANCH)
    pushed = work.head()
    assert _claim(monkeypatch, work, "PL-B1B1") == claiming.LOCAL_ONLY
    claimed = work.head()
    rival = remote.clone("rival", RIVAL)
    assert _claim(monkeypatch, rival, "PL-B1B1", when=T0 + 5 * MINUTE) == claiming.CLAIMED
    capsys.readouterr()

    code = _claim(monkeypatch, work, "PL-B1B1", "--push", when=T0 + 10 * MINUTE)

    assert code == claiming.HELD_ELSEWHERE
    out = capsys.readouterr().out
    assert f"origin/{RIVAL} holds it (claimed" in out and f"claim, {claimed[:12]}, was not" in out
    assert f"Withdrawn by {work.head()[:12]}" in out and "no claim was written" in out
    assert work.git("rev-parse", "HEAD~1").strip() == claimed
    assert _trailer(work, "Yield") == f"PL-B1B1 {BRANCH}"
    assert _trailer(work, "Co-Authored-By") == "T <t@example.com>"
    assert remote.tip(BRANCH) == pushed

    work.git("push", "-q")
    assert _order(rival) == [RIVAL]
    assert _order(remote.clone("observer")) == [f"origin/{RIVAL}"]


def test_a_retry_withdraws_a_claim_a_rival_published_over_while_it_was_unpublished(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The stress test's scenario a3 (`PL-ZLJ9`): the retry after a failed push.

    Running `claim` again is how a failed push is retried, and it used to find
    this branch holding first and push, revoking the claim another session
    made and was told it held while this one was unpublished.
    """
    remote = _Remote(tmp_path)
    remote.hook("pre-receive", "exit 1")
    work = remote.clone("work", BRANCH)
    assert _claim(monkeypatch, work, "PL-B1B1") == claiming.LOCAL_ONLY
    (remote.path / "hooks" / "pre-receive").unlink()
    rival = remote.clone("rival", RIVAL)
    assert _claim(monkeypatch, rival, "PL-B1B1", when=T0 + 5 * MINUTE) == claiming.CLAIMED
    capsys.readouterr()

    assert _claim(monkeypatch, work, "PL-B1B1", when=T0 + 10 * MINUTE) == claiming.HELD_ELSEWHERE

    out = capsys.readouterr().out
    assert "Withdrawn by" in out and f"--over origin/{RIVAL}" in out
    assert _trailer(work, "Yield") == f"PL-B1B1 {BRANCH}"
    assert remote.tip(BRANCH) == ""
    work.git("push", "-q", "-u", "origin", BRANCH)
    assert _order(rival) == [RIVAL]
    assert _order(remote.clone("observer")) == [f"origin/{RIVAL}"]


def test_a_claim_on_another_item_withdraws_a_displaced_claim_its_push_would_publish(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A push publishes every claim on the branch, so the check covers every one.

    The claim asked for goes ahead, and the push carries the withdrawn claim
    with the yield that ends it.
    """
    remote = _Remote(tmp_path)
    remote.hook("pre-receive", "exit 1")
    work = remote.clone("work", BRANCH)
    assert _claim(monkeypatch, work, "PL-B1B1") == claiming.LOCAL_ONLY
    (remote.path / "hooks" / "pre-receive").unlink()
    rival = remote.clone("rival", RIVAL)
    assert _claim(monkeypatch, rival, "PL-B1B1", when=T0 + 5 * MINUTE) == claiming.CLAIMED
    capsys.readouterr()

    assert _claim(monkeypatch, work, "PL-C2C2", when=T0 + 10 * MINUTE) == claiming.CLAIMED

    out = capsys.readouterr().out
    assert "PL-B1B1: " in out and "Withdrawn by" in out and "no claim was written" not in out
    assert "PL-C2C2: claim written on" in out and "and pushed" in out
    assert remote.tip(BRANCH) == work.head()
    observer = remote.clone("observer")
    assert _order(observer) == [f"origin/{RIVAL}"]
    assert _order(observer, "PL-C2C2") == [f"origin/{BRANCH}"]


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

    assert _claim(monkeypatch, work, "PL-F4F4") == claiming.LOCAL_ONLY

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


def test_a_remote_that_cannot_be_asked_withdraws_nothing_until_it_answers(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Scenario a3 with the remote unreachable at the retry (`PL-WX87` over `PL-ZLJ9`).

    Whether this branch's claim is on the remote is what could not be asked, so
    it is not withdrawn on a guess; nothing is pushed either, and the run that
    can ask the remote withdraws it.
    """
    remote = _Remote(tmp_path)
    remote.hook("pre-receive", "exit 1")
    work = remote.clone("work", BRANCH)
    assert _claim(monkeypatch, work, "PL-B1B1") == claiming.LOCAL_ONLY
    (remote.path / "hooks" / "pre-receive").unlink()
    rival = remote.clone("rival", RIVAL)
    assert _claim(monkeypatch, rival, "PL-B1B1", when=T0 + 5 * MINUTE) == claiming.CLAIMED
    work.git("fetch", "-q", "origin")
    url = work.git("remote", "get-url", "origin").strip()
    work.git("remote", "set-url", "origin", str(tmp_path / "gone.git"))
    unpublished = work.head()
    capsys.readouterr()

    assert (
        _claim(monkeypatch, work, "PL-B1B1", "--no-fetch", when=T0 + 10 * MINUTE)
        == claiming.LOCAL_ONLY
    )

    out = capsys.readouterr().out
    assert "`git ls-remote origin` failed" in out and "Withdrawn by" not in out
    assert "`bin/docket claim PL-B1B1` again" in out and "git push" not in out
    assert work.head() == unpublished

    work.git("remote", "set-url", "origin", url)
    assert _claim(monkeypatch, work, "PL-B1B1", when=T0 + 15 * MINUTE) == claiming.HELD_ELSEWHERE
    assert "Withdrawn by" in capsys.readouterr().out
    assert _trailer(work, "Yield") == f"PL-B1B1 {BRANCH}"


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
    message names `claim --push`, which pushes the branch to its own copy and
    gives it its own upstream.
    """
    remote = _Remote(tmp_path)
    work = remote.clone("work")
    work.git("checkout", "-q", "-b", BRANCH, "--track", "origin/main")
    work.commit(
        "PL-F4F4: capture", when=T0 - HOUR, files={"docs/items/PL-F4F4-new.md": _item("PL-F4F4")}
    )
    work.git("push", "-q", "origin", BRANCH)
    pushed = work.head()
    main = remote.tip("main")

    assert _claim(monkeypatch, work, "PL-F4F4") == claiming.LOCAL_ONLY

    out = capsys.readouterr().out
    assert f"on the remote as origin/{BRANCH}" in out
    assert "`bin/docket claim PL-F4F4 --push`" in out
    assert remote.tip(BRANCH) == pushed != work.head()

    assert _claim(monkeypatch, work, "PL-F4F4", "--push") == claiming.CLAIMED

    assert remote.tip(BRANCH) == work.head()
    assert remote.tip("main") == main
    assert work.git("rev-parse", "--abbrev-ref", "@{u}").strip() == f"origin/{BRANCH}"


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


def _close_on_main(remote: _Remote, *, publish: bool = True) -> _Clone:
    """Another session's close-out of PL-B1B1, squash-merged onto the remote's `main`.

    Unpublished, it waits under a ref no fetch copies, for a hook to move `main` onto.
    """
    landing = remote.clone("landing")
    landing.commit(
        "PL-B1B1: the work (#9)",
        when=T0 - HOUR,
        files={"docs/items/PL-B1B1-held.md": _item("PL-B1B1", "done")},
    )
    landing.git("push", "-q", "origin", "HEAD:main" if publish else "HEAD:refs/hidden/landing")
    return landing


def test_a_claim_on_an_item_the_default_branch_closed_after_the_fork_writes_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """`PL-Y48N`, scenario b: refused by the rule the read-back would have released it by.

    `_branch` read only `HEAD`'s copy, which a branch forked before the
    close-out landed still holds at `ready`, so the claim was written, pushed,
    and read back dead as "a defect in docket" - because `holdings` releases a
    claim on any item the base has closed. The base's copy is read after the
    fetch now, and nothing is written or pushed.
    """
    remote = _Remote(tmp_path)
    work = remote.clone("work", BRANCH)
    _close_on_main(remote)
    before = work.head()

    assert _claim(monkeypatch, work, "PL-B1B1") == claiming.REFUSED

    out = capsys.readouterr().out
    assert (
        "claim: PL-B1B1 is `done` on origin/main, which closed it after this branch forked, "
        "and a claim on an item origin/main has closed is released as soon as it is written; "
        "nothing was written." in out
    )
    assert "defect in docket" not in out
    assert work.head() == before
    assert remote.tip(BRANCH) == ""


def test_a_claim_reopening_an_item_the_default_branch_holds_closed_writes_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The same release where the base closed it before the fork and the branch reopened it."""
    remote = _Remote(tmp_path)
    _close_on_main(remote)
    work = remote.clone("work", BRANCH)
    work.commit(
        "PL-B1B1: reopen",
        when=T0 - DAY,
        files={"docs/items/PL-B1B1-held.md": _item("PL-B1B1", "ready")},
    )
    before = work.head()

    assert _claim(monkeypatch, work, "PL-B1B1") == claiming.REFUSED

    out = capsys.readouterr().out
    assert "claim: PL-B1B1 is `done` on origin/main and this branch's copy reopens it" in out
    assert work.head() == before


def test_a_closure_landing_between_the_check_and_the_read_back_is_named_as_one(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The window the refusal cannot close: `main` moves while the claim is pushed.

    The read-back finds the claim released because the base closed the item,
    and says that, rather than calling a finished item a defect in docket.
    """
    remote = _Remote(tmp_path)
    landing = _close_on_main(remote, publish=False)
    remote.hook("post-receive", f"git update-ref refs/heads/main {landing.head()}")
    work = remote.clone("work", BRANCH)

    assert _claim(monkeypatch, work, "PL-B1B1") == claiming.REFUSED

    out = capsys.readouterr().out
    assert "and pushed" in out
    assert "origin/main closed it after the read this claim was checked against" in out
    assert "defect in docket" not in out
