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

**Tags.** Every version the table above marks Completed carries an annotated
tag.

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
        # A real git checkout, built by running real git from `PATH`: what is
        # under test is how doc_check reads one, so a stub would test the stub.
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


# --- release tags -----------------------------------------------------------

UNTAGGED_CLAIM = "\n\n**One version is untagged**: v0.2.4.\n"


def _tagged(tmp_path: Path, *names: str, roadmap: str = VERSIONED_ROADMAP) -> Path:
    """A versioned repository that is a git checkout holding the tags given."""
    root = _versioned(tmp_path, roadmap=roadmap)
    _git_init(root)
    for name in names:
        # Real tags, made with real git - see `_git_init` above.
        subprocess.run(("git", "tag", name), cwd=root, check=True, capture_output=True)
    return root


def _advisories(root: Path) -> list[str]:
    return doc_check.analyze(root).advisories


def _tag_names(root: Path) -> set[str]:
    listed = subprocess.run(
        ("git", "tag", "--list"), cwd=root, check=True, capture_output=True, text=True
    )
    return {name.strip() for name in listed.stdout.splitlines() if name.strip()}


def test_a_roadmap_whose_tags_match_the_repository_is_quiet(tmp_path: Path) -> None:
    root = _tagged(tmp_path, "v0.2.4", "v0.2.5")

    assert _errors(root) == []
    assert _advisories(root) == []


def test_a_completed_release_with_no_tag_is_an_error(tmp_path: Path) -> None:
    """PL-J3ZK's failure: a release whose span nothing can map back to a version."""
    errors = _errors(_tagged(tmp_path, "v0.2.5"))

    assert any("v0.2.4 is marked completed but git holds no tag" in message for message in errors)


def test_the_release_being_cut_is_an_advisory_not_an_error(tmp_path: Path) -> None:
    """The tag lands on the merge commit, so the newest version has none yet.

    Failing this would turn `make check` red on every release branch, which is
    the failure PL-8HJ2 removed.
    """
    root = _tagged(tmp_path, "v0.2.4")

    assert _errors(root) == []
    assert any("v0.2.5 is the current baseline and carries no tag" in a for a in _advisories(root))


def test_the_advisory_pastes_the_tag_commands_rather_than_asking_for_a_tag(tmp_path: Path) -> None:
    advisories = _advisories(_tagged(tmp_path, "v0.2.4"))

    assert any('git tag -a v0.2.5 <merge commit> -m "v0.2.5"' in a for a in advisories)


def test_a_tag_the_version_table_does_not_name_is_an_error(tmp_path: Path) -> None:
    """A release that shipped and never reached the table is invisible to the plan."""
    errors = _errors(_tagged(tmp_path, "v0.2.4", "v0.2.5", "v0.2.9"))

    assert any("git holds v0.2.9, but no row of the version table" in message for message in errors)


def test_a_tag_of_another_shape_is_not_read_as_a_release(tmp_path: Path) -> None:
    """`v0.2.6-rc1` names something the version table has no business holding."""
    assert _errors(_tagged(tmp_path, "v0.2.4", "v0.2.5", "v0.2.6-rc1")) == []


def test_a_version_named_untagged_that_is_in_fact_tagged_is_an_error(tmp_path: Path) -> None:
    """The two sentences agreeing with the repository is not enough on its own."""
    roadmap = VERSIONED_ROADMAP.replace("tag.\n", "tag." + UNTAGGED_CLAIM, 1)
    errors = _errors(_tagged(tmp_path, "v0.2.4", "v0.2.5", roadmap=roadmap))

    assert any("v0.2.4 is named as untagged, but git holds a tag" in message for message in errors)


def test_a_version_named_untagged_is_not_also_required_to_have_one(tmp_path: Path) -> None:
    """The exception is the whole point of writing it: it stops being an error."""
    roadmap = VERSIONED_ROADMAP.replace("tag.\n", "tag." + UNTAGGED_CLAIM, 1)

    assert _errors(_tagged(tmp_path, "v0.2.5", roadmap=roadmap)) == []


