"""Tests for `claims.holdings`, against real git in scratch repositories.

Real git rather than an injected runner, because what is under test is largely
what git reports: which paragraph it reads a trailer from, how `%aI` and `%cI`
move under a rebase, where a shallow walk ends, and what a commit's own tree
holds. Every commit is dated explicitly, so each lease is judged against an
instant the test names and never against the clock.
"""

from __future__ import annotations

import dataclasses
import os
import subprocess
from collections.abc import Mapping
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

from docket import claiming, render
from docket.claims import (
    BY_CLOSED,
    BY_LANDING,
    BY_OVER,
    BY_STATUS,
    BY_YIELD,
    CLAIM,
    CUT,
    CUTOVER_MARKER,
    DISPOSITION,
    LAPSED,
    LEASE_TERM,
    LIVE,
    NAMED,
    RELEASED,
    SESSION_VARIABLE,
    Hold,
    Holdings,
    Unclaimed,
    holdings,
    in_queue,
    queue_records,
    settled_branches,
    unclaimed,
    work_under_record,
)
from docket.config import Config
from docket.vcs import SILENT, _run_git

#: When the claims under test are made. Each repository's base sits a month
#: earlier, outside every lease.
T0 = datetime(2026, 9, 1, 12, 0, tzinfo=UTC)
HOUR = timedelta(hours=1)
DAY = timedelta(days=1)

#: A branch named the way the web harness names one.
BRANCH = "claude/shallow-walk-b7xq2n"


