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

import re
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
        label="on:\n  pull_request_target:\n\njobs:\n  triage:\n    runs-on: ubuntu-latest\n",
    )
    assert [job.check_name for job in rcc.reporting_jobs(directory)] == ["triage"]


# --- the parser: every spelling of `on:`, read once (`PL-848V`) ---------------


def _events(on: str) -> set[str]:
    """The events `triggers` reads off a workflow opening with `on`."""
    return set(rcc.triggers((on + "jobs:\n").split("\n")))


def _reported(directory: Path, branch: str | None = None) -> list[str]:
    return [job.check_name for job in rcc.reporting_jobs(directory, branch)]


@pytest.mark.parametrize(
    "on", ["on:\n  - push\n  - pull_request\n", "on:\n- push\n- pull_request\n"]
)
def test_a_block_sequence_on_names_its_events(tmp_path: Path, on: str) -> None:
    """A list under `on:`, indented or at the key's own indentation (YAML 1.2.2 § 8.2.1).

    Read as no events, so a pull-request workflow written this way dropped out
    of the reconciliation and the check passed without it (`PL-848V`).
    """
    assert _events(on) == {"push", "pull_request"}
    directory = _workflows(tmp_path, quality=on + "jobs:\n  checks:\n    runs-on: x\n")
    assert _reported(directory) == ["checks"]


@pytest.mark.parametrize(
    "on",
    [
        "on: {push: {branches: [main]}, pull_request: {branches: [main]}}\n",
        "on:\n  {push: , pull_request}\n",
    ],
)
def test_a_flow_mapping_on_names_its_events(tmp_path: Path, on: str) -> None:
    """A flow mapping's keys are the events, and an event's own mapping its filters (§ 7.4.2).

    Read as one event named for the mapping's whole text, so no pull-request
    event was found (`PL-848V`). `{push: , pull_request}` leaves both values
    out, which YAML reads as null.
    """
    assert _events(on) == {"push", "pull_request"}
    directory = _workflows(tmp_path, quality=on + "jobs:\n  checks:\n    runs-on: x\n")
    assert _reported(directory, "main") == ["checks"]


@pytest.mark.parametrize(
    ("on", "events"),
    [
        ("on: pull_request  # every pull request\n", {"pull_request"}),
        ("on: [push, pull_request]  # both\n", {"push", "pull_request"}),
        ("on:\n  pull_request:  # every pull request\n", {"pull_request"}),
        ("on:  # what starts this workflow\n  pull_request:\n", {"pull_request"}),
        ("on: &triggers\n  pull_request:\n", {"pull_request"}),
        ("on: &triggers\t[push, pull_request]\n", {"push", "pull_request"}),
    ],
)
def test_a_trailing_comment_is_no_part_of_an_event_name(on: str, events: set[str]) -> None:
    """A `#` after white space opens a comment, which no event name holds (YAML 1.2.2 § 6.6).

    `on: pull_request  # every PR` was the one event `pull_request  # every
    PR`, so the workflow reported onto no pull request (`PL-PZP7`). An anchor
    names the value it opens and changes nothing in it (§ 6.9.2).
    """
    assert _events(on) == events


@pytest.mark.parametrize(
    "on",
    ["on:\n  pull_request\n", "on:\n  [push, pull_request]\n", "on:\n  # why\n  pull_request\n"],
)
def test_an_on_value_on_the_line_after_the_key_names_its_events(on: str) -> None:
    """A value may open on the line after its key (§ 8.2.2), which read as no events (`PL-4T49`)."""
    assert "pull_request" in _events(on)


