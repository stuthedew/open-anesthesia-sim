"""The tools that read a path `docket.toml` configures read it through `docket.config`.

Each held its own literal - the store as `docs/items`, the version file as
`pyproject.toml`, the plan as `ROADMAP.md` - so a project setting any of them
had docket reading one place and the tools another (`PL-WCHF`). These set a
non-default value, in the top-level form `docket.config.load` also accepts,
and assert the readers that take a root follow it.
"""

from __future__ import annotations

from pathlib import Path

import doc_check
import generator_check

SETTINGS = 'items_dir = "queue"\nroadmap_file = "PLAN.md"\nversion_file = "pkg/pyproject.toml"\n'

#: A plan whose baseline is one release past what the configured file declares.
PLAN = """# Plan

## Versioning decision

| Version | Status | Milestone |
| --- | --- | --- |
| v0.2.0 | Completed / current baseline | The current one. |

## Current baseline: v0.2.0
"""


def _project(root: Path) -> Path:
    (root / "docket.toml").write_text(SETTINGS, encoding="utf-8")
    (root / "queue").mkdir()
    (root / "queue" / "PL-K7QX-a-thing.md").write_text("---\n---\n", encoding="utf-8")
    return root


def test_the_item_files_are_read_from_the_configured_store(tmp_path: Path) -> None:
    root = _project(tmp_path)

    assert generator_check.item_files(root) == [root / "queue" / "PL-K7QX-a-thing.md"]


def test_the_dated_records_include_the_configured_store(tmp_path: Path) -> None:
    root = _project(tmp_path)

    assert doc_check.dated_records(root)[0] == "queue/"
    assert "docs/items/" not in doc_check.dated_records(root)


def test_the_plan_is_read_from_the_configured_file(tmp_path: Path) -> None:
    root = _project(tmp_path)

    assert doc_check.roadmap_path(root) == Path("PLAN.md")


def test_the_baseline_reads_the_configured_version_file(tmp_path: Path) -> None:
    """`check_baseline` holds the plan to the file a cut bumps, not to `pyproject.toml`."""
    root = _project(tmp_path)
    (root / "PLAN.md").write_text(PLAN, encoding="utf-8")
    (root / "pkg").mkdir()
    (root / "pkg" / "pyproject.toml").write_text(
        '[project]\nname = "x"\nversion = "0.1.0"\n', encoding="utf-8"
    )
    report = doc_check.Report()

    doc_check.check_baseline(root, report)

    assert report.errors == [
        "PLAN.md:7: the current baseline row is v0.2.0, but pkg/pyproject.toml holds 0.1.0"
    ]
