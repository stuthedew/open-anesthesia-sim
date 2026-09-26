"""Catch both regressions that produced this check, and refuse the shapes it cannot name.

`tools/required_checks_check.py` compares two sets that drift independently:
the jobs in the tree that report a status check onto a pull request, and the
status checks repository settings require. This repository has been hurt in
both directions - `PL-KPP1` (`#377`) by a deleted job orphaning a requirement,
and `PL-H8YD` (`#654`) by a new job arriving outside one - so those two cases
are the first the comparison is held to, replayed here as fixtures.

The three halves are tested separately because they fail for different reasons.
The **parser** reads the tree and can meet a shape whose check name it must not
guess; those cases assert an `Undecidable` rather than a silent omission, since
a job quietly dropped from the reporting set reads as "nothing to reconcile"
and passes. The **comparison** is pure, so it is driven directly rather than
through a tree or a network. The **settings read** is stubbed at the transport,
because what needs proving is that both surfaces are unioned - classic branch
protection holds this repository's list today and a ruleset is where GitHub's
UI now steers, and a check reading one surface would pass emptily after a
migration.

The last test is the end-to-end one, against the repository's own workflows: it
is what fails if a future change renames `checks` or adds a reporting job, and
it needs no network because it asserts only the tree half.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
import required_checks_check as rcc

ROOT = Path(rcc.__file__).resolve().parent.parent


def _workflows(tmp_path: Path, **files: str) -> Path:
    """A `.github/workflows/` directory holding `<name>.yml` for each keyword."""
    directory = tmp_path / ".github" / "workflows"
    directory.mkdir(parents=True)
    for name, body in files.items():
        (directory / f"{name}.yml").write_text(body, encoding="utf-8")
    return directory


def _job(name: str, jobs: rcc.ReportingJob | list[rcc.ReportingJob]) -> rcc.ReportingJob:
    """The one job called `name`, so a failure names it rather than an index."""
    found = [job for job in (jobs if isinstance(jobs, list) else [jobs]) if job.check_name == name]
    assert found, f"no job reporting {name!r}"
    return found[0]


# --- the parser: which jobs report onto a pull request -----------------------


def test_scheduled_workflow_is_not_a_reporter(tmp_path: Path) -> None:
    """`drift.yml` is the live instance: scheduled, so it reports on no pull request.

    A requirement naming one of its jobs would block every pull request
    permanently rather than silently, which is the visible failure and not the
    one this check exists for (`PL-KPP1`).
    """
    directory = _workflows(
        tmp_path,
        drift=(
            "on:\n  schedule:\n    - cron: '0 6 1 * *'\n  workflow_dispatch:\n\n"
            "jobs:\n  dependencies:\n    runs-on: ubuntu-latest\n"
        ),
    )
    assert rcc.reporting_jobs(directory) == []


def test_push_only_workflow_is_not_a_reporter(tmp_path: Path) -> None:
    """A `push`-triggered job reports against the commit, never against the pull request."""
    directory = _workflows(
        tmp_path,
        nightly=(
            "on:\n  push:\n    branches: [main]\n\njobs:\n  publish:\n    runs-on: ubuntu-latest\n"
        ),
    )
    assert rcc.reporting_jobs(directory) == []


def test_block_mapping_trigger_is_read(tmp_path: Path) -> None:
    directory = _workflows(
        tmp_path,
        quality=(
            "on:\n  push:\n    branches: [main]\n  pull_request:\n\n"
            "jobs:\n  checks:\n    runs-on: ubuntu-latest\n"
        ),
    )
    assert [job.check_name for job in rcc.reporting_jobs(directory)] == ["checks"]


def test_flow_sequence_trigger_is_read(tmp_path: Path) -> None:
    directory = _workflows(
        tmp_path,
        quality="on: [push, pull_request]\n\njobs:\n  checks:\n    runs-on: ubuntu-latest\n",
    )
    assert [job.check_name for job in rcc.reporting_jobs(directory)] == ["checks"]


def test_scalar_trigger_is_read(tmp_path: Path) -> None:
    directory = _workflows(
        tmp_path, quality="on: pull_request\n\njobs:\n  checks:\n    runs-on: ubuntu-latest\n"
    )
    assert [job.check_name for job in rcc.reporting_jobs(directory)] == ["checks"]


def test_pull_request_target_counts(tmp_path: Path) -> None:
    """It reports onto the pull request exactly as `pull_request` does."""
    directory = _workflows(
        tmp_path,
        label=(
            "on:\n  pull_request_target:\n    types: [opened]\n\n"
            "jobs:\n  triage:\n    runs-on: ubuntu-latest\n"
        ),
    )
    assert [job.check_name for job in rcc.reporting_jobs(directory)] == ["triage"]


def test_the_check_name_is_the_display_name_where_a_job_declares_one(tmp_path: Path) -> None:
    """Branch protection matches the check run's name, which `name:` overrides."""
    directory = _workflows(
        tmp_path,
        quality=(
            "on:\n  pull_request:\n\njobs:\n  checks:\n"
            "    name: quality gate\n    runs-on: ubuntu-latest\n"
        ),
    )
    jobs = rcc.reporting_jobs(directory)
    assert [job.check_name for job in jobs] == ["quality gate"]
    assert jobs[0].job_id == "checks"


