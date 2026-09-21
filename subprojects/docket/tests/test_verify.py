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
from docket.model import Item, parse_item
from docket.store import insert_field, replace_field
from docket.verify import (
    LANDED_GUARD,
    SUPPRESSIONS,
    TIMED_OUT,
    VERIFY_GUARD,
    Check,
    Verification,
    already_passing,
    changed_paths,
    command_paths,
    item_commits,
    items_reading,
    landed_workers,
    reaches_outside_tree,
    sanctioned_queue_edit,
    selects_no_test,
    strip_non_code,
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


def _stored(identifier: str, title: str, **fields: str) -> str:
    """One item file as the store holds it: front matter, then the brief."""
    front = {"id": identifier, "title": title, "status": "ready", "verify": "true", **fields}
    return (
        "---\n" + "".join(f"{key}: {value}\n" for key, value in front.items()) + "---\n\n" + BRIEF
    )


def _repo(tmp_path: Path) -> Path:
    """A repository with one commit on it, rebuilt per test rather than shared.

    The five git processes this spawns look like the thing to make cheaper, and
    are not: four of them cost about 2 ms each, and the commit costs about 5 ms
    once `conftest.py` stops the developer's `~/.gitconfig` signing it - where
    it cost 73 ms while that config reached in. Copying a prebuilt tree per test
    instead would save single-digit milliseconds and trade an independent
    checkout for a shared one, which is the one thing these tests cannot give
    up: they are what keeps `docket` correct about refs, and a fixture leaking
    state between them would let a real defect through silently (`PL-YRYR`,
    measured 2026-09-21).
    """
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
    # The store the items below are read from in real use. Without it every
    # front-matter comparison would be against a file the base does not hold,
    # which is one case rather than the ordinary one.
    items = root / "docs" / "items"
    (items / "PL-K7QX-do-the-thing.md").write_text(_stored("PL-K7QX", "Do the thing"))
    (items / "PL-B2B2-do-the-other.md").write_text(_stored("PL-B2B2", "Do the other"))
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "base")
    return root


def _check(report: Verification, name: str) -> Check:
    """The one check by that name, so a test can assert on what it said."""
    return next(check for check in report.checks if check.name == name)


FRONT_MATTER = "item front matter unchanged"


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
    # Splatting `dict[str, object]` matches `object` against every field's type; the
    # alternatives are `dict[str, Any]` or an `Unpack[TypedDict]` restating all of
    # `Item`'s fields, both wider than this line-scoped ignore.
    return Item(**base)  # type: ignore[arg-type]


def _config(**overrides: object) -> Config:
    settings: dict[str, object] = dict(
        protected_paths=("src",), gate_paths=("Makefile",), check_command="true"
    )
    settings.update(overrides)
    # Splatting `dict[str, object]` matches `object` against every field's type; the
    # alternatives are `dict[str, Any]` or an `Unpack[TypedDict]` restating all of
    # `Config`'s fields, both wider than this line-scoped ignore.
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


def test_a_nested_docket_verify_refuses_to_run_the_command_again(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The level below the first reports the re-entry instead of recursing.

    `already_passing` can decline its question and stay useful. This one
    cannot: the command is what is being asked about, so the honest answer is
    that it was not run and the item is therefore not verified.
    """
    root = _repo(tmp_path)
    _work(
        root,
        "PL-K7QX add a test",
        "tests/test_thing.py",
        KEPT + "\ndef test_b() -> None:\n    assert 1\n",
    )
    monkeypatch.setenv(VERIFY_GUARD, "1")

    report = verify(root, _item(verify="bin/docket verify PL-K7QX"), _config(), "HEAD~1")

    assert not report.passed
    command = [c for c in report.checks if c.name == "`verify:` command passes"]
    assert command and not command[0].passed
    assert any("re-enters `docket verify`" in line for line in command[0].lines)


def test_the_command_is_told_it_is_running_underneath_docket_verify(tmp_path: Path) -> None:
    """The marker the check above reads is set on the child, not merely expected."""
    root = _repo(tmp_path)
    _work(
        root,
        "PL-K7QX add a test",
        "tests/test_thing.py",
        KEPT + "\ndef test_b() -> None:\n    assert 1\n",
    )
    probe = f'test -n "${VERIFY_GUARD}"'
    assert verify(root, _item(verify=probe), _config(), "HEAD~1").passed


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
        KEPT + "\n\n@pytest.mark.xfail\ndef test_b() -> None:\n    assert 2 == 2\n",
    )
    report = verify(root, _item(), _config(), "HEAD~1")
    assert not report.passed
    assert any("suppression" in c.name and not c.passed for c in report.checks)


def test_a_pytest_option_containing_a_suppression_name_is_not_one(tmp_path: Path) -> None:
    """Each entry in `SUPPRESSIONS` names a token, and a substring search finds one
    inside a longer word: `xfail` sits in pytest's own `--maxfail`. A line listing
    that option was reported as a suppression, which rejects correct work and trains
    a reader to skim the block where a real one is printed (`PL-VHVJ`, `PL-69JZ`).
    """
    root = _repo(tmp_path)
    _work(
        root,
        "PL-K7QX read the option",
        "tests/test_thing.py",
        KEPT + '\n\nVALUE_OPTIONS = {"--maxfail", "--durations"}\n',
    )
    report = verify(root, _item(), _config(), "HEAD~1")

    assert _check(report, "no suppression added").passed


def test_a_suppression_is_still_found_after_a_word_character(tmp_path: Path) -> None:
    """The anchor is left-only and must not cost the check a real finding: a
    decorated `@pytest.mark.xfail` has a word character before the name too."""
    root = _repo(tmp_path)
    _work(
        root,
        "PL-K7QX silence it",
        "tests/test_thing.py",
        KEPT + "\n\n@pytest.mark.xfail\ndef test_b() -> None:\n    assert 2 == 2\n",
    )
    report = verify(root, _item(), _config(), "HEAD~1")

    assert not _check(report, "no suppression added").passed


def test_suppression_ignores_prose(tmp_path: Path) -> None:
    """A release cut re-adds whole prose rows, and the check read them as code.

    `ROADMAP.md`'s version table narrates the defects each release fixed, so its
    rows quote the very tokens `SUPPRESSIONS` holds. Dropping the `current
    baseline` mark from the departing row changes one cell, and a whole-line
    diff cannot see that: the entire row re-enters the diff as an addition. So
    every release cut ended `REJECT` on the one check `--self` may never relax,
    which is the refusal-on-correct-work that trains a reader to skim the block
    a real weakening is also printed in (`PL-5MFL`, `PL-69JZ`).
    """
    root = _repo(tmp_path)
    _work(
        root,
        "PL-K7QX cut the release",
        "ROADMAP.md",
        "| Version | State |\n"
        "| --- | --- |\n"
        "| v0.4.29 | Completed | stopped the suppression list matching `xfail`"
        " out of pytest's `--maxfail` |\n",
    )
    report = verify(root, _item(touches=("ROADMAP.md",)), _config(), "HEAD~1")

    assert _check(report, "no suppression added").passed


def test_a_roadmap_line_naming_xfail_is_not_a_suppression(tmp_path: Path) -> None:
    """The narrowing must not cost the check its finding, so both halves are pinned.

    Prose naming a suppression is not one; the same token in a file Python runs
    still is. They are one commit apart in one report because the pair is the
    whole claim - a narrowing that also stopped reporting the second line would
    satisfy the first assertion and gut the check (`PL-BHBZ`).
    """
    root = _repo(tmp_path)
    _work(root, "PL-K7QX write it down", "docs/releases/v0.4.29.md", "Removed the `xfail`.\n")
    _work(
        root,
        "PL-K7QX silence it",
        "tests/test_thing.py",
        KEPT + "\n\n@pytest.mark.xfail\ndef test_b() -> None:\n    assert 2 == 2\n",
    )
    report = verify(root, _item(), _config(), "HEAD~2")

    suppression = _check(report, "no suppression added")
    assert not suppression.passed
    assert suppression.detail == "1 line(s)"
    assert suppression.lines == ("@pytest.mark.xfail",)


def test_a_pytest_configuration_key_is_still_a_suppression(tmp_path: Path) -> None:
    """The suffix list is wider than the sibling assertion check's, deliberately.

    An assertion is a statement, so only a file Python executes holds one. A
    suppression is the wider claim, because it is also *configured*:
    `xfail_strict = false` in `pyproject.toml` turns every expected failure back
    into a pass without a line of Python changing. Narrowing to `.py` alone
    would have carried the sibling's rule past the reasoning that earned it.
    """
    root = _repo(tmp_path)
    _work(
        root,
        "PL-K7QX loosen it",
        "pyproject.toml",
        "[tool.pytest.ini_options]\nxfail_strict = false\n",
    )
    report = verify(root, _item(touches=("pyproject.toml",)), _config(), "HEAD~1")

    assert not _check(report, "no suppression added").passed


def test_a_type_ignore_is_not_a_suppression(tmp_path: Path) -> None:
    """The one marker that ever fired, dropped because mypy answers it better.

    Replayed over `main`'s 1,004 non-merge commits, `# type: ignore` is the
    only entry of `SUPPRESSIONS` that has ever matched a real directive - 56 of
    them, every one carrying an explicit error code, and not one a disabled
    test, which is what this check exists to catch. Whether an ignore is load-bearing is a
    mypy question, and mypy is asked it everywhere: `strict = true` runs
    `warn_unused_ignores` over `[tool.mypy] files`, and `tools/ignore_check.py`
    runs the same setting over the two test trees that list excludes
    (`PL-G21K`, `PL-J5NN`).
    """
    root = _repo(tmp_path)
    _work(
        root,
        "PL-K7QX narrow the argument",
        "tests/test_thing.py",
        KEPT + '\n\nVALUE: int = _get("x")  # type: ignore[arg-type]\n',
    )
    report = verify(root, _item(), _config(), "HEAD~1")

    assert _check(report, "no suppression added").passed


def test_a_suppression_named_in_an_item_brief_is_not_one(tmp_path: Path) -> None:
    """The case that fires on every close-out, because every close-out edits one.

    `PL-VHVJ`'s branch was refused for thirteen lines, seven of them its own
    item's brief - and an item whose subject *is* the suppression detector
    cannot have a brief that does not name suppressions, so this is structural
    for every future item on this check rather than an unlucky wording
    (`PL-STC4`). A `.md` file suppresses nothing whatever it says, which is
    what `SUPPRESSION_BEARING_SUFFIXES` settles; this pins the shape the
    suffix rule exists for, beside the `ROADMAP.md` row above that pins the
    release cut.
    """
    root = _repo(tmp_path)
    _work(
        root,
        "PL-K7QX file the finding",
        "docs/items/PL-N3WQ-the-check-reads-prose.md",
        "**Problem.** The matcher reads `xfail` in prose, and `@pytest.mark.xfail`\n"
        "in a fixture string, as directives it is not.\n",
    )
    report = verify(root, _item(touches=("docs/items",)), _config(), "HEAD~1")

    assert _check(report, "no suppression added").passed


def test_a_docstring_naming_a_suppression_is_not_one(tmp_path: Path) -> None:
    """Prose inside a file Python executes is the half no suffix list reaches.

    A module that documents the tokens it matches trips its own check, so the
    close-out that added the suffix narrowing `REJECT`ed on six of its own
    docstring lines and could not be cleared from inside its branch
    (`PL-0KQP`, `PL-STC4`). The line is the hard case rather than a convenient
    one: a diff hands over a single line of a multi-line docstring, so the
    quotes that opened the span are on another line and the markup is the only
    evidence left that this is prose.
    """
    root = _repo(tmp_path)
    _work(
        root,
        "PL-K7QX document the guard",
        "tests/test_thing.py",
        KEPT
        + '\n\ndef helper() -> None:\n    """Run the guard.\n\n'
        + "    Never `pytest.skip` or `@skipif` here: the guard has to run on\n"
        + '    every platform, which is the whole point of it.\n    """\n',
    )
    report = verify(root, _item(), _config(), "HEAD~1")

    assert _check(report, "no suppression added").passed


