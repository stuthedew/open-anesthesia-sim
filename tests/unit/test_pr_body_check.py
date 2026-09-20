"""Tests for `tools/pr_body_check.py`, the lost-squash-body guard.

The check exists because this repository's squash commit message *is* the pull
request body (`squash_merge_commit_message: PR_BODY`), and 187 of 683 squash
commits on `main` landed without one - 763,222 characters of design reasoning
that survive only on GitHub (`PL-843V`).

Three failure modes are worth more than the happy path.

A guard that stays quiet on a lost body is the defect itself, so the incident
shape asserts that it fires. A guard that fires on correct work gets worked
around, so the two shapes that legitimately carry no body each assert silence -
and those are the interesting ones, because they are exactly what a crude "does
this commit have a body" check gets wrong: the pre-2026-08-31 `Merge pull
request #101 from ...` merges, which carry the number but not in the trailing
`(#N)` form, and the 2026-08 bootstrap commits, which are nobody's pull
request. Both are real commits on `main` today, so a regression here would fire
on 20 commits that can never be recovered because there is nothing to recover.

The third is that a recovered body has to be recorded *verbatim*. It is a
historical record; a recovery that reflows, strips or re-wraps it produces a
document that reads like the original and is not, which is the failure this
whole item is about arriving a second time by another route.

`_git` and `fetch_body` are substituted rather than a repository built and the
network called, because what is under test is the reading of subjects and
bodies, not git and not GitHub.
"""

from __future__ import annotations

import pr_body_check
import pytest

#: A record as `squash_commits` asks git for it: sha, subject, body.
NUL = "\x00"
RS = "\x01"


def _install(monkeypatch: pytest.MonkeyPatch, records: list[tuple[str, str, str]]) -> None:
    """A `_git` serving one history, and a resolvable default branch."""
    log = RS.join(f"{sha}{NUL}{subject}{NUL}{body}" for sha, subject, body in records) + RS

    def fake(*args: str) -> str:
        if args[0] == "rev-parse":
            return "origin/main\n" if "origin/main" in args else ""
        if args[0] == "log" and "--first-parent" in args:
            return log
        if args[0] == "log":
            return "2026-09-20\n"
        if args[0] == "remote":
            return "https://github.com/stuthedew/open-anesthesia-sim.git\n"
        return ""

    monkeypatch.setattr(pr_body_check, "_git", fake)


def test_fires_on_a_squash_commit_whose_body_is_missing(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    """The incident shape: a `(#N)` subject with nothing under it."""
    monkeypatch.setattr(pr_body_check, "RECOVERY_DIR", tmp_path / "pr-bodies")
    _install(monkeypatch, [("abc1234", "PL-8PS6: give the flow envelope a name (#768)", "")])

    assert pr_body_check.missing("origin/main") == [
        ("abc1234", 768, "PL-8PS6: give the flow envelope a name (#768)")
    ]


def test_silent_on_a_squash_commit_that_kept_its_body(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    """The mechanism works most of the time; firing on those is the way it dies."""
    monkeypatch.setattr(pr_body_check, "RECOVERY_DIR", tmp_path / "pr-bodies")
    _install(monkeypatch, [("abc1234", "PL-8PS6: give the flow envelope a name (#768)", "Why.")])

    assert pr_body_check.missing("origin/main") == []


def test_silent_on_the_old_merge_commit_shape(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    """`Merge pull request #101 from ...` carries a number but never a `(#N)`.

    Seven such commits are on `main` and legitimately carry no body. They are
    what a check keyed on "mentions a pull request number" would wrongly claim.
    """
    monkeypatch.setattr(pr_body_check, "RECOVERY_DIR", tmp_path / "pr-bodies")
    _install(
        monkeypatch,
        [("abc1234", "Merge pull request #101 from stuthedew/claude/roadmap-write", "")],
    )

    assert pr_body_check.missing("origin/main") == []


def test_silent_on_a_direct_commit_that_was_never_a_pull_request(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    """The 2026-08 bootstrap commits owe no body to anyone."""
    monkeypatch.setattr(pr_body_check, "RECOVERY_DIR", tmp_path / "pr-bodies")
    _install(monkeypatch, [("abc1234", "Initial Commit", "")])

    assert pr_body_check.missing("origin/main") == []


def test_a_whitespace_only_body_counts_as_lost(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    """A body of blank lines carries no reasoning, whatever its length."""
    monkeypatch.setattr(pr_body_check, "RECOVERY_DIR", tmp_path / "pr-bodies")
    _install(monkeypatch, [("abc1234", "PL-8PS6: a title (#768)", "  \n\n  \n")])

    assert [pr for _, pr, _ in pr_body_check.missing("origin/main")] == [768]


def test_a_recovered_body_stops_the_advisory(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    """Once the reasoning is in the checkout the check has nothing left to say."""
    recovery = tmp_path / "pr-bodies"
    recovery.mkdir()
    (recovery / "768.md").write_text("recovered", encoding="utf-8")
    monkeypatch.setattr(pr_body_check, "RECOVERY_DIR", recovery)
    _install(monkeypatch, [("abc1234", "PL-8PS6: a title (#768)", "")])

    assert pr_body_check.missing("origin/main") == []


def test_recover_records_the_body_verbatim(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    """The record is historical, so every character of it survives the round trip."""
    recovery = tmp_path / "pr-bodies"
    monkeypatch.setattr(pr_body_check, "RECOVERY_DIR", recovery)
    body = "| Claim | What it says |\n| --- | --- |\n\n*emphasis*, `code`, <angle>.\n"
    _install(monkeypatch, [("abc1234", "PL-8PS6: a title (#768)", "")])
    monkeypatch.setattr(pr_body_check, "fetch_body", lambda slug, pr: body)
    monkeypatch.setattr(pr_body_check, "queue_backlinks", dict)

    assert pr_body_check.recover("origin/main") == 1
    written = (recovery / "768.md").read_text(encoding="utf-8")
    assert written.endswith(body.rstrip() + "\n")
    assert "pr: 768" in written
    assert "commit: abc1234" in written


def test_a_body_unreadable_from_the_api_is_left_for_a_later_run(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    """A rate limit or an outage must not write a file that then silences the check.

    Writing an empty recovery file would satisfy `recovered()` forever, and the
    loss would become permanent at the moment the tool meant to repair it ran.
    """
    recovery = tmp_path / "pr-bodies"
    monkeypatch.setattr(pr_body_check, "RECOVERY_DIR", recovery)
    _install(monkeypatch, [("abc1234", "PL-8PS6: a title (#768)", "")])
    monkeypatch.setattr(pr_body_check, "fetch_body", lambda slug, pr: None)
    monkeypatch.setattr(pr_body_check, "queue_backlinks", dict)

    assert pr_body_check.recover("origin/main") == 0
    assert not (recovery / "768.md").exists()
    assert [pr for _, pr, _ in pr_body_check.missing("origin/main")] == [768]


def test_says_nothing_when_the_default_branch_cannot_be_read(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A bare or shallow checkout has no history to judge, and must not claim one."""
    monkeypatch.setattr(pr_body_check, "_git", lambda *args: "")

    assert pr_body_check.default_branch_ref() is None
    assert pr_body_check.main([]) == 0