@pytest.fixture(autouse=True)
def _no_session(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep the session running the suite from deciding `mine` for any test."""
    monkeypatch.delenv(SESSION_VARIABLE, raising=False)


def _item(identifier: str, status: str = "ready", extra: str = "") -> str:
    """An item file carrying what the reader looks at: the id, the status, and any `extra` lines."""
    return (
        f"---\nid: {identifier}\ntitle: {identifier}\nstatus: {status}\n{extra}---\n\n"
        "**Problem.** x\n"
    )


def _dated(when: datetime) -> dict[str, str]:
    """An environment dating a commit's author and committer both at `when`."""
    return os.environ | {
        "GIT_AUTHOR_DATE": when.isoformat(),
        "GIT_COMMITTER_DATE": when.isoformat(),
    }


class _Repo:
    """A scratch repository whose every commit carries the date a test gives it.

    The base holds two open items and, unless `marked` is false, the cutover
    marker - so every commit made on it counts as made after a session could
    write a claim, and an unmarked base builds a history from before.
    """

    def __init__(self, root: Path, *, marked: bool = True) -> None:
        self.root = root
        root.mkdir(parents=True)
        self.git("-c", "init.defaultBranch=main", "init", "-q")
        for name, value in (("user.email", "t@example.com"), ("user.name", "T")):
            self.git("config", name, value)
        files = {
            "docs/items/PL-B1B1-held.md": _item("PL-B1B1"),
            "docs/items/PL-C2C2-other.md": _item("PL-C2C2"),
        }
        if marked:
            files[CUTOVER_MARKER] = "# the claim reader\n"
        self.commit("base", when=T0 - 30 * DAY, files=files)

    def git(self, *args: str, env: Mapping[str, str] | None = None) -> str:
        done = subprocess.run(
            ["git", *args], cwd=self.root, check=True, capture_output=True, text=True, env=env
        )
        return done.stdout

    def branch(self, name: str, start: str = "main") -> None:
        self.git("checkout", "-q", "-b", name, start)

    def commit(
        self, message: str, *, when: datetime, files: Mapping[str, str] | None = None
    ) -> str:
        for path, text in (files or {}).items():
            target = self.root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
        self.git("add", "-A")
        self.git("commit", "-q", "--allow-empty", "-m", message, env=_dated(when))
        return self.git("rev-parse", "HEAD").strip()

    def claim(
        self, *keys: str, when: datetime, token: str = "", session: str = "", over: str = ""
    ) -> str:
        """An empty claim commit, its attribution in the trailer paragraph as `claim` writes it."""
        branch = token or self.git("rev-parse", "--abbrev-ref", "HEAD").strip()
        tail = " ".join(part for part in (session, f"over {over}" if over else "") if part)
        trailers = "\n".join(f"Claim: {key} {branch} {tail}".rstrip() for key in keys)
        message = f"{', '.join(keys)}: start\n\n{trailers}\nCo-Authored-By: T <t@example.com>"
        return self.commit(message, when=when)


def test_a_claim_in_the_last_paragraph_holds_and_one_above_it_is_prose(tmp_path: Path) -> None:
    """git reads a trailer from the last paragraph alone, which is why `claim`
    writes its attribution lines into the same one.

    The second branch also leads with an id on a commit made after claims were
    recorded, which is attribution and claims nothing.
    """
    repo = _Repo(tmp_path / "repo")
    repo.branch("claude/held")
    repo.claim("PL-B1B1", when=T0)
    repo.branch("claude/prose")
    repo.commit(
        "PL-C2C2: start\n\nClaim: PL-C2C2 claude/prose\n\nCo-Authored-By: T <t@example.com>",
        when=T0,
    )

    read = holdings(repo.root, now=T0 + HOUR)

    assert read.known, read.declined
    assert [(hold.key, hold.ref, hold.state) for hold in read.holds] == [
        ("PL-B1B1", "claude/held", LIVE)
    ]
    assert read.ids == {"PL-B1B1"}
    assert read.now == T0 + HOUR


def test_a_claim_holds_only_for_the_branch_its_token_names(tmp_path: Path) -> None:
    """A branch that merged the claiming one carries its claim commit and holds nothing by it.

    `PL-2BZY`'s shape: crediting a commit to whichever ref reached it put a
    bystander's copy of a claim in front of the live one. A claim whose token
    names a branch that is not the one carrying it holds nothing either.
    """
    repo = _Repo(tmp_path / "repo")
    repo.branch("claude/holder")
    repo.claim("PL-B1B1", when=T0)
    repo.branch("claude/bystander")
    repo.commit("PL-C2C2: work", when=T0 + HOUR, files={"src/bystander.py": "x\n"})
    repo.git("merge", "-q", "--no-edit", "claude/holder", env=_dated(T0 + 2 * HOUR))
    repo.branch("claude/misnamed")
    repo.claim("PL-C2C2", when=T0, token="claude/elsewhere")

    read = holdings(repo.root, now=T0 + 3 * HOUR)

    assert [(hold.key, hold.ref) for hold in read.holds] == [("PL-B1B1", "claude/holder")]


def test_a_local_branch_and_its_tracking_ref_are_one_holder(tmp_path: Path) -> None:
    """Renewed by the local branch's unpushed commit, and reported under the local name.

    Leaving the checkout's own branches out reads only what was pushed, where
    the same claim has had no commit for ten days and has lapsed.
    """
    repo = _Repo(tmp_path / "repo")
    repo.branch("claude/held")
    repo.claim("PL-B1B1", when=T0)
    repo.git("remote", "add", "origin", str(tmp_path / "unreachable"))
    repo.git("update-ref", "refs/remotes/origin/main", "main")
    repo.git("update-ref", "refs/remotes/origin/claude/held", "claude/held")
    repo.commit("PL-B1B1: unpushed work", when=T0 + 6 * DAY, files={"src/held.py": "x\n"})

    [hold] = holdings(repo.root, now=T0 + 10 * DAY).holds
    [pushed] = holdings(repo.root, now=T0 + 10 * DAY, include_head=False).holds

    assert (hold.ref, hold.state, hold.renewed) == ("claude/held", LIVE, T0 + 6 * DAY)
    assert (pushed.ref, pushed.state, pushed.renewed) == ("origin/claude/held", LAPSED, T0)


def test_the_lease_holds_through_a_gap_of_exactly_the_term_and_lapses_past_it(
    tmp_path: Path,
) -> None:
    """One claim commit holding two items, judged a second either side of the term.

    Its first renewal comes exactly one term after the claim, and the reads
    fall exactly one term after the last renewal and a second past it, so both
    places a gap is measured - between two commits, and from the last to `now`
    - are pinned at the boundary.

    The claim on the item the base has closed since the branch forked is spent
    at both reads, though the branch's own copy still calls it ready - so
    `lapsed_open` names only the dead claim on the item the base holds open.

    The two claims sharing one commit are a regression test of their own: git
    joins them with `\\x1e`, which `str.splitlines()` also breaks at, and read
    that way the commit and both its claims vanished.
    """
    repo = _Repo(tmp_path / "repo")
    repo.branch("claude/held")
    repo.claim("PL-B1B1", "PL-C2C2", when=T0)
    repo.commit("PL-B1B1: work", when=T0 + LEASE_TERM, files={"src/a.py": "a\n"})
    repo.commit("PL-B1B1: more", when=T0 + 10 * DAY, files={"src/b.py": "b\n"})
    repo.git("checkout", "-q", "main")
    repo.commit(
        "PL-C2C2: close",
        when=T0 + DAY,
        files={"docs/items/PL-C2C2-other.md": _item("PL-C2C2", "done")},
    )

    at_term = holdings(repo.root, now=T0 + 10 * DAY + LEASE_TERM)
    past_term = holdings(repo.root, now=T0 + 10 * DAY + LEASE_TERM + timedelta(seconds=1))

    assert {hold.key: (hold.state, hold.released_by) for hold in at_term.holds} == {
        "PL-B1B1": (LIVE, ""),
        "PL-C2C2": (RELEASED, BY_CLOSED),
    }
    assert {hold.key: (hold.state, hold.renewed) for hold in past_term.holds} == {
        "PL-B1B1": (LAPSED, T0 + 10 * DAY),
        "PL-C2C2": (RELEASED, T0 + 10 * DAY),
    }
    assert past_term.ids == frozenset()
    assert [hold.key for hold in past_term.lapsed_open()] == ["PL-B1B1"]


def test_a_broken_lease_revives_only_through_a_new_claim_which_stakes_later(tmp_path: Path) -> None:
    """A commit after the break renews nothing; a new claim does, from its own date."""
    repo = _Repo(tmp_path / "repo")
    repo.branch("claude/held")
    repo.claim("PL-B1B1", when=T0)
    repo.commit("PL-B1B1: back after eight days", when=T0 + 8 * DAY, files={"src/a.py": "a\n"})

    [broken] = holdings(repo.root, now=T0 + 9 * DAY).holds
    reclaim = repo.claim("PL-B1B1", when=T0 + 9 * DAY)
    [revived] = holdings(repo.root, now=T0 + 10 * DAY).holds

    assert (broken.state, broken.renewed) == (LAPSED, T0)
    assert (revived.state, revived.since, revived.commit) == (LIVE, T0 + 9 * DAY, reclaim)


def test_a_rebase_keeps_the_stake_on_the_author_date_and_renews_on_the_committer_date(
    tmp_path: Path,
) -> None:
    """The first claim is rebased ten days on, which renews its lease without moving its place.

    By committer date it would now sort behind the second claim, made an hour
    after it; by author date it stays first, and without the rebase its lease
    would have lapsed two days before the read.
    """
    repo = _Repo(tmp_path / "repo")
    repo.branch("claude/first")
    repo.claim("PL-B1B1", when=T0)
    repo.branch("claude/second")
    repo.claim("PL-B1B1", when=T0 + HOUR)
    repo.commit("PL-B1B1: work", when=T0 + 5 * DAY, files={"src/second.py": "a\n"})
    repo.commit("PL-B1B1: more", when=T0 + 11 * DAY, files={"src/second.py": "b\n"})
    repo.git("checkout", "-q", "main")
    repo.commit("main moves on", when=T0 + 2 * DAY, files={"src/main.py": "m\n"})
    repo.git("checkout", "-q", "claude/first")
    rebased = T0 + 10 * DAY
    repo.git(
        "rebase",
        "-q",
        "--keep-empty",
        "main",
        env=os.environ | {"GIT_COMMITTER_DATE": rebased.isoformat()},
    )

    first, second = holdings(repo.root, now=T0 + 12 * DAY).order("PL-B1B1")

    assert (first.ref, first.since, first.renewed) == ("claude/first", T0, rebased)
    assert second.ref == "claude/second"


def test_a_yield_on_its_own_branch_releases_the_claim_and_a_later_claim_retakes_it(
    tmp_path: Path,
) -> None:
    """A yield binds like a claim: one naming another branch releases nothing."""
    repo = _Repo(tmp_path / "repo")
    repo.branch("claude/held")
    repo.claim("PL-B1B1", when=T0)
    repo.commit("PL-B1B1: not ours\n\nYield: PL-B1B1 claude/other", when=T0 + HOUR)
    [kept] = holdings(repo.root, now=T0 + 2 * HOUR).holds
    repo.commit("PL-B1B1: stop\n\nYield: PL-B1B1 claude/held", when=T0 + 2 * HOUR)
    [yielded] = holdings(repo.root, now=T0 + 3 * HOUR).holds
    again = repo.claim("PL-B1B1", when=T0 + 4 * HOUR)
    [retaken] = holdings(repo.root, now=T0 + 5 * HOUR).holds

    assert kept.state == LIVE
    assert (yielded.state, yielded.released_by) == (RELEASED, BY_YIELD)
    assert (retaken.state, retaken.commit) == (LIVE, again)


@pytest.mark.parametrize(
    ("status", "state"),
    [
        ("done", RELEASED),
        ("dropped", RELEASED),
        ("blocked", RELEASED),
        ("ready", LIVE),
        ("needs-decision", LIVE),
    ],
)
def test_the_branch_s_own_copy_reaching_a_releasing_status_releases_the_claim(
    tmp_path: Path, status: str, state: str
) -> None:
    """`blocked` releases too, by the project owner's decision of 2026-09-24."""
    repo = _Repo(tmp_path / "repo")
    repo.branch("claude/held")
    repo.claim("PL-B1B1", when=T0)
    repo.commit(
        f"PL-B1B1: {status}",
        when=T0 + HOUR,
        files={"docs/items/PL-B1B1-held.md": _item("PL-B1B1", status)},
    )

    [hold] = holdings(repo.root, now=T0 + 2 * HOUR).holds

    assert (hold.status, hold.state) == (status, state)
    assert hold.released_by == (BY_STATUS if state == RELEASED else "")


def test_a_takeover_takes_the_place_of_the_claim_it_names_and_releases_it(tmp_path: Path) -> None:
    """The successor orders ahead of a claim made while the dead one stood, not behind it.

    Named as `claim --over` will name it, by the tracking ref and an
    abbreviated hash.
    """
    repo = _Repo(tmp_path / "repo")
    repo.git("remote", "add", "origin", str(tmp_path / "unreachable"))
    repo.branch("claude/dead")
    dead = repo.claim("PL-B1B1", when=T0, session="cse_dead")
    repo.branch("claude/waiting")
    repo.claim("PL-B1B1", when=T0 + HOUR, session="cse_waiting")
    repo.branch("claude/successor")
    repo.claim(
        "PL-B1B1", when=T0 + 2 * HOUR, session="cse_next", over=f"origin/claude/dead@{dead[:12]}"
    )

    read = holdings(repo.root, now=T0 + 3 * HOUR)

    assert [hold.ref for hold in read.order("PL-B1B1")] == ["claude/successor", "claude/waiting"]
    [taken] = [hold for hold in read.holds if hold.ref == "claude/dead"]
    assert (taken.state, taken.released_by) == (RELEASED, BY_OVER)


def test_a_git_older_than_2_22_declines_rather_than_reading(tmp_path: Path) -> None:
    """The floor is declared, so an older git says it could not read instead of answering."""
    repo = _Repo(tmp_path / "repo")
    repo.branch("claude/held")
    repo.claim("PL-B1B1", when=T0)

    def old_git(args: list[str], root: Path) -> str:
        return "git version 2.21.0\n" if args == ["version"] else _run_git(args, root)

    read = holdings(repo.root, now=T0 + HOUR, runner=old_git)

    assert read.holds == ()
    assert not read.known
    assert "2.21" in read.declined and "2.22" in read.declined


@pytest.mark.parametrize("branch", [BRANCH, "claude/pl-b1b1-shallow"])
def test_a_walk_that_runs_off_a_truncated_history_is_unread_rather_than_believed(
    tmp_path: Path, branch: str
) -> None:
    """An agent container's shallow clone, in the topology `test_cli.py`'s `_shallow_pair` uses.

    The merge-base resolves, so the first guard passes; the walk still reaches
    below the default branch's graft, and a claim read from it would rest on
    history the base could not exclude. A branch named for its item still
    proves that id, which needs no history, and stays unread (`PL-TZ3R`).
    """
    origin = _Repo(tmp_path / "origin")
    for number in range(1, 11):
        if number == 7:
            origin.branch(branch, "main~5")
            origin.claim("PL-B1B1", when=T0 + HOUR)
            origin.git("merge", "-q", "--no-edit", "main", env=_dated(T0 + 2 * HOUR))
            origin.git("checkout", "-q", "main")
        origin.commit(
            f"main {number}", when=T0 + number * timedelta(minutes=1), files={f"f{number}": "x\n"}
        )
    work = tmp_path / "work"
    for args, cwd in (
        (["clone", "-q", "--depth=5", "--branch", "main", origin.root.as_uri(), str(work)], None),
        (["fetch", "-q", "--depth=3", "origin", f"{branch}:refs/remotes/origin/{branch}"], work),
    ):
        subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)

    read = holdings(work, now=T0 + DAY)

    assert read.holds == ()
    assert read.unreadable == (f"origin/{branch}",)
    named = [(held.name, held.item_id) for held in read.flight().branches]
    assert named == ([] if branch == BRANCH else [(f"origin/{branch}", "PL-B1B1")])


