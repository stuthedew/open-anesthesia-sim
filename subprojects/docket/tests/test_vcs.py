"""Tests for deriving in-flight work from the branches a checkout holds.

Git is injected rather than invoked, so these run without a repository and
assert the filtering rather than the plumbing. That the commands are spelled
in a way git accepts is proved against a real checkout in `test_cli.py`.
"""

from __future__ import annotations

import hashlib
import subprocess
from collections.abc import Mapping
from datetime import UTC, date, datetime, timedelta, timezone
from pathlib import Path

import pytest

from docket.checks import Report
from docket.vcs import (
    _PATHSPEC_BYTES,
    REWRITTEN,
    SILENT,
    BaseRelease,
    Branch,
    BranchCut,
    BranchState,
    FlightFiles,
    FlightReport,
    OpenPullRequests,
    OrphanedBranch,
    OrphanedReport,
    RewriteReport,
    Runner,
    SettledBranch,
    SettledReport,
    StrandedItem,
    StrandedReport,
    _pathspec_chunks,
    _run_git,
    _standing,
    _superseded,
    behind_remote,
    branch_state,
    branches_in_flight,
    change_landed,
    changed_items,
    closed_by,
    closures_on_base,
    cut_window,
    cuts_in_flight,
    default_base,
    filed_with_work,
    files_in_flight,
    lost,
    merged_pull_requests,
    open_pull_requests,
    orphaned,
    records_on_base,
    released_on_base,
    resolved,
    since_filed,
    stranded,
    tags,
)

ROOT = Path("/nowhere")
BASE = "origin/main"


def _tree_lines(entries: Mapping[str, str]) -> str:
    """`git ls-tree -r` output for a fake tree, as `path -> the text it holds`.

    `_item_blobs` reads the object id out of the listing so that two copies of
    one item can be told apart without opening either, which is what keeps
    `stranded` to a handful of `git show` calls. That id is content-addressed
    in git, so it is content-addressed here: two paths holding the same bytes
    get the same id and a path whose text changes gets a different one. A fake
    that has only paths to give passes the path as its own text, which is
    sound for every read that never compares two of them.
    """
    return "".join(
        f"100644 blob {hashlib.sha1(text.encode()).hexdigest()}\t{path}\n"
        for path, text in entries.items()
    )


def _when(day: str) -> str:
    """A commit date in the shape `%cI` writes, from the day a test names.

    Tests that only care which day a branch last moved on say `2026-08-20`;
    tests that care which of two branches moved *first* say the whole
    timestamp. Both reach git's format from here, so neither has to spell it.
    """
    return day if "T" in day else f"{day}T00:00:00+00:00"


#: The day a `took` entry carries where the test does not name one: later than
#: any commit these tests date. That is the shape a merge leaves behind - the
#: branch's own commits are what it took, so every one of them precedes it - and
#: it is what keeps a test about the other two facts from having to date this
#: one (`PL-8JQQ`).
TAKEN_ON = "2099-01-01"


def _taken_entry(entry: str | tuple[str, str]) -> tuple[str, str]:
    """A `took` entry as an id and the day the base took it."""
    return entry if isinstance(entry, tuple) else (entry, TAKEN_ON)


def _blob(entry: str | tuple[str, str]) -> str:
    """The blob an `adds` entry names, whether or not it also names a path."""
    return entry[0] if isinstance(entry, tuple) else entry


def _path(entry: str | tuple[str, str]) -> str:
    """The path an `adds` entry names, or one derived from its blob.

    Most tests care only whether a blob landed, so they pass the blob alone and
    the path is noise; the ones about `orphaned` report paths to a reader and
    have to name them.
    """
    return entry[1] if isinstance(entry, tuple) else f"some/{entry}"


def _runner(
    refs: list[str],
    merged: list[str] | None = None,
    commits: dict[str, list[tuple[str, ...]]] | None = None,
    unrelated: tuple[str, ...] = (),
    adds: dict[str, list[str] | list[tuple[str, str]]] | None = None,
    on_base: set[str] | None = None,
    touched: dict[str, list[tuple[str, tuple[str, ...]]]] | None = None,
    log: list[list[str]] | None = None,
    ran_out: tuple[str, ...] = (),
    head: str = "",
    tips: dict[str, dict[str, tuple[str, str]]] | None = None,
    duplicated: tuple[str, ...] = (),
    closed: tuple[str, ...] = (),
    base_items: dict[str, str] | None = None,
    took: tuple[str | tuple[str, str], ...] = (),
    same_as_base: tuple[str | tuple[str, str], ...] = (),
    statuses: dict[str, str] | None = None,
    created: tuple[str | tuple[str, str], ...] = (),
    tip_statuses: dict[str, dict[str, str]] | None = None,
):
    """A git that holds `refs`, with `commits` mapping a ref to (day, subject).

    A commit may carry a third field, its hash, for the tests that turn on two
    refs holding one commit - a local branch and its own tracking ref - which
    is what tells one piece of work from two. Left out, each ref's commits get
    hashes of their own.

    **Fields after the hash are the paths that commit changed**, which is what
    tells a commit implementing an item from one merely recording it. Left out,
    a commit changes `src/changed.py` - work, which is what every test written
    before that reading meant by a commit. A commit naming *no* paths is a
    merge, which git writes exactly that way under `--name-only`.

    `head` is the branch this checkout has checked out, which is how
    `precedence` tells the reader's own claim from somebody else's.

    `unrelated` names the refs whose merge-base with the default branch does
    not resolve - a truncated clone's missing history, which git answers with
    a failure rather than an empty result.

    `ran_out` names the refs whose walk ends at a commit with no parents in
    this checkout, which is what a walk that ran off the end of a truncated
    history looks like: every other commit reports a parent, so a walk the
    default branch stopped is told from one the history did.

    `tips` maps a ref to the two-dot diff between the default branch's tip and
    its own, per path, as `(added, deleted)` counts - which is what says whether
    a path `adds` reports as never landed is one the base is still missing.
    Left out, every such path differs by an addition, which is what a branch
    genuinely carrying work looks like and what every test written before that
    reading meant.

    `duplicated` names the refs whose divergence from the default branch is one
    rewritten history: the same commits twice over, which content comparison
    cannot tell from a merge.

    `closed` names the items the default branch's own copy records as closed,
    which is what tells an item that shipped from one a live session is closing
    on its own branch. `base_items` maps an id to the `touches` its copy on the
    base declares, for the reading that promotes an edit to a claim when the
    item's whole deliverable is a queue write - an id absent from both is an
    item the base does not hold at all, which is what a capture looks like.

    `statuses` maps an id to the `status` its copy on the base carries, for
    the reading that promotes a design round on an item at `needs-decision`;
    an id named here is held by the base whether or not `base_items` also
    names it, and one left out is `done` if `closed` names it and `ready`
    otherwise. `created` names the ids whose file a ref's commit created
    rather than changed - the commit's parent has no copy - which is what a
    capture looks like and a design round does not. An entry spelled
    `(commit, id)` rather than `id` pins that to one commit, which is what
    tells a stale capture on a bystander branch from a live round on the same
    item (`PL-61MD`).

    `tip_statuses` maps a ref to the `status` its own tip's copy of an item
    carries, for the reading that promotes a branch closing an item the base
    holds open (`PL-8FJK`). A ref or id left out answers with the base's copy,
    which is what every test written before that reading meant by a ref's copy.

    `took` names the ids the base's own commit subjects lead with since the
    fork point - each as the id alone, or as `(identifier, day)` for a test
    that turns on *when* the base took it, which is what tells a branch whose
    pull request finished it from one that has gone on committing under the
    same id (`PL-8JQQ`). `same_as_base` names the ids whose file the ref holds
    exactly as the base does. Together they are what says a ref's claim on an id is spent
    without the item having closed, which is what a triage pass merging leaves
    behind (`PL-LKFP`). A `same_as_base` entry spelled `(ref, id)` rather than
    `id` says only *that* ref's copy is the base's, which is what tells a spent
    claim on a bystander branch from a live one on the same id (`PL-2BZY`).

    `adds` maps a ref to the blobs it introduces since its fork point and
    `on_base` names the blobs the default branch has held at some point, which
    is what separates a branch whose work has landed from one still carrying
    it. `touched` maps a ref to its commits as (subject, paths), newest first,
    which is what `orphaned` reads to tell a commit the merge took from one
    nothing took. `log`, when passed, collects every command for a test that asserts
    which question was asked rather than what the answer was.
    """

    # An entry naming a ref pins the agreement to that ref; the base is the
    # other end of every such comparison, so it answers the shared oid too.
    same_pairs = {entry for entry in same_as_base if isinstance(entry, tuple)}
    same_ids = {entry for entry in same_as_base if isinstance(entry, str)}
    paired_ids = {identifier for _, identifier in same_pairs}
    # The same spelling for the parent read: an entry naming a commit answers
    # for that commit alone, so two refs' rounds on one id can differ.
    created_pairs = {entry for entry in created if isinstance(entry, tuple)}
    created_ids = {entry for entry in created if isinstance(entry, str)}

    def run(args: list[str], root: Path) -> str:
        if log is not None:
            log.append(args)
        if args[0] == "rev-parse":
            if ":" in args[-1]:
                # `git rev-parse <end>:<path>`, the blob oid of one side's copy
                # of an item file. An id in `same_as_base` answers the same oid
                # for both ends; anything else answers a different one per end.
                end, _, path = args[-1].partition(":")
                identifier = "-".join(path.rsplit("/", 1)[-1].split("-")[:2])
                if end.endswith("^"):
                    # `<commit>^:<path>`, whether the commit inherited the
                    # file: a created one has no copy there to name.
                    if identifier in created_ids or (end[:-1], identifier) in created_pairs:
                        return ""
                    return f"blob-{identifier}-parent\n"
                if identifier in same_ids or (end, identifier) in same_pairs:
                    return f"blob-{identifier}\n"
                if end == BASE and identifier in paired_ids:
                    return f"blob-{identifier}\n"
                return f"blob-{identifier}-{end}\n"
            if args[-1] == "HEAD":
                return f"{head}\n" if head else ""
            return f"{BASE}\n" if args[-1] == BASE else ""
        if args[0] == "for-each-ref":
            if any(arg.startswith("--merged=") for arg in args):
                return "\n".join(merged or [])
            return "\n".join(refs)
        if args[0] == "merge-base":
            if args[-1] == "HEAD":
                # `precedence` asks whether this checkout holds the commit that
                # staked a claim; the checkout holds whatever its own branch
                # committed. git answers by printing the merge base, so a
                # commit HEAD carries is echoed back and anything else is not.
                held = {
                    entry[2] if len(entry) > 2 else f"{head}@{position}"
                    for position, entry in enumerate((commits or {}).get(head, []))
                }
                return f"{args[-2]}\n" if args[-2] in held else "0123456789abcdef\n"
            return "" if args[-1] in unrelated else "0123456789abcdef\n"
        if args[0] == "rev-list" and "--objects" in args:
            # The object walk the landing split reads, in the shape git writes
            # it: one oid per line, a path after it for anything but a commit.
            return "\n".join(f"{blob} some/path/{blob}" for blob in sorted(on_base or set()))
        if args[0] == "ls-tree":
            # The tree listing that maps an item id to its file name on the
            # base. The store names each file for its item, which is what
            # `filename_for` guarantees and what this relies on.
            prefix = args[-1].rstrip("/")
            held = [*closed, *(base_items or {}), *same_ids, *paired_ids, *(statuses or {})]
            return _tree_lines(
                {f"{prefix}/{identifier}-shipped.md": identifier for identifier in held}
            )
        if args[0] == "show":
            # `git show <base>:<path>`, which is how the closure is read off the
            # base rather than off this checkout.
            revision, _, wanted = args[-1].partition(":")
            # The id is the first two dash-separated pieces of the basename
            # (`PL-GVXP-shipped.md`), not the first one.
            identifier = "-".join(wanted.rsplit("/", 1)[-1].split("-")[:2])
            tip = (tip_statuses or {}).get(revision, {})
            if identifier in tip:
                # `git show <ref>:<path>`, the branch's own copy, which is what
                # a closure is read from rather than the commit that made it.
                return (
                    f"---\nid: {identifier}\ntitle: groomed\nstatus: {tip[identifier]}\n"
                    "---\n\nOn the branch.\n"
                )
            declared = (base_items or {}).get(identifier)
            status = (statuses or {}).get(identifier, "done" if identifier in closed else "ready")
            if declared is not None or identifier in (statuses or {}):
                touches = "" if declared is None else f"touches: {declared}\n"
                return (
                    f"---\nid: {identifier}\ntitle: shipped\nstatus: {status}\n"
                    f"{touches}---\n\nOn the base.\n"
                )
            if identifier not in closed:
                return ""
            return f"---\nid: {identifier}\ntitle: shipped\nstatus: done\n---\n\nDone.\n"
        if args[0] == "diff" and "--numstat" in args:
            # The tip comparison: `diff --numstat --no-renames <base> <ref> --`
            # then the paths asked about. A path git does not name is one the
            # two tips agree on, so the fake omits it rather than reporting zeros.
            asked = args[args.index("--") + 1 :]
            per_path = (tips or {}).get(args[4])
            rows = []
            for path in asked:
                if per_path is None:
                    rows.append(f"1\t0\t{path}")
                    continue
                counts = per_path.get(path)
                if counts is not None:
                    rows.append(f"{counts[0]}\t{counts[1]}\t{path}")
            return "\n".join(rows)
        if args[0] == "diff":
            return "\n".join(
                f":000000 100644 {'0' * 40} {_blob(entry)} A\t{_path(entry)}"
                for entry in (adds or {}).get(args[-2], [])
            )
        if args[0] == "log":
            if "--format=%cI%x1f%s" in args:
                # The base's own subjects since a ref's fork point, dated,
                # which is what says the base has already taken work under an
                # id - and when it last did, which is what a ref that went on
                # committing under the id is judged against (`PL-8JQQ`).
                return "\n".join(
                    f"{_when(day)}\x1f{identifier}: taken on the base"
                    for identifier, day in (_taken_entry(entry) for entry in took)
                )
            if "--left-right" in args:
                # The rewrite fingerprint: the same author date and subject on
                # both sides of the divergence, which is what a rewrite leaves
                # and what forking and committing cannot produce. `--reverse`
                # puts the oldest first, and that is the commit the rule reads.
                walked = args[-2].split("...")[-1]
                if walked not in duplicated:
                    return ""
                # `%x00` between the fields, spelled explicitly: a `\0` written
                # against a digit is read as an octal escape, which is how the
                # author date `100` first reached this as a backspace.
                kept = ("1750000000", "p1", "a commit the rewrite kept")
                return "\n".join(
                    "\x00".join((side, short, *kept))
                    for side, short in (("<", "aaaaaaa"), (">", "bbbbbbb"))
                )
            if "--name-only" in args and "--source" not in args:
                # `orphaned` decides on this walk - a commit *none* of whose
                # paths reached the base - so the fake has to answer it. The
                # record shape is git's: \x1e opens each, then the hash, \x1f,
                # the subject, then one path per line. `--source` is what tells
                # it from the flight walk below, which reads paths too.
                walked = args[-2]
                return "".join(
                    "\x1e{}\x1f{}\n{}\n".format(f"{walked}@{position}", subject, "\n".join(paths))
                    for position, (subject, paths) in enumerate((touched or {}).get(walked, []))
                )
            wanted = [arg for arg in args if arg.startswith("--find-object=")]
            if wanted:
                held = wanted[0].split("=", 1)[1] in (on_base or set())
                return "fedcba9876543210\n" if held else ""
            walked = [arg for arg in args[1:] if not arg.startswith(("-", "^"))]
            lines = []
            for ref in walked:
                entries = (commits or {}).get(ref, [])
                for position, entry in enumerate(entries):
                    day, subject = entry[0], entry[1]
                    commit = entry[2] if len(entry) > 2 else f"{ref}@{position}"
                    off_the_end = ref in ran_out and position == len(entries) - 1
                    parent = "" if off_the_end else "0f1e2d3"
                    lines.append(f"{ref}\x1f{_when(day)}\x1f{parent}\x1f{commit}\x1f{subject}")
                    # git writes the paths under the commit they belong to, and
                    # a blank line between the two, which is the shape the walk
                    # has to survive parsing.
                    # An entry that names its paths gets exactly those, so a
                    # single empty one says "none" - a merge, which is what
                    # git prints for one under `--name-only`.
                    named = tuple(path for path in entry[3:] if path)
                    paths = named if len(entry) > 3 else ("src/changed.py",)
                    if paths:
                        lines.append("")
                        lines.extend(paths)
            return "\n".join(lines)
        return ""

    return run


def _in_flight(
    refs: list[str],
    merged: list[str] | None = None,
    commits: dict[str, list[tuple[str, ...]]] | None = None,
    unrelated: tuple[str, ...] = (),
    adds: dict[str, list[str] | list[tuple[str, str]]] | None = None,
    on_base: set[str] | None = None,
    ran_out: tuple[str, ...] = (),
) -> tuple[Branch, ...]:
    return _report(refs, merged, commits, unrelated, adds, on_base, ran_out=ran_out).branches


def _report(
    refs: list[str],
    merged: list[str] | None = None,
    commits: dict[str, list[tuple[str, ...]]] | None = None,
    unrelated: tuple[str, ...] = (),
    adds: dict[str, list[str] | list[tuple[str, str]]] | None = None,
    on_base: set[str] | None = None,
    ran_out: tuple[str, ...] = (),
    tips: dict[str, dict[str, tuple[str, str]]] | None = None,
    closed: tuple[str, ...] = (),
    base_items: dict[str, str] | None = None,
    took: tuple[str | tuple[str, str], ...] = (),
    same_as_base: tuple[str | tuple[str, str], ...] = (),
    statuses: dict[str, str] | None = None,
    created: tuple[str | tuple[str, str], ...] = (),
    tip_statuses: dict[str, dict[str, str]] | None = None,
) -> FlightReport:
    """The whole report, for the tests reading the file edits beside the work.

    `_in_flight` returns the branches alone because that was the whole answer
    when it was written. `editing` is a second and weaker mark on the same
    report, and most of what is worth asserting about it is what it says
    *together* with the first - that an item is edited and not in flight, or in
    flight and not also listed as edited.
    """
    runner = _runner(
        refs,
        merged,
        commits,
        unrelated,
        adds,
        on_base,
        ran_out=ran_out,
        tips=tips,
        closed=closed,
        base_items=base_items,
        took=took,
        same_as_base=same_as_base,
        statuses=statuses,
        created=created,
        tip_statuses=tip_statuses,
    )
    return branches_in_flight(ROOT, runner=runner)


def test_a_branch_naming_an_item_is_in_flight() -> None:
    assert [b.item_id for b in _in_flight(["claude/pl-k7qx-do-the-thing"])] == ["PL-K7QX"]


def test_historical_numeric_ids_are_recognized() -> None:
    assert branches_in_flight(ROOT, runner=_runner(["claude/pl-013-something"])).ids == {"PL-013"}


def test_a_branch_naming_nothing_is_ignored() -> None:
    assert _in_flight(["main", "claude/some-idea-abcd"]) == ()


def test_a_merged_branch_is_not_in_flight() -> None:
    """Deleting a remote branch leaves its tracking ref until someone prunes."""
    refs = ["origin/claude/pl-040-done", "origin/claude/pl-k7qx-live"]
    found = _in_flight(refs, merged=["origin/claude/pl-040-done"])

    assert [b.item_id for b in found] == ["PL-K7QX"]


def test_a_merged_branch_carries_no_commits_into_the_answer() -> None:
    """The commit read must honour the same exclusion the name read does."""
    found = _in_flight(
        ["origin/claude/shipped-abcdef"],
        merged=["origin/claude/shipped-abcdef"],
        commits={"origin/claude/shipped-abcdef": [("2026-08-20", "PL-K7QX Do the thing")]},
    )

    assert found == ()


SQUASHED = "origin/claude/squash-merged-abcdef"


def test_a_squash_merged_branch_whose_ref_survives_is_not_in_flight() -> None:
    """The defect: a squash keeps the branch's content and none of its commits.

    So `--merged` calls the branch unmerged for as long as the ref exists, and
    a checkout that does not prune holds it indefinitely - reporting every id
    at the front of one of its subjects as work somebody is still doing.
    """
    found = _in_flight(
        [SQUASHED],
        commits={SQUASHED: [("2026-08-20", "PL-K7QX Do the thing")]},
        adds={SQUASHED: ["a1", "a2"]},
        on_base={"a1", "a2"},
    )

    assert found == ()


def test_a_squash_merged_branch_is_judged_against_the_history_not_the_tip() -> None:
    """A landed blob stays landed; a tip comparison would un-land it on the next edit.

    Every item this store captures is edited again by the triage pass that
    follows it, so a branch judged against the default branch's *tip* would be
    back to reporting in flight one merge after the one that finished it.

    The walk is over the base's *objects*, which is every blob its history has
    held, and it is asked once for all of them rather than once per blob -
    measured at 0.033 s against 0.62 s for the seventeen `--find-object` walks
    it replaced on this repository. What the assertion pins is that the
    comparison is against the history and never against the base's tree.
    """
    calls: list[list[str]] = []
    branches_in_flight(
        ROOT,
        runner=_runner(
            [SQUASHED],
            commits={SQUASHED: [("2026-08-20", "PL-K7QX Do the thing")]},
            adds={SQUASHED: ["a1"]},
            on_base={"a1"},
            log=calls,
        ),
    )

    assert ["rev-list", "--objects", BASE] in calls
    assert not [args for args in calls if args[0] == "diff" and BASE in args]


def test_a_branch_the_squash_test_cannot_answer_is_left_in_flight() -> None:
    """Silence is not evidence of landing, and the two errors are not equal.

    A ref that introduces no blob this checkout can read - no commits yet, only
    deletions, or history it does not hold - keeps its place in the report.
    Naming a merged branch is noise; hiding a live one hands its item to a
    second session.
    """
    found = _in_flight(
        [SQUASHED], commits={SQUASHED: [("2026-08-20", "PL-K7QX Do the thing")]}, on_base={"a1"}
    )

    assert [branch.item_id for branch in found] == ["PL-K7QX"]


def test_one_blob_the_base_has_never_held_is_not_a_squash_merge() -> None:
    """Part of a branch landing is not the branch landing: all of it must have."""
    found = _in_flight(
        [SQUASHED],
        commits={SQUASHED: [("2026-08-20", "PL-K7QX Do the thing")]},
        adds={SQUASHED: ["a1", "a2"]},
        on_base={"a1"},
    )

    assert [branch.item_id for branch in found] == ["PL-K7QX"]


def test_a_local_branch_and_its_tracking_ref_are_one_piece_of_work() -> None:
    refs = ["claude/pl-k7qx-live", "origin/claude/pl-k7qx-live"]

    assert len(_in_flight(refs)) == 1


def test_a_random_suffix_is_not_read_as_an_id() -> None:
    assert _in_flight(["claude/queue-redesign-wrqfwj"]) == ()


def test_no_git_declines_rather_than_reporting_no_branches() -> None:
    """A git that does not answer is not a repository with nothing in flight.

    This test used to assert `branches == ()` against a runner returning the
    empty string, which read as compliance and was not: the empty string is what
    a *failure* collapsed to as well, so the assertion held whether the read had
    declined or had quietly reported a clean checkout. It reported a clean
    checkout. `PL-Q9Z1` is the defect; `test_vcs_silence.py` is the sweep that
    holds every read in the module to this, one silenced call at a time.

    Silence and emptiness are driven separately here, because the whole of the
    fix is that they are no longer the same value.
    """
    silent = branches_in_flight(ROOT, runner=lambda args, root: SILENT)

    assert silent.branches == ()
    assert not silent.known
    assert "did not answer" in silent.declined

    # The other case, and still a clean answer: a git that ran, resolved a base,
    # and found nothing beyond it. It needs a base that resolves, which the
    # original form of this line did not give it. Answering `""` to every
    # candidate probe is a checkout with no default branch at all, and since
    # `PL-73P0` that declines on its own account - see the test below.
    empty = branches_in_flight(ROOT, runner=_refs({"origin/main": "abc123"}))

    assert empty.branches == ()
    assert empty.known


def test_a_flight_report_against_a_base_nobody_established_declines() -> None:
    """No default branch is not a checkout with nothing in flight (`PL-73P0`).

    The gap the sweep could not see, because it is not a silence: git runs, and
    answers `no` to all four candidates truthfully. `default_base` fell back to
    the literal `main`, every ref comparison was then taken against a branch
    that is not there, and the report came back clean - which a session reads as
    "nobody is working anything", the one answer that costs two sessions a merge.
    """
    report = branches_in_flight(ROOT, runner=lambda args, root: "")

    assert not report.known
    assert "no candidate default branch" in report.declined
    # The cause, not whichever call failed downstream of it. A reader sent after
    # a git failure that never happened goes looking in the wrong place.
    assert "did not answer" not in report.declined


def test_a_harness_named_branch_is_found_by_what_it_committed() -> None:
    """The case the mechanism exists for: the branch name carries no id at all.

    A session names its own branch `claude/pl-k7qx-slug`; the web harness names
    one from the opening prompt and it cannot be renamed afterwards. Reading
    names alone left every such branch invisible, so `docket next` would offer
    an item another session was already implementing.
    """
    refs = ["origin/claude/roadmap-release-write-failure-nhsjwo"]
    found = _in_flight(
        refs,
        commits={
            refs[0]: [
                ("2026-08-30", "PL-M5FK Hold the roadmap's tag claims to git tag"),
                ("2026-08-29", "PL-M5FK Read the release train from the version table"),
            ]
        },
    )

    assert [(b.item_id, b.name) for b in found] == [("PL-M5FK", refs[0])]


def test_an_id_mentioned_mid_subject_does_not_put_that_item_in_flight() -> None:
    """A capture names an item it is not implementing; the leading id is the work."""
    refs = ["origin/claude/some-other-work-abcdef"]
    found = _in_flight(
        refs,
        commits={
            refs[0]: [("2026-08-31", "Capture PL-D2GW, found while answering what to work on next")]
        },
    )

    assert found == ()


def test_a_subject_leading_with_two_ids_puts_both_in_flight() -> None:
    """One branch may carry two items, and both lead the subject."""
    refs = ["origin/claude/paired-work-abcdef"]
    found = _in_flight(
        refs,
        commits={refs[0]: [("2026-08-30", "PL-N7R9, PL-J295: the pull request stops being a")]},
    )

    assert [b.item_id for b in found] == ["PL-J295", "PL-N7R9"]


QUEUE_ONLY = "docs/items/PL-K7QX-do-the-thing.md"
HARNESS = "origin/claude/roadmap-release-write-failure-nhsjwo"


def test_a_commit_that_only_writes_to_the_queue_is_not_work() -> None:
    """The failure this reading exists for, in its commonest shape.

    `CLAUDE.md` requires a finding to be captured before a session ends and
    requires the leading id on every subject, so recording a note into an
    item's brief produces a subject indistinguishable from one implementing
    it. Read as work, the item left `docket next` for every session until the
    branch merged - and the branches producing most of these were abandoned,
    so they never merged (queue item PL-X3WZ).
    """
    found = _in_flight(
        [HARNESS],
        commits={HARNESS: [("2026-09-03", "PL-K7QX: record a scope note", "c1", QUEUE_ONLY)]},
    )

    assert found == ()


def test_an_item_whose_whole_deliverable_is_a_queue_edit_is_work_after_all() -> None:
    """The residual `_annotates_only` could not see, recovered (`PL-7790`).

    Some items *are* queue edits - the tag items, the triage items, the
    recovery items - and for those a diff that never leaves `docs/items/` is
    the work rather than a note about it. Observed live on 2026-09-14:
    `origin/claude/loving-ride-mo6njm` held one commit closing `PL-XR8K`, whose
    `touches` is `docs/items/`, and `flight` reported the branch not at all
    while a session was working it. The subject leads with the item it wrote,
    which the promotion asks for since `PL-3W3P`.
    """
    report = _report(
        [HARNESS],
        commits={HARNESS: [("2026-09-14", "PL-K7QX: close the tag item", "c1", QUEUE_ONLY)]},
        base_items={"PL-K7QX": "docs/items/"},
    )

    assert [branch.item_id for branch in report.branches] == ["PL-K7QX"]
    assert report.editing == (), "promoted to the stronger mark, never reported as both"


