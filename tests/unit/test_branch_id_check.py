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

The claim clauses (`PL-J9S0`) are the exception, and are tested against real
repositories: what they read is trailers and each commit's own tree, which is
git's reading and `claims.holdings`'s, and a fake would test the fake. The
fake-git tests above them get an empty claim record, so nothing they assert
depends on this checkout's own branches.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import branch_id_check
import pytest
from docket.claims import CUTOVER_MARKER, Holdings
from docket.vcs import answered


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
    monkeypatch.setattr(branch_id_check, "holdings", lambda *_args, **_kwargs: Holdings())
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


def test_a_checkout_with_no_default_branch_says_so_rather_than_passing(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The guard passing every branch in a checkout it could not read (`PL-73P0`).

    `default_base` used to hand back the literal `main` when no candidate
    resolved, and `_git` collapsed a failed walk to the empty string - so
    `git log main..HEAD` against a `main` that is not there yielded no
    subjects, and this printed "nothing ahead of main; no id is owed" and
    exited 0. The unattributed branch in the first test above would have
    passed, on a checkout where nothing was checked at all.
    """
    _install(
        monkeypatch,
        ["Clear the stale origin ref and resolve the docs sweep"],
        base="",  # no candidate resolves
    )

    assert branch_id_check.main() == 0  # advisory, as an unsound walk already is
    out = capsys.readouterr().out
    assert "not checked" in out
    assert "no candidate default branch resolved" in out
    # The claim it must no longer make.
    assert "no id is owed" not in out


def test_a_subject_leading_with_an_id_passes(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _install(monkeypatch, ["Merge origin/main", "PL-CP74: file housekeeping before doing it"])

    assert branch_id_check.main() == 0
    assert "PL-CP74" in capsys.readouterr().out


def test_a_branch_name_carrying_the_id_is_enough(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # `claims.holdings` reads the name as a hold of its own, and needs no
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


@pytest.fixture
def real_git(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """`_git` as written, pointed at an empty repository rather than this checkout."""
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True, capture_output=True)
    monkeypatch.setattr(branch_id_check, "ROOT", tmp_path)


@pytest.mark.usefixtures("real_git")
def test_a_walk_git_did_not_answer_declines_instead_of_owing_nothing(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The route `PL-73P0` closed for a guessed base, reached past a named one.

    `resolved` guards a base `default_base` guessed, and a `--base` given by
    hand is not a guess, so `no-such-ref` went straight to the walk. `git log`
    exited 128, `_git` read that as the empty string, and this printed
    "nothing ahead of no-such-ref; no id is owed" and exited 0 (`PL-1PBV`).
    Real git rather than the fake, because the exit code is the evidence.
    """
    monkeypatch.delenv("GITHUB_HEAD_REF", raising=False)
    monkeypatch.setattr("sys.argv", ["branch_id_check.py", "--base", "no-such-ref"])

    assert branch_id_check.main() == 0
    out = capsys.readouterr().out
    assert "not checked" in out
    assert "no id is owed" not in out


@pytest.mark.usefixtures("real_git")
def test_git_saying_no_is_an_answer_and_git_failing_is_not() -> None:
    # `default_base` reads the first half: `rev-parse --verify` exits 1 for a
    # candidate that is not there, and reading that as a silence would mark
    # every checkout without `origin/main` as guessed and check nothing.
    missing = branch_id_check._git(["rev-parse", "--verify", "--quiet", "no-such-ref"])
    assert missing == ""
    assert answered(missing)
    assert not answered(branch_id_check._git(["log", "--format=%s", "no-such-ref..HEAD", "--"]))


# The claim record (`PL-J9S0`, `PL-MB2W` § "Design round, 2026-09-24").
#
# One instant for every lease, and commit dates a few hours before it, so no
# claim here lapses and nothing depends on the clock the suite runs under.
NOW = "2026-09-24T12:00:00+00:00"
ITEM = "---\nid: PL-K7QX\ntitle: The work\nstatus: ready\n---\n"
WORK = {"src/work.py": "WORK = 1\n"}
MARKER = '"""Writes the claim record."""\n'


def _commit(repo: Path, subject: str, when: str, **kwargs: object) -> None:
    """One commit at `when`: `files` written first, `claim` as its trailer paragraph."""
    files = kwargs.get("files") or {}
    assert isinstance(files, dict)
    for path, text in files.items():
        (repo / path).parent.mkdir(parents=True, exist_ok=True)
        (repo / path).write_text(text, encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True, capture_output=True)
    message = ["-m", subject]
    if kwargs.get("claim"):
        message += ["-m", f"Claim: {kwargs['claim']}"]
    stamp = f"2026-09-24T{when}:00+00:00"
    subprocess.run(
        ["git", "commit", "-q", "--allow-empty", *message],
        cwd=repo,
        check=True,
        capture_output=True,
        env={**os.environ, "GIT_AUTHOR_DATE": stamp, "GIT_COMMITTER_DATE": stamp},
    )


def _branch(repo: Path, name: str, start: str = "main") -> None:
    subprocess.run(["git", "checkout", "-q", "-b", name, start], cwd=repo, check=True)


def _repository(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, *, recorded: bool = True) -> Path:
    """A repository whose `main` holds one item, and the record's marker where `recorded`."""
    repo = tmp_path / "repo"
    subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True, capture_output=True)
    for key, value in (("user.email", "t@example.com"), ("user.name", "T")):
        subprocess.run(["git", "config", key, value], cwd=repo, check=True)
    files = {
        "docs/items/PL-K7QX-the-work.md": ITEM,
        # As this repository's names it: the default is no notes file at all.
        "docket.toml": '[docket]\nnotes_file = "docs/WORKING_NOTES.md"\n',
    }
    if recorded:
        # Not empty: the reader asks `git show` for the marker and reads an
        # empty answer as absent, where the real file is a whole module.
        files[CUTOVER_MARKER] = MARKER
    _commit(repo, "c0", "09:00", files=files)
    monkeypatch.setattr(branch_id_check, "ROOT", repo)
    monkeypatch.delenv("GITHUB_HEAD_REF", raising=False)
    return repo