def test_a_count_that_disagrees_with_the_names_is_an_error(tmp_path: Path) -> None:
    """Neither half can be caught by comparing it with git; only by each other."""
    claim = UNTAGGED_CLAIM.replace("One version is", "Two versions are")
    roadmap = VERSIONED_ROADMAP.replace("tag.\n", "tag." + claim, 1)
    errors = _errors(_versioned(tmp_path, roadmap=roadmap))

    assert any("says Two untagged, but names 1" in message for message in errors)


def test_a_count_written_as_a_numeral_is_read_too(tmp_path: Path) -> None:
    claim = UNTAGGED_CLAIM.replace("One version is", "1 version is")
    roadmap = VERSIONED_ROADMAP.replace("tag.\n", "tag." + claim, 1)

    assert _errors(_versioned(tmp_path, roadmap=roadmap)) == []


def test_a_count_the_checker_cannot_read_is_reported_rather_than_guessed(tmp_path: Path) -> None:
    """Silently passing an unreadable count is a check nobody is running."""
    claim = UNTAGGED_CLAIM.replace("One version is", "Several versions are")
    roadmap = VERSIONED_ROADMAP.replace("tag.\n", "tag." + claim, 1)
    errors = _errors(_versioned(tmp_path, roadmap=roadmap))

    assert any('cannot read "Several" as a count' in message for message in errors)


def test_a_version_named_untagged_that_never_shipped_is_an_error(tmp_path: Path) -> None:
    claim = UNTAGGED_CLAIM.replace("v0.2.4", "v0.9.9")
    roadmap = VERSIONED_ROADMAP.replace("tag.\n", "tag." + claim, 1)
    errors = _errors(_versioned(tmp_path, roadmap=roadmap))

    assert any("v0.9.9 is named as untagged, but no row" in message for message in errors)


def test_a_missing_tags_statement_is_an_error(tmp_path: Path) -> None:
    """Deleting the claim removes it; it does not make it true."""
    roadmap = VERSIONED_ROADMAP.replace(
        "**Tags.** Every version the table above marks Completed carries an annotated\ntag.\n", ""
    )
    errors = _errors(_versioned(tmp_path, roadmap=roadmap))

    assert any('no "**Tags.**" statement' in message for message in errors)


def test_a_checkout_git_cannot_answer_for_is_told_nothing(tmp_path: Path) -> None:
    """A tag-less clone is a normal checkout, and PL-J3ZK's own trap.

    No repository, no git and no tags fetched all collapse to the same empty
    set, so a repository holding no tags exercises the silence
    deterministically, where a directory that merely is not a checkout would
    depend on what sits above `tmp_path`.

    A shallow clone was listed here too and does *not* belong: it returns a
    partial set rather than an empty one, which is why it went unguarded until
    `PL-J295`. The test below covers it.
    """
    root = _tagged(tmp_path)

    assert _errors(root) == []
    assert _advisories(root) == []


def test_a_truncated_clone_declines_instead_of_calling_older_releases_untagged(
    tmp_path: Path,
) -> None:
    """PL-J295: a shallow clone holds some tags, so absence proves nothing.

    Built as a real `--depth=1` clone rather than a stub, because the whole
    defect was a wrong belief about what git returns in this state: the tag on
    the older commit is unreachable and simply does not appear, while the tag
    on the tip does. A fake tag reader would encode the belief instead of
    testing it.
    """
    origin = tmp_path / "origin"
    origin.mkdir()
    root = _tagged(origin, "v0.2.4")
    (root / "second.txt").write_text("a later commit\n", encoding="utf-8")
    for command in (("add", "-A"), ("commit", "-qm", "second"), ("tag", "v0.2.5")):
        subprocess.run(("git", *command), cwd=root, check=True, capture_output=True)

    clone = tmp_path / "clone"
    subprocess.run(
        ("git", "clone", "--depth=1", "--quiet", root.as_uri(), str(clone)),
        check=True,
        capture_output=True,
    )
    assert _tag_names(clone) == {"v0.2.5"}, "the fixture must actually truncate the tag set"

    report = doc_check.analyze(clone)

    assert report.errors == []
    assert any("shallow clone" in message for message in report.declined)