def test_an_annotated_item_whose_own_work_is_code_stays_out_of_flight() -> None:
    """The eight false marks, re-tested against the new reading.

    Not one of `PL-X3WZ`'s eight declares `touches` inside the queue alone, so
    reading the item rather than the commit leaves every one of them excluded.
    `PL-N5WZ` is one of the eight and this is its shape: a `docket record`
    write, leading with the id of an item whose work is in `cli.py`.
    """
    report = _report(
        [HARNESS],
        commits={HARNESS: [("2026-09-04", "PL-K7QX: record `pr: 265`", "c1", QUEUE_ONLY)]},
        base_items={"PL-K7QX": "subprojects/docket/src/docket/cli.py"},
    )

    assert report.branches == ()
    assert [edit.item_id for edit in report.editing] == ["PL-K7QX"]


def test_an_item_reaching_code_as_well_as_the_queue_is_not_promoted() -> None:
    """`PL-5WFS`'s shape, and one of the eight: `plan.py` beside `docs/items/`.

    "Entirely inside the queue" is the test, not "mentions the queue", or the
    reading would readmit every item that fixes a brief alongside its code.
    """
    report = _report(
        [HARNESS],
        commits={HARNESS: [("2026-09-04", "PL-K7QX: fill in touches", "c1", QUEUE_ONLY)]},
        base_items={"PL-K7QX": "subprojects/docket/src/docket/plan.py, docs/items/"},
    )

    assert report.branches == ()


def test_a_capture_creating_the_item_file_is_not_promoted() -> None:
    """What keeps a capture out, and it costs no extra rule.

    A capture creates the file, so the base holds no copy of it to declare
    anything - and an id the base cannot answer for is dropped rather than
    marked. This is the direction that matters: a capture is the commonest
    queue-only push this project makes.
    """
    report = _report(
        [HARNESS],
        commits={HARNESS: [("2026-09-04", "PL-K7QX: capture the finding", "c1", QUEUE_ONLY)]},
    )

    assert report.branches == ()


def test_a_write_onto_a_shipped_queue_only_item_does_not_resurrect_it() -> None:
    """`_closed_on_base` ran before these existed, so it is asked again.

    A `docket record` write onto a shipped tag item is exactly this shape, and
    naming a closed item under "do not start these again" is `PL-6BDX`.
    """
    report = _report(
        [HARNESS],
        commits={HARNESS: [("2026-09-14", "PL-K7QX: record `pr: 554`", "c1", QUEUE_ONLY)]},
        base_items={"PL-K7QX": "docs/items/"},
        closed=("PL-K7QX",),
    )

    assert report.branches == ()


def test_a_design_round_on_a_needs_decision_item_is_in_flight() -> None:
    """The other half of `_annotates_only`'s residual, recovered (`PL-VYSP`).

    A design round records its decision into the item it decides, so its
    whole output can be queue edits. Observed 2026-09-19: `PL-BHVM` had three
    commits pushed, every subject led by the id, a live session on the branch,
    and `bin/docket show` called it startable. The status on the base is what
    says this is the work rather than a note about it.
    """
    report = _report(
        [HARNESS],
        commits={HARNESS: [("2026-09-19", "PL-K7QX: record the design round", "c1", QUEUE_ONLY)]},
        statuses={"PL-K7QX": "needs-decision"},
    )

    assert [branch.item_id for branch in report.branches] == ["PL-K7QX"]
    assert report.editing == (), "promoted to the stronger mark, never reported as both"


def test_a_round_that_re_points_other_deciding_items_claims_only_its_own() -> None:
    """The conjunction, and why the promotion asks for the leading id.

    A design round re-points its cluster, so one commit writes a dozen other
    items' files - some at `needs-decision` themselves, and some being worked
    by other sessions. Only the item the subject leads with is claimed; the
    rest are file edits, which is what they are.
    """
    other = "docs/items/PL-9Z9Z-re-pointed.md"
    report = _report(
        [HARNESS],
        commits={
            HARNESS: [("2026-09-19", "PL-K7QX: re-point the cluster", "c1", QUEUE_ONLY, other)]
        },
        statuses={"PL-K7QX": "needs-decision", "PL-9Z9Z": "needs-decision"},
    )

    assert [branch.item_id for branch in report.branches] == ["PL-K7QX"]
    assert [edit.item_id for edit in report.editing] == ["PL-9Z9Z"]


def test_a_note_written_into_a_deciding_item_under_another_id_is_not_a_claim() -> None:
    """A capture that also annotates a `needs-decision` item is annotation.

    The subject leads with the captured item, not the one annotated, so the
    shape the promotion reads is absent - and the annotated item stays where
    `PL-N1JK` put it, as a file edit a second writer needs to know about.
    """
    captured = "docs/items/PL-9Z9Z-captured.md"
    subject = "PL-9Z9Z: capture it, and note it on PL-K7QX"
    report = _report(
        [HARNESS],
        commits={HARNESS: [("2026-09-19", subject, "c1", captured, QUEUE_ONLY)]},
        statuses={"PL-K7QX": "needs-decision"},
    )

    assert report.branches == ()
    assert "PL-K7QX" in {edit.item_id for edit in report.editing}


def test_the_same_commit_shape_on_any_other_open_status_is_annotation() -> None:
    """`PL-X3WZ`'s reading is intact everywhere the status is not `needs-decision`.

    A triage pass moves an item out of `untriaged` and a note lands on a
    `ready` one; both lead with the id and write its own file, and both are
    the false marks the path test exists to withhold. Measured over the 1,006
    commits on `origin/main` on 2026-09-19: of 235 queue-only commits changing
    the leading id's own file where the base held it, 120 were triage passes.
    """
    for status in ("untriaged", "ready", "blocked"):
        report = _report(
            [HARNESS],
            commits={HARNESS: [("2026-09-19", "PL-K7QX: triage it", "c1", QUEUE_ONLY)]},
            statuses={"PL-K7QX": status},
        )

        assert report.branches == (), status
        assert [edit.item_id for edit in report.editing] == ["PL-K7QX"], status


def test_a_design_round_the_base_already_holds_is_not_a_claim() -> None:
    """A round that merged leaves its ref behind, and the ref must not go on claiming.

    The base's copy is what the branch wrote, so the two-dot diff names
    nothing for the path; the same `_superseded` read that clears a merged
    file edit clears this, in the one call (`PL-8MJ3`).
    """
    report = _report(
        [HARNESS],
        commits={HARNESS: [("2026-09-19", "PL-K7QX: record the design round", "c1", QUEUE_ONLY)]},
        statuses={"PL-K7QX": "needs-decision"},
        tips={HARNESS: {}},
    )

    assert report.branches == ()
    assert report.editing == ()


def test_a_stale_capture_of_an_item_since_triaged_to_deciding_is_not_a_claim() -> None:
    """The false mark the status test alone produced, live, three times over.

    A capture merges by some other route, is triaged to `needs-decision` on
    the base, and its own branch lives on: eleven days later that branch still
    leads with the id and changes its own file, and the base holds the item at
    the status that promotes. The commit's parent is what tells it from a
    round - it created the file, and a round writes into one that exists.
    """
    report = _report(
        [HARNESS],
        commits={HARNESS: [("2026-09-08", "PL-K7QX: capture the finding", "c1", QUEUE_ONLY)]},
        statuses={"PL-K7QX": "needs-decision"},
        created=("PL-K7QX",),
    )

    assert report.branches == ()
    assert [edit.item_id for edit in report.editing] == ["PL-K7QX"]


def test_a_round_that_renames_the_item_file_still_claims_it() -> None:
    """A rename changes two paths; the one the commit inherited is the evidence."""
    renamed = "docs/items/PL-K7QX-three-items-not-eight.md"
    report = _report(
        [HARNESS],
        commits={HARNESS: [("2026-09-19", "PL-K7QX: narrow the head", "c1", QUEUE_ONLY, renamed)]},
        statuses={"PL-K7QX": "needs-decision"},
    )

    assert [branch.item_id for branch in report.branches] == ["PL-K7QX"]


def test_a_queue_only_item_s_file_edited_under_another_id_is_not_claimed() -> None:
    """The first promotion reads the subject-led shape the others do (`PL-3W3P`).

    `PL-0HPV`'s `verify:` reorder, led by `PL-0HPV`, rewrote 96 item files, and
    `flight` reported `PL-LBW5`, `PL-RWBV`, `PL-YVV4` and `PL-YZKK` in flight
    until its pull request merged: each declares `touches: docs/items` and no
    subject named any of them. The promotion was fed from every edit to an
    item's file; the edit is still a file edit, which is all it ever was.
    """
    subject = "PL-0HPV: reorder 96 verify: commands cheap-clause-first"
    report = _report(
        [HARNESS],
        commits={HARNESS: [("2026-09-22", subject, "c1", QUEUE_ONLY)]},
        base_items={"PL-K7QX": "docs/items/"},
    )

    assert report.branches == ()
    assert [edit.item_id for edit in report.editing] == ["PL-K7QX"]


GROOMING = "origin/claude/oldest-items-relevance-a0awgl"


def test_a_branch_closing_an_item_the_base_holds_open_is_in_flight() -> None:
    """The third shape of queue-only work, recovered (`PL-8FJK`).

    A grooming pass closes items it never claimed. `#914` dropped `PL-027`,
    `PL-043` and `PL-ZBR6` in queue-only commits leading with each id, and
    `docket next` went on offering all three - `docket next --oldest` hands the
    oldest items out first, and those are the ones such a pass targets. The
    branch's copy closed while the base's is open is what tells it from a note.
    """
    subject = "PL-9Z9Z, PL-K7QX: groom the ten oldest open items against the tree"
    report = _report(
        [GROOMING],
        commits={GROOMING: [("2026-09-22", subject, "c1", QUEUE_ONLY)]},
        statuses={"PL-K7QX": "ready"},
        tip_statuses={GROOMING: {"PL-K7QX": "dropped"}},
    )

    assert [(b.item_id, b.name) for b in report.branches] == [("PL-K7QX", GROOMING)]
    assert report.editing == (), "promoted to the stronger mark, never reported as both"


def test_a_closure_under_another_id_s_subject_stays_a_file_edit() -> None:
    """The limit the promotion states: the subject has to lead with the closed id.

    `CLAUDE.md` requires a closing commit to lead with every id it closes, so
    this is that rule not being kept - and reading a closure off any edit to
    the file instead is `PL-3W3P`'s false claim arriving by the other door.
    """
    report = _report(
        [GROOMING],
        commits={GROOMING: [("2026-09-22", "PL-9Z9Z: groom the oldest", "c1", QUEUE_ONLY)]},
        statuses={"PL-K7QX": "ready"},
        tip_statuses={GROOMING: {"PL-K7QX": "dropped"}},
    )

    assert report.branches == ()
    assert [edit.item_id for edit in report.editing] == ["PL-K7QX"]


def test_a_closure_the_base_already_holds_is_not_a_claim() -> None:
    """Once the pass merges, nothing is in flight however long its ref survives.

    After the squash the two tips agree and `_superseded` clears the edit
    before any promotion is asked. Where the base closed the item some other
    way and the two copies still differ, its own status answers: an item the
    base already records closed is not open to be closed.
    """
    commits = {GROOMING: [("2026-09-22", "PL-K7QX: drop it", "c1", QUEUE_ONLY)]}
    closing = {GROOMING: {"PL-K7QX": "dropped"}}
    squashed = _report(
        [GROOMING], commits=commits, closed=("PL-K7QX",), tip_statuses=closing, tips={GROOMING: {}}
    )
    elsewhere = _report([GROOMING], commits=commits, closed=("PL-K7QX",), tip_statuses=closing)

    assert squashed.branches == ()
    assert squashed.editing == ()
    assert elsewhere.branches == ()


def test_a_branch_that_closed_an_item_and_reopened_it_claims_nothing() -> None:
    """The tip is read rather than the commit, so a change of mind is not a claim.

    The reopening commit leads with another id, so the closing commit is still
    the newest one the promotion's shape records - and its own copy says
    `dropped`. Only the tip says what the branch would land.
    """
    reopen = "PL-9Z9Z: reopen PL-K7QX, whose premise holds after all"
    report = _report(
        [GROOMING],
        commits={
            GROOMING: [
                ("2026-09-22T11:00:00+00:00", reopen, "c2", QUEUE_ONLY),
                ("2026-09-22T10:00:00+00:00", "PL-K7QX: drop it", "c1", QUEUE_ONLY),
            ]
        },
        statuses={"PL-K7QX": "ready"},
        tip_statuses={GROOMING: {"PL-K7QX": "ready"}, "c1": {"PL-K7QX": "dropped"}},
    )

    assert report.branches == ()
    assert [edit.item_id for edit in report.editing] == ["PL-K7QX"]


def test_a_commit_reaching_past_the_queue_is_work() -> None:
    """A closure writes the item and the code in one commit, and is work."""
    found = _in_flight(
        [HARNESS],
        commits={
            HARNESS: [("2026-09-03", "PL-K7QX: do the thing", "c1", QUEUE_ONLY, "src/thing.py")]
        },
    )

    assert [branch.item_id for branch in found] == ["PL-K7QX"]


def test_one_recovery_commit_hides_none_of_the_items_it_names() -> None:
    """A batch subject hid a batch of items: four ids, one push, all startable.

    `bin/docket stranded`'s own workflow and the rule that a closure leads with
    every id it closes both produce multi-id subjects, so one housekeeping
    commit routinely took several items out of the queue together.
    """
    subject = "PL-HKF4, PL-PGZK, PL-5WFS, PL-22Z3: recover the stranded capture"
    found = _in_flight(
        [HARNESS],
        commits={
            HARNESS: [
                ("2026-09-04", subject, "c1", "docs/items/PL-HKF4-a.md", "docs/items/PL-PGZK-b.md")
            ]
        },
    )

    assert found == ()


def test_a_commit_naming_no_paths_keeps_its_claim() -> None:
    """A merge prints no paths, and silence is not evidence of annotation.

    Of the two errors available this is the cheaper one: an item wrongly left
    marked is one a session picks around, while an item wrongly unmarked is two
    sessions on one piece of work.
    """
    found = _in_flight(
        [HARNESS], commits={HARNESS: [("2026-09-03", "PL-K7QX: merge main", "c1", "")]}
    )

    assert [branch.item_id for branch in found] == ["PL-K7QX"]


def test_a_branch_named_for_the_item_carries_it_however_it_committed() -> None:
    """What covers the session that starts an item by filling in its fields.

    A `touches` fill or a `verify:` command is annotation by the diff and a
    claim in fact. The branch name is read whatever the diff says, so a session
    that names its own branch is still visible; a harness-named branch is not,
    which is why the skill asks for the id in the branch name.
    """
    named = "claude/pl-k7qx-do-the-thing"
    found = _in_flight(
        [named], commits={named: [("2026-09-03", "PL-K7QX: fill in touches", "c1", QUEUE_ONLY)]}
    )

    assert [branch.item_id for branch in found] == ["PL-K7QX"]


def test_a_branch_that_annotated_and_then_implemented_is_in_flight() -> None:
    """One implementing commit is enough; the annotations beside it change nothing."""
    found = _in_flight(
        [HARNESS],
        commits={
            HARNESS: [
                ("2026-09-04", "PL-K7QX: record what the fix will need", "c2", QUEUE_ONLY),
                ("2026-09-03", "PL-K7QX: add the failing test", "c1", "tests/test_thing.py"),
            ]
        },
    )

    assert [branch.item_id for branch in found] == ["PL-K7QX"]


def test_an_empty_commit_leading_with_an_id_claims_the_item_before_any_work() -> None:
    """The claim a session pushes the moment it starts, before it has any work.

    `.claude/skills/docket/modes/start.md` tells a session to push
    `git commit --allow-empty -m "PL-K7QX: start"` first, because a claim that
    waits for real work waits for as long as the work takes: `PL-0HPV`'s session
    ran twenty minutes unseen on 2026-09-22 while another reported the item
    unstarted (`PL-7TVT`). That instruction is only true while `_annotates_only`
    reads an empty diff as a claim rather than as annotation, so this pins it.
    """
    found = _in_flight([HARNESS], commits={HARNESS: [("2026-09-22", "PL-K7QX: start", "c1")]})

    assert [branch.item_id for branch in found] == ["PL-K7QX"]


def test_the_queue_directory_is_read_from_the_project_setting() -> None:
    """A project keeping its queue elsewhere gets the same reading, not a default.

    Hardcoding `docs/items` would read every commit in such a project as work,
    which is the behavior this replaces.
    """
    runner = _runner(
        [HARNESS],
        commits={HARNESS: [("2026-09-03", "PL-K7QX: capture it", "c1", "tracker/PL-K7QX-a.md")]},
    )

    assert branches_in_flight(ROOT, items_dir="tracker", runner=runner).ids == set()
    assert branches_in_flight(ROOT, items_dir="docs/items", runner=runner).ids == {"PL-K7QX"}


def test_flight_names_the_local_branch_where_the_checkout_holds_both() -> None:
    """`--source` names *a* ref that reached a commit, and promises nothing about which.

    Measured 2026-09-04: with `claude/next-workflow-item-knjkkt` and its tracking
    ref holding identical history, one walk credited the branch's newest
    `PL-YHD3` commit to the local ref and its oldest to `origin/...`. Attribution
    varies per commit inside a single walk, so it cannot be read off git at all
    (`PL-R6D8`).

    `branches_in_flight` survives that, needing only some ref per id, which is
    why it never showed as a bug. What it cost is that `flight` and `triage`
    printed whichever ref the walk happened to credit - so a session could be
    shown `origin/claude/...` for work its own local branch was carrying, which
    is the exact confusion those lines exist to remove. Candidate order decides
    it here instead, and it puts the local branch first.
    """
    # A harness-named branch, so the id comes only from the commit subject and
    # the branch-name reading cannot supply the answer on its own.
    local = "claude/next-workflow-item-knjkkt"
    tracking = f"origin/{local}"
    # git credited the shared commit to the tracking ref, which it is entitled
    # to do and did on 2026-09-04. Both refs are candidates; the report names
    # the local one regardless of which git picked.
    report = _report(
        [local, tracking],
        commits={tracking: [("2026-09-04", "PL-YHD3: the work both refs hold", "c1")]},
    )

    assert [(branch.item_id, branch.name) for branch in report.branches] == [("PL-YHD3", local)]


def test_a_queue_only_commit_is_reported_as_a_file_edit_though_not_as_work() -> None:
    """The failure `PL-N1JK` records: a triage pass no guard could see.

    A pass that only fills in fields writes nothing outside the queue, so
    `_annotates_only` withholds the claim - correctly, since it is not work -
    and until the file edits were read there was nothing else to report. Two
    sessions triaged one pair of items on 2026-09-06, each fetched, each ran
    `show`, and each was told truthfully that nothing was in flight; the merge
    discarded one of the two answers.
    """
    report = _report(
        [HARNESS], commits={HARNESS: [("2026-09-03", "PL-K7QX: triage it", "c1", QUEUE_ONLY)]}
    )

    assert report.branches == ()
    assert report.ids == frozenset()
    assert [(edit.item_id, edit.name) for edit in report.editing] == [("PL-K7QX", HARNESS)]


def test_an_item_file_already_on_the_base_is_not_reported_as_edited_on_a_branch() -> None:
    """The mark has to survive the merge that took the edit it names (`PL-8MJ3`).

    A squash merge keeps none of the branch's commits, so the branch stays ahead
    of the base indefinitely and goes on reporting every item file it ever
    touched. Measured 2026-09-07: a triage pass over five open captures was told
    to skip four of them, and every one of the four branch copies was
    byte-identical to the copy on `origin/main`, both branches having
    squash-merged as `#421` and `#422`.

    `SKILL.md` tells a triage pass to obey this mark, so obeyed literally that
    pass would have triaged one item of five - and would have gone on skipping
    the other four on every future pass, because nothing prunes the ref. The
    wrong answer was on the side that loses work rather than the side that
    duplicates it.
    """
    report = _report(
        [HARNESS],
        commits={HARNESS: [("2026-09-03", "PL-K7QX: triage it", "c1", QUEUE_ONLY)]},
        tips={HARNESS: {}},
    )

    assert report.editing == ()
    assert report.branches == ()


def _numstat_calls(log: list[list[str]]) -> list[list[str]]:
    """The tip comparisons a run made, each as the paths it named.

    `_superseded` is the only caller spelling `--numstat`, so this is exactly
    the question `PL-DMDF` is about: how many times it was put, and about what.
    """
    return [
        args[args.index("--") + 1 :] for args in log if args[0] == "diff" and "--numstat" in args
    ]


def test_superseded_is_asked_once_for_the_whole_outstanding_set() -> None:
    """One `git diff` per ref, not one per item file (`PL-DMDF`).

    `_superseded` takes `paths` and hands them to git as a single pathspec, and
    two of its three callers always did. The third called it from inside a dict
    comprehension with a one-element tuple, so a branch that edited forty item
    files - an ordinary triage pass - cost forty processes to answer one
    question about one ref.

    It is the session-start hook that pays this, on every machine, before the
    first turn. Measured on this container at 19 unmerged refs carrying 111
    item-file edits: `digest` asked git 348 times and spawned 179 processes
    before the hoist, 285 and 118 after, with `diff` alone going 155 asked and
    115 run to 92 and 54. The digest's output is byte-identical either way,
    which is the whole point - nothing about the answer changes, only how many
    times git is asked for it.

    What this pins is the call shape rather than the saving, because the saving
    is a property of the store and the call shape is a property of the code.
    """
    files = {
        "PL-3JN2": "docs/items/PL-3JN2-first.md",
        "PL-7QW5": "docs/items/PL-7QW5-second.md",
        "PL-9KD4": "docs/items/PL-9KD4-third.md",
    }
    calls: list[list[str]] = []
    report = branches_in_flight(
        ROOT,
        runner=_runner(
            [HARNESS],
            commits={
                HARNESS: [
                    ("2026-09-03", f"{identifier}: triage it", f"c{position}", path)
                    for position, (identifier, path) in enumerate(files.items())
                ]
            },
            log=calls,
        ),
    )

    assert [edit.item_id for edit in report.editing] == sorted(files)
    assert _numstat_calls(calls) == [list(files.values())]


def test_two_refs_are_asked_separately_and_each_about_only_its_own_paths() -> None:
    """The hoist groups by ref, because the question is per ref and not per store.

    `_superseded` compares one ref's tip against the base's, so a pathspec
    mixing two refs' files would ask the wrong question of half of them. One
    call per ref is the floor this can reach, and the guard against reaching
    for a lower one.
    """
    other = "origin/claude/second-branch-qqqq11"
    calls: list[list[str]] = []
    branches_in_flight(
        ROOT,
        runner=_runner(
            [HARNESS, other],
            commits={
                HARNESS: [
                    ("2026-09-03", "PL-3JN2: triage it", "c1", "docs/items/PL-3JN2-first.md")
                ],
                other: [
                    ("2026-09-03", "PL-7QW5: triage it", "c2", "docs/items/PL-7QW5-second.md"),
                    ("2026-09-03", "PL-9KD4: triage it", "c3", "docs/items/PL-9KD4-third.md"),
                ],
            },
            log=calls,
        ),
    )

    assert sorted(_numstat_calls(calls)) == [
        ["docs/items/PL-3JN2-first.md"],
        ["docs/items/PL-7QW5-second.md", "docs/items/PL-9KD4-third.md"],
    ]


def test_one_call_still_answers_each_path_on_its_own_evidence() -> None:
    """Batching the question must not batch the answer.

    Three item files on one ref, with three different verdicts in one
    `--numstat`: one whose tips agree (superseded on the branch), one the base
    holds a superset of (superseded on the base, the expensive shape
    `PL-XLQ5` records), and one carrying content the base's tip does not have.
    Only the third is work the base is missing, so only the third keeps its
    mark.
    """
    report = _report(
        [HARNESS],
        commits={
            HARNESS: [
                ("2026-09-03", "PL-3JN2: triage it", "c1", "docs/items/PL-3JN2-first.md"),
                ("2026-09-03", "PL-7QW5: triage it", "c2", "docs/items/PL-7QW5-second.md"),
                ("2026-09-03", "PL-9KD4: triage it", "c3", "docs/items/PL-9KD4-third.md"),
            ]
        },
        tips={
            HARNESS: {
                # PL-3JN2 is absent, which is how git reports two tips that agree.
                "docs/items/PL-7QW5-second.md": ("0", "4"),
                "docs/items/PL-9KD4-third.md": ("7", "0"),
            }
        },
    )

    assert [edit.item_id for edit in report.editing] == ["PL-9KD4"]


def test_a_pathspec_too_long_for_one_command_line_is_split_rather_than_sent() -> None:
    """The bound the hoist needs, and it is a safety bound rather than a speed one.

    Asking about a whole ref's paths at once puts them all on one command line.
    An argv over the platform's `ARG_MAX` does not fail loudly: `subprocess`
    raises, `_run_git` answers the empty string, and a `--numstat` that names
    no paths reads as "the tips agree about every one of them" - so every
    in-flight mark the ref carries would be dropped, which is the direction
    this module must never fail in. Splitting on a byte budget removes the
    failure mode rather than making it rarer.

    The budget holds about a thousand queue paths, so this is reachable only by
    a branch far larger than any this store has seen; the test fabricates one.
    """
    paths = tuple(
        f"docs/items/PL-{index:04d}-a-fabricated-item-file-name.md" for index in range(4000)
    )
    chunks = list(_pathspec_chunks(paths))

    assert len(chunks) > 1
    assert sum(len(chunk) for chunk in chunks) == len(paths)
    assert [path for chunk in chunks for path in chunk] == list(paths)
    for chunk in chunks:
        assert sum(len(path) + 1 for path in chunk) <= _PATHSPEC_BYTES


def test_a_split_pathspec_answers_every_path_it_was_given() -> None:
    """Splitting changes how many times git is asked, never what it is told.

    Each chunk's absences are read against that chunk alone, because "git did
    not name this path" means "the tips agree" only about paths that call
    actually asked for. Read against the union it would be a silent false
    positive for every path answered in some other chunk.
    """
    paths = tuple(
        f"docs/items/PL-{index:04d}-a-fabricated-item-file-name.md" for index in range(4000)
    )
    agreed = {paths[0], paths[2500], paths[-1]}
    asked: list[tuple[str, ...]] = []

    def run(args: list[str], root: Path) -> str:
        chunk = tuple(args[args.index("--") + 1 :])
        asked.append(chunk)
        return "\n".join(f"3\t1\t{path}" for path in chunk if path not in agreed)

    superseded = _superseded(HARNESS, BASE, paths, ROOT, run)

    assert len(asked) > 1
    assert superseded == agreed


def test_a_closed_item_is_not_reported_in_flight() -> None:
    """A ref outlives the merge that took its work, and the line outlived the release.

    Measured 2026-09-07 after a full fetch: `PL-GVXP` (shipped in v0.4.7) and
    `PL-S5LB` (v0.4.6) were both still named on the digest's `In flight on a
    branch:` line, under "do not start these again". One reading of that line had
    all three of its entries closed, and the next had a genuinely live session
    arriving *fourth* behind them (`PL-6BDX`).

    Nothing is misrouted by it - `docket next` does not offer closed items - and
    that is the point: `CLAUDE.md` calls a check that fires every run without
    changing a decision a defect in the check, because it trains a session to
    skim the output where a real entry also appears. Here the real entries are
    the ones that stop two sessions starting one item.
    """
    shipped = "origin/claude/pl-gvxp-shipped-two-releases-ago"
    report = _report(
        [shipped],
        commits={shipped: [("2026-09-03", "PL-GVXP: the work that shipped", "c1", "src/done.py")]},
        closed=("PL-GVXP",),
    )

    assert report.branches == ()


