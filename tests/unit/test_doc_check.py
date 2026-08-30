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

ROADMAP = """# Roadmap

## The plan

### The timeline

| # | Step | What it is | Size |
| --- | --- | --- | --- |
| 1 | **v0.3.0 \u2014 the foundation** | Gate 0. | 2 M |
| \u2014 | **v0.3.x \u2014 a readability pass** | A patch, not a milestone. | \u2014 |
| 2 | **v0.4.0 \u2014 the teachable case** | Scoped below. | 5 M |
| 3 | **Gate 1** | Frozen when v0.5.0 is scoped. | \u2014 |
| 4 | **v0.5.0 \u2014 the case you can branch** | Not yet scoped. | \u2014 |
| \u2014 | **MVP complete** | Run, branch, compare. | \u2014 |

## Planned milestones

Nothing yet.
"""

VERSION_SECTION = """## Versioning decision

| Version | Status | Milestone |
| --- | --- | --- |
| v0.2.4 | Completed | The one before. |
| v0.2.5 | Completed / current baseline | The current one. |
| v0.3.0 | Planned / scoped | Not out yet. |

## Current baseline: v0.2.5

What it is.

"""

VERSIONED_ROADMAP = ROADMAP.replace(
    "## Planned milestones", VERSION_SECTION + "## Planned milestones"
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
    roadmap: str = ROADMAP,
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
    (root / "ROADMAP.md").write_text(roadmap, encoding="utf-8")
    return root


def _errors(root: Path) -> list[str]:
    return doc_check.analyze(root).errors


def _versioned(tmp_path: Path, roadmap: str = VERSIONED_ROADMAP, version: str = "0.2.5") -> Path:
    """A repository that states its version in all three places the check reads."""
    root = _repo(tmp_path, roadmap=roadmap)
    (root / "pyproject.toml").write_text(
        f'[project]\nname = "demo"\nversion = "{version}"\n', encoding="utf-8"
    )
    return root


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


# --- release train ----------------------------------------------------------


def test_timeline_parses_every_row_of_the_fixture(tmp_path: Path) -> None:
    steps, problems = doc_check.parse_timeline(ROADMAP)
    assert problems == []
    assert [step.kind for step in steps] == [
        "milestone",
        "patch-track",
        "milestone",
        "gate",
        "milestone",
        "marker",
    ]
    assert [step.version for step in steps if step.kind == "milestone"] == [
        (0, 3, 0),
        (0, 4, 0),
        (0, 5, 0),
    ]


def test_a_gate_row_carries_no_version(tmp_path: Path) -> None:
    """Gates deliberately have no version; reading one as a milestone would
    invent a release that never ships."""
    steps, _ = doc_check.parse_timeline(ROADMAP)
    gate = next(step for step in steps if step.kind == "gate")
    assert gate.version is None
    assert gate.name == "1"


def test_a_patch_track_row_is_not_read_as_a_milestone(tmp_path: Path) -> None:
    """`v0.3.x` is a placeholder for patches, not a release to plan against."""
    steps, _ = doc_check.parse_timeline(ROADMAP)
    track = next(step for step in steps if step.kind == "patch-track")
    assert track.version == (0, 3, -1)
    assert track.ordinal is None


def test_a_step_that_is_not_bold_is_an_error(tmp_path: Path) -> None:
    roadmap = ROADMAP.replace("**Gate 1**", "Gate 1")
    assert any("is not bold" in e for e in _errors(_repo(tmp_path, roadmap=roadmap)))


def test_a_hyphen_typed_for_the_em_dash_is_an_error(tmp_path: Path) -> None:
    """The separator is spelled out so this fails rather than passing as a
    marker whose name happens to start with a version."""
    roadmap = ROADMAP.replace("v0.4.0 \u2014 the teachable", "v0.4.0 - the teachable")
    assert any("opens like a version" in e for e in _errors(_repo(tmp_path, roadmap=roadmap)))


def test_a_truncated_version_is_an_error(tmp_path: Path) -> None:
    roadmap = ROADMAP.replace("v0.4.0 \u2014", "v0.4 \u2014")
    assert any("opens like a version" in e for e in _errors(_repo(tmp_path, roadmap=roadmap)))


def test_milestones_out_of_order_are_an_error(tmp_path: Path) -> None:
    roadmap = ROADMAP.replace("v0.5.0 \u2014 the case", "v0.2.0 \u2014 the case")
    errors = _errors(_repo(tmp_path, roadmap=roadmap))
    assert any("is not later than the milestone above it" in e for e in errors)


def test_a_patch_track_under_the_wrong_milestone_is_an_error(tmp_path: Path) -> None:
    roadmap = ROADMAP.replace("v0.3.x \u2014", "v0.9.x \u2014")
    errors = _errors(_repo(tmp_path, roadmap=roadmap))
    assert any("does not belong to v0.3" in e for e in errors)


def test_step_numbers_out_of_order_are_an_error(tmp_path: Path) -> None:
    roadmap = ROADMAP.replace("| 4 | **v0.5.0", "| 2 | **v0.5.0")
    assert any("does not follow" in e for e in _errors(_repo(tmp_path, roadmap=roadmap)))


def test_gates_out_of_order_are_an_error(tmp_path: Path) -> None:
    roadmap = ROADMAP.replace("**Gate 1**", "**Gate 3**").replace(
        "| \u2014 | **MVP complete** | Run, branch, compare. | \u2014 |",
        "| 5 | **Gate 2** | Frozen later. | \u2014 |",
    )
    errors = _errors(_repo(tmp_path, roadmap=roadmap))
    assert any("Gate 2 does not follow Gate 3" in e for e in errors)


def test_an_unnumbered_marker_is_accepted(tmp_path: Path) -> None:
    """ "MVP complete" is a boundary on the timeline, not a step, and must not
    have to invent a version or a number to sit there."""
    assert not any("MVP complete" in e for e in _errors(_repo(tmp_path)))


def test_a_timeline_that_has_vanished_is_an_error(tmp_path: Path) -> None:
    """A renamed or reformatted heading would otherwise disable the check
    silently, which is the drift this tool exists to catch."""
    roadmap = ROADMAP.replace("### The timeline", "### The schedule")
    errors = _errors(_repo(tmp_path, roadmap=roadmap))
    assert any("no timeline table found" in e for e in errors)


def test_a_timeline_of_gates_alone_is_an_error(tmp_path: Path) -> None:
    """A plan of gates with nothing to gate is not a plan, and would leave
    `docket wave` with no version to report the project's position against."""
    roadmap = """# Roadmap

## The plan

### The timeline

| # | Step | What it is | Size |
| --- | --- | --- | --- |
| 1 | **Gate 1** | Frozen at some point. | \u2014 |
| 2 | **Gate 2** | Frozen later. | \u2014 |
"""
    assert any("names no milestone version" in e for e in _errors(_repo(tmp_path, roadmap=roadmap)))


def test_a_table_further_down_the_file_is_not_mistaken_for_the_timeline(tmp_path: Path) -> None:
    """The search stops at the next heading, so an unrelated table below it
    cannot smuggle rows into the plan."""
    roadmap = (
        ROADMAP
        + """
## Some other section

| # | Step |
| --- | --- |
| 1 | not a step at all |
"""
    )
    steps, problems = doc_check.parse_timeline(roadmap)
    assert problems == []
    assert len(steps) == 6


def test_a_roadmap_agreeing_with_the_version_file_is_quiet(tmp_path: Path) -> None:
    assert _errors(_versioned(tmp_path)) == []


def test_a_release_that_bumped_only_the_version_file_is_an_error(tmp_path: Path) -> None:
    """The drift itself: v0.2.6 shipped and the roadmap still names v0.2.5 current."""
    errors = _errors(_versioned(tmp_path, version="0.2.6"))

    assert any("pyproject.toml holds 0.2.6" in message for message in errors)


def test_a_second_row_for_the_same_version_is_an_error(tmp_path: Path) -> None:
    """The table reached two v0.2.3 rows once; nothing noticed."""
    roadmap = VERSIONED_ROADMAP.replace(
        "| v0.3.0 | Planned / scoped | Not out yet. |",
        "| v0.2.4 | Completed | The one before, again. |",
    )
    errors = _errors(_versioned(tmp_path, roadmap=roadmap))

    assert any("already has a row" in message for message in errors)


def test_two_rows_marked_current_baseline_is_an_error(tmp_path: Path) -> None:
    roadmap = VERSIONED_ROADMAP.replace(
        "| v0.2.4 | Completed | The one before. |",
        "| v0.2.4 | Completed / current baseline | The one before. |",
    )
    errors = _errors(_versioned(tmp_path, roadmap=roadmap))

    assert any("marked" in message and "current" in message for message in errors)


def test_no_row_marked_current_baseline_is_an_error(tmp_path: Path) -> None:
    roadmap = VERSIONED_ROADMAP.replace(" / current baseline", "")
    errors = _errors(_versioned(tmp_path, roadmap=roadmap))

    assert any("0 rows are marked" in message for message in errors)


def test_a_baseline_heading_naming_another_version_is_an_error(tmp_path: Path) -> None:
    """A heading and a table row disagreeing is how the file read for two releases."""
    roadmap = VERSIONED_ROADMAP.replace(
        "## Current baseline: v0.2.5", "## Current baseline: v0.2.4"
    )
    errors = _errors(_versioned(tmp_path, roadmap=roadmap))

    assert any("baseline heading names v0.2.4" in message for message in errors)


def test_a_missing_baseline_heading_is_an_error(tmp_path: Path) -> None:
    roadmap = VERSIONED_ROADMAP.replace("## Current baseline: v0.2.5", "## Where we are")
    errors = _errors(_versioned(tmp_path, roadmap=roadmap))

    assert any("Current baseline" in message and "heading" in message for message in errors)


def test_a_version_table_that_has_vanished_is_an_error(tmp_path: Path) -> None:
    roadmap = VERSIONED_ROADMAP.replace("## Versioning decision", "## How we number things")
    errors = _errors(_versioned(tmp_path, roadmap=roadmap))

    assert any("no version table found" in message for message in errors)


def test_a_repository_with_no_version_file_is_left_alone(tmp_path: Path) -> None:
    """The checker runs in projects that do not version; it is not their business."""
    assert _errors(_repo(tmp_path, roadmap=VERSIONED_ROADMAP)) == []


# --- make targets -----------------------------------------------------------

MAKEFILE = """.PHONY: check docket

check:
\tpytest

docket:
\tbin/docket check
"""


def _with_make(tmp_path: Path, *, makefile: str = MAKEFILE, mentions: str = "") -> Path:
    """A repository whose README names make commands the Makefile must honour."""
    root = _repo(tmp_path, readme=README + mentions)
    (root / "Makefile").write_text(makefile, encoding="utf-8")
    return root


def test_a_documented_target_that_runs_is_quiet(tmp_path: Path) -> None:
    assert _errors(_with_make(tmp_path, mentions="\nRun `make docket` before committing.\n")) == []


def test_a_documented_target_with_no_recipe_is_an_error(tmp_path: Path) -> None:
    """The PL-ZRFC failure: declared `.PHONY`, never given a recipe, exits 0."""
    makefile = MAKEFILE.replace(
        "docket:\n\tbin/docket check\n", "punch-list:\n\tbin/docket check\n"
    )
    errors = _errors(_with_make(tmp_path, makefile=makefile, mentions="\n`make docket` first.\n"))

    assert any("make docket" in message and "no recipe" in message for message in errors)


def test_a_documented_target_the_makefile_never_names_is_an_error(tmp_path: Path) -> None:
    errors = _errors(_with_make(tmp_path, mentions="\nRun `make lint` first.\n"))

    assert any("make lint" in message and "does not define" in message for message in errors)


def test_a_target_named_in_a_fenced_block_is_read(tmp_path: Path) -> None:
    errors = _errors(_with_make(tmp_path, mentions="\n```bash\nmake lint\n```\n"))

    assert any("make lint" in message for message in errors)


def test_prose_that_says_make_sure_names_no_target(tmp_path: Path) -> None:
    """Only code is read: English uses the word for something else entirely."""
    assert _errors(_with_make(tmp_path, mentions="\nPlease make sure the tests pass.\n")) == []


def test_a_repository_with_no_makefile_is_left_alone(tmp_path: Path) -> None:
    assert _errors(_repo(tmp_path, readme=README + "\nRun `make lint`.\n")) == []
