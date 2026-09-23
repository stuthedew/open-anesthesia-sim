"""Tests for `tools/left_behind_check.py`, the exact left-behind check.

The fixtures are real git repositories: a bare `origin` and a clone of it, with
`refs/pull/<n>/head` written into the bare remote the way GitHub writes it, so
`ls-remote`, ancestry and the squash merges are git's own answers. Only GitHub's
pull-request listing is substituted, since it is not git, and no test here
touches a network.

The two recorded vectors are rebuilt in the same shape under their real branch
names. `#284`: the branch stood one commit past the frozen `refs/pull/284/head`
(`9fee36c` against `7f87bf5`), so that commit is the loss. `#499`: the branch tip
was exactly `refs/pull/499/head` when it squash-merged as `355b604c`, so nothing
was left behind, and the squash must not confound that.
"""

from __future__ import annotations

import io
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

import left_behind_check
import pytest
from left_behind_check import (
    NO_NETWORK,
    NO_PERMISSION,
    NO_SUCH_REF,
    Commit,
    Declined,
    Git,
    PullRequest,
    Report,
    Verdict,
    check,
    github_lookup,
    lines,
    main,
    read_remote,
)


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    ).stdout.strip()


class Forge:
    """A bare `origin`, a working clone, and GitHub's pull-request listing faked."""

    def __init__(self, tmp_path: Path) -> None:
        self.remote = tmp_path / "remote.git"
        self.work = tmp_path / "work"
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(self.remote)], check=True)
        subprocess.run(["git", "init", "-q", "-b", "main", str(self.work)], check=True)
        for name, value in (("user.email", "t@example.com"), ("user.name", "T")):
            _git(self.work, "config", name, value)
        _git(self.work, "remote", "add", "origin", str(self.remote))
        self.pulls: dict[str, PullRequest] = {}
        self.commit("seed.txt", "seed", "seed")
        _git(self.work, "push", "-q", "origin", "main")

    def commit(self, path: str, text: str, message: str) -> str:
        (self.work / path).write_text(text, encoding="utf-8")
        _git(self.work, "add", "-A")
        _git(self.work, "commit", "-qm", message)
        return _git(self.work, "rev-parse", "HEAD")

    def branch(self, name: str) -> None:
        _git(self.work, "checkout", "-qB", name, "origin/main")

    def push(self, name: str, *, force: bool = False) -> None:
        _git(self.work, "push", "-q", *(["--force"] if force else []), "origin", f"HEAD:{name}")
        _git(self.work, "fetch", "-q", "origin")

    def merge(self, name: str, number: int) -> str:
        """Freeze `refs/pull/<number>/head` at the branch's tip and squash it onto main."""
        head = _git(self.work, "rev-parse", name)
        _git(self.remote, "update-ref", f"refs/pull/{number}/head", head)
        _git(self.work, "checkout", "-q", "main")
        _git(self.work, "merge", "-q", "--squash", name)
        _git(self.work, "commit", "-qm", f"{name} (#{number})")
        _git(self.work, "push", "-q", "origin", "main")
        _git(self.work, "checkout", "-q", name)
        self.pulls[name] = PullRequest(number=number, state="closed", merged=True)
        return head

    def lookup(self, branch: str) -> PullRequest | None:
        return self.pulls.get(branch)

    def verdict(self, branch: str, root: Path | None = None) -> Verdict:
        report = check(root or self.work, lookup=self.lookup)
        assert not report.declined, report.declined
        return next(verdict for verdict in report.verdicts if verdict.branch == branch)


