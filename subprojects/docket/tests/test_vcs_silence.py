"""Every public read of `vcs`, with one git call silenced, held to the floor.

`.claude/rules/apparatus-standard.md`: "What this apparatus tells a session must
be true, or must say what it could not read." `vcs` breached that wherever a
reader took the empty string a failed `git` collapses to for an empty *answer* -
`_superseded` read a failed `git diff --numstat` as the two tips agreeing about
every path it was handed, so one such call took `branches_in_flight` from
fourteen `editing` marks to none with `FlightReport.unreadable` empty in both
cases (`PL-Q9Z1`, `PL-BHVM`'s design round).

**Prose cannot enforce this, which is why the sweep exists.** `_superseded`'s
own docstring stated the right direction in three cases while the code inverted
two of them, and it had said so since the function was written. So the rule is
driven rather than asserted against itself: run each public read against a real
repository, then run it again with its *n*-th git call silenced, once for every
call it made, and hold the answer to one property - it declines, or it reports
everything the truthful read reported. Losing a mark while saying nothing went
unread is the failure.

Unlike `test_vcs.py`, which injects git rather than invoking it, this needs a
real repository: the point is the plumbing, and `_run_git`'s classification of
git's exit codes is half of what is under test.

Silencing one call at a time never reaches a read whose every call git answers
where there is no repository at all, so each read is run once more from a
directory in none, where it must decline (`PL-19T3`).
"""

from __future__ import annotations

import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import pytest

from docket.vcs import (
    SILENT,
    GitRunner,
    Runner,
    _run_git,
    answered,
    behind_remote,
    branch_state,
    branches_in_flight,
    change_landed,
    changed_items,
    churn,
    closed_by,
    closures_on_base,
    commands_written_here,
    cut_window,
    cuts_in_flight,
    default_base,
    filed_with_work,
    files_in_flight,
    is_shallow,
    lost,
    merged_pull_requests,
    open_pull_requests,
    orphaned,
    precedence,
    records_on_base,
    ref_walk,
    released_on_base,
    resolved,
    settled_branches,
    since_filed,
    stranded,
    tags,
    working_paths,
)

ITEM = """---
id: {identifier}
title: {title}
status: {status}
added: 2026-09-01
touches: src/{slug}.py
{extra}---

**Problem.** {title}
"""

CLOSED_EXTRA = "closed: 2026-09-02\nverify: uv run pytest\n"


def _git(root: Path, *args: str) -> str:
    done = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=True)
    return done.stdout.strip()


def _write(root: Path, path: str, body: str) -> None:
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body)


def _item(root: Path, identifier: str, title: str, status: str = "ready") -> None:
    _write(
        root,
        f"docs/items/{identifier}-fixture.md",
        ITEM.format(
            identifier=identifier,
            title=title,
            status=status,
            slug=identifier.lower(),
            extra=CLOSED_EXTRA if status == "done" else "",
        ),
    )


