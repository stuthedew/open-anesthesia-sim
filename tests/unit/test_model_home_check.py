"""`tools/model_home_check.py` must refuse a model id written outside `docket.toml`'s table.

The direction that matters most is the false green: a tool or an open item
that names a model the table no longer chooses, or the model the owner
excluded, passing silently. That is how an open item went on recommending
Fable 5.1 after the owner had stopped using it (`PL-0XDM`).
"""

from __future__ import annotations

from pathlib import Path

import pytest
from model_home_check import COPIES, main, problems

TABLE = (
    '[docket]\ncollected_test_paths = ["tests", "subprojects/docket/tests"]\n'
    "[models]\n"
    'default = { model = "claude-opus-5-5", effort = "high" }\n'
    'excluded = ["claude-fable-5-1"]\n'
)

OPEN_ITEM = "---\nid: PL-B7K2\ntitle: An open item\nstatus: ready\n---\n\n"
CLOSED_ITEM = "---\nid: PL-C8M3\ntitle: A closed item\nstatus: done\n---\n\n"


def _tree(root: Path, files: dict[str, str]) -> Path:
    (root / "docket.toml").write_text(TABLE, encoding="utf-8")
    for path, text in files.items():
        (root / path).parent.mkdir(parents=True, exist_ok=True)
        (root / path).write_text(text, encoding="utf-8")
    return root


@pytest.mark.reads_item_store
def test_the_repository_names_no_model_outside_its_home(capsys: pytest.CaptureFixture[str]) -> None:
    assert main([]) == 0
    assert "0 errors" in capsys.readouterr().out


def test_a_tool_naming_a_model_is_refused(tmp_path: Path) -> None:
    root = _tree(tmp_path, {"tools/run.py": 'MODEL = "claude-sonnet-5-5"\n'})
    (found,) = problems(root)
    assert found.startswith("tools/run.py: names claude-sonnet-5-5;")


def test_the_excluded_model_is_refused_in_an_open_item_and_a_registered_copy(
    tmp_path: Path,
) -> None:
    copy = next(iter(COPIES))
    root = _tree(
        tmp_path,
        {
            "docs/items/PL-B7K2-open.md": OPEN_ITEM + "Run it on `claude-fable-5-1`.\n",
            copy: "Set `claude-fable-5-1` at launch.\n",
        },
    )
    found = problems(root)
    assert len(found) == 2
    assert all("claude-fable-5-1, which [models] excludes" in line for line in found)


def test_records_tests_and_the_home_may_name_any_model(tmp_path: Path) -> None:
    root = _tree(
        tmp_path,
        {
            "docs/items/PL-C8M3-closed.md": CLOSED_ITEM + "Ran on `claude-fable-5-1`.\n",
            "docs/items/PL-B7K2-open.md": OPEN_ITEM + "Chose `claude-sonnet-5-5`.\n",
            "docs/session-ledger.tsv": "s1\tclaude-fable-5-1\n",
            "docs/worker-runs/run.json": '{"model": "claude-fable-5-1"}\n',
            "tests/unit/test_x.py": 'assert model != "claude-fable-5-1"\n',
            "subprojects/docket/tests/test_y.py": '"claude-haiku-5-5"\n',
        },
    )
    assert problems(root) == []


def test_a_registered_copy_may_name_a_model_the_table_does_not_exclude(tmp_path: Path) -> None:
    root = _tree(tmp_path, {path: "# `claude-sonnet-5-5`\n" for path in COPIES})
    assert problems(root) == []


def test_a_project_with_no_models_table_is_a_finding(tmp_path: Path) -> None:
    (tmp_path / "docket.toml").write_text("", encoding="utf-8")
    (found,) = problems(tmp_path)
    assert "no [models] table" in found
