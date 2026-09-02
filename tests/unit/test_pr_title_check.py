"""Tests for `tools/pr_title_check.py`, the pull-request title guard.

The check exists because of one incident, so the suite is built around it.
`#220` was created from the Claude Code UI with a generated title naming none
of the three items it closed; the squash landed that title as the subject on
`main`, `docket check` had nothing to recover the number from, and the release
was blocked until the number was read off GitHub by hand (`PL-2XTF`).

Two failure modes are worth more than the happy path here. A guard that stays
quiet when the title is wrong is the defect itself, so every rule has a test
that breaks the title and asserts it fires. A guard that fires on correct work
gets disabled, so each of those has a matching test asserting silence - and the
cases that must stay silent are the interesting ones, because they are what a
crude "does the title contain an id" check would get wrong: a branch that
closes nothing, and a base that already carried the closure.

`_git` is substituted rather than a repository built, because what is under
test is the comparison of two trees and the reading of a title, not git.
"""

from __future__ import annotations

import pr_title_check
import pytest

CLOSED = "---\nid: {id}\ntitle: T\nstatus: {status}\n---\n"


def _tree(**refs: dict[str, str]):
    """A `_git` serving each ref a mapping of item file name to its text."""

    def fake(args: list[str]) -> str:
        if args[0] == "ls-tree":
            # ["ls-tree", "-r", "--name-only", <ref>, "--", <dir>]
            ref = args[3]
            return "\n".join(f"docs/items/{name}" for name in refs.get(ref, {}))
        if args[0] == "show":
            ref, _, path = args[1].partition(":")
            return refs.get(ref, {}).get(path.split("/")[-1], "")
        return ""

    return fake


def _install(monkeypatch: pytest.MonkeyPatch, **refs: dict[str, str]) -> None:
    monkeypatch.setattr(pr_title_check, "_git", _tree(**refs))


def test_a_branch_that_closes_an_item_needs_its_id(monkeypatch: pytest.MonkeyPatch) -> None:
    _install(
        monkeypatch,
        base={"PL-K7QX-a.md": CLOSED.format(id="PL-K7QX", status="ready")},
        head={"PL-K7QX-a.md": CLOSED.format(id="PL-K7QX", status="done")},
    )

    assert pr_title_check.closes("base", "head") == ["PL-K7QX"]


def test_the_incident_this_exists_for_is_refused(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # #220's shape: three items closed, a generated title naming none of them.
    _install(
        monkeypatch,
        base={f"{i}-a.md": CLOSED.format(id=i, status="ready") for i in ("PL-YHF1", "PL-P909")},
        head={f"{i}-a.md": CLOSED.format(id=i, status="done") for i in ("PL-YHF1", "PL-P909")},
    )
    monkeypatch.setenv("PR_TITLE", "Design the abstraction and add safety checks")
    monkeypatch.setattr("sys.argv", ["pr_title_check.py", "--base", "base", "--head", "head"])

    assert pr_title_check.main() == 1
    assert "PL-P909, PL-YHF1" in capsys.readouterr().err


def test_a_title_leading_with_every_id_passes(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _install(
        monkeypatch,
        base={f"{i}-a.md": CLOSED.format(id=i, status="ready") for i in ("PL-YHF1", "PL-P909")},
        head={f"{i}-a.md": CLOSED.format(id=i, status="done") for i in ("PL-YHF1", "PL-P909")},
    )
    monkeypatch.setenv("PR_TITLE", "PL-P909, PL-YHF1: close them both")
    monkeypatch.setattr("sys.argv", ["pr_title_check.py", "--base", "base", "--head", "head"])

    assert pr_title_check.main() == 0
    assert "leads with PL-P909, PL-YHF1" in capsys.readouterr().out


def test_an_id_mentioned_but_not_leading_does_not_count(monkeypatch: pytest.MonkeyPatch) -> None:
    # `docket` reads the *leading* run of ids and nothing else, because an id
    # further in is usually somebody else's work being referred to. A title
    # that buries its own id is as unrecoverable as one that omits it.
    _install(
        monkeypatch,
        base={"PL-K7QX-a.md": CLOSED.format(id="PL-K7QX", status="ready")},
        head={"PL-K7QX-a.md": CLOSED.format(id="PL-K7QX", status="done")},
    )
    monkeypatch.setenv("PR_TITLE", "Fix the thing that PL-K7QX described")
    monkeypatch.setattr("sys.argv", ["pr_title_check.py", "--base", "base", "--head", "head"])

    assert pr_title_check.main() == 1


def test_a_branch_that_closes_nothing_owes_no_id(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # Most pull requests here close nothing - a capture, a doc fix, a release.
    # Demanding an id from those is how a guard gets switched off.
    _install(
        monkeypatch,
        base={"PL-K7QX-a.md": CLOSED.format(id="PL-K7QX", status="ready")},
        head={"PL-K7QX-a.md": CLOSED.format(id="PL-K7QX", status="ready")},
    )
    monkeypatch.setenv("PR_TITLE", "Tidy the README")
    monkeypatch.setattr("sys.argv", ["pr_title_check.py", "--base", "base", "--head", "head"])

    assert pr_title_check.main() == 0
    assert "closes no item" in capsys.readouterr().out


def test_a_closure_already_on_the_base_is_not_this_branch_s(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # It arrived through a merge of the base. Reading the diff rather than
    # comparing both ends would blame this branch for somebody else's closure.
    _install(
        monkeypatch,
        base={"PL-K7QX-a.md": CLOSED.format(id="PL-K7QX", status="done")},
        head={"PL-K7QX-a.md": CLOSED.format(id="PL-K7QX", status="done")},
    )

    assert pr_title_check.closes("base", "head") == []


def test_a_dropped_item_is_a_closure_too(monkeypatch: pytest.MonkeyPatch) -> None:
    _install(
        monkeypatch,
        base={"PL-K7QX-a.md": CLOSED.format(id="PL-K7QX", status="untriaged")},
        head={"PL-K7QX-a.md": CLOSED.format(id="PL-K7QX", status="dropped")},
    )

    assert pr_title_check.closes("base", "head") == ["PL-K7QX"]


def test_an_unset_title_is_not_a_failure(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # The workflow runs this only on pull requests, but a hand-run outside one
    # should say so rather than fail a checkout that has done nothing wrong.
    monkeypatch.delenv("PR_TITLE", raising=False)
    monkeypatch.setattr("sys.argv", ["pr_title_check.py"])

    assert pr_title_check.main() == 0
    assert "PR_TITLE is not set" in capsys.readouterr().err