def test_a_comment_naming_a_suppression_is_not_one(tmp_path: Path) -> None:
    """A comment explaining why a suppression was *not* used refused the branch.

    `PL-STC4` recorded this half as undecidable, and while `# type: ignore` was
    on the list it was: a rule that ignores comments deletes the only marker
    that ever fired. Dropping that marker is what makes the rule decidable,
    which is why the two halves of `PL-G21K` landed together rather than one at
    a time (`PL-4FD2`).
    """
    root = _repo(tmp_path)
    _work(
        root,
        "PL-K7QX explain the choice",
        "tests/test_thing.py",
        KEPT + "\n\nVALUE = 1  # not pytest.skip: the guard runs everywhere\n",
    )
    report = verify(root, _item(), _config(), "HEAD~1")

    assert _check(report, "no suppression added").passed


def test_a_suppression_inside_a_string_literal_is_not_one(tmp_path: Path) -> None:
    """The subject under test is not the thing itself.

    A test for this detector writes a suppression into a fixture file as a
    string, and a string suppresses nothing - it is data the suite reads. One
    of the thirteen lines `PL-VHVJ`'s own branch was refused for was exactly
    this, and it is the shape every future item on this check will carry
    (`PL-STC4`).
    """
    root = _repo(tmp_path)
    _work(
        root,
        "PL-K7QX test the detector",
        "tests/test_thing.py",
        KEPT + '\n\nFIXTURE = "@pytest.mark.xfail\\ndef test_c(): ...\\n"\n',
    )
    report = verify(root, _item(), _config(), "HEAD~1")

    assert _check(report, "no suppression added").passed


def test_a_suppression_beside_a_string_is_still_found(tmp_path: Path) -> None:
    """The strip is one line away from gutting the check, so the pair is pinned.

    A real marker holds its arguments in strings and can carry a trailing
    comment, which is every span the strip removes, on the line that is exactly
    what the check exists to report.

    `@pytest.mark.xfail` rather than `@pytest.mark.skipif` because the second
    is not a form this check detects at all - `@skip` wants its `@` against the
    name and `pytest.skip` wants its halves adjacent, and `.mark.` separates
    both. That is `PL-5B88`, found while writing this test and left to it: a
    widening is not what `PL-G21K` was ratified for.
    """
    root = _repo(tmp_path)
    _work(
        root,
        "PL-K7QX silence it while the fix lands",
        "tests/test_thing.py",
        KEPT
        + '\n\n@pytest.mark.xfail(reason="flaky", strict=False)  # for now\n'
        + "def test_b() -> None:\n    assert 2 == 2\n",
    )
    report = verify(root, _item(), _config(), "HEAD~1")

    suppression = _check(report, "no suppression added")
    assert not suppression.passed
    assert any("xfail" in line for line in suppression.lines)


def test_strip_non_code_leaves_an_unterminated_span_whole() -> None:
    """Where the strip cannot tell, the line stays on the page.

    A diff supplies one line of a wrapped statement, so the quote that closes a
    span is often on another line. Consuming to the end of the line instead
    would read everything after a stray quote as text, which is the direction
    that loses a finding; leaving it whole is the direction that reports one.
    """
    assert "xfail" in strip_non_code('MESSAGE = "an @pytest.mark.xfail marker')
    assert "xfail" not in strip_non_code('MESSAGE = "an @pytest.mark.xfail marker"')


def test_no_suppression_marker_is_comment_shaped() -> None:
    """`is_suppression_line` blanks comments, so a comment-form marker is dead.

    The two are coupled and the failure is silent: `SUPPRESSIONS` would name
    the marker, the diff would hold the directive, and the report would say
    `none`. Putting `# type: ignore` back, or adding `# mypy: ignore-errors`,
    needs `NON_CODE_RE`'s comment alternative reconsidered in the same edit,
    and this is what says so (`PL-G21K`).
    """
    assert [marker for marker in SUPPRESSIONS if marker.lstrip().startswith("#")] == []


def test_a_removed_assertion_is_rejected(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    _work(root, "PL-K7QX drop it", "tests/test_thing.py", "def test_a() -> None:\n    pass\n")
    report = verify(root, _item(), _config(), "HEAD~1")
    assert not report.passed
    assert any("assertion" in c.name and not c.passed for c in report.checks)


def test_a_suppression_added_and_then_removed_is_not_reported(tmp_path: Path) -> None:
    """A branch is judged on its net change, not on the sum of its patches.

    `git show` over the item's commits concatenates one patch per commit, so a
    suppression a worker added while iterating and deleted before pushing used
    to appear in the added lines of the first patch and be reported - with the
    cancelling commit nowhere in the output, so the worker could not argue with
    it (`PL-VP40`).
    """
    root = _repo(tmp_path)
    _work(
        root,
        "PL-K7QX silence it while iterating",
        "tests/test_thing.py",
        KEPT + "\n\n@pytest.mark.xfail\ndef test_b() -> None:\n    assert 2 == 2\n",
    )
    _work(
        root,
        "PL-K7QX take the marker back out",
        "tests/test_thing.py",
        KEPT + "\n\ndef test_b() -> None:\n    assert 2 == 2\n",
    )

    report = verify(root, _item(), _config(), "HEAD~2")

    suppression = _check(report, "no suppression added")
    assert suppression.passed
    assert suppression.detail == "none"


def test_an_assertion_removed_and_then_restored_is_not_reported(tmp_path: Path) -> None:
    """The other half of `PL-VP40`: a cut assertion that the branch puts back."""
    root = _repo(tmp_path)
    _work(root, "PL-K7QX drop it", "tests/test_thing.py", "def test_a() -> None:\n    pass\n")
    _work(root, "PL-K7QX put it back", "tests/test_thing.py", KEPT)

    report = verify(root, _item(), _config(), "HEAD~2")

    assertion = _check(report, "no existing assertion removed")
    assert assertion.passed
    assert assertion.detail == "none"


def test_a_suppression_re_added_after_removal_is_still_reported(tmp_path: Path) -> None:
    """The fold counts; it does not de-duplicate.

    This is the direction that would matter if it broke. Cancelling by set
    membership rather than by count would let a suppression deleted once and
    added twice pass, which is a real suppression reaching `HEAD` with the check
    reporting none - the opposite of the over-reporting `PL-VP40` fixed, and the
    dangerous one.
    """
    root = _repo(tmp_path)
    silenced = KEPT + "\n\n@pytest.mark.xfail\ndef test_b() -> None:\n    assert 2 == 2\n"
    _work(root, "PL-K7QX silence it", "tests/test_thing.py", silenced)
    _work(root, "PL-K7QX take it out", "tests/test_thing.py", KEPT)
    _work(root, "PL-K7QX put it back after all", "tests/test_thing.py", silenced)

    report = verify(root, _item(), _config(), "HEAD~3")

    suppression = _check(report, "no suppression added")
    assert not suppression.passed
    assert suppression.detail == "1 line(s)"
    assert any("@pytest.mark.xfail" in line for line in suppression.lines)


def test_the_scope_detail_claims_no_commit_when_the_branch_has_none(tmp_path: Path) -> None:
    """The check that reports the scope may not invent a commit to report it in.

    `len(commits) or 1` printed "1 commit(s)" for a branch carrying none, which
    is false at the one moment a session most needs a truthful answer about what
    it has committed - the container is ephemeral, so "have I committed this?"
    is the last question before a session ends (`PL-NB4D`).
    """
    root = _repo(tmp_path)
    (root / "tests" / "test_thing.py").write_text(
        KEPT + "\n\ndef test_b() -> None:\n    assert 2 == 2\n"
    )

    report = verify(root, _item(), _config(), "HEAD")

    scope = _check(report, "diff stayed inside `touches`")
    assert scope.passed
    assert scope.detail == "1 path(s), no commit naming PL-K7QX, all declared"
    # Named separately from the equality above so the `or 1` cannot come back
    # under a reworded detail line.
    assert "commit(s)" not in scope.detail


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
        root,
        "PL-K7QX note",
        "docs/items/PL-K7QX-do-the-thing.md",
        _stored("PL-K7QX", "Do the thing") + "\n**Worked.** Added the test.\n",
    )
    assert verify(root, _item(), _config(), "HEAD~1").passed


@pytest.mark.parametrize(
    ("field", "value"),
    [("status", "done"), ("touches", "src/core.py"), ("verify", "pytest -k something_else")],
)
def test_a_branch_that_edits_its_own_front_matter_is_refused(
    tmp_path: Path, field: str, value: str
) -> None:
    """Marking the work done, re-scoping it, or rewriting what measures it.

    All three are the reviewer's, and all three read as `PASS  item front
    matter unchanged` for as long as the guard looked the item file up by a
    path no ref holds (`PL-20PT`).
    """
    root = _repo(tmp_path)
    _work(
        root,
        "PL-K7QX add a test",
        "tests/test_thing.py",
        KEPT + "\ndef test_b() -> None:\n    assert 2 == 2\n",
    )
    _work(
        root,
        "PL-K7QX report on it",
        "docs/items/PL-K7QX-do-the-thing.md",
        _stored("PL-K7QX", "Do the thing", **{field: value}),
    )

    report = verify(root, _item(), _config(), "HEAD~2")

    assert not report.passed
    assert _check(report, FRONT_MATTER).detail == field


def test_an_item_file_the_base_does_not_hold_is_accepted_as_a_new_one(tmp_path: Path) -> None:
    """An item captured on the branch that works it has no earlier commission."""
    root = _repo(tmp_path)
    _work(
        root,
        "PL-N3W1 capture it",
        "docs/items/PL-N3W1-a-new-one.md",
        _stored("PL-N3W1", "A new one"),
    )
    _work(
        root,
        "PL-N3W1 add a test",
        "tests/test_thing.py",
        KEPT + "\ndef test_b() -> None:\n    assert 2 == 2\n",
    )

    report = verify(
        root, _item(identifier="PL-N3W1", path="PL-N3W1-a-new-one.md"), _config(), "HEAD~2"
    )

    assert report.passed
    assert "new item file" in _check(report, FRONT_MATTER).detail


def test_a_title_edit_that_renames_the_file_is_still_compared_by_id(tmp_path: Path) -> None:
    """The rename is `store.write_item`'s, and the title is front matter.

    Looked up by its current name, the renamed file has no copy at the base and
    reads as a new item - so the one edit that moves an item file would be the
    one edit the guard cannot see.
    """
    root = _repo(tmp_path)
    _work(
        root,
        "PL-K7QX add a test",
        "tests/test_thing.py",
        KEPT + "\ndef test_b() -> None:\n    assert 2 == 2\n",
    )
    (root / "docs" / "items" / "PL-K7QX-do-the-thing.md").unlink()
    _work(
        root,
        "PL-K7QX retitle it",
        "docs/items/PL-K7QX-do-something-else.md",
        _stored("PL-K7QX", "Do something else"),
    )

    report = verify(root, _item(path="PL-K7QX-do-something-else.md"), _config(), "HEAD~2")

    assert not report.passed
    assert _check(report, FRONT_MATTER).detail == "title"


def test_an_item_file_that_resolves_to_nothing_is_refused_rather_than_passed(
    tmp_path: Path,
) -> None:
    """A path that cannot be read is a check that did not run, not one that passed."""
    root = _repo(tmp_path)
    _work(
        root,
        "PL-K7QX add a test",
        "tests/test_thing.py",
        KEPT + "\ndef test_b() -> None:\n    assert 2 == 2\n",
    )

    report = verify(root, _item(path="PL-K7QX-under-a-name-nothing-holds.md"), _config(), "HEAD~1")

    assert not report.passed
    assert "no item file to read" in _check(report, FRONT_MATTER).detail


