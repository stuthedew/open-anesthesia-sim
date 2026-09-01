"""Tests for the commission check.

Every test here asserts a *refusal*, bar one. That ratio is the point: this
command exists to catch the ways a green build can be reached without doing
the work, so a regression that made it accept everything must fail the suite
loudly. The accepting case is present so that "rejects everything" cannot pass
either.

The git history each case needs is built in a scratch repository rather than
mocked, because what is being tested is largely what git reports.
"""

from __future__ import annotations

import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest

from docket.config import Config
from docket.model import Item
from docket.verify import (
    LANDED_GUARD,
    already_passing,
    changed_paths,
    item_commits,
    selects_no_test,
    verify,
    verify_batch,
)

KEPT = "def test_a() -> None:\n    assert 1 == 1\n"

BRIEF = "**Problem.** P\n**Why it matters.** W\n**Done when.** D\n"


def _git(root: Path, *args: str) -> None:
    # A real git checkout, built by running real git from `PATH`: verification
    # is defined in terms of a diff against a base ref, so a stub would test
    # the stub. Every subprocess call in this file is here for that reason.
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)


def _repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    (root / "docs" / "items").mkdir(parents=True)
    (root / "tests").mkdir()
    (root / "src").mkdir()
    _git(root.parent, "init", "-q", str(root))
    _git(root, "config", "user.email", "t@example.com")
    _git(root, "config", "user.name", "T")
    (root / "tests" / "test_thing.py").write_text(KEPT)
    (root / "src" / "core.py").write_text("VALUE = 1\n")
    (root / "Makefile").write_text("check:\n\ttrue\n")
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "base")
    return root


def _item(**overrides: object) -> Item:
    base: dict[str, object] = dict(
        identifier="PL-K7QX",
        title="Do the thing",
        priority="P2",
        effort="S",
        status="ready",
        classes=("test",),
        touches=("tests/test_thing.py",),
        blocked_by=(),
        feature="",
        milestone="",
        added=date(2026, 8, 1),
        closed=None,
        commit="",
        reason="",
        body=BRIEF,
        verify="true",
        path="PL-K7QX-do-the-thing.md",
    )
    base.update(overrides)
    return Item(**base)  # type: ignore[arg-type]


def _config(**overrides: object) -> Config:
    settings: dict[str, object] = dict(
        protected_paths=("src",), gate_paths=("Makefile",), check_command="true"
    )
    settings.update(overrides)
    return Config(**settings)  # type: ignore[arg-type]


def _work(root: Path, message: str, path: str, text: str) -> None:
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text)
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", message)