def test_a_merge_of_main_read_below_an_uneven_horizon_spends_only_what_a_squash_took(
    tmp_path: Path,
) -> None:
    """`PL-N162`'s review of slice 2: a claim, then a merge of `main`, read in a shallow clone.

    `main` reaches the root down a short path and is grafted on its long one,
    `test_cli.py`'s `_unevenly_truncated_pair` topology. The merge brings in
    `main`'s own long-path commits, which the walk then reaches below the
    graft: each has a parent, so nothing marks the ref unread, and each writes
    only content the base holds. Main work 3 was authored after the claim and is
    no ancestor of it, so it sorts after the claim in the walk. Taken as the
    landed prefix, it spent the live claim, and `flight` said nobody held the
    item.

    The second branch is the other direction. A squash took its first commit
    before it merged `main`, so its claim is spent, and it stays spent although
    the newest landed commit in its walk is one of `main`'s, which is no
    descendant of the claim.
    """
    squashed = "claude/squashed-q8rt2m"
    origin = _Repo(tmp_path / "origin")
    root = origin.git("rev-parse", "HEAD").strip()
    origin.branch(BRANCH)
    origin.claim("PL-B1B1", when=T0)
    origin.branch(squashed, root)
    origin.claim("PL-C2C2", when=T0)
    origin.commit("PL-C2C2: first", when=T0 + HOUR / 2, files={"src/first.py": "first\n"})
    origin.git("checkout", "-q", "main")
    for number, when in ((1, T0 - 2 * HOUR), (2, T0 - HOUR)):
        origin.commit(f"main work {number}", when=when, files={f"a{number}": f"main {number}\n"})
    origin.commit("PL-C2C2: first (#1)", when=T0 + HOUR / 2, files={"src/first.py": "first\n"})
    origin.commit("main work 3", when=T0 + HOUR, files={"a3": "main 3\n"})
    for branch, path in ((BRANCH, "src/work.py"), (squashed, "src/second.py")):
        origin.git("checkout", "-q", branch)
        origin.git("merge", "-q", "--no-edit", "main", env=_dated(T0 + 2 * HOUR))
        origin.commit("the work", when=T0 + 3 * HOUR, files={path: f"{path}\n"})
    origin.git("checkout", "-q", "main")
    for number in (4, 5, 6):
        origin.commit(
            f"main work {number}", when=T0 + number * HOUR, files={f"a{number}": f"main {number}\n"}
        )
    origin.branch("side", root)
    origin.commit("the short path", when=T0 + 7 * HOUR, files={"side": "side\n"})
    origin.git("checkout", "-q", "main")
    origin.git("merge", "-q", "--no-edit", "side", env=_dated(T0 + 8 * HOUR))
    origin.commit("the tip", when=T0 + 9 * HOUR, files={"tip": "tip\n"})
    work = tmp_path / "work"
    # Five reaches the root down the short path and stops at main work 4 on the
    # long one; the branches are then fetched whole.
    subprocess.run(
        ["git", "clone", "-q", "--depth=5", "--branch", "main", origin.root.as_uri(), str(work)],
        check=True,
        capture_output=True,
    )
    for branch in (BRANCH, squashed):
        subprocess.run(
            ["git", "fetch", "-q", "origin", f"{branch}:refs/remotes/origin/{branch}"],
            cwd=work,
            check=True,
            capture_output=True,
        )
    walk = subprocess.run(
        ["git", "log", "--no-merges", "--format=%p %s", "^origin/main", f"origin/{BRANCH}"],
        cwd=work,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()

    read = holdings(work, now=T0 + 10 * HOUR)

    # The shape the guard cannot catch: the walk reaches main's own commits,
    # and every one of them has a parent.
    assert "main work 3" in [line.split(" ", 1)[1] for line in walk]
    assert all(line.split(" ", 1)[0] for line in walk)
    assert (read.unreadable, read.declined) == ((), "")
    assert {(hold.key, hold.state, hold.released_by) for hold in read.holds} == {
        ("PL-B1B1", LIVE, ""),
        ("PL-C2C2", RELEASED, BY_LANDING),
    }
    assert [(branch.name, branch.item_id) for branch in read.flight().branches] == [
        (f"origin/{BRANCH}", "PL-B1B1")
    ]


def test_a_legacy_start_commit_still_claims_after_the_branch_merges_main(tmp_path: Path) -> None:
    """Legacy is a fact about each commit's own tree, which a later merge of `main` leaves alone.

    A queue-only commit claims nothing under the old rule either, and the
    commit made after the merge carries the marker in its tree, so its leading
    id is attribution only.
    """
    repo = _Repo(tmp_path / "repo", marked=False)
    repo.branch("claude/old")
    repo.commit("PL-B1B1: start", when=T0)
    repo.commit(
        "PL-C2C2: capture",
        when=T0 + HOUR,
        files={"docs/items/PL-C2C2-other.md": _item("PL-C2C2", "untriaged")},
    )
    repo.git("checkout", "-q", "main")
    repo.commit("the claim writer lands", when=T0 + 2 * HOUR, files={CUTOVER_MARKER: "# writer\n"})
    repo.git("checkout", "-q", "claude/old")
    repo.git("merge", "-q", "--no-edit", "main", env=_dated(T0 + 3 * HOUR))
    repo.commit("PL-D3D3: work", when=T0 + 4 * HOUR, files={"src/work.py": "x\n"})

    read = holdings(repo.root, now=T0 + DAY)

    assert [(hold.key, hold.ref, hold.state, hold.legacy) for hold in read.holds] == [
        ("PL-B1B1", "claude/old", LIVE, True)
    ]


def test_a_start_commit_made_once_the_reader_landed_but_before_claim_did_still_claims(
    tmp_path: Path,
) -> None:
    """The window `PL-SW2K` closed: `claims.py` reached `main` before `bin/docket claim`.

    A branch started in between could only push start mode's old empty start
    commit, onto a tree already carrying the reader. Marked by the reader, that
    commit read as claiming nothing; marked by the writer, it is read by the old
    rules and holds.
    """
    repo = _Repo(tmp_path / "repo", marked=False)
    repo.commit(
        "the claim reader lands",
        when=T0 - DAY,
        files={"subprojects/docket/src/docket/claims.py": "# reader\n"},
    )
    repo.branch("claude/between")
    repo.commit("PL-B1B1: start", when=T0)

    read = holdings(repo.root, now=T0 + HOUR)

    assert [(hold.key, hold.ref, hold.state, hold.legacy) for hold in read.holds] == [
        ("PL-B1B1", "claude/between", LIVE, True)
    ]


def test_the_cutover_marker_is_the_module_that_writes_claims() -> None:
    """Renaming it would read every claim written after the rename by the old rules.

    Those read no trailer, so a takeover and a yield would stop counting, with
    nothing failing to say so.
    """
    root = Path(__file__).resolve().parents[3]

    assert (root / CUTOVER_MARKER).resolve() == Path(claiming.__file__).resolve()


def test_two_claims_in_the_same_second_order_on_the_hash(tmp_path: Path) -> None:
    """Arbitrary as a ranking and total as an order, so both sessions compute the same one."""
    repo = _Repo(tmp_path / "repo")
    repo.branch("claude/a")
    first = repo.claim("PL-B1B1", when=T0)
    repo.branch("claude/b")
    second = repo.claim("PL-B1B1", when=T0)

    order = holdings(repo.root, now=T0 + HOUR).order("PL-B1B1")

    assert [hold.commit for hold in order] == sorted([first, second])


def test_a_claim_renewed_inside_its_lease_keeps_its_first_stake(tmp_path: Path) -> None:
    """A branch claiming again does not overtake a claim made before its renewal.

    Ported from `vcs.precedence`'s earliest-not-newest test (`PL-N162`): the
    session at it longest would otherwise lose the item each time it claimed
    again, as a session resuming work is told to.
    """
    repo = _Repo(tmp_path / "repo")
    repo.branch("claude/first")
    stake = repo.claim("PL-B1B1", when=T0)
    repo.branch("claude/second", "main")
    repo.claim("PL-B1B1", when=T0 + HOUR)
    repo.git("checkout", "-q", "claude/first")
    repo.claim("PL-B1B1", when=T0 + 2 * HOUR)

    first, second = holdings(repo.root, now=T0 + 3 * HOUR).order("PL-B1B1")

    assert (first.ref, first.since, first.commit, first.renewed) == (
        "claude/first",
        T0,
        stake,
        T0 + 2 * HOUR,
    )
    assert second.ref == "claude/second"


def test_a_rider_claimed_after_the_branch_s_own_item_stakes_from_its_own_claim(
    tmp_path: Path,
) -> None:
    """A branch taking on a second item did not hold it before it claimed it.

    Ported from `vcs.precedence`'s rider test (`PL-N162`): the branch's first
    claim, on its own item, is older than a rival's claim on the rider, and
    must not carry the rider ahead of it.
    """
    repo = _Repo(tmp_path / "repo")
    repo.branch("claude/rider")
    repo.claim("PL-C2C2", when=T0)
    repo.branch("claude/other", "main")
    repo.claim("PL-B1B1", when=T0 + HOUR)
    repo.git("checkout", "-q", "claude/rider")
    rider = repo.claim("PL-B1B1", when=T0 + 2 * HOUR)

    first, second = holdings(repo.root, now=T0 + 3 * HOUR).order("PL-B1B1")

    assert first.ref == "claude/other"
    assert (second.ref, second.since, second.commit) == ("claude/rider", T0 + 2 * HOUR, rider)


def test_a_branch_named_for_its_item_is_dated_from_its_first_commit_and_orders_nothing(
    tmp_path: Path,
) -> None:
    """Ported from `vcs.precedence`'s name-dating test (`PL-N162`), as the name hold now reads.

    `precedence` ordered a name as a claim; a name holds only where nothing
    claims the item, so it is dated for the reader and is in no order.
    """
    repo = _Repo(tmp_path / "repo")
    repo.branch("claude/pl-b1b1-named")
    first = repo.commit("tidy", when=T0, files={"src/a.py": "a\n"})
    repo.commit("more", when=T0 + HOUR, files={"src/b.py": "b\n"})

    read = holdings(repo.root, now=T0 + 2 * HOUR)

    [name] = read.named
    assert (name.since, name.commit, name.renewed) == (T0, first, T0 + HOUR)
    assert read.order("PL-B1B1") == ()


def test_the_verdict_never_yields_the_first_claim_a_bystander_or_both_sessions(
    tmp_path: Path,
) -> None:
    """`show`'s verdict, read from each of three checkouts of the same two claims.

    Ported from `vcs.precedence`'s three verdict tests (`PL-N162`). The branch
    claiming first holds it, the later one yields, and a branch carrying no
    claim is told the work is elsewhere without being told to yield, since it
    has nothing to hand over. Both sessions read one order, so they cannot
    both stand down, which is the failure worth more than the one it replaces.
    A read that is partial, or missing refs, says so beneath the verdict.
    """
    repo = _Repo(tmp_path / "repo")
    repo.branch("claude/first")
    repo.claim("PL-B1B1", when=T0)
    repo.branch("claude/second", "main")
    repo.claim("PL-B1B1", when=T0 + HOUR)
    repo.branch("claude/bystander", "main")
    repo.commit("PL-C2C2: other work", when=T0 + HOUR, files={"src/other.py": "x\n"})
    now = T0 + 2 * HOUR

    verdicts = {}
    for branch in ("claude/first", "claude/second", "claude/bystander"):
        repo.git("checkout", "-q", branch)
        read = holdings(repo.root, now=now)
        verdicts[branch] = render.format_holds(read, "PL-B1B1", now)
        assert [(hold.ref, hold.mine) for hold in read.order("PL-B1B1")] == [
            ("claude/first", branch == "claude/first"),
            ("claude/second", branch == "claude/second"),
        ]

    assert (
        "This branch holds PL-B1B1; the others are the ones that yield." in verdicts["claude/first"]
    )
    assert "This branch yields: stop" in verdicts["claude/second"]
    assert "This branch claims none of them" in verdicts["claude/bystander"]
    assert [branch for branch, said in verdicts.items() if "This branch yields" in said] == [
        "claude/second"
    ]
    partial = dataclasses.replace(read, declined="git failed to list refs", unreadable=("x", "y"))
    said = render.format_holds(partial, "PL-B1B1", now)
    assert "(This ordering is partial - git failed to list refs" in said
    assert "Do not stand down on it.)" in said
    assert "(2 refs went unread, so this order is over what could be read.)" in said


def test_one_legacy_claim_reached_through_a_merge_is_one_claim_in_every_checkout(
    tmp_path: Path,
) -> None:
    """`PL-N162`'s review: two clones of one merged handoff each read their own branch first.

    A claim read by the old rules counts for every branch reaching its commit,
    so a branch that merged another's carries the same claim and the two tie on
    everything the order ranks. Left to which refs a checkout lists first - its
    own under `refs/heads`, before `refs/remotes` - each clone was told its
    branch holds the item. The order now breaks the tie on the branch's name,
    and `show` prints the one commit as the one claim it is, with no verdict.
    """
    origin = _Repo(tmp_path / "origin", marked=False)
    origin.branch("claude/a")
    stake = origin.commit("PL-B1B1: work", when=T0, files={"src/a.py": "a\n"})
    origin.branch("claude/b", "main")
    origin.commit("tidy", when=T0 + HOUR, files={"src/b.py": "b\n"})
    origin.git("merge", "-q", "--no-edit", "claude/a", env=_dated(T0 + 2 * HOUR))
    origin.git("checkout", "-q", "main")
    now = T0 + 3 * HOUR

    orders, said = {}, {}
    for branch in ("claude/b", "claude/a"):
        work = tmp_path / branch.replace("/", "-")
        for args, cwd in (
            (["clone", "-q", origin.root.as_uri(), str(work)], None),
            (["checkout", "-q", branch], work),
        ):
            subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)
        read = holdings(work, now=now)
        orders[branch] = [
            (hold.ref.removeprefix("origin/"), hold.commit) for hold in read.order("PL-B1B1")
        ]
        said[branch] = render.format_holds(read, "PL-B1B1", now)

    assert orders["claude/a"] == orders["claude/b"] == [("claude/a", stake), ("claude/b", stake)]
    for branch, text in said.items():
        assert f"IN FLIGHT on this branch ({branch}) - PL-B1B1 is this session's own work." in text
        assert "the same claim commit is on origin/claude/" in text
        assert "yields" not in text