def test_an_item_the_base_took_without_closing_is_not_reported_in_flight() -> None:
    """A triage pass lands its items open, so closedness cannot end its claim.

    `test_a_closed_item_is_not_reported_in_flight` covers a branch that shipped
    something. A pass that triages an item lands it at `ready`, `blocked` or
    `needs-decision` - open on the base, so that guard never fires and the ref
    goes on saying "do not start" for as long as it survives.

    Measured 2026-09-16 on `origin/main` at `2a538ec1`: `PL-2M4X` read
    `P3 - S - ready` there while `bin/docket show` named a branch whose `#616`
    had merged forty minutes earlier. The ref-level content test could not catch
    it - of the seven blobs that branch introduced, six had landed byte for byte
    and the seventh was `ROADMAP.md`, whose squash resolution against a moved
    base is a blob the base has never held (`PL-LKFP`).
    """
    triaged = "origin/claude/pl-2m4x-triage-the-captures"
    report = _report(
        [triaged],
        commits={triaged: [("2026-09-16", "PL-2M4X: triage the captures", "c1", "src/some.py")]},
        same_as_base=("PL-2M4X",),
        took=("PL-2M4X",),
    )

    assert report.branches == ()


def test_a_claim_survives_where_the_base_took_nothing_under_its_id() -> None:
    """The base having the same file is not enough, and this is why.

    A session that has pushed its first failing test under its item's id has not
    necessarily touched the item file yet, so its copy and the base's agree.
    Dropping the claim on that alone would hand the item to a second session,
    which is the collision the whole read exists to prevent.
    """
    live = "origin/claude/some-harness-name-abcd"
    report = _report(
        [live],
        commits={live: [("2026-09-16", "PL-2M4X: the first failing test", "c1", "tests/new.py")]},
        same_as_base=("PL-2M4X",),
    )

    assert [branch.item_id for branch in report.branches] == ["PL-2M4X"]


def test_a_claim_survives_where_the_branch_holds_its_own_copy_of_the_item() -> None:
    """And the base having taken the id is not enough either.

    Both halves are needed: an id the base has taken work under, whose item file
    the ref has nonetheless moved since, is a ref with something left to give.
    """
    live = "origin/claude/some-harness-name-efgh"
    report = _report(
        [live],
        commits={live: [("2026-09-16", "PL-2M4X: close it out", "c1", "src/some.py")]},
        base_items={"PL-2M4X": "src/some.py"},
        took=("PL-2M4X",),
    )

    assert [branch.item_id for branch in report.branches] == ["PL-2M4X"]


def test_a_branch_pushed_to_after_its_pull_request_squash_merged_is_still_in_flight() -> None:
    """A squash makes both halves of the guard true, and they stay true forever.

    The branch's pull request carries the item file to the base, so the two
    copies agree byte for byte; its subject leads with the id, so the base has
    taken that id since the fork. Neither fact says anything about what the
    branch did *next* - and what it does next is the implementation, `src/` and
    `tests/` under the same id with the item file untouched, because the design
    round that merged is what wrote the item file.

    Measured 2026-09-20 and it cost exactly what the read exists to prevent:
    `PL-3K9B`'s whole implementation, 8 files and 637 insertions pushed with
    the id leading its subject, appeared in no reading of the report, while a
    second session spent three replies recommending that the item be started
    fresh. The same command had reported it before `#801` merged, and the only
    thing that changed between the two readings is that the branch's earlier
    commits landed (`PL-8JQQ`).

    Every long-lived branch here ends up in this shape, because the harness
    names a branch once and a session works several items on it.
    """
    live = "origin/claude/lucid-dijkstra-i1qy6x"
    report = _report(
        [live],
        commits={
            live: [
                (
                    "2026-09-20T16:00:00+00:00",
                    "PL-3K9B: the whole implementation",
                    "c2",
                    "src/b.py",
                ),
                ("2026-09-20T15:00:00+00:00", "PL-3K9B: the design round", "c1", "src/a.py"),
            ]
        },
        same_as_base=("PL-3K9B",),
        took=(("PL-3K9B", "2026-09-20T15:30:00+00:00"),),
    )

    assert [(branch.item_id, branch.name) for branch in report.branches] == [("PL-3K9B", live)]


def test_a_claim_older_than_the_base_s_take_is_still_spent() -> None:
    """The bound is a window rather than a switch, and this is its other edge.

    A branch whose every commit under the id precedes the merge that took it
    has nothing left to give, which is the reading `PL-LKFP` installed and the
    one a stale ref depends on to leave the line. Without this the date test
    above would read as "a ref the base took work from is live", which is every
    merged branch this checkout still holds.
    """
    merged_away = "origin/claude/pl-2m4x-triage-the-captures"
    report = _report(
        [merged_away],
        commits={
            merged_away: [
                ("2026-09-16T09:00:00+00:00", "PL-2M4X: triage the captures", "c1", "src/some.py")
            ]
        },
        same_as_base=("PL-2M4X",),
        took=(("PL-2M4X", "2026-09-16T10:00:00+00:00"),),
    )

    assert report.branches == ()


def test_a_spent_claim_on_a_bystander_branch_does_not_drop_a_live_one() -> None:
    """The guard judges a claim per ref, so the walk may not keep one ref per id.

    Observed 2026-09-19 on the fetched remote. A branch whose pull request had
    squash-merged still carried a commit leading with four ids; it sorted first
    among the remote refs, so the walk credited those ids to it and discarded
    every other carrier. `_taken_on_base` then correctly found *its* claim on
    two of them spent - the base's copy of each item file was byte for byte the
    branch's, and the base had taken a commit leading with the id since the fork
    - and deleting the ids took two live design rounds with them. `bin/docket
    show` called both startable while a session held each (`PL-2BZY`).

    So the claim that is spent is the bystander's alone, and the id stays in
    flight, reported against the branch that still has something to give.
    """
    bystander = "origin/claude/bystander-abcdef"
    live = "origin/claude/live-session-ghijkl"
    report = _report(
        [bystander, live],
        commits={
            bystander: [
                ("2026-09-19", "PL-2M4X, PL-K7QX: make the tracking items cluster heads", "c1")
            ],
            live: [("2026-09-19", "PL-2M4X: record the ratified decision", "c2", "ROADMAP.md")],
        },
        same_as_base=((bystander, "PL-2M4X"),),
        took=("PL-2M4X",),
    )

    assert [(branch.item_id, branch.name) for branch in report.branches] == [
        ("PL-2M4X", live),
        ("PL-K7QX", bystander),
    ]


def test_an_id_leaves_the_report_once_every_carrier_s_claim_is_spent() -> None:
    """The guard is not weakened by being asked per ref - it is asked of each.

    The pair above is what separates this from the collapse it replaced: one
    live carrier keeps the id, and no live carrier still drops it.
    """
    bystander = "origin/claude/bystander-abcdef"
    other = "origin/claude/also-merged-ghijkl"
    report = _report(
        [bystander, other],
        commits={
            bystander: [("2026-09-19", "PL-2M4X: the work that merged", "c1")],
            other: [("2026-09-19", "PL-2M4X: the rider that merged with it", "c2")],
        },
        same_as_base=((bystander, "PL-2M4X"), (other, "PL-2M4X")),
        took=("PL-2M4X",),
    )

    assert report.branches == ()


def test_a_superseded_file_edit_on_a_bystander_branch_does_not_drop_a_live_one() -> None:
    """`_superseded` judges a path on one ref, so the walk may not keep one per id.

    `PL-2BZY`'s collapse, one reading over: `_Walk.edited` kept the rank-first
    ref per id, and `editing` then dropped any mark whose path the base already
    holds. So where two refs have both edited one item's file and the rank-first
    ref's copy has landed - a squash merge, a rebase, a cherry-pick - the id
    left the report entirely, though the other ref's edit is unmerged and is
    exactly the collision the mark exists to name.

    Losing it is silent, which is what makes it worth a test rather than a
    warning: `flight` and `triage` print the marks that survived, and nothing
    says one was collapsed away (`PL-RY2R`).
    """
    bystander = "origin/claude/bystander-abcdef"
    live = "origin/claude/live-session-ghijkl"
    edits = "docs/items/PL-3JN2-triage-it.md"
    report = _report(
        [bystander, live],
        commits={
            bystander: [("2026-09-19", "PL-3JN2: triage it", "c1", edits)],
            live: [("2026-09-19", "PL-3JN2: triage it too", "c2", edits)],
        },
        # An empty map for the bystander is how git reports two tips that
        # agree; the live session's ref is absent from `tips` and so still
        # carries an addition the base does not have.
        tips={bystander: {}},
    )

    assert [(edit.item_id, edit.name) for edit in report.editing] == [("PL-3JN2", live)]


def test_an_id_leaves_editing_once_every_carrier_s_edit_is_superseded() -> None:
    """The supersession test is not weakened by being asked per ref - each is asked.

    The pair above is what separates this from the collapse it replaced: one
    live carrier keeps the mark, and no live carrier still drops it.
    """
    bystander = "origin/claude/bystander-abcdef"
    other = "origin/claude/also-merged-ghijkl"
    edits = "docs/items/PL-3JN2-triage-it.md"
    report = _report(
        [bystander, other],
        commits={
            bystander: [("2026-09-19", "PL-3JN2: triage it", "c1", edits)],
            other: [("2026-09-19", "PL-3JN2: triage it again", "c2", edits)],
        },
        tips={bystander: {}, other: {}},
    )

    assert report.editing == ()


def test_a_file_edit_on_an_unread_ref_does_not_drop_a_readable_carrier_s() -> None:
    """The unread-ref filter had the same shape as the supersession one above.

    A ref whose walk ran off the end of a truncated history contributes no
    commits, so its edits are not believed - but collapsing to the rank-first
    ref first meant an id whose rank-first editor was that ref lost the mark
    even where a readable ref had edited the same file (`PL-RY2R`).
    """
    unread = "origin/claude/truncated-abcdef"
    live = "origin/claude/live-session-ghijkl"
    edits = "docs/items/PL-3JN2-triage-it.md"
    report = _report(
        [unread, live],
        commits={
            unread: [("2026-09-19", "PL-3JN2: triage it", "c1", edits)],
            live: [("2026-09-19", "PL-3JN2: triage it too", "c2", edits)],
        },
        ran_out=(unread,),
    )

    assert [(edit.item_id, edit.name) for edit in report.editing] == [("PL-3JN2", live)]


def test_a_landed_design_round_on_a_bystander_branch_does_not_drop_a_live_one() -> None:
    """The third instance, and the one nearest the case `PL-VYSP` was built for.

    `own_edits` is keyed `(ref, id)`, so the walk itself keeps every carrier;
    the collapse was in the caller, which chose one by rank before either of
    its two per-ref tests ran. A bystander branch whose design-round commit
    has landed - byte-identical to the base, so `_superseded` finds nothing
    outstanding - therefore suppressed a live round another ref was running on
    the same item, and `bin/docket show` called it startable (`PL-61MD`).

    A design round leaves no diff outside the queue, so nothing else marks it.
    """
    bystander = "origin/claude/bystander-abcdef"
    live = "origin/claude/live-session-ghijkl"
    round_file = "docs/items/PL-3JN2-decide-it.md"
    report = _report(
        [bystander, live],
        commits={
            bystander: [("2026-09-19", "PL-3JN2: record the round", "c1", round_file)],
            live: [("2026-09-19", "PL-3JN2: put the case", "c2", round_file)],
        },
        statuses={"PL-3JN2": "needs-decision"},
        tips={bystander: {}},
    )

    assert [(branch.item_id, branch.name) for branch in report.branches] == [("PL-3JN2", live)]


def test_a_stale_capture_on_a_bystander_branch_does_not_drop_a_live_round() -> None:
    """`_modified_by` is a fact about a commit, so it is the second per-carrier test.

    The other half of `PL-61MD`. A capture creates the item file and a round
    writes into one that exists, which is what `_modified_by` reads off the
    commit's own parent - so where the rank-first carrier is a stale capture,
    collapsing to it failed the test for an id another ref was deciding.
    """
    bystander = "origin/claude/bystander-abcdef"
    live = "origin/claude/live-session-ghijkl"
    round_file = "docs/items/PL-3JN2-decide-it.md"
    report = _report(
        [bystander, live],
        commits={
            bystander: [("2026-09-19", "PL-3JN2: file it", "c1", round_file)],
            live: [("2026-09-19", "PL-3JN2: put the case", "c2", round_file)],
        },
        statuses={"PL-3JN2": "needs-decision"},
        created=(("c1", "PL-3JN2"),),
    )

    assert [(branch.item_id, branch.name) for branch in report.branches] == [("PL-3JN2", live)]


def test_a_design_round_leaves_the_promotion_once_every_carrier_fails() -> None:
    """Both per-carrier tests, asked of each carrier, still refuse where each fails.

    Two stale captures on one item: neither commit changed a file it
    inherited, so the promotion is withheld exactly as the collapse withheld
    it, and the ids stay on the weaker `editing` mark.
    """
    bystander = "origin/claude/bystander-abcdef"
    other = "origin/claude/also-a-capture-ghijkl"
    round_file = "docs/items/PL-3JN2-decide-it.md"
    report = _report(
        [bystander, other],
        commits={
            bystander: [("2026-09-19", "PL-3JN2: file it", "c1", round_file)],
            other: [("2026-09-19", "PL-3JN2: file it again", "c2", round_file)],
        },
        statuses={"PL-3JN2": "needs-decision"},
        created=(("c1", "PL-3JN2"), ("c2", "PL-3JN2")),
    )

    assert report.branches == ()
    assert [edit.item_id for edit in report.editing] == ["PL-3JN2"]


def test_an_item_closed_only_on_a_branch_is_still_reported_in_flight() -> None:
    """The closure has to be *on the base*, which is the care the rule turns on.

    A session closing an item right now carries that closure on its own branch.
    Reading the working tree, or any ref but the base, would suppress exactly the
    live work the line exists to protect - so the base is asked, being the one
    tree that cannot hold an unmerged session's answer.
    """
    live = "origin/claude/pl-k7qx-closing-it-now"
    report = _report(
        [live],
        commits={live: [("2026-09-03", "PL-K7QX: close it", "c1", "src/work.py")]},
        closed=(),
    )

    assert [branch.item_id for branch in report.branches] == ["PL-K7QX"]


def test_a_branch_working_an_item_is_not_also_reported_as_editing_its_file() -> None:
    """One item, one mark. The stronger one is the one the reader needs.

    A closure writes the item and the code in one commit, so both readings fire
    on it; printing two lines about one item invites the reading that they name
    two different branches.
    """
    report = _report(
        [HARNESS],
        commits={
            HARNESS: [("2026-09-03", "PL-K7QX: do the thing", "c1", QUEUE_ONLY, "src/thing.py")]
        },
    )

    assert [branch.item_id for branch in report.branches] == ["PL-K7QX"]
    assert report.editing == ()


def test_a_file_edit_is_read_from_the_paths_rather_than_from_the_subject() -> None:
    """The weaker reading infers nothing: it is a fact about the diff.

    A session working one item and capturing a finding about another produces
    exactly this commit. The subject claims the first, the diff touches the
    second, and it is the second that a triage pass on that other item would
    collide with.
    """
    report = _report(
        [HARNESS],
        commits={
            HARNESS: [
                (
                    "2026-09-03",
                    "PL-K7QX: do the thing",
                    "c1",
                    "src/thing.py",
                    "docs/items/PL-J295-a-finding.md",
                )
            ]
        },
    )

    assert [branch.item_id for branch in report.branches] == ["PL-K7QX"]
    assert [(edit.item_id, edit.name) for edit in report.editing] == [("PL-J295", HARNESS)]


def test_a_file_edit_carries_the_date_the_branch_last_moved() -> None:
    """A branch nobody will merge and a live session look alike here too.

    The same reading `flight` and `stranded` make: the age is reported and the
    reader decides, because no timeout separates the two.
    """
    report = _report(
        [HARNESS], commits={HARNESS: [("2026-09-03", "PL-K7QX: triage it", "c1", QUEUE_ONLY)]}
    )

    assert report.editing[0].last_commit == datetime(2026, 9, 3, tzinfo=UTC)


def test_a_ref_whose_walk_ran_off_the_end_contributes_no_file_edits() -> None:
    """The paths are as unproven as the ids when the walk was unbounded.

    A walk that ended at a parentless commit ran off the end of a truncated
    history rather than stopping against the default branch, so the commits it
    emitted may be the default branch's own - and their paths with them.
    """
    report = _report(
        [HARNESS],
        commits={HARNESS: [("2026-09-03", "PL-K7QX: triage it", "c1", QUEUE_ONLY)]},
        ran_out=(HARNESS,),
    )

    assert report.editing == ()
    assert report.unreadable == (HARNESS,)


def test_a_file_edit_is_read_against_the_project_queue_directory() -> None:
    """A project keeping its queue elsewhere gets the same reading, not a default."""
    runner = _runner(
        [HARNESS],
        commits={HARNESS: [("2026-09-03", "PL-K7QX: triage it", "c1", "tracker/PL-K7QX-a.md")]},
    )

    assert branches_in_flight(ROOT, items_dir="docs/items", runner=runner).editing == ()
    editing = branches_in_flight(ROOT, items_dir="tracker", runner=runner).editing
    assert [edit.item_id for edit in editing] == ["PL-K7QX"]


def test_a_queue_path_that_names_no_item_is_not_a_file_edit() -> None:
    """The store holds a README beside the items, and it belongs to no id."""
    report = _report(
        [HARNESS],
        commits={
            HARNESS: [
                ("2026-09-03", "PL-K7QX: rewrite the store's README", "c1", "docs/items/README.md")
            ]
        },
    )

    assert report.editing == ()


def test_the_last_commit_is_dated_so_a_stale_branch_can_be_told_apart() -> None:
    refs = ["origin/claude/harness-named-abcdef"]
    found = _in_flight(
        refs,
        commits={
            refs[0]: [
                ("2026-08-30", "PL-K7QX Finish the thing"),
                ("2026-07-04", "PL-K7QX Start the thing"),
            ]
        },
    )

    assert [b.last_commit for b in found] == [datetime(2026, 8, 30, tzinfo=UTC)]


def test_a_branch_with_no_commits_of_its_own_is_dated_not_guessed() -> None:
    assert _in_flight(["claude/pl-k7qx-just-created"])[0].last_commit is None


def test_a_ref_with_no_readable_merge_base_is_reported_rather_than_walked() -> None:
    """A truncated clone is missing history, not holding a branch of nothing.

    Excluding `^origin/main` from a walk that cannot reach it would report the
    ref's whole visible history as its own work, so the ref is named as unread.
    """
    refs = ["origin/claude/pl-k7qx-live", "origin/claude/beyond-the-horizon-abcdef"]
    report = branches_in_flight(ROOT, runner=_runner(refs, unrelated=(refs[1],)))

    assert report.unreadable == (refs[1],)
    assert [b.item_id for b in report.branches] == ["PL-K7QX"]
    assert report.base == BASE


TRUNCATED = "origin/claude/merged-main-in-abcdef"

# What the walk sees on such a ref: its own commit, then the default branch's
# own commits reached round the graft, the oldest of them parentless because
# the checkout holds no more history. `PL-M01` here stands for the eighteen
# closed items the 2026-08-31 digest reported as work in progress.
RAN_OFF_THE_END = [
    ("2026-08-31", "PL-K7QX Do the thing"),
    ("2026-08-20", "PL-M0J2 Something the default branch already carries"),
]


def test_ids_from_a_walk_that_cannot_prove_a_commit_is_contained_are_dropped() -> None:
    """The defect: a merge-base resolves and the walk below it is still short.

    `^base` excludes only what this checkout can reach from the default branch,
    and a truncated clone's default branch ends at a grafted commit - so a ref
    reaching round that graft has the default branch's own commits, and the ids
    leading them, reported as its work. The digest prints those under "do not
    start these again", which is why an unread ref is the cheaper error.
    """
    report = branches_in_flight(
        ROOT,
        runner=_runner([TRUNCATED], commits={TRUNCATED: RAN_OFF_THE_END}, ran_out=(TRUNCATED,)),
    )

    assert report.branches == ()
    assert report.unreadable == (TRUNCATED,)


def test_a_walk_that_proves_every_commit_is_contained_is_read_as_before() -> None:
    """The guard must not cost the read it protects.

    A walk that stops against a commit the default branch accounted for has
    proved what it found, truncated clone or not - which is the ordinary case
    in an agent session's container and must stay answered.
    """
    found = _in_flight([TRUNCATED], commits={TRUNCATED: RAN_OFF_THE_END})

    assert [branch.item_id for branch in found] == ["PL-K7QX", "PL-M0J2"]


def test_a_ref_that_cannot_prove_what_is_contained_does_not_silence_the_others() -> None:
    """One ref's missing history is not a reason to stop reading the rest."""
    live = "origin/claude/pl-9y42-live"
    report = branches_in_flight(
        ROOT,
        runner=_runner(
            [TRUNCATED, live],
            commits={TRUNCATED: RAN_OFF_THE_END, live: [("2026-08-31", "PL-9Y42 Wash-in")]},
            ran_out=(TRUNCATED,),
        ),
    )

    assert [branch.item_id for branch in report.branches] == ["PL-9Y42"]
    assert report.unreadable == (TRUNCATED,)


def test_tags_are_read_from_the_repository() -> None:
    read = tags(ROOT, runner=lambda args, root: "v0.1.0\nv0.2.0\n")

    assert read.names == frozenset({"v0.1.0", "v0.2.0"})
    assert read.known


def test_a_repository_holding_no_tags_answers_with_an_empty_set() -> None:
    """The answered emptiness, which `release.is_untagged` holds to nothing."""
    read = tags(ROOT, runner=lambda args, root: "")

    assert read.names == frozenset()
    assert read.known


def test_a_git_that_will_not_say_which_tags_exist_declines_rather_than_answering_none() -> None:
    """The two used to be one value, and the release gate acts on the difference.

    `is_untagged` reads an empty set as "this project does not tag" and holds
    the project to nothing - correct for a repository that answered, and free
    passage for one that did not: the cut went ahead with the tag gate skipped
    and nothing said. `cmd_release` refuses on `declined` now, so the direction
    turns on this distinction and not on a set that means both (`PL-ZPDM`).
    """
    silent = tags(ROOT, runner=lambda args, root: SILENT)

    assert silent.names == frozenset()
    assert not silent.known
    assert "tag --list" in silent.declined


def test_a_git_that_will_not_diff_declines_rather_than_reporting_no_changed_items() -> None:
    """The scope of `check --verify-base`, and the same collapse one read along.

    An empty set here scopes the `verify:` replay to nothing, so the run
    executes no command and reports a clean result - which is what a branch
    that changed no item also produces. The reason travels with the answer now
    and `cmd_check` declines the replay whole rather than claiming that scope.
    """
    silent = changed_items(ROOT, BASE, runner=lambda args, root: SILENT)

    assert silent.identifiers == frozenset()
    assert not silent.known
    assert "did not answer" in silent.declined

    # A git that ran and found nothing is the other case, and still an answer:
    # this branch changed no item file, which is a fact about the branch.
    answered = changed_items(ROOT, BASE, runner=lambda args, root: "")

    assert answered.identifiers == frozenset()
    assert answered.known


def _refs(known: dict[str, str]):
    """A git that resolves exactly the refs given, and counts what they say."""

    def run(args: list[str], root: Path) -> str:
        if args[:2] == ["rev-parse", "--verify"]:
            return known.get(args[-1], "")
        if args[:2] == ["rev-list", "--count"]:
            return known.get(args[-1], "")
        return ""

    return run


def test_the_default_base_prefers_the_ref_the_branch_forked_from() -> None:
    """A local `main` in a fresh clone is not what the branch diverged from."""
    runner = _refs({"origin/main": "abc123", "main": "def456"})

    assert default_base(ROOT, runner=runner) == "origin/main"


def test_the_default_base_falls_back_to_a_local_branch() -> None:
    base = default_base(ROOT, runner=_refs({"main": "def456"}))

    assert base == "main"
    # Reached by git answering `no` for both remote candidates, which is an
    # answer: this is the checkout the fallback is *for*, so it is not a guess.
    assert resolved(base)


def test_a_repository_resolving_no_default_branch_says_the_base_was_guessed() -> None:
    """The literal `main` handed back for a checkout that has no `main` (`PL-73P0`).

    It still answers, and it still answers `main`, because sixteen reads in this
    module interpolate the base into a message and the empty string names
    nothing. What has changed is that the answer carries the mark, so a caller
    comparing against it can tell the ref was picked rather than read.
    """
    base = default_base(ROOT, runner=_refs({}))

    assert base == "main"
    assert not resolved(base)


def test_a_base_reached_by_falling_past_an_unanswered_probe_is_a_guess() -> None:
    """A real ref can still be the wrong one, and this is the costly case.

    `main` resolves, so nothing here looks broken - but the probe for
    `origin/main` went unanswered, and the remote ref may be sitting there
    unread. A fresh clone's local `main` can trail the remote by many commits,
    and a diff taken against it reports everything that landed in between as
    this branch's own work: the measured instance named 20 paths outside an
    item's commission where the true answer was 4.
    """

    def run(args: list[str], root: Path) -> str:
        if args[-1] == "origin/main":
            return SILENT
        return "def456" if args[-1] == "main" else ""

    base = default_base(ROOT, runner=run)

    assert base == "main"
    assert not resolved(base)


def test_a_base_every_candidate_was_read_for_is_not_marked() -> None:
    """The ordinary path stays unmarked, or the mark means nothing.

    A guard against the cheap way to pass the tests above: marking every answer
    would satisfy them and would make `resolved` useless to every caller.
    """
    assert resolved(default_base(ROOT, runner=_refs({"origin/main": "abc123"})))
    assert resolved(default_base(ROOT, runner=_refs({"origin/main": "a", "main": "b"})))


def test_a_local_base_behind_its_remote_is_counted() -> None:
    runner = _refs({"origin/main": "abc123", "main..origin/main": "7"})

    assert behind_remote(ROOT, "main", runner=runner) == 7


def test_a_base_current_with_its_remote_counts_zero() -> None:
    runner = _refs({"origin/main": "abc123", "main..origin/main": "0"})

    assert behind_remote(ROOT, "main", runner=runner) == 0


def test_a_remote_base_is_not_judged_against_a_remote_of_its_own() -> None:
    assert behind_remote(ROOT, "origin/main", runner=_refs({"origin/origin/main": "x"})) is None


def test_a_base_with_no_counterpart_on_the_remote_is_not_judged() -> None:
    assert behind_remote(ROOT, "topic", runner=_refs({})) is None


def _pr_runner(shallow: str, subjects: list[str]):
    def run(args: list[str], root: Path) -> str:
        if args[:2] == ["rev-parse", "--is-shallow-repository"]:
            return shallow + "\n" if shallow else ""
        if args[0] == "rev-parse":
            return "origin/main\n"
        if args[0] == "log":
            return "\n".join(subjects)
        return ""

    return run


SUBJECTS = [
    "Merge pull request #86 from stuthedew/claude/scope-gate-freeze",
    "PL-ZQ9C: record the pull request (#87)",
    "Release v0.2.7",
]


def test_both_merge_subject_forms_name_their_pull_request() -> None:
    history = merged_pull_requests(ROOT, runner=_pr_runner("false", SUBJECTS))

    assert history.known
    assert history.numbers == frozenset({86, 87})


def test_a_shallow_clone_declines_and_says_why() -> None:
    """Its missing commits are the oldest, so it would report settled work as broken."""
    history = merged_pull_requests(ROOT, runner=_pr_runner("true", SUBJECTS))

    assert not history.known
    assert "shallow" in history.declined
    assert history.numbers == frozenset()


def test_a_shallow_clone_is_not_deepened_to_get_an_answer() -> None:
    """`docket check` runs from a bare tree with no network; it must stay that way."""
    asked: list[list[str]] = []

    def run(args: list[str], root: Path) -> str:
        asked.append(args)
        return "true\n" if args[:2] == ["rev-parse", "--is-shallow-repository"] else ""

    merged_pull_requests(ROOT, runner=run)

    assert not any(args[0] in ("fetch", "clone", "remote") for args in asked)


def _since_runner(log: str, shallow: str = "false") -> Runner:
    def run(args: list[str], root: Path) -> str:
        if args[:2] == ["rev-parse", "--is-shallow-repository"]:
            return shallow + "\n"
        return log if "log" in args else ""

    return run