@pytest.mark.parametrize(
    ("on", "form"),
    [
        ("on: >-\n  pull_request\n", "a block scalar (`>`)"),
        ("on:\n  pull_request:\n    ? paths\n    : ['src/**']\n", "an explicit key (`?`)"),
        ("on: *triggers\n", "an alias (`*`)"),
        ("on: !!str pull_request\n", "a tag (`!`)"),
        ("on: [push,\n  pull_request]\n", "a flow collection carried past its line"),
        ("on: pull_request\n  push\n", "continues onto a line indented under it"),
        ("on:\n\tpull_request:\n", "a tab indents this line"),
        ("on: push\non: pull_request\n", "`on:` appears twice at the top level"),
        ("on:\n", "`on:` names no event"),
    ],
)
def test_yaml_the_reader_does_not_read_is_refused_by_name(on: str, form: str) -> None:
    """Refused with its form and line, never read as no trigger (`PL-4T49`, `PL-R417`).

    Read a line at a time, `on: >-` was the event `>-`, and an explicit `?
    paths` key escaped the path-filter refusal.
    """
    with pytest.raises(rcc.Undecidable, match=re.escape(form)) as refused:
        _events(on)
    assert refused.value.line is not None


def test_a_workflow_indented_four_spaces_reports_its_jobs(tmp_path: Path) -> None:
    """YAML takes any indentation, so this reads as its two-space twin (`PL-GWQ7`).

    Two spaces were assumed under `on:` and `jobs:`, so this workflow reported
    nothing; and `_job_name`, assuming them too, read a job's next key as its
    `name:` carried on. A matrix is still refused at any indentation.
    """
    four = (
        "on:\n    pull_request:\n\njobs:\n    test:\n        name: tests\n"
        "        runs-on: ubuntu-latest\n    lint:\n        runs-on: ubuntu-latest\n"
    )
    directory = _workflows(tmp_path, quality=four)
    assert sorted(_reported(directory)) == ["lint", "tests"]
    matrix = four.replace("name: tests\n", "strategy:\n            matrix: {python: ['3.14']}\n")
    (directory / "quality.yml").write_text(matrix, encoding="utf-8")
    with pytest.raises(rcc.Undecidable, match="strategy"):
        rcc.reporting_jobs(directory)


@pytest.mark.parametrize(
    "jobs",
    [
        "jobs: {lint: {name: Lint, runs-on: x}}\n",
        "jobs:\n  {lint: {name: Lint, runs-on: x}}\n",
        "jobs: {lint: {name: Lint,\n  runs-on: x}}\n",
        "jobs:\n  lint: {name: Lint, runs-on: x}\n",
    ],
)
def test_a_flow_mapping_under_jobs_is_refused_by_name(tmp_path: Path, jobs: str) -> None:
    """Read a line at a time, `{lint:` was a job, and a carried `runs-on:` another (`PL-4T49`).

    Either is a check name GitHub never reports, so each form is refused by name.
    """
    directory = _workflows(tmp_path, quality="on: pull_request\n" + jobs)
    with pytest.raises(rcc.Undecidable, match="`jobs:` holds|written on its key's line"):
        rcc.reporting_jobs(directory)


def test_a_tab_indenting_a_job_is_refused_by_name(tmp_path: Path) -> None:
    """YAML indents with spaces alone (§ 6.1), and a tab read as no indent ended `jobs:` there.

    So `test` and every job after it dropped out of the reconciliation unsaid.
    """
    jobs = "jobs:\n  lint:\n    runs-on: x\n\ttest:\n    runs-on: x\n"
    directory = _workflows(tmp_path, quality="on: pull_request\n" + jobs)
    with pytest.raises(rcc.Undecidable, match=r"quality\.yml:5: a tab indents this line"):
        rcc.reporting_jobs(directory)


# --- the parser: what a pull-request event's filters leave out (`PL-C72H`) ----


def _filtered(tmp_path: Path, filters: str) -> Path:
    return _workflows(
        tmp_path, quality=f"on:\n  pull_request:\n{filters}jobs:\n  checks:\n    runs-on: x\n"
    )