def test_work_inside_the_declared_scope_is_accepted(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    _work(
        root,
        "PL-K7QX add a test",
        "tests/test_thing.py",
        KEPT + "\n\ndef test_b() -> None:\n    assert 2 == 2\n",
    )
    assert verify(root, _item(), _config(), "HEAD~1").passed


def test_a_file_outside_touches_is_rejected(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    _work(root, "PL-K7QX stray edit", "tests/other.py", "x = 1\n")
    report = verify(root, _item(), _config(), "HEAD~1")
    assert not report.passed
    assert any("touches" in c.name and not c.passed for c in report.checks)


def test_editing_a_protected_path_is_rejected(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    _work(root, "PL-K7QX touch the core", "src/core.py", "VALUE = 2\n")
    report = verify(root, _item(touches=("src/core.py",)), _config(), "HEAD~1")
    assert not report.passed
    assert any("protected" in c.name and not c.passed for c in report.checks)


def test_editing_the_gate_is_rejected(tmp_path: Path) -> None:
    """Changing the thing that measures the work invalidates the measurement."""
    root = _repo(tmp_path)
    _work(root, "PL-K7QX relax the build", "Makefile", "check:\n\ttrue\n\n")
    report = verify(root, _item(touches=("Makefile",)), _config(), "HEAD~1")
    assert not report.passed
    assert any("checks themselves" in c.name and not c.passed for c in report.checks)


def test_an_added_suppression_is_rejected(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    _work(
        root,
        "PL-K7QX silence it",
        "tests/test_thing.py",
        KEPT + "\n\ndef test_b() -> None:  # type: ignore[misc]\n    assert 2 == 2\n",
    )
    report = verify(root, _item(), _config(), "HEAD~1")
    assert not report.passed
    assert any("suppression" in c.name and not c.passed for c in report.checks)


def test_a_removed_assertion_is_rejected(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    _work(root, "PL-K7QX drop it", "tests/test_thing.py", "def test_a() -> None:\n    pass\n")
    report = verify(root, _item(), _config(), "HEAD~1")
    assert not report.passed
    assert any("assertion" in c.name and not c.passed for c in report.checks)


def test_a_failing_verify_command_is_rejected(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    _work(
        root,
        "PL-K7QX add a test",
        "tests/test_thing.py",
        KEPT + "\n\ndef test_b() -> None:\n    assert 2 == 2\n",
    )
    report = verify(root, _item(verify="false"), _config(), "HEAD~1")
    assert not report.passed


def test_a_failing_project_check_is_rejected(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    _work(
        root,
        "PL-K7QX add a test",
        "tests/test_thing.py",
        KEPT + "\n\ndef test_b() -> None:\n    assert 2 == 2\n",
    )
    report = verify(root, _item(), _config(check_command="false"), "HEAD~1")
    assert not report.passed


def test_an_item_with_no_verify_command_cannot_be_verified(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    report = verify(root, _item(verify=""), _config(), "HEAD")
    assert not report.passed
    assert len(report.checks) == 1


def test_uncommitted_work_is_counted(tmp_path: Path) -> None:
    """A branch is not clean because its damage has not been committed yet."""
    root = _repo(tmp_path)
    _work(
        root,
        "PL-K7QX add a test",
        "tests/test_thing.py",
        KEPT + "\n\ndef test_b() -> None:\n    assert 2 == 2\n",
    )
    (root / "src" / "core.py").write_text("VALUE = 99\n")
    assert "src/core.py" in changed_paths(root, "HEAD~1", ())


def test_the_diff_is_scoped_to_the_item_s_own_commits(tmp_path: Path) -> None:
    """A batch branch carries several items; each is judged on its own commits.

    Without this, one item checked against the whole branch fails on every
    other item's files, which is both wrong and useless.
    """
    root = _repo(tmp_path)
    base = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=True
    ).stdout.strip()
    _work(
        root,
        "PL-K7QX mine",
        "tests/test_thing.py",
        KEPT + "\n\ndef test_b() -> None:\n    assert 2 == 2\n",
    )
    _work(root, "PL-ZZZZ theirs", "tests/other.py", "x = 1\n")
    commits = item_commits(root, base, "PL-K7QX")
    assert len(commits) == 1
    assert changed_paths(root, base, commits) == ("tests/test_thing.py",)
    assert verify(root, _item(), _config(), base).passed


def test_the_item_s_own_file_is_always_in_scope(tmp_path: Path) -> None:
    """A worker is asked to append a `**Worked.**` note, so its own file counts."""
    root = _repo(tmp_path)
    _work(
        root, "PL-K7QX note", "docs/items/PL-K7QX-do-the-thing.md", "---\nid: PL-K7QX\n---\n\nx\n"
    )
    assert verify(root, _item(), _config(), "HEAD~1").passed


def test_a_base_with_nothing_between_it_and_head_is_not_a_pass(tmp_path: Path) -> None:
    """An empty diff must never read as verified work.

    Found by a test that passed the literal string "HEAD" as the base: every
    path check then had nothing to look at and every one of them passed, so a
    branch with no work in it reported ACCEPT. A mistyped or stale base is the
    likeliest way to reach this, and it is precisely the case where a
    confident green is worst.
    """
    root = _repo(tmp_path)
    report = verify(root, _item(), _config(), "HEAD")
    assert not report.passed
    assert any("something to verify" in c.name for c in report.checks)


def _runs(root: Path) -> int:
    """How many times the project-wide check has been run in this repository."""
    log = root / "runs.txt"
    return len(log.read_text().splitlines()) if log.is_file() else 0


def test_a_batch_runs_the_project_wide_check_once(tmp_path: Path) -> None:
    """Five re-proofs of a proved thing is how a reviewer learns to skip the command."""
    root = _repo(tmp_path)
    _work(
        root,
        "PL-K7QX add a test",
        "tests/test_thing.py",
        KEPT + "\ndef test_b() -> None:\n    assert 2 == 2\n",
    )
    _work(
        root, "PL-B2B2 add another", "tests/other.py", "def test_c() -> None:\n    assert 3 == 3\n"
    )
    config = _config(check_command="echo ran >> runs.txt")
    items = [
        _item(),
        _item(identifier="PL-B2B2", path="PL-B2B2-do-the-other.md", touches=("tests/other.py",)),
    ]

    reports = verify_batch(root, items, config, "HEAD~2")

    assert [report.passed for report in reports] == [True, True]
    assert _runs(root) == 1
    assert all(any("project's own checks" in c.name for c in r.checks) for r in reports)


def test_a_single_item_still_runs_the_project_wide_check(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    _work(
        root,
        "PL-K7QX add a test",
        "tests/test_thing.py",
        KEPT + "\ndef test_b() -> None:\n    assert 2 == 2\n",
    )

    report = verify(root, _item(), _config(check_command="echo ran >> runs.txt"), "HEAD~1")

    assert report.passed
    assert _runs(root) == 1


def test_each_item_in_a_batch_keeps_its_own_command(tmp_path: Path) -> None:
    """Four can be accepted and the fifth rejected, which is the point of the split."""
    root = _repo(tmp_path)
    _work(
        root,
        "PL-K7QX add a test",
        "tests/test_thing.py",
        KEPT + "\ndef test_b() -> None:\n    assert 2 == 2\n",
    )
    _work(
        root, "PL-B2B2 add another", "tests/other.py", "def test_c() -> None:\n    assert 3 == 3\n"
    )
    items = [_item(), _item(identifier="PL-B2B2", path="PL-B2B2-do-the-other.md", verify="false")]

    reports = verify_batch(root, items, _config(), "HEAD~2")

    assert [report.passed for report in reports] == [True, False]


def test_an_item_with_nothing_to_verify_does_not_hold_up_the_batch(tmp_path: Path) -> None:
    """Its report stops before the shared check, which says nothing about it."""
    root = _repo(tmp_path)
    _work(
        root,
        "PL-K7QX add a test",
        "tests/test_thing.py",
        KEPT + "\ndef test_b() -> None:\n    assert 2 == 2\n",
    )
    items = [_item(identifier="PL-B2B2", path="PL-B2B2.md", verify=""), _item()]

    reports = verify_batch(root, items, _config(check_command="echo ran >> runs.txt"), "HEAD~1")

    assert [report.passed for report in reports] == [False, True]
    assert reports[0].stopped_early
    assert _runs(root) == 1


def test_a_base_behind_its_remote_is_said_so_on_the_report(tmp_path: Path) -> None:
    """The PL-0999 failure: a fresh clone's local `main` lags what it forked from.

    Verified against that `main`, work which never left its scope is reported
    as reaching every file merged in the meantime - a refusal that reads as
    the item's fault and is not.
    """
    root = _repo(tmp_path)
    _git(root, "branch", "-M", "main")
    _git(root, "checkout", "-q", "-b", "other")
    _work(root, "another session's merged commit", "docs/items/PL-OTHR-thing.md", "x\n")
    _git(root, "update-ref", "refs/remotes/origin/main", "other")
    _git(root, "checkout", "-q", "main")
    _work(
        root,
        "PL-K7QX add a test",
        "tests/test_thing.py",
        KEPT + "\ndef test_b() -> None:\n    assert 2\n",
    )

    report = verify(root, _item(), _config(), "main")

    assert "behind origin/main" in report.base_note
    assert "behind origin/main" in report.describe()


def test_a_base_current_with_its_remote_says_nothing(tmp_path: Path) -> None:
    """A note on every report would become decoration and stop being read."""
    root = _repo(tmp_path)
    _git(root, "branch", "-M", "main")
    _git(root, "update-ref", "refs/remotes/origin/main", "main")
    _work(
        root,
        "PL-K7QX add a test",
        "tests/test_thing.py",
        KEPT + "\ndef test_b() -> None:\n    assert 2\n",
    )

    assert verify(root, _item(), _config(), "main").base_note == ""


# Finding an open item whose work already landed. Real commands rather than a
# stubbed runner, for the same reason the rest of this file uses real git:
# what is being tested is what a shell returns for a recorded command.


@pytest.fixture(autouse=True)
def _no_inherited_guard(monkeypatch: pytest.MonkeyPatch) -> None:
    """Clear the re-entry guard this suite may have inherited.

    `docket check` sets `DOCKET_SKIP_LANDED` for every command it runs, and
    one of those commands is the pytest invocation recorded as `PL-3CBS`'s own
    `verify:`. Without this, the cases below read the declined report meant for
    a nested run and the item's command fails under `check` while passing when
    run by hand - which is exactly the environment-dependent result the check
    itself exists to make visible.
    """
    monkeypatch.delenv(LANDED_GUARD, raising=False)


def test_an_item_whose_work_has_landed_is_found_by_running_its_command(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    report = already_passing(root, [_item(verify="true")])
    assert report.known
    assert report.passing == ("PL-K7QX",)
    assert report.considered == 1


def test_an_item_whose_command_still_fails_has_not_landed(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    report = already_passing(root, [_item(verify="false")])
    assert report.known
    assert report.passing == ()
    assert report.considered == 1


def test_a_closed_item_is_not_asked_whether_it_landed(tmp_path: Path) -> None:
    # `done` and `dropped` are settled, and an untriaged capture has promised
    # nothing yet. Only an open commitment can be open by mistake.
    root = _repo(tmp_path)
    items = [
        _item(identifier="PL-DONE", status="done", verify="true"),
        _item(identifier="PL-CAP", status="untriaged", verify="true"),
    ]
    assert already_passing(root, items).passing == ()


def test_a_landed_command_shared_by_two_open_items_proves_neither(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    items = [_item(identifier="PL-K7QX", verify="true"), _item(identifier="PL-A1B2", verify="true")]
    report = already_passing(root, items)
    assert report.passing == ("PL-K7QX", "PL-A1B2")
    assert report.shared == ("PL-K7QX", "PL-A1B2")


def test_a_command_unique_to_one_landed_item_is_not_called_shared(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    items = [
        _item(identifier="PL-K7QX", verify="true"),
        _item(identifier="PL-A1B2", verify="false"),
    ]
    report = already_passing(root, items)
    assert report.passing == ("PL-K7QX",)
    assert report.shared == ()


def test_the_landed_check_declines_rather_than_re_entering_docket_check(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Two open items on this store record `verify:` commands ending in
    # `bin/docket check`. Unguarded, the outer run re-enters itself once per
    # candidate and each re-entry does it again.
    root = _repo(tmp_path)
    monkeypatch.setenv(LANDED_GUARD, "1")
    report = already_passing(root, [_item(verify="true")])
    assert not report.known
    assert report.passing == ()
    assert "re-entered" in report.declined


def test_a_nested_docket_check_is_told_not_to_ask_about_landed_work(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    probe = f'test -n "${LANDED_GUARD}"'
    assert already_passing(root, [_item(verify=probe)]).passing == ("PL-K7QX",)


def test_the_landed_check_declines_when_no_command_can_be_run(tmp_path: Path) -> None:
    # What a bare checkout with no virtualenv looks like from here: every
    # command "not found". Reporting none passing would say only that the
    # toolchain is missing, which is the shape of wrong answer this package
    # declines rather than gives.
    root = _repo(tmp_path)
    items = [_item(identifier="PL-K7QX", verify="docket-no-such-command-xyz")]
    report = already_passing(root, items)
    assert not report.known
    assert "toolchain is missing" in report.declined


def test_one_missing_command_beside_a_real_one_still_reports_landed_work(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    items = [
        _item(identifier="PL-K7QX", verify="docket-no-such-command-xyz"),
        _item(identifier="PL-A1B2", verify="true"),
    ]
    report = already_passing(root, items)
    assert report.known
    assert report.passing == ("PL-A1B2",)


def test_an_item_with_no_command_is_not_a_landed_candidate(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    assert already_passing(root, [_item(verify="")]).considered == 0


# --- a command that selects no test, told apart from one that fails ----------
#
# The two arrive as the same thing at every reader of an exit status - non-zero
# - and they mean opposite things. A failing command ran an assertion that did
# not hold, which is what an unstarted item's command is meant to do. One that
# selects no test asserted nothing, and will go on asserting nothing after the
# work unless a test name happens to match.


def _pytest(selector: str) -> str:
    """A real pytest run against the scratch repository's one test.

    Deliberately the real runner rather than a stub returning 5: the whole
    claim rests on pytest returning 5 for an empty selection and 1 for a
    failing test, and a stub would test the stub's author's memory of that.
    `sys.executable` because the interpreter running this suite is the one
    that certainly has pytest importable.
    """
    return f"{sys.executable} -m pytest tests/test_thing.py -k {selector} -q -p no:cacheprovider"


def test_pytest_returns_five_for_a_selector_that_matches_nothing(tmp_path: Path) -> None:
    # The reference case the discriminator is built on, asserted against
    # pytest itself rather than against a remembered exit code.
    root = _repo(tmp_path)
    result = subprocess.run(
        _pytest("no_such_test_name"), cwd=root, shell=True, capture_output=True, text=True
    )
    assert result.returncode == 5
    assert "deselected" in result.stdout


def test_a_selector_matching_a_real_test_is_not_read_as_selecting_nothing(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    result = subprocess.run(_pytest("test_a"), cwd=root, shell=True, capture_output=True, text=True)
    assert result.returncode == 0
    assert not selects_no_test(_pytest("test_a"), result.returncode)


def test_a_failing_test_is_not_read_as_selecting_nothing() -> None:
    # Exit 1 is the state a correctly written command is supposed to be in
    # before the work, and must never be reported as an empty selection.
    assert not selects_no_test("uv run pytest tests/test_thing.py -k test_a", 1)


def test_exit_five_from_a_command_that_is_not_pytest_is_not_classified() -> None:
    # Only pytest promises that 5 means "collected nothing". Reading another
    # program's 5 that way would be the guess this check exists to prevent.
    assert not selects_no_test("grep -qF 'the sentence' docs/MODEL.md", 5)
    assert not selects_no_test("python3 tools/doc_check.py check", 5)


def test_pytest_reached_through_a_runner_is_still_recognised() -> None:
    # The three shapes the store actually records.
    assert selects_no_test("pytest -k gate", 5)
    assert selects_no_test("uv run pytest subprojects/docket/tests/test_release.py -k gate", 5)
    assert selects_no_test("python -m pytest -k gate", 5)


def test_a_path_containing_pytest_is_not_mistaken_for_the_runner() -> None:
    assert not selects_no_test("uv run python tools/test_pytest_helpers.py", 5)


def test_a_passing_command_is_never_read_as_selecting_nothing() -> None:
    assert not selects_no_test("uv run pytest -k test_a", 0)


def test_an_open_item_whose_command_selects_no_test_is_named(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    report = already_passing(root, [_item(verify=_pytest("no_such_test_name"))])
    assert report.known
    assert report.vacuous == ("PL-K7QX",)
    assert report.passing == ()
    assert report.considered == 1


def test_an_item_whose_command_genuinely_fails_is_not_named(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    report = already_passing(root, [_item(verify="false")])
    assert report.vacuous == ()


def test_the_two_findings_are_separated_within_one_run(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    items = [
        _item(identifier="PL-PASS", verify="true"),
        _item(identifier="PL-NONE", verify=_pytest("no_such_test_name")),
        _item(identifier="PL-FAIL", verify="false"),
    ]
    report = already_passing(root, items)
    assert report.passing == ("PL-PASS",)
    assert report.vacuous == ("PL-NONE",)
    assert report.considered == 3


def test_a_verify_report_says_a_command_selected_no_test_rather_than_failed(tmp_path: Path) -> None:
    # The moment the defect bites hardest: a delegated branch is being
    # reviewed, its command is non-zero, and "the work is missing" and "the
    # command cannot tell you" look identical without this line.
    root = _repo(tmp_path)
    _work(
        root,
        "PL-K7QX add a test",
        "tests/test_thing.py",
        KEPT + "\n\ndef test_b() -> None:\n    assert 2 == 2\n",
    )
    report = verify(root, _item(verify=_pytest("no_such_test_name")), _config(), "HEAD~1")
    assert not report.passed
    command = next(c for c in report.checks if "`verify:` command" in c.name)
    assert not command.passed
    assert any("selects no test" in line for line in command.lines)


def test_a_verify_report_of_a_real_failure_makes_no_such_claim(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    _work(
        root,
        "PL-K7QX add a test",
        "tests/test_thing.py",
        KEPT + "\n\ndef test_c() -> None:\n    assert 3 == 3\n",
    )
    report = verify(root, _item(verify="false"), _config(), "HEAD~1")
    command = next(c for c in report.checks if "`verify:` command" in c.name)
    assert not command.passed
    assert not any("selects no test" in line for line in command.lines)