def test_since_filed_counts_a_commit_once_per_path_and_only_beneath_it(tmp_path: Path) -> None:
    """A directory counts a commit once however many files it changed, and a sibling never.

    `docs/items` must not count a change to `docs/itemsX/`, which a bare
    prefix test would, and a path deleted since filing is the one reported
    gone rather than merely absent (`PL-TQN2`).
    """
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("a\n")
    log = "\x1fc1\0\nM\0src/a.py\0A\0src/b.py\0\x1fc2\0\nM\0docs/itemsX/y.md\0D\0gone.py\0"

    report = since_filed(
        tmp_path,
        ("src/", "src/a.py", "docs/items", "gone.py"),
        date(2026, 8, 5),
        runner=_since_runner(log),
    )

    assert report.known
    assert [(p.path, p.exists, p.commits, p.deleted) for p in report.paths] == [
        ("src/", True, 1, False),
        ("src/a.py", True, 1, False),
        ("docs/items", False, 0, False),
        ("gone.py", False, 1, True),
    ]


def test_since_filed_declines_on_a_shallow_clone_and_keeps_what_the_tree_says(
    tmp_path: Path,
) -> None:
    """Its missing commits are the oldest, which this read is about - so no count, not zero."""
    (tmp_path / "a.py").write_text("a\n")

    report = since_filed(
        tmp_path, ("a.py", "b.py"), date(2026, 8, 5), runner=_since_runner("", "true")
    )

    assert not report.known
    assert "shallow" in report.declined
    assert [(p.path, p.exists, p.commits) for p in report.paths] == [
        ("a.py", True, None),
        ("b.py", False, None),
    ]


def test_a_git_that_cannot_say_whether_the_checkout_is_complete_declines() -> None:
    history = merged_pull_requests(ROOT, runner=lambda args, root: "")

    assert not history.known
    assert "complete" in history.declined


def test_a_checkout_with_no_readable_default_branch_declines() -> None:
    history = merged_pull_requests(ROOT, runner=_pr_runner("false", []))

    assert not history.known


def test_a_hash_that_merely_looks_like_a_number_is_not_a_pull_request() -> None:
    subjects = ["Fix the thing #71 mentioned", "Merge branch 'main' into topic"]
    history = merged_pull_requests(ROOT, runner=_pr_runner("false", subjects))

    assert history.known and history.numbers == frozenset()


def _tree_runner(
    trees: dict[str, dict[str, str]],
    titles: dict[str, str] | None = None,
    history: tuple[str, ...] = (),
):
    """A git that holds the given trees, as `ref -> {item file: contents}`.

    Deliberately almost no commit graph: no `--merged`, no ancestry, nothing a
    shallow clone would answer wrongly. If these tests pass with a runner that
    cannot answer a containment question, the implementation is not asking
    one.

    `history` is the text of copies the default branch has held and has since
    moved on from, which is the one object walk this answers. A ref still
    holding one of them is behind whatever the base holds now however
    different the two files read, and without that the base rewriting its own
    prose leaves the ref holding lines the base lacks - which on text alone is
    indistinguishable from the ref having written them.

    A tree keyed `HEAD` is the checkout's own, and is deliberately not listed
    by `for-each-ref`: git lists refs under `refs/heads` and `refs/remotes`,
    and `HEAD` is neither.
    """

    def run(args: list[str], root: Path) -> str:
        if args[0] == "for-each-ref":
            return "\n".join(ref for ref in trees if ref != "HEAD")
        if args[:2] == ["rev-parse", "--verify"]:
            return "abc123\n" if args[-1] in trees else ""
        if args[0] == "rev-list" and "--objects" in args:
            # The object walk `_base_blobs` reads, in the shape git writes it:
            # an oid, then the path anything but a commit was stored under.
            return "".join(
                f"{hashlib.sha1(text.encode()).hexdigest()} docs/items/held.md\n"
                for text in history
            )
        if args[0] == "ls-tree":
            return _tree_lines(
                {f"docs/items/{name}": text for name, text in trees.get(args[2], {}).items()}
            )
        if args[0] == "show":
            ref, _, path = args[1].partition(":")
            return trees.get(ref, {}).get(path.rsplit("/", 1)[-1], "")
        return ""

    return run


def _document(identifier: str, title: str) -> str:
    return f"---\nid: {identifier}\ntitle: {title}\nstatus: untriaged\n---\n\n**Problem.** x\n"


MAIN = {"PL-0001-on-main.md": _document("PL-0001", "On main")}


def test_an_item_only_on_a_branch_is_reported() -> None:
    runner = _tree_runner(
        {
            "origin/main": MAIN,
            "origin/claude/abandoned": {
                **MAIN,
                "PL-K7QX-lost-thought.md": _document("PL-K7QX", "A lost thought"),
            },
        }
    )

    report = stranded(ROOT, {"PL-0001"}, runner=runner)

    assert [(i.identifier, i.title) for i in report.items] == [("PL-K7QX", "A lost thought")]
    assert report.items[0].branches == ("origin/claude/abandoned",)
    assert report.items[0].path == "docs/items/PL-K7QX-lost-thought.md"


def test_an_item_the_default_branch_holds_is_not_stranded() -> None:
    """However its commits got there - a squash merge contains none of them."""
    runner = _tree_runner({"origin/main": MAIN, "origin/claude/squashed": MAIN})

    assert stranded(ROOT, set(), runner=runner).items == ()


def test_an_item_this_checkout_already_holds_is_not_reported_back_to_it() -> None:
    """The session that captured it can see it; it is at risk, not lost."""
    branch = {**MAIN, "PL-K7QX-just-captured.md": _document("PL-K7QX", "Just captured")}
    runner = _tree_runner({"origin/main": MAIN, "claude/this-session": branch})

    assert stranded(ROOT, {"PL-0001", "PL-K7QX"}, runner=runner).items == ()


def test_an_item_that_landed_after_this_branch_forked_is_not_stranded() -> None:
    """A stale working tree lacks it, so the default branch has to be read too."""
    landed = {**MAIN, "PL-M3PP-landed-later.md": _document("PL-M3PP", "Landed later")}
    runner = _tree_runner({"origin/main": landed, "origin/claude/other": landed})

    assert stranded(ROOT, {"PL-0001"}, runner=runner).items == ()


def test_every_branch_holding_a_copy_is_named() -> None:
    """A branch named nowhere strands nothing; naming one copy would break that."""
    branch = {**MAIN, "PL-K7QX-two-copies.md": _document("PL-K7QX", "Two copies")}
    runner = _tree_runner(
        {"origin/main": MAIN, "claude/local": branch, "origin/claude/local": branch}
    )

    report = stranded(ROOT, {"PL-0001"}, runner=runner)

    assert report.items[0].branches == ("claude/local", "origin/claude/local")


def test_a_file_that_is_not_an_item_is_ignored() -> None:
    runner = _tree_runner({"origin/main": MAIN, "origin/topic": {**MAIN, "README.md": "notes"}})

    assert stranded(ROOT, {"PL-0001"}, runner=runner).items == ()


def test_the_number_of_refs_read_is_part_of_the_answer() -> None:
    """ "Nothing stranded" from two refs and from twenty are different claims."""
    runner = _tree_runner({"origin/main": MAIN, "origin/a": MAIN, "origin/b": MAIN})

    assert stranded(ROOT, {"PL-0001"}, runner=runner).refs_read == 3


def test_no_git_declines_rather_than_reporting_a_clean_store() -> None:
    report = stranded(ROOT, set(), runner=lambda args, root: "")

    assert not report.known
    assert report.items == ()


def test_a_default_branch_with_no_items_declines() -> None:
    """Otherwise every item on every branch reads as stranded: long, alarming, wrong."""
    runner = _tree_runner(
        {"origin/main": {}, "origin/topic": {"PL-K7QX-x.md": _document("PL-K7QX", "x")}}
    )

    report = stranded(ROOT, set(), runner=runner)

    assert not report.known
    assert "origin/main" in report.declined


# The item `#325` landed while a checkout eight minutes behind was reading, and
# the branch GitHub deleted on that merge.
MERGED = {**MAIN, "PL-XLQ5-triaged-and-merged.md": _document("PL-XLQ5", "Merged as #325")}
DELETED_ON_MERGE = "origin/claude/deleted-on-merge"


def test_a_merged_and_deleted_branch_is_not_reported_as_stranded() -> None:
    """The 2026-09-05 false report, stated as the difference the base makes.

    `PL-XLQ5` merged at 01:13 and GitHub deleted the head branch; this checkout
    held a tracking ref for it and an `origin/main` fetched at 01:05, so at
    01:16 the item read as existing only on a branch. The recovery command that
    finding prints was run, and restored the pre-triage copy over the triaged
    one the merge had just landed (`PL-KBFN`).

    The deleted remote branch is not the signal and cannot be - a merge deletes
    the branch too, so both histories look identical from the ref's absence.
    What separates them is whether the base holds the item, which is only a
    true answer on a base something refreshed. Both halves are asserted here
    because the second is the finding: the same trees give opposite answers
    across one fetch, so how fresh the base is belongs in the report.
    """
    stale = _tree_runner({"origin/main": MAIN, DELETED_ON_MERGE: MERGED})
    fresh = _tree_runner({"origin/main": MERGED, DELETED_ON_MERGE: MERGED})

    assert [i.identifier for i in stranded(ROOT, {"PL-0001"}, runner=stale).items] == ["PL-XLQ5"]
    assert stranded(ROOT, {"PL-0001"}, runner=fresh, fetched=True).items == ()


def test_whether_the_comparison_point_was_refreshed_is_part_of_the_answer() -> None:
    """Reported only in the negative, for the reason `BranchState` gives.

    A quiet `git fetch` prints nothing whether it reached the remote or not, so
    what can be claimed is that a caller tried - never that a refresh arrived.
    """
    runner = _tree_runner({"origin/main": MAIN, DELETED_ON_MERGE: MERGED})

    assert not stranded(ROOT, {"PL-0001"}, runner=runner).fetched
    assert stranded(ROOT, {"PL-0001"}, runner=runner, fetched=True).fetched


# An item file `main` holds and a branch has written to. This is the commoner
# loss: the file is created once and appended to by every session that learns
# something about it, so the unmerged *section* outnumbers the unmerged file
# (`PL-KSCW`).
APPENDED = {
    "PL-0001-on-main.md": _document("PL-0001", "On main")
    + "\n**Found again 2026-09-20.** A fourth instance, and the count it implies.\n"
}

# The same item after `main` closed it, which is what a branch forked before
# the triage pass is holding an earlier answer to (`PL-MBTZ`).
CLOSED_ON_MAIN = {
    "PL-0001-on-main.md": (
        "---\nid: PL-0001\ntitle: On main\nstatus: done\n"
        "closed: 2026-09-13\npr: 549\n---\n\n**Problem.** x\n"
    )
}


def test_stranded_reports_an_item_modified_only_on_a_branch() -> None:
    """`PL-KSCW`: the file is on the base, and the section is on the branch alone.

    `PL-879R`'s brief was missing a whole section that way - a fourth failure
    shape and the population it implied, written onto
    `origin/claude/focused-dijkstra-outqzu` by the session that found it. The
    id test this read used to make cannot see it: the item is on `main`, so
    the item is not stranded, and only 68 lines of it were.
    """
    runner = _tree_runner({"origin/main": MAIN, "origin/claude/abandoned": APPENDED})

    report = stranded(ROOT, {"PL-0001"}, runner=runner)

    assert report.items == ()
    assert [(edit.identifier, edit.branches) for edit in report.edits] == [
        ("PL-0001", ("origin/claude/abandoned",))
    ]
    assert report.edits[0].path == "docs/items/PL-0001-on-main.md"
    assert report.edits[0].base_path == "docs/items/PL-0001-on-main.md"


def test_a_branch_copy_the_base_has_closed_since_is_not_reported() -> None:
    """`PL-MBTZ`, as it ran on 2026-09-14 and as `PL-XLQ5` was actually dealt.

    `main` held `PL-THPB` at `done`, with a `closed:` date and a `verify:`;
    `origin/claude/next-version-release-o2zzaf` held the `untriaged` copy it
    had forked with. The branch carried nothing `main` lacked, and the reader
    was handed a `git checkout` of it - which restores an untriaged item over
    a closed one and discards everything the closure recorded.
    """
    runner = _tree_runner({"origin/main": CLOSED_ON_MAIN, "origin/claude/release": MAIN})

    report = stranded(ROOT, {"PL-0001"}, runner=runner)

    assert report.items == ()
    assert report.edits == ()


def test_a_branch_copy_the_base_has_only_added_to_is_not_reported() -> None:
    """The base holds every line the branch holds and more, so nothing is behind."""
    runner = _tree_runner({"origin/main": APPENDED, "origin/claude/older": MAIN})

    assert stranded(ROOT, {"PL-0001"}, runner=runner).edits == ()


def test_a_copy_the_base_has_held_and_moved_past_is_not_reported() -> None:
    """The base rewrote its own prose, so the branch holds lines the base lacks.

    On the text alone that is indistinguishable from the branch having written
    them, and it is the commonest shape in this store: 2,158 of the 2,180
    branch copies differing from `main` on 2026-09-21 are one the base has
    held. Reading them by text instead called 873 of them ahead.
    """
    rewritten = {"PL-0001-on-main.md": _document("PL-0001", "On main").replace("x", "rewritten")}
    trees = {"origin/main": rewritten, "origin/claude/older": MAIN}

    walked = stranded(ROOT, {"PL-0001"}, runner=_tree_runner(trees, history=tuple(MAIN.values())))
    unwalked = stranded(ROOT, {"PL-0001"}, runner=_tree_runner(trees))

    assert walked.edits == ()
    assert [edit.identifier for edit in unwalked.edits] == ["PL-0001"]


def test_an_edit_this_session_is_holding_is_not_reported_back_to_it() -> None:
    """`known_ids` applied to content: a copy `HEAD` holds is one the session can see."""
    runner = _tree_runner({"origin/main": MAIN, "claude/this-session": APPENDED, "HEAD": APPENDED})

    assert stranded(ROOT, {"PL-0001"}, runner=runner).edits == ()


def test_two_copies_that_each_carry_something_read_as_ahead() -> None:
    """Neither contains the other, and the reader is handed the diff either way.

    Calling this behind would hide the branch's half; the report says only
    that the branch has something the base has not, which is true of it.
    """
    base = _document("PL-0001", "On main") + "\nThe base's own paragraph.\n"
    ref = _document("PL-0001", "On main") + "\nThe branch's own paragraph.\n"

    assert _standing(base, ref) == "ahead"
    assert _standing(base, base) == "equal"


DIGEST_ITEM = """---
id: PL-0001
title: An item in the store
priority: P2
effort: S
status: ready
verify: uv run pytest
added: 2026-08-01
---

**Problem.** x
**Why it matters.** y
**Done when.** z
"""


def _store() -> Report:
    from docket.model import parse_item

    return Report(items=[parse_item(DIGEST_ITEM)])


def _digest(
    stranded: StrandedReport | None = None,
    flight: FlightReport | None = None,
    left: OrphanedReport | None = None,
) -> str:
    from docket.render import format_digest

    return format_digest(_store(), flight, None, None, stranded, (), left)


def test_the_digest_names_an_item_only_a_branch_holds() -> None:
    """The one line telling a session the queue it is reading is not all of it."""
    lost = StrandedItem(
        identifier="PL-K7QX",
        title="A lost thought",
        path="docs/items/PL-K7QX-lost.md",
        branches=("origin/claude/abandoned",),
    )

    stated = [
        line for line in _digest(StrandedReport(items=(lost,))).splitlines() if "PL-K7QX" in line
    ]

    assert len(stated) == 1
    assert "A lost thought" in stated[0]
    assert "bin/docket stranded" in stated[0]


def test_the_digest_stays_silent_when_nothing_is_only_on_a_branch() -> None:
    """It is resent on every turn, so it earns its line or does not take one."""
    assert "only on a branch" not in _digest(StrandedReport(refs_read=4))


# A checkout that read one ref and could not read another - the container this
# project's sessions run in, which on 2026-08-31 held exactly one such ref
# (`origin/Review_articles`) while `docket next` said nothing about it.
UNREAD = FlightReport(
    branches=(Branch(name="origin/claude/pl-k7qx-live", item_id="PL-K7QX"),),
    unreadable=("origin/claude/beyond-the-horizon-abcdef",),
    base=BASE,
)
READ = FlightReport(branches=UNREAD.branches, base=BASE)


def test_the_ids_a_caller_ranks_by_are_only_what_the_walk_could_prove() -> None:
    """The unread ref contributes no id, and the report still carries that it exists."""
    assert UNREAD.ids == {"PL-K7QX"}
    assert UNREAD.unreadable == ("origin/claude/beyond-the-horizon-abcdef",)


def test_the_digest_says_when_a_ref_went_unread() -> None:
    """The defect in one line: every session reads the digest, few run `flight`.

    Without it the digest names what is in flight and stays silent about the
    ref that may be carrying more, which reads as "nothing else is in flight"
    rather than as "one ref could not be asked".
    """
    stated = [
        line for line in _digest(flight=UNREAD).splitlines() if "could not be compared" in line
    ]

    assert len(stated) == 1
    assert "1 ref could not be compared with origin/main" in stated[0]
    assert "bin/docket flight" in stated[0]


def test_the_digest_stays_silent_when_every_ref_was_read() -> None:
    """It is resent on every turn, so it earns its line or does not take one."""
    assert "could not be compared" not in _digest(flight=READ)


def test_the_digest_names_a_ref_nothing_can_attribute() -> None:
    """It is the digest that has to carry it, and only in the case that earns it.

    Every session reads the digest and few run `flight`, which is the whole
    argument for the unread line above. The 2026-09-04 decline feared the
    mirror image - a line nobody acts on, resent on every turn - and the count
    that settled it is that no ref in this repository is unattributed today,
    with `tools/branch_id_check.py` holding that (`PL-B73C`).
    """
    unattributed = FlightReport(
        branches=UNREAD.branches, unattributed=("origin/Review_articles",), base=BASE
    )
    stated = [
        line
        for line in _digest(flight=unattributed).splitlines()
        if "attributable to no item" in line
    ]

    assert len(stated) == 1
    assert "origin/Review_articles" in stated[0]
    assert "file an item or delete the branch" in stated[0]


def test_the_digest_stays_silent_when_every_unlanded_ref_names_something() -> None:
    """The steady state, and the reason no suppression rule was built."""
    assert "attributable to no item" not in _digest(flight=READ)


def test_the_queue_listing_says_when_a_ref_went_unread() -> None:
    from docket.render import format_list

    assert "1 ref could not be compared with origin/main" in format_list(_store(), UNREAD)
    assert "could not be compared" not in format_list(_store(), READ)


def test_the_status_view_says_when_a_ref_went_unread() -> None:
    from docket.render import format_status

    assert "1 ref could not be compared with origin/main" in format_status(_store(), None, UNREAD)
    assert "could not be compared" not in format_status(_store(), None, READ)


def test_the_delegable_list_says_when_a_ref_went_unread() -> None:
    """Both halves of it: a worker handed a list, and a worker handed none."""
    from docket.render import format_delegable

    assert "1 ref could not be compared" in format_delegable(_store(), UNREAD, (), ())
    assert "1 ref could not be compared" in format_delegable(Report(items=[]), UNREAD, (), ())
    assert "could not be compared" not in format_delegable(_store(), READ, (), ())


def test_the_unread_line_counts_the_refs_and_names_where_they_are_listed() -> None:
    from docket.render import format_unread

    both = FlightReport(unreadable=("origin/one", "origin/two"), base=BASE)

    assert format_unread(both).startswith("2 refs could not be compared with origin/main")
    assert format_unread(both).endswith("`bin/docket flight` names them.")
    assert format_unread(FlightReport()) == ""


# The two routes into `unreadable`, on refs whose *names* answer the question
# their commits could not: no merge-base at all, and a walk that ran off the
# end of a grafted history.
NAMED_UNREADABLE = "origin/claude/pl-k7qx-live"
NAMED_RAN_OUT = "origin/claude/pl-k7qx-merged-main-in-abcdef"


def test_a_ref_with_no_readable_merge_base_still_contributes_the_id_its_name_carries() -> None:
    """The id a branch name carries needs no history, so declining it declines nothing.

    Dropping it means `docket next` offers an item a live session is holding,
    which is the collision the whole read exists to prevent - and the branch
    named for its item is the case where the checkout knew the answer.
    """
    report = branches_in_flight(
        ROOT, runner=_runner([NAMED_UNREADABLE], unrelated=(NAMED_UNREADABLE,))
    )

    assert [branch.item_id for branch in report.branches] == ["PL-K7QX"]
    assert report.unreadable == (NAMED_UNREADABLE,)
    assert report.branches[0].last_commit is None


def test_a_ref_that_ran_off_the_end_of_its_walk_contributes_its_name_id_and_no_other() -> None:
    """The halves are separable, and this is the case that proves it.

    The walk over this ref reached round the graft into the default branch's
    own commits, so `PL-M0J2` is exactly the id `PL-MGNC` stopped believing.
    The name's `PL-K7QX` was never in doubt. One survives and one does not.
    """
    report = branches_in_flight(
        ROOT,
        runner=_runner(
            [NAMED_RAN_OUT], commits={NAMED_RAN_OUT: RAN_OFF_THE_END}, ran_out=(NAMED_RAN_OUT,)
        ),
    )

    assert [branch.item_id for branch in report.branches] == ["PL-K7QX"]
    assert report.unreadable == (NAMED_RAN_OUT,)


def test_a_ref_whose_name_carries_no_id_contributes_nothing_when_it_goes_unread() -> None:
    """The harness-named branch, which is why the commit read exists at all."""
    report = branches_in_flight(ROOT, runner=_runner([TRUNCATED], unrelated=(TRUNCATED,)))

    assert report.branches == ()
    assert report.unreadable == (TRUNCATED,)


def test_a_landed_branch_contributes_nothing_however_its_name_reads() -> None:
    """The name is evidence of the item, never of the work being unfinished.

    A ref the default branch already contains never reaches the read, so
    reporting a name-proved id cannot resurrect finished work - which is what
    makes the landedness the cheaper uncertainty on the ref above.
    """
    found = _in_flight([NAMED_UNREADABLE], merged=[NAMED_UNREADABLE])

    assert found == ()


def test_flight_names_a_ref_that_contributes_by_name_in_both_halves() -> None:
    """One ref, two lines, and neither claims what the other says.

    The table carries the id its name proved; the block below says the commits
    went unread. A reader who saw only the first would think the ref had been
    read, and one who saw only the second would think it said nothing.
    """
    from docket.render import format_flight

    report = branches_in_flight(
        ROOT, runner=_runner([NAMED_UNREADABLE], unrelated=(NAMED_UNREADABLE,))
    )
    printed = format_flight(report, datetime(2026, 8, 31, tzinfo=UTC))

    assert f"PL-K7QX  {NAMED_UNREADABLE}" in printed
    assert "no commit of its own this checkout can read" in printed
    assert "so what its commits carry is unknown" in printed
    assert printed.count(NAMED_UNREADABLE) == 2


# --- read perfectly well, and attributable to nothing ------------------------


UNNAMED = "origin/Review_articles"


def test_a_ref_naming_no_item_anywhere_is_reported_as_unattributed() -> None:
    """The third outcome of the read, which used to be dropped (`PL-B73C`).

    `origin/Review_articles` is the shape: one commit ahead of the base from
    before the `claude/` convention, no id in the name, none at the front of
    its subject. It was read without difficulty and named nowhere.
    """
    report = _report([UNNAMED], commits={UNNAMED: [("1", "Added review articles on math models")]})

    assert report.unattributed == (UNNAMED,)
    assert report.branches == ()
    assert report.unreadable == ()


def test_a_queue_only_push_is_attributable_even_though_it_claims_nothing() -> None:
    """The discriminator the whole reading rests on.

    A capture, a triage pass and a `docket record` write are all withheld from
    `branches` by `_annotates_only` - they name an item they are not working.
    They are still *attributable*, and reading them as unattributed would put a
    line in every session for the most routine push this project makes.
    """
    ref = "claude/loving-ride-mo6njm"
    report = _report(
        [ref],
        commits={ref: [("1", "PL-XR8K: close the tag item", "c1", "docs/items/PL-XR8K-tag.md")]},
    )

    assert report.branches == (), "a queue-only diff still claims nothing"
    assert report.unattributed == (), "but the ref names the item it concerns"


def test_a_ref_named_for_its_item_is_never_unattributed() -> None:
    """The name is read whatever the subjects say, so it settles this too."""
    report = _report(
        ["claude/pl-k7qx-do-the-thing"],
        commits={"claude/pl-k7qx-do-the-thing": [("1", "wip, no id in the subject")]},
    )

    assert report.unattributed == ()


def test_an_unread_ref_is_not_called_unattributed() -> None:
    """Absence of an id has to be read, never assumed from a walk that stopped.

    A ref whose commits this checkout could not reach contributes no subjects
    at all, so calling it unattributed would be inventing the absence rather
    than reading it - the same overclaim `unreadable` exists to prevent.
    """
    report = branches_in_flight(ROOT, runner=_runner([TRUNCATED], unrelated=(TRUNCATED,)))

    assert report.unreadable == (TRUNCATED,)
    assert report.unattributed == ()


def test_a_local_branch_and_its_tracking_ref_are_one_unattributed_line() -> None:
    """`--source` credits a commit to whichever ref it reached first.

    So the two sides are collapsed before they are compared. Without it a
    branch whose commits git credited to its tracking ref reads as naming
    nothing, and the live session running this check reported its own branch.
    """
    report = _report(["work", "origin/work"], commits={"origin/work": [("1", "no id anywhere")]})

    assert report.unattributed == ("work",)


def test_flight_names_an_unattributed_ref_and_says_no_guard_can_see_it() -> None:
    from docket.render import format_flight

    report = _report([UNNAMED], commits={UNNAMED: [("1", "Added review articles on math models")]})
    printed = format_flight(report, datetime(2026, 8, 31, tzinfo=UTC))

    assert "1 ref carries no item id" in printed
    assert "no guard in this repository can see it" in printed
    assert UNNAMED in printed


def _commits(*entries: tuple[str, str, str, str, str]) -> str:
    """A symmetric difference as `git log --left-right --format=%m..%p..%s` prints it.

    Oldest first, which is what `--topo-order --reverse` gives and what the
    rewrite rule reads: `<` for a commit only the base holds, `>` for one only
    the branch holds. The parent field carries one hash for an ordinary commit
    and two for a merge.
    """
    return "".join("\0".join(entry) + "\n" for entry in entries)


def _branch_runner(
    branch: str = "claude/pl-k7qx-live",
    behind: int = 0,
    ahead: int = 0,
    landed: tuple[str, ...] = (),
    unrelated: bool = False,
    base_exists: bool = True,
    divergence: str = "",
):
    """A git holding one checked-out branch at a known position against the base.

    `unrelated` is the case the counts guard exists for: `merge-base` finds
    nothing, and `rev-list --left-right --count` would still answer - with the
    length of each side of two unrelated histories, which reads exactly like a
    position. `divergence` is what the symmetric difference holds, which is a
    different read and the one that tells a rewrite from a fork.
    """

    def run(args: list[str], root: Path) -> str:
        if args[:3] == ["rev-parse", "--abbrev-ref", "HEAD"]:
            return f"{branch}\n"
        if args[0] == "rev-parse":
            return f"{args[-1]}\n" if args[-1] == BASE and base_exists else ""
        if args[0] == "merge-base":
            return "" if unrelated else "0123456789abcdef\n"
        if args[0] == "rev-list":
            return f"{behind}\t{ahead}\n"
        if args[:2] == ["log", "--topo-order"]:
            return divergence
        if args[0] == "log":
            return "\n".join(f"{identifier} Something that landed" for identifier in landed)
        return ""

    return run


def test_branch_state_reports_the_position_when_the_base_has_not_moved() -> None:
    state = branch_state(ROOT, runner=_branch_runner(ahead=2))

    assert state.disposition == "current"
    assert (state.branch, state.base, state.behind, state.ahead) == (
        "claude/pl-k7qx-live",
        BASE,
        0,
        2,
    )
    assert state.landed == ()


def test_branch_state_says_restart_when_the_branch_is_behind_with_nothing_of_its_own() -> None:
    """Its work merged or it never had any, and `checkout -B` is safe either way."""
    state = branch_state(ROOT, runner=_branch_runner(behind=4))

    assert state.disposition == "restart"


