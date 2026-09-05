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


def test_the_lookup_declines_without_a_token_rather_than_reaching_the_network(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("GH_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    def never(*_: object, **__: object) -> object:
        raise AssertionError("no token, so no request should have been made")

    monkeypatch.setattr(pr_title_check.urllib.request, "urlopen", never)

    assert pr_title_check.open_pull_request("o/r", "branch") is None


def test_a_lookup_that_cannot_answer_is_a_skip_rather_than_a_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Offline, behind a proxy that refuses, rate-limited, or a repository this
    # token cannot see: all one answer, because the caller does the same thing
    # for each and a message nobody can act on differently is noise.
    monkeypatch.setenv("GH_TOKEN", "x")

    def refuse(*_: object, **__: object) -> object:
        raise OSError("Name or service not known")

    monkeypatch.setattr(pr_title_check.urllib.request, "urlopen", refuse)

    assert pr_title_check.open_pull_request("o/r", "branch") is None


def test_the_slug_is_read_from_every_remote_spelling_this_repository_uses(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # `.gitconfig` here rewrites both ssh spellings to https, so all three
    # reach this function in practice depending on when it is called.
    for url in (
        "https://github.com/stuthedew/open-anesthesia-sim.git",
        "https://github.com/stuthedew/open-anesthesia-sim",
        "git@github.com:stuthedew/open-anesthesia-sim.git",
        "ssh://git@github.com/stuthedew/open-anesthesia-sim.git",
    ):
        monkeypatch.setattr(pr_title_check, "_git", lambda _, url=url: url + "\n")
        assert pr_title_check._repo_slug() == "stuthedew/open-anesthesia-sim", url


def test_a_remote_that_is_not_github_reads_as_no_slug(monkeypatch: pytest.MonkeyPatch) -> None:
    # Not an error: a checkout with a different remote, or none, simply has no
    # pull request to look up, and that is the skip like any other.
    for url in ("https://gitlab.com/o/r.git", "/srv/mirrors/bare.git", ""):
        monkeypatch.setattr(pr_title_check, "_git", lambda _, url=url: url + "\n")
        assert pr_title_check._repo_slug() is None, url


def test_a_detached_head_has_no_branch_to_look_up(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(pr_title_check, "_git", lambda _: "HEAD\n")
    assert pr_title_check._branch() is None
