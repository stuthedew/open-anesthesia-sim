"""Tests for deriving in-flight work from branch names.

Git is injected rather than invoked, so these run without a repository and
assert the filtering rather than the plumbing.
"""

from __future__ import annotations

from pathlib import Path

from docket.vcs import behind_remote, branches_in_flight, default_base, in_flight_ids, tags

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