def test_branch_state_says_merge_when_the_branch_is_behind_and_carrying_work() -> None:
    """The case that costs the rework cycle: work of its own, on a base that moved."""
    state = branch_state(ROOT, runner=_branch_runner(behind=4, ahead=2))

    assert state.disposition == "merge"


def test_branch_state_says_pull_on_the_default_branch_itself() -> None:
    state = branch_state(ROOT, runner=_branch_runner(branch="main", behind=3))

    assert state.disposition == "pull"
    assert state.is_default


def test_branch_state_declines_rather_than_counting_two_unrelated_histories() -> None:
    """`rev-list --left-right --count` does not fail on refs sharing no history.

    It reports the whole length of each side, which reads like a position and
    is not one - and a fabricated "98 ahead" argues against merging in exactly
    the case the line exists to catch. So the fork point is proven first.
    """
    state = branch_state(ROOT, runner=_branch_runner(behind=98, ahead=98, unrelated=True))

    assert state.disposition == ""
    assert "shares no readable history" in state.declined
    assert (state.behind, state.ahead) == (0, 0)


def test_branch_state_names_the_items_that_landed_while_the_branch_sat() -> None:
    """The counts say the base moved; this says what moved, which is the question."""
    state = branch_state(
        ROOT, runner=_branch_runner(behind=2, ahead=1, landed=("PL-K7QX", "PL-9Y42"))
    )

    assert state.landed == ("PL-K7QX", "PL-9Y42")


# --- a rewritten history, which the counts alone read as ordinary divergence -
#
# `filter-repo` and `filter-branch` rebuild every commit, so a branch left on
# the old history is counted as hundreds behind *and* hundreds ahead. Merging,
# resetting or `checkout -B` onto the base - the three things that count
# invites - each lose whatever the branch pushed into the rewrite's window,
# which is the incident behind `PL-YGF3`.

REWRITE = _commits(
    ("<", "aaa1111", "1788256800", "p0", "PL-0001 The first commit"),
    (">", "bbb1111", "1788256800", "p0", "PL-0001 The first commit"),
    ("<", "aaa2222", "1788343200", "aaa1111", "PL-0002 The second commit"),
    (">", "bbb2222", "1788343200", "bbb1111", "PL-0002 The second commit"),
    ("<", "aaa3333", "1788688800", "aaa2222", "PL-9Y42 Landed after the rewrite"),
    (">", "bbb3333", "1788602400", "bbb2222", "PL-K7QX Capture what only this branch holds"),
)


def test_a_rewritten_base_is_told_apart_from_a_branch_that_is_merely_behind() -> None:
    """The divergence begins in commits the base also holds, under other hashes.

    Same author date and same subject on both sides: that is what a rewrite
    preserves and what a fork cannot fabricate. What is left over - here one
    capture - is the only copy of itself anywhere.
    """
    state = branch_state(ROOT, runner=_branch_runner(behind=3, ahead=3, divergence=REWRITE))

    assert state.disposition == REWRITTEN
    assert state.rewrite is not None
    assert state.rewrite.duplicated == 2
    assert state.rewrite.own == (("bbb3333", "PL-K7QX Capture what only this branch holds"),)
    assert state.rewrite.total == 3


def test_an_ordinary_divergence_makes_no_rewrite_claim() -> None:
    """A branch that sat while the base moved matches nothing, and merging is right."""
    ordinary = _commits(
        (">", "bbb1111", "1788256800", "p0", "PL-K7QX Do the thing"),
        ("<", "aaa2222", "1788343200", "p0", "PL-9Y42 Validate wash-in"),
    )
    state = branch_state(ROOT, runner=_branch_runner(behind=1, ahead=1, divergence=ordinary))

    assert state.rewrite is None
    assert state.disposition == "merge"


def test_a_commit_cherry_picked_from_the_base_is_not_a_rewritten_history() -> None:
    """The rule reads the *oldest* divergent commit, not any duplicate anywhere.

    A branch that forked, did its own work and then took a commit from the base
    holds a duplicate too. It is not on stale history, and telling it to
    cherry-pick its way onto a new base would be an answer to a question it
    does not have.
    """
    picked = _commits(
        (">", "bbb1111", "1788256800", "p0", "PL-K7QX Do the thing"),
        ("<", "aaa2222", "1788343200", "p0", "PL-9Y42 Validate wash-in"),
        (">", "bbb2222", "1788343200", "bbb1111", "PL-9Y42 Validate wash-in"),
    )
    state = branch_state(ROOT, runner=_branch_runner(behind=1, ahead=2, divergence=picked))

    assert state.rewrite is None
    assert state.disposition == "merge"


def test_a_rewrite_with_no_fork_point_is_reported_rather_than_declined() -> None:
    """The usual shape, and the one the fork-point guard used to swallow whole.

    Measured 2026-09-06: a `filter-branch --index-filter` rewrite of a
    four-commit repository leaves *no* merge base, so this arrived at the
    decline about a `--depth` fetch - advice that does nothing to a rewritten
    clone, and that leaves the reader holding the reflex the item is about.
    Proving the two sides are one duplicated history is what makes the counts
    mean something here.
    """
    state = branch_state(
        ROOT, runner=_branch_runner(behind=3, ahead=3, unrelated=True, divergence=REWRITE)
    )

    assert state.disposition == REWRITTEN
    assert state.declined == ""
    assert (state.behind, state.ahead) == (3, 3)
    # Nothing "landed" across a history this one shares no commit with.
    assert state.landed == ()


def test_two_commits_sharing_a_date_and_a_subject_match_one_on_the_base_once() -> None:
    """Under-reporting what is held only here is the failure that costs commits."""
    repeated = _commits(
        ("<", "aaa1111", "1788256800", "p0", "Fix the typo"),
        (">", "bbb1111", "1788256800", "p0", "Fix the typo"),
        (">", "bbb2222", "1788256800", "bbb1111", "Fix the typo"),
    )
    state = branch_state(ROOT, runner=_branch_runner(behind=1, ahead=2, divergence=repeated))

    assert state.rewrite is not None
    assert state.rewrite.own == (("bbb2222", "Fix the typo"),)


def test_the_rewritten_branch_line_replaces_the_advice_that_would_lose_the_work() -> None:
    """Both ordinary commands are destructive here, so neither is offered."""
    from docket.render import format_branch_state

    printed = format_branch_state(
        BranchState(
            branch="claude/pl-k7qx-live",
            base=BASE,
            behind=699,
            ahead=703,
            fetched=True,
            rewrite=RewriteReport(
                duplicated=702, own=(("2966d9b", "PL-8PS6 Capture the fresh gas flow range"),)
            ),
        )
    )

    assert "rewritten history, not divergence" in printed
    assert "2966d9b PL-8PS6 Capture the fresh gas flow range" in printed
    assert "git checkout -B claude/pl-k7qx-live-rewritten origin/main" in printed
    assert "git cherry-pick 2966d9b" in printed
    # Tags are the half a branch-only cleanup misses: they still point into the
    # old history, and `git fetch` will not move one that already exists.
    assert "git fetch --tags --force origin" in printed
    assert f"git merge {BASE}" not in printed
    assert "git checkout -B claude/pl-k7qx-live origin/main" not in printed


def test_every_commit_held_only_here_is_listed_and_picked() -> None:
    """A truncated recovery command is the failure this whole report prevents.

    It would look complete and drop exactly what it was printed to save, and no
    shorter honest form exists: no git command lists the commits held only
    here, because telling them from the duplicated ones is the read this module
    just did.
    """
    from docket.render import format_branch_state

    own = tuple((f"c{index:07d}", f"PL-000{index} Commit {index}") for index in range(9))
    printed = format_branch_state(
        BranchState(
            branch="claude/pl-k7qx-live",
            base=BASE,
            behind=40,
            ahead=49,
            fetched=True,
            rewrite=RewriteReport(duplicated=40, own=own),
        )
    )

    assert all(f"{short} {subject}" in printed for short, subject in own)
    picked = next(line for line in printed.splitlines() if "cherry-pick" in line)
    assert all(short in picked for short, _ in own)


def test_a_merge_commit_held_only_here_says_what_cherry_pick_needs() -> None:
    """`git cherry-pick` refuses a merge without `-m`, and one of the two commits
    the incident lost was the merge that resolved the branch's conflicts."""
    from docket.render import format_branch_state

    printed = format_branch_state(
        BranchState(
            branch="claude/pl-k7qx-live",
            base=BASE,
            behind=9,
            ahead=11,
            fetched=True,
            rewrite=RewriteReport(
                duplicated=9,
                own=(("2966d9b", "Merge origin/main into claude/pl-k7qx-live"),),
                merges=True,
            ),
        )
    )

    assert "cherry-pick -m 1" in printed


def test_a_rewrite_the_branch_added_nothing_to_is_moved_across_whole() -> None:
    """A local copy of the default branch left on the old history: nothing to save."""
    from docket.render import format_branch_state

    printed = format_branch_state(
        BranchState(
            branch="main",
            base=BASE,
            behind=700,
            ahead=699,
            fetched=True,
            rewrite=RewriteReport(duplicated=699),
        )
    )

    assert "Nothing is held only here" in printed
    assert f"git checkout -B main {BASE}" in printed
    assert "git fetch --tags --force origin" in printed
    assert "cherry-pick" not in printed


def test_branch_state_declines_on_a_detached_head() -> None:
    state = branch_state(ROOT, runner=lambda args, root: "HEAD\n")

    assert state.disposition == ""
    assert "no branch is checked out" in state.declined


def test_branch_state_declines_when_the_checkout_has_no_base_to_compare() -> None:
    state = branch_state(ROOT, runner=_branch_runner(base_exists=False))

    assert state.disposition == ""
    assert state.declined


def test_the_branch_state_line_prints_the_command_for_each_state() -> None:
    """The recovery command is printed, never run: `checkout -B` discards commits."""
    from docket.render import format_branch_state

    restart = format_branch_state(BranchState(branch="claude/pl-k7qx-live", base=BASE, behind=4))
    merge = format_branch_state(
        BranchState(branch="claude/pl-k7qx-live", base=BASE, behind=4, ahead=2, fetched=True)
    )

    assert "git checkout -B claude/pl-k7qx-live origin/main" in restart
    assert f"git merge {BASE}" in merge
    assert "rebase" not in restart + merge


def test_the_branch_state_line_says_when_nothing_refreshed_the_base() -> None:
    """A position measured against a ref nobody refreshed is a report, not a claim."""
    from docket.render import format_branch_state

    stale = format_branch_state(BranchState(branch="main", base=BASE, behind=1))
    fresh = format_branch_state(BranchState(branch="main", base=BASE, behind=1, fetched=True))

    assert "nothing refreshed origin/main" in stale
    assert "nothing refreshed" not in fresh


# --- which pull request a landed closure's own merge commit names ------------
#
# The number does not exist when the closure is committed - it travels with its
# work, which is what stops a merge taking the fix and leaving the item open -
# so a closure that reaches the default base carrying no `pr` is the normal
# shape of a successful merge, not a gap. Whether the provenance is actually
# lost is decided by whether the merge commit still names the number.

CLOSED = "---\nid: {id}\ntitle: T\nstatus: done\n---\n"


OPEN_ITEM = "---\nid: {id}\ntitle: T\nstatus: ready\n---\n"


#: The same two, declaring where the item's work lives. Only the readings that
#: ask for `touches` need them - `_declares_queue_only` here, and
#: `_queue_only_work` a level up - so the bare pair stay the default and a test
#: that says nothing about `touches` is a test about an item that declares none.
CLOSED_DECLARING = "---\nid: {id}\ntitle: T\nstatus: done\ntouches: {touches}\n---\n"


OPEN_DECLARING = "---\nid: {id}\ntitle: T\nstatus: ready\ntouches: {touches}\n---\n"


def _z_name_status(entries: tuple[tuple[str, str, list[str]], ...]) -> str:
    """What git writes for `log --format=%H%x1f%s -z --name-status`.

    `entries` is newest first, as (revision, subject, name-status fields). The
    `-z` stream NUL-terminates every field, which leaves the format output's own
    newline at the front of the status token that follows it - so a reader
    splitting on NUL meets the subject, then `\nM` or `\nR100`, then the path or
    the pair of them. Checked against this repository's own history rather than
    remembered, because the walk under test is parsing it.
    """
    if not entries:
        return ""
    fields = [
        field
        for revision, subject, entry in entries
        for field in (f"{revision}\x1f{subject}", "\n" + "\0".join(entry))
    ]
    return "\0".join(fields) + "\0"


def _closure_runner(
    on_base: dict[str, str],
    subjects: tuple[str, ...] = (),
    log: list[list[str]] | None = None,
    shallow: str = "",
    closed_from: int = 0,
    file_history: tuple[str, ...] = (),
    depth: int | None = None,
):
    """A git holding `on_base` (file name to text) and a default branch of `subjects`.

    `subjects` is newest-first, as `git log` gives it, and each is given the
    revision `c<index>` so that `c0^` resolves to `c1` the way a real parent
    does. `closed_from` is the index from which the items read `status: done`,
    so the default of 0 makes the newest subject the closure - the healthy
    shape, where the commit that landed the work is also the one that wrote the
    closure. A test wanting the defect shape says `closed_from=1` or more: the
    newest commit naming the item then finds it *already* closed, which is what
    a bookkeeping merge or a follow-up fix looks like.

    `shallow` is what `rev-parse --is-shallow-repository` answers - "true",
    "false", or the empty string for a git that will not say, which is the
    default because most cases here are about reading the base rather than
    about depth.

    `depth` is how many commits from the tip this checkout holds, which decides
    whether `c<i>^` resolves. The default of `None` means it always does - the
    revisions are a window on a history that continues below them, which is
    what every test here meant before a depth could be expressed. A number
    makes `c<depth-1>` the graft boundary of a shallow clone, whose parent git
    does not hold and which therefore cannot be compared against anything.

    `file_history` is the item file's own log, which the fallback reads when
    the subject scan cannot answer. It defaults to empty rather than to
    `subjects`, because the two are different questions - a commit can name an
    item in its subject without touching its file, and vice versa - and
    conflating them let a subject about another item answer through the
    fallback. `_recovery_runner` is the fake for tests about that path.
    """

    def index_of(revision: str) -> int | None:
        """The index a revision names, following one `^` to its parent."""
        parents = 0
        while revision.endswith("^"):
            revision, parents = revision[:-1], parents + 1
        if not revision.startswith("c") or not revision[1:].isdigit():
            return None
        return int(revision[1:]) + parents

    def run(args: list[str], root: Path) -> str:
        if log is not None:
            log.append(args)
        if args[0] == "rev-parse":
            if args[-1] == "--is-shallow-repository":
                return f"{shallow}\n" if shallow else ""
            if args[-1] == BASE:
                return f"{BASE}\n"
            if args[-1].endswith("^^{commit}"):  # is this revision's parent in reach?
                index = index_of(args[-1].removesuffix("^{commit}"))
                if index is None or (depth is not None and index >= depth):
                    return ""
                return f"c{index}\n"
            return ""
        if args[0] == "for-each-ref":
            return f"{BASE}\n"
        if args[0] == "diff" and "--name-only" in args:
            # The paths a commit changed, which is what tells a closure that
            # landed with its work from one that landed without it. These
            # histories are the healthy shape - the commit that wrote the
            # closure also carried the code - so every commit names work.
            return "src/changed.py\n"
        if args[0] == "show":
            revision, _, path = args[-1].partition(":")
            name = path.split("/")[-1]
            text = on_base.get(name, "")
            if revision == BASE or not text:
                return text
            index = index_of(revision)
            if index is None or index >= len(subjects):
                return ""
            identifier = name.split("-")[0]
            return text if index <= closed_from else OPEN_ITEM.format(id=identifier)
        if args[0] == "log":
            if "--" not in args:
                return "\n".join(f"c{index}\x1f{subject}" for index, subject in enumerate(subjects))
            return _z_name_status(
                tuple(
                    (f"c{index}", subject, ["M", args[-1]])
                    for index, subject in enumerate(file_history)
                )
            )
        return ""

    return run


def _recovery_runner(
    history: tuple[tuple[str, str], ...],
    done_at: set[str],
    name: str,
    carried: tuple[str, ...] | None = None,
    declares: str = "",
):
    """A git whose base subjects name no id, so only the file's history answers.

    `history` is the file's own log, newest first, as (revision, subject).
    `done_at` names the revisions whose tree has the item closed - written as
    revisions rather than derived, so a test can say exactly where the status
    flipped, including at a parent the walk has to look at.

    `declares` is the `touches` the item carries in every tree read here. It is
    what tells a closure that landed without its work from the landing of an
    item whose work *is* the queue, so a test that leaves it empty is a test
    about an item that has declared nothing (`PL-YFXG`).
    """

    def run(args: list[str], root: Path) -> str:
        if args[0] == "rev-parse":
            return "" if args[-1] == "--is-shallow-repository" else f"{BASE}\n"
        if args[0] == "for-each-ref":
            return f"{BASE}\n"
        if args[0] == "diff" and "--name-only" in args:
            # The paths a commit changed: these histories are all the healthy
            # shape, where the commit that wrote the closure carried the work.
            # A test about a closure that landed alone says so by naming only
            # the item file here.
            return "\n".join(carried) if carried is not None else "src/changed.py\n"
        if args[0] == "show":
            revision, _, _path = args[-1].partition(":")
            done = revision == BASE or revision in done_at
            if declares:
                template = CLOSED_DECLARING if done else OPEN_DECLARING
                return template.format(id="PL-K7QX", touches=declares)
            return CLOSED.format(id="PL-K7QX") if done else OPEN_ITEM.format(id="PL-K7QX")
        if args[0] == "log":
            if "--" in args:
                return _z_name_status(
                    tuple((revision, subject, ["M", args[-1]]) for revision, subject in history)
                )
            # The base's own subjects, naming no id - the case this recovers.
            return "Design the thing and fix the checks (#220)"
        return ""

    return run


def test_a_squash_subject_naming_no_id_is_recovered_from_the_item_s_file() -> None:
    # PL-2XTF: #220 was created from the UI, closed three items, and its title
    # led with no id. The subject scan finds nothing; the file's own history is
    # what still knows, because the commit that wrote `status: done` is the
    # closure and carries `(#N)` like every other squash.
    run = _recovery_runner(
        history=(("aaa111", "Design the thing and fix the checks (#220)"),),
        done_at={"aaa111"},
        name="PL-K7QX-a.md",
    )

    report = closures_on_base(ROOT, {"PL-K7QX": "PL-K7QX-a.md"}, runner=run)

    assert report.landed == frozenset({"PL-K7QX"})
    assert report.numbers == {"PL-K7QX": 220}


def test_a_closure_split_from_its_work_records_no_pull_request() -> None:
    """A closure that landed without its work names the wrong pull request, so it names none.

    Where the work and the closure landed in *different* pull requests, the
    commit that wrote `status: done` carries the closure and none of the code -
    so `pr:` would record a change whose diff does not contain the work the item
    describes. `commit:` was retired (`PL-T63T`), so `pr` is the only surviving
    link to the work and a wrong one is worse than an absent one (`PL-YDL6`).

    Audited over real history while fixing `PL-S5LB`: 249 of the 252 closures
    this can answer agree with what the store recorded, and all three that
    disagree are this shape, each off by one - `#128` did `PL-3CBS`'s work and
    left the item at `status: ready`, and the triage pass that merged as `#129`
    wrote the closure. The store already holds the better answer in all three,
    so declining loses nothing that was ever right.

    Declining rather than guessing which pull request held the work: nothing here
    knows which files an item's work was, and `PL-99Y4` settled that a provenance
    question the checkout cannot answer is reported rather than invented.
    """
    run = _recovery_runner(
        history=(("ccc333", "Triage the open captures (#129)"),),
        done_at={"ccc333"},
        name="PL-K7QX-a.md",
        carried=("docs/items/PL-K7QX-a.md",),
    )

    report = closures_on_base(ROOT, {"PL-K7QX": "PL-K7QX-a.md"}, runner=run)

    assert report.landed == frozenset({"PL-K7QX"})
    assert report.numbers == {}


def test_a_queue_only_closure_supplies_its_pr() -> None:
    """An item whose declared work is the queue carried it, whatever its diff looks like.

    The test above is right about the hazard and was wrong about the shape. A
    commit changing nothing outside `docs/items/` is a closure separated from
    its work only where the work was somewhere else to begin with; for a
    release-tag item, a triage pass, a stranded recovery or a rename pass it is
    what landing correctly looks like, and `.claude/skills/docket/SKILL.md`
    names that as a standing category under **Mode: start an item**.

    `PL-YTDN` is the worked example and this is its shape: its whole deliverable
    was renaming drifted item files, so `#712` changed 12 files and every one
    of them was an item. The number was declined, `docket check` raised its
    error rather than its recoverable advisory, and `origin/main` failed `make
    check` on every branch cut from it - with nothing to clear it, since the
    bare `bin/docket record` writes only what the base can supply and this was
    a number it had decided it could not (`PL-YFXG`).

    Audited over real history before it was adopted: across the 927 closed
    items on `origin/main`, this changes 29 answers and every one of the 29
    matches the `pr` the store already holds, recorded by hand or by the
    explicit `--merge` escape. No answer that was already right changes, which
    is the half the `PL-YDL6` guard was built to protect.
    """
    run = _recovery_runner(
        history=(("ddd444", "PL-K7QX: rename the drifted item files (#712)"),),
        done_at={"ddd444"},
        name="PL-K7QX-a.md",
        carried=("docs/items/PL-K7QX-a.md", "docs/items/PL-B1C2-renamed.md"),
        declares="docs/items/",
    )

    assert closures_on_base(ROOT, {"PL-K7QX": "PL-K7QX-a.md"}, runner=run).numbers == {
        "PL-K7QX": 712
    }


def test_an_item_declaring_one_other_item_s_file_is_queue_only_work_too() -> None:
    # The declaration names a path *inside* the queue rather than the directory
    # itself, which is how an item whose work is one other item's file writes
    # it - `PL-GBBZ` declares four of them, `PL-X7VY` one. Both are in the 29.
    run = _recovery_runner(
        history=(("ddd444", "PL-K7QX: repair the stale brief (#434)"),),
        done_at={"ddd444"},
        name="PL-K7QX-a.md",
        carried=("docs/items/PL-B1C2-another.md",),
        declares="docs/items/PL-B1C2-another.md",
    )

    assert closures_on_base(ROOT, {"PL-K7QX": "PL-K7QX-a.md"}, runner=run).numbers == {
        "PL-K7QX": 434
    }


def test_a_declaration_reaching_outside_the_queue_still_records_nothing() -> None:
    # The exemption is the item's own word for where its work lives, so one
    # path outside the queue withdraws it and the `PL-YDL6` reading stands.
    # `PL-21GS` is the shape: `docs/items/, docs/releases/`.
    run = _recovery_runner(
        history=(("ccc333", "PL-K7QX: triage the open captures (#129)"),),
        done_at={"ccc333"},
        name="PL-K7QX-a.md",
        carried=("docs/items/PL-K7QX-a.md",),
        declares="docs/items/, docs/releases/",
    )

    assert closures_on_base(ROOT, {"PL-K7QX": "PL-K7QX-a.md"}, runner=run).numbers == {}


def test_a_diff_this_checkout_cannot_read_declines_whatever_the_item_declares() -> None:
    # Silence is not evidence that the work was a queue edit. A commit with no
    # paths at all is a merge or a read that went wrong, and an absent `pr` is
    # a transcription still owed where a wrong one is a false provenance.
    run = _recovery_runner(
        history=(("ddd444", "PL-K7QX: rename the drifted item files (#712)"),),
        done_at={"ddd444"},
        name="PL-K7QX-a.md",
        carried=(),
        declares="docs/items/",
    )

    assert closures_on_base(ROOT, {"PL-K7QX": "PL-K7QX-a.md"}, runner=run).numbers == {}


def test_a_later_edit_to_a_closed_item_does_not_steal_the_attribution() -> None:
    # Backfilling a `pr`, or correcting a brief, touches the file long after
    # the work landed and carries its own number. Recording one of those would
    # be a false provenance, which is worse than the missing one.
    run = _recovery_runner(
        history=(
            ("ccc333", "Correct the brief (#226)"),
            ("aaa111", "Design the thing and fix the checks (#220)"),
        ),
        done_at={"ccc333", "ccc333^", "aaa111"},
        name="PL-K7QX-a.md",
    )

    assert closures_on_base(ROOT, {"PL-K7QX": "PL-K7QX-a.md"}, runner=run).numbers == {
        "PL-K7QX": 220
    }


def test_an_item_whose_file_history_names_no_number_still_reports_nothing() -> None:
    run = _recovery_runner(
        history=(("aaa111", "no number here"),), done_at={"aaa111"}, name="PL-K7QX-a.md"
    )

    assert closures_on_base(ROOT, {"PL-K7QX": "PL-K7QX-a.md"}, runner=run).numbers == {}


def test_the_file_history_is_not_read_when_a_subject_already_answered() -> None:
    # The subject scan is one history read for the whole set; the fallback is
    # one per unanswered id. Paying for it when nothing is missing would make
    # the cheap path cost the same as the expensive one.
    log: list[list[str]] = []
    run = _closure_runner(
        {"PL-K7QX-a.md": CLOSED.format(id="PL-K7QX")}, ("PL-K7QX Do the thing (#148)",), log
    )

    assert closures_on_base(ROOT, {"PL-K7QX": "PL-K7QX-a.md"}, runner=run).numbers == {
        "PL-K7QX": 148
    }
    assert not [args for args in log if args[0] == "log" and "--" in args]


def test_a_landed_closure_reports_the_pull_request_its_merge_commit_names() -> None:
    run = _closure_runner(
        {"PL-K7QX-a.md": CLOSED.format(id="PL-K7QX")},
        ("PL-K7QX Do the thing (#148)", "PL-B1C2 Something earlier (#140)"),
    )
    report = closures_on_base(ROOT, {"PL-K7QX": "PL-K7QX-a.md"}, runner=run)

    assert report.landed == frozenset({"PL-K7QX"})
    assert report.numbers == {"PL-K7QX": 148}


def test_one_merge_closing_two_items_answers_for_both() -> None:
    # A subject may open with a run of ids, because one branch may carry two
    # items. Both closed in the same pull request, so both name it.
    run = _closure_runner(
        {"PL-K7QX-a.md": CLOSED.format(id="PL-K7QX"), "PL-B1C2-b.md": CLOSED.format(id="PL-B1C2")},
        ("PL-K7QX, PL-B1C2: two items at once (#151)",),
    )
    report = closures_on_base(
        ROOT, {"PL-K7QX": "PL-K7QX-a.md", "PL-B1C2": "PL-B1C2-b.md"}, runner=run
    )

    assert report.numbers == {"PL-K7QX": 151, "PL-B1C2": 151}


def test_the_merge_that_landed_the_work_wins_over_the_commit_that_filed_it() -> None:
    # An id leads more than one subject in a healthy history: the capture that
    # filed the item, then the merge that landed it. Newest first from `git
    # log`, so the merge is what is recorded.
    run = _closure_runner(
        {"PL-K7QX-a.md": CLOSED.format(id="PL-K7QX")},
        ("PL-K7QX Do the thing (#148)", "PL-K7QX Capture the idea (#131)"),
    )
    assert closures_on_base(ROOT, {"PL-K7QX": "PL-K7QX-a.md"}, runner=run).numbers == {
        "PL-K7QX": 148
    }


def test_a_merge_naming_no_pull_request_derives_nothing() -> None:
    # A repository merging without pull requests, or a subject written by
    # hand. Deriving nothing is an answer, and the caller keeps its error.
    run = _closure_runner({"PL-K7QX-a.md": CLOSED.format(id="PL-K7QX")}, ("PL-K7QX Do the thing",))
    report = closures_on_base(ROOT, {"PL-K7QX": "PL-K7QX-a.md"}, runner=run)

    assert report.landed == frozenset({"PL-K7QX"})
    assert report.numbers == {}


def test_a_merge_the_truncated_history_no_longer_holds_derives_nothing() -> None:
    run = _closure_runner({"PL-K7QX-a.md": CLOSED.format(id="PL-K7QX")}, ())
    assert closures_on_base(ROOT, {"PL-K7QX": "PL-K7QX-a.md"}, runner=run).numbers == {}


