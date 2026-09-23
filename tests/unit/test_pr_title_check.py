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

The request behind `--discover` is `tools/open_pull_requests.py`'s since
`PL-Q664` gave `docket flight` the same question, and
`tests/unit/test_open_pull_requests.py` holds it: the token, the timeout, the
URL, and every reason a lookup declines. What stays here is what this tool does
with the answer.
"""

from __future__ import annotations

import subprocess

import open_pull_requests
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


def _git_answering(**refs: dict[str, str]):
    """`subprocess.run` as git answers `_git`: each ref's tree, exit 128 for any other.

    The fakes above replace `_git` itself, and so cannot say how a failure
    reaches it. This leaves `_git` as written, so what is under test is the
    whole path from git's exit status to the verdict (`PL-1PBV`).
    """
    tree = _tree(**refs)

    def run(argv: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        args = list(argv[1:])
        if args[0] == "rev-parse":
            return subprocess.CompletedProcess(argv, 0, "claude/pl-1pbv-slug\n", "")
        ref = args[3] if args[0] == "ls-tree" else args[1].partition(":")[0]
        if ref in refs:
            return subprocess.CompletedProcess(argv, 0, tree(args), "")
        return subprocess.CompletedProcess(argv, 128, "", f"fatal: Not a valid object name {ref}\n")

    return run


def test_a_head_git_cannot_read_is_not_a_branch_that_closes_nothing(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # The silent direction. `_git` answered a failure with the empty string, so
    # an unreadable head was an empty tree: the branch closed nothing, and any
    # title passed with exit 0.
    monkeypatch.setattr(
        subprocess,
        "run",
        _git_answering(base={"PL-K7QX-a.md": CLOSED.format(id="PL-K7QX", status="ready")}),
    )
    monkeypatch.setenv("PR_TITLE", "no id here")
    monkeypatch.setattr(
        "sys.argv", ["pr_title_check.py", "--base", "base", "--head", "no-such-head"]
    )

    assert pr_title_check.main() == 1
    captured = capsys.readouterr()
    assert "not checked" in captured.err
    assert "no-such-head" in captured.err
    assert "closes no item" not in captured.out


def test_a_base_git_cannot_read_is_not_a_branch_that_closes_everything(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # The loud direction, which failed for the wrong reason: an unreadable base
    # was an empty tree, so every item the head holds closed was this branch's,
    # and the refusal named ids nobody on the branch had closed.
    monkeypatch.setattr(
        subprocess,
        "run",
        _git_answering(head={"PL-K7QX-a.md": CLOSED.format(id="PL-K7QX", status="done")}),
    )
    monkeypatch.setenv("PR_TITLE", "no id here")
    monkeypatch.setattr(
        "sys.argv", ["pr_title_check.py", "--base", "no-such-base", "--head", "head"]
    )

    assert pr_title_check.main() == 1
    err = capsys.readouterr().err
    assert "not checked" in err
    assert "PL-K7QX" not in err


def test_an_unset_title_is_not_a_failure(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # The workflow runs this only on pull requests, but a hand-run outside one
    # should say so rather than fail a checkout that has done nothing wrong.
    monkeypatch.delenv("PR_TITLE", raising=False)
    monkeypatch.setattr("sys.argv", ["pr_title_check.py"])

    assert pr_title_check.main() == 0
    assert "PR_TITLE is not set" in capsys.readouterr().err


# --- `--discover`, which is what lets `make check` run this at all (`PL-J3BB`).
#
# The rule under test is asymmetric on purpose and both halves matter. When the
# open pull request's title *can* be read and is stale, this fails locally -
# that is the whole point, since CI was previously the only thing that could
# see it. When it cannot be read, for any reason at all, the run is silent and
# green: `make check` has to pass offline, on a branch nobody has opened a pull
# request for, and in a checkout with no token.


def _remote(url: str, **refs: dict[str, str]):
    """`_git` as `_tree`, plus an answer for `remote get-url` and the branch."""
    tree = _tree(**refs)

    def fake(args: list[str]) -> str:
        if args[:2] == ["remote", "get-url"]:
            return url + "\n"
        if args[:2] == ["rev-parse", "--abbrev-ref"]:
            return "claude/pl-j3bb-slug\n"
        return tree(args)

    return fake


def test_a_stale_title_on_the_open_pull_request_fails_locally(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # The sequencing failure this exists for: the title was right when the pull
    # request opened, and a second item closed on the branch afterwards.
    monkeypatch.setattr(
        pr_title_check,
        "_git",
        _remote(
            "https://github.com/stuthedew/open-anesthesia-sim.git",
            base={},
            head={
                "PL-P909-a.md": CLOSED.format(id="PL-P909", status="done"),
                "PL-YHF1-b.md": CLOSED.format(id="PL-YHF1", status="done"),
            },
        ),
    )
    monkeypatch.delenv("PR_TITLE", raising=False)
    monkeypatch.setattr(pr_title_check, "open_pull_request", lambda *_: (366, "PL-P909: the first"))
    monkeypatch.setattr(
        "sys.argv", ["pr_title_check.py", "--discover", "--base", "base", "--head", "head"]
    )

    assert pr_title_check.main() == 1
    err = capsys.readouterr().err
    # The number is named, because the remedy is a rename of one specific pull
    # request and a session may have several branches behind it.
    assert "#366's title" in err
    assert "PL-YHF1" in err


def test_a_discovered_title_that_leads_with_everything_passes(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(
        pr_title_check,
        "_git",
        _remote(
            "https://github.com/stuthedew/open-anesthesia-sim.git",
            base={},
            head={"PL-P909-a.md": CLOSED.format(id="PL-P909", status="done")},
        ),
    )
    monkeypatch.delenv("PR_TITLE", raising=False)
    monkeypatch.setattr(pr_title_check, "open_pull_request", lambda *_: (366, "PL-P909: the first"))
    monkeypatch.setattr(
        "sys.argv", ["pr_title_check.py", "--discover", "--base", "base", "--head", "head"]
    )

    assert pr_title_check.main() == 0
    assert "leads with PL-P909" in capsys.readouterr().out


def test_no_pull_request_to_read_is_a_silent_skip_that_never_reads_the_trees(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # Silent *and* cheap, which is the ordering the tool is written around: the
    # lookup is one request and `closes()` is several hundred `git show` calls,
    # so a branch with nothing open must not reach the second. A `_git` that
    # raises is how that is asserted rather than assumed.
    def explode(args: list[str]) -> str:
        if args[:2] in (["remote", "get-url"], ["rev-parse", "--abbrev-ref"]):
            return "https://github.com/o/r\n" if args[0] == "remote" else "branch\n"
        raise AssertionError(f"the trees must not be read when there is nothing to check: {args}")

    monkeypatch.setattr(pr_title_check, "_git", explode)
    monkeypatch.delenv("PR_TITLE", raising=False)
    monkeypatch.setattr(pr_title_check, "open_pull_request", lambda *_: None)
    monkeypatch.setattr("sys.argv", ["pr_title_check.py", "--discover"])

    assert pr_title_check.main() == 0
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_under_discover_a_tree_git_cannot_read_is_a_skip_that_says_so(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # `make check` stays green in a checkout without the base, as it does for
    # every other way `--discover` can fail. But a title was found, so the
    # skip says why rather than passing in silence.
    monkeypatch.setattr(
        subprocess,
        "run",
        _git_answering(head={"PL-K7QX-a.md": CLOSED.format(id="PL-K7QX", status="done")}),
    )
    monkeypatch.delenv("PR_TITLE", raising=False)
    monkeypatch.setattr(pr_title_check, "repo_slug", lambda: "o/r")
    monkeypatch.setattr(pr_title_check, "open_pull_request", lambda *_: (366, "no id here"))
    monkeypatch.setattr(
        "sys.argv", ["pr_title_check.py", "--discover", "--base", "no-such-base", "--head", "head"]
    )

    assert pr_title_check.main() == 0
    assert "not checked" in capsys.readouterr().err


def test_an_environment_title_wins_over_the_lookup(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # CI sets `PR_TITLE`, and `--discover` must not spend a request there.
    def never(*_: object) -> tuple[int, str] | None:
        raise AssertionError("PR_TITLE was set; nothing should have been looked up")

    _install(
        monkeypatch, base={}, head={"PL-P909-a.md": CLOSED.format(id="PL-P909", status="done")}
    )
    monkeypatch.setattr(pr_title_check, "open_pull_request", never)
    monkeypatch.setenv("PR_TITLE", "PL-P909: from the workflow")
    monkeypatch.setattr(
        "sys.argv", ["pr_title_check.py", "--discover", "--base", "base", "--head", "head"]
    )

    assert pr_title_check.main() == 0
    assert "leads with PL-P909" in capsys.readouterr().out


def test_the_lookup_reports_the_number_and_the_title_it_was_given() -> None:
    """All this now does is name the two fields it needs off the shared listing.

    The request itself, and every reason it can decline - no token, no network,
    a forge that refused, a body this cannot read - moved to
    `open_pull_requests.py` when `docket flight` came to need the same
    question (`PL-Q664`), and `tests/unit/test_open_pull_requests.py` is where
    they are held. What is left here is the mapping, and the one property that
    still belongs to this tool: an empty listing is a skip, not a title to
    check.
    """
    assert pr_title_check.open_pull_requests is open_pull_requests.open_pull_requests


def test_a_branch_with_nothing_open_reads_as_no_pull_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(pr_title_check, "open_pull_requests", lambda *a, **k: ())
    assert pr_title_check.open_pull_request("o/r", "branch") is None


def test_a_forge_that_could_not_be_asked_reads_as_no_pull_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The two are one answer here, deliberately: the caller skips on both."""
    monkeypatch.setattr(pr_title_check, "open_pull_requests", lambda *a, **k: None)
    assert pr_title_check.open_pull_request("o/r", "branch") is None


def test_the_open_pull_request_is_reported_as_its_number_and_title(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    found = (open_pull_requests.PullRequest(number=366, title="PL-P909: it", head="claude/x"),)
    monkeypatch.setattr(pr_title_check, "open_pull_requests", lambda *a, **k: found)
    assert pr_title_check.open_pull_request("o/r", "claude/x") == (366, "PL-P909: it")


def test_a_detached_head_has_no_branch_to_look_up(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(pr_title_check, "_git", lambda _: "HEAD\n")
    assert pr_title_check._branch() is None


def test_a_branch_name_git_cannot_read_is_no_branch_to_look_up(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # `_git` raises now, and `--discover` must still skip rather than crash.
    def refuse(argv: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(argv, 128, "", "fatal: not a git repository\n")

    monkeypatch.setattr(subprocess, "run", refuse)
    assert pr_title_check._branch() is None
