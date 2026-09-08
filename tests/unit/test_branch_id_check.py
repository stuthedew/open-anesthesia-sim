"""Tests for `tools/branch_id_check.py`, the branch-attribution guard.

The check exists because unfiled work is structurally invisible: every
in-flight guard this project has answers by matching a `PL-` id, so a branch
carrying none returns a clean answer for itself in `docket flight`, `show`,
`next`, `concurrent` and the session-start digest alike (`PL-CP74`).

Two failure modes are worth more than the happy path. A guard that stays quiet
on an unattributed branch is the defect itself, so the incident shape has a
test that asserts it fires. A guard that fires on correct work gets disabled or
worked around, so each form of attribution the real guards read has a matching
test asserting silence - and those are the interesting ones, because they are
what a crude "does a subject contain an id" check would get wrong in both
directions: an id mentioned mid-subject, which `docket flight` does not read
and this must not credit, and a branch *name* carrying the id, which it does
read and this must credit even when no subject does.

A third mode joined them with `PL-8P6D`: firing on somebody the rule was never
written for. The guarantee is about agent sessions, and the check refused the
project owner's own web-UI edit and would have refused the first contributor's
pull request, so the branch name now decides scope as well as attribution -
which means the exemption needs its own tests in both directions, one for a
branch outside `claude/` passing and one for the ambiguous name that must not.

`_git` is substituted rather than a repository built, because what is under
test is the reading of subjects and a branch name, not git.
"""

from __future__ import annotations

import branch_id_check
import pytest


def _install(
    monkeypatch: pytest.MonkeyPatch,
    subjects: list[str],
    *,
    branch: str = "claude/some-generated-name-a36q1s",
    parents: str = "abc1234",
    base: str = "origin/main",
) -> None:
    """A `_git` serving one branch: its name, and what it adds to the base."""
    log = "\n".join(f"{parents}\x1f{subject}" for subject in subjects)

    def fake(args: list[str]) -> str:
        if args[0] == "rev-parse" and "--abbrev-ref" in args:
            return branch + "\n"
        if args[0] == "rev-parse":
            # `default_base` probing its candidates in order.
            return args[-1] + "\n" if args[-1] == base else ""
        if args[0] == "log":
            return log
        return ""

    monkeypatch.delenv("GITHUB_HEAD_REF", raising=False)
    monkeypatch.setattr(branch_id_check, "_git", fake)
    monkeypatch.setattr("sys.argv", ["branch_id_check.py"])