def test_steps_are_not_mistaken_for_jobs(tmp_path: Path) -> None:
    """A `run:` block holds colons and list items; none of them is a job key."""
    directory = _workflows(
        tmp_path,
        quality=(
            "on:\n  pull_request:\n\njobs:\n  checks:\n    runs-on: ubuntu-latest\n"
            "    steps:\n      - uses: actions/checkout@v7.0.1\n"
            "      - name: a step, not a job\n        run: |\n          echo not: a job\n"
            "          other: still not a job\n"
        ),
    )
    assert [job.check_name for job in rcc.reporting_jobs(directory)] == ["checks"]


def test_every_job_in_a_reporting_workflow_reports(tmp_path: Path) -> None:
    directory = _workflows(
        tmp_path,
        quality=(
            "on:\n  pull_request:\n\njobs:\n  checks:\n    runs-on: ubuntu-latest\n"
            "  floor:\n    runs-on: ubuntu-latest\n"
        ),
    )
    assert sorted(job.check_name for job in rcc.reporting_jobs(directory)) == ["checks", "floor"]


# --- the parser: the exemption a job declares in the tree --------------------


def test_not_required_marker_is_read_off_the_comment_above_the_job(tmp_path: Path) -> None:
    directory = _workflows(
        tmp_path,
        extra=(
            "on:\n  pull_request:\n\njobs:\n"
            "  # Advisory only while it settles.\n"
            "  # not-required: advisory until PL-0000 lands\n"
            "  spellcheck:\n    runs-on: ubuntu-latest\n"
        ),
    )
    job = _job("spellcheck", rcc.reporting_jobs(directory))
    assert job.not_required == "advisory until PL-0000 lands"


def test_a_marker_separated_by_a_blank_line_does_not_attach(tmp_path: Path) -> None:
    """Adjacency is the whole claim to being *this* job's exemption.

    A comment further up the file is about something else, and reading it as an
    exemption would silently ungate the job below it.
    """
    directory = _workflows(
        tmp_path,
        extra=(
            "on:\n  pull_request:\n\njobs:\n"
            "  # not-required: about the file, not the job\n\n"
            "  spellcheck:\n    runs-on: ubuntu-latest\n"
        ),
    )
    assert _job("spellcheck", rcc.reporting_jobs(directory)).not_required is None


def test_a_marker_does_not_leak_onto_the_next_job(tmp_path: Path) -> None:
    directory = _workflows(
        tmp_path,
        extra=(
            "on:\n  pull_request:\n\njobs:\n"
            "  # not-required: advisory\n"
            "  spellcheck:\n    runs-on: ubuntu-latest\n"
            "  checks:\n    runs-on: ubuntu-latest\n"
        ),
    )
    jobs = rcc.reporting_jobs(directory)
    assert _job("spellcheck", jobs).not_required == "advisory"
    assert _job("checks", jobs).not_required is None


# --- the parser: what it refuses to name -------------------------------------


def test_a_matrix_job_is_refused_rather_than_guessed(tmp_path: Path) -> None:
    """A matrix expands into one check per combination, named from the matrix values."""
    directory = _workflows(
        tmp_path,
        quality=(
            "on:\n  pull_request:\n\njobs:\n  checks:\n    runs-on: ubuntu-latest\n"
            "    strategy:\n      matrix:\n        python: ['3.11', '3.14']\n"
        ),
    )
    with pytest.raises(rcc.Undecidable, match="strategy"):
        rcc.reporting_jobs(directory)