def test_a_base_holding_no_store_at_all_is_refused_rather_than_read_as_new(tmp_path: Path) -> None:
    """Every item on the branch would read as new, which is a misconfiguration.

    `vcs.stranded` declines the mirror case for the same reason: an answer that
    comes out identical for every item is the configuration reporting itself.
    """
    root = _repo(tmp_path)
    _work(
        root,
        "PL-K7QX add a test",
        "tests/test_thing.py",
        KEPT + "\ndef test_b() -> None:\n    assert 2 == 2\n",
    )
    _work(
        root,
        "PL-K7QX move the store",
        "docs/queue/PL-K7QX-do-the-thing.md",
        _stored("PL-K7QX", "Do the thing"),
    )

    report = verify(root, _item(), _config(items_dir="docs/queue"), "HEAD~2")

    assert not report.passed
    assert "no item store at HEAD~2:docs/queue" in _check(report, FRONT_MATTER).detail


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
    """Clear the re-entry guards this suite may have inherited.

    `docket check` sets `DOCKET_SKIP_LANDED` for every command it runs, and
    `docket verify` sets `DOCKET_IN_VERIFY` for the item command it runs. One
    of those commands is the pytest invocation recorded as this file's own
    `verify:`, twice over. Without this, the cases below read the declined
    report meant for a nested run and the item's command fails under the tool
    that runs it while passing when run by hand - which is exactly the
    environment-dependent result the check itself exists to make visible. The
    one case that wants the verify guard sets it itself, after this.
    """
    monkeypatch.delenv(LANDED_GUARD, raising=False)
    monkeypatch.delenv(VERIFY_GUARD, raising=False)


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


# A command that could not answer, and the two ways that happens. The failure
# both share is the one this module is otherwise built to refuse: a status that
# means "could not look" read as "looked, and it failed correctly". A killed
# command returned 1 - what a failing test returns - so it fell out of every
# finding while the report stayed clean (`PL-T940`).


def test_the_killed_status_cannot_be_confused_with_one_a_process_returned() -> None:
    # The whole fix rests on the status being unreachable by a real command: a
    # shell reports an exit status in 0-255 and a signal death as a small
    # negative number, and 1 in particular is what a failing test returns, so a
    # timeout sharing it is indistinguishable from an assertion that did not
    # hold.
    assert not -255 <= TIMED_OUT <= 255


