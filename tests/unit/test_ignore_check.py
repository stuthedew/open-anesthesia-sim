"""`tools/ignore_check.py` must never call a live suppression inert.

The check exists because nothing evaluates `warn_unused_ignores` over the two
test trees `[tool.mypy] files` excludes. Its whole value is the verdict, and a
wrong verdict is worse than no check at all: the natural response to "this
directive suppresses nothing" is to delete it, so a false accusation removes a
real suppression and leaves the reader believing a checker looked.

So the cases here are mostly about the answers that must *not* read as clean -
an unresolved import, a crash, mypy missing entirely. `report` is pure for that
reason, and takes what mypy said rather than running it.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import ignore_check

REPO_ROOT = Path(__file__).resolve().parents[2]

CLEAN = ""
INERT = (
    'subprojects/docket/tests/test_model.py:39: error: Unused "type: ignore" comment  '
    "[unused-ignore]\n"
)
UNRESOLVED = (
    "subprojects/docket/tests/test_model.py:9: error: Cannot find implementation or library "
    'stub for module named "docket.model"  [import-not-found]\n'
)
NOISE = (
    'tests/unit/test_simulation_view.py:292: error: Argument "page" to "SimulationView" has '
    'incompatible type "_FakePage"; expected "Page"  [arg-type]\n'
)


def test_a_clean_run_reports_the_number_evaluated() -> None:
    code, printed = ignore_check.report(["a.py:1", "b.py:2"], 0, CLEAN, "")

    assert code == 0
    assert printed == "type: ignore directives: 2 evaluated, 0 inert"


def test_the_errors_the_gate_excludes_are_not_findings_here() -> None:
    """The 54 errors this run reports are the reason the gate excludes them."""
    code, printed = ignore_check.report(["a.py:1"], 1, NOISE, "")

    assert code == 0
    assert printed == "type: ignore directives: 1 evaluated, 0 inert"


def test_an_inert_directive_fails_and_is_named() -> None:
    code, printed = ignore_check.report(["a.py:1"], 1, NOISE + INERT, "")

    assert code == 1
    assert "1 evaluated, 1 inert" in printed
    assert "test_model.py:39" in printed
    assert ignore_check.accuses(printed)


def test_an_unresolved_import_is_not_checked_rather_than_clean() -> None:
    """The failure that would report all six live splat directives as unused.

    An unresolved module degrades every name it provides to `Any`, so the lines
    using them raise nothing and their directives look inert. Reporting that
    run as clean would be wrong in the one direction that matters.
    """
    code, printed = ignore_check.report(["a.py:1"], 1, UNRESOLVED, "")

    assert code == 1
    assert "not checked" in printed
    assert "unresolved import" in printed
    assert not ignore_check.accuses(printed)


def test_an_unresolved_import_outranks_an_inert_finding() -> None:
    """With imports broken, the inert finding is exactly what cannot be trusted."""
    code, printed = ignore_check.report(["a.py:1"], 1, UNRESOLVED + INERT, "")

    assert code == 1
    assert "not checked" in printed
    assert "inert" not in printed


def test_mypy_crashing_is_not_checked_rather_than_clean() -> None:
    code, printed = ignore_check.report(["a.py:1"], 2, "", "usage: mypy [-h]\n")

    assert code == 1
    assert "not checked" in printed
    assert "mypy exited 2" in printed


def test_mypy_missing_entirely_is_not_checked_rather_than_clean() -> None:
    """Exit 1 with nothing on stdout is `python -m mypy` with no mypy."""
    code, printed = ignore_check.report(["a.py:1"], 1, "", "No module named mypy\n")

    assert code == 1
    assert "not checked" in printed
    assert "No module named mypy" in printed


def test_directives_finds_the_real_ones_in_this_repository() -> None:
    """Against the live tree, because what it must not count lives there.

    `verify.py` holds the marker in a tuple, `test_release.py` names it in
    prose, and `test_verify.py` writes one into a fixture file as a string
    literal. Only the last is inside a checked tree, and it is the one a grep
    over these directories would wrongly count.
    """
    found = ignore_check.directives(REPO_ROOT)

    assert found, "the repository still carries directives; this found none"
    assert all(":" in site for site in found)
    # Located rather than hardcoded. This pinned the line by its leading digit,
    # which matches every line sharing it: the fixture sat at 19x, and the
    # assertion began matching the real directive at line 100 the moment the
    # file grew by one line. What it means to say is "the occurrence written
    # inside a string literal is not counted", so it says that instead - the
    # literal is the only one carrying an escaped newline.
    fixture = Path(REPO_ROOT) / "subprojects/docket/tests/test_verify.py"
    in_a_literal = [
        number
        for number, line in enumerate(fixture.read_text().splitlines(), 1)
        if "type: ignore" in line and "\\n" in line
    ]
    assert len(in_a_literal) == 1, "the fixture no longer writes a directive as a string"
    assert f"subprojects/docket/tests/test_verify.py:{in_a_literal[0]}" not in found
    grepped = subprocess.run(
        ("grep", "-rn", "type: *ignore", "--include=*.py", *ignore_check.TREES),
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert len(grepped.stdout.splitlines()) > len(found), (
        "the string-literal occurrence is gone, so this no longer proves the "
        "tokenizer excludes anything a grep would count"
    )


def test_a_comment_directive_is_counted_and_a_string_is_not(tmp_path: Path) -> None:
    tree = tmp_path / ignore_check.TREES[0]
    tree.mkdir(parents=True)
    (tree / "sample.py").write_text(
        'MARKER = "# type: ignore[misc]"\nx = 1  # type: ignore[assignment]\n', encoding="utf-8"
    )

    assert ignore_check.directives(tmp_path) == [f"{ignore_check.TREES[0]}/sample.py:2"]


def test_an_unparseable_file_is_left_to_mypy(tmp_path: Path) -> None:
    """Reporting a syntax error twice, in different words, helps nobody."""
    tree = tmp_path / ignore_check.TREES[0]
    tree.mkdir(parents=True)
    (tree / "broken.py").write_text("def (\n", encoding="utf-8")

    assert ignore_check.directives(tmp_path) == []