@pytest.fixture
def record(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    return _repository(tmp_path, monkeypatch)


def _run(monkeypatch: pytest.MonkeyPatch, *argv: str) -> int:
    monkeypatch.setattr("sys.argv", ["branch_id_check.py", "--now", NOW, *argv])
    return branch_id_check.main()


def test_a_work_branch_holding_no_claim_is_refused(
    record: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # The forgetful session: its subject leads with the id, which the id rule
    # reads, and it never ran `bin/docket claim`, which the record needs.
    _branch(record, "claude/some-session-a1b2c3")
    _commit(record, "PL-K7QX: the work", "10:00", files=WORK)

    assert _run(monkeypatch) == 1
    assert branch_id_check.CLAIMS_NOTHING in capsys.readouterr().err


def test_a_claimed_work_branch_passes(
    record: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _branch(record, "claude/some-session-a1b2c3")
    _commit(record, "PL-K7QX: start", "10:00", claim="PL-K7QX claude/some-session-a1b2c3 cse_x")
    _commit(record, "PL-K7QX: the work", "10:30", files=WORK)

    assert _run(monkeypatch) == 0
    assert capsys.readouterr().err == ""


def test_a_claim_its_own_close_released_still_counts(
    record: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The normal finished pull request. Closing the item in the branch's own
    # copy releases the claim, so "no live claim", read as written, refused
    # every one of these; the clause is about a branch that never claimed.
    _branch(record, "claude/some-session-a1b2c3")
    _commit(record, "PL-K7QX: start", "10:00", claim="PL-K7QX claude/some-session-a1b2c3")
    _commit(record, "PL-K7QX: the work", "10:30", files=WORK)
    done = {"docs/items/PL-K7QX-the-work.md": ITEM.replace("status: ready", "status: done")}
    _commit(record, "PL-K7QX: close it out", "11:00", files=done)

    assert _run(monkeypatch) == 0


def test_a_queue_only_branch_owes_no_claim(record: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Per branch, not per id: a capture leads with the id it files and is not
    # working it, so nothing may push that id into a claim (`PL-3CTW`).
    _branch(record, "claude/some-session-a1b2c3")
    _commit(record, "PL-BBBB: capture a finding", "10:00", files={"docs/items/PL-BBBB-x.md": ""})

    assert _run(monkeypatch) == 0


def test_a_triage_pass_writing_the_gate_owes_no_claim(
    record: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Triage puts an item on the debt gate's list in the roadmap, and a design
    # round keeps its thread in the working notes. Neither is work on an item,
    # and read as the items directory alone, the queue refused both.
    _branch(record, "claude/some-session-a1b2c3")
    gate = {
        "docs/items/PL-BBBB-x.md": "",
        "ROADMAP.md": "- PL-BBBB (S) the gate entry\n",
        "docs/WORKING_NOTES.md": "## the thread\n",
    }
    _commit(record, "PL-BBBB: triage onto the gate", "10:00", files=gate)

    assert _run(monkeypatch) == 0


def test_a_body_record_owes_no_claim_and_the_refusal_names_the_records(
    record: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # Every pull request records its body before its merge, since `pr-title`
    # fails without it (`PL-979D`), so a capture's pull request carries one as
    # surely as its item. Read as work, it refused every claimless capture,
    # triage pass and design round once recorded (`PL-F6MM`).
    _branch(record, "claude/some-session-a1b2c3")
    _commit(record, "PL-BBBB: capture a finding", "10:00", files={"docs/items/PL-BBBB-x.md": ""})
    _commit(record, "PL-BBBB: record the body", "10:30", files={"docs/pr-bodies/1066.md": "pr\n"})

    assert _run(monkeypatch) == 0

    _commit(record, "PL-BBBB: the work", "11:00", files=WORK)

    assert _run(monkeypatch) == 1
    assert "docs/pr-bodies/" in capsys.readouterr().err


def test_a_branch_named_for_its_item_owes_no_claim(
    record: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _branch(record, "claude/pl-k7qx-the-work")
    _commit(record, "PL-K7QX: the work", "10:00", files=WORK)

    assert _run(monkeypatch) == 0


def test_a_legacy_commit_owes_no_claim(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Made before a session could write a claim: its tree has no marker, so the
    # clauses skip it and the old rule is all that reads it.
    repo = _repository(tmp_path, monkeypatch, recorded=False)
    _branch(repo, "claude/some-session-a1b2c3")
    _commit(repo, "PL-K7QX: the work", "10:00", files=WORK)

    assert _run(monkeypatch) == 0


def test_a_claim_ordering_behind_another_live_claim_is_refused(
    record: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _branch(record, "claude/first-session-a1b2c3")
    _commit(record, "PL-K7QX: start", "10:00", claim="PL-K7QX claude/first-session-a1b2c3")
    _branch(record, "claude/second-session-d4e5f6")
    _commit(record, "PL-K7QX: start", "10:30", claim="PL-K7QX claude/second-session-d4e5f6")
    _commit(record, "PL-K7QX: the work", "10:45", files=WORK)

    assert _run(monkeypatch) == 1
    err = capsys.readouterr().err
    assert "PL-K7QX is claimed first on claude/first-session-a1b2c3" in err
    assert "bin/docket yield PL-K7QX" in err

    # The holder is told nothing: the order is one answer, read the same way
    # from either branch.
    subprocess.run(["git", "checkout", "-q", "claude/first-session-a1b2c3"], cwd=record, check=True)
    assert _run(monkeypatch) == 0


def test_an_old_rule_hold_ordering_first_does_not_fence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # A subject leading with an id is an old-rule hold - an inference, which
    # is what the record replaces - so it does not refuse a recorded claim.
    repo = _repository(tmp_path, monkeypatch, recorded=False)
    _branch(repo, "claude/old-session-a1b2c3")
    _commit(repo, "PL-K7QX: work under the old rule", "10:00", files=WORK)
    subprocess.run(["git", "checkout", "-q", "main"], cwd=repo, check=True)
    _commit(repo, "c1", "10:15", files={CUTOVER_MARKER: MARKER})
    _branch(repo, "claude/new-session-d4e5f6")
    _commit(repo, "PL-K7QX: start", "10:30", claim="PL-K7QX claude/new-session-d4e5f6")

    assert _run(monkeypatch) == 0


def test_claims_the_reader_declined_are_not_checked_rather_than_passed(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _install(monkeypatch, ["PL-CP74: file housekeeping before doing it"])
    declined = Holdings(declined="git 2.20.1 is older than 2.22")
    monkeypatch.setattr(branch_id_check, "holdings", lambda *_args, **_kwargs: declined)

    assert branch_id_check.main() == 0
    assert "claims not checked - git 2.20.1 is older than 2.22" in capsys.readouterr().out


def test_the_hint_names_the_claim_before_work_outside_the_queue(
    record: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # A fresh session's branch: nothing on it yet, so nothing claims.
    _branch(record, "claude/some-session-a1b2c3")

    assert _run(monkeypatch, "--hint", str(record / "src" / "work.py")) == 0
    assert branch_id_check.CLAIMS_NOTHING in capsys.readouterr().out


def test_the_hint_asks_nothing_of_an_item_file_or_a_file_elsewhere(
    record: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    # Not asked, so the hook keeps its one question for the first edit that is work.
    _branch(record, "claude/some-session-a1b2c3")
    item = record / "docs" / "items" / "PL-K7QX-the-work.md"

    assert _run(monkeypatch, "--hint", str(item)) == branch_id_check.NOT_ASKED
    assert _run(monkeypatch, "--hint", str(tmp_path / "scratch.md")) == branch_id_check.NOT_ASKED
    assert capsys.readouterr().out == ""


def test_the_hint_is_silent_once_the_branch_claims(
    record: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _branch(record, "claude/some-session-a1b2c3")
    _commit(record, "PL-K7QX: start", "10:00", claim="PL-K7QX claude/some-session-a1b2c3")

    assert _run(monkeypatch, "--hint", str(record / "src" / "work.py")) == 0
    assert capsys.readouterr().out == ""