def test_a_timed_out_command_is_not_checked(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    items = [_item(identifier="PL-K7QX", verify="sleep 5"), _item(identifier="PL-A1B2")]
    report = already_passing(root, items, timeout=0.2, workers=2)

    assert report.timed_out == ("PL-K7QX",)
    assert report.passing == ("PL-A1B2",)
    assert report.vacuous == ()


def test_a_timed_out_command_is_not_counted_as_one_that_ran(tmp_path: Path) -> None:
    # `considered` is rendered to a reader as "checked". A command killed
    # part-way through was not, and counting it overstates what the run saw.
    root = _repo(tmp_path)
    items = [_item(identifier="PL-K7QX", verify="sleep 5"), _item(identifier="PL-A1B2")]

    assert already_passing(root, items, timeout=0.2, workers=2).considered == 1


def test_a_command_that_genuinely_fails_is_not_called_timed_out(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    report = already_passing(root, [_item(verify="false")])

    assert report.timed_out == ()
    assert report.considered == 1


def test_one_missing_command_beside_a_real_one_is_named_not_silently_dropped(
    tmp_path: Path,
) -> None:
    # The same subtraction as a timeout, for the other way a command answers
    # nothing: leaving it out of `considered` without saying so would replace
    # one silent gap with a quieter one.
    root = _repo(tmp_path)
    items = [
        _item(identifier="PL-K7QX", verify="docket-no-such-command-xyz"),
        _item(identifier="PL-A1B2", verify="true"),
    ]
    report = already_passing(root, items)

    assert report.unavailable == ("PL-K7QX",)
    assert report.considered == 1


def test_a_run_where_every_command_was_killed_declines(tmp_path: Path) -> None:
    # The counterpart of the missing-toolchain decline: finding none passing
    # would be a fact about the machine, not about the store.
    root = _repo(tmp_path)
    items = [
        _item(identifier="PL-K7QX", verify="sleep 5"),
        _item(identifier="PL-A1B2", verify="sleep 5"),
    ]
    report = already_passing(root, items, timeout=0.2, workers=2)

    assert not report.known
    assert "killed at the 0.2s limit" in report.declined


def test_the_limit_the_results_were_produced_under_is_carried(tmp_path: Path) -> None:
    # So a report names the number a reader would have to change, rather than
    # the module-level default the run may not have used.
    root = _repo(tmp_path)

    assert already_passing(root, [_item()], timeout=7.5).limit == 7.5


# What a command cost, not only what it returned. An outlier test lived here -
# a command 30x the pool's median was named as the one the check waited for -
# and it was retired 2026-09-19 once measurement showed it firing on nothing
# (`PL-G6J5`). What is left reports rather than judges, so what these pin is
# that each number is the one the run actually paid.


def test_the_run_carries_what_it_would_have_cost_serially(tmp_path: Path) -> None:
    # The pool holds the wall clock roughly flat as the queue grows, so the
    # number a session feels is the one that hides the growth. The serial total
    # is what the store actually asks for, and it climbs with every item
    # triaged to `ready` (`PL-9NKK`).
    root = _repo(tmp_path)
    # Four commands of 0.5 s rather than 1 s. What is under test is that the
    # total is summed while the wall clock is not, and the ratio carrying it is
    # four-to-one either way: eight workers run these at once, so `elapsed`
    # stays near one command's duration whatever that duration is (`PL-VJ7W`).
    items = [_item(identifier=f"PL-000{n}", verify="sleep 0.5") for n in range(4)]
    report = already_passing(root, items, workers=8)

    assert report.serial >= 2
    # `> 0` as well as the comparison: a pool that reported no wall clock at
    # all would satisfy `0 < serial` and print `0.0s` from the cost line. This
    # was pinned by a test that also covered the retired median (`PL-G6J5`).
    assert report.elapsed > 0
    assert report.elapsed < report.serial


def test_the_costliest_command_is_carried_on_a_pool_with_no_outlier(tmp_path: Path) -> None:
    # The property the retirement rests on. "Did an outlier arrive" is answered
    # no by a store of comparable commands, and by this project's real store
    # too; "how close is any one command to the limit" always has an answer and
    # is the margin `LANDED_TIMEOUT` is chosen against, so it is the one
    # carried (`PL-G6J5`).
    root = _repo(tmp_path)
    items = [_item(identifier=f"PL-000{n}") for n in range(6)]
    report = already_passing(root, items, workers=8)

    assert report.slowest is not None


def test_the_costliest_command_is_the_one_that_actually_cost_the_most(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    items = [_item(identifier=f"PL-000{n}") for n in range(4)]
    # 0.3 s, not 1: `slowest` is a maximum and is held to no threshold, so this
    # only has to beat four commands that take milliseconds - which it does by
    # about sixty times (`PL-VJ7W`).
    items.append(_item(identifier="PL-SLOW", verify="sleep 0.3"))
    report = already_passing(root, items, workers=8)

    assert report.slowest is not None
    assert report.slowest.identifier == "PL-SLOW"


def test_a_killed_command_does_not_count_into_the_serial_total(tmp_path: Path) -> None:
    # It was stopped at the limit rather than having cost its duration, so
    # counting it would report a total the run never paid - and this one is
    # read against the limit itself.
    root = _repo(tmp_path)
    items = [_item(identifier=f"PL-000{n}") for n in range(4)]
    items.append(_item(identifier="PL-KILL", verify="sleep 30"))
    report = already_passing(root, items, timeout=0.3, workers=8)

    assert report.timed_out == ("PL-KILL",)
    assert report.serial < 1
    assert report.slowest is not None
    assert report.slowest.identifier != "PL-KILL"


def test_the_run_says_how_wide_the_pool_that_produced_it_was(tmp_path: Path) -> None:
    # `serial` cannot be read without it: what the remaining commands cost is
    # their total divided across the workers, and a report carrying the total
    # but not the divisor can only guess (`PL-FRGP`).
    root = _repo(tmp_path)
    report = already_passing(root, [_item(identifier=f"PL-000{n}") for n in range(4)], workers=3)

    assert report.workers == 3


def test_a_run_that_chose_its_own_width_still_reports_it(tmp_path: Path) -> None:
    # The caller usually passes nothing and `landed_workers()` decides, which
    # is exactly the case a reader of the advisory is in.
    root = _repo(tmp_path)
    report = already_passing(root, [_item(identifier=f"PL-000{n}") for n in range(4)])

    assert report.workers == landed_workers()


def test_a_store_with_no_command_to_run_names_no_costliest_one(tmp_path: Path) -> None:
    # An empty run must not render as a measured one, which is what a zero here
    # would become by the time it reached a headline.
    report = already_passing(_repo(tmp_path), [])

    assert report.slowest is None
    assert report.serial == 0.0


# --- running them at once -----------------------------------------------------
#
# `make check` pays this, and the bill grows with the queue: every item triaged
# to `ready` adds its command's runtime permanently, so the serial cost rose as
# the store got healthier (`PL-LXR3`). Concurrency is the one remedy that
# changes no answer, and these three pin the properties that make that true -
# the commands really do overlap, the findings still come back in the store's
# order rather than in whichever order the shells happened to finish, and no
# two of them write coverage data to the same file.


def test_verify_commands_run_concurrently(tmp_path: Path) -> None:
    # Each command marks the shared log when it starts and again when it ends,
    # so serial execution can only ever write `sese...` and any overlap at all
    # puts two starts together. Asserting the property beats asserting a
    # duration: a wall-clock threshold fails on a loaded machine for a reason
    # that has nothing to do with the code.
    root = _repo(tmp_path)
    log = root / "overlap.log"
    items = [
        _item(identifier=f"PL-RUN{n}", verify=f"printf s >> {log}; sleep 0.3; printf e >> {log}")
        for n in range(4)
    ]

    already_passing(root, items, workers=4)

    assert "ss" in log.read_text(), f"the commands ran one after another: {log.read_text()}"


def test_the_findings_follow_the_store_order_not_the_order_the_commands_finished(
    tmp_path: Path,
) -> None:
    # The findings are reported as lists of ids. Collected as each shell
    # returned, a slow command would sink to the bottom and the same unchanged
    # store would print a different advisory run to run.
    root = _repo(tmp_path)
    items = [
        _item(identifier="PL-SLOW", verify="sleep 0.3"),
        _item(identifier="PL-FAST", verify="true"),
    ]

    report = already_passing(root, items, workers=4)

    assert report.passing == ("PL-SLOW", "PL-FAST")


def test_no_two_commands_share_a_coverage_data_file(tmp_path: Path) -> None:
    # Coverage reads its data file back to decide `--cov-fail-under`, so two
    # `--cov` commands sharing one would race and a command could fail on data
    # a sibling truncated - a wrong answer created by running them at once. The
    # store carries eight such commands today, none on an open item, so this
    # guards the case rather than reports it.
    root = _repo(tmp_path)
    seen = root / "coverage-paths"
    record = f'printf "%s\n" "$COVERAGE_FILE" >> {seen}'
    items = [_item(identifier="PL-COV1", verify=record), _item(identifier="PL-COV2", verify=record)]

    already_passing(root, items, workers=4)

    paths = [line for line in seen.read_text().splitlines() if line]
    assert len(paths) == 2
    assert len(set(paths)) == 2, f"both commands wrote coverage to {paths[0]}"
    assert all(Path(path).parent != root for path in paths), "a probe wrote into the tree"


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


# Scoping the replay to what a branch changed (`PL-SDHR`). The sweep answers a
# question about the store, which a pull request cannot have changed - the same
# argument `PL-P3B6` used to take it off `make check` - while costing 87 s of
# the quality job's 152 s and growing with the queue rather than the change.


def test_a_scoped_run_checks_only_the_items_it_was_given(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    items = [_item(identifier="PL-K7QX", verify="true"), _item(identifier="PL-A1B2", verify="true")]
    report = already_passing(root, items, scoped_to={"PL-K7QX"})

    assert report.passing == ("PL-K7QX",)
    assert report.considered == 1


def test_a_scoped_run_says_what_it_was_narrowed_to(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    report = already_passing(
        root, [_item(identifier="PL-K7QX")], scoped_to={"PL-K7QX"}, scope_base="origin/main"
    )

    assert report.scope == "1 item(s) this branch changed against origin/main"


def test_a_scope_that_holds_nothing_to_run_still_carries_the_scope(tmp_path: Path) -> None:
    # The path that would otherwise lie. A branch changing only closed items
    # runs no command, and an empty report with no scope on it is
    # indistinguishable from a store that holds no command at all - the exact
    # confusion `declined` exists to prevent one level up.
    root = _repo(tmp_path)
    report = already_passing(
        root, [_item(identifier="PL-K7QX")], scoped_to={"PL-NONE"}, scope_base="origin/main"
    )

    assert report.passing == ()
    assert report.considered == 0
    assert report.scope == "1 item(s) this branch changed against origin/main"


def test_an_unscoped_run_carries_no_scope(tmp_path: Path) -> None:
    root = _repo(tmp_path)

    assert already_passing(root, [_item()]).scope == ""


def test_an_empty_scope_is_not_the_same_as_no_scope(tmp_path: Path) -> None:
    # A branch that changed no item at all is still a scoped run, and saying
    # "0 item(s)" is the answer. `scoped_to=None` is what means "sweep".
    root = _repo(tmp_path)
    report = already_passing(root, [_item()], scoped_to=set(), scope_base="origin/main")

    assert report.scope == "0 item(s) this branch changed against origin/main"
    assert report.considered == 0


def test_a_declined_run_still_reports_what_it_would_have_covered(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # A nested run declines before running anything, and the scope is built
    # first so the decline can still say what was asked of it.
    root = _repo(tmp_path)
    monkeypatch.setenv(LANDED_GUARD, "1")
    report = already_passing(
        root, [_item(identifier="PL-K7QX")], scoped_to={"PL-K7QX"}, scope_base="origin/main"
    )

    assert not report.known
    assert report.scope == "1 item(s) this branch changed against origin/main"


# Widening that scope to the items a branch *invalidates*, not only the ones it
# edited (`PL-XMNC`). Read from the item files alone, the replay ran a command
# on the pull request that *wrote* it and never on the one that broke it - and
# all six recorded breaks were the second case, a branch editing a file some
# other item's command reads, each reported only by the whole-store sweep once
# it was already on `main`.


def test_a_branch_editing_a_file_a_verify_command_reads_is_in_scope() -> None:
    # `PL-L9FC`'s own shape: its command greps `README.md`, and `#512` made it
    # pass by writing that file without ever opening the item.
    item = _item(
        identifier="PL-L9FC", verify="python3 tools/doc_check.py check && grep -q x README.md"
    )

    assert items_reading([item], ["README.md"]) == {"PL-L9FC"}


def test_the_gate_a_command_runs_is_not_a_file_it_reads() -> None:
    """The half that keeps the widening affordable.

    `tools/doc_check.py` is named by 54 of the 168 open commands and is the
    health half of every one of them, so counting the program a clause runs
    would put the whole of that set behind any edit to the gate - while the
    thing each of them actually discriminates on sits in another clause.
    """
    item = _item(verify="python3 tools/doc_check.py check && grep -q x README.md")

    assert items_reading([item], ["tools/doc_check.py"]) == frozenset()
    assert items_reading([item], ["bin/docket"]) == frozenset()


def test_a_test_file_handed_to_pytest_is_a_file_it_reads() -> None:
    # Not the same case as the one above, though both name a path in the first
    # clause: `pytest` is the program and the file is its input, so editing the
    # file can change what the command returns.
    item = _item(verify="uv run pytest tests/unit/test_x.py && grep -q def tests/unit/test_x.py")

    assert items_reading([item], ["tests/unit/test_x.py"]) == {"PL-K7QX"}


def test_a_directory_a_command_greps_covers_a_file_added_under_it() -> None:
    # `PL-X9T3`'s shape, and the reason containment is the rule rather than
    # equality: the branch that broke it added a file the recursive grep then
    # found.
    item = _item(verify="bin/docket check && ! grep -rq phrase docs/items/")

    assert items_reading([item], ["docs/items/PL-A1B2-a-new-capture.md"]) == {"PL-K7QX"}


def test_a_file_the_branch_is_creating_is_matched_before_it_exists() -> None:
    # `PL-XH1D`'s shape, and the reason this reader asks the filesystem
    # nothing: `#487` broke it by *creating* `CONTRIBUTING.md`, which existed
    # nowhere in the tree the command was written against.
    item = _item(verify="test -f CONTRIBUTING.md")

    assert items_reading([item], ["CONTRIBUTING.md"]) == {"PL-K7QX"}


def test_a_bare_word_is_not_read_as_a_directory() -> None:
    # A candidate carrying no `/` has to match a changed path exactly. Offered
    # containment, a word inside a pattern would put the command behind every
    # edit under a directory that happens to share its name.
    item = _item(verify="grep -q src README.md")

    assert items_reading([item], ["src/core.py"]) == frozenset()
    assert items_reading([item], ["README.md"]) == {"PL-K7QX"}


def test_a_path_inside_an_inline_script_is_read() -> None:
    # Quoted spans are scanned for paths as well, which over-reports where the
    # command is matching text rather than opening a file. That costs a replay;
    # the other direction costs the finding.
    inline = "python3 -c \"import json; json.load(open('src/a.json'))\""
    item = _item(verify=inline)

    assert items_reading([item], ["src/a.json"]) == {"PL-K7QX"}


def test_a_separator_inside_a_quoted_pattern_does_not_split_a_clause() -> None:
    # Clauses are cut on the blanked command, so a `&&` inside a pattern cannot
    # start a phantom clause whose first word - the real file - would then read
    # as the program it runs.
    assert command_paths("grep -q 'a && b' docs/MODEL.md") >= {"docs/MODEL.md"}


def test_a_closed_item_is_not_put_back_in_scope_by_its_command() -> None:
    # A closed `verify:` records what was run on a tree that no longer exists.
    # Replaying it would report a break in work that is finished.
    item = _item(status="done", verify="grep -q x README.md")

    assert items_reading([item], ["README.md"]) == frozenset()


def test_an_item_with_no_command_is_in_no_scope_at_all() -> None:
    assert items_reading([_item(verify="")], ["README.md"]) == frozenset()


def test_a_widened_scope_says_which_half_each_id_came_from(tmp_path: Path) -> None:
    # The cost line is the only place a reader learns why a command ran, and
    # the two halves want different reactions: an item this branch edited is
    # probably finished, while one it merely invalidated is a command that has
    # stopped discriminating.
    root = _repo(tmp_path)
    report = already_passing(
        root,
        [_item(identifier="PL-K7QX"), _item(identifier="PL-A1B2")],
        scoped_to={"PL-K7QX", "PL-A1B2"},
        reading={"PL-A1B2"},
        scope_base="origin/main",
    )

    assert report.scope == (
        "2 item(s) in scope: 1 this branch changed and 1 whose `verify:` command "
        "reads a file it changed against origin/main"
    )


# A blocked item's command, asked about only where a branch touched the item
# (`PL-RC0M`). `PL-N092`'s command passed for a day on a tree where none of its
# work had been done, because the file its `grep` negated had been deleted and
# `grep` on a missing file exits 2 - and nothing looked, because the item was
# blocked. The pull request that unblocked it is the one that went red.


def test_a_blocked_item_is_left_out_of_the_whole_store_sweep(tmp_path: Path) -> None:
    # The cost half of the answer. The replay is this check's largest expense
    # and the sweep is where it is paid, so widening it permanently to ask
    # about work nobody can start is the repair that was rejected.
    root = _repo(tmp_path)
    report = already_passing(root, [_item(status="blocked", verify="true")])

    assert report.passing == ()
    assert report.blocked == ()
    assert report.considered == 0


def test_a_blocked_item_the_branch_changed_is_asked_about(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    report = already_passing(root, [_item(status="blocked", verify="true")], scoped_to={"PL-K7QX"})

    assert report.passing == ("PL-K7QX",)
    assert report.blocked == ("PL-K7QX",)
    assert report.considered == 1


def test_a_blocked_item_outside_the_scope_is_still_left_alone(tmp_path: Path) -> None:
    # Narrowing is what admits it, not the mere fact that the run is narrowed:
    # a scoped run still asks only about the items the branch touched.
    root = _repo(tmp_path)
    items = [
        _item(identifier="PL-K7QX", status="ready", verify="true"),
        _item(identifier="PL-A1B2", status="blocked", verify="true"),
    ]
    report = already_passing(root, items, scoped_to={"PL-K7QX"})

    assert report.passing == ("PL-K7QX",)
    assert report.blocked == ()


def test_a_blocked_item_whose_command_still_fails_is_not_a_finding(tmp_path: Path) -> None:
    # The steady state. Asking is only worth its cost if a healthy command is
    # silent, and `blocked` is a subset of `passing` rather than of the pool.
    root = _repo(tmp_path)
    report = already_passing(root, [_item(status="blocked", verify="false")], scoped_to={"PL-K7QX"})

    assert report.passing == ()
    assert report.blocked == ()
    assert report.considered == 1


def test_blocked_is_always_a_subset_of_passing(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    items = [
        _item(identifier="PL-K7QX", status="ready", verify="true"),
        _item(identifier="PL-A1B2", status="blocked", verify="true"),
    ]
    report = already_passing(root, items, scoped_to={"PL-K7QX", "PL-A1B2"})

    assert set(report.blocked) <= set(report.passing)
    assert report.passing == ("PL-K7QX", "PL-A1B2")
    assert report.blocked == ("PL-A1B2",)


TOUCHES = "diff stayed inside `touches`"


def test_a_capture_committed_on_the_branch_is_not_outside_touches(tmp_path: Path) -> None:
    """`CLAUDE.md` asks for both of these, and the audit used to refuse the pair.

    `PL-66PR`: every commit subject must lead with the current item's id, and
    a finding not fixed in the session must be captured before the session
    ends. Doing both puts a new item file on a commit `item_commits`
    attributes to the item being verified, so the `touches` audit reported it
    as outside the commission and the branch came back `REJECT` for following
    the instructions.
    """
    root = _repo(tmp_path)
    _work(
        root, "PL-K7QX do the thing", "tests/test_thing.py", KEPT + "\ndef test_more():\n    pass\n"
    )
    _work(
        root,
        "PL-K7QX capture a finding found on the way past",
        "docs/items/PL-N3W1-something-noticed.md",
        _stored("PL-N3W1", "Something noticed", status="untriaged"),
    )
    report = verify(root, _item(), _config(), "HEAD~2")
    check = _check(report, TOUCHES)
    assert check.passed, check
    assert any("capture" in line for line in check.lines), check.lines


def test_a_pr_only_addition_to_another_items_file_is_not_outside_touches(tmp_path: Path) -> None:
    """What `bin/docket record` writes, riding the commit the close-out already makes.

    `PL-ZYQC`: the `docket` skill says to let the `pr:` write ride a commit
    already being made rather than composing one for it, and `verify` then read
    those writes as paths outside the commission. Two project mechanisms gave
    opposite answers about one commit, so a session could satisfy either and
    not both.
    """
    root = _repo(tmp_path)
    neighbour = root / "docs" / "items" / "PL-B2B2-do-the-other.md"
    neighbour.write_text(neighbour.read_text().replace("verify: true\n", "verify: true\npr: 495\n"))
    (root / "tests" / "test_thing.py").write_text(KEPT + "\ndef test_more():\n    pass\n")
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "PL-K7QX close it out, and record the pr the base was owed")
    report = verify(root, _item(), _config(), "HEAD~1")
    check = _check(report, TOUCHES)
    assert check.passed, check
    assert any("pr" in line for line in check.lines), check.lines


def test_record_on_non_canonical_key_order_classifies_as_pr(tmp_path: Path) -> None:
    """`PL-7K8Y`: the exemption above held only for a block a tool had written.

    `record` used to re-render the item it was adding `pr:` to, so on a file
    whose keys were hand-typed in some other order the write moved them as
    well - a removal plus an addition, which `sanctioned_queue_edit` reads as
    an ordinary content edit. The close-out that ran the command exactly as
    the skill instructs came back `REJECT` naming the item file, so the reader
    saw an out-of-commission edit and had to diff it to learn a tool wrote it.
    And because the classifier reads the per-commit diffs rather than the net
    tree, restoring the order in a later commit left both the removal and its
    undo on the branch: rebuilding the history was the only way to clear it.

    Goes through `insert_field`, which is what `cmd_record` calls, so this
    fails again if that call site is changed back to a writer that re-renders.
    """
    root = _repo(tmp_path)
    items = root / "docs" / "items"
    neighbour = items / "PL-B2B2-do-the-other.md"
    neighbour.write_text(
        "---\nid: PL-B2B2\ntitle: Do the other\nstatus: done\n"
        "verify: true\ntouches: src/core.py\nclosed: 2026-09-01\n---\n\n" + BRIEF
    )
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "base: a neighbour whose keys are not in canonical order")

    insert_field(items, parse_item(neighbour.read_text(), neighbour.name), "pr", "495")
    (root / "tests" / "test_thing.py").write_text(KEPT + "\ndef test_more():\n    pass\n")
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "PL-K7QX close it out, and record the pr the base was owed")

    path = "docs/items/PL-B2B2-do-the-other.md"
    assert sanctioned_queue_edit(root, "HEAD~1", ("HEAD",), path) == "pr"
    check = _check(verify(root, _item(), _config(), "HEAD~1"), TOUCHES)
    assert check.passed, check
    assert any("pr" in line for line in check.lines), check.lines


def test_a_recurrence_written_by_new_classifies_as_a_sanctioned_edit(tmp_path: Path) -> None:
    """A worker that captures a finding must not fail the audit for it.

    `CLAUDE.md` requires a finding not fixed in the session to be captured
    unconditionally, and `bin/docket new` now writes a `recurrences:` entry
    onto the item that capture matched - so a worker following the instruction
    edits an item nobody commissioned it to touch, exactly as `record`'s
    backfill does. That is the shape `PL-66PR` and `PL-ZYQC` each cost a round
    trip, arriving through a third door.
    """
    root = _repo(tmp_path)
    items = root / "docs" / "items"
    neighbour = items / "PL-B2B2-do-the-other.md"

    insert_field(
        items,
        parse_item(neighbour.read_text(), neighbour.name),
        "recurrences",
        "2026-09-20 PL-N3W1",
    )
    (root / "tests" / "test_thing.py").write_text(KEPT + "\ndef test_more():\n    pass\n")
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "PL-K7QX close it out, having captured a finding on the way")

    path = "docs/items/PL-B2B2-do-the-other.md"
    assert sanctioned_queue_edit(root, "HEAD~1", ("HEAD",), path) == "recurrence"


def test_a_second_recurrence_extending_the_line_is_sanctioned_and_a_rewrite_is_not(
    tmp_path: Path,
) -> None:
    """The growth case, which reads as a removal and so has to be matched exactly.

    Appending to a line removes that line and adds a longer one, and "removes
    nothing" is what makes the `pr` exemption safe to state exactly. So the
    append is recognised on its shape - both lines whole `recurrences:` values,
    the new one starting with the old - rather than by relaxing the removal
    rule, which would forgive an entry being altered or dropped under cover of
    one being added.
    """
    root = _repo(tmp_path)
    items = root / "docs" / "items"
    neighbour = items / "PL-B2B2-do-the-other.md"
    insert_field(
        items,
        parse_item(neighbour.read_text(), neighbour.name),
        "recurrences",
        "2026-09-19 PL-N3W1",
    )
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "base: a neighbour carrying one recurrence")
    path = "docs/items/PL-B2B2-do-the-other.md"

    insert_field(
        items,
        parse_item(neighbour.read_text(), neighbour.name),
        "recurrences",
        "2026-09-20 PL-N3W2",
        append=True,
    )
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "PL-K7QX a second capture matched to the same item")
    assert sanctioned_queue_edit(root, "HEAD~1", ("HEAD",), path) == "recurrence"

    # The same line rewritten rather than extended is an ordinary content edit,
    # which is the half this must not widen into.
    neighbour.write_text(
        neighbour.read_text().replace(
            "recurrences: 2026-09-19 PL-N3W1, 2026-09-20 PL-N3W2", "recurrences: 2026-09-21 PL-N3W3"
        )
    )
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "PL-K7QX replace what was recorded")
    assert sanctioned_queue_edit(root, "HEAD~1", ("HEAD",), path) == ""


def test_a_withdrawal_is_not_exempt_though_an_append_past_one_still_is(tmp_path: Path) -> None:
    """The two sides of the boundary the withdrawal grammar moved.

    Withdrawing the *last* recorded entry appends ` withdrawn DATE PL-XXXX` to
    it, so the new line starts with the old one exactly as a fresh capture
    does. Left there, the rule written for the edit that *adds* evidence would
    have exempted the one edit that cancels it - and a withdrawal is a
    deliberate act with something to gain, unlike the append `docket new` makes
    while following an unconditional capture rule. So it declares the file it
    touches like any other work (`PL-34BG`).

    The other side has to keep working, and it is why the grammar admits the
    withdrawn form at all: one withdrawal must not make every later capture
    matched to that item read as tampering.
    """
    root = _repo(tmp_path)
    items = root / "docs" / "items"
    neighbour = items / "PL-B2B2-do-the-other.md"
    insert_field(
        items,
        parse_item(neighbour.read_text(), neighbour.name),
        "recurrences",
        "2026-09-19 PL-N3W1",
    )
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "base: a neighbour carrying one recurrence")
    path = "docs/items/PL-B2B2-do-the-other.md"

    replace_field(
        items,
        parse_item(neighbour.read_text(), neighbour.name),
        "recurrences",
        "2026-09-19 PL-N3W1 withdrawn 2026-09-21 PL-K7QX",
    )
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "PL-K7QX withdraw a match that was wrong")
    assert sanctioned_queue_edit(root, "HEAD~1", ("HEAD",), path) == ""

    # And the append that follows one is still the capture's own write.
    insert_field(
        items,
        parse_item(neighbour.read_text(), neighbour.name),
        "recurrences",
        "2026-09-22 PL-N3W2",
        append=True,
    )
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "PL-K7QX a capture matched after the withdrawal")
    assert sanctioned_queue_edit(root, "HEAD~1", ("HEAD",), path) == "recurrence"