def test_a_complete_clone_still_reports_a_release_with_no_tag(tmp_path: Path) -> None:
    """The decline must not become a blanket amnesty for the check it guards."""
    root = _tagged(tmp_path, "v0.2.5")

    assert any("v0.2.4 is marked completed but git holds no tag" in e for e in _errors(root))
    assert doc_check.analyze(root).declined == []


def test_a_roadmap_with_no_completed_release_is_left_alone(tmp_path: Path) -> None:
    roadmap = VERSIONED_ROADMAP.replace("Completed", "Planned")

    assert _errors(_tagged(tmp_path, "v0.2.4", roadmap=roadmap)) == []


# PL-W5LG: a workflow step names repository scripts by path exactly as the
# documentation does, and nothing held it to them until this check. The
# scripts live under `tools/harness/`, which the fixture's package map draws
# as a covered directory, so adding one does not trip the map check as well.

WORKFLOW = """\
name: quality

on: [push, pull_request]

jobs:
  checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7.0.1
      - run: uv run python tools/harness/thing.py check
      - run: bin/runner check
"""


def _with_workflow(root: Path, body: str = WORKFLOW) -> Path:
    """Give a repository a CI workflow, and the scripts its steps name."""
    workflows = root / ".github" / "workflows"
    workflows.mkdir(parents=True, exist_ok=True)
    (workflows / "quality.yml").write_text(body, encoding="utf-8")
    (root / "tools" / "harness").mkdir(parents=True, exist_ok=True)
    (root / "tools" / "harness" / "thing.py").write_text("", encoding="utf-8")
    (root / "bin").mkdir(exist_ok=True)
    (root / "bin" / "runner").write_text("", encoding="utf-8")
    return root


def test_a_workflow_whose_paths_resolve_is_quiet(tmp_path: Path) -> None:
    assert _errors(_with_workflow(_repo(tmp_path))) == []


def test_a_deleted_script_a_ci_step_runs_is_an_error(tmp_path: Path) -> None:
    """PL-W5LG's failure: `tools/punch_list.py` went, and only CI still named it."""
    root = _with_workflow(_repo(tmp_path))
    (root / "tools" / "harness" / "thing.py").unlink()

    errors = _errors(root)

    assert any(
        "runs `tools/harness/thing.py`, which does not exist" in message for message in errors
    )


def test_a_suffixless_script_is_held_to_the_same_standard(tmp_path: Path) -> None:
    """`bin/docket` is the reference that motivated the check, and has no suffix.

    The citation checker keys on a file's extension, which cannot see this one
    at all, so the workflow check keys on the first path segment instead.
    """
    root = _with_workflow(_repo(tmp_path))
    (root / "bin" / "runner").unlink()

    errors = _errors(root)

    assert any("runs `bin/runner`, which does not exist" in message for message in errors)


def test_an_action_reference_is_not_read_as_a_repository_path(tmp_path: Path) -> None:
    """`actions/checkout@v7.0.1` has a path's shape and names nothing in the tree."""
    root = _with_workflow(_repo(tmp_path))

    assert not any("actions/checkout" in message for message in _errors(root))


def test_a_block_scalar_step_is_read_line_by_line(tmp_path: Path) -> None:
    body = WORKFLOW.replace(
        "      - run: uv run python tools/harness/thing.py check\n",
        "      - run: |\n"
        "          uv sync --locked\n"
        "          uv run python tools/harness/gone.py check\n",
    )
    root = _with_workflow(_repo(tmp_path), body=body)

    errors = _errors(root)

    assert any(
        "runs `tools/harness/gone.py`, which does not exist" in message for message in errors
    )


