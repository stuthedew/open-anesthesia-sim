"""`tools/blind_review.py` must count the blind passes a branch owes and keep each pass blind.

A pass the count leaves out is never run and nothing says so, and a pass whose
directory holds more than the tree and the diff is not blind: `PL-TCBJ` threw
away a control run whose reviewer read the panel's findings. These tests pin the
count for each kind of change and what each pass's directory holds.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from blind_review import BRIEF, DIFF_FILE, passes_owed, prepare
from docket.arming import blind_passes


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    ).stdout


def _write(root: Path, path: str, text: str) -> None:
    (root / path).parent.mkdir(parents=True, exist_ok=True)
    (root / path).write_text(text, encoding="utf-8")


def _commit(root: Path, message: str) -> None:
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", message)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A repository with a seed commit on `main`, and a branch `work` checked out."""
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    for key, value in (("user.email", "t@example.com"), ("user.name", "T")):
        _git(root, "config", key, value)
    _write(root, "README.md", "seed\n")
    _commit(root, "seed")
    _git(root, "checkout", "-qb", "work")
    return root


@pytest.mark.parametrize(
    ("paths", "owed"),
    [
        (["tools/x.py", "docs/items/PL-B1C2.md"], 0),
        (["src/anesthesia_sim/app/chart_frame.py"], 1),
        (["README.md"], 1),
        (["tools/x.py", "src/anesthesia_sim/core/alveolar.py"], 2),
        (["src/anesthesia_sim/data/agents/sevoflurane.toml"], 2),
        (["docs/MODEL.md", "src/anesthesia_sim/app/chart_frame.py"], 2),
        (["docs/MODEL.md.bak"], 0),
    ],
)
def test_blind_passes_counts_one_for_the_simulator_and_two_for_its_clinical_paths(
    paths: list[str], owed: int
) -> None:
    assert blind_passes(paths) == owed


def test_a_test_of_the_tooling_owes_no_pass(repo: Path) -> None:
    _write(repo, "tests/unit/test_tool.py", "import json\n")
    _commit(repo, "tooling test")

    assert passes_owed(repo, "main")[0] == 0


def test_a_test_that_imports_the_simulator_owes_one_pass(repo: Path) -> None:
    _write(repo, "tests/unit/test_model.py", "import anesthesia_sim\n")
    _commit(repo, "simulator test")

    assert passes_owed(repo, "main")[0] == 1


def test_a_test_that_will_not_parse_owes_a_pass(repo: Path) -> None:
    _write(repo, "tests/unit/test_broken.py", "def (:\n")
    _commit(repo, "broken test")

    assert passes_owed(repo, "main")[0] == 1


def test_a_core_change_owes_two_passes(repo: Path) -> None:
    _write(repo, "src/anesthesia_sim/core/alveolar.py", "X = 1\n")
    _commit(repo, "core change")

    assert passes_owed(repo, "main")[0] == 2


def test_each_pass_gets_only_the_committed_tree_and_the_diff(repo: Path, tmp_path: Path) -> None:
    _write(repo, "src/anesthesia_sim/core/alveolar.py", "X = 1\n")
    _commit(repo, "PL-B1C2: add the alveolar constant")
    _write(repo, "notes.txt", "uncommitted\n")
    passes, fork = passes_owed(repo, "main")
    out = tmp_path / "out"
    out.mkdir()

    made = prepare(repo, fork, passes, out)

    assert [path.name for path in made] == ["pass-1", "pass-2"]
    assert sorted(path.name for path in out.iterdir()) == ["pass-1", "pass-2"]
    for directory in made:
        assert [path.name for path in directory.iterdir()] == ["tree"]
        tree = directory / "tree"
        assert sorted(path.name for path in tree.iterdir()) == sorted(
            ["README.md", "src", DIFF_FILE]
        )
        diff = (tree / DIFF_FILE).read_text(encoding="utf-8")
        assert "PL-B1C2: add the alveolar constant" in diff
        assert "+X = 1" in diff
        assert "seed" not in diff.split("diff --git")[0]


def test_the_brief_names_the_pass_directory_and_its_findings_file() -> None:
    brief = BRIEF.format(DIR="/tmp/blind/pass-2", SLUG="pass-2")

    assert "Your directory is /tmp/blind/pass-2." in brief
    assert "/tmp/blind/pass-2/findings-pass-2.md" in brief
    assert "{" not in brief