def test_a_closure_that_has_not_landed_is_asked_nothing_about_its_number() -> None:
    run = _closure_runner({}, ("PL-K7QX Do the thing (#148)",))
    report = closures_on_base(ROOT, {"PL-K7QX": "PL-K7QX-a.md"}, runner=run)

    assert report.landed == frozenset()
    assert report.numbers == {}


def test_no_closure_in_question_costs_no_history_read() -> None:
    # The walk is the one added cost, so it is not paid where there is nothing
    # to answer for - which is every run on a store with no closure in flight.
    log: list[list[str]] = []
    closures_on_base(ROOT, {}, runner=_closure_runner({}, (), log))

    assert not [args for args in log if args[0] == "log"]


def test_a_rider_closure_recovers_the_pull_request_that_closed_it() -> None:
    # PL-GW37. An item closed as a rider on another item's pull request is not
    # named by that subject, so the newest subject naming it is something
    # older - here the triage that filed it. Recency alone recorded `159` for
    # `PL-YLZQ`, a commit containing none of its work, and advised writing that
    # number in. Confirming the hit rejects it, and the file's own history
    # answers with the merge that actually closed it.
    run = _closure_runner(
        {"PL-K7QX-a.md": CLOSED.format(id="PL-K7QX")},
        (
            "PL-B1C2 Make the simulation step transactional (#204)",
            "PL-K7QX, PL-41B2: triage the two captures (#159)",
        ),
        file_history=(
            "PL-B1C2 Make the simulation step transactional (#204)",
            "PL-K7QX, PL-41B2: triage the two captures (#159)",
        ),
    )

    assert closures_on_base(ROOT, {"PL-K7QX": "PL-K7QX-a.md"}, runner=run).numbers == {
        "PL-K7QX": 204
    }


def test_a_bookkeeping_merge_naming_a_closed_item_does_not_win() -> None:
    # The other half of the same defect, and the commoner one: the newest
    # subject leading with the id is a merge that wrote the item's `pr` back,
    # or a follow-up fix. `PL-1TF4` and `PL-J49T` recovered `250`, whose
    # subject reads "record #249". The item is already closed at such a commit
    # *and* at its parent, which is what tells it from the closure.
    run = _closure_runner(
        {"PL-K7QX-a.md": CLOSED.format(id="PL-K7QX")},
        ("PL-K7QX: record #249 (#250)", "PL-K7QX: do the work (#249)"),
        closed_from=1,
        file_history=("PL-K7QX: record #249 (#250)", "PL-K7QX: do the work (#249)"),
    )

    assert closures_on_base(ROOT, {"PL-K7QX": "PL-K7QX-a.md"}, runner=run).numbers == {
        "PL-K7QX": 249
    }


def test_a_subject_hit_that_cannot_be_confirmed_and_has_no_file_history_says_nothing() -> None:
    # Silence is the correct outcome when nothing can be confirmed. Recording
    # the unconfirmed number would be the false provenance this exists to stop.
    run = _closure_runner(
        {"PL-K7QX-a.md": CLOSED.format(id="PL-K7QX")},
        ("PL-B1C2 Something else (#204)", "PL-K7QX: triage it (#159)"),
    )

    assert closures_on_base(ROOT, {"PL-K7QX": "PL-K7QX-a.md"}, runner=run).numbers == {}


def test_a_number_belonging_to_another_item_is_not_borrowed() -> None:
    run = _closure_runner(
        {"PL-K7QX-a.md": CLOSED.format(id="PL-K7QX")}, ("PL-ZZZZ A different item entirely (#149)",)
    )
    assert closures_on_base(ROOT, {"PL-K7QX": "PL-K7QX-a.md"}, runner=run).numbers == {}


def test_a_closure_report_records_whether_the_checkout_is_truncated() -> None:
    """The depth travels with the answer, because it qualifies what a gap means.

    `checks.py` errors on a missing `pr` only where the history is complete;
    without this field it cannot tell "no commit names a number" from "no
    commit was in reach", and reporting the second as the first is what turned
    `main` red (`PL-99Y4`).
    """
    for answer, expected in (("true", True), ("false", False), ("", None)):
        run = _closure_runner(
            {"PL-K7QX-a.md": CLOSED.format(id="PL-K7QX")},
            ("PL-K7QX Do the thing (#148)",),
            shallow=answer,
        )
        report = closures_on_base(ROOT, {"PL-K7QX": "PL-K7QX-a.md"}, runner=run)

        assert report.shallow is expected, answer
        # `shallow` describes the checkout, not this commit: the parent here is
        # in reach at every one of the three, so the number is derived at every
        # one of them. What a truncated history costs is the test below.
        assert report.numbers == {"PL-K7QX": 148}


def test_a_number_is_not_derived_where_the_parent_is_out_of_reach() -> None:
    """The defect `PL-KX9N` reports, in the reading that produced it.

    A commit is the closure only if the item reads `done` in its tree and not
    in its parent's, and `_run_git` answers a failed `git show` with empty
    output - so a parent outside the checkout reads as "not done there" and the
    oldest commit held becomes the closure of everything in it. At a graft
    boundary git reports every file as added, which is exactly that shape.

    Measured on a `--depth 1` clone of this repository: `record` wrote `#401`
    onto `PL-6Q8N`, `PL-GJDW`, `PL-N2X4` and `PL-VRMK`, whose true numbers were
    `#399`, `#400`, `#400` and `#402`. Four wrong provenances written by the
    one command the skill forbids hand-editing the field in favour of.
    """
    run = _closure_runner(
        {"PL-K7QX-a.md": CLOSED.format(id="PL-K7QX")},
        ("PL-B1C2 The newest thing held (#401)",),
        shallow="true",
        depth=1,
        file_history=("PL-B1C2 The newest thing held (#401)",),
    )

    report = closures_on_base(ROOT, {"PL-K7QX": "PL-K7QX-a.md"}, runner=run)

    assert report.landed == frozenset({"PL-K7QX"})
    assert report.numbers == {}
    assert report.shallow is True


def test_a_subject_scan_hit_is_not_confirmed_where_the_parent_is_out_of_reach() -> None:
    """The other reading, which asks the same question of the same commit.

    The scan finds a subject leading with the id and then confirms it against
    the parent, so it is unguarded in the same way. It answered correctly on
    the clone above only because the boundary commit happened to be that item's
    real closure - luck, not a property.
    """
    run = _closure_runner(
        {"PL-K7QX-a.md": CLOSED.format(id="PL-K7QX")},
        ("PL-K7QX Do the thing (#148)",),
        shallow="true",
        depth=1,
    )

    assert closures_on_base(ROOT, {"PL-K7QX": "PL-K7QX-a.md"}, runner=run).numbers == {}


def test_a_partly_deepened_clone_answers_for_what_it_holds() -> None:
    """Declining is per commit, not per checkout, and this is why that matters.

    `is_shallow` is true of a clone deepened to any bounded depth, so a rule
    keyed on it would refuse the numbers a bounded fetch had just made provable
    - including the `git fetch --depth=200` that recovered the four wrong ones.
    Keying on the parent instead answers wherever the comparison can be made.

    Measured against real git on a 12-commit history fetched to depth 4: the
    three newest closures resolve, the nine at or below the boundary do not.
    """
    run = _closure_runner(
        {"PL-K7QX-a.md": CLOSED.format(id="PL-K7QX")},
        ("PL-K7QX Do the thing (#148)", "PL-B1C2 Something earlier (#140)"),
        shallow="true",
        depth=2,
    )

    assert closures_on_base(ROOT, {"PL-K7QX": "PL-K7QX-a.md"}, runner=run).numbers == {
        "PL-K7QX": 148
    }


def _lost_runner(tree: list[str], history: list[str], *, shallow: str = "false"):
    """A git whose `ref` tree holds `tree` and whose history holds `history`.

    `history` is spelled the way `rev-list --objects` prints it - `<sha> SP
    <path>`, newest commit first - because the ordering is load-bearing: the
    first blob seen for an id is the last content it had, and that is what the
    report hands back for recovery.
    """

    def run(args: list[str], root: Path) -> str:
        if args[0] == "ls-tree":
            return _tree_lines({path: path for path in tree})
        if args[0] == "rev-list":
            return "\n".join(history)
        if args[0] == "rev-parse" and args[-1] == "--is-shallow-repository":
            return shallow
        return ""

    return run


def test_lost_finds_an_item_the_history_holds_and_the_tree_does_not() -> None:
    """The case a merge resolution creates: no commit deletes it, the tree just stops having it."""
    report = lost(
        ROOT,
        items_dir="docs/items",
        runner=_lost_runner(
            tree=["docs/items/PL-K1K1-kept.md"],
            history=[
                "aaa111 docs/items/PL-K1K1-kept.md",
                "bbb222 docs/items/PL-B2B2-dropped-by-a-merge.md",
            ],
        ),
    )

    assert [item.identifier for item in report.items] == ["PL-B2B2"]
    assert report.items[0].blob == "bbb222"
    assert report.items[0].path == "docs/items/PL-B2B2-dropped-by-a-merge.md"
    assert report.known


def test_lost_does_not_report_a_renamed_item_file() -> None:
    """A title change renames the file, adding one path and removing another.

    By path that reads as a loss, which is why the comparison is by id. The
    same trap `stranded` documents, met here from the other direction.
    """
    report = lost(
        ROOT,
        items_dir="docs/items",
        runner=_lost_runner(
            tree=["docs/items/PL-K1K1-the-new-title.md"],
            history=[
                "aaa222 docs/items/PL-K1K1-the-new-title.md",
                "aaa111 docs/items/PL-K1K1-the-old-title.md",
            ],
        ),
    )

    assert report.known
    assert report.items == ()


def test_lost_hands_back_the_newest_blob_of_a_file_that_changed() -> None:
    """Recovery should restore the item as it last stood, not as it was captured."""
    report = lost(
        ROOT,
        items_dir="docs/items",
        runner=_lost_runner(
            tree=["docs/items/PL-K1K1-kept.md"],
            history=[
                "newest0 docs/items/PL-B2B2-edited-then-lost.md",
                "oldest0 docs/items/PL-B2B2-edited-then-lost.md",
                "aaa111 docs/items/PL-K1K1-kept.md",
            ],
        ),
    )

    assert [item.blob for item in report.items] == ["newest0"]


def test_lost_ignores_paths_outside_the_store() -> None:
    report = lost(
        ROOT,
        items_dir="docs/items",
        runner=_lost_runner(
            tree=["docs/items/PL-K1K1-kept.md"],
            history=[
                "aaa111 docs/items/PL-K1K1-kept.md",
                "ccc333 docs/archive/PL-C3C3-not-an-item-any-more.md",
                "ddd444 README.md",
            ],
        ),
    )

    assert report.known
    assert report.items == ()


def test_lost_declines_rather_than_reporting_every_id_when_the_store_cannot_be_read() -> None:
    """An unreadable tree would make the whole history read as lost - long, alarming and wrong."""
    report = lost(
        ROOT,
        items_dir="docs/items",
        runner=_lost_runner(tree=[], history=["aaa111 docs/items/PL-K1K1-kept.md"]),
    )

    assert not report.known
    assert "whole history would read as lost" in report.declined
    assert report.items == ()


def test_lost_marks_a_truncated_clone_so_a_clean_answer_is_not_overclaimed() -> None:
    report = lost(
        ROOT,
        items_dir="docs/items",
        runner=_lost_runner(
            tree=["docs/items/PL-K1K1-kept.md"],
            history=["aaa111 docs/items/PL-K1K1-kept.md"],
            shallow="true",
        ),
    )

    assert report.items == ()
    assert report.truncated


def test_lost_treats_an_unanswerable_shallow_question_as_truncated() -> None:
    """`is_shallow` returns None when git will not say; absence proves nothing."""
    report = lost(
        ROOT,
        items_dir="docs/items",
        runner=_lost_runner(
            tree=["docs/items/PL-K1K1-kept.md"],
            history=["aaa111 docs/items/PL-K1K1-kept.md"],
            shallow="",
        ),
    )

    assert report.truncated


REV = "abc123"


def _closed_by_runner(
    touched: tuple[str, ...],
    trees: dict[str, str],
    *,
    resolves: bool = True,
    parent: bool = True,
    log: list[list[str]] | None = None,
):
    """A git whose `trees` map `<ref>:<path>` to the text held there.

    `touched` is what the commit changed under the item directory, which is
    what `git diff --name-only` against the first parent answers. `resolves`
    and `parent` are the two ways the read declines: a revision this checkout
    does not hold, and one whose parent it does not hold.
    """

    def run(args: list[str], root: Path) -> str:
        if log is not None:
            log.append(args)
        if args[0] == "rev-parse":
            if args[-1].startswith(f"{REV}^^"):
                return f"{REV}~1\n" if parent else ""
            return f"{REV}\n" if resolves else ""
        if args[0] == "diff":
            return "\n".join(touched)
        if args[0] == "ls-tree":
            prefix = f"{args[2]}:"
            return _tree_lines({k[len(prefix) :]: k for k in sorted(trees) if k.startswith(prefix)})
        if args[0] == "show":
            return trees.get(args[-1], "")
        return ""

    return run


def test_a_commit_that_writes_done_closed_the_item() -> None:
    run = _closed_by_runner(
        ("items/PL-K7QX-a.md",),
        {
            f"{REV}:items/PL-K7QX-a.md": CLOSED.format(id="PL-K7QX"),
            f"{REV}^:items/PL-K7QX-a.md": OPEN_ITEM.format(id="PL-K7QX"),
        },
    )

    report = closed_by(REV, ROOT, items_dir="items", runner=run)

    assert report.known
    assert report.paths == {"PL-K7QX": "items/PL-K7QX-a.md"}


def test_an_item_already_done_at_the_parent_was_not_closed_here() -> None:
    """The stricter half of the question, and the one a number depends on.

    A pull request records its number on what it closed, never on what was
    already closed when it branched - a later edit to a finished item's brief
    touches the file and must not be read as the closure.
    """
    run = _closed_by_runner(
        ("items/PL-K7QX-a.md",),
        {
            f"{REV}:items/PL-K7QX-a.md": CLOSED.format(id="PL-K7QX"),
            f"{REV}^:items/PL-K7QX-a.md": CLOSED.format(id="PL-K7QX"),
        },
    )

    assert closed_by(REV, ROOT, items_dir="items", runner=run).closed == ()


def test_a_closed_item_renamed_by_the_commit_was_not_closed_by_it() -> None:
    """A title edit renames the file, so the path proves nothing; the id does.

    Comparing paths would find nothing at the new name in the parent tree and
    read that as a closure, stamping this commit's number over the one that
    actually closed the item.
    """
    run = _closed_by_runner(
        ("items/PL-K7QX-new.md", "items/PL-K7QX-old.md"),
        {
            f"{REV}:items/PL-K7QX-new.md": CLOSED.format(id="PL-K7QX"),
            f"{REV}^:items/PL-K7QX-old.md": CLOSED.format(id="PL-K7QX"),
        },
    )

    assert closed_by(REV, ROOT, items_dir="items", runner=run).closed == ()


def test_an_item_this_commit_created_and_closed_counts() -> None:
    run = _closed_by_runner(
        ("items/PL-K7QX-a.md",), {f"{REV}:items/PL-K7QX-a.md": CLOSED.format(id="PL-K7QX")}
    )

    assert closed_by(REV, ROOT, items_dir="items", runner=run).paths == {
        "PL-K7QX": "items/PL-K7QX-a.md"
    }


def test_a_commit_that_only_captures_closes_nothing() -> None:
    run = _closed_by_runner(
        ("items/PL-K7QX-a.md",), {f"{REV}:items/PL-K7QX-a.md": OPEN_ITEM.format(id="PL-K7QX")}
    )

    report = closed_by(REV, ROOT, items_dir="items", runner=run)

    assert report.known
    assert report.closed == ()


def test_a_touched_file_that_is_not_an_item_is_ignored() -> None:
    run = _closed_by_runner(("items/README.md",), {f"{REV}:items/README.md": "not an item"})

    assert closed_by(REV, ROOT, items_dir="items", runner=run).closed == ()


def test_only_the_files_the_commit_touched_are_read() -> None:
    """What keeps this at a handful of tree reads rather than one per item."""
    log: list[list[str]] = []
    run = _closed_by_runner(
        ("items/PL-K7QX-a.md",),
        {
            f"{REV}:items/PL-K7QX-a.md": CLOSED.format(id="PL-K7QX"),
            f"{REV}:items/PL-B1C2-b.md": CLOSED.format(id="PL-B1C2"),
            f"{REV}^:items/PL-B1C2-b.md": CLOSED.format(id="PL-B1C2"),
        },
        log=log,
    )

    closed_by(REV, ROOT, items_dir="items", runner=run)

    assert not [args for args in log if args[0] == "show" and "PL-B1C2" in args[-1]]


def test_a_revision_with_no_parent_here_declines_rather_than_answering() -> None:
    """At `fetch-depth: 1` there is nothing to compare against.

    Answering anyway would read as "everything done here was closed here",
    which would stamp one pull request number across the whole store.
    """
    run = _closed_by_runner(
        ("items/PL-K7QX-a.md",),
        {f"{REV}:items/PL-K7QX-a.md": CLOSED.format(id="PL-K7QX")},
        parent=False,
    )

    report = closed_by(REV, ROOT, items_dir="items", runner=run)

    assert not report.known
    assert "parent is outside this checkout" in report.declined
    assert report.closed == ()


def test_a_revision_this_checkout_does_not_hold_declines() -> None:
    run = _closed_by_runner((), {}, resolves=False)

    report = closed_by(REV, ROOT, items_dir="items", runner=run)

    assert not report.known
    assert "names no commit here" in report.declined


def _files_runner(diffs: dict[str, list[str]], counts: dict[str, int] | None = None):
    """A git that answers `diff --name-only` and `rev-list --count` per ref.

    A ref absent from `diffs` answers with the empty string `_run_git` returns
    for a failure, which is the case the guard has to tell from a branch that
    genuinely changed nothing.
    """

    def run(args: list[str], root: Path) -> str:
        if args[0] == "diff":
            ref = args[-1].split("...")[-1]
            return "".join(f"{path}\n" for path in diffs.get(ref, []))
        if args[0] == "rev-list":
            ref = args[-1].split("..")[-1]
            return f"{(counts or {}).get(ref, 0)}\n"
        raise AssertionError(f"unexpected git call: {args}")

    return run


def _flight(*branches: tuple[str, str], unreadable: tuple[str, ...] = ()) -> FlightReport:
    return FlightReport(
        branches=tuple(Branch(name=name, item_id=item) for name, item in branches),
        unreadable=unreadable,
        base=BASE,
    )


def test_a_branch_reports_the_files_it_has_changed() -> None:
    run = _files_runner({"origin/feature": ["src/app/view.py", "docs/MODEL.md"]})

    files = files_in_flight(ROOT, _flight(("origin/feature", "PL-K7QX")), runner=run)

    assert files.base == BASE
    assert [entry.branch for entry in files.branches] == ["origin/feature"]
    assert files.branches[0].paths == ("docs/MODEL.md", "src/app/view.py")
    assert files.branches[0].item_ids == ("PL-K7QX",)


def test_two_items_on_one_branch_are_reported_once_naming_both() -> None:
    run = _files_runner({"origin/feature": ["a.py"]})

    files = files_in_flight(
        ROOT, _flight(("origin/feature", "PL-K7QX"), ("origin/feature", "PL-41B2")), runner=run
    )

    assert len(files.branches) == 1
    assert files.branches[0].item_ids == ("PL-41B2", "PL-K7QX")


def test_a_ref_whose_commits_went_unread_is_not_diffed() -> None:
    """The merge-base a three-dot diff needs is the one that already failed."""
    run = _files_runner({})

    files = files_in_flight(
        ROOT, _flight(("origin/truncated", "PL-K7QX"), unreadable=("origin/truncated",)), runner=run
    )

    assert files.branches == ()
    assert files.unreadable == ("origin/truncated",)


def test_an_empty_diff_on_a_branch_holding_commits_is_named_unread() -> None:
    """`_run_git` answers a failure with the empty string a clean branch gives.

    Reporting the first as the second would say a branch changes nothing when
    the truth is that nothing could be read about it.
    """
    run = _files_runner({}, counts={"origin/feature": 3})

    files = files_in_flight(ROOT, _flight(("origin/feature", "PL-K7QX")), runner=run)

    assert files.branches == ()
    assert files.unreadable == ("origin/feature",)


def test_an_empty_diff_on_a_branch_holding_no_commits_is_reported_as_empty() -> None:
    run = _files_runner({}, counts={"origin/feature": 0})

    files = files_in_flight(ROOT, _flight(("origin/feature", "PL-K7QX")), runner=run)

    assert [entry.paths for entry in files.branches] == [()]
    assert files.unreadable == ()


def test_a_report_with_no_base_reads_nothing() -> None:
    """No base means the flight read itself declined; there is nothing to diff."""
    files = files_in_flight(ROOT, FlightReport(), runner=_files_runner({}))

    assert files == FlightFiles()


# A branch whose pull request merged and which was then pushed to again: the
# base holds `landed.txt` and has never held `pushed-after.md`.
PARTLY = "claude/pl-k7qx-partly-landed"


def _orphaned(
    adds: dict[str, list[tuple[str, str]]],
    on_base: set[str],
    refs: list[str] | None = None,
    merged: list[str] | None = None,
    touched: dict[str, list[tuple[str, tuple[str, ...]]]] | None = None,
    tips: dict[str, dict[str, tuple[str, str]]] | None = None,
    duplicated: tuple[str, ...] = (),
) -> OrphanedReport:
    return orphaned(
        ROOT,
        runner=_runner(
            refs or [PARTLY],
            merged,
            adds=adds,
            on_base=on_base,
            touched=touched,
            tips=tips,
            duplicated=duplicated,
        ),
    )


def test_a_branch_pushed_to_after_its_pull_request_merged_is_reported() -> None:
    """The failure this exists for: one commit that no merge will ever take.

    A pull request merges the head it was opened against. A commit pushed to
    the branch afterwards is merged by nothing, conflicts with nothing and
    fails no check - and unless it happened to touch `docs/items/`, nothing in
    this project noticed before `orphaned` (`PL-3D2M`).
    """
    report = _orphaned(
        adds={PARTLY: [("a1", "landed.txt"), ("a2", "pushed-after.md")]},
        on_base={"a1"},
        touched={
            PARTLY: [
                ("PL-ZSV6 the rule pushed after the merge", ("pushed-after.md",)),
                ("PL-K7QX the work the pull request took", ("landed.txt",)),
            ]
        },
    )

    assert [branch.ref for branch in report.branches] == [PARTLY]
    assert report.branches[0].outstanding == ("pushed-after.md",)
    assert report.branches[0].landed == ("landed.txt",)
    assert [commit.subject for commit in report.branches[0].commits] == [
        "PL-ZSV6 the rule pushed after the merge"
    ]


def test_a_branch_that_revised_its_own_file_before_merging_carries_nothing() -> None:
    """The branch changed its mind once, and nothing was left behind (`PL-XLQ5`).

    An early commit wrote one version of a file and a later commit on the same
    branch rewrote it. The squash carried only the final version, so the
    intermediate blob is one the default branch has genuinely never held - and
    `_landing_split`, which asks after historical blobs, calls it outstanding.

    Observed 2026-09-05 on `origin/claude/next-workflow-item-c2b07p`,
    immediately after `PL-X3WZ` merged as `#324`: four files reported while
    `git diff origin/main HEAD` was empty. The tip comparison is that two-dot
    diff, and it is empty here for the same reason.
    """
    report = _orphaned(
        adds={PARTLY: [("a1", "landed.txt"), ("a2", "revised.py")]},
        on_base={"a1"},
        touched={
            PARTLY: [
                ("PL-X3WZ rename the helper", ("revised.py",)),
                ("PL-X3WZ introduce the helper", ("landed.txt",)),
            ]
        },
        tips={PARTLY: {}},
    )

    assert report.branches == ()
    assert report.rewritten == ()


def test_a_branch_whose_file_the_base_then_added_to_carries_nothing() -> None:
    """Supersession on the *base*, which is the expensive direction (`PL-XLQ5`).

    `PL-1VFK` (`#437`) recovered two stranded items by re-applying them and
    appended a recovery note to one in the same commit, so the blob the branch
    introduced for that file is one `main` has never held while `main`'s copy is
    a strict superset of it. The `recover:` line this report would hand a reader
    is a `git checkout` of the branch's older copy over the newer one, which
    deletes the note.

    Going from the base to the ref therefore only *removes* lines, and that is
    what the counts say: nothing is missing from the base.
    """
    report = _orphaned(
        adds={PARTLY: [("a1", "landed.txt"), ("a2", "docs/items/PL-6YYR-recovered.md")]},
        on_base={"a1"},
        touched={
            PARTLY: [
                ("PL-6YYR capture the release tag", ("docs/items/PL-6YYR-recovered.md",)),
                ("PL-K7QX the work the pull request took", ("landed.txt",)),
            ]
        },
        tips={PARTLY: {"docs/items/PL-6YYR-recovered.md": ("0", "4")}},
    )

    assert report.branches == ()


def test_a_branch_whose_only_landed_commit_is_docket_record_output_is_not_merged() -> None:
    """Convergence is not a merge, and a whole commit of it is still not a merge (`PL-JBRC`).

    `PL-5TRV` narrowed the merge verdict to "the base took one of this branch's
    commits whole", because two sessions running `bin/docket record` write
    byte-identical lines and each then holds content the other landed. That
    leaves one shape: a commit *entirely* made of `record` output, every path of
    which agrees with the base by convergence rather than by merge.

    A branch carrying one of those and one genuinely outstanding commit then
    reads as a merged pull request with work left behind - and the recovery the
    `docket` skill prescribes for that deletes the ref an open pull request was
    raised against, which is `PL-5TRV`'s harm by a narrower route.
    """
    report = _orphaned(
        adds={PARTLY: [("a1", "docs/items/PL-K7QX-recorded.md"), ("a2", "src/live.py")]},
        on_base={"a1"},
        touched={
            PARTLY: [
                ("PL-K7QX the work this session is still doing", ("src/live.py",)),
                (
                    "PL-K7QX record the merged pull request number",
                    ("docs/items/PL-K7QX-recorded.md",),
                ),
            ]
        },
    )

    assert report.branches == ()


def test_a_branch_on_duplicated_history_is_not_reported_as_orphaned() -> None:
    """A rewrite changes every hash and no byte, so content cannot tell it from a merge.

    `PL-YGF3` observed exactly this on `claude/fresh-gas-flow-range-4bom2g`.
    The hazard is not the report itself - its recovery copies a file - but the
    recipe the `docket` skill prescribes for a branch whose pull request merged,
    which deletes the ref. On pre-rewrite history that ref holds the only copy
    of the commits it carries, so it is named apart from the branches that lead
    a reader there (`PL-Y31G`).
    """
    report = _orphaned(
        adds={PARTLY: [("a1", "landed.txt"), ("a2", "pushed-after.md")]},
        on_base={"a1"},
        touched={
            PARTLY: [
                ("PL-ZSV6 the rule pushed after the merge", ("pushed-after.md",)),
                ("PL-K7QX the work the pull request took", ("landed.txt",)),
            ]
        },
        duplicated=(PARTLY,),
    )

    assert report.branches == ()
    assert report.rewritten == (PARTLY,)


def test_a_branch_that_has_landed_nothing_is_ordinary_work_in_flight() -> None:
    """The signature of a live session, and the one this must stay silent on.

    Measured on this repository the day the rule was written: the single live
    branch introduced seventeen paths and the default branch held none of
    them. A rule that fired there would fire in most sessions and be read past
    in all of them.
    """
    assert (
        _orphaned(adds={PARTLY: [("a1", "one.txt"), ("a2", "two.txt")]}, on_base=set()).branches
        == ()
    )


def test_a_branch_whose_work_all_landed_never_reaches_the_report() -> None:
    """It is excluded as landed before this read begins, not cleared by it."""
    assert (
        _orphaned(
            adds={PARTLY: [("a1", "one.txt"), ("a2", "two.txt")]}, on_base={"a1", "a2"}
        ).branches
        == ()
    )