def test_an_ordinary_edit_to_another_items_file_is_still_outside_touches(tmp_path: Path) -> None:
    """The half the exemption must not widen into.

    Reading the diff rather than the path is what keeps these apart: a `pr:`
    addition is dictated by the merge history and a capture has no prior
    content to weaken, while re-scoping a neighbouring item's `touches` is
    exactly what the audit exists to catch.
    """
    root = _repo(tmp_path)
    neighbour = root / "docs" / "items" / "PL-B2B2-do-the-other.md"
    neighbour.write_text(neighbour.read_text().replace("status: ready\n", "status: done\n"))
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "PL-K7QX quietly close somebody else's item")
    report = verify(root, _item(), _config(), "HEAD~1")
    check = _check(report, TOUCHES)
    assert not check.passed, check
    assert any("PL-B2B2" in line for line in check.lines), check.lines


def test_a_new_item_file_that_is_not_a_capture_is_still_outside_touches(tmp_path: Path) -> None:
    """`status: untriaged` is the whole of what makes an added file a capture.

    A branch that adds a fully triaged item - one it could have written to say
    anything about scope or proof - is not doing what the capture rule asks
    for, and is not exempt.
    """
    root = _repo(tmp_path)
    _work(
        root,
        "PL-K7QX add a ready item nobody triaged",
        "docs/items/PL-N3W2-invented.md",
        _stored("PL-N3W2", "Invented", status="ready"),
    )
    report = verify(root, _item(), _config(), "HEAD~1")
    check = _check(report, TOUCHES)
    assert not check.passed, check


# --- the self-audit, which is a different question (PL-69JZ, PL-B5YN, PL-4LT9)


GATES = "the checks themselves are unedited"
ALONE = "the audited diff is this item's alone"


def test_a_self_audit_reports_a_declared_gate_path_instead_of_refusing(tmp_path: Path) -> None:
    """`PL-69JZ`: the audit refused every item whose declared work is a gate path.

    `feature: worker-instructions` holds 33 items and most of them edit a
    `.claude` file, which `gate_paths` covers - so for that whole feature a
    `REJECT` was the expected result of running the close-out audit, which
    trains a reader to skim the block where the protected-path line also sits.
    The defect had already been absorbed into policy rather than fixed:
    `bin/docket triage` tells a groomer such an item is non-delegable
    "because `docket verify` fails any diff that edits the checks".
    """
    root = _repo(tmp_path)
    _work(root, "PL-K7QX edit the gate", "Makefile", "check:\n\ttrue\n# changed\n")

    report = verify(root, _item(touches=("Makefile",)), _config(), "HEAD~1", self_audit=True)

    check = _check(report, GATES)
    assert not check.passed, "it still looked, and still says what it found"
    assert check.advisory and not check.blocks
    assert "Makefile" in check.detail
    assert report.passed, "a reported commission check does not refuse the work"


def test_a_delegated_review_still_refuses_a_gate_path(tmp_path: Path) -> None:
    """The half the fix must not widen: without `--self` nothing moved.

    A delegated worker that edits the thing measuring it has made the
    measurement meaningless, which is the case this guard was built for and
    the reason it is absolute there.
    """
    root = _repo(tmp_path)
    _work(root, "PL-K7QX edit the gate", "Makefile", "check:\n\ttrue\n# changed\n")

    report = verify(root, _item(touches=("Makefile",)), _config(), "HEAD~1")

    check = _check(report, GATES)
    assert check.blocks and not check.advisory
    assert not report.passed


def test_a_self_audit_reports_a_close_outs_own_front_matter_edit(tmp_path: Path) -> None:
    """`PL-B5YN`: closing an item edits exactly the fields the guard watches.

    The `docket` skill's close-out asks for `status: done` and `closed:` in
    the same commit as the work, so the guard fired by construction on the one
    path a session is told to take. It is right for a delegated worker, who is
    not the reviewer; the session running its own close-out is.
    """
    root = _repo(tmp_path)
    _work(
        root,
        "PL-K7QX add a test",
        "tests/test_thing.py",
        KEPT + "\ndef test_b() -> None:\n    assert 2 == 2\n",
    )
    _work(
        root,
        "PL-K7QX close it out",
        "docs/items/PL-K7QX-do-the-thing.md",
        _stored("PL-K7QX", "Do the thing", status="done"),
    )

    report = verify(root, _item(), _config(), "HEAD~2", self_audit=True)

    check = _check(report, FRONT_MATTER)
    assert not check.passed and check.advisory
    assert check.detail.startswith("status")
    assert report.passed


def test_a_self_audit_names_the_other_items_its_commits_carry(tmp_path: Path) -> None:
    """`PL-4LT9`: on a batch branch the per-item scoping does not happen.

    `item_commits` selects by id so a reviewer can take four items and reject
    the fifth, and `CLAUDE.md` then requires a commit closing several items to
    lead with all of them - so every subject names every id and the selection
    is the whole branch whichever id is asked about. Reported rather than
    repaired: which item commissioned which path is not recoverable from the
    diff, and naming the other ids is what lets a reader see that the scope
    being audited is wider than the item.
    """
    root = _repo(tmp_path)
    _work(
        root,
        "PL-K7QX, PL-B2B2 do both things",
        "tests/test_thing.py",
        KEPT + "\ndef test_b() -> None:\n    assert 2 == 2\n",
    )

    report = verify(root, _item(), _config(), "HEAD~1", self_audit=True)

    check = _check(report, ALONE)
    assert check.advisory and not check.blocks
    assert "PL-B2B2" in check.detail


def test_a_single_item_branch_says_nothing_about_other_items(tmp_path: Path) -> None:
    """Silent in the delegated case, which is the one the scoping was built for."""
    root = _repo(tmp_path)
    _work(
        root,
        "PL-K7QX do the one thing",
        "tests/test_thing.py",
        KEPT + "\ndef test_b() -> None:\n    assert 2 == 2\n",
    )

    report = verify(root, _item(), _config(), "HEAD~1", self_audit=True)

    assert not any(check.name == ALONE for check in report.checks)


