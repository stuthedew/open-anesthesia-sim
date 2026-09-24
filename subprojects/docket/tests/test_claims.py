"""Tests for `claims.holdings`, against real git in scratch repositories.

Real git rather than an injected runner, because what is under test is largely
what git reports: which paragraph it reads a trailer from, how `%aI` and `%cI`
move under a rebase, where a shallow walk ends, and what a commit's own tree
holds. Every commit is dated explicitly, so each lease is judged against an
instant the test names and never against the clock.
"""

from __future__ import annotations

import os
import subprocess
from collections.abc import Mapping
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from docket import claiming
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
    RELEASED,
    SESSION_VARIABLE,
    holdings,
)
from docket.vcs import _run_git

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


def test_a_walk_that_runs_off_a_truncated_history_is_unread_rather_than_believed(
    tmp_path: Path,
) -> None:
    """An agent container's shallow clone, in the topology `test_cli.py`'s `_shallow_pair` uses.

    The merge-base resolves, so the first guard passes; the walk still reaches
    below the default branch's graft, and a claim read from it would rest on
    history the base could not exclude.
    """
    origin = _Repo(tmp_path / "origin")
    for number in range(1, 11):
        if number == 7:
            origin.branch(BRANCH, "main~5")
            origin.claim("PL-B1B1", when=T0 + HOUR)
            origin.git("merge", "-q", "--no-edit", "main", env=_dated(T0 + 2 * HOUR))
            origin.git("checkout", "-q", "main")
        origin.commit(
            f"main {number}", when=T0 + number * timedelta(minutes=1), files={f"f{number}": "x\n"}
        )
    work = tmp_path / "work"
    for args, cwd in (
        (["clone", "-q", "--depth=5", "--branch", "main", origin.root.as_uri(), str(work)], None),
        (["fetch", "-q", "--depth=3", "origin", f"{BRANCH}:refs/remotes/origin/{BRANCH}"], work),
    ):
        subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)

    read = holdings(work, now=T0 + DAY)

    assert read.holds == ()
    assert read.unreadable == (f"origin/{BRANCH}",)


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
    assert (report.branches, report.known) == ((), True)
