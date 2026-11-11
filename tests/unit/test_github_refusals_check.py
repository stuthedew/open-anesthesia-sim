"""Each escape that got past a session guard is refused at GitHub, or named as open (`PL-39Y1`).

The guards on branch deletion, forced pushes and merges read what a session
typed, and after each of four fixes, another spelling got past them. A check
now reads GitHub's own rules instead (`tools/github_refusals_check.py`). These
tests replay every recorded escape against GitHub's settings for this
repository on 2026-11-11, when only `main` had a rule, and against the settings
that the owner is asked to apply (`PL-39Y1`, `PL-KH7Y`).
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import github_refusals_check as grc
import pytest
import required_checks_check as rcc

# GitHub's responses for this repository on 2026-11-11, before the owner added
# a rule, trimmed to the keys the check reads. The requests were
# `GET /repos/{repo}/branches/main`, `/rules/branches/main`,
# `/rules/branches/<a claude branch>`, `/rulesets?targets=tag` and
# `/rulesets/21260116`.
BASE_RULESET = {
    "id": 21260116,
    "name": "Base",
    "target": "branch",
    "enforcement": "active",
    "conditions": {"ref_name": {"exclude": [], "include": ["~DEFAULT_BRANCH"]}},
    "rules": [{"type": "deletion"}, {"type": "pull_request"}, {"type": "non_fast_forward"}],
    "bypass_actors": [],
}
RECORDED = {
    "/branches/main": {
        "protection": {
            "required_status_checks": {
                "enforcement_level": "everyone",
                "contexts": ["checks", "pr-title"],
            }
        }
    },
    "/rules/branches/main": [
        {"type": "deletion", "ruleset_id": 21260116},
        {"type": "pull_request", "ruleset_id": 21260116},
        {"type": "non_fast_forward", "ruleset_id": 21260116},
    ],
    "/rules/branches/" + grc.PROBE.replace("/", "%2F"): [],
    "/rulesets?targets=tag": [],
    "/rulesets/21260116": BASE_RULESET,
}

WORKFLOWS = Path(__file__).resolve().parents[2] / ".github" / "workflows"

# The two rulesets that the owner is asked to create (`PL-39Y1`).
ALL_BRANCHES = {
    "id": 2,
    "name": "All branches",
    "target": "branch",
    "enforcement": "active",
    "conditions": {"ref_name": {"exclude": [], "include": ["~ALL"]}},
    "rules": [{"type": "non_fast_forward"}],
    "bypass_actors": [],
}
RELEASE_TAGS = {
    "id": 3,
    "name": "Release tags",
    "target": "tag",
    "enforcement": "active",
    "conditions": {"ref_name": {"exclude": [], "include": ["refs/tags/v*"]}},
    "rules": [{"type": "deletion"}, {"type": "non_fast_forward"}],
    "bypass_actors": [],
}
# `main` with the `merge-hold` check added to its required checks (`PL-KH7Y`).
MAIN_REQUIRES_MERGE_HOLD = {
    "protection": {
        "required_status_checks": {
            "enforcement_level": "everyone",
            "contexts": ["checks", "pr-title", "merge-hold"],
        }
    }
}
ASKED_FOR = {
    **RECORDED,
    "/branches/main": MAIN_REQUIRES_MERGE_HOLD,
    "/rules/branches/main": [
        *RECORDED["/rules/branches/main"],
        {"type": "non_fast_forward", "ruleset_id": 2},
    ],
    "/rules/branches/" + grc.PROBE.replace("/", "%2F"): [
        {"type": "non_fast_forward", "ruleset_id": 2}
    ],
    "/rulesets?targets=tag": [{"id": 3, "name": "Release tags", "enforcement": "active"}],
    "/rulesets/2": ALL_BRANCHES,
    "/rulesets/3": RELEASE_TAGS,
}


def _github(monkeypatch: pytest.MonkeyPatch, answers: dict[str, object]) -> None:
    """Serve the check's GitHub requests from `answers`, keyed by the path after the repository."""

    def fake_get(url: str, token: str | None, attempts: int = 3) -> object:
        path = url.split("/repos/o/r", 1)[1]
        if path not in answers:
            raise RuntimeError(f"could not read {url}: not recorded")
        return answers[path]

    monkeypatch.setattr(rcc, "_get", fake_get)


def _missing(monkeypatch: pytest.MonkeyPatch, answers: dict[str, object]) -> set[str]:
    _github(monkeypatch, answers)
    return {refusal.key for refusal in grc.missing(grc.read("o/r", "main", None))}


# --- each past escape, replayed ---------------------------------------------

