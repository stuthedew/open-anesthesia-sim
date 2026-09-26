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
    change_landed,
    changed_items,
    changed_path_args,
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


def _bare(args: list[str]) -> list[str]:
    """`args` without the `-c core.quotePath=false` a changed-path read opens with.

    `changed_path_args` puts it ahead of the subcommand, where git reads it
    (`PL-8HSX`), and the fakes here dispatch on `args[0]` and index the words
    after it. Stripped before a fake records its call, so an assertion that no
    `log` was asked still sees one.
    """
    return args[2:] if args[:2] == ["-c", "core.quotePath=false"] else args


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


def _name_only(changes: tuple[str | tuple[str, str], ...], args: list[str]) -> str:
    """What `git diff --name-only` prints for `changes`, a rename given as `(old, new)`.

    Git pairs a deleted path with a similar added one and prints the pair as its
    new name alone. `--no-renames` prints the deletion and the addition, and it
    is what every read of which paths a change touched sends
    (`vcs.changed_path_args`). Measured on git 2.43.0, 2026-09-25: a retitle git
    scores `R078` prints one name under `--name-only` and both, sorted, under
    `--no-renames`. A fake that printed a rename one way whatever it was asked
    let a test pass against a git that does not behave that way (`PL-J16N`).
    """
    apart = "--no-renames" in args
    paths: list[str] = []
    for change in changes:
        if isinstance(change, tuple):
            paths.extend(change if apart else change[1:])
        else:
            paths.append(change)
    return "\n".join(sorted(paths))


def _runner(
    refs: list[str],
    merged: list[str] | None = None,
    unrelated: tuple[str, ...] = (),
    adds: dict[str, list[str] | list[tuple[str, str]]] | None = None,
    on_base: set[str] | None = None,
    touched: dict[str, list[tuple[str, tuple[str, ...]]]] | None = None,
    tips: dict[str, dict[str, tuple[str, str]]] | None = None,
    duplicated: tuple[str, ...] = (),
):
    """A git that holds `refs`, for `orphaned` to read.

    `unrelated` names the refs whose merge-base with the default branch does
    not resolve - a truncated clone's missing history, which git answers with
    a failure rather than an empty result.

    `tips` maps a ref to the two-dot diff between the default branch's tip and
    its own, per path, as `(added, deleted)` counts - which is what says whether
    a path `adds` reports as never landed is one the base is still missing.
    Left out, every such path differs by an addition, which is what a branch
    genuinely carrying work looks like.

    `duplicated` names the refs whose divergence from the default branch is one
    rewritten history: the same commits twice over, which content comparison
    cannot tell from a merge.

    `adds` maps a ref to the blobs it introduces since its fork point and
    `on_base` names the blobs the default branch has held at some point, which
    is what separates a branch whose work has landed from one still carrying
    it. `touched` maps a ref to its commits as (subject, paths), newest first,
    which is what `orphaned` reads to tell a commit the merge took from one
    nothing took.
    """

    def run(args: list[str], root: Path) -> str:
        args = _bare(args)
        if args[0] == "rev-parse":
            return f"{BASE}\n" if args[-1] == BASE else ""
        if args[0] == "for-each-ref":
            if any(arg.startswith("--merged=") for arg in args):
                return "\n".join(merged or [])
            return "\n".join(refs)
        if args[0] == "merge-base":
            return "" if args[-1] in unrelated else "0123456789abcdef\n"
        if args[0] == "rev-list" and "--objects" in args:
            # The object walk the landing split reads, in the shape git writes
            # it: one oid per line, a path after it for anything but a commit.
            return "\n".join(f"{blob} some/path/{blob}" for blob in sorted(on_base or set()))
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
            if "--name-only" in args:
                # `orphaned` decides on this walk - a commit *none* of whose
                # paths reached the base - so the fake has to answer it. The
                # record shape is git's: \x1e opens each, then the hash, \x1f,
                # the subject, then one path per line.
                walked = args[-2]
                return "".join(
                    "\x1e{}\x1f{}\n{}\n".format(f"{walked}@{position}", subject, "\n".join(paths))
                    for position, (subject, paths) in enumerate((touched or {}).get(walked, []))
                )
            wanted = [arg for arg in args if arg.startswith("--find-object=")]
            if wanted:
                held = wanted[0].split("=", 1)[1] in (on_base or set())
                return "fedcba9876543210\n" if held else ""
        return ""

    return run


HARNESS = "origin/claude/roadmap-release-write-failure-nhsjwo"


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
        args = _bare(args)
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
        args = _bare(args)
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
        args = _bare(args)
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
        args = _bare(args)
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