def test_a_block_scalar_ends_at_the_next_step(tmp_path: Path) -> None:
    """A step after a block scalar is a step, not more of the block's body."""
    body = WORKFLOW.replace(
        "      - run: bin/runner check\n",
        "      - run: |\n          bin/runner check\n      - run: tools/harness/thing.py\n",
    )

    assert _errors(_with_workflow(_repo(tmp_path), body=body)) == []


def test_an_expansion_is_skipped_rather_than_guessed_at(tmp_path: Path) -> None:
    """A path built at run time cannot be resolved by reading the tree."""
    body = WORKFLOW.replace(
        "      - run: bin/runner check\n", "      - run: ${{ github.workspace }}/bin/runner check\n"
    )

    assert _errors(_with_workflow(_repo(tmp_path), body=body)) == []


def test_a_repository_with_no_workflows_is_left_alone(tmp_path: Path) -> None:
    assert _errors(_repo(tmp_path)) == []


# --- resident instructions --------------------------------------------------


SCOPED_RULE = """---
paths:
  - "src/**"
---

# Scoped

One line.
"""

UNSCOPED_RULE = """# Unscoped

One line.
"""


def _instructed(root: Path, *, claude: str = "# Rules\n\nOne.\n", **rules: str) -> Path:
    """Add the instruction files a session loads at launch."""
    (root / "CLAUDE.md").write_text(claude, encoding="utf-8")
    if rules:
        (root / ".claude" / "rules").mkdir(parents=True, exist_ok=True)
        for name, body in rules.items():
            (root / ".claude" / "rules" / f"{name}.md").write_text(body, encoding="utf-8")
    return root


def test_a_path_scoped_rule_is_not_resident(tmp_path: Path) -> None:
    """`paths:` frontmatter defers a rule to the sessions that match it."""
    root = _instructed(_repo(tmp_path), scoped=SCOPED_RULE, always=UNSCOPED_RULE)

    measured = dict(doc_check.measure_resident(root))

    assert measured == {"CLAUDE.md": 3, ".claude/rules/always.md": 3}


def test_frontmatter_without_a_paths_key_is_still_resident(tmp_path: Path) -> None:
    """Other frontmatter does not defer a rule; only `paths:` does."""
    root = _instructed(_repo(tmp_path), other="---\nname: x\n---\n\nBody.\n")

    assert ".claude/rules/other.md" in dict(doc_check.measure_resident(root))


def test_an_unterminated_frontmatter_block_is_not_read_as_scoped(tmp_path: Path) -> None:
    root = _instructed(_repo(tmp_path), broken="---\npaths:\n  - src\n\nBody with no close.\n")

    assert ".claude/rules/broken.md" in dict(doc_check.measure_resident(root))


def test_nested_rule_directories_are_measured(tmp_path: Path) -> None:
    """Claude Code discovers `.claude/rules/**.md` recursively, so this does too."""
    root = _instructed(_repo(tmp_path))
    nested = root / ".claude" / "rules" / "backend"
    nested.mkdir(parents=True)
    (nested / "api.md").write_text(UNSCOPED_RULE, encoding="utf-8")

    assert ".claude/rules/backend/api.md" in dict(doc_check.measure_resident(root))


def test_a_repository_with_no_instruction_files_reports_nothing(tmp_path: Path) -> None:
    assert doc_check.analyze(_repo(tmp_path)).resident is None