def test_a_self_audit_still_refuses_a_removed_assertion(tmp_path: Path) -> None:
    """The line the whole design rests on.

    A session may re-scope its own commission; it may not weaken the thing
    that measures it. The integrity checks are untouched by `--self`.
    """
    root = _repo(tmp_path)
    _work(
        root, "PL-K7QX delete the test's teeth", "tests/test_thing.py", "def test_a():\n    pass\n"
    )

    report = verify(root, _item(), _config(), "HEAD~1", self_audit=True)

    check = _check(report, "no existing assertion removed")
    assert check.blocks and not check.advisory
    assert not report.passed


def test_a_self_audit_still_refuses_a_failing_command(tmp_path: Path) -> None:
    """The other integrity half: `--self` never skips the test."""
    root = _repo(tmp_path)
    _work(
        root,
        "PL-K7QX add a test",
        "tests/test_thing.py",
        KEPT + "\ndef test_b() -> None:\n    assert 2 == 2\n",
    )

    report = verify(root, _item(verify="false"), _config(), "HEAD~1", self_audit=True)

    assert not report.passed


# `PL-7TYC` - what counts as a *removed assertion*. The check asked
# `"assert" in line`, which is true of a comment, a docstring, a release note,
# an item's brief, a variable named `removed_assertions` and of the matcher
# itself - so a correct close-out touching any of them was refused by an
# integrity check that is supposed to be unarguable. Both directions are pinned
# below, and the second group is the one that matters: a tightening of this
# check fails silently, where the over-report at least announced itself.

PROSE = (
    "def test_a() -> None:\n"
    '    """The band asserts a spread no wider than the literature supports."""\n'
    "    # what these assert is the judgment, not the git reading behind it\n"
    "    assert 1 == 1\n"
)


def test_prose_that_merely_mentions_an_assertion_is_not_reported(tmp_path: Path) -> None:
    """A docstring and a comment carrying the word, reworded away.

    The assertion itself is untouched across both commits, so it folds out and
    what reaches the check is two lines of prose.
    """
    root = _repo(tmp_path)
    _work(root, "PL-K7QX write the prose", "tests/test_thing.py", PROSE)
    _work(root, "PL-K7QX reword it", "tests/test_thing.py", KEPT)

    check = _check(
        verify(root, _item(), _config(), "HEAD~1", self_audit=True), "no existing assertion removed"
    )
    assert check.passed
    assert check.detail == "none"


def test_the_matcher_itself_is_not_an_assertion(tmp_path: Path) -> None:
    """`PL-7TYC`'s own line, which is how the defect was found.

    `bin/docket verify --self PL-K82G` REJECTed the branch that gave this check
    its first passing route, for the line of code that does the looking.
    """
    root = _repo(tmp_path)
    matcher = (
        "def collect(removed: list[str]) -> list[str]:\n"
        '    dropped = [line.strip() for line in removed if "assert" in line]\n'
        "    return dropped\n"
    )
    _work(root, "PL-K7QX the old matcher", "tests/test_thing.py", matcher)
    _work(
        root,
        "PL-K7QX replace it",
        "tests/test_thing.py",
        "def collect(removed: list[str]) -> list[str]:\n    return []\n",
    )

    check = _check(
        verify(root, _item(), _config(), "HEAD~1", self_audit=True), "no existing assertion removed"
    )
    assert check.passed


def test_prose_removed_from_a_document_is_never_an_assertion(tmp_path: Path) -> None:
    """Only a file Python executes can hold one.

    The second line would be reported in a `.py` file - a reflow can start a
    sentence with the word - and is prose here whatever its shape. This is the
    larger half of the narrowing by count: every close-out edits its own item's
    `.md` and every release edits `ROADMAP.md`.
    """
    root = _repo(tmp_path)
    note = "The test asserts the band is drawn.\nassert-led wrap of a sentence.\n"
    _work(root, "PL-K7QX write the note", "docs/notes.md", note)
    _work(root, "PL-K7QX cut it", "docs/notes.md", "Gone.\n")

    check = _check(
        verify(root, _item(touches=("docs/notes.md",)), _config(), "HEAD~1", self_audit=True),
        "no existing assertion removed",
    )
    assert check.passed


def test_a_helper_definition_or_import_is_not_an_assertion(tmp_path: Path) -> None:
    """Removing `def assert_ok` removes its call sites too, and those are caught."""
    root = _repo(tmp_path)
    helper = (
        "from unittest import TestCase  # assertEqual lives here\n"
        "\n"
        "def assert_ok(value: int) -> None:\n"
        "    pass\n"
    )
    _work(root, "PL-K7QX add the helper", "tests/test_thing.py", helper)
    _work(root, "PL-K7QX drop the helper", "tests/test_thing.py", "PLACEHOLDER = 1\n")

    check = _check(
        verify(root, _item(), _config(), "HEAD~1", self_audit=True), "no existing assertion removed"
    )
    assert check.passed


@pytest.mark.parametrize(
    ("shape", "removed"),
    [
        ("bare", "    assert value == 1\n"),
        ("message", '    assert value == 1, "the readout moved"\n'),
        ("unittest", "    self.assertEqual(value, 1)\n"),
        ("mock", "    handler.assert_called_once_with(value)\n"),
        ("numpy", "    numpy.testing.assert_allclose(value, 1.0)\n"),
        ("one-liner", "    if flaky: assert value == 1\n"),
        ("wrapped", "    assert (\n        value == 1\n    )\n"),
    ],
)
def test_a_genuinely_removed_assertion_is_still_reported(
    tmp_path: Path, shape: str, removed: str
) -> None:
    """The direction that fails silently, so every shape the check ever caught is here.

    `wrapped` is the one the item asked to be checked rather than assumed:
    `assert` is a keyword and opens its statement, so a reflow across three
    lines still puts it on the first, which is the line the deletion shows.
    `one-liner` is the shape a naive `^\\s*assert` anchor would have given up.
    """
    root = _repo(tmp_path)
    body = "def test_b(value: int, flaky: bool, handler: object, numpy: object) -> None:\n"
    _work(root, f"PL-K7QX add the {shape} assertion", "tests/test_thing.py", KEPT + body + removed)
    _work(
        root,
        f"PL-K7QX cut the {shape} assertion",
        "tests/test_thing.py",
        KEPT + body + "    pass\n",
    )

    check = _check(
        verify(root, _item(), _config(), "HEAD~1", self_audit=True), "no existing assertion removed"
    )
    assert check.blocks and not check.advisory
    assert not check.passed


# `PL-QJQL` - the same question, widened. A context manager asserts by
# *expectation* and carries the word nowhere, so `with pytest.raises(...)`
# matched neither alternative above and a whole block could be deleted with the
# check reporting none removed. It is not a random blind spot: `pytest.raises`
# is how this project pins the guards that *reject* an input, so what was
# invisible was disproportionately the safety half. Both directions are pinned
# again here, because a widening and a narrowing are one claim about what an
# assertion is, and the second group is what stops the next narrowing
# overshooting into prose.

EXPECTATION_PROSE = (
    "def test_a() -> None:\n"
    '    """With a dose of 0 the guard raises (ValueError) before the run starts."""\n'
    "    with open(PATH) as handle:  # the loader raises(OSError) on a bad path\n"
    "        handle.read()\n"
    "    assert 1 == 1\n"
)


@pytest.mark.parametrize(
    ("shape", "removed"),
    [
        ("plain", "    with pytest.raises(ValueError):\n        build(-1.0)\n"),
        ("match", '    with pytest.raises(ValueError, match="dose"):\n        build(-1.0)\n'),
        ("bound", "    with pytest.raises(ValueError) as raised:\n        build(-1.0)\n"),
        ("warns", "    with pytest.warns(DeprecationWarning):\n        build(-1.0)\n"),
        ("imported", "    with raises(ValueError):\n        build(-1.0)\n"),
        ("wrapped", "    with pytest.raises(\n        ValueError,\n    ):\n        build(-1.0)\n"),
    ],
)
def test_a_removed_pytest_raises_block_is_an_assertion_removed(
    tmp_path: Path, shape: str, removed: str
) -> None:
    """Every shape this tree writes, plus the two it does not write yet.

    `imported` is `from pytest import raises`, which is why the alternative
    matches the bare name rather than requiring the `pytest.` prefix; `warns`
    is the same family and appears nowhere here yet. `wrapped` is the form
    `ruff format` produces for a long expectation, and it is the reason the
    anchor is on `with` rather than on the closing colon: the statement opens
    on the line the deletion shows and closes three lines later.
    """
    root = _repo(tmp_path)
    body = "def test_b(build: object) -> None:\n"
    _work(
        root, f"PL-K7QX add the {shape} expectation", "tests/test_thing.py", KEPT + body + removed
    )
    _work(
        root,
        f"PL-K7QX cut the {shape} expectation",
        "tests/test_thing.py",
        KEPT + body + "    pass\n",
    )

    check = _check(
        verify(root, _item(), _config(), "HEAD~1", self_audit=True), "no existing assertion removed"
    )
    assert check.blocks and not check.advisory
    assert not check.passed


def test_prose_and_comments_mentioning_raises_are_not_assertions(tmp_path: Path) -> None:
    """The direction the widening could have broken, and the two shapes that break it.

    `raises` and `warns` are ordinary English verbs, unlike `assert`, so the
    over-report `PL-7TYC` removed is one loosened character away. Line two is a
    docstring a reflow started with the word `With` and which names the error in
    parentheses - matched by an unanchored `(?:raises|warns)\\s*\\(` and not by
    the shipped one, because prose puts a space before a parenthesis where
    `ruff format` never does. Line three is a real `with` statement whose
    trailing comment mentions the word, which is what `[^#]*` holds off.

    The assertion itself is untouched across both commits, so it folds out and
    what reaches the check is those three lines alone.
    """
    root = _repo(tmp_path)
    _work(root, "PL-K7QX write the prose", "tests/test_thing.py", EXPECTATION_PROSE)
    _work(root, "PL-K7QX reword it", "tests/test_thing.py", KEPT)

    check = _check(
        verify(root, _item(), _config(), "HEAD~1", self_audit=True), "no existing assertion removed"
    )
    assert check.passed
    assert check.detail == "none"


# `PL-K1WS` - an assertion *edited in place*. A required parameter added to a
# function rewrites every call site that passes it inside an `assert`, and the
# exact fold in `_net_line_changes` sees each rewrite as a removal. `PL-MN4J`
# took eleven of these on a diff that removed no coverage at all. The refusing
# direction is the one that fails silently, so it carries the most cases below:
# the fold is licensed by the original's tokens surviving, and nothing else.

SIGNATURE = (
    "def test_hover() -> None:\n"
    "    assert format_trace_hover(run, ALVEOLAR, 0) == header\n"
    "    assert readout == format_trace_hover(run, ALVEOLAR, index)\n"
)


def test_an_assertion_rewritten_in_place_is_not_reported_as_removed(tmp_path: Path) -> None:
    """`PL-MN4J`'s own shape, both ways the new argument was written.

    The second line is the one a greedy alignment gives up: the replacement
    ends in two closing brackets, and spending the original's `)` on the inner
    one leaves the outer at depth 0 with nothing to match. Three of `PL-MN4J`'s
    eleven lines were that shape.
    """
    root = _repo(tmp_path)
    _work(root, "PL-K7QX the call sites", "tests/test_thing.py", KEPT + SIGNATURE)
    _work(
        root,
        "PL-K7QX name the run",
        "tests/test_thing.py",
        KEPT
        + (
            "def test_hover() -> None:\n"
            "    assert format_trace_hover(run, ALVEOLAR, 0, 1) == header\n"
            "    assert readout == format_trace_hover(run, ALVEOLAR, index, len(frame.runs))\n"
        ),
    )

    check = _check(
        verify(root, _item(), _config(), "HEAD~1", self_audit=True), "no existing assertion removed"
    )
    assert check.passed
    assert check.detail == "none, 2 replaced in place"