# --- which closures already stand on the base, and what the base records -----
#
# The number does not exist when the closure is committed - it travels with its
# work, which is what stops a merge taking the fix and leaving the item open -
# and the branch writes it onto the closure while its pull request is open,
# before the merge (`PL-HMZZ`). So the base is asked two things of one tree
# read per closure in question: does the closure stand there, and what does its
# copy record. Nothing here reads history; the readings that once derived the
# number from merge subjects and item-file history are gone with their tests.

CLOSED = "---\nid: {id}\ntitle: T\nstatus: done\n---\n"


OPEN_ITEM = "---\nid: {id}\ntitle: T\nstatus: ready\n---\n"


RECORDED_CLOSURE = "---\nid: {id}\ntitle: T\nstatus: done\npr: {pr}\n---\n"


def _base_tree_runner(on_base: dict[str, str], log: list[list[str]] | None = None):
    """A git whose default branch holds `on_base`, file name to text, and nothing else.

    `ls-tree` lists that same tree, which is what the read falls back to when a
    name does not resolve: an item the base holds under another name.
    """

    def run(args: list[str], root: Path) -> str:
        args = _bare(args)
        if log is not None:
            log.append(args)
        if args[0] == "rev-parse":
            return f"{BASE}\n" if args[-1] == BASE else ""
        if args[0] == "for-each-ref":
            return f"{BASE}\n"
        if args[0] == "show":
            revision, _, path = args[-1].partition(":")
            return on_base.get(path.split("/")[-1], "") if revision == BASE else ""
        if args[0] == "ls-tree":
            return "".join(
                f"100644 blob {index:040x}\tdocs/items/{name}\n"
                for index, name in enumerate(on_base)
            )
        return ""

    return run


def test_a_landed_closure_is_reported_with_the_number_the_base_records() -> None:
    run = _base_tree_runner({"PL-K7QX-a.md": RECORDED_CLOSURE.format(id="PL-K7QX", pr=148)})

    report = closures_on_base(ROOT, {"PL-K7QX": "PL-K7QX-a.md"}, runner=run)

    assert report.landed == frozenset({"PL-K7QX"})
    assert report.unlanded == frozenset()
    assert report.numbers == {"PL-K7QX": 148}


def test_a_landed_closure_the_base_holds_without_a_number_records_none() -> None:
    # A closure that reached the base before the rule, or past the check: the
    # caller's error, and nothing here guesses a number for it.
    run = _base_tree_runner({"PL-K7QX-a.md": CLOSED.format(id="PL-K7QX")})

    report = closures_on_base(ROOT, {"PL-K7QX": "PL-K7QX-a.md"}, runner=run)

    assert report.landed == frozenset({"PL-K7QX"})
    assert report.numbers == {}


def test_a_closure_the_base_holds_open_is_still_in_flight() -> None:
    run = _base_tree_runner({"PL-K7QX-a.md": OPEN_ITEM.format(id="PL-K7QX")})

    report = closures_on_base(ROOT, {"PL-K7QX": "PL-K7QX-a.md"}, runner=run)

    assert report.landed == frozenset()
    assert report.unlanded == frozenset({"PL-K7QX"})


def test_a_closure_the_base_has_no_copy_of_is_in_flight_too() -> None:
    # An item captured and closed on the same branch: no file on the base, and
    # the fallback finds no other name for it either.
    report = closures_on_base(ROOT, {"PL-K7QX": "PL-K7QX-a.md"}, runner=_base_tree_runner({}))

    assert report.known
    assert report.unlanded == frozenset({"PL-K7QX"})


def test_a_closure_the_base_holds_under_another_name_is_read_there() -> None:
    """A title edit renames the file, and a landed closure must not read as unlanded.

    Harmless while nothing wrote on the strength of it; `docket record N` now
    does, and would have replaced this closure's `pr: 148` with the branch's own
    number.
    """
    log: list[list[str]] = []
    run = _base_tree_runner(
        {"PL-K7QX-the-old-title.md": RECORDED_CLOSURE.format(id="PL-K7QX", pr=148)}, log
    )

    report = closures_on_base(ROOT, {"PL-K7QX": "PL-K7QX-the-new-title.md"}, runner=run)

    assert report.landed == frozenset({"PL-K7QX"})
    assert report.numbers == {"PL-K7QX": 148}
    assert [args for args in log if args[0] == "ls-tree"], "the base's ids were never listed"


def test_the_base_s_ids_are_listed_only_when_a_name_fails_to_resolve() -> None:
    # One `git show` per closure is the whole cost on a healthy store.
    log: list[list[str]] = []
    run = _base_tree_runner({"PL-K7QX-a.md": CLOSED.format(id="PL-K7QX")}, log)

    closures_on_base(ROOT, {"PL-K7QX": "PL-K7QX-a.md"}, runner=run)

    assert not [args for args in log if args[0] == "ls-tree"]