def test_a_reusable_workflow_call_is_refused_rather_than_guessed(tmp_path: Path) -> None:
    """Its checks report as `<caller> / <called>`, which needs the called file to name."""
    directory = _workflows(
        tmp_path,
        quality=(
            "on:\n  pull_request:\n\njobs:\n  checks:\n    uses: ./.github/workflows/shared.yml\n"
        ),
    )
    with pytest.raises(rcc.Undecidable, match="reusable"):
        rcc.reporting_jobs(directory)


def test_a_workflow_with_no_jobs_block_is_refused(tmp_path: Path) -> None:
    directory = _workflows(tmp_path, quality="on:\n  pull_request:\n")
    with pytest.raises(rcc.Undecidable, match="jobs"):
        rcc.reporting_jobs(directory)


def test_a_workflow_with_no_trigger_block_is_refused(tmp_path: Path) -> None:
    directory = _workflows(tmp_path, quality="jobs:\n  checks:\n    runs-on: ubuntu-latest\n")
    with pytest.raises(rcc.Undecidable, match="on:"):
        rcc.reporting_jobs(directory)


# --- the comparison ----------------------------------------------------------


def _reporting(*names: str, exempt: dict[str, str] | None = None) -> dict[str, rcc.ReportingJob]:
    exempt = exempt or {}
    return {
        name: rcc.ReportingJob(
            workflow="quality.yml", job_id=name, check_name=name, not_required=exempt.get(name)
        )
        for name in names
    }


def test_agreement_is_no_problem() -> None:
    assert rcc.reconcile(_reporting("checks", "pr-title"), {"checks", "pr-title"}) == []


def test_pl_kpp1_a_deleted_job_orphans_its_requirement() -> None:
    """`PL-D551` folded `floor` into `checks` and deleted the job; `floor` stayed required.

    Every pull request then waited forever on a check that could not arrive
    (`#377`). This is the direction the workflow comments already guarded with
    prose, and the one they could not enforce.
    """
    problems = rcc.reconcile(_reporting("checks"), {"checks", "floor"})
    assert len(problems) == 1
    headline, meaning = problems[0]
    assert "reported by no job: floor" in headline
    assert "waits on them forever" in meaning


def test_pl_h8yd_a_new_job_arrives_outside_the_required_list() -> None:
    """`PL-3V8K` split the title check into its own job, moving it out from behind `checks`.

    It stayed ungated for eleven releases and `#654` merged on a failed
    `pr-title` (`PL-H8YD`). Nothing in the repository guarded this direction at
    all before this check.
    """
    problems = rcc.reconcile(_reporting("checks", "pr-title"), {"checks"})
    assert len(problems) == 1
    headline, meaning = problems[0]
    assert "is not required: pr-title" in headline
    assert "without blocking a merge" in meaning


def test_both_directions_are_reported_together() -> None:
    """A rename is both at once, and fixing one of the two leaves the gate broken."""
    problems = rcc.reconcile(_reporting("checks2"), {"checks"})
    assert [headline for headline, _ in problems] == [
        "required but reported by no job: checks",
        "reports on a pull request but is not required: checks2",
    ]


def test_an_empty_required_set_fails_rather_than_passing_quietly() -> None:
    """The migration case: the setting moves to a surface this check does not read.

    Reporting "no drift" here would be a check passing while the guarantee it
    stands for is void, which is the failure `CLAUDE.md` names first.
    """
    problems = rcc.reconcile(_reporting("checks", "pr-title"), set())
    assert len(problems) == 1
    assert "no required status check is set" in problems[0][0]


def test_an_empty_required_set_does_not_also_list_every_job_as_ungated() -> None:
    """One cause, one message. Three findings from one setting would bury it."""
    problems = rcc.reconcile(_reporting("checks", "pr-title"), set())
    assert len(problems) == 1


def test_a_declared_exemption_excuses_a_job_from_the_required_list() -> None:
    problems = rcc.reconcile(
        _reporting("checks", "spellcheck", exempt={"spellcheck": "advisory"}), {"checks"}
    )
    assert problems == []


def test_an_exemption_that_settings_contradict_is_reported() -> None:
    """The comment says advisory and the setting gates on it; a reader cannot tell which holds."""
    problems = rcc.reconcile(
        _reporting("checks", "spellcheck", exempt={"spellcheck": "advisory"}),
        {"checks", "spellcheck"},
    )
    assert len(problems) == 1
    assert "declared `not-required` but required in settings: spellcheck" in problems[0][0]


