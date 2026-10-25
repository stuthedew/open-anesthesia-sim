"""`tools/check_support.py` holds what the source checks share, so each part must be right.

`fact_home_check.py` and `literal_home_check.py` test these through their own
reports. These tests pin the parts on their own: the scope a walk reports, the
ratchet's two directions, and the status `run_report` returns.
"""

from __future__ import annotations

import ast
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import pytest
from check_support import (
    ScopedVisitor,
    Stale,
    overflows,
    repository_root,
    run_report,
    stale_entries,
    stale_lines,
)

SOURCE = """
class Outer:
    def method(self):
        async def inner():
            NAME
    NAME
NAME
"""


class _Names(ScopedVisitor):
    def __init__(self) -> None:
        super().__init__()
        self.seen: list[str] = []
        self.entered: list[str] = []

    def enter(self, node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef) -> None:
        self.entered.append(f"{'.'.join(self.scope)}>{node.name}")

    def visit_Name(self, node: ast.Name) -> None:
        self.seen.append(".".join(self.scope))


def test_a_walk_knows_the_scope_of_each_node_and_enters_each_one_before_its_body() -> None:
    walk = _Names()
    walk.visit(ast.parse(SOURCE))

    assert walk.seen == ["Outer.method.inner", "Outer", ""]
    assert walk.entered == [">Outer", "Outer>method", "Outer.method>inner"]


def test_only_a_key_above_its_allowance_overflows_and_the_order_given_is_kept() -> None:
    sites = [
        (("b.py", ("git", "f")), ["one", "two"]),
        (("a.py", ("git", "g")), ["one"]),
        (("a.py", ("git", "h")), ["one", "two"]),
    ]
    baseline = {"a.py": {("git", "g"): 1}, "b.py": {("git", "f"): 1}}

    over = overflows(sites, baseline)

    assert [(entry.path, entry.key, entry.allowed, entry.found) for entry in over] == [
        ("b.py", ("git", "f"), 1, ("one", "two")),
        ("a.py", ("git", "h"), 0, ("one", "two")),
    ]


def test_an_entry_above_what_its_file_holds_is_stale_and_an_unread_file_is_not(
    tmp_path: Path,
) -> None:
    (tmp_path / "a.py").write_text("", encoding="utf-8")
    (tmp_path / "broken.py").write_text("", encoding="utf-8")
    baseline = {
        "a.py": {("git", "f"): 2, ("git", "g"): 1},
        "gone.py": {("git", "f"): 1},
        "broken.py": {("git", "f"): 1},
    }
    found = {"a.py": Counter({("git", "f"): 1, ("git", "g"): 1})}

    stale = stale_entries(tmp_path, baseline, found, {"broken.py"})

    assert stale == [
        Stale("a.py", ("git", "f"), 2, 1, False),
        Stale("gone.py", ("git", "f"), 1, 0, True),
    ]


def test_each_stale_entry_names_its_remedy() -> None:
    entries = [
        Stale("a.py", ("git", "f"), 2, 1, False),
        Stale("a.py", ("git", "g"), 1, 0, False),
        Stale("gone.py", ("git", "f"), 1, 0, True),
    ]

    lines = stale_lines(entries, lambda key: f"{key[0]} in {key[1]}")

    assert lines == [
        "",
        "Baselined but no longer there - lower the entry, so the count stays a ratchet:",
        "  a.py, git in f: baseline 2, found 1 - set it to 1",
        "  a.py, git in g: baseline 1, found 0 - delete it",
        "  gone.py, git in f: baseline 1, found 0 - the file no longer exists; delete its entries",
    ]
    assert stale_lines([], str) == []


@dataclass(frozen=True)
class _Report:
    errors: int


@pytest.mark.parametrize(("errors", "status"), [(0, 0), (3, 1)])
def test_run_report_prints_the_report_and_fails_only_on_an_error(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], errors: int, status: int
) -> None:
    read: list[Path] = []

    def analyze(root: Path) -> _Report:
        read.append(root)
        return _Report(errors)

    assert (
        run_report(["--root", str(tmp_path)], "A check.", analyze, lambda r: "the report") == status
    )
    assert read == [tmp_path.resolve()]
    assert capsys.readouterr().out == "the report\n"


def test_with_no_root_the_repository_is_the_one_holding_tools() -> None:
    assert repository_root([], "A check.") == Path(__file__).resolve().parents[2]