def test_a_replacement_is_printed_beside_the_line_it_replaced(tmp_path: Path) -> None:
    """The fold withdraws the refusal and nothing else.

    An inserted argument can still change what a line asserts, so the pair
    stays on the page for the reader who would catch that - which is the whole
    reason folding it is safe.
    """
    root = _repo(tmp_path)
    _work(root, "PL-K7QX the call site", "tests/test_thing.py", KEPT + SIGNATURE)
    _work(
        root,
        "PL-K7QX name the run",
        "tests/test_thing.py",
        KEPT
        + (
            "def test_hover() -> None:\n"
            "    assert format_trace_hover(run, ALVEOLAR, 0, 1) == header\n"
            "    assert readout == format_trace_hover(run, ALVEOLAR, index)\n"
        ),
    )

    check = _check(
        verify(root, _item(), _config(), "HEAD~1", self_audit=True), "no existing assertion removed"
    )
    assert check.passed
    assert "replaced, not counted: assert format_trace_hover(run, ALVEOLAR, 0) == header" in (
        check.lines
    )
    assert any(line.strip().startswith("by: assert format_trace_hover") for line in check.lines)


@pytest.mark.parametrize(
    ("shape", "replacement"),
    [
        ("a changed literal", "    assert reading == pytest.approx(1.05)\n"),
        ("a dropped argument", "    assert reading == pytest.approx(2.05, rel=R)\n"),
        ("a widened condition", "    assert reading == pytest.approx(2.05) or skipped\n"),
        ("a different subject", "    assert other == pytest.approx(2.05)\n"),
    ],
)
def test_a_rewrite_that_is_not_an_insertion_is_still_reported(
    tmp_path: Path, shape: str, replacement: str
) -> None:
    """The silent direction, so every way the fold could be talked into firing is here.

    `a changed literal` is the one that decides the design: `2.05` to `1.05`
    is what the wider normalisation `PL-K1WS` proposed - erase the argument
    lists, compare what is left - would have folded, and it is a weakened
    assertion. `a dropped argument` removes `rel=R` rather than adding it, and
    reversing the direction is not the same question. `a widened condition`
    appends outside every bracket. `a different subject` keeps the shape and
    changes what is being read.
    """
    root = _repo(tmp_path)
    body = "def test_reading() -> None:\n"
    original = "    assert reading == pytest.approx(2.05)\n"
    start, end = (
        (original, replacement) if shape != "a dropped argument" else (replacement, original)
    )
    _work(root, f"PL-K7QX assert {shape}", "tests/test_thing.py", KEPT + body + start)
    _work(root, f"PL-K7QX rewrite {shape}", "tests/test_thing.py", KEPT + body + end)

    check = _check(
        verify(root, _item(), _config(), "HEAD~1", self_audit=True), "no existing assertion removed"
    )
    assert check.blocks and not check.advisory
    assert check.detail == "1 line(s)"


def test_a_replacement_in_another_file_does_not_fold(tmp_path: Path) -> None:
    """Per file, never across - the rule the exact fold above it already holds to.

    An assertion cut from one file and a similar one added to another is two
    facts rather than a move, and the check has no way to know the second was
    meant as the first. The base holds the assertion, so that what is audited
    is a removal rather than a line this branch both added and cut - which the
    exact fold above would settle first.
    """
    root = _repo(tmp_path)
    body = "def test_reading() -> None:\n    assert probe(reading) == 2\n"
    _work(root, "PL-K7QX the assertion", "tests/test_thing.py", KEPT + body)
    _work(root, "PL-K7QX cut it", "tests/test_thing.py", KEPT)
    _work(
        root,
        "PL-K7QX a similar one elsewhere",
        "tests/test_other.py",
        "def test_reading() -> None:\n    assert probe(reading, scale) == 2\n",
    )

    check = _check(
        verify(
            root,
            _item(touches=("tests/test_thing.py", "tests/test_other.py")),
            _config(),
            "HEAD~2",
            self_audit=True,
        ),
        "no existing assertion removed",
    )
    assert check.blocks
    assert check.detail == "1 line(s)"


# A changed *string* is named and never folded (`PL-K4R5`). The original
# string is gone, so nothing in the diff separates the item's own commissioned
# rewrite from an expectation quietly dropped - and the candidates are usually
# several, so choosing one would print a guess as fact.

WAVE_OLD = (
    "def test_wave() -> None:\n"
    '    assert "1 this gate can clear, 1 waiting on work outside it" in printed\n'
)

WAVE_NEW = (
    "def test_wave() -> None:\n"
    '    assert "what they wait on: PL-ZZZZ" in printed\n'
    '    assert "blocked outside the gate: PL-001" in printed\n'
    '    assert "1 this gate can clear, 2 waiting on 2 open items outside it" in printed\n'
    '    assert "what they wait on: PL-AAAA" in printed\n'
)


def test_a_changed_string_names_its_candidates_and_still_counts(tmp_path: Path) -> None:
    """`PL-FCM3`'s own shape, which is why the report names rather than folds.

    Four added lines differ from the removed one by exactly one string, and
    only the third is its rewrite. A fold would have to pick, and picking the
    first - the shape a greedy pairing gives - records `what they wait on:
    PL-ZZZZ` as the replacement for a gate summary line. So the refusal
    stands, the count stays honest, and the candidates go on the page for the
    reader who can tell which is which.
    """
    root = _repo(tmp_path)
    _work(root, "PL-K7QX pin the gate line", "tests/test_thing.py", KEPT + WAVE_OLD)
    _work(root, "PL-K7QX name what they wait on", "tests/test_thing.py", KEPT + WAVE_NEW)

    check = _check(
        verify(root, _item(), _config(), "HEAD~1", self_audit=True), "no existing assertion removed"
    )
    assert check.blocks, "a changed string is still a removed assertion"
    assert check.detail == "1 line(s), 1 differing by one string"
    assert any(
        line.strip().startswith('one string differs, still counted: assert "1 this gate can clear')
        for line in check.lines
    )
    removed_line = 'assert "1 this gate can clear, 1 waiting on work outside it" in printed'
    assert sum(removed_line in line for line in check.lines) == 1, (
        "a line with candidates is printed under them rather than also in the plain list"
    )
    named = [line.strip() for line in check.lines if line.strip().startswith("candidate ")]
    assert [line.split(":")[0] for line in named] == [
        "candidate 1 of 4",
        "candidate 2 of 4",
        "candidate 3 of 4",
    ], "the count is every candidate; only the printing is capped"
    assert any(
        "`falsifies:` on the base's copy is what declares this shape" in line
        for line in check.lines
    )


def test_a_changed_number_is_not_named_as_a_changed_string(tmp_path: Path) -> None:
    """The narrowness, stated as a test rather than as a sentence.

    `approx(2.05)` to `approx(1.05)` keeps its subject and changes what is
    expected of it, which `PL-K1WS` already identified as a weakened
    assertion. It is the shape this report must not dress up as a commissioned
    rewrite, so it reaches the refusal with no candidate beside it.
    """
    root = _repo(tmp_path)
    _work(
        root,
        "PL-K7QX pin the reading",
        "tests/test_thing.py",
        KEPT + "\ndef test_r() -> None:\n    assert reading == pytest.approx(2.05)\n",
    )
    _work(
        root,
        "PL-K7QX move the reading",
        "tests/test_thing.py",
        KEPT + "\ndef test_r() -> None:\n    assert reading == pytest.approx(1.05)\n",
    )

    check = _check(
        verify(root, _item(), _config(), "HEAD~1", self_audit=True), "no existing assertion removed"
    )
    assert check.blocks
    assert check.detail == "1 line(s)"
    assert not [line for line in check.lines if "one string differs" in line]


def test_an_ordinary_deletion_carries_no_candidate_lines(tmp_path: Path) -> None:
    """An assertion that simply left the suite reads exactly as it did before.

    The report grows only where there is a candidate to name, so the branch
    this check exists to refuse is not buried under an explanation of a shape
    it does not have.
    """
    root = _repo(tmp_path)
    _work(
        root,
        "PL-K7QX pin it",
        "tests/test_thing.py",
        KEPT + "\ndef test_r() -> None:\n    assert reading == 2\n",
    )
    _work(root, "PL-K7QX drop it", "tests/test_thing.py", KEPT)

    check = _check(
        verify(root, _item(), _config(), "HEAD~1", self_audit=True), "no existing assertion removed"
    )
    assert check.blocks
    assert check.detail == "1 line(s)"
    assert not [line for line in check.lines if "candidate" in line or "one string" in line]


# `falsifies:` - the declared exemption to "no existing assertion removed"
# (`PL-K82G`). The check had no passing route for an item whose own work makes
# a rendered string false, so a correct close-out could only game the fold or
# push through a red integrity check.

FALSIFIES = "the roadmap gives that version"
PINNED = "def test_a() -> None:\n    assert 'the roadmap gives that version' in status()\n"


def _commission(root: Path, name: str, **fields: str) -> None:
    """Rewrite an item in the store and commit it, so the *base* is what declares."""
    (root / "docs" / "items" / name).write_text(_stored("PL-K7QX", "Do the thing", **fields))
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "commission PL-K7QX")


def test_an_assertion_the_commission_declared_falsified_is_folded(tmp_path: Path) -> None:
    """`PL-C6XD`'s own close-out: the string the assertion pins is what the item deletes.

    No arrangement of the tests keeps it, so folding it is the only route this
    check has to a verdict other than a `REJECT` that has to be argued past.
    """
    root = _repo(tmp_path)
    (root / "tests" / "test_thing.py").write_text(PINNED)
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "base: the assertion that pins the string")
    _commission(root, "PL-K7QX-do-the-thing.md", falsifies=FALSIFIES)
    _work(root, "PL-K7QX drop the duplicated refusal", "tests/test_thing.py", KEPT)

    report = verify(root, _item(falsifies=FALSIFIES), _config(), "HEAD~1")

    check = _check(report, "no existing assertion removed")
    assert check.passed
    assert check.detail == "none, 1 declared falsified"
    assert any("declared falsified, not counted" in line for line in check.lines)
    assert report.passed


def test_a_removal_the_declaration_does_not_name_is_still_refused(tmp_path: Path) -> None:
    """The fold is scoped to the declared subject, not opened by the field's presence."""
    root = _repo(tmp_path)
    (root / "tests" / "test_thing.py").write_text(PINNED + "\ndef test_b():\n    assert 2 == 2\n")
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "base: two assertions")
    _commission(root, "PL-K7QX-do-the-thing.md", falsifies=FALSIFIES)
    _work(root, "PL-K7QX drop both", "tests/test_thing.py", "def test_a():\n    pass\n")

    report = verify(root, _item(falsifies=FALSIFIES), _config(), "HEAD~1")

    check = _check(report, "no existing assertion removed")
    assert check.blocks
    assert check.detail == "1 line(s), 1 declared falsified"
    assert not report.passed


def test_a_declaration_the_branch_never_acted_on_is_reported(tmp_path: Path) -> None:
    """A commission describing work the branch did not do is a finding, not silence."""
    root = _repo(tmp_path)
    _commission(root, "PL-K7QX-do-the-thing.md", falsifies=FALSIFIES)
    _work(
        root,
        "PL-K7QX add a test",
        "tests/test_thing.py",
        KEPT + "\ndef test_b() -> None:\n    assert 2 == 2\n",
    )

    report = verify(root, _item(falsifies=FALSIFIES), _config(), "HEAD~1")

    note = _check(report, "the `falsifies:` declaration holds")
    assert note.advisory and not note.blocks
    assert "no assertion matching it was removed" in note.detail
    assert report.passed