def test_the_case_this_exists_for_is_refused(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # Repository housekeeping, done well, filed nowhere: the shape PL-CP74
    # measured. No id in the branch name, none leading a subject.
    _install(
        monkeypatch,
        ["Clear the stale origin ref and resolve the docs sweep", "Fix a lint failure on main"],
    )

    assert branch_id_check.main() == 1
    err = capsys.readouterr().err
    assert "2 commit(s) ahead of origin/main" in err
    assert "bin/docket new" in err


def test_a_subject_leading_with_an_id_passes(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _install(monkeypatch, ["Merge origin/main", "PL-CP74: file housekeeping before doing it"])

    assert branch_id_check.main() == 0
    assert "PL-CP74" in capsys.readouterr().out


def test_a_branch_name_carrying_the_id_is_enough(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # `branches_in_flight` reads the name as well as the subjects, and needs no
    # history to do it. Failing here would fire on work the guards can see.
    _install(monkeypatch, ["Resolve the merge"], branch="claude/pl-cp74-unfiled-housekeeping")

    assert branch_id_check.main() == 0
    assert "PL-CP74" in capsys.readouterr().out


def test_an_id_mentioned_mid_subject_does_not_count(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # `LEADING_IDS_RE` reads the front of a subject and only there, so crediting
    # a mention would certify a branch as visible that `docket flight` cannot
    # see - the one failure mode worse than having no check.
    _install(monkeypatch, ["Clear the stale ref PL-1Q3S diagnosed"])

    assert branch_id_check.main() == 1
    assert "no item id names any of them" in capsys.readouterr().err


def test_a_release_commit_owes_no_id(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _install(monkeypatch, ["Release v0.3.7: the queue's own housekeeping"])

    assert branch_id_check.main() == 0
    assert "release commit" in capsys.readouterr().out


def test_a_subject_merely_mentioning_a_release_is_not_one(monkeypatch: pytest.MonkeyPatch) -> None:
    _install(monkeypatch, ["Back out the Release v0.3.6 version bump"])

    assert branch_id_check.main() == 1


def test_nothing_ahead_of_the_base_owes_nothing(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # `main` itself, and CI's push job, take this path every run.
    _install(monkeypatch, [])

    assert branch_id_check.main() == 0
    assert "no id is owed" in capsys.readouterr().out


def test_a_walk_that_ran_off_the_end_declines_instead_of_passing(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # A truncated clone cannot exclude the base's own commits, so the ids it
    # reports belong to other people's merged items. Answering from them would
    # keep the gate green while the guarantee it stands for was void.
    _install(monkeypatch, ["PL-0D4X: name the lane of the answer"], parents="")

    assert branch_id_check.main() == 0
    out = capsys.readouterr().out
    assert "not checked" in out
    assert "PL-0D4X" not in out


def test_a_branch_outside_the_agent_namespace_owes_no_id(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # `#394`'s shape, which is what `PL-8P6D` is: the project owner's own
    # README edit from the GitHub web UI, on the branch that dialog names, with
    # no id anywhere. Identical to the refusal above in every respect the old
    # rule could read, and the whole point is that it now passes.
    _install(
        monkeypatch,
        ["Add pre-release warning to README", "Update README.md"],
        branch="stuthedew-patch-1",
    )

    assert branch_id_check.main() == 0
    assert "stuthedew-patch-1 is outside `claude/`" in capsys.readouterr().out


def test_a_contributor_pull_request_passes_on_its_head_ref(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # The drive-by case, as CI sees it: a detached merge commit, the head
    # branch's real name only in the environment. A contributor has no queue
    # and no `bin/docket`, so the remedy this used to print named a tool they
    # cannot run.
    _install(monkeypatch, ["Fix a typo in docs/MODEL.md"], branch="HEAD")
    monkeypatch.setenv("GITHUB_HEAD_REF", "fix-model-typo")

    assert branch_id_check.main() == 0
    assert "no id is owed" in capsys.readouterr().out


def test_a_name_that_cannot_be_read_stays_in_scope(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # The exemption is a widening, so its failure mode is a branch escaping
    # that should not. An unreadable name resolves the ambiguity the way that
    # keeps the old verdict; CI never reaches it, because `GITHUB_HEAD_REF` is
    # set on every `pull_request` event.
    _install(monkeypatch, ["Resolve the merge"], branch="HEAD")

    assert branch_id_check.main() == 1
    assert "no item id names any of them" in capsys.readouterr().err


def test_the_namespace_is_matched_case_insensitively(monkeypatch: pytest.MonkeyPatch) -> None:
    # Branch names are case-sensitive to git, so `Claude/x` is a name no
    # harness produces and no contributor would choose. Folding the comparison
    # can only widen what the rule binds, which is the safe direction for it.
    _install(monkeypatch, ["Resolve the merge"], branch="Claude/some-generated-name-a36q1s")

    assert branch_id_check.main() == 1


def test_the_pull_request_head_ref_is_preferred_to_a_detached_head(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # On a `pull_request` event the checkout is a detached merge commit, so
    # `rev-parse` answers `HEAD`. Without the environment read, CI would refuse
    # a branch that `make check` passed on the same commits.
    _install(monkeypatch, ["Resolve the merge"], branch="HEAD")
    monkeypatch.setenv("GITHUB_HEAD_REF", "claude/pl-cp74-unfiled-housekeeping")

    assert branch_id_check.main() == 0
    assert "PL-CP74" in capsys.readouterr().out