@pytest.fixture
def forge(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Forge:
    monkeypatch.setattr(left_behind_check, "repo_slug", lambda: "owner/repo")
    return Forge(tmp_path)


def test_a_commit_pushed_after_the_merge_is_named_exactly(forge: Forge) -> None:
    """`#284`: the one commit past the frozen head is the loss, and only it."""
    forge.branch("claude/triage-n7hzpe")
    forge.commit("a.txt", "triage", "PL-0001: triage")
    forge.push("claude/triage-n7hzpe")
    forge.merge("claude/triage-n7hzpe", 284)
    lost = forge.commit("b.txt", "follow-up", "PL-0001: the behaviour change")
    forge.push("claude/triage-n7hzpe")

    verdict = forge.verdict("claude/triage-n7hzpe")

    assert verdict.number == 284
    assert [commit.sha for commit in verdict.left] == [lost]
    [finding, recovery] = lines(Report(verdicts=(verdict,)), frozenset())
    assert "claude/triage-n7hzpe carries 1 commit(s) pushed after #284 merged" in finding
    assert lost[:9] in finding and "PL-0001: the behaviour change" in finding
    assert "open a pull request from the branch" in recovery


def test_a_squash_merged_at_its_tip_is_silent_though_the_base_rewrote_its_file(
    forge: Forge,
) -> None:
    """`#499`: tip equals the frozen head, and no content question is asked.

    The base edits the branch's file after the squash, which is the shape that
    made the content comparison fire falsely on `#312` (`PL-JHJ3`).
    """
    forge.branch("claude/optimistic-fermat-a7wnfe")
    forge.commit("a.txt", "one", "PL-0002: first")
    forge.commit("a.txt", "two", "PL-0002: second")
    forge.push("claude/optimistic-fermat-a7wnfe")
    forge.merge("claude/optimistic-fermat-a7wnfe", 499)
    _git(forge.work, "checkout", "-q", "main")
    forge.commit("a.txt", "three", "PL-0003: the base rewrites the same file")
    _git(forge.work, "push", "-q", "origin", "main")

    verdict = forge.verdict("claude/optimistic-fermat-a7wnfe")

    assert verdict.clear == "#499 merged at its tip"
    assert lines(Report(verdicts=(verdict,)), frozenset()) == []


def test_merging_the_base_in_after_the_merge_leaves_no_work_behind(forge: Forge) -> None:
    forge.branch("claude/b")
    forge.commit("a.txt", "work", "PL-0004: work")
    forge.push("claude/b")
    forge.merge("claude/b", 7)
    _git(forge.work, "checkout", "-q", "main")
    forge.commit("c.txt", "later", "PL-0005: later work on main")
    _git(forge.work, "push", "-q", "origin", "main")
    _git(forge.work, "checkout", "-q", "claude/b")
    _git(forge.work, "merge", "-q", "--no-edit", "main")
    forge.push("claude/b")

    assert forge.verdict("claude/b").clear == "only merges of the base since #7 merged"


def test_an_open_pull_request_covers_whatever_the_branch_carries(forge: Forge) -> None:
    forge.branch("claude/open")
    forge.commit("a.txt", "work", "PL-0006: work")
    forge.push("claude/open")
    forge.pulls["claude/open"] = PullRequest(number=8, state="open", merged=False)

    assert forge.verdict("claude/open").clear == "#8 is open on it"


def test_a_branch_restarted_after_its_merge_is_not_reported_even_without_the_head(
    forge: Forge, tmp_path: Path
) -> None:
    """A fresh clone lacks the old head, and not holding it proves it is no ancestor."""
    forge.branch("claude/again")
    forge.commit("a.txt", "work", "PL-0007: work")
    forge.push("claude/again")
    forge.merge("claude/again", 9)
    forge.branch("claude/again")
    forge.commit("d.txt", "new", "PL-0008: follow-up on a restarted branch")
    forge.push("claude/again", force=True)
    fresh = tmp_path / "fresh"
    subprocess.run(["git", "clone", "-q", f"file://{forge.remote}", str(fresh)], check=True)

    head = _git(forge.remote, "rev-parse", "refs/pull/9/head")

    here = forge.verdict("claude/again")
    there = forge.verdict("claude/again", root=fresh)

    assert here.clear == there.clear == "it does not descend from the head #9 merged"
    assert not left_behind_check._has_commit(head, left_behind_check.git_runner(fresh))


def test_a_pull_request_whose_head_ref_is_gone_declines(forge: Forge) -> None:
    """`PL-LF2C`: a deleted `refs/pull/<n>/head` is never read as nothing left behind."""
    forge.branch("claude/gone")
    forge.commit("a.txt", "work", "PL-0009: work")
    forge.push("claude/gone")
    forge.merge("claude/gone", 350)
    forge.commit("e.txt", "late", "PL-0009: pushed after the merge")
    forge.push("claude/gone")
    _git(forge.remote, "update-ref", "-d", "refs/pull/350/head")

    verdict = forge.verdict("claude/gone")

    assert verdict.declined.startswith(NO_SUCH_REF) and "refs/pull/350/head" in verdict.declined
    assert verdict.left == ()
    assert lines(Report(verdicts=(verdict,)), frozenset()) == [
        f"left-behind: claude/gone not checked - {verdict.declined}."
    ]


def test_the_default_branch_and_branches_already_on_it_are_not_looked_up(forge: Forge) -> None:
    forge.branch("claude/landed")
    forge.push("claude/landed")
    asked: list[str] = []

    def lookup(branch: str) -> PullRequest | None:
        asked.append(branch)
        return None

    report = check(forge.work, lookup=lookup)

    assert [verdict.branch for verdict in report.verdicts] == ["claude/landed"]
    assert report.verdicts[0].clear == "already on the default branch"
    assert asked == []


def test_a_tip_this_checkout_has_not_fetched_declines_for_that_branch(
    forge: Forge, tmp_path: Path
) -> None:
    other = tmp_path / "other"
    subprocess.run(["git", "clone", "-q", f"file://{forge.remote}", str(other)], check=True)
    for name, value in (("user.email", "t@example.com"), ("user.name", "T")):
        _git(other, "config", name, value)
    _git(other, "checkout", "-qb", "claude/elsewhere")
    (other / "f.txt").write_text("x", encoding="utf-8")
    _git(other, "add", "-A")
    _git(other, "commit", "-qm", "PL-0010: pushed from another clone")
    _git(other, "push", "-q", "origin", "claude/elsewhere")

    report = check(forge.work, lookup=forge.lookup)

    [verdict] = report.verdicts
    assert "is not in this checkout; git fetch origin" in verdict.declined


def test_a_shallow_checkout_declines_whole(forge: Forge, tmp_path: Path) -> None:
    shallow = tmp_path / "shallow"
    subprocess.run(
        ["git", "clone", "-q", "--depth=1", f"file://{forge.remote}", str(shallow)], check=True
    )

    assert "shallow" in check(shallow, lookup=forge.lookup).declined


def test_a_remote_that_is_not_github_s_declines_whole(
    forge: Forge, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(left_behind_check, "repo_slug", lambda: None)

    assert "not a GitHub repository" in check(forge.work, lookup=forge.lookup).declined


def test_a_failed_lookup_declines_the_whole_report(forge: Forge) -> None:
    forge.branch("claude/b")
    forge.commit("a.txt", "work", "PL-0011: work")
    forge.push("claude/b")

    def unreachable(branch: str) -> PullRequest | None:
        raise Declined(f"{NO_NETWORK}: GitHub could not be reached")

    report = check(forge.work, lookup=unreachable)

    assert report.declined.startswith(NO_NETWORK) and report.verdicts == ()
    [line] = lines(report, frozenset())
    assert line.startswith("left-behind: not checked - no network")


@pytest.mark.parametrize(
    ("error", "kind"),
    [
        ("fatal: unable to access 'https://github.com/o/r/': Could not resolve host", NO_NETWORK),
        ("fatal: unable to access 'x': The requested URL returned error: 403", NO_PERMISSION),
        ("fatal: Authentication failed for 'https://github.com/o/r/'", NO_PERMISSION),
    ],
)
def test_git_s_refusal_and_its_unreachability_are_named_apart(error: str, kind: str) -> None:
    with pytest.raises(Declined, match=f"^{kind}: git ls-remote origin failed"):
        read_remote(lambda args: Git(128, "", error))


def _answer(monkeypatch: pytest.MonkeyPatch, outcome: bytes | Exception) -> None:
    def urlopen(request: object, timeout: float) -> io.BytesIO:
        if isinstance(outcome, Exception):
            raise outcome
        return io.BytesIO(outcome)

    monkeypatch.setenv("GH_TOKEN", "token")
    monkeypatch.setattr(urllib.request, "urlopen", urlopen)


@pytest.mark.parametrize(
    ("outcome", "kind"),
    [
        (urllib.error.URLError("connection refused"), NO_NETWORK),
        (TimeoutError("timed out"), NO_NETWORK),
        (urllib.error.HTTPError("u", 403, "Forbidden", {}, None), NO_PERMISSION),  # type: ignore[arg-type]
        (urllib.error.HTTPError("u", 401, "Unauthorized", {}, None), NO_PERMISSION),  # type: ignore[arg-type]
        (b"not json", "unreadable"),
        (b"{}", "unreadable"),
    ],
)
def test_github_s_failures_decline_under_their_own_names(
    monkeypatch: pytest.MonkeyPatch, outcome: bytes | Exception, kind: str
) -> None:
    _answer(monkeypatch, outcome)

    with pytest.raises(Declined, match=f"^{kind}"):
        github_lookup("owner/repo", "main")("claude/b")


def test_no_token_is_no_permission_rather_than_no_pull_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("GH_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    with pytest.raises(Declined, match=f"^{NO_PERMISSION}: no GH_TOKEN"):
        github_lookup("owner/repo", "main")("claude/b")


def test_the_listing_is_read_as_the_newest_pull_request_or_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _answer(monkeypatch, b'[{"number": 793, "state": "closed", "merged_at": "2026-09-20"}]')
    assert github_lookup("owner/repo", "main")("claude/b") == PullRequest(793, "closed", True)

    _answer(monkeypatch, b"[]")
    assert github_lookup("owner/repo", "main")("claude/b") is None


def test_each_disagreement_with_vcs_orphaned_is_printed_and_the_ref_comparison_wins() -> None:
    left = Verdict("claude/a", 1, left=(Commit("a" * 40, "2026-09-20", "late"),))
    cleared = Verdict("claude/b", 2, clear="#2 merged at its tip")
    report = Report(verdicts=(left, cleared))

    missed, disputed, _ = lines(report, frozenset({"claude/b"}))
    agreed, _ = lines(Report(verdicts=(left,)), frozenset({"claude/a"}))

    assert "vcs.orphaned does not report it, and this ref comparison wins" in missed
    assert disputed == (
        "left-behind: vcs.orphaned reports claude/b, but #2 merged at its tip, so no merged "
        "pull request left work on it; this ref comparison wins."
    )
    assert agreed.endswith("late (2026-09-20); vcs.orphaned agrees.")


def test_every_branch_clear_prints_nothing(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    clear = Report(verdicts=(Verdict("claude/b", clear="no pull request was opened from it"),))
    monkeypatch.setattr(left_behind_check, "check", lambda root: clear)
    monkeypatch.setattr(left_behind_check, "orphaned_branches", lambda root: frozenset())

    assert main([]) == 0
    assert capsys.readouterr().out == ""


def test_a_crash_in_the_check_declines_rather_than_going_quiet(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The hook discards stderr, so silence from a traceback would read as all clear."""

    def broken(root: Path) -> Report:
        raise RuntimeError("boom")

    monkeypatch.setattr(left_behind_check, "check", broken)

    assert main([]) == 0
    assert capsys.readouterr().out.startswith(
        "left-behind: not checked - the check itself failed (RuntimeError: boom)"
    )


def test_a_crash_in_vcs_orphaned_costs_only_the_agreement_clause(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import docket.vcs

    def broken(root: Path) -> object:
        raise RuntimeError("boom")

    monkeypatch.setattr(docket.vcs, "orphaned", broken)

    assert left_behind_check.orphaned_branches(Path(".")) is None