@pytest.mark.parametrize(
    "filters",
    [
        "    branches: [release]\n",
        "    branches-ignore: [main]\n",
        "    branches-ignore: 'ma*'\n",
        "    branches:\n      - '**'\n      - '!main'\n",
    ],
)
def test_a_branch_filter_excluding_the_protected_branch_does_not_report(
    tmp_path: Path, filters: str
) -> None:
    """GitHub matches the filter against the branch a pull request targets, and skips the rest.

    "If a workflow is skipped due to branch filtering ... checks associated with
    that workflow will remain in a "Pending" state" (*Workflow syntax for GitHub
    Actions*), so a requirement on the job must read as orphaned, not agreed.
    The filter was not read, and this workflow read as reporting (`PL-C72H`).
    """
    assert _reported(_filtered(tmp_path, filters), "main") == []


@pytest.mark.parametrize(
    "filters",
    [
        "    branches: [main]\n",
        "    branches: main\n",
        "    branches: ['**']\n",
        "    branches: [ma*]\n",
        "    branches: ['mai?n', release]\n",
        "    branches: ['m[a-z]+n']\n",
        "    branches-ignore: ['releases/**']\n",
        "    branches: ['**', '!main', main]\n",
    ],
)
def test_a_branch_filter_admitting_the_protected_branch_reports(
    tmp_path: Path, filters: str
) -> None:
    """The cheat sheet's constructs as documented, and a later pattern overriding an earlier one."""
    assert _reported(_filtered(tmp_path, filters), "main") == ["checks"]


@pytest.mark.parametrize(
    ("filters", "why"),
    [
        ("    branches: ['refs/heads/main']\n", "does not document"),
        ("    branches: ['?main']\n", "does not document"),
        ("    branches: ['ma[_]n']\n", "does not document"),
        ("    branches: ['**+']\n", "does not document"),
        ("    branches: ['!main']\n", "lists only `!` patterns"),
        ("    branches-ignore: ['!main']\n", "under `branches-ignore:`"),
        ("    branches: [main]\n    branches-ignore: [dev]\n", "both `branches:`"),
        ("    tags: [v1]\n", "`tags:`, which GitHub's workflow schema does not allow"),
        ("    types: [opened, reopened]\n", "without `synchronize`"),
    ],
)
def test_a_filter_that_cannot_be_read_as_reporting_is_refused(
    tmp_path: Path, filters: str, why: str
) -> None:
    """A filter GitHub refuses, a pattern its cheat sheet leaves undocumented, or a commit skipped.

    A `types:` list without `synchronize` runs nothing for a later commit, so
    that commit's required check hangs as a path filter's does (`PL-NWSK`).
    """
    with pytest.raises(rcc.Undecidable, match=re.escape(why)):
        rcc.reporting_jobs(_filtered(tmp_path, filters), "main")


def test_a_branch_filter_with_no_branch_to_match_is_refused(tmp_path: Path) -> None:
    """In or out would be a guess, so it is refused (`PL-C72H`)."""
    with pytest.raises(rcc.Undecidable, match="no branch was named"):
        rcc.reporting_jobs(_filtered(tmp_path, "    branches: [main]\n"))


def test_one_event_running_on_every_pull_request_decides(tmp_path: Path) -> None:
    """Its check runs report on each pull request, whatever the other event's filter."""
    directory = _workflows(
        tmp_path,
        quality=(
            "on:\n  pull_request:\n    branches: [release]\n  pull_request_target:\n"
            "jobs:\n  checks:\n    runs-on: x\n"
        ),
    )
    assert _reported(directory, "main") == ["checks"]


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


@pytest.mark.parametrize(
    "spelling", ["quality gate  # the gate", "'quality gate'", '"quality gate" # the gate']
)
def test_the_display_name_is_the_value_yaml_reads_on_the_keys_line(
    tmp_path: Path, spelling: str
) -> None:
    """A comment is no part of a plain name, and a quoted one is read inside its quotes.

    Each was read off the key's line by splitting it at the colon, which kept a
    trailing comment in the check name (YAML 1.2.2 § 6.6) - a name branch
    protection then reports as both unrequired and missing (`PL-TMX9`).
    """
    directory = _workflows(
        tmp_path, quality=f"on: pull_request\njobs:\n  checks:\n    name: {spelling}\n"
    )
    assert [job.check_name for job in rcc.reporting_jobs(directory)] == ["quality gate"]