# Every spelling recorded as having got past a session guard (`PL-39Y1`),
# written here independently of the check's own table.
PAST_ESCAPES = (
    "git push --no-verify origin --delete <branch>",
    "git -c core.hooksPath=/dev/null push origin --delete <branch>",
    "CLAUDECODE= git push origin --delete <branch>",
    "bash -c 'gh pr merge <number> --squash'",
    "curl -X PUT .../pulls/<number>/merge",
    "curl -X DELETE .../git/refs/heads/<branch>",
    "curl -X PATCH .../git/refs/heads/<branch> -d '{\"force\": true}'",
    "git push --force origin <branch>",
    "enable_pr_auto_merge on a pull request that `bin/docket arm` holds",
)


def test_the_check_names_every_escape_the_item_records() -> None:
    assert {escape.spelling for escape in grc.GUARD_ESCAPES} >= set(PAST_ESCAPES)


@pytest.mark.parametrize("escape", grc.GUARD_ESCAPES, ids=lambda escape: escape.spelling)
def test_every_escape_says_what_refuses_it_or_that_nothing_does(escape: grc.Escape) -> None:
    """An escape names GitHub rules, the proxy with its source, or the gap it leaves open."""
    known = {refusal.key for refusal in grc.GITHUB_RULES}
    assert set(escape.rules) <= known
    assert escape.rules or escape.proxy or escape.open
    assert not (escape.open and (escape.rules or escape.proxy))


@pytest.mark.parametrize(
    "spelling, absent",
    [
        ("git push --force origin <branch>", {"branch-history"}),
        ("curl -X PATCH .../git/refs/heads/<branch> -d '{\"force\": true}'", {"branch-history"}),
        ("curl -X POST .../git/refs with a release tag's name, after deleting it", {"tag-history"}),
        (
            "enable_pr_auto_merge on a pull request that `bin/docket arm` holds",
            {"default-merge-hold"},
        ),
    ],
)
def test_the_settings_of_2026_11_11_let_these_escapes_through(
    monkeypatch: pytest.MonkeyPatch, spelling: str, absent: set[str]
) -> None:
    """Only `main` had a rule, and it did not yet require the `merge-hold` check.

    So nothing refused a forced push to any other branch, and a pull request
    that `bin/docket arm` held still merged once armed.
    """
    escape = next(escape for escape in grc.GUARD_ESCAPES if escape.spelling == spelling)
    assert set(escape.rules) & _missing(monkeypatch, RECORDED) == absent


