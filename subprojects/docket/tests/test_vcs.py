"""Tests for deriving in-flight work from the branches a checkout holds.

Git is injected rather than invoked, so these run without a repository and
assert the filtering rather than the plumbing. That the commands are spelled
in a way git accepts is proved against a real checkout in `test_cli.py`.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from docket.vcs import (
    Branch,
    StrandedItem,
    StrandedReport,
    behind_remote,
    branches_in_flight,
    default_base,
    in_flight_ids,
    merged_pull_requests,
    stranded,
    tags,
)

ROOT = Path("/nowhere")
BASE = "origin/main"


def _runner(
    refs: list[str],
    merged: list[str] | None = None,
    commits: dict[str, list[tuple[str, str]]] | None = None,
    unrelated: tuple[str, ...] = (),
    adds: dict[str, list[str]] | None = None,
    on_base: set[str] | None = None,
    log: list[list[str]] | None = None,
    ran_out: tuple[str, ...] = (),
):
    """A git that holds `refs`, with `commits` mapping a ref to (day, subject).

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
    it. `log`, when passed, collects every command for a test that asserts
    which question was asked rather than what the answer was.
    """

    def run(args: list[str], root: Path) -> str:
        if log is not None:
            log.append(args)
        if args[0] == "rev-parse":
            return f"{BASE}\n" if args[-1] == BASE else ""
        if args[0] == "for-each-ref":
            if any(arg.startswith("--merged=") for arg in args):
                return "\n".join(merged or [])
            return "\n".join(refs)
        if args[0] == "merge-base":
            return "" if args[-1] in unrelated else "0123456789abcdef\n"
        if args[0] == "diff":
            return "\n".join(
                f":000000 100644 {'0' * 40} {blob} A\tsome/file"
                for blob in (adds or {}).get(args[-2], [])
            )
        if args[0] == "log":
            wanted = [arg for arg in args if arg.startswith("--find-object=")]
            if wanted:
                held = wanted[0].split("=", 1)[1] in (on_base or set())
                return "fedcba9876543210\n" if held else ""
            walked = [arg for arg in args[1:] if not arg.startswith(("-", "^"))]
            lines = []
            for ref in walked:
                entries = (commits or {}).get(ref, [])
                for position, (day, subject) in enumerate(entries):
                    off_the_end = ref in ran_out and position == len(entries) - 1
                    parent = "" if off_the_end else "0f1e2d3"
                    lines.append(f"{ref}\x1f{day}\x1f{parent}\x1f{subject}")
            return "\n".join(lines)
        return ""

    return run


def _in_flight(
    refs: list[str],
    merged: list[str] | None = None,
    commits: dict[str, list[tuple[str, str]]] | None = None,
    unrelated: tuple[str, ...] = (),
    adds: dict[str, list[str]] | None = None,
    on_base: set[str] | None = None,
    ran_out: tuple[str, ...] = (),
) -> tuple[Branch, ...]:
    runner = _runner(refs, merged, commits, unrelated, adds, on_base, ran_out=ran_out)
    return branches_in_flight(ROOT, runner=runner).branches


def test_a_branch_naming_an_item_is_in_flight() -> None:
    assert [b.item_id for b in _in_flight(["claude/pl-k7qx-do-the-thing"])] == ["PL-K7QX"]


def test_historical_numeric_ids_are_recognized() -> None:
    assert in_flight_ids(ROOT, runner=_runner(["claude/pl-013-something"])) == {"PL-013"}


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

    assert ["log", "-1", "--format=%H", "--find-object=a1", BASE] in calls
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


def _digest(report: StrandedReport) -> str:
    from docket.checks import Report
    from docket.model import parse_item
    from docket.render import format_digest

    return format_digest(Report(items=[parse_item(DIGEST_ITEM)]), set(), None, None, report)


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