def test_growth_against_the_default_branch_is_an_advisory(tmp_path: Path) -> None:
    root = _instructed(_repo(tmp_path))
    _git_init(root)
    subprocess.run(("git", "branch", "-M", "main"), cwd=root, check=True, capture_output=True)
    (root / "CLAUDE.md").write_text("# Rules\n\nOne.\nTwo.\nThree.\n", encoding="utf-8")

    report = doc_check.analyze(root)

    assert report.resident is not None
    assert report.resident.growth == 2
    assert report.resident.deltas() == [("CLAUDE.md", 2)]
    assert report.errors == []
    assert any("resident instructions grew 2 lines" in m for m in report.advisories)
    assert any("PL-H7XN" in m for m in report.advisories)
    assert any("Never trim other resident text" in m for m in report.advisories)


def test_one_line_of_growth_is_reported_in_the_singular(tmp_path: Path) -> None:
    """`_plural` sits two lines from this advisory and it did not use it."""
    root = _instructed(_repo(tmp_path))
    _git_init(root)
    subprocess.run(("git", "branch", "-M", "main"), cwd=root, check=True, capture_output=True)
    (root / "CLAUDE.md").write_text("# Rules\n\nOne.\nTwo.\n", encoding="utf-8")

    report = doc_check.analyze(root)

    assert report.resident is not None
    assert report.resident.growth == 1
    assert any("grew 1 line against" in m for m in report.advisories)
    assert not any("grew 1 lines" in m for m in report.advisories)


def test_shrinking_is_reported_but_is_not_an_advisory(tmp_path: Path) -> None:
    """A routing pass that moves a rule out must not read as a finding."""
    root = _instructed(_repo(tmp_path), always=UNSCOPED_RULE)
    _git_init(root)
    subprocess.run(("git", "branch", "-M", "main"), cwd=root, check=True, capture_output=True)
    (root / ".claude" / "rules" / "always.md").write_text(SCOPED_RULE, encoding="utf-8")

    report = doc_check.analyze(root)

    assert report.resident is not None
    assert report.resident.growth == -3
    assert report.advisories == []
    assert "3 fewer than main" in doc_check.format_check(report)


def test_a_trim_that_pays_for_an_addition_is_an_advisory_at_net_zero(tmp_path: Path) -> None:
    """The outcome a line limit would have forced, arriving without a limit.

    Growth and shrinkage sum into one total, so resident text cut to make room
    for an addition reports as no growth at all and the diff reads as free.
    """
    root = _instructed(_repo(tmp_path), always=UNSCOPED_RULE)
    _git_init(root)
    subprocess.run(("git", "branch", "-M", "main"), cwd=root, check=True, capture_output=True)
    (root / "CLAUDE.md").write_text("# Rules\n\nOne.\nTwo.\nThree.\n", encoding="utf-8")
    (root / ".claude" / "rules" / "always.md").write_text("# Unscoped\n", encoding="utf-8")

    report = doc_check.analyze(root)

    assert report.resident is not None
    assert report.resident.growth == 0
    assert not any("grew 0 lines" in m for m in report.advisories)
    assert any("both grew and shrank" in m for m in report.advisories)
    assert any("PL-BKQW" in m for m in report.advisories)
    assert report.errors == []


def test_growth_alongside_a_trim_raises_both_advisories(tmp_path: Path) -> None:
    """The trim is a finding on its own, not something the growth line covers."""
    root = _instructed(_repo(tmp_path), always=UNSCOPED_RULE)
    _git_init(root)
    subprocess.run(("git", "branch", "-M", "main"), cwd=root, check=True, capture_output=True)
    (root / "CLAUDE.md").write_text("# Rules\n\n" + "Line.\n" * 8, encoding="utf-8")
    (root / ".claude" / "rules" / "always.md").write_text("# Unscoped\n", encoding="utf-8")

    report = doc_check.analyze(root)

    assert report.resident is not None
    assert report.resident.growth == 5
    assert any("resident instructions grew 5 lines" in m for m in report.advisories)
    assert any("both grew and shrank" in m for m in report.advisories)


