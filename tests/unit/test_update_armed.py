"""Tests for `tools/update_armed.py`, which brings `main` into armed pull requests behind it.

GitHub is replaced by a fake that answers the three readings and records every
update, so what is pinned is the rule: which pull requests are written to, on
which head, and that a failed reading or a refused token writes nothing more.
The one real file read is the workflow, for the spelling of its secret.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import update_armed
from update_armed import WRITE_TOKEN, Answer, Declined, GitHub, run

SLUG = "owner/repo"
WORKFLOW = Path(__file__).resolve().parents[2] / ".github" / "workflows" / "update-armed.yml"


def _entry(number: int, *, armed: bool = True, draft: bool = False, fork: bool = False) -> dict:
    return {
        "number": number,
        "draft": draft,
        "auto_merge": {"merge_method": "squash"} if armed else None,
        "head": {
            "ref": f"claude/branch-{number}",
            "sha": f"{number:040d}",
            "repo": {"full_name": "someone/fork" if fork else SLUG},
        },
    }


class FakeGitHub(GitHub):
    """Answers from tables keyed by head commit, and records each update asked for."""

    def __init__(
        self,
        entries: list[dict],
        *,
        behind: dict[str, int] | None = None,
        runs: dict[str, list[dict]] | None = None,
        answers: dict[int, Answer] | None = None,
        write_token: str | None = "token",
    ) -> None:
        super().__init__(SLUG, None, write_token, root="https://api.invalid")
        self.entries = entries
        self.behind = behind or {}
        self.runs = runs or {}
        self.answers = answers or {}
        self.updated: list[tuple[int, str]] = []

    def get(self, path: str) -> object:
        if "/pulls?" in path:
            return self.entries
        if compare := re.search(r"/compare/main\.\.\.(\w+)$", path):
            if compare.group(1) not in self.behind:
                raise Declined(f"GitHub could not be read at {path}: HTTP 404, Not Found")
            return {"behind_by": self.behind[compare.group(1)]}
        if checks := re.search(r"/commits/(\w+)/check-runs", path):
            found = self.runs.get(checks.group(1), [])
            return {"total_count": len(found), "check_runs": found}
        raise AssertionError(f"unexpected read {path}")

    def update_branch(self, number: int, sha: str) -> Answer:
        self.updated.append((number, sha))
        return self.answers.get(number, Answer(202, {"message": "Updating pull request branch."}))


def _run(api: FakeGitHub, required: frozenset[str] = frozenset({"checks"})) -> list[str]:
    lines: list[str] = []
    run(api, "main", set(required), lines.append)
    return lines


def _sha(number: int) -> str:
    return f"{number:040d}"


def test_an_unarmed_pull_request_is_never_updated() -> None:
    # The trial's coordinator updated three unarmed pull requests by hand on
    # 2026-09-26, merging `main` under sessions still working them.
    api = FakeGitHub([_entry(7, armed=False)], behind={_sha(7): 3})

    lines = _run(api)

    assert api.updated == []
    assert lines == ["1 of 1 open pull request(s) onto main not armed, so not read"]


def test_an_armed_pull_request_behind_its_base_is_updated_on_the_head_it_was_read_at() -> None:
    api = FakeGitHub([_entry(8)], behind={_sha(8): 2})

    lines = _run(api)

    assert api.updated == [(8, _sha(8))]
    assert lines[-1] == "#8 claude/branch-8: 2 behind main, updated"


def test_one_level_with_its_base_is_left_as_it_stands() -> None:
    api = FakeGitHub([_entry(9)], behind={_sha(9): 0})

    assert _run(api)[0] == "#9 claude/branch-9: level with main"
    assert api.updated == []


@pytest.mark.parametrize(
    ("entry", "why"),
    [
        (_entry(10, draft=True), "armed, but a draft"),
        (_entry(10, fork=True), "armed, but from a fork"),
    ],
)
def test_a_draft_or_a_fork_is_listed_and_not_read_further(entry: dict, why: str) -> None:
    # No `behind` entry: a comparison asked for would raise in the fake.
    api = FakeGitHub([entry])

    assert _run(api)[0] == f"#10 claude/branch-10: {why}"
    assert api.updated == []


def test_a_failed_required_check_holds_one_back_and_a_failed_unrequired_check_does_not() -> None:
    api = FakeGitHub(
        [_entry(11), _entry(12)],
        behind={_sha(11): 1, _sha(12): 1},
        runs={
            _sha(11): [{"name": "checks", "conclusion": "failure"}],
            _sha(12): [
                {"name": "checks", "conclusion": "success"},
                {"name": "advisory", "conclusion": "failure"},
            ],
        },
    )

    lines = _run(api)

    assert api.updated == [(12, _sha(12))]
    assert lines[0] == (
        "#11 claude/branch-11: 1 behind main, but required check 'checks' failed on its head, "
        "which is its session's to fix"
    )


@pytest.mark.parametrize("conclusion", [None, "cancelled", "action_required"])
def test_checks_still_running_or_stopped_short_of_a_verdict_do_not_hold_one_back(
    conclusion: str | None,
) -> None:
    api = FakeGitHub(
        [_entry(13)],
        behind={_sha(13): 1},
        runs={_sha(13): [{"name": "checks", "status": "in_progress", "conclusion": conclusion}]},
    )

    _run(api)

    assert api.updated == [(13, _sha(13))]


def test_without_the_token_nothing_is_written_and_what_would_have_been_is_listed() -> None:
    api = FakeGitHub([_entry(14)], behind={_sha(14): 4}, write_token=None)

    lines = _run(api)

    assert api.updated == []
    assert lines[-1] == f"#14 claude/branch-14: 4 behind main, not updated: no {WRITE_TOKEN}"


def test_a_conflict_is_listed_and_the_next_pull_request_is_still_updated() -> None:
    conflict = Answer(422, {"message": "merge conflict between base and head"})
    api = FakeGitHub(
        [_entry(15), _entry(16)], behind={_sha(15): 1, _sha(16): 1}, answers={15: conflict}
    )

    lines = _run(api)

    assert api.updated == [(15, _sha(15)), (16, _sha(16))]
    assert lines[-2:] == [
        "#15 claude/branch-15: 1 behind main, not updated: "
        "GitHub answered 'merge conflict between base and head'",
        "#16 claude/branch-16: 1 behind main, updated",
    ]


def test_a_refused_token_stops_the_run_and_names_the_permission_github_asked_for() -> None:
    refused = Answer(
        403, {"message": "Resource not accessible by personal access token"}, "workflows=write"
    )
    api = FakeGitHub(
        [_entry(17), _entry(18)], behind={_sha(17): 1, _sha(18): 1}, answers={17: refused}
    )

    with pytest.raises(Declined, match=r"HTTP 403.*workflows=write"):
        _run(api)
    assert api.updated == [(17, _sha(17))]


def test_a_reading_that_fails_updates_nothing_even_where_the_reading_before_it_held() -> None:
    # #19 alone would be updated; #20's comparison cannot be read.
    api = FakeGitHub([_entry(19), _entry(20)], behind={_sha(19): 1})

    with pytest.raises(Declined, match="HTTP 404"):
        _run(api)
    assert api.updated == []


def test_a_listing_without_the_auto_merge_field_is_refused_rather_than_read_as_unarmed() -> None:
    entry = _entry(21)
    del entry["auto_merge"]
    api = FakeGitHub([entry], behind={_sha(21): 1})

    with pytest.raises(Declined, match="could not be read"):
        _run(api)


def test_the_workflow_hands_the_script_its_secret_under_the_name_the_script_reads() -> None:
    # A misspelt secret reads as an absent one, and the run then passes, listing.
    assert f"{WRITE_TOKEN}: ${{{{ secrets.{WRITE_TOKEN} }}}}" in WORKFLOW.read_text(
        encoding="utf-8"
    )


def test_main_stops_red_and_says_why_when_a_reading_fails(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def unreachable(repo: str, branch: str, token: str | None) -> tuple[set[str], list[str]]:
        raise RuntimeError("could not read https://api.github.com/...: timed out")

    monkeypatch.setattr(update_armed, "required_contexts", unreachable)
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    monkeypatch.delenv("GITHUB_STEP_SUMMARY", raising=False)

    assert update_armed.main(["--repo", SLUG]) == 1
    assert "the required checks on main could not be read" in capsys.readouterr().err