@pytest.fixture(scope="module")
def repo(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """A checkout carrying one of everything these reads are built to find.

    Every read in `READS` has to find something here or the sweep proves nothing
    about it, which is what the vacuity guard in the test below enforces - so
    this is long on purpose, and each block below says which read it feeds.

    Remote-tracking refs are written with `update-ref` rather than pushed to a
    second repository: `default_base` wants `origin/main` to resolve and nothing
    here needs a remote behind it, so a fabricated ref is the same fact at a
    fraction of the setup.
    """
    root = tmp_path_factory.mktemp("silence")
    _git(root, "init", "--quiet", "--initial-branch=main")
    _git(root, "config", "user.email", "t@example.invalid")
    _git(root, "config", "user.name", "Test")

    # The base: a store, a shipped release, and one item already closed on it,
    # which is what `closures_on_base` and `records_on_base` compare against.
    _write(root, "pyproject.toml", 'version = "0.1.0"\n')
    _write(root, "docs/releases/v0.1.0.md", "# v0.1.0\n")
    _item(root, "PL-K7QX", "Carried on a branch")
    _item(root, "PL-9Y42", "Edited but not claimed")
    _item(root, "PL-0CLS", "Closed on the base", status="done")
    _write(root, "src/one.py", "one = 1\n")
    _git(root, "add", "-A")
    _git(root, "commit", "--quiet", "-m", "PL-0001 Lay the store down (#1)")
    _git(root, "tag", "v0.1.0")

    # An item filed by a commit that also changed code, for `filed_with_work`.
    # On the default branch, because that is the history it walks.
    _item(root, "PL-F1LD", "Filed beside the work that found it")
    _write(root, "src/two.py", "two = 2\n")
    _git(root, "add", "-A")
    _git(root, "commit", "--quiet", "-m", "PL-F1LD Capture and work in one commit (#2)")
    _git(root, "update-ref", "refs/remotes/origin/main", "main")

    # A ref the base took half of, for `orphaned`: one item's blob is on the
    # base and the other is on no commit the base holds.
    _git(root, "checkout", "--quiet", "-b", "claude/pl-0rp1-partly")
    _item(root, "PL-0RP1", "Landed with the base")
    _write(root, "src/three.py", "three = 3\n")
    _git(root, "add", "-A")
    _git(root, "commit", "--quiet", "-m", "PL-0RP1 The commit the base took whole")
    _item(root, "PL-0RP2", "Left behind on the branch")
    _git(root, "add", "-A")
    _git(root, "commit", "--quiet", "-m", "PL-0RP2 The commit pushed after the merge")
    _git(root, "update-ref", "refs/remotes/origin/claude/pl-0rp1-partly", "HEAD")
    # The squash: the base takes the first commit's every blob and none of the
    # second's, which is what `_commits_by_landing` reads as work left behind.
    _git(root, "checkout", "--quiet", "main")
    _item(root, "PL-0RP1", "Landed with the base")
    _write(root, "src/three.py", "three = 3\n")
    _git(root, "add", "-A")
    _git(root, "commit", "--quiet", "-m", "PL-0RP1 Land the first commit (#3)")
    _git(root, "update-ref", "refs/remotes/origin/main", "main")

    # The branch this checkout is on: it claims an item, files one beside work
    # outside the queue (`filed_with_work`), drops one it had captured (`lost`),
    # closes one (`closed_by`), edits one the base closed (`records_on_base`)
    # and cuts a release (`cut_window`, `cuts_in_flight`).
    _git(root, "checkout", "--quiet", "-b", "claude/pl-k7qx-carried")
    _write(root, "src/one.py", "one = 2\n")
    _git(root, "commit", "--quiet", "-am", "PL-K7QX Start the work")

    _item(root, "PL-L0ST", "Captured here and nowhere else")
    _git(root, "add", "-A")
    _git(root, "commit", "--quiet", "-m", "PL-L0ST Capture a finding")
    (root / "docs/items/PL-L0ST-fixture.md").unlink()
    _git(root, "commit", "--quiet", "-am", "PL-L0ST Drop it in a resolution")

    _item(root, "PL-K7QX", "Carried on a branch", status="done")
    _write(
        root,
        "docs/items/PL-0CLS-fixture.md",
        (root / "docs/items/PL-0CLS-fixture.md").read_text() + "\nA line the branch added.\n",
    )
    _write(root, "pyproject.toml", 'version = "0.2.0"\n')
    _write(root, "docs/releases/v0.2.0.md", "# v0.2.0\n")
    _write(root, "src/one.py", "one = 3\n")
    _git(root, "add", "-A")
    _git(root, "commit", "--quiet", "-m", "PL-K7QX Carry the work")
    _git(root, "update-ref", "refs/remotes/origin/claude/pl-k7qx-carried", "HEAD")

    # A branch that only annotates the queue: the weaker `editing` mark, and the
    # one `_superseded` decides the fate of.
    _git(root, "checkout", "--quiet", "main")
    _git(root, "checkout", "--quiet", "-b", "claude/triage-pass-abc123")
    _write(
        root,
        "docs/items/PL-9Y42-fixture.md",
        (root / "docs/items/PL-9Y42-fixture.md").read_text() + "\nA note a triage pass added.\n",
    )
    _git(root, "commit", "--quiet", "-am", "PL-9Y42 Triage the item")
    _git(root, "update-ref", "refs/remotes/origin/claude/triage-pass-abc123", "HEAD")

    # An item that exists on a branch and in no store, for `stranded`.
    _git(root, "checkout", "--quiet", "main")
    _git(root, "checkout", "--quiet", "-b", "claude/capture-only-def456")
    _item(root, "PL-0STR", "Only on a branch", status="untriaged")
    _git(root, "add", "-A")
    _git(root, "commit", "--quiet", "-m", "PL-0STR Capture a finding")
    _git(root, "update-ref", "refs/remotes/origin/claude/capture-only-def456", "HEAD")

    # What merged while the cut above sat unmerged: the window `cut_window` is
    # named for, and empty without a commit landing after the notes were written.
    _git(root, "checkout", "--quiet", "main")
    _item(root, "PL-L8TR", "Landed while the cut was open")
    _write(root, "src/five.py", "five = 5\n")
    _git(root, "add", "-A")
    _git(root, "commit", "--quiet", "-m", "PL-L8TR Land while the cut is open (#4)")
    _git(root, "update-ref", "refs/remotes/origin/main", "main")

    _git(root, "checkout", "--quiet", "claude/pl-k7qx-carried")
    return root


def _declined(answer: Any) -> bool:
    """Whether the read said what it could not read, in whichever way it has.

    Four shapes across the module: a `declined` reason, a `known` flag, `None`
    itself for the two reads answering with a bare optional, and - for
    `default_base`, whose answer is a ref name with nowhere to put a reason - a
    string carrying the mark `resolved` reads (`PL-73P0`).
    """
    if answer is None:
        return True
    if getattr(answer, "declined", ""):
        return True
    if isinstance(answer, str) and not resolved(answer):
        return True
    return hasattr(answer, "known") and not answer.known


@dataclass(frozen=True)
class Read:
    """One public read, how to call it, and what counts as a finding it made."""

    name: str
    call: Callable[[Path, Runner], Any]
    found: Callable[[Any], frozenset[Any]]


def _findings(*names: str) -> Callable[[Any], frozenset[Any]]:
    """What a report found, as a set, over the fields that carry findings.

    A set rather than a count, because a count passes a silence that swapped one
    finding for another. A bare collection is its own set of findings, and a
    read answering with one value is a set of one - so "nothing was lost" reads
    as "the value did not change" there, which is the same demand.
    """

    def found(answer: Any) -> frozenset[Any]:
        if answer is None:
            return frozenset()
        if isinstance(answer, frozenset | set | tuple | list):
            return frozenset(answer)
        if not names:
            return frozenset({answer})
        return frozenset(
            (name, entry) for name in names for entry in (getattr(answer, name, ()) or ())
        )

    return found


READS: tuple[Read, ...] = (
    Read(
        "branches_in_flight",
        lambda r, g: branches_in_flight(r, runner=g),
        _findings("branches", "editing", "unattributed", "unreadable"),
    ),
    Read(
        "precedence",
        lambda r, g: precedence(r, "PL-K7QX", runner=g),
        _findings("carriers", "unreadable"),
    ),
    Read(
        "branch_state",
        lambda r, g: branch_state(r, runner=g),
        lambda a: frozenset({(a.branch, a.base, a.behind, a.ahead, a.disposition)}),
    ),
    Read(
        # The forge half is a callable the caller supplies, so it is answered
        # here rather than reached: what is under test is the git half and the
        # propagation of a silence through it. The fixture's own branch closes
        # `PL-K7QX` in its copy, which is exactly the shape this reads.
        "settled_branches",
        lambda r, g: settled_branches(r, branches_in_flight(r, runner=g), opened=tuple, runner=g),
        _findings("branches"),
    ),
    Read(
        # The forge answers for the fixture's own branch, so there is a row to
        # lose: what a silence can take is the match between a ref and the
        # branch name a pull request carries.
        "open_pull_requests",
        lambda r, g: open_pull_requests(
            r,
            branches_in_flight(r, runner=g),
            opened=lambda: {"claude/pl-k7qx-carried": 757},
            runner=g,
        ),
        _findings("numbers"),
    ),
    Read("stranded", lambda r, g: stranded(r, set(), runner=g), _findings("items")),
    Read("lost", lambda r, g: lost(r, runner=g), _findings("items")),
    Read("orphaned", lambda r, g: orphaned(r, runner=g), _findings("branches")),
    # The first commit on `orphaned`'s branch, whose change the base took as
    # `(#3)`: its finding is that landing, which a silence must not move to a
    # later candidate or drop without the answer saying so (`PL-GHHW`).
    Read(
        "change_landed",
        lambda r, g: change_landed("claude/pl-0rp1-partly~1", "origin/main", r, runner=g),
        _findings(),
    ),
    Read(
        "merged_pull_requests", lambda r, g: merged_pull_requests(r, runner=g), _findings("numbers")
    ),
    Read("closed_by", lambda r, g: closed_by("HEAD", r, runner=g), _findings("closed")),
    Read(
        "closures_on_base",
        lambda r, g: closures_on_base(r, {"PL-0CLS": "PL-0CLS-fixture.md"}, runner=g),
        _findings("landed", "derived"),
    ),
    Read(
        "records_on_base",
        lambda r, g: records_on_base(r, {"PL-0CLS": "PL-0CLS-fixture.md"}, runner=g),
        _findings("records"),
    ),
    Read(
        # The branch gives `PL-K7QX` a command its base copy lacks, which is the
        # write this reads; which items are open is the caller's to say.
        "commands_written_here",
        lambda r, g: commands_written_here(r, {"PL-K7QX": "uv run pytest"}, runner=g),
        _findings("identifiers"),
    ),
    Read(
        "filed_with_work",
        lambda r, g: filed_with_work(frozenset({"PL-F1LD"}), r, runner=g),
        _findings("filings"),
    ),
    Read(
        "cut_window",
        lambda r, g: cut_window(r, runner=g),
        lambda a: frozenset({a.version}) | frozenset(a.landed),
    ),
    Read(
        "cuts_in_flight",
        lambda r, g: cuts_in_flight(r, notes_dir="docs/releases", runner=g),
        _findings("branches", "unreadable"),
    ),
    Read(
        "files_in_flight",
        lambda r, g: files_in_flight(r, branches_in_flight(r, runner=g), runner=g),
        _findings("branches", "unreadable"),
    ),
    Read("working_paths", lambda r, g: working_paths(r, runner=g), _findings("paths")),
    Read(
        "ref_walk",
        lambda r, g: ref_walk(r, "docs/items", runner=g),
        lambda a: frozenset({(a.listed, a.merged, a.unmerged, a.commits, a.item_edits)}),
    ),
    Read(
        "released_on_base",
        lambda r, g: released_on_base(
            r, version_file="pyproject.toml", notes_dir="docs/releases", runner=g
        ),
        lambda a: frozenset({a.version}) | a.notes,
    ),
    Read("churn", lambda r, g: churn(r, runner=g), lambda a: frozenset(a.by_day)),
    # `None` is how these two decline, and they reach it under every silence.
    Read("is_shallow", lambda r, g: is_shallow(r, runner=g), _findings()),
    Read("behind_remote", lambda r, g: behind_remote(r, "main", runner=g), _findings()),
    Read("tags", lambda r, g: tags(r, runner=g), _findings("names")),
    Read(
        "changed_items",
        lambda r, g: changed_items(r, "origin/main", runner=g),
        _findings("identifiers"),
    ),
    # Its finding is the ref itself, and a guessed one is no finding: `_declined`
    # reads the mark, so a silence that stops every candidate resolving declines
    # here rather than answering `main` (`PL-73P0`).
    Read("default_base", lambda r, g: default_base(r, runner=g), _findings()),
    # A file the fixture changes and a directory it adds to, from a date every
    # fixture commit is after, so the truthful read counts something to lose.
    Read(
        "since_filed",
        lambda r, g: since_filed(r, ("src/one.py", "docs/items"), date(2000, 1, 1), runner=g),
        _findings("paths"),
    ),
)


class _Recording:
    """A truthful runner that remembers every answer it gave.

    The sweep runs each read once per git call it makes, and a read puts tens of
    them, so replaying from what the first pass recorded is the difference
    between a second and a minute. A call the cache has never seen - a silence
    can send a read down a path the truthful run never took - falls through to
    real git rather than being invented.
    """

    def __init__(self) -> None:
        self.answers: dict[tuple[str, ...], str] = {}
        self.order: list[tuple[str, ...]] = []

    def __call__(self, args: list[str], root: Path) -> str:
        argv = tuple(args)
        self.order.append(argv)
        if argv not in self.answers:
            self.answers[argv] = _run_git(args, root)
        return self.answers[argv]


def _silencing(recorded: _Recording, nth: int) -> Runner:
    """The recorded answers, except the `nth` call, which git does not answer."""
    seen = 0

    def run(args: list[str], root: Path) -> str:
        nonlocal seen
        seen += 1
        if seen == nth:
            return SILENT
        argv = tuple(args)
        if argv in recorded.answers:
            return recorded.answers[argv]
        return _run_git(args, root)

    return run


def _lost_to_a_silence(read: Read, repo: Path) -> list[tuple[int, frozenset[Any]]]:
    """Every silenced call after which the read lost a finding and said nothing."""
    recorded = _Recording()
    whole = read.call(repo, recorded)
    assert not _declined(whole), f"{read.name} declined against a working git"
    expected = read.found(whole)
    # A read that found nothing against a working git can lose nothing, so it
    # would pass this sweep whatever it does with a silence. That is the shape
    # of check `CLAUDE.md` retires rather than keeps, so the fixture owes every
    # read something to find and the omission fails here instead of passing.
    assert expected, f"the fixture gives {read.name} nothing to find, so the sweep proves nothing"

    lost = []
    for nth in range(1, len(recorded.order) + 1):
        answer = read.call(repo, _silencing(recorded, nth))
        if _declined(answer):
            continue
        if missing := expected - read.found(answer):
            lost.append((nth, missing, " ".join(recorded.order[nth - 1])))
    return lost


@pytest.mark.parametrize("read", READS, ids=lambda read: read.name)
def test_one_silenced_git_call_never_leaves_a_read_looking_clean(read: Read, repo: Path) -> None:
    """Silence any one call and the read declines, or reports what it did before.

    The two honest answers. What is refused is the third: a finding the truthful
    read made and this one did not, with nothing saying anything went unread -
    which is a session being told an item is startable because a `git diff`
    failed. Findings are compared as sets, so a silence that swaps one for
    another is caught too, and a read answering with a single value is a set of
    one - for which "nothing was lost" means the value did not change.

    Reporting *more* than the truthful read passes. Over-reporting is the safe
    direction all through this module: an item wrongly marked in flight costs a
    session one look, and one wrongly unmarked costs two sessions a merge.
    """
    lost = _lost_to_a_silence(read, repo)

    assert not lost, "\n".join(
        f"{read.name} lost {sorted(map(str, missing))} when git did not answer call "
        f"{nth} (`git {argv}`) and said nothing about it"
        for nth, missing, argv in lost
    )


@pytest.fixture
def nowhere(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A directory in no repository, wherever the temporary directory sits.

    `GIT_CEILING_DIRECTORIES` stops git's search at the directory's parent, so a
    `TMPDIR` inside a checkout cannot lend it one.
    """
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path))
    path = tmp_path / "no-repository"
    path.mkdir()
    return path


@pytest.mark.parametrize("read", READS, ids=lambda read: read.name)
def test_every_read_declines_from_a_directory_in_no_repository(read: Read, nowhere: Path) -> None:
    """With no repository there is nothing to report on, so every read declines.

    The environment the sweep above cannot reach. It silences one call at a
    time inside a repository, so a read whose every call git answers outside one
    passes it. `changed_items` was that read: its two `git diff` calls exit 1
    there, and it said the branch changed no item where `tags` declined
    (`PL-19T3`).
    """
    assert _declined(read.call(nowhere, _run_git))


def test_the_sweep_covers_every_public_read_that_takes_a_runner() -> None:
    """A read added later is covered, or the omission fails here rather than silently.

    The standing cost this sweep is worth paying for. `_superseded`'s defect
    survived because nothing made a new read answer the question, and a registry
    nobody is obliged to extend would leave the next one in the same place.
    """
    import inspect

    from docket import vcs

    public = {
        name
        for name, obj in vars(vcs).items()
        if not name.startswith("_")
        and inspect.isfunction(obj)
        and obj.__module__ == vcs.__name__
        and "runner" in inspect.signature(obj).parameters
    }
    # `fetch_remote` is the one write in the module: it reads nothing and
    # answers nothing, so it has no answer to get wrong.
    assert public - {"fetch_remote"} == {read.name for read in READS}


# --- what `_run_git` reads git's exit codes as -----------------------------
#
# Half of the channel is the classification: exit 1 is git saying no, exit 128
# is git not saying anything, `<rev>:<path>` is the one shape where the fatal
# exit is an answer, and `diff` the one read whose exit 1 is not. Driven
# against real git rather than asserted from the table in the docstring, because
# a table is what `_superseded` already had.


def test_a_ref_that_does_not_resolve_is_git_answering_no(repo: Path) -> None:
    """`rev-parse --verify --quiet` exits 1 for a ref that is not there.

    The probe `default_base` and four other reads are built on, and the reason
    the rule is not "any non-zero exit". Classified as a failure it would fire
    on every checkout without an `origin/main`, which is the advisory nobody
    reads that `CLAUDE.md` retires rather than keeps.
    """
    answer = _run_git(["rev-parse", "--verify", "--quiet", "refs/heads/nope"], repo)

    assert answer == ""
    assert answered(answer)


def test_a_ref_that_vanished_mid_read_is_git_not_answering(repo: Path) -> None:
    """The trigger `PL-BHVM` named: a branch deleted while the digest runs.

    `_run_git`'s ten-second timeout is not the reachable cause - the real
    `diff --numstat` calls run in about 4.5 ms - and this is: another session's
    branch deleted, or a merged one cleaned up, between the `for-each-ref` that
    listed it and the `diff` that reads it. Git answers `fatal: bad revision`.
    """
    answer = _run_git(
        ["diff", "--numstat", "origin/main", "refs/heads/deleted", "--", "docs/items"], repo
    )

    assert answer == ""
    assert not answered(answer)


def test_a_path_a_revision_does_not_hold_is_git_answering_absent(repo: Path) -> None:
    """`show <rev>:<path>` exits 128 for an absent path, and that is an answer.

    The one exception, and it is not a preference: `cat-file --batch`, which
    `GitRunner` serves the same question from, prints `missing` and exits 0 for
    exactly this case - so classifying the fatal exit as a failure would make
    the two serving paths disagree about one question.
    """
    answer = _run_git(["show", "origin/main:docs/items/PL-XXXX-nope.md"], repo)

    assert answer == ""
    assert answered(answer)


def test_a_diff_outside_a_repository_is_git_not_answering(nowhere: Path) -> None:
    """`diff` exits 1 outside a repository, and that 1 is not git saying no.

    There git compares two paths on the filesystem instead, a form that implies
    `--exit-code`, so the 1 here is `error: Could not access
    'origin/main...HEAD'`. Read as an answer, it is a branch that changed no
    item (`PL-19T3`).
    """
    answer = _run_git(["diff", "--name-only", "origin/main...HEAD", "--", "docs/items"], nowhere)

    assert answer == ""
    assert not answered(answer)


def test_a_silence_survives_the_memo_rather_than_being_served_as_an_answer(repo: Path) -> None:
    """A second caller meets a silence as a silence, whatever the memo did.

    The memo no longer stores one at all - `PL-MM7F` settled that, and
    `test_git_runner.py` pins the retry and the count behind it. This holds the
    property that outlives either decision: whether the second caller is served
    from the memo or from a fresh subprocess, what reaches it must still be
    marked as the thing git never gave. Kept as a read from the top, because a
    `GitSilence` that lost its mark anywhere on the way through would satisfy
    every test on the storing rule and still tell this module's readers that
    git had answered.
    """
    argv = ["diff", "--numstat", "origin/main", "refs/heads/deleted", "--", "docs/items"]
    with GitRunner() as runner:
        first = runner(argv, repo)
        second = runner(argv, repo)

    assert not answered(first)
    assert not answered(second)