def test_a_ref_whose_commits_went_unread_is_named_rather_than_answered() -> None:
    """The truncated clone an agent session starts from, reported as a gap."""
    report = orphaned(
        ROOT,
        runner=_runner(
            [PARTLY], adds={PARTLY: [("a1", "landed.txt")]}, on_base={"a1"}, unrelated=(PARTLY,)
        ),
    )

    assert report.branches == ()
    assert report.unreadable == (PARTLY,)


def test_a_checkout_that_can_read_no_ref_declines_rather_than_answering() -> None:
    """Nothing read is not the same claim as nothing found."""
    report = orphaned(ROOT, runner=_runner([], merged=[]))

    assert not report.known
    assert "no branch refs" in report.declined


def test_a_checkout_whose_every_branch_has_merged_answers_cleanly() -> None:
    """The opposite case, which an empty candidate list reports identically.

    Git listing nothing and git listing only merged branches are opposite
    answers - a check that could not run, and one that ran and found the
    repository sound - so `_Refs` counts the listing before the filter.
    """
    report = orphaned(ROOT, runner=_runner([PARTLY], merged=[PARTLY]))

    assert report.known
    assert report.branches == ()


def test_the_digest_names_a_commit_pushed_after_its_pull_request_merged() -> None:
    """The other half of the line above, for everything that is not an item.

    A dropped commit touching `docs/items/` reached the next session through
    the stranded line; one touching a skill, a rule or `src/` reached nobody
    (`PL-3D2M`). Both now arrive the same way, in text every session reads
    before it does anything else.
    """
    left = OrphanedReport(
        branches=(
            OrphanedBranch(
                ref="claude/pl-k7qx-do-the-thing",
                landed=("work.py",),
                outstanding=("rule.md", "docs/items/PL-ZSV6-a-rule.md"),
                commits=(),
            ),
        ),
        refs_read=1,
    )

    stated = [line for line in _digest(left=left).splitlines() if "pl-k7qx" in line]

    assert len(stated) == 1
    assert "2 files" in stated[0]
    assert "bin/docket stranded" in stated[0]


def test_the_digest_stays_silent_when_no_branch_has_been_left_behind() -> None:
    """The ordinary case, and the one a line resent every turn must not cost."""
    assert "after its pull request merged" not in _digest(left=OrphanedReport(refs_read=2))


def test_a_commit_the_merge_took_and_merged_is_not_work_left_behind() -> None:
    """The regression this check earned on its own first live firing.

    `origin/claude/snapshot-run-history-copy-dw6djz` carried the v0.3.8 release
    commit. `#312` squash-merged it while `#311` was landing edits to the same
    `ROADMAP.md` prose, so the merge wrote the combined text and three of that
    commit's ten paths no longer matched anything the base had held - and the
    branch was reported as carrying lost work while `main` was *ahead* of it.

    One commit, partly landed, is a merge that happened. Only a commit *none*
    of whose paths reached the base is work nothing took (`PL-JHJ3`).
    """
    report = _orphaned(
        adds={
            PARTLY: [
                ("a1", "pyproject.toml"),
                ("a2", "docs/releases/v0.3.8.md"),
                ("b1", "ROADMAP.md"),
            ]
        },
        on_base={"a1", "a2"},
        touched={
            PARTLY: [
                ("Release v0.3.8", ("pyproject.toml", "docs/releases/v0.3.8.md", "ROADMAP.md"))
            ]
        },
    )

    assert report.branches == ()


def test_a_branch_whose_changes_the_base_already_holds_is_not_partly_merged() -> None:
    """The false verdict `#372` drew while it was open, and nothing had merged.

    `claude/triage-fwyuus` was reported as having "already taken the rest of its
    work" while its pull request was open and `origin/main` carried none of its
    triage. What matched was `bin/docket record`: eight of its first commit's
    twelve files changed only by a `pr:` line, and the sessions behind `#366`
    and `#369` had written the same line - the command is deterministic, so both
    sides wrote identical bytes. Eight of twelve agreed with the base and the
    detector read agreement as merge (`PL-5TRV`).

    Content agreement cannot tell a merge from a convergence, and no comparison
    of those eight blobs ever will. What can be told apart is the *unit*: a
    squash merge takes whole commits, so a branch whose pull request merged has
    a commit every path of which the base holds. Convergence lands scattered
    files inside commits and leaves no whole one, which is what the shape below
    asserts - the branch has a wholly outstanding commit, and would have been
    reported for it, and no commit the base took whole.
    """
    report = _orphaned(
        adds={
            PARTLY: [
                ("r1", "docs/items/PL-3JN2-one.md"),
                ("r2", "docs/items/PL-7QW5-two.md"),
                ("w1", "docs/items/PL-7PLY-the-real-work.md"),
                ("w2", "docs/WORKING_NOTES.md"),
            ]
        },
        on_base={"r1", "r2"},
        touched={
            PARTLY: [
                ("PL-7PLY triage the queue", ("docs/WORKING_NOTES.md",)),
                (
                    "PL-7PLY triage, and record the numbers the base also recorded",
                    (
                        "docs/items/PL-3JN2-one.md",
                        "docs/items/PL-7QW5-two.md",
                        "docs/items/PL-7PLY-the-real-work.md",
                    ),
                ),
            ]
        },
    )

    assert report.branches == ()


def test_a_branch_whose_commits_cannot_be_walked_is_not_reported() -> None:
    """No commit to name is no finding to hand a reader, and it says so by silence."""
    assert (
        _orphaned(
            adds={PARTLY: [("a1", "landed.txt"), ("a2", "pushed-after.md")]}, on_base={"a1"}
        ).branches
        == ()
    )


def _base_runner(declared: str = '[project]\nversion = "0.3.8"\n', notes: tuple[str, ...] = ()):
    """A git holding one base ref, its version file, and its release notes.

    Its own runner rather than `_runner`'s: this read asks git two questions
    that one asks none of, and threading them through a helper built for the
    branch walk would make every test there carry arguments it has no use for.
    """

    def run(args: list[str], root: Path) -> str:
        if args[0] == "rev-parse":
            return f"{BASE}\n" if args[-1] == BASE else ""
        if args[0] == "show":
            return declared
        if args[0] == "ls-tree":
            return "".join(f"docs/releases/{name}\n" for name in notes)
        return ""

    return run


def test_the_base_reports_the_version_and_the_notes_it_holds() -> None:
    report = released_on_base(
        ROOT,
        version_file="pyproject.toml",
        notes_dir="docs/releases",
        runner=_base_runner(notes=("v0.3.7.md", "v0.3.8.md")),
    )

    assert report == BaseRelease(
        base=BASE, version="0.3.8", notes=frozenset({"v0.3.7.md", "v0.3.8.md"}), known=True
    )


def test_notes_are_named_without_the_directory_git_prints_them_under() -> None:
    """The directory is the caller's own constant; repeating it invites two spellings."""
    report = released_on_base(
        ROOT,
        version_file="pyproject.toml",
        notes_dir="docs/releases",
        runner=_base_runner(notes=("v0.3.8.md",)),
    )

    assert report.notes == frozenset({"v0.3.8.md"})


def test_a_base_whose_version_file_cannot_be_read_is_unknown_rather_than_empty() -> None:
    """PL-66FP: a gap in the evidence must not read as a clean bill of health."""
    report = released_on_base(
        ROOT, version_file="pyproject.toml", notes_dir="docs/releases", runner=_base_runner("")
    )

    assert not report.known
    assert report.notes == frozenset()


def test_a_base_holding_no_notes_at_all_is_still_a_real_answer() -> None:
    """No notes is what a project that has never cut one looks like."""
    report = released_on_base(
        ROOT, version_file="pyproject.toml", notes_dir="docs/releases", runner=_base_runner()
    )

    assert report.known
    assert report.notes == frozenset()


def test_the_base_is_read_from_the_ref_rather_than_the_working_tree() -> None:
    """The working tree is this session's own cut, which would answer about itself."""
    log: list[list[str]] = []

    def run(args: list[str], root: Path) -> str:
        log.append(args)
        return _base_runner()(args, root)

    released_on_base(ROOT, version_file="pyproject.toml", notes_dir="docs/releases", runner=run)

    assert ["show", f"{BASE}:pyproject.toml"] in log
    assert ["ls-tree", "--name-only", BASE, "docs/releases/"] in log


def test_an_explicit_base_is_read_instead_of_the_default_one() -> None:
    log: list[list[str]] = []

    def run(args: list[str], root: Path) -> str:
        log.append(args)
        return _base_runner()(args, root)

    report = released_on_base(
        ROOT,
        version_file="pyproject.toml",
        notes_dir="docs/releases",
        base="origin/release",
        runner=run,
    )

    assert report.base == "origin/release"
    assert ["rev-parse", "--verify", "--quiet", BASE] not in log


def _cut_runner(
    notes: dict[str, list[str]],
    merged: tuple[str, ...] = (),
    head: str = "",
    when: str = "2026-09-04T11:34:00+00:00",
):
    """A git whose refs each carry the release-notes paths `notes` gives them.

    Every ref also adds a blob of its own that the base has never held, which
    is what keeps `_unlanded_refs` from reading it as landed - the release
    files alone would not, since a merged release's notes are on the base by
    then, which is the case `on_base` exists for.
    """
    refs = list(notes)

    def run(args: list[str], root: Path) -> str:
        if args[0] == "rev-parse":
            if args[-1] == BASE:
                return f"{BASE}\n"
            return f"{args[-1]}@tip\n" if args[-1] in refs else ""
        if args[0] == "for-each-ref":
            if any(arg.startswith("--merged=") for arg in args):
                return "\n".join(merged)
            return "\n".join(refs)
        if args[0] == "merge-base":
            # `cuts_in_flight` asks whether HEAD contains a ref's tip; git
            # echoes the merge base, so a tip HEAD holds comes back unchanged.
            if args[-1] == "HEAD":
                return f"{args[-2]}\n" if args[-2] == f"{head}@tip" else "elsewhere\n"
            return "fork\n"
        if args[0] == "rev-list":
            return "onbase some/path\n"
        if args[0] == "diff" and "--name-only" in args:
            ref = args[2].split("...")[-1]
            return "".join(f"{path}\n" for path in notes.get(ref, []))
        if args[0] == "diff":
            ref = args[-2]
            return f":000000 100644 {'0' * 40} {ref}blob A\tsome/{ref}\n"
        if args[0] == "log":
            return f"{when}\n"
        return ""

    return run


def test_a_ref_carrying_release_notes_the_base_lacks_is_cutting_that_version() -> None:
    """PL-66FP: the notes file is the one artifact a release cut cannot happen without."""
    report = cuts_in_flight(
        ROOT,
        notes_dir="docs/releases",
        runner=_cut_runner({"origin/claude/a": ["docs/releases/v0.3.9.md"]}),
    )

    assert report.branches == (
        BranchCut(ref="origin/claude/a", versions=("0.3.9",), cut=date(2026, 9, 4), mine=False),
    )


def test_a_version_the_base_already_holds_is_not_in_flight() -> None:
    """The squash-merge case: the branch stays unlanded long after its release merged.

    Measured 2026-09-04 against this repository - the branch whose v0.3.9
    release had merged twenty minutes earlier was still listed by
    `_unlanded_refs`, so without this the guard fires on every release after
    the first and nobody reads it.
    """
    report = cuts_in_flight(
        ROOT,
        notes_dir="docs/releases",
        on_base=frozenset({"v0.3.9.md"}),
        runner=_cut_runner({"origin/claude/a": ["docs/releases/v0.3.9.md"]}),
    )

    assert report.branches == ()


def test_this_checkouts_own_cut_is_marked_rather_than_reported_as_a_rival() -> None:
    """Telling a session to yield to itself is the one answer this must never give."""
    report = cuts_in_flight(
        ROOT,
        notes_dir="docs/releases",
        runner=_cut_runner({"claude/mine": ["docs/releases/v0.4.0.md"]}, head="claude/mine"),
    )

    assert [branch.mine for branch in report.branches] == [True]


def test_a_ref_touching_no_release_notes_is_not_cutting_anything() -> None:
    report = cuts_in_flight(
        ROOT, notes_dir="docs/releases", runner=_cut_runner({"origin/claude/a": []})
    )

    assert report.branches == ()


def test_every_version_a_ref_carries_is_named() -> None:
    """A branch that cut twice is two collisions, not one."""
    report = cuts_in_flight(
        ROOT,
        notes_dir="docs/releases",
        runner=_cut_runner(
            {"origin/claude/a": ["docs/releases/v0.3.9.md", "docs/releases/v0.4.0.md"]}
        ),
    )

    assert report.branches[0].versions == ("0.3.9", "0.4.0")


def test_a_merged_ref_is_not_read_at_all() -> None:
    report = cuts_in_flight(
        ROOT,
        notes_dir="docs/releases",
        runner=_cut_runner(
            {"origin/claude/a": ["docs/releases/v0.3.9.md"]}, merged=("origin/claude/a",)
        ),
    )

    assert report.branches == ()


def test_an_unreadable_ref_is_named_rather_than_reported_clean() -> None:
    """A gap in the evidence is not a clean bill of health."""

    def run(args: list[str], root: Path) -> str:
        if args[0] == "merge-base" and args[-1] != "HEAD":
            return ""
        return _cut_runner({"origin/claude/a": ["docs/releases/v0.3.9.md"]})(args, root)

    report = cuts_in_flight(ROOT, notes_dir="docs/releases", runner=run)

    assert report.unreadable == ("origin/claude/a",)
    assert report.branches == ()


def test_a_cut_whose_date_cannot_be_read_is_reported_without_one() -> None:
    """The date separates a live session from an abandoned branch; its absence is not fatal."""
    report = cuts_in_flight(
        ROOT,
        notes_dir="docs/releases",
        runner=_cut_runner({"origin/claude/a": ["docs/releases/v0.3.9.md"]}, when=""),
    )

    assert report.branches[0].cut is None


# --- a closed item's recorded `verify:` --------------------------------------
#
# The other half of a closure: not "has it landed" but "does it still record
# the command that proved it". Git is injected here like everywhere else, so
# these assert the narrowing and the id resolution rather than the plumbing.

RECORDED = "---\nid: {id}\ntitle: T\nstatus: done\nverify: {verify}\n---\n"


def _record_runner(
    on_base: dict[str, str],
    committed: tuple[str, ...] = (),
    uncommitted: tuple[str, ...] = (),
    base_paths: tuple[str, ...] = (),
):
    """A git whose base holds `on_base`, keyed by the path the base stores it under.

    `committed` and `uncommitted` are the paths the two diffs report, so a case
    can put an edit in either place; `base_paths` is what `ls-tree` lists, which
    defaults to the keys of `on_base` and is given explicitly only where a test
    needs the base to hold a path the tree does not.
    """
    listing = base_paths or tuple(on_base)

    def run(args: list[str], _root: Path) -> str:
        if args[0] == "rev-parse":
            return "aaa111\n"
        if args[0] == "diff":
            paths = committed if args[2].endswith("...HEAD") else uncommitted
            return "\n".join(paths)
        if args[0] == "ls-tree":
            return _tree_lines({path: path for path in listing})
        if args[0] == "show":
            _, _, path = args[-1].partition(":")
            return on_base.get(path, "")
        return ""

    return run


def test_only_the_closed_items_this_checkout_changed_are_read() -> None:
    # Every closed item is offered - two hundred of them here - and a `git
    # show` each on every `make check` is what the diff exists to avoid.
    reads: list[list[str]] = []
    inner = _record_runner(
        {"docs/items/PL-K7QX-a.md": RECORDED.format(id="PL-K7QX", verify="pytest a")},
        committed=("docs/items/PL-K7QX-a.md",),
    )

    def run(args: list[str], root: Path) -> str:
        reads.append(args)
        return inner(args, root)

    report = records_on_base(
        ROOT, {"PL-K7QX": "PL-K7QX-a.md", "PL-B2B2": "PL-B2B2-b.md"}, runner=run
    )

    assert report.commands == {"PL-K7QX": "pytest a"}
    assert [a for a in reads if a[0] == "show"] == [["show", "origin/main:docs/items/PL-K7QX-a.md"]]


def test_an_uncommitted_edit_is_read_as_well_as_a_committed_one() -> None:
    # `make check` runs before the commit as often as after it, and the moment
    # before is when restoring the recorded command is free.
    run = _record_runner(
        {"docs/items/PL-K7QX-a.md": RECORDED.format(id="PL-K7QX", verify="pytest a")},
        uncommitted=("docs/items/PL-K7QX-a.md",),
    )

    assert records_on_base(ROOT, {"PL-K7QX": "PL-K7QX-a.md"}, runner=run).commands == {
        "PL-K7QX": "pytest a"
    }


def test_nothing_changed_here_reads_no_trees_at_all() -> None:
    # The ordinary branch touches no closed item, and pays a diff for the
    # answer rather than a listing and a read.
    reads: list[list[str]] = []
    inner = _record_runner({"docs/items/PL-K7QX-a.md": RECORDED.format(id="PL-K7QX", verify="x")})

    def run(args: list[str], root: Path) -> str:
        reads.append(args)
        return inner(args, root)

    report = records_on_base(ROOT, {"PL-K7QX": "PL-K7QX-a.md"}, runner=run)

    assert report.records == ()
    assert report.base == "origin/main"
    assert not [a for a in reads if a[0] in {"ls-tree", "show"}]


def test_a_retitled_item_is_found_by_id_rather_than_by_path() -> None:
    # Retitling renames the file, so the working tree's path need not exist on
    # the base. By path that reads as an item the base does not hold, which
    # would let a rewrite through on exactly the branch that renamed it.
    run = _record_runner(
        {"docs/items/PL-K7QX-old-title.md": RECORDED.format(id="PL-K7QX", verify="pytest a")},
        committed=("docs/items/PL-K7QX-new-title.md",),
    )

    assert records_on_base(ROOT, {"PL-K7QX": "PL-K7QX-new-title.md"}, runner=run).commands == {
        "PL-K7QX": "pytest a"
    }


def test_an_item_the_base_has_never_held_is_not_reported() -> None:
    # An item captured and closed on this branch has no recorded command to
    # contradict, which is what lets a closure travel with its own work.
    run = _record_runner({}, committed=("docs/items/PL-K7QX-a.md",), base_paths=())

    assert records_on_base(ROOT, {"PL-K7QX": "PL-K7QX-a.md"}, runner=run).records == ()


def test_an_item_still_open_on_the_base_is_not_reported() -> None:
    # A closure in flight is not yet a record, so its command is still the
    # session's to write.
    run = _record_runner(
        {"docs/items/PL-K7QX-a.md": OPEN_ITEM.format(id="PL-K7QX")},
        committed=("docs/items/PL-K7QX-a.md",),
    )

    assert records_on_base(ROOT, {"PL-K7QX": "PL-K7QX-a.md"}, runner=run).records == ()


def test_a_checkout_with_no_default_branch_declines_rather_than_passing() -> None:
    # An empty result meaning "could not look" must never render as "looked,
    # found nothing" - the standing rule for every reader in this module.
    report = records_on_base(ROOT, {"PL-K7QX": "PL-K7QX-a.md"}, runner=lambda args, root: "")

    assert not report.known
    assert "no default branch" in report.declined


# --- the file's own history, across the renames a title edit makes ----------
#
# `docket` names an item's file from its title, so editing a title renames the
# file and `bin/docket release` renames every item whose title has drifted. The
# fallback walks that file's history, and a walk that does not follow renames
# sees only as far back as the rename: `PL-3D2M` was renamed by the v0.3.9
# release commit and `bin/docket record` declined to write its number
# (`PL-S5LB`).


def _rename_runner(commits: tuple[tuple[str, str, str, str], ...], items_dir: str = "docs/items"):
    """A git whose item file changed its name partway through its own history.

    `commits` is newest first, as (revision, subject, path, text): the name the
    item file had in that commit's tree and what it read there. One path per
    commit is the whole of it - a file is at one name in one tree - and that is
    what makes `show <rev>^:<path>` answer the way git does, because a commit's
    parent is simply the next entry and holds the file under whatever name that
    entry names.

    The `log` answer is the one git really gives for the walk's own arguments,
    so a test fails here for the reason the defect failed for: the history
    reaches past the rename, and each entry carries the name the file had at
    that commit, which is the half `--follow` does not supply. The base's own
    subjects lead with no id, so the subject scan in `_merges_naming` cannot
    answer and the file's history is what is left - which is the path under
    test.
    """
    paths = [f"{items_dir}/{path}" for _, _, path, _ in commits]

    def entry(at: int) -> list[str]:
        """The `--name-status` fields for a commit, against its parent's name."""
        if at + 1 >= len(commits):
            return ["A", paths[at]]
        if paths[at] != paths[at + 1]:
            return ["R100", paths[at + 1], paths[at]]
        return ["M", paths[at]]

    def run(args: list[str], root: Path) -> str:
        if args[0] == "rev-parse":
            return "" if args[-1] == "--is-shallow-repository" else f"{BASE}\n"
        if args[0] == "for-each-ref":
            return f"{BASE}\n"
        if args[0] == "show":
            revision, _, path = args[-1].partition(":")
            named = revision.rstrip("^")
            at = (
                0
                if named == BASE
                else next(
                    (index for index, commit in enumerate(commits) if commit[0] == named),
                    len(commits),
                )
            )
            at += len(revision) - len(named)
            return commits[at][3] if at < len(commits) and paths[at] == path else ""
        if args[0] == "diff" and "--name-only" in args:
            # The paths a commit changed, which is how a closure that landed
            # with its work is told from one that landed without it. Every
            # commit in these histories carries work, which is what a closure
            # written in the same commit as the work looks like.
            return "src/changed.py\n"
        if args[0] != "log":
            return ""
        if "--" not in args:
            # The base's own subjects, naming no id - so only the file answers.
            return "".join(f"c{at}\x1f{commit[1]}\n" for at, commit in enumerate(commits))
        return _z_name_status(
            tuple(
                (revision, subject, entry(at))
                for at, (revision, subject, _, _) in enumerate(commits)
            )
        )

    return run


RENAMED = (
    ("c0", "Ship v0.3.9 (#313)", "PL-K7QX-the-new-title.md", CLOSED.format(id="PL-K7QX")),
    ("c1", "Design the thing (#204)", "PL-K7QX-the-old-title.md", CLOSED.format(id="PL-K7QX")),
    ("c2", "Capture it (#100)", "PL-K7QX-the-old-title.md", OPEN_ITEM.format(id="PL-K7QX")),
)


def test_a_rename_after_the_closure_does_not_steal_the_attribution() -> None:
    """The renaming commit is not the closure, however the walk stops at it.

    Without rename detection the oldest commit the walk can see is the rename,
    whose parent does not hold the new path at all - so it reads as "done here,
    not done there", which is exactly the closure test, and the release that
    renamed the file answers for the pull request that did the work.
    """
    run = _rename_runner(RENAMED)

    numbers = closures_on_base(ROOT, {"PL-K7QX": "PL-K7QX-the-new-title.md"}, runner=run).numbers

    assert numbers == {"PL-K7QX": 204}


def test_a_rename_carrying_no_number_does_not_silence_the_closure_behind_it() -> None:
    """The same defect's quieter half: declining rather than answering wrongly.

    `bin/docket release` stamps `milestone:` onto every item it ships, which
    renames whatever titles have drifted - and its own subject carries no
    number until it is squashed. `PL-3D2M` was renamed that way and `bin/docket
    record` printed nothing at all for it, so the omission was visible only by
    reading the store afterwards.
    """
    run = _rename_runner((("c0", "Ship v0.3.9", *RENAMED[0][2:]), *RENAMED[1:]))

    numbers = closures_on_base(ROOT, {"PL-K7QX": "PL-K7QX-the-new-title.md"}, runner=run).numbers

    assert numbers == {"PL-K7QX": 204}


RENAMED_THEN_STAMPED = (
    ("d0", "Release v0.4.0 (#320)", "PL-K7QX-the-new-title.md", CLOSED.format(id="PL-K7QX")),
    ("d1", "Chart the other thing (#319)", "PL-K7QX-the-new-title.md", CLOSED.format(id="PL-K7QX")),
    ("d2", "Design the thing (#313)", "PL-K7QX-the-old-title.md", CLOSED.format(id="PL-K7QX")),
    ("d3", "Capture it (#100)", "PL-K7QX-the-old-title.md", OPEN_ITEM.format(id="PL-K7QX")),
)


def test_a_renamed_item_file_recovers_its_own_pull_request() -> None:
    """The shape observed on this repository, where two commits sit on the rename.

    `PL-3D2M` closed in `#313`, was renamed in passing by `#319` - a pull
    request for another item entirely, which stamped a title whose slug had
    drifted - and was then modified again by the `v0.3.9` release commit. So the
    walk has to pass a commit that changes the file without renaming it, and a
    commit that renames it, before reaching the closure. Both are rejected for
    their own reason: the release finds the item already done in its parent, and
    the rename does too once the parent is read at the name it had there.
    """
    run = _rename_runner(RENAMED_THEN_STAMPED)

    numbers = closures_on_base(ROOT, {"PL-K7QX": "PL-K7QX-the-new-title.md"}, runner=run).numbers

    assert numbers == {"PL-K7QX": 313}


# --- the branch whose pull request already merged ----------------------------
#
# `PL-8M8H`. `disposition` picked between four states from the commit counts,
# and a squash merge leaves the branch containing none of the commits that
# landed its content - so a merged branch that gains one commit reads `ahead=1,
# behind=N`, which is `MERGE`. That is what the session holding `#284`'s
# follow-up commit was told, and merging the base in and pushing is what it did;
# nothing merges a merged pull request again, so the commit landed nowhere.


def _landed_runner(
    *,
    branch: str = "claude/pl-k7qx-live",
    behind: int = 2,
    ahead: int = 1,
    adds: tuple[tuple[str, str], ...] = (),
    on_base: frozenset[str] = frozenset(),
    commits: tuple[tuple[str, tuple[str, ...]], ...] = (),
    divergence: str = "",
):
    """A git holding a branch position *and* the content behind it.

    `_branch_runner` answers the counts and nothing else, which is all the four
    original states needed. This one also answers the three reads the landing
    verdict makes: the blobs the base's history holds (`adds` and `on_base`
    together decide the split), the two-dot numstat, and the commit walk
    (`commits`, as subject and paths, newest first).

    `adds` is `(blob oid, path)` for each path the branch introduces since its
    fork point; `on_base` names the oids the base has held at some point, which
    is the whole of what separates a merged branch from one still carrying work.
    """

    def run(args: list[str], root: Path) -> str:
        if args[:3] == ["rev-parse", "--abbrev-ref", "HEAD"]:
            return f"{branch}\n"
        if args[0] == "rev-parse":
            return f"{args[-1]}\n" if args[-1] == BASE else ""
        if args[0] == "merge-base":
            return "0123456789abcdef\n"
        if args[:3] == ["rev-list", "--left-right", "--count"]:
            return f"{behind}\t{ahead}\n"
        if args[:2] == ["rev-list", "--objects"]:
            return "\n".join(f"{oid} {path}" for oid, path in adds if oid in on_base)
        if args[:2] == ["diff", "--raw"]:
            return "\n".join(f":000000 100644 {'0' * 40} {oid} A\t{path}" for oid, path in adds)
        if args[:2] == ["diff", "--numstat"]:
            # Every outstanding path still differs from the base's tip, which
            # is what a branch genuinely carrying work looks like.
            return ""
        if args[:2] == ["log", "--topo-order"]:
            return divergence
        if "--name-only" in args:
            return "".join(
                "\x1e" + f"c{position}" + "\x1f" + subject + "\n" + "\n".join(paths) + "\n"
                for position, (subject, paths) in enumerate(commits)
            )
        if args[0] == "log":
            return ""
        return ""

    return run


#: One squash-merged commit: the base's history holds the blob it introduced.
MERGED_WHOLE = {
    "adds": (("a1", "src/landed.py"),),
    "on_base": frozenset({"a1"}),
    "commits": (("PL-K7QX the work the pull request took", ("src/landed.py",)),),
}


def test_a_branch_whose_work_the_base_already_holds_is_told_to_restart() -> None:
    """The defect, in its smallest form: `MERGE` where the truth is `LANDED`.

    The counts say `behind=2, ahead=1`, which is `MERGE` under the old rule and
    was for every squash-merged branch, because `RESTART` fires at `ahead == 0`
    and a squash leaves the branch containing all of its own commits.
    """
    state = branch_state(ROOT, runner=_landed_runner(**MERGED_WHOLE))

    assert (state.behind, state.ahead) == (2, 1)
    assert state.landed_whole is True
    assert state.disposition == "landed"


