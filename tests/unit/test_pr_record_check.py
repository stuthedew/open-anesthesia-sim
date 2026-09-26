"""Tests for `tools/pr_record_check.py`, the guard that a closure records its pull request.

The check is the guarantee behind `bin/docket record N` (`PL-HMZZ`): the number
is written on the closing branch before the merge, and nothing infers it from
history afterwards, so a closure that reaches `main` without it has lost the
way back to its work for good. Two failure modes are worth more than the happy
path. A guard that stays quiet when the number is missing or wrong is the
defect itself, so both shapes assert that it fires. A guard that fires on
correct work gets switched off, so the shapes that legitimately owe nothing
each assert silence - a branch closing nothing, a closure that arrived through
a merge of the base, and a drop, which records no `pr` by the store's own
convention.

`pr_title_check._git` is substituted rather than a repository built, because
the tree reads are that module's and what is under test here is the rule
applied to what they return.
"""

from __future__ import annotations

import subprocess

import pr_record_check
import pr_title_check
import pytest

ITEM = "---\nid: {id}\ntitle: T\nstatus: {status}\n{extra}---\n"


def _tree(**refs: dict[str, str]):
    """A `_git` serving each ref a mapping of item file name to its text."""

    def fake(args: list[str]) -> str:
        if args[0] == "ls-tree":
            ref = args[3]
            return "\n".join(f"docs/items/{name}" for name in refs.get(ref, {}))
        if args[0] == "show":
            ref, _, path = args[1].partition(":")
            return refs.get(ref, {}).get(path.split("/")[-1], "")
        return ""

    return fake


def _install(monkeypatch: pytest.MonkeyPatch, **refs: dict[str, str]) -> None:
    monkeypatch.setattr(pr_title_check, "_git", _tree(**refs))


def _run(monkeypatch: pytest.MonkeyPatch, number: str | None, *flags: str) -> int:
    if number is None:
        monkeypatch.delenv("PR_NUMBER", raising=False)
    else:
        monkeypatch.setenv("PR_NUMBER", number)
    monkeypatch.setattr(
        "sys.argv", ["pr_record_check.py", "--base", "base", "--head", "head", *flags]
    )
    return pr_record_check.main()