def test_an_unchanged_total_is_reported_as_unchanged(tmp_path: Path) -> None:
    root = _instructed(_repo(tmp_path))
    _git_init(root)
    subprocess.run(("git", "branch", "-M", "main"), cwd=root, check=True, capture_output=True)

    report = doc_check.analyze(root)

    assert report.advisories == []
    assert "unchanged against main" in doc_check.format_check(report)


def test_a_checkout_with_no_default_branch_still_reports_the_total(tmp_path: Path) -> None:
    """The comparison goes missing, not the measurement, and it says so."""
    root = _instructed(_repo(tmp_path))

    report = doc_check.analyze(root)

    assert report.resident is not None
    assert report.resident.total == 3
    assert report.resident.growth is None
    assert report.advisories == []
    assert "no default branch here to compare against" in doc_check.format_check(report)


def test_the_total_is_printed_even_when_nothing_else_fired(tmp_path: Path) -> None:
    report = doc_check.analyze(_instructed(_repo(tmp_path)))
    printed = doc_check.format_check(report)

    assert "resident instructions: 3 lines loaded at launch" in printed
    assert "all resolve" in printed


def test_this_repository_reports_its_own_resident_total() -> None:
    """The real tree, not only a fixture: the number has to be about this file."""
    root = Path(doc_check.__file__).resolve().parent.parent
    resident = doc_check.analyze(root).resident

    assert resident is not None
    assert dict(resident.files)["CLAUDE.md"] > 0
    assert ".claude/rules/expert-review.md" not in dict(resident.files)
    assert ".claude/rules/instruction-writing.md" in dict(resident.files)


# --- math delimiters --------------------------------------------------------


def _math_errors(root: Path, name: str, body: str) -> list[str]:
    """Errors from the math rules alone, for one markdown file added to a repo."""
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    report = doc_check.Report()
    doc_check.check_math_delimiters(root, report)
    return report.errors


def test_math_latex_inline_delimiters_are_reported(tmp_path: Path) -> None:
    r"""`\(t\)` reaches a GitHub page as the literal text `(t)`.

    CommonMark escapes the backslash before any math parser runs, so nothing
    raises and nothing looks wrong in the source - the rendered page simply
    shows parentheses where a symbol belongs.
    """
    errors = _math_errors(
        tmp_path / "repo", "docs/NOTE.md", "The step \\(\\Delta t\\) is explicit.\n"
    )

    assert len(errors) == 2
    assert all("docs/NOTE.md:1" in error for error in errors)
    assert any("does not render" in error for error in errors)


def test_math_latex_block_delimiters_are_reported(tmp_path: Path) -> None:
    errors = _math_errors(tmp_path / "repo", "docs/NOTE.md", "\\[F = 0.02\\]\n")

    assert len(errors) == 2


def test_math_github_inline_syntax_is_quiet(tmp_path: Path) -> None:
    """The correct form must not fire: a checker that flags good writing gets disabled."""
    body = "The step $`\\Delta t`$ is explicit, and $`F_D`$ is the dialed fraction.\n"

    assert _math_errors(tmp_path / "repo", "docs/NOTE.md", body) == []


def test_math_expression_split_across_a_line_break_is_reported(tmp_path: Path) -> None:
    """Inline math is parsed within a line, so a reflowed span renders as text.

    This is the half of the defect that outlives the conversion: the delimiters
    are right, and a later paragraph rewrap breaks the render silently.
    """
    body = "Arterial blood holds no independent state: $`F_a \\equiv\nF_A`$ here.\n"

    errors = _math_errors(tmp_path / "repo", "docs/NOTE.md", body)

    assert len(errors) == 2
    assert "docs/NOTE.md:1" in errors[0]
    assert "docs/NOTE.md:2" in errors[1]
    assert all("split across a line break" in error for error in errors)