def test_a_branch_carrying_work_the_base_has_never_held_still_merges() -> None:
    """The ordinary case, which must not move: work of its own, on a base that moved."""
    state = branch_state(
        ROOT,
        runner=_landed_runner(
            adds=(("b1", "src/live.py"),),
            on_base=frozenset(),
            commits=(("PL-K7QX the work this session is doing", ("src/live.py",)),),
        ),
    )

    assert state.landed_whole is False
    assert state.disposition == "merge"


def test_a_landed_commit_that_only_wrote_to_the_queue_is_not_merge_evidence() -> None:
    """Two sessions running `bin/docket record` write identical lines (`PL-JBRC`).

    Convergence is not a merge, and the recovery a `landed` verdict leads to
    deletes the ref - so the queue-only narrowing `orphaned` already carries is
    inherited rather than re-derived, which is what the project owner's
    part-two decision requires.
    """
    state = branch_state(
        ROOT,
        runner=_landed_runner(
            adds=(("a1", "docs/items/PL-K7QX-recorded.md"),),
            on_base=frozenset({"a1"}),
            commits=(
                (
                    "PL-K7QX record the merged pull request number",
                    ("docs/items/PL-K7QX-recorded.md",),
                ),
            ),
        ),
    )

    assert state.landed_whole is False
    assert state.disposition == "merge"


def test_a_rewritten_history_outranks_the_landed_verdict() -> None:
    """A rewrite changes every hash and no byte, so content cannot tell it from a merge.

    `PL-Y31G` is one of the two false-positive shapes the part-two decision
    names. Ordering `LANDED` below `REWRITTEN` excludes it at no cost, and the
    recovery matters: the rewritten block keeps commits held nowhere else,
    where a restart discards them.
    """
    state = branch_state(
        ROOT, runner=_landed_runner(behind=3, ahead=3, divergence=REWRITE, **MERGED_WHOLE)
    )

    assert state.disposition == "rewritten"


def test_the_landing_verdict_is_not_asked_where_it_could_not_change_the_advice() -> None:
    """Three git calls the session-start hook would pay on every session for nothing.

    `CURRENT`, `PULL`, `RESTART` and `REWRITTEN` are unaffected by the content,
    so only the arm that would otherwise say `MERGE` asks.
    """
    asked: list[list[str]] = []
    inner = _landed_runner(behind=4, ahead=0, **MERGED_WHOLE)

    def run(args: list[str], root: Path) -> str:
        asked.append(args)
        return inner(args, root)

    state = branch_state(ROOT, runner=run)

    assert state.disposition == "restart"
    assert state.landed_whole is False
    assert not any(args[:2] == ["rev-list", "--objects"] for args in asked)


def test_the_landed_branch_line_refuses_the_merge_it_replaces() -> None:
    """`MERGE` is the `else` fallthrough, so a state with no arm renders as its advice.

    That is the one way this change could fail silently: the right verdict
    printing the wrong instruction, with no error anywhere.
    """
    from docket.render import format_branch_state

    printed = format_branch_state(
        BranchState(
            branch="claude/pl-k7qx-live",
            base=BASE,
            behind=2,
            ahead=1,
            landed_whole=True,
            fetched=True,
        )
    )

    assert f"git merge {BASE}" not in printed
    assert "its pull request merged" in printed
    assert f"git checkout -B claude/pl-k7qx-live {BASE}" in printed
    assert f"git diff {BASE}...HEAD" in printed


# --- the release cut's own window -------------------------------------------


def _cut_window_runner(
    *, added: tuple[str, ...] = (), landed: tuple[str, ...] = (), fork: str = "abc123"
):
    """A git whose `HEAD` introduces `added` notes files and whose base gained `landed`."""

    def run(args: list[str], root: Path) -> str:
        if args[:2] == ["rev-parse", "--verify"]:
            return f"{BASE}\n" if args[-1] == BASE else ""
        if args[0] == "rev-parse":
            return f"{BASE}\n" if args[-1] == BASE else ""
        if args[:2] == ["diff", "--name-only"]:
            return "\n".join(added)
        if args[0] == "merge-base":
            return f"{fork}\n" if fork else ""
        if args[0] == "log":
            return "\n".join(f"{identifier} Something that landed" for identifier in landed)
        return ""

    return run


def test_a_checkout_carrying_a_cut_names_the_version_and_what_landed_since() -> None:
    """The seam `PL-028F` describes: notes written at the cut, tag on the merge."""
    window = cut_window(
        ROOT,
        runner=_cut_window_runner(
            added=("docs/releases/v0.3.8.md",), landed=("PL-D9WD", "PL-66FP")
        ),
    )

    assert window.version == "0.3.8"
    assert window.landed == ("PL-D9WD", "PL-66FP")
    assert window.declined == ""


def test_a_checkout_cutting_nothing_carries_no_window() -> None:
    """One session in a release cuts; every other one pays a single `git diff`."""
    window = cut_window(ROOT, runner=_cut_window_runner(landed=("PL-D9WD",)))

    assert (window.version, window.landed, window.declined) == ("", (), "")


def test_a_cut_whose_fork_point_is_unreadable_declines_rather_than_reading_as_empty() -> None:
    """Empty would mean "nothing landed in the window", which is the wrong answer."""
    window = cut_window(
        ROOT, runner=_cut_window_runner(added=("docs/releases/v0.3.8.md",), fork="")
    )

    assert window.version == "0.3.8"
    assert window.landed == ()
    assert "no readable history" in window.declined


# `filed_with_work`: the shape `PL-3CBS`'s landed-work advisory cannot reach -
# an item captured and worked in one commit, which never passes through `ready`
# and so never acquires the `verify:` command that advisory is keyed on.


def _filing_runner(shallow: str, log: str, changed: dict[str, list[str]] | None = None):
    """Git for a store whose item files were added by the commits `log` describes."""

    def run(args: list[str], root: Path) -> str:
        if args[:2] == ["rev-parse", "--is-shallow-repository"]:
            return shallow + "\n" if shallow else ""
        if args[0] == "rev-parse":
            return "origin/main\n"
        if args[0] == "log":
            return log
        if args[0] == "show":
            return "\n".join((changed or {}).get(args[-1], []))
        return ""

    return run


# #635's shape: one commit files six items and lands 385 lines of `vcs.py`.
# `PL-QQQQ` is the item the same commit filed and did not name - the ordinary
# capture in passing, and the case the subject clause exists to suppress.
FILED_LOG = "".join(
    (
        "\x00ff4be610\x01PL-XD3C, PL-MMVF, PL-0J9K: make digest's git calls",
        " measurable (#635)\n\n",
        "A\tdocs/items/PL-0J9K-git-cat-file-batch.md\n",
        "A\tdocs/items/PL-MMVF-memoize-the-runner.md\n",
        "A\tdocs/items/PL-QQQQ-something-else-entirely.md\n",
    )
)

FILED_CHANGED = {
    "ff4be610": [
        "docs/items/PL-0J9K-git-cat-file-batch.md",
        "docs/items/PL-MMVF-memoize-the-runner.md",
        "subprojects/docket/src/docket/vcs.py",
        "subprojects/docket/tests/test_vcs.py",
    ]
}


def test_an_item_filed_by_a_commit_that_also_changed_code_is_reported() -> None:
    report = filed_with_work(
        frozenset({"PL-0J9K"}),
        ROOT,
        prefix="docs/items",
        runner=_filing_runner("false", FILED_LOG, FILED_CHANGED),
    )

    assert report.known
    filing = report.filings["PL-0J9K"]
    assert filing.commit == "ff4be610"
    assert filing.pull_request == 635
    assert filing.paths == (
        "subprojects/docket/src/docket/vcs.py",
        "subprojects/docket/tests/test_vcs.py",
    )


def test_an_item_the_filing_subject_does_not_name_is_not_reported() -> None:
    """The clause that does the work: without it this matched 248 of 319 open items.

    `PL-QQQQ` was filed by the same commit and is not named by it - the ordinary
    case of a finding captured while doing unrelated work, which `CLAUDE.md`
    asks for and which is 78% of this store (`PL-SWP3`).
    """
    report = filed_with_work(
        frozenset({"PL-QQQQ"}),
        ROOT,
        prefix="docs/items",
        runner=_filing_runner("false", FILED_LOG, FILED_CHANGED),
    )

    assert report.known
    assert report.filings == {}


def test_a_pure_capture_commit_is_not_reported() -> None:
    """A commit whose whole diff is the queue worked nothing, however it is titled."""
    report = filed_with_work(
        frozenset({"PL-0J9K"}),
        ROOT,
        prefix="docs/items",
        runner=_filing_runner(
            "false", FILED_LOG, {"ff4be610": ["docs/items/PL-0J9K-git-cat-file-batch.md"]}
        ),
    )

    assert report.known
    assert report.filings == {}


def test_a_shallow_clone_declines_rather_than_reporting_nothing_filed() -> None:
    """Its missing commits are the oldest, so an old item would read as filed by nobody."""
    report = filed_with_work(
        frozenset({"PL-0J9K"}),
        ROOT,
        prefix="docs/items",
        runner=_filing_runner("true", FILED_LOG, FILED_CHANGED),
    )

    assert not report.known
    assert "shallow" in report.declined
    assert report.filings == {}


def test_a_checkout_with_no_readable_history_declines() -> None:
    report = filed_with_work(
        frozenset({"PL-0J9K"}), ROOT, prefix="docs/items", runner=_filing_runner("false", "")
    )

    assert not report.known
    assert "no default branch" in report.declined


def test_no_untriaged_items_asks_git_nothing() -> None:
    asked: list[list[str]] = []

    def run(args: list[str], root: Path) -> str:
        asked.append(args)
        return ""

    assert filed_with_work(frozenset(), ROOT, prefix="docs/items", runner=run).known
    assert asked == []


def test_a_claim_says_whether_the_base_holds_the_item_at_all() -> None:
    """Both claims stand; only what a reader is told about them differs (`PL-3CTW`)."""
    report = branches_in_flight(
        ROOT,
        runner=_runner(
            ["claude/held", "claude/filed"],
            commits={
                "claude/held": [("2026-09-19", "PL-K7QX: work the item")],
                "claude/filed": [("2026-09-19", "PL-3CTW: file it, and work something else")],
            },
            statuses={"PL-K7QX": "ready"},
        ),
    )

    # Nothing is withdrawn: the measurement on the item refuses that at every
    # width tried, so the claim stands and only the wording turns on this.
    assert report.ids == {"PL-K7QX", "PL-3CTW"}
    assert {branch.item_id: branch.on_base for branch in report.branches} == {
        "PL-K7QX": True,
        "PL-3CTW": False,
    }


def test_the_digest_sends_an_unlanded_claim_to_stranded_rather_than_refusing_it() -> None:
    """The two lines that used to contradict each other about one branch (`PL-3CTW`)."""
    flight = FlightReport(
        branches=(
            Branch(name="origin/claude/held", item_id="PL-K7QX", on_base=True),
            Branch(name="origin/claude/filed", item_id="PL-3CTW", on_base=False),
        ),
        base="origin/main",
    )

    lines = _digest(flight=flight).splitlines()

    carried = [line for line in lines if "In flight on a branch" in line]
    assert len(carried) == 1
    assert "PL-K7QX" in carried[0]
    assert "PL-3CTW" not in carried[0]

    named = [line for line in lines if "PL-3CTW" in line]
    assert named
    assert all("In flight on a branch" not in line for line in named)
    assert any("bin/docket stranded" in line for line in named)
    assert not any("do not start" in line for line in lines)


def test_flight_marks_a_claim_whose_item_the_base_does_not_hold() -> None:
    """`bin/docket flight` is the command the digest sends a reader to (`PL-3CTW`)."""
    from docket.render import format_flight

    report = FlightReport(
        branches=(
            Branch(name="origin/claude/filed", item_id="PL-3CTW", on_base=False),
            Branch(name="origin/claude/held", item_id="PL-K7QX", on_base=True),
        ),
        base="origin/main",
    )

    lines = format_flight(report, datetime(2026, 9, 19, tzinfo=UTC)).splitlines()

    assert "filed there" in next(line for line in lines if "PL-3CTW" in line)
    assert "filed there" not in next(line for line in lines if "PL-K7QX" in line)
    assert any("bin/docket stranded" in line for line in lines)


def _carrying(*branches: Branch, unreadable: tuple[str, ...] = ()) -> FlightReport:
    return FlightReport(branches=branches, unreadable=unreadable, base=BASE)


def test_a_settled_branch_is_named_apart_from_the_live_ones() -> None:
    """The row leaves the list the age is meant to separate, and says why."""
    from docket.render import format_flight

    report = _carrying(
        Branch("origin/claude/finished", "PL-NB35", datetime(2026, 9, 13, tzinfo=UTC)),
        Branch("origin/claude/working", "PL-VV16", datetime(2026, 9, 21, tzinfo=UTC)),
    )
    settled = SettledReport(
        branches=(
            SettledBranch(
                "origin/claude/finished", ("PL-NB35",), datetime(2026, 9, 13, tzinfo=UTC)
            ),
        )
    )
    printed = format_flight(report, datetime(2026, 9, 21, tzinfo=UTC), settled)
    live, _, finished = printed.partition("On 1 branch every item it carries is already closed")
    assert "origin/claude/working" in live
    assert "origin/claude/finished" not in live
    assert "origin/claude/finished" in finished
    assert "no pull request is open for it" in finished
    assert "Nothing here is being worked" in finished
    # The one reading it must never invite, however the rest is worded.
    assert "safe to merge" not in printed
    assert "ready to merge" not in printed


def test_an_unasked_reading_says_a_pull_request_may_be_open() -> None:
    from docket.render import format_flight

    printed = format_flight(
        _carrying(Branch("origin/claude/finished", "PL-NB35", datetime(2026, 9, 13, tzinfo=UTC))),
        datetime(2026, 9, 21, tzinfo=UTC),
        SettledReport(
            branches=(
                SettledBranch(
                    "origin/claude/finished", ("PL-NB35",), datetime(2026, 9, 13, tzinfo=UTC)
                ),
            ),
            asked=False,
        ),
    )
    assert "no pull request is open" not in printed
    assert "could not be read here" in printed
    assert "Nothing here is being worked" in printed


def test_a_report_whose_every_branch_has_finished_says_so_rather_than_nothing() -> None:
    """`No branch claims an item` would be false: one does, and it is finished."""
    from docket.render import format_flight

    printed = format_flight(
        _carrying(Branch("origin/claude/finished", "PL-NB35", datetime(2026, 9, 13, tzinfo=UTC))),
        datetime(2026, 9, 21, tzinfo=UTC),
        SettledReport(
            branches=(
                SettledBranch(
                    "origin/claude/finished", ("PL-NB35",), datetime(2026, 9, 13, tzinfo=UTC)
                ),
            )
        ),
    )
    assert "No branch claims an item" not in printed
    assert "No branch is carrying an item anybody is still working." in printed


#: The instant `PL-3QM9` was observed at, which every age below is read from.
READ_AT = datetime(2026, 9, 21, 0, 29, tzinfo=UTC)


def _row_aged(last_commit: datetime | None, reviews: OpenPullRequests | None = None) -> str:
    """The one row `flight` prints for a branch whose last commit is `last_commit`."""
    from docket.render import format_flight

    report = _carrying(Branch("origin/claude/working", "PL-VV16", last_commit))
    return format_flight(report, READ_AT, None, reviews).splitlines()[2]


@pytest.mark.parametrize(
    ("elapsed", "said"),
    [
        (timedelta(seconds=30), "last commit under a minute ago"),
        # Two clocks disagree by seconds, and a session's own commit read back a
        # moment later is not a clock fault.
        (timedelta(seconds=-30), "last commit under a minute ago"),
        (timedelta(minutes=1), "last commit 1 minute ago"),
        (timedelta(minutes=59, seconds=59), "last commit 59 minutes ago"),
        (timedelta(hours=1), "last commit 1 hour ago"),
        (timedelta(hours=23, minutes=59), "last commit 23 hours ago"),
        (timedelta(hours=24), "last commit 1 day ago"),
        (timedelta(days=3, hours=23), "last commit 3 days ago"),
    ],
)
def test_an_age_is_elapsed_time_in_the_unit_its_size_calls_for(
    elapsed: timedelta, said: str
) -> None:
    """Rounded down at every boundary, which reads a branch younger rather than older."""
    assert _row_aged(READ_AT - elapsed).endswith(said)


def test_a_commit_across_midnight_is_aged_by_the_clock_not_the_calendar() -> None:
    """`PL-3QM9`: 54 minutes before the read, and the day before it."""
    row = _row_aged(datetime(2026, 9, 20, 23, 34, 46, tzinfo=UTC))
    assert row.endswith("last commit 54 minutes ago")


def test_an_age_is_measured_across_offsets_as_one_instant() -> None:
    """Two sessions can be in two zones; the subtraction must not care."""
    minus_five = timezone(timedelta(hours=-5))
    row = _row_aged(datetime(2026, 9, 20, 19, 19, tzinfo=minus_five))
    assert row.endswith("last commit 10 minutes ago")


def test_a_commit_dated_after_now_says_a_clock_is_wrong_rather_than_giving_an_age() -> None:
    row = _row_aged(READ_AT + timedelta(minutes=5))
    assert row.endswith("last commit dated later than now - one of the two clocks is wrong")


def test_a_row_says_which_pull_request_is_open_on_its_branch() -> None:
    minutes_old = READ_AT - timedelta(minutes=7)
    asked = OpenPullRequests(numbers={"origin/claude/working": 757}, asked=True)
    unnumbered = OpenPullRequests(numbers={"origin/claude/working": None}, asked=True)
    none_open = OpenPullRequests(asked=True)

    assert _row_aged(minutes_old, asked).endswith(
        "last commit 7 minutes ago  pull request #757 open"
    )
    assert _row_aged(minutes_old, unnumbered).endswith("pull request open")
    assert _row_aged(minutes_old, none_open).endswith("no pull request open")
    # Not asked is not "none open": the row carries no clause at all.
    assert _row_aged(minutes_old, OpenPullRequests()).endswith("last commit 7 minutes ago")


def test_the_digest_says_how_long_each_branch_has_sat_rather_than_forbidding_it() -> None:
    """`PL-7TVT`: "do not start these again" presumed a session behind every branch."""
    from docket.render import format_digest

    flight = FlightReport(
        branches=(
            Branch("origin/claude/old", "PL-3CTW", READ_AT - timedelta(days=3, hours=2)),
            Branch("origin/claude/new", "PL-K7QX", READ_AT - timedelta(minutes=7)),
        ),
        base=BASE,
    )

    lines = format_digest(_store(), flight, now=READ_AT).splitlines()

    line = next(line for line in lines if "In flight on a branch" in line)
    assert "by time since its last commit: PL-3CTW 3 days, PL-K7QX 7 minutes." in line
    assert "not proof anybody is on it" in line
    assert "`bin/docket flight` adds each one's pull request" in line
    assert not any("do not start" in line for line in lines)


def _remotes_only(*remotes: str) -> Runner:
    """A git that knows these remotes and nothing else, which is all the match reads."""

    def run(args: list[str], root: Path) -> str:
        return "\n".join(remotes) if args[:1] == ["remote"] else ""

    return run


def test_a_tracking_ref_is_matched_to_the_branch_its_pull_request_names() -> None:
    report = _carrying(
        Branch("origin/claude/reviewing", "PL-NB35"), Branch("origin/claude/typing", "PL-VV16")
    )

    found = open_pull_requests(
        ROOT, report, opened=lambda: {"claude/reviewing": 757}, runner=_remotes_only("origin")
    )

    assert found.asked
    assert found.known
    assert dict(found.numbers) == {"origin/claude/reviewing": 757}


def test_a_forge_that_could_not_be_asked_is_not_read_as_none_open() -> None:
    report = _carrying(Branch("origin/claude/typing", "PL-VV16"))

    unasked = open_pull_requests(ROOT, report, runner=_remotes_only("origin"))
    refused = open_pull_requests(ROOT, report, opened=lambda: None, runner=_remotes_only("origin"))

    for reading in (unasked, refused):
        assert not reading.asked
        assert not reading.known


def test_the_forge_is_not_asked_when_no_branch_is_carrying_anything() -> None:
    def opened() -> dict[str, int | None]:
        raise AssertionError("asked the forge about nothing")

    assert not open_pull_requests(ROOT, _carrying(), opened=opened).asked


def test_unread_remotes_decline_rather_than_reading_every_branch_as_none_open() -> None:
    report = _carrying(Branch("origin/claude/reviewing", "PL-NB35"))

    def silent(args: list[str], root: Path) -> str:
        return SILENT

    found = open_pull_requests(ROOT, report, opened=lambda: {"claude/reviewing": 1}, runner=silent)

    assert not found.asked
    assert found.declined


# `change_landed`, the one test of whether the base already holds a change
# (`PL-GHHW`). Real repositories rather than `_runner`, because the whole
# question is what git's three-way merge makes of two histories, and a fake
# would only restate the answer the test exists to check. Every test builds
# the same shape: a branch ports a one-line fix, and the base takes the same
# fix through another pull request whose squash also carries more.
_LINES = "".join(f"{n}\n" for n in range(1, 31))


class _Repo:
    """A scratch repository on `main`, committing whole files."""

    def __init__(self, root: Path) -> None:
        self.root = root
        root.mkdir()
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "t@example.com")
        self.git("config", "user.name", "T")

    def git(self, *args: str) -> str:
        return subprocess.run(
            ["git", *args], cwd=self.root, check=True, capture_output=True, text=True
        ).stdout.strip()

    def commit(self, message: str, **files: str) -> str:
        for name, text in files.items():
            (self.root / name.replace("_", ".")).write_text(text, encoding="utf-8")
        self.git("add", "-A")
        self.git("commit", "-qm", message)
        return self.git("rev-parse", "HEAD")

    def read(self, name: str) -> str:
        return (self.root / name).read_text(encoding="utf-8")


def _edit(text: str, **replace: str) -> str:
    """`text` with each whole line named by its number replaced."""
    swapped = {f"{number[1:]}\n": f"{line}\n" for number, line in replace.items()}
    return "".join(swapped.get(line, line) for line in text.splitlines(keepends=True))


def _ported(tmp_path: Path) -> tuple[_Repo, str]:
    """A branch whose one commit ports line 10's fix, forked before the base took it."""
    repo = _Repo(tmp_path / "repo")
    repo.commit("seed", f_txt=_LINES)
    repo.git("checkout", "-qb", "port")
    port = repo.commit("PL-0001: port the fix", f_txt=_edit(_LINES, n10="ten"))
    repo.git("checkout", "-q", "main")
    return repo, port


def test_a_port_the_base_took_with_more_is_found_and_named(tmp_path: Path) -> None:
    """`PL-GHHW` itself: the squash carries the fix, another edit and 97 lines.

    Patch identity cannot see this, since the squash's diff is not the port's,
    and `_superseded` cannot either, since the base's copy is ahead of the
    branch's rather than a superset of it. The three-way replay can.
    """
    repo, port = _ported(tmp_path)
    more = "".join(f"{n}\n" for n in range(100, 197))
    landing = repo.commit(
        "PL-0002: the other fix, carrying the same line (#934)",
        f_txt=_edit(_LINES, n10="ten", n12="twelve") + more,
    )

    found = change_landed(port, "main", repo.root)

    assert found is not None
    assert found.commit == landing
    assert found.pull_request == 934


def test_a_change_the_base_took_and_then_rewrote_has_still_landed(tmp_path: Path) -> None:
    """Held once is held: the recovery would revert the rewrite, not restore work."""
    repo, port = _ported(tmp_path)
    took = repo.commit("PL-0002: the same fix (#934)", f_txt=_edit(_LINES, n10="ten"))
    repo.commit("PL-0003: rewrite the line (#935)", f_txt=_edit(_LINES, n10="TEN"))

    found = change_landed(port, "main", repo.root)

    assert found is not None
    assert found.commit == took


def test_a_silenced_replay_never_names_a_later_landing(tmp_path: Path) -> None:
    """Git not answering for the first holder is not the second one being first.

    Both base commits hold the change, so falling through to the second would
    still say "landed" - and name the wrong pull request.
    """
    repo, port = _ported(tmp_path)
    repo.commit("PL-0002: the same fix (#934)", f_txt=_edit(_LINES, n10="ten"))
    repo.commit("PL-0003: another line (#935)", f_txt=_edit(_LINES, n10="ten", n20="twenty"))
    replays = 0

    def first_replay_unanswered(args: list[str], root: Path) -> str:
        nonlocal replays
        if args[0] == "merge-tree":
            replays += 1
            if replays == 1:
                return SILENT
        return _run_git(args, root)

    found = change_landed(port, "main", repo.root)
    assert found is not None and found.pull_request == 934
    assert change_landed(port, "main", repo.root, runner=first_replay_unanswered) is None


def test_a_change_the_base_never_took_has_not_landed(tmp_path: Path) -> None:
    repo, port = _ported(tmp_path)
    repo.commit("PL-0002: something else (#934)", f_txt=_edit(_LINES, n20="twenty"))

    assert change_landed(port, "main", repo.root) is None


def test_a_conflict_reads_as_not_landed(tmp_path: Path) -> None:
    """The base changed the same line another way: git answers exit 1, never a tree."""
    repo, port = _ported(tmp_path)
    repo.commit("PL-0002: a different fix (#934)", f_txt=_edit(_LINES, n10="10.0"))

    assert change_landed(port, "main", repo.root) is None


def test_a_git_without_merge_base_reads_as_not_landed(tmp_path: Path) -> None:
    """Git before 2.40 has no `--merge-base`, so it answers nothing - never "landed"."""
    repo, port = _ported(tmp_path)
    repo.commit("PL-0002: the same fix (#934)", f_txt=_edit(_LINES, n10="ten"))

    def old_git(args: list[str], root: Path) -> str:
        return SILENT if args[0] == "merge-tree" else _run_git(args, root)

    assert change_landed(port, "main", repo.root) is not None
    assert change_landed(port, "main", repo.root, runner=old_git) is None


def _merged_with_a_port(tmp_path: Path) -> tuple[_Repo, str]:
    """`#938`'s shape: a branch's own work plus a port another pull request landed first.

    The branch commits its work and a port of a fix. The fix lands on the base
    through `#934`, which also carries more, and then the branch squash-merges
    as `#938` - which had nothing to carry for the ported file, so the base's
    copy of it is ahead of the branch's.
    """
    repo = _Repo(tmp_path / "repo")
    repo.commit("seed", f_txt=_LINES, g_txt="old\n")
    repo.git("checkout", "-qb", "claude/laughing")
    repo.commit("PL-0001: the work", g_txt="new\n")
    port = repo.commit("PL-0001: port the fix", f_txt=_edit(_LINES, n10="ten"))
    repo.git("checkout", "-q", "main")
    repo.commit(
        "PL-0002: the fix (#934)",
        f_txt=_edit(_LINES, n10="ten", n12="twelve") + "".join(f"{n}\n" for n in range(100, 197)),
    )
    repo.git("merge", "-q", "--squash", "claude/laughing")
    repo.git("commit", "-qm", "PL-0001: the work (#938)")
    return repo, port


def test_a_change_the_base_took_inside_a_larger_commit_is_not_left_behind(tmp_path: Path) -> None:
    """The finding `PL-GHHW` was filed on, with the checkout it would have printed."""
    repo, _ = _merged_with_a_port(tmp_path)

    report = orphaned(repo.root)

    assert report.known, report.declined
    assert report.branches == ()


def test_orphaned_still_reports_work_pushed_after_the_merge_beside_such_a_port(
    tmp_path: Path,
) -> None:
    """Only the port is cleared; a commit nothing took is still the finding."""
    repo, port = _merged_with_a_port(tmp_path)
    repo.git("checkout", "-q", "claude/laughing")
    lost = repo.commit("PL-0001: pushed after the merge", h_txt="lost\n")
    repo.git("checkout", "-q", "main")

    report = orphaned(repo.root)

    [branch] = report.branches
    assert [commit.commit for commit in branch.commits] == [lost]
    assert port not in {commit.commit for commit in branch.commits}