def test_no_closure_in_question_costs_no_tree_read() -> None:
    log: list[list[str]] = []

    closures_on_base(ROOT, {}, runner=_base_tree_runner({}, log))

    assert not [args for args in log if args[0] in ("show", "ls-tree", "log")]


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
    touched: tuple[str | tuple[str, str], ...],
    trees: dict[str, str],
    *,
    resolves: bool = True,
    parent: bool = True,
    log: list[list[str]] | None = None,
):
    """A git whose `trees` map `<ref>:<path>` to the text held there.

    `touched` is what the commit changed under the item directory, which is
    what `git diff --name-only` against the first parent answers, a rename
    listed as `_name_only` says git lists it. `resolves` and `parent` are the
    two ways the read declines: a revision this checkout does not hold, and
    one whose parent it does not hold.
    """

    def run(args: list[str], root: Path) -> str:
        args = _bare(args)
        if log is not None:
            log.append(args)
        if args[0] == "rev-parse":
            if args[-1].startswith(f"{REV}^^"):
                return f"{REV}~1\n" if parent else ""
            return f"{REV}\n" if resolves else ""
        if args[0] == "diff":
            return _name_only(touched, args)
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
        (("items/PL-K7QX-old.md", "items/PL-K7QX-new.md"),),
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
        args = _bare(args)
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
        args = _bare(args)
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
        args = _bare(args)
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
            ref = next(arg for arg in args if "..." in arg).split("...")[-1]
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
    committed: tuple[str | tuple[str, str], ...] = (),
    uncommitted: tuple[str | tuple[str, str], ...] = (),
    base_paths: tuple[str, ...] = (),
):
    """A git whose base holds `on_base`, keyed by the path the base stores it under.

    `committed` and `uncommitted` are the paths the two diffs report, so a case
    can put an edit in either place, a rename listed as `_name_only` says git
    lists it. `base_paths` is what `ls-tree` lists, which defaults to the keys
    of `on_base` and is given explicitly only where a test needs the base to
    hold a path the tree does not.
    """
    listing = base_paths or tuple(on_base)

    def run(args: list[str], _root: Path) -> str:
        args = _bare(args)
        if args[0] == "rev-parse":
            return "aaa111\n"
        if args[0] == "diff":
            paths = committed if any(arg.endswith("...HEAD") for arg in args) else uncommitted
            return _name_only(paths, args)
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
        committed=(("docs/items/PL-K7QX-old-title.md", "docs/items/PL-K7QX-new-title.md"),),
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
        args = _bare(args)
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
        if args[0] == "diff" and "--raw" in args:
            return "\n".join(f":000000 100644 {'0' * 40} {oid} A\t{path}" for oid, path in adds)
        if args[0] == "diff" and "--numstat" in args:
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
        args = _bare(args)
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
        args = _bare(args)
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


def test_a_changed_path_read_prints_a_path_outside_ascii_as_written(tmp_path: Path) -> None:
    """`changed_path_args` turns `core.quotePath` off for every read it builds (`PL-8HSX`).

    Left on, git printed `src/anesthesia_sim/core/café.py` as
    `"src/anesthesia_sim/core/caf\\303\\251.py"`, quotes included, and matched
    against that, `verify`'s protected-path audit passed the file as "none
    touched". `claims.work_under_record` was the one reader spelling its own
    `-c`, and now relies on this one.
    """
    repo = _Repo(tmp_path / "repo")
    repo.commit("seed", seed_txt="seed\n")
    core = repo.root / "src" / "anesthesia_sim" / "core"
    core.mkdir(parents=True)
    (core / "café.py").write_text("VALUE = 1\n", encoding="utf-8")
    repo.git("add", "-A")
    repo.git("commit", "-qm", "add a core module")

    listing = _run_git(changed_path_args("diff", "--name-only", "HEAD~1", "HEAD"), repo.root)

    assert listing.splitlines() == ["src/anesthesia_sim/core/café.py"]


def test_a_path_that_is_not_utf8_reads_as_unanswered_rather_than_raising(tmp_path: Path) -> None:
    """Printed as written, a Latin-1 `café.py` is a byte no UTF-8 decode reads (`PL-8HSX`).

    Quoted, it had been `"caf\\351.py"`; unquoted, `subprocess.run` raised out
    of `_run_git`, whose contract is that nothing does.
    """
    repo = _Repo(tmp_path / "repo")
    repo.commit("seed", seed_txt="seed\n")
    blob = repo.git("hash-object", "-w", "seed.txt").encode()
    # Through the index alone, so no filesystem is asked to hold the name.
    cacheinfo = b"100644," + blob + b",caf\xe9.py"
    subprocess.run(
        [b"git", b"update-index", b"--add", b"--cacheinfo", cacheinfo], cwd=repo.root, check=True
    )
    repo.git("commit", "-qm", "add a Latin-1 name")

    listing = _run_git(changed_path_args("diff", "--name-only", "HEAD~1", "HEAD"), repo.root)

    assert listing is SILENT


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