def test_a_quoted_display_name_holding_an_escape_is_refused(tmp_path: Path) -> None:
    """YAML unquotes `''` to `'`, which a split at the colon left doubled (`PL-TMX9`)."""
    directory = _workflows(
        tmp_path, quality="on: pull_request\njobs:\n  checks:\n    name: 'owner''s gate'\n"
    )
    with pytest.raises(rcc.Undecidable, match="holding an escape"):
        rcc.reporting_jobs(directory)


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


@pytest.mark.parametrize(
    ("trigger", "spelling"),
    [
        ("  pull_request:\n    paths:\n      - 'src/**'\n", "paths"),
        ("  pull_request_target:\n    paths-ignore: ['docs/**']\n", "paths-ignore"),
        ("  pull_request: {paths: ['src/**']}\n", "paths"),
    ],
)
def test_a_paths_filtered_pull_request_job_is_undecidable(
    tmp_path: Path, trigger: str, spelling: str
) -> None:
    """A pull request the filter excludes gets no run, so a requirement on the job hangs.

    The check name is knowable here, and that is the trap: the reconciliation
    would read agreement while merges wait forever (`PL-NWSK`).
    """
    directory = _workflows(
        tmp_path, quality=f"on:\n{trigger}\njobs:\n  checks:\n    runs-on: ubuntu-latest\n"
    )
    with pytest.raises(rcc.Undecidable, match=f"`{spelling}:` filter"):
        rcc.reporting_jobs(directory)


def test_a_paths_filter_under_push_is_not_refused(tmp_path: Path) -> None:
    """A push run reports onto no pull request, so its filter strands no requirement."""
    directory = _workflows(
        tmp_path,
        quality=(
            "on:\n  push:\n    paths:\n      - 'docs/**'\n  pull_request:\n\n"
            "jobs:\n  checks:\n    runs-on: ubuntu-latest\n"
        ),
    )
    assert [job.check_name for job in rcc.reporting_jobs(directory)] == ["checks"]


@pytest.mark.parametrize(
    ("jobs", "form"),
    [
        ("  lint:\n    runs-on: x\n stray: 1\n", "quality.yml:5: a line indented between `jobs:`"),
        ("  lint:\n      runs-on: x\n    name: L\n", "quality.yml:5: a line indented between job"),
        ("  lint:\n    - runs-on: x\n", "quality.yml:4: job `lint` holds a flow collection"),
        ("  lint:\n    runs-on: x\n  lint:\n    runs-on: y\n", "quality.yml:5: `lint:` appears"),
    ],
)
def test_a_job_mapping_yaml_refuses_is_refused_by_name(
    tmp_path: Path, jobs: str, form: str
) -> None:
    """`_jobs` reads its keys through `_keys` (`PL-CK3F`), which stops at such a line.

    Passed over, the jobs or keys after it dropped out of the reconciliation unsaid.
    """
    directory = _workflows(tmp_path, quality="on: pull_request\njobs:\n" + jobs)
    with pytest.raises(rcc.Undecidable, match=re.escape(form)):
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


def test_off_a_pull_request_the_branch_is_docket_s(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """No `--branch` and no `GITHUB_BASE_REF` reads `vcs.default_branch` (`PL-9KLN`)."""
    monkeypatch.delenv("GITHUB_BASE_REF", raising=False)
    monkeypatch.setenv("GH_TOKEN", "from-gh-token")
    monkeypatch.setattr(rcc, "default_branch", lambda root: "trunk")
    asked: list[str] = []

    def fake(repo: str, branch: str, token: str | None) -> tuple[set[str], list[str]]:
        asked.append(branch)
        return {"checks", "pr-title"}, ["classic branch protection"]

    monkeypatch.setattr(rcc, "required_contexts", fake)

    assert rcc.main(["--repo", "o/r"]) == 0
    assert asked == ["trunk"]
    assert "required-checks: o/r @ trunk" in capsys.readouterr().out
