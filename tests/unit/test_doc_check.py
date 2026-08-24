"""Tests for `tools/doc_check.py`, the documentation checker.

The tool exists to catch drift nobody remembered to look for, so its value is
entirely in the failures it detects. Every check therefore has a test that
builds the broken documentation and asserts the tool notices, and a matching
test that asserts the correct form stays quiet — a checker that fires on
correct writing gets disabled, which is the same as not having it.

Fixtures are built by `_repo()` as a miniature repository with one module and
one data file, so a test names only the thing it breaks.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import doc_check
import pytest

ARCHITECTURE = """# Architecture overview

## Package map

```text
src/anesthesia_sim/
├── core/
│   └── thing.py
└── data/
    └── agents/demo.json
```

## Developer tooling

```text
tools/
└── harness/
```
"""

FAT_KEY = "tissue_gas_partition_coefficients.fat"
ROW = "| {} | {} | dimensionless | `data/agents/demo.json` · `{}` |"

MODEL = "\n".join(
    [
        "# Model",
        "",
        "## Parameter provenance",
        "",
        "| Parameter | Selected value | Unit | Source (data file · key path) |",
        "| --- | ---: | --- | --- |",
        ROW.format("Demo blood:gas coefficient", "0.5", "blood_gas_partition_coefficient"),
        ROW.format("Demo tissue:blood coefficient", "4.0 (= 2.0 / 0.5)", FAT_KEY),
        "",
        "## Known limitations",
        "",
        "Nothing yet.",
        "",
    ]
)

README = """# Demo