def test_a_claim_on_this_branch_by_another_session_is_this_branch_s_claim(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`PL-N162`'s review: a token decides `mine`, and not whether the claim is on this branch.

    Read by another session on the claiming branch, or by the owner with no
    session at all, `show` told the reader that starting the item "here" would
    redo that branch's work - about the branch it was standing on, while
    `claim` there answered that the branch already holds it.
    """
    repo = _Repo(tmp_path / "repo")
    repo.branch("claude/held")
    repo.claim("PL-B1B1", when=T0, session="cse_first")
    now = T0 + HOUR

    for session in ("cse_second", ""):
        monkeypatch.setenv(SESSION_VARIABLE, session)
        read = holdings(repo.root, now=now)
        [hold] = read.order("PL-B1B1")
        assert (hold.mine, read.head) == (False, "claude/held")
        said = render.format_holds(read, "PL-B1B1", now)
        assert (
            "IN FLIGHT on this branch (claude/held) - claimed by another session, not this one."
            in said
        )
        assert "session cse_first" in said
        assert "starting it here would redo" not in said


def test_a_branch_named_for_its_item_that_yielded_it_holds_it_by_nothing(tmp_path: Path) -> None:
    """`PL-N162`'s review: a yield ended the claim and left the name holding for a lease more.

    A branch that recorded a claim on its item holds it by that record, so
    what ends the record ends the hold; `show` had called it a branch that
    "records no claim", which it had, and `flight` went on listing it.
    """
    repo = _Repo(tmp_path / "repo")
    repo.branch("claude/pl-b1b1-work")
    repo.claim("PL-B1B1", when=T0)
    repo.commit("work", when=T0 + HOUR, files={"src/a.py": "a\n"})
    repo.commit("PL-B1B1: stop\n\nYield: PL-B1B1 claude/pl-b1b1-work", when=T0 + 2 * HOUR)
    repo.git("checkout", "-q", "main")
    now = T0 + 3 * HOUR

    read = holdings(repo.root, now=now)

    assert [(hold.ref, hold.state, hold.released_by) for hold in read.holds] == [
        ("claude/pl-b1b1-work", RELEASED, BY_YIELD)
    ]
    assert read.named == ()
    assert "PL-B1B1" not in read.ids
    assert render.format_holds(read, "PL-B1B1", now) == ""


def test_a_claim_the_grammar_cannot_read_is_reported_rather_than_dropped(tmp_path: Path) -> None:
    """A hand-written trailer missing its branch token would otherwise vanish without a word."""
    repo = _Repo(tmp_path / "repo")
    repo.branch("claude/held")
    repo.commit("PL-B1B1: start\n\nClaim: PL-B1B1\nCo-Authored-By: T <t@example.com>", when=T0)

    read = holdings(repo.root, now=T0 + HOUR)

    assert read.holds == ()
    assert len(read.malformed) == 1
    assert read.malformed[0].endswith("on claude/held: Claim: PL-B1B1")


def test_the_session_token_decides_mine_and_the_checked_out_branch_does_without_one(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`HEAD` is on the tokenless branch and not on the branch the session's token claimed."""
    repo = _Repo(tmp_path / "repo")
    repo.branch("claude/theirs")
    repo.claim("PL-B1B1", when=T0, session="cse_theirs")
    repo.branch("claude/ours")
    repo.claim("PL-B1B1", when=T0 + HOUR, session="cse_ours")
    repo.branch("claude/tokenless")
    repo.claim("PL-C2C2", when=T0)
    monkeypatch.setenv(SESSION_VARIABLE, "cse_ours")

    read = holdings(repo.root, now=T0 + 2 * HOUR)

    assert {(hold.key, hold.ref): hold.mine for hold in read.holds} == {
        ("PL-B1B1", "claude/theirs"): False,
        ("PL-B1B1", "claude/ours"): True,
        ("PL-C2C2", "claude/tokenless"): True,
    }


def test_a_now_without_an_offset_is_refused(tmp_path: Path) -> None:
    """A naive instant would be judged in the machine's own zone, hours from the real one."""
    with pytest.raises(ValueError, match="aware"):
        holdings(tmp_path, now=datetime(2026, 9, 1, 12, 0))


def test_a_capture_absent_at_the_fork_holds_nothing(tmp_path: Path) -> None:
    """A branch's capture that the base has since triaged is not a disposition.

    Its copy's status differs from the base's, and without the fork test that
    reads as a branch moving the item: the design round counted eight such
    false holds among captures alone. It is still an edit to the file, which
    is the weaker mark.
    """
    repo = _Repo(tmp_path / "repo")
    repo.branch("claude/capture")
    repo.commit(
        "PL-D4D4: capture",
        when=T0,
        files={"docs/items/PL-D4D4-new.md": _item("PL-D4D4", "untriaged")},
    )
    repo.git("checkout", "-q", "main")
    repo.commit(
        "PL-D4D4: triage",
        when=T0 + HOUR,
        files={"docs/items/PL-D4D4-new.md": _item("PL-D4D4", "ready")},
    )

    read = holdings(repo.root, now=T0 + 2 * HOUR)

    assert (read.holds, read.dispositions, read.ids) == ((), (), frozenset())
    assert [(edit.name, edit.item_id) for edit in read.flight().editing] == [
        ("claude/capture", "PL-D4D4")
    ]


def test_a_block_is_a_disposition_that_holds_without_ordering_and_lapses_with_the_branch(
    tmp_path: Path,
) -> None:
    """`PL-8GV1`: a grooming pass blocking an item it never claimed keeps `next` off it.

    It never orders against a claim, so another branch's claim on the same
    item continues first, and it runs on the branch's lease.
    """
    repo = _Repo(tmp_path / "repo")
    repo.branch("claude/grooming")
    repo.commit(
        "PL-B1B1: block on PL-C2C2",
        when=T0,
        files={"docs/items/PL-B1B1-held.md": _item("PL-B1B1", "blocked")},
    )
    repo.branch("claude/worker", "main")
    repo.claim("PL-B1B1", when=T0 + HOUR)

    read = holdings(repo.root, now=T0 + 2 * HOUR)
    later = holdings(repo.root, now=T0 + 8 * DAY + 2 * HOUR)

    [disposition] = read.dispositions
    assert (disposition.kind, disposition.ref, disposition.state, disposition.status) == (
        DISPOSITION,
        "claude/grooming",
        LIVE,
        "blocked",
    )
    assert [hold.ref for hold in read.order("PL-B1B1")] == ["claude/worker"]
    assert [(branch.name, branch.item_id) for branch in read.flight().branches] == [
        ("claude/worker", "PL-B1B1")
    ]
    [lapsed] = later.dispositions
    assert (lapsed.state, later.ids) == (LAPSED, frozenset())


def test_a_verify_rewrite_across_many_items_holds_none_of_them(tmp_path: Path) -> None:
    """`PL-3W3P`: a pass rewriting one field of many items moves no status, so holds nothing.

    Every file it wrote is still an edit the base has not taken, and only the
    item the branch claimed is held.
    """
    repo = _Repo(tmp_path / "repo")
    keys = ["PL-F6F6", "PL-G7G7", "PL-H8H8", "PL-J9J9"]
    repo.commit(
        "more items",
        when=T0 - 20 * DAY,
        files={f"docs/items/{key}-x.md": _item(key) for key in keys},
    )
    repo.branch("claude/sweep")
    repo.claim("PL-C2C2", when=T0)
    repo.commit(
        "PL-C2C2: reorder every verify: line",
        when=T0 + HOUR,
        files={f"docs/items/{key}-x.md": _item(key, extra="verify: true\n") for key in keys},
    )

    read = holdings(repo.root, now=T0 + 2 * HOUR)
    report = read.flight()

    assert read.dispositions == ()
    assert read.ids == {"PL-C2C2"}
    assert [branch.item_id for branch in report.branches] == ["PL-C2C2"]
    assert [edit.item_id for edit in report.editing] == keys


def test_the_landed_prefix_spends_what_a_partial_squash_took_and_a_new_claim_holds(
    tmp_path: Path,
) -> None:
    """`PL-8JQQ`: the squash took the claim and its first commit; the branch went on.

    The branch is still unlanded - its later commit is not on the base - but
    the claim the squash took is spent, so continued work claims again, and
    that claim holds - even where the squash took everything before it, so
    the branch as of the new claim is all on the base. A commit restoring a file
    the base once held lands nothing, though every blob it writes is one the
    base has held.
    """
    repo = _Repo(tmp_path / "repo")
    repo.branch("claude/long")
    repo.claim("PL-B1B1", when=T0)
    repo.commit("PL-B1B1: first", when=T0 + HOUR, files={"src/a.py": "first\n"})
    repo.git("checkout", "-q", "main")
    repo.commit("PL-B1B1: first (#1)", when=T0 + 2 * HOUR, files={"src/a.py": "first\n"})
    repo.git("checkout", "-q", "claude/long")
    repo.commit("PL-B1B1: second", when=T0 + 3 * HOUR, files={"src/b.py": "second\n"})

    [spent] = holdings(repo.root, now=T0 + 4 * HOUR).holds
    again = repo.claim("PL-B1B1", when=T0 + 5 * HOUR)
    [held] = holdings(repo.root, now=T0 + 6 * HOUR).holds

    repo.branch("claude/revert", "main")
    repo.claim("PL-C2C2", when=T0)
    repo.commit("PL-C2C2: try", when=T0 + HOUR, files={"src/a.py": "tried\n"})
    repo.commit("PL-C2C2: undo", when=T0 + 2 * HOUR, files={"src/a.py": "first\n"})
    [kept] = [
        hold for hold in holdings(repo.root, now=T0 + 6 * HOUR).holds if hold.key == "PL-C2C2"
    ]

    repo.branch("claude/whole", "main")
    repo.claim("PL-D4D4", when=T0)
    repo.commit("PL-D4D4: all of it", when=T0 + HOUR, files={"src/c.py": "whole\n"})
    repo.git("checkout", "-q", "main")
    repo.commit("PL-D4D4: all of it (#2)", when=T0 + 2 * HOUR, files={"src/c.py": "whole\n"})
    repo.git("checkout", "-q", "claude/whole")
    resumed = repo.claim("PL-D4D4", when=T0 + 3 * HOUR)
    repo.commit("PL-D4D4: more", when=T0 + 4 * HOUR, files={"src/d.py": "more\n"})
    [fresh] = [
        hold for hold in holdings(repo.root, now=T0 + 6 * HOUR).holds if hold.key == "PL-D4D4"
    ]

    assert (spent.state, spent.released_by) == (RELEASED, BY_LANDING)
    assert (held.state, held.commit) == (LIVE, again)
    assert kept.state == LIVE
    # The branch as of the new claim is all on the base, but the claim wrote
    # nothing, so it cannot be where a squash took the branch; read as one, it
    # would spend the claim the work after it is done under.
    assert (fresh.state, fresh.commit) == (LIVE, resumed)


def test_holder_is_the_first_live_claim_whose_item_names_the_resource(tmp_path: Path) -> None:
    """Two release items claimed on two branches: the earlier claim holds the train.

    Read from each claiming branch's own copy, so a release item's claim holds
    it without a flag its session has to remember; once that claim yields, the
    other branch's does. A claim on an item naming no resource is never it.
    """
    train = "resource: release-train\n"
    repo = _Repo(tmp_path / "repo")
    repo.branch("claude/first")
    repo.commit(
        "PL-R1R1: file the release",
        when=T0,
        files={"docs/items/PL-R1R1-cut.md": _item("PL-R1R1", extra=train)},
    )
    repo.claim("PL-R1R1", when=T0 + HOUR)
    repo.branch("claude/second", "main")
    repo.commit(
        "PL-R2R2: file the release",
        when=T0,
        files={"docs/items/PL-R2R2-cut.md": _item("PL-R2R2", extra=train)},
    )
    repo.claim("PL-R2R2", "PL-B1B1", when=T0 + 2 * HOUR)

    first = holdings(repo.root, now=T0 + 3 * HOUR).holder("release-train")
    repo.git("checkout", "-q", "claude/first")
    repo.commit("PL-R1R1: stop\n\nYield: PL-R1R1 claude/first", when=T0 + 4 * HOUR)
    then = holdings(repo.root, now=T0 + 5 * HOUR).holder("release-train")

    assert first is not None and (first.ref, first.key, first.kind) == (
        "claude/first",
        "PL-R1R1",
        CLAIM,
    )
    assert then is not None and (then.ref, then.key) == ("claude/second", "PL-R2R2")


def test_a_cut_is_a_live_hold_and_mine_where_head_contains_the_branch(tmp_path: Path) -> None:
    """`cuts_in_flight`'s read: a notes file the base lacks, whatever the branch's age.

    A branch editing notes the base already holds is cutting nothing.
    """
    repo = _Repo(tmp_path / "repo")
    repo.commit("v0.5.9", when=T0 - 20 * DAY, files={"docs/releases/v0.5.9.md": "# v0.5.9\n"})
    repo.branch("claude/theirs")
    repo.commit("cut", when=T0, files={"docs/releases/v0.5.10.md": "# v0.5.10\n"})
    repo.branch("claude/fix-notes", "main")
    repo.commit("fix", when=T0, files={"docs/releases/v0.5.9.md": "# v0.5.9, fixed\n"})
    repo.branch("claude/ours", "main")
    repo.commit("cut", when=T0 + HOUR, files={"docs/releases/v0.5.11.md": "# v0.5.11\n"})

    cuts = holdings(repo.root, now=T0 + 30 * DAY).cuts

    assert [(hold.ref, hold.key, hold.kind, hold.state, hold.mine) for hold in cuts] == [
        ("claude/ours", "0.5.11", CUT, LIVE, True),
        ("claude/theirs", "0.5.10", CUT, LIVE, False),
    ]


def test_flight_names_a_branch_attributed_to_nothing(tmp_path: Path) -> None:
    """The third outcome beside a hold and an unread ref, kept in `FlightReport`'s shape."""
    repo = _Repo(tmp_path / "repo")
    repo.branch("claude/anonymous")
    repo.commit("tidy", when=T0, files={"src/tidy.py": "x\n"})
    repo.branch("claude/pl-b1b1-named", "main")
    repo.commit("tidy", when=T0, files={"src/named.py": "x\n"})

    report = holdings(repo.root, now=T0 + HOUR).flight()

    assert report.unattributed == ("claude/anonymous",)
    assert [(branch.name, branch.item_id) for branch in report.branches] == [
        ("claude/pl-b1b1-named", "PL-B1B1")
    ]
    assert report.known


def test_a_branch_named_for_its_item_holds_it_behind_any_claim_and_lapses_with_the_branch(
    tmp_path: Path,
) -> None:
    """`PL-TZ3R`: the name is a hold of its own, which `flight` reads where nothing else holds.

    It never orders against a claim, so a claim elsewhere is the branch
    `flight` names, and it runs on the branch's lease.
    """
    repo = _Repo(tmp_path / "repo")
    repo.branch("claude/pl-b1b1-named")
    repo.commit("tidy", when=T0, files={"src/named.py": "x\n"})

    alone = holdings(repo.root, now=T0 + HOUR)
    later = holdings(repo.root, now=T0 + 8 * DAY)
    repo.branch("claude/worker", "main")
    repo.claim("PL-B1B1", when=T0 + HOUR)
    claimed = holdings(repo.root, now=T0 + 2 * HOUR)

    [name] = alone.named
    assert (name.kind, name.ref, name.state, alone.order("PL-B1B1")) == (
        NAMED,
        "claude/pl-b1b1-named",
        LIVE,
        (),
    )
    assert [(branch.name, branch.item_id) for branch in alone.flight().branches] == [
        ("claude/pl-b1b1-named", "PL-B1B1")
    ]
    assert (later.named[0].state, later.flight().branches, later.ids) == (LAPSED, (), frozenset())
    assert [(branch.name, branch.item_id) for branch in claimed.flight().branches] == [
        ("claude/worker", "PL-B1B1")
    ]


# --- `settled_branches`: which in-flight refs have finished (`PL-Q664`) -----
#
# Read from the holds since `PL-N162`: closing an item in the branch's own copy
# releases the branch's claim, and only the disposition that the same status
# move creates still says which ref closed what.


def _close(repo: _Repo, key: str, status: str, when: datetime) -> None:
    """A commit moving the base's own copy of `key` to `status` on the checked-out branch."""
    slug = {"PL-B1B1": "held", "PL-C2C2": "other"}[key]
    repo.commit(
        f"{key}: {status}", when=when, files={f"docs/items/{key}-{slug}.md": _item(key, status)}
    )


@pytest.mark.parametrize("status", ["done", "dropped"])
def test_a_branch_that_closed_what_it_claimed_is_settled_and_stays_in_flight(
    tmp_path: Path, status: str
) -> None:
    """The claim is released by the close, and the disposition it leaves is what settles.

    The item stays in flight: the work exists on a branch, and offering it
    again would have a second session redo what is already written.
    """
    repo = _Repo(tmp_path / "repo")
    repo.branch("claude/finished")
    repo.claim("PL-B1B1", when=T0)
    _close(repo, "PL-B1B1", status, T0 + HOUR)

    read = holdings(repo.root, now=T0 + 2 * HOUR)
    settled = settled_branches(repo.root, read, opened=lambda: ())

    assert [(hold.state, hold.released_by) for hold in read.holds] == [(RELEASED, BY_STATUS)]
    assert [(entry.name, entry.item_ids) for entry in settled.branches] == [
        ("claude/finished", ("PL-B1B1",))
    ]
    assert settled.branches[0].last_commit == T0 + HOUR
    assert settled.known
    assert read.flight().ids == frozenset({"PL-B1B1"})


def test_a_branch_that_blocked_what_it_claimed_is_not_settled(tmp_path: Path) -> None:
    """`blocked` releases the claim, but a blocked item is not finished work.

    So the disposition it leaves keeps the branch in the live list, which is
    why the rule reads `CLOSED_STATUSES` rather than `RELEASING_STATUSES`.
    """
    repo = _Repo(tmp_path / "repo")
    repo.branch("claude/stalled")
    repo.claim("PL-B1B1", when=T0)
    _close(repo, "PL-B1B1", "blocked", T0 + HOUR)

    read = holdings(repo.root, now=T0 + 2 * HOUR)

    assert [hold.released_by for hold in read.holds] == [BY_STATUS]
    assert read.flight().ids == frozenset({"PL-B1B1"})
    assert settled_branches(repo.root, read, opened=lambda: ()).branches == ()


@pytest.mark.parametrize("blocked_on_base", [False, True])
def test_a_blocked_claim_with_no_disposition_behind_it_leaves_the_branch_live(
    tmp_path: Path, blocked_on_base: bool
) -> None:
    """The claim itself says the item is blocked, where no disposition is left to.

    A capture the base never had makes no disposition, and neither does a
    block the base already shows. Either way the branch holds the only record
    of unfinished work beside a close-out, and reading only the dispositions
    reported it as finished (`PL-N162`, slice 4's review).
    """
    repo = _Repo(tmp_path / "repo")
    files = {"src/y.py": "x\n"}
    if blocked_on_base:
        key = "PL-C2C2"
        _close(repo, key, "blocked", T0 - DAY)
        repo.branch("claude/work")
    else:
        key = "PL-D4D4"
        repo.branch("claude/work")
        capture = "docs/items/PL-D4D4-new.md"
        repo.commit(f"{key}: capture", when=T0 - HOUR, files={capture: _item(key)})
        files[capture] = _item(key, "blocked")
    repo.claim(key, when=T0)
    repo.commit(f"{key}: blocked", when=T0 + HOUR, files=files)
    _close(repo, "PL-B1B1", "done", T0 + 2 * HOUR)

    read = holdings(repo.root, now=T0 + 3 * HOUR)

    assert [(hold.key, hold.released_by, hold.status) for hold in read.holds] == [
        (key, BY_STATUS, "blocked")
    ]
    assert [hold.key for hold in read.dispositions] == ["PL-B1B1"]
    assert [(branch.name, branch.item_id) for branch in read.flight().branches] == [
        ("claude/work", "PL-B1B1")
    ]
    assert settled_branches(repo.root, read, opened=lambda: ()).branches == ()


def test_a_lapsed_claim_on_an_open_item_leaves_the_branch_live(tmp_path: Path) -> None:
    """A lapsed claim holds nothing, but the branch that made it may still carry its work."""
    repo = _Repo(tmp_path / "repo")
    repo.branch("claude/dormant")
    repo.claim("PL-C2C2", when=T0)
    _close(repo, "PL-B1B1", "done", T0 + LEASE_TERM + DAY)

    read = holdings(repo.root, now=T0 + LEASE_TERM + 2 * DAY)

    assert [(hold.key, hold.state) for hold in read.holds] == [("PL-C2C2", LAPSED)]
    assert [(branch.name, branch.item_id) for branch in read.flight().branches] == [
        ("claude/dormant", "PL-B1B1")
    ]
    assert settled_branches(repo.root, read, opened=lambda: ()).branches == ()


def test_a_claim_shadowed_by_another_branch_s_still_leaves_its_branch_live(tmp_path: Path) -> None:
    """Every claim the ref recorded is asked, not only one that won its item's row.

    The later claim gets no row, because the earlier one holds the item; the
    session behind it is still working, and calling its branch finished is the
    expensive mistake.
    """
    repo = _Repo(tmp_path / "repo")
    repo.branch("claude/first")
    repo.claim("PL-C2C2", when=T0)
    repo.branch("claude/second", "main")
    repo.claim("PL-C2C2", when=T0 + HOUR)
    _close(repo, "PL-B1B1", "done", T0 + 2 * HOUR)

    read = holdings(repo.root, now=T0 + 3 * HOUR)

    assert [(branch.name, branch.item_id) for branch in read.flight().branches] == [
        ("claude/second", "PL-B1B1"),
        ("claude/first", "PL-C2C2"),
    ]
    assert settled_branches(repo.root, read, opened=lambda: ()).branches == ()


def test_one_item_still_claimed_leaves_the_whole_branch_live(tmp_path: Path) -> None:
    repo = _Repo(tmp_path / "repo")
    repo.branch("claude/mixed")
    repo.claim("PL-B1B1", "PL-C2C2", when=T0)
    _close(repo, "PL-B1B1", "done", T0 + HOUR)

    read = holdings(repo.root, now=T0 + 2 * HOUR)

    assert settled_branches(repo.root, read, opened=lambda: ()).branches == ()


def test_a_branch_named_for_a_capture_it_closed_is_settled_by_its_name(tmp_path: Path) -> None:
    """A capture holds by no claim and no disposition, only by the branch's name.

    The name counts as a disposition does: it holds only where the branch
    recorded no claim, so its copy's status is the branch's own close-out.
    """
    repo = _Repo(tmp_path / "repo")
    repo.branch("claude/pl-d4d4-capture")
    repo.commit(
        "PL-D4D4: capture and close",
        when=T0,
        files={"docs/items/PL-D4D4-new.md": _item("PL-D4D4", "done")},
    )

    read = holdings(repo.root, now=T0 + HOUR)
    settled = settled_branches(repo.root, read, opened=lambda: ())

    assert [(hold.kind, hold.status, hold.on_base) for hold in read.named] == [
        (NAMED, "done", False)
    ]
    assert [(entry.name, entry.item_ids) for entry in settled.branches] == [
        ("claude/pl-d4d4-capture", ("PL-D4D4",))
    ]


def test_a_branch_named_for_an_item_it_holds_no_copy_of_is_not_settled(tmp_path: Path) -> None:
    """Its copy has no status, so nothing says it finished: the silence reads as live."""
    repo = _Repo(tmp_path / "repo")
    repo.branch("claude/pl-d4d4-thing")
    repo.commit("tidy", when=T0, files={"src/tidy.py": "x\n"})

    read = holdings(repo.root, now=T0 + HOUR)

    assert read.flight().ids == frozenset({"PL-D4D4"})
    assert settled_branches(repo.root, read, opened=lambda: ()).branches == ()


def test_a_close_out_shadowed_by_another_branch_s_claim_settles_nothing(tmp_path: Path) -> None:
    """Only a ref with a row in `flight` is asked about, so a settled row replaces a live one.

    Listing a branch the report never named would add a line about work
    nobody reads as in flight, beside a report saying nothing is.
    """
    repo = _Repo(tmp_path / "repo")
    repo.branch("claude/claimer")
    repo.claim("PL-B1B1", when=T0)
    repo.branch("claude/closer", "main")
    _close(repo, "PL-B1B1", "done", T0 + HOUR)

    read = holdings(repo.root, now=T0 + 2 * HOUR)

    assert [(branch.name, branch.item_id) for branch in read.flight().branches] == [
        ("claude/claimer", "PL-B1B1")
    ]
    assert settled_branches(repo.root, read, opened=lambda: ()).branches == ()


def test_a_finished_branch_with_a_pull_request_open_is_not_reported(tmp_path: Path) -> None:
    """Every item closed and a pull request open is a branch waiting on review.

    The pull request names `claude/x` and the ref is `origin/claude/x`, so the
    remote is stripped against the remotes git lists before they are compared.
    """
    repo = _Repo(tmp_path / "repo")
    repo.git("remote", "add", "origin", (tmp_path / "nowhere").as_uri())
    repo.branch("claude/reviewing")
    repo.claim("PL-B1B1", when=T0)
    _close(repo, "PL-B1B1", "done", T0 + HOUR)
    repo.git("update-ref", "refs/remotes/origin/claude/reviewing", "HEAD")
    repo.git("checkout", "-q", "main")
    repo.git("branch", "-q", "-D", "claude/reviewing")

    read = holdings(repo.root, now=T0 + 2 * HOUR)
    reviewing = settled_branches(repo.root, read, opened=lambda: ["claude/reviewing"])
    elsewhere = settled_branches(repo.root, read, opened=lambda: ["claude/other"])

    assert (reviewing.branches, reviewing.asked) == ((), True)
    assert [entry.name for entry in elsewhere.branches] == ["origin/claude/reviewing"]


def test_a_close_out_lists_only_the_ids_its_own_rows_show(tmp_path: Path) -> None:
    """An item whose row another branch's claim holds is not listed as settled here too.

    Its disposition still has to be closed for the branch to settle, but the
    id belongs to the live row, and printing it in both sections would say
    the item is being worked and finished at once.
    """
    repo = _Repo(tmp_path / "repo")
    repo.branch("claude/claimer")
    repo.claim("PL-B1B1", when=T0)
    repo.branch("claude/closer", "main")
    _close(repo, "PL-B1B1", "done", T0 + HOUR)
    _close(repo, "PL-C2C2", "done", T0 + 2 * HOUR)

    read = holdings(repo.root, now=T0 + 3 * HOUR)
    settled = settled_branches(repo.root, read, opened=lambda: ())

    assert sorted(hold.key for hold in read.dispositions) == ["PL-B1B1", "PL-C2C2"]
    assert [(entry.name, entry.item_ids) for entry in settled.branches] == [
        ("claude/closer", ("PL-C2C2",))
    ]


def test_a_name_the_base_closed_is_passed_over_and_the_branch_settles(tmp_path: Path) -> None:
    """A released hold asks nothing: the base's close ended it, so its status is no evidence.

    The branch blocked its named item and closed another; the base then
    closed the named one, which releases the name and leaves no disposition.
    """
    repo = _Repo(tmp_path / "repo")
    repo.branch("claude/pl-c2c2-slug")
    _close(repo, "PL-C2C2", "blocked", T0)
    _close(repo, "PL-B1B1", "done", T0 + HOUR)
    repo.git("checkout", "-q", "main")
    _close(repo, "PL-C2C2", "done", T0 + 2 * HOUR)

    read = holdings(repo.root, now=T0 + 3 * HOUR)
    settled = settled_branches(repo.root, read, opened=lambda: ())

    assert [(hold.key, hold.state, hold.released_by, hold.status) for hold in read.named] == [
        ("PL-C2C2", RELEASED, BY_CLOSED, "blocked")
    ]
    assert [hold.key for hold in read.dispositions] == ["PL-B1B1"]
    assert [(entry.name, entry.item_ids) for entry in settled.branches] == [
        ("claude/pl-c2c2-slug", ("PL-B1B1",))
    ]


def test_the_remote_prefix_is_stripped_only_for_remotes_git_lists(tmp_path: Path) -> None:
    """`feature/reviewing` is a local branch, not `reviewing` on a remote called `feature`.

    A naive first-segment strip would drop it whenever the forge had an
    unrelated `reviewing` open, silently hiding finished work.
    """
    repo = _Repo(tmp_path / "repo")
    repo.git("remote", "add", "origin", (tmp_path / "nowhere").as_uri())
    repo.branch("feature/reviewing")
    repo.claim("PL-B1B1", when=T0)
    _close(repo, "PL-B1B1", "done", T0 + HOUR)

    read = holdings(repo.root, now=T0 + 2 * HOUR)
    settled = settled_branches(repo.root, read, opened=lambda: ["reviewing"])

    assert [entry.name for entry in settled.branches] == ["feature/reviewing"]
    assert settled.known


@pytest.mark.parametrize("opened", [None, lambda: None])
def test_a_forge_that_could_not_be_asked_reports_the_half_it_read(
    tmp_path: Path, opened: Any
) -> None:
    """No way to ask and a forge that refused are one answer: half the test, said as half."""
    repo = _Repo(tmp_path / "repo")
    repo.branch("claude/finished")
    repo.claim("PL-B1B1", when=T0)
    _close(repo, "PL-B1B1", "done", T0 + HOUR)

    settled = settled_branches(repo.root, holdings(repo.root, now=T0 + 2 * HOUR), opened=opened)

    assert [entry.name for entry in settled.branches] == ["claude/finished"]
    assert (settled.asked, settled.known) == (False, False)


def test_the_forge_is_not_asked_when_no_branch_has_finished(tmp_path: Path) -> None:
    """The cheap half decides whether the expensive one runs at all."""
    repo = _Repo(tmp_path / "repo")
    repo.branch("claude/working")
    repo.claim("PL-B1B1", when=T0)
    asked: list[bool] = []

    def opened() -> tuple[str, ...]:
        asked.append(True)
        return ()

    settled = settled_branches(repo.root, holdings(repo.root, now=T0 + HOUR), opened=opened)

    assert (settled.branches, asked, settled.asked) == ((), [], True)


def test_a_ref_whose_commits_went_unread_is_never_settled() -> None:
    """Its name proves the id, and nothing read says what else the ref carries.

    Built from the holds directly, because the one shape that could settle it -
    a name hold recording a closed status on a ref in `unreadable` - is one
    `holdings` never produces: an unread ref has no copy to read a status from.
    The rule is kept anyway, so a later reader that learns to read one cannot
    settle a ref whose history it never compared.
    """
    ref = "origin/claude/pl-d4d4-thing"
    hold = Hold(
        key="PL-D4D4",
        ref=ref,
        kind=NAMED,
        state=LIVE,
        since=T0,
        renewed=T0,
        commit="",
        status="done",
    )
    read = Holdings(named=(hold,), unreadable=(ref,), now=T0)

    assert [branch.name for branch in read.flight().branches] == [ref]
    assert settled_branches(Path("."), read, opened=lambda: ()).branches == ()


# A work branch that claims nothing (`PL-FFR0`, moved here from
# `tools/branch_id_check.py`, whose tests still hold its CI refusal).

#: The queue as this repository's settings name it: the default has no notes file.
QUEUE = Config(notes_file="docs/WORKING_NOTES.md")


def test_unclaimed_names_a_work_branch_that_never_claimed_and_no_other(tmp_path: Path) -> None:
    """The forgetful session, against the branches that owe nothing.

    Its subject leads with an id, which is attribution and claims nothing.
    The branch that claimed and then closed its item has released its claim,
    and a claim counts in any state (project owner, 2026-09-24): "no live
    claim" would call every finished branch forgetful. A triage pass writes
    the roadmap and the notes as well as items, and all three are the queue.
    A branch named for its item holds it by the name, and one outside
    `claude/` is a contributor's, who has nothing to claim with.
    """
    repo = _Repo(tmp_path / "repo")
    repo.branch("claude/forgetful-a1b2c3")
    repo.commit("PL-B1B1: the work", when=T0, files={"src/work.py": "WORK = 1\n"})
    repo.branch("claude/finished-d4e5f6", "main")
    repo.claim("PL-C2C2", when=T0)
    repo.commit("PL-C2C2: the work", when=T0, files={"src/done.py": "DONE = 1\n"})
    repo.commit(
        "PL-C2C2: close", when=T0, files={"docs/items/PL-C2C2-other.md": _item("PL-C2C2", "done")}
    )
    repo.branch("claude/triage-g7h8j9", "main")
    repo.commit(
        "PL-B1B1: triage",
        when=T0,
        files={"ROADMAP.md": "- PL-B1B1\n", "docs/WORKING_NOTES.md": "## thread\n"},
    )
    repo.branch("claude/pl-b1b1-named", "main")
    repo.commit("the work", when=T0, files={"src/named.py": "NAMED = 1\n"})
    repo.branch("feature/contributor", "main")
    repo.commit("a fix", when=T0, files={"src/fix.py": "FIX = 1\n"})

    read = holdings(repo.root, now=T0 + HOUR)
    found = unclaimed(repo.root, read, QUEUE)

    assert found == Unclaimed(branches=("claude/forgetful-a1b2c3",))
    assert [(hold.ref, hold.state) for hold in read.holds] == [("claude/finished-d4e5f6", RELEASED)]


def test_unclaimed_skips_work_made_before_a_session_could_claim(tmp_path: Path) -> None:
    """A commit whose own tree lacks the marker is read by the old rule, which this catch skips."""
    repo = _Repo(tmp_path / "repo", marked=False)
    repo.branch("claude/old-session-a1b2c3")
    repo.commit("the work", when=T0, files={"src/work.py": "WORK = 1\n"})

    read = holdings(repo.root, now=T0 + HOUR)

    assert work_under_record(repo.root, "main", "claude/old-session-a1b2c3", QUEUE) is False
    assert unclaimed(repo.root, read, QUEUE) == Unclaimed()


def test_unclaimed_names_a_branch_git_did_not_answer_about_apart(tmp_path: Path) -> None:
    """A silence is not "claims something": the branch is named as unknown, not dropped."""
    repo = _Repo(tmp_path / "repo")
    repo.branch("claude/forgetful-a1b2c3")
    repo.commit("the work", when=T0, files={"src/work.py": "WORK = 1\n"})
    read = holdings(repo.root, now=T0 + HOUR)

    def silent_log(args: list[str], root: Path) -> str:
        return SILENT if "log" in args else _run_git(args, root)

    assert unclaimed(repo.root, read, QUEUE, runner=silent_log) == Unclaimed(
        unasked=("claude/forgetful-a1b2c3",)
    )
    declined = dataclasses.replace(read, declined="git did not answer")
    assert unclaimed(repo.root, declined, QUEUE) == Unclaimed()


def test_the_queue_is_the_items_the_roadmap_the_notes_and_the_body_records() -> None:
    assert queue_records(QUEUE) == (
        "docs/items/",
        "ROADMAP.md",
        "docs/WORKING_NOTES.md",
        "docs/pr-bodies/",
    )
    assert in_queue("docs/items/PL-B1B1-held.md", QUEUE)
    assert in_queue("ROADMAP.md", QUEUE)
    assert in_queue("docs/WORKING_NOTES.md", QUEUE)
    assert in_queue("docs/pr-bodies/1066.md", QUEUE)
    assert not in_queue("docs/items-archive.md", QUEUE)
    assert not in_queue("docs/pr-bodies.md", QUEUE)
    assert not in_queue("src/work.py", QUEUE)


def test_a_body_record_is_not_work_that_owes_a_claim(tmp_path: Path) -> None:
    """A pull request's body record is a queue record, so a queue-only pass still owes no claim.

    `tools/pr_body_check.py --record` writes one on every pull request's branch
    before its merge, since `pr-title` fails without it (`PL-979D`), so a
    capture, a triage pass or a design round carries one as surely as its
    items. Read as work, it named each such branch a forgetful session here and
    had CI refuse it (`PL-F6MM`). The branch whose record rides real work is
    still named, so the record is what the answer turns on.
    """
    repo = _Repo(tmp_path / "repo")
    repo.branch("claude/capture-a1b2c3")
    repo.commit(
        "PL-D3D3: capture a finding",
        when=T0,
        files={"docs/items/PL-D3D3-found.md": _item("PL-D3D3", "untriaged")},
    )
    repo.commit(
        "PL-D3D3: record the body", when=T0, files={"docs/pr-bodies/1066.md": "---\npr: 1066\n"}
    )
    repo.branch("claude/forgetful-d4e5f6", "main")
    repo.commit(
        "PL-B1B1: record the body", when=T0, files={"docs/pr-bodies/1067.md": "---\npr: 1067\n"}
    )
    repo.commit("PL-B1B1: the work", when=T0, files={"src/work.py": "WORK = 1\n"})

    read = holdings(repo.root, now=T0 + HOUR)

    assert unclaimed(repo.root, read, QUEUE) == Unclaimed(branches=("claude/forgetful-d4e5f6",))


def test_flight_s_rows_carry_the_kind_and_state_of_the_hold_behind_each(tmp_path: Path) -> None:
    """`Holdings.holding` is what `flight` rows are made from, so the columns cannot disagree.

    A claim, a status disposition and a branch name each hold one item here,
    and the rendered rows name each by its kind; the report without the read
    prints no columns, as it did before.
    """
    repo = _Repo(tmp_path / "repo")
    repo.branch("claude/claimed-a1b2c3")
    repo.claim("PL-B1B1", when=T0)
    repo.branch("claude/triage-d4e5f6", "main")
    repo.commit(
        "PL-C2C2: block",
        when=T0,
        files={"docs/items/PL-C2C2-other.md": _item("PL-C2C2", "blocked")},
    )
    repo.branch("claude/pl-f5f5-named", "main")
    repo.commit("the work", when=T0, files={"src/named.py": "NAMED = 1\n"})

    read = holdings(repo.root, now=T0 + HOUR)
    held = read.holding()
    printed = render.format_flight(read.flight(), T0 + HOUR, read=read)
    bare = render.format_flight(read.flight(), T0 + HOUR)

    assert {key: (hold.kind, hold.state) for key, hold in held.items()} == {
        "PL-B1B1": (CLAIM, LIVE),
        "PL-C2C2": (DISPOSITION, LIVE),
        "PL-F5F5": (NAMED, LIVE),
    }
    assert [row.key for row in (held[key] for key in sorted(held))] == [
        branch.item_id for branch in read.flight().branches
    ]
    rows = [line for line in printed.splitlines() if line.startswith("PL-")]
    kinds = ("claim", "status disposition", "branch name")
    assert len(rows) == len(kinds)
    for row, kind in zip(rows, kinds, strict=True):
        assert f"  live  {kind:<18}  last commit" in row
    assert "  live  " not in bare
    assert "legacy refs: 0" in printed
    assert "legacy refs" not in bare


def test_a_lapsed_claim_beside_a_later_live_claim_is_no_lapsed_row(tmp_path: Path) -> None:
    """The ordinary takeover of a dead claim: the heading would say `next` offers a held item.

    `claim` passes a lapsed claim without `--over`, so the first branch's
    claim stays lapsed beside the second's live one until its ref goes.
    `next` offers nothing there and `show` prints only the live claim, so
    `flight` lists the item once, on the live row (review of `PL-N162`'s slice 5).
    """
    repo = _Repo(tmp_path / "repo")
    repo.branch("claude/first-a1b2c3")
    repo.claim("PL-B1B1", when=T0 - LEASE_TERM - 2 * DAY)
    repo.branch("claude/second-d4e5f6", "main")
    repo.claim("PL-B1B1", when=T0)

    read = holdings(repo.root, now=T0 + HOUR)
    printed = render.format_flight(read.flight(), T0 + HOUR, read=read)

    assert [(hold.ref, hold.state) for hold in read.lapsed_open()] == [
        ("claude/first-a1b2c3", LAPSED)
    ]
    assert "PL-B1B1" in read.ids
    assert "lapsed" not in printed
    assert "claude/first-a1b2c3" not in printed
    assert [line.split()[:2] for line in printed.splitlines() if line.startswith("PL-")] == [
        ["PL-B1B1", "claude/second-d4e5f6"]
    ]


def test_unclaimed_reads_a_remote_tracking_ref_by_its_branch_name(tmp_path: Path) -> None:
    """On a real clone every ref is `origin/claude/...`, and the prefix test reads the branch.

    Asked of the ref as written, no remote ref would start `claude/`, and the
    rows would go empty for good on every checkout that matters while a run
    here still printed none - the silent wrong answer this pins.
    """
    repo = _Repo(tmp_path / "repo")
    repo.git("remote", "add", "origin", str(tmp_path / "unreachable"))
    repo.git("update-ref", "refs/remotes/origin/main", "main")
    repo.branch("claude/forgetful-a1b2c3")
    repo.commit("the work", when=T0, files={"src/work.py": "WORK = 1\n"})
    repo.branch("claude/claimed-d4e5f6", "main")
    repo.claim("PL-B1B1", when=T0)
    repo.commit("PL-B1B1: the work", when=T0, files={"src/held.py": "HELD = 1\n"})
    repo.git("checkout", "-q", "main")
    for name in ("claude/forgetful-a1b2c3", "claude/claimed-d4e5f6"):
        repo.git("update-ref", f"refs/remotes/origin/{name}", name)
        repo.git("branch", "-q", "-D", name)

    read = holdings(repo.root, now=T0 + HOUR)

    assert unclaimed(repo.root, read, QUEUE) == Unclaimed(
        branches=("origin/claude/forgetful-a1b2c3",)
    )


def test_flight_names_the_branches_git_did_not_answer_about_apart() -> None:
    """A branch whose log git refused is neither an `unclaimed:` row nor silently dropped."""
    read = Holdings(now=T0)
    printed = render.format_flight(
        read.flight(), T0, read=read, unclaimed=Unclaimed(unasked=("origin/claude/quiet-a1b2c3",))
    )

    assert "unclaimed:" not in printed
    assert (
        "Whether 1 branch claims nothing is unknown - git did not answer which of its commits "
        "are work: origin/claude/quiet-a1b2c3." in printed
    )


def test_legacy_refs_reads_no_conclusion_from_a_read_git_declined() -> None:
    """`PL-CH3Z` starts on `legacy refs: 0`, and a declined read holds nothing to count.

    `holdings` returns exactly this object when git is below the floor; the
    zero it would count is the absence of a reading, not a reading of none.
    """
    read = Holdings(now=T0, declined="git 2.1 is older than the floor")
    printed = render.format_flight(read.flight(), T0, read=read)

    assert "legacy refs: unknown - git did not answer (git 2.1 is older than the floor)" in printed
    assert "legacy refs: 0" not in printed
    assert "nothing here still needs the old rule" not in printed