def test_math_broken_syntax_quoted_in_a_code_span_is_quiet(tmp_path: Path) -> None:
    """Writing *about* the defect is not committing it.

    The item recording this work quotes the broken delimiters a dozen times;
    a rule that cannot tell a quotation from a use would have to be deleted.
    """
    body = "Markdown wrote inline math as `` `\\(...\\)` ``, which GitHub ignores.\n"

    assert _math_errors(tmp_path / "repo", "docs/NOTE.md", body) == []


def test_math_fenced_sample_is_quiet(tmp_path: Path) -> None:
    body = "Before:\n\n```text\n\\(F_A\\) and \\[F = 0.02\\]\n```\n"

    assert _math_errors(tmp_path / "repo", "docs/NOTE.md", body) == []


def test_math_shell_snippet_is_not_an_unclosed_expression(tmp_path: Path) -> None:
    """A backtick against a dollar is ordinary in shell, and common in the queue."""
    body = 'Comparing `"$upstream..HEAD"` against a deleted tip overcounts.\n'

    assert _math_errors(tmp_path / "repo", "docs/NOTE.md", body) == []


def test_math_display_fence_is_quiet(tmp_path: Path) -> None:
    """`$$` blocks are the supported block syntax and must not be touched."""
    body = "The circuit amount is:\n\n$$\nM_C = V_C F_C\n$$\n"

    assert _math_errors(tmp_path / "repo", "docs/NOTE.md", body) == []


def test_math_markdown_outside_the_documentation_globs_is_read(tmp_path: Path) -> None:
    """Rendering is not a claim held to the tree, so every markdown file counts.

    Seven queue items had copied the broken delimiters out of `docs/MODEL.md`,
    and `docs/items/` is not in `DOC_GLOBS`.
    """
    errors = _math_errors(tmp_path / "repo", "docs/items/PL-0000-demo.md", "Rate \\(Q_i\\).\n")

    assert len(errors) == 2
    assert all("docs/items/PL-0000-demo.md" in error for error in errors)


# --- frozen-list counts -----------------------------------------------------


GATE_SECTION = """## Next milestone: v0.4.0 - the teachable case

### Goal

To be teachable.

### Required scope

- Something.

### Debt gate: the frozen list

**Frozen 2026-08-25, the day this milestone was scoped, at two entries.**

Two entries were added later, per the note beneath this list.

*The loop is visibly broken without these — two entries:*

- PL-BBBB (S) The first thing
- PL-CCCC (S) The second thing

*Presentation safety — `safety`-classed, and the one entry that is not:*

*Stops new debt being introduced — three entries:*

- PL-DDDD (S) The third thing
- PL-FFFF **and PL-GGGG** (S) One problem under two ids
- PL-HHHH (S) The fifth thing

### Definition of done

- Everything above is done.

"""

GATE_ROADMAP = ROADMAP.replace("## Planned milestones", GATE_SECTION + "## Planned milestones")
VERSIONED_GATE_ROADMAP = VERSIONED_ROADMAP.replace(
    "## Planned milestones", GATE_SECTION + "## Planned milestones"
)


def _gate_errors(tmp_path: Path, roadmap: str = GATE_ROADMAP) -> list[str]:
    return [error for error in _errors(_repo(tmp_path, roadmap=roadmap)) if "frozen list" in error]


def test_the_gate_count_check_is_quiet_when_every_number_agrees(tmp_path: Path) -> None:
    assert _gate_errors(tmp_path) == []


def test_a_gate_group_heading_that_miscounts_the_entries_under_it_is_reported(
    tmp_path: Path,
) -> None:
    """The failure has to name both numbers, or it cannot be acted on."""
    roadmap = GATE_ROADMAP.replace("— three entries:*", "— four entries:*")

    errors = _gate_errors(tmp_path, roadmap)

    assert any("says 4 entries, but 3 follow it" in error for error in errors)


