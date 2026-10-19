"""`tools/new_prose.py` must print the long simulator prose a branch changed, and nothing else.

The close-out reviewer opens no file, so a unit this tool leaves out is never
reviewed and nothing says so. These tests pin which files count as the
simulator's, which units count as changed, the word threshold, and the line
that names a file the tool could not read.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from new_prose import MIN_WORDS, Unit, branch_prose, excerpt, main, prose_units

LONG = " ".join(["word"] * MIN_WORDS)
SHORT = " ".join(["word"] * (MIN_WORDS - 1))

SOURCE = f'''\
"""{LONG}"""

LIMIT = 3


def step(x):
    """{LONG}"""
    return x * LIMIT


def other(y):
    """{SHORT}"""
    # {LONG}
    return y
'''


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    ).stdout


def _write(root: Path, path: str, text: str) -> None:
    (root / path).parent.mkdir(parents=True, exist_ok=True)
    (root / path).write_text(text, encoding="utf-8")


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A repository with `SOURCE` committed on `main`, and a branch `work` checked out."""
    _git(tmp_path, "init", "-q", "-b", "main")
    for key, value in (("user.email", "t@example.com"), ("user.name", "T")):
        _git(tmp_path, "config", key, value)
    _write(tmp_path, "src/pkg/model.py", SOURCE)
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-qm", "seed")
    _git(tmp_path, "checkout", "-qb", "work")
    return tmp_path


def test_prose_units_reads_docstrings_and_joined_comment_runs() -> None:
    source = 'def f():\n    """One line."""\n    # first\n    # second\n    return 1  # after\n'

    found = prose_units("src/f.py", source)

    assert [(unit.kind, unit.first, unit.last, unit.text) for unit in found] == [
        ("docstring", 2, 2, "One line."),
        ("comment", 3, 4, "first\nsecond"),
        ("comment", 5, 5, "after"),
    ]


def test_only_a_long_unit_that_a_changed_row_falls_inside_is_printed(repo: Path) -> None:
    model = repo / "src/pkg/model.py"
    # A change to code beside a long docstring, a change inside a short one,
    # and a change inside a long comment.
    text = SOURCE.replace("x * LIMIT", "x * LIMIT * 2").replace(
        f'"""{SHORT}"""', f'"""{SHORT} more"""'
    )
    model.write_text(text.replace(f"# {LONG}", f"# {LONG} too"), encoding="utf-8")

    found = branch_prose(repo, "main")

    # The short docstring now has 30 words, so it is printed too.
    assert [(unit.kind, unit.first) for unit in found.units] == [("docstring", 12), ("comment", 13)]
    assert found.unread == []


def test_a_new_file_has_every_long_unit_printed(repo: Path) -> None:
    _write(repo, "src/pkg/fresh.py", SOURCE)

    found = branch_prose(repo, "main")

    assert [(unit.path, unit.first) for unit in found.units] == [
        ("src/pkg/fresh.py", 1),
        ("src/pkg/fresh.py", 7),
        ("src/pkg/fresh.py", 13),
    ]


def test_a_test_file_is_the_simulators_only_when_it_imports_the_product(repo: Path) -> None:
    _write(repo, "tests/unit/test_tool.py", "import json\n" + SOURCE)
    _write(repo, "tests/unit/test_sim.py", "import anesthesia_sim\n" + SOURCE)
    _write(repo, "tools/script.py", SOURCE)

    found = branch_prose(repo, "main")

    assert {unit.path for unit in found.units} == {"tests/unit/test_sim.py"}


def test_a_file_that_will_not_parse_is_named_and_not_read(repo: Path) -> None:
    _write(repo, "src/pkg/broken.py", "def f(:\n")

    found = branch_prose(repo, "main")

    assert found.units == []
    assert len(found.unread) == 1
    assert found.unread[0].startswith("src/pkg/broken.py: ")


def test_excerpt_marks_the_unit_and_the_code_around_it() -> None:
    lines = [f"line {row}" for row in range(1, 21)]

    shown = list(excerpt(lines, Unit("src/f.py", "comment", 10, 11, "")))

    assert shown[0] == "    6 | line 6"
    assert shown[4:6] == ["   10 > line 10", "   11 > line 11"]
    assert shown[-1] == "   15 | line 15"


def test_main_says_so_when_nothing_long_changed(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (repo / "src/pkg/model.py").write_text(SOURCE.replace("LIMIT = 3", "LIMIT = 4"), "utf-8")

    assert main(["--root", str(repo), "--base", "main"]) == 0
    assert capsys.readouterr().out.startswith("No docstring or comment of 30 words or more")


def test_main_numbers_each_unit_with_its_rows(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _write(repo, "src/pkg/fresh.py", SOURCE)

    assert main(["--root", str(repo), "--base", "main"]) == 0
    out = capsys.readouterr().out
    assert out.startswith("3 docstrings and comments of 30 words or more changed")
    assert f"[1] src/pkg/fresh.py, rows 1-1, docstring, {MIN_WORDS} words" in out
    assert "[3] src/pkg/fresh.py, rows 13-13, comment" in out


def _commit(repo: Path, message: str) -> str:
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "--allow-empty", "-m", message)
    return _git(repo, "rev-parse", "HEAD").strip()


def _count(repo: Path, capsys: pytest.CaptureFixture[str], *extra: str) -> tuple[int, str]:
    code = main(["--root", str(repo), "--base", "main", "--count", *extra])
    return code, capsys.readouterr().out.strip()


def test_counts_units_since_commit(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """`--count` counts committed long units, leaving out those already at a given commit.

    This is what `bin/docket arm` reads (`PL-W04Z`). A code fix after the
    review must not ask for a second review, and a new long unit must.
    """
    _write(repo, "src/pkg/fresh.py", SOURCE)
    _commit(repo, "add a file with three long units")
    assert _count(repo, capsys) == (0, "3")

    reviewed = _commit(repo, "record the review")
    (repo / "src/pkg/fresh.py").write_text(SOURCE.replace("x * LIMIT", "x * LIMIT * 2"), "utf-8")
    _commit(repo, "a code fix beside a reviewed docstring")
    assert _count(repo, capsys, reviewed) == (0, "0")

    _write(repo, "src/pkg/fresh.py", SOURCE + f'\n\ndef later():\n    """{LONG} again"""\n')
    _commit(repo, "a new long docstring")
    assert _count(repo, capsys, reviewed) == (0, "1")


def test_count_reads_the_commits_and_not_the_working_tree(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _write(repo, "src/pkg/fresh.py", SOURCE)

    assert _count(repo, capsys) == (0, "0")


def test_count_leaves_out_prose_a_merge_of_the_base_brings_in(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    reviewed = _commit(repo, "a review with nothing to review")
    _git(repo, "checkout", "-q", "main")
    _write(repo, "src/pkg/other.py", SOURCE)
    _commit(repo, "someone else's long prose")
    _git(repo, "checkout", "-q", "work")
    _git(repo, "merge", "-q", "--no-edit", "main")

    assert _count(repo, capsys, reviewed) == (0, "0")


def test_count_exits_2_when_a_changed_file_will_not_parse(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _write(repo, "src/pkg/broken.py", "def f(:\n")
    _commit(repo, "a file Python refuses")

    assert main(["--root", str(repo), "--base", "main", "--count"]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "src/pkg/broken.py" in captured.err