The simulation lives in `core/thing.py` and its parameters in
`data/agents/demo.json`. See "Known limitations" for what it omits.
"""

DATA = {
    "schema_version": 1,
    "id": "demo",
    "display_name": "Demo",
    "blood_gas_partition_coefficient": 0.5,
    "tissue_gas_partition_coefficients": {"fat": 2.0},
    "sources": [{"citation": "Nobody. A paper.", "url": "https://example.invalid/", "note": "n"}],
}


def _repo(
    tmp_path: Path,
    *,
    architecture: str = ARCHITECTURE,
    model: str = MODEL,
    readme: str = README,
    data: dict[str, object] | None = None,
    modules: tuple[str, ...] = ("core/thing.py",),
) -> Path:
    """Build a miniature repository with the structure the checker reads."""
    root = tmp_path / "repo"
    (root / "docs").mkdir(parents=True, exist_ok=True)
    (root / "tools" / "harness").mkdir(parents=True, exist_ok=True)
    (root / "tools" / "harness" / "run.py").write_text("", encoding="utf-8")

    for relative in modules:
        module = root / "src" / "anesthesia_sim" / relative
        module.parent.mkdir(parents=True, exist_ok=True)
        module.write_text("", encoding="utf-8")
    for package in (root / "src" / "anesthesia_sim").rglob("*"):
        if package.is_dir():
            (package / "__init__.py").write_text("", encoding="utf-8")

    agents = root / "src" / "anesthesia_sim" / "data" / "agents"
    agents.mkdir(parents=True, exist_ok=True)
    payload = DATA if data is None else data
    (agents / "demo.json").write_text(json.dumps(payload, indent=4), encoding="utf-8")

    (root / "docs" / "ARCHITECTURE.md").write_text(architecture, encoding="utf-8")
    (root / "docs" / "MODEL.md").write_text(model, encoding="utf-8")
    (root / "README.md").write_text(readme, encoding="utf-8")
    return root


def _errors(root: Path) -> list[str]:
    return doc_check.analyze(root).errors


def test_clean_repository_reports_nothing(tmp_path: Path) -> None:
    assert _errors(_repo(tmp_path)) == []


def test_this_repository_is_clean() -> None:
    """The real tree must satisfy its own checker, not only a fixture."""
    root = Path(doc_check.__file__).resolve().parent.parent
    assert doc_check.analyze(root).errors == []


# --- package map ------------------------------------------------------------


def test_module_missing_from_package_map_is_an_error(tmp_path: Path) -> None:
    root = _repo(tmp_path, modules=("core/thing.py", "core/undocumented.py"))
    assert any("does not list src/anesthesia_sim/core/undocumented.py" in e for e in _errors(root))


def test_package_map_entry_that_no_longer_exists_is_an_error(tmp_path: Path) -> None:
    architecture = ARCHITECTURE.replace("│   └── thing.py", "│   ├── thing.py\n│   └── deleted.py")
    root = _repo(tmp_path, architecture=architecture)
    assert any("lists src/anesthesia_sim/core/deleted.py" in e for e in _errors(root))


def test_childless_directory_covers_its_whole_subtree(tmp_path: Path) -> None:
    """`tools/harness/` is drawn without children, so `run.py` needs no line."""
    assert not any("harness/run.py" in e for e in _errors(_repo(tmp_path)))


def test_init_files_are_not_required_in_the_map(tmp_path: Path) -> None:
    assert not any("__init__.py" in e for e in _errors(_repo(tmp_path)))


def test_a_file_with_no_tree_at_all_fails_rather_than_passing_silently(tmp_path: Path) -> None:
    root = _repo(tmp_path, architecture="# Architecture overview\n\nNo trees here.\n")
    assert any("no package-map tree found" in e for e in _errors(root))


# --- provenance table -------------------------------------------------------


def test_constant_with_no_provenance_row_is_an_error(tmp_path: Path) -> None:
    data = dict(DATA) | {"mac_percent": 3.0}
    root = _repo(tmp_path, data=data)
    assert any(
        "no provenance row for data/agents/demo.json mac_percent" in e for e in _errors(root)
    )


def test_row_disagreeing_with_the_data_file_is_an_error(tmp_path: Path) -> None:
    data = dict(DATA) | {"blood_gas_partition_coefficient": 0.7}
    root = _repo(tmp_path, data=data)
    assert any("holds blood_gas_partition_coefficient = 0.7" in e for e in _errors(root))


def test_row_naming_a_key_the_file_does_not_hold_is_an_error(tmp_path: Path) -> None:
    model = MODEL.replace("`blood_gas_partition_coefficient`", "`blood_gas_coefficient`")
    root = _repo(tmp_path, model=model)
    assert any("names key 'blood_gas_coefficient'" in e for e in _errors(root))


def test_derived_row_passes_on_the_stored_value_not_the_derived_one(tmp_path: Path) -> None:
    """`4.0 (= 2.0 / 0.5)` documents a stored 2.0; the derived 4.0 is not in the file."""
    assert not any("tissue_gas_partition_coefficients.fat" in e for e in _errors(_repo(tmp_path)))


def test_derived_row_that_lost_its_stored_value_is_an_error(tmp_path: Path) -> None:
    model = MODEL.replace("4.0 (= 2.0 / 0.5)", "4.0")
    root = _repo(tmp_path, model=model)
    assert any("holds tissue_gas_partition_coefficients.fat = 2" in e for e in _errors(root))


def test_a_constant_documented_twice_is_an_error(tmp_path: Path) -> None:
    duplicate = ROW.format("Demo blood:gas again", "0.5", "blood_gas_partition_coefficient")
    model = MODEL.replace("\n## Known limitations", duplicate + "\n\n## Known limitations")
    root = _repo(tmp_path, model=model)
    assert any("already has a row at line" in e for e in _errors(root))


def test_row_without_a_key_path_is_an_error(tmp_path: Path) -> None:
    model = MODEL.replace(" · `blood_gas_partition_coefficient`", "")
    root = _repo(tmp_path, model=model)
    assert any("names 1 code spans in its source cell" in e for e in _errors(root))


def test_schema_version_is_not_treated_as_a_parameter(tmp_path: Path) -> None:
    assert not any("schema_version" in e for e in _errors(_repo(tmp_path)))


def test_a_model_with_no_table_at_all_fails_rather_than_passing_silently(tmp_path: Path) -> None:
    root = _repo(tmp_path, model="# Model\n\n## Parameter provenance\n\nNone yet.\n")
    assert any("no provenance table found" in e for e in _errors(root))


# --- citations --------------------------------------------------------------


def test_path_citation_that_does_not_exist_is_an_error(tmp_path: Path) -> None:
    root = _repo(tmp_path, readme=README.replace("`core/thing.py`", "`core/moved.py`"))
    assert any("cites `core/moved.py`" in e for e in _errors(root))


def test_package_relative_and_bare_citations_both_resolve(tmp_path: Path) -> None:
    readme = "# Demo\n\nSee `core/thing.py`, `thing.py`, and `docs/MODEL.md`.\n"
    assert not any("cites `" in e for e in _errors(_repo(tmp_path, readme=readme)))


def test_glob_citation_resolves_and_a_dangling_one_does_not(tmp_path: Path) -> None:
    readme = "# Demo\n\nParameters live in `data/agents/*.json`.\n"
    assert not any("cites `" in e for e in _errors(_repo(tmp_path, readme=readme)))
    readme = "# Demo\n\nParameters live in `data/patients/*.json`.\n"
    assert any("cites `data/patients/*.json`" in e for e in _errors(_repo(tmp_path, readme=readme)))


def test_identifiers_are_not_mistaken_for_paths(tmp_path: Path) -> None:
    readme = "# Demo\n\nSee `Entry.model_guidance`, `flet_charts.*`, `v0.2.0`, `--cov`.\n"
    assert not any("cites `" in e for e in _errors(_repo(tmp_path, readme=readme)))


def test_dangling_section_citation_is_an_error(tmp_path: Path) -> None:
    readme = README.replace('"Known limitations"', '"Renamed limitations"')
    root = _repo(tmp_path, readme=readme)
    assert any('cites section "Renamed limitations"' in e for e in _errors(root))


def test_directional_citation_must_resolve_in_the_citing_file(tmp_path: Path) -> None:
    """`see "X" below` points at this file, so a heading elsewhere is not enough."""
    readme = README.replace(
        'See "Known limitations" for what it omits.',
        'See "Known limitations" below for what it omits.',
    )
    root = _repo(tmp_path, readme=readme)
    assert any('cites section "Known limitations" in this file' in e for e in _errors(root))


def test_citation_matching_the_start_of_a_longer_heading_resolves(tmp_path: Path) -> None:
    """Prose shortens a long heading; requiring the full text would fail on it."""
    model = MODEL.replace("## Known limitations", "## Known limitations - and open questions")
    assert not any("cites section" in e for e in _errors(_repo(tmp_path, model=model)))


def test_sentence_punctuation_inside_the_quotes_still_resolves(tmp_path: Path) -> None:
    """`See "Known limitations."` is US quoting, not a heading ending in a period."""
    readme = '# Demo\n\nSee "Known limitations."\n'
    assert not any("cites section" in e for e in _errors(_repo(tmp_path, readme=readme)))


def test_a_capitalised_citation_is_checked_too(tmp_path: Path) -> None:
    readme = '# Demo\n\nSee "Renamed limitations" for what it omits.\n'
    assert any(
        'cites section "Renamed limitations"' in e for e in _errors(_repo(tmp_path, readme=readme))
    )


def test_ordinary_quoted_prose_is_not_read_as_a_citation(tmp_path: Path) -> None:
    readme = '# Demo\n\nRecord it in "the same change" as the code.\n'
    assert not any("cites section" in e for e in _errors(_repo(tmp_path, readme=readme)))


def test_broken_relative_link_is_an_error(tmp_path: Path) -> None:
    readme = "# Demo\n\nSee [the model](docs/GONE.md).\n"
    root = _repo(tmp_path, readme=readme)
    assert any("links to docs/GONE.md" in e for e in _errors(root))


def test_working_link_and_external_url_are_left_alone(tmp_path: Path) -> None:
    readme = "# Demo\n\nSee [the model](docs/MODEL.md) and [uv](https://example.invalid/).\n"
    assert not any("links to" in e for e in _errors(_repo(tmp_path, readme=readme)))


def test_link_anchor_must_name_a_heading(tmp_path: Path) -> None:
    readme = (
        "# Demo\n\nSee [limits](docs/MODEL.md#known-limitations) and [x](docs/MODEL.md#gone).\n"
    )
    errors = _errors(_repo(tmp_path, readme=readme))
    assert any("#gone" in e for e in errors)
    assert not any("#known-limitations" in e for e in errors)


# --- modes ------------------------------------------------------------------


def _git_init(root: Path) -> None:
    for command in (
        ("init", "-q"),
        ("config", "user.email", "test@example.invalid"),
        ("config", "user.name", "Test"),
        ("add", "-A"),
        ("commit", "-qm", "initial"),
    ):
        subprocess.run(("git", *command), cwd=root, check=True, capture_output=True)


def test_check_mode_exit_codes(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = _repo(tmp_path)
    assert doc_check.main(["check", "--root", str(root)]) == 0
    assert "all resolve" in capsys.readouterr().out

    broken = _repo(tmp_path / "broken", readme=README.replace("`core/thing.py`", "`core/x.py`"))
    assert doc_check.main(["check", "--root", str(broken)]) == 1
    assert "cites `core/x.py`" in capsys.readouterr().out


def test_candidates_mode_names_the_docs_that_mention_a_change(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _repo(tmp_path)
    _git_init(root)

    module = root / "src" / "anesthesia_sim" / "core" / "thing.py"
    module.write_text("def advance_thing() -> None:\n    return None\n", encoding="utf-8")

    assert doc_check.main(["candidates", "--root", str(root), "--base", "HEAD"]) == 0
    output = capsys.readouterr().out
    assert "core/thing.py" in output
    assert "README.md:3" in output


def test_candidates_mode_reports_a_removed_heading_not_a_filename(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A changed doc breaks cross-references to headings it dropped."""
    root = _repo(tmp_path)
    _git_init(root)

    model = root / "docs" / "MODEL.md"
    model.write_text(
        model.read_text(encoding="utf-8").replace("## Known limitations", "## Caveats"),
        encoding="utf-8",
    )

    assert doc_check.main(["candidates", "--root", str(root), "--base", "HEAD"]) == 0
    output = capsys.readouterr().out
    assert "Known limitations" in output
    assert "README.md:4" in output
    # The document that changed is not searched for its own name; every other
    # file linking to `docs/MODEL.md` is not evidence of drift.
    assert "MODEL.md  (MODEL.md)" not in output


def test_candidates_mode_is_quiet_when_nothing_changed(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _repo(tmp_path)
    assert doc_check.main(["candidates", "--root", str(root), "--base", "HEAD"]) == 0
    assert "nothing to sweep" in capsys.readouterr().out
