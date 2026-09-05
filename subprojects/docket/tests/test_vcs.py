"""Tests for deriving in-flight work from the branches a checkout holds.

Git is injected rather than invoked, so these run without a repository and
assert the filtering rather than the plumbing. That the commands are spelled
in a way git accepts is proved against a real checkout in `test_cli.py`.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from docket.checks import Report
from docket.vcs import (
    Branch,
    BranchState,
    FlightFiles,
    FlightReport,
    OrphanedBranch,
    OrphanedReport,
    StrandedItem,
    StrandedReport,
    behind_remote,
    branch_state,
    branches_in_flight,
    closed_by,
    closures_on_base,
    default_base,
    files_in_flight,
    lost,
    merged_pull_requests,
    orphaned,
    precedence,
    stranded,
    tags,
)

ROOT = Path("/nowhere")
BASE = "origin/main"


def _when(day: str) -> str:
    """A commit date in the shape `%cI` writes, from the day a test names.

    Tests that only care which day a branch last moved on say `2026-08-20`;
    tests that care which of two branches moved *first* say the whole
    timestamp. Both reach git's format from here, so neither has to spell it.
    """
    return day if "T" in day else f"{day}T00:00:00+00:00"


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

    `adds` maps a ref to the blobs it introduces since its fork point and
    `on_base` names the blobs the default branch has held at some point, which
    is what separates a branch whose work has landed from one still carrying
    it. `touched` maps a ref to its commits as (subject, paths), newest first,
    which is what `orphaned` reads to tell a commit the merge took from one
    nothing took. `log`, when passed, collects every command for a test that asserts
    which question was asked rather than what the answer was.
    """

    def run(args: list[str], root: Path) -> str:
        if log is not None:
            log.append(args)
        if args[0] == "rev-parse":
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
        if args[0] == "diff":
            return "\n".join(
                f":000000 100644 {'0' * 40} {_blob(entry)} A\t{_path(entry)}"
                for entry in (adds or {}).get(args[-2], [])
            )
        if args[0] == "log":
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
    runner = _runner(refs, merged, commits, unrelated, adds, on_base, ran_out=ran_out)
    return branches_in_flight(ROOT, runner=runner).branches


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


def test_no_git_means_no_claims_about_branches() -> None:
    assert branches_in_flight(ROOT, runner=lambda args, root: "").branches == ()


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

    assert [b.last_commit for b in found] == [date(2026, 8, 30)]


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
    assert tags(ROOT, runner=lambda args, root: "v0.1.0\nv0.2.0\n") == frozenset(
        {"v0.1.0", "v0.2.0"}
    )


def test_no_git_means_no_tags_rather_than_an_error() -> None:
    assert tags(ROOT, runner=lambda args, root: "") == frozenset()


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
    assert default_base(ROOT, runner=_refs({"main": "def456"})) == "main"


def test_a_repository_resolving_no_default_branch_still_answers() -> None:
    """Nothing to compare against is reported by verify as no change, not as clean."""
    assert default_base(ROOT, runner=_refs({})) == "main"


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


def _tree_runner(trees: dict[str, dict[str, str]], titles: dict[str, str] | None = None):
    """A git that holds the given trees, as `ref -> {item file: contents}`.

    Deliberately no commit graph at all: no `--merged`, no `rev-list`, nothing
    a shallow clone would answer wrongly. If these tests pass with a runner
    that cannot answer a containment question, the implementation is not
    asking one.
    """

    def run(args: list[str], root: Path) -> str:
        if args[0] == "for-each-ref":
            return "\n".join(trees)
        if args[:2] == ["rev-parse", "--verify"]:
            return "abc123\n" if args[-1] in trees else ""
        if args[0] == "ls-tree":
            return "\n".join(f"docs/items/{name}" for name in trees.get(args[3], {}))
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

    assert "1 ref could not be compared" in format_delegable(_store(), UNREAD, ())
    assert "1 ref could not be compared" in format_delegable(Report(items=[]), UNREAD, ())
    assert "could not be compared" not in format_delegable(_store(), READ, ())


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
    printed = format_flight(report, date(2026, 8, 31))

    assert f"PL-K7QX  {NAMED_UNREADABLE}" in printed
    assert "no commit of its own this checkout can read" in printed
    assert "so what its commits carry is unknown" in printed
    assert printed.count(NAMED_UNREADABLE) == 2