def test_a_declaration_added_on_the_branch_folds_nothing(tmp_path: Path) -> None:
    """The line the field rests on, tested in the mode that would defeat it.

    `PL-K82G` argued the field was safe because `front_matter_check` refuses a
    branch that edits its own item's front matter. That is true of a delegated
    review and false of the self-audit the close-out runs, where the guard is
    an advisory by design. Reading the declaration from the base is what holds
    the property in both modes.
    """
    root = _repo(tmp_path)
    (root / "tests" / "test_thing.py").write_text(PINNED)
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "base: the assertion that pins the string")
    _work(root, "PL-K7QX delete it and say I meant to", "tests/test_thing.py", KEPT)

    report = verify(root, _item(falsifies=FALSIFIES), _config(), "HEAD~1", self_audit=True)

    check = _check(report, "no existing assertion removed")
    assert check.blocks and not check.advisory
    assert not report.passed
    note = _check(report, "the `falsifies:` declaration holds")
    assert "declared on this branch and not in" in note.detail


def test_an_unreadable_commission_says_so_rather_than_folding_nothing_silently(
    tmp_path: Path,
) -> None:
    """A partial read handed over as a complete one is the one thing the floor refuses."""
    root = _repo(tmp_path)
    _work(
        root, "PL-K7QX delete the test's teeth", "tests/test_thing.py", "def test_a():\n    pass\n"
    )

    report = verify(root, _item(falsifies=FALSIFIES), _config(items_dir="nowhere"), "HEAD~1")

    note = _check(report, "the `falsifies:` declaration holds")
    assert "no item store at" in note.detail
    assert not report.passed


# The one commission that cannot declare in advance (`PL-ZMGR`). A
# `needs-decision` item's answer is the session's to make, so which assertions
# it falsifies is not known until it is made - and `falsifies:` is read from
# the base precisely so that it predates the branch. `PL-G6J5`'s close-out
# retired an advisory on a count and printed `FAIL no existing assertion
# removed - 29 line(s)`, every line an assertion about the advisory the item
# had sanctioned retiring, with every other guard green.


def _close(root: Path, message: str, **fields: str) -> None:
    """Close PL-K7QX and delete the pinned assertion in one commit, as a close-out does."""
    (root / "docs" / "items" / "PL-K7QX-do-the-thing.md").write_text(
        _stored("PL-K7QX", "Do the thing", **fields)
    )
    _work(root, message, "tests/test_thing.py", KEPT)


def test_a_needs_decision_closure_may_declare_what_it_falsifies(tmp_path: Path) -> None:
    """The base left the answer to this session, so this session is who can name it.

    The gate is the base's `status`, which a branch can no more set than it can
    the field - so the fold is granted here and refused on the `ready` item
    below, from the same branch-side declaration.
    """
    root = _repo(tmp_path)
    (root / "tests" / "test_thing.py").write_text(PINNED)
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "base: the assertion that pins the string")
    _commission(root, "PL-K7QX-do-the-thing.md", status="needs-decision")
    _close(root, "PL-K7QX retire it - the count said retire", status="done", falsifies=FALSIFIES)

    report = verify(
        root, _item(falsifies=FALSIFIES, status="done"), _config(), "HEAD~1", self_audit=True
    )

    check = _check(report, "no existing assertion removed")
    assert check.passed
    assert check.detail == "none, 1 declared falsified by this closure"
    assert any("declared falsified, not counted" in line for line in check.lines)
    # Said on the page it is honoured on, rather than folded silently.
    assert any("this closure's own" in line for line in check.lines)
    assert report.passed


def test_a_ready_commission_is_still_the_only_word_on_what_it_falsifies(tmp_path: Path) -> None:
    """The same close-out, from a `ready` base: refused.

    This is the property relaxing the check for every self-audited branch would
    have given away. A delegated worker cannot reach the fold by closing the
    item, because `ready` is the commission saying the work was settled before
    the branch opened. `_repo`'s base already holds the item at `ready`, so
    there is no commission to rewrite here - which is the whole difference from
    the test above.
    """
    root = _repo(tmp_path)
    (root / "tests" / "test_thing.py").write_text(PINNED)
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "base: the assertion that pins the string")
    _close(root, "PL-K7QX delete it and close", status="done", falsifies=FALSIFIES)

    report = verify(
        root, _item(falsifies=FALSIFIES, status="done"), _config(), "HEAD~1", self_audit=True
    )

    check = _check(report, "no existing assertion removed")
    assert check.blocks and not check.advisory
    assert check.detail == "1 line(s)"
    assert (
        "declared on this branch and not in"
        in _check(report, "the `falsifies:` declaration holds").detail
    )
    assert not report.passed


def test_a_needs_decision_item_this_branch_leaves_open_declares_nothing(tmp_path: Path) -> None:
    """Still mid-decision, so the declaration is not yet an answer.

    The exemption is for the commit that records the decision, which is what
    makes the branch-side field a closure's word rather than a worker's.
    """
    root = _repo(tmp_path)
    (root / "tests" / "test_thing.py").write_text(PINNED)
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "base: the assertion that pins the string")
    _commission(root, "PL-K7QX-do-the-thing.md", status="needs-decision")
    _close(root, "PL-K7QX delete it while deciding", status="needs-decision", falsifies=FALSIFIES)

    report = verify(
        root,
        _item(falsifies=FALSIFIES, status="needs-decision"),
        _config(),
        "HEAD~1",
        self_audit=True,
    )

    check = _check(report, "no existing assertion removed")
    assert check.blocks and not check.advisory
    assert not report.passed


def test_an_item_captured_and_closed_on_one_branch_declares_nothing(tmp_path: Path) -> None:
    """The self-grant route the base read closes, tested where the base holds no copy.

    A session that writes its own `needs-decision` item and closes it in the
    same branch has written both halves of the gate. `commissioned_falsification`
    reports an empty status for an item the base does not hold, so the
    exemption is never reached.
    """
    root = _repo(tmp_path)
    (root / "tests" / "test_thing.py").write_text(PINNED)
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "base: the assertion that pins the string")
    (root / "docs" / "items" / "PL-N3WQ-decide-it.md").write_text(
        _stored("PL-N3WQ", "Decide it", status="done", falsifies=FALSIFIES)
    )
    _work(root, "PL-N3WQ file it, decide it, delete it", "tests/test_thing.py", KEPT)

    report = verify(
        root,
        _item(
            identifier="PL-N3WQ",
            title="Decide it",
            path="PL-N3WQ-decide-it.md",
            falsifies=FALSIFIES,
            status="done",
        ),
        _config(),
        "HEAD~1",
        self_audit=True,
    )

    check = _check(report, "no existing assertion removed")
    assert check.blocks and not check.advisory
    assert (
        "declared on this branch and not in"
        in _check(report, "the `falsifies:` declaration holds").detail
    )
    assert not report.passed


# The command check's two declared exemptions (`PL-L4KX`). `docket check`
# accepts both states and `verify` refused both, so the close-out the skill
# prescribes had no passing state at all.


def test_dropped_close_out_is_not_a_missing_command(tmp_path: Path) -> None:
    """A dropped item built nothing, so there is nothing for a command to prove."""
    root = _repo(tmp_path)
    _work(
        root,
        "PL-K7QX drop it",
        "tests/test_thing.py",
        KEPT + "\ndef test_b() -> None:\n    assert 2 == 2\n",
    )

    report = verify(root, _item(status="dropped", verify=""), _config(), "HEAD~1", self_audit=True)

    command = _check(report, "has a `verify:` command")
    assert command.advisory and not command.blocks
    assert "a dropped item built nothing" in command.detail
    # The half a hard stop was throwing away: the other checks actually ran.
    assert not report.stopped_early
    assert _check(report, "no existing assertion removed").passed
    assert _check(report, "the project's own checks pass").passed
    assert report.passed


def test_a_not_delegable_item_close_out_is_not_a_missing_command(tmp_path: Path) -> None:
    """`docket check` accepts a recorded reason *instead of* a command, in those words."""
    root = _repo(tmp_path)
    _work(
        root,
        "PL-K7QX do it by hand",
        "tests/test_thing.py",
        KEPT + "\ndef test_b() -> None:\n    assert 2 == 2\n",
    )

    report = verify(
        root,
        _item(verify="", not_delegable="proving it means cutting a release"),
        _config(),
        "HEAD~1",
        self_audit=True,
    )

    command = _check(report, "has a `verify:` command")
    assert command.advisory and not command.blocks
    assert "proving it means cutting a release" in command.detail
    assert not report.stopped_early
    assert report.passed


def test_a_done_item_with_no_command_and_no_reason_still_fails_hard(tmp_path: Path) -> None:
    """The exemption reads the store; it is not a way to skip the test.

    Neither state is free to reach for - a drop owes a `reason` and a `closed`
    date, and a `not-delegable` line is what withholds the item from delegation
    in the first place. An item carrying neither has genuinely skipped it.
    """
    root = _repo(tmp_path)
    _work(
        root,
        "PL-K7QX add a test",
        "tests/test_thing.py",
        KEPT + "\ndef test_b() -> None:\n    assert 2 == 2\n",
    )

    report = verify(root, _item(status="done", verify=""), _config(), "HEAD~1", self_audit=True)

    command = _check(report, "has a `verify:` command")
    assert command.blocks and not command.advisory
    assert report.stopped_early
    assert not report.passed


# `verify:` commands that read past the tree (`PL-205P`). The two recorded
# shapes are kept verbatim from the store, because the point of these is that
# they are what was actually written rather than what a test author would
# invent.
TAG_COMMAND = "git ls-remote --tags origin v0.4.30 | grep -q 'refs/tags/v0.4.30'"
REFS_COMMAND = "! git ls-remote --heads origin 'refs/heads/claude/x' | grep -q ."
GREPS_FOR_A_NETWORK_VERB = (
    "grep -q 'git push origin --delete' .claude/skills/docket/SKILL.md && "
    "grep -q 'say the remote is gone' docs/worker.md"
)


@pytest.mark.parametrize("command", [TAG_COMMAND, REFS_COMMAND, "curl -sS https://example.com"])
def test_a_command_that_asks_the_remote_reaches_outside_the_tree(command: str) -> None:
    assert reaches_outside_tree(command) is True


@pytest.mark.parametrize(
    "command",
    [
        # The trap. `PL-K2C8`'s real command carries `git push origin --delete`
        # as a *search string* and opens no socket, so a substring scan calls
        # it non-hermetic and silently downgrades a finding that must stay an
        # error. `shlex` collapses the quoted argument into one token.
        GREPS_FOR_A_NETWORK_VERB,
        "uv run pytest tests/unit/test_thing.py",
        # A network subcommand that is not the word after `git`.
        "git log --grep fetch",
        # Unparseable, which must read as hermetic: failing to parse is not a
        # licence to soften a finding.
        "grep -q 'unbalanced",
        "",
    ],
)
def test_a_command_that_only_reads_the_tree_does_not(command: str) -> None:
    assert reaches_outside_tree(command) is False


def test_a_passing_command_that_asks_the_remote_is_reported_apart(tmp_path: Path) -> None:
    """It stays in `passing` and is named in `external`, so `checks` can soften it.

    `PL-205P`: the command's answer is a fact about the world at the moment it
    ran, so it flips with no commit behind it - which is how `main` went red
    across six commits by five unrelated sessions for `PL-8GQW` while the
    repository had not changed.
    """
    root = _repo(tmp_path)
    items = [
        _item(identifier="PL-K7QX", status="ready", verify="true"),
        _item(identifier="PL-A1B2", status="ready", verify="git ls-remote --tags . HEAD"),
    ]
    report = already_passing(root, items)

    assert report.passing == ("PL-K7QX", "PL-A1B2")
    assert set(report.external) <= set(report.passing)
    assert report.external == ("PL-A1B2",)


def test_reaching_outside_the_tree_takes_precedence_over_blocked(tmp_path: Path) -> None:
    """`blocked`'s certainty does not survive a command the world can answer.

    A blocked item's passing command is reported as certainly
    non-discriminating, because work nobody can start cannot have landed. That
    rests on the tree being the only thing the command reads.
    """
    root = _repo(tmp_path)
    items = [_item(identifier="PL-A1B2", status="blocked", verify="git ls-remote --tags . HEAD")]
    report = already_passing(root, items, scoped_to={"PL-A1B2"})

    assert report.passing == ("PL-A1B2",)
    assert report.external == ("PL-A1B2",)
    assert report.blocked == ()