def test_a_closure_recording_the_number_passes(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _install(
        monkeypatch,
        base={"PL-K7QX-a.md": ITEM.format(id="PL-K7QX", status="ready", extra="")},
        head={"PL-K7QX-a.md": ITEM.format(id="PL-K7QX", status="done", extra="pr: 1050\n")},
    )

    assert _run(monkeypatch, "1050") == 0
    assert "PL-K7QX records #1050" in capsys.readouterr().out


def test_a_closure_recording_no_number_is_refused(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The incident shape this exists for: the closure would merge and the number would be lost."""
    _install(
        monkeypatch,
        base={"PL-K7QX-a.md": ITEM.format(id="PL-K7QX", status="ready", extra="")},
        head={"PL-K7QX-a.md": ITEM.format(id="PL-K7QX", status="done", extra="")},
    )

    assert _run(monkeypatch, "1050") == 1
    err = capsys.readouterr().err
    assert "PL-K7QX" in err
    assert "bin/docket record 1050" in err


def test_a_closure_recording_another_number_is_refused(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # A pull request closed unmerged and reopened under a new number: the old
    # one is a confident wrong provenance, which is worse than none.
    _install(
        monkeypatch,
        base={"PL-K7QX-a.md": ITEM.format(id="PL-K7QX", status="ready", extra="")},
        head={"PL-K7QX-a.md": ITEM.format(id="PL-K7QX", status="done", extra="pr: 1049\n")},
    )

    assert _run(monkeypatch, "1050") == 1
    assert "records `pr: 1049`" in capsys.readouterr().err


def test_every_closure_is_held_to_it_and_the_refusal_names_each(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _install(
        monkeypatch,
        base={
            f"{i}-a.md": ITEM.format(id=i, status="ready", extra="") for i in ("PL-YHF1", "PL-P909")
        },
        head={
            "PL-YHF1-a.md": ITEM.format(id="PL-YHF1", status="done", extra="pr: 1050\n"),
            "PL-P909-a.md": ITEM.format(id="PL-P909", status="done", extra=""),
        },
    )

    assert _run(monkeypatch, "1050") == 1
    err = capsys.readouterr().err
    assert "closes PL-P909, PL-YHF1" in err
    assert "not recorded on PL-P909." in err


def test_a_drop_owes_no_number(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _install(
        monkeypatch,
        base={"PL-K7QX-a.md": ITEM.format(id="PL-K7QX", status="ready", extra="")},
        head={"PL-K7QX-a.md": ITEM.format(id="PL-K7QX", status="dropped", extra="")},
    )

    assert _run(monkeypatch, "1050") == 0
    assert "closes no item" in capsys.readouterr().out


def test_a_closure_already_on_the_base_is_not_this_branch_s(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # It arrived through a merge of the base, with whatever number its own
    # pull request wrote; this pull request is not owed on it.
    _install(
        monkeypatch,
        base={"PL-K7QX-a.md": ITEM.format(id="PL-K7QX", status="done", extra="pr: 900\n")},
        head={"PL-K7QX-a.md": ITEM.format(id="PL-K7QX", status="done", extra="pr: 900\n")},
    )

    assert _run(monkeypatch, "1050") == 0


def test_a_branch_that_closes_nothing_owes_nothing(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _install(
        monkeypatch,
        base={"PL-K7QX-a.md": ITEM.format(id="PL-K7QX", status="ready", extra="")},
        head={"PL-K7QX-a.md": ITEM.format(id="PL-K7QX", status="ready", extra="")},
    )

    assert _run(monkeypatch, "1050") == 0
    assert "closes no item" in capsys.readouterr().out


def test_an_unset_number_is_not_a_failure(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # A hand run outside a pull request says so rather than failing a checkout
    # that has done nothing wrong.
    assert _run(monkeypatch, None) == 0
    assert "PR_NUMBER is not set" in capsys.readouterr().err


def test_a_number_that_is_not_one_fails_rather_than_certifying(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    assert _run(monkeypatch, "abc") == 1
    assert "not a pull request number" in capsys.readouterr().err


def _git_answering(**refs: dict[str, str]):
    """`subprocess.run` as git answers `_git`: each ref's tree, exit 128 for any other."""
    tree = _tree(**refs)

    def run(argv: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        args = list(argv[1:])
        if args[0] == "rev-parse":
            return subprocess.CompletedProcess(argv, 0, "claude/pl-hmzz-slug\n", "")
        ref = args[3] if args[0] == "ls-tree" else args[1].partition(":")[0]
        if ref in refs:
            return subprocess.CompletedProcess(argv, 0, tree(args), "")
        return subprocess.CompletedProcess(argv, 128, "", f"fatal: Not a valid object name {ref}\n")

    return run


def test_a_tree_git_cannot_read_is_not_checked_and_the_gate_fails(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # An unreadable base read as empty would make every closure the head holds
    # this branch's; an unreadable head read as empty would pass anything.
    monkeypatch.setattr(
        subprocess,
        "run",
        _git_answering(head={"PL-K7QX-a.md": ITEM.format(id="PL-K7QX", status="done", extra="")}),
    )
    monkeypatch.setenv("PR_NUMBER", "1050")
    monkeypatch.setattr(
        "sys.argv", ["pr_record_check.py", "--base", "no-such-base", "--head", "head"]
    )

    assert pr_record_check.main() == 1
    err = capsys.readouterr().err
    assert "not checked" in err
    assert "PL-K7QX" not in err


def test_discover_skips_silently_where_no_pull_request_is_open(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # `make check` runs this offline and on branches nobody has opened anything
    # for, and must stay green there.
    monkeypatch.setattr(pr_record_check, "repo_slug", lambda: "owner/repo")
    monkeypatch.setattr(pr_record_check, "_branch", lambda: "claude/pl-hmzz-slug")
    monkeypatch.setattr(pr_record_check, "open_pull_request", lambda slug, branch: None)
    _install(
        monkeypatch,
        base={"PL-K7QX-a.md": ITEM.format(id="PL-K7QX", status="ready", extra="")},
        head={"PL-K7QX-a.md": ITEM.format(id="PL-K7QX", status="done", extra="")},
    )

    assert _run(monkeypatch, None, "--discover") == 0
    assert capsys.readouterr() == ("", "")


def test_discover_checks_against_the_open_pull_request_s_number(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # The lookup failing is a skip; the check failing is not. A session that
    # has closed an item with its pull request open learns before it pushes.
    monkeypatch.setattr(pr_record_check, "repo_slug", lambda: "owner/repo")
    monkeypatch.setattr(pr_record_check, "_branch", lambda: "claude/pl-hmzz-slug")
    monkeypatch.setattr(
        pr_record_check, "open_pull_request", lambda slug, branch: (1050, "PL-K7QX: do it")
    )
    _install(
        monkeypatch,
        base={"PL-K7QX-a.md": ITEM.format(id="PL-K7QX", status="ready", extra="")},
        head={"PL-K7QX-a.md": ITEM.format(id="PL-K7QX", status="done", extra="")},
    )

    assert _run(monkeypatch, None, "--discover") == 1
    assert "bin/docket record 1050" in capsys.readouterr().err


def test_discover_does_not_fail_on_a_tree_it_cannot_read(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(pr_record_check, "repo_slug", lambda: "owner/repo")
    monkeypatch.setattr(pr_record_check, "_branch", lambda: "claude/pl-hmzz-slug")
    monkeypatch.setattr(
        pr_record_check, "open_pull_request", lambda slug, branch: (1050, "PL-K7QX: do it")
    )
    monkeypatch.setattr(subprocess, "run", _git_answering())
    monkeypatch.delenv("PR_NUMBER", raising=False)
    monkeypatch.setattr(
        "sys.argv", ["pr_record_check.py", "--base", "no-such-base", "--head", "head", "--discover"]
    )

    assert pr_record_check.main() == 0
    assert "not checked" in capsys.readouterr().err