def _branch_runner(
    branch: str = "claude/pl-k7qx-live",
    behind: int = 0,
    ahead: int = 0,
    landed: tuple[str, ...] = (),
    unrelated: bool = False,
    base_exists: bool = True,
):
    """A git holding one checked-out branch at a known position against the base.

    `unrelated` is the case the guard exists for: `merge-base` finds nothing,
    and `rev-list --left-right --count` would still answer - with the length of
    each side of two unrelated histories, which reads exactly like a position.
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


def _closure_runner(
    on_base: dict[str, str],
    subjects: tuple[str, ...] = (),
    log: list[list[str]] | None = None,
    shallow: str = "",
    closed_from: int = 0,
    file_history: tuple[str, ...] = (),
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
            return f"{BASE}\n" if args[-1] == BASE else ""
        if args[0] == "for-each-ref":
            return f"{BASE}\n"
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
            history = file_history if "--" in args else subjects
            return "\n".join(f"c{index}\x1f{subject}" for index, subject in enumerate(history))
        return ""

    return run


def _recovery_runner(history: tuple[tuple[str, str], ...], done_at: set[str], name: str):
    """A git whose base subjects name no id, so only the file's history answers.

    `history` is the file's own log, newest first, as (revision, subject).
    `done_at` names the revisions whose tree has the item closed - written as
    revisions rather than derived, so a test can say exactly where the status
    flipped, including at a parent the walk has to look at.
    """

    def run(args: list[str], root: Path) -> str:
        if args[0] == "rev-parse":
            return "" if args[-1] == "--is-shallow-repository" else f"{BASE}\n"
        if args[0] == "for-each-ref":
            return f"{BASE}\n"
        if args[0] == "show":
            revision, _, _path = args[-1].partition(":")
            if revision == BASE:
                return CLOSED.format(id="PL-K7QX")
            return (
                CLOSED.format(id="PL-K7QX")
                if revision in done_at
                else OPEN_ITEM.format(id="PL-K7QX")
            )
        if args[0] == "log":
            if "--" in args:
                return "\n".join(f"{revision}\x1f{subject}" for revision, subject in history)
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
            "PL-K7QX, PL-A1B2: triage the two captures (#159)",
        ),
        file_history=(
            "PL-B1C2 Make the simulation step transactional (#204)",
            "PL-K7QX, PL-A1B2: triage the two captures (#159)",
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
        # Depth qualifies an absence, never a hit: the number is still derived.
        assert report.numbers == {"PL-K7QX": 148}


def _lost_runner(tree: list[str], history: list[str], *, shallow: str = "false"):
    """A git whose `ref` tree holds `tree` and whose history holds `history`.

    `history` is spelled the way `rev-list --objects` prints it - `<sha> SP
    <path>`, newest commit first - because the ordering is load-bearing: the
    first blob seen for an id is the last content it had, and that is what the
    report hands back for recovery.
    """

    def run(args: list[str], root: Path) -> str:
        if args[0] == "ls-tree":
            return "\n".join(tree)
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
            prefix = f"{args[3]}:"
            return "\n".join(sorted(k[len(prefix) :] for k in trees if k.startswith(prefix)))
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
        ROOT, _flight(("origin/feature", "PL-K7QX"), ("origin/feature", "PL-A1B2")), runner=run
    )

    assert len(files.branches) == 1
    assert files.branches[0].item_ids == ("PL-A1B2", "PL-K7QX")


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


# --- precedence: which of two branches carrying one item continues -----------

FIRST = "origin/claude/pl-k7qx-first"
SECOND = "origin/claude/pl-k7qx-second"
EARLY = ("2026-09-04T10:00:00+00:00", "PL-K7QX Start the thing", "aaaa111")
LATE = ("2026-09-04T10:40:00+00:00", "PL-K7QX Start the thing too", "bbbb222")


def _precedence(
    refs: list[str],
    commits: dict[str, list[tuple[str, ...]]] | None = None,
    head: str = "",
    item: str = "PL-K7QX",
    ran_out: tuple[str, ...] = (),
):
    return precedence(ROOT, item, runner=_runner(refs, commits=commits, head=head, ran_out=ran_out))


def test_precedence_gives_the_item_to_the_branch_that_named_it_first() -> None:
    order = _precedence([FIRST, SECOND], {FIRST: [EARLY], SECOND: [LATE]})

    assert [carrier.ref for carrier in order.carriers] == [FIRST, SECOND]
    assert order.holder is not None
    assert order.holder.ref == FIRST


def test_precedence_orders_by_the_earliest_commit_not_the_newest() -> None:
    """A branch that pushes again does not overtake one that started before it.

    The whole point of dating a claim from its first commit: otherwise the
    session that has been at it longest loses the item every time the other
    one saves its work.
    """
    order = _precedence(
        [FIRST, SECOND],
        {FIRST: [("2026-09-04T10:05:00+00:00", "PL-K7QX More", "aaaa999"), EARLY], SECOND: [LATE]},
    )

    assert order.holder is not None
    assert order.holder.ref == FIRST


def test_precedence_does_not_make_a_carrier_of_a_branch_that_only_annotated() -> None:
    """The two reads answer the same question and must not disagree about it.

    `branches_in_flight` asks whether an item is startable and `precedence`
    asks which of two sessions yields; a branch that merely recorded a note
    is carrying nothing, so it is a rival in neither. Left in here it would
    order a real session behind a commit nobody is working from.
    """
    annotating = "origin/claude/some-triage-pass-abcdef"
    order = _precedence(
        [annotating, FIRST],
        {
            annotating: [("2026-09-04T09:00:00+00:00", "PL-K7QX: triage", "cccc333", QUEUE_ONLY)],
            FIRST: [EARLY],
        },
    )

    assert [carrier.ref for carrier in order.carriers] == [FIRST]


def test_precedence_breaks_a_tie_on_the_commit_hash() -> None:
    """Two commits can share a second, and a tie both sessions cannot break is the defect."""
    same = "2026-09-04T10:00:00+00:00"
    order = _precedence(
        [SECOND, FIRST],
        {FIRST: [(same, "PL-K7QX One", "bbbb222")], SECOND: [(same, "PL-K7QX Two", "aaaa111")]},
    )

    assert order.holder is not None
    assert order.holder.ref == SECOND


def test_precedence_reads_a_branch_and_its_tracking_ref_as_one_carrier() -> None:
    """Telling a session to yield to itself is the one answer this must never give."""
    local = "claude/pl-k7qx-first"
    order = _precedence([local, FIRST], {local: [EARLY], FIRST: [EARLY]}, head=local)

    assert len(order.carriers) == 1
    assert order.carriers[0].mine
    assert not order.yields


def test_precedence_says_this_branch_yields_to_the_earlier_claim() -> None:
    local = "claude/pl-k7qx-second"
    order = _precedence([local, FIRST], {local: [LATE], FIRST: [EARLY]}, head=local)

    assert order.yields
    assert order.mine is not None
    assert order.mine.ref == local
    assert order.holder is not None
    assert order.holder.ref == FIRST


def test_precedence_does_not_call_it_a_yield_when_this_branch_carries_nothing() -> None:
    """A session that has not started has nothing to hand over and nothing to stop."""
    order = _precedence(
        ["claude/some-other-work-abcdef", FIRST],
        {FIRST: [EARLY]},
        head="claude/some-other-work-abcdef",
    )

    assert not order.yields
    assert order.mine is None
    assert order.holder is not None
    assert order.holder.ref == FIRST


def test_precedence_never_makes_both_sessions_yield() -> None:
    """The failure worth more than the one it replaces: work nobody is doing.

    Both checkouts see the same two pushed branches and differ only in which
    one they have checked out, which is the position the two sessions are
    actually in.
    """
    refs = ["claude/pl-k7qx-first", "claude/pl-k7qx-second", FIRST, SECOND]
    commits = {
        "claude/pl-k7qx-first": [EARLY],
        FIRST: [EARLY],
        "claude/pl-k7qx-second": [LATE],
        SECOND: [LATE],
    }

    stood_down = [
        _precedence(refs, commits, head=branch).yields
        for branch in ("claude/pl-k7qx-first", "claude/pl-k7qx-second")
    ]

    assert stood_down == [False, True]


def test_precedence_dates_a_branch_named_for_the_item_from_its_first_commit() -> None:
    """A branch name claims the item from the moment there is anything on it."""
    order = _precedence(
        [FIRST], {FIRST: [("2026-09-04T09:00:00+00:00", "Fix the thing", "cccc333")]}
    )

    assert order.holder is not None
    assert order.holder.staked is not None
    assert order.holder.staked.commit == "cccc333"


def test_precedence_dates_a_rider_from_the_commit_that_named_it() -> None:
    """A branch carrying somebody else's item did not claim it before it said so."""
    rider = "origin/claude/pl-j295-other"
    order = _precedence(
        [rider],
        {
            rider: [
                ("2026-09-04T11:00:00+00:00", "PL-K7QX Pick this up too", "dddd444"),
                ("2026-09-04T08:00:00+00:00", "PL-J295 The branch's own work", "eeee555"),
            ]
        },
    )

    assert order.holder is not None
    assert order.holder.staked is not None
    assert order.holder.staked.commit == "dddd444"