# --- a subject is one line, whatever it holds (`PL-139L`) --------------------
#
# `str.splitlines` breaks at `\x0b`, `\x0c`, `\x1c`-`\x1e`, `\x85`, U+2028 and
# U+2029 as well as at a newline, and git prints every one of them unchanged
# inside `%s`. So each reader of subject-bearing log output splits on `\n`
# alone, and the text after a pasted form feed cannot read as a subject of its
# own - one opening with an id, or ending with a pull request's number.

#: Every character `str.splitlines` breaks at that git does not.
LINE_BREAKS_GIT_DOES_NOT_MAKE = ("\x0b", "\x0c", "\x1c", "\x1d", "\x1e", "\x85", "\u2028", "\u2029")


@pytest.mark.parametrize("separator", LINE_BREAKS_GIT_DOES_NOT_MAKE)
def test_a_line_separator_inside_a_subject_does_not_start_another_subject(
    tmp_path: Path, separator: str
) -> None:
    """Read through git itself, which is what puts the separator in the subject.

    The first two subjects name a number only past the separator, or only
    before it, so a reader cutting there finds merges git never recorded. The
    third is the control: the number a whole subject ends with is found.
    """
    repo = _Repo(tmp_path / "repo")
    repo.commit("seed", seed_txt="0\n")
    repo.commit(f"PL-0001: quote a title{separator}Merge pull request #99 from a/b", seed_txt="1\n")
    repo.commit(f"PL-0002: land the fix (#12){separator}and say why", seed_txt="2\n")
    repo.commit(f"PL-0003: quote a title{separator}and land it (#34)", seed_txt="3\n")

    history = merged_pull_requests(repo.root)

    assert history.known, history.declined
    assert history.numbers == frozenset({34})


def test_an_id_past_a_line_separator_is_not_read_as_landed_on_the_base() -> None:
    branch = _branch_runner(behind=1, ahead=1)

    def run(args: list[str], root: Path) -> str:
        if _bare(args)[0] == "log" and "--format=%s" in args:
            return "PL-K7QX: quote a pasted title\u2028PL-9Y42 is mentioned, not landed\n"
        return branch(args, root)

    assert branch_state(ROOT, runner=run).landed == ("PL-K7QX",)


def test_a_subject_differing_only_past_a_line_separator_is_not_duplicated_history() -> None:
    """Cut there, two commits share a date and a subject, and this side's own work hides.

    Under-reporting what is held only here is the failure that costs commits.
    """
    divergence = _commits(
        ("<", "aaa1111", "1788256800", "p0", "PL-0001 The first commit"),
        (">", "bbb1111", "1788256800", "p0", "PL-0001 The first commit"),
        ("<", "aaa2222", "1788343200", "aaa1111", "PL-K7QX Record\u2028what the base took"),
        (">", "bbb2222", "1788343200", "bbb1111", "PL-K7QX Record\u2028what only this holds"),
    )
    state = branch_state(ROOT, runner=_branch_runner(behind=2, ahead=2, divergence=divergence))

    assert state.rewrite is not None
    assert state.rewrite.own == (("bbb2222", "PL-K7QX Record\u2028what only this holds"),)


def test_a_filing_subject_holding_a_line_separator_keeps_its_pull_request() -> None:
    subject = "PL-0J9K: file the item\u2028and fix the reader it names (#635)"
    log = f"\x00ff4be610\x01{subject}\n\nA\tdocs/items/PL-0J9K-git-cat-file-batch.md\n"
    changed = {
        "ff4be610": [
            "docs/items/PL-0J9K-git-cat-file-batch.md",
            "subprojects/docket/src/docket/vcs.py",
        ]
    }

    report = filed_with_work(
        frozenset({"PL-0J9K"}),
        ROOT,
        prefix="docs/items",
        runner=_filing_runner("false", log, changed),
    )

    filing = report.filings["PL-0J9K"]
    assert filing.subject == subject
    assert filing.pull_request == 635


def test_a_landing_subject_holding_a_line_separator_names_its_pull_request(tmp_path: Path) -> None:
    repo, port = _ported(tmp_path)
    repo.commit(
        "PL-0002: the same fix\u2028and a pasted note (#934)", f_txt=_edit(_LINES, n10="ten")
    )

    found = change_landed(port, "main", repo.root)

    assert found is not None
    assert found.pull_request == 934