def test_a_merge_past_the_checks_was_already_refused_on_2026_11_11(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`main`'s checks applied to an admin too, whichever client sent the merge."""
    absent = _missing(monkeypatch, RECORDED)
    for spelling in ("bash -c 'gh pr merge <number> --squash'", PAST_ESCAPES[4]):
        escape = next(escape for escape in grc.GUARD_ESCAPES if escape.spelling == spelling)
        assert escape.rules and not set(escape.rules) & absent


def test_the_settings_the_item_asks_for_refuse_every_escape_a_rule_can(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert _missing(monkeypatch, ASKED_FOR) == set()


# --- each rule, taken away ---------------------------------------------------


def _complete(monkeypatch: pytest.MonkeyPatch) -> grc.Settings:
    _github(monkeypatch, ASKED_FOR)
    return grc.read("o/r", "main", None)


@pytest.mark.parametrize(
    "change, key",
    [
        ({"default_rules": frozenset({"deletion", "pull_request"})}, "default-history"),
        ({"default_rules": frozenset({"non_fast_forward", "pull_request"})}, "default-deletion"),
        ({"default_rules": frozenset({"non_fast_forward", "deletion"})}, "default-pull-request"),
        ({"enforcement": "non_admins"}, "default-binds-admins"),
        ({"enforcement": None}, "default-binds-admins"),
        ({"required_checks": frozenset({"checks", "pr-title"})}, "default-merge-hold"),
        ({"other_rules": frozenset()}, "branch-history"),
        ({"tag_rules": frozenset({"deletion"})}, "tag-history"),
        ({"bypass": ("Base: RepositoryRole 5",)}, "no-bypass"),
    ],
)
def test_a_rule_taken_away_is_named(
    monkeypatch: pytest.MonkeyPatch, change: dict[str, object], key: str
) -> None:
    settings = replace(_complete(monkeypatch), **change)
    assert [refusal.key for refusal in grc.missing(settings)] == [key]


def test_admins_left_unbound_is_what_the_merge_guard_used_to_read(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The check fails when `main`'s required status checks do not apply to admins.

    The merge guard (`direct_merge_guard.py`) refused a merge on this setting.
    """
    answers = {
        **ASKED_FOR,
        "/branches/main": {
            "protection": {
                "required_status_checks": {
                    "enforcement_level": "non_admins",
                    "contexts": ["checks", "pr-title", "merge-hold"],
                }
            }
        },
    }
    assert _missing(monkeypatch, answers) == {"default-binds-admins"}


def test_the_merge_hold_check_counts_where_a_ruleset_requires_it(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """GitHub keeps required checks in a branch protection rule or in a ruleset.

    The owner may move them from one to the other, and the rule must not fail
    on a requirement that only moved.
    """
    answers = {
        **ASKED_FOR,
        "/branches/main": RECORDED["/branches/main"],
        "/rules/branches/main": [
            *ASKED_FOR["/rules/branches/main"],
            {
                "type": "required_status_checks",
                "ruleset_id": 21260116,
                "parameters": {"required_status_checks": [{"context": "merge-hold"}]},
            },
        ],
    }
    assert _missing(monkeypatch, answers) == set()


def test_the_required_check_is_the_one_job_that_main_s_copy_of_the_workflow_reports() -> None:
    """The rule names the check that `.github/workflows/merge-hold.yml` reports.

    The workflow must run only on `pull_request_target`. GitHub then reads the
    job from `main`, so a pull request cannot edit the job that judges it. On
    `pull_request` the job would be the pull request's own copy.
    """
    reported = [
        job.check_name
        for job in rcc.reporting_jobs(WORKFLOWS)
        if job.workflow == "merge-hold.yml"
    ]
    assert reported == ["merge-hold"] == [grc.MERGE_HOLD_CHECK]
    lines = (WORKFLOWS / "merge-hold.yml").read_text(encoding="utf-8").splitlines()
    assert set(rcc.triggers(lines)) == {"pull_request_target"}


# --- reading GitHub's settings -----------------------------------------------


def test_a_tag_ruleset_counts_only_where_it_is_active_and_covers_a_release_tag(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for change in (
        {"enforcement": "disabled"},
        {"enforcement": "evaluate"},
        {"conditions": {"ref_name": {"exclude": [], "include": ["refs/tags/release-*"]}}},
        {"conditions": {"ref_name": {"exclude": ["refs/tags/v*"], "include": ["~ALL"]}}},
    ):
        answers = {**ASKED_FOR, "/rulesets/3": {**RELEASE_TAGS, **change}}
        answers["/rulesets?targets=tag"] = [
            {"id": 3, "name": "Release tags", "enforcement": change.get("enforcement", "active")}
        ]
        assert _missing(monkeypatch, answers) == {"tag-history"}, change


def test_a_role_on_a_bypass_list_is_named_and_an_app_is_not(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A session acts as the owner's account, so a role on the list exempts the session."""
    role = {"actor_id": 5, "actor_type": "RepositoryRole", "bypass_mode": "always"}
    app = {"actor_id": 15368, "actor_type": "Integration", "bypass_mode": "always"}
    answers = {**ASKED_FOR, "/rulesets/2": {**ALL_BRANCHES, "bypass_actors": [role, app]}}
    _github(monkeypatch, answers)
    settings = grc.read("o/r", "main", None)
    assert settings.bypass == ("All branches: RepositoryRole 5",)


def test_a_bypass_list_github_does_not_show_is_reported_as_unread(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """GitHub shows the list only to a reader with write access to the ruleset."""
    hidden = {key: value for key, value in ALL_BRANCHES.items() if key != "bypass_actors"}
    _github(monkeypatch, {**ASKED_FOR, "/rulesets/2": hidden})
    settings = grc.read("o/r", "main", None)
    assert settings.bypass == ()
    assert settings.unread == ("the bypass list of the ruleset `All branches`",)


def test_main_fails_and_names_the_setting_where_a_rule_is_missing(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _github(monkeypatch, RECORDED)
    assert grc.main(["--repo", "o/r", "--branch", "main"]) == 1
    out = capsys.readouterr().out
    assert "FAIL - a forced push can replace the history of a branch other than `main`" in out
    assert "Block force pushes" in out
    assert "git push --force origin <branch>" in out


def test_main_passes_on_the_settings_the_item_asks_for(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _github(monkeypatch, ASKED_FOR)
    assert grc.main(["--repo", "o/r", "--branch", "main"]) == 0
    assert "OK" in capsys.readouterr().out


def test_main_does_not_pass_where_github_could_not_be_read(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _github(monkeypatch, {})
    assert grc.main(["--repo", "o/r", "--branch", "main"]) == 1
    assert "not a clean result" in capsys.readouterr().out
