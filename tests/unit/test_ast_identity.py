"""`tools/ast_identity.py`, which says whether a file's code moved between revisions (`PL-VHHB`).

A release cut rests "nothing computational moved" on this tool's verdict
where a simulator tree object changed. A verdict of unchanged for a changed
statement would let a computational change ship as a docstring edit, so the
tests hold both directions on real git history in a scratch repository.
"""

from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path
from types import ModuleType

import pytest

TOOL = Path(__file__).resolve().parents[2] / "tools" / "ast_identity.py"


def _tool() -> ModuleType:
    spec = importlib.util.spec_from_file_location("ast_identity", TOOL)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


AST_IDENTITY = _tool()

#: A module with a docstring at each level Python reads one: module, class and function.
BEFORE = '''"""The module."""

RATE = 2.5  # litres per minute


class Lung:
    """A lung."""

    def flow(self, minutes):
        """Return the flow."""
        return RATE * minutes
'''


def _repository(tmp_path: Path, files: dict[str, str | None]) -> tuple[Path, list[str]]:
    """A repository holding `BEFORE` and a data file, then a second commit applying `files`.

    A value of None deletes that file. Returns the root and the two commits' names.
    """

    root = tmp_path / "repo"
    root.mkdir()

    def git(*args: str) -> str:
        done = subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)
        return done.stdout.strip()

    git("init", "-q")
    git("config", "user.email", "t@example.com")
    git("config", "user.name", "T")
    (root / "src").mkdir()
    (root / "src" / "lung.py").write_text(BEFORE, encoding="utf-8")
    (root / "src" / "rates.toml").write_text("rate = 2.5\n", encoding="utf-8")
    git("add", "-A")
    git("commit", "-qm", "before")
    old = git("rev-parse", "HEAD")
    for name, text in files.items():
        target = root / name
        if text is None:
            target.unlink()
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
    git("add", "-A")
    git("commit", "-qm", "after", "--allow-empty")
    return root, [old, git("rev-parse", "HEAD")]


def test_a_docstring_only_change_reads_identical(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """New wording in every docstring, a new comment and a docstring added read as unchanged."""

    after = (
        BEFORE.replace('"""The module."""', '"""The module, now with a citation (Eger 1974)."""')
        .replace('"""Return the flow."""', '"""Return the flow, in litres."""')
        .replace("RATE = 2.5  # litres per minute", "# The rate.\nRATE = 2.5  # L/min")
        .replace("class Lung:\n", 'class Lung:\n    """A lung, documented again."""\n', 1)
        .replace('    """A lung."""\n\n', "\n", 1)
    )
    root, revisions = _repository(tmp_path, {"src/lung.py": after})

    assert AST_IDENTITY.main([*revisions, "src/lung.py"], root=root) == 0

    lines = capsys.readouterr().out.splitlines()
    assert lines[0] == "src/lung.py: unchanged apart from docstrings and comments"
    assert lines[-1].startswith("no code moved in 1 files between ")


@pytest.mark.parametrize(
    ("old", "new"),
    [
        ("RATE = 2.5", "RATE = 2.6"),
        ("return RATE * minutes", "return RATE / minutes"),
        ("def flow(self, minutes):", "def flow(self, hours):"),
    ],
    ids=["constant", "operator", "parameter"],
)
def test_a_changed_statement_does_not(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], old: str, new: str
) -> None:
    """A changed number, operator or name is a change, even beside a docstring edit."""

    after = BEFORE.replace(old, new).replace('"""A lung."""', '"""A lung, reworded."""')
    if old == "def flow(self, minutes):":
        after = after.replace("RATE * minutes", "RATE * hours")
    root, revisions = _repository(tmp_path, {"src/lung.py": after})

    assert AST_IDENTITY.main([*revisions, "src"], root=root) == 1

    lines = capsys.readouterr().out.splitlines()
    assert "src/lung.py: changed" in lines
    assert "src/rates.toml: unchanged, compared as text" in lines
    assert lines[-1].startswith("1 of 2 files moved between ")