def test_an_exemption_does_not_excuse_an_orphaned_requirement() -> None:
    """Exempting a job says nothing about a requirement naming a job that is gone."""
    problems = rcc.reconcile(
        _reporting("spellcheck", exempt={"spellcheck": "advisory"}), {"checks"}
    )
    assert [headline for headline, _ in problems] == ["required but reported by no job: checks"]


# --- the settings read: both surfaces --------------------------------------


def _stub(monkeypatch: pytest.MonkeyPatch, *, branch: object, rules: object) -> None:
    def fake_get(url: str, token: str | None, attempts: int = 3) -> object:
        return rules if "/rules/branches/" in url else branch

    monkeypatch.setattr(rcc, "_get", fake_get)


def test_classic_branch_protection_is_read(monkeypatch: pytest.MonkeyPatch) -> None:
    """Where this repository's required list lives as of 2026-09-19."""
    _stub(
        monkeypatch,
        branch={"protection": {"required_status_checks": {"contexts": ["checks", "pr-title"]}}},
        rules=[],
    )
    contexts, sources = rcc.required_contexts("o/r", "main", None)
    assert contexts == {"checks", "pr-title"}
    assert sources == ["classic branch protection"]


def test_a_ruleset_is_read(monkeypatch: pytest.MonkeyPatch) -> None:
    """Where GitHub's UI steers, and where a migration would put it."""
    _stub(
        monkeypatch,
        branch={"protection": {}},
        rules=[
            {"type": "deletion"},
            {
                "type": "required_status_checks",
                "parameters": {"required_status_checks": [{"context": "checks"}]},
            },
        ],
    )
    contexts, sources = rcc.required_contexts("o/r", "main", None)
    assert contexts == {"checks"}
    assert sources == ["a ruleset"]


def test_the_two_surfaces_are_unioned_and_both_named(monkeypatch: pytest.MonkeyPatch) -> None:
    """A half-finished migration leaves one name on each, and both still gate."""
    _stub(
        monkeypatch,
        branch={"protection": {"required_status_checks": {"contexts": ["checks"]}}},
        rules=[
            {
                "type": "required_status_checks",
                "parameters": {"required_status_checks": [{"context": "pr-title"}]},
            }
        ],
    )
    contexts, sources = rcc.required_contexts("o/r", "main", None)
    assert contexts == {"checks", "pr-title"}
    assert sources == ["classic branch protection", "a ruleset"]


def test_an_unprotected_branch_yields_nothing_and_names_no_source(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`reconcile` turns this into the hard failure; the read itself reports it honestly."""
    _stub(monkeypatch, branch={}, rules=[])
    assert rcc.required_contexts("o/r", "main", None) == (set(), [])


def test_token_is_read_in_one_precedence(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """`GH_TOKEN` over `GITHUB_TOKEN`, as every other tool and `gh` itself read them.

    This tool read them the other way round, so with both set it asked GitHub
    with a different credential from the rest of the apparatus (`PL-2TV9`).
    """
    monkeypatch.setenv("GH_TOKEN", "from-gh-token")
    monkeypatch.setenv("GITHUB_TOKEN", "from-github-token")
    asked: list[str | None] = []

    def fake(repo: str, branch: str, token: str | None) -> tuple[set[str], list[str]]:
        asked.append(token)
        return {"checks", "pr-title"}, ["classic branch protection"]

    monkeypatch.setattr(rcc, "required_contexts", fake)
    assert rcc.main(["--repo", "o/r", "--branch", "main"]) == 0
    assert asked == ["from-gh-token"]
    capsys.readouterr()


def test_the_repository_is_read_from_a_token_bearing_origin(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """The URL shape an Actions checkout can leave behind reads as its slug, not an error."""
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(tmp_path),
            "remote",
            "add",
            "origin",
            "https://x-access-token:abc@github.com/o/r.git",
        ],
        check=True,
    )
    assert rcc._repo_from_git(tmp_path) == "o/r"


# --- end to end, against this repository's own workflows ---------------------


def test_this_repository_reports_exactly_checks_and_pr_title() -> None:
    """The tree half of the live reconciliation, asserted without a network.

    These two names are load-bearing outside the tree, which is why each job key
    carries a comment saying so. Renaming one, or adding a third reporting job,
    fails here as well as in CI - and here it fails in `make check`, before the
    push.
    """
    jobs = rcc.reporting_jobs(ROOT / ".github" / "workflows")
    assert sorted(job.check_name for job in jobs) == ["checks", "pr-title"]
    assert {job.workflow for job in jobs} == {"quality.yml", "pr-title.yml"}
    assert all(job.not_required is None for job in jobs)
