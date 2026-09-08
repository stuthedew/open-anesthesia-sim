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
MARKER = "<!-- provenance: data/agents/demo.json blood_gas_partition_coefficient = {} -->"

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
        # A marked prose value, so the clean fixture is clean by the prose
        # check too - and so that every test overriding `model=` starts from
        # documentation that satisfies it.
        "The demo agent's blood:gas coefficient is 0.5.",
        MARKER.format("0.5"),
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

SOURCE = {
    "citation": "Nobody. A paper.",
    "url": "https://example.invalid/",
    "tier": "primary",
    "adopted": True,
    "note": "n",
}

DATA = {
    "schema_version": 2,
    "id": "demo",
    "display_name": "Demo",
    "blood_gas_partition_coefficient": 0.5,
    "tissue_gas_partition_coefficients": {"fat": 2.0},
    "sources": [SOURCE],
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


# --- source tiers -----------------------------------------------------------


def _sourced(*entries: dict[str, object]) -> dict[str, object]:
    """The clean data file with its `sources` array replaced."""
    return dict(DATA) | {"sources": list(entries)}


def test_clean_data_file_declares_its_tiers_quietly(tmp_path: Path) -> None:
    assert not any("tier" in e for e in _errors(_repo(tmp_path)))


def test_source_with_no_tier_is_an_error(tmp_path: Path) -> None:
    entry = {key: value for key, value in SOURCE.items() if key != "tier"}
    root = _repo(tmp_path, data=_sourced(entry))
    assert any("declares tier None" in e for e in _errors(root))


def test_source_tier_outside_the_vocabulary_is_an_error(tmp_path: Path) -> None:
    root = _repo(tmp_path, data=_sourced(dict(SOURCE) | {"tier": "tier 1"}))
    errors = _errors(root)
    assert any("declares tier 'tier 1'" in e for e in errors)
    assert any("Source hierarchy" in e for e in errors)


def test_the_error_names_the_entry_by_its_citation(tmp_path: Path) -> None:
    """An index alone does not find the entry in a file of eleven citations."""
    root = _repo(tmp_path, data=_sourced(dict(SOURCE) | {"tier": "made up"}))
    assert any("sources[0] (Nobody. A paper.)" in e for e in _errors(root))


def test_source_with_no_adopted_flag_is_an_error(tmp_path: Path) -> None:
    entry = {key: value for key, value in SOURCE.items() if key != "adopted"}
    root = _repo(tmp_path, data=_sourced(entry))
    assert any("declares adopted None" in e for e in _errors(root))


def test_a_string_adopted_flag_is_an_error(tmp_path: Path) -> None:
    """`"adopted": "false"` is truthy, so reading it loosely inverts the claim."""
    root = _repo(tmp_path, data=_sourced(dict(SOURCE) | {"adopted": "false"}))
    assert any("declares adopted 'false'" in e for e in _errors(root))


def test_an_unadopted_primary_does_not_source_the_file(tmp_path: Path) -> None:
    """The whole reason the tier is not enough on its own.

    Every agent file in this repository cites primary measurements it has
    explicitly not adopted. A rule reading the tier alone would call all four
    data files primary-sourced while every stored coefficient in them came
    from Gas Man - `docs/MODEL.md` § "Source hierarchy", second rule.
    """
    root = _repo(tmp_path, data=_sourced(dict(SOURCE) | {"adopted": False}))
    assert any("no `sources` entry is both tier 'primary' and adopted" in e for e in _errors(root))


def test_a_tier_three_only_file_with_no_gap_is_an_error(tmp_path: Path) -> None:
    entry = dict(SOURCE) | {"tier": "reference-implementation", "adopted": True}
    root = _repo(tmp_path, data=_sourced(entry))
    assert any("records no `provenance_gap`" in e for e in _errors(root))


def test_a_recorded_gap_satisfies_the_rule(tmp_path: Path) -> None:
    entry = dict(SOURCE) | {"tier": "reference-implementation", "adopted": True}
    data = _sourced(entry) | {"provenance_gap": "No primary source has been adopted."}
    assert not any("provenance_gap" in e for e in _errors(_repo(tmp_path, data=data)))


def test_an_empty_gap_is_an_error(tmp_path: Path) -> None:
    entry = dict(SOURCE) | {"tier": "reference-implementation", "adopted": True}
    data = _sourced(entry) | {"provenance_gap": "   "}
    assert any("is not a nonempty string" in e for e in _errors(_repo(tmp_path, data=data)))


def test_a_file_with_no_sources_at_all_is_an_error(tmp_path: Path) -> None:
    root = _repo(tmp_path, data=dict(DATA) | {"sources": []})
    assert any("declares no `sources` array" in e for e in _errors(root))


def test_provenance_gap_is_not_treated_as_a_parameter(tmp_path: Path) -> None:
    """It is prose beside the citations, so the provenance table owes it no row."""
    data = dict(DATA) | {"provenance_gap": "Recorded here, documented nowhere else."}
    assert not any("no provenance row" in e for e in _errors(_repo(tmp_path, data=data)))


# --- prose provenance -------------------------------------------------------

DERIVED = "<!-- derived: {} from data/agents/demo.json blood_gas_partition_coefficient = {} -->"


def _model_with(*prose: str) -> str:
    """`MODEL`, with one more marked paragraph under "Known limitations"."""
    return MODEL + "\n" + "\n".join(prose) + "\n"


def test_a_prose_value_that_disagrees_with_its_data_file_is_an_error(tmp_path: Path) -> None:
    """The failure the check exists for: the table was updated and prose was not."""
    root = _repo(tmp_path, model=_model_with("The coefficient is 0.9.", MARKER.format("0.9")))

    assert any(
        "states blood_gas_partition_coefficient = 0.9" in error and "holds 0.5" in error
        for error in _errors(root)
    )


def test_prose_reworded_without_its_marker_is_an_error(tmp_path: Path) -> None:
    """The other direction: the data file is fine and the sentence moved away.

    Without this the marker degrades into a comment nobody has to keep true,
    and the check would go on passing while pointing at a paragraph that no
    longer restates anything.
    """
    root = _repo(tmp_path, model=_model_with("The coefficient is 0.9.", MARKER.format("0.5")))

    assert any("is not in it" in error for error in _errors(root))


def test_a_derived_figure_says_to_recompute_when_an_input_moves(tmp_path: Path) -> None:
    """The half no single-key search would surface, and the reason for two kinds.

    Nothing holds the derived figure, so the check reports that what it was
    computed from has moved and stops there. Recomputing it is judgment about
    units and rounding, and a tool guessing at that would be confidently wrong
    in a document a clinician reads.
    """
    root = _repo(
        tmp_path,
        model=_model_with("Equilibration takes 4.0 units.", DERIVED.format("4.0 units", "0.9")),
    )

    assert any(
        "4.0 units was computed from" in error and "recompute" in error for error in _errors(root)
    )


def test_a_correct_derived_figure_is_left_alone(tmp_path: Path) -> None:
    root = _repo(
        tmp_path,
        model=_model_with("Equilibration takes 12.5 units.", DERIVED.format("12.5 units", "0.5")),
    )

    assert _errors(root) == []


def test_a_marker_shown_inside_a_code_fence_is_not_read_as_a_claim(tmp_path: Path) -> None:
    """The document explains the convention by printing one; that is not a claim.

    Reading an example as a claim would force every marker in the prose that
    documents the format to be coincidentally true of the shipped data.
    """
    root = _repo(
        tmp_path,
        model=_model_with("A marker looks like this:", "", "```text", MARKER.format("0.9"), "```"),
    )

    assert _errors(root) == []


def test_a_marker_naming_a_key_the_file_does_not_hold_is_an_error(tmp_path: Path) -> None:
    root = _repo(
        tmp_path,
        model=_model_with(
            "The coefficient is 0.5.",
            "<!-- provenance: data/agents/demo.json no_such_key = 0.5 -->",
        ),
    )

    assert any("does not hold as a number" in error for error in _errors(root))


def test_a_model_with_no_markers_at_all_is_an_error(tmp_path: Path) -> None:
    """Silence from a check with nothing to check reads exactly like a pass."""
    root = _repo(tmp_path, model=MODEL.replace(MARKER.format("0.5"), ""))

    assert any("this check has gone blind" in error for error in _errors(root))


def test_each_of_several_markers_on_one_paragraph_reads_that_paragraph(tmp_path: Path) -> None:
    """One sentence often restates values from several files, so markers stack.

    Walking back only to the nearest one handed every marker above it an empty
    paragraph, which contains no numbers and so reported the prose as missing
    the value - or, had the comparison been the other way, passed silently.
    """
    root = _repo(
        tmp_path,
        model=_model_with(
            "The coefficient is 0.5 and the fat coefficient is 2.0.",
            MARKER.format("0.5"),
            "<!-- provenance: data/agents/demo.json "
            "tissue_gas_partition_coefficients.fat = 2.0 -->",
        ),
    )

    assert _errors(root) == []


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


# --- wrapped citations and bold markers -------------------------------------


def _wrapped(readme_line: str) -> str:
    return "# Demo\n\n" + readme_line + "\n"


def test_a_cited_section_title_that_wraps_across_lines_is_checked(tmp_path: Path) -> None:
    """Prose hard-wraps, so a long title breaks across a source line.

    While the pattern quoted as `[^"\n]+` such a citation matched nothing and
    was silently unexamined - the check reported success over text it had not
    read, which is worse than reporting a gap.
    """
    model = MODEL.replace("## Known limitations", "## Known limitations of the coupled model")
    readme = _wrapped('See "Renamed limitations of the coupled\nmodel" for what it omits.')
    root = _repo(tmp_path, model=model, readme=readme)
    assert any(
        'cites section "Renamed limitations of the coupled model"' in e for e in _errors(root)
    )


def test_a_wrapped_citation_that_resolves_is_not_an_error(tmp_path: Path) -> None:
    model = MODEL.replace("## Known limitations", "## Known limitations of the coupled model")
    readme = _wrapped('See "Known limitations of the coupled\nmodel" for what it omits.')
    assert not any(
        "cites section" in e for e in _errors(_repo(tmp_path, model=model, readme=readme))
    )


def test_a_bold_marker_is_a_citable_section_title(tmp_path: Path) -> None:
    """This project subdivides documents with `**Bold.**`, and cites them by name."""
    model = MODEL + "\n**What the model omits.** Everything else.\n"
    readme = _wrapped('See "What the model omits" for what it leaves out.')
    assert not any(
        "cites section" in e for e in _errors(_repo(tmp_path, model=model, readme=readme))
    )


def test_a_bullet_led_bold_marker_is_a_citable_section_title(tmp_path: Path) -> None:
    model = MODEL + "\n- **What the model omits.** Everything else.\n"
    readme = _wrapped('See "What the model omits" for what it leaves out.')
    assert not any(
        "cites section" in e for e in _errors(_repo(tmp_path, model=model, readme=readme))
    )


# --- quoted sources: item briefs and docstrings ------------------------------


def _item(root: Path, name: str, body: str) -> None:
    items = root / "docs" / "items"
    items.mkdir(parents=True, exist_ok=True)
    (items / f"{name}.md").write_text(body, encoding="utf-8")


def _docstringed(root: Path, body: str) -> None:
    module = root / "src" / "anesthesia_sim" / "core" / "thing.py"
    module.write_text(f'''"""{body}"""\n''', encoding="utf-8")


def test_citation_in_an_item_brief_is_held_to_the_document_it_names(tmp_path: Path) -> None:
    """The queue is where most of this project's prose is, and it was unread."""
    root = _repo(tmp_path)
    _item(root, "PL-0000-demo", '**Context.** `docs/MODEL.md`, "A thread that was deleted".\n')
    assert any(
        'PL-0000-demo.md:1: quotes docs/MODEL.md as "A thread that was deleted"' in e
        for e in _errors(root)
    )


def test_citation_in_an_item_brief_that_resolves_is_not_an_error(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    _item(root, "PL-0000-demo", '**Context.** `docs/MODEL.md`, "Known limitations".\n')
    assert not any("quotes docs/MODEL.md" in e for e in _errors(root))


def test_citation_in_a_source_docstring_is_held_to_the_document_it_names(tmp_path: Path) -> None:
    """A contributor reading the class is sent somewhere; it has to still answer."""
    root = _repo(tmp_path)
    _docstringed(root, 'See `docs/MODEL.md`, "A thread that was deleted".')
    assert any("thing.py:1: quotes docs/MODEL.md" in e for e in _errors(root))


def test_a_docstring_citation_is_reported_on_its_own_line(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    module = root / "src" / "anesthesia_sim" / "core" / "thing.py"
    module.write_text(
        '''X = 1\n\n\ndef f() -> None:\n    """See `docs/MODEL.md`, "A deleted thread"."""\n''',
        encoding="utf-8",
    )
    assert any("thing.py:5: quotes docs/MODEL.md" in e for e in _errors(root))


def test_a_quoted_source_inside_a_fence_is_not_a_citation(tmp_path: Path) -> None:
    """An item showing a broken citation must not be an error for showing it."""
    root = _repo(tmp_path)
    _item(
        root,
        "PL-0000-demo",
        'It ended with\n\n```text\n`docs/MODEL.md`, "A thread that was deleted"\n```\n',
    )
    assert not any("quotes docs/MODEL.md" in e for e in _errors(root))


def test_an_indented_fence_hides_a_quoted_source_too(tmp_path: Path) -> None:
    """A fence under a list item is indented to sit inside it."""
    root = _repo(tmp_path)
    _item(
        root,
        "PL-0000-demo",
        '- It ended with\n\n  ```text\n  `docs/MODEL.md`, "A thread that was deleted"\n  ```\n',
    )
    assert not any("quotes docs/MODEL.md" in e for e in _errors(root))


def test_an_elided_quotation_is_not_checked(tmp_path: Path) -> None:
    """`"a ... b"` cannot be found verbatim; declining beats a false error."""
    root = _repo(tmp_path)
    _item(root, "PL-0000-demo", '`docs/MODEL.md`, "Known ... limitations".\n')
    assert not any("quotes docs/MODEL.md" in e for e in _errors(root))


def test_a_quotation_differing_only_in_dash_style_resolves(tmp_path: Path) -> None:
    """This project writes both `-` and an em dash for the same dash."""
    model = MODEL + "\nThe step is fixed - and stated once.\n"
    root = _repo(tmp_path, model=model)
    _item(root, "PL-0000-demo", '`docs/MODEL.md`, "The step is fixed \u2014 and stated once".\n')
    assert not any("quotes docs/MODEL.md" in e for e in _errors(root))


def test_a_quotation_recapitalised_to_open_a_sentence_resolves(tmp_path: Path) -> None:
    model = MODEL + "\nthe step is fixed and stated once.\n"
    root = _repo(tmp_path, model=model)
    _item(root, "PL-0000-demo", '`docs/MODEL.md`, "The step is fixed and stated once".\n')
    assert not any("quotes docs/MODEL.md" in e for e in _errors(root))


def test_a_quoted_sentence_that_is_not_a_heading_still_resolves(tmp_path: Path) -> None:
    """Whether the quotation is a title is a question this check does not ask."""
    root = _repo(tmp_path)
    _item(root, "PL-0000-demo", '`docs/MODEL.md`, "blood:gas coefficient is 0.5".\n')
    assert not any("quotes docs/MODEL.md" in e for e in _errors(root))


def test_a_citation_naming_a_document_that_does_not_exist_is_an_error(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    _item(root, "PL-0000-demo", '`docs/GONE.md`, "Anything at all".\n')
    assert any("quotes docs/GONE.md, which does not exist" in e for e in _errors(root))


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


# --- which terms enter the candidate search, and how they are matched -------
#
# `candidates` is judged by the ratio, not by recall alone: a list that is
# mostly prose trains a session to skim it, and the genuine lines get skimmed
# with them. So each rule below has a test that the noise is gone and a test
# that the signal survived it.

# Line 6 uses two identifier names in their English sense; line 7 names one of
# them as code. Only line 7 is a candidate.
PROSE_README = README + (
    "\nThe run does not settle until the compartments determine equilibrium.\n"
    "The `settle` helper is what decides that.\n"
)


def test_candidates_does_not_report_an_identifier_used_as_ordinary_prose(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """One function named `settle` returned 30 lines of unrelated prose."""
    root = _repo(tmp_path, readme=PROSE_README)
    _git_init(root)

    module = root / "src" / "anesthesia_sim" / "core" / "thing.py"
    module.write_text(
        "def settle() -> None:\n    return None\n\n\ndef mine() -> None:\n    return None\n",
        encoding="utf-8",
    )

    assert doc_check.main(["candidates", "--root", str(root), "--base", "HEAD"]) == 0
    output = capsys.readouterr().out
    # The sentence using "settle" as a verb, and "determine" as a word that
    # merely contains `mine`, are both left out.
    assert "README.md:6" not in output
    # ...and the tool says which terms it narrowed, so a reader who suspects a
    # miss knows the word to grep for rather than distrusting the whole list.
    assert "searched only where a line marks it as code" in output
    assert "mine" in output


def test_candidates_reports_a_common_word_identifier_where_a_line_marks_it_as_code(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The half that must survive the fix: a renamed symbol named in prose."""
    root = _repo(tmp_path, readme=PROSE_README)
    _git_init(root)

    module = root / "src" / "anesthesia_sim" / "core" / "thing.py"
    module.write_text("def settle() -> None:\n    return None\n", encoding="utf-8")

    assert doc_check.main(["candidates", "--root", str(root), "--base", "HEAD"]) == 0
    assert "README.md:7" in capsys.readouterr().out


def test_candidates_reports_a_distinctive_identifier_without_backticks(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`snake_case` cannot be written by accident, so it needs no marking."""
    readme = README + "\nThe settle_run helper decides when a run has finished.\n"
    root = _repo(tmp_path, readme=readme)
    _git_init(root)

    module = root / "src" / "anesthesia_sim" / "core" / "thing.py"
    module.write_text("def settle_run() -> None:\n    return None\n", encoding="utf-8")

    assert doc_check.main(["candidates", "--root", str(root), "--base", "HEAD"]) == 0
    output = capsys.readouterr().out
    assert "README.md:6  (settle_run)" in output
    # `thing`, the changed file's stem, is the only term narrowed to code
    # context; the snake_case name was matched as a bare word.
    assert "as code: thing." in output


def test_candidates_does_not_read_a_prose_line_beginning_class_as_a_definition(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A wrapped sentence is not a declaration, however it happens to start."""
    root = _repo(tmp_path, readme=README + "\nWhat the table describes is the stored value.\n")
    note = root / "docs" / "items" / "PL-0001-a-note.md"
    note.parent.mkdir(parents=True, exist_ok=True)
    note.write_text("A note.\n", encoding="utf-8")
    _git_init(root)

    note.write_text(
        "The item's safety\nclass describes the deliverable, not the subject.\n", encoding="utf-8"
    )

    assert doc_check.main(["candidates", "--root", str(root), "--base", "HEAD"]) == 0
    # `describes` never became a term, so it is neither a hit nor a narrowing.
    assert "describes" not in capsys.readouterr().out


def test_candidates_takes_a_json_key_only_from_a_json_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A `"key":` line in a changed markdown file is somebody's example."""
    root = _repo(tmp_path)
    note = root / "docs" / "items" / "PL-0002-a-note.md"
    note.parent.mkdir(parents=True, exist_ok=True)
    note.write_text("A note.\n", encoding="utf-8")
    _git_init(root)

    note.write_text(
        '```json\n{\n    "tissue_gas_partition_coefficients": {"fat": 3.0}\n}\n```\n',
        encoding="utf-8",
    )
    data = root / "src" / "anesthesia_sim" / "data" / "agents" / "demo.json"
    data.write_text(
        json.dumps({**DATA, "blood_gas_partition_coefficient": 0.6}, indent=4), encoding="utf-8"
    )

    assert doc_check.main(["candidates", "--root", str(root), "--base", "HEAD"]) == 0
    output = capsys.readouterr().out
    # The key the data file declares is a term; the same shape quoted in the
    # note is not, so only the data file draws the provenance row.
    assert "(blood_gas_partition_coefficient)" in output
    assert "tissue_gas_partition_coefficients" not in output


def test_candidates_summarizes_a_term_too_common_to_be_a_shortlist(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Eighty lines of `docket check` for one settings key is not a shortlist."""
    roadmap = ROADMAP + "".join(f"- `check` again, line {n}.\n" for n in range(12))
    root = _repo(tmp_path, roadmap=roadmap)
    _git_init(root)

    module = root / "src" / "anesthesia_sim" / "core" / "thing.py"
    module.write_text("def check() -> None:\n    return None\n", encoding="utf-8")

    assert doc_check.main(["candidates", "--root", str(root), "--base", "HEAD"]) == 0
    output = capsys.readouterr().out
    assert "(check) matches 12 lines marked as code" in output
    assert "ROADMAP.md:" not in output


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
    """PL-J3ZK's failure: a release whose span nothing can map back to a version.

    This is also what makes the baseline's silence below safe rather than a
    hole: the newest release is skipped, not forgiven. Once a newer one lands
    it becomes an ordinary completed row with no tag and is reported here -
    which is the moment the gap starts to matter, since `git describe
    --contains` only fails after history has moved past it.
    """
    errors = _errors(_tagged(tmp_path, "v0.2.5"))

    assert any("v0.2.4 is marked completed but git holds no tag" in message for message in errors)


def test_the_release_being_cut_is_silent(tmp_path: Path) -> None:
    """Not an error, and no longer an advisory either.

    Not an error because the tag lands on the merge commit, so the newest
    version has none yet, and failing it would turn `make check` red on every
    release branch - the failure PL-8HJ2 removed.

    Not an advisory because it could not tell a release that was never tagged
    from one tagged since this checkout last fetched, and it fired on a
    correctly tagged repository (PL-R7C0). A checkout holding tags for the
    older releases but not the newest is neither an empty tag set nor a
    shallow clone, so neither existing silence covered it.
    """
    root = _tagged(tmp_path, "v0.2.4")

    assert _errors(root) == []
    assert _advisories(root) == []


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


# --- the coverage gate, held identical between the Makefile and CI -----------
#
# Both files carry a comment saying the invocation has to stay the same, and
# nothing checked it. They are the local gate and the merge gate, so a drift
# means a session and CI stop asking the same question - silently, in the check
# that holds `core/` at 100% (`PL-D3M2`).

GATE = "uv run pytest -n auto --cov=demo.core --cov-branch --cov-fail-under=100"


def _gated(root: Path, *, make: str | None = GATE, ci: str | None = GATE) -> Path:
    """A repository whose Makefile and workflow each run a coverage gate."""
    recipe = f"\t{make}\n" if make else "\ttrue\n"
    (root / "Makefile").write_text(f".PHONY: check\ncheck:\n{recipe}", encoding="utf-8")
    steps = "      - run: bin/runner check\n"
    if ci:
        steps += f"      - run: {ci}\n"
    _with_workflow(
        root,
        "name: quality\n\non: [push, pull_request]\n\njobs:\n  checks:\n"
        "    runs-on: ubuntu-latest\n    steps:\n"
        "      - uses: actions/checkout@v7.0.1\n" + steps,
    )
    return root


def test_the_same_coverage_gate_in_both_places_is_quiet(tmp_path: Path) -> None:
    assert _errors(_gated(_repo(tmp_path))) == []


def test_a_coverage_gate_that_drifted_between_them_is_an_error(tmp_path: Path) -> None:
    # The failure this exists for: one side gains a flag and the other does
    # not, so the local gate and the merge gate stop matching without saying so.
    root = _gated(_repo(tmp_path), make=GATE.replace(" -n auto", ""))

    errors = _errors(root)

    assert any("the coverage gate differs between the Makefile and CI" in m for m in errors)


#: The same gate spelled for each file: Make doubles `$` in a recipe to pass one
#: through to the shell, so a command carrying a shell substitution genuinely
#: differs by that one character while being the same command.
SUBSTITUTED_CI = (
    "uv run pytest -n $(python3 -c 'import os; print(os.cpu_count() * 2)') "
    "--dist worksteal --cov=demo.core --cov-branch --cov-fail-under=100"
)
SUBSTITUTED_MAKE = SUBSTITUTED_CI.replace("$(", "$$(")


def test_makes_doubled_dollar_is_not_read_as_a_drift(tmp_path: Path) -> None:
    """The escape is Make's, not a difference in what runs (`PL-VZ8P`).

    Before this, moving the worker count from `-n auto` to a shell substitution
    failed the check on the one character Make requires - an error about the two
    gates disagreeing when they agree exactly.
    """
    root = _gated(_repo(tmp_path), make=SUBSTITUTED_MAKE, ci=SUBSTITUTED_CI)

    assert _errors(root) == []


def test_a_real_drift_inside_a_substituted_command_is_still_caught(tmp_path: Path) -> None:
    """The normalization must not become a way for drift to hide.

    Only `$$` collapses; everything else still compares exactly, so a threshold
    that moved on one side alone is an error however the line is spelled.
    """
    root = _gated(
        _repo(tmp_path),
        make=SUBSTITUTED_MAKE,
        ci=SUBSTITUTED_CI.replace("--cov-fail-under=100", "--cov-fail-under=99"),
    )

    assert any("the coverage gate differs between the Makefile and CI" in m for m in _errors(root))


def test_the_drift_error_names_both_commands(tmp_path: Path) -> None:
    # A reader has to see which side changed; naming only the rule would make
    # them diff two files by hand to find out.
    root = _gated(_repo(tmp_path), make=GATE.replace(" -n auto", ""))

    joined = " ".join(_errors(root))

    assert "Makefile:" in joined
    assert "quality.yml:" in joined


def test_a_gate_ci_runs_and_the_makefile_does_not_is_an_error(tmp_path: Path) -> None:
    # The more serious half, and it reads differently: this is not two commands
    # disagreeing, it is one gate being absent where it was promised.
    root = _gated(_repo(tmp_path), make=None)

    assert any("only one of the two gates gates coverage" in m for m in _errors(root))


def test_a_gate_the_makefile_runs_and_ci_does_not_is_an_error(tmp_path: Path) -> None:
    # The direction that matters most: green locally, ungated on merge.
    root = _gated(_repo(tmp_path), ci=None)

    assert any("only one of the two gates gates coverage" in m for m in _errors(root))


def test_a_repository_with_no_coverage_gate_at_all_is_left_alone(tmp_path: Path) -> None:
    # Absence of a gate is not this check's business - it holds two statements
    # to each other and says nothing about whether they should exist.
    assert _errors(_gated(_repo(tmp_path), make=None, ci=None)) == []


def test_a_bare_pytest_step_elsewhere_is_not_compared(tmp_path: Path) -> None:
    # `drift.yml` runs a bare `uv run pytest` on purpose, because a coverage
    # failure there would report as a dependency break. A rule keyed on "every
    # pytest command" would fire on it every run (`PL-22Z3`).
    root = _gated(_repo(tmp_path))
    (root / ".github" / "workflows" / "drift.yml").write_text(
        "name: drift\n\non: [schedule]\n\njobs:\n  drift:\n    runs-on: ubuntu-latest\n"
        "    steps:\n      - run: uv run pytest\n",
        encoding="utf-8",
    )

    assert _errors(root) == []


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

CLAUDE_BODY = "# Rules\n\nOne.\n"

# One line of body text long enough that adding or removing it is a rule
# arriving or leaving rather than a wording fix. Derived from the floor rather
# than written out, so these tests cannot drift away from the constant they are
# about.
RULE_LINE = "R" * doc_check.MATERIAL_RESIDENT_DELTA + "\n"


def _instructed(root: Path, *, claude: str = CLAUDE_BODY, **rules: str) -> Path:
    """Add the instruction files a session loads at launch."""
    (root / "CLAUDE.md").write_text(claude, encoding="utf-8")
    if rules:
        (root / ".claude" / "rules").mkdir(parents=True, exist_ok=True)
        for name, body in rules.items():
            (root / ".claude" / "rules" / f"{name}.md").write_text(body, encoding="utf-8")
    return root


def _resident_names(root: Path) -> set[str]:
    return {row.name for row in doc_check.measure_resident(root)}


def _on_main(root: Path) -> None:
    """Commit the current tree as the default branch this check compares against."""
    _git_init(root)
    subprocess.run(("git", "branch", "-M", "main"), cwd=root, check=True, capture_output=True)


def test_a_path_scoped_rule_is_not_resident(tmp_path: Path) -> None:
    """`paths:` frontmatter defers a rule to the sessions that match it."""
    root = _instructed(_repo(tmp_path), scoped=SCOPED_RULE, always=UNSCOPED_RULE)

    assert _resident_names(root) == {"CLAUDE.md", ".claude/rules/always.md"}


def test_frontmatter_without_a_paths_key_is_still_resident(tmp_path: Path) -> None:
    """Other frontmatter does not defer a rule; only `paths:` does."""
    root = _instructed(_repo(tmp_path), other="---\nname: x\n---\n\nBody.\n")

    assert ".claude/rules/other.md" in _resident_names(root)


def test_an_unterminated_frontmatter_block_is_not_read_as_scoped(tmp_path: Path) -> None:
    root = _instructed(_repo(tmp_path), broken="---\npaths:\n  - src\n\nBody with no close.\n")

    assert ".claude/rules/broken.md" in _resident_names(root)


def test_nested_rule_directories_are_measured(tmp_path: Path) -> None:
    """Claude Code discovers `.claude/rules/**.md` recursively, so this does too."""
    root = _instructed(_repo(tmp_path))
    nested = root / ".claude" / "rules" / "backend"
    nested.mkdir(parents=True)
    (nested / "api.md").write_text(UNSCOPED_RULE, encoding="utf-8")

    assert ".claude/rules/backend/api.md" in _resident_names(root)


def test_a_repository_with_no_instruction_files_reports_nothing(tmp_path: Path) -> None:
    assert doc_check.analyze(_repo(tmp_path)).resident is None


def test_growth_against_the_default_branch_is_an_advisory(tmp_path: Path) -> None:
    root = _instructed(_repo(tmp_path))
    _on_main(root)
    (root / "CLAUDE.md").write_text(CLAUDE_BODY + RULE_LINE * 2, encoding="utf-8")

    report = doc_check.analyze(root)

    assert report.resident is not None
    assert report.resident.growth == 2 * len(RULE_LINE)
    assert report.resident.deltas() == [("CLAUDE.md", 2 * len(RULE_LINE))]
    assert report.errors == []
    assert any("resident instructions grew 82 characters" in m for m in report.advisories)
    assert any("PL-H7XN" in m for m in report.advisories)
    assert any("Never trim other resident text" in m for m in report.advisories)


def test_an_addition_inside_an_unwrapped_paragraph_cannot_report_as_unchanged(
    tmp_path: Path,
) -> None:
    """The defect this metric was moved off lines to fix, in its adding form.

    A resident file is not uniformly wrapped, so a paragraph on one physical
    line can absorb a rule's worth of new instruction without moving a single
    line. Measured on 2026-09-05, six commits in this repository's history had
    moved the resident text without moving a line at all, the largest of them
    by 409 characters (`PL-QV1F`).
    """
    paragraph = "# Rules\n\n" + "word " * 200 + "\n"
    root = _instructed(_repo(tmp_path), claude=paragraph)
    _on_main(root)
    (root / "CLAUDE.md").write_text(paragraph[:-1] + "and " * 100 + "\n", encoding="utf-8")

    report = doc_check.analyze(root)

    assert report.resident is not None
    assert report.resident.growth == 400
    assert report.resident.total_lines == 3, "the line count is the one that did not move"
    assert "unchanged against" not in doc_check.format_check(report)
    assert any("resident instructions grew 400 characters" in m for m in report.advisories)


def test_a_cut_inside_an_unwrapped_paragraph_is_visible(tmp_path: Path) -> None:
    """The same defect in its cutting form: routing text out earns credit.

    Landing `PL-6SBB` cut the largest paragraph in `CLAUDE.md` by 433
    characters and the line-based metric printed "unchanged", so the routing
    pass the growth advisory itself demands could not be seen to have worked.
    """
    paragraph = "# Rules\n\n" + "word " * 200 + "\n"
    root = _instructed(_repo(tmp_path), claude=paragraph)
    _on_main(root)
    (root / "CLAUDE.md").write_text(paragraph[:-434] + "\n", encoding="utf-8")

    report = doc_check.analyze(root)

    assert report.resident is not None
    assert report.resident.growth == -433
    assert report.resident.total_lines == 3
    assert report.advisories == []
    assert "433 fewer characters than main" in doc_check.format_check(report)


def test_a_wording_fix_below_the_floor_raises_no_advisory(tmp_path: Path) -> None:
    """Characters resolve a term swap, which is noise the advisory must not carry.

    Firing on every typo would cost attention on every later run and teach a
    session to skim the line a real finding appears on. The change is still
    printed exactly; only the demand for a routing justification is withheld.
    """
    root = _instructed(_repo(tmp_path))
    _on_main(root)
    (root / "CLAUDE.md").write_text(CLAUDE_BODY.replace("One.", "One or two."), encoding="utf-8")

    report = doc_check.analyze(root)

    assert report.resident is not None
    assert report.resident.growth == 7
    assert report.advisories == []
    assert "7 more characters than main" in doc_check.format_check(report)


def test_a_wording_fix_alongside_real_growth_is_not_read_as_a_trim(tmp_path: Path) -> None:
    """The floor applies per file, or every two-file edit reads as paying for room."""
    root = _instructed(_repo(tmp_path), always=UNSCOPED_RULE)
    _on_main(root)
    (root / "CLAUDE.md").write_text(CLAUDE_BODY + RULE_LINE * 2, encoding="utf-8")
    (root / ".claude" / "rules" / "always.md").write_text(
        UNSCOPED_RULE.replace("One line.", "One lin."), encoding="utf-8"
    )

    report = doc_check.analyze(root)

    assert report.resident is not None
    assert report.resident.growth == 2 * len(RULE_LINE) - 1
    assert report.resident.deltas() == [("CLAUDE.md", 82), (".claude/rules/always.md", -1)]
    assert report.resident.material_deltas() == [("CLAUDE.md", 82)]
    assert any("resident instructions grew 81 characters" in m for m in report.advisories)
    assert not any("both grew and shrank" in m for m in report.advisories)


def test_shrinking_is_reported_but_is_not_an_advisory(tmp_path: Path) -> None:
    """A routing pass that moves a rule out must not read as a finding."""
    root = _instructed(_repo(tmp_path), always="# Unscoped\n\n" + RULE_LINE)
    _on_main(root)
    (root / ".claude" / "rules" / "always.md").write_text(SCOPED_RULE, encoding="utf-8")

    report = doc_check.analyze(root)

    assert report.resident is not None
    assert report.resident.growth == -53
    assert report.advisories == []
    assert "53 fewer characters than main" in doc_check.format_check(report)


def test_a_trim_that_pays_for_an_addition_is_an_advisory_at_net_zero(tmp_path: Path) -> None:
    """The outcome a size limit would have forced, arriving without a limit.

    Growth and shrinkage sum into one total, so resident text cut to make room
    for an addition reports as no growth at all and the diff reads as free.
    """
    root = _instructed(_repo(tmp_path), always="# Unscoped\n" + RULE_LINE * 2)
    _on_main(root)
    (root / "CLAUDE.md").write_text(CLAUDE_BODY + RULE_LINE * 2, encoding="utf-8")
    (root / ".claude" / "rules" / "always.md").write_text("# Unscoped\n", encoding="utf-8")

    report = doc_check.analyze(root)

    assert report.resident is not None
    assert report.resident.growth == 0
    assert not any("grew 0 characters" in m for m in report.advisories)
    assert any("both grew and shrank" in m for m in report.advisories)
    assert any("PL-BKQW" in m for m in report.advisories)
    assert report.errors == []


def test_growth_alongside_a_trim_raises_both_advisories(tmp_path: Path) -> None:
    """The trim is a finding on its own, not something the growth line covers."""
    root = _instructed(_repo(tmp_path), always="# Unscoped\n" + RULE_LINE)
    _on_main(root)
    (root / "CLAUDE.md").write_text(CLAUDE_BODY + RULE_LINE * 3, encoding="utf-8")
    (root / ".claude" / "rules" / "always.md").write_text("# Unscoped\n", encoding="utf-8")

    report = doc_check.analyze(root)

    assert report.resident is not None
    assert report.resident.growth == 2 * len(RULE_LINE)
    assert any("resident instructions grew 82 characters" in m for m in report.advisories)
    assert any("both grew and shrank" in m for m in report.advisories)


def test_an_unchanged_total_is_reported_as_unchanged(tmp_path: Path) -> None:
    root = _instructed(_repo(tmp_path))
    _on_main(root)

    report = doc_check.analyze(root)

    assert report.advisories == []
    assert "unchanged against main" in doc_check.format_check(report)


def test_a_checkout_with_no_default_branch_still_reports_the_total(tmp_path: Path) -> None:
    """The comparison goes missing, not the measurement, and it says so."""
    root = _instructed(_repo(tmp_path))

    report = doc_check.analyze(root)

    assert report.resident is not None
    assert report.resident.total == len(CLAUDE_BODY)
    assert report.resident.growth is None
    assert report.advisories == []
    assert "no default branch here to compare against" in doc_check.format_check(report)


def test_the_total_is_printed_even_when_nothing_else_fired(tmp_path: Path) -> None:
    report = doc_check.analyze(_instructed(_repo(tmp_path)))
    printed = doc_check.format_check(report)

    assert "resident instructions: 14 characters over 3 lines loaded at launch" in printed
    assert "chars/lines: CLAUDE.md 14/3" in printed
    assert "all resolve" in printed


def test_a_one_character_file_is_reported_in_the_singular(tmp_path: Path) -> None:
    """`_plural` sits two lines from this line and it did not always use it."""
    report = doc_check.analyze(_instructed(_repo(tmp_path), claude="x"))

    printed = doc_check.format_check(report)

    assert "resident instructions: 1 character over 1 line loaded at launch" in printed


def test_this_repository_reports_its_own_resident_total() -> None:
    """The real tree, not only a fixture: the number has to be about this file.

    `apparatus-standard.md` is the path-scoped exemplar rather than any other:
    `CLAUDE.md` requires it to stay out of the resident set (`PL-6SBB`), so it
    cannot drift into it the way `expert-review.md` did (`PL-WWDT`).
    """
    root = Path(doc_check.__file__).resolve().parent.parent
    resident = doc_check.analyze(root).resident

    assert resident is not None
    measured = {row.name: row for row in resident.files}
    assert measured["CLAUDE.md"].characters > measured["CLAUDE.md"].lines > 0
    assert ".claude/rules/apparatus-standard.md" not in measured
    assert ".claude/rules/instruction-writing.md" in measured
    assert ".claude/rules/expert-review.md" in measured


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


# --- gate re-entries, the queue read against the frozen list -----------------
#
# `check_gate_counts` above holds a frozen list's arithmetic to itself. These
# hold its *membership* to the queue: an open `safety`- or `science`-classed
# item re-enters the current gate regardless of when it was found, and until
# `PL-KTKP` nothing reconciled the two, so eleven qualifying items sat unlisted
# while every count in the file agreed.


def _queue_item(root: Path, identifier: str, *, classes: str, status: str = "ready") -> None:
    """Write one item into the fixture repository's store."""
    store = root / "docs" / "items"
    store.mkdir(parents=True, exist_ok=True)
    (store / f"{identifier}-demo.md").write_text(
        "---\n"
        f"id: {identifier}\n"
        "title: A thing\n"
        "priority: P1\n"
        "effort: S\n"
        f"status: {status}\n"
        f"classes: {classes}\n"
        "added: 2026-09-07\n"
        "---\n\n"
        "**Problem.** A thing.\n",
        encoding="utf-8",
    )


def _reentry_advisories(root: Path) -> list[str]:
    return [
        advisory
        for advisory in doc_check.analyze(root).advisories
        if "re-enter the current gate" in advisory
    ]


def test_a_safety_item_the_frozen_list_does_not_place_is_an_advisory(tmp_path: Path) -> None:
    """The failure `PL-KTKP` records, in its smallest form."""
    root = _repo(tmp_path, roadmap=VERSIONED_GATE_ROADMAP)
    _queue_item(root, "PL-ZZZZ", classes="safety, ux")

    advisories = _reentry_advisories(root)

    assert len(advisories) == 1
    assert "PL-ZZZZ (safety)" in advisories[0]
    assert "v0.4.0" in advisories[0]


def test_a_science_item_the_frozen_list_places_is_quiet(tmp_path: Path) -> None:
    root = _repo(tmp_path, roadmap=VERSIONED_GATE_ROADMAP)
    _queue_item(root, "PL-BBBB", classes="science")

    assert _reentry_advisories(root) == []


def test_a_safety_item_in_required_scope_is_quiet(tmp_path: Path) -> None:
    """An item the milestone clears itself is placed, and clears *with* it.

    This is the case the four `safety`/`science` items excluded from Gate 1's
    2026-09-07 group are in: named under `Required scope` rather than on the
    frozen list, which `scope_ids` reads as placement either way.
    """
    roadmap = VERSIONED_GATE_ROADMAP.replace("- Something.", "- Something (queue item PL-ZZZZ).")
    root = _repo(tmp_path, roadmap=roadmap)
    _queue_item(root, "PL-ZZZZ", classes="safety")

    assert _reentry_advisories(root) == []


def test_a_closed_safety_item_the_list_does_not_place_is_quiet(tmp_path: Path) -> None:
    """The rule is about open debt; a finished finding owes the gate nothing."""
    root = _repo(tmp_path, roadmap=VERSIONED_GATE_ROADMAP)
    _queue_item(root, "PL-ZZZZ", classes="safety", status="done")

    assert _reentry_advisories(root) == []


def test_an_unplaced_item_of_another_class_is_quiet(tmp_path: Path) -> None:
    """Only `safety` and `science` re-enter unconditionally.

    Every other class defers to the next gate unless its problem predates the
    freeze, which is a judgment this check must not make on a session's behalf.
    """
    root = _repo(tmp_path, roadmap=VERSIONED_GATE_ROADMAP)
    _queue_item(root, "PL-ZZZZ", classes="defect, infra")

    assert _reentry_advisories(root) == []


def test_the_advisory_names_every_unplaced_item_in_one_line(tmp_path: Path) -> None:
    """One advisory, not one per item: the eleven arrived as a group and are
    recorded as a group, and eleven lines would bury the rest of the report."""
    root = _repo(tmp_path, roadmap=VERSIONED_GATE_ROADMAP)
    _queue_item(root, "PL-ZZZZ", classes="safety")
    _queue_item(root, "PL-YYYY", classes="science, docs")

    advisories = _reentry_advisories(root)

    assert len(advisories) == 1
    assert "PL-ZZZZ (safety)" in advisories[0]
    assert "PL-YYYY (science)" in advisories[0]
    assert "2 open items" in advisories[0]


# --- gate dispositions ------------------------------------------------------
#
# `check_gate_reentries`, the sibling this sits beside, has no test of its own:
# `PL-KTKP`'s `verify:` command greps that its `def` exists, which proves the
# function is present and nothing about what it decides (`PL-PDP6`). These
# cover the half of the rule that needs a judgment, so they exercise both
# dispositions the rule allows and the silence it forbids.


def _disposition_repo(
    tmp_path: Path, items: dict[str, str], roadmap: str = VERSIONED_GATE_ROADMAP
) -> Path:
    """A repository carrying a gate, a version baseline and an item store."""
    root = _repo(tmp_path, roadmap=roadmap)
    (root / "pyproject.toml").write_text(
        '[project]\nname = "demo"\nversion = "0.2.5"\n', encoding="utf-8"
    )
    (root / "docket.toml").write_text(
        'items_dir = "docs/items"\n'
        'debt_classes = ["defect", "safety", "science", "refactor", "perf"]\n',
        encoding="utf-8",
    )
    store = root / "docs" / "items"
    store.mkdir(parents=True, exist_ok=True)
    for identifier, front in items.items():
        (store / f"{identifier}-demo.md").write_text(
            f"---\nid: {identifier}\ntitle: Demo\n{front}added: 2026-09-06\n---\n\n"
            "**Problem.** A thing.\n**Why it matters.** It does.\n**Done when.** Fixed.\n",
            encoding="utf-8",
        )
    return root


def _dispositions(tmp_path: Path, items: dict[str, str], roadmap: str | None = None) -> list[str]:
    root = _disposition_repo(
        tmp_path, items, **({"roadmap": roadmap} if roadmap is not None else {})
    )
    return [a for a in doc_check.analyze(root).advisories if "records no disposition" in a]


DEBT = "priority: P2\neffort: S\nstatus: ready\nclasses: defect\n"


def test_a_placed_debt_item_needs_no_further_disposition(tmp_path: Path) -> None:
    """PL-BBBB is on the fixture's frozen list, so the gate has answered for it."""
    assert _dispositions(tmp_path, {"PL-BBBB": DEBT}) == []


def test_an_open_debt_item_the_gate_neither_places_nor_defers_is_reported(tmp_path: Path) -> None:
    """The silence the presence rule forbids by name, and the check exists for."""
    advisories = _dispositions(tmp_path, {"PL-ZZZZ": DEBT})

    assert any("PL-ZZZZ" in advisory for advisory in advisories)


def test_an_item_deferred_with_a_recorded_reason_is_not_reported(tmp_path: Path) -> None:
    """Deferring is one of the two answers the rule allows, so it must silence this.

    The subsection is what carries the reason, and reading it is the whole
    difference between a check that can be satisfied and one that names the
    same backlog every run.
    """
    roadmap = VERSIONED_GATE_ROADMAP.replace(
        "### Definition of done",
        "### Declined to Gate 2 on the refilling-queue ground — 1 entry\n\n"
        "Deferred because pulling it in would refill the gate.\n\n"
        "- PL-ZZZZ (S) The deferred thing\n\n### Definition of done",
        1,
    )

    assert _dispositions(tmp_path, {"PL-ZZZZ": DEBT}, roadmap) == []


def test_a_needs_decision_item_is_owed_a_disposition_whatever_its_classes(tmp_path: Path) -> None:
    """The gate takes `needs-decision` regardless of class, so this must too."""
    front = "priority: P2\neffort: S\nstatus: needs-decision\nclasses: docs\n"

    advisories = _dispositions(tmp_path, {"PL-ZZZZ": front})

    assert any("PL-ZZZZ" in advisory for advisory in advisories)


def test_an_item_that_is_neither_debt_nor_needs_decision_is_left_alone(tmp_path: Path) -> None:
    front = "priority: P3\neffort: S\nstatus: ready\nclasses: docs\n"

    assert _dispositions(tmp_path, {"PL-ZZZZ": front}) == []


def test_a_closed_item_is_owed_nothing(tmp_path: Path) -> None:
    """A gate is about open work; a done item needs no placement."""
    front = "priority: P2\neffort: S\nstatus: done\nclasses: defect\nclosed: 2026-09-07\n"

    assert _dispositions(tmp_path, {"PL-ZZZZ": front}) == []


def test_this_repository_records_a_disposition_for_every_open_debt_item() -> None:
    """The real tree, not only a fixture - which is what `PL-36R4` was about."""
    root = Path(doc_check.__file__).resolve().parent.parent

    assert [a for a in doc_check.analyze(root).advisories if "records no disposition" in a] == []
