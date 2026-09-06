"""Tests for `tools/workflow_paths_check.py`, the lane-boundary completeness guard.

The check exists because `docket.toml`'s `workflow_paths` named three apparatus
test files by hand and was nine short by the following day (`PL-JBZK`). The
failure is silent, and silent in the worst direction: an item declaring one
`tools/` script and its own test lands in neither lane, so `docket next
workflow` and `docket next product` both set it aside and no session is ever
offered it.

The interesting tests are therefore not the happy path but the two directions
the list can be wrong in - an apparatus test the list has fallen behind on, and
a product test the list has over-claimed - each asserted to name the exact line
to add or remove, because a failure that says "this is wrong" without saying
what to write sends the reader back to the measurement.

Two others carry the design rather than the behavior.
`test_a_tools_script_and_its_own_test_land_in_the_same_lane` is the end-to-end
statement of what the item asked for, run against this repository's real
settings through the same `Item.lane` that ranks the queue - so it fails if the
check passes while the thing the check is *for* is still broken. And
`test_the_prefix_comparison_agrees_with_the_lane_it_mirrors` pins the one
knowing duplication in the tool: `is_covered` restates
`docket.model.is_under` because tools here may import the standard library
only, and this is what stops the two drifting apart in silence.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import workflow_paths_check
from docket.model import LANE_WORKFLOW, is_under, parse_item

ROOT = Path(workflow_paths_check.__file__).resolve().parent.parent

#: A test file that imports the simulator, and so is the simulator's.
PRODUCT_TEST = "from anesthesia_sim.core.blood import Blood\n\n\ndef test_it():\n    pass\n"

#: A test file that imports no product code, and so is apparatus. It names a
#: `src/` path in fixture text on purpose - several real apparatus tests do,
#: because they check tools that read the tree.
APPARATUS_TEST = (
    'import pr_title_check\n\nSAMPLE = "src/anesthesia_sim/core/blood.py"\n\n\n'
    "def test_it():\n    pass\n"
)


def _repo(tmp_path: Path, *, workflow_paths: tuple[str, ...], **tests: str) -> Path:
    """A repository root with a `docket.toml` and the named files under `tests/unit/`.

    Keywords are file stems, so `_repo(p, workflow_paths=(), test_a=...)`
    writes `tests/unit/test_a.py`.
    """
    entries = "".join(f'  "{entry}",\n' for entry in workflow_paths)
    (tmp_path / "docket.toml").write_text(
        f"[docket]\nworkflow_paths = [\n{entries}]\n", encoding="utf-8"
    )
    unit = tmp_path / "tests" / "unit"
    unit.mkdir(parents=True)
    for stem, body in tests.items():
        (unit / f"{stem}.py").write_text(body, encoding="utf-8")
    return tmp_path


def test_an_apparatus_test_missing_from_the_list_is_refused(tmp_path: Path) -> None:
    root = _repo(tmp_path, workflow_paths=("tools",), test_thing_check=APPARATUS_TEST)
    found = workflow_paths_check.problems(root)
    assert len(found) == 1
    assert "tests/unit/test_thing_check.py" in found[0]
    assert "does not cover it" in found[0]


def test_the_message_names_the_line_to_add(tmp_path: Path) -> None:
    root = _repo(tmp_path, workflow_paths=("tools",), test_thing_check=APPARATUS_TEST)
    (problem,) = workflow_paths_check.problems(root)
    assert 'Add "tests/unit/test_thing_check.py" to workflow_paths' in problem


def test_a_product_test_in_the_list_is_refused(tmp_path: Path) -> None:
    root = _repo(
        tmp_path, workflow_paths=("tools", "tests/unit/test_blood.py"), test_blood=PRODUCT_TEST
    )
    (problem,) = workflow_paths_check.problems(root)
    assert 'Remove "tests/unit/test_blood.py" from workflow_paths' in problem


def test_an_apparatus_test_in_the_list_is_accepted(tmp_path: Path) -> None:
    root = _repo(
        tmp_path,
        workflow_paths=("tools", "tests/unit/test_thing_check.py"),
        test_thing_check=APPARATUS_TEST,
    )
    assert workflow_paths_check.problems(root) == []


def test_a_product_test_absent_from_the_list_is_accepted(tmp_path: Path) -> None:
    root = _repo(tmp_path, workflow_paths=("tools",), test_blood=PRODUCT_TEST)
    assert workflow_paths_check.problems(root) == []


def test_the_product_package_named_only_in_a_string_is_not_an_import(tmp_path: Path) -> None:
    """The reason the tool parses rather than greps.

    `APPARATUS_TEST` writes `src/anesthesia_sim/core/blood.py` as fixture text,
    which is what several real apparatus tests do. Read as text it looks like a
    product dependency; read as code it is a string.
    """
    root = _repo(
        tmp_path,
        workflow_paths=("tools", "tests/unit/test_thing_check.py"),
        test_thing_check=APPARATUS_TEST,
    )
    assert workflow_paths_check.problems(root) == []


def test_a_submodule_import_of_the_product_counts(tmp_path: Path) -> None:
    """`import anesthesia_sim.core.blood` is a product dependency like any other."""
    root = _repo(
        tmp_path,
        workflow_paths=("tools", "tests/unit/test_plain.py"),
        test_plain="import anesthesia_sim.core.blood\n\n\ndef test_it():\n    pass\n",
    )
    (problem,) = workflow_paths_check.problems(root)
    assert "Remove" in problem


def test_a_directory_entry_covering_a_product_test_is_refused(tmp_path: Path) -> None:
    """The list is read as path prefixes, so a coarse entry over-claims too."""
    root = _repo(tmp_path, workflow_paths=("tools", "tests/unit"), test_blood=PRODUCT_TEST)
    (problem,) = workflow_paths_check.problems(root)
    assert "tests/unit/test_blood.py" in problem
    assert "covers it" in problem


def test_a_file_that_cannot_be_parsed_is_reported_rather_than_skipped(tmp_path: Path) -> None:
    root = _repo(tmp_path, workflow_paths=("tools",), test_broken="def (:\n")
    (problem,) = workflow_paths_check.problems(root)
    assert "could not be parsed" in problem
    assert "tests/unit/test_broken.py" in problem


def test_an_empty_list_is_reported_rather_than_passing_vacuously(tmp_path: Path) -> None:
    """Empty `workflow_paths` makes every item unplaced, which is not a clean tree."""
    root = _repo(tmp_path, workflow_paths=(), test_blood=PRODUCT_TEST)
    (problem,) = workflow_paths_check.problems(root)
    assert "declares no workflow_paths" in problem


def test_every_offender_is_named_not_only_the_first(tmp_path: Path) -> None:
    root = _repo(
        tmp_path,
        workflow_paths=("tools",),
        test_one_check=APPARATUS_TEST,
        test_two_check=APPARATUS_TEST,
    )
    found = workflow_paths_check.problems(root)
    assert len(found) == 2


def test_the_failure_prints_to_stderr_and_exits_one(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _repo(tmp_path, workflow_paths=("tools",), test_thing_check=APPARATUS_TEST)
    monkeypatch.setattr("sys.argv", ["workflow_paths_check.py", "--root", str(root)])
    assert workflow_paths_check.main() == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "test_thing_check.py" in captured.err
    assert "PL-JBZK" in captured.err


def test_a_clean_tree_reports_what_it_counted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _repo(
        tmp_path,
        workflow_paths=("tools", "tests/unit/test_thing_check.py"),
        test_thing_check=APPARATUS_TEST,
        test_blood=PRODUCT_TEST,
    )
    monkeypatch.setattr("sys.argv", ["workflow_paths_check.py", "--root", str(root)])
    assert workflow_paths_check.main() == 0
    assert "2 test file(s)" in capsys.readouterr().out


def test_a_tools_script_and_its_own_test_land_in_the_same_lane() -> None:
    """What `PL-JBZK` asked for, stated end to end against this repository.

    Not a restatement of the check: it goes through `Item.lane` with the real
    `workflow_paths`, which is the code that actually decides what `docket next
    workflow` offers. An item that is plainly one `tools/` script and its own
    test has to come out `workflow`, not `crossing` - `crossing` is the state
    in which no session is offered it at all.
    """
    paths = workflow_paths_check.declared_workflow_paths(ROOT)
    for stem in ("pr_title_check", "branch_id_check", "ignore_check"):
        item = parse_item(
            "---\n"
            "id: PL-TEST\n"
            f"title: A change to {stem} and its own test\n"
            "priority: P2\n"
            "effort: S\n"
            "status: ready\n"
            f"touches: tools/{stem}.py, tests/unit/test_{stem}.py\n"
            "---\n\nBody.\n"
        )
        assert item.lane(paths) == LANE_WORKFLOW, stem


def test_the_prefix_comparison_agrees_with_the_lane_it_mirrors() -> None:
    """`is_covered` restates `docket.model.is_under`; this is what pins them together.

    The tool may not import `docket` - every script in `tools/` is standard
    library only so a bare checkout can run it - so the comparison is written
    twice on purpose. Asserted over this repository's own list and every file
    the check reads, plus the edge cases a trailing slash gets wrong.
    """
    paths = workflow_paths_check.declared_workflow_paths(ROOT)
    candidates = [
        path.relative_to(ROOT).as_posix()
        for path in sorted((ROOT / workflow_paths_check.TESTS_DIR).rglob("*.py"))
    ]
    candidates += [
        "tools/doc_check.py",
        "tools",
        "toolsmith/other.py",
        "docs/items/PL-JBZK.md",
        "src/anesthesia_sim/core/blood.py",
        "docket.toml",
        "docket.toml.bak",
    ]
    for candidate in candidates:
        assert workflow_paths_check.is_covered(candidate, paths) == is_under(candidate, paths), (
            candidate
        )


def test_this_repository_passes_its_own_check() -> None:
    assert workflow_paths_check.problems(ROOT) == []
