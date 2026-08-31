"""Tests for deriving in-flight work from branch names.

Git is injected rather than invoked, so these run without a repository and
assert the filtering rather than the plumbing.
"""

from __future__ import annotations

from pathlib import Path

from docket.vcs import (
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


def _runner(refs: list[str], merged: list[str] | None = None):
    def run(args: list[str], root: Path) -> str:
        if any(arg.startswith("--merged=") for arg in args):
            return "\n".join(merged or [])
        return "\n".join(refs)

    return run


def test_a_branch_naming_an_item_is_in_flight() -> None:
    found = branches_in_flight(ROOT, runner=_runner(["claude/pl-k7qx-do-the-thing"]))

    assert [b.item_id for b in found] == ["PL-K7QX"]


def test_historical_numeric_ids_are_recognized() -> None:
    assert in_flight_ids(ROOT, runner=_runner(["claude/pl-013-something"])) == {"PL-013"}


def test_a_branch_naming_nothing_is_ignored() -> None:
    assert branches_in_flight(ROOT, runner=_runner(["main", "claude/some-idea-abcd"])) == []


def test_a_merged_branch_is_not_in_flight() -> None:
    """Deleting a remote branch leaves its tracking ref until someone prunes."""
    refs = ["origin/claude/pl-040-done", "origin/claude/pl-k7qx-live"]
    found = branches_in_flight(ROOT, runner=_runner(refs, merged=["origin/claude/pl-040-done"]))

    assert [b.item_id for b in found] == ["PL-K7QX"]


def test_a_local_branch_and_its_tracking_ref_are_one_piece_of_work() -> None:
    refs = ["claude/pl-k7qx-live", "origin/claude/pl-k7qx-live"]

    assert len(branches_in_flight(ROOT, runner=_runner(refs))) == 1


def test_a_random_suffix_is_not_read_as_an_id() -> None:
    assert branches_in_flight(ROOT, runner=_runner(["claude/queue-redesign-wrqfwj"])) == []


def test_no_git_means_no_claims_about_branches() -> None:
    assert branches_in_flight(ROOT, runner=lambda args, root: "") == []


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