def test_a_gate_whose_group_counts_do_not_sum_to_the_list_is_reported(tmp_path: Path) -> None:
    """Every heading can be right about itself while the list has outgrown them.

    An entry admitted above the first group heading belongs to no group, so
    each heading still counts what follows it correctly and the total no
    longer matches.
    """
    roadmap = GATE_ROADMAP.replace(
        "*The loop is visibly broken without these — two entries:*",
        "- PL-JJJJ (S) Admitted into no group\n\n"
        "*The loop is visibly broken without these — two entries:*",
    )

    errors = _gate_errors(tmp_path, roadmap)

    assert any("count 5 entries between them, but the list holds 6" in error for error in errors)


def test_a_gate_heading_that_miscounts_item_ids_is_reported(tmp_path: Path) -> None:
    """Entries and ids are different numbers: one entry may hold two ids."""
    roadmap = GATE_ROADMAP.replace(
        "*Stops new debt being introduced — three entries:*",
        "*Stops new debt being introduced — three entries, three item ids:*",
    )

    errors = _gate_errors(tmp_path, roadmap)

    assert any("says 3 item ids, but the entries under it hold 4" in error for error in errors)


def test_a_stale_gate_count_in_the_version_table_is_reported(tmp_path: Path) -> None:
    roadmap = VERSIONED_GATE_ROADMAP.replace(
        "| v0.3.0 | Planned / scoped | Not out yet. |",
        "| v0.3.0 | Planned / scoped | Not out yet. |\n"
        "| v0.4.0 | Planned / scoped | Nine entries of teachable case. |",
    )

    errors = _gate_errors(tmp_path, roadmap)

    assert any(
        "the version table row for v0.4.0 says 9 entries, but its frozen list holds 5" in error
        for error in errors
    )


def test_a_stale_gate_count_in_the_timeline_is_reported(tmp_path: Path) -> None:
    roadmap = GATE_ROADMAP.replace(
        "| 2 | **v0.4.0 — the teachable case** | Scoped below. | 5 M |",
        "| 2 | **v0.4.0 — the teachable case** | Its own list of nine entries. | 5 M |",
    )

    errors = _gate_errors(tmp_path, roadmap)

    assert any(
        "the timeline row for v0.4.0 says 9 entries, but its frozen list holds 5" in error
        for error in errors
    )


def test_a_table_row_naming_another_release_gate_count_is_left_alone(tmp_path: Path) -> None:
    """A row may describe a list recorded under a different release.

    v0.3.0's timeline row says what Gate 0 holds, and Gate 0 is recorded under
    v0.4.0. Only the row's own naming cell decides which list it is claiming
    something about, so the number here is not read as v0.3.0's - which
    records no list at all - nor as v0.4.0's.
    """
    roadmap = GATE_ROADMAP.replace(
        "| 1 | **v0.3.0 — the foundation** | Gate 0. | 2 M |",
        "| 1 | **v0.3.0 — the foundation** | The nine entries of v0.4.0's gate. | 2 M |",
    )

    assert _gate_errors(tmp_path, roadmap) == []


def test_prose_about_some_entries_is_not_read_as_a_gate_count_heading(tmp_path: Path) -> None:
    """The count has to sit past the dash, where a heading puts it.

    "Two entries were added later" is a sentence about the list, not a heading
    over two of its entries, and reading it as one would report a list that is
    correct.
    """
    assert not any("says 2 entries" in error for error in _gate_errors(tmp_path))


def test_a_group_heading_stating_no_gate_count_is_passed_over(tmp_path: Path) -> None:
    """Grouping the list without claiming a size is a shape the file uses."""
    errors = _gate_errors(tmp_path)

    assert errors == []
    assert "Presentation safety" in GATE_ROADMAP


def test_a_gate_count_written_in_digits_is_read(tmp_path: Path) -> None:
    """The file writes counts both ways; which one was reached for means nothing."""
    roadmap = GATE_ROADMAP.replace("— three entries:*", "— 4 entries:*")

    errors = _gate_errors(tmp_path, roadmap)

    assert any("says 4 entries, but 3 follow it" in error for error in errors)