def test_precedence_sorts_an_unreadable_claim_behind_every_dated_one() -> None:
    """An unread ref put first would make every session in a truncated clone yield."""
    truncated = "origin/claude/pl-k7qx-truncated"
    order = _precedence(
        [truncated, FIRST],
        {truncated: [("2026-09-04T08:00:00+00:00", "PL-K7QX Older", "ffff666")], FIRST: [EARLY]},
        ran_out=(truncated,),
    )

    assert [carrier.ref for carrier in order.carriers] == [FIRST, truncated]
    assert order.carriers[1].staked is None
    assert truncated in order.unreadable


def test_precedence_ignores_a_branch_carrying_another_item() -> None:
    order = _precedence(
        [FIRST, "origin/claude/pl-j295-elsewhere"],
        {FIRST: [EARLY], "origin/claude/pl-j295-elsewhere": [("2026-09-01", "PL-J295 Other")]},
    )

    assert [carrier.ref for carrier in order.carriers] == [FIRST]


def test_precedence_finds_nothing_where_no_branch_carries_the_item() -> None:
    order = _precedence(["main", "origin/claude/unrelated-abcdef"])

    assert order.carriers == ()
    assert order.holder is None
    assert not order.yields


# A branch whose pull request merged and which was then pushed to again: the
# base holds `landed.txt` and has never held `pushed-after.md`.
PARTLY = "claude/pl-k7qx-partly-landed"


def _orphaned(
    adds: dict[str, list[tuple[str, str]]],
    on_base: set[str],
    refs: list[str] | None = None,
    merged: list[str] | None = None,
    touched: dict[str, list[tuple[str, tuple[str, ...]]]] | None = None,
) -> OrphanedReport:
    return orphaned(
        ROOT, runner=_runner(refs or [PARTLY], merged, adds=adds, on_base=on_base, touched=touched)
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


def test_a_branch_whose_commits_cannot_be_walked_is_not_reported() -> None:
    """No commit to name is no finding to hand a reader, and it says so by silence."""
    assert (
        _orphaned(
            adds={PARTLY: [("a1", "landed.txt"), ("a2", "pushed-after.md")]}, on_base={"a1"}
        ).branches
        == ()
    )