def test_a_docstring_turned_into_code_is_a_change(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A statement added above a docstring is a change, though the string itself is removed."""

    after = BEFORE.replace(
        '        """Return the flow."""\n', '        scale = 1\n        """Return the flow."""\n'
    )
    root, revisions = _repository(tmp_path, {"src/lung.py": after})

    assert AST_IDENTITY.main([*revisions, "src/lung.py"], root=root) == 1
    assert capsys.readouterr().out.splitlines()[0] == "src/lung.py: changed"


def test_an_attribute_docstring_added_or_reworded_reads_identical(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`PL-6GP9`: a string under an assignment is a docstring, so editing one moves no code.

    Only each body's first string was removed, so the v0.6.7 cut read 19 files
    as changed whose only edit was an attribute docstring.
    """

    documented = BEFORE.replace(
        "RATE = 2.5  # litres per minute\n", 'RATE = 2.5  # litres per minute\n"""The rate."""\n'
    )
    reworded = documented.replace('"""The rate."""', '"""The flow rate, in L/min."""')
    root, revisions = _repository(tmp_path, {"src/lung.py": documented})

    assert AST_IDENTITY.main([*revisions, "src/lung.py"], root=root) == 0
    assert capsys.readouterr().out.splitlines()[0] == (
        "src/lung.py: unchanged apart from docstrings and comments"
    )
    assert AST_IDENTITY.without_docstrings(
        documented, "lung.py"
    ) == AST_IDENTITY.without_docstrings(reworded, "lung.py")


def test_a_string_turned_into_a_value_is_a_change(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A string that a statement uses is a value, not a docstring, so changing it counts."""

    after = BEFORE.replace("RATE = 2.5  # litres per minute", 'RATE = 2.5\nUNIT = "L/min"')
    root, revisions = _repository(tmp_path, {"src/lung.py": after})

    assert AST_IDENTITY.main([*revisions, "src/lung.py"], root=root) == 1
    assert capsys.readouterr().out.splitlines()[0] == "src/lung.py: changed"


def test_a_directory_names_every_file_added_removed_or_kept(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Under a directory, an added file and a removed one each count, and a data file is text."""

    root, revisions = _repository(
        tmp_path, {"src/new.py": "x = 1\n", "src/lung.py": None, "src/rates.toml": "rate = 2.6\n"}
    )

    assert AST_IDENTITY.main([*revisions, "src"], root=root) == 1

    assert capsys.readouterr().out.splitlines() == [
        "src/lung.py: removed",
        "src/new.py: added",
        "src/rates.toml: changed, compared as text",
        f"3 of 3 files moved between {revisions[0]} and {revisions[1]}",
    ]


def test_an_untouched_tree_reads_unchanged(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, revisions = _repository(tmp_path, {})

    assert AST_IDENTITY.main([*revisions, "src"], root=root) == 0

    assert capsys.readouterr().out.splitlines()[:2] == [
        "src/lung.py: unchanged",
        "src/rates.toml: unchanged, compared as text",
    ]


@pytest.mark.parametrize(
    ("revisions", "paths"),
    [
        (["no-such-tag", "HEAD"], ["src"]),
        (["HEAD", "HEAD"], ["no-such-dir"]),
        (["HEAD", "HEAD"], ["src", "no-such-dir"]),
    ],
    ids=["unreadable-revision", "no-file", "one-path-of-two-holds-no-file"],
)
def test_what_it_cannot_compare_exits_2(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], revisions: list[str], paths: list[str]
) -> None:
    """A revision git cannot read, or any path holding no file, is never reported as unchanged.

    A misspelt path beside a real one must not leave the real one's verdict
    standing for both.
    """

    root, _ = _repository(tmp_path, {})

    assert AST_IDENTITY.main([*revisions, *paths], root=root) == 2
    assert capsys.readouterr().out.startswith("ast_identity: ")


def test_a_file_that_does_not_parse_exits_2(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A file this interpreter cannot parse is never reported as moved or unchanged."""

    root, revisions = _repository(tmp_path, {"src/lung.py": "def flow(:\n"})

    assert AST_IDENTITY.main([*revisions, "src"], root=root) == 2
    assert capsys.readouterr().out.startswith("ast_identity: Python ")
